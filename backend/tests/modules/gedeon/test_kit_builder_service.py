"""
Testes de integração — KitBuilderService (§26 CONTRACTS_GEDEON.md v1.21).
Usa banco de dados real via SyncSessionLocal (sem mocks).
Todos os cenários cobrem §26.4–§26.8.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from modules.gedeon.services.kit_builder_service import (
    _CND_TIPOS,
    _COMP_PAGAMENTOS_TIPOS,
    CATEGORIA_TO_TIPO_DOCUMENTO,
    CompletudeKit,
    DocumentoFaltante,
    DocumentoPresente,
    KitBuilderService,
    MetricasKit,
)

# ---------------------------------------------------------------------------
# Fixtures com IDs reais (seed planilha GEDEON 03/2026 — §22.3)
# ---------------------------------------------------------------------------
IDEAL_FLORES_ID = UUID("215a124b-2dd7-4125-ab3f-6efa3aa67c99")  # kit_mensal
LARANJEIRAS_ID = UUID("7c2323fd-e226-4121-806d-d9b2598feeed")  # kit_mensal
PARISE_ID = UUID("9be1e32b-0ff1-4668-9094-74f720c9a487")  # portaria_autonoma
P_GELAIN_ID = UUID("ab146423-859e-4e6e-aeaf-041987a18f25")  # portaria_remota
GREEN_HILLS_ID = UUID("4900de33-c778-4792-818d-e0901b559aed")  # manutencao_cftv
ESCRITORIO_ID = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")  # administrativo

MES_REF_VALIDO = "03.2026"
MES_REF_SEM_DOCS = "06.2020"  # mês sem docs em onvio_documents


@pytest.fixture
def svc() -> KitBuilderService:
    return KitBuilderService()


# ---------------------------------------------------------------------------
# Cenário 1 — mes_ref inválido levanta ValueError (§26.7)
# ---------------------------------------------------------------------------
class TestMesRefValidacao:
    def test_formato_errado_levanta_value_error(self, svc):
        with pytest.raises(ValueError, match="MM.YYYY"):
            svc.build_completude(IDEAL_FLORES_ID, "2026-03")

    def test_mes_sem_ponto_levanta_value_error(self, svc):
        with pytest.raises(ValueError, match="MM.YYYY"):
            svc.build_completude(IDEAL_FLORES_ID, "032026")

    def test_build_lote_mes_ref_invalido(self, svc):
        with pytest.raises(ValueError, match="MM.YYYY"):
            svc.build_lote_condominios("2026/03")


# ---------------------------------------------------------------------------
# Cenário 2 — condomínio inexistente levanta ValueError
# ---------------------------------------------------------------------------
class TestCondominioInexistente:
    def test_uuid_inexistente_levanta_value_error(self, svc):
        with pytest.raises(ValueError, match="não encontrado"):
            svc.build_completude(uuid4(), MES_REF_VALIDO)


# ---------------------------------------------------------------------------
# Cenário 3 — kit_mensal: estrutura geral (32 templates)
# ---------------------------------------------------------------------------
class TestKitMensalEstrutura:
    def test_retorna_completude_kit(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        assert isinstance(kit, CompletudeKit)
        assert kit.condominio_id == IDEAL_FLORES_ID
        assert kit.tipo_servico == "kit_mensal"
        assert kit.mes_ref == MES_REF_VALIDO

    def test_total_esperados_igual_32_templates(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        assert kit.metricas.total_esperados == 32

    def test_soma_presentes_mais_faltantes_igual_total(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        m = kit.metricas
        assert m.total_presentes + m.total_faltantes == m.total_esperados

    def test_percentual_completude_entre_0_e_100(self, svc):
        kit = svc.build_completude(LARANJEIRAS_ID, MES_REF_VALIDO)
        assert 0.0 <= kit.metricas.percentual_completude <= 100.0

    def test_docs_presentes_tem_campos_obrigatorios(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        for dp in kit.docs_presentes:
            assert isinstance(dp, DocumentoPresente)
            assert dp.tipo_documento
            assert dp.escopo in ("condominio", "funcionario", "empresa_matriz")
            assert dp.mes_ref == MES_REF_VALIDO

    def test_docs_faltantes_tem_motivo_valido(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        motivos_validos = {"nao_encontrado", "aguarda_fase_1_cnd", "aguarda_fase_2_banco"}
        for df in kit.docs_faltantes:
            assert isinstance(df, DocumentoFaltante)
            assert df.motivo in motivos_validos


# ---------------------------------------------------------------------------
# Cenário 4 — CNDs sempre faltantes com motivo aguarda_fase_1_cnd (§26.4)
# ---------------------------------------------------------------------------
class TestCndsSempreFaltantes:
    def test_cnds_presentes_nos_faltantes(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        tipos_faltantes = {d.tipo_documento for d in kit.docs_faltantes}
        for cnd in _CND_TIPOS:
            assert cnd in tipos_faltantes, f"CND '{cnd}' deveria estar em docs_faltantes"

    def test_cnds_motivo_correto(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        cnds = [d for d in kit.docs_faltantes if d.tipo_documento in _CND_TIPOS]
        assert len(cnds) == 5
        for cnd in cnds:
            assert cnd.motivo == "aguarda_fase_1_cnd"

    def test_cnds_nao_aparecem_em_presentes(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        tipos_presentes = {d.tipo_documento for d in kit.docs_presentes}
        for cnd in _CND_TIPOS:
            assert cnd not in tipos_presentes


# ---------------------------------------------------------------------------
# Cenário 5 — comp_pagamentos sempre faltantes com motivo aguarda_fase_2_banco (§26.5)
# ---------------------------------------------------------------------------
class TestCompPagamentosSempreFaltantes:
    def test_comp_pagamentos_nos_faltantes(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        tipos_faltantes = {d.tipo_documento for d in kit.docs_faltantes}
        for comp in _COMP_PAGAMENTOS_TIPOS:
            assert comp in tipos_faltantes, f"'{comp}' deveria estar em docs_faltantes"

    def test_comp_pagamentos_motivo_correto(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_VALIDO)
        comps = [d for d in kit.docs_faltantes if d.tipo_documento in _COMP_PAGAMENTOS_TIPOS]
        assert len(comps) == len(_COMP_PAGAMENTOS_TIPOS)
        for comp in comps:
            assert comp.motivo == "aguarda_fase_2_banco"


# ---------------------------------------------------------------------------
# Cenário 6–8 — portaria/manutencao/autonoma (2 templates cada)
# ---------------------------------------------------------------------------
class TestServicosSimples:
    def test_portaria_autonoma_2_templates(self, svc):
        kit = svc.build_completude(PARISE_ID, MES_REF_VALIDO)
        assert kit.tipo_servico == "portaria_autonoma"
        assert kit.metricas.total_esperados == 2

    def test_portaria_remota_2_templates(self, svc):
        kit = svc.build_completude(P_GELAIN_ID, MES_REF_VALIDO)
        assert kit.tipo_servico == "portaria_remota"
        assert kit.metricas.total_esperados == 2

    def test_manutencao_cftv_2_templates(self, svc):
        kit = svc.build_completude(GREEN_HILLS_ID, MES_REF_VALIDO)
        assert kit.tipo_servico == "manutencao_cftv"
        assert kit.metricas.total_esperados == 2


# ---------------------------------------------------------------------------
# Cenário 9 — administrativo: tipo_servico sem templates → 0 esperados
# ---------------------------------------------------------------------------
class TestAdministrativo:
    def test_administrativo_zero_templates(self, svc):
        kit = svc.build_completude(ESCRITORIO_ID, MES_REF_VALIDO)
        assert kit.metricas.total_esperados == 0
        assert kit.metricas.percentual_completude == 0.0
        assert kit.docs_presentes == []
        assert kit.docs_faltantes == []


# ---------------------------------------------------------------------------
# Cenário 10 — build_lote: 11 condomínios ativos
# ---------------------------------------------------------------------------
class TestBuildLote:
    def test_retorna_11_condominios(self, svc):
        lote = svc.build_lote_condominios(MES_REF_VALIDO)
        assert len(lote) == 11

    def test_todos_items_sao_completude_kit(self, svc):
        lote = svc.build_lote_condominios(MES_REF_VALIDO)
        for item in lote:
            assert isinstance(item, CompletudeKit)

    def test_mes_ref_preservado_em_todos(self, svc):
        lote = svc.build_lote_condominios(MES_REF_VALIDO)
        for item in lote:
            assert item.mes_ref == MES_REF_VALIDO


# ---------------------------------------------------------------------------
# Cenário 11 — mês sem docs: todos templates faltantes (exceto CNDs/comp que já são)
# ---------------------------------------------------------------------------
class TestMesSemDocs:
    def test_mes_sem_docs_total_presentes_zero(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_SEM_DOCS)
        assert kit.metricas.total_presentes == 0
        assert kit.docs_presentes == []

    def test_mes_sem_docs_total_faltantes_igual_total_esperados(self, svc):
        kit = svc.build_completude(IDEAL_FLORES_ID, MES_REF_SEM_DOCS)
        m = kit.metricas
        assert m.total_faltantes == m.total_esperados


# ---------------------------------------------------------------------------
# Cenário 12 — CATEGORIA_TO_TIPO_DOCUMENTO (§26.3) imutável e completo
# ---------------------------------------------------------------------------
class TestCategoriaToTipoDocumento:
    def test_mapping_tem_20_entradas(self):
        assert len(CATEGORIA_TO_TIPO_DOCUMENTO) == 20

    def test_todos_valores_sao_strings_nao_vazias(self):
        for k, v in CATEGORIA_TO_TIPO_DOCUMENTO.items():
            assert isinstance(k, str) and k
            assert isinstance(v, str) and v

    def test_dctfweb_resumo_creditos_mapeia_para_extrato(self):
        assert CATEGORIA_TO_TIPO_DOCUMENTO["dctfweb_resumo_creditos"] == "dctfweb_extrato"

    def test_recibo_folha_mapeia_para_contracheque(self):
        assert CATEGORIA_TO_TIPO_DOCUMENTO["recibo_folha"] == "contracheque"
