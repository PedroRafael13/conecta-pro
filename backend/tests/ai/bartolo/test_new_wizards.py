"""
Testes automatizados para os novos Wizards do Bartolo.

Testa:
- EscalaWizard: criacao de escala mensal, tipos, turnos, parse mes/ano
- PostoWizard: cadastro de posto, armamento condicional, next steps
- DiaristaWizard: agendamento diarista, calculo descontos, validacoes valor
- ComunicadoWizard: comunicado, destinatarios condicionais, prioridade, agendamento

Total: ~60+ testes cobrindo fluxo, validacoes, skip conditions e process_result.
"""

import sys

import pytest

sys.path.insert(0, "/app")

from modules.ai.bartolo.wizards.base_wizard import StepType, WizardState
from modules.ai.bartolo.wizards.comunicado_wizard import ComunicadoWizard
from modules.ai.bartolo.wizards.diarista_wizard import DiaristaWizard
from modules.ai.bartolo.wizards.escala_wizard import EscalaWizard
from modules.ai.bartolo.wizards.posto_wizard import PostoWizard

# ==========================================================================
# EscalaWizard
# ==========================================================================


class TestEscalaWizard:
    """Testes para EscalaWizard."""

    @pytest.fixture
    def wizard(self):
        return EscalaWizard(user_id=1, session_id="sess-escala")

    def test_wizard_type(self, wizard):
        """Testa que o tipo do wizard e 'escala'."""
        assert wizard.get_wizard_type() == "escala"

    def test_wizard_name(self, wizard):
        """Testa que o nome do wizard e 'Criacao de Escala'."""
        assert wizard.get_wizard_name() == "Criacao de Escala"

    def test_wizard_description(self, wizard):
        """Testa que a descricao menciona escala."""
        desc = wizard.get_wizard_description()
        assert "escala" in desc.lower()

    def test_steps_count(self, wizard):
        """Testa que o wizard tem exatamente 8 passos."""
        assert len(wizard.steps) == 8

    def test_step_ids(self, wizard):
        """Testa que todos os step IDs esperados estao presentes."""
        step_ids = [s.id for s in wizard.steps]
        expected = [
            "posto",
            "mes_ano",
            "tipo_escala",
            "turno",
            "horario_personalizado",
            "funcionarios",
            "observacoes",
            "confirmacao",
        ]
        assert step_ids == expected

    def test_start_returns_waiting_input(self, wizard):
        """Testa que start() retorna estado WAITING_INPUT."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 8
        assert response.question is not None

    def test_tipo_escala_step_has_correct_options(self, wizard):
        """Testa que o passo tipo_escala tem as opcoes corretas."""
        tipo_step = next(s for s in wizard.steps if s.id == "tipo_escala")
        assert tipo_step.step_type == StepType.CHOICE
        options_text = " ".join(tipo_step.options)
        assert "12x36" in options_text
        assert "6x1" in options_text
        assert "5x2" in options_text
        assert "5x1" in options_text
        assert "24x72" in options_text
        assert "Personalizada" in options_text
        assert len(tipo_step.options) == 6

    def test_turno_step_has_correct_options(self, wizard):
        """Testa que o passo turno tem as opcoes corretas."""
        turno_step = next(s for s in wizard.steps if s.id == "turno")
        assert turno_step.step_type == StepType.CHOICE
        options_text = " ".join(turno_step.options)
        assert "Diurno" in options_text
        assert "Noturno" in options_text
        assert "Matutino" in options_text
        assert "Vespertino" in options_text
        assert "Madrugada" in options_text
        assert "Comercial" in options_text
        assert "Personalizado" in options_text
        assert len(turno_step.options) == 7

    def test_horario_personalizado_skip_condition_when_not_personalizado(self, wizard):
        """Testa que horario_personalizado e pulado quando turno != Personalizado."""
        horario_step = next(s for s in wizard.steps if s.id == "horario_personalizado")
        assert horario_step.skip_condition is not None
        # Turno Diurno -> deve pular
        assert horario_step.skip_condition({"turno": "Diurno (06:00 - 18:00)"}) is True

    def test_horario_personalizado_not_skipped_when_personalizado(self, wizard):
        """Testa que horario_personalizado NAO e pulado quando turno == Personalizado."""
        horario_step = next(s for s in wizard.steps if s.id == "horario_personalizado")
        assert horario_step.skip_condition({"turno": "Personalizado"}) is False

    def test_process_input_through_first_two_steps(self, wizard):
        """Testa avanco pelos dois primeiros passos (posto e mes_ano)."""
        wizard.start()
        # Passo 1: posto
        response = wizard.process_input("Portaria Principal")
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 2
        assert wizard.data.collected_data["posto"] == "Portaria Principal"

        # Passo 2: mes_ano
        response = wizard.process_input("02/2026")
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 3
        assert wizard.data.collected_data["mes_ano"] == "02/2026"

    def test_parse_mes_ano_numeric(self, wizard):
        """Testa parse de mes/ano no formato MM/AAAA."""
        mes, ano = wizard._parse_mes_ano("02/2026")
        assert mes == 2
        assert ano == 2026

    def test_parse_mes_ano_text(self, wizard):
        """Testa parse de mes/ano no formato textual."""
        mes, ano = wizard._parse_mes_ano("fevereiro 2026")
        assert mes == 2
        assert ano == 2026

    def test_parse_mes_ano_marco_sem_acento(self, wizard):
        """Testa parse de marco sem acento."""
        mes, ano = wizard._parse_mes_ano("marco 2026")
        assert mes == 3
        assert ano == 2026

    def test_parse_mes_ano_fallback(self, wizard):
        """Testa fallback quando formato nao e reconhecido."""
        from datetime import date

        mes, ano = wizard._parse_mes_ano("invalido")
        assert mes == date.today().month
        assert ano == date.today().year

    @pytest.mark.asyncio
    async def test_process_result_structure(self, wizard):
        """Testa que process_result retorna a estrutura correta."""
        data = {
            "posto": "Portaria Principal",
            "mes_ano": "02/2026",
            "tipo_escala": "12x36 (12h trabalho, 36h descanso)",
            "turno": "Diurno (06:00 - 18:00)",
            "funcionarios": "todos",
            "observacoes": "nao",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert "escala" in result
        assert "proximos_passos" in result
        assert "alertas" in result
        assert result["escala"]["posto"] == "Portaria Principal"
        assert result["escala"]["mes"] == 2
        assert result["escala"]["ano"] == 2026
        assert result["escala"]["tipo_escala"] == "12x36"
        assert result["escala"]["turno"]["nome"] == "diurno"
        assert result["escala"]["turno"]["inicio"] == "06:00"
        assert result["escala"]["turno"]["fim"] == "18:00"
        assert result["escala"]["funcionarios"] == {"tipo": "todos"}
        assert result["escala"]["observacoes"] is None

    @pytest.mark.asyncio
    async def test_process_result_12x36_alert(self, wizard):
        """Testa que 12x36 gera alerta CLT."""
        data = {
            "posto": "Posto A",
            "mes_ano": "03/2026",
            "tipo_escala": "12x36 (12h trabalho, 36h descanso)",
            "turno": "Diurno (06:00 - 18:00)",
            "funcionarios": "todos",
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("CLT" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_noturno_alert(self, wizard):
        """Testa que turno noturno gera alerta de adicional."""
        data = {
            "posto": "Posto B",
            "mes_ano": "03/2026",
            "tipo_escala": "5x2 (segunda a sexta)",
            "turno": "Noturno (18:00 - 06:00)",
            "funcionarios": "todos",
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("noturno" in a["mensagem"].lower() for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_personalizado_turno(self, wizard):
        """Testa processamento com turno personalizado."""
        data = {
            "posto": "Posto C",
            "mes_ano": "04/2026",
            "tipo_escala": "Personalizada",
            "turno": "Personalizado",
            "horario_personalizado": "07:00 - 19:00",
            "funcionarios": "Joao, Maria, Pedro",
        }
        result = await wizard.process_result(data)
        assert result["escala"]["turno"]["nome"] == "personalizado"
        assert result["escala"]["turno"]["inicio"] == "07:00"
        assert result["escala"]["turno"]["fim"] == "19:00"
        assert result["escala"]["funcionarios"]["tipo"] == "lista"
        assert len(result["escala"]["funcionarios"]["ids"]) == 3

    @pytest.mark.asyncio
    async def test_process_result_funcionarios_disponiveis(self, wizard):
        """Testa parse de funcionarios 'disponiveis'."""
        data = {
            "posto": "Posto D",
            "mes_ano": "05/2026",
            "tipo_escala": "6x1 (6 dias trabalho, 1 folga)",
            "turno": "Comercial (08:00 - 17:00)",
            "funcionarios": "disponiveis",
        }
        result = await wizard.process_result(data)
        assert result["escala"]["funcionarios"]["tipo"] == "disponiveis"

    def test_confirmacao_step_is_last(self, wizard):
        """Testa que confirmacao e o ultimo passo."""
        assert wizard.steps[-1].id == "confirmacao"
        assert wizard.steps[-1].step_type == StepType.CONFIRMATION

    def test_posto_step_validation_rules(self, wizard):
        """Testa regras de validacao do passo posto."""
        posto_step = wizard.steps[0]
        assert posto_step.validation_rules.get("min_length") == 2
        assert posto_step.validation_rules.get("max_length") == 200


# ==========================================================================
# PostoWizard
# ==========================================================================


class TestPostoWizard:
    """Testes para PostoWizard."""

    @pytest.fixture
    def wizard(self):
        return PostoWizard(user_id=1, session_id="sess-posto")

    def test_wizard_type(self, wizard):
        """Testa que o tipo do wizard e 'posto'."""
        assert wizard.get_wizard_type() == "posto"

    def test_wizard_name(self, wizard):
        """Testa que o nome do wizard e correto."""
        assert wizard.get_wizard_name() == "Criacao de Posto de Trabalho"

    def test_wizard_description(self, wizard):
        """Testa que a descricao menciona posto."""
        desc = wizard.get_wizard_description()
        assert "posto" in desc.lower()

    def test_steps_count(self, wizard):
        """Testa que o wizard tem exatamente 10 passos."""
        assert len(wizard.steps) == 10

    def test_step_ids(self, wizard):
        """Testa que todos os step IDs esperados estao presentes."""
        step_ids = [s.id for s in wizard.steps]
        expected = [
            "nome",
            "tipo",
            "endereco",
            "cliente",
            "turno",
            "efetivo_minimo",
            "requisitos",
            "armamento",
            "observacoes",
            "confirmacao",
        ]
        assert step_ids == expected

    def test_start_returns_waiting_input(self, wizard):
        """Testa que start() retorna WAITING_INPUT."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 10

    def test_tipo_step_has_options(self, wizard):
        """Testa que o passo tipo tem as opcoes corretas."""
        tipo_step = next(s for s in wizard.steps if s.id == "tipo")
        assert tipo_step.step_type == StepType.CHOICE
        option_names = tipo_step.options
        assert "Portaria" in option_names
        assert "Guarita" in option_names
        assert "Recepcao" in option_names
        assert "Ronda Motorizada" in option_names
        assert "Ronda a Pe" in option_names
        assert "CFTV (Monitoramento)" in option_names
        assert "Limpeza" in option_names
        assert "Manutencao" in option_names
        assert "Administrativo" in option_names
        assert "Outro" in option_names
        assert len(option_names) == 10

    def test_armamento_skip_condition_when_not_armada(self, wizard):
        """Testa que armamento e pulado quando Vigilancia Armada nao esta nos requisitos."""
        armamento_step = next(s for s in wizard.steps if s.id == "armamento")
        assert armamento_step.skip_condition is not None
        # Sem Vigilancia Armada -> deve pular
        assert armamento_step.skip_condition({"requisitos": "Curso de Reciclagem em dia"}) is True
        assert armamento_step.skip_condition({"requisitos": None}) is True
        assert armamento_step.skip_condition({}) is True

    def test_armamento_not_skipped_when_armada(self, wizard):
        """Testa que armamento NAO e pulado quando Vigilancia Armada esta nos requisitos."""
        armamento_step = next(s for s in wizard.steps if s.id == "armamento")
        assert armamento_step.skip_condition({"requisitos": "Vigilancia Armada, CNH (veiculo)"}) is False

    def test_efetivo_minimo_step_type(self, wizard):
        """Testa que efetivo_minimo e NUMBER_INPUT."""
        efetivo_step = next(s for s in wizard.steps if s.id == "efetivo_minimo")
        assert efetivo_step.step_type == StepType.NUMBER_INPUT
        assert efetivo_step.validation_rules.get("min_value") == 1
        assert efetivo_step.validation_rules.get("max_value") == 50

    def test_requisitos_step_is_multi_choice(self, wizard):
        """Testa que requisitos e MULTI_CHOICE."""
        req_step = next(s for s in wizard.steps if s.id == "requisitos")
        assert req_step.step_type == StepType.MULTI_CHOICE
        assert "Vigilancia Armada" in req_step.options
        assert "CNH (veiculo)" in req_step.options
        assert len(req_step.options) == 9

    def test_armamento_step_options(self, wizard):
        """Testa opcoes de armamento."""
        arm_step = next(s for s in wizard.steps if s.id == "armamento")
        assert "Revolver .38" in arm_step.options
        assert "Pistola .380" in arm_step.options
        assert "Espingarda calibre 12" in arm_step.options
        assert "Desarmado (apenas colete)" in arm_step.options
        assert "Nao se aplica" in arm_step.options

    @pytest.mark.asyncio
    async def test_process_result_structure(self, wizard):
        """Testa que process_result retorna a estrutura correta."""
        data = {
            "nome": "Portaria Principal",
            "tipo": "Portaria",
            "endereco": "Rua das Flores, 100 - Centro",
            "cliente": "Condominio Flores",
            "turno": "24 horas (diurno + noturno)",
            "efetivo_minimo": 2,
            "requisitos": "Curso de Reciclagem em dia",
            "observacoes": "nao",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert "posto" in result
        assert "proximos_passos" in result
        assert "alertas" in result
        assert result["posto"]["nome"] == "Portaria Principal"
        assert result["posto"]["tipo"] == "portaria"
        assert result["posto"]["turno"] == "24h"
        assert result["posto"]["efetivo_minimo"] == 2
        assert result["posto"]["status"] == "ativo"
        assert result["posto"]["observacoes"] is None

    @pytest.mark.asyncio
    async def test_process_result_armado(self, wizard):
        """Testa processamento com posto armado."""
        data = {
            "nome": "Guarita Norte",
            "tipo": "Guarita",
            "endereco": "Av. Norte, 500",
            "cliente": "Cond. Norte",
            "turno": "Noturno (18:00 - 06:00)",
            "efetivo_minimo": 1,
            "requisitos": "Vigilancia Armada, Curso de Reciclagem em dia",
            "armamento": "Revolver .38",
            "observacoes": "nao",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert result["posto"]["armado"] is True
        assert result["posto"]["armamento"] == "revolver_38"
        # Alertas de posto armado
        alerts = result["alertas"]
        assert any("armado" in a["mensagem"].lower() or "CNV" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_portaria_alert(self, wizard):
        """Testa que tipo portaria gera alerta de controle de acesso."""
        data = {
            "nome": "Portaria Sul",
            "tipo": "Portaria",
            "endereco": "Rua Sul, 200",
            "cliente": "Cond. Sul",
            "turno": "Comercial (08:00 - 17:00)",
            "efetivo_minimo": 1,
            "requisitos": "Nenhum requisito especial",
            "observacoes": "nao",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("controle de acesso" in a["mensagem"].lower() for a in alerts)

    def test_generate_next_steps_armado_true(self, wizard):
        """Testa que _generate_next_steps inclui passos extras quando armado."""
        steps = wizard._generate_next_steps("guarita", armado=True)
        steps_text = " ".join(steps)
        assert "armamento" in steps_text.lower()
        assert "Cadastrar posto no sistema" in steps
        assert "Verificar documentacao de armamento (RA, CLCB)" in steps

    def test_generate_next_steps_armado_false(self, wizard):
        """Testa que _generate_next_steps nao inclui armamento quando desarmado."""
        steps = wizard._generate_next_steps("portaria", armado=False)
        steps_text = " ".join(steps)
        assert "documentacao de armamento" not in steps_text.lower()
        assert "Cadastrar posto no sistema" in steps

    def test_generate_next_steps_cftv(self, wizard):
        """Testa next steps para CFTV."""
        steps = wizard._generate_next_steps("cftv", armado=False)
        assert any("CFTV" in s for s in steps)

    def test_generate_next_steps_ronda_motorizada(self, wizard):
        """Testa next steps para ronda motorizada."""
        steps = wizard._generate_next_steps("ronda_motorizada", armado=False)
        assert any("veiculo" in s.lower() or "rota" in s.lower() for s in steps)

    @pytest.mark.asyncio
    async def test_process_result_efetivo_alto_alert(self, wizard):
        """Testa alerta quando efetivo >= 5."""
        data = {
            "nome": "Central CFTV",
            "tipo": "CFTV (Monitoramento)",
            "endereco": "Bloco Central",
            "cliente": "Cond. Central",
            "turno": "24 horas (diurno + noturno)",
            "efetivo_minimo": 6,
            "requisitos": "Treinamento CFTV",
            "observacoes": "nao",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("reservas tecnicas" in a["mensagem"].lower() for a in alerts)

    def test_confirmacao_step_is_last(self, wizard):
        """Testa que confirmacao e o ultimo passo."""
        assert wizard.steps[-1].id == "confirmacao"
        assert wizard.steps[-1].step_type == StepType.CONFIRMATION


# ==========================================================================
# DiaristaWizard
# ==========================================================================


class TestDiaristaWizard:
    """Testes para DiaristaWizard."""

    @pytest.fixture
    def wizard(self):
        return DiaristaWizard(user_id=1, session_id="sess-diarista")

    def test_wizard_type(self, wizard):
        """Testa que o tipo do wizard e 'diarista'."""
        assert wizard.get_wizard_type() == "diarista"

    def test_wizard_name(self, wizard):
        """Testa que o nome do wizard e correto."""
        assert wizard.get_wizard_name() == "Agendamento de Diarista"

    def test_wizard_description(self, wizard):
        """Testa que a descricao menciona diarista."""
        desc = wizard.get_wizard_description()
        assert "diarista" in desc.lower()

    def test_steps_count(self, wizard):
        """Testa que o wizard tem exatamente 9 passos."""
        assert len(wizard.steps) == 9

    def test_step_ids(self, wizard):
        """Testa que todos os step IDs esperados estao presentes."""
        step_ids = [s.id for s in wizard.steps]
        expected = [
            "diarista",
            "data",
            "horario",
            "horario_personalizado",
            "local",
            "tipo_servico",
            "valor",
            "observacoes",
            "confirmacao",
        ]
        assert step_ids == expected

    def test_start_returns_waiting_input(self, wizard):
        """Testa que start() retorna WAITING_INPUT."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 9

    def test_horario_step_options(self, wizard):
        """Testa opcoes do passo horario."""
        horario_step = next(s for s in wizard.steps if s.id == "horario")
        assert horario_step.step_type == StepType.CHOICE
        assert "Integral (08:00 - 17:00)" in horario_step.options
        assert "Meio periodo manha (08:00 - 12:00)" in horario_step.options
        assert "Meio periodo tarde (13:00 - 17:00)" in horario_step.options
        assert "Noturno (18:00 - 06:00)" in horario_step.options
        assert "Personalizado" in horario_step.options
        assert len(horario_step.options) == 5

    def test_horario_personalizado_skip_condition_when_not_personalizado(self, wizard):
        """Testa que horario_personalizado e pulado quando horario != Personalizado."""
        h_step = next(s for s in wizard.steps if s.id == "horario_personalizado")
        assert h_step.skip_condition is not None
        assert h_step.skip_condition({"horario": "Integral (08:00 - 17:00)"}) is True

    def test_horario_personalizado_not_skipped_when_personalizado(self, wizard):
        """Testa que horario_personalizado NAO e pulado quando horario == Personalizado."""
        h_step = next(s for s in wizard.steps if s.id == "horario_personalizado")
        assert h_step.skip_condition({"horario": "Personalizado"}) is False

    def test_tipo_servico_step_options(self, wizard):
        """Testa opcoes de tipo_servico."""
        ts_step = next(s for s in wizard.steps if s.id == "tipo_servico")
        assert ts_step.step_type == StepType.CHOICE
        assert "Limpeza Geral" in ts_step.options
        assert "Limpeza Pos-Obra" in ts_step.options
        assert "Manutencao Predial" in ts_step.options
        assert "Portaria (cobertura)" in ts_step.options
        assert "Jardinagem" in ts_step.options
        assert len(ts_step.options) == 8

    def test_valor_step_validation_rules(self, wizard):
        """Testa regras de validacao do passo valor (min 50, max 10000)."""
        valor_step = next(s for s in wizard.steps if s.id == "valor")
        assert valor_step.step_type == StepType.NUMBER_INPUT
        assert valor_step.validation_rules.get("min_value") == 50
        assert valor_step.validation_rules.get("max_value") == 10000
        assert valor_step.required is False

    @pytest.mark.asyncio
    async def test_process_result_structure(self, wizard):
        """Testa que process_result retorna a estrutura correta."""
        data = {
            "diarista": "Maria da Silva",
            "data": "15/02/2026",
            "horario": "Integral (08:00 - 17:00)",
            "local": "Condominio Central - Bloco A",
            "tipo_servico": "Limpeza Geral",
            "valor": 200.0,
            "observacoes": "Trazer material de limpeza",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert "agendamento" in result
        assert "proximos_passos" in result
        assert "alertas" in result
        assert result["agendamento"]["diarista"] == "Maria da Silva"
        assert result["agendamento"]["data"] == "15/02/2026"
        assert result["agendamento"]["horario_inicio"] == "08:00"
        assert result["agendamento"]["horario_fim"] == "17:00"
        assert result["agendamento"]["horas_previstas"] == 8
        assert result["agendamento"]["tipo_servico"] == "limpeza_geral"
        assert result["agendamento"]["valor_bruto"] == 200.0
        assert result["agendamento"]["status"] == "agendado"

    @pytest.mark.asyncio
    async def test_process_result_descontos_calculation(self, wizard):
        """Testa calculo correto de descontos."""
        data = {
            "diarista": "Ana Costa",
            "data": "20/02/2026",
            "horario": "Integral (08:00 - 17:00)",
            "local": "Cond. Flores",
            "tipo_servico": "Limpeza Geral",
            "valor": 300.0,
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        descontos = result["agendamento"]["descontos"]
        assert descontos is not None
        # INSS 11%
        assert descontos["inss"] == round(300.0 * 0.11, 2)
        assert descontos["inss"] == 33.0
        # ISS 5%
        assert descontos["iss"] == round(300.0 * 0.05, 2)
        assert descontos["iss"] == 15.0
        # IRRF 7.5% (valor > 250)
        assert descontos["irrf"] == round(300.0 * 0.075, 2)
        assert descontos["irrf"] == 22.5
        # Total descontos
        total_desc = 33.0 + 15.0 + 22.5
        assert descontos["total_descontos"] == round(total_desc, 2)
        # Valor liquido
        assert descontos["valor_liquido"] == round(300.0 - total_desc, 2)

    @pytest.mark.asyncio
    async def test_process_result_descontos_sem_irrf(self, wizard):
        """Testa que IRRF nao e aplicado quando valor <= 250."""
        data = {
            "diarista": "Julia Santos",
            "data": "21/02/2026",
            "horario": "Meio periodo manha (08:00 - 12:00)",
            "local": "Cond. Sol",
            "tipo_servico": "Limpeza Geral",
            "valor": 150.0,
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        descontos = result["agendamento"]["descontos"]
        assert descontos is not None
        assert descontos["irrf"] == 0.0
        assert descontos["inss"] == round(150.0 * 0.11, 2)
        assert descontos["iss"] == round(150.0 * 0.05, 2)

    @pytest.mark.asyncio
    async def test_process_result_sem_valor(self, wizard):
        """Testa processamento sem valor informado."""
        data = {
            "diarista": "Paula Lima",
            "data": "22/02/2026",
            "horario": "Integral (08:00 - 17:00)",
            "local": "Cond. Mar",
            "tipo_servico": "Jardinagem",
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        assert result["agendamento"]["valor_bruto"] is None
        assert result["agendamento"]["descontos"] is None

    @pytest.mark.asyncio
    async def test_process_result_personalizado_horario(self, wizard):
        """Testa processamento com horario personalizado."""
        data = {
            "diarista": "Carla Nunes",
            "data": "23/02/2026",
            "horario": "Personalizado",
            "horario_personalizado": "09:00 - 15:00",
            "local": "Cond. Lago",
            "tipo_servico": "Recepcao",
            "valor": 180.0,
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        assert result["agendamento"]["horario_inicio"] == "09:00"
        assert result["agendamento"]["horario_fim"] == "15:00"

    @pytest.mark.asyncio
    async def test_process_result_noturno_alert(self, wizard):
        """Testa alerta para turno noturno."""
        data = {
            "diarista": "Roberto Alves",
            "data": "24/02/2026",
            "horario": "Noturno (18:00 - 06:00)",
            "local": "Cond. Noite",
            "tipo_servico": "Vigilancia (cobertura)",
            "valor": 250.0,
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        # Deve ter alerta de turno noturno e de jornada longa (12h)
        assert any("noturno" in a["mensagem"].lower() for a in alerts)
        assert any("12" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_valor_baixo_alert(self, wizard):
        """Testa alerta quando valor < 100."""
        data = {
            "diarista": "Teste Baixo",
            "data": "25/02/2026",
            "horario": "Meio periodo manha (08:00 - 12:00)",
            "local": "Cond. Teste",
            "tipo_servico": "Limpeza Geral",
            "valor": 80.0,
            "observacoes": "nao",
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("R$ 100" in a["mensagem"] for a in alerts)

    def test_confirmacao_step_is_last(self, wizard):
        """Testa que confirmacao e o ultimo passo."""
        assert wizard.steps[-1].id == "confirmacao"
        assert wizard.steps[-1].step_type == StepType.CONFIRMATION

    def test_observacoes_step_not_required(self, wizard):
        """Testa que observacoes nao e obrigatorio."""
        obs_step = next(s for s in wizard.steps if s.id == "observacoes")
        assert obs_step.required is False


# ==========================================================================
# ComunicadoWizard
# ==========================================================================


class TestComunicadoWizard:
    """Testes para ComunicadoWizard."""

    @pytest.fixture
    def wizard(self):
        return ComunicadoWizard(user_id=1, session_id="sess-comunicado")

    def test_wizard_type(self, wizard):
        """Testa que o tipo do wizard e 'comunicado'."""
        assert wizard.get_wizard_type() == "comunicado"

    def test_wizard_name(self, wizard):
        """Testa que o nome do wizard e correto."""
        assert wizard.get_wizard_name() == "Criacao de Comunicado"

    def test_wizard_description(self, wizard):
        """Testa que a descricao menciona comunicado."""
        desc = wizard.get_wizard_description()
        assert "comunicado" in desc.lower()

    def test_steps_count(self, wizard):
        """Testa que o wizard tem exatamente 10 passos."""
        assert len(wizard.steps) == 10

    def test_step_ids(self, wizard):
        """Testa que todos os step IDs esperados estao presentes."""
        step_ids = [s.id for s in wizard.steps]
        expected = [
            "tipo",
            "titulo",
            "conteudo",
            "prioridade",
            "destinatarios",
            "destinatarios_detalhe",
            "requer_confirmacao",
            "publicacao",
            "data_agendamento",
            "confirmacao",
        ]
        assert step_ids == expected

    def test_start_returns_waiting_input(self, wizard):
        """Testa que start() retorna WAITING_INPUT."""
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == 10

    def test_tipo_step_options(self, wizard):
        """Testa opcoes do passo tipo."""
        tipo_step = next(s for s in wizard.steps if s.id == "tipo")
        assert tipo_step.step_type == StepType.CHOICE
        assert "Informativo" in tipo_step.options
        assert "Alerta" in tipo_step.options
        assert "Procedimento" in tipo_step.options
        assert "Escala" in tipo_step.options
        assert "Treinamento" in tipo_step.options
        assert "Politica" in tipo_step.options
        assert "Urgente" in tipo_step.options
        assert "Outro" in tipo_step.options
        assert len(tipo_step.options) == 8

    def test_prioridade_options(self, wizard):
        """Testa que prioridade tem as opcoes Baixa, Normal, Alta, Urgente."""
        prio_step = next(s for s in wizard.steps if s.id == "prioridade")
        assert prio_step.step_type == StepType.CHOICE
        assert prio_step.options == ["Baixa", "Normal", "Alta", "Urgente"]

    def test_destinatarios_options(self, wizard):
        """Testa opcoes de destinatarios."""
        dest_step = next(s for s in wizard.steps if s.id == "destinatarios")
        assert dest_step.step_type == StepType.CHOICE
        assert "Todos os funcionarios" in dest_step.options
        assert "Apenas supervisores/gestores" in dest_step.options
        assert "Posto especifico" in dest_step.options
        assert "Departamento especifico" in dest_step.options
        assert "Funcionario(s) especifico(s)" in dest_step.options

    def test_destinatarios_detalhe_skip_for_todos(self, wizard):
        """Testa que destinatarios_detalhe e pulado quando destinatarios = 'Todos os funcionarios'."""
        dd_step = next(s for s in wizard.steps if s.id == "destinatarios_detalhe")
        assert dd_step.skip_condition is not None
        assert dd_step.skip_condition({"destinatarios": "Todos os funcionarios"}) is True

    def test_destinatarios_detalhe_skip_for_supervisores(self, wizard):
        """Testa que destinatarios_detalhe e pulado para supervisores/gestores."""
        dd_step = next(s for s in wizard.steps if s.id == "destinatarios_detalhe")
        assert dd_step.skip_condition({"destinatarios": "Apenas supervisores/gestores"}) is True

    def test_destinatarios_detalhe_not_skipped_for_posto(self, wizard):
        """Testa que destinatarios_detalhe NAO e pulado para posto especifico."""
        dd_step = next(s for s in wizard.steps if s.id == "destinatarios_detalhe")
        assert dd_step.skip_condition({"destinatarios": "Posto especifico"}) is False

    def test_destinatarios_detalhe_not_skipped_for_departamento(self, wizard):
        """Testa que destinatarios_detalhe NAO e pulado para departamento especifico."""
        dd_step = next(s for s in wizard.steps if s.id == "destinatarios_detalhe")
        assert dd_step.skip_condition({"destinatarios": "Departamento especifico"}) is False

    def test_destinatarios_detalhe_not_skipped_for_funcionarios(self, wizard):
        """Testa que destinatarios_detalhe NAO e pulado para funcionarios especificos."""
        dd_step = next(s for s in wizard.steps if s.id == "destinatarios_detalhe")
        assert dd_step.skip_condition({"destinatarios": "Funcionario(s) especifico(s)"}) is False

    def test_data_agendamento_skip_for_publicar_agora(self, wizard):
        """Testa que data_agendamento e pulado quando publicacao != 'Agendar publicacao'."""
        da_step = next(s for s in wizard.steps if s.id == "data_agendamento")
        assert da_step.skip_condition is not None
        assert da_step.skip_condition({"publicacao": "Publicar agora"}) is True

    def test_data_agendamento_skip_for_rascunho(self, wizard):
        """Testa que data_agendamento e pulado para rascunho."""
        da_step = next(s for s in wizard.steps if s.id == "data_agendamento")
        assert da_step.skip_condition({"publicacao": "Salvar como rascunho"}) is True

    def test_data_agendamento_not_skipped_for_agendar(self, wizard):
        """Testa que data_agendamento NAO e pulado quando publicacao == 'Agendar publicacao'."""
        da_step = next(s for s in wizard.steps if s.id == "data_agendamento")
        assert da_step.skip_condition({"publicacao": "Agendar publicacao"}) is False

    def test_publicacao_step_options(self, wizard):
        """Testa opcoes de publicacao."""
        pub_step = next(s for s in wizard.steps if s.id == "publicacao")
        assert pub_step.step_type == StepType.CHOICE
        assert "Publicar agora" in pub_step.options
        assert "Salvar como rascunho" in pub_step.options
        assert "Agendar publicacao" in pub_step.options
        assert len(pub_step.options) == 3

    def test_requer_confirmacao_step_options(self, wizard):
        """Testa opcoes de confirmacao de leitura."""
        rc_step = next(s for s in wizard.steps if s.id == "requer_confirmacao")
        assert rc_step.step_type == StepType.CHOICE
        assert rc_step.options == ["Sim", "Nao"]

    def test_titulo_validation_rules(self, wizard):
        """Testa regras de validacao do titulo."""
        titulo_step = next(s for s in wizard.steps if s.id == "titulo")
        assert titulo_step.validation_rules.get("min_length") == 5
        assert titulo_step.validation_rules.get("max_length") == 200

    def test_conteudo_validation_rules(self, wizard):
        """Testa regras de validacao do conteudo."""
        conteudo_step = next(s for s in wizard.steps if s.id == "conteudo")
        assert conteudo_step.validation_rules.get("min_length") == 10
        assert conteudo_step.validation_rules.get("max_length") == 5000

    @pytest.mark.asyncio
    async def test_process_result_structure(self, wizard):
        """Testa que process_result retorna a estrutura correta."""
        data = {
            "tipo": "Informativo",
            "titulo": "Aviso de Manutencao",
            "conteudo": "Informamos que a manutencao do elevador sera realizada amanha.",
            "prioridade": "Normal",
            "destinatarios": "Todos os funcionarios",
            "requer_confirmacao": "Nao",
            "publicacao": "Publicar agora",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert "comunicado" in result
        assert "proximos_passos" in result
        assert "alertas" in result
        assert result["comunicado"]["titulo"] == "Aviso de Manutencao"
        assert result["comunicado"]["tipo"] == "informativo"
        assert result["comunicado"]["prioridade"] == "normal"
        assert result["comunicado"]["target_type"] == "all"
        assert result["comunicado"]["target_ids"] is None
        assert result["comunicado"]["requires_acknowledgment"] is False
        assert result["comunicado"]["status"] == "publicado"
        assert result["comunicado"]["publish_action"] == "publish"
        assert result["comunicado"]["schedule_at"] is None

    @pytest.mark.asyncio
    async def test_process_result_rascunho(self, wizard):
        """Testa processamento como rascunho."""
        data = {
            "tipo": "Procedimento",
            "titulo": "Novo Procedimento de Ronda",
            "conteudo": "A partir de 01/03 o procedimento de ronda sera alterado conforme segue...",
            "prioridade": "Alta",
            "destinatarios": "Apenas supervisores/gestores",
            "requer_confirmacao": "Sim",
            "publicacao": "Salvar como rascunho",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert result["comunicado"]["status"] == "rascunho"
        assert result["comunicado"]["publish_action"] == "draft"
        assert result["comunicado"]["target_type"] == "role"
        assert result["comunicado"]["target_roles"] == ["supervisor", "gestor", "admin", "coordenador"]
        assert result["comunicado"]["requires_acknowledgment"] is True

    @pytest.mark.asyncio
    async def test_process_result_agendado(self, wizard):
        """Testa processamento agendado."""
        data = {
            "tipo": "Escala",
            "titulo": "Nova Escala Fevereiro",
            "conteudo": "Segue a escala do mes de fevereiro conforme acordado.",
            "prioridade": "Normal",
            "destinatarios": "Posto especifico",
            "destinatarios_detalhe": "Portaria Principal, Guarita Norte",
            "requer_confirmacao": "Sim",
            "publicacao": "Agendar publicacao",
            "data_agendamento": "01/02/2026 09:00",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        assert result["comunicado"]["status"] == "agendado"
        assert result["comunicado"]["publish_action"] == "schedule"
        assert result["comunicado"]["schedule_at"] == "01/02/2026 09:00"
        assert result["comunicado"]["target_type"] == "post"
        assert result["comunicado"]["target_ids"] == ["Portaria Principal", "Guarita Norte"]

    @pytest.mark.asyncio
    async def test_process_result_urgente_alert(self, wizard):
        """Testa alerta para prioridade urgente."""
        data = {
            "tipo": "Urgente",
            "titulo": "Alerta de Seguranca",
            "conteudo": "Alerta: situacao de emergencia no condominio. Todos devem seguir protocolo.",
            "prioridade": "Urgente",
            "destinatarios": "Todos os funcionarios",
            "requer_confirmacao": "Sim",
            "publicacao": "Publicar agora",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("URGENTE" in a["mensagem"] for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_alta_sem_confirmacao_alert(self, wizard):
        """Testa alerta quando alta prioridade sem confirmacao de leitura."""
        data = {
            "tipo": "Alerta",
            "titulo": "Alerta Operacional",
            "conteudo": "Atencao para mudanca operacional importante a ser implementada.",
            "prioridade": "Alta",
            "destinatarios": "Todos os funcionarios",
            "requer_confirmacao": "Nao",
            "publicacao": "Publicar agora",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("confirmacao de leitura" in a["mensagem"].lower() for a in alerts)

    @pytest.mark.asyncio
    async def test_process_result_todos_funcionarios_alert(self, wizard):
        """Testa alerta quando envia para todos os funcionarios."""
        data = {
            "tipo": "Informativo",
            "titulo": "Aviso Geral",
            "conteudo": "Informamos a todos sobre o evento de confraternizacao.",
            "prioridade": "Baixa",
            "destinatarios": "Todos os funcionarios",
            "requer_confirmacao": "Nao",
            "publicacao": "Publicar agora",
            "confirmacao": True,
        }
        result = await wizard.process_result(data)
        alerts = result["alertas"]
        assert any("TODOS os funcionarios" in a["mensagem"] for a in alerts)

    def test_confirmacao_step_is_last(self, wizard):
        """Testa que confirmacao e o ultimo passo."""
        assert wizard.steps[-1].id == "confirmacao"
        assert wizard.steps[-1].step_type == StepType.CONFIRMATION

    def test_generate_next_steps_publish(self, wizard):
        """Testa next steps para publicacao imediata."""
        steps = wizard._generate_next_steps("publish", "normal")
        assert any("publicado imediatamente" in s.lower() for s in steps)
        assert any("notificados" in s.lower() for s in steps)

    def test_generate_next_steps_draft(self, wizard):
        """Testa next steps para rascunho."""
        steps = wizard._generate_next_steps("draft", "normal")
        assert any("rascunho" in s.lower() for s in steps)

    def test_generate_next_steps_schedule(self, wizard):
        """Testa next steps para agendamento."""
        steps = wizard._generate_next_steps("schedule", "normal")
        assert any("agendada" in s.lower() for s in steps)

    def test_generate_next_steps_urgente_publish(self, wizard):
        """Testa next steps para publicacao urgente."""
        steps = wizard._generate_next_steps("publish", "urgente")
        assert any("prioridade" in s.lower() for s in steps)


# ==========================================================================
# Testes Cross-Wizard
# ==========================================================================


class TestCrossWizard:
    """Testes que abrangem todos os 4 novos wizards."""

    @pytest.fixture(
        params=[
            ("escala", EscalaWizard),
            ("posto", PostoWizard),
            ("diarista", DiaristaWizard),
            ("comunicado", ComunicadoWizard),
        ]
    )
    def wizard_pair(self, request):
        """Fixture parametrizada para todos os wizards."""
        wizard_type, wizard_class = request.param
        return wizard_type, wizard_class(user_id=1, session_id=f"sess-{wizard_type}")

    def test_all_new_wizards_start_correctly(self, wizard_pair):
        """Testa que todos os novos wizards iniciam corretamente."""
        wizard_type, wizard = wizard_pair
        response = wizard.start()
        assert response.state == WizardState.WAITING_INPUT
        assert response.step_number == 1
        assert response.total_steps == len(wizard.steps)
        assert response.question is not None
        assert response.progress_percent == 0.0
        assert response.can_go_back is False

    def test_all_new_wizards_cancel(self, wizard_pair):
        """Testa que todos os novos wizards cancelam corretamente."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.cancel()
        assert response.state == WizardState.CANCELLED
        assert "cancelado" in response.message.lower()

    def test_all_new_wizards_go_back_from_first_step(self, wizard_pair):
        """Testa que go_back no primeiro passo retorna mensagem adequada."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.go_back()
        assert "primeiro passo" in response.message.lower()
        assert response.step_number == 1

    def test_all_new_wizards_cancel_via_input(self, wizard_pair):
        """Testa cancelamento via process_input('cancelar')."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.process_input("cancelar")
        assert response.state == WizardState.CANCELLED

    def test_all_new_wizards_cancel_via_sair(self, wizard_pair):
        """Testa cancelamento via process_input('sair')."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.process_input("sair")
        assert response.state == WizardState.CANCELLED

    def test_all_new_wizards_cancel_via_parar(self, wizard_pair):
        """Testa cancelamento via process_input('parar')."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.process_input("parar")
        assert response.state == WizardState.CANCELLED

    def test_all_new_wizards_process_completed(self, wizard_pair):
        """Testa que processar input em wizard completado retorna COMPLETED."""
        wizard_type, wizard = wizard_pair
        wizard.data.state = WizardState.COMPLETED
        response = wizard.process_input("qualquer coisa")
        assert response.state == WizardState.COMPLETED
        assert "concluido" in response.message.lower()

    def test_all_new_wizards_process_cancelled(self, wizard_pair):
        """Testa que processar input em wizard cancelado retorna CANCELLED."""
        wizard_type, wizard = wizard_pair
        wizard.data.state = WizardState.CANCELLED
        response = wizard.process_input("qualquer coisa")
        assert response.state == WizardState.CANCELLED
        assert "cancelado" in response.message.lower()

    def test_all_new_wizards_have_confirmacao_last(self, wizard_pair):
        """Testa que todos os wizards terminam com confirmacao."""
        wizard_type, wizard = wizard_pair
        assert wizard.steps[-1].id == "confirmacao"
        assert wizard.steps[-1].step_type == StepType.CONFIRMATION

    def test_all_new_wizards_set_initial_data(self, wizard_pair):
        """Testa set_initial_data em todos os wizards."""
        wizard_type, wizard = wizard_pair
        wizard.set_initial_data({"custom_key": "custom_value"})
        assert wizard.data.collected_data["custom_key"] == "custom_value"

    def test_all_new_wizards_get_state(self, wizard_pair):
        """Testa get_state em todos os wizards."""
        wizard_type, wizard = wizard_pair
        state = wizard.get_state()
        assert state.wizard_type == wizard.get_wizard_type()
        assert state.state == WizardState.NOT_STARTED

    def test_all_new_wizards_first_step_required(self, wizard_pair):
        """Testa que o primeiro passo e obrigatorio em todos os wizards."""
        wizard_type, wizard = wizard_pair
        assert wizard.steps[0].required is True

    def test_all_new_wizards_empty_input_validation(self, wizard_pair):
        """Testa que input vazio no primeiro passo (obrigatorio) gera erro."""
        wizard_type, wizard = wizard_pair
        wizard.start()
        response = wizard.process_input("")
        assert response.validation_error is not None
        assert response.step_number == 1  # Nao avancou
