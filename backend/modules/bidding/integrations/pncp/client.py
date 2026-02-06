"""
Cliente HTTP para API do PNCP
=============================
Portal Nacional de Contratacoes Publicas
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

import httpx

from modules.bidding.integrations.pncp.models import (
    PNCPCompra, PNCPContrato, PNCPResponse, PNCPSearchParams
)
from modules.bidding.integrations.pncp.parser import PNCPParser

logger = logging.getLogger(__name__)


class PNCPClient:
    """Cliente para API do Portal Nacional de Contratacoes Publicas."""

    BASE_URL = "https://pncp.gov.br/api/pncp"
    TIMEOUT = 30.0

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={
                "Accept": "application/json",
                "User-Agent": "ConectaPro/1.0"
            }
        )
        self.parser = PNCPParser()

    async def close(self):
        """Fecha conexao HTTP."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def health_check(self) -> Dict[str, Any]:
        """Verifica disponibilidade da API."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/compras",
                params={"pagina": 1, "tamanhoPagina": 1}
            )
            return {
                "disponivel": response.status_code == 200,
                "status_code": response.status_code,
                "tempo_resposta_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "disponivel": False,
                "erro": str(e)
            }

    async def buscar_compras(
        self,
        params: PNCPSearchParams
    ) -> PNCPResponse:
        """
        Busca compras no PNCP.

        Args:
            params: Parametros de busca

        Returns:
            PNCPResponse com lista de compras
        """
        query_params = {
            "pagina": params.pagina,
            "tamanhoPagina": params.tamanho_pagina
        }

        if params.uf:
            query_params["uf"] = params.uf

        if params.data_inicial:
            query_params["dataInicial"] = params.data_inicial.strftime("%Y-%m-%d")

        if params.data_final:
            query_params["dataFinal"] = params.data_final.strftime("%Y-%m-%d")

        if params.modalidade:
            query_params["modalidade"] = params.modalidade

        if params.situacao:
            query_params["situacao"] = params.situacao

        if params.cnpj_orgao:
            query_params["cnpj"] = params.cnpj_orgao

        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/compras",
                params=query_params
            )
            response.raise_for_status()
            data = response.json()

            compras = [
                self.parser.parse_compra(c)
                for c in data.get("compras", [])
            ]

            return PNCPResponse(
                sucesso=True,
                total_registros=data.get("totalRegistros", len(compras)),
                pagina_atual=params.pagina,
                total_paginas=data.get("totalPaginas", 1),
                compras=compras
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao buscar compras: {e}")
            return PNCPResponse(
                sucesso=False,
                erro=f"Erro HTTP: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Erro ao buscar compras PNCP: {e}")
            return PNCPResponse(
                sucesso=False,
                erro=str(e)
            )

    async def get_compra(
        self,
        cnpj_orgao: str,
        ano: int,
        sequencial: int
    ) -> Optional[PNCPCompra]:
        """
        Busca detalhes de uma compra especifica.

        Args:
            cnpj_orgao: CNPJ do orgao (apenas numeros)
            ano: Ano da compra
            sequencial: Sequencial da compra

        Returns:
            PNCPCompra ou None
        """
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}"
            )
            response.raise_for_status()
            data = response.json()

            compra = self.parser.parse_compra(data)

            # Busca itens
            compra.itens = await self.get_itens_compra(cnpj_orgao, ano, sequencial)

            # Busca documentos
            compra.documentos = await self.get_documentos_compra(cnpj_orgao, ano, sequencial)

            return compra

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao buscar compra: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes PNCP: {e}")
            return None

    async def get_itens_compra(
        self,
        cnpj_orgao: str,
        ano: int,
        sequencial: int
    ) -> List:
        """Busca itens de uma compra."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}/itens"
            )
            response.raise_for_status()
            data = response.json()

            return [
                self.parser.parse_item(item)
                for item in data.get("itens", [])
            ]

        except Exception as e:
            logger.error(f"Erro ao buscar itens: {e}")
            return []

    async def get_documentos_compra(
        self,
        cnpj_orgao: str,
        ano: int,
        sequencial: int
    ) -> List:
        """Busca documentos/anexos de uma compra."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}/arquivos"
            )
            response.raise_for_status()
            data = response.json()

            return [
                self.parser.parse_documento(doc)
                for doc in data.get("arquivos", [])
            ]

        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {e}")
            return []

    async def buscar_contratos(
        self,
        uf: str = "AM",
        cnpj_orgao: str = None,
        pagina: int = 1,
        tamanho_pagina: int = 20
    ) -> Dict[str, Any]:
        """Busca contratos no PNCP."""
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho_pagina
        }

        if uf:
            params["uf"] = uf

        if cnpj_orgao:
            params["cnpj"] = cnpj_orgao

        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/contratos",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            return {
                "sucesso": True,
                "total": data.get("totalRegistros", 0),
                "contratos": [
                    self.parser.parse_contrato(c)
                    for c in data.get("contratos", [])
                ]
            }

        except Exception as e:
            logger.error(f"Erro ao buscar contratos: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "contratos": []
            }

    async def get_contrato(
        self,
        cnpj_orgao: str,
        ano: int,
        sequencial: int
    ) -> Optional[PNCPContrato]:
        """Busca detalhes de um contrato especifico."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/contratos/{cnpj_orgao}/{ano}/{sequencial}"
            )
            response.raise_for_status()
            return self.parser.parse_contrato(response.json())

        except Exception as e:
            logger.error(f"Erro ao buscar contrato: {e}")
            return None

    async def buscar_por_objeto(
        self,
        termo: str,
        uf: str = "AM",
        pagina: int = 1
    ) -> PNCPResponse:
        """
        Busca compras por termo no objeto.

        Args:
            termo: Termo de busca
            uf: UF para filtrar
            pagina: Pagina de resultados

        Returns:
            PNCPResponse com resultados
        """
        params = PNCPSearchParams(
            uf=uf,
            objeto=termo,
            pagina=pagina
        )
        return await self.buscar_compras(params)

    async def buscar_por_modalidade(
        self,
        modalidade: str,
        uf: str = "AM",
        data_inicial: date = None,
        data_final: date = None,
        pagina: int = 1
    ) -> PNCPResponse:
        """
        Busca compras por modalidade.

        Args:
            modalidade: Modalidade de licitacao
            uf: UF para filtrar
            data_inicial: Data inicial
            data_final: Data final
            pagina: Pagina

        Returns:
            PNCPResponse com resultados
        """
        params = PNCPSearchParams(
            uf=uf,
            modalidade=modalidade,
            data_inicial=data_inicial,
            data_final=data_final,
            pagina=pagina
        )
        return await self.buscar_compras(params)
