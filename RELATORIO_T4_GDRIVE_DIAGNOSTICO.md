# T4 — GDrive Diagnóstico
**Data:** 2026-05-04
**Executor:** Claude Sonnet 4.6 [session: t4] [module: gdrive]
**Objetivo:** Mapear estado atual completo do GDrive. Sem modificações.

---

## STEP 1 — Estado gdrive_config

### Schema real da tabela (colunas diferentes do esperado)

```
                 Table "public.gdrive_config"
     Column     |            Type             | Nullable
----------------+-----------------------------+----------
 id             | uuid                        | not null
 owner_email    | character varying(255)      | not null
 root_folder_id | character varying(255)      |
 kits_folder_id | character varying(255)      |
 access_token   | text                        |
 refresh_token  | text                        |
 token_expiry   | timestamp without time zone |
 is_connected   | boolean                     |
 scopes         | jsonb                       |
 created_at     | timestamp without time zone |
 updated_at     | timestamp without time zone |
```

> ⚠️ Coluna `folder_id` NÃO existe. Colunas reais: `root_folder_id` e `kits_folder_id`.
> ⚠️ Coluna `is_active` NÃO existe. Coluna real: `is_connected`.
> ⚠️ Coluna `folder_name` NÃO existe.

### Dados atuais

| Campo | Valor |
|---|---|
| `id` | `d93e558a-898b-43c3-8da1-0f1e63dc8131` |
| `owner_email` | `jordansjesus@gmail.com` |
| `root_folder_id` | `1XSNuCykj298Ac_ClGml3_rLnxIDOJORr` |
| `kits_folder_id` | `1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck` |
| `is_connected` | `true` |
| `token_expiry` | **2026-04-11 20:50:46 — EXPIRADO (23 dias atrás)** |
| `criado` | 2026-04-08 02:44:36 |
| `atualizado` | 2026-04-11 19:50:47 |

---

## STEP 2 — Contagens relacionadas

| Métrica | Valor |
|---|---|
| `gdrive_kits` (kits enviados ao Drive) | **0** |
| `gdrive_config` com `is_connected = true` | **1** |
| `ged_clients` (clientes GED) | **11** |
| `ged_document_kits` (kits montados) | **18** |
| `ged_kit_documents` (documentos nos kits) | **1.237** |
| com `file_path` preenchido | **7** |
| com `file_path` NULL | **1.230** ← bloqueio principal |

### Os 7 documentos com file_path (todos folha de pagamento 03/2026)

```
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Michelangelo.pdf
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Ideal Flores.pdf
/app/uploads/onvio/inss_guia/2026-04/Folha 03.2026_Mirante das Flores (2).pdf
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Prime Arena (1).pdf
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa dos Passaros.pdf
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa Dei Fior.pdf
/app/uploads/onvio/outros/2026-04/Folha 03.2026_Laranjeiras Village.pdf
```

---

## STEP 3 — Endpoints GDrive disponíveis

```
GET  /api/v1/gdrive/status
POST /api/v1/gdrive/autorizar
GET  /api/v1/gdrive/kits
GET  /api/v1/gdrive/ingestao/status
POST /api/v1/gdrive/kits/{cliente_id}/{competencia}/montar-e-enviar
POST /api/v1/gdrive/kits/{client_id}/{competencia}/enviar-email
POST /api/v1/gdrive/kits/{client_id}/{competencia}/montar
GET  /api/v1/gdrive/kits/{client_id}/{competencia}/link
GET  /api/v1/gdrive/portal/{client_id}/kits
GET  /api/v1/gdrive/oauth/callback
POST /api/v1/gdrive/desconectar
GET  /api/v1/gdrive/autorizar
```

**Endpoint `/gdrive/pastas` — NÃO EXISTE** → HTTP 404.

---

## STEP 4 — Chamadas de API

### GET /gdrive/status

```json
{
    "conectado": true,
    "email": "jordansjesus@gmail.com",
    "nome": "jordansjesus@gmail.com",
    "tipo": "oauth2",
    "credenciais_configuradas": true,
    "mensagem": "Google Drive conectado via OAuth2 (jordansjesus@gmail.com)",
    "acao": null
}
```

> ⚠️ Retorna `conectado: true` porque lê `is_connected = TRUE` no banco — NÃO verifica se o access_token é válido.

### GET /gdrive/pastas

```
{"detail":"Not Found"}
HTTP 404
```

### GET /gdrive/ingestao/status

```json
{
    "drive_conectado": false,
    "kits_enviados": 0,
    "kits_pendentes": 18,
    "total_kits": 18,
    "ultima_atualizacao": "2026-04-28 02:48:24.53377+00",
    "status": "aguardando_autorizacao"
}
```

> ⚠️ `drive_conectado: false` porque `gdrive_service.esta_conectado()` procura service account file que não existe no container.

---

