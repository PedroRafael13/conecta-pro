# CONECTA PRO — AUDITORIA SKILL 09
## UX, Acessibilidade e Experiência do Usuário
### Data: 31/03/2026 | Next.js ^16.1.6 | 604 arquivos .tsx | 267 páginas

---

## SNAPSHOT DO SISTEMA

| Métrica | Valor |
|---------|-------|
| Framework | Next.js ^16.1.6 |
| Total de páginas (page.tsx) | 267 |
| Total de componentes .tsx | 277 |
| Total de arquivos .tsx | 604 |
| Frontend (porta) | 3001 — HTTP 200 ✅ |
| Design System | Radix UI + Lucide + Tailwind custom |
| State/Data | @tanstack/react-query v5 |
| Formulários | react-hook-form + @hookform/resolvers |
| Notificações | sonner (67 arquivos) |
| Charts | recharts + echarts-for-react |
| Dark Mode | Configurado (darkMode: 'class') |
| Cores principais | Navy #1E3A5F / Brand #F97316 |

---

## RESULTADO GERAL

```
╔══════════════════════════════════════════════════════════════╗
║          CONECTA PRO — AUDITORIA SKILL 09                   ║
║          UX e Acessibilidade — 31/03/2026                   ║
╠═══════════════════════╦════════════╦════════════╦═══════════╣
║ Área                  ║ Checklist  ║  Score     ║ Status    ║
╠═══════════════════════╬════════════╬════════════╬═══════════╣
║ Design System         ║   9/10     ║  9.5/10    ║    ✅     ║
║ Performance Frontend  ║   6/10     ║  6.0/10    ║    ⚠️     ║
║ Formulários           ║   7/10     ║  7.0/10    ║    ⚠️     ║
║ Acessibilidade        ║   4/10     ║  4.0/10    ║    ❌     ║
║ Módulos Específicos   ║   8/10     ║  8.0/10    ║    ✅     ║
╠═══════════════════════╩════════════╩════════════╩═══════════╣
║ TOTAL GERAL                        ║  34.5/50   ║   69%    ║
╠══════════════════════════════════════════════════════════════╣
║ Páginas sem loading state: 3 (relatorios/central, ged,      ║
║                               rh/ia)                        ║
║ Formulários sem validação: 13 form-modals críticos          ║
║ Inputs sem label/aria-label: 244                            ║
║ Imagens sem alt text: 10                                    ║
║ React.memo aplicado: 0 componentes                          ║
║ Error boundaries por módulo: 0 (apenas 1 na raiz)          ║
╚══════════════════════════════════════════════════════════════╝
```

---

## ÁREA 1 — DESIGN SYSTEM E CONSISTÊNCIA (9.5/10)

### Checklist Detalhado

| # | Item | Status | Achado |
|---|------|--------|--------|
| 1 | Cores da marca consistentes | ✅ | 78 ocorrências hex + tokens Tailwind `navy-*`/`brand-*` em tailwind.config |
| 2 | Componentes reutilizáveis | ✅ | 35 diretórios + `/components/ui/` com 38 primitivos (button, card, dialog, modal, badge, skeleton, stepper, kpi-widget…) |
| 3 | Logo SVG e branding | ✅ | 5 variantes de logo em `/public/images/` + SVG inline na página de login |
| 4 | Login split-panel implementado | ✅ | Split-panel navy #1E3A5F + laranja #F97316, logo SVG, animações — design moderno confirmado |
| 5 | Typography consistente | ✅ | 11.279 usos de classes Tailwind tipográficas em 604 arquivos |
| 6 | Espaçamento Tailwind | ✅ | 8.392 ocorrências de `p-/px-/py-/m-/mx-/my-` — sem valores arbitrários em escala relevante |
| 7 | Ícones padronizados | ✅ | lucide-react exclusivo (372 importações) — 0 heroicons, 0 react-icons |
| 8 | Modais consistentes | ✅ | `Modal` via `@/components/ui/modal` dominante (306 ocorrências), 126 importações |
| 9 | "Marketing e Vendas" no sidebar | ⚠️ | Grupo está como **"Negócios"** em `modules.ts` linha 474 — não renomeado |
| 10 | Dark mode | ✅ | 296 classes `dark:`, `ThemeToggle` com 3 modos (light/dark/system), `useTheme` hook próprio |

