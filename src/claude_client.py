"""Thin wrapper around the Claude Code CLI for non-interactive use."""
import subprocess


def ask_claude(system: str, user: str) -> str:
    """Run a single prompt through the Claude Code CLI and return the text response."""
    result = subprocess.run(
        ["claude", "-p", f"{system}\n\n{user}"],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
