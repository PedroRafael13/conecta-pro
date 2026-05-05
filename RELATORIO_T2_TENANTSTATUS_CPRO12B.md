# T2-B CPRO12 — Fix TenantStatus enum completo
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Módulo:** config
**Branch:** feature/people-management-reorganization

---

## Arquivo enum
`backend/modules/config/models/tenant.py`

## Valores alterados

| Valor | Antes | Depois | Status |
|-------|-------|--------|--------|
| ATIVO | `"ativo"` | `"active"` | ✅ corrigido |
| INATIVO | `"inativo"` | `"inactive"` | ✅ corrigido |
| SUSPENSO | `"suspenso"` | `"suspended"` | ✅ corrigido |
| BLOQUEADO | `"bloqueado"` | `"blocked"` | ✅ corrigido |
| TRIAL | `"trial"` | `"trial"` | ✅ mantido (INV-6) |
| CANCELADO | `"cancelado"` | `"cancelled"` | ✅ corrigido |

## Testes atualizados
**1 arquivo:** `backend/tests/test_config_model.py:648–653` — 5 assertions `.value` com string literal PT-BR
**Resultado:** 105 passed, 0 failed (apenas DeprecationWarning de `datetime.utcnow()` — razão diferente, INV-12 não aplicado)

---

## Hipóteses

| Hipótese | Resultado |
|----------|-----------|
| H1 arquivo enum | `backend/modules/config/models/tenant.py` ✅ |
| H2 6 valores, TRIAL já correto | ✅ confirmado |
| H3 testes assertavam PT-BR | ✅ 5 assertions em test_config_model.py:648–653 |
| H4 usos usam .name não .value | ✅ — test_config_api.py usa `TenantStatus.X.value` (expressão, auto-corrigida) |
| H5 sem uso em zonas proibidas | ✅ zero em financial/ nem government_integrations/ |
| H6 py_compile OK | ✅ enum + 3 arquivos de teste — todos OK |
| H7 worker sem DataError | ✅ `check_late_employees succeeded` — zero DataError |
| H8 banco só tem valores inglês | ✅ `SELECT status → active (1 row)` |

---

## Worker operacional pós-fix

```
[2026-05-05 01:35:31] Task operacional.check_late_employees succeeded in 0.018s:
  [{'tenant_id': '841a3906', 'success': True, 'late_employees': 0, 'notifications_sent': 0}]
```

Zero DataError. Task executa, encontra tenant `active`, conclui com sucesso.

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `0996e1a7` | `docs(contracts): §64 — Fix TenantStatus enum completo PT-BR→inglês (CPRO12 T2-B)` |
| code | `0a41c5f7` | Incluído em commit T4 (read-only que inadvertidamente capturou os arquivos staged) |

**Nota:** Os dois arquivos de código (`tenant.py` + `test_config_model.py`) foram commitados em `0a41c5f7` por outra sessão que capturou os arquivos já staged. As mudanças são idênticas às planejadas — INV-5 verificado: `.name` preservado, apenas `.value` alterado.

---

## Cenário: A

Todos os testes passam. Worker operacional sem DataError. TenantStatus alinhado com DB.

---

## Auditoria — Observações (INV-12)

### STEP 6 — Erros de coleta pré-existentes (NÃO corrigidos)

`python3 -m pytest tests/ -k "tenant_status or TenantStatus or config_model"` interrompeu
a coleta por 2 erros pré-existentes sem relação com TenantStatus:

| Arquivo | Erro |
|---------|------|
| `tests/test_recruitment_models.py` | `ImportError: cannot import name 'EducationLevel' from modules.recruitment.models.candidate_education` |
| `tests/modules/crm/test_cpro11_regressions.py` | `Failed: 'regression' not a registered mark` |

Ambos são bugs pré-existentes. INV-12 aplicado: **NÃO corrigidos**. Os testes
específicos de TenantStatus foram executados diretamente por arquivo e obtiveram
**105 passed, 0 failed**.

### STEP 9 — Commit de código capturado por T4

O `git commit` de código falhou na primeira tentativa (hook `detect-secrets` modificou
`.secrets.baseline`). Enquanto corrigíamos o stage, a sessão T4 commitou os arquivos
já staged (`tenant.py` + `test_config_model.py`) em `0a41c5f7`. As mudanças estão
corretas no git mas com mensagem/session tag de T4 em vez de T2-B.
Não foi possível corrigir retroativamente sem `git revert` (proibido por CLAUDE.md).

---

T2-B CPRO12 OK — TenantStatus alinhado com DB. Todas as queries de status funcionarão.
