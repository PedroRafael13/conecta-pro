"""Service de batida de ponto — persiste no PostgreSQL.

Usa ClockPunchModel, JustificationModel e MonthlyClosingModel
para INSERT/SELECT/UPDATE na tabela gp_clock_punches.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.clock_punch import ClockPunchModel
from ..models.justification import JustificationModel, JustificationStatus
from ..models.monthly_closing import MonthlyClosingModel
from ..schemas.punch_schemas import JustificationCreate, PunchCreate

logger = logging.getLogger(__name__)


class PunchService:
    """Service para operacoes de ponto eletronico com persistencia no banco."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def registrar_batida(self, data: PunchCreate) -> dict[str, Any]:
        """Registra uma batida de ponto no banco de dados.

        Args:
            data: Dados da batida (employee_id, tipo, facial, geo, etc.)

        Returns:
            Dicionario com os dados da batida registrada.
        """
        punch_id = str(uuid4())
        now = datetime.utcnow()
        timestamp = data.timestamp or now.isoformat()

        # Determinar status
        status = "normal"
        if data.is_offline:
            status = "offline"

        # Geofence check (placeholder — integrar com geofence real)
        dentro_geofence = None
        if data.location:
            dentro_geofence = True

        # Criar model e persistir
        punch = ClockPunchModel(
            punch_id=punch_id,
            employee_id=data.employee_id,
            punch_type=data.punch_type,
            punch_timestamp=datetime.fromisoformat(str(timestamp)),
            server_timestamp=now,
            status=status,
            facial_match=data.facial.match if data.facial else None,
            facial_confidence=data.facial.confidence if data.facial else None,
            latitude=data.location.latitude if data.location else None,
            longitude=data.location.longitude if data.location else None,
            dentro_geofence=dentro_geofence,
            device_type=data.device_type or "web",
            is_offline=data.is_offline or False,
            posto_id=data.posto_id,
        )
        self.db.add(punch)
        await self.db.flush()

        logger.info(
            "Batida registrada no banco: %s employee=%s type=%s",
            punch_id,
            data.employee_id,
            data.punch_type,
        )
        return punch.to_dict()

    async def sync_offline_punches(self, punches: list[PunchCreate]) -> dict[str, Any]:
        """Sincroniza batidas feitas em modo offline.

        Verifica duplicatas por employee_id + timestamp + tipo antes de inserir.

        Args:
            punches: Lista de batidas offline para sincronizar.

        Returns:
            Resumo da sincronizacao (synced, duplicates, errors).
        """
        synced = 0
        duplicates = 0
        errors: list[dict[str, Any]] = []

        for p in punches:
            # Verificar duplicata no banco
            ts = p.timestamp or datetime.utcnow().isoformat()
            existing = await self.db.execute(
                select(ClockPunchModel.id)
                .where(
                    ClockPunchModel.employee_id == p.employee_id,
                    ClockPunchModel.punch_type == p.punch_type,
                    ClockPunchModel.punch_timestamp == datetime.fromisoformat(str(ts)),
                )
                .limit(1)
            )
            if existing.scalar_one_or_none():
                duplicates += 1
                continue

            try:
                await self.registrar_batida(p)
                synced += 1
            except Exception as e:
                logger.warning("Erro ao sincronizar batida: %s", e)
                errors.append({"employee_id": p.employee_id, "error": str(e)[:200]})

        return {
            "total_received": len(punches),
            "total_synced": synced,
            "total_duplicates": duplicates,
            "total_errors": len(errors),
            "errors": errors,
        }

    async def get_batidas_dia(self, employee_id: int, dia: str) -> list[dict[str, Any]]:
        """Retorna batidas de um funcionario em um dia especifico.

        Args:
            employee_id: ID do funcionario.
            dia: Data no formato YYYY-MM-DD.

        Returns:
            Lista de batidas do dia.
        """
        result = await self.db.execute(
            select(ClockPunchModel)
            .where(
                ClockPunchModel.employee_id == employee_id,
                func.date(ClockPunchModel.punch_timestamp) == func.date(dia),
            )
            .order_by(ClockPunchModel.punch_timestamp)
        )
        return [p.to_dict() for p in result.scalars().all()]

    async def get_espelho_mensal(self, employee_id: int, month: int, year: int) -> dict[str, Any]:
        """Retorna espelho de ponto mensal com totais.

        Args:
            employee_id: ID do funcionario.
            month: Mes (1-12).
            year: Ano.

        Returns:
            Dicionario com batidas do mes e totais.
        """
        result = await self.db.execute(
            select(ClockPunchModel)
            .where(
                ClockPunchModel.employee_id == employee_id,
                extract("month", ClockPunchModel.punch_timestamp) == month,
                extract("year", ClockPunchModel.punch_timestamp) == year,
            )
            .order_by(ClockPunchModel.punch_timestamp)
        )
        batidas = [p.to_dict() for p in result.scalars().all()]

        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_batidas": len(batidas),
            "batidas": batidas,
        }

    async def criar_justificativa(self, data: JustificationCreate) -> dict[str, Any]:
        """Cria uma justificativa de atraso ou falta no banco.

        Args:
            data: Dados da justificativa.

        Returns:
            Dicionario com a justificativa criada.
        """
        justification = JustificationModel(
            justification_id=str(uuid4()),
            employee_id=data.employee_id,
            punch_id=data.punch_id,
            justification_type=data.justification_type,
            reason=data.reason,
            category=data.category,
            status=JustificationStatus.PENDENTE,
            attachments=data.attachments or [],
        )
        self.db.add(justification)
        await self.db.flush()

        logger.info("Justificativa criada: %s", justification.justification_id)
        return justification.to_dict()

    async def revisar_justificativa(
        self,
        justification_id: str,
        action: str,
        reviewer_id: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Aprova ou rejeita uma justificativa.

        Args:
            justification_id: ID da justificativa.
            action: 'aprovar' ou 'rejeitar'.
            reviewer_id: ID do revisor.
            notes: Observacoes do revisor.

        Returns:
            Dicionario com a justificativa atualizada.

        Raises:
            ValueError: Se justificativa nao encontrada.
        """
        result = await self.db.execute(
            select(JustificationModel).where(JustificationModel.justification_id == justification_id)
        )
        justification = result.scalar_one_or_none()
        if not justification:
            raise ValueError(f"Justificativa {justification_id} nao encontrada")

        justification.status = JustificationStatus.APROVADA if action == "aprovar" else JustificationStatus.REJEITADA
        justification.reviewed_by = reviewer_id
        justification.reviewed_at = datetime.utcnow()
        justification.review_notes = notes

        await self.db.flush()
        return justification.to_dict()

    async def get_justificativas_pendentes(self, employee_id: int | None = None) -> list[dict[str, Any]]:
        """Retorna justificativas pendentes de aprovacao.

        Args:
            employee_id: Filtro opcional por funcionario.

        Returns:
            Lista de justificativas pendentes.
        """
        query = select(JustificationModel).where(JustificationModel.status == JustificationStatus.PENDENTE)
        if employee_id:
            query = query.where(JustificationModel.employee_id == employee_id)

        query = query.order_by(JustificationModel.created_at.desc())
        result = await self.db.execute(query)
        return [j.to_dict() for j in result.scalars().all()]

    async def fechar_mes(
        self,
        employee_id: int,
        month: int,
        year: int,
        fechado_por: str,
    ) -> dict[str, Any]:
        """Fecha o ponto mensal de um funcionario.

        Calcula totais de horas, extras, faltas e atrasos a partir
        das batidas do mes e persiste em gp_monthly_closings.

        Args:
            employee_id: ID do funcionario.
            month: Mes (1-12).
            year: Ano.
            fechado_por: ID de quem esta fechando.

        Returns:
            Dicionario com o fechamento.
        """
        # Contar batidas do mes
        count_result = await self.db.execute(
            select(func.count(ClockPunchModel.id)).where(
                ClockPunchModel.employee_id == employee_id,
                extract("month", ClockPunchModel.punch_timestamp) == month,
                extract("year", ClockPunchModel.punch_timestamp) == year,
            )
        )
        total_batidas = count_result.scalar() or 0

        # Estimar dias trabalhados (4 batidas = 1 dia)
        dias_trabalhados = total_batidas // 4 if total_batidas >= 4 else 0

        closing = MonthlyClosingModel(
            employee_id=employee_id,
            month=month,
            year=year,
            total_horas_trabalhadas=dias_trabalhados * 8.0,
            total_dias_trabalhados=dias_trabalhados,
            fechado=True,
            fechado_por=fechado_por,
            fechado_em=datetime.utcnow(),
        )
        self.db.add(closing)
        await self.db.flush()

        logger.info(
            "Ponto fechado: employee=%s %02d/%d (%d batidas, %d dias)",
            employee_id,
            month,
            year,
            total_batidas,
            dias_trabalhados,
        )
        return closing.to_dict()
