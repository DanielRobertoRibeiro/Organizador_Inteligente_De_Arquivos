"""Calculo de hash para deteccao de conteudos identicos."""

from __future__ import annotations

import hashlib
from pathlib import Path

DEFAULT_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Calcula SHA-256 em blocos, sem carregar o arquivo inteiro na memoria."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()
