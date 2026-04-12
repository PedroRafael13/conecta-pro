# RELATÓRIO — DIAGNÓSTICO BANKING / INTER ADAPTER
**Data:** 2026-04-12
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Sonnet 4.6

---

## RESULTADO GERAL

```
Adapter Inter:         ✅ 10 métodos implementados
Scopes OAuth2:         ✅ corrigidos (cob.write + extrato.read)
Endpoints ativos:      ✅ 7 endpoints /api/v1/integrations/banking/*
OpenAPI em prod:       ℹ️  desabilitado por design (main_production.py:171)
Tabelas banking:       ✅ payable_payments + receivable_payments + webhooks
Gaps identificados:    ℹ️  transfer, darf, lote, webhook — fora do escopo atual
```

---

## 1. ADAPTER BANCO INTER

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py`

### Métodos implementados (10)

| # | Método | Endpoint Inter API | Descrição |
|---|--------|--------------------|-----------|
| 1 | `authenticate()` | `POST /oauth/v2/token` | OAuth2 + mTLS (certificado digital) |
| 2 | `get_balance()` | `GET /banking/v2/saldo` | Consulta saldo disponível |
| 3 | `get_statement()` | `GET /banking/v2/extrato` | Extrato com filtro por data |
| 4 | `initiate_payment()` | `POST /banking/v2/pagamento` | Pagar boleto por código de barras |
| 5 | `get_payment_status()` | `GET /banking/v2/pagamento/{id}` | Status de pagamento |
| 6 | `cancel_payment()` | `DELETE /banking/v2/pagamento/{id}` | Cancelar pagamento agendado |
| 7 | `validate_pix_key()` | `GET /pix/v2/dict/key` | Validar chave PIX |
| 8 | `initiate_pix()` | `POST /pix/v2/pix` | Transferência PIX |
| 9 | `generate_boleto()` | `POST /cobranca/v3/cobrancas` | Emitir boleto de cobrança |
| 10 | `generate_pix_charge()` | `PUT /pix/v2/cob/{txid}` | Cobrança PIX imediata |

### Scopes OAuth2 — estado atual (pós-correção)

```python
SCOPES = {
    "extrato":   "extrato.read",
    "saldo":     "extrato.read",              # ✅ corrigido (era cob.read)
    "pix":       "pix.write pix.read",
    "cob":       "cob.write cob.read",        # ✅ adicionado (necessário para PIX charge)
    "boleto":    "boleto-cobranca.write boleto-cobranca.read",
    "pagamento": "pagamento-boleto.write pagamento-boleto.read",
}
```

**Correções aplicadas nesta sprint:**
- `saldo` de `cob.read` → `extrato.read` (escopo correto para saldo)
- `cob.write` adicionado ao authenticate() (obrigatório para `PUT /pix/v2/cob/{txid}`)
- Payload `generate_boleto()` corrigido com campos de endereço do pagador:
  `tipoPessoa`, `endereco`, `numero`, `bairro`, `cidade`, `uf`, `cep`

---

## 2. ENDPOINTS BANKING ATIVOS

**Prefixo base:** `/api/v1/integrations/banking/`
**Registrado em:** `main_production.py:789`

| Método | Endpoint completo | Descrição |
|--------|-------------------|-----------|
| `GET` | `/api/v1/integrations/banking/balances` | Saldo de todos os bancos |
| `GET` | `/api/v1/integrations/banking/status` | Status de conexão por banco |
| `GET` | `/api/v1/integrations/banking/statement` | Extrato por período |
| `GET` | `/api/v1/integrations/banking/statement/full` | Extrato completo expandido |
| `POST` | `/api/v1/integrations/banking/boleto/generate` | Emitir boleto |
| `GET` | `/api/v1/integrations/banking/boleto/list` | Listar boletos emitidos |
| `POST` | `/api/v1/integrations/banking/pix/generate` | Gerar cobrança PIX |

**Validação ao vivo (2026-04-11):**
- `/balances` → HTTP 200 ✅ — saldo real R$ 58.215,22
- `/status` → HTTP 200 ✅ — Inter `connected: true`
- `/boleto/generate` → HTTP 200 ✅ — `success: true`, `boleto_id: a24f3f5e`
- `/statement` → HTTP 200 ✅
- `/boleto/list` → HTTP 200 ✅

### OpenAPI desabilitado em produção

`/openapi.json` retorna `{"detail":"Not Found"}` — comportamento esperado:

```python
# main_production.py:171-173
docs_url=None if _is_production else "/docs",
redoc_url=None if _is_production else "/redoc",
openapi_url=None if _is_production else "/openapi.json",
```

Workaround para mapear endpoints: `grep -rn "@router\."` nos controllers.

---

## 3. TABELAS BANKING NO DB

### Tabelas de pagamento (ativas)

| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| `payable_payments` | — | Pagamentos de contas a pagar |
| `receivable_payments` | — | Pagamentos de contas a receber |
| `payment_agreements` | — | Acordos/parcelamentos |
| `payment_methods` | — | Métodos de pagamento cadastrados |

### Tabelas de webhook / agendamento

| Tabela | Descrição |
|--------|-----------|
| `webhook_configs` | Configurações de webhooks |
| `marketplace_webhook_deliveries` | Entregas de webhook |
| `marketplace_webhook_subscriptions` | Assinaturas de webhook |
| `solides_webhook_log` | Log de sincronização Solides |
| `scheduled_jobs` | Jobs agendados |
| `scheduler_tasks` / `scheduler_executions` | Histórico de execuções Celery |

### Design de dados — banking

Não há tabelas dedicadas `boleto` ou `pix_cobranca` — **por design**:
- Boletos emitidos → gerenciados em `receivable_accounts` (conta a receber)
- Pagamentos realizados → registrados em `bank_transactions`
- Vínculo via `transacao_bancaria_id` em `payable_accounts` (5 vinculados)

---

## 4. GAPS IDENTIFICADOS

### Não implementados (fora do escopo atual)

| Funcionalidade | Endpoint Inter | Status |
|----------------|----------------|--------|
| Transferência TED/DOC | `POST /banking/v2/transferencia` | ❌ não implementado |
| Pagamento DARF | `POST /banking/v2/darf` | ❌ não implementado |
| Pagamento em lote | `POST /banking/v2/pagamento/lote` | ❌ não implementado |
| Webhook de cobrança | Configuração no painel Inter | ❌ não configurado |
| Consulta boleto individual | `GET /cobranca/v3/cobrancas/{id}` | ❌ não implementado |

**Impacto dos gaps:**
- `barcode` e `pdf_url` retornam vazios após `generate_boleto()` porque não há consulta pós-criação em `/cobranca/v3/cobrancas/{id}`
- Webhook Inter não configurado — status de pagamento de boletos não atualiza automaticamente

### Banco Cora (403) — ainda desconectado

| Variável | Status |
|----------|--------|
| `CORA_CLIENT_ID` | ❌ ausente no `.env` |
| `CORA_CLIENT_SECRET` | ❌ ausente no `.env` |

---

## 5. PRÓXIMOS PASSOS RECOMENDADOS (Fase 2)

| # | Ação | Prioridade | Impacto |
|---|------|------------|---------|
| 1 | Implementar `GET /cobranca/v3/cobrancas/{id}` no adapter | 🔴 ALTA | Barcode + PDF do boleto disponíveis |
| 2 | Configurar webhook Inter no painel (`developers.inter.co`) | 🟡 MÉDIA | Atualização automática de status de boleto pago |
| 3 | Implementar pagamento em lote (`/banking/v2/pagamento/lote`) | 🟡 MÉDIA | Pagar múltiplas contas em uma requisição |
| 4 | Configurar Banco Cora (403) no `.env` | 🟢 BAIXA | Redundância bancária |
| 5 | Implementar `POST /banking/v2/transferencia` (TED) | 🟢 BAIXA | Transferências internas |

---

## 6. ESTADO CONSOLIDADO DO MÓDULO BANKING

```
Adapter Inter:         ✅ implementado e operacional
Conexão ao vivo:       ✅ connected: true
Saldo real:            ✅ R$ 58.215,22 (conta 370990072-2)
Boleto emissão:        ✅ success: true (barcode assíncrono)
PIX cobrança:          ✅ scopes corrigidos (cob.write)
PIX transferência:     ✅ initiate_pix() implementado
Pagamento boleto:      ✅ initiate_payment() implementado
Extrato:               ✅ get_statement() operacional
Webhook:               ❌ não configurado
Barcode pós-emissão:   ❌ consulta individual não implementada
Banco Cora:            ❌ sem credenciais
```

---

*Relatório gerado: 2026-04-12*
*Auditor: Claude Sonnet 4.6*
*Branch: feature/people-management-reorganization*
