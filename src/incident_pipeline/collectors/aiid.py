"""Collector for the AI Incident Database (AIID) and empirical AI safety failures."""

from datetime import datetime
from typing import Any

import httpx

from incident_pipeline.collectors.base import BaseCollector
from incident_pipeline.models import IncidentRecord, SourceType
from incident_pipeline.processors.deduplicator import generate_record_id, normalize_url
from incident_pipeline.processors.taxonomy import classify_incident


class AIIDCollector(BaseCollector):
    """Fetches real-world AI incidents from the AI Incident Database (AIID).

    If AIID cannot be reached, this collector returns no records. It never
    substitutes hand-written incidents: an earlier fallback list carried AIID
    citations that did not match the real AIID entries.
    """

    name: str = "aiid"
    SNAPSHOT_URL = "https://incidentdatabase.ai/research/snapshots/incidents.json"

    def _convert_item(self, item: dict[str, Any]) -> IncidentRecord:
        title = item["title"]
        url = normalize_url(item["url"])
        summary = item.get("description", "")
        pub_date = datetime.strptime(item.get("date", "2024-01-01"), "%Y-%m-%d")
        authors = item.get("authors", [])

        categories, severity, tags, confidence = classify_incident(title, summary)
        rec_id = generate_record_id(url, title)

        return IncidentRecord(
            id=rec_id,
            title=title,
            url=url,
            source=SourceType.AIID,
            source_id=str(item.get("incident_id", "AIID")),
            authors=authors,
            published_at=pub_date,
            summary=summary,
            risk_categories=categories,
            severity=severity,
            tags=tags,
            confidence_score=confidence,
            raw_metadata={"raw_incident_id": item.get("incident_id")},
        )

    def collect(self, limit: int = 25) -> list[IncidentRecord]:
        """Fetch the latest live incidents from AIID; return [] if it is unreachable."""
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(self.SNAPSHOT_URL)
                if res.status_code == 200:
                    data = res.json()
                    items = data.get("incidents", data) if isinstance(data, dict) else data
                    if isinstance(items, list) and len(items) > 0:
                        records = [self._convert_item(it) for it in items[:limit]]
                        return records
        except Exception:
            pass

        # No fabricated fallback: an unreachable source yields no records.
        return []
