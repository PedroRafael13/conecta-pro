"""Service para exportação de folha de pagamento."""

import csv
import hashlib
import io
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import ExportFormat, ExportStatus, PayrollExport
from modules.hr.payroll_integration.repositories import (
    PayrollEventRepository,
    PayrollExportRepository,
    PayrollIntegrationRepository,
    PayrollPeriodRepository,
)
from modules.hr.payroll_integration.schemas import (
    ExportDownloadResponse,
    ExportProgressResponse,
    PayrollExportCreate,
)

logger = logging.getLogger(__name__)


class PayrollExportService:
    """Service para exportação de dados de folha."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.period_repo = PayrollPeriodRepository(db)
        self.event_repo = PayrollEventRepository(db)
        self.export_repo = PayrollExportRepository(db)
        self.integration_repo = PayrollIntegrationRepository(db)

    async def create_export(
        self,
        data: PayrollExportCreate,
        condominio_id: UUID,
        *,
        user_id: UUID = None,
    ) -> PayrollExport:
        """Cria nova exportação."""
        if data.period_id:
            period = await self.period_repo.get_by_id(data.period_id)
            if not period:
                raise ValueError("Período não encontrado")
            if not period.can_export:
                raise ValueError("Período não pode ser exportado")

        return await self.export_repo.create(data, condominio_id, created_by=user_id)

    async def get_export(self, export_id: UUID) -> Optional[PayrollExport]:
        """Busca exportação por ID."""
        return await self.export_repo.get_by_id(export_id)

    async def list_exports(
        self,
        condominio_id: UUID,
        *,
        period_id: UUID = None,
        export_format: ExportFormat = None,
        status: ExportStatus = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple:
        """Lista exportações."""
        return await self.export_repo.list_exports(
            condominio_id,
            period_id=period_id,
            export_format=export_format,
            status=status,
            page=page,
            page_size=page_size,
        )

    async def process_export(
        self,
        export_id: UUID,
        condominio_id: UUID,
    ) -> PayrollExport:
        """Processa exportação."""
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise ValueError("Exportação não encontrada")

        # Iniciar processamento
        await self.export_repo.start_processing(export_id)

        try:
            # Buscar dados
            if export.period_id:
                events, total = await self.event_repo.list_by_period(
                    export.period_id,
                    page_size=10000,
                )
            else:
                events = []
                total = 0

            await self.export_repo.update_progress(
                export_id,
                processed_records=0,
            )

            # Gerar arquivo baseado no formato
            export_format = ExportFormat(export.export_format)
            content, file_name = await self._generate_file(
                export=export,
                events=events,
                export_format=export_format,
            )

            # Calcular hash
            file_hash = hashlib.sha256(content).hexdigest()

            # Salvar arquivo (simulado)
            file_path = f"/exports/{condominio_id}/{export.export_code}/{file_name}"

            # Completar exportação
            await self.export_repo.complete(
                export_id,
                file_path=file_path,
                file_name=file_name,
                file_size=len(content),
                file_hash=file_hash,
                total_records=total,
                success_records=total,
            )

            logger.info("Exportação concluída: %s", export.export_code)

        except Exception as e:
            logger.error("Erro na exportação %s: %s", export_id, e)
            await self.export_repo.fail(export_id, str(e))
            raise

        return await self.export_repo.get_by_id(export_id)

    async def _generate_file(
        self,
        export: PayrollExport,
        events: list,
        export_format: ExportFormat,
    ) -> tuple:
        """Gera arquivo de exportação."""
        if export_format == ExportFormat.CSV:
            return self._generate_csv(export, events)
        if export_format == ExportFormat.JSON:
            return self._generate_json(export, events)
        if export_format == ExportFormat.TXT:
            return self._generate_txt(export, events)
        if export_format == ExportFormat.CNAB240:
            return self._generate_cnab240(export, events)
        # Default: JSON
        return self._generate_json(export, events)

    def _generate_csv(
        self,
        export: PayrollExport,
        events: list,
    ) -> tuple:
        """Gera arquivo CSV."""
        output = io.StringIO()
        file_config = export.file_config or {}
        delimiter = file_config.get("delimiter", ";")

        writer = csv.writer(output, delimiter=delimiter)

        # Header
        headers = [
            "employee_id",
            "event_code",
            "event_name",
            "event_type",
            "event_category",
            "reference",
            "value",
            "esocial_code",
        ]
        writer.writerow(headers)

        # Data
        for event in events:
            writer.writerow(
                [
                    str(event.employee_id),
                    event.event_code,
                    event.event_name,
                    event.event_type,
                    event.event_category,
                    float(event.reference) if event.reference else "",
                    float(event.value),
                    event.esocial_code or "",
                ]
            )

        content = output.getvalue()
        encoding = file_config.get("encoding", "utf-8")
        file_name = f"{export.export_code}.csv"

        return content.encode(encoding), file_name

    def _generate_json(
        self,
        export: PayrollExport,
        events: list,
    ) -> tuple:
        """Gera arquivo JSON."""
        data = {
            "export_code": export.export_code,
            "export_name": export.name,
            "generated_at": datetime.utcnow().isoformat(),
            "total_records": len(events),
            "events": [
                {
                    "employee_id": str(e.employee_id),
                    "event_code": e.event_code,
                    "event_name": e.event_name,
                    "event_type": e.event_type,
                    "event_category": e.event_category,
                    "reference": float(e.reference) if e.reference else None,
                    "value": float(e.value),
                    "esocial_code": e.esocial_code,
                }
                for e in events
            ],
        }

        content = json.dumps(data, indent=2, ensure_ascii=False)
        file_name = f"{export.export_code}.json"

        return content.encode("utf-8"), file_name

    def _generate_txt(
        self,
        export: PayrollExport,
        events: list,
    ) -> tuple:
        """Gera arquivo TXT posicional."""
        lines = []

        # Header
        header = "0"  # Tipo registro
        header += datetime.utcnow().strftime("%Y%m%d")  # Data
        header += export.export_code.ljust(20)  # Código
        header += str(len(events)).zfill(10)  # Total registros
        header += " " * 60  # Filler
        lines.append(header)

        # Detalhes
        for event in events:
            line = "1"  # Tipo registro
            line += str(event.employee_id).replace("-", "")[:36].ljust(36)
            line += event.event_code.ljust(10)
            line += str(int(float(event.value) * 100)).zfill(15)  # Valor em centavos
            line += (event.esocial_code or "").ljust(10)
            line += " " * 28  # Filler
            lines.append(line)

        # Trailer
        trailer = "9"  # Tipo registro
        trailer += str(len(events)).zfill(10)
        trailer += " " * 89  # Filler
        lines.append(trailer)

        file_config = export.file_config or {}
        line_ending = file_config.get("line_ending", "\r\n")
        content = line_ending.join(lines)
        file_name = f"{export.export_code}.txt"

        return content.encode("latin-1"), file_name

    def _generate_cnab240(
        self,
        export: PayrollExport,
        events: list,  # pylint: disable=unused-argument
    ) -> tuple:
        """Gera arquivo CNAB 240."""
        lines = []

        # Header de arquivo (tipo 0)
        header_arq = "001"  # Código banco
        header_arq += "0000"  # Lote
        header_arq += "0"  # Tipo registro
        header_arq += " " * 9  # CNAB
        header_arq += "2"  # Tipo inscrição (CNPJ)
        header_arq += "00000000000000"  # CNPJ
        header_arq += " " * 20  # Convênio
        header_arq += "00000"  # Agência
        header_arq += " "  # DV Agência
        header_arq += "000000000000"  # Conta
        header_arq += " "  # DV Conta
        header_arq += " "  # DV Ag/Conta
        header_arq += "EMPRESA".ljust(30)  # Nome empresa
        header_arq += "BANCO".ljust(30)  # Nome banco
        header_arq += " " * 10  # CNAB
        header_arq += "1"  # Código remessa
        header_arq += datetime.utcnow().strftime("%d%m%Y")  # Data
        header_arq += datetime.utcnow().strftime("%H%M%S")  # Hora
        header_arq += "000001"  # NSA
        header_arq += "089"  # Versão layout
        header_arq += "00000"  # Densidade
        header_arq += " " * 20  # Reservado banco
        header_arq += " " * 20  # Reservado empresa
        header_arq += " " * 29  # CNAB
        lines.append(header_arq[:240])

        # Simplificado - em produção teria lotes e detalhes completos

        # Trailer de arquivo (tipo 9)
        trailer = "001"  # Código banco
        trailer += "9999"  # Lote
        trailer += "9"  # Tipo registro
        trailer += " " * 9  # CNAB
        trailer += "000001"  # Qtd lotes
        trailer += str(len(lines) + 1).zfill(6)  # Qtd registros
        trailer += "000000"  # Qtd contas
        trailer += " " * 205  # CNAB
        lines.append(trailer[:240])

        content = "\r\n".join(lines)
        file_name = f"{export.export_code}.rem"

        return content.encode("latin-1"), file_name

    async def get_progress(
        self,
        export_id: UUID,
    ) -> ExportProgressResponse:
        """Retorna progresso da exportação."""
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise ValueError("Exportação não encontrada")

        return ExportProgressResponse(
            export_id=export.id,
            export_code=export.export_code,
            status=export.status,
            total_records=export.total_records,
            processed_records=export.processed_records,
            success_records=export.success_records,
            error_records=export.error_records,
            progress_percentage=export.progress_percentage,
            started_at=export.started_at,
            estimated_completion=None,
            current_step=None,
        )

    async def get_download_info(
        self,
        export_id: UUID,
    ) -> ExportDownloadResponse:
        """Retorna informações para download."""
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise ValueError("Exportação não encontrada")
        if not export.is_completed:
            raise ValueError("Exportação ainda não concluída")

        # Incrementar contador
        await self.export_repo.increment_download(export_id)

        # Gerar URL temporária
        expires_at = datetime.utcnow() + timedelta(hours=24)
        download_url = f"/api/v1/hr/payroll/exports/{export_id}/file"

        content_type_map = {
            ExportFormat.CSV.value: "text/csv",
            ExportFormat.JSON.value: "application/json",
            ExportFormat.TXT.value: "text/plain",
            ExportFormat.XLSX.value: (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            ExportFormat.XML.value: "application/xml",
            ExportFormat.CNAB240.value: "text/plain",
            ExportFormat.CNAB400.value: "text/plain",
        }

        return ExportDownloadResponse(
            export_id=export.id,
            file_name=export.file_name,
            file_size=export.file_size,
            content_type=content_type_map.get(export.export_format, "application/octet-stream"),
            download_url=download_url,
            expires_at=expires_at,
        )

    async def retry_export(
        self,
        export_id: UUID,
    ) -> PayrollExport:
        """Retenta exportação que falhou."""
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise ValueError("Exportação não encontrada")
        if not export.can_retry:
            raise ValueError("Exportação não pode ser retentada")

        # Resetar status
        export.status = ExportStatus.PENDING.value
        export.errors = []
        export.warnings = []
        await self.db.commit()

        # Reprocessar
        return await self.process_export(export_id, export.condominio_id)

    async def cancel_export(
        self,
        export_id: UUID,
    ) -> PayrollExport:
        """Cancela exportação."""
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise ValueError("Exportação não encontrada")

        export.status = ExportStatus.CANCELLED.value
        export.completed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(export)

        return export

    async def process_pending_exports(
        self,
        condominio_id: UUID,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Processa exportações pendentes."""
        pending = await self.export_repo.get_pending_exports(condominio_id, limit)

        results = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "details": [],
        }

        for export in pending:
            try:
                await self.process_export(export.id, condominio_id)
                results["success"] += 1
            except Exception as e:  # pylint: disable=broad-exception-caught
                results["failed"] += 1
                results["details"].append(
                    {
                        "export_id": str(export.id),
                        "error": str(e),
                    }
                )
            results["processed"] += 1

        return results
