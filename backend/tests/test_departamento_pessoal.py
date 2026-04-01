"""
Testes de integração — Departamento Pessoal + CCT 2026
Conecta PRO ERP — chamadas HTTP reais, sem mocks.
"""

import httpx

BASE = "http://127.0.0.1:8080/api/v1"

_token: str = ""


def get_token() -> str:
    global _token
    if not _token:
        r = httpx.post(
            f"{BASE}/auth/login",
            data={"username": "jjesus@conectamais.pro", "password": "Jordan0612"},  # pragma: allowlist secret
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        assert r.status_code == 200, f"Login failed: {r.status_code}"
        _token = r.json()["access_token"]
    return _token


def h() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ── FUNCIONÁRIOS ─────────────────────────────────────────────────────────────


def test_dp_lista_funcionarios_200():
    r = httpx.get(f"{BASE}/people-management/hr/employees", headers=h(), timeout=10)
    assert r.status_code == 200


def test_dp_funcionarios_sem_token_401():
    r = httpx.get(f"{BASE}/people-management/hr/employees", timeout=5)
    assert r.status_code == 401


def test_dp_funcionarios_retorna_paginado():
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=5", headers=h(), timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body


def test_dp_tem_minimo_40_funcionarios():
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=100", headers=h(), timeout=10)
    assert r.status_code == 200
    total = r.json().get("total", 0)
    assert total >= 40, f"Esperado 40+ funcionários, encontrado {total}"


def test_dp_funcionario_campos_obrigatorios():
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=3", headers=h(), timeout=10)
    assert r.status_code == 200
    for emp in r.json()["items"]:
        assert emp.get("id"), "Funcionário sem ID"
        assert emp.get("nome"), "Funcionário sem nome"
        assert emp.get("status"), "Funcionário sem status"


def test_dp_is_active_sincronizado_com_status():
    """is_active deve refletir status=='ativo' — Skill 07 fix."""
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=100", headers=h(), timeout=10)
    assert r.status_code == 200
    divergentes = [
        f["nome"]
        for f in r.json()["items"]
        if f.get("is_active") is not None
        and f.get("status")
        and bool(f["is_active"]) != (f["status"] in ("ativo", "active"))
    ]
    assert len(divergentes) == 0, f"is_active diverge de status: {divergentes[:3]}"


def test_dp_salario_base_positivo():
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=20", headers=h(), timeout=10)
    assert r.status_code == 200
    com_salario = [f for f in r.json()["items"] if f.get("salario_base")]
    assert len(com_salario) > 0, "Nenhum funcionário com salário_base"
    for f in com_salario:
        assert float(f["salario_base"]) > 0, f"Salário inválido: {f['salario_base']}"


# ── ADMISSÕES ─────────────────────────────────────────────────────────────────


def test_dp_lista_admissoes_200():
    r = httpx.get(f"{BASE}/people-management/hr/admissions", headers=h(), timeout=10)
    assert r.status_code == 200


def test_dp_admissoes_sem_token_401():
    r = httpx.get(f"{BASE}/people-management/hr/admissions", timeout=5)
    assert r.status_code == 401


# ── DOCUMENTOS E BENEFÍCIOS ───────────────────────────────────────────────────


def test_dp_documentos_200():
    r = httpx.get(f"{BASE}/people-management/hr/documents", headers=h(), timeout=10)
    assert r.status_code == 200


def test_dp_beneficios_200():
    r = httpx.get(f"{BASE}/people-management/hr/benefits", headers=h(), timeout=10)
    assert r.status_code == 200


def test_dp_payroll_benefits_200():
    r = httpx.get(f"{BASE}/people-management/hr/payroll/benefits", headers=h(), timeout=10)
    assert r.status_code == 200


# ── CCT 2026 ─────────────────────────────────────────────────────────────────


def test_cct_beneficios_200():
    r = httpx.get(f"{BASE}/cct/beneficios", headers=h(), timeout=10)
    assert r.status_code == 200


def test_cct_feriados_200():
    r = httpx.get(f"{BASE}/cct/feriados", headers=h(), timeout=10)
    assert r.status_code == 200


def test_cct_jornadas_permitidas_200():
    r = httpx.get(f"{BASE}/cct/jornadas/permitidas", headers=h(), timeout=10)
    assert r.status_code == 200


def test_cct_compliance_metadata_200():
    r = httpx.get(f"{BASE}/cct/compliance/metadata", headers=h(), timeout=10)
    assert r.status_code == 200


def test_cct_piso_salario_condizente_com_registro():
    """Piso salarial dos funcionários deve ser >= R$1.670 (CCT 2026)."""
    r = httpx.get(f"{BASE}/people-management/hr/employees?page_size=100", headers=h(), timeout=10)
    assert r.status_code == 200
    abaixo = [f["nome"] for f in r.json()["items"] if f.get("salario_base") and float(f["salario_base"]) < 1670.00]
    assert len(abaixo) == 0, f"Funcionários abaixo do piso CCT 2026: {abaixo[:5]}"
