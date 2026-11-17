from datetime import datetime, timedelta, timezone

import pytest

from app import indicadores

BRT = timezone(timedelta(hours=-3))
AGORA = datetime(2026, 11, 16, 12, 0, tzinfo=BRT)


def chamado(bairro="Centro", horas=None, prazo=24, dias_atras=10, ponto="OSC-01001"):
    aberto = AGORA - timedelta(days=dias_atras)
    return {
        "bairro": bairro,
        "status": "resolvido" if horas is not None else "aberto",
        "aberto_em": aberto.isoformat(),
        "resolvido_em": (aberto + timedelta(hours=horas)).isoformat()
        if horas is not None
        else None,
        "prazo_horas": prazo,
        "ponto_id": ponto,
    }


def test_tempo_medio_considera_so_resolvidos():
    chamados = [chamado(horas=10), chamado(horas=30), chamado()]
    assert indicadores.tempo_medio_reparo(chamados) == 20


def test_percentual_no_prazo_inclui_o_limite_exato():
    chamados = [chamado(horas=24, prazo=24), chamado(horas=25, prazo=24), chamado(horas=1, prazo=6)]
    assert indicadores.percentual_no_prazo(chamados) == pytest.approx(200 / 3)


def test_gap_divide_bairro_mais_lento_pela_cidade():
    chamados = [
        chamado("Centro", horas=10),
        chamado("Centro", horas=10),
        chamado("Rochdale", horas=40),
    ]
    # cidade: 60 / 3 = 20 h; Rochdale: 40 h
    assert indicadores.gap_equidade(chamados) == 2


def test_reincidencia_conta_novo_chamado_no_mesmo_ponto_em_ate_30_dias():
    chamados = [
        chamado(horas=1, dias_atras=60, ponto="OSC-01001"),  # volta 20 dias depois: reincide
        chamado(dias_atras=40, ponto="OSC-01001"),
        chamado(horas=1, dias_atras=50, ponto="OSC-01002"),  # volta 45 dias depois: não conta
        chamado(dias_atras=5, ponto="OSC-01002"),
    ]
    assert indicadores.percentual_reincidencia(chamados) == 50


def test_sem_resolvidos_os_indicadores_ficam_vazios():
    chamados = [chamado()]
    assert indicadores.tempo_medio_reparo(chamados) is None
    assert indicadores.percentual_no_prazo(chamados) is None
    assert indicadores.gap_equidade(chamados) is None
    assert indicadores.percentual_reincidencia(chamados) is None


def test_por_bairro_ordena_do_mais_lento_e_escala_a_barra():
    linhas = indicadores.por_bairro(
        [chamado("Centro", horas=10), chamado("Rochdale", horas=40), chamado("Bonfim")]
    )
    assert [linha["bairro"] for linha in linhas] == ["Rochdale", "Centro", "Bonfim"]
    assert [linha["barra_percentual"] for linha in linhas] == [100, 25, 0]
    assert linhas[2]["tempo_medio_horas"] is None


def test_periodo_filtra_pela_data_de_abertura():
    chamados = [chamado(dias_atras=10), chamado(dias_atras=45)]
    assert len(indicadores.do_periodo(chamados, AGORA, 30)) == 1
    assert len(indicadores.do_periodo(chamados, AGORA, 90)) == 2


def test_semanal_conta_abertos_e_resolvidos_por_semana():
    chamados = [chamado(horas=24 * 7, dias_atras=10), chamado(dias_atras=2)]
    semanas = indicadores.semanal(chamados, AGORA)
    assert len(semanas) == 12
    assert semanas[-2] == {"inicio": "2026-11-02", "abertos": 1, "resolvidos": 0}
    assert semanas[-1] == {"inicio": "2026-11-09", "abertos": 1, "resolvidos": 1}


def test_calcular_monta_o_painel_completo():
    painel = indicadores.calcular([chamado(horas=12), chamado(dias_atras=100)], AGORA, 90)
    assert painel["total"] == 1
    assert painel["abertos"] == 0
    assert painel["tempo_medio_reparo_horas"] == 12
    assert painel["percentual_no_prazo"] == 100
    assert painel["gap_equidade"] == 1
