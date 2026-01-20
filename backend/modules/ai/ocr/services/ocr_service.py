"""OCRService - Servico de processamento OCR.

Sprint 39 - Document OCR.

Suporta multiplos providers:
- Tesseract (local)
- Google Cloud Vision
- AWS Textract
- Azure Form Recognizer
"""

import hashlib
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.ocr.models.ocr_result import OCRProvider, OCRResult

logger = logging.getLogger(__name__)


class OCRService:
    """Servico de processamento OCR."""

    def __init__(
        self,
        default_provider: OCRProvider = OCRProvider.TESSERACT,
        default_language: str = "por",
        confidence_threshold: float = 0.6,
        enable_preprocessing: bool = True,
        enable_table_detection: bool = True,
        enable_key_value_detection: bool = True,
    ):
        """Inicializa o servico.

        Args:
            default_provider: Provider padrao de OCR
            default_language: Idioma padrao
            confidence_threshold: Limite minimo de confianca
            enable_preprocessing: Habilita pre-processamento
            enable_table_detection: Habilita deteccao de tabelas
            enable_key_value_detection: Habilita deteccao de pares chave-valor
        """
        self.default_provider = default_provider
        self.default_language = default_language
        self.confidence_threshold = confidence_threshold
        self.enable_preprocessing = enable_preprocessing
        self.enable_table_detection = enable_table_detection
        self.enable_key_value_detection = enable_key_value_detection

        # Configuracoes por provider
        self.provider_configs: Dict[str, Dict[str, Any]] = {}

    def configure_provider(
        self,
        provider: OCRProvider,
        config: Dict[str, Any],
    ) -> None:
        """Configura um provider.

        Args:
            provider: Provider a configurar
            config: Configuracoes do provider
        """
        self.provider_configs[provider.value] = config
        logger.info(f"Provider {provider.value} configurado")

    def process_image(
        self,
        image_data: bytes,
        provider: Optional[OCRProvider] = None,
        language: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Processa imagem com OCR.

        Args:
            image_data: Dados da imagem
            provider: Provider a usar (ou default)
            language: Idioma do documento
            options: Opcoes adicionais

        Returns:
            Resultado do OCR
        """
        provider = provider or self.default_provider
        language = language or self.default_language
        options = options or {}

        start_time = datetime.utcnow()

        # Seleciona handler do provider
        if provider == OCRProvider.TESSERACT:
            result = self._process_tesseract(image_data, language, options)
        elif provider == OCRProvider.GOOGLE_VISION:
            result = self._process_google_vision(image_data, language, options)
        elif provider == OCRProvider.AWS_TEXTRACT:
            result = self._process_aws_textract(image_data, language, options)
        elif provider == OCRProvider.AZURE_FORM:
            result = self._process_azure_form(image_data, language, options)
        else:
            result = self._process_tesseract(image_data, language, options)

        # Calcula tempo de processamento
        end_time = datetime.utcnow()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

        result["provider"] = provider.value
        result["language"] = language
        result["processing_time_ms"] = processing_time_ms

        # Pos-processamento
        if self.enable_key_value_detection:
            result["key_value_pairs"] = self._detect_key_value_pairs(result)

        if self.enable_table_detection:
            result["tables"] = self._detect_tables(result)

        # Calcula metricas
        result["metrics"] = self._calculate_metrics(result)

        return result

    def _process_tesseract(
        self,
        image_data: bytes,
        language: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Processa com Tesseract OCR (simulado).

        Args:
            image_data: Dados da imagem
            language: Idioma
            options: Opcoes

        Returns:
            Resultado do OCR
        """
        # Simulacao - em producao usaria pytesseract
        logger.info("Processando com Tesseract OCR")

        # Gera resultado simulado baseado no hash da imagem
        image_hash = hashlib.sha256(image_data).hexdigest()[:8]

        return {
            "raw_text": f"Texto extraido do documento (hash: {image_hash})",
            "lines": [
                {
                    "text": "NOTA FISCAL ELETRONICA",
                    "confidence": 0.98,
                    "bounding_box": {"x": 100, "y": 50, "width": 300, "height": 30},
                    "words": [
                        {"text": "NOTA", "confidence": 0.99},
                        {"text": "FISCAL", "confidence": 0.98},
                        {"text": "ELETRONICA", "confidence": 0.97},
                    ],
                },
                {
                    "text": "CNPJ: 12.345.678/0001-90",
                    "confidence": 0.95,
                    "bounding_box": {"x": 100, "y": 100, "width": 250, "height": 20},
                    "words": [
                        {"text": "CNPJ:", "confidence": 0.99},
                        {"text": "12.345.678/0001-90", "confidence": 0.92},
                    ],
                },
            ],
            "blocks": [
                {
                    "type": "text",
                    "text": "NOTA FISCAL ELETRONICA\nCNPJ: 12.345.678/0001-90",
                    "confidence": 0.96,
                    "bounding_box": {"x": 100, "y": 50, "width": 300, "height": 70},
                }
            ],
            "overall_confidence": 0.96,
        }

    def _process_google_vision(
        self,
        image_data: bytes,
        language: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Processa com Google Cloud Vision (simulado).

        Args:
            image_data: Dados da imagem
            language: Idioma
            options: Opcoes

        Returns:
            Resultado do OCR
        """
        logger.info("Processando com Google Cloud Vision")

        # Simulacao - em producao usaria google-cloud-vision
        image_hash = hashlib.sha256(image_data).hexdigest()[:8]

        return {
            "raw_text": f"Texto Google Vision (hash: {image_hash})",
            "lines": [],
            "blocks": [],
            "overall_confidence": 0.97,
        }

    def _process_aws_textract(
        self,
        image_data: bytes,
        language: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Processa com AWS Textract (simulado).

        Args:
            image_data: Dados da imagem
            language: Idioma
            options: Opcoes

        Returns:
            Resultado do OCR
        """
        logger.info("Processando com AWS Textract")

        # Simulacao - em producao usaria boto3
        image_hash = hashlib.sha256(image_data).hexdigest()[:8]

        return {
            "raw_text": f"Texto AWS Textract (hash: {image_hash})",
            "lines": [],
            "blocks": [],
            "tables": [],
            "forms": [],
            "overall_confidence": 0.95,
        }

    def _process_azure_form(
        self,
        image_data: bytes,
        language: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Processa com Azure Form Recognizer (simulado).

        Args:
            image_data: Dados da imagem
            language: Idioma
            options: Opcoes

        Returns:
            Resultado do OCR
        """
        logger.info("Processando com Azure Form Recognizer")

        # Simulacao - em producao usaria azure-ai-formrecognizer
        image_hash = hashlib.sha256(image_data).hexdigest()[:8]

        return {
            "raw_text": f"Texto Azure Form (hash: {image_hash})",
            "lines": [],
            "blocks": [],
            "tables": [],
            "key_value_pairs": [],
            "overall_confidence": 0.96,
        }

    def _detect_key_value_pairs(
        self,
        ocr_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detecta pares chave-valor no texto.

        Args:
            ocr_result: Resultado do OCR

        Returns:
            Lista de pares chave-valor
        """
        pairs = []
        raw_text = ocr_result.get("raw_text", "")

        # Padroes comuns de chave-valor
        patterns = [
            # CHAVE: valor
            r"([A-ZÀ-Ú][A-ZÀ-Ú\s]{2,30}):\s*([^\n]+)",
            # Chave - valor
            r"([A-ZÀ-Ú][a-zà-ú\s]{2,30})\s*[-–]\s*([^\n]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, raw_text)
            for key, value in matches:
                key = key.strip()
                value = value.strip()
                if key and value:
                    pairs.append({
                        "key": key,
                        "value": value,
                        "confidence": 0.8,
                    })

        return pairs

    def _detect_tables(
        self,
        ocr_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detecta tabelas no resultado OCR.

        Args:
            ocr_result: Resultado do OCR

        Returns:
            Lista de tabelas detectadas
        """
        # Se o provider ja retornou tabelas, usa-las
        if ocr_result.get("tables"):
            return ocr_result["tables"]

        # Caso contrario, tenta detectar por alinhamento
        tables = []
        lines = ocr_result.get("lines", [])

        if len(lines) < 3:
            return tables

        # Detecta linhas alinhadas que podem formar tabela
        aligned_groups = self._find_aligned_lines(lines)
        for group in aligned_groups:
            if len(group) >= 2:
                table = self._lines_to_table(group)
                if table:
                    tables.append(table)

        return tables

    def _find_aligned_lines(
        self,
        lines: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """Encontra linhas alinhadas.

        Args:
            lines: Lista de linhas

        Returns:
            Grupos de linhas alinhadas
        """
        groups: List[List[Dict[str, Any]]] = []
        used = set()

        for i, line in enumerate(lines):
            if i in used:
                continue

            group = [line]
            y_pos = line.get("bounding_box", {}).get("y", 0)

            for j, other_line in enumerate(lines[i + 1:], i + 1):
                if j in used:
                    continue
                other_y = other_line.get("bounding_box", {}).get("y", 0)
                # Linhas na mesma altura (tolerancia de 10 pixels)
                if abs(other_y - y_pos) < 10:
                    group.append(other_line)
                    used.add(j)

            if len(group) > 1:
                groups.append(group)
                used.add(i)

        return groups

    def _lines_to_table(
        self,
        lines: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Converte linhas alinhadas em tabela.

        Args:
            lines: Linhas alinhadas

        Returns:
            Tabela ou None
        """
        if len(lines) < 2:
            return None

        # Ordena por posicao X
        sorted_lines = sorted(
            lines,
            key=lambda x: x.get("bounding_box", {}).get("x", 0),
        )

        cells = []
        for i, line in enumerate(sorted_lines):
            cells.append({
                "row": 0,
                "col": i,
                "text": line.get("text", ""),
                "confidence": line.get("confidence", 0),
            })

        return {
            "rows": 1,
            "columns": len(cells),
            "cells": cells,
        }

    def _calculate_metrics(
        self,
        ocr_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calcula metricas do resultado OCR.

        Args:
            ocr_result: Resultado do OCR

        Returns:
            Metricas calculadas
        """
        lines = ocr_result.get("lines", [])

        if not lines:
            return {
                "overall_confidence": ocr_result.get("overall_confidence", 0),
                "line_count": 0,
                "word_count": 0,
                "char_count": len(ocr_result.get("raw_text", "")),
            }

        confidences = [line.get("confidence", 0) for line in lines]
        word_count = sum(len(line.get("words", [])) for line in lines)

        return {
            "overall_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0,
            "line_count": len(lines),
            "word_count": word_count,
            "char_count": len(ocr_result.get("raw_text", "")),
            "low_confidence_lines": len([c for c in confidences if c < self.confidence_threshold]),
        }

    def normalize_text(self, text: str) -> str:
        """Normaliza texto extraido.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado
        """
        if not text:
            return ""

        # Remove espacos multiplos
        text = re.sub(r"\s+", " ", text)

        # Remove espacos no inicio e fim
        text = text.strip()

        return text

    def detect_document_type(
        self,
        ocr_result: Dict[str, Any],
    ) -> Tuple[Optional[str], float]:
        """Detecta tipo de documento pelo conteudo.

        Args:
            ocr_result: Resultado do OCR

        Returns:
            Tupla (tipo, confianca)
        """
        raw_text = ocr_result.get("raw_text", "").upper()

        # Padroes de deteccao
        type_patterns = {
            "invoice": [
                "NOTA FISCAL", "NFE", "DANFE", "NF-E",
                "FATURA", "INVOICE",
            ],
            "receipt": [
                "CUPOM FISCAL", "RECIBO", "COMPROVANTE",
                "RECEIPT",
            ],
            "boleto": [
                "BOLETO", "CODIGO DE BARRAS", "FICHA DE COMPENSACAO",
                "LINHA DIGITAVEL",
            ],
            "contract": [
                "CONTRATO", "CONTRACT", "ACORDO", "TERMO DE",
            ],
            "id_card": [
                "REGISTRO GERAL", "IDENTIDADE", "RG",
            ],
            "cnh": [
                "CARTEIRA NACIONAL", "HABILITACAO", "CNH",
            ],
            "cpf_card": [
                "CADASTRO DE PESSOAS FISICAS", "CPF",
            ],
        }

        best_type = None
        best_score = 0.0

        for doc_type, keywords in type_patterns.items():
            matches = sum(1 for kw in keywords if kw in raw_text)
            score = matches / len(keywords) if keywords else 0

            if score > best_score:
                best_score = score
                best_type = doc_type

        return best_type, best_score

    def get_supported_languages(self, provider: OCRProvider) -> List[str]:
        """Retorna idiomas suportados pelo provider.

        Args:
            provider: Provider de OCR

        Returns:
            Lista de codigos de idioma
        """
        # Idiomas comuns suportados
        common_languages = [
            "por",  # Portugues
            "eng",  # Ingles
            "spa",  # Espanhol
            "fra",  # Frances
            "deu",  # Alemao
            "ita",  # Italiano
        ]

        if provider == OCRProvider.TESSERACT:
            return common_languages + ["jpn", "chi_sim", "chi_tra", "kor", "ara"]

        if provider == OCRProvider.GOOGLE_VISION:
            return common_languages + ["jpn", "zh", "ko", "ar", "ru"]

        if provider == OCRProvider.AWS_TEXTRACT:
            return ["eng", "spa", "por", "fra", "deu", "ita"]

        return common_languages

    def estimate_processing_cost(
        self,
        page_count: int,
        provider: OCRProvider,
    ) -> Dict[str, Any]:
        """Estima custo de processamento.

        Args:
            page_count: Numero de paginas
            provider: Provider de OCR

        Returns:
            Estimativa de custo
        """
        # Custos aproximados por pagina (USD)
        costs = {
            OCRProvider.TESSERACT: 0.0,  # Local, sem custo API
            OCRProvider.GOOGLE_VISION: 0.0015,  # ~$1.50 por 1000 paginas
            OCRProvider.AWS_TEXTRACT: 0.0015,  # ~$1.50 por 1000 paginas
            OCRProvider.AZURE_FORM: 0.001,  # ~$1 por 1000 paginas
        }

        cost_per_page = costs.get(provider, 0.002)
        total_cost = page_count * cost_per_page

        return {
            "provider": provider.value,
            "page_count": page_count,
            "cost_per_page_usd": cost_per_page,
            "total_cost_usd": total_cost,
            "currency": "USD",
        }
