"""Testes da aplicacao segura do plano."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.executor import execute_plan
from organizer.models import OrganizerConfig, PlanItem
from organizer.planner import build_plan
from organizer.scanner import scan_files


class ExecutorTests(TestCase):
    def _config(self, destination: Path) -> OrganizerConfig:
        return OrganizerConfig(destination, "Outros", {"Textos": (".txt",)})

    def test_apply_creates_category_and_moves_file(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            original = source / "nota.txt"
            original.write_text("conteudo", encoding="utf-8")
            config = self._config(root / "saida")
            plan = build_plan(scan_files(source), config)

            execute_plan(plan, config.destination_root)

            self.assertEqual(plan[0].status, "moved")
            self.assertFalse(original.exists())
            self.assertEqual((root / "saida" / "Textos" / "nota.txt").read_text(), "conteudo")

    def test_apply_never_overwrites_existing_file(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            category = root / "saida" / "Textos"
            source.mkdir()
            category.mkdir(parents=True)
            original = source / "nota.txt"
            existing = category / "nota.txt"
            original.write_text("novo", encoding="utf-8")
            existing.write_text("antigo", encoding="utf-8")
            config = self._config(root / "saida")
            plan = build_plan(scan_files(source), config)

            execute_plan(plan, config.destination_root)

            self.assertEqual(existing.read_text(encoding="utf-8"), "antigo")
            self.assertEqual((category / "nota (1).txt").read_text(encoding="utf-8"), "novo")

    def test_failure_does_not_stop_following_items(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            destination = root / "saida"
            source.mkdir()
            valid = source / "valido.txt"
            valid.write_text("ok", encoding="utf-8")
            items = [
                PlanItem(
                    source / "inexistente.txt",
                    destination / "Textos" / "inexistente.txt",
                    "Textos",
                    "move",
                    "planned",
                ),
                PlanItem(
                    valid,
                    destination / "Textos" / "valido.txt",
                    "Textos",
                    "move",
                    "planned",
                ),
            ]

            execute_plan(items, destination)

            self.assertEqual(items[0].status, "failed")
            self.assertEqual(items[1].status, "moved")
            self.assertTrue((destination / "Textos" / "valido.txt").exists())

    def test_duplicate_is_not_moved_or_deleted(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            first = source / "a.txt"
            duplicate = source / "b.txt"
            first.write_text("igual", encoding="utf-8")
            duplicate.write_text("igual", encoding="utf-8")
            config = self._config(root / "saida")
            plan = build_plan(scan_files(source), config)

            execute_plan(plan, config.destination_root)

            self.assertEqual(plan[1].status, "duplicate")
            self.assertTrue(duplicate.exists())
