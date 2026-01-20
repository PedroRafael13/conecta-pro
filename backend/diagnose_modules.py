#!/usr/bin/env python3
"""
Diagnóstico detalhado - importa cada módulo do api/v1 com timeout individual.
"""
import sys
import time
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout!")

def test_import_with_timeout(name, import_func, timeout_sec=60):
    """Testa um import com timeout."""
    print(f"\n>>> Testing: {name}", flush=True)

    # Configurar timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)

    start = time.time()
    try:
        import_func()
        duration = time.time() - start
        signal.alarm(0)  # Cancelar alarme
        print(f"    OK ({duration:.2f}s)", flush=True)
        return True, duration
    except TimeoutError:
        print(f"    TIMEOUT após {timeout_sec}s!", flush=True)
        return False, timeout_sec
    except Exception as e:
        signal.alarm(0)
        print(f"    FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False, 0

print("=" * 70)
print("DIAGNÓSTICO DE MÓDULOS - Timeout de 60s por módulo")
print("=" * 70)

# Testar imports básicos primeiro
basic_imports = [
    ("fastapi", lambda: __import__("fastapi")),
    ("sqlalchemy", lambda: __import__("sqlalchemy")),
    ("pydantic", lambda: __import__("pydantic")),
    ("core.config", lambda: exec("from core.config import settings")),
    ("core.logging", lambda: exec("from core.logging import logger")),
    ("core.database", lambda: exec("from core.database import get_db")),
]

print("\n--- IMPORTS BÁSICOS ---")
for name, func in basic_imports:
    success, duration = test_import_with_timeout(name, func, 30)
    if not success:
        print(f"\n*** FALHOU em: {name} ***")
        sys.exit(1)

# Testar módulos individuais
module_imports = [
    ("api.v1.endpoints.auth", lambda: exec("from api.v1.endpoints.auth import router")),
    ("modules.crm.controllers", lambda: exec("from modules.crm.controllers import lead_router")),
    ("modules.operations.controllers", lambda: exec("from modules.operacional.controllers import post_router")),
    ("modules.financial.controllers", lambda: exec("from modules.financial.controllers import accounting_router")),
    ("modules.hr.analytics_dashboard", lambda: exec("from modules.hr.analytics_dashboard import router")),
    ("modules.monitoring", lambda: exec("from modules.monitoring import router")),
    ("modules.automation.workflow.controllers", lambda: exec("from modules.automation.workflow.controllers import router")),
    ("modules.fase5.controllers", lambda: exec("from modules.fase5.controllers import fase5_router")),
    ("modules.bidding", lambda: exec("from modules.bidding import tender_router")),
    ("modules.ai.intelligence_hub.controllers", lambda: exec("from modules.ai.intelligence_hub.controllers import intelligence_hub_router")),
]

print("\n--- IMPORTS DE MÓDULOS ---")
for name, func in module_imports:
    success, duration = test_import_with_timeout(name, func, 60)
    if not success:
        print(f"\n*** PROBLEMA em: {name} ***")
        break

print("\n" + "=" * 70)
print("Diagnóstico concluído")
print("=" * 70)
