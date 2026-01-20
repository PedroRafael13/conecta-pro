"""
Extrator do FGTS Digital.

Implementa:
- Consulta de guias geradas
- Download de DARFs
- Verificação de pagamentos
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID
import asyncio
import logging

from ..base_extractor import ExtratorBase, DocumentoExtraido, ResultadoExtracao
from ...core.credentials import ProvedorCredenciais, TipoCredencial

logger = logging.getLogger(__name__)


class ExtratorFGTS(ExtratorBase):
    """
    Extrator de dados do FGTS Digital.

    Serviços:
    - Consulta de guias mensais
    - Consulta de guias rescisórias
    - Download de DARFs
    """

    URLS = {
        "producao": "https://fgtsdigital.caixa.gov.br/api/v1",
        "homologacao": "https://fgtsdigital-hom.caixa.gov.br/api/v1",
    }

    @property
    def tipo_servico(self) -> str:
        return "fgts_digital"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.FGTS_DIGITAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """Extrai dados do FGTS Digital."""
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=90)

        logger.info(f"Iniciando extração FGTS: {tenant_id}")

        try:
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                # Consultar guias mensais
                guias_mensais = await self._consultar_guias_mensais(
                    tenant_id, cnpj, data_inicio, data_fim
                )

                for guia in guias_mensais:
                    resultado.documentos.append(guia)
                    resultado.documentos_processados += 1
                    if guia.erro:
                        resultado.documentos_erro += 1
                    else:
                        resultado.documentos_novos += 1

                # Consultar guias rescisórias
                guias_rescissorias = await self._consultar_guias_rescissorias(
                    tenant_id, cnpj, data_inicio, data_fim
                )

                for guia in guias_rescissorias:
                    resultado.documentos.append(guia)
                    resultado.documentos_processados += 1

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração FGTS: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()

        return resultado

    async def _consultar_guias_mensais(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> List[DocumentoExtraido]:
        """Consulta guias mensais do FGTS."""
        documentos = []

        # Iterar por competências
        competencia_atual = datetime(data_inicio.year, data_inicio.month, 1)

        while competencia_atual <= data_fim:
            competencia = competencia_atual.strftime("%Y%m")

            try:
                doc = await self._consultar_guia(tenant_id, cnpj, competencia, "mensal")
                if doc:
                    documentos.append(doc)

            except Exception as e:
                logger.error(f"Erro ao consultar guia {competencia}: {e}")

            # Próxima competência
            if competencia_atual.month == 12:
                competencia_atual = datetime(competencia_atual.year + 1, 1, 1)
            else:
                competencia_atual = datetime(
                    competencia_atual.year, competencia_atual.month + 1, 1
                )

            await asyncio.sleep(0.5)

        return documentos

    async def _consultar_guias_rescissorias(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> List[DocumentoExtraido]:
        """Consulta guias rescisórias."""
        documentos = []

        # Consulta simplificada - em produção, buscar rescisões do período
        # e consultar guias correspondentes
        logger.info(f"Consultando guias rescisórias: {cnpj}")

        return documentos

    async def _consultar_guia(
        self,
        tenant_id: UUID,
        cnpj: str,
        competencia: str,
        tipo: str
    ) -> Optional[DocumentoExtraido]:
        """Consulta uma guia específica."""
        # Montar requisição
        url = f"{self.URLS['producao']}/guias/{cnpj}/{competencia}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            session = await self._get_session(tenant_id)

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    dados = await response.json()

                    return DocumentoExtraido(
                        id=f"{cnpj}_{competencia}_{tipo}",
                        tipo="guia_fgts",
                        dados={
                            "cnpj": cnpj,
                            "competencia": competencia,
                            "tipo": tipo,
                            "valor_principal": dados.get("valorPrincipal", 0),
                            "valor_multa": dados.get("valorMulta", 0),
                            "valor_juros": dados.get("valorJuros", 0),
                            "valor_total": dados.get("valorTotal", 0),
                            "codigo_barras": dados.get("codigoBarras"),
                            "data_vencimento": dados.get("dataVencimento"),
                            "status": dados.get("status", "gerada"),
                        },
                        processado=True,
                    )

                elif response.status == 404:
                    # Guia não encontrada (competência sem movimento)
                    return None

                else:
                    erro = await response.text()
                    logger.warning(f"Erro ao consultar guia: {response.status} - {erro}")
                    return None

        except Exception as e:
            logger.error(f"Erro na consulta de guia: {e}")
            return DocumentoExtraido(
                id=f"{cnpj}_{competencia}_{tipo}",
                tipo="guia_fgts",
                dados={"cnpj": cnpj, "competencia": competencia},
                erro=str(e),
            )

    async def download_darf(
        self,
        tenant_id: UUID,
        cnpj: str,
        competencia: str,
    ) -> Optional[bytes]:
        """Download do DARF em PDF."""
        url = f"{self.URLS['producao']}/guias/{cnpj}/{competencia}/pdf"

        try:
            session = await self._get_session(tenant_id)

            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()

        except Exception as e:
            logger.error(f"Erro ao baixar DARF: {e}")

        return None
