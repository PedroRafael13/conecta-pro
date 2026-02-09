"""
Testes para eSocial - Sistema de Escrituracao Digital das Obrigacoes
Fiscais, Previdenciarias e Trabalhistas.

Testes unitarios e de integracao para o modulo eSocial.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest

from modules.government_integrations.core.esocial_transmitter import (
    CertificateInfo,
    Environment,
    ESocialError,
    ESocialEvent,
    ESocialTransmitter,
    EventType,
    TransmissionError,
    TransmissionStatus,
    ValidationError,
    XMLBuilder,
    get_esocial_transmitter,
    init_esocial_transmitter,
)
from modules.government_integrations.schemas.common import (
    StandardResponse,
)
from modules.government_integrations.schemas.esocial import (
    ESocialEventRequest,
)
from modules.government_integrations.services.esocial_service import (
    ESocialService,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    def test_esocial_event_request_valid_s2200(self):
        """Testa ESocialEventRequest valido para S-2200 (Admissao)."""
        request = ESocialEventRequest(
            tipo_evento="S-2200",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "nome": "Joao da Silva",
                "sexo": "M",
                "dtNascimento": "1990-01-15",
                "matricula": "001234",
                "dtAdmissao": "2026-01-10",
                "salario": 5000.00,
            },
            ambiente="homologacao",
        )
        assert request.tipo_evento == "S-2200"
        assert request.ambiente == "homologacao"

    def test_esocial_event_request_valid_s2299(self):
        """Testa ESocialEventRequest valido para S-2299 (Desligamento)."""
        request = ESocialEventRequest(
            tipo_evento="S-2299",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "matricula": "001234",
                "mtvDeslig": "11",
                "dtDesligamento": "2026-01-31",
            },
            ambiente="producao",
        )
        assert request.tipo_evento == "S-2299"
        assert request.ambiente == "producao"

    def test_esocial_event_request_valid_s2220(self):
        """Testa ESocialEventRequest valido para S-2220 (Monitoramento Saude)."""
        request = ESocialEventRequest(
            tipo_evento="S-2220",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "matricula": "001234",
                "tpExameOcup": 0,
                "dtAso": "2026-01-15",
                "resAso": 1,
                "nmMed": "Dr. Jose Medico",
                "nrCRM": "12345",
                "ufCRM": "SP",
            },
        )
        assert request.tipo_evento == "S-2220"

    def test_esocial_event_request_valid_s2230(self):
        """Testa ESocialEventRequest valido para S-2230 (Afastamento)."""
        request = ESocialEventRequest(
            tipo_evento="S-2230",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "matricula": "001234",
                "codMotAfast": "01",
                "dtIniAfast": "2026-01-20",
                "dtFimAfast": "2026-01-30",
            },
        )
        assert request.tipo_evento == "S-2230"

    def test_esocial_event_request_valid_s2240(self):
        """Testa ESocialEventRequest valido para S-2240 (Condicoes Ambientais)."""
        request = ESocialEventRequest(
            tipo_evento="S-2240",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "matricula": "001234",
                "codAmb": "AMB001",
                "dtIniCondicao": "2026-01-01",
            },
        )
        assert request.tipo_evento == "S-2240"

    def test_esocial_event_request_valid_s2210(self):
        """Testa ESocialEventRequest valido para S-2210 (CAT)."""
        request = ESocialEventRequest(
            tipo_evento="S-2210",
            funcionario_id=uuid4(),
            dados={
                "cpf": "12345678901",
                "matricula": "001234",
                "dtAcid": "2026-01-15",
                "tpAcid": "1",
                "hrAcid": "14:30",
                "tpCat": "1",
            },
        )
        assert request.tipo_evento == "S-2210"

    def test_esocial_event_request_ambiente_default(self):
        """Testa ambiente default (homologacao)."""
        request = ESocialEventRequest(
            tipo_evento="S-2200",
            funcionario_id=uuid4(),
            dados={"cpf": "12345678901"},
        )
        assert request.ambiente == "homologacao"

    def test_esocial_event_request_tipo_evento_invalido(self):
        """Testa rejeicao de tipo de evento invalido."""
        with pytest.raises(ValueError):
            ESocialEventRequest(
                tipo_evento="S-9999",
                funcionario_id=uuid4(),
                dados={},
            )

    def test_esocial_event_request_ambiente_invalido(self):
        """Testa rejeicao de ambiente invalido."""
        with pytest.raises(ValueError):
            ESocialEventRequest(
                tipo_evento="S-2200",
                funcionario_id=uuid4(),
                dados={},
                ambiente="teste",
            )

    def test_esocial_event_request_funcionario_id_uuid(self):
        """Testa que funcionario_id deve ser UUID."""
        func_id = uuid4()
        request = ESocialEventRequest(
            tipo_evento="S-2200",
            funcionario_id=func_id,
            dados={},
        )
        assert request.funcionario_id == func_id
        assert isinstance(request.funcionario_id, UUID)

    def test_standard_response_success(self):
        """Testa StandardResponse de sucesso."""
        response = StandardResponse(
            success=True,
            message="Evento enviado",
            data={"protocolo": "PROT123456"},
        )
        assert response.success is True
        assert response.message == "Evento enviado"
        assert response.data["protocolo"] == "PROT123456"

    def test_standard_response_error(self):
        """Testa StandardResponse de erro."""
        response = StandardResponse(
            success=False,
            message="Erro ao processar evento",
            data=None,
        )
        assert response.success is False
        assert response.data is None


class TestESocialTransmitter:
    """Testes para ESocialTransmitter (core)."""

    @pytest.fixture
    def transmitter(self):
        """Cria instancia do transmitter para testes."""
        return ESocialTransmitter(
            environment=Environment.PRODUCAO_RESTRITA,
            certificate_path=None,
            certificate_password=None,
        )

    @pytest.fixture
    def admissao_data(self):
        """Dados de admissao para testes."""
        return {
            "cpf": "12345678901",
            "nome": "Maria da Silva",
            "sexo": "F",
            "dtNascimento": "1995-05-20",
            "matricula": "EMP001",
            "dtAdmissao": "2026-01-15",
            "salario": 4500.00,
            "cargo": "Analista de Sistemas",
            "cbo": "212405",
        }

    @pytest.fixture
    def desligamento_data(self):
        """Dados de desligamento para testes."""
        return {
            "cpf": "12345678901",
            "matricula": "EMP001",
            "mtvDeslig": "11",
            "dtDesligamento": "2026-01-31",
        }

    @pytest.fixture
    def monitoramento_saude_data(self):
        """Dados de monitoramento de saude para testes."""
        return {
            "cpf": "12345678901",
            "matricula": "EMP001",
            "tpExameOcup": 0,
            "dtAso": "2026-01-10",
            "resAso": 1,
            "nmMed": "Dr. Antonio Medico",
            "nrCRM": "54321",
            "ufCRM": "RJ",
            "exames": [
                {
                    "dtExm": "2026-01-10",
                    "procRealizado": "0428",
                    "obsProc": "Audiometria ocupacional",
                }
            ],
        }

    def test_init_ambiente_producao_restrita(self, transmitter):
        """Testa inicializacao em ambiente de producao restrita."""
        assert transmitter.environment == Environment.PRODUCAO_RESTRITA

    def test_init_ambiente_producao(self):
        """Testa inicializacao em ambiente de producao."""
        transmitter = ESocialTransmitter(environment=Environment.PRODUCAO)
        assert transmitter.environment == Environment.PRODUCAO

    def test_webservice_url_producao_restrita(self, transmitter):
        """Testa URL do webservice em producao restrita."""
        url = transmitter.WEBSERVICE_URLS[Environment.PRODUCAO_RESTRITA]
        assert "producaorestrita" in url

    def test_webservice_url_producao(self):
        """Testa URL do webservice em producao."""
        transmitter = ESocialTransmitter(environment=Environment.PRODUCAO)
        url = transmitter.WEBSERVICE_URLS[Environment.PRODUCAO]
        assert "producao.esocial" in url
        assert "producaorestrita" not in url

    @pytest.mark.asyncio
    async def test_create_event_s2200(self, transmitter, admissao_data):
        """Testa criacao de evento S-2200 (Admissao)."""
        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
            employee_cpf="12345678901",
        )

        assert event.event_type == EventType.S2200_ADMISSAO
        assert event.status == TransmissionStatus.PENDING
        assert event.employer_cnpj == "12345678000199"
        assert event.employee_cpf == "12345678901"
        assert event.xml_content is not None
        assert "<evtAdmissao" in event.xml_content

    @pytest.mark.asyncio
    async def test_create_event_s2299(self, transmitter, desligamento_data):
        """Testa criacao de evento S-2299 (Desligamento)."""
        event = await transmitter.create_event(
            event_type=EventType.S2299_DESLIGAMENTO,
            employer_cnpj="12345678000199",
            data=desligamento_data,
            employee_cpf="12345678901",
        )

        assert event.event_type == EventType.S2299_DESLIGAMENTO
        assert event.status == TransmissionStatus.PENDING
        assert "<evtDeslig" in event.xml_content

    @pytest.mark.asyncio
    async def test_create_event_s2220(self, transmitter, monitoramento_saude_data):
        """Testa criacao de evento S-2220 (Monitoramento Saude)."""
        event = await transmitter.create_event(
            event_type=EventType.S2220_MONITORAMENTO_SAUDE,
            employer_cnpj="12345678000199",
            data=monitoramento_saude_data,
            employee_cpf="12345678901",
        )

        assert event.event_type == EventType.S2220_MONITORAMENTO_SAUDE
        assert event.status == TransmissionStatus.PENDING
        assert "<evtMonit" in event.xml_content

    @pytest.mark.asyncio
    async def test_create_event_with_reference(self, transmitter, admissao_data):
        """Testa criacao de evento com referencia."""
        ref_date = date(2026, 1, 15)
        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
            reference_id="ADM-2026-001",
            reference_date=ref_date,
        )

        assert event.reference_id == "ADM-2026-001"
        assert event.reference_date == ref_date

    @pytest.mark.asyncio
    async def test_validate_event_success(self, transmitter, admissao_data):
        """Testa validacao de evento com sucesso."""
        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        result = await transmitter.validate_event(event.id)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_event_not_found(self, transmitter):
        """Testa validacao de evento nao encontrado."""
        with pytest.raises(ESocialError) as exc_info:
            await transmitter.validate_event(uuid4())

        assert "nao encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_event(self, transmitter, admissao_data):
        """Testa recuperacao de evento por ID."""
        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        retrieved = await transmitter.get_event(event.id)

        assert retrieved is not None
        assert retrieved.id == event.id
        assert retrieved.event_type == event.event_type

    @pytest.mark.asyncio
    async def test_get_event_not_found(self, transmitter):
        """Testa recuperacao de evento inexistente."""
        retrieved = await transmitter.get_event(uuid4())
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_events_all(self, transmitter, admissao_data, desligamento_data):
        """Testa listagem de todos os eventos."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )
        await transmitter.create_event(
            event_type=EventType.S2299_DESLIGAMENTO,
            employer_cnpj="12345678000199",
            data=desligamento_data,
        )

        events = await transmitter.list_events()

        assert len(events) >= 2

    @pytest.mark.asyncio
    async def test_list_events_by_status(self, transmitter, admissao_data):
        """Testa listagem de eventos por status."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        events = await transmitter.list_events(status=TransmissionStatus.PENDING)

        assert len(events) >= 1
        for event in events:
            assert event.status == TransmissionStatus.PENDING

    @pytest.mark.asyncio
    async def test_list_events_by_type(self, transmitter, admissao_data):
        """Testa listagem de eventos por tipo."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        events = await transmitter.list_events(event_type=EventType.S2200_ADMISSAO)

        assert len(events) >= 1
        for event in events:
            assert event.event_type == EventType.S2200_ADMISSAO

    @pytest.mark.asyncio
    async def test_list_events_by_cnpj(self, transmitter, admissao_data):
        """Testa listagem de eventos por CNPJ."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        events = await transmitter.list_events(employer_cnpj="12345678000199")

        assert len(events) >= 1
        for event in events:
            assert event.employer_cnpj == "12345678000199"

    @pytest.mark.asyncio
    async def test_get_pending_events(self, transmitter, admissao_data):
        """Testa listagem de eventos pendentes."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        pending = await transmitter.get_pending_events()

        assert len(pending) >= 1
        for event in pending:
            assert event.status == TransmissionStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_transmission_summary(self, transmitter, admissao_data):
        """Testa geracao de resumo de transmissoes."""
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        summary = await transmitter.get_transmission_summary()

        assert "generated_at" in summary
        assert "total_events" in summary
        assert "by_status" in summary
        assert "pending_count" in summary

    @pytest.mark.asyncio
    async def test_transmit_event(self, transmitter, admissao_data):
        """Testa transmissao de evento (simulado)."""
        # Mock do certificado e assinador
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        result = await transmitter.transmit(event.id)

        assert result.status == TransmissionStatus.PROCESSING
        assert result.transmitted_at is not None
        assert result.protocol is not None
        assert result.protocol.startswith("PROT")

    @pytest.mark.asyncio
    async def test_check_status(self, transmitter, admissao_data):
        """Testa consulta de status de evento."""
        # Mock do certificado e assinador
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )

        await transmitter.transmit(event.id)
        result = await transmitter.check_status(event.id)

        assert result.status == TransmissionStatus.ACCEPTED
        assert result.processed_at is not None
        assert result.receipt_number is not None
        assert result.receipt_number.startswith("REC")

    @pytest.mark.asyncio
    async def test_batch_transmit(self, transmitter, admissao_data, desligamento_data):
        """Testa transmissao em lote."""
        # Mock do certificado e assinador
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        event1 = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data=admissao_data,
        )
        event2 = await transmitter.create_event(
            event_type=EventType.S2299_DESLIGAMENTO,
            employer_cnpj="12345678000199",
            data=desligamento_data,
        )

        result = await transmitter.batch_transmit([event1.id, event2.id])

        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["events"]) == 2


