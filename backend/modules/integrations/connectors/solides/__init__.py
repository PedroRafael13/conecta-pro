"""
Conector Sólides RH
Sprint 33: Integration Framework
"""

from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.schemas import (
    SolidesColaborador,
    SolidesColaboradorCreate,
    SolidesDepartamento,
    SolidesCargo,
    SolidesVaga,
    SolidesCandidato,
    SolidesInscricao,
    SolidesAvaliacao,
    SolidesPesquisaClima,
    SolidesEndereco,
    SolidesPaginatedResponse,
    SolidesSingleResponse,
    SolidesErrorResponse,
)
from modules.integrations.connectors.solides.mappers import (
    solides_colaborador_to_employee,
    employee_to_solides_colaborador,
    solides_candidato_to_candidate,
    candidate_to_solides_candidato,
    solides_departamento_to_department,
    solides_cargo_to_position,
    solides_vaga_to_job_position,
    solides_inscricao_to_application,
    compute_solides_entity_hash,
)

__all__ = [
    # Connector
    "SolidesConnector",
    # Schemas
    "SolidesColaborador",
    "SolidesColaboradorCreate",
    "SolidesDepartamento",
    "SolidesCargo",
    "SolidesVaga",
    "SolidesCandidato",
    "SolidesInscricao",
    "SolidesAvaliacao",
    "SolidesPesquisaClima",
    "SolidesEndereco",
    "SolidesPaginatedResponse",
    "SolidesSingleResponse",
    "SolidesErrorResponse",
    # Mappers
    "solides_colaborador_to_employee",
    "employee_to_solides_colaborador",
    "solides_candidato_to_candidate",
    "candidate_to_solides_candidato",
    "solides_departamento_to_department",
    "solides_cargo_to_position",
    "solides_vaga_to_job_position",
    "solides_inscricao_to_application",
    "compute_solides_entity_hash",
]
