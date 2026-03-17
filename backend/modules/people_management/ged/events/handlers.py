"""
Event handlers do GED — integracoes bidirecionais com outros modulos.

Reagem a eventos do sistema (folha fechada, CND renovada, assinatura,
alocacao/desalocacao) e disparam acoes automaticas nos kits documentais.
"""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.ged.models.client import GedClient
from modules.people_management.ged.models.document_kit import GedDocumentKit, KitStatus
from modules.people_management.ged.models.kit_document import DocumentType, KitDocument, SourceModule

logger = logging.getLogger(__name__)


async def on_payroll_closed(db: AsyncSession, month: int, year: int) -> dict:
    """Handler: folha de pagamento fechada.

    Quando o DP fecha a folha de um mes, cria automaticamente kits
    documentais para todos os clientes ativos que ainda nao possuem
    kit para aquele mes.

    Args:
        db: Sessao do banco de dados.
        month: Mes de referencia (1-12).
        year: Ano de referencia.

    Returns:
        Resumo dos kits criados.
    """
    from modules.people_management.ged.services.kit_builder_service import KitBuilderService

    reference_month = date(year, month, 1)
    builder = KitBuilderService(db)

    logger.info("Evento on_payroll_closed: iniciando montagem de kits para %02d/%d", month, year)

    try:
        result = await builder.auto_build_all_kits(reference_month)
        await db.flush()

        logger.info(
            "Evento on_payroll_closed concluido: %d kits criados, %d erros",
            result.get("kits_created", 0),
            len(result.get("errors", [])),
        )
        return result

    except Exception as e:
        logger.error("Erro no evento on_payroll_closed: %s", e)
        return {"error": str(e), "kits_created": 0}


async def on_cnd_renewed(db: AsyncSession, cnd_type: str, file_path: str) -> dict:
    """Handler: certidao negativa renovada.

    Quando uma CND e renovada pelo modulo fiscal, atualiza o arquivo
    em todos os kits que estao EM_MONTAGEM, garantindo que o kit
    sempre contenha a versao mais recente da certidao.

    Args:
        db: Sessao do banco de dados.
        cnd_type: Tipo da certidao (cnd_federal, crf_fgts, etc.).
        file_path: Caminho do novo arquivo.

    Returns:
        Resumo das atualizacoes.
    """
    logger.info("Evento on_cnd_renewed: atualizando %s em kits EM_MONTAGEM", cnd_type)

    # Buscar todos os kits em montagem
    kits_result = await db.execute(select(GedDocumentKit).where(GedDocumentKit.status == KitStatus.EM_MONTAGEM))
    kits = kits_result.scalars().all()

    updated = 0
    created = 0

    for kit in kits:
        # Buscar documento existente do tipo CND neste kit
        doc_result = await db.execute(
            select(KitDocument).where(
                KitDocument.kit_id == str(kit.id),
                KitDocument.document_type == cnd_type,
                KitDocument.employee_id.is_(None),
            )
        )
        existing_doc = doc_result.scalar_one_or_none()

        if existing_doc:
            # Atualizar arquivo existente
            existing_doc.file_path = file_path
            existing_doc.is_signed = True  # CNDs ja vem validadas
            existing_doc.signature_hash = None  # Resetar hash para recalculo
            existing_doc.notes = (
                (existing_doc.notes or "")
                + f"\n[CND atualizada automaticamente em {date.today().strftime('%d/%m/%Y')}]"
            ).strip()
            updated += 1
        else:
            # Criar novo documento para o tipo de CND
            cert_names = {
                DocumentType.CND_FEDERAL: "CND Federal (PGFN/RFB)",
                DocumentType.CND_ESTADUAL: "CND Estadual (SEFAZ)",
                DocumentType.CND_MUNICIPAL: "CND Municipal (ISS)",
                DocumentType.CRF_FGTS: "CRF FGTS (CEF)",
                DocumentType.CNDT_TRABALHISTA: "CNDT Trabalhista (TST)",
            }
            doc_name = cert_names.get(cnd_type, f"Certidao {cnd_type}")

            new_doc = KitDocument(
                kit_id=str(kit.id),
                employee_id=None,
                document_type=cnd_type,
                document_name=doc_name,
                file_path=file_path,
                mime_type="application/pdf",
                source_module=SourceModule.FISCAL,
                auto_generated=True,
                is_signed=True,
            )
            db.add(new_doc)
            created += 1

    if updated > 0 or created > 0:
        await db.flush()

    logger.info(
        "Evento on_cnd_renewed concluido: %d atualizados, %d criados em %d kits",
        updated,
        created,
        len(kits),
    )

    return {
        "cnd_type": cnd_type,
        "kits_checked": len(kits),
        "documents_updated": updated,
        "documents_created": created,
    }


