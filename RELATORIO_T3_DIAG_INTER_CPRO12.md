# T3 CPRO12 — Diagnóstico Profundo Banco Inter
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Tipo:** DIAGNÓSTICO (READ-ONLY — INV-2: zero chamadas à API Inter real)

---

## Módulo Inter implementado

**Arquivos:**

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `modules/integrations/banking/adapters/inter.py` | 1041 | InterAdapter — OAuth2+mTLS, saldo, extrato, PIX, boleto, pagamento |
| `modules/integrations/inter/services/payment_service.py` | 661 | D7 — máquina de estados: preparado→OTP→aprovado→executado |
| `modules/integrations/inter/inter_controller.py` | 504 | D6 — router /financeiro/inter/ |
| `modules/integrations/inter/cobranca_service.py` | 260 | D6.3 — ciclo de vida de cobranças |
| `modules/integrations/inter/conciliacao_service.py` | 249 | D6.2 — conciliação folha×transações |
| `modules/integrations/inter/payment_controller.py` | 245 | D7 — router /financeiro/inter/payments |
| `modules/integrations/inter/inter_sync_service.py` | 160 | D6.1 — sync extrato → inter_transactions |
| `modules/integrations/inter/client.py` | 92 | Facade InterClient |
| `modules/integrations/inter/schemas.py` | 85 | Pydantic schemas (Saldo, Transacao, Extrato, Cobranca, PIX) |
| `modules/integrations/inter/token_cache.py` | 45 | Cache Redis token (TTL 50min) |
| `modules/integrations/inter/config.py` | 35 | URLs + Redis keys + scopes |
| `modules/integrations/inter/exceptions.py` | 21 | InterError, InterAuthError, InterRateLimitError |
| `modules/integrations/inter/__init__.py` | 1 | — |
| `modules/integrations/inter/services/__init__.py` | 0 | — |

**Total:** 3.399 linhas de código Python

---

## Credenciais configuradas (STEP 2 — INV-3: apenas nomes)

| Variável | Descrição |
|----------|-----------|
| `INTER_CLIENT_ID` | OAuth2 client_id |
| `INTER_CLIENT_SECRET` | OAuth2 client_secret |
| `INTER_CERT_PATH` | Certificado mTLS .crt |
| `INTER_KEY_PATH` | Chave privada mTLS .key |
| `INTER_AGENCY` | Agência |
| `INTER_ACCOUNT` | Conta completa (com dígito) |
| `INTER_ACCOUNT_NUMBER` | Número conta (sem dígito) |
| `INTER_ENVIRONMENT` | `production` |
| `INTER_BASE_URL` | URL base API Inter |
| `INTER_PIX_KEY` | Chave PIX (CNPJ da empresa) |
| `INTER_WEBHOOK_CA_PATH` | CA Inter para validar webhooks |

---

## OAuth2 Scopes

### Scopes em config.py (D6 controller):

| Scope | Habilitado | Permite |
|-------|-----------|---------|
| `extrato.read` | ✅ | Consultar extrato |
| `boleto-cobranca.read` | ✅ | Consultar boletos |
| `boleto-cobranca.write` | ✅ | Emitir/cancelar boletos |
| `pagamento-pix.read` | ✅ | Consultar PIX recebidos |
| `pagamento-boleto.read` | ✅ | Consultar pagamentos de boleto |
| `cob.read` | ✅ | Consultar cobranças PIX |
| `cob.write` | ✅ | Criar cobranças PIX |
| **`pagamento-pix.write`** | ❌ | **Ausente — não pode enviar PIX via API** |

### Scopes em InterAdapter (banking adapter):

```python
SCOPES = {
    "extrato": "extrato.read",
    "pix": "pix.write pix.read",        # ← tenta pix.write
    "boleto": "boleto-cobranca.write boleto-cobranca.read",
    "pagamento": "pagamento-boleto.write pagamento-boleto.read",
    "ted": "pagamento-ted.write pagamento-ted.read",
    "darf": "pagamento-darf.write pagamento-boleto.read",
}
```

