"""
Módulo de Relatórios Gerenciais

DEPRECATED: Use 'modules.inteligencia' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.reports' is deprecated. "
    "Use 'modules.inteligencia' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.reports.controllers import router  # noqa: E402

__all__ = ["router"]
