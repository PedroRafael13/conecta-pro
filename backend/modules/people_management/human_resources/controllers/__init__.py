"""
Controllers do modulo de Recursos Humanos.

Exporta todos os routers de treinamento, desempenho, carreira
e re-exporta routers de recrutamento, clima, turnover e onboarding.
"""

from modules.people_management.human_resources.controllers.career_controller import (
    router as career_router,
)
from modules.people_management.human_resources.controllers.performance_controller import (
    router as performance_router,
)
from modules.people_management.human_resources.controllers.training_controller import (
    router as training_router,
)

# Re-exports com try/except
try:
    from modules.people_management.human_resources.controllers.recruitment_controller import (
        router as recruitment_router,
    )
except ImportError:
    recruitment_router = None  # type: ignore[assignment]

try:
    from modules.people_management.human_resources.controllers.climate_controller import (
        router as climate_router,
    )
except ImportError:
    climate_router = None  # type: ignore[assignment]

try:
    from modules.people_management.human_resources.controllers.turnover_controller import (
        router as turnover_router,
    )
except ImportError:
    turnover_router = None  # type: ignore[assignment]

try:
    from modules.people_management.human_resources.controllers.onboarding_controller import (
        router as onboarding_router,
    )
except ImportError:
    onboarding_router = None  # type: ignore[assignment]

try:
    from modules.people_management.human_resources.controllers.resume_controller import (
        router as resume_router,
    )
except ImportError:
    resume_router = None  # type: ignore[assignment]

try:
    from modules.people_management.human_resources.controllers.evaluation_360_controller import (
        router as evaluation_360_router,
    )
except ImportError:
    evaluation_360_router = None  # type: ignore[assignment]

__all__ = [
    "training_router",
    "performance_router",
    "career_router",
    "recruitment_router",
    "climate_router",
    "turnover_router",
    "onboarding_router",
    "resume_router",
    "evaluation_360_router",
]
