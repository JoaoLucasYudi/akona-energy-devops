# Akona Energy · Modelo de negócio, go-to-market e indicadores

GS 2026.2 · Business Intelligence & Startup Development · FIAP

Este documento sustenta o pitch. Ele não muda o produto que já está no ar: descreve quem paga por ele, como ele chega aos clientes e quais indicadores mostram que ele funciona. Os números marcados como **premissa** são estimativas da equipe, a validar no piloto.

## 1. O problema, com evidência

O morador vê um poste apagado e não sabe a quem avisar, nem se alguém vai resolver. Quem resolve (prefeitura ou concessionária) recebe pedidos soltos por telefone e não consegue provar prazo nem priorizar por bairro.

| Evidência | Fonte |
| --- | --- |
| Iluminação reduz crime: num experimento controlado em Nova York, mais luz levou a uma queda de pelo menos 36% nos crimes noturnos em área externa | Chalfin et al., NBER w25798 (2019), publicado no *Journal of Quantitative Criminology* (2022) |
| O canal atual não resolve: no DF, de 6.050 reclamações sobre iluminação entre janeiro e setembro, só 6,9% constavam como resolvidas | Metrópoles, dados do painel da Ouvidoria do GDF |
| O cidadão paga a iluminação (COSIP na conta de luz) mesmo quando a rua está escura | Correio Braziliense, 29/10/2026 |
| Osasco tem 728.615 habitantes (Censo 2022) e é um dos municípios mais densos do país | IBGE; Gazeta de S.Paulo |

Frase para o pitch: *"Uma rua apagada é uma rua menos segura, e hoje ninguém consegue dizer quanto tempo ela fica apagada."*

## 2. Proposta de valor

| Para quem | O que ganha |
| --- | --- |
| Cidadão | Abre um chamado em segundos, sem cadastro, e acompanha o status pelo protocolo |
| Gestor (prefeitura ou concessionária) | Fila única de chamados, prazo por tipo de problema e um painel que mostra onde a cidade está mais atrasada |
| Fiscalização e transparência | Indicadores públicos de prazo por bairro, que mostram se o serviço pago pela COSIP está sendo entregue |

## 3. Modelo de negócio (Lean Canvas)

| Bloco | Akona Energy |
| --- | --- |
| Segmentos | **Quem paga:** (a) concessionárias de PPP de iluminação pública; (b) prefeituras que operam a iluminação por contrato próprio, como Osasco. **Quem usa:** cidadãos (grátis) e equipes de gestão e manutenção |
| Problema | Chamados dispersos (156, telefone, redes sociais), sem prazo medido, sem priorização por bairro e sem prova de desempenho |
| Solução | Webapp de chamados sem cadastro, painel de gestão com indicadores e página pública de transparência |
| Proposta única | Transformar reclamação em indicador: cada chamado vira prazo medido, por bairro |
| Vantagem | Base histórica de chamados e prazos por cidade; integração com o cadastro de pontos de luz (QR code no poste) |
| Canais | CPSI (Marco Legal das Startups) para prefeituras; venda direta para concessionárias de PPP; QR code no poste para o cidadão |
| Receita | Assinatura SaaS por ponto de luz por mês, mais uma taxa de implantação |
| Custos | Nuvem, equipe de produto e suporte, implantação (cadastro dos pontos e adesivos com QR code) |
| Métricas-chave | Ver seção 6 |

### Precificação (premissa)

- **Licença:** R$ 0,25 por ponto de luz por mês.
- **Implantação:** taxa única para importar o cadastro de pontos e gerar os QR codes.

Osasco não publica o total de pontos de luz no material consultado. Pela proporção de outras cidades (Jundiaí: 47.551 pontos; Curitiba: cerca de 157 mil), estimamos **cerca de 70 mil pontos** em Osasco (premissa, a confirmar com o cadastro da prefeitura).

| Conta | Valor |
| --- | --- |
| 70.000 pontos × R$ 0,25 | R$ 17.500 por mês |
| Receita anual por cidade do porte de Osasco | R$ 210.000 |

Para comparação: a PPP de Teresina, cidade de porte parecido, tem valor estimado de R$ 775 milhões em 20 anos (cerca de R$ 39 milhões por ano). A licença do Akona custaria cerca de 0,5% disso.

