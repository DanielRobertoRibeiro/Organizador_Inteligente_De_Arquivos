"""Testes da leitura e validacao das regras externas."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.config import ConfigError, load_config


class ConfigTests(TestCase):
    def _write_config(self, root: Path, payload: object) -> Path:
        path = root / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_relative_destination_is_resolved_from_config_directory(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            config_path = self._write_config(
                root,
                {
                    "destination_root": "saida",
                    "default_category": "Outros",
                    "categories": {"Texto": [".txt"]},
                },
            )

            config = load_config(config_path, source)

            self.assertEqual(config.destination_root, (root / "saida").resolve())

    def test_rejects_extension_shared_by_categories_ignoring_case(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            config_path = self._write_config(
                root,
                {
                    "destination_root": "saida",
                    "categories": {"A": [".TXT"], "B": [".txt"]},
                },
            )

            with self.assertRaisesRegex(ConfigError, "mais de uma categoria"):
                load_config(config_path, source)

    def test_rejects_destination_equal_to_source(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            config_path = self._write_config(
                root,
                {"destination_root": str(source), "categories": {}},
            )

            with self.assertRaisesRegex(ConfigError, "nao pode ser igual"):
                load_config(config_path, source)

    def test_rejects_category_that_contains_a_path(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            config_path = self._write_config(
                root,
                {"destination_root": "saida", "categories": {"../escape": [".txt"]}},
            )

            with self.assertRaisesRegex(ConfigError, "apenas um nome"):
                load_config(config_path, source)
