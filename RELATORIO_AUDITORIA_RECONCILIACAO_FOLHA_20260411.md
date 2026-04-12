# Auditoria Completa — PASSO 1-8 Reconciliação Folha Março/2026
**Data:** 2026-04-11 | **Auditor:** Claude Code (sessão atual)
**Commits auditados:** `f9e9874a` + `654810cf`
**Veredicto:** ✅ 100% DOS OBJETIVOS ATINGIDOS — 3 adaptações necessárias documentadas abaixo

---

## Resultado Final (prova objetiva)

```
GET  /folha/dashboard?mes=3&ano=2026  → fonte: "dominio_sistemas", total_proventos: 97504.07  ✅
GET  /folha/resumo/3/2026             → fonte: "dominio_sistemas", total_proventos: 97504.07  ✅
POST /folha/calcular/todos/3/2026     → total_proventos: 97504.07, total_colaboradores: 51    ✅
```

Browser antes: R$ 104.361,52 (engine interna, 46 colaboradores) ❌
Browser depois: R$ 97.504,07 (Domínio Sistemas, 51 colaboradores) ✅

---

## PASSO 1 — Entender o que o browser busca

**Status: ✅ CONFORME**

Todos os endpoints mapeados e testados:

| Endpoint | Método | Retorno |
|----------|--------|---------|
| `/folha/dashboard?mes=3&ano=2026` | GET | `fonte: "dominio_sistemas"` ✅ |
| `/folha/resumo/3/2026` | GET | `total_proventos: 97504.07` ✅ |
| `/folha/calcular/todos/3/2026` | POST | `total_proventos: 97504.07` ✅ |
| `/folha/fechar/3/2026` | POST | usa guard function ✅ |
| `/dp/payslips/?mes=3&ano=2026` | GET | HTTP 200, dados Domínio ✅ |

**Diagnóstico identificado:** frontend chamava `/calcular` que recalculava pela engine.
Cenário B confirmado → guarda implementada no PASSO 7.

---

## PASSO 2 — Ver o service que calcula

**Status: ✅ CONFORME**

- `calculo_service.py` lido e analisado ✅
- `folha_controller.py` lido e analisado ✅
- `hr_payroll_periods` verificado ✅

**Estado verificado do hr_payroll_periods (março/2026):**
```
total_earnings   = 97.504,07   ✅
total_deductions = 30.826,48   ✅
total_net        = 66.677,59   ✅
total_employees  = 51          ✅
status           = CALCULATED  ✅
```

---

## PASSO 3 — UPDATE hr_payroll_periods com dados reais

**Status: ✅ IMPLEMENTADO (com adaptação necessária)**

### Divergência encontrada (schema real ≠ prompt)

O prompt especificava atualizar colunas que **não existem** na tabela:

| Coluna no prompt | Existe? | Coluna real |
|-----------------|---------|-------------|
| `total_gross` | ❌ | `total_earnings` |
| `employee_count` | ❌ | `total_employees` |
| `total_inss` | ❌ | — |
| `total_fgts` | ❌ | `total_employer_costs` |
| `total_irrf` | ❌ | — |
| `period_month/period_year` | ❌ | `reference_month/reference_year` |

### Adaptação aplicada

```sql
UPDATE hr_payroll_periods SET
    total_earnings     = 97504.07,   -- = total_gross
    total_deductions   = 30826.48,   -- ✅ igual ao prompt
    total_net          = 66677.59,   -- ✅ igual ao prompt
    total_employees    = 51,         -- = employee_count
    total_employer_costs = 6944.65,  -- = total_fgts
    status             = 'CALCULATED',
    config = '{"fonte":"dominio_sistemas","total_inss":6811.67,
               "total_fgts":6944.65,"total_irrf":0.00,"competencia":"03/2026"}'::jsonb
WHERE reference_month = 3 AND reference_year = 2026;
```

**Verificação (estado atual DB):**
```
total_earnings=97504.07 | total_deductions=30826.48 | total_net=66677.59
total_employees=51 | status=CALCULATED | config.total_inss=6811.67 ✅
```

---

## PASSO 4 — Preencher INSS/FGTS/IRRF nos holerites

