"""
Serviço de Geração Automática de Escalas.

Gera escalas mensais automaticamente baseadas em alocações ativas.
"""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.models.allocation import Allocation, AllocationStatus
from modules.operacional.models.scale import ScaleType
from modules.operacional.repositories.scale_repository import ScaleRepository
from modules.operacional.repositories.shift_repository import ShiftRepository
from modules.operacional.schemas.scale import ScaleCreate
from modules.operacional.services.scale_generator import scale_generator


class AutoScaleService:
    """
    Serviço para geração automática de escalas.

    Detecta alocações ativas sem escala no mês atual e gera automaticamente.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.scale_repo = ScaleRepository(db)
        self.shift_repo = ShiftRepository(db)

    async def generate_scales_for_current_month(
        self,
        created_by: str | None = None,
    ) -> dict:
        """
        Gera escalas para o mês atual baseado em alocações ativas.

        Args:
            created_by: ID do usuário que iniciou a geração (opcional)

        Returns:
            Dicionário com resumo da geração
        """
        today = date.today()
        month = today.month
        year = today.year

        logger.info(f"Iniciando geração automática de escalas para {month:02d}/{year}")

        # Buscar alocações ativas
        allocations = await self._get_active_allocations()
        logger.info(f"Encontradas {len(allocations)} alocações ativas")

        if not allocations:
            return {
                "success": True,
                "message": "Nenhuma alocação ativa encontrada",
                "scales_created": 0,
                "shifts_created": 0,
                "errors": [],
            }

        # Agrupar alocações por posto
        allocations_by_post = self._group_allocations_by_post(allocations)
        logger.info(f"Postos com alocações: {len(allocations_by_post)}")

        scales_created = 0
        shifts_created = 0
        errors = []

        # Gerar escala para cada posto
        for post_id, post_allocations in allocations_by_post.items():
            try:
                # Verificar se já existe escala para o período
                existing = await self.scale_repo.get_by_post_and_period(post_id, month, year)
                if existing:
                    logger.info(f"Escala já existe para posto {post_id} em {month:02d}/{year}")
                    continue

                # Extrair employee_ids
                employee_ids = [alloc.employee_id for alloc in post_allocations]

                # Determinar tipo de escala (usar 12x36 como padrão)
                scale_type = ScaleType.SCALE_12X36

                # Criar escala
                scale_data = ScaleCreate(
                    post_id=post_id,
                    scale_type=scale_type,
                    month=month,
                    year=year,
                    notes=f"Escala gerada automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                )

                scale = await self.scale_repo.create(scale_data, created_by=created_by)
                logger.info(f"Escala criada: {scale.id} para posto {post_id}")

                # Gerar turnos com IA
                shifts_data = scale_generator.generate(
                    scale_id=scale.id,
                    post_id=post_id,
                    scale_type=scale_type,
                    month=month,
                    year=year,
                    employee_ids=employee_ids,
                    config=None,
                )

                # Criar turnos em lote
                await self.shift_repo.create_bulk(shifts_data)

                # Atualizar métricas da escala
                await self.scale_repo.update_metrics(scale.id)

                scales_created += 1
                shifts_created += len(shifts_data)

                logger.info(
                    f"Escala {scale.id} gerada com {len(shifts_data)} turnos para {len(employee_ids)} funcionários"
                )

            except Exception as e:
                error_msg = f"Erro ao gerar escala para posto {post_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

        return {
            "success": True,
            "message": f"Geradas {scales_created} escalas com {shifts_created} turnos",
            "scales_created": scales_created,
            "shifts_created": shifts_created,
            "errors": errors,
        }

    async def generate_scales_for_month(
        self,
        month: int,
        year: int,
        created_by: str | None = None,
    ) -> dict:
        """
        Gera escalas para um mês específico.

        Args:
            month: Mês (1-12)
            year: Ano
            created_by: ID do usuário que iniciou a geração (opcional)

        Returns:
            Dicionário com resumo da geração
        """
        logger.info(f"Iniciando geração de escalas para {month:02d}/{year}")

        # Buscar alocações ativas
        allocations = await self._get_active_allocations()

        if not allocations:
            return {
                "success": True,
                "message": "Nenhuma alocação ativa encontrada",
                "scales_created": 0,
                "shifts_created": 0,
                "errors": [],
            }

        # Agrupar por posto
        allocations_by_post = self._group_allocations_by_post(allocations)

        scales_created = 0
        shifts_created = 0
        errors = []

        # Gerar escala para cada posto
        for post_id, post_allocations in allocations_by_post.items():
            try:
                # Verificar se já existe
                existing = await self.scale_repo.get_by_post_and_period(post_id, month, year)
                if existing:
                    logger.info(f"Escala já existe para posto {post_id} em {month:02d}/{year}")
                    continue

                employee_ids = [alloc.employee_id for alloc in post_allocations]
                scale_type = ScaleType.SCALE_12X36

                # Criar escala
                scale_data = ScaleCreate(
                    post_id=post_id,
                    scale_type=scale_type,
                    month=month,
                    year=year,
                    notes=f"Escala gerada automaticamente para {month:02d}/{year}",
                )

                scale = await self.scale_repo.create(scale_data, created_by=created_by)

                # Gerar turnos
                shifts_data = scale_generator.generate(
                    scale_id=scale.id,
                    post_id=post_id,
                    scale_type=scale_type,
                    month=month,
                    year=year,
                    employee_ids=employee_ids,
                    config=None,
                )

                await self.shift_repo.create_bulk(shifts_data)
                await self.scale_repo.update_metrics(scale.id)

                scales_created += 1
                shifts_created += len(shifts_data)

                logger.info(f"Escala {scale.id} gerada com {len(shifts_data)} turnos")

            except Exception as e:
                error_msg = f"Erro ao gerar escala para posto {post_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        return {
            "success": True,
            "message": f"Geradas {scales_created} escalas com {shifts_created} turnos",
            "scales_created": scales_created,
            "shifts_created": shifts_created,
            "errors": errors,
        }

    async def _get_active_allocations(self) -> list[Allocation]:
        """Busca todas as alocações ativas."""
        query = select(Allocation).where(
            Allocation.is_active.is_(True),
            Allocation.status == AllocationStatus.ACTIVE.value,
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _group_allocations_by_post(self, allocations: list[Allocation]) -> dict[str, list[Allocation]]:
        """Agrupa alocações por posto."""
        grouped = {}
        for allocation in allocations:
            if allocation.post_id not in grouped:
                grouped[allocation.post_id] = []
            grouped[allocation.post_id].append(allocation)
        return grouped
