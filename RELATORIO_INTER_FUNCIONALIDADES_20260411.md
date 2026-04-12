# Inter Banking — Funcionalidades Disponíveis
**Data:** 2026-04-11
**Engenheiro:** Claude Sonnet 4.6
**Conta:** 370990072-2 | Banco Inter (077)
**Certificado:** válido até 2027-04-11

---

## RESUMO EXECUTIVO

| Funcionalidade | API Inter | Backend ERP | Status |
|----------------|-----------|-------------|--------|
| Conexão mTLS | ✅ | ✅ | **ATIVO** |
| Saldo em tempo real | ✅ | ✅ | **ATIVO** |
| Extrato (30 dias) | ✅ | ✅ | **ATIVO** |
| Extrato completo | ✅ | ✅ | **ATIVO** |
| Listagem de boletos | ✅ | ✅ | **ATIVO** |
| Emissão de boleto | ✅ | ⚠️ bug no adapter | **PARCIAL** |
| PIX cobrança | ✅ (escopo ok) | ⚠️ falso negativo | **PARCIAL** |
| Pagamento de boleto | ✅ (escopo ok) | não testado | **NÃO TESTADO** |

---

## ENDPOINTS MAPEADOS

```
GET  /api/v1/integrations/banking/status          → Status da conexão
GET  /api/v1/integrations/banking/balances         → Saldo atual
GET  /api/v1/integrations/banking/statement        → Extrato (param: days=N)
GET  /api/v1/integrations/banking/statement/full   → Extrato completo
GET  /api/v1/integrations/banking/boleto/list      → Lista de boletos
POST /api/v1/integrations/banking/boleto/generate  → Emitir boleto
POST /api/v1/integrations/banking/pix/generate     → Gerar cobrança PIX
```

---

## RESULTADOS DOS TESTES

### ✅ 1. Status da Conexão

```json
{"bank_code": "077", "bank_name": "Banco Inter", "connected": true, "last_sync": "2026-04-11T17:35:28"}
```

---

### ✅ 2. Saldo em Tempo Real

```json
{
  "bank_code": "077",
  "account": "370990072-2",
  "balance": 58365.22,
  "available_balance": 58365.22,
  "blocked_balance": 0.0
}
```
**Saldo disponível: R$ 58.365,22**

---

### ✅ 3. Extrato 30 Dias

| Métrica | Valor |
|---------|-------|
| Total de transações | 518 |
| Valor movimentado | R$ 474.614,15 |
| PIX | 495 transações |
| Débito | 16 transações |
| Boleto | 6 transações |
| Crédito | 1 transação |

Amostra de transações reais retornadas:
```
2026-04-11 PIX ENVIADO - Cp:18236120-Meire Gabriela da Silva E Silva  R$ 32,00
2026-04-11 PIX ENVIADO - Cp:18236120-Silvana Maria da Silva Amazonas  R$ 32,00
2026-03-12 PIX ENVIADO - Cp:00360305-Bianca Hellem da Silva Meira     R$ 32,00
```

---

### ✅ 4. Extrato Completo (`statement/full`)

Retorna campos extras: `counterpart_name`, `counterpart_document`, `counterpart_bank`, `reference`, `category`.
Funcionando corretamente para todas as transações disponíveis.

---

### ✅ 5. Listagem de Boletos

```json
{"boletos": [], "total": 0}
```
Endpoint funcional. Sem boletos ativos no momento.

---

### ⚠️ 6. Emissão de Boleto — Bug no Adapter

**Via API Inter diretamente:** ✅ funciona
```bash
POST /cobranca/v3/cobrancas
→ {"codigoSolicitacao": "204c1aae-1abe-40b3-8b7c-ca9cb5bd9660"}  ✅ BOLETO GERADO
```

**Via backend ERP:** ❌ retorna erro 400

**Causa:** O adapter monta o payload sem campos de endereço do pagador obrigatórios pela Inter API v3:
```python
# O que o adapter envia (INCOMPLETO):
"pagador": {"nome": ..., "cpfCnpj": ...}

# O que a API Inter exige:
"pagador": {"nome": ..., "cpfCnpj": ..., "endereco": ...,
            "numero": ..., "bairro": ..., "cidade": ...,
            "uf": ..., "cep": ...}
```

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py` linha ~358
**Fix:** Adicionar campos de endereço ao payload do `generate_boleto()`

**Nota adicional:** Valor mínimo do Inter é R$ 2,50 (não R$ 1,00 como no teste inicial).

---

### ⚠️ 7. PIX — Escopo Disponível, Falso Negativo no Backend

**Escopos PIX:** ✅ disponíveis para esta aplicação
```json
{"scope": "pix.write pix.read"}  ← token obtido com sucesso
```

**Backend retorna:** `"PIX não habilitado na API Banco Inter"`

**Causa provável:** O adapter solicita todos os escopos em um único token. O escopo `cob.read` não está disponível para esta aplicação, o que pode causar falha no token combinado e acionar o fallback de "PIX não habilitado".

**Fix:** Separar o token de PIX do token principal, ou remover `cob.read` dos scopes solicitados no adapter.

---

## ESCOPOS CONFIRMADOS PARA ESTA APLICAÇÃO

| Escopo | Status | Funcionalidade |
|--------|--------|----------------|
| `extrato.read` | ✅ | Extrato bancário |
| `saldo.read` | ✅ | Saldo em tempo real |
| `boleto-cobranca.write` | ✅ | Emissão de boletos |
| `boleto-cobranca.read` | ✅ | Listagem de boletos |
| `pix.write` | ✅ | Gerar cobrança PIX |
| `pix.read` | ✅ | Consultar PIX |
| `pagamento-boleto.write` | ✅ (não testado) | Pagar boletos |
| `pagamento-boleto.read` | ✅ (não testado) | Consultar pagamentos |
| `cob.read` | ❌ não registrado | — |

---

## BUGS IDENTIFICADOS — AÇÕES NECESSÁRIAS

### BUG-01 — Adapter boleto sem endereço do pagador (ALTA)

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py` ~linha 358
**Fix:** Adicionar ao payload `generate_boleto()`:
```python
"pagador": {
    "nome": payer_name,
    "cpfCnpj": self._format_document(payer_document),
    "endereco": payer_address or "Endereço não informado",
    "numero": payer_number or "S/N",
    "bairro": payer_neighborhood or "Centro",
    "cidade": payer_city or "Manaus",
    "uf": payer_state or "AM",
    "cep": (payer_zip or "69000000").replace("-", ""),
}
```

### BUG-02 — Escopo `cob.read` inválido no token combinado (MÉDIA)

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py` linha ~58
**Fix:** Remover `"saldo": "cob.read"` — substituir por `"saldo": "saldo.read"` ou remover do scope combinado.

---

## DADOS DA CONTA

| Campo | Valor |
|-------|-------|
| Banco | Banco Inter (077) |
| Conta | 370990072-2 |
| Agência | 0001 |
| CNPJ | 35.710.481/0001-03 |
| Saldo atual | R$ 58.365,22 |
| Transações (30d) | 518 |
| Boletos ativos | 0 |
| Certificado válido até | 2027-04-11 |

---

*Relatório gerado em 2026-04-11 por Claude Sonnet 4.6*
*Todos os testes executados ao vivo contra a API real do Banco Inter*
