"""Testes de integracao da interface de linha de comando."""

from __future__ import annotations

import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.cli import main


class CliIntegrationTests(TestCase):
    def _scenario(self, root: Path) -> tuple[Path, Path, Path]:
        source = root / "entrada"
        destination = root / "organizados"
        source.mkdir()
        document = source / "LEIA-ME.TXT"
        document.write_text("demonstracao", encoding="utf-8")
        config = root / "config.json"
        config.write_text(
            json.dumps(
                {
                    "destination_root": "organizados",
                    "default_category": "Outros",
                    "categories": {"Documentos": [".txt"]},
                }
            ),
            encoding="utf-8",
        )
        return source, destination, config

    def _run_in(self, root: Path, arguments: list[str]) -> tuple[int, str, str]:
        previous = Path.cwd()
        stdout = StringIO()
        stderr = StringIO()
        try:
            os.chdir(root)
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = main(arguments)
            return result, stdout.getvalue(), stderr.getvalue()
        finally:
            os.chdir(previous)

    def test_default_mode_simulates_and_creates_audit_artifacts(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination, config = self._scenario(root)

            code, stdout, stderr = self._run_in(
                root,
                ["analyze", "--source", str(source), "--config", str(config)],
            )

            self.assertEqual(code, 0)
            self.assertEqual(stderr, "")
            self.assertIn("RESUMO (SIMULACAO)", stdout)
            self.assertTrue((source / "LEIA-ME.TXT").exists())
            self.assertFalse(destination.exists())
            self.assertEqual(len(list(root.glob("organizer-*.csv"))), 1)
            self.assertEqual(len(list(root.glob("organizer-*.log"))), 1)

    def test_apply_moves_the_planned_file(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination, config = self._scenario(root)

            code, stdout, _ = self._run_in(
                root,
                [
                    "analyze",
                    "--source",
                    str(source),
                    "--config",
                    str(config),
                    "--apply",
                ],
            )

            self.assertEqual(code, 0)
            self.assertIn("RESUMO (APLICACAO)", stdout)
            self.assertFalse((source / "LEIA-ME.TXT").exists())
            self.assertTrue((destination / "Documentos" / "LEIA-ME.TXT").exists())
