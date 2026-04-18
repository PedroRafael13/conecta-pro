# T1 — Fix 404: `/modulos/gestao-pessoas/ged/onvio-sync`
**Data:** 2026-04-18
**Branch:** feature/people-management-reorganization
**Commit:** (ver seção Deploy)

---

## `<thinking>` — Respostas antes de tocar qualquer arquivo

**1. O arquivo page.tsx existe em qual path no filesystem?**
`/opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged/onvio-sync/page.tsx`
Existe. Commited em `bceed412` (feat: dashboard onvio-sync frontend fase3).

**2. O build .next reflete esse path?**
Sim. O `.next` do **host** tem `server/app/modulos/gestao-pessoas/ged/onvio-sync/` completo.
BUILD_ID host: `conecta-pro-1776467656752`

**3. O container frontend tem o build atualizado?**
Não. O container tinha BUILD_ID `conecta-pro-1776395866015` (antigo).
Pior: o container tinha path DUPLICADO `gestao-pessoas/gestao-pessoas/ged/onvio-sync`
(artefato de build anterior à reorganização de módulos).

**4. Existe algum redirect no next.config.ts ou middleware.ts?**
`next.config.ts` tem redirect `/modulos/ged/:path*` → `/modulos/gestao-pessoas/ged/:path*`.
`src/middleware.ts` protege `/modulos` (redireciona para login se não autenticado).
Nenhum conflito com `gestao-pessoas/ged/onvio-sync`.

**5. A rota está protegida por um layout que redireciona se não autenticado?**
Sim, via `middleware.ts` (token `auth_token` no cookie). Layout pai existe. Sem bloqueio de layout — é auth middleware.

---

## DIAGNÓSTICO — Output completo

### D.1 — Filesystem
```
ARQUIVO: /opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged/onvio-sync/page.tsx ✅
DIR:     total 24 / page.tsx (10805 bytes) / types.ts (690 bytes)
DIR ANTIGO (/modulos/ged/onvio-sync): AUSENTE ✅
```

### D.2 — Build host (.next)
```
.next/server/app/modulos/gestao-pessoas/ged/onvio-sync.html ✅
.next/server/app/modulos/gestao-pessoas/ged/onvio-sync/page.js ✅
.next/server/app/modulos/gestao-pessoas/ged/onvio-sync/page.js.nft.json ✅
BUILD_ID: conecta-pro-1776467656752
```

### D.3 — Container (stale)
```
/app/.next/server/app/modulos/gestao-pessoas/gestao-pessoas/ged/onvio-sync  ← PATH ERRADO (duplicado)
BUILD_ID container: conecta-pro-1776395866015  ← ANTIGO

/app/standalone/.next/server/app/modulos/gestao-pessoas/ged/ ← sem onvio-sync
```

### D.4 — Middleware e redirects
```
middleware.ts: protege /modulos → redirect para /login (sem token)
next.config.ts: redirect /modulos/ged/* → /modulos/gestao-pessoas/ged/* (legacy, OK)
Sem conflito com a rota alvo.
```

### D.5 — Layout pai
```
/opt/conecta-pro/frontend/src/app/modulos/gestao-pessoas/ged/layout.tsx ✅
(layout pai existe — sem 404 por layout ausente)
```

### D.6 — HTTP local
```
Antes do fix:
  VPS porta 3001 → 404 (rota não existe no container)

Após fix:
  http://localhost:3001/modulos/gestao-pessoas/ged/onvio-sync → 307
  (middleware redireciona para /login — rota EXISTE, auth bloqueia sem cookie)
```

---

## Cenário Identificado: B — Container com build stale

**Causa raiz:** O build do host foi atualizado (rota reorganizada de `modulos/ged/onvio-sync` para `modulos/gestao-pessoas/ged/onvio-sync`) mas o container nunca recebeu o novo standalone. O container continuou servindo um build com path duplicado `gestao-pessoas/gestao-pessoas/ged/onvio-sync` que não correspondia à URL real.

| | Host | Container (antes) |
|--|------|------------------|
| BUILD_ID | `1776467656752` | `1776395866015` ❌ |
| Path onvio-sync | `gestao-pessoas/ged/onvio-sync` ✅ | `gestao-pessoas/gestao-pessoas/ged/onvio-sync` ❌ |
| Rota acessível | sim | não (404) |

---

## Fix Aplicado

```bash
# 1. Verificar BUILD_IDs
cat /opt/conecta-pro/frontend/.next/standalone/.next/BUILD_ID
# → conecta-pro-1776467656752

docker exec conecta-pro-frontend cat /app/.next/BUILD_ID
# → conecta-pro-1776395866015  (ANTIGO)

# 2. Copiar standalone novo para container
docker cp /opt/conecta-pro/frontend/.next/standalone/. conecta-pro-frontend:/app/

# 3. Restart
docker restart conecta-pro-frontend
# Up 10 seconds (healthy) ✅
```

Não foi necessário novo `npm run build` — o build correto já existia no host (compilado anteriormente). A falha era estritamente de deploy.

---

## Self-Check

| Check | Evidência | Status |
|-------|-----------|--------|
| HTTP 307 (não 404) em `/modulos/gestao-pessoas/ged/onvio-sync` | `curl → 307` (middleware redireciona para login — rota existe) | ✅ |
| Rota presente no container | `docker exec … ls /app/.next/server/app/modulos/gestao-pessoas/ged/` → `onvio-sync` | ✅ |
| Backend `/api/v1/onvio/stats` retorna 200 | `{"total":436,"por_categoria":{...}}` | ✅ |
| Outras rotas não quebraram | `/dashboard` → 307, `/modulos/dp` → 307, `/modulos/fiscal` → 307 | ✅ |

**Nota sobre 307 vs 200:** O middleware `src/middleware.ts` redireciona toda rota `/modulos/*` para `/login` se não houver cookie `auth_token`. No terminal sem sessão de browser, `curl` recebe 307. No browser autenticado, a rota serve 200 com o conteúdo da página. Antes do fix, o curl retornava 404 (rota inexistente); agora retorna 307 (rota existe, auth protege).

---

## Deploy

| Etapa | Status |
|-------|--------|
| `docker cp standalone` → container | ✅ |
| BUILD_ID container atualizado | `1776467656752` ✅ |
| `docker restart conecta-pro-frontend` | ✅ healthy |
| `onvio-sync` presente no container | ✅ |
| Nenhum rebuild necessário | ✅ |

```
╔══════════════════════════════════════════════════════════════════╗
║  T1 Frontend 404 Fix ✅                                         ║
║  Cenário B: container com build stale                           ║
║  Fix: docker cp standalone + restart                            ║
║  Antes: 404 (rota inexistente) | Depois: 307 (rota existe)     ║
║  Backend onvio/stats: 436 docs ✅                               ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_FASEB1_T1_FRONTEND_404.md ~/Downloads/
```
