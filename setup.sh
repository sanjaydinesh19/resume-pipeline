#!/bin/bash
# Resume Pipeline Setup Script
# Run once: bash setup.sh

set -e

echo "══════════════════════════════════════════════"
echo "  Resume Pipeline — Setup"
echo "══════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found. Install with: sudo apt install python3"
  exit 1
fi

echo "✔ Python found: $(python3 --version)"

# Install pip deps
echo ""
echo "Installing Python dependencies..."
pip install anthropic rich typer pymupdf --break-system-packages -q
echo "✔ Dependencies installed"

# Check for LaTeX (optional)
echo ""
if command -v pdflatex &>/dev/null; then
  echo "✔ pdflatex found — LaTeX compilation available"
else
  echo "⚠  pdflatex not found. To compile LaTeX output:"
  echo "   sudo apt install texlive-latex-recommended texlive-fonts-recommended"
fi

# API key check
echo ""
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠  ANTHROPIC_API_KEY not set."
  echo "   Add to your shell: export ANTHROPIC_API_KEY=your_key_here"
  echo "   Or add to ~/.bashrc for persistence."
else
  echo "✔ ANTHROPIC_API_KEY is set"
fi

echo ""
echo "══════════════════════════════════════════════"
echo "  Setup complete! Run the pipeline with:"
echo ""
echo "  python resume_pipeline.py"
echo "  python resume_pipeline.py --resume your_resume.pdf"
echo "  python resume_pipeline.py --resume your_resume.pdf --job 'ML at Google'"
echo "══════════════════════════════════════════════"
