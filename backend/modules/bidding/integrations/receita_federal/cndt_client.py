"""
Cliente para CNDT — Certidao Negativa de Debitos Trabalhistas
==============================================================
Consulta de CNDT no portal do Tribunal Superior do Trabalho (TST).

A CNDT e exigida para participacao em licitacoes publicas
(Lei 12.440/2011, que alterou a CLT e a Lei 8.666/93).
Validade: 180 dias a partir da emissao.
"""

import asyncio
import contextlib
import logging
import re
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class CNDTTrabalhistaClient:
    """
    Cliente HTTP para consulta de CNDT no portal do TST.

    A Certidao Negativa de Debitos Trabalhistas (CNDT) e emitida
    pelo Tribunal Superior do Trabalho e comprova a inexistencia
    de debitos trabalhistas no Banco Nacional de Devedores Trabalhistas.
    """

    # URL do servico de consulta CNDT
    BASE_URL = "https://www.tst.jus.br"
    CONSULTA_URL = "https://cndt-certidao.tst.jus.br/inicio.faces"
    API_CONSULTA_URL = "https://cndt-certidao.tst.jus.br/gerarCertidao"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 2.0

    # Tipos de certidao trabalhista
    TIPO_CNDT = "CNDT"  # Certidao Negativa
    TIPO_CPDT_EN = "CPDT-EN"  # Certidao Positiva com Efeito de Negativa
    TIPO_CPDT = "CPDT"  # Certidao Positiva

    VALIDADE_DIAS = 180

    def __init__(self):
        """Inicializa o client HTTP para CNDT."""
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
        """Executa request com retry e backoff exponencial."""
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code == 429:
                    wait = self.BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "CNDT rate limit, aguardando %.1fs (tentativa %d/%d)",
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
                logger.warning("CNDT erro de conexao, retry em %.1fs: %s", wait, e)
                await asyncio.sleep(wait)
        raise last_exc or httpx.ConnectError("Max retries exceeded for CNDT (TST)")

    def _format_cnpj(self, cnpj: str) -> str:
        """Remove formatacao do CNPJ, mantendo apenas digitos."""
        return re.sub(r"\D", "", cnpj)

    async def consultar_cndt(self, cnpj: str) -> dict[str, Any]:
        """
        Consulta CNDT (Certidao de Debitos Trabalhistas) de um CNPJ.

        Args:
            cnpj: CNPJ da empresa (com ou sem formatacao)

        Returns:
            Dict com status da certidao, tipo, validade e codigo de controle
        """
        cnpj_limpo = self._format_cnpj(cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError(f"CNPJ invalido: {cnpj}. Deve conter 14 digitos.")

        logger.info("Consultando CNDT para CNPJ %s", cnpj_limpo)

        try:
            # Etapa 1: Acessar pagina inicial para obter token/session
            init_response = await self._request_with_retry("GET", self.CONSULTA_URL)
            if init_response.status_code != 200:
                logger.warning("Pagina inicial CNDT retornou %d", init_response.status_code)

            # Etapa 2: Submeter consulta
            response = await self._request_with_retry(
                "POST",
                self.API_CONSULTA_URL,
                data={
                    "numCnpjCpf": cnpj_limpo,
                    "tipoPessoa": "J",  # J = Juridica
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

            return self._parse_resultado_cndt(response.text, cnpj_limpo)

        except Exception as e:
            logger.error("Erro ao consultar CNDT para %s: %s", cnpj_limpo, e)
            return {
                "cnpj": cnpj_limpo,
                "tipo_certidao": None,
                "situacao": "erro_consulta",
                "regular": False,
                "mensagem": str(e),
                "consultado_em": datetime.utcnow().isoformat(),
            }

    def _parse_resultado_cndt(self, html: str, cnpj: str) -> dict[str, Any]:
        """Extrai dados da CNDT do HTML de resposta do TST."""
        now = datetime.utcnow().isoformat()

        # Determinar tipo de certidao
        tipo_certidao = None
        if "Certidao Negativa" in html and "Positiva" not in html:
            tipo_certidao = self.TIPO_CNDT
        elif "Positiva com Efeitos de Negativa" in html or "Positiva com Efeito de Negativa" in html:
            tipo_certidao = self.TIPO_CPDT_EN
        elif "Certidao Positiva" in html:
            tipo_certidao = self.TIPO_CPDT

        # Extrair data de emissao
        emissao_match = re.search(
            r"[Ee]miss[aã]o.*?:\s*(\d{2}/\d{2}/\d{4})",
            html,
        )
        data_emissao = None
        if emissao_match:
            with contextlib.suppress(ValueError):
                data_emissao = datetime.strptime(emissao_match.group(1), "%d/%m/%Y").isoformat()

        # Extrair data de validade
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
            r"[Cc][oó]digo.*?[Cc]ontrole.*?:\s*([A-Z0-9.-]+)",
            html,
        )
        codigo_controle = codigo_match.group(1).strip() if codigo_match else None

        # Extrair numero da certidao
        numero_match = re.search(
            r"[Cc]ertid[aã]o\s+(?:N[º°.]?\s*)?([\d/.]+)",
            html,
        )
        numero_certidao = numero_match.group(1).strip() if numero_match else None

        regular = tipo_certidao in (self.TIPO_CNDT, self.TIPO_CPDT_EN)

        return {
            "cnpj": cnpj,
            "tipo_certidao": tipo_certidao,
            "numero_certidao": numero_certidao,
            "situacao": "regular" if regular else "irregular",
            "regular": regular,
            "data_emissao": data_emissao,
            "data_validade": data_validade,
            "codigo_controle": codigo_controle,
            "validade_dias": self.VALIDADE_DIAS,
            "emitida_por": "TST",
            "consultado_em": now,
        }

    async def verificar_debitos(self, cnpj: str) -> dict[str, Any]:
        """
        Verifica existencia de debitos trabalhistas de um CNPJ.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dict com 'possui_debitos' (bool), 'situacao' e 'detalhes'
        """
        resultado = await self.consultar_cndt(cnpj)

        possui_debitos = resultado.get("tipo_certidao") == self.TIPO_CPDT
        apto_licitar = resultado.get("regular", False)

        return {
            "cnpj": resultado["cnpj"],
            "possui_debitos": possui_debitos,
            "regular": resultado["regular"],
            "tipo_certidao": resultado.get("tipo_certidao"),
            "situacao": resultado.get("situacao"),
            "data_validade": resultado.get("data_validade"),
            "apto_licitar": apto_licitar,
            "observacao": (
                "Empresa sem debitos trabalhistas no BNDT"
                if not possui_debitos
                else "Empresa consta no BNDT — verificar debitos trabalhistas pendentes"
            ),
            "base_legal": "Lei 12.440/2011 (Art. 29, V da Lei 8.666/93)",
        }
