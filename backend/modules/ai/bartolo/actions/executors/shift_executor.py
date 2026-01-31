"""
Executor de ações relacionadas a turnos.

Integra validacoes avancadas de check-in/check-out:
- Geolocalizacao (GPS) via GeolocationService
- Biometria facial via BiometricService
- Validacao composta via CheckInValidator
- Regras de jornada CLT (intervalo entre turnos, jornada maxima, horas extras)
"""
import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select

from modules.operacional.repositories.shift_repository import ShiftRepository
from modules.operacional.repositories.post_repository import PostRepository
from modules.operacional.models.shift import ShiftStatus
from modules.operacional.models.employee import Employee
from modules.operacional.schemas.shift import ShiftCreate
from modules.operacional.permissions import has_permission
from ..action_schemas import ActionRequest, ActionPreview, ActionResult
from ..action_types import ActionType, ActionStatus
from ..action_permissions import get_required_permission
from .base_executor import BaseActionExecutor

# Imports opcionais - services de validacao avancada
try:
    from modules.operacional.services.geolocation_service import (
        GeolocationService,
        GeoPoint,
        GeolocationValidation,
    )
    _HAS_GEO_SERVICE = True
except ImportError:
    _HAS_GEO_SERVICE = False

try:
    from modules.operacional.services.biometric_service import (
        BiometricService,
        FaceValidationResult,
    )
    _HAS_BIO_SERVICE = True
except ImportError:
    _HAS_BIO_SERVICE = False

try:
    from modules.operacional.services.check_in_validator import (
        CheckInValidator,
        CheckInData,
        ValidationConfig,
        ValidationResult,
    )
    _HAS_CHECKIN_VALIDATOR = True
except ImportError:
    _HAS_CHECKIN_VALIDATOR = False

logger = logging.getLogger(__name__)

# ── Constantes de Jornada CLT ─────────────────────────────────────────────
CLT_MIN_INTER_SHIFT_HOURS = 11        # Intervalo minimo entre turnos (art. 66 CLT)
CLT_MAX_DAILY_HOURS = 10              # Jornada maxima diaria (8h + 2h extra, art. 59 CLT)
CLT_NORMAL_DAILY_HOURS = 8            # Jornada normal diaria
CLT_MAX_WEEKLY_OVERTIME_HOURS = 10    # Limite semanal de horas extras


