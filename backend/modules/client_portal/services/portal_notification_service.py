"""
Servico de Notificacoes do Portal do Cliente.

Envia notificacoes push e email para clientes do portal em eventos como:
- Kit mensal pronto
- Chamado respondido pela equipe interna
- Certidao prestes a vencer (7 dias)
- Novo documento disponivel
"""

import logging
import smtplib
import uuid as _uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# ========================================================================
# Push Service — importacao graceful
# ========================================================================
try:
    from modules.notifications.push.services.push_service import PushService

    _PUSH_AVAILABLE = True
except Exception as _push_err:
    logger.warning("PushService nao disponivel: %s", _push_err)
    PushService = None  # type: ignore[assignment,misc]
    _PUSH_AVAILABLE = False


# ========================================================================
# Settings — importacao graceful
# ========================================================================
try:
    from core.config import settings as _settings

    SMTP_HOST = getattr(_settings, "smtp_host", None)
    SMTP_PORT = int(getattr(_settings, "smtp_port", 587))
    SMTP_USER = getattr(_settings, "smtp_user", None)
    SMTP_PASSWORD = getattr(_settings, "smtp_password", None)
    FROM_EMAIL = getattr(_settings, "from_email", None) or SMTP_USER
except Exception:
    import os

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL") or SMTP_USER

# Portal push notifications usam um tenant fixo (UUID zero) para isolar
# os dispositivos do portal dos dispositivos internos do ERP.
PORTAL_TENANT_ID = _uuid.UUID("00000000-0000-0000-0000-000000000001")


# ========================================================================
# Email helper (sincrono — chamado em thread para nao bloquear async)
# ========================================================================


