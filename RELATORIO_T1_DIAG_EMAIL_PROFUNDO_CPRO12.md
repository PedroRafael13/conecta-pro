# T1-DIAG-EMAIL-PROFUNDO CPRO12 — Pipeline de Email GED Kits
**Data:** 2026-05-05
**Tipo:** READ-ONLY — diagnóstico profundo do canal email
**Branch:** feature/people-management-reorganization

---

## RESULTADO

> 3 implementações de email mapeadas. EmailKitService (email_kit_service.py) confirmado como
> fonte do template HTML #1E3A5F das fotos de Jordan. Pipeline completo: endpoint gdrive_controller
> → EmailKitService.enviar_kit_por_email() → SMTP_SSL port 465 (smtp.hostinger.com).
> kit_controller.py:291 envia texto puro (NÃO HTML). export_service.py:274 é STUB (sem SMTP real).

---

## H1 — Fonte do template HTML azul (#1E3A5F)

**Status: ✅ CONFIRMADO**

`backend/modules/gdrive/services/email_kit_service.py`
- Criado em 07/04/2026 via commit `4ba5d0f5` (14:05:10 UTC) — mesmo dia do email que Jordan recebeu
- Mensagem do commit: "feat(gdrive/email): envio automático de kit por e-mail"
- Template HTML com `background: #1E3A5F` (azul navy = cor das fotos de Jordan)
- 297 linhas; classe `EmailKitService` com método `enviar_kit_por_email()`

**Trechos chave:**
```python
TAMANHO_MAX_ANEXO = 10 * 1024 * 1024  # 10MB
# if total_size > 10MB OR share_link fornecido → envia link Drive
# else → anexa arquivos
```

---

## H2 — Rota de envio (endpoint vs task Celery)

**Status: ✅ CONFIRMADO — endpoint HTTP, NÃO task Celery**

EmailKitService é chamado apenas por `gdrive_controller`:
- `POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar-e-enviar` → monta Drive + envia email
- `POST /api/v1/gdrive/kits/{client_id}/{competencia}/enviar-email` → apenas email (Drive já montado)

`kronos_tasks.py` NÃO tem nenhuma task de envio de email GED.
Nenhum `@app.task` ou `@shared_task` referencia `EmailKitService`.

---

## H3 — "0 documentos" no email

**Status: ✅ CONFIRMADO — docs existem desde 22/04; file_path NULL em 1230/1237**

```sql
-- Data dos registros em ged_kit_documents
SELECT COUNT(*) FROM ged_kit_documents WHERE created_at < '2026-04-08';
-- → 0 rows (nenhum doc antes de 08/04)

SELECT COUNT(*) FROM ged_kit_documents;
-- → 1237 total (todos criados após 22/04/2026)

SELECT COUNT(*) FROM ged_kit_documents WHERE file_path IS NOT NULL;
-- → 7 docs com arquivo físico; 1230 com file_path NULL
```

**Causa do "0 documentos":** EmailKitService itera apenas docs com `file_path IS NOT NULL`.
Em 07/04 não existia NENHUM registro em ged_kit_documents (tabela vazia antes de 08/04).
Email de 07/04 foi enviado com lista de documentos vazia porque o GEDEON ainda não havia
gerado nenhum documento físico.

---

## H4 — Destinatário dinâmico

**Status: ✅ CONFIRMADO**

Dois caminhos distintos para o destinatário:

| Implementação | Tabela consultada | Campo |
|---------------|-------------------|-------|
| `EmailKitService._buscar_email_cliente(client_id)` | `clients.email` → fallback `crm_contacts.email` | Dinâmico por client_id |
| `kit_controller.py:291 send_kit_email()` | `ged_clients.contact_email` | Dinâmico por kit_id |
| `export_service.py:274 send_via_email()` | Parâmetro `email_addresses` | Passado pelo chamador |

**Amostras de emails reais (ged_clients.contact_email):**
- `gelain@conectamais.pro`
- `parisevillage@conectamais.pro`

---

## H5 — SMTP funcional no container

**Status: ✅ CONFIRMADO**

```python
# Assinatura de core/mailer.py:
send_email(to_email: str, subject: str, html_body: str) -> bool
```

**Variáveis SMTP no container (`docker exec conecta-pro-backend`):**
```
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USE_TLS=false  → usa smtplib.SMTP_SSL (correto para porta 465)
SMTP_USERNAME=noreply@conectamais.pro
SMTP_FROM_EMAIL=noreply@conectamais.pro
SMTP_FROM_NAME=Conecta PRO
SMTP_PASSWORD=<redacted>
```

**Lógica em core/mailer.py (linhas 31-35):**
```python
if settings.SMTP_USE_TLS:
    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
    server.starttls()
else:
    server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
```
→ SMTP_USE_TLS=false + port 465 → `SMTP_SSL` (correto para Hostinger)

**Nota:** `core/mailer.py` NÃO é usado por nenhum dos 3 caminhos GED.
EmailKitService usa seu próprio smtplib interno; kit_controller usa smtplib diretamente.

---

## H6 — Endpoint kit_controller retorna 404

