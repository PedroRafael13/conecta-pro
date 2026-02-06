# Auditoria de Performance - Conecta Plus Frontend

**Data:** 2026-02-02
**Versão:** Next.js 16 + React 19
**Ambiente:** Production Build Analysis

---

## 1. Resumo Executivo

### Estado Atual
- **Build Size Total:** 173MB
- **Bundle JS (Chunks):** 8.1MB
- **Maior Chunk Individual:** 712KB
- **Lazy Loading:** ❌ Não implementado
- **Tree Shaking:** ⚠️ Parcial (problemas com libs pesadas)

### Principais Problemas
1. **CRÍTICO:** Zero lazy loading em páginas e componentes
2. **ALTO:** 200+ imports de lucide-react (bundle completo incluído)
3. **ALTO:** jsPDF carregado globalmente (usado em 1 arquivo)
4. **MÉDIO:** Recharts incluído em todas as páginas (usado em 3)
5. **BAIXO:** node_modules de 173MB (aceitável para dev, verificar prod)

### Ganho Esperado com Otimizações
- **Redução de Bundle:** ~40-60% (3.2MB - 4.8MB)
- **First Load JS:** -2.5MB a -4MB
- **Time to Interactive:** -30-50%

---

## 2. Métricas Atuais

### Build Artifacts
```
Build Size Analysis:
├── Total Project Size: 173MB
├── JS Chunks: 8.1MB
├── Largest Chunk: 712KB
└── Pages: ~50+ (sem lazy loading)
```

### Dependências de Produção (27 deps - ✅ enxuto)
```json
{
  "@radix-ui/*": "várias (UI primitives)",
  "recharts": "charts library",
  "lucide-react": "icon library",
  "jspdf": "PDF generation",
  "date-fns": "date utilities",
  "react-hook-form": "form handling",
  "zod": "validation"
}
```

### Distribuição de Peso em node_modules
```
60MB  lucide-react      (200+ imports sem tree-shaking)
60MB  date-fns          (3 imports named - ✅ otimizado)
29MB  jspdf             (1 import - carregado globalmente ❌)
26MB  lighthouse        (devDependency - OK)
48MB  chromium-bidi     (devDependency - OK)
      + puppeteer
```

### Uso de Bibliotecas Pesadas

#### jsPDF (29MB)
- **Imports:** 1 arquivo
- **Local:** `src/utils/export.ts`
- **Problema:** Incluído no bundle principal
- **Uso Real:** Só em funções de export específicas

#### Recharts (~500KB minified)
- **Imports:** 3 arquivos
  - `src/components/sparkline.tsx`
  - `src/app/analytics/page.tsx`
  - `src/app/openclaw/page.tsx`
- **Problema:** Carregado em todas as páginas
- **Uso Real:** Só em páginas específicas de analytics

#### Lucide React (~2MB bundle completo)
- **Imports:** 200+ ícones diferentes
- **Formato:** `import { Icon1, Icon2, ... } from 'lucide-react'`
- **Problema:** Sem tree-shaking efetivo, bundle completo incluído
- **Solução:** Imports individuais

---

## 3. Problemas Identificados

### 🔴 PRIORIDADE CRÍTICA

#### P1: Zero Lazy Loading Implementado
**Impacto:** First Load JS de ~8MB em TODAS as páginas

**Páginas Afetadas:**
- Dashboard, Analytics, Equipamentos
- Financeiro (clientes, contas-pagar, contas-receber, estoque)
- Operacional (turnos, diaristas, relatórios)
- Integrações (API keys, conectores)
- CRM (leads)
- Segurança (auditoria, consentimento)
- Configurações (feature-flags, tenants)

**Código Atual:**
```typescript
// page.tsx - TODAS as páginas
import ComponentePesado from '@/components/ComponentePesado';
import OutroComponente from '@/components/OutroComponente';
// Tudo carregado sincronamente no load inicial
```

