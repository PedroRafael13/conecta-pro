"""
Module: ConsentManager
Description: Sistema de gestao de consentimentos LGPD com suporte a consentimentos
             granulares, historico completo e integracao com Redis para cache.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 7, 8, 9 - Tratamento e Consentimento de Dados Pessoais
"""

from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
import hashlib
import logging
import asyncio

from pydantic import BaseModel, Field, validator, EmailStr
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class ConsentPurpose(str, Enum):
    """Finalidades de tratamento de dados conforme LGPD."""
    ESSENTIAL = "essential"              # Execucao de contrato
    MARKETING = "marketing"              # Comunicacoes de marketing
    ANALYTICS = "analytics"              # Analise de uso e comportamento
    PROFILING = "profiling"              # Criacao de perfis
    THIRD_PARTY = "third_party"          # Compartilhamento com terceiros
    COOKIES = "cookies"                  # Cookies nao essenciais
    NEWSLETTER = "newsletter"            # Envio de newsletter
    NOTIFICATIONS = "notifications"      # Notificacoes push/email
    GEOLOCATION = "geolocation"          # Dados de localizacao
    BIOMETRIC = "biometric"              # Dados biometricos
    HEALTH = "health"                    # Dados de saude
    EMPLOYMENT = "employment"            # Dados trabalhistas
    FINANCIAL = "financial"              # Dados financeiros
    RESEARCH = "research"                # Pesquisa e estatistica


class ConsentStatus(str, Enum):
    """Status de um consentimento."""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class LegalBasis(str, Enum):
    """Bases legais para tratamento conforme LGPD Art. 7."""
    CONSENT = "consent"                          # Art. 7, I
    LEGAL_OBLIGATION = "legal_obligation"        # Art. 7, II
    PUBLIC_POLICY = "public_policy"              # Art. 7, III
    RESEARCH = "research"                        # Art. 7, IV
    CONTRACT = "contract"                        # Art. 7, V
    LEGAL_PROCESS = "legal_process"              # Art. 7, VI
    LIFE_PROTECTION = "life_protection"          # Art. 7, VII
    HEALTH_PROTECTION = "health_protection"      # Art. 7, VIII
    LEGITIMATE_INTEREST = "legitimate_interest"  # Art. 7, IX
    CREDIT_PROTECTION = "credit_protection"      # Art. 7, X


class ConsentError(Exception):
    """Erro base para operacoes de consentimento."""

    def __init__(self, message: str, subject_id: Optional[str] = None):
        self.message = message
        self.subject_id = subject_id
        super().__init__(self.message)


class ConsentNotFoundError(ConsentError):
    """Consentimento nao encontrado."""
    pass


class ConsentExpiredError(ConsentError):
    """Consentimento expirado."""
    pass


class ConsentDeniedError(ConsentError):
    """Consentimento negado ou retirado."""
    pass


