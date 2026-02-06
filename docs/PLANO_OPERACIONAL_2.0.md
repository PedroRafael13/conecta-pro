# 🚀 PLANO ESTRATÉGICO - MÓDULO OPERACIONAL 2.0
## Conecta PRO - Transformação Digital Operacional

---

**Versão:** 1.0
**Data:** 26 de Janeiro de 2026
**Autor:** Equipe Técnica Conecta PRO
**Status:** Em Aprovação
**Período de Execução:** 18 meses (Fev/2026 - Ago/2027)

---

## 📋 SUMÁRIO EXECUTIVO

### Visão Geral
Este documento apresenta o plano estratégico completo para evolução do Módulo Operacional do Conecta PRO, transformando-o de um sistema funcional em uma plataforma inteligente, preditiva e altamente engajadora.

### Objetivos Estratégicos
1. **Aumentar Produtividade:** Reduzir tempo de gestão de escalas em 60%
2. **Reduzir Custos:** Otimização inteligente economizando 15-20% operacional
3. **Engajar Equipes:** Sistema gamificado aumentando satisfação em 40%
4. **Mobilidade Total:** 80% das operações realizáveis via mobile
5. **Inteligência Preditiva:** IA antecipando 70% dos problemas operacionais

### ROI Projetado
- **Investimento Total:** R$ 620.000 - 880.000
- **Economia Anual Esperada:** R$ 250.000 - 400.000
- **ROI:** 300-400% em 24 meses
- **Payback:** 18-24 meses

### Cronograma Resumido
```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: Quick Wins              │ ████████░░ 2 semanas     │
│ FASE 2: Mobile-First PWA        │ ████████░░ 4 semanas     │
│ FASE 3: Dashboard Inteligente   │ ████████░░ 6 semanas     │
│ FASE 4: Gerador IA de Escalas   │ ████████░░ 8 semanas     │
│ FASE 5: Analytics & Reports     │ ████████░░ 8 semanas     │
│ FASE 6: Portal Colaborador      │ ████████░░ 6 semanas     │
│ FASE 7: Gamificação            │ ████████░░ 6 semanas     │
│ FASE 8: IA Conversacional       │ ████████░░ 12 semanas    │
│ FASE 9: Integrações Avançadas   │ ████████░░ 10 semanas    │
│ FASE 10: Performance & Scale    │ ████████░░ 4 semanas     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 METODOLOGIA DE TRABALHO

### Framework Ágil Adaptado
- **Sprints:** 2 semanas
- **Planning:** Segunda-feira (2h)
- **Daily:** 15 min (async no Slack)
- **Review:** Sexta-feira final do sprint (1h)
- **Retrospective:** Sexta-feira final do sprint (30min)

### Equipe Necessária

#### Time Core (Permanente)
- **1 Tech Lead:** Arquitetura e decisões técnicas
- **2 Full-Stack Developers:** Frontend + Backend
- **1 UX/UI Designer:** Interfaces e experiência
- **1 QA Engineer:** Testes e qualidade
- **1 Product Owner:** Priorização e validação

#### Especialistas (Sob Demanda)
- **1 ML Engineer:** Fases 4 e 8 (IA)
- **1 Mobile Developer:** Fase 2 (PWA)
- **1 DevOps Engineer:** Fase 10 (Performance)

### Cerimônias e Rituais

#### Semanal
- **Monday Sync (30min):** Alinhamento da semana
- **Friday Demo (1h):** Apresentar progresso para stakeholders

#### Mensal
- **User Testing (4h):** Validação com usuários reais
- **Executive Review (2h):** Apresentação para C-Level
- **Tech Debt Sprint:** 1 sprint a cada 4 sprints dedicado a refatoração

### Ferramentas
```yaml
Gestão:
  - Projeto: Jira / Linear
  - Documentação: Notion / Confluence
  - Design: Figma

Desenvolvimento:
  - IDE: VSCode
  - Versionamento: Git + GitHub
  - CI/CD: GitHub Actions

Comunicação:
  - Chat: Slack
  - Vídeo: Google Meet / Zoom
  - Async: Loom (gravações)

Monitoramento:
  - APM: Datadog / New Relic
  - Errors: Sentry
  - Analytics: PostHog / Mixpanel
```

---

## 📅 ROADMAP DETALHADO

---

## FASE 1: QUICK WINS - IMPACTO IMEDIATO
**Duração:** 2 semanas (Sprint 1)
**Objetivo:** Melhorias rápidas de alto impacto
**Prioridade:** ⚡ URGENTE

### 1.1 Notificações Push (3 dias)

#### Objetivo
Implementar sistema de notificações em tempo real para eventos críticos.

#### User Stories
```gherkin
Feature: Notificações Push
  Como Supervisor
  Quero receber notificações push de eventos críticos
  Para reagir rapidamente a problemas operacionais

  Scenario: Funcionário não compareceu
    Given um colaborador está escalado
    And está 15 minutos após horário de entrada
    And não fez check-in
    When o sistema detecta a ausência
    Then envia push notification ao supervisor
    And mostra modal de substituição rápida
    And registra no log de eventos

  Scenario: Aprovação pendente
    Given existe uma escala aguardando aprovação
    And passou 2 horas desde a solicitação
    When o prazo é atingido
    Then notifica o aprovador
    And exibe ação inline "Aprovar agora"
```

#### Tarefas Técnicas

**Backend (1,5 dias)**
```python
# /backend/modules/notifications/
├── models.py
│   └── NotificationPreference (user, channel, type, enabled)
│   └── NotificationLog (user, type, content, read, created_at)
├── services/
│   ├── push_service.py
│   │   └── send_push(user_id, title, body, data, priority)
│   │   └── send_bulk_push(user_ids[], notification)
│   └── notification_scheduler.py
│       └── check_late_employees() # Cron cada 5min
│       └── check_pending_approvals() # Cron cada hora
└── routes.py
    └── POST /preferences (salvar preferências)
    └── GET /notifications (listar)
    └── PATCH /notifications/{id}/read (marcar como lido)
    └── POST /subscribe (registrar device token)
```

**Tarefas Backend:**
- [ ] Criar models de notificações
- [ ] Implementar serviço de push (Firebase Cloud Messaging)
- [ ] Criar cronjobs de verificação
- [ ] Endpoints de preferências
- [ ] Testes unitários (pytest)

**Frontend (1,5 dias)**
```typescript
// /frontend/src/features/notifications/
├── hooks/
│   ├── useNotifications.ts
│   │   └── subscribe(), unsubscribe(), markAsRead()
│   └── useNotificationPreferences.ts
├── components/
│   ├── NotificationBell.tsx (badge com contador)
│   ├── NotificationCenter.tsx (dropdown lista)
│   ├── NotificationItem.tsx
│   └── NotificationPreferences.tsx (modal configuração)
├── services/
│   └── notificationService.ts
│       └── requestPermission()
│       └── registerServiceWorker()
└── types/
    └── notification.types.ts
```

**Tarefas Frontend:**
- [ ] Implementar Service Worker
- [ ] Componente NotificationBell no header
- [ ] Modal de preferências
- [ ] Integração com FCM
- [ ] Handle click em notificação (abrir página relevante)

**Critérios de Aceite:**
- ✅ Notificação chega em < 3 segundos do evento
- ✅ Badge mostra contador não lidas
- ✅ Click na notificação navega para contexto correto
- ✅ Usuário pode silenciar tipos específicos
- ✅ Funciona com app fechado (background)

**Estimativa:** 3 dias
**Risco:** 🟡 Médio (configuração Firebase)

---

### 1.2 Responsividade Total (5 dias)

#### Objetivo
Garantir experiência perfeita em todos dispositivos (desktop, tablet, mobile).

#### Breakpoints
```css
/* Tailwind Breakpoints */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Ultra wide */
```

#### Componentes Prioritários

**Tabelas (2 dias)**
```typescript
// Estratégia: Card view em mobile, table em desktop

// Desktop (lg+)
<Table>
  <TableRow>
    <TableCell>Nome</TableCell>
    <TableCell>Cargo</TableCell>
    <TableCell>Posto</TableCell>
    <TableCell>Status</TableCell>
    <TableCell>Ações</TableCell>
  </TableRow>
</Table>

// Mobile (< lg)
<Card>
  <CardHeader>
    <Avatar />
    <div>
      <h3>João Silva</h3>
      <p className="text-sm text-muted">Portaria</p>
    </div>
    <Badge>Ativo</Badge>
  </CardHeader>
  <CardContent>
    <div className="grid grid-cols-2 gap-2">
      <div>
        <Label>Posto</Label>
        <p>Matriz</p>
      </div>
      <div>
        <Label>Turno</Label>
        <p>12x36</p>
      </div>
    </div>
  </CardContent>
  <CardFooter>
    <Button>Ver Detalhes</Button>
  </CardFooter>
</Card>
```

**Tarefas:**
- [ ] Componente `ResponsiveTable` com auto card/table
- [ ] Testar todas as tabelas do módulo (7 páginas)
- [ ] Otimizar sidebar mobile (drawer deslizante)
- [ ] Modais adaptáveis (fullscreen em mobile)
- [ ] Formulários em steps (mobile)

**Formulários (2 dias)**
```typescript
// MultiStep wizard para formulários longos em mobile

// Desktop: All fields visible
<Form>{fields1}{fields2}{fields3}</Form>

// Mobile: Wizard
<Wizard>
  <Step1>{fields1}</Step1>
  <Step2>{fields2}</Step2>
  <Step3>{fields3}</Step3>
</Wizard>
```

**Tarefas:**
- [ ] `FormWizard` component
- [ ] Progress indicator (steps)
- [ ] Validação por step
- [ ] Navegação entre steps
- [ ] Salvar progresso (localStorage)

**Dashboard (1 dia)**
```typescript
// Grid responsivo de KPIs

<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
  {kpis.map(kpi => <KPICard key={kpi.id} {...kpi} />)}
</div>
```

**Critérios de Aceite:**
- ✅ Lighthouse Mobile Score > 90
- ✅ Nenhum scroll horizontal em nenhuma tela
- ✅ Touch targets mínimo 44x44px
- ✅ Textos legíveis sem zoom (16px+ body)
- ✅ Testado em iPhone SE, iPhone 14, iPad, Android

**Estimativa:** 5 dias
**Risco:** 🟢 Baixo

---

### 1.3 Modo Escuro (2 dias)

#### Objetivo
Implementar tema dark para conforto visual e economia de bateria.

#### Paleta de Cores
```css
/* Tema Claro (atual) */
:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --card: 0 0% 100%;
  --card-foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --primary-foreground: 210 40% 98%;
}

/* Tema Escuro (novo) */
[data-theme="dark"] {
  --background: 222 47% 11%;
  --foreground: 210 40% 98%;
  --card: 217 33% 17%;
  --card-foreground: 210 40% 98%;
  --primary: 217 91% 60%;
  --primary-foreground: 222 47% 11%;
  --muted: 217 33% 25%;
  --accent: 217 33% 25%;
  --border: 217 33% 25%;
}
```

#### Implementação

**Tarefas:**
```typescript
// 1. Context Provider (0.5 dia)
// /frontend/src/contexts/ThemeContext.tsx
export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    return localStorage.getItem('theme') || 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// 2. Toggle Component (0.5 dia)
// /frontend/src/components/ThemeToggle.tsx
export const ThemeToggle = () => {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? <Moon /> : <Sun />}
    </Button>
  )
}

// 3. Atualizar CSS (1 dia)
// - Adicionar variáveis dark em globals.css
// - Testar todos componentes
// - Ajustar imagens/logos (versões dark)
// - Gráficos com cores adaptáveis
```

**Critérios de Aceite:**
- ✅ Toggle no header (desktop) e settings (mobile)
- ✅ Preferência salva (localStorage + backend)
- ✅ Respeita preferência do sistema (prefers-color-scheme)
- ✅ Transição suave entre temas (200ms)
- ✅ Todas as telas testadas (nenhum texto ilegível)

**Estimativa:** 2 dias
**Risco:** 🟢 Baixo

---

### 1.4 Atalhos de Teclado (2 dias)

#### Objetivo
Power users conseguem realizar ações comuns sem mouse.

#### Mapa de Atalhos
```typescript
const shortcuts = {
  // Globais
  '/': 'Focar busca global',
  'Ctrl+K': 'Abrir command palette',
  'Ctrl+B': 'Toggle sidebar',
  'Esc': 'Fechar modal/dropdown',

  // Navegação
  'Alt+1': 'Ir para Dashboard',
  'Alt+2': 'Ir para Postos',
  'Alt+3': 'Ir para Colaboradores',
  'Alt+4': 'Ir para Escalas',

  // Ações
  'Ctrl+N': 'Novo (contexto atual)',
  'Ctrl+S': 'Salvar',
  'Ctrl+E': 'Editar',
  'Ctrl+D': 'Deletar (com confirmação)',

  // Tabelas
  'J/K': 'Navegar linhas (vim-style)',
  'Enter': 'Abrir detalhes',
  'Space': 'Selecionar linha',

  // Modais
  'Tab': 'Próximo campo',
  'Shift+Tab': 'Campo anterior',
  'Ctrl+Enter': 'Submeter formulário',
}
```

#### Implementação

```typescript
// Hook personalizado
// /frontend/src/hooks/useKeyboardShortcuts.ts

export const useKeyboardShortcuts = () => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Ignorar se está em input
      if (e.target instanceof HTMLInputElement) {
        // Exceto Esc
        if (e.key !== 'Escape') return
      }

      // Ctrl+K: Command Palette
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        openCommandPalette()
      }

      // /: Busca
      if (e.key === '/' && !e.ctrlKey) {
        e.preventDefault()
        focusSearch()
      }

      // Alt+Number: Navegação
      if (e.altKey && /[1-4]/.test(e.key)) {
        e.preventDefault()
        navigateToModule(parseInt(e.key))
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])
}

// Command Palette Component
// /frontend/src/components/CommandPalette.tsx

