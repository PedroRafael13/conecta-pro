"""
Service de Proposta - Licitacoes
================================
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from modules.bidding.repositories.proposal_repository import ProposalRepository
from modules.bidding.models.proposal import BiddingProposal, ProposalStatus
from modules.bidding.schemas.proposal import (
    ProposalCreate, ProposalUpdate, ProposalResponse,
    ProposalCalculateBDI, ProposalBDIResponse, ProposalListResponse
)

logger = logging.getLogger(__name__)


class ProposalService:
    """Service para operacoes com propostas."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProposalRepository(db)

    async def get(self, proposal_id: UUID) -> Optional[ProposalResponse]:
        """Busca proposta por ID."""
        proposal = await self.repository.get_by_id(proposal_id)
        if not proposal:
            return None
        return self._to_response(proposal)

    async def get_by_tender(self, tender_id: UUID) -> List[ProposalResponse]:
        """Lista propostas de um edital."""
        proposals = await self.repository.get_by_tender(tender_id)
        return [self._to_response(p) for p in proposals]

    async def list(
        self,
        tender_id: UUID = None,
        status: str = None,
        page: int = 1,
        size: int = 50
    ) -> ProposalListResponse:
        """Lista propostas com filtros."""
        items, total = await self.repository.list(tender_id, status, page, size)

        return ProposalListResponse(
            items=[self._to_response(p) for p in items],
            total=total,
            page=page,
            size=size
        )

    async def create(
        self,
        data: ProposalCreate,
        user_id: UUID = None
    ) -> ProposalResponse:
        """Cria nova proposta."""
        proposal = await self.repository.create(data, user_id)
        return self._to_response(proposal)

    async def update(
        self,
        proposal_id: UUID,
        data: ProposalUpdate,
        user_id: UUID = None
    ) -> Optional[ProposalResponse]:
        """Atualiza proposta."""
        proposal = await self.repository.update(proposal_id, data, user_id)
        if not proposal:
            return None
        return self._to_response(proposal)

    async def delete(self, proposal_id: UUID) -> bool:
        """Remove proposta."""
        return await self.repository.delete(proposal_id)

    async def marcar_pronta(self, proposal_id: UUID) -> Optional[ProposalResponse]:
        """Marca proposta como pronta para envio."""
        proposal = await self.repository.get_by_id(proposal_id)
        if not proposal:
            return None

        if proposal.status != ProposalStatus.DRAFT.value:
            raise ValueError("Somente propostas em rascunho podem ser marcadas como prontas")

        # Validacoes
        if not proposal.valor_total or proposal.valor_total <= 0:
            raise ValueError("Proposta deve ter valor total")

        update = ProposalUpdate(status=ProposalStatus.READY.value)
        return await self.update(proposal_id, update)

    async def enviar(self, proposal_id: UUID) -> Optional[ProposalResponse]:
        """Envia proposta."""
        proposal = await self.repository.submit(proposal_id)
        if not proposal:
            return None
        return self._to_response(proposal)

    async def registrar_resultado(
        self,
        proposal_id: UUID,
        vencedora: bool,
        posicao: int = None,
        valor_final: Decimal = None
    ) -> Optional[ProposalResponse]:
        """Registra resultado da proposta."""
        status = ProposalStatus.WINNER.value if vencedora else ProposalStatus.CLASSIFIED.value
        if posicao == 2:
            status = ProposalStatus.SECOND_PLACE.value

        proposal = await self.repository.register_result(
            proposal_id, status, posicao, valor_final
        )
        if not proposal:
            return None
        return self._to_response(proposal)

    async def registrar_lance(
        self,
        proposal_id: UUID,
        valor: Decimal
    ) -> Optional[ProposalResponse]:
        """Registra lance em pregao."""
        proposal = await self.repository.add_lance(proposal_id, valor)
        if not proposal:
            return None
        return self._to_response(proposal)

    async def calcular_bdi(self, data: ProposalCalculateBDI) -> ProposalBDIResponse:
        """Calcula BDI da proposta."""
        # Componentes (custos indiretos)
        ac = data.administracao_central
        seg = data.seguro
        gar = data.garantia
        risco = data.risco
        df = data.despesas_financeiras
        lucro = data.lucro

        # Tributos
        tributos = data.pis + data.cofins + data.iss

        # Formula BDI (simplificada)
        # BDI = ((1 + AC + S + G + R + DF) * (1 + L)) / (1 - T) - 1
        custos_indiretos = 1 + (ac + seg + gar + risco + df) / 100
        fator_lucro = 1 + (lucro / 100)
        fator_tributos = 1 - (tributos / 100)

        bdi_fator = (custos_indiretos * fator_lucro) / fator_tributos
        bdi_percentual = (bdi_fator - 1) * 100

        valor_bdi = data.valor_base * (bdi_percentual / 100)
        valor_total = data.valor_base + valor_bdi

        return ProposalBDIResponse(
            valor_base=data.valor_base,
            bdi_percentual=round(bdi_percentual, 2),
            valor_bdi=round(valor_bdi, 2),
            valor_total=round(valor_total, 2),
            detalhamento={
                "administracao_central": float(ac),
                "seguro": float(seg),
                "garantia": float(gar),
                "risco": float(risco),
                "despesas_financeiras": float(df),
                "lucro": float(lucro),
                "pis": float(data.pis),
                "cofins": float(data.cofins),
                "iss": float(data.iss),
                "tributos_total": float(tributos),
                "custos_indiretos": float((custos_indiretos - 1) * 100)
            }
        )

    async def get_vencedoras(self) -> List[ProposalResponse]:
        """Lista propostas vencedoras."""
        proposals = await self.repository.get_vencedoras()
        return [self._to_response(p) for p in proposals]

    async def get_estatisticas(self) -> dict:
        """Retorna estatisticas de propostas."""
        contagem = await self.repository.count_by_status()
        vencedoras = await self.repository.get_vencedoras()

        total = sum(contagem.values())
        enviadas = contagem.get(ProposalStatus.SUBMITTED.value, 0)
        vencidas = len(vencedoras)

        return {
            "total_propostas": total,
            "propostas_enviadas": enviadas,
            "propostas_vencedoras": vencidas,
            "taxa_sucesso": (vencidas / enviadas * 100) if enviadas > 0 else 0,
            "por_status": contagem,
            "valor_total_vencidas": sum(p.valor_total for p in vencedoras)
        }

    def _to_response(self, proposal: BiddingProposal) -> ProposalResponse:
        """Converte model para response."""
        return ProposalResponse(
            id=proposal.id,
            tender_id=proposal.tender_id,
            numero=proposal.numero,
            versao=proposal.versao,
            status=proposal.status,
            ativo=proposal.ativo,
            valor_total=proposal.valor_total,
            valor_unitario=proposal.valor_unitario,
            desconto_percentual=proposal.desconto_percentual,
            bdi_percentual=proposal.bdi_percentual,
            bdi_detalhamento=proposal.bdi_detalhamento or {},
            encargos_sociais=proposal.encargos_sociais,
            encargos_detalhamento=proposal.encargos_detalhamento or {},
            itens=proposal.itens or [],
            posicao_classificacao=proposal.posicao_classificacao,
            valor_lance_final=proposal.valor_lance_final,
            historico_lances=proposal.historico_lances or [],
            arquivo_pdf_url=proposal.arquivo_pdf_url,
            arquivo_planilha_url=proposal.arquivo_planilha_url,
            data_envio=proposal.data_envio,
            data_resultado=proposal.data_resultado,
            valor_com_bdi=proposal.valor_com_bdi,
            justificativa_preco=proposal.justificativa_preco,
            observacoes=proposal.observacoes,
            created_at=proposal.created_at,
            updated_at=proposal.updated_at
        )
