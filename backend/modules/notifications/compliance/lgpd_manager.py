"""Gerenciador de compliance LGPD para notificações."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Imports para coleta de dados LGPD
from core.models.user import User
from modules.notifications.models.notification_log import NotificationLog
from modules.notifications.models.notification_preference import NotificationPreference
from modules.notifications.push.models.push_device import PushDevice

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Tipos de consentimento."""

    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    SYSTEM = "system"
    NEWSLETTER = "newsletter"
    THIRD_PARTY = "third_party"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"


class ConsentStatus(Enum):
    """Status do consentimento."""

    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"


class DataRequestType(Enum):
    """Tipos de solicitação de dados."""

    ACCESS = "access"  # Direito de acesso
    PORTABILITY = "portability"  # Portabilidade
    DELETION = "deletion"  # Exclusão
    RECTIFICATION = "rectification"  # Correção
    RESTRICTION = "restriction"  # Restrição de processamento


class RequestStatus(Enum):
    """Status da solicitação."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


@dataclass
class ConsentRecord:
    """Registro de consentimento."""

    id: UUID
    user_id: int
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime | None
    withdrawn_at: datetime | None
    expires_at: datetime | None
    ip_address: str | None
    user_agent: str | None
    consent_text: str
    version: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DataProcessingRequest:
    """Solicitação de processamento de dados (DSAR)."""

    id: UUID
    user_id: int
    request_type: DataRequestType
    status: RequestStatus
    created_at: datetime
    processed_at: datetime | None
    deadline: datetime
    requester_email: str
    verification_token: str
    verified: bool = False
    notes: str = ""
    result_url: str | None = None


@dataclass
class DataExportResult:
    """Resultado de exportação de dados."""

    request_id: UUID
    user_id: int
    export_format: str
    data_categories: list[str]
    file_path: str
    file_size_bytes: int
    checksum: str
    created_at: datetime
    expires_at: datetime
    download_count: int = 0


@dataclass
class ComplianceAuditLog:
    """Log de auditoria de compliance."""

    id: UUID
    timestamp: datetime
    action: str
    user_id: int | None
    actor_id: int | None
    resource_type: str
    resource_id: str
    old_value: dict | None
    new_value: dict | None
    ip_address: str | None
    reason: str


class LGPDComplianceManager:
    """
    Gerenciador de compliance LGPD para notificações.

    Implementa:
    - Gestão de consentimento (opt-in/opt-out)
    - Direito de acesso aos dados
    - Portabilidade de dados
    - Direito ao esquecimento
    - Auditoria completa
    - Notificações de vazamento
    """

    # Prazos legais LGPD
    ACCESS_REQUEST_DEADLINE_DAYS = 15
    DELETION_REQUEST_DEADLINE_DAYS = 15
    CONSENT_EXPIRY_YEARS = 2

    # Categorias de dados coletados
    DATA_CATEGORIES = [
        "notification_preferences",
        "notification_history",
        "engagement_data",
        "device_tokens",
        "behavioral_data",
        "consent_records",
    ]

    def __init__(
        self,
        data_retention_days: int = 365,
        enable_anonymization: bool = True,
    ) -> None:
        """
        Inicializa o gerenciador.

        Args:
            data_retention_days: Dias de retenção de dados
            enable_anonymization: Habilitar anonimização
        """
        self.retention_days = data_retention_days
        self.enable_anonymization = enable_anonymization
        self._consents: dict[str, ConsentRecord] = {}
        self._requests: dict[UUID, DataProcessingRequest] = {}
        self._audit_logs: list[ComplianceAuditLog] = []

    async def record_consent(
        self,
        db: AsyncSession,
        user_id: int,
        consent_type: ConsentType,
        granted: bool,
        consent_text: str,
        version: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ) -> ConsentRecord:
        """
        Registra consentimento do usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento
            granted: Se foi concedido
            consent_text: Texto apresentado
            version: Versão do termo
            ip_address: IP do usuário
            user_agent: User agent
            metadata: Dados adicionais

        Returns:
            ConsentRecord registrado
        """
        now = datetime.utcnow()
        consent_id = uuid4()

        record = ConsentRecord(
            id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED if granted else ConsentStatus.DENIED,
            granted_at=now if granted else None,
            withdrawn_at=None,
            expires_at=now + timedelta(days=365 * self.CONSENT_EXPIRY_YEARS) if granted else None,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=consent_text,
            version=version,
            metadata=metadata or {},
        )

        # Salvar
        key = f"{user_id}:{consent_type.value}"
        self._consents[key] = record
        await self._save_consent(db, record)

        # Auditoria
        await self._log_audit(
            db=db,
            action="consent_recorded",
            user_id=user_id,
            resource_type="consent",
            resource_id=str(consent_id),
            new_value={"type": consent_type.value, "granted": granted},
            ip_address=ip_address,
            reason="User consent action",
        )

        logger.info(f"Consent recorded: user={user_id}, type={consent_type.value}, granted={granted}")
        return record

    async def withdraw_consent(
        self,
        db: AsyncSession,
        user_id: int,
        consent_type: ConsentType,
        ip_address: str | None = None,
        reason: str = "",
    ) -> ConsentRecord:
        """
        Retira consentimento do usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento
            ip_address: IP do usuário
            reason: Motivo da retirada

        Returns:
            ConsentRecord atualizado
        """
        key = f"{user_id}:{consent_type.value}"
        record = self._consents.get(key)

        if not record:
            raise ValueError(f"Consent not found: {consent_type.value}")

        record.status = ConsentStatus.WITHDRAWN
        record.withdrawn_at = datetime.utcnow()

        await self._save_consent(db, record)

        # Auditoria
        await self._log_audit(
            db=db,
            action="consent_withdrawn",
            user_id=user_id,
            resource_type="consent",
            resource_id=str(record.id),
            old_value={"status": "granted"},
            new_value={"status": "withdrawn"},
            ip_address=ip_address,
            reason=reason or "User requested withdrawal",
        )

        logger.info(f"Consent withdrawn: user={user_id}, type={consent_type.value}")
        return record

    async def check_consent(
        self,
        db: AsyncSession,
        user_id: int,
        consent_type: ConsentType,
    ) -> bool:
        """
        Verifica se usuário tem consentimento ativo.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento

        Returns:
            True se consentimento ativo
        """
        key = f"{user_id}:{consent_type.value}"
        record = self._consents.get(key)

        if not record:
            return False

        # Verificar status
        if record.status != ConsentStatus.GRANTED:
            return False

        # Verificar expiração
        if record.expires_at and record.expires_at < datetime.utcnow():
            record.status = ConsentStatus.EXPIRED
            await self._save_consent(db, record)
            return False

        return True

    async def get_user_consents(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[ConsentRecord]:
        """
        Obtém todos os consentimentos de um usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário

        Returns:
            Lista de ConsentRecord
        """
        return [r for r in self._consents.values() if r.user_id == user_id]

    async def create_data_request(
        self,
        db: AsyncSession,
        user_id: int,
        request_type: DataRequestType,
        requester_email: str,
    ) -> DataProcessingRequest:
        """
        Cria solicitação de dados (DSAR).

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            request_type: Tipo de solicitação
            requester_email: Email do solicitante

        Returns:
            DataProcessingRequest criado
        """
        now = datetime.utcnow()
        request_id = uuid4()

        # Definir prazo baseado no tipo
        if request_type == DataRequestType.DELETION:
            deadline_days = self.DELETION_REQUEST_DEADLINE_DAYS
        else:
            deadline_days = self.ACCESS_REQUEST_DEADLINE_DAYS

        # Gerar token de verificação
        token = hashlib.sha256(f"{request_id}:{user_id}:{now}".encode()).hexdigest()[:32]

        request = DataProcessingRequest(
            id=request_id,
            user_id=user_id,
            request_type=request_type,
            status=RequestStatus.PENDING,
            created_at=now,
            processed_at=None,
            deadline=now + timedelta(days=deadline_days),
            requester_email=requester_email,
            verification_token=token,
            verified=False,
        )

        self._requests[request_id] = request
        await self._save_request(db, request)

        # Auditoria
        await self._log_audit(
            db=db,
            action="data_request_created",
            user_id=user_id,
            resource_type="data_request",
            resource_id=str(request_id),
            new_value={"type": request_type.value},
            reason=f"DSAR: {request_type.value}",
        )

        logger.info(f"Data request created: id={request_id}, type={request_type.value}")
        return request

    async def verify_data_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        token: str,
    ) -> bool:
        """
        Verifica solicitação de dados.

        Args:
            db: Sessão do banco
            request_id: ID da solicitação
            token: Token de verificação

        Returns:
            True se verificado com sucesso
        """
        request = self._requests.get(request_id)
        if not request:
            return False

        if request.verification_token != token:
            return False

        request.verified = True
        request.status = RequestStatus.IN_PROGRESS
        await self._save_request(db, request)

        return True

    async def process_access_request(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> DataExportResult:
        """
        Processa solicitação de acesso aos dados.

        Args:
            db: Sessão do banco
            request_id: ID da solicitação

        Returns:
            DataExportResult com dados exportados
        """
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        if not request.verified:
            raise ValueError("Request not verified")

        # Coletar dados do usuário
        user_data = await self._collect_user_data(db, request.user_id)

        # Exportar para JSON
        export_data = json.dumps(user_data, default=str, indent=2, ensure_ascii=False)
        checksum = hashlib.sha256(export_data.encode()).hexdigest()

        # Salvar arquivo (simulado)
        file_path = f"/exports/{request.user_id}/{request_id}.json"

        result = DataExportResult(
            request_id=request_id,
            user_id=request.user_id,
            export_format="json",
            data_categories=self.DATA_CATEGORIES,
            file_path=file_path,
            file_size_bytes=len(export_data.encode()),
            checksum=checksum,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )

        # Atualizar solicitação
        request.status = RequestStatus.COMPLETED
        request.processed_at = datetime.utcnow()
        request.result_url = file_path
        await self._save_request(db, request)

        # Auditoria
        await self._log_audit(
            db=db,
            action="data_access_processed",
            user_id=request.user_id,
            resource_type="data_export",
            resource_id=str(request_id),
            new_value={"categories": self.DATA_CATEGORIES, "size": result.file_size_bytes},
            reason="Access request fulfilled",
        )

        logger.info(f"Access request processed: {request_id}")
        return result

    async def process_deletion_request(
        self,
        db: AsyncSession,
        request_id: UUID,
    ) -> bool:
        """
        Processa solicitação de exclusão de dados.

        Args:
            db: Sessão do banco
            request_id: ID da solicitação

        Returns:
            True se processado com sucesso
        """
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        if not request.verified:
            raise ValueError("Request not verified")

        user_id = request.user_id

        # Excluir ou anonimizar dados
        if self.enable_anonymization:
            await self._anonymize_user_data(db, user_id)
        else:
            await self._delete_user_data(db, user_id)

        # Revogar todos os consentimentos
        for key in list(self._consents.keys()):
            if key.startswith(f"{user_id}:"):
                record = self._consents[key]
                record.status = ConsentStatus.WITHDRAWN
                record.withdrawn_at = datetime.utcnow()

        # Atualizar solicitação
        request.status = RequestStatus.COMPLETED
        request.processed_at = datetime.utcnow()
        await self._save_request(db, request)

        # Auditoria
        await self._log_audit(
            db=db,
            action="data_deletion_processed",
            user_id=user_id,
            resource_type="user_data",
            resource_id=str(user_id),
            new_value={"action": "anonymized" if self.enable_anonymization else "deleted"},
            reason="Deletion request fulfilled",
        )

        logger.info(f"Deletion request processed: {request_id}")
        return True

    async def can_send_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
    ) -> tuple[bool, str]:
        """
        Verifica se pode enviar notificação.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação

        Returns:
            Tuple (pode_enviar, razão)
        """
        # Mapear tipo de notificação para tipo de consentimento
        consent_map = {
            "marketing": ConsentType.MARKETING,
            "newsletter": ConsentType.NEWSLETTER,
            "promo": ConsentType.MARKETING,
            "system": ConsentType.SYSTEM,
            "transaction": ConsentType.TRANSACTIONAL,
            "reminder": ConsentType.TRANSACTIONAL,
        }

        consent_type = consent_map.get(notification_type, ConsentType.SYSTEM)

        # Notificações transacionais e de sistema não precisam de consentimento explícito
        if consent_type in [ConsentType.SYSTEM, ConsentType.TRANSACTIONAL]:
            return True, "System/transactional notifications allowed"

        # Verificar consentimento
        has_consent = await self.check_consent(db, user_id, consent_type)

        if not has_consent:
            return False, f"No consent for {consent_type.value}"

        return True, "Consent verified"

    async def _collect_user_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[str, Any]:
        """
        Coleta todos os dados do usuário para exportação LGPD.

        Implementa o direito de acesso (Art. 15 LGPD) coletando:
        - Dados cadastrais básicos
        - Preferências de notificação
        - Histórico de notificações
        - Dispositivos registrados
        - Dados de engajamento
        - Registros de consentimento
        """
        logger.info(f"Coletando dados LGPD para usuário {user_id}")

        try:
            # 1. Dados básicos do usuário
            user_query = select(User).where(User.id == user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"Usuário {user_id} não encontrado")

            # 2. Preferências de notificação
            prefs_query = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
            prefs_result = await db.execute(prefs_query)
            preferences = prefs_result.scalars().all()

            # 3. Histórico de notificações (últimas 500)
            history_query = (
                select(NotificationLog)
                .where(NotificationLog.user_id == user_id)
                .order_by(NotificationLog.created_at.desc())
                .limit(500)
            )
            history_result = await db.execute(history_query)
            notifications = history_result.scalars().all()

            # 4. Dispositivos registrados
            devices_query = select(PushDevice).where(PushDevice.user_id == user_id)
            devices_result = await db.execute(devices_query)
            devices = devices_result.scalars().all()

            # 5. Processar dados coletados
            user_data = {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "data_categories": {
                    # Dados cadastrais (anonimiza dados sensíveis)
                    "basic_profile": {
                        "user_id": user_id,
                        "name": user.name,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                        "last_login": user.last_login,
                        "is_active": user.is_active if hasattr(user, "is_active") else True,
                    },
                    # Preferências de notificação
                    "notification_preferences": [
                        {
                            "id": str(pref.id),
                            "category": pref.category.value if pref.category else None,
                            "channel": pref.channel.value if pref.channel else None,
                            "enabled": pref.enabled,
                            "frequency": pref.frequency.value if pref.frequency else None,
                            "quiet_hours_start": pref.quiet_hours_start,
                            "quiet_hours_end": pref.quiet_hours_end,
                            "digest_enabled": pref.digest_enabled,
                            "digest_type": pref.digest_type.value if pref.digest_type else None,
                            "created_at": pref.created_at.isoformat() if pref.created_at else None,
                            "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
                        }
                        for pref in preferences
                    ],
                    # Histórico de notificações
                    "notification_history": {
                        "total_notifications": len(notifications),
                        "summary": {
                            "sent": len([n for n in notifications if n.status == "sent"]),
                            "delivered": len([n for n in notifications if n.status == "delivered"]),
                            "opened": len([n for n in notifications if n.status == "opened"]),
                            "failed": len([n for n in notifications if n.status == "failed"]),
                        },
                        "recent_notifications": [
                            {
                                "id": str(notif.id),
                                "template_id": str(notif.template_id) if notif.template_id else None,
                                "channel": notif.channel,
                                "title": notif.title,
                                "status": notif.status,
                                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
                                "delivered_at": notif.delivered_at.isoformat() if notif.delivered_at else None,
                                "opened_at": notif.opened_at.isoformat() if notif.opened_at else None,
                                "metadata": notif.metadata,
                                "created_at": notif.created_at.isoformat() if notif.created_at else None,
                            }
                            for notif in notifications[:100]  # Últimas 100 detalhadas
                        ],
                    },
                    # Dispositivos registrados
                    "registered_devices": [
                        {
                            "id": str(device.id),
                            "platform": device.platform.value if device.platform else None,
                            "device_type": device.device_type,
                            "app_version": device.app_version,
                            "os_version": device.os_version,
                            "status": device.status.value if device.status else None,
                            "registered_at": device.created_at.isoformat() if device.created_at else None,
                            "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                            # Token é omitido por segurança
                            "token_hash": hashlib.md5(device.token.encode(), usedforsecurity=False).hexdigest()[:8]
                            if device.token
                            else None,
                        }
                        for device in devices
                    ],
                    # Dados de engajamento calculados
                    "engagement_analytics": self._calculate_engagement_stats(notifications),
                    # Registros de consentimento (se existir tabela)
                    "consent_records": await self._collect_consent_records(db, user_id),
                },
                # Metadados da exportação
                "metadata": {
                    "export_requested_by": "lgpd_data_export",
                    "data_retention_policy": "Dados mantidos conforme política de retenção",
                    "data_sources": ["users", "notification_preferences", "notification_log", "push_devices"],
                    "anonymization_applied": False,
                    "legal_basis": "Cumprimento da LGPD - Direito de Acesso (Art. 15)",
                },
            }

            logger.info(
                f"Coleta LGPD completada para usuário {user_id} - {len(notifications)} notificações, {len(devices)} dispositivos"
            )
            return user_data

        except Exception as e:
            logger.error(f"Erro na coleta de dados LGPD para usuário {user_id}: {str(e)}")
            raise

    def _calculate_engagement_stats(self, notifications: list) -> dict[str, Any]:
        """Calcula estatísticas de engajamento do usuário."""
        if not notifications:
            return {
                "total_notifications": 0,
                "engagement_rate": 0.0,
                "avg_response_time": None,
                "most_active_hour": None,
            }

        total = len(notifications)
        opened = len([n for n in notifications if n.opened_at])

        # Calcula horários mais ativos
        active_hours = {}
        for notif in notifications:
            if notif.opened_at:
                hour = notif.opened_at.hour
                active_hours[hour] = active_hours.get(hour, 0) + 1

        most_active_hour = max(active_hours.keys(), key=active_hours.get) if active_hours else None

        return {
            "total_notifications": total,
            "opened_notifications": opened,
            "engagement_rate": round(opened / total * 100, 2) if total > 0 else 0.0,
            "most_active_hour": f"{most_active_hour:02d}:00" if most_active_hour is not None else None,
            "engagement_by_channel": self._calculate_channel_engagement(notifications),
        }

    def _calculate_channel_engagement(self, notifications: list) -> dict[str, dict]:
        """Calcula engajamento por canal."""
        channels = {}

        for notif in notifications:
            channel = notif.channel or "unknown"
            if channel not in channels:
                channels[channel] = {"total": 0, "opened": 0}

            channels[channel]["total"] += 1
            if notif.opened_at:
                channels[channel]["opened"] += 1

        # Calcula taxa de engajamento por canal
        for channel_data in channels.values():
            if channel_data["total"] > 0:
                channel_data["engagement_rate"] = round(channel_data["opened"] / channel_data["total"] * 100, 2)
            else:
                channel_data["engagement_rate"] = 0.0

        return channels

    async def _collect_consent_records(self, db: AsyncSession, user_id: int) -> list[dict]:
        """Coleta registros de consentimento (se existir tabela específica)."""
        # TODO: Implementar quando houver tabela de consentimentos
        # Por enquanto, retorna registro baseado nas preferências
        prefs_query = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id, NotificationPreference.enabled.is_(True)
        )
        prefs_result = await db.execute(prefs_query)
        active_prefs = prefs_result.scalars().all()

        consent_records = []
        for pref in active_prefs:
            consent_records.append(
                {
                    "consent_type": pref.category.value if pref.category else "notifications",
                    "status": "granted",
                    "granted_at": pref.created_at.isoformat() if pref.created_at else None,
                    "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
                    "channel": pref.channel.value if pref.channel else None,
                    "source": "notification_preferences",
                }
            )

        return consent_records

    async def _anonymize_user_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:
        """Anonimiza dados do usuário."""
        # TODO: Implementar anonimização real
        logger.info(f"Anonymizing data for user {user_id}")

    async def _delete_user_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:
        """Exclui dados do usuário."""
        # TODO: Implementar exclusão real
        logger.info(f"Deleting data for user {user_id}")

    async def _log_audit(
        self,
        db: AsyncSession,
        action: str,
        user_id: int | None,
        resource_type: str,
        resource_id: str,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        reason: str = "",
        actor_id: int | None = None,
    ) -> ComplianceAuditLog:
        """Registra log de auditoria."""
        log = ComplianceAuditLog(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            action=action,
            user_id=user_id,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            reason=reason,
        )

        self._audit_logs.append(log)
        # TODO: Persistir no banco
        return log

    async def _save_consent(
        self,
        db: AsyncSession,
        consent: ConsentRecord,
    ) -> None:
        """Salva registro de consentimento."""
        # TODO: Implementar persistência real
        pass

    async def _save_request(
        self,
        db: AsyncSession,
        request: DataProcessingRequest,
    ) -> None:
        """Salva solicitação de dados."""
        # TODO: Implementar persistência real
        pass

    async def get_audit_logs(
        self,
        db: AsyncSession,
        user_id: int | None = None,
        action: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[ComplianceAuditLog]:
        """
        Obtém logs de auditoria.

        Args:
            db: Sessão do banco
            user_id: Filtrar por usuário
            action: Filtrar por ação
            start_date: Data inicial
            end_date: Data final
            limit: Limite de registros

        Returns:
            Lista de ComplianceAuditLog
        """
        logs = self._audit_logs

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        if action:
            logs = [log for log in logs if log.action == action]
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]

        return sorted(logs, key=lambda log: log.timestamp, reverse=True)[:limit]

    async def generate_compliance_report(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Gera relatório de compliance.

        Args:
            db: Sessão do banco
            start_date: Data inicial
            end_date: Data final

        Returns:
            Dict com relatório
        """
        logs = await self.get_audit_logs(db, start_date=start_date, end_date=end_date, limit=10000)

        # Contar ações
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1

        # Contar solicitações por status
        requests_by_status = {}
        for request in self._requests.values():
            if start_date <= request.created_at <= end_date:
                status = request.status.value
                requests_by_status[status] = requests_by_status.get(status, 0) + 1

        # Calcular SLA
        completed_requests = [
            r
            for r in self._requests.values()
            if r.status == RequestStatus.COMPLETED and start_date <= r.created_at <= end_date
        ]

        on_time = sum(1 for r in completed_requests if r.processed_at and r.processed_at <= r.deadline)

        sla_compliance = on_time / len(completed_requests) if completed_requests else 1.0

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_audit_events": len(logs),
                "total_data_requests": sum(requests_by_status.values()),
                "requests_by_status": requests_by_status,
                "sla_compliance": f"{sla_compliance:.1%}",
            },
            "action_breakdown": action_counts,
            "consent_stats": {
                "total_consents": len(self._consents),
                "active_consents": sum(1 for c in self._consents.values() if c.status == ConsentStatus.GRANTED),
            },
        }

    # =============================================================================
    # MÉTODOS PÚBLICOS PARA CONTROLLER API
    # =============================================================================

    async def export_user_data(self, db: AsyncSession, user_id: int, actor_id: int | None = None) -> dict[str, Any]:
        """
        Método público para exportar dados do usuário.

        Implementa o direito de acesso (LGPD Art. 15).
        Inclui audit logging automático.
        """
        # Coleta os dados
        user_data = await self._collect_user_data(db, user_id)

        # Registra audit log
        await self._log_audit(
            db=db,
            action="data_export",
            user_id=user_id,
            resource_type="user_data",
            resource_id=str(user_id),
            reason="Solicitação de exportação de dados pessoais via API",
            actor_id=actor_id or user_id,
        )

        return user_data

    async def get_data_request_status(
        self, db: AsyncSession, request_id: UUID, user_id: int
    ) -> DataProcessingRequest | None:
        """
        Obtém status de solicitação de dados (apenas do usuário proprietário).

        Args:
            db: Sessão do banco
            request_id: ID da solicitação
            user_id: ID do usuário (para verificar propriedade)

        Returns:
            DataProcessingRequest se encontrada e pertence ao usuário, None caso contrário
        """
        request = self._requests.get(request_id)

        # Verifica se a solicitação existe e pertence ao usuário
        if request and request.user_id == user_id:
            return request

        return None

    async def complete_data_request(self, db: AsyncSession, request_id: UUID, result_data: dict[str, Any]) -> bool:
        """
        Marca solicitação de dados como completa.

        Args:
            db: Sessão do banco
            request_id: ID da solicitação
            result_data: Dados do resultado

        Returns:
            True se atualizada com sucesso
        """
        if request_id in self._requests:
            request = self._requests[request_id]
            request.status = RequestStatus.COMPLETED
            request.completion_date = datetime.utcnow()
            request.result_data = result_data

            # Log da conclusão
            await self._log_audit(
                db=db,
                action="data_request_completed",
                user_id=request.user_id,
                resource_type="data_request",
                resource_id=str(request_id),
                new_value={"status": "completed", "completion_date": request.completion_date.isoformat()},
                reason="Solicitação de dados processada com sucesso",
            )

            return True

        return False
