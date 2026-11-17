import pytest
from fastapi.testclient import TestClient

from app import dados
from app.main import app


@pytest.fixture(autouse=True)
def dados_do_mock():
    dados.reiniciar()
    yield
    dados.reiniciar()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("ENABLE_ERROR_SIMULATION", raising=False)
    return TestClient(app)


@pytest.fixture
def client_com_simulacao(monkeypatch):
    monkeypatch.setenv("ENABLE_ERROR_SIMULATION", "true")
    return TestClient(app)
