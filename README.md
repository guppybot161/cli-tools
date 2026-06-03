# cli-tools

Small CLI utilities for WSL2 daily use.

## Tools

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `rec` | Minimal audio recorder using PulseAudio (WSL2/WSLg) | — |
| `mdview` | Markdown viewer | pipx (mdview) |
| `lt` | List files modified in the last N days | — |
| `die_excel` | Convert .xlsx to .csv / .jsonl (records) | pandas, openpyxl |
| `die_word` | Convert .docx to .md (Markdown) | pandoc |
| `iview` | Open images in IrfanView from WSL2 | IrfanView (Windows) |
| `npp` | Open files in Notepad++ from WSL2 | Notepad++ (Windows) |
| `yt2md` | Fetch YouTube transcript as Markdown | yt-dlp, youtube-transcript-api |
| `cheat` | Live-filtered cheatsheet TUI (Textual) | pipx (cheat) |

## Install

Copy any tool to `~/.local/bin` and make it executable:

```bash
cp <tool> ~/.local/bin/
chmod +x ~/.local/bin/<tool>
```

Ensure `~/.local/bin` is on your PATH (add to `~/.bashrc` if not already there):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### mdview

`mdview` has its own installer that sets up pipx and the stylesheet:

```bash
bash mdview/install.sh
```

## Usage

### rec

Record audio via PulseAudio (WSL2/WSLg). Saves to `~/recordings/` by default.

```bash
rec                        # record until Ctrl+C
rec -d 10                  # record for 10 seconds
rec -o meeting.wav         # specify output file
rec --list-devices         # show available PulseAudio sources
rec --device alsa_input.0  # use a specific device
```

### mdview

Render a Markdown file and open it in Firefox. Inlines local images as base64.

```bash
mdview notes.md                   # open as HTML in Firefox
mdview notes.md --pdf             # convert to PDF and open
mdview notes.md -o out.html       # write to a file (then open)
mdview notes.md -o out.pdf        # .pdf output implies PDF mode
mdview notes.md -o out.html --no-browser   # write only, don't open
```

Options:

- `-o, --output PATH` — write the rendered file to `PATH` instead of a temp file. A `.pdf` extension implies PDF mode.
- `--pdf` — render to PDF.
- `-b, --browser` / `--no-browser` — open the result in Firefox (default: on).

Without `-o`, output goes to `/tmp/mdview_<name>.{html,pdf}` (named after the source document).

Custom styles can be placed in `~/.config/mdview/style.css`.

### lt

List files modified within the last N days (default: 1).

```bash
lt                         # files modified today in current directory
lt ~/projects              # files modified today in ~/projects
lt . -t 7                  # files modified in the last 7 days
```

### die_excel

Convert `.xlsx` files to `.csv` and/or `.jsonl`.

```bash
die_excel report.xlsx                        # convert to CSV (default)
die_excel report.xlsx -f jsonl               # convert to JSONL
die_excel report.xlsx -f both                # convert to both formats
die_excel report.xlsx -o /tmp/out/           # write to a specific directory
die_excel report.xlsx --list-sheets          # list sheet names and exit
die_excel report.xlsx -s "Sheet1" -f jsonl   # convert a single sheet
die_excel ./data/                            # convert all .xlsx in a directory
```

### die_word

Convert `.docx` files to Markdown via `pandoc`.

```bash
die_word notes.docx                    # writes notes.md alongside the input
die_word notes.docx -o /tmp/out/       # write to a specific directory
die_word ./meetings/                   # convert all .docx in a directory
die_word notes.docx --media-dir media/ # extract embedded images
die_word notes.docx --stdout           # print Markdown to stdout
```

### iview

Open images in IrfanView from WSL2. Requires IrfanView installed at the default Windows path.

```bash
iview photo.jpg
iview *.png
```

### npp

Open files in Notepad++ from WSL2. Translates WSL paths to Windows paths
automatically. Existing arguments that aren't files (e.g. Notepad++ flags
like `-multiInst`) are passed through unchanged.

```bash
npp                        # launch with no file
npp notes.md               # open one file
npp file1 file2            # open multiple files
npp -multiInst notes.md    # pass Notepad++ flags through
```

### yt2md

Fetch a YouTube transcript and write it as Markdown.

```bash
yt2md https://youtu.be/VIDEO_ID
yt2md VIDEO_ID --type interview
yt2md https://www.youtube.com/watch?v=VIDEO_ID --lang de --out notes.md
yt2md VIDEO_ID --chunk 60 --no-meta
```

### cheat

A Textual terminal UI that auto-discovers `*-commands.json` cheatsheets and
live-filters them with BM25 search. Drop a new JSON file in the data dir and a
new tab appears — no code changes.

```bash
cheat                          # uses the default data dir
cheat --dir ~/sheets           # override the data directory
CHEAT_DIR=~/sheets cheat       # same, via env var
```

Inside the TUI: `/` focuses search, `Esc` clears it, `Tab` / `Shift+Tab`
switch sheets, `↑` / `↓` scroll, `q` quits.

Install with `bash cheat/install.sh` (requires pipx).
