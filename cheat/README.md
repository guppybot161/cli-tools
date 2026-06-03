# cheat

A Textual terminal UI for live-filtered cheatsheets. Auto-discovers every
`*-commands.json` file in a data directory and renders them as tabs with BM25
search as you type.

```
 ▸ claude    winterm

Search: comp_

SLASH
  /compact        Compress context
  /compact-auto   Auto-compact on

KEYS
  Ctrl+L          Clear the screen

2 matches · tab sheet · / search · q quit
```

## Install

```bash
bash install.sh   # requires pipx
```

## Usage

```bash
cheat                          # uses the default data dir
cheat --dir ~/sheets           # override the data directory
CHEAT_DIR=~/sheets cheat       # same, via env var
```

Default data dir: `~/pyprojects/claude_hub/cheatsheets`

## Keys

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `Esc` | Clear search |
| `Tab` / `Shift+Tab` | Cycle sheets |
| `↑` / `↓` | Scroll results |
| `q` | Quit |

## Adding a cheatsheet

Drop a JSON file named `<name>-commands.json` into the data dir. It appears
as a new tab the next time `cheat` starts. No code changes needed.

Schema:

```json
{
  "group-name": [
    { "cmd": "/example",  "desc": "What it does", "tags": "search keywords" }
  ]
}
```

Each top-level key becomes a group with its own color. Known group names with
accent colors: `slash` (red), `keys` (blue), `reasoning` (purple). Unknown
groups fall back to blue.

## Dev

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests/
```
