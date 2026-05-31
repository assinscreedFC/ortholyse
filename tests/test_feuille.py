"""Tests for file operation helpers in ``app.models.operation_fichier``.

Note on the file name: the plan refers to ``test_feuille.py`` from the
original PySide6 ``Feuille`` widget, but that widget is a PySide6 view
(excluded from coverage per D-07 omit list). Coverage gate targets pure
business modules; here we cover ``operation_fichier`` which handles file
size, format detection and ffmpeg discovery.
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from app.models import operation_fichier


class TestReelFileFormat:
    def test_mp3_format(self):
        assert operation_fichier.reel_file_format("audio.mp3") == "mp3"

    def test_wav_format(self):
        assert operation_fichier.reel_file_format("recording.wav") == "wav"

    def test_mp4_format(self):
        assert operation_fichier.reel_file_format("video.mp4") == "mp4"

    def test_uppercase_extension(self):
        # Path suffix preserves case
        assert operation_fichier.reel_file_format("audio.MP3") == "MP3"

    def test_nested_path(self):
        p = os.path.join("dir1", "dir2", "file.flac")
        assert operation_fichier.reel_file_format(p) == "flac"

    def test_no_extension(self):
        assert operation_fichier.reel_file_format("noextension") == ""


class TestFileSizeMo:
    def test_small_file(self, tmp_path):
        f = tmp_path / "small.bin"
        f.write_bytes(b"x" * 1024)  # 1 KB
        size_mo = operation_fichier.file_size_Mo(str(f))
        assert size_mo == pytest.approx(1 / 1024, rel=1e-3)

    def test_one_mo_file(self, tmp_path):
        f = tmp_path / "one_mo.bin"
        f.write_bytes(b"x" * (1024 * 1024))
        size_mo = operation_fichier.file_size_Mo(str(f))
        assert size_mo == pytest.approx(1.0, rel=1e-3)

    def test_missing_file_raises(self):
        with pytest.raises(OSError):
            operation_fichier.file_size_Mo("/nonexistent/path/file.bin")


class TestFindFfmpeg:
    def test_returns_string_path(self):
        result = operation_fichier.find_ffmpeg()
        assert isinstance(result, str)
        assert "ffmpeg" in result.lower() or "_internal" in result

    def test_dev_mode_path_is_absolute(self):
        result = operation_fichier.find_ffmpeg()
        assert os.path.isabs(result)


class TestFileSizeMs:
    def test_uses_audiosegment(self, tmp_path):
        f = tmp_path / "audio.mp3"
        f.write_bytes(b"fake audio")
        fake_audio = MagicMock()
        fake_audio.__len__ = lambda self: 5000
        with patch.object(
            operation_fichier.AudioSegment, "from_file", return_value=fake_audio
        ):
            assert operation_fichier.file_size_ms(str(f)) == 5000

    def test_seconds_is_ms_divided_by_1000(self, tmp_path):
        f = tmp_path / "audio.wav"
        f.write_bytes(b"fake")
        fake_audio = MagicMock()
        fake_audio.__len__ = lambda self: 2500
        with patch.object(
            operation_fichier.AudioSegment, "from_file", return_value=fake_audio
        ):
            assert operation_fichier.file_size_sec(str(f)) == 2.5


class TestExtractAudioFmp4:
    def test_returns_output_filename(self, tmp_path):
        f = tmp_path / "video.mp4"
        f.write_bytes(b"fake mp4")
        fake_audio = MagicMock()
        with patch.object(
            operation_fichier.AudioSegment, "from_file", return_value=fake_audio
        ):
            result = operation_fichier.extract_audio_fmp4(str(f))
        # Output is now a unique tempfile path (SEC-F4 fix), not the legacy
        # shared "convertion.mp3" sitting in the CWD.
        assert result.endswith(".mp3")
        assert "ortholyse_convert_" in result
        import os
        assert os.path.exists(result)
        os.remove(result)
        fake_audio.export.assert_called_once()


class TestDetectSilence:
    def test_delegates_to_pydub(self):
        fake_audio = MagicMock()
        with patch.object(
            operation_fichier, "detect_silence", return_value=[(100, 200)]
        ) as mock_ds:
            result = operation_fichier.detect_silnce_inInterval(fake_audio)
        mock_ds.assert_called_once()
        assert result == [(100, 200)]
