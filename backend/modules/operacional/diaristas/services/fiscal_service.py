"""
Serviço Fiscal para Diaristas.

Fornece funcionalidades para:
- Cálculo de retenções (INSS, ISS, IRRF)
- Geração de RPA
- Integração com e-Social
- Relatórios fiscais
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import logging

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from modules.operacional.diaristas.models.documento_fiscal import (
    DocumentoFiscal,
    RetencaoFiscal,
    EventoESocial,
    TabelaINSS,
    TabelaIRRF,
    TipoDocumentoFiscal,
    StatusDocumentoFiscal,
    TipoRetencao,
    TipoEventoESocial,
    StatusEventoESocial,
)
from modules.operacional.diaristas.models import Diarist, DiaristPayment

logger = logging.getLogger(__name__)


# =============================================================================
# TABELAS PADRÃO (quando não há registro no banco)
# =============================================================================

TABELA_INSS_PADRAO_2026 = {
    "vigencia": "2026-01",
    "faixas": [
        {"ate": Decimal("1518.00"), "aliquota": Decimal("7.5")},
        {"ate": Decimal("2793.88"), "aliquota": Decimal("9.0")},
        {"ate": Decimal("4190.83"), "aliquota": Decimal("12.0")},
        {"ate": Decimal("8157.41"), "aliquota": Decimal("14.0")},
    ],
    "teto": Decimal("8157.41"),
    "aliquota_autonomo": Decimal("11.00"),  # Alíquota para contribuinte individual
}

TABELA_IRRF_PADRAO_2026 = {
    "vigencia": "2026-01",
    "faixas": [
        {"ate": Decimal("2428.80"), "aliquota": Decimal("0"), "deducao": Decimal("0")},
        {"ate": Decimal("2826.65"), "aliquota": Decimal("7.5"), "deducao": Decimal("182.16")},
        {"ate": Decimal("3751.05"), "aliquota": Decimal("15.0"), "deducao": Decimal("393.94")},
        {"ate": Decimal("4664.68"), "aliquota": Decimal("22.5"), "deducao": Decimal("675.18")},
        {"acima_de": Decimal("4664.68"), "aliquota": Decimal("27.5"), "deducao": Decimal("908.42")},
    ],
    "deducao_dependente": Decimal("189.59"),
}

# ISS varia por município, usando alíquota média
ALIQUOTA_ISS_PADRAO = Decimal("5.00")  # 5%


class FiscalService:
    """Serviço de cálculos e documentos fiscais para diaristas."""

    def __init__(self, db: Session):
        self.db = db
        self._tabela_inss = None
        self._tabela_irrf = None

    # =========================================================================
    # CÁLCULOS DE RETENÇÕES
    # =========================================================================

    def calcular_inss(
        self,
        valor_bruto: Decimal,
        data_referencia: Optional[date] = None,
    ) -> Dict[str, Decimal]:
        """
        Calcula INSS para contribuinte individual (autônomo).

        Para autônomos, a alíquota é de 11% sobre o valor até o teto.
        Pode ser 20% se quiser contribuir para aposentadoria por tempo de contribuição.

        Args:
            valor_bruto: Valor bruto do serviço
            data_referencia: Data de referência para tabela

        Returns:
            Dict com base_calculo, aliquota e valor
        """
        tabela = self._get_tabela_inss(data_referencia)

        # Base é o menor entre valor bruto e teto
        teto = tabela.get("teto", TABELA_INSS_PADRAO_2026["teto"])
        base_calculo = min(valor_bruto, teto)

        # Alíquota padrão para autônomo
        aliquota = tabela.get("aliquota_autonomo", Decimal("11.00"))

        # Cálculo
        valor_inss = (base_calculo * aliquota / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "base_calculo": base_calculo,
            "aliquota": aliquota,
            "valor": valor_inss,
            "teto_aplicado": base_calculo < valor_bruto,
        }

    def calcular_irrf(
        self,
        valor_bruto: Decimal,
        inss_retido: Decimal = Decimal("0"),
        dependentes: int = 0,
        data_referencia: Optional[date] = None,
    ) -> Dict[str, Decimal]:
        """
        Calcula IRRF sobre rendimentos de trabalho autônomo.

        A base é: Valor Bruto - INSS - (Dependentes * Dedução)

        Args:
            valor_bruto: Valor bruto do serviço
            inss_retido: Valor do INSS retido
            dependentes: Número de dependentes
            data_referencia: Data de referência para tabela

        Returns:
            Dict com base_calculo, aliquota, deducao e valor
        """
        tabela = self._get_tabela_irrf(data_referencia)

        # Dedução por dependente
        deducao_dependente = tabela.get(
            "deducao_dependente",
            TABELA_IRRF_PADRAO_2026["deducao_dependente"]
        )

        # Base de cálculo
        base_calculo = valor_bruto - inss_retido - (dependentes * deducao_dependente)
        base_calculo = max(base_calculo, Decimal("0"))

        # Encontrar faixa
        faixas = tabela.get("faixas", TABELA_IRRF_PADRAO_2026["faixas"])
        aliquota = Decimal("0")
        deducao = Decimal("0")

        for faixa in faixas:
            if "ate" in faixa and base_calculo <= faixa["ate"]:
                aliquota = faixa["aliquota"]
                deducao = faixa["deducao"]
                break
            elif "acima_de" in faixa and base_calculo > faixa["acima_de"]:
                aliquota = faixa["aliquota"]
                deducao = faixa["deducao"]

        # Cálculo
        if aliquota > 0:
            valor_irrf = ((base_calculo * aliquota / 100) - deducao).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            valor_irrf = max(valor_irrf, Decimal("0"))
        else:
            valor_irrf = Decimal("0")

        return {
            "base_calculo": base_calculo,
            "aliquota": aliquota,
            "deducao_tabela": deducao,
            "valor": valor_irrf,
            "dependentes": dependentes,
            "deducao_dependentes": dependentes * deducao_dependente,
        }

    def calcular_iss(
        self,
        valor_bruto: Decimal,
        aliquota: Optional[Decimal] = None,
        municipio_codigo: Optional[str] = None,
    ) -> Dict[str, Decimal]:
        """
        Calcula ISS sobre serviços prestados.

        A alíquota varia de 2% a 5% dependendo do município e serviço.

        Args:
            valor_bruto: Valor bruto do serviço
            aliquota: Alíquota do ISS (se não informada, usa padrão)
            municipio_codigo: Código IBGE do município

        Returns:
            Dict com base_calculo, aliquota e valor
        """
        # TODO: Implementar consulta de alíquota por município
        aliquota_iss = aliquota or ALIQUOTA_ISS_PADRAO

        valor_iss = (valor_bruto * aliquota_iss / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "base_calculo": valor_bruto,
            "aliquota": aliquota_iss,
            "valor": valor_iss,
            "municipio": municipio_codigo,
        }

    def calcular_todas_retencoes(
        self,
        valor_bruto: Decimal,
        dependentes: int = 0,
        aliquota_iss: Optional[Decimal] = None,
        data_referencia: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Calcula todas as retenções fiscais de uma vez.

        Args:
            valor_bruto: Valor bruto do serviço
            dependentes: Número de dependentes (para IRRF)
            aliquota_iss: Alíquota do ISS
            data_referencia: Data de referência para tabelas

        Returns:
            Dict com todos os cálculos e valor líquido
        """
        # INSS primeiro (deduz do IRRF)
        inss = self.calcular_inss(valor_bruto, data_referencia)

        # IRRF (considera INSS)
        irrf = self.calcular_irrf(
            valor_bruto, inss["valor"], dependentes, data_referencia
        )

        # ISS
        iss = self.calcular_iss(valor_bruto, aliquota_iss)

        # Total de retenções
        total_retencoes = inss["valor"] + irrf["valor"] + iss["valor"]

        # Valor líquido
        valor_liquido = valor_bruto - total_retencoes

        return {
            "valor_bruto": valor_bruto,
            "inss": inss,
            "irrf": irrf,
            "iss": iss,
            "total_retencoes": total_retencoes,
            "valor_liquido": valor_liquido,
        }

    # =========================================================================
    # GERAÇÃO DE DOCUMENTOS
    # =========================================================================

    def gerar_rpa(
        self,
        diarist_id: UUID,
        payment_id: Optional[UUID] = None,
        valor_bruto: Optional[Decimal] = None,
        competencia: Optional[str] = None,
        descricao_servico: str = "Prestação de serviços de limpeza e conservação",
        codigo_servico: str = "7.10",  # Código LC 116/2003 para limpeza
        dependentes: int = 0,
        aliquota_iss: Optional[Decimal] = None,
        tomador_cnpj: Optional[str] = None,
        tomador_razao_social: Optional[str] = None,
    ) -> DocumentoFiscal:
        """
        Gera RPA (Recibo de Pagamento Autônomo) para um diarista.

        Args:
            diarist_id: ID do diarista
            payment_id: ID do pagamento (opcional)
            valor_bruto: Valor bruto do serviço
            competencia: Mês/ano de competência (YYYY-MM)
            descricao_servico: Descrição do serviço
            codigo_servico: Código do serviço (LC 116/2003)
            dependentes: Número de dependentes
            aliquota_iss: Alíquota do ISS
            tomador_cnpj: CNPJ do tomador
            tomador_razao_social: Razão social do tomador

        Returns:
            DocumentoFiscal criado
        """
        # Buscar diarista
        diarista = self.db.query(Diarist).filter(Diarist.id == diarist_id).first()
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} não encontrado")

        # Se payment_id, buscar valor do pagamento
        payment = None
        if payment_id:
            payment = self.db.query(DiaristPayment).filter(
                DiaristPayment.id == payment_id
            ).first()
            if payment and not valor_bruto:
                valor_bruto = payment.gross_amount

        if not valor_bruto:
            raise ValueError("Valor bruto é obrigatório")

        # Competência
        if not competencia:
            competencia = date.today().strftime("%Y-%m")

        # Calcular retenções
        retencoes = self.calcular_todas_retencoes(
            valor_bruto=valor_bruto,
            dependentes=dependentes,
            aliquota_iss=aliquota_iss,
        )

        # Gerar número do RPA
        numero = self._gerar_numero_documento("RPA")

        # Criar documento
        documento = DocumentoFiscal(
            numero=numero,
            tipo=TipoDocumentoFiscal.RPA,
            status=StatusDocumentoFiscal.EMITIDO,
            diarist_id=diarist_id,
            payment_id=payment_id,
            competencia=competencia,
            data_emissao=date.today(),

            # Valores
            valor_bruto=valor_bruto,
            valor_inss=retencoes["inss"]["valor"],
            valor_iss=retencoes["iss"]["valor"],
            valor_irrf=retencoes["irrf"]["valor"],
            valor_liquido=retencoes["valor_liquido"],

            # Prestador
            prestador_cpf=diarista.cpf,
            prestador_nome=diarista.full_name,
            prestador_endereco=diarista.address if hasattr(diarista, 'address') else None,
            prestador_municipio=diarista.city if hasattr(diarista, 'city') else None,
            prestador_uf=diarista.state if hasattr(diarista, 'state') else None,
            prestador_pis=diarista.pis if hasattr(diarista, 'pis') else None,

            # Tomador
            tomador_cnpj=tomador_cnpj or "00.000.000/0001-00",  # TODO: Buscar da empresa
            tomador_razao_social=tomador_razao_social or "Conecta PRO Ltda",

            # Serviço
            descricao_servico=descricao_servico,
            codigo_servico=codigo_servico,

            # Bases de cálculo
            base_calculo_inss=retencoes["inss"]["base_calculo"],
            aliquota_inss=retencoes["inss"]["aliquota"],
            base_calculo_iss=retencoes["iss"]["base_calculo"],
            aliquota_iss=retencoes["iss"]["aliquota"],
            base_calculo_irrf=retencoes["irrf"]["base_calculo"],
            aliquota_irrf=retencoes["irrf"]["aliquota"],
        )

        self.db.add(documento)

        # Criar retenções detalhadas
        if retencoes["inss"]["valor"] > 0:
            retencao_inss = RetencaoFiscal(
                documento_id=documento.id,
                tipo=TipoRetencao.INSS,
                base_calculo=retencoes["inss"]["base_calculo"],
                aliquota=retencoes["inss"]["aliquota"],
                valor=retencoes["inss"]["valor"],
                fundamentacao_legal="Art. 30, I, Lei 8.212/91",
                codigo_receita="1162",
            )
            self.db.add(retencao_inss)

        if retencoes["iss"]["valor"] > 0:
            retencao_iss = RetencaoFiscal(
                documento_id=documento.id,
                tipo=TipoRetencao.ISS,
                base_calculo=retencoes["iss"]["base_calculo"],
                aliquota=retencoes["iss"]["aliquota"],
                valor=retencoes["iss"]["valor"],
                fundamentacao_legal="LC 116/2003",
            )
            self.db.add(retencao_iss)

        if retencoes["irrf"]["valor"] > 0:
            retencao_irrf = RetencaoFiscal(
                documento_id=documento.id,
                tipo=TipoRetencao.IRRF,
                base_calculo=retencoes["irrf"]["base_calculo"],
                aliquota=retencoes["irrf"]["aliquota"],
                valor=retencoes["irrf"]["valor"],
                fundamentacao_legal="Art. 7º, Lei 7.713/88",
                codigo_receita="0588",
            )
            self.db.add(retencao_irrf)

        self.db.commit()
        self.db.refresh(documento)

        logger.info(f"RPA {numero} gerado para diarista {diarist_id}")

        return documento

    def _gerar_numero_documento(self, prefixo: str = "RPA") -> str:
        """Gera número sequencial para documento."""
        ano = date.today().year
        # Buscar último número do ano
        ultimo = self.db.query(func.max(DocumentoFiscal.numero)).filter(
            DocumentoFiscal.numero.like(f"{prefixo}-{ano}-%")
        ).scalar()

        if ultimo:
            seq = int(ultimo.split("-")[-1]) + 1
        else:
            seq = 1

        return f"{prefixo}-{ano}-{seq:06d}"

    # =========================================================================
    # E-SOCIAL
    # =========================================================================

    def criar_evento_s2300(
        self,
        diarist_id: UUID,
        data_inicio: date,
    ) -> EventoESocial:
        """
        Cria evento S-2300 (Trabalhador Sem Vínculo - Início).

        Este evento deve ser enviado quando um autônomo é contratado.

        Args:
            diarist_id: ID do diarista
            data_inicio: Data de início da prestação de serviço

        Returns:
            EventoESocial criado
        """
        diarista = self.db.query(Diarist).filter(Diarist.id == diarist_id).first()
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} não encontrado")

        competencia = data_inicio.strftime("%Y-%m")

        # Dados do evento
        dados_evento = {
            "cpfTrab": diarista.cpf,
            "nmTrab": diarista.full_name,
            "dtNascto": diarista.birth_date.isoformat() if hasattr(diarista, 'birth_date') and diarista.birth_date else None,
            "sexo": "M" if diarista.gender == "male" else "F" if hasattr(diarista, 'gender') else "M",
            "cadIni": {
                "codCateg": "701",  # Contribuinte individual - Autônomo
                "dtInicio": data_inicio.isoformat(),
            },
            "infoComplementares": {
                "infoTrabAutonomo": {
                    "indAutonomo": "S",
                },
            },
        }

        evento = EventoESocial(
            tipo_evento=TipoEventoESocial.S2300,
            status=StatusEventoESocial.PENDENTE,
            diarist_id=diarist_id,
            competencia=competencia,
            dados_evento=dados_evento,
        )

        self.db.add(evento)
        self.db.commit()
        self.db.refresh(evento)

        logger.info(f"Evento S-2300 criado para diarista {diarist_id}")

        return evento

    def criar_evento_s1200(
        self,
        diarist_id: UUID,
        competencia: str,
        valor_remuneracao: Decimal,
    ) -> EventoESocial:
        """
        Cria evento S-1200 (Remuneração de Trabalhador vinculado ao RGPS).

        Este evento informa a remuneração mensal do autônomo.

        Args:
            diarist_id: ID do diarista
            competencia: Mês/ano (YYYY-MM)
            valor_remuneracao: Valor da remuneração

        Returns:
            EventoESocial criado
        """
        diarista = self.db.query(Diarist).filter(Diarist.id == diarist_id).first()
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} não encontrado")

        # Calcular INSS
        inss = self.calcular_inss(valor_remuneracao)

        dados_evento = {
            "cpfTrab": diarista.cpf,
            "perApur": competencia,
            "dmDev": [{
                "ideDmDev": str(uuid4())[:8],
                "codCateg": "701",
                "infoPerApur": {
                    "ideEstabLot": [{
                        "tpInsc": "1",  # CNPJ
                        "nrInsc": "00000000000100",  # TODO: Buscar CNPJ da empresa
                        "detVerbas": [{
                            "codRubr": "1000",
                            "ideTabRubr": "001",
                            "qtdRubr": 1,
                            "fatorRubr": 1,
                            "vrUnit": float(valor_remuneracao),
                            "vrRubr": float(valor_remuneracao),
                        }],
                        "infoAgNocivo": {
                            "grauExp": "1",
                        },
                    }],
                },
            }],
            "infoComplCont": {
                "codCBO": "5142-05",  # Auxiliar de serviços de limpeza
            },
        }

        evento = EventoESocial(
            tipo_evento=TipoEventoESocial.S1200,
            status=StatusEventoESocial.PENDENTE,
            diarist_id=diarist_id,
            competencia=competencia,
            dados_evento=dados_evento,
        )

        self.db.add(evento)
        self.db.commit()
        self.db.refresh(evento)

        logger.info(f"Evento S-1200 criado para diarista {diarist_id}, competência {competencia}")

        return evento

    # =========================================================================
    # CONSULTAS E RELATÓRIOS
    # =========================================================================

    def listar_documentos(
        self,
        diarist_id: Optional[UUID] = None,
        tipo: Optional[TipoDocumentoFiscal] = None,
        competencia: Optional[str] = None,
        status: Optional[StatusDocumentoFiscal] = None,
        limit: int = 50,
    ) -> List[DocumentoFiscal]:
        """Lista documentos fiscais com filtros."""
        query = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.is_active == True)

        if diarist_id:
            query = query.filter(DocumentoFiscal.diarist_id == diarist_id)
        if tipo:
            query = query.filter(DocumentoFiscal.tipo == tipo)
        if competencia:
            query = query.filter(DocumentoFiscal.competencia == competencia)
        if status:
            query = query.filter(DocumentoFiscal.status == status)

        return query.order_by(DocumentoFiscal.data_emissao.desc()).limit(limit).all()

    def relatorio_retencoes_periodo(
        self,
        data_inicio: date,
        data_fim: date,
        diarist_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Gera relatório de retenções por período.

        Args:
            data_inicio: Data inicial
            data_fim: Data final
            diarist_id: Filtrar por diarista

        Returns:
            Dict com totais de retenções
        """
        query = self.db.query(
            func.sum(DocumentoFiscal.valor_bruto).label("total_bruto"),
            func.sum(DocumentoFiscal.valor_inss).label("total_inss"),
            func.sum(DocumentoFiscal.valor_iss).label("total_iss"),
            func.sum(DocumentoFiscal.valor_irrf).label("total_irrf"),
            func.sum(DocumentoFiscal.valor_liquido).label("total_liquido"),
            func.count(DocumentoFiscal.id).label("qtd_documentos"),
        ).filter(
            DocumentoFiscal.is_active == True,
            DocumentoFiscal.status == StatusDocumentoFiscal.EMITIDO,
            DocumentoFiscal.data_emissao >= data_inicio,
            DocumentoFiscal.data_emissao <= data_fim,
        )

        if diarist_id:
            query = query.filter(DocumentoFiscal.diarist_id == diarist_id)

        resultado = query.first()

        return {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat(),
            },
            "totais": {
                "bruto": float(resultado.total_bruto or 0),
                "inss": float(resultado.total_inss or 0),
                "iss": float(resultado.total_iss or 0),
                "irrf": float(resultado.total_irrf or 0),
                "total_retencoes": float(
                    (resultado.total_inss or 0) +
                    (resultado.total_iss or 0) +
                    (resultado.total_irrf or 0)
                ),
                "liquido": float(resultado.total_liquido or 0),
            },
            "documentos": int(resultado.qtd_documentos or 0),
        }

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_tabela_inss(self, data_referencia: Optional[date] = None) -> Dict:
        """Obtém tabela INSS vigente."""
        data = data_referencia or date.today()

        tabela = self.db.query(TabelaINSS).filter(
            TabelaINSS.is_active == True,
            TabelaINSS.vigencia_inicio <= data,
            or_(
                TabelaINSS.vigencia_fim.is_(None),
                TabelaINSS.vigencia_fim >= data
            )
        ).first()

        if tabela:
            return {
                "faixas": tabela.faixas,
                "teto": tabela.teto_contribuicao,
                "aliquota_autonomo": tabela.aliquota_autonomo,
            }

        return TABELA_INSS_PADRAO_2026

    def _get_tabela_irrf(self, data_referencia: Optional[date] = None) -> Dict:
        """Obtém tabela IRRF vigente."""
        data = data_referencia or date.today()

        tabela = self.db.query(TabelaIRRF).filter(
            TabelaIRRF.is_active == True,
            TabelaIRRF.vigencia_inicio <= data,
            or_(
                TabelaIRRF.vigencia_fim.is_(None),
                TabelaIRRF.vigencia_fim >= data
            )
        ).first()

        if tabela:
            return {
                "faixas": tabela.faixas,
                "deducao_dependente": tabela.deducao_dependente,
            }

        return TABELA_IRRF_PADRAO_2026


# Singleton
def get_fiscal_service(db: Session) -> FiscalService:
    """Factory function para obter instância do serviço."""
    return FiscalService(db)
