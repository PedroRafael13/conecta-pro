"""
Testes automatizados para Wizards do Bartolo.

Testa:
- BaseWizard: fluxo de passos, validacao, navegacao, cancelamento
- WizardManager: registro, deteccao, sessoes, ciclo de vida
- PropostaComercialWizard: passos, calculo de custos, CCT
- AdmissaoWizard: passos, validacoes, alertas
"""

import pytest
import sys
sys.path.insert(0, '/app')

from modules.ai.bartolo.wizards.base_wizard import (
    BaseWizard, WizardStep, WizardData, WizardResponse,
    WizardState, StepType,
)
from modules.ai.bartolo.wizards.wizard_manager import WizardManager, WIZARD_REGISTRY
from modules.ai.bartolo.wizards.proposta_wizard import (
    PropostaComercialWizard, PostoTrabalho, CCT_PISOS_2026, ESCALAS, ENCARGOS_SOCIAIS,
)
from modules.ai.bartolo.wizards.admissao_wizard import AdmissaoWizard


# ==========================================================================
# WizardManager
# ==========================================================================

class TestWizardManager:
    """Testes para o WizardManager."""

    @pytest.fixture
    def manager(self):
        return WizardManager()

    def test_registry_has_wizards(self):
        """Testa que o registry tem wizards cadastrados."""
        assert "proposta_comercial" in WIZARD_REGISTRY
        assert "admissao_funcionario" in WIZARD_REGISTRY
        assert "admissao" in WIZARD_REGISTRY
        assert "contratar" in WIZARD_REGISTRY

    def test_get_available_wizards(self, manager):
        """Testa listagem de wizards disponiveis."""
        wizards = manager.get_available_wizards()
        assert len(wizards) >= 2
        types = [w["type"] for w in wizards]
        assert "proposta_comercial" in types
        assert "admissao_funcionario" in types

    @pytest.mark.parametrize("intent", [
        "proposta_comercial",
        "admissao_funcionario",
        "admissao",
        "contratar",
    ])
    def test_can_handle_wizard_direct_match(self, manager, intent):
        """Testa deteccao direta de wizard por nome."""
        assert manager.can_handle_wizard(intent) is True

    @pytest.mark.parametrize("intent", [
        "proposta",
        "orcamento",
        "orcar",
        "precificar",
        "custo",
        "admissao",
        "admitir",
        "contratar",
        "contratacao",
        "novo funcionario",
    ])
    def test_can_handle_wizard_keywords(self, manager, intent):
        """Testa deteccao de wizard por keywords."""
        assert manager.can_handle_wizard(intent) is True

    @pytest.mark.parametrize("intent", [
        "relatorio",
        "cobertura",
        "alerta",
        "bom dia",
    ])
    def test_cannot_handle_unknown_wizard(self, manager, intent):
        """Testa que intencoes irrelevantes nao ativam wizard."""
        assert manager.can_handle_wizard(intent) is False

    def test_detect_wizard_type_proposta(self, manager):
        """Testa deteccao do tipo proposta."""
        assert manager.detect_wizard_type("proposta_comercial") == "proposta_comercial"
        assert manager.detect_wizard_type("preciso de uma proposta") == "proposta_comercial"
        assert manager.detect_wizard_type("fazer orcamento") == "proposta_comercial"

    def test_detect_wizard_type_admissao(self, manager):
        """Testa deteccao do tipo admissao."""
        assert manager.detect_wizard_type("admissao_funcionario") == "admissao_funcionario"
        assert manager.detect_wizard_type("quero admitir um funcionario") == "admissao_funcionario"
        assert manager.detect_wizard_type("contratar novo funcionario") == "admissao_funcionario"

    def test_detect_wizard_type_none(self, manager):
        """Testa que intencao irrelevante retorna None."""
        assert manager.detect_wizard_type("bom dia") is None
        assert manager.detect_wizard_type("xyz_desconhecido") is None

    def test_detect_wizard_type_escala(self, manager):
        """Testa deteccao do tipo escala."""
        assert manager.detect_wizard_type("escala") == "escala"
        assert manager.detect_wizard_type("criar escala") == "escala"
        assert manager.detect_wizard_type("nova escala") == "escala"

    def test_detect_wizard_type_posto(self, manager):
        """Testa deteccao do tipo posto."""
        assert manager.detect_wizard_type("posto") == "posto"
        assert manager.detect_wizard_type("criar posto") == "posto"
        assert manager.detect_wizard_type("cadastrar posto") == "posto"

    def test_detect_wizard_type_diarista(self, manager):
        """Testa deteccao do tipo diarista."""
        assert manager.detect_wizard_type("diarista") == "diarista"
        assert manager.detect_wizard_type("agendar diarista") == "diarista"

    def test_detect_wizard_type_comunicado(self, manager):
        """Testa deteccao do tipo comunicado."""
        assert manager.detect_wizard_type("comunicado") == "comunicado"
        assert manager.detect_wizard_type("criar comunicado") == "comunicado"

    def test_session_key(self, manager):
        """Testa geracao de chave de sessao."""
        key = manager.get_session_key(1, "sess-abc")
        assert key == "1:sess-abc"

    def test_no_active_wizard_initially(self, manager):
        """Testa que nao ha wizard ativo no inicio."""
        assert manager.has_active_wizard(1, "sess-1") is False
        assert manager.get_active_wizard(1, "sess-1") is None

    def test_start_wizard_success(self, manager):
        """Testa inicio de wizard com sucesso."""
        response = manager.start_wizard("proposta_comercial", 1, "sess-1")
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps > 0
        assert manager.has_active_wizard(1, "sess-1") is True

    def test_start_wizard_invalid_type(self, manager):
        """Testa inicio de wizard com tipo invalido."""
        response = manager.start_wizard("inexistente", 1, "sess-1")
        assert response.state == WizardState.ERROR
        assert "nao encontrado" in response.message

    def test_start_wizard_with_initial_data(self, manager):
        """Testa inicio de wizard com dados iniciais."""
        initial = {"cliente": "Test Corp"}
        response = manager.start_wizard("proposta_comercial", 1, "sess-1", initial_data=initial)
        assert response.state == WizardState.WAITING_INPUT
        wizard = manager.get_active_wizard(1, "sess-1")
        assert wizard.data.collected_data.get("cliente") == "Test Corp"

    def test_process_input_active_wizard(self, manager):
        """Testa processamento de input em wizard ativo."""
        manager.start_wizard("proposta_comercial", 1, "sess-1")
        response = manager.process_input(1, "sess-1", "Cliente Teste")
        assert response is not None
        assert response.state in [WizardState.WAITING_INPUT, WizardState.COMPLETED]

    def test_process_input_no_wizard(self, manager):
        """Testa processamento sem wizard ativo."""
        response = manager.process_input(1, "sess-1", "texto qualquer")
        assert response is None

    def test_cancel_wizard(self, manager):
        """Testa cancelamento de wizard."""
        manager.start_wizard("proposta_comercial", 1, "sess-1")
        assert manager.has_active_wizard(1, "sess-1") is True
        response = manager.cancel_wizard(1, "sess-1")
        assert response is not None
        assert response.state == WizardState.CANCELLED

    def test_cancel_wizard_no_active(self, manager):
        """Testa cancelamento sem wizard ativo."""
        response = manager.cancel_wizard(1, "sess-1")
        assert response is None

    def test_get_wizard_status(self, manager):
        """Testa status do wizard."""
        manager.start_wizard("proposta_comercial", 1, "sess-1")
        status = manager.get_wizard_status(1, "sess-1")
        assert status is not None
        assert status["wizard_type"] == "proposta_comercial"
        assert status["state"] == WizardState.IN_PROGRESS.value
        assert status["current_step"] == 0
        assert status["total_steps"] > 0

    def test_get_wizard_status_none(self, manager):
        """Testa status sem wizard."""
        status = manager.get_wizard_status(1, "sess-1")
        assert status is None

    def test_get_wizard_help(self, manager):
        """Testa ajuda de wizard."""
        help_text = manager.get_wizard_help("proposta_comercial")
        assert "Proposta Comercial" in help_text

    def test_get_wizard_help_not_found(self, manager):
        """Testa ajuda de wizard inexistente."""
        help_text = manager.get_wizard_help("inexistente")
        assert "nao encontrado" in help_text


