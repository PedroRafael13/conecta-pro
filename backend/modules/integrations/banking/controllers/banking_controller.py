"""
Controller para operações bancárias (Cora, Inter).

Endpoints para consulta de saldos, extratos e status de conexão.
"""

import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from core.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = Path("/opt/conecta-pro/credentials/.env.credentials")


def _load_credentials_env() -> dict[str, str]:
    """Carrega variáveis do arquivo .env.credentials se existir."""
    env_vars: dict[str, str] = {}
    if CREDENTIALS_FILE.exists():
        for line in CREDENTIALS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    return env_vars


router = APIRouter(prefix="/banking", tags=["Banking"])


# --- Response Schemas ---


class BankBalanceItem(BaseModel):
    bank_code: str
    bank_name: str
    account: str
    balance: float
    available_balance: float
    blocked_balance: float
    updated_at: str


class BankingBalancesResponse(BaseModel):
    balances: list[BankBalanceItem]
    total_balance: float
    updated_at: str


class BankTransactionItem(BaseModel):
    id: str
    bank_code: str
    date: str
    description: str
    amount: float
    type: str  # credit | debit
    category: str | None = None
    balance_after: float | None = None


class BankingStatementResponse(BaseModel):
    transactions: list[BankTransactionItem]
    total_credits: float
    total_debits: float
    period_start: str
    period_end: str


class BankConnectionStatus(BaseModel):
    bank_code: str
    bank_name: str
    connected: bool
    last_sync: str | None = None
    error: str | None = None


class BoletoGenerateRequest(BaseModel):
    bank_code: str  # "403" = Cora, "077" = Inter
    amount: float
    due_date: str  # formato ISO: "2026-03-15"
    payer_name: str
    payer_document: str  # CPF ou CNPJ
    description: str


class BoletoResponse(BaseModel):
    success: bool
    bank_code: str
    bank_name: str
    boleto_id: str | None = None
    barcode: str | None = None
    digitable_line: str | None = None
    pdf_url: str | None = None
    pix_qrcode: str | None = None
    pix_copy_paste: str | None = None
    amount: float
    due_date: str
    payer_name: str
    created_at: str
    error: str | None = None


class BoletoListItem(BaseModel):
    boleto_id: str
    bank_code: str
    bank_name: str
    amount: float
    due_date: str
    payer_name: str
    status: str
    barcode: str | None = None
    digitable_line: str | None = None
    pdf_url: str | None = None
    created_at: str | None = None


class BoletoListResponse(BaseModel):
    boletos: list[BoletoListItem]
    total: int


class PixChargeRequest(BaseModel):
    bank_code: str = "403"  # "403" = Cora, "077" = Inter
    amount: float  # Valor em R$
    description: str = "Cobrança Conecta Mais Patrimonial"
    payer_name: str | None = None
    payer_document: str | None = None
    chave_pix: str = "35710481000103"  # CNPJ Conecta Mais como chave PIX padrão
    expiracao_horas: int = 24  # Validade em horas


class PixChargeResponse(BaseModel):
    success: bool
    bank_code: str
    bank_name: str
    charge_id: str | None = None
    pix_qrcode: str | None = None
    pix_copy_paste: str | None = None
    amount: float
    description: str
    chave_pix: str
    expires_at: str | None = None
    created_at: str
    error: str | None = None


class BankTransactionFull(BaseModel):
    transaction_id: str
    date: str
    amount: float
    transaction_type: str
    description: str
    counterpart_name: str | None = None
    counterpart_document: str | None = None
    counterpart_bank: str | None = None
    balance_after: float | None = None
    reference: str | None = None
    category: str | None = None
    bank_code: str
    bank_name: str


class BankStatementFullResponse(BaseModel):
    transactions: list[BankTransactionFull]
    total_credits: float
    total_debits: float
    period_start: str
    period_end: str
    opening_balance: float
    closing_balance: float


# --- Helper ---


