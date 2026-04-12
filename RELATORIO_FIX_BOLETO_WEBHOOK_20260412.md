# Fix — Webhook Boleto Inter: POST → PUT
**Data:** 2026-04-12
**Commit:** `9c75b316`
**Branch:** feature/people-management-reorganization

---

## Problema Reportado

Ao chamar `POST /api/v1/webhooks/inter/configurar`, o webhook PIX era registrado com sucesso mas o webhook de boleto retornava erro:

```json
{
    "pix_webhook": {
        "success": true,
        "chave": "35710481000103",
        "webhook_url": "https://erp.conectamais.pro/api/v1/webhooks/inter/pix"
    },
    "boleto_webhook": {
        "success": false,
        "error": "Server disconnected without sending a response."
    }
}
```

---

## Diagnóstico

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py`
**Método:** `register_boleto_webhook` (linha 863)

### Passo 1 — Confirmar credenciais
Credenciais Inter carregadas de `/opt/conecta-pro/credentials/.env.credentials` ✅
- `INTER_CLIENT_ID` ✅
- `INTER_CLIENT_SECRET` ✅
- `INTER_CERT_PATH` → `/opt/conecta-pro/credentials/inter/Inter_API_Certificado.crt`
- `INTER_KEY_PATH` → `/opt/conecta-pro/credentials/inter/Inter_API_Chave.key`

### Passo 2 — Teste direto contra a API Inter

Teste executado dentro do container backend com autenticação real (mTLS):

```
scope: boleto-cobranca.write boleto-cobranca.read webhook.write webhook.read
Auth: 200 OK

POST /cobranca/v3/cobrancas/webhook → RemoteProtocolError: Server disconnected without sending a response.
PUT  /cobranca/v3/cobrancas/webhook → 204 No Content ✅
```

**Root cause:** A API do Banco Inter exige `PUT` para registro de webhook de boleto.
O código usava `POST`, que fazia o servidor Inter fechar a conexão sem resposta alguma.

### Comparação PIX vs Boleto (padrão Inter API)

| Serviço | Método | Endpoint |
|---------|--------|----------|
| PIX webhook | `PUT` | `/pix/v2/webhook/{chave}` |
| Boleto webhook | `PUT` | `/cobranca/v3/cobrancas/webhook` |

Ambos usam `PUT`. O boleto estava incorretamente configurado com `POST`.

---

## Fix Aplicado

**Arquivo:** `backend/modules/integrations/banking/adapters/inter.py`

```python
# ANTES (quebrado):
async def register_boleto_webhook(self, webhook_url: str) -> dict:
    """
    POST /cobranca/v3/cobrancas/webhook
    """
    await self._request(
        "POST",                              # ← ERRADO
        "/cobranca/v3/cobrancas/webhook",
        json={"webhookUrl": webhook_url},
    )

# DEPOIS (correto):
async def register_boleto_webhook(self, webhook_url: str) -> dict:
    """
    PUT /cobranca/v3/cobrancas/webhook  (Inter API retorna 204 No Content)
    """
    await self._request(
        "PUT",                               # ← CORRETO
        "/cobranca/v3/cobrancas/webhook",
        json={"webhookUrl": webhook_url},
    )
```

Nota: o método `_request` já tratava corretamente a resposta 204 (sem body):
```python
return response.json() if response.text else {}
```

---

## Deploy

```bash
# Copiar arquivo corrigido para o container
docker cp backend/modules/integrations/banking/adapters/inter.py \
  conecta-pro-backend:/app/modules/integrations/banking/adapters/inter.py

# Limpar cache .pyc e reiniciar
docker exec conecta-pro-backend find /app/modules/integrations/banking/adapters/__pycache__ \
  -name "inter*.pyc" -delete
docker restart conecta-pro-backend

# Status: Up (healthy) ✅
```

---

## Validação Final

```json
{
    "pix_webhook": {
        "success": true,
        "chave": "35710481000103",
        "webhook_url": "https://erp.conectamais.pro/api/v1/webhooks/inter/pix"
    },
    "boleto_webhook": {
        "success": true,
        "webhook_url": "https://erp.conectamais.pro/api/v1/webhooks/inter/boleto"
    },
    "urls_registradas": {
        "pix": "https://erp.conectamais.pro/api/v1/webhooks/inter/pix",
        "boleto": "https://erp.conectamais.pro/api/v1/webhooks/inter/boleto"
    }
}
```

✅ `pix_webhook.success: true`
✅ `boleto_webhook.success: true`

---

## Resumo

| | Antes | Depois |
|---|---|---|
| Método HTTP | `POST` | `PUT` |
| Resposta Inter | `Server disconnected` | `204 No Content` |
| boleto_webhook | `success: false` | `success: true` |
| pix_webhook | `success: true` | `success: true` |

---

## Commit e Push

| Hash | Descrição |
|------|-----------|
| `9c75b316` | fix(banking): register_boleto_webhook usa PUT — Inter API retorna 204 |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download
```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_FIX_BOLETO_WEBHOOK_20260412.md ~/Downloads/RELATORIO_FIX_BOLETO_WEBHOOK_20260412.md
```