@dataclass
class ConsentRecord:
    """Registro de consentimento individual."""
    id: UUID
    subject_id: str                      # ID do titular
    purpose: ConsentPurpose
    status: ConsentStatus
    legal_basis: LegalBasis
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    version: int = 1
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Verifica se o consentimento esta valido."""
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "subject_id": self.subject_id,
            "purpose": self.purpose.value,
            "status": self.status.value,
            "legal_basis": self.legal_basis.value,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "withdrawn_at": self.withdrawn_at.isoformat() if self.withdrawn_at else None,
            "version": self.version,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "consent_text": self.consent_text,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsentRecord":
        """Reconstroi a partir de dicionario."""
        return cls(
            id=UUID(data["id"]),
            subject_id=data["subject_id"],
            purpose=ConsentPurpose(data["purpose"]),
            status=ConsentStatus(data["status"]),
            legal_basis=LegalBasis(data["legal_basis"]),
            granted_at=datetime.fromisoformat(data["granted_at"]) if data.get("granted_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            withdrawn_at=datetime.fromisoformat(data["withdrawn_at"]) if data.get("withdrawn_at") else None,
            version=data.get("version", 1),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            consent_text=data.get("consent_text"),
            metadata=data.get("metadata", {}),
        )


# SQLAlchemy Models
class ConsentModel(Base):
    """Modelo de banco de dados para consentimentos."""
    __tablename__ = "lgpd_consents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id = Column(String(100), nullable=False, index=True)
    purpose = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    legal_basis = Column(String(50), nullable=False)
    granted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    withdrawn_at = Column(DateTime, nullable=True)
    version = Column(String(10), default="1")
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    consent_text = Column(Text, nullable=True)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    history = relationship("ConsentHistoryModel", back_populates="consent")


class ConsentHistoryModel(Base):
    """Modelo para historico de alteracoes de consentimento."""
    __tablename__ = "lgpd_consent_history"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    consent_id = Column(PGUUID(as_uuid=True), ForeignKey("lgpd_consents.id"), nullable=False)
    action = Column(String(20), nullable=False)  # granted, withdrawn, updated, expired
    previous_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    reason = Column(Text, nullable=True)
    metadata = Column(JSONB, default={})

    consent = relationship("ConsentModel", back_populates="history")


class ConsentStoreInterface(ABC):
    """Interface abstrata para armazenamento de consentimentos."""

    @abstractmethod
    async def save(self, consent: ConsentRecord) -> bool:
        """Salva um consentimento."""
        pass

    @abstractmethod
    async def get(self, consent_id: UUID) -> Optional[ConsentRecord]:
        """Recupera um consentimento por ID."""
        pass

    @abstractmethod
    async def get_by_subject(
        self,
        subject_id: str,
        purpose: Optional[ConsentPurpose] = None
    ) -> List[ConsentRecord]:
        """Recupera consentimentos de um titular."""
        pass

    @abstractmethod
    async def delete(self, consent_id: UUID) -> bool:
        """Remove um consentimento."""
        pass

    @abstractmethod
    async def log_history(
        self,
        consent_id: UUID,
        action: str,
        previous_status: Optional[str],
        new_status: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Registra historico de alteracao."""
        pass


