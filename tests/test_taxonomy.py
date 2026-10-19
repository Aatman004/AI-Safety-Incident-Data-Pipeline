"""Unit tests for the AI Safety threat taxonomy classifier."""

from incident_pipeline.models import RiskCategory, SeverityLevel
from incident_pipeline.processors.taxonomy import classify_incident


def test_classify_prompt_injection():
    title = "Jailbreak Vulnerabilities in Aligned Large Language Models"
    text = "We discover that adversarial suffix attacks bypass safety alignment filters reliably."
    cats, severity, tags, confidence = classify_incident(title, text)

    assert RiskCategory.PROMPT_INJECTION in cats
    assert len(tags) > 0
    assert 0.0 <= confidence <= 1.0


def test_classify_hallucination():
    title = "Measuring Truthfulness and Factuality in Legal AI Applications"
    text = "Attorneys suffered hallucination failures where ungrounded citations were confabulated."
    cats, severity, tags, confidence = classify_incident(title, text)

    assert RiskCategory.HALLUCINATION in cats


def test_classify_deceptive_alignment():
    title = "Strategic Deception and Reward Hacking in Autonomous Reinforcement Learning"
    text = "The agent demonstrated deceptive alignment and specification gaming during sandbox evaluation."
    cats, severity, tags, confidence = classify_incident(title, text)

    assert RiskCategory.DECEPTION_REWARD_HACKING in cats


def test_classify_critical_severity():
    title = "Zero-Day Autonomous Exploitation and Critical Remote Code Execution"
    text = "Unrestricted exploit generation enabled remote takeover of infrastructure."
    cats, severity, tags, confidence = classify_incident(title, text)

    assert severity == SeverityLevel.CRITICAL
