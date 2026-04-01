"""
conftest.py para testes do módulo CRM.

As classes StrEnum que estavam faltando (ContractServiceType, ServiceStatus,
IntegrationType, SyncDirection, SyncStatus, UnitType, UnitStatus) foram
adicionadas diretamente nos arquivos de modelo em modules/clients/models/.

Este conftest garante que os módulos reais são carregados corretamente,
removendo qualquer stub que tenha sido registrado antes deles.
"""

import importlib
import sys


def _ensure_real_module(module_name: str) -> None:
    """
    Remove stub (se houver) e carrega o módulo real.
    Stubs têm __file__ com prefixo '<stub:'.
    """
    existing = sys.modules.get(module_name)
    if existing is not None:
        file_attr = getattr(existing, "__file__", "") or ""
        if file_attr.startswith("<stub:"):
            # Remove o stub para que o módulo real seja importado
            del sys.modules[module_name]
    # Importa o módulo real (pode falhar silenciosamente se houver outros problemas)
    try:
        importlib.import_module(module_name)
    except Exception:
        pass


# Garante módulos reais (com StrEnums adicionados) antes de qualquer fixture
_ensure_real_module("modules.clients.models.client_contract")
_ensure_real_module("modules.clients.models.integration_settings")
_ensure_real_module("modules.clients.models.unit")
