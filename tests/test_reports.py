"""Testes do contrato CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.models import PlanItem
from organizer.reports import CSV_FIELDS, write_csv_report


class ReportTests(TestCase):
    def test_csv_has_expected_columns_and_values(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "report.csv"
            item = PlanItem(
                root / "origem.txt",
                root / "destino" / "origem.txt",
                "Textos",
                "move",
                "planned",
                sha256="abc123",
                message="Simulacao",
            )

            write_csv_report([item], report)

            with report.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                rows = list(reader)
            self.assertEqual(tuple(reader.fieldnames or ()), CSV_FIELDS)
            self.assertEqual(rows[0]["status"], "planned")
            self.assertEqual(rows[0]["sha256"], "abc123")
