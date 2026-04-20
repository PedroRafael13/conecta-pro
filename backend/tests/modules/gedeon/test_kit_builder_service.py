"""Testes de integração — KitBuilderService (§26.6 CONTRACTS_GEDEON.md v1.21).

Cobrem 10 cenários do §26.6. Banco real via SyncSessionLocal (sem mocks).
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal
from modules.gedeon.services.kit_builder_service import (
    TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND,
    CategoriaToTipoDocumento,
    CompletudeKit,
    DocumentoFaltante,
    DocumentoPresente,
    KitBuilderService,
    MetricasKit,
    _determinar_motivo_faltante,
    _validate_mes_ref,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db():
    session = SyncSessionLocal()
    yield session
    session.close()


@pytest.fixture
def service(db):
    return KitBuilderService(db)


def _get_condominio_id(db, nome_normalizado: str) -> UUID:
    row = db.execute(
        text("SELECT id FROM condominios WHERE nome_normalizado = :n"),
        {"n": nome_normalizado},
    ).fetchone()
    assert row, f"Condomínio não encontrado: {nome_normalizado}"
    return UUID(str(row[0]))


# ---------------------------------------------------------------------------
# Cenário 9 — mes_ref inválido → raise ValueError (INV-13)
# ---------------------------------------------------------------------------
class TestMesRefValidacao:
    def test_formato_errado_levanta_value_error(self):
        with pytest.raises(ValueError, match="mes_ref inválido"):
            _validate_mes_ref("2026-04")

    def test_formato_texto_levanta_value_error(self):
        with pytest.raises(ValueError):
            _validate_mes_ref("abril 2026")

    def test_mes_13_levanta_value_error(self):
        with pytest.raises(ValueError):
            _validate_mes_ref("13.2026")  # mês > 12

    def test_mes_00_levanta_value_error(self):
        with pytest.raises(ValueError):
            _validate_mes_ref("00.2026")  # mês 0

    def test_none_levanta_value_error(self):
        with pytest.raises(ValueError):
            _validate_mes_ref(None)

    def test_formatos_validos_nao_levantam(self):
        _validate_mes_ref("01.2026")
        _validate_mes_ref("03.2026")
        _validate_mes_ref("12.2025")


# ---------------------------------------------------------------------------
# Cenário 10 — condominio_id inexistente → raise ValueError (INV-14)
# ---------------------------------------------------------------------------
class TestCondominioInexistente:
    def test_uuid_inexistente_levanta_value_error(self, service):
        with pytest.raises(ValueError, match="não encontrado"):
            service.build_completude(uuid4(), "03.2026")


# ---------------------------------------------------------------------------
# Cenário 1 — kit_mensal: estrutura e métricas corretas
# ---------------------------------------------------------------------------
class TestKitMensalEstrutura:
    def test_retorna_completude_kit(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        assert isinstance(result, CompletudeKit)
        assert result.tipo_servico == "kit_mensal"
        assert result.mes_ref == "03.2026"
        # kit_mensal tem 32 templates
        assert result.metricas.total_esperado == 32

    def test_metricas_percentual_entre_0_e_100(self, service, db):
        cid = _get_condominio_id(db, "mirante")
        result = service.build_completude(cid, "03.2026")
        m = result.metricas
        assert 0.0 <= m.pct_completude_confirmada <= 100.0
        assert 0.0 <= m.pct_completude_total <= 100.0

    def test_soma_tipos_igual_total_esperado(self, service, db):
        """INV: total_presente_confirmado + total_presente_pendente + total_faltante >= total_esperado."""
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        m = result.metricas
        total_presente = m.total_presente_confirmado + m.total_presente_pendente_revisao
        # Pode ser > total_esperado se um tipo_doc tem múltiplos arquivos
        assert total_presente + m.total_faltante >= m.total_esperado

    def test_docs_presentes_tem_campos_corretos(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        for dp in result.docs_presentes:
            assert isinstance(dp, DocumentoPresente)
            assert dp.tipo_documento
            assert dp.escopo in ("condominio", "empresa_matriz", "funcionario")
            assert isinstance(dp.onvio_document_id, UUID)
            assert isinstance(dp.revisao_pendente, bool)

    def test_docs_faltantes_tem_campos_corretos(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        motivos_validos = {
            "nao_encontrado_onvio",
            "aguarda_fase_1_cnd",
            "aguarda_fase_2_banco",
            "nao_sincronizado",
        }
        for df in result.docs_faltantes:
            assert isinstance(df, DocumentoFaltante)
            assert df.motivo in motivos_validos
            assert df.periodicidade


# ---------------------------------------------------------------------------
# Cenário 2 — docs confirmados vs pendentes revisão separados corretamente
# ---------------------------------------------------------------------------
class TestDocumentosPendentesVsConfirmados:
    def test_separacao_confirmados_pendentes(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        m = result.metricas
        total_presente = m.total_presente_confirmado + m.total_presente_pendente_revisao
        assert len(result.docs_presentes) == total_presente

    def test_revisao_pendente_e_booleano(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        for p in result.docs_presentes:
            assert isinstance(p.revisao_pendente, bool)


# ---------------------------------------------------------------------------
# Cenário 3 — CNDs aparecem como faltantes (aguarda_fase_1_cnd)
# ---------------------------------------------------------------------------
class TestCndsSempreFaltantes:
    def test_cnds_presentes_nos_faltantes(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        tipos_faltantes = {d.tipo_documento for d in result.docs_faltantes}
        for cnd in TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND:
            assert cnd in tipos_faltantes, f"CND '{cnd}' deveria estar em docs_faltantes"

    def test_cnds_motivo_correto(self, service, db):
        cid = _get_condominio_id(db, "ideal_flores")
        result = service.build_completude(cid, "03.2026")
        cnds = [d for d in result.docs_faltantes if d.tipo_documento in TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND]
        assert len(cnds) == 5
        for cnd in cnds:
            assert cnd.motivo == "aguarda_fase_1_cnd"
            assert cnd.escopo == "empresa_matriz"


# ---------------------------------------------------------------------------
# Cenário 4 — Comprovantes de pagamento aparecem como faltantes (aguarda_fase_2_banco)
# ---------------------------------------------------------------------------
class TestCompPagamentosFaltantes:
    def test_comp_pagamentos_aparecem_como_faltantes(self, service, db):
        cid = _get_condominio_id(db, "mirante")
        result = service.build_completude(cid, "03.2026")
        comp_faltantes = [f for f in result.docs_faltantes if f.motivo == "aguarda_fase_2_banco"]
        assert len(comp_faltantes) >= 3


# ---------------------------------------------------------------------------
# Cenários 5-7 — Serviços simples (portaria_remota, manutencao_cftv, portaria_autonoma)
# ---------------------------------------------------------------------------
class TestServicosSimples:
    @pytest.mark.parametrize(
        "nome_norm,tipo_esperado",
        [
            ("p_gelain", "portaria_remota"),
            ("green_hills", "manutencao_cftv"),
            ("parise", "portaria_autonoma"),
        ],
    )
    def test_servicos_simples_tem_2_templates(self, service, db, nome_norm, tipo_esperado):
        cid = _get_condominio_id(db, nome_norm)
        result = service.build_completude(cid, "03.2026")
        assert result.tipo_servico == tipo_esperado
        assert result.metricas.total_esperado == 2


# ---------------------------------------------------------------------------
# Cenário 8 — Administrativo retorna kit vazio (INV-7)
# ---------------------------------------------------------------------------
class TestAdministrativo:
    def test_administrativo_retorna_kit_vazio(self, service, db):
        cid = _get_condominio_id(db, "escritorio")
        result = service.build_completude(cid, "03.2026")
        assert result.tipo_servico == "administrativo"
        assert result.metricas.total_esperado == 0
        assert result.metricas.total_faltante == 0
        assert result.docs_presentes == []
        assert result.docs_faltantes == []
        assert result.metricas.pct_completude_confirmada == 0.0


# ---------------------------------------------------------------------------
# build_lote_condominios — 11 condomínios
# ---------------------------------------------------------------------------
class TestBuildLote:
    def test_retorna_11_condominios(self, service):
        results = service.build_lote_condominios("03.2026")
        assert len(results) == 11

    def test_mes_ref_preservado_em_todos(self, service):
        results = service.build_lote_condominios("03.2026")
        for r in results:
            assert r.mes_ref == "03.2026"
            assert r.condominio_id is not None

    def test_lote_mes_ref_invalido_levanta(self, service):
        with pytest.raises(ValueError, match="mes_ref inválido"):
            service.build_lote_condominios("2026/03")


# ---------------------------------------------------------------------------
# _determinar_motivo_faltante
# ---------------------------------------------------------------------------
class TestDeterminarMotivo:
    def test_motivo_cnd(self):
        assert _determinar_motivo_faltante("cnd_rfb") == "aguarda_fase_1_cnd"
        assert _determinar_motivo_faltante("cnd_trabalhista") == "aguarda_fase_1_cnd"

    def test_motivo_banco(self):
        assert _determinar_motivo_faltante("comp_pag_fgts") == "aguarda_fase_2_banco"
        assert _determinar_motivo_faltante("comp_salario_individual") == "aguarda_fase_2_banco"
        assert _determinar_motivo_faltante("nfse") == "aguarda_fase_2_banco"
        assert _determinar_motivo_faltante("boleto") == "aguarda_fase_2_banco"

    def test_motivo_sem_sincronizacao(self):
        assert _determinar_motivo_faltante("comp_va_solides") == "nao_sincronizado"
        assert _determinar_motivo_faltante("relatorio_pedido_va") == "nao_sincronizado"

    def test_motivo_generico(self):
        assert _determinar_motivo_faltante("tipo_qualquer") == "nao_encontrado_onvio"


# ---------------------------------------------------------------------------
# CategoriaToTipoDocumento (sanity — §26.3)
# ---------------------------------------------------------------------------
class TestCategoriaToTipoDocumento:
    def test_tem_20_entradas(self):
        assert len(CategoriaToTipoDocumento) == 20

    def test_chaves_esperadas(self):
        assert CategoriaToTipoDocumento["folha_pagamento"] == "folha_pagamento"
        assert CategoriaToTipoDocumento["recibo_folha"] == "contracheque"
        assert CategoriaToTipoDocumento["fgts_guia"] == "gfd_fgts_mensal"
        assert CategoriaToTipoDocumento["dctfweb_resumo_creditos"] == "dctfweb_extrato"
        assert CategoriaToTipoDocumento["dctfweb_debitos"] == "dctfweb_extrato"
