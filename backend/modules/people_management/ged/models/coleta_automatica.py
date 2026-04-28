"""Models D4 — Coleta Automatica config + logs."""

import uuid

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class GedColetaConfig(Base):
    """Singleton (id=1): configuração da coleta automática mensal."""

    __tablename__ = "ged_coleta_config"
    __table_args__ = (CheckConstraint("id = 1", name="ged_coleta_config_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cron_expr: Mapped[str] = mapped_column(String(50), nullable=False, default="0 6 21 * *")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="America/Manaus")
    last_run: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)


class GedColetaLog(Base):
    """Histórico de execuções da coleta automática."""

    __tablename__ = "ged_coleta_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    run_type: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sync_novos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    kits_assembled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    onvio_matched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    erros: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certidoes_atualizadas: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0", default=0)
    alertas_disparados: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0", default=0)
