---
name: break-even-ponto-equilibrio
agent: PricingOptimizerAgent
prioridade: ALTA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
mrr_bruto: 270586.96
saldo_inter: 88684.29
---

# Skill 02 — Analise de Ponto de Equilibrio (Break-even)
## Conecta Mais | CCT SINDECOMPRESTS 2026 | Lucro Real

### ESTRUTURA DE CUSTOS REAIS (extrato Inter jan-mar/2026)

**Custos Fixos Mensais (media real):**

| Item | Fonte | Valor/mes |
|------|-------|-----------|
| Folha CLT 52 funcionarios | extrato: folha_pagamento media jan-mar | R$160.357,03 |
| Fornecedores fixos | extrato: fornecedores media | R$15.150,97 |
| Pro-labore (Jordan Jesus) | extrato: pro_labore media | R$8.987,50 |
| Operacional (aluguel, moto) | extrato: operacional media | R$7.828,33 |
| Financiamentos (Toyota + C6) | extrato: financiamentos media | R$3.039,47 |
| TI/Telecom (LWSA, Econdos) | extrato: ti_telecom media | R$400,25 |
| Beneficios CLT | extrato: beneficios media | R$262,50 |
| Taxa bancaria Inter | extrato: taxa_bancaria media | R$1.217,49 |
| **TOTAL FIXO ESTIMADO** | | **R$197.243,54** |

**Deducoes Fiscais sobre MRR bruto (Lucro Real):**

| Tributo | Aliquota | Sobre R$270.586,96 |
|---------|----------|-------------------|
| ISS Manaus | 5,00% | R$13.529,35 |
| PIS (nao-cumulativo) | 1,65% | R$4.464,68 |
| COFINS (nao-cumulativo) | 7,60% | R$20.564,61 |
| **TOTAL DEDUCOES** | **14,25%** | **R$38.558,64** |

**MRR liquido (apos tributos sobre faturamento): R$232.028,32**

### CALCULO DO BREAK-EVEN

```
Receita Bruta Necessaria = Custos Fixos / (1 - Aliquota_impostos)

Break-even tributos = R$197.243,54 / (1 - 0,1425)
                    = R$197.243,54 / 0,8575
                    = R$229.990,74 de MRR bruto

Margem de seguranca = (MRR_atual - Break-even) / MRR_atual * 100
                    = (R$270.586,96 - R$229.990,74) / R$270.586,96
                    = 15,0% — FRAGIL (ideal > 25%)
```

**Break-even por tipo de custo:**

| Cenario | MRR necessario | Margem atual |
|---------|----------------|-------------|
| Apenas folha + tributos | R$186.989,62 | 30,9% |
| Folha + tributos + fornecedores | R$204.574,56 | 24,4% |
| Todos os custos fixos + tributos | R$229.990,74 | 15,0% |
| + IRPJ/CSLL LR provisionados | R$271.862,91 | -0,5% NEGATIVO |

**ATENCAO:** Incluindo IRPJ/CSLL sobre lucro real, a empresa opera NO LIMITE do break-even com o MRR atual.

### CCT SINDECOMPRESTS 2026 — IMPACTO NOS CUSTOS

| Item | Valor CCT 2026 | Calculo |
|------|----------------|---------|
| Piso salarial vigilante | R$1.847,93/mes | Base para 52 funcionarios |
| FGTS (8%) | R$147,83/funcionario | R$7.687,16/total |
| INSS patronal (~20%) | R$369,59/funcionario | R$19.218,72/total |
| VR: R$26,40/dia x 22 dias | R$580,80/funcionario | R$30.201,60/total |
| VT (media R$150/funcionario) | R$150,00/funcionario | R$7.800,00/total |
| 13o provisionado (1/12) | R$153,99/funcionario | R$8.007,48/total |
| Ferias provisionadas (1/12) | R$205,32/funcionario | R$10.676,64/total |
| **Custo minimo CCT/funcionario** | **R$3.455,46** | **R$179.683,92/total** |

**Custo real medio por funcionario (extrato): R$160.357,03 / 52 = R$3.083,79**
(Diferenca sugere que nem todos os 52 sao vigilantes — parte e administrativo com salario menor)

### FORMULAS DE BREAK-EVEN POR TIPO DE SERVICO

**Kit Mensal CLT (por posto de vigilante):**
```
Custo_por_posto = R$3.455,46 (CCT 2026 all-in)
Break-even_ticket = Custo_posto / (1 - 0,1425) / (1 - Margem_minima_20%)
Break-even_ticket = R$3.455,46 / 0,8575 / 0,80 = R$5.037,72/posto
Ticket_atual_medio = R$262.386,96 / 7 contratos = R$37.484/contrato
Postos_estimados_por_contrato = 3-13 (Ideal Flores = 13 postos)
```

**Portaria Remota (Gelain):**
```
Custo_direto = R$3.270/mes (Econdos + operador parcial)
Ticket = R$6.000/mes
MC = R$2.730 (45,5%) — ACIMA do break-even
Break-even_portaria = R$3.270 / (1 - 0,1425) = R$3.814,06
Margem de seguranca: 36,4%
```

**Manutencao CFTV (Parise + Green Hills):**
```
Custo_variavel_estimado = ~35% do ticket (pecas + hora tecnica)
Ticket medio = R$1.100/mes
MC media = R$715 (65%) — BOA mas volume baixo
Break-even_cftv = Custo_hora_tecnico / (1 - 0,1425)
```

### ALERTAS DE BREAK-EVEN

- IRPJ/CSLL ainda nao contabilizados nas projecoes acima
- Reajuste CCT 2027 (jan/2027): estimar +5-8% sobre piso salarial
- Sem reajuste de precos em 2027: margem cai para ~7-10%
- Contrato abaixo de R$5.037/posto: operar com prejuizo

### CONSULTAS SQL

```sql
-- Custo folha real por mes (para calibrar break-even)
SELECT
    to_char(date_trunc('month', transaction_date), 'MM/YYYY') as mes,
    round(sum(ABS(amount))::numeric, 2) as custo_folha,
    count(*) as transacoes_folha
FROM bank_transactions
WHERE category = 'folha_pagamento'
GROUP BY date_trunc('month', transaction_date)
ORDER BY 1;

-- MRR e contratos para calcular break-even
SELECT
    CASE
        WHEN name ILIKE '%Portaria Remota%' OR name ILIKE '%Seg. Eletr%' THEN 'portaria_remota'
        WHEN name ILIKE '%CFTV%' THEN 'manutencao_cftv'
        ELSE 'kit_mensal_clt'
    END as tipo,
    count(*) as contratos,
    round(sum(base_value)::numeric, 2) as mrr,
    round(avg(base_value)::numeric, 2) as ticket_medio
FROM billing_rules
WHERE status = 'ativa'
GROUP BY 1;

-- Total impostos realmente pagos (DARF, GPS, GFIP)
SELECT round(sum(ABS(amount))::numeric, 2) as total_impostos
FROM bank_transactions
WHERE category = 'impostos'
AND date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE - interval '1 month');
```
