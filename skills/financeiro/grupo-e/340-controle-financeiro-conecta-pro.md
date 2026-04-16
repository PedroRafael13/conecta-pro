---
name: controle-financeiro-conecta-pro
description: Como usar o módulo financeiro do Conecta PRO como ferramenta de controle diário — rotina de conferência de saldo, aprovação de pagamentos, fechamento mensal e geração do DRE gerencial para tomada de decisão.
---

# Controle Financeiro com Conecta PRO (Skill 340 reescrita)

## O Prompt

```
Você é controller financeiro de uma PME de serviços.

Crie a rotina de controle financeiro usando o Conecta PRO:

**Ferramenta:** erp.conectamais.pro | Módulo Financeiro
**Empresa:** JORDAN SANTOS DE JESUS LTDA | 13 clientes | 52 funcionários

ROTINA DIÁRIA (15 minutos):
1. Verificar saldo Inter no dashboard (R$54k atual)
2. Conferir transações não categorizadas (banco_transactions sem categoria)
3. Aprovar pagamentos pendentes acima de R$1.000
4. Verificar inadimplentes: clientes com vencimento hoje/ontem

ROTINA SEMANAL (30 minutos):
1. Conciliação bancária: transações Inter vs. registros no sistema
2. Status dos 10 contratos: algum em atraso?
3. Previsão de caixa 30 dias: fluxo de caixa → projeção

ROTINA MENSAL (2 horas — até dia 5):
1. Fechar competência anterior (justificar saídas Lucro Real)
2. Gerar DRE gerencial (Relatórios → DRE)
3. Emitir NFS-e pendentes (Fiscal → NFS-e)
4. Calcular folha (DP → Folha de Pagamento)
5. Pagar folha via PIX batch (52 funcionários)
6. Analisar margem por tipo de contrato (Custos → Custeio ABC)

Para cada etapa: print da tela do Conecta PRO + interpretação do dado.
```
