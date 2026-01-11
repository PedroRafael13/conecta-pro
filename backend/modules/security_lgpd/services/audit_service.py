"""
Service de Auditoria LGPD.
"""

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuditService:
    """Service para gerenciamento de trilha de auditoria.

    Encapsula a logica de registro e consulta de eventos
    de auditoria com hash chain.
    """

    # Armazenamento em memoria (em producao, usar banco de dados)
    _logs: List[Dict[str, Any]] = []
    _last_hash: str = "0" * 64

    def __init__(self):
        """Inicializa o service."""
        pass

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calcula hash do evento para hash chain."""
        content = f"{self._last_hash}{data['timestamp']}{data['action']}{data['resource_id']}"
        return hashlib.sha256(content.encode()).hexdigest()

    def log_event(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> Dict[str, Any]:
        """Registra evento de auditoria.

        Args:
            action: Acao executada.
            resource_type: Tipo de recurso.
            resource_id: ID do recurso.
            user_id: ID do usuario.
            details: Detalhes adicionais.
            severity: Severidade do evento.

        Returns:
            Dict com confirmacao do registro.
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        log_entry = {
            "log_id": log_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "details": details or {},
            "severity": severity,
            "timestamp": timestamp,
            "previous_hash": self._last_hash,
        }

        # Calcula hash para hash chain
        log_entry["hash"] = self._calculate_hash(log_entry)
        self._last_hash = log_entry["hash"]

        self._logs.append(log_entry)

        logger.info(
            "Evento de auditoria registrado: action=%s, resource=%s",
            action,
            resource_type,
        )

        return {
            "log_id": log_id,
            "action": action,
            "resource_type": resource_type,
            "timestamp": timestamp,
            "hash": log_entry["hash"][:16] + "...",
        }

    def query_logs(
        self,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Consulta eventos de auditoria.

        Args:
            resource_type: Filtro por tipo de recurso.
            user_id: Filtro por usuario.
            start_date: Data inicial.
            end_date: Data final.
            limit: Limite de resultados.
            offset: Offset para paginacao.

        Returns:
            Dict com lista de eventos.
        """
        filtered_logs = self._logs.copy()

        if resource_type:
            filtered_logs = [l for l in filtered_logs if l["resource_type"] == resource_type]

        if user_id:
            filtered_logs = [l for l in filtered_logs if l["user_id"] == user_id]

        if start_date:
            start_str = start_date.isoformat()
            filtered_logs = [l for l in filtered_logs if l["timestamp"] >= start_str]

        if end_date:
            end_str = end_date.isoformat()
            filtered_logs = [l for l in filtered_logs if l["timestamp"] <= end_str]

        # Paginacao
        total = len(filtered_logs)
        paginated = filtered_logs[offset:offset + limit]

        return {
            "logs": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verifica integridade da cadeia de hashes.

        Returns:
            Dict com resultado da verificacao.
        """
        if not self._logs:
            return {"valid": True, "total_logs": 0, "message": "Cadeia vazia"}

        previous_hash = "0" * 64
        for i, log in enumerate(self._logs):
            if log["previous_hash"] != previous_hash:
                return {
                    "valid": False,
                    "total_logs": len(self._logs),
                    "error_at": i,
                    "message": f"Hash inconsistente no log {i}",
                }
            previous_hash = log["hash"]

        return {
            "valid": True,
            "total_logs": len(self._logs),
            "message": "Cadeia integra",
        }

    def get_actions(self) -> List[Dict[str, str]]:
        """Lista acoes de auditoria disponiveis.

        Returns:
            Lista de acoes.
        """
        return [
            {"id": "create", "description": "Criacao de recurso"},
            {"id": "read", "description": "Leitura de recurso"},
            {"id": "update", "description": "Atualizacao de recurso"},
            {"id": "delete", "description": "Exclusao de recurso"},
            {"id": "export", "description": "Exportacao de dados"},
            {"id": "consent", "description": "Operacao de consentimento"},
            {"id": "login", "description": "Login de usuario"},
            {"id": "logout", "description": "Logout de usuario"},
            {"id": "encrypt", "description": "Criptografia de dados"},
            {"id": "decrypt", "description": "Descriptografia de dados"},
            {"id": "mask", "description": "Mascaramento de dados"},
            {"id": "erasure", "description": "Exclusao de dados"},
        ]

    def get_resource_types(self) -> List[Dict[str, str]]:
        """Lista tipos de recurso auditados.

        Returns:
            Lista de tipos de recurso.
        """
        return [
            {"id": "user", "description": "Usuario"},
            {"id": "document", "description": "Documento"},
            {"id": "consent", "description": "Consentimento"},
            {"id": "data", "description": "Dados"},
            {"id": "system", "description": "Sistema"},
            {"id": "audit", "description": "Auditoria"},
        ]
