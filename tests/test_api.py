def test_lista_todos_os_chamados(client):
    resposta = client.get("/api/chamados")
    assert resposta.status_code == 200
    chamados = resposta.json()
    assert len(chamados) == 20
    assert {c["status"] for c in chamados} == {"aberto", "em andamento", "resolvido"}


def test_detalhe_de_chamado(client):
    resposta = client.get("/api/chamados/109")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": 109,
        "cidadao_id": 3,
        "tipo": "fio caído",
        "bairro": "Vila Yara",
        "status": "aberto",
        "prioridade": "alta",
        "data_abertura": "2026-11-11",
    }


def test_chamado_inexistente_retorna_404(client):
    assert client.get("/api/chamados/999").status_code == 404