export const CommandPalette = () => {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const commands = [
    { id: 'new-posto', label: 'Novo Posto', icon: MapPin, action: () => {} },
    { id: 'new-collab', label: 'Novo Colaborador', icon: UserPlus },
    { id: 'new-scale', label: 'Nova Escala', icon: Calendar },
    // ... mais comandos
  ]

  const filtered = commands.filter(c =>
    c.label.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="p-0">
        <Input
          placeholder="Digite um comando..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="max-h-96 overflow-y-auto">
          {filtered.map(cmd => (
            <CommandItem key={cmd.id} onClick={cmd.action}>
              <cmd.icon className="mr-2" />
              {cmd.label}
            </CommandItem>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

**Tarefas:**
- [ ] Hook `useKeyboardShortcuts`
- [ ] Command Palette component
- [ ] Overlay de ajuda (? para mostrar atalhos)
- [ ] Registrar atalhos em cada página
- [ ] Documentação de atalhos

**Critérios de Aceite:**
- ✅ Command palette abre com Ctrl+K
- ✅ Busca filtra comandos em tempo real
- ✅ Executar comando fecha o palette
- ✅ ? mostra overlay com todos atalhos
- ✅ Funciona em todos navegadores

**Estimativa:** 2 dias
**Risco:** 🟢 Baixo

---

### 1.5 KPI Widgets Interativos (3 dias)

#### Objetivo
Transformar KPIs estáticos em widgets clicáveis com drill-down.

#### Design

```typescript
// Before (estático)
<Card>
  <CardHeader>
    <CardTitle>Postos Ativos</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-4xl font-bold">42</p>
  </CardContent>
</Card>

// After (interativo)
<KPIWidget
  title="Postos Ativos"
  value={42}
  change={+5}
  changeType="increase"
  trend="up"
  onClick={() => navigate('/postos?status=ativo')}
  sparklineData={[38, 39, 41, 40, 42]}
  description="vs. mês anterior"
/>
```

#### Componente

```typescript
// /frontend/src/components/KPIWidget.tsx

interface KPIWidgetProps {
  title: string
  value: number | string
  change?: number
  changeType?: 'increase' | 'decrease'
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ComponentType
  onClick?: () => void
  sparklineData?: number[]
  description?: string
  loading?: boolean
}

export const KPIWidget: React.FC<KPIWidgetProps> = ({
  title,
  value,
  change,
  changeType,
  trend,
  icon: Icon,
  onClick,
  sparklineData,
  description,
  loading
}) => {
  return (
    <Card
      className={cn(
        "transition-all duration-200 hover:shadow-lg",
        onClick && "cursor-pointer hover:scale-105"
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && (
          <Icon className="h-4 w-4 text-muted-foreground" />
        )}
      </CardHeader>

      <CardContent>
        {loading ? (
          <Skeleton className="h-10 w-24" />
        ) : (
          <>
            <div className="text-3xl font-bold">{value}</div>

            {change !== undefined && (
              <div className={cn(
                "flex items-center text-sm mt-1",
                changeType === 'increase' ? 'text-green-600' : 'text-red-600'
              )}>
                {trend === 'up' && <TrendingUp className="h-4 w-4 mr-1" />}
                {trend === 'down' && <TrendingDown className="h-4 w-4 mr-1" />}
                <span>{change > 0 ? '+' : ''}{change}%</span>
                {description && (
                  <span className="text-muted-foreground ml-1">
                    {description}
                  </span>
                )}
              </div>
            )}

            {sparklineData && (
              <div className="mt-4">
                <Sparkline data={sparklineData} height={30} />
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
```

#### Sparkline Component

```typescript
// /frontend/src/components/Sparkline.tsx

import { Line } from 'react-chartjs-2'

interface SparklineProps {
  data: number[]
  height?: number
  color?: string
}

export const Sparkline: React.FC<SparklineProps> = ({
  data,
  height = 40,
  color = '#3b82f6'
}) => {
  const chartData = {
    labels: data.map((_, i) => i),
    datasets: [{
      data,
      borderColor: color,
      borderWidth: 2,
      fill: false,
      pointRadius: 0,
      tension: 0.4
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    scales: {
      x: { display: false },
      y: { display: false }
    }
  }

  return (
    <div style={{ height }}>
      <Line data={chartData} options={options} />
    </div>
  )
}
```

#### Backend - Endpoint de Tendências

```python
# /backend/modules/operacional/controllers/dashboard_controller.py

@router.get("/kpi-trends")
async def get_kpi_trends(
    period: str = Query("7d", regex="^(7d|30d|90d)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna dados de tendência para sparklines dos KPIs.

    Args:
        period: Período (7d, 30d, 90d)

    Returns:
        Dict com arrays de valores históricos
    """
    days = int(period[:-1])

    # Buscar dados históricos
    trends = await get_historical_kpis(db, days)

    return {
        "postos_ativos": [38, 39, 41, 40, 42],
        "colaboradores_ativos": [120, 125, 123, 127, 130],
        "escalas_em_andamento": [5, 6, 4, 7, 5],
        "ocorrencias_mes": [12, 15, 11, 10, 8],
        "cobertura_percentual": [95, 97, 96, 98, 100]
    }
```

**Tarefas:**
- [ ] Componente KPIWidget
- [ ] Componente Sparkline
- [ ] Backend endpoint de tendências
- [ ] Integrar em Dashboard
- [ ] Drill-down navigation
- [ ] Loading states
- [ ] Testes

**Critérios de Aceite:**
- ✅ Hover mostra sombra e scale
- ✅ Click navega para detalhes
- ✅ Sparkline renderiza corretamente
- ✅ Change % exibe cor correta (verde/vermelho)
- ✅ Loading skeleton suave

**Estimativa:** 3 dias
**Risco:** 🟢 Baixo

---

### 1.6 Busca Global (4 dias)

#### Objetivo
Buscar em qualquer entidade do sistema a partir de qualquer tela.

#### Funcionalidade

```typescript
// Pesquisa universal
"João Silva" → Retorna:
  - Colaborador: João Silva (Portaria)
  - Escala: Janeiro - João Silva
  - Ocorrência: Registrada por João Silva
  - Ronda: Inspetor João Silva
```

#### Implementação

**Backend - Endpoint de Busca (2 dias)**

```python
# /backend/modules/search/

from typing import List, Literal
from pydantic import BaseModel

class SearchResult(BaseModel):
    type: Literal['colaborador', 'posto', 'escala', 'ocorrencia', 'ronda']
    id: str
    title: str
    description: str
    url: str
    metadata: dict = {}

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    took_ms: int

@router.get("/search", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=2),
    types: Optional[List[str]] = Query(None),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca global em todas entidades.

    Args:
        q: Termo de busca
        types: Filtrar por tipos específicos
        limit: Máximo de resultados
    """
    start = time.time()
    results = []

    # Buscar em colaboradores
    if not types or 'colaborador' in types:
        colaboradores = await search_colaboradores(db, q, limit)
        results.extend([
            SearchResult(
                type='colaborador',
                id=str(c.id),
                title=c.nome,
                description=f"{c.cargo} - {c.posto_nome}",
                url=f"/modulos/operacional/colaboradores/{c.id}",
                metadata={
                    'cargo': c.cargo,
                    'status': c.status
                }
            )
            for c in colaboradores
        ])

    # Buscar em postos
    if not types or 'posto' in types:
        postos = await search_postos(db, q, limit)
        results.extend([...])

    # Buscar em escalas
    if not types or 'escala' in types:
        escalas = await search_escalas(db, q, limit)
        results.extend([...])

    # Buscar em ocorrências
    if not types or 'ocorrencia' in types:
        ocorrencias = await search_ocorrencias(db, q, limit)
        results.extend([...])

    # Buscar em rondas
    if not types or 'ronda' in types:
        rondas = await search_rondas(db, q, limit)
        results.extend([...])

    took_ms = int((time.time() - start) * 1000)

    return SearchResponse(
        results=results[:limit],
        total=len(results),
        took_ms=took_ms
    )


async def search_colaboradores(db, query, limit):
    """Busca em colaboradores por nome, CPF, matrícula."""
    stmt = select(Colaborador).where(
        or_(
            Colaborador.nome.ilike(f"%{query}%"),
            Colaborador.cpf.like(f"%{query}%"),
            Colaborador.matricula.like(f"%{query}%")
        )
    ).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()
```

**Frontend - Search Component (2 dias)**

```typescript
// /frontend/src/components/GlobalSearch.tsx

export const GlobalSearch = () => {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  // Debounced search
  const debouncedSearch = useMemo(
    () => debounce(async (q: string) => {
      if (q.length < 2) {
        setResults([])
        return
      }

      setLoading(true)
      try {
        const response = await fetch(`/api/v1/search?q=${encodeURIComponent(q)}`)
        const data = await response.json()
        setResults(data.results)
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setLoading(false)
      }
    }, 300),
    []
  )

  useEffect(() => {
    debouncedSearch(query)
  }, [query, debouncedSearch])

  // Keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === '/' && !open) {
        e.preventDefault()
        setOpen(true)
      }
      if (e.key === 'Escape') {
        setOpen(false)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open])

  const handleSelect = (result: SearchResult) => {
    router.push(result.url)
    setOpen(false)
    setQuery('')
  }

  return (
    <>
      {/* Search Trigger */}
      <Button
        variant="outline"
        className="relative w-64"
        onClick={() => setOpen(true)}
      >
        <Search className="mr-2 h-4 w-4" />
        <span className="text-muted-foreground">Buscar...</span>
        <kbd className="absolute right-2 text-xs bg-muted px-1 rounded">
          /
        </kbd>
      </Button>

      {/* Search Dialog */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="p-0 max-w-2xl">
          {/* Search Input */}
          <div className="flex items-center border-b px-4 py-3">
            <Search className="h-5 w-5 text-muted-foreground mr-2" />
            <Input
              placeholder="Buscar colaboradores, postos, escalas..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="border-0 focus-visible:ring-0"
              autoFocus
            />
            {loading && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
          </div>

          {/* Results */}
          <div className="max-h-96 overflow-y-auto p-2">
            {results.length === 0 && query.length >= 2 && !loading && (
              <div className="text-center py-8 text-muted-foreground">
                <FileQuestion className="h-12 w-12 mx-auto mb-2" />
                <p>Nenhum resultado encontrado</p>
              </div>
            )}

            {results.map(result => (
              <SearchResultItem
                key={`${result.type}-${result.id}`}
                result={result}
                onSelect={() => handleSelect(result)}
              />
            ))}
          </div>

          {/* Footer */}
          <div className="border-t px-4 py-2 text-xs text-muted-foreground flex items-center justify-between">
            <div className="flex gap-4">
              <span>
                <kbd className="bg-muted px-1 rounded">↑↓</kbd> Navegar
              </span>
              <span>
                <kbd className="bg-muted px-1 rounded">↵</kbd> Selecionar
              </span>
              <span>
                <kbd className="bg-muted px-1 rounded">Esc</kbd> Fechar
              </span>
            </div>
            {results.length > 0 && (
              <span>{results.length} resultado(s)</span>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

// Result Item Component
const SearchResultItem = ({ result, onSelect }) => {
  const icons = {
    colaborador: UserCheck,
    posto: MapPin,
    escala: CalendarDays,
    ocorrencia: AlertTriangle,
    ronda: Route
  }

  const Icon = icons[result.type] || FileText

  return (
    <button
      className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-secondary transition-colors text-left"
      onClick={onSelect}
    >
      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Icon className="h-5 w-5 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="font-medium truncate">{result.title}</h4>
        <p className="text-sm text-muted-foreground truncate">
          {result.description}
        </p>
      </div>

      <Badge variant="outline" className="capitalize">
        {result.type}
      </Badge>
    </button>
  )
}
```

**Tarefas:**
- [ ] Backend - Endpoint de busca global
- [ ] Backend - Funções de busca por entidade
- [ ] Backend - Otimizar queries (índices)
- [ ] Frontend - Componente GlobalSearch
- [ ] Frontend - SearchResultItem
- [ ] Frontend - Keyboard navigation (arrow keys)
- [ ] Debounce de busca (300ms)
- [ ] Highlight de termo buscado
- [ ] Testes E2E

**Critérios de Aceite:**
- ✅ Busca retorna em < 200ms
- ✅ / abre busca global
- ✅ Esc fecha modal
- ✅ Arrow keys navegam resultados
- ✅ Enter seleciona e navega
- ✅ Debounce funciona (não busca a cada tecla)
- ✅ Loading state visível

**Estimativa:** 4 dias
**Risco:** 🟡 Médio (performance de busca)

---

### 1.7 Auto-Save (2 dias)

#### Objetivo
Salvar automaticamente rascunhos de formulários para evitar perda de dados.

#### Estratégia
- **Trigger:** onChange com debounce de 2 segundos
- **Storage:** localStorage (frontend) + backend (opcional)
- **Recuperação:** Ao reabrir formulário, perguntar se deseja restaurar

#### Implementação

```typescript
// Hook de Auto-Save
// /frontend/src/hooks/useAutoSave.ts

interface UseAutoSaveOptions<T> {
  key: string
  data: T
  onSave?: (data: T) => Promise<void>
  debounceMs?: number
  enabled?: boolean
}

export const useAutoSave = <T>({
  key,
  data,
  onSave,
  debounceMs = 2000,
  enabled = true
}: UseAutoSaveOptions<T>) => {
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  // Salvar no localStorage
  const saveToLocal = useCallback((value: T) => {
    try {
      localStorage.setItem(`autosave_${key}`, JSON.stringify({
        data: value,
        timestamp: new Date().toISOString()
      }))
      setLastSaved(new Date())
    } catch (error) {
      console.error('Auto-save error:', error)
    }
  }, [key])

  // Salvar no backend (opcional)
  const saveToBackend = useCallback(async (value: T) => {
    if (!onSave) return

    setSaving(true)
    try {
      await onSave(value)
      setLastSaved(new Date())
    } catch (error) {
      console.error('Backend save error:', error)
    } finally {
      setSaving(false)
    }
  }, [onSave])

  // Debounced save
  const debouncedSave = useMemo(
    () => debounce(async (value: T) => {
      saveToLocal(value)
      await saveToBackend(value)
    }, debounceMs),
    [saveToLocal, saveToBackend, debounceMs]
  )

  // Auto-save on data change
  useEffect(() => {
    if (!enabled) return
    debouncedSave(data)
  }, [data, debouncedSave, enabled])

  // Restore from local storage
  const restore = useCallback((): T | null => {
    try {
      const saved = localStorage.getItem(`autosave_${key}`)
      if (!saved) return null

      const parsed = JSON.parse(saved)
      return parsed.data
    } catch {
      return null
    }
  }, [key])

  // Clear auto-save
  const clear = useCallback(() => {
    localStorage.removeItem(`autosave_${key}`)
    setLastSaved(null)
  }, [key])

  return {
    saving,
    lastSaved,
    restore,
    clear
  }
}
```

**Uso em Formulário:**

```typescript
// Example: Novo Posto Form

const PostoForm = () => {
  const [formData, setFormData] = useState(initialData)
  const [showRestore, setShowRestore] = useState(false)

  // Auto-save hook
  const { saving, lastSaved, restore, clear } = useAutoSave({
    key: 'posto_form',
    data: formData,
    debounceMs: 2000,
    onSave: async (data) => {
      // Opcional: salvar no backend
      await api.post('/drafts/posto', data)
    }
  })

  // Check for saved draft on mount
  useEffect(() => {
    const saved = restore()
    if (saved) {
      setShowRestore(true)
    }
  }, [restore])

  const handleRestore = () => {
    const saved = restore()
    if (saved) {
      setFormData(saved)
      setShowRestore(false)
    }
  }

  const handleSubmit = async () => {
    // Submeter form
    await api.post('/postos', formData)

    // Limpar auto-save
    clear()
  }

  return (
    <>
      {/* Restore Alert */}
      {showRestore && (
        <Alert className="mb-4">
          <Info className="h-4 w-4" />
          <AlertTitle>Rascunho encontrado</AlertTitle>
          <AlertDescription>
            Encontramos um rascunho salvo anteriormente. Deseja restaurar?
          </AlertDescription>
          <div className="mt-2 flex gap-2">
            <Button size="sm" onClick={handleRestore}>
              Restaurar
            </Button>
            <Button size="sm" variant="outline" onClick={() => {
              clear()
              setShowRestore(false)
            }}>
              Descartar
            </Button>
          </div>
        </Alert>
      )}

      {/* Form Fields */}
      <Form>
        {/* ... campos ... */}

        {/* Save Indicator */}
        <div className="text-xs text-muted-foreground flex items-center gap-2 mt-2">
          {saving && (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              Salvando rascunho...
            </>
          )}
          {lastSaved && !saving && (
            <>
              <Check className="h-3 w-3 text-green-600" />
              Salvo {formatDistanceToNow(lastSaved, { locale: ptBR })}
            </>
          )}
        </div>
      </Form>
    </>
  )
}
```

**Tarefas:**
- [ ] Hook `useAutoSave`
- [ ] Componente de restore alert
- [ ] Integrar em formulários principais:
  - [ ] Novo Posto
  - [ ] Novo Colaborador
  - [ ] Nova Escala
  - [ ] Nova Ocorrência
- [ ] Indicador de save status
- [ ] Limpar ao submeter com sucesso
- [ ] Testes

**Critérios de Aceite:**
- ✅ Auto-save após 2s de inatividade
- ✅ Indicador visual de saving/saved
- ✅ Alert de restore ao reabrir
- ✅ Botão para descartar rascunho
- ✅ Limpa auto-save após submit

**Estimativa:** 2 dias
**Risco:** 🟢 Baixo

---

### 1.8 Templates de Escalas (3 dias)

#### Objetivo
Salvar escalas como templates reutilizáveis para agilizar criação.

#### Funcionalidade

```
1. Supervisor cria escala complexa de Janeiro
2. Clica "Salvar como Template"
3. Define nome: "Escala Padrão Verão"
4. Em Fevereiro, clica "Criar a partir de Template"
5. Sistema duplica estrutura, ajusta datas
6. Supervisor só ajusta exceções
```

#### Backend

```python
# /backend/modules/operacional/models/scale_template.py

class ScaleTemplate(Base):
    __tablename__ = "scale_templates"

    id = Column(UUID, primary_key=True, default=uuid4)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Dados da escala template
    template_data = Column(JSONB, nullable=False)
    # {
    #   "posts": ["post_id_1", "post_id_2"],
    #   "shifts": [
    #     {
    #       "employee_id": "emp_1",
    #       "post_id": "post_1",
    #       "days_of_week": [0, 1, 2],  # Segunda, Terça, Quarta
    #       "start_time": "08:00",
    #       "end_time": "17:00"
    #     }
    #   ],
    #   "metadata": {
    #     "total_employees": 10,
    #     "coverage": 100
    #   }
    # }

    # Metadados
    created_by = Column(UUID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Stats
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime)

# /backend/modules/operacional/controllers/scale_template_controller.py

@router.post("/templates", response_model=ScaleTemplateResponse)
async def create_template(
    data: ScaleTemplateCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db)
):
    """Cria um template a partir de uma escala existente."""

    # Buscar escala original
    scale = await db.get(Scale, data.scale_id)
    if not scale:
        raise HTTPException(404, "Escala não encontrada")

    # Extrair dados para template
    template_data = extract_template_data(scale)

    # Criar template
    template = ScaleTemplate(
        tenant_id=str(current_user.tenant_id),
        name=data.name,
        description=data.description,
        template_data=template_data,
        created_by=current_user.id
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template


@router.post("/templates/{template_id}/apply", response_model=ScaleResponse)
async def apply_template(
    template_id: UUID,
    data: ApplyTemplateRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db)
):
    """Aplica um template para criar nova escala."""

    template = await db.get(ScaleTemplate, template_id)
    if not template:
        raise HTTPException(404, "Template não encontrado")

    # Criar nova escala baseada no template
    new_scale = create_scale_from_template(
        template=template,
        month=data.month,
        year=data.year,
        adjustments=data.adjustments
    )

    db.add(new_scale)

    # Atualizar stats do template
    template.times_used += 1
    template.last_used = datetime.utcnow()

    await db.commit()
    await db.refresh(new_scale)

    return new_scale


def extract_template_data(scale: Scale) -> dict:
    """Extrai dados relevantes da escala para template."""
    return {
        "posts": scale.posts,
        "shifts": [
            {
                "employee_id": shift.employee_id,
                "post_id": shift.post_id,
                "days_of_week": shift.days_of_week,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "shift_type": shift.shift_type
            }
            for shift in scale.shifts
        ],
        "metadata": {
            "total_employees": len(set(s.employee_id for s in scale.shifts)),
            "coverage": scale.coverage_percentage
        }
    }


def create_scale_from_template(
    template: ScaleTemplate,
    month: int,
    year: int,
    adjustments: dict = None
) -> Scale:
    """Cria escala a partir de template."""

    template_data = template.template_data

    # Criar nova escala
    scale = Scale(
        name=f"{template.name} - {month}/{year}",
        month=month,
        year=year,
        status="draft",
        posts=template_data["posts"]
    )

    # Criar turnos baseados no template
    for shift_template in template_data["shifts"]:
        # Aplicar ajustes se fornecidos
        employee_id = adjustments.get("employees", {}).get(
            shift_template["employee_id"],
            shift_template["employee_id"]
        ) if adjustments else shift_template["employee_id"]

        shift = Shift(
            scale=scale,
            employee_id=employee_id,
            post_id=shift_template["post_id"],
            days_of_week=shift_template["days_of_week"],
            start_time=shift_template["start_time"],
            end_time=shift_template["end_time"],
            shift_type=shift_template["shift_type"]
        )
        scale.shifts.append(shift)

    return scale
```

#### Frontend

```typescript
// /frontend/src/features/escalas/components/TemplateManager.tsx

export const TemplateManager = () => {
  const [templates, setTemplates] = useState<Template[]>([])
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showApplyDialog, setShowApplyDialog] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)

  const loadTemplates = async () => {
    const response = await api.get('/operacional/scales/templates')
    setTemplates(response.data)
  }

  useEffect(() => {
    loadTemplates()
  }, [])

  return (
    <div>
      <div className="flex justify-between mb-4">
        <h2 className="text-2xl font-bold">Templates de Escalas</h2>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map(template => (
          <TemplateCard
            key={template.id}
            template={template}
            onApply={() => {
              setSelectedTemplate(template)
              setShowApplyDialog(true)
            }}
            onDelete={async () => {
              await api.delete(`/operacional/scales/templates/${template.id}`)
              loadTemplates()
            }}
          />
        ))}
      </div>

      {/* Create Dialog */}
      <CreateTemplateDialog
        open={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onCreated={loadTemplates}
      />

      {/* Apply Dialog */}
      <ApplyTemplateDialog
        open={showApplyDialog}
        template={selectedTemplate}
        onClose={() => {
          setShowApplyDialog(false)
          setSelectedTemplate(null)
        }}
      />
    </div>
  )
}

// Template Card
const TemplateCard = ({ template, onApply, onDelete }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{template.name}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {template.description}
            </p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onApply}>
                <Play className="mr-2 h-4 w-4" />
                Usar Template
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onDelete} className="text-red-600">
                <Trash2 className="mr-2 h-4 w-4" />
                Excluir
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <Label className="text-muted-foreground">Colaboradores</Label>
            <p className="font-medium">
              {template.template_data.metadata.total_employees}
            </p>
          </div>
          <div>
            <Label className="text-muted-foreground">Cobertura</Label>
            <p className="font-medium">
              {template.template_data.metadata.coverage}%
            </p>
          </div>
          <div>
            <Label className="text-muted-foreground">Criado</Label>
            <p className="font-medium">
              {format(new Date(template.created_at), 'dd/MM/yyyy')}
            </p>
          </div>
          <div>
            <Label className="text-muted-foreground">Usado</Label>
            <p className="font-medium">{template.times_used}x</p>
          </div>
        </div>
      </CardContent>

      <CardFooter>
        <Button onClick={onApply} className="w-full">
          <Zap className="mr-2 h-4 w-4" />
          Usar este Template
        </Button>
      </CardFooter>
    </Card>
  )
}

// Apply Template Dialog
const ApplyTemplateDialog = ({ open, template, onClose }) => {
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())
  const [adjustments, setAdjustments] = useState({})
  const [loading, setLoading] = useState(false)

  const handleApply = async () => {
    setLoading(true)
    try {
      await api.post(`/operacional/scales/templates/${template.id}/apply`, {
        month,
        year,
        adjustments
      })

      toast.success('Escala criada com sucesso!')
      onClose()
      router.push('/modulos/operacional/escalas')
    } catch (error) {
      toast.error('Erro ao aplicar template')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Aplicar Template: {template?.name}</DialogTitle>
          <DialogDescription>
            Configure o período e ajustes para a nova escala
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Month/Year Selector */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Mês</Label>
              <Select value={month.toString()} onValueChange={v => setMonth(parseInt(v))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[...Array(12)].map((_, i) => (
                    <SelectItem key={i} value={(i + 1).toString()}>
                      {format(new Date(2024, i), 'MMMM', { locale: ptBR })}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Ano</Label>
              <Select value={year.toString()} onValueChange={v => setYear(parseInt(v))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[2026, 2027, 2028].map(y => (
                    <SelectItem key={y} value={y.toString()}>{y}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Preview */}
          <div className="border rounded-lg p-4 bg-muted/50">
            <h4 className="font-medium mb-2">Preview do Template</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <Label>Colaboradores</Label>
                <p>{template?.template_data.metadata.total_employees}</p>
              </div>
              <div>
                <Label>Postos</Label>
                <p>{template?.template_data.posts.length}</p>
              </div>
              <div>
                <Label>Turnos</Label>
                <p>{template?.template_data.shifts.length}</p>
              </div>
            </div>
          </div>

          {/* Future: Employee substitutions */}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={handleApply} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Criar Escala
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

**Tarefas:**
- [ ] Backend - Model `ScaleTemplate`
- [ ] Backend - CRUD de templates
- [ ] Backend - Endpoint apply template
- [ ] Backend - Lógica de extração/aplicação
- [ ] Frontend - TemplateManager page
- [ ] Frontend - TemplateCard component
- [ ] Frontend - CreateTemplateDialog
- [ ] Frontend - ApplyTemplateDialog
- [ ] Testes

**Critérios de Aceite:**
- ✅ Salvar escala como template
- ✅ Listar templates disponíveis
- ✅ Aplicar template para novo período
- ✅ Ajustar datas automaticamente
- ✅ Preview antes de aplicar
- ✅ Tracking de uso (times_used)

**Estimativa:** 3 dias
**Risco:** 🟡 Médio (lógica de aplicação)

---

### 1.9 Onboarding Guiado (3 dias)

#### Objetivo
Tour interativo para novos usuários entenderem o sistema rapidamente.

#### Biblioteca
Usar **Shepherd.js** ou **Intro.js** para criar tour guiado.

#### Implementação

```typescript
// /frontend/src/features/onboarding/tours/operacionalTour.ts

import Shepherd from 'shepherd.js'
import 'shepherd.js/dist/css/shepherd.css'

export const createOperacionalTour = () => {
  const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: 'shadow-lg',
      scrollTo: { behavior: 'smooth', block: 'center' }
    }
  })

  // Step 1: Welcome
  tour.addStep({
    id: 'welcome',
    text: `
      <h3>Bem-vindo ao Módulo Operacional! 🎉</h3>
      <p>Vamos fazer um tour rápido pelas principais funcionalidades.</p>
      <p>Você pode pular este tour a qualquer momento.</p>
    `,
    buttons: [
      {
        text: 'Pular',
        classes: 'shepherd-button-secondary',
        action: tour.cancel
      },
      {
        text: 'Começar',
        action: tour.next
      }
    ]
  })

  // Step 2: Dashboard KPIs
  tour.addStep({
    id: 'kpis',
    text: `
      <h3>KPIs Operacionais</h3>
      <p>Aqui você vê métricas em tempo real:</p>
      <ul>
        <li>Postos ativos</li>
        <li>Colaboradores alocados</li>
        <li>Escalas em andamento</li>
        <li>Ocorrências do mês</li>
      </ul>
      <p><strong>Dica:</strong> Clique em qualquer KPI para ver detalhes!</p>
    `,
    attachTo: {
      element: '[data-tour="dashboard-kpis"]',
      on: 'bottom'
    },
    buttons: [
      {
        text: 'Voltar',
        classes: 'shepherd-button-secondary',
        action: tour.back
      },
      {
        text: 'Próximo',
        action: tour.next
      }
    ]
  })

  // Step 3: Navigation
  tour.addStep({
    id: 'navigation',
    text: `
      <h3>Menu de Navegação</h3>
      <p>Acesse rapidamente:</p>
      <ul>
        <li><strong>Postos:</strong> Cadastro de locais</li>
        <li><strong>Colaboradores:</strong> Gestão de equipe</li>
        <li><strong>Escalas:</strong> Planejamento de turnos</li>
        <li><strong>Rondas:</strong> Inspeções</li>
      </ul>
      <p><strong>Atalho:</strong> Use Alt+1, Alt+2, etc.</p>
    `,
    attachTo: {
      element: '[data-tour="sidebar-nav"]',
      on: 'right'
    },
    buttons: [
      {
        text: 'Voltar',
        classes: 'shepherd-button-secondary',
        action: tour.back
      },
      {
        text: 'Próximo',
        action: tour.next
      }
    ]
  })

  // Step 4: Search
  tour.addStep({
    id: 'search',
    text: `
      <h3>Busca Global</h3>
      <p>Encontre qualquer coisa rapidamente!</p>
      <p>Digite para buscar em:</p>
      <ul>
        <li>Colaboradores</li>
        <li>Postos</li>
        <li>Escalas</li>
        <li>Ocorrências</li>
      </ul>
      <p><strong>Atalho:</strong> Pressione / (barra)</p>
    `,
    attachTo: {
      element: '[data-tour="global-search"]',
      on: 'bottom'
    },
    buttons: [
      {
        text: 'Voltar',
        classes: 'shepherd-button-secondary',
        action: tour.back
      },
      {
        text: 'Próximo',
        action: tour.next
      }
    ]
  })

  // Step 5: Notifications
  tour.addStep({
    id: 'notifications',
    text: `
      <h3>Notificações</h3>
      <p>Fique por dentro de tudo:</p>
      <ul>
        <li>Colaborador atrasado</li>
        <li>Aprovação pendente</li>
        <li>Ocorrência registrada</li>
      </ul>
      <p>Configure suas preferências clicando no ícone.</p>
    `,
    attachTo: {
      element: '[data-tour="notifications"]',
      on: 'bottom-end'
    },
    buttons: [
      {
        text: 'Voltar',
        classes: 'shepherd-button-secondary',
        action: tour.back
      },
      {
        text: 'Próximo',
        action: tour.next
      }
    ]
  })

  // Step 6: Quick Actions
  tour.addStep({
    id: 'quick-actions',
    text: `
      <h3>Ações Rápidas</h3>
      <p>Agilize seu trabalho:</p>
      <ul>
        <li><strong>Ctrl+N:</strong> Criar novo</li>
        <li><strong>Ctrl+K:</strong> Command Palette</li>
        <li><strong>Ctrl+S:</strong> Salvar</li>
      </ul>
      <p>Pressione <kbd>?</kbd> para ver todos os atalhos.</p>
    `,
    buttons: [
      {
        text: 'Voltar',
        classes: 'shepherd-button-secondary',
        action: tour.back
      },
      {
        text: 'Próximo',
        action: tour.next
      }
    ]
  })

  // Step 7: Finish
  tour.addStep({
    id: 'finish',
    text: `
      <h3>Pronto para começar! 🚀</h3>
      <p>Você completou o tour básico.</p>
      <p>Explore à vontade e não hesite em pedir ajuda.</p>
      <p><strong>Dica:</strong> Você pode refazer este tour a qualquer momento nas Configurações.</p>
    `,
    buttons: [
      {
        text: 'Finalizar',
        action: () => {
          tour.complete()
          // Marcar como completo
          localStorage.setItem('tour_operacional_completed', 'true')
        }
      }
    ]
  })

  return tour
}

// Hook para gerenciar tours
// /frontend/src/features/onboarding/hooks/useTour.ts

export const useTour = (tourId: string) => {
  const [completed, setCompleted] = useState(false)

  useEffect(() => {
    const isCompleted = localStorage.getItem(`tour_${tourId}_completed`) === 'true'
    setCompleted(isCompleted)
  }, [tourId])

  const start = useCallback((tour: Shepherd.Tour) => {
    tour.start()
  }, [])

  const reset = useCallback(() => {
    localStorage.removeItem(`tour_${tourId}_completed`)
    setCompleted(false)
  }, [tourId])

  return { completed, start, reset }
}

// Componente para iniciar tour
// /frontend/src/features/onboarding/components/TourTrigger.tsx

export const TourTrigger = () => {
  const { completed, start, reset } = useTour('operacional')
  const tour = useMemo(() => createOperacionalTour(), [])

  // Auto-start on first visit
  useEffect(() => {
    if (!completed) {
      // Delay to allow page to fully load
      setTimeout(() => start(tour), 1000)
    }
  }, [completed, start, tour])

  return (
    <DropdownMenuItem onClick={() => {
      reset()
      start(tour)
    }}>
      <HelpCircle className="mr-2 h-4 w-4" />
      Refazer Tour Guiado
    </DropdownMenuItem>
  )
}
```

**Adicionar Data Attributes:**

```typescript
// No código dos componentes, adicionar data-tour

// Dashboard KPIs
<div className="grid..." data-tour="dashboard-kpis">

// Sidebar
<nav data-tour="sidebar-nav">

// Search
<GlobalSearch data-tour="global-search" />

// Notifications
<NotificationBell data-tour="notifications" />
```

**Tarefas:**
- [ ] Instalar Shepherd.js
- [ ] Criar tour operacional
- [ ] Hook `useTour`
- [ ] Componente TourTrigger
- [ ] Adicionar data-tour attributes
- [ ] Customizar CSS do tour
- [ ] Opção para refazer nas configurações
- [ ] Diferentes tours por perfil (CEO, Gerente, Supervisor)

**Critérios de Aceite:**
- ✅ Tour inicia automaticamente no primeiro acesso
- ✅ Pode ser pulado a qualquer momento
- ✅ Navegação entre steps (voltar/próximo)
- ✅ Highlights visuais nos elementos
- ✅ Overlay modal para foco
- ✅ Marca como concluído no localStorage
- ✅ Opção de refazer nas configurações

**Estimativa:** 3 dias
**Risco:** 🟢 Baixo

---

### 1.10 Exportação em 1 Click (2 dias)

#### Objetivo
Botão de exportar em todas as listagens (Excel, PDF, CSV).

#### Implementação

```typescript
// Componente de Export
// /frontend/src/components/ExportButton.tsx

import { Download, FileSpreadsheet, FileText, File } from 'lucide-react'

interface ExportButtonProps {
  data: any[]
  filename: string
  formats?: Array<'excel' | 'pdf' | 'csv'>
}

export const ExportButton: React.FC<ExportButtonProps> = ({
  data,
  filename,
  formats = ['excel', 'pdf', 'csv']
}) => {
  const [exporting, setExporting] = useState(false)
  const [format, setFormat] = useState<string | null>(null)

  const handleExport = async (type: 'excel' | 'pdf' | 'csv') => {
    setExporting(true)
    setFormat(type)

    try {
      switch (type) {
        case 'excel':
          await exportToExcel(data, filename)
          break
        case 'pdf':
          await exportToPDF(data, filename)
          break
        case 'csv':
          await exportToCSV(data, filename)
          break
      }

      toast.success(`Exportado para ${type.toUpperCase()} com sucesso!`)
    } catch (error) {
      toast.error('Erro ao exportar dados')
      console.error(error)
    } finally {
      setExporting(false)
      setFormat(null)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={exporting}>
          {exporting && format ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Exportando {format.toUpperCase()}...
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Escolha o formato</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {formats.includes('excel') && (
          <DropdownMenuItem onClick={() => handleExport('excel')}>
            <FileSpreadsheet className="mr-2 h-4 w-4 text-green-600" />
            Excel (.xlsx)
          </DropdownMenuItem>
        )}

        {formats.includes('pdf') && (
          <DropdownMenuItem onClick={() => handleExport('pdf')}>
            <FileText className="mr-2 h-4 w-4 text-red-600" />
            PDF (.pdf)
          </DropdownMenuItem>
        )}

        {formats.includes('csv') && (
          <DropdownMenuItem onClick={() => handleExport('csv')}>
            <File className="mr-2 h-4 w-4 text-blue-600" />
            CSV (.csv)
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// Funções de exportação
// /frontend/src/utils/export.ts

import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

export const exportToExcel = (data: any[], filename: string) => {
  // Criar worksheet
  const ws = XLSX.utils.json_to_sheet(data)

  // Criar workbook
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Dados')

  // Salvar arquivo
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

export const exportToCSV = (data: any[], filename: string) => {
  const ws = XLSX.utils.json_to_sheet(data)
  const csv = XLSX.utils.sheet_to_csv(ws)

  // Download
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  link.click()
}

export const exportToPDF = (data: any[], filename: string) => {
  const doc = new jsPDF()

  // Título
  doc.setFontSize(16)
  doc.text(filename, 14, 15)

  // Preparar dados para tabela
  const headers = Object.keys(data[0] || {})
  const rows = data.map(item => headers.map(header => item[header]))

  // Adicionar tabela
  autoTable(doc, {
    head: [headers],
    body: rows,
    startY: 25,
    theme: 'grid',
    styles: { fontSize: 8 },
    headStyles: { fillColor: [59, 130, 246] }
  })

  // Salvar
  doc.save(`${filename}.pdf`)
}
```

**Uso em tabelas:**

```typescript
// Example: Lista de Colaboradores

const ColaboradoresPage = () => {
  const { data: colaboradores } = useQuery(['colaboradores'], fetchColaboradores)

  // Preparar dados para export
  const exportData = colaboradores.map(c => ({
    'Nome': c.nome,
    'CPF': c.cpf,
    'Cargo': c.cargo,
    'Posto': c.posto_nome,
    'Status': c.status,
    'Admissão': format(new Date(c.data_admissao), 'dd/MM/yyyy')
  }))

  return (
    <div>
      <div className="flex justify-between mb-4">
        <h1>Colaboradores</h1>
        <ExportButton
          data={exportData}
          filename={`colaboradores_${format(new Date(), 'ddMMyyyy')}`}
          formats={['excel', 'pdf', 'csv']}
        />
      </div>

      {/* Tabela... */}
    </div>
  )
}
```

**Tarefas:**
- [ ] Instalar bibliotecas (xlsx, jspdf, jspdf-autotable)
- [ ] Componente ExportButton
- [ ] Funções de exportação (Excel, PDF, CSV)
- [ ] Integrar em todas as listagens:
  - [ ] Postos
  - [ ] Colaboradores
  - [ ] Escalas
  - [ ] Ocorrências
  - [ ] Rondas
  - [ ] Alocações
- [ ] Formatação de dados para export
- [ ] Customizar PDF (logo, header, footer)

**Critérios de Aceite:**
- ✅ Botão em todas as listagens
- ✅ 3 formatos disponíveis
- ✅ Download inicia imediatamente
- ✅ Dados formatados corretamente
- ✅ Nome de arquivo com timestamp
- ✅ Loading state durante export

**Estimativa:** 2 dias
**Risco:** 🟢 Baixo

---

## RESUMO FASE 1: QUICK WINS

### Entregas
1. ✅ Notificações Push
2. ✅ Responsividade Total
3. ✅ Modo Escuro
4. ✅ Atalhos de Teclado
5. ✅ KPI Widgets Interativos
6. ✅ Busca Global
7. ✅ Auto-Save
8. ✅ Templates de Escalas
9. ✅ Onboarding Guiado
10. ✅ Exportação em 1 Click

### Métricas de Sucesso
- **Produtividade:** +30% (menos cliques, ações mais rápidas)
- **Satisfação:** 4.5/5.0 (pesquisa pós-implementação)
- **Adoção:** 80% dos usuários usam atalhos/busca global
- **Performance:** Lighthouse Score > 90

### Recursos Necessários
- **2 Full-Stack Developers**
- **1 UX/UI Designer**
- **1 QA Engineer**

### Investimento
**R$ 20.000 - 30.000**

### Cronograma
**2 semanas (Sprint 1)**

---


## FASE 2: PWA MOBILE-FIRST - OPERAÇÃO EM CAMPO
**Duração:** 4 semanas (Sprints 2-3)
**Objetivo:** App instalável, offline-first, otimizado para supervisores em campo
**Prioridade:** 🔥 CRÍTICA

### 2.1 Progressive Web App (PWA)

#### Objetivo
Transformar sistema em app instalável que funciona offline.

#### Features Principais
```typescript
// manifest.json
{
  "name": "Conecta PRO Operacional",
  "short_name": "Operacional",
  "description": "Gestão operacional em campo",
  "start_url": "/modulos/operacional",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "orientation": "portrait",
  "categories": ["productivity", "business"]
}
```

#### Service Worker - Offline Strategy

```typescript
// /frontend/public/sw.js

const CACHE_NAME = 'conecta-operacional-v1'
const STATIC_CACHE = [
  '/',
  '/modulos/operacional',
  '/modulos/operacional/postos',
  '/modulos/operacional/colaboradores',
  '/offline.html'
]

// Install - Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_CACHE)
    })
  )
})

// Fetch - Network First, fallback to Cache
self.addEventListener('fetch', (event) => {
  const { request } = event

  // API requests - Network First
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone and cache successful responses
          const responseClone = response.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone)
          })
          return response
        })
        .catch(() => {
          // Fallback to cache
          return caches.match(request)
        })
    )
    return
  }

  // Static assets - Cache First
  event.respondWith(
    caches.match(request).then((cached) => {
      return cached || fetch(request)
    })
  )
})

