# GS 2026.2 · Secure DevOps — Deploy Blindado

Entrega da disciplina Secure DevOps Tools & Cloud Computing (FIAP), prazo 19/11/2026 23h55. O plano completo está em `docs/plano-devops.md`. As specs por épico vivem no Linear (uma issue por épico, projeto `gs-devops`).

## Decisões fixas (não mudar sem pedir)

- App: Python 3.12 + FastAPI + Jinja2, sem JavaScript, dados mockados em `app/data/mock.json`, sem banco, sem autenticação e sem formulário que grava.
- Contrato da plataforma: porta 8000; `/health` (200); `/metrics` (Prometheus, sem auth); `/simular-erro` atrás de `ENABLE_ERROR_SIMULATION`.
- Container: multi-stage `python:3.12-slim`, `USER 10001`, nenhum segredo na imagem.
- Nuvem: Azure, eastus2, Container Apps consumption, 1 réplica (min = max = 1). Sem VM, sem SSH.
- Registry: GHCR público, nome da imagem sempre em minúsculas (`ghcr.io/joaolucasyudi/akona-energy-devops`). IaC: Terraform azurerm ~> 4.0, state local (fora do Git), `ignore_changes` na imagem.
- CI: `.github/workflows/devsecops.yml` com qualidade, Gitleaks, Semgrep, build + Trivy, push e deploy. Gatilhos: `push` (todos os branches) e `workflow_dispatch`, sem `pull_request`.
- Observabilidade: Prometheus + Grafana locais (profile `observability`), uma regra de alerta.

## Convenções

- Dependências com versão fixa (`==`). `ruff check`, `ruff format --check` e `pytest` passam antes de PR.
- Config só por variáveis de ambiente, em `app/config.py`. Exemplos em `.env.example` e `terraform.tfvars.example` com `trocar-me`.
- Produto: Akona Energy. Repositório: `akona-energy-devops`. Integrantes e descrição do produto em "Definições do produto e da equipe" no plano. Se faltar um valor, pergunte; nunca invente.
- Um branch por épico (`epic/e<n>-<nome>`), PR para `main`, Conventional Commits. `demo/barrado-semgrep` nunca é mergeado.
- Textos de interface e docs em português do Brasil.
- Actions oficiais (`actions/*`, `docker/*`, `azure/*`) por tag de versão maior (ex.: `actions/checkout@v4`), conferida no repositório da action. Actions de terceiros (Trivy, Gitleaks) por SHA completo do commit, com a versão em comentário.

## Limites

- Nunca leia nem escreva `.env`, `*.tfvars` ou `*.tfstate*`. Nunca imprima segredos.
- `terraform apply`, `gh secret set`, criação de service principal, `git commit`, `git push` e merge pedem aprovação.
- `terraform destroy` e apagar resource group ficam fora do alcance dos agentes (limpeza manual em 01/12).
- Ao chegar numa tarefa humana do plano (H1–H8), pare e peça.

## Ambiente

- Mac M1: `docker build` local gera imagem arm64, ok para testes. A imagem de produção é sempre a do CI (amd64). Nunca dê push de imagem local.
- Credenciais vêm de `az login` e `gh auth login` da conta pessoal. Confira com `az account show` e `gh auth status` antes de qualquer comando na nuvem.

## Agent skills

### Issue tracker

Issues vivem no Linear (time `JOA`, projeto `gs-devops`), via MCP `linear-server`. See `docs/agents/issue-tracker.md`.

### Triage labels

Cinco labels canônicos, nomes padrão (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (`GLOSSARY.md` + `docs/adr/` na raiz). See `docs/agents/domain.md`.
