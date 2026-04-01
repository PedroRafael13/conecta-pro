"""
Cliente para Compras.gov.br (ComprasNet)
========================================
Portal de compras do Governo Federal (antigo ComprasNet).
Utiliza a API publica do Compras.gov.br quando disponivel,
com fallback para scraping da pagina de resultados.
"""

import asyncio
import logging
import re
from datetime import date, datetime
from decimal import Decimal
from html.parser import HTMLParser
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class _PregaoHTMLParser(HTMLParser):
    """Parser simplificado para extrair pregoes de paginas HTML do ComprasNet."""

    def __init__(self):
        super().__init__()
        self.resultados: list[dict] = []
        self._current: dict[str, Any] = {}
        self._capture_tag: str | None = None
        self._capture_data: str = ""
        self._in_result_row = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)
        css_class = attrs_dict.get("class", "") or ""

        if tag == "tr" and "resultado" in css_class:
            self._in_result_row = True
            self._current = {}

        if self._in_result_row and tag == "td":
            data_field = attrs_dict.get("data-field", "")
            if data_field:
                self._capture_tag = data_field
                self._capture_data = ""

        if tag == "a" and self._in_result_row:
            href = attrs_dict.get("href", "")
            if href:
                self._current["link"] = href

    def handle_data(self, data: str):
        if self._capture_tag:
            self._capture_data += data.strip()

    def handle_endtag(self, tag: str):
        if self._capture_tag and tag == "td":
            self._current[self._capture_tag] = self._capture_data
            self._capture_tag = None
            self._capture_data = ""

        if tag == "tr" and self._in_result_row:
            if self._current:
                self.resultados.append(self._current)
            self._current = {}
            self._in_result_row = False


