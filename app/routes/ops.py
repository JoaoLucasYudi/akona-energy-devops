from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.config import Settings, load_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/simular-erro")
def simular_erro(settings: Annotated[Settings, Depends(load_settings)]) -> JSONResponse:
    if not settings.enable_error_simulation:
        raise HTTPException(status_code=404)
    return JSONResponse(status_code=500, content={"detail": "Erro simulado para observabilidade"})
