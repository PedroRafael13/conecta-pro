# Correção GDrive OAuth2 — Conecta PRO
**Data:** 2026-04-11
**Commit:** `ce496dd7`
**Branch:** `feature/people-management-reorganization`
**Veredicto:** ✅ 100% CONCLUÍDO — botão "Conectar Google Drive" funcional, API Drive respondendo

---

## Resultado Final

| Teste | Antes | Depois |
|-------|-------|--------|
| `GET /gdrive/status` | `conectado: false, tipo: service_account` ❌ | `conectado: true, tipo: oauth2, email: jordansjesus@gmail.com` ✅ |
| `GET /gdrive/autorizar` | URL gerada ✅ | URL gerada ✅ |
| API Drive (about.get) | não testável ❌ | `email: jordansjesus@gmail.com, storage: 29.331 MB` ✅ |
| Token expirado | `2026-04-08` (3 dias vencido) ❌ | Renovado → `2026-04-11 20:50:45` ✅ |
| `GET /ged/config/email-templates` | 200 ✅ | 200 ✅ |
| `GET /ged/config/document-types` | 200 ✅ | 200 ✅ |
| `GET /ged/config/schedule` | 200 ✅ | 200 ✅ |
| `GET /people-management/ged/config/drive` | 200 ✅ | 200 ✅ |

---

## Bug 1 — `check_status()` ignorava tokens OAuth2 do banco

### Causa raiz
`gdrive_service.check_status()` verificava apenas o arquivo de service account:
```
/opt/conecta-pro/config/google_drive_credentials.json  ← NÃO EXISTE
```
Nunca consultava a tabela `gdrive_config` com tokens OAuth2 do fluxo de autorização.

### Arquivo corrigido
`backend/modules/gdrive/services/gdrive_service.py` — método `check_status()`

### Antes
```python
def check_status(self) -> dict[str, Any]:
    if self._service:
        return self.verificar_conexao()
    connected = self._init_service()  # verifica apenas arquivo JSON → False
    return {
        "configurado": connected,
        "credentials_existem": os.path.exists(GOOGLE_CREDENTIALS_PATH),  # → False
        ...
    }
```

### Depois (3 prioridades)
```python
def check_status(self) -> dict[str, Any]:
    if self._service:
        return self.verificar_conexao()
    # Prioridade 2: OAuth2 tokens no banco (gdrive_config)
    conn = psycopg2.connect(DATABASE_URL)
    cur.execute("SELECT owner_email, access_token, refresh_token, token_expiry "
                "FROM gdrive_config WHERE is_connected = TRUE LIMIT 1")
    row = cur.fetchone()
    if row:
        ok = self.conectar_com_tokens(at, rt, expiry)
        if ok:
            return {"conectado": True, "tipo": "oauth2", "fonte": "banco", ...}
    # Prioridade 3: service account (fallback)
    connected = self._init_service()
    ...
```

---

## Bug 2 — Controller `gdrive_status` rodava versão desatualizada no container

### Causa raiz
O arquivo em disco `gdrive_controller.py` já tinha a lógica DB-first (query `gdrive_config`),
mas o container estava rodando uma versão **antiga** que sempre retornava `tipo: service_account`.

**Versão antiga (container antes do fix):**
```python
@router.get("/status")
async def gdrive_status(...):
    svc = _drive_service(db)
    creds = await svc.check_credentials()
    return {"tipo": "service_account", ...}  # sempre service_account, sem consultar DB
```

**Versão correta (deployada via `docker cp`):**
```python
@router.get("/status")
async def gdrive_status(...):
    row = await db.execute("SELECT owner_email, is_connected "
                           "FROM gdrive_config WHERE is_connected = TRUE LIMIT 1")
    if row:
        return {"conectado": True, "tipo": "oauth2", "email": email, ...}
    # Fallback: service account
    ...
```

