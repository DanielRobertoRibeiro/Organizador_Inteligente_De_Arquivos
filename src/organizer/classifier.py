"""Classificacao previsivel de arquivos por extensao."""

from __future__ import annotations

from pathlib import Path

from organizer.models import OrganizerConfig


class ExtensionClassifier:
    """Classifica extensoes sem diferenciar maiusculas de minusculas."""

    def __init__(self, config: OrganizerConfig) -> None:
        self.default_category = config.default_category
        self._categories_by_extension = {
            extension.casefold(): category
            for category, extensions in config.categories.items()
            for extension in extensions
        }

    def classify(self, path: Path) -> str:
        """Retorna a categoria configurada ou a categoria padrao."""

        return self._categories_by_extension.get(path.suffix.casefold(), self.default_category)
