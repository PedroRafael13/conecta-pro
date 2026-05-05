# T1 CPRO12 — Diagnóstico Canais de Envio Kit GED
**Data:** 2026-05-05
**Tipo:** READ-ONLY — diagnóstico pré-implementação
**Branch:** feature/people-management-reorganization

---

## CANAL EMAIL

**Código send_email:**
- `backend/modules/people_management/ged/controllers/kit_controller.py` — linha 291
  - `POST /{kit_id}/send-email` — endpoint existe, usa smtplib diretamente (texto puro, sem link Drive)
- `backend/modules/gdrive/services/email_kit_service.py` — `EmailKitService`
  - Implementação mais completa: HTML responsivo, decide link Drive (>10MB) vs anexos (<10MB)
  - **NÃO está conectado ao endpoint atual**

**core/mailer.py:** 87 linhas, `async def send_email` na linha 13 — disponível mas não usado no GED

**Credenciais SMTP no .env raiz (apenas nomes):**
```
SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
SMTP_USE_TLS, SMTP_FROM_EMAIL, SMTP_FROM_NAME, SMTP_USER, SMTP_FROM
```
→ Todas presentes. SMTP parece configurado.

**Endpoint HTTP:** `POST /api/v1/people-management/ged/kits/{kit_id}/send-email` — HTTP 404 (kit_id inválido no teste) = endpoint roteado corretamente.

**Uso no GED:** ✅ Endpoint implementado. Lógica: busca cliente, monta texto puro, envia via SMTP diretamente.

**Status: ⚠️ PARCIAL**
**Falta:**
1. Endpoint atual (`kit_controller.py`) envia texto puro sem link do Drive — não integra com `EmailKitService`
2. `EmailKitService` (HTML + Drive link) existe mas não está conectado a nenhum endpoint do GED
3. Integrar `EmailKitService.enviar_kit_por_email()` ao endpoint, ou criar endpoint no `gdrive_controller` que une GDrive + Email

---

## CANAL GOOGLE DRIVE

**Módulo gdrive (arquivos):**
```
backend/modules/gdrive/__init__.py
backend/modules/gdrive/controllers/gdrive_controller.py
backend/modules/gdrive/services/gdrive_service.py       ← GDriveService (OAuth2 + service account)
backend/modules/gdrive/services/kit_drive_service.py    ← KitDriveService (upload completo)
backend/modules/gdrive/services/email_kit_service.py    ← EmailKitService (email com link)
```

**Funções de upload implementadas:**
- `GDriveService.fazer_upload_arquivo(file_path, folder_id, file_name)` → upload + retorna webViewLink
- `GDriveService.garantir_estrutura_cliente(client_name, competencia)` → cria pastas cliente/mês
- `GDriveService.obter_link_pasta(folder_id, tornar_publico=True)` → link compartilhável
- `KitDriveService.montar_kit_no_drive(client_id, competencia)` → pipeline completo

**Credenciais GDrive (apenas nomes):**
```
GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REDIRECT_URI,
GDRIVE_ROOT_FOLDER_ID, GDRIVE_KITS_FOLDER_ID, GDRIVE_OWNER_EMAIL, GDRIVE_ENABLED
```

**Service account file:** `/opt/conecta-pro/config/google_drive_credentials.json` — referenciado no código, não encontrado em `credentials/`

**Endpoints disponíveis (registrados em /api/v1/gdrive):**
```
GET  /status
POST /autorizar
GET  /kits
POST /kits/{client_id}/{competencia}/montar
POST /kits/{client_id}/{competencia}/montar-e-enviar   ← monta Drive + envia email
POST /kits/{client_id}/{competencia}/enviar-email
GET  /kits/{client_id}/{competencia}/link
GET  /portal/{client_id}/kits
GET  /oauth/callback
POST /desconectar
```

**Status OAuth2 real:**
```json
{"conectado":true,"email":"jordansjesus@gmail.com","tipo":"oauth2",
 "credenciais_configuradas":true,"mensagem":"Google Drive conectado via OAuth2 (jordansjesus@gmail.com)"}
```
→ **GDrive JÁ ESTÁ CONECTADO e autorizado com conta jordansjesus@gmail.com**

**Kits montados no Drive:** 0 (gdrive_kits vazio — nenhum kit enviado ainda)

**Tabelas de suporte:** `gdrive_config`, `gdrive_kits`, `gdrive_uploads`, `gdrive_client_folders` — todas existem

**Status: ✅ PRONTO**
**Falta:**
1. Nenhuma implementação nova necessária — apenas acionar o endpoint `/montar-e-enviar` para um kit real
2. `GDRIVE_ROOT_FOLDER_ID` e `GDRIVE_KITS_FOLDER_ID` precisam ser IDs reais de pastas no Drive de Jordan

---

## CANAL WHATSAPP

**Código WhatsApp no projeto:**
- Sem módulo específico para WhatsApp no GED ou gedeon
- Menções apenas em migrations (schemas de tabelas de notificação) e `main_production.py`
- Sem `send_kit_via_whatsapp` implementado em nenhum arquivo

**Credenciais WhatsApp (apenas nomes):**
```
WHATSAPP_API_ENABLED, EVOLUTION_API_URL, EVOLUTION_API_KEY, WHATSAPP_INSTANCE_ID
```
→ Variáveis presentes no .env

