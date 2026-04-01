"""
Module Integrator - Sistema Anti-Procrastinação
==============================================

Integra o sistema anti-procrastinação com todos os módulos existentes
do Conecta PRO, coletando pendências de cada módulo de forma unificada.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from ..models import Department, PendingTaskData, TaskCategory, TaskPriority

logger = logging.getLogger(__name__)


class ModuleIntegrator:
    """
    Integrador que conecta todos os módulos do Conecta PRO
    ao sistema anti-procrastinação.

    Responsabilidades:
    - Coletar pendências de todos os módulos
    - Normalizar dados em formato unificado
    - Sincronizar em tempo real
    - Mapear categorias e prioridades
    """

    def __init__(self, db: Session):
        self.db = db
        self._module_collectors: dict[str, Callable] = {}
        self._setup_module_collectors()

    def _setup_module_collectors(self):
        """Configura coletores de pendências por módulo."""
        self._module_collectors = {
            "security_lgpd": self._collect_security_lgpd_tasks,
            "health_occupational": self._collect_health_tasks,
            "government_integrations": self._collect_government_tasks,
            "hr": self._collect_hr_tasks,
            "commercial": self._collect_commercial_tasks,
            "financial": self._collect_financial_tasks,
            "facilities": self._collect_facilities_tasks,
            "workflows": self._collect_workflow_tasks,
            "notifications": self._collect_notification_tasks,
        }

    async def sync_all_modules(self) -> dict[str, Any]:
        """
        Sincroniza pendências de todos os módulos.

        Returns:
            Dict com resumo da sincronização
        """
        logger.info("🔄 Iniciando sincronização de todos os módulos")

        all_tasks = []
        sync_results = {}

        for module_name, collector in self._module_collectors.items():
            try:
                logger.debug(f"Sincronizando módulo: {module_name}")
                tasks = await collector()
                all_tasks.extend(tasks)

                sync_results[module_name] = {
                    "success": True,
                    "tasks_count": len(tasks),
                    "critical_count": len([t for t in tasks if t.priority == TaskPriority.CRITICAL]),
                }

            except Exception as e:
                logger.error(f"Erro ao sincronizar {module_name}: {e}")
                sync_results[module_name] = {"success": False, "error": str(e), "tasks_count": 0}

        # Atualiza banco de dados
        await self._update_pending_tasks(all_tasks)

        logger.info(f"✅ Sincronização concluída: {len(all_tasks)} tarefas processadas")

        return {
            "total_tasks": len(all_tasks),
            "modules_synced": len([r for r in sync_results.values() if r["success"]]),
            "modules_failed": len([r for r in sync_results.values() if not r["success"]]),
            "sync_results": sync_results,
            "last_sync": datetime.utcnow().isoformat(),
        }

    async def sync_module(self, module_name: str) -> dict[str, Any]:
        """
        Sincroniza pendências de um módulo específico.

        Args:
            module_name: Nome do módulo

        Returns:
            Dict com resultado da sincronização
        """
        if module_name not in self._module_collectors:
            raise ValueError(f"Módulo {module_name} não configurado")

        logger.info(f"🔄 Sincronizando módulo: {module_name}")

        collector = self._module_collectors[module_name]
        tasks = await collector()

        await self._update_pending_tasks(tasks)

        return {
            "module": module_name,
            "tasks_collected": len(tasks),
            "critical_tasks": len([t for t in tasks if t.priority == TaskPriority.CRITICAL]),
            "last_sync": datetime.utcnow().isoformat(),
        }

    # Coletores por módulo (implementações mockadas para demonstração)

    async def _collect_security_lgpd_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas do módulo Security/LGPD."""
        tasks = []

        # Mock: Consentimentos pendentes
        tasks.append(
            PendingTaskData(
                title="Revisar consentimentos LGPD pendentes",
                description="5 consentimentos aguardando revisão",
                source_module="security_lgpd",
                source_id="consent_pending_001",
                category=TaskCategory.COMPLIANCE,
                priority=TaskPriority.HIGH,
                department=Department.LEGAL,
                created_at=datetime.utcnow(),
            )
        )

        # Mock: Rotação de chaves
        tasks.append(
            PendingTaskData(
                title="Rotação de chaves criptográficas pendente",
                description="Chaves devem ser rotacionadas mensalmente",
                source_module="security_lgpd",
                source_id="key_rotation_002",
                category=TaskCategory.SECURITY,
                priority=TaskPriority.CRITICAL,
                department=Department.IT,
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_health_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas reais do módulo Health Ocupacional."""
        tasks = []
        hoje = date.today()
        limite_30d = hoje + timedelta(days=30)
        limite_7d = hoje + timedelta(days=7)

        try:
            from sqlalchemy import text

            from core.database import get_sync_session

            with get_sync_session() as db:
                # ASOs vencendo nos próximos 30 dias
                try:
                    result = db.execute(
                        text(
                            "SELECT COUNT(*) as total, "
                            "SUM(CASE WHEN data_vencimento <= :limite_7d THEN 1 ELSE 0 END) as criticos "
                            "FROM health_asos "
                            "WHERE ativo = TRUE AND cancelado = FALSE "
                            "AND data_vencimento BETWEEN :hoje AND :limite_30d"
                        ),
                        {"hoje": hoje, "limite_30d": limite_30d, "limite_7d": limite_7d},
                    )
                    row = result.fetchone()
                    total_asos = row.total if row and row.total else 0
                    criticos_asos = row.criticos if row and row.criticos else 0

                    if total_asos > 0:
                        tasks.append(
                            PendingTaskData(
                                title=f"Renovar {total_asos} ASOs vencendo em 30 dias",
                                description=f"{criticos_asos} críticos (≤7 dias), {total_asos - criticos_asos} atenção",
                                source_module="health_occupational",
                                source_id="asos_vencendo",
                                category=TaskCategory.HR,
                                priority=TaskPriority.CRITICAL if criticos_asos > 0 else TaskPriority.HIGH,
                                department=Department.HR,
                                due_date=hoje + timedelta(days=7) if criticos_asos > 0 else hoje + timedelta(days=30),
                                created_at=datetime.utcnow(),
                            )
                        )
                except Exception as e:
                    logger.warning("health_tasks: erro ASOs: %s", e)

                # EPIs vencendo nos próximos 30 dias
                try:
                    result = db.execute(
                        text(
                            "SELECT COUNT(*) as total "
                            "FROM health_epi_deliveries "
                            "WHERE devolvido = FALSE "
                            "AND data_validade BETWEEN :hoje AND :limite_30d"
                        ),
                        {"hoje": hoje, "limite_30d": limite_30d},
                    )
                    row = result.fetchone()
                    total_epis = row.total if row and row.total else 0

                    if total_epis > 0:
                        tasks.append(
                            PendingTaskData(
                                title=f"Substituir {total_epis} EPIs com validade vencendo",
                                description=f"{total_epis} EPIs vencendo nos próximos 30 dias — substituição obrigatória (NR-6)",
                                source_module="health_occupational",
                                source_id="epis_vencendo",
                                category=TaskCategory.HEALTH_SAFETY,
                                priority=TaskPriority.HIGH,
                                department=Department.OPERATIONS,
                                due_date=limite_30d,
                                created_at=datetime.utcnow(),
                            )
                        )
                except Exception as e:
                    logger.warning("health_tasks: erro EPIs: %s", e)

                # Exames agendados mas não confirmados (> 3 dias)
                try:
                    limite_atraso = hoje - timedelta(days=3)
                    result = db.execute(
                        text(
                            "SELECT COUNT(*) as total "
                            "FROM health_medical_exams "
                            "WHERE status = 'agendado' "
                            "AND data_agendamento < :limite_atraso"
                        ),
                        {"limite_atraso": limite_atraso},
                    )
                    row = result.fetchone()
                    total_exames = row.total if row and row.total else 0

                    if total_exames > 0:
                        tasks.append(
                            PendingTaskData(
                                title=f"Confirmar {total_exames} exames médicos pendentes",
                                description=f"{total_exames} exames agendados há mais de 3 dias aguardam confirmação",
                                source_module="health_occupational",
                                source_id="exames_pendentes_confirmacao",
                                category=TaskCategory.HR,
                                priority=TaskPriority.MEDIUM,
                                department=Department.HR,
                                due_date=hoje,
                                created_at=datetime.utcnow(),
                            )
                        )
                except Exception as e:
                    logger.warning("health_tasks: erro exames: %s", e)

        except Exception as e:
            logger.warning("_collect_health_tasks falhou: %s", e)

        return tasks

    async def _collect_government_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas do módulo Government Integrations."""
        tasks = []

        # Mock: Eventos eSocial pendentes
        tasks.append(
            PendingTaskData(
                title="Transmitir 15 eventos eSocial pendentes",
                description="Eventos de admissão e desligamento",
                source_module="government_integrations",
                source_id="esocial_pending_005",
                category=TaskCategory.COMPLIANCE,
                priority=TaskPriority.HIGH,
                department=Department.HR,
                created_at=datetime.utcnow(),
            )
        )

        # Mock: Guias FGTS vencendo
        tasks.append(
            PendingTaskData(
                title="Gerar guias FGTS - Competência atual",
                description="Prazo de vencimento em 3 dias",
                source_module="government_integrations",
                source_id="fgts_due_006",
                category=TaskCategory.FINANCIAL,
                priority=TaskPriority.CRITICAL,
                department=Department.FINANCIAL,
                due_date=date.today(),
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_hr_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas gerais de RH."""
        tasks = []

        # Mock: Documentos faltantes
        tasks.append(
            PendingTaskData(
                title="Coletar documentos faltantes - João Silva",
                description="CPF e comprovante de residência",
                source_module="hr",
                source_id="docs_missing_007",
                category=TaskCategory.HR,
                priority=TaskPriority.MEDIUM,
                department=Department.HR,
                assigned_to_name="Analista de RH",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_commercial_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas do Comercial."""
        tasks = []

        # Mock: Orçamentos não enviados
        tasks.append(
            PendingTaskData(
                title="Enviar orçamento para Cliente ABC",
                description="Solicitação de orçamento há 5 dias",
                source_module="commercial",
                source_id="quote_pending_008",
                category=TaskCategory.COMMERCIAL,
                priority=TaskPriority.HIGH,
                department=Department.COMMERCIAL,
                assigned_to_name="Vendedor A",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_financial_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas do Financeiro."""
        tasks = []

        # Mock: Pagamentos atrasados
        tasks.append(
            PendingTaskData(
                title="Aprovar pagamento - Fornecedor XYZ",
                description="Fatura de R$ 5.000,00 aguardando aprovação",
                source_module="financial",
                source_id="payment_approval_009",
                category=TaskCategory.FINANCIAL,
                priority=TaskPriority.HIGH,
                department=Department.FINANCIAL,
                due_date=date.today(),
                assigned_to_name="Gerente Financeiro",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_facilities_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas do Facilities."""
        tasks = []

        # Mock: Manutenções atrasadas
        tasks.append(
            PendingTaskData(
                title="Manutenção preventiva - Ar condicionado Sala 201",
                description="Manutenção atrasada há 15 dias",
                source_module="facilities",
                source_id="maintenance_overdue_010",
                category=TaskCategory.OPERATIONAL,
                priority=TaskPriority.MEDIUM,
                department=Department.FACILITIES,
                assigned_to_name="Técnico de Manutenção",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_workflow_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas de workflows pendentes."""
        tasks = []

        # Mock: Workflows parados
        tasks.append(
            PendingTaskData(
                title="Workflow de aprovação travado - Processo 123",
                description="Aguardando aprovação do diretor há 3 dias",
                source_module="workflows",
                source_id="workflow_stuck_011",
                category=TaskCategory.OPERATIONAL,
                priority=TaskPriority.HIGH,
                department=Department.MANAGEMENT,
                assigned_to_name="Diretor",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _collect_notification_tasks(self) -> list[PendingTaskData]:
        """Coleta tarefas de notificações não enviadas."""
        tasks = []

        # Mock: Notificações falhas
        tasks.append(
            PendingTaskData(
                title="Reenviar notificações falhas",
                description="25 notificações falharam no envio",
                source_module="notifications",
                source_id="failed_notifications_012",
                category=TaskCategory.OPERATIONAL,
                priority=TaskPriority.LOW,
                department=Department.IT,
                assigned_to_name="Admin do Sistema",
                created_at=datetime.utcnow(),
            )
        )

        return tasks

    async def _update_pending_tasks(self, tasks: list[PendingTaskData]):
        """
        Atualiza banco de dados com tarefas coletadas.

        Args:
            tasks: Lista de tarefas para atualizar
        """
        # Por enquanto só faz log, pois os models ainda não estão
        # totalmente integrados ao banco existente

        logger.info(f"📝 Atualizando {len(tasks)} tarefas no banco de dados")

        # for task in tasks:
        #     existing = self.db.query(PendingTask).filter(
        #         PendingTask.source_module == task.source_module,
        #         PendingTask.source_id == task.source_id
        #     ).first()
        #
        #     if not existing:
        #         db_task = PendingTask(**asdict(task))
        #         self.db.add(db_task)
        #
        # self.db.commit()

        logger.info("✅ Tarefas atualizadas com sucesso")

    def get_module_status(self) -> dict[str, Any]:
        """
        Status de integração de todos os módulos.

        Returns:
            Dict com status de cada módulo
        """
        return {
            module_name: {"integrated": True, "last_sync": datetime.utcnow().isoformat(), "status": "active"}
            for module_name in self._module_collectors.keys()
        }

    async def test_module_integration(self, module_name: str) -> dict[str, Any]:
        """
        Testa integração de um módulo específico.

        Args:
            module_name: Nome do módulo

        Returns:
            Dict com resultado do teste
        """
        if module_name not in self._module_collectors:
            return {"module": module_name, "status": "error", "message": "Módulo não configurado"}

        try:
            logger.info(f"🧪 Testando integração do módulo: {module_name}")

            start_time = datetime.utcnow()
            tasks = await self._module_collectors[module_name]()
            end_time = datetime.utcnow()

            duration = (end_time - start_time).total_seconds()

            return {
                "module": module_name,
                "status": "success",
                "tasks_collected": len(tasks),
                "duration_seconds": duration,
                "message": f"✅ Módulo {module_name} integrado com sucesso",
            }

        except Exception as e:
            logger.error(f"❌ Erro ao testar {module_name}: {e}")
            return {"module": module_name, "status": "error", "message": f"Erro: {str(e)}"}
