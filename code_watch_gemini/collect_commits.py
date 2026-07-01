"""Collect recent commits from a git remote branch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class Commit:
    sha: str
    date: str
    author: str
    subject: str

    @property
    def short_sha(self) -> str:
        return self.sha[:8]


def _run_git(repo_path: Path, *args: str) -> str:
    cmd = ["git", *args]
    proc = subprocess.run(
        cmd,
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Git command failed: {' '.join(cmd)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc.stdout


def fetch_remote(repo_path: Path, remote: str) -> None:
    _run_git(repo_path, "fetch", remote)


def ensure_github_remote(repo_path: Path, remote: str, repo_slug: str) -> str:
    repo_slug = repo_slug.strip().strip("/")
    if "/" not in repo_slug:
        raise ValueError("repo_slug must be in the form 'owner/repo'")
    desired_url = f"https://github.com/{repo_slug}.git"

    try:
        existing_url = _run_git(repo_path, "remote", "get-url", remote).strip()
        # Keep existing remotes read-only; avoid mutating git config in automation.
        if existing_url:
            return existing_url
        return desired_url
    except RuntimeError:
        _run_git(repo_path, "remote", "add", remote, desired_url)
        return desired_url

    return desired_url


def list_recent_commits(
    repo_path: Path,
    remote: str,
    branch: str,
    n_commits: int,
) -> list[Commit]:
    if n_commits <= 0:
        raise ValueError("n_commits must be > 0")

    pretty = "%H%x09%ad%x09%an%x09%s"
    output = _run_git(
        repo_path,
        "log",
        f"{remote}/{branch}",
        "-n",
        str(n_commits),
        "--date=short",
        f"--pretty=format:{pretty}",
    ).strip()

    if not output:
        return []

    commits: list[Commit] = []
    for line in output.splitlines():
        parts = line.split("\t", 3)
        if len(parts) != 4:
            # Skip malformed lines instead of failing the whole report.
            continue
        sha, date, author, subject = parts
        commits.append(Commit(sha=sha, date=date, author=author, subject=subject))
    return commits
