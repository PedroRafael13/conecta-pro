# CORREÇÃO OPUS — Auditoria Fase 2
**De:** Claude Auditor | **Para:** Opus Executor | **Prioridade:** ALTA

---

## Problema 1: Bug em useNotificationWebSocket.ts

O `useEffect` que seta `connectRef.current = connect` está na **linha 103**, mas `const connect = useCallback(...)` só é declarado na **linha 110**.

**ESLint warning:** `Cannot access variable before it is declared`

**Fix:** Mova este bloco:
```ts
useEffect(() => {
    connectRef.current = connect;
}, [connect]);
```
Para **DEPOIS** de `const connect = useCallback(() => { ... }, [...]);` (depois da linha 173).

---

## Problema 2: Commit pendente

Você tem 8 arquivos modificados sem commit:

**Backend (3 arquivos):**
- `efd_reinf_service.py` — fix Decimal(str(None))
- `unified_dashboard.py` — fix metadata → task_metadata
- `test_gov_connections.py` — fix Bandit B501

**Frontend (5 arquivos):**
- `useLocalStorage.ts` — fix set-state-in-effect
- `useKeyboardShortcuts.ts` — fix refs
- `checkin/page.tsx` — fix immutability
- `kits/page.tsx` — fix immutability
- `useNotificationWebSocket.ts` — fix exhaustive-deps (CORRIGIR BUG PRIMEIRO)

**Commitar separado:**
```bash
# Backend
git add backend/modules/government_integrations/services/efd_reinf_service.py \
       backend/modules/notifications/anti_procrastination/dashboard/unified_dashboard.py \
       backend/scripts/test_gov_connections.py
git commit -m "fix(backend): corrige 2 bugs produção + 1 Bandit B501"

# Frontend (após corrigir o bug)
git add frontend/src/
git commit -m "fix(eslint): corrige 5 warnings (set-state-in-effect, exhaustive-deps, refs, immutability)"
```

---

## Próximas tarefas após commit:
1. **set-state-in-effect** — 41 warnings restantes (padrão: setState dentro de useEffect → mover para useState lazy init ou useCallback)
2. **exhaustive-deps** — 30 warnings
3. **no-anonymous-default-export** — 15 warnings
