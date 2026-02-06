"""
Trigger Service - Gerenciamento de triggers de workflow.

Processa eventos, webhooks e agendamentos para disparar workflows.
"""

import asyncio
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
import uuid

from modules._deprecated_workflows_dataclass.models.trigger import (
    DataChangeConfig,
    ScheduleConfig,
    ScheduleFrequency,
    Trigger,
    TriggerEvent,
    TriggerType,
    WebhookConfig,
)
from modules._deprecated_workflows_dataclass.models.workflow import Workflow

logger = logging.getLogger(__name__)


class TriggerRegistry:
    """Registro de triggers ativos."""

    def __init__(self):
        self._triggers: Dict[str, Trigger] = {}
        self._event_handlers: Dict[str, List[str]] = {}  # event -> [trigger_ids]
        self._webhook_handlers: Dict[str, str] = {}  # webhook_id -> trigger_id
        self._data_handlers: Dict[str, List[str]] = {}  # entity_type -> [trigger_ids]

    def register(self, trigger: Trigger) -> None:
        """Registra trigger."""
        self._triggers[trigger.id] = trigger

        if trigger.trigger_type == TriggerType.EVENT:
            event_key = trigger.event.value if trigger.event else trigger.custom_event
            if event_key not in self._event_handlers:
                self._event_handlers[event_key] = []
            if trigger.id not in self._event_handlers[event_key]:
                self._event_handlers[event_key].append(trigger.id)

        elif trigger.trigger_type == TriggerType.WEBHOOK:
            self._webhook_handlers[trigger.id] = trigger.id

        elif trigger.trigger_type == TriggerType.DATA_CHANGE:
            if trigger.data_change_config:
                entity = trigger.data_change_config.entity_type
                if entity not in self._data_handlers:
                    self._data_handlers[entity] = []
                if trigger.id not in self._data_handlers[entity]:
                    self._data_handlers[entity].append(trigger.id)

    def unregister(self, trigger_id: str) -> None:
        """Remove trigger."""
        trigger = self._triggers.pop(trigger_id, None)
        if not trigger:
            return

        # Remove de handlers
        for handlers in self._event_handlers.values():
            if trigger_id in handlers:
                handlers.remove(trigger_id)

        self._webhook_handlers.pop(trigger_id, None)

        for handlers in self._data_handlers.values():
            if trigger_id in handlers:
                handlers.remove(trigger_id)

    def get_trigger(self, trigger_id: str) -> Optional[Trigger]:
        """Obtem trigger por ID."""
        return self._triggers.get(trigger_id)

    def get_triggers_for_event(self, event: str) -> List[Trigger]:
        """Obtem triggers para evento."""
        trigger_ids = self._event_handlers.get(event, [])
        return [
            self._triggers[tid]
            for tid in trigger_ids
            if tid in self._triggers
        ]

    def get_triggers_for_data_change(self, entity_type: str) -> List[Trigger]:
        """Obtem triggers para mudanca de dados."""
        trigger_ids = self._data_handlers.get(entity_type, [])
        return [
            self._triggers[tid]
            for tid in trigger_ids
            if tid in self._triggers
        ]


