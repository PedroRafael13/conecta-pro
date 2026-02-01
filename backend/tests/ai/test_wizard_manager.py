"""
Testes do WizardManager - Gerenciador de Wizards do Bartolo.

Testa especificamente:
- Bug #3: detect_wizard_type() distingue consulta vs criação
- Ciclo de vida do wizard (start, process_input, cancel)
- Session management
"""

import pytest

# Importação condicional para rodar tanto dentro quanto fora do container
try:
    from modules.ai.bartolo.wizards.base_wizard import WizardState
    from modules.ai.bartolo.wizards.wizard_manager import WIZARD_REGISTRY, WizardManager

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Módulo Bartolo não disponível")


class TestDetectWizardType:
    """Testes para detect_wizard_type() - Bug #3 fix."""

    def setup_method(self):
        self.manager = WizardManager()

    # =====================================================================
    # CONSULTAS - Deve retornar None (NÃO iniciar wizard)
    # =====================================================================

    def test_consulta_quais_funcionarios_turno_noite(self):
        """Bug #3: 'Quais funcionários estão no turno da noite' é consulta, não wizard."""
        result = self.manager.detect_wizard_type("Quais funcionários estão escalados para o turno da noite hoje?")
        assert result is None

    def test_consulta_verificar_escala(self):
        """'Verificar escala' é consulta, não criação de escala."""
        result = self.manager.detect_wizard_type("verificar escala de hoje")
        assert result is None

    def test_consulta_listar_rondas(self):
        """'Listar rondas' é consulta, não criação de ronda."""
        result = self.manager.detect_wizard_type("listar rondas de hoje")
        assert result is None

    def test_consulta_mostrar_postos(self):
        """'Mostrar postos' é consulta."""
        result = self.manager.detect_wizard_type("mostrar postos ativos")
        assert result is None

    def test_consulta_ver_comunicados(self):
        """'Ver comunicados' é consulta."""
        result = self.manager.detect_wizard_type("ver comunicados recentes")
        assert result is None

    def test_consulta_quantos_funcionarios(self):
        """'Quantos funcionários' é consulta."""
        result = self.manager.detect_wizard_type("quantos funcionários estão trabalhando?")
        assert result is None

    def test_consulta_tem_ocorrencia(self):
        """'Tem alguma ocorrência' é consulta."""
        result = self.manager.detect_wizard_type("tem alguma ocorrência aberta?")
        assert result is None

    def test_consulta_checar_escala(self):
        """'Checar escala' é consulta."""
        result = self.manager.detect_wizard_type("checar escala da semana")
        assert result is None

    def test_consulta_consultar_banco_horas(self):
        """'Consultar banco de horas' é consulta."""
        result = self.manager.detect_wizard_type("consultar banco de horas")
        assert result is None

    def test_consulta_buscar_funcionario(self):
        """'Buscar funcionário' é consulta."""
        result = self.manager.detect_wizard_type("buscar funcionário João")
        assert result is None

    # =====================================================================
    # CRIAÇÃO - Deve retornar o tipo correto de wizard
    # =====================================================================

    def test_criar_escala_retorna_wizard(self):
        """'Criar escala' deve iniciar wizard de escala."""
        result = self.manager.detect_wizard_type("criar escala para o próximo mês")
        assert result == "escala"

    def test_nova_escala_retorna_wizard(self):
        """'Nova escala' deve iniciar wizard de escala."""
        result = self.manager.detect_wizard_type("nova escala semanal")
        assert result == "escala"

    def test_montar_escala_retorna_wizard(self):
        """'Montar escala' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("montar escala de fevereiro")
        assert result == "escala"

    def test_criar_ronda_retorna_wizard(self):
        """'Criar ronda' deve iniciar wizard de ronda."""
        result = self.manager.detect_wizard_type("criar ronda de inspeção")
        assert result == "ronda"

    def test_nova_ronda_retorna_wizard(self):
        """'Nova ronda' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("nova ronda noturna")
        assert result == "ronda"

    def test_registrar_ocorrencia_retorna_wizard(self):
        """'Abrir ocorrência' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("abrir ocorrencia de invasão")
        assert result == "ocorrencia"

    def test_nova_ocorrencia_retorna_wizard(self):
        """'Nova ocorrência' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("nova ocorrencia")
        assert result == "ocorrencia"

    def test_criar_comunicado_retorna_wizard(self):
        """'Criar comunicado' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("criar comunicado para os funcionários")
        assert result == "comunicado"

    def test_novo_comunicado_retorna_wizard(self):
        """'Novo comunicado' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("novo comunicado urgente")
        assert result == "comunicado"

    def test_criar_posto_retorna_wizard(self):
        """'Criar posto' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("criar posto de segurança")
        assert result == "posto"

    def test_cadastrar_posto_retorna_wizard(self):
        """'Cadastrar posto' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("cadastrar posto novo")
        assert result == "posto"

    def test_contratar_funcionario_retorna_wizard(self):
        """'Contratar funcionário' deve iniciar wizard de admissão."""
        result = self.manager.detect_wizard_type("contratar novo funcionário")
        assert result == "admissao_funcionario"

    def test_criar_proposta_retorna_wizard(self):
        """'Criar proposta' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("criar proposta comercial")
        assert result == "proposta_comercial"

    def test_advertencia_retorna_wizard(self):
        """'Advertência' é ação disciplinar, deve iniciar wizard."""
        result = self.manager.detect_wizard_type("medida disciplinar para o funcionário")
        assert result == "disciplinar"

    def test_agendar_diarista_retorna_wizard(self):
        """'Agendar diarista' deve iniciar wizard."""
        result = self.manager.detect_wizard_type("agendar diarista para amanhã")
        assert result == "diarista"

    # =====================================================================
    # MATCH DIRETO - Deve retornar tipo correto
    # =====================================================================

    def test_match_direto_escala(self):
        """Match direto 'escala' está no WIZARD_REGISTRY."""
        result = self.manager.detect_wizard_type("escala")
        assert result == "escala"

    def test_match_direto_ocorrencia(self):
        """Match direto 'ocorrencia'."""
        result = self.manager.detect_wizard_type("ocorrencia")
        assert result == "ocorrencia"


class TestWizardLifecycle:
    """Testa ciclo de vida do wizard."""

    def setup_method(self):
        self.manager = WizardManager()

    def test_start_wizard_valido(self):
        """Inicia wizard com tipo válido."""
        response = self.manager.start_wizard("escala", user_id=1, session_id="test-session")
        assert response is not None
        assert response.state == WizardState.IN_PROGRESS or response.state == WizardState.WAITING_INPUT

    def test_start_wizard_invalido(self):
        """Wizard inexistente retorna erro."""
        response = self.manager.start_wizard("inexistente", user_id=1, session_id="test-session")
        assert response.state == WizardState.ERROR
        assert "nao encontrado" in response.message.lower()

    def test_has_active_wizard(self):
        """Verifica wizard ativo após start."""
        self.manager.start_wizard("escala", user_id=1, session_id="test-session")
        assert self.manager.has_active_wizard(1, "test-session") is True

    def test_no_active_wizard(self):
        """Sem wizard ativo retorna False."""
        assert self.manager.has_active_wizard(1, "test-session") is False

    def test_cancel_wizard(self):
        """Cancela wizard ativo."""
        self.manager.start_wizard("escala", user_id=1, session_id="test-session")
        response = self.manager.cancel_wizard(1, "test-session")
        assert response is not None
        assert self.manager.has_active_wizard(1, "test-session") is False

    def test_cancel_wizard_inexistente(self):
        """Cancelar wizard sem wizard ativo retorna None."""
        result = self.manager.cancel_wizard(1, "test-session")
        assert result is None

    def test_get_active_wizard(self):
        """Retorna wizard ativo."""
        self.manager.start_wizard("escala", user_id=1, session_id="test-session")
        wizard = self.manager.get_active_wizard(1, "test-session")
        assert wizard is not None

    def test_session_isolation(self):
        """Wizards são isolados por sessão."""
        self.manager.start_wizard("escala", user_id=1, session_id="session-1")
        assert self.manager.has_active_wizard(1, "session-1") is True
        assert self.manager.has_active_wizard(1, "session-2") is False
        assert self.manager.has_active_wizard(2, "session-1") is False


class TestGetAvailableWizards:
    """Testa listagem de wizards."""

    def setup_method(self):
        self.manager = WizardManager()

    def test_lista_wizards(self):
        """Retorna lista não-vazia de wizards."""
        wizards = self.manager.get_available_wizards()
        assert len(wizards) > 0

    def test_wizard_tem_campos_obrigatorios(self):
        """Cada wizard tem type, name, description."""
        wizards = self.manager.get_available_wizards()
        for w in wizards:
            assert "type" in w
            assert "name" in w
            assert "description" in w

    def test_wizard_sem_duplicatas(self):
        """Não há duplicatas na lista."""
        wizards = self.manager.get_available_wizards()
        types = [w["type"] for w in wizards]
        assert len(types) == len(set(types))
