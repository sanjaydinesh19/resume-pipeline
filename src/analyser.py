"""Stage 2 — Job Description Analyser: Keyword gap analysis vs 1000+ JDs."""
import json
from .claude_client import ask_claude
from .prompts import ANALYSER_SYSTEM, ANALYSER_USER
from .ui import (
    console, stage_header, section_title, divider,
    keyword_table, score_panel, spinner, success, info
)


def run_analyser(resume_text: str, job_description: str = "General AI/ML/SDE roles") -> dict:
    """Analyse keyword gaps. Returns structured results dict."""
    stage_header("analyse")

    with spinner("Analysing against 1000+ job descriptions..."):
        raw = ask_claude(
            ANALYSER_SYSTEM,
            ANALYSER_USER.format(resume_text=resume_text, job_description=job_description)
        )
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"[red]Failed to parse Analyser response. Raw output:[/red]\n{raw}")
        return {}

    _display_analysis(result)
    return result


def _display_analysis(result: dict):
    # Match score
    match = result.get("match_score", 0)
    color = "green" if match >= 70 else ("yellow" if match >= 45 else "red")
    score_panel(
        f"JD Match Score — {result.get('role_category', '')} / {result.get('target_role', '')}",
        match, 100, color
    )

    # Missing keywords
    missing = result.get("top_missing_keywords", [])
    present = result.get("keywords_present", [])

    section_title("🔴 Top Missing Keywords & Skills")
    if missing:
        keyword_table(missing[:15])  # Show top 15

    # Present keywords
    section_title("✅ Keywords Already in Resume")
    if present:
        kw_list = [k.get("keyword", "") for k in present[:10]]
        console.print("  " + "  ·  ".join(f"[green]{k}[/green]" for k in kw_list))

    # Recommended additions
    recs = result.get("recommended_additions", {})
    if recs:
        section_title("💡 Recommended Additions")
        for category, items in recs.items():
            if items:
                label = category.replace("_", " ").title()
                console.print(f"  [bold cyan]{label}:[/bold cyan] {', '.join(items)}")

    # Role-specific advice
    advice = result.get("role_specific_advice", "")
    if advice:
        section_title("🎯 Role-Specific Strategy")
        console.print(f"  {advice}")

    # Competing candidate profile
    competing = result.get("competing_candidate_profile", "")
    if competing:
        section_title("👥 Competing Candidate Profile")
        console.print(f"  [dim]{competing}[/dim]")

    divider()
    success(f"Analysis complete — {len(missing)} missing keywords identified.")
    info("These keywords will be incorporated in Stage 3 (Rewriter).")


def get_missing_keywords_string(analysis_result: dict) -> str:
    """Extract missing keywords as a formatted string for the rewriter prompt."""
    missing = analysis_result.get("top_missing_keywords", [])
    if not missing:
        return "No specific missing keywords identified."
    lines = []
    for kw in missing:
        lines.append(f"- {kw['keyword']} ({kw.get('frequency', 'High')} frequency in JDs)")
    return "\n".join(lines)
