---
name: plano-acao-90-dias
agent: FinancialAdvisorAgent
prioridade: ALTA
versao: 2.0
---

# Skill 11 — Plano de Ação 90 Dias — Conecta Mais (abril-junho/2026)

### FASE 1 — Estabilização (Dias 1-30): LIQUIDEZ
Meta: Saldo > R$88.360,22 (1x custo fixo mensal)
- Ativar cobrança overdue — recuperar R$52k+ em 30 dias
- Negociar antecipação com clientes chave
- Cortar custos variáveis não essenciais (R$439k/mês é insustentável)
- Marco D30: saldo > R$88k ✓

### FASE 2 — Estruturação (Dias 31-60): MARGEM
Meta: Margem bruta > 25%
- Revisar precificação Kit Mensal com impacto CCT 2026
- Propor reajuste para contratos sem cláusula automática
- 10 clientes = 10 negociações individuais
- Marco D60: 80% contratos com cláusula de reajuste ✓

### FASE 3 — Crescimento (Dias 61-90): EXPANSÃO
Meta: +2 novos contratos (portaria remota — maior margem)
- Portaria remota: MC estimada 45% vs Kit Mensal ~18%
- Qualificar 5 leads condomínios em Manaus
- Marco D90: 1 contrato assinado ✓

### KPIs DE ACOMPANHAMENTO
| Indicador | Atual | Meta D30 | Meta D60 | Meta D90 |
|-----------|-------|----------|----------|----------|
| Saldo Inter | R$88.684 | R$120.000 | R$120.000 | R$176.000 |
| Despesas/mês | R$439.030 | R$350.000 | R$320.000 | R$300.000 |
| MRR | R$270.587 | R$270.587 | R$270.587 | R$290.000 |
| Contratos | 10 | 10 | 10 | 12 |
| Runway | ~2,5d | 7,5d | 11d | 17,5d |

### AÇÕES IMEDIATAS (Semana 1)
1. Ligar para todos os inadimplentes — hoje
2. Mapear contratos sem cláusula reajuste — até sexta
3. Identificar 3 despesas cortáveis imediatamente
4. Analisar se despesas R$439k incluem pagamentos transitórios

### CONSULTAS ACOMPANHAMENTO
```sql
-- Evolução saldo semanal
SELECT date_trunc('week', transaction_date) as semana,
       sum(amount) as fluxo_semana
FROM bank_transactions WHERE bank_account_id IN
    (SELECT id FROM bank_accounts WHERE bank_code='077')
GROUP BY 1 ORDER BY 1 DESC LIMIT 8;
```
