"""SQLite storage engine with FTS5 full-text search and analytical aggregation."""

from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from incident_pipeline.models import IncidentRecord, RiskCategory, SeverityLevel, SourceType


class IncidentDatabase:
    """Manages SQLite storage, full-text search (FTS5), and analytical queries."""

    def __init__(self, db_path: str | Path = "data/incidents.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema, indices, and FTS5 full-text virtual table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Primary incidents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                authors TEXT NOT NULL,
                published_at TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT,
                risk_categories TEXT NOT NULL,
                primary_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                tags TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                raw_metadata TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # Indexing for fast analytical grouping
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_source ON incidents(source);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_primary_cat ON incidents(primary_category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_published ON incidents(published_at);")

            # FTS5 full-text search virtual table
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS incidents_fts USING fts5(
                id UNINDEXED,
                title,
                summary,
                tags,
                content
            );
            """)

            # Triggers to keep FTS5 synchronized with primary table
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_incidents_ai AFTER INSERT ON incidents BEGIN
                INSERT INTO incidents_fts(id, title, summary, tags, content)
                VALUES (new.id, new.title, new.summary, new.tags, coalesce(new.content, ''));
            END;
            """)

            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_incidents_ad AFTER DELETE ON incidents BEGIN
                DELETE FROM incidents_fts WHERE id = old.id;
            END;
            """)

            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_incidents_au AFTER UPDATE ON incidents BEGIN
                DELETE FROM incidents_fts WHERE id = old.id;
                INSERT INTO incidents_fts(id, title, summary, tags, content)
                VALUES (new.id, new.title, new.summary, new.tags, coalesce(new.content, ''));
            END;
            """)
            conn.commit()

    def record_exists(self, record_id: str) -> bool:
        """Check if a record with the canonical ID already exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM incidents WHERE id = ?", (record_id,))
            return cursor.fetchone() is not None

    def save_record(self, record: IncidentRecord) -> bool:
        """Save a single incident record. Returns True if inserted, False if already present."""
        if self.record_exists(record.id):
            return False

        primary_category = (
            record.risk_categories[0].value
            if record.risk_categories
            else RiskCategory.GENERAL_SAFETY.value
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO incidents (
                id, title, url, source, source_id, authors, published_at,
                summary, content, risk_categories, primary_category, severity,
                tags, confidence_score, raw_metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.title,
                record.url,
                record.source.value,
                record.source_id,
                json.dumps(record.authors),
                record.published_at.isoformat(),
                record.summary,
                record.content,
                json.dumps([c.value for c in record.risk_categories]),
                primary_category,
                record.severity.value,
                json.dumps(record.tags),
                record.confidence_score,
                json.dumps(record.raw_metadata),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True

    def save_records(self, records: List[IncidentRecord]) -> Tuple[int, int]:
        """Bulk save records. Returns (inserted_count, skipped_duplicates_count)."""
        inserted = 0
        skipped = 0
        for rec in records:
            if self.save_record(rec):
                inserted += 1
            else:
                skipped += 1
        return inserted, skipped

    def _row_to_record(self, row: sqlite3.Row) -> IncidentRecord:
        """Map a database row to an IncidentRecord model."""
        raw_cats = json.loads(row["risk_categories"])
        categories = [RiskCategory(c) for c in raw_cats] if raw_cats else [RiskCategory.GENERAL_SAFETY]
        
        return IncidentRecord(
            id=row["id"],
            title=row["title"],
            url=row["url"],
            source=SourceType(row["source"]),
            source_id=row["source_id"],
            authors=json.loads(row["authors"]),
            published_at=datetime.fromisoformat(row["published_at"]),
            summary=row["summary"],
            content=row["content"],
            risk_categories=categories,
            severity=SeverityLevel(row["severity"]),
            tags=json.loads(row["tags"]),
            confidence_score=row["confidence_score"],
            raw_metadata=json.loads(row["raw_metadata"]) if row["raw_metadata"] else {}
        )

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[IncidentRecord]:
        """Perform full-text search across records using FTS5."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean and sanitize FTS query
            sanitized = "".join(c for c in query if c.isalnum() or c in " *_-").strip()
            if not sanitized:
                return []

            sql = """
            SELECT i.* FROM incidents i
            JOIN incidents_fts fts ON i.id = fts.id
            WHERE incidents_fts MATCH ?
            """
            params: List[Any] = [sanitized]

            if category:
                sql += " AND i.primary_category = ?"
                params.append(category)

            if severity:
                sql += " AND i.severity = ?"
                params.append(severity)

            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_record(r) for r in rows]

    def get_all(self, limit: int = 500) -> List[IncidentRecord]:
        """Retrieve recent records ordered by published date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incidents ORDER BY published_at DESC LIMIT ?", (limit,))
            return [self._row_to_record(r) for r in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Compute aggregated distribution of incidents and safety research."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS total FROM incidents")
            total = cursor.fetchone()["total"]

            cursor.execute("""
            SELECT primary_category, COUNT(*) AS count 
            FROM incidents 
            GROUP BY primary_category 
            ORDER BY count DESC
            """)
            categories = {r["primary_category"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("""
            SELECT source, COUNT(*) AS count 
            FROM incidents 
            GROUP BY source 
            ORDER BY count DESC
            """)
            sources = {r["source"]: r["count"] for r in cursor.fetchall()}

            cursor.execute("""
            SELECT severity, COUNT(*) AS count 
            FROM incidents 
            GROUP BY severity 
            ORDER BY count DESC
            """)
            severities = {r["severity"]: r["count"] for r in cursor.fetchall()}

            return {
                "total_records": total,
                "by_category": categories,
                "by_source": sources,
                "by_severity": severities,
            }
