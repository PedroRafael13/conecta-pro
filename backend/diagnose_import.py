#!/usr/bin/env python3
"""
Script de diagnóstico para identificar imports problemáticos.
"""

import time


def test_import(name, import_statement):
    """Testa um import específico."""
    print(f"Testing: {name}...", end=" ", flush=True)
    start = time.time()
    try:
        exec(import_statement)  # noqa: S102
        duration = time.time() - start
        print(f"OK ({duration:.2f}s)")
        return True, duration
    except Exception as e:
        print(f"FAILED: {e}")
        return False, 0


# Lista de imports a testar (na ordem do main.py e api/v1)
imports = [
    ("contextlib", "from contextlib import asynccontextmanager"),
    ("typing", "from typing import AsyncGenerator"),
    ("fastapi", "from fastapi import FastAPI, Request, Response"),
    ("fastapi.middleware.cors", "from fastapi.middleware.cors import CORSMiddleware"),
    ("fastapi.middleware.gzip", "from fastapi.middleware.gzip import GZipMiddleware"),
    ("starlette.middleware.base", "from starlette.middleware.base import BaseHTTPMiddleware"),
    ("slowapi", "from slowapi import Limiter, _rate_limit_exceeded_handler"),
    ("slowapi.util", "from slowapi.util import get_remote_address"),
    ("slowapi.errors", "from slowapi.errors import RateLimitExceeded"),
    ("core.config", "from core.config import settings"),
    ("core.logging", "from core.logging import configure_logging, logger"),
    ("core.monitoring", "from core.monitoring import MetricsMiddleware, get_metrics"),
]

print("=" * 60)
print("DIAGNÓSTICO DE IMPORTS - Backend Conecta PRO")
print("=" * 60)

total_time = 0
failed = []

for name, stmt in imports:
    success, duration = test_import(name, stmt)
    total_time += duration
    if not success:
        failed.append(name)

print("=" * 60)
print(f"Total time: {total_time:.2f}s")
print(f"Failed imports: {failed if failed else 'None'}")

if not failed:
    print("\nTesting api.v1 router import...")
    test_import("api.v1", "from api.v1 import router as api_v1_router")

print("=" * 60)
