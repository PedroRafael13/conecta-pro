"""
Predictive Orchestra - Orquestrador de Predições Múltiplas

Gerencia e orquestra múltiplas predições de IA simultaneamente:
1. Queue de predições com prioridades
2. Gerenciamento de recursos computacionais
3. Resolução de conflitos entre predições
4. Otimização de performance
5. Circuit breaker para proteção

Versão adaptada para Conecta PRO
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import PriorityQueue
from typing import Any

logger = logging.getLogger(__name__)


class PredictionPriority(Enum):
    """Prioridades de predição"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class PredictionStatus(Enum):
    """Status de predição"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PredictionRequest:
    """Requisição de predição"""

    id: str
    module_name: str
    data_type: str
    data: dict[str, Any]
    priority: PredictionPriority
    tenant_id: str
    user_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    deadline: datetime | None = None
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """Para ordenação na queue (prioridade mais alta primeiro)"""
        return self.priority.value > other.priority.value


@dataclass
class PredictionResult:
    """Resultado de predição"""

    request_id: str
    status: PredictionStatus
    prediction: Any
    confidence: float
    processing_time: float
    error_message: str | None = None
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """Circuit breaker para proteção contra sobrecarga"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Verifica se pode executar operação"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def record_success(self):
        """Registra sucesso"""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Registra falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class PredictiveOrchestra:
    """
    Orquestrador de Predições para a Central de IA do Conecta PRO

    Funcionalidades:
    - Queue de predições com prioridades
    - Processamento paralelo otimizado
    - Resolução de conflitos
    - Circuit breaker para proteção
    - Métricas de performance
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.prediction_queue = PriorityQueue()
        self.active_predictions: dict[str, PredictionRequest] = {}
        self.completed_predictions: dict[str, PredictionResult] = {}
        self.circuit_breaker = CircuitBreaker()

        # Métricas
        self.metrics = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "average_processing_time": 0.0,
            "queue_size": 0,
        }

        # Workers
        self.workers: list[asyncio.Task] = []
        self.running = False

        # Módulos e tipos conhecidos do Conecta PRO
        self.known_modules = [
            "ai",
            "analytics",
            "audit",
            "automation",
            "bidding",
            "clients",
            "config",
            "core",
            "crm",
            "diarists",
            "document_kits",
            "documents",
            "equipment_management",
            "facilities",
            "fase5",
            "field_service",
            "financial",
            "ged",
            "government_integrations",
            "health_occupational",
            "hr",
            "integrations",
            "marketplace",
            "mobile",
            "monitoring",
            "notifications",
            "occurrences",
            "operations",
            "recruitment",
            "reports",
            "scheduler",
            "security_lgpd",
            "services",
        ]

    async def start(self):
        """Inicia o orquestrador"""
        if self.running:
            return

        self.running = True

        # Criar workers
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker_{i}"))
            self.workers.append(worker)

        logger.info(f"Predictive Orchestra iniciado com {self.max_workers} workers")

    async def stop(self):
        """Para o orquestrador"""
        self.running = False

        # Cancelar workers
        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Predictive Orchestra parado")

    async def submit_prediction(self, request: PredictionRequest) -> str:
        """
        Submete uma predição para a queue
        """
        try:
            # Validar requisição
            if not await self._validate_request(request):
                raise ValueError("Requisição inválida")

            # Verificar circuit breaker
            if not self.circuit_breaker.can_execute():
                raise Exception("Sistema temporariamente indisponível (circuit breaker ativo)")

            # Detectar conflitos
            conflicts = await self._detect_conflicts(request)
            if conflicts:
                resolution = await self._resolve_conflicts(request, conflicts)
                if not resolution:
                    raise Exception("Conflito não resolvido")

            # Adicionar à queue
            self.prediction_queue.put(request)
            self.active_predictions[request.id] = request

            # Atualizar métricas
            self.metrics["total_predictions"] += 1
            self.metrics["queue_size"] = self.prediction_queue.qsize()

            logger.info(f"Predição {request.id} adicionada à queue")
            return request.id

        except Exception as e:
            logger.error(f"Erro ao submeter predição: {e}")
            raise

    async def get_prediction_status(self, prediction_id: str) -> dict[str, Any] | None:
        """Obtém status de uma predição"""

        # Verificar se está ativa
        if prediction_id in self.active_predictions:
            request = self.active_predictions[prediction_id]
            return {
                "id": prediction_id,
                "status": "processing" if request.id in [r.id for r in list(self.prediction_queue.queue)] else "queued",
                "module": request.module_name,
                "priority": request.priority.name,
                "created_at": request.created_at.isoformat(),
            }

        # Verificar se está completa
        if prediction_id in self.completed_predictions:
            result = self.completed_predictions[prediction_id]
            return {
                "id": prediction_id,
                "status": result.status.value,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "completed_at": result.completed_at.isoformat(),
            }

        return None

    async def get_queue_status(self) -> dict[str, Any]:
        """Obtém status da queue"""
        queue_items = list(self.prediction_queue.queue)

        return {
            "queue_size": len(queue_items),
            "active_predictions": len(self.active_predictions),
            "completed_predictions": len(self.completed_predictions),
            "workers_active": len([w for w in self.workers if not w.done()]),
            "circuit_breaker_state": self.circuit_breaker.state,
            "metrics": self.metrics,
            "queue_by_priority": self._analyze_queue_priorities(queue_items),
        }

    async def _worker(self, worker_name: str):
        """Worker que processa predições da queue"""
        logger.info(f"Worker {worker_name} iniciado")

        while self.running:
            try:
                # Tentar pegar item da queue (timeout para permitir parada)
                try:
                    request = self.prediction_queue.get(timeout=1)
                except Exception:  # noqa: S112
                    continue

                # Processar predição
                start_time = time.time()
                result = await self._process_prediction(request)
                processing_time = time.time() - start_time

                # Registrar resultado
                result.processing_time = processing_time
                self.completed_predictions[request.id] = result

                # Remover da lista ativa
                if request.id in self.active_predictions:
                    del self.active_predictions[request.id]

                # Atualizar métricas
                if result.status == PredictionStatus.COMPLETED:
                    self.metrics["successful_predictions"] += 1
                    self.circuit_breaker.record_success()
                else:
                    self.metrics["failed_predictions"] += 1
                    self.circuit_breaker.record_failure()

                # Atualizar tempo médio
                total = self.metrics["successful_predictions"] + self.metrics["failed_predictions"]
                if total > 0:
                    self.metrics["average_processing_time"] = (
                        self.metrics["average_processing_time"] * (total - 1) + processing_time
                    ) / total

                self.metrics["queue_size"] = self.prediction_queue.qsize()

                logger.info(f"Worker {worker_name} processou {request.id} em {processing_time:.2f}s")

            except Exception as e:
                logger.error(f"Erro no worker {worker_name}: {e}")
                await asyncio.sleep(1)

    async def _process_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Processa uma predição individual"""
        try:
            # Simular processamento de IA (em produção, chamaria UnifiedAIEngine)
            await asyncio.sleep(0.1)  # Simular processamento

            # Gerar predição simulada baseada no módulo
            prediction = await self._generate_mock_prediction(request)
            confidence = 0.85  # Confiança simulada

            return PredictionResult(
                request_id=request.id,
                status=PredictionStatus.COMPLETED,
                prediction=prediction,
                confidence=confidence,
                processing_time=0.0,  # Será preenchido pelo worker
                insights=[f"Análise de {request.module_name} concluída", "Padrões identificados"],
                recommendations=[f"Implementar ações baseadas na análise de {request.module_name}"],
            )

        except Exception as e:
            logger.error(f"Erro no processamento da predição {request.id}: {e}")
            return PredictionResult(
                request_id=request.id,
                status=PredictionStatus.FAILED,
                prediction=None,
                confidence=0.0,
                processing_time=0.0,
                error_message=str(e),
            )

    async def _generate_mock_prediction(self, request: PredictionRequest) -> Any:
        """Gera predição simulada baseada no módulo"""
        module = request.module_name
        data_type = request.data_type

        # Predições específicas por módulo
        if module == "financial":
            if "forecast" in data_type.lower():
                return {"predicted_revenue": 125000, "confidence_interval": [115000, 135000]}
            elif "cash_flow" in data_type.lower():
                return {"cash_position": "positive", "risk_level": "low"}
        elif module == "hr":
            if "turnover" in data_type.lower():
                return {"turnover_risk": 0.15, "at_risk_employees": 3}
            elif "performance" in data_type.lower():
                return {"team_performance": "above_average", "improvement_areas": ["communication"]}
        elif module == "crm":
            if "lead_scoring" in data_type.lower():
                return {"lead_score": 85, "conversion_probability": 0.73}
            elif "churn" in data_type.lower():
                return {"churn_risk": "low", "retention_actions": ["follow_up"]}

        # Predição genérica
        return {"status": "processed", "module": module, "data_type": data_type, "result": "analysis_complete"}

    async def _validate_request(self, request: PredictionRequest) -> bool:
        """Valida uma requisição de predição"""

        # Verificar campos obrigatórios
        if not request.id or not request.module_name or not request.tenant_id:
            return False

        # Verificar módulo válido
        if request.module_name not in self.known_modules:
            logger.warning(f"Módulo desconhecido: {request.module_name}")

        # Verificar deadline
        if request.deadline and request.deadline < datetime.now():
            logger.warning(f"Deadline já passou para predição {request.id}")
            return False

        return True

    async def _detect_conflicts(self, request: PredictionRequest) -> list[str]:
        """Detecta conflitos com outras predições"""
        conflicts = []

        # Verificar se há predições similares em andamento
        for active_id, active_request in self.active_predictions.items():
            if (
                active_request.module_name == request.module_name
                and active_request.data_type == request.data_type
                and active_request.tenant_id == request.tenant_id
            ):
                conflicts.append(active_id)

        return conflicts

    async def _resolve_conflicts(self, request: PredictionRequest, conflicts: list[str]) -> bool:
        """Resolve conflitos entre predições"""

        for conflict_id in conflicts:
            conflict_request = self.active_predictions[conflict_id]

            # Se nova predição tem prioridade maior, cancela a antiga
            if request.priority.value > conflict_request.priority.value:
                await self._cancel_prediction(conflict_id)
                logger.info(f"Predição {conflict_id} cancelada por prioridade")
            else:
                # Senão, rejeita a nova
                logger.info(f"Predição {request.id} rejeitada por conflito")
                return False

        return True

    async def _cancel_prediction(self, prediction_id: str):
        """Cancela uma predição"""
        if prediction_id in self.active_predictions:
            # Marcar como cancelada
            result = PredictionResult(
                request_id=prediction_id,
                status=PredictionStatus.CANCELLED,
                prediction=None,
                confidence=0.0,
                processing_time=0.0,
            )
            self.completed_predictions[prediction_id] = result
            del self.active_predictions[prediction_id]

    def _analyze_queue_priorities(self, queue_items: list[PredictionRequest]) -> dict[str, int]:
        """Analisa prioridades da queue"""
        priority_counts = defaultdict(int)

        for item in queue_items:
            priority_counts[item.priority.name] += 1

        return dict(priority_counts)

    async def cleanup_old_predictions(self, days_old: int = 7):
        """Remove predições antigas para economizar memória"""
        cutoff = datetime.now() - timedelta(days=days_old)

        old_predictions = [
            pred_id for pred_id, result in self.completed_predictions.items() if result.completed_at < cutoff
        ]

        for pred_id in old_predictions:
            del self.completed_predictions[pred_id]

        logger.info(f"Removidas {len(old_predictions)} predições antigas")

    async def health_check(self) -> dict[str, Any]:
        """Verifica saúde do orquestrador"""
        return {
            "status": "healthy" if self.running else "stopped",
            "workers_running": len([w for w in self.workers if not w.done()]),
            "queue_size": self.prediction_queue.qsize(),
            "active_predictions": len(self.active_predictions),
            "circuit_breaker_state": self.circuit_breaker.state,
            "metrics": self.metrics,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }
