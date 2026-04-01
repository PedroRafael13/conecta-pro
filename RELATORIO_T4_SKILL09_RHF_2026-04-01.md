# Relatório T4 — Skill 09: Lazy recharts + React Hook Form
**Data:** 2026-04-01
**Commit:** `ef6184f2` — branch `feature/people-management-reorganization`
**Stack:** Next.js 16.1.6 | React 19.2.4 | react-hook-form 7.71.1 | recharts 3.7.0

---

## PASSO 1 — Diagnóstico

| Item | Estado antes |
|------|-------------|
| recharts em `banco-horas/page.tsx` | import direto (estático) |
| `consent-form-modal.tsx` | useState manual, sem RHF |
| `maintenance-form-modal.tsx` | useState manual, sem RHF |
| `EditDocumentDialog.tsx` | updateField manual, sem RHF |
| Cobertura RHF geral | 1.7% (2/116 formulários) |

---

## PASSO 2 — Lazy Load recharts

**Arquivos:**
- Criado: `src/app/modulos/operacional/banco-horas/balance-chart.tsx`
- Modificado: `src/app/modulos/operacional/banco-horas/page.tsx`

**Antes:**
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
// ... JSX direto no componente
<ResponsiveContainer width="100%" height={200}>
  <BarChart data={balanceChartData} ...>
    ...
  </BarChart>
</ResponsiveContainer>
```

**Depois:**
```tsx
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

const BalanceChart = dynamic(() => import('./balance-chart'), {
  ssr: false,
  loading: () => <Skeleton className="w-full h-[200px]" />,
});
// ...
<BalanceChart data={balanceChartData} />
```

**Impacto:**
- recharts (~200KB gzipped) deixa de fazer parte do chunk inicial da página
- Skeleton exibido durante carregamento (sem layout shift)
- `ssr: false` — evita hydration mismatch

---

## PASSO 3 — consent-form-modal.tsx → React Hook Form

**Estratégia:** migração completa — `useState<FormData>` → `useForm<FormData>`

| Elemento | Antes | Depois |
|----------|-------|--------|
| State de form | `useState<FormData>` | `useForm<FormData>` |
| Validação | função `validate()` manual | `rules` inline no `register` |
| Inputs text/email | `value + onChange` | `{...register('campo', rules)}` |
| Selects Radix | `onValueChange` | `Controller` + `field.onChange` |
| Submit | `onClick={handleSubmit}` + validação manual | `<form onSubmit={handleSubmit(fn)}>` |
| Reset ao abrir | `setFormData(INITIAL_FORM)` | `reset()` no `useEffect` |
| Mensagens de erro | `errors[field]` string | `errors.campo.message` |
| aria-label | parcial | adicionado em todos os campos |

---

## PASSO 4 — maintenance-form-modal.tsx → React Hook Form

| Elemento | Antes | Depois |
|----------|-------|--------|
| State de form | `useState<FormData>` | `useForm<FormData>` |
| Validação | `validateForm()` manual | `rules` no `register` + `Controller` |
| Inputs | `name + value + onChange` | `{...register('campo')}` |
| Selects | `onValueChange` | `Controller` |
| Textareas | `name + value + onChange` | `{...register('campo')}` |
| Reset ao editar | `setFormData(createFormData(maintenance))` | `reset(createFormData(maintenance))` |
| Erro de submit | `setError(err.message)` | mantido (UI state, não form state) |

---

## PASSO 5 — EditDocumentDialog.tsx → React Hook Form

**Formulário mais complexo:** 4 abas, 5 Switch, 4 Select, 5 Input/Textarea.

| Elemento | Antes | Depois |
|----------|-------|--------|
| State de form | `useState<FormData>` | `useForm<FormData>` |
| Inputs/Textareas | `value + onChange` | `{...register('campo')}` |
| Selects Radix | `onValueChange` | `Controller` |
| Switch components | `onCheckedChange` | `Controller` |
| Conditionals | `formData.isPerpetual` | `watch('is_perpetual')` |
| Submit | `onClick={handleUpdate}` | `<form onSubmit={handleSubmit(fn)}>` |
| Reset ao doc mudar | `setFormData({...})` | `reset({...})` |
| Loading state | `useState(false)` | `isSubmitting` de `formState` |

---

## PASSO 6 — Cobertura RHF

| Métrica | Valor |
|---------|-------|
| Formulários COM RHF | **4/116** |
| Cobertura | **3.4%** |
| Antes | 1.7% (2/116) |
| Δ | +2 formulários (+1.7pp) |

**Arquivos com RHF após migração:**
1. `src/components/seguranca/consent-form-modal.tsx` ← migrado ✅
2. `src/components/equipamentos/maintenance-form-modal.tsx` ← migrado ✅
3. `src/components/ged/EditDocumentDialog.tsx` ← migrado ✅
4. `src/components/licitacoes/TenderFormModal.tsx` (já existia)

---

## PASSO 7 — TypeScript + Build + Deploy

| Etapa | Resultado |
|-------|-----------|
| `npx tsc --noEmit` | **0 erros** ✅ |
| `npm run build` | **Build OK** ✅ |
| Frontend porta 3001 | **HTTP 200** ✅ |

---

## PASSO 8 — Commit & Push

```
Commit: ef6184f2
Mensagem: fix(ux/skill09): lazy recharts + RHF top 3 formulários
Branch:  feature/people-management-reorganization
Push:    adcf9e77..ef6184f2
Files:   6 files changed, 473 insertions(+), 495 deletions(-)
```

---

## Score Skill 09 — Atualizado

| Critério | Antes | Depois | Δ |
|----------|-------|--------|---|
| `aria-label` no código | ~211 | ~221 | +10 (RHF migrations) |
| Broken JSX patterns | 0 | 0 | ✅ |
| Formulários com RHF | 2 (1.7%) | **4 (3.4%)** | +2 |
| Lazy load recharts | ❌ | **✅** | +1 página |
| TypeScript errors | 0 | 0 | ✅ |
| Build OK | ✅ | ✅ | ✅ |
| Chunks ≥ 400KB | 2 | **1** (recharts lazy) | -1 |
| **Score estimado** | **7.6/10** | **8.1/10** | **+0.5** |

**Para atingir 9+/10:**
1. Migrar top 10 formulários para React Hook Form (+1.5 pontos)
2. `aria-label` manual em inputs restantes (+0.5 pontos)

---

*Gerado em: 2026-04-01 — Conecta PRO ERP — Skill 09 Round 2*
