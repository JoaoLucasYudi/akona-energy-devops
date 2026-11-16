# Estimativa de custo

A infraestrutura fica no ar de 14/11/2026 até a limpeza em 01/12/2026, cerca de 17 dias. A assinatura é a Azure for Students: o gasto sai do crédito da conta e, se o crédito acabar, a assinatura é suspensa, sem cobrança em cartão. Por isso não há budget configurado.

Os valores foram calculados com os preços públicos de varejo da Azure para eastus2, consultados em 16/11/2026 na [Azure Retail Prices API](https://prices.azure.com/api/retail/prices), a mesma base da [calculadora de preços](https://azure.microsoft.com/pt-br/pricing/calculator/). São estimativas, não cotação.

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

O período começa em 14/11 e vai até 30/11 (17 dias, na franquia de novembro). O dia 01/12 usa a franquia de dezembro e sai a custo zero.

## Preços unitários (eastus2, US$)

| Medidor | Preço | Franquia gratuita mensal |
| --- | --- | --- |
| Container Apps · vCPU em uso ativo | 0,000024 por vCPU-segundo | 180.000 vCPU-segundos |
| Container Apps · vCPU ociosa | 0,000003 por vCPU-segundo | (a mesma franquia) |
| Container Apps · memória (ativa ou ociosa) | 0,000003 por GiB-segundo | 360.000 GiB-segundos |
| Container Apps · requisições | 0,40 por milhão | 2 milhões |
| Log Analytics · ingestão (Analytics Logs) | 2,76 por GB | 5 GB |

A franquia vale por assinatura. A réplica fica "ociosa" quando não está processando requisições, e aí a vCPU é cobrada a um oitavo do preço ativo. A taxa de gerenciamento de ambiente (US$0,10/hora) é do plano Dedicated; o ambiente usa só o perfil Consumption e não paga essa taxa. O tráfego do MVP fica muito abaixo de 2 milhões de requisições por mês, então requisições custam zero.

## Estimativa

Valor de referência conservador: a réplica é cobrada como se ficasse em uso ativo o tempo todo, e os logs ficam dentro da franquia de 5 GB por mês. O volume de logs não foi medido, mas um único app com pouco tráfego fica bem abaixo disso.

| Item | Conta (excedente da franquia × preço) | Custo mensal (US$) | Custo de 14/11 a 01/12 (US$) |
| --- | --- | --- | --- |
| Container Apps · vCPU | mês: 468.000 × 0,000024; período: 187.200 × 0,000024 | 11,23 | 4,49 |
| Container Apps · memória | mês: 936.000 × 0,000003; período: 374.400 × 0,000003 | 2,81 | 1,12 |
| Container Apps · requisições | dentro da franquia | 0,00 | 0,00 |
| Log Analytics | dentro da franquia de 5 GB | 0,00 | 0,00 |
| GHCR e GitHub Actions | gratuitos para repositório público | 0,00 | 0,00 |
| **Total** | | **14,04** | **5,62** |

O resultado confirma a ordem de grandeza prevista no plano: US$12–14 por mês e US$5–7 no período.

### Faixa possível

| Cenário | Premissa | Custo mensal (US$) | Custo de 14/11 a 01/12 (US$) |
| --- | --- | --- | --- |
| Otimista | Réplica ociosa quase o tempo todo (vCPU a 0,000003), logs dentro da franquia | 4,21 | 1,68 |
| Referência | Réplica sempre em uso ativo, logs dentro da franquia | 14,04 | 5,62 |
| Pior caso | Referência + logs batendo a cota de 0,5 GB todo dia (15 GB/mês; 8,5 GB no período) | 41,64 | 15,28 |

O pior caso é um teto teórico: a cota diária corta a ingestão em 0,5 GB, então o gasto com logs não passa de US$27,60 por mês.

## Controle de gasto

- **Crédito da Azure for Students:** o consumo é acompanhado pelo saldo de crédito no portal da Students. Não há budget, porque a assinatura não gera cobrança em cartão.
- **Limites na própria infra:** réplica única, recursos mínimos (0.25 vCPU, 0.5 GiB) e cota diária de logs.
- **Limpeza:** em 01/12/2026, `terraform destroy`, exclusão do service principal e conferência no Cost Management de que não sobrou gasto.
