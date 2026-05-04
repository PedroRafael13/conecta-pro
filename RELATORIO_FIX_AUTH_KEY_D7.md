# Relatório — Fix Auth Key D7 Pagamentos Inter
**Data:** 2026-05-04
**Commit:** a05c70d5
**Branch:** feature/people-management-reorganization
**CONTRACTS_GEDEON:** §53

---

## 1. Sintoma

Página `/modulos/financeiro/inter/pagamentos` renderizava sem erros (TDZ fix já aplicado),
mas:
- 3 cards de saldo exibiam `—` (dados não carregados)
- Aba "Audit Log" ausente mesmo logado como Jordan

---

## 2. Investigação

### 2.1 — Esquema de auth client-side

| Chave | Onde fica | O que guarda |
|-------|-----------|--------------|
| `access_token` | `localStorage` | JWT de sessão (lido por `api.ts` interceptor) |
| `refresh_token` | `localStorage` | Token de renovação |
| `auth_token` | Cookie (`document.cookie`) | Cópia do JWT para Next.js middleware SSR (redirect /login) |

`api.ts` (lib/api.ts linha 28): `localStorage.getItem('access_token')` — chave CORRETA.

### 2.2 — Bug em page.tsx

`apiFetch` local (linha 37) e `isJordan` useEffect (linha 486) liam `"auth_token"`:
```typescript
const token = localStorage.getItem("auth_token") || "";  // ← ERRADO: cookie key
```

`localStorage.getItem("auth_token")` retorna `null` → token vazio → headers `Authorization: Bearer ` → 401.

`isJordan` decodificava token vazio → `sub` inválido → `false` → aba Audit Log ausente.

---

## 3. Fix

**Arquivo:** `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx`

```diff
- const token = localStorage.getItem("auth_token") || "";   // linha 37
+ const token = localStorage.getItem("access_token") || "";

- const token = localStorage.getItem("auth_token") || "";   // linha 486 (isJordan)
+ const token = localStorage.getItem("access_token") || "";
```

---

## 4. Build e Deploy

```
NODE_OPTIONS=--max-old-space-size=4096 npm run build
docker cp .next/standalone/. conecta-pro-frontend:/app/
docker cp .next/static/. /opt/conecta-pro/frontend/.next/static/
docker restart conecta-pro-frontend
```

**Build ID:** `conecta-pro-1777859686351`

---

## 5. Validações

| Item | Status |
|------|--------|
| Cards exibem valores reais (pós auth fix) | ✅ |
| Aba "Audit Log" visível para Jordan | ✅ |
| Aba "Audit Log" ausente para não-Jordan | ✅ |
| `localStorage.getItem("access_token")` retorna JWT válido | ✅ |

---

## 6. Regra derivada

> `page.tsx` com `apiFetch` local deve sempre ler `localStorage.getItem("access_token")`,
> nunca `"auth_token"` (que é cookie SSR exclusivo do Next.js middleware).
