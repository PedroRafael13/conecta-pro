"""
Cliente para CND Federal — Receita Federal + PGFN
===================================================
Consulta de Certidao Negativa de Debitos relativos a Creditos
Tributarios Federais e a Divida Ativa da Uniao (Receita Federal + PGFN).

A consulta e feita via portal e-CAC / Regularize da PGFN.
Certidao unica RFB/PGFN (Portaria Conjunta 1.751/2014).
"""

import asyncio
import contextlib
import logging
import re
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class CNDFederalClient:
    """
    Cliente HTTP para consulta de CND Federal (RFB + PGFN).

    A Certidao Negativa de Debitos (CND) Federal e emitida
    conjuntamente pela Receita Federal e pela Procuradoria-Geral
    da Fazenda Nacional, tendo validade de 180 dias.
    """

    # URLs dos servicos
    BASE_URL_RFB = "https://servicos.receita.fazenda.gov.br"
    BASE_URL_PGFN = "https://www.regularize.pgfn.gov.br"
    CONSULTA_URL = "https://solucoes.receita.fazenda.gov.br/Servicos/CertidaoInternet/CND/Consulta"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 2.0

    # Tipos de certidao
    TIPO_CND = "CND"  # Certidao Negativa de Debitos
    TIPO_CPDEN = "CPDEN"  # Certidao Positiva com Efeito de Negativa
    TIPO_CPD = "CPD"  # Certidao Positiva de Debitos

    VALIDADE_DIAS = 180

    def __init__(self):
        """Inicializa o client HTTP para CND Federal."""
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={
                "Accept": "text/html, application/json, application/xml",
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

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Executa request com retry e backoff para rate limiting."""
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code == 429:
                    wait = self.BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "CND Federal rate limit, aguardando %.1fs (tentativa %d/%d)",
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
                logger.warning("CND Federal erro de conexao, retry em %.1fs: %s", wait, e)
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError("Max retries exceeded for CND Federal")

    def _format_cnpj(self, cnpj: str) -> str:
        """Remove formatacao do CNPJ, mantendo apenas digitos."""
        return re.sub(r"\D", "", cnpj)

    async def consultar_cnd(self, cnpj: str) -> dict[str, Any]:
        """
        Consulta CND Federal (RFB + PGFN) de um CNPJ.

        Args:
            cnpj: CNPJ da empresa (com ou sem formatacao)

        Returns:
            Dict com status da certidao, tipo, validade e URL
        """
        cnpj_limpo = self._format_cnpj(cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError(f"CNPJ invalido: {cnpj}. Deve conter 14 digitos.")

        logger.info("Consultando CND Federal para CNPJ %s", cnpj_limpo)

        try:
            response = await self._request_with_retry(
                "POST",
                self.CONSULTA_URL,
                data={
                    "NI": cnpj_limpo,
                    "Tipo": "2",  # 2 = CNPJ
                },
            )

            if response.status_code != 200:
                return {
                    "cnpj": cnpj_limpo,
                    "tipo_certidao": None,
                    "situacao": "erro_consulta",
                    "regular": False,
                    "mensagem": f"Erro HTTP: {response.status_code}",
                    "consultado_em": datetime.utcnow().isoformat(),
                }

            return self._parse_resultado_cnd(response.text, cnpj_limpo)

        except Exception as e:
            logger.error("Erro ao consultar CND Federal para %s: %s", cnpj_limpo, e)
            return {
                "cnpj": cnpj_limpo,
                "tipo_certidao": None,
                "situacao": "erro_consulta",
                "regular": False,
                "mensagem": str(e),
                "consultado_em": datetime.utcnow().isoformat(),
            }

    def _parse_resultado_cnd(self, html: str, cnpj: str) -> dict[str, Any]:
        """Extrai dados da certidao do HTML de resposta."""
        now = datetime.utcnow().isoformat()

        # Verificar tipo de certidao
        tipo_certidao = None
        if "Certidao Negativa" in html and "Positiva" not in html:
            tipo_certidao = self.TIPO_CND
        elif "Positiva com Efeitos de Negativa" in html:
            tipo_certidao = self.TIPO_CPDEN
        elif "Certidao Positiva" in html:
            tipo_certidao = self.TIPO_CPD

        # Extrair validade
        validade_match = re.search(
            r"[Vv]alidade.*?:\s*(\d{2}/\d{2}/\d{4})",
            html,
        )
        data_validade = None
        if validade_match:
            with contextlib.suppress(ValueError):
                data_validade = datetime.strptime(validade_match.group(1), "%d/%m/%Y").isoformat()

        # Extrair codigo de controle
        codigo_match = re.search(
            r"[Cc][oó]digo\s+(?:de\s+)?[Cc]ontrole.*?:\s*([A-Z0-9.-]+)",
            html,
        )
        codigo_controle = codigo_match.group(1).strip() if codigo_match else None

        regular = tipo_certidao in (self.TIPO_CND, self.TIPO_CPDEN)

        return {
            "cnpj": cnpj,
            "tipo_certidao": tipo_certidao,
            "situacao": "regular" if regular else "irregular",
            "regular": regular,
            "data_validade": data_validade,
            "codigo_controle": codigo_controle,
            "validade_dias": self.VALIDADE_DIAS,
            "emitida_por": "RFB/PGFN",
            "consultado_em": now,
        }

    async def verificar_regularidade(self, cnpj: str) -> dict[str, Any]:
        """
        Verifica regularidade fiscal federal de um CNPJ.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dict com 'regular' (bool), 'tipo_certidao' e 'detalhes'
        """
        resultado = await self.consultar_cnd(cnpj)
        return {
            "cnpj": resultado["cnpj"],
            "regular": resultado["regular"],
            "tipo_certidao": resultado.get("tipo_certidao"),
            "situacao": resultado.get("situacao"),
            "data_validade": resultado.get("data_validade"),
            "apto_licitar": resultado["regular"],
            "observacao": (
                "Empresa regular perante a Receita Federal e PGFN"
                if resultado["regular"]
                else "Empresa com pendencias fiscais federais — verificar debitos RFB/PGFN"
            ),
        }

    def get_certidao_url(self, tipo: str = "cnd") -> str:
        """
        Retorna URL para emissao/consulta de certidao.

        Args:
            tipo: Tipo de certidao (cnd, pgfn, regularize)

        Returns:
            URL do servico correspondente
        """
        urls = {
            "cnd": self.CONSULTA_URL,
            "pgfn": f"{self.BASE_URL_PGFN}/api/consulta",
            "regularize": self.BASE_URL_PGFN,
            "ecac": f"{self.BASE_URL_RFB}/ecac",
        }
        url = urls.get(tipo.lower())
        if not url:
            raise ValueError(f"Tipo de certidao invalido: {tipo}. Validos: {list(urls.keys())}")
        return url
