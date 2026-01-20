"""Modelo TimeEntry - Registro de Ponto Eletrônico.

Conformidade com Portaria 671 do MTE (Ministério do Trabalho).
"""

import uuid
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Time,
    Integer,
    String,
    Text,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from .work_schedule import WorkSchedule
    from .time_justification import TimeJustification


class EntryType(str, Enum):
    """Tipo de registro de ponto."""

    ENTRADA = "entrada"
    SAIDA = "saida"
    INICIO_INTERVALO = "inicio_intervalo"
    FIM_INTERVALO = "fim_intervalo"
    ENTRADA_EXTRA = "entrada_extra"
    SAIDA_EXTRA = "saida_extra"


class RegistrationMethod(str, Enum):
    """Método de registro do ponto."""

    BIOMETRIA_DIGITAL = "biometria_digital"
    BIOMETRIA_FACIAL = "biometria_facial"
    CARTAO_RFID = "cartao_rfid"
    CARTAO_PROXIMIDADE = "cartao_proximidade"
    APP_MOBILE = "app_mobile"
    APP_WEB = "app_web"
    MANUAL = "manual"
    REP = "rep"  # Registrador Eletrônico de Ponto
    GEOLOCALIZACAO = "geolocalizacao"
    QR_CODE = "qr_code"
    PIN = "pin"


class EntryStatus(str, Enum):
    """Status do registro de ponto."""

    CONFIRMADO = "confirmado"
    PENDENTE = "pendente"
    REJEITADO = "rejeitado"
    JUSTIFICADO = "justificado"
    AJUSTADO = "ajustado"
    DUPLICADO = "duplicado"
    INVALIDO = "invalido"


class AnomalyType(str, Enum):
    """Tipo de anomalia detectada."""

    ATRASO = "atraso"
    SAIDA_ANTECIPADA = "saida_antecipada"
    FALTA_ENTRADA = "falta_entrada"
    FALTA_SAIDA = "falta_saida"
    INTERVALO_CURTO = "intervalo_curto"
    INTERVALO_LONGO = "intervalo_longo"
    HORA_EXTRA_NAO_AUTORIZADA = "hora_extra_nao_autorizada"
    LOCALIZACAO_INVALIDA = "localizacao_invalida"
    BIOMETRIA_FALHA = "biometria_falha"
    HORARIO_INCOMUM = "horario_incomum"
    MULTIPLAS_MARCACOES = "multiplas_marcacoes"
    SEM_ANOMALIA = "sem_anomalia"


