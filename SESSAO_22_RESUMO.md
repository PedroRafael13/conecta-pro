# Sessao 22 - Conecta PRO

**Data:** 2026-01-27
**Foco:** Correcao do modulo DIARISTAS

---

## O QUE FOI FEITO

### 1. Correcao Completa do Modulo DIARISTAS (Backend)

O modulo DIARISTAS estava retornando erro 500 e forcando logout. Problemas corrigidos:

#### 1.1 Prefixo de Rota
- **Arquivo:** `/opt/conecta-pro/backend/main_production.py`
- **Problema:** Rota duplicada ou incorreta
- **Solucao:** Prefixo correto `/operacional/diaristas`

#### 1.2 Repositorio Async
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/repositories/diarist_repository.py`
- **Problema:** Usava sintaxe sincrona (`db.query()`) com AsyncSession
- **Solucao:** Convertido para `select()` + `await db.execute()`

#### 1.3 Sintaxe require_roles
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/controllers/diarist_controller.py`
- **Problema:** `require_roles(["admin", "sindico"])` - lista como argumento
- **Solucao:** `require_roles("admin", "sindico")` - argumentos separados

#### 1.4 Tipos de Coluna no Banco
- **Problema:** Banco usava tipos enum customizados (diarist_type_array[], weekday_array[])
- **Solucao:** Alterado para tipos flexiveis via SQL:
```sql
ALTER TABLE diarists ALTER COLUMN tipos_servico TYPE text[] USING tipos_servico::text[];
ALTER TABLE diarists ALTER COLUMN dias_disponiveis TYPE text[] USING dias_disponiveis::text[];
ALTER TABLE diarists ALTER COLUMN status TYPE varchar(30) USING status::text;
```

#### 1.5 Model SQLAlchemy
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/models/diarist.py`
- **Problema:** Colunas JSONB incompativeis com banco
- **Solucao:** Alterado para `ARRAY(String)`:
```python
tipos_servico = Column(ARRAY(String), default=[])
especialidades = Column(ARRAY(String), default=[])
dias_disponiveis = Column(ARRAY(String), default=[])
```

#### 1.6 Enum Status
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/services/diarist_service.py`
- **Problema:** `DiaristStatus.PENDENTE` nao existe no enum
- **Solucao:** Alterado para `DiaristStatus.ATIVO.value`

#### 1.7 JoinedLoad Removido
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/repositories/diarist_repository.py`
- **Problema:** joinedload carregava tabelas relacionadas com estrutura diferente do banco
- **Solucao:** Removido joinedload do metodo `get_by_id()`

#### 1.8 Sintaxe APIRouter
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/controllers/diarist_controller.py`
- **Problema:** `router = APIRouter(tags=["Diaristas"))` - parentese extra
- **Solucao:** `router = APIRouter(tags=["Diaristas"])`

#### 1.9 DiaristListResponse
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/diaristas/controllers/diarist_controller.py`
- **Problema:** Retornava `skip/limit` mas schema esperava `page/page_size/pages`
- **Solucao:** Calculado paginacao corretamente

### 2. Importacao Occurrence
- **Arquivo:** `/opt/conecta-pro/backend/modules/operacional/models/__init__.py`
- **Problema:** Mapper Post nao encontrava Occurrence
- **Solucao:** Adicionado import de Occurrence para registrar no SQLAlchemy

---

## RESULTADO DOS TESTES BACKEND

| Endpoint | Metodo | Status | Resultado |
|----------|--------|--------|-----------|
| /operacional/diaristas/ | GET | 200 | OK |
| /operacional/diaristas/ | POST | 201 | OK |
| /operacional/diaristas/{id} | GET | 200 | OK |
| /operacional/diaristas/{id} | PUT | 200 | OK |
| /operacional/diaristas/{id} | DELETE | 204 | OK |

---

## PROBLEMA PENDENTE (PONTO DE PARTIDA PROXIMA SESSAO)

### Erro Client-Side no Frontend

**Sintoma:** Ao clicar em "+ Novo Diarista" no frontend, aparece:
```
Application error: a client-side exception has occurred while loading erp.conectamais.pro
(see the browser console for more information)
```

**Localizacao provavel:**
- `/opt/conecta-pro/frontend/src/app/modulos/operacional/diaristas/`
- Formulario de criacao de diarista
- Possivel incompatibilidade entre schema frontend e backend

**Investigar:**
1. Console do browser para ver erro exato
2. Componente de formulario de diarista
3. Schema/tipos TypeScript vs schema Pydantic
4. Campos obrigatorios no formulario vs API

---

## ARQUIVOS MODIFICADOS NESTA SESSAO

```
/opt/conecta-pro/backend/
├── main_production.py (prefixo diaristas)
├── core/config/settings.py (LLM config)
├── modules/
│   ├── operacional/
│   │   ├── models/__init__.py (import Occurrence)
│   │   └── diaristas/
│   │       ├── models/diarist.py (tipos ARRAY)
│   │       ├── repositories/diarist_repository.py (async, sem joinedload)
│   │       ├── services/diarist_service.py (ATIVO.value)
│   │       └── controllers/diarist_controller.py (require_roles, paginacao)
│   └── ai/bartolo/ (integracao OpenAI)
├── requirements.txt (openai>=1.0.0)
└── .env (OPENAI_API_KEY, LLM configs)

/opt/conecta-pro/
├── docker-compose.yml (LLM env vars)
└── .env (LLM configs)
```

---

## BANCO DE DADOS - ALTERACOES

```sql
-- Tabela diarists - tipos alterados
ALTER TABLE diarists ALTER COLUMN tipos_servico TYPE text[];
ALTER TABLE diarists ALTER COLUMN dias_disponiveis TYPE text[];
ALTER TABLE diarists ALTER COLUMN status TYPE varchar(30);
```

---

## CONTEXTO SESSAO ANTERIOR

- Bartolo AI integrado com OpenAI GPT-4-turbo-preview
- Auditoria OPERACIONAL: 7.5/10 (DIARISTAS era 0/10, agora corrigido no backend)
- Plano original em `/root/.claude/plans/wiggly-floating-giraffe.md`

---

## PROXIMOS PASSOS RECOMENDADOS

1. **URGENTE:** Corrigir erro client-side no formulario de diaristas
2. Verificar outros endpoints de diaristas (assignments, schedules, payments)
3. Testar integracao completa frontend-backend
4. Continuar plano original (Sentry, PWA, Analytics)
