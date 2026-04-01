# PLANO DE DEPLOY PARA PRODUÇÃO — Conecta PRO

**Versão:** 1.0
**Data:** 2026-02-10
**Autor:** Claude Opus 4.6 (Auditor)
**Aprovação:** Pendente Jordan

---

## OBJETIVO

Levar o Conecta PRO de "código 100% estável" para "produção 100% funcional" em 1 sessão.

**Servidor alvo:** 82.25.75.74 (srv1134814.hstgr.cloud) — Ubuntu 24.04, 4 CPUs, 16GB RAM, 200GB disk
**Domínio:** erp.conectamais.pro

---

## ESTRATÉGIA

Mesma do Plano Mestre:
- **Kimi:** Executor (monitoramento, logrotate, load testing)
- **Opus:** Executor (scripts deploy/rollback, segurança, backup/DR)
- **Claude:** Auditor (não executa sem autorização, valida tudo)
- **Fase final:** Triple verification (3 terminais, todos os checks)

---

## PRÉ-REQUISITOS (já temos)

| Item | Status |
|------|--------|
| Docker Compose principal | OK |
| Docker Compose Celery | OK |
| Docker Compose Monitoring | OK |
| Nginx config + SSL params | OK |
| Prometheus + alertas (7 rules) | OK |
| Grafana + dashboards | OK |
| Loki + Promtail | OK |
| .env.example completo | OK |
| init-letsencrypt.sh | OK |
| backup_database.sh | OK (precisa fix) |
| health_monitor.py | OK |
| verify-all.sh | OK |
| Código: 0 errors, 0 warnings | OK |

---

## FASE 1 — Scripts de Deploy & Rollback (Opus)

**Objetivo:** Criar scripts automatizados de deploy e rollback.

### 1.1 Criar `/opt/conecta-pro/scripts/deploy.sh`
```
Funcionalidades:
- Pull latest code (git pull)
- Build imagens Docker (com cache)
- Run migrações Alembic (alembic upgrade head)
- Deploy containers (docker compose up -d)
- Wait for health checks (curl /health com retry)
- Ativar monitoring stack
- Notificar sucesso/falha (Discord/Slack)
- Log em /opt/conecta-pro/logs/deploy.log
```

### 1.2 Criar `/opt/conecta-pro/scripts/rollback.sh`
```
Funcionalidades:
- Aceita tag/commit como argumento
- Backup database antes de rollback
- git checkout <tag>
- Rebuild + restart containers
- Verificar health
- Opção: rollback de migration (alembic downgrade)
```

### 1.3 Criar `/opt/conecta-pro/scripts/health-check.sh`
```
Wrapper simples que:
- Verifica todos os containers (docker ps)
- Curl /health no backend
- Curl / no frontend
- Check redis-cli ping
- Check pg_isready
- Return exit code 0/1
```

**Entregável:** 3 scripts testáveis
**Tempo estimado:** 1-2h

---

## FASE 2 — Segurança & Secrets (Opus)

**Objetivo:** Eliminar credenciais expostas.

### 2.1 Auditar `.env`
```
- Verificar permissões (deve ser 600 root:root)
- Confirmar que está no .gitignore
- Verificar que não foi commitado (git log --all -- .env)
```

### 2.2 Corrigir `backup_database.sh`
```
- Remover credenciais hardcoded (DB_USER, PGPASSWORD)
- Ler de .env via source
- Validar que vars existem antes de usar
```

### 2.3 Gerar secrets fortes
```bash
# JWT Secret (se ainda for o default)
openssl rand -hex 32

# Redis password
openssl rand -base64 24

# Encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2.4 Verificar CORS origins
```
- Backend: CORS_ORIGINS deve listar apenas erp.conectamais.pro
- Não deve ter * em produção
```

**Entregável:** .env seguro, backup script corrigido, CORS validado
**Tempo estimado:** 30min

---

## FASE 3 — AlertManager & Notificações (Kimi)

**Objetivo:** Rotear alertas do Prometheus para Discord/Slack.

### 3.1 Criar `monitoring/alertmanager/alertmanager.yml`
```yaml
route:
  receiver: 'discord-webhook'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'discord-critical'
      repeat_interval: 1h

receivers:
  - name: 'discord-webhook'
    webhook_configs:
      - url: '${DISCORD_WEBHOOK}'
  - name: 'discord-critical'
    webhook_configs:
      - url: '${DISCORD_WEBHOOK}'
