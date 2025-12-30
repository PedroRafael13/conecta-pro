"""
Sistema de auditoria para acessos a dados sensiveis.
Registra todas as operacoes criticas para conformidade LGPD.
"""

from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from core.logging import logger


class AuditAction(str, Enum):
    """Tipos de acoes auditaveis."""

    # Dados pessoais
    VIEW_PERSONAL_DATA = "view_personal_data"
    EDIT_PERSONAL_DATA = "edit_personal_data"
    DELETE_PERSONAL_DATA = "delete_personal_data"
    EXPORT_PERSONAL_DATA = "export_personal_data"

    # Dados financeiros
    VIEW_SALARY = "view_salary"
    EDIT_SALARY = "edit_salary"
    VIEW_FINANCIAL = "view_financial"

    # Autenticacao
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"

    # Permissoes
    ROLE_CHANGE = "role_change"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"

    # Administracao
    USER_CREATE = "user_create"
    USER_DEACTIVATE = "user_deactivate"
    CONFIG_CHANGE = "config_change"


class AuditLog(BaseModel):
    """Registro de auditoria."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Quem
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # O que
    action: AuditAction
    resource_type: str  # Ex: "user", "employee", "contract"
    resource_id: Optional[str] = None

    # Contexto
    details: Optional[dict] = None
    success: bool = True
    error_message: Optional[str] = None


# Storage em memoria (substituir por banco em producao)
_audit_logs: list[AuditLog] = []


async def log_audit(
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> AuditLog:
    """
    Registra evento de auditoria.

    Args:
        action: Tipo da acao
        resource_type: Tipo do recurso acessado
        resource_id: ID do recurso (opcional)
        user_id: ID do usuario que realizou a acao
        user_email: Email do usuario
        ip_address: IP do cliente
        user_agent: User-Agent do cliente
        details: Detalhes adicionais (sem dados sensiveis!)
        success: Se a operacao foi bem-sucedida
        error_message: Mensagem de erro se falhou

    Returns:
        Registro de auditoria criado
    """
    audit_log = AuditLog(
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        user_agent=user_agent,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        success=success,
        error_message=error_message,
    )

    # Salvar (em producao, usar banco de dados)
    _audit_logs.append(audit_log)

    # Log estruturado
    log_data = {
        "audit_id": str(audit_log.id),
        "action": action.value,
        "resource": f"{resource_type}:{resource_id or 'N/A'}",
        "user": user_email or user_id or "anonymous",
        "ip": ip_address or "unknown",
        "success": success,
    }

    if success:
        logger.info(f"AUDIT: {action.value}", extra=log_data)
    else:
        logger.warning(f"AUDIT FAIL: {action.value} - {error_message}", extra=log_data)

    return audit_log


def audit_sensitive_access(
    action: AuditAction,
    resource_type: str,
    resource_id_param: Optional[str] = None,
):
    """
    Decorator para auditar acessos a dados sensiveis.

    Args:
        action: Tipo da acao
        resource_type: Tipo do recurso
        resource_id_param: Nome do parametro que contem o ID do recurso

    Usage:
        @audit_sensitive_access(AuditAction.VIEW_SALARY, "employee", "employee_id")
        async def get_employee_salary(employee_id: int):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair resource_id se especificado
            resource_id = None
            if resource_id_param and resource_id_param in kwargs:
                resource_id = str(kwargs[resource_id_param])

            # Tentar extrair user_id do contexto (se disponivel)
            user_id = kwargs.get("current_user_id")
            user_email = None

            # Executar funcao
            try:
                result = await func(*args, **kwargs)

                # Registrar acesso bem-sucedido
                await log_audit(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    user_email=user_email,
                    success=True,
                )

                return result

            except Exception as e:
                # Registrar falha
                await log_audit(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    user_email=user_email,
                    success=False,
                    error_message=str(e),
                )
                raise

        return wrapper

    return decorator


async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> list[AuditLog]:
    """
    Busca logs de auditoria com filtros.

    Args:
        user_id: Filtrar por usuario
        action: Filtrar por tipo de acao
        resource_type: Filtrar por tipo de recurso
        start_date: Data inicial
        end_date: Data final
        limit: Limite de resultados

    Returns:
        Lista de logs de auditoria
    """
    results = _audit_logs.copy()

    if user_id:
        results = [r for r in results if r.user_id == user_id]

    if action:
        results = [r for r in results if r.action == action]

    if resource_type:
        results = [r for r in results if r.resource_type == resource_type]

    if start_date:
        results = [r for r in results if r.timestamp >= start_date]

    if end_date:
        results = [r for r in results if r.timestamp <= end_date]

    # Ordenar por timestamp decrescente
    results.sort(key=lambda x: x.timestamp, reverse=True)

    return results[:limit]
