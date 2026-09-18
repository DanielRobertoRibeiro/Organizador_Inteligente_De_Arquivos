"""Testes do detector de conteudo duplicado."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from organizer.duplicates import sha256_file


class DuplicateHashTests(TestCase):
    def test_equal_contents_have_equal_hashes(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "a.bin"
            second = root / "b.bin"
            first.write_bytes(b"mesmo conteudo")
            second.write_bytes(b"mesmo conteudo")

            self.assertEqual(sha256_file(first), sha256_file(second))

    def test_different_contents_have_different_hashes(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "a.bin"
            second = root / "b.bin"
            first.write_bytes(b"conteudo A")
            second.write_bytes(b"conteudo B")

            self.assertNotEqual(sha256_file(first), sha256_file(second))