class TriggerService:
    """
    Servico de gerenciamento de triggers.

    Responsavel por:
    - Registrar e gerenciar triggers
    - Processar eventos do sistema
    - Validar webhooks
    - Calcular proximas execucoes de schedules
    """

    def __init__(self):
        self.registry = TriggerRegistry()
        self._workflow_executor: Optional[Callable] = None
        self._scheduled_tasks: Dict[str, asyncio.Task] = {}

    def set_executor(self, executor: Callable) -> None:
        """Define executor de workflows."""
        self._workflow_executor = executor

    async def register_trigger(self, trigger: Trigger, workflow: Workflow) -> bool:
        """
        Registra trigger para workflow.

        Args:
            trigger: Trigger a registrar
            workflow: Workflow associado

        Returns:
            True se registrado com sucesso
        """
        if not trigger.is_enabled:
            logger.info(f"Trigger {trigger.id} desabilitado, nao registrado")
            return False

        trigger.workflow_id = workflow.id
        self.registry.register(trigger)

        # Se for schedule, inicia task
        if trigger.trigger_type == TriggerType.SCHEDULE:
            await self._start_schedule_task(trigger)

        logger.info(
            f"Trigger {trigger.id} ({trigger.trigger_type.value}) "
            f"registrado para workflow {workflow.name}"
        )
        return True

    async def unregister_trigger(self, trigger_id: str) -> bool:
        """Remove registro de trigger."""
        # Cancela task de schedule se existir
        if trigger_id in self._scheduled_tasks:
            self._scheduled_tasks[trigger_id].cancel()
            del self._scheduled_tasks[trigger_id]

        self.registry.unregister(trigger_id)
        logger.info(f"Trigger {trigger_id} removido")
        return True

    async def process_event(
        self,
        event_name: str,
        event_data: Dict[str, Any],
    ) -> List[str]:
        """
        Processa evento do sistema.

        Args:
            event_name: Nome do evento
            event_data: Dados do evento

        Returns:
            Lista de IDs de execucoes iniciadas
        """
        execution_ids = []

        triggers = self.registry.get_triggers_for_event(event_name)

        for trigger in triggers:
            if not trigger.is_enabled or not trigger.can_trigger:
                continue

            if trigger.matches_event(event_name, event_data):
                exec_id = await self._execute_workflow(trigger, event_data)
                if exec_id:
                    execution_ids.append(exec_id)
                    trigger.record_trigger()

        logger.info(
            f"Evento {event_name} processado, "
            f"{len(execution_ids)} workflows disparados"
        )
        return execution_ids

    async def process_webhook(
        self,
        trigger_id: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        remote_ip: str = "",
    ) -> Dict[str, Any]:
        """
        Processa chamada de webhook.

        Args:
            trigger_id: ID do trigger webhook
            payload: Dados da requisicao
            headers: Headers da requisicao
            remote_ip: IP de origem

        Returns:
            Resultado do processamento
        """
        trigger = self.registry.get_trigger(trigger_id)

        if not trigger:
            return {"error": "Trigger nao encontrado", "status": 404}

        if trigger.trigger_type != TriggerType.WEBHOOK:
            return {"error": "Trigger nao e webhook", "status": 400}

        if not trigger.is_enabled:
            return {"error": "Trigger desabilitado", "status": 403}

        if not trigger.can_trigger:
            return {"error": "Cooldown ativo", "status": 429}

        # Valida webhook
        if not trigger.validate_webhook(headers, remote_ip):
            return {"error": "Validacao falhou", "status": 401}

        # Valida assinatura se configurado
        if trigger.webhook_config and trigger.webhook_config.validate_signature:
            signature = headers.get(trigger.webhook_config.signature_header, "")
            if not self._validate_signature(
                payload,
                signature,
                trigger.webhook_config.secret_key,
            ):
                return {"error": "Assinatura invalida", "status": 401}

        # Executa workflow
        exec_id = await self._execute_workflow(trigger, payload)
        trigger.record_trigger()

        return {
            "status": 200,
            "execution_id": exec_id,
            "message": "Workflow iniciado",
        }

    async def process_data_change(
        self,
        entity_type: str,
        entity_id: str,
        operation: str,
        old_data: Dict[str, Any] = None,
        new_data: Dict[str, Any] = None,
    ) -> List[str]:
        """
        Processa mudanca de dados.

        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade
            operation: Operacao (create, update, delete)
            old_data: Dados anteriores
            new_data: Novos dados

        Returns:
            Lista de IDs de execucoes iniciadas
        """
        execution_ids = []

        triggers = self.registry.get_triggers_for_data_change(entity_type)

        for trigger in triggers:
            if not trigger.is_enabled or not trigger.can_trigger:
                continue

            config = trigger.data_change_config
            if not config:
                continue

            # Verifica operacao
            if config.operations and operation not in config.operations:
                continue

            # Verifica ID especifico
            if config.entity_id and config.entity_id != entity_id:
                continue

            # Verifica campos alterados
            if config.fields and old_data and new_data:
                changed_fields = [
                    f for f in config.fields
                    if old_data.get(f) != new_data.get(f)
                ]
                if not changed_fields:
                    continue

            # Prepara dados
            event_data = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "operation": operation,
                "old_data": old_data or {},
                "new_data": new_data or {},
            }

            exec_id = await self._execute_workflow(trigger, event_data)
            if exec_id:
                execution_ids.append(exec_id)
                trigger.record_trigger()

        return execution_ids

    async def _execute_workflow(
        self,
        trigger: Trigger,
        input_data: Dict[str, Any],
    ) -> Optional[str]:
        """Executa workflow associado ao trigger."""
        if not self._workflow_executor:
            logger.error("Executor de workflow nao configurado")
            return None

        # Mapeia input
        mapped_input = self._map_input(trigger, input_data)

        try:
            return await self._workflow_executor(
                workflow_id=trigger.workflow_id,
                trigger_id=trigger.id,
                input_data=mapped_input,
            )
        except Exception as e:
            logger.error(f"Erro ao executar workflow: {e}")
            return None

    def _map_input(
        self,
        trigger: Trigger,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mapeia dados de entrada."""
        if not trigger.input_mapping:
            return input_data

        mapped = {}
        for target_key, source_path in trigger.input_mapping.items():
            value = self._get_value_by_path(input_data, source_path)
            if value is not None:
                mapped[target_key] = value

        return mapped

    def _get_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """Obtem valor por path (ex: $.user.name)."""
        if not path:
            return None

        if path.startswith("$."):
            path = path[2:]

        parts = path.split(".")
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def _validate_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        secret: str,
    ) -> bool:
        """Valida assinatura HMAC."""
        if not signature or not secret:
            return False

        import json
        payload_str = json.dumps(payload, sort_keys=True)
        expected = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    async def _start_schedule_task(self, trigger: Trigger) -> None:
        """Inicia task para trigger agendado."""
        if trigger.id in self._scheduled_tasks:
            self._scheduled_tasks[trigger.id].cancel()

        task = asyncio.create_task(
            self._schedule_loop(trigger)
        )
        self._scheduled_tasks[trigger.id] = task

    async def _schedule_loop(self, trigger: Trigger) -> None:
        """Loop de agendamento."""
        while trigger.is_enabled:
            try:
                next_run = self.get_next_run_time(trigger)

                if not next_run:
                    logger.info(f"Schedule {trigger.id} sem proxima execucao")
                    break

                # Calcula delay
                now = datetime.utcnow()
                if next_run <= now:
                    delay = 0
                else:
                    delay = (next_run - now).total_seconds()

                logger.debug(
                    f"Schedule {trigger.id} aguardando {delay}s "
                    f"para proxima execucao em {next_run}"
                )

                await asyncio.sleep(delay)

                # Verifica se ainda esta habilitado
                current_trigger = self.registry.get_trigger(trigger.id)
                if not current_trigger or not current_trigger.is_enabled:
                    break

                # Executa
                if current_trigger.can_trigger:
                    await self._execute_workflow(current_trigger, {})
                    current_trigger.record_trigger()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no schedule {trigger.id}: {e}")
                await asyncio.sleep(60)  # Aguarda antes de tentar novamente

    def get_next_run_time(self, trigger: Trigger) -> Optional[datetime]:
        """
        Calcula proxima execucao para trigger agendado.

        Args:
            trigger: Trigger com schedule_config

        Returns:
            Data/hora da proxima execucao
        """
        config = trigger.schedule_config
        if not config:
            return None

        now = datetime.utcnow()

        # Verifica limites
        if config.start_date and now < config.start_date:
            return config.start_date

        if config.end_date and now > config.end_date:
            return None

        if config.max_runs and trigger.trigger_count >= config.max_runs:
            return None

        freq = config.frequency

        if freq == ScheduleFrequency.ONCE:
            if trigger.trigger_count > 0:
                return None
            return config.run_at

        if freq == ScheduleFrequency.MINUTELY:
            return now + timedelta(minutes=config.interval)

        if freq == ScheduleFrequency.HOURLY:
            return now + timedelta(hours=config.interval)

        if freq == ScheduleFrequency.DAILY:
            next_run = now.replace(
                hour=config.time_of_day.hour if config.time_of_day else 0,
                minute=config.time_of_day.minute if config.time_of_day else 0,
                second=0,
                microsecond=0,
            )
            if next_run <= now:
                next_run += timedelta(days=config.interval)
            return next_run

        if freq == ScheduleFrequency.WEEKLY:
            if not config.days_of_week:
                return now + timedelta(weeks=1)

            # Encontra proximo dia da semana
            for i in range(7):
                check_date = now + timedelta(days=i)
                if check_date.weekday() in config.days_of_week:
                    next_run = check_date.replace(
                        hour=config.time_of_day.hour if config.time_of_day else 0,
                        minute=config.time_of_day.minute if config.time_of_day else 0,
                        second=0,
                    )
                    if next_run > now:
                        return next_run

            return now + timedelta(weeks=1)

        if freq == ScheduleFrequency.MONTHLY:
            next_run = now.replace(
                day=config.day_of_month,
                hour=config.time_of_day.hour if config.time_of_day else 0,
                minute=config.time_of_day.minute if config.time_of_day else 0,
                second=0,
            )
            if next_run <= now:
                # Proximo mes
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run

        if freq == ScheduleFrequency.CRON:
            # Implementacao basica de cron
            # Para producao, usar biblioteca como croniter
            return now + timedelta(minutes=1)

        return None

    def generate_webhook_url(self, trigger: Trigger, base_url: str) -> str:
        """Gera URL para webhook."""
        return f"{base_url}/api/v1/workflows/webhook/{trigger.id}"

    def generate_webhook_secret(self) -> str:
        """Gera secret para webhook."""
        return str(uuid.uuid4())
