# Arquitetura do Akona Energy

MVP publicado: <https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io>

O código só vira imagem no GitHub Container Registry (GHCR) se passar pelos testes e pelos três scanners (Gitleaks, Semgrep e Trivy). O deploy troca a imagem do Container App, que é a única parte exposta ao cidadão, e só por HTTPS.

```mermaid
flowchart LR
  subgraph LOCAL["Máquina da equipe"]
    DEV["Equipe<br/>commits por épico, via PR"]
    TF["Terraform<br/>state local, apply manual"]
    PG["Prometheus + Grafana<br/>docker compose local"]
  end
  subgraph GH["GitHub (repositório público)"]
    R["Repositório<br/>akona-energy-devops"] -->|push| GA["GitHub Actions<br/>qualidade · Gitleaks · Semgrep<br/>build · Trivy · push · deploy"]
    GA -->|"imagem :sha"| GHCR["GHCR<br/>imagem pública"]
  end
  subgraph AZ["Azure · eastus2"]
    CA["Container App (MVP)<br/>FastAPI + Jinja2, porta 8000<br/>1 réplica · 0.25 vCPU · 0.5 GiB<br/>ingress só HTTPS 443, sem SSH"]
    LA["Log Analytics<br/>logs, retenção de 30 dias"]
  end
  C["Cidadão<br/>celular ou navegador"]
  DEV -->|git push| R
  GA -->|"deploy (az containerapp update)"| CA
  GHCR -->|pull| CA
  CA -->|logs| LA
  TF -->|provisiona| AZ
  PG -->|"raspa /metrics (HTTPS)"| CA
  C -->|HTTPS 443| CA
```

## Componentes

| Componente | Onde roda | Papel |
| --- | --- | --- |
| Aplicação MVP | Container App na Azure | FastAPI + Jinja2, sem JavaScript, com dados simulados em `app/data/mock.json` e chamados novos em memória (uma réplica). Expõe as páginas, `/health` e `/metrics` na porta 8000 |
| Repositório | GitHub, público | Código, Dockerfile, workflow, Terraform e documentação |
| GitHub Actions | Runners do GitHub | Pipeline `devsecops.yml`: qualidade (ruff e pytest), Gitleaks, Semgrep, build, Trivy, push no GHCR e deploy |
| GHCR | GitHub | Guarda a imagem `ghcr.io/joaolucasyudi/akona-energy-devops`, marcada pelo SHA do commit |
| Terraform | Máquina da equipe | Cria o resource group, o Log Analytics, o ambiente e o Container App. O state fica local, fora do Git |
| Log Analytics | Azure | Recebe os logs do Container App, com retenção de 30 dias e cota diária de 0,5 GB |
| Prometheus + Grafana | Máquina da equipe | Raspam `/metrics` da URL pública e mostram as 4 métricas de ouro, com uma regra de alerta |

## Por que não existe porta administrativa aberta

Não há VM, NSG nem IP público de máquina. O Container Apps só expõe o ingress HTTPS (443), gerenciado pela Azure. Não existe SSH nem RDP para abrir, e o deploy usa a API da Azure, não acesso à máquina.

## Fluxo de uma mudança

1. A equipe envia um commit para um branch e abre um PR para a `main`.
2. A cada push, o workflow roda qualidade, Gitleaks e Semgrep. Se os três passarem, faz o build da imagem e roda o Trivy.
3. Só na `main`, a imagem aprovada é publicada no GHCR com a tag do SHA, e o job `deploy` atualiza o Container App para essa imagem e confere `/health`.
4. O Prometheus local raspa `/metrics` da URL pública, e o Grafana mostra o dashboard e avalia o alerta.

## Situação dos componentes

Todos os componentes estão no ar desde 15/11/2026.

| Componente | Épico | Situação |
| --- | --- | --- |
| Aplicação MVP | E1 | Publicada na URL acima |
| Dockerfile e docker compose | E2 | Imagem multi-stage, `USER 10001`; stack local com `docker compose` |
| Workflow DevSecOps e push no GHCR | E3 | Roda a cada push; imagem pública no GHCR, marcada pelo SHA |
| Terraform (Container App, Log Analytics) | E4 | Aplicado em eastus2 (resource group `rg-akona-energy-prod`) |
| Deploy contínuo | E5 | Push na `main` troca a imagem do Container App e confere `/health` |
| Prometheus, Grafana e alerta | E6 | Locais, raspando `/metrics` da URL pública; alerta disparado em 16/11 |

O diagrama também está em PNG, para o relatório: [`docs/evidencias/00-arquitetura.png`](evidencias/00-arquitetura.png).
