# API Reference - Módulo Operacional

Documentação completa dos endpoints do módulo Operacional do Conecta PRO.

**Base URL:** `/api/v1/operacional`

---

## 📋 Índice

- [Postos de Trabalho](#-postos-de-trabalho)
- [Escalas](#-escalas)
- [Turnos](#-turnos)
- [Substituições](#-substituições)
- [Ocorrências](#-ocorrências)
- [Diaristas](#-diaristas)
- [Check-in/Check-out](#-check-incheck-out)

---

## 🏢 Postos de Trabalho

Base path: `/posts`

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/posts` | Criar novo posto | `POSTS_CREATE` |
| GET | `/posts` | Listar postos (com filtros) | `POSTS_VIEW` |
| GET | `/posts/stats` | Estatísticas de postos | `POSTS_VIEW` |
| GET | `/posts/{post_id}` | Buscar posto por ID | `POSTS_VIEW` |
| PATCH | `/posts/{post_id}` | Atualizar posto | `POSTS_EDIT` |
| DELETE | `/posts/{post_id}` | Remover posto (soft delete) | `POSTS_DELETE` |
| GET | `/posts/contract/{contract_id}` | Listar postos por contrato | `POSTS_VIEW` |
| GET | `/posts/client/{client_id}` | Listar postos por cliente | `POSTS_VIEW` |

### Query Parameters - Listar Postos

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página atual (padrão: 1) |
| `page_size` | int | Itens por página (padrão: 20, max: 100) |
| `post_type` | enum | Tipo: `FIXED`, `MOBILE`, `EVENT`, `EMERGENCY` |
| `status` | enum | Status: `ACTIVE`, `INACTIVE`, `SUSPENDED` |
| `shift_type` | enum | Turno: `12X36`, `24X72`, `5X2`, `6X1`, `CUSTOM` |
| `contract_id` | string | Filtrar por contrato |
| `client_id` | string | Filtrar por cliente |
| `city` | string | Filtrar por cidade |
| `state` | string | Filtrar por estado |
| `requires_armed` | bool | Requer armamento |
| `requires_vehicle` | bool | Requer veículo |
| `has_vacancy` | bool | Possui vagas |
| `search` | string | Busca textual |

### Exemplos

```bash
# Listar postos ativos
GET /api/v1/operacional/posts?status=ACTIVE&page=1&page_size=20

# Criar posto
POST /api/v1/operacional/posts
{
  "name": "Portaria Principal",
  "client_id": "uuid",
  "contract_id": "uuid",
  "post_type": "FIXED",
  "shift_type": "12X36",
  "address": {
    "street": "Rua Exemplo",
    "city": "São Paulo",
    "state": "SP"
  }
}
```

---

## 📅 Escalas

Base path: `/scales`

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/scales` | Criar escala (sem turnos) | `SCALES_CREATE` |
| POST | `/scales/generate` | Gerar escala com IA | `SCALES_CREATE` |
| GET | `/scales` | Listar escalas | `SCALES_VIEW_ALL` / `SCALES_VIEW_OWN` |
| GET | `/scales/stats` | Estatísticas de escalas | `SCALES_VIEW_ALL` / `SCALES_VIEW_OWN` |
| GET | `/scales/{scale_id}` | Buscar escala por ID | `SCALES_VIEW_ALL` / `SCALES_VIEW_OWN` |
| PATCH | `/scales/{scale_id}` | Atualizar escala | `SCALES_CREATE` |
| POST | `/scales/{scale_id}/submit` | Enviar para aprovação | `SCALES_CREATE` |
| POST | `/scales/{scale_id}/approve` | Aprovar escala | `SCALES_APPROVE` |
| POST | `/scales/{scale_id}/reject` | Rejeitar escala | `SCALES_APPROVE` |
| POST | `/scales/{scale_id}/publish` | Publicar escala | `SCALES_PUBLISH` |
| DELETE | `/scales/{scale_id}` | Remover escala | `SCALES_CREATE` |
| POST | `/scales/auto-generate` | Gerar escalas automáticas | `SCALES_CREATE` |

### Query Parameters - Listar Escalas

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página atual |
| `page_size` | int | Itens por página (max: 100) |
| `post_id` | string | Filtrar por posto |
| `scale_type` | enum | Tipo: `12X36`, `24X72`, `5X2`, `6X1`, `CUSTOM` |
| `status` | enum | Status: `DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `PUBLISHED`, `ARCHIVED` |
| `month` | int | Mês (1-12) |
| `year` | int | Ano (2020-2100) |
| `is_current_month` | bool | Mês atual |
| `created_by` | string | Filtrar por criador |

### Gerar Escala com IA

```bash
POST /api/v1/operacional/scales/generate
{
  "post_id": "uuid",
  "scale_type": "12X36",
  "month": 2,
  "year": 2026,
  "employee_ids": ["uuid1", "uuid2", "uuid3"],
  "config": {
    "min_employees_per_shift": 1,
    "max_consecutive_work_days": 6
  }
}
```

### Auto-Generate Escalas

```bash
POST /api/v1/operacional/scales/auto-generate?month=2&year=2026
```

---

## 🕐 Turnos

Base path: `/shifts`

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/shifts` | Criar turno | `SHIFTS_CREATE` |
| GET | `/shifts` | Listar turnos | `SHIFTS_VIEW_ALL` / `SHIFTS_VIEW_OWN` |
| GET | `/shifts/today` | Turnos de hoje | `SHIFTS_VIEW_ALL` / `SHIFTS_VIEW_OWN` |
| GET | `/shifts/scale/{scale_id}` | Turnos por escala | `SHIFTS_VIEW_ALL` / `SHIFTS_VIEW_OWN` |
| GET | `/shifts/{shift_id}` | Buscar turno por ID | `SHIFTS_VIEW_ALL` / `SHIFTS_VIEW_OWN` |
| PATCH | `/shifts/{shift_id}` | Atualizar turno | `SHIFTS_CREATE` |
| POST | `/shifts/{shift_id}/check-in` | Registrar entrada | `SHIFTS_CHECKIN` |
| POST | `/shifts/{shift_id}/check-out` | Registrar saída | `SHIFTS_CHECKIN` |
| POST | `/shifts/{shift_id}/mark-missed` | Marcar como falta | `SHIFTS_MARK_MISSED` |
| DELETE | `/shifts/{shift_id}` | Remover turno | `SHIFTS_CREATE` |
| PATCH | `/shifts/bulk` | Atualização em lote | `SHIFTS_CREATE` |

### Query Parameters - Listar Turnos

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página atual |
| `page_size` | int | Itens por página (max: 200) |
| `scale_id` | string | Filtrar por escala |
| `employee_id` | string | Filtrar por funcionário |
| `post_id` | string | Filtrar por posto |
| `status` | enum | Status: `SCHEDULED`, `CONFIRMED`, `IN_PROGRESS`, `COMPLETED`, `MISSED`, `CANCELLED` |
| `start_date` | date | Data inicial |
| `end_date` | date | Data final |
| `is_holiday` | bool | Feriado |
| `is_night_shift` | bool | Turno noturno |
| `is_off_day` | bool | Folga |
| `is_filled` | bool | Preenchido |
| `needs_substitution` | bool | Precisa substituição |

### Check-in

```bash
POST /api/v1/operacional/shifts/{shift_id}/check-in
{
  "actual_start_time": "2026-02-05T08:00:00",
  "notes": "Entrada registrada"
}
```

### Check-out

```bash
POST /api/v1/operacional/shifts/{shift_id}/check-out
{
  "actual_end_time": "2026-02-05T20:00:00",
  "actual_break_minutes": 60,
  "notes": "Saída registrada"
}
```

### Marcar Falta

```bash
POST /api/v1/operacional/shifts/{shift_id}/mark-missed?reason=Doença
```

### Bulk Update

```bash
PATCH /api/v1/operacional/shifts/bulk
{
  "items": [
    {
      "shift_id": "uuid1",
      "employee_id": "uuid2",
      "status": "CONFIRMED"
    }
  ]
}
```

---

## 🔄 Substituições

Base path: `/substitutions`

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/substitutions` | Criar substituição | `SUBSTITUTIONS_CREATE` |
| GET | `/substitutions` | Listar substituições | `SUBSTITUTIONS_CREATE` / `SUBSTITUTIONS_APPROVE` |
| GET | `/substitutions/pending` | Substituições pendentes | `SUBSTITUTIONS_APPROVE` |
| POST | `/substitutions/suggest` | Sugerir substitutos (IA) | `SUBSTITUTIONS_CREATE` |
| GET | `/substitutions/by-date/{date}` | Substituições por data | `SUBSTITUTIONS_CREATE` / `SUBSTITUTIONS_APPROVE` |
| GET | `/substitutions/{substitution_id}` | Buscar substituição | `SUBSTITUTIONS_CREATE` / `SUBSTITUTIONS_APPROVE` |
| PATCH | `/substitutions/{substitution_id}` | Atualizar substituição | `SUBSTITUTIONS_CREATE` |
| POST | `/substitutions/{substitution_id}/confirm` | Confirmar substituição | `SUBSTITUTIONS_APPROVE` |
| POST | `/substitutions/{substitution_id}/reject` | Rejeitar substituição | `SUBSTITUTIONS_APPROVE` |
| POST | `/substitutions/{substitution_id}/complete` | Concluir substituição | `SUBSTITUTIONS_APPROVE` |
| DELETE | `/substitutions/{substitution_id}` | Remover substituição | `SUBSTITUTIONS_CREATE` |

### Query Parameters - Listar Substituições

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página atual |
| `page_size` | int | Itens por página |
| `shift_id` | string | Filtrar por turno |
| `post_id` | string | Filtrar por posto |
| `original_employee_id` | string | Funcionário original |
| `substitute_employee_id` | string | Funcionário substituto |
| `status` | enum | Status: `PENDING`, `CONFIRMED`, `REJECTED`, `COMPLETED`, `CANCELLED` |
| `reason` | enum | Motivo: `SICK_LEAVE`, `VACATION`, `ABSENCE`, `SUSPENSION`, `OTHER` |
| `start_date` | date | Data inicial |
| `end_date` | date | Data final |
| `is_pending` | bool | Pendentes |
| `has_substitute` | bool | Com substituto definido |

### Criar Substituição

```bash
POST /api/v1/operacional/substitutions
{
  "shift_id": "uuid",
  "original_employee_id": "uuid",
  "substitution_date": "2026-02-10",
  "reason": "SICK_LEAVE",
  "notes": "Funcionário com atestado médico"
}
```

### Sugerir Substitutos (IA)

```bash
POST /api/v1/operacional/substitutions/suggest
{
  "shift_id": "uuid",
  "preferred_skills": ["armado"],
  "max_distance_km": 50
}
```

### Confirmar Substituição

```bash
POST /api/v1/operacional/substitutions/{substitution_id}/confirm
{
  "substitute_employee_id": "uuid",
  "notes": "Substituto confirmado"
}
```

---

## ⚠️ Ocorrências

Base path: `/occurrences`

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/occurrences` | Criar ocorrência | `OCCURRENCES_CREATE` |
| GET | `/occurrences` | Listar ocorrências | `OCCURRENCES_VIEW` |
| GET | `/occurrences/stats` | Estatísticas | `OCCURRENCES_VIEW` |
| GET | `/occurrences/by-post/{post_id}` | Ocorrências por posto | `OCCURRENCES_VIEW` |
| GET | `/occurrences/{occurrence_id}` | Buscar ocorrência | `OCCURRENCES_VIEW` |
| PATCH | `/occurrences/{occurrence_id}` | Atualizar ocorrência | `OCCURRENCES_EDIT` |
| POST | `/occurrences/{occurrence_id}/resolve` | Resolver ocorrência | `OCCURRENCES_RESOLVE` |
| POST | `/occurrences/{occurrence_id}/attachments` | Adicionar anexo | `OCCURRENCES_EDIT` |
| DELETE | `/occurrences/{occurrence_id}` | Remover ocorrência | `OCCURRENCES_DELETE` |

### Query Parameters - Listar Ocorrências

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página atual |
| `page_size` | int | Itens por página |
| `occurrence_type` | enum | Tipo: `DISCIPLINARY`, `OPERATIONAL`, `SAFETY`, `CLIENT`, `OTHER` |
| `severity` | enum | Severidade: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `category` | enum | Categoria: `ATTENDANCE`, `UNIFORM`, `CONDUCT`, `PERFORMANCE`, `SAFETY_VIOLATION` |
| `status` | enum | Status: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `CANCELLED` |
| `employee_id` | string | Funcionário envolvido |
| `inspector_id` | string | Fiscal que registrou |
| `post_id` | string | Posto |
| `patrol_round_id` | string | Ronda relacionada |
| `date_from` | string | Data inicial (ISO) |
| `date_to` | string | Data final (ISO) |
| `search` | string | Busca textual |

### Criar Ocorrência

```bash
POST /api/v1/operacional/occurrences
{
  "title": "Uniforme incompleto",
  "description": "Funcionário apresentou-se sem cinto",
  "occurrence_type": "DISCIPLINARY",
  "severity": "MEDIUM",
  "category": "UNIFORM",
  "employee_id": "uuid",
  "post_id": "uuid"
}
```

### Resolver Ocorrência

```bash
POST /api/v1/operacional/occurrences/{occurrence_id}/resolve
{
  "resolution_notes": "Funcionário orientado",
  "action_taken": "Advertência verbal",
  "follow_up_required": false
}
```

### Adicionar Anexo

```bash
POST /api/v1/operacional/occurrences/{occurrence_id}/attachments
{
  "type": "image",
  "url": "https://storage...",
  "name": "foto.jpg",
  "size": 2048
}
```

---

## 👷 Diaristas

Base path: `/diaristas`

### Gestão de Diaristas

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/diaristas/consulta-cpf/{cpf}` | Consultar CPF | Autenticado |
| POST | `/diaristas` | Criar diarista | `admin`, `sindico` |
| GET | `/diaristas` | Listar diaristas | Autenticado |
| GET | `/diaristas/available` | Diaristas disponíveis | Autenticado |
| GET | `/diaristas/{diarist_id}` | Buscar diarista | Autenticado |
| PUT | `/diaristas/{diarist_id}` | Atualizar diarista | `admin`, `sindico` |
| POST | `/diaristas/{diarist_id}/activate` | Ativar diarista | `admin`, `sindico` |
| POST | `/diaristas/{diarist_id}/deactivate` | Desativar diarista | `admin`, `sindico` |
| DELETE | `/diaristas/{diarist_id}` | Remover diarista | `admin` |
| GET | `/diaristas/{diarist_id}/metrics` | Métricas da diarista | Autenticado |

### Alocações (Assignments)

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/diaristas/assignments` | Criar alocação | `admin`, `sindico` |
| GET | `/diaristas/assignments` | Listar alocações | Autenticado |
| GET | `/diaristas/assignments/{id}` | Buscar alocação | Autenticado |
| POST | `/diaristas/assignments/{id}/cancel` | Cancelar alocação | `admin`, `sindico` |

### Agendamentos (Schedules)

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/diaristas/schedules/batch` | Criar escala em lote | `admin`, `sindico` |
| POST | `/diaristas/schedules` | Criar agendamento | `admin`, `sindico`, `porteiro` |
| GET | `/diaristas/schedules` | Listar agendamentos | Autenticado |
| GET | `/diaristas/schedules/today` | Agendamentos de hoje | Autenticado |
| GET | `/diaristas/schedules/{id}` | Buscar agendamento | Autenticado |
| POST | `/diaristas/schedules/{id}/confirm` | Confirmar | `admin`, `sindico`, `porteiro` |
| POST | `/diaristas/schedules/{id}/cancel` | Cancelar | `admin`, `sindico` |
| POST | `/diaristas/schedules/checkin` | Registrar check-in | `admin`, `sindico`, `porteiro` |
| POST | `/diaristas/schedules/checkout` | Registrar check-out | `admin`, `sindico`, `porteiro` |

### Pagamentos

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/diaristas/payments/payroll-report` | Relatório de folha | `admin`, `sindico` |
| POST | `/diaristas/payments/payroll-generate` | Gerar pagamentos em lote | `admin`, `sindico` |
| POST | `/diaristas/payments` | Criar pagamento | `admin`, `sindico` |
| GET | `/diaristas/payments` | Listar pagamentos | Autenticado |
| GET | `/diaristas/payments/pending` | Pagamentos pendentes | Autenticado |
| GET | `/diaristas/payments/{id}` | Buscar pagamento | Autenticado |
| POST | `/diaristas/payments/{id}/process` | Processar pagamento | `admin`, `sindico` |
| POST | `/diaristas/payments/generate` | Gerar de agendamentos | `admin`, `sindico` |

### Avaliações

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/diaristas/evaluations` | Criar avaliação | Autenticado |
| GET | `/diaristas/evaluations` | Listar avaliações | Autenticado |
| GET | `/diaristas/evaluations/{id}` | Buscar avaliação | Autenticado |

### Inteligência Artificial

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/diaristas/ai/suggest` | Sugerir diaristas (IA) | Autenticado |
| GET | `/diaristas/ai/availability` | Analisar disponibilidade | Autenticado |
| GET | `/diaristas/ai/performance/{id}` | Analisar performance | Autenticado |
| GET | `/diaristas/ai/optimize` | Otimizar agendamentos | Autenticado |

### Estatísticas

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/diaristas/statistics/general` | Estatísticas gerais | Autenticado |
| GET | `/diaristas/statistics/ranking` | Ranking de diaristas | Autenticado |

### Query Parameters

**Listar Diaristas:**
- `skip`, `limit`: Paginação
- `status`: `ACTIVE`, `INACTIVE`, `SUSPENDED`, `BLACKLISTED`
- `tipo`: `DIARIA`, `PLANTAO`, `EVENTO`, `EMERGENCIA`
- `search`: Busca textual

**Diaristas Disponíveis:**
- `data`: Data desejada
- `tipo`: Tipo de diarista

### Exemplos

```bash
# Consultar CPF
GET /api/v1/operacional/diaristas/consulta-cpf/12345678900

# Criar diarista
POST /api/v1/operacional/diaristas
{
  "nome": "Maria Silva",
  "cpf": "12345678900",
  "telefone": "11999999999",
  "tipo": "DIARIA",
  "valor_diaria": 150.00
}

# Check-in de diarista
POST /api/v1/operacional/diaristas/schedules/checkin
{
  "schedule_id": "uuid",
  "checkin_time": "2026-02-05T08:00:00",
  "location": "Portaria Principal",
  "observations": "Diarista chegou no horário"
}

# Check-out de diarista
POST /api/v1/operacional/diaristas/schedules/checkout
{
  "schedule_id": "uuid",
  "checkout_time": "2026-02-05T17:00:00",
  "observations": "Serviço concluído"
}

# Sugerir diaristas com IA
GET /api/v1/operacional/diaristas/ai/suggest?data=2026-02-10&tipo=DIARIA&duracao_horas=8

# Relatório de folha
GET /api/v1/operacional/diaristas/payments/payroll-report?competencia=2026-02
```

---

## ✅ Check-in/Check-out

O módulo operacional possui dois sistemas de check-in/check-out:

### 1. Turnos de Funcionários (Escala 12x36, 24x72, etc.)

**Endpoints:** `/shifts/{shift_id}/check-in` e `/shifts/{shift_id}/check-out`

```bash
# Check-in
POST /api/v1/operacional/shifts/{shift_id}/check-in
{
  "actual_start_time": "2026-02-05T07:55:00",
  "notes": "Entrada antecipada"
}

# Check-out
POST /api/v1/operacional/shifts/{shift_id}/check-out
{
  "actual_end_time": "2026-02-05T19:05:00",
  "actual_break_minutes": 60,
  "notes": "Saída com 5 min extras"
}
```

**Campos:**
- `actual_start_time`: Data/hora real de entrada
- `actual_end_time`: Data/hora real de saída
- `actual_break_minutes`: Minutos de intervalo realizados
- `notes`: Observações

### 2. Diaristas (Serviços avulsos)

**Endpoints:** `/diaristas/schedules/checkin` e `/diaristas/schedules/checkout`

```bash
# Check-in
POST /api/v1/operacional/diaristas/schedules/checkin
{
  "schedule_id": "uuid",
  "checkin_time": "2026-02-05T08:00:00",
  "location": "Torre A",
  "observations": "Início do serviço"
}

# Check-out
POST /api/v1/operacional/diaristas/schedules/checkout
{
  "schedule_id": "uuid",
  "checkout_time": "2026-02-05T17:00:00",
  "observations": "Serviço finalizado"
}
```

---

## 🔐 Autenticação

Todos os endpoints requerem autenticação via Bearer Token:

```bash
Authorization: Bearer <access_token>
```

## 📊 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 204 | No Content - Sucesso sem conteúdo |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 409 | Conflict - Conflito de dados |
| 422 | Unprocessable Entity - Validação falhou |
| 429 | Too Many Requests - Rate limit |
| 500 | Internal Server Error - Erro interno |

## 📝 Notas

- Todos os endpoints implementam **soft delete** (os dados são marcados como inativos, não removidos fisicamente)
- As listas suportam **paginação** padrão com `page` e `page_size`
- Filtros de data aceitam formato **ISO 8601** (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
- Alguns endpoints utilizam **cache** (TTL indicado na documentação específica)
- Rate limiting aplicado em endpoints críticos (geração de escalas, operações em lote)

---

**Documentação gerada em:** 2026-02-05
**Versão:** 1.0.0
