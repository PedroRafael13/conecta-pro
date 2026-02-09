"""
Validador XSD para documentos fiscais.

Valida XMLs contra schemas oficiais.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Tentar importar lxml (preferido) ou usar ElementTree
try:
    from lxml import etree  # noqa: N817

    LXML_DISPONIVEL = True
except ImportError:
    LXML_DISPONIVEL = False

    logger.warning("lxml não disponível. Validação XSD limitada.")


@dataclass
class ResultadoValidacao:
    """Resultado de validação XSD."""

    valido: bool
    erros: list[str]
    avisos: list[str]
    schema_usado: str | None = None


class ValidadorXSD:
    """Valida XMLs contra schemas XSD oficiais."""

    # Diretório base dos schemas
    SCHEMAS_DIR = os.environ.get("GOV_SCHEMAS_DIR", "/opt/conecta-pro/schemas")

    # Mapeamento de tipos para arquivos XSD
    XSD_PATHS: dict[str, str] = {
        # NF-e
        "nfe_4.00": "nfe/nfe_v4.00.xsd",
        "nfe_proc_4.00": "nfe/procNFe_v4.00.xsd",
        "nfe_evento_4.00": "nfe/procEventoNFe_v1.00.xsd",
        "nfe_inut_4.00": "nfe/procInutNFe_v4.00.xsd",
        # CT-e
        "cte_4.00": "cte/cte_v4.00.xsd",
        "cte_proc_4.00": "cte/procCTe_v4.00.xsd",
        # MDF-e
        "mdfe_3.00": "mdfe/mdfe_v3.00.xsd",
        "mdfe_proc_3.00": "mdfe/procMDFe_v3.00.xsd",
        # NFS-e
        "nfse_abrasf_2.04": "nfse/nfse_v2.04.xsd",
        "nfse_nacional": "nfse/nfse_nacional_v1.00.xsd",
        # eSocial
        "esocial_s1000": "esocial/evtInfoEmpregador_v_S_01_02_00.xsd",
        "esocial_s1200": "esocial/evtRemun_v_S_01_02_00.xsd",
        "esocial_s2200": "esocial/evtAdmissao_v_S_01_02_00.xsd",
        "esocial_s2299": "esocial/evtDeslig_v_S_01_02_00.xsd",
        "esocial_lote": "esocial/loteEventos_v_S_01_02_00.xsd",
        # EFD-Reinf
        "reinf_r1000": "reinf/R1000_v2_01_02.xsd",
        "reinf_r2010": "reinf/R2010_v2_01_02.xsd",
        "reinf_r4010": "reinf/R4010_v2_01_02.xsd",
        "reinf_lote": "reinf/envioLoteEventos_v2_01_02.xsd",
    }

    # Cache de schemas carregados
    _schemas_cache: dict[str, any] = {}

    @classmethod
    def validar(cls, xml_content: bytes, tipo_schema: str, ignorar_avisos: bool = False) -> ResultadoValidacao:
        """
        Valida XML contra XSD.

        Args:
            xml_content: Conteúdo XML em bytes
            tipo_schema: Tipo do schema (ex: "nfe_4.00")
            ignorar_avisos: Se True, não inclui avisos no resultado

        Returns:
            ResultadoValidacao com status e erros
        """
        if not LXML_DISPONIVEL:
            # Validação básica sem lxml
            return cls._validar_basico(xml_content, tipo_schema)

        try:
            schema = cls._carregar_schema(tipo_schema)
            if schema is None:
                return ResultadoValidacao(
                    valido=True,
                    erros=[],
                    avisos=[f"Schema {tipo_schema} não encontrado. Validação ignorada."],
                    schema_usado=None,
                )

            # Parsear XML
            xml_doc = etree.fromstring(xml_content)

            # Validar
            if schema.validate(xml_doc):
                return ResultadoValidacao(
                    valido=True,
                    erros=[],
                    avisos=[],
                    schema_usado=tipo_schema,
                )
            else:
                erros = []
                avisos = []

                for erro in schema.error_log:
                    msg = f"Linha {erro.line}: {erro.message}"
                    if erro.level == etree.ErrorLevels.WARNING:
                        avisos.append(msg)
                    else:
                        erros.append(msg)

                return ResultadoValidacao(
                    valido=False,
                    erros=erros,
                    avisos=avisos if not ignorar_avisos else [],
                    schema_usado=tipo_schema,
                )

        except etree.XMLSyntaxError as e:
            return ResultadoValidacao(
                valido=False,
                erros=[f"Erro de sintaxe XML: {e}"],
                avisos=[],
                schema_usado=tipo_schema,
            )
        except Exception as e:
            logger.error(f"Erro na validação XSD: {e}")
            return ResultadoValidacao(
                valido=False,
                erros=[f"Erro na validação: {e}"],
                avisos=[],
                schema_usado=tipo_schema,
            )

    @classmethod
    def _carregar_schema(cls, tipo_schema: str) -> any | None:
        """Carrega e cacheia schema XSD."""
        if tipo_schema in cls._schemas_cache:
            return cls._schemas_cache[tipo_schema]

        xsd_relative = cls.XSD_PATHS.get(tipo_schema)
        if not xsd_relative:
            logger.warning(f"Schema não mapeado: {tipo_schema}")
            return None

        xsd_path = Path(cls.SCHEMAS_DIR) / xsd_relative

        if not xsd_path.exists():
            logger.warning(f"Arquivo XSD não encontrado: {xsd_path}")
            return None

        try:
            with open(xsd_path, "rb") as f:
                xsd_doc = etree.parse(f)
                schema = etree.XMLSchema(xsd_doc)
                cls._schemas_cache[tipo_schema] = schema
                logger.debug(f"Schema carregado: {tipo_schema}")
                return schema

        except Exception as e:
            logger.error(f"Erro ao carregar schema {tipo_schema}: {e}")
            return None

    @classmethod
    def _validar_basico(cls, xml_content: bytes, tipo_schema: str) -> ResultadoValidacao:
        """
        Validação básica sem lxml (apenas verifica se é XML bem formado).
        """
        try:
            etree.fromstring(xml_content)
            return ResultadoValidacao(
                valido=True,
                erros=[],
                avisos=["Validação XSD não disponível (instale lxml)"],
                schema_usado=None,
            )
        except Exception as e:
            return ResultadoValidacao(
                valido=False,
                erros=[f"XML mal formado: {e}"],
                avisos=[],
                schema_usado=None,
            )

    @classmethod
    def validar_nfe(cls, xml_content: bytes) -> ResultadoValidacao:
        """Atalho para validar NF-e."""
        return cls.validar(xml_content, "nfe_4.00")

    @classmethod
    def validar_cte(cls, xml_content: bytes) -> ResultadoValidacao:
        """Atalho para validar CT-e."""
        return cls.validar(xml_content, "cte_4.00")

    @classmethod
    def validar_mdfe(cls, xml_content: bytes) -> ResultadoValidacao:
        """Atalho para validar MDF-e."""
        return cls.validar(xml_content, "mdfe_3.00")

    @classmethod
    def validar_nfse(cls, xml_content: bytes, padrao: str = "abrasf") -> ResultadoValidacao:
        """Atalho para validar NFS-e."""
        if padrao == "nacional":
            return cls.validar(xml_content, "nfse_nacional")
        return cls.validar(xml_content, "nfse_abrasf_2.04")

    @classmethod
    def validar_esocial(cls, xml_content: bytes, tipo_evento: str) -> ResultadoValidacao:
        """
        Valida evento eSocial.

        Args:
            xml_content: XML do evento
            tipo_evento: Tipo (S-1000, S-1200, etc)
        """
        # Mapear tipo de evento para schema
        mapa = {
            "S-1000": "esocial_s1000",
            "S-1200": "esocial_s1200",
            "S-2200": "esocial_s2200",
            "S-2299": "esocial_s2299",
        }

        schema_tipo = mapa.get(tipo_evento.upper(), "esocial_lote")
        return cls.validar(xml_content, schema_tipo)

    @classmethod
    def limpar_cache(cls):
        """Limpa cache de schemas."""
        cls._schemas_cache.clear()
        logger.info("Cache de schemas XSD limpo")

    @classmethod
    def listar_schemas_disponiveis(cls) -> list[str]:
        """Lista schemas disponíveis no diretório."""
        disponiveis = []

        for tipo, path_rel in cls.XSD_PATHS.items():
            path_full = Path(cls.SCHEMAS_DIR) / path_rel
            if path_full.exists():
                disponiveis.append(tipo)

        return disponiveis

    @classmethod
    def detectar_tipo_documento(cls, xml_content: bytes) -> str | None:
        """
        Detecta tipo de documento a partir do XML.

        Returns:
            Tipo do schema ou None se não detectado
        """
        try:
            if LXML_DISPONIVEL:
                root = etree.fromstring(xml_content)
            else:
                root = etree.fromstring(xml_content)

            tag = root.tag.lower()

            # Remover namespace
            if "}" in tag:
                tag = tag.split("}")[1]

            # Mapear tags para tipos
            mapa_tags = {
                "nfe": "nfe_4.00",
                "nfeproc": "nfe_proc_4.00",
                "procnfe": "nfe_proc_4.00",
                "cte": "cte_4.00",
                "cteproc": "cte_proc_4.00",
                "proccte": "cte_proc_4.00",
                "mdfe": "mdfe_3.00",
                "mdfeproc": "mdfe_proc_3.00",
                "compnfse": "nfse_abrasf_2.04",
                "nfse": "nfse_abrasf_2.04",
                "esocial": "esocial_lote",
                "reinf": "reinf_lote",
            }

            return mapa_tags.get(tag)

        except Exception as e:
            logger.warning(f"Não foi possível detectar tipo do documento: {e}")
            return None
