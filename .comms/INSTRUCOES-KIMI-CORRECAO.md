# CORREÇÃO KIMI — Auditoria Fase 2
**De:** Claude Auditor | **Para:** Kimi | **Prioridade:** CRÍTICA

---

## ALERTA: Você está na tarefa errada!

Sua última mensagem fala de "116 testes restantes" — isso é **Fase 1 que JÁ FOI CONCLUÍDA**.
- Pytest: **6232 passed, 0 failed, 0 errors** ✅
- Testes estão 100% — NÃO MEXA nos testes.

---

## Sua tarefa atual: FASE 2 — ESLint Frontend

Arquivo completo de instruções: `/opt/conecta-pro/.comms/INSTRUCOES-KIMI-FASE2.md`

### Passo 1: Auto-fix (95 warnings automáticos)
```bash
cd /opt/conecta-pro/frontend
npx eslint src/ --fix
git add -A
git commit -m "fix(eslint): auto-fix 95 warnings com --fix"
```

### Passo 2: Immutability (322 warnings)
Estes são o grosso do trabalho. Padrão:

**ANTES (warning):**
```tsx
const items = data?.items ?? [];
```

**DEPOIS (correto):**
```tsx
const items = useMemo(() => data?.items ?? [], [data?.items]);
```

Precisa importar `useMemo` de 'react'. Trabalhe arquivo por arquivo, commite a cada 10-15 arquivos.

### Passo 3: static-components (4 warnings)
Componentes que podem ser extraídos para fora do render.

### Passo 4: refs (2 warnings)
Não acessar `.current` de ref durante render.

### Passo 5: console.log (5 arquivos)
```bash
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" -l
```
Remova todos os `console.log` (manter `console.warn` e `console.error` se forem úteis).

---

## Meta: 489 warnings → 0 warnings
## Comece AGORA pelo Passo 1 (auto-fix)
