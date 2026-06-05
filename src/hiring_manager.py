"""Stage 4 — Hiring Manager: Mock interview with scoring and ATS assessment."""
import json
import anthropic
from .prompts import (
    INTERVIEW_SYSTEM,
    INTERVIEW_QUESTIONS_PROMPT,
    INTERVIEW_EVAL_PROMPT,
    FINAL_ASSESSMENT_PROMPT,
)
from .ui import (
    console, stage_header, section_title, divider,
    score_panel, spinner, success, info, prompt_input,
    ask_continue
)
from rich.panel import Panel
from rich.table import Table
from rich import box


def run_interview(resume_text: str, job_description: str = "General Tech Role") -> dict:
    """Run interactive mock interview. Returns final assessment dict."""
    stage_header("interview")

    client = anthropic.Anthropic()

    # Generate questions
    with spinner("Generating your 10 hardest interview questions..."):
        q_response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            system=INTERVIEW_SYSTEM,
            messages=[{
                "role": "user",
                "content": INTERVIEW_QUESTIONS_PROMPT.format(
                    resume_text=resume_text,
                    job_description=job_description
                )
            }]
        )

    raw = q_response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        q_data = json.loads(raw)
        questions = q_data.get("questions", [])
    except json.JSONDecodeError:
        console.print(f"[red]Failed to parse questions.[/red]\n{raw}")
        return {}

    if not questions:
        console.print("[red]No questions generated.[/red]")
        return {}

    # Welcome
    console.print(Panel(
        "[bold]Welcome to your Mock Technical Interview[/bold]\n\n"
        f"[dim]Role: {job_description}[/dim]\n\n"
        "Answer each question as thoroughly as you can.\n"
        "You'll be scored 1–10 per question with honest feedback.\n"
        "Type your answer and press Enter twice (empty line) to submit.",
        border_style="#4D96FF",
        padding=(1, 3),
    ))

    qa_log = []
    total_score = 0

    for i, q in enumerate(questions, 1):
        console.print()
        q_type = q.get("type", "Technical")
        difficulty = q.get("difficulty", "Hard")
        diff_color = {"Medium": "yellow", "Hard": "orange1", "Expert": "red"}.get(difficulty, "white")

        console.print(
            f"[bold cyan]Q{i}/{len(questions)}[/bold cyan]  "
            f"[dim][{q_type}  ·  [{diff_color}]{difficulty}[/{diff_color}]][/dim]\n"
        )
        console.print(Panel(
            q.get("question", ""),
            border_style="cyan",
            padding=(0, 2),
        ))

        # Collect multiline answer
        console.print("\n[dim]Your answer (press Enter twice to submit):[/dim]")
        lines = []
        while True:
            line = console.input("  ")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        answer = "\n".join(lines).strip()

        if not answer:
            answer = "[No answer provided]"

        # Evaluate answer
        with spinner("Evaluating your answer..."):
            eval_response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=800,
                system=INTERVIEW_SYSTEM,
                messages=[{
                    "role": "user",
                    "content": INTERVIEW_EVAL_PROMPT.format(
                        question=q.get("question", ""),
                        what_looking_for=q.get("what_im_looking_for", ""),
                        answer=answer
                    )
                }]
            )

        eval_raw = eval_response.content[0].text.strip()
        if eval_raw.startswith("```"):
            eval_raw = eval_raw.split("```")[1]
            if eval_raw.startswith("json"):
                eval_raw = eval_raw[4:]
        eval_raw = eval_raw.strip()

        try:
            evaluation = json.loads(eval_raw)
        except json.JSONDecodeError:
            evaluation = {"score": 5, "verdict": "Evaluated", "feedback": eval_raw}

        score = evaluation.get("score", 5)
        total_score += score
        verdict = evaluation.get("verdict", "")
        verdict_colors = {
            "Excellent": "green", "Good": "cyan",
            "Acceptable": "yellow", "Weak": "orange1", "Poor": "red"
        }
        vc = verdict_colors.get(verdict, "white")

        console.print()
        console.print(
            f"  Score: [{vc}][bold]{score}/10[/bold][/{vc}]  "
            f"[{vc}]{verdict}[/{vc}]"
        )
        console.print(f"\n  [bold]Feedback:[/bold] {evaluation.get('feedback', '')}")
        if evaluation.get("missing"):
            console.print(f"  [dim]Missing: {evaluation['missing']}[/dim]")
        if evaluation.get("model_answer_hint"):
            console.print(f"  [dim]💡 Strong answer would include: {evaluation['model_answer_hint']}[/dim]")

        qa_log.append({
            "question": q.get("question", ""),
            "type": q_type,
            "answer": answer,
            "score": score,
            "verdict": verdict,
            "feedback": evaluation.get("feedback", ""),
        })

        divider()

    # Final assessment
    avg_score = round(total_score / len(questions), 1)

    qa_summary = "\n".join([
        f"Q{i+1} [{qa['type']}]: {qa['question'][:80]}...\n"
        f"Score: {qa['score']}/10 — {qa['feedback']}"
        for i, qa in enumerate(qa_log)
    ])

    with spinner("Generating final hiring assessment..."):
        final_response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=INTERVIEW_SYSTEM,
            messages=[{
                "role": "user",
                "content": FINAL_ASSESSMENT_PROMPT.format(
                    resume_text=resume_text,
                    job_description=job_description,
                    qa_summary=qa_summary
                )
            }]
        )

    final_raw = final_response.content[0].text.strip()
    if final_raw.startswith("```"):
        final_raw = final_raw.split("```")[1]
        if final_raw.startswith("json"):
            final_raw = final_raw[4:]
    final_raw = final_raw.strip()

    try:
        final = json.loads(final_raw)
    except json.JSONDecodeError:
        final = {"interview_score": avg_score}

    _display_final(final, qa_log, avg_score)
    return final