class TestXMLBuilder:
    """Testes para XMLBuilder."""

    @pytest.fixture
    def builder(self):
        """Cria instancia do XMLBuilder."""
        return XMLBuilder(environment=Environment.PRODUCAO_RESTRITA)

    def test_build_event_id(self, builder):
        """Testa geracao de ID de evento."""
        event_id = builder.build_event_id("S-2200", "12345678000199")

        assert event_id.startswith("ID")
        assert "12345678" in event_id

    def test_build_s2200_admissao(self, builder):
        """Testa construcao de XML S-2200."""
        data = {
            "cpf": "12345678901",
            "nome": "Maria Teste",
            "sexo": "F",
            "dtNascimento": "1990-01-01",
            "matricula": "001",
            "dtAdmissao": "2026-01-15",
            "salario": 5000.00,
            "cargo": "Analista",
            "cbo": "212405",
            "employer_cnpj": "12345678000199",
        }

        xml = builder.build_s2200_admissao(data)

        assert "<eSocial" in xml
        assert "<evtAdmissao" in xml
        assert "<cpfTrab>12345678901</cpfTrab>" in xml
        assert "<nmTrab>Maria Teste</nmTrab>" in xml
        assert "<sexo>F</sexo>" in xml
        assert "<matricula>001</matricula>" in xml
        assert "<vrSalFx>5000.0</vrSalFx>" in xml

    def test_build_s2299_desligamento(self, builder):
        """Testa construcao de XML S-2299."""
        data = {
            "cpf": "12345678901",
            "matricula": "001",
            "mtvDeslig": "11",
            "dtDesligamento": "2026-01-31",
            "employer_cnpj": "12345678000199",
        }

        xml = builder.build_s2299_desligamento(data)

        assert "<eSocial" in xml
        assert "<evtDeslig" in xml
        assert "<cpfTrab>12345678901</cpfTrab>" in xml
        assert "<mtvDeslig>11</mtvDeslig>" in xml
        assert "<dtDeslig>2026-01-31</dtDeslig>" in xml

    def test_build_s2220_monitoramento_saude(self, builder):
        """Testa construcao de XML S-2220."""
        data = {
            "cpf": "12345678901",
            "matricula": "001",
            "tpExameOcup": 0,
            "dtAso": "2026-01-10",
            "resAso": 1,
            "nmMed": "Dr. Medico Teste",
            "nrCRM": "12345",
            "ufCRM": "SP",
            "exames": [
                {
                    "dtExm": "2026-01-10",
                    "procRealizado": "0428",
                    "obsProc": "Audiometria",
                }
            ],
            "employer_cnpj": "12345678000199",
        }

        xml = builder.build_s2220_monitoramento_saude(data)

        assert "<eSocial" in xml
        assert "<evtMonit" in xml
        assert "<cpfTrab>12345678901</cpfTrab>" in xml
        assert "<tpExameOcup>0</tpExameOcup>" in xml
        assert "<dtAso>2026-01-10</dtAso>" in xml
        assert "<nmMed>Dr. Medico Teste</nmMed>" in xml
        assert "<nrCRM>12345</nrCRM>" in xml

    def test_xml_namespace(self, builder):
        """Testa namespace do XML."""
        assert "esocial.gov.br" in builder.NAMESPACE

    def test_xml_version(self, builder):
        """Testa versao do layout."""
        assert builder.VERSION.startswith("S_")


