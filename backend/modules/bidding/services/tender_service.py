"""
Service de Edital (Tender) - Licitacoes
=======================================
"""

import builtins
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from modules.bidding.models.tender import Tender, TenderStatus
from modules.bidding.repositories.tender_repository import TenderRepository
from modules.bidding.schemas.tender import (
    TenderCreate,
    TenderListResponse,
    TenderResponse,
    TenderSearchParams,
    TenderUpdate,
)

logger = logging.getLogger(__name__)


class TenderService:
    """Service para operacoes com editais."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TenderRepository(db)

    async def get(self, tender_id: UUID) -> TenderResponse | None:
        """Busca edital por ID."""
        tender = await self.repository.get_by_id(tender_id)
        if not tender:
            return None
        return self._to_response(tender)

    async def get_by_numero(self, numero: str, ano: int) -> TenderResponse | None:
        """Busca edital por numero e ano."""
        tender = await self.repository.get_by_numero(numero, ano)
        if not tender:
            return None
        return self._to_response(tender)

    async def list(self, params: TenderSearchParams) -> TenderListResponse:
        """Lista editais com filtros."""
        items, total = await self.repository.list(params)
        pages = (total + params.size - 1) // params.size

        return TenderListResponse(
            items=[self._to_response(t) for t in items], total=total, page=params.page, size=params.size, pages=pages
        )

    async def create(self, data: TenderCreate, user_id: UUID = None) -> TenderResponse:
        """Cria novo edital."""
        # Verifica duplicidade
        existing = await self.repository.get_by_numero(data.numero, data.ano)
        if existing:
            raise ValueError(f"Edital {data.numero}/{data.ano} ja existe")

        tender = await self.repository.create(data, user_id)
        return self._to_response(tender)

    async def update(self, tender_id: UUID, data: TenderUpdate, user_id: UUID = None) -> TenderResponse | None:
        """Atualiza edital."""
        tender = await self.repository.update(tender_id, data, user_id)
        if not tender:
            return None
        return self._to_response(tender)

    async def delete(self, tender_id: UUID) -> bool:
        """Remove edital."""
        return await self.repository.delete(tender_id)

    async def marcar_participacao(
        self, tender_id: UUID, participando: bool, motivo: str = None
    ) -> TenderResponse | None:
        """Marca interesse/participacao em edital."""
        update = TenderUpdate(
            participando=participando,
            interesse=participando,
            motivo_nao_participacao=motivo if not participando else None,
        )
        return await self.update(tender_id, update)

    async def alterar_status(self, tender_id: UUID, novo_status: str, user_id: UUID = None) -> TenderResponse | None:
        """Altera status do edital."""
        if novo_status not in [s.value for s in TenderStatus]:
            raise ValueError(f"Status invalido: {novo_status}")

        update = TenderUpdate(status=novo_status)
        return await self.update(tender_id, update, user_id)

    async def get_abertos(self, uf: str = "AM") -> builtins.list[TenderResponse]:
        """Lista editais abertos."""
        tenders = await self.repository.get_abertos(uf)
        return [self._to_response(t) for t in tenders]

    async def get_participando(self) -> builtins.list[TenderResponse]:
        """Lista editais que estamos participando."""
        tenders = await self.repository.get_participando()
        return [self._to_response(t) for t in tenders]

    async def get_por_segmento(self, segmento: str, uf: str = "AM") -> builtins.list[TenderResponse]:
        """Lista editais por segmento."""
        tenders = await self.repository.get_por_segmento(segmento, uf)
        return [self._to_response(t) for t in tenders]

    async def get_dashboard(self, uf: str = "AM") -> dict:
        """Retorna dados para dashboard."""
        contagem = await self.repository.count_by_status(uf)
        abertos = await self.repository.get_abertos(uf)
        participando = await self.repository.get_participando()

        return {
            "por_status": contagem,
            "total_abertos": len(abertos),
            "total_participando": len(participando),
            "proximos_editais": [self._to_response(t) for t in abertos[:5]],
        }

    async def add_document(self, tender_id: UUID, nome: str, tipo: str, arquivo_url: str = None, **kwargs):
        """Adiciona documento ao edital."""
        return await self.repository.add_document(tender_id, nome, tipo, arquivo_url, **kwargs)

    async def get_documents(self, tender_id: UUID) -> builtins.list[dict]:
        """Lista documentos do edital."""
        docs = await self.repository.get_documents(tender_id)
        return [
            {
                "id": str(d.id),
                "nome": d.nome,
                "tipo": d.tipo,
                "arquivo_url": d.arquivo_url,
                "obrigatorio": d.obrigatorio,
            }
            for d in docs
        ]

    def _to_response(self, tender: Tender) -> TenderResponse:
        """Converte model para response."""
        return TenderResponse(
            id=tender.id,
            numero=tender.numero,
            numero_processo=tender.numero_processo,
            ano=tender.ano,
            orgao_cnpj=tender.orgao_cnpj,
            orgao_nome=tender.orgao_nome,
            orgao_uf=tender.orgao_uf,
            orgao_municipio=tender.orgao_municipio,
            unidade_gestora=tender.unidade_gestora,
            modalidade=tender.modalidade,
            criterio_julgamento=tender.criterio_julgamento,
            tipo_contratacao=tender.tipo_contratacao,
            regime_execucao=tender.regime_execucao,
            objeto=tender.objeto,
            objeto_resumido=tender.objeto_resumido,
            valor_estimado=tender.valor_estimado,
            valor_homologado=tender.valor_homologado,
            data_publicacao=tender.data_publicacao,
            data_abertura=tender.data_abertura,
            data_encerramento_propostas=tender.data_encerramento_propostas,
            data_impugnacao_limite=tender.data_impugnacao_limite,
            data_esclarecimentos_limite=tender.data_esclarecimentos_limite,
            data_resultado=tender.data_resultado,
            data_homologacao=tender.data_homologacao,
            status=tender.status,
            ativo=tender.ativo,
            pncp_id=tender.pncp_id,
            pncp_link=tender.pncp_link,
            pncp_ultima_sync=tender.pncp_ultima_sync,
            participando=tender.participando,
            interesse=tender.interesse,
            motivo_nao_participacao=tender.motivo_nao_participacao,
            segmento=tender.segmento,
            tags=tender.tags or [],
            requisitos=tender.requisitos or [],
            documentos_exigidos=tender.documentos_exigidos or [],
            anexos=tender.anexos or [],
            esta_aberto=tender.esta_aberto,
            prazo_impugnacao_valido=tender.prazo_impugnacao_valido,
            dias_para_abertura=tender.dias_para_abertura,
            observacoes=tender.observacoes,
            fonte=tender.fonte,
            created_at=tender.created_at,
            updated_at=tender.updated_at,
        )