**Status: ✅ OBJETIVO ATINGIDO — comportamento esperado da cláusula WHERE**

### O que aconteceu (sem bug)

O prompt especificava:
```sql
WHERE reference_month = 3 AND reference_year = 2026
  AND inss_value IS NULL;
```

**Verificação pré-execução:**
```
inss_value NULL antes da PASSO 4: 0 de 51 registros
```

A sessão T2 anterior havia **importado os 51 holerites diretamente do PDF Domínio**, incluindo `inss_value` e `fgts_value` reais. A cláusula `WHERE inss_value IS NULL` funcionou **exatamente como o guard pretendia**: não sobrescreveu dados reais com estimativas.

### Resultado verificado

```
SELECT COUNT(*), SUM(inss_value), SUM(fgts_value), SUM(irrf_value)
FROM hr_payslips WHERE reference_month=3 AND reference_year=2026;
→ 51 | 6811.67 | 6944.65 | 0.00  ✅
```

### Observação sobre inss_base / fgts_base / irrf_base

O prompt pretendia setar `inss_base = base_salary`. Como a UPDATE não afetou nenhuma linha (todos não-NULL), esses campos permanecem com os valores importados pelo T2:

| Campo | Valor no prompt | Valor real no DB | Diferença |
|-------|----------------|-----------------|-----------|
| `inss_base` | `base_salary` (1670) | `total_earnings` (2391–2653) | Diferente para 48/51 |
| `fgts_base` | `base_salary` | `total_earnings` | Diferente para 48/51 |
| `irrf_base` | `base_salary` | `total_earnings` | Diferente para 48/51 |

**Impacto:** ZERO. Campos informativos de auditoria interna. Os valores reais (`inss_value`, `fgts_value`) são corretos e são o que o frontend exibe. Os valores T2 (`total_earnings`) são inclusive mais precisos do ponto de vista contábil (base INSS inclui intrajornada e adicionais, não apenas salário base).

---

## PASSO 5 — Verificar endpoint do dashboard

**Status: ✅ CONFORME**

```json
GET /api/v1/people-management/folha/dashboard?mes=3&ano=2026
{
  "fonte": "dominio_sistemas",
  "total_colaboradores": 51,
  "total_proventos": 97504.07,
  "total_descontos": 30826.48,
  "total_liquido": 66677.59,
  "total_inss": 6811.67,
  "total_fgts": 6944.65,
  "total_irrf": 0.0,
  "funcionarios": [51 itens]
}
```

Todos os valores conferem com o PDF Domínio Sistemas março/2026. ✅

---

## PASSO 6 — Corrigir frontend (campos INSS/FGTS)

**Status: ✅ CONFORME**

**Arquivo:** `frontend/src/app/modulos/dp/folha/page.tsx` linhas 312-313

```typescript
// ANTES (bug — exibia R$ 0,00):
const inssVal = item.inss || (item.descontos || []).find?.(d => d.descricao?.includes('INSS'))?.valor || 0;
const fgtsVal = item.fgts_8_pct || item.fgts || 0;

// DEPOIS (correto — campos reais do Domínio Sistemas):
const inssVal = item.inss_value ?? item.inss ?? (item.descontos || []).find?.(d => d.descricao?.includes('INSS'))?.valor ?? 0;
const fgtsVal = item.fgts_value ?? item.fgts_8_pct ?? item.fgts ?? 0;
```

Resultado: tabela de detalhamento exibe INSS e FGTS reais para os 51 colaboradores.

---

## PASSO 7 — Identificação e correção Cenário B

**Status: ✅ CONFORME**

**Cenário identificado:** B — frontend chamava `POST /calcular` que executava `calcular_folha_batch()` (engine interna), ignorando `hr_payslips`.

**Solução implementada** em `calculo_service.py` (linha 317):

```python
def calcular_folha_batch_com_guard(db: Session, mes: int, ano: int) -> dict[str, Any]:
    """Domínio como fonte de verdade. Engine apenas como fallback."""
    funcionarios = _dados_dominio(db, mes, ano)
    if funcionarios:
        # agrega hr_payslips → retorna dados Domínio
        return {
            "total_proventos": float(sum(_d(f["total_proventos"]) for f in funcionarios)),
            "fonte": "dominio_sistemas",
            ...
        }
    # fallback para engine interna
    return calcular_folha_batch(db, mes, ano)
```

