"""
Package: fgts_inss
Description: Modulo de integracao com FGTS e INSS
             - Calculo e recolhimento FGTS (Lei 8.036/1990)
             - Contribuicoes previdenciarias INSS (Lei 8.212/1991)
             - Geracao de guias (GRF, GRRF, GPS, DAE)
             - Consultas e certidoes (CRF, CND)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Legislacao trabalhista e previdenciaria brasileira
"""

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
    # Manager principal
    "FGTSINSSManager",
    "get_fgts_inss_manager",
    "init_fgts_inss_manager",
    # Calculadoras
    "CalculadoraFGTS",
    "CalculadoraINSS",
    "TabelaINSS",
    # Data classes
    "Trabalhador",
    "Remuneracao",
    "CalculoFGTS",
    "CalculoINSS",
    "Guia",
    "Certidao",
    "ExtratoFGTS",
    # Enums
    "TipoRecolhimento",
    "CodigoRecolhimento",
    "ModalidadeSaque",
    "CategoriaContribuinte",
    "TipoGuia",
    "StatusGuia",
    "StatusCertidao",
    "TipoCertidao",
    # Exceptions
    "FGTSINSSError",
    "CalculoError",
    "GuiaError",
    "ConsultaError",
    "TransmissaoError",
    # Models
    "GuiaRecolhimentoModel",
    "RecolhimentoFGTSModel",
    "ContribuicaoINSSModel",
    "CertidaoModel",
    # Geradores
    "GeradorGRF",
    "GeradorGRRF",
    "GeradorGPS",
    # Utilitarios
    "validar_pis_pasep",
    "formatar_pis_pasep",
    "calcular_aliquota_efetiva_inss",
]

__version__ = "1.0.0"
