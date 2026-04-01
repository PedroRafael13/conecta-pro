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

# eSocial e FGTS
from .esocial import ExtratoreSocial
from .fgts import ExtratorFGTS

# Gov.br
from .govbr import ExtratorGovBR

# NFS-e
from .nfse import ExtratorNFSeManaus, ExtratorNFSeNacional
from .orchestrator import (
    ConfiguracaoExtracao,
    OrquestradorExtracao,
    ResultadoExtracao,
    StatusExtracao,
    TipoServico,
    get_orchestrator,
)

# Receita Federal
from .receita_federal import (
    ExtratorDCTFWeb,
    ExtratorECAC,
    ExtratorEFDReinf,
    ExtratorRFB,
    ExtratorSimplesNacional,
)

# SEFAZ
from .sefaz import ExtratorCTe, ExtratorMDFe, ExtratorNFe

# SEFAZ-AM
from .sefaz_am import ExtratorSEFAZAM

# SPED
from .sped import ExtratorSPEDContabil, ExtratorSPEDFiscal

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
