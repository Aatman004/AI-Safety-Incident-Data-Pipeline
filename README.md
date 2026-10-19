# AI Safety Incident & Threat Intelligence Pipeline

[![CI](https://github.com/aatmangupta/ai-safety-incident-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/aatmangupta/ai-safety-incident-pipeline/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An automated data ingestion, threat taxonomy classification, and analytical storage pipeline that monitors global AI safety research, vulnerability reports, and near-miss incidents. Built to support empirical alignment research, risk trend analysis, and frontier safety governance.

---

## Overview & AI Safety Motivation

As frontier models are deployed into higher-stakes autonomous environments, tracking empirical failure modes, emergent vulnerability vectors, and pre-deployment safety research is critical. This pipeline automates the tracking of:
- **Academic Research Preprints**: arXiv feeds across `cs.AI`, `cs.LG`, `cs.CR`, and `cs.CY` filtered for alignment, jailbreaking, unlearning, backdoors, and steering vectors.
- **Empirical Incident Reports**: Public incidents and vulnerabilities from the AI Incident Database (AIID) and public safety feeds.
- **Safety Community Research**: New posts and discussion from Alignment Forum and LessWrong AI alignment tags.

All ingested records undergo canonical URL/text deduplication, are mapped into an AI Safety Threat Taxonomy (aligned with NIST AI RMF and OWASP for LLMs), and are indexed into an SQLite database equipped with **FTS5 full-text search** and analytical views.

---

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    arXiv API    │    │  AIID Database  │    │ Alignment Forum │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └───────────────┬──────┴──────────────────────┘
                         ▼
        ┌───────────────────────────────────┐
        │        Collector Layer            │
        └────────────────┬──────────────────┘
                         ▼
        ┌───────────────────────────────────┐
        │     Processing & Normalization    │
        │  • Canonical URL Deduplication    │
        │  • Safety Taxonomy Classifier     │
        │  • Severity & Tag Extractor       │
        └────────────────┬──────────────────┘
                         ▼
        ┌───────────────────────────────────┐
        │    Storage & Retrieval Engine     │
        │  • SQLite + FTS5 Full Text Index  │
        │  • Categorical Trend Aggregates   │
        └────────────────┬──────────────────┘
                         ▼
        ┌───────────────────────────────────┐
        │       CLI & Reporting Layer       │
        │  • `ingest`, `search`, `export`   │
        │  • Markdown & JSON Briefings      │
        └───────────────────────────────────┘
```

---

## Safety Threat Taxonomy

Records are mapped into categorized safety threat vectors:
- `prompt_injection`: Direct jailbreaks, indirect injections, prompt leaking.
- `hallucination_sycophancy`: Factuality failures, confabulation, ungrounded outputs.
- `deception_reward_hacking`: Specification gaming, deceptive alignment, outer/inner misalignment.
- `cyber_offense`: Autonomous vulnerability discovery, exploit generation.
- `cbrn_risks`: Chemical, biological, radiological, or nuclear knowledge enablement.
- `agentic_autonomous_failure`: Runaway loops, tool abuse, cascading downstream failure.
- `model_theft_extraction`: Model extraction, inversion, weight exfiltration.
- `bias_toxicity`: Toxic generation, representational harms.
- `governance_evaluations`: Safety benchmarks, auditing protocols, red-team methodologies.

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Git

### Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/aatmangupta/ai-safety-incident-pipeline.git
cd ai-safety-incident-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package and dependencies
pip install -e ".[dev]"
```

---

## CLI Usage

The pipeline exposes a clean CLI via `incident-pipeline`:

### 1. Ingest from All Sources
```bash
# Ingest 25 recent items from arXiv, AIID, and safety forums
incident-pipeline ingest --limit 25
```

### 2. Search Records via FTS5
```bash
# Instant full-text search across titles, abstracts, and summaries
incident-pipeline search "jailbreak"
incident-pipeline search "reward hacking" --category deception_reward_hacking
```

### 3. Generate Safety Trend Report
```bash
# Export weekly trend intelligence report in Markdown format
incident-pipeline report --format markdown --output reports/ai_safety_briefing.md
```

### 4. Export Structured Data
```bash
# Export all records to CSV or JSONL for external research & dashboarding
incident-pipeline export --format csv --output data/incidents.csv
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Author

**Aatman Gupta**  
Queen's University — Bachelor of Computing (Artificial Intelligence)  
Email: [aatmangupta8@gmail.com](mailto:aatmangupta8@gmail.com)  
AI Safety Fellowship Lead | Queen's Effective Altruism
