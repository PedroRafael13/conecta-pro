"""
Controller de Kits Documentais — endpoints REST.

Gerencia o ciclo de vida dos kits documentais mensais:
criacao, montagem automatica, envio, aprovacao e exportacao.
"""

import logging
import os
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.ged.schemas.kit import (
    KitCreate,
    KitListResponse,
    KitResponse,
    KitSummary,
    KitUpdate,
)
from modules.people_management.ged.services.export_service import ExportService
from modules.people_management.ged.services.kit_builder_service import KitBuilderService
from modules.people_management.ged.services.kit_service import KitService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kits", tags=["GED - Kits Documentais"])


class KitSendRequest(BaseModel):
    """Schema para marcar kit como enviado."""

    method: str = Field(..., description="Metodo de envio: email, google_drive, portal, impresso")
    sent_to: str | None = Field(None, max_length=500, description="Destinatario(s)")


class KitApproveRequest(BaseModel):
    """Schema para aprovar kit."""

    approved_by: str = Field(..., max_length=255, description="Nome de quem aprovou")


class KitBuildRequest(BaseModel):
    """Schema para solicitar montagem automatica de kit."""

    reference_month: date | None = Field(None, description="Mes de referencia (usa o do kit se nao informado)")


@router.get("", response_model=KitListResponse)
@router.get("", response_model=KitListResponse, include_in_schema=False)
async def list_kits(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    client_id: str | None = Query(None, description="Filtrar por cliente"),
    status: str | None = Query(None, description="Filtrar por status"),
    year: int | None = Query(None, ge=2020, le=2030, description="Filtrar por ano"),
    month: int | None = Query(None, ge=1, le=12, description="Filtrar por mes"),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(20, ge=1, le=100, description="Limite"),
) -> Any:
    """Lista kits documentais com filtros e paginacao."""
    service = KitService(db)
    return await service.list_kits(
        client_id=client_id,
        status=status,
        year=year,
        month=month,
        skip=skip,
        limit=limit,
    )


@router.get("/summary", response_model=KitSummary)
async def get_kit_summary(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    year: int | None = Query(None, ge=2020, le=2030, description="Ano de referencia"),
    month: int | None = Query(None, ge=1, le=12, description="Mes de referencia"),
) -> Any:
    """Retorna resumo geral dos kits para dashboard."""
    service = KitService(db)
    reference_month = None
    if year and month:
        reference_month = date(year, month, 1)
    return await service.get_kit_summary(reference_month=reference_month)


@router.get("/dashboard")
async def get_kit_dashboard(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    year: int | None = Query(None, ge=2020, le=2030),
    month: int | None = Query(None, ge=1, le=12),
) -> Any:
    """Dashboard completo dos kits documentais.

    Retorna resumo + proxima geracao + clientes sem kit.
    """
    from datetime import datetime

    from modules.people_management.ged.models.client import GedClient
    from modules.people_management.ged.models.document_kit import GedDocumentKit

    now = datetime.now()
    ref_year = year or now.year
    ref_month = month or now.month
    ref_date = date(ref_year, ref_month, 1)

    # Summary basico
    service = KitService(db)
    summary = await service.get_kit_summary(reference_month=ref_date)

    # Proxima geracao (dia 1 do proximo mes as 02:00)
    if ref_month == 12:
        next_month = date(ref_year + 1, 1, 1)
    else:
        next_month = date(ref_year, ref_month + 1, 1)
    proxima_geracao = f"{next_month.isoformat()}T02:00:00"

    # Clientes sem kit neste mes
    from sqlalchemy import select

    all_clients_q = select(GedClient.id, GedClient.name)
    all_clients = (await db.execute(all_clients_q)).all()

    clients_with_kit_q = select(GedDocumentKit.client_id).where(GedDocumentKit.reference_month == ref_date).distinct()
    clients_with_kit = {row[0] for row in (await db.execute(clients_with_kit_q)).all()}

    clientes_sem_kit = [{"id": str(cid), "name": cname} for cid, cname in all_clients if cid not in clients_with_kit]

    # Scheduler status
    try:
        from modules.document_kits import scheduler as kit_scheduler

        sched_status = kit_scheduler.get_scheduler_status()
    except Exception:
        sched_status = {"running": False, "message": "Scheduler indisponivel"}

    return {
        "reference_month": ref_date.isoformat(),
        "summary": summary,
        "proxima_geracao": proxima_geracao,
        "scheduler": sched_status,
        "clientes_sem_kit": clientes_sem_kit,
        "total_clientes_sem_kit": len(clientes_sem_kit),
    }


