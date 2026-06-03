from cheat.loader import Entry
from cheat.search import match_spans, rank

ENTRIES = [
    Entry(cmd="/help", desc="List commands", tags="show list"),
    Entry(cmd="/compact", desc="Compress context", tags="tokens summarise"),
    Entry(cmd="/clear", desc="Reset conversation history", tags="wipe reset"),
]


def test_empty_query_returns_original_order():
    assert rank(ENTRIES, "") == ENTRIES
    assert rank(ENTRIES, "   ") == ENTRIES


def test_query_filters_to_matching_entries():
    result = rank(ENTRIES, "compact")
    assert [e.cmd for e in result] == ["/compact"]


def test_query_ranks_best_match_first():
    # "reset" appears in both desc and tags of /clear, nowhere else.
    result = rank(ENTRIES, "reset")
    assert result[0].cmd == "/clear"


def test_match_spans_finds_case_insensitive_occurrence():
    assert match_spans("Compress context", "comp") == [(0, 4)]


def test_match_spans_ignores_short_and_missing_words():
    assert match_spans("Compress context", "a") == []
    assert match_spans("Compress context", "xyz") == []
    assert match_spans("", "comp") == []


def test_match_spans_merges_overlaps():
    # "comp" and "compr" overlap at index 0; expect a single merged span.
    assert match_spans("Compress", "comp compr") == [(0, 5)]
