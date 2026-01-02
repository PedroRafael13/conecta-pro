# CONECTA MAIS - SKILLS DE REFINAMENTO DE QUALIDADE
**Versão**: 1.0 | **Target**: 10.00/10 em todos os 21 módulos

---

## 📋 OVERVIEW

Skills especializadas para corrigir os ~340 issues identificados no ERP Conecta Mais e elevar todos os módulos para 10.00/10.

---

## 🎯 SKILL 1: CORREÇÃO DE UNUSED-ARGUMENT

**Problema**: ~100 ocorrências de `unused-argument` (principalmente `current_user`)
**Score Impact**: Alto (representa ~30% dos issues)

### O QUE É

FastAPI injeta `current_user` via Dependency Injection em endpoints protegidos, mas nem sempre usamos esse parâmetro na função.

```python
# ❌ PROBLEMA
@router.post("/leads")
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),  # ← Pylint reclama: unused-argument
    db: AsyncSession = Depends(get_db)
):
    return await lead_service.create(db, data)  # current_user não usado
```

### SOLUÇÃO 1: Pylint Disable (Rápido)

```python
@router.post("/leads")
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db)
):
    return await lead_service.create(db, data)
```

### SOLUÇÃO 2: Prefixar com underscore (Pythonic)

```python
@router.post("/leads")
async def create_lead(
    data: LeadCreate,
    _current_user: User = Depends(get_current_user),  # ← Underscore indica "não usado"
    db: AsyncSession = Depends(get_db)
):
    return await lead_service.create(db, data)
```

### SOLUÇÃO 3: Usar o parâmetro (Ideal quando faz sentido)

```python
@router.post("/leads")
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Adicionar auditoria
    await audit_log.create(db, action="create_lead", user_id=current_user.id)
    return await lead_service.create(db, data, created_by=current_user.id)
```

### CRITÉRIO DE ESCOLHA

- **Solução 1**: Se endpoint precisa apenas verificar autenticação
- **Solução 2**: Se código é muito estável e não vai mudar
- **Solução 3**: Se faz sentido adicionar auditoria/tracking

### PROMPT PARA CLAUDE CODE

```
TAREFA: Corrigir unused-argument no módulo {MODULE_NAME}

CONTEXTO:
Módulo do ERP Conecta Mais com ~{N} ocorrências de unused-argument
Maioria são parâmetros `current_user` em controllers FastAPI

CRITÉRIOS:
1. Endpoints de READ (GET): Usar Solução 2 (underscore)
2. Endpoints de WRITE (POST/PUT/DELETE): Usar Solução 3 (adicionar audit)
3. Demais casos: Usar Solução 1 (pylint disable)

AÇÃO:
Para cada arquivo em {MODULE_PATH}/controllers/:
1. Identificar funções com unused-argument
2. Aplicar solução apropriada
3. Se Solução 3: Adicionar chamada ao audit_log
4. Testar que endpoints ainda funcionam

OUTPUT:
Código corrigido mantendo funcionalidade
```

---

## 🎯 SKILL 2: CORREÇÃO DE TOO-MANY-LOCALS/BRANCHES

**Problema**: ~50 ocorrências
**Score Impact**: Médio

### O QUE É

Funções com muitas variáveis locais (>15) ou branches (>12) são complexas de manter.

```python
# ❌ PROBLEMA: 20 variáveis locais
def get_leads_with_filters(
    db: AsyncSession,
    status: str = None,
    source: str = None,
    score_min: int = None,
    # ... mais 15 parâmetros
):
    query = select(Lead)
    
    # 20 variáveis locais diferentes
    status_filter = ...
    source_filter = ...
    # ...
```

### SOLUÇÃO 1: Pylint Disable (Se complexidade é necessária)

```python
def get_leads_with_filters(  # pylint: disable=too-many-locals
    db: AsyncSession,
    filters: LeadFilters  # ← Agrupar parâmetros
):
    # Código mantém complexidade mas está documentado
    ...
```

