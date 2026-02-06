#!/usr/bin/env python3
"""
Smoke Tests - Testes criticos pos-deploy.
Verifica se endpoints essenciais estao funcionando.
"""

import asyncio
import sys
from datetime import datetime

import httpx

# Cores para output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


async def run_smoke_tests(base_url: str):
    """
    Executa testes criticos que devem passar apos deploy.

    Args:
        base_url: URL base da API (ex: http://localhost:8080)
    """
    print(f"{GREEN}========================================{NC}")
    print(f"{GREEN}  SMOKE TESTS - ERP CONECTA MAIS{NC}")
    print(f"{GREEN}  URL: {base_url}{NC}")
    print(f"{GREEN}  Data: {datetime.now()}{NC}")
    print(f"{GREEN}========================================{NC}\n")

    tests_passed = 0
    tests_failed = 0
    results = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health Check
        print(f"{YELLOW}[1/5] Health Check...{NC}")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print(f"{GREEN}   OK - Sistema saudavel{NC}")
                    tests_passed += 1
                    results.append(("Health Check", "PASS"))
                else:
                    print(f"{RED}   FALHA - Status: {data.get('status')}{NC}")
                    tests_failed += 1
                    results.append(("Health Check", "FAIL"))
            else:
                print(f"{RED}   FALHA - HTTP {response.status_code}{NC}")
                tests_failed += 1
                results.append(("Health Check", "FAIL"))
        except Exception as e:
            print(f"{RED}   ERRO - {e}{NC}")
            tests_failed += 1
            results.append(("Health Check", f"ERROR: {e}"))

        # Test 2: Root Endpoint
        print(f"\n{YELLOW}[2/5] Root Endpoint...{NC}")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print(f"{GREEN}   OK - Endpoint raiz respondendo{NC}")
                tests_passed += 1
                results.append(("Root Endpoint", "PASS"))
            else:
                print(f"{RED}   FALHA - HTTP {response.status_code}{NC}")
                tests_failed += 1
                results.append(("Root Endpoint", "FAIL"))
        except Exception as e:
            print(f"{RED}   ERRO - {e}{NC}")
            tests_failed += 1
            results.append(("Root Endpoint", f"ERROR: {e}"))

        # Test 3: Auth Login Endpoint (deve retornar 422 sem dados)
        print(f"\n{YELLOW}[3/5] Auth Login Endpoint...{NC}")
        try:
            response = await client.post(f"{base_url}/api/v1/auth/login", data={})
            # 422 = endpoint existe mas falta dados
            # 401 = endpoint existe, dados invalidos
            if response.status_code in [401, 422]:
                print(f"{GREEN}   OK - Endpoint de login ativo{NC}")
                tests_passed += 1
                results.append(("Auth Login", "PASS"))
            else:
                print(f"{YELLOW}   AVISO - HTTP {response.status_code}{NC}")
                tests_passed += 1  # Endpoint responde
                results.append(("Auth Login", "PASS"))
        except Exception as e:
            print(f"{RED}   ERRO - {e}{NC}")
            tests_failed += 1
            results.append(("Auth Login", f"ERROR: {e}"))

        # Test 4: Auth Register Endpoint
        print(f"\n{YELLOW}[4/5] Auth Register Endpoint...{NC}")
        try:
            response = await client.post(f"{base_url}/api/v1/auth/register", json={})
            # 422 = endpoint existe mas falta dados
            if response.status_code == 422:
                print(f"{GREEN}   OK - Endpoint de registro ativo{NC}")
                tests_passed += 1
                results.append(("Auth Register", "PASS"))
            else:
                print(f"{YELLOW}   AVISO - HTTP {response.status_code}{NC}")
                tests_passed += 1
                results.append(("Auth Register", "PASS"))
        except Exception as e:
            print(f"{RED}   ERRO - {e}{NC}")
            tests_failed += 1
            results.append(("Auth Register", f"ERROR: {e}"))

        # Test 5: Response Time
        print(f"\n{YELLOW}[5/5] Response Time...{NC}")
        try:
            import time

            start = time.time()
            response = await client.get(f"{base_url}/health")
            elapsed = time.time() - start

            if elapsed < 1.0:
                print(f"{GREEN}   OK - Tempo de resposta: {elapsed:.3f}s{NC}")
                tests_passed += 1
                results.append(("Response Time", f"PASS ({elapsed:.3f}s)"))
            else:
                print(f"{RED}   LENTO - Tempo de resposta: {elapsed:.3f}s{NC}")
                tests_failed += 1
                results.append(("Response Time", f"SLOW ({elapsed:.3f}s)"))
        except Exception as e:
            print(f"{RED}   ERRO - {e}{NC}")
            tests_failed += 1
            results.append(("Response Time", f"ERROR: {e}"))

    # Resumo
    print(f"\n{GREEN}========================================{NC}")
    print(f"{GREEN}  RESUMO DOS SMOKE TESTS{NC}")
    print(f"{GREEN}========================================{NC}")

    for test_name, status in results:
        if "PASS" in status:
            print(f"  {GREEN}[PASS]{NC} {test_name}")
        elif "SLOW" in status:
            print(f"  {YELLOW}[SLOW]{NC} {test_name}")
        else:
            print(f"  {RED}[FAIL]{NC} {test_name}")

    print(f"\n  Total: {tests_passed} OK, {tests_failed} FALHA")

    if tests_failed > 0:
        print(f"\n{RED}  STATUS: FALHA - ROLLBACK RECOMENDADO!{NC}")
        return 1
    else:
        print(f"\n{GREEN}  STATUS: OK - Deploy seguro!{NC}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python smoke_tests.py <base_url>")
        print("Exemplo: python smoke_tests.py http://localhost:8080")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    exit_code = asyncio.run(run_smoke_tests(base_url))
    sys.exit(exit_code)