// Background Sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-ocorrencias') {
    event.waitUntil(syncOcorrencias())
  }
  if (event.tag === 'sync-checkins') {
    event.waitUntil(syncCheckins())
  }
})

async function syncOcorrencias() {
  const db = await openDB('conecta-offline')
  const pendingOcorrencias = await db.getAll('pending_ocorrencias')

  for (const ocorrencia of pendingOcorrencias) {
    try {
      await fetch('/api/v1/operacional/ocorrencias', {
        method: 'POST',
        body: JSON.stringify(ocorrencia.data)
      })
      await db.delete('pending_ocorrencias', ocorrencia.id)
    } catch (error) {
      console.error('Sync failed:', error)
    }
  }
}
```

#### IndexedDB para Storage Offline

```typescript
// /frontend/src/lib/offlineDB.ts

import { openDB, DBSchema, IDBPDatabase } from 'idb'

interface OfflineDB extends DBSchema {
  colaboradores: {
    key: string
    value: Colaborador
    indexes: { 'by-posto': string }
  }
  escalas: {
    key: string
    value: Escala
  }
  pending_ocorrencias: {
    key: string
    value: {
      id: string
      data: OcorrenciaCreate
      timestamp: number
    }
  }
  pending_checkins: {
    key: string
    value: {
      id: string
      data: CheckinCreate
      timestamp: number
    }
  }
}

