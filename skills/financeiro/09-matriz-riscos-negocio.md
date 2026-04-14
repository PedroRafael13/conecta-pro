---
name: matriz-riscos-negocio
agent: RiskMonitorAgent
prioridade: ALTA
versao: 2.0
---

# Skill 09 — Matriz de Riscos da Conecta Mais

### RISCOS FINANCEIROS (estado atual)
| Risco | Prob | Impacto | Score | Status |
|-------|------|---------|-------|--------|
| Saldo < 1x custo fixo (runway < 15d) | ALTA | CRÍTICO | 🔴 | ATIVO AGORA |
| Overdue > 50% MRR | ALTA | CRÍTICO | 🔴 | Verificar no banco |
| Perda de 1 cliente > 10% MRR | MÉDIA | ALTO | 🟡 | Monitorar |
| Reajuste CCT sem repasse | BAIXA | ALTO | 🟡 | Contratos sem cláusula |
| DARF vencendo sem provisão | MÉDIA | ALTO | 🟡 | Lucro Real trimestral |

### RISCOS OPERACIONAIS
| Risco | Score |
|-------|-------|
| Vigilante CLT doente sem substituto | 🟡 |
| Equipamento CFTV falha em contrato de manutenção | 🟡 |
| Downtime Conecta PRO (VPS Hostinger KV4) | 🟡 |

### RISCOS LEGAIS
- LGPD: imagens de câmeras nos condomínios
- Compliance Lucro Real: apuração trimestral (atual: 100% ✅)
- PSEG/AM: licença vigilância particular

### SAÍDA OBRIGATÓRIA
```json
{
  "health_score_risco": 0,
  "riscos_criticos_ativos": [],
  "indicadores_semaforo": {
    "saldo_atual": 36476.27,
    "saldo_minimo": 88360.22,
    "liquidez_ratio": 0.41,
    "alerta_liquidez": true
  },
  "top_3_acoes_imediatas": [],
  "proximo_vencimento_critico": ""
}
```

### CONSULTAS SQL
```sql
SELECT
    (SELECT round(current_balance::numeric,2) FROM bank_accounts WHERE bank_code='077') as saldo,
    (SELECT round(sum(net_value)::numeric,2) FROM payable_accounts
     WHERE status NOT IN ('pago','cancelado') AND due_date <= CURRENT_DATE+7) as pagar_7d,
    (SELECT round(sum(net_value)::numeric,2) FROM receivable_accounts
     WHERE status NOT IN ('paga','cancelada') AND due_date < CURRENT_DATE) as overdue;
```
