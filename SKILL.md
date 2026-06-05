---
name: resume-pipeline
description: >
  A 4-stage AI resume optimization pipeline for AI/ML/Robotics/SDE job seekers.
  Use this skill when the user wants to improve, diagnose, analyze, rewrite, or
  prepare interview questions for their resume. Triggers on any mention of:
  resume review, ATS scan, resume rewrite, job description tailoring, keyword
  gap analysis, mock interview prep, LaTeX resume, Google XYZ formula,
  or "tailor my resume". Runs as a CLI tool on Ubuntu via Claude Code.
  Stages: (1) Diagnoser → ATS scan, (2) Analyser → keyword gaps vs 1000 JDs,
  (3) Rewriter → XYZ formula + LaTeX output, (4) Hiring Manager → mock interview + score.
---

# Resume Pipeline Skill

## Overview

Four-stage pipeline for end-to-end resume optimization. Built as a Python CLI
with a `rich` terminal UI. Located at `~/resume-pipeline/`.

## Stages

### Stage 1 — Diagnoser
- Scans resume section-by-section like ATS software
- Flags weak bullets, passive voice, missing metrics, keyword density
- Outputs a flagged report with severity levels (🔴 Critical, 🟡 Warn, 🟢 OK)

### Stage 2 — Analyser
- Simulates analysis against 1000 job descriptions from AI/ML/Robotics/SDE fields
- Identifies top missing keywords and skills by role category
- Produces a prioritized keyword gap list with frequency scores

### Stage 3 — Rewriter
- Rewrites every bullet using Google's XYZ formula:
  "Accomplished [X] as measured by [Y], by doing [Z]"
- Outputs complete LaTeX code using Sanjay's custom template
- Tailors content to a specific job description if provided

### Stage 4 — Hiring Manager
- Asks the 10 hardest technical + behavioral questions based on resume content
- Accepts user answers and rates each out of 10
- Provides final ATS Score and overall interview readiness rating

## Usage

```bash
# Full pipeline
python resume_pipeline.py --resume path/to/resume.pdf --job "ML Engineer at DeepMind"

# Single stage
python resume_pipeline.py --resume resume.pdf --stage diagnose
python resume_pipeline.py --resume resume.pdf --stage analyse --role robotics
python resume_pipeline.py --resume resume.pdf --stage rewrite --job "SDE at Google"
python resume_pipeline.py --resume resume.pdf --stage interview

# Interactive mode (recommended)
python resume_pipeline.py
```

## File Structure

```
resume-pipeline/
├── resume_pipeline.py     # Main CLI entry point
├── src/
│   ├── diagnoser.py       # Stage 1
│   ├── analyser.py        # Stage 2
│   ├── rewriter.py        # Stage 3
│   ├── hiring_manager.py  # Stage 4
│   ├── pdf_reader.py      # PDF → text extraction
│   ├── ui.py              # Rich terminal UI helpers
│   └── prompts.py         # All LLM prompt templates
├── assets/
│   └── latex_template.tex # Base LaTeX resume template
└── skills/resume-pipeline/SKILL.md
```

## LaTeX Template

Uses Sanjay's established template with:
- Packages: geometry, titlesec, enumitem, hyperref, changepage, needspace
- Ruled section headers, ragged-right, two-column entry environments
- Sections: Education, Experience, Projects, Achievements, Skills, Certifications
