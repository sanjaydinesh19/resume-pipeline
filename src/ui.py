"""Terminal UI helpers using Rich."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from contextlib import contextmanager

console = Console()

STAGE_COLORS = {
    "diagnose":  "#FF6B6B",
    "analyse":   "#FFD93D",
    "rewrite":   "#6BCB77",
    "interview": "#4D96FF",
}

STAGE_ICONS = {
    "diagnose":  "🔍",
    "analyse":   "📊",
    "rewrite":   "✍️ ",
    "interview": "🎯",
}

STAGE_TITLES = {
    "diagnose":  "Stage 1 — ATS Diagnoser",
    "analyse":   "Stage 2 — Job Description Analyser",
    "rewrite":   "Stage 3 — Resume Rewriter (Google XYZ)",
    "interview": "Stage 4 — Hiring Manager Interview",
}


def banner():
    console.print()
    console.print(Panel.fit(
        "[bold white]RESUME PIPELINE[/bold white]\n"
        "[dim]AI-Powered Resume Optimization · 4-Stage Pipeline[/dim]",
        border_style="bright_blue",
        padding=(1, 4),
    ))
    console.print()


def stage_header(stage: str):
    color = STAGE_COLORS.get(stage, "white")
    icon = STAGE_ICONS.get(stage, "▶")
    title = STAGE_TITLES.get(stage, stage)
    console.print()
    console.print(Panel(
        f"[bold]{icon}  {title}[/bold]",
        border_style=color,
        padding=(0, 2),
    ))
    console.print()


def section_title(text: str):
    console.print(f"\n[bold underline]{text}[/bold underline]\n")


def info(msg: str):
    console.print(f"[cyan]ℹ[/cyan]  {msg}")


def success(msg: str):
    console.print(f"[green]✔[/green]  {msg}")


def warn(msg: str):
    console.print(f"[yellow]⚠[/yellow]  {msg}")


def error(msg: str):
    console.print(f"[red]✘[/red]  {msg}")


def divider():
    console.print("[dim]" + "─" * 72 + "[/dim]")


def print_markdown_block(text: str):
    """Print raw text with basic rich markup passthrough."""
    console.print(text)


def prompt_input(prompt: str) -> str:
    return console.input(f"[bold cyan]{prompt}[/bold cyan] ")


def ask_continue(label: str = "Continue to next stage?") -> bool:
    answer = console.input(f"\n[bold yellow]{label} (y/n): [/bold yellow]").strip().lower()
    return answer in ("y", "yes", "")


@contextmanager
def spinner(label: str):
    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn(f"[cyan]{label}[/cyan]"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("", total=None)
        yield


def severity_table(flags: list[dict]):
    """Render a table of ATS flags: [{section, issue, severity, suggestion}]"""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
    table.add_column("Section", style="bold", width=18)
    table.add_column("Issue", width=32)
    table.add_column("Sev", width=6, justify="center")
    table.add_column("Suggestion", width=38)

    sev_colors = {"🔴": "red", "🟡": "yellow", "🟢": "green"}

    for flag in flags:
        sev = flag.get("severity", "🟡")
        color = sev_colors.get(sev, "white")
        table.add_row(
            flag.get("section", ""),
            flag.get("issue", ""),
            f"[{color}]{sev}[/{color}]",
            flag.get("suggestion", ""),
        )
    console.print(table)


def keyword_table(keywords: list[dict]):
    """Render keyword gap table: [{keyword, frequency, category, in_resume}]"""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
    table.add_column("Keyword / Skill", style="bold", width=28)
    table.add_column("JD Freq", width=10, justify="right")
    table.add_column("Category", width=18)
    table.add_column("In Resume?", width=12, justify="center")

    for kw in keywords:
        present = kw.get("in_resume", False)
        status = "[green]✔[/green]" if present else "[red]✘ Missing[/red]"
        table.add_row(
            kw.get("keyword", ""),
            str(kw.get("frequency", "")),
            kw.get("category", ""),
            status,
        )
    console.print(table)


def score_panel(label: str, score: int, out_of: int = 10, color: str = "cyan"):
    bar_filled = int((score / out_of) * 20)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    console.print(Panel(
        f"[bold]{label}[/bold]\n\n"
        f"[{color}]{bar}[/{color}]  [{color}]{score}/{out_of}[/{color}]",
        border_style=color,
        padding=(0, 2),
    ))
