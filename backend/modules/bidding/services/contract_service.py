"""
Service de Contrato Publico - Licitacoes
========================================
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from modules.bidding.repositories.contract_repository import ContractRepository
from modules.bidding.models.public_contract import PublicContract, ContractStatus
from modules.bidding.models.measurement import Measurement, MeasurementStatus
from modules.bidding.schemas.contract import (
    PublicContractCreate, PublicContractUpdate, PublicContractResponse,
    ContractAddendumCreate, ContractReadjustRequest, ContractReadjustResponse,
    ContractListResponse, MeasurementSummary
)

logger = logging.getLogger(__name__)


class ContractService:
    """Service para operacoes com contratos publicos."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ContractRepository(db)

    async def get(self, contract_id: UUID) -> Optional[PublicContractResponse]:
        """Busca contrato por ID."""
        contract = await self.repository.get_by_id(contract_id)
        if not contract:
            return None
        return self._to_response(contract)

    async def get_by_numero(
        self,
        numero: str,
        ano: int
    ) -> Optional[PublicContractResponse]:
        """Busca contrato por numero e ano."""
        contract = await self.repository.get_by_numero(numero, ano)
        if not contract:
            return None
        return self._to_response(contract)

    async def list(
        self,
        orgao_cnpj: str = None,
        status: str = None,
        vigente: bool = None,
        page: int = 1,
        size: int = 50
    ) -> ContractListResponse:
        """Lista contratos com filtros."""
        items, total = await self.repository.list(
            orgao_cnpj, status, vigente, page, size
        )

        totals = await self.repository.get_totals()

        return ContractListResponse(
            items=[self._to_response(c) for c in items],
            total=total,
            page=page,
            size=size,
            valor_total_contratos=totals['valor_total'],
            valor_total_executado=totals['total_executado']
        )

    async def create(
        self,
        data: PublicContractCreate,
        user_id: UUID = None
    ) -> PublicContractResponse:
        """Cria novo contrato."""
        # Verifica duplicidade
        existing = await self.repository.get_by_numero(
            data.numero_contrato, data.ano_contrato
        )
        if existing:
            raise ValueError(
                f"Contrato {data.numero_contrato}/{data.ano_contrato} ja existe"
            )

        contract = await self.repository.create(data, user_id)
        return self._to_response(contract)

    async def update(
        self,
        contract_id: UUID,
        data: PublicContractUpdate,
        user_id: UUID = None
    ) -> Optional[PublicContractResponse]:
        """Atualiza contrato."""
        contract = await self.repository.update(contract_id, data, user_id)
        if not contract:
            return None
        return self._to_response(contract)

    async def delete(self, contract_id: UUID) -> bool:
        """Remove contrato."""
        return await self.repository.delete(contract_id)

    async def add_addendum(
        self,
        contract_id: UUID,
        data: ContractAddendumCreate
    ) -> Optional[PublicContractResponse]:
        """Adiciona aditivo ao contrato."""
        contract = await self.repository.add_addendum(
            contract_id,
            numero=data.numero,
            tipo=data.tipo,
            objeto=data.objeto,
            valor=data.valor,
            prazo_dias=data.prazo_dias,
            data_assinatura=data.data_assinatura
        )
        if not contract:
            return None
        return self._to_response(contract)

    async def calcular_reajuste(
        self,
        contract_id: UUID,
        data: ContractReadjustRequest
    ) -> Optional[ContractReadjustResponse]:
        """Calcula reajuste do contrato."""
        contract = await self.repository.get_by_id(contract_id)
        if not contract:
            return None

        valor_reajuste = contract.valor_contrato * (data.percentual / 100)
        valor_novo = contract.valor_contrato + valor_reajuste

        return ContractReadjustResponse(
            contrato_id=contract.id,
            numero_contrato=contract.numero_contrato,
            valor_original=contract.valor_contrato,
            percentual_reajuste=data.percentual,
            valor_reajuste=valor_reajuste,
            valor_novo=valor_novo,
            indice_utilizado=contract.indice_reajuste or "IGPM",
            data_aplicacao=data.data_aplicacao or date.today()
        )

    async def aplicar_reajuste(
        self,
        contract_id: UUID,
        percentual: Decimal,
        data_aplicacao: date = None
    ) -> Optional[PublicContractResponse]:
        """Aplica reajuste ao contrato."""
        contract = await self.repository.get_by_id(contract_id)
        if not contract:
            return None

        contract.calcular_reajuste(percentual, data_aplicacao)
        await self.db.commit()
        await self.db.refresh(contract)

        return self._to_response(contract)

    async def get_expiring(self, days: int = 90) -> List[PublicContractResponse]:
        """Lista contratos vencendo."""
        contracts = await self.repository.get_expiring(days)
        return [self._to_response(c) for c in contracts]

    async def get_vigentes(self) -> List[PublicContractResponse]:
        """Lista contratos vigentes."""
        contracts = await self.repository.get_vigentes()
        return [self._to_response(c) for c in contracts]

    async def get_dashboard(self) -> dict:
        """Retorna dados para dashboard."""
        totals = await self.repository.get_totals()
        expiring = await self.repository.get_expiring(90)
        vigentes = await self.repository.get_vigentes()

        return {
            "total_contratos_vigentes": totals['total_contratos'],
            "valor_total": totals['valor_total'],
            "valor_executado": totals['total_executado'],
            "valor_pago": totals['total_pago'],
            "percentual_executado": (
                (totals['total_executado'] / totals['valor_total'] * 100)
                if totals['valor_total'] > 0 else 0
            ),
            "contratos_vencendo_90d": len(expiring),
            "proximos_vencimentos": [
                {
                    "id": str(c.id),
                    "numero": c.numero_contrato,
                    "orgao": c.orgao_nome,
                    "vencimento": c.data_vigencia_fim.isoformat(),
                    "dias_restantes": c.dias_para_vencer
                }
                for c in expiring[:5]
            ]
        }

    # Medicoes
    async def add_measurement(
        self,
        contract_id: UUID,
        competencia: str,
        periodo_inicio: date,
        periodo_fim: date,
        valor_bruto: Decimal,
        user_id: UUID = None
    ) -> dict:
        """Adiciona medicao ao contrato."""
        # Busca proxima medicao
        medicoes = await self.repository.get_measurements(contract_id)
        numero = (len(medicoes) + 1)

        measurement = await self.repository.add_measurement(
            contract_id=contract_id,
            numero=numero,
            competencia=competencia,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            valor_bruto=valor_bruto,
            user_id=user_id
        )

        return self._measurement_to_dict(measurement)

    async def get_measurements(self, contract_id: UUID) -> List[dict]:
        """Lista medicoes de um contrato."""
        measurements = await self.repository.get_measurements(contract_id)
        return [self._measurement_to_dict(m) for m in measurements]

    async def approve_measurement(
        self,
        measurement_id: UUID,
        aprovador: str,
        cargo: str = None,
        observacoes: str = None
    ) -> Optional[dict]:
        """Aprova medicao."""
        measurement = await self.repository.approve_measurement(
            measurement_id, aprovador, cargo, observacoes
        )
        if not measurement:
            return None
        return self._measurement_to_dict(measurement)

    def _to_response(self, contract: PublicContract) -> PublicContractResponse:
        """Converte model para response."""
        medicoes_summary = [
            MeasurementSummary(
                id=m.id,
                numero_medicao=m.numero_medicao,
                competencia=m.competencia,
                valor_bruto=m.valor_bruto,
                valor_liquido=m.valor_liquido,
                status=m.status,
                data_aprovacao=m.data_aprovacao
            )
            for m in (contract.medicoes or [])
        ]

        return PublicContractResponse(
            id=contract.id,
            tender_id=contract.tender_id,
            numero_contrato=contract.numero_contrato,
            ano_contrato=contract.ano_contrato,
            objeto=contract.objeto,
            objeto_resumido=contract.objeto_resumido,
            orgao_cnpj=contract.orgao_cnpj,
            orgao_nome=contract.orgao_nome,
            orgao_uf=contract.orgao_uf,
            unidade_gestora=contract.unidade_gestora,
            gestor_contrato=contract.gestor_contrato,
            fiscal_contrato=contract.fiscal_contrato,
            status=contract.status,
            ativo=contract.ativo,
            valor_contrato=contract.valor_contrato,
            valor_empenhado=contract.valor_empenhado,
            valor_executado=contract.valor_executado,
            valor_pago=contract.valor_pago,
            saldo_contrato=contract.saldo_contrato,
            numero_empenho=contract.numero_empenho,
            data_empenho=contract.data_empenho,
            nota_empenho_url=contract.nota_empenho_url,
            data_assinatura=contract.data_assinatura,
            data_publicacao=contract.data_publicacao,
            data_vigencia_inicio=contract.data_vigencia_inicio,
            data_vigencia_fim=contract.data_vigencia_fim,
            prazo_meses=contract.prazo_meses,
            indice_reajuste=contract.indice_reajuste,
            data_base_reajuste=contract.data_base_reajuste,
            ultimo_reajuste=contract.ultimo_reajuste,
            percentual_ultimo_reajuste=contract.percentual_ultimo_reajuste,
            garantia_tipo=contract.garantia_tipo,
            garantia_valor=contract.garantia_valor,
            garantia_percentual=contract.garantia_percentual,
            garantia_vencimento=contract.garantia_vencimento,
            garantia_documento_url=contract.garantia_documento_url,
            aditivos=contract.aditivos or [],
            quantidade_aditivos=contract.quantidade_aditivos,
            pncp_id=contract.pncp_id,
            pncp_link=contract.pncp_link,
            arquivo_contrato_url=contract.arquivo_contrato_url,
            arquivo_publicacao_url=contract.arquivo_publicacao_url,
            esta_vigente=contract.esta_vigente,
            dias_para_vencer=contract.dias_para_vencer,
            percentual_executado=contract.percentual_executado,
            saldo_a_executar=contract.saldo_a_executar,
            medicoes=medicoes_summary,
            observacoes=contract.observacoes,
            created_at=contract.created_at,
            updated_at=contract.updated_at
        )

    def _measurement_to_dict(self, m: Measurement) -> dict:
        """Converte medicao para dict."""
        return {
            "id": str(m.id),
            "contrato_id": str(m.contrato_id),
            "numero_medicao": m.numero_medicao,
            "competencia": m.competencia,
            "tipo": m.tipo,
            "periodo_inicio": m.periodo_inicio.isoformat() if m.periodo_inicio else None,
            "periodo_fim": m.periodo_fim.isoformat() if m.periodo_fim else None,
            "valor_bruto": float(m.valor_bruto),
            "valor_retencoes": float(m.valor_retencoes or 0),
            "valor_glosas": float(m.valor_glosas or 0),
            "valor_liquido": float(m.valor_liquido),
            "status": m.status,
            "data_envio": m.data_envio.isoformat() if m.data_envio else None,
            "data_aprovacao": m.data_aprovacao.isoformat() if m.data_aprovacao else None,
            "aprovador_nome": m.aprovador_nome,
            "nota_fiscal_numero": m.nota_fiscal_numero,
            "created_at": m.created_at.isoformat()
        }
