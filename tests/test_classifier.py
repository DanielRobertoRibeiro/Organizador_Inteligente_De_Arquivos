"""Testes das regras de classificacao."""

from pathlib import Path
from unittest import TestCase

from organizer.classifier import ExtensionClassifier
from organizer.models import OrganizerConfig


class ExtensionClassifierTests(TestCase):
    def setUp(self) -> None:
        config = OrganizerConfig(
            destination_root=Path("organizados"),
            default_category="Outros",
            categories={"Imagens": (".jpg", ".png"), "Documentos": (".pdf",)},
        )
        self.classifier = ExtensionClassifier(config)

    def test_classifies_known_extension(self) -> None:
        self.assertEqual(self.classifier.classify(Path("foto.jpg")), "Imagens")

    def test_extension_is_case_insensitive(self) -> None:
        self.assertEqual(self.classifier.classify(Path("FOTO.JpG")), "Imagens")

    def test_unknown_extension_uses_default_category(self) -> None:
        self.assertEqual(self.classifier.classify(Path("arquivo.xyz")), "Outros")

    def test_file_without_extension_uses_default_category(self) -> None:
        self.assertEqual(self.classifier.classify(Path("LEIAME")), "Outros")
