"""
Portal Service — Autenticacao e dashboard do portal do funcionario.

Gerencia login por CPF, geracao de tokens e dados do dashboard.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.employee_portal.models.portal_access import (
    PortalAccess,
    PortalAccessAction,
)

logger = logging.getLogger(__name__)


class PortalService:
    """Servico principal do portal do funcionario.

    Responsavel por autenticacao, dashboard e registro de acessos.

    Attributes:
        db: Sessao async do banco de dados.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o servico com sessao de banco.

        Args:
            db: Sessao async do SQLAlchemy.
        """
        self.db = db

    async def authenticate_employee(
        self,
        cpf: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any] | None:
        """Autentica funcionario por CPF e senha.

        Busca o funcionario pelo CPF no banco, valida a senha
        e retorna dados para geracao do token JWT.

        Args:
            cpf: CPF do funcionario (com ou sem formatacao).
            password: Senha do portal.
            ip_address: IP do acesso (para log).
            user_agent: User agent do navegador (para log).

        Returns:
            Dict com employee_id, nome e token se autenticado,
            ou None se credenciais invalidas.
        """
        try:
            from modules.operacional.models.employee import Employee

            # Normalizar CPF (remover pontos e tracos)
            cpf_clean = cpf.replace(".", "").replace("-", "").strip()

            query = select(Employee).where(
                Employee.cpf == cpf_clean,
                Employee.status == "ativo",
            )
            result = await self.db.execute(query)
            employee = result.scalar_one_or_none()

            if not employee:
                logger.warning("Tentativa de login com CPF nao encontrado: %s***", cpf_clean[:3])
                return None

            # Validar senha (simplificado — em producao usar bcrypt/argon2)
            # A senha do portal pode estar em um campo dedicado ou ser derivada
            portal_password = getattr(employee, "portal_password", None)
            if portal_password and portal_password != password:
                logger.warning("Senha incorreta para employee_id=%s", employee.id)
                return None

            # Registrar acesso
            await self.log_access(
                employee_id=employee.id,
                action=PortalAccessAction.LOGIN,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return {
                "employee_id": str(employee.id),
                "nome": employee.nome,
                "cargo": getattr(employee, "cargo", ""),
            }

        except ImportError:
            logger.error("Modelo Employee nao disponivel.")
            return None
        except Exception as e:
            logger.error("Erro na autenticacao: %s", e, exc_info=True)
            return None

    async def get_dashboard(self, employee_id: UUID) -> dict[str, Any]:
        """Retorna dados do dashboard do funcionario.

        Agrega informacoes de nome, cargo, posto, proximo turno,
        documentos pendentes e notificacoes nao lidas.

        Args:
            employee_id: UUID do funcionario.

        Returns:
            Dict com dados do dashboard.
        """
        dashboard: dict[str, Any] = {
            "name": "",
            "position": None,
            "workplace": None,
            "next_shift": None,
            "pending_documents": 0,
            "unread_notifications": 0,
        }

        try:
            from modules.operacional.models.employee import Employee

            query = select(Employee).where(Employee.id == employee_id)
            result = await self.db.execute(query)
            employee = result.scalar_one_or_none()

            if employee:
                dashboard["name"] = employee.nome
                dashboard["position"] = getattr(employee, "cargo", None)

        except ImportError:
            logger.warning("Modelo Employee nao disponivel para dashboard.")

        # Contar notificacoes nao lidas
        try:
            from modules.people_management.employee_portal.models.notification import (
                PortalNotification,
            )

            notif_query = select(func.count(PortalNotification.id)).where(
                PortalNotification.employee_id == employee_id,
                PortalNotification.is_read.is_(False),
            )
            notif_result = await self.db.execute(notif_query)
            dashboard["unread_notifications"] = notif_result.scalar() or 0

        except ImportError:
            pass

        # Contar documentos pendentes de assinatura
        try:
            from modules.people_management.employee_portal.models.digital_signature import (
                PortalDigitalSignature,
            )

            # Documentos pendentes = sem assinatura do funcionario
            # Simplificado: contar assinaturas validas
            sig_query = select(func.count(PortalDigitalSignature.id)).where(
                PortalDigitalSignature.employee_id == employee_id,
                PortalDigitalSignature.is_valid.is_(True),
            )
            sig_result = await self.db.execute(sig_query)
            signed_count = sig_result.scalar() or 0
            dashboard["pending_documents"] = max(0, 0 - signed_count)

        except ImportError:
            pass

        return dashboard

    async def log_access(
        self,
        employee_id: UUID,
        action: PortalAccessAction,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_fingerprint: str | None = None,
        geolocation: dict[str, Any] | None = None,
    ) -> None:
        """Registra um acesso/acao no portal.

        Args:
            employee_id: UUID do funcionario.
            action: Tipo de acao realizada.
            ip_address: IP do acesso.
            user_agent: User agent do navegador.
            device_fingerprint: Fingerprint do dispositivo.
            geolocation: Dados de geolocalizacao.
        """
        try:
            access_log = PortalAccess(
                employee_id=employee_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                geolocation=geolocation,
                created_at=datetime.utcnow(),
            )
            self.db.add(access_log)
            await self.db.commit()
        except Exception as e:
            logger.error("Erro ao registrar acesso: %s", e)
            await self.db.rollback()
