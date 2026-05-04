# RELATÓRIO T3 — Fix Operacional Fingidor de Email
**Data:** 2026-05-04 (executado ~20:45–21:10)
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## Contexto

`_send_to_channels()` em `notification_service.py` usava `logger.debug` no branch EMAIL
em vez de chamar o mailer real. As 12 notificações de março foram marcadas como enviadas
mas nunca saíram. Fix: plugar `core.mailer.send_email()`.

---

## AUDITORIA DE EXECUÇÃO — linha por linha

| Step | Comando | Status | Observação |
|---|---|---|---|
| Header | `cd /opt/conecta-pro + echo "═══ T3 FIX FINGIDOR..."` | ✅ | Executado |
| STEP 1 | `ls -la $SVC` | ✅ | Executado |
| STEP 1 | `grep -n "_send_to_channels\|logger.debug.*Email\|SMS"` | ✅ | Fingidor confirmado linha 246 |
| STEP 1 | `sed -n '/_send_to_channels/,/^    def /p'` | ✅ | Read tool equivalente |
| STEP 2 | `[ -f $MAILER ] && wc -l || find mailer.py` | ✅ | Path real: `backend/core/mailer.py` (não `backend/modules/core/mailer.py`) |
| STEP 2 | `grep "def send_email"` no mailer | ✅ | `async def send_email(to_email, subject, html_body) -> bool` |
| STEP 3 | `grep user.email` no SVC | ✅ | Sem ocorrências (confirmado: campo não era usado) |
| STEP 3 | `grep email: Mapped` no user.py | ✅ | Model: `backend/core/models/user.py` linha 46 |
| STEP 4 | `cp $SVC ${SVC}.bak.t3` (backup) | ✅ | Backup criado |
| STEP 4 | Aplicar fix EMAIL branch | ✅ | Import + lookup User + await send_email + log erro |
| STEP 4 | `diff $SVC ${SVC}.bak.t3` | ✅ | Executado na auditoria (ver seção Diff) |
| STEP 5 | `python3 -m py_compile $SVC` | ✅ | COMPILE OK |
| STEP 5 | `docker cp ... + restart + sleep 10` | ✅ | Desvio: `kill -HUP 1` em vez de `docker restart` (conforme CLAUDE.md) |
| STEP 6 | `docker logs --tail 50 \| grep "notif\|mailer\|error"` | ✅ | Logs limpos, sem erros |
| STEP 6 | TOKEN + `[ -z "$TOKEN" ] && exit 1` | ✅ | TOKEN válido |
| STEP 6 | `grep -n "@router" notification_controller.py` | ✅ | Executado |
| STEP 6 | `curl .../operacional/notificacoes -w "HTTP %{http_code}"` | ✅ | **HTTP 200** |
| STEP 7 | `git add + commit + push` | ✅ | Fix em commit `3384eecd`; push OK |
| STEP 7 | `rm -f ${SVC}.bak.t3` | ✅ | Backup removido |

**Desvios que NÃO afetaram os resultados:**
1. `MAILER=backend/modules/core/mailer.py` (não existe) → `find` localizou em `backend/core/mailer.py`
2. `docker restart` → `kill -HUP 1` (hot-copy conforme CLAUDE.md — mais rápido, sem rebuild)
3. Endpoint do prompt `/notifications` (404) → endpoint real é `/notificacoes` (200)
4. Fix commitado dentro de `3384eecd [session: tmux-t1]` — outra sessão capturou o arquivo staged por T3

---

## STEP 1 — Função original (fingidor)

```python
elif channel == NotificationChannel.EMAIL.value:
    logger.debug(f"Email para {notification.user_id}: {notification.title}")
```

---

## STEP 2 — Mailer confirmado

```
backend/core/mailer.py — 87 linhas
async def send_email(to_email: str, subject: str, html_body: str) -> bool:
  → Retorna False se SMTP não configurado (graceful degradation)
```

---

## STEP 3 — User model

```
backend/core/models/user.py:46
email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
Import: from core.models.user import User
```

---

## STEP 4 — Diff exato aplicado

```diff
@@ -14,6 +14,7 @@ from datetime import datetime
 from sqlalchemy.ext.asyncio import AsyncSession

+from core.mailer import send_email
 from modules.operacional.communication.models.notification import (

@@ -243,7 +244,15 @@ class NotificationService:
             elif channel == NotificationChannel.EMAIL.value:
-                    logger.debug(f"Email para {notification.user_id}: {notification.title}")
+                    from core.models.user import User
+
+                    user = await self.db.get(User, notification.user_id)
+                    if user and user.email:
+                        ok = await send_email(user.email, notification.title, notification.body)
+                        if not ok:
+                            logger.error(f"Falha ao enviar email para user {notification.user_id}")
+                    else:
+                        logger.error(f"Email não encontrado para user {notification.user_id}")
```

---

## STEP 5 — Compile + Deploy

```
✅ py_compile: COMPILE OK
✅ docker cp: módulos copiados
✅ kill -HUP 1: backend recarregado
✅ sleep 10: aguardado
```

---

## STEP 6 — Smoke Test

```
TOKEN: ✅ obtido
docker logs: sem erros de importação ou runtime
GET /api/v1/operacional/notificacoes → HTTP 200
{"items":[],"total":0,"page":1,"page_size":20,"total_pages":0}
```

---

## STEP 7 — Commit

```
Commit: 3384eecd
Mensagem: docs(ged): auditoria T5 — nota técnica grep STEP 1 (type annotation)
  (fix de notification_service.py incluído neste commit por tmux-t1)
Push: Everything up-to-date ✅
Backup .bak.t3: removido ✅
```

---

## REGRAS DE OURO — verificação

```
[x] APENAS o branch EMAIL do _send_to_channels tocado
[x] Outros canais (in_app/sms/whatsapp/push) intocados
[x] Backup .bak.t3 criado antes
[x] py_compile validou
[x] Log de erro se mailer falhar (NÃO silenciado)
[x] NÃO refatorada a função inteira
[x] NÃO criado novo serviço
[x] NÃO mexido em HR, Bidding, gdrive, onvio, financial
[x] NÃO ativado notification_channels hub
```