**Ganho Esperado:** -50-70% no First Load JS por página

---

#### P2: Lucide Icons - Bundle Completo Incluído
**Impacto:** +2MB no bundle principal

**Padrão Atual (200+ arquivos):**
```typescript
import { Home, Settings, User, Mail, ... } from 'lucide-react';
// Webpack inclui o bundle COMPLETO mesmo com named imports
```

**Problema:** Next.js/Webpack não consegue fazer tree-shaking efetivo de lucide-react com imports agregados.

**Ganho Esperado:** -1.5MB a -2MB

---

### 🟠 PRIORIDADE ALTA

#### P3: jsPDF Carregado Globalmente
**Impacto:** +500KB em todas as páginas

**Uso Atual:**
```typescript
// src/utils/export.ts
import jsPDF from 'jspdf';

export function exportarPDF(data) {
  const doc = new jsPDF();
  // ...
}

// Importado em várias páginas mesmo quando não usam export
```

**Problema:** Incluído no bundle mesmo em páginas que nunca exportam PDF.

**Ganho Esperado:** -500KB em 90% das páginas

---

#### P4: Recharts em Bundle Principal
**Impacto:** +300KB em todas as páginas

**Uso Atual:**
```typescript
// Sparkline component
import { LineChart, Line } from 'recharts';

// Página de analytics
import { BarChart, Bar, XAxis, YAxis } from 'recharts';
```

**Problema:** Carregado mesmo em páginas sem gráficos.

**Ganho Esperado:** -300KB em 95% das páginas

---

### 🟡 PRIORIDADE MÉDIA

#### P5: Componentes de UI Radix Não Lazy
**Impacto:** +200KB de componentes raramente usados

**Exemplos:**
- Dialog, Modal, Popover, Dropdown, Select, etc.
- Carregados mesmo quando não usados na página

**Ganho Esperado:** -100KB a -200KB

---

## 4. Recomendações de Otimização

### R1: Implementar Lazy Loading de Páginas
**Prioridade:** 🔴 CRÍTICA

#### Next.js App Router - Dynamic Imports

**Antes:**
```typescript
// app/analytics/page.tsx
import AnalyticsChart from '@/components/AnalyticsChart';
import HeavyTable from '@/components/HeavyTable';

export default function AnalyticsPage() {
  return (
    <>
      <AnalyticsChart />
      <HeavyTable />
    </>
  );
}
```

**Depois:**
```typescript
// app/analytics/page.tsx
import dynamic from 'next/dynamic';
import { Suspense } from 'react';

const AnalyticsChart = dynamic(
  () => import('@/components/AnalyticsChart'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false // se não precisa SSR
  }
);

const HeavyTable = dynamic(
  () => import('@/components/HeavyTable'),
  { loading: () => <TableSkeleton /> }
);

export default function AnalyticsPage() {
  return (
    <>
      <Suspense fallback={<ChartSkeleton />}>
        <AnalyticsChart />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <HeavyTable />
      </Suspense>
    </>
  );
}
```

#### Componentes para Priorizar (ordem de impacto):
1. **Charts/Gráficos** (Recharts)
2. **Tabelas complexas** (DataTables com muitos dados)
3. **Modais/Dialogs** (abertos sob demanda)
4. **Formulários complexos** (multi-step, validação pesada)
5. **Visualizadores** (PDF, imagens, mapas)

---

### R2: Otimizar Imports de Lucide Icons
**Prioridade:** 🔴 CRÍTICA

#### Opção A: Imports Individuais (Recomendado)

**Antes:**
```typescript
import { Home, Settings, User, Mail, Bell } from 'lucide-react';
```

**Depois:**
```typescript
import Home from 'lucide-react/dist/esm/icons/home';
import Settings from 'lucide-react/dist/esm/icons/settings';
import User from 'lucide-react/dist/esm/icons/user';
import Mail from 'lucide-react/dist/esm/icons/mail';
import Bell from 'lucide-react/dist/esm/icons/bell';
```

