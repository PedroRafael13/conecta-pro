"""
Services para integrações governamentais.

Sprint 34: Adicionado FGTS Digital (guias via PIX, rescisões, relatórios)
Sprint 34: Adicionado SPED Fiscal (EFD ICMS/IPI, apuração, arquivo)
Sprint 34: Adicionado SPED Contábil (ECD, lançamentos, demonstrações)
Sprint 35: Adicionado e-CAC (Situação Fiscal, Certidões, Débitos)
Sprint 35: Adicionado CT-e (Conhecimento de Transporte Eletrônico)
Sprint 35: Adicionado MDF-e (Manifesto Eletrônico de Documentos Fiscais)
Sprint 36: Adicionado NFS-e Padrao Nacional (preparacao para migracao)
"""

from .receita_federal_service import ReceitaFederalApiService
from .fgts_inss_service import FGTSINSSService
from .esocial_service import ESocialService
from .sefaz_service import SEFAZService
from .nfse_manaus_service import NFSeManausService, get_nfse_manaus_service
from .efd_reinf_service import EFDReinfService, get_efd_reinf_service
from .dctfweb_service import DCTFWebService, get_dctfweb_service
from .simples_nacional_service import SimplesNacionalService, get_simples_nacional_service
from .fgts_digital_service import FGTSDigitalService, get_fgts_digital_service
from .sped_fiscal_service import SPEDFiscalService, get_sped_fiscal_service
from .sped_contabil_service import SPEDContabilService, get_sped_contabil_service
from .ecac_service import EcacService, get_ecac_service
from .cte_service import CTeService, get_cte_service
from .mdfe_service import MDFeService, get_mdfe_service
from .govbr_service import GovBrService, get_govbr_service
from .nfse_nacional_service import NFSeNacionalService, get_nfse_nacional_service

__all__ = [
    "ReceitaFederalApiService",
    "FGTSINSSService",
    "ESocialService",
    "SEFAZService",
    "NFSeManausService",
    "get_nfse_manaus_service",
    "EFDReinfService",
    "get_efd_reinf_service",
    "DCTFWebService",
    "get_dctfweb_service",
    "SimplesNacionalService",
    "get_simples_nacional_service",
    "FGTSDigitalService",
    "get_fgts_digital_service",
    "SPEDFiscalService",
    "get_sped_fiscal_service",
    "SPEDContabilService",
    "get_sped_contabil_service",
    "EcacService",
    "get_ecac_service",
    "CTeService",
    "get_cte_service",
    "MDFeService",
    "get_mdfe_service",
    "GovBrService",
    "get_govbr_service",
    "NFSeNacionalService",
    "get_nfse_nacional_service",
]