class TimeEntry(Base):
    """Modelo de Registro de Ponto Eletrônico.

    Cada registro representa uma marcação de ponto do funcionário.
    Segue as normas da Portaria 671 do MTE.
    """

    __tablename__ = "time_entries"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    # Funcionário
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    employee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    employee_registration: Mapped[Optional[str]] = mapped_column(String(50))
    employee_cpf: Mapped[Optional[str]] = mapped_column(String(14))
    department_id: Mapped[Optional[str]] = mapped_column(String(50))
    department_name: Mapped[Optional[str]] = mapped_column(String(100))
    position_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Jornada
    work_schedule_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Registro
    entry_type: Mapped[EntryType] = mapped_column(
        String(30), default=EntryType.ENTRADA
    )
    registration_method: Mapped[RegistrationMethod] = mapped_column(
        String(30), default=RegistrationMethod.BIOMETRIA_DIGITAL
    )
    status: Mapped[EntryStatus] = mapped_column(
        String(20), default=EntryStatus.CONFIRMADO
    )

    # Data e hora
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    entry_time: Mapped[time] = mapped_column(Time, nullable=False)
    entry_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Horário esperado (da jornada)
    expected_time: Mapped[Optional[time]] = mapped_column(Time)
    tolerance_minutes: Mapped[int] = mapped_column(Integer, default=10)

    # Diferença calculada
    difference_minutes: Mapped[int] = mapped_column(Integer, default=0)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    is_early: Mapped[bool] = mapped_column(Boolean, default=False)
    is_overtime: Mapped[bool] = mapped_column(Boolean, default=False)

    # Geolocalização
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    accuracy_meters: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    address: Mapped[Optional[str]] = mapped_column(String(500))
    is_within_allowed_area: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_area_id: Mapped[Optional[str]] = mapped_column(String(50))
    distance_from_work_meters: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Dispositivo
    device_id: Mapped[Optional[str]] = mapped_column(String(100))
    device_name: Mapped[Optional[str]] = mapped_column(String(200))
    device_type: Mapped[Optional[str]] = mapped_column(String(50))
    device_ip: Mapped[Optional[str]] = mapped_column(String(50))
    device_mac: Mapped[Optional[str]] = mapped_column(String(20))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    app_version: Mapped[Optional[str]] = mapped_column(String(20))

    # Biometria
    biometric_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    biometric_template_id: Mapped[Optional[str]] = mapped_column(String(100))
    face_match_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    liveness_check: Mapped[bool] = mapped_column(Boolean, default=True)

    # REP - Registrador Eletrônico de Ponto
    rep_id: Mapped[Optional[str]] = mapped_column(String(50))
    rep_serial: Mapped[Optional[str]] = mapped_column(String(50))
    nsr: Mapped[Optional[int]] = mapped_column(Integer)  # Número Sequencial do Registro
    pis_pasep: Mapped[Optional[str]] = mapped_column(String(15))

    # Anomalia
    anomaly_type: Mapped[AnomalyType] = mapped_column(
        String(40), default=AnomalyType.SEM_ANOMALIA
    )
    anomaly_description: Mapped[Optional[str]] = mapped_column(Text)
    anomaly_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    anomaly_resolved_by_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Justificativa (se houver)
    justification_id: Mapped[Optional[str]] = mapped_column(String(50))
    has_justification: Mapped[bool] = mapped_column(Boolean, default=False)

    # Ajuste manual
    is_manual_entry: Mapped[bool] = mapped_column(Boolean, default=False)
    original_time: Mapped[Optional[time]] = mapped_column(Time)
    adjusted_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    adjusted_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    adjusted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    adjustment_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Aprovação (para ajustes manuais)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    approved_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Noturno
    is_night_shift: Mapped[bool] = mapped_column(Boolean, default=False)
    night_hours_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # Condomínio/Local
    condominium_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    work_location_id: Mapped[Optional[str]] = mapped_column(String(50))
    work_location_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Observações e metadados
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Controle
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Índices compostos
    __table_args__ = (
        Index("ix_time_entries_employee_date", "employee_id", "entry_date"),
        Index("ix_time_entries_date_type", "entry_date", "entry_type"),
        Index("ix_time_entries_condominium_date", "condominium_id", "entry_date"),
    )

    def __init__(self, **kwargs) -> None:
        """Inicializa o registro de ponto."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()
        if self.entry_datetime and not self.entry_date:
            self.entry_date = self.entry_datetime.date()
        if self.entry_datetime and not self.entry_time:
            self.entry_time = self.entry_datetime.time()

    def _generate_code(self) -> str:
        """Gera código único do registro."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:18]
        return f"REG-{timestamp}"

    def calculate_difference(self) -> int:
        """Calcula diferença em minutos do horário esperado.

        Returns:
            int: Diferença em minutos (positivo = atrasado, negativo = adiantado)
        """
        if not self.expected_time:
            return 0

        entry_dt = datetime.combine(self.entry_date, self.entry_time)
        expected_dt = datetime.combine(self.entry_date, self.expected_time)

        diff = entry_dt - expected_dt
        diff_minutes = int(diff.total_seconds() / 60)

        self.difference_minutes = diff_minutes

        # Determina se é atraso, adiantado ou hora extra
        if self.entry_type in [EntryType.ENTRADA, EntryType.FIM_INTERVALO]:
            self.is_late = diff_minutes > self.tolerance_minutes
            self.is_early = diff_minutes < -self.tolerance_minutes
        elif self.entry_type in [EntryType.SAIDA, EntryType.INICIO_INTERVALO]:
            self.is_early = diff_minutes < -self.tolerance_minutes
            self.is_overtime = diff_minutes > self.tolerance_minutes

        return diff_minutes

    def detect_anomaly(self) -> AnomalyType:
        """Detecta anomalias no registro.

        Returns:
            AnomalyType: Tipo de anomalia detectada
        """
        # Atraso
        if self.is_late and self.entry_type == EntryType.ENTRADA:
            self.anomaly_type = AnomalyType.ATRASO
            self.anomaly_description = (
                f"Atraso de {self.difference_minutes} minutos"
            )
            return self.anomaly_type

        # Saída antecipada
        if self.is_early and self.entry_type == EntryType.SAIDA:
            self.anomaly_type = AnomalyType.SAIDA_ANTECIPADA
            self.anomaly_description = (
                f"Saída {abs(self.difference_minutes)} minutos antes"
            )
            return self.anomaly_type

        # Localização inválida
        if not self.is_within_allowed_area:
            self.anomaly_type = AnomalyType.LOCALIZACAO_INVALIDA
            self.anomaly_description = "Registro fora da área permitida"
            return self.anomaly_type

        # Falha biométrica
        if self.biometric_score and self.biometric_score < 70:
            self.anomaly_type = AnomalyType.BIOMETRIA_FALHA
            self.anomaly_description = (
                f"Score biométrico baixo: {self.biometric_score}"
            )
            return self.anomaly_type

        self.anomaly_type = AnomalyType.SEM_ANOMALIA
        return self.anomaly_type

    def mark_as_manual(
        self,
        adjusted_by_id: str,
        adjusted_by_name: str,
        reason: str,
    ) -> None:
        """Marca como registro manual/ajustado.

        Args:
            adjusted_by_id: ID de quem ajustou
            adjusted_by_name: Nome de quem ajustou
            reason: Motivo do ajuste
        """
        self.is_manual_entry = True
        self.original_time = self.entry_time
        self.adjusted_by_id = adjusted_by_id
        self.adjusted_by_name = adjusted_by_name
        self.adjusted_at = datetime.utcnow()
        self.adjustment_reason = reason
        self.status = EntryStatus.AJUSTADO
        self.requires_approval = True

    def approve(
        self,
        approved_by_id: str,
        approved_by_name: str,
        notes: str = None,
    ) -> None:
        """Aprova o registro (para ajustes manuais).

        Args:
            approved_by_id: ID do aprovador
            approved_by_name: Nome do aprovador
            notes: Observações da aprovação
        """
        self.status = EntryStatus.CONFIRMADO
        self.approved_by_id = approved_by_id
        self.approved_by_name = approved_by_name
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        self.requires_approval = False

    def reject(
        self,
        rejected_by_id: str,
        rejected_by_name: str,
        reason: str,
    ) -> None:
        """Rejeita o registro.

        Args:
            rejected_by_id: ID de quem rejeitou
            rejected_by_name: Nome de quem rejeitou
            reason: Motivo da rejeição
        """
        self.status = EntryStatus.REJEITADO
        self.approved_by_id = rejected_by_id
        self.approved_by_name = rejected_by_name
        self.approved_at = datetime.utcnow()
        self.approval_notes = reason
        self.requires_approval = False

    def link_justification(self, justification_id: str) -> None:
        """Vincula uma justificativa ao registro.

        Args:
            justification_id: ID da justificativa
        """
        self.justification_id = justification_id
        self.has_justification = True
        self.status = EntryStatus.JUSTIFICADO
        self.anomaly_resolved = True
        self.anomaly_resolved_at = datetime.utcnow()

    def resolve_anomaly(self, resolved_by_id: str) -> None:
        """Marca anomalia como resolvida.

        Args:
            resolved_by_id: ID de quem resolveu
        """
        self.anomaly_resolved = True
        self.anomaly_resolved_at = datetime.utcnow()
        self.anomaly_resolved_by_id = resolved_by_id

    def calculate_night_hours(self) -> int:
        """Calcula minutos em horário noturno (22h às 05h).

        Returns:
            int: Minutos em horário noturno
        """
        night_start = time(22, 0)
        night_end = time(5, 0)
        entry = self.entry_time

        # Verifica se está no período noturno
        if entry >= night_start or entry <= night_end:
            self.is_night_shift = True

            # Calcula minutos noturnos (simplificado)
            if entry >= night_start:
                # Entre 22h e meia-noite
                midnight = time(23, 59, 59)
                diff = datetime.combine(date.today(), midnight) - datetime.combine(
                    date.today(), entry
                )
                self.night_hours_minutes = int(diff.total_seconds() / 60)
            else:
                # Entre meia-noite e 5h
                diff = datetime.combine(date.today(), entry) - datetime.combine(
                    date.today(), time(0, 0)
                )
                self.night_hours_minutes = int(diff.total_seconds() / 60)

        return self.night_hours_minutes

    def soft_delete(self) -> None:
        """Soft delete do registro."""
        self.is_deleted = True
        self.status = EntryStatus.INVALIDO

    @property
    def is_pending_approval(self) -> bool:
        """Verifica se está pendente de aprovação."""
        return self.requires_approval and self.status not in [
            EntryStatus.CONFIRMADO,
            EntryStatus.REJEITADO,
        ]

    @property
    def has_anomaly(self) -> bool:
        """Verifica se tem anomalia não resolvida."""
        return (
            self.anomaly_type != AnomalyType.SEM_ANOMALIA
            and not self.anomaly_resolved
        )

    @property
    def is_valid_biometric(self) -> bool:
        """Verifica se biometria é válida (score >= 80)."""
        if not self.biometric_score:
            return True  # Não usa biometria
        return self.biometric_score >= 80

    @property
    def time_formatted(self) -> str:
        """Retorna horário formatado."""
        return self.entry_time.strftime("%H:%M")

    @property
    def datetime_formatted(self) -> str:
        """Retorna data/hora formatada."""
        return self.entry_datetime.strftime("%d/%m/%Y %H:%M")

    @property
    def entry_type_display(self) -> str:
        """Retorna tipo de registro para exibição."""
        display_map = {
            EntryType.ENTRADA: "Entrada",
            EntryType.SAIDA: "Saída",
            EntryType.INICIO_INTERVALO: "Início Intervalo",
            EntryType.FIM_INTERVALO: "Fim Intervalo",
            EntryType.ENTRADA_EXTRA: "Entrada Extra",
            EntryType.SAIDA_EXTRA: "Saída Extra",
        }
        return display_map.get(self.entry_type, self.entry_type.value)

    def __repr__(self) -> str:
        """Representação do objeto."""
        return (
            f"<TimeEntry {self.code}: {self.employee_name} "
            f"{self.entry_type.value} {self.datetime_formatted}>"
        )
