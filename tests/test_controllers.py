"""Tests for transcription helper functions in ``app.models.transcription``.

Note on the file name: the plan refers to ``test_controllers.py``, but the
PySide6 ``app.controllers`` package is excluded from coverage per D-07
(controllers are tightly coupled to Qt widgets and signals). Instead we
cover the pure functions that controllers delegate to:
``custom_tokenize``, ``extraire_mapping_depuis_segments`` and
``ajuster_mapping`` (all in ``app.models.transcription``).
"""
from __future__ import annotations

import pytest

from app.models.transcription import (
    ajuster_mapping,
    custom_tokenize,
    extraire_mapping_depuis_segments,
)


class TestCustomTokenize:
    def test_simple_split(self):
        assert custom_tokenize("hello world") == ["hello", "world"]

    def test_combines_apostrophe_tokens(self):
        # "m" + "'appeler" -> "m'appeler"
        result = custom_tokenize("je m 'appeler anis")
        assert "m'appeler" in result
        assert len(result) == 3

    def test_empty_string(self):
        assert custom_tokenize("") == []

    def test_no_apostrophe(self):
        assert custom_tokenize("un deux trois") == ["un", "deux", "trois"]

    def test_trailing_apostrophe_token(self):
        result = custom_tokenize("hello 'world")
        # The last apostrophe token combines with the previous one
        assert "hello'world" in result


class TestExtraireMappingDepuisSegments:
    def test_empty_segments(self):
        text, mapping = extraire_mapping_depuis_segments([])
        assert text == ""
        assert mapping == []

    def test_segment_without_word_timestamps(self):
        segs = [
            {"start": 0.0, "end": 2.0, "text": "bonjour le monde"},
        ]
        text, mapping = extraire_mapping_depuis_segments(segs)
        assert "bonjour" in text
        assert "monde" in text
        assert len(mapping) == 3  # three words

    def test_segment_with_word_timestamps(self):
        segs = [
            {
                "start": 0.0,
                "end": 1.0,
                "text": "hi there",
                "word_timestamps": [
                    {"start": 0.0, "end": 0.5, "word": "hi"},
                    {"start": 0.5, "end": 1.0, "word": "there"},
                ],
            }
        ]
        text, mapping = extraire_mapping_depuis_segments(segs)
        assert "hi" in text
        assert "there" in text
        assert len(mapping) == 2

    def test_apostrophe_tokens_are_combined(self):
        segs = [
            {
                "start": 0.0,
                "end": 1.0,
                "text": "m'appeler",
                "word_timestamps": [
                    {"start": 0.0, "end": 0.3, "word": "m"},
                    {"start": 0.3, "end": 1.0, "word": "'appeler"},
                ],
            }
        ]
        text, mapping = extraire_mapping_depuis_segments(segs)
        # combined token "m'appeler" produces a single mapping entry
        assert len(mapping) == 1
        assert "m'appeler" in text


class TestAjusterMapping:
    def test_unchanged_token_count(self):
        ancien = "bonjour le monde"
        nouveau = "bonsoir le monde"
        old_mapping = [
            (0.0, 1.0, 0, 7),
            (1.0, 1.5, 8, 10),
            (1.5, 2.5, 11, 16),
        ]
        new_mapping = ajuster_mapping(ancien, nouveau, old_mapping)
        assert len(new_mapping) == 3
        # Timestamps preserved
        assert new_mapping[0][0] == 0.0
        assert new_mapping[2][1] == 2.5

    def test_minor_changes_within_15_percent(self):
        ancien = "un deux trois quatre cinq six sept huit neuf dix"
        nouveau = "un deux trois quatre cinq six sept huit neuf dix onze"
        old_mapping = [(float(i), float(i + 1), i * 3, i * 3 + 2) for i in range(10)]
        new_mapping = ajuster_mapping(ancien, nouveau, old_mapping)
        assert len(new_mapping) == 11

    def test_major_change_distributes_uniformly(self):
        ancien = "un deux"
        nouveau = "un deux trois quatre cinq six sept huit neuf dix"
        old_mapping = [(0.0, 5.0, 0, 2), (5.0, 10.0, 3, 7)]
        new_mapping = ajuster_mapping(ancien, nouveau, old_mapping)
        assert len(new_mapping) == 10
        # First word starts at the original start time
        assert new_mapping[0][0] == 0.0
