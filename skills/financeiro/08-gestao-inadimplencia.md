---
name: gestao-inadimplencia
agent: CollectionNegotiatorAgent
prioridade: CRITICA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
mrr_bruto: 270586.96
saldo_inter: 88684.29
---

# Skill 08 — Gestao de Inadimplencia
## Conecta Mais — Regua de Cobranca para 10 Condominios Manaus

### ESTADO ATUAL — 14/04/2026

| Status | Clientes | Valor | Acao |
|--------|----------|-------|------|
| Vencido >30d | 2 (Laranjeiras + Gelain) | R$46.117,28 | URGENTE |
| Vencido D+4 (normal) | 8 clientes | R$270.087,00 | Cobranca rotina |
| **Total overdue** | **10** | **R$316.704,24** | |

### CLIENTES CRITICOS (overdue >30d)

**Laranjeiras Village (CNPJ: 24.632.786/0001-28)**
- Valor: R$40.417,28 (fatura marco/2026, status: parcial)
- Vencimento: 15/03/2026 — 30 dias em atraso
- Ticket mensal: R$42.544,50
- Sindico: verificar contato em clients.phone / clients.email
- PIX recebimento: CNPJ 35.710.481/0001-03 (Banco Inter 077)
- Proposta: parcelamento 3x ou desconto 2% quitacao ate 17/04

**Gelain (CNPJ: 00.736.037/0001-82)**
- Valor: R$5.700,00 (fatura marco/2026, status: pendente)
- Vencimento: 15/03/2026 — 30 dias em atraso
- Ticket mensal: R$6.000,00 (portaria remota)
- Contato prioritario: PIX imediato
- Observacao: contrato de portaria remota — nao ha mao de obra in loco como alavanca

### REGUA DE COBRANCA CONECTA MAIS

**Fase 1 — Cobranca Amigavel (D+1 a D+7)**

| Dia | Canal | Mensagem |
|-----|-------|---------|
| D+1 | WhatsApp (sindico) | "Ola [Nome], identificamos que a fatura de [mes] no valor de R$[X] venceu ontem. Por gentileza, realize o pagamento via PIX CNPJ 35.710.481/0001-03 (Banco Inter). Qualquer duvida, estou a disposicao. Atenciosamente, Jordan Jesus — Conecta Mais." |
| D+3 | WhatsApp | "Bom dia [Nome], gentileza verificar a pendencia anterior. Podemos ajudar com alguma questao na fatura?" |
| D+7 | Ligacao | Tom parceiro: verificar se ha problema especifico (erro de NFS-e, dados bancarios, aprovacao em assembleia) |

**Fase 2 — Cobranca Formal (D+8 a D+20)**

| Dia | Canal | Acao |
|-----|-------|------|
| D+8 | Email formal | Carta de cobranca com dados da NFS-e, valor corrigido (multa 2% + juros 1%/mes CCT) |
| D+15 | Email + WhatsApp | Segunda notificacao formal — prazo 5 dias uteis |
| D+20 | Visita presencial | Jordan Jesus ou gestor direto vai ao condominio + reuniao com sindico |

**Fase 3 — Escalada (D+21 a D+60)**

| Dia | Canal | Acao |
|-----|-------|------|
| D+21 | Email juridico | Cruz Queiroz Advogados envia notificacao extrajudicial |
| D+30 | Cruz Queiroz | Notificacao formal 10 dias para pagamento |
| D+45 | CFTV apenas | Suspensao de manutencao CFTV (NUNCA suspender mao de obra) |
| D+60 | Judicial | Acao de cobranca + protesto do titulo |

### REGRAS DE COBRANCA PARA CONDOMINIOS MANAUS

1. **Nunca ameacar suspensao de mao de obra (vigilantes):**
   Risco de vida para moradores. Proibido contratualmente.
   Apenas CFTV/manutencao pode ser suspenso.

2. **Assembleias condominiais:**
   Pagamento frequentemente depende de aprovacao em assembleia.
   Antecipar NFS-e ate dia 20 para dar tempo de aprovacao.

3. **Sindico profissional vs voluntario:**
   - Profissional: ligacao direta funciona bem
   - Voluntario (morador): preferir WhatsApp + email

4. **Parcelamento:**
   - Dividas ate R$5.000: 2 parcelas
   - Dividas R$5.000 - R$20.000: 3 parcelas
   - Dividas > R$20.000: ate 6 parcelas com juros 1%/mes

5. **Desconto para quitacao:**
   - Multa (2%): negociar remocao se pagar em 48h
   - Juros (1%/mes): negociar remocao para clientes sem historico de atraso

6. **Chave PIX recebimento:**
   CNPJ: 35.710.481/0001-03
   Banco Inter 077 | Agencia 0001 | Conta 370990072-2

### PRIORIZACAO DE COBRANCA

