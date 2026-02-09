"""
Mappers para Bling ERP
Sprint 33: Integration Framework

Mapeamento bidirecional entre entidades Bling API v3 e modelos internos Conecta PRO.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from modules.integrations.connectors.bling.schemas import (
    BlingContatoCreate,
    BlingEndereco,
    BlingProdutoCreate,
)

logger = logging.getLogger(__name__)


class BlingMapperError(Exception):
    """Erro no mapeamento de entidades Bling."""

    pass


# ==================== CONTATO → CUSTOMER/SUPPLIER ====================


def bling_contato_to_customer(
    bling_data: dict[str, Any], condominio_id: UUID, defaults: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Mapeia contato Bling para dados de Customer interno.

    Args:
        bling_data: Dados do contato do Bling
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados para criar/atualizar Customer
    """
    defaults = defaults or {}
    endereco = bling_data.get("endereco") or {}

    # Determinar tipo baseado em tipoContato
    tipo_contato = bling_data.get("tipoContato", "J")
    customer_type = "empresa" if tipo_contato == "J" else "externo"

    # Determinar status baseado em situacao
    situacao = bling_data.get("situacao", "A")
    status_map = {
        "A": "ativo",
        "I": "inativo",
        "E": "inativo",  # Excluído = inativo
    }
    status = status_map.get(situacao, "ativo")

    return {
        "condominio_id": condominio_id,
        "cpf_cnpj": _clean_document(bling_data.get("numeroDocumento")),
        "name": bling_data.get("nome", ""),
        "trade_name": bling_data.get("codigo"),  # Código como nome fantasia
        "customer_type": customer_type,
        "status": status,
        "email": bling_data.get("email"),
        "phone": bling_data.get("telefone"),
        "whatsapp": bling_data.get("celular"),
        "address_street": endereco.get("endereco"),
        "address_number": endereco.get("numero"),
        "address_complement": endereco.get("complemento"),
        "address_neighborhood": endereco.get("bairro"),
        "address_city": endereco.get("municipio"),
        "address_state": endereco.get("uf"),
        "address_zipcode": _clean_cep(endereco.get("cep")),
        "credit_limit": bling_data.get("limiteCredito", Decimal("0")),
        "extra_data": {
            "bling_id": bling_data.get("id"),
            "bling_codigo": bling_data.get("codigo"),
            "ie": bling_data.get("ie"),
            "rg": bling_data.get("rg"),
            "contribuinte": bling_data.get("contribuinte"),
        },
        "ativo": situacao == "A",
        **defaults,
    }


