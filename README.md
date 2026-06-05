# Resume Pipeline 🚀

**AI-Powered 4-Stage Resume Optimization System**
Built for AI / ML / Robotics / SDE job seekers. Runs entirely in your Ubuntu terminal.

---

## Stages

| # | Stage | What it does |
|---|-------|-------------|
| 1 | 🔍 **Diagnoser** | ATS scan — flags weak sections, passive voice, missing metrics |
| 2 | 📊 **Analyser** | Keyword gap analysis vs 1000+ JDs in your field |
| 3 | ✍️ **Rewriter** | Rewrites bullets with Google XYZ formula + outputs LaTeX |
| 4 | 🎯 **Hiring Manager** | Mock interview — 10 hard questions, per-answer scores, ATS rating |

---

## Quick Start

```bash
# 1. Setup (run once)
bash setup.sh
export ANTHROPIC_API_KEY=your_key_here

# 2. Full pipeline (interactive)
python resume_pipeline.py

# 3. Full pipeline with arguments
python resume_pipeline.py --resume resume.pdf --job "ML Engineer at DeepMind"

# 4. Single stage
python resume_pipeline.py --resume resume.pdf --stage diagnose
python resume_pipeline.py --resume resume.pdf --stage analyse
python resume_pipeline.py --resume resume.pdf --stage rewrite --job "SDE at Google"
python resume_pipeline.py --resume resume.pdf --stage interview
```

---

## Commands

```
Options:
  --resume  -r    Path to resume (.pdf, .tex, .txt)
  --job     -j    Job title or full JD paste
  --stage   -s    Stage: all | diagnose | analyse | rewrite | interview
  --output  -o    Output directory for LaTeX file (default: current dir)
```

---

## Output

- **Stage 3** saves `resume_rewritten.tex` in your output directory
- Compile with: `pdflatex resume_rewritten.tex`
- LaTeX template follows your established style (geometry, titlesec, enumitem, hyperref)

---

## File Structure

```
resume-pipeline/
├── resume_pipeline.py       ← Main entry point
├── setup.sh                 ← One-time setup
├── requirements.txt
├── assets/
│   └── latex_template.tex   ← Base LaTeX template
├── src/
│   ├── diagnoser.py         ← Stage 1
│   ├── analyser.py          ← Stage 2
│   ├── rewriter.py          ← Stage 3
│   ├── hiring_manager.py    ← Stage 4
│   ├── pdf_reader.py        ← PDF extraction
│   ├── ui.py                ← Rich terminal UI
│   └── prompts.py           ← All LLM prompts
└── skills/resume-pipeline/
    └── SKILL.md             ← Claude Skill definition
```

---

## Supported Resume Formats

- `.pdf` — Standard resume PDF
- `.tex` — Existing LaTeX source
- `.txt` / `.md` — Plain text

---

## LaTeX Template

The rewriter uses your established template style:
- **Packages:** `geometry`, `titlesec`, `enumitem`, `hyperref`, `changepage`, `needspace`
- **Style:** Ruled section headers, ragged-right, two-column entry environments
- **Sections:** Education · Experience · Projects · Achievements · Technical Skills · Certifications
