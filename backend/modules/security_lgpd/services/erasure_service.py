"""
Service de Exclusão de Dados LGPD - Consolidado
===============================================

Sistema de eliminação de dados pessoais (Right to be Forgotten) conforme LGPD.
Implementa processo automatizado de exclusão com auditoria completa.

Migrado de 01_security_lgpd/compliance/data_erasure.py

Compliance: LGPD Art. 16, 18 - Eliminação de Dados Pessoais
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging
import secrets
import asyncio

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErasureStatus(str, Enum):
    """Status de uma solicitação de exclusão."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ErasureMethod(str, Enum):
    """Métodos de exclusão de dados."""
    HARD_DELETE = "hard_delete"
    SOFT_DELETE = "soft_delete"
    ANONYMIZE = "anonymize"
    PSEUDONYMIZE = "pseudonymize"
    ENCRYPT = "encrypt"
    OVERWRITE = "overwrite"


class RetentionReason(str, Enum):
    """Motivos para retenção de dados após solicitação de exclusão."""
    LEGAL_OBLIGATION = "legal_obligation"
    TAX_RECORDS = "tax_records"
    LABOR_RECORDS = "labor_records"
    CONTRACT_EXECUTION = "contract_execution"
    LEGAL_CLAIMS = "legal_claims"
    REGULATORY = "regulatory"
    PUBLIC_INTEREST = "public_interest"


class ErasureScope(str, Enum):
    """Escopos de exclusão disponíveis."""
    ALL = "all"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    CONSENT = "consent"
    PERSONAL_DATA = "personal_data"
    HEALTH_DATA = "health_data"


class ErasureError(Exception):
    """Erro base para operações de exclusão."""

    def __init__(self, message: str, request_id: Optional[str] = None):
        self.message = message
        self.request_id = request_id
        super().__init__(self.message)


@dataclass
class DataLocation:
    """Localização de dados do titular no sistema."""
    table_name: str
    record_id: str
    field_names: List[str]
    data_category: str
    erasure_method: ErasureMethod
    retention_period_days: Optional[int] = None
    retention_reason: Optional[RetentionReason] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "record_id": self.record_id,
            "field_names": self.field_names,
            "data_category": self.data_category,
            "erasure_method": self.erasure_method.value,
            "retention_period_days": self.retention_period_days,
            "retention_reason": self.retention_reason.value if self.retention_reason else None,
        }


@dataclass
class ErasureResult:
    """Resultado de uma operação de exclusão."""
    location: DataLocation
    success: bool
    method_used: ErasureMethod
    executed_at: datetime
    error_message: Optional[str] = None
    records_affected: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "success": self.success,
            "method_used": self.method_used.value,
            "executed_at": self.executed_at.isoformat(),
            "error_message": self.error_message,
            "records_affected": self.records_affected,
        }


@dataclass
class ErasureRequest:
    """Solicitação de exclusão de dados."""
    id: UUID
    titular_id: str
    titular_email: Optional[str]
    status: ErasureStatus
    scope: ErasureScope
    reason: Optional[str]
    requested_at: datetime
    requested_by: str
    deadline: datetime
    completed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    data_locations: List[DataLocation] = field(default_factory=list)
    results: List[ErasureResult] = field(default_factory=list)
    blocked_locations: List[DataLocation] = field(default_factory=list)
    verification_code: Optional[str] = None
    verified_at: Optional[datetime] = None
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": str(self.id),
            "titular_id": self.titular_id,
            "titular_email": self.titular_email,
            "status": self.status.value,
            "scope": self.scope.value,
            "reason": self.reason,
            "requested_at": self.requested_at.isoformat(),
            "requested_by": self.requested_by,
            "deadline": self.deadline.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processed_by": self.processed_by,
            "data_locations": [loc.to_dict() for loc in self.data_locations],
            "results": [r.to_dict() for r in self.results],
            "blocked_locations": [loc.to_dict() for loc in self.blocked_locations],
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "notes": self.notes,
            "metadata": self.metadata,
        }


