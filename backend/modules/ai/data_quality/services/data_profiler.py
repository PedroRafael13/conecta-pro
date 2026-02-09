"""
DataProfiler Service - Sprint 48.

Serviço de profiling estatístico de dados.
"""

import contextlib
import re
import statistics
import uuid
from collections import Counter
from datetime import datetime
from typing import Any

from modules.ai.data_quality.models import (
    DataProfile,
    DataTypeEnum,
)


class DataProfiler:
    """Serviço de profiling de dados."""

    def __init__(self):
        self.type_patterns = {
            DataTypeEnum.EMAIL: r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            DataTypeEnum.CPF: r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$",
            DataTypeEnum.CNPJ: r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$",
            DataTypeEnum.CEP: r"^\d{5}-?\d{3}$",
            DataTypeEnum.PHONE: r"^(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}$",
            DataTypeEnum.URL: r"^https?://[^\s]+$",
            DataTypeEnum.UUID: r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        }

    def profile_field(self, values: list[Any], entity_type: str, field_name: str) -> DataProfile:
        """
        Gera perfil para campo específico.

        Args:
            values: Lista de valores do campo
            entity_type: Tipo da entidade
            field_name: Nome do campo

        Returns:
            DataProfile com estatísticas
        """
        profile_code = f"PROF-{entity_type}-{field_name}-{uuid.uuid4().hex[:8]}"

        profile = DataProfile(
            profile_code=profile_code,
            entity_type=entity_type,
            field_name=field_name,
            is_entity_profile=False,
            total_records=len(values),
        )

        profile.start_profiling()

        try:
            # Análise básica
            self._analyze_basic_stats(profile, values)

            # Detecta tipo
            profile.detected_type = self._detect_type(values)

            # Estatísticas específicas por tipo
            if profile.detected_type in [DataTypeEnum.INTEGER, DataTypeEnum.FLOAT, DataTypeEnum.CURRENCY]:
                self._analyze_numeric_stats(profile, values)
            elif profile.detected_type == DataTypeEnum.STRING:
                self._analyze_string_stats(profile, values)
            elif profile.detected_type in [DataTypeEnum.DATE, DataTypeEnum.DATETIME]:
                self._analyze_date_stats(profile, values)

            # Distribuição de valores
            self._analyze_distribution(profile, values)

            # Outliers
            self._detect_outliers(profile, values)

            # Recomendações
            self._generate_recommendations(profile)

            profile.complete_profiling()

        except Exception as e:
            profile.fail_profiling(str(e))

        return profile

    def profile_entity(self, records: list[dict[str, Any]], entity_type: str) -> DataProfile:
        """Gera perfil para entidade inteira."""
        profile_code = f"PROF-{entity_type}-ENTITY-{uuid.uuid4().hex[:8]}"

        profile = DataProfile(
            profile_code=profile_code, entity_type=entity_type, is_entity_profile=True, total_records=len(records)
        )

        profile.start_profiling()

        try:
            # Analisa completude por registro
            completeness_scores = []
            for record in records:
                non_null = sum(1 for v in record.values() if v is not None)
                total = len(record)
                completeness_scores.append((non_null / total * 100) if total > 0 else 0)

            profile.completeness_score = statistics.mean(completeness_scores) if completeness_scores else 0

            # Conta campos nulos por registro
            null_counts = [sum(1 for v in record.values() if v is None) for record in records]
            profile.null_count = sum(null_counts)

            # Detecta duplicatas potenciais
            if records:
                # Usa representação string para detectar duplicatas exatas
                record_strings = [str(sorted(r.items())) for r in records]
                profile.duplicate_count = len(record_strings) - len(set(record_strings))

            profile.complete_profiling()

        except Exception as e:
            profile.fail_profiling(str(e))

        return profile

    def _analyze_basic_stats(self, profile: DataProfile, values: list[Any]) -> None:
        """Analisa estatísticas básicas."""
        total = len(values)
        null_values = [v for v in values if v is None or v == ""]
        non_null_values = [v for v in values if v is not None and v != ""]

        profile.null_count = len(null_values)
        profile.null_percentage = (profile.null_count / total * 100) if total > 0 else 0
        profile.empty_count = len([v for v in values if v == ""])
        profile.empty_percentage = (profile.empty_count / total * 100) if total > 0 else 0

        # Distinct values
        distinct_values = {str(v) for v in non_null_values}
        profile.distinct_count = len(distinct_values)
        profile.distinct_percentage = (profile.distinct_count / len(non_null_values) * 100) if non_null_values else 0

        # Duplicados
        value_counts = Counter(str(v) for v in non_null_values)
        profile.duplicate_count = sum(c - 1 for c in value_counts.values() if c > 1)

        # Completeness
        profile.completeness_score = 100 - profile.null_percentage

    def _detect_type(self, values: list[Any]) -> DataTypeEnum:
        """Detecta tipo de dado predominante."""
        non_null = [v for v in values if v is not None and v != ""]
        if not non_null:
            return DataTypeEnum.UNKNOWN

        sample = non_null[:100]  # Analisa amostra

        # Tenta tipos específicos primeiro
        for data_type, pattern in self.type_patterns.items():
            matches = sum(1 for v in sample if re.match(pattern, str(v), re.I))
            if matches / len(sample) > 0.8:
                return data_type

        # Tipos básicos
        int_count = 0
        float_count = 0
        bool_count = 0

        for v in sample:
            if isinstance(v, bool):
                bool_count += 1
            elif isinstance(v, int):
                int_count += 1
            elif isinstance(v, float):
                float_count += 1
            elif isinstance(v, str):
                try:
                    int(v)
                    int_count += 1
                except ValueError:
                    try:
                        float(v)
                        float_count += 1
                    except ValueError:
                        pass

        total = len(sample)
        if bool_count / total > 0.8:
            return DataTypeEnum.BOOLEAN
        if int_count / total > 0.8:
            return DataTypeEnum.INTEGER
        if float_count / total > 0.8:
            return DataTypeEnum.FLOAT

        return DataTypeEnum.STRING

    def _analyze_numeric_stats(self, profile: DataProfile, values: list[Any]) -> None:
        """Analisa estatísticas numéricas."""
        numeric_values = []
        for v in values:
            if v is not None:
                with contextlib.suppress(ValueError, TypeError):
                    numeric_values.append(float(v))

        if not numeric_values:
            return

        profile.min_value = min(numeric_values)
        profile.max_value = max(numeric_values)
        profile.mean_value = statistics.mean(numeric_values)
        profile.median_value = statistics.median(numeric_values)
        profile.sum_value = sum(numeric_values)

        if len(numeric_values) > 1:
            profile.std_deviation = statistics.stdev(numeric_values)
            profile.variance = statistics.variance(numeric_values)

        # Percentis
        sorted_values = sorted(numeric_values)
        n = len(sorted_values)
        profile.percentiles = {
            "p25": sorted_values[int(n * 0.25)],
            "p50": sorted_values[int(n * 0.50)],
            "p75": sorted_values[int(n * 0.75)],
            "p90": sorted_values[int(n * 0.90)],
            "p95": sorted_values[int(n * 0.95)],
            "p99": sorted_values[min(int(n * 0.99), n - 1)],
        }

    def _analyze_string_stats(self, profile: DataProfile, values: list[Any]) -> None:
        """Analisa estatísticas de string."""
        string_values = [str(v) for v in values if v is not None and v != ""]

        if not string_values:
            return

        lengths = [len(s) for s in string_values]
        profile.min_length = min(lengths)
        profile.max_length = max(lengths)
        profile.avg_length = statistics.mean(lengths)

        # Detecta padrões comuns
        patterns = self._detect_patterns(string_values[:100])
        profile.common_patterns = patterns[:5]

    def _analyze_date_stats(self, profile: DataProfile, values: list[Any]) -> None:
        """Analisa estatísticas de data."""
        dates = []
        for v in values:
            if v is not None:
                if isinstance(v, datetime):
                    dates.append(v)
                elif isinstance(v, str):
                    with contextlib.suppress(ValueError):
                        dates.append(datetime.fromisoformat(v.replace("Z", "+00:00")))

        if not dates:
            return

        profile.date_range_start = min(dates)
        profile.date_range_end = max(dates)

        now = datetime.utcnow()
        profile.future_dates_count = sum(1 for d in dates if d > now)

    def _analyze_distribution(self, profile: DataProfile, values: list[Any]) -> None:
        """Analisa distribuição de valores."""
        non_null = [v for v in values if v is not None and v != ""]
        if not non_null:
            return

        # Top 10 valores mais frequentes
        counter = Counter(str(v) for v in non_null)
        top_values = counter.most_common(10)
        profile.value_distribution = dict(top_values)

    def _detect_outliers(self, profile: DataProfile, values: list[Any]) -> None:
        """Detecta outliers usando IQR."""
        numeric_values = []
        for v in values:
            if v is not None:
                with contextlib.suppress(ValueError, TypeError):
                    numeric_values.append(float(v))

        if len(numeric_values) < 4:
            return

        sorted_vals = sorted(numeric_values)
        n = len(sorted_vals)
        q1 = sorted_vals[int(n * 0.25)]
        q3 = sorted_vals[int(n * 0.75)]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
        profile.outlier_count = len(outliers)
        profile.outlier_percentage = (len(outliers) / len(numeric_values) * 100) if numeric_values else 0
        profile.outliers = outliers[:10]  # Sample

    def _detect_patterns(self, values: list[str]) -> list[str]:
        """Detecta padrões comuns nos valores."""
        patterns = []

        # Padrão numérico
        numeric_pattern = sum(1 for v in values if re.match(r"^\d+$", v))
        if numeric_pattern / len(values) > 0.5:
            patterns.append("numeric_only")

        # Padrão alfanumérico
        alphanum_pattern = sum(1 for v in values if re.match(r"^[a-zA-Z0-9]+$", v))
        if alphanum_pattern / len(values) > 0.5:
            patterns.append("alphanumeric")

        # Padrão com prefixo comum
        if len(values) > 10:
            prefixes = [v[:3] for v in values if len(v) >= 3]
            common_prefix = Counter(prefixes).most_common(1)
            if common_prefix and common_prefix[0][1] / len(values) > 0.5:
                patterns.append(f"common_prefix:{common_prefix[0][0]}")

        return patterns

    def _generate_recommendations(self, profile: DataProfile) -> None:
        """Gera recomendações baseadas no perfil."""
        if profile.null_percentage > 20:
            profile.add_recommendation(
                f"Alto índice de valores nulos ({profile.null_percentage:.1f}%). "
                "Considere tornar campo obrigatório ou revisar processo de coleta.",
                "high",
            )

        if profile.duplicate_count > 0 and profile.distinct_percentage < 50:
            profile.add_recommendation(
                f"Baixa diversidade de valores ({profile.distinct_percentage:.1f}% únicos). "
                "Considere usar enum ou validar entrada.",
                "medium",
            )

        if profile.outlier_percentage > 5:
            profile.add_recommendation(
                f"Detectados {profile.outlier_count} outliers ({profile.outlier_percentage:.1f}%). "
                "Revise valores extremos.",
                "medium",
            )
