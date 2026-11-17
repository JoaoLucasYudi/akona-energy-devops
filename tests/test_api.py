def test_lista_todos_os_chamados(client):
    resposta = client.get("/api/chamados")
    assert resposta.status_code == 200
    chamados = resposta.json()
    assert len(chamados) == 300
    assert {c["status"] for c in chamados} == {"aberto", "em andamento", "resolvido"}


def test_detalhe_de_chamado(client):
    resposta = client.get("/api/chamados/1001")
    assert resposta.status_code == 200
    assert set(resposta.json()) == {
        "id",
        "cidadao_id",
        "tipo",
        "bairro",
        "status",
        "prioridade",
        "aberto_em",
        "resolvido_em",
        "prazo_horas",
        "ponto_id",
        "ponto_referencia",
    }


def test_chamado_inexistente_retorna_404(client):
    assert client.get("/api/chamados/999").status_code == 404


def test_indicadores_em_json(client):
    resposta = client.get("/api/indicadores?dias=30")
    assert resposta.status_code == 200
    painel = resposta.json()
    assert painel["dias"] == 30
    for campo in (
        "abertos",
        "tempo_medio_reparo_horas",
        "percentual_no_prazo",
        "gap_equidade",
        "percentual_reincidencia",
        "por_bairro",
        "semanal",
    ):
        assert campo in painel
    assert len(painel["semanal"]) == 12


def test_indicadores_rejeita_periodo_invalido(client):
    assert client.get("/api/indicadores?dias=0").status_code == 422
