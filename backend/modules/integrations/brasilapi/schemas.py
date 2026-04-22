"""Pydantic schemas for BrasilAPI responses (subset used by Conecta PRO)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class QSAMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nome_socio: str | None = None
    qualificacao_socio: str | None = None
    data_entrada_sociedade: str | None = None


class CNPJResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cnpj: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    cnae_fiscal: int | None = None
    cnae_fiscal_descricao: str | None = None
    cnae_fiscal_secundario: list[dict[str, Any]] = []
    qsa: list[QSAMember] = []
    capital_social: float | None = None
    situacao_cadastral: Any | None = None  # BrasilAPI returns int (2=Ativa)
    descricao_situacao_cadastral: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    municipio: str | None = None
    uf: str | None = None
    cep: str | None = None
    ddd_telefone_1: str | None = None
    porte: str | None = None
    data_inicio_atividade: str | None = None
    opcao_pelo_simples: bool | None = None


class CEPCoordinates(BaseModel):
    model_config = ConfigDict(extra="ignore")
    longitude: str | None = None
    latitude: str | None = None


class CEPLocation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str | None = None
    coordinates: CEPCoordinates | None = None

    @field_validator("coordinates", mode="before")
    @classmethod
    def empty_dict_to_none(cls, v: Any) -> Any:
        # BrasilAPI may return {} for coordinates when unavailable
        if isinstance(v, dict) and not v:
            return None
        return v


class CEPResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cep: str
    state: str | None = None
    city: str | None = None
    neighborhood: str | None = None
    street: str | None = None
    service: str | None = None
    location: CEPLocation | None = None


class Taxa(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nome: str
    valor: float
