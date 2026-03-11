# Reorganizacao Backend — Guia de Migracao

Data: 2026-03-11 | De 35 modulos para 9 agregadores | URLs de API inalteradas

## 1. Visao Geral

O backend foi reorganizado de ~35 modulos independentes para **9 modulos agregadores**.
Cada agregador e um `__init__.py` que re-exporta routers dos modulos de implementacao originais.
Nenhuma URL de API mudou. O codigo de implementacao permanece no local original.

## 2. Mapeamento: Modulos Antigos -> Agregadores

| Agregador | Modulos de implementacao |
|---|---|
| `comercial` | crm, clients, bidding, services |
| `operacoes` | operacional (core, ai, communication, diaristas, disciplinary, inspection_rounds, occurrences, vacations, websockets), campo |
| `tecnico` | equipment_management, document_kits |
| `pessoas` | recruitment, retention, reimbursement, ged, health_occupational |
| `financeiro` | financial (core, bi_dashboard) |
| `fiscal_contabil` | empresas, fiscal, government_integrations |
| `inteligencia` | ai/bartolo, analytics, reports, monitoring |
| `gestao` | config, audit, notifications, mobile, automation/workflows, integrations |
| `cadastros` | (reservado — sera populado gradualmente) |

## 3. Como Funciona — Aggregator Pattern

Cada agregador (`modules/<agregador>/__init__.py`) faz apenas imports e re-exports:

```python
# modules/comercial/__init__.py
from modules.crm.controllers import lead_router as crm_lead_router
from modules.clients.controllers import router as client_router
# ...
__all__ = ["crm_lead_router", "client_router", ...]
```

O codigo real (models, services, controllers) **permanece** nos modulos originais.
O agregador e apenas um ponto de entrada unificado.

## 4. Regras de Importacao

**Em producao (main.py, routers):**
```python
# CORRETO — importar do agregador
from modules.comercial import crm_lead_router
from modules.operacoes import employee_router, allocation_router
from modules.financeiro import payable_router, receivable_router

# EVITAR — import direto do modulo de implementacao
from modules.crm.controllers import lead_router  # funciona, mas nao recomendado
```

**Dentro dos modulos de implementacao:** imports internos continuam normais.
```python
# Dentro de modules/crm/controllers.py — sem mudanca
from modules.crm.models import Lead
from modules.crm.services import LeadService
```

## 5. Modulos Removidos

| Modulo | Motivo |
|---|---|
| `guardian` | Pertencia ao Conecta PLUS (produto separado). Routers, models e services removidos. |
| `search` | Busca global — funcionalidade nao utilizada. Removido. |
| `fase5` | Experimental/prototipo — deprecado e removido. |

Nenhuma API publica dependia desses modulos. Se algum import quebrar, remova a referencia.

## 6. Aliases e Deprecacao

Imports antigos dos modulos de implementacao **continuam funcionando** por compatibilidade.
Prazo de deprecacao: **60 dias (ate 2026-05-10)**.

Apos essa data, apenas imports via agregador serao suportados.
Ate la, migre gradualmente:

```python
# ANTES (deprecado em 60 dias)
from modules.crm.controllers import lead_router

# DEPOIS (recomendado)
from modules.comercial import crm_lead_router
```

## 7. Guardian Cleanup

O modulo `guardian` foi completamente removido:
- Controllers, models, services, migrations — tudo deletado
- Referencia em `main.py` removida
- Pertencia ao produto Conecta PLUS (monitoramento 24h), que tem repositorio proprio
- Se encontrar imports de `modules.guardian`, remova-os

## 8. Como Adicionar Novo Router

1. Crie o router no modulo de implementacao existente:
   ```python
   # modules/crm/controllers.py
   new_router = APIRouter(prefix="/crm/campaigns", tags=["CRM"])
   ```

2. Adicione o re-export no agregador correspondente:
   ```python
   # modules/comercial/__init__.py
   from modules.crm.controllers import new_router as crm_campaign_router
   ```

3. Inclua no `__all__`:
   ```python
   __all__ = [..., "crm_campaign_router"]
   ```

4. Registre em `main.py`:
   ```python
   from modules.comercial import crm_campaign_router
   app.include_router(crm_campaign_router)
   ```

## 9. Testes

Validacao dos imports de todos os agregadores:

```bash
pytest tests/test_aggregator_imports.py -v
```

Este teste verifica que todos os routers listados em `__all__` de cada agregador
sao importaveis e sao instancias validas de `APIRouter`.

---

Duvidas: consulte os `__init__.py` de cada agregador em `modules/<nome>/__init__.py`.