#### Opção B: Script de Transformação Automatizada

Criar script para converter automaticamente:

```typescript
// scripts/optimize-lucide-imports.ts
import { readFileSync, writeFileSync } from 'fs';
import { glob } from 'glob';

const files = glob.sync('src/**/*.{ts,tsx}');

files.forEach(file => {
  let content = readFileSync(file, 'utf-8');

  // Regex para capturar imports agregados
  const match = content.match(/import\s*\{([^}]+)\}\s*from\s*['"]lucide-react['"]/);

  if (match) {
    const icons = match[1].split(',').map(i => i.trim());
    const newImports = icons.map(icon =>
      `import ${icon} from 'lucide-react/dist/esm/icons/${icon.toLowerCase()}';`
    ).join('\n');

    content = content.replace(match[0], newImports);
    writeFileSync(file, content);
  }
});
```

#### Opção C: Babel Plugin (Mais elegante)

```javascript
// babel.config.js ou next.config.js
module.exports = {
  plugins: [
    [
      'babel-plugin-transform-imports',
      {
        'lucide-react': {
          transform: 'lucide-react/dist/esm/icons/${member}',
          preventFullImport: true,
        },
      },
    ],
  ],
};
```

**Ganho:** -1.5MB a -2MB no bundle principal

---

### R3: Lazy Load jsPDF
**Prioridade:** 🟠 ALTA

**Antes:**
```typescript
// src/utils/export.ts
import jsPDF from 'jspdf';

export function exportarPDF(data: any) {
  const doc = new jsPDF();
  // ... configuração
  doc.save('relatorio.pdf');
}
```

**Depois:**
```typescript
// src/utils/export.ts
export async function exportarPDF(data: any) {
  // Dynamic import - só carrega quando necessário
  const { default: jsPDF } = await import('jspdf');

  const doc = new jsPDF();
  // ... configuração
  doc.save('relatorio.pdf');
}

// Uso no componente
async function handleExportar() {
  setLoading(true);
  try {
    await exportarPDF(dados);
  } finally {
    setLoading(false);
  }
}
```

**Alternativa: Lazy Component**
```typescript
// components/ExportButton.tsx
import dynamic from 'next/dynamic';

const PDFExporter = dynamic(
  () => import('@/components/PDFExporter'),
  { ssr: false }
);

export function ExportButton({ data }) {
  const [showExporter, setShowExporter] = useState(false);

  return (
    <>
      <Button onClick={() => setShowExporter(true)}>
        Exportar PDF
      </Button>
      {showExporter && <PDFExporter data={data} />}
    </>
  );
}
```

**Ganho:** -500KB em páginas sem funcionalidade de export

---

### R4: Lazy Load Recharts
**Prioridade:** 🟠 ALTA

**Antes:**
```typescript
// components/AnalyticsChart.tsx
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function AnalyticsChart({ data }) {
  return (
    <LineChart data={data}>
      <Line dataKey="value" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
    </LineChart>
  );
}
```

**Depois:**
```typescript
// components/AnalyticsChart.tsx
import dynamic from 'next/dynamic';

const Chart = dynamic(
  () => import('./ChartRenderer'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false // Charts geralmente não precisam SSR
  }
);

export function AnalyticsChart({ data }) {
  return <Chart data={data} />;
}

// components/ChartRenderer.tsx (separado)
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export default function ChartRenderer({ data }) {
  return (
    <LineChart data={data}>
      <Line dataKey="value" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
    </LineChart>
  );
}
```

**Ganho:** -300KB em páginas sem gráficos

---

### R5: Code Splitting Estratégico
**Prioridade:** 🟡 MÉDIA

#### Separar Rotas por Feature Module

