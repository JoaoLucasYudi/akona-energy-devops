# Plano de refino do MVP para Business Intelligence

O objetivo é que o MVP aguente o critério de maior peso do pitch, **"MVP demonstrado em uso real" (2,5 pontos)**, e mostre na tela os indicadores do [negocio.md](negocio.md), **sem mudar a infraestrutura**. Continua sem banco, sem login e sem JavaScript, e o pipeline, o Terraform e a observabilidade ficam como estão. Cada mudança é um PR para a `main`, e o deploy acontece pelo próprio pipeline.

## O que falta hoje

| Lacuna | Por que pesa no pitch |
| --- | --- |
| O formulário de novo chamado não grava (o botão fica desativado) | A banca precisa ver o cidadão abrir um chamado e a gestão recebê-lo. Hoje a demo é só navegação |
| O `/gestao` só mostra contagens por status, tipo e bairro | Não há nenhum indicador de prazo ou de impacto, que é o que o pitch defende |
| São só 20 chamados, sem data de resolução | Não dá para calcular tempo de reparo nem chamados no prazo |

## Mudanças (em ordem de prioridade)

### R1 · Dados sintéticos com histórico (obrigatório)

- `scripts/gerar_mock.py`, com seed fixa, gera cerca de 300 chamados nos últimos 90 dias, em cerca de 12 bairros reais de Osasco (Centro, Presidente Altino, Vila Yara, Rochdale, Jardim Bussocaba, Km 18, Quitaúna, Helena Maria, Munhoz Júnior, Bonfim, Novo Osasco, Jardim D'Abril).
- Campos novos em cada chamado: `aberto_em` e `resolvido_em` (data e hora; `null` se ainda aberto), `prazo_horas` (pelo tipo) e `ponto_id` (código do poste, para medir reincidência).
- Prazos por tipo: fio caído em 6 h, queda de energia em 24 h, poste apagado em 48 h e lâmpada piscando em 72 h.
- O cenário simulado faz alguns bairros periféricos demorarem mais, para o gap de equidade aparecer. **O README e o pitch dizem que os dados são simulados e como foram gerados.**
- O cidadão de demonstração continua o mesmo, com nome claramente fictício. Os outros chamados não precisam de cidadão.

### R2 · Chamado de verdade (obrigatório)

- `POST /chamados/novo` grava o chamado numa lista em memória do processo e redireciona para `/chamados/{id}`, que mostra o protocolo.
- Campos: tipo (select), bairro (select) e ponto de referência (texto curto, até 120 caracteres, com o aviso *"não informe nome, telefone ou endereço"*). Sem campo livre longo.
- Funciona porque o Container App tem uma réplica só. Se o container reiniciar, os chamados novos se perdem; isso vai documentado como limitação.
- `GET /chamados/novo?ponto=OSC-01234` já preenche o ponto. É assim que o QR code no poste funcionaria, e dá para mostrar no pitch com um QR impresso.

### R3 · Gestão muda o status (obrigatório)

- Na tabela do `/gestao`, um formulário por linha com o botão **Iniciar** (aberto → em andamento) ou **Resolver** (em andamento → resolvido, grava `resolvido_em`).
- `POST /gestao/chamados/{id}/status`, sem login (limitação declarada: em produção seria um perfil autenticado).
- É o que fecha o ciclo na demo: o cidadão abre, a gestão resolve e o indicador muda na tela.

### R4 · Painel de BI no `/gestao` (obrigatório)

- `app/indicadores.py`, com funções puras e testadas, calcula os indicadores da seção 6 do [negocio.md](negocio.md).
- No topo, cartões com: chamados abertos, tempo médio de reparo, % no prazo, gap de equidade e reincidência.
- Tabela por bairro com chamados, tempo médio, % no prazo e uma barra horizontal feita em CSS (largura proporcional, sem JavaScript), ordenada do pior para o melhor.
- Tabela semanal das últimas 12 semanas: chamados abertos × resolvidos.
- Filtro de período por query string: `?dias=30`, `?dias=90`.
- `GET /api/indicadores` devolve o mesmo cálculo em JSON, como contrato para outro consumidor (Power BI, Databricks).

### R5 · Página pública de transparência (desejável)

- `/transparencia`: % no prazo e tempo médio por bairro, sem identificar ninguém. É a resposta ao cidadão que paga a COSIP e sustenta o argumento de venda para a prefeitura.

### R6 · Métrica de negócio no Grafana (desejável, barato)

- Contador Prometheus `akona_chamados_criados_total{tipo}` e `akona_chamados_resolvidos_total{tipo}`, mais um painel no dashboard atual. Liga a entrega de DevOps à de BI com um print só.

## O que não fazer

- Não criar banco, login, fila nem novo recurso na Azure.
- Não colocar JavaScript nem biblioteca de gráficos: barras em CSS bastam.
- Não coletar nenhum dado pessoal.

## Documentos a ajustar depois do deploy

| Documento | Ajuste |
| --- | --- |
| README (Ficha Técnica) | Proposta de valor sem "somente leitura"; indicadores de impacto agora medidos sobre dados simulados; link para o [negocio.md](negocio.md); ODS 11, 10 e 7 |
| [lgpd.md](lgpd.md) | O formulário grava em memória: tipo, bairro e ponto de referência, sem dado pessoal, perdidos ao reiniciar |
| Relatório de DevOps | A conclusão diz que "o MVP é somente leitura". Atualizar essa frase se o PDF ainda não tiver sido enviado |

Os testes (pytest) cobrem os cálculos de `indicadores.py`, a criação de chamado e a troca de status. O Semgrep já roda no pipeline, e o Jinja2 escapa a entrada do usuário por padrão.

## Roteiro do pitch (até 5 minutos)

| Tempo | Bloco | Critério (peso) | O que mostrar |
| --- | --- | --- | --- |
| 0:00 | Cidadão e problema | Problema com evidência (1,5) | Rua apagada em Osasco. Dado: luz reduz pelo menos 36% dos crimes noturnos (NYC); no DF, só 6,9% das reclamações sobre iluminação constavam como resolvidas |
| 0:30 | Solução | (1,5) | "Cada reclamação vira um prazo medido, por bairro" |
| 1:00 | Demo ao vivo na URL pública | MVP em uso real (2,5) | 1) Celular lê o QR do poste e abre o formulário com o ponto preenchido. 2) Envia e recebe o protocolo. 3) No `/gestao`, o chamado aparece no topo; clicar em Iniciar e depois em Resolver. 4) Os cartões de indicadores mudam. 5) A tabela por bairro mostra o gap de equidade. 6) `/transparencia` |
| 2:30 | Modelo de negócio e GTM | Negócio e GTM (2,0) | Quem paga (concessionária de PPP ou prefeitura), quem usa (cidadão, grátis), preço por ponto, CPSI e QR no poste |
| 3:30 | Indicadores e ODS | Indicadores (1,5) | As metas do piloto (−30% no tempo de reparo, 85% no prazo, gap < 1,5) e os ODS 11, 10 e 7 |
| 4:15 | Viabilidade e pedido | Viabilidade (1,0) | Nuvem a US$ 14 por mês, equilíbrio com 3 cidades, pedido de piloto CPSI de R$ 300 mil em 12 meses |
| 4:45 | Fecho | Clareza (1,5) | "Rua escura tem prazo. O Akona mede esse prazo." |

Dicas: gravar a demo antes, com a URL visível na barra do navegador; legendas; deixar avisado na tela que os dados são simulados; testar o link do YouTube (não listado) numa janela anônima.
