"""
Service para CT-e (Conhecimento de Transporte Eletronico).

Camada de servico que encapsula a logica de negocio do CT-e.
"""

import logging
import os
from decimal import Decimal
from typing import Any

from ..core.cte import (
    Carga,
    ComponenteValor,
    CTe,
    CTeManager,
    ModalTransporte,
    NFReferenciada,
    Participante,
    TipoServico,
    TomadorServico,
)

logger = logging.getLogger(__name__)


class CTeService:
    """
    Service para operacoes do CT-e.

    Encapsula todas as operacoes relacionadas ao CT-e,
    incluindo criacao, geracao de XML e consultas.
    """

    # Descricoes dos modais
    MODAIS = {
        "01": "Rodoviario",
        "02": "Aereo",
        "03": "Aquaviario",
        "04": "Ferroviario",
        "05": "Dutoviario",
        "06": "Multimodal",
    }

    # Descricoes dos tipos de servico
    TIPOS_SERVICO = {
        "0": "Normal",
        "1": "Subcontratacao",
        "2": "Redespacho",
        "3": "Redespacho Intermediario",
        "4": "Servico Vinculado Multimodal",
    }

    def __init__(self):
        """Inicializa o service."""
        self.cnpj = os.environ.get("CTE_CNPJ", os.environ.get("EMPRESA_CNPJ", ""))
        self.razao_social = os.environ.get("EMPRESA_RAZAO_SOCIAL", "Empresa")
        self.ie = os.environ.get("EMPRESA_IE", "")
        self.uf = os.environ.get("EMPRESA_UF", "SP")
        self.ambiente = os.environ.get("CTE_AMBIENTE", "homologacao")

        self.manager = CTeManager(
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            inscricao_estadual=self.ie,
            uf=self.uf,
            ambiente=self.ambiente,
        )

        # Cache de CT-e criados
        self._ctes: dict[str, CTe] = {}

        logger.info(f"CTeService iniciado: CNPJ={self.cnpj}, UF={self.uf}, Ambiente={self.ambiente}")

    def validar_status(self) -> dict[str, Any]:
        """Valida e retorna status da configuracao."""
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "inscricao_estadual": self.ie,
            "uf": self.uf,
            "ambiente": self.ambiente,
            "versao": "4.00",
            "operacoes_disponiveis": [
                "criar_cte",
                "gerar_xml",
                "consultar_status_servico",
                "listar_modais",
                "listar_tipos_servico",
            ],
        }

    def criar_cte(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria um novo CT-e.

        Args:
            dados: Dados do CT-e

        Returns:
            CT-e criado
        """
        numero = dados["numero"]
        serie = dados.get("serie", 1)
        modal_str = dados.get("modal", "01")
        modal = ModalTransporte(modal_str) if modal_str else ModalTransporte.RODOVIARIO

        cte = self.manager.criar_cte(
            numero=numero,
            serie=serie,
            modal=modal,
        )

        # Configura tipo de servico
        tipo_servico_str = dados.get("tipo_servico", "0")
        cte.tipo_servico = TipoServico(tipo_servico_str)

        # Configura tomador
        tomador_str = dados.get("tomador", "0")
        cte.tomador = TomadorServico(tomador_str)

        # Configura municipios
        cte.municipio_inicio = dados.get("municipio_inicio", "")
        cte.uf_inicio = dados.get("uf_inicio", self.uf)
        cte.municipio_fim = dados.get("municipio_fim", "")
        cte.uf_fim = dados.get("uf_fim", "")

        # Configura participantes
        if dados.get("remetente"):
            cte.remetente = self._criar_participante(dados["remetente"])
        if dados.get("destinatario"):
            cte.destinatario = self._criar_participante(dados["destinatario"])
        if dados.get("expedidor"):
            cte.expedidor = self._criar_participante(dados["expedidor"])
        if dados.get("recebedor"):
            cte.recebedor = self._criar_participante(dados["recebedor"])

        # Configura NF-e referenciadas
        if dados.get("nf_referenciadas"):
            for nf in dados["nf_referenciadas"]:
                cte.nf_referenciadas.append(
                    NFReferenciada(
                        chave=nf["chave"],
                        pin=nf.get("pin"),
                    )
                )

        # Configura carga
        if dados.get("carga"):
            carga_dados = dados["carga"]
            cte.carga = Carga(
                valor_total_carga=Decimal(str(carga_dados["valor_total_carga"])),
                produto_predominante=carga_dados["produto_predominante"],
                peso_bruto=Decimal(str(carga_dados.get("peso_bruto", 0))),
                peso_cubado=Decimal(str(carga_dados.get("peso_cubado", 0))),
                peso_aferido=Decimal(str(carga_dados.get("peso_aferido", 0))),
                quantidade_volumes=carga_dados.get("quantidade_volumes", 0),
                unidade_medida=carga_dados.get("unidade_medida", "KG"),
            )

        # Configura valores
        cte.valor_total_servico = Decimal(str(dados.get("valor_total_servico", 0)))
        cte.valor_receber = Decimal(str(dados.get("valor_receber", 0)))

        # Configura componentes de valor
        if dados.get("componentes_valor"):
            for comp in dados["componentes_valor"]:
                cte.componentes_valor.append(
                    ComponenteValor(
                        nome=comp["nome"],
                        valor=Decimal(str(comp["valor"])),
                    )
                )

        # Configura ICMS
        cte.icms_base_calculo = Decimal(str(dados.get("icms_base_calculo", 0)))
        cte.icms_aliquota = Decimal(str(dados.get("icms_aliquota", 0)))
        cte.icms_valor = Decimal(str(dados.get("icms_valor", 0)))
        cte.icms_cst = dados.get("icms_cst", "00")

        # Armazena no cache
        key = f"{numero}-{serie}"
        self._ctes[key] = cte

        logger.info(f"CT-e criado: {numero}/{serie}")

        return {
            "numero": cte.numero,
            "serie": cte.serie,
            "modal": cte.modal.value,
            "tipo_servico": cte.tipo_servico.value,
            "tomador": cte.tomador.value,
            "situacao": cte.situacao.value,
            "municipio_inicio": cte.municipio_inicio,
            "municipio_fim": cte.municipio_fim,
            "valor_total_servico": str(cte.valor_total_servico),
            "valor_receber": str(cte.valor_receber),
        }

    def gerar_xml(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Gera XML do CT-e.

        Args:
            dados: Dados do CT-e

        Returns:
            XML gerado
        """
        numero = dados["numero"]
        serie = dados.get("serie", 1)
        key = f"{numero}-{serie}"

        # Verifica se CT-e ja existe no cache
        if key in self._ctes:
            cte = self._ctes[key]
        else:
            # Cria novo CT-e com os dados fornecidos
            self.criar_cte(dados)
            cte = self._ctes[key]

        xml = self.manager.gerar_xml(cte)

        logger.info(f"XML gerado para CT-e {numero}/{serie}")

        return {
            "numero": cte.numero,
            "serie": cte.serie,
            "xml": xml,
        }

    def consultar_status_servico(self) -> dict[str, Any]:
        """
        Consulta status do servico CT-e na SEFAZ.

        Returns:
            Status do servico
        """
        resultado = self.manager.consultar_status_servico()

        logger.info(f"Consultado status do servico CT-e: {resultado['status']}")

        return resultado

    def listar_modais(self) -> dict[str, Any]:
        """Lista modais de transporte disponiveis."""
        return {"modais": [{"codigo": k, "descricao": v} for k, v in self.MODAIS.items()]}

    def listar_tipos_servico(self) -> dict[str, Any]:
        """Lista tipos de servico disponiveis."""
        return {"tipos_servico": [{"codigo": k, "descricao": v} for k, v in self.TIPOS_SERVICO.items()]}

    def obter_cte(self, numero: int, serie: int = 1) -> dict[str, Any] | None:
        """
        Obtem CT-e do cache.

        Args:
            numero: Numero do CT-e
            serie: Serie

        Returns:
            CT-e ou None
        """
        key = f"{numero}-{serie}"
        cte = self._ctes.get(key)

        if not cte:
            return None

        return {
            "numero": cte.numero,
            "serie": cte.serie,
            "modal": cte.modal.value,
            "tipo_servico": cte.tipo_servico.value,
            "tomador": cte.tomador.value,
            "situacao": cte.situacao.value,
            "municipio_inicio": cte.municipio_inicio,
            "municipio_fim": cte.municipio_fim,
            "valor_total_servico": str(cte.valor_total_servico),
            "valor_receber": str(cte.valor_receber),
        }

    def listar_ctes(self) -> dict[str, Any]:
        """Lista todos os CT-e em cache."""
        return {
            "ctes": [
                {
                    "numero": cte.numero,
                    "serie": cte.serie,
                    "modal": cte.modal.value,
                    "situacao": cte.situacao.value,
                    "valor_total_servico": str(cte.valor_total_servico),
                }
                for cte in self._ctes.values()
            ]
        }

    def limpar_cache(self) -> dict[str, Any]:
        """Limpa cache de CT-e."""
        count = len(self._ctes)
        self._ctes.clear()

        logger.info(f"Cache limpo: {count} CT-e removidos")

        return {"message": f"Cache limpo: {count} CT-e removidos"}

    def _criar_participante(self, dados: dict[str, Any]) -> Participante:
        """Cria participante a partir de dados."""
        return Participante(
            tipo=dados.get("tipo", "remetente"),
            cnpj_cpf=dados["cnpj_cpf"].replace(".", "").replace("-", "").replace("/", ""),
            nome=dados["nome"],
            inscricao_estadual=dados.get("inscricao_estadual"),
            endereco=dados.get("endereco"),
            numero=dados.get("numero"),
            bairro=dados.get("bairro"),
            codigo_municipio=dados.get("codigo_municipio"),
            municipio=dados.get("municipio"),
            uf=dados.get("uf"),
            cep=dados.get("cep"),
            telefone=dados.get("telefone"),
            email=dados.get("email"),
        )


# Singleton
_service_instance: CTeService | None = None


def get_cte_service() -> CTeService:
    """Retorna instancia singleton do service."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CTeService()
    return _service_instance