```typescript
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      'date-fns',
    ],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          // Vendor chunks separados
          recharts: {
            test: /[\\/]node_modules[\\/]recharts[\\/]/,
            name: 'recharts',
            priority: 10,
          },
          radix: {
            test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
            name: 'radix-ui',
            priority: 9,
          },
          // Chunks por feature
          financeiro: {
            test: /[\\/]src[\\/]app[\\/]modulos[\\/]financeiro[\\/]/,
            name: 'feature-financeiro',
            priority: 8,
          },
          equipamentos: {
            test: /[\\/]src[\\/]app[\\/]modulos[\\/]equipamentos[\\/]/,
            name: 'feature-equipamentos',
            priority: 8,
          },
        },
      };
    }
    return config;
  },
};
```

---

### R6: Image Optimization
**Prioridade:** 🟡 MÉDIA

```typescript
// Antes
<img src="/logo.png" alt="Logo" />

// Depois
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority // apenas para LCP images
  placeholder="blur" // se tiver blurDataURL
/>
```

**Configuração Next.js:**
```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96],
  },
};
```

---

### R7: Font Optimization
**Prioridade:** 🟡 MÉDIA

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
});

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

---

### R8: Bundle Analysis e Monitoring
**Prioridade:** 🟡 MÉDIA

```bash
# Instalar
npm install -D @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // ... resto da config
});

# Executar análise
ANALYZE=true npm run build
```

**Adicionar ao package.json:**
```json
{
  "scripts": {
    "analyze": "ANALYZE=true next build",
    "analyze:server": "BUNDLE_ANALYZE=server next build",
    "analyze:browser": "BUNDLE_ANALYZE=browser next build"
  }
}
```

---

## 5. Ganhos Esperados

### Cenário Conservador (implementação parcial)

| Otimização | Redução Bundle | Impacto TTI |
|------------|----------------|-------------|
| Lazy loading páginas principais | -1.5MB | -20% |
| Lucide icons individuais | -1.2MB | -15% |
| jsPDF lazy load | -400KB | -5% |
| Recharts lazy load | -200KB | -3% |
| **TOTAL CONSERVADOR** | **-3.3MB** | **-30%** |

### Cenário Otimista (implementação completa)

| Otimização | Redução Bundle | Impacto TTI |
|------------|----------------|-------------|
| Lazy loading completo | -2.5MB | -30% |
| Lucide icons + tree shaking | -1.8MB | -20% |
| jsPDF + outras libs pesadas | -600KB | -8% |
| Code splitting estratégico | -500KB | -7% |
| Image + Font optimization | -300KB | -5% |
| **TOTAL OTIMISTA** | **-5.7MB** | **-50%** |

### Métricas de Performance Esperadas

**Antes:**
```
First Load JS: 8.1MB
Time to Interactive: ~4.5s (3G)
Lighthouse Score: ~65-75
```

**Depois (conservador):**
```
First Load JS: ~4.8MB (-40%)
Time to Interactive: ~3.2s (3G) (-29%)
Lighthouse Score: ~80-85
```

**Depois (otimista):**
```
First Load JS: ~2.4MB (-70%)
Time to Interactive: ~2.2s (3G) (-51%)
Lighthouse Score: ~90-95
```

---

## 6. Plano de Implementação

### Fase 1: Quick Wins (1-2 dias)
**Impacto:** ~40% de melhoria

- [ ] **Sprint 1.1:** Otimizar imports de Lucide Icons
  - Criar script de transformação automática
  - Executar em todos os arquivos
  - Testar build
  - **Ganho:** -1.5MB

- [ ] **Sprint 1.2:** Lazy load de jsPDF e Recharts
  - Converter export.ts para dynamic import
  - Lazy load componentes de chart
  - **Ganho:** -700KB

- [ ] **Sprint 1.3:** Configurar bundle analyzer
  - Instalar e configurar
  - Gerar relatório baseline
  - Identificar outros problemas

**Entrega Fase 1:** Bundle reduzido de 8.1MB para ~5.9MB

---

### Fase 2: Lazy Loading Core (3-5 dias)
**Impacto:** +30% de melhoria adicional

