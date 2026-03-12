"""
SCOUT Agent - Busca de oportunidades de licitacao
===================================================
Busca editais no Portal Nacional de Contratacoes Publicas (PNCP)
e filtra por criterios relevantes para a empresa.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, Field

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent
from modules.bidding.integrations.pncp.client import PNCPClient
from modules.bidding.integrations.pncp.models import PNCPCompra, PNCPSearchParams

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DTOs de resposta
# ──────────────────────────────────────────────


class OpportunityResponse(BaseModel):
    """Oportunidade de licitacao encontrada pelo SCOUT."""

    numero_compra: str
    ano_compra: int
    sequencial_compra: int
    orgao_cnpj: str
    orgao_nome: str
    orgao_uf: str
    modalidade: str | None = None
    objeto: str
    objeto_resumido: str | None = None
    valor_estimado: Decimal | None = None
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    link_pncp: str | None = None
    relevancia_score: float = 0.0
    keywords_matched: list[str] = Field(default_factory=list)
    fonte: str = "pncp"


class ScoutSearchParams(BaseModel):
    """Parametros de busca do SCOUT."""

    keywords: list[str] = Field(
        default_factory=lambda: [
            "vigilancia",
            "seguranca patrimonial",
            "seguranca eletronica",
            "portaria",
            "monitoramento",
            "cftv",
            "alarme",
            "controle de acesso",
        ]
    )
    ufs: list[str] = Field(default_factory=lambda: ["AM"])
    modalidades: list[str] | None = None
    valor_minimo: Decimal | None = None
    valor_maximo: Decimal | None = None
    data_inicial: date | None = None
    data_final: date | None = None
    max_paginas: int = 5
    tamanho_pagina: int = 20


# ──────────────────────────────────────────────
# SCOUT Agent
# ──────────────────────────────────────────────


class ScoutAgent(BaseAgent):
    """
    Agente SCOUT - Busca e filtra oportunidades de licitacao.

    Responsabilidades:
    - Buscar editais no PNCP por UF, modalidade e periodo
    - Filtrar por palavras-chave relevantes (seguranca, vigilancia, etc.)
    - Calcular score de relevancia
    - Retornar lista ordenada por relevancia
    """

    AGENT_NAME = "scout"
    AGENT_DESCRIPTION = "Busca oportunidades de licitacao no PNCP"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    def __init__(self, config: AgentConfig | None = None):
        super().__init__(config)
        self.pncp_client = PNCPClient()

    async def execute(
        self,
        search_params: ScoutSearchParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        Executa busca de oportunidades no PNCP.

        Args:
            search_params: Parametros de busca. Se None, usa defaults.

        Returns:
            Lista de OpportunityResponse como dicts, ordenada por relevancia.
        """
        params = search_params or ScoutSearchParams()

        if params.data_inicial is None:
            params.data_inicial = date.today() - timedelta(days=30)
        if params.data_final is None:
            params.data_final = date.today()

        all_opportunities: list[OpportunityResponse] = []

        try:
            async with self.pncp_client as client:
                for uf in params.ufs:
                    uf_opportunities = await self._buscar_por_uf(client, uf, params)
                    all_opportunities.extend(uf_opportunities)

        except Exception as e:
            self.logger.error(f"Erro ao buscar oportunidades: {e}")
            raise

        # Ordenar por relevancia (maior primeiro)
        all_opportunities.sort(key=lambda o: o.relevancia_score, reverse=True)

        self.logger.info(f"SCOUT encontrou {len(all_opportunities)} oportunidades em {len(params.ufs)} UF(s)")

        return [opp.model_dump(mode="json") for opp in all_opportunities]

    async def _buscar_por_uf(
        self,
        client: PNCPClient,
        uf: str,
        params: ScoutSearchParams,
    ) -> list[OpportunityResponse]:
        """Busca oportunidades em uma UF especifica."""
        opportunities: list[OpportunityResponse] = []

        for pagina in range(1, params.max_paginas + 1):
            search_params = PNCPSearchParams(
                uf=uf,
                data_inicial=params.data_inicial,
                data_final=params.data_final,
                modalidade=params.modalidades[0] if params.modalidades else None,
                pagina=pagina,
                tamanho_pagina=params.tamanho_pagina,
            )

            response = await client.buscar_compras(search_params)

            if not response.sucesso or not response.compras:
                break

            for compra in response.compras:
                opp = self._avaliar_compra(compra, params)
                if opp is not None:
                    opportunities.append(opp)

            # Se esta na ultima pagina, para
            if pagina >= response.total_paginas:
                break

        return opportunities

    def _avaliar_compra(
        self,
        compra: PNCPCompra,
        params: ScoutSearchParams,
    ) -> OpportunityResponse | None:
        """
        Avalia se uma compra e relevante para a empresa.

        Retorna OpportunityResponse se relevante, None caso contrario.
        """
        texto_busca = f"{compra.objeto} {compra.objeto_resumido or ''}".lower()

        # Verificar keywords
        matched_keywords = [kw for kw in params.keywords if kw.lower() in texto_busca]

        if not matched_keywords:
            return None

        # Filtrar por faixa de valor
        if compra.valor_estimado_total is not None:
            if params.valor_minimo and compra.valor_estimado_total < params.valor_minimo:
                return None
            if params.valor_maximo and compra.valor_estimado_total > params.valor_maximo:
                return None

        # Calcular score de relevancia (0-100)
        relevancia = self._calcular_relevancia(compra, matched_keywords, params)

        return OpportunityResponse(
            numero_compra=compra.numero_compra,
            ano_compra=compra.ano_compra,
            sequencial_compra=compra.sequencial_compra,
            orgao_cnpj=compra.orgao.cnpj,
            orgao_nome=compra.orgao.razao_social,
            orgao_uf=compra.orgao.uf,
            modalidade=compra.modalidade_nome,
            objeto=compra.objeto,
            objeto_resumido=compra.objeto_resumido,
            valor_estimado=compra.valor_estimado_total,
            data_publicacao=compra.data_publicacao_pncp,
            data_abertura=compra.data_abertura_proposta,
            data_encerramento=compra.data_encerramento_proposta,
            link_pncp=compra.link_pncp,
            relevancia_score=relevancia,
            keywords_matched=matched_keywords,
            fonte="pncp",
        )

    def _calcular_relevancia(
        self,
        compra: PNCPCompra,
        matched_keywords: list[str],
        params: ScoutSearchParams,
    ) -> float:
        """
        Calcula score de relevancia de 0 a 100.

        Fatores:
        - Quantidade de keywords matched (peso 40)
        - Modalidade preferida (peso 20)
        - Prazo disponivel (peso 20)
        - Valor na faixa ideal (peso 20)
        """
        score = 0.0

        # Keywords (ate 40 pontos)
        keyword_ratio = len(matched_keywords) / max(len(params.keywords), 1)
        score += keyword_ratio * 40

        # Modalidade preferida - pregao eletronico tem mais peso (ate 20 pontos)
        modalidade = (compra.modalidade_nome or "").lower()
        if "pregao" in modalidade and "eletronico" in modalidade:
            score += 20
        elif "pregao" in modalidade:
            score += 15
        elif "concorrencia" in modalidade:
            score += 10
        elif "dispensa" in modalidade:
            score += 5

        # Prazo disponivel (ate 20 pontos)
        if compra.data_abertura_proposta:
            dias_restantes = (compra.data_abertura_proposta - datetime.utcnow()).days
            if dias_restantes > 15:
                score += 20
            elif dias_restantes > 7:
                score += 15
            elif dias_restantes > 3:
                score += 10
            elif dias_restantes > 0:
                score += 5

        # Valor na faixa ideal: 100k-5M (ate 20 pontos)
        if compra.valor_estimado_total:
            valor = float(compra.valor_estimado_total)
            if 100_000 <= valor <= 5_000_000:
                score += 20
            elif 50_000 <= valor <= 10_000_000:
                score += 15
            elif valor > 0:
                score += 5

        return round(min(score, 100.0), 1)
