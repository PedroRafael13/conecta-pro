# Sistema de Geração Automática de Escalas

## Visão Geral

Sistema desenvolvido para gerar automaticamente escalas e turnos de trabalho baseado nas alocações ativas de funcionários em postos.

## Problema Resolvido

O sistema tinha **ZERO turnos** cadastrados apesar de ter 44 alocações ativas em 9 postos, impedindo a operação 24/7 do módulo operacional.

## Solução Implementada

### 1. Serviço de Geração Automática (`auto_scale_service.py`)

Serviço que:
- Detecta alocações ativas sem escala
- Agrupa funcionários por posto
- Gera escalas automaticamente (padrão 12x36)
- Cria turnos diários (diurnos 7h-19h e noturnos 19h-7h)

### 2. Correção do Gerador de Escalas (`scale_generator.py`)

Corrigido campos do schema:
- `start_time` → `planned_start_time`
- `end_time` → `planned_end_time`
- Removido campo `is_sunday` (não existe no schema)

### 3. API Endpoint

Endpoint: `POST /api/v1/operacional/scales/auto-generate`

Query Parameters:
- `month` (opcional): Mês para gerar (1-12)
- `year` (opcional): Ano para gerar

Se não especificado, gera para o mês atual.

### 4. Script Manual

Script: `/opt/conecta-pro/backend/scripts/generate_current_month_scales.py`

Uso:
```bash
# Mês atual
python scripts/generate_current_month_scales.py

# Mês específico
python scripts/generate_current_month_scales.py --month 2 --year 2026
```

### 5. Celery Task

Task agendável: `operacional.auto_generate_monthly_scales`

Pode ser executada:
- Manualmente via Celery CLI
- Agendada no Celery Beat para rodar todo dia 1º do mês
- Chamada via API

## Resultado

**Janeiro/2026 Gerado:**
- ✅ 9 escalas criadas (uma por posto)
- ✅ 558 turnos gerados (01/01 a 31/01)
- ✅ 18 turnos por dia (9 postos × 2 turnos = diurno + noturno)
- ✅ Sistema 100% operacional para gestão 24/7

## Estrutura de Turnos 12x36

Cada posto recebe:
- **Turno Diurno**: 07:00 - 19:00 (12h)
- **Turno Noturno**: 19:00 - 07:00 (12h)
- Funcionários alternam a cada 2 dias (trabalha 1, descansa 1.5)

## Tipos de Escala Suportados

- `12x36`: 12h trabalho, 36h descanso (padrão)
- `6x1`: 6 dias trabalho, 1 folga
- `5x2`: 5 dias trabalho, 2 folgas (administrativo)
- `5x1`: 5 dias trabalho, 1 folga
- `4x2`: 4 dias trabalho, 2 folgas
- `turno_revezamento`: Rodízio manhã/tarde/noite
- `administrativo`: Segunda a sexta, 8h-18h

## Como Usar

### Geração Manual (API)

```bash
curl -X POST "http://localhost:8080/api/v1/operacional/scales/auto-generate" \
  -H "Authorization: Bearer {TOKEN}"
```

### Geração Manual (Script)

```bash
cd /opt/conecta-pro/backend
python scripts/generate_current_month_scales.py
```

### Geração Automática (Celery)

```python
from modules.operacional.tasks import auto_generate_monthly_scales_task

# Mês atual
auto_generate_monthly_scales_task.delay()

# Mês específico
auto_generate_monthly_scales_task.delay(month=2, year=2026)
```

## Próximos Passos

1. Adicionar no Celery Beat para rodar automaticamente dia 1º de cada mês
2. Implementar notificação aos funcionários quando escala for gerada
3. Permitir configuração de tipo de escala por posto
4. Interface no frontend para geração sob demanda

## Arquivos Criados/Modificados

**Criados:**
- `/opt/conecta-pro/backend/modules/operacional/services/auto_scale_service.py`
- `/opt/conecta-pro/backend/scripts/generate_current_month_scales.py`
- `/opt/conecta-pro/backend/modules/operacional/services/README_AUTO_SCALES.md`

**Modificados:**
- `/opt/conecta-pro/backend/modules/operacional/services/scale_generator.py`
- `/opt/conecta-pro/backend/modules/operacional/controllers/scale_controller.py`
- `/opt/conecta-pro/backend/modules/operacional/tasks.py`

## Data de Implementação

26/01/2026 - Jordan (via Claude Code)
