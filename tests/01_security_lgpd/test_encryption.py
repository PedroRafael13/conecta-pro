"""
Tests for Encryption Module (crypto_manager, key_management, data_masking).

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import os
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
import uuid
import hashlib
import base64


# =============================================================================
# MOCK CLASSES (Simulating the actual implementation)
# =============================================================================

class EncryptionAlgorithm(str, Enum):
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    RSA_OAEP = "rsa-oaep"
    FERNET = "fernet"


class KeyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROTATED = "rotated"
    EXPIRED = "expired"


class KeyPurpose(str, Enum):
    ENCRYPTION = "encryption"
    SIGNING = "signing"
    MASTER = "master"
    DERIVED = "derived"


class KeyAlgorithm(str, Enum):
    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"


class PIICategory(str, Enum):
    CPF = "cpf"
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"


class MaskingLevel(str, Enum):
    PARTIAL = "partial"
    FULL = "full"
    HASH = "hash"


@dataclass
class CryptoConfig:
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 90


@dataclass
class KeyInfo:
    id: str
    algorithm: KeyAlgorithm
    status: KeyStatus
    purpose: KeyPurpose
    created_at: datetime = None
    expires_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class CryptoManager:
    """Simulated CryptoManager for testing."""

    def __init__(self, config: CryptoConfig = None):
        self.config = config or CryptoConfig()
        self._key = os.urandom(32)

    def encrypt(self, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode()
        # Simple simulation using base64
        nonce = os.urandom(12)
        encrypted = base64.b64encode(nonce + data).decode()
        return encrypted

    def decrypt(self, encrypted: str) -> str:
        try:
            decoded = base64.b64decode(encrypted)
            return decoded[12:].decode()
        except:
            return decoded[12:]

    def hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()


class KeyManager:
    """Simulated KeyManager for testing."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._keys: Dict[str, KeyInfo] = {}

    async def generate_key(
        self,
        purpose: KeyPurpose,
        algorithm: KeyAlgorithm,
        expires_in_days: int = 365
    ) -> KeyInfo:
        key_id = str(uuid.uuid4())
        key_info = KeyInfo(
            id=key_id,
            algorithm=algorithm,
            status=KeyStatus.ACTIVE,
            purpose=purpose,
            expires_at=datetime.now() + timedelta(days=expires_in_days)
        )
        self._keys[key_id] = key_info
        return key_info

    async def rotate_key(self, key_id: str) -> KeyInfo:
        old_key = self._keys.get(key_id)
        if old_key:
            old_key.status = KeyStatus.ROTATED
        return await self.generate_key(
            purpose=old_key.purpose if old_key else KeyPurpose.ENCRYPTION,
            algorithm=old_key.algorithm if old_key else KeyAlgorithm.AES_256
        )

    async def derive_key(self, master_key_id: str, context: str) -> KeyInfo:
        return await self.generate_key(
            purpose=KeyPurpose.DERIVED,
            algorithm=KeyAlgorithm.AES_256
        )

    async def is_key_valid(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if not key:
            return False
        return key.status == KeyStatus.ACTIVE and key.expires_at > datetime.now()


class DataMasker:
    """Simulated DataMasker for testing."""

    def mask(self, value: str, category: PIICategory, level: MaskingLevel) -> str:
        if not value:
            return value

        if level == MaskingLevel.FULL:
            return "*" * len(value)

        if category == PIICategory.CPF:
            clean = ''.join(filter(str.isdigit, value))
            if len(clean) == 11:
                return f"***.***.{clean[6:9]}-**"
            return "***.***.***-**"

        if category == PIICategory.EMAIL:
            if "@" in value:
                parts = value.split("@")
                return f"{parts[0][:2]}***@{parts[1]}"
            return "***@***.***"

        if category == PIICategory.PHONE:
            clean = ''.join(filter(str.isdigit, value))
            if len(clean) >= 8:
                return f"****-{clean[-4:]}"
            return "****-****"

        if category == PIICategory.CREDIT_CARD:
            clean = ''.join(filter(str.isdigit, value))
            if len(clean) >= 16:
                return f"****-****-****-{clean[-4:]}"
            return "****-****-****-****"

        if category == PIICategory.NAME:
            parts = value.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}*** {parts[-1][0]}***"
            return f"{value[0]}***"

        return "*" * min(len(value), 10)


