# PLANO DE CORREÇÕES - MÓDULO OPERACIONAL
## Baseado no Relatório de Auditoria Completa

**Data:** 2026-01-23
**Responsável:** Claude AI + Jordan
**Objetivo:** Resolver 100% dos problemas identificados

---

## SUMÁRIO EXECUTIVO

| Fase | Módulo | Prioridade | Esforço | Status |
|------|--------|------------|---------|--------|
| 1 | Alocações - Corrigir UUIDs | CRÍTICO | 2h | PENDENTE |
| 2 | Dashboard - Cards Clicáveis | ALTO | 1h | PENDENTE |
| 3 | Dashboard - KPIs Estratégicos | ALTO | 3h | PENDENTE |
| 4 | Escalas - Página de Detalhes | CRÍTICO | 4h | PENDENTE |
| 5 | Escalas - Editor Visual | CRÍTICO | 6h | PENDENTE |
| 6 | Rondas - Frontend Completo | CRÍTICO | 8h | PENDENTE |
| 7 | Turnos - Melhorias Calendário | MÉDIO | 2h | PENDENTE |
| 8 | Postos - Wizard Multi-Step | MÉDIO | 4h | PENDENTE |
| 9 | Postos - Validação ViaCEP | BAIXO | 1h | PENDENTE |
| 10 | Postos - Funcionalidades Avançadas | BAIXO | 3h | PENDENTE |

**Tempo Total Estimado:** ~34 horas de desenvolvimento

---

## FASE 1: ALOCAÇÕES - CORRIGIR UUIDs (CRÍTICO)

### Problema
- Tabela mostra UUIDs em vez de nomes de colaboradores
- Frontend faz lookup manual em memória (ineficiente)

### Solução

#### 1.1 Backend - Atualizar Schema
**Arquivo:** `/opt/conecta-pro/backend/modules/operacional/schemas/allocation.py`

```python
# Adicionar campos ao AllocationResponse
class AllocationResponse(BaseModel):
    # ... campos existentes ...

    # Novos campos denormalizados
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    employee_registration: Optional[str] = None
    post_name: Optional[str] = None
    post_code: Optional[str] = None
```

#### 1.2 Backend - Atualizar Repository
**Arquivo:** `/opt/conecta-pro/backend/modules/operacional/repositories/allocation_repository.py`

- Fazer JOIN com tabela employees
- Fazer JOIN com tabela posts
- Popular campos denormalizados

#### 1.3 Frontend - Atualizar Types
**Arquivo:** `/opt/conecta-pro/frontend/src/types/operacional.ts`

```typescript
export interface Allocation {
  // ... campos existentes ...
  employee_name?: string;
  employee_email?: string;
  employee_registration?: string;
  post_name?: string;
  post_code?: string;
}
```

#### 1.4 Frontend - Simplificar Página
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/operacional/alocacoes/page.tsx`

- Remover lógica de lookup manual
- Usar diretamente `allocation.employee_name`
- Remover carregamento de 200 funcionários

### Critério de Aceite
- [ ] Tabela mostra nome do colaborador
- [ ] Tabela mostra nome do posto
- [ ] Sem lookup manual no frontend
- [ ] Performance melhorada

---

## FASE 2: DASHBOARD - CARDS CLICÁVEIS (ALTO)

### Problema
- Cards de estatísticas não são clicáveis
- Usuário não consegue drill-down nos dados

### Solução

#### 2.1 Cards com Links
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/operacional/page.tsx`

```tsx
// Card Postos -> Link para /postos
<Link href="/modulos/operacional/postos">
  <Card clickable>
    <h3>{stats.total}</h3>
    <p>Postos</p>
  </Card>
</Link>

// Card Com Vagas -> Link filtrado
<Link href="/modulos/operacional/postos?filter=com_vagas">
  <Card clickable>
    <h3>{stats.with_vacancy}</h3>
    <p>Com vagas</p>
  </Card>
</Link>

// Card Alocados -> Link para alocações
<Link href="/modulos/operacional/alocacoes">
  <Card clickable>
    <h3>{stats.total_allocated}</h3>
    <p>Alocados</p>
  </Card>
</Link>
```

