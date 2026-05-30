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

# Ortholyse reads JSON assets relative to the current working directory.
# Pin it to the repo root so tests run from any location.
os.chdir(ROOT)


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
for mod_name in (
    "whisper",
    "torch",
    "pyaudio",
    "sounddevice",
    "pydub",
    "pydub.silence",
):
    if mod_name not in sys.modules:
        _install_module_mock(mod_name)

# pydub.AudioSegment.converter assignment must not blow up at import time
if hasattr(sys.modules.get("pydub"), "AudioSegment"):
    sys.modules["pydub"].AudioSegment = MagicMock()


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