## STEP 5 — Controller: nenhum endpoint de listagem de pastas

Grep em `gdrive_controller.py` por `listar_pastas`, `folders`, `/pastas`: **resultado vazio**.
Não existe nenhum endpoint para listar pastas do Drive do Jordan.

---

## STEP 6 — kit_drive_service: uso do folder_id

O serviço lê tokens do banco e chama `gdrive_service.conectar_com_tokens()`.
A query de documentos:

```sql
SELECT gkd.file_path, gkd.document_name, gkd.document_type, gkd.file_size_bytes
FROM ged_kit_documents gkd
JOIN ged_document_kits gdk ON gdk.id = gkd.kit_id
WHERE gdk.client_id = :client_id
  AND gdk.reference_month::text LIKE :comp_prefix
  AND gkd.file_path IS NOT NULL   -- ← filtra NULL
```

Com 1.230 de 1.237 documentos com `file_path = NULL`, o resultado é sempre **0 documentos** → kit não sobe para o Drive.

`kits_folder_id` é usado como `parent_id` ao criar pasta no Drive (via `garantir_estrutura_cliente`).
Env vars no container: `GDRIVE_KITS_FOLDER_ID=1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck` ✅

---

## DECISÃO

| Pergunta | Resposta |
|---|---|
| GDrive autorizado? | **PARCIALMENTE** — tokens no banco, `is_connected=true`, mas access_token expirado 23 dias atrás; service account file ausente |
| Endpoint pra listar pastas via UI? | **NÃO** — `/gdrive/pastas` = 404, não existe |
| `kits_folder_id` atual | `1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck` — preenchido (não estava vazio) |
| Configs ativas | **1** (`is_connected = true`) |

---

## Diagnóstico: 3 problemas sobrepostos

### Problema 1 — Access token expirado (bloqueio de autenticação)
- `token_expiry = 2026-04-11` — expirado há 23 dias
- `refresh_token` ainda está no banco e é permanente (OAuth2 refresh tokens não expiram)
- Mas `gdrive_service.esta_conectado()` tenta **service account** primeiro → falha → nunca tenta OAuth2

### Problema 2 — Service account file não existe (bloqueio de SDK)
- `gdrive_service.esta_conectado()` procura `/opt/conecta-pro/config/google_drive_credentials.json`
- Arquivo ausente no container → `_service = None` → SDK não faz nenhuma chamada real ao Drive
- Resultado: `ingestao/status` → `drive_conectado: false`; kits não sobem

### Problema 3 — file_path NULL em 99% dos documentos (bloqueio de conteúdo)
- 1.230 de 1.237 documentos têm `file_path = NULL`
- Query do kit_drive_service filtra `WHERE file_path IS NOT NULL`
- Resultado: 0 documentos encontrados → kit não é montado → `gdrive_kits = 0`
- **Mesmo que os problemas 1 e 2 fossem resolvidos, o upload continuaria falhando**

---

## Respostas finais

**"Existe endpoint pra Jordan listar pastas via UI?"**
→ **NÃO.** Não existe `/gdrive/pastas` nem qualquer outro endpoint de listagem de pastas do Drive.

**"É preciso pegar folder_id direto do Google Drive (manual)?"**
→ **NÃO** — o `kits_folder_id` já está cadastrado tanto no banco quanto na env var. O problema não é o folder_id — é a autenticação expirada e os file_paths nulos.

---

## Opções para Jordan decidir

| Opção | Resolve | Esforço |
|---|---|---|
| **A — Re-fazer OAuth** | Problema 1: renova access + refresh token | Jordan acessa URL de autorização (5min) |
| **B — Preencher file_path** nos 1.230 documentos | Problema 3: documentos ficam uploadáveis | Tarefa backend — mapear PDFs Onvio para os registros |
| **C — A + B em sequência** | Problemas 1 + 3: Drive conecta E encontra documentos | Necessário para `gdrive_kits > 0` |

> **Atenção:** Problema 2 (service account) é ignorável se o OAuth2 for refeito corretamente — o `conectar_com_tokens` usa as credenciais OAuth diretamente, sem depender do arquivo JSON.

---

## Variáveis de ambiente no container (confirmadas)

```
GDRIVE_ROOT_FOLDER_ID=1XSNuCykj298Ac_ClGml3_rLnxIDOJORr
GDRIVE_KITS_FOLDER_ID=1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck
GDRIVE_CLIENT_ID=576020339239-bs4amjo67m3v0j9gerqnrk6gpohvjqvd.apps.googleusercontent.com
GDRIVE_CLIENT_SECRET=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
GDRIVE_REDIRECT_URI=https://erp.conectamais.pro/api/v1/gdrive/oauth/callback
GDRIVE_ENABLED=true
GDRIVE_OWNER_EMAIL=jordansjesus@gmail.com
```

[session: t4] [module: gdrive]
