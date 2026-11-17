"""Gera `app/data/mock.json` com chamados sintéticos dos últimos 90 dias em Osasco.

O cenário é simulado, com seed fixa (o arquivo sai sempre igual):
- cerca de 300 chamados em 12 bairros reais de Osasco, distribuídos ao longo de 90 dias
  até a data de referência;
- o prazo de cada chamado vem do tipo (fio caído 6 h, queda de energia 24 h,
  poste apagado 48 h, lâmpada piscando 72 h);
- o tempo de reparo é sorteado em torno do prazo e multiplicado por um fator do bairro:
  bairros periféricos demoram mais, para o gap de equidade aparecer no painel;
- cada chamado aponta para um poste (`ponto_id`) de um conjunto de 60 por bairro,
  o que gera reincidência;
- chamados cujo reparo terminaria depois da data de referência ficam abertos.

Uso:
    python scripts/gerar_mock.py
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 2026
TOTAL = 300
DIAS = 90
BRT = timezone(timedelta(hours=-3))
REFERENCIA = datetime(2026, 11, 16, 12, 0, tzinfo=BRT)
ARQUIVO = Path(__file__).resolve().parent.parent / "app" / "data" / "mock.json"

PRAZOS = {"fio caído": 6, "queda de energia": 24, "poste apagado": 48, "lâmpada piscando": 72}
PESOS_TIPO = {"poste apagado": 45, "lâmpada piscando": 25, "queda de energia": 18, "fio caído": 12}
PRIORIDADES = {
    "fio caído": "alta",
    "queda de energia": "alta",
    "poste apagado": "média",
    "lâmpada piscando": "baixa",
}

# Fator multiplicador do tempo de reparo: acima de 1, o bairro espera mais.
BAIRROS = {
    "Centro": 0.6,
    "Presidente Altino": 0.7,
    "Vila Yara": 0.7,
    "Bonfim": 0.8,
    "Km 18": 0.9,
    "Quitaúna": 1.0,
    "Novo Osasco": 1.1,
    "Helena Maria": 1.2,
    "Rochdale": 1.4,
    "Munhoz Júnior": 1.5,
    "Jardim Bussocaba": 1.6,
    "Jardim D'Abril": 1.9,
}
POSTES_POR_BAIRRO = 60
CHANCE_PENDENCIA = 0.08  # chamado esquecido na fila: demora 3 a 6 vezes mais

CIDADAO_DEMO = {"id": 1, "nome": "Ana Fictícia da Silva", "bairro": "Presidente Altino"}


def _iso(momento: datetime | None) -> str | None:
    return momento.isoformat(timespec="minutes") if momento else None


def gerar() -> dict:
    rnd = random.Random(SEED)  # noqa: S311 (dados simulados, não é criptografia)
    bairros = list(BAIRROS)
    rascunhos = []
    for _ in range(TOTAL):
        bairro = rnd.choice(bairros)
        tipo = rnd.choices(list(PESOS_TIPO), weights=list(PESOS_TIPO.values()))[0]
        aberto_em = REFERENCIA - timedelta(minutes=rnd.randint(30, DIAS * 24 * 60))
        prazo = PRAZOS[tipo]
        horas = prazo * BAIRROS[bairro] * rnd.lognormvariate(-0.35, 0.4)
        if rnd.random() < CHANCE_PENDENCIA:
            horas *= rnd.uniform(3, 6)
        resolvido_em = aberto_em + timedelta(hours=max(horas, 0.5))
        posicao = bairros.index(bairro) + 1
        ponto_id = f"OSC-{posicao:02d}{rnd.randint(1, POSTES_POR_BAIRRO):03d}"
        rascunhos.append((aberto_em, bairro, tipo, prazo, resolvido_em, ponto_id))

    rascunhos.sort()
    chamados = []
    for indice, (aberto_em, bairro, tipo, prazo, resolvido_em, ponto_id) in enumerate(rascunhos):
        if resolvido_em <= REFERENCIA:
            status = "resolvido"
        else:
            resolvido_em = None
            # Ainda não resolvido: parte dos chamados já tem equipe em campo.
            status = "em andamento" if rnd.random() < 0.5 else "aberto"
        chamados.append(
            {
                "id": 1001 + indice,
                "cidadao_id": None,
                "tipo": tipo,
                "bairro": bairro,
                "status": status,
                "prioridade": PRIORIDADES[tipo],
                "aberto_em": _iso(aberto_em),
                "resolvido_em": _iso(resolvido_em),
                "prazo_horas": prazo,
                "ponto_id": ponto_id,
                "ponto_referencia": ponto_id,
            }
        )

    _atribuir_ao_cidadao_demo(chamados)
    return {"cidadaos": [CIDADAO_DEMO], "chamados": chamados}


def _atribuir_ao_cidadao_demo(chamados: list[dict]) -> None:
    """Dá à cidadã fictícia os chamados mais recentes de cada status (dois resolvidos)."""
    recentes = list(reversed(chamados))
    for status in ("aberto", "em andamento", "resolvido", "resolvido"):
        chamado = next(c for c in recentes if c["status"] == status and not c["cidadao_id"])
        chamado["cidadao_id"] = CIDADAO_DEMO["id"]


def main() -> None:
    dados = gerar()
    linhas = [json.dumps(c, ensure_ascii=False) for c in dados["chamados"]]
    cidadaos = json.dumps(dados["cidadaos"], ensure_ascii=False)
    corpo = ",\n    ".join(linhas)
    texto = f'{{\n  "cidadaos": {cidadaos},\n  "chamados": [\n    {corpo}\n  ]\n}}\n'
    ARQUIVO.write_text(texto, encoding="utf-8")
    print(f"{len(dados['chamados'])} chamados gravados em {ARQUIVO}")


if __name__ == "__main__":
    main()
