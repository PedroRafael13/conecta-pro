"""
Repository de Solicitacao de Exclusao de Dados LGPD.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from modules.security_lgpd.models.erasure_request import (
    ErasureRequest,
    ErasureStatus,
)

logger = logging.getLogger(__name__)


class ErasureRepository:
    """Repository para operacoes de persistencia de solicitacoes de exclusao.

    Encapsula o acesso ao banco de dados para a entidade ErasureRequest.
    """

    def __init__(self, db: Session):
        """Inicializa o repository.

        Args:
            db: Sessao do banco de dados.
        """
        self.db = db

    def create(self, request: ErasureRequest) -> ErasureRequest:
        """Cria uma nova solicitacao de exclusao.

        Args:
            request: Instancia da solicitacao.

        Returns:
            Solicitacao criada.
        """
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        logger.info("Solicitacao de exclusao criada: %s", request.id)
        return request

    def get_by_id(self, request_id: UUID) -> ErasureRequest | None:
        """Busca solicitacao por ID.

        Args:
            request_id: UUID da solicitacao.

        Returns:
            Solicitacao ou None.
        """
        return self.db.query(ErasureRequest).filter(ErasureRequest.id == request_id).first()

    def get_by_titular(self, titular_id: UUID) -> list[ErasureRequest]:
        """Busca solicitacoes de um titular.

        Args:
            titular_id: UUID do titular.

        Returns:
            Lista de solicitacoes.
        """
        return (
            self.db.query(ErasureRequest)
            .filter(ErasureRequest.titular_id == titular_id)
            .order_by(ErasureRequest.created_at.desc())
            .all()
        )

    def update(self, request: ErasureRequest) -> ErasureRequest:
        """Atualiza uma solicitacao.

        Args:
            request: Instancia da solicitacao.

        Returns:
            Solicitacao atualizada.
        """
        request.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(request)
        return request

    def update_status(
        self,
        request_id: UUID,
        status: ErasureStatus,
        processor_id: str | None = None,
        notes: str | None = None,
    ) -> ErasureRequest | None:
        """Atualiza status de uma solicitacao.

        Args:
            request_id: UUID da solicitacao.
            status: Novo status.
            processor_id: ID do processador.
            notes: Notas de processamento.

        Returns:
            Solicitacao atualizada ou None.
        """
        request = self.get_by_id(request_id)
        if request:
            request.status = status
            if processor_id:
                request.processed_by = processor_id
            if notes:
                request.processing_notes = notes
            if status == ErasureStatus.COMPLETED:
                request.completed_at = datetime.utcnow()
            return self.update(request)
        return None

    def list_pending(self, limit: int = 100, offset: int = 0) -> list[ErasureRequest]:
        """Lista solicitacoes pendentes.

        Args:
            limit: Limite de resultados.
            offset: Offset para paginacao.

        Returns:
            Lista de solicitacoes pendentes.
        """
        return (
            self.db.query(ErasureRequest)
            .filter(ErasureRequest.status == ErasureStatus.PENDING)
            .order_by(ErasureRequest.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_overdue(self) -> list[ErasureRequest]:
        """Lista solicitacoes com prazo vencido.

        Returns:
            Lista de solicitacoes vencidas.
        """
        now = datetime.utcnow()
        return (
            self.db.query(ErasureRequest)
            .filter(ErasureRequest.status.in_([ErasureStatus.PENDING, ErasureStatus.IN_PROGRESS]))
            .filter(ErasureRequest.deadline_at < now)
            .all()
        )

    def count_by_status(self) -> dict:
        """Conta solicitacoes por status.

        Returns:
            Dict com contagens por status.
        """
        from sqlalchemy import func

        result = (
            self.db.query(ErasureRequest.status, func.count(ErasureRequest.id)).group_by(ErasureRequest.status).all()
        )
        return {status.value: count for status, count in result}
