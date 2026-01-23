"""
Módulo de Reembolso de Despesas.

Este módulo gerencia solicitações de reembolso de funcionários,
com fluxo de aprovação e integração com o módulo financeiro.
"""

from modules.reimbursement.controllers.reimbursement_controller import router as reimbursement_router

__all__ = ["reimbursement_router"]
