"""Test CIPA endpoints (NR-5) - Fase 10 SST."""

import json
import urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

# Login
data = b"username=admin%40conectapro.com.br&password=admin123"
req = urllib.request.Request(
    f"{BASE}/auth/login",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())["access_token"]
print("TOKEN OK")
print()

# 1. GET /sst/cipa/membros
print("=== GET /sst/cipa/membros ===")
req2 = urllib.request.Request(
    f"{BASE}/people-management/sst/cipa/membros",
    headers={"Authorization": f"Bearer {token}"},
)
resp2 = urllib.request.urlopen(req2)
r2 = json.loads(resp2.read())
print(json.dumps(r2, indent=2, ensure_ascii=False))
print()

# 2. POST /sst/cipa/reunioes
print("=== POST /sst/cipa/reunioes ===")
body = json.dumps(
    {
        "data_reuniao": "2026-04-01",
        "tipo": "ordinaria",
        "pauta": "Primeira reuniao CIPA 2026 - Plano de trabalho",
    }
).encode()
req3 = urllib.request.Request(
    f"{BASE}/people-management/sst/cipa/reunioes",
    data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST",
)
resp3 = urllib.request.urlopen(req3)
r3 = json.loads(resp3.read())
print(json.dumps(r3, indent=2, ensure_ascii=False))
print()

# 3. GET /sst/cipa/reunioes
print("=== GET /sst/cipa/reunioes (after POST) ===")
req4 = urllib.request.Request(
    f"{BASE}/people-management/sst/cipa/reunioes",
    headers={"Authorization": f"Bearer {token}"},
)
resp4 = urllib.request.urlopen(req4)
r4 = json.loads(resp4.read())
print(json.dumps(r4, indent=2, ensure_ascii=False))
print()

# Summary
print("=" * 50)
print(f"CIPA Membros: {r2['total']} membros ativos")
for m in r2["membros"]:
    print(f"  - {m['funcao']:20s} | {m['representacao']:12s} | {m['nome']}")
print(f"CIPA Reunioes: {r4['total']} reuniao(oes)")
for rn in r4["reunioes"]:
    print(f"  - {rn['data']} | {rn['tipo']:15s} | {rn['status']}")
print()
print("ALL 3 ENDPOINTS OK!")