**Conflito:** adapter solicita `pix.write` mas scope habilitado é `pagamento-pix.read` — versão de scope pode diferir entre contas Inter. Se token falhar em pix.write, fallback implícito para somente leitura.

---

## Endpoints Inter implementados (STEP 3)

### D6 — `GET|POST /api/v1/financeiro/inter/...`

| Endpoint | Método | Descrição | Status prod |
|----------|--------|-----------|-------------|
| `/saldo` | GET | Saldo conta (cache Redis 5min) | ❌ 404 |
| `/sync-extrato` | POST | Sync extrato N dias (background) | ❌ 404 |
| `/transactions` | GET | Lista inter_transactions | ❌ 404 |
| `/extrato/resumo` | GET | Totais crédito/débito por tipo | ❌ 404 |
| `/conciliar/{competencia}` | POST | Prepara + concilia folha | ❌ 404 |
| `/payroll/pagamentos` | GET | Lista conciliacao_folha | ❌ 404 |
| `/payroll/divergencias` | GET | Status='em_conciliacao' | ❌ 404 |
| `/cobrancas` | POST | Emite boleto | ❌ 404 |
| `/cobrancas` | GET | Lista cobranças | ❌ 404 |
| `/cobrancas/{id}` | GET | Consulta cobrança Inter | ❌ 404 |
| `/cobrancas/{id}/cancelar` | POST | Cancela cobrança | ❌ 404 |
| `/cobrancas/{id}/pdf` | GET | URL PDF do boleto | ❌ 404 |
| `/cobrancas/sincronizar-status` | POST | Atualiza status cobranças | ❌ 404 |
| `/pix/sync-recebidos` | POST | Sync PIX recebidos (background) | ❌ 404 |
| `/pix/recebidos` | GET | Lista PIX recebidos | ❌ 404 |
| `/pix/{e2e_id}` | GET | Consulta PIX individual | ❌ 404 |

### D7 — `GET|POST /api/v1/financeiro/inter/payments/...`

| Endpoint | Método | Descrição | Status prod |
|----------|--------|-----------|-------------|
| `/payments` | POST | Prepara pagamento | ❌ 404 |
| `/payments/{id}/gerar-otp` | POST | Gera OTP → email Jordan | ❌ 404 |
| `/payments/{id}/aprovar` | POST | Valida OTP | ❌ 404 |
| `/payments/{id}/executar` | POST | Chama Inter API | ❌ 404 |
| `/payments/{id}/cancelar` | POST | Cancela | ❌ 404 |
| `/payments` | GET | Lista pagamentos | ❌ 404 |
| `/payments/saldo-limite` | GET | Limite diário | ❌ 404 |
| `/payments/audit` | GET | Audit log (Jordan only) | ❌ 404 |
| `/payments/{id}/audit` | GET | Audit log de pagamento | ❌ 404 |

### Endpoints de diagnóstico testados:

| Endpoint | HTTP | Observação |
|----------|------|-----------|
| `GET /api/v1/banking/inter/status` | 404 | não registrado |
| `GET /api/v1/financial/banking/status` | 404 | não registrado |

### Causa raiz dos 404:

`modules/integrations/inter/` ausente no container. Container tem apenas: `banking`, `connectors`, `email`, `models`, `repositories`, `schemas`, `services`, `sync`, `whatsapp`. `safe_import` silencia o ImportError → todos os 25 endpoints retornam 404.

---

## O que retorna da API Inter (STEP 4)

### Endpoints Inter chamados pelo adapter

