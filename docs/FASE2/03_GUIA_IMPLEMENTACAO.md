# GUIA DE IMPLEMENTACAO - FASE 2
## ERP CONECTA MAIS - PASSO A PASSO DETALHADO

**Versao:** 2.0
**Data:** Janeiro 2026
**Executor:** Claude Opus 4.5

---

## VISAO GERAL

Este guia fornece instrucoes passo-a-passo para implementacao de cada modulo da Fase 2.
Siga EXATAMENTE a ordem indicada para garantir consistencia e qualidade.

---

## PREPARACAO DO AMBIENTE

### 1. Verificacao Pre-Requisitos

```bash
# Executar ANTES de qualquer sprint
cd /opt/erp-conecta-mais/backend

# 1. Verificar Python e ambiente virtual
python3 --version  # Deve ser 3.12+
source venv/bin/activate

# 2. Verificar dependencias
pip list | grep -E "(fastapi|sqlalchemy|pydantic|pytest)"

# 3. Verificar banco de dados
docker ps | grep postgres

# 4. Verificar Redis
docker ps | grep redis

# 5. Verificar qualidade atual
pylint --rcfile=.pylintrc modules/ core/ --score=y
```

### 2. Configuracao de Ferramentas de Qualidade

```bash
# Instalar ferramentas se nao existirem
pip install pylint mypy black isort bandit pytest pytest-cov pytest-asyncio

# Verificar configuracoes
cat .pylintrc  # Deve existir
cat pyproject.toml  # Deve ter [tool.black] e [tool.isort]
```

### 3. Estrutura de Diretorios Fase 2

```
/opt/erp-conecta-mais/backend/
├── modules/
│   ├── crm/                 # Existente - Expandir
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── controllers/
│   │   └── services/
│   ├── financial/           # NOVO - Sprint 22+
│   ├── hr/                   # NOVO - Sprint 15+
│   ├── operations/           # NOVO - Sprint 30+
│   ├── bi/                   # NOVO - Sprint 30
│   └── integrations/         # NOVO - Sprint 26+
├── core/
│   ├── auth/
│   ├── cache/
│   ├── logging/
│   └── events/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## PADRAO DE IMPLEMENTACAO POR ENTIDADE

### Ordem de Criacao (SEMPRE seguir esta ordem)

```
1. Model (SQLAlchemy)     -> models/<entidade>.py
2. Schema (Pydantic)      -> schemas/<entidade>.py
3. Repository (CRUD)      -> repositories/<entidade>_repository.py
4. Service (Logica)       -> services/<entidade>_service.py
5. Controller (API)       -> controllers/<entidade>_controller.py
6. Tests (Unitarios)      -> tests/test_<entidade>.py
7. Tests (Integracao)     -> tests/integration/test_<entidade>_api.py
```

### Template Model

```python
"""
Model para [Entidade].

Este modulo define o modelo SQLAlchemy para [Entidade],
incluindo campos, relacionamentos e validacoes.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Entidade(Base):
    """
    Representa [descricao da entidade].

    Attributes:
        id: Identificador unico UUID
        nome: Nome da entidade
        valor: Valor monetario (Decimal)
        ativo: Status de ativacao
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "entidades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String(200), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    valor = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id"), nullable=True)
    parent = relationship("Parent", back_populates="entidades")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string da entidade."""
        return f"<Entidade(id={self.id}, nome='{self.nome}')>"
```

### Template Schema

```python
"""
Schemas Pydantic para [Entidade].

Define os schemas de entrada, saida e atualizacao
para a API REST.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class EntidadeBase(BaseModel):
    """Schema base com campos comuns."""

    nome: str = Field(..., min_length=1, max_length=200, description="Nome da entidade")
    descricao: Optional[str] = Field(None, max_length=2000, description="Descricao")
    valor: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Valor monetario"
    )

    @field_validator("valor", mode="before")
    @classmethod
    def validate_valor(cls, value: any) -> Decimal:
        """Garante que valor e Decimal com 2 casas."""
        if isinstance(value, float):
            value = Decimal(str(value))
        if isinstance(value, str):
            value = Decimal(value)
        return value.quantize(Decimal("0.01"))


class EntidadeCreate(EntidadeBase):
    """Schema para criacao de entidade."""

    parent_id: Optional[UUID] = Field(None, description="ID do parent")


class EntidadeUpdate(BaseModel):
    """Schema para atualizacao parcial."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    valor: Optional[Decimal] = Field(None, ge=0)
    ativo: Optional[bool] = None


class EntidadeResponse(EntidadeBase):
    """Schema de resposta com todos os campos."""

    id: UUID
    ativo: bool
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class EntidadeList(BaseModel):
    """Schema para listagem paginada."""

    items: list[EntidadeResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

### Template Repository

```python
"""
Repository para [Entidade].

