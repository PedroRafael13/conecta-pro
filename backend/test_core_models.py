#!/usr/bin/env python3
import signal
import sys
import time

def timeout_handler(signum, frame):
    raise TimeoutError("Import timeout")

def test_import(module_name, timeout=30):
    print(f"Testing: {module_name}...", end=" ", flush=True)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        start_time = time.time()
        exec(f"import {module_name}")
        duration = time.time() - start_time
        print(f"OK ({duration:.2f}s)")
        return True
    except TimeoutError:
        print(f"TIMEOUT após {timeout}s!")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        signal.alarm(0)

print("=== TESTANDO CORE.MODELS ===")
test_import("core.models", 60)
test_import("core.models.user", 60)