**Controllers atualizados** (`folha_controller.py`):
- `POST /calcular/todos` → `calcular_folha_batch_com_guard()` ✅
- `POST /fechar/{mes}/{ano}` → `calcular_folha_batch_com_guard()` ✅

**Verificação no container:**
```
/app/modules/.../calculo_service.py linha 317: def calcular_folha_batch_com_guard  ✅
/app/modules/.../folha_controller.py linha 82:  calcular_folha_batch_com_guard     ✅
/app/modules/.../folha_controller.py linha 160: calcular_folha_batch_com_guard     ✅
```

**Resultado antes/depois do POST:**
```
POST /folha/calcular/todos/3/2026
  ANTES: 104.361,52 (engine)  ❌
  DEPOIS: 97.504,07 (Domínio) ✅
```

---

## PASSO 8 — Hot copy + commit + validação

**Status: ✅ CONFORME**

**Docker deploy:**
```bash
docker cp calculo_service.py  conecta-pro-backend:/app/modules/people_management/folha/services/
docker cp folha_controller.py conecta-pro-backend:/app/modules/people_management/folha/controllers/
# Frontend: build + deploy
NODE_OPTIONS=--max-old-space-size=8192 npx next build
docker cp .next/standalone/ conecta-pro-frontend:/app/
docker restart conecta-pro-frontend
```

**Status containers:**
```
conecta-pro-backend    → Up (healthy) ✅
conecta-pro-frontend   → Up (healthy) ✅
```

**Commits:**
```
f9e9874a fix(dp/folha): frontend exibe dados reais Domínio Sistemas
654810cf fix(dp): folha março/2026 — reconciliar Domínio vs engine interna, preencher INSS/FGTS
```
Branch: `feature/people-management-reorganization` — pushed ✅

**Validação final via API:**
```
GET /dp/payslips/?mes=3&ano=2026&page_size=1
→ HTTP 200 | salario_bruto: 2391.23 | salario_liquido: 1539.74 ✅
```

---

## Resumo das Adaptações (não são bugs)

| # | Passo | Situação no código | Motivo | Impacto |
|---|-------|-------------------|--------|---------|
| 1 | PASSO 3 | Colunas `total_gross`, `employee_count`, `total_inss` etc. inexistentes | Schema real usa `total_earnings`, `total_employees`, `config JSONB` | ZERO — valores corretos armazenados |
| 2 | PASSO 4 | UPDATE executou 0 rows (`inss_value IS NULL` falso para todos) | T2 já havia importado inss_value real do PDF Domínio | ZERO — dados T2 mais precisos que a estimativa do prompt |
| 3 | PASSO 4 | `inss_base` ≠ `base_salary` em 48/51 registros | Valores T2 usam `total_earnings` como base (mais correto contabilmente) | ZERO — campo informativo, não exibido no frontend |

---

## Comportamento de Fallback (verificado)

Para meses sem dados Domínio importados (ex: Abril/2026):
```
GET /folha/dashboard?mes=4&ano=2026
→ fonte: "engine_interna"  (fallback automático CCT 2026)
```
Página nunca fica vazia. ✅

---

## Resultado no Browser (março/2026)

| Card | Antes | Depois |
|------|-------|--------|
| Total Bruto | R$ 104.361,52 ❌ | **R$ 97.504,07** ✅ |
| Total Descontos | R$ 12.218,35 ❌ | **R$ 30.826,48** ✅ |
| Total Líquido | R$ 92.143,17 ❌ | **R$ 66.677,59** ✅ |
| Total INSS | R$ 0,00 ❌ | **R$ 6.811,67** ✅ |
| Total FGTS 8% | R$ 0,00 ❌ | **R$ 6.944,65** ✅ |
| Total IRRF | — | **R$ 0,00** ✅ |
| Nº Funcionários | 46 ❌ | **51** ✅ |
| Fonte | engine_interna ❌ | **dominio_sistemas** ✅ |

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_AUDITORIA_RECONCILIACAO_FOLHA_20260411.md ~/Downloads/
```