class TestCertificateInfo:
    """Testes para CertificateInfo."""

    @pytest.fixture
    def valid_certificate(self):
        """Certificado valido."""
        return CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

    @pytest.fixture
    def expired_certificate(self):
        """Certificado expirado."""
        return CertificateInfo(
            serial_number="654321",
            subject_cn="Expired Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2020, 1, 1),
            valid_until=datetime(2023, 12, 31),
            type="A1",
        )

    def test_certificate_is_valid(self, valid_certificate):
        """Testa verificacao de certificado valido."""
        assert valid_certificate.is_valid() is True

    def test_certificate_is_expired(self, expired_certificate):
        """Testa verificacao de certificado expirado."""
        assert expired_certificate.is_valid() is False

    def test_days_until_expiry_positive(self, valid_certificate):
        """Testa dias ate vencimento (positivo)."""
        days = valid_certificate.days_until_expiry()
        assert days > 0

    def test_days_until_expiry_negative(self, expired_certificate):
        """Testa dias ate vencimento (negativo/expirado)."""
        days = expired_certificate.days_until_expiry()
        assert days < 0


class TestESocialEvent:
    """Testes para ESocialEvent dataclass."""

    def test_event_to_dict(self):
        """Testa conversao de evento para dict."""
        event = ESocialEvent(
            id=uuid4(),
            event_type=EventType.S2200_ADMISSAO,
            status=TransmissionStatus.PENDING,
            employer_cnpj="12345678000199",
            employee_cpf="12345678901",
        )

        event_dict = event.to_dict()

        assert "id" in event_dict
        assert event_dict["event_type"] == "S-2200"
        assert event_dict["status"] == "pending"
        assert event_dict["employer_cnpj"] == "12345678000199"
        assert event_dict["employee_cpf"] == "12345678901"

    def test_event_to_dict_with_dates(self):
        """Testa conversao de evento com datas."""
        event = ESocialEvent(
            id=uuid4(),
            event_type=EventType.S2200_ADMISSAO,
            status=TransmissionStatus.ACCEPTED,
            employer_cnpj="12345678000199",
            transmitted_at=datetime(2026, 1, 15, 10, 30),
            processed_at=datetime(2026, 1, 15, 10, 35),
        )

        event_dict = event.to_dict()

        assert event_dict["transmitted_at"] == "2026-01-15T10:30:00"
        assert event_dict["processed_at"] == "2026-01-15T10:35:00"