| Endpoint Inter | Método | Descrição |
|----------------|--------|-----------|
| `POST /oauth/v2/token` | POST | OAuth2 token (mTLS + client_credentials) |
| `GET /banking/v2/saldo` | GET | Saldo: `disponivel`, `bloqueadoCheque` |
| `GET /banking/v2/extrato` | GET | Lista `transacoes[]` com tipo, valor, descricao |
| `POST /pix/v2/cob` | POST | Cria cobrança PIX imediata |
| `GET /pix/v2/cob` | GET | Lista cobranças PIX |
| `POST /pix/v2/payment` | POST | Envia PIX |
| `GET /banking/v2/pagamento` | GET | Lista pagamentos por período/tipo |
| `GET /banking/v2/pagamento/{id}` | GET | Status de pagamento específico |
| `DELETE /banking/v2/pagamento/{id}` | DELETE | Cancela pagamento agendado |
| `GET /pix/v2/dict/key` | GET | Valida chave PIX (retorna CPF/CNPJ titular) |
| `POST /cobranca/v3/cobrancas` | POST | Emite boleto |
| `GET /cobranca/v3/cobrancas/{id}` | GET | Consulta boleto |

### Campos retornados pelo extrato (`/banking/v2/extrato`)

```json
{
  "transacoes": [{
    "tipoOperacao": "C|D",
    "tipoTransacao": "PIX|TED|BOLETO|DEBITO",
    "valor": "decimal",
    "descricao": "texto (inclui CPF parcial no padrão 'Cp :XXXXXXXX-NOME')",
    "dataTransacao": "YYYY-MM-DD",
    "detalhes": { "cpfCnpj": "...", "nome": "..." }
  }]
}
```

**CRÍTICO:** `detalhes_destinatario` (que contém CPF) **está disponível na API Inter**, mas `inter_sync_service.py:82` hardcoda `raw_payload=None` e não salva `detalhes_destinatario` no banco:

```python
# inter_sync_service.py linha 82 — bug
"raw": None,  # ← hardcoded None, descarta detalhes_destinatario
```

### Tabelas Inter no banco

| Tabela | Rows | Observação |
|--------|------|-----------|
| `inter_transactions` | 536 | 03.2026: 15 | 04.2026: 521 |
| `inter_conciliacao_folha` | 46 | 2026-03, status='previsto' (nunca conciliadas) |
| `inter_payments` | 0 | Nenhum pagamento via D7 |
| `inter_payment_audit` | 0 | — |
| `inter_payment_otp` | 0 | — |
| `inter_pix_recebidos` | 1 | 1 PIX recebido |
| `inter_cobrancas` | 0 | — |

### Tabelas relacionadas a pagamento (mais amplo)

| Tabela | Rows | Relevância GEDEON |
|--------|------|-------------------|
| `payroll_payments` | 46 | ⚠️ ALTA — 46 pagamentos PIX de salário Março/2026 com `pix_e2e_id`, status='pendente_pagamento' |
| `bank_transactions` | ? | Usado por `_add_comprovantes_bancarios` no kit_real_controller |
| `commission_payments` | ? | Comissões — não relevante GEDEON |
| `diarist_payments` | ? | Diaristas — não relevante GEDEON |

**`payroll_payments` — Schema:** `employee_id, payslip_id, mes, ano, valor_liquido, metodo (PIX), pix_key, pix_e2e_id, pix_txid, status, data_pagamento, comprovante_id`

---

## Comprovantes de Pagamento (STEP 5)

### Existe endpoint para buscar comprovante por colaborador?

```
❌ Nenhuma função def.*comprovante ou def.*get_payment retorna
   comprovante de salário por CPF na API Inter.
```

### Existe implementação no GED?

**SIM** — `kit_real_controller.py` tem função `_add_comprovantes_bancarios()` (linha 423):
- Busca em `bank_transactions` onde `description ILIKE '%salario%|%folha%|%PIX ENVIADO%'`
- Gera PDF consolidado via ReportLab
- Insere como `document_type='comprovante_salario'` em `ged_kit_documents`
- **Problema:** usa tabela `bank_transactions` (não `inter_transactions`) — pode estar vazia

Também existe `_add_comprovante_vt()` (linha 661) para vale-transporte.

### `payroll_payments` — Caminho promissor

```sql
-- 46 pagamentos Março/2026 com PIX e2e_id e pix_txid
SELECT status, COUNT(*) FROM payroll_payments GROUP BY status;
-- pendente_pagamento: 46
```