### Problemas

- **[⚠️ BAIXA]** 20 arquivos usam hex literals (`#1E3A5F`, `#F97316`) em vez de tokens Tailwind (`navy-800`, `brand-500`)
- **[⚠️ BAIXA]** Grupo "Negócios" → renomear para "Marketing e Vendas" em `modules.ts:474` (mudança de 1 linha)
- **[⚠️ BAIXA]** `Dialog` (1 importação) vs `Modal` (126) — consolidar ou documentar quando usar cada um

---

## ÁREA 2 — PERFORMANCE FRONTEND (6/10)

### Checklist Detalhado

| # | Item | Status | Achado |
|---|------|--------|--------|
| 1 | useQuery com staleTime | ✅ | 61 chamadas useQuery, staleTime global 30s em `providers.tsx`, 25 individuais |
| 2 | useState([]) sem useQuery | ✅ | **0 ocorrências** do anti-padrão — dados de servidor via useQuery |
| 3 | Lazy loading | ✅ | 38 ocorrências em 20 arquivos; pasta `/components/lazy/` dedicada |
| 4 | Imagens com next/image | ✅ | 100% das imagens usam `<Image>` — 0 `<img>` sem otimização |
| 5 | Bundle size razoável | ⚠️ | 290 MB total; 16 chunks > 100 KB; maior chunk: **409 KB** |
| 6 | Loading state em API calls | ✅ | 1.832 ocorrências em 238 arquivos (97% cobertura) |
| 7 | Error boundaries por módulo | ⚠️ | **1 único** `error.tsx` na raiz — 0 por módulo em 267 páginas |
| 8 | Skeleton/loading placeholders | ✅ | 460 ocorrências; `form-skeleton`, `chart-skeleton`, `table-skeleton` dedicados |
| 9 | Debounce em buscas | ⚠️ | 36 com debounce OK, mas **8 campos sem debounce** — `CommandPalette` crítico |
| 10 | Memoização | ⚠️ | useMemo (217) + useCallback (222) presentes, mas **React.memo = 0 componentes** |

### Gargalos Críticos

1. **Bundle 290 MB / chunk 409 KB** — 6 chunks de ~381 KB exatos sugerem duplicação. Falta `optimizePackageImports` no `next.config`
2. **React.memo = 0** — tabelas e cards em módulos de alta densidade (operacional, financeiro) re-renderizam sem controle
3. **CommandPalette sem debounce** — paleta global dispara filter a cada keystroke
4. **Error boundaries apenas na raiz** — crash em qualquer módulo derruba tudo

### Quick Wins

```bash
# 1. CommandPalette.tsx — adicionar useDebounce(query, 150)
# 2. Criar error.tsx nos módulos críticos:
cp /src/app/error.tsx /src/app/modulos/financeiro/error.tsx
cp /src/app/error.tsx /src/app/modulos/operacional/error.tsx
cp /src/app/error.tsx /src/app/modulos/dp/error.tsx
# 3. next.config.js — optimizePackageImports: ['lucide-react', 'date-fns']
# 4. Debounce em TenderFilters.tsx, postos/page.tsx, diaristas/page.tsx
```

---

## ÁREA 3 — FORMULÁRIOS E VALIDAÇÃO (7/10)

### Checklist Detalhado

| # | Item | Status | Achado |
|---|------|--------|--------|
| 1 | React Hook Form | ✅ | Presente em 3 arquivos (cobertura 1% — adoção muito baixa) |
| 2 | Zod para validação | ⚠️ | Apenas **1 arquivo** (`TenderFormModal.tsx`) usa zodResolver |
| 3 | Mensagens de erro PT-BR | ⚠️ | Apenas **7 de 36** form-modals exibem erros em campos |
| 4 | Loading state nos submits | ✅ | **36/36** form-modals com `disabled={isLoading}`; 16/36 com spinner animado |
| 5 | Toast/notificações | ✅ | `sonner` em 67 arquivos; `useToast` (shadcn) em 8 arquivos |
| 6 | Confirmação antes de deletar | ⚠️ | `confirm()` nativo em 19 pontos; `AlertDialog` apenas em 5 lugares |
| 7 | Máscaras CPF/CNPJ/telefone/CEP | ⚠️ | Componentes mascarados existem **apenas em `__tests__/`** — não usados em produção |
| 8 | Wizard/stepper de admissão | ✅ | Posto: 6 steps com `<Stepper>`; DP admissão: 2 steps com barra de progresso |
| 9 | Paginação nos datatables | ✅ | **76 arquivos** com `currentPage/totalPages/PAGE_SIZE` — padrão consistente |
| 10 | Busca e filtros | ✅ | **54 arquivos** com `searchTerm/handleSearch/setFilter` — busca em tempo real |