## 4. Tamanho de mercado

| Recorte | Base | Estimativa anual |
| --- | --- | --- |
| TAM | 18 milhões de pontos de luz no Brasil (Abdib) × R$ 3,00 por ano | R$ 54 milhões |
| SAM | Municípios paulistas com PPP de iluminação em estruturação ou contratada (71, segundo a Brasil Energia), com porte médio de 30 mil pontos | cerca de R$ 6,4 milhões |
| SOM em 3 anos | 5 cidades da Grande SP, com 250 mil pontos no total | R$ 750 mil |

Os portes médios do SAM e do SOM são premissas.

## 5. Go-to-market

### Quem paga e por que paga agora

- **Concessionárias de PPP:** quase 30% das PPPs assinadas no país nos últimos cinco anos foram de iluminação pública. Esses contratos medem prazos de atendimento (em Porto Alegre, a carta de serviços da PPP prevê prazos de 6 horas a 15 dias, conforme a criticidade). A concessionária precisa provar que cumpre o prazo, e o Akona gera essa prova.
- **Prefeituras sem PPP (caso de Osasco):** pagam a manutenção por contrato tradicional e não têm um painel para fiscalizar a contratada.

### Como a venda acontece

| Fase | Período | Ação | Meta |
| --- | --- | --- | --- |
| 0 · MVP | Hoje | Produto no ar, dados simulados | Validar o fluxo com moradores e gestores |
| 1 · Piloto em Osasco | 12 meses | CPSI (Contrato Público para Solução Inovadora) com a prefeitura. Começa em 3 bairros e expande para a cidade | Medir o tempo de reparo antes e depois e atingir 85% dos chamados no prazo |
| 2 · Concessionárias | Ano 2 | Venda direta a consórcios de PPP de iluminação, usando o case de Osasco | 2 contratos |
| 3 · Grande SP | Ano 2 e 3 | Cidades vizinhas (Barueri, Carapicuíba, Cotia) por CPSI ou contrato de fornecimento | 5 cidades no total |

Por que o CPSI: o Marco Legal das Startups (LC 182/2021) criou uma licitação especial para testar soluções inovadoras, com contrato de até R$ 1,6 milhão e 12 meses, prorrogáveis por mais 12. Se o teste der certo, a prefeitura pode assinar um contrato de fornecimento de até R$ 8 milhões. É o caminho natural para uma startup vender ao poder público sem disputar só por menor preço.

### Como o cidadão chega ao produto

- **QR code no poste:** um adesivo com o código do ponto de luz. O morador aponta o celular e o chamado já sai com o local exato, sem pedir endereço nem dado pessoal (bom para a LGPD).
- Link no site da prefeitura, no 156 e no WhatsApp oficial.
- Instalação dos adesivos pelas equipes de manutenção, durante as rondas que já fazem.

## 6. Indicadores

### Impacto no cidadão

| Indicador | Fórmula | Meta do piloto |
| --- | --- | --- |
| Tempo médio de reparo | média de (data de resolução − data de abertura), em horas | Reduzir 30% em relação à linha de base |
| Chamados no prazo | chamados resolvidos dentro do prazo do tipo ÷ chamados resolvidos | 85% |
| Gap de equidade | tempo médio de reparo do bairro mais lento ÷ tempo médio da cidade | Abaixo de 1,5 |
| Reincidência | chamados reabertos no mesmo ponto em até 30 dias ÷ chamados resolvidos | Abaixo de 10% |
| Pontos apagados agora | chamados abertos de "poste apagado" | Tendência de queda |

Prazos por tipo (premissa, inspirada em cartas de serviço de São Paulo, Curitiba e Porto Alegre): fio caído em 6 h, queda de energia em 24 h, poste apagado em 48 h e lâmpada piscando em 72 h.

### Negócio

| Indicador | O que mostra |
| --- | --- |
| Pontos de luz sob contrato e MRR | Tamanho e receita recorrente |
| Chamados por mês e % vindos do Akona (contra o 156) | Adoção pelo cidadão |
| Avaliação do atendimento (1 a 5, após a resolução) | Satisfação |
| Renovação de contrato | Retenção |
| Custo de aquisição por cidade (CAC) | Eficiência comercial |