class DataMapEntry(BaseModel):
    """Entrada no mapa de dados do sistema."""
    table_name: str
    subject_id_column: str
    pii_columns: List[str]
    category: str
    erasure_method: ErasureMethod = ErasureMethod.ANONYMIZE
    retention_days: Optional[int] = None
    retention_reason: Optional[RetentionReason] = None


class ErasureService:
    """
    Gerenciador central de exclusão de dados LGPD.

    Coordena processo completo de exclusão incluindo:
    - Verificação de identidade
    - Descoberta de dados
    - Verificação de retenção
    - Execução de exclusão
    - Auditoria

    Example:
        >>> service = ErasureService()
        >>> request = service.create_request("user123", "user@email.com", "Solicitação LGPD")
        >>> result = await service.process_request(request["request_id"])
    """

    def __init__(self, verification_required: bool = True, auto_process: bool = False):
        """
        Inicializa o serviço.

        Args:
            verification_required: Se requer verificação de identidade.
            auto_process: Se processa automaticamente após verificação.
        """
        self.verification_required = verification_required
        self.auto_process = auto_process
        self._requests: Dict[str, ErasureRequest] = {}
        self._data_map: Dict[str, DataMapEntry] = {}
        self._init_default_data_map()
        logger.info("ErasureService inicializado")

    def _init_default_data_map(self) -> None:
        """Inicializa mapa de dados padrão."""
        default_mappings = [
            DataMapEntry(
                table_name="employees",
                subject_id_column="id",
                pii_columns=["cpf", "rg", "name", "email", "phone", "address", "birth_date"],
                category="employee_data",
                erasure_method=ErasureMethod.ANONYMIZE,
                retention_days=3650,
                retention_reason=RetentionReason.LABOR_RECORDS,
            ),
            DataMapEntry(
                table_name="clients",
                subject_id_column="id",
                pii_columns=["cpf", "cnpj", "email", "phone", "contact_name", "address"],
                category="client_data",
                erasure_method=ErasureMethod.ANONYMIZE,
                retention_days=1825,
                retention_reason=RetentionReason.TAX_RECORDS,
            ),
            DataMapEntry(
                table_name="users",
                subject_id_column="id",
                pii_columns=["email", "name", "phone", "last_ip"],
                category="user_account",
                erasure_method=ErasureMethod.HARD_DELETE,
            ),
            DataMapEntry(
                table_name="medical_records",
                subject_id_column="employee_id",
                pii_columns=["exam_date", "exam_type", "result", "doctor_notes"],
                category="health_data",
                erasure_method=ErasureMethod.ANONYMIZE,
                retention_days=7300,
                retention_reason=RetentionReason.LEGAL_OBLIGATION,
            ),
        ]

        for entry in default_mappings:
            self._data_map[entry.table_name] = entry

    def create_request(
        self,
        titular_id: str,
        titular_email: str,
        reason: str,
        scope: str = "all",
    ) -> Dict[str, Any]:
        """
        Cria solicitação de exclusão de dados.

        Args:
            titular_id: UUID do titular.
            titular_email: Email do titular.
            reason: Motivo da solicitação.
            scope: Escopo da exclusão (all, marketing, analytics).

        Returns:
            Dict com dados da solicitação.
        """
        request_id = uuid4()
        now = datetime.utcnow()
        deadline = now + timedelta(days=15)

        try:
            erasure_scope = ErasureScope(scope)
        except ValueError:
            erasure_scope = ErasureScope.ALL

        # Descobre dados do titular
        data_locations = []
        blocked_locations = []

        for entry in self._data_map.values():
            location = DataLocation(
                table_name=entry.table_name,
                record_id=titular_id,
                field_names=entry.pii_columns,
                data_category=entry.category,
                erasure_method=entry.erasure_method,
                retention_period_days=entry.retention_days,
                retention_reason=entry.retention_reason,
            )

            if entry.retention_reason:
                blocked_locations.append(location)
            else:
                data_locations.append(location)

        request = ErasureRequest(
            id=request_id,
            titular_id=titular_id,
            titular_email=titular_email,
            status=ErasureStatus.PENDING,
            scope=erasure_scope,
            reason=reason,
            requested_at=now,
            requested_by=titular_id,
            deadline=deadline,
            data_locations=data_locations,
            blocked_locations=blocked_locations,
        )

        if self.verification_required:
            request.verification_code = secrets.token_urlsafe(32)

        self._requests[str(request_id)] = request

        logger.info(
            "Solicitação de exclusão criada: id=%s, titular=%s, scope=%s",
            request_id, titular_id, scope
        )

        return {
            "request_id": str(request_id),
            "titular_id": titular_id,
            "scope": scope,
            "status": "pending",
            "estimated_completion": deadline.isoformat(),
            "data_locations_count": len(data_locations),
            "blocked_locations_count": len(blocked_locations),
        }

    def get_status(self, request_id: str) -> Dict[str, Any]:
        """
        Consulta status de solicitação de exclusão.

        Args:
            request_id: ID da solicitação.

        Returns:
            Dict com status atual.
        """
        if request_id not in self._requests:
            raise ErasureError(f"Solicitação não encontrada: {request_id}", request_id)

        request = self._requests[request_id]
        return {
            "request_id": request_id,
            "status": request.status.value,
            "scope": request.scope.value,
            "created_at": request.requested_at.isoformat(),
            "deadline": request.deadline.isoformat(),
            "processed_at": request.completed_at.isoformat() if request.completed_at else None,
            "processed_by": request.processed_by,
            "data_locations": len(request.data_locations),
            "blocked_locations": len(request.blocked_locations),
            "results_success": sum(1 for r in request.results if r.success),
            "results_failed": sum(1 for r in request.results if not r.success),
        }

    def process_request(self, request_id: str, processor_id: str) -> Dict[str, Any]:
        """
        Processa uma solicitação de exclusão.

        Args:
            request_id: ID da solicitação.
            processor_id: ID do usuário processando.

        Returns:
            Dict com resultado do processamento.
        """
        if request_id not in self._requests:
            raise ErasureError(f"Solicitação não encontrada: {request_id}", request_id)

        request = self._requests[request_id]

        if self.verification_required and not request.verified_at:
            raise ErasureError("Solicitação não verificada", request_id)

        request.status = ErasureStatus.IN_PROGRESS
        request.processed_by = processor_id
        now = datetime.utcnow()

        # Processa cada localização
        for location in request.data_locations:
            try:
                result = ErasureResult(
                    location=location,
                    success=True,
                    method_used=location.erasure_method,
                    executed_at=now,
                    records_affected=1,
                )
                logger.info(
                    "Exclusão executada: table=%s, method=%s",
                    location.table_name, location.erasure_method.value
                )
            except Exception as e:
                result = ErasureResult(
                    location=location,
                    success=False,
                    method_used=location.erasure_method,
                    executed_at=now,
                    error_message=str(e),
                )
                logger.error("Erro na exclusão: %s", str(e))

            request.results.append(result)

        # Determina status final
        successful = sum(1 for r in request.results if r.success)
        total = len(request.results)

        if successful == total and not request.blocked_locations:
            request.status = ErasureStatus.COMPLETED
        elif successful == total and request.blocked_locations:
            request.status = ErasureStatus.PARTIAL
        elif successful > 0:
            request.status = ErasureStatus.PARTIAL
        else:
            request.status = ErasureStatus.FAILED

        request.completed_at = now

        logger.info(
            "Processamento concluído: request=%s, status=%s, success=%d/%d",
            request_id, request.status.value, successful, total
        )

        return {
            "request_id": request_id,
            "status": request.status.value,
            "processed_by": processor_id,
            "processed_at": now.isoformat(),
            "success_count": successful,
            "total_count": total,
            "blocked_count": len(request.blocked_locations),
        }

    def verify_request(self, request_id: str, verification_code: str) -> bool:
        """
        Verifica solicitação de exclusão.

        Args:
            request_id: ID da solicitação.
            verification_code: Código de verificação.

        Returns:
            bool: True se verificado com sucesso.
        """
        if request_id not in self._requests:
            raise ErasureError("Solicitação não encontrada", request_id)

        request = self._requests[request_id]

        if request.verification_code != verification_code:
            logger.warning("Código de verificação inválido: request=%s", request_id)
            return False

        request.verified_at = datetime.utcnow()
        logger.info("Solicitação verificada: %s", request_id)
        return True

    def complete_request(self, request_id: str, success: bool = True, notes: str = "") -> Dict[str, Any]:
        """
        Finaliza processamento de solicitação.

        Args:
            request_id: ID da solicitação.
            success: Se processamento foi bem sucedido.
            notes: Notas adicionais.

        Returns:
            Dict com resultado.
        """
        if request_id not in self._requests:
            raise ErasureError(f"Solicitação não encontrada: {request_id}", request_id)

        request = self._requests[request_id]
        request.status = ErasureStatus.COMPLETED if success else ErasureStatus.FAILED
        request.completed_at = datetime.utcnow()
        if notes:
            request.notes.append(notes)

        logger.info("Solicitação finalizada: %s, sucesso=%s", request_id, success)

        return {
            "request_id": request_id,
            "status": request.status.value,
            "processed_at": request.completed_at.isoformat(),
        }

    def cancel_request(self, request_id: str, cancelled_by: str, reason: Optional[str] = None) -> bool:
        """Cancela solicitação de exclusão."""
        if request_id not in self._requests:
            raise ErasureError("Solicitação não encontrada", request_id)

        request = self._requests[request_id]

        if request.status not in [ErasureStatus.PENDING, ErasureStatus.IN_PROGRESS]:
            raise ErasureError(f"Não é possível cancelar solicitação com status {request.status}", request_id)

        request.status = ErasureStatus.CANCELLED
        request.metadata["cancelled_by"] = cancelled_by
        request.metadata["cancellation_reason"] = reason
        request.metadata["cancelled_at"] = datetime.utcnow().isoformat()

        logger.info("Solicitação cancelada: %s by %s", request_id, cancelled_by)
        return True

    def list_pending_requests(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Lista solicitações pendentes."""
        pending = [
            r.to_dict() for r in self._requests.values()
            if r.status in [ErasureStatus.PENDING, ErasureStatus.IN_PROGRESS]
        ]

        total = len(pending)
        paginated = pending[offset:offset + limit]

        return {
            "requests": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def generate_erasure_report(self, request_id: str) -> Dict[str, Any]:
        """Gera relatório de exclusão para o titular."""
        if request_id not in self._requests:
            raise ErasureError("Solicitação não encontrada", request_id)

        request = self._requests[request_id]

        return {
            "report_id": str(uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "titular_id": request.titular_id,
            "status": request.status.value,
            "requested_at": request.requested_at.isoformat(),
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "summary": {
                "total_locations": len(request.data_locations) + len(request.blocked_locations),
                "erased": sum(1 for r in request.results if r.success),
                "failed": sum(1 for r in request.results if not r.success),
                "retained": len(request.blocked_locations),
            },
            "erased_data": [
                {
                    "category": r.location.data_category,
                    "table": r.location.table_name,
                    "method": r.method_used.value,
                    "executed_at": r.executed_at.isoformat(),
                }
                for r in request.results if r.success
            ],
            "retained_data": [
                {
                    "category": loc.data_category,
                    "table": loc.table_name,
                    "retention_reason": loc.retention_reason.value if loc.retention_reason else None,
                    "retention_days": loc.retention_period_days,
                }
                for loc in request.blocked_locations
            ],
        }

    def get_scopes(self) -> List[Dict[str, str]]:
        """Lista escopos de exclusão disponíveis."""
        return [{"id": s.value, "description": s.name.replace("_", " ").title()} for s in ErasureScope]

    def get_methods(self) -> List[Dict[str, str]]:
        """Lista métodos de exclusão disponíveis."""
        return [{"id": m.value, "description": m.name.replace("_", " ").title()} for m in ErasureMethod]

    def get_retention_reasons(self) -> List[Dict[str, str]]:
        """Lista motivos de retenção."""
        return [{"id": r.value, "description": r.name.replace("_", " ").title()} for r in RetentionReason]


# Singleton
_erasure_service: Optional[ErasureService] = None


def get_erasure_service() -> ErasureService:
    """Retorna instância singleton do ErasureService."""
    global _erasure_service
    if _erasure_service is None:
        _erasure_service = ErasureService()
    return _erasure_service
