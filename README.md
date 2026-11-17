# Akona Energy · Deploy Blindado

MVP do Akona Energy publicado com uma esteira DevSecOps, entregue na disciplina Secure DevOps Tools & Cloud Computing (FIAP, GS 2026.2).

## Ficha Técnica do MVP

| Campo | Descrição |
| --- | --- |
| Nome do produto | Akona Energy |
| Cidadão e território | Moradores de Osasco (SP) que dependem de iluminação pública e da rede de distribuição de energia, atendidos pela prefeitura ou pela concessionária local |
| Problema em uma frase | Problemas de iluminação e energia (poste apagado, lâmpada piscando, fio caído, queda de energia) demoram a chegar a quem resolve e não viram dados para priorizar o atendimento |
| Proposta de valor | Um webapp em que cidadãos reportam esses problemas sem cadastro e a gestão (prefeitura ou concessionária) acompanha, prioriza e resolve os chamados com dados. No MVP, o cidadão abre um chamado e recebe o protocolo, a gestão inicia e resolve o chamado, e os indicadores mudam na tela. Modelo de negócio e go-to-market em [negocio.md](docs/negocio.md) |
| Componentes da arquitetura | Aplicação FastAPI + Jinja2 em container, imagem no GitHub Container Registry, Azure Container Apps (eastus2) criado por Terraform, Log Analytics, pipeline GitHub Actions com Gitleaks, Semgrep e Trivy, e Prometheus + Grafana locais. Ver [arquitetura](docs/arquitetura.md) |
| Fontes de dados | Dados simulados: 300 chamados dos últimos 90 dias em 12 bairros de Osasco, gerados por `scripts/gerar_mock.py` com seed fixa e versionados em `app/data/mock.json`. O cenário faz bairros periféricos demorarem mais no reparo. Chamados novos ficam só na memória do processo (uma réplica) e se perdem quando o container reinicia |
| Modelos de IA utilizados | Nenhum nesta versão |
| URL do MVP e repositório | MVP: <https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io>. Repositório: <https://github.com/JoaoLucasYudi/akona-energy-devops> |
| Indicadores de impacto | Tempo médio de reparo, % de chamados no prazo, gap de equidade (bairro mais lento ÷ cidade) e reincidência no mesmo poste em 30 dias, calculados em `app/indicadores.py` e mostrados em `/gestao`, `/transparencia` e `/api/indicadores`. Hoje são medidos sobre dados simulados; as metas do piloto estão em [negocio.md](docs/negocio.md) |
| ODS conectados | ODS 11 (cidades e comunidades sustentáveis), ODS 10 (redução das desigualdades) e ODS 7 (energia limpa e acessível) |

Autenticação e banco de dados fazem parte do produto, mas ficaram fora desta entrega. Por isso a troca de status em `/gestao` não pede login (em produção seria um perfil autenticado) e os chamados novos não sobrevivem a um reinício do container.

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

### Com Docker

Com Docker e o plugin `docker compose`:

```bash
cp .env.example .env   # troque os valores "trocar-me"
docker compose up -d --build
docker compose ps      # o serviço app deve aparecer como "healthy"
```

O app sobe em <http://localhost:8000>, com o mesmo container da produção: imagem multi-stage, usuário `10001`, sistema de arquivos somente leitura e sem capabilities. Para parar: `docker compose down`.

## Como provisionar a infraestrutura

A infraestrutura fica em `infra/terraform` (provider `azurerm ~> 4.0`) e cria, em eastus2, o resource group, o Log Analytics, o ambiente do Container Apps (perfil Consumption) e o Container App, com 1 réplica, 0.25 vCPU, 0.5 GiB e ingress só HTTPS. Não há VM, NSG nem porta administrativa.

Pré-requisitos: Terraform, Azure CLI e uma assinatura da Azure.

```bash
az login
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # troque "trocar-me" pelo ID da assinatura
terraform init
terraform plan
terraform apply
terraform output app_url
```

O state fica local, fora do Git, assim como o `terraform.tfvars` (ver `.gitignore`). Depois do primeiro apply, quem troca a imagem do container é o pipeline: o Terraform ignora mudanças na imagem (`ignore_changes`).

Para o deploy contínuo funcionar, o repositório precisa de:

- **Secret** `AZURE_CREDENTIALS`: JSON de um service principal com papel Contributor só no resource group do projeto.
- **Variables** `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINERAPP_NAME` e `APP_FQDN`, com os valores dos outputs do Terraform.

## Como funciona o pipeline

O workflow `.github/workflows/devsecops.yml` roda a cada push, em qualquer branch, e também pode ser disparado à mão (`workflow_dispatch`).

| Job | O que faz | Quando barra |
| --- | --- | --- |
| `qualidade` | `ruff check`, `ruff format --check` e `pytest` | Erro de lint, formatação ou teste |
| `gitleaks` | Procura segredos em todo o histórico do Git | Qualquer segredo encontrado |
| `semgrep` | Análise estática com as regras `p/python`, `p/secrets` e `p/dockerfile` | Qualquer achado bloqueante |
| `build-scan-push` | Build da imagem e Trivy; na `main`, push para o GHCR com as tags do SHA e `latest` | CVE HIGH ou CRITICAL com correção disponível |
| `deploy` | Só na `main`: troca a imagem do Container App pela do SHA e testa `/health` por até 3 minutos | `/health` não responde 200 |

