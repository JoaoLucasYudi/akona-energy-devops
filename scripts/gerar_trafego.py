"""Gera tráfego contra o MVP para alimentar o dashboard e, com --erros, disparar o alerta.

Uso:
    python scripts/gerar_trafego.py --url http://localhost:8000 --minutos 5
    python scripts/gerar_trafego.py --url https://<app_fqdn> --minutos 5 --erros
"""

import argparse
import time
import urllib.error
import urllib.request
from collections import Counter
from urllib.parse import urlparse

ROTAS_NORMAIS = ["/", "/chamados", "/gestao", "/api/chamados", "/api/chamados/101"]
ROTA_ERRO = "/simular-erro"


def chamar(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=10) as resposta:  # noqa: S310 (esquema validado em main)
            return f"{resposta.status // 100}xx"
    except urllib.error.HTTPError as erro:
        return f"{erro.code // 100}xx"
    except (urllib.error.URLError, TimeoutError):
        return "falha"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8000", help="URL base do MVP")
    parser.add_argument("--minutos", type=float, default=5, help="duração em minutos")
    parser.add_argument("--intervalo", type=float, default=0.2, help="pausa entre chamadas (s)")
    parser.add_argument("--erros", action="store_true", help=f"também chama {ROTA_ERRO}")
    args = parser.parse_args()

    if urlparse(args.url).scheme not in ("http", "https"):
        parser.error("--url precisa começar com http:// ou https://")

    rotas = ROTAS_NORMAIS + ([ROTA_ERRO] if args.erros else [])
    base = args.url.rstrip("/")
    fim = time.monotonic() + args.minutos * 60
    contagem: Counter[str] = Counter()

    print(f"Gerando tráfego em {base} por {args.minutos} min (erros: {args.erros}).")
    try:
        while time.monotonic() < fim:
            for rota in rotas:
                contagem[chamar(base + rota)] += 1
                time.sleep(args.intervalo)
            print(f"\r{dict(sorted(contagem.items()))}", end="", flush=True)
    except KeyboardInterrupt:
        pass
    print(f"\nTotal: {dict(sorted(contagem.items()))}")


if __name__ == "__main__":
    main()