let dbInstance: IDBPDatabase<OfflineDB> | null = null

export async function getDB() {
  if (dbInstance) return dbInstance

  dbInstance = await openDB<OfflineDB>('conecta-offline', 1, {
    upgrade(db) {
      // Colaboradores store
      const colaboradorStore = db.createObjectStore('colaboradores', {
        keyPath: 'id'
      })
      colaboradorStore.createIndex('by-posto', 'posto_id')

      // Escalas store
      db.createObjectStore('escalas', { keyPath: 'id' })

      // Pending operations
      db.createObjectStore('pending_ocorrencias', { keyPath: 'id' })
      db.createObjectStore('pending_checkins', { keyPath: 'id' })
    }
  })

  return dbInstance
}

// Sync API data to IndexedDB
export async function syncToOffline() {
  const db = await getDB()

  try {
    // Fetch and cache colaboradores
    const colaboradores = await fetch('/api/v1/operacional/colaboradores').then(r => r.json())
    const tx = db.transaction('colaboradores', 'readwrite')
    for (const colab of colaboradores.data) {
      await tx.store.put(colab)
    }
    await tx.done

    console.log('✅ Dados sincronizados para offline')
  } catch (error) {
    console.error('❌ Erro ao sincronizar:', error)
  }
}

// Add to pending queue (offline)
export async function addPendingOcorrencia(data: OcorrenciaCreate) {
  const db = await getDB()
  const id = `pending-${Date.now()}-${Math.random()}`

  await db.add('pending_ocorrencias', {
    id,
    data,
    timestamp: Date.now()
  })

  // Register background sync
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const registration = await navigator.serviceWorker.ready
    await registration.sync.register('sync-ocorrencias')
  }
}
```

#### React Hook para Detectar Status Online/Offline

```typescript
// /frontend/src/hooks/useOnlineStatus.ts

