# INSTRUÇÕES KIMI — Plano de Deploy para Produção

**Papel:** Executor (monitoramento, logrotate, load testing)
**Branch:** feature/openclaw-v2
**Plano completo:** `/opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md`

---

## CONTEXTO

O Plano Mestre de Produção foi concluído 100% (2026-02-10). O código está estável:
- Pytest: 6287/0 | ESLint: 0 warn | TypeScript: 0 err | Vitest: 1985/1985 | Build: OK

Agora você trabalha na infraestrutura de monitoramento e testes. **NÃO toque no código da aplicação.**

---

## LEIA ANTES DE COMEÇAR

```bash
cat /opt/conecta-pro/.kimi/ERROS-PASSADOS.md
cat /opt/conecta-pro/.comms/HANDOFF.md
cat /opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md
```

---

## SUAS FASES (em ordem)

### FASE 3 — AlertManager & Notificações (1h)

#### 3.1 Criar `/opt/conecta-pro/monitoring/alertmanager/alertmanager.yml`

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default-webhook'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'critical-webhook'
      repeat_interval: 1h

receivers:
  - name: 'default-webhook'
    webhook_configs:
      - url: 'http://host.docker.internal:9095/webhook'
        send_resolved: true
  - name: 'critical-webhook'
    webhook_configs:
      - url: 'http://host.docker.internal:9095/webhook'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

**NOTA:** O webhook URL será configurado depois com Discord/Slack. Por agora usar placeholder.

#### 3.2 Adicionar AlertManager ao monitoring docker-compose

Editar `/opt/conecta-pro/monitoring/docker-compose.yml`:

Adicionar serviço:
```yaml
  alertmanager:
    image: prom/alertmanager:v0.27.0
    container_name: conecta-pro-alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9093/-/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - monitoring
```

#### 3.3 Conectar Prometheus ao AlertManager

Editar `/opt/conecta-pro/monitoring/prometheus/prometheus.yml`:

Adicionar seção alerting (se não existir):
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

Verificar que rule_files está correto:
```yaml
rule_files:
  - "alerts/*.yml"
```

#### 3.4 Verificar sintaxe
```bash
# Verificar config do AlertManager
docker run --rm -v /opt/conecta-pro/monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml prom/alertmanager:v0.27.0 --config.file=/etc/alertmanager/alertmanager.yml --dry-run 2>&1 || echo "Usar amtool check-config"

# Verificar config do Prometheus
docker run --rm -v /opt/conecta-pro/monitoring/prometheus:/etc/prometheus prom/prometheus:v2.48.0 promtool check config /etc/prometheus/prometheus.yml
```

---

### FASE 4 — Logrotate & Manutenção (30min)

#### 4.1 Criar logrotate config

Criar `/etc/logrotate.d/conecta-pro`:
```
/opt/conecta-pro/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker exec conecta-pro-nginx nginx -s reopen 2>/dev/null || true
    endscript
}
```

#### 4.2 Atualizar Loki retention

Editar `/opt/conecta-pro/monitoring/loki/loki-config.yml`:

Adicionar/atualizar:
```yaml
limits_config:
  retention_period: 720h  # 30 dias
  max_entries_limit_per_query: 5000

compactor:
  working_directory: /loki/compactor
  retention_enabled: true
  retention_delete_delay: 2h
```

#### 4.3 Testar
```bash
# Testar logrotate (dry-run)
logrotate -d /etc/logrotate.d/conecta-pro

# Forçar rotação (para testar)
logrotate -f /etc/logrotate.d/conecta-pro

# Verificar que logs não perderam
ls -la /opt/conecta-pro/logs/
```

---

### FASE 6 — Load Testing (1-2h)

#### 6.1 Instalar k6

```bash
# Verificar se já está instalado
which k6 && k6 version && echo "k6 já instalado" && exit 0

# Instalar via apt
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 \
  --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install -y k6
```

#### 6.2 Criar cenários de teste

Criar `/opt/conecta-pro/tests/load/k6-scenarios.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    // Cenário 1: Health check (baseline)
    health: {
      executor: 'constant-vus',
      vus: 10,
      duration: '1m',
      exec: 'healthCheck',
    },
    // Cenário 2: Login flow
    login: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 0 },
      ],
      exec: 'loginFlow',
      startTime: '1m',
    },
    // Cenário 3: API reads (dashboard, listagens)
    api_reads: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 30,
      maxVUs: 100,
      exec: 'apiReads',
      startTime: '3m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export function healthCheck() {
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    'health status 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}

export function loginFlow() {
  const payload = JSON.stringify({
    email: 'loadtest@conectamais.pro',
    password: 'LoadTest2024!',
  });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post(`${BASE_URL}/api/v1/auth/login`, payload, params);
  check(res, {
    'login status 200 or 401': (r) => [200, 401].includes(r.status),
    'login response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}

export function apiReads() {
  const endpoints = [
    '/api/v1/health/detailed',
    '/docs',
  ];
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const res = http.get(`${BASE_URL}${endpoint}`);
  check(res, {
    'api status not 500': (r) => r.status !== 500,
    'api response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(0.5);
}
```

#### 6.3 Executar (SOMENTE quando containers estiverem UP na Fase 8)
```bash
# Primeiro: teste rápido de smoke
k6 run --duration 30s --vus 5 /opt/conecta-pro/tests/load/k6-scenarios.js

# Depois: teste completo
k6 run /opt/conecta-pro/tests/load/k6-scenarios.js 2>&1 | tee /opt/conecta-pro/logs/load-test-results.txt
```

#### 6.4 Documentar resultados
Criar `/opt/conecta-pro/docs/LOAD-TEST-RESULTS.md` com:
```
Data: YYYY-MM-DD
Cenários: health, login, api_reads
VUs máximo: 100
Duração: 5min
P95 latency: Xms
P99 latency: Xms
Error rate: X%
Throughput: X req/s
```

---

## COMUNICAÇÃO

Ao iniciar:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","type":"status","subject":"Deploy Phase Start","content":"Iniciando Fase 3 - AlertManager"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

Ao concluir cada fase:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","type":"done","subject":"Fase X Concluída","content":"RESULTADO AQUI"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

---

## REGRAS

1. **NÃO toque no código da aplicação** (backend/frontend) — só monitoramento/infra
2. **NÃO suba containers** até Fase 8 (staging deploy é conjunto)
3. **NÃO rode load test** até containers estarem UP
4. **Leia ERROS-PASSADOS.md** antes de começar
5. **Commite após cada fase** com formato: `infra(escopo): descrição`
6. Se algo falhar, reporte no canal — NÃO tente corrigir sem aprovação
