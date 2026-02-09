"""
Service para gerenciamento de templates de escalas.

Implementa lógica de negócio para extração de templates de escalas existentes
e aplicação de templates em novos períodos.
"""

import calendar
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.models.scale import Scale
from modules.operacional.repositories.scale_repository import ScaleRepository
from modules.operacional.repositories.shift_repository import ShiftRepository
from modules.operacional.schemas.scale import ScaleCreate
from modules.operacional.schemas.scale_template import (
    ScaleTemplateApplyRequest,
    TemplateData,
    TemplateMetadata,
    TemplateShiftPattern,
)


class ScaleTemplateService:
    """Service para operações com templates de escalas."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.scale_repo = ScaleRepository(db)
        self.shift_repo = ShiftRepository(db)

    async def extract_template_from_scale(
        self,
        scale_id: str,
        include_employee_mapping: bool = False,
    ) -> TemplateData:
        """
        Extrai estrutura de template de uma escala existente.

        Remove dados específicos de datas e mantém apenas padrões de alocação.

        Args:
            scale_id: ID da escala base
            include_employee_mapping: Se deve manter IDs reais de funcionários

        Returns:
            TemplateData com estrutura da escala

        Raises:
            ValueError: Se escala não encontrada ou inválida
        """
        scale = await self.scale_repo.get_by_id(scale_id)
        if not scale:
            raise ValueError(f"Escala não encontrada: {scale_id}")

        # Carregar turnos da escala
        shifts = await self.shift_repo.list_by_scale(scale_id)
        if not shifts:
            raise ValueError("Escala não possui turnos para extrair template")

        # Agrupar turnos por funcionário e padrão
        shifts_pattern = self._extract_shift_patterns(shifts, include_employee_mapping)

        # Calcular metadados
        metadata = self._calculate_metadata(shifts, scale)

        # Coletar postos únicos
        posts = list({shift.post_id for shift in shifts})

        template_data = TemplateData(
            scale_type=scale.scale_type,
            posts=posts,
            shifts_pattern=shifts_pattern,
            config=scale.config or {},
            metadata=metadata,
        )

        logger.info(
            f"Template extraído da escala {scale_id}: "
            f"{len(shifts_pattern)} padrões, {metadata.total_employees} funcionários"
        )

        return template_data

    def _extract_shift_patterns(
        self,
        shifts: list,
        include_employee_mapping: bool,
    ) -> list[TemplateShiftPattern]:
        """
        Extrai padrões de turnos dos shifts.

        Agrupa shifts por funcionário/posto/horário e identifica dias da semana.
        """
        patterns_dict: dict[str, dict[str, Any]] = {}

        for shift in shifts:
            if shift.status == "off_day":
                continue

            # Criar chave única por funcionário/posto/horário
            employee_key = shift.employee_id if include_employee_mapping else "EMPLOYEE_PLACEHOLDER"
            pattern_key = f"{employee_key}:{shift.post_id}:{shift.planned_start_time}:{shift.planned_end_time}"

            if pattern_key not in patterns_dict:
                patterns_dict[pattern_key] = {
                    "employee_id": employee_key,
                    "post_id": shift.post_id,
                    "start_time": shift.planned_start_time.strftime("%H:%M"),
                    "end_time": shift.planned_end_time.strftime("%H:%M"),
                    "days_of_week": set(),
                    "shift_type": self._infer_shift_type(shift),
                    "is_night_shift": shift.is_night_shift or False,
                    "break_minutes": shift.planned_break_minutes or 60,
                }

            # Adicionar dia da semana (0=segunda, 6=domingo)
            weekday = shift.shift_date.weekday()
            patterns_dict[pattern_key]["days_of_week"].add(weekday)

        # Converter para lista de TemplateShiftPattern
        patterns = []
        for pattern_data in patterns_dict.values():
            # Converter set de dias para lista ordenada
            pattern_data["days_of_week"] = sorted(pattern_data["days_of_week"])

            patterns.append(TemplateShiftPattern(**pattern_data))

        return patterns

    def _infer_shift_type(self, shift) -> str:
        """Infere tipo de turno baseado nas características."""
        # Calcular duração do turno
        start = datetime.combine(date.today(), shift.planned_start_time)
        end = datetime.combine(date.today(), shift.planned_end_time)

        # Se end < start, turno cruza meia-noite
        if end < start:
            end += timedelta(days=1)

        duration_hours = (end - start).total_seconds() / 3600

        # Inferir tipo baseado na duração
        if duration_hours >= 11 and duration_hours <= 13:
            return "12x36"
        elif duration_hours >= 7 and duration_hours <= 9:
            return "administrativo"
        elif duration_hours >= 5 and duration_hours <= 7:
            return "6x1"
        else:
            return "personalizado"

    def _calculate_metadata(self, shifts: list, scale: Scale) -> TemplateMetadata:
        """Calcula metadados do template."""
        # Total de funcionários únicos
        unique_employees = {s.employee_id for s in shifts if s.employee_id}
        total_employees = len(unique_employees)

        # Total de turnos válidos (não folgas)
        valid_shifts = [s for s in shifts if s.status != "off_day"]
        total_shifts = len(valid_shifts)

        # Horas médias por funcionário
        total_hours = sum(s.planned_hours for s in valid_shifts)
        avg_hours = total_hours / total_employees if total_employees > 0 else 0

        # Cobertura (baseado em métricas da escala)
        coverage = scale.fill_rate if hasattr(scale, "fill_rate") else 100.0

        return TemplateMetadata(
            total_employees=total_employees,
            coverage_percentage=coverage,
            total_shifts_per_month=total_shifts,
            avg_hours_per_employee=avg_hours,
        )

    async def apply_template_to_period(
        self,
        template_data: dict[str, Any],
        apply_request: ScaleTemplateApplyRequest,
        created_by: str,
    ) -> Scale:
        """
        Aplica template em um novo período, criando nova escala.

        Args:
            template_data: Dados do template
            apply_request: Configurações de aplicação
            created_by: ID do usuário criador

        Returns:
            Scale criada

        Raises:
            ValueError: Se período inválido ou já existe escala
        """
        month = apply_request.month
        year = apply_request.year

        # Validar período
        if not self._validate_period(month, year):
            raise ValueError(f"Período inválido: {month}/{year}")

        # Determinar posto (do request ou do template)
        post_id = apply_request.post_id or template_data.get("posts", [])[0]
        if not post_id:
            raise ValueError("Posto não especificado")

        # Verificar se já existe escala para o período
        existing = await self.scale_repo.get_by_post_and_period(post_id, month, year)
        if existing:
            raise ValueError(f"Já existe escala para o posto {post_id} em {month}/{year}")

        # Criar escala base
        scale_type = template_data.get("scale_type", "personalizado")
        config = template_data.get("config", {})

        # Sobrescrever config se fornecido
        if apply_request.config_overrides:
            config.update(apply_request.config_overrides)

        scale_data = ScaleCreate(
            post_id=post_id,
            scale_type=scale_type,
            month=month,
            year=year,
            config=config,
        )

        scale = await self.scale_repo.create(scale_data, created_by=created_by)

        # Gerar turnos baseado no template
        shifts_data = self._generate_shifts_from_template(
            template_data=template_data,
            scale_id=scale.id,
            post_id=post_id,
            month=month,
            year=year,
            employee_mapping=apply_request.employee_mapping or {},
        )

        # Criar turnos em lote
        await self.shift_repo.create_bulk(shifts_data)

        # Atualizar métricas da escala
        scale = await self.scale_repo.update_metrics(scale.id)

        logger.info(f"Template aplicado: escala {scale.id} criada com {len(shifts_data)} turnos")

        return scale

    def _validate_period(self, month: int, year: int) -> bool:
        """Valida se o período é válido."""
        if month < 1 or month > 12:
            return False
        if year < 2020 or year > 2100:
            return False
        return True

    def _generate_shifts_from_template(
        self,
        template_data: dict[str, Any],
        scale_id: str,
        post_id: str,
        month: int,
        year: int,
        employee_mapping: dict[str, str],
    ) -> list[dict[str, Any]]:
        """
        Gera dados de turnos baseado no template para um período específico.

        Args:
            template_data: Dados do template
            scale_id: ID da escala criada
            post_id: ID do posto
            month: Mês da nova escala
            year: Ano da nova escala
            employee_mapping: Mapeamento de IDs de funcionários

        Returns:
            Lista de dicts com dados de turnos
        """
        shifts_data = []
        shifts_pattern = template_data.get("shifts_pattern", [])

        # Calcular dias do mês
        _, last_day = calendar.monthrange(year, month)

        for day in range(1, last_day + 1):
            shift_date = date(year, month, day)
            weekday = shift_date.weekday()

            # Para cada padrão de turno
            for pattern in shifts_pattern:
                # Verificar se o padrão se aplica a este dia da semana
                if weekday not in pattern.get("days_of_week", []):
                    continue

                # Mapear funcionário
                template_employee_id = pattern.get("employee_id")
                employee_id = employee_mapping.get(
                    template_employee_id,
                    template_employee_id if template_employee_id != "EMPLOYEE_PLACEHOLDER" else None,
                )

                # Parse horários
                start_time = time.fromisoformat(pattern.get("start_time"))
                end_time = time.fromisoformat(pattern.get("end_time"))

                shift_data = {
                    "scale_id": scale_id,
                    "post_id": post_id,
                    "employee_id": employee_id,
                    "shift_date": shift_date,
                    "planned_start_time": start_time,
                    "planned_end_time": end_time,
                    "planned_break_minutes": pattern.get("break_minutes", 60),
                    "is_night_shift": pattern.get("is_night_shift", False),
                    "status": "scheduled",
                }

                shifts_data.append(shift_data)

        return shifts_data
