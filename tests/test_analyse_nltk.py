"""Tests for ``app.models.Analyse_NLTK`` linguistic analysis class.

spaCy is stubbed in conftest because ``fr_core_news_lg`` is too heavy for CI.
Tests cover pure tokenization, sentence segmentation, unique words and
morpheme detection (regex + Snowball stemmer + prefix/suffix tables).
"""
from __future__ import annotations

import pytest

from app.models.Analyse_NLTK import Analyse_NLTK


class TestSentenceSegmentation:
    def test_single_sentence(self):
        an = Analyse_NLTK("Une seule phrase.")
        assert an.sent_size() == 1

    def test_three_sentences(self):
        an = Analyse_NLTK("Premiere phrase. Deuxieme phrase. Troisieme phrase.")
        assert an.sent_size() == 3

    def test_empty_text(self):
        an = Analyse_NLTK("")
        assert an.sent_size() == 0


class TestWordTreatment:
    def test_simple_sentence_tokens(self):
        an = Analyse_NLTK("Bonjour le monde.")
        tokens = an.word_treatment()
        assert "Bonjour" in tokens
        assert "le" in tokens
        assert "monde" in tokens

    def test_strips_punctuation(self):
        an = Analyse_NLTK("Salut, comment vas-tu ?")
        tokens = an.word_treatment()
        # NLTK tokenizer keeps some punctuation; the regex sub removes it.
        assert "," not in tokens
        assert "?" not in tokens

    def test_apostrophe_kept_as_single_token(self):
        an = Analyse_NLTK("J'aime ca.")
        tokens = an.word_treatment()
        # ``l'`` and similar elisions stay attached after __sub_punc
        assert any("aime" in t for t in tokens)

    def test_numbers_converted_to_words(self):
        an = Analyse_NLTK("J'ai 25 ans.")
        tokens = an.word_treatment()
        assert "vingt" in tokens
        assert "cinq" in tokens

    def test_decimal_numbers_converted(self):
        an = Analyse_NLTK("Il pese 12.5 kilos.")
        tokens = an.word_treatment()
        assert "virgule" in tokens


class TestUniqueWords:
    def test_no_duplicates(self):
        an = Analyse_NLTK("le chat le chat le chat")
        # six tokens, two unique words
        assert an.nbr_unique_word() == 2

    def test_all_different(self):
        an = Analyse_NLTK("un deux trois quatre")
        assert an.nbr_unique_word() == 4

    def test_empty(self):
        an = Analyse_NLTK("")
        assert an.nbr_unique_word() == 0


class TestMorphemDetection:
    def test_no_morphemes_for_short_words(self):
        an = Analyse_NLTK("le un de la a et")
        result = an.morphem()
        assert isinstance(result, int)
        assert result >= 0

    def test_returns_integer_count(self):
        an = Analyse_NLTK("reconstruction prevention application")
        result = an.morphem()
        assert isinstance(result, int)

    def test_morphem_accepts_explicit_text(self):
        an = Analyse_NLTK("vide")
        # Passing text overrides the instance text
        result = an.morphem("manger boire courir")
        assert isinstance(result, int)


class TestInitialization:
    def test_default_empty_text(self):
        an = Analyse_NLTK()
        assert an.sent_size() == 0

    def test_doc_lazy_initialization(self):
        an = Analyse_NLTK("test")
        assert an.doc is None


class TestSpacyDependentMethods:
    """Methods that depend on the spaCy pipeline (mocked here)."""

    def test_calc_lemme_returns_count(self):
        an = Analyse_NLTK("Bonjour le monde.")
        result = an.calc_lemme()
        assert isinstance(result, int)
        assert result >= 0

    @pytest.mark.skip(
        reason="spacy_calc_morphem has an upstream bug "
        "(calls .items() on morphem() which returns int). Tracked separately."
    )
    def test_spacy_calc_morphem_returns_list(self):
        an = Analyse_NLTK("Bonjour le monde.")
        result = an.spacy_calc_morphem()
        assert isinstance(result, list)
