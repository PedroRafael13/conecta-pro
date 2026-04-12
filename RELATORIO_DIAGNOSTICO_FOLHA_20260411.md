# Relatório de Diagnóstico — Sistema de Folha de Pagamento
**Data:** 2026-04-11
**Executado por:** Claude Code (claude-sonnet-4-6)
**Módulo:** Departamento Pessoal — Folha

---

## 1. Tabelas Relacionadas à Folha (29 tabelas)

| Tabela | Propósito |
|--------|-----------|
| `hr_payslips` | Contracheques — 51 colunas — dados do Domínio Sistemas |
| `hr_payroll_periods` | Períodos de folha (MAR-2026: status CALCULATED) |
| `hr_payroll_events` | Eventos individuais por funcionário (EARNING/DEDUCTION) |
| `hr_employee_payroll_configs` | Configuração CLT por funcionário (benefícios, empréstimos, etc.) |
| `hr_payroll_exports` | Exportações de folha |
| `hr_payroll_integrations` | Integrações com sistemas externos |
| `rubricas_folha` | Tabela mestra de rubricas (24 cadastradas) |
| `eventos_esocial` | Eventos para transmissão ao eSocial |

---

## 2. Estrutura hr_payslips (tabela principal)

### Campos numéricos disponíveis
| Campo | Tipo | Dados Importados |
|-------|------|------------------|
| `base_salary` | numeric(12,2) | `salario_base` do employee |
| `total_earnings` | numeric(12,2) | ✅ R$ 97.504,07 (soma) |
| `total_deductions` | numeric(12,2) | ✅ R$ 30.826,48 (soma) |
| `net_salary` | numeric(12,2) | ✅ R$ 66.677,59 (soma) |
| `inss_base` | numeric(12,2) | ⚠️ NULL (não importado) |
| `inss_value` | numeric(12,2) | ⚠️ NULL (não importado) |
| `irrf_base` | numeric(12,2) | ⚠️ NULL (não importado) |
| `irrf_value` | numeric(12,2) | ⚠️ NULL (não importado) |
| `fgts_base` | numeric(12,2) | ⚠️ NULL (não importado) |
| `fgts_value` | numeric(12,2) | ⚠️ NULL (não importado) |

### Campos JSONB
| Campo | Estrutura | Exemplo |
|-------|-----------|---------|
| `earnings` | `[{code, value, reference, description}]` | `[{"code":"0001","value":1670.0,"reference":"30d","description":"Salário Base"}]` |
| `deductions` | `[{code, value, reference, description}]` | `[{"code":"900","value":851.49,"reference":0,"description":"Total Descontos"}]` |
| `informative` | `{}` (vazio atualmente) | Bases INSS/IRRF/FGTS, dependentes |
| `bank_info` | nullable | Dados bancários para crédito |

### Campos de controle de portal
- `view_count`, `first_viewed_at`, `last_viewed_at` — rastreio de visualização
- `download_count`, `last_download_at` — rastreio de download
- `acknowledged_at`, `acknowledged_by_ip` — confirmação de ciência
- `contested_at`, `contest_reason`, `contest_resolution` — contestação
- `pdf_path`, `pdf_generated_at`, `pdf_hash` — PDF persistido em disco

---

## 3. Dois Sistemas de Folha em Paralelo

### Sistema A — hr_payslips (importação Domínio Sistemas)
```
Mês:             Março/2026
Holerites:       51
Total Proventos: R$ 97.504,07
Total Descontos: R$ 30.826,48
Líquido Geral:   R$ 66.677,59
Status:          published
INSS/IRRF/FGTS:  ⚠️ NULL — não importados do PDF
Fonte:           dominio_sistemas / batch d3707a1e
```

### Sistema B — hr_payroll_periods + hr_payroll_events (engine interna)
```
Período:         MAR-2026 (id: 10a78be6)
Status:          CALCULATED
Funcionários:    52
Total Proventos: R$ 87.410,15
Total Descontos: R$  8.145,63
Líquido Geral:   R$ 79.264,52
Eventos:         52×EARNING/SALARY + 52×DEDUCTION/INSS
                 2×DEDUCTION/PENSAO_ALIMENTICIA + 3×DEDUCTION/CONSIGNADO
Fonte:           engine interna
```

