"""Service de IA para Contabilidade."""

import logging
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.accounting_account import (
    AccountingAccount,
    AccountType,
)
from modules.financial.models.accounting_period import (
    AccountingPeriod,
    PeriodStatus,
)
from modules.financial.models.chart_of_accounts import ChartOfAccounts, ChartStatus
from modules.financial.models.cost_center import (
    CostCenter,
    CostCenterStatus,
)
from modules.financial.models.journal_entry import (
    EntryStatus,
    EntryType,
    JournalEntry,
    JournalEntryLine,
)
from modules.financial.models.trial_balance import (
    BalanceStatus,
    TrialBalance,
)
from modules.financial.repositories.accounting_repository import (
    AccountingAccountRepository,
    AccountingPeriodRepository,
    ChartOfAccountsRepository,
    CostCenterRepository,
    JournalEntryLineRepository,
    JournalEntryRepository,
    TrialBalanceItemRepository,
    TrialBalanceRepository,
)

logger = logging.getLogger(__name__)


class AccountingAIService:
    """Service de IA para analise e sugestoes contabeis."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.chart_repo = ChartOfAccountsRepository(session)
        self.account_repo = AccountingAccountRepository(session)
        self.cost_center_repo = CostCenterRepository(session)
        self.period_repo = AccountingPeriodRepository(session)
        self.entry_repo = JournalEntryRepository(session)
        self.line_repo = JournalEntryLineRepository(session)
        self.balance_repo = TrialBalanceRepository(session)
        self.balance_item_repo = TrialBalanceItemRepository(session)

    # =========================================================================
    # DETECCAO DE ANOMALIAS EM LANCAMENTOS
    # =========================================================================

    async def detect_journal_anomalies(
        self,
        condominio_id: UUID,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        sensitivity: str = "medium",
    ) -> List[Dict[str, Any]]:
        """Detecta anomalias em lancamentos contabeis."""
        logger.info(f"Detectando anomalias em lancamentos para {condominio_id}")
        anomalies = []

        # Define periodo padrao (ultimos 6 meses)
        if not period_end:
            period_end = date.today()
        if not period_start:
            period_start = period_end - timedelta(days=180)

        # Busca lancamentos do periodo
        entries = await self._get_journal_entries(condominio_id, period_start, period_end)

        if len(entries) < 10:
            logger.info("Poucos lancamentos para detectar anomalias")
            return anomalies

        # Define limiar baseado em sensibilidade
        thresholds = {"low": 2.5, "medium": 2.0, "high": 1.5}
        threshold = thresholds.get(sensitivity, 2.0)

        # 1. Analisa valores atipicos
        value_anomalies = await self._detect_value_anomalies(entries, threshold)
        anomalies.extend(value_anomalies)

        # 2. Analisa padroes de horario
        timing_anomalies = await self._detect_timing_anomalies(entries)
        anomalies.extend(timing_anomalies)

        # 3. Analisa lancamentos duplicados
        duplicate_anomalies = await self._detect_duplicate_entries(entries)
        anomalies.extend(duplicate_anomalies)

        # 4. Analisa sequencia numerica
        sequence_anomalies = await self._detect_sequence_gaps(entries)
        anomalies.extend(sequence_anomalies)

        # 5. Analisa contas incomuns
        account_anomalies = await self._detect_unusual_accounts(
            condominio_id, entries, period_start
        )
        anomalies.extend(account_anomalies)

        # 6. Analisa estornos excessivos
        reversal_anomalies = await self._detect_excessive_reversals(entries)
        anomalies.extend(reversal_anomalies)

        return sorted(anomalies, key=lambda x: x.get("severity_score", 0), reverse=True)

    async def _get_journal_entries(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[JournalEntry]:
        """Busca lancamentos contabeis do periodo."""
        query = (
            select(JournalEntry)
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                    JournalEntry.ativo.is_(True),
                )
            )
            .order_by(JournalEntry.entry_date, JournalEntry.entry_number)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _detect_value_anomalies(
        self,
        entries: List[JournalEntry],
        threshold: float,
    ) -> List[Dict[str, Any]]:
        """Detecta valores atipicos em lancamentos."""
        anomalies = []

        # Agrupa por tipo de lancamento
        entries_by_type: Dict[str, List[Decimal]] = {}
        for entry in entries:
            entry_type = entry.entry_type or "geral"
            if entry_type not in entries_by_type:
                entries_by_type[entry_type] = []
            entries_by_type[entry_type].append(entry.total_debit or Decimal("0"))

        # Analisa cada grupo
        for entry_type, values in entries_by_type.items():
            if len(values) < 5:
                continue

            float_values = [float(v) for v in values]
            avg = sum(float_values) / len(float_values)
            variance = sum((x - avg) ** 2 for x in float_values) / len(float_values)
            std_dev = variance**0.5

            if std_dev == 0:
                continue

            for entry in entries:
                if entry.entry_type != entry_type:
                    continue

                value = float(entry.total_debit or Decimal("0"))
                z_score = abs(value - avg) / std_dev

                if z_score > threshold:
                    severity = "critica" if z_score > 3.5 else "alta" if z_score > 3 else "media"
                    anomalies.append(
                        {
                            "id": str(uuid.uuid4()),
                            "type": "valor_atipico",
                            "entry_id": str(entry.id),
                            "entry_number": entry.entry_number,
                            "entry_date": (
                                entry.entry_date.isoformat() if entry.entry_date else None
                            ),
                            "value": float(value),
                            "expected_range": {
                                "min": avg - (threshold * std_dev),
                                "max": avg + (threshold * std_dev),
                            },
                            "deviation": value - avg,
                            "z_score": z_score,
                            "severity": severity,
                            "severity_score": min(100, int(z_score * 25)),
                            "description": (
                                f"Lancamento #{entry.entry_number} com valor R$ {value:,.2f} "
                                f"fora do padrao (media: R$ {avg:,.2f}, desvio: {z_score:.1f} DP)"
                            ),
                            "recommendation": (
                                "Verificar se o lancamento esta correto "
                                "ou requer aprovacao especial"
                            ),
                        }
                    )

        return anomalies

    async def _detect_timing_anomalies(
        self,
        entries: List[JournalEntry],
    ) -> List[Dict[str, Any]]:
        """Detecta padroes de horario incomuns."""
        anomalies = []

        # Analisa lancamentos fora do horario comercial
        for entry in entries:
            if not entry.created_at:
                continue

            hour = entry.created_at.hour
            weekday = entry.created_at.weekday()

            # Fora do horario comercial (antes das 7h ou depois das 20h)
            if hour < 7 or hour > 20:
                anomalies.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "horario_incomum",
                        "entry_id": str(entry.id),
                        "entry_number": entry.entry_number,
                        "entry_date": (
                            entry.entry_date.isoformat()
                            if entry.entry_date else None
                        ),
                        "created_at": entry.created_at.isoformat(),
                        "hour": hour,
                        "severity": "baixa",
                        "severity_score": 20,
                        "description": (
                            f"Lancamento #{entry.entry_number} criado as {hour}h "
                            f"(fora do horario comercial)"
                        ),
                        "recommendation": (
                            "Verificar se usuario tinha autorizacao "
                            "para acesso fora do horario"
                        ),
                    }
                )

            # Fim de semana
            if weekday >= 5:
                day_name = "sabado" if weekday == 5 else "domingo"
                anomalies.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "lancamento_fim_semana",
                        "entry_id": str(entry.id),
                        "entry_number": entry.entry_number,
                        "entry_date": (
                            entry.entry_date.isoformat()
                            if entry.entry_date else None
                        ),
                        "created_at": entry.created_at.isoformat(),
                        "weekday": weekday,
                        "severity": "baixa",
                        "severity_score": 15,
                        "description": (
                            f"Lancamento #{entry.entry_number} criado no {day_name}"
                        ),
                        "recommendation": (
                            "Verificar procedimento de lancamentos "
                            "em finais de semana"
                        ),
                    }
                )

        return anomalies

    async def _detect_duplicate_entries(
        self,
        entries: List[JournalEntry],
    ) -> List[Dict[str, Any]]:
        """Detecta possiveis lancamentos duplicados."""
        anomalies = []
        checked_pairs = set()

        for i, entry1 in enumerate(entries):
            for _, entry2 in enumerate(entries[i + 1 :], start=i + 1):
                pair_key = tuple(sorted([str(entry1.id), str(entry2.id)]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                # Verifica se sao similares
                if (
                    entry1.entry_date == entry2.entry_date
                    and entry1.total_debit == entry2.total_debit
                    and entry1.description == entry2.description
                    and entry1.id != entry2.id
                ):
                    anomalies.append(
                        {
                            "id": str(uuid.uuid4()),
                            "type": "possivel_duplicata",
                            "entry_ids": [str(entry1.id), str(entry2.id)],
                            "entry_numbers": [entry1.entry_number, entry2.entry_number],
                            "entry_date": (
                                entry1.entry_date.isoformat()
                                if entry1.entry_date else None
                            ),
                            "value": float(entry1.total_debit or 0),
                            "description": entry1.description,
                            "severity": "alta",
                            "severity_score": 75,
                            "description_text": (
                                f"Lancamentos #{entry1.entry_number} e #{entry2.entry_number} "
                                f"parecem duplicados (mesma data, valor e descricao)"
                            ),
                            "recommendation": "Verificar se um dos lancamentos deve ser estornado",
                        }
                    )

        return anomalies

    async def _detect_sequence_gaps(
        self,
        entries: List[JournalEntry],
    ) -> List[Dict[str, Any]]:
        """Detecta falhas na sequencia de numeracao."""
        anomalies = []

        # Ordena por numero de lancamento
        sorted_entries = sorted(
            [e for e in entries if e.entry_number],
            key=lambda x: int(x.entry_number) if x.entry_number.isdigit() else 0,
        )

        for i in range(1, len(sorted_entries)):
            prev = sorted_entries[i - 1]
            curr = sorted_entries[i]

            try:
                prev_num = int(prev.entry_number)
                curr_num = int(curr.entry_number)

                if curr_num - prev_num > 1:
                    gap = curr_num - prev_num - 1
                    anomalies.append(
                        {
                            "id": str(uuid.uuid4()),
                            "type": "falha_sequencia",
                            "from_number": prev.entry_number,
                            "to_number": curr.entry_number,
                            "gap_size": gap,
                            "severity": "media" if gap <= 5 else "alta",
                            "severity_score": min(60, 20 + gap * 5),
                            "description": (
                                f"Falha na sequencia: {gap} numero(s) ausente(s) "
                                f"entre #{prev.entry_number} e #{curr.entry_number}"
                            ),
                            "recommendation": (
                                "Verificar se lancamentos foram excluidos "
                                "ou se houve erro no sistema"
                            ),
                        }
                    )
            except (ValueError, TypeError):
                continue

        return anomalies

    async def _detect_unusual_accounts(
        self,
        condominio_id: UUID,
        entries: List[JournalEntry],
        period_start: date,
    ) -> List[Dict[str, Any]]:
        """Detecta uso de contas incomuns."""
        anomalies = []

        # Busca historico de uso de contas (12 meses antes)
        historical_start = period_start - timedelta(days=365)

        query = (
            select(
                JournalEntryLine.account_id,
                func.count(JournalEntryLine.id).label("usage_count"),
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.entry_date >= historical_start,
                    JournalEntry.entry_date < period_start,
                    JournalEntry.ativo.is_(True),
                )
            )
            .group_by(JournalEntryLine.account_id)
        )

        result = await self.session.execute(query)
        historical_usage = {row.account_id: row.usage_count for row in result}

        # Verifica contas usadas no periodo atual
        for entry in entries:
            # Busca linhas do lancamento
            lines_query = select(JournalEntryLine).where(
                JournalEntryLine.journal_entry_id == entry.id
            )
            lines_result = await self.session.execute(lines_query)
            lines = list(lines_result.scalars().all())

            for line in lines:
                if line.account_id not in historical_usage:
                    # Conta nunca usada antes
                    anomalies.append(
                        {
                            "id": str(uuid.uuid4()),
                            "type": "conta_nova",
                            "entry_id": str(entry.id),
                            "entry_number": entry.entry_number,
                            "account_id": str(line.account_id),
                            "account_code": line.account_code,
                            "value": float(line.debit_value or line.credit_value or 0),
                            "severity": "baixa",
                            "severity_score": 25,
                            "description": (
                                f"Lancamento #{entry.entry_number} usa conta {line.account_code} "
                                f"que nunca foi utilizada antes"
                            ),
                            "recommendation": (
                                "Verificar se a conta esta correta "
                                "para este tipo de operacao"
                            ),
                        }
                    )
                elif historical_usage[line.account_id] <= 2:
                    # Conta raramente usada
                    anomalies.append(
                        {
                            "id": str(uuid.uuid4()),
                            "type": "conta_rara",
                            "entry_id": str(entry.id),
                            "entry_number": entry.entry_number,
                            "account_id": str(line.account_id),
                            "account_code": line.account_code,
                            "historical_usage": historical_usage[line.account_id],
                            "severity": "baixa",
                            "severity_score": 15,
                            "description": (
                                f"Lancamento #{entry.entry_number} usa conta {line.account_code} "
                                f"raramente utilizada "
                                f"(apenas {historical_usage[line.account_id]}x no ultimo ano)"
                            ),
                            "recommendation": "Confirmar se a classificacao contabil esta adequada",
                        }
                    )

        return anomalies

    async def _detect_excessive_reversals(
        self,
        entries: List[JournalEntry],
    ) -> List[Dict[str, Any]]:
        """Detecta volume excessivo de estornos."""
        anomalies = []

        # Conta estornos
        reversal_entries = [
            e for e in entries if e.entry_type == EntryType.ESTORNO.value
        ]

        total_entries = len(entries)
        reversal_count = len(reversal_entries)

        if total_entries > 0:
            reversal_rate = (reversal_count / total_entries) * 100

            if reversal_rate > 10:
                anomalies.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "estornos_excessivos",
                        "total_entries": total_entries,
                        "reversal_count": reversal_count,
                        "reversal_rate": reversal_rate,
                        "severity": "alta" if reversal_rate > 20 else "media",
                        "severity_score": min(80, int(reversal_rate * 3)),
                        "description": (
                            f"{reversal_count} estornos em {total_entries} lancamentos "
                            f"({reversal_rate:.1f}% de taxa de estorno)"
                        ),
                        "recommendation": (
                            "Taxa de estorno acima de 10% indica problemas no processo. "
                            "Revisar procedimentos de lancamento e treinamento de usuarios."
                        ),
                    }
                )

        return anomalies

    # =========================================================================
    # SUGESTOES DE CLASSIFICACAO DE CONTAS
    # =========================================================================

    async def suggest_account_classification(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        description: str,
        value: Decimal,
        transaction_type: str = "expense",  # "expense" ou "income"
    ) -> List[Dict[str, Any]]:
        """Sugere classificacao contabil baseada no historico."""
        logger.info(f"Sugerindo classificacao para: {description}")
        suggestions = []

        # Busca lancamentos similares no historico
        similar_entries = await self._find_similar_entries(
            condominio_id, description, value, transaction_type
        )

        # Agrupa por conta utilizada
        account_usage: Dict[str, Dict[str, Any]] = {}

        for entry in similar_entries:
            # Busca linhas do lancamento
            lines_query = select(JournalEntryLine).where(
                JournalEntryLine.journal_entry_id == entry.id
            )
            result = await self.session.execute(lines_query)
            lines = list(result.scalars().all())

            for line in lines:
                account_id = str(line.account_id)
                if account_id not in account_usage:
                    account_usage[account_id] = {
                        "account_id": account_id,
                        "account_code": line.account_code,
                        "account_name": line.account_name,
                        "usage_count": 0,
                        "total_value": Decimal("0"),
                        "similarity_scores": [],
                    }
                account_usage[account_id]["usage_count"] += 1
                account_usage[account_id]["total_value"] += (
                    line.debit_value or line.credit_value or Decimal("0")
                )
                account_usage[account_id]["similarity_scores"].append(
                    self._calculate_description_similarity(description, entry.description or "")
                )

        # Calcula score de confianca para cada conta
        for account_id, data in account_usage.items():
            avg_similarity = (
                sum(data["similarity_scores"]) / len(data["similarity_scores"])
                if data["similarity_scores"]
                else 0
            )
            frequency_score = min(100, data["usage_count"] * 10)
            confidence = int((avg_similarity * 0.6 + frequency_score * 0.4))

            suggestions.append(
                {
                    "account_id": data["account_id"],
                    "account_code": data["account_code"],
                    "account_name": data["account_name"],
                    "confidence": confidence,
                    "usage_count": data["usage_count"],
                    "average_value": float(data["total_value"] / data["usage_count"]),
                    "similarity_score": avg_similarity,
                    "reason": self._generate_suggestion_reason(
                        data["usage_count"], avg_similarity
                    ),
                }
            )

        # Ordena por confianca
        suggestions = sorted(suggestions, key=lambda x: x["confidence"], reverse=True)

        # Limita a 5 sugestoes
        return suggestions[:5]

    async def _find_similar_entries(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        description: str,
        value: Decimal,
        transaction_type: str,  # pylint: disable=unused-argument
    ) -> List[JournalEntry]:
        """Busca lancamentos similares no historico."""
        # Busca lancamentos dos ultimos 12 meses
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        # Palavras-chave da descricao
        keywords = description.lower().split()

        # Query basica
        query = select(JournalEntry).where(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
                JournalEntry.status == EntryStatus.APROVADO.value,
                JournalEntry.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        entries = list(result.scalars().all())

        # Filtra por similaridade
        similar_entries = []
        for entry in entries:
            entry_desc = (entry.description or "").lower()

            # Verifica se alguma palavra-chave aparece
            keyword_match = any(kw in entry_desc for kw in keywords if len(kw) > 3)

            # Verifica range de valor (dentro de 50%)
            entry_value = entry.total_debit or Decimal("0")
            value_in_range = (
                value * Decimal("0.5") <= entry_value <= value * Decimal("1.5")
            )

            if keyword_match or value_in_range:
                similar_entries.append(entry)

        return similar_entries[:50]  # Limita para performance

    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calcula similaridade entre descricoes (0-100)."""
        if not desc1 or not desc2:
            return 0

        words1 = set(desc1.lower().split())
        words2 = set(desc2.lower().split())

        # Remove palavras muito curtas
        words1 = {w for w in words1 if len(w) > 2}
        words2 = {w for w in words2 if len(w) > 2}

        if not words1 or not words2:
            return 0

        intersection = words1 & words2
        union = words1 | words2

        return (len(intersection) / len(union)) * 100

    def _generate_suggestion_reason(self, usage_count: int, similarity: float) -> str:
        """Gera justificativa para a sugestao."""
        reasons = []

        if usage_count >= 10:
            reasons.append(f"Conta usada {usage_count}x em lancamentos similares")
        elif usage_count >= 5:
            reasons.append(f"Conta usada frequentemente ({usage_count}x)")
        else:
            reasons.append(f"Conta usada {usage_count}x anteriormente")

        if similarity >= 80:
            reasons.append("descricoes muito similares")
        elif similarity >= 60:
            reasons.append("descricoes parcialmente similares")

        return " - ".join(reasons)

    # =========================================================================
    # PREVISAO DE BALANCO
    # =========================================================================

    async def forecast_balance(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        months_ahead: int = 3,
    ) -> Dict[str, Any]:
        """Gera previsao de balanco patrimonial."""
        logger.info(f"Gerando previsao de balanco para {condominio_id}")

        # Obtem ultimo balancete
        latest_balance = await self._get_latest_trial_balance(condominio_id)

        if not latest_balance:
            return {
                "error": "Nenhum balancete encontrado para gerar previsao",
                "condominio_id": str(condominio_id),
            }

        # Coleta dados historicos
        historical_data = await self._collect_balance_history(condominio_id, months=12)

        # Analisa tendencias
        trends = self._analyze_balance_trends(historical_data)

        # Gera previsoes por grupo de contas
        forecast_date = date.today() + timedelta(days=30 * months_ahead)

        projections = {
            "ativo_circulante": self._project_account_group(
                historical_data.get("ativo_circulante", []),
                months_ahead,
            ),
            "ativo_nao_circulante": self._project_account_group(
                historical_data.get("ativo_nao_circulante", []),
                months_ahead,
            ),
            "passivo_circulante": self._project_account_group(
                historical_data.get("passivo_circulante", []),
                months_ahead,
            ),
            "passivo_nao_circulante": self._project_account_group(
                historical_data.get("passivo_nao_circulante", []),
                months_ahead,
            ),
            "patrimonio_liquido": self._project_account_group(
                historical_data.get("patrimonio_liquido", []),
                months_ahead,
            ),
        }

        # Calcula totais projetados
        total_ativo = (
            projections["ativo_circulante"]["projected_value"]
            + projections["ativo_nao_circulante"]["projected_value"]
        )
        total_passivo = (
            projections["passivo_circulante"]["projected_value"]
            + projections["passivo_nao_circulante"]["projected_value"]
        )
        total_pl = projections["patrimonio_liquido"]["projected_value"]

        # Calcula indicadores projetados
        ativo_circ = projections["ativo_circulante"]["projected_value"]
        passivo_circ = projections["passivo_circulante"]["projected_value"]
        liquidity_ratio = (
            ativo_circ / passivo_circ if passivo_circ > 0 else 0
        )

        debt_ratio = (
            total_passivo / total_ativo * 100 if total_ativo > 0 else 0
        )

        # Calcula confianca baseada em dados historicos
        confidence = self._calculate_forecast_confidence(historical_data, trends)

        return {
            "condominio_id": str(condominio_id),
            "forecast_date": forecast_date.isoformat(),
            "months_ahead": months_ahead,
            "base_balance_id": str(latest_balance.id) if latest_balance else None,
            "base_balance_date": (
                latest_balance.reference_date.isoformat()
                if latest_balance and latest_balance.reference_date else None
            ),
            "projections": {
                "ativo_circulante": {
                    "current": projections["ativo_circulante"]["current_value"],
                    "projected": projections["ativo_circulante"]["projected_value"],
                    "change_percent": projections["ativo_circulante"]["change_percent"],
                    "trend": projections["ativo_circulante"]["trend"],
                },
                "ativo_nao_circulante": {
                    "current": projections["ativo_nao_circulante"]["current_value"],
                    "projected": projections["ativo_nao_circulante"]["projected_value"],
                    "change_percent": projections["ativo_nao_circulante"]["change_percent"],
                    "trend": projections["ativo_nao_circulante"]["trend"],
                },
                "passivo_circulante": {
                    "current": projections["passivo_circulante"]["current_value"],
                    "projected": projections["passivo_circulante"]["projected_value"],
                    "change_percent": projections["passivo_circulante"]["change_percent"],
                    "trend": projections["passivo_circulante"]["trend"],
                },
                "passivo_nao_circulante": {
                    "current": projections["passivo_nao_circulante"]["current_value"],
                    "projected": projections["passivo_nao_circulante"]["projected_value"],
                    "change_percent": projections["passivo_nao_circulante"]["change_percent"],
                    "trend": projections["passivo_nao_circulante"]["trend"],
                },
                "patrimonio_liquido": {
                    "current": projections["patrimonio_liquido"]["current_value"],
                    "projected": projections["patrimonio_liquido"]["projected_value"],
                    "change_percent": projections["patrimonio_liquido"]["change_percent"],
                    "trend": projections["patrimonio_liquido"]["trend"],
                },
            },
            "totals": {
                "total_ativo": total_ativo,
                "total_passivo": total_passivo,
                "total_patrimonio_liquido": total_pl,
                "balance_check": abs(total_ativo - (total_passivo + total_pl)) < 0.01,
            },
            "indicators": {
                "liquidity_ratio": liquidity_ratio,
                "debt_ratio": debt_ratio,
                "liquidity_status": (
                    "saudavel" if liquidity_ratio >= 1
                    else "atencao" if liquidity_ratio >= 0.5 else "critico"
                ),
                "debt_status": (
                    "baixo" if debt_ratio < 40
                    else "moderado" if debt_ratio < 70 else "alto"
                ),
            },
            "trends": trends,
            "confidence": confidence,
            "confidence_level": (
                "alta" if confidence >= 75 else "media" if confidence >= 50 else "baixa"
            ),
            "ai_model": "accounting-forecast-v1.0",
            "generated_at": datetime.now().isoformat(),
        }

    async def _get_latest_trial_balance(
        self,
        condominio_id: UUID,
    ) -> Optional[TrialBalance]:
        """Busca ultimo balancete."""
        query = (
            select(TrialBalance)
            .where(
                and_(
                    TrialBalance.condominio_id == condominio_id,
                    TrialBalance.status == BalanceStatus.PUBLICADO.value,
                    TrialBalance.ativo.is_(True),
                )
            )
            .order_by(TrialBalance.reference_date.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _collect_balance_history(
        self,
        condominio_id: UUID,
        months: int = 12,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Coleta historico de balancetes."""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        query = (
            select(TrialBalance)
            .where(
                and_(
                    TrialBalance.condominio_id == condominio_id,
                    TrialBalance.reference_date >= start_date,
                    TrialBalance.reference_date <= end_date,
                    TrialBalance.ativo.is_(True),
                )
            )
            .order_by(TrialBalance.reference_date.asc())
        )

        result = await self.session.execute(query)
        balances = list(result.scalars().all())

        # Agrupa por grupo de contas
        history: Dict[str, List[Dict[str, Any]]] = {
            "ativo_circulante": [],
            "ativo_nao_circulante": [],
            "passivo_circulante": [],
            "passivo_nao_circulante": [],
            "patrimonio_liquido": [],
        }

        for balance in balances:
            history["ativo_circulante"].append(
                {
                    "date": balance.reference_date,
                    "value": float(balance.total_current_assets or 0),
                }
            )
            history["ativo_nao_circulante"].append(
                {
                    "date": balance.reference_date,
                    "value": float(balance.total_non_current_assets or 0),
                }
            )
            history["passivo_circulante"].append(
                {
                    "date": balance.reference_date,
                    "value": float(balance.total_current_liabilities or 0),
                }
            )
            history["passivo_nao_circulante"].append(
                {
                    "date": balance.reference_date,
                    "value": float(balance.total_non_current_liabilities or 0),
                }
            )
            history["patrimonio_liquido"].append(
                {
                    "date": balance.reference_date,
                    "value": float(balance.total_equity or 0),
                }
            )

        return history

    def _analyze_balance_trends(
        self,
        historical_data: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Analisa tendencias nos dados historicos."""
        trends = {}

        for group, data in historical_data.items():
            if len(data) < 2:
                trends[group] = {"direction": "estavel", "change_rate": 0, "volatility": 0}
                continue

            values = [d["value"] for d in data]
            first_half_avg = (
                sum(values[: len(values) // 2]) / (len(values) // 2)
                if len(values) >= 2 else values[0]
            )
            second_half_avg = (
                sum(values[len(values) // 2 :]) / len(values[len(values) // 2 :])
                if len(values) >= 2 else values[-1]
            )

            if first_half_avg > 0:
                change_rate = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            else:
                change_rate = 0

            # Calcula volatilidade
            avg = sum(values) / len(values)
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            volatility = (variance**0.5 / avg * 100) if avg > 0 else 0

            direction = (
                "crescente" if change_rate > 5
                else "decrescente" if change_rate < -5 else "estavel"
            )

            trends[group] = {
                "direction": direction,
                "change_rate": change_rate,
                "volatility": volatility,
            }

        return trends

    def _project_account_group(
        self,
        historical_values: List[Dict[str, Any]],
        months_ahead: int,
    ) -> Dict[str, Any]:
        """Projeta valor futuro para um grupo de contas."""
        if not historical_values:
            return {
                "current_value": 0,
                "projected_value": 0,
                "change_percent": 0,
                "trend": "sem_dados",
            }

        current_value = historical_values[-1]["value"] if historical_values else 0

        if len(historical_values) < 2:
            return {
                "current_value": current_value,
                "projected_value": current_value,
                "change_percent": 0,
                "trend": "estavel",
            }

        # Calcula taxa de crescimento mensal media
        monthly_changes = []
        for i in range(1, len(historical_values)):
            prev = historical_values[i - 1]["value"]
            curr = historical_values[i]["value"]
            if prev > 0:
                monthly_changes.append((curr - prev) / prev)

        if not monthly_changes:
            return {
                "current_value": current_value,
                "projected_value": current_value,
                "change_percent": 0,
                "trend": "estavel",
            }

        avg_monthly_change = sum(monthly_changes) / len(monthly_changes)

        # Projeta valor futuro
        projected_value = current_value * ((1 + avg_monthly_change) ** months_ahead)

        change_percent = (
            ((projected_value - current_value) / current_value * 100)
            if current_value > 0 else 0
        )

        trend = (
            "crescente" if avg_monthly_change > 0.01
            else "decrescente" if avg_monthly_change < -0.01 else "estavel"
        )

        return {
            "current_value": current_value,
            "projected_value": projected_value,
            "change_percent": change_percent,
            "trend": trend,
        }

    def _calculate_forecast_confidence(
        self,
        historical_data: Dict[str, List[Dict[str, Any]]],
        trends: Dict[str, Any],
    ) -> int:
        """Calcula nivel de confianca da previsao."""
        confidence = 50  # Base

        # Mais dados historicos = mais confianca
        data_points = len(historical_data.get("ativo_circulante", []))
        if data_points >= 12:
            confidence += 25
        elif data_points >= 6:
            confidence += 15
        elif data_points >= 3:
            confidence += 5

        # Baixa volatilidade = mais confianca
        avg_volatility = (
            sum(t.get("volatility", 50) for t in trends.values()) / len(trends)
            if trends
            else 50
        )

        if avg_volatility < 10:
            confidence += 20
        elif avg_volatility < 25:
            confidence += 10
        elif avg_volatility > 50:
            confidence -= 10

        return min(100, max(0, confidence))

    # =========================================================================
    # OTIMIZACAO DE CENTROS DE CUSTO
    # =========================================================================

    async def optimize_cost_center_allocation(
        self,
        condominio_id: UUID,
    ) -> Dict[str, Any]:
        """Sugere otimizacoes na alocacao de centros de custo."""
        logger.info(f"Analisando centros de custo para {condominio_id}")

        # Busca centros de custo ativos
        cost_centers = await self._get_active_cost_centers(condominio_id)

        if not cost_centers:
            return {
                "error": "Nenhum centro de custo encontrado",
                "condominio_id": str(condominio_id),
            }

        # Analisa utilizacao
        usage_analysis = await self._analyze_cost_center_usage(
            condominio_id, cost_centers
        )

        # Identifica problemas
        issues = []
        suggestions = []

        # 1. Centros de custo sem uso
        unused = [
            cc for cc in cost_centers
            if usage_analysis.get(str(cc.id), {}).get("usage_count", 0) == 0
        ]
        if unused:
            issues.append(
                {
                    "type": "centros_sem_uso",
                    "count": len(unused),
                    "centers": [
                        {"id": str(cc.id), "code": cc.code, "name": cc.name}
                        for cc in unused
                    ],
                    "severity": "media",
                    "impact": "Estrutura de custos desnecessariamente complexa",
                }
            )
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "desativar_centros",
                    "title": "Desativar centros de custo sem uso",
                    "description": (
                        f"{len(unused)} centro(s) de custo nao tem lancamentos. "
                        "Considere desativa-los."
                    ),
                    "affected_centers": [cc.code for cc in unused],
                    "effort": "baixo",
                    "priority": "media",
                }
            )

        # 2. Centros de custo com uso muito baixo
        low_usage = [
            cc
            for cc in cost_centers
            if 0 < usage_analysis.get(str(cc.id), {}).get("usage_count", 0) < 5
        ]
        if low_usage:
            issues.append(
                {
                    "type": "centros_baixo_uso",
                    "count": len(low_usage),
                    "centers": [
                        {
                            "id": str(cc.id),
                            "code": cc.code,
                            "name": cc.name,
                            "usage": usage_analysis.get(str(cc.id), {}).get("usage_count", 0),
                        }
                        for cc in low_usage
                    ],
                    "severity": "baixa",
                    "impact": "Possivel fragmentacao excessiva de custos",
                }
            )
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "consolidar_centros",
                    "title": "Considerar consolidacao de centros",
                    "description": (
                        f"{len(low_usage)} centro(s) com poucos lancamentos "
                        "podem ser consolidados com centros relacionados"
                    ),
                    "affected_centers": [cc.code for cc in low_usage],
                    "effort": "medio",
                    "priority": "baixa",
                }
            )

        # 3. Concentracao excessiva
        high_concentration = await self._detect_cost_concentration(usage_analysis)
        if high_concentration:
            issues.append(
                {
                    "type": "concentracao_custos",
                    "top_centers": high_concentration,
                    "severity": "alta",
                    "impact": "Dificuldade em analisar custos detalhadamente",
                }
            )
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "detalhar_custos",
                    "title": "Detalhar centros de custo concentrados",
                    "description": (
                        "Centros com alta concentracao podem ser "
                        "subdivididos para melhor analise"
                    ),
                    "affected_centers": [c["code"] for c in high_concentration],
                    "effort": "alto",
                    "priority": "media",
                }
            )

        # 4. Verifica hierarquia
        hierarchy_issues = await self._check_hierarchy_issues(cost_centers)
        issues.extend(hierarchy_issues)

        # Calcula metricas gerais
        total_centers = len(cost_centers)
        active_centers = len([
            cc for cc in cost_centers
            if usage_analysis.get(str(cc.id), {}).get("usage_count", 0) > 0
        ])

        return {
            "condominio_id": str(condominio_id),
            "summary": {
                "total_cost_centers": total_centers,
                "active_cost_centers": active_centers,
                "inactive_cost_centers": total_centers - active_centers,
                "utilization_rate": (
                    (active_centers / total_centers * 100) if total_centers > 0 else 0
                ),
            },
            "usage_analysis": usage_analysis,
            "issues": issues,
            "suggestions": suggestions,
            "health_score": self._calculate_cost_center_health(issues, total_centers),
            "ai_model": "cost-center-optimizer-v1.0",
            "generated_at": datetime.now().isoformat(),
        }

    async def _get_active_cost_centers(
        self,
        condominio_id: UUID,
    ) -> List[CostCenter]:
        """Busca centros de custo ativos."""
        query = select(CostCenter).where(
            and_(
                CostCenter.condominio_id == condominio_id,
                CostCenter.status == CostCenterStatus.ATIVO.value,
                CostCenter.ativo.is_(True),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _analyze_cost_center_usage(
        self,
        condominio_id: UUID,
        cost_centers: List[CostCenter],
    ) -> Dict[str, Dict[str, Any]]:
        """Analisa utilizacao de cada centro de custo."""
        usage = {}

        # Periodo de analise: ultimos 12 meses
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        for cc in cost_centers:
            # Conta lancamentos
            query = (
                select(func.count(JournalEntryLine.id), func.sum(JournalEntryLine.debit_value))
                .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
                .where(
                    and_(
                        JournalEntry.condominio_id == condominio_id,
                        JournalEntry.entry_date >= start_date,
                        JournalEntry.entry_date <= end_date,
                        JournalEntryLine.cost_center_id == cc.id,
                        JournalEntry.ativo.is_(True),
                    )
                )
            )

            result = await self.session.execute(query)
            row = result.one()

            usage[str(cc.id)] = {
                "code": cc.code,
                "name": cc.name,
                "usage_count": row[0] or 0,
                "total_value": float(row[1] or 0),
            }

        return usage

    async def _detect_cost_concentration(
        self,
        usage_analysis: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Detecta concentracao excessiva em poucos centros."""
        if not usage_analysis:
            return []

        total_value = sum(u.get("total_value", 0) for u in usage_analysis.values())

        if total_value == 0:
            return []

        # Calcula participacao de cada centro
        high_concentration = []
        for cc_id, data in usage_analysis.items():
            percentage = (data.get("total_value", 0) / total_value * 100) if total_value > 0 else 0
            if percentage > 30:  # Mais de 30% em um unico centro
                high_concentration.append(
                    {
                        "id": cc_id,
                        "code": data.get("code"),
                        "name": data.get("name"),
                        "percentage": percentage,
                        "value": data.get("total_value"),
                    }
                )

        return sorted(high_concentration, key=lambda x: x["percentage"], reverse=True)

    async def _check_hierarchy_issues(
        self,
        cost_centers: List[CostCenter],
    ) -> List[Dict[str, Any]]:
        """Verifica problemas na hierarquia de centros de custo."""
        issues = []

        # Verifica centros sem pai quando deveriam ter
        orphans = [
            cc
            for cc in cost_centers
            if cc.level and cc.level > 1 and not cc.parent_id
        ]

        if orphans:
            issues.append(
                {
                    "type": "hierarquia_incompleta",
                    "count": len(orphans),
                    "centers": [
                        {"id": str(cc.id), "code": cc.code, "name": cc.name}
                        for cc in orphans
                    ],
                    "severity": "media",
                    "impact": "Estrutura hierarquica inconsistente",
                }
            )

        return issues

    def _calculate_cost_center_health(
        self,
        issues: List[Dict[str, Any]],
        total_centers: int,  # pylint: disable=unused-argument
    ) -> int:
        """Calcula score de saude da estrutura de centros de custo."""
        score = 100

        for issue in issues:
            severity = issue.get("severity", "baixa")
            if severity == "alta":
                score -= 20
            elif severity == "media":
                score -= 10
            else:
                score -= 5

        return max(0, min(100, score))

    # =========================================================================
    # ANALISE DRE
    # =========================================================================

    async def analyze_income_statement(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self,
        condominio_id: UUID,
        period_start: date,
        period_end: date,
    ) -> Dict[str, Any]:
        """Analisa DRE do periodo."""
        logger.info(f"Analisando DRE para {condominio_id} de {period_start} a {period_end}")

        # Busca lancamentos do periodo
        entries = await self._get_journal_entries(condominio_id, period_start, period_end)

        if not entries:
            return {
                "error": "Nenhum lancamento encontrado no periodo",
                "condominio_id": str(condominio_id),
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            }

        # Agrupa por natureza de conta
        revenues = Decimal("0")
        expenses = Decimal("0")
        revenue_breakdown: Dict[str, Decimal] = {}
        expense_breakdown: Dict[str, Decimal] = {}

        for entry in entries:
            lines_query = select(JournalEntryLine).where(
                JournalEntryLine.journal_entry_id == entry.id
            )
            result = await self.session.execute(lines_query)
            lines = list(result.scalars().all())

            for line in lines:
                # Busca conta para determinar natureza
                account_query = select(AccountingAccount).where(
                    AccountingAccount.id == line.account_id
                )
                account_result = await self.session.execute(account_query)
                account = account_result.scalar_one_or_none()

                if not account:
                    continue

                if account.account_type == AccountType.RECEITA.value:
                    value = line.credit_value or Decimal("0")
                    revenues += value
                    category = account.parent_code or account.code
                    if category not in revenue_breakdown:
                        revenue_breakdown[category] = Decimal("0")
                    revenue_breakdown[category] += value

                elif account.account_type == AccountType.DESPESA.value:
                    value = line.debit_value or Decimal("0")
                    expenses += value
                    category = account.parent_code or account.code
                    if category not in expense_breakdown:
                        expense_breakdown[category] = Decimal("0")
                    expense_breakdown[category] += value

        # Calcula resultado
        net_income = revenues - expenses
        margin = (net_income / revenues * 100) if revenues > 0 else Decimal("0")

        # Compara com periodo anterior
        prev_start = period_start - timedelta(days=(period_end - period_start).days + 1)
        prev_end = period_start - timedelta(days=1)
        prev_entries = await self._get_journal_entries(condominio_id, prev_start, prev_end)

        prev_revenues = Decimal("0")
        prev_expenses = Decimal("0")

        for entry in prev_entries:
            lines_query = select(JournalEntryLine).where(
                JournalEntryLine.journal_entry_id == entry.id
            )
            result = await self.session.execute(lines_query)
            lines = list(result.scalars().all())

            for line in lines:
                account_query = select(AccountingAccount).where(
                    AccountingAccount.id == line.account_id
                )
                account_result = await self.session.execute(account_query)
                account = account_result.scalar_one_or_none()

                if account:
                    if account.account_type == AccountType.RECEITA.value:
                        prev_revenues += line.credit_value or Decimal("0")
                    elif account.account_type == AccountType.DESPESA.value:
                        prev_expenses += line.debit_value or Decimal("0")

        prev_net_income = prev_revenues - prev_expenses

        # Calcula variacoes
        revenue_change = (
            ((revenues - prev_revenues) / prev_revenues * 100)
            if prev_revenues > 0 else Decimal("0")
        )
        expense_change = (
            ((expenses - prev_expenses) / prev_expenses * 100)
            if prev_expenses > 0 else Decimal("0")
        )
        income_change = (
            ((net_income - prev_net_income) / abs(prev_net_income) * 100)
            if prev_net_income != 0 else Decimal("0")
        )

        # Gera insights
        insights = self._generate_dre_insights(
            revenues,
            expenses,
            net_income,
            revenue_change,
            expense_change,
            revenue_breakdown,
            expense_breakdown,
        )

        return {
            "condominio_id": str(condominio_id),
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "summary": {
                "total_revenues": float(revenues),
                "total_expenses": float(expenses),
                "net_income": float(net_income),
                "margin_percent": float(margin),
            },
            "breakdown": {
                "revenues": {k: float(v) for k, v in revenue_breakdown.items()},
                "expenses": {k: float(v) for k, v in expense_breakdown.items()},
            },
            "comparison": {
                "previous_period": {
                    "start": prev_start.isoformat(),
                    "end": prev_end.isoformat(),
                },
                "previous_revenues": float(prev_revenues),
                "previous_expenses": float(prev_expenses),
                "previous_net_income": float(prev_net_income),
                "revenue_change_percent": float(revenue_change),
                "expense_change_percent": float(expense_change),
                "net_income_change_percent": float(income_change),
            },
            "insights": insights,
            "entry_count": len(entries),
            "ai_model": "income-statement-analyzer-v1.0",
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_dre_insights(
        self,
        revenues: Decimal,
        expenses: Decimal,  # pylint: disable=unused-argument
        net_income: Decimal,
        revenue_change: Decimal,
        expense_change: Decimal,
        revenue_breakdown: Dict[str, Decimal],  # pylint: disable=unused-argument
        expense_breakdown: Dict[str, Decimal],
    ) -> List[Dict[str, Any]]:
        """Gera insights sobre a DRE."""
        insights = []

        # Insight sobre resultado
        if net_income > 0:
            insights.append(
                {
                    "type": "resultado_positivo",
                    "severity": "info",
                    "title": "Resultado positivo no periodo",
                    "description": (
                        f"Superavit de R$ {float(net_income):,.2f} "
                        f"({float(net_income/revenues*100):.1f}% de margem)"
                        if revenues > 0
                        else f"Superavit de R$ {float(net_income):,.2f}"
                    ),
                }
            )
        else:
            insights.append(
                {
                    "type": "resultado_negativo",
                    "severity": "alta",
                    "title": "Resultado negativo no periodo",
                    "description": (
                        f"Deficit de R$ {float(abs(net_income)):,.2f}. "
                        f"Despesas excedem receitas em "
                        f"{float(abs(net_income)/revenues*100):.1f}%"
                        if revenues > 0
                        else f"Deficit de R$ {float(abs(net_income)):,.2f}"
                    ),
                }
            )

        # Insight sobre variacao de receitas
        if revenue_change > 10:
            insights.append(
                {
                    "type": "receita_crescendo",
                    "severity": "info",
                    "title": "Crescimento de receitas",
                    "description": (
                        f"Receitas cresceram {float(revenue_change):.1f}% "
                        "em relacao ao periodo anterior"
                    ),
                }
            )
        elif revenue_change < -10:
            insights.append(
                {
                    "type": "receita_caindo",
                    "severity": "alta",
                    "title": "Queda de receitas",
                    "description": (
                        f"Receitas cairam {float(abs(revenue_change)):.1f}% "
                        "em relacao ao periodo anterior"
                    ),
                }
            )

        # Insight sobre variacao de despesas
        if expense_change > 15:
            insights.append(
                {
                    "type": "despesa_crescendo",
                    "severity": "media",
                    "title": "Aumento significativo de despesas",
                    "description": (
                        f"Despesas aumentaram {float(expense_change):.1f}%. "
                        "Recomenda-se revisar os principais gastos."
                    ),
                }
            )
        elif expense_change < -10:
            insights.append(
                {
                    "type": "despesa_reduzindo",
                    "severity": "info",
                    "title": "Reducao de despesas",
                    "description": (
                        f"Despesas reduziram {float(abs(expense_change)):.1f}% "
                        "em relacao ao periodo anterior"
                    ),
                }
            )

        # Insight sobre concentracao de despesas
        if expense_breakdown:
            total_expenses = sum(expense_breakdown.values())
            top_expense = max(expense_breakdown.items(), key=lambda x: x[1])
            top_percentage = (top_expense[1] / total_expenses * 100) if total_expenses > 0 else 0

            if top_percentage > 40:
                insights.append(
                    {
                        "type": "concentracao_despesa",
                        "severity": "media",
                        "title": "Concentracao de despesas",
                        "description": (
                            f"A categoria {top_expense[0]} representa "
                            f"{float(top_percentage):.1f}% das despesas totais"
                        ),
                    }
                )

        return insights

    # =========================================================================
    # RECOMENDACOES GERAIS
    # =========================================================================

    async def get_accounting_recommendations(
        self,
        condominio_id: UUID,
    ) -> Dict[str, Any]:
        """Gera recomendacoes gerais de contabilidade."""
        logger.info(f"Gerando recomendacoes contabeis para {condominio_id}")

        recommendations = []

        # 1. Verifica fechamento de periodos
        period_recs = await self._check_period_closures(condominio_id)
        recommendations.extend(period_recs)

        # 2. Verifica lancamentos pendentes
        pending_recs = await self._check_pending_entries(condominio_id)
        recommendations.extend(pending_recs)

        # 3. Verifica balancete
        balance_recs = await self._check_trial_balance(condominio_id)
        recommendations.extend(balance_recs)

        # 4. Verifica plano de contas
        chart_recs = await self._check_chart_of_accounts(condominio_id)
        recommendations.extend(chart_recs)

        # Ordena por prioridade
        priority_order = {"alta": 0, "media": 1, "baixa": 2}
        recommendations = sorted(
            recommendations,
            key=lambda x: priority_order.get(x.get("priority", "baixa"), 2),
        )

        return {
            "condominio_id": str(condominio_id),
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "by_priority": {
                "alta": len([r for r in recommendations if r.get("priority") == "alta"]),
                "media": len([r for r in recommendations if r.get("priority") == "media"]),
                "baixa": len([r for r in recommendations if r.get("priority") == "baixa"]),
            },
            "ai_model": "accounting-advisor-v1.0",
            "generated_at": datetime.now().isoformat(),
        }

    async def _check_period_closures(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Verifica fechamento de periodos."""
        recommendations = []

        # Verifica periodos que deveriam estar fechados
        today = date.today()
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)

        query = select(AccountingPeriod).where(
            and_(
                AccountingPeriod.condominio_id == condominio_id,
                AccountingPeriod.end_date < last_month_end,
                AccountingPeriod.status.in_([
                    PeriodStatus.ABERTO.value, PeriodStatus.EM_FECHAMENTO.value
                ]),
                AccountingPeriod.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        open_periods = list(result.scalars().all())

        if open_periods:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "periodos_abertos",
                    "title": "Periodos contabeis pendentes de fechamento",
                    "description": f"{len(open_periods)} periodo(s) anteriores ainda estao abertos",
                    "priority": "alta",
                    "action": "Revisar e fechar os periodos pendentes",
                    "affected_items": [
                        {
                            "id": str(p.id),
                            "reference": p.reference,
                            "end_date": p.end_date.isoformat() if p.end_date else None,
                        }
                        for p in open_periods
                    ],
                }
            )

        return recommendations

    async def _check_pending_entries(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Verifica lancamentos pendentes."""
        recommendations = []

        # Conta lancamentos em rascunho
        query = select(func.count(JournalEntry.id)).where(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.status == EntryStatus.RASCUNHO.value,
                JournalEntry.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        draft_count = result.scalar_one() or 0

        if draft_count > 0:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "lancamentos_rascunho",
                    "title": "Lancamentos em rascunho",
                    "description": f"{draft_count} lancamento(s) aguardando finalizacao",
                    "priority": "media",
                    "action": "Revisar e aprovar lancamentos pendentes",
                }
            )

        # Conta lancamentos pendentes de aprovacao
        query = select(func.count(JournalEntry.id)).where(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.status == EntryStatus.PENDENTE.value,
                JournalEntry.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        pending_count = result.scalar_one() or 0

        if pending_count > 0:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "lancamentos_pendentes",
                    "title": "Lancamentos aguardando aprovacao",
                    "description": f"{pending_count} lancamento(s) precisam de aprovacao",
                    "priority": "alta" if pending_count > 10 else "media",
                    "action": "Aprovar ou rejeitar lancamentos pendentes",
                }
            )

        return recommendations

    async def _check_trial_balance(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Verifica situacao do balancete."""
        recommendations = []

        # Verifica se existe balancete do mes anterior
        today = date.today()
        last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

        query = select(TrialBalance).where(
            and_(
                TrialBalance.condominio_id == condominio_id,
                func.extract("year", TrialBalance.reference_date) == last_month.year,
                func.extract("month", TrialBalance.reference_date) == last_month.month,
                TrialBalance.status == BalanceStatus.PUBLICADO.value,
                TrialBalance.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        balance = result.scalar_one_or_none()

        if not balance:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "balancete_pendente",
                    "title": "Balancete do mes anterior nao gerado",
                    "description": (
                        f"O balancete de {last_month.strftime('%m/%Y')} "
                        "ainda nao foi publicado"
                    ),
                    "priority": "alta",
                    "action": "Gerar e publicar o balancete do periodo",
                }
            )

        return recommendations

    async def _check_chart_of_accounts(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Verifica plano de contas."""
        recommendations = []

        # Verifica se existe plano de contas ativo
        query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.condominio_id == condominio_id,
                ChartOfAccounts.status == ChartStatus.ATIVO.value,
                ChartOfAccounts.ativo.is_(True),
            )
        )

        result = await self.session.execute(query)
        charts = list(result.scalars().all())

        if not charts:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "plano_contas_ausente",
                    "title": "Nenhum plano de contas ativo",
                    "description": "O condominio nao possui plano de contas configurado",
                    "priority": "alta",
                    "action": "Criar ou ativar um plano de contas",
                }
            )
        elif len(charts) > 1:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "multiplos_planos",
                    "title": "Multiplos planos de contas ativos",
                    "description": (
                        f"{len(charts)} planos de contas ativos. "
                        "Recomenda-se manter apenas um ativo"
                    ),
                    "priority": "media",
                    "action": "Revisar e desativar planos de contas desnecessarios",
                }
            )

        return recommendations
