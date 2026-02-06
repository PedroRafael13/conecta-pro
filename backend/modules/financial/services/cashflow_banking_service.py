"""Service que integra fluxo de caixa com Open Banking.

Combina projecoes de fluxo de caixa com saldo real
obtido via Open Banking para visao consolidada.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, UTC
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.services.cashflow_service import CashFlowProjection, CashFlowService
from modules.integrations.banking import (
    AccountBalance,
    BankCredentials,
    BankingAdapterError,
    BankingService,
)

logger = logging.getLogger(__name__)


@dataclass
class BankAccountConfig:
    """Configuracao de conta bancaria para integracao."""

    account_id: str
    bank_code: str
    credentials: BankCredentials
    is_primary: bool = False


@dataclass
class ConsolidatedBalance:
    """Saldo consolidado de multiplas contas."""

    total_available: Decimal = Decimal("0")
    total_blocked: Decimal = Decimal("0")
    total_balance: Decimal = Decimal("0")
    accounts: Dict[str, AccountBalance] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    errors: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Converte para dicionario."""
        return {
            "total_available": float(self.total_available),
            "total_blocked": float(self.total_blocked),
            "total_balance": float(self.total_balance),
            "accounts": {
                k: {
                    "available": float(v.available),
                    "blocked": float(v.blocked),
                    "total": float(v.total),
                    "currency": v.currency,
                }
                for k, v in self.accounts.items()
            },
            "updated_at": self.updated_at.isoformat(),
            "errors": self.errors,
        }


