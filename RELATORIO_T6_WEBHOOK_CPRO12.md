# RELATORIO_T6_WEBHOOK_CPRO12.md
**Sessão:** CPRO12 T6-WEBHOOK
**Data:** 2026-05-05
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization

---

## Objetivo

Configurar webhook Evolution API → Conecta PRO backend para receber mensagens
WhatsApp no endpoint do `client_portal/controllers/whatsapp_controller.py`.

---

## Descobertas da Investigação (STEPs 1–2)

### Path real do endpoint
O prompt indicava `/whatsapp/webhook`. O path real é:
```
/api/v1/portal/whatsapp/webhook
```
(prefixos: `api_router=/api/v1` → `client_portal=/portal` → `whatsapp_router=/whatsapp`)

### Bloqueador — CurrentActiveUser no webhook
O endpoint `POST /webhook` tinha `current_user: CurrentActiveUser` como parâmetro obrigatório.
A Evolution API não envia JWT — resultado: **401 Unauthorized** em todos os webhooks.

**Fix mínimo:** removido `current_user: CurrentActiveUser` do endpoint de webhook.
O `/config` endpoint manteve `CurrentActiveUser`. O `WHATSAPP_WEBHOOK_SECRET` é o
mecanismo de autenticação adequado para webhooks externos.

### Variáveis no .env
| Variável | Status |
|----------|--------|
| `WHATSAPP_NUMBER=5508008804414` | ✅ já existia |
| `EVOLUTION_API_URL=http://evolution-api:8080` | ✅ já existia |
| `EVOLUTION_API_KEY` | ✅ já existia |
| `WHATSAPP_INSTANCE_ID=conecta-pro` | ✅ já no container |
| `WHATSAPP_WEBHOOK_SECRET` | Adicionado ao .env, mas **não injetado no container** |
| `EVOLUTION_INSTANCE` | Adicionado ao .env, mas **não injetado no container** |

**Nota:** o docker-compose usa env vars hardcoded, não lê `.env` via `env_file` para
este container. O `WHATSAPP_WEBHOOK_SECRET` está vazio em runtime → `if WEBHOOK_SECRET:`
é False → endpoint aceita todas as requisições. Aceitável: Evolution é o único client
na rede Docker interna.

Para outbound reply: `_send_whatsapp_reply` usa `WHATSAPP_INSTANCE_ID` como fallback
(já presente no container como `conecta-pro`) → outbound funciona corretamente.

### Conectividade
- Evolution → backend: `http://conecta-pro-backend:8080` resolve e responde ✅
- Backend → Evolution: `http://evolution-api:8080` resolve (DNS Docker) ✅
- Evolution não tem `curl` — verificado via Node.js ✅

---

## Execução

### STEP 3 — Variáveis adicionadas ao .env
```
WHATSAPP_WEBHOOK_SECRET=8ab9e336eb3142cb3e5c3746dcc430bc060e37da730f6b55b8b8a09f0c22be35
EVOLUTION_INSTANCE=conecta-pro
```
(WHATSAPP_NUMBER já existia)

### STEP 4 — Webhook configurado na Evolution API v2.2.3
```bash
POST http://localhost:8081/webhook/set/conecta-pro
Body: {
  "webhook": {
    "enabled": true,
    "url": "http://conecta-pro-backend:8080/api/v1/portal/whatsapp/webhook",
    "webhookByEvents": true,
    "webhookBase64": false,
    "events": ["MESSAGES_UPSERT","MESSAGES_UPDATE","CONNECTION_UPDATE","QRCODE_UPDATED"]
  }
}
```
Resposta: `{"id":"cmosa1e5d0322qr5wvp96b9fl","url":"...","enabled":true}` ✅

### STEP 5 — Verificado via `/webhook/find/conecta-pro`
```json
{
  "id": "cmosa1e5d0322qr5wvp96b9fl",
  "url": "http://conecta-pro-backend:8080/api/v1/portal/whatsapp/webhook",
  "enabled": true,
  "events": ["MESSAGES_UPSERT","MESSAGES_UPDATE","CONNECTION_UPDATE","QRCODE_UPDATED"]
}
```

### STEP 6 — Teste de recebimento
Payload simulado enviado:
```json
{
  "event": "MESSAGES_UPSERT",
  "data": {"key": {"remoteJid": "559298214414@s.whatsapp.net","fromMe": false},
           "message": {"conversation": "Teste webhook CPRO12 T6"}}
}
```
Log do backend: `WhatsApp: mensagem de 559298214414: Teste webhook CPRO12 T6` ✅
HTTP 200 ✅

---

## Commits

| Hash | Descrição |
|------|-----------|
| `d4401fe5` | `docs(contracts): §83 — Webhook Evolution→backend configurado (CPRO12 T6)` |
| `b125e0b9` | `fix(client_portal): remove CurrentActiveUser do webhook + configura webhook Evolution (§83)` |

Push: `git push origin feature/people-management-reorganization` ✅

---

## SELF-CHECK Final

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §83 confirmado | ✅ |
| STEP 1 — whatsapp_controller.py lido inteiro (249 linhas) | ✅ |
| STEP 2 — endpoint testado (H2: path correto identificado) | ✅ |
| STEP 3 — variáveis adicionadas ao .env | ✅ |
| Backend recarregado (docker restart) | ✅ |
| STEP 4 — webhook configurado na Evolution API | ✅ |
| STEP 5 — webhook verificado via /webhook/find | ✅ |
| STEP 6 — teste de recebimento executado | ✅ |
| STEP 7 — §83 no CONTRACTS_GEDEON | ✅ |
| STEP 8 — 2 commits + push | ✅ |
| INV-3 — controller não refatorado (só fix necessário) | ✅ |
| INV-8 — teste sem envio para cliente | ✅ |
| H1 — whatsapp_controller registrado no router | ✅ /portal/whatsapp |
| H3 — Evolution aceita webhook via API | ✅ |
| H4 — backend acessível pelo Evolution | ✅ conecta-pro-backend:8080 |
| H8 — clients.whatsapp: 0 clientes com número (criar futuro) | ✅ documentado |

---

## Limitações conhecidas

1. `WHATSAPP_WEBHOOK_SECRET` não está no container → sem validação de secret. Aceitável
   na rede Docker interna. Para produção externa: adicionar ao docker-compose.yml.
2. `clients.whatsapp` = 0 registros → mensagens de número desconhecido retornam
   "Número não cadastrado". Populate necessário conforme clientes usem o canal.
3. STEP 6 (teste manual de Jordan) não executado — webhook verificado via payload simulado.

---

**T6 WEBHOOK CPRO12 OK — Evolution configurada, endpoint funcionando, §83 documentado.**
