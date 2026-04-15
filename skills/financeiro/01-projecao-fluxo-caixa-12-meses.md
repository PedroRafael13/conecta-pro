---
name: projecao-fluxo-caixa-12-meses
agent: CashflowPredictorAgent
prioridade: CRITICA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
---

# Skill 01 — Projecao de Fluxo de Caixa 12 Meses
## Conecta Mais — Seguranca Patrimonial & Eletronica | Lucro Real

### ESTADO ATUAL (dados reais 14/04/2026)

| Indicador | Valor | Status |
|-----------|-------|--------|
| MRR bruto (billing_rules) | R$270.586,96 | 10 contratos ativos |
| Saldo Inter (bank_accounts) | R$88.684,29 | unico banco |
| Folha media mensal (extrato) | R$160.357,03 | jan-mar/2026 |
| Custo total medio mensal | ~R$250.000,00 | Jan+Fev media |
| Liquidez atual | 0.15x | CRITICO — < 1x |
| Regime fiscal | Lucro Real | desde jan/2026 |
| Overdue >30d | R$46.117,28 | Laranjeiras + Gelain |
| Overdue <15d (aguardando) | R$270.087,00 | faturas abr/2026 D+4 |

**Status semaforo: VERMELHO — saldo cobre menos de 1 semana de custo**

### CLIENTES E MRR REAL (billing_rules + NFS-e marco/2026)

| Cliente | CNPJ | Tipo | Bruto/mes |
|---------|------|------|-----------|
| Ideal Flores da Cidade | 23.147.782/0001-91 | Kit Mensal CLT | R$65.842,42 |
| Laranjeiras Village | 24.632.786/0001-28 | Kit Mensal CLT | R$42.544,50 |
| Mirante das Flores | 52.605.708/0001-70 | Kit Mensal CLT | R$42.255,80 |
| Prime Arena | 47.405.340/0001-66 | Kit Mensal CLT | R$40.466,50 |
| Villa dos Passaros | 13.221.953/0001-21 | Kit Mensal CLT | R$37.338,33 |
| Villa Dei Fiori | 02.153.384/0001-08 | Kit Mensal CLT | R$25.592,71 |
| Michelangelo | 04.911.208/0001-13 | Kit Mensal CLT | R$8.346,70 |
| Gelain | 00.736.037/0001-82 | Portaria Remota | R$6.000,00 |
| Parise Village | 34.857.941/0001-68 | Manutencao CFTV | R$1.700,00 |
| Green Hills | 08.063.476/0001-83 | Manutencao CFTV | R$500,00 |
| **TOTAL** | | | **R$270.586,96** |

**EXCLUIDO:** Life Centro (R$1.500,00) — inativa desde 14/04/2026 (nao consta nas 13 NFS-e mar/2026)

### HISTORICO REAL (extrato Banco Inter jan-abr/2026)

| Mes | Entradas | Saidas | Resultado | Observacao |
|-----|----------|--------|-----------|------------|
| Jan/2026 | R$237.826,40 | R$245.271,97 | -R$7.445,57 | Ferias — pagamentos atrasados |
| Fev/2026 | R$247.649,26 | R$258.214,72 | -R$10.565,46 | Normal — folha R$166.512 |
| Mar/2026 | R$495.973,25 | R$439.030,38 | +R$56.942,87 | Recebimentos acumulados + pagamentos acumulados |
| Abr/2026 (13d) | R$150.242,66 | R$124.042,61 | +R$26.200,05 | Parcial |

**Media real Jan+Fev (mais representativos):**
- Entradas: R$242.737,83/mes
- Saidas: R$251.743,35/mes
- Resultado medio: -R$9.005,52/mes (DEFICIT antes de receber MRR completo)

### PREMISSAS DA PROJECAO

**Receita (entradas):**
- MRR bruto: R$270.586,96
- ISS Manaus (5%): -R$13.529,35
- PIS/COFINS LR nao-cumulativo (9,25%): -R$25.029,29
- **MRR liquido estimado: R$232.028,32/mes**
- Prazo de recebimento: D+5 a D+15 apos emissao NFS-e (dia 24-28 do mes)

