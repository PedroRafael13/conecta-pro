#!/usr/bin/env python3
"""
Script para criptografar valores sensíveis em arquivos de credenciais.

Uso:
    # Gerar nova chave de criptografia:
    python scripts/encrypt_secrets.py --generate-key

    # Criptografar um valor:
    python scripts/encrypt_secrets.py --encrypt "minha_senha_secreta"

    # Descriptografar um valor (para debug):
    python scripts/encrypt_secrets.py --decrypt "ENC:gAAAAA..."

    # Criptografar arquivo .env.credentials:
    python scripts/encrypt_secrets.py --encrypt-file /path/to/.env.credentials

A variável ENCRYPTION_KEY deve estar definida no ambiente.
"""

import argparse
import os
import sys

from cryptography.fernet import Fernet, InvalidToken

SENSITIVE_KEYS = {
    "CERTIFICATE_PASSWORD",
    "NFE_CERT_PASSWORD",
    "GOVBR_CLIENT_SECRET",
    "GOOGLE_CLIENT_SECRET",
}

ENC_PREFIX = "ENC:"


def get_fernet() -> Fernet:
    """Obtém instância Fernet usando ENCRYPTION_KEY do ambiente."""
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        print("ERRO: ENCRYPTION_KEY não definida no ambiente.")
        print("Gere uma com: python scripts/encrypt_secrets.py --generate-key")
        sys.exit(1)

    try:
        return Fernet(key.encode())
    except Exception as e:
        print(f"ERRO: ENCRYPTION_KEY inválida: {e}")
        sys.exit(1)


def generate_key() -> str:
    """Gera nova chave Fernet."""
    return Fernet.generate_key().decode()


def encrypt_value(value: str) -> str:
    """Criptografa um valor e retorna com prefixo ENC:."""
    if value.startswith(ENC_PREFIX):
        return value  # Já criptografado
    f = get_fernet()
    encrypted = f.encrypt(value.encode()).decode()
    return f"{ENC_PREFIX}{encrypted}"


def decrypt_value(value: str) -> str:
    """Descriptografa um valor com prefixo ENC:."""
    if not value.startswith(ENC_PREFIX):
        return value  # Não criptografado
    f = get_fernet()
    encrypted_data = value[len(ENC_PREFIX) :]
    try:
        return f.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        print("ERRO: Falha na descriptografia. Verifique ENCRYPTION_KEY.")
        sys.exit(1)


def encrypt_file(filepath: str) -> None:
    """Criptografa valores sensíveis em um arquivo .env."""
    if not os.path.exists(filepath):
        print(f"ERRO: Arquivo não encontrado: {filepath}")
        sys.exit(1)

    lines = []
    modified = 0

    with open(filepath) as f:
        for line in f:
            stripped = line.strip()
            if "=" in stripped and not stripped.startswith("#"):
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()

                if key in SENSITIVE_KEYS and value and not value.startswith(ENC_PREFIX):
                    encrypted = encrypt_value(value)
                    lines.append(f"{key}={encrypted}\n")
                    modified += 1
                    print(f"  Criptografado: {key}")
                    continue

            lines.append(line)

    if modified > 0:
        with open(filepath, "w") as f:
            f.writelines(lines)
        print(f"\n{modified} valor(es) criptografado(s) em {filepath}")
    else:
        print("Nenhum valor sensível encontrado para criptografar.")


def main():
    parser = argparse.ArgumentParser(description="Gerenciador de secrets criptografados")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate-key", action="store_true", help="Gera nova ENCRYPTION_KEY")
    group.add_argument("--encrypt", type=str, help="Criptografa um valor")
    group.add_argument("--decrypt", type=str, help="Descriptografa um valor ENC:")
    group.add_argument("--encrypt-file", type=str, help="Criptografa valores em arquivo .env")

    args = parser.parse_args()

    if args.generate_key:
        key = generate_key()
        print(f"Nova ENCRYPTION_KEY gerada:\n{key}")
        print("\nAdicione ao seu .env:")
        print(f"ENCRYPTION_KEY={key}")

    elif args.encrypt:
        result = encrypt_value(args.encrypt)
        print(f"Valor criptografado:\n{result}")

    elif args.decrypt:
        result = decrypt_value(args.decrypt)
        print(f"Valor descriptografado:\n{result}")

    elif args.encrypt_file:
        encrypt_file(args.encrypt_file)


if __name__ == "__main__":
    main()
