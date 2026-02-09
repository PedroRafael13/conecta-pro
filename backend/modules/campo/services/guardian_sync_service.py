"""
Serviço de Sincronização com Conecta Guardian.

Gerencia a comunicação bidirecional entre o ERP e o sistema Guardian.
"""

import logging
from datetime import datetime, timedelta

from modules.campo.models.guardian_sync import (
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)

logger = logging.getLogger(__name__)


class GuardianSyncService:
    """
    Serviço de sincronização com Conecta Guardian.

    Responsável por:
    - Preparar dados para envio ao Guardian
    - Processar dados recebidos do Guardian
    - Gerenciar retentativas de sincronização
    - Validar payloads de sincronização
    """

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self._initialized = True
        self._guardian_base_url: str | None = None
        self._api_key: str | None = None

    def configure(self, base_url: str, api_key: str) -> None:
        """Configura conexão com Guardian."""
        self._guardian_base_url = base_url
        self._api_key = api_key
        logger.info("Guardian sync service configured")

    def prepare_contract_payload(
        self,
        contract_id: str,
        client_id: str,
        client_name: str,
        address: str,
        services: list[str],
        start_date: datetime,
        end_date: datetime | None = None,
        posts: list[dict] | None = None,
        employees: list[dict] | None = None,
    ) -> dict:
        """
        Prepara payload de contrato para envio ao Guardian.

        Args:
            contract_id: ID do contrato no ERP
            client_id: ID do cliente
            client_name: Nome do cliente
            address: Endereço do cliente
            services: Lista de serviços contratados
            start_date: Data de início do contrato
            end_date: Data de fim do contrato
            posts: Lista de postos
            employees: Lista de funcionários alocados

        Returns:
            Payload formatado para API do Guardian
        """
        payload = {
            "contract_id": contract_id,
            "client_id": client_id,
            "client_name": client_name,
            "address": address,
            "services": services,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "posts": posts or [],
            "employees": employees or [],
            "sync_timestamp": datetime.utcnow().isoformat(),
            "source": "erp_conecta_mais",
        }

        logger.debug("Contract payload prepared: %s", contract_id)
        return payload

    def prepare_authorized_person_payload(
        self,
        person_id: str,
        client_id: str,
        name: str,
        document: str,
        person_type: str,
        unit_code: str | None = None,
        access_type: str = "full",
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
        photo_url: str | None = None,
        vehicle_plates: list[str] | None = None,
    ) -> dict:
        """
        Prepara payload de pessoa autorizada para envio ao Guardian.

        Args:
            person_id: ID da pessoa no ERP
            client_id: ID do cliente/condomínio
            name: Nome da pessoa
            document: CPF/RG
            person_type: Tipo (morador, funcionario, prestador)
            unit_code: Código da unidade (se morador)
            access_type: Tipo de acesso (full, restricted, visitor)
            valid_from: Início da autorização
            valid_until: Fim da autorização
            photo_url: URL da foto
            vehicle_plates: Placas de veículos autorizados

        Returns:
            Payload formatado para API do Guardian
        """
        payload = {
            "person_id": person_id,
            "client_id": client_id,
            "name": name,
            "document": document,
            "person_type": person_type,
            "unit_code": unit_code,
            "access_type": access_type,
            "valid_from": valid_from.isoformat() if valid_from else None,
            "valid_until": valid_until.isoformat() if valid_until else None,
            "photo_url": photo_url,
            "vehicle_plates": vehicle_plates or [],
            "is_active": True,
            "sync_timestamp": datetime.utcnow().isoformat(),
            "source": "erp_conecta_mais",
        }

        logger.debug("Authorized person payload prepared: %s", person_id)
        return payload

    def prepare_access_config_payload(
        self,
        client_id: str,
        post_id: str,
        access_points: list[dict],
        schedules: list[dict] | None = None,
        rules: list[dict] | None = None,
    ) -> dict:
        """
        Prepara payload de configuração de acesso para envio ao Guardian.

        Args:
            client_id: ID do cliente
            post_id: ID do posto
            access_points: Lista de pontos de acesso
            schedules: Horários de funcionamento
            rules: Regras de acesso

        Returns:
            Payload formatado para API do Guardian
        """
        payload = {
            "client_id": client_id,
            "post_id": post_id,
            "access_points": access_points,
            "schedules": schedules or [],
            "rules": rules or [],
            "sync_timestamp": datetime.utcnow().isoformat(),
            "source": "erp_conecta_mais",
        }

        logger.debug("Access config payload prepared for post: %s", post_id)
        return payload

    def validate_occurrence_payload(self, payload: dict) -> tuple[bool, str | None]:
        """
        Valida payload de ocorrência recebido do Guardian.

        Args:
            payload: Dados da ocorrência

        Returns:
            Tupla (válido, mensagem de erro)
        """
        required_fields = [
            "guardian_id",
            "occurrence_type",
            "severity",
            "client_id",
            "title",
            "description",
            "event_timestamp",
        ]

        for field in required_fields:
            if field not in payload or payload[field] is None:
                return False, f"Campo obrigatório ausente: {field}"

        valid_severities = ["low", "medium", "high", "critical"]
        if payload.get("severity") not in valid_severities:
            return False, f"Gravidade inválida: {payload.get('severity')}"

        return True, None

    def validate_access_log_payload(self, payload: dict) -> tuple[bool, str | None]:
        """
        Valida payload de log de acesso recebido do Guardian.

        Args:
            payload: Dados do log de acesso

        Returns:
            Tupla (válido, mensagem de erro)
        """
        required_fields = [
            "guardian_id",
            "log_type",
            "client_id",
            "person_name",
            "event_timestamp",
        ]

        for field in required_fields:
            if field not in payload or payload[field] is None:
                return False, f"Campo obrigatório ausente: {field}"

        valid_types = [
            "entry",
            "exit",
            "denied",
            "visitor",
            "delivery",
            "service",
            "emergency",
            "patrol",
            "intercom",
        ]
        if payload.get("log_type") not in valid_types:
            return False, f"Tipo de log inválido: {payload.get('log_type')}"

        return True, None

    def validate_equipment_status_payload(
        self,
        payload: dict,
    ) -> tuple[bool, str | None]:
        """
        Valida payload de status de equipamento recebido do Guardian.

        Args:
            payload: Dados do status

        Returns:
            Tupla (válido, mensagem de erro)
        """
        required_fields = [
            "guardian_id",
            "equipment_id",
            "equipment_type",
            "equipment_name",
            "status",
            "client_id",
        ]

        for field in required_fields:
            if field not in payload or payload[field] is None:
                return False, f"Campo obrigatório ausente: {field}"

        valid_statuses = [
            "online",
            "offline",
            "warning",
            "error",
            "maintenance",
            "disabled",
        ]
        if payload.get("status") not in valid_statuses:
            return False, f"Status inválido: {payload.get('status')}"

        return True, None

    def calculate_retry_delay(self, retry_count: int) -> timedelta:
        """
        Calcula delay para próxima tentativa usando backoff exponencial.

        Args:
            retry_count: Número de tentativas já realizadas

        Returns:
            Intervalo até próxima tentativa
        """
        base_delay = 60  # 1 minuto
        max_delay = 3600  # 1 hora

        delay_seconds = min(base_delay * (2**retry_count), max_delay)
        return timedelta(seconds=delay_seconds)

    def get_sync_priority(
        self,
        entity_type: SyncEntityType,
        _direction: SyncDirection,
    ) -> int:
        """
        Determina prioridade de sincronização.

        Args:
            entity_type: Tipo de entidade
            _direction: Direção da sincronização

        Returns:
            Prioridade (menor = mais prioritário)
        """
        priorities = {
            SyncEntityType.OCCURRENCE: 1,
            SyncEntityType.ACCESS_LOG: 2,
            SyncEntityType.EQUIPMENT_STATUS: 3,
            SyncEntityType.AUTHORIZED_PERSON: 4,
            SyncEntityType.CONTRACT: 5,
            SyncEntityType.CLIENT: 6,
            SyncEntityType.POST: 7,
            SyncEntityType.EMPLOYEE: 8,
            SyncEntityType.ACCESS_CONFIG: 9,
            SyncEntityType.EVENT_MEDIA: 10,
            SyncEntityType.ATTENDANCE_REPORT: 11,
        }
        return priorities.get(entity_type, 99)

    def should_retry(
        self,
        status: SyncStatus,
        retry_count: int,
        max_retries: int,
        error_message: str | None = None,
    ) -> bool:
        """
        Determina se deve tentar novamente.

        Args:
            status: Status atual
            retry_count: Tentativas realizadas
            max_retries: Máximo de tentativas
            error_message: Mensagem de erro

        Returns:
            True se deve tentar novamente
        """
        if status != SyncStatus.FAILED:
            return False

        if retry_count >= max_retries:
            return False

        # Não tenta novamente para erros permanentes
        permanent_errors = [
            "not found",
            "unauthorized",
            "forbidden",
            "invalid payload",
            "duplicate",
        ]

        if error_message:
            error_lower = error_message.lower()
            if any(err in error_lower for err in permanent_errors):
                return False

        return True

    def format_sync_summary(
        self,
        total: int,
        completed: int,
        failed: int,
        pending: int,
    ) -> dict:
        """
        Formata resumo de sincronização.

        Args:
            total: Total de sincronizações
            completed: Concluídas
            failed: Falhas
            pending: Pendentes

        Returns:
            Dicionário com resumo formatado
        """
        success_rate = (completed / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "in_progress": total - completed - failed - pending,
            "success_rate": round(success_rate, 2),
            "health": "healthy" if success_rate >= 95 else ("warning" if success_rate >= 80 else "critical"),
            "generated_at": datetime.utcnow().isoformat(),
        }


# Instância singleton
guardian_sync_service = GuardianSyncService()
