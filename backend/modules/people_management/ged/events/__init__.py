"""
Event handlers do modulo GED.

Integra o GED com eventos de outros modulos:
folha de pagamento, certidoes, assinaturas e alocacoes.
"""

from modules.people_management.ged.events.handlers import (
    on_cnd_renewed,
    on_document_signed,
    on_employee_allocated,
    on_employee_deallocated,
    on_payroll_closed,
)

__all__ = [
    "on_cnd_renewed",
    "on_document_signed",
    "on_employee_allocated",
    "on_employee_deallocated",
    "on_payroll_closed",
]
