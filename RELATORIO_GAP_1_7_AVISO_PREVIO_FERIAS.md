# T_GAP_1_7 | Gap 1.7 — Aviso Prévio de Férias | 2026-04-18
**Contrato início:** v1.11 | **Contrato após:** v1.12 | **Princípios:** 13.4 Escopo Sagrado + 13.1 Chesterton + 13.3 Docs antes de código

---

## STEP 0 — Contrato
- v1.11 lido ✅
- Princípio 13.4 (Escopo Sagrado): adicionar método ao ContractGeneratorService do T1, não duplicar
- T1 entregou: `ContractGeneratorService.gerar_contrato_trabalho_html(employee_id)` + helpers `_get_employee`, `_get_template`
- Reusei todos os helpers + generalizei `_get_template` → `_get_template_by_service_type`

---

## STEP 1 — Investigação

### 1.1 Variáveis REAIS do template (10 variáveis, extraídas via grep)

```
{{ admission_date }}
{{ employee_name }}
{{ notice_date }}
{{ period_end }}
{{ period_start }}
{{ return_date }}
{{ role }}
{{ vacation_days }}
{{ vacation_end }}
{{ vacation_start }}
```

Sem divergência com suposição inicial (todas mapeadas no service).

### 1.2 Service T1 confirmado

```
contract_generator_service.py: def gerar_contrato_trabalho_html(employee_id)
```

Helpers reusados: `_get_employee(employee_id)`, `_get_template_by_service_type(st, fallback_paths)`

### 1.3 Padrão de rota adotado (coerente com T1)
```
POST /api/v1/people-management/hr/contracts/employee/{id}/gerar-aviso-previo-ferias-html
```

### 1.4 Campos de férias em Employee
Employee tem `data_admissao` — usado para calcular `period_start`/`period_end`.
Não há campo `periodo_aquisitivo` nativo. Cálculo derivado da admissão.

### 1.5 Frontend férias
Páginas encontradas: `dp/ferias/page.tsx`, `operacional/ferias/page.tsx`
Integração feita em: `dp/funcionarios/page.tsx` linha ~613 (ao lado do BotaoGerarContrato)

---

## STEP 2 — Seeder

`backend/modules/people_management/hr/seeders/seed_aviso_previo_ferias.py` executado

| Tabela | Antes | Depois |
|--------|-------|--------|
| contract_templates rows | 1 (admissao) | **2** (admissao + ferias) |

```sql
SELECT service_type, name FROM contract_templates WHERE is_active = true;
→ admissao | Contrato de Trabalho CLT
→ ferias   | Aviso Prévio de Férias — CLT
```

---

## STEP 3 — Método adicionado ao ContractGeneratorService

Adicionado ao service EXISTENTE (INV-1 respeitado, zero duplicação):

```python
async def gerar_aviso_previo_ferias_html(
    self, employee_id: str, data_inicio_ferias: str, dias: int = 30
) -> ContratoGerado
```

Validações de domínio (antes de tocar DB):
1. `dias <= 0 or dias > 30` → ValueError
2. `data_inicio_ferias` não parseável → ValueError
3. `data_inicio` no passado → ValueError

Contexto Jinja2 (10 vars):

| Var template | Fonte |
|---|---|
| `employee_name` | `emp["nome"]` |
| `role` | `emp["cargo"]` |
| `admission_date` | `emp["data_admissao"].strftime(...)` |
| `period_start` | `_calc_periodo_aquisitivo()` |
| `period_end` | `_calc_periodo_aquisitivo()` |
| `vacation_start` | `data_inicio_ferias` |
| `vacation_end` | `data_inicio + dias - 1` |
| `vacation_days` | `str(dias)` |
| `return_date` | `data_inicio + dias` |
| `notice_date` | `date.today()` |

Persistência: `/app/uploads/avisos_gerados/{employee_id}/aviso_previo_ferias_{ts}.html`

Helper generalizado:
```python
async def _get_template_by_service_type(self, service_type: str, fallback_paths: list[Path]) -> str
```

