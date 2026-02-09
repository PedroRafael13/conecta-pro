# 📊 RELATÓRIO DE ANÁLISE DE BUNDLE FRONTEND

**Projeto:** Conecta PRO (Next.js 16)
**Diretório:** `/opt/conecta-pro/frontend/`
**Data:** 2026-02-05

---

## ✅ Resumo Executivo

| Métrica | Valor Atual | Meta | Gap |
|---------|-------------|------|-----|
| Bundle `.next` | 439MB | < 300MB | +139MB ⚠️ |
| Maior chunk JS | ~279KB | < 200KB | +79KB |
| Dependências pesadas | 3 | 0 | 3 |
| Code splitting | Parcial | Completo | Incompleto |

---

## 🔴 Dependências Pesadas Encontradas

### 1. `xlsx` - 7.4MB ⚠️ ALTA

**Local:** `src/utils/export.ts:6`

**Problema:**
```typescript
import * as XLSX from 'xlsx'  // Import síncrono no bundle
```

**Impacto:** 7.4MB carregados no bundle inicial, mesmo quando usuário não exporta Excel.

**Solução:**
```typescript
// src/utils/export.ts
export async function exportToExcel(data: any[], filename: string) {
  const XLSX = await import('xlsx');  // Dynamic import
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(data);
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  XLSX.writeFile(wb, `${filename}.xlsx`);
}
```

**Economia:** ~7MB do bundle inicial

---

### 2. `shepherd.js` - 2.8MB 🟡 MÉDIA

**Locais:**
- `src/features/onboarding/hooks/useTour.ts:2`
- `src/features/onboarding/tours/operacionalTour.ts:1`

**Problema:**
```typescript
import Shepherd from 'shepherd.js'  // Import síncrono
```

**Impacto:** 2.8MB carregados para tour que nem todo usuário usa.

**Solução:**
```typescript
// src/features/onboarding/hooks/useTour.ts
import { useEffect, useState, useCallback } from 'react';

export function useTour(tourId: string) {
  const [Shepherd, setShepherd] = useState<typeof import('shepherd.js') | null>(null);
  const [tour, setTour] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;

    import('shepherd.js').then((mod) => {
      if (isMounted) {
        setShepherd(mod.default);
      }
    });

    return () => { isMounted = false; };
  }, []);

  const startTour = useCallback(() => {
    if (!Shepherd) return;

    const tourInstance = new Shepherd.Tour({
      defaultStepOptions: {
        cancelIcon: { enabled: true },
      },
    });

    // ... configuração do tour

    tourInstance.start();
    setTour(tourInstance);
  }, [Shepherd]);

  return { startTour, tour, isReady: !!Shepherd };
}
```

**Economia:** ~2.8MB do bundle inicial

---

### 3. `recharts` - 13MB 🟡 MÉDIA

**Local:** `src/app/modulos/analytics/page.tsx:23`

**Problema:**
```typescript
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, Legend
} from 'recharts';
```

**Impacto:** 13MB carregados na página analytics, mesmo quando componentes não são usados.

**Solução (Seguir padrão openclaw):**
```typescript
// src/app/modulos/analytics/page.tsx
import dynamic from 'next/dynamic';

const BarChart = dynamic(
  () => import('recharts').then((mod) => ({ default: mod.BarChart })),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const Bar = dynamic(
  () => import('recharts').then((mod) => ({ default: mod.Bar })),
  { ssr: false }
);

const XAxis = dynamic(
  () => import('recharts').then((mod) => ({ default: mod.XAxis })),
  { ssr: false }
);

// ... outros componentes

// Componente skeleton para loading
function ChartSkeleton() {
  return (
    <div className="h-[300px] w-full animate-pulse bg-gray-100 rounded-lg flex items-center justify-center">
      <span className="text-gray-400">Carregando gráfico...</span>
    </div>
  );
}
```

**Referência:** `src/app/modulos/openclaw/page.tsx` já implementa este padrão.

**Economia:** ~13MB na página analytics (carregado sob demanda)

---

## 🟢 Code Splitting - Implementações Corretas

### ✅ Já Implementados Corretamente:

1. **`src/components/ui/sparkline.tsx`**
   ```typescript
   import dynamic from 'next/dynamic';

   const LineChart = dynamic(
     () => import('recharts').then((mod) => ({ default: mod.LineChart })),
     { ssr: false }
   );
   ```

