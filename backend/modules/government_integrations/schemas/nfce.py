"""
Schemas para NFC-e (Nota Fiscal de Consumidor Eletronica).
Modelo 65 - Vendas ao consumidor final.

Author: Conecta PRO
Date: 2026-01-17
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TipoPagamentoNFCe(str, Enum):
    """Tipos de pagamento aceitos na NFC-e."""
    DINHEIRO = "01"
    CHEQUE = "02"
    CARTAO_CREDITO = "03"
    CARTAO_DEBITO = "04"
    CREDITO_LOJA = "05"
    VALE_ALIMENTACAO = "10"
    VALE_REFEICAO = "11"
    VALE_PRESENTE = "12"
    VALE_COMBUSTIVEL = "13"
    PIX = "17"
    TRANSFERENCIA = "18"
    CASHBACK = "19"
    SEM_PAGAMENTO = "90"
    OUTROS = "99"


class ConsumidorNFCe(BaseModel):
    """Dados do consumidor (opcional na NFC-e)."""
    cpf: Optional[str] = Field(None, min_length=11, max_length=14, description="CPF do consumidor")
    nome: Optional[str] = Field(None, max_length=60, description="Nome do consumidor")
    email: Optional[str] = Field(None, max_length=60, description="Email para envio do XML")


class ItemNFCe(BaseModel):
    """Item/Produto da NFC-e."""
    codigo: str = Field(..., min_length=1, max_length=60, description="Codigo do produto")
    ean: Optional[str] = Field(None, max_length=14, description="Codigo EAN/GTIN")
    descricao: str = Field(..., min_length=1, max_length=120, description="Descricao do produto")
    ncm: str = Field(..., min_length=8, max_length=8, description="Codigo NCM")
    cest: Optional[str] = Field(None, min_length=7, max_length=7, description="Codigo CEST")
    cfop: str = Field(default="5102", min_length=4, max_length=4, description="CFOP")
    unidade: str = Field(default="UN", max_length=6, description="Unidade de medida")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade")
    valor_unitario: Decimal = Field(..., gt=0, description="Valor unitario")
    valor_desconto: Decimal = Field(default=Decimal("0"), ge=0, description="Valor do desconto")

    # Tributacao
    origem: str = Field(default="0", description="Origem da mercadoria (0=Nacional)")
    cst_icms: str = Field(default="102", description="CST/CSOSN ICMS")
    aliquota_icms: Decimal = Field(default=Decimal("0"), ge=0, description="Aliquota ICMS")

    @property
    def valor_total(self) -> Decimal:
        """Calcula valor total do item."""
        return (self.quantidade * self.valor_unitario) - self.valor_desconto


class PagamentoNFCe(BaseModel):
    """Dados de pagamento da NFC-e."""
    tipo: TipoPagamentoNFCe = Field(..., description="Tipo de pagamento")
    valor: Decimal = Field(..., gt=0, description="Valor do pagamento")
    bandeira: Optional[str] = Field(None, description="Bandeira do cartao")
    autorizacao: Optional[str] = Field(None, description="Numero da autorizacao")


class NFCeEmissaoRequest(BaseModel):
    """Request para emissao de NFC-e."""

    # Consumidor (opcional)
    consumidor: Optional[ConsumidorNFCe] = Field(None, description="Dados do consumidor")

    # Itens
    itens: List[ItemNFCe] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Lista de itens (max 500 para NFC-e)"
    )

    # Pagamentos
    pagamentos: List[PagamentoNFCe] = Field(
        ...,
        min_length=1,
        description="Formas de pagamento"
    )

    # Configuracoes
    serie: int = Field(default=1, ge=1, le=999, description="Serie da NFC-e")

    # Contingencia
    contingencia: bool = Field(default=False, description="Emitir em contingencia offline")

    @field_validator('itens')
    @classmethod
    def validate_itens(cls, v):
        if not v:
            raise ValueError("NFC-e deve ter pelo menos 1 item")
        return v


class NFCeConsultaRequest(BaseModel):
    """Request para consulta de NFC-e."""
    chave_acesso: str = Field(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da NFC-e (44 digitos)"
    )


class NFCeCancelamentoRequest(BaseModel):
    """Request para cancelamento de NFC-e."""
    chave_acesso: str = Field(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da NFC-e"
    )
    justificativa: str = Field(
        ...,
        min_length=15,
        max_length=255,
        description="Justificativa do cancelamento (min 15 caracteres)"
    )


class NFCeInutilizacaoRequest(BaseModel):
    """Request para inutilizacao de numeracao."""
    serie: int = Field(..., ge=1, le=999, description="Serie")
    numero_inicial: int = Field(..., ge=1, description="Numero inicial")
    numero_final: int = Field(..., ge=1, description="Numero final")
    justificativa: str = Field(
        ...,
        min_length=15,
        max_length=255,
        description="Justificativa da inutilizacao"
    )

    @field_validator('numero_final')
    @classmethod
    def validate_numeros(cls, v, info):
        if 'numero_inicial' in info.data and v < info.data['numero_inicial']:
            raise ValueError("Numero final deve ser maior ou igual ao inicial")
        return v


class NFCeContingenciaRequest(BaseModel):
    """Request para transmitir NFC-e em contingencia."""
    xml_contingencia: str = Field(..., description="XML da NFC-e emitida em contingencia")
    motivo_contingencia: str = Field(
        ...,
        min_length=15,
        max_length=255,
        description="Motivo da contingencia"
    )
    data_contingencia: str = Field(..., description="Data/hora entrada em contingencia (ISO8601)")


class NFCeResponse(BaseModel):
    """Response padrao de operacoes NFC-e."""
    sucesso: bool = Field(..., description="Indica sucesso da operacao")
    codigo: str = Field(..., description="Codigo de retorno")
    mensagem: str = Field(..., description="Mensagem de retorno")

    # Dados da NFC-e (quando aplicavel)
    chave_acesso: Optional[str] = Field(None, description="Chave de acesso")
    protocolo: Optional[str] = Field(None, description="Protocolo de autorizacao")
    numero: Optional[int] = Field(None, description="Numero da NFC-e")
    serie: Optional[int] = Field(None, description="Serie da NFC-e")

    # QR Code
    qrcode_url: Optional[str] = Field(None, description="URL do QR Code")
    url_consulta: Optional[str] = Field(None, description="URL de consulta pela chave")

    # XML
    xml: Optional[str] = Field(None, description="XML autorizado")

    # Dados adicionais
    data_autorizacao: Optional[str] = Field(None, description="Data/hora autorizacao")
    valor_total: Optional[Decimal] = Field(None, description="Valor total da NFC-e")


class NFCeStatusServicoResponse(BaseModel):
    """Response de status do servico NFC-e."""
    online: bool = Field(..., description="Servico online")
    codigo: str = Field(..., description="Codigo de status")
    mensagem: str = Field(..., description="Mensagem de status")
    tempo_medio: Optional[int] = Field(None, description="Tempo medio de resposta (ms)")
    data_consulta: str = Field(..., description="Data/hora da consulta")


class NFCeDANFERequest(BaseModel):
    """Request para geracao de DANFE NFC-e."""
    chave_acesso: str = Field(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da NFC-e"
    )
    formato: str = Field(
        default="pdf",
        pattern=r"^(pdf|html|escpos)$",
        description="Formato de saida (pdf, html, escpos)"
    )


class NFCeResumoResponse(BaseModel):
    """Resumo de NFC-e para listagem."""
    chave_acesso: str
    numero: int
    serie: int
    data_emissao: str
    valor_total: Decimal
    status: str
    consumidor_cpf: Optional[str] = None
    consumidor_nome: Optional[str] = None
