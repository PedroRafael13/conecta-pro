# RELATÓRIO — DIAGNÓSTICO FINANCEIRO / BANKING / NFS-e
**Data:** 2026-04-11
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Sonnet 4.6

---

## RESULTADO GERAL

```
Tabelas financeiras:      ✅ 11 tabelas mapeadas
Endpoints financeiros:    ✅ 50+ ativos (payable, receivable, banking, boleto, pix)
Inter Banking conectado:  ✅ R$ 58.215,22 saldo real
NFS-e Sync Portal:        ❌ BUG — 405 em ambos os métodos POST/GET
Boleto Inter — payload:   ⚠️ INCOMPLETO — endereço do pagador ausente
PIX scope:                ⚠️ SUSPEITO — cob.read onde cobrança exige cob.write
bank_reconciliations:     ⚠️ 0 registros (tabela existe mas vazia)
cashflow_entries:         ⚠️ 0 registros (tabela existe mas vazia)
```

---

## 1. TABELAS FINANCEIRAS — ESTADO ATUAL

| Tabela | Registros | Observação |
|--------|-----------|------------|
| `bank_transactions` | **649** | ✅ Populada — transações bancárias ativas |
| `nfses` (NFS-e saída) | **27** | ✅ NFS-e emitidas |
| `nfse_entrada` | **9** | ✅ NFS-e recebidas |
| `receivable_accounts` | **11** | ✅ Contas a receber |
| `payable_accounts` | **8** | ✅ Contas a pagar |
| `nfes` | **2** | ✅ NF-e modelo 55 |
| `nfe_entradas` | **1** | ✅ NF-e entrada (upload XML) |
| `nfe_compras_estoque` | **2** | ✅ Itens em estoque virtual (EPI) |
| `fin_stock_items` | **0** | ⚠️ Tabela existe, vazia |
| `bank_reconciliations` | **0** | ⚠️ Conciliação bancária sem registros |
| `cashflow_entries` | **0** | ⚠️ Fluxo de caixa sem registros |

---

## 2. ENDPOINTS FINANCEIROS ATIVOS

Mapeados via controllers em `backend/modules/financial/controllers/`:

### Contabilidade
`/accounts`, `/accounts/stats`, `/accounts/tree`, `/accounts/{id}`, `/accounts/{id}/balance`, `/balancete`, `/balanco-patrimonial`, `/cost-centers`, `/cost-centers/stats`

### Contas a Pagar / Receber
`/payable_accounts`, `/receivable_accounts`, `/receivable_installments`, `/payable_installments`, `/bulk-approve`, `/bulk-payment`, `/bulk-generate-boletos`

### Banking / PIX / Boleto
`/api/v1/integrations/banking/balances`, `/status`, `/statement`, `/statement/full`, `/boleto/generate`, `/boleto/list`, `/pix/generate`

### Fiscal
`/nfse-entrada` (9 notas), `/nfse-entrada/sync`, `/nfse-entrada/status-sync`, `/fiscal/nfe-entrada/listar`, `/fiscal/nfe-entrada/estoque`, `/cfop`, `/calcular/*`

### BI / AI Financeiro
`/advisor/chat`, `/advisor/recommendations`, `/ai/anomalies`, `/ai/forecast`, `/ai/predict-demand`, `/cashflow-prediction`

### Faturamento
`/billing/contracts`, `/billing/contrato-ativado`, `/billing/medicao`, `/billing/preview`, `/billing/summary`

---

## 3. BUG #1 — NFS-e Sync Portal Nacional: 405

**Arquivo:** `backend/modules/government_integrations/services/nfse_entrada_sync_service.py`
**Endpoint chamado:** `POST /nfse/consulta-tomador` → **405**
**Fallback:** `GET /nfse?cpfCnpjTomador=35710481000103` → **405**

**Resposta do portal:**
```json
{
  "status_http": 405,
  "metodo": "GET /nfse?cpfCnpjTomador=",
  "response": "The requested resource does not support http method 'GET'.",
  "portal": "nacional",
  "cert_subject": "JORDAN SANTOS DE JESUS LTDA:35710481000103",
  "cert_valido_ate": "2027-01-13"
}
```

**Diagnóstico:**
- Certificado válido ✅ (até 2027-01-13)
- CNPJ correto ✅ (35.710.481/0001-03)
- Problema: **endpoint incorreto** — Portal Nacional ABRASF v2.1 usa path diferente

**Possíveis endpoints corretos (Portal Nacional):**
```
POST /v1/cidades/{codigoMunicipio}/nfse/consulta-tomador
POST /v1/nfse/consulta                  # alguns portais
POST /v2/nfse/consultar-tomador
```
O código de município de Manaus é **1302603** (IBGE).

**Fix sugerido** em `nfse_entrada_sync_service.py`:
```python
# Tentar endpoint com código de município (Manaus = 1302603)
url_municipio = f"{PORTAL_URL}/v1/cidades/1302603/nfse/consulta-tomador"
resp = requests.post(url_municipio, json={"cpfCnpjTomador": CNPJ}, ...)
```

---

