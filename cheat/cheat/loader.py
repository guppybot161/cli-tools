"""Discover and parse *-commands.toml cheatsheets into a typed model.

Pure stdlib. No Textual dependency — unit-testable without a terminal.
"""
from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_DIR = Path.home() / "pyprojects" / "claude_hub" / "cheatsheets"


@dataclass(frozen=True)
class Entry:
    cmd: str
    desc: str
    tags: str


@dataclass
class Group:
    key: str            # raw TOML table key, e.g. "slash"
    label: str          # display label, e.g. "SLASH"
    entries: list[Entry]


@dataclass
class Sheet:
    title: str          # e.g. "claude"
    groups: list[Group]

    @property
    def entries(self) -> list[Entry]:
        return [e for g in self.groups for e in g.entries]


def resolve_data_dir(cli_dir: str | None = None, env: Mapping[str, str] | None = None) -> Path:
    """Resolve the cheatsheet data dir: --dir > $CHEAT_DIR > DEFAULT_DATA_DIR."""
    env = os.environ if env is None else env
    if cli_dir:
        return Path(cli_dir).expanduser()
    env_dir = env.get("CHEAT_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    return DEFAULT_DATA_DIR


def _title_from_filename(path: Path) -> str:
    stem = path.stem  # "claude-commands"
    suffix = "-commands"
    if stem.endswith(suffix):
        stem = stem[: -len(suffix)]
    return stem


def _parse_entry(raw: dict) -> Entry | None:
    cmd = raw.get("cmd")
    if not isinstance(cmd, str):
        return None
    return Entry(cmd=cmd, desc=str(raw.get("desc", "")), tags=str(raw.get("tags", "")))


def load_sheet(path: Path) -> Sheet | None:
    """Parse one TOML file into a Sheet, or None if malformed / empty."""
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    groups: list[Group] = []
    for key, raw_entries in data.items():
        if not isinstance(raw_entries, list):
            continue
        entries = [
            e
            for e in (_parse_entry(r) for r in raw_entries if isinstance(r, dict))
            if e is not None
        ]
        if entries:
            groups.append(Group(key=key, label=key.upper(), entries=entries))
    if not groups:
        return None
    return Sheet(title=_title_from_filename(path), groups=groups)


def discover(data_dir: Path) -> list[Sheet]:
    """Load every *-commands.toml in data_dir, skipping unusable files."""
    sheets: list[Sheet] = []
    for path in sorted(Path(data_dir).glob("*-commands.toml")):
        sheet = load_sheet(path)
        if sheet is not None:
            sheets.append(sheet)
    return sheets
