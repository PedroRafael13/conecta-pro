---
name: metas-smart-financeiras
agent: FinancialAdvisorAgent
prioridade: MÉDIA
versao: 2.0
---

# Skill 14 — Metas SMART Financeiras — Conecta Mais

### METAS SMART PRIORITÁRIAS (situação abril/2026)

**META 1 — LIQUIDEZ (URGENTE 🔴)**
- **S**pecífico: Atingir saldo Inter R$88.360,22 (1x custo fixo mensal)
- **M**ensurável: `SELECT current_balance FROM bank_accounts WHERE bank_code='077'` >= 88360.22
- **A**tingível: Gap R$51.884 — recuperável via overdue + corte despesas
- **R**elevante: Runway atual ~2,5 dias — risco de não pagar folha
- **T**emporal: Até 31/05/2026 (47 dias)
- Ação semana 1: ligar para todos os inadimplentes antes de D+7

**META 2 — DESPESAS (30 DIAS 🟡)**
- **S**: Reduzir despesas mensais de R$439.030 para R$350.000
- **M**: Soma bank_transactions.amount < 0 no mês < 350000
- **A**: Identificar R$89k de cortes entre variáveis e adiáveis
- **R**: Despesas > MRR é insustentável — resultado negativo todo mês
- **T**: Até 30/06/2026
- Ação: mapear top 10 despesas do mês anterior

**META 3 — INADIMPLÊNCIA (60 DIAS 🟡)**
- **S**: Reduzir overdue para < 20% do MRR
- **M**: `SUM(net_value) FROM receivable_accounts WHERE status NOT IN ('paga','cancelada') AND due_date < TODAY` / 270586.96 <= 0.20
- **A**: Ativar régua de cobrança automatizada no Conecta PRO
- **R**: Overdue elevado reduz previsibilidade do fluxo de caixa
- **T**: Até 31/07/2026

**META 4 — MARGEM BRUTA (90 DIAS 🟡)**
- **S**: Atingir margem bruta 28%
- **M**: (receita - cpv) / receita >= 0.28
- **A**: Reajuste Kit Mensal + migração contratos humanizados → CNPJ 2 (Simples)
- **R**: Gap vs benchmark setorial (25%): -7pp = -R$18.941/mês perdidos
- **T**: Até 31/07/2026
- Ação: enviar proposta reajuste para clientes Kit Mensal até 30/04

### CONSULTAS ACOMPANHAMENTO
```sql
-- Status das 4 metas em uma query
SELECT
    (SELECT round(current_balance::numeric,2) FROM bank_accounts WHERE bank_code='077') as m1_saldo_atual,
    88360.22 as m1_meta,
    (SELECT round(sum(ABS(amount))::numeric,2) FROM bank_transactions
     WHERE amount<0 AND date_trunc('month',transaction_date)=date_trunc('month',CURRENT_DATE)) as m2_despesas_mes,
    350000 as m2_meta,
    (SELECT round(sum(net_value)::numeric,2) FROM receivable_accounts
     WHERE status NOT IN ('paga','cancelada') AND due_date < CURRENT_DATE) as m3_overdue,
    round(270586.96 * 0.20, 2) as m3_meta_max;
```

### SAÍDA OBRIGATÓRIA
```json
{
  "metas_smart": [
    {
      "meta": "liquidez",
      "prazo": "2026-05-31",
      "valor_atual": 88684.29,
      "valor_meta": 88360.22,
      "gap": -51883.95,
      "status": "atrasado",
      "acao_imediata": ""
    }
  ],
  "acao_imediata_hoje": ""
}
```
