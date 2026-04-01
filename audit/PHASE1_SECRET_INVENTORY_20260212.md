# FASE 1 — INVENTÁRIO DE SEGREDOS
**Data:** 2026-02-12T18:05Z
**Agente:** Security-Lead (claude-opus-4.6)
**Task ID:** SEC-001

---

## 1. SEGREDOS EM ARQUIVOS DE CONFIGURAÇÃO

### .env (raiz do projeto)
| Linha | Variável | Tipo | Risco |
|-------|----------|------|-------|
| 22 | POSTGRES_PASSWORD | Database password | P0 |
| 33 | JWT_SECRET_KEY | JWT signing key | P0 |
| 56 | EVOLUTION_API_KEY | API key terceiro | P1 |
| 60 | GOOGLE_MAPS_API_KEY | API key Google | P1 |
| 68 | GOOGLE_CLIENT_SECRET | OAuth secret | P0 |
| 75 | SOLIDES_API_TOKEN | API token terceiro | P1 |
| 76 | SOLIDES_WEBHOOK_SECRET | Webhook secret | P1 |
| 84 | GOVBR_CLIENT_SECRET | OAuth gov.br | P0 |
| 92 | CERTIFICATE_PASSWORD | Certificado digital | P0 |
| 121 | OPENAI_API_KEY | LLM API key | P1 |
| 130 | ANTHROPIC_API_KEY | LLM API key | P1 |
| 137 | TELEGRAM_BOT_TOKEN | Bot token | P1 |
| 146 | SMTP_PASSWORD | Email password | P1 |

**Status .gitignore:** `.env` ESTÁ no .gitignore. Porém arquivo foi commitado em algum momento anterior.

### docker-compose.prod.yml
| Linha | Variável | Tipo | Risco |
|-------|----------|------|-------|
| 10 | POSTGRES_PASSWORD | Hardcoded "postgres" | P0 |
| 46 | JWT_SECRET_KEY | Hardcoded em plaintext | P0 |

### docker-compose.yml
| Linha | Variável | Tipo | Risco |
|-------|----------|------|-------|
| 11 | POSTGRES_PASSWORD | Default "postgres" | P1 |
| 35 | REDIS_PASSWORD | Default "conecta_redis_2024" | P1 |

### scripts/
| Arquivo | Linha | Variável | Risco |
|---------|-------|----------|-------|
| scripts/plano_execucao.sh | 44 | JWT_SECRET_KEY hardcoded | P0 |
| scripts/plano_execucao.sh | 45 | REDIS_PASSWORD hardcoded | P1 |
| scripts/plano_execucao.sh | 46 | OPENAI_API_KEY hardcoded | P1 |
| deploy/update-dns.sh | 14 | API_TOKEN (Hostinger) hardcoded | P0 |

### backend/core/config/settings.py
| Linha | Variável | Tipo | Risco |
|-------|----------|------|-------|
| 66 | GOOGLE_CLIENT_SECRET | Default vazio (OK) | P2 |
| 71 | OPENAI_API_KEY | Default vazio (OK) | P2 |
| 72 | ANTHROPIC_API_KEY | Default vazio (OK) | P2 |
| 81 | NFE_CERT_PASSWORD | Default vazio (OK) | P2 |
| 93 | SMTP_PASSWORD | Default vazio (OK) | P2 |

---

## 2. CERTIFICADOS E CHAVES PRIVADAS (TRACKED no git)

**CRÍTICO:** 14 arquivos em `credentials/` estão versionados (git ls-files confirma):

| Arquivo | Tipo | Risco |
|---------|------|-------|
| credentials/certificates/inter_key.pem | Chave privada Inter API | P0 |
| credentials/certificates/inter_api.key | Chave privada Inter API | P0 |
| credentials/certificates/a1_key.pem | Chave privada certificado A1 | P0 |
| credentials/certificates/cora_api.key | Chave privada Cora API | P0 |
| credentials/certificates/certificado.pfx | Certificado digital completo | P0 |
| credentials/certificates/inter_cert.pem | Certificado Inter (público) | P2 |
| credentials/certificates/inter_api.crt | Certificado Inter (público) | P2 |
| credentials/certificates/a1_cert.pem | Certificado A1 (público) | P2 |
| credentials/certificates/cora_api.crt | Certificado Cora (público) | P2 |
| credentials/certificates/ca.crt | CA root (público) | P2 |
| credentials/certificates/*.zip | Pacotes com chaves | P0 |
| credentials/.env.credentials | Credenciais adicionais | P0 |

---

## 3. OAUTH TOKEN EM QUERY STRING

**Arquivo:** `backend/api/v1/endpoints/auth.py`
**Linhas:** 466-475

```python
redirect_params = urlencode({
    "access_token": jwt_access_token,
    "refresh_token": jwt_refresh_token,
    "token_type": "bearer",
})
return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?{redirect_params}")
```

**Risco:** Tokens JWT (access + refresh) passados via query string. Vazam em:
- Logs do servidor/proxy (nginx access log)
- Browser history
- HTTP Referer header
- Analytics/tracking scripts

---

## 4. HISTÓRICO GIT

Commits que adicionaram arquivos sensíveis:
- `0c316577` — feat(operacional): adicionou .env e integrações
- `5e25ecc5` — feat: adicionou certificados Inter e Cora

**Status:** Arquivos sensíveis existem no histórico git mesmo se removidos do working tree.

---

## 5. STATUS DO .gitignore

| Pattern | Presente | Protege |
|---------|----------|---------|
| `.env` | ✅ SIM | Arquivo .env raiz |
| `.env.local` | ✅ SIM | Env local |
| `backend/.env.*` | ✅ SIM | Envs backend |
| `credentials/` | ❌ NÃO | Certificados/chaves |
| `*.pem` | ❌ NÃO | Chaves PEM |
| `*.key` | ❌ NÃO | Chaves privadas |
| `*.pfx` | ❌ NÃO | Certificados PKCS12 |

---

## RESUMO POR PRIORIDADE

| Prioridade | Quantidade | Descrição |
|------------|-----------|-----------|
| **P0** | 12 | JWT secret hardcoded, chaves privadas tracked, API token DNS, certificado digital, OAuth creds |
| **P1** | 8 | API keys terceiros, passwords default, tokens LLM |
| **P2** | 7 | Certificados públicos, defaults vazios em settings.py |
| **TOTAL** | 27 | |
