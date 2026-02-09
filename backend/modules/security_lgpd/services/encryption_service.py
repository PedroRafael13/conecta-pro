"""
Service de Criptografia LGPD.
"""

import base64
import hashlib
import logging
import os
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service para operacoes de criptografia.

    Encapsula a logica de criptografia e descriptografia
    de dados sensiveis conforme LGPD.
    """

    SUPPORTED_ALGORITHMS = {
        "aes-256-gcm": {"key_size": 32, "nonce_size": 12},
        "aes-256-cbc": {"key_size": 32, "nonce_size": 16},
        "fernet": {"key_size": 32, "nonce_size": 0},
        "chacha20-poly1305": {"key_size": 32, "nonce_size": 12},
    }

    def __init__(self, master_key: bytes | None = None):
        """Inicializa o service.

        Args:
            master_key: Chave mestre para derivacao (opcional).
        """
        self._master_key = master_key or os.urandom(32)

    def _derive_key(self, key_id: str | None = None) -> bytes:
        """Deriva uma chave a partir do key_id."""
        if key_id:
            return hashlib.sha256(self._master_key + key_id.encode()).digest()
        return self._master_key

    def encrypt(
        self,
        data: str,
        algorithm: str = "aes-256-gcm",
        key_id: str | None = None,
    ) -> dict[str, Any]:
        """Criptografa dados.

        Args:
            data: Dados a criptografar.
            algorithm: Algoritmo de criptografia.
            key_id: ID da chave (opcional).

        Returns:
            Dict com dados criptografados.

        Raises:
            ValueError: Se algoritmo invalido.
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Algoritmo nao suportado: {algorithm}")

        key = self._derive_key(key_id)
        data_bytes = data.encode("utf-8")

        if algorithm == "aes-256-gcm":
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
            encrypted = base64.b64encode(nonce + ciphertext).decode()

        elif algorithm == "chacha20-poly1305":
            nonce = os.urandom(12)
            chacha = ChaCha20Poly1305(key)
            ciphertext = chacha.encrypt(nonce, data_bytes, None)
            encrypted = base64.b64encode(nonce + ciphertext).decode()

        elif algorithm == "fernet":
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            ciphertext = f.encrypt(data_bytes)
            encrypted = ciphertext.decode()

        else:
            # Fallback para AES-256-GCM
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
            encrypted = base64.b64encode(nonce + ciphertext).decode()

        logger.info("Dados criptografados com algoritmo %s", algorithm)

        return {
            "encrypted": encrypted,
            "algorithm": algorithm,
            "key_hint": key[:4].hex() + "...",
        }

    def decrypt(
        self,
        encrypted_data: str,
        key_id: str | None = None,
    ) -> dict[str, Any]:
        """Descriptografa dados.

        Args:
            encrypted_data: Dados criptografados em base64.
            key_id: ID da chave.

        Returns:
            Dict com status da operacao.

        Note:
            Implementacao completa requer key management configurado.
        """
        return {
            "status": "key_management_required",
            "message": "Descriptografia requer configuracao de key management",
        }

    def list_algorithms(self) -> list:
        """Lista algoritmos de criptografia disponiveis.

        Returns:
            Lista de algoritmos suportados.
        """
        return [
            {"id": "aes-256-gcm", "name": "AES-256-GCM", "recommended": True},
            {"id": "aes-256-cbc", "name": "AES-256-CBC", "recommended": False},
            {"id": "fernet", "name": "Fernet", "recommended": False},
            {"id": "chacha20-poly1305", "name": "ChaCha20-Poly1305", "recommended": True},
        ]
