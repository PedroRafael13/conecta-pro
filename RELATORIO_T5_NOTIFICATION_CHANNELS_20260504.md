# RELATORIO T5 — Notification Channels Diagnóstico
**Data:** 2026-05-04
**Tipo:** READ-ONLY / Diagnóstico
**Branch:** feature/people-management-reorganization

---

## Execução do Prompt

**T+0:** 17:09:44

---

## STEP 1 — Schema `notification_channels`

```
Table "public.notification_channels"
Column                    | Type
--------------------------+-----------------------------
id                        | uuid (PK)
tenant_id                 | uuid (NOT NULL)
name                      | varchar(100)
slug                      | varchar(100)
description               | text
channel_type              | channeltype (enum)
provider                  | channelprovider (enum)
status                    | channelstatus (enum)
provider_config           | jsonb  ← credenciais do provedor
sender_config             | jsonb  ← config de remetente
rate_limit_per_second     | integer
rate_limit_per_minute     | integer
rate_limit_per_hour       | integer
rate_limit_per_day        | integer
current_rate_count        | integer
rate_reset_at             | timestamp
max_retries               | integer
retry_delay_seconds       | integer
retry_backoff_multiplier  | double precision
priority                  | integer
fallback_channel_id       | uuid (FK → notification_channels.id)
is_default                | boolean
business_hours_only       | boolean
business_hours_start      | varchar(5)
business_hours_end        | varchar(5)
business_days             | integer[]
timezone                  | varchar(50)
total_sent / delivered / failed / bounced | integer (métricas)
delivery_rate             | double precision
avg_delivery_time_seconds | double precision
last_sent_at / last_error_at / last_error_message | timestamp/text
cost_per_message          | double precision
monthly_budget            | double precision
current_month_spend       | double precision
supported_categories      | varchar[]
extra_data / tags         | jsonb / varchar[]
active                    | boolean
created_at / updated_at   | timestamp
created_by / updated_by   | uuid
```

**Referenciada por:** `notification_logs`, `notification_queue`, `notification_templates`

---

## STEP 2 — Enums suportados

### `channeltype` (9 valores)
`email`, `in_app`, `push`, `sms`, `slack`, `teams`, `telegram`, `voice`, `webhook`, `whatsapp`

### `channelprovider` (23 valores)
| Categoria | Providers |
|-----------|-----------|
| Email | `smtp`, `sendgrid`, `mailgun`, `postmark`, `aws_ses` |
| Telegram | `telegram_bot` |
| WhatsApp | `twilio_whatsapp`, `whatsapp_business`, `messagebird_whatsapp` |
| SMS | `twilio_sms`, `nexmo`, `messagebird_sms`, `zenvia`, `aws_sns` |
| Push | `fcm`, `apns`, `onesignal` |
| Outros | `slack_api`, `teams_api`, `pusher`, `custom_webhook`, `internal` |

### `channelstatus`
`active`, `inactive`, `degraded`, `error`, `maintenance`

### Enum legado `notification_channel` (paralelo)
`email`, `in_app`, `push`, `slack`, `sms`, `telegram`, `webhook`, `whatsapp`

---

## STEP 3 — Código que CRIA notification_channels

**Resultado:** Nenhum INSERT direto em código Python.

Arquivos que referenciam `notification_channels`:
- `backend/alembic/versions/sprint36_create_notification_hub_tables.py` — migration que CRIA a tabela
- `backend/modules/notifications/models/notification_channel.py:88` — model ORM (`__tablename__ = "notification_channels"`)
- `backend/modules/config/models/notification_template.py:21` — FK do config
- `backend/modules/notifications/models/notification_template.py:61` — FK do hub
- `backend/modules/notifications/models/notification_log.py:76` — FK de log
- `backend/modules/notifications/models/notification_queue.py:64` — FK de queue

**Usos do campo `notification_channels` (como atributo JSONB em outros modelos — diferente da tabela):**
- `backend/modules/financial/models/billing_rule.py` — `notification_channels = Column(JSONB, default=["email", "push"])`
- `backend/modules/operacional/schemas/scale.py` — `notification_channels: list[str]`
- `backend/modules/hr/employee_portal/models/employee_preferences.py` — preferências de canal por user

**Conclusão:** Não há seed script. A tabela é criada pela migration sprint36 mas nunca populada.

---

## STEP 4 — Código que USA notification_channels

O dispatcher busca canais assim (`_get_channel`):
```python
# backend/modules/notifications/services/channel_dispatcher.py:554
db.query(NotificationChannel).filter(
    NotificationChannel.tenant_id == self.tenant_id,
    NotificationChannel.channel_type == queue_item.channel_type,
    NotificationChannel.is_default,
    NotificationChannel.active,
).first()
```

**ACHADO CRÍTICO:** Quando `_get_channel()` retorna `None` (tabela vazia), o dispatcher usa:
```python
# linha 578 — fallback silencioso
def _create_default_channel(self, channel_type: str) -> NotificationChannel:
    return NotificationChannel(
        name=f"Default {channel_type}",
        channel_type=ChannelType(channel_type),
        provider=ChannelProvider.INTERNAL,  # ← não envia nada
        max_retries=3,
        retry_delay_seconds=60,
    )
```

**Isso explica o comportamento atual:** O sistema não quebra com 500, mas usa `provider=INTERNAL` que não despacha para nenhum provedor real. As notificações ficam enfileiradas ou marcadas como enviadas sem chegar ao destinatário.

