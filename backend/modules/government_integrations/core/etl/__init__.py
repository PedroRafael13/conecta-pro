"""
Sistema ETL para Integrações Governamentais.

Implementa:
- Normalização de dados
- De-duplicação
- Versionamento de documentos
- Validação XSD
- Mapeamento de campos
"""

from .deduplicator import (
    DeduplicadorDocumentos,
    RegraDedup,
)
from .document_versioning import (
    GerenciadorVersoes,
    VersaoDocumento,
)
from .field_mapper import (
    MAPEAMENTO_CTE,
    MAPEAMENTO_ESOCIAL,
    MAPEAMENTO_FGTS,
    MAPEAMENTO_NFE,
    MAPEAMENTO_NFSE,
    MapeadorCampos,
)
from .normalizer import (
    NormalizadorDados,
    normalizar_cnpj,
    normalizar_cpf,
    normalizar_data,
    normalizar_ie,
    normalizar_valor,
)
from .xsd_validator import (
    ResultadoValidacao,
    ValidadorXSD,
)

__all__ = [
    # Normalizer
    "NormalizadorDados",
    "normalizar_cnpj",
    "normalizar_cpf",
    "normalizar_data",
    "normalizar_valor",
    "normalizar_ie",
    # Field Mapper
    "MapeadorCampos",
    "MAPEAMENTO_NFE",
    "MAPEAMENTO_CTE",
    "MAPEAMENTO_NFSE",
    "MAPEAMENTO_ESOCIAL",
    "MAPEAMENTO_FGTS",
    # Deduplicator
    "DeduplicadorDocumentos",
    "RegraDedup",
    # XSD Validator
    "ValidadorXSD",
    "ResultadoValidacao",
    # Versioning
    "GerenciadorVersoes",
    "VersaoDocumento",
]
