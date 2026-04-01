"""
Módulo de Reembolso de Despesas.

DEPRECATED: Use 'modules.pessoas' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.reimbursement' is deprecated. "
    "Use 'modules.pessoas' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.reimbursement.controllers.reimbursement_controller import router as reimbursement_router  # noqa: E402

__all__ = ["reimbursement_router"]