### 13 Formulários Críticos Sem Validação

```
1.  /components/crm/cliente-form-modal.tsx        — CNPJ sem máscara, sem required
2.  /components/crm/oportunidade-form-modal.tsx
3.  /components/servicos/contrato-form-modal.tsx
4.  /components/servicos/ordem-form-modal.tsx
5.  /components/servicos/agendamento-form-modal.tsx
6.  /components/equipamentos/equipment-form-modal.tsx
7.  /components/integracoes/webhook-form-modal.tsx
8.  /components/campo/comunicado-form-modal.tsx
9.  /components/seguranca/pia-form-modal.tsx
10. /components/configuracoes/tenant-form-modal.tsx
11. /components/configuracoes/feature-flag-form-modal.tsx
12. /components/configuracoes/template-form-modal.tsx
13. /components/configuracoes/system-config-form-modal.tsx
```

### Problemas por Prioridade

**[ALTA]** Sem validação em formulários de negócio — cliente com CNPJ inválido entra no banco silenciosamente
**[ALTA]** Máscaras CPF/CNPJ/telefone/CEP ausentes nos forms principais — componentes mascarados existem apenas como mocks de teste
**[ALTA]** Deleção sem confirmação na maioria dos módulos (CRM, financeiro, operacional)
**[MÉDIA]** `confirm()` nativo em 19 pontos — fora do design system, bloqueante, sem dark mode
**[MÉDIA]** Busca sem debounce em 54 tabelas — refiltram a cada keystroke
**[BAIXA]** `useToast` (8 arquivos) vs `sonner` (67 arquivos) — inconsistência visual

---

## ÁREA 4 — ACESSIBILIDADE WCAG 2.1 (4/10)

### Checklist Detalhado

