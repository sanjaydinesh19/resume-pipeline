"""Stage 1 — ATS Diagnoser: Scans resume like ATS software and flags issues."""
import json
from .claude_client import ask_claude
from .prompts import DIAGNOSER_SYSTEM, DIAGNOSER_USER
from .ui import (
    console, stage_header, section_title, divider,
    severity_table, score_panel, spinner, success, warn
)


def run_diagnoser(resume_text: str, job_description: str = "Not specified") -> dict:
    """Run ATS diagnosis on resume. Returns structured results dict."""
    stage_header("diagnose")

    with spinner("Scanning resume with ATS engine..."):
        raw = ask_claude(
            DIAGNOSER_SYSTEM,
            DIAGNOSER_USER.format(resume_text=resume_text, job_description=job_description)
        )
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"[red]Failed to parse ATS response. Raw output:[/red]\n{raw}")
        return {}

    _display_diagnosis(result)
    return result


def _display_diagnosis(result: dict):
    # ATS Score
    ats_score = result.get("ats_score", 0)
    color = "green" if ats_score >= 75 else ("yellow" if ats_score >= 50 else "red")
    score_panel("ATS Score", ats_score, 100, color)

    # Summary
    section_title("📋 Overall Assessment")
    console.print(result.get("summary", ""))

    # Strengths
    strengths = result.get("strengths", [])
    if strengths:
        section_title("✅ Strengths")
        for s in strengths:
            console.print(f"  [green]•[/green] {s}")

    # Critical fixes
    critical = result.get("critical_fixes", [])
    if critical:
        section_title("🔴 Critical Fixes Required")
        for c in critical:
            console.print(f"  [red]•[/red] {c}")

    # Flags table
    flags = result.get("flags", [])
    if flags:
        section_title("🔍 Detailed ATS Flags")
        severity_table(flags)

    divider()
    success(f"Diagnosis complete — {len(flags)} issues found.")
