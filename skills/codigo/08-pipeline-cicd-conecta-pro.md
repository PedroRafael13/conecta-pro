---
name: pipeline-cicd-conecta-pro
description: Protocolo de deploy, versionamento e automação para o Conecta PRO. Inclui padrão de commit, hot copy, build serializado, rollback e GitHub Actions. Usar em toda sessão de desenvolvimento para garantir rastreabilidade e deploys seguros.
---

# Pipeline CI/CD — Conecta PRO

## Repositório
- GitHub: https://github.com/jjesus1982/conecta-pro
- Branch ativa: `feature/people-management-reorganization`
- Deploy: push → VPS via git pull + hot copy

## Quando usar
- Final de cada sessão de desenvolvimento — commit + push
- Antes de cada modificação — garantir estado limpo
- Após cada fix — commit descritivo imediato
- Para rollback de um deploy com problema

## Padrão de commit obrigatório

```bash
cd /opt/conecta-pro

# Ver o que mudou antes de commitar
git status
git diff --stat

# Commit com mensagem descritiva (padrão Conventional Commits)
# feat(modulo): descrição da nova funcionalidade
# fix(modulo): descrição do bug corrigido
# refactor(modulo): descrição da refatoração
# chore: atualização de dependências ou config

git add -A
git commit -m "fix(ged): dropdown clientes vazio no modal Novo Kit — useEffect com isOpen"
git push origin feature/people-management-reorganization

# Verificar que foi enviado
git log --oneline -3
```

## Exemplos de mensagens de commit do Conecta PRO

```bash
# ✅ BONS commits (descritivos, rastreáveis)
git commit -m "fix(financeiro): status 'pago' → 'paga' — AI Command Center mostrava R$ 258k falso"
git commit -m "feat(ged): endpoint /ged/config/schedule + /ged/reports/monthly criados"
git commit -m "fix(bartolo): guard _is_query_not_action — palavra solta nunca abre modal"
git commit -m "fix(frontend): modal Novo Kit — dropdown clientes com useEffect(isOpen)"
git commit -m "feat(cct): 52/52 funcionários vinculados CCT 2026 SINDECOMPRESTS"

# ❌ RUINS (impossível rastrear)
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

## Deploy seguro — protocolo completo

```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# PASSO 1 — Garantir estado limpo antes de qualquer mudança
cd /opt/conecta-pro
git status
git log --oneline -3

# PASSO 2 — Fazer a mudança necessária
# [implementar o fix]

# PASSO 3 — Hot copy do backend (nunca rebuild completo no dia a dia)
docker cp /opt/conecta-pro/backend/modules/[modulo]/[arquivo].py \
  $CONTAINER:/app/modules/[modulo]/[arquivo].py
docker restart $CONTAINER && sleep 8

# PASSO 4 — Validar backend
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -sf -o /dev/null -w "Backend: %{http_code}\n" \
  "http://127.0.0.1:8080/api/v1/[endpoint]" \
  -H "Authorization: Bearer $TOKEN"

# PASSO 5 — Build frontend SE houve mudança no frontend
# (SERIALIZADO — nunca dois builds ao mesmo tempo)
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -15
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8

# PASSO 6 — Commitar e pushar
cd /opt/conecta-pro
git add -A
git commit -m "fix([modulo]): [descrição precisa do que foi corrigido]"
git push origin feature/people-management-reorganization

echo "✅ Deploy concluído"
git log --oneline -3
```

## Rollback rápido

```bash
# Ver commits recentes para escolher ponto de rollback
git log --oneline -10

# Rollback de um commit específico (sem perder histórico)
git revert [hash_do_commit] --no-edit
git push origin feature/people-management-reorganization

# Rollback de arquivo específico para versão anterior
git checkout [hash_do_commit] -- backend/modules/[modulo]/[arquivo].py
docker cp /opt/conecta-pro/backend/modules/[modulo]/[arquivo].py \
  $CONTAINER:/app/modules/[modulo]/[arquivo].py
docker restart $CONTAINER && sleep 8

# Verificar que o rollback funcionou
curl -sf -o /dev/null -w "Status após rollback: %{http_code}\n" \
  "http://127.0.0.1:8080/api/v1/[endpoint]" \
  -H "Authorization: Bearer $TOKEN"
```

## GitHub Actions — workflow de validação

```yaml
# .github/workflows/validate.yml
name: Validar Conecta PRO

on:
  push:
    branches: [feature/people-management-reorganization]
  pull_request:
    branches: [main]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pylint
      - run: pylint backend/modules/ --score=yes
        continue-on-error: true

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
        continue-on-error: true

  check-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
        env:
          NODE_OPTIONS: --max-old-space-size=4096
```

## Estado atual do repositório

```bash
# Ver branches
git branch -a | head -10

# Ver arquivos modificados não commitados
git status --short

# Ver tamanho do repositório
du -sh /opt/conecta-pro/.git

# Limpar arquivos temporários (seguro)
find /opt/conecta-pro -name "*.pyc" -delete
find /opt/conecta-pro -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /opt/conecta-pro -name ".next" -type d | head -3
```
