"""
Testes do Portal do Funcionario — Auth + Endpoints.

Cobre: auth JWT com audience, token refresh, perfil, beneficios,
CCT direitos, feriados, adicional noturno, calculadora, comunicados.
"""

import pytest


class TestPortalAuth:
    """Testes de autenticacao do portal."""

    def test_create_access_token(self):
        from jose import jwt

        from core.config import settings
        from modules.people_management.employee_portal.auth import (
            PORTAL_AUDIENCE,
            create_portal_access_token,
        )

        token = create_portal_access_token(
            "emp-123",
            "Joao Silva",
            "Porteiro",
            cpf="03527554238",
            escala="12x36",
        )
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], audience=PORTAL_AUDIENCE
        )

        assert payload["employee_id"] == "emp-123"
        assert payload["nome"] == "Joao Silva"
        assert payload["cargo"] == "Porteiro"
        assert payload["cpf"] == "03527554238"
        assert payload["escala"] == "12x36"
        assert payload["aud"] == "employee_portal"
        assert payload["type"] == "portal_access"
        assert "jti" in payload
        assert "exp" in payload

    def test_create_refresh_token(self):
        from jose import jwt

        from core.config import settings
        from modules.people_management.employee_portal.auth import (
            PORTAL_AUDIENCE,
            create_portal_refresh_token,
        )

        token = create_portal_refresh_token("emp-123")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], audience=PORTAL_AUDIENCE
        )

        assert payload["sub"] == "emp-123"
        assert payload["aud"] == "employee_portal"
        assert payload["type"] == "portal_refresh"
        assert "jti" in payload

    def test_decode_portal_token_valid(self):
        from modules.people_management.employee_portal.auth import (
            _decode_portal_token,
            create_portal_access_token,
        )

        token = create_portal_access_token("emp-456", "Maria", "Zeladora")
        payload = _decode_portal_token(token, "portal_access")

        assert payload["employee_id"] == "emp-456"
        assert payload["aud"] == "employee_portal"

    def test_decode_portal_token_wrong_type(self):
        from fastapi import HTTPException

        from modules.people_management.employee_portal.auth import (
            _decode_portal_token,
            create_portal_refresh_token,
        )

        token = create_portal_refresh_token("emp-123")

        with pytest.raises(HTTPException) as exc_info:
            _decode_portal_token(token, "portal_access")
        assert exc_info.value.status_code == 401

    def test_decode_admin_token_rejected(self):
        from fastapi import HTTPException

        from core.auth.jwt import create_access_token
        from modules.people_management.employee_portal.auth import _decode_portal_token

        admin_token = create_access_token("admin-user-id")

        with pytest.raises(HTTPException) as exc_info:
            _decode_portal_token(admin_token, "portal_access")
        assert exc_info.value.status_code == 401

    def test_token_audience_prevents_crossover(self):
        from jose import jwt
        from jose.exceptions import JWTClaimsError

        from core.config import settings
        from modules.people_management.employee_portal.auth import create_portal_access_token

        token = create_portal_access_token("emp-789", "Pedro", "Vigia")

        # Tentar decodificar com audience errada
        with pytest.raises(JWTClaimsError):
            jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], audience="admin")


class TestPortalSchemas:
    """Testes dos schemas do portal."""

    def test_login_request_with_password(self):
        from modules.people_management.employee_portal.schemas.portal import PortalLoginRequest

        req = PortalLoginRequest(cpf="03527554238", password="1234")
        assert req.cpf == "03527554238"
        assert req.password == "1234"
        assert req.data_nascimento is None

    def test_login_request_with_data_nascimento(self):
        from modules.people_management.employee_portal.schemas.portal import PortalLoginRequest

        req = PortalLoginRequest(cpf="03527554238", data_nascimento="1990-05-15")
        assert req.data_nascimento == "1990-05-15"
        assert req.password is None

    def test_login_response(self):
        from modules.people_management.employee_portal.schemas.portal import PortalLoginResponse

        resp = PortalLoginResponse(
            access_token="abc",
            refresh_token="def",
            employee_name="Joao",
            employee_id="uuid-123",
        )
        assert resp.token_type == "bearer"
        assert resp.expires_in == 28800

    def test_dashboard(self):
        from modules.people_management.employee_portal.schemas.portal import PortalDashboard

        dash = PortalDashboard(name="Joao")
        assert dash.pending_documents == 0


