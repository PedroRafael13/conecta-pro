"""
Categoria: Gestao de Pessoas (People Management)

Agrupa os modulos:
- hr (Departamento Pessoal)
- human_resources (Recursos Humanos)
- operations (Operacoes)
- employee_portal (Portal do Funcionario)

Integracao bidirecional entre todos os modulos.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/people-management", tags=["Gestao de Pessoas"])


def register_routers() -> None:
    """Registra sub-routers quando disponiveis."""
    try:
        from .hr.aggregator import router as hr_router

        router.include_router(hr_router)
    except ImportError:
        pass

    try:
        from .human_resources.aggregator import router as human_resources_router

        router.include_router(human_resources_router)
    except ImportError:
        pass

    try:
        from .operations.aggregator import router as operations_router

        router.include_router(operations_router)
    except ImportError:
        pass

    try:
        from .employee_portal.aggregator import router as portal_router

        router.include_router(portal_router)
    except ImportError:
        pass


register_routers()
