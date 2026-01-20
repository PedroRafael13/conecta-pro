"""Gerenciador de compliance LGPD para notificações."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

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
    granted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    ip_address: Optional[str]
    user_agent: Optional[str]
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
    processed_at: Optional[datetime]
    deadline: datetime
    requester_email: str
    verification_token: str
    verified: bool = False
    notes: str = ""
    result_url: Optional[str] = None


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
    user_id: Optional[int]
    actor_id: Optional[int]
    resource_type: str
    resource_id: str
    old_value: Optional[dict]
    new_value: Optional[dict]
    ip_address: Optional[str]
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
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
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
        ip_address: Optional[str] = None,
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
        """Coleta todos os dados do usuário."""
        # TODO: Implementar coleta real

        return {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "data_categories": {
                "notification_preferences": {
                    "channels": ["push", "email"],
                    "quiet_hours": {"start": "22:00", "end": "08:00"},
                    "frequency": "normal",
                },
                "notification_history": {
                    "total_received": 150,
                    "total_opened": 100,
                    "total_clicked": 45,
                    "recent_notifications": [],  # Últimas 100
                },
                "engagement_data": {
                    "avg_open_rate": 0.67,
                    "avg_click_rate": 0.30,
                    "preferred_time": "10:00",
                },
                "device_tokens": [
                    {"type": "fcm", "registered_at": "2024-01-15"},
                ],
                "consent_records": [
                    {"type": "marketing", "granted": True, "date": "2024-01-10"},
                ],
            },
        }

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
        user_id: Optional[int],
        resource_type: str,
        resource_id: str,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        reason: str = "",
        actor_id: Optional[int] = None,
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
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
            logs = [l for l in logs if l.user_id == user_id]
        if action:
            logs = [l for l in logs if l.action == action]
        if start_date:
            logs = [l for l in logs if l.timestamp >= start_date]
        if end_date:
            logs = [l for l in logs if l.timestamp <= end_date]

        return sorted(logs, key=lambda l: l.timestamp, reverse=True)[:limit]

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
            r for r in self._requests.values()
            if r.status == RequestStatus.COMPLETED
            and start_date <= r.created_at <= end_date
        ]

        on_time = sum(
            1 for r in completed_requests
            if r.processed_at and r.processed_at <= r.deadline
        )

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
                "active_consents": sum(
                    1 for c in self._consents.values()
                    if c.status == ConsentStatus.GRANTED
                ),
            },
        }
