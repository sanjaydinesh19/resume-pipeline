#!/usr/bin/env python3
"""
Resume Pipeline — AI-Powered 4-Stage Resume Optimization
=========================================================
Usage:
  python resume_pipeline.py                                      # interactive
  python resume_pipeline.py --resume resume.pdf                  # full pipeline
  python resume_pipeline.py --resume resume.pdf --job "ML at Google"
  python resume_pipeline.py --resume resume.pdf --stage diagnose
  python resume_pipeline.py --resume resume.pdf --stage analyse
  python resume_pipeline.py --resume resume.pdf --stage rewrite --job "SDE at OpenAI"
  python resume_pipeline.py --resume resume.pdf --stage interview
"""

import sys
import re
import shutil
from pathlib import Path
import typer
from typing import Optional
from enum import Enum

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui import console, banner, info, warn, error, ask_continue, prompt_input
from src.pdf_reader import extract_resume_text
from src.diagnoser import run_diagnoser
from src.analyser import run_analyser, get_missing_keywords_string
from src.rewriter import run_rewriter
from src.hiring_manager import run_interview

app = typer.Typer(add_completion=False, help="AI Resume Pipeline — 4-stage optimization tool")


class Stage(str, Enum):
    all = "all"
    diagnose = "diagnose"
    analyse = "analyse"
    rewrite = "rewrite"
    interview = "interview"


def _next_output_name(output_dir: str) -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    nums = [
        int(m.group(1))
        for f in out.glob("Resume *.tex")
        if (m := re.match(r"Resume (\d+)", f.stem))
    ]
    return f"Resume {max(nums, default=0) + 1}"


def _get_resume_path(resume: Optional[str]) -> str:
    if resume:
        return resume
    console.print("\n[bold]No resume file specified.[/bold]")
    path = prompt_input("Enter path to your resume (.pdf / .tex / .txt):")
    return path.strip()


def _get_job_description(job: Optional[str]) -> str:
    if job:
        return job
    console.print()
    info("Enter a job description or role target for tailored analysis.")
    info("Examples: 'ML Engineer at DeepMind', 'Robotics SWE at Boston Dynamics'")
    info("Or paste a full JD. Press Enter twice (empty line) to finish.\n")
    lines = []
    while True:
        line = console.input("  ")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    jd = "\n".join(lines).strip()
    return jd if jd else "General AI/ML/SDE roles"


@app.command()
def main(
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Path to resume file"),
    job: Optional[str] = typer.Option(None, "--job", "-j", help="Job title or description"),
    stage: Stage = typer.Option(Stage.all, "--stage", "-s", help="Which stage to run"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory for LaTeX file"),
):
    """AI-Powered Resume Pipeline — Diagnose → Analyse → Rewrite → Interview"""

    banner()

    # ── Check Claude Code CLI ─────────────────────────────────────────────────
    if not shutil.which("claude"):
        error("Claude Code CLI not found.")
        console.print("  Install it from: [bold cyan]https://claude.ai/code[/bold cyan]")
        raise typer.Exit(1)

    # ── Load resume ───────────────────────────────────────────────────────────
    resume_path = _get_resume_path(resume)
    try:
        resume_text = extract_resume_text(resume_path)
        info(f"Loaded resume: {resume_path} ({len(resume_text)} chars)")
    except (FileNotFoundError, ValueError) as e:
        error(str(e))
        raise typer.Exit(1)

    # ── Job description ───────────────────────────────────────────────────────
    job_desc = job or ""

    # ── Run selected stage(s) ─────────────────────────────────────────────────
    analysis_result = {}

    if stage in (Stage.all, Stage.diagnose):
        if not job_desc and stage == Stage.all:
            job_desc = _get_job_description(job)
        elif not job_desc:
            job_desc = _get_job_description(job)

        run_diagnoser(resume_text, job_desc)

        if stage == Stage.all:
            if not ask_continue("Proceed to Stage 2 — Keyword Analyser?"):
                raise typer.Exit()

    if stage in (Stage.all, Stage.analyse):
        if not job_desc:
            job_desc = _get_job_description(job)

        analysis_result = run_analyser(resume_text, job_desc)

        if stage == Stage.all:
            if not ask_continue("Proceed to Stage 3 — Resume Rewriter?"):
                raise typer.Exit()

    if stage in (Stage.all, Stage.rewrite):
        if not job_desc:
            job_desc = _get_job_description(job)

        missing_kws = get_missing_keywords_string(analysis_result) if analysis_result else ""
        output_name = _next_output_name(output)
        run_rewriter(resume_text, job_desc, missing_kws, output_dir=output, output_name=output_name)

        if stage == Stage.all:
            if not ask_continue("Proceed to Stage 4 — Mock Interview with Hiring Manager?"):
                raise typer.Exit()

    if stage in (Stage.all, Stage.interview):
        if not job_desc:
            job_desc = _get_job_description(job)

        run_interview(resume_text, job_desc)

    console.print("\n[bold green]✅ Pipeline complete![/bold green]\n")


if __name__ == "__main__":
    app()
