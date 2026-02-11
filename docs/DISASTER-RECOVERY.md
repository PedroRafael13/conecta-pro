# Disaster Recovery — Conecta PRO

**Última atualização:** 2026-02-11
**Autor:** Opus Executor

---

## Métricas de Recuperação

| Métrica | Valor | Justificativa |
|---------|-------|---------------|
| **RPO** (Recovery Point Objective) | 24 horas | Backup diário às 3AM UTC via cron |
| **RTO** (Recovery Time Objective) | ~15 minutos | Restore testado: < 1 min (268K gz) + rebuild containers ~10min |

---

## Backup

### Configuração Atual
- **Script:** `/opt/conecta-pro/scripts/backup_database.sh`
- **Frequência:** Diário às 3AM UTC (cron)
- **Localização:** `/opt/conecta-pro/backups/postgresql/`
- **Formato:** `backup_YYYYMMDD_HHMMSS.sql.gz` (pg_dump comprimido)
- **Retenção:** 30 dias (limpeza automática)
- **Offsite:** S3 (quando configurado via `S3_BACKUP_BUCKET`)
- **Verificação:** Integridade gzip validada automaticamente

### Teste de Backup (2026-02-11)
- Backup executado: **268K** comprimido
- Integridade gzip: **OK**
- Restore testado: **395/395 tabelas** restauradas com sucesso
- Tempo de restore: **< 1 minuto**

---

## Procedimento de Restore

### 1. Restore Completo (banco inteiro)

```bash
# Identificar último backup
BACKUP=$(ls -t /opt/conecta-pro/backups/postgresql/backup_*.sql.gz | head -1)
echo "Restaurando: $BACKUP"

# Parar aplicação
cd /opt/conecta-pro
docker compose down

# Restore
docker compose up -d postgres
sleep 5  # aguardar postgres iniciar

# Dropar e recriar banco
docker exec conecta-pro-postgres dropdb -U postgres conecta_pro --if-exists
docker exec conecta-pro-postgres createdb -U postgres conecta_pro

# Restaurar dados
gunzip -c "$BACKUP" | docker exec -i conecta-pro-postgres psql -U postgres conecta_pro

# Subir aplicação
docker compose up -d

# Verificar
bash /opt/conecta-pro/scripts/health-check.sh
```

### 2. Restore em Banco Temporário (para verificação)

```bash
BACKUP=$(ls -t /opt/conecta-pro/backups/postgresql/backup_*.sql.gz | head -1)

# Criar banco temporário
docker exec conecta-pro-postgres createdb -U postgres conecta_pro_test

# Restore
gunzip -c "$BACKUP" | docker exec -i conecta-pro-postgres psql -U postgres conecta_pro_test

# Verificar
docker exec conecta-pro-postgres psql -U postgres conecta_pro_test \
  -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"

# Limpar
docker exec conecta-pro-postgres dropdb -U postgres conecta_pro_test
```

---

## Rollback de Código

```bash
# Rollback para commit/tag específico
bash /opt/conecta-pro/scripts/rollback.sh <commit-or-tag>

# Exemplos
bash /opt/conecta-pro/scripts/rollback.sh HEAD~1
bash /opt/conecta-pro/scripts/rollback.sh v1.0.0
```

O script de rollback automaticamente:
1. Faz backup do banco antes do rollback
2. Para containers
3. Checkout para a versão alvo
4. Rebuild + restart containers
5. Executa health check

---

## Cenários de Falha

| Cenário | Ação | Tempo Estimado |
|---------|------|----------------|
| Banco corrompido | Restore do último backup | ~15 min |
| Deploy com bug | `rollback.sh HEAD~1` | ~10 min |
| Servidor caiu | Restore em novo servidor + DNS update | ~1h |
| Container crashando | `docker compose up -d --force-recreate` | ~5 min |

---

## Checklist de Validação Pós-Restore

- [ ] `health-check.sh` passa (6/6 serviços)
- [ ] Login funciona via https://erp.conectamais.pro
- [ ] Dados verificados no banco (contagem de registros)
- [ ] Logs sem erros críticos (`docker logs conecta-pro-backend --tail 50`)
