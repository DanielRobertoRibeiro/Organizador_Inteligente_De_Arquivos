"""Modelos de dados compartilhados pela aplicacao."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

PlanStatus = Literal["planned", "moved", "skipped", "duplicate", "failed"]
PlanAction = Literal["move", "skip"]


@dataclass(frozen=True, slots=True)
class OrganizerConfig:
    """Configuracao validada e pronta para uso pelo planejador."""

    destination_root: Path
    default_category: str
    categories: dict[str, tuple[str, ...]]


@dataclass(slots=True)
class PlanItem:
    """Uma decisao individual do plano de organizacao."""

    source: Path
    target: Path
    category: str
    action: PlanAction
    status: PlanStatus
    sha256: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionSummary:
    """Contadores finais de uma simulacao ou aplicacao."""

    planned: int = 0
    moved: int = 0
    skipped: int = 0
    duplicates: int = 0
    failed: int = 0

    @classmethod
    def from_items(cls, items: list[PlanItem]) -> "ExecutionSummary":
        """Cria um resumo contando os estados atuais dos itens."""

        return cls(
            planned=sum(item.status == "planned" for item in items),
            moved=sum(item.status == "moved" for item in items),
            skipped=sum(item.status == "skipped" for item in items),
            duplicates=sum(item.status == "duplicate" for item in items),
            failed=sum(item.status == "failed" for item in items),
        )
