"""Registro dos itens do Lattes descritos por especificação (ver docs/plano-implantacao-itens.md)."""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Any

PASTA = pathlib.Path(__file__).resolve().parent / "especificacao"


@lru_cache(maxsize=None)
def especificacao(item_id: str) -> dict[str, Any] | None:
    """Especificação estruturada do item (campos do formulário real do Lattes) ou None."""
    p = PASTA / f"{item_id}.json"
    if not p.is_file() or "/" in item_id or "\\" in item_id:
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def ids_especificados() -> list[str]:
    return sorted(p.stem for p in PASTA.glob("*.json"))
