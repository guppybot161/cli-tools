#!/usr/bin/env python3
"""mdview — render a Markdown file and open it in a browser."""

import argparse
import base64
import mimetypes
import re
import sys
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


MERMAID_SCRIPT = (
    '<script type="module">'
    'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";'
    'mermaid.initialize({startOnLoad:true});'
    "</script>"
)


def render_mermaid(html: str) -> str:
    """Convert <pre><code class="language-mermaid">...</code></pre> to <div class="mermaid">."""
    return re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        lambda m: f'<div class="mermaid">{m.group(1)}</div>',
        html,
        flags=re.DOTALL,
    )


def render(md_path: Path) -> str:
    md = MarkdownIt("commonmark").enable("table")
    body = md.render(md_path.read_text(encoding="utf-8"))
    body = inline_images(body, md_path.parent)
    body = render_mermaid(body)
    css = load_css()
    title = md_path.name
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
{MERMAID_SCRIPT}
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


def _is_wsl() -> bool:
    return Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists()


def open_in_browser(file_path: Path):
    if _is_wsl():
        win_path = subprocess.check_output(
            ["wslpath", "-w", str(file_path)]
        ).decode().strip()
        subprocess.Popen(
            ["explorer.exe", win_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        import webbrowser
        webbrowser.open(file_path.as_uri())


def main():
    parser = argparse.ArgumentParser(
        prog="mdview", description="Render a Markdown file to HTML/PDF and open it in a browser."
    )
    parser.add_argument("file", help="Markdown file to render")
    parser.add_argument("-o", "--output", help="Write output to this path instead of a temp file")
    parser.add_argument("--pdf", action="store_true", help="Render to PDF")
    parser.add_argument(
        "-b", "--browser", action=argparse.BooleanOptionalAction, default=True,
        help="Open the result in the default browser (default: on)",
    )
    args = parser.parse_args()

    md_path = Path(args.file).resolve()
    if not md_path.exists():
        print(f"File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output).resolve() if args.output else None
    pdf_mode = args.pdf or (out_path is not None and out_path.suffix.lower() == ".pdf")
    ext = ".pdf" if pdf_mode else ".html"

    if out_path is None:
        out_path = Path("/tmp") / f"mdview_{md_path.stem}{ext}"

    html = render(md_path)

    if pdf_mode:
        try:
            from weasyprint import HTML
        except ImportError:
            print("PDF mode requires weasyprint: pipx inject mdview weasyprint", file=sys.stderr)
            sys.exit(1)
        HTML(string=html).write_pdf(str(out_path))
    else:
        out_path.write_text(html, encoding="utf-8")

    if args.browser:
        open_in_browser(out_path)


if __name__ == "__main__":
    main()
