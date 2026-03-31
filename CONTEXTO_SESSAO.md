# CONTEXTO DE SESSÃO — Conecta PRO
## Gerado em 31/03/2026 18:06
## Branch: feature/people-management-reorganization
## VPS: srv1134814.hstgr.cloud (82.25.75.74) · Backend: 8080 · Frontend: 3001

---

## TOKEN DE ACESSO
```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend --format '{{.Names}}' | head -1)
```

---

## STATUS DOS MÓDULOS
  ✅ Auth /me: HTTP 200
  ⚠️  GED /kits: HTTP 422
  ⚠️  Financeiro /recv: HTTP 422
  ⚠️  Operacional /posts: HTTP 404
  ✅ Bartolo /greeting: HTTP 200
  ✅ DP /employees: HTTP 200
  ⚠️  Gov /jobs/status: HTTP 422
  ✅ BI /dashboard: HTTP 200

---

## DADOS REAIS DO BANCO
- Funcionários ativos: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- Batidas de ponto: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- Kits documentais: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- Documentos GED: OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- A receber (pendente): R$ OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- A pagar (pendente):   R$ OCI runtime exec failed: exec failed: unable to start container process: exec: "psql": executable file not found in $PATH
- MRR estimado: R$ 272.086,96
- Clientes ativos: 11

---

## SCORES DAS AUDITORIAS (Skills 01–04)
  • Skill 01 — Debugger: 6.4/10 (284/376 endpoints passando)
  • Skill 02 — Code Review: 6.7/10 (12 endpoints sem auth, 42 UUID params)
  • Skill 03 — REST Design: 6.2/10 (GED 4.5 | Financeiro 5.0 | DP 6.3 | Op 8.2 | AI 7.1)
  • Skill 04 — Testes: 4.1/10 (pytest NÃO instalado, 22 bugs sem regressão)

---

## BUGS CRÍTICOS PENDENTES (por prioridade)
  🔴 P1 — pytest NÃO instalado no container (todos os 3247 testes inoperantes)
  🔴 P2 — BI Dashboard bi_controller.py: Session→AsyncSession (0/11 endpoints)
  🔴 P3 — 10 handlers sem auth: punch_controller + folha_controller
  🔴 P4 — accounting_controller current_user["key"] (72 ocorrências, 4 endpoints 500)
  🔴 P5 — CCT Controller SQL colunas erradas (nome_cargo→cargo_nome, 5 endpoints 500)
  🟡 P6 — DocumentTagRepository sem is_associated (4 endpoints GED 500)
  🟡 P7 — TimeBankRepository sem get_stats (dashboard banco de horas 500)
  🟡 P8 — tenant_id mismatch: 10 comunicados + 11 medidas invisíveis
  🟡 P9 — 60+ testes SKIPADOS por falta de auth fixture
  🟡 P10 — Frontend: ZERO arquivos de teste

---

## ÚLTIMOS COMMITS
```
ab7fe383 Revert "feat(monitor): reinício automático após reboot — systemd timer + docker unless-stopped + health_check 5min + cron @reboot fallback"
924d91bf feat(monitor): reinício automático após reboot — systemd timer + docker unless-stopped + health_check 5min + cron @reboot fallback
8f3fa32d Revert "fix(financial): grace_days + condominio_id JWT + N+1 bulk + list_with_filters + paginação + f-strings"
064434ef fix(financial): grace_days + condominio_id JWT + N+1 bulk + list_with_filters + paginação + f-strings
5b03d45c feat(monitor): robustez 24h completa — logrotate + startup abrangente
aec453f5 feat(monitor): heartbeat 6h — score + tendência + infra + estatísticas + saúde dos serviços
0df8bd0c fix(security): 3 endpoints sem auth protegidos + UUID path params + rotas estáticas + bugs de dados
6ebe7bbc chore: git add -A — arquivos backend pendentes após commits anteriores
```

---

## ARQUIVOS DE AUDITORIA GERADOS
  /opt/conecta-pro/AUDITORIA_SKILL01.md  — Debugger sistemático (31/03/2026)
  /opt/conecta-pro/CODE_REVIEW_SKILL02.md — Code Review 15 pontos (31/03/2026)
  /opt/conecta-pro/AUDITORIA_SKILL03.md  — REST Design 10 critérios (31/03/2026)
  /opt/conecta-pro/AUDITORIA_SKILL04.md  — Cobertura de Testes (31/03/2026)

---

## ZONAS PROIBIDAS
alembic/versions/ · main_production.py · docker-compose*.yml · .env* · credentials/

## HOT COPY (padrão)
```bash
docker cp /opt/conecta-pro/backend/modules/[mod]/[file].py \
  $CONTAINER:/app/modules/[mod]/[file].py
docker restart $CONTAINER && sleep 8
```

## BUILD FRONTEND (serializado)
```bash
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -15
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8
```