def _get_banking_service():
    """Retorna instância do BankingService com adapters configurados."""
    from modules.integrations.banking.adapters import BankCode, BankCredentials
    from modules.integrations.banking.services import BankingService

    service = BankingService()
    env = _load_credentials_env()

    # Registrar Cora
    cora_client_id = env.get("CORA_CLIENT_ID") or os.environ.get("CORA_CLIENT_ID")
    cora_cert = env.get("CORA_CERT_PATH") or os.environ.get("CORA_CERT_PATH")
    cora_key = env.get("CORA_KEY_PATH") or os.environ.get("CORA_KEY_PATH")
    cora_env = env.get("CORA_ENVIRONMENT", "production")
    if cora_client_id and cora_cert and cora_key:
        try:
            cora_creds = BankCredentials(
                client_id=cora_client_id,
                client_secret="",  # Cora usa mTLS, sem client_secret
                certificate_path=cora_cert,
                private_key_path=cora_key,
                environment=cora_env,
            )
            service.register_account(BankCode.CORA, BankCode.CORA, cora_creds)
        except Exception as exc:
            logger.warning("Falha ao registrar Cora: %s", exc)

    # Registrar Inter
    inter_client_id = env.get("INTER_CLIENT_ID") or os.environ.get("INTER_CLIENT_ID")
    inter_secret = env.get("INTER_CLIENT_SECRET") or os.environ.get("INTER_CLIENT_SECRET")
    inter_cert = env.get("INTER_CERT_PATH") or os.environ.get("INTER_CERT_PATH")
    inter_key = env.get("INTER_KEY_PATH") or os.environ.get("INTER_KEY_PATH")
    inter_agency = env.get("INTER_AGENCY") or os.environ.get("INTER_AGENCY")
    inter_account = env.get("INTER_ACCOUNT") or os.environ.get("INTER_ACCOUNT")
    inter_env = env.get("INTER_ENVIRONMENT", "production")
    if inter_client_id and inter_secret and inter_cert and inter_key:
        try:
            inter_creds = BankCredentials(
                client_id=inter_client_id,
                client_secret=inter_secret,
                certificate_path=inter_cert,
                private_key_path=inter_key,
                agency=inter_agency,
                account=inter_account,
                environment=inter_env,
            )
            service.register_account(BankCode.INTER, BankCode.INTER, inter_creds)
        except Exception as exc:
            logger.warning("Falha ao registrar Inter: %s", exc)

    return service


async def _try_adapter_balance(
    service,
    bank_code: str,
    bank_name: str,
    account_label: str,
) -> BankBalanceItem | None:
    """Tenta obter saldo de um adapter registrado."""
    try:
        balance = await service.get_balance(bank_code)
        return BankBalanceItem(
            bank_code=bank_code,
            bank_name=bank_name,
            account=account_label,
            balance=float(balance.total),
            available_balance=float(balance.available),
            blocked_balance=float(balance.blocked),
            updated_at=balance.updated_at.isoformat() if balance.updated_at else datetime.now().isoformat(),
        )
    except Exception as exc:
        logger.debug("Saldo indisponível para %s: %s", bank_name, str(exc))
        return BankBalanceItem(
            bank_code=bank_code,
            bank_name=bank_name,
            account=account_label,
            balance=0,
            available_balance=0,
            blocked_balance=0,
            updated_at=datetime.now().isoformat(),
        )


# --- Endpoints ---


@router.get("/balances", response_model=BankingBalancesResponse)
async def get_bank_balances(
    current_user=Depends(get_current_user),
):
    """Consulta saldos de todas as contas bancárias configuradas."""
    now = datetime.now().isoformat()
    balances: list[BankBalanceItem] = []

    env = _load_credentials_env()
    inter_account = env.get("INTER_ACCOUNT") or os.environ.get("INTER_ACCOUNT") or "****-2"

    # Bancos configurados no sistema
    banks = [
        ("403", "Banco Cora", "Conta Digital"),
        ("077", "Banco Inter", inter_account),
    ]

    service = _get_banking_service()

    for bank_code, bank_name, account_label in banks:
        item = await _try_adapter_balance(service, bank_code, bank_name, account_label)
        if item:
            balances.append(item)

    total = sum(b.available_balance for b in balances)

    return BankingBalancesResponse(
        balances=balances,
        total_balance=total,
        updated_at=now,
    )


