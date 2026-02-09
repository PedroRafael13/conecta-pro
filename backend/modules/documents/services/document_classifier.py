"""
Document Classifier Service.

Responsavel pela classificacao automatica de tipos de documentos
usando regras, keywords e machine learning.
"""

import contextlib
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from ..models.document import DocumentType
from ..models.extraction_template import ExtractionTemplate
from ..models.ocr_result import OCRResult

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Resultado da classificacao."""

    document_type: DocumentType
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    alternative_types: list[tuple[DocumentType, float]] = field(default_factory=list)
    template_id: str | None = None


@dataclass
class ClassificationRule:
    """Regra de classificacao."""

    document_type: DocumentType
    keywords: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    required_keywords: list[str] = field(default_factory=list)
    excluded_keywords: list[str] = field(default_factory=list)
    min_keyword_matches: int = 1
    weight: float = 1.0


@dataclass
class ClassifierConfig:
    """Configuracao do classificador."""

    min_confidence: float = 0.5
    use_ml_model: bool = False
    ml_model_path: str | None = None
    fallback_type: DocumentType = DocumentType.DESCONHECIDO


class DocumentClassifier:
    """
    Classificador de documentos.

    Identifica o tipo de documento usando:
    - Palavras-chave
    - Padroes regex
    - Templates conhecidos
    - ML (opcional)
    """

    # Regras de classificacao por tipo de documento
    DEFAULT_RULES: list[ClassificationRule] = [
        # Boleto
        ClassificationRule(
            document_type=DocumentType.BOLETO,
            keywords=[
                "boleto",
                "codigo de barras",
                "linha digitavel",
                "valor do documento",
                "vencimento",
                "cedente",
                "sacado",
                "nosso numero",
                "pagavel em qualquer banco",
                "ficha de compensacao",
            ],
            patterns=[
                r"\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\s+\d\s+\d{14}",
                r"banco\s+\d{3}",
            ],
            min_keyword_matches=3,
            weight=1.2,
        ),
        # NFe
        ClassificationRule(
            document_type=DocumentType.NFE,
            keywords=[
                "nota fiscal",
                "nfe",
                "danfe",
                "chave de acesso",
                "icms",
                "ipi",
                "cfop",
                "natureza da operacao",
                "destinatario",
                "emitente",
                "protocolo de autorizacao",
            ],
            patterns=[
                r"\d{44}",  # Chave NFe
                r"nf[-.e]?\s*\d+",
                r"serie\s*\d+",
            ],
            required_keywords=["nota fiscal", "nfe", "danfe"],
            min_keyword_matches=3,
            weight=1.3,
        ),
        # NFSe
        ClassificationRule(
            document_type=DocumentType.NFSE,
            keywords=[
                "nota fiscal de servico",
                "nfs-e",
                "nfse",
                "iss",
                "servico prestado",
                "tomador",
                "prestador",
                "rps",
                "inss",
            ],
            patterns=[
                r"nfs-?e?\s*\d+",
                r"iss\s*[\d.,]+",
            ],
            min_keyword_matches=2,
            weight=1.2,
        ),
        # Fatura
        ClassificationRule(
            document_type=DocumentType.FATURA,
            keywords=[
                "fatura",
                "invoice",
                "valor total",
                "vencimento",
                "cliente",
                "referencia",
                "descricao",
                "quantidade",
                "preco unitario",
            ],
            min_keyword_matches=3,
            weight=1.0,
        ),
        # Recibo
        ClassificationRule(
            document_type=DocumentType.RECIBO,
            keywords=[
                "recibo",
                "receipt",
                "recebi de",
                "recebemos de",
                "a importancia de",
                "referente",
                "quitacao",
            ],
            min_keyword_matches=2,
            weight=1.0,
        ),
        # CNH
        ClassificationRule(
            document_type=DocumentType.CNH,
            keywords=[
                "carteira nacional de habilitacao",
                "cnh",
                "habilitacao",
                "categoria",
                "permissao",
                "detran",
                "condutor",
                "1 habilitacao",
                "validade",
            ],
            patterns=[
                r"registro\s*\d{9,11}",
                r"cat\s*[abcde]{1,5}",
            ],
            min_keyword_matches=3,
            weight=1.2,
        ),
        # RG
        ClassificationRule(
            document_type=DocumentType.RG,
            keywords=[
                "registro geral",
                "identidade",
                "carteira de identidade",
                "cedula de identidade",
                "ssp",
                "secretaria de seguranca",
                "filiacao",
                "naturalidade",
                "data nascimento",
            ],
            patterns=[
                r"\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?[0-9x]",
            ],
            min_keyword_matches=2,
            weight=1.1,
        ),
        # CPF
        ClassificationRule(
            document_type=DocumentType.CPF,
            keywords=[
                "cadastro de pessoa fisica",
                "cpf",
                "receita federal",
                "comprovante de inscricao",
            ],
            patterns=[
                r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}",
            ],
            required_keywords=["cpf"],
            min_keyword_matches=2,
            weight=1.0,
        ),
        # Holerite
        ClassificationRule(
            document_type=DocumentType.HOLERITE,
            keywords=[
                "holerite",
                "contracheque",
                "demonstrativo de pagamento",
                "salario",
                "proventos",
                "descontos",
                "inss",
                "irrf",
                "fgts",
                "liquido a receber",
                "base de calculo",
            ],
            patterns=[
                r"competencia\s*\d{2}/\d{4}",
                r"salario\s*base",
            ],
            min_keyword_matches=4,
            weight=1.2,
        ),
        # Contrato
        ClassificationRule(
            document_type=DocumentType.CONTRATO,
            keywords=[
                "contrato",
                "contratante",
                "contratada",
                "clausula",
                "objeto",
                "partes",
                "vigencia",
                "rescisao",
                "assinatura",
                "testemunhas",
            ],
            min_keyword_matches=4,
            weight=1.0,
        ),
        # Comprovante de Endereco
        ClassificationRule(
            document_type=DocumentType.COMPROVANTE_ENDERECO,
            keywords=[
                "comprovante de endereco",
                "comprovante de residencia",
                "endereco",
                "cep",
                "bairro",
                "cidade",
                "estado",
                "uf",
            ],
            min_keyword_matches=4,
            weight=0.8,
        ),
        # Conta de Luz
        ClassificationRule(
            document_type=DocumentType.CONTA_LUZ,
            keywords=[
                "energia eletrica",
                "conta de luz",
                "kwh",
                "consumo",
                "leitura anterior",
                "leitura atual",
                "tarifa",
                "iluminacao publica",
                "bandeira",
                "distribuidora",
            ],
            patterns=[
                r"\d+\s*kwh",
            ],
            min_keyword_matches=4,
            weight=1.1,
        ),
        # Conta de Agua
        ClassificationRule(
            document_type=DocumentType.CONTA_AGUA,
            keywords=[
                "agua",
                "esgoto",
                "saneamento",
                "hidrometro",
                "consumo",
                "m3",
                "metros cubicos",
                "leitura",
            ],
            patterns=[
                r"\d+\s*m[³3]",
            ],
            min_keyword_matches=3,
            weight=1.1,
        ),
        # Extrato Bancario
        ClassificationRule(
            document_type=DocumentType.EXTRATO,
            keywords=[
                "extrato",
                "saldo anterior",
                "saldo atual",
                "credito",
                "debito",
                "transferencia",
                "deposito",
                "saque",
                "movimentacao",
                "periodo",
            ],
            min_keyword_matches=4,
            weight=1.0,
        ),
        # Comprovante de Pagamento
        ClassificationRule(
            document_type=DocumentType.COMPROVANTE_PAGAMENTO,
            keywords=[
                "comprovante",
                "pagamento",
                "pago",
                "autenticacao",
                "transacao",
                "confirmacao",
                "data pagamento",
                "valor pago",
            ],
            min_keyword_matches=3,
            weight=1.0,
        ),
        # Proposta
        ClassificationRule(
            document_type=DocumentType.PROPOSTA,
            keywords=[
                "proposta",
                "orcamento",
                "cotacao",
                "validade",
                "condicoes",
                "prazo",
                "escopo",
            ],
            min_keyword_matches=3,
            weight=0.9,
        ),
        # Procuracao
        ClassificationRule(
            document_type=DocumentType.PROCURACAO,
            keywords=[
                "procuracao",
                "outorgante",
                "outorgado",
                "poderes",
                "mandato",
                "representar",
                "substabelecer",
                "cartorio",
            ],
            min_keyword_matches=3,
            weight=1.0,
        ),
        # Declaracao
        ClassificationRule(
            document_type=DocumentType.DECLARACAO,
            keywords=[
                "declaracao",
                "declaro",
                "declaramos",
                "afirmo",
                "atesto",
                "para os devidos fins",
                "sob pena",
            ],
            min_keyword_matches=2,
            weight=0.9,
        ),
        # Atestado
        ClassificationRule(
            document_type=DocumentType.ATESTADO,
            keywords=[
                "atestado",
                "atesto",
                "medico",
                "cid",
                "comparecimento",
                "afastamento",
                "dias",
            ],
            min_keyword_matches=3,
            weight=1.0,
        ),
    ]

    def __init__(
        self,
        config: ClassifierConfig | None = None,
        custom_rules: list[ClassificationRule] | None = None,
    ):
        """
        Inicializa classificador.

        Args:
            config: Configuracao do classificador
            custom_rules: Regras customizadas adicionais
        """
        self.config = config or ClassifierConfig()
        self.rules = self.DEFAULT_RULES.copy()
        if custom_rules:
            self.rules.extend(custom_rules)

        # Compilar padroes
        self._compiled_patterns: dict[DocumentType, list[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compila padroes regex."""
        for rule in self.rules:
            patterns = []
            for pattern in rule.patterns:
                try:
                    patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    logger.warning(f"Padrao invalido {pattern}: {e}")
            self._compiled_patterns[rule.document_type] = patterns

    async def classify(
        self,
        ocr_result: OCRResult,
        templates: list[ExtractionTemplate] | None = None,
    ) -> ClassificationResult:
        """
        Classifica documento.

        Args:
            ocr_result: Resultado do OCR
            templates: Templates para matching

        Returns:
            Resultado da classificacao
        """
        full_text = ocr_result.get_full_text().lower()

        # Calcular scores para cada tipo
        scores: dict[DocumentType, tuple[float, list[str], list[str]]] = {}

        for rule in self.rules:
            score, matched_kw, matched_pat = self._evaluate_rule(rule, full_text)
            if score > 0:
                if rule.document_type not in scores or score > scores[rule.document_type][0]:
                    scores[rule.document_type] = (score, matched_kw, matched_pat)

        # Matching com templates
        template_match = None
        if templates:
            template_match, template_score = self._match_templates(ocr_result, templates)
            if template_match:
                doc_type = self._template_to_document_type(template_match.document_type)
                if doc_type in scores:
                    # Combinar scores
                    current = scores[doc_type]
                    scores[doc_type] = (
                        current[0] + template_score * 0.3,
                        current[1],
                        current[2],
                    )
                else:
                    scores[doc_type] = (template_score, [], [])

        # Determinar melhor match
        if not scores:
            return ClassificationResult(
                document_type=self.config.fallback_type,
                confidence=0.0,
            )

        # Ordenar por score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
        best_type, (best_score, matched_kw, matched_pat) = sorted_scores[0]

        # Normalizar confianca (0-1)
        confidence = min(best_score / 10, 1.0)

        # Alternativas
        alternatives = [(doc_type, min(score / 10, 1.0)) for doc_type, (score, _, _) in sorted_scores[1:4] if score > 0]

        return ClassificationResult(
            document_type=best_type,
            confidence=confidence,
            matched_keywords=matched_kw,
            matched_patterns=matched_pat,
            alternative_types=alternatives,
            template_id=template_match.id if template_match else None,
        )

    def _evaluate_rule(self, rule: ClassificationRule, text: str) -> tuple[float, list[str], list[str]]:
        """Avalia uma regra de classificacao."""
        matched_keywords = []
        matched_patterns = []

        # Verificar palavras excluidas
        for excluded in rule.excluded_keywords:
            if excluded.lower() in text:
                return 0, [], []

        # Contar keywords
        for keyword in rule.keywords:
            if keyword.lower() in text:
                matched_keywords.append(keyword)

        # Verificar keywords obrigatorias
        if rule.required_keywords:
            has_required = any(kw.lower() in text for kw in rule.required_keywords)
            if not has_required:
                return 0, [], []

        # Verificar minimo de matches
        if len(matched_keywords) < rule.min_keyword_matches:
            return 0, [], []

        # Verificar padroes
        patterns = self._compiled_patterns.get(rule.document_type, [])
        for pattern in patterns:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)

        # Calcular score
        score = len(matched_keywords) * 1.5 + len(matched_patterns) * 2.0
        score *= rule.weight

        return score, matched_keywords, matched_patterns

    def _match_templates(
        self,
        ocr_result: OCRResult,
        templates: list[ExtractionTemplate],
    ) -> tuple[ExtractionTemplate | None, float]:
        """Encontra template que melhor corresponde."""
        full_text = ocr_result.get_full_text().lower()
        best_template = None
        best_score = 0

        for template in templates:
            score = 0

            # Keywords de deteccao
            for keyword in template.detection_keywords:
                if keyword.lower() in full_text:
                    score += 2

            # Padroes de deteccao
            for pattern in template.detection_patterns:
                try:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        score += 3
                except re.error:
                    pass

            # Regras de deteccao
            for rule in template.detection_rules:
                if rule.pattern:
                    try:
                        if re.search(rule.pattern, full_text, re.IGNORECASE):
                            score += 2
                    except re.error:
                        pass

            # Normalizar
            normalized_score = score / max(
                len(template.detection_keywords) + len(template.detection_patterns) * 1.5,
                1,
            )

            if normalized_score >= template.min_detection_score:
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_template = template

        return best_template, best_score

    def _template_to_document_type(self, type_str: str) -> DocumentType:
        """Converte tipo do template para DocumentType."""
        type_map = {
            "boleto": DocumentType.BOLETO,
            "nfe": DocumentType.NFE,
            "nfse": DocumentType.NFSE,
            "fatura": DocumentType.FATURA,
            "recibo": DocumentType.RECIBO,
            "cnh": DocumentType.CNH,
            "rg": DocumentType.RG,
            "cpf": DocumentType.CPF,
            "holerite": DocumentType.HOLERITE,
            "contrato": DocumentType.CONTRATO,
        }
        return type_map.get(type_str.lower(), DocumentType.OUTRO)

    def add_rule(self, rule: ClassificationRule) -> None:
        """Adiciona regra de classificacao."""
        self.rules.append(rule)
        # Recompilar padroes
        patterns = []
        for pattern in rule.patterns:
            with contextlib.suppress(re.error):
                patterns.append(re.compile(pattern, re.IGNORECASE))
        self._compiled_patterns[rule.document_type] = patterns

    def get_supported_types(self) -> list[DocumentType]:
        """Retorna tipos suportados."""
        return list({rule.document_type for rule in self.rules})

    def explain_classification(self, result: ClassificationResult) -> dict[str, Any]:
        """Explica a classificacao realizada."""
        return {
            "document_type": result.document_type.value,
            "confidence": f"{result.confidence * 100:.1f}%",
            "reasoning": {
                "matched_keywords": result.matched_keywords,
                "matched_patterns": result.matched_patterns,
                "template_used": result.template_id is not None,
            },
            "alternatives": [{"type": t.value, "confidence": f"{c * 100:.1f}%"} for t, c in result.alternative_types],
        }
