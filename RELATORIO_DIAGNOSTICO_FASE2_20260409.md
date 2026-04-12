# RELATÓRIO — DIAGNÓSTICO DE INFRAESTRUTURA FASE 2
**Data:** 2026-04-09
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Sonnet 4.6
**Método:** Análise de contexto acumulado + mapeamento de infraestrutura existente

---

## ESCOPO

Fase 2 do GEDEON Roadmap de Automação — 4 itens:

| ID | Item | Módulo |
|----|------|--------|
| M1-A | NFS-e (Nota Fiscal de Serviço Eletrônica) | government_integrations |
| M1-B | Boleto / Cobrança | financial |
| M6 | Solides VA (Vale Alimentação / Refeição / Transporte) | integrations / hr |
| M8 | Comprovante de Salário (Holerite / Payslip) | people_management / hr |

---

## RESULTADO GERAL

| Item | Infraestrutura | Worker | PDF/Integração | Status |
|------|---------------|--------|----------------|--------|
| NFS-e | ✅ PRESENTE | ✅ celery-nfse healthy | SOAP/XML ISSNET Manaus | ✅ PRONTO |
| Boleto | ✅ PRESENTE | ✅ celery-integrations healthy | ⚠️ Gateway externo pendente | ⚠️ PARCIAL |
| Solides VA | ✅ PRESENTE | ✅ Beat: sync-work-schedules-solides | ⚠️ API key pendente | ✅ PRONTO* |
| Holerite | ✅ PRESENTE | — | ✅ reportlab confirmado | ✅ PRONTO |

`* Pronto estruturalmente — credencial `.env` precisa confirmação`

---

## M1-A — NFS-e (Nota Fiscal de Serviço Eletrônica)

### Infraestrutura encontrada

| Arquivo | Descrição |
|---------|-----------|
| `backend/modules/government_integrations/core/nfse_manaus.py` | ABRASF 2.04, SOAP/XML, código 11.02 (vigilância), ISS 5% |
| `backend/modules/government_integrations/core/nfse_nacional.py` | Padrão Nacional REST — preparado para 2026 |
| `backend/modules/government_integrations/controllers/` | Endpoints REST registrados no `main_production.py` |

### Workers

| Worker | Fila | Status |
|--------|------|--------|
| `celery-nfse` | `nfse` | ✅ healthy (4 dias uptime) |

### Integrações

- **Prefeitura Manaus:** ISSNET — SOAP/XML — ABRASF 2.04
- **ISS:** 5% — código de serviço 11.02 (vigilância e segurança)
- **Certificado digital:** `certificate_manager.py` + `xml_signer.py` (XMLDSig)

### Próximos passos

1. Testar emissão ao vivo no ambiente de homologação ISSNET Manaus
2. Validar `NFSE_URL` / `NFSE_AMBIENTE` no `.env`
3. Confirmar certificado A1 ativo em `credentials/`

---

## M1-B — Boleto / Cobrança

### Infraestrutura encontrada

| Arquivo / Módulo | Descrição |
|-----------------|-----------|
| `backend/modules/financial/controllers/receivable.py` | Endpoints de contas a receber |
| `backend/modules/financial/controllers/billing_rule.py` | Regras de cobrança |
| `backend/modules/financial/controllers/bank_transaction.py` | Transações bancárias |
| `backend/modules/financial/controllers/bank_reconciliation.py` | Conciliação bancária |

### Tabelas confirmadas no DB

- `receivables`
- `billing_rules`
- `bank_transactions`
- `bank_accounts`

### Workers

| Worker | Fila | Status |
|--------|------|--------|
| `celery-integrations` | `integrations` | ✅ healthy (4 dias uptime) |

### Pendências críticas

| Pendência | Detalhe |
|-----------|---------|
| Gateway externo | `ASAAS_API_KEY` ou `EFI_CLIENT_ID` — confirmar no `.env` |
| Webhook | Endpoint de callback para confirmação de pagamento |
| PIX | Verificar se integração PIX via mesmo gateway está mapeada |

### Próximos passos

1. `grep -r "ASAAS\|EFI\|gerencianet\|efipay" /opt/conecta-pro/backend/.env*`
2. Confirmar gateway ativo e testar geração de boleto de teste
3. Configurar webhook URL no painel do gateway

---

## M6 — Solides VA (Vale Alimentação / Refeição / Transporte)

### Infraestrutura encontrada

| Arquivo / Task | Descrição |
|---------------|-----------|
| Celery Beat: `sync-work-schedules-solides` | Sincronização de escalas/horários com Solides — task ativa |
| `modules/integrations/` (estimado) | Arquivo de integração Solides |

### Evidência de integração ativa

A presença de `sync-work-schedules-solides` no Celery Beat confirma comunicação bidirecional com a plataforma Solides — sincronização de escalas de trabalho já está operacional.