@router.get("/statement", response_model=BankingStatementResponse)
async def get_bank_statement(
    days: int = Query(default=30, ge=1, le=365),
    bank_code: str | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    """Consulta extrato bancário recente."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    transactions: list[BankTransactionItem] = []
    service = _get_banking_service()

    banks_to_query = []
    if bank_code:
        banks_to_query.append(bank_code)
    else:
        banks_to_query = ["403", "077"]

    for code in banks_to_query:
        try:
            statement = await service.get_statement(code, start_date, end_date)
            for tx in statement.transactions:
                tx_type = "credit" if tx.amount >= 0 else "debit"
                transactions.append(
                    BankTransactionItem(
                        id=tx.transaction_id,
                        bank_code=code,
                        date=tx.date.isoformat() if tx.date else "",
                        description=tx.description or "",
                        amount=float(abs(tx.amount)),
                        type=tx_type,
                        category=str(tx.transaction_type) if tx.transaction_type else None,
                    )
                )
        except Exception as exc:
            logger.debug("Extrato indisponível para banco %s: %s", code, str(exc))

    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")

    return BankingStatementResponse(
        transactions=transactions,
        total_credits=total_credits,
        total_debits=total_debits,
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
    )


@router.get("/status", response_model=list[BankConnectionStatus])
async def get_bank_status(
    current_user=Depends(get_current_user),
):
    """Consulta status de conexão dos bancos integrados."""
    statuses: list[BankConnectionStatus] = []

    banks = [
        ("403", "Banco Cora"),
        ("077", "Banco Inter"),
    ]

    service = _get_banking_service()

    for bank_code, bank_name in banks:
        try:
            # Tenta obter saldo como health check
            await service.get_balance(bank_code)
            statuses.append(
                BankConnectionStatus(
                    bank_code=bank_code,
                    bank_name=bank_name,
                    connected=True,
                    last_sync=datetime.now().isoformat(),
                )
            )
        except Exception as exc:
            statuses.append(
                BankConnectionStatus(
                    bank_code=bank_code,
                    bank_name=bank_name,
                    connected=False,
                    last_sync=None,
                    error=str(exc),
                )
            )

    return statuses


# Mapeamento banco_code -> (nome legível, método de geração)
_BANK_NAMES = {
    "403": "Banco Cora",
    "077": "Banco Inter",
}


@router.post("/boleto/generate", response_model=BoletoResponse)
async def generate_boleto(
    req: BoletoGenerateRequest,
    current_user=Depends(get_current_user),
):
    """Emite boleto de cobrança via Cora (403) ou Banco Inter (077)."""
    bank_name = _BANK_NAMES.get(req.bank_code, req.bank_code)
    now_iso = datetime.now().isoformat()

    try:
        due_date_obj = date.fromisoformat(req.due_date)
    except ValueError as exc:
        return BoletoResponse(
            success=False,
            bank_code=req.bank_code,
            bank_name=bank_name,
            amount=req.amount,
            due_date=req.due_date,
            payer_name=req.payer_name,
            created_at=now_iso,
            error=f"due_date inválido: {exc}",
        )

    service = _get_banking_service()
    adapter = service._adapters.get(req.bank_code)

    if adapter is None:
        return BoletoResponse(
            success=False,
            bank_code=req.bank_code,
            bank_name=bank_name,
            amount=req.amount,
            due_date=req.due_date,
            payer_name=req.payer_name,
            created_at=now_iso,
            error=f"Banco {req.bank_code} não configurado ou sem credenciais",
        )

    try:
        from decimal import Decimal

        amount_decimal = Decimal(str(req.amount))

        if req.bank_code == "403":
            # Cora: generate_invoice
            result = await adapter.generate_invoice(
                amount=amount_decimal,
                due_date=due_date_obj,
                payer_name=req.payer_name,
                payer_document=req.payer_document,
                description=req.description,
            )
            return BoletoResponse(
                success=True,
                bank_code=req.bank_code,
                bank_name=bank_name,
                boleto_id=result.get("invoice_id"),
                barcode=result.get("barcode"),
                digitable_line=result.get("digitable_line"),
                pdf_url=result.get("pdf_url"),
                pix_qrcode=result.get("pix_qrcode"),
                pix_copy_paste=result.get("pix_copy_paste"),
                amount=req.amount,
                due_date=req.due_date,
                payer_name=req.payer_name,
                created_at=now_iso,
            )

        elif req.bank_code == "077":
            # Inter: generate_boleto
            result = await adapter.generate_boleto(
                amount=amount_decimal,
                due_date=due_date_obj,
                payer_name=req.payer_name,
                payer_document=req.payer_document,
                description=req.description,
            )
            return BoletoResponse(
                success=True,
                bank_code=req.bank_code,
                bank_name=bank_name,
                boleto_id=result.get("boleto_id"),
                barcode=result.get("barcode"),
                digitable_line=result.get("digitable_line"),
                pdf_url=result.get("pdf_url"),
                pix_copy_paste=result.get("pix_qrcode"),  # Inter retorna pixCopiaECola mapeado
                amount=req.amount,
                due_date=req.due_date,
                payer_name=req.payer_name,
                created_at=now_iso,
            )

        else:
            return BoletoResponse(
                success=False,
                bank_code=req.bank_code,
                bank_name=bank_name,
                amount=req.amount,
                due_date=req.due_date,
                payer_name=req.payer_name,
                created_at=now_iso,
                error=f"Emissão de boleto não suportada para banco {req.bank_code}",
            )

    except Exception as exc:
        logger.exception("Erro ao gerar boleto para banco %s: %s", req.bank_code, exc)
        return BoletoResponse(
            success=False,
            bank_code=req.bank_code,
            bank_name=bank_name,
            amount=req.amount,
            due_date=req.due_date,
            payer_name=req.payer_name,
            created_at=now_iso,
            error=str(exc),
        )


@router.post("/pix/generate", response_model=PixChargeResponse)
async def generate_pix_charge(
    req: PixChargeRequest,
    current_user=Depends(get_current_user),
):
    """
    Gera cobrança PIX com QR Code dinâmico.

    - Cora (403): invoice PIX-only → retorna QR Code e copia-e-cola
    - Inter (077): cobrança imediata /pix/v2/cob → retorna copia-e-cola
    - Chave PIX padrão: CNPJ 35710481000103 (Conecta Mais Patrimonial)
    """
    from datetime import datetime, timedelta

    bank_name = _BANK_NAMES.get(req.bank_code, req.bank_code)
    now = datetime.now()
    now_iso = now.isoformat()
    expires_at = (now + timedelta(hours=req.expiracao_horas)).isoformat()

    service = _get_banking_service()
    adapter = service._adapters.get(req.bank_code)

    if adapter is None:
        return PixChargeResponse(
            success=False,
            bank_code=req.bank_code,
            bank_name=bank_name,
            amount=req.amount,
            description=req.description,
            chave_pix=req.chave_pix,
            created_at=now_iso,
            error=f"Banco {req.bank_code} não configurado ou sem credenciais",
        )

    try:
        from decimal import Decimal

        amount_decimal = Decimal(str(req.amount))
        expiracao_segundos = req.expiracao_horas * 3600

        if req.bank_code == "403":
            result = await adapter.generate_pix_charge(
                amount=amount_decimal,
                description=req.description,
                payer_name=req.payer_name,
                payer_document=req.payer_document,
                expiracao_segundos=expiracao_segundos,
            )
        elif req.bank_code == "077":
            result = await adapter.generate_pix_charge(
                amount=amount_decimal,
                description=req.description,
                chave_pix=req.chave_pix,
                payer_name=req.payer_name,
                payer_document=req.payer_document,
                expiracao_segundos=expiracao_segundos,
            )
        else:
            return PixChargeResponse(
                success=False,
                bank_code=req.bank_code,
                bank_name=bank_name,
                amount=req.amount,
                description=req.description,
                chave_pix=req.chave_pix,
                created_at=now_iso,
                error=f"PIX não suportado para banco {req.bank_code}",
            )

        return PixChargeResponse(
            success=True,
            bank_code=req.bank_code,
            bank_name=bank_name,
            charge_id=result.get("charge_id"),
            pix_qrcode=result.get("pix_qrcode") or None,
            pix_copy_paste=result.get("pix_copy_paste") or None,
            amount=req.amount,
            description=req.description,
            chave_pix=req.chave_pix,
            expires_at=expires_at,
            created_at=now_iso,
        )

    except Exception as exc:
        logger.exception("Erro ao gerar PIX para banco %s: %s", req.bank_code, exc)
        error_msg = str(exc)
        # Mensagens de erro amigáveis para problemas conhecidos
        if "401" in error_msg and req.bank_code == "077":
            error_msg = (
                "PIX não habilitado na API Banco Inter. "
                "Acesse developers.inter.co → sua aplicação → habilite os escopos 'pix.read' e 'pix.write', "
                "depois solicite um novo certificado mTLS com esses escopos."
            )
        elif "500" in error_msg and req.bank_code == "403":
            error_msg = (
                "Conta Cora não possui PIX configurado. "
                "Acesse app.cora.com.br → Configurações → Pix → cadastre o CNPJ 35.710.481/0001-03 como chave PIX, "
                "depois tente novamente."
            )
        elif "403" in error_msg:
            error_msg = "Sem permissão para operação PIX neste banco. Verifique os escopos da aplicação."
        return PixChargeResponse(
            success=False,
            bank_code=req.bank_code,
            bank_name=bank_name,
            amount=req.amount,
            description=req.description,
            chave_pix=req.chave_pix,
            created_at=now_iso,
            error=error_msg,
        )


@router.get("/boleto/list", response_model=BoletoListResponse)
async def list_boletos(
    bank_code: str | None = Query(default=None),
    status: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    current_user=Depends(get_current_user),
):
    """Lista boletos emitidos. Suporte completo via Cora; Inter retorna lista vazia."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    boletos: list[BoletoListItem] = []
    service = _get_banking_service()

    banks_to_query = [bank_code] if bank_code else ["403", "077"]

    for code in banks_to_query:
        bank_name = _BANK_NAMES.get(code, code)
        adapter = service._adapters.get(code)

        if adapter is None:
            logger.debug("Adapter não disponível para banco %s — ignorando", code)
            continue

        if code == "403":
            # Cora suporta listagem de invoices
            try:
                items = await adapter.list_invoices(
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                )
                for item in items:
                    payer = item.get("customer", {})
                    bank_slip = item.get("bank_slip", {})
                    boletos.append(
                        BoletoListItem(
                            boleto_id=item.get("id", ""),
                            bank_code=code,
                            bank_name=bank_name,
                            amount=float(item.get("amount", 0)) / 100,  # centavos → reais
                            due_date=item.get("due_date", ""),
                            payer_name=payer.get("name", ""),
                            status=item.get("status", ""),
                            barcode=bank_slip.get("barcode"),
                            digitable_line=bank_slip.get("digitable_line"),
                            pdf_url=bank_slip.get("url"),
                            created_at=item.get("created_at"),
                        )
                    )
            except Exception as exc:
                logger.debug("Erro ao listar boletos Cora: %s", exc)

        elif code == "077":
            # Inter não expõe listagem direta na versão atual do adapter
            logger.debug("Listagem de boletos não disponível para Banco Inter (077)")

    return BoletoListResponse(boletos=boletos, total=len(boletos))


@router.get("/statement/full", response_model=BankStatementFullResponse)
async def get_bank_statement_full(
    days: int = Query(default=30, ge=1, le=365),
    bank_code: str | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    """Extrato completo com todos os campos disponíveis por transação."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    transactions: list[BankTransactionFull] = []
    total_credits = 0.0
    total_debits = 0.0
    opening_balance = 0.0
    closing_balance = 0.0

    service = _get_banking_service()

    banks_to_query = [bank_code] if bank_code else ["403", "077"]

    for code in banks_to_query:
        bank_name = _BANK_NAMES.get(code, code)
        try:
            statement = await service.get_statement(code, start_date, end_date)

            # Acumula saldos (último banco vence se múltiplos consultados)
            opening_balance += float(statement.opening_balance or 0)
            closing_balance += float(statement.closing_balance or 0)

            for tx in statement.transactions:
                amount = float(abs(tx.amount))
                tx_type_str = str(tx.transaction_type.value) if tx.transaction_type else "unknown"
                is_credit = tx.amount >= 0

                if is_credit:
                    total_credits += amount
                else:
                    total_debits += amount

                transactions.append(
                    BankTransactionFull(
                        transaction_id=tx.transaction_id,
                        date=tx.date.isoformat() if tx.date else "",
                        amount=amount,
                        transaction_type=tx_type_str,
                        description=tx.description or "",
                        counterpart_name=tx.counterpart_name,
                        counterpart_document=tx.counterpart_document,
                        counterpart_bank=tx.counterpart_bank,
                        balance_after=float(tx.balance_after) if tx.balance_after is not None else None,
                        reference=tx.reference,
                        category=tx.category or (str(tx.transaction_type.value) if tx.transaction_type else None),
                        bank_code=code,
                        bank_name=bank_name,
                    )
                )
        except Exception as exc:
            logger.debug("Extrato completo indisponível para banco %s: %s", code, exc)

    # Ordena por data decrescente
    transactions.sort(key=lambda t: t.date, reverse=True)

    return BankStatementFullResponse(
        transactions=transactions,
        total_credits=total_credits,
        total_debits=total_debits,
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        opening_balance=opening_balance,
        closing_balance=closing_balance,
    )
