# INSTRUÇÕES CLAUDE — Plano de Deploy para Produção

**Papel:** Auditor e Coordenador
**Branch:** feature/openclaw-v2
**Plano completo:** `/opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md`

---

## SEU PAPEL

Você NÃO executa. Você:
1. **Monitora** progresso de Kimi e Opus via `.comms/messages/`
2. **Valida** entregáveis de cada fase (review de scripts, configs)
3. **Reporta** problemas ao Jordan
4. **Coordena** a Fase 8 (staging deploy) e Fase 9 (validação final)
5. **Executa** SOMENTE quando Jordan autoriza explicitamente

---

## CHECKLIST DE AUDITORIA POR FASE

### Fase 1 (Opus): Scripts deploy/rollback
- [ ] `deploy.sh` existe e tem syntax válida (`bash -n`)
- [ ] `rollback.sh` existe e aceita argumento
- [ ] `health-check.sh` verifica todos os serviços
- [ ] Scripts são idempotentes
- [ ] Nenhuma credencial hardcoded nos scripts
- [ ] Chmod 755

### Fase 2 (Opus): Segurança
- [ ] `.env` tem chmod 600
- [ ] `.env` está no .gitignore
- [ ] `.env` nunca foi commitado (`git log --all -- .env`)
- [ ] `backup_database.sh` sem credentials hardcoded
- [ ] CORS não tem `*` para produção

### Fase 3 (Kimi): AlertManager
- [ ] `alertmanager.yml` existe e é válido
- [ ] Adicionado ao docker-compose monitoring
- [ ] Prometheus aponta para alertmanager:9093
- [ ] `erp_alerts.yml` carrega corretamente
- [ ] NÃO tocou em código da aplicação

### Fase 4 (Kimi): Logrotate
- [ ] `/etc/logrotate.d/conecta-pro` existe
- [ ] Loki retention configurado (30 dias)
- [ ] Dry-run sem erros

### Fase 5 (Opus): Backup/DR
- [ ] Backup executado com sucesso
- [ ] Restore testado e tabelas conferem
- [ ] Cron configurado (3AM diário)
- [ ] RTO/RPO documentados

### Fase 6 (Kimi): Load Test
- [ ] k6 instalado
- [ ] Cenários criados e revisados
- [ ] Resultados dentro dos thresholds (P95 < 500ms, error < 1%)
- [ ] Documentação criada

### Fase 7 (Jordan + Opus): DNS/SSL
- [ ] DNS propagado (dig erp.conectamais.pro)
- [ ] SSL válido (curl -I https://erp.conectamais.pro)
- [ ] Auto-renovação funciona (certbot renew --dry-run)

### Fase 8: Staging Deploy
- [ ] Todos os containers UP e healthy
- [ ] Health checks passando
- [ ] Migrações rodaram sem erro
- [ ] E2E manual OK

### Fase 9: Validação Final (triple-verified)
- [ ] 15/15 checks PASS — Claude
- [ ] 15/15 checks PASS — Kimi
- [ ] 15/15 checks PASS — Opus

---

## SWEEP DE MONITORAMENTO

A cada ~20 minutos:
```bash
# Verificar mensagens de Kimi e Opus
tail -5 /opt/conecta-pro/.comms/messages/kimi-out.jsonl
tail -5 /opt/conecta-pro/.comms/messages/opus-exec-out.jsonl

# Verificar commits recentes
cd /opt/conecta-pro && git log --oneline -5

# Verificar que código não foi tocado
git diff --stat HEAD -- backend/routers/ backend/models/ backend/services/ frontend/src/
# Deve ser vazio (só infra foi tocada)
```

---

## VALIDAÇÃO FINAL — 15 Checks

Quando Fase 8 concluir, rodar:

```bash
# 1. Containers UP
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. Backend health
curl -sf http://localhost:8080/health | python3 -m json.tool

# 3. Frontend health
curl -sf -o /dev/null -w "%{http_code}" http://localhost:3001

# 4. PostgreSQL
docker exec conecta-pro-postgres pg_isready -U postgres

# 5. Redis
docker exec conecta-pro-redis redis-cli ping

# 6. Alembic head
cd /opt/conecta-pro/backend && source venv/bin/activate && alembic heads

# 7. SSL (se DNS configurado)
curl -I https://erp.conectamais.pro 2>/dev/null | head -5

# 8. Prometheus
curl -sf http://localhost:9090/-/ready

# 9. Grafana
curl -sf -o /dev/null -w "%{http_code}" http://localhost:3000/api/health

# 10. AlertManager
curl -sf http://localhost:9093/-/ready

# 11. Backup testado
ls -la /opt/conecta-pro/backups/postgresql/ 2>/dev/null | head -3

# 12. Logrotate
logrotate -d /etc/logrotate.d/conecta-pro 2>&1 | tail -3

# 13. Cron backup
crontab -l 2>/dev/null | grep backup

# 14. Certbot renewal (se SSL ativo)
certbot renew --dry-run 2>&1 | tail -3

# 15. Load test P95
grep "p(95)" /opt/conecta-pro/logs/load-test-results.txt 2>/dev/null || echo "Pendente"
```
