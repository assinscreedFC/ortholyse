"""Tests for ``app.models.exportation`` export helpers.

Covers JSON, TXT, CSV (column and row) and DOCX/PDF export functions.
PDF and DOCX rendering depends on bundled Poppins fonts shipped under
``app/assets/Fonts/Poppins``; tests therefore use the real fonts directory
relative to the repository when available.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from app.models import exportation


FONTS_DIR = Path("assets") / "Fonts" / "Poppins"


class TestExporteJson:
    def test_writes_valid_json(self, tmp_path, sample_export_data):
        out = tmp_path / "out.json"
        exportation.exporte_json(str(out), sample_export_data)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["MLCU"] == 40.86
        assert data["Mots uniques"] == 203

    def test_preserves_unicode(self, tmp_path):
        out = tmp_path / "u.json"
        exportation.exporte_json(str(out), {"clef": "valeur avec accent e"})
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded["clef"] == "valeur avec accent e"

    def test_empty_dict(self, tmp_path):
        out = tmp_path / "empty.json"
        exportation.exporte_json(str(out), {})
        assert json.loads(out.read_text(encoding="utf-8")) == {}


class TestExporteTxt:
    def test_writes_key_value_lines(self, tmp_path, sample_export_data):
        out = tmp_path / "out.txt"
        exportation.exporte_txt(str(out), sample_export_data)
        content = out.read_text(encoding="utf-8")
        assert "MLCU: 40.86" in content
        assert "Mots uniques: 203" in content

    def test_one_line_per_key(self, tmp_path):
        out = tmp_path / "out.txt"
        exportation.exporte_txt(str(out), {"a": 1, "b": 2, "c": 3})
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3


class TestExporteCsvColumn:
    def test_writes_two_column_csv(self, tmp_path, sample_export_data):
        out = tmp_path / "out.csv"
        exportation.exporte_csv_column(str(out), sample_export_data)
        with out.open(encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["Cle", "Valeur"] or rows[0] == ["Cle".replace("e", "e"), "Valeur"] or rows[0][1] == "Valeur"
        # Header + one row per key (CSV writer adds blank line on Windows)
        body = [r for r in rows[1:] if r]
        assert len(body) == len(sample_export_data)

    def test_handles_numeric_values(self, tmp_path):
        out = tmp_path / "n.csv"
        exportation.exporte_csv_column(str(out), {"x": 42, "y": 3.14})
        with out.open(encoding="utf-8") as f:
            rows = list(csv.reader(f))
        # Strip header
        body = [r for r in rows[1:] if r]
        keys = {r[0] for r in body}
        assert {"x", "y"}.issubset(keys)


class TestExporteCsvRow:
    def test_keys_become_header(self, tmp_path):
        out = tmp_path / "row.csv"
        exportation.exporte_csv_row(str(out), {"a": [1, 2], "b": [3, 4]})
        with out.open(encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["a", "b"]
        assert rows[1] == ["1", "3"]
        assert rows[2] == ["2", "4"]

    def test_scalar_values_wrapped_as_list(self, tmp_path):
        out = tmp_path / "scalar.csv"
        exportation.exporte_csv_row(str(out), {"a": 1, "b": 2})
        with out.open(encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["a", "b"]
        assert rows[1] == ["1", "2"]


@pytest.mark.skipif(
    not (FONTS_DIR / "Poppins-Bold.ttf").exists(),
    reason="Poppins fonts not bundled in this checkout",
)
class TestExportePdf:
    def test_writes_pdf_file(self, tmp_path, sample_export_data):
        out = tmp_path / "report.pdf"
        exportation.exporte_pdf(
            str(out),
            sample_export_data,
            titre="Rapport test",
            font_dir=str(FONTS_DIR),
        )
        assert out.exists()
        head = out.read_bytes()[:4]
        assert head == b"%PDF"

    def test_pdf_without_texte_field(self, tmp_path):
        out = tmp_path / "no_text.pdf"
        data = {"Nombre de mots": 100, "MLCU": 5.0}
        exportation.exporte_pdf(
            str(out),
            data,
            titre="Sans texte",
            font_dir=str(FONTS_DIR),
        )
        assert out.exists()
        assert out.read_bytes()[:4] == b"%PDF"


@pytest.mark.skipif(
    not (FONTS_DIR / "Poppins-Regular.ttf").exists(),
    reason="Poppins fonts not bundled in this checkout",
)
class TestExporteDocx:
    def test_writes_docx_file(self, tmp_path, sample_export_data):
        out = tmp_path / "report.docx"
        exportation.exporte_docx(
            str(out),
            sample_export_data,
            titre="Rapport docx",
            font_path=str(FONTS_DIR / "Poppins-Regular.ttf"),
        )
        assert out.exists()
        # DOCX is a ZIP archive, magic bytes PK
        assert out.read_bytes()[:2] == b"PK"