def _send_email_sync(to_email: str, subject: str, body_html: str, body_text: str) -> bool:
    """Envia email via SMTP sincrono. Retorna True se enviado com sucesso."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        logger.debug("SMTP nao configurado — email nao enviado para %s", to_email)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL or SMTP_USER
        msg["To"] = to_email
        msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            if SMTP_PORT != 465:
                server.starttls()
                server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL or SMTP_USER, [to_email], msg.as_string())

        logger.info("Email enviado para %s — assunto: %s", to_email, subject)
        return True

    except Exception as exc:
        logger.warning("Falha ao enviar email para %s: %s", to_email, exc)
        return False


# ========================================================================
# Notification preferences helper
# ========================================================================


async def _get_client_email_and_prefs(db: AsyncSession, client_id: str) -> tuple[str | None, dict]:
    """Busca email de contato e preferencias de notificacao do cliente."""
    from modules.people_management.ged.models.client import GedClient

    result = await db.execute(
        select(GedClient.contact_email, GedClient.portal_username).where(GedClient.id == client_id)
    )
    row = result.first()
    contact_email = row[0] if row else None
    return contact_email, {}


# ========================================================================
# Push helper — envia para todos os dispositivos registrados do cliente
# ========================================================================


def _send_push_to_client(db_sync, client_id: str, title: str, body: str, data: dict | None = None) -> bool:
    """Envia push para todos os devices ativos do cliente (sincrono)."""
    if not _PUSH_AVAILABLE or PushService is None:
        return False

    try:
        # Dispositivos do portal ficam com user_id = client_id (string cast para UUID)
        import uuid as _u

        try:
            user_uuid = _u.UUID(str(client_id))
        except ValueError:
            logger.warning("client_id invalido para push: %s", client_id)
            return False

        svc = PushService(db=db_sync, tenant_id=PORTAL_TENANT_ID)
        notifications = svc.send_to_user(
            user_id=user_uuid,
            title=title,
            body=body,
            data_payload=data or {},
            source_type="portal",
        )
        logger.info("Push enviado para client_id=%s — %d notificacoes", client_id, len(notifications))
        return len(notifications) > 0
    except Exception as exc:
        logger.warning("Falha ao enviar push para client_id=%s: %s", client_id, exc)
        return False


# ========================================================================
# Portal Notification Service
# ========================================================================


class PortalNotificationService:
    """Servico de notificacoes do portal do cliente.

    Coordena push (via PushService) e email (via smtplib) para clientes
    do portal quando eventos relevantes ocorrem.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # notify_kit_ready
    # ------------------------------------------------------------------

    async def notify_kit_ready(
        self,
        client_id: str,
        kit_id: str,
        reference_month: str,
    ) -> None:
        """Notifica cliente quando kit mensal fica pronto.

        Args:
            client_id: UUID do cliente GED.
            kit_id: UUID do kit documental.
            reference_month: Mes de referencia (ex: '2026-03-01').
        """
        title = "Kit Documental Pronto"

        contact_email, _ = await _get_client_email_and_prefs(self.db, client_id)

        if contact_email:
            body_html = f"""
<html><body>
<h2>Kit Documental Disponivel</h2>
<p>Seu kit de documentos de <strong>{reference_month}</strong> esta pronto para download no portal.</p>
<p>
  <a href="https://erp.conectamais.pro/area-cliente/kits/{kit_id}"
     style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;
            text-decoration:none;font-weight:600;display:inline-block;">
    Acessar Kit
  </a>
</p>
<p style="color:#6b7280;font-size:0.85em;margin-top:24px;">
  Conecta PRO - Gestao de Documentos
</p>
</body></html>"""
            body_text = (
                f"Kit Documental Disponivel\n\n"
                f"Seu kit de documentos de {reference_month} esta pronto para download.\n"
                f"Acesse: https://erp.conectamais.pro/area-cliente/kits/{kit_id}"
            )
            _send_email_sync(contact_email, title, body_html, body_text)

        logger.info(
            "notify_kit_ready: client_id=%s kit_id=%s mes=%s",
            client_id,
            kit_id,
            reference_month,
        )

    # ------------------------------------------------------------------
    # notify_ticket_answered
    # ------------------------------------------------------------------

    async def notify_ticket_answered(
        self,
        client_id: str,
        ticket_id: str,
        subject: str,
    ) -> None:
        """Notifica cliente quando chamado recebe resposta da equipe.

        Args:
            client_id: UUID do cliente GED.
            ticket_id: UUID do ticket.
            subject: Assunto do ticket.
        """
        title = "Chamado Respondido"

        contact_email, _ = await _get_client_email_and_prefs(self.db, client_id)

        if contact_email:
            body_html = f"""
<html><body>
<h2>Novo resposta em seu Chamado</h2>
<p>Seu chamado <strong>"{subject}"</strong> recebeu uma nova resposta da nossa equipe.</p>
<p>
  <a href="https://erp.conectamais.pro/area-cliente/chamados/{ticket_id}"
     style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;
            text-decoration:none;font-weight:600;display:inline-block;">
    Ver Resposta
  </a>
</p>
<p style="color:#6b7280;font-size:0.85em;margin-top:24px;">
  Conecta PRO - Suporte ao Cliente
</p>
</body></html>"""
            body_text = (
                f"Chamado Respondido\n\n"
                f"Seu chamado '{subject}' recebeu uma nova resposta.\n"
                f"Acesse: https://erp.conectamais.pro/area-cliente/chamados/{ticket_id}"
            )
            _send_email_sync(contact_email, title, body_html, body_text)

        logger.info(
            "notify_ticket_answered: client_id=%s ticket_id=%s subject=%s",
            client_id,
            ticket_id,
            subject,
        )

    # ------------------------------------------------------------------
    # notify_certificate_expiring
    # ------------------------------------------------------------------

    async def notify_certificate_expiring(
        self,
        client_id: str,
        cert_name: str,
        expires_at: str,
    ) -> None:
        """Notifica cliente sobre certidao vencendo em 7 dias.

        Args:
            client_id: UUID do cliente GED.
            cert_name: Nome do documento/certidao.
            expires_at: Data de vencimento (ISO string).
        """
        title = "Certidao Vencendo"

        contact_email, _ = await _get_client_email_and_prefs(self.db, client_id)

        if contact_email:
            body_html = f"""
<html><body>
<h2>Aviso: Certidao Prestes a Vencer</h2>
<p>A certidao <strong>"{cert_name}"</strong> vence em <strong>{expires_at}</strong>.</p>
<p>Por favor, providencie a renovacao o quanto antes para evitar irregularidades.</p>
<p>
  <a href="https://erp.conectamais.pro/area-cliente/kits"
     style="background:#dc2626;color:#fff;padding:10px 20px;border-radius:6px;
            text-decoration:none;font-weight:600;display:inline-block;">
    Acessar Portal
  </a>
</p>
<p style="color:#6b7280;font-size:0.85em;margin-top:24px;">
  Conecta PRO - Gestao Documental
</p>
</body></html>"""
            body_text = (
                f"Certidao Vencendo\n\n"
                f"A certidao '{cert_name}' vence em {expires_at}.\n"
                f"Providencie a renovacao: https://erp.conectamais.pro/area-cliente/kits"
            )
            _send_email_sync(contact_email, title, body_html, body_text)

        logger.info(
            "notify_certificate_expiring: client_id=%s cert=%s expires=%s",
            client_id,
            cert_name,
            expires_at,
        )

    # ------------------------------------------------------------------
    # notify_document_available
    # ------------------------------------------------------------------

    async def notify_document_available(
        self,
        client_id: str,
        document_name: str,
        kit_id: str,
    ) -> None:
        """Notifica cliente quando novo documento fica disponivel no kit.

        Args:
            client_id: UUID do cliente GED.
            document_name: Nome do documento.
            kit_id: UUID do kit que contem o documento.
        """
        title = "Novo Documento Disponivel"

        contact_email, _ = await _get_client_email_and_prefs(self.db, client_id)

        if contact_email:
            body_html = f"""
<html><body>
<h2>Novo Documento Disponivel</h2>
<p>O documento <strong>"{document_name}"</strong> foi adicionado ao seu kit e esta disponivel
para download.</p>
<p>
  <a href="https://erp.conectamais.pro/area-cliente/kits/{kit_id}"
     style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;
            text-decoration:none;font-weight:600;display:inline-block;">
    Ver Documento
  </a>
</p>
<p style="color:#6b7280;font-size:0.85em;margin-top:24px;">
  Conecta PRO - Gestao Documental
</p>
</body></html>"""
            body_text = (
                f"Novo Documento Disponivel\n\n"
                f"O documento '{document_name}' esta disponivel para download.\n"
                f"Acesse: https://erp.conectamais.pro/area-cliente/kits/{kit_id}"
            )
            _send_email_sync(contact_email, title, body_html, body_text)

        logger.info(
            "notify_document_available: client_id=%s doc=%s kit_id=%s",
            client_id,
            document_name,
            kit_id,
        )
