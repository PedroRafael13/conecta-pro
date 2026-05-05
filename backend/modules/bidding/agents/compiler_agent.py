"""
COMPILER Agent - Geracao de documentos de proposta
====================================================
Gera documentos para propostas de licitacao usando templates:
carta proposta, planilha de custos, declaracoes, checklist.

Inclui renderizacao real em PDF via reportlab (pdf_renderer).

Status: DEVELOPMENT — gera conteudo estruturado + PDFs renderizados.
"""

import logging
import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from modules.bidding.agents.base_agent import AgentConfig, AgentStatus, BaseAgent
from modules.bidding.agents.pdf_renderer import render_pdf, save_pdf

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Constantes da empresa padrao
# ──────────────────────────────────────────────

EMPRESA_PADRAO = {
    "razao_social": "CONECTAMAIS ELETRONICA LTDA",
    "cnpj": "35.710.481/0001-03",
    "inscricao_municipal": "45177801",
    "inscricao_suframa": "210140500",
    "endereco": "Manaus-AM",
    "representante_legal": "Jordan Santos de Jesus",
    "telefone": "",
    "email": "",
    "cpf_representante": "",
    "rg_representante": "",
    "banco": "Banco do Brasil",
    "agencia": "",
    "conta": "",
    "regime_tributario": "Lucro Real",
}


# ──────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────


class TipoDocumento(StrEnum):
    """Tipos de documento de proposta."""

    CARTA_PROPOSTA = "carta_proposta"
    PLANILHA_CUSTOS = "planilha_custos"
    DECLARACAO_ME_EPP = "declaracao_me_epp"
    DECLARACAO_INEXISTENCIA_FATO_IMPEDITIVO = "declaracao_fato_impeditivo"
    DECLARACAO_MENOR = "declaracao_menor"
    DECLARACAO_ELABORACAO_INDEPENDENTE = "declaracao_elaboracao_independente"
    DECLARACAO_CUMPRIMENTO_RESERVA_CARGOS = "declaracao_reserva_cargos"
    DECLARACAO_LGPD = "declaracao_lgpd"
    CHECKLIST_HABILITACAO = "checklist_habilitacao"
    PROCURACAO = "procuracao"
    ATESTADO_VISITA_TECNICA = "atestado_visita_tecnica"


class DocumentoGerado(BaseModel):
    """Documento gerado pelo COMPILER."""

    tipo: TipoDocumento
    titulo: str
    conteudo: str  # Texto do documento
    formato: str = "txt"  # txt, html, pdf
    variaveis_preenchidas: dict[str, str] = Field(default_factory=dict)
    revisao_necessaria: bool = True
    observacoes: list[str] = Field(default_factory=list)
    # PDF rendering fields
    pdf_gerado: bool = False
    pdf_path: str = ""  # Caminho absoluto do PDF salvo
    pdf_tamanho_bytes: int = 0


class CompilerInput(BaseModel):
    """Dados de entrada para geracao de documentos."""

    # Dados do edital
    numero_edital: str = ""
    orgao: str = ""
    orgao_cnpj: str = ""
    objeto: str = ""
    modalidade: str = ""

    # Dados da empresa
    razao_social: str = EMPRESA_PADRAO["razao_social"]
    cnpj: str = EMPRESA_PADRAO["cnpj"]
    inscricao_municipal: str = EMPRESA_PADRAO["inscricao_municipal"]
    endereco: str = EMPRESA_PADRAO["endereco"]
    representante_legal: str = EMPRESA_PADRAO["representante_legal"]
    cpf_representante: str = ""
    rg_representante: str = ""
    telefone: str = ""
    email: str = ""

    # Dados bancarios
    banco: str = EMPRESA_PADRAO["banco"]
    agencia: str = ""
    conta: str = ""

    # Dados da proposta (do PRICER)
    valor_mensal: str = ""
    valor_total: str = ""
    prazo_validade_proposta_dias: int = 60
    prazo_contrato_meses: int = 12

    # Documentos a gerar
    tipos_documento: list[TipoDocumento] = Field(
        default_factory=lambda: [
            TipoDocumento.CARTA_PROPOSTA,
            TipoDocumento.PLANILHA_CUSTOS,
            TipoDocumento.DECLARACAO_ME_EPP,
            TipoDocumento.DECLARACAO_INEXISTENCIA_FATO_IMPEDITIVO,
            TipoDocumento.DECLARACAO_MENOR,
            TipoDocumento.DECLARACAO_ELABORACAO_INDEPENDENTE,
            TipoDocumento.DECLARACAO_CUMPRIMENTO_RESERVA_CARGOS,
            TipoDocumento.DECLARACAO_LGPD,
            TipoDocumento.CHECKLIST_HABILITACAO,
        ]
    )


class CompilerResponse(BaseModel):
    """Resultado da geracao de documentos."""

    # Documentos organizados por categoria
    carta_proposta: dict | None = None
    planilha_custos: dict | None = None
    declaracoes: list[dict] = Field(default_factory=list)
    checklist: dict | None = None

    # Lista completa (compatibilidade)
    documentos: list[DocumentoGerado] = Field(default_factory=list)
    total_gerados: int = 0
    total_erros: int = 0
    erros: list[str] = Field(default_factory=list)
    compilado_em: datetime | None = None
    observacoes: list[str] = Field(default_factory=list)

    # PDF rendering summary
    pdfs_gerados: int = 0
    pdfs_paths: list[str] = Field(default_factory=list)
    pdf_diretorio: str = ""


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

