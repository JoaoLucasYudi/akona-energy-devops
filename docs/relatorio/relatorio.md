# Akona Energy · Deploy Blindado

GS 2026.2 · Secure DevOps Tools & Cloud Computing · FIAP

O Akona Energy é um webapp em que moradores de Osasco (SP) reportam problemas de iluminação pública e de energia, e a gestão (prefeitura ou concessionária) acompanha, prioriza e resolve os chamados com dados. Esta entrega publica o MVP do produto na Azure, com uma esteira DevSecOps completa: container enxuto e sem root, infraestrutura em Terraform, pipeline com três scanners de segurança, deploy automático e observabilidade com alerta.

| Nome completo | RM |
| --- | --- |
| João Lucas Yudi Redi Handa | RM98458 |
| Guilherme Dal | RM98694 |
| Guilherme Vargas | RM98278 |
| Ryan Perez Pacheco | RM987872 |
| Lucas Laia | RM97709 |

## Links

| Item | Link |
| --- | --- |
| URL do MVP | <https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io> |
| Repositório | <https://github.com/JoaoLucasYudi/akona-energy-devops> |
| README com a Ficha Técnica do MVP | <https://github.com/JoaoLucasYudi/akona-energy-devops#readme> |
| Imagem no GHCR | <https://github.com/JoaoLucasYudi/akona-energy-devops/pkgs/container/akona-energy-devops> |
| Workflow DevSecOps | <https://github.com/JoaoLucasYudi/akona-energy-devops/blob/main/.github/workflows/devsecops.yml> |
| Execução com deploy na `main` | <https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43770107360> |
| Execução barrada pelo Semgrep | <https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43773324239> |
| Execução corrigida | <https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43773523765> |
| Terraform | <https://github.com/JoaoLucasYudi/akona-energy-devops/tree/main/infra/terraform> |

## Arquitetura

O código só vira imagem no GitHub Container Registry (GHCR) se passar pelos testes e pelos três scanners (Gitleaks, Semgrep e Trivy). O deploy troca a imagem do Container App, a única parte exposta ao cidadão, e só por HTTPS. Terraform, Prometheus e Grafana rodam na máquina da equipe.

![Diagrama de arquitetura](evidencias/00-arquitetura.png)

