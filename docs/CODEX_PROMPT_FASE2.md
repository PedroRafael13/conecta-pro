# Prompt para Codex - Continuidade Módulo Operacional Fase 2

## Contexto do Projeto

**Projeto:** Conecta Pro - Sistema ERP de gestão para empresas de segurança e facilities
**Localização:** `/opt/conecta-pro/`
**URL Produção:** `https://erp.conectamais.pro`

### Stack Tecnológica

**Backend:**
- Python 3.12 + FastAPI
- SQLAlchemy (async) + Alembic para migrações
- PostgreSQL 16 + Redis 7
- Pydantic v2 para schemas
- Arquitetura: Controllers → Repositories → Models

**Frontend:**
- Next.js 15 + React 19 + TypeScript
- Tailwind CSS + shadcn/ui components
- Orval para geração de API client a partir do OpenAPI
- React Query para cache e state

**Estrutura de Diretórios:**
```
/opt/conecta-pro/
├── backend/
│   ├── api/v1/              # Routers principais
│   ├── modules/operacional/ # Módulo atual
│   │   ├── controllers/     # Endpoints FastAPI
│   │   ├── repositories/    # Acesso a dados
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Lógica de negócio
│   ├── core/                # Auth, DB, Config
│   └── alembic/versions/    # Migrações
├── frontend/
│   ├── src/app/modulos/operacional/  # Páginas Next.js
│   ├── src/components/operacional/   # Componentes
│   ├── src/api/generated/            # Código gerado Orval
│   ├── src/types/operacional.ts      # Tipos TypeScript
│   ├── src/lib/services/             # Services manuais
│   └── orval.config.ts               # Config Orval
└── docker-compose.yml
```

---

## O Que Foi Concluído na Sessão Anterior (Fase 1)

### Backend Implementado:
1. **Post (Postos de Trabalho)** - CRUD completo
   - `post_controller.py` - Endpoints REST
   - `post_repository.py` - Queries com filtros
   - Model e Schemas alinhados

2. **Scale (Escalas)** - CRUD + Workflow
   - `scale_controller.py` - Endpoints incluindo geração automática
   - Workflow: draft → pending_approval → approved → published

3. **Shift (Turnos)** - CRUD + Check-in/out
   - `shift_controller.py` - Endpoints com check-in/check-out

4. **Allocation (Alocações)** - CRUD básico
   - `allocation_controller.py` - Endpoints prontos

### Frontend Implementado:
1. **Dashboard Operacional** - `/modulos/operacional/page.tsx`
2. **Listagem de Postos** - `/modulos/operacional/postos/page.tsx`
   - Tabela com paginação, busca, filtros
   - Modais: visualização, criação/edição, exclusão
3. **Listagem de Escalas** - `/modulos/operacional/escalas/page.tsx`
   - Cards com filtros
   - Modal de geração automática

---

## Tarefas da Fase 2 (Para Implementar)

### 1. MÓDULO ALOCAÇÕES (Frontend)
Criar página `/modulos/operacional/alocacoes/page.tsx`:

**Funcionalidades:**
- Listagem em tabela com colunas: Funcionário, Posto, Data Início, Status, Ações
- Filtros: por posto, por funcionário, status, período
- Modal de criação com seleção de funcionário e posto
- Modal de visualização detalhada
- Ação de encerramento (terminate)
- Integração com endpoint `/api/v1/operacional/allocations`

**Componentes necessários:**
- `src/components/operacional/allocation-form-modal.tsx`
- `src/components/operacional/allocation-detail-modal.tsx`

### 2. MÓDULO TURNOS (Frontend)
Criar página `/modulos/operacional/turnos/page.tsx`:

**Funcionalidades:**
- Visualização em calendário (semana/mês)
- Lista de turnos do dia com status
- Check-in/Check-out com registro de horário
- Marcação de faltas com motivo
- Filtros: por escala, por funcionário, por posto, período
- Integração com endpoint `/api/v1/operacional/shifts`

**Componentes necessários:**
- `src/components/operacional/shift-calendar.tsx`
- `src/components/operacional/shift-check-modal.tsx`
- `src/components/operacional/shift-day-view.tsx`

### 3. INTEGRAÇÃO FUNCIONÁRIOS
Criar hook e service para buscar funcionários disponíveis:
- `src/hooks/useEmployees.ts`
- `src/lib/services/employees.ts`
- Endpoint já existe: `/api/v1/hr/employees`

### 4. RELATÓRIOS BÁSICOS
Criar página `/modulos/operacional/relatorios/page.tsx`:
- Relatório de cobertura (postos x alocações)
- Relatório de horas trabalhadas
- Relatório de custos estimados

---

## Padrões de Código a Seguir

