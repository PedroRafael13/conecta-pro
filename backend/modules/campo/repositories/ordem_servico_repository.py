"""
Repository para Ordem de Servico.
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession

from modules.campo.models.ordem_servico import OrdemServico, StatusOS
from modules.campo.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoUpdate,
    OSDashboardStats,
    OSFiltro,
)


class OrdemServicoRepository:
    """Repository para operacoes com Ordem de Servico."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    # =========================================================================
    # CRUD BASICO
    # =========================================================================

    async def create(self, data: OrdemServicoCreate, created_by: UUID = None) -> OrdemServico:
        """Cria uma nova OS."""
        # Gerar numero sequencial
        numero = await self._gerar_numero()

        os = OrdemServico(
            numero=numero,
            tipo=data.tipo,
            prioridade=data.prioridade,
            origem=data.origem,
            cliente_id=data.cliente_id,
            contrato_id=data.contrato_id,
            contato_nome=data.contato_nome,
            contato_telefone=data.contato_telefone,
            contato_email=data.contato_email,
            endereco_servico=data.endereco_servico,
            endereco_complemento=data.endereco_complemento,
            bairro=data.bairro,
            cidade=data.cidade,
            estado=data.estado,
            cep=data.cep,
            latitude=data.latitude,
            longitude=data.longitude,
            ponto_referencia=data.ponto_referencia,
            data_agendada=data.data_agendada,
            horario_inicio_previsto=data.horario_inicio_previsto,
            horario_fim_previsto=data.horario_fim_previsto,
            duracao_estimada_minutos=data.duracao_estimada_minutos,
            janela_atendimento=data.janela_atendimento,
            tecnico_id=data.tecnico_id,
            tecnico_auxiliar_id=data.tecnico_auxiliar_id,
            titulo=data.titulo,
            descricao=data.descricao,
            problema_relatado=data.problema_relatado,
            instrucoes_cliente=data.instrucoes_cliente,
            equipamento_id=data.equipamento_id,
            equipamento_tipo=data.equipamento_tipo,
            equipamento_modelo=data.equipamento_modelo,
            equipamento_serie=data.equipamento_serie,
            checklist_template_id=data.checklist_template_id,
            materiais_previstos=[m.model_dump() for m in data.materiais_previstos] if data.materiais_previstos else [],
            valor_mao_obra=data.valor_mao_obra,
            valor_deslocamento=data.valor_deslocamento,
            is_cobrado=data.is_cobrado,
            is_garantia=data.is_garantia,
            is_cortesia=data.is_cortesia,
            motivo_isencao=data.motivo_isencao,
            sla_horas=data.sla_horas,
            ticket_origem_id=data.ticket_origem_id,
            ticket_sistema=data.ticket_sistema,
            tags=data.tags or [],
            created_by=created_by,
            status=StatusOS.AGENDADA if data.data_agendada else StatusOS.ABERTA,
        )

        # Definir SLA se informado
        if data.sla_horas:
            os.definir_sla(data.sla_horas)

        self.db.add(os)
        await self.db.commit()
        await self.db.refresh(os)
        return os

    async def get_by_id(self, os_id: UUID) -> OrdemServico | None:
        """Busca OS por ID."""
        result = await self.db.execute(select(OrdemServico).where(OrdemServico.id == os_id))
        return result.scalar_one_or_none()

    async def get_by_numero(self, numero: str) -> OrdemServico | None:
        """Busca OS por numero."""
        result = await self.db.execute(select(OrdemServico).where(OrdemServico.numero == numero))
        return result.scalar_one_or_none()

    async def update(self, os: OrdemServico, data: OrdemServicoUpdate, updated_by: UUID = None) -> OrdemServico:
        """Atualiza uma OS."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "materiais_previstos" and value:
                value = [m.model_dump() if hasattr(m, "model_dump") else m for m in value]
            if field == "materiais_utilizados" and value:
                value = [m.model_dump() if hasattr(m, "model_dump") else m for m in value]
            setattr(os, field, value)

        os.updated_by = updated_by
        os.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(os)
        return os

    async def delete(self, os: OrdemServico, soft: bool = True) -> bool:
        """Remove uma OS (soft delete por padrao)."""
        if soft:
            os.is_active = False
            os.updated_at = datetime.utcnow()
            await self.db.commit()
        else:
            await self.db.delete(os)
            await self.db.commit()
        return True

    # =========================================================================
    # LISTAGEM E FILTROS
    # =========================================================================

    async def list_all(
        self,
        filtro: OSFiltro | None = None,
        skip: int = 0,
        limit: int = 50,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[OrdemServico], int]:
        """Lista OS com filtros e paginacao."""
        query = select(OrdemServico).where(OrdemServico.is_active)

        if filtro:
            if filtro.tipo:
                query = query.where(OrdemServico.tipo == filtro.tipo)
            if filtro.status:
                query = query.where(OrdemServico.status == filtro.status)
            if filtro.prioridade:
                query = query.where(OrdemServico.prioridade == filtro.prioridade)
            if filtro.origem:
                query = query.where(OrdemServico.origem == filtro.origem)
            if filtro.cliente_id:
                query = query.where(OrdemServico.cliente_id == filtro.cliente_id)
            if filtro.contrato_id:
                query = query.where(OrdemServico.contrato_id == filtro.contrato_id)
            if filtro.tecnico_id:
                query = query.where(OrdemServico.tecnico_id == filtro.tecnico_id)
            if filtro.data_inicio:
                query = query.where(OrdemServico.data_agendada >= filtro.data_inicio)
            if filtro.data_fim:
                query = query.where(OrdemServico.data_agendada <= filtro.data_fim)
            if filtro.cidade:
                query = query.where(OrdemServico.cidade.ilike(f"%{filtro.cidade}%"))
            if filtro.estado:
                query = query.where(OrdemServico.estado == filtro.estado)
            if filtro.sla_vencido is True:
                query = query.where(
                    and_(
                        OrdemServico.sla_vencimento.isnot(None),
                        OrdemServico.sla_vencimento < datetime.utcnow(),
                        OrdemServico.status.notin_([StatusOS.CONCLUIDA, StatusOS.CANCELADA]),
                    )
                )
            if filtro.avaliado is True:
                query = query.where(OrdemServico.avaliacao_nota.isnot(None))
            if filtro.avaliado is False:
                query = query.where(OrdemServico.avaliacao_nota.is_(None))
            if filtro.faturado is not None:
                query = query.where(OrdemServico.faturado == filtro.faturado)
            if filtro.busca:
                search = f"%{filtro.busca}%"
                query = query.where(
                    or_(
                        OrdemServico.numero.ilike(search),
                        OrdemServico.titulo.ilike(search),
                        OrdemServico.descricao.ilike(search),
                    )
                )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Ordenacao
        _valid_order_column_cols = {c.key for c in sa_inspect(OrdemServico).mapper.column_attrs}
        order_column = getattr(OrdemServico, order_by if order_by in _valid_order_column_cols else "created_at")
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginacao
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def list_by_cliente(self, cliente_id: UUID, limit: int = 50) -> list[OrdemServico]:
        """Lista OS de um cliente."""
        result = await self.db.execute(
            select(OrdemServico)
            .where(and_(OrdemServico.cliente_id == cliente_id, OrdemServico.is_active))
            .order_by(OrdemServico.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_by_tecnico(
        self,
        tecnico_id: UUID,
        data: date | None = None,
        apenas_abertas: bool = False,
    ) -> list[OrdemServico]:
        """Lista OS de um tecnico."""
        query = select(OrdemServico).where(and_(OrdemServico.tecnico_id == tecnico_id, OrdemServico.is_active))

        if data:
            query = query.where(OrdemServico.data_agendada == data)

        if apenas_abertas:
            query = query.where(
                OrdemServico.status.in_(
                    [
                        StatusOS.ABERTA,
                        StatusOS.AGENDADA,
                        StatusOS.EM_DESLOCAMENTO,
                        StatusOS.EM_ANDAMENTO,
                        StatusOS.PAUSADA,
                    ]
                )
            )

        query = query.order_by(OrdemServico.horario_inicio_previsto.asc().nullslast())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_atrasadas(self, limit: int = 100) -> list[OrdemServico]:
        """Lista OS com SLA vencido."""
        result = await self.db.execute(
            select(OrdemServico)
            .where(
                and_(
                    OrdemServico.sla_vencimento < datetime.utcnow(),
                    OrdemServico.status.notin_([StatusOS.CONCLUIDA, StatusOS.CANCELADA]),
                    OrdemServico.is_active,
                )
            )
            .order_by(OrdemServico.sla_vencimento.asc())
            .limit(limit)
        )
        return result.scalars().all()

    # =========================================================================
    # ESTATISTICAS
    # =========================================================================

    async def get_stats(
        self,
        cliente_id: UUID | None = None,
        tecnico_id: UUID | None = None,
        periodo_dias: int = 30,
    ) -> OSDashboardStats:
        """Obtem estatisticas de OS."""
        hoje = date.today()
        inicio_periodo = hoje - timedelta(days=periodo_dias)

        base_filter = [OrdemServico.is_active]
        if cliente_id:
            base_filter.append(OrdemServico.cliente_id == cliente_id)
        if tecnico_id:
            base_filter.append(OrdemServico.tecnico_id == tecnico_id)

        # Total abertas
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(and_(*base_filter, OrdemServico.status == StatusOS.ABERTA))
        )
        total_abertas = result.scalar() or 0

        # Total agendadas
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(and_(*base_filter, OrdemServico.status == StatusOS.AGENDADA))
        )
        total_agendadas = result.scalar() or 0

        # Total em andamento
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(and_(*base_filter, OrdemServico.status.in_([StatusOS.EM_DESLOCAMENTO, StatusOS.EM_ANDAMENTO])))
        )
        total_em_andamento = result.scalar() or 0

        # Total concluidas hoje
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                and_(
                    *base_filter,
                    OrdemServico.status == StatusOS.CONCLUIDA,
                    func.date(OrdemServico.data_conclusao) == hoje,
                )
            )
        )
        total_concluidas_hoje = result.scalar() or 0

        # Total concluidas no periodo
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                and_(
                    *base_filter,
                    OrdemServico.status == StatusOS.CONCLUIDA,
                    func.date(OrdemServico.data_conclusao) >= inicio_periodo,
                )
            )
        )
        total_concluidas_mes = result.scalar() or 0

        # Total atrasadas
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                and_(
                    *base_filter,
                    OrdemServico.sla_vencimento < datetime.utcnow(),
                    OrdemServico.status.notin_([StatusOS.CONCLUIDA, StatusOS.CANCELADA]),
                )
            )
        )
        total_atrasadas = result.scalar() or 0

        # Tempo medio de atendimento
        result = await self.db.execute(
            select(func.avg(OrdemServico.tempo_execucao_minutos))
            .select_from(OrdemServico)
            .where(
                and_(
                    *base_filter,
                    OrdemServico.status == StatusOS.CONCLUIDA,
                    OrdemServico.tempo_execucao_minutos.isnot(None),
                    func.date(OrdemServico.data_conclusao) >= inicio_periodo,
                )
            )
        )
        tempo_medio = result.scalar()

        # Avaliacao media
        result = await self.db.execute(
            select(func.avg(OrdemServico.avaliacao_nota))
            .select_from(OrdemServico)
            .where(
                and_(
                    *base_filter,
                    OrdemServico.avaliacao_nota.isnot(None),
                    func.date(OrdemServico.data_conclusao) >= inicio_periodo,
                )
            )
        )
        avaliacao_media = result.scalar()

        return OSDashboardStats(
            total_abertas=total_abertas,
            total_agendadas=total_agendadas,
            total_em_andamento=total_em_andamento,
            total_concluidas_hoje=total_concluidas_hoje,
            total_concluidas_mes=total_concluidas_mes,
            total_atrasadas=total_atrasadas,
            tempo_medio_atendimento_minutos=float(tempo_medio) if tempo_medio else None,
            avaliacao_media=float(avaliacao_media) if avaliacao_media else None,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _gerar_numero(self) -> str:
        """Gera numero sequencial para OS."""
        ano = datetime.utcnow().year

        # Buscar ultimo numero do ano
        result = await self.db.execute(
            select(func.max(OrdemServico.numero)).where(OrdemServico.numero.like(f"OS-{ano}-%"))
        )
        ultimo = result.scalar()

        if ultimo:
            try:
                seq = int(ultimo.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"OS-{ano}-{seq:05d}"
