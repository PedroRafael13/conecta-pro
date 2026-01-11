"""
Parser de respostas da API PNCP
===============================
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

from modules.bidding.integrations.pncp.models import (
    PNCPCompra, PNCPOrgao, PNCPItem, PNCPDocumento, PNCPContrato
)

logger = logging.getLogger(__name__)


class PNCPParser:
    """Parser para converter respostas da API PNCP em DTOs."""

    def parse_compra(self, data: Dict[str, Any]) -> PNCPCompra:
        """
        Converte dados de compra da API para DTO.

        Args:
            data: Dict com dados da compra

        Returns:
            PNCPCompra
        """
        orgao_data = data.get("orgaoEntidade", {})

        orgao = PNCPOrgao(
            cnpj=orgao_data.get("cnpj", ""),
            razao_social=orgao_data.get("razaoSocial", ""),
            nome_unidade=orgao_data.get("nomeUnidade"),
            uf=orgao_data.get("uf", "AM"),
            municipio=orgao_data.get("municipio"),
            codigo_ibge=orgao_data.get("codigoIbge"),
            esfera=orgao_data.get("esferaId")
        )

        return PNCPCompra(
            numero_compra=str(data.get("numeroCompra", "")),
            ano_compra=data.get("anoCompra", datetime.now().year),
            sequencial_compra=data.get("sequencialCompra", 0),
            numero_controle_pncp=data.get("numeroControlePNCP"),
            orgao=orgao,
            modalidade_id=data.get("modalidadeId"),
            modalidade_nome=data.get("modalidadeNome"),
            modo_disputa_id=data.get("modoDisputaId"),
            modo_disputa_nome=data.get("modoDisputaNome"),
            tipo_contratacao=data.get("tipoContratacao"),
            tipo_instrumento_convocatorio=data.get("tipoInstrumentoConvocatorioNome"),
            objeto=data.get("objetoCompra", ""),
            objeto_resumido=self._truncate(data.get("objetoCompra", ""), 500),
            informacao_complementar=data.get("informacaoComplementar"),
            valor_estimado_total=self._parse_decimal(data.get("valorEstimadoTotal")),
            valor_homologado_total=self._parse_decimal(data.get("valorHomologadoTotal")),
            data_publicacao_pncp=self._parse_datetime(data.get("dataPublicacaoPncp")),
            data_abertura_proposta=self._parse_datetime(data.get("dataAberturaProposta")),
            data_encerramento_proposta=self._parse_datetime(data.get("dataEncerramentoProposta")),
            data_resultado=self._parse_datetime(data.get("dataResultado")),
            situacao_compra_id=data.get("situacaoCompraId"),
            situacao_compra_nome=data.get("situacaoCompraNome"),
            link_sistema_origem=data.get("linkSistemaOrigem"),
            link_pncp=self._gerar_link_pncp(orgao.cnpj, data.get("anoCompra"), data.get("sequencialCompra")),
            srp=data.get("srp", False),
            processo_administrativo=data.get("processoAdministrativo"),
            justificativa=data.get("justificativa")
        )

    def parse_item(self, data: Dict[str, Any]) -> PNCPItem:
        """
        Converte dados de item para DTO.

        Args:
            data: Dict com dados do item

        Returns:
            PNCPItem
        """
        return PNCPItem(
            numero_item=data.get("numeroItem", 0),
            descricao=data.get("descricao", ""),
            quantidade=self._parse_decimal(data.get("quantidade")) or Decimal("1"),
            unidade_medida=data.get("unidadeMedida", "UN"),
            valor_unitario_estimado=self._parse_decimal(data.get("valorUnitarioEstimado")),
            valor_total_estimado=self._parse_decimal(data.get("valorTotalEstimado")),
            situacao=data.get("situacao"),
            codigo_material_servico=data.get("codigoMaterialServico"),
            tipo_beneficio=data.get("tipoBeneficio")
        )

    def parse_documento(self, data: Dict[str, Any]) -> PNCPDocumento:
        """
        Converte dados de documento para DTO.

        Args:
            data: Dict com dados do documento

        Returns:
            PNCPDocumento
        """
        return PNCPDocumento(
            titulo=data.get("titulo", "Documento"),
            tipo=data.get("tipo", "documento"),
            url=data.get("url", ""),
            data_publicacao=self._parse_datetime(data.get("dataPublicacao")),
            tamanho_bytes=data.get("tamanhoBytes"),
            hash_arquivo=data.get("hashArquivo")
        )

    def parse_contrato(self, data: Dict[str, Any]) -> PNCPContrato:
        """
        Converte dados de contrato para DTO.

        Args:
            data: Dict com dados do contrato

        Returns:
            PNCPContrato
        """
        return PNCPContrato(
            numero_contrato=str(data.get("numeroContrato", "")),
            ano_contrato=data.get("anoContrato", datetime.now().year),
            sequencial_contrato=data.get("sequencialContrato", 0),
            cnpj_orgao=data.get("orgaoEntidade", {}).get("cnpj", ""),
            nome_orgao=data.get("orgaoEntidade", {}).get("razaoSocial", ""),
            cnpj_fornecedor=data.get("fornecedor", {}).get("cnpj", ""),
            nome_fornecedor=data.get("fornecedor", {}).get("razaoSocial", ""),
            valor_inicial=self._parse_decimal(data.get("valorInicial")) or Decimal("0"),
            valor_global=self._parse_decimal(data.get("valorGlobal")),
            data_assinatura=self._parse_date(data.get("dataAssinatura")),
            data_publicacao=self._parse_date(data.get("dataPublicacao")),
            data_vigencia_inicio=self._parse_date(data.get("dataVigenciaInicio")),
            data_vigencia_fim=self._parse_date(data.get("dataVigenciaFim")),
            objeto=data.get("objetoContrato", ""),
            link_pncp=data.get("linkPncp")
        )

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """Parse de datetime."""
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        try:
            # ISO format with timezone
            if "T" in str(value):
                return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            # Simple date format
            return datetime.strptime(str(value), "%Y-%m-%d")
        except Exception:
            return None

    def _parse_date(self, value: Any):
        """Parse de date."""
        dt = self._parse_datetime(value)
        return dt.date() if dt else None

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse de decimal."""
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except Exception:
            return None

    def _truncate(self, text: str, max_length: int) -> str:
        """Trunca texto para tamanho maximo."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _gerar_link_pncp(
        self,
        cnpj: str,
        ano: int,
        sequencial: int
    ) -> str:
        """Gera link para visualizacao no PNCP."""
        if not all([cnpj, ano, sequencial]):
            return ""
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