### Critério de Aceite
- [ ] Todos os 4 cards são clicáveis
- [ ] Hover mostra cursor pointer
- [ ] Navegação funcional
- [ ] Filtros aplicados corretamente

---

## FASE 3: DASHBOARD - KPIs ESTRATÉGICOS (ALTO)

### Problema
- Faltam métricas executivas importantes
- Dashboard muito básico para gestão

### Solução

#### 3.1 Novos KPIs a Implementar

```
┌─────────────────────────────────────────┐
│  VISÃO GERAL OPERACIONAL                │
├─────────────────────────────────────────┤
│ Taxa de Ocupação: 88.6% ↑ 2.3%          │
│ Custo Mensal: R$ 127.450,00             │
│ Ocorrências Abertas: 3                  │
│ Turnos Hoje: 12                         │
│                                          │
│ ALERTAS:                                 │
│ • 2 postos sem cobertura                │
│ • 5 documentos vencem em 15 dias        │
│ • 1 ocorrência grave não resolvida      │
└─────────────────────────────────────────┘
```

#### 3.2 Backend - Novo Endpoint de Dashboard
**Arquivo:** `/opt/conecta-pro/backend/modules/operacional/controllers/`

```python
@router.get("/dashboard/executive")
async def get_executive_dashboard():
    return {
        "occupation_rate": 88.6,
        "monthly_cost": 127450.00,
        "open_occurrences": 3,
        "today_shifts": 12,
        "alerts": [...]
    }
```

#### 3.3 Frontend - Componente Dashboard Executivo
**Arquivo:** `/opt/conecta-pro/frontend/src/components/operacional/executive-dashboard.tsx`

### Critério de Aceite
- [ ] KPIs estratégicos visíveis
- [ ] Alertas em destaque
- [ ] Dados em tempo real
- [ ] Comparativo com período anterior

---

## FASE 4: ESCALAS - PÁGINA DE DETALHES (CRÍTICO)

### Problema
- Não existe página de visualização detalhada
- Impossível ver turnos de uma escala

### Solução

#### 4.1 Criar Página Dinâmica
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/operacional/escalas/[id]/page.tsx`

```tsx
// Estrutura da página
- Header com info da escala (código, status, período)
- Timeline de workflow (draft → aprovado → publicado)
- Calendário visual dos turnos
- Lista de funcionários alocados
- Botões de ação (aprovar, publicar, editar)
```

#### 4.2 Componentes Necessários
- `ScaleDetailHeader` - Info e status
- `ScaleWorkflowTimeline` - Progresso do workflow
- `ScaleShiftsCalendar` - Calendário visual
- `ScaleEmployeesList` - Funcionários da escala

### Critério de Aceite
- [ ] Página carrega por ID
- [ ] Mostra todos os turnos
- [ ] Workflow visível
- [ ] Ações funcionais

---

## FASE 5: ESCALAS - EDITOR VISUAL (CRÍTICO)

### Problema
- Não é possível editar escala visualmente
- Falta drag-and-drop

### Solução

#### 5.1 Componente Editor
**Arquivo:** `/opt/conecta-pro/frontend/src/components/operacional/scale-editor.tsx`

```tsx
// Funcionalidades
- Grid de dias x funcionários
- Drag-and-drop de turnos
- Validação em tempo real
- Detecção de conflitos
- Cálculo automático de horas
```

#### 5.2 Backend - Endpoints de Suporte
- `PATCH /scales/{id}/shifts/bulk` - Atualização em lote
- `GET /scales/{id}/conflicts` - Verificar conflitos

### Critério de Aceite
- [ ] Editor visual funcional
- [ ] Drag-and-drop implementado
- [ ] Conflitos detectados
- [ ] Salvar alterações

---

## FASE 6: RONDAS - FRONTEND COMPLETO (CRÍTICO)

### Problema
- Backend 100% implementado
- Frontend apenas placeholder "Coming Soon"

### Solução

#### 6.1 Types TypeScript
**Arquivo:** `/opt/conecta-pro/frontend/src/types/rondas.ts`

```typescript
export type InspectionRoundStatus =
  | 'agendada' | 'em_andamento' | 'pausada'
  | 'concluida' | 'cancelada';

