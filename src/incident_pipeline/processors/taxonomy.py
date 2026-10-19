"""Rule-based and heuristic AI Safety threat taxonomy classifier."""

import re

from incident_pipeline.models import RiskCategory, SeverityLevel

TAXONOMY_PATTERNS: dict[RiskCategory, list[str]] = {
    RiskCategory.PROMPT_INJECTION: [
        r"\bjailbreak(?:s|ing)?\b",
        r"\bprompt injection\b",
        r"\badversarial (?:prompt|suffix|attack|perturbation)\b",
        r"\bgcg\b",
        r"\bindirect injection\b",
        r"\bsystem prompt leak(?:age)?\b",
        r"\buniversal attack\b",
        r"\brefusal bypass\b",
    ],
    RiskCategory.HALLUCINATION: [
        r"\bhallucinat(?:ion|ions|ing)?\b",
        r"\bconfabulat(?:ion|ions)?\b",
        r"\bsycophan(?:cy|tic)\b",
        r"\btruthful(?:ness)?\b",
        r"\bfactual accuracy\b",
        r"\bunfaithfulness\b",
        r"\bunfounded claim\b",
    ],
    RiskCategory.DECEPTION_REWARD_HACKING: [
        r"\bdeceptive alignment\b",
        r"\breward hacking\b",
        r"\bspecification gaming\b",
        r"\binner misalign(?:ment)?\b",
        r"\bouter misalign(?:ment)?\b",
        r"\bstrategic deception\b",
        r"\bscheming\b",
        r"\bsandbagging\b",
    ],
    RiskCategory.CYBER_OFFENSE: [
        r"\bcyber offensive\b",
        r"\bmalware synthes(?:is|ize)\b",
        r"\bexploit generation\b",
        r"\bzero-day discovery\b",
        r"\bautomated hacking\b",
        r"\bvulnerability exploitation\b",
    ],
    RiskCategory.CBRN: [
        r"\bcbrn\b",
        r"\bbiological agent\b",
        r"\bpathogen design\b",
        r"\bdual-use bio\b",
        r"\bchemical weapon\b",
        r"\bradiological threat\b",
    ],
    RiskCategory.AGENTIC_FAILURE: [
        r"\bagentic fail(?:ure)?\b",
        r"\bautonomous loop\b",
        r"\brunaway agent\b",
        r"\btool abuse\b",
        r"\bunauthorized action\b",
        r"\bcascading failure\b",
        r"\bcontext window overflow agent\b",
    ],
    RiskCategory.MODEL_THEFT_EXTRACTION: [
        r"\bmodel extraction\b",
        r"\bweight exfiltration\b",
        r"\bmembership inference\b",
        r"\bmodel inversion\b",
        r"\bprompt extraction\b",
        r"\bdata extraction attack\b",
    ],
    RiskCategory.BIAS_TOXICITY: [
        r"\btoxicit(?:y|ies)\b",
        r"\bhate speech\b",
        r"\bdemographic bias\b",
        r"\bdisparate impact\b",
        r"\bstereotyp(?:e|ing)\b",
    ],
    RiskCategory.GOVERNANCE_EVALS: [
        r"\bsafety benchmark(?:s)?\b",
        r"\bevaluation harness\b",
        r"\beval(?:s)? framework\b",
        r"\bred-team(?:ing)? protocol\b",
        r"\brisk assessment\b",
        r"\bai governance\b",
        r"\bauditing\b",
    ],
}

SEVERITY_KEYWORDS: dict[SeverityLevel, list[str]] = {
    SeverityLevel.CRITICAL: [
        r"\bcritical\b",
        r"\bzero-day\b",
        r"\bcbrn\b",
        r"\bcatastrophic\b",
        r"\bunrestricted\b",
        r"\bcomplete bypass\b",
        r"\bremote code execution\b",
    ],
    SeverityLevel.HIGH: [
        r"\bhigh\b",
        r"\bexploit\b",
        r"\buniversal jailbreak\b",
        r"\bpersistent failure\b",
        r"\bsystemic risk\b",
        r"\bsevere\b",
    ],
    SeverityLevel.MEDIUM: [
        r"\bmoderate\b",
        r"\bmedium\b",
        r"\bpartial\b",
        r"\bdegradation\b",
        r"\blimited\b",
        r"\bhallucination\b",
    ],
    SeverityLevel.LOW: [r"\blow\b", r"\bminor\b", r"\btheoretical\b", r"\bpreliminary\b"],
}


def classify_incident(
    title: str, text: str
) -> tuple[list[RiskCategory], SeverityLevel, list[str], float]:
    """Classify incident text against AI safety risk taxonomies and assess severity."""
    combined_content = f"{title} {text}".lower()
    matched_categories: set[RiskCategory] = set()
    extracted_tags: set[str] = set()
    category_scores: dict[RiskCategory, int] = {}

    for category, patterns in TAXONOMY_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, combined_content, re.IGNORECASE)
            if matches:
                score += len(matches)
                # Clean matched text to use as tag
                clean_tag = re.sub(r"[^\w\s-]", "", matches[0].lower()).strip()
                extracted_tags.add(clean_tag)
        if score > 0:
            category_scores[category] = score
            matched_categories.add(category)

    # Default category if nothing specific matched
    if not matched_categories:
        matched_categories.add(RiskCategory.GENERAL_SAFETY)

    # Determine severity based on keywords
    assessed_severity = SeverityLevel.MEDIUM
    for severity, patterns in SEVERITY_KEYWORDS.items():
        if any(re.search(pat, combined_content, re.IGNORECASE) for pat in patterns):
            assessed_severity = severity
            break

    # Confidence calculation: ratio of matched categories to heuristic certainty
    confidence = min(0.95, 0.65 + 0.1 * min(3, len(category_scores)))

    sorted_categories = sorted(
        matched_categories, key=lambda c: category_scores.get(c, 0), reverse=True
    )

    return sorted_categories, assessed_severity, sorted(extracted_tags), confidence
