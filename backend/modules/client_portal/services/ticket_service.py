"""
Servico de Tickets do Portal do Cliente.

Gerencia a criacao, listagem, detalhamento, mensagens e
fechamento de tickets de suporte abertos por clientes.
"""

import logging
import math
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.client_portal.models.ticket import (
    ClientTicket,
    TicketPriority,
    TicketStatus,
)
from modules.client_portal.models.ticket_message import ClientTicketMessage, SenderType
from modules.client_portal.schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketMessageResponse,
    TicketResponse,
    TicketUpdate,
)
from modules.people_management.ged.models.client import GedClient
from modules.people_management.ged.models.document_kit import GedDocumentKit

logger = logging.getLogger(__name__)


class PortalTicketService:
    """Servico de tickets de suporte do portal do cliente.

    Permite que clientes abram chamados, adicionem mensagens
    e acompanhem o status de suas solicitacoes.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_ticket(
        self,
        client_id: str,
        data: TicketCreate,
    ) -> TicketResponse:
        """Cria um novo ticket de suporte.

        Args:
            client_id: UUID do cliente autenticado.
            data: Dados do ticket a ser criado.

        Returns:
            TicketResponse com dados do ticket criado.

        Raises:
            ValueError: Se kit_id informado nao pertence ao cliente.
        """
        if data.kit_id:
            kit_result = await self.db.execute(
                select(GedDocumentKit).where(
                    GedDocumentKit.id == data.kit_id,
                    GedDocumentKit.client_id == client_id,
                )
            )
            if not kit_result.scalar_one_or_none():
                raise ValueError(f"Kit documental nao encontrado ou nao pertence ao cliente: {data.kit_id}")

        priority = data.priority
        if priority not in [p.value for p in TicketPriority]:
            priority = TicketPriority.NORMAL

        ticket = ClientTicket(
            client_id=client_id,
            kit_id=data.kit_id,
            subject=data.subject,
            description=data.description,
            status=TicketStatus.ABERTO,
            priority=priority,
        )
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)

        client_result = await self.db.execute(select(GedClient.name).where(GedClient.id == client_id))
        client_name = client_result.scalar_one_or_none() or "Cliente"

        initial_message = ClientTicketMessage(
            ticket_id=str(ticket.id),
            sender_type=SenderType.CLIENT,
            sender_id=client_id,
            sender_name=client_name,
            message=data.description,
        )
        self.db.add(initial_message)
        await self.db.flush()
        await self.db.refresh(ticket)

        logger.info(
            "Ticket criado: id=%s, client_id=%s, subject=%s",
            ticket.id,
            client_id,
            ticket.subject,
        )

        return await self._to_response(ticket)

    async def list_tickets(
        self,
        client_id: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: str | None = None,
    ) -> TicketListResponse:
        """Lista tickets do cliente com paginacao.

        Args:
            client_id: UUID do cliente autenticado.
            skip: Offset para paginacao.
            limit: Limite de registros por pagina.
            status_filter: Filtro opcional por status.

        Returns:
            TicketListResponse com tickets paginados.
        """
        base_filter = ClientTicket.client_id == client_id
        query = select(ClientTicket).where(base_filter)
        count_query = select(func.count()).select_from(ClientTicket).where(base_filter)

        if status_filter:
            query = query.where(ClientTicket.status == status_filter)
            count_query = count_query.where(ClientTicket.status == status_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            query.options(selectinload(ClientTicket.messages))
            .order_by(ClientTicket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        tickets = result.scalars().unique().all()

        page = (skip // limit) + 1 if limit > 0 else 1
        pages = math.ceil(total / limit) if limit > 0 else 0

        items = []
        for ticket in tickets:
            items.append(await self._to_response(ticket))

        return TicketListResponse(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            pages=pages,
        )

    async def get_ticket(self, client_id: str, ticket_id: str) -> TicketResponse:
        """Retorna detalhes de um ticket especifico.

        Args:
            client_id: UUID do cliente autenticado.
            ticket_id: UUID do ticket.

        Returns:
            TicketResponse com dados completos e mensagens.

        Raises:
            ValueError: Se ticket nao encontrado ou nao pertence ao cliente.
        """
        ticket = await self._get_ticket_or_raise(client_id, ticket_id)
        return await self._to_response(ticket)

    async def add_message(
        self,
        client_id: str,
        ticket_id: str,
        data: TicketUpdate,
    ) -> TicketResponse:
        """Adiciona uma mensagem a um ticket existente.

        Muda o status para ABERTO se estava RESPONDIDO ou EM_ANDAMENTO,
        indicando nova interacao do cliente.

        Args:
            client_id: UUID do cliente autenticado.
            ticket_id: UUID do ticket.
            data: Dados da mensagem.

        Returns:
            TicketResponse atualizado com a nova mensagem.

        Raises:
            ValueError: Se ticket nao encontrado, fechado ou nao pertence ao cliente.
        """
        ticket = await self._get_ticket_or_raise(client_id, ticket_id)

        if ticket.status == TicketStatus.FECHADO:
            raise ValueError("Nao e possivel adicionar mensagens a um ticket fechado")

        client_result = await self.db.execute(select(GedClient.name).where(GedClient.id == client_id))
        client_name = client_result.scalar_one_or_none() or "Cliente"

        message = ClientTicketMessage(
            ticket_id=str(ticket.id),
            sender_type=SenderType.CLIENT,
            sender_id=client_id,
            sender_name=client_name,
            message=data.message,
            attachments=data.attachments,
        )
        self.db.add(message)

        if ticket.status in (TicketStatus.RESPONDIDO, TicketStatus.EM_ANDAMENTO):
            ticket.status = TicketStatus.ABERTO

        await self.db.flush()
        await self.db.refresh(ticket)

        logger.info(
            "Mensagem adicionada ao ticket: ticket_id=%s, client_id=%s",
            ticket_id,
            client_id,
        )

        return await self._to_response(ticket)

    async def close_ticket(self, client_id: str, ticket_id: str) -> TicketResponse:
        """Fecha um ticket de suporte.

        Args:
            client_id: UUID do cliente autenticado.
            ticket_id: UUID do ticket.

        Returns:
            TicketResponse com status FECHADO.

        Raises:
            ValueError: Se ticket nao encontrado, ja fechado ou nao pertence ao cliente.
        """
        ticket = await self._get_ticket_or_raise(client_id, ticket_id)

        if ticket.status == TicketStatus.FECHADO:
            raise ValueError("Ticket ja esta fechado")

        ticket.status = TicketStatus.FECHADO
        ticket.closed_at = datetime.now(UTC)

        await self.db.flush()
        await self.db.refresh(ticket)

        logger.info(
            "Ticket fechado: ticket_id=%s, client_id=%s",
            ticket_id,
            client_id,
        )

        return await self._to_response(ticket)

    async def _get_ticket_or_raise(
        self,
        client_id: str,
        ticket_id: str,
    ) -> ClientTicket:
        """Busca ticket por ID garantindo que pertence ao cliente.

        Args:
            client_id: UUID do cliente autenticado.
            ticket_id: UUID do ticket.

        Returns:
            ClientTicket com mensagens carregadas.

        Raises:
            ValueError: Se ticket nao encontrado ou nao pertence ao cliente.
        """
        result = await self.db.execute(
            select(ClientTicket)
            .options(selectinload(ClientTicket.messages))
            .where(
                ClientTicket.id == ticket_id,
                ClientTicket.client_id == client_id,
            )
        )
        ticket = result.scalar_one_or_none()

        if not ticket:
            raise ValueError(f"Ticket nao encontrado: {ticket_id}")

        return ticket

    async def _to_response(self, ticket: ClientTicket) -> TicketResponse:
        """Converte ClientTicket ORM para TicketResponse."""
        messages = []
        if ticket.messages:
            messages = [
                TicketMessageResponse(
                    id=str(msg.id),
                    ticket_id=str(msg.ticket_id),
                    sender_type=msg.sender_type,
                    sender_name=msg.sender_name,
                    message=msg.message,
                    attachments=msg.attachments,
                    created_at=msg.created_at,
                )
                for msg in ticket.messages
            ]

        return TicketResponse(
            id=str(ticket.id),
            client_id=str(ticket.client_id),
            kit_id=str(ticket.kit_id) if ticket.kit_id else None,
            subject=ticket.subject,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            closed_at=ticket.closed_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            messages=messages,
        )
