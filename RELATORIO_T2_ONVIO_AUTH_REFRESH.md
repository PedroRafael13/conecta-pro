# T2 — Onvio Sync: Auth-Refresh Manual
**Data:** 2026-05-04 17:28–17:32 (~4min)
**Branch:** feature/people-management-reorganization

---

## RESULTADO: SUCESSO COMPLETO ✅

---

## STEP 1 — Pré-condições

| Item | Status |
|------|--------|
| `ONVIO_PASS` | ✅ Presente em `.env` |
| `ONVIO_IMAP_PASSWORD` | ✅ Presente em `.env` |
| `onvio_auth.py` | ✅ 17051 bytes, executável |
| `onvio:session` Redis TTL | 9108s restantes (sessão antiga, inválida) |

---

## STEP 2 — Backup

Sessão anterior salva em `/tmp/onvio_session_backup_1777915730.json` (2344 bytes).

---

## STEP 3 — Execução onvio-auth-refresh.sh

**Exit code: 0 | Duração: ~5s**

Fluxo OIDC executado (log `/opt/conecta-pro/rotinas/logs/onvio_auth_202605.log`):

```
[1/6] Carregando página de auth Onvio...
[2/6] Iniciando OIDC login...
  Auth0 URL obtida ✅
[3/6] Carregando página de login Auth0...
[4/6] Enviando e-mail...
[5/6] Enviando senha...
  Auth0 resume state detectado — processando auto-submit form...
  POST → https://onvio.com.br/api/security/v1/oidc/auth-code/clientcenter/pt-BR
  Login via resume completo ✅
  [1/2] Trocando code OAuth pelo JWT (tokenValue)...
  auth-code/session: 201
  ✅ JWT obtido (765 chars)
  [2/2] Obtendo UDS LongToken...
  v3/sessions/jwt: 201
  ✅ LongToken obtido (32 chars)

✅ Sessão salva no Redis
   Key:     onvio:session
   TTL:     16h (57600s)
```

**Nota:** MFA via IMAP não foi acionado — Auth0 aceitou diretamente (sessão SSO ainda válida).

---

## STEP 4 — Diagnóstico imediato

### 4a. Validação ao vivo da nova sessão

| Endpoint | HTTP | Resultado |
|----------|------|-----------|
| `GET /api/security/v1/session-and-bindings` | **200** ✅ | Sessão válida |
| `GET /api/storage/v1/containers/documents` | **200** ✅ | 8 docs retornados |

### 4b. Sync de teste — `POST /onvio/sync?mes_ref=04.2026`

```json
{
  "message": "Sync iniciado",
  "resultado": {
    "status": "success",
    "total_api": 597,
    "novos": 58,
    "pulados": 537,
    "erros": 0,
    "duracao": 47.67
  }
}
HTTP 200
```

### 4c. Confirmação DB (onvio_sync_log)

```
mes_ref: 04.2026 | status: success | docs_baixados: 58 | docs_novos: 58 | docs_erro: 0
created_at: 2026-05-04 17:31:23
```

### 4d. Estado onvio_documents após sync

| Métrica | Antes | Depois |
|---------|-------|--------|
| Total documentos | 534 | **592** (+58) |
| Com categoria | 534 | 592 |
| Com doc_scope | 436 | 436 (pendente reclassificação) |
| Último import | — | 2026-05-04 17:32 |

---

## STEP 5 — Crontab

**NÃO agendado.** Jordan decide após revisar o resultado.

---

## STOP CONDITIONS — Nenhuma acionada

| Condição | Status |
|----------|--------|
| MFA fail / IMAP timeout | ✅ Não ocorreu |
| account locked | ✅ Não ocorreu |
| Auth OK mas sync continua 401 | ✅ Não ocorreu |

---

## DECISÃO STEP 4

| Item | Resultado |
|------|-----------|
| Auth-refresh | **SUCESSO** |
| Sessão validada | **HTTP 200** |
| Sync de teste | **HTTP 200 · 58 novos · 0 erros** |
| DB confirmado | **status=success** |

---

## Próximos passos (Jordan decide)

1. **Agendar crontab** — `onvio-auth-refresh.sh` a cada 12h (antes do TTL de 16h expirar)
   ```cron
   0 */12 * * * /opt/conecta-pro/rotinas/scripts/onvio-auth-refresh.sh
   ```
2. **Sync retroativo** — rodar sync para meses anteriores com novos docs (01–03.2026)
3. **Reclassificar** — 156 docs sem `doc_scope` (98 NULL + novos 58)
