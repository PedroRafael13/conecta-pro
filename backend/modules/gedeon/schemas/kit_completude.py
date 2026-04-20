"""Schemas Pydantic — FASE 4 BLOCO 3 / T2 (§28).

Refletem 1:1 os dataclasses do KitBuilderService v1.22 (§26).
Usados pelos endpoints definidos em §27.

§13.1 Chesterton: NÃO inventar campos. Bater 1:1 com §27.4 e §27.6.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from modules.gedeon.services.kit_builder_service import CompletudeKit


class DocumentoPresenteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tipo_documento: str
    escopo: str
    onvio_document_id: UUID
    nome_arquivo: str
    revisao_pendente: bool


class DocumentoFaltanteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tipo_documento: str
    escopo: str
    obrigatorio: bool
    periodicidade: str
    motivo: str


class MetricasKitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_esperado: int
    total_presente_confirmado: int
    total_presente_pendente_revisao: int
    total_faltante: int
    pct_completude_confirmada: float
    pct_completude_total: float


class CompletudeKitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    condominio_id: UUID
    condominio_nome: str
    tipo_servico: str
    mes_ref: str
    gerado_em: datetime
    docs_presentes: list[DocumentoPresenteResponse]
    docs_faltantes: list[DocumentoFaltanteResponse]
    metricas: MetricasKitResponse

    @classmethod
    def from_dataclass(cls, kit: CompletudeKit) -> CompletudeKitResponse:
        """Converte dataclass CompletudeKit para response Pydantic."""
        return cls.model_validate(dataclasses.asdict(kit))
