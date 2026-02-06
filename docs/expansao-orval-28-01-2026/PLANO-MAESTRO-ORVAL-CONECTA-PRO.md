# 🎯 PLANO MAESTRO - EXPANSÃO ORVAL EM TODOS OS MÓDULOS

**Data:** 28/01/2026
**Objetivo:** Implementar Orval + Cobertura 100% em TODOS os módulos do Conecta PRO
**Estratégia:** HÍBRIDA (Orval + Manual) - Modelo do OPERACIONAL e GED
**Duração Total:** 325 horas (~8 semanas)

---

## 📊 SITUAÇÃO ATUAL

```
╔═══════════════════════════════════════════════════════════════════╗
║  CONECTA PRO - VISÃO GERAL                                        ║
╠═══════════════════════════════════════════════════════════════════╣
║  Total Módulos Backend:         32                                ║
║  Total Endpoints Backend:       1.928                             ║
║  Total Métodos Frontend:        345                               ║
║                                                                   ║
║  ✅ Módulos 100% Cobertura:     10 (operacional, ged, crm, etc.)  ║
║  ⚠️  Módulos Parciais:          1 (government_integrations: 26%)  ║
║  ❌ Módulos 0% Cobertura:       15 (recruitment, ai, audit, etc.) ║
║  🔧 Módulos Infra (sem UI):     6 (automation, core, hr, etc.)    ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Status do Orval:**
- ✅ OPERACIONAL: Implementado (em outro terminal)
- ✅ GED: Auditado e pronto (100% cobertura)
- ⏳ DEMAIS 30 MÓDULOS: Pendentes

**Gap Total:** **673 endpoints** não implementados no frontend

---

## 🎯 MÓDULOS PRIORITÁRIOS (15 módulos com 0%)

### 🔴 CRÍTICO - Semana 1-2 (2 módulos | 75h)

| # | Módulo | Endpoints | Estimativa | Sprint | Observação |
|---|--------|-----------|------------|--------|------------|
| 1 | **recruitment** | 79 | 40h | 1 | Vagas, candidatos, entrevistas |
| 2 | **ai** | 25 | 35h | 1-2 | Bartolo, OCR, análise contratos |

**Justificativa:** Funcionalidades essenciais do negócio sem nenhuma UI.

### 🟠 ALTO - Semana 2-4 (3 módulos | 75h)

| # | Módulo | Endpoints Faltantes | Estimativa | Sprint | Observação |
|---|--------|---------------------|------------|--------|------------|
| 3 | **government_integrations** | 153 | 50h | 2-3 | NFS-e, eSocial, SEFAZ, FGTS |
| 4 | **audit** | 31 | 25h | 3 | Logs, compliance, rastreabilidade |
| 5 | **notifications** | 53 | 30h | 3 | Centro notificações inteligentes |

**Justificativa:** Compliance governamental e auditoria são obrigatórios.

### 🟡 MÉDIO - Semana 4-6 (5 módulos | 100h)

| # | Módulo | Endpoints | Estimativa | Sprint | Observação |
|---|--------|-----------|------------|--------|------------|
| 6 | **health_occupational** | 40 | 30h | 4 | PPRA, PCMSO, EPI |
| 7 | **security_lgpd** | 21 | 20h | 4 | Compliance LGPD |
| 8 | **document_kits** | 54 | 35h | 5 | Geração kits documentais |
| 9 | **monitoring** | 26 | 20h | 5 | Dashboard alertas |
| 10 | **config** | 47 | 25h | 6 | Painel administrativo |

**Justificativa:** Compliance, segurança e gestão de configurações.

### 🟢 BAIXO - Semana 6+ (5 módulos | 75h)

| # | Módulo | Endpoints | Estimativa | Sprint | Observação |
|---|--------|-----------|------------|--------|------------|
| 11 | **bidding** | 64 | 40h | 7 | Licitações públicas |
| 12 | **mobile** | 17 | 15h | 7 | APIs mobile (tipos only) |
| 13 | **scheduler** | 26 | 10h | 8 | Background service |
| 14 | **documents** | 16 | 10h | 8 | Suporte ao GED |
| 15 | **search** | 1 | 2h | 8 | Busca global |

**Justificativa:** Funcionalidades auxiliares, menor impacto no negócio.

---

## 📦 MÓDULOS COM 100% COBERTURA (10 módulos)

| Módulo | Endpoints | Status | Orval | Observação |
|--------|-----------|--------|-------|------------|
| operacional | 88 | ✅ 100% | ✅ | Em progresso (outro terminal) |
| ged | 133 | ✅ 100% | ✅ | Auditado, pronto para manter |
| crm | 100 | ✅ 100% | ⏳ | Implementar Orval para manter |
| financial | 369 | ✅ 100% | ⏳ | Implementar Orval para manter |
| clients | 51 | ✅ 92% | ⏳ | Completar 8% faltante |
| services | 63 | ✅ 100% | ⏳ | Implementar Orval |
| campo | 152 | ✅ 100% | ⏳ | Implementar Orval |
| equipment_management | 93 | ✅ 100% | ⏳ | Implementar Orval |
| integrations | 63 | ✅ 100% | ⏳ | Implementar Orval |
| reimbursement | 26 | ✅ 100% | ⏳ | Implementar Orval |
| analytics | 32 | ✅ 100% | ⏳ | Implementar Orval |
| reports | 38 | ✅ 100% | ⏳ | Implementar Orval |

**Ação:** Implementar Orval para manter sincronização automática (modelo GED).

---

## 🗓️ CRONOGRAMA DETALHADO (8 SEMANAS)

### SEMANA 1: CRÍTICO - RECRUITMENT (40h)
**Objetivo:** Recuperar funcionalidade de recrutamento

**Dias 1-2: Setup Orval (8h)**
- Extrair OpenAPI spec do módulo recruitment
- Configurar orval.config.recruitment.ts
- Gerar tipos TypeScript
- Validar build

**Dias 3-4: Service Layer (16h)**
- Criar recruitmentService (vagas, candidatos, entrevistas)
- Implementar hooks React Query
- Integrar com API

**Dia 5: UI Components (16h)**
- Componentes de vagas
- Componentes de candidatos
- Dashboard de recrutamento

### SEMANA 2: CRÍTICO - AI/BARTOLO (35h)
**Objetivo:** Implementar IA e análise inteligente

**Dias 1-2: Setup Orval (8h)**
- Extrair OpenAPI spec do módulo ai
- Configurar orval.config.ai.ts
- Gerar tipos

**Dias 3-5: Service + UI (27h)**
- aiService (análise contratos, OCR, detecção fraude)
- Hooks React Query
- Componentes de IA
- Dashboard Bartolo

### SEMANA 3: ALTO - GOVERNMENT INTEGRATIONS (50h)
**Objetivo:** Completar integrações governamentais

**Dias 1-2: Setup Orval (10h)**
- Extrair OpenAPI spec government_integrations
- Configurar orval.config.government.ts
- Gerar tipos

**Dias 3-5: Service + UI (40h)**
- governmentService (NFS-e, eSocial, SEFAZ, FGTS)
- Hooks React Query
- Dashboard de sync
- Logs de integração

### SEMANA 4: ALTO - AUDIT + NOTIFICATIONS (55h)
**Objetivo:** Auditoria e centro de notificações

**Dias 1-2: Audit (25h)**
- Setup Orval audit
- auditService + hooks
- Dashboard auditoria

**Dias 3-5: Notifications (30h)**
- Setup Orval notifications
- notificationsService + hooks
- Centro de notificações

### SEMANA 5: MÉDIO - HEALTH + SECURITY (50h)
**Objetivo:** Compliance ocupacional e LGPD

**Dias 1-3: Health Occupational (30h)**
- Setup Orval health_occupational
- healthService + hooks
- Dashboard PPRA/PCMSO/EPI

**Dias 4-5: Security LGPD (20h)**
- Setup Orval security_lgpd
- securityService + hooks
- Dashboard compliance LGPD

### SEMANA 6: MÉDIO - DOCUMENT KITS + MONITORING + CONFIG (80h)
**Objetivo:** Kits documentais, monitoramento e config

**Dias 1-2: Document Kits (35h)**
- Setup Orval document_kits
- documentKitsService + hooks
- UI de templates

**Dia 3: Monitoring (20h)**
- Setup Orval monitoring
- monitoringService + hooks
- Dashboard alertas

**Dia 4-5: Config (25h)**
- Setup Orval config
- configService + hooks
- Painel admin

### SEMANA 7: BAIXO - BIDDING + MOBILE (55h)
**Objetivo:** Licitações e APIs mobile

**Dias 1-4: Bidding (40h)**
- Setup Orval bidding
- biddingService + hooks
- UI de licitações

**Dia 5: Mobile (15h)**
- Setup Orval mobile
- Gerar tipos (sem UI)

### SEMANA 8: BAIXO - SCHEDULER + DOCUMENTS + SEARCH (22h)
**Objetivo:** Finalizar módulos auxiliares

**Dia 1: Scheduler (10h)**
- Setup Orval scheduler
- Gerar tipos

**Dia 2: Documents (10h)**
- Setup Orval documents
- documentsService + hooks

**Dia 3: Search (2h)**
- Setup Orval search
- searchService + hook

---

## 🚀 ESTRATÉGIA DE IMPLEMENTAÇÃO

### FASE 1: PREPARAÇÃO (Paralela - 1 dia)

**Criar script universal de extração:**
```python
# extract-module-spec.py
def extract_module_spec(module_name, base_path="/api/v1"):
    # Extrai apenas endpoints do módulo especificado
    # Reutilizável para todos os 15 módulos
