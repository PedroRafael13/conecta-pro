# TASK-002: Cobertura Backend — De 60% para 80%+

> Prioridade: ALTA
> Atribuído a: Kimi K2.5
> Criado por: Claude Opus 4.6 — 2026-02-09
> Status: PENDENTE

## Contexto

Os 3 test files criados na TASK-001 agora passam (44/44 PASS). Claude corrigiu:
- Bug do mapper `NotificationChannel.templates` (conftest lazy-load + remoção de relationships conflitantes)
- Testes de default values (mapped_column defaults são INSERT defaults, não Python-side)
- MCP docker removido do `/root/.kimi/mcp.json` (era isso que crashava o Kimi)

Cobertura backend atual: ~60%. Meta: 80%+.

## Objetivo

Criar testes unitários para os módulos backend com MAIS endpoints/lógica, subindo a cobertura de ~60% para 80%+.

## Regras OBRIGATÓRIAS

1. **RODAR TESTES NO CONTAINER:** `docker exec conecta-pro-backend python -m pytest /app/tests/<arquivo> -v --no-cov --tb=short`
2. **COPIAR ANTES DE TESTAR:** Após criar/editar em `/opt/conecta-pro/backend/tests/`, copiar para o container: `docker cp /opt/conecta-pro/backend/tests/<arquivo> conecta-pro-backend:/app/tests/<arquivo> && docker exec -u root conecta-pro-backend chmod 644 /app/tests/<arquivo>`
3. **ZERO FAILURES:** Todos os testes devem passar. NÃO entregar com failures.
4. **NÃO USAR `from main import app`** no topo dos testes. O conftest já faz lazy-load.
5. **mapped_column defaults são DB-side:** Para testar defaults, usar `sa_inspect(Model).columns` (ver `test_operacional_models.py` como exemplo)
6. **configure_mappers() não é necessário:** O conftest lazy-load resolve. NÃO chamar `configure_mappers()` nos testes.
7. **Imports dos models:** Importar diretamente, ex: `from modules.financial.models.invoice import Invoice`
8. **Testes de enum/constantes SÃO simples e PASSAM fácil** — comece por eles.

## Módulos Prioritários (por número de endpoints)

| Módulo | Endpoints | Prioridade |
|--------|-----------|------------|
| `modules/financial/` | 483 | ALTA |
| `modules/crm/` | ~200 | ALTA |
| `modules/hr/` | ~150 | MÉDIA |
| `modules/operacional/` | ~130 | MÉDIA (já tem testes) |

## Estratégia Sugerida

### Fase 1: Models + Enums (rápido, alta cobertura)
- Criar `test_financial_models.py` — testar models Invoice, Payment, BankAccount, etc.
- Criar `test_crm_models.py` — testar models Lead, Contact, Pipeline, etc.
- Criar `test_hr_models.py` — testar models Employee, Department, Vacation, etc.
- Foco: criação de instância, enums, propriedades calculadas

### Fase 2: Services/Utils (lógica de negócio)
- Testar funções puras (cálculos, validações, formatações)
- Usar mocks para dependências externas (DB, Redis, APIs)

### Fase 3: Verificação
- Rodar TODOS os testes juntos: `docker exec conecta-pro-backend python -m pytest /app/tests/ -v --no-cov --tb=short`
- Confirmar 0 failures
- Reportar cobertura estimada

## Exemplo de Teste Correto

```python
"""Testes para models do módulo financial."""

import pytest
from datetime import date
from uuid import uuid4

from modules.financial.models.invoice import Invoice, InvoiceStatus


class TestInvoiceModel:
    """Testes para model Invoice."""

    def test_invoice_creation(self):
        """Testa criação de instância Invoice."""
        inv = Invoice(
            id=str(uuid4()),
            number="NF-001",
            tenant_id=str(uuid4()),
        )
        assert inv.number == "NF-001"

    def test_invoice_enums(self):
        """Testa enums do Invoice."""
        assert InvoiceStatus.PENDING == "pending"
        assert InvoiceStatus.PAID == "paid"

    def test_invoice_defaults(self):
        """Testa defaults via inspeção de coluna."""
        from sqlalchemy import inspect as sa_inspect
        mapper = sa_inspect(Invoice)
        col_defaults = {}
        for col in mapper.columns:
            if col.default is not None:
                col_defaults[col.key] = col.default.arg
        assert col_defaults.get("status") == InvoiceStatus.PENDING.value
```

## Entregáveis

1. Mínimo 3 novos arquivos de teste
2. Mínimo 30 testes novos
3. 0 failures ao rodar todos juntos
4. Mensagem via `.comms/messages/kimi-out.jsonl` com relatório

## Deadline

Sem deadline fixo, mas reporte progresso a cada fase concluída.
