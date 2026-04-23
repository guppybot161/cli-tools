# cli-tools

Small CLI utilities for WSL2 daily use.

## Tools

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `rec` | Minimal audio recorder using PulseAudio (WSL2/WSLg) | — |
| `mdview` | Markdown viewer | pipx (mdview) |
| `lt` | List files modified in the last N days | — |
| `die_excel` | Convert .xlsx to .csv / .jsonl (records) | pandas, openpyxl |
| `iview` | Open images in IrfanView from WSL2 | IrfanView (Windows) |

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
mdview notes.md            # open as HTML in Firefox
mdview notes.md --pdf      # convert to PDF and open
```

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

### iview

Open images in IrfanView from WSL2. Requires IrfanView installed at the default Windows path.

```bash
iview photo.jpg
iview *.png
```
