"""
Service para FGTS Digital.

Camada de serviço que encapsula a lógica de negócio do FGTS Digital.
"""

import os
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any

from ..core.fgts_digital import (
    FGTSDigitalManager,
    TrabalhadorFGTS,
    TipoRecolhimento,
    ModalidadeSaque,
    RecolhimentoRescisorio,
    SituacaoGuia,
)

logger = logging.getLogger(__name__)


class FGTSDigitalService:
    """
    Service para operações do FGTS Digital.

    Encapsula todas as operações relacionadas ao FGTS Digital,
    incluindo cálculos, geração de guias e consultas.
    """

    # Descrições das categorias
    CATEGORIAS = {
        "101": "Empregado Geral",
        "104": "Empregado Doméstico",
        "103": "Aprendiz",
        "106": "Trabalhador Temporário",
        "721": "Diretor com FGTS",
    }

    # Descrições das modalidades de saque
    MODALIDADES_SAQUE = {
        "01": "Rescisão sem justa causa",
        "04": "Aposentadoria",
        "23": "Falecimento do trabalhador",
        "98": "Saque-aniversário",
        "99": "Calamidade pública",
    }

    def __init__(self):
        """Inicializa o service."""
        self.cnpj = os.environ.get("FGTS_CNPJ", os.environ.get("EMPRESA_CNPJ", ""))
        self.razao_social = os.environ.get("EMPRESA_RAZAO_SOCIAL", "Empresa")
        self.ambiente = os.environ.get("FGTS_AMBIENTE", "homologacao")

        self.manager = FGTSDigitalManager(
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            ambiente=self.ambiente,
        )

        logger.info(f"FGTSDigitalService iniciado: CNPJ={self.cnpj}, ambiente={self.ambiente}")

    def validar_status(self) -> Dict[str, Any]:
        """Valida e retorna status da configuração."""
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "ambiente": self.ambiente,
            "portal_url": self.manager.base_url,
            "aliquota_fgts": "8%",
            "aliquota_multa": "40%",
            "operacoes_disponiveis": [
                "calcular_folha",
                "importar_esocial",
                "gerar_guia_mensal",
                "gerar_guia_rescisoria",
                "consultar_debitos",
                "consultar_extrato",
                "simular_saque",
                "relatorio_mensal",
            ],
        }

    def calcular_folha(
        self,
        competencia: str,
        trabalhadores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula FGTS da folha de pagamento.

        Args:
            competencia: Competência YYYY-MM
            trabalhadores: Lista de trabalhadores

        Returns:
            Resultado do cálculo
        """
        lista_trabalhadores = []

        for t in trabalhadores:
            trab = TrabalhadorFGTS(
                cpf=t["cpf"].replace(".", "").replace("-", ""),
                nome=t["nome"],
                pis_pasep=t["pis_pasep"],
                data_admissao=datetime.strptime(t["data_admissao"], "%Y-%m-%d").date(),
                categoria=t.get("categoria", "101"),
                remuneracao=Decimal(str(t["remuneracao"])),
            )

            # Base FGTS
            if t.get("base_fgts"):
                trab.remuneracao = Decimal(str(t["base_fgts"]))

            # 13º salário
            if t.get("valor_13_salario"):
                trab.valor_fgts_13 = Decimal(str(t["valor_13_salario"])) * self.manager.ALIQUOTA_FGTS

            lista_trabalhadores.append(trab)

        resultado = self.manager.calcular_fgts_folha(lista_trabalhadores, competencia)

        logger.info(f"FGTS calculado: {competencia}, {len(lista_trabalhadores)} trabalhadores")

        return resultado

    def importar_esocial(
        self,
        competencia: str,
        eventos_s1200: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Importa dados do eSocial.

        Args:
            competencia: Competência YYYY-MM
            eventos_s1200: Eventos S-1200

        Returns:
            Trabalhadores importados com FGTS calculado
        """
        dados_esocial = {"eventos_s1200": eventos_s1200}

        trabalhadores = self.manager.importar_esocial(dados_esocial, competencia)

        total_fgts = sum(t.valor_total for t in trabalhadores)

        return {
            "competencia": competencia,
            "quantidade_importados": len(trabalhadores),
            "total_fgts": str(total_fgts),
            "trabalhadores": [
                {
                    "cpf": t.cpf,
                    "nome": t.nome,
                    "pis_pasep": t.pis_pasep,
                    "categoria": t.categoria,
                    "remuneracao": str(t.remuneracao),
                    "fgts_mensal": str(t.valor_fgts),
                    "fgts_13": str(t.valor_fgts_13),
                    "fgts_total": str(t.valor_total),
                }
                for t in trabalhadores
            ]
        }

    def gerar_guia_mensal(
        self,
        competencia: str,
        trabalhadores: List[Dict[str, Any]],
        data_vencimento: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera guia de recolhimento mensal (GRFGTS).

        Args:
            competencia: Competência YYYY-MM
            trabalhadores: Lista de trabalhadores
            data_vencimento: Data de vencimento opcional

        Returns:
            Guia gerada com código PIX
        """
        lista_trabalhadores = []

        for t in trabalhadores:
            trab = TrabalhadorFGTS(
                cpf=t["cpf"].replace(".", "").replace("-", ""),
                nome=t["nome"],
                pis_pasep=t["pis_pasep"],
                data_admissao=datetime.strptime(t["data_admissao"], "%Y-%m-%d").date(),
                categoria=t.get("categoria", "101"),
                remuneracao=Decimal(str(t["remuneracao"])),
            )

            # Calcula FGTS
            trab.valor_fgts = trab.remuneracao * self.manager.ALIQUOTA_FGTS

            # 13º salário
            if t.get("valor_13_salario"):
                trab.valor_fgts_13 = Decimal(str(t["valor_13_salario"])) * self.manager.ALIQUOTA_FGTS

            lista_trabalhadores.append(trab)

        # Data de vencimento
        dt_vencimento = None
        if data_vencimento:
            dt_vencimento = datetime.strptime(data_vencimento, "%Y-%m-%d").date()

        guia = self.manager.gerar_guia_mensal(lista_trabalhadores, competencia, dt_vencimento)

        return {
            "guia": {
                "numero": guia.numero,
                "competencia": guia.competencia,
                "data_geracao": guia.data_geracao.isoformat(),
                "data_vencimento": guia.data_vencimento.isoformat(),
                "valor_principal": str(guia.valor_principal),
                "valor_atualizacao": str(guia.valor_atualizacao),
                "valor_multa": str(guia.valor_multa),
                "valor_juros": str(guia.valor_juros),
                "valor_total": str(guia.valor_total),
                "chave_pix": guia.chave_pix,
                "codigo_pix": guia.codigo_pix,
                "qrcode_pix": guia.qrcode_pix,
                "situacao": guia.situacao.value,
            },
            "trabalhadores": [
                {
                    "cpf": t.cpf,
                    "nome": t.nome,
                    "fgts": str(t.valor_total),
                }
                for t in lista_trabalhadores
            ],
        }

    def gerar_guia_rescisoria(
        self,
        dados_rescisao: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera guia de recolhimento rescisório (GRRF).

        Args:
            dados_rescisao: Dados da rescisão

        Returns:
            Guia rescisória gerada
        """
        trabalhador = TrabalhadorFGTS(
            cpf=dados_rescisao["cpf"].replace(".", "").replace("-", ""),
            nome=dados_rescisao["nome"],
            pis_pasep=dados_rescisao["pis_pasep"],
            data_admissao=datetime.strptime(dados_rescisao["data_admissao"], "%Y-%m-%d").date(),
            remuneracao=Decimal(str(dados_rescisao["remuneracao"])),
        )

        rescisao = RecolhimentoRescisorio(
            trabalhador=trabalhador,
            data_desligamento=datetime.strptime(dados_rescisao["data_desligamento"], "%Y-%m-%d").date(),
            motivo_desligamento=dados_rescisao["motivo_desligamento"],
            aviso_previo=dados_rescisao["aviso_previo"],
            saldo_fgts=Decimal(str(dados_rescisao["saldo_fgts"])),
        )

        guia = self.manager.gerar_guia_rescisoria(rescisao)

        return {
            "guia": {
                "numero": guia.numero,
                "cpf_trabalhador": guia.cpf_trabalhador,
                "nome_trabalhador": guia.nome_trabalhador,
                "data_desligamento": guia.data_desligamento.isoformat(),
                "valor_deposito_mes": str(guia.valor_deposito_mes),
                "valor_deposito_aviso": str(guia.valor_deposito_aviso),
                "valor_deposito_13": str(guia.valor_deposito_13),
                "valor_multa_rescisoria": str(guia.valor_multa_rescisoria),
                "valor_total": str(guia.valor_total),
                "codigo_pix": guia.codigo_pix,
                "qrcode_pix": guia.qrcode_pix,
                "data_vencimento": guia.data_vencimento.isoformat() if guia.data_vencimento else None,
                "situacao": guia.situacao.value,
            },
            "rescisao": {
                "motivo": rescisao.motivo_desligamento,
                "aviso_previo": rescisao.aviso_previo,
                "saldo_fgts": str(rescisao.saldo_fgts),
                "multa_40_percent": str(rescisao.multa_40_percent),
            }
        }

    def consultar_debitos(
        self,
        competencia_inicio: Optional[str] = None,
        competencia_fim: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta débitos de FGTS.

        Args:
            competencia_inicio: Competência inicial
            competencia_fim: Competência final

        Returns:
            Lista de débitos
        """
        debitos = self.manager.consultar_debitos(competencia_inicio, competencia_fim)

        return {
            "cnpj": self.cnpj,
            "periodo": {
                "inicio": competencia_inicio,
                "fim": competencia_fim,
            },
            "quantidade": len(debitos),
            "debitos": [
                {
                    "competencia": d.competencia,
                    "tipo": d.tipo.value,
                    "valor_principal": str(d.valor_principal),
                    "valor_atualizacao": str(d.valor_atualizacao),
                    "valor_multa": str(d.valor_multa),
                    "valor_juros": str(d.valor_juros),
                    "valor_total": str(d.valor_total),
                    "data_vencimento": d.data_vencimento.isoformat() if d.data_vencimento else None,
                }
                for d in debitos
            ]
        }

    def consultar_extrato(
        self,
        cpf: str,
        pis_pasep: str
    ) -> Dict[str, Any]:
        """
        Consulta extrato do FGTS de um trabalhador.

        Args:
            cpf: CPF do trabalhador
            pis_pasep: Número PIS/PASEP

        Returns:
            Extrato do trabalhador
        """
        return self.manager.consultar_extrato_trabalhador(cpf, pis_pasep)

    def simular_saque(
        self,
        cpf: str,
        modalidade: str,
        valor_solicitado: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simula saque do FGTS.

        Args:
            cpf: CPF do trabalhador
            modalidade: Código da modalidade
            valor_solicitado: Valor solicitado

        Returns:
            Simulação do saque
        """
        mod = ModalidadeSaque(modalidade)
        valor = Decimal(valor_solicitado) if valor_solicitado else None

        return self.manager.simular_saque(cpf, mod, valor)

    def gerar_relatorio_mensal(
        self,
        competencia: str,
        trabalhadores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Gera relatório mensal de FGTS.

        Args:
            competencia: Competência YYYY-MM
            trabalhadores: Lista de trabalhadores

        Returns:
            Relatório detalhado
        """
        lista_trabalhadores = []

        for t in trabalhadores:
            trab = TrabalhadorFGTS(
                cpf=t["cpf"].replace(".", "").replace("-", ""),
                nome=t["nome"],
                pis_pasep=t["pis_pasep"],
                data_admissao=datetime.strptime(t["data_admissao"], "%Y-%m-%d").date(),
                categoria=t.get("categoria", "101"),
                remuneracao=Decimal(str(t["remuneracao"])),
            )

            # Calcula FGTS
            trab.valor_fgts = trab.remuneracao * self.manager.ALIQUOTA_FGTS

            # 13º salário
            if t.get("valor_13_salario"):
                trab.valor_fgts_13 = Decimal(str(t["valor_13_salario"])) * self.manager.ALIQUOTA_FGTS

            lista_trabalhadores.append(trab)

        return self.manager.gerar_relatorio_mensal(lista_trabalhadores, competencia)

    def listar_categorias(self) -> Dict[str, Any]:
        """Lista categorias de trabalhadores."""
        return {
            "categorias": [
                {"codigo": k, "descricao": v}
                for k, v in self.CATEGORIAS.items()
            ]
        }

    def listar_modalidades_saque(self) -> Dict[str, Any]:
        """Lista modalidades de saque."""
        return {
            "modalidades": [
                {"codigo": k, "descricao": v}
                for k, v in self.MODALIDADES_SAQUE.items()
            ]
        }


# Singleton
_service_instance: Optional[FGTSDigitalService] = None


def get_fgts_digital_service() -> FGTSDigitalService:
    """Retorna instância singleton do service."""
    global _service_instance
    if _service_instance is None:
        _service_instance = FGTSDigitalService()
    return _service_instance
