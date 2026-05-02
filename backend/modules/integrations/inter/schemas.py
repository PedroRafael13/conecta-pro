"""D6 — Pydantic schemas para respostas da API Inter."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class SaldoResponse(BaseModel):
    disponivel: Decimal
    bloqueado: Decimal
    total: Decimal
    conta: str
    updated_at: datetime | None = None


class TransacaoResponse(BaseModel):
    id: str
    data_lancamento: date
    tipo_operacao: str  # 'C' ou 'D'
    tipo_transacao: str | None
    valor: Decimal
    descricao: str | None
    detalhes_pagador: dict[str, Any] | None = None
    detalhes_destinatario: dict[str, Any] | None = None


class ExtratoResponse(BaseModel):
    total: int
    transactions: list[TransacaoResponse]


class ExtratoResumoItem(BaseModel):
    tipo_operacao: str
    tipo_transacao: str | None
    qtd: int
    total: Decimal


class ExtratoResumoResponse(BaseModel):
    periodo_dias: int
    resumo: list[ExtratoResumoItem]


class CobrancaResponse(BaseModel):
    id: str
    cobranca_id_inter: str | None
    seu_numero: str | None
    valor: Decimal
    vencimento: date
    status: str
    url_boleto: str | None = None
    pix_copia_cola: str | None = None
    barcode: str | None = None
    linha_digitavel: str | None = None
    descricao: str | None = None


class ConciliacaoFolhaItem(BaseModel):
    id: str
    competencia: str
    status: str
    match_tipo: str | None
    valor_liquido: Decimal
    data_paga: date | None = None
    nome: str | None = None
    cpf: str | None = None


class ConciliacaoFolhaResponse(BaseModel):
    competencia: str
    matches_fortes: int
    matches_medios: int
    em_conciliacao: int
    total_txs_analisadas: int


class PixRecebidoResponse(BaseModel):
    id: str
    end_to_end_id: str
    txid: str | None
    valor: Decimal
    pagador: dict[str, Any] | None = None
    data_horario: datetime | None = None
