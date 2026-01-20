# INSTRUCOES CLAUDE CODE - EXECUCAO DE SPRINTS
## ERP CONECTA MAIS - FASE 2

**Versao:** 2.0
**Data:** Janeiro 2026
**Executor:** Claude Opus 4.5

---

## CONFIGURACAO OBRIGATORIA

### Modelo

```
UNICO MODELO PERMITIDO: claude-opus-4-5-20251101
NUNCA usar Sonnet, Haiku, ou outros modelos
```

### Ambiente

```bash
# Diretorio de trabalho
cd /opt/erp-conecta-mais/backend

# Ativar ambiente virtual
source venv/bin/activate

# Verificar Python
python3 --version  # Deve ser 3.12+
```

---

## FLUXO DE EXECUCAO DE SPRINT

### PASSO 1: Preparacao

```
ANTES de iniciar qualquer codigo:

1. Ler documentacao do sprint
   - docs/FASE2/sprints/sprint_XX.md

2. Ler skill do modulo
   - docs/FASE2/skills/{modulo}.md

3. Verificar dependencias
   - Sprint anterior concluido?
   - Testes passando?

4. Verificar ambiente
   - venv ativo
   - Banco de dados UP
   - Redis UP
```

### PASSO 2: Criacao de Arquivos

```
ORDEM OBRIGATORIA:

1. Model (models/entidade.py)
   - Campos com tipo correto
   - Relacionamentos
   - __repr__
   - Docstrings

2. Schema (schemas/entidade.py)
   - Create, Update, Response, List
   - Validacoes Pydantic
   - Field descriptions

3. Repository (repositories/entidade_repository.py)
   - CRUD basico
   - Queries especificas
   - Logging

4. Service (services/entidade_service.py)
   - Logica de negocio
   - Validacoes complexas
   - Orquestracao

5. Controller (controllers/entidade_controller.py)
   - Endpoints REST
   - Documentacao OpenAPI
   - Tratamento de erros

6. Testes (tests/test_entidade.py)
   - Unitarios
   - Integracao
   - Casos de borda
```

### PASSO 3: Auditoria

```bash
# APOS cada arquivo criado:

# 1. Verificar sintaxe
python -m py_compile arquivo.py

# 2. Verificar qualidade
pylint --rcfile=.pylintrc arquivo.py

# 3. Corrigir ate 100/100
# Se < 100, corrigir ANTES de continuar

# 4. Formatar
black arquivo.py
isort arquivo.py
```

### PASSO 4: Testes

```bash
# Rodar testes do arquivo
pytest tests/test_entidade.py -v

# Verificar cobertura
pytest tests/test_entidade.py --cov=modules/modulo --cov-report=term-missing

# Cobertura deve ser >= 85%
```

### PASSO 5: Migracao

```bash
# Se criou novo model:

# 1. Gerar migracao
alembic revision --autogenerate -m "adiciona tabela X"

# 2. Revisar arquivo gerado
cat alembic/versions/xxx_*.py

# 3. Aplicar
alembic upgrade head
```

### PASSO 6: Finalizacao

```bash
# 1. Auditoria completa do modulo
pylint --rcfile=.pylintrc modules/modulo/

# 2. Todos os testes
pytest tests/ -v

# 3. Cobertura geral
pytest tests/ --cov=modules --cov-report=term-missing

# 4. Se tudo OK, documentar
echo "Sprint XX concluido - $(date)" >> docs/PROGRESSO_GERAL.md
```

---

## COMANDOS RAPIDOS

### Auditoria Completa

```bash
# Script de auditoria
cd /opt/erp-conecta-mais/backend
source venv/bin/activate

echo "=== PYLINT ===" && \
pylint --rcfile=.pylintrc modules/ core/ --score=y && \
echo "" && \
echo "=== MYPY ===" && \
mypy modules/ core/ --ignore-missing-imports && \
echo "" && \
echo "=== BLACK ===" && \
black --check modules/ core/ && \
echo "" && \
echo "=== ISORT ===" && \
isort --check-only modules/ core/ && \
echo "" && \
echo "=== BANDIT ===" && \
bandit -r modules/ core/ -ll && \
echo "" && \
echo "=== PYTEST ===" && \
pytest tests/ -v --cov=modules --cov-report=term-missing
```

### Formatacao Automatica

```bash
# Formatar todos os arquivos
black modules/ core/ tests/
isort modules/ core/ tests/
```

### Verificar Arquivo Especifico

```bash
# Verificacao rapida de um arquivo
FILE="modules/crm/models/proposal.py"

python -m py_compile $FILE && \
pylint --rcfile=.pylintrc $FILE && \
mypy $FILE --ignore-missing-imports && \
black --check $FILE && \
isort --check-only $FILE
```

---

## TEMPLATES DE CODIGO

### Template de Import

