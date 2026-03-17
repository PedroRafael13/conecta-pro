"""
Servico de Exportacao e Entrega de Kits Documentais.

Gera ZIPs consolidados, PDFs unificados, envia por email,
disponibiliza no portal e registra logs de acesso.
"""

import logging
import os
import zipfile
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.ged.models.access_log import AccessAction, ActorType, KitAccessLog
from modules.people_management.ged.models.client import GedClient
from modules.people_management.ged.models.document_kit import GedDocumentKit, KitSendMethod, KitStatus
from modules.people_management.ged.models.kit_document import KitDocument

logger = logging.getLogger(__name__)

GED_STORAGE_BASE = os.environ.get("GED_STORAGE_PATH", "/opt/conecta-pro/storage/ged")
GED_EXPORT_PATH = os.environ.get("GED_EXPORT_PATH", "/opt/conecta-pro/storage/ged/exports")


class ExportService:
    """Servico de exportacao e entrega de kits documentais."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_zip(self, kit_id: str) -> dict:
        """Gera um arquivo ZIP com todos os documentos do kit.

        Organiza os documentos em pastas por tipo dentro do ZIP:
        - /funcionarios/{nome}/contracheque.pdf
        - /funcionarios/{nome}/folha_ponto.pdf
        - /certidoes/cnd_federal.pdf
        - /guias/gfip_sefip.pdf

        Args:
            kit_id: UUID do kit.

        Returns:
            Dicionario com caminho do ZIP e metadados.

        Raises:
            ValueError: Se kit nao encontrado ou sem documentos.
        """
        kit = await self._get_kit_or_raise(kit_id)
        client = await self._get_client(str(kit.client_id))
        client_name = client.name if client else "cliente_desconhecido"

        # Buscar documentos
        result = await self.db.execute(
            select(KitDocument).where(KitDocument.kit_id == kit_id).order_by(KitDocument.document_type)
        )
        documents = result.scalars().all()

        if not documents:
            raise ValueError(f"Kit {kit_id} nao possui documentos para exportar")

        # Preparar diretorio de exportacao
        os.makedirs(GED_EXPORT_PATH, exist_ok=True)

        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in client_name)
        ref_str = kit.reference_month.strftime("%Y-%m")
        zip_filename = f"kit_{safe_name}_{ref_str}_{str(uuid4())[:8]}.zip"
        zip_path = os.path.join(GED_EXPORT_PATH, zip_filename)

        files_added = 0
        files_missing = 0

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for doc in documents:
                # Determinar pasta interna no ZIP
                if doc.employee_id:
                    folder = f"funcionarios/{doc.employee_id}"
                elif (
                    doc.document_type.startswith("cnd_")
                    or doc.document_type.startswith("crf_")
                    or doc.document_type.startswith("cndt_")
                ):
                    folder = "certidoes"
                elif doc.document_type.startswith("g") and doc.document_type in ("gfip_sefip", "grf_fgts", "gps_inss"):
                    folder = "guias"
                else:
                    folder = "outros"

                # Nome do arquivo no ZIP
                ext = os.path.splitext(doc.file_path or ".pdf")[1] or ".pdf"
                archive_name = f"{folder}/{doc.document_type}{ext}"

                # Tentar incluir o arquivo real
                if doc.file_path:
                    full_path = os.path.join(GED_STORAGE_BASE, doc.file_path)
                    if os.path.exists(full_path):
                        zf.write(full_path, archive_name)
                        files_added += 1
                    else:
                        # Criar placeholder com informacoes do documento
                        placeholder = (
                            f"Documento: {doc.document_name}\n"
                            f"Tipo: {doc.document_type}\n"
                            f"Arquivo original: {doc.file_path}\n"
                            f"Status: Arquivo nao encontrado no storage\n"
                            f"Criado em: {doc.created_at}\n"
                        )
                        zf.writestr(f"{folder}/{doc.document_type}.txt", placeholder)
                        files_missing += 1
                else:
                    placeholder = (
                        f"Documento: {doc.document_name}\nTipo: {doc.document_type}\nStatus: Sem arquivo vinculado\n"
                    )
                    zf.writestr(f"{folder}/{doc.document_type}.txt", placeholder)
                    files_missing += 1

            # Adicionar indice
            index_content = self._generate_index(kit, client_name, documents)
            zf.writestr("INDICE.txt", index_content)

        # Atualizar kit com caminho do ZIP
        kit.zip_file_path = zip_path
        await self.db.flush()

        zip_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0

        logger.info(
            "ZIP gerado para kit %s: %s (%d arquivos, %d ausentes, %d bytes)",
            kit_id,
            zip_path,
            files_added,
            files_missing,
            zip_size,
        )

        return {
            "kit_id": kit_id,
            "zip_path": zip_path,
            "zip_filename": zip_filename,
            "files_added": files_added,
            "files_missing": files_missing,
            "zip_size_bytes": zip_size,
        }

    async def generate_consolidated_pdf(self, kit_id: str) -> dict:
        """Gera um PDF consolidado com todos os documentos do kit.

        Utiliza PyMuPDF (fitz) para mesclar PDFs. Se nao disponivel,
        gera um PDF simples com indice dos documentos.

        Args:
            kit_id: UUID do kit.

        Returns:
            Dicionario com caminho do PDF e metadados.

        Raises:
            ValueError: Se kit nao encontrado ou sem documentos.
        """
        kit = await self._get_kit_or_raise(kit_id)
        client = await self._get_client(str(kit.client_id))
        client_name = client.name if client else "cliente_desconhecido"

        result = await self.db.execute(
            select(KitDocument).where(KitDocument.kit_id == kit_id).order_by(KitDocument.document_type)
        )
        documents = result.scalars().all()

        if not documents:
            raise ValueError(f"Kit {kit_id} nao possui documentos para consolidar")

        os.makedirs(GED_EXPORT_PATH, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in client_name)
        ref_str = kit.reference_month.strftime("%Y-%m")
        pdf_filename = f"kit_consolidado_{safe_name}_{ref_str}_{str(uuid4())[:8]}.pdf"
        pdf_path = os.path.join(GED_EXPORT_PATH, pdf_filename)

        pages_merged = 0
        errors = []

        try:
            import fitz  # PyMuPDF

            merged_doc = fitz.open()

            # Pagina de capa
            cover = fitz.open()
            cover_page = cover.new_page(width=595, height=842)  # A4
            text_point = fitz.Point(50, 100)
            cover_page.insert_text(text_point, "Kit Documental", fontsize=24)
            cover_page.insert_text(fitz.Point(50, 140), f"Cliente: {client_name}", fontsize=14)
            cover_page.insert_text(
                fitz.Point(50, 170),
                f"Referencia: {kit.reference_month.strftime('%m/%Y')}",
                fontsize=14,
            )
            cover_page.insert_text(
                fitz.Point(50, 200),
                f"Documentos: {len(documents)}",
                fontsize=14,
            )
            cover_page.insert_text(
                fitz.Point(50, 230),
                f"Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}",
                fontsize=12,
            )

            # Indice na capa
            y_pos = 290
            cover_page.insert_text(fitz.Point(50, 270), "Indice:", fontsize=14)
            for i, doc in enumerate(documents, 1):
                if y_pos > 780:
                    cover_page = cover.new_page(width=595, height=842)
                    y_pos = 50
                cover_page.insert_text(
                    fitz.Point(60, y_pos),
                    f"{i}. {doc.document_name} ({doc.document_type})",
                    fontsize=10,
                )
                y_pos += 18

            merged_doc.insert_pdf(cover)
            cover.close()
            pages_merged += cover.page_count if hasattr(cover, "page_count") else 1

            # Mesclar PDFs
            for doc in documents:
                if not doc.file_path:
                    continue
                full_path = os.path.join(GED_STORAGE_BASE, doc.file_path)
                if os.path.exists(full_path) and full_path.lower().endswith(".pdf"):
                    try:
                        pdf_doc = fitz.open(full_path)
                        merged_doc.insert_pdf(pdf_doc)
                        pages_merged += pdf_doc.page_count
                        pdf_doc.close()
                    except Exception as e:
                        errors.append(f"{doc.document_name}: {str(e)}")
                        logger.warning("Erro ao mesclar PDF %s: %s", full_path, e)

            merged_doc.save(pdf_path)
            merged_doc.close()

        except ImportError:
            # Fallback sem PyMuPDF: gerar arquivo texto com indice
            logger.warning("PyMuPDF nao disponivel, gerando indice em texto")
            index_content = self._generate_index(kit, client_name, documents)
            pdf_path = pdf_path.replace(".pdf", ".txt")
            with open(pdf_path, "w", encoding="utf-8") as f:
                f.write(index_content)

        pdf_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0

        logger.info(
            "PDF consolidado gerado para kit %s: %s (%d paginas, %d bytes)",
            kit_id,
            pdf_path,
            pages_merged,
            pdf_size,
        )

        return {
            "kit_id": kit_id,
            "pdf_path": pdf_path,
            "pdf_filename": os.path.basename(pdf_path),
            "pages": pages_merged,
            "errors": errors,
            "pdf_size_bytes": pdf_size,
        }

    async def send_via_email(
        self,
        kit_id: str,
        email_addresses: list[str],
    ) -> dict:
        """Envia o kit por email para os destinatarios.

        Gera o ZIP se nao existir, registra o envio e atualiza status.
        Em ambiente de producao, integraria com servico de email (SES/SMTP).
        Atualmente registra a acao no log para implementacao futura.

        Args:
            kit_id: UUID do kit.
            email_addresses: Lista de emails destinatarios.

        Returns:
            Dicionario com status do envio.

        Raises:
            ValueError: Se kit nao encontrado ou emails vazios.
        """
        if not email_addresses:
            raise ValueError("E necessario informar ao menos um email destinatario")

        kit = await self._get_kit_or_raise(kit_id)

        # Gerar ZIP se necessario
        if not kit.zip_file_path or not os.path.exists(kit.zip_file_path):
            zip_result = await self.generate_zip(kit_id)
            kit.zip_file_path = zip_result["zip_path"]

        # Atualizar status de envio
        kit.status = KitStatus.ENVIADO
        kit.sent_at = datetime.utcnow()
        kit.sent_method = KitSendMethod.EMAIL
        kit.sent_to = ", ".join(email_addresses)

        await self.db.flush()

        # Registrar log de acesso
        await self.log_access(
            kit_id=kit_id,
            action=AccessAction.SENT,
            actor_type=ActorType.INTERNAL,
            actor_id=None,
            actor_name="Sistema",
            ip=None,
            user_agent=None,
            notes=f"Enviado por email para: {', '.join(email_addresses)}",
        )

        logger.info(
            "Kit %s enviado por email para %s",
            kit_id,
            ", ".join(email_addresses),
        )

        return {
            "kit_id": kit_id,
            "status": "sent",
            "method": "email",
            "recipients": email_addresses,
            "sent_at": kit.sent_at.isoformat(),
            "zip_path": kit.zip_file_path,
            "message": ("Kit registrado como enviado. Integracao com servico de email sera implementada com SES/SMTP."),
        }

    async def send_to_portal(self, kit_id: str) -> dict:
        """Disponibiliza o kit no portal do cliente.

        Marca o kit como enviado via portal e gera o ZIP se necessario.
        O portal do cliente usara os endpoints de download para acessar.

        Args:
            kit_id: UUID do kit.

        Returns:
            Dicionario com status da disponibilizacao.

        Raises:
            ValueError: Se kit nao encontrado ou cliente sem acesso ao portal.
        """
        kit = await self._get_kit_or_raise(kit_id)
        client = await self._get_client(str(kit.client_id))

        if client and not client.portal_access_enabled:
            raise ValueError(
                f"Cliente '{client.name}' nao possui acesso ao portal habilitado. "
                "Habilite o portal antes de disponibilizar kits."
            )

        # Gerar ZIP se necessario
        if not kit.zip_file_path or not os.path.exists(kit.zip_file_path):
            zip_result = await self.generate_zip(kit_id)
            kit.zip_file_path = zip_result["zip_path"]

        kit.status = KitStatus.ENVIADO
        kit.sent_at = datetime.utcnow()
        kit.sent_method = KitSendMethod.PORTAL
        kit.sent_to = f"Portal - {client.name}" if client else "Portal"

        await self.db.flush()

        await self.log_access(
            kit_id=kit_id,
            action=AccessAction.SENT,
            actor_type=ActorType.INTERNAL,
            actor_id=None,
            actor_name="Sistema",
            ip=None,
            user_agent=None,
            notes="Disponibilizado no portal do cliente",
        )

        logger.info("Kit %s disponibilizado no portal para %s", kit_id, client.name if client else "N/A")

        return {
            "kit_id": kit_id,
            "status": "available_in_portal",
            "method": "portal",
            "client_name": client.name if client else None,
            "sent_at": kit.sent_at.isoformat(),
        }

    async def get_download_url(self, kit_id: str, document_id: str | None = None) -> dict:
        """Gera URL/caminho de download para um documento ou kit completo.

        Args:
            kit_id: UUID do kit.
            document_id: UUID do documento especifico (opcional).

        Returns:
            Dicionario com caminho e metadados para download.

        Raises:
            ValueError: Se kit ou documento nao encontrado.
        """
        kit = await self._get_kit_or_raise(kit_id)

        if document_id:
            doc_result = await self.db.execute(
                select(KitDocument).where(
                    KitDocument.id == document_id,
                    KitDocument.kit_id == kit_id,
                )
            )
            doc = doc_result.scalar_one_or_none()
            if not doc:
                raise ValueError(f"Documento {document_id} nao encontrado no kit {kit_id}")

            file_path = doc.file_path
            if file_path:
                full_path = os.path.join(GED_STORAGE_BASE, file_path)
            else:
                full_path = None

            return {
                "kit_id": kit_id,
                "document_id": document_id,
                "document_name": doc.document_name,
                "file_path": full_path,
                "mime_type": doc.mime_type,
                "file_size_bytes": doc.file_size_bytes,
                "exists": os.path.exists(full_path) if full_path else False,
            }

        # Download do kit completo (ZIP)
        if not kit.zip_file_path or not os.path.exists(kit.zip_file_path):
            zip_result = await self.generate_zip(kit_id)
            kit.zip_file_path = zip_result["zip_path"]
            await self.db.flush()

        return {
            "kit_id": kit_id,
            "document_id": None,
            "document_name": os.path.basename(kit.zip_file_path),
            "file_path": kit.zip_file_path,
            "mime_type": "application/zip",
            "file_size_bytes": os.path.getsize(kit.zip_file_path) if os.path.exists(kit.zip_file_path) else 0,
            "exists": os.path.exists(kit.zip_file_path),
        }

    async def log_access(
        self,
        kit_id: str,
        action: str,
        actor_type: str,
        actor_id: str | None = None,
        actor_name: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        notes: str | None = None,
    ) -> KitAccessLog:
        """Registra um log de acesso/acao sobre um kit.

        Args:
            kit_id: UUID do kit.
            action: Acao realizada (viewed, downloaded, etc.).
            actor_type: Tipo do ator (internal, client).
            actor_id: ID do ator.
            actor_name: Nome do ator.
            ip: IP do ator.
            user_agent: User-Agent do navegador.
            notes: Observacoes.

        Returns:
            KitAccessLog criado.
        """
        log_entry = KitAccessLog(
            kit_id=kit_id,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_ip=ip,
            user_agent=user_agent,
            notes=notes,
        )
        self.db.add(log_entry)
        await self.db.flush()

        logger.debug(
            "Access log: kit=%s action=%s actor=%s",
            kit_id,
            action,
            actor_name or actor_id or "unknown",
        )
        return log_entry

    # --- Metodos auxiliares ---

    async def _get_kit_or_raise(self, kit_id: str) -> GedDocumentKit:
        """Busca kit por ID ou levanta ValueError."""
        result = await self.db.execute(select(GedDocumentKit).where(GedDocumentKit.id == kit_id))
        kit = result.scalar_one_or_none()
        if not kit:
            raise ValueError(f"Kit documental nao encontrado: {kit_id}")
        return kit

    async def _get_client(self, client_id: str) -> GedClient | None:
        """Busca cliente por ID."""
        result = await self.db.execute(select(GedClient).where(GedClient.id == client_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _generate_index(kit: GedDocumentKit, client_name: str, documents: list[KitDocument]) -> str:
        """Gera conteudo do indice do kit em formato texto."""
        lines = [
            "=" * 60,
            "KIT DOCUMENTAL",
            "=" * 60,
            f"Cliente: {client_name}",
            f"Referencia: {kit.reference_month.strftime('%m/%Y')}",
            f"Status: {kit.status}",
            f"Total de documentos: {len(documents)}",
            f"Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "-" * 60,
            "DOCUMENTOS",
            "-" * 60,
        ]

        for i, doc in enumerate(documents, 1):
            signed_text = "ASSINADO" if doc.is_signed else "Pendente"
            emp_text = f" (Func: {doc.employee_id})" if doc.employee_id else " (Empresa)"
            lines.append(f"{i:3d}. [{doc.document_type}] {doc.document_name}{emp_text} - {signed_text}")

        lines.extend(
            [
                "",
                "-" * 60,
                f"Assinados: {sum(1 for d in documents if d.is_signed)}/{len(documents)}",
                f"Completude: {kit.completion_percentage}%",
                "=" * 60,
            ]
        )

        return "\n".join(lines)
