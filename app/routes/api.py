from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app import dados, indicadores

router = APIRouter(prefix="/api")


@router.get("/chamados")
def listar_chamados() -> list[dict]:
    return dados.listar_chamados()


@router.get("/chamados/{chamado_id}")
def detalhar_chamado(chamado_id: int) -> dict:
    chamado = dados.obter_chamado(chamado_id)
    if chamado is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado


@router.get("/indicadores")
def calcular_indicadores(dias: Annotated[int, Query(ge=1, le=365)] = 90) -> dict:
    return indicadores.calcular(dados.listar_chamados(), dados.agora(), dias)