---

## STEP 4 — Endpoints

```
POST /employee/{employee_id}/gerar-aviso-previo-ferias-html
  params: data_inicio_ferias (str, obrigatório), dias (int, default 30, 1-30)
  auth: CurrentActiveUser ✅

GET /employee/{employee_id}/download-aviso/{filename}
  serve: /app/uploads/avisos_gerados/{employee_id}/{filename}
  auth: CurrentActiveUser ✅
```

---

## STEP 5 — Frontend

| Componente | Path | Status |
|-----------|------|--------|
| Hook | `src/hooks/useGerarAvisoPrevioFerias.ts` | TanStack useMutation, zero any ✅ |
| Componente | `src/app/modulos/gestao-pessoas/dp/components/BotaoAvisoPrevioFerias.tsx` | Dialog shadcn + inputs date/número ✅ |
| Integração | `dp/funcionarios/page.tsx` linha ~613 | `<BotaoAvisoPrevioFerias employeeId={editingId} />` ao lado do BotaoGerarContrato ✅ |

---

## STEP 6 — Validações

| Teste | Resultado |
|-------|-----------|
| A: POST sem token → 401 | ✅ |
| B: POST token válido → 200 + ContratoGerado JSON | ✅ `employee_name: ANDREA GONÇALVES DOS SANTOS` |
| C: arquivo em `/app/uploads/avisos_gerados/` | ✅ `aviso_previo_ferias_20260418_174349.html` (1564 bytes) |
| D: download-aviso endpoint → 200 + HTML | ✅ `<!DOCTYPE html>` servido corretamente |

---

## STEP 7 — Falsificação 🔴

| Teste | Resultado |
|-------|-----------|
| A: data_inicio_ferias no passado → ValueError | ✅ `data_inicio_ferias não pode estar no passado: 2026-04-08` |
| B: dias=0 → ValueError | ✅ `dias deve estar entre 1 e 30, recebido: 0` |
| C: dias=31 → ValueError | ✅ `dias deve estar entre 1 e 30, recebido: 31` |
| D: employee inexistente → HTTP 400 | ✅ `Funcionário 00000000... não encontrado` |

---

## STEP 8 — Contrato v1.12

`CONTRACTS_GEDEON.md §20` documentado com arquitetura completa + padrão para futuros templates.
Versão 1.11 → **1.12**

---

## STEP 9 — Commits

| Hash | Tipo | Conteúdo |
|------|------|----------|
| `40dd07cd` | docs | CONTRACTS_GEDEON v1.12 §20 |
| `d373a6bd` | feat | Gap 1.7 (seeder + service + endpoint + frontend) |

Pushed: `feature/people-management-reorganization` → `e6493870..d373a6bd`

---

## Self-check 12/12

| # | Item | ✅ |
|---|------|---|
| 1 | STEP 0 — contrato v1.11 lido + princípio 13.4 citado | ✅ |
| 2 | STEP 1.1 — 10 variáveis REAIS extraídas via grep | ✅ |
| 3 | STEP 1.2 — ContractGeneratorService confirmado + método T1 listado | ✅ |
| 4 | STEP 2 — seeder criado + contract_templates tem 2 rows | ✅ |
| 5 | STEP 3 — método adicionado AO MESMO service (zero duplicação) | ✅ |
| 6 | STEP 4 — endpoint com Depends(get_current_user) / CurrentActiveUser | ✅ |
| 7 | STEP 5 — hook + modal dialog + integração funcionarios/page.tsx | ✅ |
| 8 | STEP 6 — Validações A+B+C+D passam | ✅ |
| 9 | STEP 7 — 4 falsificações 🔴 passaram | ✅ |
| 10 | STEP 8 — CONTRATO v1.12 §20 (antes do commit de código) | ✅ |
| 11 | STEP 9 — 2 commits separados + push | ✅ |
| 12 | INV-8 respeitado — arquivos do T1 só receberam adições, nada removido/refatorado | ✅ |

---

**GAP 1.7 RESOLVIDO — LIBERAR T7**
