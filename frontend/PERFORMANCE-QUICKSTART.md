# Performance Monitoring - Quick Start

Guia rápido para começar a usar as ferramentas de monitoramento de performance.

## Instalação

Tudo já está configurado! As ferramentas estão prontas para uso.

## Comandos Essenciais

### Análise de Bundle

```bash
# Ver composição do bundle (interface visual)
npm run analyze

# Comparar tamanho com baseline
npm run perf:compare

# Atualizar baseline (após aprovar mudanças)
npm run perf:baseline
```

### Lighthouse

```bash
# Executar Lighthouse CI
npm run lighthouse

# Ver relatório formatado
npm run lighthouse:report

# Executar tudo (build + lighthouse + report)
npm run perf:test
```

### Análise Completa

```bash
# Build + Bundle Analysis + Lighthouse
npm run perf:all
```

## Workflow Típico

### Durante Desenvolvimento

1. **Antes de começar uma feature**:
   ```bash
   npm run perf:compare
   ```
   Anote o tamanho atual do bundle.

2. **Após completar a feature**:
   ```bash
   npm run build
   npm run perf:compare
   ```
   Verifique se o bundle cresceu mais de 5%.

3. **Se cresceu muito**:
   - Revise imports
   - Aplique lazy loading
   - Use `npm run analyze` para identificar culpados

### Antes de Abrir PR

```bash
# Executar análise completa
npm run perf:all
```

Verificar:
- Bundle size dentro do limite
- Lighthouse scores aceitáveis
- Sem regressões críticas

### Após Merge (Automático)

O GitHub Actions vai:
1. Executar análise de performance
2. Atualizar baseline automaticamente
3. Comentar no PR com resultados

## Thresholds Importantes

| Métrica | Limite | Ação se Exceder |
|---------|--------|-----------------|
| Bundle Growth | 5% | Revisar imports, aplicar lazy load |
| Performance Score | 80% | Otimizar recursos, code splitting |
| Accessibility | 90% | Corrigir issues de a11y |
| FCP | 2000ms | Otimizar critical path |
| LCP | 3000ms | Otimizar imagens e recursos |
| TBT | 300ms | Reduzir JavaScript, code split |
| CLS | 0.1 | Definir dimensões, evitar shifts |

## Interpretando Resultados

### Bundle Size

```
⚠️  Total: 2.45 MB (+125 KB / +5.3%)
```

**O que fazer**:
1. Executar `npm run analyze`
2. Identificar módulos grandes
3. Aplicar lazy loading ou remover dependências

### Lighthouse Scores

```
Performance:     🟢 85%
Accessibility:   🟢 92%
Best Practices:  🟡 78%
SEO:             🟢 95%
```

**Cores**:
- 🟢 (90-100%): Excelente
- 🟡 (50-89%): Precisa melhorias
- 🔴 (0-49%): Crítico

## Problemas Comuns

### Bundle cresceu sem motivo aparente

**Causa**: Import não otimizado

**Solução**:
```typescript
// ❌ Ruim - importa tudo
import * as Icons from 'lucide-react';

// ✅ Bom - tree-shaking
import { User, Home } from 'lucide-react';
```

### Performance score baixo

**Causa**: Componentes pesados carregados imediatamente

**Solução**:
```typescript
// ❌ Ruim - carrega tudo upfront
import { Chart } from '@/components/Chart';

// ✅ Bom - lazy load
const Chart = dynamic(() => import('@/components/Chart'), {
  loading: () => <Loading />
});
```

### CLS alto

**Causa**: Elementos sem dimensões

**Solução**:
```typescript
// ❌ Ruim
<img src="/image.jpg" />

// ✅ Bom
<Image src="/image.jpg" width={800} height={600} />
```

## CI/CD

### Pull Request

Automaticamente executa:
- Bundle size comparison
- Lighthouse audits
- Comenta resultados no PR

### Merge to Main

Automaticamente:
- Atualiza baseline
- Commit novo baseline

## Recursos

- Documentação completa: [PERFORMANCE-MONITORING.md](./PERFORMANCE-MONITORING.md)
- Next.js Performance: https://nextjs.org/docs/app/building-your-application/optimizing
- Web Vitals: https://web.dev/vitals/

## Dúvidas?

Consultar [PERFORMANCE-MONITORING.md](./PERFORMANCE-MONITORING.md) para documentação detalhada.