_UNIDADES = [
    "",
    "um",
    "dois",
    "tres",
    "quatro",
    "cinco",
    "seis",
    "sete",
    "oito",
    "nove",
    "dez",
    "onze",
    "doze",
    "treze",
    "quatorze",
    "quinze",
    "dezesseis",
    "dezessete",
    "dezoito",
    "dezenove",
]
_DEZENAS = [
    "",
    "",
    "vinte",
    "trinta",
    "quarenta",
    "cinquenta",
    "sessenta",
    "setenta",
    "oitenta",
    "noventa",
]
_CENTENAS = [
    "",
    "cento",
    "duzentos",
    "trezentos",
    "quatrocentos",
    "quinhentos",
    "seiscentos",
    "setecentos",
    "oitocentos",
    "novecentos",
]


def _grupo_por_extenso(n: int) -> str:
    """Converte um numero de 0..999 para extenso."""
    if n == 0:
        return ""
    if n == 100:
        return "cem"
    partes = []
    c = n // 100
    d = n % 100
    if c:
        partes.append(_CENTENAS[c])
    if d < 20:
        if d:
            partes.append(_UNIDADES[d])
    else:
        dezena = d // 10
        unidade = d % 10
        partes.append(_DEZENAS[dezena])
        if unidade:
            partes.append(_UNIDADES[unidade])
    return " e ".join(partes)


def valor_por_extenso(valor: float) -> str:
    """Converte valor numerico para texto por extenso em reais."""
    if valor == 0:
        return "zero reais"

    reais = int(valor)
    centavos = round((valor - reais) * 100)

    partes_reais = []
    if reais >= 1_000_000:
        milhoes = reais // 1_000_000
        reais %= 1_000_000
        if milhoes == 1:
            partes_reais.append("um milhao")
        else:
            partes_reais.append(f"{_grupo_por_extenso(milhoes)} milhoes")

    if reais >= 1_000:
        milhares = reais // 1_000
        reais %= 1_000
        if milhares == 1:
            partes_reais.append("mil")
        else:
            partes_reais.append(f"{_grupo_por_extenso(milhares)} mil")

    if reais > 0:
        partes_reais.append(_grupo_por_extenso(reais))

    total_reais = int(valor)
    if total_reais == 0:
        texto = ""
    elif total_reais == 1:
        texto = "um real"
    else:
        # In Portuguese, groups are connected with "e"
        # e.g. "mil e quinhentos", "um milhao e duzentos mil e trezentos"
        # Exception: "e" is omitted between milhoes/mil when followed by hundreds
        # that already contain "e" internally — but for simplicity and correctness
        # in legal documents, always use "e" between groups.
        texto = " e ".join(partes_reais) + " reais"

    if centavos:
        centavos_ext = _grupo_por_extenso(centavos)
        if centavos == 1:
            centavos_texto = f"{centavos_ext} centavo"
        else:
            centavos_texto = f"{centavos_ext} centavos"
        if total_reais == 0:
            texto = centavos_texto
        else:
            texto += f" e {centavos_texto}"

    return texto


def _parse_valor(valor_str: str) -> float:
    """Extrai valor numerico de uma string como 'R$ 1.234,56' ou 'R$ 540,000.00' ou '1234.56'.

    Handles both Brazilian (1.234,56) and US (1,234.56) number formats.
    Detection: if the last separator is a comma, it's Brazilian decimal;
    if the last separator is a dot, it's US/international decimal.
    """
    if not valor_str:
        return 0.0
    limpo = valor_str.replace("R$", "").replace(" ", "").strip()
    if not limpo:
        return 0.0

    # Determine format by looking at last separator
    last_comma = limpo.rfind(",")
    last_dot = limpo.rfind(".")

    if last_comma > last_dot:
        # Brazilian format: 1.234,56 — comma is decimal separator
        limpo = limpo.replace(".", "").replace(",", ".")
    elif last_dot > last_comma:
        # US/international format: 1,234.56 — dot is decimal separator
        limpo = limpo.replace(",", "")
    else:
        # No separators or only one type
        limpo = limpo.replace(",", "")

    try:
        return float(limpo)
    except ValueError:
        return 0.0


# ──────────────────────────────────────────────
# COMPILER Agent
# ──────────────────────────────────────────────