```
Score = (dias_vencido * 0.40) + (valor_R$ / 1000 * 0.40) + (historico_atraso * 0.20)

P1 — URGENTE: Laranjeiras Village
  Score = (30 * 0.40) + (40.4 * 0.40) + (historico * 0.20) = 12 + 16.2 = 28.2
  Acao: contato IMEDIATO Jordan Jesus pessoalmente

P2 — URGENTE: Gelain
  Score = (30 * 0.40) + (5.7 * 0.40) = 12 + 2.3 = 14.3
  Acao: PIX request via WhatsApp hoje

P3 — ROTINA: 8 faturas D+4 (R$270.087)
  Vencimento D+10 = 18/04/2026
  Acao: envio de cobranca padrao via WhatsApp no dia 18/04
```

### MODELOS DE MENSAGEM

**WhatsApp D+1 (fatura vencida ontem):**
```
Bom dia, [Nome do Sindico]! 😊

Passando para informar que a fatura de servicos de
segurança do [Condominio] referente a [mes/ano],
no valor de R$[X], venceu ontem, dia [data].

Segue dados para pagamento:

PIX CNPJ: 35.710.481/0001-03
Banco Inter | Ag. 0001 | CC 370990072-2

Qualquer duvida, estou a disposicao!

Atenciosamente,
Jordan Jesus — Conecta Mais
📱 [telefone]
```

**Email formal D+8:**
```
Assunto: Notificacao de Cobranca — [Condominio] — Ref. [mes/ano]

Prezado(a) Sr(a). [Nome],

Viemos por meio desta comunicar o vencimento, em [data],
da fatura n° [numero NFS-e] referente aos servicos de
seguranca patrimonial prestados em [mes/ano].

Valor original: R$[X]
Multa (2%): R$[Y]
Juros (1%/mes): R$[Z]
TOTAL ATUALIZADO: R$[TOTAL]

Solicitamos a regularizacao em ate 5 (cinco) dias uteis, sob
pena de encaminhamento para o setor juridico da Conecta Mais.

[...informacoes bancarias...]

Respeitosamente,
Jordan Jesus
Conecta Mais — Seguranca e Tecnologia
CNPJ 35.710.481/0001-03
```

### CONSULTAS SQL

```sql
-- Inadimplentes por cliente, valor e dias
SELECT
    ra.description,
    ra.net_value,
    ra.due_date,
    CURRENT_DATE - ra.due_date as dias_vencido,
    ra.status,
    CASE
        WHEN CURRENT_DATE - ra.due_date > 30 THEN 'P1_URGENTE'
        WHEN CURRENT_DATE - ra.due_date > 15 THEN 'P2_ALTA'
        WHEN CURRENT_DATE - ra.due_date > 7  THEN 'P3_MEDIA'
        ELSE 'P4_ROTINA'
    END as prioridade,
    round(ra.net_value * 0.02, 2) as multa_2pct,
    round(ra.net_value * 0.01 * (CURRENT_DATE - ra.due_date) / 30.0, 2) as juros_acumulados
FROM receivable_accounts ra
WHERE ra.status NOT IN ('paga', 'cancelada')
AND ra.due_date < CURRENT_DATE
ORDER BY ra.net_value DESC, dias_vencido DESC;

-- Total overdue por faixa de atraso
SELECT
    CASE
        WHEN CURRENT_DATE - due_date <= 7   THEN '01_ate_7d'
        WHEN CURRENT_DATE - due_date <= 15  THEN '02_8_15d'
        WHEN CURRENT_DATE - due_date <= 30  THEN '03_16_30d'
        WHEN CURRENT_DATE - due_date <= 60  THEN '04_31_60d'
        ELSE '05_acima_60d'
    END as faixa,
    count(*) as qtd,
    round(sum(net_value)::numeric, 2) as total,
    round(sum(net_value) / (SELECT sum(net_value) FROM receivable_accounts
        WHERE status NOT IN ('paga','cancelada') AND due_date < CURRENT_DATE) * 100, 1) as pct_total
FROM receivable_accounts
WHERE status NOT IN ('paga', 'cancelada')
AND due_date < CURRENT_DATE
GROUP BY 1 ORDER BY 1;

-- Historico de pagamentos por cliente (para calibrar abordagem)
SELECT
    description,
    count(*) as total_faturas,
    count(CASE WHEN status = 'paga' THEN 1 END) as pagas,
    count(CASE WHEN payment_date > due_date THEN 1 END) as pagas_com_atraso,
    round(avg(CASE WHEN payment_date > due_date
        THEN payment_date - due_date END)::numeric, 0) as dias_atraso_medio
FROM receivable_accounts
WHERE payment_date IS NOT NULL
GROUP BY description
ORDER BY dias_atraso_medio DESC NULLS LAST;
```
