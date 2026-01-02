# PROMPTS ESPECÍFICOS - SPRINTS DE QUALIDADE CONECTA MAIS
**4 Sprints para elevar todos os 21 módulos para 10.00/10**

---

## 🎯 SPRINT Q1: WINS RÁPIDOS
**Meta**: Elevar 4 módulos para 10.00/10
**Módulos**: clients (9.98), services (9.97), facilities (9.95), visitors (9.94)
**Total Issues**: ~50
**Duração Estimada**: 3-5 dias

---

### PROMPT Q1.1: MÓDULO CLIENTS (9.98 → 10.00)

```
REFINAMENTO: Módulo CLIENTS - Elevar para 10.00/10

CONTEXTO:
Módulo de cadastro de clientes/condomínios do ERP Conecta Mais
Score atual: 9.98/10
Gap: 0.02 (apenas 5 issues)
Arquivos: 16

ISSUES IDENTIFICADOS:
1. Too many branches em client_repository.py (14/12)
2. Too many branches em client_ai_service.py (3 ocorrências)
3. Too many local variables em client_controller.py (17/15)

ESTRATÉGIA DE CORREÇÃO:

1. client_repository.py:
   - Adicionar: # pylint: disable=too-many-branches
   - Ou: Extrair funções _apply_X_filter() para cada tipo de filtro
   - Escolher baseado em: se lógica for simples → disable, se complexa → extrair

2. client_ai_service.py:
   - Analisar 3 funções com muitos branches
   - Aplicar early returns para reduzir nesting
   - Considerar pattern matching (Python 3.10+)

3. client_controller.py:
   - Identificar variáveis que podem ser agrupadas em dict/class
   - Criar DTO se necessário
   - Ou: # pylint: disable=too-many-locals

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Funcionalidade: mantida 100%
- Testes: todos passando

PRIORIDADE: Alta (quick win - só 5 issues)

ENTREGUE:
Módulo clients com score 10.00/10
```

---

### PROMPT Q1.2: MÓDULO SERVICES (9.97 → 10.00)

```
REFINAMENTO: Módulo SERVICES - Elevar para 10.00/10

CONTEXTO:
Módulo de gestão de serviços prestados pela empresa
Score atual: 9.97/10
Gap: 0.03 (7 issues)
Arquivos: 16

ISSUES IDENTIFICADOS:
Too few public methods em service_schemas.py (7 classes Pydantic)

ESTRATÉGIA DE CORREÇÃO:

1. service_schemas.py:
   ```python
   # Adicionar no topo do arquivo
   # pylint: disable=too-few-public-methods
   
   class ServiceCatalogCreate(BaseModel):
       """Schema for creating service catalog entry."""
       name: str
       description: str
       # ...
   ```

2. Validar que todas as 7 classes Pydantic estão cobertas

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Schemas: funcionando normalmente
- Validações Pydantic: mantidas

PRIORIDADE: Alta (quick win - issue trivial)

ENTREGUE:
Módulo services com score 10.00/10
```

---

### PROMPT Q1.3: MÓDULO FACILITIES (9.95 → 10.00)

```
REFINAMENTO: Módulo FACILITIES - Elevar para 10.00/10

CONTEXTO:
Módulo de gestão de facilities (áreas, manutenções, inspeções)
Score atual: 9.95/10
Gap: 0.05 (18 issues)
Arquivos: 29

ISSUES IDENTIFICADOS:
1. Too many local variables: area_repository.py (21), inspection_repository.py (28), 
   checklist_repository.py (26), service_request_repository.py (37), 
   maintenance_repository.py (29)
2. Too many branches: vários arquivos
3. Import outside toplevel: maintenance.py
4. Wrong import position: service_request.py

ESTRATÉGIA DE CORREÇÃO:

1. Repositories com too-many-locals (Priority P1):
   ```python
   # Opção 1: Disable (se lógica é filtros complexos)
   def get_with_filters(  # pylint: disable=too-many-locals
       self, db, filters
   ):
       ...
   
   # Opção 2: Agrupar variáveis em dataclass
   @dataclass
   class QueryFilters:
       status_filter: str = None
       date_filter: date = None
       # ...
   
   def get_with_filters(self, db, filters: QueryFilters):
       ...
   ```

2. Import issues (Priority P2):
   - maintenance.py: Mover imports para topo
   - service_request.py: Reordenar imports (stdlib → third-party → local)

3. Too many branches (Priority P3):
   - Se ≤15 branches: disable
   - Se >15: aplicar early returns

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Queries: funcionando corretamente
- Performance: mantida ou melhorada

PRIORIDADE: Alta (importante para operações)

ENTREGUE:
Módulo facilities com score 10.00/10
```

