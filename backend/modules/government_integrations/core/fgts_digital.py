"""
FGTS Digital - Fundo de Garantia do Tempo de Serviço.

Portal: https://fgtsdigital.caixa.gov.br/
Documentação: Manual do FGTS Digital

O FGTS Digital substituiu o SEFIP/GFIP e é integrado com o eSocial.
A partir de março/2024, os recolhimentos são feitos via PIX.

Funcionalidades:
- Consulta de débitos
- Geração de guias (GRFGTS via PIX)
- Consulta de recolhimentos
- Parcelamentos
- Compensações
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class TipoRecolhimento(StrEnum):
    """Tipo de recolhimento FGTS."""

    MENSAL = "1"  # Recolhimento mensal
    RESCISORIO = "2"  # Recolhimento rescisório
    RECURSAL = "3"  # Depósito recursal
    INFORME_COMPETENCIA = "4"  # Competência declarada sem movimento


class ModalidadeSaque(StrEnum):
    """Modalidade de saque FGTS."""

    RESCISAO = "01"
    APOSENTADORIA = "04"
    FALECIMENTO = "23"
    SAQUE_ANIVERSARIO = "98"
    CALAMIDADE = "99"


class SituacaoGuia(StrEnum):
    """Situação da guia FGTS."""

    GERADA = "gerada"
    PAGA = "paga"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


@dataclass
class TrabalhadorFGTS:
    """Dados do trabalhador para FGTS."""

    cpf: str
    nome: str
    pis_pasep: str
    data_admissao: date
    categoria: str = "101"  # Empregado geral
    remuneracao: Decimal = Decimal("0")
    valor_fgts: Decimal = Decimal("0")
    valor_fgts_13: Decimal = Decimal("0")

    @property
    def valor_total(self) -> Decimal:
        return self.valor_fgts + self.valor_fgts_13


@dataclass
class DebitoFGTS:
    """Débito de FGTS."""

    competencia: str  # YYYY-MM
    tipo: TipoRecolhimento
    valor_principal: Decimal
    valor_atualizacao: Decimal = Decimal("0")
    valor_multa: Decimal = Decimal("0")
    valor_juros: Decimal = Decimal("0")
    data_vencimento: date | None = None

    @property
    def valor_total(self) -> Decimal:
        return self.valor_principal + self.valor_atualizacao + self.valor_multa + self.valor_juros


@dataclass
class GRFGTS:
    """Guia de Recolhimento do FGTS."""

    numero: str
    competencia: str
    data_geracao: datetime
    data_vencimento: date
    valor_principal: Decimal
    valor_atualizacao: Decimal = Decimal("0")
    valor_multa: Decimal = Decimal("0")
    valor_juros: Decimal = Decimal("0")
    valor_total: Decimal = Decimal("0")

    # PIX
    chave_pix: str | None = None
    codigo_pix: str | None = None  # Copia e cola
    qrcode_pix: str | None = None  # QR Code base64

    # Situação
    situacao: SituacaoGuia = SituacaoGuia.GERADA
    data_pagamento: datetime | None = None

    def __post_init__(self):
        if self.valor_total == Decimal("0"):
            self.valor_total = self.valor_principal + self.valor_atualizacao + self.valor_multa + self.valor_juros


@dataclass
class RecolhimentoRescisorio:
    """Dados para recolhimento rescisório."""

    trabalhador: TrabalhadorFGTS
    data_desligamento: date
    motivo_desligamento: str
    aviso_previo: str  # "trabalhado", "indenizado", "ausencia"
    saldo_fgts: Decimal = Decimal("0")
    multa_40_percent: Decimal = Decimal("0")
    valor_total: Decimal = Decimal("0")

    def calcular_multa(self) -> Decimal:
        """Calcula multa rescisória de 40%."""
        self.multa_40_percent = self.saldo_fgts * Decimal("0.40")
        self.valor_total = self.saldo_fgts + self.multa_40_percent
        return self.multa_40_percent


@dataclass
class GuiaRescisoria:
    """Guia de Recolhimento Rescisório."""

    numero: str
    cpf_trabalhador: str
    nome_trabalhador: str
    data_desligamento: date
    valor_deposito_mes: Decimal
    valor_deposito_aviso: Decimal
    valor_deposito_13: Decimal
    valor_multa_rescisoria: Decimal
    valor_total: Decimal

    # PIX
    codigo_pix: str | None = None
    qrcode_pix: str | None = None

    data_vencimento: date | None = None
    situacao: SituacaoGuia = SituacaoGuia.GERADA


class FGTSDigitalManager:
    """
    Gerenciador do FGTS Digital.

    Integra dados do eSocial para gerar guias de FGTS via PIX.
    """

    # URLs do FGTS Digital
    URL_PRODUCAO = "https://fgtsdigital.caixa.gov.br"
    URL_HOMOLOGACAO = "https://fgtsdigital-hom.caixa.gov.br"

    # Alíquota padrão FGTS
    ALIQUOTA_FGTS = Decimal("0.08")  # 8%
    ALIQUOTA_MULTA_RESCISORIA = Decimal("0.40")  # 40%

    def __init__(
        self,
        cnpj: str,
        razao_social: str,
        ambiente: str = "producao",
    ):
        """
        Inicializa o gerenciador.

        Args:
            cnpj: CNPJ do empregador
            razao_social: Razão social
            ambiente: 'producao' ou 'homologacao'
        """
        self.cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        self.razao_social = razao_social
        self.ambiente = ambiente
        self.base_url = self.URL_PRODUCAO if ambiente == "producao" else self.URL_HOMOLOGACAO

    def calcular_fgts_folha(self, trabalhadores: list[TrabalhadorFGTS], competencia: str) -> dict[str, Any]:
        """
        Calcula FGTS da folha de pagamento.

        Args:
            trabalhadores: Lista de trabalhadores
            competencia: Competência YYYY-MM

        Returns:
            Resumo do cálculo
        """
        total_remuneracao = Decimal("0")
        total_fgts = Decimal("0")

        for trab in trabalhadores:
            trab.valor_fgts = trab.remuneracao * self.ALIQUOTA_FGTS
            total_remuneracao += trab.remuneracao
            total_fgts += trab.valor_fgts

        logger.info(f"Calculado FGTS {competencia}: {len(trabalhadores)} trabalhadores, R$ {total_fgts}")

        return {
            "competencia": competencia,
            "quantidade_trabalhadores": len(trabalhadores),
            "total_remuneracao": str(total_remuneracao),
            "total_fgts": str(total_fgts),
            "trabalhadores": [
                {
                    "cpf": t.cpf,
                    "nome": t.nome,
                    "remuneracao": str(t.remuneracao),
                    "fgts": str(t.valor_fgts),
                }
                for t in trabalhadores
            ],
        }

    def importar_esocial(self, dados_esocial: dict[str, Any], competencia: str) -> list[TrabalhadorFGTS]:
        """
        Importa dados do eSocial para cálculo do FGTS.

        Args:
            dados_esocial: Dados dos eventos S-1200/S-1210
            competencia: Competência YYYY-MM

        Returns:
            Lista de trabalhadores com FGTS calculado
        """
        trabalhadores = []

        # Processa eventos de remuneração (S-1200)
        for evento in dados_esocial.get("eventos_s1200", []):
            trab = TrabalhadorFGTS(
                cpf=evento.get("cpf", ""),
                nome=evento.get("nome", ""),
                pis_pasep=evento.get("pis_pasep", ""),
                data_admissao=datetime.strptime(evento.get("data_admissao", "2020-01-01"), "%Y-%m-%d").date(),
                categoria=evento.get("categoria", "101"),
                remuneracao=Decimal(str(evento.get("remuneracao_total", 0))),
            )

            # Base de cálculo do FGTS
            base_fgts = Decimal(str(evento.get("base_fgts", trab.remuneracao)))
            trab.valor_fgts = base_fgts * self.ALIQUOTA_FGTS

            # 13º salário
            if evento.get("valor_13_salario"):
                base_13 = Decimal(str(evento.get("valor_13_salario")))
                trab.valor_fgts_13 = base_13 * self.ALIQUOTA_FGTS

            trabalhadores.append(trab)

        logger.info(f"Importados {len(trabalhadores)} trabalhadores do eSocial para FGTS")
        return trabalhadores

    def gerar_guia_mensal(
        self, trabalhadores: list[TrabalhadorFGTS], competencia: str, data_vencimento: date | None = None
    ) -> GRFGTS:
        """
        Gera guia de recolhimento mensal (GRFGTS).

        Args:
            trabalhadores: Lista de trabalhadores
            competencia: Competência YYYY-MM
            data_vencimento: Data de vencimento (default: dia 20 do mês seguinte)

        Returns:
            Guia gerada
        """
        if data_vencimento is None:
            ano, mes = map(int, competencia.split("-"))
            if mes == 12:
                ano += 1
                mes = 1
            else:
                mes += 1
            data_vencimento = date(ano, mes, 20)

        total_fgts = sum(t.valor_total for t in trabalhadores)

        guia = GRFGTS(
            numero=f"GRFGTS{competencia.replace('-', '')}{datetime.now().strftime('%H%M%S')}",
            competencia=competencia,
            data_geracao=datetime.now(),
            data_vencimento=data_vencimento,
            valor_principal=total_fgts,
        )

        # Gerar código PIX (simulado)
        guia.chave_pix = "fgts@caixa.gov.br"
        guia.codigo_pix = self._gerar_pix_copia_cola(guia)

        logger.info(f"Gerada GRFGTS {guia.numero}: R$ {guia.valor_total}")

        return guia

    def gerar_guia_rescisoria(self, rescisao: RecolhimentoRescisorio) -> GuiaRescisoria:
        """
        Gera guia de recolhimento rescisório (GRRF).

        Args:
            rescisao: Dados da rescisão

        Returns:
            Guia rescisória gerada
        """
        # Calcula multa rescisória
        rescisao.calcular_multa()

        # Calcula depósito do mês
        deposito_mes = rescisao.trabalhador.remuneracao * self.ALIQUOTA_FGTS

        # Calcula depósito do aviso prévio indenizado
        deposito_aviso = Decimal("0")
        if rescisao.aviso_previo == "indenizado":
            deposito_aviso = rescisao.trabalhador.remuneracao * self.ALIQUOTA_FGTS

        # Calcula depósito do 13º proporcional
        meses_trabalhados = rescisao.data_desligamento.month
        deposito_13 = (rescisao.trabalhador.remuneracao / 12 * meses_trabalhados) * self.ALIQUOTA_FGTS

        valor_total = deposito_mes + deposito_aviso + deposito_13 + rescisao.multa_40_percent

        # Vencimento: 10 dias após desligamento
        from datetime import timedelta

        data_venc = rescisao.data_desligamento + timedelta(days=10)

        guia = GuiaRescisoria(
            numero=f"GRRF{datetime.now().strftime('%Y%m%d%H%M%S')}",
            cpf_trabalhador=rescisao.trabalhador.cpf,
            nome_trabalhador=rescisao.trabalhador.nome,
            data_desligamento=rescisao.data_desligamento,
            valor_deposito_mes=deposito_mes,
            valor_deposito_aviso=deposito_aviso,
            valor_deposito_13=deposito_13,
            valor_multa_rescisoria=rescisao.multa_40_percent,
            valor_total=valor_total,
            data_vencimento=data_venc,
        )

        # Gerar código PIX
        guia.codigo_pix = self._gerar_pix_copia_cola_rescisorio(guia)

        logger.info(f"Gerada GRRF {guia.numero}: R$ {guia.valor_total}")

        return guia

    def consultar_debitos(
        self, competencia_inicio: str | None = None, competencia_fim: str | None = None
    ) -> list[DebitoFGTS]:
        """
        Consulta débitos de FGTS.

        Args:
            competencia_inicio: Competência inicial YYYY-MM
            competencia_fim: Competência final YYYY-MM

        Returns:
            Lista de débitos
        """
        # Na implementação real, consultaria o FGTS Digital via API
        logger.info(f"Consulta de débitos FGTS: {competencia_inicio} a {competencia_fim}")

        return []

    def consultar_extrato_trabalhador(self, cpf: str, pis_pasep: str) -> dict[str, Any]:
        """
        Consulta extrato do FGTS de um trabalhador.

        Args:
            cpf: CPF do trabalhador
            pis_pasep: Número do PIS/PASEP

        Returns:
            Extrato do FGTS
        """
        # Na implementação real, consultaria o FGTS Digital
        return {
            "cpf": cpf,
            "pis_pasep": pis_pasep,
            "saldo_total": "0.00",
            "mensagem": "Implementar consulta via FGTS Digital",
        }

    def simular_saque(
        self, cpf: str, modalidade: ModalidadeSaque, valor_solicitado: Decimal | None = None
    ) -> dict[str, Any]:
        """
        Simula saque do FGTS.

        Args:
            cpf: CPF do trabalhador
            modalidade: Modalidade de saque
            valor_solicitado: Valor solicitado (opcional)

        Returns:
            Simulação do saque
        """
        return {
            "cpf": cpf,
            "modalidade": modalidade.value,
            "valor_solicitado": str(valor_solicitado) if valor_solicitado else None,
            "status": "simulacao_pendente",
            "mensagem": "Implementar simulação via FGTS Digital",
        }

    def _gerar_pix_copia_cola(self, guia: GRFGTS) -> str:
        """
        Gera código PIX copia e cola para GRFGTS.

        Args:
            guia: Guia FGTS

        Returns:
            Código PIX
        """
        # Na implementação real, seria gerado pela Caixa
        return f"00020126580014br.gov.bcb.pix0136fgts@caixa.gov.br5204000053039865406{guia.valor_total:.2f}5802BR62070503***6304"

    def _gerar_pix_copia_cola_rescisorio(self, guia: GuiaRescisoria) -> str:
        """
        Gera código PIX copia e cola para GRRF.

        Args:
            guia: Guia rescisória

        Returns:
            Código PIX
        """
        return f"00020126580014br.gov.bcb.pix0136fgts@caixa.gov.br5204000053039865406{guia.valor_total:.2f}5802BR62070503***6304"

    def gerar_relatorio_mensal(self, trabalhadores: list[TrabalhadorFGTS], competencia: str) -> dict[str, Any]:
        """
        Gera relatório mensal de FGTS.

        Args:
            trabalhadores: Lista de trabalhadores
            competencia: Competência YYYY-MM

        Returns:
            Relatório detalhado
        """
        total_remuneracao = sum(t.remuneracao for t in trabalhadores)
        total_fgts = sum(t.valor_fgts for t in trabalhadores)
        total_fgts_13 = sum(t.valor_fgts_13 for t in trabalhadores)

        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "competencia": competencia,
            "data_geracao": datetime.now().isoformat(),
            "resumo": {
                "quantidade_trabalhadores": len(trabalhadores),
                "total_remuneracao": str(total_remuneracao),
                "total_fgts_mensal": str(total_fgts),
                "total_fgts_13": str(total_fgts_13),
                "total_geral": str(total_fgts + total_fgts_13),
            },
            "detalhamento": [
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
            ],
        }
