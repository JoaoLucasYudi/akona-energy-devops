"""Indicadores de impacto (seção 6 de docs/negocio.md), calculados sobre uma lista de chamados.

Funções puras: recebem os chamados e o instante de referência (`agora`) e não leem nada de fora.
Tempos em horas. Um chamado está no prazo quando foi resolvido em até `prazo_horas`.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean

JANELA_REINCIDENCIA = timedelta(days=30)
SEMANAS = 12


def _data(valor: str | None) -> datetime | None:
    return datetime.fromisoformat(valor) if valor else None


def _horas_de_reparo(chamado: dict) -> float:
    delta = _data(chamado["resolvido_em"]) - _data(chamado["aberto_em"])
    return delta.total_seconds() / 3600


def _resolvidos(chamados: list[dict]) -> list[dict]:
    return [c for c in chamados if c["resolvido_em"]]


def _arredondar(valor: float | None, casas: int = 1) -> float | None:
    return None if valor is None else round(valor, casas)


def do_periodo(chamados: list[dict], agora: datetime, dias: int) -> list[dict]:
    """Chamados abertos nos últimos `dias` dias."""
    inicio = agora - timedelta(days=dias)
    return [c for c in chamados if _data(c["aberto_em"]) >= inicio]


def tempo_medio_reparo(chamados: list[dict]) -> float | None:
    resolvidos = _resolvidos(chamados)
    return mean(_horas_de_reparo(c) for c in resolvidos) if resolvidos else None


def percentual_no_prazo(chamados: list[dict]) -> float | None:
    resolvidos = _resolvidos(chamados)
    if not resolvidos:
        return None
    no_prazo = sum(1 for c in resolvidos if _horas_de_reparo(c) <= c["prazo_horas"])
    return 100 * no_prazo / len(resolvidos)


def gap_equidade(chamados: list[dict]) -> float | None:
    """Tempo médio do bairro mais lento ÷ tempo médio da cidade."""
    cidade = tempo_medio_reparo(chamados)
    if not cidade:
        return None
    por_bairro = defaultdict(list)
    for chamado in _resolvidos(chamados):
        por_bairro[chamado["bairro"]].append(chamado)
    return max(tempo_medio_reparo(lista) for lista in por_bairro.values()) / cidade


def percentual_reincidencia(chamados: list[dict]) -> float | None:
    """Resolvidos cujo ponto teve novo chamado em até 30 dias ÷ resolvidos."""
    resolvidos = [c for c in _resolvidos(chamados) if c["ponto_id"]]
    if not resolvidos:
        return None
    aberturas = defaultdict(list)
    for chamado in chamados:
        if chamado["ponto_id"]:
            aberturas[chamado["ponto_id"]].append(_data(chamado["aberto_em"]))
    reincidentes = 0
    for chamado in resolvidos:
        fim = _data(chamado["resolvido_em"])
        if any(
            fim < aberto <= fim + JANELA_REINCIDENCIA for aberto in aberturas[chamado["ponto_id"]]
        ):
            reincidentes += 1
    return 100 * reincidentes / len(resolvidos)


def por_bairro(chamados: list[dict]) -> list[dict]:
    """Uma linha por bairro, do maior para o menor tempo médio (sem resolvidos fica no fim)."""
    grupos = defaultdict(list)
    for chamado in chamados:
        grupos[chamado["bairro"]].append(chamado)
    linhas = [
        {
            "bairro": bairro,
            "chamados": len(lista),
            "tempo_medio_horas": tempo_medio_reparo(lista),
            "percentual_no_prazo": percentual_no_prazo(lista),
        }
        for bairro, lista in grupos.items()
    ]
    linhas.sort(
        key=lambda linha: (linha["tempo_medio_horas"] is None, -(linha["tempo_medio_horas"] or 0))
    )
    maior = max((linha["tempo_medio_horas"] or 0 for linha in linhas), default=0)
    for linha in linhas:
        tempo = linha["tempo_medio_horas"]
        linha["barra_percentual"] = round(100 * tempo / maior) if tempo and maior else 0
        linha["tempo_medio_horas"] = _arredondar(tempo)
        linha["percentual_no_prazo"] = _arredondar(linha["percentual_no_prazo"])
    return linhas


def semanal(chamados: list[dict], agora: datetime, semanas: int = SEMANAS) -> list[dict]:
    """Chamados abertos e resolvidos em cada uma das últimas semanas (janelas de 7 dias)."""
    linhas = []
    for i in range(semanas, 0, -1):
        inicio = agora - timedelta(weeks=i)
        fim = inicio + timedelta(weeks=1)

        def na_semana(valor: str | None, inicio=inicio, fim=fim) -> bool:
            momento = _data(valor)
            return momento is not None and inicio < momento <= fim

        linhas.append(
            {
                "inicio": inicio.date().isoformat(),
                "abertos": sum(1 for c in chamados if na_semana(c["aberto_em"])),
                "resolvidos": sum(1 for c in chamados if na_semana(c["resolvido_em"])),
            }
        )
    return linhas


def calcular(chamados: list[dict], agora: datetime, dias: int) -> dict:
    """Painel completo: cartões e tabela por bairro no período; tabela semanal das 12 semanas."""
    periodo = do_periodo(chamados, agora, dias)
    return {
        "dias": dias,
        "total": len(periodo),
        "abertos": sum(1 for c in periodo if c["status"] != "resolvido"),
        "tempo_medio_reparo_horas": _arredondar(tempo_medio_reparo(periodo)),
        "percentual_no_prazo": _arredondar(percentual_no_prazo(periodo)),
        "gap_equidade": _arredondar(gap_equidade(periodo), 2),
        "percentual_reincidencia": _arredondar(percentual_reincidencia(periodo)),
        "por_bairro": por_bairro(periodo),
        "semanal": semanal(chamados, agora),
    }
