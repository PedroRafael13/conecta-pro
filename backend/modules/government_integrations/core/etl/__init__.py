"""
Sistema ETL para Integrações Governamentais.

Implementa:
- Normalização de dados
- De-duplicação
- Versionamento de documentos
- Validação XSD
- Mapeamento de campos
"""

from .normalizer import (
    NormalizadorDados,
    normalizar_cnpj,
    normalizar_cpf,
    normalizar_data,
    normalizar_valor,
    normalizar_ie,
)
from .field_mapper import (
    MapeadorCampos,
    MAPEAMENTO_NFE,
    MAPEAMENTO_CTE,
    MAPEAMENTO_NFSE,
    MAPEAMENTO_ESOCIAL,
    MAPEAMENTO_FGTS,
)
from .deduplicator import (
    DeduplicadorDocumentos,
    RegraDedup,
)
from .xsd_validator import (
    ValidadorXSD,
    ResultadoValidacao,
)
from .document_versioning import (
    GerenciadorVersoes,
    VersaoDocumento,
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