### SOLUÇÃO 2: Extrair Funções (Ideal)

```python
def get_leads_with_filters(db: AsyncSession, filters: LeadFilters):
    query = select(Lead)
    query = _apply_status_filters(query, filters)  # ← Extrair
    query = _apply_source_filters(query, filters)   # ← Extrair
    query = _apply_score_filters(query, filters)    # ← Extrair
    return await db.execute(query)

def _apply_status_filters(query, filters):
    # Lógica isolada
    ...
```

### SOLUÇÃO 3: Simplificar Lógica

```python
# ❌ ANTES: Muitos branches
if status == "active":
    if score > 80:
        if source == "website":
            priority = "high"
        else:
            priority = "medium"
    else:
        priority = "low"

# ✅ DEPOIS: Early returns
def calculate_priority(status, score, source):
    if status != "active":
        return "low"
    if score > 80 and source == "website":
        return "high"
    if score > 80:
        return "medium"
    return "low"

priority = calculate_priority(status, score, source)
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Reduzir complexidade em {MODULE_NAME}

ARQUIVOS ALVO:
{listar arquivos com too-many-locals/branches}

ESTRATÉGIA:
1. Funções >100 linhas: Aplicar Solução 2 (extrair)
2. Funções com lógica de filtros: Agrupar em classes Filter
3. Funções < 50 linhas: Aplicar Solução 1 (disable)

CRITÉRIO QUALIDADE:
- Cada função extraída deve ter nome descritivo
- Manter testes passando
- Complexity final ≤ 10

OUTPUT:
Código refatorado com complexity reduzida
```

---

## 🎯 SKILL 3: CORREÇÃO DE SINGLETON-COMPARISON

**Problema**: ~30 ocorrências
**Score Impact**: Baixo (mas fácil de corrigir)

### O QUE É

Comparar booleanos usando `==` ao invés de `is`.

```python
# ❌ PROBLEMA
if user.is_active == True:  # pylint: singleton-comparison
    ...

if lead.is_qualified == False:
    ...
```

### SOLUÇÃO

```python
# ✅ CORRETO
if user.is_active is True:
    ...

# ✅ AINDA MELHOR (mais pythonic)
if user.is_active:
    ...

if not lead.is_qualified:
    ...
```

### REGRA

- `== True` → `is True` ou simplesmente remover
- `== False` → `is False` ou usar `not`
- `== None` → `is None`
- `!= None` → `is not None`

### PROMPT PARA CLAUDE CODE

```
TAREFA: Corrigir singleton-comparison em {MODULE_NAME}

AÇÃO:
Substituir todas ocorrências:
- "== True" → "" (remover)
- "== False" → "not "
- "== None" → "is None"
- "!= None" → "is not None"

Testar que lógica se mantém correta.
```

---

## 🎯 SKILL 4: CORREÇÃO DE IMPORT-OUTSIDE-TOPLEVEL

**Problema**: ~20 ocorrências
**Score Impact**: Médio

### O QUE É

Imports dentro de funções ao invés de no topo do arquivo.

```python
# ❌ PROBLEMA
def process_document():
    import hashlib  # pylint: import-outside-toplevel
    import json
    
    data = json.loads(content)
    hash_value = hashlib.sha256(data).hexdigest()
```

### SOLUÇÃO

```python
# ✅ CORRETO
import hashlib
import json

def process_document():
    data = json.loads(content)
    hash_value = hashlib.sha256(data).hexdigest()
```

### EXCEÇÕES (quando import dentro é OK)

```python
# OK: Import circular
def get_user():
    from .models import User  # Evita circular import
    return User

# OK: Import pesado usado raramente
def generate_report():
    if format == "pdf":
        import weasyprint  # Pesado, só importa se necessário
        ...
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Mover imports para topo em {MODULE_NAME}

AÇÃO:
1. Identificar todos imports dentro de funções
2. Verificar se é import circular (pesquisar "circular")
3. Se NÃO for circular: mover para topo
4. Se FOR circular: adicionar comentário explicando

OUTPUT:
Imports organizados no topo do arquivo
```

