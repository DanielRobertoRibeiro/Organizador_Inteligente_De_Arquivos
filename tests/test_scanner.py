"""Testes da descoberta nao recursiva."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.scanner import SourceError, scan_files


class ScannerTests(TestCase):
    def test_lists_only_regular_files_at_root(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "arquivo.txt").write_text("ok", encoding="utf-8")
            child = root / "subpasta"
            child.mkdir()
            (child / "interno.txt").write_text("ignorado", encoding="utf-8")

            files = scan_files(root)

            self.assertEqual([path.name for path in files], ["arquivo.txt"])

    def test_missing_source_is_a_fatal_error(self) -> None:
        with TemporaryDirectory() as temporary:
            missing = Path(temporary) / "nao-existe"

            with self.assertRaisesRegex(SourceError, "nao encontrada"):
                scan_files(missing)
