"""
SENTINEL Agent - Monitoramento de certidoes e documentos
==========================================================
Monitora validade de certidoes, documentos e certificados
necessarios para participacao em licitacoes.
"""

import logging
from datetime import date, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, Field

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class TipoDocumentoMonitorado(StrEnum):
    """Tipos de documentos monitorados pelo SENTINEL."""

    CND_FEDERAL = "cnd_federal"  # Certidao Negativa Debitos Federais (RFB/PGFN)
    CND_ESTADUAL = "cnd_estadual"  # Certidao Negativa Debitos Estaduais
    CND_MUNICIPAL = "cnd_municipal"  # Certidao Negativa Debitos Municipais (ISS)
    CRF_FGTS = "crf_fgts"  # Certificado Regularidade FGTS (Caixa)
    CNDT_TRABALHISTA = "cndt_trabalhista"  # Certidao Negativa Debitos Trabalhistas (TST)
    SICAF = "sicaf"  # Sistema Cadastramento Unificado Fornecedores
    AUTORIZACAO_PF = "autorizacao_pf"  # Autorizacao Policia Federal (vigilancia)
    ALVARA_FUNCIONAMENTO = "alvara_funcionamento"
    CERTIFICADO_DIGITAL = "certificado_digital"  # e-CNPJ / A1
    ISO_9001 = "iso_9001"
    ISO_14001 = "iso_14001"
    SEGURO_RESPONSABILIDADE = "seguro_responsabilidade"
    REGISTRO_CREA = "registro_crea"
    BALANCO_PATRIMONIAL = "balanco_patrimonial"


class StatusDocumento(StrEnum):
    """Status de um documento monitorado."""

    VALIDO = "valido"
    VENCENDO = "vencendo"  # Proximo do vencimento (dentro do alerta)
    VENCIDO = "vencido"
    NAO_POSSUI = "nao_possui"
    RENOVANDO = "renovando"  # Em processo de renovacao
    ERRO_CONSULTA = "erro_consulta"


class NivelAlerta(StrEnum):
    """Nivel de alerta para documentos."""

    OK = "ok"
    ATENCAO = "atencao"  # Vence em 30-60 dias
    URGENTE = "urgente"  # Vence em 15-30 dias
    CRITICO = "critico"  # Vence em < 15 dias ou ja vencido


class DocumentoMonitorado(BaseModel):
    """Documento individual monitorado."""

    tipo: TipoDocumentoMonitorado
    nome_exibicao: str
    cnpj_empresa: str = "35.710.481/0001-03"

    # Validade
    data_emissao: date | None = None
    data_validade: date | None = None
    validade_padrao_dias: int = 180  # Validade default se nao informada

    # Status
    status: StatusDocumento = StatusDocumento.NAO_POSSUI
    nivel_alerta: NivelAlerta = NivelAlerta.OK
    dias_para_vencimento: int | None = None

    # Consulta
    url_consulta: str | None = None  # URL para emissao/consulta online
    ultima_consulta: datetime | None = None
    proximo_check: datetime | None = None
    erro_consulta: str | None = None

    # Arquivo
    arquivo_path: str | None = None
    arquivo_hash: str | None = None

    # Observacoes
    observacoes: str | None = None


class SentinelResponse(BaseModel):
    """Resultado do monitoramento de documentos."""

    # Resumo
    total_documentos: int = 0
    validos: int = 0
    vencendo: int = 0
    vencidos: int = 0
    nao_possui: int = 0

    # Alertas
    alertas_criticos: list[str] = Field(default_factory=list)
    alertas_urgentes: list[str] = Field(default_factory=list)
    alertas_atencao: list[str] = Field(default_factory=list)

    # Documentos detalhados
    documentos: list[DocumentoMonitorado] = Field(default_factory=list)

    # Aptidao para licitar
    apto_licitar: bool = False
    motivo_inaptidao: list[str] = Field(default_factory=list)

    # Metadados
    verificado_em: datetime | None = None
    proxima_verificacao: datetime | None = None


# ──────────────────────────────────────────────
# Registro de documentos padrao
# ──────────────────────────────────────────────