@router.post("", response_model=KitResponse, status_code=201)
async def create_kit(
    data: KitCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo kit documental para um cliente/mes."""
    service = KitService(db)
    try:
        result = await service.create_kit(data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{kit_id}", response_model=KitResponse)
async def get_kit(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um kit com resumo de documentos."""
    service = KitService(db)
    try:
        return await service.get_kit(kit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: str,
    data: KitUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza campos editaveis de um kit."""
    service = KitService(db)
    try:
        result = await service.update_kit(kit_id, data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{kit_id}")
async def delete_kit(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove um kit. Somente permitido se status = EM_MONTAGEM."""
    service = KitService(db)
    try:
        result = await service.delete_kit(kit_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kit_id}/build")
async def build_kit(
    kit_id: str,
    data: KitBuildRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dispara montagem automatica do kit.

    Coleta documentos de DP, Fiscal e Operacoes automaticamente.
    """
    kit_service = KitService(db)
    try:
        kit_resp = await kit_service.get_kit(kit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    builder = KitBuilderService(db)
    try:
        ref_month = data.reference_month or kit_resp.reference_month
        result = await builder.build_kit_for_client(
            client_id=kit_resp.client_id,
            reference_month=ref_month,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auto-assemble")
async def auto_assemble_kits(
    reference_month: date | None = Query(None, description="Mes de referencia (default: mes atual)"),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Monta kits automaticamente para todos os clientes ativos.

    Coleta documentos de DP, Fiscal e Operacoes automaticamente
    para cada cliente que tem funcionarios alocados.
    """
    ref = reference_month or date.today().replace(day=1)
    builder = KitBuilderService(db)
    try:
        result = await builder.auto_build_all_kits(ref)
        await db.commit()
        return result
    except Exception as e:
        logger.error(f"Erro no auto-assemble: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kit_id}/send", response_model=KitResponse)
async def send_kit(
    kit_id: str,
    data: KitSendRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Marca o kit como enviado com metodo e destinatario."""
    service = KitService(db)
    try:
        result = await service.mark_kit_sent(
            kit_id=kit_id,
            method=data.method,
            sent_to=data.sent_to,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kit_id}/send-email")
async def send_kit_email(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Envia kit por email para o cliente.

    Busca o email do cliente GED, compoe o email com resumo do kit
    e envia via SMTP. Marca o kit como enviado se bem sucedido.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    from sqlalchemy import func, select

    from core.config.settings import settings
    from modules.people_management.ged.models.client import GedClient
    from modules.people_management.ged.models.document_kit import GedDocumentKit
    from modules.people_management.ged.models.kit_document import KitDocument

    # Buscar kit
    kit_result = await db.execute(select(GedDocumentKit).where(GedDocumentKit.id == kit_id))
    kit = kit_result.scalars().first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")

    # Buscar cliente
    client_result = await db.execute(select(GedClient).where(GedClient.id == kit.client_id))
    client = client_result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    if not client.contact_email:
        return {
            "status": "sem_email",
            "kit_id": kit_id,
            "client_name": client.name,
            "message": "Cliente nao possui email cadastrado",
        }

    # Contar documentos por tipo
    doc_count_result = await db.execute(
        select(KitDocument.document_type, func.count())
        .where(KitDocument.kit_id == kit_id)
        .group_by(KitDocument.document_type)
    )
    doc_counts = {row[0]: row[1] for row in doc_count_result.all()}

    ref_month = kit.reference_month.strftime("%m/%Y") if kit.reference_month else "N/A"

    # Montar email
    subject = f"Kit Documental {ref_month} - Conecta Mais Seguranca e Tecnologia"
    doc_list = "\n".join(f"  - {dtype}: {count} documento(s)" for dtype, count in sorted(doc_counts.items()))

    body = f"""Prezado(a),

Segue o kit documental referente ao periodo {ref_month} para {client.name}.

RESUMO DO KIT:
  Funcionarios: {kit.total_employees}
  Total de documentos: {kit.total_documents}
  Documentos assinados: {kit.documents_signed}

DOCUMENTOS INCLUIDOS:
{doc_list}

Para acessar e baixar os documentos, entre no portal do cliente
ou solicite o envio do arquivo ZIP ao seu contato na Conecta Mais.

Atenciosamente,
Conecta Mais - Seguranca e Tecnologia
CNPJ: 35.710.481/0001-03
"""

    # Enviar email
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = client.contact_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        smtp_host = settings.SMTP_HOST
        smtp_port = settings.SMTP_PORT
        smtp_user = settings.SMTP_USERNAME
        smtp_pass = settings.SMTP_PASSWORD

        if not smtp_host or not smtp_user:
            return {
                "status": "smtp_nao_configurado",
                "kit_id": kit_id,
                "message": "SMTP nao configurado no servidor",
            }

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()

        # Marcar kit como enviado
        service = KitService(db)
        await service.mark_kit_sent(
            kit_id=kit_id,
            method="email",
            sent_to=client.contact_email,
        )
        await db.commit()

        logger.info("Kit %s enviado por email para %s (%s)", kit_id, client.name, client.contact_email)

        return {
            "status": "enviado",
            "kit_id": kit_id,
            "client_name": client.name,
            "email": client.contact_email,
            "subject": subject,
            "documents_count": sum(doc_counts.values()),
        }

    except smtplib.SMTPException as e:
        logger.error("Erro SMTP ao enviar kit %s: %s", kit_id, e)
        return {
            "status": "erro_smtp",
            "kit_id": kit_id,
            "client_name": client.name,
            "email": client.contact_email,
            "error": str(e),
        }
    except Exception as e:
        logger.error("Erro ao enviar kit %s por email: %s", kit_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {e}") from e


@router.post("/{kit_id}/approve", response_model=KitResponse)
async def approve_kit(
    kit_id: str,
    data: KitApproveRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Aprova o kit documental."""
    service = KitService(db)
    try:
        result = await service.approve_kit(
            kit_id=kit_id,
            approved_by=data.approved_by,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{kit_id}/export/zip")
async def export_zip(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera e retorna o ZIP do kit para download."""
    export_svc = ExportService(db)
    try:
        result = await export_svc.generate_zip(kit_id)
        await db.commit()

        zip_path = result["zip_path"]
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Arquivo ZIP nao foi gerado corretamente")

        # Registrar log de acesso
        await export_svc.log_access(
            kit_id=kit_id,
            action="downloaded",
            actor_type="internal",
            actor_id=str(current_user.id),
            actor_name=getattr(current_user, "full_name", None) or str(current_user.id),
            ip=None,
            user_agent=None,
            notes="Download ZIP via API",
        )
        await db.commit()

        return FileResponse(
            path=zip_path,
            filename=result["zip_filename"],
            media_type="application/zip",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{kit_id}/export/pdf")
async def export_pdf(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera e retorna o PDF consolidado do kit para download."""
    export_svc = ExportService(db)
    try:
        result = await export_svc.generate_consolidated_pdf(kit_id)
        await db.commit()

        pdf_path = result["pdf_path"]
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Arquivo PDF nao foi gerado corretamente")

        # Detectar tipo MIME pelo arquivo gerado
        media_type = "application/pdf"
        if pdf_path.endswith(".txt"):
            media_type = "text/plain"

        await export_svc.log_access(
            kit_id=kit_id,
            action="downloaded",
            actor_type="internal",
            actor_id=str(current_user.id),
            actor_name=getattr(current_user, "full_name", None) or str(current_user.id),
            ip=None,
            user_agent=None,
            notes="Download PDF consolidado via API",
        )
        await db.commit()

        return FileResponse(
            path=pdf_path,
            filename=result["pdf_filename"],
            media_type=media_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
