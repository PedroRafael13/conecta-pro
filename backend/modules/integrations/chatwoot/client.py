"""
Cliente HTTP para a API REST do Chatwoot fazer.ai.

PRD Sec. 7.2 — assinatura completa da classe, sem implementacao real
no Slice 1. Apos aprovacao do approach, Slice 2 preenche os corpos
com httpx + tenacity (retry exponencial).
"""
from __future__ import annotations

from typing import Any, Optional


class ChatwootError(Exception):
    """Erro generico ao falar com a API do Chatwoot."""


class ChatwootClient:
    """
    Cliente HTTP para Chatwoot fazer.ai.

    Uso esperado (Slice 2+):
        client = ChatwootClient(
            base_url="https://chat.conectamais.pro",
            api_token=settings.chatwoot_api_token,
            account_id=1,
        )
        contact = await client.search_contact_by_phone("+5592999990000")

    Sec. 7.2 do PRD T5 v1.0.
    """

    def __init__(self, base_url: str, api_token: str, account_id: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.account_id = account_id
        # NOTE Slice 2: self._http = httpx.AsyncClient(timeout=10.0, ...)

    # ---------------------------------------------------------------- Contatos

    async def create_contact(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        custom_attrs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """POST /api/v1/accounts/{account_id}/contacts"""
        raise NotImplementedError("Slice 2")

    async def update_contact(self, contact_id: int, **fields: Any) -> dict[str, Any]:
        """PATCH /api/v1/accounts/{account_id}/contacts/{id}"""
        raise NotImplementedError("Slice 2")

    async def search_contact_by_phone(self, phone: str) -> Optional[dict[str, Any]]:
        """GET /api/v1/accounts/{account_id}/contacts/search?include=phone_number"""
        raise NotImplementedError("Slice 2")

    # ---------------------------------------------------------------- Conversas

    async def create_conversation(
        self,
        contact_id: int,
        inbox_id: int,
        message: Optional[str] = None,
    ) -> dict[str, Any]:
        """POST /api/v1/accounts/{account_id}/conversations"""
        raise NotImplementedError("Slice 2")

    async def assign_conversation(self, conversation_id: int, agent_id: int) -> None:
        """POST /api/v1/accounts/{account_id}/conversations/{id}/assignments"""
        raise NotImplementedError("Slice 2")

    async def add_label(self, conversation_id: int, label: str) -> None:
        """POST /api/v1/accounts/{account_id}/conversations/{id}/labels"""
        raise NotImplementedError("Slice 2")

    async def remove_label(self, conversation_id: int, label: str) -> None:
        """DELETE /api/v1/accounts/{account_id}/conversations/{id}/labels"""
        raise NotImplementedError("Slice 2")

    async def resolve_conversation(self, conversation_id: int) -> None:
        """POST /api/v1/accounts/{account_id}/conversations/{id}/toggle_status"""
        raise NotImplementedError("Slice 2")

    # ---------------------------------------------------------------- Mensagens

    async def send_message(
        self,
        conversation_id: int,
        content: str,
        attachments: Optional[list[dict[str, Any]]] = None,
        private: bool = False,
    ) -> dict[str, Any]:
        """POST /api/v1/accounts/{account_id}/conversations/{id}/messages"""
        raise NotImplementedError("Slice 2")

    async def send_template_message(
        self,
        conversation_id: int,
        template_id: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Futuro Cloud API. Slice >= 6."""
        raise NotImplementedError("Slice >= 6 (Cloud API)")

    # ---------------------------------------------------------------- Atributos

    async def set_contact_custom_attribute(
        self,
        contact_id: int,
        key: str,
        value: Any,
    ) -> None:
        """PATCH /api/v1/accounts/{account_id}/contacts/{id} (custom_attributes)"""
        raise NotImplementedError("Slice 2")

    async def set_conversation_custom_attribute(
        self,
        conversation_id: int,
        key: str,
        value: Any,
    ) -> None:
        """POST /api/v1/accounts/{account_id}/conversations/{id}/custom_attributes"""
        raise NotImplementedError("Slice 2")

    # ---------------------------------------------------------------- Lifecycle

    async def close(self) -> None:
        """Fecha o httpx.AsyncClient (Slice 2)."""
        return None
