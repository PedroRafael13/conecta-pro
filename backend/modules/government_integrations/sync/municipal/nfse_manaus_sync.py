"""
Sincronizador de NFS-e para Manaus/AM.

Extrai e sincroniza:
- NFS-e emitidas
- NFS-e recebidas (tomadas)
- Eventos de cancelamento
- Substituições
"""

import logging
from collections.abc import AsyncGenerator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class NFSeManausSynchronizer(BaseSynchronizer):
    """Sincronizador de NFS-e do município de Manaus."""

    SERVICO_NOME = "nfse_manaus"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # URL base do webservice de Manaus
    URL_PRODUCAO = "https://nfse-prd.manaus.am.gov.br/nfse/servlet"
    URL_HOMOLOGACAO = "https://nfse-hml.manaus.am.gov.br/nfse/servlet"
    URL_LOGIN = "https://nfse-prd.manaus.am.gov.br/nfse/servlet/hlogin"

    # Códigos de serviço mais comuns (LC 116/2003)
    SERVICOS_COMUNS = [
        "01.01",  # Análise e desenvolvimento de sistemas
        "01.02",  # Programação
        "01.03",  # Processamento de dados
        "01.04",  # Elaboração de programas
        "07.02",  # Execução de construção civil
        "17.01",  # Assessoria ou consultoria
        "17.02",  # Datilografia, digitação
    ]

    def __init__(self, db_session, certificate_manager=None, nfse_transmitter=None):
        super().__init__(db_session, certificate_manager)
        self.nfse_transmitter = nfse_transmitter
        self.ambiente = "producao"

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai NFS-e do webservice de Manaus.

        Args:
            config: Configuração da sincronização

        Yields:
            Dict com dados de cada NFS-e
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)
        inscricao_municipal = config.parametros_extras.get("inscricao_municipal")

        logger.info(
            f"[NFS-e Manaus] Extraindo notas - CNPJ: {cnpj}, Período: {config.data_inicial} a {config.data_final}"
        )

        # 1. Consultar NFS-e emitidas
        async for nfse in self._consultar_nfse_emitidas(cnpj, inscricao_municipal, config):
            yield nfse

        # 2. Consultar NFS-e recebidas (tomadas)
        async for nfse in self._consultar_nfse_tomadas(cnpj, config):
            yield nfse

        # 3. Verificar cancelamentos
        async for cancelamento in self._consultar_cancelamentos(cnpj, inscricao_municipal, config):
            yield cancelamento

    async def _consultar_nfse_emitidas(
        self,
        cnpj: str,
        inscricao_municipal: str | None,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta NFS-e emitidas pelo prestador."""
        try:
            if not self.nfse_transmitter:
                logger.warning("[NFS-e Manaus] Transmitter não configurado")
                return

            # Consultar por período
            notas = await self._request_com_retry(
                self.nfse_transmitter.consultar_nfse_prestador,
                cnpj=cnpj,
                inscricao_municipal=inscricao_municipal,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas:
                yield await self._processar_nfse(nota, "emitida")

        except Exception as e:
            logger.error(f"[NFS-e Manaus] Erro consultando notas emitidas: {e}")
            raise

    async def _consultar_nfse_tomadas(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta NFS-e tomadas (recebidas como tomador)."""
        try:
            if not self.nfse_transmitter:
                return

            notas = await self._request_com_retry(
                self.nfse_transmitter.consultar_nfse_tomador,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas:
                yield await self._processar_nfse(nota, "tomada")

        except Exception as e:
            logger.error(f"[NFS-e Manaus] Erro consultando notas tomadas: {e}")

    async def _consultar_cancelamentos(
        self,
        cnpj: str,
        inscricao_municipal: str | None,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Verifica cancelamentos de NFS-e."""
        try:
            if not self.nfse_transmitter:
                return

            # Buscar NFS-e ativas no banco para verificar cancelamento
            notas_ativas = await self._buscar_nfse_ativas(cnpj)

            for nota in notas_ativas:
                numero = nota.get("numero")
                if not numero:
                    continue

                # Consultar situação atual
                situacao = await self._request_com_retry(
                    self.nfse_transmitter.consultar_situacao_nfse,
                    cnpj=cnpj,
                    inscricao_municipal=inscricao_municipal,
                    numero_nfse=numero,
                )

                if situacao.get("cancelada"):
                    yield {
                        "tipo": "cancelamento",
                        "numero_nfse": numero,
                        "data_cancelamento": self._parse_data(situacao.get("data_cancelamento")),
                        "motivo": situacao.get("motivo_cancelamento"),
                        "protocolo": situacao.get("protocolo_cancelamento"),
                    }

        except Exception as e:
            logger.error(f"[NFS-e Manaus] Erro verificando cancelamentos: {e}")

    async def _buscar_nfse_ativas(self, cnpj: str) -> list[dict]:
        """Busca NFS-e ativas no banco local."""
        # Implementação depende do modelo real
        return []

    async def _processar_nfse(
        self,
        nota: dict[str, Any],
        direcao: str,
    ) -> dict[str, Any]:
        """Processa dados de uma NFS-e."""
        # Extrair dados do XML se presente
        xml_content = nota.get("xml")
        dados_xml = {}

        if xml_content:
            dados_xml = self._parse_xml_nfse(xml_content)

        return {
            "tipo": "nfse",
            "direcao": direcao,  # emitida ou tomada
            "numero": nota.get("numero") or dados_xml.get("numero"),
            "codigo_verificacao": nota.get("codigo_verificacao") or dados_xml.get("codigo_verificacao"),
            "data_emissao": self._parse_data(nota.get("data_emissao")) or dados_xml.get("data_emissao"),
            "competencia": nota.get("competencia") or dados_xml.get("competencia"),
            # Prestador
            "cnpj_prestador": nota.get("cnpj_prestador") or dados_xml.get("cnpj_prestador"),
            "inscricao_prestador": nota.get("inscricao_prestador") or dados_xml.get("inscricao_prestador"),
            "razao_social_prestador": nota.get("razao_social_prestador") or dados_xml.get("razao_social_prestador"),
            # Tomador
            "cnpj_tomador": nota.get("cnpj_tomador") or dados_xml.get("cnpj_tomador"),
            "cpf_tomador": nota.get("cpf_tomador") or dados_xml.get("cpf_tomador"),
            "razao_social_tomador": nota.get("razao_social_tomador") or dados_xml.get("razao_social_tomador"),
            "email_tomador": nota.get("email_tomador") or dados_xml.get("email_tomador"),
            # Serviço
            "discriminacao": nota.get("discriminacao") or dados_xml.get("discriminacao"),
            "codigo_servico": nota.get("codigo_servico") or dados_xml.get("codigo_servico"),
            "codigo_cnae": nota.get("codigo_cnae") or dados_xml.get("codigo_cnae"),
            "codigo_tributacao_municipio": nota.get("codigo_tributacao_municipio"),
            # Valores
            "valor_servicos": self._parse_decimal(nota.get("valor_servicos") or dados_xml.get("valor_servicos")),
            "valor_deducoes": self._parse_decimal(nota.get("valor_deducoes") or dados_xml.get("valor_deducoes")),
            "valor_pis": self._parse_decimal(nota.get("valor_pis") or dados_xml.get("valor_pis")),
            "valor_cofins": self._parse_decimal(nota.get("valor_cofins") or dados_xml.get("valor_cofins")),
            "valor_inss": self._parse_decimal(nota.get("valor_inss") or dados_xml.get("valor_inss")),
            "valor_ir": self._parse_decimal(nota.get("valor_ir") or dados_xml.get("valor_ir")),
            "valor_csll": self._parse_decimal(nota.get("valor_csll") or dados_xml.get("valor_csll")),
            "valor_iss": self._parse_decimal(nota.get("valor_iss") or dados_xml.get("valor_iss")),
            "valor_iss_retido": self._parse_decimal(nota.get("valor_iss_retido") or dados_xml.get("valor_iss_retido")),
            "aliquota_iss": self._parse_decimal(nota.get("aliquota_iss") or dados_xml.get("aliquota_iss")),
            "base_calculo": self._parse_decimal(nota.get("base_calculo") or dados_xml.get("base_calculo")),
            "valor_liquido": self._parse_decimal(nota.get("valor_liquido") or dados_xml.get("valor_liquido")),
            "valor_total": self._parse_decimal(nota.get("valor_total") or dados_xml.get("valor_total")),
            # Impostos retidos
            "iss_retido": nota.get("iss_retido", False) or dados_xml.get("iss_retido", False),
            # Status
            "status": nota.get("status", "normal"),
            "situacao": nota.get("situacao"),
            # XML
            "xml_completo": xml_content,
        }

    def _parse_xml_nfse(self, xml_content: str) -> dict[str, Any]:
        """Parse XML de NFS-e padrão Manaus/ABRASF."""
        dados = {}

        try:
            # Remover namespaces para facilitar parsing
            xml_clean = xml_content
            for ns in ['xmlns="', "xmlns='", "xmlns:"]:
                while ns in xml_clean:
                    start = xml_clean.find(ns)
                    if start == -1:
                        break
                    end = xml_clean.find('"', start + len(ns))
                    if end == -1:
                        end = xml_clean.find("'", start + len(ns))
                    if end != -1:
                        xml_clean = xml_clean[:start] + xml_clean[end + 1 :]

            root = ET.fromstring(xml_clean)

            # Dados da NFS-e
            def find_text(element, *tags):
                for tag in tags:
                    el = element.find(f".//{tag}")
                    if el is not None and el.text:
                        return el.text.strip()
                return None

            # Identificação
            dados["numero"] = find_text(root, "Numero", "NumeroNfse", "NumeroNota")
            dados["codigo_verificacao"] = find_text(root, "CodigoVerificacao", "CodVerificacao")
            dados["data_emissao"] = self._parse_data(find_text(root, "DataEmissao", "DataEmissaoNfse"))
            dados["competencia"] = find_text(root, "Competencia")

            # Prestador
            prestador = root.find(".//Prestador") or root.find(".//IdentificacaoPrestador")
            if prestador is not None:
                dados["cnpj_prestador"] = find_text(prestador, "Cnpj", "CpfCnpj/Cnpj")
                dados["inscricao_prestador"] = find_text(prestador, "InscricaoMunicipal")
                dados["razao_social_prestador"] = find_text(root, "RazaoSocialPrestador", "RazaoSocial")

            # Tomador
            tomador = root.find(".//Tomador") or root.find(".//DadosTomador")
            if tomador is not None:
                dados["cnpj_tomador"] = find_text(tomador, "Cnpj", "CpfCnpj/Cnpj")
                dados["cpf_tomador"] = find_text(tomador, "Cpf", "CpfCnpj/Cpf")
                dados["razao_social_tomador"] = find_text(tomador, "RazaoSocial")
                dados["email_tomador"] = find_text(tomador, "Email")

            # Serviço
            servico = root.find(".//Servico") or root.find(".//DadosServico")
            if servico is not None:
                dados["discriminacao"] = find_text(servico, "Discriminacao")
                dados["codigo_servico"] = find_text(servico, "ItemListaServico", "CodigoServico")
                dados["codigo_cnae"] = find_text(servico, "CodigoCnae")

            # Valores
            valores = root.find(".//Valores") or servico
            if valores is not None:
                dados["valor_servicos"] = self._parse_decimal(find_text(valores, "ValorServicos"))
                dados["valor_deducoes"] = self._parse_decimal(find_text(valores, "ValorDeducoes"))
                dados["valor_pis"] = self._parse_decimal(find_text(valores, "ValorPis"))
                dados["valor_cofins"] = self._parse_decimal(find_text(valores, "ValorCofins"))
                dados["valor_inss"] = self._parse_decimal(find_text(valores, "ValorInss"))
                dados["valor_ir"] = self._parse_decimal(find_text(valores, "ValorIr"))
                dados["valor_csll"] = self._parse_decimal(find_text(valores, "ValorCsll"))
                dados["valor_iss"] = self._parse_decimal(find_text(valores, "ValorIss"))
                dados["valor_iss_retido"] = self._parse_decimal(find_text(valores, "ValorIssRetido"))
                dados["aliquota_iss"] = self._parse_decimal(find_text(valores, "Aliquota"))
                dados["base_calculo"] = self._parse_decimal(find_text(valores, "BaseCalculo"))
                dados["valor_liquido"] = self._parse_decimal(find_text(valores, "ValorLiquidoNfse"))

                iss_retido = find_text(valores, "IssRetido")
                dados["iss_retido"] = iss_retido in ("1", "true", "True", "S", "Sim")

            # Calcular valor total se não presente
            if not dados.get("valor_total") and dados.get("valor_servicos"):
                dados["valor_total"] = dados["valor_servicos"]

        except ET.ParseError as e:
            logger.warning(f"[NFS-e Manaus] Erro parseando XML: {e}")
        except Exception as e:
            logger.warning(f"[NFS-e Manaus] Erro extraindo dados XML: {e}")

        return dados

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """
        Processa registro extraído.

        Args:
            registro: Dados do registro
            config: Configuração

        Returns:
            True se registro novo, False se atualizado
        """
        tipo = registro.get("tipo")

        if tipo == "nfse":
            return await self._salvar_nfse(registro, config)
        elif tipo == "cancelamento":
            return await self._processar_cancelamento(registro, config)

        return False

    async def _salvar_nfse(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza NFS-e no banco."""
        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal, TipoDocumentoFiscal

        numero = registro.get("numero")
        codigo_verificacao = registro.get("codigo_verificacao")

        # Chave única: CNPJ + número + código verificação
        chave = f"{config.cnpj_empresa}_{numero}_{codigo_verificacao}"

        # Verificar se existe
        existente = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        # Determinar CNPJ da empresa baseado na direção
        if registro.get("direcao") == "emitida":
            cnpj_empresa = registro.get("cnpj_prestador")
            cnpj_emitente = registro.get("cnpj_prestador")
            nome_emitente = registro.get("razao_social_prestador")
            cnpj_destinatario = registro.get("cnpj_tomador") or registro.get("cpf_tomador")
            nome_destinatario = registro.get("razao_social_tomador")
        else:
            cnpj_empresa = registro.get("cnpj_tomador") or config.cnpj_empresa
            cnpj_emitente = registro.get("cnpj_prestador")
            nome_emitente = registro.get("razao_social_prestador")
            cnpj_destinatario = registro.get("cnpj_tomador") or registro.get("cpf_tomador")
            nome_destinatario = registro.get("razao_social_tomador")

        if existente:
            # Atualizar
            existente.status = StatusDocumentoFiscal.AUTORIZADA
            existente.valor_total = registro.get("valor_total")
            existente.updated_at = datetime.utcnow()
            return False
        else:
            # Criar novo
            novo = DocumentoFiscal(
                cnpj_empresa=cnpj_empresa or config.cnpj_empresa,
                tipo_documento=TipoDocumentoFiscal.NFSE,
                chave_acesso=chave,
                numero=numero,
                serie="U",  # NFS-e não tem série
                data_emissao=registro.get("data_emissao") or date.today(),
                cnpj_emitente=cnpj_emitente,
                nome_emitente=nome_emitente,
                cnpj_destinatario=cnpj_destinatario,
                nome_destinatario=nome_destinatario,
                valor_total=registro.get("valor_total") or Decimal("0"),
                valor_produtos=registro.get("valor_servicos") or Decimal("0"),
                valor_servicos=registro.get("valor_servicos"),
                valor_iss=registro.get("valor_iss"),
                codigo_servico=registro.get("codigo_servico"),
                status=StatusDocumentoFiscal.AUTORIZADA,
                direcao=registro.get("direcao"),
                xml_documento=registro.get("xml_completo"),
                dados_adicionais={
                    "codigo_verificacao": codigo_verificacao,
                    "discriminacao": registro.get("discriminacao"),
                    "codigo_cnae": registro.get("codigo_cnae"),
                    "aliquota_iss": registro.get("aliquota_iss"),
                    "iss_retido": registro.get("iss_retido"),
                    "email_tomador": registro.get("email_tomador"),
                },
                sync_id=self._current_sync_id,
            )
            self.db.add(novo)
            return True

    async def _processar_cancelamento(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa cancelamento de NFS-e."""
        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal

        numero = registro.get("numero_nfse")

        # Buscar NFS-e
        nfse = (
            self.db.query(DocumentoFiscal)
            .filter(
                DocumentoFiscal.cnpj_empresa == config.cnpj_empresa,
                DocumentoFiscal.numero == numero,
                DocumentoFiscal.tipo_documento == "nfse",
            )
            .first()
        )

        if nfse:
            nfse.status = StatusDocumentoFiscal.CANCELADA
            nfse.data_cancelamento = registro.get("data_cancelamento")
            nfse.dados_adicionais = {
                **(nfse.dados_adicionais or {}),
                "motivo_cancelamento": registro.get("motivo"),
                "protocolo_cancelamento": registro.get("protocolo"),
            }
            nfse.updated_at = datetime.utcnow()
            return False

        return False

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtém última sincronização de NFS-e Manaus."""
        from ..models.sync_models import StatusSincronizacao, SyncLog

        ultimo = (
            self.db.query(SyncLog)
            .filter(
                SyncLog.cnpj_empresa == cnpj,
                SyncLog.servico == self.SERVICO_NOME,
                SyncLog.status == StatusSincronizacao.SUCESSO,
            )
            .order_by(SyncLog.fim_execucao.desc())
            .first()
        )

        return ultimo.fim_execucao if ultimo else None

    # =========================================================================
    # MÉTODOS ADICIONAIS
    # =========================================================================

    async def consultar_por_numero(
        self,
        cnpj: str,
        inscricao_municipal: str,
        numero: str,
    ) -> dict[str, Any] | None:
        """
        Consulta NFS-e específica por número.

        Args:
            cnpj: CNPJ do prestador
            inscricao_municipal: Inscrição municipal
            numero: Número da NFS-e

        Returns:
            Dados da NFS-e ou None
        """
        try:
            if not self.nfse_transmitter:
                return None

            resultado = await self._request_com_retry(
                self.nfse_transmitter.consultar_nfse_numero,
                cnpj=cnpj,
                inscricao_municipal=inscricao_municipal,
                numero=numero,
            )

            if resultado:
                return await self._processar_nfse(resultado, "emitida")

            return None

        except Exception as e:
            logger.error(f"[NFS-e Manaus] Erro consultando NFS-e {numero}: {e}")
            return None

    async def cancelar_nfse(
        self,
        cnpj: str,
        inscricao_municipal: str,
        numero: str,
        codigo_verificacao: str,
        motivo: str,
    ) -> dict[str, Any]:
        """
        Solicita cancelamento de NFS-e.

        Args:
            cnpj: CNPJ do prestador
            inscricao_municipal: Inscrição municipal
            numero: Número da NFS-e
            codigo_verificacao: Código de verificação
            motivo: Motivo do cancelamento

        Returns:
            Resultado do cancelamento
        """
        try:
            if not self.nfse_transmitter:
                raise ValueError("Transmitter não configurado")

            resultado = await self._request_com_retry(
                self.nfse_transmitter.cancelar_nfse,
                cnpj=cnpj,
                inscricao_municipal=inscricao_municipal,
                numero=numero,
                codigo_verificacao=codigo_verificacao,
                motivo=motivo,
            )

            return resultado

        except Exception as e:
            logger.error(f"[NFS-e Manaus] Erro cancelando NFS-e {numero}: {e}")
            raise

    async def obter_resumo(self, cnpj: str) -> dict[str, Any]:
        """
        Obtém resumo das NFS-e sincronizadas.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dict com resumo
        """
        from sqlalchemy import func

        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal, TipoDocumentoFiscal

        # Contar por status
        por_status = (
            self.db.query(DocumentoFiscal.status, func.count(DocumentoFiscal.id))
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo_documento == TipoDocumentoFiscal.NFSE,
            )
            .group_by(DocumentoFiscal.status)
            .all()
        )

        # Contar por direção
        por_direcao = (
            self.db.query(DocumentoFiscal.direcao, func.count(DocumentoFiscal.id))
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo_documento == TipoDocumentoFiscal.NFSE,
            )
            .group_by(DocumentoFiscal.direcao)
            .all()
        )

        # Somar valores
        valores = (
            self.db.query(
                func.sum(DocumentoFiscal.valor_total),
                func.sum(DocumentoFiscal.valor_iss),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo_documento == TipoDocumentoFiscal.NFSE,
                DocumentoFiscal.status == StatusDocumentoFiscal.AUTORIZADA,
            )
            .first()
        )

        return {
            "total_nfse": sum(c for _, c in por_status),
            "por_status": {str(s.value): c for s, c in por_status},
            "por_direcao": {str(d): c for d, c in por_direcao if d},
            "valor_total_servicos": float(valores[0]) if valores[0] else 0,
            "valor_total_iss": float(valores[1]) if valores[1] else 0,
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