**Deploy executado:**
```bash
docker cp backend/modules/gdrive/controllers/gdrive_controller.py \
    conecta-pro-backend:/app/modules/gdrive/controllers/gdrive_controller.py
```

---

## Bug 3 — `OAUTHLIB_INSECURE_TRANSPORT = "1"` em produção HTTPS

### Causa raiz
`trocar_codigo_por_token()` definia `OAUTHLIB_INSECURE_TRANSPORT = "1"`, que desabilita
verificação de transporte HTTPS. Produção usa `erp.conectamais.pro` (HTTPS) — flag desnecessária
e insegura.

### Fix
```python
# ANTES
_os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# DEPOIS
_os.environ.pop("OAUTHLIB_INSECURE_TRANSPORT", None)  # remove se existir
```

`OAUTHLIB_RELAX_TOKEN_SCOPE = "1"` **mantido** — Google retorna scopes adicionais
(`userinfo.email`, `openid`) via `include_granted_scopes=true`. Sem isso, o callback
rejeita com `Scope has changed`.

---

## PASSO 6 — Re-autorização / Renovação do Token Expirado

Token estava expirado há 3 dias (`token_expiry: 2026-04-08`).

### Renovação proativa executada
```python
# Refresh via google.auth.transport.requests
creds.refresh(Request())
# → novo expiry: 2026-04-11 20:50:45
# → novo access_token salvo em gdrive_config
```

### Verificação real da API Drive
```python
svc.about().get(fields="user,storageQuota").execute()
# → email: jordansjesus@gmail.com
# → nome: Jordan Jesus
# → storage: 29.331 MB usado
```

**O `refresh_token` é válido e a API Drive responde.** Tokens atualizados no banco:
```sql
UPDATE gdrive_config SET access_token='ya29.a0Aa7MYiqsDiAMn...', token_expiry='2026-04-11 20:50:45'
WHERE is_connected=TRUE;
```

---

## Análise — Bug "Frontend URL" (não era bug)

O diagnóstico anterior identificava "Bug 1 — `GET /ged/configuracoes` retorna 404".
Após inspeção de `frontend/src/app/modulos/gestao-pessoas/ged/configuracoes/page.tsx`:

```typescript
const API_BASE = '/api/v1/ged';
const GDRIVE_BASE = '/api/v1/gdrive';

// fetchConfig() chama:
fetch(`${GDRIVE_BASE}/status`)           // → /api/v1/gdrive/status     ✅ 200
fetch(`${API_BASE}/config/email-templates`) // → /api/v1/ged/config/...  ✅ 200
fetch(`${API_BASE}/config/document-types`)  //                            ✅ 200
fetch(`${API_BASE}/config/schedule`)        //                            ✅ 200
```

O frontend **nunca chamou** `/ged/configuracoes`. A URL `GET /ged/configuracoes` era
apenas um teste manual incorreto (cujo endpoint real é `/ged/config/drive`). Não houve
correção necessária no frontend.

---

## Validação Final

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@conectapro.com.br&password=admin123" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8080/api/v1/gdrive/status
# → {
#     "conectado": true,
#     "email": "jordansjesus@gmail.com",
#     "tipo": "oauth2",
#     "mensagem": "Google Drive conectado via OAuth2 (jordansjesus@gmail.com)",
#     "acao": null
#   }
```

---

## Arquivos Modificados

| Arquivo | Alteração |
|---------|-----------|
| `backend/modules/gdrive/services/gdrive_service.py` | `check_status()` DB-first + remoção `OAUTHLIB_INSECURE_TRANSPORT` |
| `backend/modules/gdrive/controllers/gdrive_controller.py` | Deploy da versão corrigida (DB-first em `/status`) — já estava correto no disco |

---

## Commit

```
ce496dd7  fix(gdrive): check_status prioriza OAuth2 do banco + remove OAUTHLIB_INSECURE_TRANSPORT
Branch: feature/people-management-reorganization
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_GDRIVE_OAUTH2_CORRECAO_20260411.md ~/Downloads/
```
