"""
Service de Precificacao — Licitacoes
=====================================
Wrapper service para o agente Pricer, gerenciando calculos de
precificacao, composicao de custos, BDI e comparativos de mercado.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from modules.bidding.agents.pricer_agent import PricerAgent

logger = logging.getLogger(__name__)


class PricingService:
    """Service para operacoes de precificacao de licitacoes."""

    # Regimes tributarios suportados
    REGIME_SIMPLES = "simples"
    REGIME_LUCRO_PRESUMIDO = "lucro_presumido"
    REGIME_LUCRO_REAL = "lucro_real"
    VALID_REGIMES = {REGIME_SIMPLES, REGIME_LUCRO_PRESUMIDO, REGIME_LUCRO_REAL}

    # Cenarios de precificacao
    CENARIO_CONSERVADOR = "conservador"
    CENARIO_MODERADO = "moderado"
    CENARIO_AGRESSIVO = "agressivo"
    VALID_CENARIOS = {CENARIO_CONSERVADOR, CENARIO_MODERADO, CENARIO_AGRESSIVO}

    def __init__(self, db=None):
        """
        Inicializa o service.

        Args:
            db: Sessao de banco de dados (opcional)
        """
        self.db = db
        self.pricer_agent = PricerAgent()
        self._cache: dict[str, dict[str, Any]] = {}

    async def calculate_pricing(
        self,
        tender_id: str | UUID,
        items: list[dict[str, Any]],
        regime: str = "simples",
        cenario: str = "moderado",
        bdi_percentual: float | None = None,
    ) -> dict[str, Any]:
        """
        Calcula precificacao para um edital usando o agente Pricer.

        Args:
            tender_id: ID do edital
            items: Lista de itens com quantidade e descricao
            regime: Regime tributario (simples, lucro_presumido, lucro_real)
            cenario: Cenario de precificacao (conservador, moderado, agressivo)
            bdi_percentual: Percentual de BDI customizado (opcional)

        Returns:
            Resultado da precificacao com detalhamento de custos
        """
        if regime not in self.VALID_REGIMES:
            raise ValueError(f"Regime tributario invalido: {regime}. Validos: {self.VALID_REGIMES}")

        if cenario not in self.VALID_CENARIOS:
            raise ValueError(f"Cenario invalido: {cenario}. Validos: {self.VALID_CENARIOS}")

        pricing_input = {
            "regime_tributario": regime,
            "cenario": cenario,
            "bdi_percentual": bdi_percentual,
            "itens": items,
        }

        logger.info(
            "Calculando precificacao para edital %s (regime=%s, cenario=%s)",
            tender_id,
            regime,
            cenario,
        )

        try:
            result = await self.pricer_agent.run(pricing_input=pricing_input)
            if not result.success:
                logger.error("Erro no agente Pricer: %s", result.error)
                raise RuntimeError(f"Erro no Pricer: {result.error}")

            pricing_id = str(uuid4())
            now = datetime.utcnow().isoformat()

            pricing_record = {
                "id": pricing_id,
                "tender_id": str(tender_id),
                "regime_tributario": regime,
                "cenario": cenario,
                "bdi_percentual": bdi_percentual,
                "itens_count": len(items),
                "resultado": result.data,
                "created_at": now,
            }

            self._cache[pricing_id] = pricing_record
            logger.info("Precificacao %s calculada com sucesso para edital %s", pricing_id, tender_id)
            return pricing_record

        except RuntimeError:
            raise
        except Exception as e:
            logger.error("Erro ao calcular precificacao: %s", e, exc_info=True)
            raise RuntimeError(f"Erro ao calcular precificacao: {str(e)}") from e

    async def get_pricing(self, pricing_id: str | UUID) -> dict[str, Any] | None:
        """
        Busca precificacao por ID.

        Args:
            pricing_id: ID do calculo de precificacao

        Returns:
            Dados da precificacao ou None
        """
        key = str(pricing_id)
        pricing = self._cache.get(key)
        if not pricing:
            logger.warning("Precificacao nao encontrada: %s", key)
            return None
        return pricing

    async def list_pricings(self, tender_id: str | UUID) -> list[dict[str, Any]]:
        """
        Lista precificacoes de um edital.

        Args:
            tender_id: ID do edital

        Returns:
            Lista de precificacoes calculadas para o edital
        """
        tid = str(tender_id)
        results = [p for p in self._cache.values() if p.get("tender_id") == tid]
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        logger.info("Encontradas %d precificacoes para edital %s", len(results), tid)
        return results

    async def compare_market(self, item: dict[str, Any], price: float) -> dict[str, Any]:
        """
        Compara preco proposto com valores de mercado.

        Args:
            item: Dados do item (descricao, unidade, quantidade)
            price: Preco unitario proposto

        Returns:
            Comparativo de mercado com indicadores
        """
        descricao = item.get("descricao", "")
        quantidade = item.get("quantidade", 1)
        unidade = item.get("unidade", "un")

        # Simulacao de comparativo (sera integrado com bases de precos reais)
        preco_referencia = price * 1.05  # Margem de referencia
        variacao_percentual = ((price - preco_referencia) / preco_referencia * 100) if preco_referencia else 0

        competitividade = "competitivo"
        if variacao_percentual > 10:
            competitividade = "acima_mercado"
        elif variacao_percentual < -15:
            competitividade = "muito_abaixo"
        elif variacao_percentual < -5:
            competitividade = "abaixo_mercado"

        logger.info(
            "Comparativo de mercado para '%s': preco=%.2f, ref=%.2f, variacao=%.1f%%",
            descricao,
            price,
            preco_referencia,
            variacao_percentual,
        )

        return {
            "item": descricao,
            "unidade": unidade,
            "quantidade": quantidade,
            "preco_proposto": price,
            "preco_referencia": float(preco_referencia),
            "variacao_percentual": round(variacao_percentual, 2),
            "competitividade": competitividade,
            "fontes_referencia": [
                "Painel de Precos (Compras.gov.br)",
                "Banco de Precos TCU",
                "Historico interno Conecta PRO",
            ],
            "observacao": f"Item {'competitivo' if competitividade == 'competitivo' else 'requer atencao'} em relacao ao mercado",
        }
