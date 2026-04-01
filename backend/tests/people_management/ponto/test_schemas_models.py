"""Testes dos schemas Pydantic e models SQLAlchemy do Ponto Eletronico."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from modules.people_management.ponto.models.clock_punch import (
    ClockPunchModel,
    ClockPunchStatus,
    ClockPunchType,
)
from modules.people_management.ponto.models.justification import (
    JustificationCategory,
    JustificationModel,
    JustificationStatus,
)
from modules.people_management.ponto.models.monthly_closing import MonthlyClosingModel
from modules.people_management.ponto.schemas.dashboard_schemas import (
    AjusteRequest,
    BancoHorasResponse,
    ColaboradorSemEscalaResponse,
    DashboardPontoResponse,
    InconsistenciaResponse,
    InconsistenciaResumoResponse,
    SyncSolidesRequest,
    SyncSolidesResponse,
    TipoInconsistencia,
)
from modules.people_management.ponto.schemas.punch_schemas import (
    FacialSchema,
    GeoLocationSchema,
    JustificationCreate,
    JustificationResponse,
    JustificationReview,
    MonthlyClosingResponse,
    PunchCreate,
    PunchResponse,
    PunchSyncRequest,
    PunchSyncResponse,
)

# ========================================================================
# ENUMS
# ========================================================================


class TestClockPunchTypeEnum:
    def test_valores(self):
        assert ClockPunchType.ENTRADA == "entrada"
        assert ClockPunchType.SAIDA_ALMOCO == "saida_almoco"
        assert ClockPunchType.RETORNO_ALMOCO == "retorno_almoco"
        assert ClockPunchType.SAIDA == "saida"

    def test_total_valores(self):
        assert len(ClockPunchType) == 4


class TestClockPunchStatusEnum:
    def test_valores(self):
        assert ClockPunchStatus.NORMAL == "normal"
        assert ClockPunchStatus.ATRASO == "atraso"
        assert ClockPunchStatus.ANTECIPADO == "antecipado"
        assert ClockPunchStatus.FORA_LOCAL == "fora_local"
        assert ClockPunchStatus.OFFLINE == "offline"
        assert ClockPunchStatus.SYNC_OK == "sync_ok"
        assert ClockPunchStatus.SYNC_ERROR == "sync_error"

    def test_total_valores(self):
        assert len(ClockPunchStatus) == 7


class TestJustificationEnums:
    def test_categorias(self):
        assert JustificationCategory.TRANSITO == "transito"
        assert JustificationCategory.SAUDE == "saude"
        assert JustificationCategory.FAMILIAR == "familiar"
        assert JustificationCategory.TRANSPORTE_PUBLICO == "transporte_publico"
        assert JustificationCategory.ACIDENTE == "acidente"
        assert JustificationCategory.OUTRO == "outro"
        assert len(JustificationCategory) == 6

    def test_status(self):
        assert JustificationStatus.PENDENTE == "pendente"
        assert JustificationStatus.APROVADA == "aprovada"
        assert JustificationStatus.REJEITADA == "rejeitada"
        assert len(JustificationStatus) == 3


class TestTipoInconsistencia:
    def test_todos_tipos(self):
        assert TipoInconsistencia.FALTA_BATIDA_ENTRADA == "falta_batida_entrada"
        assert TipoInconsistencia.JORNADA_EXCEDIDA == "jornada_excedida"
        assert TipoInconsistencia.INTRAJORNADA_NAO_CONCEDIDA == "intrajornada_nao_concedida"
        assert TipoInconsistencia.ESCALA_NAO_CADASTRADA == "escala_nao_cadastrada"
        assert TipoInconsistencia.PONTO_EM_ABERTO == "ponto_em_aberto"
        assert len(TipoInconsistencia) == 8


# ========================================================================
# PUNCH SCHEMAS
# ========================================================================


class TestGeoLocationSchema:
    def test_valido(self):
        geo = GeoLocationSchema(latitude=-3.1, longitude=-60.0, accuracy=10.0)
        assert geo.latitude == -3.1
        assert geo.accuracy == 10.0

    def test_accuracy_default(self):
        geo = GeoLocationSchema(latitude=0.0, longitude=0.0)
        assert geo.accuracy == 0.0


class TestFacialSchema:
    def test_valido(self):
        f = FacialSchema(match=True, confidence=0.95)
        assert f.match is True
        assert f.liveness_check is True  # default

    def test_com_foto(self):
        f = FacialSchema(match=True, confidence=0.9, foto_base64="base64data")
        assert f.foto_base64 == "base64data"


class TestPunchCreate:
    def test_minimo(self):
        p = PunchCreate(employee_id=1, punch_type="entrada")
        assert p.device_type == "web"
        assert p.is_offline is False
        assert p.location is None
        assert p.facial is None

    def test_completo(self):
        p = PunchCreate(
            employee_id="emp-1",
            punch_type="saida",
            timestamp="2026-03-13T17:00:00",
            location=GeoLocationSchema(latitude=-3.1, longitude=-60.0),
            facial=FacialSchema(match=True, confidence=0.99),
            device_type="mobile",
            is_offline=True,
            posto_id=42,
        )
        assert p.employee_id == "emp-1"
        assert p.posto_id == 42

    def test_sem_employee_id_invalido(self):
        with pytest.raises(ValidationError):
            PunchCreate(punch_type="entrada")

    def test_sem_punch_type_invalido(self):
        with pytest.raises(ValidationError):
            PunchCreate(employee_id=1)


class TestPunchResponse:
    def test_valido(self):
        r = PunchResponse(punch_id="abc", employee_id=1, punch_type="entrada", status="normal")
        assert r.message == "Ponto registrado"
        assert r.is_offline is False

    def test_com_geofence(self):
        r = PunchResponse(
            punch_id="abc",
            employee_id=1,
            dentro_geofence=True,
            distancia_posto_metros=50.5,
        )
        assert r.dentro_geofence is True


class TestPunchSyncRequest:
    def test_valido(self):
        req = PunchSyncRequest(punches=[PunchCreate(employee_id=1, punch_type="entrada")])
        assert len(req.punches) == 1

    def test_vazio(self):
        req = PunchSyncRequest(punches=[])
        assert len(req.punches) == 0


class TestPunchSyncResponse:
    def test_valido(self):
        r = PunchSyncResponse(
            total_received=4,
            total_synced=3,
            total_duplicates=1,
            total_errors=0,
        )
        assert r.errors == []


class TestJustificationCreate:
    def test_valido(self):
        j = JustificationCreate(
            employee_id=1,
            justification_type="atraso",
            reason="Transito muito intenso",
            category="transito",
        )
        assert j.punch_id is None
        assert j.attachments == []

    def test_reason_curta_invalida(self):
        with pytest.raises(ValidationError):
            JustificationCreate(
                employee_id=1,
                justification_type="atraso",
                reason="abc",
                category="transito",
            )

    def test_com_anexos(self):
        j = JustificationCreate(
            employee_id=1,
            justification_type="falta",
            reason="Atestado medico",
            category="saude",
            attachments=[{"file": "doc.pdf"}],
        )
        assert len(j.attachments) == 1


class TestJustificationResponse:
    def test_valido(self):
        r = JustificationResponse(
            justification_id="j1",
            employee_id=1,
            type="atraso",
            reason="Motivo",
            category="transito",
            status="pendente",
            created_at="2026-03-13T10:00:00",
        )
        assert r.reviewed_by is None


class TestJustificationReview:
    def test_aprovar(self):
        r = JustificationReview(action="aprovar", reviewer_id="sup-1")
        assert r.notes is None

    def test_rejeitar_com_notes(self):
        r = JustificationReview(action="rejeitar", reviewer_id="sup-1", notes="Sem comprovante")
        assert r.notes == "Sem comprovante"


class TestMonthlyClosingResponse:
    def test_valido(self):
        r = MonthlyClosingResponse(
            employee_id=1,
            month=3,
            year=2026,
            total_horas_trabalhadas=160.0,
            total_horas_extras_50=10.0,
            total_horas_extras_100=2.0,
            total_faltas=1,
            total_atrasos_minutos=30.0,
            fechado=True,
        )
        assert r.fechado is True


# ========================================================================
# DASHBOARD SCHEMAS
# ========================================================================


class TestDashboardSchemas:
    def test_inconsistencia_response(self):
        r = InconsistenciaResponse(
            employee_id="1",
            employee_nome="Joao",
            data="2026-03-13",
            tipo=TipoInconsistencia.PONTO_EM_ABERTO,
            descricao="Ponto sem saida",
        )
        assert r.gravidade == "media"
        assert r.resolvida is False

    def test_inconsistencia_resumo(self):
        r = InconsistenciaResumoResponse(
            periodo_inicio="2026-03-01",
            periodo_fim="2026-03-31",
            total_inconsistencias=5,
            por_tipo={"ponto_em_aberto": 3},
            por_gravidade={"alta": 2, "media": 3},
        )
        assert r.total_inconsistencias == 5

    def test_banco_horas(self):
        r = BancoHorasResponse(
            employee_id="1",
            employee_nome="Maria",
            saldo_horas=12.5,
            creditos=15.0,
            debitos=2.5,
        )
        assert r.saldo_horas == 12.5

    def test_dashboard_ponto(self):
        r = DashboardPontoResponse(
            total_colaboradores=44,
            presentes_hoje=30,
            ausentes_hoje=10,
            afastados=4,
        )
        assert r.inconsistencias_periodo == 0

    def test_sync_solides_request_defaults(self):
        r = SyncSolidesRequest()
        assert r.periodo_inicio is None
        assert r.force is False

    def test_sync_solides_response(self):
        r = SyncSolidesResponse(
            success=True,
            message="OK",
            total_importados=100,
        )
        assert r.erros == []

    def test_ajuste_request(self):
        r = AjusteRequest(
            employee_id="1",
            data="2026-03-13",
            punch_type="entrada",
            timestamp="2026-03-13T08:00:00",
            motivo="Esqueceu de bater ponto",
            ajustado_por="admin",
        )
        assert r.motivo == "Esqueceu de bater ponto"

    def test_ajuste_request_motivo_curto(self):
        with pytest.raises(ValidationError):
            AjusteRequest(
                employee_id="1",
                data="2026-03-13",
                punch_type="entrada",
                timestamp="2026-03-13T08:00:00",
                motivo="abc",
                ajustado_por="admin",
            )

    def test_colaborador_sem_escala(self):
        r = ColaboradorSemEscalaResponse(
            employee_id="1",
            nome="Pedro",
            cargo="Vigilante",
            data_admissao="2025-01-15",
        )
        assert r.nome == "Pedro"


# ========================================================================
# MODELS — to_dict
# ========================================================================


class TestClockPunchModelToDict:
    def test_to_dict_completo(self):
        now = datetime(2026, 3, 13, 8, 0, 0)
        model = ClockPunchModel(
            id=1,
            punch_id="abc-123",
            employee_id="emp-1",
            punch_type="entrada",
            punch_timestamp=now,
            server_timestamp=now,
            status="normal",
            facial_match=True,
            facial_confidence=0.95,
            latitude=-3.1,
            longitude=-60.0,
            dentro_geofence=True,
            device_type="mobile",
            is_offline=False,
            posto_id="p1",
            justification_id=None,
            created_at=now,
        )
        d = model.to_dict()
        assert d["punch_id"] == "abc-123"
        assert d["punch_type"] == "entrada"
        assert d["punch_timestamp"] == "2026-03-13T08:00:00"
        assert d["facial_match"] is True
        assert d["latitude"] == -3.1
        assert d["dentro_geofence"] is True
        assert d["is_offline"] is False

    def test_to_dict_campos_nulos(self):
        model = ClockPunchModel(
            id=2,
            punch_id="xyz",
            employee_id="1",
            punch_type="saida",
            punch_timestamp=datetime(2026, 3, 13, 17, 0),
            server_timestamp=datetime(2026, 3, 13, 17, 0),
            status="normal",
            created_at=datetime(2026, 3, 13, 17, 0),
        )
        d = model.to_dict()
        assert d["facial_match"] is None
        assert d["latitude"] is None
        assert d["dentro_geofence"] is None

    def test_tablename(self):
        assert ClockPunchModel.__tablename__ == "gp_clock_punches"


class TestJustificationModelToDict:
    def test_to_dict(self):
        now = datetime(2026, 3, 13, 10, 0, 0)
        model = JustificationModel(
            id=1,
            justification_id="j-1",
            employee_id=1,
            justification_type="atraso",
            reason="Transito",
            category="transito",
            status="pendente",
            attachments=[{"file": "doc.pdf"}],
            created_at=now,
        )
        d = model.to_dict()
        assert d["justification_id"] == "j-1"
        assert d["type"] == "atraso"
        assert d["status"] == "pendente"
        assert d["attachments"] == [{"file": "doc.pdf"}]
        assert d["reviewed_by"] is None

    def test_to_dict_aprovada(self):
        now = datetime(2026, 3, 13, 10, 0, 0)
        reviewed = datetime(2026, 3, 13, 14, 0, 0)
        model = JustificationModel(
            id=2,
            justification_id="j-2",
            employee_id=1,
            justification_type="falta",
            reason="Atestado medico",
            category="saude",
            status="aprovada",
            reviewed_by="sup-1",
            reviewed_at=reviewed,
            created_at=now,
        )
        d = model.to_dict()
        assert d["status"] == "aprovada"
        assert d["reviewed_by"] == "sup-1"
        assert d["reviewed_at"] == "2026-03-13T14:00:00"

    def test_tablename(self):
        assert JustificationModel.__tablename__ == "gp_justifications"


class TestMonthlyClosingModelToDict:
    def test_to_dict(self):
        now = datetime(2026, 3, 31, 18, 0, 0)
        model = MonthlyClosingModel(
            id=1,
            employee_id=1,
            month=3,
            year=2026,
            total_horas_trabalhadas=160.0,
            total_horas_extras_50=8.0,
            total_horas_extras_100=2.0,
            total_horas_noturnas=0.0,
            total_faltas=1,
            total_atrasos_minutos=45.0,
            total_dias_trabalhados=20,
            fechado=True,
            fechado_em=now,
        )
        d = model.to_dict()
        assert d["employee_id"] == 1
        assert d["month"] == 3
        assert d["total_horas_trabalhadas"] == 160.0
        assert d["total_dias_trabalhados"] == 20
        assert d["fechado"] is True
        assert d["fechado_em"] == "2026-03-31T18:00:00"

    def test_to_dict_nao_fechado(self):
        model = MonthlyClosingModel(
            id=2,
            employee_id=2,
            month=3,
            year=2026,
            total_horas_trabalhadas=0.0,
            fechado=False,
        )
        d = model.to_dict()
        assert d["fechado"] is False
        assert d["fechado_em"] is None

    def test_tablename(self):
        assert MonthlyClosingModel.__tablename__ == "gp_monthly_closings"
