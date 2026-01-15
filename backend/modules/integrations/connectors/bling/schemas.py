"""
Schemas Pydantic para API Bling v3
Sprint 33: Integration Framework

Baseado na documentação: https://developer.bling.com.br/
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ==================== CONTATOS ====================

class BlingEndereco(BaseModel):
    """Endereço no Bling."""
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    pais: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class BlingContato(BaseModel):
    """Contato (cliente/fornecedor) no Bling."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    situacao: Optional[str] = None  # A (Ativo), E (Excluído), I (Inativo)
    numeroDocumento: Optional[str] = None  # CPF/CNPJ
    ie: Optional[str] = None  # Inscrição Estadual
    rg: Optional[str] = None
    orgaoEmissor: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    fax: Optional[str] = None
    endereco: Optional[BlingEndereco] = None
    tipoContato: Optional[str] = None  # F (Física), J (Jurídica)
    contribuinte: Optional[int] = None  # 1, 2, 9
    limiteCredito: Optional[Decimal] = None
    vendedor: Optional[dict] = None
    dadosAdicionais: Optional[dict] = None
    dataAlteracao: Optional[datetime] = None
    dataCriacao: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class BlingContatoCreate(BaseModel):
    """Schema para criar contato no Bling."""
    nome: str = Field(..., min_length=1, max_length=120)
    codigo: Optional[str] = Field(None, max_length=50)
    situacao: str = Field(default="A")
    numeroDocumento: Optional[str] = None
    ie: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    endereco: Optional[BlingEndereco] = None
    tipoContato: str = Field(default="J")  # J = Jurídica

    model_config = ConfigDict(extra="allow")


# ==================== PRODUTOS ====================

class BlingProduto(BaseModel):
    """Produto no Bling."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None  # SKU
    preco: Optional[Decimal] = None
    precoCusto: Optional[Decimal] = None
    tipo: Optional[str] = None  # P (Produto), S (Serviço)
    situacao: Optional[str] = None  # A (Ativo), I (Inativo)
    formato: Optional[str] = None  # S (Simples), V (Variação), E (Com composição)
    descricaoCurta: Optional[str] = None
    descricaoComplementar: Optional[str] = None
    unidade: Optional[str] = None
    pesoLiquido: Optional[Decimal] = None
    pesoBruto: Optional[Decimal] = None
    largura: Optional[Decimal] = None
    altura: Optional[Decimal] = None
    profundidade: Optional[Decimal] = None
    volumes: Optional[int] = None
    itensPorCaixa: Optional[int] = None
    gtin: Optional[str] = None  # EAN/GTIN
    gtinEmbalagem: Optional[str] = None
    tipoProducao: Optional[str] = None
    condicao: Optional[int] = None  # 0 (Não especificado), 1 (Novo), 2 (Usado)
    freteGratis: Optional[bool] = None
    marca: Optional[str] = None
    categoria: Optional[dict] = None
    estoque: Optional[dict] = None
    tributacao: Optional[dict] = None
    midia: Optional[dict] = None
    dataAlteracao: Optional[datetime] = None
    dataCriacao: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class BlingProdutoCreate(BaseModel):
    """Schema para criar produto no Bling."""
    nome: str = Field(..., min_length=1, max_length=120)
    codigo: Optional[str] = Field(None, max_length=120)  # SKU
    preco: Decimal = Field(..., ge=0)
    tipo: str = Field(default="P")  # P = Produto
    situacao: str = Field(default="A")  # A = Ativo
    formato: str = Field(default="S")  # S = Simples
    unidade: Optional[str] = Field(default="UN")
    gtin: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== ESTOQUE ====================

class BlingEstoqueSaldo(BaseModel):
    """Saldo de estoque no Bling."""
    produto: Optional[dict] = None
    deposito: Optional[dict] = None
    saldoFisico: Optional[Decimal] = None
    saldoVirtual: Optional[Decimal] = None

    model_config = ConfigDict(extra="allow")


# ==================== PEDIDOS ====================

class BlingPedidoItem(BaseModel):
    """Item de pedido no Bling."""
    id: Optional[int] = None
    codigo: Optional[str] = None
    unidade: Optional[str] = None
    quantidade: Optional[Decimal] = None
    desconto: Optional[Decimal] = None
    valor: Optional[Decimal] = None
    aliquotaIPI: Optional[Decimal] = None
    descricao: Optional[str] = None
    produto: Optional[dict] = None

    model_config = ConfigDict(extra="allow")


class BlingPedido(BaseModel):
    """Pedido de venda no Bling."""
    id: Optional[int] = None
    numero: Optional[int] = None
    numeroLoja: Optional[str] = None
    data: Optional[date] = None
    dataSaida: Optional[date] = None
    dataPrevista: Optional[date] = None
    contato: Optional[dict] = None
    situacao: Optional[dict] = None  # id, valor (ex: "Em aberto", "Atendido")
    itens: Optional[List[BlingPedidoItem]] = None
    parcelas: Optional[List[dict]] = None
    transporte: Optional[dict] = None
    vendedor: Optional[dict] = None
    desconto: Optional[dict] = None
    observacoes: Optional[str] = None
    observacoesInternas: Optional[str] = None
    totalProdutos: Optional[Decimal] = None
    total: Optional[Decimal] = None
    dataAlteracao: Optional[datetime] = None
    dataCriacao: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== NOTAS FISCAIS ====================

class BlingNFe(BaseModel):
    """Nota Fiscal Eletrônica no Bling."""
    id: Optional[int] = None
    tipo: Optional[int] = None  # 0 (Entrada), 1 (Saída)
    situacao: Optional[int] = None  # 1-9
    numero: Optional[str] = None
    serie: Optional[str] = None
    dataEmissao: Optional[date] = None
    dataOperacao: Optional[date] = None
    contato: Optional[dict] = None
    naturezaOperacao: Optional[dict] = None
    loja: Optional[dict] = None
    valorNota: Optional[Decimal] = None
    chaveAcesso: Optional[str] = None
    xml: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== RESPONSES ====================

class BlingPaginatedResponse(BaseModel):
    """Resposta paginada do Bling."""
    data: List[Any] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class BlingSingleResponse(BaseModel):
    """Resposta de item único do Bling."""
    data: Optional[dict] = None

    model_config = ConfigDict(extra="allow")


class BlingErrorResponse(BaseModel):
    """Resposta de erro do Bling."""
    error: Optional[dict] = None

    model_config = ConfigDict(extra="allow")
