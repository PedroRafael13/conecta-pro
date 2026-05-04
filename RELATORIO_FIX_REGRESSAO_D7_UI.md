# Relatório — Fix Regressão D7 Pagamentos UI
**Data:** 2026-05-04
**Commit:** 88f85178
**Branch:** feature/people-management-reorganization

---

## 1. STEP 1 — Erro capturado

**Sintoma:** Página `/modulos/financeiro/inter/pagamentos` exibia error boundary "Algo deu errado" após commits `7f34afaa`+`6ccdb1a2`+`7639bde5`.

**Build:** Passava sem erros (Next.js compilou 0 erros).
**Backend:** 3/3 curl validações passando.
**SSR/HTML:** Renderizava loading state (sem error boundary no HTML inicial).
**Diagnóstico:** Erro ocorria no cliente, após hydration — ReferenceError de runtime.

---

## 2. STEP 2 — Causa Raiz

**`ReferenceError: Cannot access 'fetchAudit' before initialization`**

```
Linha 517-526:  useEffect(..., [tab, fetchPayments, fetchSaldo, fetchAudit])
                                                                ^^^^^^^^^^
                                                     referenciado aqui
Linha 528:      const fetchAudit = useCallback(...)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        declarado AQUI — depois do useEffect
```

Em JavaScript, `const` entra em **temporal dead zone (TDZ)** desde o início do bloco até a linha de declaração. A dependency array `[..., fetchAudit]` é avaliada **sincroniamente** durante o render, na linha do `useEffect` — antes de `fetchAudit` ser inicializado. Isso lança `ReferenceError` no cliente, que o error boundary captura e exibe "Algo deu errado".

O build passa porque TypeScript/webpack analisa o bundle final (onde hoisting já ocorreu), não a ordem de execução runtime do componente.

---

## 3. STEP 3 — Diff do fix

**Arquivo:** `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx`

```diff
-  useEffect(() => {
-    fetchSaldo();
-    ...
-    else if (tab === "audit") fetchAudit();
-    ...
-  }, [tab, fetchPayments, fetchSaldo, fetchAudit]);  ← fetchAudit não existe ainda
-
-  const fetchAudit = useCallback(async () => {       ← declarado DEPOIS
-    ...
-  }, []);

+  const fetchAudit = useCallback(async () => {       ← declarado ANTES
+    ...
+  }, []);
+
+  useEffect(() => {
+    fetchSaldo();
+    ...
+    else if (tab === "audit") fetchAudit();
+    ...
+  }, [tab, fetchPayments, fetchSaldo, fetchAudit]);  ← fetchAudit já existe
```

**Regra:** sempre declarar `useCallback`/`useMemo` ANTES do `useEffect` que os usa na dependency array.

---

## 4. BUILD_ID novo

`conecta-pro-1777858218457`

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