class TestEventTypes:
    """Testes para tipos de eventos."""

    def test_event_type_values(self):
        """Testa valores dos tipos de eventos."""
        assert EventType.S2200_ADMISSAO.value == "S-2200"
        assert EventType.S2299_DESLIGAMENTO.value == "S-2299"
        assert EventType.S2220_MONITORAMENTO_SAUDE.value == "S-2220"
        assert EventType.S2230_AFASTAMENTO.value == "S-2230"
        assert EventType.S2210_CAT.value == "S-2210"
        assert EventType.S1200_REMUNERACAO.value == "S-1200"
        assert EventType.S1299_FECHAMENTO.value == "S-1299"
        assert EventType.S3000_EXCLUSAO.value == "S-3000"

    def test_transmission_status_values(self):
        """Testa valores dos status de transmissao."""
        assert TransmissionStatus.PENDING.value == "pending"
        assert TransmissionStatus.VALIDATING.value == "validating"
        assert TransmissionStatus.TRANSMITTED.value == "transmitted"
        assert TransmissionStatus.PROCESSING.value == "processing"
        assert TransmissionStatus.ACCEPTED.value == "accepted"
        assert TransmissionStatus.REJECTED.value == "rejected"
        assert TransmissionStatus.ERROR.value == "error"
        assert TransmissionStatus.CANCELLED.value == "cancelled"

    def test_environment_values(self):
        """Testa valores dos ambientes."""
        assert Environment.PRODUCAO.value == "1"
        assert Environment.PRODUCAO_RESTRITA.value == "2"