---

## 🎯 SKILL 5: CORREÇÃO DE LINE-TOO-LONG

**Problema**: ~15 ocorrências
**Score Impact**: Baixo

### O QUE É

Linhas com >100 caracteres (limite do Pylint).

```python
# ❌ PROBLEMA (130 chars)
lead = await db.execute(select(Lead).where(Lead.id == lead_id).options(selectinload(Lead.opportunities).selectinload(Opportunity.proposals)))
```

### SOLUÇÃO

```python
# ✅ CORRETO
lead = await db.execute(
    select(Lead)
    .where(Lead.id == lead_id)
    .options(
        selectinload(Lead.opportunities)
        .selectinload(Opportunity.proposals)
    )
)
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Quebrar linhas longas em {MODULE_NAME}

REGRAS:
- Máximo 100 caracteres por linha
- Queries: quebrar por .where(), .options(), .join()
- Listas/dicts: um item por linha se >100 chars
- Strings: usar f-strings multi-linha

OUTPUT:
Código formatado <100 chars por linha
```

---

## 🎯 SKILL 6: CORREÇÃO DE UNUSED-IMPORT

**Problema**: ~15 ocorrências
**Score Impact**: Baixo

### O QUE É

Imports não utilizados no arquivo.

```python
# ❌ PROBLEMA
from sqlalchemy import select, update, delete  # delete não usado
from datetime import datetime, timedelta  # timedelta não usado
```

### SOLUÇÃO

```python
# ✅ CORRETO
from sqlalchemy import select, update
from datetime import datetime
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Remover imports não utilizados em {MODULE_NAME}

AÇÃO:
1. Executar: pylint --disable=all --enable=unused-import {MODULE}
2. Para cada import não usado: remover
3. Verificar que código ainda funciona

OUTPUT:
Apenas imports realmente usados
```

---

## 🎯 SKILL 7: CORREÇÃO DE TOO-FEW-PUBLIC-METHODS

**Problema**: ~25 ocorrências (principalmente schemas Pydantic)
**Score Impact**: Baixo

### O QUE É

Classes com <2 métodos públicos (Pydantic schemas quase sempre têm apenas `__init__`).

```python
# ❌ PROBLEMA
class LeadCreate(BaseModel):  # pylint: too-few-public-methods
    name: str
    email: str
    phone: str
```

### SOLUÇÃO

```python
# ✅ CORRETO
class LeadCreate(BaseModel):  # pylint: disable=too-few-public-methods
    """Schema for creating a lead."""
    name: str
    email: str
    phone: str
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Adicionar pylint disable em schemas Pydantic

AÇÃO:
Para cada arquivo *_schemas.py:
1. Adicionar # pylint: disable=too-few-public-methods após class
2. Ou adicionar no topo: # pylint: disable=too-few-public-methods

OUTPUT:
Schemas sem warning de too-few-public-methods
```

---

## 🎯 SKILL 8: CORREÇÃO DE TODO/FIXME

**Problema**: ~10 ocorrências
**Score Impact**: Baixo

### O QUE É

Comentários TODO/FIXME no código.

```python
# ❌ PROBLEMA
def calculate_commission():
    # TODO: Implementar cálculo de comissão progressiva  # pylint: fixme
    return base_commission
```

### SOLUÇÃO 1: Implementar

```python
# ✅ IDEAL
def calculate_commission(sales_amount, tier):
    if tier == "progressive":
        return _calculate_progressive_commission(sales_amount)
    return base_commission
```

### SOLUÇÃO 2: Remover se obsoleto

```python
# Se TODO está resolvido ou não é mais necessário
def calculate_commission():
    return base_commission
```

### SOLUÇÃO 3: Criar Issue e remover

