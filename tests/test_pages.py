def test_home_apresenta_proposta_e_links_de_demonstracao(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "Akona Energy" in resposta.text
    assert 'href="/chamados"' in resposta.text
    assert 'href="/gestao"' in resposta.text


def test_area_do_cidadao_lista_so_os_chamados_dele(client):
    resposta = client.get("/chamados")
    assert resposta.status_code == 200
    assert "Ana Fictícia da Silva" in resposta.text
    for proprio in (101, 102, 103, 104):
        assert f'href="/chamados/{proprio}"' in resposta.text
    for alheio in (105, 109, 120):
        assert f'href="/chamados/{alheio}"' not in resposta.text


def test_detalhe_de_chamado_do_cidadao(client):
    resposta = client.get("/chamados/103")
    assert resposta.status_code == 200
    assert "#103" in resposta.text
    assert "queda de energia" in resposta.text
    assert "resolvido" in resposta.text


def test_detalhe_de_chamado_de_outro_cidadao_retorna_404(client):
    assert client.get("/chamados/109").status_code == 404


def test_detalhe_de_chamado_inexistente_retorna_404(client):
    assert client.get("/chamados/999").status_code == 404


def test_novo_chamado_e_ilustrativo_e_nao_grava(client):
    resposta = client.get("/chamados/novo")
    assert resposta.status_code == 200
    assert "<form" in resposta.text
    assert "action=" not in resposta.text
    assert "method=" not in resposta.text
    assert "não grava" in resposta.text


def test_gestao_lista_todos_os_chamados(client):
    resposta = client.get("/gestao")
    assert resposta.status_code == 200
    for chamado_id in range(101, 121):
        assert f"#{chamado_id}" in resposta.text


def test_gestao_mostra_contagens_por_status_tipo_e_bairro(client):
    corpo = client.get("/gestao").text
    esperado = {
        "aberto": 7,
        "em andamento": 5,
        "resolvido": 8,
        "poste apagado": 7,
        "lâmpada piscando": 5,
        "queda de energia": 5,
        "fio caído": 3,
        "Presidente Altino": 4,
        "Centro": 4,
        "Vila Yara": 4,
        "Rochdale": 4,
        "Jardim Bussocaba": 4,
    }
    for rotulo, total in esperado.items():
        assert f'<th scope="row">{rotulo}</th><td>{total}</td>' in corpo


def test_privacidade_explica_que_nao_ha_dados_pessoais(client):
    resposta = client.get("/privacidade")
    assert resposta.status_code == 200
    assert "LGPD" in resposta.text
    assert "fictícios" in resposta.text


def test_nenhuma_pagina_usa_javascript_nem_cookie(client):
    for rota in ("/", "/chamados", "/chamados/101", "/chamados/novo", "/gestao", "/privacidade"):
        resposta = client.get(rota)
        assert resposta.status_code == 200, rota
        assert "<script" not in resposta.text.lower(), rota
        assert "set-cookie" not in resposta.headers, rota