class TestPortalCCTIntegration:
    """Testes de integracao CCT com portal."""

    def test_benefits_cct_data_available(self):
        from modules.cct.models.benefits import BENEFICIOS_OBRIGATORIOS_CCT, get_beneficios_obrigatorios

        obrig = get_beneficios_obrigatorios()
        assert len(obrig) == 6

    def test_holidays_available(self):
        from modules.cct.models.holidays import FERIADOS_MANAUS_2026

        assert len(FERIADOS_MANAUS_2026) == 16

    def test_salary_validator_available(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        result = SalaryValidator.validar_salario("PORTEIROS AGENTE DE PORTARIA GUARDETE", 1670.00)
        assert result["conforme"] is True

    def test_schedule_validator_available(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        result = ScheduleValidator.calcular_adicional_noturno(
            salario_base=1670.00,
            jornada_tipo="12x36",
            horas_noturnas=7,
        )
        assert result["valor_adicional_noturno"] > 0

    def test_termination_validator_available(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        result = TerminationValidator.validar_rescisao(
            employee_id="test",
            data_admissao="2024-01-01",
            data_demissao="2026-03-15",
            salario_base=1670.00,
            motivo="sem_justa_causa",
        )
        assert result["homologacao_obrigatoria"] is True


class TestPortalControllerImports:
    """Testes de importacao dos controllers."""

    def test_import_portal_controller(self):
        from modules.people_management.employee_portal.controllers.portal_controller import router

        assert router is not None

    def test_import_my_benefits_controller(self):
        from modules.people_management.employee_portal.controllers.my_benefits_controller import router

        assert router is not None

    def test_import_my_cct_controller(self):
        from modules.people_management.employee_portal.controllers.my_cct_controller import router

        assert router is not None

    def test_import_my_profile_controller(self):
        from modules.people_management.employee_portal.controllers.my_profile_controller import router

        assert router is not None

    def test_import_my_comunicados_controller(self):
        from modules.people_management.employee_portal.controllers.my_comunicados_controller import router

        assert router is not None

    def test_import_my_ponto_controller(self):
        from modules.people_management.employee_portal.controllers.my_ponto_controller import router

        assert router is not None

    def test_import_aggregator(self):
        from modules.people_management.employee_portal.aggregator import router

        assert router is not None

    def test_aggregator_has_all_routes(self):
        from modules.people_management.employee_portal.aggregator import router

        paths = [r.path for r in router.routes]
        # Auth
        assert "/portal/auth/login" in paths
        assert "/portal/auth/me" in paths
        assert "/portal/auth/logout" in paths
        assert "/portal/auth/refresh" in paths
        # Perfil e contrato
        assert "/portal/perfil" in paths
        assert "/portal/contrato" in paths
        # Contracheques (historico + detalhado + PDF)
        assert "/portal/my-payslips" in paths
        assert "/portal/my-payslips/{month}/{year}" in paths
        assert "/portal/my-payslips/{month}/{year}/pdf" in paths
        # Ponto e banco de horas
        assert "/portal/ponto/historico" in paths
        assert "/portal/banco-horas" in paths
        # Beneficios e CCT
        assert "/portal/my-benefits" in paths
        assert "/portal/cct/direitos" in paths
        assert "/portal/cct/feriados" in paths
        assert "/portal/cct/adicional-noturno" in paths
        assert "/portal/cct/calculadora" in paths
        # Documentos e comunicados
        assert "/portal/comunicados" in paths
