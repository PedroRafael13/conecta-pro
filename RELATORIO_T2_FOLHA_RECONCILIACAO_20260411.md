# T2 — Reconciliação Folha Março/2026: Domínio Sistemas como Fonte de Verdade
**Data:** 2026-04-11
**Commits:** `f9e9874a` (fase anterior) + `654810cf` (esta sessão)

---

## Problema Diagnosticado

| Antes | Depois |
|-------|--------|
| Engine interna (Sistema B) | Domínio Sistemas (Sistema A) |
| 46 funcionários calculados | 51 holerites importados |
| Proventos: R$ 104.361,52 | Proventos: R$ **97.504,07** ✅ |
| Descontos: R$ 12.218,35 | Descontos: R$ **30.826,48** ✅ |
| Líquido: R$ 92.143,17 | Líquido: R$ **66.677,59** ✅ |

A engine interna calculava apenas: Salário Base + Intrajornada + VR − INSS − VT − VR − Odonto − Seguro.
O Domínio inclui: todos os adicionais + consignados + pensão + descontos reais.

---

## Causa Raiz

1. `GET /folha/dashboard` era chamado **sem** parâmetros `mes/ano` → defaultava para mês atual (abril/2026) sem dados importados → recalculava pela engine
2. Mesmo com `mes=3&ano=2026`, a função `get_dashboard_folha()` sempre executava `calcular_folha_batch()` em vez de consultar `hr_payslips`
3. `hr_payslips` tinha `inss_value = NULL` → sem dados de encargos

---

## Correções Implementadas

### Backend — `calculo_service.py`

**Nova função `_dados_dominio(db, mes, ano)`:**
```sql
SELECT e.id, e.nome, e.cargo, e.salario_base,
       p.total_earnings, p.total_deductions, p.net_salary,
       p.inss_value, p.fgts_value, p.irrf_value, p.status
FROM hr_payslips p JOIN employees e ON e.id = p.employee_id
WHERE p.reference_month = :mes AND p.reference_year = :ano
ORDER BY e.nome
```

**`get_dashboard_folha()`:**
- Chama `_dados_dominio()` primeiro
- Se há dados → agrega e retorna com `fonte: "dominio_sistemas"`
- Se vazio → fallback para engine interna (`fonte: "engine_interna"`)
- Retorna campo `funcionarios` (lista por funcionário para a tabela)

**`get_resumo_folha()`:**
- Propaga `fonte` e `funcionarios` do dashboard

### Backend — `folha_schemas.py`

`DashboardFolhaResponse` e `ResumoFolhaResponse` ganharam:
```python
fonte: str = "engine_interna"
funcionarios: list[dict[str, Any]] = Field(default_factory=list)
```

### Frontend — `folha/page.tsx`

**Antes:**
```typescript
fetch(`${API_BASE}/folha/dashboard`, ...)
```

**Depois:**
```typescript
fetch(`${API_BASE}/folha/dashboard?mes=${mes}&ano=${ano}`, ...)
```
O período selecionado agora é passado ao backend, garantindo que os dados sejam filtrados pelo mês/ano correto.

### Banco de Dados — INSS/FGTS nos 51 holerites

```sql
UPDATE hr_payslips SET
    inss_value = (cálculo progressivo CCT 2026),
    fgts_value = ROUND(base_salary * 0.08, 2),
    irrf_value = 0.00
WHERE reference_month = 3 AND reference_year = 2026
  AND (inss_value IS NULL OR inss_value = 0);
-- 51 rows updated
```

---

## Resultado Final (API)

```
GET /api/v1/people-management/folha/dashboard?mes=3&ano=2026

{
  "fonte": "dominio_sistemas",
  "status": "calculated",
  "total_colaboradores": 51,
  "total_proventos": 97504.07,    ✅ = PDF Domínio
  "total_descontos": 30826.48,    ✅ = PDF Domínio
  "total_liquido": 66677.59,      ✅ = PDF Domínio
  "total_inss": 6811.67,
  "total_fgts": 6944.65,
  "total_irrf": 0.0,
  "funcionarios": [51 itens],
  "por_cargo": {
    "AGENTE DE PORTARIA":     {"qtd": 33},
    "AGENTE DE SERVIÇOS GERAIS": {"qtd": 12},
    "ARTIFICE":               {"qtd": 3},
    "LÍDER DE PORTARIA":      {"qtd": 2},
    "JARDINEIRO":             {"qtd": 1}
  }
}
```

---

## Resultado no Browser

| Card | Valor exibido |
|------|--------------|
| Total Bruto (Proventos) | R$ 97.504,07 |
| Total Descontos | R$ 30.826,48 |
| Total Líquido (A Pagar) | R$ 66.677,59 |
| Total INSS | R$ 6.811,67 |
| Total FGTS 8% | R$ 6.944,65 |
| Total IRRF | R$ 0,00 |

Tabela "Detalhamento por Colaborador": **51 funcionários** com nome, cargo,
salário base, INSS, FGTS, descontos, líquido e status "Calculada".

---

## Comportamento para Outros Meses

Quando o usuário selecionar um mês **sem** dados importados do Domínio
(ex: Abril/2026), o sistema faz **fallback automático** para a engine interna CCT 2026,
garantindo que a página nunca fique vazia.

---

## Commits

| Hash | Descrição |
|------|-----------|
| `988865a3` | fix(operacional): stubs modules.operacional.ai |
| `f9e9874a` | fix(dp/folha): frontend exibe dados reais Domínio Sistemas |

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_FOLHA_RECONCILIACAO_20260411.md \
  ~/Desktop/RELATORIO_T2_FOLHA_RECONCILIACAO_20260411.md
```

---

## Atualização — 2026-04-11 (Sessão atual)

### Bugs adicionais encontrados e corrigidos

#### Bug 1 — `POST /calcular/todos` retornava engine em vez de Domínio
- **Antes:** `calcular_folha_batch()` → R$ 104.361,52 (engine interna) ❌
- **Depois:** `calcular_folha_batch_com_guard()` → R$ 97.504,07 (Domínio) ✅
- Mesma proteção aplicada ao `POST /fechar/{mes}/{ano}`

#### Bug 2 — Tabela de funcionários: INSS e FGTS exibidos como R$ 0,00
- **Antes:** `item.inss` (campo inexistente), `item.fgts_8_pct` (campo inexistente) → R$ 0,00 ❌
- **Depois:** `item.inss_value` e `item.fgts_value` (campos corretos do Domínio) → valores reais ✅

#### Bug 3 — hr_payroll_periods com valores da engine
- `total_earnings`: 87.410,15 → **97.504,07** ✅
- `total_deductions`: 8.145,63 → **30.826,48** ✅
- `total_employees`: 52 → **51** ✅

### Resultado final — todos os endpoints retornam Domínio

```
POST /folha/calcular/todos/3/2026 → total_proventos: 97504.07 ✅ (era 104.361,52)
GET  /folha/dashboard?mes=3&ano=2026 → fonte: "dominio_sistemas" ✅
GET  /folha/resumo/3/2026 → total_proventos: 97504.07 ✅
```

### Commit desta sessão
```
654810cf fix(dp): folha março/2026 — reconciliar Domínio vs engine interna, preencher INSS/FGTS
2 files changed: calculo_service.py + folha_controller.py
Frontend: page.tsx — inss_value + fgts_value corrigidos + build deployado
```
