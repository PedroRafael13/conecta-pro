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
    CertificateInfo as CertInfo,  # noqa: F401
)
from .certificate_manager import (
    CertificateManager,  # noqa: F401
    CertificateStatus,  # noqa: F401
    CertificateStore,  # noqa: F401
    CertificateType,  # noqa: F401
)

# CT-e
from .cte import (
    Carga,
    ComponenteValor,
    CTe,
    CTeManager,
    ModalTransporte,
    NFReferenciada,
    SituacaoCTe,
    TipoServico,
    TomadorServico,
)
from .cte import (
    Participante as ParticipanteCTe,
)

# DCTFWeb
from .dctfweb import (
    DARF,
    CreditoVinculavel,
    DCTFWebDeclaracao,
    DCTFWebManager,
    DebitoContribuicao,
    SituacaoDeclaracao,
    TipoCredito,
    TipoDeclaracao,
)
from .ecac import (
    Certidao as CertidaoEcac,
)
from .ecac import (
    DebitoFiscal as DebitoFiscalEcac,
)

# e-CAC
from .ecac import (
    DeclaracaoConsultada,
    EcacManager,
    PendenciaFiscal,
    ResultadoSituacaoFiscal,
    SituacaoFiscal,
    TipoDeclaracaoConsulta,
    TipoPendencia,
)
from .ecac import (
    TipoCertidao as TipoCertidaoEcac,
)

# EFD-Reinf
from .efd_reinf import (
    ClassificacaoTributaria,
    EFDReinfManager,
    InfoContribuinte,
    PagamentoBeneficiarioPF,
    PagamentoBeneficiarioPJ,
    RetencaoServico,
    TipoInscricao,
)
from .efd_reinf import (
    TipoAmbiente as TipoAmbienteReinf,
)

# eSocial
from .esocial_transmitter import (
    CertificateInfo,
    Environment,
    ESocialError,
    ESocialEvent,
    ESocialTransmitter,
    EventType,
    TransmissionStatus,
    XMLBuilder,
)

# FGTS Digital
from .fgts_digital import (
    GRFGTS,
    DebitoFGTS,
    FGTSDigitalManager,
    GuiaRescisoria,
    RecolhimentoRescisorio,
    SituacaoGuia,
    TrabalhadorFGTS,
)
from .fgts_digital import (
    ModalidadeSaque as ModalidadeSaqueFGTS,
)
from .fgts_digital import (
    TipoRecolhimento as TipoRecolhimentoFGTS,
)

# FGTS/INSS
from .fgts_inss_manager import (
    # Calculadoras
    CalculadoraFGTS,
    CalculadoraINSS,
    CalculoError,
    CalculoFGTS,
    CalculoINSS,
    CategoriaContribuinte,
    Certidao,
    CertidaoModel,
    CodigoRecolhimento,
    ConsultaError,
    ContribuicaoINSSModel,
    ExtratoFGTS,
    # Exceptions
    FGTSINSSError,
    # Manager principal
    FGTSINSSManager,
    GeradorGPS,
    # Geradores
    GeradorGRF,
    GeradorGRRF,
    Guia,
    GuiaError,
    # Models
    GuiaRecolhimentoModel,
    ModalidadeSaque,
    RecolhimentoFGTSModel,
    Remuneracao,
    StatusCertidao,
    StatusGuia,
    TabelaINSS,
    TipoCertidao,
    TipoGuia,
    # Enums
    TipoRecolhimento,
    # Data classes
    Trabalhador,
    TransmissaoError,
    calcular_aliquota_efetiva_inss,
    formatar_pis_pasep,
    get_fgts_inss_manager,
    init_fgts_inss_manager,
    # Utilitarios
    validar_pis_pasep,
)

# Gov.br
from .govbr import (
    GovBrManager,
    NivelAutenticacao,
    TipoDocumento,
    TokenGovBr,
    UsuarioGovBr,
)