def bling_contato_to_supplier(
    bling_data: dict[str, Any], condominio_id: UUID, defaults: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Mapeia contato Bling para dados de Supplier interno.

    Args:
        bling_data: Dados do contato do Bling
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados para criar/atualizar Supplier
    """
    defaults = defaults or {}
    endereco = bling_data.get("endereco") or {}

    # Determinar tipo baseado em tipoContato
    tipo_contato = bling_data.get("tipoContato", "J")
    supplier_type = "pessoa_juridica" if tipo_contato == "J" else "pessoa_fisica"

    # Determinar status baseado em situacao
    situacao = bling_data.get("situacao", "A")
    status_map = {
        "A": "ativo",
        "I": "inativo",
        "E": "inativo",
    }
    status = status_map.get(situacao, "ativo")

    return {
        "condominio_id": condominio_id,
        "code": bling_data.get("codigo"),
        "name": bling_data.get("nome", ""),
        "trade_name": None,
        "supplier_type": supplier_type,
        "status": status,
        "cpf_cnpj": _clean_document(bling_data.get("numeroDocumento")),
        "state_registration": bling_data.get("ie"),
        "email": bling_data.get("email"),
        "phone": bling_data.get("telefone"),
        "mobile": bling_data.get("celular"),
        "whatsapp": bling_data.get("celular"),
        "address_street": endereco.get("endereco"),
        "address_number": endereco.get("numero"),
        "address_complement": endereco.get("complemento"),
        "address_neighborhood": endereco.get("bairro"),
        "address_city": endereco.get("municipio"),
        "address_state": endereco.get("uf"),
        "address_zip": _clean_cep(endereco.get("cep")),
        "ativo": situacao == "A",
        **defaults,
    }


def customer_to_bling_contato(customer_data: dict[str, Any]) -> BlingContatoCreate:
    """
    Mapeia Customer interno para dados de criação no Bling.

    Args:
        customer_data: Dados do Customer

    Returns:
        BlingContatoCreate schema
    """
    endereco = None
    if customer_data.get("address_street"):
        endereco = BlingEndereco(
            endereco=customer_data.get("address_street"),
            numero=customer_data.get("address_number"),
            complemento=customer_data.get("address_complement"),
            bairro=customer_data.get("address_neighborhood"),
            municipio=customer_data.get("address_city"),
            uf=customer_data.get("address_state"),
            cep=customer_data.get("address_zipcode"),
        )

    # Determinar tipo
    tipo = "J" if customer_data.get("customer_type") == "empresa" else "F"

    return BlingContatoCreate(
        nome=customer_data.get("name", ""),
        codigo=customer_data.get("trade_name"),
        situacao="A" if customer_data.get("ativo", True) else "I",
        numeroDocumento=customer_data.get("cpf_cnpj"),
        email=customer_data.get("email"),
        telefone=customer_data.get("phone"),
        celular=customer_data.get("whatsapp"),
        endereco=endereco,
        tipoContato=tipo,
    )


def supplier_to_bling_contato(supplier_data: dict[str, Any]) -> BlingContatoCreate:
    """
    Mapeia Supplier interno para dados de criação no Bling.

    Args:
        supplier_data: Dados do Supplier

    Returns:
        BlingContatoCreate schema
    """
    endereco = None
    if supplier_data.get("address_street"):
        endereco = BlingEndereco(
            endereco=supplier_data.get("address_street"),
            numero=supplier_data.get("address_number"),
            complemento=supplier_data.get("address_complement"),
            bairro=supplier_data.get("address_neighborhood"),
            municipio=supplier_data.get("address_city"),
            uf=supplier_data.get("address_state"),
            cep=supplier_data.get("address_zip"),
        )

    # Determinar tipo
    tipo = "J" if supplier_data.get("supplier_type") in ["pessoa_juridica", "mei", "eireli", "cooperativa"] else "F"

    return BlingContatoCreate(
        nome=supplier_data.get("name", ""),
        codigo=supplier_data.get("code"),
        situacao="A" if supplier_data.get("ativo", True) else "I",
        numeroDocumento=supplier_data.get("cpf_cnpj"),
        ie=supplier_data.get("state_registration"),
        email=supplier_data.get("email"),
        telefone=supplier_data.get("phone"),
        celular=supplier_data.get("mobile") or supplier_data.get("whatsapp"),
        endereco=endereco,
        tipoContato=tipo,
    )


# ==================== PRODUTO ====================


def bling_produto_to_product(
    bling_data: dict[str, Any], condominio_id: UUID, defaults: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Mapeia produto Bling para dados de Product interno.

    Args:
        bling_data: Dados do produto do Bling
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados para criar/atualizar Product
    """
    defaults = defaults or {}

    # Mapear tipo
    tipo_bling = bling_data.get("tipo", "P")
    product_type = "servico" if tipo_bling == "S" else "produto"

    # Mapear status
    situacao = bling_data.get("situacao", "A")
    status_map = {
        "A": "ativo",
        "I": "inativo",
    }
    status = status_map.get(situacao, "ativo")

    # Mapear unidade
    unidade = bling_data.get("unidade", "UN")
    unit_map = {
        "UN": "un",
        "PC": "pc",
        "CX": "cx",
        "KG": "kg",
        "G": "g",
        "L": "l",
        "ML": "ml",
        "M": "m",
        "M2": "m2",
        "M3": "m3",
        "HR": "hr",
        "DIA": "dia",
        "MES": "mes",
        "SV": "sv",
    }
    unit = unit_map.get(unidade.upper() if unidade else "UN", "un")

    return {
        "condominio_id": condominio_id,
        "code": bling_data.get("codigo"),  # SKU
        "barcode": bling_data.get("gtin"),  # EAN/GTIN
        "name": bling_data.get("nome", ""),
        "description": bling_data.get("descricaoComplementar") or bling_data.get("descricaoCurta"),
        "product_type": product_type,
        "status": status,
        "unit_of_measure": unit,
        "reference_price": bling_data.get("preco"),
        "last_purchase_price": bling_data.get("precoCusto"),
        "ncm": None,  # Bling não retorna NCM diretamente na listagem
        "brand": bling_data.get("marca"),
        "attributes": {
            "bling_id": bling_data.get("id"),
            "formato": bling_data.get("formato"),
            "peso_liquido": str(bling_data.get("pesoLiquido")) if bling_data.get("pesoLiquido") else None,
            "peso_bruto": str(bling_data.get("pesoBruto")) if bling_data.get("pesoBruto") else None,
            "largura": str(bling_data.get("largura")) if bling_data.get("largura") else None,
            "altura": str(bling_data.get("altura")) if bling_data.get("altura") else None,
            "profundidade": str(bling_data.get("profundidade")) if bling_data.get("profundidade") else None,
        },
        "ativo": situacao == "A",
        **defaults,
    }


def product_to_bling_produto(product_data: dict[str, Any]) -> BlingProdutoCreate:
    """
    Mapeia Product interno para dados de criação no Bling.

    Args:
        product_data: Dados do Product

    Returns:
        BlingProdutoCreate schema
    """
    # Mapear tipo
    tipo = "S" if product_data.get("product_type") == "servico" else "P"

    # Mapear unidade
    unit_map = {
        "un": "UN",
        "pc": "PC",
        "cx": "CX",
        "kg": "KG",
        "g": "G",
        "l": "L",
        "ml": "ML",
        "m": "M",
        "m2": "M2",
        "m3": "M3",
        "hr": "HR",
        "dia": "DIA",
        "mes": "MES",
        "sv": "SV",
    }
    unidade = unit_map.get(product_data.get("unit_of_measure", "un"), "UN")

    return BlingProdutoCreate(
        nome=product_data.get("name", ""),
        codigo=product_data.get("code"),
        preco=product_data.get("reference_price") or Decimal("0"),
        tipo=tipo,
        situacao="A" if product_data.get("ativo", True) else "I",
        formato="S",  # Simples
        unidade=unidade,
        gtin=product_data.get("barcode"),
    )


# ==================== NFE ====================


def bling_nfe_to_nfe(
    bling_data: dict[str, Any], condominio_id: UUID, defaults: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Mapeia NFe Bling para dados de NFe interno.

    Args:
        bling_data: Dados da NFe do Bling
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados para criar/atualizar NFe
    """
    defaults = defaults or {}

    # Mapear tipo
    tipo_bling = bling_data.get("tipo", 1)
    tipo = "0" if tipo_bling == 0 else "1"  # 0=Entrada, 1=Saída

    # Mapear status
    situacao_bling = bling_data.get("situacao", 1)
    status_map = {
        1: "rascunho",
        2: "pendente_envio",
        3: "enviada",
        4: "rejeitada",
        5: "autorizada",
        6: "cancelada",
        7: "denegada",
        8: "inutilizada",
        9: "contingencia",
    }
    status = status_map.get(situacao_bling, "rascunho")

    # Extrair dados do contato/destinatário
    contato = bling_data.get("contato") or {}

    return {
        "condominio_id": condominio_id,
        "chave_acesso": bling_data.get("chaveAcesso"),
        "numero": int(bling_data.get("numero")) if bling_data.get("numero") else None,
        "serie": bling_data.get("serie") or "1",
        "tipo": tipo,
        "status": status,
        "data_emissao": _parse_date(bling_data.get("dataEmissao")),
        "data_saida_entrada": _parse_date(bling_data.get("dataOperacao")),
        "destinatario_cpf_cnpj": contato.get("numeroDocumento"),
        "destinatario_razao_social": contato.get("nome"),
        "valor_total": bling_data.get("valorNota"),
        "xml_retorno": bling_data.get("xml"),
        "active": True,
        **defaults,
    }


# ==================== PEDIDO ====================


def bling_pedido_to_order(
    bling_data: dict[str, Any], condominio_id: UUID, defaults: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Mapeia Pedido Bling para dados de pedido interno.

    Args:
        bling_data: Dados do pedido do Bling
        condominio_id: ID do condomínio
        defaults: Valores padrão adicionais

    Returns:
        Dict com dados do pedido
    """
    defaults = defaults or {}

    # Mapear status
    situacao = bling_data.get("situacao") or {}
    situacao_valor = situacao.get("valor", "Em aberto")

    status_map = {
        "Em aberto": "aberto",
        "Atendido": "atendido",
        "Cancelado": "cancelado",
        "Em andamento": "em_andamento",
        "Venda Agenciada": "agenciada",
        "Verificado": "verificado",
    }
    status = status_map.get(situacao_valor, "aberto")

    # Extrair dados do contato
    contato = bling_data.get("contato") or {}

    # Extrair itens
    itens = []
    for item_bling in bling_data.get("itens") or []:
        produto = item_bling.get("produto") or {}
        itens.append(
            {
                "produto_id": produto.get("id"),
                "produto_codigo": item_bling.get("codigo"),
                "descricao": item_bling.get("descricao"),
                "quantidade": item_bling.get("quantidade"),
                "valor_unitario": item_bling.get("valor"),
                "desconto": item_bling.get("desconto"),
                "unidade": item_bling.get("unidade"),
            }
        )

    return {
        "condominio_id": condominio_id,
        "numero": bling_data.get("numero"),
        "numero_loja": bling_data.get("numeroLoja"),
        "data": _parse_date(bling_data.get("data")),
        "data_prevista": _parse_date(bling_data.get("dataPrevista")),
        "status": status,
        "cliente_id_externo": contato.get("id"),
        "cliente_nome": contato.get("nome"),
        "cliente_documento": contato.get("numeroDocumento"),
        "itens": itens,
        "valor_produtos": bling_data.get("totalProdutos"),
        "valor_total": bling_data.get("total"),
        "observacoes": bling_data.get("observacoes"),
        "observacoes_internas": bling_data.get("observacoesInternas"),
        "extra_data": {
            "bling_id": bling_data.get("id"),
            "vendedor": bling_data.get("vendedor"),
            "transporte": bling_data.get("transporte"),
            "parcelas": bling_data.get("parcelas"),
        },
        **defaults,
    }


# ==================== HELPERS ====================


def _clean_document(doc: str | None) -> str | None:
    """Remove formatação de CPF/CNPJ."""
    if not doc:
        return None
    return doc.replace(".", "").replace("-", "").replace("/", "").strip()


def _clean_cep(cep: str | None) -> str | None:
    """Remove formatação de CEP."""
    if not cep:
        return None
    return cep.replace("-", "").replace(".", "").strip()


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse de data do Bling."""
    if not date_str:
        return None

    # Formatos possíveis do Bling
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str[:26], fmt)
        except (ValueError, TypeError):
            continue

    logger.warning(f"Não foi possível parsear data: {date_str}")
    return None


def _parse_decimal(value: Any) -> Decimal | None:
    """Parse de valor decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


# ==================== DATA HASH ====================


def compute_bling_entity_hash(entity_type: str, data: dict[str, Any]) -> str:
    """
    Computa hash de dados da entidade para detectar mudanças.

    Args:
        entity_type: Tipo da entidade
        data: Dados da entidade

    Returns:
        Hash MD5 dos dados relevantes
    """
    import hashlib
    import json

    # Campos relevantes por tipo de entidade
    hash_fields = {
        "contatos": ["nome", "numeroDocumento", "email", "telefone", "situacao", "endereco"],
        "produtos": ["nome", "codigo", "preco", "situacao", "tipo", "gtin"],
        "pedidos": ["numero", "data", "situacao", "total", "itens"],
        "notas": ["numero", "serie", "situacao", "chaveAcesso", "valorNota"],
    }

    fields = hash_fields.get(entity_type, list(data.keys()))

    # Extrair apenas campos relevantes
    hash_data = {k: data.get(k) for k in fields if k in data}

    # Serializar e computar hash
    json_str = json.dumps(hash_data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()
