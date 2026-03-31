---
name: modelagem-banco-conecta-pro
description: Auditoria e boas práticas de modelagem de banco de dados para o PostgreSQL do Conecta PRO. Usar para diagnosticar queries lentas, auditar tabelas problemáticas, criar índices necessários e garantir integridade dos dados do ERP.
---

# Modelagem de Banco de Dados — Conecta PRO

## Contexto
- Banco: PostgreSQL (dentro do Docker conecta-pro-backend)
- ORM: SQLAlchemy (modelos em /opt/conecta-pro/backend/modules/)
- Migrações: Alembic (ZONA PROIBIDA — nunca editar /alembic/versions/)
- Banco: `conectapro`
- User: `postgres`

## Quando usar
- Queries retornam dados errados — verificar schema real
- Endpoint demora mais de 500ms — verificar índices
- Dados inconsistentes entre módulos — verificar foreign keys
- Antes de criar novo modelo — verificar se tabela já existe

## Comandos de diagnóstico

```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Listar TODAS as tabelas com contagem de registros
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  schemaname,
  tablename,
  n_live_tup as registros
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;" 2>/dev/null

# Ver estrutura de uma tabela específica
docker exec $CONTAINER psql -U postgres -d conectapro -c "
\d+ [nome_da_tabela]" 2>/dev/null

# Ver todos os índices
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;" 2>/dev/null

# Verificar foreign keys quebradas
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  conname as constraint_name,
  conrelid::regclass as tabela,
  confrelid::regclass as referencia
FROM pg_constraint
WHERE contype = 'f'
ORDER BY tabela;" 2>/dev/null

# Queries mais lentas (precisa pg_stat_statements ativo)
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT
  LEFT(query, 80) as query,
  calls,
  ROUND(mean_exec_time::numeric, 2) as media_ms,
  ROUND(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
WHERE mean_exec_time > 50
ORDER BY mean_exec_time DESC
LIMIT 10;" 2>/dev/null
```

## Tabelas críticas do Conecta PRO

```bash
# Verificar estrutura das tabelas mais importantes
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

for TABELA in \
  "employees" \
  "clients" \
  "ged_document_kits" \
  "ged_clients" \
  "ged_documents" \
  "receivable_accounts" \
  "payable_accounts" \
  "escalas" \
  "postos" \
  "ocorrencias"; do
  echo "=== $TABELA ==="
  docker exec $CONTAINER psql -U postgres -d conectapro -t -c \
    "SELECT COUNT(*) FROM $TABELA;" 2>/dev/null \
    || echo "Tabela não existe"
done
```

## Diagnóstico de dados inconsistentes

```bash
# Verificar status inconsistentes em contas a receber
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT DISTINCT status, COUNT(*) as qtd
FROM receivable_accounts
GROUP BY status ORDER BY qtd DESC;"

# Verificar status inconsistentes em contas a pagar
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT DISTINCT status, COUNT(*) as qtd
FROM payable_accounts
GROUP BY status ORDER BY qtd DESC;"

# Verificar funcionários sem CCT vinculada
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT COUNT(*) as sem_cct
FROM employees
WHERE status = 'ativo' AND cct_cargo_id IS NULL;"

# Verificar kits sem cliente vinculado
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT COUNT(*) as kits_sem_cliente
FROM ged_document_kits gk
LEFT JOIN ged_clients gc ON gk.client_id = gc.id
WHERE gc.id IS NULL;"
```

## Criar índices para performance

```bash
# Índices recomendados para o Conecta PRO
docker exec $CONTAINER psql -U postgres -d conectapro -c "
-- Índice para busca de kits por cliente
CREATE INDEX IF NOT EXISTS idx_ged_kits_client_id
ON ged_document_kits(client_id);

-- Índice para busca de documentos por kit
CREATE INDEX IF NOT EXISTS idx_ged_docs_kit_id
ON ged_documents(kit_id);

-- Índice para contas a receber por status e vencimento
CREATE INDEX IF NOT EXISTS idx_receivables_status_due
ON receivable_accounts(status, due_date)
WHERE status NOT IN ('paga', 'pago', 'cancelada');

-- Índice para funcionários ativos por cargo
CREATE INDEX IF NOT EXISTS idx_employees_status_role
ON employees(status, role)
WHERE status = 'ativo';

-- Índice para ocorrências por data
CREATE INDEX IF NOT EXISTS idx_ocorrencias_created
ON ocorrencias(created_at DESC);

ANALYZE;
" 2>/dev/null
echo "✅ Índices criados"
```

## Padrão de modelo SQLAlchemy para novos módulos

```python
# /opt/conecta-pro/backend/modules/[modulo]/models/[modelo].py
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class NovoModelo(Base):
    __tablename__ = "novo_modelos"

    # IDs sempre UUID
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4)

    # Foreign keys com ON DELETE CASCADE quando faz sentido
    client_id = Column(UUID(as_uuid=True),
                       ForeignKey("clients.id", ondelete="CASCADE"),
                       nullable=False)

    # Status como Enum — nunca string livre
    status = Column(
        Enum("ativo", "inativo", "pendente", name="novo_modelo_status"),
        default="ativo", nullable=False
    )

    # Timestamps sempre com timezone
    created_at = Column(DateTime(timezone=True),
                        default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relacionamentos
    client = relationship("Client", back_populates="novo_modelos")
```

## Backup antes de alterar dados

```bash
# SEMPRE fazer backup antes de UPDATE/DELETE em produção
docker exec $CONTAINER psql -U postgres -d conectapro -c "
CREATE TABLE [tabela]_backup_$(date +%Y%m%d) AS
SELECT * FROM [tabela];"

# Restaurar se necessário
docker exec $CONTAINER psql -U postgres -d conectapro -c "
INSERT INTO [tabela]
SELECT * FROM [tabela]_backup_[data]
WHERE id NOT IN (SELECT id FROM [tabela]);"
```
