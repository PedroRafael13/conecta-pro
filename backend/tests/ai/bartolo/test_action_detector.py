"""
Testes automatizados para o ActionDetector do Bartolo.

Testa:
- Detecao de 13 tipos de acao via pattern matching
- Extracao de parametros (posto, mes, ano, funcionario, escala)
- Calculo de confianca
- Mapeamento de categorias
- Frases que NAO devem detectar acao (negativos)
"""

import sys

import pytest

sys.path.insert(0, "/app")

from modules.ai.bartolo.actions.action_detector import ActionDetector
from modules.ai.bartolo.actions.action_schemas import ActionRequest
from modules.ai.bartolo.actions.action_types import ActionCategory, ActionType


class TestActionDetectorPatterns:
    """Testes para detecao de patterns de acao."""

    @pytest.fixture
    def detector(self):
        """Fixture para ActionDetector."""
        return ActionDetector()

    def _detect(self, detector, message, user_id="user-1", session_id="sess-1"):
        """Helper para detectar acao."""
        return detector.detect(message, user_id, session_id)

    # ==========================================================================
    # CREATE_SCALE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "criar escala",
            "criar uma escala",
            "cria escala",
            "gerar escala",
            "gerar uma escala",
            "gera escala",
            "montar escala",
            "montar uma escala",
            "nova escala",
            "nova escala para fevereiro",
        ],
    )
    def test_create_scale(self, detector, message):
        """Testa detecao de CREATE_SCALE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.CREATE_SCALE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # APPROVE_SCALE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "aprovar escala",
            "aprovar a escala",
            "aprova escala",
            "aprova a escala",
        ],
    )
    def test_approve_scale(self, detector, message):
        """Testa detecao de APPROVE_SCALE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.APPROVE_SCALE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # PUBLISH_SCALE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "publicar escala",
            "publicar a escala",
            "publica escala",
            "divulgar escala",
            "divulgar a escala",
            "divulga escala",
        ],
    )
    def test_publish_scale(self, detector, message):
        """Testa detecao de PUBLISH_SCALE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.PUBLISH_SCALE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # ALLOCATE_EMPLOYEE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "alocar funcionario",
            "alocar o funcionario",
            "aloca funcionario",
            "alocar colaborador",
            "alocar o colaborador",
            "colocar o funcionario no posto",
            "colocar o colaborador na escala",
            "designar funcionario",
            "designar o colaborador",
        ],
    )
    def test_allocate_employee(self, detector, message):
        """Testa detecao de ALLOCATE_EMPLOYEE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.ALLOCATE_EMPLOYEE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # TERMINATE_ALLOCATION
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "encerrar alocacao",
            "encerrar a alocacao",
            "encerrar a alocação",
            "terminar alocacao",
            "terminar a alocacao",
            "finalizar alocacao",
            "finalizar a alocacao",
            "remover funcionario do posto",
            "remover o colaborador da escala",
        ],
    )
    def test_terminate_allocation(self, detector, message):
        """Testa detecao de TERMINATE_ALLOCATION."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.TERMINATE_ALLOCATION, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # TRANSFER_EMPLOYEE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "transferir funcionario",
            "transferir o funcionario",
            "transferi funcionario",
            "transferir colaborador",
            "transferir o colaborador",
            "mudar o funcionario de posto",
            "mudar o funcionario para outro posto",
            "mudar o colaborador de local",
            "mudar o colaborador para outra unidade",
        ],
    )
    def test_transfer_employee(self, detector, message):
        """Testa detecao de TRANSFER_EMPLOYEE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.TRANSFER_EMPLOYEE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # CREATE_SHIFT
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "criar turno",
            "criar um turno",
            "cria turno",
            "registrar turno",
            "registrar um turno",
            "registra turno",
            "lancar turno",
            "lancar um turno",
            "lanca turno",
            "lançar turno",
        ],
    )
    def test_create_shift(self, detector, message):
        """Testa detecao de CREATE_SHIFT."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.CREATE_SHIFT, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # REGISTER_CHECKIN
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "registrar entrada",
            "registrar a entrada",
            "fazer check-in",
            "fazer a entrada",
            "fazer checkin",
            "bater entrada",
            "bater a entrada",
            "bater check-in",
            "marcar entrada",
            "marca entrada",
        ],
    )
    def test_register_checkin(self, detector, message):
        """Testa detecao de REGISTER_CHECKIN."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.REGISTER_CHECKIN, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # REGISTER_CHECKOUT
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "registrar saida",
            "registrar a saida",
            "registrar a saída",
            "fazer check-out",
            "fazer a saida",
            "fazer checkout",
            "bater saida",
            "bater a saida",
            "bater check-out",
            "marcar saida",
            "marca saida",
        ],
    )
    def test_register_checkout(self, detector, message):
        """Testa detecao de REGISTER_CHECKOUT."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.REGISTER_CHECKOUT, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # MARK_ABSENCE
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "marcar falta",
            "marcar como falta",
            "marcar como ausente",
            "marca falta",
            "registrar falta",
            "registrar a falta",
            "registrar ausencia",
            "registrar a ausencia",
            "registrar a ausência",
            "registra falta",
        ],
    )
    def test_mark_absence(self, detector, message):
        """Testa detecao de MARK_ABSENCE."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.MARK_ABSENCE, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # CREATE_SUBSTITUTION
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "criar substituicao",
            "criar uma substituicao",
            "criar substituição",
            "criar uma substituição",
            "cria substituicao",
            "substituir funcionario",
            "substituir o funcionario",
            "substituir colaborador",
            "substitui funcionario",
        ],
    )
    def test_create_substitution(self, detector, message):
        """Testa detecao de CREATE_SUBSTITUTION."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.CREATE_SUBSTITUTION, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # SEND_NOTIFICATION
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "enviar notificacao",
            "enviar uma notificacao",
            "enviar notificação",
            "envia notificacao",
            "notificar",
            "avisar",
        ],
    )
    def test_send_notification(self, detector, message):
        """Testa detecao de SEND_NOTIFICATION."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.SEND_NOTIFICATION, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # GENERATE_REPORT
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "gerar relatorio",
            "gerar um relatorio",
            "gerar relatório",
            "gera relatorio",
            "criar relatorio",
            "criar um relatorio",
            "cria relatorio",
            "exportar relatorio",
            "exportar um relatorio",
            "exporta relatorio",
        ],
    )
    def test_generate_report(self, detector, message):
        """Testa detecao de GENERATE_REPORT."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.action_type == ActionType.GENERATE_REPORT, f"Tipo errado para: '{message}'"

    # ==========================================================================
    # Testes negativos - NAO devem detectar acao
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "ola",
            "bom dia",
            "como esta a operacao",
            "quais escalas pendentes",
            "quem esta trabalhando",
            "resumo do dia",
            "me ajude",
            "obrigado",
            "cobertura critica",
            "postos sem cobertura",
            "ver funcionarios",
            "status das escalas",
        ],
    )
    def test_nao_deve_detectar_acao(self, detector, message):
        """Testa que mensagens de consulta NAO detectam acao executiva."""
        result = self._detect(detector, message)
        assert result is None, (
            f"Detectou acao incorretamente para: '{message}' -> {result.action_type if result else None}"
        )


class TestActionDetectorParameterExtraction:
    """Testes para extracao de parametros."""

    @pytest.fixture
    def detector(self):
        return ActionDetector()

    def _detect(self, detector, message, user_id="user-1", session_id="sess-1"):
        return detector.detect(message, user_id, session_id)

    def test_extract_month_name(self, detector):
        """Testa extracao de mes pelo nome."""
        result = self._detect(detector, "criar escala para fevereiro")
        assert result is not None
        assert result.parameters.get("month") == 2

    @pytest.mark.parametrize(
        "month_name,expected_month",
        [
            ("janeiro", 1),
            ("fevereiro", 2),
            ("abril", 4),
            ("maio", 5),
            ("junho", 6),
            ("julho", 7),
            ("agosto", 8),
            ("setembro", 9),
            ("outubro", 10),
            ("novembro", 11),
            ("dezembro", 12),
        ],
    )
    def test_extract_months_by_name(self, detector, month_name, expected_month):
        """Testa extracao de todos os meses por nome."""
        result = self._detect(detector, f"criar escala para {month_name}")
        assert result is not None
        assert result.parameters.get("month") == expected_month, f"Falhou para mes: {month_name}"

    def test_extract_month_year_numeric(self, detector):
        """Testa extracao de mes/ano numerico."""
        result = self._detect(detector, "criar escala 02/2026")
        assert result is not None
        assert result.parameters.get("month") == 2
        assert result.parameters.get("year") == 2026

    def test_extract_year(self, detector):
        """Testa extracao de ano isolado."""
        result = self._detect(detector, "criar escala para fevereiro 2026")
        assert result is not None
        assert result.parameters.get("year") == 2026

    def test_extract_post_code(self, detector):
        """Testa extracao de codigo de posto numerico."""
        result = self._detect(detector, "criar escala posto 001")
        assert result is not None
        assert result.parameters.get("post_code") == "POST-0001"

    def test_extract_post_code_with_hyphen(self, detector):
        """Testa extracao de codigo de posto com hifen."""
        result = self._detect(detector, "criar escala posto POST-0021")
        assert result is not None
        assert result.parameters.get("post_code") == "POST-0021"

    def test_extract_post_code_short(self, detector):
        """Testa extracao de codigo de posto curto (2 digitos)."""
        result = self._detect(detector, "criar escala posto 21")
        assert result is not None
        assert result.parameters.get("post_code") == "POST-0021"

    def test_extract_post_code_normalizes(self, detector):
        """Testa que codigo e normalizado para 4 digitos."""
        result = self._detect(detector, "criar escala post-001")
        assert result is not None
        assert result.parameters.get("post_code") == "POST-0001"

    # ==========================================================================
    # post_name - Nomes de posto em linguagem natural
    # ==========================================================================
    def test_extract_post_name_after_posto(self, detector):
        """Testa extracao de nome apos 'posto'."""
        result = self._detect(detector, "criar escala posto prime arena")
        assert result is not None
        assert result.parameters.get("post_name") == "prime arena"

    def test_extract_post_name_condominio(self, detector):
        """Testa extracao de nome apos 'condomínio'."""
        result = self._detect(detector, "criar escala condominio michelangelo em fevereiro")
        assert result is not None
        assert result.parameters.get("post_name") == "michelangelo"

    def test_extract_post_name_residencial(self, detector):
        """Testa extracao de nome apos 'residencial'."""
        result = self._detect(detector, "criar escala residencial villa dei fiori em fevereiro")
        assert result is not None
        assert "villa" in result.parameters.get("post_name", "")

    def test_extract_post_name_base(self, detector):
        """Testa extracao de nome apos 'base'."""
        result = self._detect(detector, "criar escala base conecta mais")
        assert result is not None
        assert result.parameters.get("post_name") == "conecta mais"

    def test_extract_post_name_with_month(self, detector):
        """Testa que mes nao entra no post_name."""
        result = self._detect(detector, "criar escala posto laranjeiras village em fevereiro 2026")
        assert result is not None
        assert result.parameters.get("post_name") == "laranjeiras village"
        assert result.parameters.get("month") == 2
        assert result.parameters.get("year") == 2026

    def test_post_code_has_priority_over_name(self, detector):
        """Testa que codigo tem prioridade sobre nome."""
        result = self._detect(detector, "criar escala post-0021 fevereiro")
        assert result is not None
        assert result.parameters.get("post_code") == "POST-0021"
        assert "post_name" not in result.parameters

    def test_no_params_extracted(self, detector):
        """Testa que mensagem simples nao extrai parametros exoticos."""
        result = self._detect(detector, "criar escala")
        assert result is not None
        # Pode nao ter parametros ou ter parametros vazios
        assert isinstance(result.parameters, dict)

    # ==========================================================================
    # employee_name - Nome de funcionário em linguagem natural
    # ==========================================================================
    def test_extract_employee_name_after_funcionario(self, detector):
        """Testa extracao de nome apos 'funcionário'."""
        result = self._detect(detector, "alocar funcionário João Silva no posto 21")
        assert result is not None
        assert result.parameters.get("employee_name") == "João Silva"

    def test_extract_employee_name_after_colaborador(self, detector):
        """Testa extracao de nome apos 'colaborador'."""
        result = self._detect(detector, "transferir colaborador Carlos Santos")
        assert result is not None
        assert result.parameters.get("employee_name") == "Carlos Santos"

    def test_extract_employee_name_after_vigilante(self, detector):
        """Testa extracao de nome apos 'vigilante' (com trigger de ação)."""
        result = self._detect(detector, "alocar funcionario vigilante Roberto Lima no posto 5")
        assert result is not None
        assert result.parameters.get("employee_name") == "Roberto Lima"

    def test_extract_employee_name_after_verb_article(self, detector):
        """Testa extracao de nome apos 'alocar o funcionário'."""
        result = self._detect(detector, "alocar o funcionário Pedro Henrique no posto central")
        assert result is not None
        assert result.parameters.get("employee_name") == "Pedro Henrique"

    def test_extract_employee_name_single(self, detector):
        """Testa extracao de nome simples com transferência."""
        result = self._detect(detector, "transferir funcionario Maria para posto 1")
        assert result is not None
        assert result.parameters.get("employee_name") == "Maria"

    def test_extract_matricula(self, detector):
        """Testa extracao de matricula."""
        result = self._detect(detector, "alocar funcionario matricula 12345 no posto 1")
        assert result is not None
        assert result.parameters.get("employee_matricula") == "12345"

    def test_extract_matricula_abbrev(self, detector):
        """Testa extracao de matricula abreviada."""
        result = self._detect(detector, "alocar funcionario mat 98765 no posto 1")
        assert result is not None
        assert result.parameters.get("employee_matricula") == "98765"

    def test_employee_uuid_has_priority(self, detector):
        """Testa que UUID tem prioridade sobre nome."""
        result = self._detect(detector, "alocar funcionário 550e8400-e29b-41d4-a716-446655440000 no posto 1")
        assert result is not None
        assert result.parameters.get("employee_id") == "550e8400-e29b-41d4-a716-446655440000"
        assert "employee_name" not in result.parameters


class TestActionDetectorConfidence:
    """Testes para calculo de confianca."""

    @pytest.fixture
    def detector(self):
        return ActionDetector()

    def _detect(self, detector, message, user_id="user-1", session_id="sess-1"):
        return detector.detect(message, user_id, session_id)

    def test_confidence_base(self, detector):
        """Testa confianca base (sem parametros)."""
        result = self._detect(detector, "criar escala")
        assert result is not None
        assert result.confidence >= 0.7, "Confianca base deve ser >= 0.7"

    def test_confidence_with_params(self, detector):
        """Testa confianca aumenta com parametros."""
        # Sem parametros
        result_base = self._detect(detector, "criar escala")
        # Com parametros
        result_full = self._detect(detector, "criar escala posto POST-001 fevereiro 2026")
        assert result_full is not None
        assert result_base is not None
        assert result_full.confidence >= result_base.confidence, "Confianca com params deve ser >= base"

    def test_confidence_max_1(self, detector):
        """Testa que confianca nunca ultrapassa 1.0."""
        result = self._detect(detector, "criar escala posto POST-001 fevereiro 2026")
        assert result is not None
        assert result.confidence <= 1.0, "Confianca nao pode ultrapassar 1.0"

    def test_confidence_range(self, detector):
        """Testa que confianca esta entre 0 e 1."""
        result = self._detect(detector, "gerar relatorio")
        assert result is not None
        assert 0.0 <= result.confidence <= 1.0


class TestActionDetectorCategories:
    """Testes para mapeamento de categorias."""

    @pytest.fixture
    def detector(self):
        return ActionDetector()

    def _detect(self, detector, message, user_id="user-1", session_id="sess-1"):
        return detector.detect(message, user_id, session_id)

    @pytest.mark.parametrize(
        "message,expected_category",
        [
            ("criar escala", ActionCategory.OPERATIONAL),
            ("aprovar escala", ActionCategory.ADMINISTRATIVE),
            ("publicar escala", ActionCategory.ADMINISTRATIVE),
            ("alocar funcionario", ActionCategory.OPERATIONAL),
            ("encerrar alocacao", ActionCategory.OPERATIONAL),
            ("transferir funcionario", ActionCategory.OPERATIONAL),
            ("criar turno", ActionCategory.OPERATIONAL),
            ("registrar entrada", ActionCategory.OPERATIONAL),
            ("registrar saida", ActionCategory.OPERATIONAL),
            ("marcar falta", ActionCategory.OPERATIONAL),
            ("criar substituicao", ActionCategory.OPERATIONAL),
            ("enviar notificacao", ActionCategory.NOTIFICATION),
            ("gerar relatorio", ActionCategory.REPORT),
        ],
    )
    def test_category_mapping(self, detector, message, expected_category):
        """Testa mapeamento de categoria para cada tipo de acao."""
        result = self._detect(detector, message)
        assert result is not None, f"Nao detectou acao para: '{message}'"
        assert result.category == expected_category, (
            f"Categoria errada para '{message}': esperado {expected_category}, obtido {result.category}"
        )


class TestActionDetectorSchema:
    """Testes para o schema ActionRequest retornado."""

    @pytest.fixture
    def detector(self):
        return ActionDetector()

    def test_action_request_fields(self, detector):
        """Testa que ActionRequest tem todos os campos esperados."""
        result = detector.detect("criar escala", "user-1", "sess-1")
        assert result is not None
        assert isinstance(result, ActionRequest)
        assert result.action_type == ActionType.CREATE_SCALE
        assert result.category == ActionCategory.OPERATIONAL
        assert isinstance(result.parameters, dict)
        assert result.detected_from_message == "criar escala"
        assert 0.0 <= result.confidence <= 1.0
        assert result.user_id == "user-1"
        assert result.session_id == "sess-1"

    def test_action_request_preserves_original_message(self, detector):
        """Testa que a mensagem original e preservada."""
        msg = "Criar Escala Para Fevereiro 2026"
        result = detector.detect(msg, "u1", "s1")
        assert result is not None
        assert result.detected_from_message == msg

    def test_action_request_user_session(self, detector):
        """Testa que user_id e session_id sao propagados."""
        result = detector.detect("gerar relatorio", "user-42", "sess-xyz")
        assert result is not None
        assert result.user_id == "user-42"
        assert result.session_id == "sess-xyz"


class TestActionTypes:
    """Testes para os enums de tipos de acao."""

    def test_action_type_values(self):
        """Testa valores dos ActionType."""
        assert ActionType.CREATE_SCALE.value == "create_scale"
        assert ActionType.APPROVE_SCALE.value == "approve_scale"
        assert ActionType.PUBLISH_SCALE.value == "publish_scale"
        assert ActionType.ALLOCATE_EMPLOYEE.value == "allocate_employee"
        assert ActionType.TERMINATE_ALLOCATION.value == "terminate_allocation"
        assert ActionType.TRANSFER_EMPLOYEE.value == "transfer_employee"
        assert ActionType.CREATE_SHIFT.value == "create_shift"
        assert ActionType.REGISTER_CHECKIN.value == "register_checkin"
        assert ActionType.REGISTER_CHECKOUT.value == "register_checkout"
        assert ActionType.MARK_ABSENCE.value == "mark_absence"
        assert ActionType.CREATE_SUBSTITUTION.value == "create_substitution"
        assert ActionType.SEND_NOTIFICATION.value == "send_notification"
        assert ActionType.GENERATE_REPORT.value == "generate_report"

    def test_action_type_count(self):
        """Testa que existem 43 tipos de acao."""
        assert len(ActionType) == 55

    def test_action_category_values(self):
        """Testa valores das categorias."""
        assert ActionCategory.OPERATIONAL.value == "operational"
        assert ActionCategory.ADMINISTRATIVE.value == "administrative"
        assert ActionCategory.NOTIFICATION.value == "notification"
        assert ActionCategory.REPORT.value == "report"

    def test_action_type_is_str_enum(self):
        """Testa que ActionType e str Enum."""
        assert isinstance(ActionType.CREATE_SCALE, str)
        assert ActionType.CREATE_SCALE == "create_scale"
