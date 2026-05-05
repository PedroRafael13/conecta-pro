---
name: contratos-operacionais-conecta-mais
description: Três templates de contratos para operação diária da Conecta Mais — contrato simples de serviço (253), estrutura com revisão final (305) e template pronto para editar (318). Adaptados para portaria, CFTV e facilities em Manaus/AM.
---

# Contratos Operacionais (Skills 253 + 305 + 318)

## Por que unificar estas três skills
As skills 253, 305 e 318 fazem a mesma coisa em níveis diferentes de complexidade.
Para a Conecta Mais, mapeamos em três cenários de uso:

| Skill | Quando usar | Complexidade |
|-------|-------------|--------------|
| 253 | Contrato de experiência / kickoff rápido | Simples — 1 página |
| 318 | Template padrão para novos clientes | Médio — 4-6 páginas |
| 305 | Contrato grande com revisão jurídica | Completo — 10+ páginas |

---

## Template 253 — Contrato Rápido (Ordem de Serviço)
Para: primeiro mês, serviços pontuais, emergências operacionais

```
ORDEM DE SERVIÇO — Conecta Mais

Data: [data]
Cliente: [nome do condomínio] | CNPJ: [CNPJ]
Responsável: [síndico]
Serviço: [descrever em 2-3 linhas]
Período: [data início] a [data fim]
Valor: R$[valor] — Pagamento: [forma]
Observações: [escopo, limitações]

Conecta Mais assume responsabilidade apenas pelo escrito acima.
Alterações devem ser formalizadas por escrito.

Assinatura Conecta Mais: _________________ Data: _____
Assinatura Contratante: _________________ Data: _____
```

## Template 318 — Contrato Padrão Conecta Mais

```
Você é especialista em contratos para facilities e segurança patrimonial em Manaus/AM.

Gere contrato padrão para:
**Cliente:** [nome do condomínio]
**Serviço principal:** [Kit Mensal / Portaria Remota / CFTV]
**Postos:** [número] **Turno:** [tipo]
**Valor mensal:** R$[valor]
**Início:** [data]

Use o template padrão da Conecta Mais com:
- Cabeçalho: CONECTAMAIS ELETRONICA LTDA | CNPJ 35.710.481/0001-03
- Cláusula de substituição: prazo máximo 24h para posto crítico
- Reajuste: INPC anual ou CCT (o que for maior)
- Rescisão: 30 dias de aviso ou multa de 1 mês
- Foro: Comarca de Manaus/AM
- 4-6 páginas, linguagem direta
```

## Template 305 — Contrato Completo com Revisão
Para: contratos acima de R$30.000/mês ou com cláusulas especiais

```
Você é advogado especializado em direito empresarial, trabalhista e segurança patrimonial no AM.

Elabore contrato completo para:
**Contratante:** [nome, CNPJ, endereço, representante]
**Valor anual estimado:** R$[valor]
**Particularidades:** [cláusulas especiais solicitadas pelo cliente]

Inclua análise de riscos jurídicos específicos para:
- Responsabilidade em caso de ocorrência no condomínio
- Responsabilidade trabalhista (terceirização — Lei 6019/74)
- Responsabilidade por dados de moradores (LGPD)
- Cláusula de não concorrência com funcionários

Marque com [REVISAR] todas as cláusulas que requerem atenção jurídica específica.
```

## Integração com o Conecta PRO
Todos os contratos gerados devem ser:
1. Salvos como PDF no GED do cliente: /ged/clients/{client_id}/contratos/
2. Registrados no CRM: clients.contract_date, clients.contract_value
3. Enviados por email ao síndico via noreply@conectamais.pro
4. Lembrete automático 60 dias antes do vencimento via BillingAutomatorAgent
