"""Command Line Interface for the AI Safety Incident & Threat Intelligence Pipeline."""

import csv
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from incident_pipeline.collectors.aiid import AIIDCollector
from incident_pipeline.collectors.arxiv import ArxivCollector
from incident_pipeline.collectors.rss import SafetyRSSCollector
from incident_pipeline.reporting.generator import SafetyReportGenerator
from incident_pipeline.storage.database import IncidentDatabase

app = typer.Typer(
    help="AI Safety Incident & Research Threat Intelligence Pipeline CLI",
    add_completion=False,
)
console = Console()


@app.command()
def ingest(
    limit: int = typer.Option(25, "--limit", "-l", help="Max records per collector source"),
    source: str | None = typer.Option(
        None, "--source", "-s", help="Specific collector to run: arxiv, aiid, rss (default: all)"
    ),
    db_path: str = typer.Option("data/incidents.db", "--db", help="Path to SQLite database file"),
):
    """Ingest AI safety incidents and research preprints from global sources."""
    console.print(
        f"[bold cyan]Initiating AI Safety Ingestion Pipeline (Target Limit: {limit})...[/bold cyan]"
    )
    db = IncidentDatabase(db_path)

    collectors = []
    if not source or source.lower() == "arxiv":
        collectors.append(ArxivCollector())
    if not source or source.lower() == "aiid":
        collectors.append(AIIDCollector())
    if not source or source.lower() in ("rss", "safety_rss"):
        collectors.append(SafetyRSSCollector())

    total_inserted = 0
    total_skipped = 0

    table = Table(
        title="Collector Ingestion Summary", show_header=True, header_style="bold magenta"
    )
    table.add_column("Source", style="cyan")
    table.add_column("Collected", justify="right")
    table.add_column("New Inserted", justify="right", style="green")
    table.add_column("Duplicates Skipped", justify="right", style="yellow")

    for col in collectors:
        with console.status(f"[bold green]Collecting from {col.name}..."):
            records = col.collect(limit=limit)
            inserted, skipped = db.save_records(records)
            total_inserted += inserted
            total_skipped += skipped
            table.add_row(col.name.upper(), str(len(records)), str(inserted), str(skipped))

    console.print(table)
    console.print(
        f"\n[bold green]Ingestion complete![/bold green] "
        f"[green]{total_inserted} new records added[/green], "
        f"[yellow]{total_skipped} existing duplicates retained.[/yellow]"
    )


