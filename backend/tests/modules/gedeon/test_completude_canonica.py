"""Testes canônicos — KitBuilderService com modelo §35 (BLOCO A).

Cobrem fórmula dinâmica total_esperado por condomínio × N_funcionarios.
Banco real via SyncSessionLocal (sem mocks).
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal
from modules.gedeon.services.kit_builder_service import KitBuilderService


@pytest.fixture
def db():
    session = SyncSessionLocal()
    yield session
    session.close()


@pytest.fixture
def service(db):
    return KitBuilderService(db)


def _get_id(db, nome_normalizado: str) -> UUID:
    row = db.execute(
        text("SELECT id FROM condominios WHERE nome_normalizado = :n"),
        {"n": nome_normalizado},
    ).fetchone()
    assert row, f"Condomínio não encontrado: {nome_normalizado}"
    return UUID(str(row[0]))


def _get_n_func(db, condominio_id: UUID) -> int:
    row = db.execute(
        text(
            "SELECT COUNT(DISTINCT employee_id) FROM employee_alocacoes "
            "WHERE condominio_id = CAST(:cid AS uuid) AND ativo = true"
        ),
        {"cid": str(condominio_id)},
    ).fetchone()
    return int(row[0]) if row else 0


# ---------------------------------------------------------------------------
# P. Gelain / Green Hills / Parise — apenas 2 docs condominio (nfse + boleto)
# ---------------------------------------------------------------------------
class TestServicosSimplesDoisTemplates:
    @pytest.mark.parametrize("nome_norm", ["p_gelain", "green_hills", "parise"])
    def test_total_esperado_e_2(self, service, db, nome_norm):
        """P. Gelain / Green Hills / Parise: só nfse + boleto = 2 (§35.2)."""
        cid = _get_id(db, nome_norm)
        result = service.build_completude(cid, "03.2026")
        assert result.metricas.total_esperado == 2

    def test_nao_tem_cnds(self, service, db):
        """P. Gelain não tem CNDs (presença='na' para empresa_matriz)."""
        cid = _get_id(db, "p_gelain")
        result = service.build_completude(cid, "03.2026")
        cnd_slugs = {"cnd_rfb", "cnd_caixa", "cnd_prefeitura", "cnd_sefaz", "cnd_trabalhista"}
        tipos_presentes = {d.tipo_documento for d in result.docs_presentes}
        tipos_faltantes = {d.tipo_documento for d in result.docs_faltantes}
        # CNDs não devem aparecer como faltantes (presença='na' para P.Gelain)
        assert not cnd_slugs.intersection(tipos_faltantes)
        assert not cnd_slugs.intersection(tipos_presentes)


# ---------------------------------------------------------------------------
# Eventuais NÃO entram em total_esperado
# ---------------------------------------------------------------------------
class TestEventuaisNaoContamEmEsperado:
    def test_ideal_flores_aviso_ferias_nao_conta(self, service, db):
        """Ideal Flores tem aviso_previo_ferias como ⚠️ — NÃO soma em total_esperado."""
        cid = _get_id(db, "ideal_flores")
        n_func = _get_n_func(db, cid)
        result = service.build_completude(cid, "03.2026")
        # empresa_matriz=5, condominio=12, funcionario=10 (sem eventual docs)
        # esperado = 5 + 12 + 10*N (aviso_ferias=eventual, NÃO conta)
        expected_min = 5 + 12 + 0  # com N=0
        assert result.metricas.total_esperado == expected_min + 10 * n_func

    def test_laranjeiras_rescisao_nao_conta(self, service, db):
        """Laranjeiras tem rescisao_contrato/comp_rescisao como ⚠️ — NÃO somam."""
        cid = _get_id(db, "laranjeiras")
        n_func = _get_n_func(db, cid)
        result = service.build_completude(cid, "03.2026")
        # empresa_matriz=5, condominio=12, funcionario=11 (sem rescisao/comp_rescisao)
        # Laranjeiras func obrig: 4,5,9,10,11,20,21,22,26,27,32 = 11
        expected_min = 5 + 12 + 0
        assert result.metricas.total_esperado == expected_min + 11 * n_func


# ---------------------------------------------------------------------------
# Condomínios sem CNDs têm empresa_matriz=0
# ---------------------------------------------------------------------------
class TestSemCNDs:
    @pytest.mark.parametrize("nome_norm", ["p_gelain", "green_hills", "parise"])
    def test_empresa_matriz_zero(self, service, db, nome_norm):
        """Condominios com — em todos CNDs: contribuição empresa_matriz = 0."""
        cid = _get_id(db, nome_norm)
        # total=2 já confirma empresa_matriz=0 + funcionario=0 (sem folha CLT)
        result = service.build_completude(cid, "03.2026")
        assert result.metricas.total_esperado == 2


# ---------------------------------------------------------------------------
# Consistência total_esperado vs fórmula §35.4
# ---------------------------------------------------------------------------
class TestFormulaCanonicaConsistencia:
    @pytest.mark.parametrize(
        "nome_norm,esperado_empresa,esperado_cond,esperado_func_por_n",
        [
            ("prime_arena", 5, 12, 11),  # 28✅ = 5+12+11(func)
            ("michelangelo", 5, 8, 4),  # 17✅ = 5+8+4(func)
            ("villa_dei_fiori", 5, 11, 8),  # 64 = 5+11+8×6func
            ("villa_passaros", 5, 10, 5),  # 45 = 5+10+5×6func
        ],
    )
    def test_total_esperado_formula(self, service, db, nome_norm, esperado_empresa, esperado_cond, esperado_func_por_n):
        cid = _get_id(db, nome_norm)
        n_func = _get_n_func(db, cid)
        result = service.build_completude(cid, "03.2026")
        expected = esperado_empresa + esperado_cond + esperado_func_por_n * n_func
        assert result.metricas.total_esperado == expected, (
            f"{nome_norm}: esperado={expected} "
            f"(empresa={esperado_empresa}+cond={esperado_cond}+func={esperado_func_por_n}×{n_func}), "
            f"got={result.metricas.total_esperado}"
        )
