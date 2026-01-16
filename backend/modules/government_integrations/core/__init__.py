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

# NFS-e Manaus
from .nfse_manaus import (
    NFSeManausManager,
    NFSeManaus,
    Tomador,
    Servico,
    NFSeStatus,
    TipoTributacao,
    NaturezaOperacao,
)

# EFD-Reinf
from .efd_reinf import (
    EFDReinfManager,
    InfoContribuinte,
    RetencaoServico,
    PagamentoBeneficiarioPF,
    PagamentoBeneficiarioPJ,
    TipoAmbiente as TipoAmbienteReinf,
    TipoInscricao,
    ClassificacaoTributaria,
)

# DCTFWeb
from .dctfweb import (
    DCTFWebManager,
    DCTFWebDeclaracao,
    DebitoContribuicao,
    CreditoVinculavel,
    DARF,
    TipoDeclaracao,
    SituacaoDeclaracao,
    TipoCredito,
)

# FGTS Digital
from .fgts_digital import (
    FGTSDigitalManager,
    TrabalhadorFGTS,
    DebitoFGTS,
    GRFGTS,
    GuiaRescisoria,
    RecolhimentoRescisorio,
    TipoRecolhimento as TipoRecolhimentoFGTS,
    ModalidadeSaque as ModalidadeSaqueFGTS,
    SituacaoGuia,
)

# Simples Nacional
from .simples_nacional import (
    SimplesNacionalManager,
    PGDASD,
    DAS,
    DEFIS,
    ReceitaCompetencia,
    FaixaAliquota,
    AnexoSimples,
    SituacaoOpcao,
    TipoReceita,
)

# SPED Fiscal
from .sped_fiscal import (
    SPEDFiscalManager,
    Participante as ParticipanteFiscal,
    Produto as ProdutoFiscal,
    DocumentoFiscal,
    ApuracaoICMS,
    Inventario,
    FinalidadeArquivo,
    PerfilArquivo,
)

# SPED Contábil
from .sped_contabil import (
    SPEDContabilManager,
    ContaContabil,
    LancamentoContabil,
    SaldoPeriodico,
    DemonstrativoBalancoPatrimonial,
    DemonstrativoDRE,
    TipoECD,
    NaturezaConta,
    TipoConta,
)

# CT-e
from .cte import (
    CTeManager,
    CTe,
    Participante as ParticipanteCTe,
    NFReferenciada,
    Carga,
    ComponenteValor,
    ModalTransporte,
    TipoServico,
    TomadorServico,
    SituacaoCTe,
)

# MDF-e
from .mdfe import (
    MDFeManager,
    MDFe,
    Condutor,
    Veiculo,
    Reboque,
    DocumentoVinculado,
    Municipio,
    Percurso,
    ModalTransporteMDFe,
    TipoEmitente,
    TipoCarroceria,
    TipoRodado,
    SituacaoMDFe,
)

# Gov.br
from .govbr import (
    GovBrManager,
    UsuarioGovBr,
    TokenGovBr,
    NivelAutenticacao,
    TipoDocumento,
)

# e-CAC
from .ecac import (
    EcacManager,
    ResultadoSituacaoFiscal,
    PendenciaFiscal,
    DebitoFiscal as DebitoFiscalEcac,
    Certidao as CertidaoEcac,
    DeclaracaoConsultada,
    TipoCertidao as TipoCertidaoEcac,
    SituacaoFiscal,
    TipoPendencia,
    TipoDeclaracaoConsulta,
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

    # ===== NOVAS INTEGRAÇÕES (Sprint 33) =====

    # NFS-e Manaus
    "NFSeManausManager",
    "NFSeManaus",
    "Tomador",
    "Servico",
    "NFSeStatus",
    "TipoTributacao",
    "NaturezaOperacao",

    # EFD-Reinf
    "EFDReinfManager",
    "InfoContribuinte",
    "RetencaoServico",
    "PagamentoBeneficiarioPF",
    "PagamentoBeneficiarioPJ",
    "TipoAmbienteReinf",
    "TipoInscricao",
    "ClassificacaoTributaria",

    # DCTFWeb
    "DCTFWebManager",
    "DCTFWebDeclaracao",
    "DebitoContribuicao",
    "CreditoVinculavel",
    "DARF",
    "TipoDeclaracao",
    "SituacaoDeclaracao",
    "TipoCredito",

    # FGTS Digital
    "FGTSDigitalManager",
    "TrabalhadorFGTS",
    "DebitoFGTS",
    "GRFGTS",
    "GuiaRescisoria",
    "RecolhimentoRescisorio",
    "TipoRecolhimentoFGTS",
    "ModalidadeSaqueFGTS",
    "SituacaoGuia",

    # Simples Nacional
    "SimplesNacionalManager",
    "PGDASD",
    "DAS",
    "DEFIS",
    "ReceitaCompetencia",
    "FaixaAliquota",
    "AnexoSimples",
    "SituacaoOpcao",
    "TipoReceita",

    # SPED Fiscal
    "SPEDFiscalManager",
    "ParticipanteFiscal",
    "ProdutoFiscal",
    "DocumentoFiscal",
    "ApuracaoICMS",
    "Inventario",
    "FinalidadeArquivo",
    "PerfilArquivo",

    # SPED Contábil
    "SPEDContabilManager",
    "ContaContabil",
    "LancamentoContabil",
    "SaldoPeriodico",
    "DemonstrativoBalancoPatrimonial",
    "DemonstrativoDRE",
    "TipoECD",
    "NaturezaConta",
    "TipoConta",

    # CT-e
    "CTeManager",
    "CTe",
    "ParticipanteCTe",
    "NFReferenciada",
    "Carga",
    "ComponenteValor",
    "ModalTransporte",
    "TipoServico",
    "TomadorServico",
    "SituacaoCTe",

    # MDF-e
    "MDFeManager",
    "MDFe",
    "Condutor",
    "Veiculo",
    "Reboque",
    "DocumentoVinculado",
    "Municipio",
    "Percurso",
    "ModalTransporteMDFe",
    "TipoEmitente",
    "TipoCarroceria",
    "TipoRodado",
    "SituacaoMDFe",

    # Gov.br
    "GovBrManager",
    "UsuarioGovBr",
    "TokenGovBr",
    "NivelAutenticacao",
    "TipoDocumento",

    # e-CAC
    "EcacManager",
    "ResultadoSituacaoFiscal",
    "PendenciaFiscal",
    "DebitoFiscalEcac",
    "CertidaoEcac",
    "DeclaracaoConsultada",
    "TipoCertidaoEcac",
    "SituacaoFiscal",
    "TipoPendencia",
    "TipoDeclaracaoConsulta",
]

__version__ = "1.1.0"
