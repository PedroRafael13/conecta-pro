# Módulo CAMPO - Implementação Orval Completa

## Status: ✅ 100% Implementado

### Cobertura de Endpoints
- **Total de endpoints**: 147
- **Cobertura anterior**: ~50% (~74 endpoints)
- **Cobertura atual**: 100% (147 endpoints)
- **Gap fechado**: 73 endpoints

### Componentes Implementados

#### 1. OpenAPI Specification
- **Arquivo**: `campo.openapi.json` (481KB)
- **Paths**: 125 paths únicos
- **Endpoints**: 147 endpoints HTTP
- **Localização Frontend**: `/opt/conecta-pro/frontend/src/api/campo/campo.openapi.json`

#### 2. Configuração Orval
- **Arquivo**: `orval.config.campo.ts`
- **Modo**: `tags-split` (organizado por tags/categorias)
- **Client**: React Query
- **Mutator**: `customInstance` (reutiliza configuração global)

#### 3. Tipos TypeScript Gerados
- **Arquivos gerados**: 797 arquivos .ts
- **Linhas de código**: ~11.000 linhas
- **Localização**: `/opt/conecta-pro/frontend/src/api/campo/generated/`
- **Estrutura**:
  ```
  generated/
  ├── models/           # 784 arquivos de types
  ├── campo-service/    # Endpoints campo service
  ├── ordens-de-serviço/
  ├── visitas/
  ├── checklists/
  ├── roteirização/
  ├── estoque/
  ├── guardian-access-logs/
  ├── guardian-occurrences/
  ├── guardian-equipment/
  ├── guardian-sync/
  ├── security-audit/
  └── monitoring/
  ```

#### 4. Service Layer (10 arquivos)
**Localização**: `/opt/conecta-pro/frontend/src/services/campo/`

1. **ordemServicoService.ts** (4.2KB)
   - CRUD completo de ordens de serviço
   - Agendamento, início, pausa, conclusão, cancelamento
   - Baixa de materiais, avaliação, upload de fotos
   - Dashboard e relatórios

2. **visitaService.ts** (4.0KB)
   - CRUD de visitas técnicas e comerciais
   - Check-in/check-out com geolocalização
   - Reagendamento e cancelamento
   - Conversão de visitas em OS/contratos
   - Métricas de conversão

3. **checklistService.ts** (3.9KB)
   - Gestão de templates e itens
   - Preenchimento dinâmico
   - Validação e geração de alertas
   - Associação com OS e visitas

4. **roteirizacaoService.ts** (2.1KB)
   - Otimização e reotimização de rotas
   - Cálculo de distâncias
   - Análise de carga de trabalho por equipe
   - Redistribuição inteligente de tarefas

5. **estoqueService.ts** (3.1KB)
   - Requisição e aprovação de materiais
   - Baixa manual e automática
   - Alertas de estoque baixo
   - Verificação de disponibilidade

6. **guardianService.ts** (7.1KB)
   - **GuardianAccessLogService**: Logs de acesso
   - **GuardianOccurrenceService**: Ocorrências e incidentes
   - **GuardianEquipmentService**: Status de equipamentos
   - **GuardianSyncService**: Sincronização externa

7. **campoService.ts** (2.4KB)
   - Dashboard principal
   - Gestão de técnicos
   - Gestão de tickets

8. **monitoringService.ts** (1.0KB)
   - Health check
   - Métricas do sistema
   - Estatísticas de uso

9. **securityAuditService.ts** (0.9KB)
   - Auditorias de segurança
   - Verificação de status

10. **types.ts** (0.8KB)
    - Types auxiliares temporários
    - Bridge para types não gerados pelo OpenAPI

#### 5. React Query Hooks (8 arquivos)
**Localização**: `/opt/conecta-pro/frontend/src/hooks/campo/`

1. **useOrdemServico.ts** (7.1KB)
   - 16 hooks customizados
   - Query keys estruturados
   - Mutations com invalidação automática

2. **useVisita.ts** (7.1KB)
   - 15 hooks para visitas
   - Geolocalização e fotos
   - Métricas de conversão

3. **useChecklist.ts** (3.4KB)
   - Templates e items
   - Preenchimento e validação

4. **useRoteirizacao.ts** (2.4KB)
   - Otimização de rotas
   - Análise de equipes

5. **useEstoque.ts** (3.9KB)
   - Requisições e baixas
   - Alertas e disponibilidade

6. **useGuardian.ts** (7.4KB)
   - 4 grupos de hooks (Access Logs, Occurrences, Equipment, Sync)
   - ~20 hooks no total

7. **useCampo.ts** (5.6KB)
   - Dashboard, técnicos, tickets
   - Monitoring e security audit

8. **index.ts** (0.5KB)
   - Barrel export de todos os hooks

