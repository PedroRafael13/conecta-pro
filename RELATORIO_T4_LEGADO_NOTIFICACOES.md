# T4 — Investigação Sistema Legado de Notificações
**Data:** 2026-05-04
**Executor:** Claude Sonnet 4.6 [session: t4] [module: notifications]
**Objetivo:** Mapear estado real do sistema legado. Read-only.

---

## STEP 1 — communication_notifications: histórico completo

### Por canal e tipo

| Canais | Tipo | Qtd | Primeiro | Último |
|--------|------|-----|----------|--------|
| `["in_app", "email"]` | lembrete | 1 | 2026-03-09 07:07 | 2026-03-09 07:07 |
| `["in_app"]` | alerta | 2 | 2026-03-09 01:37 | 2026-03-09 05:37 |
| `["in_app", "email"]` | alerta | 1 | 2026-03-09 03:37 | 2026-03-09 03:37 |
| `["in_app"]` | operacional | 4 | 2026-03-06 07:37 | 2026-03-08 23:37 |
| `["in_app"]` | lembrete | 1 | 2026-03-08 07:37 | 2026-03-08 07:37 |
| `["in_app", "email"]` | operacional | 1 | 2026-03-08 07:37 | 2026-03-08 07:37 |
| `["in_app"]` | sistema | 1 | 2026-03-04 07:37 | 2026-03-04 07:37 |
| `["in_app"]` | comunicado | 1 | 2026-03-02 07:37 | 2026-03-02 07:37 |

**Total: 12 registros. Tudo em março/2026. Zero após 2026-03-09.**

### Por mês

| Mês | Qtd | Users distintos |
|-----|-----|-----------------|
| 2026-03 | 12 | 1 |

### Últimas 5 entries

| Tipo | Título | Canais | Enviado | Lido |
|------|--------|--------|---------|------|
| lembrete | Prazo de reembolso vencendo | in_app + email | ✅ | ❌ |
| alerta | Posto Gelain sem cobertura | in_app | ✅ | ❌ |
| alerta | Ocorrência crítica registrada | in_app + email | ✅ | ❌ |
| alerta | Ronda não concluída — Posto IAM | in_app | ✅ | ❌ |
| operacional | Banco de horas — saldo negativo | in_app | ✅ | ✅ |

> ⚠️ `sent_at IS NOT NULL` = marcado como enviado, mas **não significa que saiu por email** (ver STEP 4).

---

## STEP 2 — Quem dispara notificações no código

### Arquivo ORM do modelo

```
backend/modules/operacional/communication/models/notification.py
  → __tablename__ = "communication_notifications"
```

### Quem usa CommunicationNotification (importadores reais)

| Módulo | Arquivo |
|--------|---------|
| Operacional | `communication/services/notification_service.py` |
| Operacional | `communication/repositories/communication_repository.py` |
| Operacional | `communication/controllers/notification_controller.py` |
| Operacional | `communication/services/announcement_service.py` (lazy import) |
| Operacional | `communication/services/alert_service.py` (lazy import) |
| **Bidding** | `bidding/services/notification_service.py` (lazy import) |

### Todos os services de notif encontrados

```
backend/modules/bidding/services/notification_service.py
backend/modules/bidding/tasks/notification_tasks.py
backend/modules/client_portal/services/portal_notification_service.py
backend/modules/hr/employee_portal/services/notification_service.py
backend/modules/hr/mobile_time_clock/services/push_notification_service.py
backend/modules/mobile/services/push_notification_service.py
backend/modules/notifications/controllers/intelligent_notification_controller.py
backend/modules/notifications/controllers/notification_controller.py
```

---

## STEP 3 — Os 4 enums fragmentados

### Enum 1: Operacional (`communication/models/notification.py`)

```python
class NotificationType(StrEnum):
    OCORRENCIA | MEDIDA | COMUNICADO | ESCALA | ALERTA
    SUBSTITUICAO | BANCO_HORAS | TAREFA | APROVACAO | SISTEMA

class NotificationChannel(StrEnum):
    PUSH | EMAIL | SMS | WHATSAPP | IN_APP
```

### Enum 2: HR Employee Portal (`employee_portal/models/employee_notification.py`)

```python
class NotificationType(StrEnum):
    PAYSLIP_AVAILABLE | PAYSLIP_RECTIFIED | PAYMENT_SCHEDULED
    VACATION_APPROVED | VACATION_REJECTED | VACATION_REMINDER | VACATION_EXPIRING
    DOCUMENT_AVAILABLE | (+ mais)

class NotificationPriority(StrEnum):
    LOW | NORMAL | HIGH | URGENT

class NotificationChannel(StrEnum):
    PORTAL (in_app) — sem email/telegram/whatsapp
```

