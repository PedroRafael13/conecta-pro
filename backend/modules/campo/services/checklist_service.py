"""
Service para Checklist.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.campo.models.checklist import (
    ChecklistItem,
    ChecklistPreenchido,
    ChecklistResposta,
    ChecklistTemplate,
    TipoServico,
)
from modules.campo.repositories.checklist_repository import ChecklistRepository
from modules.campo.schemas.checklist import (
    ChecklistComItens,
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    ChecklistPreenchidoCompleto,
    ChecklistPreenchidoCreate,
    ChecklistPreenchidoRead,
    ChecklistRespostaCreate,
    ChecklistRespostaRead,
    ChecklistTemplateCreate,
    ChecklistTemplateListItem,
    ChecklistTemplateRead,
    ChecklistTemplateUpdate,
    TemplateFiltro,
    TemplatePaginatedResponse,
    ValidacaoResult,
)


class ChecklistService:
    """Service para logica de negocio de Checklist."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o service."""
        self.db = db
        self.repository = ChecklistRepository(db)

    # =========================================================================
    # TEMPLATE - CRUD
    # =========================================================================

    async def criar_template(self, data: ChecklistTemplateCreate, created_by: UUID = None) -> ChecklistTemplate:
        """Cria um novo template de checklist."""
        return await self.repository.create_template(data, created_by)

    async def obter_template(self, template_id: UUID) -> ChecklistComItens | None:
        """Obtem template com seus itens."""
        template = await self.repository.get_template_by_id(template_id)
        if not template:
            return None

        itens = await self.repository.list_itens_template(template_id)

        return ChecklistComItens(
            template=ChecklistTemplateRead.model_validate(template),
            itens=[ChecklistItemRead.model_validate(item) for item in itens],
        )

    async def obter_template_por_codigo(self, codigo: str) -> ChecklistTemplate | None:
        """Obtem template por codigo."""
        return await self.repository.get_template_by_codigo(codigo)

    async def atualizar_template(
        self,
        template_id: UUID,
        data: ChecklistTemplateUpdate,
        updated_by: UUID = None,
    ) -> ChecklistTemplate | None:
        """Atualiza um template."""
        template = await self.repository.get_template_by_id(template_id)
        if not template:
            return None
        return await self.repository.update_template(template, data, updated_by)

    async def excluir_template(self, template_id: UUID) -> bool:
        """Exclui um template (soft delete)."""
        template = await self.repository.get_template_by_id(template_id)
        if not template:
            return False
        return await self.repository.delete_template(template)

    async def listar_templates(
        self,
        filtro: TemplateFiltro | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> TemplatePaginatedResponse:
        """Lista templates com paginacao."""
        skip = (page - 1) * page_size
        items, total = await self.repository.list_templates(filtro, skip, page_size)

        return TemplatePaginatedResponse(
            items=[ChecklistTemplateListItem.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    async def listar_templates_por_tipo(self, tipo_servico: TipoServico) -> list[ChecklistTemplate]:
        """Lista templates ativos para um tipo de servico."""
        return await self.repository.get_templates_por_tipo_servico(tipo_servico)

    async def clonar_template(
        self, template_id: UUID, novo_nome: str, created_by: UUID = None
    ) -> ChecklistTemplate | None:
        """Clona um template existente."""
        template = await self.repository.get_template_by_id(template_id)
        if not template:
            return None

        # Criar novo template
        novo = template.clonar(novo_nome)
        novo.created_by = created_by

        self.db.add(novo)
        await self.db.commit()
        await self.db.refresh(novo)

        # Gerar codigo
        novo.codigo = await self.repository._gerar_codigo_template(novo.tipo_servico)
        await self.db.commit()

        # Clonar itens
        itens = await self.repository.list_itens_template(template_id)
        for item in itens:
            novo_item = ChecklistItem(
                template_id=novo.id,
                ordem=item.ordem,
                secao=item.secao,
                secao_ordem=item.secao_ordem,
                pergunta=item.pergunta,
                descricao=item.descricao,
                categoria=item.categoria,
                tipo_resposta=item.tipo_resposta,
                opcoes=item.opcoes,
                valor_minimo=item.valor_minimo,
                valor_maximo=item.valor_maximo,
                unidade_medida=item.unidade_medida,
                valor_padrao=item.valor_padrao,
                obrigatorio=item.obrigatorio,
                pontos=item.pontos,
                peso=item.peso,
                gera_alerta=item.gera_alerta,
                alerta_condicao=item.alerta_condicao,
                alerta_mensagem=item.alerta_mensagem,
                alerta_severidade=item.alerta_severidade,
            )
            self.db.add(novo_item)

        await self.db.commit()
        await self.db.refresh(novo)
        return novo

    # =========================================================================
    # ITEM - CRUD
    # =========================================================================

    async def adicionar_item(self, data: ChecklistItemCreate) -> ChecklistItem:
        """Adiciona item a um template."""
        return await self.repository.create_item(data)

    async def obter_item(self, item_id: UUID) -> ChecklistItem | None:
        """Obtem item por ID."""
        return await self.repository.get_item_by_id(item_id)

    async def atualizar_item(self, item_id: UUID, data: ChecklistItemUpdate) -> ChecklistItem | None:
        """Atualiza um item."""
        item = await self.repository.get_item_by_id(item_id)
        if not item:
            return None
        return await self.repository.update_item(item, data)

    async def excluir_item(self, item_id: UUID) -> bool:
        """Exclui um item (soft delete)."""
        item = await self.repository.get_item_by_id(item_id)
        if not item:
            return False
        return await self.repository.delete_item(item)

    async def listar_itens_template(self, template_id: UUID) -> list[ChecklistItem]:
        """Lista itens de um template."""
        return await self.repository.list_itens_template(template_id)

    async def reordenar_itens(self, template_id: UUID, nova_ordem: list[UUID]) -> bool:
        """Reordena itens de um template."""
        return await self.repository.reordenar_itens(template_id, nova_ordem)

    # =========================================================================
    # PREENCHIMENTO DE CHECKLIST
    # =========================================================================

    async def iniciar_checklist(
        self,
        ordem_servico_id: UUID,
        template_id: UUID,
        preenchido_por: UUID = None,
        offline: bool = False,
    ) -> ChecklistPreenchido:
        """Inicia preenchimento de checklist para uma OS."""
        # Verificar se ja existe preenchimento
        existente = await self.repository.get_preenchido_by_os(ordem_servico_id)
        if existente:
            raise ValueError("Ja existe checklist iniciado para esta OS")

        data = ChecklistPreenchidoCreate(
            ordem_servico_id=ordem_servico_id,
            template_id=template_id,
            preenchido_offline=offline,
        )

        preenchido = await self.repository.create_preenchido(data, preenchido_por)
        preenchido.iniciar(preenchido_por)

        await self.db.commit()
        await self.db.refresh(preenchido)
        return preenchido

    async def responder_item(
        self,
        ordem_servico_id: UUID,
        item_id: UUID,
        valor: str | int | float | bool | list | dict | None,
        respondido_por: UUID = None,
        foto_url: str = None,
        fotos_urls: list[str] = None,
        assinatura_url: str = None,
        latitude: float = None,
        longitude: float = None,
        observacao: str = None,
    ) -> tuple[ChecklistResposta, ValidacaoResult]:
        """Responde um item do checklist."""
        # Buscar preenchido
        preenchido = await self.repository.get_preenchido_by_os(ordem_servico_id)
        if not preenchido:
            raise ValueError("Checklist nao iniciado para esta OS")

        # Verificar se item ja foi respondido
        existente = await self.repository.get_resposta_item_os(ordem_servico_id, item_id)
        if existente:
            # Atualizar resposta existente
            item = await self.repository.get_item_by_id(item_id)
            if item:
                existente.set_valor(item.tipo_resposta, valor)
                existente.respondido_at = datetime.utcnow()
                if foto_url:
                    existente.resposta_foto_url = foto_url
                if fotos_urls:
                    existente.resposta_fotos_urls = fotos_urls
                if assinatura_url:
                    existente.resposta_assinatura_url = assinatura_url
                if latitude:
                    existente.latitude = latitude
                if longitude:
                    existente.longitude = longitude
                if observacao:
                    existente.observacao = observacao

                # Revalidar
                valido, msg = item.validar_resposta(valor)
                existente.is_valida = valido
                existente.mensagem_validacao = msg

                # Verificar alerta
                alerta = item.verificar_alerta(valor)
                if alerta:
                    existente.gerou_alerta = True
                    existente.alerta_data = alerta

                await self.db.commit()
                await self.db.refresh(existente)

                # Atualizar progresso
                await self.repository.atualizar_progresso_preenchido(preenchido)

                return existente, ValidacaoResult(
                    valido=valido,
                    mensagem=msg,
                    alerta=alerta,
                )

        # Criar nova resposta
        data = ChecklistRespostaCreate(
            ordem_servico_id=ordem_servico_id,
            template_id=preenchido.template_id,
            item_id=item_id,
            valor=valor,
            foto_url=foto_url,
            fotos_urls=fotos_urls,
            assinatura_url=assinatura_url,
            latitude=latitude,
            longitude=longitude,
            observacao=observacao,
        )

        resposta = await self.repository.create_resposta(data, respondido_por)

        # Atualizar progresso
        await self.repository.atualizar_progresso_preenchido(preenchido)

        # Buscar item para validacao
        item = await self.repository.get_item_by_id(item_id)
        alerta = item.verificar_alerta(valor) if item else None

        return resposta, ValidacaoResult(
            valido=resposta.is_valida,
            mensagem=resposta.mensagem_validacao,
            alerta=alerta,
        )

    async def concluir_checklist(
        self,
        ordem_servico_id: UUID,
        observacoes: str = None,
    ) -> ChecklistPreenchido:
        """Conclui preenchimento do checklist."""
        preenchido = await self.repository.get_preenchido_by_os(ordem_servico_id)
        if not preenchido:
            raise ValueError("Checklist nao encontrado")

        return await self.repository.concluir_preenchido(preenchido, observacoes)

    async def obter_checklist_completo(
        self,
        ordem_servico_id: UUID,
    ) -> ChecklistPreenchidoCompleto | None:
        """Obtem checklist preenchido completo com template, itens e respostas."""
        preenchido = await self.repository.get_preenchido_by_os(ordem_servico_id)
        if not preenchido:
            return None

        template = await self.repository.get_template_by_id(preenchido.template_id)
        itens = await self.repository.list_itens_template(preenchido.template_id)
        respostas = await self.repository.list_respostas_os(ordem_servico_id)

        return ChecklistPreenchidoCompleto(
            preenchimento=ChecklistPreenchidoRead.model_validate(preenchido),
            template=ChecklistTemplateRead.model_validate(template),
            itens=[ChecklistItemRead.model_validate(item) for item in itens],
            respostas=[ChecklistRespostaRead.model_validate(resp) for resp in respostas],
        )

    async def obter_progresso_checklist(
        self,
        ordem_servico_id: UUID,
    ) -> ChecklistPreenchidoRead | None:
        """Obtem progresso do checklist."""
        preenchido = await self.repository.get_preenchido_by_os(ordem_servico_id)
        if not preenchido:
            return None

        # Atualizar progresso
        preenchido = await self.repository.atualizar_progresso_preenchido(preenchido)

        return ChecklistPreenchidoRead.model_validate(preenchido)
