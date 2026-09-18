"""Testes de planejamento, colisao e duplicidade."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.models import OrganizerConfig
from organizer.planner import build_plan, unique_target
from organizer.scanner import scan_files


class PlannerTests(TestCase):
    def _config(self, destination: Path) -> OrganizerConfig:
        return OrganizerConfig(destination, "Outros", {"Textos": (".txt",)})

    def test_collision_gets_numbered_name(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "destino"
            destination.mkdir()
            (destination / "relatorio.pdf").write_text("existente", encoding="utf-8")
            (destination / "relatorio (1).pdf").write_text("existente", encoding="utf-8")

            result = unique_target(destination, "relatorio.pdf")

            self.assertEqual(result.name, "relatorio (2).pdf")

    def test_simulation_does_not_create_destination_or_move_files(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            destination = root / "saida"
            source.mkdir()
            original = source / "nota.txt"
            original.write_text("conteudo", encoding="utf-8")

            plan = build_plan(scan_files(source), self._config(destination))

            self.assertEqual(plan[0].status, "planned")
            self.assertEqual(plan[0].category, "Textos")
            self.assertTrue(original.exists())
            self.assertFalse(destination.exists())

    def test_second_equal_file_is_marked_as_duplicate(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entrada"
            source.mkdir()
            (source / "a.txt").write_text("igual", encoding="utf-8")
            (source / "b.txt").write_text("igual", encoding="utf-8")

            plan = build_plan(scan_files(source), self._config(root / "saida"))

            self.assertEqual([item.status for item in plan], ["planned", "duplicate"])
            self.assertEqual(plan[0].sha256, plan[1].sha256)
            self.assertIn("a.txt", plan[1].message or "")

    def test_read_error_marks_item_as_skipped(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "arquivo.txt"
            source.write_text("conteudo", encoding="utf-8")

            def failing_hash(_: Path) -> str:
                raise PermissionError("acesso negado")

            plan = build_plan(
                [source], self._config(root / "saida"), hash_function=failing_hash
            )

            self.assertEqual(plan[0].status, "skipped")
            self.assertEqual(plan[0].action, "skip")
            self.assertIn("acesso negado", plan[0].message or "")
