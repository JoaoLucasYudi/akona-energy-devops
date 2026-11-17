"""Chamados em memória do processo, carregados de `app/data/mock.json` (dados simulados).

Chamados novos e mudanças de status ficam só na memória: funciona porque o Container App
roda com uma réplica, e tudo se perde quando o container reinicia.
"""

import copy
import json
import re
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ARQUIVO = Path(__file__).parent / "data" / "mock.json"
_MOCK = json.loads(_ARQUIVO.read_text(encoding="utf-8"))

BRT = timezone(timedelta(hours=-3))
PRAZOS = {"fio caído": 6, "queda de energia": 24, "poste apagado": 48, "lâmpada piscando": 72}
PRIORIDADES = {
    "fio caído": "alta",
    "queda de energia": "alta",
    "poste apagado": "média",
    "lâmpada piscando": "baixa",
}
TIPOS = tuple(PRAZOS)
BAIRROS = tuple(sorted({c["bairro"] for c in _MOCK["chamados"]}))
PONTO_MAX = 120
# Teto de chamados novos por processo, para a URL pública não encher a memória.
LIMITE_NOVOS = 1000
# Transições permitidas: status atual → próximo status.
PROXIMO_STATUS = {"aberto": "em andamento", "em andamento": "resolvido"}
_CODIGO_POSTE = re.compile(r"OSC-\d{5}")

_trava = threading.Lock()
_chamados: list[dict] = []
_novos = 0


def agora() -> datetime:
    return datetime.now(BRT).replace(second=0, microsecond=0)


def reiniciar() -> None:
    """Volta ao estado do mock (usado na carga do módulo e nos testes)."""
    global _novos
    with _trava:
        _chamados[:] = copy.deepcopy(_MOCK["chamados"])
        _novos = 0


reiniciar()


def listar_chamados() -> list[dict]:
    return list(_chamados)


def obter_chamado(chamado_id: int) -> dict | None:
    return next((c for c in _chamados if c["id"] == chamado_id), None)


def obter_cidadao(cidadao_id: int) -> dict:
    return next(c for c in _MOCK["cidadaos"] if c["id"] == cidadao_id)


def chamados_do_cidadao(cidadao_id: int) -> list[dict]:
    """Do mais recente para o mais antigo."""
    return sorted(
        (c for c in _chamados if c["cidadao_id"] == cidadao_id),
        key=lambda c: c["aberto_em"],
        reverse=True,
    )


class LimiteAtingido(Exception):
    pass


def criar_chamado(cidadao_id: int, tipo: str, bairro: str, ponto: str) -> dict:
    """Grava um chamado aberto. `ponto` já validado; vira `ponto_id` se for um código de poste."""
    global _novos
    with _trava:
        if _novos >= LIMITE_NOVOS:
            raise LimiteAtingido
        chamado = {
            "id": max(c["id"] for c in _chamados) + 1,
            "cidadao_id": cidadao_id,
            "tipo": tipo,
            "bairro": bairro,
            "status": "aberto",
            "prioridade": PRIORIDADES[tipo],
            "aberto_em": agora().isoformat(timespec="minutes"),
            "resolvido_em": None,
            "prazo_horas": PRAZOS[tipo],
            "ponto_id": ponto if _CODIGO_POSTE.fullmatch(ponto) else None,
            "ponto_referencia": ponto,
        }
        _chamados.append(chamado)
        _novos += 1
    return chamado


def avancar_status(chamado_id: int, novo_status: str) -> dict | None:
    """Aplica a transição se ela for a próxima do chamado; devolve o chamado ou None."""
    with _trava:
        chamado = obter_chamado(chamado_id)
        if chamado is None or PROXIMO_STATUS.get(chamado["status"]) != novo_status:
            return None
        chamado["status"] = novo_status
        if novo_status == "resolvido":
            chamado["resolvido_em"] = agora().isoformat(timespec="minutes")
    return chamado