### Divergência entre os dois sistemas
| Métrica | Domínio (A) | Engine (B) | Δ |
|---------|-------------|------------|---|
| Funcionários | 51 | 52 | -1 |
| Total Proventos | R$ 97.504,07 | R$ 87.410,15 | R$ 10.093,92 |
| Total Descontos | R$ 30.826,48 | R$ 8.145,63 | R$ 22.680,85 |
| Líquido Geral | R$ 66.677,59 | R$ 79.264,52 | -R$ 12.586,93 |

**Causa provável da divergência:**
- Sistema B calcula apenas INSS como desconto (R$ 8.145,63 ≈ 52×INSS médio)
- Sistema A tem TODOS os descontos (VT, VR, consignado, pensão, etc.) conforme PDF Domínio
- Sistema B usa salário base sem hora extra/adicionais; Sistema A tem proventos completos

---

## 4. Rubricas Cadastradas (24 rubricas)

### Proventos (14)
| Código | Descrição | INSS | IRRF | FGTS |
|--------|-----------|------|------|------|
| 0001 | Salário Base | ✓ | ✓ | ✓ |
| 0010 | Hora Extra 50% | ✓ | ✓ | ✓ |
| 0011 | Hora Extra 100% | ✓ | ✓ | ✓ |
| 0020 | Adicional Noturno | ✓ | ✓ | ✓ |
| 0021 | Hora Noturna Reduzida | ✓ | ✓ | ✓ |
| 0030 | Intrajornada Não Concedida | ✓ | ✓ | ✓ |
| 0040 | Adicional Ronda 15% | ✓ | ✓ | ✓ |
| 0041 | Adicional Ronda 30% | ✓ | ✓ | ✓ |
| 0050 | Adicional Insalubridade 10% | ✓ | ✓ | ✓ |
| 0051 | Adicional Periculosidade 30% | ✓ | ✓ | ✓ |
| 0060 | Vale Refeição | ✗ | ✗ | ✗ |
| 0061 | Vale Transporte | ✗ | ✗ | ✗ |
| 0070 | 13º Salário 1ª Parcela | ✗ | ✗ | ✓ |
| 0071 | 13º Salário 2ª Parcela | ✓ | ✓ | ✓ |
| 0080 | Férias | ✓ | ✓ | ✓ |
| 0090 | DSR sobre HE | ✓ | ✓ | ✓ |
| 0100 | Taxa Negocial Provento | ✗ | ✗ | ✗ |

### Descontos (7)
| Código | Descrição |
|--------|-----------|
| 1001 | INSS |
| 1002 | IRRF |
| 1010 | Desconto VT |
| 1011 | Desconto VR |
| 1020 | Desconto Plano Odontológico |
| 1021 | Desconto Seguro de Vida |
| 1030 | Taxa Negocial Desconto |

**Rubricas ausentes que existem no Domínio:**
- Consignado (CONSIGNADO existe em hr_payroll_events mas sem rubrica cadastrada)
- Pensão Alimentícia (PENSAO_ALIMENTICIA existe em events mas sem rubrica)
- Adiantamento Salarial
- Faltas/Atrasos

---

## 5. Engine de Cálculo — CCT 2026 SINDECOMPRESTS

**Arquivo:** `modules/people_management/folha/services/calculo_service.py`

```
Tabelas legais implementadas:
  INSS progressivo 2026:  R$ 1.518 (7,5%) / R$ 2.793,88 (9%) / R$ 4.190,83 (12%) / R$ 8.157,41 (14%)
  IRRF progressivo 2026:  R$ 2.259,20 (isento) / R$ 2.826,65 (7,5%) / R$ 3.751,05 (15%)
                          R$ 4.664,68 (22,5%) / acima (27,5%)

Constantes CCT 2026:
  VR: R$ 22,00/dia
  Desconto VT: 4% do salário
  Desconto VR: 1% do salário
  Desconto Odonto: R$ 9,00/mês
  Desconto Seguro: R$ 2,00/mês
  Taxa Negocial: R$ 22,00 (meses 1,3,5,7,9,11)
  FGTS: 8%

Divisores de escala:
  12×36: 180h/mês, 15 dias trabalhados
  44h: 220h/mês, 22 dias trabalhados
```

**Arquivo:** `modules/people_management/common/utils/clt_calculator.py`
- Calculadora genérica CLT com Decimal precision
- Tabelas INSS 2026 (base 2026 ligeiramente diferente: R$ 1.412 / R$ 2.666,68 / R$ 4.000,03 / R$ 7.786,02)
- IRRF idêntico
- FGTS 8%