### Enum 3: Bidding (`bidding/services/notification_service.py`)

```python
class NotificationChannel(StrEnum):
    EMAIL | PUSH | INTERNAL  ← sem whatsapp, sem in_app

class BiddingNotificationType(StrEnum):
    EDITAL_NOVO | EDITAL_VENCENDO | CERTIDAO_VENCENDO | PROPOSTA_STATUS
    DISPUTA_INICIANDO | CONVOCACAO | RESULTADO | + mais
```

### Enum 4: Notifications Hub (`notifications/models/notification_channel.py`)

```python
class ChannelType(StrEnum):
    EMAIL | WHATSAPP | SMS | PUSH | SLACK | TEAMS | WEBHOOK | IN_APP | TELEGRAM | VOICE
    ← hub não-ativo, não integrado ao legado
```

> ⚠️ Nenhum enum é compartilhado. Cada módulo definiu o seu próprio `NotificationChannel`.

---

## STEP 4 — Como cada módulo despacha: realidade vs. aparência

### Operacional — `notification_service._send_to_channels()`

```python
for channel in notification.channels:
    if channel == PUSH:
        provider = PushProviderFactory.get_provider("firebase")
        if provider:                           # ← se provider None: nada
            await provider.send_push(...)
    elif channel == EMAIL:
        logger.debug(f"Email para {user_id}: {title}")   # ← APENAS LOG
    elif channel == SMS:
        logger.debug(...)                                  # ← APENAS LOG
    elif channel == WHATSAPP:
        logger.debug(...)                                  # ← APENAS LOG
```

**Resultado:** Canal `in_app` → salva no banco ✅. Canal `email` → **`logger.debug` silencioso, sem envio real** ❌.

### HR — `notification_service.send_notification()`

```python
return await self.repo.create(data, condominio_id, created_by=created_by)
# ← salva em hr_employee_notifications. Zero envio externo.
```

**Resultado:** Apenas persiste no banco. Canal `PORTAL` = in_app ✅. Zero email/telegram ❌.

### Bidding — `_dispatch()` + `_dispatch_email()`

```python
if canal == INTERNAL: logger.info(...)          # ← log only
elif canal == EMAIL:  self._dispatch_email()    # ← tenta SMTP real
elif canal == PUSH:   self._push_buffer.append() # ← buffer in-memory
```

`_dispatch_email()` usa `smtplib` com fallback para log se SMTP não configurado.

**Resultado:**
- INTERNAL: log only ❌ (não chega ao usuário)
- EMAIL: **tenta enviar via SMTP** — o único módulo que realmente aciona envio externo
- PUSH: buffer in-memory (não persiste, não chega ao device) ❌

---

## STEP 5 — Canais externos: realmente funcionais?

### SMTP (email)

| Variável | Valor |
|----------|-------|
| `SMTP_HOST` | `smtp.hostinger.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USE_TLS` | `false` |
| `SMTP_USERNAME` | `noreply@conectamais.pro` |
| `SMTP_FROM_EMAIL` | `noreply@conectamais.pro` |

**Análise:** `SMTP_USE_TLS=false` + porta 465 → código entra no branch `SMTP_SSL(465)` — **correto para Hostinger**. SMTP está configurado e o `core/mailer.py` funciona.

**Mas:** Operacional e HR **não chamam** `core/mailer.send_email()`. Só Bidding chama.
Bidding despacha email **para `self._smtp_user`** (o próprio remetente `noreply@conectamais.pro`), não para Jordan nem colaboradores.

### Telegram

| Variável | Valor |
|----------|-------|
| `TELEGRAM_BOT_TOKEN` | `8343886201:AAFS...` (configurado) |
| `TELEGRAM_CHAT_ID` | `5536961034` |

**Único uso:** `financial/services/justificativa_service.py` — manda `requests.post` para Telegram quando uma justificativa financeira ocorre. **Funcional mas escopo muito limitado** — só finança, só para o chat de Jordan.

### WhatsApp / Evolution

| Variável | Valor |
|----------|-------|
| `EVOLUTION_API_KEY` | `your_evolution_api_key_here` ← **placeholder** |
| `EVOLUTION_API_URL` | `https://api.evolution.app.br` |
| `WHATSAPP_API_ENABLED` | `true` |

**Resultado: WhatsApp NÃO funciona.** `EVOLUTION_API_KEY` é o valor placeholder `"your_evolution_api_key_here"` — nunca configurado.

---

## STEP 6 — Tabelas auxiliares de notif

