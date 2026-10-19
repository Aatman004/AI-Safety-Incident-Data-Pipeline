"""Unit tests for SQLite storage and FTS5 search."""

from datetime import datetime
from pathlib import Path

import pytest

from incident_pipeline.models import IncidentRecord, RiskCategory, SeverityLevel, SourceType
from incident_pipeline.storage.database import IncidentDatabase


@pytest.fixture
def temp_db(tmp_path: Path) -> IncidentDatabase:
    db_file = tmp_path / "test_incidents.db"
    return IncidentDatabase(db_file)


def test_insert_and_deduplicate(temp_db: IncidentDatabase):
    record = IncidentRecord(
        id="test-hash-123",
        title="Test Incident Title",
        url="https://example.com/incident-1",
        source=SourceType.AIID,
        source_id="AIID-001",
        authors=["Alice", "Bob"],
        published_at=datetime.utcnow(),
        summary="Test incident summary describing prompt injection failure.",
        risk_categories=[RiskCategory.PROMPT_INJECTION],
        severity=SeverityLevel.HIGH,
        tags=["prompt injection"],
    )

    # First insert succeeds
    assert temp_db.save_record(record) is True

    # Duplicate insert is rejected
    assert temp_db.save_record(record) is False

    stats = temp_db.get_statistics()
    assert stats["total_records"] == 1
    assert stats["by_severity"]["high"] == 1


def test_fts5_search(temp_db: IncidentDatabase):
    rec1 = IncidentRecord(
        id="hash-1",
        title="Adversarial Jailbreak and Refusal Bypass",
        url="https://example.com/1",
        source=SourceType.ARXIV,
        source_id="arxiv-1",
        authors=["Researcher"],
        published_at=datetime.utcnow(),
        summary="A study on automated jailbreak techniques against aligned models.",
        risk_categories=[RiskCategory.PROMPT_INJECTION],
        severity=SeverityLevel.HIGH,
    )
    rec2 = IncidentRecord(
        id="hash-2",
        title="Quantifying Sycophancy and Hallucination",
        url="https://example.com/2",
        source=SourceType.ARXIV,
        source_id="arxiv-2",
        authors=["Evaluator"],
        published_at=datetime.utcnow(),
        summary="Measuring truthful outputs and ungrounded confabulation rates.",
        risk_categories=[RiskCategory.HALLUCINATION],
        severity=SeverityLevel.MEDIUM,
    )

    temp_db.save_records([rec1, rec2])

    # Search for jailbreak
    results = temp_db.search("jailbreak")
    assert len(results) == 1
    assert results[0].id == "hash-1"

    # Search for hallucination
    results = temp_db.search("hallucination")
    assert len(results) == 1
    assert results[0].id == "hash-2"
