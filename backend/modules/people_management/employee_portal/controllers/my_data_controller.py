"""
My Data Controller — Dados pessoais do funcionario.

Endpoints:
- GET /portal/my-data
- PUT /portal/my-data
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal - Meus Dados"])


class MyDataResponse(BaseModel):
    """Dados pessoais do funcionario (somente leitura parcial).

    Attributes:
        nome: Nome completo.
        cpf: CPF (mascarado).
        cargo: Cargo atual.
        data_admissao: Data de admissao.
        telefone: Telefone de contato.
        email: Email pessoal.
        endereco: Endereco completo.
        contato_emergencia: Contato de emergencia.
    """

    nome: str | None = None
    cpf: str | None = None
    cargo: str | None = None
    data_admissao: str | None = None
    telefone: str | None = None
    email: str | None = None
    endereco: str | None = None
    contato_emergencia: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateMyDataRequest(BaseModel):
    """Campos que o funcionario pode alterar pelo portal.

    Apenas telefone, email, endereco e contato de emergencia
    podem ser atualizados pelo proprio funcionario.

    Attributes:
        telefone: Novo telefone de contato.
        email: Novo email pessoal.
        endereco: Novo endereco.
        contato_emergencia: Novo contato de emergencia.
    """

    telefone: str | None = Field(None, max_length=20, description="Telefone de contato")
    email: str | None = Field(None, max_length=255, description="Email pessoal")
    endereco: str | None = Field(None, max_length=500, description="Endereco completo")
    contato_emergencia: str | None = Field(None, max_length=255, description="Contato de emergencia")

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/my-data",
    response_model=MyDataResponse,
    summary="Meus dados pessoais",
    description="Retorna dados pessoais do funcionario logado.",
)
async def get_my_data(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna dados pessoais do funcionario.

    O CPF e retornado mascarado por seguranca (ex: ***.***.***-XX).

    Args:
        db: Sessao do banco de dados.

    Returns:
        MyDataResponse com dados do funcionario.
    """
    # TODO: Extrair employee_id do token JWT do portal
    return MyDataResponse(
        nome="Funcionario",
        cpf="***.***.***.***-**",
        cargo=None,
        data_admissao=None,
        telefone=None,
        email=None,
        endereco=None,
        contato_emergencia=None,
    )


@router.put(
    "/my-data",
    response_model=MyDataResponse,
    summary="Atualizar meus dados",
    description="Atualiza campos limitados dos dados pessoais (telefone, email, endereco, contato_emergencia).",
)
async def update_my_data(
    update_data: UpdateMyDataRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados pessoais do funcionario.

    Apenas os campos telefone, email, endereco e contato_emergencia
    podem ser alterados pelo funcionario via portal.

    Args:
        update_data: Dados a serem atualizados.
        db: Sessao do banco de dados.

    Returns:
        MyDataResponse com dados atualizados.

    Raises:
        HTTPException: 400 se nenhum campo fornecido.
    """
    # Verificar se pelo menos um campo foi fornecido
    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar. Campos permitidos: telefone, email, endereco, contato_emergencia.",
        )

    # Campos permitidos para atualizacao pelo funcionario
    allowed_fields = {"telefone", "email", "endereco", "contato_emergencia"}
    invalid_fields = set(update_fields.keys()) - allowed_fields
    if invalid_fields:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Campos nao permitidos para atualizacao: {invalid_fields}",
        )

    # TODO: Extrair employee_id do token JWT e atualizar no banco
    try:
        from modules.operacional.models.employee import Employee  # noqa: F401

        # Placeholder: buscar e atualizar funcionario
        # query = select(Employee).where(Employee.id == employee_id)
        # result = await db.execute(query)
        # employee = result.scalar_one_or_none()
        # for field, value in update_fields.items():
        #     setattr(employee, field, value)
        # await db.commit()

        logger.info("Dados atualizados (simulacao): %s", update_fields)

    except ImportError:
        logger.warning("Modelo Employee nao disponivel para atualizacao.")

    return MyDataResponse(
        nome="Funcionario",
        cpf="***.***.***.***-**",
        **dict(update_fields.items()),
    )
