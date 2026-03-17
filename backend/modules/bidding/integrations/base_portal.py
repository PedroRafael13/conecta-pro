"""
Base Portal Client — Integracao de Portais de Licitacao
=======================================================
Classe abstrata base para todos os clients de portais de licitacao.
Define a interface padronizada que cada portal deve implementar,
alem de metodos utilitarios comuns (retry, parse, etc.).
"""

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BasePortalClient(ABC):
    """
    Classe abstrata base para clients de portais de licitacao.

    Todos os clients de portal (PNCP, ComprasNet, Licitacoes-e,
    e-Compras AM, BLL) devem herdar desta classe e implementar
    os metodos abstratos.
    """

    # Configuracoes padrao (sobreescrever nas subclasses)
    BASE_URL: str = ""
    TIMEOUT: float = 30.0
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.5
    PORTAL_NAME: str = "base"

    def __init__(self):
        """Inicializa o client HTTP base."""
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={
                "Accept": "text/html, application/json",
                "User-Agent": "ConectaPro/1.0",
                "Accept-Language": "pt-BR,pt;q=0.9",
            },
            follow_redirects=True,
        )

    async def close(self):
        """Fecha conexao HTTP."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # ---- Metodos abstratos (devem ser implementados) ----

    @abstractmethod
    async def buscar_oportunidades(self, **filters) -> list[dict[str, Any]]:
        """
        Busca oportunidades de licitacao no portal.

        Args:
            **filters: Filtros aceitos pelo portal (uf, data_inicial, termo, etc.)

        Returns:
            Lista de dicts compativeis com BiddingOpportunity
        """
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """
        Verifica disponibilidade do portal.

        Returns:
            Dict com 'disponivel' (bool), 'status_code', 'tempo_resposta_ms'
        """
        ...

    # ---- Metodos utilitarios comuns ----

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Executa request HTTP com retry e backoff exponencial.

        Trata rate limiting (HTTP 429) e erros de conexao
        com retries automaticos e backoff progressivo.

        Args:
            method: Metodo HTTP (GET, POST, etc.)
            url: URL do endpoint
            **kwargs: Argumentos adicionais para httpx

        Returns:
            httpx.Response

        Raises:
            httpx.ConnectError: Apos esgotar retries
        """
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code == 429:
                    wait = self.BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "%s rate limit atingido, aguardando %.1fs (tentativa %d/%d)",
                        self.PORTAL_NAME,
                        wait,
                        attempt + 1,
                        self.MAX_RETRIES,
                    )
                    await asyncio.sleep(wait)
                    continue
                return response
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_exc = e
                wait = self.BACKOFF_BASE * (2**attempt)
                logger.warning(
                    "%s erro de conexao, retry em %.1fs: %s",
                    self.PORTAL_NAME,
                    wait,
                    e,
                )
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError(f"Max retries exceeded for {self.PORTAL_NAME}")

    def _parse_date(self, value: str | None) -> datetime | None:
        """
        Faz parse de string de data em diversos formatos brasileiros.

        Args:
            value: String de data (dd/mm/yyyy, dd/mm/yyyy HH:MM, ISO, etc.)

        Returns:
            datetime ou None se parse falhar
        """
        if not value:
            return None
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None

    def _parse_valor(self, value: str | None) -> Decimal | None:
        """
        Faz parse de string de valor monetario brasileiro.

        Args:
            value: String de valor (R$ 1.234,56 ou 1234.56)

        Returns:
            Decimal ou None se parse falhar
        """
        if not value:
            return None
        try:
            cleaned = value.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return Decimal(cleaned) if cleaned else None
        except Exception:
            return None

    def _strip_html(self, text: str) -> str:
        """
        Remove tags HTML de uma string.

        Args:
            text: Texto com possiveis tags HTML

        Returns:
            Texto limpo
        """
        return re.sub(r"<[^>]+>", "", text).strip()

    def _to_opportunity_dict(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        Converte dados brutos do portal para formato padronizado.

        Subclasses devem sobreescrever este metodo para definir
        o campo 'portal' e mapeamentos especificos.

        Args:
            raw: Dados brutos extraidos do portal

        Returns:
            Dict compativel com BiddingOpportunity
        """
        return {
            "portal": self.PORTAL_NAME,
            "portal_id": str(raw.get("id") or raw.get("numero") or ""),
            "objeto": raw.get("objeto") or raw.get("descricao") or "",
            "valor_estimado": raw.get("valor_estimado"),
            "modalidade": raw.get("modalidade") or "",
            "orgao_nome": raw.get("orgao_nome") or raw.get("orgao") or "",
            "orgao_cnpj": raw.get("orgao_cnpj") or "",
            "uf": raw.get("uf") or "",
            "municipio": raw.get("municipio") or "",
            "data_publicacao": raw.get("data_publicacao"),
            "data_abertura": raw.get("data_abertura"),
            "data_encerramento": raw.get("data_encerramento"),
            "url_edital": raw.get("url_edital") or raw.get("link") or "",
            "status": "nova",
            "relevancia_score": 0,
        }
