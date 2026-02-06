"""
modules/fase5/core/orchestrator.py - ECOSYSTEM ORCHESTRATOR
============================================================
Orquestrador unificado que conecta todas as fases do Conecta PRO.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class PhaseType(str, Enum):
    """Enum para identificar as fases do sistema."""
    FASE1_CORE_BUSINESS = "fase1_core"
    FASE2_GESTAO_EMPRESARIAL = "fase2_gestao"
    FASE3_SEGURANCA_SAUDE_GOV = "fase3_security"
    FASE4_LICITACOES_INTELIGENTES = "fase4_bidding"
    FASE5_EMAIL_CCT_FINALE = "fase5_finale"


class SystemComponent(str, Enum):
    """Componentes principais de cada fase."""
    # Fase 1
    CONDOMINIOS = "condominios"
    PROPOSTAS_COMERCIAIS = "propostas_comerciais"
    # Fase 2
    RECURSOS_HUMANOS = "recursos_humanos"
    CONTABILIDADE = "contabilidade"
    FINANCEIRO = "financeiro"
    # Fase 3
    LGPD_COMPLIANCE = "lgpd_compliance"
    SAUDE_OCUPACIONAL = "saude_ocupacional"
    INTEGRACOES_GOV = "integracoes_gov"
    # Fase 4
    AI_ENGINE = "ai_engine"
    LICITACOES = "licitacoes"
    MARKETPLACE = "marketplace"
    # Fase 5
    EMAIL_INTELLIGENCE = "email_intelligence"
    CCT_COMPLIANCE = "cct_compliance"
    DOMAIN_MIGRATION = "domain_migration"
    MCP_SERVERS = "mcp_servers"


@dataclass
class SystemHealth:
    """Status de saude do sistema."""
    component: SystemComponent
    phase: PhaseType
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    error_rate: float
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossPhaseEvent:
    """Evento que percorre multiplas fases."""
    event_id: str
    event_type: str
    source_phase: PhaseType
    source_component: SystemComponent
    target_phases: List[PhaseType]
    data: Dict[str, Any]
    correlation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_by: List[PhaseType] = field(default_factory=list)


class IntegrationError(Exception):
    """Excecao para erros de integracao."""
    def __init__(
        self,
        message: str,
        phase: PhaseType,
        component: SystemComponent,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.phase = phase
        self.component = component
        self.details = details or {}
        super().__init__(self.message)


@runtime_checkable
class PhaseInterface(Protocol):
    """Interface que cada fase deve implementar."""

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa a fase."""
        ...

    async def health_check(self) -> SystemHealth:
        """Verifica saude dos componentes."""
        ...

    async def process_event(self, event: CrossPhaseEvent) -> Dict[str, Any]:
        """Processa evento cross-phase."""
        ...

    async def get_data_for_integration(
        self,
        component: SystemComponent,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retorna dados para integracao."""
        ...


class ConectaProOrchestrator:
    """
    Orquestrador principal que gerencia todas as fases do Conecta PRO.

    Responsabilidades:
    1. Coordenar comunicacao entre fases
    2. Monitorar saude do ecosystem
    3. Orquestrar workflows cross-phase
    4. Gerenciar eventos e notificacoes
    5. Garantir consistencia de dados
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.phases: Dict[PhaseType, PhaseInterface] = {}
        self.health_status: Dict[PhaseType, List[SystemHealth]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.correlation_tracker: Dict[str, List[CrossPhaseEvent]] = {}

    async def register_phase(
        self,
        phase_type: PhaseType,
        phase_implementation: PhaseInterface
    ) -> None:
        """Registra uma fase no orquestrador."""
        try:
            logger.info(f"Registering phase: {phase_type}")

            initialized = await phase_implementation.initialize(
                self.config.get(phase_type.value, {})
            )
            if not initialized:
                raise IntegrationError(
                    f"Failed to initialize phase {phase_type}",
                    phase_type,
                    SystemComponent.CONDOMINIOS
                )

            self.phases[phase_type] = phase_implementation
            logger.info(f"Phase {phase_type} registered successfully")

        except Exception as e:
            logger.error(f"Error registering phase {phase_type}: {e}")
            raise IntegrationError(
                f"Registration failed for {phase_type}",
                phase_type,
                SystemComponent.CONDOMINIOS
            )

    async def start_orchestrator(self) -> None:
        """Inicia o orquestrador."""
        logger.info("Starting Conecta PRO Orchestrator...")
        self.running = True

        tasks = [
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._event_processor()),
            asyncio.create_task(self._correlation_cleanup())
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            self.running = False
            raise

    async def stop_orchestrator(self) -> None:
        """Para o orquestrador."""
        logger.info("Stopping Conecta PRO Orchestrator...")
        self.running = False

    async def _health_monitor(self) -> None:
        """Monitor de saude continuo."""
        while self.running:
            try:
                for phase_type, phase in self.phases.items():
                    health = await phase.health_check()

                    if phase_type not in self.health_status:
                        self.health_status[phase_type] = []

                    self.health_status[phase_type].append(health)

                    if len(self.health_status[phase_type]) > 10:
                        self.health_status[phase_type] = self.health_status[phase_type][-10:]

                    if health.status != "healthy":
                        logger.warning(
                            f"Health issue in {phase_type}: {health.status}"
                        )

                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _event_processor(self) -> None:
        """Processador de eventos cross-phase."""
        while self.running:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                await self._process_cross_phase_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processor error: {e}")

    async def _correlation_cleanup(self) -> None:
        """Limpa correlacoes antigas."""
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                expired = []

                for corr_id, events in self.correlation_tracker.items():
                    if events:
                        age = (current_time - events[0].timestamp).total_seconds()
                        if age > 3600:
                            expired.append(corr_id)

                for corr_id in expired:
                    del self.correlation_tracker[corr_id]

                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Correlation cleanup error: {e}")

    async def _process_cross_phase_event(self, event: CrossPhaseEvent) -> None:
        """Processa evento que percorre multiplas fases."""
        try:
            logger.info(f"Processing event: {event.event_id} from {event.source_phase}")

            if event.correlation_id not in self.correlation_tracker:
                self.correlation_tracker[event.correlation_id] = []
            self.correlation_tracker[event.correlation_id].append(event)

            for target_phase in event.target_phases:
                if target_phase in self.phases and target_phase not in event.processed_by:
                    try:
                        phase = self.phases[target_phase]
                        result = await phase.process_event(event)
                        event.processed_by.append(target_phase)
                        logger.info(f"Event {event.event_id} processed by {target_phase}")

                    except Exception as e:
                        logger.error(
                            f"Error processing event {event.event_id} in {target_phase}: {e}"
                        )

        except Exception as e:
            logger.error(f"Cross-phase event processing error: {e}")

    async def publish_event(self, event: CrossPhaseEvent) -> None:
        """Publica evento cross-phase."""
        await self.event_queue.put(event)

    async def get_system_overview(self) -> Dict[str, Any]:
        """Retorna overview completo do sistema."""
        overview = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phases": {},
            "overall_health": "healthy",
            "active_correlations": len(self.correlation_tracker),
            "event_queue_size": self.event_queue.qsize()
        }

        for phase_type, health_list in self.health_status.items():
            if health_list:
                latest = health_list[-1]
                overview["phases"][phase_type.value] = {
                    "status": latest.status,
                    "component": latest.component.value,
                    "response_time_ms": latest.response_time_ms,
                    "error_rate": latest.error_rate,
                    "last_check": latest.last_check.isoformat()
                }

                if latest.status != "healthy":
                    overview["overall_health"] = "degraded"

        return overview


class WorkflowOrchestrator:
    """
    Orquestrador de workflows que integram multiplas fases.

    Workflows:
    1. Proposta Comercial Completa (Fases 1, 2, 3, 5)
    2. Admissao de Funcionario (Fases 2, 3, 5)
    3. Participacao em Licitacao (Fases 1, 2, 4, 5)
    """

    def __init__(self, orchestrator: ConectaProOrchestrator):
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Dict[str, Any]] = {}

    async def execute_proposta_comercial_workflow(
        self,
        dados_cliente: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Workflow completo para proposta comercial:
        1. Fase 1: Dados do condominio e proposta base
        2. Fase 2: Calculos financeiros e RH
        3. Fase 3: Verificacoes de compliance LGPD
        4. Fase 5: CCT compliance + contexto historico email
        """
        workflow_id = f"proposta_{dados_cliente.get('cnpj', 'unknown')}_{int(datetime.now().timestamp())}"
        correlation_id = f"correlation_{workflow_id}"

        try:
            logger.info(f"Starting proposta comercial workflow: {workflow_id}")

            # Fase 1: Core business
            fase1_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_fase1",
                event_type="proposta_comercial_dados",
                source_phase=PhaseType.FASE5_EMAIL_CCT_FINALE,
                source_component=SystemComponent.EMAIL_INTELLIGENCE,
                target_phases=[PhaseType.FASE1_CORE_BUSINESS],
                data=dados_cliente,
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase1_event)

            # Fase 2: Gestao empresarial
            fase2_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_fase2",
                event_type="calculos_financeiros_rh",
                source_phase=PhaseType.FASE1_CORE_BUSINESS,
                source_component=SystemComponent.PROPOSTAS_COMERCIAIS,
                target_phases=[PhaseType.FASE2_GESTAO_EMPRESARIAL],
                data={**dados_cliente, "fonte": "proposta_comercial"},
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase2_event)

            # Fase 3: Compliance
            fase3_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_fase3",
                event_type="verificacao_compliance",
                source_phase=PhaseType.FASE2_GESTAO_EMPRESARIAL,
                source_component=SystemComponent.CONTABILIDADE,
                target_phases=[PhaseType.FASE3_SEGURANCA_SAUDE_GOV],
                data={**dados_cliente, "check_lgpd": True},
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase3_event)

            # Fase 5: CCT + Email context
            fase5_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_fase5_cct",
                event_type="cct_compliance_check",
                source_phase=PhaseType.FASE3_SEGURANCA_SAUDE_GOV,
                source_component=SystemComponent.LGPD_COMPLIANCE,
                target_phases=[PhaseType.FASE5_EMAIL_CCT_FINALE],
                data={
                    **dados_cliente,
                    "cargos_solicitados": dados_cliente.get("cargos", []),
                    "regime_trabalho": dados_cliente.get("regime", "clt")
                },
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase5_event)

            return {
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "status": "initiated",
                "phases_involved": ["fase1", "fase2", "fase3", "fase5"]
            }

        except Exception as e:
            logger.error(f"Proposta comercial workflow error: {e}")
            raise IntegrationError(
                f"Workflow failed: {e}",
                PhaseType.FASE5_EMAIL_CCT_FINALE,
                SystemComponent.EMAIL_INTELLIGENCE
            )

    async def execute_admissao_funcionario_workflow(
        self,
        dados_funcionario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Workflow de admissao de funcionario:
        1. Fase 2: Cadastro RH e calculos trabalhistas
        2. Fase 3: PPRA/PCMSO e exames obrigatorios
        3. Fase 5: CCT compliance para cargo + email notificacoes
        """
        workflow_id = f"admissao_{dados_funcionario.get('cpf', 'unknown')}_{int(datetime.now().timestamp())}"
        correlation_id = f"correlation_{workflow_id}"

        try:
            logger.info(f"Starting admissao funcionario workflow: {workflow_id}")

            # Fase 2: RH
            fase2_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_rh",
                event_type="cadastro_funcionario",
                source_phase=PhaseType.FASE5_EMAIL_CCT_FINALE,
                source_component=SystemComponent.EMAIL_INTELLIGENCE,
                target_phases=[PhaseType.FASE2_GESTAO_EMPRESARIAL],
                data=dados_funcionario,
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase2_event)

            # Fase 3: Saude ocupacional
            fase3_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_saude",
                event_type="exames_admissionais",
                source_phase=PhaseType.FASE2_GESTAO_EMPRESARIAL,
                source_component=SystemComponent.RECURSOS_HUMANOS,
                target_phases=[PhaseType.FASE3_SEGURANCA_SAUDE_GOV],
                data={
                    **dados_funcionario,
                    "cargo": dados_funcionario.get("cargo"),
                    "tipo_exame": "admissional"
                },
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase3_event)

            # Fase 5: CCT compliance para cargo especifico
            fase5_event = CrossPhaseEvent(
                event_id=f"{workflow_id}_cct_cargo",
                event_type="validacao_cargo_cct",
                source_phase=PhaseType.FASE3_SEGURANCA_SAUDE_GOV,
                source_component=SystemComponent.SAUDE_OCUPACIONAL,
                target_phases=[PhaseType.FASE5_EMAIL_CCT_FINALE],
                data={
                    "funcionario": dados_funcionario,
                    "cargo_cct": dados_funcionario.get("cargo"),
                    "validar_salario": True,
                    "validar_beneficios": True
                },
                correlation_id=correlation_id
            )
            await self.orchestrator.publish_event(fase5_event)

            return {
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "status": "initiated",
                "phases_involved": ["fase2", "fase3", "fase5"],
                "next_steps": ["exames_medicos", "documentacao", "cct_validation"]
            }

        except Exception as e:
            logger.error(f"Admissao workflow error: {e}")
            raise IntegrationError(
                f"Admissao workflow failed: {e}",
                PhaseType.FASE5_EMAIL_CCT_FINALE,
                SystemComponent.CCT_COMPLIANCE
            )
