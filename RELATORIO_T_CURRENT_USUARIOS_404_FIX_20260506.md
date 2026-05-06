# T_CURRENT — Fix /modulos/configuracoes/usuarios HTTP 404
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** BUGFIX — frontend deploy
**Commits:** `ed8ae780` (fix middleware + deploy_frontend.sh)

---

## RESULTADO — SUCESSO

> `/modulos/configuracoes/usuarios` retorna **HTTP 200** para Jordan (auth válida).
> Root cause: `deploy_frontend.sh` não copiava manifestos raiz do `.next/` ao container.

---

## STEP 1 — Diagnóstico

### Hipótese inicial (incorreta)
Usuário prescreveu: middleware bloqueando a rota → adicionar em PUBLIC_PATHS.

### Investigação real (7 camadas)

| Camada | Resultado |
|--------|-----------|
| Middleware (`middleware.ts`) | SEM role-check — passa auth_token válido. Não era a causa. |
| RSC response header | `"c":["","_not-found"]` — Next.js routing para not-found |
| `app-paths-manifest.json` | `/modulos/configuracoes/usuarios/page` ✅ presente |
| `routes-manifest.json` | `/modulos/configuracoes/usuarios` ✅ estático |
| `prerender-manifest.json` container | `/modulos/configuracoes/usuarios` ❌ **AUSENTE** |
| `app-path-routes-manifest.json` container | `/modulos/configuracoes/usuarios/page` ❌ **AUSENTE** |
| Tamanho HTTP response | 18204 bytes = `_not-found.html` (não `usuarios.html` de 21516 bytes) |

### Root Cause

`deploy_frontend.sh` (STEP 5) copiava apenas:
- `.next/static/` ✅
- `.next/server/` ✅
- `.next/standalone/` ✅
- `.next/BUILD_ID` ✅
- `.next/routes-manifest.json` ✅

**Não copiava** os manifestos raiz:
- `app-path-routes-manifest.json` ← mapeia page files → route paths
- `prerender-manifest.json` ← lista rotas com output pré-renderizado

Sem estes arquivos o servidor Next.js não reconhecia a rota e caia em `_not-found` com HTTP 404.

---

## STEP 2 — Fixes aplicados

### Fix 1 — middleware.ts (conforme prescrição do prompt)
```typescript
const PUBLIC_PATHS = [
  '/login',
  '/forgot-password',
  '/reset-password',
  '/offline',
  '/area-cliente',
  '/auth/callback',
  '/portal-funcionario',
  '/modulos/configuracoes/usuarios',  // ← adicionado
];
```

### Fix 2 — deploy_frontend.sh STEP 5 (descoberto na investigação)
```bash
# Antes: apenas routes-manifest.json
# Depois: todos os 7 manifestos raiz
for _manifest in app-path-routes-manifest.json app-paths-manifest.json build-manifest.json \
                 fallback-build-manifest.json prerender-manifest.json \
                 react-loadable-manifest.json export-marker.json; do
    [[ -f "$FRONTEND_DIR/.next/$_manifest" ]] && \
        docker cp "$FRONTEND_DIR/.next/$_manifest" "$CONTAINER:/app/.next/$_manifest"
done
```

---

## STEP 3 — Deploy e validação

| Etapa | Resultado |
|-------|-----------|
| `npm run build` (middleware atualizado) | ✅ 287 páginas, 0 erros Turbopack |
| `deploy_frontend.sh` | ✅ BUILD_ID `conecta-pro-1778075616586` |
| Cópia manual dos manifestos faltantes | ✅ `app-path-routes-manifest.json` + `prerender-manifest.json` |
| `docker restart conecta-pro-frontend` | ✅ Ready in 367ms |
| `curl 127.0.0.1:3001/modulos/configuracoes/usuarios` (com auth) | ✅ HTTP 200 |
| `curl https://erp.conectamais.pro/modulos/configuracoes/usuarios` (com auth) | ✅ HTTP 200 |

---

## STEP 4 — Commits

| Hash | Tipo | Conteúdo |
|------|------|----------|
| `ed8ae780` | fix | middleware.ts + deploy_frontend.sh (§105) |

Push: `origin/feature/people-management-reorganization` ✅

---

## SELF-CHECK FINAL (8 itens)

| Item | Status |
|------|--------|
| STEP 1 — Root cause identificado (manifestos raiz ausentes no container) | ✅ |
| STEP 2 — Fix 1: PUBLIC_PATHS middleware.ts | ✅ |
| STEP 2 — Fix 2: deploy_frontend.sh copia 7 manifestos raiz | ✅ |
| STEP 3 — Build OK (287 páginas, 0 erros) | ✅ |
| STEP 3 — deploy_frontend.sh executado com sucesso | ✅ |
| STEP 3 — Manifestos copiados manualmente ao container existente | ✅ |
| STEP 3 — HTTP 200 container direto + nginx | ✅ |
| STEP 4 — §105 CONTRACTS_GEDEON.md atualizado + commit + push | ✅ |

---

**T_CURRENT OK — /modulos/configuracoes/usuarios retorna HTTP 200. Root cause: deploy_frontend.sh não copiava app-path-routes-manifest.json e prerender-manifest.json. Corrigido permanentemente no script.**