2. **`src/app/modulos/openclaw/page.tsx`**
   - Lazy load por componente do recharts
   - Padrão exemplar para replicar

3. **`src/components/lazy/LazyDialog.tsx`**
   - Dialogs lazy-loaded com loading state

4. **`src/components/lazy/LazyDropdown.tsx`**
   - Dropdowns lazy-loaded

5. **`src/components/BartoloClientWrapper.tsx`**
   - BartoloChat lazy-loaded

6. **`src/utils/export.ts` (função PDF)**
   ```typescript
   export async function exportToPDF(...) {
     const jsPDF = (await import('jspdf')).default;
     const autoTable = (await import('jspdf-autotable')).default;
     // ...
   }
   ```

---

## 🟡 Imports Problemáticos

| Arquivo | Linha | Problema | Correção |
|---------|-------|----------|----------|
| `src/app/modulos/analytics/page.tsx` | 23 | Import completo recharts | Dynamic import |
| `src/utils/export.ts` | 6 | `import * as XLSX from 'xlsx'` | Dynamic import |
| `src/features/onboarding/hooks/useTour.ts` | 2 | Import síncrono shepherd | Dynamic import |
| `src/features/onboarding/tours/operacionalTour.ts` | 1 | Import síncrono shepherd | Dynamic import |

---

## 📦 Configuração do next.config.ts

### ✅ Configurações Positivas:

```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      'date-fns',
      'recharts',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
    ],
  },
  // ...
};
```

### ⚠️ Configurações Comentadas:

```typescript
// webpack splitChunks configurado mas comentado
// Se migrar de Turbopack para Webpack, reativar:
/*
webpack: (config, { isServer }) => {
  if (!isServer) {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    };
  }
  return config;
},
*/
```

---

## 💡 Oportunidades Adicionais

### 1. Analisar bundle com @next/bundle-analyzer

```bash
cd /opt/conecta-pro/frontend
npm install --save-dev @next/bundle-analyzer

# Adicionar ao next.config.ts
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);

# Executar
ANALYZE=true npm run build
```

### 2. Tree shaking de bibliotecas grandes

**date-fns:** Já configurado em `optimizePackageImports` ✅

**lucide-react:** Já configurado em `optimizePackageImports` ✅

**lodash (se usado):**
```typescript
// Errado: Importa tudo
import _ from 'lodash';

// Correto: Importa apenas o necessário
import debounce from 'lodash/debounce';
import throttle from 'lodash/throttle';

// Ou use lodash-es para tree shaking
import { debounce, throttle } from 'lodash-es';
```

---

## 🎯 Plano de Ação

### Prioridade 1: Alta (Esta semana)

- [ ] **1. Lazy load XLSX** (`src/utils/export.ts`)
  - Tempo estimado: 30 minutos
  - Economia: ~7MB

- [ ] **2. Lazy load shepherd.js** (`src/features/onboarding/hooks/useTour.ts`)
  - Tempo estimado: 45 minutos
  - Economia: ~2.8MB

### Prioridade 2: Média (Próxima semana)

- [ ] **3. Otimizar recharts em analytics** (`src/app/modulos/analytics/page.tsx`)
  - Tempo estimado: 1 hora
  - Economia: ~13MB (na página)

- [ ] **4. Configurar bundle analyzer**
  - Tempo estimado: 30 minutos
  - Identificar outras oportunidades

### Prioridade 3: Baixa (Mês 2)

- [ ] **5. Revisar todas as páginas de módulos**
  - Identificar outros imports pesados

- [ ] **6. Considerar lazy load de módulos inteiros**
  - Módulos administrativos raramente usados

---

## 📊 Resultado Esperado

| Otimização | Economia | Bundle Final Estimado |
|------------|----------|----------------------|
| Atual | - | 439MB |
| Lazy XLSX | -7MB | 432MB |
| Lazy shepherd | -2.8MB | 429MB |
| Recharts analytics | -13MB (página) | 429MB (inicial) |
| **Total** | **-9.8MB inicial** | **~429MB** |

---

## ✅ Checklist de Validação

- [ ] Executar `npm run build` sem erros
- [ ] Verificar `.next/static/chunks` para tamanho dos chunks
- [ ] Testar exportação XLSX funciona
- [ ] Testar tour/onboarding funciona
- [ ] Testar gráficos em analytics funcionam
- [ ] Executar Lighthouse para medir melhoria

---

**Relatório gerado:** 2026-02-05
**Status:** Aguardando implementação
