"""
Testes para o modulo de Certificados Digitais A1
Sprint 33: Integracoes Governamentais

Testes para:
- CertificateManager: Gerenciamento de certificados .pfx/.p12
- XMLSigner: Assinatura digital XML (XMLDSig)
- Endpoints REST: Upload, validacao, listagem de certificados
"""

import pytest
import base64
import hashlib
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from uuid import uuid4
from io import BytesIO

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# Imports do modulo de certificados
from modules.government_integrations.core.certificate_manager import (
    CertificateManager,
    CertificateStore,
    CertificateInfo,
    CertificateStatus,
    CertificateType,
)
from modules.government_integrations.core.xml_signer import (
    XMLSigner,
    ESocialXMLSigner,
    NFEXMLSigner,
    CTEXMLSigner,
    MDFEXMLSigner,
    SignatureType,
    SignatureConfig,
    DigestMethod,
    SignatureMethod,
    CanonicalizationMethod,
    TransformMethod,
    NAMESPACES,
    DEFAULT_CONFIGS,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_certificate_info():
    """Fixture para informacoes de certificado mock."""
    return CertificateInfo(
        serial_number="ABC123456789",
        thumbprint="1234567890ABCDEF1234567890ABCDEF12345678",
        subject_cn="EMPRESA TESTE LTDA:12345678000199",
        subject_cpf_cnpj="12345678000199",
        subject_organization="EMPRESA TESTE LTDA",
        subject_ou="Certificado Digital",
        issuer_cn="AC TESTE v5",
        issuer_organization="Autoridade Certificadora",
        valid_from=datetime.utcnow() - timedelta(days=30),
        valid_until=datetime.utcnow() + timedelta(days=335),
        certificate_type=CertificateType.A1,
        status=CertificateStatus.VALID,
        key_size=2048,
        signature_algorithm="sha256WithRSAEncryption"
    )


@pytest.fixture
def mock_certificate_info_expired():
    """Fixture para certificado expirado."""
    return CertificateInfo(
        serial_number="XYZ987654321",
        thumbprint="FEDCBA0987654321FEDCBA0987654321FEDCBA09",
        subject_cn="EMPRESA EXPIRADA LTDA:98765432000188",
        subject_cpf_cnpj="98765432000188",
        subject_organization="EMPRESA EXPIRADA LTDA",
        issuer_cn="AC TESTE v5",
        valid_from=datetime.utcnow() - timedelta(days=400),
        valid_until=datetime.utcnow() - timedelta(days=35),
        certificate_type=CertificateType.A1,
        status=CertificateStatus.EXPIRED,
        key_size=2048,
    )


@pytest.fixture
def mock_certificate_info_expiring_soon():
    """Fixture para certificado expirando em breve."""
    return CertificateInfo(
        serial_number="EXP123456789",
        thumbprint="AAAA567890BBBB1234567890CCCC12345678",
        subject_cn="EMPRESA EXPIRANDO LTDA:11111111000111",
        subject_cpf_cnpj="11111111000111",
        subject_organization="EMPRESA EXPIRANDO LTDA",
        issuer_cn="AC TESTE v5",
        valid_from=datetime.utcnow() - timedelta(days=345),
        valid_until=datetime.utcnow() + timedelta(days=15),
        certificate_type=CertificateType.A1,
        status=CertificateStatus.EXPIRING_SOON,
        key_size=2048,
    )


@pytest.fixture
def mock_pfx_data():
    """Fixture para dados PFX simulados."""
    # Simulacao de dados binarios de um arquivo PFX
    return b"MOCK_PFX_BINARY_DATA_FOR_TESTING"


@pytest.fixture
def sample_xml_content():
    """Fixture para XML de exemplo para assinatura."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<documento Id="DOC123456">
    <dados>
        <campo1>Valor1</campo1>
        <campo2>Valor2</campo2>
    </dados>
</documento>'''


@pytest.fixture
def sample_nfe_xml():
    """Fixture para XML de NF-e."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
    <infNFe Id="NFe35210112345678000199550010000000011000000017" versao="4.00">
        <ide>
            <cUF>35</cUF>
            <natOp>VENDA</natOp>
        </ide>
        <emit>
            <CNPJ>12345678000199</CNPJ>
        </emit>
    </infNFe>
</NFe>'''


@pytest.fixture
def sample_esocial_xml():
    """Fixture para XML de eSocial."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<eSocial xmlns="http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_01_00">
    <evtAdmissao Id="ID1123456789012345678901234567890123456789">
        <ideEvento>
            <indRetif>1</indRetif>
            <tpAmb>2</tpAmb>
        </ideEvento>
        <ideEmpregador>
            <tpInsc>1</tpInsc>
            <nrInsc>12345678000199</nrInsc>
        </ideEmpregador>
    </evtAdmissao>
</eSocial>'''


# =============================================================================
# TestCertificateInfo - Testes para dataclass CertificateInfo
# =============================================================================

class TestCertificateInfo:
    """Testes para CertificateInfo dataclass."""

    def test_days_until_expiry_valid(self, mock_certificate_info):
        """Testa calculo de dias ate expiracao para certificado valido."""
        days = mock_certificate_info.days_until_expiry
        assert days > 0
        assert days <= 365

    def test_days_until_expiry_expired(self, mock_certificate_info_expired):
        """Testa calculo de dias para certificado expirado."""
        days = mock_certificate_info_expired.days_until_expiry
        assert days == 0

    def test_is_valid_true(self, mock_certificate_info):
        """Testa propriedade is_valid para certificado valido."""
        assert mock_certificate_info.is_valid is True

    def test_is_valid_false_expired(self, mock_certificate_info_expired):
        """Testa propriedade is_valid para certificado expirado."""
        assert mock_certificate_info_expired.is_valid is False

    def test_is_expiring_soon_true(self, mock_certificate_info_expiring_soon):
        """Testa propriedade is_expiring_soon."""
        assert mock_certificate_info_expiring_soon.is_expiring_soon is True

    def test_is_expiring_soon_false(self, mock_certificate_info):
        """Testa que certificado valido nao esta expirando em breve."""
        assert mock_certificate_info.is_expiring_soon is False

    def test_to_dict(self, mock_certificate_info):
        """Testa conversao para dicionario."""
        result = mock_certificate_info.to_dict()

        assert isinstance(result, dict)
        assert result["serial_number"] == "ABC123456789"
        assert result["subject_cn"] == "EMPRESA TESTE LTDA:12345678000199"
        assert result["subject_cpf_cnpj"] == "12345678000199"
        assert result["certificate_type"] == "A1"
        assert result["status"] == "valid"
        assert "valid_from" in result
        assert "valid_until" in result
        assert "days_until_expiry" in result
        assert result["is_valid"] is True
        assert result["key_size"] == 2048

    def test_to_dict_expired(self, mock_certificate_info_expired):
        """Testa conversao para dicionario de certificado expirado."""
        result = mock_certificate_info_expired.to_dict()

        assert result["status"] == "expired"
        assert result["is_valid"] is False


# =============================================================================
# TestCertificateManager - Testes para o gerenciador de certificados A1
# =============================================================================

class TestCertificateManager:
    """Testes para CertificateManager."""

    def test_init_with_path(self):
        """Testa inicializacao com caminho de arquivo."""
        manager = CertificateManager(
            pfx_path="/path/to/cert.pfx",
            password="senha123"
        )

        assert manager._pfx_path == "/path/to/cert.pfx"
        assert manager._password == b"senha123"
        assert manager._loaded is False

    def test_init_with_data(self, mock_pfx_data):
        """Testa inicializacao com dados binarios."""
        manager = CertificateManager(
            pfx_data=mock_pfx_data,
            password="senha123"
        )

        assert manager._pfx_data == mock_pfx_data
        assert manager._loaded is False

    def test_init_without_password(self):
        """Testa inicializacao sem senha."""
        manager = CertificateManager(pfx_path="/path/to/cert.pfx")

        assert manager._password is None

    @pytest.mark.asyncio
    async def test_load_no_certificate_specified(self):
        """Testa erro ao carregar sem certificado especificado."""
        manager = CertificateManager()

        with pytest.raises(ValueError) as exc_info:
            manager.load()

        # Aceita mensagem com ou sem acento
        error_msg = str(exc_info.value).lower()
        assert "certificado" in error_msg and "especificado" in error_msg

    @pytest.mark.asyncio
    async def test_load_file_not_found(self):
        """Testa erro ao carregar arquivo inexistente."""
        manager = CertificateManager(
            pfx_path="/path/nonexistent.pfx",
            password="senha"
        )

        with pytest.raises(ValueError):
            manager.load()

    @pytest.mark.asyncio
    async def test_load_invalid_password(self, mock_pfx_data):
        """Testa erro com senha invalida."""
        from OpenSSL import crypto

        manager = CertificateManager(
            pfx_data=mock_pfx_data,
            password="senha_errada"
        )

        with patch.object(crypto, 'load_pkcs12', side_effect=crypto.Error("bad password")):
            with pytest.raises(ValueError) as exc_info:
                manager.load()

            assert "Erro ao carregar certificado" in str(exc_info.value)

    def test_load_success_mocked(self, mock_certificate_info):
        """Testa carregamento com sucesso (mockado)."""
        manager = CertificateManager(
            pfx_data=b"mock_data",
            password="senha123"
        )

        # Mock dos objetos OpenSSL e cryptography
        with patch('modules.government_integrations.core.certificate_manager.crypto') as mock_crypto:
            with patch('modules.government_integrations.core.certificate_manager.x509') as mock_x509:
                with patch('modules.government_integrations.core.certificate_manager.serialization') as mock_serial:
                    with patch.object(CertificateManager, '_extract_info', return_value=mock_certificate_info):
                        # Setup mocks
                        mock_pkcs12 = MagicMock()
                        mock_cert = MagicMock()
                        mock_pkey = MagicMock()

                        mock_pkcs12.get_certificate.return_value = mock_cert
                        mock_pkcs12.get_privatekey.return_value = mock_pkey
                        mock_crypto.load_pkcs12.return_value = mock_pkcs12
                        mock_crypto.dump_certificate.return_value = b"PEM_CERT"
                        mock_crypto.dump_privatekey.return_value = b"PEM_KEY"

                        # Mock x509 certificate
                        mock_x509_cert = MagicMock()
                        mock_x509_cert.subject = MagicMock()
                        mock_x509_cert.issuer = MagicMock()
                        mock_x509_cert.serial_number = 123456789
                        mock_x509_cert.not_valid_before = datetime.utcnow() - timedelta(days=30)
                        mock_x509_cert.not_valid_after = datetime.utcnow() + timedelta(days=335)
                        mock_x509_cert.fingerprint.return_value = b"1234567890" * 4
                        mock_x509_cert.public_key.return_value = MagicMock(key_size=2048)

                        mock_x509.load_pem_x509_certificate.return_value = mock_x509_cert

                        # Mock private key
                        mock_private_key = MagicMock()
                        mock_serial.load_pem_private_key.return_value = mock_private_key

                        # Executar
                        result = manager.load()

                        assert result is True
                        assert manager._loaded is True

    def test_already_loaded(self, mock_certificate_info):
        """Testa que certificado ja carregado retorna True."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._info = mock_certificate_info

        result = manager.load()

        assert result is True

    def test_info_property_triggers_load(self):
        """Testa que acessar info dispara load."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        with patch.object(manager, 'load') as mock_load:
            mock_load.return_value = True
            manager._info = MagicMock()

            _ = manager.info

            mock_load.assert_called_once()

    def test_certificate_property_triggers_load(self):
        """Testa que acessar certificate dispara load."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        with patch.object(manager, 'load') as mock_load:
            mock_load.return_value = True
            manager._certificate = MagicMock()

            _ = manager.certificate

            mock_load.assert_called_once()

    def test_get_certificate_pem(self):
        """Testa obtencao do certificado em formato PEM."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._certificate = MagicMock()

        with patch('modules.government_integrations.core.certificate_manager.crypto') as mock_crypto:
            mock_crypto.dump_certificate.return_value = b"-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----"
            mock_crypto.FILETYPE_PEM = 1

            result = manager.get_certificate_pem()

            assert b"BEGIN CERTIFICATE" in result

    def test_get_certificate_der(self):
        """Testa obtencao do certificado em formato DER."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._certificate = MagicMock()

        with patch('modules.government_integrations.core.certificate_manager.crypto') as mock_crypto:
            mock_crypto.dump_certificate.return_value = b"\x30\x82\x01"  # DER bytes
            mock_crypto.FILETYPE_ASN1 = 2

            result = manager.get_certificate_der()

            assert isinstance(result, bytes)

    def test_get_certificate_base64(self):
        """Testa obtencao do certificado em base64."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._certificate = MagicMock()

        with patch.object(manager, 'get_certificate_der', return_value=b"mock_der_data"):
            result = manager.get_certificate_base64()

            expected = base64.b64encode(b"mock_der_data").decode('ascii')
            assert result == expected

    def test_sign_data(self):
        """Testa assinatura de dados."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True

        mock_private_key = MagicMock()
        mock_private_key.sign.return_value = b"mock_signature"
        manager._private_key_crypto = mock_private_key

        result = manager.sign_data(b"data_to_sign", algorithm="sha256")

        assert result == b"mock_signature"
        mock_private_key.sign.assert_called_once()

    def test_sign_data_base64(self):
        """Testa assinatura de dados em base64."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        with patch.object(manager, 'sign_data', return_value=b"mock_signature"):
            result = manager.sign_data_base64(b"data", "sha256")

            expected = base64.b64encode(b"mock_signature").decode('ascii')
            assert result == expected

    def test_verify_signature_valid(self):
        """Testa verificacao de assinatura valida."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True

        mock_cert = MagicMock()
        mock_public_key = MagicMock()
        mock_public_key.verify.return_value = None  # Nao lanca excecao = valido
        mock_cert.public_key.return_value = mock_public_key
        manager._x509_cert = mock_cert

        result = manager.verify_signature(b"data", b"signature", "sha256")

        assert result is True

    def test_verify_signature_invalid(self):
        """Testa verificacao de assinatura invalida."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True

        mock_cert = MagicMock()
        mock_public_key = MagicMock()
        mock_public_key.verify.side_effect = Exception("Invalid signature")
        mock_cert.public_key.return_value = mock_public_key
        manager._x509_cert = mock_cert

        result = manager.verify_signature(b"data", b"bad_signature", "sha256")

        assert result is False

    def test_validate_valid_certificate(self, mock_certificate_info):
        """Testa validacao de certificado valido."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._info = mock_certificate_info

        is_valid, message = manager.validate()

        assert is_valid is True
        # Aceita "valido" ou "válido"
        assert "lid" in message.lower()  # parte comum de valido/válido

    def test_validate_expired_certificate(self, mock_certificate_info_expired):
        """Testa validacao de certificado expirado."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._info = mock_certificate_info_expired

        is_valid, message = manager.validate()

        assert is_valid is False
        assert "expirado" in message.lower()

    def test_validate_expiring_soon(self, mock_certificate_info_expiring_soon):
        """Testa validacao de certificado expirando em breve."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")
        manager._loaded = True
        manager._info = mock_certificate_info_expiring_soon

        is_valid, message = manager.validate()

        assert is_valid is True
        assert "expira" in message.lower()

    def test_validate_not_loaded_triggers_load(self):
        """Testa que validacao carrega certificado se necessario."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        with patch.object(manager, 'load', side_effect=Exception("Load error")):
            is_valid, message = manager.validate()

            assert is_valid is False
            assert "Erro ao carregar" in message

    def test_extract_cpf_cnpj_from_cn(self):
        """Testa extracao de CPF/CNPJ do Common Name."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        # Testar CNPJ
        result = manager._extract_cpf_cnpj("EMPRESA TESTE:12345678000199", None)
        assert result == "12345678000199"

        # Testar CPF
        result = manager._extract_cpf_cnpj("PESSOA FISICA:12345678901", None)
        assert result == "12345678901"

    def test_extract_cpf_cnpj_from_ou(self):
        """Testa extracao de CPF/CNPJ do Organizational Unit."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        result = manager._extract_cpf_cnpj(None, "OU com CNPJ 12345678000199")
        assert result == "12345678000199"

    def test_extract_cpf_cnpj_not_found(self):
        """Testa quando CPF/CNPJ nao e encontrado."""
        manager = CertificateManager(pfx_data=b"mock", password="senha")

        result = manager._extract_cpf_cnpj("Nome sem documento", "OU sem documento")
        assert result is None


# =============================================================================
# TestCertificateStore - Testes para armazenamento de multiplos certificados
# =============================================================================

class TestCertificateStore:
    """Testes para CertificateStore."""

    def test_init_default_path(self):
        """Testa inicializacao com caminho padrao."""
        store = CertificateStore()

        assert store._storage_path == "/opt/conecta-pro/certificates"

    def test_init_custom_path(self):
        """Testa inicializacao com caminho customizado."""
        store = CertificateStore(storage_path="/custom/path")

        assert store._storage_path == "/custom/path"

    def test_add_certificate(self, mock_certificate_info):
        """Testa adicao de certificado."""
        store = CertificateStore(storage_path="/tmp/test_certs")

        with patch.object(CertificateManager, 'load', return_value=True):
            with patch.object(CertificateManager, 'info', new_callable=PropertyMock) as mock_info:
                mock_info.return_value = mock_certificate_info

                with patch.object(store, '_save_certificate'):
                    result = store.add_certificate(
                        identifier="12345678000199",
                        pfx_data=b"mock_pfx",
                        password="senha"
                    )

                    assert result.subject_cn == mock_certificate_info.subject_cn
                    assert "12345678000199" in store._certificates

    def test_get_certificate_found(self, mock_certificate_info):
        """Testa obtencao de certificado existente."""
        store = CertificateStore()
        mock_manager = MagicMock()
        store._certificates["test_id"] = mock_manager

        result = store.get_certificate("test_id")

        assert result == mock_manager

    def test_get_certificate_not_found(self):
        """Testa obtencao de certificado inexistente."""
        store = CertificateStore()

        result = store.get_certificate("nonexistent")

        assert result is None

    def test_remove_certificate_success(self):
        """Testa remocao de certificado com sucesso."""
        store = CertificateStore(storage_path="/tmp/test")
        store._certificates["test_id"] = MagicMock()

        with patch.object(store, '_delete_certificate_file'):
            result = store.remove_certificate("test_id")

            assert result is True
            assert "test_id" not in store._certificates

    def test_remove_certificate_not_found(self):
        """Testa remocao de certificado inexistente."""
        store = CertificateStore()

        result = store.remove_certificate("nonexistent")

        assert result is False

    def test_list_certificates(self, mock_certificate_info):
        """Testa listagem de certificados."""
        store = CertificateStore()

        mock_manager1 = MagicMock()
        mock_manager1.info = mock_certificate_info

        mock_manager2 = MagicMock()
        mock_manager2.info = mock_certificate_info

        store._certificates = {
            "cert1": mock_manager1,
            "cert2": mock_manager2,
        }

        result = store.list_certificates()

        assert len(result) == 2
        assert "cert1" in result
        assert "cert2" in result


# =============================================================================
# TestXMLSigner - Testes para assinatura XML
# =============================================================================

class TestXMLSigner:
    """Testes para XMLSigner."""

    @pytest.fixture
    def mock_cert_manager(self, mock_certificate_info):
        """Fixture para CertificateManager mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.info = mock_certificate_info
        manager.get_certificate_base64.return_value = "MOCK_CERT_BASE64=="
        manager.sign_data.return_value = b"mock_signature_bytes"
        return manager

    def test_init(self, mock_cert_manager):
        """Testa inicializacao do XMLSigner."""
        signer = XMLSigner(mock_cert_manager)

        assert signer.cert_manager == mock_cert_manager

    def test_init_loads_certificate_if_needed(self):
        """Testa que certificado e carregado se necessario."""
        mock_manager = MagicMock(spec=CertificateManager)
        mock_manager._loaded = False

        XMLSigner(mock_manager)

        mock_manager.load.assert_called_once()

    def test_sign_generic(self, mock_cert_manager, sample_xml_content):
        """Testa assinatura generica de XML."""
        signer = XMLSigner(mock_cert_manager)

        result = signer.sign(
            sample_xml_content,
            signature_type=SignatureType.GENERIC,
            reference_uri="#DOC123456"
        )

        assert "<?xml" in result
        assert "Signature" in result
        assert "SignedInfo" in result
        assert "SignatureValue" in result
        assert "X509Certificate" in result

    def test_sign_with_custom_config(self, mock_cert_manager, sample_xml_content):
        """Testa assinatura com configuracao customizada."""
        signer = XMLSigner(mock_cert_manager)

        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            digest_method=DigestMethod.SHA256,
            signature_method=SignatureMethod.RSA_SHA256,
            canonicalization=CanonicalizationMethod.C14N_EXCLUSIVE,
            reference_uri="#DOC123456"
        )

        result = signer.sign(
            sample_xml_content,
            config=config
        )

        assert "Signature" in result
        assert "sha256" in result.lower() or "SHA256" in result

    def test_sign_invalid_xml(self, mock_cert_manager):
        """Testa erro ao assinar XML invalido."""
        signer = XMLSigner(mock_cert_manager)

        with pytest.raises(ValueError) as exc_info:
            signer.sign("<invalid>xml", reference_uri="#test")

        assert "Erro ao assinar XML" in str(exc_info.value)

    def test_sign_element_not_found(self, mock_cert_manager, sample_xml_content):
        """Testa erro quando elemento referenciado nao existe."""
        signer = XMLSigner(mock_cert_manager)

        with pytest.raises(ValueError) as exc_info:
            signer.sign(
                sample_xml_content,
                reference_uri="#NONEXISTENT"
            )

        # Aceita mensagem com ou sem acento
        assert "encontrado" in str(exc_info.value).lower()

    def test_find_element_to_sign_root(self, mock_cert_manager, sample_xml_content):
        """Testa busca de elemento raiz para assinatura."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        element = signer._find_element_to_sign(xml_doc, "")

        assert element.tag == "documento"

    def test_find_element_to_sign_by_id(self, mock_cert_manager, sample_xml_content):
        """Testa busca de elemento por ID."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        element = signer._find_element_to_sign(xml_doc, "#DOC123456")

        assert element.get('Id') == "DOC123456"

    def test_calculate_digest_sha1(self, mock_cert_manager, sample_xml_content):
        """Testa calculo de digest SHA1."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            digest_method=DigestMethod.SHA1
        )

        result = signer._calculate_digest(xml_doc, config)

        # Resultado deve ser base64
        assert isinstance(result, str)
        base64.b64decode(result)  # Nao deve lancar excecao

    def test_calculate_digest_sha256(self, mock_cert_manager, sample_xml_content):
        """Testa calculo de digest SHA256."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            digest_method=DigestMethod.SHA256
        )

        result = signer._calculate_digest(xml_doc, config)

        # SHA256 gera digest maior que SHA1
        decoded = base64.b64decode(result)
        assert len(decoded) == 32  # SHA256 = 32 bytes

    def test_canonicalize(self, mock_cert_manager, sample_xml_content):
        """Testa canonicalizacao de XML."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            canonicalization=CanonicalizationMethod.C14N
        )

        result = signer._canonicalize(xml_doc, config)

        assert isinstance(result, bytes)

    def test_canonicalize_exclusive(self, mock_cert_manager, sample_xml_content):
        """Testa canonicalizacao exclusiva."""
        signer = XMLSigner(mock_cert_manager)
        from lxml import etree

        xml_doc = etree.fromstring(sample_xml_content.encode('utf-8'))
        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            canonicalization=CanonicalizationMethod.C14N_EXCLUSIVE
        )

        result = signer._canonicalize(xml_doc, config)

        assert isinstance(result, bytes)

    def test_create_signature_element(self, mock_cert_manager):
        """Testa criacao do elemento Signature."""
        signer = XMLSigner(mock_cert_manager)

        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            reference_uri="#TEST123"
        )

        result = signer._create_signature_element("digest_value_test", config)

        # Verificar estrutura
        assert result.tag == "{http://www.w3.org/2000/09/xmldsig#}Signature"

        signed_info = result.find('.//ds:SignedInfo', NAMESPACES)
        assert signed_info is not None

        reference = signed_info.find('.//ds:Reference', NAMESPACES)
        assert reference is not None
        assert reference.get('URI') == "#TEST123"

        key_info = result.find('.//ds:KeyInfo', NAMESPACES)
        assert key_info is not None

        x509_cert = result.find('.//ds:X509Certificate', NAMESPACES)
        assert x509_cert is not None
        assert x509_cert.text == "MOCK_CERT_BASE64=="

    def test_verify_signed_xml(self, mock_cert_manager, sample_xml_content):
        """Testa verificacao de XML assinado."""
        signer = XMLSigner(mock_cert_manager)

        # Assinar primeiro
        signed_xml = signer.sign(
            sample_xml_content,
            reference_uri="#DOC123456"
        )

        # Verificar
        is_valid, message = signer.verify(signed_xml)

        assert is_valid is True
        # Aceita "valida" ou "válida"
        assert "lida" in message.lower()  # parte comum

    def test_verify_signature_not_found(self, mock_cert_manager):
        """Testa verificacao de XML sem assinatura."""
        signer = XMLSigner(mock_cert_manager)

        xml_without_signature = "<doc>test</doc>"

        is_valid, message = signer.verify(xml_without_signature)

        assert is_valid is False
        # Aceita mensagem com ou sem acento
        assert "encontrada" in message.lower()

    def test_verify_invalid_xml(self, mock_cert_manager):
        """Testa verificacao de XML invalido."""
        signer = XMLSigner(mock_cert_manager)

        is_valid, message = signer.verify("<invalid>xml")

        assert is_valid is False
        assert "Erro" in message


