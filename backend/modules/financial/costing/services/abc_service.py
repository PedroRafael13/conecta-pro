"""ABC Costing Service - Custeio Baseado em Atividades."""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.costing.models import (
    CostActivity,
    CostAllocation,
    CostAnalysis,
    CostDriver,
    CostObject,
    CostPool,
)
from modules.financial.costing.models.cost_activity import ActivityStatus
from modules.financial.costing.models.cost_allocation import (
    AllocationStatus,
    AllocationType,
)
from modules.financial.costing.models.cost_analysis import AnalysisType
from modules.financial.costing.models.cost_driver import DriverStatus

logger = logging.getLogger(__name__)


class ABCService:
    """Serviço de Custeio Baseado em Atividades (ABC).

    Implementa a metodologia ABC de duas etapas:
    1. Alocação de custos dos pools para atividades
    2. Alocação de custos das atividades para objetos de custo
    """

    def __init__(self, session: AsyncSession):
        """Inicializa o serviço ABC."""
        self.session = session

    async def calculate_driver_rates(
        self,
        condominio_id: UUID,
        periodo_inicio: date,  # pylint: disable=unused-argument
        periodo_fim: date,  # pylint: disable=unused-argument
    ) -> list[dict[str, Any]]:
        """Calcula taxas dos cost drivers para o período.

        Args:
            condominio_id: ID do condomínio
            periodo_inicio: Data inicial do período
            periodo_fim: Data final do período

        Returns:
            Lista de drivers com suas taxas calculadas
        """
        query = select(CostDriver).where(
            CostDriver.condominio_id == condominio_id,
            CostDriver.status == DriverStatus.ACTIVE,
            CostDriver.ativo.is_(True),
        )
        result = await self.session.execute(query)
        drivers = result.scalars().all()

        calculated_rates = []
        for driver in drivers:
            if driver.quantidade_usada and driver.quantidade_usada > 0:
                rate = driver.custo_total / driver.quantidade_usada
            else:
                rate = Decimal("0")

            calculated_rates.append(
                {
                    "driver_id": str(driver.id),
                    "codigo": driver.codigo,
                    "nome": driver.nome,
                    "custo_total": float(driver.custo_total),
                    "quantidade_usada": float(driver.quantidade_usada or 0),
                    "capacidade_pratica": float(driver.capacidade_pratica or 0),
                    "taxa_calculada": float(rate),
                    "unidade_medida": driver.unidade_medida.value if driver.unidade_medida else None,
                    "capacidade_ociosa_percentual": float(driver.capacity_usage_percent or 0),
                    "custo_ociosidade": float(driver.idle_capacity_cost or 0),
                }
            )

        logger.info(f"Calculadas taxas de {len(calculated_rates)} drivers para condomínio {condominio_id}")
        return calculated_rates

    async def calculate_activity_costs(
        self,
        condominio_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
    ) -> list[dict[str, Any]]:
        """Calcula custos totais das atividades.

        Soma custos diretos + custos alocados dos pools.

        Args:
            condominio_id: ID do condomínio
            periodo_inicio: Data inicial
            periodo_fim: Data final

        Returns:
            Lista de atividades com custos calculados
        """
        query = select(CostActivity).where(
            CostActivity.condominio_id == condominio_id,
            CostActivity.status == ActivityStatus.ACTIVE,
            CostActivity.ativo.is_(True),
        )
        result = await self.session.execute(query)
        activities = result.scalars().all()

        activity_costs = []
        for activity in activities:
            # Busca alocações recebidas
            alloc_query = select(func.sum(CostAllocation.valor_alocado)).where(
                CostAllocation.destino_id == activity.id,
                CostAllocation.tipo == AllocationType.POOL_TO_ACTIVITY,
                CostAllocation.status == AllocationStatus.EXECUTED,
                CostAllocation.data_alocacao >= periodo_inicio,
                CostAllocation.data_alocacao <= periodo_fim,
            )
            alloc_result = await self.session.execute(alloc_query)
            allocated_cost = alloc_result.scalar() or Decimal("0")

            total_cost = (activity.custo_direto or Decimal("0")) + allocated_cost

            # Calcula taxa por unidade de output
            if activity.output_quantidade and activity.output_quantidade > 0:
                rate_per_unit = total_cost / activity.output_quantidade
            else:
                rate_per_unit = Decimal("0")

            activity_costs.append(
                {
                    "activity_id": str(activity.id),
                    "codigo": activity.codigo,
                    "nome": activity.nome,
                    "nivel": activity.nivel.value if activity.nivel else None,
                    "tipo_valor": (activity.tipo_valor_agregado.value if activity.tipo_valor_agregado else None),
                    "custo_direto": float(activity.custo_direto or 0),
                    "custo_alocado": float(allocated_cost),
                    "custo_total": float(total_cost),
                    "output_quantidade": float(activity.output_quantidade or 0),
                    "taxa_por_unidade": float(rate_per_unit),
                    "capacidade_pratica": float(activity.capacidade_pratica or 0),
                    "capacidade_usada": float(activity.capacidade_usada or 0),
                }
            )

        logger.info(f"Calculados custos de {len(activity_costs)} atividades para condomínio {condominio_id}")
        return activity_costs

    async def calculate_object_costs(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
    ) -> list[dict[str, Any]]:
        """Calcula custos totais dos objetos de custo.

        Soma custos diretos + custos indiretos alocados.

        Args:
            condominio_id: ID do condomínio
            periodo_inicio: Data inicial
            periodo_fim: Data final

        Returns:
            Lista de objetos com custos e margens calculados
        """
        query = select(CostObject).where(
            CostObject.condominio_id == condominio_id,
            CostObject.ativo.is_(True),
        )
        result = await self.session.execute(query)
        objects = result.scalars().all()

        object_costs = []
        for obj in objects:
            # Busca alocações recebidas das atividades
            alloc_query = select(func.sum(CostAllocation.valor_alocado)).where(
                CostAllocation.destino_id == obj.id,
                CostAllocation.tipo == AllocationType.ACTIVITY_TO_OBJECT,
                CostAllocation.status == AllocationStatus.EXECUTED,
                CostAllocation.data_alocacao >= periodo_inicio,
                CostAllocation.data_alocacao <= periodo_fim,
            )
            alloc_result = await self.session.execute(alloc_query)
            indirect_cost = alloc_result.scalar() or Decimal("0")

            direct_cost = obj.custo_direto or Decimal("0")
            total_cost = direct_cost + indirect_cost

            # Calcula margens
            receita = obj.receita or Decimal("0")
            gross_margin = receita - total_cost

            if receita > 0:
                gross_margin_pct = (gross_margin / receita) * 100
            else:
                gross_margin_pct = Decimal("0")

            # Custo unitário
            if obj.quantidade and obj.quantidade > 0:
                unit_cost = total_cost / obj.quantidade
            else:
                unit_cost = Decimal("0")

            object_costs.append(
                {
                    "object_id": str(obj.id),
                    "codigo": obj.codigo,
                    "nome": obj.nome,
                    "tipo": obj.tipo.value if obj.tipo else None,
                    "custo_direto": float(direct_cost),
                    "custo_indireto": float(indirect_cost),
                    "custo_total": float(total_cost),
                    "receita": float(receita),
                    "margem_bruta": float(gross_margin),
                    "margem_bruta_percentual": float(gross_margin_pct),
                    "quantidade": float(obj.quantidade or 0),
                    "custo_unitario": float(unit_cost),
                    "nivel_lucratividade": (obj.profitability_level.value if obj.profitability_level else None),
                }
            )

        # Ordena por margem (do pior para o melhor para identificar problemas)
        object_costs.sort(key=lambda x: x["margem_bruta_percentual"])

        logger.info(f"Calculados custos de {len(object_costs)} objetos para condomínio {condominio_id}")
        return object_costs

    async def run_abc_costing(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Executa custeio ABC completo para o período.

        Args:
            condominio_id: ID do condomínio
            periodo_inicio: Data inicial
            periodo_fim: Data final
            user_id: ID do usuário executando

        Returns:
            Resultado completo do custeio ABC
        """
        logger.info(f"Iniciando custeio ABC para condomínio {condominio_id} período {periodo_inicio} a {periodo_fim}")

        # Etapa 1: Calcula taxas dos drivers
        driver_rates = await self.calculate_driver_rates(condominio_id, periodo_inicio, periodo_fim)

        # Etapa 2: Calcula custos das atividades
        activity_costs = await self.calculate_activity_costs(condominio_id, periodo_inicio, periodo_fim)

        # Etapa 3: Calcula custos dos objetos
        object_costs = await self.calculate_object_costs(condominio_id, periodo_inicio, periodo_fim)

        # Estatísticas gerais
        total_driver_cost = sum(d["custo_total"] for d in driver_rates)
        total_idle_cost = sum(d["custo_ociosidade"] for d in driver_rates)
        total_activity_cost = sum(a["custo_total"] for a in activity_costs)
        total_object_cost = sum(o["custo_total"] for o in object_costs)
        total_revenue = sum(o["receita"] for o in object_costs)
        total_margin = sum(o["margem_bruta"] for o in object_costs)

        # Análise de valor agregado
        value_added = [a for a in activity_costs if a.get("tipo_valor") == "VALUE_ADDED"]
        non_value_added = [a for a in activity_costs if a.get("tipo_valor") == "NON_VALUE_ADDED"]

        result = {
            "condominio_id": str(condominio_id),
            "periodo_inicio": periodo_inicio.isoformat(),
            "periodo_fim": periodo_fim.isoformat(),
            "executado_em": datetime.utcnow().isoformat(),
            "executado_por": str(user_id) if user_id else None,
            "resumo": {
                "total_drivers": len(driver_rates),
                "total_atividades": len(activity_costs),
                "total_objetos": len(object_costs),
                "custo_total_drivers": total_driver_cost,
                "custo_ociosidade": total_idle_cost,
                "custo_total_atividades": total_activity_cost,
                "custo_total_objetos": total_object_cost,
                "receita_total": total_revenue,
                "margem_total": total_margin,
                "margem_percentual": ((total_margin / total_revenue * 100) if total_revenue > 0 else 0),
            },
            "analise_valor": {
                "atividades_valor_agregado": len(value_added),
                "custo_valor_agregado": sum(a["custo_total"] for a in value_added),
                "atividades_sem_valor": len(non_value_added),
                "custo_sem_valor": sum(a["custo_total"] for a in non_value_added),
            },
            "drivers": driver_rates,
            "atividades": activity_costs,
            "objetos": object_costs,
        }

        # Cria registro de análise
        analysis = CostAnalysis(
            condominio_id=condominio_id,
            codigo=f"ABC-{periodo_inicio.strftime('%Y%m%d')}-{periodo_fim.strftime('%Y%m%d')}",
            nome=f"Custeio ABC {periodo_inicio} a {periodo_fim}",
            tipo=AnalysisType.ABC_COSTING,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            parametros={
                "metodo": "ABC",
                "drivers_count": len(driver_rates),
                "activities_count": len(activity_costs),
                "objects_count": len(object_costs),
            },
            resultados=result["resumo"],
            insights=[
                f"Custo total alocado: R$ {total_object_cost:,.2f}",
                (
                    f"Custo de ociosidade: R$ {total_idle_cost:,.2f} ({total_idle_cost / total_driver_cost * 100:.1f}%)"
                    if total_driver_cost > 0
                    else "Sem custos de ociosidade"
                ),
                f"Margem média: {result['resumo']['margem_percentual']:.1f}%",
                (
                    f"Atividades sem valor agregado: {len(non_value_added)} "
                    f"({sum(a['custo_total'] for a in non_value_added):,.2f})"
                ),
            ],
            executado_por=user_id,
            executado_em=datetime.utcnow(),
            ativo=True,
        )
        self.session.add(analysis)
        await self.session.flush()

        result["analysis_id"] = str(analysis.id)

        logger.info(f"Custeio ABC concluído. Análise {analysis.id} criada. Custo total: R$ {total_object_cost:,.2f}")

        return result

    async def get_pool_distribution(
        self,
        pool_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
    ) -> dict[str, Any]:
        """Obtém distribuição de custos de um pool para atividades.

        Args:
            pool_id: ID do pool
            periodo_inicio: Data inicial
            periodo_fim: Data final

        Returns:
            Distribuição detalhada do pool
        """
        # Busca o pool
        pool = await self.session.get(CostPool, pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} não encontrado")

        # Busca alocações do pool
        query = select(CostAllocation).where(
            CostAllocation.origem_id == pool_id,
            CostAllocation.tipo == AllocationType.POOL_TO_ACTIVITY,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
        )
        result = await self.session.execute(query)
        allocations = result.scalars().all()

        total_allocated = sum(a.valor_alocado for a in allocations)
        unallocated = (pool.valor_total or Decimal("0")) - total_allocated

        distribution = []
        for alloc in allocations:
            activity = await self.session.get(CostActivity, alloc.destino_id)
            distribution.append(
                {
                    "allocation_id": str(alloc.id),
                    "activity_id": str(alloc.destino_id),
                    "activity_nome": activity.nome if activity else "Desconhecida",
                    "valor": float(alloc.valor_alocado),
                    "percentual": float(alloc.percentual_alocado or 0),
                    "driver_id": str(alloc.driver_id) if alloc.driver_id else None,
                    "driver_quantidade": float(alloc.driver_quantidade or 0),
                }
            )

        return {
            "pool_id": str(pool_id),
            "pool_codigo": pool.codigo,
            "pool_nome": pool.nome,
            "valor_total": float(pool.valor_total or 0),
            "valor_alocado": float(total_allocated),
            "valor_nao_alocado": float(unallocated),
            "percentual_alocado": (float(total_allocated / pool.valor_total * 100) if pool.valor_total else 0),
            "distribuicao": distribution,
        }

    async def get_activity_distribution(  # pylint: disable=too-many-locals
        self,
        activity_id: UUID,
        periodo_inicio: date,
        periodo_fim: date,
    ) -> dict[str, Any]:
        """Obtém distribuição de custos de uma atividade para objetos.

        Args:
            activity_id: ID da atividade
            periodo_inicio: Data inicial
            periodo_fim: Data final

        Returns:
            Distribuição detalhada da atividade
        """
        # Busca a atividade
        activity = await self.session.get(CostActivity, activity_id)
        if not activity:
            raise ValueError(f"Atividade {activity_id} não encontrada")

        # Busca alocações da atividade
        query = select(CostAllocation).where(
            CostAllocation.origem_id == activity_id,
            CostAllocation.tipo == AllocationType.ACTIVITY_TO_OBJECT,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
        )
        result = await self.session.execute(query)
        allocations = result.scalars().all()

        # Calcula custo total da atividade
        activity_total = activity.custo_direto or Decimal("0")

        # Soma alocações recebidas
        received_query = select(func.sum(CostAllocation.valor_alocado)).where(
            CostAllocation.destino_id == activity_id,
            CostAllocation.tipo == AllocationType.POOL_TO_ACTIVITY,
            CostAllocation.status == AllocationStatus.EXECUTED,
            CostAllocation.data_alocacao >= periodo_inicio,
            CostAllocation.data_alocacao <= periodo_fim,
        )
        received_result = await self.session.execute(received_query)
        received = received_result.scalar() or Decimal("0")
        activity_total += received

        total_allocated = sum(a.valor_alocado for a in allocations)
        unallocated = activity_total - total_allocated

        distribution = []
        for alloc in allocations:
            obj = await self.session.get(CostObject, alloc.destino_id)
            distribution.append(
                {
                    "allocation_id": str(alloc.id),
                    "object_id": str(alloc.destino_id),
                    "object_nome": obj.nome if obj else "Desconhecido",
                    "object_tipo": obj.tipo.value if obj and obj.tipo else None,
                    "valor": float(alloc.valor_alocado),
                    "percentual": float(alloc.percentual_alocado or 0),
                    "driver_id": str(alloc.driver_id) if alloc.driver_id else None,
                    "driver_quantidade": float(alloc.driver_quantidade or 0),
                }
            )

        return {
            "activity_id": str(activity_id),
            "activity_codigo": activity.codigo,
            "activity_nome": activity.nome,
            "custo_direto": float(activity.custo_direto or 0),
            "custo_recebido": float(received),
            "custo_total": float(activity_total),
            "valor_alocado": float(total_allocated),
            "valor_nao_alocado": float(unallocated),
            "percentual_alocado": (float(total_allocated / activity_total * 100) if activity_total else 0),
            "distribuicao": distribution,
        }

    async def calculate_break_even(
        self,
        object_id: UUID,
    ) -> dict[str, Any]:
        """Calcula ponto de equilíbrio para um objeto de custo.

        Args:
            object_id: ID do objeto

        Returns:
            Análise de break-even
        """
        obj = await self.session.get(CostObject, object_id)
        if not obj:
            raise ValueError(f"Objeto {object_id} não encontrado")

        custo_fixo = obj.custo_fixo or Decimal("0")
        custo_variavel = obj.custo_variavel or Decimal("0")
        quantidade = obj.quantidade or Decimal("1")
        receita = obj.receita or Decimal("0")

        # Custo variável unitário
        if quantidade > 0:
            custo_variavel_unit = custo_variavel / quantidade
            receita_unitaria = receita / quantidade
        else:
            custo_variavel_unit = Decimal("0")
            receita_unitaria = Decimal("0")

        # Margem de contribuição unitária
        margem_contrib_unit = receita_unitaria - custo_variavel_unit

        # Ponto de equilíbrio em quantidade
        if margem_contrib_unit > 0:
            break_even_qty = custo_fixo / margem_contrib_unit
            break_even_revenue = break_even_qty * receita_unitaria
        else:
            break_even_qty = Decimal("0")
            break_even_revenue = Decimal("0")

        # Margem de segurança
        if quantidade > 0 and break_even_qty > 0:
            margem_seguranca = ((quantidade - break_even_qty) / quantidade) * 100
        else:
            margem_seguranca = Decimal("0")

        return {
            "object_id": str(object_id),
            "object_nome": obj.nome,
            "custo_fixo": float(custo_fixo),
            "custo_variavel_total": float(custo_variavel),
            "custo_variavel_unitario": float(custo_variavel_unit),
            "receita_unitaria": float(receita_unitaria),
            "margem_contribuicao_unitaria": float(margem_contrib_unit),
            "ponto_equilibrio_quantidade": float(break_even_qty),
            "ponto_equilibrio_receita": float(break_even_revenue),
            "quantidade_atual": float(quantidade),
            "margem_seguranca_percentual": float(margem_seguranca),
            "acima_ponto_equilibrio": quantidade > break_even_qty if break_even_qty > 0 else False,
        }
