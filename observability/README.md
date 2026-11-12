# Observabilidade local

Prometheus e Grafana rodam no docker compose, no profile `observability`. Dashboard, fonte de dados e regra de alerta são provisionados por arquivo: nada precisa ser criado à mão no Grafana.

## Subir

```bash
cp .env.example .env   # troque GF_SECURITY_ADMIN_PASSWORD
docker compose --profile observability up -d --build
```

- Grafana: <http://127.0.0.1:3000> (usuário `admin`, senha do `.env`). Dashboard "Golden Signals — Akona Energy", pasta "Akona Energy".
- Prometheus: <http://127.0.0.1:9090/targets>.

## Gerar tráfego

```bash
python scripts/gerar_trafego.py --minutos 5            # só tráfego normal
python scripts/gerar_trafego.py --minutos 5 --erros    # inclui /simular-erro
```

`--url` aponta para outra instância (padrão `http://localhost:8000`). Com `--erros`, o app precisa de `ENABLE_ERROR_SIMULATION=true`; sem isso, `/simular-erro` responde 404 e o alerta não dispara.

## Regra "Taxa de erro alta"

Dispara quando mais de 5% das respostas de um job são 5xx por 1 minuto, com uma instância por job (`mvp-local` e `mvp-prod`). Sem tráfego a razão é 0/0, e "No data" e "Error" contam como OK: numa stack recém-criada o estado aparece como `Normal (NoData)`; depois do primeiro tráfego, `Normal`.

## Alvo de produção (E6b)

O job `mvp-prod` em `prometheus/prometheus.yml` está declarado com a lista de alvos vazia, porque o FQDN do Container App só existe depois do `terraform apply` (H4). Para preencher:

```bash
terraform -chdir=infra/terraform output -raw app_fqdn
```

Troque `targets: []` por `targets: ["<app_fqdn>:443"]` e reinicie o Prometheus (`docker compose --profile observability restart prometheus`). O job passa a aparecer na variável "Ambiente" do dashboard assim que tiver um alvo.
