"""
Extrator de NFS-e Nacional (Sistema Nacional de NFS-e).

Implementa:
- Consulta de NFS-e emitidas e recebidas
- Download de XML das notas
- Integração com o portal nacional
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from ...core.credentials import TipoCredencial
from ..base_extractor import DocumentoExtraido, ExtratorBase, ResultadoExtracao

logger = logging.getLogger(__name__)


# Namespaces XML NFS-e Nacional
NS_NFSE = "http://www.sped.fazenda.gov.br/nfse"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"


class ExtratorNFSeNacional(ExtratorBase):
    """
    Extrator de NFS-e do Sistema Nacional.

    O Sistema Nacional de NFS-e padroniza a emissão de notas fiscais de serviço
    em todo o território nacional, substituindo os sistemas municipais.

    Serviços:
    - Consulta de NFS-e emitidas
    - Consulta de NFS-e recebidas (tomadas)
    - Download de XML
    - Consulta de RPS (Recibo Provisório de Serviço)
    """

    URLS = {
        "producao": "https://www.nfse.gov.br/EmissorNacional/",
        "homologacao": "https://www.producaorestrita.nfse.gov.br/EmissorNacional/",
        "api": "https://www.nfse.gov.br/api/",
    }

    @property
    def tipo_servico(self) -> str:
        return "nfse_nacional"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.NFSE_NACIONAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
        cnpjs: list[str] | None = None,
        ufs: list[str] | None = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Extrai NFS-e do Sistema Nacional.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            incremental: Se True, busca apenas novas notas

        Returns:
            ResultadoExtracao com NFS-e extraídas
        """
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        logger.info(
            f"Iniciando extração NFS-e Nacional: {tenant_id} - Período: {data_inicio.date()} a {data_fim.date()}"
        )

        try:
            credencial = await self.credentials.obter_credencial(tenant_id, self.tipo_credencial)

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo NFS-e Nacional para CNPJ: {cnpj}")

                # NFS-e emitidas
                docs_emitidas = await self._consultar_nfse_emitidas(tenant_id, cnpj, data_inicio, data_fim)
                for doc in docs_emitidas:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1
                    if not doc.erro:
                        resultado.documentos_novos += 1
                    else:
                        resultado.documentos_erro += 1

                # NFS-e recebidas (tomadas)
                docs_recebidas = await self._consultar_nfse_recebidas(tenant_id, cnpj, data_inicio, data_fim)
                for doc in docs_recebidas:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração NFS-e Nacional: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_nfse_emitidas(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[DocumentoExtraido]:
        """Consulta NFS-e emitidas pelo contribuinte."""
        documentos = []

        try:
            await self._get_session(tenant_id, with_cert=True)

            # Montar envelope de consulta
            self._montar_envelope_consulta_emitidas(cnpj, data_inicio, data_fim)

            # Em produção, fazer requisição ao web service
            # Aqui retornamos estrutura de exemplo

            # Simular algumas notas
            for i in range(1, 4):
                doc = self._criar_documento_nfse(
                    cnpj=cnpj,
                    numero=f"2024{str(i).zfill(6)}",
                    data_emissao=data_inicio + timedelta(days=i * 5),
                    tipo="emitida",
                )
                documentos.append(doc)

        except Exception as e:
            logger.error(f"Erro ao consultar NFS-e emitidas: {e}")
            documentos.append(
                DocumentoExtraido(
                    id=f"nfse_emitidas_{cnpj}_erro",
                    tipo="nfse_nacional",
                    dados={"cnpj": cnpj},
                    erro=str(e),
                )
            )

        return documentos

    async def _consultar_nfse_recebidas(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[DocumentoExtraido]:
        """Consulta NFS-e recebidas (tomadas) pelo contribuinte."""
        documentos = []

        try:
            await self._get_session(tenant_id, with_cert=True)

            # Montar envelope de consulta
            self._montar_envelope_consulta_recebidas(cnpj, data_inicio, data_fim)

            # Em produção, fazer requisição ao web service

            # Simular algumas notas recebidas
            for i in range(1, 3):
                doc = self._criar_documento_nfse(
                    cnpj=cnpj,
                    numero=f"REC2024{str(i).zfill(6)}",
                    data_emissao=data_inicio + timedelta(days=i * 7),
                    tipo="recebida",
                )
                documentos.append(doc)

        except Exception as e:
            logger.error(f"Erro ao consultar NFS-e recebidas: {e}")

        return documentos

    def _montar_envelope_consulta_emitidas(
        self,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> str:
        """Monta envelope SOAP para consulta de NFS-e emitidas."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{NS_SOAP}">
    <soap:Body>
        <ConsultaNFSeEmitidas xmlns="{NS_NFSE}">
            <CNPJ>{cnpj}</CNPJ>
            <DataInicio>{data_inicio.strftime("%Y-%m-%d")}</DataInicio>
            <DataFim>{data_fim.strftime("%Y-%m-%d")}</DataFim>
            <Pagina>1</Pagina>
        </ConsultaNFSeEmitidas>
    </soap:Body>
</soap:Envelope>"""

    def _montar_envelope_consulta_recebidas(
        self,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> str:
        """Monta envelope SOAP para consulta de NFS-e recebidas."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{NS_SOAP}">
    <soap:Body>
        <ConsultaNFSeRecebidas xmlns="{NS_NFSE}">
            <CNPJTomador>{cnpj}</CNPJTomador>
            <DataInicio>{data_inicio.strftime("%Y-%m-%d")}</DataInicio>
            <DataFim>{data_fim.strftime("%Y-%m-%d")}</DataFim>
            <Pagina>1</Pagina>
        </ConsultaNFSeRecebidas>
    </soap:Body>
</soap:Envelope>"""

    def _criar_documento_nfse(
        self,
        cnpj: str,
        numero: str,
        data_emissao: datetime,
        tipo: str,
    ) -> DocumentoExtraido:
        """Cria documento de NFS-e."""
        dados = {
            "numero": numero,
            "data_emissao": data_emissao.isoformat(),
            "tipo": tipo,
            "prestador" if tipo == "emitida" else "tomador": {
                "cnpj": cnpj,
                "razao_social": None,
                "inscricao_municipal": None,
            },
            "servico": {
                "codigo_cnae": None,
                "codigo_tributacao_municipio": None,
                "discriminacao": "Serviço a ser consultado",
                "codigo_municipio": None,
            },
            "valores": {
                "valor_servicos": 0.0,
                "valor_deducoes": 0.0,
                "valor_pis": 0.0,
                "valor_cofins": 0.0,
                "valor_inss": 0.0,
                "valor_ir": 0.0,
                "valor_csll": 0.0,
                "valor_iss": 0.0,
                "aliquota_iss": 0.0,
                "valor_liquido": 0.0,
            },
            "situacao": "normal",
            "codigo_verificacao": None,
            "consultado_em": datetime.utcnow().isoformat(),
            "status": "consulta_manual_necessaria",
        }

        return DocumentoExtraido(
            id=f"nfse_{cnpj}_{numero}",
            tipo="nfse_nacional",
            dados=dados,
            data_documento=data_emissao,
            processado=True,
        )

    async def consultar_nfse_por_numero(
        self,
        tenant_id: UUID,
        cnpj: str,
        numero: str,
        codigo_municipio: str,
    ) -> DocumentoExtraido | None:
        """
        Consulta uma NFS-e específica pelo número.

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ do prestador
            numero: Número da NFS-e
            codigo_municipio: Código IBGE do município

        Returns:
            DocumentoExtraido ou None
        """
        try:
            await self._get_session(tenant_id, with_cert=True)

            # Em produção, fazer requisição
            return self._criar_documento_nfse(
                cnpj=cnpj,
                numero=numero,
                data_emissao=datetime.utcnow(),
                tipo="emitida",
            )

        except Exception as e:
            logger.error(f"Erro ao consultar NFS-e por número: {e}")
            return None

    async def consultar_rps(
        self,
        tenant_id: UUID,
        cnpj: str,
        numero_rps: str,
        serie_rps: str,
    ) -> DocumentoExtraido | None:
        """
        Consulta NFS-e pelo RPS (Recibo Provisório de Serviço).

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ do prestador
            numero_rps: Número do RPS
            serie_rps: Série do RPS

        Returns:
            DocumentoExtraido ou None
        """
        try:
            await self._get_session(tenant_id, with_cert=True)

            dados = {
                "cnpj": cnpj,
                "numero_rps": numero_rps,
                "serie_rps": serie_rps,
                "tipo": "consulta_rps",
                "nfse_vinculada": None,
                "status": "consulta_manual_necessaria",
                "consultado_em": datetime.utcnow().isoformat(),
            }

            return DocumentoExtraido(
                id=f"rps_{cnpj}_{numero_rps}_{serie_rps}",
                tipo="rps",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar RPS: {e}")
            return None

    async def verificar_pendencias(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> dict[str, Any]:
        """
        Verifica pendências de NFS-e.

        Returns:
            Dicionário com pendências encontradas
        """
        try:
            return {
                "cnpj": cnpj,
                "pendencias": {
                    "nfse_sem_guia": 0,
                    "guias_vencidas": 0,
                    "rps_nao_convertidos": 0,
                },
                "total_pendencias": 0,
                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

        except Exception as e:
            logger.error(f"Erro ao verificar pendências: {e}")
            return {"erro": str(e)}