- [ ] **Sprint 2.1:** Lazy loading - Páginas de Analytics
  - Dashboard principal
  - Relatórios
  - Gráficos e visualizações
  - **Ganho:** -800KB por página

- [ ] **Sprint 2.2:** Lazy loading - Módulo Financeiro
  - Clientes, Contas a Pagar/Receber
  - Estoque, Contabilidade
  - Componentes de tabela pesados
  - **Ganho:** -600KB por página

- [ ] **Sprint 2.3:** Lazy loading - Equipamentos e CRM
  - Patrimônio, Manutenções
  - Leads CRM
  - **Ganho:** -500KB por página

**Entrega Fase 2:** First Load JS médio de ~3.5MB

---

### Fase 3: Otimizações Avançadas (2-3 dias)
**Impacto:** +15% de melhoria adicional

- [ ] **Sprint 3.1:** Code splitting estratégico
  - Configurar webpack chunks por feature
  - Separar vendor chunks
  - **Ganho:** -400KB

- [ ] **Sprint 3.2:** Image e Font optimization
  - Migrar para next/image
  - Configurar fonts otimizados
  - **Ganho:** -300KB

- [ ] **Sprint 3.3:** Radix UI lazy loading
  - Lazy load de Dialogs, Modals
  - Dropdowns e Selects sob demanda
  - **Ganho:** -200KB

**Entrega Fase 3:** First Load JS target de ~2.5MB

---

### Fase 4: Monitoramento e Fine-tuning (ongoing)

- [ ] **Setup de Monitoring**
  - Lighthouse CI
  - Bundle size tracking
  - Performance budgets

- [ ] **Performance Budgets:**
  ```json
  {
    "budgets": [
      {
        "path": "/_app",
        "maxSize": "200KB"
      },
      {
        "path": "/page/**",
        "maxSize": "300KB"
      },
      {
        "path": "/chunks/**",
        "maxSize": "150KB"
      }
    ]
  }
  ```

---

## 7. Checklist de Validação

### Após Cada Fase

- [ ] Build sem erros
- [ ] Bundle size reduzido conforme esperado
- [ ] Lighthouse score melhorado
- [ ] Testes E2E passando
- [ ] Nenhuma regressão funcional
- [ ] Performance em 3G testada
- [ ] Documentação atualizada

### Ferramentas de Validação

```bash
# Bundle analysis
npm run analyze

# Lighthouse CI
npx lhci autorun

# Performance test
npm run build && npm start
# Abrir DevTools > Performance > Record

# Size comparison
du -sh .next/ > build-size-after.txt
diff build-size-before.txt build-size-after.txt
```

---

## 8. Riscos e Mitigações

### Risco 1: Breaking Changes em Imports
**Probabilidade:** Média
**Impacto:** Alto
**Mitigação:**
- Testar em ambiente de staging primeiro
- Ter script de rollback
- Fazer em batches pequenos

### Risco 2: Lazy Loading Causando UX Ruim
**Probabilidade:** Baixa
**Impacto:** Médio
**Mitigação:**
- Implementar skeletons de qualidade
- Prefetch de rotas comuns
- Testar em conexões lentas

### Risco 3: Aumento de Complexidade
**Probabilidade:** Alta
**Impacto:** Baixo
**Mitigação:**
- Documentar padrões
- Code reviews rigorosos
- Linting rules customizadas

---

## 9. Próximos Passos

1. **Aprovar plano de implementação**
2. **Executar Fase 1 (Quick Wins)**
3. **Medir resultados e ajustar estratégia**
4. **Continuar com Fases 2 e 3**
5. **Setup de monitoring contínuo**

---

## 10. Referências

- [Next.js Performance Optimization](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Bundle Analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Web Vitals](https://web.dev/vitals/)

---

**Gerado por:** Claude Code (Auditoria Automatizada)
**Última Atualização:** 2026-02-02