async def on_document_signed(db: AsyncSession, document_id: str, employee_id: str) -> dict:
    """Handler: documento assinado.

    Quando um documento e assinado digitalmente, recalcula o
    percentual de completude do kit correspondente.

    Args:
        db: Sessao do banco de dados.
        document_id: UUID do documento assinado.
        employee_id: UUID do funcionario que assinou.

    Returns:
        Resumo da atualizacao.
    """
    logger.info("Evento on_document_signed: doc=%s, employee=%s", document_id, employee_id)

    doc_result = await db.execute(select(KitDocument).where(KitDocument.id == document_id))
    doc = doc_result.scalar_one_or_none()
    if not doc:
        logger.warning("Documento %s nao encontrado no evento on_document_signed", document_id)
        return {"error": f"Documento {document_id} nao encontrado"}

    # Recalcular completude do kit
    from modules.people_management.ged.services.kit_service import KitService

    kit_service = KitService(db)
    try:
        kit_response = await kit_service.recalculate_kit_completion(str(doc.kit_id))
        await db.flush()

        logger.info(
            "Kit %s recalculado apos assinatura: %.2f%% completo",
            doc.kit_id,
            kit_response.completion_percentage,
        )

        return {
            "document_id": document_id,
            "kit_id": str(doc.kit_id),
            "completion_percentage": float(kit_response.completion_percentage),
            "status": kit_response.status,
        }

    except ValueError as e:
        logger.error("Erro ao recalcular kit %s: %s", doc.kit_id, e)
        return {"error": str(e)}


async def on_employee_allocated(db: AsyncSession, employee_id: str, post_id: str) -> dict:
    """Handler: funcionario alocado em um posto.

    Quando um funcionario e alocado, verifica se o posto pertence
    a algum cliente GED e adiciona os documentos do funcionario
    nos kits EM_MONTAGEM daquele cliente.

    Args:
        db: Sessao do banco de dados.
        employee_id: UUID do funcionario.
        post_id: UUID do posto.

    Returns:
        Resumo dos documentos adicionados.
    """
    logger.info("Evento on_employee_allocated: emp=%s, post=%s", employee_id, post_id)

    # Buscar o post para obter client_id
    client_id = await _get_client_id_from_post(db, post_id)
    if not client_id:
        logger.debug("Posto %s nao pertence a nenhum cliente GED", post_id)
        return {"message": "Posto nao vinculado a cliente GED", "documents_added": 0}

    # Verificar se o client_id corresponde a um GedClient
    ged_client_result = await db.execute(select(GedClient).where(GedClient.id == client_id))
    if not ged_client_result.scalar_one_or_none():
        logger.debug("Client %s do posto %s nao e um GedClient", client_id, post_id)
        return {"message": "Cliente do posto nao e GedClient", "documents_added": 0}

    # Buscar kits EM_MONTAGEM do cliente
    kits_result = await db.execute(
        select(GedDocumentKit).where(
            GedDocumentKit.client_id == client_id,
            GedDocumentKit.status == KitStatus.EM_MONTAGEM,
        )
    )
    kits = kits_result.scalars().all()

    documents_added = 0

    for kit in kits:
        # Adicionar documentos padrao do funcionario ao kit
        doc_types = [
            (DocumentType.CONTRACHEQUE, f"Contracheque {kit.reference_month.strftime('%m/%Y')}"),
            (DocumentType.FOLHA_PONTO, f"Folha de Ponto {kit.reference_month.strftime('%m/%Y')}"),
            (DocumentType.COMPROVANTE_VT, f"Comprovante VT {kit.reference_month.strftime('%m/%Y')}"),
        ]

        for doc_type, doc_name in doc_types:
            existing = await db.execute(
                select(KitDocument).where(
                    KitDocument.kit_id == str(kit.id),
                    KitDocument.employee_id == employee_id,
                    KitDocument.document_type == doc_type,
                )
            )
            if existing.scalar_one_or_none():
                continue

            ref_str = kit.reference_month.strftime("%Y-%m")
            new_doc = KitDocument(
                kit_id=str(kit.id),
                employee_id=employee_id,
                document_type=doc_type,
                document_name=doc_name,
                file_path=f"documents/dp/{doc_type}/{ref_str}/{employee_id}.pdf",
                mime_type="application/pdf",
                source_module=SourceModule.DP,
                auto_generated=True,
                is_signed=False,
            )
            db.add(new_doc)
            documents_added += 1

        # Atualizar contadores
        kit.total_employees = (kit.total_employees or 0) + 1

    if documents_added > 0:
        await db.flush()

    logger.info(
        "Evento on_employee_allocated: %d documentos adicionados em %d kits",
        documents_added,
        len(kits),
    )

    return {
        "employee_id": employee_id,
        "post_id": post_id,
        "client_id": client_id,
        "kits_updated": len(kits),
        "documents_added": documents_added,
    }


