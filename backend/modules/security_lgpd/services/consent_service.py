"""
Service de Consentimento LGPD.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class ConsentService:
    """Service para gerenciamento de consentimentos LGPD.

    Encapsula a logica de registro, consulta e revogacao
    de consentimentos de titulares de dados conforme Art. 7 LGPD.
    """

    # Armazenamento em memoria (em producao, usar banco de dados)
    _consents: dict[str, dict[str, Any]] = {}

    def __init__(self):
        """Inicializa o service."""
        pass

    def register_consent(
        self,
        titular_id: str,
        titular_email: str,
        purpose: str,
        legal_basis: str,
        description: str,
        expiration_days: int = 365,
    ) -> dict[str, Any]:
        """Registra consentimento de titular.

        Args:
            titular_id: UUID do titular.
            titular_email: Email do titular.
            purpose: Finalidade do consentimento.
            legal_basis: Base legal LGPD.
            description: Descricao detalhada.
            expiration_days: Dias ate expirar.

        Returns:
            Dict com dados do consentimento registrado.
        """
        consent_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expiration = now + timedelta(days=expiration_days)

        consent_data = {
            "consent_id": consent_id,
            "titular_id": titular_id,
            "titular_email": titular_email,
            "purpose": purpose,
            "legal_basis": legal_basis,
            "description": description,
            "status": "active",
            "created_at": now.isoformat(),
            "expires_at": expiration.isoformat(),
            "revoked_at": None,
            "revoke_reason": None,
        }

        self._consents[consent_id] = consent_data

        logger.info(
            "Consentimento registrado: titular=%s, finalidade=%s",
            titular_id,
            purpose,
        )

        return {
            "consent_id": consent_id,
            "titular_id": titular_id,
            "purpose": purpose,
            "legal_basis": legal_basis,
            "status": "active",
            "expires_at": expiration.isoformat(),
        }

    def get_consents_by_titular(self, titular_id: str) -> dict[str, Any]:
        """Consulta consentimentos de um titular.

        Args:
            titular_id: UUID do titular.

        Returns:
            Dict com lista de consentimentos.
        """
        consents = [c for c in self._consents.values() if c["titular_id"] == titular_id]

        return {
            "titular_id": titular_id,
            "consents": consents,
            "total": len(consents),
        }

    def revoke_consent(self, consent_id: str, reason: str) -> dict[str, Any]:
        """Revoga um consentimento.

        Args:
            consent_id: ID do consentimento.
            reason: Motivo da revogacao.

        Returns:
            Dict com confirmacao da revogacao.

        Raises:
            ValueError: Se consentimento nao encontrado.
        """
        if consent_id not in self._consents:
            raise ValueError(f"Consentimento nao encontrado: {consent_id}")

        consent = self._consents[consent_id]
        consent["status"] = "revoked"
        consent["revoked_at"] = datetime.utcnow().isoformat()
        consent["revoke_reason"] = reason

        logger.info("Consentimento revogado: %s", consent_id)

        return {
            "consent_id": consent_id,
            "status": "revoked",
            "reason": reason,
            "revoked_at": consent["revoked_at"],
        }

    def list_purposes(self) -> list[dict[str, str]]:
        """Lista finalidades de consentimento disponiveis.

        Returns:
            Lista de finalidades conforme Art. 7 LGPD.
        """
        return [
            {"id": "marketing", "description": "Marketing e comunicacoes"},
            {"id": "analytics", "description": "Analise de dados e metricas"},
            {"id": "personalization", "description": "Personalizacao de conteudo"},
            {"id": "service_provision", "description": "Prestacao de servicos"},
            {"id": "legal_obligation", "description": "Obrigacao legal"},
            {"id": "vital_interest", "description": "Interesse vital"},
            {"id": "public_interest", "description": "Interesse publico"},
            {"id": "legitimate_interest", "description": "Interesse legitimo"},
        ]

    def list_legal_bases(self) -> list[dict[str, str]]:
        """Lista bases legais LGPD disponiveis.

        Returns:
            Lista de bases legais conforme Art. 7 LGPD.
        """
        return [
            {"id": "consent", "description": "Consentimento do titular", "article": "Art. 7, I"},
            {"id": "contract", "description": "Execucao de contrato", "article": "Art. 7, V"},
            {"id": "legal_obligation", "description": "Obrigacao legal", "article": "Art. 7, II"},
            {"id": "vital_interest", "description": "Protecao da vida", "article": "Art. 7, VII"},
            {"id": "public_policy", "description": "Politica publica", "article": "Art. 7, III"},
            {"id": "research", "description": "Pesquisa", "article": "Art. 7, IV"},
            {"id": "legitimate_interest", "description": "Interesse legitimo", "article": "Art. 7, IX"},
            {"id": "credit_protection", "description": "Protecao ao credito", "article": "Art. 7, X"},
        ]
