"""
Serviço de Integração com Estoque para Campo.

Fornece funcionalidades para:
- Requisição de materiais para OS
- Verificação de disponibilidade
- Baixa automática ao concluir OS
- Alertas de estoque baixo
- Histórico de movimentações
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TipoMovimentacao(StrEnum):
    """Tipos de movimentação de estoque."""

    REQUISICAO = "requisicao"  # Solicitação de material para OS
    BAIXA = "baixa"  # Baixa efetiva após uso
    DEVOLUCAO = "devolucao"  # Devolução de material não usado
    TRANSFERENCIA = "transferencia"  # Transferência entre técnicos


class StatusRequisicao(StrEnum):
    """Status da requisição de material."""

    PENDENTE = "pendente"
    APROVADA = "aprovada"
    SEPARADA = "separada"
    ENTREGUE = "entregue"
    CANCELADA = "cancelada"
    PARCIAL = "parcial"


class ItemRequisicao(BaseModel):
    """Item de requisição de material."""

    produto_id: UUID
    produto_codigo: str
    produto_nome: str
    quantidade_solicitada: Decimal
    quantidade_aprovada: Decimal | None = None
    quantidade_entregue: Decimal | None = None
    unidade: str = "UN"
    observacao: str | None = None


class RequisicaoMaterial(BaseModel):
    """Requisição de materiais para OS."""

    id: UUID
    ordem_servico_id: UUID
    tecnico_id: UUID
    status: StatusRequisicao
    itens: list[ItemRequisicao]
    data_solicitacao: datetime
    data_aprovacao: datetime | None = None
    data_entrega: datetime | None = None
    aprovador_id: UUID | None = None
    observacoes: str | None = None


class EstoqueIntegrationService:
    """Serviço de integração com estoque para Campo."""

    def __init__(self, db: Session):
        self.db = db
        # Cache em memória para requisições (em produção, usar banco)
        self._requisicoes: dict[UUID, RequisicaoMaterial] = {}
        self._movimentacoes: list[dict] = []
        self._estoque_cache: dict[UUID, dict] = {}

    # =========================================================================
    # REQUISIÇÃO DE MATERIAIS
    # =========================================================================

    def criar_requisicao(
        self,
        ordem_servico_id: UUID,
        tecnico_id: UUID,
        itens: list[dict[str, Any]],
        observacoes: str | None = None,
    ) -> RequisicaoMaterial:
        """
        Cria requisição de materiais para uma OS.

        Args:
            ordem_servico_id: ID da ordem de serviço
            tecnico_id: ID do técnico solicitante
            itens: Lista de itens [{produto_id, quantidade, ...}]
            observacoes: Observações da requisição

        Returns:
            RequisicaoMaterial criada
        """
        # Verificar se OS existe
        from modules.campo.models.ordem_servico import OrdemServico, StatusOS

        os = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()

        if not os:
            raise ValueError(f"Ordem de Serviço {ordem_servico_id} não encontrada")

        if os.status in [StatusOS.CONCLUIDA, StatusOS.CANCELADA]:
            raise ValueError(f"OS {ordem_servico_id} já está {os.status.value}")

        # Converter itens
        itens_req = []
        for item in itens:
            # Buscar dados do produto do estoque
            produto = self._get_produto(item.get("produto_id"))

            item_req = ItemRequisicao(
                produto_id=item.get("produto_id"),
                produto_codigo=produto.get("codigo", "N/A"),
                produto_nome=produto.get("nome", "Produto"),
                quantidade_solicitada=Decimal(str(item.get("quantidade", 1))),
                unidade=produto.get("unidade", "UN"),
                observacao=item.get("observacao"),
            )
            itens_req.append(item_req)

        # Criar requisição
        requisicao = RequisicaoMaterial(
            id=uuid4(),
            ordem_servico_id=ordem_servico_id,
            tecnico_id=tecnico_id,
            status=StatusRequisicao.PENDENTE,
            itens=itens_req,
            data_solicitacao=datetime.now(),
            observacoes=observacoes,
        )

        # Salvar (em memória por enquanto)
        self._requisicoes[requisicao.id] = requisicao

        # Atualizar materiais previstos na OS
        if hasattr(os, "materiais_previstos"):
            materiais = os.materiais_previstos or []
            for item in itens_req:
                materiais.append(
                    {
                        "produto_id": str(item.produto_id),
                        "codigo": item.produto_codigo,
                        "nome": item.produto_nome,
                        "quantidade": float(item.quantidade_solicitada),
                        "unidade": item.unidade,
                        "requisicao_id": str(requisicao.id),
                    }
                )
            os.materiais_previstos = materiais
            self.db.commit()

        logger.info(f"Requisição {requisicao.id} criada para OS {ordem_servico_id} com {len(itens_req)} itens")

        return requisicao

    def aprovar_requisicao(
        self,
        requisicao_id: UUID,
        aprovador_id: UUID,
        itens_aprovados: list[dict] | None = None,
        observacoes: str | None = None,
    ) -> RequisicaoMaterial:
        """
        Aprova uma requisição de materiais.

        Args:
            requisicao_id: ID da requisição
            aprovador_id: ID do aprovador
            itens_aprovados: Lista com quantidades aprovadas por item
            observacoes: Observações da aprovação

        Returns:
            RequisicaoMaterial atualizada
        """
        requisicao = self._requisicoes.get(requisicao_id)
        if not requisicao:
            raise ValueError(f"Requisição {requisicao_id} não encontrada")

        if requisicao.status != StatusRequisicao.PENDENTE:
            raise ValueError("Requisição não está pendente")

        # Atualizar quantidades aprovadas
        if itens_aprovados:
            for item_aprov in itens_aprovados:
                for item in requisicao.itens:
                    if str(item.produto_id) == str(item_aprov.get("produto_id")):
                        item.quantidade_aprovada = Decimal(
                            str(item_aprov.get("quantidade", item.quantidade_solicitada))
                        )
        else:
            # Aprovar tudo
            for item in requisicao.itens:
                item.quantidade_aprovada = item.quantidade_solicitada

        # Verificar disponibilidade
        for item in requisicao.itens:
            disponivel = self.verificar_disponibilidade(item.produto_id, item.quantidade_aprovada)
            if not disponivel["disponivel"]:
                pass

        requisicao.status = StatusRequisicao.APROVADA
        requisicao.data_aprovacao = datetime.now()
        requisicao.aprovador_id = aprovador_id

        if observacoes:
            requisicao.observacoes = (requisicao.observacoes or "") + f"\n[Aprovação] {observacoes}"

        logger.info(f"Requisição {requisicao_id} aprovada por {aprovador_id}")

        return requisicao

    def registrar_entrega(
        self,
        requisicao_id: UUID,
        itens_entregues: list[dict] | None = None,
    ) -> RequisicaoMaterial:
        """
        Registra entrega de materiais para uma requisição.

        Args:
            requisicao_id: ID da requisição
            itens_entregues: Lista com quantidades entregues

        Returns:
            RequisicaoMaterial atualizada
        """
        requisicao = self._requisicoes.get(requisicao_id)
        if not requisicao:
            raise ValueError(f"Requisição {requisicao_id} não encontrada")

        if requisicao.status not in [StatusRequisicao.APROVADA, StatusRequisicao.SEPARADA]:
            raise ValueError("Requisição não está aprovada/separada")

        # Registrar quantidades entregues
        entrega_parcial = False

        if itens_entregues:
            for item_ent in itens_entregues:
                for item in requisicao.itens:
                    if str(item.produto_id) == str(item_ent.get("produto_id")):
                        item.quantidade_entregue = Decimal(str(item_ent.get("quantidade", 0)))
                        if item.quantidade_entregue < (item.quantidade_aprovada or 0):
                            entrega_parcial = True
        else:
            # Entregar tudo aprovado
            for item in requisicao.itens:
                item.quantidade_entregue = item.quantidade_aprovada

        requisicao.data_entrega = datetime.now()
        requisicao.status = StatusRequisicao.PARCIAL if entrega_parcial else StatusRequisicao.ENTREGUE

        # Registrar movimentação de saída
        for item in requisicao.itens:
            if item.quantidade_entregue and item.quantidade_entregue > 0:
                self._registrar_movimentacao(
                    tipo=TipoMovimentacao.REQUISICAO,
                    produto_id=item.produto_id,
                    quantidade=item.quantidade_entregue,
                    ordem_servico_id=requisicao.ordem_servico_id,
                    tecnico_id=requisicao.tecnico_id,
                    requisicao_id=requisicao.id,
                )

        logger.info(f"Entrega registrada para requisição {requisicao_id}")

        return requisicao

    # =========================================================================
    # BAIXA DE MATERIAIS
    # =========================================================================

    def registrar_baixa_os(
        self,
        ordem_servico_id: UUID,
        itens_utilizados: list[dict[str, Any]],
        tecnico_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Registra baixa de materiais utilizados em uma OS.

        Args:
            ordem_servico_id: ID da ordem de serviço
            itens_utilizados: Lista de itens efetivamente utilizados
            tecnico_id: ID do técnico

        Returns:
            Dict com resultado da baixa
        """
        from modules.campo.models.ordem_servico import OrdemServico

        os = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()

        if not os:
            raise ValueError(f"OS {ordem_servico_id} não encontrada")

        baixas = []
        devolvidos = []

        for item in itens_utilizados:
            produto_id = item.get("produto_id")
            qtd_utilizada = Decimal(str(item.get("quantidade_utilizada", 0)))
            qtd_requisitada = Decimal(str(item.get("quantidade_requisitada", qtd_utilizada)))

            # Registrar baixa
            if qtd_utilizada > 0:
                self._registrar_movimentacao(
                    tipo=TipoMovimentacao.BAIXA,
                    produto_id=UUID(produto_id),
                    quantidade=qtd_utilizada,
                    ordem_servico_id=ordem_servico_id,
                    tecnico_id=tecnico_id,
                )
                baixas.append(
                    {
                        "produto_id": produto_id,
                        "quantidade": float(qtd_utilizada),
                    }
                )

            # Registrar devolução do excedente
            qtd_devolver = qtd_requisitada - qtd_utilizada
            if qtd_devolver > 0:
                self._registrar_movimentacao(
                    tipo=TipoMovimentacao.DEVOLUCAO,
                    produto_id=UUID(produto_id),
                    quantidade=qtd_devolver,
                    ordem_servico_id=ordem_servico_id,
                    tecnico_id=tecnico_id,
                )
                devolvidos.append(
                    {
                        "produto_id": produto_id,
                        "quantidade": float(qtd_devolver),
                    }
                )

        # Atualizar materiais utilizados na OS
        if hasattr(os, "materiais_utilizados"):
            os.materiais_utilizados = baixas
            self.db.commit()

        logger.info(
            f"Baixa registrada para OS {ordem_servico_id}: {len(baixas)} itens utilizados, {len(devolvidos)} devolvidos"
        )

        return {
            "ordem_servico_id": str(ordem_servico_id),
            "itens_baixados": baixas,
            "itens_devolvidos": devolvidos,
            "data_baixa": datetime.now().isoformat(),
        }

    def baixa_automatica_conclusao(
        self,
        ordem_servico_id: UUID,
    ) -> dict[str, Any]:
        """
        Realiza baixa automática quando OS é concluída.

        Baixa todos os materiais requisitados que ainda não foram baixados.
        """
        # Buscar requisições da OS
        requisicoes = [
            r
            for r in self._requisicoes.values()
            if r.ordem_servico_id == ordem_servico_id and r.status == StatusRequisicao.ENTREGUE
        ]

        if not requisicoes:
            return {
                "ordem_servico_id": str(ordem_servico_id),
                "message": "Nenhuma requisição entregue para baixa",
            }

        itens_baixar = []
        for req in requisicoes:
            for item in req.itens:
                if item.quantidade_entregue and item.quantidade_entregue > 0:
                    itens_baixar.append(
                        {
                            "produto_id": str(item.produto_id),
                            "quantidade_utilizada": float(item.quantidade_entregue),
                            "quantidade_requisitada": float(item.quantidade_entregue),
                        }
                    )

        if itens_baixar:
            return self.registrar_baixa_os(
                ordem_servico_id=ordem_servico_id,
                itens_utilizados=itens_baixar,
            )

        return {
            "ordem_servico_id": str(ordem_servico_id),
            "message": "Nenhum item para baixa",
        }

    # =========================================================================
    # VERIFICAÇÕES E ALERTAS
    # =========================================================================

    def verificar_disponibilidade(
        self,
        produto_id: UUID,
        quantidade: Decimal,
    ) -> dict[str, Any]:
        """
        Verifica disponibilidade de um produto no estoque.

        Args:
            produto_id: ID do produto
            quantidade: Quantidade desejada

        Returns:
            Dict com status de disponibilidade
        """
        # TODO: Integrar com módulo real de estoque (financial/inventory)
        # Por ora, simulação
        produto = self._get_produto(produto_id)
        estoque_atual = produto.get("estoque_atual", Decimal("100"))
        estoque_minimo = produto.get("estoque_minimo", Decimal("10"))

        disponivel = estoque_atual >= quantidade
        alerta_baixo = estoque_atual <= estoque_minimo

        return {
            "produto_id": str(produto_id),
            "produto_nome": produto.get("nome", "Produto"),
            "quantidade_solicitada": float(quantidade),
            "estoque_atual": float(estoque_atual),
            "estoque_minimo": float(estoque_minimo),
            "disponivel": disponivel,
            "quantidade_disponivel": float(estoque_atual),
            "alerta_estoque_baixo": alerta_baixo,
        }

    def verificar_estoque_tecnico(
        self,
        tecnico_id: UUID,
    ) -> dict[str, Any]:
        """
        Verifica estoque em posse de um técnico.

        Args:
            tecnico_id: ID do técnico

        Returns:
            Dict com itens em posse do técnico
        """
        # Buscar movimentações do técnico
        itens_tecnico = {}

        for mov in self._movimentacoes:
            if mov.get("tecnico_id") == str(tecnico_id):
                produto_id = mov.get("produto_id")

                if produto_id not in itens_tecnico:
                    itens_tecnico[produto_id] = {
                        "produto_id": produto_id,
                        "quantidade": Decimal("0"),
                    }

                if mov.get("tipo") in [TipoMovimentacao.REQUISICAO.value]:
                    itens_tecnico[produto_id]["quantidade"] += Decimal(str(mov.get("quantidade", 0)))
                elif mov.get("tipo") in [TipoMovimentacao.BAIXA.value, TipoMovimentacao.DEVOLUCAO.value]:
                    itens_tecnico[produto_id]["quantidade"] -= Decimal(str(mov.get("quantidade", 0)))

        # Filtrar apenas positivos
        itens = [
            {
                "produto_id": item["produto_id"],
                "quantidade": float(item["quantidade"]),
            }
            for item in itens_tecnico.values()
            if item["quantidade"] > 0
        ]

        return {
            "tecnico_id": str(tecnico_id),
            "itens": itens,
            "total_itens": len(itens),
        }

    def alertas_estoque_baixo(
        self,
        _threshold_percentual: float = 20,
    ) -> list[dict[str, Any]]:
        """
        Retorna alertas de produtos com estoque baixo.

        Args:
            threshold_percentual: Percentual abaixo do mínimo para alertar

        Returns:
            Lista de alertas
        """
        # TODO: Integrar com módulo real de estoque
        # Simulação
        alertas = [
            {
                "produto_id": str(uuid4()),
                "produto_nome": "Fita Isolante",
                "codigo": "FI-001",
                "estoque_atual": 5,
                "estoque_minimo": 20,
                "percentual": 25,
                "urgencia": "alta",
            },
            {
                "produto_id": str(uuid4()),
                "produto_nome": "Parafuso Philips 4mm",
                "codigo": "PF-004",
                "estoque_atual": 15,
                "estoque_minimo": 50,
                "percentual": 30,
                "urgencia": "media",
            },
        ]

        return alertas

    # =========================================================================
    # RELATÓRIOS
    # =========================================================================

    def relatorio_consumo_os(
        self,
        ordem_servico_id: UUID,
    ) -> dict[str, Any]:
        """
        Relatório de consumo de materiais de uma OS.
        """
        movimentacoes = [m for m in self._movimentacoes if m.get("ordem_servico_id") == str(ordem_servico_id)]

        requisitado = sum(
            Decimal(str(m.get("quantidade", 0)))
            for m in movimentacoes
            if m.get("tipo") == TipoMovimentacao.REQUISICAO.value
        )

        utilizado = sum(
            Decimal(str(m.get("quantidade", 0))) for m in movimentacoes if m.get("tipo") == TipoMovimentacao.BAIXA.value
        )

        devolvido = sum(
            Decimal(str(m.get("quantidade", 0)))
            for m in movimentacoes
            if m.get("tipo") == TipoMovimentacao.DEVOLUCAO.value
        )

        return {
            "ordem_servico_id": str(ordem_servico_id),
            "resumo": {
                "total_requisitado": float(requisitado),
                "total_utilizado": float(utilizado),
                "total_devolvido": float(devolvido),
                "taxa_aproveitamento": float(utilizado / requisitado * 100) if requisitado > 0 else 0,
            },
            "movimentacoes": movimentacoes,
        }

    def relatorio_consumo_periodo(
        self,
        data_inicio: date,
        data_fim: date,
        tecnico_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Relatório de consumo de materiais por período.
        """
        movimentacoes = [
            m for m in self._movimentacoes if data_inicio <= datetime.fromisoformat(m["data"]).date() <= data_fim
        ]

        if tecnico_id:
            movimentacoes = [m for m in movimentacoes if m.get("tecnico_id") == str(tecnico_id)]

        # Agrupar por produto
        por_produto = {}
        for m in movimentacoes:
            produto_id = m.get("produto_id")
            if produto_id not in por_produto:
                por_produto[produto_id] = {
                    "requisitado": Decimal("0"),
                    "utilizado": Decimal("0"),
                    "devolvido": Decimal("0"),
                }

            qtd = Decimal(str(m.get("quantidade", 0)))
            if m.get("tipo") == TipoMovimentacao.REQUISICAO.value:
                por_produto[produto_id]["requisitado"] += qtd
            elif m.get("tipo") == TipoMovimentacao.BAIXA.value:
                por_produto[produto_id]["utilizado"] += qtd
            elif m.get("tipo") == TipoMovimentacao.DEVOLUCAO.value:
                por_produto[produto_id]["devolvido"] += qtd

        return {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat(),
            },
            "tecnico_id": str(tecnico_id) if tecnico_id else None,
            "por_produto": {
                k: {
                    "requisitado": float(v["requisitado"]),
                    "utilizado": float(v["utilizado"]),
                    "devolvido": float(v["devolvido"]),
                }
                for k, v in por_produto.items()
            },
            "total_movimentacoes": len(movimentacoes),
        }

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_produto(self, produto_id: UUID) -> dict[str, Any]:
        """Obtém dados de um produto do estoque."""
        # TODO: Integrar com módulo real de estoque
        # Cache simulado
        if produto_id in self._estoque_cache:
            return self._estoque_cache[produto_id]

        # Dados simulados
        produto = {
            "id": str(produto_id),
            "codigo": f"PROD-{str(produto_id)[:8]}",
            "nome": "Produto Genérico",
            "unidade": "UN",
            "estoque_atual": Decimal("100"),
            "estoque_minimo": Decimal("10"),
        }

        self._estoque_cache[produto_id] = produto
        return produto

    def _registrar_movimentacao(
        self,
        tipo: TipoMovimentacao,
        produto_id: UUID,
        quantidade: Decimal,
        ordem_servico_id: UUID | None = None,
        tecnico_id: UUID | None = None,
        requisicao_id: UUID | None = None,
    ):
        """Registra movimentação de estoque."""
        movimentacao = {
            "id": str(uuid4()),
            "tipo": tipo.value,
            "produto_id": str(produto_id),
            "quantidade": float(quantidade),
            "ordem_servico_id": str(ordem_servico_id) if ordem_servico_id else None,
            "tecnico_id": str(tecnico_id) if tecnico_id else None,
            "requisicao_id": str(requisicao_id) if requisicao_id else None,
            "data": datetime.now().isoformat(),
        }

        self._movimentacoes.append(movimentacao)

        logger.debug(f"Movimentação {tipo.value}: produto {produto_id}, qtd {quantidade}")


# Singleton
def get_estoque_integration_service(db: Session) -> EstoqueIntegrationService:
    """Factory function para obter instância do serviço."""
    return EstoqueIntegrationService(db)
