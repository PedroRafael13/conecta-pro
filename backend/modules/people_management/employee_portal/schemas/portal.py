"""
Schemas do portal principal — login, dashboard.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PortalLoginRequest(BaseModel):
    """Request para autenticacao no portal do funcionario.

    Attributes:
        cpf: CPF do funcionario (com ou sem formatacao).
        password: Senha de acesso ao portal.
    """

    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do funcionario")
    password: str = Field(..., min_length=4, description="Senha do portal")

    model_config = ConfigDict(from_attributes=True)


class PortalLoginResponse(BaseModel):
    """Response apos autenticacao bem-sucedida.

    Attributes:
        access_token: Token JWT para autenticacao nas demais rotas.
        employee_name: Nome do funcionario logado.
        employee_id: UUID do funcionario.
    """

    access_token: str
    employee_name: str
    employee_id: UUID

    model_config = ConfigDict(from_attributes=True)


class PortalDashboard(BaseModel):
    """Dados do dashboard principal do portal.

    Attributes:
        name: Nome do funcionario.
        position: Cargo atual.
        workplace: Nome do posto de trabalho.
        next_shift: Data/hora do proximo turno.
        pending_documents: Quantidade de documentos pendentes de assinatura.
        unread_notifications: Quantidade de notificacoes nao lidas.
    """

    name: str
    position: str | None = None
    workplace: str | None = None
    next_shift: datetime | None = None
    pending_documents: int = 0
    unread_notifications: int = 0

    model_config = ConfigDict(from_attributes=True)
