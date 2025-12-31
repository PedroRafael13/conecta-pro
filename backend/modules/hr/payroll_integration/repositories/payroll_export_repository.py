"""Repository para exportação de folha de pagamento."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import (
    PayrollExport,
    ExportFormat,
    ExportStatus,
)
from modules.hr.payroll_integration.schemas import (
    PayrollExportCreate,
    PayrollExportUpdate,
)

logger = logging.getLogger(__name__)


class PayrollExportRepository:
    """Repository para operações de exportação."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PayrollExportCreate,
        condominio_id: UUID,
        *,
        created_by: UUID = None,
    ) -> PayrollExport:
        """Cria nova exportação."""
        export_code = f"EXP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6].upper()}"

        export = PayrollExport(
            condominio_id=condominio_id,
            period_id=data.period_id,
            integration_id=data.integration_id,
            export_code=export_code,
            name=data.name,
            description=data.description,
            export_format=data.export_format.value,
            export_type=data.export_type,
            scope=data.scope.model_dump() if data.scope else {},
            file_config=data.file_config.model_dump() if data.file_config else {},
            status=ExportStatus.PENDING.value,
            created_by=created_by,
        )

        self.db.add(export)
        await self.db.commit()
        await self.db.refresh(export)

        logger.info("Exportação criada: %s", export_code)
        return export

    async def get_by_id(
        self,
        export_id: UUID,
    ) -> Optional[PayrollExport]:
        """Busca exportação por ID."""
        query = select(PayrollExport).where(
            and_(
                PayrollExport.id == export_id,
                PayrollExport.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        export_code: str,
        condominio_id: UUID,
    ) -> Optional[PayrollExport]:
        """Busca exportação por código."""
        query = select(PayrollExport).where(
            and_(
                PayrollExport.export_code == export_code,
                PayrollExport.condominio_id == condominio_id,
                PayrollExport.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_exports(
        self,
        condominio_id: UUID,
        *,
        period_id: UUID = None,
        export_format: ExportFormat = None,
        status: ExportStatus = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[PayrollExport], int]:
        """Lista exportações com filtros."""
        conditions = [
            PayrollExport.condominio_id == condominio_id,
            PayrollExport.ativo.is_(True),
        ]

        if period_id:
            conditions.append(PayrollExport.period_id == period_id)
        if export_format:
            conditions.append(PayrollExport.export_format == export_format.value)
        if status:
            conditions.append(PayrollExport.status == status.value)

        # Count
        count_query = select(func.count(PayrollExport.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch
        query = (
            select(PayrollExport)
            .where(and_(*conditions))
            .order_by(PayrollExport.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        exports = list(result.scalars().all())

        return exports, total

    async def update(
        self,
        export_id: UUID,
        data: PayrollExportUpdate,
    ) -> Optional[PayrollExport]:
        """Atualiza exportação."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "scope" in update_data and update_data["scope"]:
            update_data["scope"] = update_data["scope"].model_dump()
        if "file_config" in update_data and update_data["file_config"]:
            update_data["file_config"] = update_data["file_config"].model_dump()

        for field, value in update_data.items():
            if value is not None:
                setattr(export, field, value)

        export.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def start_processing(
        self,
        export_id: UUID,
    ) -> Optional[PayrollExport]:
        """Inicia processamento."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.start_processing()
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def complete(
        self,
        export_id: UUID,
        *,
        file_path: str,
        file_name: str,
        file_size: int,
        file_hash: str = None,
        total_records: int = 0,
        success_records: int = 0,
    ) -> Optional[PayrollExport]:
        """Marca exportação como concluída."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.complete(file_path, file_name, file_size, file_hash)
        export.total_records = total_records
        export.success_records = success_records
        export.processed_records = total_records

        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def fail(
        self,
        export_id: UUID,
        error: str,
    ) -> Optional[PayrollExport]:
        """Marca exportação como falha."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.fail(error)
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def add_error(
        self,
        export_id: UUID,
        *,
        record: int,
        field: str,
        code: str,
        message: str,
        employee_id: str = None,
    ) -> Optional[PayrollExport]:
        """Adiciona erro à exportação."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.add_error(record, field, code, message, employee_id)
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def record_transmission(
        self,
        export_id: UUID,
        *,
        transmission_id: str,
        receipt_number: str = None,
    ) -> Optional[PayrollExport]:
        """Registra transmissão."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.record_transmission(transmission_id, receipt_number)
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def update_progress(
        self,
        export_id: UUID,
        *,
        processed_records: int,
        success_records: int = None,
        error_records: int = None,
    ) -> Optional[PayrollExport]:
        """Atualiza progresso da exportação."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.processed_records = processed_records
        if success_records is not None:
            export.success_records = success_records
        if error_records is not None:
            export.error_records = error_records

        export.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def increment_download(
        self,
        export_id: UUID,
    ) -> Optional[PayrollExport]:
        """Incrementa contador de downloads."""
        export = await self.get_by_id(export_id)
        if not export:
            return None

        export.download_count += 1
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def delete(self, export_id: UUID) -> bool:
        """Soft delete da exportação."""
        export = await self.get_by_id(export_id)
        if not export:
            return False

        export.ativo = False
        export.updated_at = datetime.utcnow()
        await self.db.commit()

        return True

    async def get_pending_exports(
        self,
        condominio_id: UUID,
        limit: int = 10,
    ) -> List[PayrollExport]:
        """Retorna exportações pendentes."""
        query = (
            select(PayrollExport)
            .where(
                and_(
                    PayrollExport.condominio_id == condominio_id,
                    PayrollExport.status == ExportStatus.PENDING.value,
                    PayrollExport.ativo.is_(True),
                )
            )
            .order_by(PayrollExport.created_at)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_retryable_exports(
        self,
        condominio_id: UUID,
        limit: int = 10,
    ) -> List[PayrollExport]:
        """Retorna exportações que podem ser retentadas."""
        query = (
            select(PayrollExport)
            .where(
                and_(
                    PayrollExport.condominio_id == condominio_id,
                    PayrollExport.status == ExportStatus.FAILED.value,
                    PayrollExport.retry_count < PayrollExport.max_retries,
                    PayrollExport.ativo.is_(True),
                )
            )
            .order_by(PayrollExport.created_at)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