**Custos fixos mensais (extrato real):**
- Folha CLT 52 funcionarios: R$160.357,03 (media jan-mar)
- Fornecedores (media): R$15.150,97/mes
- Outros pagamentos (media): R$14.903,14/mes
- Impostos (media): R$10.781,12/mes
- Pro-labore (media): R$8.987,50/mes
- Operacional (media): R$7.828,33/mes
- Financiamentos (media): R$3.039,47/mes
- **TOTAL CUSTOS ESTIMADO: ~R$220.047,56/mes**

### SAZONALIDADE MANAUS (multiplicador sobre MRR base)

| Mes | Mult | Motivo |
|-----|------|--------|
| Jan | 0.95 | Ferias — aprovacoes atrasadas, pagamentos postergados |
| Fev | 1.00 | Normal pos-CCT vigente |
| Mar | 1.00 | Normal |
| Abr | 1.02 | Retomada pos-carnaval + renovacoes Q1 |
| Mai | 1.00 | Normal |
| Jun | 0.98 | Festas juninas — atrasos leves |
| Jul | 0.97 | Ferias escolares — sindicos ausentes |
| Ago | 1.00 | Normal |
| Set | 1.00 | Normal |
| Out | 1.01 | Pre-fim de ano |
| Nov | 1.03 | Renovacoes contratuais anuais |
| Dez | 0.88 | 13o salario impacta caixa (-R$13.363,08 extra) |

### ALERTAS AUTOMATICOS

- Saldo < R$220.047 → ALERTA VERMELHO (< 1x custo mensal)
- Saldo < R$440.095 → ALERTA AMARELO (< 2x custo mensal)
- Dezembro: provisionar 13o + ferias = +R$26.726 em saidas
- Janeiro: atraso de recebimento (MRR ref dez chega em jan)
- Qualquer mes com resultado negativo: notificar Jordan Jesus

### SAIDA OBRIGATORIA

```json
{
  "periodo": "MM/YYYY a MM/YYYY",
  "premissas": {
    "mrr_bruto": 270586.96,
    "mrr_liquido_estimado": 232028.32,
    "saldo_inicial": 88684.29,
    "custo_mensal_estimado": 220047.56,
    "folha_mensal_media": 160357.03
  },
  "projecao_mensal": [
    {
      "mes": "05/2026",
      "receita_bruta": 0,
      "deducoes_fiscais": 0,
      "receita_liquida": 0,
      "custo_total": 0,
      "resultado_liquido": 0,
      "saldo_acumulado": 0,
      "multiplicador_sazonal": 1.0,
      "alerta": null
    }
  ],
  "cenarios": {
    "base": {"taxa_crescimento_anual": 0.0, "saldo_final_12m": 0},
    "otimista": {"novo_contrato_q3": 30000, "saldo_final_12m": 0},
    "pessimista": {"perda_contrato": -42544.50, "saldo_final_12m": 0}
  },
  "alertas": [],
  "recomendacoes": []
}
```

### CONSULTAS SQL

```sql
-- Saldo atual e disponivel
SELECT bank_name, current_balance, available_balance, updated_at
FROM bank_accounts WHERE bank_code = '077';

-- Historico real mensal completo
SELECT
    to_char(date_trunc('month', transaction_date), 'MM/YYYY') as mes,
    round(sum(CASE WHEN amount > 0 THEN amount ELSE 0 END)::numeric, 2) as entradas,
    round(sum(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END)::numeric, 2) as saidas,
    round(sum(amount)::numeric, 2) as resultado
FROM bank_transactions
GROUP BY date_trunc('month', transaction_date)
ORDER BY 1;

-- MRR atual (billing_rules ativas)
SELECT name, base_value
FROM billing_rules WHERE status = 'ativa'
ORDER BY base_value DESC;

-- Recebiveis pendentes proximos 30 dias
SELECT description, net_value, due_date, status
FROM receivable_accounts
WHERE status NOT IN ('paga', 'cancelada')
AND due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
ORDER BY due_date;
```
