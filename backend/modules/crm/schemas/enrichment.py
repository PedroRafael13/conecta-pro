"""Enrichment schemas — shape que o frontend consome."""

from typing import Any

from pydantic import BaseModel, Field


class CNPJEnrichment(BaseModel):
    cnpj: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    cnae_principal: str | None = Field(
        default=None,
        description="Código + descrição do CNAE principal",
    )
    cnaes_secundarios: list[str] = []
    qsa: list[dict[str, Any]] = []
    capital_social: float | None = None
    situacao: str | None = None
    endereco: dict[str, str | None] = {}
    telefone: str | None = None
    porte: str | None = None
    data_abertura: str | None = None
    simples_nacional: bool | None = None
    cache_hit: bool = False


class CEPEnrichment(BaseModel):
    cep: str
    logradouro: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    coordenadas: dict[str, Any] | None = None
    cache_hit: bool = False


class TaxaItem(BaseModel):
    nome: str
    valor: float


class TaxasResponse(BaseModel):
    taxas: list[TaxaItem] = []
    selic: float | None = None
    cdi: float | None = None
    ipca: float | None = None
    cache_hit: bool = False