---

### PROMPT Q1.4: MÓDULO VISITORS (9.94 → 10.00)

```
REFINAMENTO: Módulo VISITORS - Elevar para 10.00/10

CONTEXTO:
Módulo de gestão de visitantes em condomínios
Score atual: 9.94/10
Gap: 0.06 (20 issues)
Arquivos: 27

ISSUES IDENTIFICADOS:
1. Too many branches: visitor_repository.py (24), log_repository.py (25), 
   schedule_repository.py (26)
2. Too many local variables: log_repository.py (37)
3. Too many statements: log_repository.py (53/50)
4. Unused imports: vários arquivos

ESTRATÉGIA DE CORREÇÃO:

1. Repositories com complexidade (Priority P1):
   ```python
   # visitor_repository.py, log_repository.py, schedule_repository.py
   class VisitorRepository:  # pylint: disable=too-many-branches,too-many-locals
       
       def get_with_filters(self, ...):
           # Lógica complexa de filtros mantida
           ...
   ```

2. Unused imports (Priority P2):
   - Executar: pylint --disable=all --enable=unused-import visitor_module/
   - Remover todos imports não usados
   - Testar que código funciona

3. Too many statements (Priority P3):
   - log_repository.py: Se função >50 statements, extrair sub-funções
   - Ou: # pylint: disable=too-many-statements

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Filtros: funcionando corretamente
- Logs: mantendo integridade

PRIORIDADE: Alta (usado frequentemente)

ENTREGUE:
Módulo visitors com score 10.00/10
```

---

## 🎯 SPRINT Q2: INTERMEDIÁRIOS
**Meta**: Elevar 4 módulos para 10.00/10
**Módulos**: ged (9.87), occurrences (9.78), crm (9.73), operations (9.68)
**Total Issues**: ~95
**Duração Estimada**: 5-7 dias

---

### PROMPT Q2.1: MÓDULO GED (9.87 → 10.00)

```
REFINAMENTO: Módulo GED - Elevar para 10.00/10

CONTEXTO:
Módulo de Gestão Eletrônica de Documentos
Score atual: 9.87/10
Gap: 0.13 (20 issues)
Arquivos: 36

ISSUES IDENTIFICADOS:
1. Unused imports: 6 arquivos
2. Import hashlib outside toplevel: document_share_repository.py
3. Singleton comparison (== True): vários arquivos
4. Too many branches: document_repository.py (19/12)
5. Comparing against callable: folder_repository.py

ESTRATÉGIA DE CORREÇÃO:

1. Singleton comparisons (P1 - fácil):
   ```python
   # ❌ ANTES
   if document.is_signed == True:
       ...
   
   # ✅ DEPOIS
   if document.is_signed:
       ...
   ```
   - Trocar todas ocorrências: "== True" → remover, "== False" → "not"

2. Unused imports (P1 - fácil):
   - Remover todos imports não utilizados

3. Import outside toplevel (P2):
   ```python
   # ❌ ANTES (dentro de função)
   import hashlib
   
   # ✅ DEPOIS (topo do arquivo)
   import hashlib
   ```

4. Too many branches (P2):
   - document_repository.py: disable ou refatorar filtros

5. Callable comparison (P3):
   - folder_repository.py: Investigar e corrigir

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- GED: funcionando normalmente
- Versionamento: integridade mantida

PRIORIDADE: Alta (módulo crítico)

ENTREGUE:
Módulo ged com score 10.00/10
```

---

### PROMPT Q2.2: MÓDULO OCCURRENCES (9.78 → 10.00)

