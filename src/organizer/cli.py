"""Interface de linha de comando do Organizador Inteligente."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

from organizer import __version__
from organizer.config import ConfigError, load_config
from organizer.executor import execute_plan
from organizer.models import ExecutionSummary
from organizer.planner import build_plan
from organizer.reports import (
    close_logging,
    configure_logging,
    print_plan,
    print_summary,
    write_csv_report,
)
from organizer.scanner import SourceError, scan_files

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser publico da CLI."""

    parser = argparse.ArgumentParser(
        prog="organizer",
        description="Organiza arquivos por regras, em modo de simulacao por padrao.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="analisa e planeja a organizacao")
    analyze.add_argument("--source", required=True, type=Path, help="pasta de origem")
    analyze.add_argument("--config", required=True, type=Path, help="arquivo JSON de regras")
    analyze.add_argument(
        "--apply",
        action="store_true",
        help="aplica o plano; sem esta opcao, somente simula",
    )
    analyze.add_argument("--verbose", action="store_true", help="aumenta o detalhe do log")
    return parser


def _artifact_paths(now: datetime | None = None) -> tuple[Path, Path]:
    timestamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%S%fZ")
    current = Path.cwd()
    return current / f"organizer-{timestamp}.log", current / f"organizer-{timestamp}.csv"


def _run_analyze(args: argparse.Namespace) -> int:
    log_path, report_path = _artifact_paths()
    logging_ready = False
    try:
        configure_logging(log_path, verbose=args.verbose)
        logging_ready = True
        source = args.source.expanduser().resolve()
        LOGGER.info("Execucao iniciada em modo %s", "aplicacao" if args.apply else "simulacao")
        LOGGER.info("Origem solicitada: %s", source)
        config = load_config(args.config, source)
        files = scan_files(source, exclude=(log_path, report_path))
        items = build_plan(files, config)

        LOGGER.info("Destino: %s", config.destination_root)
        LOGGER.debug("Arquivos regulares encontrados: %d", len(files))
        for item in items:
            LOGGER.info(
                "Plano: %s | %s -> %s | categoria=%s",
                item.status,
                item.source,
                item.target,
                item.category,
            )

        if args.apply:
            execute_plan(items, config.destination_root)

        print_plan(items, sys.stdout)
        summary = ExecutionSummary.from_items(items)
        print_summary(summary, sys.stdout, applied=args.apply)
        write_csv_report(items, report_path)
        LOGGER.info("Relatorio CSV: %s", report_path)

        print(f"Relatorio: {report_path}")
        print(f"Log:       {log_path}")
        return 1 if summary.failed else 0
    except (ConfigError, SourceError, OSError) as exc:
        if logging_ready:
            LOGGER.error("Execucao cancelada: %s", exc)
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    finally:
        if logging_ready:
            close_logging()


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a CLI e retorna um codigo adequado para automacao."""

    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        return _run_analyze(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
