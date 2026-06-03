from pathlib import Path

import pytest

from cheat.app import CheatApp

FIXTURES = Path(__file__).parent / "fixtures" / "app"


@pytest.fixture
def app():
    return CheatApp(FIXTURES)


async def test_typing_a_query_filters_the_list(app):
    async with app.run_test() as pilot:
        assert app.match_count() == 3          # full claude sheet: 2 slash + 1 key
        await pilot.press("/")                 # focus search
        await pilot.press(*"compact")          # type the query
        assert app.match_count() == 1
        assert "/compact" in app._render_results().plain
        assert "/help" not in app._render_results().plain


async def test_tab_switches_the_active_sheet(app):
    async with app.run_test() as pilot:
        assert app.active_sheet.title == "claude"
        await pilot.press("tab")
        assert app.active_sheet.title == "winterm"
        await pilot.press("shift+tab")
        assert app.active_sheet.title == "claude"
