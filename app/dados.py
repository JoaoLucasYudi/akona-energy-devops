"""Acesso somente leitura aos dados sintéticos de `app/data/mock.json`."""

import json
from collections import Counter
from functools import cache
from pathlib import Path

_ARQUIVO = Path(__file__).parent / "data" / "mock.json"

TIPOS = ("poste apagado", "lâmpada piscando", "fio caído", "queda de energia")


@cache
def _mock() -> dict:
    return json.loads(_ARQUIVO.read_text(encoding="utf-8"))


def listar_chamados() -> list[dict]:
    return _mock()["chamados"]


def obter_chamado(chamado_id: int) -> dict | None:
    return next((c for c in listar_chamados() if c["id"] == chamado_id), None)


def obter_cidadao(cidadao_id: int) -> dict:
    return next(c for c in _mock()["cidadaos"] if c["id"] == cidadao_id)


def chamados_do_cidadao(cidadao_id: int) -> list[dict]:
    return [c for c in listar_chamados() if c["cidadao_id"] == cidadao_id]


def contar_por(campo: str) -> list[tuple[str, int]]:
    """Contagem de chamados por valor do campo, do mais frequente ao menos frequente."""
    return Counter(c[campo] for c in listar_chamados()).most_common()