class InMemoryConsentStore(ConsentStoreInterface):
    """
    Armazenamento em memoria para desenvolvimento/testes.
    NAO usar em producao.
    """

    def __init__(self):
        self._consents: Dict[UUID, ConsentRecord] = {}
        self._history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        logger.warning("InMemoryConsentStore inicializado - NAO usar em producao!")

    async def save(self, consent: ConsentRecord) -> bool:
        async with self._lock:
            self._consents[consent.id] = consent
            return True

    async def get(self, consent_id: UUID) -> Optional[ConsentRecord]:
        async with self._lock:
            return self._consents.get(consent_id)

    async def get_by_subject(
        self,
        subject_id: str,
        purpose: Optional[ConsentPurpose] = None
    ) -> List[ConsentRecord]:
        async with self._lock:
            results = []
            for consent in self._consents.values():
                if consent.subject_id == subject_id:
                    if purpose is None or consent.purpose == purpose:
                        results.append(consent)
            return results

    async def delete(self, consent_id: UUID) -> bool:
        async with self._lock:
            if consent_id in self._consents:
                del self._consents[consent_id]
                return True
            return False

    async def log_history(
        self,
        consent_id: UUID,
        action: str,
        previous_status: Optional[str],
        new_status: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        async with self._lock:
            self._history.append({
                "consent_id": str(consent_id),
                "action": action,
                "previous_status": previous_status,
                "new_status": new_status,
                "changed_at": datetime.utcnow().isoformat(),
                "changed_by": changed_by,
                "reason": reason,
            })
            return True


class ConsentManagerConfig(BaseModel):
    """Configuracao do gerenciador de consentimentos."""
    default_expiry_days: int = Field(default=365, ge=30)
    require_explicit_consent: bool = True
    allow_implied_consent: bool = False
    cache_ttl_seconds: int = Field(default=300, ge=60)
    enable_audit_logging: bool = True
    require_double_optin: bool = False
    min_consent_age: int = Field(default=18, ge=13)


class ConsentManager:
    """
    Gerenciador central de consentimentos LGPD.

    Responsavel por:
    - Registro e gerenciamento de consentimentos
    - Verificacao de validade
    - Historico completo de alteracoes
    - Cache em Redis para performance

    Example:
        >>> manager = ConsentManager(store)
        >>> consent = await manager.grant_consent(
        ...     subject_id="user123",
        ...     purpose=ConsentPurpose.MARKETING,
        ...     legal_basis=LegalBasis.CONSENT
        ... )
        >>> is_valid = await manager.check_consent("user123", ConsentPurpose.MARKETING)
    """

    def __init__(
        self,
        store: ConsentStoreInterface,
        config: Optional[ConsentManagerConfig] = None,
        redis_client: Optional[Any] = None
    ):
        """
        Inicializa o gerenciador de consentimentos.

        Args:
            store: Backend de armazenamento.
            config: Configuracao opcional.
            redis_client: Cliente Redis para cache.
        """
        self.store = store
        self.config = config or ConsentManagerConfig()
        self.redis = redis_client
        logger.info("ConsentManager inicializado")

    def _cache_key(self, subject_id: str, purpose: ConsentPurpose) -> str:
        """Gera chave de cache."""
        return f"consent:{subject_id}:{purpose.value}"

    async def _cache_get(self, key: str) -> Optional[ConsentRecord]:
        """Recupera do cache."""
        if not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            if data:
                return ConsentRecord.from_dict(json.loads(data))
        except Exception as e:
            logger.warning("Erro ao acessar cache: %s", str(e))
        return None

    async def _cache_set(self, key: str, consent: ConsentRecord) -> None:
        """Armazena no cache."""
        if not self.redis:
            return
        try:
            await self.redis.setex(
                key,
                self.config.cache_ttl_seconds,
                json.dumps(consent.to_dict())
            )
        except Exception as e:
            logger.warning("Erro ao gravar cache: %s", str(e))

    async def _cache_delete(self, key: str) -> None:
        """Remove do cache."""
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning("Erro ao remover cache: %s", str(e))

    async def grant_consent(
        self,
        subject_id: str,
        purpose: ConsentPurpose,
        legal_basis: LegalBasis,
        expires_in_days: Optional[int] = None,
        consent_text: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """
        Registra concessao de consentimento.

        Args:
            subject_id: ID do titular dos dados.
            purpose: Finalidade do tratamento.
            legal_basis: Base legal aplicavel.
            expires_in_days: Dias ate expiracao.
            consent_text: Texto do consentimento apresentado.
            ip_address: IP do dispositivo.
            user_agent: User agent do navegador.
            metadata: Metadados adicionais.

        Returns:
            ConsentRecord: Registro do consentimento.
        """
        now = datetime.utcnow()
        expiry_days = expires_in_days or self.config.default_expiry_days

        # Verifica se ja existe consentimento para esta finalidade
        existing = await self.store.get_by_subject(subject_id, purpose)
        existing_active = [c for c in existing if c.status == ConsentStatus.GRANTED]

        if existing_active:
            # Atualiza versao do consentimento existente
            old_consent = existing_active[0]
            consent = ConsentRecord(
                id=uuid4(),
                subject_id=subject_id,
                purpose=purpose,
                status=ConsentStatus.GRANTED,
                legal_basis=legal_basis,
                granted_at=now,
                expires_at=now + timedelta(days=expiry_days),
                version=old_consent.version + 1,
                ip_address=ip_address,
                user_agent=user_agent,
                consent_text=consent_text,
                metadata=metadata or {},
            )
            # Marca antigo como substituido
            old_consent.status = ConsentStatus.WITHDRAWN
            old_consent.withdrawn_at = now
            await self.store.save(old_consent)
            await self.store.log_history(
                old_consent.id, "superseded", "granted", "withdrawn",
                reason=f"Substituido por {consent.id}"
            )
        else:
            consent = ConsentRecord(
                id=uuid4(),
                subject_id=subject_id,
                purpose=purpose,
                status=ConsentStatus.GRANTED,
                legal_basis=legal_basis,
                granted_at=now,
                expires_at=now + timedelta(days=expiry_days),
                version=1,
                ip_address=ip_address,
                user_agent=user_agent,
                consent_text=consent_text,
                metadata=metadata or {},
            )

        await self.store.save(consent)
        await self.store.log_history(
            consent.id, "granted", None, "granted",
            reason=f"Consentimento concedido para {purpose.value}"
        )

        # Atualiza cache
        cache_key = self._cache_key(subject_id, purpose)
        await self._cache_set(cache_key, consent)

        if self.config.enable_audit_logging:
            logger.info(
                "Consentimento concedido: subject=%s, purpose=%s, basis=%s",
                subject_id, purpose.value, legal_basis.value
            )

        return consent

    async def withdraw_consent(
        self,
        subject_id: str,
        purpose: ConsentPurpose,
        reason: Optional[str] = None,
        withdrawn_by: Optional[str] = None
    ) -> bool:
        """
        Revoga consentimento do titular.

        Args:
            subject_id: ID do titular.
            purpose: Finalidade a revogar.
            reason: Motivo da revogacao.
            withdrawn_by: Quem solicitou a revogacao.

        Returns:
            bool: True se revogado com sucesso.
        """
        consents = await self.store.get_by_subject(subject_id, purpose)
        active = [c for c in consents if c.status == ConsentStatus.GRANTED]

        if not active:
            raise ConsentNotFoundError(
                f"Nenhum consentimento ativo para {purpose.value}",
                subject_id
            )

        now = datetime.utcnow()
        for consent in active:
            old_status = consent.status.value
            consent.status = ConsentStatus.WITHDRAWN
            consent.withdrawn_at = now
            await self.store.save(consent)
            await self.store.log_history(
                consent.id, "withdrawn", old_status, "withdrawn",
                changed_by=withdrawn_by, reason=reason
            )

        # Invalida cache
        cache_key = self._cache_key(subject_id, purpose)
        await self._cache_delete(cache_key)

        if self.config.enable_audit_logging:
            logger.info(
                "Consentimento revogado: subject=%s, purpose=%s, reason=%s",
                subject_id, purpose.value, reason
            )

        return True

    async def check_consent(
        self,
        subject_id: str,
        purpose: ConsentPurpose,
        raise_if_denied: bool = False
    ) -> bool:
        """
        Verifica se titular tem consentimento valido.

        Args:
            subject_id: ID do titular.
            purpose: Finalidade a verificar.
            raise_if_denied: Se True, levanta excecao se negado.

        Returns:
            bool: True se consentimento valido.

        Raises:
            ConsentDeniedError: Se raise_if_denied=True e consentimento negado.
        """
        # Tenta cache primeiro
        cache_key = self._cache_key(subject_id, purpose)
        cached = await self._cache_get(cache_key)
        if cached:
            is_valid = cached.is_valid()
            if not is_valid and raise_if_denied:
                raise ConsentDeniedError(
                    f"Consentimento nao valido para {purpose.value}",
                    subject_id
                )
            return is_valid

        # Busca no store
        consents = await self.store.get_by_subject(subject_id, purpose)
        active = [c for c in consents if c.status == ConsentStatus.GRANTED]

        if not active:
            if raise_if_denied:
                raise ConsentDeniedError(
                    f"Nenhum consentimento encontrado para {purpose.value}",
                    subject_id
                )
            return False

        consent = active[0]
        is_valid = consent.is_valid()

        # Atualiza cache
        if is_valid:
            await self._cache_set(cache_key, consent)

        if not is_valid and raise_if_denied:
            raise ConsentDeniedError(
                f"Consentimento expirado para {purpose.value}",
                subject_id
            )

        return is_valid

    async def get_all_consents(self, subject_id: str) -> Dict[ConsentPurpose, ConsentRecord]:
        """
        Recupera todos os consentimentos de um titular.

        Args:
            subject_id: ID do titular.

        Returns:
            Dict: Mapa de finalidade -> consentimento.
        """
        consents = await self.store.get_by_subject(subject_id)
        result = {}

        for consent in consents:
            if consent.purpose not in result or consent.status == ConsentStatus.GRANTED:
                result[consent.purpose] = consent

        return result

    async def get_consent_status(self, subject_id: str) -> Dict[str, Any]:
        """
        Retorna status completo de consentimentos do titular.

        Args:
            subject_id: ID do titular.

        Returns:
            Dict: Status formatado para exibicao.
        """
        consents = await self.get_all_consents(subject_id)

        status = {
            "subject_id": subject_id,
            "timestamp": datetime.utcnow().isoformat(),
            "consents": {}
        }

        for purpose in ConsentPurpose:
            if purpose in consents:
                consent = consents[purpose]
                status["consents"][purpose.value] = {
                    "status": consent.status.value,
                    "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                    "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                    "is_valid": consent.is_valid(),
                    "version": consent.version,
                }
            else:
                status["consents"][purpose.value] = {
                    "status": "not_requested",
                    "is_valid": False,
                }

        return status

    async def bulk_withdraw(
        self,
        subject_id: str,
        purposes: Optional[List[ConsentPurpose]] = None,
        reason: str = "User request"
    ) -> int:
        """
        Revoga multiplos consentimentos de uma vez.

        Args:
            subject_id: ID do titular.
            purposes: Lista de finalidades (todas se None).
            reason: Motivo da revogacao.

        Returns:
            int: Numero de consentimentos revogados.
        """
        if purposes is None:
            purposes = list(ConsentPurpose)

        count = 0
        for purpose in purposes:
            try:
                await self.withdraw_consent(subject_id, purpose, reason)
                count += 1
            except ConsentNotFoundError:
                continue

        logger.info(
            "Revogacao em massa: subject=%s, count=%d, reason=%s",
            subject_id, count, reason
        )

        return count

    async def renew_consent(
        self,
        subject_id: str,
        purpose: ConsentPurpose,
        expires_in_days: Optional[int] = None
    ) -> ConsentRecord:
        """
        Renova um consentimento existente.

        Args:
            subject_id: ID do titular.
            purpose: Finalidade a renovar.
            expires_in_days: Novos dias de validade.

        Returns:
            ConsentRecord: Consentimento renovado.
        """
        consents = await self.store.get_by_subject(subject_id, purpose)
        active = [c for c in consents if c.status == ConsentStatus.GRANTED]

        if not active:
            raise ConsentNotFoundError(
                f"Nenhum consentimento ativo para renovar: {purpose.value}",
                subject_id
            )

        old_consent = active[0]
        expiry_days = expires_in_days or self.config.default_expiry_days

        # Cria nova versao
        renewed = await self.grant_consent(
            subject_id=subject_id,
            purpose=purpose,
            legal_basis=old_consent.legal_basis,
            expires_in_days=expiry_days,
            consent_text=old_consent.consent_text,
            metadata={**old_consent.metadata, "renewed_from": str(old_consent.id)},
        )

        logger.info(
            "Consentimento renovado: subject=%s, purpose=%s, new_expiry=%s",
            subject_id, purpose.value, renewed.expires_at
        )

        return renewed

    async def check_expiring_soon(
        self,
        days_threshold: int = 30
    ) -> List[ConsentRecord]:
        """
        Lista consentimentos proximos de expirar.

        Args:
            days_threshold: Dias ate expiracao para considerar.

        Returns:
            List: Consentimentos proximos de expirar.
        """
        # Implementacao simplificada - em producao seria query no banco
        threshold = datetime.utcnow() + timedelta(days=days_threshold)
        expiring = []

        # Esta implementacao requer acesso ao store completo
        # Em producao, usar query SQL direta
        logger.warning(
            "check_expiring_soon requer implementacao especifica do store"
        )

        return expiring


# Instancia singleton
_consent_manager: Optional[ConsentManager] = None


def get_consent_manager() -> ConsentManager:
    """Retorna instancia singleton do ConsentManager."""
    global _consent_manager
    if _consent_manager is None:
        raise ConsentError("ConsentManager nao inicializado. Chame init_consent_manager() primeiro.")
    return _consent_manager


def init_consent_manager(
    store: Optional[ConsentStoreInterface] = None,
    config: Optional[ConsentManagerConfig] = None,
    redis_client: Optional[Any] = None
) -> ConsentManager:
    """
    Inicializa o ConsentManager singleton.

    Args:
        store: Backend de armazenamento.
        config: Configuracao.
        redis_client: Cliente Redis.

    Returns:
        ConsentManager: Instancia inicializada.
    """
    global _consent_manager
    if store is None:
        store = InMemoryConsentStore()
    _consent_manager = ConsentManager(store, config, redis_client)
    return _consent_manager


# Decoradores para verificacao de consentimento
def require_consent(*purposes: ConsentPurpose):
    """
    Decorador para exigir consentimento em endpoints.

    Usage:
        @require_consent(ConsentPurpose.MARKETING)
        async def send_newsletter(user_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extrai subject_id dos argumentos
            subject_id = kwargs.get('subject_id') or kwargs.get('user_id')
            if not subject_id and args:
                subject_id = args[0]

            manager = get_consent_manager()
            for purpose in purposes:
                await manager.check_consent(subject_id, purpose, raise_if_denied=True)

            return await func(*args, **kwargs)
        return wrapper
    return decorator