# ==========================================================================
# PropostaComercialWizard
# ==========================================================================

class TestPropostaComercialWizard:
    """Testes para PropostaComercialWizard."""

    @pytest.fixture
    def wizard(self):
        return PropostaComercialWizard(user_id=1, session_id="sess-test")

    def test_wizard_type(self, wizard):
        """Testa tipo do wizard."""
        assert wizard.get_wizard_type() == "proposta_comercial"

    def test_wizard_name(self, wizard):
        """Testa nome do wizard."""
        assert wizard.get_wizard_name() == "Proposta Comercial"

    def test_wizard_description(self, wizard):
        """Testa descricao do wizard."""
        desc = wizard.get_wizard_description()
        assert "proposta comercial" in desc.lower()

    def test_steps_defined(self, wizard):
        """Testa que os passos estao definidos."""
        assert len(wizard.steps) == 9
        step_ids = [s.id for s in wizard.steps]
        assert "cliente" in step_ids
        assert "tipo_servico" in step_ids
        assert "cargo" in step_ids
        assert "quantidade" in step_ids
        assert "escala" in step_ids
        assert "periculosidade" in step_ids
        assert "mais_postos" in step_ids
        assert "custos_operacionais" in step_ids
        assert "margem_lucro" in step_ids

    def test_start_wizard(self, wizard):
        """Testa inicio do wizard."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 9
        assert response.question is not None

    def test_cct_pisos_loaded(self):
        """Testa que pisos da CCT estao carregados."""
        assert "Porteiro" in CCT_PISOS_2026
        assert "Vigilante" in CCT_PISOS_2026
        assert "Faxineiro" in CCT_PISOS_2026
        assert CCT_PISOS_2026["Porteiro"] == 1847.12

    def test_escalas_loaded(self):
        """Testa que tipos de escala estao carregados."""
        assert "12x36 Diurno" in ESCALAS
        assert "12x36 Noturno" in ESCALAS
        assert "5x2 (44h)" in ESCALAS
        assert ESCALAS["12x36 Noturno"]["adicional_noturno"] is True

    def test_encargos_sociais(self):
        """Testa valor dos encargos sociais."""
        assert ENCARGOS_SOCIAIS == 0.72

    def test_posto_trabalho_salario_base(self):
        """Testa calculo de salario base sem adicionais."""
        posto = PostoTrabalho(
            cargo="Porteiro",
            quantidade=1,
            escala="12x36 Diurno",
            salario_base=1847.12,
        )
        assert posto.salario_total == 1847.12

    def test_posto_trabalho_com_periculosidade(self):
        """Testa calculo com adicional de periculosidade."""
        posto = PostoTrabalho(
            cargo="Vigilante",
            quantidade=1,
            escala="12x36 Diurno",
            salario_base=2456.78,
            adicional_periculosidade=True,
        )
        expected = 2456.78 * 1.30
        assert abs(posto.salario_total - expected) < 0.01

    def test_posto_trabalho_com_noturno(self):
        """Testa calculo com adicional noturno."""
        posto = PostoTrabalho(
            cargo="Porteiro",
            quantidade=1,
            escala="12x36 Noturno",
            salario_base=1847.12,
            adicional_noturno=True,
        )
        expected = 1847.12 * 1.20
        assert abs(posto.salario_total - expected) < 0.01

    def test_posto_trabalho_custo_mensal_unitario(self):
        """Testa calculo de custo mensal unitario."""
        posto = PostoTrabalho(
            cargo="Porteiro",
            quantidade=1,
            escala="12x36 Diurno",
            salario_base=1847.12,
        )
        expected = 1847.12 * (1 + ENCARGOS_SOCIAIS)
        assert abs(posto.custo_mensal_unitario - expected) < 0.01

    def test_posto_trabalho_custo_mensal_total(self):
        """Testa calculo de custo mensal total com quantidade."""
        posto = PostoTrabalho(
            cargo="Porteiro",
            quantidade=3,
            escala="12x36 Diurno",
            salario_base=1847.12,
        )
        expected = 1847.12 * (1 + ENCARGOS_SOCIAIS) * 3
        assert abs(posto.custo_mensal_total - expected) < 0.01

    @pytest.mark.asyncio
    async def test_process_result(self, wizard):
        """Testa processamento do resultado final."""
        # Simula postos
        wizard.postos = [
            PostoTrabalho(
                cargo="Porteiro",
                quantidade=2,
                escala="12x36 Diurno",
                salario_base=1847.12,
            )
        ]
        data = {
            "cliente": "Condominio Teste",
            "tipo_servico": "Portaria e Controle de Acesso",
            "custos_operacionais": 500.0,
            "margem_lucro": "15%",
        }
        result = await wizard.process_result(data)
        assert result["cliente"] == "Condominio Teste"
        assert result["tipo_servico"] == "Portaria e Controle de Acesso"
        assert result["resumo"]["total_funcionarios"] == 2
        assert result["resumo"]["custo_mao_obra"] > 0
        assert result["resumo"]["custos_operacionais"] == 500.0
        assert result["resumo"]["margem_lucro"] == 0.15
        assert result["resumo"]["valor_proposta"] > 0
        assert len(result["observacoes"]) > 0


# ==========================================================================
# AdmissaoWizard
# ==========================================================================

class TestAdmissaoWizard:
    """Testes para AdmissaoWizard."""

    @pytest.fixture
    def wizard(self):
        return AdmissaoWizard(user_id=1, session_id="sess-test")

    def test_wizard_type(self, wizard):
        """Testa tipo do wizard."""
        assert wizard.get_wizard_type() == "admissao_funcionario"

    def test_wizard_name(self, wizard):
        """Testa nome do wizard."""
        assert wizard.get_wizard_name() == "Admissao de Funcionario"

    def test_wizard_description(self, wizard):
        """Testa descricao do wizard."""
        desc = wizard.get_wizard_description()
        assert "admitir" in desc.lower()

    def test_steps_defined(self, wizard):
        """Testa que os passos estao definidos."""
        assert len(wizard.steps) == 11
        step_ids = [s.id for s in wizard.steps]
        assert "nome_completo" in step_ids
        assert "cpf" in step_ids
        assert "data_nascimento" in step_ids
        assert "cargo" in step_ids
        assert "salario" in step_ids
        assert "data_admissao" in step_ids
        assert "tipo_contrato" in step_ids
        assert "escala" in step_ids
        assert "posto_trabalho" in step_ids
        assert "documentos_ok" in step_ids
        assert "exame_admissional" in step_ids

    def test_start_wizard(self, wizard):
        """Testa inicio do wizard."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 11

    @pytest.mark.asyncio
    async def test_process_result(self, wizard):
        """Testa processamento do resultado."""
        data = {
            "nome_completo": "Joao Silva",
            "cpf": "12345678901",
            "data_nascimento": "15/05/1990",
            "cargo": "Porteiro",
            "salario": 1900.0,
            "data_admissao": "01/02/2026",
            "tipo_contrato": "CLT Prazo Indeterminado",
            "escala": "12x36 Diurno",
            "posto_trabalho": "Centro-001",
            "documentos_ok": True,
            "exame_admissional": True,
        }
        result = await wizard.process_result(data)
        assert result["funcionario"]["nome"] == "Joao Silva"
        assert result["funcionario"]["cargo"] == "Porteiro"
        assert len(result["proximos_passos"]) > 0

    @pytest.mark.asyncio
    async def test_process_result_alerts_docs_pending(self, wizard):
        """Testa alertas quando documentos pendentes."""
        data = {
            "nome_completo": "Joao Silva",
            "documentos_ok": False,
            "exame_admissional": True,
            "cargo": "Porteiro",
            "salario": 1900.0,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("Documentos pendentes" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_alerts_exame_pending(self, wizard):
        """Testa alertas quando exame admissional pendente."""
        data = {
            "nome_completo": "Joao Silva",
            "documentos_ok": True,
            "exame_admissional": False,
            "cargo": "Porteiro",
            "salario": 1900.0,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("Exame admissional" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_alerts_salario_abaixo_piso(self, wizard):
        """Testa alerta de salario abaixo do piso."""
        data = {
            "nome_completo": "Joao Silva",
            "documentos_ok": True,
            "exame_admissional": True,
            "cargo": "Porteiro",
            "salario": 1500.0,  # Abaixo do piso de Porteiro (1847.12)
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("piso" in a["mensagem"].lower() for a in alerts)


# ==========================================================================
# Fluxo de Navegacao do BaseWizard
# ==========================================================================

class TestWizardNavigation:
    """Testes para navegacao entre passos."""

    @pytest.fixture
    def wizard(self):
        """Usa AdmissaoWizard por ter passos mais simples."""
        return AdmissaoWizard(user_id=1, session_id="sess-nav")

    def test_advance_step(self, wizard):
        """Testa avanco de passo."""
        wizard.start()
        # Passo 1: nome_completo
        response = wizard.process_input("Joao da Silva Santos")
        assert response.step_number == 2  # Avancou
        assert response.state == WizardState.WAITING_INPUT

    def test_go_back(self, wizard):
        """Testa voltar ao passo anterior."""
        wizard.start()
        # Avanca
        wizard.process_input("Joao da Silva Santos")
        # Volta
        response = wizard.go_back()
        assert response.step_number == 1  # Voltou

    def test_go_back_first_step(self, wizard):
        """Testa voltar no primeiro passo."""
        wizard.start()
        response = wizard.go_back()
        assert "primeiro passo" in response.message.lower()

    def test_cancel_via_input(self, wizard):
        """Testa cancelamento via mensagem."""
        wizard.start()
        response = wizard.process_input("cancelar")
        assert response.state == WizardState.CANCELLED

    @pytest.mark.parametrize("cancel_word", ["cancelar", "sair", "parar"])
    def test_cancel_words(self, cancel_word):
        """Testa palavras de cancelamento."""
        wiz = AdmissaoWizard(user_id=1, session_id="sess-c")
        wiz.start()
        response = wiz.process_input(cancel_word)
        assert response.state == WizardState.CANCELLED

    @pytest.mark.parametrize("back_word", ["voltar", "anterior"])
    def test_back_words(self, back_word):
        """Testa palavras de voltar."""
        wiz = AdmissaoWizard(user_id=1, session_id="sess-b")
        wiz.start()
        wiz.process_input("Joao Silva Santos")  # avanca
        response = wiz.process_input(back_word)
        assert response.step_number == 1  # Voltou

    def test_process_completed_wizard(self, wizard):
        """Testa processar input em wizard ja completado."""
        wizard.data.state = WizardState.COMPLETED
        response = wizard.process_input("qualquer coisa")
        assert response.state == WizardState.COMPLETED
        assert "concluido" in response.message.lower()

    def test_process_cancelled_wizard(self, wizard):
        """Testa processar input em wizard cancelado."""
        wizard.data.state = WizardState.CANCELLED
        response = wizard.process_input("qualquer coisa")
        assert response.state == WizardState.CANCELLED
        assert "cancelado" in response.message.lower()

    def test_can_go_back_false_on_first_step(self, wizard):
        """Testa can_go_back false no primeiro passo."""
        response = wizard.start()
        assert response.can_go_back is False

    def test_can_go_back_true_on_second_step(self, wizard):
        """Testa can_go_back true no segundo passo."""
        wizard.start()
        response = wizard.process_input("Joao da Silva Santos")
        assert response.can_go_back is True

    def test_progress_percent(self, wizard):
        """Testa calculo de progresso."""
        response = wizard.start()
        # Primeiro passo de 11 = 0%
        assert response.progress_percent == 0.0

        # Avanca um passo
        response2 = wizard.process_input("Joao da Silva Santos")
        assert response2.progress_percent > 0.0


# ==========================================================================
# Validacao de Input
# ==========================================================================

class TestWizardValidation:
    """Testes para validacao de input."""

    @pytest.fixture
    def wizard(self):
        return AdmissaoWizard(user_id=1, session_id="sess-val")

    def test_validation_required_field_empty(self, wizard):
        """Testa validacao de campo obrigatorio vazio."""
        wizard.start()
        response = wizard.process_input("")
        # Deve retornar erro de validacao sem avancar
        assert response.validation_error is not None
        assert response.step_number == 1  # Nao avancou

    def test_validation_min_length(self, wizard):
        """Testa validacao de tamanho minimo."""
        wizard.start()
        # nome_completo tem min_length=5
        response = wizard.process_input("Ab")
        assert response.validation_error is not None

    def test_validation_number_input_invalid(self, wizard):
        """Testa validacao de campo numerico com texto."""
        wizard.start()
        # Avanca ate o campo salario (passo 5)
        wizard.process_input("Joao da Silva Santos")     # nome
        wizard.process_input("12345678901")               # cpf
        wizard.process_input("15/05/1990")                # data nasc
        wizard.process_input("1")                         # cargo (Porteiro)
        # Agora no campo salario - tenta texto invalido
        response = wizard.process_input("abc")
        assert response.validation_error is not None

    def test_set_initial_data(self, wizard):
        """Testa definicao de dados iniciais."""
        wizard.set_initial_data({"nome_completo": "Pre-definido"})
        assert wizard.data.collected_data["nome_completo"] == "Pre-definido"

    def test_get_state(self, wizard):
        """Testa retorno do estado."""
        state = wizard.get_state()
        assert isinstance(state, WizardData)
        assert state.wizard_type == "admissao_funcionario"
        assert state.state == WizardState.NOT_STARTED
