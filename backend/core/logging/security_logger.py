"""
Security Logger - Logs especificos para eventos de seguranca.

Conecta PRO - Sistema de logging para auditoria de seguranca.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from core.logging import logger


class SecurityEventType(StrEnum):
    """Tipos de eventos de seguranca."""

    # Autenticacao
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"  # noqa: S105
    TOKEN_EXPIRED = "token_expired"  # noqa: S105
    TOKEN_INVALID = "token_invalid"  # noqa: S105

    # Autorizacao
    ACCESS_DENIED = "access_denied"
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGED = "role_changed"

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_WARNING = "rate_limit_warning"

    # Atividades suspeitas
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"

    # Dados
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"

    # Configuracao
    CONFIG_CHANGED = "config_changed"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    PASSWORD_CHANGED = "password_changed"  # noqa: S105
    PASSWORD_RESET = "password_reset"  # noqa: S105


class SecuritySeverity(StrEnum):
    """Severidade do evento de seguranca."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLogger:
    """Logger especializado para eventos de seguranca."""

    # Mapeamento de eventos para severidade padrao
    DEFAULT_SEVERITY = {
        SecurityEventType.LOGIN_SUCCESS: SecuritySeverity.LOW,
        SecurityEventType.LOGIN_FAILED: SecuritySeverity.MEDIUM,
        SecurityEventType.LOGIN_BLOCKED: SecuritySeverity.HIGH,
        SecurityEventType.LOGOUT: SecuritySeverity.LOW,
        SecurityEventType.TOKEN_REFRESH: SecuritySeverity.LOW,
        SecurityEventType.TOKEN_EXPIRED: SecuritySeverity.LOW,
        SecurityEventType.TOKEN_INVALID: SecuritySeverity.MEDIUM,
        SecurityEventType.ACCESS_DENIED: SecuritySeverity.MEDIUM,
        SecurityEventType.PERMISSION_DENIED: SecuritySeverity.MEDIUM,
        SecurityEventType.ROLE_CHANGED: SecuritySeverity.MEDIUM,
        SecurityEventType.RATE_LIMIT_EXCEEDED: SecuritySeverity.MEDIUM,
        SecurityEventType.RATE_LIMIT_WARNING: SecuritySeverity.LOW,
        SecurityEventType.BRUTE_FORCE_ATTEMPT: SecuritySeverity.CRITICAL,
        SecurityEventType.SUSPICIOUS_ACTIVITY: SecuritySeverity.HIGH,
        SecurityEventType.IP_BLOCKED: SecuritySeverity.HIGH,
        SecurityEventType.DATA_ACCESS: SecuritySeverity.LOW,
        SecurityEventType.DATA_EXPORT: SecuritySeverity.MEDIUM,
        SecurityEventType.SENSITIVE_DATA_ACCESS: SecuritySeverity.MEDIUM,
        SecurityEventType.CONFIG_CHANGED: SecuritySeverity.MEDIUM,
        SecurityEventType.USER_CREATED: SecuritySeverity.MEDIUM,
        SecurityEventType.USER_DELETED: SecuritySeverity.HIGH,
        SecurityEventType.PASSWORD_CHANGED: SecuritySeverity.MEDIUM,
        SecurityEventType.PASSWORD_RESET: SecuritySeverity.MEDIUM,
    }

    def __init__(self):
        self._failed_logins: dict[str, list] = {}  # Rastreia tentativas falhas

    def log_event(
        self,
        event_type: SecurityEventType,
        message: str,
        user_id: str | None = None,
        user_email: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        resource: str | None = None,
        severity: SecuritySeverity | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Registra evento de seguranca.

        Args:
            event_type: Tipo do evento
            message: Mensagem descritiva
            user_id: ID do usuario (se disponivel)
            user_email: Email do usuario (sanitizado)
            ip_address: IP de origem
            user_agent: User agent do cliente
            resource: Recurso acessado
            severity: Severidade (usa padrao se nao informado)
            metadata: Dados adicionais
        """
        # Determina severidade
        sev = severity or self.DEFAULT_SEVERITY.get(event_type, SecuritySeverity.MEDIUM)

        # Monta log estruturado
        log_data = {
            "security_event": True,
            "event_type": event_type.value,
            "severity": sev.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "message": message,
        }

        # Adiciona campos opcionais
        if user_id:
            log_data["user_id"] = user_id
        if user_email:
            # Sanitiza email para logs
            log_data["user_email"] = self._sanitize_email(user_email)
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent[:200]  # Limita tamanho
        if resource:
            log_data["resource"] = resource
        if metadata:
            log_data["metadata"] = metadata

        # Loga baseado na severidade
        if sev == SecuritySeverity.CRITICAL:
            logger.critical(f"[SECURITY] {message}", **log_data)
        elif sev == SecuritySeverity.HIGH:
            logger.error(f"[SECURITY] {message}", **log_data)
        elif sev == SecuritySeverity.MEDIUM:
            logger.warning(f"[SECURITY] {message}", **log_data)
        else:
            logger.info(f"[SECURITY] {message}", **log_data)

    def _sanitize_email(self, email: str) -> str:
        """Sanitiza email para logs (mascara parte do email)."""
        if not email or "@" not in email:
            return "[INVALID]"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            return f"{local[0]}***@{domain}"
        return f"{local[:2]}***@{domain}"

    def log_login_success(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        user_agent: str | None = None,
    ) -> None:
        """Registra login bem-sucedido."""
        # Limpa tentativas falhas
        if ip_address in self._failed_logins:
            del self._failed_logins[ip_address]

        self.log_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            message=f"Login bem-sucedido para {self._sanitize_email(user_email)}",
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def log_login_failed(
        self,
        user_email: str,
        ip_address: str,
        reason: str = "invalid_credentials",
        user_agent: str | None = None,
    ) -> bool:
        """
        Registra tentativa de login falha.

        Returns:
            True se deve bloquear (muitas tentativas), False caso contrario
        """
        # Rastreia tentativas
        now = datetime.now(UTC).timestamp()
        if ip_address not in self._failed_logins:
            self._failed_logins[ip_address] = []

        # Limpa tentativas antigas (ultimos 15 minutos)
        self._failed_logins[ip_address] = [
            ts
            for ts in self._failed_logins[ip_address]
            if now - ts < 900  # 15 minutos
        ]
        self._failed_logins[ip_address].append(now)

        attempts = len(self._failed_logins[ip_address])

        # Determina severidade baseada no numero de tentativas
        if attempts >= 10:
            severity = SecuritySeverity.CRITICAL
            event_type = SecurityEventType.BRUTE_FORCE_ATTEMPT
        elif attempts >= 5:
            severity = SecuritySeverity.HIGH
            event_type = SecurityEventType.LOGIN_BLOCKED
        else:
            severity = SecuritySeverity.MEDIUM
            event_type = SecurityEventType.LOGIN_FAILED

        self.log_event(
            event_type=event_type,
            message=f"Login falhou para {self._sanitize_email(user_email)} ({attempts} tentativas)",
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            metadata={
                "reason": reason,
                "attempts": attempts,
                "window_minutes": 15,
            },
        )

        # Retorna True se deve bloquear (5+ tentativas)
        return attempts >= 5

    def log_access_denied(
        self,
        user_id: str,
        resource: str,
        action: str,
        ip_address: str | None = None,
        reason: str = "insufficient_permissions",
    ) -> None:
        """Registra acesso negado."""
        self.log_event(
            event_type=SecurityEventType.ACCESS_DENIED,
            message=f"Acesso negado ao recurso {resource}",
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            metadata={
                "action": action,
                "reason": reason,
            },
        )

    def log_rate_limit(
        self,
        ip_address: str,
        endpoint: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        """Registra rate limit excedido."""
        self.log_event(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit excedido para {ip_address}",
            ip_address=ip_address,
            resource=endpoint,
            metadata={
                "limit": limit,
                "window_seconds": window_seconds,
            },
        )

    def log_token_event(
        self,
        event_type: SecurityEventType,
        user_id: str | None = None,
        ip_address: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Registra evento relacionado a token."""
        messages = {
            SecurityEventType.TOKEN_REFRESH: "Token atualizado",
            SecurityEventType.TOKEN_EXPIRED: "Token expirado",
            SecurityEventType.TOKEN_INVALID: "Token invalido",
        }

        self.log_event(
            event_type=event_type,
            message=messages.get(event_type, "Evento de token"),
            user_id=user_id,
            ip_address=ip_address,
            metadata={"reason": reason} if reason else None,
        )


# Instancia global
security_logger = SecurityLogger()