class CompilerAgent(BaseAgent):
    """
    Agente COMPILER - Gera documentos de proposta de licitacao.

    Responsabilidades:
    - Gerar carta proposta com valores do PRICER (com valor por extenso)
    - Gerar planilha de custos detalhada
    - Gerar 6 declaracoes obrigatorias (ME/EPP, fato impeditivo, menor,
      elaboracao independente, reserva PCD, LGPD)
    - Gerar checklist de habilitacao
    - Preencher templates com dados da empresa e do edital
    - Status: DEVELOPMENT (geracao de conteudo estruturado funcional)
    """

    AGENT_NAME = "compiler"
    AGENT_DESCRIPTION = "Gera documentos de proposta de licitacao"
    AGENT_STATUS = AgentStatus.DEVELOPMENT

    def __init__(self, config: AgentConfig | None = None):
        super().__init__(config)

    async def execute(
        self,
        analysis_data: dict | None = None,
        pricing_data: dict | None = None,
        company_data: dict | None = None,
        # Compatibilidade com chamadas anteriores
        compiler_input: CompilerInput | dict | None = None,
        analysis: dict | None = None,
        **kwargs,
    ) -> dict:
        """
        Gera documentos de proposta de licitacao.

        Args:
            analysis_data: Resultado do ANALYST (dados do edital).
            pricing_data: Resultado do PRICER (precificacao).
            company_data: Dados da empresa licitante (usa padrao se nao informado).
            compiler_input: (Compat.) Input estruturado direto.
            analysis: (Compat.) Alias para analysis_data.

        Returns:
            Dict com keys: carta_proposta, planilha_custos, declaracoes, checklist,
            alem de documentos (lista completa), total_gerados, erros, etc.
        """
        # Resolver compatibilidade: analysis_data tem prioridade sobre analysis
        analysis_result = analysis_data or analysis

        # Construir CompilerInput
        if isinstance(compiler_input, dict):
            inp = CompilerInput(**compiler_input)
        elif isinstance(compiler_input, CompilerInput):
            inp = compiler_input
        else:
            inp = CompilerInput()

        # Aplicar company_data (sobrescreve defaults)
        if company_data:
            for campo in [
                "razao_social",
                "cnpj",
                "inscricao_municipal",
                "endereco",
                "representante_legal",
                "cpf_representante",
                "rg_representante",
                "telefone",
                "email",
                "banco",
                "agencia",
                "conta",
            ]:
                val = company_data.get(campo)
                if val:
                    setattr(inp, campo, val)

        # Preencher dados do analysis se disponivel
        if analysis_result:
            if not inp.numero_edital:
                inp.numero_edital = analysis_result.get("numero_edital", "")
            if not inp.orgao:
                inp.orgao = analysis_result.get("orgao", "")
            if not inp.orgao_cnpj:
                inp.orgao_cnpj = analysis_result.get("orgao_cnpj", "")
            if not inp.objeto:
                inp.objeto = analysis_result.get("objeto_resumido", "") or analysis_result.get("objeto", "")
            if not inp.modalidade:
                inp.modalidade = analysis_result.get("modalidade", "")
            # Prazo do contrato
            prazo = analysis_result.get("prazo_contrato_meses")
            if prazo:
                inp.prazo_contrato_meses = int(prazo)

        # Preencher valores do pricing
        if pricing_data:
            preco_mensal = pricing_data.get("preco_mensal_recomendado", "")
            preco_total = pricing_data.get("preco_total_recomendado", "")
            if preco_mensal:
                inp.valor_mensal = f"R$ {float(preco_mensal):,.2f}"
            if preco_total:
                inp.valor_total = f"R$ {float(preco_total):,.2f}"
            # Prazo do contrato do pricing
            prazo_pricing = pricing_data.get("prazo_contrato_meses")
            if prazo_pricing:
                inp.prazo_contrato_meses = int(prazo_pricing)

        # Gerar documentos
        documentos: list[DocumentoGerado] = []
        erros: list[str] = []

        for tipo in inp.tipos_documento:
            try:
                doc = self._gerar_documento(tipo, inp, pricing_data)
                documentos.append(doc)
            except Exception as e:
                self.logger.error(f"Erro ao gerar {tipo.value}: {e}")
                erros.append(f"{tipo.value}: {e}")

        # ── Render PDFs ──
        # Build a safe subdirectory name from the edital number
        edital_slug = re.sub(r"[^\w\-]", "_", inp.numero_edital or "sem_edital").strip("_") or "sem_edital"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        pdf_subdir = f"{edital_slug}_{timestamp}"

        pdfs_paths: list[str] = []

        for doc in documentos:
            try:
                pdf_bytes = render_pdf(
                    document_content=doc.conteudo,
                    document_type=doc.tipo.value,
                    variaveis=doc.variaveis_preenchidas,
                    pricing_data=pricing_data,
                    titulo=doc.titulo,
                )
                filename = f"{doc.tipo.value}.pdf"
                saved_path = save_pdf(pdf_bytes, filename, subdirectory=pdf_subdir)

                doc.pdf_gerado = True
                doc.pdf_path = saved_path
                doc.pdf_tamanho_bytes = len(pdf_bytes)
                doc.formato = "pdf"
                pdfs_paths.append(saved_path)

                self.logger.info(f"PDF renderizado: {doc.tipo.value} -> {saved_path} ({len(pdf_bytes)} bytes)")
            except Exception as e:
                self.logger.error(f"Erro ao renderizar PDF {doc.tipo.value}: {e}")
                erros.append(f"pdf_{doc.tipo.value}: {e}")

        # ── Organizar por categoria ──
        carta_proposta = None
        planilha_custos = None
        declaracoes = []
        checklist = None

        for doc in documentos:
            doc_dict = doc.model_dump(mode="json")
            if doc.tipo == TipoDocumento.CARTA_PROPOSTA:
                carta_proposta = doc_dict
            elif doc.tipo == TipoDocumento.PLANILHA_CUSTOS:
                planilha_custos = doc_dict
            elif doc.tipo == TipoDocumento.CHECKLIST_HABILITACAO:
                checklist = doc_dict
            elif doc.tipo.value.startswith("declaracao_"):
                declaracoes.append(doc_dict)

        from modules.bidding.agents.pdf_renderer import PDF_OUTPUT_DIR

        response = CompilerResponse(
            carta_proposta=carta_proposta,
            planilha_custos=planilha_custos,
            declaracoes=declaracoes,
            checklist=checklist,
            documentos=documentos,
            total_gerados=len(documentos),
            total_erros=len(erros),
            erros=erros,
            compilado_em=datetime.utcnow(),
            observacoes=[
                "Documentos gerados com renderizacao PDF via reportlab.",
                "Revisao manual recomendada antes da submissao.",
                f"PDFs salvos em: {PDF_OUTPUT_DIR / pdf_subdir}",
            ],
            pdfs_gerados=len(pdfs_paths),
            pdfs_paths=pdfs_paths,
            pdf_diretorio=str(PDF_OUTPUT_DIR / pdf_subdir),
        )

        self.logger.info(
            f"COMPILER: {len(documentos)} documentos gerados, {len(pdfs_paths)} PDFs renderizados, {len(erros)} erros"
        )

        return response.model_dump(mode="json")

    def _gerar_documento(
        self,
        tipo: TipoDocumento,
        inp: CompilerInput,
        pricing_data: dict | None,
    ) -> DocumentoGerado:
        """Gera um documento especifico baseado no tipo."""
        generators = {
            TipoDocumento.CARTA_PROPOSTA: self._gerar_carta_proposta,
            TipoDocumento.PLANILHA_CUSTOS: self._gerar_planilha_custos,
            TipoDocumento.DECLARACAO_ME_EPP: self._gerar_declaracao_me_epp,
            TipoDocumento.DECLARACAO_INEXISTENCIA_FATO_IMPEDITIVO: self._gerar_declaracao_fato_impeditivo,
            TipoDocumento.DECLARACAO_MENOR: self._gerar_declaracao_menor,
            TipoDocumento.DECLARACAO_ELABORACAO_INDEPENDENTE: self._gerar_declaracao_elaboracao_independente,
            TipoDocumento.DECLARACAO_CUMPRIMENTO_RESERVA_CARGOS: self._gerar_declaracao_reserva_cargos,
            TipoDocumento.DECLARACAO_LGPD: self._gerar_declaracao_lgpd,
            TipoDocumento.CHECKLIST_HABILITACAO: self._gerar_checklist_habilitacao,
        }

        generator = generators.get(tipo)
        if generator is None:
            return DocumentoGerado(
                tipo=tipo,
                titulo=tipo.value,
                conteudo=f"[Template para {tipo.value} ainda nao implementado]",
                revisao_necessaria=True,
                observacoes=["Template nao implementado - gerar manualmente"],
            )

        return generator(inp, pricing_data)

    # ──────────────────────────────────────────
    # Carta Proposta
    # ──────────────────────────────────────────

    def _gerar_carta_proposta(self, inp: CompilerInput, pricing_data: dict | None) -> DocumentoGerado:
        """Gera carta proposta comercial com valor por extenso e dados bancarios."""
        data_hoje = datetime.utcnow().strftime("%d/%m/%Y")

        # Calcular valor por extenso
        valor_total_num = _parse_valor(inp.valor_total)
        valor_mensal_num = _parse_valor(inp.valor_mensal)
        valor_total_extenso = valor_por_extenso(valor_total_num) if valor_total_num else "[VALOR POR EXTENSO]"
        valor_mensal_extenso = valor_por_extenso(valor_mensal_num) if valor_mensal_num else "[VALOR POR EXTENSO]"

        variaveis = {
            "orgao": inp.orgao or "[ORGAO]",
            "numero_edital": inp.numero_edital or "[NUMERO_EDITAL]",
            "modalidade": inp.modalidade or "[MODALIDADE]",
            "objeto": inp.objeto or "[OBJETO]",
            "razao_social": inp.razao_social,
            "cnpj": inp.cnpj,
            "inscricao_municipal": inp.inscricao_municipal,
            "endereco": inp.endereco,
            "valor_mensal": inp.valor_mensal or "[VALOR_MENSAL]",
            "valor_mensal_extenso": valor_mensal_extenso,
            "valor_total": inp.valor_total or "[VALOR_TOTAL]",
            "valor_total_extenso": valor_total_extenso,
            "prazo_validade": str(inp.prazo_validade_proposta_dias),
            "prazo_contrato": str(inp.prazo_contrato_meses),
            "representante": inp.representante_legal or "[REPRESENTANTE_LEGAL]",
            "cpf_representante": inp.cpf_representante or "[CPF]",
            "rg_representante": inp.rg_representante or "[RG]",
            "telefone": inp.telefone or "[TELEFONE]",
            "email": inp.email or "[EMAIL]",
            "banco": inp.banco or "[BANCO]",
            "agencia": inp.agencia or "[AGENCIA]",
            "conta": inp.conta or "[CONTA]",
            "data": data_hoje,
        }

        conteudo = f"""CARTA PROPOSTA COMERCIAL

Ao
{variaveis["orgao"]}

Ref.: {variaveis["modalidade"]} - Edital n. {variaveis["numero_edital"]}

Prezados Senhores,

A empresa {variaveis["razao_social"]}, inscrita no CNPJ sob o n. {variaveis["cnpj"]}, \
Inscricao Municipal n. {variaveis["inscricao_municipal"]}, \
com sede em {variaveis["endereco"]}, por intermedio de seu representante legal infra-assinado, \
apresenta a Vossa Senhoria proposta comercial para prestacao dos servicos objeto do Edital \
em referencia, nos termos a seguir:

1. OBJETO
{variaveis["objeto"]}

2. VALORES
Valor Mensal: {variaveis["valor_mensal"]} ({variaveis["valor_mensal_extenso"]})
Valor Total ({variaveis["prazo_contrato"]} meses): {variaveis["valor_total"]} ({variaveis["valor_total_extenso"]})

3. VALIDADE DA PROPOSTA
Esta proposta tem validade de {variaveis["prazo_validade"]} (sessenta) dias corridos, \
contados da data de sua apresentacao.

4. PRAZO DE EXECUCAO
O prazo de execucao dos servicos sera de {variaveis["prazo_contrato"]} ({variaveis["prazo_contrato"]}) meses, \
conforme estabelecido no Edital, podendo ser prorrogado nos termos da legislacao vigente.

5. DADOS BANCARIOS
Banco: {variaveis["banco"]}
Agencia: {variaveis["agencia"]}
Conta Corrente: {variaveis["conta"]}
Titular: {variaveis["razao_social"]}
CNPJ: {variaveis["cnpj"]}

6. DECLARACOES
Declaramos que:
a) Nos precos propostos estao inclusos todos os custos diretos e indiretos, encargos sociais, \
trabalhistas, previdenciarios, fiscais, comerciais, taxas, seguros, deslocamentos, bem como \
quaisquer outros custos que incidam ou venham a incidir sobre o objeto licitado;
b) Temos pleno conhecimento das condicoes e peculiaridades inerentes a natureza dos servicos, \
assumindo total responsabilidade por esse fato;
c) Atendemos a todos os requisitos de habilitacao constantes do Edital;
d) Nao possuimos em nosso quadro societario servidor publico da ativa, ou empregado de \
empresa publica ou de sociedade de economia mista;
e) Nao possuimos, em nossa cadeia produtiva, empregados executando trabalho degradante ou \
forcado, observando o disposto nos incisos III e IV do art. 1o e no inciso III do art. 5o \
da Constituicao Federal;
f) Cumprimos as exigencias de reserva de cargos para pessoa com deficiencia e para \
reabilitado da Previdencia Social, previstas em lei e em outras normas especificas.

7. CONTATO
Telefone: {variaveis["telefone"]}
E-mail: {variaveis["email"]}

Manaus-AM, {variaveis["data"]}.

___________________________________
{variaveis["razao_social"]}
CNPJ: {variaveis["cnpj"]}
{variaveis["representante"]}
CPF: {variaveis["cpf_representante"]}
RG: {variaveis["rg_representante"]}"""

        return DocumentoGerado(
            tipo=TipoDocumento.CARTA_PROPOSTA,
            titulo="Carta Proposta Comercial",
            conteudo=conteudo,
            variaveis_preenchidas=variaveis,
            revisao_necessaria=True,
            observacoes=[
                "Revisar valores e dados antes de submeter",
                "Confirmar dados bancarios",
                "Verificar se valor por extenso esta correto",
            ],
        )

    # ──────────────────────────────────────────
    # Planilha de Custos
    # ──────────────────────────────────────────

    def _gerar_planilha_custos(self, inp: CompilerInput, pricing_data: dict | None) -> DocumentoGerado:
        """Gera planilha de custos detalhada em formato texto."""
        if not pricing_data:
            return DocumentoGerado(
                tipo=TipoDocumento.PLANILHA_CUSTOS,
                titulo="Planilha de Composicao de Custos",
                conteudo="[Dados de precificacao nao disponiveis - executar PRICER primeiro]",
                revisao_necessaria=True,
                observacoes=["Necessario dados do PRICER"],
            )

        cenario_recomendado = pricing_data.get("cenario_recomendado", "moderado")
        cenarios = pricing_data.get("cenarios", [])
        cenario = None
        for c in cenarios:
            if c.get("tipo") == cenario_recomendado:
                cenario = c
                break
        if not cenario and cenarios:
            cenario = cenarios[0]

        if not cenario:
            return DocumentoGerado(
                tipo=TipoDocumento.PLANILHA_CUSTOS,
                titulo="Planilha de Composicao de Custos",
                conteudo="[Nenhum cenario disponivel]",
                revisao_necessaria=True,
            )

        mdo = cenario.get("custo_mao_de_obra", {})
        regime = pricing_data.get("regime_tributario", "lucro_real").upper().replace("_", " ")
        prazo = pricing_data.get("prazo_contrato_meses", inp.prazo_contrato_meses)

        # Formatar BDI composicao
        bdi_pct = cenario.get("bdi_percentual", "0")
        margem_pct = cenario.get("margem_lucro_percentual", "0")

        conteudo = f"""PLANILHA DE COMPOSICAO DE CUSTOS E FORMACAO DE PRECOS
=====================================================================
Empresa: {inp.razao_social}
CNPJ: {inp.cnpj}
Edital: {inp.numero_edital or "[N/A]"}
Orgao: {inp.orgao or "[N/A]"}
Regime Tributario: {regime}
Cenario: {cenario_recomendado.upper()}

1. MAO DE OBRA - REMUNERACAO
---------------------------------------------------------------
1.1 Salario Base:                    R$ {mdo.get("salario_base", "0.00")}
1.2 Adicional Periculosidade (30%):  R$ {mdo.get("adicional_periculosidade", "0.00")}
1.3 Adicional Noturno (20%):         R$ {mdo.get("adicional_noturno", "0.00")}
1.4 Adicional Insalubridade:         R$ {mdo.get("adicional_insalubridade", "0.00")}
1.5 Horas Extras:                    R$ {mdo.get("horas_extras", "0.00")}
---------------------------------------------------------------
SUBTOTAL REMUNERACAO:                R$ {mdo.get("total_remuneracao", "0.00")}

2. ENCARGOS SOCIAIS E TRABALHISTAS
---------------------------------------------------------------
2.1 INSS Patronal (20%):            R$ {mdo.get("inss_patronal", "0.00")}
2.2 FGTS (8%):                      R$ {mdo.get("fgts", "0.00")}
2.3 Terceiros/Sistema S (5,8%):     R$ {mdo.get("terceiros_sistema_s", "0.00")}
2.4 Provisao Ferias (12,1%):        R$ {mdo.get("provisao_ferias", "0.00")}
2.5 Provisao 13o Salario (8,93%):   R$ {mdo.get("provisao_13o", "0.00")}
2.6 Provisao Rescisao (5,2%):       R$ {mdo.get("provisao_rescisao", "0.00")}
---------------------------------------------------------------
TOTAL ENCARGOS:                      R$ {mdo.get("total_encargos", "0.00")}

3. BENEFICIOS
---------------------------------------------------------------
3.1 Vale Transporte:                 R$ {mdo.get("vale_transporte", "0.00")}
3.2 Vale Alimentacao:                R$ {mdo.get("vale_alimentacao", "0.00")}
3.3 Assistencia Medica:              R$ {mdo.get("assistencia_medica", "0.00")}
3.4 Seguro de Vida:                  R$ {mdo.get("seguro_vida", "0.00")}
3.5 Uniforme/EPI:                    R$ {mdo.get("uniforme_epi", "0.00")}
---------------------------------------------------------------
SUBTOTAL BENEFICIOS:                 R$ {mdo.get("total_beneficios", "0.00")}

4. CUSTO TOTAL MAO DE OBRA
---------------------------------------------------------------
Qtd. Profissionais:                  {mdo.get("quantidade_profissionais", 0)}
Custo Unitario/Mes:                  R$ {mdo.get("custo_mensal_unitario", "0.00")}
TOTAL MAO DE OBRA/MES:              R$ {mdo.get("custo_mensal_total", "0.00")}

5. CUSTOS INDIRETOS (Administrativos + Equipamentos)
---------------------------------------------------------------
TOTAL CUSTOS INDIRETOS:              R$ {cenario.get("custos_indiretos", "0.00")}

6. CUSTO TOTAL DIRETO
---------------------------------------------------------------
CUSTO TOTAL DIRETO:                  R$ {cenario.get("custo_total_direto", "0.00")}

7. BDI - BENEFICIOS E DESPESAS INDIRETAS
---------------------------------------------------------------
7.1 Administracao Central:           6,00%
7.2 Seguro/Garantia:                 1,00%
7.3 Risco:                           1,50%
7.4 Despesas Financeiras:            0,80%
7.5 Margem de Lucro:                 {margem_pct}%
7.6 Tributos:                        (ver item 8)
---------------------------------------------------------------
BDI TOTAL:                           {bdi_pct}%
Valor BDI:                           R$ {cenario.get("valor_bdi", "0.00")}

8. IMPOSTOS E TRIBUTOS
---------------------------------------------------------------
{self._formatar_impostos(cenario.get("impostos_detalhamento", {}))}
---------------------------------------------------------------
TOTAL IMPOSTOS:                      R$ {cenario.get("total_impostos", "0.00")}

9. LUCRO
---------------------------------------------------------------
Margem de Lucro:                     {margem_pct}%
Valor Lucro:                         R$ {cenario.get("valor_lucro", "0.00")}

10. RESUMO GERAL
===============================================================
PRECO MENSAL:                        R$ {cenario.get("preco_mensal", "0.00")}
PRECO ANUAL:                         R$ {cenario.get("preco_anual", "0.00")}
PRECO TOTAL CONTRATO ({prazo} meses): R$ {cenario.get("preco_total_contrato", "0.00")}
===============================================================

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.PLANILHA_CUSTOS,
            titulo="Planilha de Composicao de Custos e Formacao de Precos",
            conteudo=conteudo,
            revisao_necessaria=True,
            observacoes=[
                "Valores calculados automaticamente pelo PRICER",
                "Verificar convencao coletiva vigente para salarios e beneficios",
                "Ajustar impostos conforme regime tributario atual",
                f"Cenario utilizado: {cenario_recomendado}",
            ],
        )

    def _formatar_impostos(self, impostos: dict) -> str:
        """Formata detalhamento de impostos para a planilha."""
        linhas = []
        for nome, valor in impostos.items():
            nome_formatado = nome.upper().replace("_", " ")
            espacos = max(1, 35 - len(nome_formatado))
            linhas.append(f"  {nome_formatado}:{' ' * espacos}{valor}%")
        return "\n".join(linhas) if linhas else "  (Sem detalhamento disponivel)"

    # ──────────────────────────────────────────
    # Declaracoes
    # ──────────────────────────────────────────

    def _gerar_declaracao_me_epp(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera declaracao de enquadramento como ME/EPP."""
        conteudo = f"""DECLARACAO DE ENQUADRAMENTO COMO MICROEMPRESA OU
EMPRESA DE PEQUENO PORTE

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
por intermedio de seu representante legal, o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do RG n. {inp.rg_representante or "[RG]"} e CPF n. {inp.cpf_representante or "[CPF]"}, \
DECLARA, sob as penalidades da lei, que:

1. Cumpre os requisitos estabelecidos no art. 3o da Lei Complementar n. 123, de 14 de \
dezembro de 2006, alterada pela Lei Complementar n. 147, de 7 de agosto de 2014, e que \
esta apta a usufruir do tratamento favorecido estabelecido nos artigos 42 a 49 da referida \
Lei Complementar;

2. Nao possui qualquer dos impedimentos previstos nos paragrafos 4o e seguintes todos do \
artigo 3o da Lei Complementar n. 123/2006, e esta ciente da obrigatoriedade de declarar \
ocorrencias posteriores impeditivas de tal beneficio;

3. O faturamento bruto anual da empresa nao excede o limite previsto na legislacao para \
enquadramento como Empresa de Pequeno Porte.

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_ME_EPP,
            titulo="Declaracao de Enquadramento ME/EPP",
            conteudo=conteudo,
            revisao_necessaria=True,
            observacoes=[
                "Verificar se a empresa se enquadra como ME/EPP antes de usar",
                "Se regime Lucro Real, esta declaracao pode nao ser aplicavel",
                "ATENCAO: CNPJ 35.710.481/0001-03 esta atualmente em LUCRO REAL",
            ],
        )

    def _gerar_declaracao_fato_impeditivo(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera declaracao de inexistencia de fato impeditivo."""
        conteudo = f"""DECLARACAO DE INEXISTENCIA DE FATO IMPEDITIVO

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
sediada em {inp.endereco}, por intermedio de seu representante legal, \
o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do CPF n. {inp.cpf_representante or "[CPF]"}, DECLARA, \
sob as penalidades da lei, que ate a presente data inexistem fatos impeditivos para \
sua habilitacao no presente processo licitatorio, ciente da obrigatoriedade de declarar \
ocorrencias posteriores.

DECLARA ainda que:

a) Nao foi declarada inidonea por nenhum orgao da Administracao Publica de qualquer \
esfera de governo;

b) Nao possui em seu quadro societario servidor publico da ativa, ou empregado de \
empresa publica ou de sociedade de economia mista, nos termos da legislacao vigente;

c) Nao possui no quadro de diretores pessoa que participou, em razao de vinculo de \
mesma natureza, de empresa declarada inidonea.

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}
CPF: {inp.cpf_representante or "[CPF]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_INEXISTENCIA_FATO_IMPEDITIVO,
            titulo="Declaracao de Inexistencia de Fato Impeditivo",
            conteudo=conteudo,
            revisao_necessaria=True,
        )

    def _gerar_declaracao_menor(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera declaracao de nao emprego de menor."""
        conteudo = f"""DECLARACAO DE NAO EMPREGO DE MENOR
(Lei n. 9.854/1999 - Decreto n. 4.358/2002)

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
por intermedio de seu representante legal, o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do CPF n. {inp.cpf_representante or "[CPF]"}, \
DECLARA, para fins do disposto no inciso V do art. 68 da Lei n. 14.133/2021, \
que nao emprega menor de 18 (dezoito) anos em trabalho noturno, perigoso ou insalubre \
e nao emprega menor de 16 (dezesseis) anos.

Ressalva: emprega menor, a partir de 14 (quatorze) anos, na condicao de aprendiz ( ).

(Observacao: em caso afirmativo, assinalar a ressalva acima)

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}
CPF: {inp.cpf_representante or "[CPF]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_MENOR,
            titulo="Declaracao de Nao Emprego de Menor",
            conteudo=conteudo,
            revisao_necessaria=True,
        )

    def _gerar_declaracao_elaboracao_independente(
        self, inp: CompilerInput, _pricing_data: dict | None
    ) -> DocumentoGerado:
        """Gera declaracao de elaboracao independente de proposta."""
        conteudo = f"""DECLARACAO DE ELABORACAO INDEPENDENTE DE PROPOSTA

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
por intermedio de seu representante legal, o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do CPF n. {inp.cpf_representante or "[CPF]"}, DECLARA, sob as penas da lei, em especial \
o art. 299 do Codigo Penal Brasileiro, que:

