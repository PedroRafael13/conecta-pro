---
name: kpis-financeiros
agent: RiskMonitorAgent,FinancialAdvisorAgent
prioridade: CRITICA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
---

# Skill 07 — KPIs Financeiros Conecta Mais
## Painel de Indicadores em Tempo Real | 14 KPIs Core

### PAINEL EXECUTIVO — ESTADO 14/04/2026

| KPI | Valor Atual | Meta | Alerta | Status |
|-----|-------------|------|--------|--------|
| MRR bruto | R$270.586,96 | >R$280k | <R$250k | ATENCAO |
| Saldo Inter | R$88.684,29 | >R$440k | <R$220k | VERMELHO |
| Liquidez | 0.15x | >2.0x | <1.0x | VERMELHO |
| Runway (dias) | ~6 dias | >60 dias | <30 dias | VERMELHO |
| Overdue total | R$316.704,24 | <R$27k (10%) | >R$54k (20%) | VERMELHO |
| Overdue real >30d | R$46.117,28 | <R$13.5k (5%) | >R$27k (10%) | VERMELHO |
| Payable vencido | R$141.651,43 | R$0 | >R$50k | VERMELHO |
| Margem bruta caixa | 34,9% | >30% | <20% | VERDE |
| EBITDA estimado | 19,1% anual | >15% | <8% | VERDE |
| Margem liquida estim. | 4,4% | >8% | <3% | AMARELO |
| Contratos ativos | 10 | >12 | <8 | ATENCAO |
| Churn YTD | 0% | 0% | >10% | VERDE |
| Compliance fiscal LR | 100% | 100% | <100% | VERDE |
| Health Score | 22/100 | >70 | <40 | VERMELHO |

### HEALTH SCORE — ALGORITMO (0-100)

```python
def calcular_health_score(dados: dict) -> dict:
    score = 100
    alertas = []
    deducoes = []

    # LIQUIDEZ (peso 30)
    liquidez = dados['saldo'] / dados['custo_mensal']
    if liquidez < 0.5:
        score -= 30
        alertas.append("CRITICO: saldo cobre menos de 15 dias de operacao")
        deducoes.append(("liquidez_critica", -30))
    elif liquidez < 1.0:
        score -= 20
        alertas.append("ALERTA: saldo abaixo de 1 mes de custo fixo")
        deducoes.append(("liquidez_baixa", -20))
    elif liquidez < 2.0:
        score -= 10
        deducoes.append(("liquidez_media", -10))

    # INADIMPLENCIA (peso 25)
    overdue_pct = dados['overdue_30d'] / dados['mrr_bruto'] * 100
    if overdue_pct > 15:
        score -= 25
        alertas.append(f"CRITICO: inadimplencia {overdue_pct:.1f}% do MRR")
        deducoes.append(("inadimplencia_critica", -25))
    elif overdue_pct > 10:
        score -= 15
        alertas.append(f"ALERTA: inadimplencia {overdue_pct:.1f}% do MRR")
        deducoes.append(("inadimplencia_alta", -15))
    elif overdue_pct > 5:
        score -= 8
        deducoes.append(("inadimplencia_media", -8))

    # PAYABLE VENCIDO (peso 20)
    if dados['payable_vencido'] > dados['saldo']:
        score -= 20
        alertas.append("CRITICO: contas a pagar vencem superiores ao saldo")
        deducoes.append(("payable_maior_saldo", -20))
    elif dados['payable_vencido'] > dados['saldo'] * 0.5:
        score -= 10
        deducoes.append(("payable_alto", -10))

    # MARGEM BRUTA (peso 15)
    if dados['margem_bruta_pct'] < 20:
        score -= 15
        alertas.append("CRITICO: margem bruta abaixo de 20%")
        deducoes.append(("margem_critica", -15))
    elif dados['margem_bruta_pct'] < 25:
        score -= 8
        deducoes.append(("margem_baixa", -8))

    # CRESCIMENTO MRR (peso 10)
    if dados.get('mrr_crescimento_mom', 0) < -5:
        score -= 10
        alertas.append("ALERTA: queda de MRR mes a mes")
        deducoes.append(("mrr_caindo", -10))

    return {
        "score": max(0, score),
        "nivel": "CRITICO" if score < 30 else "ALERTA" if score < 50 else "ATENCAO" if score < 70 else "SAUDAVEL",
        "alertas": alertas,
        "deducoes": deducoes
    }

# Estado atual estimado:
# liquidez 0.15x → -30
# overdue_30d R$46.117 / R$270.587 = 17% → -25
# payable vencido R$141.651 > saldo R$88.684 → -20
# margem bruta 34,9% → 0
# Score: 100 - 30 - 25 - 20 = 25/100 (CRITICO)
```