class ShiftActionExecutor(BaseActionExecutor):
    """Executor para ações de turno."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para ação de turno."""
        action_type = request.action_type

        if action_type == ActionType.CREATE_SHIFT:
            return await self._create_shift_preview(request)
        elif action_type == ActionType.REGISTER_CHECKIN:
            return await self._checkin_preview(request)
        elif action_type == ActionType.REGISTER_CHECKOUT:
            return await self._checkout_preview(request)
        elif action_type == ActionType.MARK_ABSENCE:
            return await self._mark_absence_preview(request)
        else:
            raise ValueError(f"Ação não suportada: {action_type.value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa ação de turno."""
        action_type = request.action_type
        started_at = datetime.utcnow()

        try:
            if action_type == ActionType.CREATE_SHIFT:
                result = await self._execute_create_shift(request, action_id, started_at)
            elif action_type == ActionType.REGISTER_CHECKIN:
                result = await self._execute_checkin(request, action_id, started_at)
            elif action_type == ActionType.REGISTER_CHECKOUT:
                result = await self._execute_checkout(request, action_id, started_at)
            elif action_type == ActionType.MARK_ABSENCE:
                result = await self._execute_mark_absence(request, action_id, started_at)
            else:
                raise ValueError(f"Ação não suportada: {action_type.value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar ação {action_type.value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar ação: {action_type.value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # ── Helpers ──────────────────────────────────────────────────────────

    async def _get_employee(self, employee_id: str) -> Optional[Employee]:
        """Busca funcionário por ID."""
        result = await self.db.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    def _build_permission_info(self, request: ActionRequest) -> tuple:
        """Retorna (required_perm, user_has_perm)."""
        required_perm = get_required_permission(request.action_type)
        user_role = getattr(self, 'user_role', None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissão {required_perm.value}: role={user_role}, has_perm={user_has_perm}")
        return required_perm, user_has_perm

    def _parse_time(self, time_str: str) -> time:
        """Converte string de hora para objeto time."""
        if not time_str:
            raise ValueError("Horário não informado")
        # Suporta formatos HH:MM e HH:MM:SS
        parts = time_str.strip().split(':')
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
        return time(hour, minute, second)

    def _parse_datetime(self, dt_str: str, shift_date: date) -> datetime:
        """Converte string de hora para datetime combinando com a data do turno."""
        if not dt_str:
            raise ValueError("Horário não informado")
        # Se já for ISO datetime completo
        if 'T' in dt_str or len(dt_str) > 10:
            return datetime.fromisoformat(dt_str)
        # Se for só hora (HH:MM ou HH:MM:SS)
        t = self._parse_time(dt_str)
        return datetime.combine(shift_date, t)

    # ── Validações Avançadas ─────────────────────────────────────────────

    async def _validate_geolocation(
        self,
        params: Dict[str, Any],
        post: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Valida geolocalizacao do funcionario em relacao ao posto.

        Retorna dict com resultado da validacao ou None se servico indisponivel.
        """
        if not _HAS_GEO_SERVICE:
            logger.warning("GeolocationService nao disponivel, pulando validacao GPS")
            return None

        latitude = params.get("latitude")
        longitude = params.get("longitude")
        accuracy = params.get("gps_accuracy")

        if latitude is None or longitude is None:
            return {"status": "skipped", "reason": "Coordenadas GPS nao fornecidas"}

        # Buscar coordenadas do posto
        post_lat = getattr(post, "latitude", None)
        post_lon = getattr(post, "longitude", None)
        allowed_radius = getattr(post, "allowed_radius_meters", 100.0) or 100.0

        if post_lat is None or post_lon is None:
            return {"status": "skipped", "reason": "Posto sem coordenadas GPS cadastradas"}

        try:
            geo_service = GeolocationService()
            user_point = GeoPoint(latitude=latitude, longitude=longitude, accuracy=accuracy)
            post_point = GeoPoint(latitude=post_lat, longitude=post_lon)

            result = geo_service.validate_location(
                user_point=user_point,
                post_point=post_point,
                allowed_radius_meters=allowed_radius,
            )

            return {
                "status": "validated",
                "is_valid": result.is_valid,
                "distance_meters": result.distance_meters,
                "within_radius": result.within_radius,
                "accuracy_acceptable": result.accuracy_acceptable,
                "allowed_radius": allowed_radius,
                "message": result.message,
            }
        except Exception as e:
            logger.warning(f"Erro na validacao GPS: {e}")
            return {"status": "error", "reason": str(e)}

    async def _validate_biometric(
        self,
        params: Dict[str, Any],
        employee_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Valida biometria facial do funcionario.

        Retorna dict com resultado da validacao ou None se servico indisponivel.
        """
        if not _HAS_BIO_SERVICE:
            logger.warning("BiometricService nao disponivel, pulando validacao facial")
            return None

        photo_path = params.get("photo_path") or params.get("captured_photo")
        if not photo_path:
            return {"status": "skipped", "reason": "Foto nao fornecida"}

        if not employee_id:
            return {"status": "skipped", "reason": "ID do funcionario nao disponivel"}

        try:
            bio_service = BiometricService()
            result = await bio_service.validate_face(
                captured_photo_path=photo_path,
                employee_id=employee_id,
            )

            return {
                "status": "validated",
                "is_valid": result.is_valid,
                "confidence": result.confidence,
                "liveness_passed": result.liveness_passed,
                "face_detected": result.face_detected,
                "match_score": result.match_score,
                "message": result.message,
            }
        except Exception as e:
            logger.warning(f"Erro na validacao biometrica: {e}")
            return {"status": "error", "reason": str(e)}

    async def _validate_checkin_composite(
        self,
        params: Dict[str, Any],
        employee_id: str,
        shift_id: str,
        post: Any,
        scheduled_time: time,
    ) -> Optional[Dict[str, Any]]:
        """
        Executa validacao composta via CheckInValidator (GPS + biometria + tempo + device).

        Retorna dict com resultado completo ou None se servico indisponivel.
        """
        if not _HAS_CHECKIN_VALIDATOR or not _HAS_GEO_SERVICE or not _HAS_BIO_SERVICE:
            logger.warning("CheckInValidator ou dependencias nao disponiveis")
            return None

        post_lat = getattr(post, "latitude", None)
        post_lon = getattr(post, "longitude", None)
        if post_lat is None or post_lon is None:
            return {"status": "skipped", "reason": "Posto sem coordenadas GPS"}

        try:
            geo_service = GeolocationService()
            bio_service = BiometricService()
            validator = CheckInValidator(geo_service, bio_service)

            post_id = getattr(post, "id", params.get("post_id", ""))

            check_data = CheckInData(
                employee_id=employee_id,
                shift_id=shift_id,
                post_id=post_id,
                latitude=params.get("latitude"),
                longitude=params.get("longitude"),
                accuracy=params.get("gps_accuracy"),
                photo_path=params.get("photo_path") or params.get("captured_photo"),
                device_id=params.get("device_id"),
                device_info=params.get("device_info"),
                ip_address=params.get("ip_address"),
            )

            config = ValidationConfig(
                require_geolocation=params.get("latitude") is not None,
                require_photo=params.get("photo_path") is not None,
                require_face_validation=params.get("photo_path") is not None,
                allowed_radius_meters=getattr(post, "allowed_radius_meters", 100.0) or 100.0,
            )

            post_location = GeoPoint(latitude=post_lat, longitude=post_lon)
            known_device = params.get("known_device_id")

            result = await validator.validate_check_in(
                data=check_data,
                config=config,
                post_location=post_location,
                scheduled_time=scheduled_time,
                known_device_id=known_device,
            )

            return {
                "status": "validated",
                "is_valid": result.is_valid,
                "overall_score": result.overall_score,
                "anomalies": result.anomalies,
                "warnings": result.warnings,
                "details": result.details,
            }
        except Exception as e:
            logger.warning(f"Erro na validacao composta: {e}")
            return {"status": "error", "reason": str(e)}

    async def _validate_clt_rules(
        self,
        employee_id: str,
        shift_date: date,
        start_time: time,
        end_time: Optional[time] = None,
        is_checkout: bool = False,
        actual_start: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Valida regras de jornada CLT.

        Verifica:
        - Intervalo minimo de 11h entre turnos (art. 66 CLT)
        - Jornada maxima diaria de 10h (8h + 2h extra, art. 59 CLT)
        - Alerta de horas extras

        Returns:
            Dict com resultados das validacoes CLT.
        """
        clt_result: Dict[str, Any] = {
            "inter_shift_valid": True,
            "daily_hours_valid": True,
            "overtime_alert": False,
            "warnings": [],
            "details": {},
        }

        shift_repo = ShiftRepository(self.db)

        try:
            # 1. Verificar intervalo entre turnos (11h minimo)
            yesterday = shift_date - timedelta(days=1)
            yesterday_shifts = await shift_repo.get_by_employee_and_date(
                employee_id, yesterday
            )
            if yesterday_shifts:
                last_shift = yesterday_shifts[-1]
                last_end = getattr(last_shift, "actual_end_time", None) or getattr(
                    last_shift, "planned_end_time", None
                )
                if last_end:
                    # Converter para datetime se necessario
                    if isinstance(last_end, time):
                        last_end_dt = datetime.combine(yesterday, last_end)
                    elif isinstance(last_end, datetime):
                        last_end_dt = last_end
                    else:
                        last_end_dt = None

                    if last_end_dt:
                        current_start_dt = datetime.combine(shift_date, start_time)
                        interval = current_start_dt - last_end_dt
                        interval_hours = interval.total_seconds() / 3600

                        clt_result["details"]["inter_shift_hours"] = round(interval_hours, 1)

                        if interval_hours < CLT_MIN_INTER_SHIFT_HOURS:
                            clt_result["inter_shift_valid"] = False
                            clt_result["warnings"].append(
                                f"Intervalo entre turnos insuficiente: "
                                f"{interval_hours:.1f}h (minimo CLT: {CLT_MIN_INTER_SHIFT_HOURS}h)"
                            )

            # 2. Verificar jornada maxima diaria e horas extras
            if is_checkout and actual_start:
                checkout_time = datetime.combine(shift_date, end_time) if end_time else datetime.utcnow()
                worked_delta = checkout_time - actual_start
                worked_hours = worked_delta.total_seconds() / 3600

                clt_result["details"]["worked_hours"] = round(worked_hours, 2)

                if worked_hours > CLT_MAX_DAILY_HOURS:
                    clt_result["daily_hours_valid"] = False
                    clt_result["warnings"].append(
                        f"Jornada diaria excede limite CLT: "
                        f"{worked_hours:.1f}h (maximo: {CLT_MAX_DAILY_HOURS}h)"
                    )
                elif worked_hours > CLT_NORMAL_DAILY_HOURS:
                    overtime = worked_hours - CLT_NORMAL_DAILY_HOURS
                    clt_result["overtime_alert"] = True
                    clt_result["details"]["overtime_hours"] = round(overtime, 2)
                    clt_result["warnings"].append(
                        f"Horas extras: {overtime:.1f}h "
                        f"(jornada normal: {CLT_NORMAL_DAILY_HOURS}h)"
                    )
            else:
                # No check-in, verificar se ja existe turno no dia
                today_shifts = await shift_repo.get_by_employee_and_date(
                    employee_id, shift_date
                )
                completed_hours = 0.0
                for s in today_shifts:
                    actual_h = getattr(s, "actual_hours", None)
                    if actual_h:
                        completed_hours += float(actual_h)

                if completed_hours > 0:
                    clt_result["details"]["hours_already_worked_today"] = round(completed_hours, 2)
                    remaining = CLT_MAX_DAILY_HOURS - completed_hours
                    if remaining <= 0:
                        clt_result["daily_hours_valid"] = False
                        clt_result["warnings"].append(
                            f"Funcionario ja trabalhou {completed_hours:.1f}h hoje. "
                            f"Limite CLT de {CLT_MAX_DAILY_HOURS}h atingido."
                        )
                    elif remaining <= 2:
                        clt_result["overtime_alert"] = True
                        clt_result["warnings"].append(
                            f"Funcionario ja trabalhou {completed_hours:.1f}h hoje. "
                            f"Restam apenas {remaining:.1f}h ate o limite CLT."
                        )

        except Exception as e:
            logger.warning(f"Erro ao validar regras CLT: {e}")
            clt_result["warnings"].append(f"Nao foi possivel validar regras CLT: {e}")

        return clt_result

    # ── Previews ─────────────────────────────────────────────────────────

    async def _create_shift_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criação de turno."""
        params = request.parameters
        scale_id = params.get('scale_id')
        employee_id = params.get('employee_id')
        post_code = params.get('post_code')
        shift_date_str = params.get('shift_date')
        start_time_str = params.get('start_time', '07:00')
        end_time_str = params.get('end_time', '19:00')

        warnings = []
        affected_entities = []
        changes_summary = []

        # Validar escala
        if not scale_id:
            warnings.append("⚠️ ID da escala não informado")
        else:
            changes_summary.append(f"Escala: {scale_id}")

        # Buscar funcionário
        employee = await self._get_employee(employee_id) if employee_id else None
        if employee:
            affected_entities.append({
                "type": "employee",
                "id": str(employee.id),
                "name": employee.nome,
            })
            changes_summary.append(f"Funcionário: {employee.nome}")
        else:
            if employee_id:
                warnings.append(f"⚠️ Funcionário '{employee_id}' não encontrado")
            changes_summary.append("Funcionário: Não alocado (turno vago)")

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_code(post_code) if post_code else None
        if post:
            affected_entities.append({
                "type": "post",
                "id": post.id,
                "name": post.name,
                "code": post.code,
            })
            changes_summary.append(f"Posto: {post.code} - {post.name}")
        elif post_code:
            warnings.append(f"⚠️ Posto '{post_code}' não encontrado")

        # Data e horários
        if shift_date_str:
            changes_summary.append(f"Data: {shift_date_str}")
        else:
            changes_summary.append(f"Data: {date.today().isoformat()} (hoje)")

        changes_summary.append(f"Horário: {start_time_str} - {end_time_str}")

        # Verificar conflitos de turno
        if employee and shift_date_str:
            try:
                shift_dt = date.fromisoformat(shift_date_str)
                shift_repo = ShiftRepository(self.db)
                existing = await shift_repo.get_by_employee_and_date(
                    str(employee.id), shift_dt
                )
                if existing:
                    warnings.append(
                        f"⚠️ Funcionário já possui {len(existing)} turno(s) nesta data"
                    )
            except ValueError:
                warnings.append("⚠️ Data do turno inválida")

        title = "Criar Turno"
        description = "Criar novo turno na escala"
        if employee and post:
            title = f"Criar Turno - {employee.nome} em {post.code}"
            description = f"Turno para {employee.nome} no posto {post.name}"

        required_perm, user_has_perm = self._build_permission_info(request)

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _checkin_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para registro de check-in com validacoes avancadas."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        checkin_time_str = params.get('checkin_time') or params.get('actual_start_time')

        warnings = []
        affected_entities = []
        changes_summary = []

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno por ID ou pelo funcionário no dia atual
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            today_shifts = await shift_repo.get_by_employee_and_date(
                employee_id, date.today()
            )
            if today_shifts:
                # Pegar o turno agendado mais recente
                scheduled = [
                    s for s in today_shifts
                    if s.status == ShiftStatus.SCHEDULED.value
                ]
                shift = scheduled[0] if scheduled else today_shifts[0]

        if not shift:
            warnings.append("Turno nao encontrado")
            title = "Registrar Check-in"
            description = "Turno não encontrado"
        else:
            affected_entities.append({
                "type": "shift",
                "id": shift.id,
                "date": shift.shift_date.isoformat(),
                "status": shift.status,
            })

            changes_summary.append(f"Turno: {shift.id}")
            changes_summary.append(f"Data: {shift.shift_date.isoformat()}")
            changes_summary.append(
                f"Horário previsto: {shift.planned_start_time} - {shift.planned_end_time}"
            )

            if checkin_time_str:
                changes_summary.append(f"Hora check-in: {checkin_time_str}")
            else:
                changes_summary.append(
                    f"Hora check-in: {datetime.now().strftime('%H:%M')} (agora)"
                )

            changes_summary.append(
                f"Status: {shift.status} -> {ShiftStatus.IN_PROGRESS.value}"
            )

            if shift.status == ShiftStatus.IN_PROGRESS.value:
                warnings.append("Check-in ja registrado para este turno")
            elif shift.status == ShiftStatus.COMPLETED.value:
                warnings.append("Turno ja foi concluido")
            elif shift.status == ShiftStatus.MISSED.value:
                warnings.append("Turno marcado como falta")

            # Buscar dados do funcionário
            emp_id_str = str(shift.employee_id) if shift.employee_id else employee_id
            employee = None
            if emp_id_str:
                employee = await self._get_employee(emp_id_str)
                if employee:
                    changes_summary.insert(0, f"Funcionário: {employee.nome}")

            # ── Validacoes avancadas no preview ──────────────────────
            # Buscar posto para validacao GPS
            post = None
            post_id = getattr(shift, "post_id", None)
            if post_id:
                try:
                    post_repo = PostRepository(self.db)
                    post = await post_repo.get_by_id(post_id)
                except Exception as e:
                    logger.warning(f"Erro ao buscar posto para preview checkin: {e}")

            # Validacao GPS
            geo_result = await self._validate_geolocation(params, post) if post else None
            if geo_result:
                if geo_result["status"] == "validated":
                    dist = geo_result.get("distance_meters", "?")
                    changes_summary.append(f"Distancia do posto: {dist:.0f}m")
                    if not geo_result["is_valid"]:
                        warnings.append(f"GPS: {geo_result['message']}")
                    else:
                        changes_summary.append(f"GPS: {geo_result['message']}")
                elif geo_result["status"] == "skipped":
                    changes_summary.append(f"GPS: {geo_result['reason']}")

            # Validacao biometrica
            bio_result = await self._validate_biometric(params, emp_id_str)
            if bio_result:
                if bio_result["status"] == "validated":
                    if bio_result["is_valid"]:
                        changes_summary.append(
                            f"Biometria: Validada ({bio_result['confidence']*100:.0f}% confianca)"
                        )
                    else:
                        warnings.append(f"Biometria: {bio_result['message']}")
                elif bio_result["status"] == "skipped":
                    changes_summary.append(f"Biometria: {bio_result['reason']}")

            # Validacao CLT
            if emp_id_str:
                planned_start = getattr(shift, "planned_start_time", None) or time(7, 0)
                if isinstance(planned_start, str):
                    planned_start = self._parse_time(planned_start)
                clt_result = await self._validate_clt_rules(
                    employee_id=emp_id_str,
                    shift_date=shift.shift_date,
                    start_time=planned_start,
                    is_checkout=False,
                )
                for w in clt_result.get("warnings", []):
                    warnings.append(f"CLT: {w}")
                inter_h = clt_result.get("details", {}).get("inter_shift_hours")
                if inter_h is not None:
                    changes_summary.append(f"Intervalo entre turnos: {inter_h:.1f}h")

            title = f"Registrar Check-in - {shift.shift_date.isoformat()}"
            description = f"Registrar entrada no turno de {shift.shift_date}"

        required_perm, user_has_perm = self._build_permission_info(request)

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _checkout_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para registro de check-out com validacoes avancadas."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        checkout_time_str = params.get('checkout_time') or params.get('actual_end_time')

        warnings = []
        affected_entities = []
        changes_summary = []

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno por ID ou pelo funcionário no dia atual
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            today_shifts = await shift_repo.get_by_employee_and_date(
                employee_id, date.today()
            )
            if today_shifts:
                # Pegar turno em andamento
                in_progress = [
                    s for s in today_shifts
                    if s.status == ShiftStatus.IN_PROGRESS.value
                ]
                shift = in_progress[0] if in_progress else today_shifts[0]

        if not shift:
            warnings.append("Turno nao encontrado")
            title = "Registrar Check-out"
            description = "Turno não encontrado"
        else:
            affected_entities.append({
                "type": "shift",
                "id": shift.id,
                "date": shift.shift_date.isoformat(),
                "status": shift.status,
            })

            changes_summary.append(f"Turno: {shift.id}")
            changes_summary.append(f"Data: {shift.shift_date.isoformat()}")

            if shift.actual_start_time:
                changes_summary.append(
                    f"Check-in registrado: {shift.actual_start_time}"
                )

            if checkout_time_str:
                changes_summary.append(f"Hora check-out: {checkout_time_str}")
            else:
                changes_summary.append(
                    f"Hora check-out: {datetime.now().strftime('%H:%M')} (agora)"
                )

            changes_summary.append(
                f"Status: {shift.status} -> {ShiftStatus.COMPLETED.value}"
            )

            if shift.status == ShiftStatus.COMPLETED.value:
                warnings.append("Turno ja foi concluido")
            elif shift.status == ShiftStatus.SCHEDULED.value:
                warnings.append("Check-in nao foi registrado ainda")

            # Buscar dados do funcionário
            emp_id_str = str(shift.employee_id) if shift.employee_id else employee_id
            employee = None
            if emp_id_str:
                employee = await self._get_employee(emp_id_str)
                if employee:
                    changes_summary.insert(0, f"Funcionário: {employee.nome}")

            # ── Validacoes avancadas no preview de checkout ──────────
            # Buscar posto para validacao GPS
            post = None
            post_id = getattr(shift, "post_id", None)
            if post_id:
                try:
                    post_repo = PostRepository(self.db)
                    post = await post_repo.get_by_id(post_id)
                except Exception as e:
                    logger.warning(f"Erro ao buscar posto para preview checkout: {e}")

            # Validacao GPS
            geo_result = await self._validate_geolocation(params, post) if post else None
            if geo_result:
                if geo_result["status"] == "validated":
                    dist = geo_result.get("distance_meters", "?")
                    changes_summary.append(f"Distancia do posto: {dist:.0f}m")
                    if not geo_result["is_valid"]:
                        warnings.append(f"GPS: {geo_result['message']}")
                    else:
                        changes_summary.append(f"GPS: {geo_result['message']}")
                elif geo_result["status"] == "skipped":
                    changes_summary.append(f"GPS: {geo_result['reason']}")

            # Validacao biometrica
            bio_result = await self._validate_biometric(params, emp_id_str)
            if bio_result:
                if bio_result["status"] == "validated":
                    if bio_result["is_valid"]:
                        changes_summary.append(
                            f"Biometria: Validada ({bio_result['confidence']*100:.0f}% confianca)"
                        )
                    else:
                        warnings.append(f"Biometria: {bio_result['message']}")
                elif bio_result["status"] == "skipped":
                    changes_summary.append(f"Biometria: {bio_result['reason']}")

            # Validacao CLT (checkout - verifica jornada maxima)
            if emp_id_str and shift.actual_start_time:
                planned_end = getattr(shift, "planned_end_time", None) or time(19, 0)
                if isinstance(planned_end, str):
                    planned_end = self._parse_time(planned_end)

                actual_start = shift.actual_start_time
                if isinstance(actual_start, time):
                    actual_start = datetime.combine(shift.shift_date, actual_start)

                clt_result = await self._validate_clt_rules(
                    employee_id=emp_id_str,
                    shift_date=shift.shift_date,
                    start_time=planned_end,
                    end_time=planned_end,
                    is_checkout=True,
                    actual_start=actual_start,
                )
                for w in clt_result.get("warnings", []):
                    warnings.append(f"CLT: {w}")
                worked_h = clt_result.get("details", {}).get("worked_hours")
                if worked_h is not None:
                    changes_summary.append(f"Horas trabalhadas (estimado): {worked_h:.1f}h")
                overtime_h = clt_result.get("details", {}).get("overtime_hours")
                if overtime_h is not None:
                    changes_summary.append(f"Horas extras (estimado): {overtime_h:.1f}h")

            title = f"Registrar Check-out - {shift.shift_date.isoformat()}"
            description = f"Registrar saída do turno de {shift.shift_date}"

        required_perm, user_has_perm = self._build_permission_info(request)

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _mark_absence_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para marcar falta."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        reason = params.get('reason', 'Não informado')
        shift_date_str = params.get('shift_date')

        warnings = []
        affected_entities = []
        changes_summary = []

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            target_date = (
                date.fromisoformat(shift_date_str)
                if shift_date_str
                else date.today()
            )
            shifts = await shift_repo.get_by_employee_and_date(
                employee_id, target_date
            )
            if shifts:
                shift = shifts[0]

        if not shift:
            warnings.append("⚠️ Turno não encontrado")
            title = "Marcar Falta"
            description = "Turno não encontrado"
        else:
            affected_entities.append({
                "type": "shift",
                "id": shift.id,
                "date": shift.shift_date.isoformat(),
                "status": shift.status,
            })

            changes_summary.append(f"Turno: {shift.id}")
            changes_summary.append(f"Data: {shift.shift_date.isoformat()}")
            changes_summary.append(
                f"Status: {shift.status} -> {ShiftStatus.MISSED.value}"
            )
            changes_summary.append(f"Motivo: {reason}")
            changes_summary.append("Necessita substituição: Sim")

            if shift.status == ShiftStatus.MISSED.value:
                warnings.append("⚠️ Turno já está marcado como falta")
            elif shift.status == ShiftStatus.COMPLETED.value:
                warnings.append("⚠️ Turno já foi concluído")

            # Buscar dados do funcionário
            if shift.employee_id:
                employee = await self._get_employee(str(shift.employee_id))
                if employee:
                    changes_summary.insert(0, f"Funcionário: {employee.nome}")

            title = f"Marcar Falta - {shift.shift_date.isoformat()}"
            description = f"Marcar falta no turno de {shift.shift_date}"

        required_perm, user_has_perm = self._build_permission_info(request)

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    # ── Execuções ────────────────────────────────────────────────────────

    async def _execute_create_shift(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criação de turno."""
        params = request.parameters
        scale_id = params.get('scale_id')
        employee_id = params.get('employee_id')
        post_code = params.get('post_code')
        shift_date_str = params.get('shift_date')
        start_time_str = params.get('start_time', '07:00')
        end_time_str = params.get('end_time', '19:00')
        is_night_shift = params.get('is_night_shift', False)
        is_holiday = params.get('is_holiday', False)
        notes = params.get('notes')

        if not scale_id:
            raise ValueError("ID da escala é obrigatório para criar turno")

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_code(post_code) if post_code else None
        if not post and post_code:
            raise ValueError(f"Posto '{post_code}' não encontrado")

        # Parsear data e horários
        shift_dt = (
            date.fromisoformat(shift_date_str) if shift_date_str else date.today()
        )
        start_t = self._parse_time(start_time_str)
        end_t = self._parse_time(end_time_str)

        # Validar funcionário (opcional -- turno pode ser vago)
        employee = None
        if employee_id:
            employee = await self._get_employee(employee_id)
            if not employee:
                raise ValueError(f"Funcionário '{employee_id}' não encontrado")

        # Determinar post_id
        post_id = post.id if post else params.get('post_id')
        if not post_id:
            raise ValueError("Posto é obrigatório para criar turno")

        # Criar turno
        shift_data = ShiftCreate(
            scale_id=scale_id,
            employee_id=str(employee.id) if employee else None,
            post_id=post_id,
            shift_date=shift_dt,
            planned_start_time=start_t,
            planned_end_time=end_t,
            is_night_shift=is_night_shift,
            is_holiday=is_holiday,
            notes=notes,
        )

        shift_repo = ShiftRepository(self.db)
        shift = await shift_repo.create(shift_data)

        logger.info(f"Turno criado via Bartolo: {shift.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Turno criado com sucesso",
            details={
                "shift_id": shift.id,
                "scale_id": scale_id,
                "employee_id": str(employee.id) if employee else None,
                "employee_name": employee.nome if employee else None,
                "post_id": post_id,
                "post_code": post.code if post else None,
                "shift_date": shift_dt.isoformat(),
                "start_time": start_time_str,
                "end_time": end_time_str,
                "status": shift.status,
                "planned_hours": shift.planned_hours,
            },
            affected_entities=[
                {"type": "shift", "id": shift.id},
                {"type": "scale", "id": scale_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_checkin(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa registro de check-in com validacoes avancadas."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        checkin_time_str = params.get('checkin_time') or params.get('actual_start_time')
        notes = params.get('notes')

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            today_shifts = await shift_repo.get_by_employee_and_date(
                employee_id, date.today()
            )
            if today_shifts:
                scheduled = [
                    s for s in today_shifts
                    if s.status == ShiftStatus.SCHEDULED.value
                ]
                shift = scheduled[0] if scheduled else today_shifts[0]

        if not shift:
            raise ValueError("Turno não encontrado")

        if shift.status == ShiftStatus.IN_PROGRESS.value:
            raise ValueError("Check-in já registrado para este turno")
        if shift.status == ShiftStatus.COMPLETED.value:
            raise ValueError("Turno já foi concluído")

        # Parsear horário de check-in
        if checkin_time_str:
            actual_start = self._parse_datetime(checkin_time_str, shift.shift_date)
        else:
            actual_start = datetime.utcnow()

        # ── Validacoes avancadas na execucao ─────────────────────────
        validation_details: Dict[str, Any] = {}
        validation_warnings: List[str] = []

        # Buscar posto para validacoes
        post = None
        post_id = getattr(shift, "post_id", None)
        if post_id:
            try:
                post_repo = PostRepository(self.db)
                post = await post_repo.get_by_id(post_id)
            except Exception as e:
                logger.warning(f"Erro ao buscar posto para checkin: {e}")

        emp_id_str = str(shift.employee_id) if shift.employee_id else employee_id

        # Validacao GPS
        geo_result = await self._validate_geolocation(params, post) if post else None
        if geo_result:
            validation_details["geolocation"] = geo_result
            if geo_result["status"] == "validated" and not geo_result["is_valid"]:
                validation_warnings.append(f"GPS: {geo_result['message']}")

        # Validacao biometrica
        bio_result = await self._validate_biometric(params, emp_id_str)
        if bio_result:
            validation_details["biometric"] = bio_result
            if bio_result["status"] == "validated" and not bio_result["is_valid"]:
                validation_warnings.append(f"Biometria: {bio_result['message']}")

        # Validacao composta (se todos os services disponiveis)
        if post and emp_id_str:
            planned_start = getattr(shift, "planned_start_time", None) or time(7, 0)
            if isinstance(planned_start, str):
                planned_start = self._parse_time(planned_start)
            composite_result = await self._validate_checkin_composite(
                params=params,
                employee_id=emp_id_str,
                shift_id=shift.id,
                post=post,
                scheduled_time=planned_start,
            )
            if composite_result:
                validation_details["composite_validation"] = composite_result

        # Validacao CLT
        if emp_id_str:
            planned_start = getattr(shift, "planned_start_time", None) or time(7, 0)
            if isinstance(planned_start, str):
                planned_start = self._parse_time(planned_start)
            clt_result = await self._validate_clt_rules(
                employee_id=emp_id_str,
                shift_date=shift.shift_date,
                start_time=planned_start,
                is_checkout=False,
            )
            validation_details["clt_validation"] = clt_result
            for w in clt_result.get("warnings", []):
                validation_warnings.append(f"CLT: {w}")

        # Registrar check-in via repository
        updated_shift = await shift_repo.check_in(
            shift_id=shift.id,
            actual_start_time=actual_start,
            notes=notes,
        )

        if not updated_shift:
            raise ValueError("Não foi possível registrar o check-in")

        logger.info(f"Check-in registrado via Bartolo: {updated_shift.id}")

        # Montar detalhes do resultado
        result_details = {
            "shift_id": updated_shift.id,
            "shift_date": updated_shift.shift_date.isoformat(),
            "actual_start_time": actual_start.isoformat(),
            "planned_start_time": str(updated_shift.planned_start_time),
            "status": updated_shift.status,
            "employee_id": str(updated_shift.employee_id) if updated_shift.employee_id else None,
        }

        # Incluir detalhes de validacao
        if validation_details:
            result_details["validations"] = validation_details
        if validation_warnings:
            result_details["validation_warnings"] = validation_warnings

        message = "Check-in registrado com sucesso"
        if validation_warnings:
            message += f" (com {len(validation_warnings)} alerta(s) de validacao)"

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=message,
            details=result_details,
            affected_entities=[
                {"type": "shift", "id": updated_shift.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_checkout(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa registro de check-out com validacoes avancadas."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        checkout_time_str = params.get('checkout_time') or params.get('actual_end_time')
        break_minutes = params.get('break_minutes', 0)
        notes = params.get('notes')

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            today_shifts = await shift_repo.get_by_employee_and_date(
                employee_id, date.today()
            )
            if today_shifts:
                in_progress = [
                    s for s in today_shifts
                    if s.status == ShiftStatus.IN_PROGRESS.value
                ]
                shift = in_progress[0] if in_progress else today_shifts[0]

        if not shift:
            raise ValueError("Turno não encontrado")

        if shift.status == ShiftStatus.COMPLETED.value:
            raise ValueError("Turno já foi concluído")
        if shift.status == ShiftStatus.SCHEDULED.value:
            raise ValueError("Check-in não foi registrado ainda")

        # Parsear horário de check-out
        if checkout_time_str:
            actual_end = self._parse_datetime(checkout_time_str, shift.shift_date)
        else:
            actual_end = datetime.utcnow()

        # ── Validacoes avancadas na execucao do checkout ─────────────
        validation_details: Dict[str, Any] = {}
        validation_warnings: List[str] = []

        # Buscar posto para validacoes
        post = None
        post_id = getattr(shift, "post_id", None)
        if post_id:
            try:
                post_repo = PostRepository(self.db)
                post = await post_repo.get_by_id(post_id)
            except Exception as e:
                logger.warning(f"Erro ao buscar posto para checkout: {e}")

        emp_id_str = str(shift.employee_id) if shift.employee_id else employee_id

        # Validacao GPS
        geo_result = await self._validate_geolocation(params, post) if post else None
        if geo_result:
            validation_details["geolocation"] = geo_result
            if geo_result["status"] == "validated" and not geo_result["is_valid"]:
                validation_warnings.append(f"GPS: {geo_result['message']}")

        # Validacao biometrica
        bio_result = await self._validate_biometric(params, emp_id_str)
        if bio_result:
            validation_details["biometric"] = bio_result
            if bio_result["status"] == "validated" and not bio_result["is_valid"]:
                validation_warnings.append(f"Biometria: {bio_result['message']}")

        # Validacao CLT (checkout - verificar jornada)
        if emp_id_str and shift.actual_start_time:
            actual_start_dt = shift.actual_start_time
            if isinstance(actual_start_dt, time):
                actual_start_dt = datetime.combine(shift.shift_date, actual_start_dt)

            end_t = actual_end.time() if isinstance(actual_end, datetime) else actual_end
            clt_result = await self._validate_clt_rules(
                employee_id=emp_id_str,
                shift_date=shift.shift_date,
                start_time=end_t,
                end_time=end_t,
                is_checkout=True,
                actual_start=actual_start_dt,
            )
            validation_details["clt_validation"] = clt_result
            for w in clt_result.get("warnings", []):
                validation_warnings.append(f"CLT: {w}")

        # Registrar check-out via repository
        updated_shift = await shift_repo.check_out(
            shift_id=shift.id,
            actual_end_time=actual_end,
            actual_break_minutes=break_minutes,
            notes=notes,
        )

        if not updated_shift:
            raise ValueError("Não foi possível registrar o check-out")

        logger.info(f"Check-out registrado via Bartolo: {updated_shift.id}")

        # Montar detalhes do resultado
        result_details = {
            "shift_id": updated_shift.id,
            "shift_date": updated_shift.shift_date.isoformat(),
            "actual_start_time": str(updated_shift.actual_start_time) if updated_shift.actual_start_time else None,
            "actual_end_time": actual_end.isoformat(),
            "actual_hours": updated_shift.actual_hours,
            "overtime_hours": updated_shift.overtime_hours,
            "break_minutes": break_minutes,
            "status": updated_shift.status,
            "employee_id": str(updated_shift.employee_id) if updated_shift.employee_id else None,
        }

        # Incluir detalhes de validacao
        if validation_details:
            result_details["validations"] = validation_details
        if validation_warnings:
            result_details["validation_warnings"] = validation_warnings

        message = "Check-out registrado com sucesso"
        if validation_warnings:
            message += f" (com {len(validation_warnings)} alerta(s) de validacao)"

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=message,
            details=result_details,
            affected_entities=[
                {"type": "shift", "id": updated_shift.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_mark_absence(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa marcação de falta."""
        params = request.parameters
        shift_id = params.get('shift_id')
        employee_id = params.get('employee_id')
        shift_date_str = params.get('shift_date')
        reason = params.get('reason')

        shift_repo = ShiftRepository(self.db)
        shift = None

        # Buscar turno
        if shift_id:
            shift = await shift_repo.get_by_id(shift_id)
        elif employee_id:
            target_date = (
                date.fromisoformat(shift_date_str)
                if shift_date_str
                else date.today()
            )
            shifts = await shift_repo.get_by_employee_and_date(
                employee_id, target_date
            )
            if shifts:
                shift = shifts[0]

        if not shift:
            raise ValueError("Turno não encontrado")

        if shift.status == ShiftStatus.MISSED.value:
            raise ValueError("Turno já está marcado como falta")
        if shift.status == ShiftStatus.COMPLETED.value:
            raise ValueError("Turno já foi concluído, não pode ser marcado como falta")

        # Marcar como falta via repository
        updated_shift = await shift_repo.mark_as_missed(
            shift_id=shift.id,
            reason=reason,
        )

        if not updated_shift:
            raise ValueError("Não foi possível marcar a falta")

        logger.info(f"Falta registrada via Bartolo: {updated_shift.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Falta registrada com sucesso",
            details={
                "shift_id": updated_shift.id,
                "shift_date": updated_shift.shift_date.isoformat(),
                "status": updated_shift.status,
                "needs_substitution": updated_shift.needs_substitution,
                "reason": reason,
                "employee_id": str(updated_shift.employee_id) if updated_shift.employee_id else None,
            },
            affected_entities=[
                {"type": "shift", "id": updated_shift.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
