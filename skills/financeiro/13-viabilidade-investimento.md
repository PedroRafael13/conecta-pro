---
name: viabilidade-investimento
agent: FinancialAdvisorAgent
prioridade: MÉDIA
versao: 2.0
---

# Skill 13 — Análise de Viabilidade de Investimento — Conecta Mais

### CONTEXTO ATUAL (restrições obrigatórias)
- Saldo R$88.684,29 — CONDIÇÃO BLOQUEANTE para qualquer investimento
- Custo de capital Inter (crédito PJ): ~1,8-2,5%/mês
- Custo de oportunidade: qualquer R$ investido compete com custo fixo
- Payback máximo aceitável: 12 meses
- Condição mínima: saldo > R$88.360,22 antes de qualquer investimento

### INVESTIMENTOS TÍPICOS CONECTA MAIS
| Investimento | Ticket | Receita gerada | Payback |
|---|---|---|---|
| Kit CFTV (câmeras + DVR + instalação) | R$8.000-15.000 | +R$1.200/mês | 7-12 meses |
| Veículo operacional (Fiat Fiorino) | R$65.000 | -R$3.000/mês (economia) | 21 meses |
| VPS upgrade (Hostinger KV4→KV8) | R$300/mês | +R$0 direto (SLA) | N/A (custo) |
| Treinamento NR-35 vigilantes | R$2.500 | +habilitação altura | ROI contrato |
| Portaria remota (hardware cliente) | R$12.000 | +R$2.800/mês | 4,3 meses |

### FÓRMULAS DE ANÁLISE
```
Payback_simples = Investimento / Receita_adicional_mensal
ROI_12m = ((Receita_adicional_12m - Investimento) / Investimento) * 100
Break_even = Investimento / MC_mensal_gerada
TIR (12 meses) = usar fluxo de caixa descontado
```

### REGRA DE DECISÃO
| Payback | ROI 12m | Recomendação |
|---------|---------|---|
| < 6 meses | > 100% | fazer_agora (desde que saldo OK) |
| 6-12 meses | 50-100% | fazer_com_condicoes |
| 12-24 meses | 0-50% | adiar |
| > 24 meses | < 0% | nao_fazer |

### SAÍDA OBRIGATÓRIA
```json
{
  "investimento": {"descricao": "", "valor_total": 0, "tipo": "capex|opex"},
  "viabilidade": {
    "payback_meses": 0,
    "roi_12m_pct": 0,
    "break_even_rs": 0,
    "tir_estimada_pct": 0
  },
  "condicao_bloqueante": "saldo_atual < 88360.22",
  "recomendacao": "fazer_agora|fazer_com_condicoes|adiar|nao_fazer",
  "justificativa": "",
  "data_minima_viavel": ""
}
```
