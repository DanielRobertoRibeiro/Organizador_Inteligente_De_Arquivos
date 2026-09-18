"""Descoberta nao recursiva e segura de arquivos da origem."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


class SourceError(ValueError):
    """Erro que impede a leitura da pasta de origem."""


def scan_files(source: Path, *, exclude: Iterable[Path] = ()) -> list[Path]:
    """Lista arquivos regulares diretos, ignorando links e caminhos excluidos."""

    source = source.expanduser().resolve()
    if not source.exists():
        raise SourceError(f"Pasta de origem nao encontrada: {source}")
    if not source.is_dir():
        raise SourceError(f"A origem nao e uma pasta: {source}")

    try:
        entries = sorted(source.iterdir(), key=lambda entry: (entry.name.casefold(), entry.name))
    except OSError as exc:
        raise SourceError(f"Nao foi possivel listar a origem {source}: {exc}") from exc

    excluded = {path.resolve(strict=False) for path in exclude}
    files: list[Path] = []
    for entry in entries:
        try:
            if entry.resolve(strict=False) in excluded:
                continue
            if entry.is_symlink():
                LOGGER.warning("Link simbolico ignorado: %s", entry)
                continue
            if entry.is_file():
                files.append(entry)
        except OSError as exc:
            LOGGER.warning("Entrada ignorada (%s): %s", entry, exc)
    return files
