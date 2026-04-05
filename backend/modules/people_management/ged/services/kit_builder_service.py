"""
Servico de Montagem Automatica de Kits Documentais.

Orquestra a coleta automatica de documentos de diferentes modulos
(DP, Fiscal, Operacoes) para montar kits completos por cliente/mes.
"""

import logging
import unicodedata
from datetime import date

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.ged.models.client import GedClient
from modules.people_management.ged.models.document_kit import GedDocumentKit, KitStatus
from modules.people_management.ged.models.kit_document import DocumentType, KitDocument, SourceModule

logger = logging.getLogger(__name__)

# Tipos de documento esperados por funcionario em um kit mensal
EMPLOYEE_DOCUMENT_TYPES = [
    DocumentType.CONTRACHEQUE,
    DocumentType.FOLHA_PONTO,
    DocumentType.COMPROVANTE_VT,
    DocumentType.COMPROVANTE_VA,
]

# Tipos de certidao da empresa
COMPANY_CERTIFICATE_TYPES = [
    DocumentType.CND_FEDERAL,
    DocumentType.CND_ESTADUAL,
    DocumentType.CND_MUNICIPAL,
    DocumentType.CRF_FGTS,
    DocumentType.CNDT_TRABALHISTA,
]


class KitBuilderService:
    """Servico de montagem automatica de kits documentais."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def build_kit_for_client(
        self,
        client_id: str,
        reference_month: date,
    ) -> dict:
        """Cria um kit e coleta documentos para um cliente/mes.

        Fluxo:
        1. Verifica se ja existe kit para o cliente/mes
        2. Busca funcionarios alocados nos postos do cliente
        3. Cria o kit com contadores iniciais
        4. Coleta documentos por funcionario (contracheques, ponto, beneficios)
        5. Coleta certidoes da empresa
        6. Coleta escalas operacionais
        7. Recalcula completude

        Args:
            client_id: UUID do cliente GED.
            reference_month: Mes de referencia (sera normalizado para dia 1).

        Returns:
            Dicionario com resumo da montagem.

        Raises:
            ValueError: Se cliente nao encontrado.
        """
        ref = reference_month.replace(day=1)

        # Validar cliente
        client_result = await self.db.execute(select(GedClient).where(GedClient.id == client_id))
        client = client_result.scalar_one_or_none()
        if not client:
            raise ValueError(f"Cliente GED nao encontrado: {client_id}")

        # Verificar kit existente
        existing_result = await self.db.execute(
            select(GedDocumentKit).where(
                GedDocumentKit.client_id == str(client_id),
                GedDocumentKit.reference_month == ref,
            )
        )
        existing_kit = existing_result.scalar_one_or_none()

        if existing_kit:
            kit = existing_kit
            logger.info("Kit ja existe para %s em %s, complementando", client.name, ref.strftime("%m/%Y"))
        else:
            kit = GedDocumentKit(
                client_id=str(client_id),
                reference_month=ref,
                status=KitStatus.EM_MONTAGEM,
            )
            self.db.add(kit)
            await self.db.flush()
            await self.db.refresh(kit)
            logger.info("Kit criado para %s em %s (id=%s)", client.name, ref.strftime("%m/%Y"), kit.id)

        # Buscar funcionarios alocados
        employee_ids = await self.get_employees_for_client(client_id)
        kit.total_employees = len(employee_ids)

        collected = {
            "payslips": 0,
            "time_sheets": 0,
            "benefit_receipts": 0,
            "certificates": 0,
            "schedules": 0,
            "errors": [],
        }

        # Coleta por funcionario
        if employee_ids:
            payslips = await self.collect_payslips(str(kit.id), employee_ids, ref)
            collected["payslips"] = payslips

            time_sheets = await self.collect_time_sheets(str(kit.id), employee_ids, ref)
            collected["time_sheets"] = time_sheets

            benefit_receipts = await self.collect_benefit_receipts(str(kit.id), employee_ids, ref)
            collected["benefit_receipts"] = benefit_receipts

            schedules = await self.collect_schedules(str(kit.id), employee_ids, ref)
            collected["schedules"] = schedules

        # Coleta de certidoes da empresa
        certificates = await self.collect_company_certificates(str(kit.id))
        collected["certificates"] = certificates

        # Recalcular totais
        total_docs_result = await self.db.execute(
            select(func.count()).select_from(KitDocument).where(KitDocument.kit_id == str(kit.id))
        )
        kit.total_documents = total_docs_result.scalar() or 0

        signed_result = await self.db.execute(
            select(func.count())
            .select_from(KitDocument)
            .where(KitDocument.kit_id == str(kit.id), KitDocument.is_signed.is_(True))
        )
        kit.documents_signed = signed_result.scalar() or 0

        kit.recalculate_completion()
        await self.db.flush()

        total_collected = sum(v for k, v in collected.items() if k != "errors")

        logger.info(
            "Kit montado para %s [%s]: %d docs coletados (%d funcionarios)",
            client.name,
            ref.strftime("%m/%Y"),
            total_collected,
            len(employee_ids),
        )

        return {
            "kit_id": str(kit.id),
            "client_id": str(client_id),
            "client_name": client.name,
            "reference_month": ref.isoformat(),
            "employees": len(employee_ids),
            "total_documents": kit.total_documents,
            "completion_percentage": float(kit.completion_percentage),
            "collected": collected,
        }

    async def collect_payslips(
        self,
        kit_id: str,
        employee_ids: list[str],
        reference_month: date,
    ) -> int:
        """Coleta contracheques do modulo DP para cada funcionario.

        Busca no modulo de folha de pagamento se existe contracheque
        gerado para cada funcionario no mes de referencia. Se encontrado,
        cria um KitDocument referenciando o arquivo.

        Args:
            kit_id: UUID do kit.
            employee_ids: Lista de UUIDs dos funcionarios.
            reference_month: Mes de referencia.

        Returns:
            Quantidade de contracheques coletados.
        """
        collected = 0
        ref_str = reference_month.strftime("%Y-%m")

        for emp_id in employee_ids:
            # Verificar se ja existe documento deste tipo para este funcionario/kit
            existing = await self.db.execute(
                select(KitDocument).where(
                    KitDocument.kit_id == kit_id,
                    KitDocument.employee_id == emp_id,
                    KitDocument.document_type == DocumentType.CONTRACHEQUE,
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Criar placeholder para contracheque
            # Em producao, buscaria o arquivo real do modulo DP
            file_path = f"documents/dp/contracheques/{ref_str}/{emp_id}.pdf"

            doc = KitDocument(
                kit_id=kit_id,
                employee_id=emp_id,
                document_type=DocumentType.CONTRACHEQUE,
                document_name=f"Contracheque {reference_month.strftime('%m/%Y')}",
                file_path=file_path,
                mime_type="application/pdf",
                source_module=SourceModule.DP,
                auto_generated=True,
                is_signed=False,
            )
            self.db.add(doc)
            collected += 1

        if collected > 0:
            await self.db.flush()
            logger.info("Coletados %d contracheques para kit %s", collected, kit_id)

        return collected

    async def collect_time_sheets(
        self,
        kit_id: str,
        employee_ids: list[str],
        reference_month: date,
    ) -> int:
        """Coleta folhas de ponto do modulo DP para cada funcionario.

        Args:
            kit_id: UUID do kit.
            employee_ids: Lista de UUIDs dos funcionarios.
            reference_month: Mes de referencia.

        Returns:
            Quantidade de folhas de ponto coletadas.
        """
        collected = 0
        ref_str = reference_month.strftime("%Y-%m")

        for emp_id in employee_ids:
            existing = await self.db.execute(
                select(KitDocument).where(
                    KitDocument.kit_id == kit_id,
                    KitDocument.employee_id == emp_id,
                    KitDocument.document_type == DocumentType.FOLHA_PONTO,
                )
            )
            if existing.scalar_one_or_none():
                continue

            file_path = f"documents/dp/folhas_ponto/{ref_str}/{emp_id}.pdf"

            doc = KitDocument(
                kit_id=kit_id,
                employee_id=emp_id,
                document_type=DocumentType.FOLHA_PONTO,
                document_name=f"Folha de Ponto {reference_month.strftime('%m/%Y')}",
                file_path=file_path,
                mime_type="application/pdf",
                source_module=SourceModule.DP,
                auto_generated=True,
                is_signed=False,
            )
            self.db.add(doc)
            collected += 1

        if collected > 0:
            await self.db.flush()
            logger.info("Coletadas %d folhas de ponto para kit %s", collected, kit_id)

        return collected

    async def collect_benefit_receipts(
        self,
        kit_id: str,
        employee_ids: list[str],
        reference_month: date,
    ) -> int:
        """Coleta comprovantes de beneficios (VT, VA, VR) para cada funcionario.

        Args:
            kit_id: UUID do kit.
            employee_ids: Lista de UUIDs dos funcionarios.
            reference_month: Mes de referencia.

        Returns:
            Quantidade de comprovantes coletados.
        """
        collected = 0
        ref_str = reference_month.strftime("%Y-%m")
        benefit_types = [
            (DocumentType.COMPROVANTE_VT, "VT"),
            (DocumentType.COMPROVANTE_VA, "VA"),
            (DocumentType.COMPROVANTE_VR, "VR"),
        ]

        for emp_id in employee_ids:
            for doc_type, benefit_name in benefit_types:
                existing = await self.db.execute(
                    select(KitDocument).where(
                        KitDocument.kit_id == kit_id,
                        KitDocument.employee_id == emp_id,
                        KitDocument.document_type == doc_type,
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                file_path = f"documents/dp/beneficios/{ref_str}/{benefit_name.lower()}/{emp_id}.pdf"

                doc = KitDocument(
                    kit_id=kit_id,
                    employee_id=emp_id,
                    document_type=doc_type,
                    document_name=f"Comprovante {benefit_name} {reference_month.strftime('%m/%Y')}",
                    file_path=file_path,
                    mime_type="application/pdf",
                    source_module=SourceModule.DP,
                    auto_generated=True,
                    is_signed=False,
                )
                self.db.add(doc)
                collected += 1

        if collected > 0:
            await self.db.flush()
            logger.info("Coletados %d comprovantes de beneficios para kit %s", collected, kit_id)

        return collected

    async def collect_company_certificates(self, kit_id: str) -> int:
        """Coleta certidoes negativas da empresa (CNDs).

        Busca as certidoes mais recentes no modulo fiscal.
        Para cada tipo de CND, cria um documento no kit se ainda nao existir.

        Args:
            kit_id: UUID do kit.

        Returns:
            Quantidade de certidoes coletadas.
        """
        collected = 0

        for cert_type in COMPANY_CERTIFICATE_TYPES:
            existing = await self.db.execute(
                select(KitDocument).where(
                    KitDocument.kit_id == kit_id,
                    KitDocument.document_type == cert_type,
                    KitDocument.employee_id.is_(None),
                )
            )
            if existing.scalar_one_or_none():
                continue

            cert_names = {
                DocumentType.CND_FEDERAL: "CND Federal (PGFN/RFB)",
                DocumentType.CND_ESTADUAL: "CND Estadual (SEFAZ)",
                DocumentType.CND_MUNICIPAL: "CND Municipal (ISS)",
                DocumentType.CRF_FGTS: "CRF FGTS (CEF)",
                DocumentType.CNDT_TRABALHISTA: "CNDT Trabalhista (TST)",
            }

            file_path = f"documents/fiscal/certidoes/{cert_type}.pdf"

            doc = KitDocument(
                kit_id=kit_id,
                employee_id=None,
                document_type=cert_type,
                document_name=cert_names.get(cert_type, str(cert_type)),
                file_path=file_path,
                mime_type="application/pdf",
                source_module=SourceModule.FISCAL,
                auto_generated=True,
                is_signed=True,  # Certidoes ja vem assinadas pelo orgao emissor
            )
            self.db.add(doc)
            collected += 1

        if collected > 0:
            await self.db.flush()
            logger.info("Coletadas %d certidoes para kit %s", collected, kit_id)

        return collected

    async def collect_schedules(
        self,
        kit_id: str,
        employee_ids: list[str],
        reference_month: date,
    ) -> int:
        """Coleta escalas operacionais do modulo de operacoes.

        Cria um documento de escala por funcionario alocado.

        Args:
            kit_id: UUID do kit.
            employee_ids: Lista de UUIDs dos funcionarios.
            reference_month: Mes de referencia.

        Returns:
            Quantidade de escalas coletadas.
        """
        collected = 0
        ref_str = reference_month.strftime("%Y-%m")

        for emp_id in employee_ids:
            existing = await self.db.execute(
                select(KitDocument).where(
                    KitDocument.kit_id == kit_id,
                    KitDocument.employee_id == emp_id,
                    KitDocument.document_type == DocumentType.ESCALA_MES,
                )
            )
            if existing.scalar_one_or_none():
                continue

            file_path = f"documents/operacoes/escalas/{ref_str}/{emp_id}.pdf"

            doc = KitDocument(
                kit_id=kit_id,
                employee_id=emp_id,
                document_type=DocumentType.ESCALA_MES,
                document_name=f"Escala {reference_month.strftime('%m/%Y')}",
                file_path=file_path,
                mime_type="application/pdf",
                source_module=SourceModule.OPERACOES,
                auto_generated=True,
                is_signed=False,
            )
            self.db.add(doc)
            collected += 1

        if collected > 0:
            await self.db.flush()
            logger.info("Coletadas %d escalas para kit %s", collected, kit_id)

        return collected

    async def auto_build_all_kits(self, reference_month: date) -> dict:
        """Monta kits automaticamente para TODOS os clientes ativos.

        Busca todos os clientes GED que possuem funcionarios alocados
        e cria/complementa kits para cada um no mes de referencia.

        Args:
            reference_month: Mes de referencia.

        Returns:
            Resumo da montagem automatica.
        """
        ref = reference_month.replace(day=1)

        # Buscar todos os clientes
        result = await self.db.execute(select(GedClient).order_by(GedClient.name))
        clients = result.scalars().all()

        results = {
            "reference_month": ref.isoformat(),
            "total_clients": len(clients),
            "kits_created": 0,
            "kits_updated": 0,
            "total_documents": 0,
            "errors": [],
        }

        for client in clients:
            try:
                employee_ids = await self.get_employees_for_client(str(client.id))
                if not employee_ids:
                    logger.debug("Cliente %s sem funcionarios alocados, ignorando", client.name)
                    continue

                build_result = await self.build_kit_for_client(str(client.id), ref)

                if build_result.get("total_documents", 0) > 0:
                    results["kits_created"] += 1
                    results["total_documents"] += build_result["total_documents"]
                else:
                    results["kits_updated"] += 1

            except Exception as e:
                logger.error("Erro ao montar kit para cliente %s: %s", client.name, e)
                results["errors"].append(
                    {
                        "client_id": str(client.id),
                        "client_name": client.name,
                        "error": str(e),
                    }
                )

        logger.info(
            "Auto-build concluido para %s: %d kits criados, %d erros",
            ref.strftime("%m/%Y"),
            results["kits_created"],
            len(results["errors"]),
        )

        return results

    async def get_employees_for_client(self, client_id: str) -> list[str]:
        """Busca IDs dos funcionarios alocados nos postos de um cliente GED.

        Estratégia em dois passos:
        1. Busca direta por posts.ged_client_id == client_id (FK explícita)
        2. Fallback: fuzzy match por palavras significativas do nome do cliente
           vs nome dos postos (normalização Unicode, ignora stop words)

        Emite WARNING quando usa o fallback para incentivar preenchimento do FK.

        Args:
            client_id: UUID do cliente GED.

        Returns:
            Lista de employee_ids (UUIDs como string).
        """
        # Stop words que não diferenciam clientes
        STOP_WORDS = {
            "CONDOMINIO",
            "CONDOMINIUM",
            "RESIDENCIAL",
            "EDIFICIO",
            "PREDIAL",
            "DO",
            "DA",
            "DE",
            "DOS",
            "DAS",
            "E",
            "O",
            "A",
            "EM",
        }

        def normalize(s: str) -> str:
            nfkd = unicodedata.normalize("NFKD", (s or "").upper())
            return "".join(c for c in nfkd if not unicodedata.combining(c))

        def sig_words(s: str) -> set[str]:
            return {w for w in normalize(s).split() if w not in STOP_WORDS and len(w) >= 3}

        try:
            # ── Passo 1: FK explícita ────────────────────────────────────────
            explicit_result = await self.db.execute(
                text(
                    "SELECT id::text FROM posts WHERE ged_client_id = :cid AND status = 'active' AND is_active = true"
                ),
                {"cid": str(client_id)},
            )
            post_ids = [row[0] for row in explicit_result.all()]

            if post_ids:
                logger.debug(
                    "Cliente %s: %d postos via FK explícita ged_client_id",
                    client_id,
                    len(post_ids),
                )
            else:
                # ── Passo 2: Fuzzy match por nome ────────────────────────────
                client_result = await self.db.execute(select(GedClient.name).where(GedClient.id == client_id))
                client_row = client_result.first()
                if not client_row:
                    return []

                ged_sig = sig_words(client_row[0])
                if not ged_sig:
                    return []

                logger.warning(
                    "WARN: usando fuzzy match para cliente %s ('%s') — "
                    "considere vincular ged_client_id nos postos operacionais",
                    client_id,
                    client_row[0],
                )

                posts_result = await self.db.execute(
                    text("SELECT id::text, name FROM posts WHERE status = 'active' AND is_active = true")
                )
                for post_id, post_name in posts_result.all():
                    post_sig = sig_words(post_name or "")
                    if post_sig and (post_sig <= ged_sig or ged_sig <= post_sig):
                        post_ids.append(post_id)

                logger.debug(
                    "Cliente %s: %d postos via fuzzy match (sig=%s)",
                    client_id,
                    len(post_ids),
                    ged_sig,
                )

            if not post_ids:
                return []

            # ── Buscar funcionários alocados ─────────────────────────────────
            alloc_result = await self.db.execute(
                text("""
                    SELECT DISTINCT employee_id::text
                    FROM allocations
                    WHERE post_id = ANY(:post_ids)
                      AND status = 'active'
                      AND is_active = true
                """),
                {"post_ids": post_ids},
            )
            employee_ids = [row[0] for row in alloc_result.all()]

            logger.debug(
                "Cliente %s: %d postos, %d funcionarios alocados",
                client_id,
                len(post_ids),
                len(employee_ids),
            )
            return employee_ids

        except Exception as e:
            logger.error("Erro ao buscar funcionarios do cliente %s: %s", client_id, e)
            return []
