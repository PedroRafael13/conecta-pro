"""
Service para integrações com SEFAZ (NFe/NFCe).
"""

import logging
from datetime import datetime
from typing import Any

# Imports relativos do módulo pai
from modules.government_integrations.utils import (
    DocumentType,
    get_sefaz_manager,
)

logger = logging.getLogger(__name__)


class SEFAZService:
    """Service para operações com SEFAZ (NFe/NFCe)."""

    @staticmethod
    def emitir_nfe(
        tipo: str,
        destinatario: dict[str, Any],
        produtos: list[dict[str, Any]],
        pagamento: dict[str, Any],
        observacoes: str | None = None,
    ) -> dict[str, Any]:
        """
        Emite NFe ou NFCe.

        Args:
            tipo: Tipo do documento (nfe ou nfce).
            destinatario: Dados do destinatário.
            produtos: Lista de produtos.
            pagamento: Dados de pagamento.
            observacoes: Observações adicionais.

        Returns:
            Dict com dados da emissão.

        Raises:
            ValueError: Se dados inválidos.
        """
        sefaz = get_sefaz_manager()
        doc_type = DocumentType(tipo.lower())

        resultado = sefaz.emit_document(
            doc_type=doc_type,
            destinatario=destinatario,
            produtos=produtos,
            pagamento=pagamento,
            observacoes=observacoes,
        )

        logger.info(
            "NFe emitida: tipo=%s, chave=%s",
            tipo,
            resultado.get("chave_acesso"),
        )

        return {
            "tipo": tipo,
            "chave_acesso": resultado.get("chave_acesso"),
            "numero": resultado.get("numero"),
            "serie": resultado.get("serie"),
            "protocolo": resultado.get("protocolo"),
            "status": "enviada",
            "data_emissao": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def consultar_nfe(chave_acesso: str) -> dict[str, Any]:
        """
        Consulta NFe pela chave de acesso.

        Args:
            chave_acesso: Chave de acesso da NFe (44 dígitos).

        Returns:
            Dict com dados da NFe.

        Raises:
            ValueError: Se NFe não encontrada.
        """
        sefaz = get_sefaz_manager()
        resultado = sefaz.query_document(chave_acesso)

        return {
            "chave_acesso": chave_acesso,
            "status": resultado.get("status"),
            "protocolo": resultado.get("protocolo"),
            "data_autorizacao": resultado.get("data_autorizacao"),
            "motivo": resultado.get("motivo"),
        }