### Backend - Controller (FastAPI)
```python
"""
Controller (endpoints) para [Entidade].
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operacional.repositories.[repo] import [Repo]Repository
from modules.operacional.schemas.[schema] import (
    [Entity]Create,
    [Entity]Filter,
    [Entity]ListResponse,
    [Entity]Response,
    [Entity]Update,
)

router = APIRouter(prefix="/[entities]", tags=["Operations - [Entities]"])


@router.post("/", response_model=[Entity]Response, status_code=status.HTTP_201_CREATED)
async def create_[entity](
    data: [Entity]Create,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> [Entity]Response:
    """
    Cria um novo [entity].
    """
    repo = [Entity]Repository(db)
    entity = await repo.create(data)

    logger.info(f"[Entity] criado por {current_user.email}: {entity.id}")
    return [Entity]Response.model_validate(entity)


@router.get("/", response_model=[Entity]ListResponse)
async def list_[entities](
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    # filtros...
) -> [Entity]ListResponse:
    """
    Lista [entities] com filtros e paginação.
    """
    repo = [Entity]Repository(db)
    filters = [Entity]Filter(...)

    items, total = await repo.list(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return [Entity]ListResponse(
        items=[[Entity]Response.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
```

### Backend - Schema (Pydantic)
```python
"""
Schemas Pydantic para [Entidade].
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class [Entity]Base(BaseModel):
    """Schema base para [Entity]."""

    campo: str = Field(..., description="Descrição")
    opcional: Optional[str] = Field(None, description="Descrição")


class [Entity]Create([Entity]Base):
    """Schema para criação."""
    pass


class [Entity]Update(BaseModel):
    """Schema para atualização parcial."""

    campo: Optional[str] = None


class [Entity]Response(BaseModel):
    """Schema de resposta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    campo: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class [Entity]ListResponse(BaseModel):
    """Schema para listagem paginada."""

    items: List[[Entity]Response]
    total: int
    page: int
    page_size: int
    total_pages: int


class [Entity]Filter(BaseModel):
    """Schema para filtros de busca."""

    campo: Optional[str] = None
```

### Frontend - Página (Next.js)
```typescript
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Search,
  Plus,
  Filter,
  Eye,
  Edit2,
  Trash2,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ConfirmModal } from '@/components/ui/modal';
import { useAuth } from '@/hooks/useAuth';
import { use[Entities], use[Entity]Stats } from '@/hooks/use[Entities]';
import { [entities]Service } from '@/lib/services/[entities]';
import { getErrorMessage } from '@/lib/api';
import type { [Entity] } from '@/types/operacional';

export default function [Entities]Page() {
  const router = useRouter();
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const {
    [entities],
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    setPage,
    refresh,
  } = use[Entities]({ initialPageSize: 10 });

  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Modal states
  const [selected[Entity], setSelected[Entity]] = useState<[Entity] | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters({ ...filters, search: searchTerm || undefined });
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Handlers...

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        {/* ... */}
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        {/* Search and Filters */}
        {/* Table */}
        {/* Pagination */}
      </main>

      {/* Modals */}
    </div>
  );
}
```

### Frontend - Hook
```typescript
import { useState, useEffect, useCallback } from 'react';
import { [entities]Service } from '@/lib/services/[entities]';
import type { [Entity], [Entity]Filter, PaginatedResponse } from '@/types/operacional';

interface Use[Entities]Options {
  initialPageSize?: number;
  initialFilters?: [Entity]Filter;
}

export function use[Entities](options: Use[Entities]Options = {}) {
  const { initialPageSize = 20, initialFilters = {} } = options;

  const [[entities], set[Entities]] = useState<[Entity][]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<[Entity]Filter>(initialFilters);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await [entities]Service.list({
        page,
        page_size: pageSize,
        ...filters,
      });

      set[Entities](response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    [entities],
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    setPage,
    refresh: fetchData,
  };
}
```

### Frontend - Service
```typescript
import { api } from '@/lib/api';
import type { [Entity], [Entity]Create, [Entity]Update, [Entity]Filter, PaginatedResponse } from '@/types/operacional';

const BASE_URL = '/api/v1/operacional/[entities]';

export const [entities]Service = {
  async list(params: [Entity]Filter & { page?: number; page_size?: number }): Promise<PaginatedResponse<[Entity]>> {
    const response = await api.get<PaginatedResponse<[Entity]>>(BASE_URL, { params });
    return response.data;
  },

  async getById(id: string): Promise<[Entity]> {
    const response = await api.get<[Entity]>(`${BASE_URL}/${id}`);
    return response.data;
  },

  async create(data: [Entity]Create): Promise<[Entity]> {
    const response = await api.post<[Entity]>(BASE_URL, data);
    return response.data;
  },

  async update(id: string, data: [Entity]Update): Promise<[Entity]> {
    const response = await api.patch<[Entity]>(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`${BASE_URL}/${id}`);
  },
};
```

---

## Orval - Geração de API Client

Após criar/modificar endpoints backend:

1. Atualizar OpenAPI snapshot:
```bash
cd /opt/conecta-pro/frontend
curl -o openapi-snapshot.json https://erp.conectamais.pro/openapi.json
```

2. Gerar código:
```bash
npx orval --config orval.config.ts
```

