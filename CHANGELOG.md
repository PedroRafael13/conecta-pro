# Changelog - Conecta PRO

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.0.0-rc] - 2026-04-01

### Added
- Sistema de agentes autônomos 24h: 80 agentes, 13 orquestradores, score 10.0/10
- Bot monitor Telegram @conecta_pro_monitor_bot (alertas a cada 30 min)
- docs/RUNBOOK.md: 6 incidentes documentados com diagnóstico e resolução

### Fixed
- Auth: HTTPBearer retorna 401 (não 403) sem token — RFC 6750
- Auth: 68 endpoints LGPD + config protegidos com JWT
- DB Schema: 88 colunas adicionadas (tenants, feature_flags, system_configs)
- SQLAlchemy: @property removido de queries — substituído por colunas reais
- CI/CD: DEPLOY_PATH corrigido (/opt/erp-conecta-mais → /opt/conecta-pro)
- CI/CD: branch feature/* adicionada aos triggers de push/pull_request
- CI/CD: 5 quality gates || true removidos (mypy, eslint, tsc, safety, vitest)
- Financeiro: 12/12 agentes corrigidos (condominio_id obrigatório)
- DP: is_active sincronizado com status (campo exposto no schema DPEmployeeRead)
- GED: trailing slash 404 corrigido em 6 endpoints (redirect_slashes=False)
- GED: UUID inválido em kits/{id}/send retorna 422 (não 500)
- Operacional: time_bank/stats corrigido (func.case() → case() — SA 2.x compat)
- Rate limit: token compartilhado entre agentes (monkey-patch BaseAgent)
- CLAUDE.md: atualizado (estava 58 dias desatualizado)
- README.md: path /opt/erp-conecta-mais corrigido para /opt/conecta-pro

### Security
- 111 controllers sem auth mapeados — correção em progresso (Skill 06)
- LGPD: 21 endpoints protegidos com JWT
- Config: 47 endpoints protegidos com JWT

---

## [Unreleased] - 2026-01-26

### 🎯 Quick Wins - Fase 1 (Em Desenvolvimento)

#### ✅ Added - Funcionalidades Implementadas

##### 1. Sistema de Templates de Escalas (70%)
- **Backend:**
  - ✅ Model `ScaleTemplate` com suporte a JSONB para flexibilidade
  - ✅ Repository completo com CRUD + estatísticas
  - ✅ Schemas Pydantic com validações robustas
  - ✅ Tabela `scale_templates` no PostgreSQL
  - ⚠️ Service em desenvolvimento
  - ⚠️ Controller pendente
  - ⚠️ Rotas não registradas

- **Frontend:**
  - ✅ Hook `useScaleTemplates` com 3 hooks especializados:
    - `useTemplates()` - Listagem paginada com filtros
    - `useTemplate(id)` - Buscar template individual
    - `useTemplateOperations()` - CRUD + apply/preview
  - ✅ Types TypeScript completos
  - ⚠️ UI de templates pendente
  - ⚠️ Integração com tela de escalas pendente

##### 2. Auto-save em Formulários (50%)
- ✅ Hook `useAutoSave` com features enterprise:
  - Debounce configurável (padrão 2s)
  - Persistência dupla: localStorage + backend opcional
  - Sanitização automática de campos sensíveis (password, token, etc)
  - Restore de rascunhos com validação de expiração (7 dias)
  - Cleanup automático de rascunhos antigos
  - Indicadores de estado: saving, lastSaved, hasDraft, error
- ✅ Component `<RestoreAlert />` criado
- ⚠️ Hook não integrado em formulários ainda
- ⚠️ Precisa aplicar em: Postos, Escalas, Ocorrências, Colaboradores

##### 3. Atalhos de Teclado (40%)
- ✅ Hook `useKeyboardShortcuts` genérico e reutilizável
- ✅ Hook `useGlobalShortcuts` com atalhos padrão:
  - `/` - Abrir busca global
  - `Ctrl+K` - Command palette
  - `Ctrl+B` - Toggle sidebar
  - `Alt+1` - Dashboard
  - `Alt+2` - Operacional
  - `Alt+3` - Financeiro
  - `Alt+4` - CRM
  - `Shift+?` - Help overlay
  - `Esc` - Fechar modais/dropdowns
- ⚠️ Hook criado mas não integrado no layout
- ⚠️ Help overlay (lista de atalhos) não implementado
- ⚠️ Callbacks não conectados

##### 4. Responsividade Mobile Avançada (90%)
- ✅ Layout de módulos totalmente responsivo
- ✅ Sidebar desktop collapsible
- ✅ Sidebar mobile com overlay e animações
- ✅ Menu hamburguer mobile
- ✅ Header mobile sticky
- ✅ Transitions suaves (duration-300)
- ✅ Breakpoints Tailwind bem definidos
- ⚠️ Tabelas responsivas em desenvolvimento
- ⚠️ Testes em dispositivos reais pendentes

##### 5. KPI Widgets com Métricas (40%)
- ✅ Dashboard operacional com 5 KPIs estratégicos:
  - Taxa de Cobertura de Postos (com código de cores)
  - Horas Trabalhadas do Mês
  - Ocorrências Pendentes
  - Escalas em Andamento
  - Alertas de Turnos
- ✅ Cards clicáveis com navegação
- ✅ Ícones coloridos por categoria
- ✅ Indicadores visuais (TrendingUp/Down)
- ⚠️ Sparklines (mini gráficos) não implementados
- ⚠️ Recharts instalado mas não usado para KPIs
- ⚠️ Dados históricos não sendo buscados

##### 6. Sistema de Notificações Push (60%)
- **Backend:**
  - ✅ Módulo `notifications/push/` completo
  - ✅ Models: `PushNotification`, `PushCampaign`, `PushDevice`
  - ✅ Services: `push_service.py`, `fcm_service.py`
  - ✅ Controller: `push_controller.py` com endpoints
  - ✅ Schemas: `push_schemas.py` com validações

- **Frontend:**
  - ⚠️ NotificationBell component não criado
  - ⚠️ Service Worker não configurado
  - ⚠️ Device registration não implementado
  - ⚠️ PWA manifest incompleto

##### 7. Exportação de Dados (40%)
- ✅ Dependências instaladas:
  - `jspdf: ^4.0.0`
  - `jspdf-autotable: ^5.0.7`
  - `xlsx: ^0.18.5`
- ⚠️ Implementação parcial em:
  - `postos/page.tsx`
  - `relatorios/page.tsx`
- ⚠️ Funções utilitárias não centralizadas
- ⚠️ Botões de export ausentes em várias listagens
- ⚠️ Formatação de dados não padronizada

#### ⚠️ In Progress - Em Desenvolvimento

##### 8. Modo Escuro / Dark Mode (50%)
- ✅ Classe `dark` aplicada no HTML root
- ✅ Variáveis CSS HSL configuradas
- ⚠️ ThemeContext não criado
- ⚠️ ThemeToggle component não implementado
- ⚠️ Modo sempre escuro (não há toggle)
- ⚠️ Preferência não persistida em localStorage
- ⚠️ ThemeProvider não integrado

##### 9. Command Palette (30%)
- ✅ Atalho `Ctrl+K` definido
- ✅ Callback `onCommandPaletteOpen` preparado
- ⚠️ Component `<CommandPalette />` não criado
- ⚠️ Lógica de busca/ações não implementada
- ⚠️ UI modal/dropdown ausente
- ⚠️ Integrações com módulos ausentes

##### 10. Busca Global (30%)
- ✅ Atalho `/` definido
- ✅ Callback `onSearchOpen` preparado
- ⚠️ Component `<GlobalSearch />` não criado
- ⚠️ Backend endpoint de busca global ausente
- ⚠️ Indexação de dados não implementada
- ⚠️ UI de resultados não existe

##### 11. Onboarding Tour (20%)
- ✅ Biblioteca `shepherd.js: ^14.5.1` instalada
- ⚠️ Hook `useTour` não encontrado
- ⚠️ Tours não configurados
- ⚠️ Data attributes `data-tour-*` não adicionados
- ⚠️ CSS customizado ausente
- ⚠️ Auto-start lógica não implementada
- ⚠️ TourTrigger component não criado

---

### 📊 Infraestrutura e DevOps

#### Added
- ✅ Container backend rodando (healthy)
- ✅ Container frontend rodando (healthy)
- ✅ PostgreSQL 16 rodando (healthy)
- ✅ Redis 7 rodando (healthy)

#### ⚠️ Issues
- ⚠️ Celery workers unhealthy (6 workers)
- ⚠️ Flower monitoring unhealthy

---

### 🛠️ Dependências Novas

#### Frontend
```json
{
  "shepherd.js": "^14.5.1",     // Onboarding tours
  "jspdf": "^4.0.0",            // Export PDF
  "jspdf-autotable": "^5.0.7",  // PDF tables
  "xlsx": "^0.18.5",            // Export Excel
  "recharts": "^3.7.0"          // Charts/Sparklines
}
```

#### Backend
- Nenhuma dependência nova identificada nesta fase

---

### 🔧 Melhorias Técnicas

#### Frontend
- ✅ Hooks customizados organizados em `/src/hooks/`
- ✅ Types TypeScript centralizados
- ✅ React Query para cache de dados
- ✅ Layout responsivo com Tailwind CSS 4.x

#### Backend
- ✅ Repository pattern para database
- ✅ Pydantic schemas com validações
- ✅ Soft delete implementado
- ✅ Async/await em todas operações

---

### 🐛 Known Issues

#### Críticos
1. **Hooks não integrados:** useKeyboardShortcuts, useAutoSave criados mas não usados
2. **ScaleTemplate sem endpoints:** Backend incompleto, rotas não registradas
3. **ThemeProvider ausente:** Modo escuro hardcoded, sem toggle dinâmico
4. **Celery unhealthy:** Workers de notificações podem estar comprometidos

#### Altos
1. **Sparklines não implementados:** KPIs sem visualização gráfica
2. **Onboarding tour não configurado:** UX de primeiro acesso inexistente
3. **Service Worker ausente:** PWA capabilities não ativadas
4. **Exportação inconsistente:** Funcionalidade não padronizada

#### Médios
1. **Testes automatizados:** Sem evidência de E2E tests
2. **Performance audit:** Lighthouse não executado
3. **Error boundaries:** React error handling não verificado

---

### 📝 Notas de Desenvolvimento

#### Para Desenvolvedores
- **Hooks criados estão em:** `/frontend/src/hooks/`
- **Backend models em:** `/backend/modules/operacional/models/`
- **Schemas em:** `/backend/modules/operacional/schemas/`
- **Repositories em:** `/backend/modules/operacional/repositories/`

#### Tasks Pendentes
- [ ] Criar ScaleTemplateService
- [ ] Criar ScaleTemplateController
- [ ] Registrar rotas de templates
- [ ] Criar migration para scale_templates
- [ ] Implementar ThemeContext + ThemeToggle
- [ ] Integrar useKeyboardShortcuts no layout
- [ ] Aplicar useAutoSave em formulários
- [ ] Criar CommandPalette component
- [ ] Criar GlobalSearch component
- [ ] Implementar Sparklines em KPIs
- [ ] Configurar Onboarding tours
- [ ] Padronizar exportação de dados
- [ ] Implementar NotificationBell
- [ ] Configurar Service Worker
- [ ] Fix Celery workers

---

### 🎯 Próxima Release

**Objetivo:** Completar Quick Wins Fase 1
**Target:** 100% das 11 features funcionais
**ETA:** 44-60h de desenvolvimento restante

#### Prioridades:
1. Completar features iniciadas (ScaleTemplates, ThemeProvider, Integrar hooks)
2. Implementar UIs faltantes (CommandPalette, GlobalSearch, NotificationBell, Sparklines)
3. Finalizar features restantes (OnboardingTour, Exportação padronizada)
4. QA rigoroso + Performance audit + Testes de regressão

---

## Versões Anteriores

### [2.0.0] - 2025-01-XX
- Sistema base Conecta PRO
- Módulos: Operacional, CRM, Financeiro
- Autenticação JWT
- Dashboard inicial

---

**Mantido por:** CONECTAMAIS ELETRONICA LTDA
**Última atualização:** 2026-01-26