Os três primeiros jobs rodam em paralelo, e o build só começa se todos passarem. Fora da `main`, o pipeline valida tudo, mas não publica a imagem nem faz deploy. A única credencial é `AZURE_CREDENTIALS`, em GitHub Secrets; o push no GHCR usa o `GITHUB_TOKEN` da própria execução.

O branch `demo/barrado-semgrep` guarda a demonstração de uma execução barrada pelo Semgrep (injeção de comando com `shell=True`) e da execução corrigida. Ele nunca é mergeado.

## Observabilidade

Prometheus e Grafana rodam na máquina da equipe, pelo docker compose (profile `observability`), e raspam o `/metrics` tanto do app local quanto da URL pública da produção:

```bash
cp .env.example .env   # defina GF_SECURITY_ADMIN_PASSWORD
docker compose --profile observability up -d --build
```

- Grafana: <http://127.0.0.1:3000>, dashboard "Golden Signals — Akona Energy", com latência, tráfego, erros e saturação. A variável "Ambiente" escolhe entre `mvp-local` e `mvp-prod`.
- Prometheus: <http://127.0.0.1:9090/targets>.
- Alerta "Taxa de erro alta" (regra do Grafana): dispara quando mais de 5% das respostas são 5xx por 1 minuto.

Para provocar o alerta, ligue a rota `/simular-erro` (`ENABLE_ERROR_SIMULATION=true`; na produção, `terraform apply -var enable_error_simulation=true`) e gere tráfego com erros:

```bash
python scripts/gerar_trafego.py --url <URL> --minutos 5 --erros
```

Detalhes em [observability/README.md](observability/README.md).

## Rollback

O rollback é manual, para um SHA que já passou pelo pipeline. Há dois caminhos:

1. **Pelo GitHub Actions:** na aba Actions, abra a execução do workflow `devsecops` do commit anterior na `main` e use **Re-run all jobs**. O job `deploy` reimplanta a imagem daquele SHA.
2. **Pelo Azure CLI:**

   ```bash
   az containerapp update --name ca-akona-energy-prod --resource-group rg-akona-energy-prod \
     --image ghcr.io/joaolucasyudi/akona-energy-devops:<sha-anterior>
   ```

O próximo push na `main` volta a implantar o código mais recente. Para um rollback que dure, reverta o commit com `git revert` e abra um PR.

## Como destruir a infraestrutura

```bash
cd infra/terraform
terraform destroy
```

Depois, apague o service principal do pipeline (`az ad sp delete --id <appId>`) e confira no Cost Management que não sobrou nenhum recurso cobrando. A limpeza desta entrega está marcada para 01/12/2026, depois da correção.

## Relatório em PDF

O relatório fica em `docs/relatorio/relatorio.md`. Para gerar o PDF (precisa do Google Chrome e do pacote `markdown`, que está em `requirements-dev.txt`):

```bash
scripts/gerar_pdf.sh
```

O PDF sai em `docs/relatorio/relatorio.pdf`. Os prints de evidência ficam fora do Git; o script os procura em `~/Documents/prints-gs-devops-4nao/`, ou na pasta informada em `PRINTS`. Fora do macOS, informe o caminho do Chrome em `CHROME`.

O diagrama de arquitetura entra no PDF como `docs/evidencias/00-arquitetura.png`, exportado do Mermaid de `docs/arquitetura.md` com o [mermaid-cli](https://github.com/mermaid-js/mermaid-cli).

## Créditos de imagens, fonte e ícones

O site não carrega nenhum recurso externo: fotos, fonte e ícones ficam em `app/static/` ou no próprio HTML.

| Arquivo em `app/static/img/` | Onde aparece | Autor | Foto original | Licença |
| --- | --- | --- | --- | --- |
| `hero-rua-iluminada.webp` | Topo da página inicial (espelhada no CSS) | Fawazlul Rizqi | <https://unsplash.com/photos/8I-gdwRMw_M> | [Unsplash License](https://unsplash.com/license) |
| `rua-lampioes.webp` | Cartão "Cidadão" | Zoltan Tasi | <https://unsplash.com/photos/MzVIlXk0AJg> | [Unsplash License](https://unsplash.com/license) |
| `tecnicos-cesto.webp` | Cartão "Gestor" | Mario Spencer | <https://unsplash.com/photos/UyqxlMS8X84> | [Unsplash License](https://unsplash.com/license) |
| `poste-led.webp` | Cartão "Fiscalização e transparência" | Sara Mobasheri | <https://unsplash.com/photos/XaOJLeMGgvM> | [Unsplash License](https://unsplash.com/license) |
| `sao-paulo-noite.webp` | Faixa "Leve o Akona para a sua cidade" | Daniel Esteves | <https://unsplash.com/photos/u2rwF2C3wgo> | [Unsplash License](https://unsplash.com/license) |

As fotos foram recortadas, redimensionadas e convertidas para WebP.

- **Fonte:** [Plus Jakarta Sans](https://github.com/tokotype/PlusJakartaSans), © 2020 The Plus Jakarta Sans Project Authors, sob a SIL Open Font License 1.1 (texto em `app/static/fonts/OFL.txt`). O arquivo `woff2` (subconjunto latino, peso variável) vem do pacote [`@fontsource-variable/plus-jakarta-sans`](https://fontsource.org/fonts/plus-jakarta-sans) 5.2.8.
- **Ícones:** [Lucide](https://lucide.dev) 0.460.0, licença ISC (© Lucide Contributors; partes © Cole Bemis, do Feather, licença MIT), copiados como SVG inline em `app/templates/_icones.html`.
- **Logo:** desenho próprio em SVG, no mesmo arquivo.
