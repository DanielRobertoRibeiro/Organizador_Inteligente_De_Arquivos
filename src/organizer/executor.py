"""Aplicacao do plano com protecao contra sobrescrita."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from organizer.models import PlanItem
from organizer.planner import _is_inside, unique_target

LOGGER = logging.getLogger(__name__)


def _copy_then_remove(source: Path, target: Path) -> None:
    """Move sem sobrescrever, reservando o destino com criacao exclusiva."""

    created = False
    source_removed = False
    try:
        with source.open("rb") as input_stream, target.open("xb") as output_stream:
            created = True
            shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)
        shutil.copystat(source, target, follow_symlinks=False)
        source.unlink()
        source_removed = True
    except Exception:
        if created and not source_removed:
            try:
                target.unlink(missing_ok=True)
            except OSError:
                LOGGER.exception("Nao foi possivel remover o destino parcial: %s", target)
        raise


def execute_plan(items: list[PlanItem], destination_root: Path) -> list[PlanItem]:
    """Executa itens planejados; uma falha individual nao interrompe os demais."""

    destination_root = destination_root.resolve(strict=False)
    used_targets: set[str] = set()
    for item in items:
        if item.status != "planned" or item.action != "move":
            continue

        try:
            while True:
                target = unique_target(item.target.parent, item.target.name, used_targets)
                if not _is_inside(target, destination_root):
                    raise ValueError("Destino fora da raiz configurada.")
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    _copy_then_remove(item.source, target)
                except FileExistsError:
                    LOGGER.warning("Colisao detectada durante a aplicacao: %s", target)
                    continue
                break
        except (OSError, ValueError) as exc:
            item.status = "failed"
            item.message = f"Falha ao mover: {exc}"
            LOGGER.exception("Falha ao mover %s para %s", item.source, item.target)
            continue

        item.target = target
        used_targets.add(str(target.resolve(strict=False)))
        item.status = "moved"
        item.message = "Arquivo movido com sucesso."
        LOGGER.info("Movido: %s -> %s", item.source, item.target)
    return items
