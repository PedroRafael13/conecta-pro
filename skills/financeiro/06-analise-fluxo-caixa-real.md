---
name: analise-fluxo-caixa-real
agent: CashflowPredictorAgent
prioridade: CRITICA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
mrr_bruto: 270586.96
saldo_inter: 88684.29
---

# Skill 06 — Analise de Fluxo de Caixa Real
## Conecta Mais | Banco Inter 077 unico | 2.875 transacoes jan-abr/2026

### SNAPSHOT ATUAL (14/04/2026)

| Indicador | Valor | Status |
|-----------|-------|--------|
| Saldo Inter | R$88.684,29 | VERMELHO |
| Liquidez (saldo/custo_mensal) | 0.15x | CRITICO |
| Runway (dias) | ~5-7 dias util | EMERGENCIA |
| MRR pendente de receber | R$270.087,00 | D+4 (vence D+10) |
| Overdue real >30d | R$46.117,28 | 2 clientes |
| Payable vencido | R$141.651,43 | 16 contas |

**O caixa atual NAO cobre os pagamentos vencidos (R$141.651,43 > R$88.684,29).**
**Dependencia total do recebimento do MRR de abril (D+10 a D+15).**

### HISTORICO REAL EXTRATO INTER (jan-abr/2026)

| Mes | Entradas | Saidas | Resultado | Folha |
|-----|----------|--------|-----------|-------|
| Jan/2026 | R$237.826,40 | R$245.271,97 | -R$7.445,57 | R$166.089,72 |
| Fev/2026 | R$247.649,26 | R$258.214,72 | -R$10.565,46 | R$166.512,49 |
| Mar/2026 | R$495.973,25 | R$439.030,38 | +R$56.942,87 | R$148.468,89 |
| Abr/2026 (13d) | R$150.242,66 | R$124.042,61 | +R$26.200,05 | R$92.505,69 |
| **YTD** | **R$1.131.691,57** | **R$1.066.559,68** | **+R$65.131,89** | **R$573.576,79** |

**Analise:**
- Jan/Fev: resultado negativo — entradas < MRR porque clientes atrasam pagamento
- Mar: entrada dupla (recebimentos acumulados fev+mar) — nao representa realidade
- Abr: positivo ate D+13, mas MRR de abr ainda nao entrou (R$270k pendente)

### CICLO FINANCEIRO CONECTA MAIS

```
Dia 24-28: Emissao NFS-e do mes corrente
Dia 28-31: Envio de cobrancas aos clientes
────────────────────────────────────────────
Mes seguinte:
Dia 01-05: Folha CLT (D+5 util) → SAIDA R$148-166k
Dia 05-07: FGTS (guia SEFIP)    → SAIDA ~R$11k
Dia 10-15: Recebiveis chegam    → ENTRADA R$270k
Dia 15-20: Fornecedores fixos   → SAIDA ~R$15k
Dia 20-25: Impostos (DARF, GPS) → SAIDA ~R$11k
────────────────────────────────────────────
JANELA DE RISCO: Dias 1-9 (folha paga, MRR nao entrou)
JANELA POSITIVA: Dias 10-15 (MRR entra, proximo ciclo)
```

**MESES CRITICOS:**
- Dezembro: pagamento 13o salario (+R$148-166k extra em saidas)
- Janeiro: atraso de recebimento (MRR de dez emitido no dia 28-31)
- Julho: ferias coletivas aumentam custo

### OVERDUE REAL — STATUS 14/04/2026

| Cliente | Valor | Vencimento | Dias | Status |
|---------|-------|-----------|------|--------|
| Laranjeiras Village | R$40.417,28 | 15/03/2026 | 30d | parcial |
| Gelain | R$5.700,00 | 15/03/2026 | 30d | pendente |
| **Total >30d** | **R$46.117,28** | | | |
| Faturas abr/2026 (8 clientes) | R$270.087,00 | 10/04/2026 | 4d | pendente |

