"""Métricas de negócio expostas em /metrics, ao lado das métricas HTTP."""

from prometheus_client import Counter

from app.dados import TIPOS

chamados_criados = Counter(
    "akona_chamados_criados_total", "Chamados abertos pelo formulário", ["tipo"]
)
chamados_resolvidos = Counter(
    "akona_chamados_resolvidos_total", "Chamados resolvidos pela gestão", ["tipo"]
)

# Cria as séries zeradas, para o Grafana mostrar 0 em vez de "sem dados".
for _tipo in TIPOS:
    chamados_criados.labels(tipo=_tipo)
    chamados_resolvidos.labels(tipo=_tipo)
