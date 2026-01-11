"""
Service para integrações com SEFAZ (NFe/NFCe).
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, "/opt/conecta-pro")

from government_integrations import (
    get_sefaz_manager,
    DocumentType,
)

logger = logging.getLogger(__name__)


class SEFAZService:
    """Service para operações com SEFAZ (NFe/NFCe)."""

    @staticmethod
    def emitir_nfe(
        tipo: str,
        destinatario: Dict[str, Any],
        produtos: List[Dict[str, Any]],
        pagamento: Dict[str, Any],
        observacoes: Optional[str] = None,
    ) -> Dict[str, Any]:
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
        doc_type = DocumentType(tipo.upper())

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
    def consultar_nfe(chave_acesso: str) -> Dict[str, Any]:
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