Faturas de abril vencidas em D+4 sao NORMAIS (prazo ate D+15).
Overdue real de risco: R$46.117,28 (Laranjeiras parcial + Gelain).

### PAYABLE VENCIDO — STATUS 14/04/2026

| Total vencido | R$141.651,43 |
|---|---|
| Quantidade de contas | 16 |
| Prioridade 1 (folha/encargos) | identificar na tabela |
| Prioridade 2 (financiamentos) | Toyota + C6 |
| Prioridade 3 (fornecedores) | Cruz Q., Portte |

**SALDO R$88.684,29 < PAYABLE VENCIDO R$141.651,43 — DEFICIT DE CAIXA IMEDIATO.**

### SEMAFORO DE CAIXA — PARAMETROS CONECTA MAIS

| Cor | Condicao | Acao |
|-----|---------|------|
| VERDE | Saldo > R$440.095 (2x custo mensal) | Normal |
| AMARELO | Saldo R$220.047 – R$440.095 (1x–2x) | Monitorar diario |
| LARANJA | Saldo R$88.000 – R$220.047 (0,4x–1x) | Antecipar recebiveis |
| VERMELHO | Saldo < R$88.000 (< 0,4x) | **ESTADO ATUAL** — acao imediata |

**Estado atual: VERMELHO PROFUNDO (0.15x)**

### ACOES IMEDIATAS (baseadas no estado atual)

1. **Cobrar Laranjeiras Village** (R$40.417,28 parcial, 30d):
   Contato sindico: proposta de quitacao em 3 parcelas ou desconto 2% pagamento total ate 17/04.

2. **Cobrar Gelain** (R$5.700,00, 30d):
   PIX imediato chave CNPJ 35.710.481/0001-03, conta Inter.

3. **Priorizar recebimento das 8 faturas de abril**:
   Enviar cobrancas via WhatsApp + email para vencimento 10/04 (ja vencidas D+4).

4. **Negociar prazo com fornecedores**:
   Cruz Queiroz, Portte Contabil: solicitar extensao ate dia 20/04 (apos entrada do MRR).

### PROJECAO PROXIMOS 30 DIAS

```
Saldo inicial (14/04):       R$  88.684,29
+ Recebiveis abr (D+10-15):  R$270.087,00 (assumindo 95% recebimento)
- Folha abr (D+5 ja pago):   R$        0  (pago parcialmente: R$92.505)
- Payable vencido critico:   R$(141.651,43) (a pagar após MRR entrar)
- Folha mai (D+5 de mai):    R$(160.357,03)
                              ─────────────
Saldo estimado D+30:         R$   4.049,81 — CRITICO

Se recebimento do MRR for apenas 80%:
Saldo D+30:                  R$  (49.986,09) — NEGATIVO
```

### CONSULTAS SQL

```sql
-- Fluxo diario dos proximos 30 dias (recebiveis + pagaveis)
SELECT
    data_vencimento as data,
    'entrada' as tipo,
    round(net_value::numeric, 2) as valor,
    description
FROM receivable_accounts
WHERE status NOT IN ('paga', 'cancelada')
AND data_vencimento BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
UNION ALL
SELECT
    due_date,
    'saida',
    round(net_value::numeric, 2),
    description
FROM payable_accounts
WHERE status NOT IN ('paga', 'cancelada')
AND due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
ORDER BY data, tipo DESC;

-- Saldo projetado dia a dia
WITH fluxo AS (
    SELECT data_vencimento as data, net_value as valor
    FROM receivable_accounts
    WHERE status NOT IN ('paga','cancelada')
    AND data_vencimento BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
    UNION ALL
    SELECT due_date, -net_value
    FROM payable_accounts
    WHERE status NOT IN ('paga','cancelada')
    AND due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
)
SELECT
    data,
    round(sum(valor)::numeric, 2) as fluxo_dia,
    round((88684.29 + sum(sum(valor)) OVER (ORDER BY data))::numeric, 2) as saldo_acumulado
FROM fluxo
GROUP BY data
ORDER BY data;
```
