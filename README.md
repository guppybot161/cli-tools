# cli-tools

Small CLI utilities for WSL2 daily use.

## Tools

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `rec` | Minimal audio recorder using PulseAudio (WSL2/WSLg) | — |
| `mdview` | Markdown viewer | pipx (mdview) |
| `lt` | Local tunnel | — |
| `die_excel` | Convert .xlsx to .csv / .jsonl (records) | pandas, openpyxl |

## Install

Copy any tool to `~/.local/bin` and make it executable:

```bash
cp <tool> ~/.local/bin/
chmod +x ~/.local/bin/<tool>
```