`pix_e2e_id` + `pix_txid` são os identificadores que permitiriam buscar o comprovante na API Inter via `GET /pix/v2/cob/{txid}`. Porém com status `pendente_pagamento` — os pagamentos não foram executados via D7.

---

## Para VA/VT

| Integração | Implementado | Detalhe |
|------------|-------------|---------|
| VA Sólides | ⚠️ Parcial | `comp_va_solides` como tipo de doc em kit, mas sem endpoint de sync automático |
| VT individual | ⚠️ Parcial | `_add_comprovante_vt()` gera comprovante de lista de funcionários, não por CPF |
| VR (vale refeição) | ❌ Não | Sem integração Inter para VR |
| Comprovante PIX VA | ❌ Não | VA pago por Sólides, não por Inter |

`_add_comprovante_vt()` busca funcionários alocados no condomínio e gera PDF consolidado — **não é por CPF individual, é por condomínio**.

---

## INV-5 — Pode GEDEON buscar comprovante de salário para colaborador X? (STEP 7)

**Resposta: NÃO — 3 bloqueios simultâneos impedem completamente.**

### Bloqueio 1 — Módulo não carregado em produção

`modules/integrations/inter/` ausente no container.
Todos os 25 endpoints D6/D7 retornam HTTP 404.

### Bloqueio 2 — CPF não está em dados estruturados

`inter_sync_service.py:82` hardcoda `raw_payload=None` → `detalhes_destinatario` nunca salvo.
536/536 rows com `detalhes_destinatario=NULL`.
O campo `descricao` tem padrão "Cp :XXXXXXXX" (8 dígitos) ≠ CPF employee (11 dígitos) → matching impossível.

### Bloqueio 3 — `payroll_payments` nunca executados via Inter

46 pagamentos de Março/2026 com `metodo=PIX` e `status='pendente_pagamento'`.
Os `pix_e2e_id`/`pix_txid` desses registros seriam o elo de ligação com a API Inter — mas os pagamentos não foram executados via D7, então não geraram transação real na conta Inter.

### O que seria necessário para GEDEON ter comprovante de salário por colaborador X

1. **Corrigir `inter_sync_service.py:82`:** salvar `detalhes_destinatario` (contém CPF)
2. **Hot-copy `inter/` para container:** `docker cp + kill -HUP 1`
3. **Re-sync extrato:** `POST /financeiro/inter/sync-extrato?dias=60`
4. **Executar conciliação:** `POST /financeiro/inter/conciliar/2026-04` (match CPF×transação)
5. **Endpoint GEDEON:** `GET /gedeon/colaborador/{cpf}/comprovante-salario?mes_ref=MM.YYYY` → busca `inter_conciliacao_folha` por employee CPF → retorna `{data_paga, valor, match_tipo, inter_transaction_id}`

---

## Status da integração

| Endpoint | HTTP | Resposta |
|----------|------|---------|
| `GET /api/v1/financeiro/inter/transactions` | 404 | `{"detail":"Not Found"}` |
| `GET /api/v1/financeiro/inter/payments` | 404 | `{"detail":"Not Found"}` |
| `GET /api/v1/financeiro/inter/payroll/pagamentos` | 404 | `{"detail":"Not Found"}` |
| `GET /api/v1/banking/inter/status` | 404 | `{"detail":"Not Found"}` |
| `GET /api/v1/financial/banking/status` | 404 | `{"detail":"Not Found"}` |

**Todos os 25 endpoints Inter retornam 404.** Causa: módulo ausente no container.

---

## Achados Arquiteturais

