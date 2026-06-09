"""Textual TUI: a live-filtered, auto-discovering cheatsheet viewer."""
from __future__ import annotations

import argparse
from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Input, Static

from .loader import Entry, Group, Sheet, discover, resolve_data_dir
from .search import match_spans, rank

# Group accent colors ported from the HTML viewer; unknown groups fall back.
GROUP_COLORS = {
    # claude sheet
    "slash": "#ff7b72",
    "keys": "#79c0ff",
    "reasoning": "#d2a8ff",
    # nvim sheet — six mutually distinct accents
    "custom": "#ffa657",
    "neotree": "#7ee787",
    "motions": "#56d4dd",
    "editing": "#e3b341",
    "windows": "#79c0ff",
    "search": "#ff9bce",
}
DEFAULT_COLOR = "#79c0ff"
DIM = "#6e7681"
HILITE = "#56d364"
CMD_WIDTH = 14


class CheatApp(App):
    CSS_PATH = "cheat.tcss"
    BINDINGS = [
        Binding("/", "focus_search", "search", show=False),
        Binding("escape", "clear_search", "clear", show=False),
        Binding("tab", "next_sheet", "sheet", priority=True),
        Binding("shift+tab", "prev_sheet", "prev", priority=True),
        Binding("down", "scroll_down", "down", show=False, priority=True),
        Binding("up", "scroll_up", "up", show=False, priority=True),
        Binding("q", "quit", "quit", show=False),
    ]

    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.sheets: list[Sheet] = []
        self.active = 0

    def compose(self) -> ComposeResult:
        yield Static(id="tabs")
        yield Input(placeholder="search commands…", id="search")
        yield VerticalScroll(Static(id="results"), id="results-scroll")
        yield Static(id="footer")

    def on_mount(self) -> None:
        self.sheets = discover(self.data_dir)
        self.set_focus(None)  # start unfocused so /, tab, q work immediately
        self.refresh_view()

    # ── state helpers (also used by tests) ──
    @property
    def active_sheet(self) -> Sheet | None:
        return self.sheets[self.active] if self.sheets else None

    @property
    def query_value(self) -> str:
        return self.query_one("#search", Input).value

    def filtered_groups(self) -> list[tuple[Group, list[Entry]]]:
        sheet = self.active_sheet
        if sheet is None:
            return []
        q = self.query_value
        return [(g, rank(g.entries, q)) for g in sheet.groups]

    def match_count(self) -> int:
        return sum(len(entries) for _, entries in self.filtered_groups())

    # ── events ──
    def on_input_changed(self, event: Input.Changed) -> None:
        self.refresh_view()

    # ── actions ──
    def action_focus_search(self) -> None:
        self.query_one("#search", Input).focus()

    def action_clear_search(self) -> None:
        inp = self.query_one("#search", Input)
        inp.value = ""
        inp.blur()

    def action_next_sheet(self) -> None:
        if self.sheets:
            self.active = (self.active + 1) % len(self.sheets)
            self.refresh_view()

    def action_prev_sheet(self) -> None:
        if self.sheets:
            self.active = (self.active - 1) % len(self.sheets)
            self.refresh_view()

    def action_scroll_down(self) -> None:
        self.query_one("#results-scroll", VerticalScroll).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one("#results-scroll", VerticalScroll).scroll_up()

    # ── rendering ──
    def refresh_view(self) -> None:
        self.query_one("#tabs", Static).update(self._render_tabs())
        self.query_one("#results", Static).update(self._render_results())
        self.query_one("#footer", Static).update(self._render_footer())

    def _render_tabs(self) -> Text:
        text = Text()
        for i, sheet in enumerate(self.sheets):
            if i == self.active:
                text.append(f" ▸ {sheet.title} ", style=f"bold {HILITE}")
            else:
                text.append(f"   {sheet.title} ", style=DIM)
        return text

    def _hl(self, raw: str, query: str, base_style: str, width: int = 0) -> Text:
        padded = raw.ljust(width) if width else raw
        text = Text(padded, style=base_style)
        for start, end in match_spans(raw, query):
            text.stylize(f"bold {HILITE}", start, end)
        return text

    def _render_results(self) -> Text:
        q = self.query_value
        text = Text()
        first = True
        for group, entries in self.filtered_groups():
            if not entries:
                continue
            if not first:
                text.append("\n")
            first = False
            color = GROUP_COLORS.get(group.key, DEFAULT_COLOR)
            text.append(f"{group.label}\n", style=f"bold {color}")
            for e in entries:
                text.append("  ")
                text.append_text(self._hl(e.cmd, q, color, width=CMD_WIDTH))
                text.append("  ")
                text.append_text(self._hl(e.desc, q, DIM))
                text.append("\n")
        if not text.plain:
            return Text("no matches", style=DIM)
        return text

    def _render_footer(self) -> Text:
        n = self.match_count()
        plural = "" if n == 1 else "es"
        return Text(
            f"{n} match{plural} · tab sheet · / search · q quit", style=DIM
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cheat", description="Live-filtered cheatsheet TUI"
    )
    parser.add_argument(
        "--dir", help="cheatsheet data directory (overrides $CHEAT_DIR)"
    )
    args = parser.parse_args()
    CheatApp(resolve_data_dir(args.dir)).run()


if __name__ == "__main__":
    main()
