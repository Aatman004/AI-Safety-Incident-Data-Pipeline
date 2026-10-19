# AI Safety Incident & Threat Intelligence Pipeline

[![CI](https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline/actions/workflows/ci.yml)
[![Daily Ingestion & Timeline Update](https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline/actions/workflows/scheduled_ingest.yml/badge.svg)](https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline/actions/workflows/scheduled_ingest.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> 🌐 **Live Interactive Timeline:** **[https://aatman004.github.io/AI-Safety-Incident-Data-Pipeline/](https://aatman004.github.io/AI-Safety-Incident-Data-Pipeline/)**  
> *An intentional, fluid visual chronology tracking landmark AI Safety incidents, jailbreak discoveries, deceptive alignment observations, and governance milestones from the release of ChatGPT (Nov 2022) to 2026.*

An automated data ingestion, threat taxonomy classification, and analytical storage pipeline that monitors global AI safety research, vulnerability reports, and near-miss incidents. Built to support empirical alignment research, risk trend analysis, and frontier safety governance. Also because I couldn't find an existing data pipeline.

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
git clone https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline.git
cd AI-Safety-Incident-Data-Pipeline

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

### 4. Interactive Timeline & Local Dashboard
```bash
# Generate standalone interactive HTML timeline (merges database records with landmark chronology)
incident-pipeline timeline --output docs/index.html

# Launch local server and open timeline in your default browser at http://localhost:8000
incident-pipeline serve --port 8000
```

### 5. Automated Periodic Monitoring Daemon
```bash
# Run continuous background ingestion daemon scanning arXiv & AIID every hour
incident-pipeline monitor --interval 3600 --limit 20
```

### 6. Export Structured Data
```bash
# Export all records to CSV or JSON for external research & dashboarding
incident-pipeline export --format csv --output data/incidents.csv
```

---

## Automated Ingestion & GitHub Pages Hosting

The repository includes a GitHub Actions workflow (`.github/workflows/scheduled_ingest.yml`) that runs daily at `06:00 UTC`:
1. Ingests fresh AI safety preprints and incident filings.
2. Deduplicates and assigns risk taxonomy tags.
3. Automatically rebuilds and deploys the live interactive timeline at `docs/index.html`.

### Enabling GitHub Pages (1-Click)
1. Go to your repository **Settings** -> **Pages**.
2. Under **Build and deployment > Branch**, select `main` and folder `/docs`.
3. Click **Save**. Your interactive timeline will be permanently hosted at:  
   `https://aatman004.github.io/AI-Safety-Incident-Data-Pipeline/`

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
