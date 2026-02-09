"""Serviço de gestão de arquivos AFD.

Arquivo-Fonte de Dados conforme Portaria 671 MTE.
"""

import hashlib
import logging
import os
import tempfile
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import AFDRecord
from modules.hr.rep_integration.repositories import (
    AFDRecordRepository,
    REPDeviceRepository,
)
from modules.hr.rep_integration.schemas import (
    AFDExportRequest,
    AFDExportResponse,
    AFDImportRequest,
    AFDImportResponse,
    AFDValidationResult,
)

logger = logging.getLogger(__name__)


class AFDService:
    """Serviço para gestão de arquivos AFD."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = REPDeviceRepository(db)
        self.afd_repo = AFDRecordRepository(db)

    async def export_afd(
        self,
        request: AFDExportRequest,
        company_cnpj: str,
        company_cei: str,
        company_name: str,
    ) -> AFDExportResponse:
        """Exporta arquivo AFD para um período.

        Args:
            request: Parâmetros de exportação
            company_cnpj: CNPJ da empresa
            company_cei: CEI da empresa
            company_name: Razão social

        Returns:
            Resposta com dados do arquivo gerado.
        """
        device = await self.device_repo.get_by_id(request.device_id)
        if not device:
            raise ValueError("Dispositivo não encontrado")

        # Gerar conteúdo AFD
        content = await self.afd_repo.generate_afd_file(
            device_id=device.id,
            start_date=request.start_date,
            end_date=request.end_date,
            company_cnpj=company_cnpj,
            company_cei=company_cei,
            company_name=company_name,
            rep_serial=device.serial_number,
            manufacturer=device.manufacturer,
            model=device.model,
        )

        if not content:
            return AFDExportResponse(
                success=False,
                file_name="",
                total_records=0,
                period_start=request.start_date,
                period_end=request.end_date,
                generated_at=datetime.utcnow(),
                file_size_bytes=0,
                checksum="",
            )

        # Gerar nome do arquivo
        file_name = self._generate_file_name(
            device.serial_number,
            request.start_date,
            request.end_date,
        )

        # Calcular checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()

        # Contar registros tipo 3
        total_records = content.count("\n3")  # Linhas que começam com tipo 3

        # Salvar arquivo temporário
        file_path = self._save_temp_file(file_name, content)

        # Marcar registros como exportados
        records = await self.afd_repo.get_records_for_export(
            device.id,
            request.start_date,
            request.end_date,
        )
        if records:
            record_ids = [r.id for r in records]
            await self.afd_repo.mark_as_exported(record_ids)

        return AFDExportResponse(
            success=True,
            file_path=file_path,
            file_name=file_name,
            total_records=total_records,
            period_start=request.start_date,
            period_end=request.end_date,
            generated_at=datetime.utcnow(),
            file_size_bytes=len(content.encode()),
            checksum=checksum,
        )

    def _generate_file_name(
        self,
        serial: str,
        start_date: date,
        end_date: date,
    ) -> str:
        """Gera nome do arquivo AFD."""
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        return f"AFD_{serial}_{start_str}_{end_str}.txt"

    def _save_temp_file(self, file_name: str, content: str) -> str:
        """Salva arquivo temporário."""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    async def validate_afd_file(  # pylint: disable=too-many-locals
        self,
        content: str,
    ) -> AFDValidationResult:
        """Valida conteúdo de um arquivo AFD.

        Args:
            content: Conteúdo do arquivo AFD

        Returns:
            Resultado da validação.
        """
        lines = content.strip().split("\n")
        errors = []
        warnings = []
        valid_lines = 0
        invalid_lines = 0
        header_info = None
        company_info = None
        records_count = 0
        dates = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            validation = await self.afd_repo.validate_afd_line(line)

            if validation["is_valid"]:
                valid_lines += 1

                # Extrair informações
                record_type = validation.get("record_type")

                if record_type == "1":
                    header_info = AFDRecord.parse_afd_line(line)
                elif record_type == "2":
                    company_info = AFDRecord.parse_afd_line(line)
                elif record_type == "3":
                    records_count += 1
                    parsed = AFDRecord.parse_afd_line(line)
                    if "record_date" in parsed:
                        dates.append(parsed["record_date"])
            else:
                invalid_lines += 1
                for error in validation.get("errors", []):
                    errors.append(
                        {
                            "line": i,
                            "content": line[:50],
                            "error": error,
                        }
                    )

        # Verificações adicionais
        if not header_info:
            warnings.append(
                {
                    "type": "missing_header",
                    "message": "Arquivo sem cabeçalho (tipo 1)",
                }
            )

        if not company_info:
            warnings.append(
                {
                    "type": "missing_company",
                    "message": "Arquivo sem dados do empregador (tipo 2)",
                }
            )

        # Ordenar datas
        date_range_start = min(dates) if dates else None
        date_range_end = max(dates) if dates else None

        return AFDValidationResult(
            is_valid=len(errors) == 0,
            total_lines=len(lines),
            valid_lines=valid_lines,
            invalid_lines=invalid_lines,
            errors=errors,
            warnings=warnings,
            header_info=header_info,
            company_info=company_info,
            records_count=records_count,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
        )

    async def import_afd_file(  # pylint: disable=too-many-locals
        self,
        request: AFDImportRequest,
    ) -> AFDImportResponse:
        """Importa arquivo AFD.

        Args:
            request: Dados da importação

        Returns:
            Resultado da importação.
        """
        # Validar primeiro
        validation = await self.validate_afd_file(request.file_content)

        if request.validate_only:
            return AFDImportResponse(
                success=True,
                total_lines=validation.total_lines,
                imported_records=0,
                skipped_records=0,
                error_records=0,
                validation_result=validation,
            )

        if not validation.is_valid:
            return AFDImportResponse(
                success=False,
                total_lines=validation.total_lines,
                imported_records=0,
                skipped_records=0,
                error_records=validation.invalid_lines,
                errors=validation.errors,
                validation_result=validation,
            )

        # Importar registros
        lines = request.file_content.strip().split("\n")
        imported = 0
        skipped = 0
        error_count = 0
        errors = []

        device = await self.device_repo.get_by_id(request.device_id)
        if not device:
            return AFDImportResponse(
                success=False,
                total_lines=len(lines),
                imported_records=0,
                skipped_records=0,
                error_records=len(lines),
                errors=[{"error": "Dispositivo não encontrado"}],
            )

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                parsed = AFDRecord.parse_afd_line(line)
                if "error" in parsed:
                    error_count += 1
                    continue

                record_type = parsed.get("record_type")

                # Apenas importar tipo 3 (marcações)
                if record_type != "3":
                    continue

                nsr = parsed.get("nsr")

                # Verificar duplicado
                if request.skip_duplicates:
                    existing = await self.afd_repo.get_by_device_nsr(
                        device.id,
                        nsr,
                    )
                    if existing:
                        skipped += 1
                        continue

                # Criar registro
                line_hash = hashlib.sha256(line.encode()).hexdigest()

                # pylint: disable=import-outside-toplevel
                from modules.hr.rep_integration.schemas import AFDRecordCreate

                await self.afd_repo.create(
                    AFDRecordCreate(
                        device_id=device.id,
                        condominio_id=device.condominio_id,
                        nsr=nsr,
                        record_type=record_type,
                        afd_line=line,
                        record_date=parsed.get("record_date"),
                        record_time=parsed.get("record_time"),
                        pis_number=parsed.get("pis_number"),
                        line_hash=line_hash,
                    )
                )

                imported += 1

            except Exception as e:  # pylint: disable=broad-exception-caught
                error_count += 1
                errors.append(
                    {
                        "line": line[:50],
                        "error": str(e),
                    }
                )

        return AFDImportResponse(
            success=error_count == 0,
            total_lines=len(lines),
            imported_records=imported,
            skipped_records=skipped,
            error_records=error_count,
            errors=errors if errors else None,
            validation_result=validation,
        )

    async def get_afd_statistics(
        self,
        device_id: UUID = None,
        condominio_id: UUID = None,
    ) -> dict[str, Any]:
        """Retorna estatísticas de registros AFD."""
        return await self.afd_repo.get_statistics(
            device_id=device_id,
            condominio_id=condominio_id,
        )

    async def get_export_periods(
        self,
        device_id: UUID,  # pylint: disable=unused-argument
    ) -> list[dict[str, Any]]:
        """Retorna períodos disponíveis para exportação."""
        # TODO: Implementar busca de períodos com registros  # pylint: disable=fixme
        return []