# =============================================================================
# TestESocialXMLSigner - Testes para assinador eSocial
# =============================================================================

class TestESocialXMLSigner:
    """Testes para ESocialXMLSigner."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Fixture para CertificateManager mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.get_certificate_base64.return_value = "MOCK_CERT=="
        manager.sign_data.return_value = b"mock_signature"
        return manager

    def test_sign_event(self, mock_cert_manager, sample_esocial_xml):
        """Testa assinatura de evento eSocial."""
        signer = ESocialXMLSigner(mock_cert_manager)

        result = signer.sign_event(
            sample_esocial_xml,
            event_id="ID1123456789012345678901234567890123456789"
        )

        assert "Signature" in result
        assert "SignatureValue" in result

    def test_esocial_uses_sha256(self, mock_cert_manager):
        """Testa que eSocial usa SHA256."""
        config = DEFAULT_CONFIGS[SignatureType.ESOCIAL]

        assert config.digest_method == DigestMethod.SHA256
        assert config.signature_method == SignatureMethod.RSA_SHA256

    def test_esocial_uses_exclusive_c14n(self, mock_cert_manager):
        """Testa que eSocial usa C14N exclusivo."""
        config = DEFAULT_CONFIGS[SignatureType.ESOCIAL]

        assert config.canonicalization == CanonicalizationMethod.C14N_EXCLUSIVE


# =============================================================================
# TestNFEXMLSigner - Testes para assinador NF-e
# =============================================================================

class TestNFEXMLSigner:
    """Testes para NFEXMLSigner."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Fixture para CertificateManager mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.get_certificate_base64.return_value = "MOCK_CERT=="
        manager.sign_data.return_value = b"mock_signature"
        return manager

    def test_sign_nfe(self, mock_cert_manager, sample_nfe_xml):
        """Testa assinatura de NF-e."""
        signer = NFEXMLSigner(mock_cert_manager)

        result = signer.sign_nfe(
            sample_nfe_xml,
            inf_nfe_id="NFe35210112345678000199550010000000011000000017"
        )

        assert "Signature" in result

    def test_sign_nfce(self, mock_cert_manager, sample_nfe_xml):
        """Testa assinatura de NFC-e."""
        signer = NFEXMLSigner(mock_cert_manager)

        result = signer.sign_nfce(
            sample_nfe_xml,
            inf_nfe_id="NFe35210112345678000199550010000000011000000017"
        )

        assert "Signature" in result

    def test_sign_cancellation(self, mock_cert_manager):
        """Testa assinatura de cancelamento."""
        signer = NFEXMLSigner(mock_cert_manager)

        cancel_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <envEvento xmlns="http://www.portalfiscal.inf.br/nfe">
            <evento>
                <infEvento Id="ID110111012345678000199550010000000011100000001">
                    <tpEvento>110111</tpEvento>
                </infEvento>
            </evento>
        </envEvento>'''

        result = signer.sign_cancellation(
            cancel_xml,
            inf_evento_id="ID110111012345678000199550010000000011100000001"
        )

        assert "Signature" in result

    def test_nfe_uses_sha1(self, mock_cert_manager):
        """Testa que NF-e usa SHA1."""
        config = DEFAULT_CONFIGS[SignatureType.NFE]

        assert config.digest_method == DigestMethod.SHA1
        assert config.signature_method == SignatureMethod.RSA_SHA1


# =============================================================================
# TestCTEXMLSigner - Testes para assinador CT-e
# =============================================================================

class TestCTEXMLSigner:
    """Testes para CTEXMLSigner."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Fixture para CertificateManager mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.get_certificate_base64.return_value = "MOCK_CERT=="
        manager.sign_data.return_value = b"mock_signature"
        return manager

    def test_sign_cte(self, mock_cert_manager):
        """Testa assinatura de CT-e."""
        signer = CTEXMLSigner(mock_cert_manager)

        cte_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <CTe xmlns="http://www.portalfiscal.inf.br/cte">
            <infCte Id="CTe35210112345678000199570010000000011000000013">
                <ide>
                    <cUF>35</cUF>
                </ide>
            </infCte>
        </CTe>'''

        result = signer.sign_cte(
            cte_xml,
            inf_cte_id="CTe35210112345678000199570010000000011000000013"
        )

        assert "Signature" in result


