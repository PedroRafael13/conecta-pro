---
title: Backend Development
description: Desenvolvimento Python/FastAPI para Conecta PRO
stack: [python, fastapi, sqlalchemy, pydantic]
---

# backend-dev

Desenvolvimento Python/FastAPI para Conecta PRO

## Uso

```yaml
skills:
  - backend-dev
```

---

## Padrão de Camadas (OBRIGATÓRIO)

```
Controller → Service → Repository → Model
```

### 1. Controller (`controllers/{entity}_controller.py`)
```python
from fastapi import APIRouter, Depends
from modules.{modulo}.schemas.{entity}_schema import {Entity}Create, {Entity}Response
from modules.{modulo}.services.{entity}_service import {Entity}Service, get_{entity}_service

router = APIRouter(prefix="/{entities}", tags=["{Entities}"])

@router.post("", response_model={Entity}Response)
async def create_{entity}(
    data: {Entity}Create,
    service: {Entity}Service = Depends(get_{entity}_service)
):
    """Criar novo {entity}."""
    return await service.create(data)

@router.get("/{id}", response_model={Entity}Response)
async def get_{entity}(
    id: UUID,
    service: {Entity}Service = Depends(get_{entity}_service)
):
    """Obter {entity} por ID."""
    return await service.get_by_id(id)
```

### 2. Service (`services/{entity}_service.py`)
```python
from modules.{modulo}.repositories.{entity}_repository import {Entity}Repository

class {Entity}Service:
    def __init__(self, repo: {Entity}Repository):
        self._repo = repo

    async def create(self, data: {Entity}Create) -> {Entity}:
        return await self._repo.create(data)

    async def get_by_id(self, id: UUID) -> {Entity}:
        entity = await self._repo.get_by_id(id)
        if not entity:
            raise HTTPException(status_code=404, detail="{Entity} not found")
        return entity

def get_{entity}_service():
    return {Entity}Service({Entity}Repository())
```

### 3. Repository (`repositories/{entity}_repository.py`)
```python
from modules.{modulo}.models.{entity}_model import {Entity}
from modules.core.database import get_session

class {Entity}Repository:
    async def create(self, data: {Entity}Create) -> {Entity}:
        async with get_session() as session:
            entity = {Entity}(**data.model_dump())
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def get_by_id(self, id: UUID) -> {Entity} | None:
        async with get_session() as session:
            result = await session.execute(
                select({Entity}).where({Entity}.id == id)
            )
            return result.scalar_one_or_none()
```

### 4. Model (`models/{entity}_model.py`)
```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from modules.core.database import Base

class {Entity}(Base):
    __tablename__ = "{entities}"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
```

### 5. Schema (`schemas/{entity}_schema.py`)
```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class {Entity}Base(BaseModel):
    name: str

class {Entity}Create({Entity}Base):
    pass

class {Entity}Update({Entity}Base):
    name: str | None = None

class {Entity}Response({Entity}Base):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
```

---

## Convenções

- **Async:** SEMPRE usar async/await para I/O
- **Erros:** NUNCA bare except, sempre específico
- **Soft Delete:** Sempre ter deleted_at
- **Types:** Usar mypy strict
- **Imports:** isort (stdlib, third-party, local)

---

## Comandos

```bash
pytest tests/modules/{modulo}/ -v
ruff check modules/{modulo}/
black modules/{modulo}/
mypy modules/{modulo}/
```