def _display_final(final: dict, qa_log: list, avg_score: float):
    section_title("📊 Interview Results Summary")

    # Q-by-Q scores table
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
    table.add_column("Q#", width=4, justify="center")
    table.add_column("Type", width=14)
    table.add_column("Score", width=8, justify="center")
    table.add_column("Verdict", width=12)

    for i, qa in enumerate(qa_log, 1):
        score = qa["score"]
        verdict = qa.get("verdict", "")
        color = "green" if score >= 8 else ("yellow" if score >= 5 else "red")
        table.add_row(
            str(i), qa["type"],
            f"[{color}]{score}/10[/{color}]",
            f"[{color}]{verdict}[/{color}]"
        )
    console.print(table)

    console.print()

    # Scores
    ats = final.get("ats_score", 0)
    interview = final.get("interview_score", avg_score)
    ats_color = "green" if ats >= 75 else ("yellow" if ats >= 50 else "red")
    int_color = "green" if interview >= 7 else ("yellow" if interview >= 5 else "red")

    score_panel("Final ATS Score", int(ats), 100, ats_color)
    console.print()
    score_panel("Overall Interview Score", int(interview * 10), 100, int_color)

    # Hiring decision
    decision = final.get("hiring_decision", "")
    decision_colors = {
        "Hire": "green", "Strong Consider": "cyan",
        "Consider": "yellow", "Pass": "red"
    }
    dc = decision_colors.get(decision, "white")

    section_title("🏆 Hiring Manager's Decision")
    console.print(Panel(
        f"[bold {dc}]{decision}[/bold {dc}]\n\n"
        f"{final.get('hiring_rationale', '')}",
        border_style=dc,
        padding=(1, 2),
    ))

    readiness = final.get("overall_readiness", "")
    if readiness:
        console.print(f"\n  Readiness: [bold]{readiness}[/bold]")

    # Strengths / gaps
    strongest = final.get("strongest_area", "")
    biggest_gap = final.get("biggest_gap", "")
    if strongest:
        console.print(f"\n  [green]Strongest area:[/green] {strongest}")
    if biggest_gap:
        console.print(f"  [red]Biggest gap:[/red] {biggest_gap}")

    # Top 3 improvements
    improvements = final.get("top_3_improvements", [])
    if improvements:
        section_title("📌 Top 3 Improvements Before Applying")
        for i, imp in enumerate(improvements, 1):
            console.print(f"  [cyan]{i}.[/cyan] {imp}")

    divider()
    success("Interview complete. Good luck with your applications!")
