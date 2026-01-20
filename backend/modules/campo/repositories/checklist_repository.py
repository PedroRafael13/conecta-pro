"""
Repository para Checklist.
"""

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import func, or_, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.campo.models.checklist import (
    ChecklistTemplate,
    ChecklistItem,
    ChecklistResposta,
    ChecklistPreenchido,
    TipoServico,
    TipoResposta,
)
from modules.campo.schemas.checklist import (
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistRespostaCreate,
    ChecklistPreenchidoCreate,
    TemplateFiltro,
)


class ChecklistRepository:
    """Repository para operacoes com Checklist."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    # =========================================================================
    # TEMPLATE - CRUD
    # =========================================================================

    async def create_template(self, data: ChecklistTemplateCreate, created_by: UUID = None) -> ChecklistTemplate:
        """Cria um novo template de checklist."""
        codigo = await self._gerar_codigo_template(data.tipo_servico)

        template = ChecklistTemplate(
            codigo=codigo,
            nome=data.nome,
            descricao=data.descricao,
            tipo_servico=data.tipo_servico,
            categoria_equipamento=data.categoria_equipamento,
            is_obrigatorio=data.is_obrigatorio,
            permite_itens_adicionais=data.permite_itens_adicionais,
            tempo_estimado_minutos=data.tempo_estimado_minutos,
            pontuacao_maxima=data.pontuacao_maxima,
            visivel_cliente=data.visivel_cliente,
            tags=data.tags or [],
            created_by=created_by,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_template_by_id(self, template_id: UUID) -> Optional[ChecklistTemplate]:
        """Busca template por ID."""
        result = await self.db.execute(
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.itens))
            .where(ChecklistTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_template_by_codigo(self, codigo: str) -> Optional[ChecklistTemplate]:
        """Busca template por codigo."""
        result = await self.db.execute(
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.itens))
            .where(ChecklistTemplate.codigo == codigo)
        )
        return result.scalar_one_or_none()

    async def update_template(self, template: ChecklistTemplate, data: ChecklistTemplateUpdate, updated_by: UUID = None) -> ChecklistTemplate:
        """Atualiza um template."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(template, field, value)

        template.updated_by = updated_by
        template.updated_at = datetime.utcnow()

        # Incrementar versao
        try:
            version_parts = template.versao.split(".")
            minor = int(version_parts[1]) + 1
            template.versao = f"{version_parts[0]}.{minor}"
        except (IndexError, ValueError):
            template.versao = "1.1"

        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete_template(self, template: ChecklistTemplate, soft: bool = True) -> bool:
        """Remove um template."""
        if soft:
            template.is_ativo = False
            template.updated_at = datetime.utcnow()
            await self.db.commit()
        else:
            await self.db.delete(template)
            await self.db.commit()
        return True

    async def list_templates(
        self,
        filtro: Optional[TemplateFiltro] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ChecklistTemplate], int]:
        """Lista templates com filtros."""
        query = select(ChecklistTemplate)

        if filtro:
            if filtro.is_ativo is not None:
                query = query.where(ChecklistTemplate.is_ativo == filtro.is_ativo)
            if filtro.tipo_servico:
                query = query.where(ChecklistTemplate.tipo_servico == filtro.tipo_servico)
            if filtro.categoria_equipamento:
                query = query.where(ChecklistTemplate.categoria_equipamento == filtro.categoria_equipamento)
            if filtro.is_obrigatorio is not None:
                query = query.where(ChecklistTemplate.is_obrigatorio == filtro.is_obrigatorio)
            if filtro.busca:
                search = f"%{filtro.busca}%"
                query = query.where(
                    or_(
                        ChecklistTemplate.codigo.ilike(search),
                        ChecklistTemplate.nome.ilike(search),
                    )
                )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginacao
        query = query.order_by(ChecklistTemplate.nome.asc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_templates_por_tipo_servico(self, tipo_servico: TipoServico) -> List[ChecklistTemplate]:
        """Lista templates ativos para um tipo de servico."""
        result = await self.db.execute(
            select(ChecklistTemplate)
            .where(
                and_(
                    ChecklistTemplate.tipo_servico == tipo_servico,
                    ChecklistTemplate.is_ativo == True
                )
            )
            .order_by(ChecklistTemplate.nome.asc())
        )
        return result.scalars().all()

    # =========================================================================
    # ITEM - CRUD
    # =========================================================================

    async def create_item(self, data: ChecklistItemCreate) -> ChecklistItem:
        """Cria um novo item de checklist."""
        # Determinar ordem se nao informada
        if not data.ordem:
            result = await self.db.execute(
                select(func.max(ChecklistItem.ordem))
                .where(ChecklistItem.template_id == data.template_id)
            )
            max_ordem = result.scalar() or 0
            ordem = max_ordem + 1
        else:
            ordem = data.ordem

        item = ChecklistItem(
            template_id=data.template_id,
            ordem=ordem,
            secao=data.secao,
            secao_ordem=data.secao_ordem,
            pergunta=data.pergunta,
            descricao=data.descricao,
            categoria=data.categoria,
            tipo_resposta=data.tipo_resposta,
            opcoes=[o.model_dump() for o in data.opcoes] if data.opcoes else [],
            valor_minimo=data.valor_minimo,
            valor_maximo=data.valor_maximo,
            unidade_medida=data.unidade_medida,
            valor_padrao=data.valor_padrao,
            obrigatorio=data.obrigatorio,
            condicional_item_id=data.condicional_item_id,
            condicional_valor=data.condicional_valor,
            pontos=data.pontos,
            peso=data.peso,
            gera_alerta=data.gera_alerta,
            alerta_condicao=data.alerta_condicao,
            alerta_mensagem=data.alerta_mensagem,
            alerta_severidade=data.alerta_severidade,
        )

        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_item_by_id(self, item_id: UUID) -> Optional[ChecklistItem]:
        """Busca item por ID."""
        result = await self.db.execute(
            select(ChecklistItem).where(ChecklistItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def update_item(self, item: ChecklistItem, data: ChecklistItemUpdate) -> ChecklistItem:
        """Atualiza um item."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "opcoes" and value:
                value = [o.model_dump() if hasattr(o, 'model_dump') else o for o in value]
            setattr(item, field, value)

        item.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item: ChecklistItem, soft: bool = True) -> bool:
        """Remove um item."""
        if soft:
            item.is_active = False
            item.updated_at = datetime.utcnow()
            await self.db.commit()
        else:
            await self.db.delete(item)
            await self.db.commit()
        return True

    async def list_itens_template(self, template_id: UUID) -> List[ChecklistItem]:
        """Lista itens de um template."""
        result = await self.db.execute(
            select(ChecklistItem)
            .where(
                and_(
                    ChecklistItem.template_id == template_id,
                    ChecklistItem.is_active == True
                )
            )
            .order_by(ChecklistItem.secao_ordem.asc(), ChecklistItem.ordem.asc())
        )
        return result.scalars().all()

    async def reordenar_itens(self, template_id: UUID, nova_ordem: List[UUID]) -> bool:
        """Reordena itens de um template."""
        for idx, item_id in enumerate(nova_ordem, 1):
            await self.db.execute(
                select(ChecklistItem)
                .where(
                    and_(
                        ChecklistItem.id == item_id,
                        ChecklistItem.template_id == template_id
                    )
                )
            )
            # Atualizar ordem
            result = await self.db.execute(
                select(ChecklistItem).where(ChecklistItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if item:
                item.ordem = idx

        await self.db.commit()
        return True

    # =========================================================================
    # RESPOSTA - CRUD
    # =========================================================================

    async def create_resposta(self, data: ChecklistRespostaCreate, respondido_por: UUID = None) -> ChecklistResposta:
        """Cria uma resposta de checklist."""
        resposta = ChecklistResposta(
            ordem_servico_id=data.ordem_servico_id,
            template_id=data.template_id,
            item_id=data.item_id,
            latitude=data.latitude,
            longitude=data.longitude,
            observacao=data.observacao,
            respondido_por=respondido_por,
        )

        # Buscar item para determinar tipo de resposta
        item = await self.get_item_by_id(data.item_id)
        if item:
            resposta.set_valor(item.tipo_resposta, data.valor)

            # Validar resposta
            valido, msg = item.validar_resposta(data.valor)
            resposta.is_valida = valido
            resposta.mensagem_validacao = msg

            # Verificar alerta
            alerta = item.verificar_alerta(data.valor)
            if alerta:
                resposta.gerou_alerta = True
                resposta.alerta_data = alerta

        # URLs de arquivos
        if data.foto_url:
            resposta.resposta_foto_url = data.foto_url
        if data.fotos_urls:
            resposta.resposta_fotos_urls = data.fotos_urls
        if data.assinatura_url:
            resposta.resposta_assinatura_url = data.assinatura_url

        self.db.add(resposta)
        await self.db.commit()
        await self.db.refresh(resposta)
        return resposta

    async def get_resposta_by_id(self, resposta_id: UUID) -> Optional[ChecklistResposta]:
        """Busca resposta por ID."""
        result = await self.db.execute(
            select(ChecklistResposta).where(ChecklistResposta.id == resposta_id)
        )
        return result.scalar_one_or_none()

    async def get_resposta_item_os(self, ordem_servico_id: UUID, item_id: UUID) -> Optional[ChecklistResposta]:
        """Busca resposta de um item especifico em uma OS."""
        result = await self.db.execute(
            select(ChecklistResposta)
            .where(
                and_(
                    ChecklistResposta.ordem_servico_id == ordem_servico_id,
                    ChecklistResposta.item_id == item_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_respostas_os(self, ordem_servico_id: UUID) -> List[ChecklistResposta]:
        """Lista todas respostas de uma OS."""
        result = await self.db.execute(
            select(ChecklistResposta)
            .where(ChecklistResposta.ordem_servico_id == ordem_servico_id)
            .order_by(ChecklistResposta.respondido_at.asc())
        )
        return result.scalars().all()

    # =========================================================================
    # PREENCHIDO - CRUD
    # =========================================================================

    async def create_preenchido(self, data: ChecklistPreenchidoCreate, preenchido_por: UUID = None) -> ChecklistPreenchido:
        """Inicia preenchimento de checklist para uma OS."""
        # Buscar template para obter totais
        template = await self.get_template_by_id(data.template_id)
        if not template:
            raise ValueError("Template nao encontrado")

        itens = await self.list_itens_template(data.template_id)

        preenchido = ChecklistPreenchido(
            ordem_servico_id=data.ordem_servico_id,
            template_id=data.template_id,
            preenchido_por=preenchido_por,
            preenchido_offline=data.preenchido_offline,
            total_itens=len(itens),
            itens_obrigatorios=sum(1 for i in itens if i.obrigatorio),
            pontuacao_maxima=sum(i.pontos for i in itens),
        )

        self.db.add(preenchido)
        await self.db.commit()
        await self.db.refresh(preenchido)
        return preenchido

    async def get_preenchido_by_os(self, ordem_servico_id: UUID) -> Optional[ChecklistPreenchido]:
        """Busca checklist preenchido de uma OS."""
        result = await self.db.execute(
            select(ChecklistPreenchido)
            .where(ChecklistPreenchido.ordem_servico_id == ordem_servico_id)
        )
        return result.scalar_one_or_none()

    async def atualizar_progresso_preenchido(self, preenchido: ChecklistPreenchido) -> ChecklistPreenchido:
        """Atualiza progresso do preenchimento."""
        # Contar respostas
        result = await self.db.execute(
            select(func.count())
            .select_from(ChecklistResposta)
            .where(ChecklistResposta.ordem_servico_id == preenchido.ordem_servico_id)
        )
        total_respondidos = result.scalar() or 0

        # Contar respostas de itens obrigatorios
        itens = await self.list_itens_template(preenchido.template_id)
        itens_obrigatorios_ids = [i.id for i in itens if i.obrigatorio]

        result = await self.db.execute(
            select(func.count())
            .select_from(ChecklistResposta)
            .where(
                and_(
                    ChecklistResposta.ordem_servico_id == preenchido.ordem_servico_id,
                    ChecklistResposta.item_id.in_(itens_obrigatorios_ids)
                )
            )
        )
        obrigatorios_respondidos = result.scalar() or 0

        # Somar pontuacao
        respostas = await self.list_respostas_os(preenchido.ordem_servico_id)
        pontuacao = 0
        alertas = []
        for resp in respostas:
            if resp.is_valida:
                # Buscar item para pegar pontos
                item = await self.get_item_by_id(resp.item_id)
                if item:
                    pontuacao += item.pontos
            if resp.gerou_alerta and resp.alerta_data:
                alertas.append(resp.alerta_data)

        preenchido.itens_respondidos = total_respondidos
        preenchido.itens_obrigatorios_respondidos = obrigatorios_respondidos
        preenchido.percentual_conclusao = (total_respondidos / preenchido.total_itens * 100) if preenchido.total_itens > 0 else 0
        preenchido.pontuacao_obtida = pontuacao
        preenchido.alertas = alertas
        preenchido.total_alertas = len(alertas)

        await self.db.commit()
        await self.db.refresh(preenchido)
        return preenchido

    async def concluir_preenchido(self, preenchido: ChecklistPreenchido, observacoes: str = None) -> ChecklistPreenchido:
        """Conclui preenchimento do checklist."""
        if preenchido.itens_obrigatorios_respondidos < preenchido.itens_obrigatorios:
            raise ValueError("Itens obrigatorios pendentes")

        preenchido.concluido = True
        preenchido.concluido_at = datetime.utcnow()
        preenchido.observacoes_finais = observacoes

        # Calcular conformidade
        if preenchido.pontuacao_maxima > 0:
            preenchido.percentual_conformidade = (preenchido.pontuacao_obtida / preenchido.pontuacao_maxima * 100)

        await self.db.commit()
        await self.db.refresh(preenchido)
        return preenchido

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _gerar_codigo_template(self, tipo_servico: TipoServico) -> str:
        """Gera codigo para template."""
        # Abreviacao do tipo
        abrevs = {
            TipoServico.INSTALACAO: "INST",
            TipoServico.MANUTENCAO_PREVENTIVA: "PREV",
            TipoServico.MANUTENCAO_CORRETIVA: "CORR",
            TipoServico.VISITA_TECNICA: "VTEC",
            TipoServico.VISTORIA: "VIST",
            TipoServico.RETIRADA: "RET",
            TipoServico.TROCA: "TRC",
            TipoServico.SUPORTE: "SUP",
            TipoServico.GERAL: "GER",
        }
        abrev = abrevs.get(tipo_servico, "GER")

        # Buscar ultimo codigo
        result = await self.db.execute(
            select(func.max(ChecklistTemplate.codigo))
            .where(ChecklistTemplate.codigo.like(f"CHK-{abrev}-%"))
        )
        ultimo = result.scalar()

        if ultimo:
            try:
                seq = int(ultimo.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"CHK-{abrev}-{seq:03d}"
