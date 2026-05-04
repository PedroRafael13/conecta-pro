# T4 — Investigação Bidding Email Loop
**Data:** 2026-05-04
**Executor:** Claude Sonnet 4.6 [session: t4] [module: bidding]
**Objetivo:** Mapear por que `_dispatch_email()` envia pro próprio remetente. Read-only.

---

## STEP 1 — Localizar `_dispatch_email`

```
backend/modules/bidding/services/notification_service.py
-rw-r--r-- 1 root root 46182 Apr  1 10:35
```

---

## STEP 2 — Quem chama `_dispatch_email`?

Apenas **um caller** — o método `_dispatch()` na linha 1076, dentro do mesmo arquivo:

```python
# notification_service.py:1066
def _dispatch(self, notification: BiddingNotification) -> None:
    canal = notification.canal

    if canal == NotificationChannel.INTERNAL:
        logger.info("[BIDDING_NOTIF][INTERNAL] ...")

    elif canal == NotificationChannel.EMAIL:
        self._dispatch_email(notification)   # ← única chamada

    elif canal == NotificationChannel.PUSH:
        self._push_buffer.append(notification)

    notification.enviado = True
    notification.enviado_em = datetime.utcnow()
```

---

## STEP 3 — Onde `self._smtp_user` é definido?

```python
# notification_service.py:161 — __init__
self._smtp_host = os.environ.get("SMTP_HOST", "")
self._smtp_port = int(os.environ.get("SMTP_PORT", "587"))
self._smtp_user = os.environ.get("SMTP_USER", "")      # ← PROBLEMA AQUI
self._smtp_pass = os.environ.get("SMTP_PASS", "")
```

**Variáveis no container (reais):**

```
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USERNAME=noreply@conectamais.pro   ← nome correto no .env
SMTP_PASSWORD=JsJ618908@#%              ← nome correto no .env
```

---

## STEP 4 — Destinatários esperados

```python
# notification_service.py:1109-1110
msg["From"] = self._smtp_user
msg["To"] = self._smtp_user  # Default: envia para o proprio usuario SMTP
```

Nenhuma variável de destinatário real existe: zero referências a `destinatario`, `recipient`,
`to_email`, `to_addr`, `jordan`, `BIDDING_NOTIFY_EMAIL` ou qualquer email de pessoa.

---

## STEP 5 — Tasks Celery que disparam notif

As 3 tasks registradas no Celery (`notificar_oportunidade_nova`, `notificar_prazo_edital`,
`notificar_resultado_pipeline`) **NÃO importam `BiddingNotificationService`**.

```python
# notification_tasks.py — imports reais
import asyncio, logging, uuid
from celery import shared_task
# ← BiddingNotificationService nunca importado
```

As tasks fazem INSERT direto na tabela `notifications` via SQL raw, canal `"database"`:

```python
db.execute(text("""
    INSERT INTO notifications (id, title, message, type, priority, created_at)
    VALUES (:id, :title, :message, :type, :priority, :created_at)
    ON CONFLICT DO NOTHING
"""), {...})
return {"notified": True, "channels": ["database"]}
```

→ `_dispatch_email` **nunca é chamado pelas tasks Celery**. São sistemas completamente desconectados.

---

## STEP 6 — Histórico de execução das tasks

```
# Apenas tasks REGISTRADAS — nenhuma execução real nos logs:
  . bidding.notificar_oportunidade_nova
  . bidding.notificar_prazo_edital
  . bidding.notificar_resultado_pipeline

# Última task executada no worker integrations:
[2026-04-28 02:31:48] Task solides.incremental_sync[e6a1e94c...] received
[2026-04-28 02:31:50] Task solides.incremental_sync succeeded in 2.09s
```

**Nenhuma task `bidding.notif*` executou nos últimos dias.** Só `solides.incremental_sync` está ativo.

---

## Diagnóstico: 3 bugs em camadas (nenhum do outro chega)

### Bug 1 — `SMTP_USER` vs `SMTP_USERNAME` (bloqueia tudo)

| Variável que o código lê | Valor em produção |
|---|---|
| `os.environ.get("SMTP_USER", "")` | `""` (vazia — não existe) |
| `os.environ.get("SMTP_USERNAME", "")` | `"noreply@conectamais.pro"` ← nome real |

Consequência: `not self._smtp_user` → **True** → código cai no branch:
```python
if not self._smtp_host or not self._smtp_user:
    logger.info("[BIDDING_NOTIF][EMAIL] SMTP nao configurado (fallback log): ...")
    return   # ← sai aqui, nunca chega no smtplib
```

**`_dispatch_email` NUNCA abre conexão SMTP em produção.** O log diz "SMTP nao configurado"
mesmo com SMTP_HOST preenchido — porque `SMTP_USER` está vazio.

