import re

from app import dados

CHAMADOS_DA_ANA = (1294, 1296, 1297, 1300)


def criar(client, **campos):
    formulario = {"tipo": "poste apagado", "bairro": "Rochdale", "ponto": "OSC-09007"} | campos
    return client.post("/chamados/novo", data=formulario, follow_redirects=False)


def test_home_apresenta_proposta_e_links_de_demonstracao(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "Akona Energy" in resposta.text
    for link in ("/chamados", "/gestao", "/transparencia"):
        assert f'href="{link}"' in resposta.text


def test_area_do_cidadao_lista_so_os_chamados_dele(client):
    resposta = client.get("/chamados")
    assert resposta.status_code == 200
    assert "Ana Fictícia da Silva" in resposta.text
    for proprio in CHAMADOS_DA_ANA:
        assert f'href="/chamados/{proprio}"' in resposta.text
    for alheio in (1001, 1295, 1299):
        assert f'href="/chamados/{alheio}"' not in resposta.text


def test_detalhe_de_chamado_do_cidadao(client):
    resposta = client.get("/chamados/1297")
    assert resposta.status_code == 200
    assert "Protocolo #1297" in resposta.text
    assert "aberto" in resposta.text


def test_detalhe_de_chamado_de_outro_cidadao_retorna_404(client):
    assert client.get("/chamados/1001").status_code == 404


def test_detalhe_de_chamado_inexistente_retorna_404(client):
    assert client.get("/chamados/999").status_code == 404


def test_formulario_grava_e_avisa_para_nao_informar_dados_pessoais(client):
    resposta = client.get("/chamados/novo")
    assert resposta.status_code == 200
    assert 'method="post" action="/chamados/novo"' in resposta.text
    assert "Não informe nome, telefone ou endereço." in resposta.text
    assert 'maxlength="120"' in resposta.text
    assert "<textarea" not in resposta.text


def test_qr_code_preenche_o_ponto(client):
    resposta = client.get("/chamados/novo?ponto=OSC-01234")
    assert 'value="OSC-01234"' in resposta.text


def test_criar_chamado_redireciona_para_o_protocolo(client):
    resposta = criar(client)
    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/chamados/1301?criado=1"

    detalhe = client.get(resposta.headers["location"])
    assert "Protocolo #1301" in detalhe.text
    assert "Chamado registrado" in detalhe.text
    chamado = dados.obter_chamado(1301)
    assert chamado["status"] == "aberto"
    assert chamado["prazo_horas"] == 48
    assert chamado["ponto_id"] == "OSC-09007"
    assert 'href="/chamados/1301"' in client.get("/chamados").text


def test_ponto_em_texto_livre_nao_vira_codigo_de_poste(client):
    criar(client, ponto="em frente à praça")
    chamado = dados.obter_chamado(1301)
    assert chamado["ponto_id"] is None
    assert chamado["ponto_referencia"] == "em frente à praça"


def test_criar_chamado_escapa_o_texto_do_usuario(client):
    criar(client, ponto="<b>oi</b>")
    assert "&lt;b&gt;oi&lt;/b&gt;" in client.get("/chamados/1301").text
    assert "<b>oi</b>" not in client.get("/gestao").text


def test_criar_chamado_rejeita_entrada_invalida(client):
    for campos in ({"tipo": "outro"}, {"bairro": "Lisboa"}, {"ponto": ""}, {"ponto": "x" * 121}):
        resposta = criar(client, **campos)
        assert resposta.status_code == 422, campos
        assert 'role="alert"' in resposta.text
    assert dados.obter_chamado(1301) is None


def test_criar_chamado_respeita_o_limite_em_memoria(client, monkeypatch):
    monkeypatch.setattr(dados, "LIMITE_NOVOS", 1)
    assert criar(client).status_code == 303
    assert criar(client).status_code == 503


def test_gestao_mostra_cartoes_e_tabelas(client):
    resposta = client.get("/gestao")
    assert resposta.status_code == 200
    for texto in (
        "Chamados abertos",
        "Tempo médio de reparo",
        "No prazo",
        "Gap de equidade",
        "Reincidência",
        "Por bairro",
        "Últimas 12 semanas",
        "Jardim D&#39;Abril",
    ):
        assert texto in resposta.text, texto
    assert 'href="/gestao?dias=30"' in resposta.text


def test_gestao_aceita_filtro_de_periodo(client):
    assert client.get("/gestao?dias=30").status_code == 200
    assert client.get("/gestao?dias=abc").status_code == 422


def test_ciclo_completo_cidadao_abre_e_gestao_resolve(client):
    criar(client)
    fila = client.get("/gestao").text
    assert fila.index("#1301") < fila.index("#1300")  # o novo aparece no topo da fila

    acao = "/gestao/chamados/1301/status"
    assert (
        client.post(acao, data={"status": "em andamento"}, follow_redirects=False).status_code
        == 303
    )
    assert dados.obter_chamado(1301)["status"] == "em andamento"

    assert (
        client.post(acao, data={"status": "resolvido"}, follow_redirects=False).status_code == 303
    )
    chamado = dados.obter_chamado(1301)
    assert chamado["status"] == "resolvido"
    assert chamado["resolvido_em"] is not None
    assert "#1301" not in client.get("/gestao").text


def test_gestao_rejeita_transicao_invalida(client):
    criar(client)
    acao = "/gestao/chamados/1301/status"
    assert client.post(acao, data={"status": "resolvido"}).status_code == 409
    assert client.post(acao, data={"status": "aberto"}).status_code == 409
    assert (
        client.post("/gestao/chamados/999/status", data={"status": "resolvido"}).status_code == 404
    )
    assert dados.obter_chamado(1301)["status"] == "aberto"


def test_botoes_da_fila_indicam_a_proxima_acao(client):
    corpo = client.get("/gestao").text
    assert re.search(r'name="status" value="em andamento">\s*<button[^>]*>Iniciar', corpo)
    assert re.search(r'name="status" value="resolvido">\s*<button[^>]*>Resolver', corpo)


def test_transparencia_mostra_prazo_por_bairro_sem_identificar_ninguem(client):
    resposta = client.get("/transparencia")
    assert resposta.status_code == 200
    assert "Por bairro" in resposta.text
    assert "Centro" in resposta.text
    assert "Ana Fictícia" not in resposta.text
    assert "OSC-" not in resposta.text


def test_privacidade_explica_o_que_e_gravado(client):
    resposta = client.get("/privacidade")
    assert resposta.status_code == 200
    assert "LGPD" in resposta.text
    assert "memória" in resposta.text


def test_nenhuma_pagina_usa_javascript_nem_cookie(client):
    rotas = (
        "/",
        "/chamados",
        "/chamados/1297",
        "/chamados/novo",
        "/gestao",
        "/transparencia",
        "/privacidade",
    )
    for rota in rotas:
        resposta = client.get(rota)
        assert resposta.status_code == 200, rota
        assert "<script" not in resposta.text.lower(), rota
        assert "set-cookie" not in resposta.headers, rota
