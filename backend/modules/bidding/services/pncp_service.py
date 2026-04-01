"""
Service de Integracao PNCP - Licitacoes
=======================================
Portal Nacional de Contratacoes Publicas
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy.orm import Session

from modules.bidding.models.tender import BiddingModality, TenderStatus
from modules.bidding.repositories.tender_repository import TenderRepository
from modules.bidding.schemas.tender import TenderCreate

logger = logging.getLogger(__name__)


class PNCPService:
    """Service para integracao com o Portal Nacional de Contratacoes Publicas."""

    BASE_URL = "https://pncp.gov.br/api/pncp"
    TIMEOUT = 30.0

    # Mapeamento de modalidades PNCP para interno
    MODALIDADE_MAP = {
        "pregaoEletronico": BiddingModality.PREGAO_ELETRONICO.value,
        "pregaoPresencial": BiddingModality.PREGAO_PRESENCIAL.value,
        "concorrencia": BiddingModality.CONCORRENCIA.value,
        "tomadaPrecos": BiddingModality.TOMADA_PRECOS.value,
        "convite": BiddingModality.CONVITE.value,
        "dispensa": BiddingModality.DISPENSA.value,
        "inexigibilidade": BiddingModality.INEXIGIBILIDADE.value,
        "dialogoCompetitivo": BiddingModality.DIALOGO_COMPETITIVO.value,
        "leilao": BiddingModality.LEILAO.value,
        "concurso": BiddingModality.CONCURSO.value,
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = TenderRepository(db)
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT)

    async def close(self):
        """Fecha cliente HTTP."""
        await self.client.aclose()

    async def buscar_compras(
        self,
        uf: str = "AM",
        data_inicio: date = None,
        data_fim: date = None,
        modalidade: str = None,
        pagina: int = 1,
        tam_pagina: int = 20,
    ) -> dict[str, Any]:
        """
        Busca compras no PNCP.

        Args:
            uf: UF para filtrar (default: AM)
            data_inicio: Data inicial de publicacao
            data_fim: Data final de publicacao
            modalidade: Modalidade de licitacao
            pagina: Numero da pagina
            tam_pagina: Tamanho da pagina

        Returns:
            Dict com resultados e metadados
        """
        params = {"uf": uf, "pagina": pagina, "tamanhoPagina": tam_pagina}

        if data_inicio:
            params["dataInicial"] = data_inicio.strftime("%Y-%m-%d")

        if data_fim:
            params["dataFinal"] = data_fim.strftime("%Y-%m-%d")

        if modalidade:
            params["modalidade"] = modalidade

        try:
            response = await self.client.get(f"{self.BASE_URL}/v1/compras", params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "sucesso": True,
                "total": data.get("totalRegistros", 0),
                "pagina": pagina,
                "tamanho_pagina": tam_pagina,
                "compras": data.get("compras", []),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao buscar compras: {e}")
            return {"sucesso": False, "erro": f"Erro HTTP: {e.response.status_code}", "compras": []}
        except Exception as e:
            logger.error(f"Erro ao buscar compras PNCP: {e}")
            return {"sucesso": False, "erro": str(e), "compras": []}

    async def buscar_detalhes_compra(self, cnpj_orgao: str, ano: int, sequencial: int) -> dict[str, Any] | None:
        """
        Busca detalhes de uma compra especifica.

        Args:
            cnpj_orgao: CNPJ do orgao
            ano: Ano da compra
            sequencial: Sequencial da compra

        Returns:
            Dict com detalhes da compra ou None
        """
        try:
            response = await self.client.get(f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro ao buscar detalhes da compra: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes PNCP: {e}")
            return None

    async def buscar_itens_compra(self, cnpj_orgao: str, ano: int, sequencial: int) -> list[dict[str, Any]]:
        """Busca itens de uma compra."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}/itens")
            response.raise_for_status()
            return response.json().get("itens", [])

        except Exception as e:
            logger.error(f"Erro ao buscar itens PNCP: {e}")
            return []

    async def buscar_documentos_compra(self, cnpj_orgao: str, ano: int, sequencial: int) -> list[dict[str, Any]]:
        """Busca documentos/anexos de uma compra."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}/arquivos"
            )
            response.raise_for_status()
            return response.json().get("arquivos", [])

        except Exception as e:
            logger.error(f"Erro ao buscar documentos PNCP: {e}")
            return []

    async def sincronizar_editais(self, uf: str = "AM", dias: int = 30, segmentos: list[str] = None) -> dict[str, Any]:
        """
        Sincroniza editais do PNCP para o banco local.

        Args:
            uf: UF para buscar
            dias: Dias retroativos para buscar
            segmentos: Segmentos de interesse (filtro por palavras-chave)

        Returns:
            Estatisticas da sincronizacao
        """
        from datetime import timedelta

        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)

        stats = {"total_encontrados": 0, "novos_importados": 0, "atualizados": 0, "erros": 0, "ignorados": 0}

        # Palavras-chave para segmentos
        palavras_segmentos = {
            "seguranca": ["vigilância", "vigilancia", "segurança", "seguranca", "portaria", "monitoramento"],
            "limpeza": ["limpeza", "conservação", "conservacao", "asseio", "higienização"],
            "facilities": ["facilities", "terceirização", "terceirizacao", "mão de obra", "mao de obra"],
        }

        pagina = 1
        while True:
            resultado = await self.buscar_compras(uf=uf, data_inicio=data_inicio, data_fim=data_fim, pagina=pagina)

            if not resultado["sucesso"] or not resultado["compras"]:
                break

            stats["total_encontrados"] += len(resultado["compras"])

            for compra in resultado["compras"]:
                try:
                    # Verifica se ja existe
                    pncp_id = self._gerar_pncp_id(compra)
                    existing = await self.repository.get_by_pncp_id(pncp_id)

                    # Identifica segmento
                    objeto = compra.get("objetoCompra", "").lower()
                    segmento_identificado = None
                    for seg, palavras in palavras_segmentos.items():
                        if any(p in objeto for p in palavras):
                            segmento_identificado = seg
                            break

                    # Filtra por segmento se especificado
                    if segmentos and segmento_identificado not in segmentos:
                        stats["ignorados"] += 1
                        continue

                    if existing:
                        # Atualiza
                        await self._atualizar_edital(existing, compra)
                        stats["atualizados"] += 1
                    else:
                        # Cria novo
                        await self._criar_edital(compra, segmento_identificado)
                        stats["novos_importados"] += 1

                except Exception as e:
                    logger.error(f"Erro ao processar compra: {e}")
                    stats["erros"] += 1

            # Proxima pagina
            if len(resultado["compras"]) < 20:
                break
            pagina += 1

        logger.info(f"Sincronizacao PNCP concluida: {stats}")
        return stats

    async def _criar_edital(self, compra: dict[str, Any], segmento: str = None):
        """Cria edital a partir de dados do PNCP."""
        orgao = compra.get("orgaoEntidade", {})

        tender_data = TenderCreate(
            numero=str(compra.get("numeroCompra", "")),
            ano=compra.get("anoCompra", date.today().year),
            orgao_cnpj=orgao.get("cnpj", ""),
            orgao_nome=orgao.get("razaoSocial", ""),
            orgao_uf=orgao.get("uf", "AM"),
            orgao_municipio=orgao.get("municipio"),
            modalidade=self._mapear_modalidade(compra.get("modalidadeNome")),
            objeto=compra.get("objetoCompra", ""),
            valor_estimado=Decimal(str(compra.get("valorEstimadoTotal", 0))),
            data_publicacao=self._parse_data(compra.get("dataPublicacaoPncp")),
            data_abertura=self._parse_data(compra.get("dataAberturaProposta")),
            status=TenderStatus.PUBLISHED.value,
            pncp_id=self._gerar_pncp_id(compra),
            pncp_link=compra.get("linkSistemaOrigem"),
            segmento=segmento,
            fonte="pncp",
        )

        await self.repository.create(tender_data)

    async def _atualizar_edital(self, tender, compra: dict[str, Any]):
        """Atualiza edital existente com dados do PNCP."""
        tender.pncp_ultima_sync = datetime.utcnow()

        # Atualiza datas se disponiveis
        if compra.get("dataAberturaProposta"):
            tender.data_abertura = self._parse_data(compra["dataAberturaProposta"])

        if compra.get("valorEstimadoTotal"):
            tender.valor_estimado = Decimal(str(compra["valorEstimadoTotal"]))

        await self.db.commit()

    def _gerar_pncp_id(self, compra: dict[str, Any]) -> str:
        """Gera ID unico para compra do PNCP."""
        orgao = compra.get("orgaoEntidade", {})
        return f"{orgao.get('cnpj', '')}_{compra.get('anoCompra')}_{compra.get('sequencialCompra')}"

    def _mapear_modalidade(self, modalidade_pncp: str) -> str:
        """Mapeia modalidade PNCP para modalidade interna."""
        if not modalidade_pncp:
            return BiddingModality.PREGAO_ELETRONICO.value

        modalidade_lower = modalidade_pncp.lower().replace(" ", "")
        return self.MODALIDADE_MAP.get(modalidade_lower, BiddingModality.PREGAO_ELETRONICO.value)

    def _parse_data(self, data_str: str) -> datetime | None:
        """Parse de data do PNCP."""
        if not data_str:
            return None

        try:
            # Formato ISO
            if "T" in data_str:
                return datetime.fromisoformat(data_str.replace("Z", "+00:00"))
            # Formato simples
            return datetime.strptime(data_str, "%Y-%m-%d")
        except Exception:
            return None

    async def verificar_disponibilidade(self) -> dict[str, Any]:
        """Verifica disponibilidade da API PNCP."""
        try:
            response = await self.client.get(f"{self.BASE_URL}/v1/compras", params={"pagina": 1, "tamanhoPagina": 1})
            return {
                "disponivel": response.status_code == 200,
                "status_code": response.status_code,
                "tempo_resposta_ms": response.elapsed.total_seconds() * 1000,
            }
        except Exception as e:
            return {"disponivel": False, "erro": str(e)}
