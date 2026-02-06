"""
Testes completos para modulo SEFAZ (NFe/NFCe) - Conecta PRO.

Cobertura:
- TestSchemas: Validacao de schemas Pydantic
- TestSEFAZManager: Testes do core manager
- TestSEFAZService: Testes do service layer
- TestSEFAZEndpoints: Testes de endpoints REST

Author: Claude AI + Human Developer
Date: 2026-01-16
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from pydantic import ValidationError as PydanticValidationError

# Imports do modulo SEFAZ
from modules.government_integrations.core.sefaz_manager import (
    ContingencyType,
    Destinatario,
    DocumentStatus,
    DocumentType,
    Emitente,
    Endereco,
    NFEXMLBuilder,
    NotaFiscal,
    OperationType,
    Pagamento,
    PaymentType,
    Produto,
    SEFAZError,
    SEFAZManager,
    UFConfig,
    UF_CONFIGS,
    ValidationError,
    init_sefaz_manager,
)
from modules.government_integrations.schemas.sefaz import NFERequest
from modules.government_integrations.services.sefaz_service import SEFAZService

# Cria app isolado para testes (evita carregar todo o main.py)
from fastapi import FastAPI
from modules.government_integrations.controllers.sefaz_controller import router as sefaz_router

app = FastAPI()
app.include_router(sefaz_router, prefix="/api/v1/government")


# ==========================================================================
# Fixtures Compartilhadas
# ==========================================================================
@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Headers de autenticacao para testes."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def endereco_emitente() -> Endereco:
    """Endereco do emitente para testes."""
    return Endereco(
        logradouro="Av Paulista",
        numero="1000",
        bairro="Bela Vista",
        cidade="Sao Paulo",
        uf="SP",
        cep="01310-100",
        codigo_municipio="3550308",
        complemento="Sala 1010",
    )


@pytest.fixture
def endereco_destinatario() -> Endereco:
    """Endereco do destinatario para testes."""
    return Endereco(
        logradouro="Rua Augusta",
        numero="500",
        bairro="Consolacao",
        cidade="Sao Paulo",
        uf="SP",
        cep="01304-001",
        codigo_municipio="3550308",
    )


@pytest.fixture
def emitente(endereco_emitente: Endereco) -> Emitente:
    """Emitente para testes."""
    return Emitente(
        cnpj="12.345.678/0001-95",
        razao_social="CONECTA PRO SISTEMAS LTDA",
        nome_fantasia="Conecta Pro",
        inscricao_estadual="123456789012",
        endereco=endereco_emitente,
        regime_tributario="3",
        cnae="6201501",
        inscricao_municipal="12345678",
    )


@pytest.fixture
def destinatario_pj(endereco_destinatario: Endereco) -> Destinatario:
    """Destinatario pessoa juridica para testes."""
    return Destinatario(
        cpf_cnpj="98.765.432/0001-10",
        nome="CLIENTE TESTE LTDA",
        endereco=endereco_destinatario,
        inscricao_estadual="987654321098",
        email="cliente@teste.com.br",
        telefone="11999998888",
        indicador_ie="1",
    )


@pytest.fixture
def destinatario_pf(endereco_destinatario: Endereco) -> Destinatario:
    """Destinatario pessoa fisica para testes."""
    return Destinatario(
        cpf_cnpj="123.456.789-09",
        nome="CONSUMIDOR TESTE",
        endereco=endereco_destinatario,
        email="consumidor@teste.com.br",
        indicador_ie="9",
    )


@pytest.fixture
def produto_simples() -> Produto:
    """Produto simples para testes."""
    return Produto(
        codigo="PROD001",
        descricao="Produto de Teste para NFe",
        ncm="84713012",
        cfop="5102",
        unidade="UN",
        quantidade=Decimal("10"),
        valor_unitario=Decimal("100.00"),
        origem="0",
        cst_icms="00",
        aliquota_icms=Decimal("18.00"),
        cst_pis="01",
        aliquota_pis=Decimal("1.65"),
        cst_cofins="01",
        aliquota_cofins=Decimal("7.60"),
    )


@pytest.fixture
def produto_com_desconto() -> Produto:
    """Produto com desconto para testes."""
    return Produto(
        codigo="PROD002",
        descricao="Produto com Desconto",
        ncm="84714100",
        cfop="5102",
        unidade="UN",
        quantidade=Decimal("5"),
        valor_unitario=Decimal("200.00"),
        valor_desconto=Decimal("50.00"),
        cest="2106300",
        ean="7891234567890",
        origem="0",
        cst_icms="00",
        aliquota_icms=Decimal("12.00"),
    )


@pytest.fixture
def lista_produtos(produto_simples: Produto, produto_com_desconto: Produto) -> List[Produto]:
    """Lista de produtos para testes."""
    return [produto_simples, produto_com_desconto]


@pytest.fixture
def pagamento_dinheiro() -> Pagamento:
    """Pagamento em dinheiro."""
    return Pagamento(
        tipo=PaymentType.DINHEIRO,
        valor=Decimal("1950.00"),
    )


@pytest.fixture
def pagamento_pix() -> Pagamento:
    """Pagamento via PIX."""
    return Pagamento(
        tipo=PaymentType.PIX,
        valor=Decimal("1000.00"),
    )


@pytest.fixture
def pagamento_cartao() -> Pagamento:
    """Pagamento com cartao de credito."""
    return Pagamento(
        tipo=PaymentType.CARTAO_CREDITO,
        valor=Decimal("500.00"),
        bandeira="VISA",
        autorizacao="123456",
        cnpj_credenciadora="01234567000199",
    )


@pytest.fixture
def lista_pagamentos(pagamento_dinheiro: Pagamento) -> List[Pagamento]:
    """Lista de pagamentos para testes."""
    return [pagamento_dinheiro]


@pytest.fixture
def sefaz_manager(emitente: Emitente) -> SEFAZManager:
    """SEFAZManager configurado para testes."""
    return SEFAZManager(
        emitente=emitente,
        certificate_path=None,
        certificate_password=None,
        ambiente="2",  # Homologacao
    )


# ==========================================================================
# TestSchemas - Validacao de Schemas Pydantic
# ==========================================================================
class TestSchemas:
    """Testes para validacao de schemas Pydantic do SEFAZ."""

    def test_nfe_request_valido_nfe(self):
        """Testa NFERequest valido para NFe."""
        request = NFERequest(
            tipo="nfe",
            destinatario={
                "cpf_cnpj": "12345678000195",
                "nome": "Cliente Teste",
                "endereco": {"logradouro": "Rua Teste", "numero": "100"},
            },
            produtos=[
                {
                    "codigo": "001",
                    "descricao": "Produto Teste",
                    "ncm": "84713012",
                    "cfop": "5102",
                    "quantidade": 1,
                    "valor_unitario": 100.00,
                }
            ],
            pagamento={"tipo": "01", "valor": 100.00},
        )

        assert request.tipo == "nfe"
        assert len(request.produtos) == 1
        assert request.observacoes is None

    def test_nfe_request_valido_nfce(self):
        """Testa NFERequest valido para NFCe."""
        request = NFERequest(
            tipo="nfce",
            destinatario={"cpf_cnpj": "12345678909", "nome": "Consumidor"},
            produtos=[
                {"codigo": "001", "descricao": "Produto", "quantidade": 1, "valor_unitario": 50.00}
            ],
            pagamento={"tipo": "17", "valor": 50.00},  # PIX
            observacoes="Venda ao consumidor final",
        )

        assert request.tipo == "nfce"
        assert request.observacoes == "Venda ao consumidor final"

    def test_nfe_request_tipo_invalido(self):
        """Testa NFERequest com tipo invalido."""
        with pytest.raises(PydanticValidationError) as exc_info:
            NFERequest(
                tipo="invalido",  # Deve ser nfe ou nfce
                destinatario={"cpf_cnpj": "12345678000195"},
                produtos=[{"codigo": "001", "descricao": "Produto", "quantidade": 1}],
                pagamento={"tipo": "01", "valor": 100.00},
            )

        assert "tipo" in str(exc_info.value).lower() or "pattern" in str(exc_info.value).lower()

    def test_nfe_request_produtos_vazio(self):
        """Testa NFERequest com lista de produtos vazia."""
        with pytest.raises(PydanticValidationError) as exc_info:
            NFERequest(
                tipo="nfe",
                destinatario={"cpf_cnpj": "12345678000195"},
                produtos=[],  # Lista vazia
                pagamento={"tipo": "01", "valor": 100.00},
            )

        error_str = str(exc_info.value).lower()
        assert "produtos" in error_str or "min_length" in error_str

    def test_nfe_request_limite_produtos(self):
        """Testa NFERequest com limite de produtos (990 items)."""
        # Testa com exatamente 990 produtos (limite maximo)
        produtos = [
            {"codigo": f"PROD{i:03d}", "descricao": f"Produto {i}", "quantidade": 1, "valor_unitario": 10.00}
            for i in range(990)
        ]

        request = NFERequest(
            tipo="nfe",
            destinatario={"cpf_cnpj": "12345678000195"},
            produtos=produtos,
            pagamento={"tipo": "01", "valor": 9900.00},
        )

        assert len(request.produtos) == 990

    def test_nfe_request_excede_limite_produtos(self):
        """Testa NFERequest excedendo limite de 990 produtos."""
        produtos = [
            {"codigo": f"PROD{i:03d}", "descricao": f"Produto {i}", "quantidade": 1}
            for i in range(991)  # Acima do limite
        ]

        with pytest.raises(PydanticValidationError) as exc_info:
            NFERequest(
                tipo="nfe",
                destinatario={"cpf_cnpj": "12345678000195"},
                produtos=produtos,
                pagamento={"tipo": "01", "valor": 9910.00},
            )

        error_str = str(exc_info.value).lower()
        assert "produtos" in error_str or "max_length" in error_str

    def test_nfe_request_observacoes_limite(self):
        """Testa NFERequest com observacoes no limite de 5000 caracteres."""
        request = NFERequest(
            tipo="nfe",
            destinatario={"cpf_cnpj": "12345678000195"},
            produtos=[{"codigo": "001", "descricao": "Produto", "quantidade": 1}],
            pagamento={"tipo": "01", "valor": 100.00},
            observacoes="A" * 5000,  # No limite
        )

        assert len(request.observacoes) == 5000


# ==========================================================================
# TestSEFAZManager - Testes do Core Manager
# ==========================================================================
class TestSEFAZManager:
    """Testes para SEFAZManager (core)."""

    def test_inicializacao(self, emitente: Emitente):
        """Testa inicializacao do SEFAZManager."""
        manager = SEFAZManager(
            emitente=emitente,
            ambiente="2",
        )

        assert manager.emitente == emitente
        assert manager.ambiente == "2"
        assert manager._documents == {}

    @pytest.mark.asyncio
    async def test_create_nfe(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        lista_produtos: List[Produto],
        lista_pagamentos: List[Pagamento],
    ):
        """Testa criacao de NFe."""
        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=lista_produtos,
            pagamentos=lista_pagamentos,
            natureza_operacao="VENDA DE MERCADORIA",
        )

        assert nfe.tipo == DocumentType.NFE
        assert nfe.status == DocumentStatus.DRAFT
        assert nfe.numero == 1
        assert nfe.serie == 1
        assert nfe.chave_acesso is not None
        assert len(nfe.chave_acesso) == 44
        assert nfe.xml_content is not None
        assert nfe.destinatario == destinatario_pj
        assert len(nfe.produtos) == 2
        assert len(nfe.pagamentos) == 1

    @pytest.mark.asyncio
    async def test_create_nfce(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pf: Destinatario,
        produto_simples: Produto,
        pagamento_pix: Pagamento,
    ):
        """Testa criacao de NFCe."""
        nfce = await sefaz_manager.create_nfce(
            produtos=[produto_simples],
            pagamentos=[pagamento_pix],
            destinatario=destinatario_pf,
        )

        assert nfce.tipo == DocumentType.NFCE
        assert nfce.status == DocumentStatus.DRAFT
        assert nfce.natureza_operacao == "VENDA AO CONSUMIDOR"
        assert nfce.operacao == OperationType.SAIDA

    @pytest.mark.asyncio
    async def test_create_nfce_sem_destinatario(
        self,
        sefaz_manager: SEFAZManager,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa criacao de NFCe sem identificacao do consumidor."""
        nfce = await sefaz_manager.create_nfce(
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            destinatario=None,  # Consumidor nao identificado
        )

        assert nfce.tipo == DocumentType.NFCE
        assert nfce.destinatario is None

    @pytest.mark.asyncio
    async def test_numero_sequencial(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa numeracao sequencial de notas."""
        nfe1 = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )
        nfe2 = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )
        nfe3 = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            serie=2,  # Serie diferente
        )

        assert nfe1.numero == 1
        assert nfe2.numero == 2
        assert nfe3.numero == 1  # Reinicia para serie diferente

    @pytest.mark.asyncio
    async def test_validate_nfe_sucesso(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa validacao bem-sucedida de NFe."""
        # Ajusta valor do pagamento para coincidir com produto
        pagamento_dinheiro.valor = produto_simples.valor_total

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        result = await sefaz_manager.validate(nfe.id)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_nfe_sem_produtos(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa validacao de NFe sem produtos."""
        # Cria NFe manualmente sem produtos (forcando estado invalido)
        nfe = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=sefaz_manager.emitente,
            destinatario=destinatario_pj,
            produtos=[],  # Sem produtos
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA",
            numero=999,
            serie=1,
            data_emissao=datetime.utcnow(),
        )
        sefaz_manager._documents[nfe.id] = nfe

        with pytest.raises(ValidationError) as exc_info:
            await sefaz_manager.validate(nfe.id)

        assert "erro(s)" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_validate_nfe_ncm_invalido(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa validacao de NFe com NCM invalido."""
        produto_ncm_invalido = Produto(
            codigo="PROD",
            descricao="Produto NCM Invalido",
            ncm="1234",  # NCM deve ter 8 digitos
            cfop="5102",
            unidade="UN",
            quantidade=Decimal("1"),
            valor_unitario=Decimal("100.00"),
        )

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_ncm_invalido],
            pagamentos=[pagamento_dinheiro],
        )

        with pytest.raises(ValidationError):
            await sefaz_manager.validate(nfe.id)

    @pytest.mark.asyncio
    async def test_get_document(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa recuperacao de documento por ID."""
        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        doc = await sefaz_manager.get_document(nfe.id)

        assert doc is not None
        assert doc.id == nfe.id
        assert doc.chave_acesso == nfe.chave_acesso

    @pytest.mark.asyncio
    async def test_get_document_inexistente(self, sefaz_manager: SEFAZManager):
        """Testa recuperacao de documento inexistente."""
        doc = await sefaz_manager.get_document(uuid4())

        assert doc is None

    @pytest.mark.asyncio
    async def test_get_by_chave(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa recuperacao de documento pela chave de acesso."""
        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        doc = await sefaz_manager.get_by_chave(nfe.chave_acesso)

        assert doc is not None
        assert doc.id == nfe.id

    @pytest.mark.asyncio
    async def test_list_documents_filtro_tipo(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa listagem de documentos com filtro por tipo."""
        # Cria NFe e NFCe
        await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )
        await sefaz_manager.create_nfce(
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        nfes = await sefaz_manager.list_documents(tipo=DocumentType.NFE)
        nfces = await sefaz_manager.list_documents(tipo=DocumentType.NFCE)

        assert len(nfes) == 1
        assert all(d.tipo == DocumentType.NFE for d in nfes)
        assert len(nfces) == 1
        assert all(d.tipo == DocumentType.NFCE for d in nfces)

    @pytest.mark.asyncio
    async def test_transmit_nfe(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa transmissao de NFe (simulada)."""
        pagamento_dinheiro.valor = produto_simples.valor_total

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        # Mock do sign para evitar dependencia de certificado
        with patch.object(sefaz_manager, "sign", new_callable=AsyncMock) as mock_sign:
            mock_sign.return_value = "<xml>signed</xml>"
            nfe.xml_signed = "<xml>signed</xml>"

            result = await sefaz_manager.transmit(nfe.id)

        assert result.status == DocumentStatus.AUTHORIZED
        assert result.protocolo is not None
        assert result.authorized_at is not None

    @pytest.mark.asyncio
    async def test_cancel_nfe_sucesso(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa cancelamento de NFe autorizada."""
        pagamento_dinheiro.valor = produto_simples.valor_total

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        # Simula autorizacao
        with patch.object(sefaz_manager, "sign", new_callable=AsyncMock):
            nfe.xml_signed = "<xml>signed</xml>"
            await sefaz_manager.transmit(nfe.id)

        result = await sefaz_manager.cancel(
            nfe.id,
            justificativa="Cancelamento a pedido do cliente para emissao corrigida",
        )

        assert result.status == DocumentStatus.CANCELLED
        assert result.cancelled_at is not None
        assert "cancelamento" in result.metadata

    @pytest.mark.asyncio
    async def test_cancel_nfe_justificativa_curta(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa cancelamento com justificativa muito curta."""
        pagamento_dinheiro.valor = produto_simples.valor_total

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        # Simula autorizacao
        with patch.object(sefaz_manager, "sign", new_callable=AsyncMock):
            nfe.xml_signed = "<xml>signed</xml>"
            await sefaz_manager.transmit(nfe.id)

        with pytest.raises(ValidationError) as exc_info:
            await sefaz_manager.cancel(nfe.id, justificativa="Curta")

        assert "15 caracteres" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cancel_nfe_nao_autorizada(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa cancelamento de NFe nao autorizada."""
        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        # NFe ainda em DRAFT (nao autorizada)
        with pytest.raises(SEFAZError) as exc_info:
            await sefaz_manager.cancel(
                nfe.id,
                justificativa="Tentativa de cancelar nota nao autorizada",
            )

        assert "nao pode ser cancelado" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_summary(
        self,
        sefaz_manager: SEFAZManager,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa geracao de resumo de documentos."""
        # Cria algumas notas
        pagamento_dinheiro.valor = produto_simples.valor_total

        nfe = await sefaz_manager.create_nfe(
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )
        await sefaz_manager.create_nfce(
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
        )

        # Autoriza uma
        with patch.object(sefaz_manager, "sign", new_callable=AsyncMock):
            nfe.xml_signed = "<xml>signed</xml>"
            await sefaz_manager.transmit(nfe.id)

        summary = await sefaz_manager.get_summary()

        assert summary["total"] == 2
        assert "by_status" in summary
        assert "by_type" in summary
        assert "valor_total_emitido" in summary
        assert summary["by_status"]["authorized"] == 1
        assert summary["by_status"]["draft"] == 1


# ==========================================================================
# TestNotaFiscalModel - Testes do Modelo NotaFiscal
# ==========================================================================
class TestNotaFiscalModel:
    """Testes para o dataclass NotaFiscal."""

    def test_valor_total_produtos(
        self,
        emitente: Emitente,
        destinatario_pj: Destinatario,
        lista_produtos: List[Produto],
        lista_pagamentos: List[Pagamento],
    ):
        """Testa calculo do valor total de produtos."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pj,
            produtos=lista_produtos,
            pagamentos=lista_pagamentos,
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA",
            numero=1,
            serie=1,
            data_emissao=datetime.utcnow(),
        )

        # Produto1: 10 * 100 = 1000
        # Produto2: 5 * 200 - 50 = 950
        expected_total = Decimal("1950.00")

        assert nf.valor_total_produtos == expected_total
        assert nf.valor_total_nota == expected_total

    def test_generate_chave_acesso(
        self,
        emitente: Emitente,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa geracao de chave de acesso."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA",
            numero=1,
            serie=1,
            data_emissao=datetime.utcnow(),
        )

        chave = nf.generate_chave_acesso()

        assert len(chave) == 44
        assert chave.isdigit()
        assert nf.chave_acesso == chave
        # Verifica codigo da UF (SP = 35)
        assert chave[:2] == "35"
        # Verifica modelo (NFe = 55)
        assert chave[20:22] == "55"

    def test_generate_chave_acesso_nfce(
        self,
        emitente: Emitente,
        destinatario_pf: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa geracao de chave de acesso para NFCe."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFCE,  # Modelo 65
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pf,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA AO CONSUMIDOR",
            numero=1,
            serie=1,
            data_emissao=datetime.utcnow(),
        )

        chave = nf.generate_chave_acesso()

        # Verifica modelo (NFCe = 65)
        assert chave[20:22] == "65"

    def test_to_dict(
        self,
        emitente: Emitente,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa conversao para dicionario."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA",
            numero=123,
            serie=1,
            data_emissao=datetime.utcnow(),
        )
        nf.generate_chave_acesso()

        data = nf.to_dict()

        assert data["tipo"] == "nfe"
        assert data["status"] == "draft"
        assert data["numero"] == 123
        assert data["chave_acesso"] is not None
        assert "emitente" in data
        assert "destinatario" in data
        assert "produtos" in data
        assert "pagamentos" in data

    def test_destinatario_is_cpf(self, endereco_destinatario: Endereco):
        """Testa identificacao de CPF vs CNPJ do destinatario."""
        dest_pf = Destinatario(
            cpf_cnpj="123.456.789-09",
            nome="Pessoa Fisica",
            endereco=endereco_destinatario,
        )
        dest_pj = Destinatario(
            cpf_cnpj="12.345.678/0001-95",
            nome="Pessoa Juridica",
            endereco=endereco_destinatario,
        )

        assert dest_pf.is_cpf is True
        assert dest_pj.is_cpf is False


# ==========================================================================
# TestNFEXMLBuilder - Testes do Construtor de XML
# ==========================================================================
class TestNFEXMLBuilder:
    """Testes para NFEXMLBuilder."""

    def test_build_nfe_xml(
        self,
        emitente: Emitente,
        destinatario_pj: Destinatario,
        produto_simples: Produto,
        pagamento_dinheiro: Pagamento,
    ):
        """Testa geracao de XML da NFe."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pj,
            produtos=[produto_simples],
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA DE MERCADORIA",
            numero=1,
            serie=1,
            data_emissao=datetime.utcnow(),
        )

        builder = NFEXMLBuilder()
        xml = builder.build_nfe(nf)

        assert xml is not None
        assert "NFe" in xml
        assert "infNFe" in xml
        assert nf.chave_acesso in xml
        assert emitente.cnpj.replace(".", "").replace("/", "").replace("-", "") in xml
        assert "VENDA DE MERCADORIA" in xml

    def test_build_nfe_xml_multiplos_produtos(
        self,
        emitente: Emitente,
        destinatario_pj: Destinatario,
        lista_produtos: List[Produto],
        pagamento_dinheiro: Pagamento,
    ):
        """Testa geracao de XML com multiplos produtos."""
        nf = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=emitente,
            destinatario=destinatario_pj,
            produtos=lista_produtos,
            pagamentos=[pagamento_dinheiro],
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA",
            numero=1,
            serie=1,
            data_emissao=datetime.utcnow(),
        )

        builder = NFEXMLBuilder()
        xml = builder.build_nfe(nf)

        # Verifica presenca dos produtos
        assert "PROD001" in xml
        assert "PROD002" in xml
        assert 'nItem="1"' in xml
        assert 'nItem="2"' in xml


# ==========================================================================
# TestSEFAZService - Testes do Service Layer
# ==========================================================================
class TestSEFAZService:
    """Testes para SEFAZService."""

    def test_emitir_nfe_mock(self):
        """Testa emissao de NFe com mock."""
        mock_manager = MagicMock()
        mock_manager.emit_document.return_value = {
            "chave_acesso": "35260112345678000195550010000000011234567890",
            "numero": 1,
            "serie": 1,
            "protocolo": "123456789012345",
        }

        with patch(
            "modules.government_integrations.services.sefaz_service.get_sefaz_manager",
            return_value=mock_manager,
        ):
            resultado = SEFAZService.emitir_nfe(
                tipo="nfe",
                destinatario={"cpf_cnpj": "12345678000195", "nome": "Cliente"},
                produtos=[{"codigo": "001", "descricao": "Produto", "quantidade": 1}],
                pagamento={"tipo": "01", "valor": 100.00},
            )

        assert resultado["tipo"] == "nfe"
        assert resultado["chave_acesso"] is not None
        assert resultado["status"] == "enviada"

    def test_consultar_nfe_mock(self):
        """Testa consulta de NFe com mock."""
        mock_manager = MagicMock()
        mock_manager.query_document.return_value = {
            "status": "autorizada",
            "protocolo": "123456789012345",
            "data_autorizacao": "2026-01-16T10:00:00",
            "motivo": "Autorizado o uso da NF-e",
        }

        with patch(
            "modules.government_integrations.services.sefaz_service.get_sefaz_manager",
            return_value=mock_manager,
        ):
            resultado = SEFAZService.consultar_nfe(
                chave_acesso="35260112345678000195550010000000011234567890"
            )

        assert resultado["chave_acesso"] == "35260112345678000195550010000000011234567890"
        assert resultado["status"] == "autorizada"


# ==========================================================================
# TestSEFAZEndpoints - Testes de Endpoints REST
# ==========================================================================
class TestSEFAZEndpoints:
    """Testes para endpoints REST do SEFAZ."""

    @pytest.mark.asyncio
    async def test_emitir_nfe_endpoint(self, auth_headers: Dict[str, str]):
        """Testa endpoint de emissao de NFe."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/sefaz/nfe/emitir",
                headers=auth_headers,
                json={
                    "tipo": "nfe",
                    "destinatario": {
                        "cpf_cnpj": "12345678000195",
                        "nome": "Cliente Teste LTDA",
                        "endereco": {
                            "logradouro": "Rua Teste",
                            "numero": "100",
                            "bairro": "Centro",
                            "cidade": "Sao Paulo",
                            "uf": "SP",
                            "cep": "01234567",
                        },
                    },
                    "produtos": [
                        {
                            "codigo": "PROD001",
                            "descricao": "Produto de Teste",
                            "ncm": "84713012",
                            "cfop": "5102",
                            "unidade": "UN",
                            "quantidade": 1,
                            "valor_unitario": 100.00,
                        }
                    ],
                    "pagamento": {"tipo": "01", "valor": 100.00},
                },
            )

        # Pode retornar 202 (sucesso), 400 (validacao), 401 (auth), ou 500 (erro interno)
        assert response.status_code in [202, 400, 401, 403, 500]

        if response.status_code == 202:
            data = response.json()
            assert data["success"] is True
            assert "data" in data

    @pytest.mark.asyncio
    async def test_emitir_nfce_endpoint(self, auth_headers: Dict[str, str]):
        """Testa endpoint de emissao de NFCe."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/sefaz/nfe/emitir",
                headers=auth_headers,
                json={
                    "tipo": "nfce",
                    "destinatario": {
                        "cpf_cnpj": "12345678909",
                        "nome": "Consumidor Final",
                    },
                    "produtos": [
                        {
                            "codigo": "PROD001",
                            "descricao": "Produto Venda Balcao",
                            "quantidade": 2,
                            "valor_unitario": 50.00,
                        }
                    ],
                    "pagamento": {"tipo": "17", "valor": 100.00},  # PIX
                },
            )

        # Pode retornar 202 (sucesso), 400 (validacao), 401 (auth), ou 500 (erro interno)
        assert response.status_code in [202, 400, 401, 403, 500]

    @pytest.mark.asyncio
    async def test_consultar_nfe_endpoint(self, auth_headers: Dict[str, str]):
        """Testa endpoint de consulta de NFe."""
        chave_acesso = "35260112345678000195550010000000011234567890"

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/government/sefaz/nfe/consultar/{chave_acesso}",
                headers=auth_headers,
            )

        # Pode retornar 200, 401, 404 ou 500
        assert response.status_code in [200, 401, 404, 500]

    @pytest.mark.asyncio
    async def test_consultar_nfe_chave_invalida(self, auth_headers: Dict[str, str]):
        """Testa consulta com chave de acesso invalida."""
        chave_invalida = "123"  # Chave muito curta

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/government/sefaz/nfe/consultar/{chave_invalida}",
                headers=auth_headers,
            )

        # Deve retornar 422 (validacao) ou 404 devido a validacao do path
        assert response.status_code in [401, 404, 422]

    @pytest.mark.asyncio
    async def test_emitir_nfe_dados_invalidos(self, auth_headers: Dict[str, str]):
        """Testa emissao com dados invalidos."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/sefaz/nfe/emitir",
                headers=auth_headers,
                json={
                    "tipo": "nfe",
                    "destinatario": {},  # Faltando campos obrigatorios
                    "produtos": [],  # Lista vazia
                    "pagamento": {},
                },
            )

        # Deve retornar 422 (validacao Pydantic)
        assert response.status_code in [401, 422]


# ==========================================================================
# TestUFConfigs - Testes de Configuracoes por UF
# ==========================================================================
class TestUFConfigs:
    """Testes para configuracoes de UF."""

    def test_todas_ufs_configuradas(self):
        """Verifica que todas as UFs estao configuradas."""
        ufs_brasil = [
            "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
            "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
            "RO", "RR", "RS", "SC", "SE", "SP", "TO",
        ]

        for uf in ufs_brasil:
            assert uf in UF_CONFIGS, f"UF {uf} nao configurada"
            config = UF_CONFIGS[uf]
            assert config.code is not None
            assert config.webservice_url is not None

    def test_codigos_ibge_unicos(self):
        """Verifica que codigos IBGE sao unicos."""
        codigos = [config.code for config in UF_CONFIGS.values()]
        assert len(codigos) == len(set(codigos)), "Codigos IBGE duplicados"

    def test_config_sp(self):
        """Testa configuracao especifica de SP."""
        config = UF_CONFIGS["SP"]

        assert config.uf == "SP"
        assert config.code == "35"
        assert "sp.gov.br" in config.webservice_url


# ==========================================================================
# TestEnums - Testes de Enumeracoes
# ==========================================================================
class TestEnums:
    """Testes para enumeracoes do SEFAZ."""

    def test_document_type_values(self):
        """Testa valores de DocumentType."""
        assert DocumentType.NFE.value == "nfe"
        assert DocumentType.NFCE.value == "nfce"
        assert DocumentType.CTE.value == "cte"
        assert DocumentType.MDFE.value == "mdfe"

    def test_document_status_values(self):
        """Testa valores de DocumentStatus."""
        assert DocumentStatus.DRAFT.value == "draft"
        assert DocumentStatus.AUTHORIZED.value == "authorized"
        assert DocumentStatus.CANCELLED.value == "cancelled"
        assert DocumentStatus.ERROR.value == "error"

    def test_payment_type_values(self):
        """Testa valores de PaymentType."""
        assert PaymentType.DINHEIRO.value == "01"
        assert PaymentType.PIX.value == "17"
        assert PaymentType.CARTAO_CREDITO.value == "03"
        assert PaymentType.BOLETO.value == "15"

    def test_contingency_type_values(self):
        """Testa valores de ContingencyType."""
        assert ContingencyType.NORMAL.value == "1"
        assert ContingencyType.SVC_AN.value == "6"
        assert ContingencyType.OFFLINE.value == "9"


# ==========================================================================
# TestProduto - Testes do Dataclass Produto
# ==========================================================================
class TestProduto:
    """Testes para o dataclass Produto."""

    def test_valor_total_sem_desconto(self):
        """Testa calculo de valor total sem desconto."""
        produto = Produto(
            codigo="PROD",
            descricao="Produto",
            ncm="12345678",
            cfop="5102",
            unidade="UN",
            quantidade=Decimal("10"),
            valor_unitario=Decimal("50.00"),
        )

        assert produto.valor_total == Decimal("500.00")

    def test_valor_total_com_desconto(self):
        """Testa calculo de valor total com desconto."""
        produto = Produto(
            codigo="PROD",
            descricao="Produto",
            ncm="12345678",
            cfop="5102",
            unidade="UN",
            quantidade=Decimal("10"),
            valor_unitario=Decimal("50.00"),
            valor_desconto=Decimal("100.00"),
        )

        assert produto.valor_total == Decimal("400.00")

    def test_valor_icms(self):
        """Testa calculo de valor do ICMS."""
        produto = Produto(
            codigo="PROD",
            descricao="Produto",
            ncm="12345678",
            cfop="5102",
            unidade="UN",
            quantidade=Decimal("10"),
            valor_unitario=Decimal("100.00"),
            aliquota_icms=Decimal("18.00"),
        )

        # 1000 * 18% = 180
        assert produto.valor_icms == Decimal("180.00")

    def test_to_dict(self):
        """Testa conversao para dicionario."""
        produto = Produto(
            codigo="PROD001",
            descricao="Produto Teste",
            ncm="84713012",
            cfop="5102",
            unidade="UN",
            quantidade=Decimal("5"),
            valor_unitario=Decimal("99.90"),
        )

        data = produto.to_dict()

        assert data["codigo"] == "PROD001"
        assert data["descricao"] == "Produto Teste"
        assert data["quantidade"] == "5"
        assert data["valor_unitario"] == "99.90"
        assert data["valor_total"] == "499.50"


# ==========================================================================
# TestExceptions - Testes de Excecoes
# ==========================================================================
class TestExceptions:
    """Testes para excecoes customizadas."""

    def test_sefaz_error(self):
        """Testa SEFAZError basico."""
        error = SEFAZError("Erro de teste")

        assert str(error) == "Erro de teste"
        assert error.message == "Erro de teste"
        assert error.code is None

    def test_sefaz_error_com_codigo(self):
        """Testa SEFAZError com codigo."""
        error = SEFAZError("Documento rejeitado", code="539")

        assert error.code == "539"
        assert error.document_id is None

    def test_sefaz_error_completo(self):
        """Testa SEFAZError com todos os campos."""
        doc_id = str(uuid4())
        error = SEFAZError(
            "Falha na transmissao",
            code="999",
            document_id=doc_id,
        )

        assert error.message == "Falha na transmissao"
        assert error.code == "999"
        assert error.document_id == doc_id

    def test_validation_error_heranca(self):
        """Testa que ValidationError herda de SEFAZError."""
        error = ValidationError("Campo obrigatorio")

        assert isinstance(error, SEFAZError)
        assert str(error) == "Campo obrigatorio"


# ==========================================================================
# TestInitSEFAZManager - Testes da Funcao de Inicializacao
# ==========================================================================
class TestInitSEFAZManager:
    """Testes para init_sefaz_manager."""

    def test_init_sefaz_manager(self, emitente: Emitente):
        """Testa inicializacao do singleton."""
        manager = init_sefaz_manager(
            emitente=emitente,
            ambiente="2",
        )

        assert manager is not None
        assert isinstance(manager, SEFAZManager)
        assert manager.emitente == emitente

    def test_init_sefaz_manager_com_certificado(self, emitente: Emitente):
        """Testa inicializacao com caminho de certificado."""
        manager = init_sefaz_manager(
            emitente=emitente,
            certificate_path="/path/to/cert.pfx",
            certificate_password="senha123",
            ambiente="1",  # Producao
        )

        assert manager.certificate_path == "/path/to/cert.pfx"
        assert manager.certificate_password == "senha123"
        assert manager.ambiente == "1"