class ComprasNetClient:
    """
    Cliente para Compras.gov.br (antigo ComprasNet).

    O portal Compras.gov.br e a plataforma de compras do Governo Federal.
    Utiliza endpoints da API publica e scraping como fallback.
    """

    BASE_URL = "https://www.gov.br/compras"
    API_URL = "https://contratos.comprasnet.gov.br/api"
    SEARCH_URL = "https://www.gov.br/compras/pt-br/acesso-a-informacao/consultas"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.0

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={
                "Accept": "application/json, text/html",
                "User-Agent": "ConectaPro/1.0",
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

    # ---- Helpers ----

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Executa request com retry e backoff para rate limiting."""
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code == 429:
                    wait = self.BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "ComprasNet rate limit atingido, aguardando %.1fs (tentativa %d/%d)",
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
                logger.warning("ComprasNet erro de conexao, retry em %.1fs: %s", wait, e)
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError("Max retries exceeded for ComprasNet")

    def _parse_date(self, value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None

    def _parse_valor(self, value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            cleaned = value.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return Decimal(cleaned) if cleaned else None
        except Exception:
            return None

    def _to_opportunity_dict(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Converte dados brutos para formato compativel com BiddingOpportunity."""
        return {
            "portal": "comprasnet",
            "portal_id": raw.get("numero") or raw.get("id") or raw.get("codigoUasg", ""),
            "objeto": raw.get("objeto") or raw.get("descricao") or "",
            "valor_estimado": raw.get("valor_estimado"),
            "modalidade": raw.get("modalidade") or "Pregao Eletronico",
            "orgao_nome": raw.get("orgao_nome") or raw.get("nomeUasg") or raw.get("unidadeGestora", ""),
            "orgao_cnpj": raw.get("orgao_cnpj") or raw.get("cnpj") or "",
            "uf": raw.get("uf") or "",
            "municipio": raw.get("municipio") or "",
            "data_publicacao": raw.get("data_publicacao"),
            "data_abertura": raw.get("data_abertura"),
            "data_encerramento": raw.get("data_encerramento"),
            "url_edital": raw.get("url_edital") or raw.get("link") or "",
            "status": "nova",
            "relevancia_score": 0,
        }

    # ---- API Publica ----

    async def health_check(self) -> dict[str, Any]:
        """Verifica disponibilidade do portal."""
        try:
            response = await self._request_with_retry("GET", self.BASE_URL)
            return {
                "disponivel": response.status_code == 200,
                "status_code": response.status_code,
                "tempo_resposta_ms": response.elapsed.total_seconds() * 1000,
            }
        except Exception as e:
            return {"disponivel": False, "erro": str(e)}

    async def buscar_pregoes(
        self,
        uf: str = "AM",
        data_inicial: date | None = None,
        data_final: date | None = None,
        pagina: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Busca pregoes eletronicos no ComprasNet.

        Tenta API publica primeiro; se falhar, faz scraping da pagina.
        """
        params: dict[str, Any] = {
            "uf": uf,
            "pagina": pagina,
            "tipo": "pregao_eletronico",
        }
        if data_inicial:
            params["dataInicial"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dataFinal"] = data_final.strftime("%d/%m/%Y")

        # Tenta API publica
        try:
            response = await self._request_with_retry("GET", f"{self.API_URL}/consulta/v1/pregoes", params=params)
            if response.status_code == 200:
                data = response.json()
                results = data if isinstance(data, list) else data.get("resultados", [])
                return [self._to_opportunity_dict(r) for r in results]
        except Exception as e:
            logger.info("API ComprasNet indisponivel, tentando scraping: %s", e)

        # Fallback: scraping
        return await self._scrape_pregoes(uf, data_inicial, data_final)

    async def _scrape_pregoes(
        self,
        uf: str,
        data_inicial: date | None,
        data_final: date | None,
    ) -> list[dict[str, Any]]:
        """Scraping de pregoes a partir de pagina HTML do ComprasNet."""
        params: dict[str, str] = {"uf": uf}
        if data_inicial:
            params["dt_inicio"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dt_fim"] = data_final.strftime("%d/%m/%Y")

        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.SEARCH_URL}/pregao-eletronico",
                params=params,
                headers={"Accept": "text/html"},
            )
            if response.status_code != 200:
                logger.warning("Scraping ComprasNet retornou %d", response.status_code)
                return []

            html = response.text
            return self._parse_html_pregoes(html)
        except Exception as e:
            logger.error("Erro no scraping ComprasNet: %s", e)
            return []

    def _parse_html_pregoes(self, html: str) -> list[dict[str, Any]]:
        """Extrai pregoes do HTML usando regex e parser."""
        results: list[dict[str, Any]] = []

        # Tenta parser estruturado
        parser = _PregaoHTMLParser()
        try:
            parser.feed(html)
            for item in parser.resultados:
                results.append(self._to_opportunity_dict(item))
        except Exception:  # noqa: S110
            pass

        if results:
            return results

        # Fallback regex para layouts comuns
        pattern = re.compile(
            r"Preg[aã]o\s+(?:Eletr[oô]nico)?\s*(?:N[º°.]?\s*)?([\d/]+).*?"
            r"Objeto:\s*(.*?)(?:<|$)",
            re.DOTALL | re.IGNORECASE,
        )
        for match in pattern.finditer(html):
            results.append(
                self._to_opportunity_dict(
                    {
                        "numero": match.group(1).strip(),
                        "objeto": re.sub(r"<[^>]+>", "", match.group(2)).strip(),
                    }
                )
            )

        return results

    async def get_pregao(self, numero: str) -> dict[str, Any] | None:
        """
        Busca detalhes de um pregao especifico.

        Args:
            numero: Numero do pregao (ex: "05/2026")
        """
        try:
            response = await self._request_with_retry("GET", f"{self.API_URL}/consulta/v1/pregoes/{numero}")
            if response.status_code == 200:
                data = response.json()
                return self._to_opportunity_dict(data)
        except Exception as e:
            logger.error("Erro ao buscar pregao %s: %s", numero, e)

        # Fallback: busca na pagina de detalhes
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.SEARCH_URL}/pregao-eletronico/{numero}",
                headers={"Accept": "text/html"},
            )
            if response.status_code == 200:
                return self._parse_detalhe_pregao(response.text, numero)
        except Exception as e:
            logger.error("Erro scraping pregao %s: %s", numero, e)

        return None

    def _parse_detalhe_pregao(self, html: str, numero: str) -> dict[str, Any] | None:
        """Extrai dados de detalhe de pregao via regex."""
        data: dict[str, Any] = {"numero": numero}

        obj_match = re.search(
            r"Objeto.*?:\s*</(?:th|td|span)>\s*<(?:td|span)[^>]*>(.*?)</",
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if obj_match:
            data["objeto"] = re.sub(r"<[^>]+>", "", obj_match.group(1)).strip()

        valor_match = re.search(
            r"Valor\s+(?:Estimado|Total).*?R\$\s*([\d.,]+)",
            html,
            re.IGNORECASE,
        )
        if valor_match:
            data["valor_estimado"] = self._parse_valor(valor_match.group(1))

        uasg_match = re.search(
            r"UASG.*?:\s*</(?:th|td|span)>\s*<(?:td|span)[^>]*>(.*?)</",
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if uasg_match:
            data["orgao_nome"] = re.sub(r"<[^>]+>", "", uasg_match.group(1)).strip()

        return self._to_opportunity_dict(data) if data.get("objeto") else None

    async def buscar_por_objeto(self, termo: str, uf: str = "AM", pagina: int = 1) -> list[dict[str, Any]]:
        """Busca pregoes por termo no objeto."""
        params: dict[str, Any] = {
            "uf": uf,
            "objeto": termo,
            "pagina": pagina,
        }

        try:
            response = await self._request_with_retry("GET", f"{self.API_URL}/consulta/v1/pregoes", params=params)
            if response.status_code == 200:
                data = response.json()
                results = data if isinstance(data, list) else data.get("resultados", [])
                return [self._to_opportunity_dict(r) for r in results]
        except Exception as e:
            logger.info("API busca por objeto indisponivel: %s", e)

        # Fallback scraping
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.SEARCH_URL}/pregao-eletronico",
                params={"texto": termo, "uf": uf},
                headers={"Accept": "text/html"},
            )
            if response.status_code == 200:
                return self._parse_html_pregoes(response.text)
        except Exception as e:
            logger.error("Erro scraping busca por objeto: %s", e)

        return []

    async def get_ata_sessao(self, pregao_id: str) -> dict[str, Any] | None:
        """
        Busca ata de sessao de um pregao.

        Args:
            pregao_id: Identificador do pregao
        """
        try:
            response = await self._request_with_retry("GET", f"{self.API_URL}/consulta/v1/pregoes/{pregao_id}/ata")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.info("API ata indisponivel: %s", e)

        # Fallback scraping
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.SEARCH_URL}/pregao-eletronico/{pregao_id}/ata",
                headers={"Accept": "text/html"},
            )
            if response.status_code == 200:
                html = response.text
                content_match = re.search(
                    r'<div[^>]*class="[^"]*ata[^"]*"[^>]*>(.*?)</div>',
                    html,
                    re.DOTALL | re.IGNORECASE,
                )
                if content_match:
                    texto = re.sub(r"<[^>]+>", "\n", content_match.group(1)).strip()
                    return {"pregao_id": pregao_id, "conteudo": texto}
        except Exception as e:
            logger.error("Erro scraping ata: %s", e)

        return None

    async def buscar_oportunidades(self, **filters) -> list[dict[str, Any]]:
        """
        Metodo padronizado para buscar oportunidades.

        Retorna lista de dicts compativeis com BiddingOpportunity.

        Filtros aceitos:
            uf, data_inicial, data_final, termo, pagina
        """
        termo = filters.get("termo")
        if termo:
            return await self.buscar_por_objeto(
                termo=termo,
                uf=filters.get("uf", "AM"),
                pagina=filters.get("pagina", 1),
            )
        return await self.buscar_pregoes(
            uf=filters.get("uf", "AM"),
            data_inicial=filters.get("data_inicial"),
            data_final=filters.get("data_final"),
            pagina=filters.get("pagina", 1),
        )
