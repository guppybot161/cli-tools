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
