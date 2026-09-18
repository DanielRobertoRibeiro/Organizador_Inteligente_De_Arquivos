"""Organizador Inteligente de Arquivos."""

import logging

from organizer.models import OrganizerConfig, PlanItem

__all__ = ["OrganizerConfig", "PlanItem"]
__version__ = "1.0.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())
