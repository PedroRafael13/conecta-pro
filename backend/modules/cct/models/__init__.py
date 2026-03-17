"""
Models do modulo CCT 2026 — SINDECOMPRESTS/SINDICOND-AM.

Re-exporta todos os modelos e constantes da CCT.
"""

from .benefits import (
    BENEFICIOS_OBRIGATORIOS_CCT,
    TAXA_NEGOCIAL_2026,
    BeneficioCCT,
)
from .cct_metadata import CCT_METADATA
from .cct_tables import (
    CCTBenefitConfig,
    CCTComplianceCheck,
    CCTSalaryAudit,
)
from .holidays import (
    FERIADOS_MANAUS_2026,
    FeriadoCCT,
)
from .salary_table import (
    REAJUSTE_ACIMA_PISO,
    REAJUSTE_PISO,
    SALARIO_PISO,
    TABELA_SALARIAL_CCT_2026,
    CargoAdditional,
    SalaryEntry,
)
from .schedule import (
    JORNADAS_PERMITIDAS,
    AdicionaisCCT,
    JornadaCCT,
)

__all__ = [
    "SALARIO_PISO",
    "REAJUSTE_PISO",
    "REAJUSTE_ACIMA_PISO",
    "TABELA_SALARIAL_CCT_2026",
    "CargoAdditional",
    "SalaryEntry",
    "BENEFICIOS_OBRIGATORIOS_CCT",
    "TAXA_NEGOCIAL_2026",
    "BeneficioCCT",
    "JORNADAS_PERMITIDAS",
    "JornadaCCT",
    "AdicionaisCCT",
    "FERIADOS_MANAUS_2026",
    "FeriadoCCT",
    "CCT_METADATA",
    "CCTSalaryAudit",
    "CCTComplianceCheck",
    "CCTBenefitConfig",
]