DOCUMENTOS_PADRAO: list[dict] = [
    {
        "tipo": TipoDocumentoMonitorado.CND_FEDERAL,
        "nome_exibicao": "CND Federal (RFB/PGFN)",
        "validade_padrao_dias": 180,
        "url_consulta": "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CND_ESTADUAL,
        "nome_exibicao": "CND Estadual (SEFAZ-AM)",
        "validade_padrao_dias": 90,
        "url_consulta": "https://online.sefaz.am.gov.br/certidao",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CND_MUNICIPAL,
        "nome_exibicao": "CND Municipal (ISS Manaus)",
        "validade_padrao_dias": 90,
        "url_consulta": "https://semef.manaus.am.gov.br",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CRF_FGTS,
        "nome_exibicao": "CRF FGTS (Caixa)",
        "validade_padrao_dias": 30,
        "url_consulta": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CNDT_TRABALHISTA,
        "nome_exibicao": "CNDT Trabalhista (TST)",
        "validade_padrao_dias": 180,
        "url_consulta": "https://www.tst.jus.br/certidao1",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.SICAF,
        "nome_exibicao": "Cadastro SICAF",
        "validade_padrao_dias": 365,
        "url_consulta": "https://www.gov.br/compras/pt-br/acesso-ao-sicaf",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.AUTORIZACAO_PF,
        "nome_exibicao": "Autorizacao Policia Federal (Vigilancia)",
        "validade_padrao_dias": 365,
        "url_consulta": "https://www.gov.br/pf/pt-br/assuntos/seguranca-privada",
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.ALVARA_FUNCIONAMENTO,
        "nome_exibicao": "Alvara de Funcionamento",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.CERTIFICADO_DIGITAL,
        "nome_exibicao": "Certificado Digital e-CNPJ (A1)",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
    {
        "tipo": TipoDocumentoMonitorado.SEGURO_RESPONSABILIDADE,
        "nome_exibicao": "Seguro de Responsabilidade Civil",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": False,
    },
    {
        "tipo": TipoDocumentoMonitorado.BALANCO_PATRIMONIAL,
        "nome_exibicao": "Balanco Patrimonial (ultimo exercicio)",
        "validade_padrao_dias": 365,
        "url_consulta": None,
        "obrigatorio_licitar": True,
    },
]


# ──────────────────────────────────────────────
# SENTINEL Agent
# ──────────────────────────────────────────────


class SentinelAgent(BaseAgent):
    """
    Agente SENTINEL - Monitoramento de certidoes e documentos.

    Responsabilidades:
    - Verificar validade de todas as certidoes obrigatorias
    - Alertar sobre documentos vencendo/vencidos
    - Classificar nivel de alerta (OK, atencao, urgente, critico)
    - Determinar aptidao para licitar
    - Agendar verificacoes periodicas

    Em producao, integraria com:
    - APIs dos orgaos emissores para consulta automatica
    - Storage para arquivos PDF das certidoes
    - Notificacoes (email/whatsapp) para alertas
    """

    AGENT_NAME = "sentinel"
    AGENT_DESCRIPTION = "Monitora validade de certidoes e documentos para licitacoes"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    # Limiares de alerta (dias)
    ALERTA_ATENCAO_DIAS = 60
    ALERTA_URGENTE_DIAS = 30
    ALERTA_CRITICO_DIAS = 15

    def __init__(
        self,
        config: AgentConfig | None = None,
        documentos_cadastrados: list[DocumentoMonitorado] | None = None,
    ):
        super().__init__(config)
        self._documentos = documentos_cadastrados or []

    async def execute(
        self,
        documentos: list[dict] | None = None,
        cnpj: str = "35.710.481/0001-03",
        verificar_online: bool = False,
        **kwargs,
    ) -> dict:
        """
        Verifica status de todos os documentos monitorados.

        Args:
            documentos: Lista de documentos com datas de validade (override).
                        Cada dict: {"tipo": str, "data_emissao": str, "data_validade": str}
            cnpj: CNPJ da empresa.
            verificar_online: Se True, tenta consultar APIs dos orgaos (futuro).

        Returns:
            SentinelResponse como dict.
        """
        hoje = date.today()
        docs_monitorados: list[DocumentoMonitorado] = []

        # Usar documentos passados ou defaults
        if documentos:
            docs_monitorados = self._parse_documentos_input(documentos, cnpj)
        elif self._documentos:
            docs_monitorados = self._documentos
        else:
            docs_monitorados = self._criar_documentos_padrao(cnpj)

        # Atualizar status de cada documento
        for doc in docs_monitorados:
            self._atualizar_status(doc, hoje)

        # Verificar online (futuro)
        if verificar_online:
            await self._verificar_online(docs_monitorados)

        # Construir resposta
        response = self._construir_resposta(docs_monitorados, hoje)

        self.logger.info(
            f"SENTINEL: {response.total_documentos} docs verificados | "
            f"Validos: {response.validos} | Vencendo: {response.vencendo} | "
            f"Vencidos: {response.vencidos} | Apto: {response.apto_licitar}"
        )

        return response.model_dump(mode="json")

    def _parse_documentos_input(self, documentos: list[dict], cnpj: str) -> list[DocumentoMonitorado]:
        """Converte input de documentos para DocumentoMonitorado."""
        resultado = []

        # Mapa de info padrao por tipo
        info_padrao = {d["tipo"].value: d for d in DOCUMENTOS_PADRAO}

        for doc_input in documentos:
            tipo_str = doc_input.get("tipo", "")
            try:
                tipo = TipoDocumentoMonitorado(tipo_str)
            except ValueError:
                self.logger.warning(f"Tipo de documento desconhecido: {tipo_str}")
                continue

            padrao = info_padrao.get(tipo_str, {})

            data_emissao = None
            data_validade = None

            if doc_input.get("data_emissao"):
                data_emissao = date.fromisoformat(doc_input["data_emissao"])
            if doc_input.get("data_validade"):
                data_validade = date.fromisoformat(doc_input["data_validade"])

            doc = DocumentoMonitorado(
                tipo=tipo,
                nome_exibicao=padrao.get("nome_exibicao", tipo_str),
                cnpj_empresa=cnpj,
                data_emissao=data_emissao,
                data_validade=data_validade,
                validade_padrao_dias=padrao.get("validade_padrao_dias", 180),
                url_consulta=padrao.get("url_consulta"),
                arquivo_path=doc_input.get("arquivo_path"),
            )
            resultado.append(doc)

        return resultado

    def _criar_documentos_padrao(self, cnpj: str) -> list[DocumentoMonitorado]:
        """Cria lista de documentos padrao sem datas (status: nao_possui)."""
        resultado = []
        for padrao in DOCUMENTOS_PADRAO:
            doc = DocumentoMonitorado(
                tipo=padrao["tipo"],
                nome_exibicao=padrao["nome_exibicao"],
                cnpj_empresa=cnpj,
                validade_padrao_dias=padrao["validade_padrao_dias"],
                url_consulta=padrao.get("url_consulta"),
                status=StatusDocumento.NAO_POSSUI,
            )
            resultado.append(doc)
        return resultado

    def _atualizar_status(self, doc: DocumentoMonitorado, hoje: date) -> None:
        """Atualiza status e nivel de alerta de um documento."""
        if doc.data_validade is None:
            if doc.data_emissao is not None:
                # Calcular validade estimada
                doc.data_validade = doc.data_emissao + timedelta(days=doc.validade_padrao_dias)
            else:
                doc.status = StatusDocumento.NAO_POSSUI
                doc.nivel_alerta = NivelAlerta.CRITICO
                doc.dias_para_vencimento = None
                return

        dias_restantes = (doc.data_validade - hoje).days
        doc.dias_para_vencimento = dias_restantes
        doc.ultima_consulta = datetime.utcnow()

        if dias_restantes < 0:
            doc.status = StatusDocumento.VENCIDO
            doc.nivel_alerta = NivelAlerta.CRITICO
        elif dias_restantes <= self.ALERTA_CRITICO_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.CRITICO
        elif dias_restantes <= self.ALERTA_URGENTE_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.URGENTE
        elif dias_restantes <= self.ALERTA_ATENCAO_DIAS:
            doc.status = StatusDocumento.VENCENDO
            doc.nivel_alerta = NivelAlerta.ATENCAO
        else:
            doc.status = StatusDocumento.VALIDO
            doc.nivel_alerta = NivelAlerta.OK

        # Proximo check: documentos criticos verificar diariamente,
        # urgentes a cada 3 dias, atencao semanalmente, ok mensalmente
        intervalo = {
            NivelAlerta.CRITICO: 1,
            NivelAlerta.URGENTE: 3,
            NivelAlerta.ATENCAO: 7,
            NivelAlerta.OK: 30,
        }[doc.nivel_alerta]
        doc.proximo_check = datetime.utcnow() + timedelta(days=intervalo)

    async def _verificar_online(self, documentos: list[DocumentoMonitorado]) -> None:
        """
        Verifica documentos online nos portais dos orgaos emissores.

        TODO: Implementar integracao real com APIs:
        - RFB/PGFN para CND Federal
        - Caixa para CRF FGTS
        - TST para CNDT
        - SEFAZ-AM para CND Estadual
        - SEMEF Manaus para CND Municipal
        """
        for doc in documentos:
            if doc.url_consulta:
                self.logger.info(
                    f"[SENTINEL] Verificacao online para {doc.nome_exibicao}: TODO - integrar com {doc.url_consulta}"
                )
                # Em producao: httpx.get(doc.url_consulta) + parse resultado

    def _construir_resposta(self, documentos: list[DocumentoMonitorado], hoje: date) -> SentinelResponse:
        """Constroi resposta consolidada."""
        validos = sum(1 for d in documentos if d.status == StatusDocumento.VALIDO)
        vencendo = sum(1 for d in documentos if d.status == StatusDocumento.VENCENDO)
        vencidos = sum(1 for d in documentos if d.status == StatusDocumento.VENCIDO)
        nao_possui = sum(1 for d in documentos if d.status == StatusDocumento.NAO_POSSUI)

        alertas_criticos = []
        alertas_urgentes = []
        alertas_atencao = []

        # Mapa de obrigatoriedade
        obrigatorio_map = {d["tipo"].value: d.get("obrigatorio_licitar", True) for d in DOCUMENTOS_PADRAO}

        motivos_inaptidao = []

        for doc in documentos:
            obrigatorio = obrigatorio_map.get(doc.tipo.value, True)

            if doc.nivel_alerta == NivelAlerta.CRITICO:
                msg = f"{doc.nome_exibicao}: "
                if doc.status == StatusDocumento.VENCIDO:
                    msg += f"VENCIDO ha {abs(doc.dias_para_vencimento or 0)} dias"
                elif doc.status == StatusDocumento.VENCENDO:
                    msg += f"vence em {doc.dias_para_vencimento} dias"
                elif doc.status == StatusDocumento.NAO_POSSUI:
                    msg += "NAO CADASTRADO"
                alertas_criticos.append(msg)
                if obrigatorio:
                    motivos_inaptidao.append(msg)

            elif doc.nivel_alerta == NivelAlerta.URGENTE:
                alertas_urgentes.append(f"{doc.nome_exibicao}: vence em {doc.dias_para_vencimento} dias")
                if obrigatorio and doc.status == StatusDocumento.VENCENDO:
                    # Urgente mas ainda valido
                    pass

            elif doc.nivel_alerta == NivelAlerta.ATENCAO:
                alertas_atencao.append(f"{doc.nome_exibicao}: vence em {doc.dias_para_vencimento} dias")

        # Apto para licitar = sem alertas criticos em documentos obrigatorios
        apto = len(motivos_inaptidao) == 0

        # Proxima verificacao = menor proximo_check entre documentos
        proxima = None
        for doc in documentos:
            if doc.proximo_check:
                if proxima is None or doc.proximo_check < proxima:
                    proxima = doc.proximo_check

        return SentinelResponse(
            total_documentos=len(documentos),
            validos=validos,
            vencendo=vencendo,
            vencidos=vencidos,
            nao_possui=nao_possui,
            alertas_criticos=alertas_criticos,
            alertas_urgentes=alertas_urgentes,
            alertas_atencao=alertas_atencao,
            documentos=documentos,
            apto_licitar=apto,
            motivo_inaptidao=motivos_inaptidao,
            verificado_em=datetime.utcnow(),
            proxima_verificacao=proxima,
        )
