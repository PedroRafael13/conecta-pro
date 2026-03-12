"""
Cliente para Licitacoes-e (Banco do Brasil)
============================================
Portal de licitacoes eletronicas do Banco do Brasil.
https://www.licitacoes-e.com.br

O portal Licitacoes-e nao disponibiliza API publica REST,
portanto utiliza scraping HTTP com parsing via regex.
"""

import asyncio
import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LicitacoesEClient:
    """
    Cliente para o portal Licitacoes-e do Banco do Brasil.

    Plataforma de licitacoes eletronicas amplamente utilizada
    por orgaos publicos municipais, estaduais e federais.
    Como nao dispoe de API publica, utiliza scraping HTTP.
    """

    BASE_URL = "https://www.licitacoes-e.com.br"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.5

    # Segmentos disponiveis no portal
    SEGMENTOS = {
        "todos": "0",
        "bens": "1",
        "servicos": "2",
        "obras": "3",
        "saude": "4",
        "ti": "5",
    }

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={
                "Accept": "text/html, application/xhtml+xml, application/json",
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
                        "Licitacoes-e rate limit, aguardando %.1fs (tentativa %d/%d)",
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
                logger.warning("Licitacoes-e erro de conexao, retry em %.1fs: %s", wait, e)
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError("Max retries exceeded for Licitacoes-e")

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
        """Remove tags HTML."""
        return re.sub(r"<[^>]+>", "", text).strip()

    def _to_opportunity_dict(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Converte dados brutos para formato compativel com BiddingOpportunity."""
        return {
            "portal": "licitacoes_e",
            "portal_id": str(raw.get("id") or raw.get("numero") or raw.get("licitacao_id") or ""),
            "objeto": raw.get("objeto") or raw.get("descricao") or "",
            "valor_estimado": raw.get("valor_estimado"),
            "modalidade": raw.get("modalidade") or raw.get("tipo") or "",
            "orgao_nome": raw.get("orgao_nome") or raw.get("orgao") or raw.get("entidade") or "",
            "orgao_cnpj": raw.get("orgao_cnpj") or "",
            "uf": raw.get("uf") or "",
            "municipio": raw.get("municipio") or "",
            "data_publicacao": raw.get("data_publicacao"),
            "data_abertura": raw.get("data_abertura") or raw.get("data_inicio"),
            "data_encerramento": raw.get("data_encerramento") or raw.get("data_fim"),
            "url_edital": raw.get("url_edital") or raw.get("link") or "",
            "status": "nova",
            "relevancia_score": 0,
        }

    def _resolve_segmento(self, segmento: str | None) -> str:
        """Resolve nome de segmento para codigo do portal."""
        if not segmento:
            return self.SEGMENTOS["todos"]
        return self.SEGMENTOS.get(segmento.lower(), segmento)

    # ---- Metodos publicos ----

    async def health_check(self) -> dict[str, Any]:
        """Verifica disponibilidade do portal Licitacoes-e."""
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
        segmento: str | None = None,
        uf: str = "AM",
        data_inicial: date | None = None,
        pagina: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Busca editais no portal Licitacoes-e.

        Args:
            segmento: Segmento de licitacao (todos, bens, servicos, obras, saude, ti)
            uf: UF para filtrar
            data_inicial: Data a partir da qual buscar
            pagina: Pagina de resultados

        Returns:
            Lista de dicts compativeis com BiddingOpportunity
        """
        seg_code = self._resolve_segmento(segmento)

        # Tenta endpoint de consulta publica (POST com form data)
        form_data: dict[str, Any] = {
            "uf": uf,
            "segmento": seg_code,
            "pagina": str(pagina),
        }
        if data_inicial:
            form_data["dt_inicio"] = data_inicial.strftime("%d/%m/%Y")

        try:
            response = await self._request_with_retry(
                "POST",
                f"{self.BASE_URL}/aop/consultar/consultarLicitacao.aop",
                data=form_data,
            )
            if response.status_code == 200:
                return self._parse_html_resultados(response.text, uf)
        except Exception as e:
            logger.info("POST consulta Licitacoes-e falhou: %s", e)

        # Fallback: GET na pagina de pesquisa
        try:
            params = {"uf": uf, "segmento": seg_code}
            if data_inicial:
                params["dt_inicio"] = data_inicial.strftime("%d/%m/%Y")

            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/aop/pesquisar/pesquisarLicitacao.aop",
                params=params,
            )
            if response.status_code == 200:
                return self._parse_html_resultados(response.text, uf)
        except Exception as e:
            logger.error("Erro scraping Licitacoes-e: %s", e)

        return []

    def _parse_html_resultados(self, html: str, uf: str = "") -> list[dict[str, Any]]:
        """Extrai licitacoes do HTML de resultados do Licitacoes-e."""
        results: list[dict[str, Any]] = []

        # Padrao 1: tabela de resultados
        row_pattern = re.compile(
            r'<tr[^>]*class="[^"]*(?:linha|result|item)[^"]*"[^>]*>.*?</tr>',
            re.DOTALL | re.IGNORECASE,
        )
        td_pattern = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
        link_pattern = re.compile(
            r'href=["\']([^"\']*(?:detalhar|edital|licitacao)[^"\']*)["\']',
            re.IGNORECASE,
        )
        id_pattern = re.compile(r"(?:idLicitacao|id)=(\d+)", re.IGNORECASE)

        for row_match in row_pattern.finditer(html):
            row_html = row_match.group()
            cells = td_pattern.findall(row_html)
            if len(cells) >= 2:
                link_match = link_pattern.search(row_html)
                link = ""
                licitacao_id = ""
                if link_match:
                    link = link_match.group(1)
                    if not link.startswith("http"):
                        link = f"{self.BASE_URL}{link}"
                    id_match = id_pattern.search(link)
                    if id_match:
                        licitacao_id = id_match.group(1)

                raw: dict[str, Any] = {
                    "licitacao_id": licitacao_id or self._strip_html(cells[0]),
                    "objeto": self._strip_html(cells[1]) if len(cells) > 1 else "",
                    "entidade": self._strip_html(cells[2]) if len(cells) > 2 else "",
                    "modalidade": self._strip_html(cells[3]) if len(cells) > 3 else "",
                    "uf": uf,
                    "link": link,
                }

                if len(cells) > 4:
                    raw["data_abertura"] = self._parse_date(self._strip_html(cells[4]))
                if len(cells) > 5:
                    raw["valor_estimado"] = self._parse_valor(self._strip_html(cells[5]))

                if raw.get("objeto"):
                    results.append(self._to_opportunity_dict(raw))

        # Padrao 2: divs/cards
        if not results:
            card_pattern = re.compile(
                r"(?:Licita[çc][aã]o|Preg[aã]o|Edital)\s*(?:N[º°.]?\s*)?([\d/.]+).*?"
                r"(?:Objeto|Descri[çc][aã]o)\s*:?\s*(.*?)(?:<(?:br|/div|/p)|Entidade|[OÓ]rg[aã]o)",
                re.DOTALL | re.IGNORECASE,
            )
            for match in card_pattern.finditer(html):
                raw = {
                    "numero": match.group(1).strip(),
                    "objeto": self._strip_html(match.group(2)),
                    "uf": uf,
                }
                if raw["objeto"]:
                    results.append(self._to_opportunity_dict(raw))

        return results

    async def get_edital(self, edital_id: str) -> dict[str, Any] | None:
        """
        Busca detalhes de um edital especifico.

        Args:
            edital_id: Identificador da licitacao no portal
        """
        # Tenta POST (padrao do portal)
        try:
            response = await self._request_with_retry(
                "POST",
                f"{self.BASE_URL}/aop/consultar/detalharLicitacao.aop",
                data={"idLicitacao": edital_id},
            )
            if response.status_code == 200:
                return self._parse_detalhe_edital(response.text, edital_id)
        except Exception as e:
            logger.info("POST detalhe Licitacoes-e falhou: %s", e)

        # Fallback GET
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/aop/consultar/detalharLicitacao.aop",
                params={"idLicitacao": edital_id},
            )
            if response.status_code == 200:
                return self._parse_detalhe_edital(response.text, edital_id)
        except Exception as e:
            logger.error("Erro ao buscar edital %s: %s", edital_id, e)

        return None

    def _parse_detalhe_edital(self, html: str, edital_id: str) -> dict[str, Any] | None:
        """Extrai detalhes de um edital do HTML."""
        raw: dict[str, Any] = {"licitacao_id": edital_id}

        field_patterns = {
            "objeto": r"(?:Objeto|Descri[çc][aã]o)\s*:?\s*</(?:th|td|label|span|strong|b)>\s*<(?:td|span|div|p)[^>]*>(.*?)</",
            "orgao": r"(?:Entidade|[OÓ]rg[aã]o)\s*:?\s*</(?:th|td|label|span|strong|b)>\s*<(?:td|span|div|p)[^>]*>(.*?)</",
            "modalidade": r"(?:Modalidade|Tipo)\s*:?\s*</(?:th|td|label|span|strong|b)>\s*<(?:td|span|div|p)[^>]*>(.*?)</",
            "uf": r"(?:UF|Estado)\s*:?\s*</(?:th|td|label|span|strong|b)>\s*<(?:td|span|div|p)[^>]*>(.*?)</",
            "municipio": r"(?:Munic[ií]pio|Cidade)\s*:?\s*</(?:th|td|label|span|strong|b)>\s*<(?:td|span|div|p)[^>]*>(.*?)</",
        }

        for field, pattern in field_patterns.items():
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                raw[field] = self._strip_html(match.group(1))

        # Valor estimado
        valor_match = re.search(
            r"Valor\s+(?:Estimado|Total|Global|Referencia).*?R\$\s*([\d.,]+)",
            html,
            re.IGNORECASE,
        )
        if valor_match:
            raw["valor_estimado"] = self._parse_valor(valor_match.group(1))

        # Data abertura
        abertura_match = re.search(
            r"(?:Data|In[ií]cio).*?(?:Abertura|Disputa|Sessao).*?:\s*(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2})?)",
            html,
            re.IGNORECASE,
        )
        if abertura_match:
            raw["data_abertura"] = self._parse_date(abertura_match.group(1))

        # Data encerramento
        encerramento_match = re.search(
            r"(?:Data|T[eé]rmino).*?(?:Encerramento|Fim|Proposta).*?:\s*(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2})?)",
            html,
            re.IGNORECASE,
        )
        if encerramento_match:
            raw["data_encerramento"] = self._parse_date(encerramento_match.group(1))

        # Link do edital/arquivo
        edital_link_match = re.search(
            r'href=["\']([^"\']*(?:download|arquivo|edital\.pdf)[^"\']*)["\']',
            html,
            re.IGNORECASE,
        )
        if edital_link_match:
            link = edital_link_match.group(1)
            if not link.startswith("http"):
                link = f"{self.BASE_URL}{link}"
            raw["url_edital"] = link

        return self._to_opportunity_dict(raw) if raw.get("objeto") else None

    async def buscar_por_objeto(self, termo: str, uf: str = "AM", pagina: int = 1) -> list[dict[str, Any]]:
        """
        Busca licitacoes por termo no objeto.

        Args:
            termo: Texto para buscar no objeto
            uf: UF para filtrar
            pagina: Pagina de resultados
        """
        # POST com campo de texto
        form_data = {
            "uf": uf,
            "objeto": termo,
            "pagina": str(pagina),
        }

        try:
            response = await self._request_with_retry(
                "POST",
                f"{self.BASE_URL}/aop/consultar/consultarLicitacao.aop",
                data=form_data,
            )
            if response.status_code == 200:
                return self._parse_html_resultados(response.text, uf)
        except Exception as e:
            logger.info("Busca por objeto Licitacoes-e falhou: %s", e)

        # Fallback GET
        try:
            response = await self._request_with_retry(
                "GET",
                f"{self.BASE_URL}/aop/pesquisar/pesquisarLicitacao.aop",
                params={"uf": uf, "texto": termo},
            )
            if response.status_code == 200:
                all_results = self._parse_html_resultados(response.text, uf)
                if termo:
                    termo_lower = termo.lower()
                    return [r for r in all_results if termo_lower in r.get("objeto", "").lower()]
                return all_results
        except Exception as e:
            logger.error("Erro fallback busca por objeto: %s", e)

        return []

    async def buscar_oportunidades(self, **filters) -> list[dict[str, Any]]:
        """
        Metodo padronizado para buscar oportunidades.

        Retorna lista de dicts compativeis com BiddingOpportunity.

        Filtros aceitos:
            uf, segmento, data_inicial, termo, pagina
        """
        termo = filters.get("termo")
        if termo:
            return await self.buscar_por_objeto(
                termo=termo,
                uf=filters.get("uf", "AM"),
                pagina=filters.get("pagina", 1),
            )
        return await self.buscar_editais(
            segmento=filters.get("segmento"),
            uf=filters.get("uf", "AM"),
            data_inicial=filters.get("data_inicial"),
            pagina=filters.get("pagina", 1),
        )