```

**Criar template Orval config:**
```typescript
// orval.config.template.ts
export default defineConfig({
  [moduleName]: {
    input: { target: `./openapi-${moduleName}.json` },
    output: {
      mode: 'tags-split',
      target: `./src/types/generated/${moduleName}`,
      client: 'axios'
    }
  }
});
```

### FASE 2: GERAÇÃO EM LOTE (Paralela - 2 dias)

**Gerar configs para todos os 15 módulos:**
```bash
# Loop para gerar configs
for module in recruitment ai audit notifications health_occupational \
              security_lgpd document_kits monitoring config bidding \
              mobile scheduler documents search government_integrations
do
  python3 extract-module-spec.py --module $module
  cp orval.config.template.ts orval.config.$module.ts
  # Editar template
done
```

**Adicionar scripts no package.json:**
```json
{
  "scripts": {
    "orval:recruitment": "orval --config orval.config.recruitment.ts",
    "orval:ai": "orval --config orval.config.ai.ts",
    "orval:audit": "orval --config orval.config.audit.ts",
    // ... 12 módulos restantes
    "orval:all": "npm run orval:recruitment && npm run orval:ai && ..."
  }
}
```

### FASE 3: IMPLEMENTAÇÃO MODULAR (8 semanas)

**Padrão repetitivo para cada módulo:**

1. **Setup Orval (20% do tempo)**
   - Extrair OpenAPI spec
   - Configurar Orval
   - Gerar tipos
   - Validar build

2. **Service Layer (40% do tempo)**
   - Criar service com tipos gerados
   - Implementar métodos principais
   - Tratamento de erros

3. **Hooks React Query (20% do tempo)**
   - Criar hooks customizados
   - Cache e invalidação
   - Mutations

4. **UI Components (20% do tempo)**
   - Componentes reutilizáveis
   - Formulários
   - Tabelas/listas

**Exemplo completo (recruitment):**
```typescript
// 1. Tipos gerados automaticamente
import type {
  Candidate,
  CandidateCreate,
  CandidateFilter
} from '@/types/generated/recruitment';