**Arquivo:** `modules/hr/payroll_integration/services/payroll_calculation_service.py`
- Engine async baseada em `hr_payroll_events`
- Gera eventos por funcionário (EARNING/DEDUCTION)
- Atualiza `hr_payroll_periods` com totais consolidados

---

## 6. hr_employee_payroll_configs — Configurações por Funcionário

**Campos principais:**
- `contract_type`: clt (padrão)
- `monthly_hours`: 220h / `weekly_hours`: 44h
- `base_salary`: salário base individual
- `overtime_50_rate`: 1.5× / `overtime_100_rate`: 2.0×
- `night_shift_rate`: 1.2× / `night_shift_enabled`: true
- `benefits`: JSONB — VT, VR, plano odonto, etc.
- `loans`: JSONB — consignados
- `alimony`: JSONB — pensão alimentícia
- `dependents`: JSONB + `dependents_count`
- `bank_hours_balance`, `bank_hours_limit`: banco de horas

**Observação:** Tabela existe mas sem dados cadastrados para os 51 funcionários importados.
Os holerites importados do Domínio usam apenas `employees.salario_base`.

---

## 7. Pasta de Uploads

| Path | Status |
|------|--------|
| `/opt/conecta-pro/uploads/` | ✅ Existe |
| `/opt/conecta-pro/uploads/ged/` | ✅ Existe (GED usa) |
| `/opt/conecta-pro/uploads/folhas/` | ❌ NÃO EXISTE |

**Impacto:** O campo `hr_payslips.pdf_path` armazena caminho do PDF gerado.
Atualmente PDFs são gerados on-demand (não persistidos). Para persistência seria necessário criar esta pasta.

---

## 8. Gaps Identificados

| # | Gap | Severidade | Impacto |
|---|-----|------------|---------|
| 1 | `inss_value`, `irrf_value`, `fgts_value` = NULL em todos os 51 holerites | Alta | PDF incompleto; eSocial inconsistente |
| 2 | `hr_employee_payroll_configs` vazio para os 51 funcionários | Média | Engine interna não consegue calcular individual |
| 3 | Divergência de totais: Domínio (R$ 97.504,07) ≠ Engine B (R$ 87.410,15) | Alta | Dados duplos sem reconciliação |
| 4 | `hr_payroll_events` tem apenas SALARY + INSS (sem VT, VR, adicionais) | Alta | Folha interna incompleta |
| 5 | Rubricas ausentes: consignado, pensão, adiantamento, faltas | Média | Cálculo automático incompleto |
| 6 | `uploads/folhas/` não existe | Baixa | PDFs não são persistidos em disco |
| 7 | JOSIANE matrícula "000184" (não atualizada para Domínio) | Baixa | Inconsistência de matrícula |

---

## 9. O que Funciona Hoje

| Funcionalidade | Status |
|----------------|--------|
| GET /dp/payslips/?mes=3&ano=2026 | ✅ 51 holerites retornados |
| GET /dp/payslips/{id}/pdf | ✅ PDF gerado via reportlab |
| GET /operacional/employees/ | ✅ 51 funcionários com matriculas corretas |
| Totais Domínio verificados | ✅ R$ 97.504,07 / 30.826,48 / 66.677,59 |
| Publicação de holerite (PATCH /publicar) | ✅ |
| Portal do funcionário (my_payslips) | ✅ |
| Engine CCT 2026 implementada | ✅ calculo_service.py |
| hr_payroll_periods MAR-2026 CALCULATED | ✅ |

---

## 10. Próximos Passos Sugeridos

1. **Preencher INSS/IRRF/FGTS nos 51 holerites** — calcular retroativamente com `clt_calculator.py` e atualizar `inss_value`, `irrf_value`, `fgts_value`, `inss_base`, `irrf_base`, `fgts_base`

2. **Criar `uploads/folhas/`** — para persistência de PDFs e preenchimento de `pdf_path`

3. **Reconciliar Sistema A × B** — definir se Domínio é a fonte de verdade ou se a engine interna deve ser priorizada

4. **Popular `hr_employee_payroll_configs`** — para habilitar cálculo automático mensal sem depender de importação

5. **Adicionar rubricas faltantes** — consignado (código 1040), pensão (1050), adiantamento (1060), faltas (1070)

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_DIAGNOSTICO_FOLHA_20260411.md \
  ~/Downloads/RELATORIO_DIAGNOSTICO_FOLHA_20260411.md
```
