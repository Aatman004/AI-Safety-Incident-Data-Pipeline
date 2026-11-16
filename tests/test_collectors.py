"""Unit tests for data collectors."""

from incident_pipeline.collectors.aiid import AIIDCollector
from incident_pipeline.models import SourceType


def test_aiid_unreachable_returns_no_records(monkeypatch):
    """A failed AIID fetch must yield nothing, never invented incidents."""
    import httpx

    def boom(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx.Client, "get", boom)
    assert AIIDCollector().collect(limit=3) == []
    assert not hasattr(AIIDCollector, "SEED_INCIDENTS")


def test_aiid_converts_live_items():
    item = {
        "incident_id": 421,
        "title": "Example live AIID incident",
        "url": "https://incidentdatabase.ai/cite/421",
        "description": "Example description.",
        "date": "2022-11-20",
    }
    r = AIIDCollector()._convert_item(item)
    assert r.source == SourceType.AIID
    assert len(r.id) == 64
    assert r.title
    assert r.source_id == "421"
