---
name: diagnostico-financeiro-completo
agent: FinancialAdvisorAgent
prioridade: ALTA
versao: 2.0
---

# Skill 10 — Diagnóstico Financeiro Completo

### GARGALOS CONHECIDOS (base para diagnóstico)
1. **Liquidez crítica** — saldo R$88.684,29 vs necessário R$88.360,22 (runway ~12d)
2. **Concentração receita** — 10 contratos, risco de cliente dominante > 20% MRR
3. **Despesas mes anterior R$439.030,38** — superior ao MRR R$270.586,96 (déficit estrutural)
4. **Margem Kit Mensal comprimida** — CCT 2026 pressionando custo de mão de obra
5. **Regime Lucro Real** — carga tributária mais elevada que Simples Nacional

### METODOLOGIA
1. Retrato atual (números sem interpretação)
2. Mapa de gargalos (com impacto em R$ e urgência)
3. Causa-raiz (estrutural ou comportamental)
4. Recomendações priorizadas por ROI

### CONSULTAS SQL
```sql
-- Concentração receita por cliente
SELECT c.name, round(br.base_value::numeric,2) as ticket,
       round(br.base_value / sum(br.base_value) OVER () * 100, 1) as pct_mrr
FROM billing_rules br
LEFT JOIN clients c ON c.id = br.client_id
WHERE br.ativo=true ORDER BY br.base_value DESC;

-- Evolução mensal receita x despesa
SELECT date_trunc('month',transaction_date) as mes,
       round(sum(CASE WHEN amount>0 THEN amount ELSE 0 END)::numeric,2) as entradas,
       round(sum(CASE WHEN amount<0 THEN ABS(amount) ELSE 0 END)::numeric,2) as saidas,
       round(sum(amount)::numeric,2) as resultado
FROM bank_transactions GROUP BY 1 ORDER BY 1 DESC LIMIT 6;

-- Runway atual
SELECT round(current_balance / NULLIF(
    (SELECT sum(ABS(amount))/3 FROM bank_transactions
     WHERE amount<0 AND transaction_date >= CURRENT_DATE - 90), 0) * 30, 1) as runway_dias
FROM bank_accounts WHERE bank_code='077';
```

### SAÍDA OBRIGATÓRIA
```json
{
  "retrato_atual": {
    "mrr": 270586.96,
    "saldo": 88684.29,
    "despesas_media_mensal": 439030.38,
    "runway_dias": 0,
    "resultado_mes": 0
  },
  "gargalos": [],
  "causa_raiz": "",
  "recomendacoes": []
}
```