### KPIs DE CRESCIMENTO

| KPI | Tendencia | Observacao |
|-----|----------|-----------|
| MRR crescimento MoM | 0% | Carteira estavel, sem novos contratos Q1/2026 |
| Novos contratos Q1 | 0 | Nenhum novo contrato assinado |
| Churn Q1 | 0% | Nenhuma saida de cliente |
| Ticket medio | R$27.058,70 | Media de 10 contratos |
| Ticket medio Kit Mensal | R$37.483,85 | Media de 7 contratos |
| Concentracao Ideal Flores | 24,3% do MRR | RISCO CONCENTRACAO |

**ALERTA CONCENTRACAO:** Ideal Flores = 24,3% do MRR. Perda deste contrato impacta R$65.842/mes.
Limiar saudavel de concentracao: max 20% em 1 cliente.

### KPIs OPERACIONAIS DE SEGURANCA

| KPI | Atual | Meta | Fonte |
|-----|-------|------|-------|
| Funcionarios ativos | 52 | 50-55 | RH |
| Funcionarios por contrato | 5,2 | - | calculado |
| Turnover anual | verificar | <20% | RH |
| Ocorrencias mes | verificar | <5 | DP |
| SLA contratual cumprido | verificar | >95% | operacional |

### HISTORICO HEALTH SCORE ESTIMADO

| Mes | Score | Nivel | Evento |
|-----|-------|-------|--------|
| Jan/2026 | ~35 | CRITICO | Deficit Jan R$7.446 |
| Fev/2026 | ~30 | CRITICO | Deficit Fev R$10.566 |
| Mar/2026 | ~55 | ATENCAO | Superavit Mar R$56.943 (receb. acumulados) |
| Abr/2026 | ~25 | CRITICO | Saldo R$88.684 + payable R$141.651 vencido |

### CONSULTAS SQL

```sql
-- Health score em tempo real
WITH metricas AS (
    SELECT
        (SELECT round(current_balance::numeric, 2) FROM bank_accounts WHERE bank_code='077') as saldo,
        (SELECT round(sum(base_value)::numeric, 2) FROM billing_rules WHERE status='ativa') as mrr,
        (SELECT round(sum(net_value)::numeric, 2) FROM receivable_accounts
         WHERE status NOT IN ('paga','cancelada') AND due_date < CURRENT_DATE - 30) as overdue_30d,
        (SELECT round(sum(net_value)::numeric, 2) FROM payable_accounts
         WHERE status NOT IN ('paga','cancelada') AND due_date < CURRENT_DATE) as payable_vencido,
        220047.56 as custo_mensal_estimado
)
SELECT
    saldo,
    mrr,
    overdue_30d,
    payable_vencido,
    round(saldo / custo_mensal_estimado, 2) as liquidez_x,
    round(overdue_30d / mrr * 100, 1) as overdue_pct_mrr,
    CASE
        WHEN saldo / custo_mensal_estimado < 0.5 THEN 'CRITICO'
        WHEN saldo / custo_mensal_estimado < 1.0 THEN 'ALERTA'
        WHEN saldo / custo_mensal_estimado < 2.0 THEN 'ATENCAO'
        ELSE 'SAUDAVEL'
    END as status_semaforo
FROM metricas;

-- Concentracao de MRR por cliente
SELECT
    name as contrato,
    base_value as mrr,
    round(base_value / (SELECT sum(base_value) FROM billing_rules WHERE status='ativa') * 100, 1) as pct_mrr
FROM billing_rules
WHERE status = 'ativa'
ORDER BY base_value DESC;
```
