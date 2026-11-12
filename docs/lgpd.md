# LGPD: onde ficam os dados pessoais

O MVP do Akona Energy não coleta nem armazena dados pessoais. Os únicos dados potencialmente pessoais são os endereços IP de quem acessa a URL pública. Na infraestrutura definida no plano (E4, em construção em 11/11/2026), eles ficam nos logs enviados ao Log Analytics, na região eastus2, por 30 dias.

## Dados da aplicação

- Todos os cidadãos e chamados vêm de `app/data/mock.json`, um arquivo sintético escrito à mão e versionado no repositório. Os nomes são claramente fictícios (por exemplo, "Ana Fictícia da Silva").
- O mock não tem CPF, e-mail, telefone nem endereço exato, só o bairro de Osasco.
- Não há banco de dados, cadastro, login, cookie nem sessão.
- O formulário de novo chamado é ilustrativo: não envia nem grava nada, e avisa isso na tela.
- A página `/privacidade` explica isso ao visitante.

## Dados técnicos

| Dado | Onde fica | Retenção | Contém dado pessoal? |
| --- | --- | --- | --- |
| Métricas em `/metrics` | Memória do container e Prometheus local | Enquanto o container ou o Prometheus local estiverem de pé | Não. Só contadores técnicos (requisições, latência, status, CPU, memória), sem IP, nome ou identificador de usuário |
| Logs do Container App | Log Analytics, eastus2 | 30 dias | Sim, potencialmente: o IP do cliente pode aparecer nos logs de acesso do servidor e nos logs da plataforma |
| Imagem do container | GHCR | Até ser apagada | Não. A imagem só tem código e dados sintéticos |

## Princípios aplicados

- **Minimização:** o MVP não pede nem guarda nenhum dado pessoal para funcionar.
- **Transparência:** a página `/privacidade` diz o que é e o que não é coletado.
- **Limitação do armazenamento:** os logs ficam 30 dias no Log Analytics, e toda a infraestrutura é destruída em 01/12/2026.
- **Segurança:** pela infraestrutura definida no plano (E2 a E5), só HTTPS, nenhuma porta administrativa e segredos fora do repositório e da imagem.

## O que uma versão real exigiria

A proposta do produto prevê cidadãos autenticados reportando problemas. Uma versão real trataria dados pessoais (nome, contato e localização do problema) e exigiria, no mínimo:

- **Base legal e finalidade:** definir a base legal de cada tratamento (por exemplo, execução de política pública pela prefeitura) e usar os dados só para atender o chamado.
- **Transferência internacional (art. 33):** a região eastus2 fica nos Estados Unidos. Guardar dados pessoais lá exigiria enquadrar a transferência numa das hipóteses do art. 33 da LGPD, ou migrar os recursos para a região brazilsouth.
- **Direitos do titular:** canal para acesso, correção e exclusão dos dados, e um encarregado (DPO) indicado.
- **Segurança e retenção:** banco com criptografia e acesso restrito, prazo de retenção definido para chamados e logs, e mascaramento ou anonimização do IP nos logs quando possível.
- **Relatório de impacto:** avaliar a necessidade de um relatório de impacto à proteção de dados, já que o produto envolveria localização de moradores.

**Pendente (E8b):** confirmar no Log Analytics de produção que a retenção está em 30 dias e que a região é eastus2. Ambas dependem do E4 aplicado.
