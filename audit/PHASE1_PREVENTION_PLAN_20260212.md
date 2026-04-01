# FASE 1 — PLANO DE PREVENÇÃO
**Data:** 2026-02-12T18:20Z
**Agente:** Security-Lead (claude-opus-4.6)
**Task ID:** SEC-003

---

## 1. PRE-COMMIT HOOKS (JÁ ATIVO)

### Hooks de segurança em `.pre-commit-config.yaml`:
| Hook | Repo | Função | Status |
|------|------|--------|--------|
| detect-private-key | pre-commit-hooks | Bloqueia chaves privadas | ✅ Ativo |
| gitleaks | gitleaks/gitleaks v8.21.2 | Scanner de secrets amplo | ✅ Ativo |
| detect-secrets | Yelp/detect-secrets v1.5.0 | Scanner com baseline | ✅ Adicionado |
| bandit | PyCQA/bandit 1.8.3 | SAST Python | ✅ Ativo |

### Baseline de secrets:
- Arquivo: `.secrets.baseline` (gerado por detect-secrets scan)
- Escopo: .env, docker-compose*.yml, scripts/, deploy/, settings.py
- Atualizar com: `detect-secrets scan --update .secrets.baseline`

## 2. .GITIGNORE HARDENING (JÁ APLICADO)

Patterns adicionados:
```
credentials/
*.pem
*.key
*.pfx
*.p12
.env.secrets
.env.credentials
.env.mcp
```

## 3. DOCKER-COMPOSE PROD (JÁ APLICADO)

- Todos os secrets via `${VAR:?required}` — compose falha se variável não definida
- Zero secrets hardcoded

## 4. RECOMENDAÇÕES FUTURAS

### 4.1. CI/CD Secret Scanning
- Adicionar step de `gitleaks detect` no pipeline CI
- Falhar build se secrets detectados

### 4.2. Secret Manager
- Migrar de .env para HashiCorp Vault ou AWS Secrets Manager
- Prioridade: JWT_SECRET_KEY, POSTGRES_PASSWORD, API keys

### 4.3. Rotação automática
- Implementar rotação periódica de JWT_SECRET_KEY (ex: 90 dias)
- Alertar via Discord/Telegram quando certificados expirarem (30 dias antes)

### 4.4. Auditoria periódica
- Scan mensal com detect-secrets + gitleaks em todo o repo
- Revisão trimestral de permissões e API keys ativas