export interface InspectionRound {
  id: string;
  code: string;
  inspector_id: string;
  inspector_name?: string;
  status: InspectionRoundStatus;
  scheduled_date: string;
  started_at?: string;
  completed_at?: string;
  posts_to_visit: string[];
  posts_visited: string[];
  total_checkpoints: number;
  total_occurrences: number;
  observations?: string;
}

export interface Checkpoint {
  id: string;
  round_id: string;
  post_id: string;
  type: CheckpointType;
  status: CheckpointStatus;
  latitude?: number;
  longitude?: number;
  photos?: string[];
  observations?: string;
}
```

#### 6.2 Service API
**Arquivo:** `/opt/conecta-pro/frontend/src/lib/services/rondas.ts`

```typescript
export const rondasService = {
  list: () => api.get('/operacional/rondas'),
  getById: (id) => api.get(`/operacional/rondas/${id}`),
  create: (data) => api.post('/operacional/rondas', data),
  start: (id) => api.post(`/operacional/rondas/${id}/iniciar`),
  pause: (id) => api.post(`/operacional/rondas/${id}/pausar`),
  complete: (id) => api.post(`/operacional/rondas/${id}/concluir`),
  addCheckpoint: (id, data) => api.post(`/operacional/rondas/${id}/checkpoints`, data),
  getDashboard: () => api.get('/operacional/rondas/dashboard'),
};
```

#### 6.3 Hook useRondas
**Arquivo:** `/opt/conecta-pro/frontend/src/hooks/useRondas.ts`

#### 6.4 Página Principal
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/operacional/rondas/page.tsx`

```tsx
// Estrutura
- Dashboard com estatísticas
- Lista de rondas (agendadas, em andamento, concluídas)
- Filtros por status, inspetor, data
- Botão "Nova Ronda"
- Cards de ronda com ações rápidas
```

#### 6.5 Componentes
- `RoundCard` - Card de ronda com status
- `RoundFormModal` - Criar/editar ronda
- `RoundDetailModal` - Detalhes e checkpoints
- `CheckpointForm` - Registrar checkpoint
- `RoundMap` - Mapa com GPS (futuro)

### Critério de Aceite
- [ ] Listagem funcional
- [ ] CRUD completo
- [ ] Workflow (iniciar, pausar, concluir)
- [ ] Checkpoints funcionais
- [ ] Integração com ocorrências

---

## FASE 7: TURNOS - MELHORIAS CALENDÁRIO (MÉDIO)

### Problema
- Calendário funcional mas sem informações ricas
- Faltam indicadores visuais

### Solução

#### 7.1 Enriquecer Calendário
**Arquivo:** `/opt/conecta-pro/frontend/src/components/operacional/shift-calendar.tsx`

```tsx
// Melhorias
- Badge colorido por status (verde=ok, vermelho=faltas)
- Tooltip com resumo do dia
- Indicador de cobertura (%)
- Alertas visuais para dias críticos
```

#### 7.2 Vista Expandida do Dia
**Arquivo:** `/opt/conecta-pro/frontend/src/components/operacional/shift-day-view.tsx`

```tsx
// Melhorias
- Foto do funcionário
- Informações do posto
- Timeline visual
- Quick actions
```

### Critério de Aceite
- [ ] Calendário com cores por status
- [ ] Tooltips informativos
- [ ] Indicadores de cobertura
- [ ] UX melhorada

---

## FASE 8: POSTOS - WIZARD MULTI-STEP (MÉDIO)

### Problema
- Formulário com 25+ campos em uma tela
- UX ruim, taxa de abandono alta

### Solução

#### 8.1 Componente Wizard
**Arquivo:** `/opt/conecta-pro/frontend/src/components/operacional/post-form-wizard.tsx`

```tsx
// Steps
const steps = [
  { title: 'Informações Básicas', fields: ['name', 'type', 'shift'] },
  { title: 'Efetivo e Valores', fields: ['headcount', 'hourlyRate', 'cost'] },
  { title: 'Localização', fields: ['address', 'city', 'state', 'cep'] },
  { title: 'Requisitos', fields: ['armed', 'vehicle', 'certifications'] },
];

// Componente
<FormWizard steps={steps}>
  <Step1BasicInfo />
  <Step2Staffing />
  <Step3Location />
  <Step4Requirements />
</FormWizard>
```

