from fastapi import APIRouter, HTTPException

from app import dados

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