---

## STEP 5 — Schema `notification_templates`

Tabela completa com campos específicos por canal:
- `email_subject`, `email_body_html`, `email_body_text`, `email_from_name/address`, `email_cc/bcc`, `email_attachments`
- `whatsapp_template_name/namespace`, `whatsapp_body`, `whatsapp_buttons`, `whatsapp_variables`
- `sms_body`, `sms_unicode`, `sms_flash`
- `push_title`, `push_body`, `push_image_url`, `push_android_config`, `push_ios_config`
- `slack_text`, `slack_blocks`, `slack_attachments`
- `in_app_title`, `in_app_body`, `in_app_icon`, `in_app_action_url`
- `webhook_url`, `webhook_method`, `webhook_headers`, `webhook_body_template`

Também suporta: A/B testing (`is_variant`, `variant_weight`), aprovação (`requires_approval`), localização (`locale`, `translations`), versionamento (`version`, `previous_version_id`).

**FK:** `channel_id → notification_channels.id` (nullable) — templates podem existir sem canal mas não serão usados.

---

## STEP 6 — Sistema legado `communication_notifications`

Schema simples, sem FK para `notification_channels`:

```
Column          | Type
----------------+---------------------------
id              | uuid (PK)
tenant_id       | uuid
user_id         | uuid
title           | varchar(255)
body            | text
type            | varchar(50)  default 'sistema'
reference_type  | varchar(50)
reference_id    | uuid
channels        | jsonb  default '["in_app"]'  ← array de strings
sent_at         | timestamp
read_at         | timestamp
clicked_at      | timestamp
action_url      | varchar(500)
extra_data      | jsonb  default '{}'
is_active       | boolean  default true
created_at      | timestamp
```

**Últimos 3 registros (09/03/2026):**
| channels | type |
|----------|------|
| `["in_app", "email"]` | lembrete |
| `["in_app"]` | alerta |
| `["in_app", "email"]` | alerta |

Sistema legado usa apenas `in_app` e `email` como strings hard-coded.
**Independente do notification_channels hub** — nenhuma FK, nenhuma relação.

---

## STEP 7 — Variáveis de Ambiente

| Canal | Vars presentes |
|-------|---------------|
| **Telegram** | `TELEGRAM_BOT_TOKEN` ✅ · `TELEGRAM_CHAT_ID` ✅ |
| **WhatsApp (Evolution API)** | `WHATSAPP_API_ENABLED` ✅ · `EVOLUTION_API_URL` ✅ · `EVOLUTION_API_KEY` ✅ · `WHATSAPP_INSTANCE_ID` ✅ (duplicado em `.env` e `backend/.env`) |
| **Email/SMTP** | `SMTP_HOST` ✅ · `SMTP_PORT` ✅ · `SMTP_USERNAME` ✅ · `SMTP_PASSWORD` ✅ · `SMTP_USE_TLS` ✅ · `SMTP_FROM_EMAIL` ✅ · `SMTP_FROM_NAME` ✅ |

---

## DECISÃO — Mapa para Jordan

| Item | Resposta |
|------|----------|
| **[x] Tipos de canal suportados pelo enum** | `email`, `whatsapp`, `telegram`, `sms`, `push`, `in_app`, `slack`, `teams`, `voice`, `webhook` |
| **[x] Sistema legado funcional usa quais canais** | `in_app` e `email` (string JSONB, sem hub) |
| **[x] ENV vars já existem pra** | Telegram ✅ · WhatsApp Evolution ✅ · SMTP/Email ✅ |
| **[x] Há fluxo "novo" parado por falta de seed?** | **SIM** — tabela vazia → dispatcher usa fallback `provider=INTERNAL` → nada enviado |

---

## Achados Adicionais (auditoria)

### Achado crítico: fallback silencioso
O sistema **não falha com erro** quando `notification_channels` está vazia. O `ChannelDispatcher._create_default_channel()` cria um canal temporário em memória com `provider=INTERNAL`. Este provider não envia para nenhum serviço externo, mas também não loga erro visível. **Resultado:** notificações parecem "enviadas" no dashboard mas nunca chegam ao destinatário.

### Três StrEnums paralelos (fragmentação)
Existem 4 definições de `NotificationChannel` no código:
1. `backend/modules/notifications/models/notification_channel.py` — model ORM (tabela)
2. `backend/modules/operacional/communication/models/notification.py:37` — StrEnum legado
3. `backend/modules/hr/employee_portal/models/employee_notification.py:82` — StrEnum HR
4. `backend/modules/bidding/services/notification_service.py:47` — StrEnum licitações

Os módulos legados (operacional, HR, bidding) usam seus próprios enums e o sistema legado (`communication_notifications`), não o hub.

---

## Recomendação (Jordan decide)

Os 3 canais com credenciais prontas para seed imediato:

| Canal | `channel_type` | `provider` | Credenciais |
|-------|----------------|------------|-------------|
| Email | `email` | `smtp` | `SMTP_*` no `.env` |
| Telegram | `telegram` | `telegram_bot` | `TELEGRAM_BOT_TOKEN` |
| WhatsApp | `whatsapp` | `whatsapp_business` | `EVOLUTION_API_*` |

**Jordan decide:**
1. Quais canais ativar primeiro?
2. Manter sistema legado em paralelo ou migrar?
3. Quando seedar — próxima task executa o INSERT.

---

*T5 — READ-ONLY concluído. Nenhuma modificação no sistema.*
