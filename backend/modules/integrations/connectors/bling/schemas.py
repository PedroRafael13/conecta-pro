"""
Schemas Pydantic para API Bling v3
Sprint 33: Integration Framework

Baseado na documentação: https://developer.bling.com.br/
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==================== CONTATOS ====================


class BlingEndereco(BaseModel):
    """Endereço no Bling."""

    endereco: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    municipio: str | None = None
    uf: str | None = None
    pais: str | None = None

    model_config = ConfigDict(extra="allow")


class BlingContato(BaseModel):
    """Contato (cliente/fornecedor) no Bling."""

    id: int | None = None
    nome: str
    codigo: str | None = None
    situacao: str | None = None  # A (Ativo), E (Excluído), I (Inativo)
    numeroDocumento: str | None = None  # noqa: N815  # CPF/CNPJ
    ie: str | None = None  # Inscrição Estadual
    rg: str | None = None
    orgaoEmissor: str | None = None  # noqa: N815
    email: str | None = None
    telefone: str | None = None
    celular: str | None = None
    fax: str | None = None
    endereco: BlingEndereco | None = None
    tipoContato: str | None = None  # noqa: N815  # F (Física), J (Jurídica)
    contribuinte: int | None = None  # 1, 2, 9
    limiteCredito: Decimal | None = None  # noqa: N815
    vendedor: dict | None = None
    dadosAdicionais: dict | None = None  # noqa: N815
    dataAlteracao: datetime | None = None  # noqa: N815
    dataCriacao: datetime | None = None  # noqa: N815

    model_config = ConfigDict(extra="allow")


class BlingContatoCreate(BaseModel):
    """Schema para criar contato no Bling."""

    nome: str = Field(..., min_length=1, max_length=120)
    codigo: str | None = Field(None, max_length=50)
    situacao: str = Field(default="A")
    numeroDocumento: str | None = None  # noqa: N815
    ie: str | None = None
    email: str | None = None
    telefone: str | None = None
    celular: str | None = None
    endereco: BlingEndereco | None = None
    tipoContato: str = Field(default="J")  # noqa: N815  # J = Jurídica

    model_config = ConfigDict(extra="allow")


# ==================== PRODUTOS ====================


class BlingProduto(BaseModel):
    """Produto no Bling."""

    id: int | None = None
    nome: str
    codigo: str | None = None  # SKU
    preco: Decimal | None = None
    precoCusto: Decimal | None = None  # noqa: N815
    tipo: str | None = None  # P (Produto), S (Serviço)
    situacao: str | None = None  # A (Ativo), I (Inativo)
    formato: str | None = None  # S (Simples), V (Variação), E (Com composição)
    descricaoCurta: str | None = None  # noqa: N815
    descricaoComplementar: str | None = None  # noqa: N815
    unidade: str | None = None
    pesoLiquido: Decimal | None = None  # noqa: N815
    pesoBruto: Decimal | None = None  # noqa: N815
    largura: Decimal | None = None
    altura: Decimal | None = None
    profundidade: Decimal | None = None
    volumes: int | None = None
    itensPorCaixa: int | None = None  # noqa: N815
    gtin: str | None = None  # EAN/GTIN
    gtinEmbalagem: str | None = None  # noqa: N815
    tipoProducao: str | None = None  # noqa: N815
    condicao: int | None = None  # 0 (Não especificado), 1 (Novo), 2 (Usado)
    freteGratis: bool | None = None  # noqa: N815
    marca: str | None = None
    categoria: dict | None = None
    estoque: dict | None = None
    tributacao: dict | None = None
    midia: dict | None = None
    dataAlteracao: datetime | None = None  # noqa: N815
    dataCriacao: datetime | None = None  # noqa: N815

    model_config = ConfigDict(extra="allow")


class BlingProdutoCreate(BaseModel):
    """Schema para criar produto no Bling."""

    nome: str = Field(..., min_length=1, max_length=120)
    codigo: str | None = Field(None, max_length=120)  # SKU
    preco: Decimal = Field(..., ge=0)
    tipo: str = Field(default="P")  # P = Produto
    situacao: str = Field(default="A")  # A = Ativo
    formato: str = Field(default="S")  # S = Simples
    unidade: str | None = Field(default="UN")
    gtin: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== ESTOQUE ====================


class BlingEstoqueSaldo(BaseModel):
    """Saldo de estoque no Bling."""

    produto: dict | None = None
    deposito: dict | None = None
    saldoFisico: Decimal | None = None  # noqa: N815
    saldoVirtual: Decimal | None = None  # noqa: N815

    model_config = ConfigDict(extra="allow")


# ==================== PEDIDOS ====================


class BlingPedidoItem(BaseModel):
    """Item de pedido no Bling."""

    id: int | None = None
    codigo: str | None = None
    unidade: str | None = None
    quantidade: Decimal | None = None
    desconto: Decimal | None = None
    valor: Decimal | None = None
    aliquotaIPI: Decimal | None = None  # noqa: N815
    descricao: str | None = None
    produto: dict | None = None

    model_config = ConfigDict(extra="allow")


class BlingPedido(BaseModel):
    """Pedido de venda no Bling."""

    id: int | None = None
    numero: int | None = None
    numeroLoja: str | None = None  # noqa: N815
    data: date | None = None
    dataSaida: date | None = None  # noqa: N815
    dataPrevista: date | None = None  # noqa: N815
    contato: dict | None = None
    situacao: dict | None = None  # id, valor (ex: "Em aberto", "Atendido")
    itens: list[BlingPedidoItem] | None = None
    parcelas: list[dict] | None = None
    transporte: dict | None = None
    vendedor: dict | None = None
    desconto: dict | None = None
    observacoes: str | None = None
    observacoesInternas: str | None = None  # noqa: N815
    totalProdutos: Decimal | None = None  # noqa: N815
    total: Decimal | None = None
    dataAlteracao: datetime | None = None  # noqa: N815
    dataCriacao: datetime | None = None  # noqa: N815

    model_config = ConfigDict(extra="allow")


# ==================== NOTAS FISCAIS ====================


class BlingNFe(BaseModel):
    """Nota Fiscal Eletrônica no Bling."""

    id: int | None = None
    tipo: int | None = None  # 0 (Entrada), 1 (Saída)
    situacao: int | None = None  # 1-9
    numero: str | None = None
    serie: str | None = None
    dataEmissao: date | None = None  # noqa: N815
    dataOperacao: date | None = None  # noqa: N815
    contato: dict | None = None
    naturezaOperacao: dict | None = None  # noqa: N815
    loja: dict | None = None
    valorNota: Decimal | None = None  # noqa: N815
    chaveAcesso: str | None = None  # noqa: N815
    xml: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== RESPONSES ====================


class BlingPaginatedResponse(BaseModel):
    """Resposta paginada do Bling."""

    data: list[Any] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class BlingSingleResponse(BaseModel):
    """Resposta de item único do Bling."""

    data: dict | None = None

    model_config = ConfigDict(extra="allow")


class BlingErrorResponse(BaseModel):
    """Resposta de erro do Bling."""

    error: dict | None = None

    model_config = ConfigDict(extra="allow")
