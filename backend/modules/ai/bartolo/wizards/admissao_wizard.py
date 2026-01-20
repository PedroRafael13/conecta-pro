"""
Wizard de Admissao de Funcionario.

Guia o usuario no processo de admissao, coletando todos os dados
necessarios e validando conforme CLT.
"""

from datetime import datetime
from typing import Any
from modules.ai.bartolo.wizards.base_wizard import (
    BaseWizard, WizardStep, StepType
)


class AdmissaoWizard(BaseWizard):
    """Wizard para admissao de funcionario."""

    def get_wizard_type(self) -> str:
        return "admissao_funcionario"

    def get_wizard_name(self) -> str:
        return "Admissao de Funcionario"

    def get_wizard_description(self) -> str:
        return "Vou te ajudar a admitir um novo funcionario, coletando todas as informacoes necessarias e gerando os documentos."

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # Dados Pessoais
            WizardStep(
                id="nome_completo",
                name="Nome Completo",
                description="Nome completo do funcionario",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome completo do novo funcionario?",
                required=True,
                validation_rules={"min_length": 5, "max_length": 200},
            ),

            WizardStep(
                id="cpf",
                name="CPF",
                description="CPF do funcionario",
                step_type=StepType.TEXT_INPUT,
                question="Qual o CPF do funcionario? (apenas numeros)",
                required=True,
                help_text="Digite apenas os 11 numeros do CPF.",
                validation_rules={"min_length": 11, "max_length": 14},
            ),

            WizardStep(
                id="data_nascimento",
                name="Data de Nascimento",
                description="Data de nascimento",
                step_type=StepType.DATE_INPUT,
                question="Qual a data de nascimento? (DD/MM/AAAA)",
                required=True,
            ),

            # Dados do Contrato
            WizardStep(
                id="cargo",
                name="Cargo",
                description="Cargo do funcionario",
                step_type=StepType.CHOICE,
                question="Qual o cargo do funcionario?",
                required=True,
                options=[
                    "Porteiro",
                    "Porteiro Lider",
                    "Vigilante",
                    "Zelador",
                    "Faxineiro",
                    "Auxiliar de Limpeza",
                    "Recepcionista",
                    "Eletricista",
                    "Auxiliar de Manutencao",
                    "Outro",
                ],
            ),

            WizardStep(
                id="salario",
                name="Salario",
                description="Salario mensal",
                step_type=StepType.NUMBER_INPUT,
                question="Qual o salario mensal? (R$)",
                required=True,
                help_text="O sistema validara se esta acima do piso da categoria conforme CCT.",
                validation_rules={"min_value": 1412.00},  # Salario minimo 2024
            ),

            WizardStep(
                id="data_admissao",
                name="Data de Admissao",
                description="Data de inicio",
                step_type=StepType.DATE_INPUT,
                question="Qual a data de admissao? (DD/MM/AAAA)",
                required=True,
                help_text="Data em que o funcionario comecara a trabalhar.",
            ),

            WizardStep(
                id="tipo_contrato",
                name="Tipo de Contrato",
                description="Tipo de contrato de trabalho",
                step_type=StepType.CHOICE,
                question="Qual o tipo de contrato?",
                required=True,
                options=[
                    "CLT Prazo Indeterminado",
                    "CLT Prazo Determinado (90 dias)",
                    "Experiencia (45+45 dias)",
                ],
            ),

            WizardStep(
                id="escala",
                name="Escala de Trabalho",
                description="Escala de trabalho",
                step_type=StepType.CHOICE,
                question="Qual a escala de trabalho?",
                required=True,
                options=[
                    "12x36 Diurno",
                    "12x36 Noturno",
                    "5x2 (Segunda a Sexta)",
                    "6x1 (Folga rotativa)",
                ],
            ),

            WizardStep(
                id="posto_trabalho",
                name="Posto de Trabalho",
                description="Local onde ira trabalhar",
                step_type=StepType.TEXT_INPUT,
                question="Qual o posto/cliente onde o funcionario ira trabalhar?",
                required=True,
            ),

            # Documentos
            WizardStep(
                id="documentos_ok",
                name="Documentos",
                description="Conferencia de documentos",
                step_type=StepType.CONFIRMATION,
                question="Todos os documentos foram entregues? (RG, CPF, CTPS, Comprovante Residencia, Foto 3x4)",
                required=True,
                options=["Sim, todos entregues", "Nao, faltam documentos"],
                help_text="A admissao so pode ser finalizada com todos os documentos.",
            ),

            WizardStep(
                id="exame_admissional",
                name="Exame Admissional",
                description="Exame admissional",
                step_type=StepType.CONFIRMATION,
                question="O exame admissional ja foi realizado e o funcionario esta APTO?",
                required=True,
                options=["Sim, apto", "Nao, ainda nao realizou"],
                help_text="O exame admissional e obrigatorio antes do inicio das atividades.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da admissao."""
        # Aqui integraria com o modulo de RH para criar o funcionario

        return {
            "funcionario": {
                "nome": data.get("nome_completo"),
                "cpf": data.get("cpf"),
                "data_nascimento": data.get("data_nascimento"),
                "cargo": data.get("cargo"),
                "salario": data.get("salario"),
                "data_admissao": data.get("data_admissao"),
                "tipo_contrato": data.get("tipo_contrato"),
                "escala": data.get("escala"),
                "posto_trabalho": data.get("posto_trabalho"),
            },
            "status": {
                "documentos_ok": data.get("documentos_ok"),
                "exame_admissional": data.get("exame_admissional"),
            },
            "proximos_passos": [
                "Cadastrar funcionario no sistema",
                "Gerar contrato de trabalho",
                "Registrar na CTPS",
                "Enviar evento S-2200 ao eSocial",
                "Agendar integracao/treinamento",
                "Providenciar uniforme e EPI",
            ],
            "alertas": self._generate_alerts(data),
        }

    def _generate_alerts(self, data: dict) -> list:
        """Gera alertas baseados nos dados."""
        alerts = []

        if not data.get("documentos_ok"):
            alerts.append({
                "tipo": "warning",
                "mensagem": "Documentos pendentes - aguardar entrega antes de finalizar admissao",
            })

        if not data.get("exame_admissional"):
            alerts.append({
                "tipo": "error",
                "mensagem": "Exame admissional pendente - OBRIGATORIO antes do inicio das atividades",
            })

        # Valida piso salarial
        salario = data.get("salario", 0)
        cargo = data.get("cargo", "")

        pisos = {
            "Porteiro": 1847.12,
            "Porteiro Lider": 2124.19,
            "Vigilante": 2456.78,
            "Zelador": 1970.23,
            "Faxineiro": 1601.90,
            "Auxiliar de Limpeza": 1540.13,
            "Recepcionista": 1847.12,
            "Eletricista": 2370.41,
            "Auxiliar de Manutencao": 1724.51,
        }

        piso = pisos.get(cargo, 1412.00)
        if salario and salario < piso:
            alerts.append({
                "tipo": "error",
                "mensagem": f"Salario abaixo do piso da categoria ({cargo}). Minimo: R$ {piso:,.2f}",
            })

        return alerts
