#!/usr/bin/env python3
"""mdview — render a Markdown file and open it in Firefox."""

import base64
import mimetypes
import re
import sys
import tempfile
import subprocess
from pathlib import Path

from markdown_it import MarkdownIt


CONFIG_CSS = Path.home() / ".config" / "mdview" / "style.css"


def load_css() -> str:
    if CONFIG_CSS.exists():
        return CONFIG_CSS.read_text()
    return ""


def inline_images(html: str, base_dir: Path) -> str:
    """Replace relative <img src="..."> paths with base64 data URIs."""
    def replace(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        img_path = (base_dir / src).resolve()
        if not img_path.exists():
            return m.group(0)
        mime = mimetypes.guess_type(img_path)[0] or "image/png"
        data = base64.b64encode(img_path.read_bytes()).decode()
        return f'<img src="data:{mime};base64,{data}"'

    return re.sub(r'<img src="([^"]*)"', replace, html)


def render(md_path: Path) -> str:
    md = MarkdownIt("commonmark").enable("table")
    body = md.render(md_path.read_text(encoding="utf-8"))
    body = inline_images(body, md_path.parent)
    css = load_css()
    title = md_path.name
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    args = sys.argv[1:]
    pdf_mode = "--pdf" in args
    args = [a for a in args if a != "--pdf"]

    if len(args) != 1:
        print("Usage: mdview [--pdf] <file.md>", file=sys.stderr)
        sys.exit(1)

    md_path = Path(args[0]).resolve()
    if not md_path.exists():
        print(f"File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    html = render(md_path)

    if pdf_mode:
        try:
            from weasyprint import HTML
        except ImportError:
            print("PDF mode requires weasyprint: pipx inject mdview weasyprint", file=sys.stderr)
            sys.exit(1)
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", prefix="mdview_", dir="/tmp", delete=False
        ) as f:
            tmp_path = f.name
        HTML(string=html).write_pdf(tmp_path)
    else:
        with tempfile.NamedTemporaryFile(
            suffix=".html", prefix="mdview_", dir="/tmp", delete=False, mode="w", encoding="utf-8"
        ) as f:
            f.write(html)
            tmp_path = f.name

    win_path = subprocess.check_output(["wslpath", "-w", tmp_path]).decode().strip()
    subprocess.Popen(
        ["/mnt/c/Program Files/Mozilla Firefox/firefox.exe", "-new-window", win_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    main()
