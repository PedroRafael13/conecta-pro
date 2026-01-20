"""
Matriz de Contingência por UF.

Define endpoints principais e de contingência para cada UF.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum


class TipoContingencia(Enum):
    """Tipos de contingência SEFAZ."""
    SVC_AN = "svc_an"      # Contingência Ambiente Nacional
    SVC_RS = "svc_rs"      # Contingência Rio Grande do Sul
    EPEC = "epec"          # Evento Prévio de Emissão em Contingência
    FS_DA = "fs_da"        # Formulário de Segurança - Documento Auxiliar


@dataclass
class EndpointConfig:
    """Configuração de endpoint."""
    url: str
    versao: str = "4.00"
    timeout: int = 30
    requer_certificado: bool = True


@dataclass
class ConfigUF:
    """Configuração de endpoints por UF."""
    uf: str
    principal: EndpointConfig
    contingencia: Optional[EndpointConfig] = None
    contingencia_2: Optional[EndpointConfig] = None
    tipo_contingencia: TipoContingencia = TipoContingencia.SVC_AN


# Endpoints Centralizados
ENDPOINTS_CENTRALIZADOS: Dict[str, Dict[str, str]] = {
    # SEFAZ AM - Produção (case-sensitive: Nfe com f minúsculo)
    "AM_PROD": {
        "NfeStatusServico": "https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
        "NfeAutorizacao": "https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
        "NfeRetAutorizacao": "https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4",
        "NfeConsultaProtocolo": "https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta4",
        "NfeInutilizacao": "https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4",
        "RecepcaoEvento": "https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4",
    },
    # SEFAZ AM - Homologação (case-sensitive: Nfe com f minúsculo)
    "AM_HOM": {
        "NfeStatusServico": "https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
        "NfeAutorizacao": "https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
        "NfeRetAutorizacao": "https://homnfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4",
        "NfeConsultaProtocolo": "https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta4",
        "NfeInutilizacao": "https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4",
        "RecepcaoEvento": "https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4",
    },
    # SEFAZ Virtual Rio Grande do Sul
    "SVRS": {
        "NfeStatusServico": "https://nfe.svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx",
        "NfeAutorizacao": "https://nfe.svrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx",
        "NfeRetAutorizacao": "https://nfe.svrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx",
        "NfeConsultaProtocolo": "https://nfe.svrs.rs.gov.br/ws/NfeConsulta/NfeConsulta4.asmx",
        "NfeInutilizacao": "https://nfe.svrs.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao4.asmx",
        "RecepcaoEvento": "https://nfe.svrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx",
        "NfeConsultaCadastro": "https://cad.svrs.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro4.asmx",
    },
    # SEFAZ Virtual Ambiente Nacional
    "SVAN": {
        "NfeStatusServico": "https://www.sefazvirtual.fazenda.gov.br/NFeStatusServico4/NFeStatusServico4.asmx",
        "NfeAutorizacao": "https://www.sefazvirtual.fazenda.gov.br/NFeAutorizacao4/NFeAutorizacao4.asmx",
        "NfeRetAutorizacao": "https://www.sefazvirtual.fazenda.gov.br/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx",
        "NfeConsultaProtocolo": "https://www.sefazvirtual.fazenda.gov.br/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx",
        "NfeInutilizacao": "https://www.sefazvirtual.fazenda.gov.br/NFeInutilizacao4/NFeInutilizacao4.asmx",
        "RecepcaoEvento": "https://www.sefazvirtual.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx",
    },
    # SVC-AN (Contingência Ambiente Nacional)
    "SVC_AN": {
        "NfeStatusServico": "https://www.svc.fazenda.gov.br/NFeStatusServico4/NFeStatusServico4.asmx",
        "NfeAutorizacao": "https://www.svc.fazenda.gov.br/NFeAutorizacao4/NFeAutorizacao4.asmx",
        "NfeRetAutorizacao": "https://www.svc.fazenda.gov.br/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx",
        "NfeConsultaProtocolo": "https://www.svc.fazenda.gov.br/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx",
        "RecepcaoEvento": "https://www.svc.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx",
    },
    # SVC-RS (Contingência Rio Grande do Sul)
    "SVC_RS": {
        "NfeStatusServico": "https://nfe-svc.svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx",
        "NfeAutorizacao": "https://nfe-svc.svrs.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao4.asmx",
        "NfeRetAutorizacao": "https://nfe-svc.svrs.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao4.asmx",
        "NfeConsultaProtocolo": "https://nfe-svc.svrs.rs.gov.br/ws/NfeConsulta/NfeConsulta4.asmx",
        "RecepcaoEvento": "https://nfe-svc.svrs.rs.gov.br/ws/recepcaoevento/recepcaoevento4.asmx",
    },
    # Ambiente Nacional (EPEC e distribuição)
    "AN": {
        "RecepcaoEvento": "https://www.nfe.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx",
        "NFeDistribuicaoDFe": "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
    },
    # CT-e SVRS
    "SVRS_CTE": {
        "CteStatusServico": "https://cte.svrs.rs.gov.br/ws/ctestatus/CteStatusServico.asmx",
        "CteRecepcaoSinc": "https://cte.svrs.rs.gov.br/ws/cterecepcaosinc/CTeRecepcaoSinc.asmx",
        "CteConsulta": "https://cte.svrs.rs.gov.br/ws/cteconsulta/CteConsulta.asmx",
        "CteRecepcaoEvento": "https://cte.svrs.rs.gov.br/ws/cterecepcaoevento/CteRecepcaoEvento.asmx",
    },
    # MDF-e SVRS
    "SVRS_MDFE": {
        "MDFeStatusServico": "https://mdfe.svrs.rs.gov.br/ws/MDFeStatusServico/MDFeStatusServico.asmx",
        "MDFeRecepcaoSinc": "https://mdfe.svrs.rs.gov.br/ws/MDFeRecepcaoSinc/MDFeRecepcaoSinc.asmx",
        "MDFeConsulta": "https://mdfe.svrs.rs.gov.br/ws/MDFeConsulta/MDFeConsulta.asmx",
        "MDFeRecepcaoEvento": "https://mdfe.svrs.rs.gov.br/ws/MDFeRecepcaoEvento/MDFeRecepcaoEvento.asmx",
    },
}


# Matriz de Contingência NF-e por UF
MATRIZ_CONTINGENCIA_NFE: Dict[str, ConfigUF] = {
    # ===== NORTE =====
    "AC": ConfigUF(
        uf="AC",
        principal=EndpointConfig(url="SVRS"),  # Usa SVRS
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "AM": ConfigUF(
        uf="AM",
        principal=EndpointConfig(url="AM_PROD"),  # Usa endpoints centralizados AM
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "AP": ConfigUF(
        uf="AP",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "PA": ConfigUF(
        uf="PA",
        principal=EndpointConfig(url="SVAN"),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "RO": ConfigUF(
        uf="RO",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "RR": ConfigUF(
        uf="RR",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "TO": ConfigUF(
        uf="TO",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),

    # ===== NORDESTE =====
    "AL": ConfigUF(
        uf="AL",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "BA": ConfigUF(
        uf="BA",
        principal=EndpointConfig(
            url="https://nfe.sefaz.ba.gov.br/webservices/NFeAutorizacao4/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "CE": ConfigUF(
        uf="CE",
        principal=EndpointConfig(
            url="https://nfe.sefaz.ce.gov.br/nfe4/services/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "MA": ConfigUF(
        uf="MA",
        principal=EndpointConfig(url="SVAN"),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "PB": ConfigUF(
        uf="PB",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "PE": ConfigUF(
        uf="PE",
        principal=EndpointConfig(
            url="https://nfe.sefaz.pe.gov.br/nfe-service/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "PI": ConfigUF(
        uf="PI",
        principal=EndpointConfig(url="SVAN"),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "RN": ConfigUF(
        uf="RN",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "SE": ConfigUF(
        uf="SE",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),

    # ===== CENTRO-OESTE =====
    "DF": ConfigUF(
        uf="DF",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "GO": ConfigUF(
        uf="GO",
        principal=EndpointConfig(
            url="https://nfe.sefaz.go.gov.br/nfe/services/"
        ),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "MS": ConfigUF(
        uf="MS",
        principal=EndpointConfig(
            url="https://nfe.sefaz.ms.gov.br/ws/"
        ),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "MT": ConfigUF(
        uf="MT",
        principal=EndpointConfig(
            url="https://nfe.sefaz.mt.gov.br/nfews/"
        ),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),

    # ===== SUDESTE =====
    "ES": ConfigUF(
        uf="ES",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "MG": ConfigUF(
        uf="MG",
        principal=EndpointConfig(
            url="https://nfe.fazenda.mg.gov.br/nfe2/services/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "RJ": ConfigUF(
        uf="RJ",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "SP": ConfigUF(
        uf="SP",
        principal=EndpointConfig(
            url="https://nfe.fazenda.sp.gov.br/ws/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),

    # ===== SUL =====
    "PR": ConfigUF(
        uf="PR",
        principal=EndpointConfig(
            url="https://nfe.sefa.pr.gov.br/nfe/NFeAutorizacao4"
        ),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
    "RS": ConfigUF(
        uf="RS",
        principal=EndpointConfig(
            url="https://nfe.sefazrs.rs.gov.br/ws/"
        ),
        contingencia=EndpointConfig(url="SVC_AN"),
        tipo_contingencia=TipoContingencia.SVC_AN,
    ),
    "SC": ConfigUF(
        uf="SC",
        principal=EndpointConfig(url="SVRS"),
        contingencia=EndpointConfig(url="SVC_RS"),
        tipo_contingencia=TipoContingencia.SVC_RS,
    ),
}

# Matriz de Contingência CT-e por UF
MATRIZ_CONTINGENCIA_CTE: Dict[str, ConfigUF] = {
    # Maioria usa SVRS
    "DEFAULT": ConfigUF(
        uf="DEFAULT",
        principal=EndpointConfig(url="SVRS_CTE"),
        contingencia=None,
    ),
    # UFs com SEFAZ própria para CT-e
    "MG": ConfigUF(
        uf="MG",
        principal=EndpointConfig(
            url="https://cte.fazenda.mg.gov.br/cte/services/"
        ),
        contingencia=EndpointConfig(url="SVRS_CTE"),
    ),
    "MS": ConfigUF(
        uf="MS",
        principal=EndpointConfig(
            url="https://producao.cte.ms.gov.br/ws/"
        ),
        contingencia=EndpointConfig(url="SVRS_CTE"),
    ),
    "MT": ConfigUF(
        uf="MT",
        principal=EndpointConfig(
            url="https://cte.sefaz.mt.gov.br/ctews2/"
        ),
        contingencia=EndpointConfig(url="SVRS_CTE"),
    ),
    "PR": ConfigUF(
        uf="PR",
        principal=EndpointConfig(
            url="https://cte.fazenda.pr.gov.br/cte4/"
        ),
        contingencia=EndpointConfig(url="SVRS_CTE"),
    ),
    "SP": ConfigUF(
        uf="SP",
        principal=EndpointConfig(
            url="https://nfe.fazenda.sp.gov.br/CTeWS/"
        ),
        contingencia=EndpointConfig(url="SVRS_CTE"),
    ),
}

# Matriz de Contingência MDF-e por UF
MATRIZ_CONTINGENCIA_MDFE: Dict[str, ConfigUF] = {
    # Maioria usa SVRS
    "DEFAULT": ConfigUF(
        uf="DEFAULT",
        principal=EndpointConfig(url="SVRS_MDFE"),
        contingencia=None,
    ),
    # RS tem SEFAZ própria
    "RS": ConfigUF(
        uf="RS",
        principal=EndpointConfig(
            url="https://mdfe.svrs.rs.gov.br/ws/"
        ),
        contingencia=None,
    ),
}


class MatrizContingencia:
    """Gerencia matriz de contingência para documentos fiscais."""

    @classmethod
    def obter_config_nfe(cls, uf: str) -> ConfigUF:
        """Obtém configuração de NF-e para UF."""
        return MATRIZ_CONTINGENCIA_NFE.get(
            uf.upper(),
            MATRIZ_CONTINGENCIA_NFE.get("AC")  # Fallback para SVRS
        )

    @classmethod
    def obter_config_cte(cls, uf: str) -> ConfigUF:
        """Obtém configuração de CT-e para UF."""
        return MATRIZ_CONTINGENCIA_CTE.get(
            uf.upper(),
            MATRIZ_CONTINGENCIA_CTE["DEFAULT"]
        )

    @classmethod
    def obter_config_mdfe(cls, uf: str) -> ConfigUF:
        """Obtém configuração de MDF-e para UF."""
        return MATRIZ_CONTINGENCIA_MDFE.get(
            uf.upper(),
            MATRIZ_CONTINGENCIA_MDFE["DEFAULT"]
        )

    @classmethod
    def resolver_url(cls, config_url: str, servico: str) -> str:
        """
        Resolve URL de endpoint.

        Se config_url é um identificador (SVRS, SVAN, etc),
        busca nos endpoints centralizados.
        """
        if config_url in ENDPOINTS_CENTRALIZADOS:
            endpoints = ENDPOINTS_CENTRALIZADOS[config_url]
            return endpoints.get(servico, "")

        # URL direta
        return f"{config_url.rstrip('/')}/{servico}"

    @classmethod
    def listar_ufs_com_sefaz_propria(cls) -> List[str]:
        """Lista UFs que têm SEFAZ própria para NF-e."""
        ufs = []
        for uf, config in MATRIZ_CONTINGENCIA_NFE.items():
            if not config.principal.url.startswith(("SVRS", "SVAN")):
                ufs.append(uf)
        return sorted(ufs)

    @classmethod
    def obter_tipo_contingencia(cls, uf: str) -> TipoContingencia:
        """Obtém tipo de contingência para UF."""
        config = cls.obter_config_nfe(uf)
        return config.tipo_contingencia