// 2. Service layer
export const recruitmentService = {
  listCandidates: async (filters?: CandidateFilter) => {
    return api.get<PaginatedResponse<Candidate>>('/api/v1/recruitment/candidates', {
      params: filters
    });
  },

  createCandidate: async (data: CandidateCreate) => {
    return api.post<Candidate>('/api/v1/recruitment/candidates', data);
  },
};

// 3. Hooks React Query
export function useCandidates(filters?: CandidateFilter) {
  return useQuery({
    queryKey: ['recruitment', 'candidates', filters],
    queryFn: () => recruitmentService.listCandidates(filters),
  });
}

export function useCandidateMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: recruitmentService.createCandidate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recruitment', 'candidates'] });
    },
  });

  return { create };
}

// 4. UI Component
export function CandidatesPage() {
  const { data, isLoading } = useCandidates({ status: 'active' });
  const { create } = useCandidateMutations();

  if (isLoading) return <LoadingSpinner />;

  return (
    <div>
      <Button onClick={() => create.mutate(newCandidateData)}>
        Novo Candidato
      </Button>

      {data?.items.map(candidate => (
        <CandidateCard key={candidate.id} candidate={candidate} />
      ))}
    </div>
  );
}
```

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs por Módulo

| Métrica | Meta | Medição |
|---------|------|---------|
| Cobertura de Endpoints | 100% | Endpoints backend vs métodos frontend |
| Tipos Sincronizados | 100% | Zero erros TypeScript |
| Cobertura de Testes | 80% | Coverage report |
| Performance API | <500ms | Latência média |
| Cache Hit Rate | >70% | React Query devtools |

### Dashboard de Progresso

```
╔═══════════════════════════════════════════════════════════════════╗
║  EXPANSÃO ORVAL - CONECTA PRO                                     ║
╠═══════════════════════════════════════════════════════════════════╣
║  Semana 1:  recruitment          [████████████████████] 100%      ║
║  Semana 2:  ai                   [████████████████████] 100%      ║
║  Semana 3:  government_integ.    [████████░░░░░░░░░░░] 60%       ║
║  Semana 4:  audit, notifications [░░░░░░░░░░░░░░░░░░░] 0%        ║
║  ...                                                              ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🔄 MANUTENÇÃO CONTÍNUA

