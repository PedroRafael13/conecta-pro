"""Service para Folder."""

import logging
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.repositories.folder_repository import FolderRepository
from modules.ged.models.folder import FolderType, FolderPermission
from modules.ged.schemas.folder import (
    FolderCreate,
    FolderUpdate,
    FolderFilter,
    FolderResponse,
    FolderListResponse,
    FolderTreeNode,
    FolderStats,
)

logger = logging.getLogger(__name__)


class FolderService:
    """Service para operações de Folder."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = FolderRepository(session)

    async def create(self, data: FolderCreate) -> FolderResponse:
        """Cria uma nova pasta."""
        folder = await self.repository.create(data)
        await self.session.commit()
        logger.info("Pasta criada: %s - %s", folder.id, folder.name)
        return FolderResponse.model_validate(folder)

    async def get_by_id(self, folder_id: str) -> Optional[FolderResponse]:
        """Busca pasta por ID."""
        folder = await self.repository.get_by_id(folder_id)
        if not folder:
            return None
        return FolderResponse.model_validate(folder)

    async def get_by_code(self, code: str) -> Optional[FolderResponse]:
        """Busca pasta por código."""
        folder = await self.repository.get_by_code(code)
        if not folder:
            return None
        return FolderResponse.model_validate(folder)

    async def update(
        self, folder_id: str, data: FolderUpdate
    ) -> Optional[FolderResponse]:
        """Atualiza uma pasta."""
        folder = await self.repository.update(folder_id, data)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta atualizada: %s", folder_id)
        return FolderResponse.model_validate(folder)

    async def delete(self, folder_id: str) -> bool:
        """Remove pasta (soft delete)."""
        # Verifica se é pasta do sistema
        folder = await self.repository.get_by_id(folder_id)
        if folder and folder.is_system:
            raise ValueError("Não é possível remover pasta do sistema")

        result = await self.repository.soft_delete(folder_id)
        if result:
            await self.session.commit()
            logger.info("Pasta removida: %s", folder_id)
        return result

    async def list(
        self,
        filters: Optional[FolderFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> FolderListResponse:
        """Lista pastas com filtros e paginação."""
        skip = (page - 1) * page_size
        folders, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return FolderListResponse(
            items=[FolderResponse.model_validate(f) for f in folders],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_root_folders(
        self, condominium_id: str = None
    ) -> List[FolderResponse]:
        """Retorna pastas raiz."""
        folders = await self.repository.get_root_folders(condominium_id)
        return [FolderResponse.model_validate(f) for f in folders]

    async def get_children(self, folder_id: str) -> List[FolderResponse]:
        """Retorna subpastas."""
        folders = await self.repository.get_children(folder_id)
        return [FolderResponse.model_validate(f) for f in folders]

    async def get_tree(
        self, root_id: str = None, condominium_id: str = None
    ) -> List[FolderTreeNode]:
        """Retorna árvore de pastas."""
        folders = await self.repository.get_tree(root_id, condominium_id)

        # Constrói a árvore
        folder_map = {}
        root_nodes = []

        for folder in folders:
            node = FolderTreeNode(
                id=folder.id,
                name=folder.name,
                path=folder.full_path,
                folder_type=folder.folder_type,
                status=folder.status,
                icon=folder.icon,
                color=folder.color,
                document_count=folder.document_count,
                subfolder_count=folder.subfolder_count,
                children=[],
            )
            folder_map[folder.id] = node

            if folder.parent_id and folder.parent_id in folder_map:
                folder_map[folder.parent_id].children.append(node)
            else:
                root_nodes.append(node)

        return root_nodes

    async def get_by_type(
        self, folder_type: FolderType, condominium_id: str = None
    ) -> List[FolderResponse]:
        """Retorna pastas por tipo."""
        folders = await self.repository.get_by_type(folder_type, condominium_id)
        return [FolderResponse.model_validate(f) for f in folders]

    async def archive(
        self, folder_id: str, archived_by: str
    ) -> Optional[FolderResponse]:
        """Arquiva pasta."""
        folder = await self.repository.archive(folder_id, archived_by)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta arquivada: %s", folder_id)
        return FolderResponse.model_validate(folder)

    async def unarchive(self, folder_id: str) -> Optional[FolderResponse]:
        """Desarquiva pasta."""
        folder = await self.repository.unarchive(folder_id)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta desarquivada: %s", folder_id)
        return FolderResponse.model_validate(folder)

    async def block(self, folder_id: str) -> Optional[FolderResponse]:
        """Bloqueia pasta."""
        folder = await self.repository.block(folder_id)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta bloqueada: %s", folder_id)
        return FolderResponse.model_validate(folder)

    async def unblock(self, folder_id: str) -> Optional[FolderResponse]:
        """Desbloqueia pasta."""
        folder = await self.repository.unblock(folder_id)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta desbloqueada: %s", folder_id)
        return FolderResponse.model_validate(folder)

    async def move(
        self, folder_id: str, new_parent_id: str = None
    ) -> Optional[FolderResponse]:
        """Move pasta para novo pai."""
        # Verifica se não está movendo para si mesmo ou descendente
        if new_parent_id:
            folder = await self.repository.get_by_id(folder_id)
            new_parent = await self.repository.get_by_id(new_parent_id)
            if new_parent and new_parent.path.startswith(folder.full_path):
                raise ValueError("Não é possível mover pasta para um descendente")

        folder = await self.repository.move(folder_id, new_parent_id)
        if not folder:
            return None
        await self.session.commit()
        logger.info("Pasta movida: %s para %s", folder_id, new_parent_id)
        return FolderResponse.model_validate(folder)

    async def grant_permission(
        self, folder_id: str, user_id: str, permission: FolderPermission
    ) -> Optional[FolderResponse]:
        """Concede permissão ao usuário."""
        folder = await self.repository.get_by_id(folder_id)
        if not folder:
            return None

        folder.grant_permission(user_id, permission)
        await self.session.commit()
        logger.info("Permissão concedida: %s -> %s", folder_id, user_id)
        return FolderResponse.model_validate(folder)

    async def revoke_permission(
        self, folder_id: str, user_id: str, permission: FolderPermission
    ) -> Optional[FolderResponse]:
        """Revoga permissão do usuário."""
        folder = await self.repository.get_by_id(folder_id)
        if not folder:
            return None

        folder.revoke_permission(user_id, permission)
        await self.session.commit()
        logger.info("Permissão revogada: %s -> %s", folder_id, user_id)
        return FolderResponse.model_validate(folder)

    async def check_permission(
        self, folder_id: str, user_id: str, permission: FolderPermission
    ) -> bool:
        """Verifica permissão do usuário."""
        folder = await self.repository.get_by_id(folder_id)
        if not folder:
            return False
        return folder.has_permission(user_id, permission)

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> List[FolderResponse]:
        """Busca pastas por texto."""
        folders = await self.repository.search(query, condominium_id, limit)
        return [FolderResponse.model_validate(f) for f in folders]

    async def get_stats(self, condominium_id: str = None) -> FolderStats:
        """Retorna estatísticas de pastas."""
        stats = await self.repository.get_stats(condominium_id)
        return FolderStats(**stats)

    async def create_default_structure(
        self, condominium_id: str, owner_id: str, created_by: str
    ) -> List[FolderResponse]:
        """Cria estrutura padrão de pastas."""
        default_folders = [
            {"name": "Contratos", "type": FolderType.CONTRATO, "icon": "file-contract"},
            {"name": "Funcionários", "type": FolderType.FUNCIONARIO, "icon": "users"},
            {"name": "Administrativo", "type": FolderType.DEPARTAMENTO, "icon": "folder"},
            {"name": "Financeiro", "type": FolderType.DEPARTAMENTO, "icon": "money-bill"},
            {"name": "Jurídico", "type": FolderType.DEPARTAMENTO, "icon": "gavel"},
            {"name": "Arquivo Morto", "type": FolderType.ARQUIVO, "icon": "archive"},
        ]

        created = []
        for folder_data in default_folders:
            data = FolderCreate(
                name=folder_data["name"],
                folder_type=folder_data["type"],
                condominium_id=condominium_id,
                owner_id=owner_id,
                created_by=created_by,
                icon=folder_data["icon"],
            )
            folder = await self.repository.create(data)
            created.append(FolderResponse.model_validate(folder))

        await self.session.commit()
        logger.info(
            "Estrutura padrão criada para condomínio: %s", condominium_id
        )
        return created