@dataclass
class CashFlowWithBalance:
    """Projecao de fluxo de caixa com saldo inicial real."""

    current_balance: ConsolidatedBalance
    projections: List[CashFlowProjection]
    alerts: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Converte para dicionario."""
        return {
            "current_balance": self.current_balance.to_dict(),
            "projections": [p.to_dict() for p in self.projections],
            "alerts": self.alerts,
        }


class CashFlowBankingService:
    """Service que integra fluxo de caixa com Open Banking.

    Fornece visao consolidada do fluxo de caixa usando
    saldo real das contas bancarias via Open Banking.
    """

    # Limite de saldo baixo para alertas (configuravel)
    LOW_BALANCE_THRESHOLD = Decimal("10000.00")

    # Limite critico para alertas urgentes
    CRITICAL_BALANCE_THRESHOLD = Decimal("5000.00")

    def __init__(
        self,
        session: AsyncSession,
        banking_service: Optional[BankingService] = None,
    ):
        """Inicializa o service.

        Args:
            session: Sessao do banco de dados.
            banking_service: Servico de banking. Se None, cria novo.
        """
        self.session = session
        self.cashflow_service = CashFlowService(session)
        self.banking_service = banking_service or BankingService()
        self._account_configs: Dict[str, BankAccountConfig] = {}

    def register_bank_account(
        self,
        account_id: str,
        bank_code: str,
        credentials: BankCredentials,
        is_primary: bool = False,
    ) -> None:
        """Registra conta bancaria para integracao.

        Args:
            account_id: Identificador unico da conta.
            bank_code: Codigo do banco (001, 341, 237).
            credentials: Credenciais de acesso.
            is_primary: Se e a conta principal.
        """
        config = BankAccountConfig(
            account_id=account_id,
            bank_code=bank_code,
            credentials=credentials,
            is_primary=is_primary,
        )
        self._account_configs[account_id] = config

        self.banking_service.register_account(
            account_id=account_id,
            bank_code=bank_code,
            credentials=credentials,
        )

        logger.info(
            "Conta bancaria registrada",
            extra={"account_id": account_id, "bank_code": bank_code},
        )

    def unregister_bank_account(self, account_id: str) -> None:
        """Remove conta bancaria do registro.

        Args:
            account_id: Identificador da conta.
        """
        if account_id in self._account_configs:
            del self._account_configs[account_id]
            self.banking_service.unregister_account(account_id)
            logger.info("Conta bancaria removida", extra={"account_id": account_id})

    async def get_consolidated_balance(self) -> ConsolidatedBalance:
        """Obtem saldo consolidado de todas as contas registradas.

        Returns:
            Saldo consolidado com detalhes por conta.
        """
        consolidated = ConsolidatedBalance()

        for account_id in self._account_configs:
            try:
                balance = await self.banking_service.get_balance(account_id)
                consolidated.accounts[account_id] = balance
                consolidated.total_available += balance.available
                consolidated.total_blocked += balance.blocked
                consolidated.total_balance += balance.total

            except BankingAdapterError as exc:
                logger.warning(
                    "Erro ao obter saldo",
                    extra={"account_id": account_id, "error": str(exc)},
                )
                consolidated.errors[account_id] = str(exc)

        consolidated.updated_at = datetime.now(UTC)
        return consolidated

    async def get_projection_with_balance(
        self,
        condominio_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = "day",
        low_balance_threshold: Optional[Decimal] = None,
    ) -> CashFlowWithBalance:
        """Obtem projecao de fluxo de caixa com saldo real.

        Combina saldo atual das contas via Open Banking com
        projecoes de pagamentos/recebimentos futuros.

        Args:
            condominio_id: ID do condominio.
            start_date: Data inicial (default: hoje).
            end_date: Data final (default: hoje + 90 dias).
            group_by: Agrupamento (day, week, month).
            low_balance_threshold: Limite para alertas de saldo baixo.

        Returns:
            Projecao com saldo atual e alertas.
        """
        threshold = low_balance_threshold or self.LOW_BALANCE_THRESHOLD

        # Obtem saldo atual via Open Banking
        current_balance = await self.get_consolidated_balance()

        # Obtem projecoes de fluxo de caixa
        projections = await self.cashflow_service.get_projection(
            condominio_id=condominio_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )

        # Recalcula saldo acumulado usando saldo real como base
        running_balance = current_balance.total_available

        for proj in projections:
            running_balance += proj.balance  # balance ja tem sinal correto
            proj.cumulative_balance = running_balance

        # Gera alertas
        alerts = self._generate_alerts(
            current_balance=current_balance,
            projections=projections,
            threshold=threshold,
        )

        return CashFlowWithBalance(
            current_balance=current_balance,
            projections=projections,
            alerts=alerts,
        )

    def _generate_alerts(
        self,
        current_balance: ConsolidatedBalance,
        projections: List[CashFlowProjection],
        threshold: Decimal,
    ) -> List[Dict]:
        """Gera alertas baseados no fluxo de caixa.

        Args:
            current_balance: Saldo atual consolidado.
            projections: Projecoes futuras.
            threshold: Limite para saldo baixo.

        Returns:
            Lista de alertas.
        """
        alerts: List[Dict] = []

        # Alerta se saldo atual ja esta baixo
        if current_balance.total_available < self.CRITICAL_BALANCE_THRESHOLD:
            alerts.append(
                {
                    "type": "CRITICAL_BALANCE",
                    "severity": "critical",
                    "message": "Saldo atual abaixo do limite critico",
                    "current_balance": float(current_balance.total_available),
                    "threshold": float(self.CRITICAL_BALANCE_THRESHOLD),
                    "date": date.today().isoformat(),
                }
            )
        elif current_balance.total_available < threshold:
            alerts.append(
                {
                    "type": "LOW_BALANCE",
                    "severity": "warning",
                    "message": "Saldo atual abaixo do limite recomendado",
                    "current_balance": float(current_balance.total_available),
                    "threshold": float(threshold),
                    "date": date.today().isoformat(),
                }
            )

        # Alertas para projecoes futuras
        for proj in projections:
            if proj.cumulative_balance < self.CRITICAL_BALANCE_THRESHOLD:
                alerts.append(
                    {
                        "type": "PROJECTED_CRITICAL",
                        "severity": "critical",
                        "message": f"Saldo projetado critico em {proj.date}",
                        "projected_balance": float(proj.cumulative_balance),
                        "threshold": float(self.CRITICAL_BALANCE_THRESHOLD),
                        "date": proj.date.isoformat(),
                    }
                )
            elif proj.cumulative_balance < threshold:
                alerts.append(
                    {
                        "type": "PROJECTED_LOW",
                        "severity": "warning",
                        "message": f"Saldo projetado baixo em {proj.date}",
                        "projected_balance": float(proj.cumulative_balance),
                        "threshold": float(threshold),
                        "date": proj.date.isoformat(),
                    }
                )

        # Alertas para erros de conexao
        for account_id, error in current_balance.errors.items():
            alerts.append(
                {
                    "type": "CONNECTION_ERROR",
                    "severity": "error",
                    "message": f"Erro ao conectar conta {account_id}: {error}",
                    "account_id": account_id,
                    "date": date.today().isoformat(),
                }
            )

        return alerts

    async def get_investment_suggestions(
        self,
        condominio_id: UUID,
        min_surplus_days: int = 30,
    ) -> List[Dict]:
        """Sugere investimentos baseado no fluxo de caixa.

        Analisa o fluxo de caixa e sugere quando ha
        excesso de saldo que pode ser investido.

        Args:
            condominio_id: ID do condominio.
            min_surplus_days: Dias minimos de saldo excedente.

        Returns:
            Lista de sugestoes de investimento.
        """
        suggestions: List[Dict] = []

        # Obtem projecao completa
        result = await self.get_projection_with_balance(
            condominio_id=condominio_id,
            group_by="day",
        )

        if not result.projections:
            return suggestions

        # Analisa saldo minimo no periodo
        min_balance = min(p.cumulative_balance for p in result.projections)

        # Se saldo minimo ainda e alto, sugere investimento
        reserve_needed = self.LOW_BALANCE_THRESHOLD * Decimal("1.5")

        if min_balance > reserve_needed:
            surplus = min_balance - reserve_needed
            suggestions.append(
                {
                    "type": "INVESTMENT_OPPORTUNITY",
                    "amount": float(surplus),
                    "reason": "Saldo excedente consistente no periodo",
                    "min_projected_balance": float(min_balance),
                    "reserve_recommended": float(reserve_needed),
                    "suggestion": "Considere aplicacao em CDB ou fundo de renda fixa",
                }
            )

        # Analisa dias consecutivos com saldo alto
        high_balance_days = sum(
            1 for p in result.projections if p.cumulative_balance > reserve_needed
        )

        if high_balance_days >= min_surplus_days:
            avg_surplus = sum(
                max(p.cumulative_balance - reserve_needed, Decimal("0")) for p in result.projections
            ) / len(result.projections)

            if avg_surplus > Decimal("0"):
                suggestions.append(
                    {
                        "type": "RECURRING_SURPLUS",
                        "average_surplus": float(avg_surplus),
                        "days_with_surplus": high_balance_days,
                        "suggestion": (
                            "Padrao de excesso de caixa identificado. "
                            "Considere investimento programado."
                        ),
                    }
                )

        return suggestions

    async def get_dashboard_data(
        self,
        condominio_id: UUID,
    ) -> Dict:
        """Retorna dados consolidados para dashboard.

        Combina todas as informacoes relevantes para
        exibicao em dashboard de fluxo de caixa.

        Args:
            condominio_id: ID do condominio.

        Returns:
            Dados consolidados do dashboard.
        """
        # Projecao com saldo real
        projection_result = await self.get_projection_with_balance(
            condominio_id=condominio_id,
            group_by="day",
        )

        # Resumo do service de cashflow
        summary = await self.cashflow_service.get_summary(condominio_id)

        # Breakdown por categoria
        category_breakdown = await self.cashflow_service.get_category_breakdown(condominio_id)

        # Top fornecedores
        supplier_breakdown = await self.cashflow_service.get_supplier_breakdown(
            condominio_id,
            limit=5,
        )

        # Tendencia mensal
        monthly_trend = await self.cashflow_service.get_monthly_trend(
            condominio_id,
            months=6,
        )

        # Sugestoes de investimento
        investment_suggestions = await self.get_investment_suggestions(condominio_id)

        return {
            "current_balance": projection_result.current_balance.to_dict(),
            "projections": [p.to_dict() for p in projection_result.projections[:30]],
            "alerts": projection_result.alerts,
            "summary": summary,
            "category_breakdown": category_breakdown,
            "top_suppliers": supplier_breakdown,
            "monthly_trend": monthly_trend,
            "investment_suggestions": investment_suggestions,
            "updated_at": datetime.now(UTC).isoformat(),
        }

    async def close(self) -> None:
        """Fecha conexoes do servico."""
        await self.banking_service.close_all()