async def on_employee_deallocated(db: AsyncSession, employee_id: str, post_id: str) -> dict:
    """Handler: funcionario desalocado de um posto.

    Quando um funcionario e desalocado, remove seus documentos
    dos kits EM_MONTAGEM futuros (nao remove de kits ja enviados).

    Args:
        db: Sessao do banco de dados.
        employee_id: UUID do funcionario.
        post_id: UUID do posto.

    Returns:
        Resumo dos documentos removidos.
    """
    logger.info("Evento on_employee_deallocated: emp=%s, post=%s", employee_id, post_id)

    client_id = await _get_client_id_from_post(db, post_id)
    if not client_id:
        return {"message": "Posto nao vinculado a cliente GED", "documents_removed": 0}

    # Buscar kits EM_MONTAGEM do cliente (futuros)
    kits_result = await db.execute(
        select(GedDocumentKit).where(
            GedDocumentKit.client_id == client_id,
            GedDocumentKit.status == KitStatus.EM_MONTAGEM,
        )
    )
    kits = kits_result.scalars().all()

    documents_removed = 0

    for kit in kits:
        # Remover documentos auto-gerados do funcionario neste kit
        docs_result = await db.execute(
            select(KitDocument).where(
                KitDocument.kit_id == str(kit.id),
                KitDocument.employee_id == employee_id,
                KitDocument.auto_generated.is_(True),
            )
        )
        docs_to_remove = docs_result.scalars().all()

        for doc in docs_to_remove:
            await db.delete(doc)
            documents_removed += 1

        # Atualizar contador de funcionarios
        if docs_to_remove and kit.total_employees > 0:
            kit.total_employees = max(0, kit.total_employees - 1)

        # Recalcular completude
        kit.recalculate_completion()

    if documents_removed > 0:
        await db.flush()

    logger.info(
        "Evento on_employee_deallocated: %d documentos removidos de %d kits",
        documents_removed,
        len(kits),
    )

    return {
        "employee_id": employee_id,
        "post_id": post_id,
        "client_id": client_id,
        "kits_updated": len(kits),
        "documents_removed": documents_removed,
    }


# --- Funcoes auxiliares ---


async def _get_client_id_from_post(db: AsyncSession, post_id: str) -> str | None:
    """Busca o client_id de um posto de trabalho.

    Args:
        db: Sessao do banco.
        post_id: UUID do posto.

    Returns:
        client_id como string ou None.
    """
    try:
        from modules.operacional.models.post import Post

        result = await db.execute(select(Post.client_id).where(Post.id == post_id))
        row = result.scalar_one_or_none()
        return str(row) if row else None
    except ImportError:
        logger.warning("Modelo Post nao disponivel para buscar client_id")
        return None
    except Exception as e:
        logger.error("Erro ao buscar client_id do posto %s: %s", post_id, e)
        return None