| # | Item | Status | WCAG | Achado |
|---|------|--------|------|--------|
| 1 | Alt text em imagens | ⚠️ | 1.1.1 (A) | 10 sem alt: 3 `<img>` + 7 `<Image>` em login, layout, dashboard |
| 2 | Labels em inputs | ❌ | 1.3.1 (A) | **244 inputs nativos sem label/aria-label** — falha crítica |
| 3 | Contraste de cores | ⚠️ | 1.4.3 (AA) | `text-orange-500` (#F97316) sobre fundo branco = ratio ~3:1 (mínimo 4.5:1) |
| 4 | Navegação por teclado | ⚠️ | 2.1.1 (A) | tabIndex = apenas 4 ocorrências; focus:ring via Shadcn OK; divs clicáveis sem tabIndex |
| 5 | Atributos ARIA | ⚠️ | 4.1.2 (A) | aria-describedby=0, aria-expanded=0, aria-live=0, aria-hidden=1 |
| 6 | Headings hierárquicos | ✅ | 1.3.1 (A) | h1=256, h2=168, h3=297, h4=37; 215/240 páginas com h1 |
| 7 | Feedback visual | ✅ | — | 481 animate-spin, 70 Spinner, 1.832 isLoading |
| 8 | Responsividade mobile | ✅ | — | 387+383+388 breakpoints sm/md/lg; 86 overflow-x-auto |
| 9 | Touch targets (44px) | ⚠️ | 2.5.8 (AA) | **387 elementos h-10 (40px)** — 4px abaixo do mínimo; 23 botões h-4/h-6 |
| 10 | Cor como único indicador | ⚠️ | 1.4.1 (A) | Dots de status no mapa sem aria-label; 67 badges coloridos sem texto alternativo |

### Violações WCAG por Prioridade

| Prioridade | Critério | Nível | Ocorrências |
|-----------|----------|-------|------------|
| 🔴 CRÍTICO | 1.3.1 / 3.3.2 — Labels em inputs | A | 244 inputs |
| 🔴 CRÍTICO | 4.1.2 — ARIA Name, Role, Value | A | 0 aria-describedby/expanded |
| 🟠 ALTO | 1.1.1 — Non-text Content | A | 10 imagens sem alt |
| 🟠 ALTO | 1.4.1 — Uso de Cor | A | Dots no mapa; 67 badges |
| 🟠 ALTO | 2.1.1 — Teclado | A | Divs clicáveis sem tabIndex |
| 🟡 MÉDIO | 4.1.3 — Status Messages | AA | 591 toasts sem aria-live customizado |
| 🟡 MÉDIO | 1.4.3 — Contraste | AA | 617 text-orange/yellow |
| 🟡 MÉDIO | 2.5.8 — Target Size | AA (2.2) | 387 elementos h-10 + 23 botões h-4 |

### Arquivos Críticos para Correção Imediata

```
/app/modulos/financeiro/cobrancas/page.tsx     — 2 <img> sem alt
/app/modulos/financeiro/boletos/page.tsx        — 1 <img> sem alt
/app/forgot-password/page.tsx                  — <Image> sem alt (página pública)
/app/reset-password/page.tsx                   — <Image> sem alt (página pública)
/app/modulos/layout.tsx                        — 4x <Image> sem alt
/app/modulos/operacional/mapa/page.tsx         — dots de status sem aria-label
```

### Impacto Estimado

- Usuários com leitores de tela: **impacto ALTO** — 244 inputs sem label são ininteligíveis
- Usuários com daltonismo (~8% homens): **impacto MODERADO** — status "alta/grave" em laranja/amarelo
- Usuários mobile com limitações motoras: **impacto MODERADO** — 387 botões com 40px (abaixo de 44px)
- **Risco legal**: LBI — Lei 13.146/2015 (Lei Brasileira de Inclusão) + eMAG

---

## ÁREA 5 — MÓDULOS ESPECÍFICOS (8/10)

### Checklist Detalhado

| # | Item | Status | Achado |
|---|------|--------|--------|
| 1 | Frontend rodando | ✅ | HTTP 200 em `http://127.0.0.1:3001` |
| 2 | GED implementado | ✅ | `/app/modulos/documentos/` + hooks `/hooks/ged/` + 8 tipos gerados + 5 test files |
| 3 | Financeiro implementado | ✅ | 22 páginas: dashboard, fluxo-caixa, contas-receber/pagar, faturamento, boletos, NFS-e… |
| 4 | DP/RH implementados | ✅ | DP: 14 páginas; RH: 11 páginas; gestao-pessoas: 5 páginas |
| 5 | Bartolo/Chat AI | ✅ | `BartoloChat.tsx` + widget + hooks + service + types gerados |
| 6 | Navegação Marketing/Negócios | ✅ | `id: 'marketing'` com 4 sub-itens; grupo `id: 'negocios'` agrupa CRM+Marketing+Licitações |
| 7 | Sidebar/Nav principal | ✅ | `layout.tsx` com 70+ ícones, WebSocket, AlertsBadge, ThemeToggle, NotificationBell |
| 8 | Dashboards com dados reais | ✅ | BI: 3 queries reais; CRM, Marketing, Ponto: useQuery com fetch autenticado |
| 9 | Multi-Agent Dashboard | ⚠️ | `/agents/dashboard` = **HTTP 404**; agentes existem em `/operacional/agentes/` e `/licitacoes/ia/` |
| 10 | Markdown no Bartolo | ⚠️ | Via `DOMPurify` + HTML do backend (sem react-markdown cliente); fallback ausente se `response_html` = null |

### Módulos Completamente Implementados
operacional (25+), financeiro (22), dp (14), rh (11), licitacoes (12), documentos/GED, crm, marketing, gestao-pessoas, bi, relatorios, configuracoes, fiscal, equipamentos, recrutamento, saude-ocupacional, portal-funcionario, area-cliente, seguranca, integracoes, automacoes, campo, analytics

### Pendências
- Rota `/agents/dashboard` dedicada (404 — agentes estão em operacional/licitações)
- Fallback client-side para Markdown no Bartolo quando `response_html` = null

---

## PLANO DE AÇÃO PRIORITÁRIO

### 🔴 CRÍTICO — Acessibilidade (fazer primeiro)

```
ISSUE 1: 244 inputs sem label/aria-label
→ Adicionar aria-label em todos <input> sem htmlFor associado
→ Prioridade: financeiro/cobrancas, financeiro/boletos, páginas públicas

ISSUE 2: 10 imagens sem alt text
→ /app/modulos/financeiro/cobrancas/page.tsx (2 imgs)
→ /app/modulos/financeiro/boletos/page.tsx (1 img)
→ /app/forgot-password/page.tsx, /app/reset-password/page.tsx
→ /app/modulos/layout.tsx (4 Images)

ISSUE 3: 0 aria-describedby, aria-expanded, aria-live
→ Adicionar em dropdowns, accordions, mensagens de status
```

### 🟠 ALTO — Formulários e Performance

```
ISSUE 4: 13 form-modals sem validação
→ Migrar para react-hook-form + zod em cliente-form-modal, contrato-form-modal
→ Prioridade: CRM e Financeiro (dados críticos de negócio)

ISSUE 5: Máscaras CPF/CNPJ/telefone ausentes em produção
→ Mover /components/__tests__/CPFInput, CNPJInput → /components/ui/
→ Aplicar em cliente-form-modal, supplier-form-modal

ISSUE 6: confirm() nativo em 19 pontos
→ Substituir por <AlertDialog> (Radix, já instalado)
→ Manter consistência com dark mode

ISSUE 7: Error boundaries por módulo (0 existentes)
→ Criar error.tsx em /modulos/financeiro/, /operacional/, /dp/, /rh/
→ Copiar template do /app/error.tsx existente
```

### 🟡 MÉDIO — Performance

```
ISSUE 8: Bundle 290 MB / chunk 409 KB
→ Adicionar optimizePackageImports em next.config.js
→ Auditar imports de lucide-react (372 importações — potencial tree-shaking)

ISSUE 9: CommandPalette sem debounce
→ Adicionar useDebounce(query, 150) antes do useMemo
→ Impacto imediato em UX da paleta global

ISSUE 10: React.memo = 0
→ Aplicar em componentes de lista pesada: PostCoverageCard, cards de alocação
→ Prioridade: módulos com 50+ itens em tabela
```

### 🟢 BAIXO — Polish e Consistência

```
ISSUE 11: Sidebar "Negócios" → "Marketing e Vendas"
→ modules.ts linha 474: title: 'Negócios' → title: 'Marketing e Vendas'

ISSUE 12: Migrar 8 arquivos de useToast → sonner
→ Consistência visual de notificações

ISSUE 13: 20 arquivos com hex literals → tokens Tailwind
→ Centralizar mudanças futuras de marca

ISSUE 14: Markdown fallback no Bartolo
→ Adicionar react-markdown como fallback quando response_html = null
```

---

## RESUMO EXECUTIVO

O frontend do Conecta PRO está **funcionalmente maduro** (267 páginas, 277 componentes, 22 módulos implementados) com um design system sólido (9.5/10) e boa cobertura de módulos de negócio (8/10).

Os pontos críticos estão concentrados em **acessibilidade** (4/10 — a maior lacuna), **validação de formulários** (cobertura de 1% com React Hook Form/Zod) e **performance de bundle** (290 MB com chunks de 409 KB).

**Risco operacional imediato**: 244 inputs sem label/aria-label violam WCAG 2.1 Nível A e podem gerar passivo sob a Lei Brasileira de Inclusão (LBI 13.146/2015).

**Prioridade de sprint sugerida**:
1. Alt text nas 10 imagens (30 min)
2. Error boundaries nos 4 módulos críticos (1h)
3. AlertDialog substituindo confirm() nos 19 pontos (2h)
4. Validação RHF+Zod nos 5 form-modals de maior risco (1 sprint)
5. Máscaras CPF/CNPJ em produção (1 sprint)

---

*Gerado pela Skill 09 — ux-acessibilidade-conecta-pro*
*Engenheiro Sênior Conecta PRO — Sessão 31/03/2026*
