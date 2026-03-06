# FASE 1 — PROGRESSO DE REMEDIAÇÃO
**Data:** 2026-02-12T18:20Z
**Agente:** Security-Lead (claude-opus-4.6)
**Task ID:** SEC-003

---

## AÇÕES EXECUTADAS

### 1. .gitignore hardening ✅
**Arquivo:** `/opt/conecta-pro/.gitignore`
**Adicionado:**
```gitignore
credentials/
*.pem
*.key
*.pfx
*.p12
.env.secrets
.env.credentials
.env.mcp
*.crt.key
```

### 2. Remoção de credenciais do git tracking ✅
**Comando:** `git rm --cached -r credentials/`
**Resultado:** 14 arquivos removidos do tracking
```
rm 'credentials/.env.credentials'
rm 'credentials/certificates/Certificado_Webhook.zip'
rm 'credentials/certificates/Inter_API-Chave_e_Certificado.zip'
rm 'credentials/certificates/a1_cert.pem'
rm 'credentials/certificates/a1_key.pem'
rm 'credentials/certificates/ca.crt'
rm 'credentials/certificates/cert_key_cora_production_2026_01_16.zip'
rm 'credentials/certificates/certificado.pfx'
rm 'credentials/certificates/cora_api.crt'
rm 'credentials/certificates/cora_api.key'
rm 'credentials/certificates/inter_api.crt'
rm 'credentials/certificates/inter_api.key'
rm 'credentials/certificates/inter_cert.pem'
rm 'credentials/certificates/inter_key.pem'
```
**Verificação:** `git ls-files -- credentials/ | wc -l` = **0**

### 3. Backup de chaves privadas em local seguro ✅
**Destino:** `/opt/conecta-secrets/certificates/`
**Permissões:** `chmod 600`, `chown root:root`
**Arquivos copiados:**
- a1_key.pem
- certificado.pfx
- cora_api.key
- inter_api.key
- inter_key.pem

### 4. Remoção de secrets hardcoded do docker-compose.prod.yml ✅
**Antes:**
```yaml
POSTGRES_PASSWORD: postgres
JWT_SECRET_KEY=qYKv60f...
command: redis-server --requirepass redis_secret_2024
```
**Depois:**
```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}
JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY required}
command: redis-server --requirepass ${REDIS_PASSWORD:?REDIS_PASSWORD required}
```
**Verificação:** 0 secrets hardcoded, tudo via env vars com validação `:?required`

### 5. deploy/update-dns.sh ✅ (já estava correto)
API_TOKEN já usava `${HOSTINGER_API_TOKEN:-}` — sem hardcoded.

### 6. scripts/plano_execucao.sh ✅ (já estava correto)
Script de rotação que GERA novos secrets dinamicamente — sem hardcoded permanente.

---

## AÇÕES PENDENTES (requer Jordan)

| # | Ação | Motivo |
|---|------|--------|
| 1 | Rotação efetiva de JWT_SECRET_KEY em produção | Requer restart backend |
| 2 | Rotação de POSTGRES_PASSWORD | Requer ALTER USER no PostgreSQL |
| 3 | Rotação de chaves Inter/Cora/A1 | Requer acesso aos painéis dos bancos |
| 4 | Rotação de API keys terceiros (OpenAI, Anthropic, etc.) | Requer acesso dashboards |
| 5 | Limpeza do histórico git | Requer aprovação explícita (force push) |

---

## GATE A — STATUS ATUALIZADO

| Critério | Antes | Agora |
|----------|-------|-------|
| Credenciais tracked no git | 14 arquivos | **0** |
| Secrets hardcoded no compose | 3 valores | **0** (env vars) |
| .gitignore protege secrets | Parcial | **Completo** |
| Chaves privadas com backup | Não | **Sim** (/opt/conecta-secrets/) |
| Prevenção pre-commit | detect-private-key + gitleaks | **+ detect-secrets** |

**Gate A parcialmente resolvido.** Falta: rotação efetiva (Jordan) + limpeza histórico (aprovação).
