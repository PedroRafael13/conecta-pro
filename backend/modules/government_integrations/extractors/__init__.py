"""
Extratores de Dados Governamentais.

Módulo responsável por extrair dados de:
- SEFAZ (NF-e, CT-e, MDF-e)
- SEFAZ-AM (Amazonas)
- eSocial
- FGTS Digital
- NFS-e (Nacional e Municipal)
- Receita Federal (DCTFWeb, EFD-Reinf, e-CAC, Simples Nacional)
- SPED (Fiscal e Contábil)
- Gov.br
"""

from .orchestrator import (
    OrquestradorExtracao,
    ResultadoExtracao,
    ConfiguracaoExtracao,
    TipoServico,
    StatusExtracao,
    get_orchestrator,
)

# SEFAZ
from .sefaz import ExtratorNFe, ExtratorCTe, ExtratorMDFe

# SEFAZ-AM
from .sefaz_am import ExtratorSEFAZAM

# eSocial e FGTS
from .esocial import ExtratoreSocial
from .fgts import ExtratorFGTS

# NFS-e
from .nfse import ExtratorNFSeManaus, ExtratorNFSeNacional

# Receita Federal
from .receita_federal import (
    ExtratorRFB,
    ExtratorDCTFWeb,
    ExtratorEFDReinf,
    ExtratorECAC,
    ExtratorSimplesNacional,
)

# SPED
from .sped import ExtratorSPEDFiscal, ExtratorSPEDContabil

# Gov.br
from .govbr import ExtratorGovBR

__all__ = [
    # Orchestrator
    "OrquestradorExtracao",
    "ResultadoExtracao",
    "ConfiguracaoExtracao",
    "TipoServico",
    "StatusExtracao",
    "get_orchestrator",

    # SEFAZ
    "ExtratorNFe",
    "ExtratorCTe",
    "ExtratorMDFe",

    # SEFAZ-AM
    "ExtratorSEFAZAM",

    # eSocial e FGTS
    "ExtratoreSocial",
    "ExtratorFGTS",

    # NFS-e
    "ExtratorNFSeManaus",
    "ExtratorNFSeNacional",

    # Receita Federal
    "ExtratorRFB",
    "ExtratorDCTFWeb",
    "ExtratorEFDReinf",
    "ExtratorECAC",
    "ExtratorSimplesNacional",

    # SPED
    "ExtratorSPEDFiscal",
    "ExtratorSPEDContabil",

    # Gov.br
    "ExtratorGovBR",
]
