"""
Wizard de Agendamento de Diarista.

Guia o usuario no processo de agendamento de uma diarista,
coletando diarista, data, horario, local e observacoes.
"""

from datetime import datetime

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep


class DiaristaWizard(BaseWizard):
    """Wizard para agendamento guiado de diarista."""

    def get_wizard_type(self) -> str:
        return "diarista"

    def get_wizard_name(self) -> str:
        return "Agendamento de Diarista"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a agendar uma diarista, "
            "coletando todas as informacoes necessarias como "
            "profissional, data, horario e local de trabalho."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Diarista
            WizardStep(
                id="diarista",
                name="Diarista",
                description="Nome ou ID da diarista a ser escalada",
                step_type=StepType.TEXT_INPUT,
                question="Qual diarista deseja escalar? (nome ou ID, ou 'disponivel' para ver disponiveis)",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text=(
                    "Informe o nome ou ID da diarista.\nOu digite 'disponivel' para listar diaristas com agenda livre."
                ),
            ),
            # 2. Data
            WizardStep(
                id="data",
                name="Data do Servico",
                description="Data em que o servico sera realizado",
                step_type=StepType.TEXT_INPUT,
                question="Para qual data? (ex: 15/02/2026, amanha, segunda)",
                required=True,
                validation_rules={"min_length": 2, "max_length": 30},
                help_text="Informe a data no formato DD/MM/AAAA ou use termos como 'amanha', 'segunda'.",
            ),
            # 3. Horario
            WizardStep(
                id="horario",
                name="Horario",
                description="Horario de inicio e fim do servico",
                step_type=StepType.CHOICE,
                question="Qual o horario do servico?",
                required=True,
                options=[
                    "Integral (08:00 - 17:00)",
                    "Meio periodo manha (08:00 - 12:00)",
                    "Meio periodo tarde (13:00 - 17:00)",
                    "Noturno (18:00 - 06:00)",
                    "Personalizado",
                ],
                help_text="Selecione o horario de trabalho da diarista.",
            ),
            # 4. Horario personalizado (condicional)
            WizardStep(
                id="horario_personalizado",
                name="Horario Personalizado",
                description="Horarios de inicio e fim personalizados",
                step_type=StepType.TEXT_INPUT,
                question="Informe o horario de inicio e fim (ex: 09:00 - 15:00)",
                required=False,
                validation_rules={"min_length": 5, "max_length": 30},
                help_text="Formato: HH:MM - HH:MM",
                skip_condition=lambda data: data.get("horario") != "Personalizado",
            ),
            # 5. Local
            WizardStep(
                id="local",
                name="Local de Trabalho",
                description="Local onde o servico sera realizado",
                step_type=StepType.TEXT_INPUT,
                question="Qual o local de trabalho? (posto, endereco ou referencia)",
                required=True,
                validation_rules={"min_length": 3, "max_length": 300},
                help_text="Informe o posto, condominio ou endereco completo.",
            ),
            # 6. Tipo de servico
            WizardStep(
                id="tipo_servico",
                name="Tipo de Servico",
                description="Tipo de servico a ser realizado",
                step_type=StepType.CHOICE,
                question="Qual o tipo de servico?",
                required=True,
                options=[
                    "Limpeza Geral",
                    "Limpeza Pos-Obra",
                    "Manutencao Predial",
                    "Portaria (cobertura)",
                    "Vigilancia (cobertura)",
                    "Jardinagem",
                    "Recepcao",
                    "Outro",
                ],
                help_text="Tipo de servico que a diarista realizara.",
            ),
            # 7. Valor (opcional)
            WizardStep(
                id="valor",
                name="Valor da Diaria",
                description="Valor a ser pago pela diaria",
                step_type=StepType.NUMBER_INPUT,
                question="Qual o valor da diaria? (em R$, ex: 150.00)",
                required=False,
                validation_rules={"min_value": 50, "max_value": 10000},
                help_text="Informe o valor bruto da diaria. Se nao informado, sera usado o valor padrao.",
            ),
            # 8. Observacoes
            WizardStep(
                id="observacoes",
                name="Observacoes",
                description="Observacoes adicionais",
                step_type=StepType.TEXT_INPUT,
                question="Alguma observacao adicional? (ou 'nao' para pular)",
                required=False,
                help_text="Materiais necessarios, instrucoes especiais, contato no local, etc.",
            ),
            # 9. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao do agendamento",
                step_type=StepType.CONFIRMATION,
                question="Os dados estao corretos? Deseja confirmar o agendamento?",
                required=True,
                options=["Sim, agendar diarista", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final do agendamento."""
        # Parsear horario
        horario_str = data.get("horario", "")
        horario_map = {
            "Integral (08:00 - 17:00)": {"inicio": "08:00", "fim": "17:00", "horas": 8},
            "Meio periodo manha (08:00 - 12:00)": {"inicio": "08:00", "fim": "12:00", "horas": 4},
            "Meio periodo tarde (13:00 - 17:00)": {"inicio": "13:00", "fim": "17:00", "horas": 4},
            "Noturno (18:00 - 06:00)": {"inicio": "18:00", "fim": "06:00", "horas": 12},
            "Personalizado": {"inicio": "", "fim": "", "horas": 0},
        }
        horario_info = horario_map.get(horario_str, {"inicio": "", "fim": "", "horas": 0})

        if horario_info["inicio"] == "" and data.get("horario_personalizado"):
            horario = data["horario_personalizado"]
            partes = horario.replace(" ", "").split("-")
            if len(partes) == 2:
                horario_info["inicio"] = partes[0].strip()
                horario_info["fim"] = partes[1].strip()

        # Tipo de servico
        tipo_map = {
            "Limpeza Geral": "limpeza_geral",
            "Limpeza Pos-Obra": "limpeza_pos_obra",
            "Manutencao Predial": "manutencao",
            "Portaria (cobertura)": "portaria",
            "Vigilancia (cobertura)": "vigilancia",
            "Jardinagem": "jardinagem",
            "Recepcao": "recepcao",
            "Outro": "outro",
        }
        tipo_valor = tipo_map.get(data.get("tipo_servico", ""), "outro")

        # Valor
        valor = data.get("valor")
        if isinstance(valor, str):
            try:
                valor = float(valor.replace(",", ".").replace("R$", "").strip())
            except ValueError:
                valor = None

        # Observacoes
        obs = data.get("observacoes", "")
        if obs and obs.lower() in ("nao", "n", "nenhuma", "sem", "-", ""):
            obs = None

        # Calcular descontos estimados
        descontos = {}
        if valor:
            inss = valor * 0.11  # 11% INSS
            iss = valor * 0.05  # 5% ISS
            irrf = 0.0
            if valor > 250:
                irrf = valor * 0.075  # 7.5% IRRF simplificado
            descontos = {
                "inss": round(inss, 2),
                "iss": round(iss, 2),
                "irrf": round(irrf, 2),
                "total_descontos": round(inss + iss + irrf, 2),
                "valor_liquido": round(valor - inss - iss - irrf, 2),
            }

        return {
            "agendamento": {
                "diarista": data.get("diarista"),
                "data": data.get("data"),
                "horario_inicio": horario_info["inicio"],
                "horario_fim": horario_info["fim"],
                "horas_previstas": horario_info["horas"],
                "local": data.get("local"),
                "tipo_servico": tipo_valor,
                "valor_bruto": valor,
                "descontos": descontos if descontos else None,
                "observacoes": obs,
                "data_agendamento": datetime.utcnow().isoformat(),
                "status": "agendado",
            },
            "proximos_passos": [
                "Confirmar agendamento no sistema",
                "Notificar diarista sobre o agendamento",
                "Preparar materiais/equipamentos no local",
                "Registrar presenca no dia do servico",
                "Avaliar servico apos conclusao",
                "Gerar pagamento apos avaliacao",
            ],
            "alertas": self._generate_alerts(data, horario_info, valor),
        }

    def _generate_alerts(self, data: dict, horario_info: dict, valor) -> list:
        """Gera alertas baseados nos dados."""
        alerts = []

        # Turno noturno
        if horario_info.get("horas", 0) >= 12:
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": (
                        "Jornada de 12+ horas: Verificar conformidade CLT. "
                        "Intervalo intrajornada obrigatorio de no minimo 1h."
                    ),
                }
            )

        horario_str = data.get("horario", "")
        if "Noturno" in horario_str:
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Turno noturno: Adicional noturno de 20% sobre hora normal. "
                        "Hora noturna = 52min30s (CLT art. 73)."
                    ),
                }
            )

        # Valor baixo
        if valor and valor < 100:
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": "Valor da diaria abaixo de R$ 100,00. Verifique se esta correto.",
                }
            )

        return alerts