## 4. BUG #2 — Boleto Inter: Endereço do Pagador Ausente

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py`
**Função:** `generate_boleto()` — linha 347

**Payload atual (incompleto):**
```python
"pagador": {
    "nome": payer_name,
    "cpfCnpj": self._format_document(payer_document),
    # ❌ endereço ausente
}
```

**API Inter v3 exige** (`/cobranca/v3/cobrancas`):
```python
"pagador": {
    "nome": payer_name,
    "cpfCnpj": self._format_document(payer_document),
    "endereco": payer_address,       # logradouro + número
    "cidade": payer_city,
    "uf": payer_state,
    "cep": payer_zip,
    "bairro": payer_neighborhood,    # opcional mas recomendado
}
```

**Impacto:** Boleto emitido pode ser recusado pelo Inter com erro `422 Unprocessable Entity` na produção por campo obrigatório ausente.

**Fix:** Adicionar campos de endereço opcionais em `BoletoGenerateRequest` e repassá-los ao payload `pagador`.

---

## 5. SUSPEITA #3 — PIX Scope: cob.read vs cob.write

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py` — linha 59

**Código atual:**
```python
SCOPES = {
    "extrato": "extrato.read",
    "saldo": "cob.read",          # ⚠️ SUSPEITO
    "pix": "pix.write pix.read",
    "boleto": "boleto-cobranca.write boleto-cobranca.read",
    "pagamento": "pagamento-boleto.write pagamento-boleto.read",
}
```

**Problema:** O scope `"saldo": "cob.read"` está nomeado como "saldo" mas usa `cob.read` (cobranças). A **criação de cobranças PIX** via `PUT /pix/v2/cob/{txid}` exige `cob.write`, não `cob.read`.

**Fix:**
```python
SCOPES = {
    "extrato":   "extrato.read",
    "saldo":     "extrato.read",           # saldo vem do extrato
    "cob_read":  "cob.read",
    "cob_write": "cob.write",             # ← necessário para criar cobranças PIX
    "pix":       "pix.write pix.read",
    "boleto":    "boleto-cobranca.write boleto-cobranca.read",
    "pagamento": "pagamento-boleto.write pagamento-boleto.read",
}
# E no authenticate():
scopes = " ".join([
    self.SCOPES["extrato"],
    self.SCOPES["cob_read"],
    self.SCOPES["cob_write"],   # ← adicionar
    self.SCOPES["pix"],
    self.SCOPES["boleto"],
    self.SCOPES["pagamento"],
])
```

---

## 6. OBSERVAÇÕES — bank_reconciliations e cashflow_entries

**`bank_reconciliations`: 0 registros**
- Tabela e endpoints existem (`/bank-reconciliations/auto`, `/bank-reconciliations/status`)
- 649 transações em `bank_transactions` disponíveis para conciliar
- Auto-conciliação não foi executada ainda
- **Não é bug** — feature pronta, aguarda execução

**`cashflow_entries`: 0 registros**
- `/cashflow-prediction` e `/cashflow-entries` endpoints ativos
- Fluxo de caixa precisa ser alimentado por lançamentos ou importação
- **Não é bug** — módulo pronto, sem dados de entrada ainda

**`fin_stock_items`: 0 registros**
- Tabela diferente de `nfe_compras_estoque` (2 itens)
- Pode ser tabela legada ou módulo de estoque financeiro separado do estoque físico de EPIs
- Baixa criticidade

---

## 7. RESUMO DOS ACHADOS

| # | Item | Tipo | Criticidade | Ação |
|---|------|------|-------------|------|
| 1 | NFS-e Sync 405 — endpoint incorreto | Bug | 🔴 ALTA | Corrigir URL para `/v1/cidades/1302603/nfse/consulta-tomador` |
| 2 | Boleto Inter — endereço pagador ausente | Bug | 🟡 MÉDIA | Adicionar campos endereço em `BoletoGenerateRequest` e payload |
| 3 | PIX scope `cob.read` vs `cob.write` | Suspeita | 🟡 MÉDIA | Adicionar `cob.write` ao authenticate() |
| 4 | bank_reconciliations vazia | Info | 🟢 BAIXA | Executar auto-conciliação com 649 transações |
| 5 | cashflow_entries vazio | Info | 🟢 BAIXA | Alimentar via lançamentos ou importação |
| 6 | fin_stock_items vazio | Info | 🟢 BAIXA | Investigar relação com nfe_compras_estoque |

---

## 8. ESTADO DOS DADOS FINANCEIROS

```
bank_transactions:    649  ✅ (histórico bancário importado)
nfses saída:           27  ✅ (NFS-e emitidas)
nfse_entrada:           9  ✅ (NFS-e recebidas — TOTVS, fornecedores)
receivable_accounts:   11  ✅ (contas a receber ativas)
payable_accounts:       8  ✅ (contas a pagar ativas)
nfes:                   2  ✅ (NF-e modelo 55)
nfe_entradas:           1  ✅ (XML upload funcionando)
nfe_compras_estoque:    2  ✅ (EPIs: colete + capacete)
```

---

*Relatório gerado: 2026-04-11*
*Auditor: Claude Sonnet 4.6*
*Branch: feature/people-management-reorganization*
