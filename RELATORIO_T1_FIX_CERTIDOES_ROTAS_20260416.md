# T1 — Fix Rotas Certidões (405 → 200)
**Data:** 2026-04-16
**Branch:** feature/people-management-reorganization
**Commit:** 33c42b10 (push ✅)

---

## Problema

| Endpoint | Antes | Depois |
|----------|-------|--------|
| `POST /api/v1/ged/certidoes/sync` | 405 Method Not Allowed | 200 OK |
| `POST /api/v1/ged/certidoes/sync/{tipo}` | 404 (capturado por PUT) | 200 OK |
| `GET  /api/v1/ged/certidoes/tipos` | 405 Method Not Allowed | 200 OK |
| `PUT  /api/v1/ged/certidoes/{id}` | OK | OK (regressão: não) |

**Impacto corrigido:** 9 páginas frontend em `/modulos/fiscal/certidoes/` desbloqueadas.

---

## Root Cause

**Arquivo:** `backend/modules/ged/controllers/ged_certidoes_controller.py`

FastAPI resolve rotas por **ordem de declaração**. O controller definia:

```
linha 90:  GET  /certidoes
linha 124: POST /certidoes
linha 157: PUT  /certidoes/{certidao_id}   ← AQUI estava o problema
linha 190: POST /certidoes/sync            ← declarado DEPOIS do /{id}
linha 214: POST /certidoes/sync/{param}    ← declarado DEPOIS do /{id}
```

Quando o cliente fazia `POST /certidoes/sync`, FastAPI não encontrava
um handler POST para `/{certidao_id}` mas respondia **405** com `allow: PUT`
— porque o path pattern `/{certidao_id}` existia apenas com método PUT.

`GET /certidoes/tipos` também não existia como endpoint — só havia `PUT /{certidao_id}`,
resultando em 405 com `allow: PUT`.

---

## Fix Aplicado

**1. Reordenação:** rotas específicas movidas para ANTES de `/{certidao_id}`:

```
# ORDEM CORRETA (depois do fix)
GET  /certidoes           (lista)
POST /certidoes           (criar)
GET  /certidoes/tipos     ← NOVO + antes de /{id}
POST /certidoes/sync      ← movido antes de /{id}
POST /certidoes/sync/{p}  ← movido antes de /{id}
PUT  /certidoes/{id}      ← agora depois das rotas específicas
DELETE /certidoes/{id}
```

**2. Novo endpoint `GET /certidoes/tipos`:**

```python
@router.get("/certidoes/tipos")
async def listar_tipos_certidao(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    from modules.people_management.ged.tasks.cnd_sync_task import CERTIDAO_CONFIG
    tipos = [
        {"key": key, "document_type": cfg["document_type"],
         "name": cfg["name"], "issuing_body": cfg["issuing_body"]}
        for key, cfg in CERTIDAO_CONFIG.items()
    ]
    return {"tipos": tipos, "total": len(tipos)}
```

Retorna os 5 tipos de CND configurados:
`cnd_federal`, `cndt_trabalhista`, `crf_fgts`, `cnd_estadual`, `cnd_municipal`

---

## Nota sobre reload

`kill -HUP 1` **não é suficiente** para mudanças de rota — FastAPI registra
rotas apenas no startup. Foi necessário `docker restart conecta-pro-backend`
para que as rotas fossem re-registradas.

---

## Validação Final

| Check | Resultado |
|-------|-----------|
| `POST /certidoes/sync/cnd_federal` | ✅ 200 OK |
| `POST /certidoes/sync/cndt_trabalhista` | ✅ 200 OK |
| `POST /certidoes/sync/crf_fgts` | ✅ 200 OK |
| `POST /certidoes/sync/cnd_estadual` | ✅ 200 OK |
| `POST /certidoes/sync/cnd_municipal` | ✅ 200 OK |
| `GET /certidoes/tipos` | ✅ 200 OK (5 tipos retornados) |
| `PUT /certidoes/{id}` (regressão) | ✅ 404 (id inexistente — rota funcional) |
| `DELETE /certidoes/{id}` (regressão) | ✅ 404 (id inexistente — rota funcional) |
| `GET /certidoes/{id}` (não existe) | ✅ 405 (correto — endpoint por ID não implementado) |
| `OPTIONS /certidoes/1` | ⚠️ `allow: PUT` (Starlette quirk: handlers separados para PUT e DELETE no mesmo path pattern; DELETE funcional via HTTP 404 em ID inexistente) |
| MD5 container == MD5 disco | ✅ `d6f9e1209f0840b6c5004bbd6f49ea9e` |
| Rotas no app (docker exec inspect) | ✅ GET /certidoes, POST /certidoes, GET /tipos, POST /sync, POST /sync/{param}, PUT /{id}, DELETE /{id} |

---

## Deploy

| Etapa | Status |
|-------|--------|
| Reescrita do controller com ordem correta | ✅ |
| `docker cp` → container | ✅ |
| `docker restart conecta-pro-backend` | ✅ |
| `docker cp` pós-ruff-format | ✅ |
| `git commit 33c42b10` | ✅ |
| `git push` | ✅ |

```
╔══════════════════════════════════════════════════════════════════╗
║  T1 Fix Certidões Rotas ✅                                      ║
║  5/5 sync: 405 → 200 | /tipos: 405 → 200                       ║
║  Causa: ordem de declaração FastAPI — PUT/{id} antes do /sync   ║
║  9 páginas frontend de certidões desbloqueadas                  ║
╚══════════════════════════════════════════════════════════════════╝
```
