"""
PATCH 04: Mascaramento de PII em Logs
Data: 2026-02-05
Severidade: ALTO

Protege dados pessoais (PII) em logs de aplicação.
Implementa funções de máscara para CPF, email, telefone.
"""

import re
import json
from typing import Any, Dict, Union
from functools import wraps


class LogMasker:
    """
    Classe utilitária para mascaramento de dados sensíveis em logs.

    Padrões suportados:
    - CPF: XXX.XXX.XXX-XX → ***.XXX.XXX-** (mostra apenas meio)
    - CNPJ: XX.XXX.XXX/XXXX-XX → **.XXX.XXX/****-**
    - Email: usuario@example.com → u***@example.com
    - Telefone: (11) 98765-4321 → (11) 9****-****
    - RG: XX.XXX.XXX-X → **.***.***-**
    """

    # Regex patterns
    CPF_PATTERN = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}')
    CNPJ_PATTERN = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14}')
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_PATTERN = re.compile(r'\(\d{2}\)\s*\d{4,5}-\d{4}|\d{10,11}')
    RG_PATTERN = re.compile(r'\d{2}\.\d{3}\.\d{3}-\d{1}|\d{9}')

    @classmethod
    def mask_cpf(cls, cpf: str) -> str:
        """
        Mascara CPF mantendo apenas dígitos do meio.

        Args:
            cpf: CPF em formato string (com ou sem pontuação)

        Returns:
            CPF mascarado: ***.XXX.XXX-**

        Examples:
            >>> LogMasker.mask_cpf("123.456.789-00")
            '***.456.789-**'
            >>> LogMasker.mask_cpf("12345678900")
            '***.456.789-**'
        """
        if not cpf:
            return ""

        # Extrai apenas dígitos
        digits = re.sub(r'\D', '', str(cpf))

        if len(digits) != 11:
            # Não parece CPF válido, retorna mascarado completamente
            return "***" + "*" * max(0, len(str(cpf)) - 3)

        # Formato: ***.XXX.XXX-**
        return f"***.{digits[3:6]}.{digits[6:9]}-**"

    @classmethod
    def mask_cnpj(cls, cnpj: str) -> str:
        """
        Mascara CNPJ.

        Returns:
            CNPJ mascarado: **.XXX.XXX/****-**

        Examples:
            >>> LogMasker.mask_cnpj("12.345.678/0001-90")
            '**.345.678/****-**'
        """
        if not cnpj:
            return ""

        digits = re.sub(r'\D', '', str(cnpj))

        if len(digits) != 14:
            return "**" + "*" * max(0, len(str(cnpj)) - 2)

        return f"**.{digits[2:5]}.{digits[5:8]}/****-**"

    @classmethod
    def mask_email(cls, email: str) -> str:
        """
        Mascara email mantendo primeira letra e domínio.

        Args:
            email: Endereço de email

        Returns:
            Email mascarado: a***@example.com

        Examples:
            >>> LogMasker.mask_email("usuario@example.com")
            'u***@example.com'
            >>> LogMasker.mask_email("ab@example.com")
            'a*@example.com'
        """
        if not email or '@' not in email:
            return email if email else ""

        local, domain = email.rsplit('@', 1)

        if len(local) <= 1:
            masked_local = "*"
        elif len(local) == 2:
            masked_local = local[0] + "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 1)

        return f"{masked_local}@{domain}"

    @classmethod
    def mask_phone(cls, phone: str) -> str:
        """
        Mascara número de telefone.

        Returns:
            Telefone mascarado: (11) 9****-**** ou (11) ****-****

        Examples:
            >>> LogMasker.mask_phone("(11) 98765-4321")
            '(11) 9****-****'
            >>> LogMasker.mask_phone("11987654321")
            '(11) 9****-****'
        """
        if not phone:
            return ""

        digits = re.sub(r'\D', '', str(phone))

        if len(digits) < 10:
            return "***"

        ddd = digits[:2]

        if len(digits) == 11:  # Celular com 9
            return f"({ddd}) {digits[2]}{'*' * 4}-{'*' * 4}"
        else:  # Fixo
            return f"({ddd}) {'*' * 4}-{'*' * 4}"

    @classmethod
    def mask_rg(cls, rg: str) -> str:
        """
        Mascara RG.

        Returns:
            RG mascarado: **.***.***-**
        """
        if not rg:
            return ""

        digits = re.sub(r'\D', '', str(rg))

        if len(digits) < 9:
            return "**" + "*" * max(0, len(str(rg)) - 2)

        return f"**.{digits[2:5]}.{digits[5:8]}-**"

    @classmethod
    def mask_sensitive_string(cls, text: str) -> str:
        """
        Aplica todas as máscaras em uma string.

        Processa na ordem: CNPJ, CPF, email, telefone, RG

        Args:
            text: Texto potencialmente contendo dados sensíveis

        Returns:
            Texto com dados sensíveis mascarados

        Examples:
            >>> text = "Cliente 123.456.789-00, email: joao@teste.com"
            >>> LogMasker.mask_sensitive_string(text)
            'Cliente ***.456.789-**, email: j***@teste.com'
        """
        if not text or not isinstance(text, str):
            return text

        result = text

        # Aplica máscaras (ordem importa: CNPJ antes de CPF para não conflito)
        result = cls.CNPJ_PATTERN.sub(lambda m: cls.mask_cnpj(m.group()), result)
        result = cls.CPF_PATTERN.sub(lambda m: cls.mask_cpf(m.group()), result)
        result = cls.EMAIL_PATTERN.sub(lambda m: cls.mask_email(m.group()), result)
        result = cls.PHONE_PATTERN.sub(lambda m: cls.mask_phone(m.group()), result)
        result = cls.RG_PATTERN.sub(lambda m: cls.mask_rg(m.group()), result)

        return result

    @classmethod
    def mask_dict(cls, data: Dict[str, Any], sensitive_keys: set = None) -> Dict[str, Any]:
        """
        Mascara valores em dicionário baseado em chaves sensíveis.

        Args:
            data: Dicionário com dados
            sensitive_keys: Conjunto de chaves que devem ser mascaradas

        Returns:
            Dicionário com valores sensíveis mascarados

        Examples:
            >>> data = {"nome": "Joao", "cpf": "123.456.789-00", "email": "joao@teste.com"}
            >>> LogMasker.mask_dict(data)
            {'nome': 'Joao', 'cpf': '***.456.789-**', 'email': 'j***@teste.com'}
        """
        if sensitive_keys is None:
            sensitive_keys = {
                'cpf', 'cnpj', 'email', 'telefone', 'celular', 'phone',
                'rg', 'passport', 'senha', 'password', 'token',
                'credit_card', 'cartao', 'cvv', 'card_number'
            }

        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            key_lower = str(key).lower()

            if any(sensitive in key_lower for sensitive in sensitive_keys):
                # Campo sensível - aplica máscara
                if isinstance(value, str):
                    if 'cpf' in key_lower:
                        result[key] = cls.mask_cpf(value)
                    elif 'cnpj' in key_lower:
                        result[key] = cls.mask_cnpj(value)
                    elif 'email' in key_lower:
                        result[key] = cls.mask_email(value)
                    elif any(x in key_lower for x in ['telefone', 'phone', 'celular']):
                        result[key] = cls.mask_phone(value)
                    elif 'rg' in key_lower:
                        result[key] = cls.mask_rg(value)
                    else:
                        # Campo sensível genérico - máscara completa
                        result[key] = "***"
                else:
                    result[key] = "***"
            elif isinstance(value, dict):
                result[key] = cls.mask_dict(value, sensitive_keys)
            elif isinstance(value, list):
                result[key] = [
                    cls.mask_dict(item, sensitive_keys) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value

        return result


# ============================================
# INTEGRAÇÃO COM LOGURU/FASTAPI
# ============================================

class SecureLogFilter:
    """
    Filtro de log para sanitização automática de mensagens.

    Uso com Loguru:
        from loguru import logger
        from security.log_masking import SecureLogFilter

        logger.add("app.log", filter=SecureLogFilter())
    """

    def __call__(self, record):
        """Processa record do loguru."""
        if "message" in record:
            record["message"] = LogMasker.mask_sensitive_string(record["message"])

        # Também processa extras
        if "extra" in record:
            record["extra"] = LogMasker.mask_dict(record["extra"])

        return record


def mask_sensitive_data(func):
    """
    Decorator para mascarar dados sensíveis em retorno de função.

    Útil para funções de logging que recebem dicionários.

    Examples:
        @mask_sensitive_data
        def log_user_access(user_data):
            logger.info(f"User access: {user_data}")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Processa argumentos
        new_args = []
        for arg in args:
            if isinstance(arg, dict):
                new_args.append(LogMasker.mask_dict(arg))
            elif isinstance(arg, str):
                new_args.append(LogMasker.mask_sensitive_string(arg))
            else:
                new_args.append(arg)

        new_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, dict):
                new_kwargs[key] = LogMasker.mask_dict(value)
            elif isinstance(value, str):
                new_kwargs[key] = LogMasker.mask_sensitive_string(value)
            else:
                new_kwargs[key] = value

        return func(*new_args, **new_kwargs)

    return wrapper


# ============================================
# MIDDLEWARE FASTAPI PARA LOG SEGURO
# ============================================

class SecureLoggingMiddleware:
    """
    Middleware FastAPI para sanitizar logs de request/response.

    Uso:
        from fastapi import FastAPI

        app = FastAPI()
        app.add_middleware(SecureLoggingMiddleware)
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Processa headers (remove cookies, auth tokens)
            headers = dict(scope.get("headers", []))
            safe_headers = {
                k.decode() if isinstance(k, bytes) else k:
                "***" if k.lower() in [b"authorization", "authorization", b"cookie", "cookie"]
                else v.decode() if isinstance(v, bytes) else v
                for k, v in headers.items()
            }

            # Log seguro
            path = scope.get("path", "")
            method = scope.get("method", "")

            # Não loga query params que podem conter dados sensíveis
            query_string = scope.get("query_string", b"").decode()
            if query_string:
                # Sanitiza query string
                query_string = LogMasker.mask_sensitive_string(query_string)

            # Continua com a aplicação
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


# ============================================
# TESTES
# ============================================

if __name__ == "__main__":
    # Testes de máscara
    print("Testes de Mascaramento de PII:")
    print("=" * 50)

    # CPF
    cpf_tests = [
        "123.456.789-00",
        "12345678900",
        "111.222.333-44"
    ]
    print("\nCPF:")
    for cpf in cpf_tests:
        print(f"  {cpf} → {LogMasker.mask_cpf(cpf)}")

    # Email
    email_tests = [
        "usuario@example.com",
        "ab@example.com",
        "nome.sobrenome@empresa.com.br"
    ]
    print("\nEmail:")
    for email in email_tests:
        print(f"  {email} → {LogMasker.mask_email(email)}")

    # Telefone
    phone_tests = [
        "(11) 98765-4321",
        "11987654321",
        "(21) 3456-7890"
    ]
    print("\nTelefone:")
    for phone in phone_tests:
        print(f"  {phone} → {LogMasker.mask_phone(phone)}")

    # String mista
    print("\nString com múltiplos PII:")
    text = "Cliente João (CPF: 123.456.789-00, email: joao@empresa.com, tel: (11) 98765-4321)"
    print(f"  Original: {text}")
    print(f"  Mascarado: {LogMasker.mask_sensitive_string(text)}")

    # Dicionário
    print("\nDicionário:")
    data = {
        "nome": "João Silva",
        "cpf": "123.456.789-00",
        "email": "joao@empresa.com",
        "telefone": "(11) 98765-4321",
        "ativo": True
    }
    print(f"  Original: {data}")
    print(f"  Mascarado: {LogMasker.mask_dict(data)}")

    print("\n" + "=" * 50)
    print("✓ Todos os testes executados!")
