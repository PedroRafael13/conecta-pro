"""Repository para Folder."""

import logging
from typing import Optional, List, Tuple
from uuid import uuid4

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.ged.models.folder import Folder, FolderStatus, FolderType
from modules.ged.schemas.folder import FolderCreate, FolderUpdate, FolderFilter

logger = logging.getLogger(__name__)


class FolderRepository:
    """Repository para operações de Folder."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    def _generate_code(self) -> str:
        """Gera código único para pasta."""
        return f"FLD-{str(uuid4())[:8].upper()}"

    async def create(self, data: FolderCreate) -> Folder:
        """Cria uma nova pasta."""
        folder = Folder(
            code=self._generate_code(),
            **data.model_dump(),
        )

        # Define path baseado no parent
        if data.parent_id:
            parent = await self.get_by_id(data.parent_id)
            if parent:
                folder.update_path(parent.full_path)
                parent.increment_subfolder_count()

        self.session.add(folder)
        await self.session.flush()
        return folder

    async def get_by_id(self, folder_id: str) -> Optional[Folder]:
        """Busca pasta por ID."""
        result = await self.session.execute(
            select(Folder).where(Folder.id == folder_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Folder]:
        """Busca pasta por código."""
        result = await self.session.execute(
            select(Folder).where(Folder.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_path(self, path: str) -> Optional[Folder]:
        """Busca pasta por caminho."""
        result = await self.session.execute(
            select(Folder).where(Folder.full_path == path)
        )
        return result.scalar_one_or_none()

    async def update(self, folder_id: str, data: FolderUpdate) -> Optional[Folder]:
        """Atualiza uma pasta."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)

        await self.session.flush()
        return folder

    async def soft_delete(self, folder_id: str) -> bool:
        """Remove pasta (soft delete)."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return False

        folder.soft_delete()

        # Atualiza contador do pai
        if folder.parent_id:
            parent = await self.get_by_id(folder.parent_id)
            if parent:
                parent.decrement_subfolder_count()

        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[FolderFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[Folder], int]:
        """Lista pastas com filtros e paginação."""
        query = select(Folder).where(Folder.status != FolderStatus.EXCLUIDA)

        if filters:
            if filters.folder_type:
                query = query.where(Folder.folder_type == filters.folder_type)
            if filters.status:
                query = query.where(Folder.status == filters.status)
            if filters.parent_id:
                query = query.where(Folder.parent_id == filters.parent_id)
            if filters.condominium_id:
                query = query.where(Folder.condominium_id == filters.condominium_id)
            if filters.owner_id:
                query = query.where(Folder.owner_id == filters.owner_id)
            if filters.is_public is not None:
                query = query.where(Folder.is_public == filters.is_public)
            if filters.is_root:
                query = query.where(Folder.parent_id.is_(None))
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Folder.name.ilike(search_term),
                        Folder.description.ilike(search_term),
                        Folder.code.ilike(search_term),
                    )
                )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação
        order_column = getattr(Folder, order_by, Folder.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        folders = result.scalars().all()

        return list(folders), total

    async def get_root_folders(
        self, condominium_id: str = None
    ) -> List[Folder]:
        """Retorna pastas raiz."""
        query = select(Folder).where(
            and_(
                Folder.parent_id.is_(None),
                Folder.status == FolderStatus.ATIVA,
            )
        )
        if condominium_id:
            query = query.where(Folder.condominium_id == condominium_id)

        result = await self.session.execute(query.order_by(Folder.order, Folder.name))
        return list(result.scalars().all())

    async def get_children(self, folder_id: str) -> List[Folder]:
        """Retorna subpastas."""
        query = select(Folder).where(
            and_(
                Folder.parent_id == folder_id,
                Folder.status == FolderStatus.ATIVA,
            )
        )
        result = await self.session.execute(query.order_by(Folder.order, Folder.name))
        return list(result.scalars().all())

    async def get_tree(
        self, root_id: str = None, condominium_id: str = None
    ) -> List[Folder]:
        """Retorna árvore de pastas."""
        if root_id:
            # Retorna subárvore a partir de root_id
            root = await self.get_by_id(root_id)
            if not root:
                return []
            query = select(Folder).where(
                and_(
                    Folder.path.startswith(root.full_path),
                    Folder.status == FolderStatus.ATIVA,
                )
            )
        else:
            # Retorna todas as pastas
            query = select(Folder).where(Folder.status == FolderStatus.ATIVA)
            if condominium_id:
                query = query.where(Folder.condominium_id == condominium_id)

        result = await self.session.execute(
            query.order_by(Folder.level, Folder.order, Folder.name)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self, folder_type: FolderType, condominium_id: str = None
    ) -> List[Folder]:
        """Retorna pastas por tipo."""
        query = select(Folder).where(
            and_(
                Folder.folder_type == folder_type,
                Folder.status == FolderStatus.ATIVA,
            )
        )
        if condominium_id:
            query = query.where(Folder.condominium_id == condominium_id)

        result = await self.session.execute(query.order_by(Folder.name))
        return list(result.scalars().all())

    async def archive(
        self, folder_id: str, archived_by: str
    ) -> Optional[Folder]:
        """Arquiva pasta."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None
        folder.archive(archived_by)
        await self.session.flush()
        return folder

    async def unarchive(self, folder_id: str) -> Optional[Folder]:
        """Desarquiva pasta."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None
        folder.unarchive()
        await self.session.flush()
        return folder

    async def block(self, folder_id: str) -> Optional[Folder]:
        """Bloqueia pasta."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None
        folder.block()
        await self.session.flush()
        return folder

    async def unblock(self, folder_id: str) -> Optional[Folder]:
        """Desbloqueia pasta."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None
        folder.unblock()
        await self.session.flush()
        return folder

    async def move(
        self, folder_id: str, new_parent_id: str = None
    ) -> Optional[Folder]:
        """Move pasta para novo pai."""
        folder = await self.get_by_id(folder_id)
        if not folder:
            return None

        # Remove do pai antigo
        if folder.parent_id:
            old_parent = await self.get_by_id(folder.parent_id)
            if old_parent:
                old_parent.decrement_subfolder_count()

        # Adiciona ao novo pai
        if new_parent_id:
            new_parent = await self.get_by_id(new_parent_id)
            if new_parent:
                folder.update_path(new_parent.full_path)
                new_parent.increment_subfolder_count()
        else:
            folder.update_path("/")

        folder.parent_id = new_parent_id
        await self.session.flush()
        return folder

    async def update_document_stats(
        self, folder_id: str, size_diff: int, count_diff: int = 1
    ) -> None:
        """Atualiza estatísticas de documentos."""
        folder = await self.get_by_id(folder_id)
        if folder:
            if count_diff > 0:
                folder.increment_document_count(size_diff)
            else:
                folder.decrement_document_count(abs(size_diff))
            await self.session.flush()

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas de pastas."""
        query = select(Folder).where(Folder.status != FolderStatus.EXCLUIDA)
        if condominium_id:
            query = query.where(Folder.condominium_id == condominium_id)

        result = await self.session.execute(query)
        folders = result.scalars().all()

        stats = {
            "total_folders": len(folders),
            "active_folders": 0,
            "archived_folders": 0,
            "by_type": {},
            "total_documents": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0,
        }

        for folder in folders:
            if folder.status == FolderStatus.ATIVA:
                stats["active_folders"] += 1
            elif folder.status == FolderStatus.ARQUIVADA:
                stats["archived_folders"] += 1

            folder_type = folder.folder_type.value
            stats["by_type"][folder_type] = stats["by_type"].get(folder_type, 0) + 1
            stats["total_documents"] += folder.document_count
            stats["total_size_bytes"] += folder.total_size_bytes

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        return stats

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> List[Folder]:
        """Busca pastas por texto."""
        search_term = f"%{query}%"
        stmt = (
            select(Folder)
            .where(
                and_(
                    Folder.status == FolderStatus.ATIVA,
                    or_(
                        Folder.name.ilike(search_term),
                        Folder.description.ilike(search_term),
                        Folder.code.ilike(search_term),
                    ),
                )
            )
            .limit(limit)
        )
        if condominium_id:
            stmt = stmt.where(Folder.condominium_id == condominium_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
