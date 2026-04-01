# Patches de Segurança - Conecta PRO

> Correções para vulnerabilidades críticas identificadas na auditoria de segurança

---

## 🚨 ATENÇÃO

**Estes patches devem ser aplicados em ordem e com cuidado.**

- Faça backup completo antes de aplicar
- Teste em ambiente de staging primeiro
- Siga os checklists de verificação de cada patch

---

## 📋 Índice de Patches

| Patch | Descrição | Severidade | Tempo Est. | Status |
|-------|-----------|------------|------------|--------|
| [PATCH 01](#patch-01) | Atualização de Dependências CVE | 🔴 **CRÍTICO** | 30 min | Pronto |
| [PATCH 02](#patch-02) | SQL Injection - Whitelist | 🔴 **CRÍTICO** | 2 horas | Pronto |
| [PATCH 03](#patch-03) | Endpoint LGPD | 🔴 **CRÍTICO** | 4 horas | Pronto |
| [PATCH 04](#patch-04) | Mascaramento em Logs | 🟠 **ALTO** | 2 horas | Pronto |
| [PATCH 05](#patch-05) | Configurações Docker | 🟠 **ALTO** | 1 hora | Pronto |

---

## PATCH 01: Atualização de Dependências CVE

**Arquivos:**
- `PATCH_01_DEPENDENCIES.sh` - Script de atualização
- `PATCH_01_VERIFICATION.md` - Checklist de validação

### Vulnerabilidades Corrigidas

| CVE | Pacote | Impacto |
|-----|--------|---------|
| CVE-2024-33663 | python-jose 3.3.0 | Algorithm confusion (bypass auth) |
| CVE-2024-33664 | python-jose 3.3.0 | JWT Bomb (DoS) |
| CVE-2025-66478 | Next.js 16.1.3 | Remote Code Execution |
| CVE-2025-55182 | React 19.2.3 | React2Shell RCE |

### Aplicação

```bash
# 1. Execute o script
cd /opt/conecta-pro/docs/patches
chmod +x PATCH_01_DEPENDENCIES.sh
./PATCH_01_DEPENDENCIES.sh

# 2. Siga o checklist em PATCH_01_VERIFICATION.md
```

### Rollback

```bash
# Se necessário, restore o backup
BACKUP_DIR="/opt/conecta-pro/docs/patches/backups_YYYYMMDD_HHMMSS"
cp "$BACKUP_DIR/requirements.txt.bak" /opt/conecta-pro/backend/requirements.txt
cp "$BACKUP_DIR/package.json.bak" /opt/conecta-pro/frontend/package.json
cd /opt/conecta-pro/backend && pip install -r requirements.txt
cd /opt/conecta-pro/frontend && npm install
```

---

## PATCH 02: SQL Injection - Whitelist de Tabelas

**Arquivo:** `PATCH_02_SQL_INJECTION.py`

### Vulnerabilidade

Queries dinâmicas em ETL e LGPD permitem SQL Injection via nomes de tabelas:
```python
query = text(f"SELECT * FROM {table_name} WHERE id = :id")  # ❌ Inseguro
```

### Solução

Módulo `SQLTableValidator` com whitelist de tabelas permitidas.

### Aplicação

1. Copie o módulo para o projeto:
```bash
cp /opt/conecta-pro/docs/patches/PATCH_02_SQL_INJECTION.py \
   /opt/conecta-pro/backend/core/security/sql_validator.py
```

2. Modifique os arquivos afetados (veja instruções no arquivo):
- `deduplicator.py`
- `lgpd_compliance.py`
- `document_versioning.py`

### Uso

```python
from core.security.sql_validator import validate_table_name

# Antes
table_name = user_input  # ❌ Inseguro
query = text(f"SELECT * FROM {table_name} WHERE id = :id")

# Depois
from core.security.sql_validator import validate_table_name
validate_table_name(table_name)  # ✅ Valida contra whitelist
query = text(f"SELECT * FROM {table_name} WHERE id = :id")
```

---

## PATCH 03: Endpoint LGPD - Exclusão de Dados

**Arquivo:** `PATCH_03_LGPD_ENDPOINT.py`

### Funcionalidades

Implementa direitos do titular LGPD:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/me/export` | GET | Portabilidade de dados (JSON) |
| `/api/v1/me/anonymize` | POST | Anonimização de dados |
| `/api/v1/me/` | DELETE | Exclusão com anonimização |

### Regras de Negócio

- **CPF:** `123.456.789-00` → `***.456.789-**`
- **Email:** `joao@empresa.com` → `j***@empresa.com`
- **Nome:** `João Silva` → `ANONIMIZADO_XXXXXXXX`
- **Dados fiscais:** Preservados (obrigação legal) com máscara

### Aplicação

1. Copie o arquivo para o módulo LGPD:
```bash
mkdir -p /opt/conecta-pro/backend/modules/lgpd/routes
cp /opt/conecta-pro/docs/patches/PATCH_03_LGPD_ENDPOINT.py \
   /opt/conecta-pro/backend/modules/lgpd/routes/delete_me.py
```

2. Adicione o router em `main.py`:
```python
from modules.lgpd.routes.delete_me import router as lgpd_router
app.include_router(lgpd_router)
```

3. Execute migrations para adicionar campos necessários:
```bash
cd /opt/conecta-pro/backend
alembic revision -m "Add anonymized_at field to users"
# Edite a migration para adicionar:
# - users.anonymized_at (timestamp)
# - users.original_name_hash (string)
alembic upgrade head
```

---

## PATCH 04: Mascaramento de PII em Logs

**Arquivo:** `PATCH_04_LOG_MASKING.py`

### Funcionalidades

- Máscara automática de CPF, CNPJ, email, telefone
- Filtro para Loguru
- Middleware FastAPI para sanitização
- Decorator para funções de logging

### Aplicação

1. Copie o módulo:
```bash
cp /opt/conecta-pro/docs/patches/PATCH_04_LOG_MASKING.py \
   /opt/conecta-pro/backend/core/security/log_masking.py
```

2. Integre ao logging:
```python
# core/logging/__init__.py
from core.security.log_masking import SecureLogFilter

# Configure loguru com filtro
logger.add("app.log", filter=SecureLogFilter())
```

3. Use nas funções de log:
```python
from core.security.log_masking import LogMasker

# Máscara em strings
logger.info(f"User {LogMasker.mask_cpf(cpf)} logged in")

# Máscara em dicionários
logger.info("User data", extra=LogMasker.mask_dict(user_data))
```

---

## PATCH 05: Configurações Docker

**Arquivos:**
- `PATCH_05_DOCKER_SECURITY.yml` - Docker Compose seguro
- `PATCH_05_ENV_SECURITY.md` - Template de variáveis
- `PATCH_05_CORS_CONFIG.py` - Configuração CORS

### Melhorias

| Aspecto | Antes | Depois |
|---------|-------|--------|
| PostgreSQL | Porta exposta | Somente rede interna |
| Redis | Sem senha | Senha obrigatória |
| Network | Default | Bridge isolada |
| Recursos | Ilimitado | Limits e reservations |
| Privilégios | Root | no-new-privileges |

### Aplicação

1. Faça backup do docker-compose atual
2. Revise o novo arquivo e adapte as variáveis
3. Aplique as mudanças:
```bash
cd /opt/conecta-pro
docker-compose down
cp docker-compose.yml docker-compose.yml.pre-security
cp docs/patches/PATCH_05_DOCKER_SECURITY.yml docker-compose.yml
# Configure as variáveis em .env
docker-compose up -d
```

---

## 📊 Ordem de Aplicação Recomendada

```
Dia 1 (Crítico):
├── PATCH 01 (30 min)
├── PATCH 02 (2 horas)
└── PATCH 03 (4 horas)

Dia 2 (Alto):
├── PATCH 04 (2 horas)
└── PATCH 05 (1 hora)

Dia 3 (Validação):
└── Testes completos de regressão
```

---

## ✅ Checklist Final de Aplicação

Após aplicar todos os patches:

- [ ] Aplicação inicia sem erros
- [ ] Testes unitários passam
- [ ] Testes E2E passam
- [ ] Login JWT funciona (PATCH 01)
- [ ] Exportação LGPD funciona (PATCH 03)
- [ ] Logs não expõem CPF/email (PATCH 04)
- [ ] PostgreSQL não acessível externamente (PATCH 05)
- [ ] Redis requer senha (PATCH 05)
- [ ] `npm audit` sem vulnerabilidades críticas
- [ ] `pip-audit` sem vulnerabilidades críticas

---

## 📞 Suporte

Em caso de problemas:

1. Consulte o documento de verificação específico
2. Verifique backups em `/docs/patches/backups_*`
3. Consulte a documentação de segurança:
   - `/docs/SECURITY_INDEX.md`
   - `/docs/SECURITY_CODE_AUDIT.md`
   - `/docs/LGPD_COMPLIANCE.md`

---

**Data de Geração:** 2026-02-05
**Versão:** 1.0
**Status:** Pronto para aplicação
