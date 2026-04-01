# FASE 1 — PLANO DE ROTAÇÃO DE CREDENCIAIS
**Data:** 2026-02-12T18:08Z
**Agente:** Security-Lead (claude-opus-4.6)
**Task ID:** SEC-001

---

## PRINCÍPIO: Toda credencial exposta no repositório deve ser considerada comprometida e rotacionada.

---

## 1. ROTAÇÃO P0 (IMEDIATA — bloqueador de release)

| # | Credencial | Onde está | Owner | Ação | Prazo |
|---|-----------|-----------|-------|------|-------|
| R1 | JWT_SECRET_KEY | .env, docker-compose.prod.yml, scripts/plano_execucao.sh | Jordan/SRE | Gerar novo secret (openssl rand -hex 64), atualizar .env prod, restart backend | IMEDIATO |
| R2 | POSTGRES_PASSWORD | .env, docker-compose.prod.yml | Jordan/SRE | Alterar via ALTER USER no PostgreSQL, atualizar .env e compose | IMEDIATO |
| R3 | Chaves privadas Inter (inter_key.pem, inter_api.key) | credentials/certificates/ | Jordan | Revogar no painel Inter, gerar novo par, salvar FORA do repo | IMEDIATO |
| R4 | Chaves privadas Cora (cora_api.key) | credentials/certificates/ | Jordan | Revogar no painel Cora, gerar novo par, salvar FORA do repo | IMEDIATO |
| R5 | Chave privada A1 (a1_key.pem) + certificado.pfx | credentials/certificates/ | Jordan | Verificar validade, revogar se comprometido, salvar FORA do repo | IMEDIATO |
| R6 | GOOGLE_CLIENT_SECRET | .env | Jordan | Rotacionar no Google Cloud Console, atualizar .env prod | IMEDIATO |
| R7 | GOVBR_CLIENT_SECRET | .env | Jordan | Rotacionar no portal gov.br, atualizar .env prod | IMEDIATO |
| R8 | API_TOKEN (Hostinger DNS) | deploy/update-dns.sh | Jordan | Rotacionar no painel Hostinger, remover do script, usar env var | IMEDIATO |

## 2. ROTAÇÃO P1 (URGENTE — até 48h)

| # | Credencial | Onde está | Owner | Ação | Prazo |
|---|-----------|-----------|-------|------|-------|
| R9 | OPENAI_API_KEY | .env, scripts/plano_execucao.sh | Jordan | Rotacionar no dashboard OpenAI | 48h |
| R10 | ANTHROPIC_API_KEY | .env | Jordan | Rotacionar no dashboard Anthropic | 48h |
| R11 | EVOLUTION_API_KEY | .env | Jordan | Rotacionar no painel Evolution | 48h |
| R12 | SOLIDES_API_TOKEN + WEBHOOK_SECRET | .env | Jordan | Rotacionar no painel Sólides | 48h |
| R13 | TELEGRAM_BOT_TOKEN | .env | Jordan | Revogar via @BotFather, criar novo token | 48h |
| R14 | SMTP_PASSWORD | .env | Jordan | Alterar senha no painel Hostinger email | 48h |
| R15 | REDIS_PASSWORD | docker-compose.yml, scripts/ | SRE | Alterar, atualizar compose e .env | 48h |
| R16 | CERTIFICATE_PASSWORD | .env | Jordan | Alterar se possível, documentar | 48h |

---

## 3. REMOÇÃO DO REPOSITÓRIO

### Ação 1: Adicionar ao .gitignore (IMEDIATO)
```gitignore
# Credentials and secrets
credentials/
*.pem
*.key
*.pfx
*.p12
.env.secrets
.env.credentials
```

### Ação 2: Remover arquivos tracked (IMEDIATO)
```bash
git rm --cached -r credentials/
git rm --cached .env 2>/dev/null  # se tracked
git commit -m "sec: remove credenciais e chaves do tracking git"
```

### Ação 3: Mover credenciais para local seguro
```bash
# Mover para diretório fora do repo
mkdir -p /opt/conecta-secrets/certificates
mv credentials/certificates/*.key /opt/conecta-secrets/certificates/
mv credentials/certificates/*.pem /opt/conecta-secrets/certificates/
mv credentials/certificates/*.pfx /opt/conecta-secrets/certificates/
chmod 600 /opt/conecta-secrets/certificates/*
chown root:root /opt/conecta-secrets/certificates/*
```

### Ação 4: Limpeza do histórico git (REQUER APROVAÇÃO JORDAN)
```bash
# ATENÇÃO: reescreve histórico — requer force push
# Apenas executar com aprovação explícita
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch credentials/certificates/*.key credentials/certificates/*.pem credentials/certificates/*.pfx' \
  --prune-empty -- --all
```
**Status:** AGUARDANDO APROVAÇÃO — reescrever histórico é destrutivo.

---

## 4. CORREÇÃO DO OAUTH TOKEN EM QUERY STRING

**Arquivo:** `backend/api/v1/endpoints/auth.py:466-475`

**Plano:**
1. Substituir redirect com tokens na URL por redirect com código temporário
2. Frontend recebe código, troca por tokens via POST seguro
3. Alternativa: setar tokens como cookies httpOnly no redirect

**Implementação recomendada (código temporário em Redis):**
```python
# Backend: gerar código temporário
import secrets
code = secrets.token_urlsafe(32)
redis.setex(f"oauth_code:{code}", 300, json.dumps({"access_token": ..., "refresh_token": ...}))
return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?code={code}")

# Frontend: trocar código por tokens via POST
# POST /api/v1/auth/exchange-code {code: "..."}
```

---

## 5. PREVENÇÃO RECORRENTE

### Pre-commit hook (detect-secrets)
```bash
pip install detect-secrets
detect-secrets scan > .secrets.baseline
# Adicionar ao .pre-commit-config.yaml
```

### .gitignore hardening
Adicionar patterns para prevenir futuros commits acidentais de credenciais.

---

## CRONOGRAMA RESUMO

| Fase | Ação | Responsável | Prazo |
|------|------|-------------|-------|
| 1 | .gitignore + git rm --cached | Claude (executor) | Agora |
| 2 | Mover certificados para /opt/conecta-secrets | Claude (executor) | Agora |
| 3 | Rotação P0 (JWT, DB, OAuth secrets) | Jordan (manual) | IMEDIATO |
| 4 | Rotação P1 (API keys terceiros) | Jordan (manual) | 48h |
| 5 | Fix OAuth query string | Claude (executor) | Fase 2 |
| 6 | Limpeza histórico git | Jordan (aprovação) | Após rotação |
| 7 | Pre-commit detect-secrets | Claude (executor) | Fase 1 |
