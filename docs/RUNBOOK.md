# Runbook de Incidentes — Conecta PRO
**Versão:** 1.0 | **Data:** 2026-04-01 | **Responsável:** Jordan Jesus

---

## Severidades

| Nível | Descrição | SLA Resposta |
|-------|-----------|-------------|
| P0 — Crítico | Sistema indisponível, dados em risco | 15 min |
| P1 — Alto | Módulo principal fora, perda de dados | 1 hora |
| P2 — Médio | Funcionalidade degradada | 4 horas |
| P3 — Baixo | Bug cosmético, workaround disponível | 24 horas |

---

## Incidente 1 — Backend indisponível (porta 8080)

**Severidade:** P0 | **Sintomas:** API retorna connection refused, frontend sem dados

**Diagnóstico:**
```bash
# Verificar container
docker ps | grep conecta-pro-backend
docker logs $(docker ps -q --filter ancestor=conecta-pro-backend) --tail 50

# Testar endpoint de saúde
curl -s http://127.0.0.1:8080/health
```

**Resolução:**
```bash
# CENÁRIO A — container parado
docker start $(docker ps -aq --filter ancestor=conecta-pro-backend)

# CENÁRIO B — container com erro, reiniciar
docker restart $(docker ps -aq --filter ancestor=conecta-pro-backend)

# Aguardar 30s e verificar
sleep 30 && curl -s http://127.0.0.1:8080/health
```

---

## Incidente 2 — Frontend indisponível (porta 3001)

**Severidade:** P1 | **Sintomas:** ERP não carrega no browser

**Diagnóstico:**
```bash
pm2 status
pm2 logs --lines 30
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001
```

**Resolução:**
```bash
# CENÁRIO A — processo morto
pm2 restart all

# CENÁRIO B — build corrompido
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public
pm2 restart all
```

---

## Incidente 3 — Banco de dados lento ou com timeout

**Severidade:** P1 | **Sintomas:** Requests lentos, timeout 504, erros 500

**Diagnóstico:**
```bash
# Queries ativas há mais de 5 segundos
docker exec $(docker ps -q --filter ancestor=conecta-pro-backend) \
  python3 -c "
import asyncio
from core.database import get_db
# Ver pg_stat_activity via psql
"

# Alternativa: psql direto
docker exec -it $(docker ps -q --filter name=postgres) \
  psql -U erp_user -d erp_db -c "
  SELECT pid, now()-query_start AS duracao, LEFT(query,80) AS query
  FROM pg_stat_activity
  WHERE state = 'active' AND now()-query_start > interval '5 seconds'
  ORDER BY duracao DESC LIMIT 10;
"
```

**Resolução:**
```bash
# Encerrar queries travadas (>30s)
docker exec -it $(docker ps -q --filter name=postgres) \
  psql -U erp_user -d erp_db -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'active'
    AND now()-query_start > interval '30 seconds'
    AND pid <> pg_backend_pid();
"
```

---

## Incidente 4 — Agentes 24h sem reportar no Telegram

**Severidade:** P2 | **Sintomas:** Sem mensagem no bot há mais de 35 min

**Diagnóstico:**
```bash
# Verificar cron configurado
crontab -l | grep orchestrator

# Verificar logs do ciclo
tail -50 /opt/conecta-pro/logs/orchestrator.log

# Testar ciclo manualmente
cd /opt/conecta-pro
python3 agents/orchestrator_geral.py 2>&1 | tail -20
```

**Resolução:**
```bash
# CENÁRIO A — cron ausente, recriar
crontab -e
# Adicionar linha:
# */30 * * * * cd /opt/conecta-pro && MONITOR_BOT_TOKEN=$TOKEN TELEGRAM_CHAT_ID=5536961034 python3 agents/orchestrator_geral.py >> logs/orchestrator.log 2>&1

# CENÁRIO B — erro em agente específico
grep "ERROR\|ERRO" /opt/conecta-pro/logs/orchestrator.log | tail -10
# Corrigir o agente e testar individualmente
```

---

## Incidente 5 — Certificado A1 expirado

**Severidade:** P0 | **Sintomas:** NFS-e não emite, integração bancária falha, erro 401/403 em gov

**Ação imediata:**
1. Verificar data de expiração: `openssl pkcs12 -in credentials/*.pfx -nokeys -passin pass:Conecta123 2>/dev/null | openssl x509 -noout -enddate`
2. Contatar certificadora (Certisign / Serasa / Soluti)
3. Emitir novo certificado A1 (.pfx)
4. Atualizar arquivo em `/opt/conecta-pro/credentials/`
5. Ajustar permissões: `chown root:999 credentials/*.pfx && chmod 640 credentials/*.pfx`
6. Reiniciar container backend: `docker restart $(docker ps -q --filter ancestor=conecta-pro-backend)`

---

## Incidente 6 — Rate limit de auth atingido (429)

**Severidade:** P2 | **Sintomas:** Agentes retornam 429 / token não obtido

**Diagnóstico:**
```bash
# Verificar se rate limit está ativo
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612"
```

**Resolução:**
```bash
# Aguardar 60s (janela de rate limit) e rodar ciclo com token compartilhado
sleep 60
cd /opt/conecta-pro
python3 agents/orchestrator_geral.py
# orchestrator_geral.py já usa token compartilhado (monkey-patch BaseAgent)
```

---

## Contatos de Emergência

| Contato | Função | Canal |
|---------|--------|-------|
| Jordan Jesus | CEO/CTO | WhatsApp / jjesus@conectamais.pro |
| Suporte Hostinger | VPS/Infra | https://hpanel.hostinger.com |
| Bot Monitor | Alertas automáticos | Telegram @conecta_pro_monitor_bot |
