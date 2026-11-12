import sys

import pytest


def test_health_retorna_ok(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_metrics_expoe_formato_prometheus_com_metricas_http(client):
    client.get("/simular-erro")
    resposta = client.get("/metrics")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/plain")
    corpo = resposta.text
    assert 'http_requests_total{handler="/simular-erro",method="GET",status="4xx"}' in corpo
    assert "# TYPE http_request_duration_seconds histogram" in corpo
    assert "http_requests_inprogress" in corpo


def test_metrics_nao_instrumenta_health_nem_metrics(client):
    client.get("/health")
    client.get("/metrics")
    corpo = client.get("/metrics").text
    assert 'handler="/health"' not in corpo
    assert 'handler="/metrics"' not in corpo


@pytest.mark.skipif(sys.platform != "linux", reason="métricas de processo só existem no Linux")
def test_metrics_inclui_metricas_de_processo(client):
    corpo = client.get("/metrics").text
    assert "process_cpu_seconds_total" in corpo
    assert "process_resident_memory_bytes" in corpo


def test_simular_erro_com_flag_desligada_retorna_404(client):
    assert client.get("/simular-erro").status_code == 404


def test_simular_erro_com_flag_ligada_retorna_500(client_com_simulacao):
    assert client_com_simulacao.get("/simular-erro").status_code == 500
