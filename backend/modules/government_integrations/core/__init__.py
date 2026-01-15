"""
Core do módulo Government Integrations - Implementações avançadas
=================================================================

Código consolidado de 03_government_integrations/

Compliance:
- eSocial (Decreto 8.373/2014)
- NF-e/NFC-e (SEFAZ)
- FGTS (Lei 8.036/1990)
- INSS (Lei 8.212/1991)

Sprint 33: Suporte a Certificados Digitais A1
"""

# Certificados Digitais
from .certificate_manager import (
    CertificateType,
    CertificateStatus,
    CertificateInfo as CertInfo,
    CertificateManager,
    CertificateStore,
)

# Assinatura XML
from .xml_signer import (
    SignatureType,
    DigestMethod,
    SignatureMethod,
    CanonicalizationMethod,
    TransformMethod,
    SignatureConfig,
    XMLSigner,
    ESocialXMLSigner,
    NFEXMLSigner,
    CTEXMLSigner,
    MDFEXMLSigner,
)

# eSocial
from .esocial_transmitter import (
    EventType,
    TransmissionStatus,
    Environment,
    ESocialError,
    CertificateInfo,
    ESocialEvent,
    XMLBuilder,
    ESocialTransmitter,
)

# SEFAZ (NF-e/NFC-e)
from .sefaz_manager import (
    DocumentType,
    DocumentStatus,
    OperationType,
    PaymentType,
    ContingencyType,
    SEFAZError,
    UFConfig,
    Endereco,
    Emitente,
    Destinatario,
    Produto,
    Pagamento,
    NotaFiscal,
    NFEXMLBuilder,
    SEFAZManager,
)

# FGTS/INSS
from .fgts_inss_manager import (
    # Manager principal
    FGTSINSSManager,
    get_fgts_inss_manager,
    init_fgts_inss_manager,
    # Calculadoras
    CalculadoraFGTS,
    CalculadoraINSS,
    TabelaINSS,
    # Data classes
    Trabalhador,
    Remuneracao,
    CalculoFGTS,
    CalculoINSS,
    Guia,
    Certidao,
    ExtratoFGTS,
    # Enums
    TipoRecolhimento,
    CodigoRecolhimento,
    ModalidadeSaque,
    CategoriaContribuinte,
    TipoGuia,
    StatusGuia,
    StatusCertidao,
    TipoCertidao,
    # Exceptions
    FGTSINSSError,
    CalculoError,
    GuiaError,
    ConsultaError,
    TransmissaoError,
    # Models
    GuiaRecolhimentoModel,
    RecolhimentoFGTSModel,
    ContribuicaoINSSModel,
    CertidaoModel,
    # Geradores
    GeradorGRF,
    GeradorGRRF,
    GeradorGPS,
    # Utilitarios
    validar_pis_pasep,
    formatar_pis_pasep,
    calcular_aliquota_efetiva_inss,
)

__all__ = [
    # eSocial
    "EventType",
    "TransmissionStatus",
    "Environment",
    "ESocialError",
    "CertificateInfo",
    "ESocialEvent",
    "XMLBuilder",
    "ESocialTransmitter",
    # SEFAZ
    "DocumentType",
    "DocumentStatus",
    "OperationType",
    "PaymentType",
    "ContingencyType",
    "SEFAZError",
    "UFConfig",
    "Endereco",
    "Emitente",
    "Destinatario",
    "Produto",
    "Pagamento",
    "NotaFiscal",
    "NFEXMLBuilder",
    "SEFAZManager",
    # FGTS/INSS - Manager
    "FGTSINSSManager",
    "get_fgts_inss_manager",
    "init_fgts_inss_manager",
    # FGTS/INSS - Calculadoras
    "CalculadoraFGTS",
    "CalculadoraINSS",
    "TabelaINSS",
    # FGTS/INSS - Data classes
    "Trabalhador",
    "Remuneracao",
    "CalculoFGTS",
    "CalculoINSS",
    "Guia",
    "Certidao",
    "ExtratoFGTS",
    # FGTS/INSS - Enums
    "TipoRecolhimento",
    "CodigoRecolhimento",
    "ModalidadeSaque",
    "CategoriaContribuinte",
    "TipoGuia",
    "StatusGuia",
    "StatusCertidao",
    "TipoCertidao",
    # FGTS/INSS - Exceptions
    "FGTSINSSError",
    "CalculoError",
    "GuiaError",
    "ConsultaError",
    "TransmissaoError",
    # FGTS/INSS - Models
    "GuiaRecolhimentoModel",
    "RecolhimentoFGTSModel",
    "ContribuicaoINSSModel",
    "CertidaoModel",
    # FGTS/INSS - Geradores
    "GeradorGRF",
    "GeradorGRRF",
    "GeradorGPS",
    # FGTS/INSS - Utilitarios
    "validar_pis_pasep",
    "formatar_pis_pasep",
    "calcular_aliquota_efetiva_inss",
]

__version__ = "1.0.0"
