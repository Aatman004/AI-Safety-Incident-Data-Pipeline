"""Collector for AI Safety community forums and research RSS feeds."""

from datetime import datetime

import feedparser
import httpx
from bs4 import BeautifulSoup

from incident_pipeline.collectors.base import BaseCollector
from incident_pipeline.models import IncidentRecord, SourceType
from incident_pipeline.processors.deduplicator import generate_record_id, normalize_url
from incident_pipeline.processors.taxonomy import classify_incident


class SafetyRSSCollector(BaseCollector):
    """Fetches discussions and technical posts from Alignment Forum and LessWrong."""

    name: str = "safety_rss"

    FEEDS = [
        ("https://www.alignmentforum.org/feed.xml", SourceType.ALIGNMENT_FORUM),
        ("https://www.lesswrong.com/feed.xml?view=curated-rss", SourceType.LESSWRONG),
    ]

    def _clean_html(self, html_content: str) -> str:
        """Strip HTML tags and convert to clean text for classification."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def collect(self, limit: int = 25) -> list[IncidentRecord]:
        """Fetch items from community safety feeds."""
        records: list[IncidentRecord] = []
        per_feed_limit = max(5, limit // len(self.FEEDS))

        for feed_url, source_type in self.FEEDS:
            try:
                with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                    resp = client.get(feed_url)
                    if resp.status_code != 200:
                        continue
                    parsed = feedparser.parse(resp.text)
            except Exception:
                continue

            for entry in parsed.entries[:per_feed_limit]:
                title = getattr(entry, "title", "Untitled Safety Post").strip()
                raw_url = getattr(entry, "link", "")
                canonical_url = normalize_url(raw_url)

                raw_summary = getattr(entry, "summary", "")
                clean_text = self._clean_html(raw_summary)

                author = getattr(entry, "author", "Unknown Author")
                authors = [author] if author else []

                pub_date = datetime.utcnow()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])

                categories, severity, tags, confidence = classify_incident(title, clean_text)
                rec_id = generate_record_id(canonical_url, title)

                record = IncidentRecord(
                    id=rec_id,
                    title=title,
                    url=canonical_url,
                    source=source_type,
                    source_id=canonical_url,
                    authors=authors,
                    published_at=pub_date,
                    summary=clean_text[:1000],  # Truncate summary if long
                    risk_categories=categories,
                    severity=severity,
                    tags=tags,
                    confidence_score=confidence,
                    raw_metadata={"feed_url": feed_url},
                )
                records.append(record)

        return records[:limit]