| Tabela | Registros |
|--------|-----------|
| `communication_notifications` | **12** |
| `hr_employee_notifications` | **0** |
| `portal_notifications` | **0** |
| `push_notifications` | **0** |
| `mobile_notification_logs` | não existe |
| `whatsapp_messages` | não existe |
| `telegram_messages` | não existe |
| `email_logs` | não existe |

> Praticamente todo o sistema de notif está na tabela central `communication_notifications` com 12 registros de março/2026. O restante: tabelas vazias ou inexistentes.

---

## STEP 7 — Celery: tasks de notificação ativas

Tasks registradas no worker `conecta-pro-celery-integrations`:

```
bidding.notificar_oportunidade_nova
bidding.notificar_prazo_edital
bidding.notificar_resultado_pipeline
```

**Nenhum log** de execução dessas tasks nos últimos 200 lines. Tasks registradas mas aparentemente não disparadas recentemente. Zero tasks de notif em celery-priority.

---

## DECISÃO — 5 perguntas respondidas

### ☑ Módulos que DISPARAM notif hoje

| Módulo | Tabela alvo | Frequência real |
|--------|-------------|-----------------|
| **Operacional** | `communication_notifications` | Última: 2026-03-09. Zero desde então |
| **HR** | `hr_employee_notifications` | Zero registros — nunca disparou em produção |
| **Bidding** | in-memory / SMTP | Tasks Celery registradas mas sem logs recentes |
| **Financeiro** | Telegram direto | Funciona mas escopo limitado (justificativas) |

### ☑ Canais REALMENTE funcionais

| Canal | Status real |
|-------|-------------|
| **in_app** | ✅ Funciona — salva no banco, frontend pode ler |
| **email (SMTP)** | ⚠️ SMTP configurado corretamente, MAS: operacional/HR não chamam o mailer. Só Bidding chama — e manda para o próprio remetente |
| **Telegram** | ✅ Funcional, mas apenas para justificativas financeiras → chat de Jordan |
| **WhatsApp** | ❌ Quebrado — `EVOLUTION_API_KEY` é placeholder não preenchido |
| **Push/Firebase** | ❌ `PushProviderFactory.get_provider("firebase")` retorna None (Firebase não configurado) |
| **SMS** | ❌ Apenas `logger.debug` — sem integração real |

### ☑ Há fluxos quebrados em silêncio? **SIM**

1. **Email operacional/HR:** `sent_at` marcado como não-nulo (aparece como "enviado") mas **o email nunca saiu** — só `logger.debug`. Falsa confirmação de entrega nos 12 registros de março.

2. **WhatsApp:** `WHATSAPP_API_ENABLED=true` mas `EVOLUTION_API_KEY=your_evolution_api_key_here` — toda chamada falha silenciosamente.

3. **Push Firebase:** `PushProviderFactory.get_provider("firebase")` retorna `None` — nenhuma exceção, nenhum log de erro, silêncio total.

4. **HR zero disparos:** `hr_employee_notifications` tem 0 rows — módulo de portal do funcionário nunca enviou notificação em produção, mesmo com service implementado.

5. **Bidding buffer in-memory:** notificações PUSH ficam no `_push_buffer` do singleton — reinício do container = perda total.

### ☑ Cobertura do sistema legado

| Categoria | Cobertura |
|-----------|-----------|
| Notif crítica (ocorrência, alerta) | ⚠️ Parcial — chega ao in_app, não ao celular/email |
| Alerta operacional (ronda, escala) | ⚠️ Parcial — só in_app |
| Lembrete (prazo, férias) | ⚠️ Parcial — só in_app |
| Comunicado administrativo | ⚠️ Parcial — só in_app |
| Notif financeira | ✅ Telegram funcional |
| Licitações | ⚠️ Parcial — Celery dispara mas entrega é in-memory |

### ☑ Recomendação simples (sem ativar hub)

**Três correções de baixo esforço que desbloqueiam entrega real:**

1. **Plugar `core/mailer.send_email()` no operacional `_send_to_channels`** (10 linhas): substituir o `logger.debug` de email pelo `await send_email(user_email, title, body)` — SMTP já está configurado e funcional.

2. **Preencher `EVOLUTION_API_KEY`** na env do container — única mudança de config necessária para desbloquear WhatsApp.

3. **Configurar Firebase** (ou remover canal PUSH dos registros existentes) — elimina o fluxo silencioso de push que nunca entrega.

Sem essas correções, o sistema legado entrega **apenas in_app** + **Telegram para finança**. Todo o resto é silêncio.

---

[session: t4] [module: notifications]
