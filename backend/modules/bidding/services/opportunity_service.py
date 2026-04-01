"""
Service de Oportunidades — Licitacoes
======================================
Gerencia oportunidades de licitacao detectadas pelo agente Scout
e consolidadas a partir de multiplos portais.
"""

import contextlib
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class OpportunityFilters:
    """Filtros para listagem de oportunidades."""

    def __init__(
        self,
        portal: str | None = None,
        uf: str | None = None,
        modalidade: str | None = None,
        valor_minimo: float | None = None,
        valor_maximo: float | None = None,
        status: str | None = None,
        segmento: str | None = None,
        page: int = 1,
        size: int = 20,
    ):
        self.portal = portal
        self.uf = uf
        self.modalidade = modalidade
        self.valor_minimo = valor_minimo
        self.valor_maximo = valor_maximo
        self.status = status
        self.segmento = segmento
        self.page = page
        self.size = size


class OpportunityService:
    """Service para operacoes com oportunidades de licitacao."""

    # Status possiveis de uma oportunidade
    STATUS_NOVA = "nova"
    STATUS_EM_ANALISE = "em_analise"
    STATUS_APROVADA = "aprovada"
    STATUS_DESCARTADA = "descartada"
    STATUS_PARTICIPANDO = "participando"

    VALID_STATUSES = {STATUS_NOVA, STATUS_EM_ANALISE, STATUS_APROVADA, STATUS_DESCARTADA, STATUS_PARTICIPANDO}

    def __init__(self, db=None):
        """
        Inicializa o service.

        Args:
            db: Sessao de banco de dados (opcional, para futuro ORM)
        """
        self.db = db
        self._cache: dict[str, dict[str, Any]] = {}

    async def list_opportunities(self, filters: OpportunityFilters | None = None) -> list[dict[str, Any]]:
        """
        Lista oportunidades com filtros opcionais.

        Args:
            filters: Filtros de busca (portal, uf, modalidade, valor, status, segmento)

        Returns:
            Lista de oportunidades encontradas
        """
        logger.info("Listando oportunidades com filtros: %s", filters)

        results = list(self._cache.values())

        if filters:
            if filters.portal:
                results = [r for r in results if r.get("portal") == filters.portal]
            if filters.uf:
                results = [r for r in results if r.get("uf") == filters.uf]
            if filters.modalidade:
                results = [r for r in results if r.get("modalidade") == filters.modalidade]
            if filters.status:
                results = [r for r in results if r.get("status") == filters.status]
            if filters.segmento:
                results = [r for r in results if r.get("segmento") == filters.segmento]
            if filters.valor_minimo is not None:
                results = [r for r in results if (r.get("valor_estimado") or 0) >= filters.valor_minimo]
            if filters.valor_maximo is not None:
                results = [r for r in results if (r.get("valor_estimado") or 0) <= filters.valor_maximo]

            # Paginacao
            start = (filters.page - 1) * filters.size
            end = start + filters.size
            results = results[start:end]

        return results

    async def get_opportunity(self, opportunity_id: str | UUID) -> dict[str, Any] | None:
        """
        Busca oportunidade por ID.

        Args:
            opportunity_id: Identificador unico da oportunidade

        Returns:
            Dados da oportunidade ou None se nao encontrada
        """
        key = str(opportunity_id)
        opportunity = self._cache.get(key)
        if not opportunity:
            logger.warning("Oportunidade nao encontrada: %s", key)
            return None
        return opportunity

    async def create_from_scout(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Cria oportunidade a partir de dados retornados pelo agente Scout.

        Args:
            data: Dados da oportunidade do Scout (portal, portal_id, objeto, etc.)

        Returns:
            Oportunidade criada com ID interno
        """
        opportunity_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        opportunity = {
            "id": opportunity_id,
            "portal": data.get("portal", ""),
            "portal_id": data.get("portal_id", ""),
            "objeto": data.get("objeto", ""),
            "valor_estimado": data.get("valor_estimado"),
            "modalidade": data.get("modalidade", ""),
            "orgao_nome": data.get("orgao_nome", ""),
            "orgao_cnpj": data.get("orgao_cnpj", ""),
            "uf": data.get("uf", "AM"),
            "municipio": data.get("municipio", ""),
            "data_publicacao": data.get("data_publicacao"),
            "data_abertura": data.get("data_abertura"),
            "data_encerramento": data.get("data_encerramento"),
            "url_edital": data.get("url_edital", ""),
            "relevancia_score": data.get("relevancia_score", 0),
            "segmento": data.get("segmento", "vigilancia"),
            "status": self.STATUS_NOVA,
            "created_at": now,
            "updated_at": now,
        }

        self._cache[opportunity_id] = opportunity
        logger.info("Oportunidade criada: %s (portal=%s)", opportunity_id, opportunity["portal"])
        return opportunity

    async def update_status(
        self, opportunity_id: str | UUID, status: str, motivo: str | None = None
    ) -> dict[str, Any] | None:
        """
        Atualiza status de uma oportunidade.

        Args:
            opportunity_id: ID da oportunidade
            status: Novo status (nova, em_analise, aprovada, descartada, participando)
            motivo: Motivo da mudanca de status (opcional)

        Returns:
            Oportunidade atualizada ou None
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Status invalido: {status}. Validos: {self.VALID_STATUSES}")

        key = str(opportunity_id)
        opportunity = self._cache.get(key)
        if not opportunity:
            logger.warning("Oportunidade nao encontrada para update: %s", key)
            return None

        opportunity["status"] = status
        opportunity["motivo_status"] = motivo
        opportunity["updated_at"] = datetime.utcnow().isoformat()
        logger.info("Oportunidade %s atualizada para status=%s", key, status)
        return opportunity

    async def get_statistics(self) -> dict[str, Any]:
        """
        Retorna estatisticas das oportunidades.

        Returns:
            Dict com contagem por status, portal, uf e totais
        """
        all_opportunities = list(self._cache.values())
        total = len(all_opportunities)

        por_status: dict[str, int] = {}
        por_portal: dict[str, int] = {}
        por_uf: dict[str, int] = {}
        valor_total_estimado = 0.0

        for opp in all_opportunities:
            status = opp.get("status", "desconhecido")
            por_status[status] = por_status.get(status, 0) + 1

            portal = opp.get("portal", "desconhecido")
            por_portal[portal] = por_portal.get(portal, 0) + 1

            uf = opp.get("uf", "desconhecido")
            por_uf[uf] = por_uf.get(uf, 0) + 1

            valor = opp.get("valor_estimado")
            if valor is not None:
                with contextlib.suppress(TypeError, ValueError):
                    valor_total_estimado += float(valor)

        return {
            "total": total,
            "por_status": por_status,
            "por_portal": por_portal,
            "por_uf": por_uf,
            "valor_total_estimado": valor_total_estimado,
            "novas": por_status.get("nova", 0),
            "em_analise": por_status.get("em_analise", 0),
            "aprovadas": por_status.get("aprovada", 0),
        }
