"""
Service de Mascaramento de Dados LGPD - Consolidado
===================================================

Sistema de mascaramento de dados pessoais (PII) para compliance LGPD.
Suporta múltiplas estratégias de mascaramento para diferentes tipos de dados.

Migrado de 01_security_lgpd/encryption/data_masking.py

Compliance: LGPD Art. 12, 18 - Anonimização e Pseudonimização
"""

from typing import Dict, List, Optional, Any, Set, Pattern
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re
import hashlib
import secrets
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MaskingStrategy(str, Enum):
    """Estratégias de mascaramento disponíveis."""
    FULL = "full"
    PARTIAL = "partial"
    HASH = "hash"
    PSEUDONYMIZE = "pseudonymize"
    TOKENIZE = "tokenize"
    REDACT = "redact"
    GENERALIZE = "generalize"


class PIICategory(str, Enum):
    """Categorias de dados pessoais identificáveis."""
    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    ADDRESS = "address"
    CREDIT_CARD = "credit_card"
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    DATE_OF_BIRTH = "date_of_birth"
    SALARY = "salary"
    HEALTH_DATA = "health_data"
    IP_ADDRESS = "ip_address"
    LOCATION = "location"
    BIOMETRIC = "biometric"
    GENERIC = "generic"


class MaskingLevel(str, Enum):
    """Níveis de mascaramento baseados em contexto."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class MaskingRule:
    """Regra de mascaramento para um tipo de dado."""
    category: PIICategory
    strategy: MaskingStrategy
    pattern: Optional[str] = None
    replacement: Optional[str] = None
    preserve_length: bool = False
    preserve_format: bool = False
    hash_salt: Optional[str] = None
    visible_chars: int = 0
    visible_position: str = "end"


@dataclass
class MaskingConfig:
    """Configuração global de mascaramento."""
    default_strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    default_level: MaskingLevel = MaskingLevel.MEDIUM
    log_masking_operations: bool = True
    preserve_null_values: bool = True
    global_salt: str = field(default_factory=lambda: secrets.token_hex(16))
    rules: Dict[PIICategory, MaskingRule] = field(default_factory=dict)


# Padrões regex para detecção de PII
PII_PATTERNS: Dict[PIICategory, Pattern] = {
    PIICategory.CPF: re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
    PIICategory.CNPJ: re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
    PIICategory.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    PIICategory.PHONE: re.compile(r'\b\(?\d{2}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}\b'),
    PIICategory.CREDIT_CARD: re.compile(r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b'),
    PIICategory.IP_ADDRESS: re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
    PIICategory.DATE_OF_BIRTH: re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),
}


class MaskingService:
    """
    Sistema de mascaramento de dados PII.

    Aplica mascaramento configurável a dados pessoais para
    compliance com LGPD e proteção de privacidade.

    Example:
        >>> service = MaskingService()
        >>> masked = service.mask_cpf("123.456.789-00")
        >>> print(masked)  # "***.***.***-00"
    """

    def __init__(self, config: Optional[MaskingConfig] = None):
        """
        Inicializa o mascarador.

        Args:
            config: Configuração de mascaramento.
        """
        self.config = config or MaskingConfig()
        self._token_vault: Dict[str, str] = {}
        self._reverse_vault: Dict[str, str] = {}
        self._init_default_rules()
        logger.info("MaskingService inicializado com nível: %s", self.config.default_level.value)

    def _init_default_rules(self) -> None:
        """Inicializa regras padrão para cada categoria PII."""
        default_rules = {
            PIICategory.CPF: MaskingRule(category=PIICategory.CPF, strategy=MaskingStrategy.PARTIAL, visible_chars=2, visible_position="end", preserve_format=True),
            PIICategory.CNPJ: MaskingRule(category=PIICategory.CNPJ, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="end", preserve_format=True),
            PIICategory.EMAIL: MaskingRule(category=PIICategory.EMAIL, strategy=MaskingStrategy.PARTIAL, visible_chars=3, visible_position="start"),
            PIICategory.PHONE: MaskingRule(category=PIICategory.PHONE, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="end"),
            PIICategory.NAME: MaskingRule(category=PIICategory.NAME, strategy=MaskingStrategy.PARTIAL, visible_chars=2, visible_position="start"),
            PIICategory.CREDIT_CARD: MaskingRule(category=PIICategory.CREDIT_CARD, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="end"),
            PIICategory.CARD: MaskingRule(category=PIICategory.CARD, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="end"),
            PIICategory.BANK_ACCOUNT: MaskingRule(category=PIICategory.BANK_ACCOUNT, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="end"),
            PIICategory.DATE_OF_BIRTH: MaskingRule(category=PIICategory.DATE_OF_BIRTH, strategy=MaskingStrategy.GENERALIZE),
            PIICategory.SALARY: MaskingRule(category=PIICategory.SALARY, strategy=MaskingStrategy.GENERALIZE),
            PIICategory.HEALTH_DATA: MaskingRule(category=PIICategory.HEALTH_DATA, strategy=MaskingStrategy.REDACT),
            PIICategory.IP_ADDRESS: MaskingRule(category=PIICategory.IP_ADDRESS, strategy=MaskingStrategy.PARTIAL, visible_chars=4, visible_position="start"),
            PIICategory.BIOMETRIC: MaskingRule(category=PIICategory.BIOMETRIC, strategy=MaskingStrategy.HASH),
        }

        for category, rule in default_rules.items():
            if category not in self.config.rules:
                self.config.rules[category] = rule

    def _get_rule(self, category: PIICategory) -> MaskingRule:
        """Obtém regra para categoria."""
        return self.config.rules.get(category, MaskingRule(category=category, strategy=self.config.default_strategy))

    def _apply_strategy(self, value: str, rule: MaskingRule, level: MaskingLevel) -> str:
        """Aplica estratégia de mascaramento."""
        if not value:
            return value

        if level == MaskingLevel.NONE:
            return value

        # Ajusta estratégia baseado no nível
        strategy = rule.strategy
        if level == MaskingLevel.MAXIMUM:
            strategy = MaskingStrategy.REDACT
        elif level == MaskingLevel.HIGH:
            strategy = MaskingStrategy.HASH

        if strategy == MaskingStrategy.FULL:
            return "*" * (len(value) if rule.preserve_length else 8)
        elif strategy == MaskingStrategy.PARTIAL:
            return self._partial_mask(value, rule)
        elif strategy == MaskingStrategy.HASH:
            return self._hash_mask(value, rule)
        elif strategy == MaskingStrategy.REDACT:
            return rule.replacement or "[REDACTED]"
        elif strategy == MaskingStrategy.GENERALIZE:
            return self._generalize_mask(value)
        elif strategy == MaskingStrategy.TOKENIZE:
            return self._tokenize(value)
        else:
            return "*" * len(value)

    def _partial_mask(self, value: str, rule: MaskingRule) -> str:
        """Mascaramento parcial."""
        visible = rule.visible_chars
        if visible >= len(value):
            return value

        mask_char = rule.replacement or "*"
        masked_len = len(value) - visible

        if rule.visible_position == "start":
            return value[:visible] + mask_char * masked_len
        elif rule.visible_position == "middle":
            half = visible // 2
            return value[:half] + mask_char * masked_len + value[-half:] if half > 0 else mask_char * len(value)
        else:
            return mask_char * masked_len + value[-visible:]

    def _hash_mask(self, value: str, rule: MaskingRule) -> str:
        """Hash irreversível."""
        salt = rule.hash_salt or self.config.global_salt
        salted = f"{salt}{value}"
        hash_value = hashlib.sha256(salted.encode()).hexdigest()
        return hash_value[:len(value)] if rule.preserve_length else hash_value[:16]

    def _generalize_mask(self, value: str) -> str:
        """Generaliza o valor."""
        date_match = re.match(r'(\d{2})/(\d{2})/(\d{4})', value)
        if date_match:
            return "**/**/****"

        if value.isdigit():
            num = int(value)
            if num < 100:
                return f"{(num // 10) * 10}-{(num // 10) * 10 + 9}"
            return f"{(num // 100) * 100}+"

        return value[0] + "***" if value else value

    def _tokenize(self, value: str) -> str:
        """Substituição por token."""
        if value in self._token_vault:
            return self._token_vault[value]

        token = f"TOK_{secrets.token_hex(8)}"
        self._token_vault[value] = token
        self._reverse_vault[token] = value
        return token

    def detokenize(self, token: str) -> Optional[str]:
        """Reverte token para valor original."""
        return self._reverse_vault.get(token)

    # Métodos específicos para cada tipo de PII
    def mask_cpf(self, cpf: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara CPF brasileiro."""
        if not cpf:
            return cpf

        level = level or self.config.default_level
        cpf_clean = re.sub(r'[^\d]', '', cpf)
        if len(cpf_clean) != 11:
            return "*" * len(cpf)

        if level in [MaskingLevel.MAXIMUM, MaskingLevel.HIGH]:
            return "***.***.***-**"

        return f"{cpf_clean[:3]}.***.***-{cpf_clean[-2:]}"

    def mask_cnpj(self, cnpj: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara CNPJ brasileiro."""
        if not cnpj:
            return cnpj

        level = level or self.config.default_level
        cnpj_clean = re.sub(r'[^\d]', '', cnpj)
        if len(cnpj_clean) != 14:
            return "*" * len(cnpj)

        if level in [MaskingLevel.MAXIMUM, MaskingLevel.HIGH]:
            return "**.***.***/****.***"

        return f"{cnpj_clean[:2]}.***.***/{cnpj_clean[8:12]}-**"

    def mask_email(self, email: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara email preservando domínio."""
        if not email or '@' not in email:
            return "*" * len(email) if email else email

        level = level or self.config.default_level
        local, domain = email.rsplit('@', 1)

        if level == MaskingLevel.MAXIMUM:
            return f"{'*' * len(local)}@*****.***"

        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    def mask_phone(self, phone: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara telefone."""
        if not phone:
            return phone

        level = level or self.config.default_level
        phone_clean = re.sub(r'[^\d]', '', phone)

        if level in [MaskingLevel.MAXIMUM, MaskingLevel.HIGH]:
            return "*" * len(phone_clean)

        if len(phone_clean) >= 4:
            return phone_clean[:2] + "*" * (len(phone_clean) - 4) + phone_clean[-2:]
        return "*" * len(phone_clean)

    def mask_credit_card(self, card: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara cartão de crédito."""
        if not card:
            return card

        level = level or self.config.default_level
        card_clean = re.sub(r'[^\d]', '', card)

        if level == MaskingLevel.MAXIMUM:
            return "**** **** **** ****"

        if len(card_clean) >= 4:
            return f"**** **** **** {card_clean[-4:]}"
        return "*" * len(card_clean)

    def mask_name(self, name: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara nome pessoal."""
        if not name:
            return name

        level = level or self.config.default_level

        if level in [MaskingLevel.MAXIMUM, MaskingLevel.HIGH]:
            return "*" * len(name)

        words = name.split()
        masked_words = []
        for word in words:
            if len(word) > 1:
                masked_words.append(word[0] + "*" * (len(word) - 1))
            else:
                masked_words.append("*")
        return " ".join(masked_words)

    # Método principal de mascaramento
    def mask(self, data: str, category: str, level: str = "medium") -> Dict[str, Any]:
        """
        Mascara dados PII.

        Args:
            data: Dado a mascarar.
            category: Categoria do dado (cpf, email, phone, etc).
            level: Nível de mascaramento (partial/low, medium, high, full/maximum).

        Returns:
            Dict com dado mascarado.
        """
        # Mapeia level para MaskingLevel
        level_map = {
            "partial": MaskingLevel.LOW,
            "low": MaskingLevel.LOW,
            "medium": MaskingLevel.MEDIUM,
            "high": MaskingLevel.HIGH,
            "full": MaskingLevel.MAXIMUM,
            "maximum": MaskingLevel.MAXIMUM,
        }
        mask_level = level_map.get(level.lower(), MaskingLevel.MEDIUM)

        # Mapeia category para PIICategory
        cat_lower = category.lower()
        try:
            pii_category = PIICategory(cat_lower)
        except ValueError:
            pii_category = PIICategory.GENERIC

        # Aplica mascaramento específico
        mask_methods = {
            PIICategory.CPF: self.mask_cpf,
            PIICategory.CNPJ: self.mask_cnpj,
            PIICategory.EMAIL: self.mask_email,
            PIICategory.PHONE: self.mask_phone,
            PIICategory.CREDIT_CARD: self.mask_credit_card,
            PIICategory.CARD: self.mask_credit_card,
            PIICategory.NAME: self.mask_name,
        }

        mask_func = mask_methods.get(pii_category)
        if mask_func:
            masked = mask_func(data, mask_level)
        else:
            rule = self._get_rule(pii_category)
            masked = self._apply_strategy(data, rule, mask_level)

        if self.config.log_masking_operations:
            logger.debug("Dado mascarado: categoria=%s, nível=%s", category, level)

        return {
            "original_length": len(data),
            "masked": masked,
            "category": category,
            "level": level,
        }

    def mask_dict(self, data: Dict[str, Any], field_mappings: Dict[str, PIICategory], level: Optional[MaskingLevel] = None) -> Dict[str, Any]:
        """Mascara campos de um dicionário."""
        masked_data = data.copy()
        level = level or self.config.default_level

        for field_name, category in field_mappings.items():
            if field_name in masked_data and masked_data[field_name]:
                result = self.mask(str(masked_data[field_name]), category.value, level.value)
                masked_data[field_name] = result["masked"]

        return masked_data

    def mask_list(self, items: List[Dict[str, Any]], field_mappings: Dict[str, PIICategory], level: Optional[MaskingLevel] = None) -> List[Dict[str, Any]]:
        """Mascara lista de dicionários."""
        return [self.mask_dict(item, field_mappings, level) for item in items]

    def detect_pii(self, text: str) -> Dict[PIICategory, List[str]]:
        """Detecta dados PII em texto livre."""
        detected: Dict[PIICategory, List[str]] = {}

        for category, pattern in PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                detected[category] = matches

        return detected

    def mask_text(self, text: str, level: Optional[MaskingLevel] = None, categories: Optional[Set[PIICategory]] = None) -> str:
        """Mascara dados PII em texto livre."""
        if not text:
            return text

        level = level or self.config.default_level
        result = text
        detected = self.detect_pii(text)

        for category, values in detected.items():
            if categories and category not in categories:
                continue

            for value in values:
                mask_result = self.mask(value, category.value, level.value)
                result = result.replace(value, mask_result["masked"])

        return result

    def get_formats(self) -> Dict[str, List[Dict[str, str]]]:
        """Retorna formatos de mascaramento disponíveis."""
        return {
            "categories": [{"id": c.value, "description": c.name.replace("_", " ").title()} for c in PIICategory],
            "levels": [{"id": l.value, "description": l.name.replace("_", " ").title()} for l in MaskingLevel],
            "strategies": [{"id": s.value, "description": s.name.replace("_", " ").title()} for s in MaskingStrategy],
        }


# Singleton
_masking_service: Optional[MaskingService] = None


def get_masking_service(config: Optional[MaskingConfig] = None) -> MaskingService:
    """Retorna instância singleton do MaskingService."""
    global _masking_service
    if _masking_service is None:
        _masking_service = MaskingService(config)
    return _masking_service


# Funções utilitárias de mascaramento rápido
def mask_cpf(cpf: str) -> str:
    """Mascara CPF rapidamente."""
    return get_masking_service().mask_cpf(cpf)


def mask_email(email: str) -> str:
    """Mascara email rapidamente."""
    return get_masking_service().mask_email(email)


def mask_phone(phone: str) -> str:
    """Mascara telefone rapidamente."""
    return get_masking_service().mask_phone(phone)


def mask_pii_in_text(text: str) -> str:
    """Mascara PII em texto rapidamente."""
    return get_masking_service().mask_text(text)