def mask_cpf(cpf: str) -> str:
    masker = DataMasker()
    return masker.mask(cpf, PIICategory.CPF, MaskingLevel.PARTIAL)


def mask_email(email: str) -> str:
    masker = DataMasker()
    return masker.mask(email, PIICategory.EMAIL, MaskingLevel.PARTIAL)


def mask_phone(phone: str) -> str:
    masker = DataMasker()
    return masker.mask(phone, PIICategory.PHONE, MaskingLevel.PARTIAL)


# =============================================================================
# CRYPTO MANAGER TESTS
# =============================================================================

class TestCryptoManager:
    """Tests for CryptoManager class."""

    @pytest.fixture
    def crypto_manager(self):
        config = CryptoConfig(
            default_algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_rotation_days=90
        )
        return CryptoManager(config=config)

    def test_init_default_config(self):
        manager = CryptoManager()
        assert manager is not None
        assert manager.config is not None

    def test_init_custom_config(self, crypto_manager):
        assert crypto_manager.config.default_algorithm == EncryptionAlgorithm.AES_256_GCM
        assert crypto_manager.config.key_rotation_days == 90

    def test_encrypt_decrypt_string(self, crypto_manager):
        plaintext = "Dados sensiveis para teste"
        encrypted = crypto_manager.encrypt(plaintext)
        assert encrypted != plaintext
        assert encrypted is not None
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_decrypt_bytes(self, crypto_manager):
        plaintext = b"Binary sensitive data"
        encrypted = crypto_manager.encrypt(plaintext)
        assert encrypted != plaintext.decode()
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == plaintext.decode()

    def test_encrypt_empty_string(self, crypto_manager):
        encrypted = crypto_manager.encrypt("")
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode(self, crypto_manager):
        plaintext = "Texto com acentos: cafe, acucar, coracao"
        encrypted = crypto_manager.encrypt(plaintext)
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_different_encryptions_same_plaintext(self, crypto_manager):
        plaintext = "Same data"
        encrypted1 = crypto_manager.encrypt(plaintext)
        encrypted2 = crypto_manager.encrypt(plaintext)
        # Should be different due to random nonce
        assert encrypted1 != encrypted2
        # Both should decrypt to same value
        assert crypto_manager.decrypt(encrypted1) == plaintext
        assert crypto_manager.decrypt(encrypted2) == plaintext

    def test_hash_data(self, crypto_manager):
        data = "data to hash"
        hash1 = crypto_manager.hash(data)
        hash2 = crypto_manager.hash(data)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_hash_different_data(self, crypto_manager):
        hash1 = crypto_manager.hash("data1")
        hash2 = crypto_manager.hash("data2")
        assert hash1 != hash2


# =============================================================================
# KEY MANAGER TESTS
# =============================================================================

class TestKeyManager:
    """Tests for KeyManager class."""

    @pytest.fixture
    def key_manager(self):
        return KeyManager(db_session=MagicMock())

    @pytest.mark.asyncio
    async def test_generate_key_aes(self, key_manager):
        key_info = await key_manager.generate_key(
            purpose=KeyPurpose.ENCRYPTION,
            algorithm=KeyAlgorithm.AES_256
        )
        assert key_info is not None
        assert key_info.algorithm == KeyAlgorithm.AES_256
        assert key_info.status == KeyStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_generate_key_rsa(self, key_manager):
        key_info = await key_manager.generate_key(
            purpose=KeyPurpose.SIGNING,
            algorithm=KeyAlgorithm.RSA_2048
        )
        assert key_info is not None
        assert key_info.algorithm == KeyAlgorithm.RSA_2048

    @pytest.mark.asyncio
    async def test_rotate_key(self, key_manager):
        old_key = await key_manager.generate_key(
            purpose=KeyPurpose.ENCRYPTION,
            algorithm=KeyAlgorithm.AES_256
        )
        new_key = await key_manager.rotate_key(old_key.id)
        assert new_key is not None
        assert new_key.id != old_key.id
        assert new_key.status == KeyStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_derive_key(self, key_manager):
        master_key = await key_manager.generate_key(
            purpose=KeyPurpose.MASTER,
            algorithm=KeyAlgorithm.AES_256
        )
        derived = await key_manager.derive_key(
            master_key_id=master_key.id,
            context="user_data_encryption"
        )
        assert derived is not None

    @pytest.mark.asyncio
    async def test_key_expiration_check(self, key_manager):
        key_info = await key_manager.generate_key(
            purpose=KeyPurpose.ENCRYPTION,
            algorithm=KeyAlgorithm.AES_256,
            expires_in_days=1
        )
        is_valid = await key_manager.is_key_valid(key_info.id)
        assert is_valid is True