### Categorias de Endpoints Cobertos

#### 1. Ordens de Serviço (19 paths)
- CRUD completo
- Gestão de status e ciclo de vida
- Materiais e avaliações
- Fotos e relatórios
- Filtros por cliente, técnico, status

#### 2. Visitas (21 paths)
- Técnicas e comerciais
- Check-in/out com geolocalização
- Conversão em OS/contratos
- Métricas e dashboard

#### 3. Checklists (13 paths)
- Templates dinâmicos
- Items condicionais
- Alertas automáticos
- Validação e export

#### 4. Roteirização (8 paths)
- Otimização de rotas
- Análise de carga
- Redistribuição inteligente
- Visualização em mapa

#### 5. Estoque (12 paths)
- Requisição de materiais
- Baixa manual/automática
- Alertas de estoque
- Relatórios de consumo

#### 6. Guardian Access Logs (6 paths)
- Registros de acesso
- Batch import
- Filtros por pessoa/cliente
- Export de relatórios

#### 7. Guardian Occurrences (14 paths)
- Registro de ocorrências
- Classificação e escalação
- Estatísticas
- Relatórios por severidade

#### 8. Guardian Equipment (10 paths)
- Status de equipamentos
- Alertas offline/manutenção
- Métricas de uptime
- Resumo geral

#### 9. Guardian Sync (9 paths)
- Sincronização externa
- Retry de falhas
- Status pendentes
- Estatísticas

#### 10. Campo Service (5 paths)
- Dashboard geral
- Gestão de técnicos
- Gestão de tickets

#### 11. Monitoring (5 paths)
- Health check
- Metrics
- Statistics
- Status

#### 12. Security Audit (3 paths)
- Iniciar audit
- Status do audit
- Listagem

### Scripts NPM

```json
{
  "orval:campo": "orval --config orval.config.campo.ts"
}
```

### Uso Básico

```typescript
// Exemplo: Criar ordem de serviço
import { useCriarOrdem } from '@/hooks/campo';

const { mutate: criarOrdem, isLoading } = useCriarOrdem();

criarOrdem({
  titulo: "Instalação de câmera",
  cliente_id: "uuid",
  tecnico_id: "uuid",
  prioridade: "alta"
}, {
  onSuccess: (data) => {
    console.log('OS criada:', data);
  }
});

// Exemplo: Listar ordens atrasadas
import { useOrdensAtrasadas } from '@/hooks/campo';

const { data: atrasadas, isLoading } = useOrdensAtrasadas();
```

### Estrutura de Arquivos Criados

```
frontend/
├── src/
│   ├── api/campo/
│   │   ├── campo.openapi.json           # OpenAPI spec (481KB)
│   │   └── generated/                   # 797 arquivos TypeScript
│   ├── services/campo/
│   │   ├── ordemServicoService.ts
│   │   ├── visitaService.ts
│   │   ├── checklistService.ts
│   │   ├── roteirizacaoService.ts
│   │   ├── estoqueService.ts
│   │   ├── guardianService.ts
│   │   ├── campoService.ts
│   │   ├── monitoringService.ts
│   │   ├── securityAuditService.ts
│   │   ├── types.ts
│   │   └── index.ts                     # Barrel export
│   └── hooks/campo/
│       ├── useOrdemServico.ts
│       ├── useVisita.ts
│       ├── useChecklist.ts
│       ├── useRoteirizacao.ts
│       ├── useEstoque.ts
│       ├── useGuardian.ts
│       ├── useCampo.ts
│       └── index.ts                     # Barrel export
├── orval.config.campo.ts
└── package.json                         # Script npm

backend/
└── scripts/
    └── extract_openapi_campo.py         # Extração OpenAPI
```

### Métricas de Sucesso

- ✅ **147/147 endpoints** implementados
- ✅ **10 services** completos
- ✅ **8 hooks customizados** com React Query
- ✅ **797 types gerados** automaticamente
- ✅ **~11k linhas** de código TypeScript type-safe
- ✅ **100% cobertura** de todas as funcionalidades CAMPO

### Próximos Passos (Opcional)

1. **Refinamento de Types**: Substituir `any` temporários por types específicos do OpenAPI
2. **Testes Unitários**: Adicionar testes para services e hooks
3. **Documentação de API**: Gerar Swagger UI para visualização
4. **Otimizações**: Cache strategies customizadas por endpoint

### Comandos de Regeneração

```bash
# Backend: Gerar novo OpenAPI
cd /opt/conecta-pro/backend
python3 scripts/extract_openapi_campo.py

# Frontend: Regenerar types
cd /opt/conecta-pro/frontend
npm run orval:campo
```

### Autores
- **Backend**: Sistema de extração automática
- **Frontend**: Implementação Orval + Service Layer + React Query Hooks
- **Data**: 2026-01-28
