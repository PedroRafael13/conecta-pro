"""
Servico de Clientes GED — CRUD completo para GedClient.

Gerencia condominios e administradoras que recebem kits documentais mensais.
"""

import logging
import math

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.ged.models.client import GedClient
from modules.people_management.ged.models.document_kit import GedDocumentKit, KitStatus
from modules.people_management.ged.schemas.client import (
    GedClientCreate,
    GedClientList,
    GedClientResponse,
    GedClientUpdate,
)

logger = logging.getLogger(__name__)


class ClientService:
    """Servico de CRUD para clientes GED (condominios/administradoras)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_client(self, data: GedClientCreate, created_by: str | None = None) -> GedClientResponse:
        """Cria um novo cliente GED.

        Args:
            data: Dados do cliente a ser criado.
            created_by: ID do usuario que esta criando.

        Returns:
            GedClientResponse com os dados do cliente criado.

        Raises:
            ValueError: Se CNPJ ja existir no sistema.
        """
        if data.cnpj:
            existing = await self._get_by_cnpj(data.cnpj)
            if existing:
                raise ValueError(f"Ja existe um cliente com o CNPJ {data.cnpj}")

        if data.portal_username:
            username_exists = await self.db.execute(
                select(GedClient).where(GedClient.portal_username == data.portal_username)
            )
            if username_exists.scalar_one_or_none():
                raise ValueError(f"Username '{data.portal_username}' ja esta em uso")

        password_hash = None
        if data.portal_password:
            password_hash = self._hash_password(data.portal_password)

        client = GedClient(
            name=data.name,
            type=data.type,
            cnpj=data.cnpj,
            address=data.address,
            contact_name=data.contact_name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            google_drive_folder_id=data.google_drive_folder_id,
            portal_access_enabled=data.portal_access_enabled,
            portal_username=data.portal_username,
            portal_password_hash=password_hash,
            created_by=created_by,
        )

        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)

        logger.info("Cliente GED criado: %s (id=%s)", client.name, client.id)
        return await self._to_response(client)

    async def get_client(self, client_id: str) -> GedClientResponse:
        """Retorna um cliente pelo ID com contagem de kits ativos.

        Args:
            client_id: UUID do cliente.

        Returns:
            GedClientResponse com dados completos.

        Raises:
            ValueError: Se cliente nao for encontrado.
        """
        client = await self._get_or_raise(client_id)
        return await self._to_response(client)

    async def list_clients(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        type_filter: str | None = None,
    ) -> GedClientList:
        """Lista clientes paginados com busca e filtro.

        Args:
            skip: Offset para paginacao.
            limit: Limite de registros por pagina.
            search: Termo de busca (nome, CNPJ, contato).
            type_filter: Filtro por tipo (condominio, administradora).

        Returns:
            GedClientList com items paginados.
        """
        query = select(GedClient)
        count_query = select(func.count()).select_from(GedClient)

        if search:
            search_term = f"%{search}%"
            search_filter = or_(
                GedClient.name.ilike(search_term),
                GedClient.cnpj.ilike(search_term),
                GedClient.contact_name.ilike(search_term),
                GedClient.contact_email.ilike(search_term),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if type_filter:
            query = query.where(GedClient.type == type_filter)
            count_query = count_query.where(GedClient.type == type_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(GedClient.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        clients = result.scalars().all()

        page = (skip // limit) + 1 if limit > 0 else 1
        pages = math.ceil(total / limit) if limit > 0 else 0

        items = []
        for client in clients:
            items.append(await self._to_response(client))

        return GedClientList(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            pages=pages,
        )

    async def update_client(self, client_id: str, data: GedClientUpdate) -> GedClientResponse:
        """Atualiza parcialmente um cliente GED.

        Args:
            client_id: UUID do cliente.
            data: Campos a atualizar (somente os informados).

        Returns:
            GedClientResponse com dados atualizados.

        Raises:
            ValueError: Se cliente nao encontrado ou CNPJ duplicado.
        """
        client = await self._get_or_raise(client_id)
        update_data = data.model_dump(exclude_unset=True)

        if "cnpj" in update_data and update_data["cnpj"]:
            existing = await self._get_by_cnpj(update_data["cnpj"])
            if existing and str(existing.id) != str(client_id):
                raise ValueError(f"Ja existe outro cliente com o CNPJ {update_data['cnpj']}")

        if "portal_username" in update_data and update_data["portal_username"]:
            username_result = await self.db.execute(
                select(GedClient).where(
                    GedClient.portal_username == update_data["portal_username"],
                    GedClient.id != client_id,
                )
            )
            if username_result.scalar_one_or_none():
                raise ValueError(f"Username '{update_data['portal_username']}' ja esta em uso")

        if "portal_password" in update_data:
            pwd = update_data.pop("portal_password")
            if pwd:
                update_data["portal_password_hash"] = self._hash_password(pwd)

        for field, value in update_data.items():
            if hasattr(client, field):
                setattr(client, field, value)

        await self.db.flush()
        await self.db.refresh(client)

        logger.info("Cliente GED atualizado: %s (id=%s)", client.name, client.id)
        return await self._to_response(client)

    async def delete_client(self, client_id: str) -> dict:
        """Remove um cliente GED.

        Realiza hard delete se o cliente nao possui kits.
        Se possui kits, retorna erro orientando a inativar.

        Args:
            client_id: UUID do cliente.

        Returns:
            Confirmacao da exclusao.

        Raises:
            ValueError: Se cliente nao encontrado ou possui kits.
        """
        client = await self._get_or_raise(client_id)

        kit_count_result = await self.db.execute(
            select(func.count()).select_from(GedDocumentKit).where(GedDocumentKit.client_id == str(client_id))
        )
        kit_count = kit_count_result.scalar() or 0

        if kit_count > 0:
            raise ValueError(
                f"Cliente possui {kit_count} kit(s) documental(is). "
                "Remova os kits antes de excluir o cliente ou desative o acesso ao portal."
            )

        await self.db.delete(client)
        await self.db.flush()

        logger.info("Cliente GED removido: %s (id=%s)", client.name, client_id)
        return {"message": f"Cliente '{client.name}' removido com sucesso", "id": str(client_id)}

    async def get_client_by_cnpj(self, cnpj: str) -> GedClientResponse | None:
        """Busca um cliente pelo CNPJ.

        Args:
            cnpj: CNPJ formatado ou somente digitos.

        Returns:
            GedClientResponse ou None se nao encontrado.
        """
        digits = "".join(c for c in cnpj if c.isdigit())
        if len(digits) == 14:
            formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
        else:
            formatted = cnpj

        client = await self._get_by_cnpj(formatted)
        if not client:
            return None
        return await self._to_response(client)

    async def toggle_portal_access(
        self,
        client_id: str,
        enabled: bool,
        username: str | None = None,
        password_hash: str | None = None,
    ) -> GedClientResponse:
        """Habilita ou desabilita o acesso ao portal do cliente.

        Args:
            client_id: UUID do cliente.
            enabled: Se deve habilitar (True) ou desabilitar (False).
            username: Login do portal (obrigatorio se habilitando).
            password_hash: Hash bcrypt da senha (obrigatorio se habilitando).

        Returns:
            GedClientResponse com dados atualizados.

        Raises:
            ValueError: Se habilitando sem username/password.
        """
        client = await self._get_or_raise(client_id)

        if enabled:
            if not username and not client.portal_username:
                raise ValueError("Username e obrigatorio para habilitar o acesso ao portal")
            if not password_hash and not client.portal_password_hash:
                raise ValueError("Senha e obrigatoria para habilitar o acesso ao portal")

            if username:
                username_result = await self.db.execute(
                    select(GedClient).where(
                        GedClient.portal_username == username,
                        GedClient.id != client_id,
                    )
                )
                if username_result.scalar_one_or_none():
                    raise ValueError(f"Username '{username}' ja esta em uso")
                client.portal_username = username

            if password_hash:
                client.portal_password_hash = password_hash

        client.portal_access_enabled = enabled

        await self.db.flush()
        await self.db.refresh(client)

        action = "habilitado" if enabled else "desabilitado"
        logger.info("Portal %s para cliente %s (id=%s)", action, client.name, client.id)
        return await self._to_response(client)

    # --- Metodos auxiliares ---

    async def _get_or_raise(self, client_id: str) -> GedClient:
        """Busca cliente por ID ou levanta ValueError."""
        result = await self.db.execute(select(GedClient).where(GedClient.id == client_id))
        client = result.scalar_one_or_none()
        if not client:
            raise ValueError(f"Cliente GED nao encontrado: {client_id}")
        return client

    async def _get_by_cnpj(self, cnpj: str) -> GedClient | None:
        """Busca cliente por CNPJ formatado."""
        result = await self.db.execute(select(GedClient).where(GedClient.cnpj == cnpj))
        return result.scalar_one_or_none()

    async def _count_active_kits(self, client_id: str) -> int:
        """Conta kits em montagem ou enviados para um cliente."""
        result = await self.db.execute(
            select(func.count())
            .select_from(GedDocumentKit)
            .where(
                GedDocumentKit.client_id == str(client_id),
                GedDocumentKit.status.in_([KitStatus.EM_MONTAGEM, KitStatus.ENVIADO]),
            )
        )
        return result.scalar() or 0

    async def _to_response(self, client: GedClient) -> GedClientResponse:
        """Converte GedClient ORM para GedClientResponse."""
        active_kits = await self._count_active_kits(str(client.id))
        return GedClientResponse(
            id=str(client.id),
            name=client.name,
            type=client.type,
            cnpj=client.cnpj,
            address=client.address,
            contact_name=client.contact_name,
            contact_email=client.contact_email,
            contact_phone=client.contact_phone,
            google_drive_folder_id=client.google_drive_folder_id,
            portal_access_enabled=client.portal_access_enabled,
            portal_username=client.portal_username,
            active_kits_count=active_kits,
            created_by=str(client.created_by) if client.created_by else None,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    @staticmethod
    def _hash_password(password: str) -> str:
        """Gera hash bcrypt de uma senha.

        Tenta usar bcrypt; se nao disponivel, usa hashlib como fallback.
        """
        try:
            import bcrypt

            return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        except ImportError:
            import hashlib

            logger.warning("bcrypt nao disponivel, usando SHA-256 como fallback para hash de senha")
            return hashlib.sha256(password.encode("utf-8")).hexdigest()
