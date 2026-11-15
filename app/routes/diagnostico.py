import subprocess

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/diagnostico", response_class=PlainTextResponse)
def diagnostico(host: str) -> str:
    comando = f"ping -c 1 {host}"
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)  # noqa: S602
    return resultado.stdout + resultado.stderr
