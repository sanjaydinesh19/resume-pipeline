"""Stage 3 — Resume Rewriter: Google XYZ formula + LaTeX output."""
import json
from pathlib import Path
import anthropic
from .prompts import REWRITER_SYSTEM, REWRITER_USER
from .ui import (
    console, stage_header, section_title, divider,
    spinner, success, info, warn
)
from rich.syntax import Syntax
from rich.panel import Panel


def run_rewriter(
    resume_text: str,
    job_description: str,
    missing_keywords: str = "",
    output_dir: str = "."
) -> dict:
    """Rewrite resume with XYZ formula. Saves LaTeX file. Returns result dict."""
    stage_header("rewrite")

    client = anthropic.Anthropic()

    with spinner("Rewriting resume with Google XYZ formula + LaTeX..."):
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8192,
            system=REWRITER_SYSTEM,
            messages=[{
                "role": "user",
                "content": REWRITER_USER.format(
                    resume_text=resume_text,
                    job_description=job_description,
                    missing_keywords=missing_keywords or "None provided"
                )
            }]
        )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"[red]Failed to parse Rewriter response.[/red]")
        # Try to salvage LaTeX if JSON failed
        _save_raw_latex(raw, output_dir)
        return {}

    _display_rewrite(result, output_dir)
    return result


def _display_rewrite(result: dict, output_dir: str):
    # Bullet rewrites
    bullets = result.get("rewritten_bullets", [])
    if bullets:
        section_title("✍️  Rewritten Bullets (Google XYZ Formula)")
        for b in bullets[:5]:  # Show first 5 to avoid flooding terminal
            console.print(f"\n  [dim]Original:[/dim]  {b.get('original', '')}")
            console.print(f"  [green]Rewritten:[/green] {b.get('rewritten', '')}")
            breakdown = b.get("formula_breakdown", {})
            if breakdown:
                console.print(
                    f"  [dim]  X={breakdown.get('X','')} "
                    f"| Y={breakdown.get('Y','')} "
                    f"| Z={breakdown.get('Z','')}[/dim]"
                )
        if len(bullets) > 5:
            info(f"  ... and {len(bullets)-5} more bullets rewritten (see LaTeX file)")

    # Tailoring changes
    changes = result.get("tailoring_changes", [])
    if changes:
        section_title("🎯 Tailoring Changes for This JD")
        for c in changes:
            console.print(f"  [cyan]•[/cyan] {c}")

    # Keywords inserted
    kws = result.get("keywords_inserted", [])
    if kws:
        section_title("🔑 Keywords Inserted")
        console.print("  " + ", ".join(f"[green]{k}[/green]" for k in kws))

    # Save LaTeX
    latex_code = result.get("latex_code", "")
    if latex_code:
        output_path = _save_latex(latex_code, output_dir)
        console.print()
        console.print(Panel(
            f"[bold green]LaTeX resume saved to:[/bold green]\n[cyan]{output_path}[/cyan]\n\n"
            f"[dim]Compile with: pdflatex {Path(output_path).name}[/dim]",
            border_style="green",
            padding=(1, 2),
        ))

        # Show first 30 lines of LaTeX as preview
        section_title("📄 LaTeX Preview (first 30 lines)")
        preview = "\n".join(latex_code.split("\n")[:30])
        console.print(Syntax(preview, "latex", theme="monokai", line_numbers=True))
    else:
        warn("No LaTeX code generated. Check the output above.")

    divider()
    success("Rewrite complete. LaTeX file ready to compile.")


def _save_latex(latex_code: str, output_dir: str) -> str:
    out = Path(output_dir) / "resume_rewritten.tex"
    out.write_text(latex_code, encoding="utf-8")
    return str(out)


def _save_raw_latex(raw: str, output_dir: str):
    """Fallback: save raw response in case JSON parse failed."""
    out = Path(output_dir) / "resume_raw_output.txt"
    out.write_text(raw, encoding="utf-8")
    warn(f"Raw output saved to: {out}")
