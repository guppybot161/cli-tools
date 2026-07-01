# Minimal Scope (v0): Upstream Commit Patch Notes

## Goal
Produce a quick, high-level report of what changed recently in the upstream repository by summarizing the most recent `n` commits into a single patch note.

## Explicitly Out of Scope (v0)
- Fork comparison.
- File intersection/risk scoring.
- Merge recommendation ("Go/No-Go").
- Any write operations to git remotes.

## Inputs
- `repo_path`: local clone path.
- `remote`: default `upstream`.
- `branch`: default `main`.
- `n_commits`: number of recent commits to summarize (for example `20`, `50`, `100`).

## Output
A Markdown report with:
1. One-paragraph TL;DR.
2. 3-7 themed bullet points (grouped changes).
3. Notable commits list (hash + subject + author + date).
4. Optional "Watch next" bullets (areas with high commit activity).

## Implementation Approach

### Step 1: Collect Commit Data
Use plain `git` CLI from Python (`subprocess`) for reliability:
1. `git fetch <remote>`.
2. `git log <remote>/<branch> -n <n_commits> --date=short --pretty=format:'%H%x09%ad%x09%an%x09%s'`.

### Step 2: Build LLM Payload
Create a compact payload containing:
- repo name.
- selected range (`latest n commits`).
- structured commit list (hash/date/author/subject).

No diffs in v0. Commit messages only.

### Step 3: Summarize with Gemini
Prompt Gemini to generate patch notes from commit messages only.

System instruction:
> You are a technical release assistant. Summarize recent commits into concise patch notes. Do not invent details beyond the commit messages.

Required response format:
1. `TL;DR`
2. `Themes`
3. `Notable commits`
4. `Watch next`

### Step 4: Render Report
Write Markdown to:
- stdout (on-demand runs), and/or
- `reports/patch_notes_<YYYYMMDD_HHMM>.md` (cron runs).

## Proposed File Layout (v0)
1. `collect_commits.py` - fetch + log extraction.
2. `summarize_commits.py` - Gemini call + formatting rules.
3. `main.py` - CLI orchestration.

## Success Criteria
- Running `python main.py --n-commits 50` produces a readable Markdown patch note in under 30 seconds (excluding network/API latency).
- Output remains useful without code diffs.
- No write actions to git branches or remotes.

## Next Step After v0
Add optional diff metadata (diffstat per commit) before any fork-aware analysis.
