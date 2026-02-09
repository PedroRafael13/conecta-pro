"""
Service para EFD-Reinf.

Camada de serviço para operações de EFD-Reinf.
"""

import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..core.certificate_manager import CertificateManager
from ..core.efd_reinf import (
    NATUREZAS_RENDIMENTO,
    ClassificacaoTributaria,
    EFDReinfManager,
    IndRetificacao,
    InfoContribuinte,
    PagamentoBeneficiarioPF,
    PagamentoBeneficiarioPJ,
    RetencaoServico,
    TipoAmbiente,
)

logger = logging.getLogger(__name__)


class EFDReinfService:
    """Service para operações EFD-Reinf."""

    def __init__(self):
        """Inicializa o service."""
        self.cnpj = os.getenv("EFD_REINF_CNPJ", os.getenv("EMPRESA_CNPJ", "35710481000103"))
        self.ambiente_str = os.getenv("EFD_REINF_ENVIRONMENT", "producao_restrita")
        self.cert_path = os.getenv("CERTIFICATE_PATH", "")
        self.cert_password = os.getenv("CERTIFICATE_PASSWORD", "")

        self.ambiente = TipoAmbiente.PRODUCAO if self.ambiente_str == "producao" else TipoAmbiente.PRODUCAO_RESTRITA

        # Certificado é opcional
        self.cert_manager = None
        if self.cert_path and os.path.exists(self.cert_path):
            try:
                self.cert_manager = CertificateManager(certificate_path=self.cert_path, password=self.cert_password)
                logger.info("Certificado digital carregado para EFD-Reinf")
            except Exception as e:
                logger.warning(f"Certificado não carregado: {e}")

        self.manager = EFDReinfManager(
            certificate_manager=self.cert_manager,
            ambiente=self.ambiente,
            cnpj=self.cnpj,
        )

        logger.info(f"EFD-Reinf Service inicializado - Ambiente: {self.ambiente_str}, CNPJ: {self.cnpj}")

    def gerar_r1000(
        self,
        razao_social: str,
        classificacao_tributaria: str,
        inicio_validade: str,
        fim_validade: str | None = None,
        natureza_juridica: str | None = None,
        ind_coop: str = "0",
        ind_constr: str = "0",
        ind_desoneracao: str = "0",
        telefone: str | None = None,
        email: str | None = None,
        retificacao: bool = False,
    ) -> dict[str, Any]:
        """
        Gera evento R-1000 - Informações do Contribuinte.

        Args:
            razao_social: Razão social do contribuinte
            classificacao_tributaria: Código da classificação tributária
            inicio_validade: Início da validade (YYYY-MM)
            fim_validade: Fim da validade (YYYY-MM) - opcional
            natureza_juridica: Código da natureza jurídica
            ind_coop: Indicador de cooperativa (0=Não)
            ind_constr: Indicador de construtora (0=Não)
            ind_desoneracao: Indicador de desoneração (0=Não)
            telefone: Telefone de contato
            email: Email de contato
            retificacao: Se é retificação

        Returns:
            Dict com resultado da geração
        """
        try:
            # Mapeia classificação tributária
            class_trib = ClassificacaoTributaria(classificacao_tributaria)
        except ValueError:
            class_trib = ClassificacaoTributaria.EMPRESA_SIMPLES

        info = InfoContribuinte(
            cnpj=self.cnpj,
            razao_social=razao_social,
            classificacao_tributaria=class_trib,
            inicio_validade=inicio_validade,
            fim_validade=fim_validade,
            natureza_juridica=natureza_juridica,
            ind_coop=ind_coop,
            ind_constr=ind_constr,
            ind_desoneracao=ind_desoneracao,
            telefone=telefone,
            email=email,
        )

        ind_ret = IndRetificacao.RETIFICADOR if retificacao else IndRetificacao.ORIGINAL

        xml = self.manager.gerar_r1000(info, ind_ret)

        logger.info(f"Evento R-1000 gerado para CNPJ {self.cnpj}")

        return {
            "evento": "R-1000",
            "descricao": "Informações do Contribuinte",
            "xml": xml,
            "cnpj": self.cnpj,
            "inicio_validade": inicio_validade,
            "classificacao_tributaria": classificacao_tributaria,
            "ambiente": self.ambiente.value,
            "status": "gerado",
        }

    def gerar_r2010(
        self,
        periodo_apuracao: str,
        retencoes: list[dict[str, Any]],
        retificacao: bool = False,
    ) -> dict[str, Any]:
        """
        Gera evento R-2010 - Retenção Contribuição Previdenciária - Serviços Tomados.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            retencoes: Lista de retenções com dados das NFs
            retificacao: Se é retificação

        Returns:
            Dict com resultado da geração
        """
        lista_retencoes = []
        valor_total_bruto = Decimal("0")
        valor_total_retencao = Decimal("0")

        for ret in retencoes:
            retencao = RetencaoServico(
                cnpj_prestador=ret["cnpj_prestador"],
                valor_bruto=Decimal(str(ret["valor_bruto"])),
                valor_base_retencao=Decimal(str(ret.get("valor_base_retencao", ret["valor_bruto"]))),
                valor_retencao=Decimal(str(ret["valor_retencao"])),
                valor_retencao_adicional=Decimal(str(ret.get("valor_retencao_adicional", "0"))),
                valor_nf_retido=Decimal(str(ret.get("valor_nf_retido", "0"))),
                serie_nf=ret.get("serie_nf", "1"),
                numero_nf=ret.get("numero_nf", ""),
                data_emissao_nf=(
                    datetime.strptime(ret["data_emissao_nf"], "%Y-%m-%d").date() if ret.get("data_emissao_nf") else None
                ),
                codigo_servico=ret.get("codigo_servico", "100000001"),
                ind_cprb=ret.get("ind_cprb", "0"),
            )
            lista_retencoes.append(retencao)
            valor_total_bruto += retencao.valor_bruto
            valor_total_retencao += retencao.valor_retencao

        ind_ret = IndRetificacao.RETIFICADOR if retificacao else IndRetificacao.ORIGINAL

        xml = self.manager.gerar_r2010(periodo_apuracao, lista_retencoes, ind_ret)

        logger.info(f"Evento R-2010 gerado: {len(lista_retencoes)} retenções, período {periodo_apuracao}")

        return {
            "evento": "R-2010",
            "descricao": "Retenção Contribuição Previdenciária - Serviços Tomados",
            "xml": xml,
            "cnpj": self.cnpj,
            "periodo_apuracao": periodo_apuracao,
            "quantidade_retencoes": len(lista_retencoes),
            "valor_total_bruto": str(valor_total_bruto),
            "valor_total_retencao": str(valor_total_retencao),
            "ambiente": self.ambiente.value,
            "status": "gerado",
        }

    def gerar_r4010(
        self,
        periodo_apuracao: str,
        pagamentos: list[dict[str, Any]],
        retificacao: bool = False,
    ) -> dict[str, Any]:
        """
        Gera evento R-4010 - Pagamentos a Beneficiário Pessoa Física.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            pagamentos: Lista de pagamentos a PF
            retificacao: Se é retificação

        Returns:
            Dict com resultado da geração
        """
        lista_pagamentos = []
        valor_total_bruto = Decimal("0")
        valor_total_irrf = Decimal("0")

        for pag in pagamentos:
            pagamento = PagamentoBeneficiarioPF(
                cpf_beneficiario=pag["cpf_beneficiario"].replace(".", "").replace("-", ""),
                nome_beneficiario=pag["nome_beneficiario"],
                natureza_rendimento=pag["natureza_rendimento"],
                valor_bruto=Decimal(str(pag["valor_bruto"])),
                valor_irrf=Decimal(str(pag.get("valor_irrf", "0"))),
                valor_inss=Decimal(str(pag.get("valor_inss", "0"))),
                data_pagamento=(
                    datetime.strptime(pag["data_pagamento"], "%Y-%m-%d").date()
                    if pag.get("data_pagamento")
                    else date.today()
                ),
                descricao=pag.get("descricao"),
            )
            lista_pagamentos.append(pagamento)
            valor_total_bruto += pagamento.valor_bruto
            valor_total_irrf += pagamento.valor_irrf

        ind_ret = IndRetificacao.RETIFICADOR if retificacao else IndRetificacao.ORIGINAL

        xml = self.manager.gerar_r4010(periodo_apuracao, lista_pagamentos, ind_ret)

        logger.info(f"Evento R-4010 gerado: {len(lista_pagamentos)} pagamentos PF, período {periodo_apuracao}")

        return {
            "evento": "R-4010",
            "descricao": "Pagamentos/créditos a beneficiário pessoa física",
            "xml": xml,
            "cnpj": self.cnpj,
            "periodo_apuracao": periodo_apuracao,
            "quantidade_pagamentos": len(lista_pagamentos),
            "valor_total_bruto": str(valor_total_bruto),
            "valor_total_irrf": str(valor_total_irrf),
            "ambiente": self.ambiente.value,
            "status": "gerado",
        }

    def gerar_r4020(
        self,
        periodo_apuracao: str,
        pagamentos: list[dict[str, Any]],
        retificacao: bool = False,
    ) -> dict[str, Any]:
        """
        Gera evento R-4020 - Pagamentos a Beneficiário Pessoa Jurídica.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            pagamentos: Lista de pagamentos a PJ
            retificacao: Se é retificação

        Returns:
            Dict com resultado da geração
        """
        lista_pagamentos = []
        valor_total_bruto = Decimal("0")
        valor_total_retencoes = Decimal("0")

        for pag in pagamentos:
            pagamento = PagamentoBeneficiarioPJ(
                cnpj_beneficiario=pag["cnpj_beneficiario"].replace(".", "").replace("/", "").replace("-", ""),
                razao_social=pag["razao_social"],
                natureza_rendimento=pag["natureza_rendimento"],
                valor_bruto=Decimal(str(pag["valor_bruto"])),
                valor_irrf=Decimal(str(pag.get("valor_irrf", "0"))),
                valor_csll=Decimal(str(pag.get("valor_csll", "0"))),
                valor_cofins=Decimal(str(pag.get("valor_cofins", "0"))),
                valor_pis=Decimal(str(pag.get("valor_pis", "0"))),
                data_pagamento=(
                    datetime.strptime(pag["data_pagamento"], "%Y-%m-%d").date()
                    if pag.get("data_pagamento")
                    else date.today()
                ),
                numero_nf=pag.get("numero_nf"),
            )
            lista_pagamentos.append(pagamento)
            valor_total_bruto += pagamento.valor_bruto
            valor_total_retencoes += (
                pagamento.valor_irrf + pagamento.valor_csll + pagamento.valor_cofins + pagamento.valor_pis
            )

        ind_ret = IndRetificacao.RETIFICADOR if retificacao else IndRetificacao.ORIGINAL

        xml = self.manager.gerar_r4020(periodo_apuracao, lista_pagamentos, ind_ret)

        logger.info(f"Evento R-4020 gerado: {len(lista_pagamentos)} pagamentos PJ, período {periodo_apuracao}")

        return {
            "evento": "R-4020",
            "descricao": "Pagamentos/créditos a beneficiário pessoa jurídica",
            "xml": xml,
            "cnpj": self.cnpj,
            "periodo_apuracao": periodo_apuracao,
            "quantidade_pagamentos": len(lista_pagamentos),
            "valor_total_bruto": str(valor_total_bruto),
            "valor_total_retencoes": str(valor_total_retencoes),
            "ambiente": self.ambiente.value,
            "status": "gerado",
        }

    def gerar_r2099(
        self,
        periodo_apuracao: str,
        retificacao: bool = False,
    ) -> dict[str, Any]:
        """
        Gera evento R-2099 - Fechamento dos Eventos Periódicos.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            retificacao: Se é retificação

        Returns:
            Dict com resultado da geração
        """
        ind_ret = IndRetificacao.RETIFICADOR if retificacao else IndRetificacao.ORIGINAL

        xml = self.manager.gerar_r2099(periodo_apuracao, ind_ret)

        logger.info(f"Evento R-2099 gerado: fechamento período {periodo_apuracao}")

        return {
            "evento": "R-2099",
            "descricao": "Fechamento dos Eventos Periódicos",
            "xml": xml,
            "cnpj": self.cnpj,
            "periodo_apuracao": periodo_apuracao,
            "ambiente": self.ambiente.value,
            "status": "gerado",
        }

    def enviar_lote(self, eventos_xml: list[str]) -> dict[str, Any]:
        """
        Envia lote de eventos para a Receita Federal.

        Args:
            eventos_xml: Lista de XMLs de eventos

        Returns:
            Dict com resultado do envio
        """
        resultado = self.manager.enviar_lote(eventos_xml)

        logger.info(f"Lote EFD-Reinf enviado: {len(eventos_xml)} eventos")

        return {
            "xml_envio": resultado["xml_envio"],
            "quantidade_eventos": resultado["quantidade_eventos"],
            "ambiente": self.ambiente.value,
            "status": resultado["status"],
            "mensagem": "Lote preparado para envio" if self.cert_manager else "Modo simulado (sem certificado)",
        }

    def listar_naturezas_rendimento(self) -> dict[str, Any]:
        """
        Lista as naturezas de rendimento disponíveis.

        Returns:
            Dict com lista de naturezas
        """
        pf = {k: v for k, v in NATUREZAS_RENDIMENTO.items() if k.startswith("10")}
        pj = {k: v for k, v in NATUREZAS_RENDIMENTO.items() if k.startswith("15")}

        return {
            "pessoa_fisica": [{"codigo": k, "descricao": v} for k, v in pf.items()],
            "pessoa_juridica": [{"codigo": k, "descricao": v} for k, v in pj.items()],
        }

    def listar_classificacoes_tributarias(self) -> dict[str, Any]:
        """
        Lista as classificações tributárias disponíveis.

        Returns:
            Dict com lista de classificações
        """
        descricoes = {
            "01": "Empresa em geral",
            "02": "Optante pelo Simples Nacional",
            "03": "Microempreendedor Individual (MEI)",
            "04": "Produtor Rural Pessoa Jurídica",
            "06": "Agroindústria",
            "07": "Produtor Rural Pessoa Física",
            "08": "Consórcio",
            "09": "Entidade Imune ou Isenta",
            "10": "Missão Diplomática",
            "11": "Órgão Público",
        }

        return {
            "classificacoes": [
                {"codigo": ct.value, "descricao": descricoes.get(ct.value, ct.name)} for ct in ClassificacaoTributaria
            ]
        }

    def validar_status(self) -> dict[str, Any]:
        """
        Valida status da configuração EFD-Reinf.

        Returns:
            Dict com status da configuração
        """
        return {
            "ambiente": self.ambiente_str,
            "url": self.manager.url,
            "cnpj": self.cnpj,
            "certificado_configurado": self.cert_manager is not None,
            "certificado_valido": (self.cert_manager._loaded if self.cert_manager else False),
            "versao_layout": self.manager.VERSAO,
            "eventos_disponiveis": [
                "R-1000 - Informações do Contribuinte",
                "R-2010 - Retenção CP Serviços Tomados",
                "R-4010 - Pagamentos PF",
                "R-4020 - Pagamentos PJ",
                "R-2099 - Fechamento Periódico",
            ],
        }


# Singleton
_efd_reinf_service: EFDReinfService | None = None


def get_efd_reinf_service() -> EFDReinfService:
    """Retorna instância singleton do service."""
    global _efd_reinf_service
    if _efd_reinf_service is None:
        _efd_reinf_service = EFDReinfService()
    return _efd_reinf_service