a) A proposta apresentada foi elaborada de maneira independente, e seu conteudo nao foi, \
no todo ou em parte, direta ou indiretamente, informado, discutido ou recebido de qualquer \
outro participante potencial ou de fato do presente processo licitatorio;

b) A intencao de apresentar a proposta nao foi informada, discutida ou recebida de qualquer \
outro participante potencial ou de fato do presente processo licitatorio;

c) Nao tentou, por qualquer meio ou por qualquer pessoa, influir na decisao de qualquer \
outro participante potencial ou de fato quanto a participar ou nao do referido processo;

d) O conteudo da proposta nao sera, no todo ou em parte, direta ou indiretamente, \
comunicado ou discutido com qualquer outro participante potencial ou de fato do processo \
antes da adjudicacao do objeto;

e) O conteudo da proposta nao foi, no todo ou em parte, informado, discutido ou recebido \
de qualquer integrante do orgao licitante antes da abertura oficial das propostas;

f) Esta plenamente ciente do teor e da extensao desta declaracao e que detem plenos \
poderes e informacoes para firma-la.

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}
CPF: {inp.cpf_representante or "[CPF]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_ELABORACAO_INDEPENDENTE,
            titulo="Declaracao de Elaboracao Independente de Proposta",
            conteudo=conteudo,
            revisao_necessaria=True,
        )

    def _gerar_declaracao_reserva_cargos(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera declaracao de cumprimento da reserva de cargos para PcD."""
        conteudo = f"""DECLARACAO DE CUMPRIMENTO DA RESERVA DE CARGOS PARA
PESSOA COM DEFICIENCIA E REABILITADO DA PREVIDENCIA SOCIAL
(Art. 63, IV, da Lei n. 14.133/2021)

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
por intermedio de seu representante legal, o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do CPF n. {inp.cpf_representante or "[CPF]"}, DECLARA, para fins do disposto no \
art. 63, inciso IV, da Lei n. 14.133/2021, que:

1. Cumpre as exigencias de reserva de cargos para pessoa com deficiencia e para \
reabilitado da Previdencia Social, previstas em lei e em outras normas especificas;

2. Observa o percentual minimo de 2% (dois por cento) a 5% (cinco por cento) de seus \
cargos para beneficiarios reabilitados ou pessoas portadoras de deficiencia, conforme \
art. 93 da Lei n. 8.213/1991;

3. Compromete-se a manter o cumprimento dessas exigencias durante toda a vigencia \
do contrato decorrente desta licitacao.

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}
CPF: {inp.cpf_representante or "[CPF]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_CUMPRIMENTO_RESERVA_CARGOS,
            titulo="Declaracao de Cumprimento da Reserva de Cargos PCD",
            conteudo=conteudo,
            revisao_necessaria=True,
        )

    def _gerar_declaracao_lgpd(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera declaracao de conformidade com LGPD."""
        conteudo = f"""DECLARACAO DE CONFORMIDADE COM A LEI GERAL DE PROTECAO DE DADOS
(Lei n. 13.709/2018 - LGPD)

{inp.orgao or "[ORGAO LICITANTE]"}
Ref.: {inp.modalidade or "[MODALIDADE]"} - Edital n. {inp.numero_edital or "[N/EDITAL]"}

A empresa {inp.razao_social}, inscrita no CNPJ sob o n. {inp.cnpj}, \
por intermedio de seu representante legal, o(a) Sr(a). {inp.representante_legal or "[REPRESENTANTE]"}, \
portador(a) do CPF n. {inp.cpf_representante or "[CPF]"}, DECLARA que:

1. Conhece e se compromete a cumprir integralmente as disposicoes da Lei n. 13.709/2018 \
(Lei Geral de Protecao de Dados Pessoais - LGPD);

2. Adota medidas de seguranca, tecnicas e administrativas aptas a proteger os dados \
pessoais de acessos nao autorizados e de situacoes acidentais ou ilicitas de destruicao, \
perda, alteracao, comunicacao ou qualquer forma de tratamento inadequado ou ilicito;

3. Compromete-se a tratar os dados pessoais a que tiver acesso em razao da execucao \
contratual apenas para as finalidades previstas no contrato, em conformidade com a LGPD \
e com as orientacoes da Autoridade Nacional de Protecao de Dados (ANPD);

4. Nao compartilhara dados pessoais com terceiros sem autorizacao expressa do Contratante, \
exceto quando exigido por lei ou regulamentacao aplicavel;

5. Notificara o Contratante em prazo razoavel, nao superior a 48 (quarenta e oito) horas, \
sobre qualquer incidente de seguranca que possa acarretar risco ou dano relevante aos \
titulares dos dados;

6. Mantera registro das operacoes de tratamento de dados pessoais que realizar em razao \
do contrato, conforme art. 37 da LGPD;

7. Ao termino do contrato, eliminara os dados pessoais tratados em razao da execucao \
contratual, salvo nas hipoteses de conservacao previstas no art. 16 da LGPD.

Manaus-AM, {datetime.utcnow().strftime("%d/%m/%Y")}.

___________________________________
{inp.razao_social}
CNPJ: {inp.cnpj}
{inp.representante_legal or "[REPRESENTANTE LEGAL]"}
CPF: {inp.cpf_representante or "[CPF]"}"""

        return DocumentoGerado(
            tipo=TipoDocumento.DECLARACAO_LGPD,
            titulo="Declaracao de Conformidade com a LGPD",
            conteudo=conteudo,
            revisao_necessaria=True,
        )

    # ──────────────────────────────────────────
    # Checklist de Habilitacao
    # ──────────────────────────────────────────

    def _gerar_checklist_habilitacao(self, inp: CompilerInput, _pricing_data: dict | None) -> DocumentoGerado:
        """Gera checklist de documentos necessarios para habilitacao."""
        data_hoje = datetime.utcnow().strftime("%d/%m/%Y")

        conteudo = f"""CHECKLIST DE DOCUMENTOS PARA HABILITACAO
=====================================================================
Empresa: {inp.razao_social}
CNPJ: {inp.cnpj}
Edital: {inp.numero_edital or "[N/A]"}
Orgao: {inp.orgao or "[N/A]"}
Data de Verificacao: {data_hoje}

HABILITACAO JURIDICA
---------------------------------------------------------------
[ ] Ato constitutivo, estatuto ou contrato social em vigor
[ ] Documento de eleicao de administradores (se aplicavel)
[ ] Cedula de identidade do representante legal
[ ] Procuracao (se representado por procurador)

REGULARIDADE FISCAL E TRABALHISTA
---------------------------------------------------------------
[ ] Prova de inscricao no CNPJ
[ ] Prova de inscricao no cadastro de contribuintes estadual/municipal
[ ] Certidao Negativa de Debitos Federais (RFB/PGFN)
[ ] Certidao Negativa de Debitos Estaduais
[ ] Certidao Negativa de Debitos Municipais
[ ] Certificado de Regularidade do FGTS (CRF)
[ ] Certidao Negativa de Debitos Trabalhistas (CNDT)
[ ] Certidao Negativa de Falencia e Concordata

QUALIFICACAO TECNICA
---------------------------------------------------------------
[ ] Registro ou inscricao na entidade profissional competente
[ ] Atestado(s) de capacidade tecnica
[ ] Autorizacao de funcionamento emitida pela Policia Federal (vigilancia)
[ ] Certificado de Seguranca atualizado
[ ] Relacao de profissionais com formacao em vigilancia

QUALIFICACAO ECONOMICO-FINANCEIRA
---------------------------------------------------------------
[ ] Balanco patrimonial e demonstracoes contabeis do ultimo exercicio
[ ] Certidao negativa de falencia e recuperacao judicial
[ ] Comprovacao de capital social minimo ou patrimonio liquido minimo
[ ] Garantia de proposta (se exigida no edital)

DECLARACOES OBRIGATORIAS
---------------------------------------------------------------
[ ] Declaracao de Enquadramento ME/EPP (se aplicavel)
[ ] Declaracao de Inexistencia de Fato Impeditivo
[ ] Declaracao de Nao Emprego de Menor
[ ] Declaracao de Elaboracao Independente de Proposta
[ ] Declaracao de Cumprimento de Reserva de Cargos PCD
[ ] Declaracao de Conformidade LGPD

PROPOSTA COMERCIAL
---------------------------------------------------------------
[ ] Carta Proposta assinada
[ ] Planilha de Composicao de Custos e Formacao de Precos
[ ] Cronograma de implantacao (se exigido)

DOCUMENTOS COMPLEMENTARES
---------------------------------------------------------------
[ ] Comprovante de visita tecnica (se exigida)
[ ] Amostra ou demonstracao (se exigida)
[ ] Documentacao especifica do edital (verificar)

OBSERVACOES:
- Verificar prazos de validade de todas as certidoes
- Conferir se o edital exige documentos adicionais especificos
- Autenticar copias conforme exigencia do edital
- Organizar documentos na ordem do edital
- Paginar todos os documentos sequencialmente

___________________________________
Responsavel pela verificacao:
Data: {data_hoje}"""

        return DocumentoGerado(
            tipo=TipoDocumento.CHECKLIST_HABILITACAO,
            titulo="Checklist de Documentos para Habilitacao",
            conteudo=conteudo,
            revisao_necessaria=True,
            observacoes=[
                "Adaptar checklist conforme exigencias especificas do edital",
                "Verificar prazos de validade das certidoes antes da sessao",
                "Documentos de vigilancia requerem autorizacao PF vigente",
            ],
        )