| Achado | Impacto |
|--------|---------|
| `modules/integrations/inter/` ausente no container | CRÍTICO — D6/D7 100% inacessíveis |
| `inter_sync_service.py:82` — `raw_payload=None` hardcoded | detalhes_destinatario nunca salvo → conciliação CPF impossível |
| `payroll_payments` — 46 pagamentos PIX Mar/2026 nunca executados | D7 não foi usado; pix_e2e_id existe mas transação não chegou ao banco Inter |
| `kit_real_controller._add_comprovantes_bancarios` usa `bank_transactions` | tabela genérica, não `inter_transactions` — pode não ter dados |
| Scope `pagamento-pix.write` ausente em config.py mas `pix.write` no adapter | Conflito de nomenclatura — pode causar AuthError em produção |
| `inter_conciliacao_folha` — 46 rows status='previsto' nunca conciliadas | Histórico Mar/2026 sem conciliação |
| `get_payment_list()` no adapter — busca `GET /banking/v2/pagamento` por período | Existe mas nunca chamado pelo ERP |
| `validate_pix_key()` — retorna cpfCnpj do titular | Poderia ser usado para verificar CPF destinatário de PIX |
| Deprecation warning `modules.integrations` → `modules.gestao` | Prazo 2026-05-11 — migração não concluída |

---

## Próximos Passos (não implementados — INV-2)

1. **FIX URGENTE:** `inter_sync_service.py:82` — salvar `detalhes_destinatario` + `raw_payload`
2. **HOT-COPY:** `docker cp backend/modules/integrations/inter/ conecta-pro-backend:/app/modules/integrations/inter/`
3. **Re-sync:** `POST /api/v1/financeiro/inter/sync-extrato?dias=60`
4. **Conciliação:** `POST /api/v1/financeiro/inter/conciliar/2026-04`
5. **Investigar `bank_transactions`:** verificar se tem dados e se `_add_comprovantes_bancarios` funciona
6. **Executar `payroll_payments`:** completar fluxo D7 para Mar/2026 e gerar `pix_e2e_id` reais
7. **Endpoint GEDEON comprovante:** `GET /gedeon/colaborador/{cpf}/comprovante-salario?mes_ref=MM.YYYY`

---

## Self-check (auditoria 100%)

| Item | Status |
|------|--------|
| STEP 0 — `tail -10 CONTRACTS_GEDEON.md` → última seção §86 | ✅ |
| STEP 1 — 14 arquivos Python Inter+banking lidos integralmente | ✅ |
| STEP 1 — contagem total: 3.399 linhas | ✅ |
| STEP 2 — 11 variáveis .env mapeadas (apenas nomes — INV-3) | ✅ |
| STEP 2 — grep scopes/oauth em módulos | ✅ |
| STEP 3 — 25 endpoints D6+D7 mapeados + status HTTP prod | ✅ |
| STEP 3 — endpoints `banking/inter/status` e `financial/banking/status` testados | ✅ (ambos 404) |
| STEP 4 — schemas de resposta documentados | ✅ |
| STEP 4 — grep `comprovante/pagamento/cpf` nos arquivos Inter | ✅ |
| STEP 4 — tabelas `inter_%` + `banking%` + `payment%` + `pagamento%` inspecionadas | ✅ |
| STEP 5 — `_add_comprovantes_bancarios` e `_add_comprovante_vt` documentados | ✅ |
| STEP 5 — `payroll_payments` (46 rows, pendente_pagamento) documentada | ✅ |
| STEP 5 — grep `https://cdpj\|api.bancointer\|developers.inter` | ✅ |
| STEP 6 — 7 scopes config.py + adapter SCOPES dict documentados | ✅ |
| STEP 6 — conflito pix.write vs pagamento-pix.read identificado | ✅ |
| STEP 7 — INV-5 respondido: NÃO, 3 bloqueios + caminho para resolver | ✅ |
| STEP 7 — `get_payment_list()` e `get_payment_status()` no adapter documentados | ✅ |
| STEP 8 — seção "Para VA/VT" presente no relatório | ✅ |
| STEP 8 — seção "Status da integração" com HTTP status real | ✅ |
| STEP 8 — §87 adicionado ao CONTRACTS_GEDEON.md | ✅ |
| INV-2 — zero chamadas à API real Banco Inter | ✅ |
| INV-3 — credenciais: apenas nomes de variáveis, nunca valores | ✅ |
| INV-6 — commit único de docs ao final | ✅ |

---

T3 DIAG INTER CPRO12 OK — AUDITORIA 100%

[session: t5] [module: ged]
