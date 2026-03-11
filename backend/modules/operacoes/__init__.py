"""
Módulo OPERAÇÕES — Agregador
Unifica: operacional (+ submodulos) + campo

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Operacional Core ---
# --- Campo (Ordens de Serviço, Visitas, Checklists) ---
from modules.campo import (
    checklist_router,
    ordem_servico_router,
    visita_router,
)

# --- Operacional AI ---
from modules.operacional.ai.controller import ai_router as operacional_ai_router

# --- Operacional Communication ---
from modules.operacional.communication import communication_router
from modules.operacional.controllers import (
    allocation_router,
    employee_router,
    kpi_trends_router,
    post_router,
    reports_router,
    scale_router,
    scale_template_router,
    shift_router,
    substitution_router,
    time_bank_router,
)

# --- Operacional Diaristas ---
from modules.operacional.diaristas.controllers import fiscal_router as diarist_fiscal_router
from modules.operacional.diaristas.controllers import router as diarist_router

# --- Operacional Disciplinary ---
from modules.operacional.disciplinary import router as disciplinary_router

# --- Operacional Inspection Rounds ---
from modules.operacional.inspection_rounds import inspection_round_router

# --- Operacional Occurrences ---
from modules.operacional.occurrences import occurrence_router

# --- Operacional Vacations ---
from modules.operacional.vacations import vacation_router

# --- Operacional WebSocket ---
from modules.operacional.websockets import websocket_router as operacional_ws_router

__all__ = [
    "post_router",
    "scale_router",
    "scale_template_router",
    "shift_router",
    "allocation_router",
    "employee_router",
    "substitution_router",
    "time_bank_router",
    "reports_router",
    "kpi_trends_router",
    "occurrence_router",
    "diarist_router",
    "diarist_fiscal_router",
    "disciplinary_router",
    "inspection_round_router",
    "communication_router",
    "vacation_router",
    "operacional_ai_router",
    "operacional_ws_router",
    "ordem_servico_router",
    "visita_router",
    "checklist_router",
]