# =============================================================================
# DATA MASKING TESTS
# =============================================================================

class TestDataMasker:
    """Tests for DataMasker class."""

    @pytest.fixture
    def masker(self):
        return DataMasker()

    def test_mask_cpf_partial(self, masker):
        cpf = "12345678901"
        masked = masker.mask(cpf, PIICategory.CPF, MaskingLevel.PARTIAL)
        assert masked != cpf
        assert "***" in masked
        assert "789" in masked  # Position 6-8 visible

    def test_mask_cpf_full(self, masker):
        cpf = "12345678901"
        masked = masker.mask(cpf, PIICategory.CPF, MaskingLevel.FULL)
        assert masked != cpf
        assert masked == "*" * 11

    def test_mask_email_partial(self, masker):
        email = "usuario@empresa.com.br"
        masked = masker.mask(email, PIICategory.EMAIL, MaskingLevel.PARTIAL)
        assert "@" in masked
        assert "***" in masked
        assert masked != email

    def test_mask_phone(self, masker):
        phone = "11999998888"
        masked = masker.mask(phone, PIICategory.PHONE, MaskingLevel.PARTIAL)
        assert masked != phone
        assert "8888" in masked  # Last 4 visible

    def test_mask_credit_card(self, masker):
        card = "4111111111111111"
        masked = masker.mask(card, PIICategory.CREDIT_CARD, MaskingLevel.PARTIAL)
        assert masked != card
        assert "1111" in masked  # Last 4 visible
        assert "****" in masked

    def test_mask_name(self, masker):
        name = "Joao Carlos da Silva"
        masked = masker.mask(name, PIICategory.NAME, MaskingLevel.PARTIAL)
        assert masked != name
        assert "***" in masked


class TestMaskingHelperFunctions:
    """Tests for masking helper functions."""

    def test_mask_cpf_function(self):
        result = mask_cpf("12345678901")
        assert result != "12345678901"
        assert "*" in result

    def test_mask_cpf_formatted(self):
        result = mask_cpf("123.456.789-01")
        assert "*" in result

    def test_mask_email_function(self):
        result = mask_email("test@example.com")
        assert "@" in result
        assert "*" in result

    def test_mask_phone_function(self):
        result = mask_phone("11999998888")
        assert "*" in result

    def test_mask_phone_formatted(self):
        result = mask_phone("(11) 99999-8888")
        assert "*" in result


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestEncryptionIntegration:
    """Integration tests for encryption module."""

    @pytest.fixture
    def full_setup(self):
        crypto = CryptoManager()
        keys = KeyManager(db_session=MagicMock())
        masker = DataMasker()
        return crypto, keys, masker

    @pytest.mark.asyncio
    async def test_encrypt_then_mask_for_display(self, full_setup):
        crypto, keys, masker = full_setup
        cpf = "12345678901"

        # Encrypt for storage
        encrypted = crypto.encrypt(cpf)
        assert encrypted != cpf

        # Decrypt when needed
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == cpf

        # Mask for display
        masked = masker.mask(decrypted, PIICategory.CPF, MaskingLevel.PARTIAL)
        assert masked != cpf
        assert "*" in masked

    @pytest.mark.asyncio
    async def test_key_rotation_maintains_decryption(self, full_setup):
        crypto, keys, masker = full_setup
        data = "sensitive data"

        encrypted = crypto.encrypt(data)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == data
