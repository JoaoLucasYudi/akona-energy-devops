# Responsabilidade compartilhada

O Akona Energy roda no Azure Container Apps, um PaaS de containers. A Azure cuida de tudo abaixo do container: datacenter, rede, hosts e orquestração. A equipe responde pelo que vai dentro do container e pela forma como ele é configurado e exposto.

| Camada | Azure | Equipe |
| --- | --- | --- |
| Datacenter e segurança física | ✔ | |
| Rede física e proteção da infraestrutura de rede | ✔ | |
| Hosts, hipervisor e sistema operacional dos nós | ✔ | |
| Orquestração do Container Apps (agendamento, reinício, réplicas, revisões) | ✔ | |
| Certificado e terminação TLS do ingress | ✔ | |
| Configuração do ingress (externo, só HTTPS, porta de destino 8000) | | ✔ |
| Imagem do container (base, pacotes do sistema, usuário não root) | | ✔ |
| Dependências Python e correção de CVEs | | ✔ |
| Código da aplicação | | ✔ |
| Segredos (GitHub Secrets, nada na imagem nem no repositório) | | ✔ |
| Escopo do service principal (Contributor só no resource group) | | ✔ |
| Dados e conformidade com a LGPD | | ✔ |
| Monitoramento da aplicação (métricas, dashboard, alerta) | | ✔ |
| Custo e limpeza dos recursos | | ✔ |

## Como a equipe cumpre a sua parte

Os controles abaixo são os definidos no plano. A coluna "Épico" indica onde cada um é construído; em 11/11/2026, só os do E1 estavam prontos.

| Responsabilidade | Controle | Épico |
| --- | --- | --- |
| Imagem | Dockerfile multi-stage em `python:3.12-slim`, `USER 10001`, sem segredo em `ARG` ou `ENV`. O Trivy barra CVE HIGH ou CRITICAL com correção disponível | E2, E3 |
| Dependências | Versões fixas (`==`) em `requirements.txt` e `requirements-dev.txt` | E1 |
| Código | `ruff` e `pytest` a cada push; o Semgrep barra padrões inseguros | E3 |
| Segredos | Gitleaks a cada push. A única credencial do pipeline é `AZURE_CREDENTIALS`, em GitHub Secrets. `.env`, `*.tfvars` e `*.tfstate` ficam fora do Git | E3, E5 |
| Service principal | Papel Contributor restrito ao resource group do projeto, não à assinatura | E5 (H5) |
| Ingress | `allow_insecure_connections = false` e nenhuma porta além da 443. Não há VM nem SSH | E4 |
| Dados | Só dados sintéticos; ver [LGPD](lgpd.md) | E1 |
| Monitoramento | Prometheus e Grafana locais com as 4 métricas de ouro e o alerta "Taxa de erro alta" | E6 |
| Custo | Budget de US$10 e `terraform destroy` após a correção; ver [Custo](custo.md) | H4, E9 |

O GitHub tem um papel parecido com o da Azure para os runners do Actions e o GHCR: cuida da infraestrutura deles. A equipe responde pelo conteúdo do workflow, pelas permissões de cada job, pela fixação das actions de terceiros por SHA e por manter o pacote do GHCR público.

**Pendente (E8b):** os controles de imagem, pipeline, service principal, ingress, monitoramento e budget dependem do E2 ao E6. Confirmar cada linha contra o que foi entregue.
