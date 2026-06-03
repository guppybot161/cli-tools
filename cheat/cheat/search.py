"""BM25 ranking + highlight spans for cheatsheet entries.

Pure stdlib. Ported from cc-cheatsheet-v2.html (BM25 class, tok, hilite).
Operates on any list of Entry, so the app ranks each group independently —
matching the HTML viewer's proven per-column BM25 behavior.
"""
from __future__ import annotations

import math
import re

from .loader import Entry

# JS: /[\s\/\+\-\_\·\,\.]+/  — split on whitespace, / + - _ · , .
_SPLIT = re.compile(r"[\s/+\-_·,.]+")


def _tok(s: str) -> list[str]:
    return [t for t in _SPLIT.split(s.lower()) if len(t) > 1]


class _BM25:
    def __init__(self, entries: list[Entry], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b, self.entries = k1, b, entries
        n = len(entries)
        df: dict[str, int] = {}
        total = 0
        self.tf: list[tuple[dict[str, int], int]] = []
        for e in entries:
            toks = _tok(f"{e.cmd} {e.desc} {e.tags}")
            freq: dict[str, int] = {}
            for t in toks:
                freq[t] = freq.get(t, 0) + 1
            total += len(toks)
            for t in freq:
                df[t] = df.get(t, 0) + 1
            self.tf.append((freq, len(toks)))
        self.avgdl = total / n if n else 0.0
        self.idf = {
            t: math.log((n - c + 0.5) / (c + 0.5) + 1) for t, c in df.items()
        }

    def score(self, query: str) -> list[tuple[Entry, float]]:
        qt = _tok(query)
        scored: list[tuple[Entry, float]] = []
        for e, (freq, length) in zip(self.entries, self.tf):
            s = 0.0
            for q in qt:
                for t, f in freq.items():
                    if q not in t and t not in q:
                        continue
                    w = 1.0 if t == q else 0.65
                    idf = self.idf.get(t, 0.1)
                    denom = f + self.k1 * (1 - self.b + self.b * length / self.avgdl)
                    s += w * idf * (f * (self.k1 + 1)) / denom
            scored.append((e, s))
        return scored


def rank(entries: list[Entry], query: str) -> list[Entry]:
    """Empty query → entries in original order. Else BM25, zero-score dropped."""
    if not query.strip():
        return list(entries)
    scored = _BM25(entries).score(query)
    ranked = [(e, s) for e, s in scored if s > 0]
    ranked.sort(key=lambda es: es[1], reverse=True)
    return [e for e, _ in ranked]


def match_spans(text: str, query: str) -> list[tuple[int, int]]:
    """Char ranges in `text` to highlight (ports the HTML <mark> behavior)."""
    words = [w for w in query.strip().lower().split() if len(w) > 1]
    if not words:
        return []
    low = text.lower()
    spans: list[tuple[int, int]] = []
    for w in words:
        start = 0
        while True:
            i = low.find(w, start)
            if i == -1:
                break
            spans.append((i, i + len(w)))
            start = i + len(w)
    return _merge(spans)


def _merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        ls, le = merged[-1]
        if s <= le:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    return merged
