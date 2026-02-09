"""
Repository para Visita.
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.campo.models.visita import StatusVisita, Visita
from modules.campo.schemas.visita import (
    VisitaCreate,
    VisitaDashboardStats,
    VisitaFiltro,
    VisitaUpdate,
)


class VisitaRepository:
    """Repository para operacoes com Visita."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    # =========================================================================
    # CRUD BASICO
    # =========================================================================

    async def create(self, data: VisitaCreate, created_by: UUID = None) -> Visita:
        """Cria uma nova visita."""
        numero = await self._gerar_numero()

        visita = Visita(
            numero=numero,
            tipo=data.tipo,
            origem=data.origem,
            responsavel_id=data.responsavel_id,
            responsavel_tipo=data.responsavel_tipo,
            responsavel_nome=data.responsavel_nome,
            cliente_id=data.cliente_id,
            contrato_id=data.contrato_id,
            is_prospect=data.is_prospect,
            prospect_nome=data.prospect_nome,
            prospect_empresa=data.prospect_empresa,
            prospect_cargo=data.prospect_cargo,
            prospect_telefone=data.prospect_telefone,
            prospect_celular=data.prospect_celular,
            prospect_email=data.prospect_email,
            prospect_cnpj=data.prospect_cnpj,
            prospect_cpf=data.prospect_cpf,
            lead_id=data.lead_id,
            oportunidade_id=data.oportunidade_id,
            endereco=data.endereco,
            endereco_complemento=data.endereco_complemento,
            bairro=data.bairro,
            cidade=data.cidade,
            estado=data.estado,
            cep=data.cep,
            latitude=data.latitude,
            longitude=data.longitude,
            ponto_referencia=data.ponto_referencia,
            data_visita=data.data_visita,
            horario_inicio=data.horario_inicio,
            horario_fim=data.horario_fim,
            duracao_prevista_minutos=data.duracao_prevista_minutos,
            objetivo=data.objetivo,
            tags=data.tags or [],
            created_by=created_by,
        )

        self.db.add(visita)
        await self.db.commit()
        await self.db.refresh(visita)
        return visita

    async def get_by_id(self, visita_id: UUID) -> Visita | None:
        """Busca visita por ID."""
        result = await self.db.execute(select(Visita).where(Visita.id == visita_id))
        return result.scalar_one_or_none()

    async def get_by_numero(self, numero: str) -> Visita | None:
        """Busca visita por numero."""
        result = await self.db.execute(select(Visita).where(Visita.numero == numero))
        return result.scalar_one_or_none()

    async def update(self, visita: Visita, data: VisitaUpdate, updated_by: UUID = None) -> Visita:
        """Atualiza uma visita."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "levantamento" and value and hasattr(value, "model_dump"):
                value = value.model_dump()
            if field == "necessidades_identificadas" and value:
                value = [n.model_dump() if hasattr(n, "model_dump") else n for n in value]
            setattr(visita, field, value)

        visita.updated_by = updated_by
        visita.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(visita)
        return visita

    async def delete(self, visita: Visita, soft: bool = True) -> bool:
        """Remove uma visita (soft delete por padrao)."""
        if soft:
            visita.is_active = False
            visita.updated_at = datetime.utcnow()
            await self.db.commit()
        else:
            await self.db.delete(visita)
            await self.db.commit()
        return True

    # =========================================================================
    # LISTAGEM E FILTROS
    # =========================================================================

    async def list_all(
        self,
        filtro: VisitaFiltro | None = None,
        skip: int = 0,
        limit: int = 50,
        order_by: str = "data_visita",
        order_desc: bool = True,
    ) -> tuple[list[Visita], int]:
        """Lista visitas com filtros e paginacao."""
        query = select(Visita).where(Visita.is_active)

        if filtro:
            if filtro.tipo:
                query = query.where(Visita.tipo == filtro.tipo)
            if filtro.status:
                query = query.where(Visita.status == filtro.status)
            if filtro.resultado:
                query = query.where(Visita.resultado == filtro.resultado)
            if filtro.origem:
                query = query.where(Visita.origem == filtro.origem)
            if filtro.responsavel_id:
                query = query.where(Visita.responsavel_id == filtro.responsavel_id)
            if filtro.responsavel_tipo:
                query = query.where(Visita.responsavel_tipo == filtro.responsavel_tipo)
            if filtro.cliente_id:
                query = query.where(Visita.cliente_id == filtro.cliente_id)
            if filtro.lead_id:
                query = query.where(Visita.lead_id == filtro.lead_id)
            if filtro.data_inicio:
                query = query.where(Visita.data_visita >= filtro.data_inicio)
            if filtro.data_fim:
                query = query.where(Visita.data_visita <= filtro.data_fim)
            if filtro.cidade:
                query = query.where(Visita.cidade.ilike(f"%{filtro.cidade}%"))
            if filtro.estado:
                query = query.where(Visita.estado == filtro.estado)
            if filtro.confirmada is not None:
                query = query.where(Visita.confirmada == filtro.confirmada)
            if filtro.proposta_gerada is not None:
                query = query.where(Visita.proposta_gerada == filtro.proposta_gerada)
            if filtro.contrato_fechado is not None:
                query = query.where(Visita.contrato_fechado == filtro.contrato_fechado)
            if filtro.busca:
                search = f"%{filtro.busca}%"
                query = query.where(
                    or_(
                        Visita.numero.ilike(search),
                        Visita.prospect_nome.ilike(search),
                        Visita.prospect_empresa.ilike(search),
                    )
                )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Ordenacao
        order_column = getattr(Visita, order_by, Visita.data_visita)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginacao
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def list_by_responsavel(
        self,
        responsavel_id: UUID,
        data: date | None = None,
        apenas_agendadas: bool = False,
    ) -> list[Visita]:
        """Lista visitas de um responsavel."""
        query = select(Visita).where(and_(Visita.responsavel_id == responsavel_id, Visita.is_active))

        if data:
            query = query.where(Visita.data_visita == data)

        if apenas_agendadas:
            query = query.where(Visita.status.in_([StatusVisita.AGENDADA, StatusVisita.CONFIRMADA]))

        query = query.order_by(Visita.horario_inicio.asc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_cliente(self, cliente_id: UUID, limit: int = 50) -> list[Visita]:
        """Lista visitas de um cliente."""
        result = await self.db.execute(
            select(Visita)
            .where(and_(Visita.cliente_id == cliente_id, Visita.is_active))
            .order_by(Visita.data_visita.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_by_lead(self, lead_id: UUID) -> list[Visita]:
        """Lista visitas de um lead."""
        result = await self.db.execute(
            select(Visita).where(and_(Visita.lead_id == lead_id, Visita.is_active)).order_by(Visita.data_visita.desc())
        )
        return result.scalars().all()

    async def list_pendentes_confirmacao(self, dias_antecedencia: int = 2) -> list[Visita]:
        """Lista visitas proximas que precisam confirmacao."""
        data_limite = date.today() + timedelta(days=dias_antecedencia)
        result = await self.db.execute(
            select(Visita)
            .where(
                and_(
                    Visita.status == StatusVisita.AGENDADA,
                    not Visita.confirmada,
                    Visita.data_visita <= data_limite,
                    Visita.data_visita >= date.today(),
                    Visita.is_active,
                )
            )
            .order_by(Visita.data_visita.asc())
        )
        return result.scalars().all()

    # =========================================================================
    # ESTATISTICAS
    # =========================================================================

    async def get_stats(
        self,
        responsavel_id: UUID | None = None,
        periodo_dias: int = 30,
    ) -> VisitaDashboardStats:
        """Obtem estatisticas de visitas."""
        hoje = date.today()
        inicio_periodo = hoje - timedelta(days=periodo_dias)

        base_filter = [Visita.is_active]
        if responsavel_id:
            base_filter.append(Visita.responsavel_id == responsavel_id)

        # Total agendadas (futuras)
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.status == StatusVisita.AGENDADA, Visita.data_visita >= hoje))
        )
        total_agendadas = result.scalar() or 0

        # Total confirmadas
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.status == StatusVisita.CONFIRMADA, Visita.data_visita >= hoje))
        )
        total_confirmadas = result.scalar() or 0

        # Total realizadas hoje
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.status == StatusVisita.REALIZADA, Visita.data_visita == hoje))
        )
        total_realizadas_hoje = result.scalar() or 0

        # Total realizadas no periodo
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.status == StatusVisita.REALIZADA, Visita.data_visita >= inicio_periodo))
        )
        total_realizadas_mes = result.scalar() or 0

        # Total canceladas no periodo
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.status == StatusVisita.CANCELADA, Visita.data_visita >= inicio_periodo))
        )
        total_canceladas_mes = result.scalar() or 0

        # Taxa de comparecimento
        total_periodo = total_realizadas_mes + total_canceladas_mes
        taxa_comparecimento = (total_realizadas_mes / total_periodo * 100) if total_periodo > 0 else None

        # Taxa de conversao para proposta
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(
                and_(
                    *base_filter,
                    Visita.status == StatusVisita.REALIZADA,
                    Visita.proposta_gerada,
                    Visita.data_visita >= inicio_periodo,
                )
            )
        )
        total_com_proposta = result.scalar() or 0
        taxa_conversao_proposta = (
            (total_com_proposta / total_realizadas_mes * 100) if total_realizadas_mes > 0 else None
        )

        # Taxa de conversao para contrato
        result = await self.db.execute(
            select(func.count())
            .select_from(Visita)
            .where(and_(*base_filter, Visita.contrato_fechado, Visita.data_visita >= inicio_periodo))
        )
        total_com_contrato = result.scalar() or 0
        taxa_conversao_contrato = (
            (total_com_contrato / total_realizadas_mes * 100) if total_realizadas_mes > 0 else None
        )

        # Interesse medio
        result = await self.db.execute(
            select(func.avg(Visita.interesse_nivel))
            .select_from(Visita)
            .where(and_(*base_filter, Visita.interesse_nivel.isnot(None), Visita.data_visita >= inicio_periodo))
        )
        interesse_medio = result.scalar()

        return VisitaDashboardStats(
            total_agendadas=total_agendadas,
            total_confirmadas=total_confirmadas,
            total_realizadas_hoje=total_realizadas_hoje,
            total_realizadas_mes=total_realizadas_mes,
            total_canceladas_mes=total_canceladas_mes,
            taxa_comparecimento=float(taxa_comparecimento) if taxa_comparecimento else None,
            taxa_conversao_proposta=float(taxa_conversao_proposta) if taxa_conversao_proposta else None,
            taxa_conversao_contrato=float(taxa_conversao_contrato) if taxa_conversao_contrato else None,
            interesse_medio=float(interesse_medio) if interesse_medio else None,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _gerar_numero(self) -> str:
        """Gera numero sequencial para visita."""
        ano = datetime.utcnow().year

        result = await self.db.execute(select(func.max(Visita.numero)).where(Visita.numero.like(f"VIS-{ano}-%")))
        ultimo = result.scalar()

        if ultimo:
            try:
                seq = int(ultimo.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"VIS-{ano}-{seq:05d}"
