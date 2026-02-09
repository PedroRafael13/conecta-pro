#!/usr/bin/env python3
"""Teste que simula exatamente os imports do auth.py"""

import signal
import time


def timeout_handler(signum, frame):
    raise TimeoutError("Import timeout")


def test_step(step_name, code, timeout=30):
    print(f"Testing: {step_name}...", end=" ", flush=True)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        start_time = time.time()
        exec(code, globals(), globals())  # noqa: S102
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


print("=== SIMULANDO IMPORTS EXATOS DO AUTH.PY ===")

# Imports básicos primeiro
test_step("datetime", "from datetime import datetime")
test_step("fastapi", "from fastapi import APIRouter, Depends, HTTPException, status")
test_step("fastapi.security", "from fastapi.security import OAuth2PasswordRequestForm")
test_step("sqlalchemy", "from sqlalchemy import select")
test_step("sqlalchemy.ext.asyncio", "from sqlalchemy.ext.asyncio import AsyncSession")

# Agora os imports problemáticos
test_step("core.auth (1)", "from core.auth import create_access_token", 60)
test_step("core.auth (2)", "from core.auth import create_refresh_token", 60)
test_step("core.auth (3)", "from core.auth import verify_refresh_token", 60)
test_step("core.auth.dependencies", "from core.auth.dependencies import get_current_active_user", 60)
test_step("core.auth.security", "from core.auth.security import get_password_hash, verify_password", 60)
test_step("core.database", "from core.database import get_db", 60)
test_step("core.logging", "from core.logging import logger", 60)
test_step("core.models", "from core.models import User", 60)
test_step("core.schemas.auth", "from core.schemas.auth import Token, TokenRefresh", 60)
test_step("core.schemas.user", "from core.schemas.user import UserCreate, UserResponse", 60)
