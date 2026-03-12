"""
Cliente para e-Compras AM
=========================
Portal de compras do Estado do Amazonas.
https://www.e-compras.am.gov.br

O portal e-Compras AM nao dispoe de API publica documentada,
portanto utiliza scraping HTTP com fallback via regex.
"""

import asyncio
import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class EComprasAMClient:
    """
    Cliente para o portal e-Compras AM (Amazonas).

    Portal de compras eletronicas do Governo do Estado do Amazonas.
    Como nao ha API publica documentada, o client faz scraping
    das paginas HTML com parsing via regex.
    """

    BASE_URL = "https://www.e-compras.am.gov.br"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.5

    def __init__(self):
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
                        "e-Compras AM rate limit, aguardando %.1fs (tentativa %d/%d)",
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
                logger.warning("e-Compras AM erro de conexao, retry em %.1fs: %s", wait, e)
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError("Max retries exceeded for e-Compras AM")

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

    def _strip_html(self, text: str) -> str:
        """Remove tags HTML de uma string."""
        return re.sub(r"<[^>]+>", "", text).strip()

    def _to_opportunity_dict(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Converte dados brutos para formato compativel com BiddingOpportunity."""
        return {
            "portal": "ecompras_am",
            "portal_id": str(raw.get("id") or raw.get("numero") or ""),
            "objeto": raw.get("objeto") or raw.get("descricao") or "",
            "valor_estimado": raw.get("valor_estimado"),
            "modalidade": raw.get("modalidade") or "",
            "orgao_nome": raw.get("orgao_nome") or raw.get("orgao") or "",
            "orgao_cnpj": raw.get("orgao_cnpj") or "",
            "uf": "AM",
            "municipio": raw.get("municipio") or "Manaus",
            "data_publicacao": raw.get("data_publicacao"),
            "data_abertura": raw.get("data_abertura"),
            "data_encerramento": raw.get("data_encerramento"),
            "url_edital": raw.get("url_edital") or raw.get("link") or "",
            "status": "nova",
            "relevancia_score": 0,
        }

    # ---- Metodos publicos ----

    async def health_check(self) -> dict[str, Any]:
        """Verifica disponibilidade do portal e-Compras AM."""
        try:
            response = await self._request_with_retry("GET", self.BASE_URL)
            return {
                "disponivel": response.status_code == 200,
                "status_code": response.status_code,
                "tempo_resposta_ms": response.elapsed.total_seconds() * 1000,
            }
        except Exception as e:
            return {"disponivel": False, "erro": str(e)}

    async def buscar_editais(
        self,
        data_inicial: date | None = None,
        data_final: date | None = None,
        pagina: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Busca editais publicados no e-Compras AM.

        Args:
            data_inicial: Data inicial do filtro
            data_final: Data final do filtro
            pagina: Pagina de resultados

        Returns:
            Lista de dicts compativeis com BiddingOpportunity
        """
        params: dict[str, Any] = {"pagina": pagina}
        if data_inicial:
            params["dt_inicio"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dt_fim"] = data_final.strftime("%d/%m/%Y")

        # Tenta busca via endpoint de consulta (possivel API interna)
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/publico/editais/consulta",
                params=params,
            )
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    data = response.json()
                    results = data if isinstance(data, list) else data.get("editais", data.get("resultados", []))
                    return [self._to_opportunity_dict(r) for r in results]
                else:
                    return self._parse_html_editais(response.text)
        except Exception as e:
            logger.info("e-Compras AM consulta indisponivel, tentando scraping: %s", e)

        # Fallback: pagina principal de editais
        return await self._scrape_editais(data_inicial, data_final)

    async def _scrape_editais(
        self,
        data_inicial: date | None,
        data_final: date | None,
    ) -> list[dict[str, Any]]:
        """Scraping da pagina de editais do e-Compras AM."""
        params: dict[str, str] = {}
        if data_inicial:
            params["dt_inicio"] = data_inicial.strftime("%d/%m/%Y")
        if data_final:
            params["dt_fim"] = data_final.strftime("%d/%m/%Y")

        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/publico/editais",
                params=params,
            )
            if response.status_code != 200:
                logger.warning("Scraping e-Compras AM retornou %d", response.status_code)
                return []
            return self._parse_html_editais(response.text)
        except Exception as e:
            logger.error("Erro scraping e-Compras AM: %s", e)
            return []

    def _parse_html_editais(self, html: str) -> list[dict[str, Any]]:
        """Extrai editais de HTML do e-Compras AM via regex."""
        results: list[dict[str, Any]] = []

        # Padrao 1: tabela de editais
        row_pattern = re.compile(r"<tr[^>]*>.*?</tr>", re.DOTALL | re.IGNORECASE)
        td_pattern = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
        link_pattern = re.compile(r'href=["\']([^"\']*edital[^"\']*)["\']', re.IGNORECASE)

        for row_match in row_pattern.finditer(html):
            row_html = row_match.group()
            cells = td_pattern.findall(row_html)
            if len(cells) >= 3:
                link_match = link_pattern.search(row_html)
                link = link_match.group(1) if link_match else ""
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL}{link}"

                raw = {
                    "numero": self._strip_html(cells[0]),
                    "objeto": self._strip_html(cells[1]) if len(cells) > 1 else "",
                    "modalidade": self._strip_html(cells[2]) if len(cells) > 2 else "",
                    "orgao_nome": self._strip_html(cells[3]) if len(cells) > 3 else "",
                    "data_publicacao": self._parse_date(self._strip_html(cells[4])) if len(cells) > 4 else None,
                    "data_abertura": self._parse_date(self._strip_html(cells[5])) if len(cells) > 5 else None,
                    "link": link,
                }

                valor_col = self._strip_html(cells[6]) if len(cells) > 6 else ""
                if valor_col:
                    raw["valor_estimado"] = self._parse_valor(valor_col)

                if raw.get("objeto"):
                    results.append(self._to_opportunity_dict(raw))

        # Padrao 2: divs ou cards
        if not results:
            edital_pattern = re.compile(
                r"(?:Edital|Processo)\s*(?:N[º°.]?\s*)?([\d/.]+).*?"
                r"(?:Objeto|Descri[çc][aã]o)\s*:\s*(.*?)(?:<|Modalidade|Valor)",
                re.DOTALL | re.IGNORECASE,
            )
            for match in edital_pattern.finditer(html):
                raw = {
                    "numero": match.group(1).strip(),
                    "objeto": self._strip_html(match.group(2)),
                }
                if raw["objeto"]:
                    results.append(self._to_opportunity_dict(raw))

        return results

    async def get_edital(self, edital_id: str) -> dict[str, Any] | None:
        """
        Busca detalhes de um edital especifico.

        Args:
            edital_id: Identificador do edital no portal
        """
        # Tenta endpoint direto
        try:
            response = await self._request_with_retry("GET", f"{self.BASE_URL}/publico/editais/{edital_id}")
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    return self._to_opportunity_dict(response.json())
                else:
                    return self._parse_detalhe_edital(response.text, edital_id)
        except Exception as e:
            logger.error("Erro ao buscar edital %s: %s", edital_id, e)

        return None

    def _parse_detalhe_edital(self, html: str, edital_id: str) -> dict[str, Any] | None:
        """Extrai detalhes de edital de pagina HTML."""
        raw: dict[str, Any] = {"id": edital_id}

        obj_match = re.search(
            r"(?:Objeto|Descri[çc][aã]o).*?:\s*</(?:th|td|label|span|strong)>\s*"
            r"<(?:td|span|div|p)[^>]*>(.*?)</",
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if obj_match:
            raw["objeto"] = self._strip_html(obj_match.group(1))

        orgao_match = re.search(
            r"[OÓ]rg[aã]o.*?:\s*</(?:th|td|label|span|strong)>\s*"
            r"<(?:td|span|div|p)[^>]*>(.*?)</",
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if orgao_match:
            raw["orgao_nome"] = self._strip_html(orgao_match.group(1))

        valor_match = re.search(
            r"Valor\s+(?:Estimado|Total|Global).*?R\$\s*([\d.,]+)",
            html,
            re.IGNORECASE,
        )
        if valor_match:
            raw["valor_estimado"] = self._parse_valor(valor_match.group(1))

        modalidade_match = re.search(
            r"Modalidade.*?:\s*</(?:th|td|label|span|strong)>\s*"
            r"<(?:td|span|div|p)[^>]*>(.*?)</",
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if modalidade_match:
            raw["modalidade"] = self._strip_html(modalidade_match.group(1))

        abertura_match = re.search(
            r"(?:Data\s+de\s+)?Abertura.*?:\s*(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2})?)",
            html,
            re.IGNORECASE,
        )
        if abertura_match:
            raw["data_abertura"] = self._parse_date(abertura_match.group(1))

        return self._to_opportunity_dict(raw) if raw.get("objeto") else None

    async def buscar_por_objeto(self, termo: str, pagina: int = 1) -> list[dict[str, Any]]:
        """
        Busca editais por termo no objeto.

        Args:
            termo: Texto para buscar no objeto da licitacao
            pagina: Pagina de resultados
        """
        params: dict[str, Any] = {
            "texto": termo,
            "pagina": pagina,
        }

        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/publico/editais/consulta",
                params=params,
            )
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "json" in content_type:
                    data = response.json()
                    results = data if isinstance(data, list) else data.get("editais", data.get("resultados", []))
                    return [self._to_opportunity_dict(r) for r in results]
                else:
                    return self._parse_html_editais(response.text)
        except Exception as e:
            logger.error("Erro busca por objeto e-Compras AM: %s", e)

        # Fallback: busca geral e filtra localmente
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/publico/editais",
                params={"texto": termo},
            )
            if response.status_code == 200:
                all_results = self._parse_html_editais(response.text)
                termo_lower = termo.lower()
                return [r for r in all_results if termo_lower in r.get("objeto", "").lower()]
        except Exception as e:
            logger.error("Erro fallback busca por objeto: %s", e)

        return []

    async def buscar_oportunidades(self, **filters) -> list[dict[str, Any]]:
        """
        Metodo padronizado para buscar oportunidades.

        Retorna lista de dicts compativeis com BiddingOpportunity.

        Filtros aceitos:
            data_inicial, data_final, termo, pagina
        """
        termo = filters.get("termo")
        if termo:
            return await self.buscar_por_objeto(
                termo=termo,
                pagina=filters.get("pagina", 1),
            )
        return await self.buscar_editais(
            data_inicial=filters.get("data_inicial"),
            data_final=filters.get("data_final"),
            pagina=filters.get("pagina", 1),
        )