# MDF-e
from .mdfe import (
    Condutor,
    DocumentoVinculado,
    MDFe,
    MDFeManager,
    ModalTransporteMDFe,
    Municipio,
    Percurso,
    Reboque,
    SituacaoMDFe,
    TipoCarroceria,
    TipoEmitente,
    TipoRodado,
    Veiculo,
)

# NFS-e Manaus
from .nfse_manaus import (
    NaturezaOperacao,
    NFSeManaus,
    NFSeManausManager,
    NFSeStatus,
    Servico,
    TipoTributacao,
    Tomador,
)

# NFS-e Padrão Nacional (Preparação para migração 2026)
from .nfse_nacional import (
    MAPEAMENTO_SERVICOS_VIGILANCIA,
    AmbienteNacional,
    DPSNacional,
    NFSeNacionalManager,
    PrestadorNacional,
    RegimeEspecial,
    ServicoNacional,
    TomadorNacional,
)

# SEFAZ-AM (Amazonas)
from .sefaz_am import (
    ENDPOINTS_SEFAZ_AM,
    AmbienteSEFAZ,
    InformacaoCadastral,
    ResultadoAutorizacao,
    ResultadoConsulta,
    ResultadoEvento,
    SefazAMClient,
    SefazAMService,
    StatusServico,
    TipoEvento,
)

# SEFAZ (NF-e/NFC-e)
from .sefaz_manager import (
    ContingencyType,
    Destinatario,
    DocumentStatus,
    DocumentType,
    Emitente,
    Endereco,
    NFEXMLBuilder,
    NotaFiscal,
    OperationType,
    Pagamento,
    PaymentType,
    Produto,
    SEFAZError,
    SEFAZManager,
    UFConfig,
)

# Simples Nacional
from .simples_nacional import (
    DAS,
    DEFIS,
    PGDASD,
    AnexoSimples,
    FaixaAliquota,
    ReceitaCompetencia,
    SimplesNacionalManager,
    SituacaoOpcao,
    TipoReceita,
)

# SPED Contábil
from .sped_contabil import (
    ContaContabil,
    DemonstrativoBalancoPatrimonial,
    DemonstrativoDRE,
    LancamentoContabil,
    NaturezaConta,
    SaldoPeriodico,
    SPEDContabilManager,
    TipoConta,
    TipoECD,
)

# SPED Fiscal
from .sped_fiscal import (
    ApuracaoICMS,
    DocumentoFiscal,
    FinalidadeArquivo,
    Inventario,
    PerfilArquivo,
    SPEDFiscalManager,
)
from .sped_fiscal import (
    Participante as ParticipanteFiscal,
)
from .sped_fiscal import (
    Produto as ProdutoFiscal,
)

# Assinatura XML
from .xml_signer import (
    CanonicalizationMethod,  # noqa: F401
    CTEXMLSigner,  # noqa: F401
    DigestMethod,  # noqa: F401
    ESocialXMLSigner,  # noqa: F401
    MDFEXMLSigner,  # noqa: F401
    NFEXMLSigner,  # noqa: F401
    SignatureConfig,  # noqa: F401
    SignatureMethod,  # noqa: F401
    SignatureType,  # noqa: F401
    TransformMethod,  # noqa: F401
    XMLSigner,  # noqa: F401
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
    # NFS-e Padrão Nacional (Preparação 2026)
    "NFSeNacionalManager",
    "DPSNacional",
    "PrestadorNacional",
    "TomadorNacional",
    "ServicoNacional",
    "AmbienteNacional",
    "RegimeEspecial",
    "MAPEAMENTO_SERVICOS_VIGILANCIA",
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
    # SEFAZ-AM (Amazonas)
    "SefazAMClient",
    "SefazAMService",
    "AmbienteSEFAZ",
    "TipoEvento",
    "StatusServico",
    "ResultadoConsulta",
    "ResultadoAutorizacao",
    "ResultadoEvento",
    "InformacaoCadastral",
    "ENDPOINTS_SEFAZ_AM",
]

__version__ = "1.2.0"
