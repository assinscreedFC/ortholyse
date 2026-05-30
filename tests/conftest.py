"""Shared fixtures for the Ortholyse test suite.

Heavy ML wrappers (Whisper, spaCy, pyaudio) and PySide6 widgets are mocked so
the suite can run without GPU, audio devices, or a display server. Coverage
config in ``pyproject.toml`` further excludes these modules from the gate.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Ortholyse reads JSON assets relative to the current working directory
# (``./assets/JSON/*``). The assets live under ``app/assets/JSON``, so we
# chdir into ``app/`` before any source module is imported.
APP_DIR = ROOT / "app"
if APP_DIR.is_dir():
    os.chdir(APP_DIR)


def _install_module_mock(name: str, mock: MagicMock | None = None) -> MagicMock:
    """Insert a MagicMock into ``sys.modules`` under ``name``."""
    mod = mock if mock is not None else MagicMock(name=name)
    sys.modules[name] = mod
    return mod


# ---------------------------------------------------------------------------
# Heavy third-party stubs installed once at import time so collection works
# even when whisper/torch/pyaudio/PySide6 are not installed locally.
# In CI these are installed and the stubs are skipped (sys.modules already set
# after real import).
# ---------------------------------------------------------------------------
import importlib.util as _importlib_util


def _stub_if_missing(name: str) -> None:
    """Insert a MagicMock for ``name`` only when the real module is unavailable.

    This avoids breaking healthy installations (CI) where the real module
    must be used, while keeping local collection working when heavy ML
    dependencies are not installed.
    """
    if name in sys.modules:
        return
    try:
        if _importlib_util.find_spec(name) is None:
            _install_module_mock(name)
    except (ImportError, ValueError):
        _install_module_mock(name)


for mod_name in (
    "whisper",
    "torch",
    "pyaudio",
    "sounddevice",
    "pydub",
    "pydub.silence",
):
    _stub_if_missing(mod_name)

# pydub.AudioSegment.converter assignment must not blow up at import time
_pydub = sys.modules.get("pydub")
if isinstance(_pydub, MagicMock):
    _pydub.AudioSegment = MagicMock()

# spaCy ``fr_core_news_lg`` is ~500MB and not available in CI by default.
# We force a fake module that returns a tiny doc when ``nlp(text)`` is called.
# Tests requiring the real pipeline are excluded from the coverage gate.
_fake_spacy = MagicMock()
_fake_token = MagicMock()
_fake_token.text = "mot"
_fake_token.lemma_ = "mot"
_fake_token.prefix_ = ""
_fake_token.suffix_ = ""
_fake_token.pos_ = "NOUN"
_fake_token.morph = ""
_fake_nlp = MagicMock(return_value=[_fake_token])
_fake_nlp.pipe_names = []
_fake_spacy.load = MagicMock(return_value=_fake_nlp)
sys.modules["spacy"] = _fake_spacy


@pytest.fixture
def sample_text() -> str:
    """A short French paragraph for linguistic analysis tests."""
    return (
        "Lors d'une belle matinee, le soleil brillait. "
        "Marie marchait dans la foret. "
        "Elle decouvrit une cabane mysterieuse."
    )


@pytest.fixture
def tmp_export_dir(tmp_path) -> Path:
    """A clean temporary directory for export tests."""
    return tmp_path


@pytest.fixture
def sample_export_data() -> dict:
    """Representative payload used by exporte_json/txt/csv/pdf."""
    return {
        "Nombre de mots": 286,
        "Nombre d'enonces": 7,
        "MLCU": 40.86,
        "Mots uniques": 203,
        "texte": "Texte de transcription d'exemple.",
    }


@pytest.fixture
def mock_spacy(monkeypatch):
    """Replace ``spacy.load`` with a lightweight mock returning a fake nlp pipeline."""
    fake_token = MagicMock(text="mot", lemma_="mot", pos_="NOUN")
    fake_doc = MagicMock()
    fake_doc.__iter__ = lambda self: iter([fake_token])
    fake_nlp = MagicMock(return_value=fake_doc)
    fake_spacy = MagicMock(load=MagicMock(return_value=fake_nlp))
    monkeypatch.setitem(sys.modules, "spacy", fake_spacy)
    return fake_spacy
