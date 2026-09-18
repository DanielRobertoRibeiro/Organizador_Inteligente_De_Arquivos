"""Saida em terminal, log e relatorio CSV."""

from __future__ import annotations

import csv
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from organizer.models import ExecutionSummary, PlanItem

CSV_FIELDS = (
    "timestamp",
    "source",
    "target",
    "category",
    "action",
    "status",
    "sha256",
    "message",
)

_owned_handler: logging.Handler | None = None
_previous_root_level: int | None = None


def configure_logging(path: Path, *, verbose: bool = False) -> None:
    """Anexa um log UTF-8 proprio sem substituir handlers da aplicacao hospedeira."""

    global _owned_handler, _previous_root_level
    close_logging()

    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root_logger = logging.getLogger()
    _previous_root_level = root_logger.level
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    root_logger.addHandler(handler)
    _owned_handler = handler


def close_logging() -> None:
    """Fecha apenas o handler criado pelo organizador e restaura o nivel anterior."""

    global _owned_handler, _previous_root_level
    if _owned_handler is None:
        return
    root_logger = logging.getLogger()
    root_logger.removeHandler(_owned_handler)
    _owned_handler.close()
    _owned_handler = None
    if _previous_root_level is not None:
        root_logger.setLevel(_previous_root_level)
        _previous_root_level = None


def write_csv_report(items: list[PlanItem], path: Path) -> Path:
    """Grava o estado final de todos os itens usando o contrato do SDD."""

    timestamp = datetime.now(UTC).isoformat()
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "timestamp": timestamp,
                    "source": str(item.source),
                    "target": str(item.target),
                    "category": item.category,
                    "action": item.action,
                    "status": item.status,
                    "sha256": item.sha256 or "",
                    "message": item.message or "",
                }
            )
    return path


def print_plan(items: list[PlanItem], stream: TextIO) -> None:
    """Exibe um plano compacto e legivel, inclusive quando estiver vazio."""

    if not items:
        print("Nenhum arquivo regular encontrado na origem.", file=stream)
        return

    print("\nPLANO DE ORGANIZACAO", file=stream)
    print("-" * 88, file=stream)
    for item in items:
        print(f"[{item.status.upper():9}] {item.source.name}", file=stream)
        print(f"  categoria: {item.category}", file=stream)
        print(f"  destino:   {item.target}", file=stream)
        if item.message:
            print(f"  detalhe:   {item.message}", file=stream)


def print_summary(summary: ExecutionSummary, stream: TextIO, *, applied: bool) -> None:
    """Exibe contadores finais e deixa explicito o modo usado."""

    mode = "APLICACAO" if applied else "SIMULACAO"
    print(f"\nRESUMO ({mode})", file=stream)
    print(
        " | ".join(
            (
                f"planejados: {summary.planned}",
                f"movidos: {summary.moved}",
                f"ignorados: {summary.skipped}",
                f"duplicados: {summary.duplicates}",
                f"falhas: {summary.failed}",
            )
        ),
        file=stream,
    )
