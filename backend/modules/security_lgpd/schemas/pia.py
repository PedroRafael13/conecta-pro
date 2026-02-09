"""
Schemas de PIA (Privacy Impact Assessment) do modulo de seguranca LGPD.
"""

from typing import Any

from pydantic import BaseModel, Field


class PIARequest(BaseModel):
    """Request para avaliacao de impacto de privacidade.

    Attributes:
        project_name: Nome do projeto/processo.
        description: Descricao do tratamento de dados.
        data_categories: Categorias de dados tratados.
        processing_purposes: Finalidades do tratamento.
        data_subjects: Titulares afetados.
        risk_factors: Fatores de risco identificados.
    """

    project_name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome do projeto",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Descricao do tratamento",
    )
    data_categories: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Categorias de dados tratados",
    )
    processing_purposes: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Finalidades do tratamento",
    )
    data_subjects: list[str] = Field(
        default_factory=lambda: ["funcionarios"],
        description="Titulares afetados",
    )
    risk_factors: list[str] = Field(
        default_factory=list,
        description="Fatores de risco identificados",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_name": "Sistema de RH",
                "description": "Tratamento de dados pessoais para gestao de recursos humanos",
                "data_categories": ["dados_pessoais", "dados_profissionais"],
                "processing_purposes": ["gestao_contrato", "folha_pagamento"],
                "data_subjects": ["funcionarios", "candidatos"],
                "risk_factors": ["volume_alto", "dados_sensiveis"],
            }
        }
    }


class PIAResponse(BaseModel):
    """Response de avaliacao PIA."""

    assessment_id: str = Field(..., description="ID da avaliacao")
    project_name: str = Field(..., description="Nome do projeto")
    risk_level: str = Field(..., description="Nivel de risco")
    requires_dpia: bool = Field(..., description="Requer DPIA completo")
    recommendations: list[str] = Field(..., description="Recomendacoes")
    details: dict[str, Any] | None = Field(None, description="Detalhes completos")
