"""Schemas do modulo financeiro - Contas a Pagar e Contas a Receber."""

# Contas a Pagar
from modules.financial.schemas.category import (
    PayableCategoryCreate,
    PayableCategoryFilter,
    PayableCategoryListResponse,
    PayableCategoryResponse,
    PayableCategoryTreeResponse,
    PayableCategoryUpdate,
)
from modules.financial.schemas.payable import (
    PayableAccountCreate,
    PayableAccountFilter,
    PayableAccountListResponse,
    PayableAccountResponse,
    PayableAccountStats,
    PayableAccountUpdate,
    PayableBulkApproveRequest,
    PayableBulkPaymentRequest,
    PayableInstallmentCreate,
    PayableInstallmentRenegotiateRequest,
    PayableInstallmentResponse,
    PayableInstallmentUpdate,
    PayablePaymentCreate,
    PayablePaymentReconcileRequest,
    PayablePaymentResponse,
    PayablePaymentReverseRequest,
    PayablePaymentUpdate,
    PayableScheduleRequest,
)
from modules.financial.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodListResponse,
    PaymentMethodResponse,
    PaymentMethodUpdate,
)
from modules.financial.schemas.supplier import (
    SupplierBlockRequest,
    SupplierCreate,
    SupplierFilter,
    SupplierListResponse,
    SupplierQualifyRequest,
    SupplierResponse,
    SupplierStats,
    SupplierUpdate,
)

# Contas a Receber
from modules.financial.schemas.receivable import (
    BillingRuleCreate,
    BillingRuleFilter,
    BillingRuleResponse,
    BillingRuleUpdate,
    CustomerCreate,
    CustomerFilter,
    CustomerResponse,
    CustomerUpdate,
    ReceivableAccountCreate,
    ReceivableAccountFilter,
    ReceivableAccountListResponse,
    ReceivableAccountResponse,
    ReceivableAccountStats,
    ReceivableAccountUpdate,
    ReceivableAgreementRequest,
    ReceivableBulkBoletoRequest,
    ReceivableBulkNotifyRequest,
    ReceivableBulkPaymentRequest,
    ReceivableCategoryCreate,
    ReceivableCategoryResponse,
    ReceivableCategoryUpdate,
    ReceivableInstallmentBoletoRequest,
    ReceivableInstallmentCreate,
    ReceivableInstallmentPixRequest,
    ReceivableInstallmentRenegotiateRequest,
    ReceivableInstallmentResponse,
    ReceivableInstallmentUpdate,
    ReceivablePaymentCreate,
    ReceivablePaymentReconcileRequest,
    ReceivablePaymentResponse,
    ReceivablePaymentReverseRequest,
    ReceivablePaymentUpdate,
    ReceivableProtestRequest,
    ReceivableWriteOffRequest,
)

__all__ = [
    # === Contas a Pagar ===
    # Supplier
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierResponse",
    "SupplierListResponse",
    "SupplierFilter",
    "SupplierStats",
    "SupplierBlockRequest",
    "SupplierQualifyRequest",
    # PaymentMethod
    "PaymentMethodCreate",
    "PaymentMethodUpdate",
    "PaymentMethodResponse",
    "PaymentMethodListResponse",
    # PayableCategory
    "PayableCategoryCreate",
    "PayableCategoryUpdate",
    "PayableCategoryResponse",
    "PayableCategoryListResponse",
    "PayableCategoryTreeResponse",
    "PayableCategoryFilter",
    # PayableAccount
    "PayableAccountCreate",
    "PayableAccountUpdate",
    "PayableAccountResponse",
    "PayableAccountListResponse",
    "PayableAccountFilter",
    "PayableAccountStats",
    # PayableInstallment
    "PayableInstallmentCreate",
    "PayableInstallmentUpdate",
    "PayableInstallmentResponse",
    "PayableInstallmentRenegotiateRequest",
    # PayablePayment
    "PayablePaymentCreate",
    "PayablePaymentUpdate",
    "PayablePaymentResponse",
    "PayablePaymentReverseRequest",
    "PayablePaymentReconcileRequest",
    # Bulk Operations (Payable)
    "PayableBulkPaymentRequest",
    "PayableBulkApproveRequest",
    "PayableScheduleRequest",
    # === Contas a Receber ===
    # Customer
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerFilter",
    # ReceivableCategory
    "ReceivableCategoryCreate",
    "ReceivableCategoryUpdate",
    "ReceivableCategoryResponse",
    # ReceivableAccount
    "ReceivableAccountCreate",
    "ReceivableAccountUpdate",
    "ReceivableAccountResponse",
    "ReceivableAccountListResponse",
    "ReceivableAccountFilter",
    "ReceivableAccountStats",
    # ReceivableInstallment
    "ReceivableInstallmentCreate",
    "ReceivableInstallmentUpdate",
    "ReceivableInstallmentResponse",
    "ReceivableInstallmentRenegotiateRequest",
    "ReceivableInstallmentBoletoRequest",
    "ReceivableInstallmentPixRequest",
    # ReceivablePayment
    "ReceivablePaymentCreate",
    "ReceivablePaymentUpdate",
    "ReceivablePaymentResponse",
    "ReceivablePaymentReverseRequest",
    "ReceivablePaymentReconcileRequest",
    # BillingRule
    "BillingRuleCreate",
    "BillingRuleUpdate",
    "BillingRuleResponse",
    "BillingRuleFilter",
    # Bulk Operations (Receivable)
    "ReceivableBulkPaymentRequest",
    "ReceivableBulkBoletoRequest",
    "ReceivableBulkNotifyRequest",
    # Special Operations
    "ReceivableWriteOffRequest",
    "ReceivableProtestRequest",
    "ReceivableAgreementRequest",
]
