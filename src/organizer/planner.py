"""Construcao do plano seguro de organizacao."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable

from organizer.classifier import ExtensionClassifier
from organizer.duplicates import sha256_file
from organizer.models import OrganizerConfig, PlanItem

LOGGER = logging.getLogger(__name__)
HashFunction = Callable[[Path], str]


def _path_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=False)))


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def unique_target(directory: Path, filename: str, occupied: set[str] | None = None) -> Path:
    """Retorna um destino livre, considerando disco e nomes ja planejados."""

    occupied = occupied if occupied is not None else set()
    original = directory / filename
    candidate = original
    counter = 1
    while candidate.exists() or _path_key(candidate) in occupied:
        candidate = directory / f"{original.stem} ({counter}){original.suffix}"
        counter += 1
    return candidate


def build_plan(
    files: list[Path],
    config: OrganizerConfig,
    *,
    hash_function: HashFunction = sha256_file,
) -> list[PlanItem]:
    """Classifica, calcula hashes e planeja destinos sem alterar o disco."""

    classifier = ExtensionClassifier(config)
    plan: list[PlanItem] = []
    first_by_hash: dict[str, Path] = {}
    occupied: set[str] = set()

    for source in files:
        category = classifier.classify(source)
        category_root = config.destination_root / category
        preliminary_target = category_root / source.name

        if not _is_inside(preliminary_target, config.destination_root):
            message = "Destino rejeitado por estar fora da raiz configurada."
            LOGGER.error("%s Origem: %s", message, source)
            plan.append(
                PlanItem(source, preliminary_target, category, "skip", "skipped", message=message)
            )
            continue

        try:
            digest = hash_function(source)
        except OSError as exc:
            message = f"Nao foi possivel ler o arquivo: {exc}"
            LOGGER.warning("%s (%s)", message, source)
            plan.append(
                PlanItem(source, preliminary_target, category, "skip", "skipped", message=message)
            )
            continue

        original = first_by_hash.get(digest)
        if original is not None:
            message = f"Possivel duplicado de: {original}"
            plan.append(
                PlanItem(
                    source,
                    preliminary_target,
                    category,
                    "skip",
                    "duplicate",
                    sha256=digest,
                    message=message,
                )
            )
            LOGGER.warning("Duplicado sinalizado: %s", source)
            continue

        first_by_hash[digest] = source
        target = unique_target(category_root, source.name, occupied)
        occupied.add(_path_key(target))
        plan.append(
            PlanItem(
                source,
                target,
                category,
                "move",
                "planned",
                sha256=digest,
                message="Simulacao: nenhuma alteracao realizada.",
            )
        )
    return plan
