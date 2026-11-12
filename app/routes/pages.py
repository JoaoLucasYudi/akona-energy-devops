from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import dados

# Cidadão fictício fixo da demonstração: não há login, cookie nem sessão.
CIDADAO_DEMO_ID = 1

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
router = APIRouter(default_response_class=HTMLResponse)


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


@router.get("/chamados/novo")
def novo_chamado(request: Request):
    return templates.TemplateResponse(request, "novo_chamado.html", {"tipos": dados.TIPOS})


@router.get("/chamados/{chamado_id}")
def detalhe_chamado(request: Request, chamado_id: int):
    chamado = dados.obter_chamado(chamado_id)
    if chamado is None or chamado["cidadao_id"] != CIDADAO_DEMO_ID:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return templates.TemplateResponse(request, "chamado.html", {"chamado": chamado})


@router.get("/gestao")
def gestao(request: Request):
    return templates.TemplateResponse(
        request,
        "gestao.html",
        {
            "chamados": dados.listar_chamados(),
            "contagens": [
                ("Por status", dados.contar_por("status")),
                ("Por tipo", dados.contar_por("tipo")),
                ("Por bairro", dados.contar_por("bairro")),
            ],
        },
    )


@router.get("/privacidade")
def privacidade(request: Request):
    return templates.TemplateResponse(request, "privacidade.html")