### Processo Padronizado

```bash
# 1. Backend atualizado? Regenerar tipos de todos os módulos
npm run orval:all

# 2. Verificar erros TypeScript
npm run types:check

# 3. Corrigir erros se houver

# 4. Build
npm run build
```

### CI/CD Integration

```yaml
# .github/workflows/sync-all-types.yml
name: Sync All Types

on:
  push:
    paths:
      - 'backend/modules/**'

jobs:
  sync-types:
    runs-on: ubuntu-latest
    steps:
      - name: Generate OpenAPI
        run: curl -s http://localhost:8080/openapi.json -o openapi.json

      - name: Extract all modules
        run: python3 extract-all-modules.py

      - name: Generate types
        run: npm run orval:all

      - name: Check types
        run: npm run types:check
```

---

## 💰 ESTIMATIVA DE CUSTOS

### Recursos Humanos

| Perfil | Quantidade | Horas/Semana | Semanas | Total Horas |
|--------|------------|--------------|---------|-------------|
| Frontend Sênior | 1 | 40h | 8 | 320h |
| Frontend Pleno | 1 | 40h | 4 (apoio) | 160h |

**OU**

| Perfil | Quantidade | Horas/Semana | Semanas | Total Horas |
|--------|------------|--------------|---------|-------------|
| Frontend Sênior | 2 | 40h | 4 | 320h |

### Timeline com 2 Devs (Recomendado)

**Duração:** 4 semanas (em vez de 8)

**Distribuição:**
- Dev 1: Módulos críticos e altos (recruitment, ai, government_integrations)
- Dev 2: Módulos médios e baixos (audit, notifications, health, security, etc.)

**Paralelização:**
- Semana 1: recruitment + audit
- Semana 2: ai + notifications
- Semana 3: government_integrations + health + security
- Semana 4: Demais módulos + refinamentos

---

## 🎯 ENTREGÁVEIS FINAIS

### Por Módulo

1. **OpenAPI spec** extraído (`openapi-{module}.json`)
2. **Config Orval** (`orval.config.{module}.ts`)
3. **Tipos gerados** (`src/types/generated/{module}/`)
4. **Service layer** (`src/lib/services/{module}.ts`)
5. **Hooks React Query** (`src/hooks/{module}/`)
6. **UI Components** (`src/components/{module}/`)
7. **Páginas** (`src/app/modulos/{module}/`)
8. **Testes** (`tests/{module}/`)
9. **Documentação** (`docs/{module}/README.md`)

### Global

1. **Script universal** de extração (`extract-module-spec.py`)
2. **Dashboard de progresso** (tracking implementação)
3. **Documentação completa** (como usar Orval em cada módulo)
4. **CI/CD pipeline** (sync automático)
5. **Guia de contribuição** (padrão para novos módulos)

---

## 🏆 RESULTADO ESPERADO

```
╔═══════════════════════════════════════════════════════════════════╗
║  CONECTA PRO - APÓS EXPANSÃO ORVAL (8 SEMANAS)                    ║
╠═══════════════════════════════════════════════════════════════════╣
║  Cobertura Backend→Frontend:     100% (1.928/1.928 endpoints)    ║
║  Tipos Sincronizados:            100% AUTOMÁTICO                  ║
║  Módulos com Orval:              32/32 (100%)                     ║
║  Manutenção:                     AUTOMATIZADA                     ║
║  Time to Market:                 50% REDUÇÃO                      ║
║                                                                   ║
║  🎯 PADRÃO ORVAL APLICADO EM TODOS OS MÓDULOS                     ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📚 REFERÊNCIAS

### Módulos Modelo
- **OPERACIONAL:** Em progresso (outro terminal)
- **GED:** `/opt/conecta-pro/docs/auditoria-ged-28-01-2026/`

### Scripts Reutilizáveis
- `extract-ged-spec.py` - Template base para outros módulos
- `orval.config.ged.ts` - Template de configuração

### Documentação Completa
- `EXECUTE-AGORA-GED.md` - Modelo de guia de execução
- `AUDITORIA-GED.md` - Modelo de auditoria
- `PLANO-COBERTURA-GED.md` - Modelo de plano

---

**Plano criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
**Objetivo:** Cobertura 100% + Orval em TODOS os módulos do Conecta PRO
