"""Allocation Service - Serviço de Alocação e Rateio de Custos."""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from uuid import UUID
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.costing.models import (
    CostDriver,
    CostActivity,
    CostPool,
    CostObject,
    CostAllocation,
)
from modules.financial.costing.models.cost_pool import AllocationBasis
from modules.financial.costing.models.cost_allocation import (
    AllocationStatus,
    AllocationType,
    AllocationMethod,
)

logger = logging.getLogger(__name__)


class AllocationService:
    """Serviço de Alocação e Rateio de Custos.

    Implementa diferentes métodos de alocação:
    - Driver-based: baseado em cost drivers
    - Percentage: percentual fixo
    - Proportional: proporcional a uma base
    - Equal: divisão igual
    - Step-down: alocação escalonada
    """

    def __init__(self, session: AsyncSession):
        """Inicializa o serviço de alocação."""
        self.session = session

    async def allocate_pool_to_activities(
        self,
        pool_id: UUID,
        activity_allocations: list[dict[str, Any]],
        data_alocacao: date,
        user_id: Optional[UUID] = None,
        descricao: Optional[str] = None,
        auto_execute: bool = False,
    ) -> list[CostAllocation]:
        """Aloca custos de um pool para múltiplas atividades.

        Args:
            pool_id: ID do pool origem
            activity_allocations: Lista com {activity_id, percentual ou valor, driver_quantidade}
            data_alocacao: Data da alocação
            user_id: ID do usuário
            descricao: Descrição da alocação
            auto_execute: Se True, executa automaticamente

        Returns:
            Lista de alocações criadas
        """
        pool = await self.session.get(CostPool, pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} não encontrado")

        if not pool.valor_total or pool.valor_total <= 0:
            raise ValueError(f"Pool {pool_id} sem valor para alocar")

        allocations = []
        total_allocated = Decimal("0")

        for alloc_data in activity_allocations:
            activity_id = UUID(alloc_data["activity_id"])
            activity = await self.session.get(CostActivity, activity_id)
            if not activity:
                logger.warning(f"Atividade {activity_id} não encontrada, pulando")
                continue

            # Determina valor a alocar
            if "valor" in alloc_data:
                valor = Decimal(str(alloc_data["valor"]))
                percentual = (valor / pool.valor_total * 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            elif "percentual" in alloc_data:
                percentual = Decimal(str(alloc_data["percentual"]))
                valor = (pool.valor_total * percentual / 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            else:
                raise ValueError("Necessário informar 'valor' ou 'percentual'")

            allocation = CostAllocation(
                condominio_id=pool.condominio_id,
                codigo=f"ALLOC-{pool.codigo}-{activity.codigo}-{data_alocacao.strftime('%Y%m%d')}",
                tipo=AllocationType.POOL_TO_ACTIVITY,
                metodo=AllocationMethod(alloc_data.get("metodo", "PERCENTAGE")),
                origem_tipo="pool",
                origem_id=pool_id,
                destino_tipo="activity",
                destino_id=activity_id,
                valor_alocado=valor,
                percentual_alocado=percentual,
                driver_id=UUID(alloc_data["driver_id"]) if alloc_data.get("driver_id") else pool.driver_id,
                driver_quantidade=Decimal(str(alloc_data.get("driver_quantidade", 0))),
                data_alocacao=data_alocacao,
                periodo_inicio=data_alocacao.replace(day=1),
                periodo_fim=data_alocacao,
                descricao=descricao or f"Alocação de {pool.nome} para {activity.nome}",
                status=AllocationStatus.PENDING,
                criado_por=user_id,
                ativo=True,
            )

            if auto_execute:
                allocation.status = AllocationStatus.EXECUTED
                allocation.executado_por = user_id
                allocation.executado_em = datetime.utcnow()

            self.session.add(allocation)
            allocations.append(allocation)
            total_allocated += valor

        await self.session.flush()

        logger.info(
            f"Criadas {len(allocations)} alocações do pool {pool.codigo}. "
            f"Total: R$ {total_allocated:,.2f}"
        )
        return allocations

    async def allocate_activity_to_objects(
        self,
        activity_id: UUID,
        object_allocations: list[dict[str, Any]],
        data_alocacao: date,
        user_id: Optional[UUID] = None,
        descricao: Optional[str] = None,
        auto_execute: bool = False,
    ) -> list[CostAllocation]:
        """Aloca custos de uma atividade para múltiplos objetos de custo.

        Args:
            activity_id: ID da atividade origem
            object_allocations: Lista com {object_id, percentual ou valor, driver_quantidade}
            data_alocacao: Data da alocação
            user_id: ID do usuário
            descricao: Descrição da alocação
            auto_execute: Se True, executa automaticamente

        Returns:
            Lista de alocações criadas
        """
        activity = await self.session.get(CostActivity, activity_id)
        if not activity:
            raise ValueError(f"Atividade {activity_id} não encontrada")

        # Calcula custo total da atividade (direto + alocado)
        activity_total = activity.custo_direto or Decimal("0")

        alloc_query = select(
            func.sum(CostAllocation.valor_alocado)
        ).where(
            CostAllocation.destino_id == activity_id,
            CostAllocation.tipo == AllocationType.POOL_TO_ACTIVITY,
            CostAllocation.status == AllocationStatus.EXECUTED,
        )
        result = await self.session.execute(alloc_query)
        allocated_to_activity = result.scalar() or Decimal("0")
        activity_total += allocated_to_activity

        if activity_total <= 0:
            raise ValueError(f"Atividade {activity_id} sem custo para alocar")

        allocations = []
        total_allocated = Decimal("0")

        for alloc_data in object_allocations:
            object_id = UUID(alloc_data["object_id"])
            obj = await self.session.get(CostObject, object_id)
            if not obj:
                logger.warning(f"Objeto {object_id} não encontrado, pulando")
                continue

            # Determina valor a alocar
            if "valor" in alloc_data:
                valor = Decimal(str(alloc_data["valor"]))
                percentual = (valor / activity_total * 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            elif "percentual" in alloc_data:
                percentual = Decimal(str(alloc_data["percentual"]))
                valor = (activity_total * percentual / 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            else:
                raise ValueError("Necessário informar 'valor' ou 'percentual'")

            allocation = CostAllocation(
                condominio_id=activity.condominio_id,
                codigo=f"ALLOC-{activity.codigo}-{obj.codigo}-{data_alocacao.strftime('%Y%m%d')}",
                tipo=AllocationType.ACTIVITY_TO_OBJECT,
                metodo=AllocationMethod(alloc_data.get("metodo", "PERCENTAGE")),
                origem_tipo="activity",
                origem_id=activity_id,
                destino_tipo="object",
                destino_id=object_id,
                valor_alocado=valor,
                percentual_alocado=percentual,
                driver_id=UUID(alloc_data["driver_id"]) if alloc_data.get("driver_id") else activity.driver_id,
                driver_quantidade=Decimal(str(alloc_data.get("driver_quantidade", 0))),
                data_alocacao=data_alocacao,
                periodo_inicio=data_alocacao.replace(day=1),
                periodo_fim=data_alocacao,
                descricao=descricao or f"Alocação de {activity.nome} para {obj.nome}",
                status=AllocationStatus.PENDING,
                criado_por=user_id,
                ativo=True,
            )

            if auto_execute:
                allocation.status = AllocationStatus.EXECUTED
                allocation.executado_por = user_id
                allocation.executado_em = datetime.utcnow()

            self.session.add(allocation)
            allocations.append(allocation)
            total_allocated += valor

        await self.session.flush()

        logger.info(
            f"Criadas {len(allocations)} alocações da atividade {activity.codigo}. "
            f"Total: R$ {total_allocated:,.2f}"
        )
        return allocations

    async def allocate_by_driver(
        self,
        origem_tipo: str,
        origem_id: UUID,
        driver_id: UUID,
        destinos: list[dict[str, Any]],
        data_alocacao: date,
        user_id: Optional[UUID] = None,
        auto_execute: bool = False,
    ) -> list[CostAllocation]:
        """Aloca custos proporcionalmente ao consumo de um driver.

        Args:
            origem_tipo: Tipo da origem (pool, activity)
            origem_id: ID da origem
            driver_id: ID do driver base
            destinos: Lista com {destino_id, driver_quantidade}
            data_alocacao: Data da alocação
            user_id: ID do usuário
            auto_execute: Se True, executa automaticamente

        Returns:
            Lista de alocações criadas
        """
        driver = await self.session.get(CostDriver, driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} não encontrado")

        # Obtém valor total a alocar
        if origem_tipo == "pool":
            origem = await self.session.get(CostPool, origem_id)
            if not origem:
                raise ValueError(f"Pool {origem_id} não encontrado")
            valor_total = origem.valor_total or Decimal("0")
            alloc_type = AllocationType.POOL_TO_ACTIVITY
        elif origem_tipo == "activity":
            origem = await self.session.get(CostActivity, origem_id)
            if not origem:
                raise ValueError(f"Atividade {origem_id} não encontrada")
            valor_total = origem.custo_direto or Decimal("0")
            alloc_type = AllocationType.ACTIVITY_TO_OBJECT
        else:
            raise ValueError(f"Tipo de origem inválido: {origem_tipo}")

        if valor_total <= 0:
            raise ValueError(f"Origem {origem_id} sem valor para alocar")

        # Calcula total de driver consumido
        total_driver = sum(Decimal(str(d["driver_quantidade"])) for d in destinos)
        if total_driver <= 0:
            raise ValueError("Total de driver consumido deve ser maior que zero")

        # Taxa por unidade de driver
        taxa_driver = valor_total / total_driver

        allocations = []
        for dest in destinos:
            destino_id = UUID(dest["destino_id"])
            driver_qty = Decimal(str(dest["driver_quantidade"]))
            valor = (taxa_driver * driver_qty).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            percentual = (driver_qty / total_driver * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            # Determina tipo de destino
            if alloc_type == AllocationType.POOL_TO_ACTIVITY:
                destino_tipo = "activity"
            else:
                destino_tipo = "object"

            allocation = CostAllocation(
                condominio_id=origem.condominio_id,
                codigo=f"ALLOC-DRV-{driver.codigo}-{data_alocacao.strftime('%Y%m%d')}-{destino_id.hex[:8]}",
                tipo=alloc_type,
                metodo=AllocationMethod.DRIVER_BASED,
                origem_tipo=origem_tipo,
                origem_id=origem_id,
                destino_tipo=destino_tipo,
                destino_id=destino_id,
                valor_alocado=valor,
                percentual_alocado=percentual,
                driver_id=driver_id,
                driver_quantidade=driver_qty,
                taxa_driver=taxa_driver,
                data_alocacao=data_alocacao,
                periodo_inicio=data_alocacao.replace(day=1),
                periodo_fim=data_alocacao,
                descricao=f"Alocação por driver {driver.nome}",
                status=AllocationStatus.PENDING,
                criado_por=user_id,
                ativo=True,
            )

            if auto_execute:
                allocation.status = AllocationStatus.EXECUTED
                allocation.executado_por = user_id
                allocation.executado_em = datetime.utcnow()

            self.session.add(allocation)
            allocations.append(allocation)

        await self.session.flush()

        logger.info(
            f"Criadas {len(allocations)} alocações por driver {driver.codigo}. "
            f"Taxa: R$ {taxa_driver:,.4f}/unidade"
        )
        return allocations

    async def allocate_equal(
        self,
        origem_tipo: str,
        origem_id: UUID,
        destino_ids: list[UUID],
        data_alocacao: date,
        user_id: Optional[UUID] = None,
        auto_execute: bool = False,
    ) -> list[CostAllocation]:
        """Aloca custos igualmente entre destinos.

        Args:
            origem_tipo: Tipo da origem (pool, activity)
            origem_id: ID da origem
            destino_ids: Lista de IDs dos destinos
            data_alocacao: Data da alocação
            user_id: ID do usuário
            auto_execute: Se True, executa automaticamente

        Returns:
            Lista de alocações criadas
        """
        if not destino_ids:
            raise ValueError("Necessário pelo menos um destino")

        # Obtém valor total
        if origem_tipo == "pool":
            origem = await self.session.get(CostPool, origem_id)
            if not origem:
                raise ValueError(f"Pool {origem_id} não encontrado")
            valor_total = origem.valor_total or Decimal("0")
            alloc_type = AllocationType.POOL_TO_ACTIVITY
            destino_tipo = "activity"
        elif origem_tipo == "activity":
            origem = await self.session.get(CostActivity, origem_id)
            if not origem:
                raise ValueError(f"Atividade {origem_id} não encontrada")
            valor_total = origem.custo_direto or Decimal("0")
            alloc_type = AllocationType.ACTIVITY_TO_OBJECT
            destino_tipo = "object"
        else:
            raise ValueError(f"Tipo de origem inválido: {origem_tipo}")

        if valor_total <= 0:
            raise ValueError(f"Origem {origem_id} sem valor para alocar")

        # Calcula valor por destino
        n_destinos = len(destino_ids)
        valor_por_destino = (valor_total / n_destinos).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        percentual = Decimal("100") / n_destinos

        allocations = []
        for destino_id in destino_ids:
            allocation = CostAllocation(
                condominio_id=origem.condominio_id,
                codigo=f"ALLOC-EQ-{origem.codigo}-{data_alocacao.strftime('%Y%m%d')}-{destino_id.hex[:8]}",
                tipo=alloc_type,
                metodo=AllocationMethod.EQUAL,
                origem_tipo=origem_tipo,
                origem_id=origem_id,
                destino_tipo=destino_tipo,
                destino_id=destino_id,
                valor_alocado=valor_por_destino,
                percentual_alocado=percentual,
                data_alocacao=data_alocacao,
                periodo_inicio=data_alocacao.replace(day=1),
                periodo_fim=data_alocacao,
                descricao=f"Alocação igual de {origem.nome}",
                status=AllocationStatus.PENDING,
                criado_por=user_id,
                ativo=True,
            )

            if auto_execute:
                allocation.status = AllocationStatus.EXECUTED
                allocation.executado_por = user_id
                allocation.executado_em = datetime.utcnow()

            self.session.add(allocation)
            allocations.append(allocation)

        await self.session.flush()

        logger.info(
            f"Criadas {len(allocations)} alocações iguais. "
            f"Valor por destino: R$ {valor_por_destino:,.2f}"
        )
        return allocations

    async def approve_allocation(
        self,
        allocation_id: UUID,
        user_id: UUID,
        observacao: Optional[str] = None,
    ) -> CostAllocation:
        """Aprova uma alocação pendente.

        Args:
            allocation_id: ID da alocação
            user_id: ID do usuário aprovador
            observacao: Observação opcional

        Returns:
            Alocação aprovada
        """
        allocation = await self.session.get(CostAllocation, allocation_id)
        if not allocation:
            raise ValueError(f"Alocação {allocation_id} não encontrada")

        if allocation.status != AllocationStatus.PENDING:
            raise ValueError(
                f"Alocação {allocation_id} não está pendente. "
                f"Status atual: {allocation.status.value}"
            )

        allocation.status = AllocationStatus.APPROVED
        allocation.aprovado_por = user_id
        allocation.aprovado_em = datetime.utcnow()
        if observacao:
            allocation.observacoes = observacao

        await self.session.flush()

        logger.info(f"Alocação {allocation_id} aprovada por {user_id}")
        return allocation

    async def execute_allocation(
        self,
        allocation_id: UUID,
        user_id: UUID,
    ) -> CostAllocation:
        """Executa uma alocação aprovada.

        Args:
            allocation_id: ID da alocação
            user_id: ID do usuário executor

        Returns:
            Alocação executada
        """
        allocation = await self.session.get(CostAllocation, allocation_id)
        if not allocation:
            raise ValueError(f"Alocação {allocation_id} não encontrada")

        if allocation.status not in [AllocationStatus.PENDING, AllocationStatus.APPROVED]:
            raise ValueError(
                f"Alocação {allocation_id} não pode ser executada. "
                f"Status atual: {allocation.status.value}"
            )

        allocation.status = AllocationStatus.EXECUTED
        allocation.executado_por = user_id
        allocation.executado_em = datetime.utcnow()

        # Atualiza custo indireto do destino
        if allocation.destino_tipo == "object":
            obj = await self.session.get(CostObject, allocation.destino_id)
            if obj:
                obj.custo_indireto = (obj.custo_indireto or Decimal("0")) + allocation.valor_alocado

        await self.session.flush()

        logger.info(
            f"Alocação {allocation_id} executada. "
            f"Valor: R$ {allocation.valor_alocado:,.2f}"
        )
        return allocation

    async def reverse_allocation(
        self,
        allocation_id: UUID,
        user_id: UUID,
        motivo: str,
    ) -> CostAllocation:
        """Reverte uma alocação executada.

        Args:
            allocation_id: ID da alocação
            user_id: ID do usuário
            motivo: Motivo da reversão

        Returns:
            Alocação de reversão criada
        """
        original = await self.session.get(CostAllocation, allocation_id)
        if not original:
            raise ValueError(f"Alocação {allocation_id} não encontrada")

        if original.status != AllocationStatus.EXECUTED:
            raise ValueError(
                f"Apenas alocações executadas podem ser revertidas. "
                f"Status atual: {original.status.value}"
            )

        # Marca original como revertida
        original.status = AllocationStatus.REVERSED
        original.revertido_por = user_id
        original.revertido_em = datetime.utcnow()
        original.motivo_reversao = motivo

        # Cria alocação de reversão (valor negativo)
        reversal = CostAllocation(
            condominio_id=original.condominio_id,
            codigo=f"REV-{original.codigo}",
            tipo=original.tipo,
            metodo=original.metodo,
            origem_tipo=original.origem_tipo,
            origem_id=original.origem_id,
            destino_tipo=original.destino_tipo,
            destino_id=original.destino_id,
            valor_alocado=-original.valor_alocado,
            percentual_alocado=original.percentual_alocado,
            driver_id=original.driver_id,
            driver_quantidade=original.driver_quantidade,
            data_alocacao=date.today(),
            periodo_inicio=original.periodo_inicio,
            periodo_fim=original.periodo_fim,
            descricao=f"Reversão: {motivo}",
            status=AllocationStatus.EXECUTED,
            alocacao_referencia_id=original.id,
            criado_por=user_id,
            executado_por=user_id,
            executado_em=datetime.utcnow(),
            ativo=True,
        )

        # Reverte custo indireto do destino
        if original.destino_tipo == "object":
            obj = await self.session.get(CostObject, original.destino_id)
            if obj:
                obj.custo_indireto = (obj.custo_indireto or Decimal("0")) - original.valor_alocado

        self.session.add(reversal)
        await self.session.flush()

        logger.info(
            f"Alocação {allocation_id} revertida. "
            f"Reversão: {reversal.id}"
        )
        return reversal

    async def batch_execute(
        self,
        allocation_ids: list[UUID],
        user_id: UUID,
    ) -> dict[str, Any]:
        """Executa múltiplas alocações em lote.

        Args:
            allocation_ids: Lista de IDs das alocações
            user_id: ID do usuário

        Returns:
            Resultado do lote
        """
        executed = []
        failed = []

        for alloc_id in allocation_ids:
            try:
                allocation = await self.execute_allocation(alloc_id, user_id)
                executed.append({
                    "id": str(allocation.id),
                    "valor": float(allocation.valor_alocado),
                })
            except Exception as e:
                failed.append({
                    "id": str(alloc_id),
                    "erro": str(e),
                })

        await self.session.commit()

        total_executed = sum(a["valor"] for a in executed)

        result = {
            "total_solicitadas": len(allocation_ids),
            "executadas": len(executed),
            "falhas": len(failed),
            "valor_total_executado": total_executed,
            "detalhes_executadas": executed,
            "detalhes_falhas": failed,
        }

        logger.info(
            f"Lote executado: {len(executed)}/{len(allocation_ids)} alocações. "
            f"Total: R$ {total_executed:,.2f}"
        )
        return result

    async def get_allocation_summary(
        self,
        condominio_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
    ) -> dict[str, Any]:
        """Obtém resumo das alocações do período.

        Args:
            condominio_id: ID do condomínio
            periodo_inicio: Data inicial
            periodo_fim: Data final

        Returns:
            Resumo das alocações
        """
        # Por status
        status_query = select(
            CostAllocation.status,
            func.count(CostAllocation.id).label("count"),
            func.sum(CostAllocation.valor_alocado).label("total"),
        ).where(
            CostAllocation.condominio_id == condominio_id,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
            CostAllocation.valor_alocado > 0,  # Exclui reversões
        ).group_by(CostAllocation.status)

        status_result = await self.session.execute(status_query)
        by_status = {
            row.status.value: {
                "quantidade": row.count,
                "valor": float(row.total or 0),
            }
            for row in status_result
        }

        # Por tipo
        type_query = select(
            CostAllocation.tipo,
            func.count(CostAllocation.id).label("count"),
            func.sum(CostAllocation.valor_alocado).label("total"),
        ).where(
            CostAllocation.condominio_id == condominio_id,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.valor_alocado > 0,
        ).group_by(CostAllocation.tipo)

        type_result = await self.session.execute(type_query)
        by_type = {
            row.tipo.value: {
                "quantidade": row.count,
                "valor": float(row.total or 0),
            }
            for row in type_result
        }

        # Por método
        method_query = select(
            CostAllocation.metodo,
            func.count(CostAllocation.id).label("count"),
            func.sum(CostAllocation.valor_alocado).label("total"),
        ).where(
            CostAllocation.condominio_id == condominio_id,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.valor_alocado > 0,
        ).group_by(CostAllocation.metodo)

        method_result = await self.session.execute(method_query)
        by_method = {
            row.metodo.value if row.metodo else "N/A": {
                "quantidade": row.count,
                "valor": float(row.total or 0),
            }
            for row in method_result
        }

        # Totais
        total_query = select(
            func.count(CostAllocation.id).label("count"),
            func.sum(CostAllocation.valor_alocado).label("total"),
        ).where(
            CostAllocation.condominio_id == condominio_id,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.valor_alocado > 0,
        )
        total_result = await self.session.execute(total_query)
        totals = total_result.first()

        return {
            "periodo": {
                "inicio": periodo_inicio.isoformat(),
                "fim": periodo_fim.isoformat(),
            },
            "totais": {
                "quantidade": totals.count if totals else 0,
                "valor": float(totals.total or 0) if totals else 0,
            },
            "por_status": by_status,
            "por_tipo": by_type,
            "por_metodo": by_method,
        }
