"""Leitura e validacao da configuracao JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from organizer.models import OrganizerConfig


class ConfigError(ValueError):
    """Erro de configuracao com mensagem adequada para a CLI."""


def _validate_category_name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{field} deve ser um texto nao vazio.")
    if value != value.strip():
        raise ConfigError(f"{field} nao pode comecar ou terminar com espacos.")
    if value in {".", ".."} or any(separator in value for separator in ("/", "\\")):
        raise ConfigError(f"{field} deve ser apenas um nome de pasta, sem caminhos.")
    if "\x00" in value:
        raise ConfigError(f"{field} contem um caractere invalido.")
    return value


def _validate_categories(raw: object) -> dict[str, tuple[str, ...]]:
    if not isinstance(raw, dict):
        raise ConfigError("categories deve ser um objeto JSON.")

    categories: dict[str, tuple[str, ...]] = {}
    extension_owners: dict[str, str] = {}
    for raw_name, raw_extensions in raw.items():
        name = _validate_category_name(raw_name, "Nome da categoria")
        if not isinstance(raw_extensions, list):
            raise ConfigError(f"A categoria {name!r} deve conter uma lista de extensoes.")

        normalized: list[str] = []
        for extension in raw_extensions:
            if not isinstance(extension, str) or len(extension) < 2 or not extension.startswith("."):
                raise ConfigError(
                    f"Extensao invalida em {name!r}: {extension!r}. "
                    "Use valores como '.pdf'."
                )
            extension = extension.casefold()
            if any(character in extension for character in ("/", "\\", "\x00")):
                raise ConfigError(f"Extensao invalida em {name!r}: {extension!r}.")
            owner = extension_owners.get(extension)
            if owner is not None:
                raise ConfigError(
                    f"A extensao {extension!r} aparece em mais de uma categoria: "
                    f"{owner!r} e {name!r}."
                )
            extension_owners[extension] = name
            normalized.append(extension)
        categories[name] = tuple(normalized)
    return categories


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            raw = json.load(stream)
    except FileNotFoundError as exc:
        raise ConfigError(f"Arquivo de configuracao nao encontrado: {path}") from exc
    except PermissionError as exc:
        raise ConfigError(f"Sem permissao para ler a configuracao: {path}") from exc
    except UnicodeDecodeError as exc:
        raise ConfigError(f"A configuracao deve estar codificada em UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"JSON invalido em {path}, linha {exc.lineno}, coluna {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(raw, dict):
        raise ConfigError("A raiz da configuracao deve ser um objeto JSON.")
    return raw


def load_config(config_path: Path, source: Path) -> OrganizerConfig:
    """Carrega e valida o JSON, resolvendo o destino para um caminho absoluto.

    Caminhos relativos de ``destination_root`` sao interpretados a partir da pasta
    que contem o arquivo de configuracao, e nao a partir do terminal.
    """

    path = config_path.expanduser().resolve()
    raw = _load_json(path)

    destination_value = raw.get("destination_root")
    if not isinstance(destination_value, str) or not destination_value.strip():
        raise ConfigError("destination_root e obrigatorio e deve ser um texto nao vazio.")

    destination = Path(destination_value).expanduser()
    if not destination.is_absolute():
        destination = path.parent / destination
    destination = destination.resolve()

    source = source.expanduser().resolve()
    if destination == source:
        raise ConfigError("O destino nao pode ser igual a pasta de origem.")
    if destination.exists() and not destination.is_dir():
        raise ConfigError(f"O destino existe, mas nao e uma pasta: {destination}")

    default_category = _validate_category_name(
        raw.get("default_category", "Outros"), "default_category"
    )
    categories = _validate_categories(raw.get("categories"))
    return OrganizerConfig(
        destination_root=destination,
        default_category=default_category,
        categories=categories,
    )