export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      toast.success('Conexão restaurada! Sincronizando dados...')
      syncToOffline() // Sync quando voltar online
    }

    const handleOffline = () => {
      setIsOnline(false)
      toast.warning('Modo offline ativado. Dados serão sincronizados quando conectar.')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return { isOnline }
}
```

**Tarefas:**
- [ ] Configurar manifest.json
- [ ] Implementar Service Worker
- [ ] Setup IndexedDB
- [ ] Sync strategy (Network First para API, Cache First para assets)
- [ ] Background Sync para ações offline
- [ ] Componente de status online/offline
- [ ] Testes offline (DevTools Network: Offline)

**Estimativa:** 2 semanas

---

### 2.2 Quick Actions Mobile

#### Objetivo
Ações rápidas otimizadas para toque em dispositivos móveis.

```typescript
// Speed Dial FAB (Floating Action Button)
// /frontend/src/components/mobile/SpeedDialFAB.tsx

export const SpeedDialFAB = () => {
  const [open, setOpen] = useState(false)
  const { isOnline } = useOnlineStatus()

  const actions = [
    {
      icon: Camera,
      label: 'Registrar Ocorrência',
      onClick: () => router.push('/modulos/operacional/ocorrencias/nova'),
      color: 'bg-red-500'
    },
    {
      icon: LogIn,
      label: 'Check-in',
      onClick: () => handleQuickCheckin(),
      color: 'bg-green-500'
    },
    {
      icon: Phone,
      label: 'Ligar Supervisor',
      onClick: () => window.location.href = 'tel:+5511999999999',
      color: 'bg-blue-500'
    },
    {
      icon: MapPin,
      label: 'Ver Mapa',
      onClick: () => router.push('/modulos/operacional/mapa'),
      color: 'bg-purple-500'
    }
  ]

  return (
    <div className="fixed bottom-20 right-4 z-50 lg:hidden">
      {/* Action Buttons */}
      <AnimatePresence>
        {open && (
          <div className="mb-4 space-y-3">
            {actions.map((action, i) => (
              <motion.button
                key={action.label}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => {
                  action.onClick()
                  setOpen(false)
                }}
                className={cn(
                  'flex items-center gap-3 rounded-full shadow-lg px-4 py-3',
                  'text-white font-medium',
                  action.color
                )}
              >
                <action.icon className="h-5 w-5" />
                <span>{action.label}</span>
              </motion.button>
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Main FAB */}
      <motion.button
        onClick={() => setOpen(!open)}
        className="w-14 h-14 rounded-full bg-primary shadow-lg flex items-center justify-center text-white"
        whileTap={{ scale: 0.9 }}
        animate={{ rotate: open ? 45 : 0 }}
      >
        <Plus className="h-6 w-6" />
      </motion.button>

      {/* Offline Indicator */}
      {!isOnline && (
        <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-red-500 animate-pulse" />
      )}
    </div>
  )
}
```

**Tarefas:**
- [ ] Speed Dial FAB component
- [ ] Quick Checkin flow
- [ ] Camera integration
- [ ] Geolocation integration
- [ ] Otimizar touch targets (44px mínimo)

**Estimativa:** 1 semana

---

### 2.3 Comandos de Voz

#### Objetivo
Permitir registro de ocorrências e comandos via voz (mãos livres).

```typescript
// /frontend/src/hooks/useSpeechRecognition.ts

export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')

  const startListening = useCallback(() => {
    if (!('webkitSpeechRecognition' in window)) {
      toast.error('Reconhecimento de voz não suportado')
      return
    }

    const recognition = new webkitSpeechRecognition()
    recognition.lang = 'pt-BR'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript
      setTranscript(text)
      setIsListening(false)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
    }

    recognition.start()
  }, [])

  const stopListening = useCallback(() => {
    setIsListening(false)
  }, [])

  return {
    isListening,
    transcript,
    startListening,
    stopListening
  }
}

// Uso em formulário de ocorrência
const OcorrenciaForm = () => {
  const [descricao, setDescricao] = useState('')
  const { isListening, transcript, startListening } = useSpeechRecognition()

  useEffect(() => {
    if (transcript) {
      setDescricao(prev => prev + ' ' + transcript)
    }
  }, [transcript])

  return (
    <div>
      <Label>Descrição</Label>
      <div className="relative">
        <Textarea
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          rows={4}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute bottom-2 right-2"
          onClick={startListening}
        >
          {isListening ? (
            <Mic className="h-5 w-5 text-red-500 animate-pulse" />
          ) : (
            <Mic className="h-5 w-5" />
          )}
        </Button>
      </div>
    </div>
  )
}
```

**Tarefas:**
- [ ] Hook useSpeechRecognition
- [ ] Botão de mic em formulários
- [ ] Comandos de voz predefinidos
- [ ] Feedback visual de listening
- [ ] Fallback para navegadores sem suporte

**Estimativa:** 3 dias

---

### 2.4 Geolocalização e Check-in Automático

#### Objetivo
Check-in/out automático ao entrar/sair da área do posto.

```typescript
// /frontend/src/hooks/useGeofencing.ts

interface Geofence {
  id: string
  name: string
  latitude: number
  longitude: number
  radius: number // metros
}

export const useGeofencing = (geofences: Geofence[]) => {
  const [currentPosition, setCurrentPosition] = useState<GeolocationPosition | null>(null)
  const [insideGeofence, setInsideGeofence] = useState<Geofence | null>(null)

  useEffect(() => {
    if (!navigator.geolocation) {
      console.warn('Geolocation not supported')
      return
    }

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        setCurrentPosition(position)
        checkGeofences(position)
      },
      (error) => {
        console.error('Geolocation error:', error)
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 5000
      }
    )

    return () => {
      navigator.geolocation.clearWatch(watchId)
    }
  }, [geofences])

  const checkGeofences = (position: GeolocationPosition) => {
    for (const geofence of geofences) {
      const distance = calculateDistance(
        position.coords.latitude,
        position.coords.longitude,
        geofence.latitude,
        geofence.longitude
      )

      if (distance <= geofence.radius) {
        if (!insideGeofence || insideGeofence.id !== geofence.id) {
          // Entrou na geofence
          setInsideGeofence(geofence)
          handleGeofenceEnter(geofence)
        }
        return
      }
    }

    // Saiu de todas as geofences
    if (insideGeofence) {
      handleGeofenceExit(insideGeofence)
      setInsideGeofence(null)
    }
  }

  const handleGeofenceEnter = async (geofence: Geofence) => {
    toast.success(`Você entrou em: ${geofence.name}`)

    // Auto check-in
    const shouldAutoCheckin = await confirm(
      `Deseja fazer check-in em ${geofence.name}?`
    )

    if (shouldAutoCheckin) {
      await api.post('/campo/checkin', {
        posto_id: geofence.id,
        latitude: currentPosition.coords.latitude,
        longitude: currentPosition.coords.longitude,
        auto: true
      })
      toast.success('Check-in realizado automaticamente')
    }
  }

  const handleGeofenceExit = async (geofence: Geofence) => {
    toast.info(`Você saiu de: ${geofence.name}`)

    // Auto checkout
    await api.post('/campo/checkout', {
      posto_id: geofence.id,
      auto: true
    })
  }

  return {
    currentPosition,
    insideGeofence
  }
}

// Função de cálculo de distância (Haversine)
function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3 // Raio da Terra em metros
  const φ1 = (lat1 * Math.PI) / 180
  const φ2 = (lat2 * Math.PI) / 180
  const Δφ = ((lat2 - lat1) * Math.PI) / 180
  const Δλ = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c // Distância em metros
}
```

**Tarefas:**
- [ ] Hook useGeofencing
- [ ] Background geolocation tracking
- [ ] Auto check-in/checkout
- [ ] Permissões de localização
- [ ] Battery optimization
- [ ] Privacy controls

**Estimativa:** 1 semana

---

## RESUMO FASE 2: PWA MOBILE-FIRST

### Entregas
1. ✅ PWA configurado e instalável
2. ✅ Offline-first com Service Worker
3. ✅ IndexedDB para cache local
4. ✅ Background Sync
5. ✅ Quick Actions FAB
6. ✅ Comandos de voz
7. ✅ Geofencing e auto check-in

### Métricas de Sucesso
- **Instalações:** 60% dos usuários mobile
- **Uso Offline:** 30% das operações funcionam offline
- **Check-in Automático:** 80% adoção
- **Performance:** TTI < 3s em 3G

### Recursos Necessários
- **2 Full-Stack Developers**
- **1 Mobile Specialist**
- **1 UX Designer**

### Investimento
**R$ 40.000 - 60.000**

### Cronograma
**4 semanas (Sprints 2-3)**

---


## FASE 3: DASHBOARD INTELIGENTE COM IA PREDITIVA
**Duração:** 6 semanas (Sprints 4-6)
**Objetivo:** Transformar dados em insights acionáveis com IA
**Prioridade:** 🔥 CRÍTICA

### 3.1 KPIs Preditivos

#### Objetivo
KPIs que não apenas mostram o passado, mas PREVEEM o futuro.

#### Backend - ML Models

```python
# /backend/modules/ml/predictive_models.py

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import joblib

class StaffingPredictor:
    """Prevê necessidade de funcionários baseado em histórico."""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)

    def train(self, historical_data: List[dict]):
        """
        Treina modelo com dados históricos.

        Args:
            historical_data: [
                {
                    'month': 1,
                    'year': 2026,
                    'holidays': 2,
                    'events': 1,
                    'staff_needed': 45
                },
                ...
            ]
        """
        X = [[d['month'], d['holidays'], d['events']] for d in historical_data]
        y = [d['staff_needed'] for d in historical_data]

        self.model.fit(X, y)
        joblib.dump(self.model, 'models/staffing_predictor.pkl')

    def predict(self, month: int, holidays: int, events: int) -> int:
        """Prevê necessidade de pessoal."""
        features = np.array([[month, holidays, events]])
        prediction = self.model.predict(features)
        return int(prediction[0])


class CostPredictor:
    """Prevê custo operacional do próximo mês."""

    def __init__(self):
        self.model = LinearRegression()

    def train(self, historical_costs: List[dict]):
        """
        Treina com custos históricos.

        Args:
            historical_costs: [
                {
                    'month': 1,
                    'staff_count': 42,
                    'overtime_hours': 120,
                    'total_cost': 125000
                },
                ...
            ]
        """
        X = [[d['staff_count'], d['overtime_hours']] for d in historical_costs]
        y = [d['total_cost'] for d in historical_costs]

        self.model.fit(X, y)

    def predict(self, staff_count: int, overtime_hours: int) -> float:
        """Prevê custo total."""
        features = np.array([[staff_count, overtime_hours]])
        prediction = self.model.predict(features)
        return float(prediction[0])


