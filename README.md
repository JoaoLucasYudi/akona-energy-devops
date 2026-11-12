# Akona Energy · Deploy Blindado

MVP do Akona Energy publicado com uma esteira DevSecOps, entregue na disciplina Secure DevOps Tools & Cloud Computing (FIAP, GS 2026.2).

## Ficha Técnica do MVP

| Campo | Descrição |
| --- | --- |
| Nome do produto | Akona Energy |
| Cidadão e território | Moradores de Osasco (SP) que dependem de iluminação pública e da rede de distribuição de energia, atendidos pela prefeitura ou pela concessionária local |
| Problema em uma frase | Problemas de iluminação e energia (poste apagado, lâmpada piscando, fio caído, queda de energia) demoram a chegar a quem resolve e não viram dados para priorizar o atendimento |
| Proposta de valor | Um webapp em que cidadãos reportam esses problemas e a gestão (prefeitura ou concessionária) acompanha, prioriza e resolve os chamados com dados. Este MVP é uma demonstração somente leitura dessa proposta |
| Componentes da arquitetura | Aplicação FastAPI + Jinja2 em container, imagem no GitHub Container Registry, Azure Container Apps (eastus2) criado por Terraform, Log Analytics, pipeline GitHub Actions com Gitleaks, Semgrep e Trivy, e Prometheus + Grafana locais. Ver [arquitetura](docs/arquitetura.md) |
| Fontes de dados | Mock sintético versionado no repositório (`app/data/mock.json`), com cidadãos fictícios e chamados de bairros de Osasco |
| Modelos de IA utilizados | Nenhum nesta versão |
| URL do MVP e repositório | MVP: **pendente (E8b)**. Repositório: <https://github.com/JoaoLucasYudi/akona-energy-devops> |
| Indicadores de impacto | Tempo médio de resolução de chamado, percentual de chamados resolvidos no prazo e número de chamados por bairro. São metas do produto, propostas e não medidas, porque os dados do MVP são sintéticos |
| ODS conectados | ODS 7 (energia limpa e acessível) e ODS 11 (cidades e comunidades sustentáveis) |

Autenticação, banco de dados e gravação de chamados fazem parte do produto, mas ficaram fora desta entrega.

## Integrantes

| Nome completo | RM |
| --- | --- |
| João Lucas Yudi Redi Handa | RM98458 |
| Guilherme Dal | RM98694 |
| Guilherme Vargas | RM98278 |
| Ryan Perez Pacheco | RM987872 |
| Lucas Laia | RM97709 |

## Arquitetura

Diagrama e componentes em [docs/arquitetura.md](docs/arquitetura.md). Os outros textos da documentação:

- [Responsabilidade compartilhada](docs/responsabilidade-compartilhada.md)
- [LGPD: onde ficam os dados pessoais](docs/lgpd.md)
- [Estimativa de custo](docs/custo.md)

## Como rodar localmente

Com Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --port 8000
```

Abra <http://localhost:8000>. As rotas operacionais são `/health` e `/metrics`. A rota `/simular-erro` só responde 500 com `ENABLE_ERROR_SIMULATION=true`; sem isso, responde 404.

Para rodar lint e testes:

```bash
ruff check . && ruff format --check . && pytest
```

A preencher (E8b): subir a stack com `docker compose`.

## Como provisionar a infraestrutura

A preencher (E8b).

## Como funciona o pipeline

A preencher (E8b).

## Observabilidade

A preencher (E8b).

## Rollback

A preencher (E8b).

## Como destruir a infraestrutura

A preencher (E8b).

## Relatório em PDF

O relatório fica em `docs/relatorio/relatorio.md`. Para gerar o PDF (precisa do Google Chrome e do pacote `markdown`, que está em `requirements-dev.txt`):

```bash
scripts/gerar_pdf.sh
```

O PDF sai em `docs/relatorio/relatorio.pdf`. Fora do macOS, informe o caminho do Chrome em `CHROME`.
