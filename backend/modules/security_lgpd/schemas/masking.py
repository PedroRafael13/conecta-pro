"""
Schemas de mascaramento do modulo de seguranca LGPD.
"""

from pydantic import BaseModel, Field


class MaskDataRequest(BaseModel):
    """Request para mascaramento de dados.

    Attributes:
        data: Dado a ser mascarado.
        category: Categoria do dado (cpf, email, phone, card, etc).
        level: Nivel de mascaramento (partial, full, reversible).
    """

    data: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Dado a mascarar",
    )
    category: str = Field(
        ...,
        description="Categoria do dado PII",
        pattern=r"^(cpf|cnpj|email|phone|card|name|address|generic)$",
    )
    level: str = Field(
        default="partial",
        description="Nivel de mascaramento",
        pattern=r"^(partial|full|reversible)$",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "123.456.789-00",
                "category": "cpf",
                "level": "partial",
            }
        }
    }


class MaskingCategory(BaseModel):
    """Categoria de mascaramento disponivel."""

    id: str = Field(..., description="ID da categoria")
    description: str = Field(..., description="Descricao da categoria")


class MaskingLevel(BaseModel):
    """Nivel de mascaramento disponivel."""

    id: str = Field(..., description="ID do nivel")
    description: str = Field(..., description="Descricao do nivel")


class MaskingFormatResponse(BaseModel):
    """Response com formatos de mascaramento disponiveis."""

    categories: list[MaskingCategory] = Field(..., description="Categorias disponiveis")
    levels: list[MaskingLevel] = Field(..., description="Niveis disponiveis")