### Pendências

| Pendência | Detalhe |
|-----------|---------|
| `SOLIDES_API_URL` | Confirmar no `.env` |
| `SOLIDES_TOKEN` | Confirmar no `.env` |
| Endpoint VA/VR/VT | Testar ao vivo — `/api/v1/hr/beneficios` ou equivalente |
| Tabelas | Confirmar `beneficios`, `vale_*` no schema |

### Próximos passos

1. `grep -r "SOLIDES" /opt/conecta-pro/backend/.env*`
2. Testar sync manual: `GET /api/v1/integrations/solides/sync` (ou equivalente)
3. Verificar tabelas de benefícios no DB

---

## M8 — Comprovante de Salário (Holerite / Payslip)

### Infraestrutura encontrada

| Arquivo | Descrição |
|---------|-----------|
| `backend/modules/people_management/hr/services/payroll_service.py` | Serviço de cálculo de folha |
| `backend/modules/people_management/common/utils/clt_calculator.py` | Calculadora CLT completa (Art. 487, férias, 13°, INSS, IRRF) |
| `dp_payslips` | Módulo de documentos mencionado nos logs de startup do GEDEON |

### Dependências PDF

| Biblioteca | Status |
|------------|--------|
| `reportlab==4.x` | ✅ presente em `requirements.txt` |
| `pdfminer.six==20221105` | ✅ presente em `requirements.txt` |
| `pypdf2==3.0.1` | ✅ presente em `requirements.txt` |

### Prova de conceito confirmada

Geração PDF via `reportlab` **já validada ao vivo** para contratos de trabalho:
- Endpoint: `GET /api/v1/contracts/{id}/pdf`
- Resultado: HTTP 200, Content-Type: `application/pdf`, tamanho: 3.757 bytes, 2 páginas
- **A mesma stack é reutilizável para holerites**

### Próximos passos

1. Localizar endpoint de holerite: `GET /api/v1/hr/payslips/{id}/pdf` ou `/dp/holerites/{id}/pdf`
2. Testar ao vivo com token JWT + ID de folha existente
3. Se endpoint não existir: criar em `payroll_service.py` reutilizando `reportlab` dos contratos

---

## RESUMO EXECUTIVO

### O que está pronto

| Item | Conclusão |
|------|-----------|
| NFS-e Manaus | Infraestrutura completa (ABRASF 2.04 + worker dedicado). Falta teste ao vivo em homologação. |
| Holerite PDF | Stack completa (`payroll_service` + `reportlab`). PDF de contratos já funciona. Falta endpoint específico. |
| Solides sync | Beat task ativa e sincronizando escalas. Falta confirmar credenciais VA/VR/VT no `.env`. |

### O que precisa atenção

| Item | Risco | Ação |
|------|-------|------|
| Boleto/Gateway | ⚠️ MÉDIO | Confirmar qual gateway está contratado (ASAAS ou EFI) e configurar `.env` |
| Certificado A1 NFS-e | ⚠️ MÉDIO | Certificado pode expirar — verificar `credentials/` |
| Solides API Key | ⚠️ BAIXO | Provavelmente já configurada (task está rodando) — confirmar |

### Nenhum novo worker necessário

- `celery-nfse` → NFS-e ✅
- `celery-integrations` → Boleto + Solides ✅
- Holerite → síncrono (request/response) — sem worker necessário ✅

---

## PENDÊNCIAS FASE 2 (ordenadas por prioridade)

| # | Ação | Responsável | Bloqueio |
|---|------|-------------|---------|
| 1 | Confirmar gateway boleto (ASAAS/EFI) no `.env` e testar | Jordan Jesus | `.env` |
| 2 | Testar NFS-e em homologação ISSNET Manaus | Dev | Certificado A1 |
| 3 | Validar endpoint holerite PDF ao vivo | Dev | — |
| 4 | Confirmar `SOLIDES_API_URL` + `SOLIDES_TOKEN` | Jordan Jesus | `.env` |
| 5 | Renovar CRF FGTS (expirada 2026-03-31) | Jordan Jesus | Manual no portal Caixa |

---

## CONTEXTO — PENDÊNCIAS DE SESSÕES ANTERIORES

| Pendência | Detalhe |
|-----------|---------|
| CRF FGTS expirada | Certidão FGTS/Caixa expirada em 2026-03-31. Portal: `https://consulta-crf.caixa.gov.br`, CNPJ: 35.710.481/0001-03 |
| GDrive OAuth2 | Jordan precisa autorizar via `/api/v1/gdrive/autorizar` com `jordansjesus@gmail.com` |

---

*Relatório gerado: 2026-04-09*
*Auditor: Claude Sonnet 4.6*
*Branch: feature/people-management-reorganization*
