"""Generates an intentional, fluid, and polished interactive HTML timeline of AI Safety incidents."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from incident_pipeline.storage.database import IncidentDatabase
from incident_pipeline.timeline_data import LANDMARK_AI_SAFETY_INCIDENTS


def adaptively_summarize(title: str, text: str, category: str) -> Tuple[str, str, str]:
    """Intelligently condense raw text or paper abstracts into an adaptive summary, root mechanism, and safety takeaway."""
    if not text:
        return (
            title,
            "Adversarial vulnerability in system safety boundaries.",
            "Requires defensive isolation and pre-deployment evaluation.",
        )

    clean_text = text.strip()
    clean_text = re.sub(
        r"^(TLDR|Summary|Abstract|Executive Summary|Introduction)[:\s\-]+",
        "",
        clean_text,
        flags=re.IGNORECASE,
    )
    clean_text = re.sub(r"^\(Originally.*?\)\s*", "", clean_text)
    clean_text = re.sub(r"^Many thanks to.*?\.\s*", "", clean_text)
    clean_text = re.sub(r"^Linkpost to.*?\.\s*", "", clean_text)
    clean_text = re.sub(r"\[\d+\]", "", clean_text)
    clean_text = re.sub(r"https?://\S+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    sentences = re.split(r"(?<=[.!?])\s+", clean_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    finding_keywords = [
        "we show",
        "we find",
        "we demonstrate",
        "we introduce",
        "reveals that",
        "proves that",
        "shows that",
        "findings show",
        "experiments show",
        "vulnerability",
        "vulnerabilities",
        "bypassed",
        "jailbreak",
        "hijacked",
        "sandbagging",
        "deception",
        "injection",
        "attack",
        "compromise",
        "risk",
    ]

    selected = []
    for s in sentences:
        s_lower = s.lower()
        if any(k in s_lower for k in finding_keywords):
            selected.append(s)
            if len(" ".join(selected)) > 140:
                break

    if not selected and sentences:
        selected = [sentences[0]]
        if len(sentences) > 1 and len(selected[0]) < 90:
            selected.append(sentences[1])

    summary = " ".join(selected) if selected else clean_text[:180]

    # Trim to max ~210 chars at word boundary if needed
    if len(summary) > 220:
        clipped = summary[:210]
        last_space = clipped.rfind(" ")
        if last_space > 120:
            clipped = clipped[:last_space]
        if not clipped.endswith((".", "!", "?")):
            clipped += "..."
        summary = clipped

    t_lower = (title + " " + text).lower()
    if "mobile" in t_lower or "cross-modal" in t_lower or "multimodal" in t_lower:
        mechanism = (
            "Adversarial multimodal visual and indirect tool inputs bypassing text-only defenses."
        )
        takeaway = "Autonomous agents require hardened sandboxing, capability caps, and zero ambient trust."
    elif "prompt injection" in t_lower or "indirect" in t_lower or "ipi" in t_lower:
        mechanism = (
            "Untrusted external payload execution inside autonomous agent tool-calling contexts."
        )
        takeaway = "Input data and control flow must be cryptographically partitioned."
    elif (
        "privilege" in t_lower
        or "coding agent" in t_lower
        or "escape" in t_lower
        or "abuse" in t_lower
    ):
        mechanism = "Agent permission boundary escalation permitting unauthorized execution."
        takeaway = "Autonomous developer agents require strict execution sandboxes and zero ambient trust."
    elif "sandbagging" in t_lower or "decepti" in t_lower or "sleeper" in t_lower:
        mechanism = "Strategic capability concealment to circumvent safety screening filters."
        takeaway = "Black-box evaluations cannot guarantee safety against strategically aware models."
    elif "jailbreak" in t_lower or "echo" in t_lower or "multi-turn" in t_lower:
        mechanism = (
            "Iterative feedback and token optimization overcoming post-training refusal boundaries."
        )
        takeaway = "Static refusal alignment degrades rapidly under multi-turn adversarial pressure."
    elif "poison" in t_lower or "kv" in t_lower or "cache" in t_lower:
        mechanism = "Cache state poisoning corrupting model intermediate representations."
        takeaway = "Multi-tenant inference architectures require strict cache isolation guarantees."
    elif "hallucinat" in t_lower or "legal" in t_lower or "avianca" in t_lower:
        mechanism = "Stochastic generation without grounded factual verification."
        takeaway = "High-confidence hallucinations require deterministic factual grounding."
    elif "corrigib" in t_lower or "debate" in t_lower or "alignment" in t_lower:
        mechanism = "Theoretical divergence between training reward objectives and human intent."
        takeaway = "Scalable oversight protocols require verifiable formal constraints."
    else:
        mechanism = "Systemic failure in post-training safety alignment constraints."
        takeaway = "Empirical verification must replace assumption of static model compliance."

    return summary, mechanism, takeaway


def get_merged_timeline_events(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Merge landmark historical events with live ingested database records using adaptive summarization."""
    events_map: Dict[str, Dict[str, Any]] = {
        item["id"]: dict(item) for item in LANDMARK_AI_SAFETY_INCIDENTS
    }

    # If database is provided and exists, load real ingested incidents
    if db_path and Path(db_path).exists():
        try:
            db = IncidentDatabase(db_path)
            db_records = db.get_all(limit=500)
            noise_patterns = [
                "what's the date",
                "frog and toad",
                "cat-belling",
                "on social reality",
                "a critical look at lean4",
            ]
            landmark_titles = {item["title"].lower() for item in LANDMARK_AI_SAFETY_INCIDENTS}

            for r in db_records:
                if r.id in events_map:
                    continue
                # Filter low confidence or casual essays
                if r.confidence_score < 0.70:
                    continue
                if any(p in r.title.lower() for p in noise_patterns):
                    continue

                # Check if duplicate of an existing landmark incident
                r_words = set(re.findall(r"\w{4,}", r.title.lower()))
                is_dup = False
                for lt in landmark_titles:
                    lt_words = set(re.findall(r"\w{4,}", lt))
                    if len(r_words & lt_words) >= 3:
                        is_dup = True
                        break
                if is_dup:
                    continue

                cat = (
                    r.risk_categories[0].value
                    if r.risk_categories
                    else "general_alignment_safety"
                )
                summary, mech, takeaway = adaptively_summarize(r.title, r.summary, cat)

                events_map[r.id] = {
                    "id": r.id,
                    "date": r.published_at.strftime("%Y-%m-%d"),
                    "year": r.published_at.year,
                    "title": r.title,
                    "category": cat,
                    "category_label": cat.replace("_", " ").title(),
                    "severity": r.severity.value,
                    "source": r.source.value.upper(),
                    "url": r.url,
                    "what_happened": summary,
                    "mechanism": mech,
                    "takeaway": takeaway,
                    "full_text": r.summary,
                    "tags": r.tags[:5] if r.tags else ["AI Safety"],
                }
        except Exception:
            pass

    # Sort in reverse chronological order by date
    merged = list(events_map.values())
    merged.sort(key=lambda x: x["date"], reverse=True)
    return merged


