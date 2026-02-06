"""
Schemas para integrações com Receita Federal.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class ValidateDocumentRequest(BaseModel):
    """Request para validação de documento.

    Attributes:
        documento: Número do documento (CPF ou CNPJ).
        tipo: Tipo do documento.
    """

    documento: str = Field(
        ...,
        min_length=11,
        max_length=18,
        description="Numero do documento (CPF ou CNPJ)",
    )
    tipo: str = Field(
        ...,
        description="Tipo do documento",
        pattern=r"^(cpf|cnpj)$",
    )

    @field_validator("documento")
    @classmethod
    def clean_documento(cls, v: str) -> str:
        """Remove caracteres especiais do documento."""
        return "".join(c for c in v if c.isdigit())


class ConsultaCPFRequest(BaseModel):
    """Request para consulta de CPF.

    Attributes:
        cpf: Número do CPF.
        data_nascimento: Data de nascimento do titular.
    """

    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="Numero do CPF",
    )
    data_nascimento: date = Field(..., description="Data de nascimento")


class ConsultaCNPJRequest(BaseModel):
    """Request para consulta de CNPJ.

    Attributes:
        cnpj: Número do CNPJ.
    """

    cnpj: str = Field(
        ...,
        min_length=14,
        max_length=18,
        description="Numero do CNPJ",
    )