@app.command()
def search(
    query: str = typer.Argument(..., help="Search keyword or term (FTS5 enabled)"),
    category: str | None = typer.Option(None, "--category", "-c", help="Filter by risk category"),
    severity: str | None = typer.Option(None, "--severity", "-s", help="Filter by severity level"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to return"),
    db_path: str = typer.Option("data/incidents.db", "--db", help="Path to SQLite database file"),
):
    """Full-text search indexed AI safety incidents and research."""
    db = IncidentDatabase(db_path)
    records = db.search(query=query, category=category, severity=severity, limit=limit)

    if not records:
        console.print(f"[yellow]No matching records found for query:[/yellow] '{query}'")
        return

    table = Table(
        title=f"Search Results for: '{query}'", show_header=True, header_style="bold cyan"
    )
    table.add_column("Date", style="dim", width=12)
    table.add_column("Severity", width=10)
    table.add_column("Primary Category", style="magenta", width=22)
    table.add_column("Title", style="bold white")

    for r in records:
        sev_color = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(r.severity.value, "white")
        cat = r.risk_categories[0].value.replace("_", " ") if r.risk_categories else "general"
        table.add_row(
            r.published_at.strftime("%Y-%m-%d"),
            f"[{sev_color}]{r.severity.value.upper()}[/{sev_color}]",
            cat,
            r.title,
        )

    console.print(table)


@app.command()
def stats(
    db_path: str = typer.Option("data/incidents.db", "--db", help="Path to SQLite database file"),
):
    """Display overall distribution and metrics across all indexed records."""
    db = IncidentDatabase(db_path)
    statistics = db.get_statistics()

    console.print(f"[bold cyan]Total Tracked Records:[/bold cyan] {statistics['total_records']}")

    cat_table = Table(
        title="Risk Category Distribution", show_header=True, header_style="bold green"
    )
    cat_table.add_column("Risk Category", style="cyan")
    cat_table.add_column("Count", justify="right")
    for cat, count in statistics.get("by_category", {}).items():
        cat_table.add_row(cat.replace("_", " ").title(), str(count))
    console.print(cat_table)

    sev_table = Table(title="Severity Distribution", show_header=True, header_style="bold yellow")
    sev_table.add_column("Severity Level", style="cyan")
    sev_table.add_column("Count", justify="right")
    for sev, count in statistics.get("by_severity", {}).items():
        sev_table.add_row(sev.upper(), str(count))
    console.print(sev_table)


@app.command()
def report(
    output: str | None = typer.Option(
        None, "--output", "-o", help="Optional filepath to save the report (e.g., briefing.md)"
    ),
    format_type: str = typer.Option(
        "markdown", "--format", "-f", help="Report format: markdown or json"
    ),
    db_path: str = typer.Option("data/incidents.db", "--db", help="Path to SQLite database file"),
):
    """Generate a structured AI Safety Intelligence Briefing."""
    db = IncidentDatabase(db_path)
    generator = SafetyReportGenerator(db)

    content = (
        generator.generate_markdown()
        if format_type.lower() == "markdown"
        else generator.generate_json()
    )

    if output:
        generator.export_report(output, format_type=format_type)
        console.print(
            f"[bold green]Report successfully generated and saved to:[/bold green] {output}"
        )
    else:
        console.print(content)


@app.command()
def export(
    output: str = typer.Option(..., "--output", "-o", help="Output filepath (e.g., incidents.csv)"),
    format_type: str = typer.Option("csv", "--format", "-f", help="Format: csv or json"),
    db_path: str = typer.Option("data/incidents.db", "--db", help="Path to SQLite database file"),
):
    """Export all stored records to CSV or JSON for external analysis."""
    db = IncidentDatabase(db_path)
    records = db.get_all(limit=5000)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if format_type.lower() == "csv":
        with open(out_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "title",
                    "url",
                    "source",
                    "source_id",
                    "published_at",
                    "severity",
                    "primary_category",
                    "confidence_score",
                    "tags",
                    "summary",
                ]
            )
            for r in records:
                cat = (
                    r.risk_categories[0].value if r.risk_categories else "general_alignment_safety"
                )
                writer.writerow(
                    [
                        r.id,
                        r.title,
                        r.url,
                        r.source.value,
                        r.source_id,
                        r.published_at.isoformat(),
                        r.severity.value,
                        cat,
                        r.confidence_score,
                        ";".join(r.tags),
                        r.summary,
                    ]
                )
        console.print(f"[bold green]Exported {len(records)} records to CSV:[/bold green] {output}")
    else:
        generator = SafetyReportGenerator(db)
        out_path.write_text(generator.generate_json(), encoding="utf-8")
        console.print(f"[bold green]Exported {len(records)} records to JSON:[/bold green] {output}")


@app.command()
def timeline(
    output: str = typer.Option(
        "reports/ai_safety_timeline.html",
        "--output",
        "-o",
        help="Output filepath for HTML timeline visualization",
    ),
):
    """Generate an interactive HTML timeline of AI Safety incidents since ChatGPT."""
    from incident_pipeline.reporting.timeline_html import build_timeline_html

    html_content = build_timeline_html()
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    console.print(
        f"[bold green]Interactive AI Safety Timeline successfully generated:[/bold green] [white]{output}[/white]"
    )


if __name__ == "__main__":
    app()
