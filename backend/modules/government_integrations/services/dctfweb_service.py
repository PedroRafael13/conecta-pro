"""
Service para DCTFWeb.

Camada de serviço para operações de DCTFWeb.
"""

import os
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any

from ..core.dctfweb import (
    DCTFWebManager,
    DCTFWebDeclaracao,
    DebitoContribuicao,
    CreditoVinculavel,
    DARF,
    TipoDeclaracao,
    SituacaoDeclaracao,
    TipoCredito,
)

logger = logging.getLogger(__name__)


class DCTFWebService:
    """Service para operações DCTFWeb."""

    def __init__(self):
        """Inicializa o service."""
        self.cnpj = os.getenv("DCTFWEB_CNPJ", os.getenv("EMPRESA_CNPJ", "35710481000103"))
        self.razao_social = os.getenv("EMPRESA_RAZAO_SOCIAL", "Conecta Seguranca LTDA")
        self.ambiente = os.getenv("DCTFWEB_ENVIRONMENT", "producao")

        self.manager = DCTFWebManager(
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            ambiente=self.ambiente,
        )

        logger.info(
            f"DCTFWeb Service inicializado - Ambiente: {self.ambiente}, "
            f"CNPJ: {self.cnpj}"
        )

    def criar_declaracao(
        self,
        periodo_apuracao: str,
        tipo: str = "1",
    ) -> Dict[str, Any]:
        """
        Cria uma nova declaração DCTFWeb.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            tipo: Tipo da declaração (1=Mensal, 2=Anual, 3=Diária, 4=Especial)

        Returns:
            Dict com dados da declaração criada
        """
        tipo_enum = TipoDeclaracao(tipo)

        declaracao = self.manager.criar_declaracao(
            periodo_apuracao=periodo_apuracao,
            tipo=tipo_enum,
        )

        logger.info(f"DCTFWeb criada: período {periodo_apuracao}, tipo {tipo}")

        return {
            "periodo_apuracao": declaracao.periodo_apuracao,
            "tipo": declaracao.tipo.value,
            "tipo_descricao": self._get_tipo_descricao(declaracao.tipo),
            "situacao": declaracao.situacao.value,
            "cnpj": declaracao.cnpj,
            "razao_social": declaracao.razao_social,
            "total_debitos": str(declaracao.total_debitos),
            "total_creditos": str(declaracao.total_creditos),
            "saldo_a_pagar": str(declaracao.saldo_a_pagar),
        }

    def importar_esocial(
        self,
        periodo_apuracao: str,
        dados_esocial: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Cria declaração e importa dados do eSocial.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            dados_esocial: Dados vindos do eSocial

        Returns:
            Dict com declaração atualizada
        """
        declaracao = self.manager.criar_declaracao(periodo_apuracao)
        declaracao = self.manager.importar_esocial(declaracao, dados_esocial)

        logger.info(
            f"Importado eSocial para DCTFWeb: {len(declaracao.debitos)} débitos, "
            f"{len(declaracao.creditos)} créditos"
        )

        return self._declaracao_to_dict(declaracao)

    def importar_reinf(
        self,
        periodo_apuracao: str,
        dados_reinf: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Cria declaração e importa dados da EFD-Reinf.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            dados_reinf: Dados vindos da EFD-Reinf

        Returns:
            Dict com declaração atualizada
        """
        declaracao = self.manager.criar_declaracao(periodo_apuracao)
        declaracao = self.manager.importar_reinf(declaracao, dados_reinf)

        logger.info(f"Importado EFD-Reinf para DCTFWeb: {len(declaracao.creditos)} créditos")

        return self._declaracao_to_dict(declaracao)

    def consolidar_declaracao(
        self,
        periodo_apuracao: str,
        dados_esocial: Optional[Dict[str, Any]] = None,
        dados_reinf: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Consolida declaração com dados do eSocial e EFD-Reinf.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            dados_esocial: Dados do eSocial
            dados_reinf: Dados da EFD-Reinf

        Returns:
            Dict com declaração consolidada
        """
        declaracao = self.manager.criar_declaracao(periodo_apuracao)

        if dados_esocial:
            declaracao = self.manager.importar_esocial(declaracao, dados_esocial)

        if dados_reinf:
            declaracao = self.manager.importar_reinf(declaracao, dados_reinf)

        logger.info(
            f"DCTFWeb consolidada: {len(declaracao.debitos)} débitos, "
            f"{len(declaracao.creditos)} créditos"
        )

        return self._declaracao_to_dict(declaracao)

    def gerar_darfs(
        self,
        periodo_apuracao: str,
        dados_esocial: Optional[Dict[str, Any]] = None,
        dados_reinf: Optional[Dict[str, Any]] = None,
        data_vencimento: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera DARFs para uma declaração.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            dados_esocial: Dados do eSocial
            dados_reinf: Dados da EFD-Reinf
            data_vencimento: Data de vencimento (YYYY-MM-DD)

        Returns:
            Dict com DARFs gerados
        """
        declaracao = self.manager.criar_declaracao(periodo_apuracao)

        if dados_esocial:
            declaracao = self.manager.importar_esocial(declaracao, dados_esocial)

        if dados_reinf:
            declaracao = self.manager.importar_reinf(declaracao, dados_reinf)

        dt_venc = None
        if data_vencimento:
            dt_venc = datetime.strptime(data_vencimento, "%Y-%m-%d").date()

        darfs = self.manager.gerar_darfs(declaracao, dt_venc)

        logger.info(f"Gerados {len(darfs)} DARFs para período {periodo_apuracao}")

        return {
            "periodo_apuracao": periodo_apuracao,
            "total_debitos": str(declaracao.total_debitos),
            "total_creditos": str(declaracao.total_creditos),
            "saldo_a_pagar": str(declaracao.saldo_a_pagar),
            "quantidade_darfs": len(darfs),
            "darfs": [self._darf_to_dict(d) for d in darfs],
        }

    def transmitir(
        self,
        periodo_apuracao: str,
        dados_esocial: Optional[Dict[str, Any]] = None,
        dados_reinf: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Transmite declaração DCTFWeb.

        Args:
            periodo_apuracao: Período (YYYY-MM)
            dados_esocial: Dados do eSocial
            dados_reinf: Dados da EFD-Reinf

        Returns:
            Dict com resultado da transmissão
        """
        declaracao = self.manager.criar_declaracao(periodo_apuracao)

        if dados_esocial:
            declaracao = self.manager.importar_esocial(declaracao, dados_esocial)

        if dados_reinf:
            declaracao = self.manager.importar_reinf(declaracao, dados_reinf)

        self.manager.gerar_darfs(declaracao)
        resultado = self.manager.transmitir(declaracao)

        logger.info(f"DCTFWeb transmitida: {resultado['numero_recibo']}")

        return resultado

    def consultar(self, periodo_apuracao: str) -> Dict[str, Any]:
        """
        Consulta declaração por período.

        Args:
            periodo_apuracao: Período (YYYY-MM)

        Returns:
            Dict com dados da declaração
        """
        return self.manager.consultar(periodo_apuracao)

    def listar_codigos_receita(self) -> Dict[str, Any]:
        """
        Lista códigos de receita disponíveis.

        Returns:
            Dict com códigos de receita
        """
        return {
            "codigos": [
                {"codigo": k, "descricao": v}
                for k, v in self.manager.CODIGOS_RECEITA.items()
            ]
        }

    def listar_tipos_declaracao(self) -> Dict[str, Any]:
        """
        Lista tipos de declaração disponíveis.

        Returns:
            Dict com tipos de declaração
        """
        descricoes = {
            "1": "DCTFWeb Mensal",
            "2": "DCTFWeb 13º Salário (Anual)",
            "3": "DCTFWeb Diária (Espetáculos Desportivos)",
            "4": "DCTFWeb Especial",
        }

        return {
            "tipos": [
                {"codigo": t.value, "descricao": descricoes.get(t.value, t.name)}
                for t in TipoDeclaracao
            ]
        }

    def listar_tipos_credito(self) -> Dict[str, Any]:
        """
        Lista tipos de crédito vinculáveis.

        Returns:
            Dict com tipos de crédito
        """
        descricoes = {
            "1": "Salário-Família",
            "2": "Salário-Maternidade",
            "3": "Retenção Lei 9.711/98",
            "4": "Compensação",
            "5": "Suspensão",
            "6": "Parcelamento",
        }

        return {
            "tipos": [
                {"codigo": t.value, "descricao": descricoes.get(t.value, t.name)}
                for t in TipoCredito
            ]
        }

    def validar_status(self) -> Dict[str, Any]:
        """
        Valida status da configuração DCTFWeb.

        Returns:
            Dict com status
        """
        return {
            "ambiente": self.ambiente,
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "portal_ecac": "https://cav.receita.fazenda.gov.br/",
            "operacoes_disponiveis": [
                "Criar declaração",
                "Importar eSocial",
                "Importar EFD-Reinf",
                "Consolidar declaração",
                "Gerar DARFs",
                "Transmitir",
                "Consultar",
            ],
        }

    def _get_tipo_descricao(self, tipo: TipoDeclaracao) -> str:
        """Retorna descrição do tipo de declaração."""
        descricoes = {
            TipoDeclaracao.MENSAL: "DCTFWeb Mensal",
            TipoDeclaracao.ANUAL: "DCTFWeb 13º Salário",
            TipoDeclaracao.DIARIA: "DCTFWeb Diária",
            TipoDeclaracao.ESPECIAL: "DCTFWeb Especial",
        }
        return descricoes.get(tipo, tipo.name)

    def _declaracao_to_dict(self, declaracao: DCTFWebDeclaracao) -> Dict[str, Any]:
        """Converte declaração para dict."""
        return {
            "numero_recibo": declaracao.numero_recibo,
            "tipo": declaracao.tipo.value,
            "tipo_descricao": self._get_tipo_descricao(declaracao.tipo),
            "situacao": declaracao.situacao.value,
            "periodo_apuracao": declaracao.periodo_apuracao,
            "data_transmissao": (
                declaracao.data_transmissao.isoformat()
                if declaracao.data_transmissao else None
            ),
            "cnpj": declaracao.cnpj,
            "razao_social": declaracao.razao_social,
            "debitos": [self._debito_to_dict(d) for d in declaracao.debitos],
            "creditos": [self._credito_to_dict(c) for c in declaracao.creditos],
            "total_debitos": str(declaracao.total_debitos),
            "total_creditos": str(declaracao.total_creditos),
            "saldo_a_pagar": str(declaracao.saldo_a_pagar),
            "darfs": [self._darf_to_dict(d) for d in declaracao.darfs],
        }

    def _debito_to_dict(self, debito: DebitoContribuicao) -> Dict[str, Any]:
        """Converte débito para dict."""
        return {
            "codigo_receita": debito.codigo_receita,
            "descricao": debito.descricao,
            "valor_principal": str(debito.valor_principal),
            "valor_acrescimos": str(debito.valor_acrescimos),
            "valor_total": str(debito.valor_total),
            "periodo_apuracao": debito.periodo_apuracao,
        }

    def _credito_to_dict(self, credito: CreditoVinculavel) -> Dict[str, Any]:
        """Converte crédito para dict."""
        return {
            "tipo": credito.tipo.value,
            "descricao": credito.descricao,
            "valor": str(credito.valor),
            "periodo_apuracao": credito.periodo_apuracao,
            "numero_documento": credito.numero_documento,
        }

    def _darf_to_dict(self, darf: DARF) -> Dict[str, Any]:
        """Converte DARF para dict."""
        return {
            "codigo_receita": darf.codigo_receita,
            "periodo_apuracao": darf.periodo_apuracao,
            "data_vencimento": darf.data_vencimento.isoformat(),
            "valor_principal": str(darf.valor_principal),
            "valor_multa": str(darf.valor_multa),
            "valor_juros": str(darf.valor_juros),
            "valor_total": str(darf.valor_total),
            "numero_referencia": darf.numero_referencia,
            "codigo_barras": darf.codigo_barras,
            "linha_digitavel": darf.linha_digitavel,
        }


# Singleton
_dctfweb_service: Optional[DCTFWebService] = None


def get_dctfweb_service() -> DCTFWebService:
    """Retorna instância singleton do service."""
    global _dctfweb_service
    if _dctfweb_service is None:
        _dctfweb_service = DCTFWebService()
    return _dctfweb_service
