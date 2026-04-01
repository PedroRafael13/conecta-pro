"""
Schemas de tickets do Portal do Cliente.

Define os modelos de request/response para criacao, listagem
e atualizacao de tickets de suporte.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketMessageResponse(BaseModel):
    """Response de uma mensagem de ticket."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID da mensagem")
    ticket_id: str = Field(..., description="UUID do ticket")
    sender_type: str = Field(..., description="Tipo do remetente: CLIENT ou INTERNAL")
    sender_name: str = Field(..., description="Nome do remetente")
    message: str = Field(..., description="Conteudo da mensagem")
    attachments: list[dict] | None = Field(None, description="Lista de anexos")
    created_at: datetime = Field(..., description="Data/hora de criacao")


class TicketCreate(BaseModel):
    """Request para criar um ticket de suporte."""

    model_config = ConfigDict(from_attributes=True)

    kit_id: str | None = Field(
        None,
        description="UUID do kit documental relacionado (opcional)",
    )
    subject: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Assunto do ticket",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descricao detalhada do problema ou solicitacao",
    )
    priority: str = Field(
        default="NORMAL",
        description="Prioridade: BAIXA, NORMAL, ALTA, URGENTE",
    )


class TicketResponse(BaseModel):
    """Response de um ticket de suporte."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID do ticket")
    client_id: str = Field(..., description="UUID do cliente")
    kit_id: str | None = Field(None, description="UUID do kit relacionado")
    subject: str = Field(..., description="Assunto do ticket")
    description: str = Field(..., description="Descricao do ticket")
    status: str = Field(..., description="Status atual do ticket")
    priority: str = Field(..., description="Prioridade do ticket")
    closed_at: datetime | None = Field(None, description="Data/hora do fechamento")
    created_at: datetime = Field(..., description="Data/hora de criacao")
    updated_at: datetime = Field(..., description="Data/hora da ultima atualizacao")
    messages: list[TicketMessageResponse] = Field(
        default_factory=list,
        description="Mensagens do ticket",
    )


class TicketUpdate(BaseModel):
    """Request para adicionar mensagem a um ticket."""

    model_config = ConfigDict(from_attributes=True)

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Conteudo da mensagem",
    )
    attachments: list[dict] | None = Field(
        None,
        description="Lista de anexos [{name, size}]",
    )


class TicketListResponse(BaseModel):
    """Response paginada de tickets."""

    model_config = ConfigDict(from_attributes=True)

    items: list[TicketResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    pages: int = Field(default=0)
