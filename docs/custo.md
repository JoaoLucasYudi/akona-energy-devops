# Estimativa de custo

A infraestrutura fica no ar de 14/11/2026 até a limpeza em 01/12/2026, cerca de 17 dias. Um budget de US$10 no resource group, a criar na tarefa H4, vai proteger contra gasto inesperado.

**Pendente (E8b):** os valores em dólar desta página saem da [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/). O link da estimativa salva e o print (item 20 do checklist de evidências) entram no E8b.

## Premissas

| Item | Configuração | Observação |
| --- | --- | --- |
| Região | eastus2 | |
| Azure Container Apps | Plano consumption, 1 réplica sempre ativa (min = max = 1), 0.25 vCPU e 0.5 GiB | A réplica nunca escala a zero, então é cobrada o mês inteiro |
| Log Analytics | SKU `PerGB2018`, cota diária de 0,5 GB, retenção de 30 dias | O volume esperado é bem menor que a cota; a cota é um teto |
| GitHub Container Registry | Pacote público | Gratuito para repositório público |
| GitHub Actions | Runners hospedados pelo GitHub | Gratuito para repositório público |
| Prometheus e Grafana | Máquina da equipe | Sem custo de nuvem |

## Consumo do Container App

Com a réplica sempre ativa, o consumo é fixo:

| Período | Segundos | vCPU-segundos (× 0.25) | GiB-segundos (× 0.5) |
| --- | --- | --- | --- |
| Mês de 30 dias | 2.592.000 | 648.000 | 1.296.000 |
| 14/11 a 01/12 (17 dias) | 1.468.800 | 367.200 | 734.400 |

O plano consumption tem uma franquia gratuita mensal de vCPU-segundos, GiB-segundos e requisições por assinatura. A calculadora já desconta essa franquia.

## Estimativa

| Item | Custo mensal (US$) | Custo de 14/11 a 01/12 (US$) |
| --- | --- | --- |
| Azure Container Apps | Pendente | Pendente |
| Log Analytics | Pendente | Pendente |
| GHCR e GitHub Actions | 0,00 | 0,00 |
| **Total** | **Pendente** | **Pendente** |

O plano previa uma ordem de grandeza de US$12–14 por mês e US$5–7 no período, já descontada a franquia. Esses números não foram confirmados; a tabela acima só recebe valores tirados da calculadora.

## Controle de gasto

- **Budget:** US$10 no resource group, com alertas em 50% e 90%. Pela estimativa do plano, o alerta de 50% deve disparar no período, e isso é esperado.
- **Limites na própria infra:** réplica única, recursos mínimos (0.25 vCPU, 0.5 GiB) e cota diária de logs.
- **Limpeza:** em 01/12/2026, `terraform destroy`, exclusão do service principal e conferência no Cost Management de que não sobrou gasto.

**Pendente (E8b):** confirmar que o budget foi criado no portal (tarefa H4) e incluir o print (item 9 do checklist de evidências). Se a assinatura Azure for Students não permitir budgets, registrar aqui que o acompanhamento foi feito pelo crédito no portal de patrocínio.
