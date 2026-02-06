# PRE-MORTEM: Integrações Sólides + Bling + Domínio + GOV.BR

**Data:** 2026-01-15
**Cenário:** É 2026-07-15 (6 meses no futuro). O projeto de integrações falhou. Por quê?

---

## TOP 15 RISCOS CRÍTICOS

### RISCO 1: API do fornecedor não cobre o que precisamos

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (70%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Domínio (principal), Bling (secundário) |
| **Sinais precoces** | Documentação incompleta, endpoints retornando 404, campos ausentes |
| **Mitigação** | Discovery técnico ANTES de implementar. POC com API real em sandbox. |
| **Plano B** | Provedor intermediário (Omie/Nibo para contábil), importação manual com templates |

---

### RISCO 2: Rate limits e bloqueios

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (80%) |
| **Impacto** | MÉDIO-ALTO |
| **Sistemas afetados** | Bling (principal), Sólides |
| **Sinais precoces** | HTTP 429 frequente, lentidão súbita, IP bloqueado |
| **Mitigação** | Rate limiter local respeitando limites. Backoff exponencial. Queue de requests. |
| **Plano B** | Sync em horários de baixo uso. Múltiplos API keys se permitido. Cache agressivo. |

---

### RISCO 3: Mapeamento de dados divergente e duplicidades

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (75%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Todos |
| **Sinais precoces** | Clientes duplicados, produtos com IDs conflitantes, totais divergentes |
| **Mitigação** | ID Map robusto. Validação de unicidade. Merge rules documentadas. |
| **Plano B** | Ferramenta de deduplicação manual. Rollback de sync. Quarentena de registros suspeitos. |

---

### RISCO 4: Mudanças de contrato/escopo com fornecedor

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (50%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Sólides, Domínio |
| **Sinais precoces** | Emails de aviso, deprecation warnings, changelog de API |
| **Mitigação** | Monitorar changelogs. Versionar integrações. Contrato com SLA de aviso prévio. |
| **Plano B** | Feature flags para desativar integrações. Modo degradado com funcionalidades core. |

---

### RISCO 5: Certificado A1/A3 e cadeia ICP Brasil

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (80%) |
| **Impacto** | CRÍTICO |
| **Sistemas afetados** | GOV.BR (eSocial, SEFAZ, NFS-e) |
| **Sinais precoces** | Erros de SSL/TLS, assinatura inválida, certificado expirado |
| **Mitigação** | Certificado A1 primeiro (mais simples). Alertas de expiração 30 dias antes. Rotação automatizada. |
| **Plano B** | Provedor homologado que gerencia certificados (Focus NFe, TecnoSpeed). |

---

### RISCO 6: Webservices governamentais instáveis

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MUITO ALTA (90%) |
| **Impacto** | MÉDIO |
| **Sistemas afetados** | GOV.BR (todos) |
| **Sinais precoces** | Timeouts frequentes, indisponibilidade em horários de pico, erros 500 |
| **Mitigação** | Circuit breaker. Retry com backoff. Queue de reenvio. Horários alternativos. |
| **Plano B** | Fila de contingência. Processamento batch fora do horário comercial. |

---

### RISCO 7: LGPD e segurança de dados

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (40%) |
| **Impacto** | CRÍTICO |
| **Sistemas afetados** | Sólides (dados de colaboradores), todos os sistemas |
| **Sinais precoces** | Logs com dados sensíveis, credenciais expostas, falta de consentimento |
| **Mitigação** | Usar security_lgpd existente. Criptografia AES-256-GCM. Masking de PII. Audit trail. |
| **Plano B** | Erasure completo. Notificação de incidente. Seguro cyber. |

---

### RISCO 8: Falha em sincronização incremental gerando inconsistência

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (70%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Todos |
| **Sinais precoces** | Registros desatualizados, cursores perdidos, gaps de dados |
| **Mitigação** | Sync state persistente. Checkpoints frequentes. Full sync periódico de validação. |
| **Plano B** | Full sync de recuperação. Reconciliação manual. |

---

### RISCO 9: Time operacional rejeita mudança

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (50%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Todos (adoção) |
| **Sinais precoces** | Resistência em treinamentos, workarounds manuais, reclamações |
| **Mitigação** | Envolvimento early. Treinamento prático. Quick wins visíveis. Suporte dedicado. |
| **Plano B** | Período de transição estendido. Sistemas em paralelo por mais tempo. |

---

### RISCO 10: Custo de provedores homologados / gateways fiscais

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (80%) |
| **Impacto** | MÉDIO |
| **Sistemas afetados** | GOV.BR, Domínio |
| **Sinais precoces** | Orçamentos acima do esperado, custos por transação altos |
| **Mitigação** | Pesquisa de mercado. Negociação de volume. Comparativo de provedores. |
| **Plano B** | Integração direta onde possível. Priorizar sistemas com melhor ROI. |

---

### RISCO 11: Autenticação OAuth2 expira e sync falha silenciosamente

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (75%) |
| **Impacto** | MÉDIO-ALTO |
| **Sistemas afetados** | Sólides (OAuth2) |
| **Sinais precoces** | HTTP 401 frequente, tokens expirando, refresh falhando |
| **Mitigação** | Token refresh automático. Alertas de expiração. Healthcheck de credenciais. |
| **Plano B** | Reautenticação manual via UI. Notificação ao admin. |

---

### RISCO 12: Schema de dados muda sem aviso

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (50%) |
| **Impacto** | ALTO |
| **Sistemas afetados** | Bling, Sólides |
| **Sinais precoces** | Erros de parsing, campos null inesperados, tipos diferentes |
| **Mitigação** | Validação de schema rigorosa. Campos opcionais. Logging de anomalias. |
| **Plano B** | Quarentena de registros inválidos. Alerta para revisão manual. |

---

### RISCO 13: Performance degradada com volume de dados

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (60%) |
| **Impacto** | MÉDIO |
| **Sistemas afetados** | Todos em produção |
| **Sinais precoces** | Sync demorando mais, timeouts, uso de memória alto |
| **Mitigação** | Batch processing. Paginação eficiente. Índices de BD. Worker pool. |
| **Plano B** | Escalar workers. Sync fora do horário. Priorização de entidades críticas. |

---

### RISCO 14: Webhooks perdidos ou duplicados

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | ALTA (70%) |
| **Impacto** | MÉDIO |
| **Sistemas afetados** | Bling, Sólides |
| **Sinais precoces** | Eventos não processados, duplicatas no banco, inconsistências |
| **Mitigação** | Idempotência por webhook_id. Dead Letter Queue. Reprocessamento. |
| **Plano B** | Sync periódico de reconciliação. Alerta de webhooks falhados. |

---

### RISCO 15: Falta de ambiente de teste/sandbox

| Aspecto | Detalhe |
|---------|---------|
| **Probabilidade** | MÉDIA (50%) |
| **Impacto** | MÉDIO |
| **Sistemas afetados** | Domínio, alguns endpoints GOV |
| **Sinais precoces** | Testes em produção, erros em dados reais, medo de testar |
| **Mitigação** | Solicitar sandbox ao fornecedor. Mock services para testes. Ambiente de staging. |
| **Plano B** | Testes com tenant de teste isolado. Feature flags para rollback rápido. |

---

## MATRIZ DE RISCOS

```
IMPACTO
   ^
   |  [R7]           [R5][R1]
   |  LGPD           Cert  API
   |
   |  [R10]    [R3][R4][R8][R12]
   |  Custo    Mapeamento/Schema
   |
   |  [R6][R13]  [R2][R11][R14]
   |  GOV/Perf   Rate/Auth/Webhook
   |
   |  [R15]
   |  Sandbox
   +---------------------------------> PROBABILIDADE
       BAIXA    MÉDIA    ALTA
```

---

## PLANO DE CONTINGÊNCIA GERAL

### Nível 1: Problema Isolado
- Desativar sync do conector afetado via feature flag
- Manter sistemas em paralelo
- Investigar e corrigir

### Nível 2: Falha Múltipla
- Rollback para última versão estável
- Comunicar stakeholders
- War room para resolução

### Nível 3: Falha Crítica
- Desativar todo o framework de integrações
- Voltar para operação manual
- Post-mortem e redesign

---

## AÇÕES IMEDIATAS (ANTES DE CODAR)

- [ ] Obter documentação completa de APIs (Sólides, Bling)
- [ ] Contato comercial com Domínio Sistemas
- [ ] Definir provedores para NFS-e e eSocial
- [ ] Configurar certificado A1
- [ ] Criar ambiente de staging para testes
- [ ] Definir stakeholders para aprovação de cutover

---

*Documento criado em: 2026-01-15*
*Revisão: Antes de cada fase do projeto*