**Endpoint /whatsapp/status:**
```json
{"online":false,"instance":"conecta-pro","enabled":true,
 "details":{"online":false,"error":"Cannot connect to host api.evolution.app.br:443 ssl:default [Name or service not known]"}}
HTTP 200
```
→ `EVOLUTION_API_URL` aponta para `api.evolution.app.br` — DNS não resolve (host inválido ou serviço down)

**Status: ❌ AUSENTE para GED**
**Falta:**
1. Fix em `EVOLUTION_API_URL` — URL atual não resolve DNS
2. Implementar endpoint de envio do kit por WhatsApp (link Drive via Evolution API)
3. Recomendação Jordan: configurar Evolution API self-hosted ou corrigir a URL antes de implementar

---

## BANCO — campos de envio em ged_document_kits

| Coluna | Tipo | Nullable | Estado |
|--------|------|----------|--------|
| sent_at | timestamptz | YES | NULL em todos os kits |
| sent_method | varchar | YES | NULL em todos os kits |
| sent_to | varchar | YES | NULL em todos os kits |
| zip_file_path | varchar | YES | NULL em todos os kits |
| google_drive_link | varchar | YES | NULL em todos os kits |

**google_drive_folder_id:** NÃO existe como coluna (gdrive_kits tem folder_id separado)

**Estado dos kits (TOP 10 por completude):**
```
status       | enviado | sent_method | drive_link | zip  | docs | docs_com_arq | pct
em_montagem  | f       | -           | f          | f    |   24 |            1 | 4.2%
em_montagem  | f       | -           | f          | f    |   30 |            1 | 3.3%
em_montagem  | f       | -           | f          | f    |   42 |            1 | 2.4%
...restante 0.0%
```
→ Nenhum kit enviado. Completude máxima: 4.2% — documentos físicos ainda em geração pelo GEDEON.

---

## GATILHO: MANUAL vs AUTOMÁTICO

**Botão manual na UI (endpoints disponíveis):**
- `POST /api/v1/people-management/ged/kits/{kit_id}/send-email` → email texto puro ✅
- `POST /api/v1/people-management/ged/kits/{kit_id}/send` → marca como enviado (método livre) ✅
- `POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar-e-enviar` → Drive + email completo ✅

**Task automática KRONOS:** ❌ Não existe — `kronos_tasks.py` tem apenas verificação diária, assinaturas e certidões. Nenhuma task de envio automático quando completude atinge 100%.

**Recomendação:** Manual primeiro (botão no frontend chamando `/montar-e-enviar`) + automático no KRONOS como fase 2 (threshold completude=100%).

---

## RESUMO POR CANAL

| Canal | Código | Credenciais | Endpoint | O que falta |
|-------|--------|-------------|----------|-------------|
| Email | ⚠️ Parcial | ✅ SMTP configurado | ✅ HTTP 404→kit_id válido | Integrar EmailKitService (HTML + Drive link) ao endpoint |
| GDrive | ✅ Completo | ✅ OAuth2 conectado (jordansjesus@gmail.com) | ✅ /montar-e-enviar | Apenas acionar com kit real + verificar GDRIVE_ROOT_FOLDER_ID |
| WhatsApp | ❌ Ausente | ⚠️ Variáveis existem, URL inválida | ❌ Offline (DNS fail) | Fix Evolution API URL + implementar endpoint de envio |

---

## Estimativa de esforço por canal

| Canal | Esforço | Observação |
|-------|---------|------------|
| GDrive | **0 prompts** | Pronto — apenas acionar |
| Email | **1 prompt** | Integrar EmailKitService ao endpoint existente |
| WhatsApp | **2 prompts** | Fix URL + implementar endpoint (pós-configuração Evolution) |

---

## Hipóteses validadas (H1-H8)

| Hipótese | Resultado |
|----------|-----------|
| H1: código send_email no GED/gedeon | ✅ CONFIRMADO — kit_controller.py:291 + EmailKitService |
| H2: código upload Google Drive no GED | ✅ CONFIRMADO — gdrive_service.py + kit_drive_service.py |
| H3: credenciais SMTP no .env | ✅ CONFIRMADO — 9 variáveis SMTP presentes |
| H4: credenciais GDrive no .env | ✅ CONFIRMADO — 7 variáveis GDRIVE presentes |
| H5: endpoint de envio registrado | ✅ CONFIRMADO — /send-email + /montar-e-enviar |
| H6: task Celery de envio no gedeon | ❌ NÃO EXISTE — kronos_tasks.py sem task de envio |
| H7: campos sent_at/sent_method/zip/drive_link na tabela | ✅ CONFIRMADO — todos presentes, todos NULL |
| H8: módulo gdrive com serviço de upload funcional | ✅ CONFIRMADO — GDriveService.fazer_upload_arquivo() implementado |

---

## Achado crítico — GDrive JÁ CONECTADO

`/api/v1/gdrive/status` retornou `conectado: true, email: jordansjesus@gmail.com`.
O Drive está autorizado e pronto. Nenhuma implementação de autenticação necessária.
Próximo passo imediato: acionar `POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar-e-enviar`
com um kit que tenha documentos reais (file_path não-null).

---

Commit: [ver STEP 8]

**T1 DIAG ENVIO CPRO12 OK — mapa completo gerado.**
**GDrive: PRONTO. Email: parcial (1 prompt). WhatsApp: não configurado (2 prompts).**