class TestExceptions:
    """Testes para excecoes customizadas."""

    def test_esocial_error(self):
        """Testa ESocialError."""
        error = ESocialError("Erro de teste", event_id="EVT001", code="ERR001")

        assert str(error) == "Erro de teste"
        assert error.event_id == "EVT001"
        assert error.code == "ERR001"

    def test_validation_error(self):
        """Testa ValidationError."""
        error = ValidationError("Erro de validacao")

        assert str(error) == "Erro de validacao"
        assert isinstance(error, ESocialError)

    def test_transmission_error(self):
        """Testa TransmissionError."""
        error = TransmissionError("Erro de transmissao")

        assert str(error) == "Erro de transmissao"
        assert isinstance(error, ESocialError)


class TestSingleton:
    """Testes para funcoes singleton."""

    def test_get_esocial_transmitter_singleton(self):
        """Testa que get_esocial_transmitter retorna singleton."""
        import modules.government_integrations.core.esocial_transmitter as module

        # Reset singleton
        module._esocial_transmitter = None

        transmitter1 = get_esocial_transmitter()
        transmitter2 = get_esocial_transmitter()

        assert transmitter1 is transmitter2

        # Cleanup
        module._esocial_transmitter = None

    def test_init_esocial_transmitter(self):
        """Testa inicializacao do transmitter."""
        import modules.government_integrations.core.esocial_transmitter as module

        # Reset singleton
        module._esocial_transmitter = None

        transmitter = init_esocial_transmitter(
            environment=Environment.PRODUCAO,
            certificate_path="/path/to/cert.pfx",
            certificate_password="senha123",
        )

        assert transmitter.environment == Environment.PRODUCAO
        assert transmitter.certificate_path == "/path/to/cert.pfx"

        # Cleanup
        module._esocial_transmitter = None


