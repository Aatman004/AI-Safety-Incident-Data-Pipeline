"""Data models for the AI Safety Incident and Research Pipeline."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    """Taxonomy of AI safety & security risk categories.

    Synthesizes taxonomies from NIST AI RMF, OWASP Top 10 for LLMs,
    and frontier AI safety frameworks.
    """

    PROMPT_INJECTION = "prompt_injection"
    HALLUCINATION = "hallucination_sycophancy"
    DECEPTION_REWARD_HACKING = "deception_reward_hacking"
    CYBER_OFFENSE = "cyber_offense"
    CBRN = "cbrn_risks"
    AGENTIC_FAILURE = "agentic_autonomous_failure"
    MODEL_THEFT_EXTRACTION = "model_theft_extraction"
    BIAS_TOXICITY = "bias_toxicity"
    GOVERNANCE_EVALS = "governance_evaluations"
    GENERAL_SAFETY = "general_alignment_safety"


class SeverityLevel(str, Enum):
    """Severity ratings for observed incidents or vulnerabilities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceType(str, Enum):
    """Origin source of the incident or research record."""

    ARXIV = "arxiv"
    AIID = "ai_incident_database"
    ALIGNMENT_FORUM = "alignment_forum"
    LESSWRONG = "lesswrong"
    CUSTOM_RSS = "custom_rss"


class IncidentRecord(BaseModel):
    """Canonical representation of an AI safety incident or research publication."""

    id: str = Field(
        description="Unique canonical SHA-256 hash derived from normalized URL and title"
    )
    title: str = Field(description="Title of the incident report or paper")
    url: str = Field(description="Direct canonical URL to the report or paper")
    source: SourceType = Field(description="Data source category")
    source_id: str = Field(description="Native identifier in the originating platform")
    authors: list[str] = Field(default_factory=list, description="Authors or reporting entities")
    published_at: datetime = Field(description="Timestamp when originally published or reported")
    summary: str = Field(description="Summary or abstract of the incident/paper")
    content: str | None = Field(
        default=None, description="Full body or extracted text if available"
    )
    risk_categories: list[RiskCategory] = Field(
        default_factory=lambda: [RiskCategory.GENERAL_SAFETY],
        description="Classified safety risk categories",
    )
    severity: SeverityLevel = Field(
        default=SeverityLevel.MEDIUM, description="Assessed severity level"
    )
    tags: list[str] = Field(default_factory=list, description="Extracted keywords and topic tags")
    confidence_score: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Classification confidence score"
    )
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Original payload or metadata from source API"
    )