```
REFINAMENTO: Módulo OCCURRENCES - Elevar para 10.00/10

CONTEXTO:
Módulo de ocorrências internas da empresa
Score atual: 9.78/10
Gap: 0.22 (20 issues)
Arquivos: 27

ISSUES IDENTIFICADOS:
1. Import outside toplevel: __init__.py (3 ocorrências)
2. Too many local variables: occurrence_controller.py
3. Unused argument 'current_user': occurrence_controller.py (15+ ocorrências)
4. Unused import: occurrence_controller.py

ESTRATÉGIA DE CORREÇÃO:

1. Unused argument (P1 - mais impactante):
   ```python
   # Endpoints de leitura
   @router.get("/occurrences")
   async def list_occurrences(
       _current_user: User = Depends(get_current_user),  # ← underscore
       db: AsyncSession = Depends(get_db)
   ):
       ...
   
   # Endpoints de escrita
   @router.post("/occurrences")
   async def create_occurrence(
       data: OccurrenceCreate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       # Adicionar auditoria
       await audit_log.create(db, "create_occurrence", current_user.id)
       return await service.create(db, data, created_by=current_user.id)
   ```

2. Import outside toplevel (P2):
   - __init__.py: Avaliar se é import circular
   - Se não for: mover para topo
   - Se for: manter com comentário explicativo

3. Too many locals (P3):
   - occurrence_controller.py: disable ou agrupar variáveis

4. Unused import (P3):
   - Remover

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Auditoria: adicionada onde faz sentido
- Testes: passando

PRIORIDADE: Alta (muitas ocorrências de unused-argument)

ENTREGUE:
Módulo occurrences com score 10.00/10
```

---

### PROMPT Q2.3: MÓDULO CRM (9.73 → 10.00)

```
REFINAMENTO: Módulo CRM - Elevar para 10.00/10

CONTEXTO:
Módulo completo de CRM (Leads, Oportunidades, Propostas, Comissões, Contratos)
Score atual: 9.73/10
Gap: 0.27 (30 issues)
Arquivos: 32

ISSUES IDENTIFICADOS:
1. Unused argument 'current_user': commission_controller.py (9), 
   proposal_controller.py (9), lead_controller.py
2. Too many local variables: vários arquivos (17-20/15)
3. Unused import: commission_controller.py

ESTRATÉGIA DE CORREÇÃO:

1. Unused argument (P1 - ~20 ocorrências):
   ```python
   # Pattern para todos controllers
   
   # GETs: usar underscore
   @router.get("/leads")
   async def list_leads(
       _current_user: User = Depends(get_current_user),
       ...
   
   # POSTs/PUTs/DELETEs: adicionar auditoria
   @router.post("/leads")
   async def create_lead(
       data: LeadCreate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       await audit_log.create(db, "create_lead", current_user.id, data.dict())
       return await lead_service.create(db, data, created_by=current_user.id)
   ```

2. Too many locals (P2):
   - Aplicar disable nos repositories com filtros complexos
   - Considerar criar FilterBuilder pattern se muitos arquivos afetados

3. Unused import (P3):
   - Remover

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- CRM completo: funcionando
- Auditoria: implementada em operações críticas

PRIORIDADE: Alta (módulo core do negócio)

ENTREGUE:
Módulo crm com score 10.00/10
```

---

### PROMPT Q2.4: MÓDULO OPERATIONS (9.68 → 10.00)

```
REFINAMENTO: Módulo OPERATIONS - Elevar para 10.00/10

CONTEXTO:
Módulo de postos, escalas, turnos e substituições
Score atual: 9.68/10
Gap: 0.32 (25 issues)
Arquivos: 33

ISSUES IDENTIFICADOS:
1. TODO/FIXME comments: scale_controller.py
2. Unused argument 'current_user': vários arquivos (10+ ocorrências)
3. Too many local variables: substitution_controller.py (19/15)
4. Too many positional arguments: substitution_controller.py
5. Unused import: substitution_controller.py

ESTRATÉGIA DE CORREÇÃO:

1. TODO/FIXME (P1 - resolver ou remover):
   - scale_controller.py: Analisar cada TODO
   - Se simples: implementar
   - Se complexo: criar issue e remover do código
   - Se obsoleto: remover

2. Unused argument (P2):
   - Mesmo padrão: underscore para GETs, auditoria para POSTs

3. Too many locals (P3):
   - substitution_controller.py: disable

4. Too many positional arguments (P3):
   - Converter para keyword arguments ou criar DTO

5. Unused import (P3):
   - Remover

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- TODOs: resolvidos ou documentados em issues
- Escalas: funcionando corretamente

PRIORIDADE: Alta (operações críticas)

ENTREGUE:
Módulo operations com score 10.00/10
```

---

## 🎯 SPRINT Q3: COMPLEXOS
**Meta**: Elevar 5 módulos para 10.00/10
**Módulos**: recruitment (9.68), hr (9.65), core (9.64), residents (9.64), financial (9.60)
**Total Issues**: ~160
**Duração Estimada**: 7-10 dias

---

### PROMPT Q3.1: MÓDULO RECRUITMENT (9.68 → 10.00)

```
REFINAMENTO: Módulo RECRUITMENT - Elevar para 10.00/10

CONTEXTO:
Módulo de recrutamento e seleção
Score atual: 9.68/10
Gap: 0.32 (25 issues)
Arquivos: 33

ISSUES IDENTIFICADOS:
1. Unused argument 'current_user': application_controller.py (20+ ocorrências)
2. Too many local variables: application_controller.py (18/15)

ESTRATÉGIA DE CORREÇÃO:

1. Unused argument (P1 - 20+ ocorrências):
   - application_controller.py tem muitos endpoints
   - Aplicar padrão consistente:
     * GETs → underscore
     * POSTs/PUTs → auditoria (criar aplicação, atualizar status)
     * DELETEs → auditoria

2. Too many locals (P2):
   - application_controller.py: disable ou refatorar

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Recrutamento: funcionando
- Auditoria: presente em ações críticas

PRIORIDADE: Alta

ENTREGUE:
Módulo recruitment com score 10.00/10
```

---

### PROMPT Q3.2: MÓDULO HR (9.65 → 10.00)

```
REFINAMENTO: Módulo HR - Elevar para 10.00/10

CONTEXTO:
Módulo completo de RH (ponto, REP, mobile, analytics, folha, portal)
Score atual: 9.65/10
Gap: 0.35 (25 issues)
Arquivos: 167 (maior módulo!)

ISSUES IDENTIFICADOS:
1. Line too long: scheduled_report.py, dashboard_controller.py
2. Unused imports: vários arquivos (10+ ocorrências)
3. Unused variable 'total': kpi_controller.py (3 ocorrências)
4. Unused argument: vários arquivos
5. Import outside toplevel: dashboard_config.py

ESTRATÉGIA DE CORREÇÃO (por prioridade):

1. Unused imports (P1 - mais comum):
   - Executar: find . -name "*.py" -exec pylint --disable=all --enable=unused-import {} \;
   - Remover todos imports não usados

2. Line too long (P1 - fácil):
   - Quebrar linhas >100 chars
   - Usar formatação automática

3. Unused variable (P2):
   - kpi_controller.py: Remover variável 'total' ou usar

4. Import outside (P2):
   - dashboard_config.py: Mover para topo

5. Unused argument (P3):
   - Padrão consistente

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- HR completo: funcionando
- 167 arquivos: todos limpos

PRIORIDADE: Alta (módulo maior)

ENTREGUE:
Módulo hr com score 10.00/10
```

---

### PROMPT Q3.3: MÓDULO CORE (9.64 → 10.00)

```
REFINAMENTO: Módulo CORE - Elevar para 10.00/10

CONTEXTO:
Infraestrutura base (auth, database, cache, logging, monitoring)
Score atual: 9.64/10
Gap: 0.36 (25 issues)
Arquivos: 26

ISSUES IDENTIFICADOS:
1. Line too long: structured_logging.py (4), dependencies.py
2. Missing final newline: logging_config.py, structured_logging.py
3. Import outside toplevel: vários arquivos (5+)
4. Unused import json: structured_logging.py
5. Catching too general exception: redis.py (2)
6. Too few public methods: models/base.py

ESTRATÉGIA DE CORREÇÃO:

1. Line too long (P1):
   - structured_logging.py: Quebrar linhas longas
   - dependencies.py: idem

2. Missing newline (P1):
   - Adicionar linha vazia no final dos arquivos

3. Import outside (P2):
   - Avaliar se são imports circulares
   - Se não: mover para topo

4. Unused import (P2):
   - Remover import json não usado

5. Catching general exception (P3):
   ```python
   # ❌ ANTES
   try:
       ...
   except Exception:  # muito genérico
       ...
   
   # ✅ DEPOIS
   try:
       ...
   except (ConnectionError, TimeoutError) as e:
       logger.error(f"Redis error: {e}")
   ```

6. Too few methods (P3):
   - models/base.py: disable (é classe base)

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Core: funcionando perfeitamente (É A BASE!)
- Logging: mantendo estrutura

PRIORIDADE: CRÍTICA (é o core!)

ENTREGUE:
Módulo core com score 10.00/10
```

---

### PROMPT Q3.4: MÓDULO RESIDENTS (9.64 → 10.00)

```
REFINAMENTO: Módulo RESIDENTS - Elevar para 10.00/10

CONTEXTO:
Módulo de moradores de condomínios
Score atual: 9.64/10
Gap: 0.36 (25 issues)
Arquivos: 33

ISSUES IDENTIFICADOS:
1. Unused argument 'current_user': dependent_controller.py (20+)
2. Too many local variables: dependent_controller.py
3. Import outside toplevel: dependent_controller.py

ESTRATÉGIA DE CORREÇÃO:

1. Unused argument (P1):
   - dependent_controller.py: padrão underscore/auditoria

2. Too many locals (P2):
   - disable ou refatorar

3. Import outside (P3):
   - Mover para topo

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Moradores: funcionando

PRIORIDADE: Alta

ENTREGUE:
Módulo residents com score 10.00/10
```

---

### PROMPT Q3.5: MÓDULO FINANCIAL (9.60 → 10.00)

```
REFINAMENTO: Módulo FINANCIAL - Elevar para 10.00/10

CONTEXTO:
Módulo financeiro completo (maior depois de HR!)
Score atual: 9.60/10
Gap: 0.40 (50 issues)
Arquivos: 137

ISSUES IDENTIFICADOS:
1. Too few public methods: vários schemas (15+ classes)
2. Missing class docstring: vários schemas (10+)
3. Unnecessary pass statement: vários schemas (4)
4. Unused imports: vários arquivos (5+)

ESTRATÉGIA DE CORREÇÃO:

1. Too few public methods (P1 - mais comum):
   ```python
   # Adicionar no topo de cada arquivo *_schemas.py
   # pylint: disable=too-few-public-methods
   ```

2. Missing docstrings (P2):
   ```python
   class PayableCreate(BaseModel):  # pylint: disable=too-few-public-methods
       """Schema for creating accounts payable."""
       amount: Decimal
       due_date: date
       # ...
   ```

3. Unnecessary pass (P2):
   - Remover statements "pass" desnecessários

4. Unused imports (P3):
   - Remover

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Financeiro: funcionando perfeitamente
- 137 arquivos: todos limpos

PRIORIDADE: CRÍTICA (financeiro é crítico!)

ENTREGUE:
Módulo financial com score 10.00/10
```

---

## 🎯 SPRINT Q4: CRÍTICOS + POLIMENTO
**Meta**: 100% em TODOS os módulos
**Módulos**: equipment_management (9.60), field_service (9.52), + Revisão Geral
**Total Issues**: ~73 + revisão
**Duração Estimada**: 5-7 dias

---

### PROMPT Q4.1: MÓDULO EQUIPMENT_MANAGEMENT (9.60 → 10.00)

```
REFINAMENTO: Módulo EQUIPMENT_MANAGEMENT - Elevar para 10.00/10

CONTEXTO:
Módulo de gestão de equipamentos internos da empresa
Score atual: 9.60/10
Gap: 0.40 (25 issues)
Arquivos: 27

ISSUES IDENTIFICADOS:
1. Import outside toplevel: __init__.py (2)
2. Line too long: comodato.py
3. Singleton comparison: installation_repository.py (10+), equipment_repository.py (5+)
4. Too many local variables: maintenance_controller.py
5. Too many branches: installation_repository.py

ESTRATÉGIA DE CORREÇÃO:

1. Singleton comparison (P1 - 15+ ocorrências):
   - Trocar todos "== True" → remover, "== False" → "not"

2. Import outside (P2):
   - __init__.py: Avaliar circular import

3. Line too long (P2):
   - comodato.py: Quebrar linhas

4. Too many locals/branches (P3):
   - Disable

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Equipamentos: funcionando

PRIORIDADE: Alta

ENTREGUE:
Módulo equipment_management com score 10.00/10
```

---

### PROMPT Q4.2: MÓDULO FIELD_SERVICE (9.52 → 10.00)

```
REFINAMENTO: Módulo FIELD_SERVICE - Elevar para 10.00/10

CONTEXTO:
Módulo de serviço de campo (técnicos, tickets)
Score atual: 9.52/10 (MENOR SCORE!)
Gap: 0.48 (48 issues - MAIS ISSUES!)
Arquivos: 30

ISSUES IDENTIFICADOS:
1. Line too long: vários arquivos
2. Missing final newline: vários arquivos
3. Pointless string statement
4. TODO comments: 7 ocorrências
5. Unused variable e imports
6. Unused argument
7. Redefining name from outer scope

ESTRATÉGIA DE CORREÇÃO (ataque sistemático):

1. TODOs (P1 - resolver primeiro):
   - Implementar ou criar issues e remover

2. Line too long (P1):
   - Quebrar todas linhas >100 chars

3. Missing newline (P1):
   - Adicionar em todos arquivos

4. Unused imports/variables (P2):
   - Remover todos

5. Unused argument (P2):
   - Padrão underscore/auditoria

6. Redefining names (P3):
   - Renomear variáveis com shadowing

7. Pointless strings (P3):
   - Remover ou converter em docstrings

CRITÉRIOS DE QUALIDADE:
- Pylint: 10.00/10
- Field service: funcionando
- TODOs: resolvidos

PRIORIDADE: CRÍTICA (menor score!)

ENTREGUE:
Módulo field_service com score 10.00/10
```

---

### PROMPT Q4.3: REVISÃO GERAL E POLIMENTO FINAL

```
REVISÃO FINAL: Todos os 21 Módulos → 10.00/10

OBJETIVO:
Garantir que TODOS os 21 módulos do ERP Conecta Mais estejam em 10.00/10

PROCESSO:

1. AUDITORIA COMPLETA:
   ```bash
   ./conecta-mais-audit-system.sh /caminho/backend all full
   ```

2. VERIFICAÇÃO MÓDULO POR MÓDULO:
   Para cada módulo que não estiver em 10.00:
   - Executar Pylint individual
   - Identificar issues remanescentes
   - Aplicar correções finais

3. TESTES COMPLETOS:
   ```bash
   pytest --cov --cov-report=term-missing
   ```
   - Garantir que TODOS os testes passam
   - Coverage mantido ou melhorado

4. LINTING FINAL:
   ```bash
   ruff check . --fix
   black .
   mypy .
   ```

5. DOCUMENTAÇÃO:
   - Verificar que todos módulos têm README
   - ADRs para decisões importantes documentadas

CHECKLIST FINAL:

[ ] Todos 21 módulos em 10.00/10
[ ] 0 issues do Pylint
[ ] Todos testes passando
[ ] Coverage ≥85%
[ ] Type hints 100%
[ ] Docstrings completos
[ ] README atualizado
[ ] Git limpo (sem uncommitted changes)

META ATINGIDA:
✅ 21/21 módulos em 10.00/10
✅ Média geral: 10.00/10
✅ Qualidade de código: PERFEITA

ENTREGUE:
ERP Conecta Mais com 100% de qualidade em todos os módulos
```

---

## 📊 RESUMO DOS SPRINTS

| Sprint | Módulos | Issues | Dias | Prioridade |
|--------|---------|--------|------|------------|
| Q1 | 4 | ~50 | 3-5 | Alta (wins rápidos) |
| Q2 | 4 | ~95 | 5-7 | Alta (intermediários) |
| Q3 | 5 | ~160 | 7-10 | Crítica (complexos) |
| Q4 | 2+revisão | ~73 | 5-7 | Crítica (polimento) |
| **TOTAL** | **21** | **~378** | **20-29** | - |

---

## 🚀 EXECUÇÃO COM CLAUDE CODE

### Sprint Q1:
```bash
claude-code \
  --skill=conecta-mais-quality-skills.md \
  --prompts=conecta-mais-quality-prompts.md \
  --prompt="Execute PROMPT Q1.1: MÓDULO CLIENTS" \
  /caminho/backend/modules/clients
```

### Sequencial:
```bash
for sprint in Q1.1 Q1.2 Q1.3 Q1.4; do
  echo "Executando $sprint..."
  claude-code --prompt="Execute PROMPT $sprint" ...
  ./conecta-mais-audit-system.sh ... all full
done
```

---

**FIM DOS PROMPTS - PRONTO PARA EXECUÇÃO!**
