"""
Module: DataMasking
Description: Sistema de mascaramento de dados pessoais (PII) para compliance LGPD.
             Suporta multiplas estrategias de mascaramento para diferentes tipos de dados.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 12, 18 - Anonimizacao e Pseudonimizacao
"""

from typing import Dict, List, Optional, Any, Callable, Pattern, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, date
import re
import hashlib
import secrets
import logging
import json

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MaskingStrategy(str, Enum):
    """Estrategias de mascaramento disponiveis."""
    FULL = "full"                    # Substitui completamente
    PARTIAL = "partial"              # Mantem parte do dado
    HASH = "hash"                    # Hash irreversivel
    PSEUDONYMIZE = "pseudonymize"    # Pseudonimizacao reversivel
    TOKENIZE = "tokenize"            # Substituicao por token
    REDACT = "redact"                # Remove completamente
    GENERALIZE = "generalize"        # Generaliza o valor
    NOISE = "noise"                  # Adiciona ruido estatistico
    SHUFFLE = "shuffle"              # Embaralha caracteres


class PIICategory(str, Enum):
    """Categorias de dados pessoais identificaveis."""
    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    ADDRESS = "address"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    DATE_OF_BIRTH = "date_of_birth"
    SALARY = "salary"
    HEALTH_DATA = "health_data"
    IP_ADDRESS = "ip_address"
    LOCATION = "location"
    BIOMETRIC = "biometric"
    CUSTOM = "custom"


class MaskingLevel(str, Enum):
    """Niveis de mascaramento baseados em contexto."""
    NONE = "none"              # Sem mascaramento (somente producao interna)
    LOW = "low"                # Mascaramento leve (auditoria interna)
    MEDIUM = "medium"          # Mascaramento medio (desenvolvimento)
    HIGH = "high"              # Mascaramento alto (staging)
    MAXIMUM = "maximum"        # Mascaramento maximo (logs, exports)