---

### Bug 2 — `msg["To"] = self._smtp_user` (envia pro remetente)

Mesmo que Bug 1 fosse corrigido (nome da variável), o destinatário ainda seria **errado**:

```python
msg["From"] = self._smtp_user   # noreply@conectamais.pro
msg["To"] = self._smtp_user     # noreply@conectamais.pro ← mesmo endereço
```

Não existe variável, parâmetro ou config para definir o destinatário real.
O comentário no código confirma: `# Default: envia para o proprio usuario SMTP`.

---

### Bug 3 — `smtplib.SMTP` + porta 465 (TLS handshake failure)

```python
with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10) as server:
    server.ehlo()
    if self._smtp_port != 25:
        server.starttls()   # ← STARTTLS = protocolo para porta 587
```

| Porta | Protocolo correto | O que o código faz |
|---|---|---|
| 465 (Hostinger) | `smtplib.SMTP_SSL(host, 465)` — SSL implícito | `smtplib.SMTP(host, 465)` + `starttls()` |
| 587 | `smtplib.SMTP(host, 587)` + `starttls()` | ← isso funciona, mas não é o que está configurado |

Com `SMTP_PORT=465` e `smtplib.SMTP`, a conexão falha por TLS handshake antes de `login()`.
Se executasse, cairia na `except Exception` silenciosa — `logger.warning`.

**Bugs 2 e 3 nunca são alcançados porque Bug 1 já retorna antes.**

---

## Respostas às 3 perguntas

### 1. `_dispatch_email` envia pro próprio remetente OU pro destinatário real?

**Próprio remetente** (`msg["To"] = self._smtp_user`). Não existe destinatário real configurado.
Mas isso é irrelevante porque **o código nunca chega até o `msg["To"]`** — o Bug 1 faz return
antes de montar o EmailMessage.

### 2. Onde está o bug (variável trocada, hardcode)?

**Dois bugs de variável, um de protocolo:**

1. **Bug 1 (root cause):** `os.environ.get("SMTP_USER")` mas o .env tem `SMTP_USERNAME` e `SMTP_PASSWORD`
   → Fix: mudar para `os.environ.get("SMTP_USERNAME")` e `os.environ.get("SMTP_PASSWORD")`

2. **Bug 2 (To errado):** `msg["To"] = self._smtp_user` — hardcoded para o remetente
   → Fix: adicionar `BIDDING_NOTIFY_EMAIL` no .env e ler `os.environ.get("BIDDING_NOTIFY_EMAIL")`

3. **Bug 3 (TLS errado):** `smtplib.SMTP` + `starttls()` incompatível com porta 465
   → Fix: usar `smtplib.SMTP_SSL(host, 465)` sem `starttls()`

### 3. Tasks bidding executaram nos últimos dias?

**NÃO.** Nenhuma das 3 tasks `bidding.notif*` executou. Apenas `solides.incremental_sync`
está rodando (último: 2026-04-28). As tasks de notif de bidding nunca foram disparadas.

Adicionalmente: **as tasks Celery não usam `BiddingNotificationService`** — são completamente
desconectadas. Mesmo que fossem disparadas, não chamariam `_dispatch_email`.

---

## Recomendação de fix (sem aplicar)

**3 mudanças no `notification_service.py` + 1 no `.env`:**

```python
# __init__ — corrigir nomes das variáveis (Bug 1 + Bug 3 setup)
self._smtp_user = os.environ.get("SMTP_USERNAME", "")   # era "SMTP_USER"
self._smtp_pass = os.environ.get("SMTP_PASSWORD", "")   # era "SMTP_PASS"
self._notify_to = os.environ.get("BIDDING_NOTIFY_EMAIL", "")  # novo

# _dispatch_email — corrigir To (Bug 2)
msg["To"] = self._notify_to or self._smtp_user  # fallback para remetente se não config

# _dispatch_email — corrigir protocolo TLS (Bug 3)
if self._smtp_port == 465:
    ctx = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port, timeout=10)
else:
    ctx = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
with ctx as server:
    server.ehlo()
    if self._smtp_port != 25 and self._smtp_port != 465:
        server.starttls()
        server.ehlo()
    server.login(self._smtp_user, self._smtp_pass)
    server.send_message(msg)
```

```bash
# .env — adicionar destinatário real para bidding
BIDDING_NOTIFY_EMAIL=jjesus@conectamais.pro
```

**Esforço:** ~15 linhas. Desbloqueia os 3 bugs em sequência.
**Prioridade:** baixa — as tasks Celery de bidding não disparam atualmente.

---

[session: t4] [module: bidding]
