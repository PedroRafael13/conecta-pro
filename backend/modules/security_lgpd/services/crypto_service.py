"""
Service de Criptografia LGPD - Consolidado
==========================================

Gerenciador central de criptografia com suporte a AES-256, RSA e Fernet.
Migrado de 01_security_lgpd/encryption/crypto_manager.py

Compliance: LGPD Art. 46 - Medidas de Segurança
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import secrets
import logging
import json

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(str, Enum):
    """Algoritmos de criptografia suportados."""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    RSA_OAEP = "rsa-oaep"
    FERNET = "fernet"
    CHACHA20_POLY1305 = "chacha20-poly1305"


class KeyType(str, Enum):
    """Tipos de chaves criptográficas."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    DERIVED = "derived"


class CryptoError(Exception):
    """Exceção base para erros de criptografia."""

    def __init__(self, message: str, algorithm: Optional[str] = None):
        self.message = message
        self.algorithm = algorithm
        super().__init__(self.message)


class EncryptionError(CryptoError):
    """Erro durante criptografia."""
    pass


class DecryptionError(CryptoError):
    """Erro durante descriptografia."""
    pass


class KeyGenerationError(CryptoError):
    """Erro relacionado a chaves."""
    pass


@dataclass
class EncryptionResult:
    """Resultado de uma operação de criptografia."""
    ciphertext: bytes
    algorithm: EncryptionAlgorithm
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    key_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "algorithm": self.algorithm.value,
            "iv": base64.b64encode(self.iv).decode() if self.iv else None,
            "tag": base64.b64encode(self.tag).decode() if self.tag else None,
            "key_id": self.key_id,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EncryptionResult":
        """Reconstrói a partir de dicionário."""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            algorithm=EncryptionAlgorithm(data["algorithm"]),
            iv=base64.b64decode(data["iv"]) if data.get("iv") else None,
            tag=base64.b64decode(data["tag"]) if data.get("tag") else None,
            key_id=data.get("key_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class CryptoConfig(BaseModel):
    """Configuração do gerenciador de criptografia."""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_derivation_iterations: int = Field(default=100000, ge=10000)
    rsa_key_size: int = Field(default=4096, ge=2048)
    enable_key_rotation: bool = True
    key_rotation_days: int = Field(default=90, ge=30)
    enable_audit_logging: bool = True

    @validator("rsa_key_size")
    def validate_rsa_key_size(cls, v):
        if v not in [2048, 3072, 4096]:
            raise ValueError("RSA key size deve ser 2048, 3072 ou 4096")
        return v


class CryptoManagerInterface(ABC):
    """Interface abstrata para operações criptográficas."""

    @abstractmethod
    def encrypt(self, plaintext: bytes, key: bytes, algorithm: EncryptionAlgorithm) -> EncryptionResult:
        """Criptografa dados."""
        pass

    @abstractmethod
    def decrypt(self, encrypted: EncryptionResult, key: bytes) -> bytes:
        """Descriptografa dados."""
        pass

    @abstractmethod
    def generate_key(self, algorithm: EncryptionAlgorithm) -> bytes:
        """Gera nova chave."""
        pass


class CryptoService(CryptoManagerInterface):
    """
    Gerenciador central de criptografia para compliance LGPD.

    Suporta múltiplos algoritmos de criptografia com configuração
    flexível e logging de auditoria integrado.

    Example:
        >>> service = CryptoService()
        >>> key = service.generate_key(EncryptionAlgorithm.AES_256_GCM)
        >>> result = service.encrypt(b"dados sensíveis", key)
        >>> plaintext = service.decrypt(result, key)
    """

    def __init__(self, config: Optional[CryptoConfig] = None):
        """
        Inicializa o gerenciador de criptografia.

        Args:
            config: Configuração opcional. Usa defaults se não fornecida.
        """
        self.config = config or CryptoConfig()
        self._backend = default_backend()
        self._rsa_key_cache: Dict[str, Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]] = {}
        logger.info("CryptoService inicializado com algoritmo padrão: %s",
                   self.config.default_algorithm.value)

    def generate_key(self, algorithm: Optional[EncryptionAlgorithm] = None) -> bytes:
        """
        Gera uma nova chave criptográfica segura.

        Args:
            algorithm: Algoritmo para o qual gerar a chave. Usa default se não especificado.

        Returns:
            bytes: Chave gerada.

        Raises:
            KeyGenerationError: Se algoritmo não suportado.
        """
        algo = algorithm or self.config.default_algorithm

        try:
            if algo in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key = secrets.token_bytes(32)  # 256 bits
            elif algo == EncryptionAlgorithm.FERNET:
                key = Fernet.generate_key()
            elif algo == EncryptionAlgorithm.CHACHA20_POLY1305:
                key = secrets.token_bytes(32)  # 256 bits
            elif algo == EncryptionAlgorithm.RSA_OAEP:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=self.config.rsa_key_size,
                    backend=self._backend
                )
                key = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                raise KeyGenerationError(f"Algoritmo não suportado: {algo}", algo.value)

            if self.config.enable_audit_logging:
                logger.info("Chave gerada para algoritmo: %s", algo.value)

            return key

        except Exception as e:
            logger.error("Erro ao gerar chave para %s: %s", algo.value, str(e))
            raise KeyGenerationError(f"Falha ao gerar chave: {str(e)}", algo.value if algo else None)

    def encrypt(
        self,
        plaintext: Union[bytes, str],
        key: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Criptografa dados usando o algoritmo especificado.

        Args:
            plaintext: Dados a criptografar (bytes ou string UTF-8).
            key: Chave de criptografia.
            algorithm: Algoritmo a usar. Usa default se não especificado.
            associated_data: Dados adicionais autenticados (para GCM/AEAD).

        Returns:
            EncryptionResult: Resultado com ciphertext e metadados.

        Raises:
            EncryptionError: Se falhar a criptografia.
        """
        algo = algorithm or self.config.default_algorithm

        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")

        try:
            if algo == EncryptionAlgorithm.AES_256_GCM:
                return self._encrypt_aes_gcm(plaintext, key, associated_data)
            elif algo == EncryptionAlgorithm.AES_256_CBC:
                return self._encrypt_aes_cbc(plaintext, key)
            elif algo == EncryptionAlgorithm.FERNET:
                return self._encrypt_fernet(plaintext, key)
            elif algo == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._encrypt_chacha20(plaintext, key, associated_data)
            elif algo == EncryptionAlgorithm.RSA_OAEP:
                return self._encrypt_rsa(plaintext, key)
            else:
                raise EncryptionError(f"Algoritmo não suportado: {algo}", algo.value)

        except EncryptionError:
            raise
        except Exception as e:
            logger.error("Erro de criptografia com %s: %s", algo.value, str(e))
            raise EncryptionError(f"Falha na criptografia: {str(e)}", algo.value)

    def decrypt(
        self,
        encrypted: Union[EncryptionResult, Dict[str, Any]],
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Descriptografa dados.

        Args:
            encrypted: Resultado de criptografia ou dicionário equivalente.
            key: Chave de descriptografia.
            associated_data: Dados adicionais autenticados (para GCM/AEAD).

        Returns:
            bytes: Dados descriptografados.

        Raises:
            DecryptionError: Se falhar a descriptografia.
        """
        if isinstance(encrypted, dict):
            encrypted = EncryptionResult.from_dict(encrypted)

        algo = encrypted.algorithm

        try:
            if algo == EncryptionAlgorithm.AES_256_GCM:
                return self._decrypt_aes_gcm(encrypted, key, associated_data)
            elif algo == EncryptionAlgorithm.AES_256_CBC:
                return self._decrypt_aes_cbc(encrypted, key)
            elif algo == EncryptionAlgorithm.FERNET:
                return self._decrypt_fernet(encrypted, key)
            elif algo == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._decrypt_chacha20(encrypted, key, associated_data)
            elif algo == EncryptionAlgorithm.RSA_OAEP:
                return self._decrypt_rsa(encrypted, key)
            else:
                raise DecryptionError(f"Algoritmo não suportado: {algo}", algo.value)

        except DecryptionError:
            raise
        except InvalidToken:
            raise DecryptionError("Token inválido ou chave incorreta", algo.value)
        except Exception as e:
            logger.error("Erro de descriptografia com %s: %s", algo.value, str(e))
            raise DecryptionError(f"Falha na descriptografia: {str(e)}", algo.value)

    def _encrypt_aes_gcm(
        self,
        plaintext: bytes,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """Criptografa usando AES-256-GCM (authenticated encryption)."""
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self._backend)
        encryptor = cipher.encryptor()

        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            iv=iv,
            tag=encryptor.tag
        )

    def _decrypt_aes_gcm(
        self,
        encrypted: EncryptionResult,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """Descriptografa usando AES-256-GCM."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(encrypted.iv, encrypted.tag),
            backend=self._backend
        )
        decryptor = cipher.decryptor()

        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        return decryptor.update(encrypted.ciphertext) + decryptor.finalize()

    def _encrypt_aes_cbc(self, plaintext: bytes, key: bytes) -> EncryptionResult:
        """Criptografa usando AES-256-CBC com PKCS7 padding."""
        iv = secrets.token_bytes(16)

        block_size = 16
        padding_length = block_size - (len(plaintext) % block_size)
        padded_plaintext = plaintext + bytes([padding_length] * padding_length)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self._backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            iv=iv
        )

    def _decrypt_aes_cbc(self, encrypted: EncryptionResult, key: bytes) -> bytes:
        """Descriptografa usando AES-256-CBC."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(encrypted.iv),
            backend=self._backend
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(encrypted.ciphertext) + decryptor.finalize()

        padding_length = padded_plaintext[-1]
        return padded_plaintext[:-padding_length]

    def _encrypt_fernet(self, plaintext: bytes, key: bytes) -> EncryptionResult:
        """Criptografa usando Fernet (AES-128-CBC + HMAC)."""
        f = Fernet(key)
        ciphertext = f.encrypt(plaintext)

        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.FERNET
        )

    def _decrypt_fernet(self, encrypted: EncryptionResult, key: bytes) -> bytes:
        """Descriptografa usando Fernet."""
        f = Fernet(key)
        return f.decrypt(encrypted.ciphertext)

    def _encrypt_chacha20(
        self,
        plaintext: bytes,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """Criptografa usando ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        nonce = secrets.token_bytes(12)
        chacha = ChaCha20Poly1305(key)
        ciphertext = chacha.encrypt(nonce, plaintext, associated_data)

        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            iv=nonce
        )

    def _decrypt_chacha20(
        self,
        encrypted: EncryptionResult,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """Descriptografa usando ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        chacha = ChaCha20Poly1305(key)
        return chacha.decrypt(encrypted.iv, encrypted.ciphertext, associated_data)

    def _encrypt_rsa(self, plaintext: bytes, key: bytes) -> EncryptionResult:
        """Criptografa usando RSA-OAEP (para dados pequenos)."""
        private_key = serialization.load_pem_private_key(
            key, password=None, backend=self._backend
        )
        public_key = private_key.public_key()

        max_size = (self.config.rsa_key_size // 8) - 66
        if len(plaintext) > max_size:
            raise EncryptionError(
                f"Dados muito grandes para RSA ({len(plaintext)} > {max_size}). "
                "Use criptografia híbrida para dados maiores.",
                EncryptionAlgorithm.RSA_OAEP.value
            )

        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return EncryptionResult(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.RSA_OAEP
        )

    def _decrypt_rsa(self, encrypted: EncryptionResult, key: bytes) -> bytes:
        """Descriptografa usando RSA-OAEP."""
        private_key = serialization.load_pem_private_key(
            key, password=None, backend=self._backend
        )

        return private_key.decrypt(
            encrypted.ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def derive_key(
        self,
        password: Union[str, bytes],
        salt: Optional[bytes] = None,
        key_length: int = 32
    ) -> Tuple[bytes, bytes]:
        """
        Deriva uma chave a partir de uma senha usando PBKDF2.

        Args:
            password: Senha para derivar chave.
            salt: Salt aleatório (gerado se não fornecido).
            key_length: Tamanho da chave em bytes.

        Returns:
            Tuple[bytes, bytes]: (chave derivada, salt usado).
        """
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        if isinstance(password, str):
            password = password.encode("utf-8")

        if salt is None:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=self.config.key_derivation_iterations,
            backend=self._backend
        )

        key = kdf.derive(password)
        return key, salt

    def generate_hmac(self, data: bytes, key: bytes) -> bytes:
        """
        Gera HMAC-SHA256 para verificação de integridade.

        Args:
            data: Dados para gerar HMAC.
            key: Chave HMAC.

        Returns:
            bytes: HMAC gerado.
        """
        return hmac.new(key, data, hashlib.sha256).digest()

    def verify_hmac(self, data: bytes, key: bytes, expected_hmac: bytes) -> bool:
        """
        Verifica HMAC-SHA256.

        Args:
            data: Dados originais.
            key: Chave HMAC.
            expected_hmac: HMAC esperado.

        Returns:
            bool: True se HMAC válido.
        """
        computed = self.generate_hmac(data, key)
        return hmac.compare_digest(computed, expected_hmac)

    def hash_data(self, data: Union[bytes, str], algorithm: str = "sha256") -> str:
        """
        Gera hash de dados.

        Args:
            data: Dados para hash.
            algorithm: Algoritmo (sha256, sha384, sha512).

        Returns:
            str: Hash em hexadecimal.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha384":
            return hashlib.sha384(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        else:
            raise ValueError(f"Algoritmo de hash não suportado: {algorithm}")

    def encrypt_for_storage(
        self,
        data: Any,
        key: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None
    ) -> str:
        """
        Criptografa dados para armazenamento seguro (retorna string base64).

        Args:
            data: Dados a criptografar (serializável em JSON).
            key: Chave de criptografia.
            algorithm: Algoritmo a usar.

        Returns:
            str: Dados criptografados em base64.
        """
        json_data = json.dumps(data, default=str, ensure_ascii=False)
        result = self.encrypt(json_data.encode("utf-8"), key, algorithm)
        return base64.b64encode(json.dumps(result.to_dict()).encode()).decode()

    def decrypt_from_storage(self, encrypted_string: str, key: bytes) -> Any:
        """
        Descriptografa dados de armazenamento.

        Args:
            encrypted_string: String base64 com dados criptografados.
            key: Chave de descriptografia.

        Returns:
            Any: Dados originais deserializados.
        """
        encrypted_dict = json.loads(base64.b64decode(encrypted_string))
        decrypted = self.decrypt(encrypted_dict, key)
        return json.loads(decrypted.decode("utf-8"))


# Instância singleton para uso global
_default_service: Optional[CryptoService] = None


def get_crypto_service(config: Optional[CryptoConfig] = None) -> CryptoService:
    """
    Retorna instância singleton do CryptoService.

    Args:
        config: Configuração opcional (usada apenas na primeira chamada).

    Returns:
        CryptoService: Instância do gerenciador.
    """
    global _default_service
    if _default_service is None:
        _default_service = CryptoService(config)
    return _default_service
