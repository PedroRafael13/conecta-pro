"""Service de batida de ponto."""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from ..schemas.punch_schemas import JustificationCreate, PunchCreate

logger = logging.getLogger(__name__)


class PunchService:
    """Service para operacoes de ponto eletronico."""

    def __init__(self, db=None) -> None:
        self.db = db
        self._punches: list[dict[str, Any]] = []
        self._justifications: list[dict[str, Any]] = []
        self._closings: list[dict[str, Any]] = []

    async def registrar_batida(self, data: PunchCreate) -> dict[str, Any]:
        """Registra uma batida de ponto."""
        punch_id = str(uuid4())
        timestamp = data.timestamp or datetime.utcnow().isoformat()

        # Determinar status
        status = "normal"
        if data.is_offline:
            status = "offline"

        # Geofence check
        dentro_geofence = None
        if data.location:
            dentro_geofence = True  # Seria validado contra posto
            if not dentro_geofence:
                status = "fora_local"

        punch = {
            "punch_id": punch_id,
            "employee_id": data.employee_id,
            "punch_type": data.punch_type,
            "punch_timestamp": timestamp,
            "server_timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "facial_match": data.facial.match if data.facial else None,
            "facial_confidence": data.facial.confidence if data.facial else None,
            "latitude": data.location.latitude if data.location else None,
            "longitude": data.location.longitude if data.location else None,
            "dentro_geofence": dentro_geofence,
            "device_type": data.device_type,
            "is_offline": data.is_offline,
            "posto_id": data.posto_id,
        }

        self._punches.append(punch)
        logger.info(f"Batida registrada: {punch_id} employee={data.employee_id} type={data.punch_type}")
        return punch

    async def sync_offline_punches(self, punches: list[PunchCreate]) -> dict[str, Any]:
        """Sincroniza batidas offline."""
        synced = 0
        duplicates = 0
        errors = []

        for p in punches:
            # Check duplicate
            existing = [
                ep
                for ep in self._punches
                if ep["employee_id"] == p.employee_id
                and ep.get("punch_timestamp") == p.timestamp
                and ep["punch_type"] == p.punch_type
            ]
            if existing:
                duplicates += 1
                continue

            try:
                await self.registrar_batida(p)
                synced += 1
            except Exception as e:
                errors.append({"employee_id": p.employee_id, "error": str(e)})

        return {
            "total_received": len(punches),
            "total_synced": synced,
            "total_duplicates": duplicates,
            "total_errors": len(errors),
            "errors": errors,
        }

    async def get_batidas_dia(self, employee_id: int, dia: str) -> list[dict[str, Any]]:
        """Retorna batidas de um funcionario em um dia."""
        return [
            p for p in self._punches if p["employee_id"] == employee_id and p.get("punch_timestamp", "").startswith(dia)
        ]

    async def get_espelho_mensal(self, employee_id: int, month: int, year: int) -> dict[str, Any]:
        """Retorna espelho de ponto mensal."""
        prefix = f"{year}-{month:02d}"
        batidas = [
            p
            for p in self._punches
            if p["employee_id"] == employee_id and p.get("punch_timestamp", "").startswith(prefix)
        ]
        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_batidas": len(batidas),
            "batidas": batidas,
        }

    async def criar_justificativa(self, data: JustificationCreate) -> dict[str, Any]:
        """Cria uma justificativa."""
        justification = {
            "justification_id": str(uuid4()),
            "employee_id": data.employee_id,
            "punch_id": data.punch_id,
            "type": data.justification_type,
            "reason": data.reason,
            "category": data.category,
            "status": "pendente",
            "attachments": data.attachments,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._justifications.append(justification)
        return justification

    async def revisar_justificativa(
        self, justification_id: str, action: str, reviewer_id: str, notes: str = None
    ) -> dict[str, Any]:
        """Aprova ou rejeita justificativa."""
        for j in self._justifications:
            if j["justification_id"] == justification_id:
                j["status"] = "aprovada" if action == "aprovar" else "rejeitada"
                j["reviewed_by"] = reviewer_id
                j["reviewed_at"] = datetime.utcnow().isoformat()
                j["review_notes"] = notes
                return j
        return {"error": "Justificativa nao encontrada"}

    async def get_justificativas_pendentes(self, employee_id: int = None) -> list[dict[str, Any]]:
        """Retorna justificativas pendentes."""
        result = [j for j in self._justifications if j["status"] == "pendente"]
        if employee_id:
            result = [j for j in result if j["employee_id"] == employee_id]
        return result

    async def fechar_mes(self, employee_id: int, month: int, year: int, fechado_por: str) -> dict[str, Any]:
        """Fecha o ponto mensal de um funcionario."""
        closing = {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_horas_trabalhadas": 0.0,
            "total_horas_extras_50": 0.0,
            "total_horas_extras_100": 0.0,
            "total_faltas": 0,
            "total_atrasos_minutos": 0.0,
            "total_dias_trabalhados": 0,
            "fechado": True,
            "fechado_por": fechado_por,
            "fechado_em": datetime.utcnow().isoformat(),
        }
        self._closings.append(closing)
        return closing