```python
"""
[Descricao do modulo].

Este modulo implementa [funcionalidade].
"""

# Standard library
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

# Third party
from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID

# Local
from core.database import Base
from core.logging import logger
```

### Template de Model

```python
class NomeEntidade(Base):
    """
    Representa [descricao].

    Attributes:
        id: Identificador UUID
        nome: Nome da entidade
    """

    __tablename__ = "nome_entidades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String(200), nullable=False)
    # ... mais campos

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NomeEntidade(id={self.id}, nome='{self.nome}')>"
```

### Template de Endpoint

```python
@router.get("/", response_model=EntidadeList)
async def listar_entidades(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> EntidadeList:
    """
    Lista entidades com paginacao.

    Args:
        page: Numero da pagina
        page_size: Itens por pagina
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Lista paginada de entidades
    """
    repo = EntidadeRepository(db)
    skip = (page - 1) * page_size
    items, total = repo.get_all(skip=skip, limit=page_size)

    return EntidadeList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )
```

### Template de Teste

```python
"""Testes para [Entidade]."""

import pytest
from decimal import Decimal
from uuid import uuid4

from modules.modulo.models.entidade import Entidade


class TestEntidadeModel:
    """Testes do model."""

    def test_criar_valido(self) -> None:
        """Testa criacao valida."""
        obj = Entidade(nome="Teste", valor=Decimal("100.00"))
        assert obj.nome == "Teste"
        assert obj.valor == Decimal("100.00")

    def test_repr(self) -> None:
        """Testa __repr__."""
        obj = Entidade(id=uuid4(), nome="Teste")
        assert "Entidade" in repr(obj)
        assert "Teste" in repr(obj)
```

---

## CHECKLIST PRE-COMMIT

Antes de QUALQUER commit:

```
[ ] Pylint >= 99/100 em todos os arquivos modificados
[ ] Mypy sem errors
[ ] Black --check passa
[ ] Isort --check passa
[ ] Bandit sem high/critical
[ ] Todos os testes passando
[ ] Cobertura >= 85% nos arquivos novos
[ ] Docstrings em todas funcoes publicas
[ ] Type hints em todos os parametros e retornos
```

---

## RESOLUCAO DE PROBLEMAS

### Pylint "missing-function-docstring"

```python
# ANTES (erro)
def calcula_total(items):
    return sum(i.valor for i in items)

# DEPOIS (correto)
def calcula_total(items: list[Item]) -> Decimal:
    """
    Calcula total dos itens.

    Args:
        items: Lista de itens

    Returns:
        Soma dos valores
    """
    return sum(i.valor for i in items)
```

### Pylint "too-many-arguments"

```python
# ANTES (erro - 6+ argumentos)
def create_proposal(
    client_id, seller_id, items, discount, notes, template
):
    pass

# DEPOIS (correto - usar dataclass)
@dataclass
class ProposalInput:
    client_id: UUID
    seller_id: UUID
    items: list[dict]
    discount: Decimal = Decimal("0")
    notes: str = ""
    template: Optional[str] = None

def create_proposal(data: ProposalInput) -> Proposal:
    """Cria proposta."""
    pass
```

### Pylint "unused-argument"

```python
# Em controllers, current_user pode nao ser usado diretamente
# mas e necessario para autenticacao

# Adicionar disable com justificativa:
async def endpoint(
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> Response:
    """Endpoint que requer autenticacao."""
    pass
```

### Decimal vs Float

```python
# ERRADO - NUNCA fazer
price = 19.99
total = price * 3  # 59.970000000000006

# CORRETO - SEMPRE assim
from decimal import Decimal
price = Decimal("19.99")
total = price * 3  # Decimal("59.97")
```

---

## COMUNICACAO

### O que reportar apos cada sprint:

```markdown
## Sprint XX - [Nome]
**Data:** YYYY-MM-DD
**Status:** CONCLUIDO / EM ANDAMENTO / BLOQUEADO

### Entregaveis
- [x] Model X criado
- [x] Endpoints CRUD funcionando
- [x] Testes com 87% cobertura
- [ ] Integracao Y (pendente)

### Metricas
- Pylint: 100/100
- Cobertura: 87%
- Arquivos novos: 8
- Linhas adicionadas: 1.234

### Proximos Passos
1. Iniciar Sprint XX+1
2. Revisar integracao pendente

### Bloqueios
- Nenhum
```

---

## LEMBRETES IMPORTANTES

```
1. NUNCA pular a auditoria de codigo
2. NUNCA usar float para dinheiro
3. NUNCA deploy na sexta-feira
4. NUNCA commit com testes falhando
5. SEMPRE documentar funcoes publicas
6. SEMPRE usar type hints
7. SEMPRE rodar pylint ANTES de continuar
8. SEMPRE manter score >= 99/100
```

---

*Instrucoes Claude Code - ERP Conecta Mais Fase 2*
*"Qualidade e inegociavel"*
