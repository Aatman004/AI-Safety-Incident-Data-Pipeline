"""Generates an intentional, tasteful interactive HTML timeline visualization for AI Safety incidents."""

import json

from incident_pipeline.timeline_data import LANDMARK_AI_SAFETY_INCIDENTS


def build_timeline_html() -> str:
    """Generate self-contained, responsive, interactive HTML timeline."""
    incidents_json = json.dumps(LANDMARK_AI_SAFETY_INCIDENTS)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chronology of AI Safety Incidents (Post-ChatGPT)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Custom scrollbar and subtle accents */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(150, 150, 150, 0.25); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(150, 150, 150, 0.45); }}
    
    .timeline-spine::before {{
      content: '';
      position: absolute;
      top: 1.5rem;
      bottom: 2rem;
      left: 1.25rem;
      width: 2px;
      background: linear-gradient(to bottom, var(--border), rgba(150,150,150,0.15));
    }}
    @media (min-width: 768px) {{
      .timeline-spine::before {{
        left: 50%;
        transform: translateX(-50%);
      }}
    }}
  </style>
</head>
<body class="bg-[var(--background,#0f1117)] text-[var(--foreground,#f1f5f9)] antialiased min-h-screen p-4 sm:p-8">

  <!-- Header Section -->
  <div class="max-w-6xl mx-auto mb-10">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[var(--border,#334155)] pb-6">
      <div>
        <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 mb-3">
          <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
          AI Safety Threat Intelligence
        </div>
        <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-[var(--foreground,#f8fafc)]">
          Chronology of AI Safety Incidents
        </h1>
        <p class="text-sm sm:text-base text-[var(--muted-foreground,#94a3b8)] mt-2 max-w-2xl">
          An empirical historical record of landmark safety failures, jailbreak discoveries, deceptive alignment observations, and frontier governance milestones from the release of ChatGPT (Nov 2022) to 2026.
        </p>
      </div>
      <div class="flex items-center gap-4 text-xs text-[var(--muted-foreground,#94a3b8)]">
        <div>Curated by <span class="font-semibold text-[var(--foreground,#f8fafc)]">Aatman Gupta</span></div>
        <div class="h-4 w-px bg-[var(--border,#334155)]"></div>
        <div>Total Incidents: <span id="stat-total" class="font-bold text-[var(--foreground,#f8fafc)]">15</span></div>
      </div>
    </div>

    <!-- Metrics Cards Overview -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 my-6">
      <div class="bg-[var(--card,#1e293b)]/60 border border-[var(--border,#334155)] rounded-xl p-3 sm:p-4">
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] font-medium">Timeline Window</div>
        <div class="text-lg font-bold text-[var(--foreground,#f8fafc)] mt-1">2022 — 2026</div>
        <div class="text-xs text-blue-400 mt-0.5">Post-ChatGPT Era</div>
      </div>
      <div class="bg-[var(--card,#1e293b)]/60 border border-[var(--border,#334155)] rounded-xl p-3 sm:p-4">
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] font-medium">Critical Breaches</div>
        <div class="text-lg font-bold text-red-400 mt-1" id="stat-critical">5</div>
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] mt-0.5">High systemic risk</div>
      </div>
      <div class="bg-[var(--card,#1e293b)]/60 border border-[var(--border,#334155)] rounded-xl p-3 sm:p-4">
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] font-medium">Top Vulnerability</div>
        <div class="text-lg font-bold text-[var(--foreground,#f8fafc)] mt-1">Prompt Injection</div>
        <div class="text-xs text-amber-400 mt-0.5">33% of incidents</div>
      </div>
      <div class="bg-[var(--card,#1e293b)]/60 border border-[var(--border,#334155)] rounded-xl p-3 sm:p-4">
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] font-medium">Deceptive Alignment</div>
        <div class="text-lg font-bold text-purple-400 mt-1">3 Milestones</div>
        <div class="text-xs text-[var(--muted-foreground,#94a3b8)] mt-0.5">Sandbagging & Sleeper Agents</div>
      </div>
    </div>

    <!-- Interactive Filters & Search -->
    <div class="bg-[var(--card,#1e293b)]/80 border border-[var(--border,#334155)] rounded-xl p-4 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
      <!-- Search Input -->
      <div class="w-full md:w-72 relative">
        <input
          type="text"
          id="search-input"
          placeholder="Search incidents, papers, tags..."
          class="w-full bg-[var(--background,#0f1117)] border border-[var(--border,#334155)] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground,#f8fafc)] placeholder-[var(--muted-foreground,#94a3b8)] focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      <!-- Year Filter Pills -->
      <div class="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0" id="year-filters">
        <button class="filter-year active px-2.5 py-1 rounded-md text-xs font-medium bg-blue-600 text-white" data-year="all">All Years</button>
        <button class="filter-year px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--background,#0f1117)] text-[var(--muted-foreground,#94a3b8)] hover:text-[var(--foreground,#f8fafc)] border border-[var(--border,#334155)]" data-year="2022">2022</button>
        <button class="filter-year px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--background,#0f1117)] text-[var(--muted-foreground,#94a3b8)] hover:text-[var(--foreground,#f8fafc)] border border-[var(--border,#334155)]" data-year="2023">2023</button>
        <button class="filter-year px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--background,#0f1117)] text-[var(--muted-foreground,#94a3b8)] hover:text-[var(--foreground,#f8fafc)] border border-[var(--border,#334155)]" data-year="2024">2024</button>
        <button class="filter-year px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--background,#0f1117)] text-[var(--muted-foreground,#94a3b8)] hover:text-[var(--foreground,#f8fafc)] border border-[var(--border,#334155)]" data-year="2025">2025</button>
        <button class="filter-year px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--background,#0f1117)] text-[var(--muted-foreground,#94a3b8)] hover:text-[var(--foreground,#f8fafc)] border border-[var(--border,#334155)]" data-year="2026">2026</button>
      </div>

      <!-- Category Filter Dropdown -->
      <div class="w-full md:w-auto">
        <select
          id="category-select"
          class="w-full md:w-auto bg-[var(--background,#0f1117)] border border-[var(--border,#334155)] rounded-lg px-3 py-1.5 text-xs text-[var(--foreground,#f8fafc)] focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Safety Categories</option>
          <option value="prompt_injection">Prompt Injection & Jailbreaks</option>
          <option value="deception_reward_hacking">Deception & Sandbagging</option>
          <option value="agentic_autonomous_failure">Autonomous Agent Failures</option>
          <option value="hallucination_sycophancy">Hallucination & Legal Liability</option>
          <option value="governance_evaluations">Governance & Safety Evals</option>
          <option value="general_alignment_safety">Mechanistic Interpretability</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Timeline Container -->
  <div class="max-w-5xl mx-auto relative timeline-spine pb-16" id="timeline-container">
    <!-- Populated by JavaScript -->
  </div>

  <!-- Footer -->
  <div class="max-w-6xl mx-auto text-center border-t border-[var(--border,#334155)] pt-8 pb-12 text-xs text-[var(--muted-foreground,#94a3b8)]">
    Crafted as part of the <span class="font-semibold text-[var(--foreground,#f8fafc)]">AI Safety Incident Data Pipeline</span> portfolio project by Aatman Gupta.
  </div>

  <script>
    const incidents = {incidents_json};

    let activeYear = 'all';
    let activeCategory = 'all';
    let searchQuery = '';

    const container = document.getElementById('timeline-container');
    const searchInput = document.getElementById('search-input');
    const categorySelect = document.getElementById('category-select');
    const yearButtons = document.querySelectorAll('.filter-year');

    const severityConfig = {{
      critical: {{ badge: 'bg-rose-500/15 text-rose-400 border-rose-500/30', dot: 'bg-rose-500 ring-rose-500/20' }},
      high: {{ badge: 'bg-amber-500/15 text-amber-400 border-amber-500/30', dot: 'bg-amber-500 ring-amber-500/20' }},
      medium: {{ badge: 'bg-blue-500/15 text-blue-400 border-blue-500/30', dot: 'bg-blue-500 ring-blue-500/20' }},
      low: {{ badge: 'bg-slate-500/15 text-slate-400 border-slate-500/30', dot: 'bg-slate-400 ring-slate-500/20' }}
    }};

    function render() {{
      const filtered = incidents.filter(item => {{
        const matchYear = activeYear === 'all' || item.year.toString() === activeYear;
        const matchCat = activeCategory === 'all' || item.category === activeCategory;
        const query = searchQuery.toLowerCase();
        const matchSearch = !query || 
          item.title.toLowerCase().includes(query) ||
          item.summary.toLowerCase().includes(query) ||
          item.impact.toLowerCase().includes(query) ||
          item.tags.some(t => t.toLowerCase().includes(query));
        return matchYear && matchCat && matchSearch;
      }});

      if (filtered.length === 0) {{
        container.innerHTML = `
          <div class="text-center py-16 bg-[var(--card,#1e293b)]/40 border border-[var(--border,#334155)] rounded-2xl p-8">
            <div class="text-sm text-[var(--muted-foreground,#94a3b8)]">No incidents found matching your criteria.</div>
            <button onclick="resetFilters()" class="mt-3 px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md font-medium hover:bg-blue-500 transition-colors">Reset Filters</button>
          </div>
        `;
        return;
      }}

      let html = '';
      filtered.forEach((item, index) => {{
        const isEven = index % 2 === 0;
        const sev = severityConfig[item.severity] || severityConfig.medium;

        html += `
          <div class="relative pl-10 md:pl-0 mb-8 sm:mb-12 group">
            <!-- Central Node / Dot -->
            <div class="absolute left-3.5 md:left-1/2 top-4 -translate-x-1/2 w-4 h-4 rounded-full ${{sev.dot}} ring-4 flex items-center justify-center z-10 transition-transform duration-300 group-hover:scale-125">
              <span class="w-1.5 h-1.5 rounded-full bg-white"></span>
            </div>

            <!-- Card Layout alternating left/right on md screens -->
            <div class="md:grid md:grid-cols-2 md:gap-8 items-start">
              <div class="${{isEven ? 'md:pr-10' : 'md:col-start-2 md:pl-10'}}">
                <div class="bg-[var(--card,#1e293b)] border border-[var(--border,#334155)] rounded-xl p-5 shadow-sm hover:shadow-md hover:border-slate-500 transition-all duration-200">
                  
                  <!-- Metadata Header -->
                  <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <span class="font-mono text-xs font-semibold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                      ${{item.date}}
                    </span>
                    <span class="text-xs px-2 py-0.5 rounded-full font-medium border ${{sev.badge}}">
                      ${{item.severity.toUpperCase()}}
                    </span>
                  </div>

                  <!-- Title -->
                  <h3 class="text-base sm:text-lg font-bold text-[var(--foreground,#f8fafc)] leading-snug">
                    <a href="${{item.url}}" target="_blank" class="hover:text-blue-400 transition-colors inline-flex items-center gap-1">
                      ${{item.title}}
                      <svg class="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                  </h3>

                  <!-- Source attribution -->
                  <div class="text-xs text-[var(--muted-foreground,#94a3b8)] mt-1 font-medium">
                    Source: <span class="text-slate-300">${{item.source}}</span>
                  </div>

                  <!-- Summary -->
                  <p class="text-xs sm:text-sm text-slate-300 mt-3 leading-relaxed">
                    ${{item.summary}}
                  </p>

                  <!-- Impact Callout -->
                  <div class="mt-3.5 pt-3 border-t border-[var(--border,#334155)]/60 text-xs">
                    <span class="font-semibold text-amber-400/90">Safety Implication:</span>
                    <span class="text-[var(--muted-foreground,#94a3b8)] ml-1">${{item.impact}}</span>
                  </div>

                  <!-- Tags -->
                  <div class="flex flex-wrap gap-1.5 mt-3 pt-2">
                    ${{item.tags.map(tag => `<span class="text-xs px-2 py-0.5 rounded bg-[var(--background,#0f1117)] text-slate-400 border border-[var(--border,#334155)]">#${{tag}}</span>`).join('')}}
                  </div>

                </div>
              </div>
            </div>
          </div>
        `;
      }});

      container.innerHTML = html;
    }}

    function resetFilters() {{
      activeYear = 'all';
      activeCategory = 'all';
      searchQuery = '';
      searchInput.value = '';
      categorySelect.value = 'all';
      yearButtons.forEach(b => {{
        b.classList.remove('bg-blue-600', 'text-white');
        b.classList.add('bg-[var(--background,#0f1117)]', 'text-[var(--muted-foreground,#94a3b8)]');
        if (b.dataset.year === 'all') {{
          b.classList.add('bg-blue-600', 'text-white');
          b.classList.remove('bg-[var(--background,#0f1117)]', 'text-[var(--muted-foreground,#94a3b8)]');
        }}
      }});
      render();
    }}

    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value;
      render();
    }});

    categorySelect.addEventListener('change', (e) => {{
      activeCategory = e.target.value;
      render();
    }});

    yearButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        yearButtons.forEach(b => {{
          b.classList.remove('bg-blue-600', 'text-white');
          b.classList.add('bg-[var(--background,#0f1117)]', 'text-[var(--muted-foreground,#94a3b8)]');
        }});
        btn.classList.add('bg-blue-600', 'text-white');
        btn.classList.remove('bg-[var(--background,#0f1117)]', 'text-[var(--muted-foreground,#94a3b8)]');
        activeYear = btn.dataset.year;
        render();
      }});
    }});

    render();
  </script>
</body>
</html>
"""