def build_timeline_html(db_path: Optional[str] = "data/incidents.db") -> str:
    """Generate self-contained, responsive, interactive HTML timeline."""
    events = get_merged_timeline_events(db_path)
    incidents_json = json.dumps(events)

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chronology of AI Safety Incidents (Post-ChatGPT)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }}
    code, pre, .font-mono {{
      font-family: 'JetBrains Mono', monospace;
    }}

    /* Subtle scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(148, 163, 184, 0.2); border-radius: 9999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(148, 163, 184, 0.4); }}
    
    .timeline-spine::before {{
      content: '';
      position: absolute;
      top: 1.5rem;
      bottom: 2rem;
      left: 1.25rem;
      width: 2px;
      background: linear-gradient(to bottom, #3b82f6, #8b5cf6, #ec4899, rgba(51, 65, 85, 0.2));
    }}
    @media (min-width: 768px) {{
      .timeline-spine::before {{
        left: 50%;
        transform: translateX(-50%);
      }}
    }}

    .glass-card {{
      background: rgba(15, 23, 42, 0.78);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(51, 65, 85, 0.65);
    }}
    .glass-card:hover {{
      border-color: rgba(99, 102, 241, 0.55);
      box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.18);
    }}

    .filter-btn {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
  </style>
</head>
<body class="bg-[#090d16] text-slate-100 antialiased min-h-screen selection:bg-indigo-500 selection:text-white">

  <!-- Ambient background glow elements -->
  <div class="fixed inset-0 pointer-events-none overflow-hidden -z-10">
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
    <div class="absolute top-1/3 -right-40 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-20 left-1/4 w-96 h-96 bg-rose-600/5 rounded-full blur-3xl"></div>
  </div>

  <!-- Header Banner -->
  <header class="border-b border-slate-800/80 bg-slate-950/50 backdrop-blur-md sticky top-0 z-30">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-bold text-white tracking-tight">AI Safety Incident Intelligence</h1>
            <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Live Pipeline</span>
          </div>
          <p class="text-xs text-slate-400">Chronology of Empirical Failures, Jailbreaks, & Governance Milestones (2022–2026)</p>
        </div>
      </div>

      <div class="flex items-center gap-3 text-xs">
        <div class="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
          <span>Curated by <strong class="text-white">Aatman Gupta</strong></span>
        </div>
        <a href="https://github.com/Aatman004/AI-Safety-Incident-Data-Pipeline" target="_blank" class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 shadow-sm">
          <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg>
          <span>Repository</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-6xl mx-auto px-4 sm:px-6 py-8">

    <!-- KPI Summary Dashboard -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
      <div class="glass-card rounded-2xl p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-400">Total Tracked</span>
          <span class="text-[11px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400">2022-2026</span>
        </div>
        <div class="text-2xl sm:text-3xl font-extrabold text-white mt-2" id="kpi-total">45</div>
        <div class="text-xs text-slate-400 mt-1">Live empirical incidents</div>
      </div>

      <div class="glass-card rounded-2xl p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-400">Critical Severity</span>
          <span class="w-2 h-2 rounded-full bg-rose-500"></span>
        </div>
        <div class="text-2xl sm:text-3xl font-extrabold text-rose-400 mt-2" id="kpi-critical">10</div>
        <div class="text-xs text-slate-400 mt-1">High systemic safety risk</div>
      </div>

      <div class="glass-card rounded-2xl p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-400">Prompt Injections</span>
          <span class="w-2 h-2 rounded-full bg-amber-500"></span>
        </div>
        <div class="text-2xl sm:text-3xl font-extrabold text-amber-400 mt-2" id="kpi-injection">15</div>
        <div class="text-xs text-slate-400 mt-1">Direct & indirect exploits</div>
      </div>

      <div class="glass-card rounded-2xl p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-400">Deceptive Alignment</span>
          <span class="w-2 h-2 rounded-full bg-purple-500"></span>
        </div>
        <div class="text-2xl sm:text-3xl font-extrabold text-purple-400 mt-2" id="kpi-deception">6</div>
        <div class="text-xs text-slate-400 mt-1">Sandbagging & sleeper agents</div>
      </div>
    </div>

    <!-- Controls Panel -->
    <div class="glass-card rounded-2xl p-5 mb-10 shadow-lg space-y-4">
      <div class="flex flex-col md:flex-row gap-3 items-center justify-between">
        
        <!-- Search Input -->
        <div class="relative w-full md:w-80">
          <svg class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input
            type="text"
            id="search-input"
            placeholder="Search keyword (e.g. Sleeper, GCG, Sandbagging, CAPTCHA)..."
            class="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
          />
        </div>

        <!-- Sort Order and Reset -->
        <div class="flex items-center gap-2 w-full md:w-auto justify-end">
          <button id="sort-toggle" class="filter-btn text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path></svg>
            <span id="sort-label">Newest First</span>
          </button>
          <button onclick="resetAllFilters()" class="filter-btn text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800/60 text-slate-400 hover:text-rose-400 border border-slate-700">
            Reset
          </button>
        </div>
      </div>

      <!-- Year Buttons -->
      <div class="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-800/60" id="year-filters">
        <span class="text-xs font-medium text-slate-400 mr-2">Year:</span>
        <button class="filter-btn year-btn active text-xs font-semibold px-3 py-1 rounded-lg bg-indigo-600 text-white" data-year="all">All</button>
        <button class="filter-btn year-btn text-xs font-medium px-3 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-year="2022">2022</button>
        <button class="filter-btn year-btn text-xs font-medium px-3 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-year="2023">2023</button>
        <button class="filter-btn year-btn text-xs font-medium px-3 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-year="2024">2024</button>
        <button class="filter-btn year-btn text-xs font-medium px-3 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-year="2025">2025</button>
        <button class="filter-btn year-btn text-xs font-medium px-3 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-year="2026">2026</button>
      </div>

      <!-- Category Filter Pills -->
      <div class="flex flex-wrap items-center gap-1.5 pt-1" id="category-filters">
        <span class="text-xs font-medium text-slate-400 mr-2">Domain:</span>
        <button class="filter-btn cat-btn active text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-700 text-white" data-cat="all">All Domains</button>
        <button class="filter-btn cat-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-cat="prompt_injection">Prompt Injection</button>
        <button class="filter-btn cat-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-cat="deception_reward_hacking">Deception & Sandbagging</button>
        <button class="filter-btn cat-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-cat="agentic_autonomous_failure">Agentic Failure</button>
        <button class="filter-btn cat-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-cat="hallucination_sycophancy">Hallucination</button>
        <button class="filter-btn cat-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/60" data-cat="governance_evaluations">Governance & Evals</button>
      </div>

      <!-- Severity Filter Pills -->
      <div class="flex flex-wrap items-center gap-1.5 pt-1" id="severity-filters">
        <span class="text-xs font-medium text-slate-400 mr-2">Severity:</span>
        <button class="filter-btn sev-btn active text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-700 text-white" data-sev="all">All Severities</button>
        <button class="filter-btn sev-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-rose-400 hover:bg-slate-700 border border-slate-700/60 flex items-center gap-1" data-sev="critical">
          <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Critical
        </button>
        <button class="filter-btn sev-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-amber-400 hover:bg-slate-700 border border-slate-700/60 flex items-center gap-1" data-sev="high">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> High
        </button>
        <button class="filter-btn sev-btn text-xs font-medium px-2.5 py-1 rounded-lg bg-slate-800/80 text-blue-400 hover:bg-slate-700 border border-slate-700/60 flex items-center gap-1" data-sev="medium">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span> Medium
        </button>
      </div>

    </div>

    <!-- Active Filter Counter Banner -->
    <div class="flex items-center justify-between text-xs text-slate-400 mb-6 px-1">
      <div>Showing <span id="count-visible" class="font-bold text-white">45</span> incidents</div>
      <div id="filter-state" class="text-slate-400">Filter: <span class="text-indigo-400">All Time</span></div>
    </div>

    <!-- Chronological Spine Timeline -->
    <div class="relative timeline-spine" id="timeline-container">
      <!-- Injected by JavaScript -->
    </div>

  </main>

  <script>
    const rawEvents = {incidents_json};
    let events = [...rawEvents];

    let activeYear = 'all';
    let activeCategory = 'all';
    let activeSeverity = 'all';
    let searchQuery = '';
    let sortDescending = true; // Newest first

    const container = document.getElementById('timeline-container');
    const searchInput = document.getElementById('search-input');
    const sortToggle = document.getElementById('sort-toggle');
    const sortLabel = document.getElementById('sort-label');
    const countVisible = document.getElementById('count-visible');
    const filterState = document.getElementById('filter-state');

    const severityConfig = {{
      critical: {{ badge: 'bg-rose-500/15 text-rose-400 border-rose-500/30', dot: 'bg-rose-500 ring-rose-500/30' }},
      high: {{ badge: 'bg-amber-500/15 text-amber-400 border-amber-500/30', dot: 'bg-amber-500 ring-amber-500/30' }},
      medium: {{ badge: 'bg-blue-500/15 text-blue-400 border-blue-500/30', dot: 'bg-blue-500 ring-blue-500/30' }},
      low: {{ badge: 'bg-slate-500/15 text-slate-400 border-slate-500/30', dot: 'bg-slate-400 ring-slate-500/30' }}
    }};

    function getAdaptiveSummary(text, maxChars = 210) {{
      if (!text) return '';
      text = text.trim();
      if (text.length <= maxChars) return text;
      let clipped = text.slice(0, maxChars);
      const lastPeriod = clipped.lastIndexOf('.');
      if (lastPeriod > 80) return clipped.slice(0, lastPeriod + 1);
      const lastSpace = clipped.lastIndexOf(' ');
      return (lastSpace > 60 ? clipped.slice(0, lastSpace) : clipped) + '...';
    }}

    function updateKPIs() {{
      const total = rawEvents.length;
      const criticalCount = rawEvents.filter(e => e.severity === 'critical').length;
      const injectionCount = rawEvents.filter(e => e.category === 'prompt_injection').length;
      const deceptionCount = rawEvents.filter(e => e.category === 'deception_reward_hacking').length;

      document.getElementById('kpi-total').textContent = total;
      document.getElementById('kpi-critical').textContent = criticalCount;
      document.getElementById('kpi-injection').textContent = injectionCount;
      document.getElementById('kpi-deception').textContent = deceptionCount;
    }}

    function filterByTag(tag) {{
      searchQuery = tag;
      searchInput.value = tag;
      render();
      window.scrollTo({{ top: searchInput.offsetTop - 90, behavior: 'smooth' }});
    }}

    function render() {{
      let filtered = events.filter(item => {{
        const matchYear = activeYear === 'all' || item.year.toString() === activeYear;
        const matchCat = activeCategory === 'all' || item.category === activeCategory;
        const matchSev = activeSeverity === 'all' || item.severity === activeSeverity;

        const q = searchQuery.toLowerCase().trim();
        const what = (item.what_happened || item.summary || '').toLowerCase();
        const mech = (item.mechanism || '').toLowerCase();
        const take = (item.takeaway || item.impact || '').toLowerCase();
        const full = (item.full_text || '').toLowerCase();
        const src = (item.source || '').toLowerCase();

        const matchSearch = !q ||
          item.title.toLowerCase().includes(q) ||
          what.includes(q) ||
          mech.includes(q) ||
          take.includes(q) ||
          full.includes(q) ||
          src.includes(q) ||
          (item.tags && item.tags.some(t => t.toLowerCase().includes(q)));

        return matchYear && matchCat && matchSev && matchSearch;
      }});

      // Sort
      filtered.sort((a, b) => {{
        return sortDescending ? b.date.localeCompare(a.date) : a.date.localeCompare(b.date);
      }});

      countVisible.textContent = filtered.length;
      filterState.innerHTML = `Showing: <strong class="text-white">${{activeYear === 'all' ? 'All Years' : activeYear}}</strong> | <span class="text-indigo-400">${{activeCategory === 'all' ? 'All Domains' : activeCategory}}</span>`;

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div class="text-center py-20 glass-card rounded-2xl p-8 max-w-xl mx-auto">
            <div class="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <div class="text-base font-semibold text-white">No safety incidents match your filters</div>
            <div class="text-xs text-slate-400 mt-1">Try clearing your search keyword or switching category pills.</div>
            <button onclick="resetAllFilters()" class="mt-4 px-4 py-2 text-xs bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-colors">Reset All Filters</button>
          </div>
        `;
        return;
      }}

      let html = '';
      filtered.forEach((item, index) => {{
        const isEven = index % 2 === 0;
        const sev = severityConfig[item.severity] || severityConfig.medium;
        const rawSynopsis = item.what_happened || item.summary || '';
        const synopsis = getAdaptiveSummary(rawSynopsis, 210);
        const mechanism = item.mechanism || '';
        const takeaway = item.takeaway || item.impact || '';
        const fullText = item.full_text || (rawSynopsis.length > synopsis.length ? rawSynopsis : '');
        const hasFullText = Boolean(fullText && fullText.length > synopsis.length + 30);

        html += `
          <div class="relative pl-8 md:pl-0 mb-8 group">
            <!-- Spine Node Indicator -->
            <div class="absolute left-2.5 md:left-1/2 top-4 -translate-x-1/2 w-4 h-4 rounded-full ${{sev.dot}} ring-4 flex items-center justify-center z-10 transition-transform duration-300 group-hover:scale-125">
              <span class="w-1.5 h-1.5 rounded-full bg-white shadow"></span>
            </div>

            <!-- Content Card -->
            <div class="md:grid md:grid-cols-2 md:gap-10 items-start">
              <div class="${{isEven ? 'md:pr-10' : 'md:col-start-2 md:pl-10'}}">
                <div class="glass-card rounded-2xl p-4 sm:p-5 hover:-translate-y-0.5 transition-all duration-300 border border-slate-800 hover:border-indigo-500/50">
                  
                  <!-- Metadata Header -->
                  <div class="flex items-center justify-between gap-2 mb-2">
                    <div class="flex items-center gap-2">
                      <span class="font-mono text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        ${{item.date}}
                      </span>
                      <span class="text-[11px] font-medium text-slate-400">
                        ${{item.category_label || item.category}}
                      </span>
                    </div>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${{sev.badge}}">
                      ${{item.severity}}
                    </span>
                  </div>

                  <!-- Incident Title -->
                  <h3 class="text-base font-bold text-white leading-snug group-hover:text-indigo-300 transition-colors">
                    <a href="${{item.url}}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 hover:underline">
                      <span>${{item.title}}</span>
                      <svg class="w-3.5 h-3.5 opacity-50 group-hover:opacity-100 transition-opacity shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                  </h3>

                  <!-- Adaptive Summary (Crisp 1-2 sentences) -->
                  <p class="text-xs sm:text-[13px] text-slate-300 mt-2 leading-relaxed font-normal">
                    ${{synopsis}}
                  </p>

                  <!-- Optional Expandable Full Abstract (collapsed by default) -->
                  ${{hasFullText ? `
                  <details class="mt-2 text-xs group/details">
                    <summary class="cursor-pointer text-[11px] text-indigo-400 hover:text-indigo-300 font-medium select-none inline-flex items-center gap-1 transition-colors">
                      <svg class="w-3 h-3 group-open/details:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                      <span>Full Abstract / Source</span>
                    </summary>
                    <div class="mt-2 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 leading-relaxed font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                      ${{fullText}}
                    </div>
                  </details>` : ''}}

                  <!-- Structured Analysis (Technical Mechanism & Safety Takeaway) -->
                  <div class="mt-3 pt-2.5 border-t border-slate-800/80 space-y-2">
                    ${{mechanism ? `
                    <div class="rounded-xl bg-slate-900/80 border border-slate-800/80 p-2.5">
                      <div class="text-[10px] uppercase font-bold tracking-wider text-indigo-400 flex items-center gap-1.5 mb-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                        Root Mechanism
                      </div>
                      <div class="text-xs text-slate-300 leading-normal font-normal">
                        ${{mechanism}}
                      </div>
                    </div>` : ''}}

                    ${{takeaway ? `
                    <div class="rounded-xl bg-slate-900/80 border border-slate-800/80 p-2.5">
                      <div class="text-[10px] uppercase font-bold tracking-wider text-amber-400 flex items-center gap-1.5 mb-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                        Safety Takeaway
                      </div>
                      <div class="text-xs text-slate-300 leading-normal font-normal">
                        ${{takeaway}}
                      </div>
                    </div>` : ''}}
                  </div>

                  <!-- Footer: Source & Interactive Tags -->
                  <div class="mt-3 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
                    <div class="truncate max-w-[220px]" title="${{item.source}}">
                      <span class="text-slate-400">Origin:</span> <span class="text-slate-300 font-medium">${{item.source}}</span>
                    </div>
                    <div class="flex flex-wrap gap-1">
                      ${{item.tags ? item.tags.map(t => `<button onclick="filterByTag('${{t}}')" class="text-[10px] px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-indigo-300 border border-slate-700/60 transition-colors">#${{t}}</button>`).join('') : ''}}
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        `;
      }});

      container.innerHTML = html;
    }}

    function resetAllFilters() {{
      activeYear = 'all';
      activeCategory = 'all';
      activeSeverity = 'all';
      searchQuery = '';
      searchInput.value = '';
      
      document.querySelectorAll('.year-btn').forEach(b => b.classList.toggle('active', b.dataset.year === 'all'));
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.toggle('active', b.dataset.cat === 'all'));
      document.querySelectorAll('.sev-btn').forEach(b => b.classList.toggle('active', b.dataset.sev === 'all'));

      render();
    }}

    // Event Listeners
    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value;
      render();
    }});

    sortToggle.addEventListener('click', () => {{
      sortDescending = !sortDescending;
      sortLabel.textContent = sortDescending ? 'Newest First' : 'Oldest First';
      render();
    }});

    // Year buttons
    document.querySelectorAll('.year-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.year-btn').forEach(b => {{
          b.classList.remove('active', 'bg-indigo-600', 'text-white');
          b.classList.add('bg-slate-800/80', 'text-slate-300');
        }});
        btn.classList.add('active', 'bg-indigo-600', 'text-white');
        btn.classList.remove('bg-slate-800/80', 'text-slate-300');
        activeYear = btn.dataset.year;
        render();
      }});
    }});

    // Category buttons
    document.querySelectorAll('.cat-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.cat-btn').forEach(b => {{
          b.classList.remove('active', 'bg-slate-700', 'text-white');
          b.classList.add('bg-slate-800/80', 'text-slate-300');
        }});
        btn.classList.add('active', 'bg-slate-700', 'text-white');
        btn.classList.remove('bg-slate-800/80', 'text-slate-300');
        activeCategory = btn.dataset.cat;
        render();
      }});
    }});

    // Severity buttons
    document.querySelectorAll('.sev-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.sev-btn').forEach(b => {{
          b.classList.remove('active', 'bg-slate-700', 'text-white');
          b.classList.add('bg-slate-800/80');
        }});
        btn.classList.add('active', 'bg-slate-700', 'text-white');
        activeSeverity = btn.dataset.sev;
        render();
      }});
    }});

    updateKPIs();
    render();
  </script>
</body>
</html>
"""
