from datetime import datetime
from pathlib import Path
from typing import Annotated
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app import dados, indicadores, metricas

# Cidadão fictício fixo da demonstração: não há login, cookie nem sessão.
CIDADAO_DEMO_ID = 1
PERIODOS = (30, 90)

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
router = APIRouter(default_response_class=HTMLResponse)


def _data_hora(valor: str | None) -> str:
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M") if valor else "—"


def _numero(valor: float | None, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",") if valor is not None else "—"


templates.env.filters["data_hora"] = _data_hora
templates.env.filters["numero"] = _numero

Dias = Annotated[int, Query(ge=1, le=365)]


async def _formulario(request: Request) -> dict[str, str]:
    """Lê um formulário urlencoded (campos repetidos: fica o primeiro)."""
    corpo = (await request.body()).decode("utf-8", errors="replace")
    return {campo: valores[0] for campo, valores in parse_qs(corpo).items()}


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/chamados")
def meus_chamados(request: Request):
    return templates.TemplateResponse(
        request,
        "chamados.html",
        {
            "cidadao": dados.obter_cidadao(CIDADAO_DEMO_ID),
            "chamados": dados.chamados_do_cidadao(CIDADAO_DEMO_ID),
        },
    )


def _tela_novo(request: Request, valores: dict, erro: str | None = None, status_code: int = 200):
    return templates.TemplateResponse(
        request,
        "novo_chamado.html",
        {
            "tipos": dados.TIPOS,
            "bairros": dados.BAIRROS,
            "ponto_max": dados.PONTO_MAX,
            "valores": valores,
            "erro": erro,
        },
        status_code=status_code,
    )


@router.get("/chamados/novo")
def novo_chamado(request: Request, ponto: Annotated[str, Query(max_length=dados.PONTO_MAX)] = ""):
    return _tela_novo(request, {"ponto": ponto})


@router.post("/chamados/novo")
async def criar_chamado(request: Request):
    valores = await _formulario(request)
    tipo = valores.get("tipo", "")
    bairro = valores.get("bairro", "")
    ponto = valores.get("ponto", "").strip()
    if tipo not in dados.TIPOS or bairro not in dados.BAIRROS:
        return _tela_novo(request, valores, "Escolha o tipo e o bairro da lista.", 422)
    if not ponto or len(ponto) > dados.PONTO_MAX:
        erro = f"Informe o ponto de referência, com até {dados.PONTO_MAX} caracteres."
        return _tela_novo(request, valores, erro, 422)
    try:
        chamado = dados.criar_chamado(CIDADAO_DEMO_ID, tipo, bairro, ponto)
    except dados.LimiteAtingido:
        erro = "A demonstração atingiu o limite de chamados novos. Tente mais tarde."
        return _tela_novo(request, valores, erro, 503)
    metricas.chamados_criados.labels(tipo=tipo).inc()
    return RedirectResponse(f"/chamados/{chamado['id']}?criado=1", status_code=303)


@router.get("/chamados/{chamado_id}")
def detalhe_chamado(request: Request, chamado_id: int, criado: bool = False):
    chamado = dados.obter_chamado(chamado_id)
    if chamado is None or chamado["cidadao_id"] != CIDADAO_DEMO_ID:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return templates.TemplateResponse(
        request, "chamado.html", {"chamado": chamado, "criado": criado}
    )


@router.get("/gestao")
def gestao(request: Request, dias: Dias = 90):
    chamados = dados.listar_chamados()
    fila = sorted(
        (c for c in chamados if c["status"] != "resolvido"),
        key=lambda c: c["aberto_em"],
        reverse=True,
    )
    return templates.TemplateResponse(
        request,
        "gestao.html",
        {
            "painel": indicadores.calcular(chamados, dados.agora(), dias),
            "fila": fila,
            "proximo_status": dados.PROXIMO_STATUS,
            "periodos": PERIODOS,
        },
    )


@router.post("/gestao/chamados/{chamado_id}/status")
async def mudar_status(request: Request, chamado_id: int):
    if dados.obter_chamado(chamado_id) is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    novo_status = (await _formulario(request)).get("status", "")
    chamado = dados.avancar_status(chamado_id, novo_status)
    if chamado is None:
        raise HTTPException(status_code=409, detail="Mudança de status inválida")
    if novo_status == "resolvido":
        metricas.chamados_resolvidos.labels(tipo=chamado["tipo"]).inc()
    return RedirectResponse("/gestao", status_code=303)


@router.get("/transparencia")
def transparencia(request: Request, dias: Dias = 90):
    painel = indicadores.calcular(dados.listar_chamados(), dados.agora(), dias)
    return templates.TemplateResponse(
        request, "transparencia.html", {"painel": painel, "periodos": PERIODOS}
    )


@router.get("/privacidade")
def privacidade(request: Request):
    return templates.TemplateResponse(request, "privacidade.html")
