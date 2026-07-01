"""CLI for generating upstream patch notes from recent commits."""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import sys

from collect_commits import ensure_github_remote, fetch_remote, list_recent_commits
from summarize_commits import DEFAULT_MODEL, summarize_commits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize latest N commits on a remote branch into patch notes."
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to local git repo clone (default: current directory).",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="GitHub repository slug (owner/name). If set, remote URL is assumed as https://github.com/<owner>/<name>.git.",
    )
    parser.add_argument(
        "--remote",
        default="upstream",
        help="Git remote name to fetch/log from (default: upstream).",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Remote branch to summarize (default: main).",
    )
    parser.add_argument(
        "--n-commits",
        type=int,
        default=50,
        help="Number of recent commits to summarize (default: 50).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write report file; print only.",
    )
    return parser.parse_args()


def _repo_name(repo_path: Path) -> str:
    return repo_path.resolve().name


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _write_report(markdown: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = output_dir / f"patch_notes_{ts}.md"
    out_path.write_text(markdown, encoding="utf-8")
    return out_path


def main() -> int:
    args = parse_args()
    repo_path = Path(args.repo_path).resolve()
    if not (repo_path / ".git").exists():
        print(f"Error: not a git repository: {repo_path}", file=sys.stderr)
        return 2
    project_dir = Path(__file__).resolve().parent
    _load_env_file(project_dir / ".env")
    if repo_path != project_dir:
        _load_env_file(repo_path / ".env")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print(
            "Warning: no Gemini API key found (GEMINI_API_KEY or GOOGLE_API_KEY); using fallback summary.",
            file=sys.stdout,
        )

    try:
        source_ref = f"{args.remote}/{args.branch}"
        if args.repo:
            remote_url = ensure_github_remote(repo_path, args.remote, args.repo)
            source_ref = f"{remote_url}#{args.branch}"
        fetch_remote(repo_path, args.remote)
        commits = list_recent_commits(
            repo_path=repo_path,
            remote=args.remote,
            branch=args.branch,
            n_commits=args.n_commits,
        )
        result = summarize_commits(
            repo_name=_repo_name(repo_path),
            commits=commits,
            model=args.model,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not result.used_llm:
        if result.fallback_reason == "missing_google_genai_sdk":
            print(
                "Warning: Gemini SDK not installed in this Python environment. Install with: pip install google-genai",
                file=sys.stdout,
            )
        elif result.fallback_reason in {"empty_llm_response"}:
            print(
                "Warning: Gemini returned an empty response; fallback summary was used.",
                file=sys.stdout,
            )

    header = [
        f"# Patch Notes: {_repo_name(repo_path)}",
        "",
        f"- Source: `{source_ref}`",
        f"- Commit window: latest `{args.n_commits}` commits",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Summary mode: `{'Gemini' if result.used_llm else 'fallback'}`",
        "",
    ]
    final_markdown = "\n".join(header) + result.markdown

    out_path = None
    if not args.no_write:
        project_reports_dir = Path(__file__).resolve().parent / "reports"
        out_path = _write_report(final_markdown, project_reports_dir)

    print(final_markdown)
    if out_path:
        print(f"\nReport written to: {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
