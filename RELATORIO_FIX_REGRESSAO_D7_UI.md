# Relatório — Fix Regressão D7 Pagamentos UI
**Data:** 2026-05-04
**Commits:** 88f85178 → final (auditoria round 2)
**Branch:** feature/people-management-reorganization

---

## 1. STEP 1 — Diagnóstico completo

**Sintoma:** Página `/modulos/financeiro/inter/pagamentos` exibia error boundary "Algo deu errado" após commits `7f34afaa`+`6ccdb1a2`+`7639bde5`.

### 1.1 — Estado do código
- 781 linhas | últimos 3 commits alteraram o arquivo

### 1.2 — Imports presentes
- `Wallet, TrendingDown, ShieldCheck, Lock` de `lucide-react` ✅
- `ReactNode` de `react` ✅

### 1.3 — Componentes UI
- `table.tsx` ✅ existe em `src/components/ui/`
- `card.tsx` ✅ existe em `src/components/ui/`
- `lucide-react` Wallet/Lock ✅ existe em `node_modules`

### 1.4 — TypeScript (npx tsc --noEmit)
Encontrou **2 erros** na página pagamentos:
1. `linha 488`: `atob(token.split(".")[1])` — `split()[1]` é `string | undefined`, `atob` exige `string` → **corrigido na auditoria**
2. (pré-existente, não relacionado ao fix)

### 1.5 — Build
Passou sem erros (Next.js não detecta runtime TDZ).

### 1.6 — Container logs (equivalente pm2 — container usa next-server standalone, sem PM2)
- `✓ Ready in Xms` em todos os restarts
- Apenas erros de `EACCES /app/.next/cache/images` (pré-existente, não relacionado)

### 1.7 — nginx error.log
Não existe no container frontend (Next.js standalone serve diretamente na porta 3000).

### 1.8 — Curl da página
HTTP 307 redirect para `/login` (comportamento correto — middleware de auth ativo).

---

## 2. STEP 2 — Causa Raiz

**DECISÃO:**
- **Erro no console:** `ReferenceError: Cannot access 'fetchAudit' before initialization`
- **Causa raiz:** JavaScript `const` temporal dead zone — `useEffect` dependency array referencia `fetchAudit` antes de sua declaração
- **Linha culpada:** Linha 526 (deps) + linha 528 (declaração tardia)

```
Linha 517-526:  useEffect(..., [tab, fetchPayments, fetchSaldo, fetchAudit])
                                                                ^^^^^^^^^^
                                                     avaliado aqui (TDZ ativo)
Linha 528:      const fetchAudit = useCallback(...)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        inicializado AQUI — tarde demais
```

O build passa porque TypeScript/webpack analisa o bundle compilado (onde hoisting ocorreu). O erro só aparece em runtime no browser.

---

## 3. STEP 3 — Diff do fix

**Arquivo:** `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx`

```diff
-  useEffect(() => {
-    ...
-  }, [tab, fetchPayments, fetchSaldo, fetchAudit]);  ← TDZ: fetchAudit não existe ainda

-  const fetchAudit = useCallback(...);               ← declarado DEPOIS

+  const fetchAudit = useCallback(...);               ← movido para ANTES

+  useEffect(() => {
+    ...
+  }, [tab, fetchPayments, fetchSaldo, fetchAudit]);  ← OK: fetchAudit já existe
```

**Fix adicional (auditoria):** `token.split(".")[1] ?? ""` — corrige TS2769 `string | undefined` → `string`.

**Regra derivada:** sempre declarar `useCallback`/`useMemo` ANTES do `useEffect` que os usa na dependency array.

---

## 4. BUILD_ID final

`conecta-pro-1777858786727`

---

## 5. Confirmação: funcionalidades mantidas

| Funcionalidade | Status |
|---|---|
| 3 cards (Saldo Inter / Consumido Hoje / Limite Restante) | ✅ Mantido |
| Tab "Audit Log" condicional (só Jordan) | ✅ Mantido |
| Lock icon + text-red-700 no tab | ✅ Mantido |
| refetchInterval 60s no saldo | ✅ Mantido |
| isLoading / isError no AuditLogTable | ✅ Mantido |
| Endpoint backend GET /payments/audit | ✅ Não tocado |
| Subtitle "Conta 370990072-2" Card 1 | ✅ Mantido |
| Subtitle "disponível pra hoje" Card 3 | ✅ Mantido |

---

## 6. STEP 3 — ls components/ui (verificação cenários)

```
alert-dialog.tsx  card.tsx  dialog.tsx  input.tsx  label.tsx
table-skeleton.tsx  table.tsx  ...  (30+ componentes)
```
`table.tsx` e `card.tsx` existem. Imports não eram o problema.

---

## 7. Container runtime (STEP 4 — next-server, sem PM2)

```
▲ Next.js 16.1.6
✓ Starting...
✓ Ready in 179ms
```
Nenhum erro de runtime pós-deploy.
