"""Unit tests for data collectors."""

from incident_pipeline.collectors.aiid import AIIDCollector
from incident_pipeline.models import SourceType


def test_aiid_seed_collection():
    collector = AIIDCollector()
    # Collect up to 3 seed records
    records = collector.collect(limit=3)

    assert len(records) == 3
    for r in records:
        assert r.source == SourceType.AIID
        assert len(r.id) == 64
        assert r.title
        assert len(r.risk_categories) > 0