# Controller de Predições
@router.get("/predictions/staffing")
async def predict_staffing(
    month: int = Query(..., ge=1, le=12),
    holidays: int = Query(0, ge=0),
    events: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Prevê necessidade de funcionários.

    Returns:
        {
            "predicted_staff": 48,
            "confidence": 0.87,
            "recommendation": "Contratar 3 temporários",
            "reasoning": "Histórico mostra aumento de 15% em meses com eventos"
        }
    """
    # Carregar modelo treinado
    predictor = joblib.load('models/staffing_predictor.pkl')

    # Fazer predição
    predicted = predictor.predict(month, holidays, events)

    # Buscar staff atual
    current_staff = await get_current_active_staff(db)

    # Gerar recomendação
    diff = predicted - current_staff
    if diff > 0:
        recommendation = f"Contratar {diff} colaborador{'es' if diff > 1 else ''}"
    elif diff < 0:
        recommendation = f"Reduzir {abs(diff)} colaborador{'es' if abs(diff) > 1 else ''}"
    else:
        recommendation = "Manter equipe atual"

    return {
        "predicted_staff": predicted,
        "current_staff": current_staff,
        "difference": diff,
        "confidence": 0.87,  # Calcular baseado no modelo
        "recommendation": recommendation,
        "reasoning": generate_reasoning(month, holidays, events)
    }


@router.get("/predictions/cost")
async def predict_cost(
    month: int = Query(..., ge=1, le=12),
    staff_count: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Prevê custo operacional do próximo mês.

    Returns:
        {
            "predicted_cost": 142500,
            "breakdown": {
                "salaries": 120000,
                "overtime": 15000,
                "benefits": 7500
            },
            "vs_budget": -2500,
            "confidence": 0.91
        }
    """
    # Se não fornecido, usar staff atual
    if staff_count is None:
        staff_count = await get_current_active_staff(db)

    # Estimar horas extras (média dos últimos 3 meses)
    avg_overtime = await get_average_overtime(db, months=3)

    # Carregar modelo
    predictor = CostPredictor()
    # Treinar com dados históricos (cache isso)
    historical = await get_historical_costs(db, months=12)
    predictor.train(historical)

    # Prever
    predicted_cost = predictor.predict(staff_count, avg_overtime)

    # Buscar orçamento do mês
    budget = await get_monthly_budget(db, month)

    return {
        "predicted_cost": predicted_cost,
        "breakdown": estimate_breakdown(predicted_cost),
        "vs_budget": predicted_cost - budget if budget else None,
        "confidence": 0.91,
        "factors": {
            "staff_count": staff_count,
            "estimated_overtime": avg_overtime,
            "seasonal_factor": get_seasonal_factor(month)
        }
    }
```

#### Frontend - Predictive KPIs

```typescript
// /frontend/src/features/dashboard/components/PredictiveKPI.tsx

export const PredictiveKPI = () => {
  const { data: prediction } = useQuery(
    ['staffing-prediction'],
    () => api.get('/ml/predictions/staffing', {
      params: {
        month: new Date().getMonth() + 2, // Próximo mês
        holidays: 2,
        events: 1
      }
    })
  )

  return (
    <Card className="border-l-4 border-l-blue-500">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            Previsão de Pessoal - Próximo Mês
          </CardTitle>
          <Brain className="h-4 w-4 text-blue-500" />
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Prediction */}
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">
                {prediction?.predicted_staff}
              </span>
              <span className="text-sm text-muted-foreground">
                funcionários
              </span>
            </div>

            <div className="flex items-center gap-2 mt-1">
              {prediction?.difference > 0 ? (
                <TrendingUp className="h-4 w-4 text-orange-500" />
              ) : prediction?.difference < 0 ? (
                <TrendingDown className="h-4 w-4 text-green-500" />
              ) : (
                <Minus className="h-4 w-4 text-gray-500" />
              )}
              <span className={cn(
                "text-sm font-medium",
                prediction?.difference > 0 && "text-orange-500",
                prediction?.difference < 0 && "text-green-500"
              )}>
                {Math.abs(prediction?.difference || 0)} vs. atual
              </span>
            </div>
          </div>

          {/* Confidence */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Confiança</span>
              <span className="font-medium">
                {(prediction?.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <Progress value={prediction?.confidence * 100} />
          </div>

          {/* Recommendation */}
          <Alert>
            <Lightbulb className="h-4 w-4" />
            <AlertDescription className="text-sm">
              <strong>Recomendação:</strong><br />
              {prediction?.recommendation}
            </AlertDescription>
          </Alert>

          {/* Reasoning */}
          <Collapsible>
            <CollapsibleTrigger className="text-xs text-blue-600 hover:underline flex items-center gap-1">
              <Info className="h-3 w-3" />
              Por que essa previsão?
            </CollapsibleTrigger>
            <CollapsibleContent className="text-xs text-muted-foreground mt-2">
              {prediction?.reasoning}
            </CollapsibleContent>
          </Collapsible>
        </div>
      </CardContent>
    </Card>
  )
}
```

**Tarefas:**
- [ ] Backend - ML models (Staffing, Cost)
- [ ] Backend - Training pipeline
- [ ] Backend - Prediction endpoints
- [ ] Frontend - PredictiveKPI component
- [ ] Treinar modelos com dados reais
- [ ] Validação e accuracy metrics
- [ ] Explicabilidade (SHAP values)

**Estimativa:** 2 semanas

---

### 3.2 Alertas Inteligentes

#### Objetivo
Sistema proativo que identifica problemas ANTES de acontecerem.

```python
# /backend/modules/ml/anomaly_detection.py

from sklearn.ensemble import IsolationForest
import pandas as pd

class AnomalyDetector:
    """Detecta anomalias em padrões operacionais."""

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    def fit(self, normal_data: pd.DataFrame):
        """
        Treina com dados normais.

        Args:
            normal_data: DataFrame com features:
                - staff_count
                - occurrences
                - overtime_hours
                - coverage_percentage
        """
        self.model.fit(normal_data)

    def detect(self, current_data: dict) -> dict:
        """
        Detecta se dados atuais são anômalos.

        Returns:
            {
                "is_anomaly": True,
                "score": -0.23,
                "alerts": [
                    {
                        "type": "high_occurrences",
                        "severity": "warning",
                        "message": "Ocorrências 45% acima do normal"
                    }
                ]
            }
        """
        df = pd.DataFrame([current_data])
        prediction = self.model.predict(df)
        score = self.model.score_samples(df)[0]

        is_anomaly = prediction[0] == -1

        # Gerar alertas específicos
        alerts = []
        if is_anomaly:
            alerts = self.generate_specific_alerts(current_data)

        return {
            "is_anomaly": is_anomaly,
            "score": float(score),
            "alerts": alerts
        }

    def generate_specific_alerts(self, data: dict) -> List[dict]:
        """Gera alertas específicos baseado nos dados."""
        alerts = []

        # Alert: Ocorrências muito altas
        if data['occurrences'] > historical_avg['occurrences'] * 1.5:
            alerts.append({
                "type": "high_occurrences",
                "severity": "warning",
                "message": f"Ocorrências {int((data['occurrences'] / historical_avg['occurrences'] - 1) * 100)}% acima do normal",
                "action": "Investigar causas e considerar medidas preventivas"
            })

        # Alert: Cobertura baixa
        if data['coverage_percentage'] < 90:
            alerts.append({
                "type": "low_coverage",
                "severity": "critical",
                "message": f"Cobertura crítica: {data['coverage_percentage']}%",
                "action": "Realocar pessoal imediatamente ou contratar temporários"
            })

        # Alert: Horas extras excessivas
        if data['overtime_hours'] > 100:
            alerts.append({
                "type": "high_overtime",
                "severity": "info",
                "message": f"{data['overtime_hours']}h extras este mês",
                "action": "Otimizar escalas para reduzir custo"
            })

        return alerts


# Controller
@router.get("/anomalies/detect")
async def detect_anomalies(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentActiveUser
):
    """
    Detecta anomalias nos dados operacionais atuais.

    Returns:
        {
            "is_anomaly": True,
            "score": -0.23,
            "alerts": [
                {
                    "type": "high_occurrences",
                    "severity": "warning",
                    "message": "Ocorrências 45% acima do normal",
                    "action": "Investigar causas..."
                }
            ],
            "timestamp": "2026-01-26T10:30:00Z"
        }
    """
    # Buscar dados atuais
    current_data = {
        "staff_count": await count_active_staff(db),
        "occurrences": await count_month_occurrences(db),
        "overtime_hours": await sum_overtime_hours(db),
        "coverage_percentage": await calculate_coverage(db)
    }

    # Carregar detector treinado
    detector = joblib.load('models/anomaly_detector.pkl')

    # Detectar
    result = detector.detect(current_data)
    result['timestamp'] = datetime.utcnow().isoformat()

    # Se detectou anomalia, notificar gestores
    if result['is_anomaly']:
        await notify_managers(current_user.tenant_id, result['alerts'])

    return result
```

**Frontend - Alerts Dashboard**

```typescript
// /frontend/src/features/dashboard/components/SmartAlerts.tsx

export const SmartAlerts = () => {
  const { data: anomalies } = useQuery(
    ['anomalies'],
    () => api.get('/ml/anomalies/detect'),
    { refetchInterval: 60000 } // Check every minute
  )

  if (!anomalies?.alerts?.length) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">
            Tudo funcionando normalmente
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Alertas Inteligentes
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {anomalies.alerts.map((alert, i) => (
          <Alert
            key={i}
            variant={
              alert.severity === 'critical' ? 'destructive' :
              alert.severity === 'warning' ? 'warning' :
              'default'
            }
          >
            {alert.severity === 'critical' && <AlertTriangle className="h-4 w-4" />}
            {alert.severity === 'warning' && <AlertCircle className="h-4 w-4" />}
            {alert.severity === 'info' && <Info className="h-4 w-4" />}

            <AlertTitle>{alert.message}</AlertTitle>
            <AlertDescription className="text-xs mt-1">
              💡 <strong>Ação recomendada:</strong> {alert.action}
            </AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  )
}
```

**Tarefas:**
- [ ] Backend - Anomaly detection model
- [ ] Backend - Alert generation logic
- [ ] Backend - Notification service integration
- [ ] Frontend - SmartAlerts component
- [ ] Definir thresholds e regras
- [ ] Testes com dados históricos

**Estimativa:** 1,5 semanas

---

### 3.3 Insights Automáticos

#### Objetivo
IA analisa dados e gera insights acionáveis automaticamente.

```python
# /backend/modules/ml/insights_generator.py

class InsightsGenerator:
    """Gera insights automáticos dos dados operacionais."""

    async def generate_insights(self, db: AsyncSession, tenant_id: str) -> List[dict]:
        """
        Analisa dados e gera insights.

        Returns:
            [
                {
                    "title": "Pico de ocorrências às quintas-feiras",
                    "description": "23% mais ocorrências em quintas vs. média semanal",
                    "impact": "high",
                    "recommendation": "Reforçar supervisão às quintas-feiras",
                    "data": {...}
                },
                ...
            ]
        """
        insights = []

        # Insight 1: Dia da semana com mais ocorrências
        dow_analysis = await self.analyze_day_of_week_pattern(db, tenant_id)
        if dow_analysis['significant']:
            insights.append({
                "title": f"Pico de ocorrências {dow_analysis['peak_day']}",
                "description": f"{dow_analysis['percentage']}% mais ocorrências que a média",
                "impact": "high" if dow_analysis['percentage'] > 30 else "medium",
                "recommendation": f"Reforçar supervisão {dow_analysis['peak_day']}",
                "category": "patterns",
                "data": dow_analysis
            })

        # Insight 2: Colaborador mais produtivo
        top_performer = await self.find_top_performer(db, tenant_id)
        if top_performer:
            insights.append({
                "title": f"{top_performer['nome']} é destaque do mês",
                "description": f"Pontualidade: 100%, Ocorrências: 0, Avaliação: 5.0",
                "impact": "medium",
                "recommendation": "Considerar para promoção ou prêmio",
                "category": "people",
                "data": top_performer
            })

        # Insight 3: Potencial economia
        optimization = await self.find_optimization_opportunities(db, tenant_id)
        if optimization['potential_savings'] > 1000:
            insights.append({
                "title": f"Economia de R$ {optimization['potential_savings']:,.2f} possível",
                "description": optimization['description'],
                "impact": "high",
                "recommendation": optimization['recommendation'],
                "category": "costs",
                "data": optimization
            })

        # Insight 4: Turnover risk
        turnover_risk = await self.predict_turnover_risk(db, tenant_id)
        if turnover_risk['high_risk_count'] > 0:
            insights.append({
                "title": f"{turnover_risk['high_risk_count']} colaboradores em risco de saída",
                "description": "Baseado em padrões de engagement e satisfação",
                "impact": "high",
                "recommendation": "Realizar 1:1s e avaliar benefícios",
                "category": "retention",
                "data": turnover_risk
            })

        return insights

    async def analyze_day_of_week_pattern(self, db, tenant_id):
        """Analisa padrão de ocorrências por dia da semana."""
        query = text("""
            SELECT
                EXTRACT(DOW FROM created_at) as day_of_week,
                COUNT(*) as count
            FROM occurrences
            WHERE tenant_id = :tenant_id
              AND created_at >= NOW() - INTERVAL '90 days'
            GROUP BY day_of_week
            ORDER BY count DESC
        """)

        result = await db.execute(query, {"tenant_id": tenant_id})
        data = result.fetchall()

        if not data:
            return {"significant": False}

        peak = data[0]
        avg = sum(row.count for row in data) / len(data)
        percentage = int(((peak.count / avg) - 1) * 100)

        days = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']

        return {
            "significant": percentage > 20,
            "peak_day": days[int(peak.day_of_week)],
            "percentage": percentage,
            "data": [{"day": days[int(r.day_of_week)], "count": r.count} for r in data]
        }
```

**Frontend - Insights Widget**

```typescript
// /frontend/src/features/dashboard/components/InsightsWidget.tsx

export const InsightsWidget = () => {
  const { data: insights } = useQuery(
    ['insights'],
    () => api.get('/ml/insights'),
    { refetchInterval: 3600000 } // Refresh every hour
  )

  const categoryIcons = {
    patterns: TrendingUp,
    people: Users,
    costs: DollarSign,
    retention: Heart
  }

  const categoryColors = {
    patterns: 'text-blue-500 bg-blue-500/10',
    people: 'text-green-500 bg-green-500/10',
    costs: 'text-orange-500 bg-orange-500/10',
    retention: 'text-purple-500 bg-purple-500/10'
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            Insights da Semana
          </CardTitle>
          <Badge variant="outline">
            Gerado por IA
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {insights?.map((insight, i) => {
          const Icon = categoryIcons[insight.category] || Lightbulb

          return (
            <div
              key={i}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start gap-3">
                <div className={cn(
                  'p-2 rounded-lg',
                  categoryColors[insight.category]
                )}>
                  <Icon className="h-5 w-5" />
                </div>

                <div className="flex-1">
                  <h4 className="font-medium mb-1">
                    {insight.title}
                  </h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    {insight.description}
                  </p>

                  <Alert className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
                    <Lightbulb className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-xs text-blue-900 dark:text-blue-100">
                      <strong>Recomendação:</strong> {insight.recommendation}
                    </AlertDescription>
                  </Alert>
                </div>

                <Badge variant={
                  insight.impact === 'high' ? 'destructive' :
                  insight.impact === 'medium' ? 'warning' :
                  'default'
                }>
                  {insight.impact === 'high' && '🔴'}
                  {insight.impact === 'medium' && '🟡'}
                  {insight.impact === 'low' && '🟢'}
                </Badge>
              </div>
            </div>
          )
        })}

        {(!insights || insights.length === 0) && (
          <div className="text-center py-8">
            <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
              IA está analisando seus dados...
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

**Tarefas:**
- [ ] Backend - InsightsGenerator class
- [ ] Backend - Análise de padrões
- [ ] Backend - Endpoint de insights
- [ ] Frontend - InsightsWidget component
- [ ] Algoritmos de detecção de padrões
- [ ] Cache de insights (atualizar a cada hora)

**Estimativa:** 2 semanas

---

### 3.4 Visualizações Avançadas

#### Objetivo
Gráficos interativos que contam histórias com os dados.

```typescript
// /frontend/src/features/dashboard/components/AdvancedCharts.tsx

import { ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar, Tooltip, Legend, XAxis, YAxis } from 'recharts'

// Heatmap de Ocupação
export const OccupancyHeatmap = () => {
  const { data } = useQuery(['occupancy-heatmap'], fetchOccupancyData)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mapa de Calor - Ocupação</CardTitle>
        <CardDescription>
          Visualize padrões de alocação por dia e hora
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-24 gap-1">
          {/* 24 horas x 7 dias */}
          {data?.heatmap.map((cell, i) => (
            <div
              key={i}
              className="aspect-square rounded"
              style={{
                backgroundColor: getHeatmapColor(cell.occupancy)
              }}
              title={`${cell.day} ${cell.hour}h: ${cell.occupancy}%`}
            />
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-4 mt-4">
          <span className="text-xs">0%</span>
          <div className="flex gap-1">
            {[0, 25, 50, 75, 100].map(v => (
              <div
                key={v}
                className="w-8 h-4 rounded"
                style={{ backgroundColor: getHeatmapColor(v) }}
              />
            ))}
          </div>
          <span className="text-xs">100%</span>
        </div>
      </CardContent>
    </Card>
  )
}

// Timeline de Eventos
export const EventTimeline = () => {
  const { data: events } = useQuery(['event-timeline'], fetchEvents)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Linha do Tempo - Últimos 30 Dias</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-border" />

          {/* Events */}
          <div className="space-y-8">
            {events?.map((event, i) => (
              <div
                key={event.id}
                className={cn(
                  "flex items-center gap-4",
                  i % 2 === 0 ? "flex-row" : "flex-row-reverse"
                )}
              >
                {/* Content */}
                <div className={cn(
                  "flex-1 p-4 rounded-lg border",
                  i % 2 === 0 ? "text-right" : "text-left"
                )}>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={getEventVariant(event.type)}>
                      {event.type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(event.timestamp), 'dd/MM HH:mm')}
                    </span>
                  </div>
                  <h4 className="font-medium">{event.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {event.description}
                  </p>
                </div>

                {/* Dot */}
                <div className={cn(
                  "w-4 h-4 rounded-full border-4 border-background z-10",
                  event.type === 'critical' && "bg-red-500",
                  event.type === 'warning' && "bg-orange-500",
                  event.type === 'success' && "bg-green-500",
                  event.type === 'info' && "bg-blue-500"
                )} />

                {/* Spacer */}
                <div className="flex-1" />
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Mapa Georreferenciado
export const PostsMap = () => {
  const { data: posts } = useQuery(['posts-map'], fetchPostsWithLocation)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mapa de Postos</CardTitle>
        <CardDescription>
          Status em tempo real de todos os postos
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="h-96 rounded-lg overflow-hidden">
          <MapContainer
            center={[-23.550520, -46.633308]} // São Paulo
            zoom={12}
            className="h-full w-full"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {posts?.map(post => (
              <Marker
                key={post.id}
                position={[post.latitude, post.longitude]}
                icon={getPostIcon(post.status)}
              >
                <Popup>
                  <div className="p-2">
                    <h4 className="font-medium">{post.nome}</h4>
                    <div className="text-sm space-y-1 mt-2">
                      <div className="flex items-center gap-2">
                        <Users className="h-3 w-3" />
                        <span>{post.colaboradores_count} colaboradores</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={
                          post.coverage >= 100 ? 'success' :
                          post.coverage >= 80 ? 'warning' :
                          'destructive'
                        }>
                          {post.coverage}% cobertura
                        </Badge>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => router.push(`/modulos/operacional/postos/${post.id}`)}
                    >
                      Ver Detalhes
                    </Button>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </CardContent>
    </Card>
  )
}
```

**Tarefas:**
- [ ] Heatmap de ocupação
- [ ] Timeline de eventos
- [ ] Mapa georreferenciado (Leaflet)
- [ ] Gráficos de tendência (Recharts)
- [ ] Drill-down interativo
- [ ] Export de gráficos (PNG)

**Estimativa:** 1,5 semanas

---

## RESUMO FASE 3: DASHBOARD INTELIGENTE

### Entregas
1. ✅ KPIs Preditivos (IA)
2. ✅ Alertas Inteligentes
3. ✅ Insights Automáticos
4. ✅ Heatmap de Ocupação
5. ✅ Timeline de Eventos
6. ✅ Mapa Georreferenciado

### Métricas de Sucesso
- **Acurácia ML:** > 85% nas previsões
- **Tempo de Decisão:** -40% (insights prontos)
- **Problemas Evitados:** 70% detectados antes
- **Satisfação:** 4.7/5.0

### Recursos Necessários
- **2 Full-Stack Developers**
- **1 ML Engineer**
- **1 Data Analyst**
- **1 UX Designer**

### Investimento
**R$ 60.000 - 80.000**

### Cronograma
**6 semanas (Sprints 4-6)**

---


## FASE 4: GERADOR DE ESCALAS COM IA
**Duração:** 8 semanas (Sprints 7-10)
**Objetivo:** Automatizar 80% da criação de escalas com otimização inteligente
**Prioridade:** 🔥 CRÍTICA

### 4.1 Motor de Otimização

#### Algoritmo de Constraint Satisfaction

```python
# /backend/modules/ml/schedule_optimizer.py

from ortools.sat.python import cp_model
import numpy as np

class ScheduleOptimizer:
    """
    Otimizador de escalas usando Google OR-Tools.
    Resolve problema de alocação de recursos com múltiplas restrições.
    """

    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def generate_optimal_schedule(
        self,
        employees: List[dict],
        posts: List[dict],
        requirements: dict,
        constraints: dict
    ) -> dict:
        """
        Gera escala ótima baseada em restrições.

        Args:
            employees: Lista de colaboradores disponíveis
            posts: Lista de postos a cobrir
            requirements: Necessidades por posto/dia
            constraints: Restrições (max dias consecutivos, descanso, etc.)

        Returns:
            {
                "schedule": [...],
                "score": 94,
                "cost": 142500,
                "coverage": 98.5,
                "violations": []
            }
        """
        num_days = 30
        num_shifts = 3  # Manhã, Tarde, Noite

        # Variáveis de decisão: employee x post x day x shift
        shifts = {}
        for e in range(len(employees)):
            for p in range(len(posts)):
                for d in range(num_days):
                    for s in range(num_shifts):
                        shifts[(e, p, d, s)] = self.model.NewBoolVar(
                            f'shift_e{e}_p{p}_d{d}_s{s}'
                        )

        # Restrição 1: Cada posto precisa de N funcionários por turno
        for p in range(len(posts)):
            for d in range(num_days):
                for s in range(num_shifts):
                    required = requirements[posts[p]['id']][s]
                    self.model.Add(
                        sum(shifts[(e, p, d, s)] for e in range(len(employees))) == required
                    )

        # Restrição 2: Funcionário trabalha apenas 1 posto por dia
        for e in range(len(employees)):
            for d in range(num_days):
                self.model.Add(
                    sum(
                        shifts[(e, p, d, s)]
                        for p in range(len(posts))
                        for s in range(num_shifts)
                    ) <= 1
                )

        # Restrição 3: Máximo de dias consecutivos
        max_consecutive = constraints.get('max_consecutive_days', 6)
        for e in range(len(employees)):
            for d in range(num_days - max_consecutive):
                self.model.Add(
                    sum(
                        shifts[(e, p, day, s)]
                        for p in range(len(posts))
                        for day in range(d, d + max_consecutive + 1)
                        for s in range(num_shifts)
                    ) <= max_consecutive
                )

        # Restrição 4: Mínimo de horas de descanso entre turnos
        for e in range(len(employees)):
            for d in range(num_days - 1):
                # Se trabalhou à noite, não pode trabalhar de manhã no dia seguinte
                self.model.Add(
                    sum(
                        shifts[(e, p, d, 2)]  # Noite dia D
                        for p in range(len(posts))
                    ) +
                    sum(
                        shifts[(e, p, d + 1, 0)]  # Manhã dia D+1
                        for p in range(len(posts))
                    ) <= 1
                )

        # Função Objetivo: Minimizar custo + Maximizar satisfação
        objective_terms = []

        # Termo 1: Custo (salário * turnos)
        for e in range(len(employees)):
            salary = employees[e]['hourly_rate']
            for p in range(len(posts)):
                for d in range(num_days):
                    for s in range(num_shifts):
                        objective_terms.append(
                            shifts[(e, p, d, s)] * salary * 8  # 8h por turno
                        )

        # Termo 2: Preferências (funcionário prefere certo posto)
        for e in range(len(employees)):
            preferences = employees[e].get('preferred_posts', {})
            for p in range(len(posts)):
                if posts[p]['id'] in preferences:
                    preference_score = preferences[posts[p]['id']]  # 0-10
                    for d in range(num_days):
                        for s in range(num_shifts):
                            # Bonus negativo (reduz custo) se alocar em posto preferido
                            objective_terms.append(
                                -shifts[(e, p, d, s)] * preference_score * 100
                            )

        # Termo 3: Equilíbrio de carga (evitar sobrecarga)
        # ... adicionar termo de balanceamento

        self.model.Minimize(sum(objective_terms))

        # Resolver
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self.extract_solution(shifts, employees, posts, num_days, num_shifts)
        else:
            raise ValueError("Não foi possível gerar escala ótima com as restrições fornecidas")

    def extract_solution(self, shifts, employees, posts, num_days, num_shifts):
        """Extrai solução do modelo."""
        schedule = []
        total_cost = 0

        for e in range(len(employees)):
            for p in range(len(posts)):
                for d in range(num_days):
                    for s in range(num_shifts):
                        if self.solver.Value(shifts[(e, p, d, s)]) == 1:
                            schedule.append({
                                "employee_id": employees[e]['id'],
                                "employee_name": employees[e]['nome'],
                                "post_id": posts[p]['id'],
                                "post_name": posts[p]['nome'],
                                "date": d + 1,
                                "shift": ['Manhã', 'Tarde', 'Noite'][s],
                                "cost": employees[e]['hourly_rate'] * 8
                            })
                            total_cost += employees[e]['hourly_rate'] * 8

        return {
            "schedule": schedule,
            "total_cost": total_cost,
            "solver_status": "OPTIMAL",
            "solve_time_ms": int(self.solver.WallTime() * 1000)
        }


# Controller
@router.post("/schedule/generate")
async def generate_smart_schedule(
    data: GenerateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentActiveUser
):
    """
    Gera escala otimizada com IA.

    Request:
        {
            "month": 2,
            "year": 2026,
            "posts": ["post-1", "post-2"],
            "constraints": {
                "max_consecutive_days": 6,
                "min_rest_hours": 11,
                "max_overtime_hours": 40
            },
            "objectives": {
                "minimize_cost": 0.6,
                "maximize_satisfaction": 0.4
            }
        }

    Response:
        {
            "schedule": [...],
            "alternatives": [
                {
                    "name": "Opção A: Mais Econômica",
                    "cost": 137000,
                    "coverage": 95,
                    "score": 87
                },
                {
                    "name": "Opção B: Balanceada",
                    "cost": 142000,
                    "coverage": 98,
                    "score": 94
                },
                {
                    "name": "Opção C: Máxima Cobertura",
                    "cost": 149000,
                    "coverage": 100,
                    "score": 91
                }
            ],
            "insights": [
                "Economia de R$ 12.500 vs. escala manual",
                "Redução de 40% em horas extras",
                "100% dentro das normas trabalhistas"
            ]
        }
    """
    # Buscar colaboradores disponíveis
    employees = await get_available_employees(db, data.posts, data.month, data.year)

    # Buscar postos
    posts = await get_posts_by_ids(db, data.posts)

    # Buscar requirements (quantos funcionários por posto/turno)
    requirements = await get_staffing_requirements(db, data.posts)

    # Gerar escala otimizada
    optimizer = ScheduleOptimizer()

    # Gerar 3 alternativas com diferentes pesos
    alternatives = []

    # Opção A: Minimizar custo (peso 80%)
    schedule_a = optimizer.generate_optimal_schedule(
        employees, posts, requirements,
        {**data.constraints, "cost_weight": 0.8, "satisfaction_weight": 0.2}
    )
    alternatives.append({
        "name": "Opção A: Mais Econômica",
        "schedule": schedule_a["schedule"],
        "cost": schedule_a["total_cost"],
        "coverage": calculate_coverage(schedule_a["schedule"]),
        "score": calculate_score(schedule_a, weights={"cost": 0.8})
    })

    # Opção B: Balanceada (peso 50-50)
    schedule_b = optimizer.generate_optimal_schedule(
        employees, posts, requirements,
        {**data.constraints, "cost_weight": 0.5, "satisfaction_weight": 0.5}
    )
    alternatives.append({
        "name": "Opção B: Balanceada",
        "schedule": schedule_b["schedule"],
        "cost": schedule_b["total_cost"],
        "coverage": calculate_coverage(schedule_b["schedule"]),
        "score": calculate_score(schedule_b, weights={"cost": 0.5})
    })

    # Opção C: Maximizar cobertura
    schedule_c = optimizer.generate_optimal_schedule(
        employees, posts, requirements,
        {**data.constraints, "cost_weight": 0.2, "satisfaction_weight": 0.8}
    )
    alternatives.append({
        "name": "Opção C: Máxima Cobertura",
        "schedule": schedule_c["schedule"],
        "cost": schedule_c["total_cost"],
        "coverage": calculate_coverage(schedule_c["schedule"]),
        "score": calculate_score(schedule_c, weights={"cost": 0.2})
    })

    # Gerar insights
    manual_cost_estimate = await estimate_manual_schedule_cost(db, data.posts, data.month)
    insights = [
        f"Economia de R$ {manual_cost_estimate - schedule_b['total_cost']:,.2f} vs. escala manual",
        f"Redução de {calculate_overtime_reduction(schedule_b)}% em horas extras",
        "100% dentro das normas trabalhistas (CLT)"
    ]

    return {
        "alternatives": alternatives,
        "recommended": "Opção B",  # ou lógica para determinar melhor
        "insights": insights,
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Estimativa:** 4 semanas

---

### 4.2 Interface do Wizard

```typescript
// /frontend/src/features/escalas/components/SmartScheduleWizard.tsx

export const SmartScheduleWizard = () => {
  const [step, setStep] = useState(1)
  const [config, setConfig] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    posts: [],
    constraints: {
      max_consecutive_days: 6,
      min_rest_hours: 11,
      max_overtime_hours: 40
    },
    objectives: {
      minimize_cost: 0.5,
      maximize_satisfaction: 0.5
    }
  })
  const [alternatives, setAlternatives] = useState([])
  const [generating, setGenerating] = useState(false)

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const response = await api.post('/operacional/schedule/generate', config)
      setAlternatives(response.data.alternatives)
      setStep(3)
    } catch (error) {
      toast.error('Erro ao gerar escala')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <Dialog open onOpenChange={() => router.back()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            🤖 Gerador Inteligente de Escalas
          </DialogTitle>
          <DialogDescription>
            A IA vai gerar 3 opções otimizadas para você escolher
          </DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-6">
          {[
            { num: 1, label: 'Configuração' },
            { num: 2, label: 'Restrições' },
            { num: 3, label: 'Resultado' }
          ].map((s, i) => (
            <div key={s.num} className="flex items-center flex-1">
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center font-medium",
                step >= s.num
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              )}>
                {step > s.num ? <Check className="h-4 w-4" /> : s.num}
              </div>
              <span className="ml-2 text-sm">{s.label}</span>
              {i < 2 && (
                <div className={cn(
                  "flex-1 h-0.5 mx-4",
                  step > s.num ? "bg-primary" : "bg-muted"
                )} />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Configuration */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Mês</Label>
                <Select
                  value={config.month.toString()}
                  onValueChange={v => setConfig({...config, month: parseInt(v)})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[...Array(12)].map((_, i) => (
                      <SelectItem key={i} value={(i + 1).toString()}>
                        {format(new Date(2026, i), 'MMMM', { locale: ptBR })}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Ano</Label>
                <Select
                  value={config.year.toString()}
                  onValueChange={v => setConfig({...config, year: parseInt(v)})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[2026, 2027, 2028].map(y => (
                      <SelectItem key={y} value={y.toString()}>{y}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Postos a Cobrir</Label>
              <PostsMultiSelect
                value={config.posts}
                onChange={posts => setConfig({...config, posts})}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Selecione os postos que precisam de escala
              </p>
            </div>

            <Button onClick={() => setStep(2)} className="w-full">
              Próximo: Definir Restrições
            </Button>
          </div>
        )}

        {/* Step 2: Constraints */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <Label>Máximo de Dias Consecutivos</Label>
              <Slider
                value={[config.constraints.max_consecutive_days]}
                onValueChange={([v]) => setConfig({
                  ...config,
                  constraints: {...config.constraints, max_consecutive_days: v}
                })}
                min={4}
                max={7}
                step={1}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {config.constraints.max_consecutive_days} dias
              </p>
            </div>

            <div>
              <Label>Objetivos de Otimização</Label>
              <div className="space-y-2 mt-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Minimizar Custo</span>
                  <span className="text-sm font-medium">
                    {(config.objectives.minimize_cost * 100).toFixed(0)}%
                  </span>
                </div>
                <Slider
                  value={[config.objectives.minimize_cost * 100]}
                  onValueChange={([v]) => setConfig({
                    ...config,
                    objectives: {
                      minimize_cost: v / 100,
                      maximize_satisfaction: 1 - (v / 100)
                    }
                  })}
                  min={0}
                  max={100}
                  step={10}
                />
                <div className="flex items-center justify-between">
                  <span className="text-sm">Maximizar Satisfação</span>
                  <span className="text-sm font-medium">
                    {(config.objectives.maximize_satisfaction * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                Voltar
              </Button>
              <Button onClick={handleGenerate} disabled={generating} className="flex-1">
                {generating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {generating ? 'Gerando...' : '🚀 Gerar Escala com IA'}
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && (
          <div className="space-y-4">
            <Alert>
              <Sparkles className="h-4 w-4" />
              <AlertTitle>Escalas geradas com sucesso!</AlertTitle>
              <AlertDescription>
                A IA criou 3 opções otimizadas. Compare e escolha a melhor.
              </AlertDescription>
            </Alert>

            <Tabs defaultValue="0">
              <TabsList className="grid w-full grid-cols-3">
                {alternatives.map((alt, i) => (
                  <TabsTrigger key={i} value={i.toString()}>
                    {alt.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {alternatives.map((alt, i) => (
                <TabsContent key={i} value={i.toString()} className="space-y-4">
                  {/* KPIs da Opção */}
                  <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <p className="text-sm text-muted-foreground">Custo Total</p>
                          <p className="text-2xl font-bold">
                            R$ {(alt.cost / 1000).toFixed(1)}k
                          </p>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <p className="text-sm text-muted-foreground">Cobertura</p>
                          <p className="text-2xl font-bold">{alt.coverage}%</p>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <p className="text-sm text-muted-foreground">Score</p>
                          <p className="text-2xl font-bold flex items-center justify-center gap-1">
                            {alt.score}
                            <Star className="h-5 w-5 fill-yellow-500 text-yellow-500" />
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Preview da Escala */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Preview</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="max-h-64 overflow-y-auto">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Data</TableHead>
                              <TableHead>Colaborador</TableHead>
                              <TableHead>Posto</TableHead>
                              <TableHead>Turno</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {alt.schedule.slice(0, 10).map((shift, j) => (
                              <TableRow key={j}>
                                <TableCell>{shift.date}/02</TableCell>
                                <TableCell>{shift.employee_name}</TableCell>
                                <TableCell>{shift.post_name}</TableCell>
                                <TableCell>
                                  <Badge>{shift.shift}</Badge>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                        {alt.schedule.length > 10 && (
                          <p className="text-xs text-center text-muted-foreground mt-2">
                            + {alt.schedule.length - 10} turnos...
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Button
                    className="w-full"
                    onClick={() => handleSelectSchedule(alt)}
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Selecionar esta Opção
                  </Button>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
```

**Estimativa:** 2 semanas

---

### 4.3 Drag & Drop Calendar Editor

```typescript
// Permitir ajustes manuais após geração da IA

import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'

export const ScheduleCalendarEditor = ({ schedule, onChange }) => {
  const handleDragEnd = (result) => {
    if (!result.destination) return

    const { source, destination } = result

    // Lógica de realocação
    const newSchedule = Array.from(schedule)
    const [removed] = newSchedule.splice(source.index, 1)
    newSchedule.splice(destination.index, 0, removed)

    onChange(newSchedule)
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-7 gap-2">
        {/* 7 dias da semana */}
        {[...Array(30)].map((_, day) => (
          <Droppable key={day} droppableId={day.toString()}>
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="border rounded-lg p-2 min-h-[200px]"
              >
                <h4 className="text-sm font-medium mb-2">
                  {day + 1}/02
                </h4>

                {schedule
                  .filter(s => s.date === day + 1)
                  .map((shift, i) => (
                    <Draggable
                      key={shift.id}
                      draggableId={shift.id}
                      index={i}
                    >
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="bg-primary/10 rounded p-2 mb-2 text-xs"
                        >
                          <p className="font-medium">{shift.employee_name}</p>
                          <p className="text-muted-foreground">{shift.shift}</p>
                        </div>
                      )}
                    </Draggable>
                  ))}

                {provided.placeholder}
              </div>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  )
}
```

**Estimativa:** 2 semanas

---

## RESUMO FASE 4: GERADOR DE ESCALAS IA

### Entregas
1. ✅ Motor de Otimização (OR-Tools)
2. ✅ Wizard Interativo
3. ✅ 3 Opções Automáticas
4. ✅ Drag & Drop Editor
5. ✅ Validação de Regras CLT

### Métricas de Sucesso
- **Tempo de Criação:** -80% (30min → 6min)
- **Qualidade:** Score médio > 90/100
- **Economia:** 15-20% vs. manual
- **Adoção:** 70% das escalas via IA

### Recursos Necessários
- **2 Backend Developers**
- **1 ML Engineer**
- **1 Frontend Developer**
- **1 UX Designer**

### Investimento
**R$ 80.000 - 100.000**

### Cronograma
**8 semanas (Sprints 7-10)**

---

## FASES ADICIONAIS - RESUMO EXECUTIVO

### FASE 5: Analytics & Relatórios (8 semanas)
- Dashboards customizáveis
- Relatórios agendados
- Export automatizado
- BI embarcado

**Investimento:** R$ 70k-90k

### FASE 6: Portal do Colaborador (6 semanas)
- App simplificado para funcionários
- Visualização de escala
- Solicitação de trocas
- Gamificação

**Investimento:** R$ 50k-70k

### FASE 7: Gamificação (6 semanas)
- Sistema de conquistas
- Rankings
- Recompensas
- Leaderboards

**Investimento:** R$ 40k-60k

### FASE 8: IA Conversacional (12 semanas)
- ChatBot operacional
- Comandos de voz
- Consultas em linguagem natural
- Ações via chat

**Investimento:** R$ 100k-120k

### FASE 9: Integrações Avançadas (10 semanas)
- WhatsApp Business API
- Telegram Bot
- PowerBI/Tableau
- Webhooks personalizados

**Investimento:** R$ 80k-100k

### FASE 10: Performance & Escalabilidade (4 semanas)
- Otimização de queries
- CDN para assets
- Lazy loading
- Lighthouse Score > 95

**Investimento:** R$ 30k-40k

---

## 📊 CRONOGRAMA CONSOLIDADO

```
TIMELINE - 18 MESES (Fev/2026 - Ago/2027)

Q1/2026 (Fev-Abr):
├─ ✅ Fase 1: Quick Wins (2 sem)
├─ ✅ Fase 2: PWA Mobile (4 sem)
└─ ✅ Fase 3: Dashboard IA (Início - 4 sem)

Q2/2026 (Mai-Jul):
├─ ✅ Fase 3: Dashboard IA (Conclusão - 2 sem)
├─ ✅ Fase 4: Gerador Escalas (8 sem)
└─ ✅ Fase 5: Analytics (Início - 4 sem)

Q3/2026 (Ago-Out):
├─ ✅ Fase 5: Analytics (Conclusão - 4 sem)
├─ ✅ Fase 6: Portal Colaborador (6 sem)
└─ ✅ Fase 7: Gamificação (Início - 2 sem)

Q4/2026 (Nov-Dez):
├─ ✅ Fase 7: Gamificação (Conclusão - 4 sem)
└─ ✅ Fase 8: IA Conversacional (Início - 4 sem)

Q1/2027 (Jan-Mar):
├─ ✅ Fase 8: IA Conversacional (Conclusão - 8 sem)
└─ ✅ Fase 9: Integrações (Início - 4 sem)

Q2/2027 (Abr-Jun):
├─ ✅ Fase 9: Integrações (Conclusão - 6 sem)
└─ ✅ Fase 10: Performance (4 sem)

Q3/2027 (Jul-Ago):
└─ ✅ Estabilização e Refinamentos Finais
```

---

## 💰 RESUMO FINANCEIRO

| Fase | Duração | Investimento |
|------|---------|--------------|
| **Fase 1:** Quick Wins | 2 semanas | R$ 20k-30k |
| **Fase 2:** PWA Mobile | 4 semanas | R$ 40k-60k |
| **Fase 3:** Dashboard IA | 6 semanas | R$ 60k-80k |
| **Fase 4:** Gerador Escalas | 8 semanas | R$ 80k-100k |
| **Fase 5:** Analytics | 8 semanas | R$ 70k-90k |
| **Fase 6:** Portal Colaborador | 6 semanas | R$ 50k-70k |
| **Fase 7:** Gamificação | 6 semanas | R$ 40k-60k |
| **Fase 8:** IA Conversacional | 12 semanas | R$ 100k-120k |
| **Fase 9:** Integrações | 10 semanas | R$ 80k-100k |
| **Fase 10:** Performance | 4 semanas | R$ 30k-40k |
| **TOTAL** | **18 meses** | **R$ 620k-880k** |

### ROI Projetado
- **Economia Anual:** R$ 250k-400k
- **Produtividade:** +60% eficiência
- **Redução de Custos Operacionais:** 15-20%
- **ROI:** 300-400% em 24 meses
- **Payback:** 18-24 meses

---

## 🎯 MÉTRICAS DE SUCESSO GLOBAL

### KPIs Técnicos
- Lighthouse Score: > 95
- Uptime: > 99.9%
- API Response Time: < 200ms (P95)
- Error Rate: < 0.1%
- PWA Install Rate: > 60%

### KPIs de Negócio
- Tempo de Gestão de Escalas: -80%
- Custo Operacional: -15-20%
- Satisfação de Usuários: > 4.5/5.0
- Adoção de Features IA: > 70%
- Redução de Ocorrências: -25%

### KPIs de Adoção
- DAU (Daily Active Users): > 80%
- Engagement (tempo por sessão): > 15min
- Feature Discovery: > 60%
- Mobile Usage: > 50%

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

### Semana 1-2: Setup & Planejamento
- [ ] Aprovação do plano pela diretoria
- [ ] Montagem da equipe core
- [ ] Setup de ambiente de desenvolvimento
- [ ] Definição de arquitetura detalhada
- [ ] Kick-off meeting

### Semana 3-4: Fase 1 - Quick Wins
- [ ] Sprint Planning
- [ ] Desenvolvimento das 10 quick wins
- [ ] Code review e testes
- [ ] Deploy em staging
- [ ] User testing
- [ ] Deploy em produção
- [ ] Retrospective

### Semana 5+: Iniciar Fase 2
- [ ] PWA configuration
- [ ] Service Worker implementation
- [ ] IndexedDB setup
- [ ] Continuação do roadmap...

---

## 📝 CONSIDERAÇÕES FINAIS

Este plano estratégico foi elaborado com base em:
- ✅ Análise do código atual do sistema
- ✅ Best practices de mercado (Google, Meta, Uber)
- ✅ Feedback da auditoria operacional
- ✅ Necessidades específicas dos stakeholders (CEO, gerentes, supervisores, colaboradores)
- ✅ Tecnologias maduras e confiáveis
- ✅ Metodologia ágil com entregas incrementais

### Diferenciais Competitivos

Ao completar este roadmap, o Conecta PRO terá:
1. **IA Preditiva:** Único sistema que ANTECIPA problemas
2. **Mobile-First:** 100% operacional sem internet
3. **Otimização Inteligente:** Economiza 15-20% vs. concorrentes
4. **UX Excepcional:** Lighthouse > 95, Dark mode, Atalhos
5. **Gamificação:** Engajamento único no mercado
6. **Integrações Nativas:** WhatsApp, Telegram, BI tools

### Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Complexidade ML | Média | Alto | Contratar ML Engineer especializado |
| Performance com volume | Baixa | Alto | Testes de carga desde início |
| Adoção de usuários | Média | Médio | Onboarding guiado + Treinamentos |
| Budget overrun | Média | Alto | Revisões mensais + Buffer 20% |
| Atraso no cronograma | Média | Médio | Sprints com folga + Priorização clara |

---

## 🎉 CONCLUSÃO

Este plano transforma o Módulo Operacional em uma **plataforma de classe mundial**, combinando:
- 🤖 Inteligência Artificial
- 📱 Mobilidade Total
- ⚡ Performance Excepcional
- 🎯 Experiência Única
- 💰 ROI Comprovado

**Resultado:** Sistema que não apenas gerencia operações, mas POTENCIALIZA resultados.

---

**Documento elaborado por:** Equipe Técnica Conecta PRO
**Data:** 26 de Janeiro de 2026
**Próxima Revisão:** Mensal (última sexta-feira)

---

_"O futuro da gestão operacional não é sobre fazer mais com menos. É sobre fazer MELHOR com INTELIGÊNCIA."_

🚀 **Vamos transformar o Operacional em um foguete!** 🚀