```python
# Criar issue no GitHub/JIRA e remover do código
# Issue #123: Implementar comissão progressiva
def calculate_commission():
    return base_commission
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Resolver TODOs em {MODULE_NAME}

AÇÃO:
1. Listar todos TODO/FIXME
2. Para cada um:
   a) Se simples (<10 linhas): implementar
   b) Se obsoleto: remover
   c) Se complexo: criar issue no tracking e remover

OUTPUT:
Código sem TODOs
```

---

## 🎯 SKILL 9: CORREÇÃO DE MISSING-DOCSTRING

**Problema**: ~10 ocorrências
**Score Impact**: Médio

### O QUE É

Classes/funções públicas sem docstring.

```python
# ❌ PROBLEMA
class LeadService:  # pylint: missing-class-docstring
    def create(self, data):  # pylint: missing-function-docstring
        ...
```

### SOLUÇÃO

```python
# ✅ CORRETO
class LeadService:
    """Service for managing leads in the CRM system.
    
    Handles CRUD operations, scoring, and lifecycle management
    for sales leads.
    """
    
    def create(self, db: AsyncSession, data: LeadCreate) -> Lead:
        """Create a new lead in the database.
        
        Args:
            db: Database session
            data: Lead creation data
            
        Returns:
            Created lead instance
            
        Raises:
            ValueError: If email already exists
        """
        ...
```

### TEMPLATE

```python
"""[One-line summary].

[Optional detailed description]

Args:
    param1: Description
    param2: Description
    
Returns:
    Description
    
Raises:
    ExceptionType: When it happens
"""
```

### PROMPT PARA CLAUDE CODE

```
TAREFA: Adicionar docstrings em {MODULE_NAME}

AÇÃO:
Para cada classe/função pública sem docstring:
1. Adicionar docstring Google-style
2. Incluir: summary, args, returns, raises (se aplicável)

OUTPUT:
100% classes/funções públicas com docstrings
```

---

## 🎯 SKILL 10: CORREÇÃO DE MISSING-FINAL-NEWLINE

**Problema**: ~5 ocorrências
**Score Impact**: Muito baixo

### O QUE É

Arquivo não termina com linha em branco.

### SOLUÇÃO

Adicionar uma linha vazia no final do arquivo.

### PROMPT PARA CLAUDE CODE

```
TAREFA: Adicionar newline final

AÇÃO:
Para cada arquivo Python:
echo "" >> {arquivo}

Ou configurar editor para adicionar automaticamente.
```

---

## 📊 RESUMO DAS SKILLS

| Skill | Issues | Solução | Dificuldade | Prioridade |
|-------|--------|---------|-------------|------------|
| 1. Unused-argument | ~100 | pylint disable / underscore | Fácil | Alta |
| 2. Too-many-locals | ~50 | Refatorar / disable | Médio | Alta |
| 3. Singleton-comparison | ~30 | Trocar == por is | Fácil | Média |
| 4. Import-outside | ~20 | Mover para topo | Fácil | Média |
| 5. Line-too-long | ~15 | Quebrar linhas | Fácil | Baixa |
| 6. Unused-import | ~15 | Remover | Fácil | Baixa |
| 7. Too-few-methods | ~25 | pylint disable | Fácil | Baixa |
| 8. TODO/FIXME | ~10 | Implementar/remover | Médio | Média |
| 9. Missing-docstring | ~10 | Adicionar | Médio | Média |
| 10. Missing-newline | ~5 | Adicionar linha | Fácil | Baixa |

---

## 🚀 USO DAS SKILLS

### Para Claude Code:

```bash
claude-code \
  --skill=conecta-mais-quality-skills.md \
  --prompt="Aplicar Skill 1 (Unused-argument) no módulo CRM" \
  /caminho/backend/modules/crm
```

### Para correção em batch:

```bash
# Corrigir todos issues fáceis (Skills 3, 5, 6, 10)
for skill in 3 5 6 10; do
  claude-code --skill=skills.md \
    --prompt="Aplicar Skill $skill em todos módulos" \
    /caminho/backend
done
```

---

**FIM DAS SKILLS**
