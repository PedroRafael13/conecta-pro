"""
SCOUT Agent - Busca de oportunidades de licitacao MULTI-PORTAL
===============================================================
Busca editais em 6 portais simultaneamente:
- PNCP (Portal Nacional de Contratacoes Publicas)
- ComprasNet (Compras.gov.br - Governo Federal)
- Licitacoes-e (Banco do Brasil)
- e-Compras AM (Estado do Amazonas)
- BLL Compras (Portal de licitacoes eletronicas)
- Portal de Compras Publicas
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, Field

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent
from modules.bidding.integrations.bll.client import BLLClient
from modules.bidding.integrations.comprasnet.client import ComprasNetClient
from modules.bidding.integrations.ecompras_am.client import EComprasAMClient
from modules.bidding.integrations.licitacoes_e.client import LicitacoesEClient
from modules.bidding.integrations.pncp.client import PNCPClient
from modules.bidding.integrations.pncp.models import PNCPCompra, PNCPSearchParams
from modules.bidding.integrations.portal_compras_publicas.client import PortalComprasPublicasClient

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DTOs de resposta
# ──────────────────────────────────────────────


class OpportunityResponse(BaseModel):
    """Oportunidade de licitacao encontrada pelo SCOUT."""

    numero_compra: str
    ano_compra: int = 0
    sequencial_compra: int = 0
    orgao_cnpj: str = ""
    orgao_nome: str = ""
    orgao_uf: str = ""
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
    portais: list[str] = Field(
        default_factory=lambda: ["pncp", "comprasnet", "licitacoes_e", "ecompras_am", "bll", "portal_compras_publicas"]
    )


# ──────────────────────────────────────────────
# Configuracao de portais
# ──────────────────────────────────────────────

PORTAIS_DISPONIVEIS = {
    "pncp": {
        "nome": "PNCP",
        "descricao": "Portal Nacional de Contratacoes Publicas",
        "tipo": "federal",
        "api": True,
    },
    "comprasnet": {
        "nome": "ComprasNet",
        "descricao": "Compras.gov.br - Governo Federal",
        "tipo": "federal",
        "api": True,
    },
    "licitacoes_e": {
        "nome": "Licitacoes-e",
        "descricao": "Banco do Brasil - Licitacoes Eletronicas",
        "tipo": "privado",
        "api": False,
    },
    "ecompras_am": {
        "nome": "e-Compras AM",
        "descricao": "Portal de Compras do Amazonas",
        "tipo": "estadual",
        "api": False,
    },
    "bll": {
        "nome": "BLL Compras",
        "descricao": "BLL Compras - Portal de Licitacoes Eletronicas",
        "tipo": "privado",
        "api": False,
    },
    "portal_compras_publicas": {
        "nome": "Portal de Compras Publicas",
        "descricao": "Portal de Compras Publicas - Licitacoes Eletronicas",
        "tipo": "privado",
        "api": False,
    },
}


# ──────────────────────────────────────────────
# SCOUT Agent
# ──────────────────────────────────────────────


class ScoutAgent(BaseAgent):
    """
    Agente SCOUT - Busca e filtra oportunidades de licitacao em 5 portais.

    Responsabilidades:
    - Buscar editais no PNCP, ComprasNet, Licitacoes-e, e-Compras AM, BLL Compras e Portal de Compras Publicas
    - Consultar todos os portais simultaneamente via asyncio.gather
    - Filtrar por palavras-chave relevantes (seguranca, vigilancia, etc.)
    - Calcular score de relevancia uniforme para todos os portais
    - Deduplicar resultados de portais diferentes
    - Retornar lista ordenada por relevancia
    """

    AGENT_NAME = "scout"
    AGENT_DESCRIPTION = "Busca oportunidades de licitacao em 6 portais simultaneamente"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    def __init__(self, config: AgentConfig | None = None):
        super().__init__(config)
        self.pncp_client = PNCPClient()
        self.comprasnet_client = ComprasNetClient()
        self.licitacoes_e_client = LicitacoesEClient()
        self.ecompras_am_client = EComprasAMClient()
        self.bll_client = BLLClient()
        self.portal_compras_publicas_client = PortalComprasPublicasClient()

    async def execute(
        self,
        search_params: ScoutSearchParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        Executa busca de oportunidades em todos os portais configurados.

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

        # Montar lista de tasks por portal
        tasks = []
        portal_names = []

        if "pncp" in params.portais:
            tasks.append(self._buscar_pncp(params))
            portal_names.append("PNCP")

        if "comprasnet" in params.portais:
            tasks.append(self._buscar_comprasnet(params))
            portal_names.append("ComprasNet")

        if "licitacoes_e" in params.portais:
            tasks.append(self._buscar_licitacoes_e(params))
            portal_names.append("Licitacoes-e")

        if "ecompras_am" in params.portais:
            tasks.append(self._buscar_ecompras_am(params))
            portal_names.append("e-Compras AM")

        if "bll" in params.portais:
            tasks.append(self._buscar_bll(params))
            portal_names.append("BLL Compras")

        if "portal_compras_publicas" in params.portais:
            tasks.append(self._buscar_portal_compras_publicas(params))
            portal_names.append("Portal de Compras Publicas")

        if not tasks:
            self.logger.warning("SCOUT: nenhum portal selecionado")
            return []

        # Executar busca em todos os portais simultaneamente
        self.logger.info(f"SCOUT: buscando em {len(tasks)} portais: {', '.join(portal_names)}")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Consolidar resultados, ignorando portais com erro
        all_opportunities: list[OpportunityResponse] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"SCOUT: erro no portal {portal_names[i]}: {result}")
                continue
            count = len(result)
            self.logger.info(f"SCOUT: {portal_names[i]} retornou {count} oportunidades")
            all_opportunities.extend(result)

        # Deduplicar (mesmo edital pode aparecer em portais diferentes)
        all_opportunities = self._deduplicar(all_opportunities)

        # Ordenar por relevancia (maior primeiro)
        all_opportunities.sort(key=lambda o: o.relevancia_score, reverse=True)

        self.logger.info(
            f"SCOUT: {len(all_opportunities)} oportunidades unicas em "
            f"{len(params.ufs)} UF(s) de {len(portal_names)} portais"
        )

        return [opp.model_dump(mode="json") for opp in all_opportunities]

    # ──────────────────────────────────────────────
    # Busca por portal
    # ──────────────────────────────────────────────

    async def _buscar_pncp(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no PNCP."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.pncp_client as client:
                for uf in params.ufs:
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
                            opp = self._avaliar_compra_pncp(compra, params)
                            if opp is not None:
                                opportunities.append(opp)
                        if pagina >= response.total_paginas:
                            break
        except Exception as e:
            self.logger.error(f"Erro ao buscar PNCP: {e}")
            raise
        return opportunities

    async def _buscar_comprasnet(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no ComprasNet."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.comprasnet_client as client:
                for uf in params.ufs:
                    results = await client.buscar_oportunidades(
                        uf=uf,
                        data_inicial=params.data_inicial,
                        data_final=params.data_final,
                        pagina=1,
                    )
                    for raw in results:
                        opp = self._avaliar_oportunidade_generica(raw, params, "comprasnet")
                        if opp is not None:
                            opportunities.append(opp)
        except Exception as e:
            self.logger.error(f"Erro ao buscar ComprasNet: {e}")
            raise
        return opportunities

    async def _buscar_licitacoes_e(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no Licitacoes-e (Banco do Brasil)."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.licitacoes_e_client as client:
                for uf in params.ufs:
                    results = await client.buscar_oportunidades(
                        uf=uf,
                        data_inicial=params.data_inicial,
                        pagina=1,
                    )
                    for raw in results:
                        opp = self._avaliar_oportunidade_generica(raw, params, "licitacoes_e")
                        if opp is not None:
                            opportunities.append(opp)
        except Exception as e:
            self.logger.error(f"Erro ao buscar Licitacoes-e: {e}")
            raise
        return opportunities

    async def _buscar_ecompras_am(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no e-Compras AM."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.ecompras_am_client as client:
                results = await client.buscar_oportunidades(
                    data_inicial=params.data_inicial,
                    data_final=params.data_final,
                    pagina=1,
                )
                for raw in results:
                    opp = self._avaliar_oportunidade_generica(raw, params, "ecompras_am")
                    if opp is not None:
                        opportunities.append(opp)
        except Exception as e:
            self.logger.error(f"Erro ao buscar e-Compras AM: {e}")
            raise
        return opportunities

    async def _buscar_bll(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no BLL Compras."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.bll_client as client:
                for uf in params.ufs:
                    results = await client.buscar_oportunidades(
                        uf=uf,
                        data_inicial=params.data_inicial,
                        data_final=params.data_final,
                        pagina=1,
                    )
                    for raw in results:
                        opp = self._avaliar_oportunidade_generica(raw, params, "bll")
                        if opp is not None:
                            opportunities.append(opp)
        except Exception as e:
            self.logger.error(f"Erro ao buscar BLL Compras: {e}")
            raise
        return opportunities

    async def _buscar_portal_compras_publicas(self, params: ScoutSearchParams) -> list[OpportunityResponse]:
        """Busca oportunidades no Portal de Compras Publicas."""
        opportunities: list[OpportunityResponse] = []
        try:
            async with self.portal_compras_publicas_client as client:
                for uf in params.ufs:
                    results = await client.buscar_oportunidades(
                        uf=uf,
                        data_inicial=params.data_inicial,
                        data_final=params.data_final,
                        pagina=1,
                    )
                    for raw in results:
                        opp = self._avaliar_oportunidade_generica(raw, params, "portal_compras_publicas")
                        if opp is not None:
                            opportunities.append(opp)
        except Exception as e:
            self.logger.error(f"Erro ao buscar Portal de Compras Publicas: {e}")
            raise
        return opportunities

    # ──────────────────────────────────────────────
    # Avaliacao e scoring
    # ──────────────────────────────────────────────

    def _avaliar_compra_pncp(
        self,
        compra: PNCPCompra,
        params: ScoutSearchParams,
    ) -> OpportunityResponse | None:
        """Avalia se uma compra do PNCP e relevante."""
        texto_busca = f"{compra.objeto} {compra.objeto_resumido or ''}".lower()
        matched_keywords = [kw for kw in params.keywords if kw.lower() in texto_busca]

        if not matched_keywords:
            return None

        if compra.valor_estimado_total is not None:
            if params.valor_minimo and compra.valor_estimado_total < params.valor_minimo:
                return None
            if params.valor_maximo and compra.valor_estimado_total > params.valor_maximo:
                return None

        relevancia = self._calcular_relevancia(
            modalidade=compra.modalidade_nome,
            data_abertura=compra.data_abertura_proposta,
            valor_estimado=float(compra.valor_estimado_total) if compra.valor_estimado_total else None,
            matched_keywords=matched_keywords,
            total_keywords=len(params.keywords),
        )

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

    def _avaliar_oportunidade_generica(
        self,
        raw: dict,
        params: ScoutSearchParams,
        portal: str,
    ) -> OpportunityResponse | None:
        """Avalia oportunidade vinda de portais genericos (ComprasNet, Licitacoes-e, eCompras-AM, BLL)."""
        objeto = raw.get("objeto", "")
        if not objeto:
            return None

        texto_busca = objeto.lower()
        matched_keywords = [kw for kw in params.keywords if kw.lower() in texto_busca]

        if not matched_keywords:
            return None

        valor_estimado = raw.get("valor_estimado")
        if valor_estimado is not None:
            try:
                valor_decimal = Decimal(str(valor_estimado))
                if params.valor_minimo and valor_decimal < params.valor_minimo:
                    return None
                if params.valor_maximo and valor_decimal > params.valor_maximo:
                    return None
            except Exception:
                valor_decimal = None
        else:
            valor_decimal = None

        data_abertura = self._parse_datetime(raw.get("data_abertura"))

        relevancia = self._calcular_relevancia(
            modalidade=raw.get("modalidade"),
            data_abertura=data_abertura,
            valor_estimado=float(valor_decimal) if valor_decimal else None,
            matched_keywords=matched_keywords,
            total_keywords=len(params.keywords),
        )

        return OpportunityResponse(
            numero_compra=raw.get("portal_id", "") or raw.get("numero", "") or "N/A",
            orgao_cnpj=raw.get("orgao_cnpj", ""),
            orgao_nome=raw.get("orgao_nome", ""),
            orgao_uf=raw.get("uf", ""),
            modalidade=raw.get("modalidade"),
            objeto=objeto,
            valor_estimado=valor_decimal,
            data_publicacao=self._parse_datetime(raw.get("data_publicacao")),
            data_abertura=data_abertura,
            data_encerramento=self._parse_datetime(raw.get("data_encerramento")),
            link_pncp=raw.get("url_edital", ""),
            relevancia_score=relevancia,
            keywords_matched=matched_keywords,
            fonte=portal,
        )

    def _calcular_relevancia(
        self,
        modalidade: str | None,
        data_abertura: datetime | None,
        valor_estimado: float | None,
        matched_keywords: list[str],
        total_keywords: int,
    ) -> float:
        """
        Calcula score de relevancia de 0 a 100 (uniforme para todos os portais).

        Fatores:
        - Quantidade de keywords matched (peso 40)
        - Modalidade preferida (peso 20)
        - Prazo disponivel (peso 20)
        - Valor na faixa ideal (peso 20)
        """
        score = 0.0

        # Keywords (ate 40 pontos)
        keyword_ratio = len(matched_keywords) / max(total_keywords, 1)
        score += keyword_ratio * 40

        # Modalidade preferida (ate 20 pontos)
        mod = (modalidade or "").lower()
        if "pregao" in mod and "eletronico" in mod:
            score += 20
        elif "pregao" in mod:
            score += 15
        elif "concorrencia" in mod:
            score += 10
        elif "dispensa" in mod:
            score += 5

        # Prazo disponivel (ate 20 pontos)
        if data_abertura:
            dias_restantes = (data_abertura - datetime.utcnow()).days
            if dias_restantes > 15:
                score += 20
            elif dias_restantes > 7:
                score += 15
            elif dias_restantes > 3:
                score += 10
            elif dias_restantes > 0:
                score += 5

        # Valor na faixa ideal: 100k-5M (ate 20 pontos)
        if valor_estimado:
            if 100_000 <= valor_estimado <= 5_000_000:
                score += 20
            elif 50_000 <= valor_estimado <= 10_000_000:
                score += 15
            elif valor_estimado > 0:
                score += 5

        return round(min(score, 100.0), 1)

    # ──────────────────────────────────────────────
    # Deduplicacao
    # ──────────────────────────────────────────────

    def _deduplicar(self, opportunities: list[OpportunityResponse]) -> list[OpportunityResponse]:
        """
        Remove duplicatas entre portais.

        Dedup em 2 passos:
        1. Chave exata: orgao_cnpj + numero_compra
        2. Similaridade de texto: >85% de overlap no objeto (cross-portal)
        """
        if not opportunities:
            return []

        seen_keys: set[str] = set()
        unique: list[OpportunityResponse] = []

        for opp in opportunities:
            # Passo 1: chave exata
            key = f"{opp.orgao_cnpj}:{opp.numero_compra}".lower().strip()
            if key and key != ":" and key in seen_keys:
                continue

            # Passo 2: similaridade de texto (somente se houver objeto)
            is_dup = False
            if opp.objeto:
                opp_words = set(opp.objeto.lower().split())
                for existing in unique:
                    if not existing.objeto:
                        continue
                    existing_words = set(existing.objeto.lower().split())
                    if not opp_words or not existing_words:
                        continue
                    intersection = opp_words & existing_words
                    union = opp_words | existing_words
                    similarity = len(intersection) / len(union) if union else 0
                    if similarity > 0.85:
                        # Manter o que tem maior relevancia
                        if opp.relevancia_score > existing.relevancia_score:
                            unique.remove(existing)
                            unique.append(opp)
                        is_dup = True
                        break

            if not is_dup:
                if key and key != ":":
                    seen_keys.add(key)
                unique.append(opp)

        return unique

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _parse_datetime(self, value) -> datetime | None:
        """Converte diversos formatos de data para datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value.strip(), fmt)
                except ValueError:
                    continue
        return None