## 7. ODS

| ODS | Contribuição |
| --- | --- |
| 11 · Cidades e comunidades sustentáveis | Espaços públicos mais seguros (meta 11.7), com reparo mais rápido da iluminação |
| 10 · Redução das desigualdades | O gap de equidade mostra quando a periferia espera mais que o centro e orienta a priorização |
| 7 · Energia limpa e acessível | Chamados de "lâmpada acesa de dia" e o histórico por ponto ajudam a cortar desperdício e a priorizar a troca para LED (meta 7.3) |

## 8. Viabilidade e pedido

| Item | Valor (premissa) |
| --- | --- |
| Custo da nuvem hoje (medido) | US$ 14 por mês (ver [custo.md](custo.md)) |
| Custo operacional depois do piloto (equipe de 3 pessoas, nuvem em brazilsouth com banco, comercial) | cerca de R$ 45 mil por mês |
| Receita por cidade do porte de Osasco | R$ 17,5 mil por mês |
| Ponto de equilíbrio | 3 cidades de porte médio (cerca de 210 mil pontos) |

**Pedido:** um piloto via CPSI com a Prefeitura de Osasco, de 12 meses, por R$ 300 mil (R$ 210 mil de licença e R$ 90 mil de implantação: cadastro dos pontos e QR codes). É menos de 20% do teto do CPSI. O critério de sucesso é público: tempo de reparo 30% menor e 85% dos chamados no prazo.

## Fontes

- [Chalfin et al. · Reducing Crime Through Environmental Design (NBER)](https://www2.nber.org/digest/jul19/w25798.shtml)
- [Metrópoles · CEB resolve só 6,9% das reclamações sobre iluminação no DF](https://www.metropoles.com/distrito-federal/ceb-resolve-so-69-das-reclamacoes-sobre-iluminacao-precaria-no-df)
- [Correio Braziliense · Moradores pagam Cosip com a rua às escuras](https://www.correiobraziliense.com.br/cbradar/iluminacao-publica-prefeitura-omissao-acao-civil-publica/)
- [População de Osasco, Censo 2022](https://cepsbrasil.com.br/sp/osasco/ibge)
- [Jus.com.br · Quase 30% das PPPs dos últimos cinco anos são de iluminação](https://jus.com.br/artigos/71862/seis-pontos-de-atencao-em-modelagens-de-ppps-no-setor-de-iluminacao-publica)
- [Brasil Energia · 71 municípios paulistas com projetos de PPP de iluminação](https://brasilenergia.com.br/brasilenergia/novos-modelos-e-tecnologias-em-energia/iluminacao-publica-avanca-com-modelos-de-ppps-e-consorcios)
- [Folha Vitória · 18 milhões de pontos de luz no Brasil (Abdib)](https://www.folhavitoria.com.br/economia/ppps-de-iluminacao-geram-disputa-entre-investidores/)
- [Prefeitura de Jundiaí · 47.551 pontos de iluminação](https://jundiai.sp.gov.br/noticias/2020/01/09/parceria-publico-privada-para-troca-da-iluminacao-da-cidade-e-tema-de-audiencia-publica/)
- [Prefeitura de Curitiba · cerca de 160 mil pontos e reparo em 48 h](https://www.curitiba.pr.gov.br/noticias/viu-uma-lampada-que-precisa-de-reparo-informe-ao-156/61334)
- [eixos · PPP de Teresina, R$ 775 milhões em 20 anos](https://eixos.com.br/?p=27025)
- [Prefeitura de Porto Alegre · prazos da PPP de iluminação, de 6 h a 15 dias](https://prefeitura.poa.br/carta-de-servicos/iluminacao-publica-luminaria-acesa-durante-o-dia)
- [SP Regula · reparo em até 24 h](https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/335723)
- [Direção Concursos · CPSI: até R$ 1,6 milhão, 12 + 12 meses](https://www.direcaoconcursos.com.br/artigos/lei-startups)
- [Findes · Contrato de fornecimento de até R$ 8 milhões](https://findes.com.br/wp-content/uploads/2020/03/Apresentacao-Marco-Legal-Startups-2021.pdf)