Implementa operacoes CRUD e queries especializadas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from core.logging import logger
from modules.modulo.models.entidade import Entidade


class EntidadeRepository:
    """
    Repository para operacoes de Entidade.

    Implementa o padrao Repository para abstrair
    acesso ao banco de dados.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao do SQLAlchemy
        """
        self.db = db

    def get_by_id(self, entidade_id: UUID) -> Optional[Entidade]:
        """
        Busca entidade por ID.

        Args:
            entidade_id: UUID da entidade

        Returns:
            Entidade ou None se nao encontrada
        """
        return self.db.query(Entidade).filter(Entidade.id == entidade_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None
    ) -> tuple[list[Entidade], int]:
        """
        Lista entidades com paginacao.

        Args:
            skip: Registros a pular
            limit: Limite de registros
            ativo: Filtro por status

        Returns:
            Tupla (lista de entidades, total)
        """
        query = self.db.query(Entidade)

        if ativo is not None:
            query = query.filter(Entidade.ativo == ativo)

        total = query.count()
        items = query.order_by(Entidade.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def create(self, **kwargs: any) -> Entidade:
        """
        Cria nova entidade.

        Args:
            **kwargs: Campos da entidade

        Returns:
            Entidade criada
        """
        entidade = Entidade(**kwargs)
        self.db.add(entidade)
        self.db.commit()
        self.db.refresh(entidade)

        logger.info(
            "Entidade criada",
            extra={"entidade_id": str(entidade.id), "nome": entidade.nome}
        )

        return entidade

    def update(self, entidade: Entidade, **kwargs: any) -> Entidade:
        """
        Atualiza entidade existente.

        Args:
            entidade: Entidade a atualizar
            **kwargs: Campos a atualizar

        Returns:
            Entidade atualizada
        """
        for key, value in kwargs.items():
            if value is not None:
                setattr(entidade, key, value)

        self.db.commit()
        self.db.refresh(entidade)

        logger.info(
            "Entidade atualizada",
            extra={"entidade_id": str(entidade.id)}
        )

        return entidade

    def delete(self, entidade: Entidade, soft: bool = True) -> bool:
        """
        Remove entidade.

        Args:
            entidade: Entidade a remover
            soft: Se True, apenas desativa

        Returns:
            True se removida
        """
        if soft:
            entidade.ativo = False
            self.db.commit()
        else:
            self.db.delete(entidade)
            self.db.commit()

        logger.info(
            "Entidade removida",
            extra={"entidade_id": str(entidade.id), "soft": soft}
        )

        return True
```

### Template Controller

```python
"""
Controller para [Entidade].

Define endpoints REST para operacoes CRUD.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.modulo.repositories.entidade_repository import EntidadeRepository
from modules.modulo.schemas.entidade import (
    EntidadeCreate,
    EntidadeList,
    EntidadeResponse,
    EntidadeUpdate,
)

router = APIRouter(prefix="/entidades", tags=["Entidades"])


@router.get("/", response_model=EntidadeList)
async def listar_entidades(
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por pagina"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> EntidadeList:
    """
    Lista entidades com paginacao.

    Args:
        page: Numero da pagina (1-based)
        page_size: Quantidade por pagina
        ativo: Filtro opcional por status
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Lista paginada de entidades
    """
    repo = EntidadeRepository(db)
    skip = (page - 1) * page_size

    items, total = repo.get_all(skip=skip, limit=page_size, ativo=ativo)

    pages = (total + page_size - 1) // page_size

    return EntidadeList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{entidade_id}", response_model=EntidadeResponse)
async def obter_entidade(
    entidade_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> EntidadeResponse:
    """
    Obtem entidade por ID.

    Args:
        entidade_id: UUID da entidade
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Entidade encontrada

    Raises:
        HTTPException: 404 se nao encontrada
    """
    repo = EntidadeRepository(db)
    entidade = repo.get_by_id(entidade_id)

    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade nao encontrada"
        )

    return entidade


@router.post("/", response_model=EntidadeResponse, status_code=status.HTTP_201_CREATED)
async def criar_entidade(
    data: EntidadeCreate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> EntidadeResponse:
    """
    Cria nova entidade.

    Args:
        data: Dados da entidade
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Entidade criada
    """
    repo = EntidadeRepository(db)
    entidade = repo.create(**data.model_dump())

    logger.info(
        "Entidade criada via API",
        extra={"entidade_id": str(entidade.id), "user_id": str(current_user.id)}
    )

    return entidade


@router.patch("/{entidade_id}", response_model=EntidadeResponse)
async def atualizar_entidade(
    entidade_id: UUID,
    data: EntidadeUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> EntidadeResponse:
    """
    Atualiza entidade existente.

    Args:
        entidade_id: UUID da entidade
        data: Dados a atualizar
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Entidade atualizada

    Raises:
        HTTPException: 404 se nao encontrada
    """
    repo = EntidadeRepository(db)
    entidade = repo.get_by_id(entidade_id)

    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade nao encontrada"
        )

    entidade = repo.update(entidade, **data.model_dump(exclude_unset=True))

    return entidade


@router.delete("/{entidade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_entidade(
    entidade_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> None:
    """
    Remove entidade (soft delete).

    Args:
        entidade_id: UUID da entidade
        db: Sessao do banco
        current_user: Usuario autenticado

    Raises:
        HTTPException: 404 se nao encontrada
    """
    repo = EntidadeRepository(db)
    entidade = repo.get_by_id(entidade_id)

    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade nao encontrada"
        )

    repo.delete(entidade, soft=True)
```

### Template Teste Unitario

```python
"""
Testes unitarios para [Entidade].

Testa models, schemas e services isoladamente.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.modulo.models.entidade import Entidade
from modules.modulo.schemas.entidade import EntidadeCreate, EntidadeUpdate


class TestEntidadeModel:
    """Testes do model Entidade."""

    def test_criar_entidade_valida(self) -> None:
        """Testa criacao de entidade com dados validos."""
        entidade = Entidade(
            nome="Teste",
            valor=Decimal("100.00"),
            ativo=True
        )

        assert entidade.nome == "Teste"
        assert entidade.valor == Decimal("100.00")
        assert entidade.ativo is True

    def test_repr_entidade(self) -> None:
        """Testa representacao string."""
        entidade = Entidade(id=uuid4(), nome="Teste")
        repr_str = repr(entidade)

        assert "Entidade" in repr_str
        assert "Teste" in repr_str


class TestEntidadeSchemas:
    """Testes dos schemas Pydantic."""

    def test_create_schema_valido(self) -> None:
        """Testa schema de criacao valido."""
        data = EntidadeCreate(
            nome="Teste",
            valor=Decimal("100.00")
        )

        assert data.nome == "Teste"
        assert data.valor == Decimal("100.00")

    def test_create_schema_valor_float_convertido(self) -> None:
        """Testa conversao de float para Decimal."""
        data = EntidadeCreate(
            nome="Teste",
            valor=100.50  # type: ignore
        )

        assert isinstance(data.valor, Decimal)
        assert data.valor == Decimal("100.50")

    def test_update_schema_parcial(self) -> None:
        """Testa atualizacao parcial."""
        data = EntidadeUpdate(nome="Novo Nome")

        assert data.nome == "Novo Nome"
        assert data.valor is None
        assert data.ativo is None

    def test_create_schema_nome_vazio_erro(self) -> None:
        """Testa erro com nome vazio."""
        with pytest.raises(ValueError):
            EntidadeCreate(nome="", valor=Decimal("100.00"))

    def test_create_schema_valor_negativo_erro(self) -> None:
        """Testa erro com valor negativo."""
        with pytest.raises(ValueError):
            EntidadeCreate(nome="Teste", valor=Decimal("-100.00"))
```

---

## FLUXO DE IMPLEMENTACAO POR SPRINT

### Inicio de Sprint

```bash
# 1. Verificar ambiente
cd /opt/erp-conecta-mais/backend
source venv/bin/activate

# 2. Atualizar dependencias
pip install -r requirements.txt

# 3. Rodar testes existentes (devem passar)
pytest tests/ -v --tb=short

# 4. Verificar qualidade atual
pylint --rcfile=.pylintrc modules/ core/ --score=y
# Deve ser >= 99/100

# 5. Ler documentacao do sprint
cat /opt/erp-conecta-mais/docs/FASE2/sprints/sprint_XX.md
```

### Durante Sprint

```bash
# Apos cada arquivo criado:
# 1. Verificar sintaxe
python -m py_compile caminho/arquivo.py

# 2. Verificar qualidade
pylint --rcfile=.pylintrc caminho/arquivo.py

# 3. Formatar codigo
black caminho/arquivo.py
isort caminho/arquivo.py

# 4. Rodar testes do modulo
pytest tests/test_arquivo.py -v
```

### Finalizacao de Sprint

```bash
# 1. Auditoria completa
./scripts/audit.sh

# Ou manualmente:
echo "=== PYLINT ===" && pylint --rcfile=.pylintrc modules/ core/
echo "=== MYPY ===" && mypy modules/ core/ --ignore-missing-imports
echo "=== BLACK ===" && black --check modules/ core/
echo "=== ISORT ===" && isort --check-only modules/ core/
echo "=== BANDIT ===" && bandit -r modules/ core/ -ll
echo "=== PYTEST ===" && pytest tests/ -v --cov=modules --cov-report=term-missing

# 2. Verificar cobertura
pytest tests/ --cov=modules --cov-report=html
# Abrir htmlcov/index.html - deve ser >= 85%

# 3. Commit com mensagem semantica
git add .
git commit -m "feat: implementa [descricao do sprint]

- Adiciona model X
- Adiciona endpoints CRUD
- Adiciona testes unitarios
- Cobertura: XX%
- Pylint: 100/100"

# 4. Atualizar progresso
cat >> /opt/erp-conecta-mais/docs/PROGRESSO_GERAL.md << EOF

## Sprint XX - [Data]
- Status: CONCLUIDO
- Pylint: 100/100
- Cobertura: XX%
- Arquivos: N criados
EOF
```

---

## RESOLUCAO DE PROBLEMAS COMUNS

### Pylint Score Baixo

```bash
# Ver issues especificas
pylint --rcfile=.pylintrc arquivo.py --output-format=json | python -m json.tool

# Problemas comuns e solucoes:

# 1. missing-function-docstring
# Solucao: Adicionar docstring
def funcao():
    """Descricao da funcao."""
    pass

# 2. line-too-long
# Solucao: Quebrar linha ou ajustar codigo
valor = (
    primeiro_termo +
    segundo_termo +
    terceiro_termo
)

# 3. too-many-arguments
# Solucao: Usar dataclass ou dict
from dataclasses import dataclass

@dataclass
class Config:
    param1: str
    param2: int
    param3: bool

# 4. unused-argument (em controllers)
# Solucao: Adicionar disable com justificativa
async def endpoint(
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> Response:
    pass
```

### Testes Falhando

```bash
# Ver detalhes do erro
pytest tests/test_arquivo.py -v --tb=long

# Rodar teste especifico
pytest tests/test_arquivo.py::TestClasse::test_metodo -v

# Debug com print
pytest tests/test_arquivo.py -v -s

# Problemas comuns:

# 1. Fixture nao encontrada
# Solucao: Verificar conftest.py

# 2. Database error
# Solucao: Usar mock ou fixture isolada

# 3. Import error
# Solucao: Verificar PYTHONPATH
export PYTHONPATH=/opt/erp-conecta-mais/backend
```

### Migracao de Banco

```bash
# Criar nova migracao
cd /opt/erp-conecta-mais/backend
alembic revision --autogenerate -m "adiciona tabela X"

# Verificar migracao gerada
cat alembic/versions/xxx_adiciona_tabela_x.py

# Aplicar migracao
alembic upgrade head

# Rollback se necessario
alembic downgrade -1
```

---

## CHECKLIST POR TIPO DE ENTIDADE

### Entidade Simples (CRUD basico)
- [ ] Model com campos, __repr__, docstrings
- [ ] Schemas Create, Update, Response, List
- [ ] Repository com get_by_id, get_all, create, update, delete
- [ ] Controller com 5 endpoints (GET all, GET one, POST, PATCH, DELETE)
- [ ] Testes unitarios (model, schemas)
- [ ] Testes de API (todos endpoints)
- [ ] Migracao Alembic
- [ ] Pylint 100/100 em todos arquivos

### Entidade com Relacionamentos
- [ ] Tudo acima +
- [ ] Relacionamentos no model (ForeignKey, relationship)
- [ ] Nested schemas para response
- [ ] Repository com queries de join
- [ ] Testes de relacionamentos

### Entidade com Logica de Negocio
- [ ] Tudo acima +
- [ ] Service com logica especializada
- [ ] Validacoes complexas no service
- [ ] Eventos/notificacoes se aplicavel
- [ ] Testes do service (mocks)

### Entidade Financeira
- [ ] Tudo acima +
- [ ] Decimal para TODOS os valores monetarios
- [ ] Validacao de precisao (2 casas)
- [ ] Arredondamento ROUND_HALF_UP
- [ ] Testes de precisao financeira
- [ ] Auditoria de alteracoes

---

## PROXIMOS PASSOS

Apos ler este guia:
1. Ler `04_ROADMAP_SPRINTS.md` para cronograma
2. Ler skill do primeiro modulo a implementar
3. Ler sprint detalhado correspondente
4. Executar conforme instrucoes

---

*Guia de Implementacao - ERP Conecta Mais Fase 2*
*"Codigo de qualidade, um passo de cada vez"*