# =============================================================================
# TestMDFEXMLSigner - Testes para assinador MDF-e
# =============================================================================

class TestMDFEXMLSigner:
    """Testes para MDFEXMLSigner."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Fixture para CertificateManager mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.get_certificate_base64.return_value = "MOCK_CERT=="
        manager.sign_data.return_value = b"mock_signature"
        return manager

    def test_sign_mdfe(self, mock_cert_manager):
        """Testa assinatura de MDF-e."""
        signer = MDFEXMLSigner(mock_cert_manager)

        mdfe_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <MDFe xmlns="http://www.portalfiscal.inf.br/mdfe">
            <infMDFe Id="MDFe35210112345678000199580010000000011000000015">
                <ide>
                    <cUF>35</cUF>
                </ide>
            </infMDFe>
        </MDFe>'''

        result = signer.sign_mdfe(
            mdfe_xml,
            inf_mdfe_id="MDFe35210112345678000199580010000000011000000015"
        )

        assert "Signature" in result


# =============================================================================
# TestSignatureConfig - Testes para configuracao de assinatura
# =============================================================================

class TestSignatureConfig:
    """Testes para SignatureConfig."""

    def test_default_transforms(self):
        """Testa transforms padrao."""
        config = SignatureConfig(signature_type=SignatureType.GENERIC)

        assert TransformMethod.ENVELOPED in config.transforms
        assert TransformMethod.C14N in config.transforms

    def test_custom_transforms(self):
        """Testa transforms customizados."""
        config = SignatureConfig(
            signature_type=SignatureType.GENERIC,
            transforms=[TransformMethod.ENVELOPED, TransformMethod.C14N_EXCLUSIVE]
        )

        assert TransformMethod.C14N_EXCLUSIVE in config.transforms

    def test_default_configs_exist(self):
        """Testa que configuracoes padrao existem para todos os tipos."""
        assert SignatureType.ESOCIAL in DEFAULT_CONFIGS
        assert SignatureType.NFE in DEFAULT_CONFIGS
        assert SignatureType.NFCE in DEFAULT_CONFIGS
        assert SignatureType.CTE in DEFAULT_CONFIGS
        assert SignatureType.MDFE in DEFAULT_CONFIGS


# =============================================================================
# TestCertificateEndpoints - Testes para endpoints REST
# =============================================================================

class TestCertificateEndpoints:
    """Testes para endpoints REST de certificados."""

    @pytest.fixture
    def mock_store(self):
        """Fixture para CertificateStore mockado."""
        # Sem spec para permitir qualquer metodo ser mockado
        mock = MagicMock()
        mock.add_certificate = MagicMock()
        mock.get_certificate = MagicMock()
        mock.list_certificates = MagicMock()
        mock.remove_certificate = MagicMock()
        return mock

    @pytest.fixture
    def mock_file(self):
        """Fixture para arquivo de upload mockado."""
        file = MagicMock()
        file.filename = "certificado.pfx"
        file.read = AsyncMock(return_value=b"mock_pfx_content")
        return file

    @pytest.mark.asyncio
    async def test_upload_certificate_success(self, mock_store, mock_file, mock_certificate_info):
        """Testa upload de certificado com sucesso."""
        from modules.government_integrations.controllers.certificate_controller import upload_certificate

        mock_cert_manager = MagicMock()
        mock_cert_manager.load.return_value = True
        mock_cert_manager.validate.return_value = (True, "Certificado valido")
        mock_cert_manager.get_info.return_value = mock_certificate_info

        mock_store.add.return_value = "cert_123"

        with patch('modules.government_integrations.controllers.certificate_controller.CertificateManager') as MockManager:
            MockManager.return_value = mock_cert_manager

            result = await upload_certificate(
                file=mock_file,
                password="senha123",
                alias="meu_cert",
                store=mock_store
            )

            assert result.success is True
            assert result.certificate_id == "cert_123"
            assert result.type == "A1"

    @pytest.mark.asyncio
    async def test_upload_certificate_invalid_extension(self, mock_store):
        """Testa upload com extensao invalida."""
        from modules.government_integrations.controllers.certificate_controller import upload_certificate

        mock_file = MagicMock()
        mock_file.filename = "certificado.txt"

        with pytest.raises(HTTPException) as exc_info:
            await upload_certificate(
                file=mock_file,
                password="senha",
                store=mock_store
            )

        assert exc_info.value.status_code == 400
        assert "Formato invalido" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_upload_certificate_no_filename(self, mock_store):
        """Testa upload sem nome de arquivo."""
        from modules.government_integrations.controllers.certificate_controller import upload_certificate

        mock_file = MagicMock()
        mock_file.filename = None

        with pytest.raises(HTTPException) as exc_info:
            await upload_certificate(
                file=mock_file,
                password="senha",
                store=mock_store
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_certificate_invalid_password(self, mock_store, mock_file):
        """Testa upload com senha invalida."""
        from modules.government_integrations.controllers.certificate_controller import upload_certificate

        mock_cert_manager = MagicMock()
        mock_cert_manager.load.return_value = False

        with patch('modules.government_integrations.controllers.certificate_controller.CertificateManager') as MockManager:
            MockManager.return_value = mock_cert_manager

            with pytest.raises(HTTPException) as exc_info:
                await upload_certificate(
                    file=mock_file,
                    password="senha_errada",
                    store=mock_store
                )

            assert exc_info.value.status_code == 400
            assert "Verifique a senha" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_validate_certificate_success(self, mock_file, mock_certificate_info):
        """Testa validacao de certificado com sucesso."""
        from modules.government_integrations.controllers.certificate_controller import validate_certificate

        mock_cert_manager = MagicMock()
        mock_cert_manager.load.return_value = True
        mock_cert_manager.validate.return_value = (True, "Certificado valido")
        mock_cert_manager.get_info.return_value = mock_certificate_info

        with patch('modules.government_integrations.controllers.certificate_controller.CertificateManager') as MockManager:
            MockManager.return_value = mock_cert_manager

            result = await validate_certificate(
                file=mock_file,
                password="senha123"
            )

            assert result.is_valid is True
            assert result.subject == mock_certificate_info.subject_cn

    @pytest.mark.asyncio
    async def test_validate_certificate_expired(self, mock_file, mock_certificate_info_expired):
        """Testa validacao de certificado expirado."""
        from modules.government_integrations.controllers.certificate_controller import validate_certificate

        mock_cert_manager = MagicMock()
        mock_cert_manager.load.return_value = True
        mock_cert_manager.validate.return_value = (False, "Certificado expirado")
        mock_cert_manager.get_info.return_value = mock_certificate_info_expired

        with patch('modules.government_integrations.controllers.certificate_controller.CertificateManager') as MockManager:
            MockManager.return_value = mock_cert_manager

            result = await validate_certificate(
                file=mock_file,
                password="senha123"
            )

            assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_validate_certificate_expiring_soon_warning(self, mock_file, mock_certificate_info_expiring_soon):
        """Testa aviso de certificado expirando em breve."""
        from modules.government_integrations.controllers.certificate_controller import validate_certificate

        mock_cert_manager = MagicMock()
        mock_cert_manager.load.return_value = True
        mock_cert_manager.validate.return_value = (True, "Certificado valido")
        mock_cert_manager.get_info.return_value = mock_certificate_info_expiring_soon

        with patch('modules.government_integrations.controllers.certificate_controller.CertificateManager') as MockManager:
            MockManager.return_value = mock_cert_manager

            result = await validate_certificate(
                file=mock_file,
                password="senha123"
            )

            assert result.is_valid is True
            assert len(result.warnings) > 0
            assert any("vence" in w.lower() for w in result.warnings)

    @pytest.mark.asyncio
    async def test_list_certificates_empty(self, mock_store):
        """Testa listagem de certificados vazia."""
        from modules.government_integrations.controllers.certificate_controller import list_certificates

        mock_store.list_all.return_value = []

        result = await list_certificates(store=mock_store)

        assert result.total == 0
        assert result.certificates == []

    @pytest.mark.asyncio
    async def test_list_certificates_with_items(self, mock_store, mock_certificate_info):
        """Testa listagem com certificados."""
        from modules.government_integrations.controllers.certificate_controller import list_certificates

        mock_manager = MagicMock()
        mock_manager.get_info.return_value = mock_certificate_info
        mock_manager.validate.return_value = (True, "OK")

        mock_store.list_all.return_value = [
            ("cert1", mock_manager),
            ("cert2", mock_manager),
        ]

        result = await list_certificates(store=mock_store)

        assert result.total == 2
        assert len(result.certificates) == 2

    @pytest.mark.asyncio
    async def test_get_certificate_success(self, mock_store, mock_certificate_info):
        """Testa obtencao de certificado especifico."""
        from modules.government_integrations.controllers.certificate_controller import get_certificate

        mock_manager = MagicMock()
        mock_manager.get_info.return_value = mock_certificate_info
        mock_manager.validate.return_value = (True, "OK")

        mock_store.get.return_value = mock_manager

        result = await get_certificate(
            certificate_id="cert_123",
            store=mock_store
        )

        assert result.certificate_id == "cert_123"
        assert result.subject_cn == mock_certificate_info.subject_cn

    @pytest.mark.asyncio
    async def test_get_certificate_not_found(self, mock_store):
        """Testa obtencao de certificado inexistente."""
        from modules.government_integrations.controllers.certificate_controller import get_certificate

        mock_store.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_certificate(
                certificate_id="nonexistent",
                store=mock_store
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_certificate_success(self, mock_store):
        """Testa exclusao de certificado com sucesso."""
        from modules.government_integrations.controllers.certificate_controller import delete_certificate

        mock_store.get.return_value = MagicMock()
        mock_store.remove.return_value = None

        result = await delete_certificate(
            certificate_id="cert_123",
            store=mock_store
        )

        assert result.success is True
        mock_store.remove.assert_called_once_with("cert_123")

    @pytest.mark.asyncio
    async def test_delete_certificate_not_found(self, mock_store):
        """Testa exclusao de certificado inexistente."""
        from modules.government_integrations.controllers.certificate_controller import delete_certificate

        mock_store.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await delete_certificate(
                certificate_id="nonexistent",
                store=mock_store
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_public_key_success(self, mock_store):
        """Testa obtencao de chave publica."""
        from modules.government_integrations.controllers.certificate_controller import get_public_key

        mock_manager = MagicMock()
        mock_manager.get_certificate_base64.return_value = "MOCK_CERT_BASE64=="

        mock_store.get.return_value = mock_manager

        result = await get_public_key(
            certificate_id="cert_123",
            store=mock_store
        )

        assert result["certificate_id"] == "cert_123"
        assert result["public_certificate"] == "MOCK_CERT_BASE64=="
        assert result["format"] == "X509 DER Base64"

    @pytest.mark.asyncio
    async def test_get_public_key_not_found(self, mock_store):
        """Testa obtencao de chave publica de certificado inexistente."""
        from modules.government_integrations.controllers.certificate_controller import get_public_key

        mock_store.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_public_key(
                certificate_id="nonexistent",
                store=mock_store
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_test_signature_success(self, mock_store):
        """Testa endpoint de teste de assinatura."""
        from modules.government_integrations.controllers.certificate_controller import test_signature

        mock_manager = MagicMock()
        mock_manager.sign_data.return_value = b"mock_signature"
        mock_manager.verify_signature.return_value = True

        mock_store.get.return_value = mock_manager

        result = await test_signature(
            certificate_id="cert_123",
            data="dados_para_assinar",
            store=mock_store
        )

        assert result["certificate_id"] == "cert_123"
        assert result["original_data"] == "dados_para_assinar"
        assert result["signature_verified"] is True
        assert "signature" in result

    @pytest.mark.asyncio
    async def test_test_signature_not_found(self, mock_store):
        """Testa teste de assinatura com certificado inexistente."""
        from modules.government_integrations.controllers.certificate_controller import test_signature

        mock_store.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await test_signature(
                certificate_id="nonexistent",
                data="test",
                store=mock_store
            )

        assert exc_info.value.status_code == 404


# =============================================================================
# TestEnums - Testes para enumeracoes
# =============================================================================

class TestEnums:
    """Testes para enumeracoes do modulo."""

    def test_certificate_type_values(self):
        """Testa valores de CertificateType."""
        assert CertificateType.A1.value == "A1"
        assert CertificateType.A3.value == "A3"

    def test_certificate_status_values(self):
        """Testa valores de CertificateStatus."""
        assert CertificateStatus.VALID.value == "valid"
        assert CertificateStatus.EXPIRED.value == "expired"
        assert CertificateStatus.EXPIRING_SOON.value == "expiring_soon"
        assert CertificateStatus.REVOKED.value == "revoked"
        assert CertificateStatus.INVALID.value == "invalid"

    def test_signature_type_values(self):
        """Testa valores de SignatureType."""
        assert SignatureType.ESOCIAL.value == "esocial"
        assert SignatureType.NFE.value == "nfe"
        assert SignatureType.NFCE.value == "nfce"
        assert SignatureType.CTE.value == "cte"
        assert SignatureType.MDFE.value == "mdfe"
        assert SignatureType.GENERIC.value == "generic"

    def test_digest_method_values(self):
        """Testa valores de DigestMethod."""
        assert "sha1" in DigestMethod.SHA1.value.lower()
        assert "sha256" in DigestMethod.SHA256.value.lower()

    def test_signature_method_values(self):
        """Testa valores de SignatureMethod."""
        assert "rsa-sha1" in SignatureMethod.RSA_SHA1.value.lower()
        assert "rsa-sha256" in SignatureMethod.RSA_SHA256.value.lower()

    def test_canonicalization_method_values(self):
        """Testa valores de CanonicalizationMethod."""
        assert "c14n" in CanonicalizationMethod.C14N.value.lower()
        assert "exc" in CanonicalizationMethod.C14N_EXCLUSIVE.value.lower()

    def test_transform_method_values(self):
        """Testa valores de TransformMethod."""
        assert "enveloped" in TransformMethod.ENVELOPED.value.lower()


# =============================================================================
# TestNamespaces - Testes para namespaces XML
# =============================================================================

class TestNamespaces:
    """Testes para namespaces XML."""

    def test_xmldsig_namespace(self):
        """Testa namespace XMLDSig."""
        assert NAMESPACES['ds'] == 'http://www.w3.org/2000/09/xmldsig#'

    def test_esocial_namespace(self):
        """Testa namespace eSocial."""
        assert 'esocial.gov.br' in NAMESPACES['esocial']

    def test_nfe_namespace(self):
        """Testa namespace NF-e."""
        assert 'portalfiscal.inf.br/nfe' in NAMESPACES['nfe']

    def test_cte_namespace(self):
        """Testa namespace CT-e."""
        assert 'portalfiscal.inf.br/cte' in NAMESPACES['cte']

    def test_mdfe_namespace(self):
        """Testa namespace MDF-e."""
        assert 'portalfiscal.inf.br/mdfe' in NAMESPACES['mdfe']


# =============================================================================
# TestIntegration - Testes de integracao
# =============================================================================

class TestIntegration:
    """Testes de integracao do modulo de certificados."""

    @pytest.fixture
    def mock_cert_manager(self, mock_certificate_info):
        """Fixture para CertificateManager completo mockado."""
        manager = MagicMock(spec=CertificateManager)
        manager._loaded = True
        manager.info = mock_certificate_info
        manager.get_certificate_base64.return_value = base64.b64encode(b"MOCK_CERT").decode()
        manager.sign_data.return_value = b"mock_signature_bytes"
        manager.verify_signature.return_value = True
        manager.validate.return_value = (True, "Certificado valido")
        return manager

    def test_sign_and_verify_flow(self, mock_cert_manager, sample_xml_content):
        """Testa fluxo completo de assinatura e verificacao."""
        signer = XMLSigner(mock_cert_manager)

        # Assinar
        signed_xml = signer.sign(
            sample_xml_content,
            reference_uri="#DOC123456"
        )

        # Verificar estrutura
        assert "<?xml" in signed_xml
        assert "Signature" in signed_xml
        assert "SignedInfo" in signed_xml
        assert "SignatureValue" in signed_xml
        assert "DigestValue" in signed_xml
        assert "X509Certificate" in signed_xml

    def test_multiple_signature_types(self, mock_cert_manager):
        """Testa configuracoes para diferentes tipos de assinatura."""
        for sig_type in [SignatureType.ESOCIAL, SignatureType.NFE, SignatureType.CTE]:
            config = DEFAULT_CONFIGS.get(sig_type)
            assert config is not None
            assert config.signature_type == sig_type
            assert config.digest_method in [DigestMethod.SHA1, DigestMethod.SHA256]
            assert config.signature_method in [SignatureMethod.RSA_SHA1, SignatureMethod.RSA_SHA256]

    def test_certificate_lifecycle(self, mock_certificate_info):
        """Testa ciclo de vida do certificado."""
        store = CertificateStore(storage_path="/tmp/test_lifecycle")

        # Criar um manager pre-carregado (mockado)
        manager = MagicMock(spec=CertificateManager)
        manager.info = mock_certificate_info
        manager._loaded = True
        manager._info = mock_certificate_info

        # Adicionar diretamente ao store
        store.add("test_cert", manager)

        # Verificar existencia
        assert store.get_certificate("test_cert") is not None

        # Listar usando o metodo que retorna dicionario
        certs = store._certificates
        assert "test_cert" in certs

        # Remover
        with patch.object(store, '_delete_certificate_file'):
            result = store.remove_certificate("test_cert")
            assert result is True

        # Verificar remocao
        assert store.get_certificate("test_cert") is None
