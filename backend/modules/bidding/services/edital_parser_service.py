"""
EditalParserService - Parser de PDFs de editais de licitacao
=============================================================
Extrai texto de PDFs e estrutura informacoes de editais brasileiros
usando apenas regex e operacoes de string (sem dependencias NLP).

Compativel com editais da Lei 14.133/2021 e Lei 8.666/1993.
"""

import io
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# DTOs
# ──────────────────────────────────────────────────────────────


@dataclass
class EditalItem:
    """Item extraido da tabela de itens do edital."""

    numero: int
    descricao: str
    quantidade: Decimal = Decimal("1")
    unidade: str = "UN"
    valor_unitario_estimado: Decimal | None = None
    valor_total_estimado: Decimal | None = None


@dataclass
class RedFlag:
    """Red flag identificada no edital."""

    tipo: str
    descricao: str
    severidade: str  # alta, media, baixa
    trecho: str | None = None


@dataclass
class RequisitoHabilitacao:
    """Requisito de habilitacao extraido do edital."""

    categoria: str  # juridica, fiscal, tecnica, economica
    descricao: str
    obrigatorio: bool = True


@dataclass
class EditalParseResult:
    """Resultado completo do parse de um edital."""

    # Texto bruto
    texto_completo: str = ""

    # Identificacao
    numero_edital: str | None = None
    modalidade: str | None = None
    processo_administrativo: str | None = None

    # Objeto
    objeto: str | None = None

    # Valores
    valor_estimado: Decimal | None = None

    # Datas
    data_abertura: str | None = None
    data_encerramento: str | None = None

    # Julgamento
    criterio_julgamento: str | None = None

    # Orgao
    orgao_nome: str | None = None
    orgao_cnpj: str | None = None

    # Habilitacao
    requisitos_habilitacao: list[RequisitoHabilitacao] = field(default_factory=list)

    # Documentos exigidos
    documentos_exigidos: list[str] = field(default_factory=list)

    # Itens
    itens: list[EditalItem] = field(default_factory=list)

    # Contrato
    prazo_contrato: str | None = None

    # Garantias
    garantias: list[str] = field(default_factory=list)

    # Penalidades
    penalidades: list[str] = field(default_factory=list)

    # Red flags
    red_flags: list[RedFlag] = field(default_factory=list)

    # Classificacao
    segmento: str | None = None

    # Metadados
    total_paginas: int = 0
    total_caracteres: int = 0
    parsed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario serializavel."""
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Decimal):
                result[k] = float(v)
            elif isinstance(v, list):
                items = []
                for item in v:
                    if hasattr(item, "__dict__"):
                        d = {}
                        for ik, iv in item.__dict__.items():
                            d[ik] = float(iv) if isinstance(iv, Decimal) else iv
                        items.append(d)
                    else:
                        items.append(item)
                result[k] = items
            else:
                result[k] = v
        return result


# ──────────────────────────────────────────────────────────────
# Constantes e Patterns
# ──────────────────────────────────────────────────────────────

# Modalidades de licitacao
MODALIDADES = {
    "pregao eletronico": "Pregão Eletrônico",
    "pregao presencial": "Pregão Presencial",
    "pregão eletrônico": "Pregão Eletrônico",
    "pregão presencial": "Pregão Presencial",
    "concorrencia": "Concorrência",
    "concorrência": "Concorrência",
    "concorrência eletrônica": "Concorrência Eletrônica",
    "concorrencia eletronica": "Concorrência Eletrônica",
    "tomada de precos": "Tomada de Preços",
    "tomada de preços": "Tomada de Preços",
    "convite": "Convite",
    "leilao": "Leilão",
    "leilão": "Leilão",
    "dialogo competitivo": "Diálogo Competitivo",
    "diálogo competitivo": "Diálogo Competitivo",
    "dispensa": "Dispensa",
    "dispensa eletronica": "Dispensa Eletrônica",
    "dispensa eletrônica": "Dispensa Eletrônica",
    "inexigibilidade": "Inexigibilidade",
    "rdc": "RDC",
    "chamamento publico": "Chamamento Público",
    "chamamento público": "Chamamento Público",
}

# Criterios de julgamento
CRITERIOS_JULGAMENTO = [
    "menor preço",
    "menor preco",
    "maior desconto",
    "melhor técnica",
    "melhor tecnica",
    "técnica e preço",
    "tecnica e preco",
    "maior retorno econômico",
    "maior retorno economico",
    "maior lance",
]

# Segmentos de servico
SEGMENTOS_KEYWORDS = {
    "vigilancia_armada": [
        "vigilância armada",
        "vigilancia armada",
        "segurança armada",
        "seguranca armada",
        "vigilante armado",
        "armamento",
    ],
    "vigilancia_desarmada": [
        "vigilância desarmada",
        "vigilancia desarmada",
        "segurança desarmada",
        "seguranca desarmada",
        "vigilante desarmado",
    ],
    "seguranca_eletronica": [
        "segurança eletrônica",
        "seguranca eletronica",
        "cftv",
        "câmera",
        "camera",
        "alarme",
        "monitoramento eletrônico",
        "monitoramento eletronico",
        "cerca elétrica",
        "cerca eletrica",
        "controle de acesso",
    ],
    "portaria_presencial": [
        "portaria presencial",
        "porteiro",
        "portaria humanizada",
        "controle de acesso presencial",
    ],
    "portaria_remota": [
        "portaria remota",
        "portaria virtual",
        "portaria autônoma",
        "portaria autonoma",
    ],
    "limpeza": [
        "limpeza",
        "asseio",
        "conservação predial",
        "conservacao predial",
        "higienização",
        "higienizacao",
        "servente",
    ],
    "jardinagem": [
        "jardinagem",
        "paisagismo",
        "área verde",
        "area verde",
        "poda",
        "roçagem",
        "rocagem",
    ],
    "facilities": [
        "facilities",
        "manutenção predial",
        "manutencao predial",
        "zeladoria",
        "recepção",
        "recepcao",
        "copa",
        "copeira",
        "brigadista",
    ],
}


# ──────────────────────────────────────────────────────────────
# Service
# ──────────────────────────────────────────────────────────────


class EditalParserService:
    """
    Servico para extrair e estruturar dados de editais de licitacao a partir de PDF.

    Funciona inteiramente com regex e operacoes de string — nenhuma dependencia
    de NLP e necessaria. Compativel com editais brasileiros (Lei 14.133/2021,
    Lei 8.666/1993, decretos de pregao).
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    # ──────────────────────────────────────────────
    # 1. parse_pdf - Extracao de texto do PDF
    # ──────────────────────────────────────────────

    def parse_pdf(self, file_path_or_bytes: str | bytes | Path) -> str:
        """
        Extrai texto de um PDF.

        Args:
            file_path_or_bytes: Caminho do arquivo PDF, objeto Path, ou bytes do PDF.

        Returns:
            Texto extraido concatenado de todas as paginas.

        Raises:
            ValueError: Se nenhum texto puder ser extraido.
            FileNotFoundError: Se o arquivo nao existir.
        """
        reader = None
        total_pages = 0

        # Tentar PyPDF2 primeiro
        try:
            from PyPDF2 import PdfReader

            if isinstance(file_path_or_bytes, (str, Path)):
                path = Path(file_path_or_bytes)
                if not path.exists():
                    raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
                reader = PdfReader(str(path))
            else:
                reader = PdfReader(io.BytesIO(file_path_or_bytes))

            total_pages = len(reader.pages)
            pages_text = []
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    pages_text.append(text)
                except Exception as e:
                    self.logger.warning(f"Erro ao extrair pagina {i + 1}: {e}")
                    pages_text.append("")

            full_text = "\n\n".join(pages_text)
            if full_text.strip():
                self.logger.info(f"PDF extraido com PyPDF2: {total_pages} paginas, {len(full_text)} caracteres")
                return full_text

        except ImportError:
            self.logger.warning("PyPDF2 nao disponivel, tentando pdfplumber...")

        # Fallback: pdfplumber
        try:
            import pdfplumber

            if isinstance(file_path_or_bytes, (str, Path)):
                path = Path(file_path_or_bytes)
                if not path.exists():
                    raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
                pdf = pdfplumber.open(str(path))
            else:
                pdf = pdfplumber.open(io.BytesIO(file_path_or_bytes))

            with pdf:
                total_pages = len(pdf.pages)
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ""
                        pages_text.append(text)
                    except Exception as e:
                        self.logger.warning(f"Erro ao extrair pagina {i + 1}: {e}")
                        pages_text.append("")

                full_text = "\n\n".join(pages_text)
                if full_text.strip():
                    self.logger.info(f"PDF extraido com pdfplumber: {total_pages} paginas, {len(full_text)} caracteres")
                    return full_text

        except ImportError:
            self.logger.warning("pdfplumber nao disponivel, tentando pymupdf...")

        # Fallback: PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF

            if isinstance(file_path_or_bytes, (str, Path)):
                path = Path(file_path_or_bytes)
                if not path.exists():
                    raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
                doc = fitz.open(str(path))
            else:
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")

            total_pages = len(doc)
            pages_text = []
            for page in doc:
                try:
                    text = page.get_text() or ""
                    pages_text.append(text)
                except Exception as e:
                    self.logger.warning(f"Erro ao extrair pagina: {e}")
                    pages_text.append("")
            doc.close()

            full_text = "\n\n".join(pages_text)
            if full_text.strip():
                self.logger.info(f"PDF extraido com PyMuPDF: {total_pages} paginas, {len(full_text)} caracteres")
                return full_text

        except ImportError:
            self.logger.warning("PyMuPDF (fitz) nao disponivel.")

        raise ValueError(
            "Nenhuma biblioteca de PDF disponivel (PyPDF2, pdfplumber, PyMuPDF). "
            "Instale ao menos uma: pip install PyPDF2"
        )

    # ──────────────────────────────────────────────
    # 2. parse_edital_text - Extracao estruturada
    # ──────────────────────────────────────────────

    def parse_edital_text(self, text: str) -> EditalParseResult:
        """
        Extrai dados estruturados do texto de um edital de licitacao.

        Args:
            text: Texto completo do edital.

        Returns:
            EditalParseResult com todos os campos extraidos.
        """
        result = EditalParseResult(
            texto_completo=text,
            total_caracteres=len(text),
            parsed_at=datetime.utcnow().isoformat(),
        )

        text_lower = text.lower()

        # Extrair cada campo
        result.numero_edital = self._extract_numero_edital(text)
        result.modalidade = self._extract_modalidade(text_lower)
        result.processo_administrativo = self._extract_processo(text)
        result.objeto = self._extract_objeto(text)
        result.valor_estimado = self._extract_valor_estimado(text)
        result.data_abertura = self._extract_data_abertura(text)
        result.data_encerramento = self._extract_data_encerramento(text)
        result.criterio_julgamento = self._extract_criterio_julgamento(text_lower)
        result.orgao_nome = self._extract_orgao_nome(text)
        result.orgao_cnpj = self._extract_cnpj_orgao(text)
        result.requisitos_habilitacao = self._extract_requisitos_habilitacao(text)
        result.documentos_exigidos = self._extract_documentos_exigidos(text)
        result.itens = self.extract_items_table(text)
        result.prazo_contrato = self._extract_prazo_contrato(text)
        result.garantias = self._extract_garantias(text)
        result.penalidades = self._extract_penalidades(text)
        result.red_flags = self.detect_red_flags(text)
        result.segmento = self.classify_segment(text)

        self.logger.info(
            f"Edital parseado: {result.numero_edital or 'N/I'} | "
            f"modalidade={result.modalidade} | "
            f"itens={len(result.itens)} | "
            f"red_flags={len(result.red_flags)} | "
            f"segmento={result.segmento}"
        )

        return result

    # ──────────────────────────────────────────────
    # 3. extract_items_table - Tabela de itens
    # ──────────────────────────────────────────────

    def extract_items_table(self, text: str) -> list[EditalItem]:
        """
        Extrai tabela de itens do edital.

        Identifica padroes comuns em tabelas de editais brasileiros:
        - ITEM | DESCRICAO | QTD | UNIDADE | VALOR
        - Numeracao sequencial (1, 2, 3...)
        - Lote/Grupo com sub-itens

        Args:
            text: Texto completo do edital.

        Returns:
            Lista de EditalItem.
        """
        items: list[EditalItem] = []
        seen_numbers: set[int] = set()

        # ---- Pattern 1: Tabela estruturada ----
        # Item | Descricao | Qtd | Unid | Valor Unit | Valor Total
        # Captura linhas com numero de item seguido de campos separados por espacos/tabs/pipes
        pattern_table = re.compile(
            r"(?:^|\n)\s*"
            r"(?:item\s+)?(\d{1,4})\s*[|\t.)\-–]+\s*"  # numero do item
            r"(.{10,300}?)\s*[|\t]+\s*"  # descricao (min 10 chars)
            r"(\d+(?:[.,]\d+)?)\s*[|\t]+\s*"  # quantidade
            r"([A-Za-zÀ-ú]{1,20})\s*[|\t]*\s*"  # unidade
            r"(?:R?\$?\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?))?",  # valor unitario (opcional)
            re.IGNORECASE | re.MULTILINE,
        )

        for m in pattern_table.finditer(text):
            num = int(m.group(1))
            if num in seen_numbers or num > 9999:
                continue
            seen_numbers.add(num)
            items.append(
                EditalItem(
                    numero=num,
                    descricao=self._clean_text(m.group(2)),
                    quantidade=self._parse_decimal_br(m.group(3)),
                    unidade=m.group(4).strip().upper(),
                    valor_unitario_estimado=self._parse_decimal_br(m.group(5)) if m.group(5) else None,
                )
            )

        # ---- Pattern 2: Formato "Item X - Descricao" com valor na mesma ou proxima linha ----
        if not items:
            pattern_inline = re.compile(
                r"(?:^|\n)\s*"
                r"(?:item|lote|grupo)\s*(?:n[.ºo°]?\s*)?(\d{1,4})\s*[\-–:\.]\s*"
                r"(.{15,500}?)"
                r"(?:\n|$)",
                re.IGNORECASE | re.MULTILINE,
            )

            for m in pattern_inline.finditer(text):
                num = int(m.group(1))
                if num in seen_numbers or num > 9999:
                    continue

                desc_block = m.group(2).strip()

                # Extrair quantidade se presente
                qty = Decimal("1")
                qty_match = re.search(
                    r"(?:quantidade|qtd|qtde)[:\s]*(\d+(?:[.,]\d+)?)",
                    desc_block,
                    re.IGNORECASE,
                )
                if qty_match:
                    qty = self._parse_decimal_br(qty_match.group(1))

                # Extrair unidade
                unit = "UN"
                unit_match = re.search(
                    r"(?:unidade|unid)[:\s]*([\w]+)",
                    desc_block,
                    re.IGNORECASE,
                )
                if unit_match:
                    unit = unit_match.group(1).upper()

                # Extrair valor
                val = None
                val_match = re.search(
                    r"R\$\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
                    desc_block,
                )
                if val_match:
                    val = self._parse_valor_br(val_match.group(1))

                seen_numbers.add(num)
                items.append(
                    EditalItem(
                        numero=num,
                        descricao=self._clean_text(desc_block[:300]),
                        quantidade=qty,
                        unidade=unit,
                        valor_unitario_estimado=val,
                    )
                )

        # ---- Pattern 3: Lista numerada simples (1. Descricao / 1) Descricao) ----
        if not items:
            pattern_simple = re.compile(
                r"(?:^|\n)\s*(\d{1,3})\s*[.)]\s+"
                r"(.{20,500}?)"
                r"(?=\n\s*\d{1,3}\s*[.)]|\n\s*$|\n\s*[A-Z])",
                re.MULTILINE,
            )

            # Somente considerar se encontrar no contexto de itens/lotes
            section_match = re.search(
                r"(?:dos\s+itens|da\s+proposta|objeto|lotes|especifica[çc][ãa]o)",
                text,
                re.IGNORECASE,
            )
            if section_match:
                search_start = max(0, section_match.start() - 200)
                search_text = text[search_start:]
                for m in pattern_simple.finditer(search_text):
                    num = int(m.group(1))
                    if num in seen_numbers or num > 500:
                        continue
                    seen_numbers.add(num)
                    items.append(
                        EditalItem(
                            numero=num,
                            descricao=self._clean_text(m.group(2)),
                        )
                    )

        # Calcular valor total quando possivel
        for item in items:
            if item.valor_unitario_estimado and item.quantidade:
                item.valor_total_estimado = item.valor_unitario_estimado * item.quantidade

        items.sort(key=lambda x: x.numero)
        return items

    # ──────────────────────────────────────────────
    # 4. detect_red_flags - Deteccao de problemas
    # ──────────────────────────────────────────────

    def detect_red_flags(self, text: str) -> list[RedFlag]:
        """
        Detecta potenciais irregularidades ou pontos de atencao no edital.

        Verifica:
        - Prazo muito curto para apresentacao de propostas
        - Exigencia de marca especifica
        - Atestado com quantitativo minimo desproporcional
        - Capital social elevado
        - Restricao geografica indevida
        - Ausencia de planilha de custos
        - Clausulas restritivas de competicao

        Args:
            text: Texto completo do edital.

        Returns:
            Lista de RedFlag.
        """
        flags: list[RedFlag] = []
        text_lower = text.lower()

        # ---- 1. Prazo muito curto (< 8 dias uteis) ----
        prazo_patterns = [
            r"(\d{1,2})\s*\(?dias?\s*[uú]teis?\)?\s*(?:para|de)\s*(?:apresenta[çc][ãa]o|envio|entrega)\s*(?:d[aeo]s?\s*)?propost",
            r"prazo\s*(?:de|para)\s*(?:apresenta[çc][ãa]o|envio)\s*(?:d[aeo]s?\s*)?propost\w*[:\s]+(\d{1,2})\s*\(?dias?\s*[uú]teis?\)?",
            r"no\s*prazo\s*(?:m[ií]nimo\s*)?de\s*(\d{1,2})\s*\(?dias?\s*[uú]teis?\)?",
        ]
        for pat in prazo_patterns:
            m = re.search(pat, text_lower)
            if m:
                dias = int(m.group(1))
                if dias < 8:
                    flags.append(
                        RedFlag(
                            tipo="prazo_curto",
                            descricao=(
                                f"Prazo de {dias} dias uteis para apresentacao de propostas "
                                f"e inferior ao minimo recomendado de 8 dias uteis."
                            ),
                            severidade="alta",
                            trecho=self._extract_context(text, m.start(), 150),
                        )
                    )
                break

        # ---- 2. Exigencia de marca especifica ----
        marca_patterns = [
            r"(?:marca|fabricante)\s+(?:espec[ií]fic[ao]|exclusiv[ao]|obrigat[oó]ri[ao])\s*[:\-]?\s*([^\n]{5,80})",
            r"(?:somente|apenas|exclusivamente)\s+(?:da\s+)?marca\s+([^\n]{5,60})",
            r"dever[áa]\s+ser\s+da\s+marca\s+([^\n]{5,60})",
            r"marca\s*[:\-]\s*([A-Z][A-Za-z\s]{3,40})(?:\s|,|\.|$)",
        ]
        for pat in marca_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                # Verificar se nao e "marca ou similar/equivalente" (que e aceitavel)
                context = text[m.start() : min(m.end() + 100, len(text))].lower()
                if not re.search(r"(?:ou\s+similar|ou\s+equivalente|de\s+refer[eê]ncia)", context):
                    flags.append(
                        RedFlag(
                            tipo="marca_especifica",
                            descricao=(
                                f"Possivel exigencia de marca especifica: '{m.group(1).strip()}'. "
                                "Isso pode restringir a competitividade (Art. 41 da Lei 14.133/2021)."
                            ),
                            severidade="alta",
                            trecho=self._extract_context(text, m.start(), 150),
                        )
                    )
                break

        # ---- 3. Atestado com quantitativo minimo desproporcional ----
        atestado_patterns = [
            r"atestado\w*\s+(?:de\s+capacidade\s+)?t[eé]cnic\w*[^.]*?"
            r"(?:m[ií]nimo|no\s+m[ií]nimo|pelo\s+menos)\s+(?:de\s+)?(\d+)\s*%",
            r"(?:comprovar|demonstrar)[^.]*?(?:no\s+m[ií]nimo|m[ií]nimo\s+de)\s+(\d+)\s*%"
            r"[^.]*?atestado",
        ]
        for pat in atestado_patterns:
            m = re.search(pat, text_lower)
            if m:
                pct = int(m.group(1))
                if pct > 50:
                    flags.append(
                        RedFlag(
                            tipo="atestado_desproporcional",
                            descricao=(
                                f"Atestado de capacidade tecnica exige quantitativo minimo de {pct}%, "
                                "acima do usual (50%). Pode restringir competicao."
                            ),
                            severidade="media" if pct <= 75 else "alta",
                            trecho=self._extract_context(text, m.start(), 150),
                        )
                    )
                break

        # ---- 4. Capital social elevado ----
        capital_patterns = [
            r"capital\s+social\s+(?:m[ií]nimo|integralizado)[^.]*?"
            r"R\$\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
            r"(?:patrimônio\s+l[ií]quido|patrimonio\s+liquido)\s+(?:m[ií]nimo)?[^.]*?"
            r"R\$\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
        ]
        for pat in capital_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                valor = self._parse_valor_br(m.group(1))
                if valor and valor > Decimal("1000000"):
                    flags.append(
                        RedFlag(
                            tipo="capital_social_elevado",
                            descricao=(
                                f"Capital social/patrimonio liquido minimo de R$ {valor:,.2f} "
                                "pode ser considerado elevado e restritivo a competicao."
                            ),
                            severidade="media" if valor <= Decimal("5000000") else "alta",
                            trecho=self._extract_context(text, m.start(), 150),
                        )
                    )
                break

        # ---- 5. Restricao geografica indevida ----
        geo_patterns = [
            r"(?:sede|filial|escrit[oó]rio|domic[ií]lio)[^.]*?"
            r"(?:obrigatoriamente|necessariamente|dever[áa])\s+(?:estar\s+)?(?:localizada?|situada?|instalada?|sediada?)"
            r"[^.]*?(?:no\s+munic[ií]pio|na\s+cidade|no\s+estado|na\s+localidade)",
            r"(?:somente|apenas)\s+(?:empresas?|licitantes?)\s+(?:com\s+)?(?:sede|domicilio|domic[ií]lio)"
            r"\s+(?:no|na|em)\s+([^\n,.]{5,50})",
            r"(?:exige|exig[eê]ncia)\s+(?:de\s+)?(?:sede|filial|escrit[oó]rio)\s+(?:no|na|em)\s+",
        ]
        for pat in geo_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                flags.append(
                    RedFlag(
                        tipo="restricao_geografica",
                        descricao=(
                            "Possivel restricao geografica indevida para participacao. "
                            "Exigencia de sede/filial em localidade especifica pode violar "
                            "o principio da competitividade."
                        ),
                        severidade="alta",
                        trecho=self._extract_context(text, m.start(), 150),
                    )
                )
                break

        # ---- 6. Ausencia de planilha de custos ----
        is_servico_continuado = bool(
            re.search(
                r"servi[çc]os?\s+(?:de\s+natureza\s+)?continu(?:ad)?[ao]",
                text_lower,
            )
        )
        has_planilha = bool(
            re.search(
                r"planilha\s+(?:de\s+)?(?:custos?|forma[çc][ãa]o\s+de\s+pre[çc]os?|composi[çc][ãa]o)",
                text_lower,
            )
        )
        if is_servico_continuado and not has_planilha:
            flags.append(
                RedFlag(
                    tipo="ausencia_planilha_custos",
                    descricao=(
                        "Edital de servicos continuados sem referencia a planilha de custos "
                        "e formacao de precos. A planilha e obrigatoria para servicos continuados "
                        "com dedicacao exclusiva de mao de obra."
                    ),
                    severidade="alta",
                    trecho=None,
                )
            )

        # ---- 7. Exigencia de visita tecnica obrigatoria ----
        visita_match = re.search(
            r"visita\s+t[eé]cnica[^.]*?obrigat[oó]ri[ao]",
            text_lower,
        )
        if visita_match:
            # Lei 14.133 permite exigir, mas nao como obrigatoria — pode ser substituida
            # por declaracao
            has_declaracao_subst = bool(
                re.search(
                    r"(?:declara[çc][ãa]o|atestado)[^.]*?(?:substitui|em\s+substitui|dispensar)\w*"
                    r"[^.]*?visita",
                    text_lower,
                )
            )
            if not has_declaracao_subst:
                flags.append(
                    RedFlag(
                        tipo="visita_tecnica_obrigatoria",
                        descricao=(
                            "Visita tecnica obrigatoria sem opcao de declaracao substitutiva. "
                            "A Lei 14.133/2021 (Art. 63, §2o) permite substituicao por declaracao."
                        ),
                        severidade="media",
                        trecho=self._extract_context(text, visita_match.start(), 150),
                    )
                )

        # ---- 8. Prazo de pagamento excessivo ----
        pagamento_match = re.search(
            r"(?:pagamento|pagar)[^.]*?(?:em\s+at[eé]|no\s+prazo\s+de|at[eé])\s+(\d+)\s+dias",
            text_lower,
        )
        if pagamento_match:
            dias_pgto = int(pagamento_match.group(1))
            if dias_pgto > 30:
                flags.append(
                    RedFlag(
                        tipo="prazo_pagamento_excessivo",
                        descricao=(
                            f"Prazo de pagamento de {dias_pgto} dias e superior ao padrao de 30 dias. "
                            "Isso afeta o fluxo de caixa e pode indicar condicao desfavoravel."
                        ),
                        severidade="media" if dias_pgto <= 60 else "alta",
                        trecho=self._extract_context(text, pagamento_match.start(), 150),
                    )
                )

        # ---- 9. Indice de reajuste nao especificado ----
        is_contrato_longo = bool(
            re.search(
                r"(?:vig[eê]ncia|prazo)[^.]*?(?:12|24|36|48|60)\s*meses",
                text_lower,
            )
        )
        has_reajuste = bool(
            re.search(
                r"(?:reajuste|reajustamento|repactua[çc][ãa]o)[^.]*?"
                r"(?:IPCA|INPC|IGP-?M|[ií]ndice|anual)",
                text,
                re.IGNORECASE,
            )
        )
        if is_contrato_longo and not has_reajuste:
            flags.append(
                RedFlag(
                    tipo="sem_clausula_reajuste",
                    descricao=(
                        "Contrato com vigencia superior a 12 meses sem clausula clara de "
                        "reajuste/repactuacao ou sem indicacao de indice (IPCA, IGP-M, etc.)."
                    ),
                    severidade="media",
                    trecho=None,
                )
            )

        return flags

    # ──────────────────────────────────────────────
    # 5. classify_segment - Classificacao do edital
    # ──────────────────────────────────────────────

    def classify_segment(self, text: str) -> str:
        """
        Classifica o segmento principal do edital.

        Retorna:
            - "vigilancia_armada"
            - "vigilancia_desarmada"
            - "seguranca_eletronica"
            - "portaria_presencial"
            - "portaria_remota"
            - "limpeza"
            - "jardinagem"
            - "facilities"
            - "misto"
            - "nao_identificado"
        """
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for segmento, keywords in SEGMENTOS_KEYWORDS.items():
            count = 0
            for kw in keywords:
                occurrences = text_lower.count(kw)
                count += occurrences
            if count > 0:
                scores[segmento] = count

        if not scores:
            return "nao_identificado"

        sorted_segments = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Se houver mais de um segmento com ocorrencias significativas, e misto
        if len(sorted_segments) >= 2:
            top = sorted_segments[0][1]
            second = sorted_segments[1][1]
            # Se o segundo tem ao menos 30% das ocorrencias do primeiro, e misto
            if second >= top * 0.3:
                return "misto"

        return sorted_segments[0][0]

    # ──────────────────────────────────────────────
    # Metodo de conveniencia: parse completo
    # ──────────────────────────────────────────────

    def parse_pdf_completo(self, file_path_or_bytes: str | bytes | Path) -> EditalParseResult:
        """
        Metodo de conveniencia: extrai texto do PDF e faz o parse completo.

        Args:
            file_path_or_bytes: Caminho do arquivo PDF ou bytes.

        Returns:
            EditalParseResult completo.
        """
        text = self.parse_pdf(file_path_or_bytes)
        result = self.parse_edital_text(text)
        return result

    # ──────────────────────────────────────────────
    # Metodos privados de extracao
    # ──────────────────────────────────────────────

    def _extract_numero_edital(self, text: str) -> str | None:
        """Extrai o numero do edital."""
        patterns = [
            # PREGÃO ELETRÔNICO Nº 001/2026
            r"(?:PREG[ÃA]O\s+ELETR[ÔO]NICO|PREG[ÃA]O\s+PRESENCIAL|CONCORR[ÊE]NCIA|"
            r"TOMADA\s+DE\s+PRE[ÇC]OS?|CONVITE|LEIL[ÃA]O|RDC|DISPENSA|"
            r"CONCORR[ÊE]NCIA\s+ELETR[ÔO]NICA|DI[ÁA]LOGO\s+COMPETITIVO)\s*"
            r"(?:N[.ºo°]?\s*|n[.ºo°]?\s*)"
            r"(\d{1,5}\s*/\s*\d{4}(?:\s*-\s*\w+)?)",
            # Edital Nº 001/2026
            r"EDITAL\s+(?:DE\s+LICITA[ÇC][ÃA]O\s+)?N[.ºo°]?\s*(\d{1,5}\s*/\s*\d{4}(?:\s*-\s*\w+)?)",
            # PE 001/2026 ou PE-001/2026
            r"(?:PE|PP|CC|TP|CV|DL|IN)\s*[\-]?\s*(?:N[.ºo°]?\s*)?(\d{1,5}\s*/\s*\d{4})",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                # Reconstruir numero completo com modalidade se possivel
                full_match = text[m.start() : m.end()].strip()
                return self._clean_text(full_match)

        return None

    def _extract_modalidade(self, text_lower: str) -> str | None:
        """Extrai a modalidade da licitacao."""
        for key, normalized in MODALIDADES.items():
            if key in text_lower:
                return normalized
        return None

    def _extract_processo(self, text: str) -> str | None:
        """Extrai o numero do processo administrativo."""
        patterns = [
            r"(?:processo\s+(?:administrativo|licitat[oó]rio)?)\s*(?:n[.ºo°]?\s*)?"
            r"(\d{1,10}[./-]\d{1,10}[./-]?\d{0,10})",
            r"(?:PAD|PA|PROC)\s*(?:n[.ºo°]?\s*)?(\d{1,10}[./-]\d{1,10}[./-]?\d{0,10})",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_objeto(self, text: str) -> str | None:
        """Extrai a descricao do objeto da licitacao."""
        patterns = [
            # DO OBJETO / OBJETO: ... (secao tipica de editais)
            r"(?:DO\s+OBJETO|OBJETO\s+DA\s+LICITA[ÇC][ÃA]O|CL[ÁA]USULA\s+PRIMEIRA\s*[\-–:]\s*"
            r"(?:DO\s+)?OBJETO)\s*[\-–:.\n]\s*"
            r"(?:\d+[.\d]*\s*[\-–.]?\s*)?"  # possivel numeracao (1.1 -)
            r"(.{30,1000}?)(?:\n\s*\n|\n\s*\d+[.\s])",
            # Constitui objeto ... / O objeto do presente ...
            r"(?:constitui\s+objeto|o\s+objeto\s+(?:do\s+presente|desta))[^.]*?"
            r"(?:a\s+contrata[çc][ãa]o|o\s+registro|a\s+presta[çc][ãa]o|a\s+aquisi[çc][ãa]o)"
            r"(.{20,800}?)(?:\.\s*\n|\n\s*\n)",
            # Contratacao de ...
            r"(?:contrata[çc][ãa]o\s+de\s+(?:empresa|pessoa\s+jur[ií]dica)\s+(?:especializada\s+)?(?:para|em)\s+)"
            r"(.{20,500}?)(?:\.\s*\n|\n\s*\n)",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
            if m:
                obj = m.group(1) if m.lastindex else m.group(0)
                obj = self._clean_text(obj)
                # Limitar tamanho
                if len(obj) > 500:
                    obj = obj[:500] + "..."
                return obj

        return None

    def _extract_valor_estimado(self, text: str) -> Decimal | None:
        """Extrai o valor estimado/total da licitacao."""
        patterns = [
            # Valor total/global/estimado: R$ 1.234.567,89
            r"(?:valor\s+(?:total|global|estimado|m[áa]ximo)\s*(?:da\s+contrata[çc][ãa]o|"
            r"da\s+licita[çc][ãa]o|do\s+edital|anual|mensal)?)\s*"
            r"(?:[eé]|de)?\s*[:.]?\s*(?:R\$|BRL)\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
            # Valor total estimado: R$ ... (with colon)
            r"(?:valor\s+(?:total|global|estimado|m[áa]ximo))\s*(?:estimad[oa])?\s*"
            r"[:.]?\s*(?:R\$|BRL)\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
            # R$ 1.234.567,89 (valor global/total/estimado)
            r"(?:R\$|BRL)\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)\s*"
            r"\(?\s*(?:valor\s+)?(?:total|global|estimado)",
            # Orcamento estimado em R$ ...
            r"(?:or[çc]amento\s+(?:estimado|previsto|b[áa]sico))[^.]*?"
            r"(?:R\$|BRL)\s*([\d.,]+(?:\.\d{3})*(?:,\d{1,2})?)",
        ]

        best_value = None
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = self._parse_valor_br(m.group(1))
                if val and val > Decimal("0"):
                    if best_value is None or val > best_value:
                        best_value = val

        return best_value

    def _extract_data_abertura(self, text: str) -> str | None:
        """Extrai a data de abertura da sessao publica."""
        patterns = [
            # Abertura: 15/03/2026 às 09:00
            r"(?:abertura|sess[ãa]o\s+p[úu]blica|data\s+(?:da\s+)?sess[ãa]o|"
            r"in[ií]cio\s+(?:do\s+)?acolhimento|recebimento\s+(?:das?\s+)?propost)"
            r"[^.]*?(\d{2}/\d{2}/\d{4})\s*(?:[àa]s?\s*)?(\d{2}[h:]\d{2})?",
            # Dia 15 de março de 2026
            r"(?:abertura|sess[ãa]o)[^.]*?"
            r"(?:dia\s+)?(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\s*"
            r"(?:[àa]s?\s*)?(\d{2}[h:]\d{2})?",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                groups = m.groups()
                if "/" in (groups[0] or ""):
                    # Formato dd/mm/yyyy
                    result = groups[0]
                    if groups[1]:
                        hora = groups[1].replace("h", ":")
                        result += f" {hora}"
                    return result
                else:
                    # Formato "dia de mes de ano"
                    try:
                        dia = groups[0]
                        mes_nome = groups[1]
                        ano = groups[2]
                        mes_num = self._mes_para_numero(mes_nome)
                        if mes_num:
                            result = f"{dia.zfill(2)}/{mes_num}/{ano}"
                            if groups[3]:
                                hora = groups[3].replace("h", ":")
                                result += f" {hora}"
                            return result
                    except (IndexError, ValueError):
                        pass

        return None

    def _extract_data_encerramento(self, text: str) -> str | None:
        """Extrai a data de encerramento das propostas."""
        patterns = [
            r"(?:encerramento|fim|t[eé]rmino|prazo\s+final)[^.]*?(?:propost|envio|recebimento)"
            r"[^.]*?(\d{2}/\d{2}/\d{4})\s*(?:[àa]s?\s*)?(\d{2}[h:]\d{2})?",
            r"(?:propost\w+|proposta)[^.]*?(?:at[eé]|encerr\w+|prazo\s+final)[^.]*?"
            r"(\d{2}/\d{2}/\d{4})\s*(?:[àa]s?\s*)?(\d{2}[h:]\d{2})?",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result = m.group(1)
                if m.group(2):
                    hora = m.group(2).replace("h", ":")
                    result += f" {hora}"
                return result

        return None

    def _extract_criterio_julgamento(self, text_lower: str) -> str | None:
        """Extrai o criterio de julgamento."""
        # Buscar em contexto proximo a "criterio de julgamento" / "tipo de julgamento"
        context_match = re.search(
            r"(?:crit[eé]rio\s+de\s+julgamento|tipo\s+de\s+julgamento|modo\s+de\s+disputa)"
            r"[^.]{0,100}",
            text_lower,
        )
        search_text = context_match.group(0) if context_match else text_lower

        for criterio in CRITERIOS_JULGAMENTO:
            if criterio in search_text:
                return criterio.title()

        # Buscar em todo o texto se nao encontrou no contexto
        if context_match:
            for criterio in CRITERIOS_JULGAMENTO:
                if criterio in text_lower:
                    return criterio.title()

        return None

    def _extract_orgao_nome(self, text: str) -> str | None:
        """Extrai o nome do orgao licitante."""
        patterns = [
            # PREAMBULO: orgao geralmente esta nas primeiras linhas
            r"^(.{0,500}?)(?:torna\s+p[úu]blico|faz\s+saber|realiza\w*)",
            # Orgao/Entidade: ...
            r"(?:[oó]rg[ãa]o|entidade|[oó]rg[ãa]o\s+licitante|contratante)"
            r"\s*[:\-]\s*(.{10,200}?)(?:\n|CNPJ|,\s*inscrit)",
            # Prefeitura/Secretaria/Ministério/Estado/etc
            r"((?:PREFEITURA|SECRETARIA|MINIST[ÉE]RIO|ESTADO|MUNIC[ÍI]PIO|"
            r"TRIBUNAL|C[ÂA]MARA|UNIVERSIDADE|INSTITUTO|FUNDA[ÇC][ÃA]O|"
            r"EMPRESA|COMPANHIA|AUTARQUIA|AG[ÊE]NCIA|DEPARTAMENTO|DIRETORIA)"
            r"[^.\n]{5,150}?)(?:\n|\.\s|,\s*(?:CNPJ|inscrit))",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
            if m:
                # Primeiro grupo que tenha conteudo
                for g in range(1, m.lastindex + 1 if m.lastindex else 2):
                    candidate = m.group(g)
                    if candidate and len(candidate.strip()) > 10:
                        return self._clean_text(candidate)[:200]

        return None

    def _extract_cnpj_orgao(self, text: str) -> str | None:
        """Extrai o CNPJ do orgao licitante."""
        # CNPJ padrao brasileiro: XX.XXX.XXX/XXXX-XX
        cnpj_pattern = r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"

        # Buscar CNPJ proximo a "orgao", "contratante", "licitante"
        context_match = re.search(
            r"(?:[oó]rg[ãa]o|contratante|licitante|entidade)[^.]{0,200}?" + cnpj_pattern,
            text,
            re.IGNORECASE,
        )
        if context_match:
            return context_match.group(1)

        # Buscar primeiro CNPJ (geralmente e do orgao, no preambulo)
        first_cnpj = re.search(cnpj_pattern, text[:3000])
        if first_cnpj:
            return first_cnpj.group(1)

        return None

    def _extract_requisitos_habilitacao(self, text: str) -> list[RequisitoHabilitacao]:
        """Extrai os requisitos de habilitacao do edital."""
        requisitos: list[RequisitoHabilitacao] = []

        # Encontrar a secao de habilitacao
        hab_section = self._extract_section(
            text,
            start_patterns=[
                r"(?:DA\s+)?HABILITA[ÇC][ÃA]O",
                r"DOCUMENTOS?\s+(?:DE|PARA)\s+HABILITA[ÇC][ÃA]O",
                r"EXIG[ÊE]NCIAS?\s+(?:DE|PARA)\s+HABILITA[ÇC][ÃA]O",
            ],
            max_length=15000,
        )

        if not hab_section:
            return requisitos

        # Categorias e seus patterns
        categorias = {
            "juridica": {
                "header_patterns": [
                    r"habilita[çc][ãa]o\s+jur[ií]dica",
                    r"regularidade\s+jur[ií]dica",
                ],
                "item_patterns": [
                    r"registro\s+comercial",
                    r"ato\s+constitutivo",
                    r"estatuto\s+social",
                    r"contrato\s+social",
                    r"inscri[çc][ãa]o\s+no\s+registro",
                    r"c[eé]dula\s+de\s+identidade",
                    r"decreto\s+de\s+autoriza[çc][ãa]o",
                    r"prova\s+de\s+inscri[çc][ãa]o\s+(?:no\s+)?(?:cadastro|CNPJ)",
                    r"certid[ãa]o\s+simplificada\s+da\s+junta",
                    r"autoriza[çc][ãa]o\s+(?:de\s+)?funcionamento",
                    r"alvara",
                ],
            },
            "fiscal": {
                "header_patterns": [
                    r"regularidade\s+fiscal",
                    r"habilita[çc][ãa]o\s+fiscal",
                    r"fiscal\s+e\s+trabalhista",
                ],
                "item_patterns": [
                    r"(?:CND|certid[ãa]o\s+negativa)\s+(?:de\s+)?d[eé]bitos?\s+(?:federais?|tribut)",
                    r"FGTS",
                    r"certid[ãa]o\s+(?:negativa|de\s+regularidade)\s+(?:do\s+)?INSS",
                    r"(?:certid[ãa]o|prova)\s+(?:de\s+)?regularidade\s+(?:com\s+a?\s*)?Fazenda",
                    r"CNDT|certid[ãa]o\s+(?:negativa\s+)?(?:de\s+)?d[eé]bitos?\s+trabalhist",
                    r"inscri[çc][ãa]o\s+(?:no\s+)?cadastro\s+(?:de\s+)?contribuintes?\s+(?:estadual|municipal)",
                    r"prova\s+de\s+regularidade\s+(?:para\s+com\s+a?\s*)?(?:Fazenda|tribut)",
                ],
            },
            "tecnica": {
                "header_patterns": [
                    r"qualifica[çc][ãa]o\s+t[eé]cnica",
                    r"habilita[çc][ãa]o\s+t[eé]cnica",
                    r"capacidade\s+t[eé]cnica",
                ],
                "item_patterns": [
                    r"atestado\s+(?:de\s+)?capacidade\s+t[eé]cnica",
                    r"registro\s+(?:no\s+)?(?:CREA|CRA|CRQ|CAU|CRM)",
                    r"autoriza[çc][ãa]o\s+(?:da\s+)?(?:Pol[ií]cia\s+Federal|PF|DELESP)",
                    r"certifica[çc][ãa]o\s+(?:ISO|ABNT|INMETRO)",
                    r"curso\s+de\s+forma[çc][ãa]o\s+de\s+vigilante",
                    r"responsavel\s+t[eé]cnico",
                    r"acervo\s+t[eé]cnico",
                    r"atestado\w*\s+(?:que\s+)?comprov\w+\s+(?:a\s+)?execu[çc][ãa]o",
                    r"experi[eê]ncia\s+(?:anterior|pr[eé]via|m[ií]nima|comprovada)",
                ],
            },
            "economica": {
                "header_patterns": [
                    r"qualifica[çc][ãa]o\s+econ[oô]mico[\-\s]?financeira",
                    r"habilita[çc][ãa]o\s+econ[oô]mica",
                    r"capacidade\s+econ[oô]mica",
                ],
                "item_patterns": [
                    r"balan[çc]o\s+patrimonial",
                    r"demonstra[çc][oõ]es?\s+cont[aá]beis",
                    r"certid[ãa]o\s+negativa\s+(?:de\s+)?fal[eê]ncia",
                    r"capital\s+social\s+(?:m[ií]nimo|integralizado)",
                    r"patrim[oô]nio\s+l[ií]quido",
                    r"[ií]ndice\s+(?:de\s+)?(?:liquidez|endividamento|solvencia)",
                    r"garantia\s+(?:de\s+)?proposta",
                    r"seguro[\-\s]?garantia",
                ],
            },
        }

        for categoria, config in categorias.items():
            # Verificar se a secao menciona esta categoria
            for hp in config["header_patterns"]:
                if re.search(hp, hab_section, re.IGNORECASE):
                    break

            # Buscar itens especificos
            for ip in config["item_patterns"]:
                m = re.search(ip, hab_section, re.IGNORECASE)
                if m:
                    # Extrair a linha/frase completa como descricao
                    start = m.start()
                    # Voltar ao inicio da linha/item
                    line_start = hab_section.rfind("\n", max(0, start - 300), start)
                    if line_start == -1:
                        line_start = max(0, start - 50)
                    # Avancar ate o fim da frase
                    line_end = hab_section.find("\n", m.end())
                    if line_end == -1 or line_end - start > 500:
                        line_end = min(start + 500, len(hab_section))

                    desc = self._clean_text(hab_section[line_start:line_end])
                    if len(desc) > 10:
                        requisitos.append(
                            RequisitoHabilitacao(
                                categoria=categoria,
                                descricao=desc[:500],
                                obrigatorio=True,
                            )
                        )

        return requisitos

    def _extract_documentos_exigidos(self, text: str) -> list[str]:
        """Extrai lista de documentos exigidos."""
        documentos: list[str] = []
        seen: set[str] = set()

        # Patterns de documentos comuns em licitacoes
        doc_patterns = [
            r"(?:certid[ãa]o\s+(?:negativa|positiva\s+com\s+efeito\s+de\s+negativa)\s+[^;\n.]{10,200})",
            r"(?:atestado\s+(?:de\s+capacidade\s+)?t[eé]cnic[ao]\s+[^;\n.]{10,200})",
            r"(?:contrato\s+social\s+[^;\n.]{5,100})",
            r"(?:balan[çc]o\s+patrimonial\s+[^;\n.]{5,150})",
            r"(?:declara[çc][ãa]o\s+(?:de\s+)?[^;\n.]{10,200})",
            r"(?:comprovante\s+de\s+inscri[çc][ãa]o\s+[^;\n.]{10,150})",
            r"(?:prova\s+de\s+regularidade\s+[^;\n.]{10,200})",
            r"(?:registro\s+(?:no\s+)?(?:CREA|CRA|CAU|CRQ)\s*[^;\n.]{0,100})",
            r"(?:autoriza[çc][ãa]o\s+(?:de\s+funcionamento|da\s+Pol[ií]cia|da\s+PF)\s*[^;\n.]{0,150})",
            r"(?:alvar[áa]\s+(?:de\s+)?(?:funcionamento|localiza[çc][ãa]o)\s*[^;\n.]{0,100})",
            r"(?:carta\s+de\s+(?:fian[çc]a|cr[eé]dito)\s*[^;\n.]{0,100})",
            r"(?:seguro[\-\s]?garantia\s*[^;\n.]{0,100})",
            r"(?:proposta\s+(?:de\s+)?pre[çc]os?\s*[^;\n.]{0,150})",
            r"(?:planilha\s+(?:de\s+)?(?:custos?|composi[çc][ãa]o|forma[çc][ãa]o)\s*[^;\n.]{0,150})",
            r"(?:CNDT\s*[^;\n.]{0,100})",
            r"(?:CRF\s*(?:do\s+FGTS)?\s*[^;\n.]{0,100})",
        ]

        for pat in doc_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                doc = self._clean_text(m.group(0))
                doc_key = doc.lower()[:60]
                if doc_key not in seen and len(doc) > 10:
                    seen.add(doc_key)
                    documentos.append(doc[:300])

        return documentos

    def _extract_prazo_contrato(self, text: str) -> str | None:
        """Extrai o prazo de vigencia do contrato."""
        patterns = [
            # Vigencia de 12 (doze) meses
            r"(?:vig[eê]ncia|dura[çc][ãa]o|prazo\s+(?:do\s+)?contrat\w*)"
            r"[^.]{0,100}?(\d+)\s*\(?\s*\w+\s*\)?\s*(?:meses|anos?|dias?)",
            # 12 meses de vigencia / contados da assinatura
            r"(\d+)\s*\(?\s*\w+\s*\)?\s*(?:meses|anos?)\s*"
            r"(?:de\s+)?(?:vig[eê]ncia|dura[çc][ãa]o|contad[oa]s?)",
            # Vigencia: dd/mm/yyyy a dd/mm/yyyy
            r"vig[eê]ncia[^.]*?(\d{2}/\d{2}/\d{4})\s*(?:a|at[eé]|[àa])\s*(\d{2}/\d{2}/\d{4})",
        ]

        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                # Extrair contexto completo
                start = max(0, m.start() - 20)
                end = min(len(text), m.end() + 50)
                return self._clean_text(text[start:end])

        return None

    def _extract_garantias(self, text: str) -> list[str]:
        """Extrai exigencias de garantia do edital."""
        garantias: list[str] = []

        # Encontrar secao de garantias
        section = self._extract_section(
            text,
            start_patterns=[
                r"(?:DA\s+)?GARANTIA",
                r"GARANTIA\s+(?:DE\s+EXECU[ÇC][ÃA]O|CONTRATUAL)",
            ],
            max_length=5000,
        )

        search_text = section if section else text

        patterns = [
            r"garantia\s+(?:de\s+)?execu[çc][ãa]o[^.]*?(\d+)\s*%\s*[^.]{0,100}",
            r"garantia\s+contratual[^.]*?(\d+)\s*%\s*[^.]{0,100}",
            r"cau[çc][ãa]o\s+(?:em\s+)?(?:dinheiro|t[ií]tulos?)[^.]{0,150}",
            r"seguro[\-\s]?garantia[^.]{0,150}",
            r"fian[çc]a\s+banc[aá]ria[^.]{0,150}",
            r"garantia\s+(?:de\s+)?proposta[^.]{0,150}",
        ]

        seen = set()
        for pat in patterns:
            for m in re.finditer(pat, search_text, re.IGNORECASE):
                gar = self._clean_text(m.group(0))
                key = gar.lower()[:50]
                if key not in seen and len(gar) > 10:
                    seen.add(key)
                    garantias.append(gar[:300])

        return garantias

    def _extract_penalidades(self, text: str) -> list[str]:
        """Extrai clausulas de penalidades."""
        penalidades: list[str] = []

        section = self._extract_section(
            text,
            start_patterns=[
                r"(?:DAS?\s+)?(?:SAN[ÇC][ÕO]ES|PENALIDADES)",
                r"(?:DAS?\s+)?INFRA[ÇC][ÕO]ES\s+E\s+SAN[ÇC][ÕO]ES",
            ],
            max_length=10000,
        )

        search_text = section if section else text

        patterns = [
            r"(?:multa\s+(?:de\s+)?(?:morat[oó]ria|compensat[oó]ria|di[aá]ria)?[^.]{0,200}?(?:\d+[.,]?\d*\s*%))[^.]{0,100}",
            r"(?:advert[eê]ncia)[^.]{0,200}",
            r"(?:suspens[ãa]o\s+(?:tempor[aá]ria)?[^.]{0,200})",
            r"(?:declara[çc][ãa]o\s+de\s+inidoneidade[^.]{0,200})",
            r"(?:impedimento\s+de\s+licitar[^.]{0,200})",
            r"(?:multa\s+de\s+)(\d+[.,]?\d*\s*%[^.]{0,150})",
        ]

        seen = set()
        for pat in patterns:
            for m in re.finditer(pat, search_text, re.IGNORECASE):
                pen = self._clean_text(m.group(0))
                key = pen.lower()[:50]
                if key not in seen and len(pen) > 10:
                    seen.add(key)
                    penalidades.append(pen[:400])

        return penalidades

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _extract_section(
        self,
        text: str,
        start_patterns: list[str],
        max_length: int = 10000,
    ) -> str | None:
        """Extrai uma secao do edital baseada em patterns de cabecalho."""
        for pat in start_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                start = m.start()
                end = min(start + max_length, len(text))
                return text[start:end]
        return None

    def _extract_context(self, text: str, position: int, chars: int = 150) -> str:
        """Extrai contexto ao redor de uma posicao no texto."""
        start = max(0, position - 30)
        end = min(len(text), position + chars)
        return self._clean_text(text[start:end])

    def _clean_text(self, text: str) -> str:
        """Limpa texto removendo espacos extras e quebras de linha desnecessarias."""
        if not text:
            return ""
        # Substituir quebras de linha por espaco
        text = re.sub(r"[\n\r]+", " ", text)
        # Remover espacos multiplos
        text = re.sub(r"\s{2,}", " ", text)
        # Remover numeracao no inicio (ex: "1.1 -", "a)")
        text = re.sub(r"^\s*\d+[.\d]*\s*[\-–.)\]]\s*", "", text)
        return text.strip()

    def _parse_valor_br(self, valor_str: str) -> Decimal | None:
        """
        Converte valor em formato brasileiro (1.234.567,89) para Decimal.
        """
        if not valor_str:
            return None
        try:
            # Remover espacos
            clean = valor_str.strip()
            # Formato BR: pontos sao separadores de milhar, virgula e decimal
            # Verificar se tem virgula (formato BR) ou apenas pontos
            if "," in clean:
                # Remover pontos de milhar, trocar virgula por ponto
                clean = clean.replace(".", "").replace(",", ".")
            else:
                # Se tem mais de um ponto, sao separadores de milhar
                if clean.count(".") > 1:
                    clean = clean.replace(".", "")
                # Se tem exatamente um ponto, pode ser decimal (verificar posicao)
                elif "." in clean:
                    parts = clean.split(".")
                    if len(parts[1]) == 3:
                        # Provavelmente separador de milhar (ex: 1.000)
                        clean = clean.replace(".", "")
            return Decimal(clean)
        except (InvalidOperation, ValueError):
            return None

    def _parse_decimal_br(self, value: str) -> Decimal:
        """Parse simples de decimal em formato BR."""
        if not value:
            return Decimal("1")
        try:
            clean = value.strip().replace(".", "").replace(",", ".")
            return Decimal(clean)
        except (InvalidOperation, ValueError):
            return Decimal("1")

    def _mes_para_numero(self, mes_nome: str) -> str | None:
        """Converte nome do mes para numero (01-12)."""
        meses = {
            "janeiro": "01",
            "fevereiro": "02",
            "marco": "03",
            "março": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }
        return meses.get(mes_nome.lower().strip())