class TestESocialService:
    """Testes para ESocialService."""

    def test_eventos_suportados(self):
        """Testa lista de eventos suportados."""
        eventos = ESocialService.EVENTOS_SUPORTADOS

        assert len(eventos) > 0

        codigos = [e["codigo"] for e in eventos]
        assert "S-2200" in codigos
        assert "S-2299" in codigos
        assert "S-2220" in codigos
        assert "S-2230" in codigos

    def test_listar_eventos_suportados(self):
        """Testa metodo listar_eventos_suportados."""
        resultado = ESocialService.listar_eventos_suportados()

        assert "eventos" in resultado
        assert "ambiente_producao" in resultado
        assert "ambiente_homologacao" in resultado
        assert len(resultado["eventos"]) > 0

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_enviar_evento(self, mock_transmitter):
        """Testa envio de evento via service."""
        mock_esocial = MagicMock()
        mock_esocial.transmit_event.return_value = {"protocolo": "PROT123456"}
        mock_transmitter.return_value = mock_esocial

        resultado = ESocialService.enviar_evento(
            tipo_evento="S-2200",
            funcionario_id="func-001",
            dados={"cpf": "12345678901"},
            ambiente="homologacao",
        )

        assert resultado["tipo_evento"] == "S-2200"
        assert resultado["funcionario_id"] == "func-001"
        assert resultado["ambiente"] == "homologacao"
        assert resultado["status"] == "enviado"
        assert "protocolo" in resultado
        assert "data_transmissao" in resultado

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_consultar_status(self, mock_transmitter):
        """Testa consulta de status via service."""
        mock_esocial = MagicMock()
        mock_esocial.get_event_status.return_value = {
            "status": "aceito",
            "recibo": "REC123456",
            "erros": [],
            "data_processamento": "2026-01-15T10:30:00",
        }
        mock_transmitter.return_value = mock_esocial

        resultado = ESocialService.consultar_status("PROT123456")

        assert resultado["protocolo"] == "PROT123456"
        assert resultado["status"] == "aceito"
        assert resultado["recibo"] == "REC123456"


class TestESocialEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.esocial_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_list_eventos_suportados(self, client):
        """Testa endpoint de eventos suportados."""
        response = client.get("/api/v1/government/esocial/eventos-suportados")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "eventos" in data["data"]

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_enviar_evento_s2200(self, mock_transmitter, client):
        """Testa endpoint de envio de evento S-2200."""
        mock_esocial = MagicMock()
        mock_esocial.transmit_event.return_value = {"protocolo": "PROT123456"}
        mock_transmitter.return_value = mock_esocial

        payload = {
            "tipo_evento": "S-2200",
            "funcionario_id": str(uuid4()),
            "dados": {
                "cpf": "12345678901",
                "nome": "Maria da Silva",
                "sexo": "F",
                "dtNascimento": "1995-05-20",
                "matricula": "EMP001",
                "dtAdmissao": "2026-01-15",
                "salario": 4500.00,
            },
            "ambiente": "homologacao",
        }

        response = client.post("/api/v1/government/esocial/evento", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "protocolo" in data["data"]

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_enviar_evento_s2299(self, mock_transmitter, client):
        """Testa endpoint de envio de evento S-2299."""
        mock_esocial = MagicMock()
        mock_esocial.transmit_event.return_value = {"protocolo": "PROT654321"}
        mock_transmitter.return_value = mock_esocial

        payload = {
            "tipo_evento": "S-2299",
            "funcionario_id": str(uuid4()),
            "dados": {
                "cpf": "12345678901",
                "matricula": "EMP001",
                "mtvDeslig": "11",
                "dtDesligamento": "2026-01-31",
            },
            "ambiente": "producao",
        }

        response = client.post("/api/v1/government/esocial/evento", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_enviar_evento_s2220(self, mock_transmitter, client):
        """Testa endpoint de envio de evento S-2220."""
        mock_esocial = MagicMock()
        mock_esocial.transmit_event.return_value = {"protocolo": "PROT789012"}
        mock_transmitter.return_value = mock_esocial

        payload = {
            "tipo_evento": "S-2220",
            "funcionario_id": str(uuid4()),
            "dados": {
                "cpf": "12345678901",
                "matricula": "EMP001",
                "tpExameOcup": 0,
                "dtAso": "2026-01-10",
                "resAso": 1,
                "nmMed": "Dr. Jose",
                "nrCRM": "12345",
                "ufCRM": "SP",
            },
        }

        response = client.post("/api/v1/government/esocial/evento", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True

    def test_enviar_evento_tipo_invalido(self, client):
        """Testa rejeicao de tipo de evento invalido."""
        payload = {
            "tipo_evento": "S-9999",
            "funcionario_id": str(uuid4()),
            "dados": {},
        }

        response = client.post("/api/v1/government/esocial/evento", json=payload)

        assert response.status_code == 422

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_consultar_status_endpoint(self, mock_transmitter, client):
        """Testa endpoint de consulta de status."""
        mock_esocial = MagicMock()
        mock_esocial.get_event_status.return_value = {
            "status": "aceito",
            "recibo": "REC123456",
            "erros": [],
            "data_processamento": "2026-01-15T10:30:00",
        }
        mock_transmitter.return_value = mock_esocial

        response = client.get("/api/v1/government/esocial/consultar/PROT123456")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["protocolo"] == "PROT123456"

    def test_consultar_status_protocolo_curto(self, client):
        """Testa rejeicao de protocolo muito curto."""
        response = client.get("/api/v1/government/esocial/consultar/ABC")

        assert response.status_code == 422

    @patch("modules.government_integrations.services.esocial_service.get_esocial_transmitter")
    def test_enviar_evento_erro_interno(self, mock_transmitter, client):
        """Testa tratamento de erro interno."""
        mock_esocial = MagicMock()
        mock_esocial.transmit_event.side_effect = Exception("Erro interno")
        mock_transmitter.return_value = mock_esocial

        payload = {
            "tipo_evento": "S-2200",
            "funcionario_id": str(uuid4()),
            "dados": {"cpf": "12345678901"},
        }

        response = client.post("/api/v1/government/esocial/evento", json=payload)

        assert response.status_code == 500
        data = response.json()
        assert "Erro interno" in data["detail"]


class TestESocialIntegration:
    """Testes de integracao do modulo eSocial."""

    @pytest.mark.asyncio
    async def test_fluxo_completo_admissao(self):
        """Testa fluxo completo de admissao."""
        transmitter = ESocialTransmitter(
            environment=Environment.PRODUCAO_RESTRITA,
        )

        # Mock certificado
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        # 1. Criar evento
        event = await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj="12345678000199",
            data={
                "cpf": "12345678901",
                "nome": "Funcionario Teste",
                "sexo": "M",
                "dtNascimento": "1990-01-01",
                "matricula": "001",
                "dtAdmissao": "2026-01-15",
                "salario": 5000.00,
            },
            employee_cpf="12345678901",
        )

        assert event.status == TransmissionStatus.PENDING

        # 2. Validar evento
        validation = await transmitter.validate_event(event.id)
        assert validation["valid"] is True

        # 3. Transmitir evento
        event = await transmitter.transmit(event.id)
        assert event.status == TransmissionStatus.PROCESSING
        assert event.protocol is not None

        # 4. Consultar status
        event = await transmitter.check_status(event.id)
        assert event.status == TransmissionStatus.ACCEPTED
        assert event.receipt_number is not None

    @pytest.mark.asyncio
    async def test_fluxo_completo_desligamento(self):
        """Testa fluxo completo de desligamento."""
        transmitter = ESocialTransmitter(
            environment=Environment.PRODUCAO_RESTRITA,
        )

        # Mock certificado
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        # Criar e transmitir evento
        event = await transmitter.create_event(
            event_type=EventType.S2299_DESLIGAMENTO,
            employer_cnpj="12345678000199",
            data={
                "cpf": "12345678901",
                "matricula": "001",
                "mtvDeslig": "11",
                "dtDesligamento": "2026-01-31",
            },
            employee_cpf="12345678901",
        )

        await transmitter.transmit(event.id)
        event = await transmitter.check_status(event.id)

        assert event.status == TransmissionStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_multiplos_eventos_mesmo_funcionario(self):
        """Testa envio de multiplos eventos para mesmo funcionario."""
        transmitter = ESocialTransmitter(
            environment=Environment.PRODUCAO_RESTRITA,
        )

        # Mock certificado
        transmitter._certificate_info = CertificateInfo(
            serial_number="123456",
            subject_cn="Test Certificate",
            issuer_cn="Test CA",
            valid_from=datetime(2025, 1, 1),
            valid_until=datetime(2027, 12, 31),
            type="A1",
        )

        mock_signer = MagicMock()
        mock_signer.sign_event.return_value = "<xml>signed</xml>"
        transmitter._xml_signer = mock_signer

        cpf = "12345678901"
        cnpj = "12345678000199"

        # Evento 1: Admissao
        await transmitter.create_event(
            event_type=EventType.S2200_ADMISSAO,
            employer_cnpj=cnpj,
            data={
                "cpf": cpf,
                "nome": "Funcionario",
                "sexo": "M",
                "dtNascimento": "1990-01-01",
                "matricula": "001",
                "dtAdmissao": "2026-01-15",
                "salario": 5000.00,
            },
            employee_cpf=cpf,
        )

        # Evento 2: Monitoramento saude
        await transmitter.create_event(
            event_type=EventType.S2220_MONITORAMENTO_SAUDE,
            employer_cnpj=cnpj,
            data={
                "cpf": cpf,
                "matricula": "001",
                "tpExameOcup": 0,
                "dtAso": "2026-01-16",
                "resAso": 1,
                "nmMed": "Dr. Teste",
                "nrCRM": "12345",
                "ufCRM": "SP",
            },
            employee_cpf=cpf,
        )

        # Listar eventos do funcionario
        events = await transmitter.list_events(employer_cnpj=cnpj)

        cpf_events = [e for e in events if e.employee_cpf == cpf]
        assert len(cpf_events) >= 2

        types = [e.event_type for e in cpf_events]
        assert EventType.S2200_ADMISSAO in types
        assert EventType.S2220_MONITORAMENTO_SAUDE in types