class MaskingError(Exception):
    """Erro durante operacao de mascaramento."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


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
    visible_chars: int = 0         # Caracteres visiveis (para PARTIAL)
    visible_position: str = "end"  # start, end, middle

    def __post_init__(self):
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)
        else:
            self._compiled_pattern = None


@dataclass
class MaskingConfig:
    """Configuracao global de mascaramento."""
    default_strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    default_level: MaskingLevel = MaskingLevel.MEDIUM
    log_masking_operations: bool = True
    preserve_null_values: bool = True
    global_salt: str = field(default_factory=lambda: secrets.token_hex(16))
    rules: Dict[PIICategory, MaskingRule] = field(default_factory=dict)


# Padroes regex para deteccao de PII
PII_PATTERNS: Dict[PIICategory, Pattern] = {
    PIICategory.CPF: re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
    PIICategory.CNPJ: re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
    PIICategory.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    PIICategory.PHONE: re.compile(r'\b\(?\d{2}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}\b'),
    PIICategory.CREDIT_CARD: re.compile(r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b'),
    PIICategory.IP_ADDRESS: re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
    PIICategory.DATE_OF_BIRTH: re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),
}


class MaskingStrategyInterface(ABC):
    """Interface abstrata para estrategias de mascaramento."""

    @abstractmethod
    def mask(self, value: str, rule: MaskingRule) -> str:
        """Aplica mascaramento ao valor."""
        pass


class FullMaskingStrategy(MaskingStrategyInterface):
    """Substitui valor completamente por caractere de mascara."""

    def mask(self, value: str, rule: MaskingRule) -> str:
        if not value:
            return value
        replacement_char = rule.replacement or "*"
        if rule.preserve_length:
            return replacement_char * len(value)
        return replacement_char * 8


class PartialMaskingStrategy(MaskingStrategyInterface):
    """Mantem parte do valor visivel."""

    def mask(self, value: str, rule: MaskingRule) -> str:
        if not value:
            return value

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
        else:  # end
            return mask_char * masked_len + value[-visible:]


class HashMaskingStrategy(MaskingStrategyInterface):
    """Gera hash irreversivel do valor."""

    def mask(self, value: str, rule: MaskingRule) -> str:
        if not value:
            return value

        salt = rule.hash_salt or ""
        salted_value = f"{salt}{value}"
        hash_value = hashlib.sha256(salted_value.encode()).hexdigest()

        if rule.preserve_length:
            return hash_value[:len(value)]
        return hash_value[:16]  # Retorna primeiros 16 caracteres


class RedactMaskingStrategy(MaskingStrategyInterface):
    """Remove valor completamente."""

    def mask(self, value: str, rule: MaskingRule) -> str:
        return rule.replacement or "[REDACTED]"


class GeneralizeMaskingStrategy(MaskingStrategyInterface):
    """Generaliza o valor (ex: idade exata -> faixa etaria)."""

    def mask(self, value: str, rule: MaskingRule) -> str:
        if not value:
            return value

        # Para datas, generaliza para ano/mes
        date_match = re.match(r'(\d{2})/(\d{2})/(\d{4})', value)
        if date_match:
            return f"**/**/****"

        # Para numeros, arredonda
        if value.isdigit():
            num = int(value)
            if num < 100:
                return f"{(num // 10) * 10}-{(num // 10) * 10 + 9}"
            return f"{(num // 100) * 100}+"

        # Para texto, retorna inicial
        return value[0] + "***" if value else value


class TokenizeMaskingStrategy(MaskingStrategyInterface):
    """Substitui por token unico reversivel."""

    def __init__(self):
        self._token_vault: Dict[str, str] = {}
        self._reverse_vault: Dict[str, str] = {}

    def mask(self, value: str, rule: MaskingRule) -> str:
        if not value:
            return value

        if value in self._token_vault:
            return self._token_vault[value]

        token = f"TOK_{secrets.token_hex(8)}"
        self._token_vault[value] = token
        self._reverse_vault[token] = value
        return token

    def detokenize(self, token: str) -> Optional[str]:
        """Reverte token para valor original."""
        return self._reverse_vault.get(token)


class DataMasker:
    """
    Sistema de mascaramento de dados PII.

    Aplica mascaramento configurable a dados pessoais para
    compliance com LGPD e protecao de privacidade.

    Example:
        >>> masker = DataMasker()
        >>> masked = masker.mask_value("123.456.789-00", PIICategory.CPF)
        >>> print(masked)  # "***.***.***-00"
    """

    def __init__(self, config: Optional[MaskingConfig] = None):
        """
        Inicializa o mascarador.

        Args:
            config: Configuracao de mascaramento.
        """
        self.config = config or MaskingConfig()
        self._strategies: Dict[MaskingStrategy, MaskingStrategyInterface] = {
            MaskingStrategy.FULL: FullMaskingStrategy(),
            MaskingStrategy.PARTIAL: PartialMaskingStrategy(),
            MaskingStrategy.HASH: HashMaskingStrategy(),
            MaskingStrategy.REDACT: RedactMaskingStrategy(),
            MaskingStrategy.GENERALIZE: GeneralizeMaskingStrategy(),
            MaskingStrategy.TOKENIZE: TokenizeMaskingStrategy(),
        }
        self._init_default_rules()
        logger.info("DataMasker inicializado com nivel: %s", self.config.default_level.value)

    def _init_default_rules(self) -> None:
        """Inicializa regras padrao para cada categoria PII."""
        default_rules = {
            PIICategory.CPF: MaskingRule(
                category=PIICategory.CPF,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=2,
                visible_position="end",
                preserve_format=True
            ),
            PIICategory.CNPJ: MaskingRule(
                category=PIICategory.CNPJ,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=4,
                visible_position="end",
                preserve_format=True
            ),
            PIICategory.EMAIL: MaskingRule(
                category=PIICategory.EMAIL,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=3,
                visible_position="start"
            ),
            PIICategory.PHONE: MaskingRule(
                category=PIICategory.PHONE,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=4,
                visible_position="end"
            ),
            PIICategory.NAME: MaskingRule(
                category=PIICategory.NAME,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=2,
                visible_position="start"
            ),
            PIICategory.CREDIT_CARD: MaskingRule(
                category=PIICategory.CREDIT_CARD,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=4,
                visible_position="end"
            ),
            PIICategory.BANK_ACCOUNT: MaskingRule(
                category=PIICategory.BANK_ACCOUNT,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=4,
                visible_position="end"
            ),
            PIICategory.DATE_OF_BIRTH: MaskingRule(
                category=PIICategory.DATE_OF_BIRTH,
                strategy=MaskingStrategy.GENERALIZE
            ),
            PIICategory.SALARY: MaskingRule(
                category=PIICategory.SALARY,
                strategy=MaskingStrategy.GENERALIZE
            ),
            PIICategory.HEALTH_DATA: MaskingRule(
                category=PIICategory.HEALTH_DATA,
                strategy=MaskingStrategy.REDACT
            ),
            PIICategory.IP_ADDRESS: MaskingRule(
                category=PIICategory.IP_ADDRESS,
                strategy=MaskingStrategy.PARTIAL,
                visible_chars=4,
                visible_position="start"
            ),
            PIICategory.BIOMETRIC: MaskingRule(
                category=PIICategory.BIOMETRIC,
                strategy=MaskingStrategy.HASH
            ),
        }

        for category, rule in default_rules.items():
            if category not in self.config.rules:
                self.config.rules[category] = rule

    def _get_rule(self, category: PIICategory) -> MaskingRule:
        """Obtem regra para categoria."""
        return self.config.rules.get(
            category,
            MaskingRule(category=category, strategy=self.config.default_strategy)
        )

    def _get_strategy(self, strategy: MaskingStrategy) -> MaskingStrategyInterface:
        """Obtem implementacao da estrategia."""
        return self._strategies.get(strategy, self._strategies[MaskingStrategy.FULL])

    def mask_value(
        self,
        value: Any,
        category: PIICategory,
        level: Optional[MaskingLevel] = None
    ) -> Any:
        """
        Mascara um valor individual.

        Args:
            value: Valor a mascarar.
            category: Categoria do dado PII.
            level: Nivel de mascaramento (usa default se nao especificado).

        Returns:
            Any: Valor mascarado.
        """
        if value is None and self.config.preserve_null_values:
            return None

        level = level or self.config.default_level

        if level == MaskingLevel.NONE:
            return value

        # Converte para string para processar
        str_value = str(value) if value is not None else ""

        rule = self._get_rule(category)

        # Ajusta estrategia baseado no nivel
        effective_rule = rule
        if level == MaskingLevel.MAXIMUM:
            effective_rule = MaskingRule(
                category=category,
                strategy=MaskingStrategy.REDACT
            )
        elif level == MaskingLevel.HIGH:
            effective_rule = MaskingRule(
                category=category,
                strategy=MaskingStrategy.HASH,
                hash_salt=self.config.global_salt
            )

        strategy = self._get_strategy(effective_rule.strategy)
        masked = strategy.mask(str_value, effective_rule)

        if self.config.log_masking_operations:
            logger.debug(
                "Mascaramento aplicado: categoria=%s, estrategia=%s, nivel=%s",
                category.value, effective_rule.strategy.value, level.value
            )

        return masked

    def mask_cpf(self, cpf: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara CPF."""
        if not cpf:
            return cpf

        # Normaliza CPF
        cpf_clean = re.sub(r'[^\d]', '', cpf)
        if len(cpf_clean) != 11:
            return self.mask_value(cpf, PIICategory.CPF, level)

        masked = self.mask_value(cpf_clean, PIICategory.CPF, level)

        # Reformata se necessario
        rule = self._get_rule(PIICategory.CPF)
        if rule.preserve_format and '.' in cpf:
            # Reconstroi formato XXX.XXX.XXX-XX
            if len(masked) >= 11:
                return f"{masked[:3]}.{masked[3:6]}.{masked[6:9]}-{masked[9:11]}"

        return masked

    def mask_cnpj(self, cnpj: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara CNPJ."""
        if not cnpj:
            return cnpj

        cnpj_clean = re.sub(r'[^\d]', '', cnpj)
        masked = self.mask_value(cnpj_clean, PIICategory.CNPJ, level)

        rule = self._get_rule(PIICategory.CNPJ)
        if rule.preserve_format and '/' in cnpj:
            if len(masked) >= 14:
                return f"{masked[:2]}.{masked[2:5]}.{masked[5:8]}/{masked[8:12]}-{masked[12:14]}"

        return masked

    def mask_email(self, email: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara email preservando dominio."""
        if not email or '@' not in email:
            return self.mask_value(email, PIICategory.EMAIL, level)

        local, domain = email.rsplit('@', 1)
        masked_local = self.mask_value(local, PIICategory.EMAIL, level)

        if level == MaskingLevel.MAXIMUM:
            return f"{masked_local}@*****.***"

        return f"{masked_local}@{domain}"

    def mask_phone(self, phone: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara telefone."""
        return self.mask_value(phone, PIICategory.PHONE, level)

    def mask_credit_card(self, card: str, level: Optional[MaskingLevel] = None) -> str:
        """Mascara cartao de credito."""
        if not card:
            return card

        card_clean = re.sub(r'[^\d]', '', card)
        masked = self.mask_value(card_clean, PIICategory.CREDIT_CARD, level)

        # Formato padrao XXXX XXXX XXXX XXXX
        if len(masked) == 16 and ' ' in card:
            return f"{masked[:4]} {masked[4:8]} {masked[8:12]} {masked[12:16]}"

        return masked

    def mask_dict(
        self,
        data: Dict[str, Any],
        field_mappings: Dict[str, PIICategory],
        level: Optional[MaskingLevel] = None
    ) -> Dict[str, Any]:
        """
        Mascara campos de um dicionario.

        Args:
            data: Dicionario com dados.
            field_mappings: Mapeamento campo -> categoria PII.
            level: Nivel de mascaramento.

        Returns:
            Dict: Dicionario com campos mascarados.
        """
        masked_data = data.copy()

        for field_name, category in field_mappings.items():
            if field_name in masked_data:
                masked_data[field_name] = self.mask_value(
                    masked_data[field_name],
                    category,
                    level
                )

        return masked_data

    def mask_object(
        self,
        obj: Any,
        field_mappings: Dict[str, PIICategory],
        level: Optional[MaskingLevel] = None
    ) -> Dict[str, Any]:
        """
        Mascara campos de um objeto (SQLAlchemy model, Pydantic, etc).

        Args:
            obj: Objeto com dados.
            field_mappings: Mapeamento campo -> categoria PII.
            level: Nivel de mascaramento.

        Returns:
            Dict: Dicionario com campos mascarados.
        """
        if hasattr(obj, '__dict__'):
            data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif hasattr(obj, 'dict'):
            data = obj.dict()
        else:
            data = dict(obj)

        return self.mask_dict(data, field_mappings, level)

    def mask_list(
        self,
        items: List[Dict[str, Any]],
        field_mappings: Dict[str, PIICategory],
        level: Optional[MaskingLevel] = None
    ) -> List[Dict[str, Any]]:
        """
        Mascara lista de dicionarios.

        Args:
            items: Lista de dicionarios.
            field_mappings: Mapeamento campo -> categoria PII.
            level: Nivel de mascaramento.

        Returns:
            List: Lista com dados mascarados.
        """
        return [self.mask_dict(item, field_mappings, level) for item in items]

    def detect_pii(self, text: str) -> Dict[PIICategory, List[str]]:
        """
        Detecta dados PII em texto livre.

        Args:
            text: Texto a analisar.

        Returns:
            Dict: Categorias encontradas e valores detectados.
        """
        detected: Dict[PIICategory, List[str]] = {}

        for category, pattern in PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                detected[category] = matches

        return detected

    def mask_text(
        self,
        text: str,
        level: Optional[MaskingLevel] = None,
        categories: Optional[Set[PIICategory]] = None
    ) -> str:
        """
        Mascara dados PII em texto livre.

        Args:
            text: Texto com possiveis dados PII.
            level: Nivel de mascaramento.
            categories: Categorias a mascarar (todas se nao especificado).

        Returns:
            str: Texto com PII mascarado.
        """
        if not text:
            return text

        result = text
        detected = self.detect_pii(text)

        for category, values in detected.items():
            if categories and category not in categories:
                continue

            for value in values:
                masked = self.mask_value(value, category, level)
                result = result.replace(value, masked)

        return result

    def create_audit_safe_copy(
        self,
        data: Dict[str, Any],
        pii_fields: Dict[str, PIICategory]
    ) -> Dict[str, Any]:
        """
        Cria copia segura para auditoria com PII mascarado.

        Args:
            data: Dados originais.
            pii_fields: Campos PII e suas categorias.

        Returns:
            Dict: Copia segura para logs/auditoria.
        """
        return self.mask_dict(data, pii_fields, MaskingLevel.HIGH)

    def create_export_safe_copy(
        self,
        data: Dict[str, Any],
        pii_fields: Dict[str, PIICategory]
    ) -> Dict[str, Any]:
        """
        Cria copia segura para export com maximo mascaramento.

        Args:
            data: Dados originais.
            pii_fields: Campos PII e suas categorias.

        Returns:
            Dict: Copia segura para export externo.
        """
        return self.mask_dict(data, pii_fields, MaskingLevel.MAXIMUM)


class PIIFieldRegistry:
    """
    Registro de campos PII por modelo/entidade.

    Centraliza definicao de quais campos contem dados pessoais
    em cada modelo do sistema.
    """

    def __init__(self):
        self._registry: Dict[str, Dict[str, PIICategory]] = {}

    def register_model(
        self,
        model_name: str,
        pii_fields: Dict[str, PIICategory]
    ) -> None:
        """
        Registra campos PII de um modelo.

        Args:
            model_name: Nome do modelo/tabela.
            pii_fields: Mapeamento campo -> categoria.
        """
        self._registry[model_name] = pii_fields
        logger.info("Modelo registrado: %s com %d campos PII", model_name, len(pii_fields))

    def get_pii_fields(self, model_name: str) -> Dict[str, PIICategory]:
        """Obtem campos PII de um modelo."""
        return self._registry.get(model_name, {})

    def list_models(self) -> List[str]:
        """Lista modelos registrados."""
        return list(self._registry.keys())

    def get_all_pii_fields(self) -> Dict[str, Dict[str, PIICategory]]:
        """Retorna todo o registro."""
        return self._registry.copy()


# Registro global de campos PII
_pii_registry = PIIFieldRegistry()


def get_pii_registry() -> PIIFieldRegistry:
    """Retorna registro global de campos PII."""
    return _pii_registry


def register_pii_fields(model_name: str, fields: Dict[str, PIICategory]) -> None:
    """Registra campos PII de um modelo."""
    _pii_registry.register_model(model_name, fields)


# Instancia singleton do mascarador
_default_masker: Optional[DataMasker] = None


def get_data_masker(config: Optional[MaskingConfig] = None) -> DataMasker:
    """
    Retorna instancia singleton do DataMasker.

    Args:
        config: Configuracao (usada apenas na primeira chamada).

    Returns:
        DataMasker: Instancia do mascarador.
    """
    global _default_masker
    if _default_masker is None:
        _default_masker = DataMasker(config)
    return _default_masker


# Funcoes utilitarias de mascaramento rapido
def mask_cpf(cpf: str) -> str:
    """Mascara CPF rapidamente."""
    return get_data_masker().mask_cpf(cpf)


def mask_email(email: str) -> str:
    """Mascara email rapidamente."""
    return get_data_masker().mask_email(email)


def mask_phone(phone: str) -> str:
    """Mascara telefone rapidamente."""
    return get_data_masker().mask_phone(phone)


def mask_pii_in_text(text: str) -> str:
    """Mascara PII em texto rapidamente."""
    return get_data_masker().mask_text(text)


# Registro padrao de campos PII comuns
def init_default_pii_registry() -> None:
    """Inicializa registro com campos PII comuns do sistema."""
    common_mappings = {
        "employees": {
            "cpf": PIICategory.CPF,
            "rg": PIICategory.RG,
            "email": PIICategory.EMAIL,
            "phone": PIICategory.PHONE,
            "mobile_phone": PIICategory.PHONE,
            "name": PIICategory.NAME,
            "full_name": PIICategory.NAME,
            "birth_date": PIICategory.DATE_OF_BIRTH,
            "salary": PIICategory.SALARY,
            "address": PIICategory.ADDRESS,
            "bank_account": PIICategory.BANK_ACCOUNT,
        },
        "clients": {
            "cpf": PIICategory.CPF,
            "cnpj": PIICategory.CNPJ,
            "email": PIICategory.EMAIL,
            "phone": PIICategory.PHONE,
            "contact_name": PIICategory.NAME,
            "address": PIICategory.ADDRESS,
        },
        "users": {
            "email": PIICategory.EMAIL,
            "name": PIICategory.NAME,
            "phone": PIICategory.PHONE,
            "ip_address": PIICategory.IP_ADDRESS,
        },
        "medical_records": {
            "cpf": PIICategory.CPF,
            "name": PIICategory.NAME,
            "diagnosis": PIICategory.HEALTH_DATA,
            "medical_history": PIICategory.HEALTH_DATA,
            "exam_results": PIICategory.HEALTH_DATA,
        },
    }

    for model_name, fields in common_mappings.items():
        register_pii_fields(model_name, fields)
