"""
Configurações e fixtures para testes do módulo de integrações governamentais.
"""

# Adicionar path do módulo
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend/modules/government_integrations")


@pytest.fixture
def tenant_id():
    """Fixture para ID de tenant."""
    return uuid4()


@pytest.fixture
def usuario_id():
    """Fixture para ID de usuário."""
    return uuid4()


@pytest.fixture
def documento_id():
    """Fixture para ID de documento."""
    return uuid4()


@pytest.fixture
def chave_nfe():
    """Fixture para chave de acesso NF-e."""
    return "35260112345678000190550010000001231234567890"


@pytest.fixture
def dados_nfe():
    """Fixture para dados de NF-e."""
    return {
        "nNF": "123",
        "serie": "1",
        "dhEmi": "2026-01-15T10:00:00-03:00",
        "vNF": "1000.00",
        "emit": {
            "CNPJ": "12345678000190",
            "xNome": "Empresa Emitente LTDA",
            "enderEmit": {
                "xLgr": "Rua Teste",
                "nro": "100",
                "xBairro": "Centro",
                "cMun": "3550308",
                "xMun": "São Paulo",
                "UF": "SP",
                "CEP": "01310100",
            },
        },
        "dest": {
            "CNPJ": "98765432000190",
            "xNome": "Empresa Destinatária LTDA",
        },
        "total": {
            "ICMSTot": {
                "vBC": "1000.00",
                "vICMS": "180.00",
                "vProd": "1000.00",
                "vNF": "1000.00",
            },
        },
    }


@pytest.fixture
def dados_funcionario():
    """Fixture para dados de funcionário."""
    return {
        "id": str(uuid4()),
        "nome": "João da Silva Santos",
        "cpf": "12345678900",
        "email": "joao.silva@empresa.com",
        "telefone": "11999998888",
        "data_nascimento": "1990-05-15",
        "endereco": {
            "logradouro": "Rua das Flores",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01310100",
        },
        "dados_bancarios": {
            "banco": "341",
            "agencia": "1234",
            "conta": "56789-0",
        },
        "salario": 5000.00,
    }


@pytest.fixture
def mock_db_session():
    """Fixture para mock de sessão do banco de dados."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_redis():
    """Fixture para mock do Redis."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.publish = AsyncMock()
    redis.lpush = AsyncMock()
    redis.ltrim = AsyncMock()
    redis.incr = AsyncMock()
    redis.expire = AsyncMock()
    redis.pipeline = MagicMock()
    return redis


@pytest.fixture
def mock_http_response():
    """Fixture para mock de resposta HTTP."""
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="<xml>OK</xml>")
    response.json = AsyncMock(return_value={"status": "ok"})
    return response


@pytest.fixture
def resultado_verificacao_sucesso():
    """Fixture para resultado de verificação bem-sucedido."""
    from core.contingency.availability_checker import ResultadoVerificacao

    return ResultadoVerificacao(
        uf="SP",
        tipo_documento="nfe",
        endpoint="https://nfe.fazenda.sp.gov.br/ws/NfeStatusServico4.asmx",
        disponivel=True,
        tempo_resposta_ms=150,
        http_status=200,
    )


@pytest.fixture
def resultado_verificacao_falha():
    """Fixture para resultado de verificação com falha."""
    from core.contingency.availability_checker import ResultadoVerificacao

    return ResultadoVerificacao(
        uf="SP",
        tipo_documento="nfe",
        endpoint="https://nfe.fazenda.sp.gov.br/ws/NfeStatusServico4.asmx",
        disponivel=False,
        tempo_resposta_ms=10000,
        erro="Timeout",
    )


@pytest.fixture
def evento_auditoria():
    """Fixture para evento de auditoria."""
    from core.compliance.audit_logger import AuditEvent, TipoEvento

    return AuditEvent(
        tenant_id=uuid4(),
        usuario_id=uuid4(),
        tipo=TipoEvento.NFE_EMITIDA,
        recurso="nfe",
        recurso_id="123",
        acao="Consulta de NF-e",
        ip_origem="192.168.1.100",
    )


@pytest.fixture
def xml_nfe_valido():
    """Fixture para XML de NF-e válido (simplificado)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <NFe>
        <infNFe Id="NFe35260112345678000190550010000001231234567890" versao="4.00">
            <ide>
                <cUF>35</cUF>
                <cNF>12345678</cNF>
                <natOp>VENDA</natOp>
                <mod>55</mod>
                <serie>1</serie>
                <nNF>123</nNF>
                <dhEmi>2026-01-15T10:00:00-03:00</dhEmi>
                <tpNF>1</tpNF>
            </ide>
            <emit>
                <CNPJ>12345678000190</CNPJ>
                <xNome>Empresa Teste</xNome>
            </emit>
            <total>
                <ICMSTot>
                    <vNF>1000.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
</nfeProc>"""
