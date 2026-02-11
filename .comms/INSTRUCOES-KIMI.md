# Instruções para Kimi — Lote A: Model Tests

Leia `/opt/conecta-pro/.comms/HANDOFF.md` para contexto completo do projeto.

## Sua Tarefa: Corrigir 70 falhas em 7 arquivos de model test

Todos seguem o **mesmo padrão**: enums inventados, campos inventados, SQLAlchemy defaults que não aplicam sem session.

### Arquivos (faça nesta ordem):

| # | Arquivo | Falhas |
|---|---------|--------|
| 1 | tests/test_diarist_model.py | 15 |
| 2 | tests/test_maintenance_model.py | 11 |
| 3 | tests/test_installation_model.py | 11 |
| 4 | tests/test_comodato_model.py | 10 |
| 5 | tests/test_equipment_model.py | 8 |
| 6 | tests/test_integrations_model.py | 8 |
| 7 | tests/test_payroll_event_model.py | 7 |

### Método OBRIGATÓRIO para CADA arquivo:

```bash
cd /opt/conecta-pro/backend && source venv/bin/activate

# PASSO 1: Rodar o teste e ver erros EXATOS
python3 -m pytest tests/test_XXX.py -v --tb=short 2>&1 | tail -80

# PASSO 2: Introspect os models REAIS
python3 -c "
import sys, enum, inspect; sys.path.insert(0, '.')
from modules.XXX.models import *

# Ver TODOS os enums do módulo
for name, obj in sorted(vars().items()):
    if isinstance(obj, type) and issubclass(obj, enum.Enum):
        print(f'\n{name}:')
        for e in obj:
            print(f'  {e.name} = {e.value!r}')

# Ver campos do model
for model_cls in [MeuModel]:  # substituir pelo model real
    print(f'\n=== {model_cls.__name__} ===')
    for col in model_cls.__table__.columns:
        print(f'  {col.name}: {col.type} nullable={col.nullable} default={col.default}')
"

# PASSO 3: Corrigir APENAS o teste (NÃO código de produção)
# - Enum values: usar os valores EXATOS da introspection
# - Campos: usar os nomes EXATOS das columns
# - Defaults: passar created_at, updated_at, etc. explicitamente

# PASSO 4: Rodar e confirmar 0 failures
python3 -m pytest tests/test_XXX.py -v --tb=short

# PASSO 5: Commitar
git add tests/test_XXX.py && git commit -m "fix(tests): corrigir N falhas em test_XXX.py"
```

### Regras:
- NÃO editar código de produção
- NÃO inventar valores — usar APENAS o que a introspection mostra
- NÃO pular pro próximo arquivo sem ter 0 failures no atual
- Após cada commit, reportar status em `/opt/conecta-pro/.comms/messages/kimi-out.jsonl`:
```json
{"ts":"2026-02-10T...","from":"kimi","type":"status","file":"test_XXX.py","before":N,"after":0,"result":"PASSED"}
```
