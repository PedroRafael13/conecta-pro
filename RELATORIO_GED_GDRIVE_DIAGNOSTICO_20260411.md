# Diagnóstico GED / Google Drive OAuth2 — Conecta PRO
**Data:** 2026-04-11
**Comandos executados:** `GET /ged/configuracoes`, `GET /gdrive/configuracoes`, `GET /gdrive/autorizar`, logs backend

---

## Resumo Executivo

| Item | Status | Detalhe |
|------|--------|---------|
| `GET /ged/configuracoes` | ❌ 404 | URL errada — endpoint real é `/ged/config/drive` |
| `GET /gdrive/configuracoes` | ❌ 404 | Endpoint não existe |
| `GET /gdrive/autorizar` | ✅ URL gerada | OAuth2 funcionando |
| `GET /gdrive/status` | ❌ `conectado: false` | Service verifica service account (arquivo ausente), ignora tokens OAuth2 do banco |
| Tokens OAuth2 no banco | ⚠️ EXPIRADO | `token_expiry: 2026-04-08` — 3 dias vencido |
| Callback OAuth (log) | ❌ Erro scope | `Scope has changed` no último fluxo de autorização |

---

## Problema 1 — `GET /ged/configuracoes` retorna 404

### Causa raiz
O `ged_config_router` tem **dois prefixes acumulados**:

```
modules/ged/controllers/ged_config_controller.py  → prefix="/config"
main_production.py                                 → include_router(..., prefix="/ged")
```

**URL real:** `/api/v1/ged/config/drive` (não `/api/v1/ged/configuracoes`)

### Mapeamento completo dos endpoints GED config

| Método | URL Real | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/ged/config/drive` | Configuração Google Drive |
| POST | `/api/v1/ged/config/drive` | Salvar configuração |
| POST | `/api/v1/ged/config/drive/connect` | Conectar Drive |
| DELETE | `/api/v1/ged/config/drive/disconnect` | Desconectar |
| GET | `/api/v1/ged/config/email-templates` | Templates de email |
| GET | `/api/v1/ged/config/document-types` | Tipos de documento |
| GET | `/api/v1/ged/config/schedule` | Agendamento |
| POST | `/api/v1/ged/config/schedule` | Salvar agendamento |

### Teste do endpoint correto
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/ged/config/drive"
# → 404 (também falha — ver Problema 2)
```

---

## Problema 2 — `GET /gdrive/status` sempre `conectado: false`

### Causa raiz
O `gdrive_service.check_status()` usa **service account** (arquivo JSON), não os tokens OAuth2 salvos no banco:

```python
GOOGLE_CREDENTIALS_PATH = "/opt/conecta-pro/config/google_drive_credentials.json"

def check_status(self):
    if self._service:
        return self.verificar_conexao()
    connected = self._init_service()  # tenta carregar JSON do disco
    return {
        "credenciais_existem": os.path.exists(GOOGLE_CREDENTIALS_PATH),  # → False
        ...
    }
```

**O arquivo não existe:**
```
/opt/conecta-pro/config/
  smtp_config.json       ← existe
  google_drive_credentials.json  ← NÃO EXISTE
```

### Estado do banco (`gdrive_config`)

```
owner_email:   jordansjesus@gmail.com
is_connected:  TRUE
access_token:  ya29.a0Aa7MYiojW87C2... (truncado)
refresh_token: SIM (presente)
token_expiry:  2026-04-08 03:44:35   ← EXPIRADO (3 dias)
scopes:        ["https://www.googleapis.com/auth/drive"]
root_folder_id: 1XSNuCykj298Ac_ClGml3_rLnxIDOJORr
kits_folder_id: 1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck
```

**O banco TEM os tokens** — o service simplesmente não os usa no `check_status()`.

---

## Problema 3 — Erro "Scope has changed" no callback OAuth

### Log registrado
```
GDrive callback erro: Scope has changed from
  "https://www.googleapis.com/auth/drive.metadata.readonly
   https://www.googleapis.com/auth/drive.file"
to
  "https://www.googleapis.com/auth/drive
   https://www.googleapis.com/auth/userinfo.email
   https://www.googleapis.com/auth/userinfo.profile
   openid
   https://www.googleapis.com/auth/drive.metadata.readonly
   https://www.googleapis.com/auth/drive.file"
```

### Causa raiz
O Google retorna scopes **adicionais** (`userinfo.email`, `openid`, etc.) quando `include_granted_scopes=true`. A biblioteca `requests-oauthlib` rejeita se os scopes retornados não casam exatamente com os solicitados.

### O que está no código
```python
# gdrive_service.py linha 128 — ANTES do fetch_token
_os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
```

O `OAUTHLIB_RELAX_TOKEN_SCOPE=1` **está presente** mas o log ainda registra erro. Isso sugere que:
- O erro ocorreu numa versão anterior do código (antes de `OAUTHLIB_RELAX_TOKEN_SCOPE` ser adicionado), **ou**
- O `os.environ` não propaga para threads/processos do callback a tempo

---

## Fluxo OAuth2 GDrive (atual)

```
1. GET /api/v1/gdrive/autorizar
   → gera URL Google com scopes: drive.file + drive.metadata.readonly
   → state salvo temporariamente

2. Usuário autoriza no Google → redireciona para:
   GET /api/v1/gdrive/oauth/callback?code=XXX&state=YYY

3. gdrive_service.trocar_codigo_por_token(code)
   → OAUTHLIB_RELAX_TOKEN_SCOPE = "1"
   → flow.fetch_token(code=code)
   → salva tokens em gdrive_config no banco
   → redireciona para /modulos/gestao-pessoas/ged/configuracoes?gdrive=conectado

4. gdrive_service.check_status()
   → verifica /opt/conecta-pro/config/google_drive_credentials.json (não existe)
   → retorna conectado: false  ← BUG (ignora tokens do banco)
```

---

## Ações Necessárias (pendentes)

### Ação 1 — Re-autorizar (token expirado há 3 dias)
Acesse no browser e autorize novamente:
```
GET http://erp.conectamais.pro/api/v1/gdrive/autorizar
```
O `refresh_token` está presente — o sistema pode renovar automaticamente se o `check_status` for corrigido.

### Ação 2 — Corrigir `check_status()` para usar tokens OAuth2 do banco
O método deve verificar `gdrive_config.is_connected` **antes** de verificar o arquivo JSON:
```python
def check_status(self):
    # Prioridade: tokens OAuth2 já carregados em memória
    if self._service:
        return self.verificar_conexao()
    # Fallback 1: tokens no banco (OAuth2)
    # → consultar gdrive_config WHERE is_connected=TRUE
    # → chamar conectar_com_tokens(at, rt, exp)
    # Fallback 2: service account (arquivo JSON)
    connected = self._init_service()
    ...
```

### Ação 3 — Corrigir URL no frontend (`/ged/configuracoes` → `/ged/config/drive`)
O frontend provavelmente chama `/ged/configuracoes` — precisa chamar `/ged/config/drive`.

---

## URL OAuth2 Gerada (válida por ~10 min)

```
https://accounts.google.com/o/oauth2/auth
  ?client_id=576020339239-bs4amjo67m3v0j9gerqnrk6gpohvjqvd.apps.googleusercontent.com
  &redirect_uri=https://erp.conectamais.pro/api/v1/gdrive/oauth/callback
  &scope=https://www.googleapis.com/auth/drive.file
         https://www.googleapis.com/auth/drive.metadata.readonly
  &access_type=offline
  &include_granted_scopes=true
  &prompt=consent
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_GED_GDRIVE_DIAGNOSTICO_20260411.md ~/Downloads/
```