```

### 3.2 Adicionar AlertManager ao docker-compose monitoring
```
- Imagem: prom/alertmanager:v0.26.0
- Port: 9093
- Volume: alertmanager.yml
- Health check
```

### 3.3 Conectar Prometheus ao AlertManager
```
- Atualizar prometheus.yml: alerting.alertmanagers
- Verificar que erp_alerts.yml carrega corretamente
```

### 3.4 Testar alerta
```
- Simular métrica fora do threshold
- Verificar que notificação chega no Discord/Slack
```

**Entregável:** AlertManager rodando, alertas testados
**Tempo estimado:** 1h

---

## FASE 4 — Logrotate & Manutenção (Kimi)

**Objetivo:** Logs não crescem infinitamente.

### 4.1 Criar `/etc/logrotate.d/conecta-pro`
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

### 4.2 Configurar Loki retention
```
- Definir retention_period em loki-config.yml (30 dias)
- Limits: max_entries_limit_per_query: 5000
```

### 4.3 Testar rotação manual
```bash
logrotate -f /etc/logrotate.d/conecta-pro
```

**Entregável:** Logrotate ativo, Loki com retention
**Tempo estimado:** 30min

---

## FASE 5 — Backup & Disaster Recovery (Opus)

**Objetivo:** Backup testado e restore comprovado.

### 5.1 Executar backup completo
```bash
./scripts/backup_database.sh
```

### 5.2 Testar restore
```bash
# Criar database temporário
docker exec conecta-pro-postgres createdb -U postgres conecta_pro_test

# Restore
gunzip -c backup.sql.gz | docker exec -i conecta-pro-postgres psql -U postgres conecta_pro_test

# Verificar tabelas
docker exec conecta-pro-postgres psql -U postgres conecta_pro_test -c "\dt" | wc -l

# Limpar
docker exec conecta-pro-postgres dropdb -U postgres conecta_pro_test
```

### 5.3 Configurar cron de backup
```bash
# Backup diário 3AM
echo "0 3 * * * /opt/conecta-pro/scripts/backup_database.sh >> /var/log/conecta-backup.log 2>&1" | crontab -
```

### 5.4 Documentar RTO/RPO
```
RTO (Recovery Time Objective): tempo para restaurar
RPO (Recovery Point Objective): máxima perda de dados aceitável
```

**Entregável:** Backup + restore testados, cron ativo, RTO/RPO documentados
**Tempo estimado:** 1h

---

## FASE 6 — Load Testing (Kimi)

**Objetivo:** Validar que o sistema aguenta carga real.

### 6.1 Instalar k6
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

### 6.2 Criar cenários de teste
```
Arquivo: /opt/conecta-pro/tests/load/scenarios.js

Cenários:
1. Login flow (POST /api/v1/auth/login) — 50 VUs, 2min
2. Dashboard load (GET /api/v1/dashboard) — 30 VUs, 2min
3. Financial listing (GET /api/v1/financial/invoices) — 20 VUs, 2min
4. Mixed workload (all above) — 100 VUs, 5min
```

### 6.3 Executar e documentar
```
Métricas alvo:
- P95 latency < 500ms
- Error rate < 1%
- Throughput > 100 req/s
```

**Entregável:** k6 instalado, cenários criados, resultados documentados
**Tempo estimado:** 1-2h

---

## FASE 7 — DNS & SSL (Jordan + Opus)

**Objetivo:** Domínio apontando para servidor com HTTPS.

### 7.1 Configurar DNS (Jordan manual)
```
Apontar erp.conectamais.pro → 82.25.75.74
Tipo: A record
TTL: 300 (5 min para propagação rápida)
```

### 7.2 Ativar Let's Encrypt (Opus)
```bash
sudo bash /opt/conecta-pro/scripts/init-letsencrypt.sh
```

### 7.3 Verificar HTTPS
```bash
curl -I https://erp.conectamais.pro
# Deve retornar 200 com headers de segurança
```

### 7.4 Verificar auto-renovação
```bash
certbot renew --dry-run
```

**Entregável:** HTTPS funcional, auto-renovação confirmada
**Tempo estimado:** 30min (após propagação DNS)

**NOTA:** Esta fase depende de Jordan configurar o DNS manualmente via Hostinger.

---

## FASE 8 — Deploy Staging (Todos)

**Objetivo:** Subir todo o stack e validar.

### 8.1 Subir stack principal
```bash
cd /opt/conecta-pro
docker compose up -d --build
```

### 8.2 Subir Celery workers
```bash
docker compose -f docker-compose.celery.yml up -d
```

### 8.3 Subir monitoring
```bash
cd /opt/conecta-pro/monitoring
docker compose up -d
```

### 8.4 Verificar todos os containers
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 8.5 Health checks
```bash
# Backend
curl -s http://localhost:8080/health | python3 -m json.tool

# Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001

# Redis
docker exec conecta-pro-redis redis-cli ping

# PostgreSQL
docker exec conecta-pro-postgres pg_isready -U postgres

# Prometheus
curl -s http://localhost:9090/-/ready

# Grafana
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
```

### 8.6 Rodar migrações
```bash
docker exec conecta-pro-backend alembic upgrade head
```

### 8.7 Teste E2E manual
```
1. Login: POST /api/v1/auth/login
2. Dashboard: GET /api/v1/dashboard
3. Listar condominios: GET /api/v1/condominios
4. Criar item: POST /api/v1/financial/invoices
5. WebSocket: /ws/notifications
```

**Entregável:** Todos os serviços UP, health OK, E2E passando
**Tempo estimado:** 1h

---

## FASE 9 — Validação Final Triple-Verified (Todos)

**Objetivo:** Mesma estratégia do Plano Mestre — 3 terminais, todos os checks.

### Checklist de Produção (15 checks)

| # | Check | Comando | Esperado |
|---|-------|---------|----------|
| 1 | Containers UP | `docker ps` | Todos healthy |
| 2 | Backend health | `curl localhost:8080/health` | 200 OK |
| 3 | Frontend health | `curl localhost:3001` | 200 OK |
| 4 | PostgreSQL | `pg_isready` | accepting connections |
| 5 | Redis | `redis-cli ping` | PONG |
| 6 | Alembic head | `alembic heads` | 1 head |
| 7 | SSL válido | `curl -I https://erp.conectamais.pro` | 200 + HSTS |
| 8 | Prometheus UP | `curl localhost:9090/-/ready` | 200 |
| 9 | Grafana UP | `curl localhost:3000/api/health` | 200 |
| 10 | AlertManager UP | `curl localhost:9093/-/ready` | 200 |
| 11 | Backup testado | Restore test log | OK |
| 12 | Logrotate ativo | `logrotate -d /etc/logrotate.d/conecta-pro` | No errors |
| 13 | Cron backup | `crontab -l` | 3AM daily |
| 14 | Certbot renewal | `certbot renew --dry-run` | Simulated OK |
| 15 | Load test P95 | k6 results | < 500ms |

### Cada terminal roda TODOS os 15 checks e reporta.

**Entregável:** Tabela comparativa 3×15 — tudo PASS
**Tempo estimado:** 30min

---

## CRONOGRAMA

| Ordem | Fase | Assignee | Deps | Tempo |
|-------|------|----------|------|-------|
| 1 | Fase 1: Scripts deploy/rollback | Opus | — | 1-2h |
| 1 | Fase 3: AlertManager | Kimi | — | 1h |
| 2 | Fase 2: Segurança/secrets | Opus | Fase 1 | 30min |
| 2 | Fase 4: Logrotate | Kimi | — | 30min |
| 3 | Fase 5: Backup/DR | Opus | Fase 2 | 1h |
| 3 | Fase 6: Load testing | Kimi | — | 1-2h |
| 4 | Fase 7: DNS/SSL | Jordan+Opus | Fase 1 | 30min |
| 5 | Fase 8: Deploy staging | Todos | Fases 1-7 | 1h |
| 6 | Fase 9: Validação final | Todos | Fase 8 | 30min |

**Tempo total estimado:** 4-6h (com paralelismo Kimi+Opus)

---

## REGRAS (mesmas do Plano Mestre)

1. NÃO quebre o que já funciona (código estável a 100%)
2. Claude audita, NÃO executa sem autorização
3. Cada fase: implementar → testar → commitar → próxima
4. Se algo falhar, PARE e reporte — NÃO tente corrigir sem aprovação
5. Comunicação via `.comms/` (JSONL + Markdown)
6. Validação final é triple-verified (3 terminais)

---

## DEFINIÇÃO DE DONE

O deploy está 100% quando:
- [ ] 15/15 checks PASS em todos os 3 terminais
- [ ] https://erp.conectamais.pro responde com 200
- [ ] Login funciona end-to-end
- [ ] Alertas chegam no Discord/Slack
- [ ] Backup + restore testados
- [ ] Load test P95 < 500ms
- [ ] Zero credentials em texto plano fora de .env (e .env tem chmod 600)
