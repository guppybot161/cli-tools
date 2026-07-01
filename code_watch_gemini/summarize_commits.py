"""Summarize commit messages into patch notes."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Iterable

from collect_commits import Commit


DEFAULT_MODEL = "gemini-2.5-pro"


@dataclass(frozen=True)
class SummaryResult:
    markdown: str
    used_llm: bool
    fallback_reason: str | None = None


def _commit_payload(commits: Iterable[Commit]) -> str:
    rows = [
        {
            "sha": c.sha,
            "date": c.date,
            "author": c.author,
            "subject": c.subject,
        }
        for c in commits
    ]
    return json.dumps(rows, ensure_ascii=True, indent=2)


def _prompt(repo_name: str, commits: list[Commit]) -> str:
    return (
        "Create patch notes from commit messages only.\n"
        "Do not invent details not present in the commit list.\n"
        "Output Markdown with exactly these sections:\n"
        "## TL;DR\n"
        "## Themes\n"
        "## Notable commits\n"
        "## Watch next\n\n"
        f"Repository: {repo_name}\n"
        f"Commit count: {len(commits)}\n"
        "Commit list (JSON):\n"
        f"{_commit_payload(commits)}\n"
    )


def _fallback_summary(commits: list[Commit]) -> str:
    top = commits[:10]
    lines = [
        "## TL;DR",
        f"Latest {len(commits)} commits collected. LLM summary unavailable; showing raw highlights.",
        "",
        "## Themes",
        "- Commit-message-only mode enabled.",
        "- Use GEMINI_API_KEY and google-genai to enable thematic summarization.",
        "",
        "## Notable commits",
    ]
    for c in top:
        lines.append(f"- `{c.short_sha}` ({c.date}) {c.author}: {c.subject}")
    lines.extend(
        [
            "",
            "## Watch next",
            "- Repeated edits in the same subsystem across multiple commits.",
            "- Large refactors hidden behind generic commit messages.",
        ]
    )
    return "\n".join(lines)


def summarize_commits(
    repo_name: str,
    commits: list[Commit],
    model: str = DEFAULT_MODEL,
) -> SummaryResult:
    if not commits:
        return SummaryResult(
            markdown=(
                "## TL;DR\nNo commits found for the requested range.\n\n"
                "## Themes\n- No data.\n\n"
                "## Notable commits\n- None.\n\n"
                "## Watch next\n- Verify remote/branch settings."
            ),
            used_llm=False,
            fallback_reason="no_commits",
        )

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return SummaryResult(
            markdown=_fallback_summary(commits),
            used_llm=False,
            fallback_reason="missing_api_key",
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return SummaryResult(
            markdown=_fallback_summary(commits),
            used_llm=False,
            fallback_reason="missing_google_genai_sdk",
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            temperature=0.2,
            system_instruction=(
                "You are a technical release assistant. Summarize recent commits into "
                "concise patch notes. Do not invent details beyond the commit messages."
            ),
        ),
        contents=_prompt(repo_name, commits),
    )

    text = (response.text or "").strip()
    if not text:
        text = _fallback_summary(commits)
        return SummaryResult(markdown=text, used_llm=False, fallback_reason="empty_llm_response")
    return SummaryResult(markdown=text, used_llm=True, fallback_reason=None)
