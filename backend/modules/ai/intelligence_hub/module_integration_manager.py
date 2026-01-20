"""
Module Integration Manager - Gerenciador de Integrações de Módulos

Gerencia conexões e integrações da Central de IA com todos os módulos:
1. Auto-descoberta de módulos
2. Health monitoring dos módulos
3. Otimização de integrações
4. Circuit breakers para proteção
5. Load balancing e cache

Versão adaptada para Conecta PRO
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Status de um módulo"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class IntegrationType(Enum):
    """Tipos de integração"""
    API_REST = "api_rest"
    WEBHOOK = "webhook"
    MESSAGE_QUEUE = "message_queue"
    DIRECT_DB = "direct_db"
    EVENT_STREAM = "event_stream"


@dataclass
class ModuleInfo:
    """Informações de um módulo"""
    name: str
    status: ModuleStatus
    version: str
    endpoints: Dict[str, str]
    capabilities: List[str]
    health_endpoint: str
    last_check: datetime
    response_time: float
    error_count: int = 0
    integration_types: List[IntegrationType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationConfig:
    """Configuração de integração"""
    module_name: str
    integration_type: IntegrationType
    endpoint_url: str
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutos


class CircuitBreakerState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker para proteger integrações"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class ModuleIntegrationManager:
    """
    Gerenciador de Integrações de Módulos para a Central de IA do Conecta PRO
    
    Funcionalidades:
    - Auto-descoberta e monitoramento de módulos
    - Health checks automáticos
    - Circuit breakers e proteção
    - Cache e otimização
    - Load balancing
    """

    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0
        }
        
        # Tarefas de background
        self.monitoring_task: Optional[asyncio.Task] = None
        self.discovery_task: Optional[asyncio.Task] = None
        
        # Módulos disponíveis do Conecta PRO
        self.available_modules = [
            "ai", "analytics", "audit", "automation", "bidding", "clients",
            "config", "core", "crm", "diarists", "document_kits", "documents",
            "equipment_management", "facilities", "fase5", "field_service",
            "financial", "ged", "government_integrations", "health_occupational",
            "hr", "integrations", "marketplace", "mobile", "monitoring",
            "notifications", "occurrences", "operations", "recruitment",
            "reports", "scheduler", "security_lgpd", "services"
        ]

    async def start(self):
        """Inicia o gerenciador"""
        logger.info("Iniciando Module Integration Manager...")
        
        # Auto-descoberta inicial
        await self.auto_discover_modules()
        
        # Iniciar tarefas de background
        self.monitoring_task = asyncio.create_task(self._background_monitoring())
        self.discovery_task = asyncio.create_task(self._periodic_discovery())
        
        logger.info(f"Module Integration Manager iniciado com {len(self.modules)} módulos")

    async def stop(self):
        """Para o gerenciador"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.discovery_task:
            self.discovery_task.cancel()
        
        await asyncio.gather(
            self.monitoring_task, self.discovery_task, 
            return_exceptions=True
        )
        
        logger.info("Module Integration Manager parado")

    async def auto_discover_modules(self) -> Dict[str, Any]:
        """
        Auto-descobre módulos disponíveis no sistema
        """
        discovery_results = {
            "discovered": [],
            "failed": [],
            "updated": []
        }
        
        for module_name in self.available_modules:
            try:
                module_info = await self._discover_single_module(module_name)
                
                if module_info["discovered"]:
                    if module_name in self.modules:
                        discovery_results["updated"].append(module_name)
                    else:
                        discovery_results["discovered"].append(module_name)
                    
                    # Criar integração automática
                    integration = await self._create_auto_integration(module_name, module_info)
                    self.integrations[module_name] = integration
                    
                    # Criar circuit breaker
                    self.circuit_breakers[module_name] = CircuitBreaker()
                    
                    # Atualizar info do módulo
                    self.modules[module_name] = ModuleInfo(
                        name=module_name,
                        status=ModuleStatus.HEALTHY,
                        version=module_info.get("version", "unknown"),
                        endpoints=module_info.get("endpoints", {}),
                        capabilities=module_info.get("capabilities", []),
                        health_endpoint=module_info.get("health_endpoint", "/health"),
                        last_check=datetime.now(),
                        response_time=module_info.get("response_time", 0.0)
                    )
                    
                else:
                    discovery_results["failed"].append(module_name)
                    
            except Exception as e:
                logger.error(f"Erro na descoberta do módulo {module_name}: {e}")
                discovery_results["failed"].append(module_name)
        
        logger.info(f"Descoberta concluída: {len(discovery_results['discovered'])} novos, "
                   f"{len(discovery_results['updated'])} atualizados, "
                   f"{len(discovery_results['failed'])} falharam")
        
        return discovery_results

    async def call_module_api(self, module_name: str, endpoint: str, 
                             method: str = "GET", data: Optional[Dict] = None,
                             use_cache: bool = True) -> Any:
        """
        Faz chamada para API de um módulo
        """
        start_time = time.time()
        
        try:
            # Verificar se módulo existe
            if module_name not in self.modules:
                raise ValueError(f"Módulo {module_name} não encontrado")
            
            # Verificar circuit breaker
            circuit_breaker = self.circuit_breakers.get(module_name)
            if circuit_breaker and not circuit_breaker.can_execute():
                raise Exception(f"Circuit breaker ativo para módulo {module_name}")
            
            # Verificar cache
            cache_key = f"{module_name}_{endpoint}_{hash(str(data))}"
            if use_cache and cache_key in self.cache:
                if self._is_cache_valid(cache_key):
                    self.stats["cache_hits"] += 1
                    return self.cache[cache_key]
            
            # Fazer chamada
            response = await self._make_api_call(module_name, endpoint, method, data)
            
            # Cachear resposta se aplicável
            if use_cache and method == "GET":
                self._cache_response(cache_key, response)
            
            # Registrar sucesso
            if circuit_breaker:
                circuit_breaker.record_success()
            
            # Atualizar estatísticas
            response_time = time.time() - start_time
            self._update_stats(True, response_time)
            
            return response
            
        except Exception as e:
            # Registrar falha
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            self._update_stats(False, time.time() - start_time)
            
            logger.error(f"Erro na chamada para {module_name}/{endpoint}: {e}")
            raise

    async def get_module_health(self, module_name: str) -> Dict[str, Any]:
        """Obtém saúde de um módulo"""
        
        if module_name not in self.modules:
            return {"status": "unknown", "error": "Módulo não encontrado"}
        
        module_info = self.modules[module_name]
        
        try:
            # Fazer health check
            health_response = await self.call_module_api(
                module_name, 
                module_info.health_endpoint, 
                use_cache=False
            )
            
            # Atualizar status do módulo
            self.modules[module_name].status = ModuleStatus.HEALTHY
            self.modules[module_name].last_check = datetime.now()
            self.modules[module_name].error_count = 0
            
            return {
                "module": module_name,
                "status": "healthy",
                "last_check": module_info.last_check.isoformat(),
                "response_time": module_info.response_time,
                "details": health_response
            }
            
        except Exception as e:
            # Atualizar status de erro
            self.modules[module_name].error_count += 1
            
            if self.modules[module_name].error_count >= 3:
                self.modules[module_name].status = ModuleStatus.UNHEALTHY
            else:
                self.modules[module_name].status = ModuleStatus.DEGRADED
            
            return {
                "module": module_name,
                "status": self.modules[module_name].status.value,
                "error": str(e),
                "error_count": self.modules[module_name].error_count
            }

    async def get_all_modules_health(self) -> Dict[str, Any]:
        """Obtém saúde de todos os módulos"""
        health_summary = {
            "healthy": [],
            "degraded": [],
            "unhealthy": [],
            "offline": [],
            "total_modules": len(self.modules),
            "timestamp": datetime.now().isoformat()
        }
        
        for module_name in self.modules:
            health = await self.get_module_health(module_name)
            status = health["status"]
            
            if status == "healthy":
                health_summary["healthy"].append(module_name)
            elif status == "degraded":
                health_summary["degraded"].append(module_name)
            elif status == "unhealthy":
                health_summary["unhealthy"].append(module_name)
            else:
                health_summary["offline"].append(module_name)
        
        # Calcular percentual de saúde
        total = len(self.modules)
        if total > 0:
            health_summary["health_percentage"] = (len(health_summary["healthy"]) / total) * 100
        else:
            health_summary["health_percentage"] = 0
        
        return health_summary

    async def register_module_webhook(self, module_name: str, webhook_url: str, 
                                     events: List[str]) -> bool:
        """Registra webhook de um módulo"""
        try:
            # Validar URL
            if not webhook_url.startswith(('http://', 'https://')):
                raise ValueError("URL de webhook inválida")
            
            # Adicionar configuração de webhook
            if module_name not in self.integrations:
                self.integrations[module_name] = IntegrationConfig(
                    module_name=module_name,
                    integration_type=IntegrationType.WEBHOOK,
                    endpoint_url=webhook_url
                )
            
            # Registrar eventos
            if module_name not in self.modules:
                self.modules[module_name] = ModuleInfo(
                    name=module_name,
                    status=ModuleStatus.UNKNOWN,
                    version="unknown",
                    endpoints={"webhook": webhook_url},
                    capabilities=["webhook"],
                    health_endpoint="/health",
                    last_check=datetime.now(),
                    response_time=0.0
                )
            
            self.modules[module_name].metadata["webhook_events"] = events
            
            logger.info(f"Webhook registrado para módulo {module_name}: {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar webhook para {module_name}: {e}")
            return False

    async def send_webhook_notification(self, module_name: str, event_type: str, 
                                       data: Dict[str, Any]) -> bool:
        """Envia notificação via webhook"""
        try:
            if module_name not in self.integrations:
                return False
            
            integration = self.integrations[module_name]
            if integration.integration_type != IntegrationType.WEBHOOK:
                return False
            
            # Preparar payload
            payload = {
                "event_type": event_type,
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # Enviar webhook (simulado)
            logger.info(f"Enviando webhook para {module_name}: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar webhook para {module_name}: {e}")
            return False

    async def _discover_single_module(self, module_name: str) -> Dict[str, Any]:
        """Descobre um módulo específico"""
        
        # Simular descoberta (em produção, faria introspection real)
        discovered = module_name in self.available_modules
        
        if discovered:
            return {
                "discovered": True,
                "version": "1.0.0",
                "endpoints": {
                    "health": f"/api/v1/{module_name}/health",
                    "info": f"/api/v1/{module_name}/info"
                },
                "capabilities": ["health_check", "api_rest"],
                "health_endpoint": "/health",
                "response_time": 0.1
            }
        else:
            return {"discovered": False}

    async def _create_auto_integration(self, module_name: str, module_info: Dict[str, Any]) -> IntegrationConfig:
        """Cria integração automática para um módulo"""
        
        return IntegrationConfig(
            module_name=module_name,
            integration_type=IntegrationType.API_REST,
            endpoint_url=f"/api/v1/{module_name}",
            timeout=30,
            retry_count=3,
            circuit_breaker_enabled=True,
            cache_enabled=True,
            cache_ttl=300
        )

    async def _make_api_call(self, module_name: str, endpoint: str, 
                            method: str, data: Optional[Dict]) -> Any:
        """Faz chamada real para API do módulo"""
        
        # Em produção, faria chamada HTTP real
        # Por enquanto, simular resposta baseada no módulo
        await asyncio.sleep(0.05)  # Simular latência
        
        return {
            "status": "success",
            "module": module_name,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.now().isoformat(),
            "data": f"Response from {module_name}"
        }

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se entrada do cache é válida"""
        if cache_key not in self.cache_timestamps:
            return False
        
        timestamp = self.cache_timestamps[cache_key]
        ttl = timedelta(seconds=300)  # 5 minutos
        
        return datetime.now() - timestamp < ttl

    def _cache_response(self, cache_key: str, response: Any):
        """Armazena resposta no cache"""
        self.cache[cache_key] = response
        self.cache_timestamps[cache_key] = datetime.now()

    def _update_stats(self, success: bool, response_time: float):
        """Atualiza estatísticas"""
        self.stats["total_requests"] += 1
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        # Atualizar tempo médio de resposta
        total = self.stats["total_requests"]
        current_avg = self.stats["avg_response_time"]
        self.stats["avg_response_time"] = ((current_avg * (total - 1)) + response_time) / total

    async def _background_monitoring(self):
        """Monitoramento contínuo em background"""
        while True:
            try:
                # Health check de todos os módulos a cada 5 minutos
                await asyncio.sleep(300)
                
                for module_name in list(self.modules.keys()):
                    await self.get_module_health(module_name)
                
                # Limpar cache expirado
                await self._cleanup_expired_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")

    async def _periodic_discovery(self):
        """Descoberta periódica de novos módulos"""
        while True:
            try:
                # Re-descobrir módulos a cada 30 minutos
                await asyncio.sleep(1800)
                await self.auto_discover_modules()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro na descoberta periódica: {e}")

    async def _cleanup_expired_cache(self):
        """Remove entradas expiradas do cache"""
        expired_keys = []
        
        for cache_key in self.cache_timestamps:
            if not self._is_cache_valid(cache_key):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
        
        if expired_keys:
            logger.info(f"Removidas {len(expired_keys)} entradas expiradas do cache")

    async def get_integration_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de integração"""
        circuit_breaker_stats = {}
        
        for module_name, cb in self.circuit_breakers.items():
            circuit_breaker_stats[module_name] = {
                "state": cb.state.value,
                "failure_count": cb.failure_count,
                "last_failure": cb.last_failure_time
            }
        
        return {
            "modules_discovered": len(self.modules),
            "integrations_active": len(self.integrations),
            "cache_entries": len(self.cache),
            "circuit_breakers": circuit_breaker_stats,
            "performance_stats": self.stats,
            "module_statuses": {
                name: info.status.value for name, info in self.modules.items()
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do gerenciador"""
        return {
            "status": "healthy",
            "modules_managed": len(self.modules),
            "integrations_active": len(self.integrations),
            "cache_size": len(self.cache),
            "monitoring_active": self.monitoring_task is not None and not self.monitoring_task.done(),
            "discovery_active": self.discovery_task is not None and not self.discovery_task.done(),
            "stats": self.stats,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
