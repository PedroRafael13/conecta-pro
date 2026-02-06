"""
Wizard de Solicitacao de Compensacao de Horas.

Guia o usuario no processo de solicitar compensacao de horas
do banco de horas, coletando funcionario, horas, data e motivo.
"""

from datetime import datetime
from typing import Any
from modules.ai.bartolo.wizards.base_wizard import (
    BaseWizard, WizardStep, StepType
)


class BancoHorasWizard(BaseWizard):
    """Wizard para solicitacao de compensacao de horas do banco."""

    def get_wizard_type(self) -> str:
        return "compensacao_banco_horas"

    def get_wizard_name(self) -> str:
        return "Solicitacao de Compensacao de Horas"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a solicitar uma compensacao de horas do banco, "
            "coletando todas as informacoes necessarias para o registro."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Selecionar funcionario
            WizardStep(
                id="funcionario",
                name="Funcionario",
                description="Funcionario que ira compensar as horas",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome ou ID do funcionario que ira compensar as horas?",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text=(
                    "Informe o nome completo ou o ID do funcionario no sistema. "
                    "Ex: 'Jose Silva' ou o UUID do funcionario."
                ),
            ),

            # 2. Verificar saldo disponivel (exibicao)
            WizardStep(
                id="verificacao_saldo",
                name="Verificacao de Saldo",
                description="Exibe o saldo disponivel do funcionario",
                step_type=StepType.DISPLAY,
                question=(
                    "Verificando saldo do funcionario...\n\n"
                    "**Informacoes do banco de horas serao exibidas aqui.**\n\n"
                    "O saldo sera consultado automaticamente ao processar a solicitacao.\n"
                    "Digite 'ok' para continuar."
                ),
                required=False,
                help_text="O sistema ira consultar o saldo em tempo real ao processar a solicitacao.",
            ),

            # 3. Definir horas a compensar
            WizardStep(
                id="horas_compensar",
                name="Horas a Compensar",
                description="Quantidade de horas para compensacao",
                step_type=StepType.NUMBER_INPUT,
                question="Quantas horas deseja compensar? (Ex: 4, 8, 2.5)",
                required=True,
                validation_rules={
                    "min_value": 0.5,
                    "max_value": 24.0,
                },
                help_text=(
                    "Informe a quantidade de horas a compensar. "
                    "Valores aceitos: 0.5h a 24h. "
                    "Use ponto ou virgula para decimais (ex: 4.5 ou 4,5)."
                ),
            ),

            # 4. Definir data da compensacao
            WizardStep(
                id="data_compensacao",
                name="Data da Compensacao",
                description="Data em que a compensacao sera realizada",
                step_type=StepType.DATE_INPUT,
                question="Qual a data da compensacao? (formato: dd/mm/aaaa)",
                required=True,
                validation_rules={"min_length": 8, "max_length": 10},
                help_text=(
                    "Informe a data em que o funcionario ira compensar as horas. "
                    "Formato: dd/mm/aaaa (ex: 05/02/2026). "
                    "A data deve ser futura ou igual a hoje."
                ),
            ),

            # 5. Motivo da compensacao
            WizardStep(
                id="motivo",
                name="Motivo da Compensacao",
                description="Motivo ou justificativa para a compensacao",
                step_type=StepType.CHOICE,
                question="Qual o motivo da compensacao?",
                required=True,
                options=[
                    "Folga compensatoria",
                    "Saida antecipada",
                    "Entrada tardia",
                    "Consulta medica",
                    "Compromisso pessoal",
                    "Ferias parciais",
                    "Outro motivo",
                ],
                help_text=(
                    "Selecione o motivo da compensacao. "
                    "Se nenhuma opcao se aplica, selecione 'Outro motivo' "
                    "e sera solicitada uma descricao."
                ),
            ),

            # 5b. Descricao do motivo (condicional - apenas se "Outro motivo")
            WizardStep(
                id="motivo_descricao",
                name="Descricao do Motivo",
                description="Descricao detalhada do motivo (quando 'Outro motivo')",
                step_type=StepType.TEXT_INPUT,
                question="Descreva o motivo da compensacao:",
                required=True,
                validation_rules={"min_length": 5, "max_length": 500},
                help_text="Informe uma descricao clara do motivo da compensacao.",
                depends_on="motivo",
                skip_condition=lambda data: data.get("motivo") != "Outro motivo",
            ),

            # 6. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.CONFIRMATION,
                question="Os dados acima estao corretos? Deseja solicitar esta compensacao?",
                required=True,
                options=["Sim, solicitar", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar a solicitacao.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da solicitacao de compensacao."""
        # Mapear motivos para valores internos
        motivo_map = {
            "Folga compensatoria": "folga_compensatoria",
            "Saida antecipada": "saida_antecipada",
            "Entrada tardia": "entrada_tardia",
            "Consulta medica": "consulta_medica",
            "Compromisso pessoal": "compromisso_pessoal",
            "Ferias parciais": "ferias_parciais",
            "Outro motivo": "outro",
        }

        motivo_selecionado = data.get("motivo", "")
        motivo_valor = motivo_map.get(motivo_selecionado, "outro")

        # Se motivo e "outro", usar a descricao fornecida
        motivo_descricao = data.get("motivo_descricao", "")
        if motivo_valor == "outro" and motivo_descricao:
            motivo_final = motivo_descricao
        else:
            motivo_final = motivo_selecionado

        # Parsear data
        data_compensacao_str = data.get("data_compensacao", "")
        data_compensacao = None
        try:
            parts = data_compensacao_str.replace("-", "/").split("/")
            if len(parts) == 3:
                if len(parts[0]) == 4:
                    # yyyy/mm/dd
                    data_compensacao = f"{parts[0]}-{parts[1]}-{parts[2]}"
                else:
                    # dd/mm/yyyy
                    data_compensacao = f"{parts[2]}-{parts[1]}-{parts[0]}"
        except (ValueError, IndexError):
            data_compensacao = data_compensacao_str

        # Horas
        horas = data.get("horas_compensar", 0)
        if isinstance(horas, str):
            try:
                horas = float(horas.replace(",", ".").replace("h", "").strip())
            except ValueError:
                horas = 0

        return {
            "compensacao": {
                "funcionario": data.get("funcionario"),
                "horas": horas,
                "data_compensacao": data_compensacao,
                "motivo": motivo_final,
                "motivo_tipo": motivo_valor,
                "data_solicitacao": datetime.utcnow().isoformat(),
            },
            "validacoes": self._generate_validations(data, horas),
            "proximos_passos": self._generate_next_steps(horas),
            "alertas": self._generate_alerts(data, horas),
        }

    def _generate_validations(self, data: dict, horas: float) -> list:
        """Gera validacoes para a solicitacao."""
        validations = []

        if horas > 0:
            validations.append({
                "tipo": "info",
                "mensagem": f"Compensacao de {horas:.1f}h solicitada.",
            })

        if horas > 8:
            validations.append({
                "tipo": "warning",
                "mensagem": (
                    f"Compensacao superior a 8h ({horas:.1f}h). "
                    "Verificar se o funcionario nao excede jornada diaria."
                ),
            })

        return validations

    def _generate_next_steps(self, horas: float) -> list:
        """Gera proximos passos apos a solicitacao."""
        steps = [
            "Registrar solicitacao no sistema",
            "Enviar para aprovacao do supervisor",
            "Notificar funcionario sobre a solicitacao",
        ]

        if horas >= 8:
            steps.extend([
                "Verificar cobertura do posto no dia da compensacao",
                "Providenciar substituto se necessario",
            ])

        steps.append("Atualizar saldo do banco de horas apos aprovacao")
        return steps

    def _generate_alerts(self, data: dict, horas: float) -> list:
        """Gera alertas baseados nos dados."""
        alerts = []

        if horas > 12:
            alerts.append({
                "tipo": "warning",
                "mensagem": (
                    f"Compensacao de {horas:.1f}h e significativa. "
                    "Considerar dividir em mais de um dia."
                ),
            })

        # Verificar se motivo exige documentacao
        motivos_com_doc = ["Consulta medica"]
        motivo = data.get("motivo", "")
        if motivo in motivos_com_doc:
            alerts.append({
                "tipo": "info",
                "mensagem": (
                    f"Motivo '{motivo}' pode exigir documentacao comprobatoria. "
                    "Solicitar ao funcionario o documento pertinente."
                ),
            })

        return alerts