#### 8.2 Progress Bar
- Indicador visual de progresso
- Navegação entre steps
- Validação por step

### Critério de Aceite
- [ ] Wizard com 4 steps
- [ ] Progress bar funcional
- [ ] Validação por step
- [ ] Navegação bidirecional

---

## FASE 9: POSTOS - VALIDAÇÃO VIACEP (BAIXO)

### Problema
- CEP não busca endereço automaticamente
- Usuário precisa digitar tudo manualmente

### Solução

#### 9.1 Integração ViaCEP
**Arquivo:** `/opt/conecta-pro/frontend/src/lib/services/viacep.ts`

```typescript
export async function fetchAddressByCep(cep: string) {
  const cleanCep = cep.replace(/\D/g, '');
  if (cleanCep.length !== 8) return null;

  const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
  const data = await response.json();

  if (data.erro) return null;

  return {
    address: data.logradouro,
    neighborhood: data.bairro,
    city: data.localidade,
    state: data.uf,
  };
}
```

#### 9.2 Componente CEP Input
```tsx
<CepInput
  onAddressFound={(address) => {
    setFieldValue('address', address.address);
    setFieldValue('city', address.city);
    setFieldValue('state', address.state);
  }}
/>
```

### Critério de Aceite
- [ ] CEP busca endereço automaticamente
- [ ] Campos preenchidos automaticamente
- [ ] Feedback visual de busca
- [ ] Tratamento de CEP inválido

---

## FASE 10: POSTOS - FUNCIONALIDADES AVANÇADAS (BAIXO)

### Problema
- Faltam funcionalidades de produtividade
- Duplicar, importar, histórico

### Solução

#### 10.1 Duplicar Posto
```tsx
// Botão na tabela
<Button onClick={() => duplicarPosto(posto.id)}>
  <Copy /> Duplicar
</Button>

// Endpoint backend
POST /posts/{id}/duplicate
```

#### 10.2 Importação em Massa
```tsx
// Modal de importação
<ImportModal
  templateUrl="/templates/postos.xlsx"
  onImport={handleBulkImport}
/>

// Endpoint backend
POST /posts/bulk-import
```

#### 10.3 Histórico de Alterações
```tsx
// Modal de histórico
<HistoryModal postId={posto.id} />

// Endpoint backend
GET /posts/{id}/history
```

### Critério de Aceite
- [ ] Duplicar posto funcional
- [ ] Importação CSV/Excel
- [ ] Histórico de alterações
- [ ] Audit log

---

## ORDEM DE EXECUÇÃO

```
Semana 1:
├── Fase 1: Alocações - Corrigir UUIDs (2h)
├── Fase 2: Dashboard - Cards Clicáveis (1h)
└── Fase 3: Dashboard - KPIs (3h)

Semana 2:
├── Fase 4: Escalas - Página Detalhes (4h)
└── Fase 5: Escalas - Editor Visual (6h)

Semana 3:
└── Fase 6: Rondas - Frontend Completo (8h)

Semana 4:
├── Fase 7: Turnos - Melhorias (2h)
├── Fase 8: Postos - Wizard (4h)
├── Fase 9: Postos - ViaCEP (1h)
└── Fase 10: Postos - Avançadas (3h)
```

---

## MÉTRICAS DE SUCESSO

| Métrica | Antes | Depois |
|---------|-------|--------|
| Nota Módulo | 6.3/10 | 9.0/10 |
| Funcionalidades | 60% | 100% |
| UX Score | 5/10 | 8/10 |
| Performance | Regular | Boa |
| Bugs Conhecidos | 8 | 0 |

---

## PRÓXIMO PASSO

Iniciar pela **Fase 1: Alocações - Corrigir UUIDs** por ser:
- Crítico para usabilidade
- Rápido de implementar (2h)
- Alto impacto visual
- Fundação para outras melhorias

**Aguardando aprovação para iniciar execução.**
