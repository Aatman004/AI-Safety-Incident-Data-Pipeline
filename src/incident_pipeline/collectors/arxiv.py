"""arXiv API collector for AI Safety and Alignment research preprints."""

from datetime import datetime
import re
from typing import List
import feedparser
import httpx
from incident_pipeline.collectors.base import BaseCollector
from incident_pipeline.models import IncidentRecord, SourceType
from incident_pipeline.processors.deduplicator import generate_record_id, normalize_url
from incident_pipeline.processors.taxonomy import classify_incident


class ArxivCollector(BaseCollector):
    """Fetches AI safety and alignment preprints from arXiv export API."""

    name: str = "arxiv"
    API_URL: str = "https://export.arxiv.org/api/query"

    SAFETY_KEYWORDS = [
        "jailbreak",
        "prompt injection",
        "adversarial attack",
        "AI alignment",
        "reward hacking",
        "machine unlearning",
        "steering vector",
        "mechanistic interpretability",
        "sycophancy",
        "model hallucination",
    ]

    def _build_query(self) -> str:
        """Construct arXiv API search query targeting computer science categories and safety terms."""
        terms = [f'all:"{kw}"' for kw in self.SAFETY_KEYWORDS]
        keyword_clause = " OR ".join(terms)
        category_clause = "(cat:cs.AI OR cat:cs.LG OR cat:cs.CR OR cat:cs.CY)"
        return f"{category_clause} AND ({keyword_clause})"

    def collect(self, limit: int = 25) -> List[IncidentRecord]:
        """Query arXiv and transform papers into normalized IncidentRecord models."""
        query = self._build_query()
        params = {
            "search_query": query,
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(self.API_URL, params=params)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
        except Exception as e:
            # Return empty list on network error, allowing caller to handle
            return []

        records: List[IncidentRecord] = []
        for entry in feed.entries:
            title = entry.title.replace("\n", " ").strip()
            summary = entry.summary.replace("\n", " ").strip()
            raw_url = entry.link
            canonical_url = normalize_url(raw_url)

            # Extract arXiv ID
            arxiv_id_match = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+(?:\w+)?)", canonical_url)
            arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else canonical_url

            # Extract authors
            authors = [a.name for a in getattr(entry, "authors", []) if hasattr(a, "name")]

            # Parse publication timestamp
            pub_date = datetime.utcnow()
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])

            # Classify risk taxonomy and severity
            categories, severity, tags, confidence = classify_incident(title, summary)
            rec_id = generate_record_id(canonical_url, title)

            record = IncidentRecord(
                id=rec_id,
                title=title,
                url=canonical_url,
                source=SourceType.ARXIV,
                source_id=arxiv_id,
                authors=authors,
                published_at=pub_date,
                summary=summary,
                risk_categories=categories,
                severity=severity,
                tags=tags,
                confidence_score=confidence,
                raw_metadata={"arxiv_categories": [t.get("term") for t in getattr(entry, "tags", [])]}
            )
            records.append(record)

        return records
