"""
Model para registro de acessos ao Portal do Funcionario.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class PortalAccessAction(enum.StrEnum):
    """Acoes possiveis no portal do funcionario."""

    LOGIN = "login"
    LOGOUT = "logout"
    VIEW_PAYSLIP = "view_payslip"
    VIEW_SCHEDULE = "view_schedule"
    SIGN_DOCUMENT = "sign_document"
    UPDATE_DATA = "update_data"
    VIEW_WARNING = "view_warning"


class PortalAccess(Base):
    """Registro de log de acesso ao portal do funcionario.

    Attributes:
        id: Identificador unico do registro.
        employee_id: FK para o funcionario.
        action: Tipo de acao realizada.
        ip_address: Endereco IP do acesso.
        user_agent: User agent do navegador.
        device_fingerprint: Fingerprint do dispositivo.
        geolocation: Dados de geolocalizacao em JSON.
        created_at: Data/hora do acesso.
    """

    __tablename__ = "portal_access_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(
        Enum(PortalAccessAction, name="portal_access_action_enum"),
        nullable=False,
    )
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    geolocation = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