*Diagrama de arquitetura. Fonte em Mermaid: [docs/arquitetura.md](https://github.com/JoaoLucasYudi/akona-energy-devops/blob/main/docs/arquitetura.md).*

| Componente | Onde roda | Papel |
| --- | --- | --- |
| Aplicação MVP | Azure Container Apps, eastus2 | FastAPI + Jinja2, sem JavaScript, com dados sintéticos. Expõe as páginas, `/health` e `/metrics` na porta 8000 |
| GitHub Actions | Runners do GitHub | Qualidade, Gitleaks, Semgrep, build, Trivy, push no GHCR e deploy |
| GHCR | GitHub | Imagem pública `ghcr.io/joaolucasyudi/akona-energy-devops`, marcada pelo SHA do commit |
| Terraform | Máquina da equipe | Cria resource group, Log Analytics, ambiente e Container App. State local, fora do Git |
| Log Analytics | Azure, eastus2 | Logs do Container App, retenção de 30 dias e cota diária de 0,5 GB |
| Prometheus + Grafana | Máquina da equipe | Raspam `/metrics` da URL pública, mostram as 4 métricas de ouro e avaliam o alerta |

## Container

O `Dockerfile` usa dois estágios sobre `python:3.12-slim`: o primeiro instala as dependências num venv; o segundo copia só o venv e o código, atualiza os pacotes do sistema e roda como o usuário `10001`, sem shell de login. Nenhum segredo entra na imagem: não há `ARG` ou `ENV` com credencial, e a configuração vem só de variáveis de ambiente.

![Dockerfile](prints/01-dockerfile.png)

*01 · Dockerfile multi-stage, com `USER 10001` e healthcheck em `/health`.*

![docker compose up e docker ps](prints/02-compose-ps.png)

*02 · `docker compose up -d --build` e `docker ps`: o serviço `app` sobe e fica `healthy`. No compose, o container roda com sistema de arquivos somente leitura, sem capabilities e com `no-new-privileges`.*

![id -u na imagem de produção](prints/03-id-u.png)

*03 · `id -u` na imagem de produção do GHCR (amd64) retorna `10001`: o container não roda como root.*

![docker images](prints/04-docker-images.png)

*04 · Imagem de produção com 53,6 MB de conteúdo (223 MB descompactada em disco).*

## IaC e porta administrativa

Toda a nuvem é criada pelo Terraform (`azurerm ~> 4.0`) em `infra/terraform`: resource group, Log Analytics, ambiente do Container Apps e Container App. O state e o `terraform.tfvars` ficam fora do repositório; no Git só existe o `terraform.tfvars.example`, com o valor `trocar-me`.

**Não existe porta administrativa aberta.** A arquitetura não tem VM, NSG nem IP público de máquina, então não há SSH nem RDP para abrir para `0.0.0.0/0`. O único ponto de entrada é o ingress HTTPS gerenciado pela Azure, na porta 443, com conexões inseguras desligadas (`allow_insecure_connections = false`). O deploy usa a API da Azure, não acesso à máquina.

![terraform output](prints/05-terraform-apply.png)

*05 · Outputs do Terraform depois do `apply`: FQDN, URL, nome do Container App e do resource group.*

![.gitignore](prints/06-gitignore.png)

*06 · `.gitignore` com `*.tfstate` e `*.tfvars`, e `git check-ignore` confirmando que os dois arquivos reais ficam fora do Git.*

![Resource group no portal](prints/07-resource-group.png)

*07 · Resource group `rg-akona-energy-prod` com os três recursos, todos em East US 2. Não há VM, disco, IP público nem NSG.*

![Ingress do Container App](prints/08-ingress.png)

*08 · Ingress do Container App: HTTP na porta de destino 8000, conexões inseguras desligadas e endpoint só em HTTPS. Não há portas TCP adicionais.*

## Pipeline e execução barrada

O workflow `devsecops.yml` roda a cada push, em qualquer branch. `qualidade` (ruff e pytest), `gitleaks` e `semgrep` rodam em paralelo; o build só começa se os três passarem. O Trivy barra a imagem se houver CVE HIGH ou CRITICAL com correção disponível. Só na `main` a imagem é publicada no GHCR e o job `deploy` troca a imagem do Container App e testa `/health`. A única credencial é `AZURE_CREDENTIALS`, em GitHub Secrets; actions de terceiros (Gitleaks e Trivy) são fixadas por SHA do commit.

![Pipeline verde com deploy](prints/10-pipeline-deploy.png)

*10 · Execução #8 na `main`, commit `554c3b1`: todos os jobs verdes, incluindo o `deploy`. [Abrir a execução](https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43770107360).*

![Secrets do repositório](prints/11a-secrets.png)

*11a · Secrets do repositório: só `AZURE_CREDENTIALS`, com o valor protegido pelo GitHub.*

![Variables do repositório](prints/11b-variables.png)

*11b · Variables do repositório: nomes do resource group, do Container App e o FQDN. Nenhum valor sensível.*

![Pacote no GHCR](prints/12-ghcr-tags.png)

*12 · Pacote público no GHCR com as tags por SHA. A tag `latest` aponta para `554c3b1…`, o mesmo commit da execução 10.*

### Execução barrada e execução corrigida

Para provar que o pipeline barra código inseguro antes do deploy, o branch `demo/barrado-semgrep` (que nunca é mergeado) recebeu uma rota `/diagnostico` que executa `ping` com o host informado pelo usuário, via `subprocess.run(..., shell=True)`: uma injeção de comando.

![Execução barrada: grafo](prints/13a-semgrep-barrado-grafo.png)

*13a · Execução #9, branch `demo/barrado-semgrep`, commit `7f41565`: só o `semgrep` falha, e `build-scan-push` e `deploy` nem rodam. [Abrir a execução](https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43773324239).*

![Execução barrada: log](prints/13b-semgrep-barrado-log.png)

*13b · Log do `semgrep` na mesma execução (`demo/barrado-semgrep`, `7f41565`): a regra `subprocess-shell-true` (Blocking) aponta a linha 12 de `app/routes/diagnostico.py`.*

![Execução corrigida](prints/14-semgrep-corrigido.png)

*14 · Execução #11, branch `demo/barrado-semgrep`, commit `1b235ff`, que remove a rota: todos os jobs passam. O `deploy` é pulado porque o branch não é a `main`. [Abrir a execução](https://github.com/JoaoLucasYudi/akona-energy-devops/actions/runs/43773523765).*

## Deploy

Um push na `main` vai para produção sem intervenção: o pipeline publica a imagem e o job `deploy` executa `az containerapp update` com a imagem do SHA, depois testa `/health` por até 3 minutos.

![Home do MVP](prints/15a-home.png)

*15a · Home do MVP na URL pública, por HTTPS.*

![Área do cidadão](prints/15b-cidadao.png)

*15b · Área do cidadão (`/chamados`), com os chamados de uma moradora fictícia.*

![Painel da gestão](prints/15c-gestao.png)

*15c · Painel da gestão (`/gestao`), com as contagens por status, tipo e bairro.*

![Revisão ativa](prints/16-revisao-ativa.png)

*16 · Container ativo no portal, com a imagem `ghcr.io/joaolucasyudi/akona-energy-devops:554c3b1…` publicada pelo pipeline, 0,25 vCPU e 0,5 Gi.*

## Observabilidade

Prometheus e Grafana rodam na máquina da equipe, pelo docker compose, e raspam o `/metrics` da URL pública por HTTPS. O dashboard "Golden Signals" mostra as 4 métricas de ouro: latência (p50 e p95), tráfego (req/s), erros (% de respostas 5xx) e saturação (CPU, memória e requisições em andamento). A regra "Taxa de erro alta", provisionada no Grafana, dispara quando mais de 5% das respostas são 5xx por 1 minuto.

Para o disparo real, em 16/11, a rota `/simular-erro` foi ligada na produção pelo Terraform (`enable_error_simulation = true`), o script `scripts/gerar_trafego.py --erros` gerou tráfego contra a URL pública, e a rota foi desligada em seguida (voltou a responder 404).

![Targets do Prometheus](prints/17-prometheus-targets.png)

*17 · Prometheus com o alvo `mvp-prod` UP: `https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io/metrics`. O alvo `mvp-local` aparece DOWN porque o app local não estava rodando.*

![Dashboard com dados de produção](prints/18-dashboard-prod.png)

*18 · Dashboard com "Ambiente" = `mvp-prod`, ou seja, o alvo de produção do print 17. Os quatro painéis mostram o teste de 16/11: tráfego por volta de 1,2 req/s, erros perto de 18% e latência p95 perto de 95 ms.*

![Painel de erros](prints/18-extra-painel-erros.png)

*Painel de erros ampliado: a taxa de 5xx chega a 16,1% às 17:24, acima da linha de limite de 5%.*

![Alerta em Firing](prints/19-alerta-firing.png)

*19 · Alerta "Taxa de erro alta" em Firing, com a instância `job=mvp-prod` em Alerting desde 17:24:30.*

## Responsabilidade compartilhada

O Container Apps é um PaaS de containers: a Azure cuida de tudo abaixo do container, e a equipe responde pelo que vai dentro dele e por como ele é exposto.

| Camada | Azure | Equipe |
| --- | --- | --- |
| Datacenter, rede física, hosts e sistema operacional dos nós | ✔ | |
| Orquestração do Container Apps (agendamento, reinício, réplicas, revisões) | ✔ | |
| Certificado e terminação TLS do ingress | ✔ | |
| Configuração do ingress (externo, só HTTPS, porta 8000) | | ✔ |
| Imagem do container, dependências e correção de CVEs | | ✔ |
| Código da aplicação | | ✔ |
| Segredos e escopo do service principal (Contributor só no resource group) | | ✔ |
| Dados e LGPD | | ✔ |
| Monitoramento, custo e limpeza dos recursos | | ✔ |

Cada responsabilidade da equipe tem um controle: Trivy e `USER 10001` na imagem, versões fixas nas dependências, ruff, pytest e Semgrep no código, Gitleaks e GitHub Secrets para segredos, ingress só HTTPS, dados sintéticos e o dashboard com alerta. Documento completo: [docs/responsabilidade-compartilhada.md](https://github.com/JoaoLucasYudi/akona-energy-devops/blob/main/docs/responsabilidade-compartilhada.md).

## LGPD

O MVP não coleta nem armazena dados pessoais. Os cidadãos e chamados vêm de um mock sintético versionado, com nomes claramente fictícios e sem CPF, e-mail, telefone ou endereço exato. Não há banco, cadastro, login, cookie nem sessão, e o formulário de novo chamado não grava nada.

| Dado | Onde fica | Retenção | Dado pessoal? |
| --- | --- | --- | --- |
| Métricas em `/metrics` | Memória do container e Prometheus local | Enquanto estiverem de pé | Não: só contadores técnicos |
| Logs do Container App | Log Analytics, eastus2 (EUA) | 30 dias | Potencialmente: o IP do cliente |
| Imagem do container | GHCR | Até ser apagada | Não |

Uma versão real, com cidadãos autenticados, exigiria base legal e finalidade definidas, canal para os direitos do titular e um encarregado (DPO). Como eastus2 fica nos Estados Unidos, guardar dados pessoais ali exigiria enquadrar a transferência internacional no art. 33 da LGPD ou migrar para a região brazilsouth. Documento completo: [docs/lgpd.md](https://github.com/JoaoLucasYudi/akona-energy-devops/blob/main/docs/lgpd.md).

![Página de privacidade](prints/15d-privacidade.png)

*Página `/privacidade` do MVP, que explica ao visitante que nenhum dado pessoal é coletado.*

## Custo

A estimativa usa os preços públicos de varejo da Azure para eastus2, consultados em 16/11/2026 na [Azure Retail Prices API](https://prices.azure.com/api/retail/prices). A infraestrutura fica no ar de 14/11 a 01/12/2026. A réplica nunca escala a zero, então é cobrada o tempo todo; o valor de referência considera a réplica sempre em uso ativo, o cenário mais caro para ela.

| Item | Custo mensal (US$) | Custo de 14/11 a 01/12 (US$) |
| --- | --- | --- |
| Container Apps · vCPU (0,25) | 11,23 | 4,49 |
| Container Apps · memória (0,5 GiB) | 2,81 | 1,12 |
| Container Apps · requisições | 0,00 | 0,00 |
| Log Analytics (dentro da franquia de 5 GB/mês) | 0,00 | 0,00 |
| GHCR e GitHub Actions (repositório público) | 0,00 | 0,00 |
| **Total de referência** | **14,04** | **5,62** |

A faixa possível vai de US$4,21 por mês (réplica ociosa quase o tempo todo) a US$41,64 por mês (réplica sempre ativa e logs batendo a cota diária de 0,5 GB). A assinatura é a Azure for Students: o gasto sai do crédito e não há cobrança em cartão, por isso não foi configurado budget. O controle é o acompanhamento do crédito, a réplica única com recursos mínimos, a cota diária de logs e o `terraform destroy` em 01/12. Conta completa: [docs/custo.md](https://github.com/JoaoLucasYudi/akona-energy-devops/blob/main/docs/custo.md).

## Conclusão técnica

A entrega cobre a esteira inteira: um container enxuto e sem root, a nuvem criada só por Terraform e sem porta administrativa, um pipeline que barra segredo, código inseguro e imagem vulnerável antes do deploy, deploy automático a cada push na `main` e observabilidade com um alerta disparado de verdade contra a produção.

Alguns pontos exigiram ajuste durante o caminho:

- **Nome da imagem em minúsculas:** o usuário do GitHub tem maiúsculas, e o Docker rejeita referências assim. O workflow e o Terraform usam o nome literal `ghcr.io/joaolucasyudi/akona-energy-devops`, e uma validação no Terraform recusa maiúsculas.
- **Drift do Terraform:** a Azure cria o ambiente com o perfil de workload Consumption, e o primeiro `plan` depois do apply queria removê-lo. O perfil passou a ser declarado no código. O Terraform também ignora mudanças na imagem, porque quem troca a imagem é o pipeline.
- **Execução barrada isolada:** a rota insegura da demonstração também era acusada pelo Ruff. Para a execução vermelha mostrar só o Semgrep, a linha recebeu `# noqa: S602`, e o commit nunca chegou à `main`.

Limitações conscientes desta versão: o state do Terraform é local (um time maior usaria um backend remoto com lock), há uma única réplica sem alta disponibilidade, Prometheus e Grafana rodam na máquina da equipe e não na nuvem, e o MVP é somente leitura. Os próximos passos naturais são autenticação, banco de dados com os chamados reais, migração para brazilsouth por causa da LGPD e observabilidade gerenciada na própria Azure.
