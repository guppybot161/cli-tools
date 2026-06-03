from pathlib import Path

from cheat.loader import (
    DEFAULT_DATA_DIR,
    Entry,
    Sheet,
    discover,
    load_sheet,
    resolve_data_dir,
)

FIXTURES = Path(__file__).parent / "fixtures" / "loader"


def test_load_sheet_derives_title_and_labels():
    sheet = load_sheet(FIXTURES / "good-commands.json")
    assert sheet is not None
    assert sheet.title == "good"
    assert [g.key for g in sheet.groups] == ["slash", "keys"]
    assert [g.label for g in sheet.groups] == ["SLASH", "KEYS"]


def test_load_sheet_parses_entries_in_order():
    sheet = load_sheet(FIXTURES / "good-commands.json")
    slash = sheet.groups[0]
    assert slash.entries[0] == Entry(cmd="/help", desc="List commands", tags="show list")
    assert slash.entries[1].cmd == "/compact"
    assert sheet.entries == [e for g in sheet.groups for e in g.entries]
    assert len(sheet.entries) == 3


def test_load_sheet_returns_none_for_malformed_json():
    assert load_sheet(FIXTURES / "malformed-commands.json") is None


def test_load_sheet_returns_none_when_no_usable_groups():
    assert load_sheet(FIXTURES / "empty-commands.json") is None


def test_discover_skips_unusable_files():
    sheets = discover(FIXTURES)
    assert [s.title for s in sheets] == ["good"]


def test_resolve_data_dir_precedence():
    assert resolve_data_dir("/tmp/x") == Path("/tmp/x")
    assert resolve_data_dir(None, {"CHEAT_DIR": "/tmp/y"}) == Path("/tmp/y")
    assert resolve_data_dir(None, {}) == DEFAULT_DATA_DIR
