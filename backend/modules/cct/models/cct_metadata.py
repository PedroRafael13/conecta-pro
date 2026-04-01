"""
Metadados da CCT 2026 SINDECOMPRESTS/SINDICOND-AM.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class _CCTMetadata:
    """Dados identificadores da Convencao Coletiva."""

    nome: str = "CCT SINDECOMPRESTS/SINDICOND-AM 2026"
    registro_mte: str = "AM000613/2025"
    vigencia_inicio: str = "2026-01-01"
    vigencia_fim: str = "2026-12-31"
    sindicato_laboral: str = "SINDECOMPRESTS"
    sindicato_laboral_cnpj: str = "00.444.514/0001-36"
    sindicato_patronal: str = "SINDICOND-AM"
    sindicato_patronal_cnpj: str = "52.753.671/0001-27"
    municipio: str = "Manaus"
    uf: str = "AM"
    data_base: str = "01/01"


CCT_METADATA = _CCTMetadata()