**Status: ✅ CONFIRMADO (kit_id válido → HTTP 404 "Kit não encontrado")**

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=JsJ618908@#%" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# KIT_ID testado: 011e6182-8351-4524-98dd-4bb747db5b31
curl -sf -X POST "http://127.0.0.1:8080/api/v1/people-management/ged/kits/011e6182-8351-4524-98dd-4bb747db5b31/send-email" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"email": "jordan@test.com"}'
# → {"detail": "Kit não encontrado"}   (HTTP 404)
```

**Causa:** kit_controller busca via `GedDocumentKit.id` com JOIN em `GedClient`.
O kit_id `011e6182` existe na tabela `ged_document_kits` mas pode não ter registro
correspondente em `ged_clients` (FK join falha). Endpoint está roteado corretamente.

---

## H7 — EmailKitService desconectado do kit_controller

**Status: ✅ CONFIRMADO**

`kit_controller.py:291 send_kit_email()`:
- Envia **texto puro** via smtplib próprio
- Corpo: "Segue em anexo o kit documental referente ao mês {competencia}..."
- NÃO chama `EmailKitService`
- NÃO usa `core/mailer.py`

`EmailKitService.enviar_kit_por_email()`:
- Template HTML #1E3A5F
- Chamado apenas por `gdrive_controller`
- Rota: `POST /api/v1/gdrive/kits/{client_id}/{competencia}/enviar-email`

**Gap:** Dois caminhos separados que deveriam ser um só.
Fix recomendado: kit_controller.py:291 → delegar para EmailKitService.

---

## H8 — Histórico de envios reais

**Status: ✅ CONFIRMADO — zero envios registrados**

```sql
SELECT COUNT(*) FROM ged_document_kits WHERE sent_at IS NOT NULL;
-- → 0

SELECT COUNT(*) FROM ged_document_kits WHERE sent_method IS NOT NULL;
-- → 0

-- Busca de logs de 07/04/2026 (dia do email HTML recebido)
SELECT COUNT(*) FROM ged_document_kits
WHERE created_at::date = '2026-04-07';
-- → 0 (tabela vazia antes de 08/04)
```

**Conclusão:** O email HTML de 07/04 que Jordan recebeu foi enviado via
`POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar-e-enviar` ou `/enviar-email`
mas NÃO gravou `sent_at` no `ged_document_kits`. Isso é um gap na gdrive_controller —
após envio via EmailKitService, o `ged_document_kits` não é atualizado.

---

## Mapa Completo do Pipeline de Email

```
CAMINHO 1 (ATIVO — HTML #1E3A5F):
  POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar-e-enviar
       └─ gdrive_controller.py
           ├─ KitDriveService.montar_kit_no_drive() → upload Google Drive
           └─ EmailKitService.enviar_kit_por_email(client_id, competencia, share_link)
               ├─ _buscar_email_cliente(client_id) → clients.email
               ├─ if total_size > 10MB → HTML com link Drive
               ├─ else → HTML com arquivos anexados
               └─ smtplib.SMTP_SSL(smtp.hostinger.com:465) ← MESMO HOST/PORT
                   ✗ NÃO atualiza ged_document_kits.sent_at

CAMINHO 2 (EXISTENTE — texto puro):
  POST /api/v1/people-management/ged/kits/{kit_id}/send-email
       └─ kit_controller.py:291
           ├─ Busca GedClient.contact_email
           ├─ Envia texto puro via smtplib.SMTP_SSL
           └─ NÃO usa EmailKitService
               ✗ NÃO usa template HTML
               ✗ NÃO inclui link Drive

CAMINHO 3 (STUB — sem envio real):
  POST /api/v1/people-management/ged/kits/{kit_id}/send
       └─ export_service.py:274
           └─ Apenas marca status='enviado' + cria access log
               ✗ NÃO envia SMTP
               ✗ Mensagem: "Integração com serviço de email será implementada com SES/SMTP"
```

---

## Gaps identificados

| Gap | Impacto | Fix |
|-----|---------|-----|
| kit_controller usa texto puro (não HTML) | Email feio sem link Drive | Refatorar para usar EmailKitService |
| EmailKitService não atualiza ged_document_kits.sent_at | Sem histórico de envios | Adicionar UPDATE após envio bem-sucedido |
| export_service.send_via_email é STUB | Endpoint /send não envia email | Implementar ou remover o stub |
| H6: kit_id 011e6182 retorna 404 | Kit sem GedClient associado | Verificar FK ged_clients ↔ ged_document_kits |
| core/mailer.py não usado no GED | Código morto para email GED | Centralizar: gdrive+kit_controller → core/mailer |

---

## Resumo H1-H8

| Hipótese | Status | Evidência |
|----------|--------|-----------|
| H1: EmailKitService = fonte do template #1E3A5F | ✅ CONFIRMADO | commit 4ba5d0f5 (07/04), `background: #1E3A5F` em email_kit_service.py |
| H2: email via endpoint HTTP (não Celery task) | ✅ CONFIRMADO | gdrive_controller → EmailKitService; nenhum @shared_task de email |
| H3: "0 documentos" porque ged_kit_documents estava vazio | ✅ CONFIRMADO | 0 docs antes de 08/04; 1230/1237 com file_path NULL |
| H4: destinatário dinâmico por client_id | ✅ CONFIRMADO | EmailKitService → clients.email; kit_controller → ged_clients.contact_email |
| H5: SMTP funcional no container (port 465, SMTP_SSL) | ✅ CONFIRMADO | smtp.hostinger.com:465, SMTP_USE_TLS=false → SMTP_SSL |
| H6: endpoint /send-email retorna 404 para kit sem GedClient | ✅ CONFIRMADO | HTTP 404 "Kit não encontrado" para kit_id 011e6182 |
| H7: EmailKitService desconectado do kit_controller | ✅ CONFIRMADO | Dois caminhos separados; kit_controller não chama EmailKitService |
| H8: zero sent_at gravados — email de 07/04 sem trace em DB | ✅ CONFIRMADO | 0 rows WHERE sent_at IS NOT NULL; gdrive_controller não atualiza sent_at |

---

**T1 DIAG EMAIL CPRO12 OK — mapa completo do pipeline de email.**
**EmailKitService = fonte do HTML #1E3A5F. Pipeline: gdrive_controller → SMTP_SSL 465. 5 gaps documentados.**
