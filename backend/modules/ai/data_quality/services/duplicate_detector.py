"""
DuplicateDetector Service - Sprint 48.

Serviço de detecção de registros duplicados.
"""

import uuid
from difflib import SequenceMatcher
from typing import Any

from modules.ai.data_quality.models import (
    DuplicateRecord,
    DuplicateStatusEnum,
    DuplicateTypeEnum,
)


class DuplicateDetector:
    """Serviço de detecção de duplicatas."""

    def __init__(self, threshold: float = 80.0):
        self.threshold = threshold

    def find_duplicates(
        self, records: list[dict[str, Any]], fields: list[str], id_field: str = "id", entity_type: str = "unknown"
    ) -> list[DuplicateRecord]:
        """
        Encontra registros duplicados.

        Args:
            records: Lista de registros para analisar
            fields: Campos para comparação
            id_field: Nome do campo de ID
            entity_type: Tipo da entidade

        Returns:
            Lista de DuplicateRecord
        """
        duplicates = []
        processed_pairs = set()

        for i, record1 in enumerate(records):
            for _j, record2 in enumerate(records[i + 1 :], start=i + 1):
                pair_key = tuple(sorted([str(record1.get(id_field)), str(record2.get(id_field))]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)

                similarity, field_scores, matching_fields = self._compare_records(record1, record2, fields)

                if similarity >= self.threshold:
                    duplicate = self._create_duplicate_record(
                        record1=record1,
                        record2=record2,
                        id_field=id_field,
                        entity_type=entity_type,
                        similarity=similarity,
                        field_scores=field_scores,
                        matching_fields=matching_fields,
                    )
                    duplicates.append(duplicate)

        return duplicates

    def _compare_records(
        self, record1: dict[str, Any], record2: dict[str, Any], fields: list[str]
    ) -> tuple[float, dict[str, float], list[str]]:
        """Compara dois registros."""
        field_scores = {}
        matching_fields = []
        total_weight = 0
        weighted_score = 0

        for field in fields:
            value1 = record1.get(field)
            value2 = record2.get(field)

            # Pula campos nulos
            if value1 is None and value2 is None:
                continue

            score = self._compare_values(value1, value2)
            field_scores[field] = score

            # Peso baseado na importância do campo
            weight = self._get_field_weight(field)
            weighted_score += score * weight
            total_weight += weight

            if score >= 90:
                matching_fields.append(field)

        overall_score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        return overall_score, field_scores, matching_fields

    def _compare_values(self, value1: Any, value2: Any) -> float:
        """Compara dois valores."""
        if value1 is None or value2 is None:
            return 0.0

        str1 = self._normalize_value(value1)
        str2 = self._normalize_value(value2)

        # Comparação exata
        if str1 == str2:
            return 100.0

        # Similaridade por SequenceMatcher
        ratio = SequenceMatcher(None, str1, str2).ratio()
        return ratio * 100

    def _normalize_value(self, value: Any) -> str:
        """Normaliza valor para comparação."""
        if value is None:
            return ""
        text = str(value).lower().strip()
        # Remove caracteres especiais
        import re

        text = re.sub(r"[^\w\s]", "", text)
        # Remove espaços duplicados
        text = re.sub(r"\s+", " ", text)
        return text

    def _get_field_weight(self, field: str) -> float:
        """Retorna peso do campo para cálculo de similaridade."""
        # Campos com maior peso para identificação
        high_weight_fields = ["email", "cpf", "cnpj", "phone", "telefone", "documento"]
        medium_weight_fields = ["name", "nome", "razao_social", "company"]

        field_lower = field.lower()
        if any(f in field_lower for f in high_weight_fields):
            return 3.0
        if any(f in field_lower for f in medium_weight_fields):
            return 2.0
        return 1.0

    def _create_duplicate_record(
        self,
        record1: dict[str, Any],
        record2: dict[str, Any],
        id_field: str,
        entity_type: str,
        similarity: float,
        field_scores: dict[str, float],
        matching_fields: list[str],
    ) -> DuplicateRecord:
        """Cria registro de duplicata."""
        group_id = uuid.uuid4()
        id1 = str(record1.get(id_field))
        id2 = str(record2.get(id_field))

        # Determina tipo de duplicata
        if similarity >= 99:
            dup_type = DuplicateTypeEnum.EXACT
        elif similarity >= 90:
            dup_type = DuplicateTypeEnum.FUZZY
        else:
            dup_type = DuplicateTypeEnum.PARTIAL

        # Identifica campos conflitantes
        conflicting_fields = [f for f, score in field_scores.items() if score < 100 and score > 0]

        # Pode fazer auto-merge se similaridade alta e sem conflitos importantes
        can_auto_merge = similarity >= 95 and len(conflicting_fields) <= 2

        return DuplicateRecord(
            group_id=group_id,
            status=DuplicateStatusEnum.DETECTED,
            duplicate_type=dup_type,
            entity_type=entity_type,
            record_ids=[id1, id2],
            record_count=2,
            matching_fields=matching_fields,
            conflicting_fields=conflicting_fields,
            similarity_score=similarity,
            confidence_score=min(similarity, 100) / 100,
            field_scores=field_scores,
            can_auto_merge=can_auto_merge,
        )

    def compare_two_records(
        self, record1: dict[str, Any], record2: dict[str, Any], fields: list[str] = None
    ) -> dict[str, Any]:
        """
        Compara dois registros específicos.

        Returns:
            Dict com resultado da comparação
        """
        if fields is None:
            # Usa todos os campos em comum
            fields = list(set(record1.keys()) & set(record2.keys()))

        similarity, field_scores, matching_fields = self._compare_records(record1, record2, fields)

        return {
            "is_duplicate": similarity >= self.threshold,
            "similarity_score": similarity,
            "field_scores": field_scores,
            "matching_fields": matching_fields,
            "conflicting_fields": [f for f, score in field_scores.items() if score < 100 and score > 0],
            "threshold": self.threshold,
        }