**Configuração atual do Orval:**
- Tags filtradas: `['Operacional', 'Escalas', 'Postos', 'Vigilantes']`
- Output: `./src/api/generated/operacional.ts`
- Client: `react-query`
- Mutator: `./src/lib/api.ts` (axiosInstance)

---

## Comandos Úteis

```bash
# Backend - Rodar servidor dev
cd /opt/conecta-pro/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Frontend - Rodar dev
cd /opt/conecta-pro/frontend
npm run dev

# Docker - Rebuild e restart
docker compose build backend --no-cache && docker compose up -d backend
docker compose build frontend --no-cache && docker compose up -d frontend

# Logs
docker logs -f conecta-backend
docker logs -f conecta-frontend

# Migrações Alembic
cd /opt/conecta-pro/backend
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

---

## Endpoints Backend Existentes

### Postos
- `GET /api/v1/operacional/posts` - Listar
- `POST /api/v1/operacional/posts` - Criar
- `GET /api/v1/operacional/posts/{id}` - Buscar
- `PATCH /api/v1/operacional/posts/{id}` - Atualizar
- `DELETE /api/v1/operacional/posts/{id}` - Remover
- `GET /api/v1/operacional/posts/stats` - Estatísticas

### Escalas
- `GET /api/v1/operacional/scales` - Listar
- `POST /api/v1/operacional/scales` - Criar
- `GET /api/v1/operacional/scales/{id}` - Buscar
- `PATCH /api/v1/operacional/scales/{id}` - Atualizar
- `DELETE /api/v1/operacional/scales/{id}` - Remover
- `POST /api/v1/operacional/scales/generate` - Gerar automática
- `POST /api/v1/operacional/scales/{id}/approve` - Aprovar
- `POST /api/v1/operacional/scales/{id}/publish` - Publicar

### Turnos
- `GET /api/v1/operacional/shifts` - Listar
- `POST /api/v1/operacional/shifts` - Criar
- `GET /api/v1/operacional/shifts/{id}` - Buscar
- `PATCH /api/v1/operacional/shifts/{id}` - Atualizar
- `DELETE /api/v1/operacional/shifts/{id}` - Remover
- `GET /api/v1/operacional/shifts/today` - Turnos de hoje
- `GET /api/v1/operacional/shifts/scale/{scale_id}` - Por escala
- `POST /api/v1/operacional/shifts/{id}/check-in` - Check-in
- `POST /api/v1/operacional/shifts/{id}/check-out` - Check-out
- `POST /api/v1/operacional/shifts/{id}/mark-missed` - Marcar falta

### Alocações
- `GET /api/v1/operacional/allocations` - Listar
- `POST /api/v1/operacional/allocations` - Criar
- `GET /api/v1/operacional/allocations/{id}` - Buscar
- `PATCH /api/v1/operacional/allocations/{id}` - Atualizar
- `DELETE /api/v1/operacional/allocations/{id}` - Remover
- `GET /api/v1/operacional/allocations/current` - Vigentes
- `GET /api/v1/operacional/allocations/post/{post_id}` - Por posto
- `GET /api/v1/operacional/allocations/employee/{employee_id}` - Por funcionário
- `GET /api/v1/operacional/allocations/available-employees` - Disponíveis
- `POST /api/v1/operacional/allocations/{id}/terminate` - Encerrar

---

## Prioridade de Implementação

1. **Página de Alocações** (mais crítico - vincula funcionários aos postos)
2. **Página de Turnos** (calendário e check-in/out)
3. **Integração com Funcionários** (select de funcionários nas telas)
4. **Relatórios** (cobertura, horas, custos)

---

## Observações Importantes

- Todos os endpoints requerem autenticação (Bearer token)
- Usar `model_validate()` ao retornar dados do banco
- Soft delete padrão (campo `is_active`)
- Logs com `logger.info()` para ações importantes
- Paginação padrão: page=1, page_size=20
- Filtros são opcionais e combinados com AND
- Frontend usa CSS variables do Tailwind: `hsl(var(--background))`, etc.
- Modais usam componentes de `@/components/ui/modal`
- Ícones do Lucide React

---

## Arquivos de Referência (Leia Primeiro)

**Backend:**
- `/opt/conecta-pro/backend/modules/operacional/controllers/post_controller.py`
- `/opt/conecta-pro/backend/modules/operacional/controllers/allocation_controller.py`
- `/opt/conecta-pro/backend/modules/operacional/schemas/allocation.py`

**Frontend:**
- `/opt/conecta-pro/frontend/src/app/modulos/operacional/postos/page.tsx`
- `/opt/conecta-pro/frontend/src/types/operacional.ts`
- `/opt/conecta-pro/frontend/src/lib/api.ts`
- `/opt/conecta-pro/frontend/orval.config.ts`

---

Ao implementar, siga a mesma estrutura e padrões dos arquivos existentes. Mantenha consistência no estilo de código, nomenclatura e organização.
