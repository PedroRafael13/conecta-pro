"""
Wizard de Criacao de Ronda de Inspecao.

Guia o usuario no processo de criacao de uma nova ronda de inspecao,
coletando tipo, area, inspetor, data, checkpoints e observacoes.

Steps:
    1. tipo_ronda      - Tipo de inspecao
    2. area            - Area/setor a inspecionar
    3. inspetor        - Inspetor responsavel
    4. data_agendamento - Data e hora
    5. checkpoints     - Pontos de verificacao
    6. observacoes     - Observacoes (opcional)
    7. confirmacao     - Revisao e confirmacao

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep  # noqa: E402


class RondaWizard(BaseWizard):
    """Wizard para criacao de ronda de inspecao."""

    def get_wizard_type(self) -> str:
        return "ronda_inspecao"

    def get_wizard_name(self) -> str:
        return "Criacao de Ronda de Inspecao"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a criar uma nova ronda de inspecao, coletando "
            "todas as informacoes necessarias para agendar e configurar a ronda."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Tipo de Inspecao
            WizardStep(
                id="tipo_ronda",
                name="Tipo de Inspecao",
                description="Tipo da ronda de inspecao a ser realizada",
                step_type=StepType.CHOICE,
                question="Qual o tipo de inspecao a ser realizada?",
                required=True,
                options=[
                    "Rotina",
                    "Programada",
                    "Emergencial",
                    "Especial",
                    "Noturna",
                    "Fim de Semana/Feriado",
                ],
                help_text=(
                    "Rotina: Inspecao regular do dia a dia.\n"
                    "Programada: Agendada com antecedencia.\n"
                    "Emergencial: Resposta a incidente ou denuncia.\n"
                    "Especial: Auditoria ou verificacao pontual.\n"
                    "Noturna: Inspecao no periodo noturno.\n"
                    "Fim de Semana/Feriado: Inspecao em dias especiais."
                ),
            ),
            # 2. Area/Setor
            WizardStep(
                id="area",
                name="Area/Setor",
                description="Area ou setor a ser inspecionado",
                step_type=StepType.TEXT_INPUT,
                question="Qual a area ou setor a ser inspecionado?",
                required=True,
                validation_rules={"min_length": 3, "max_length": 200},
                help_text=(
                    "Informe a area, setor ou local onde a ronda sera realizada.\n"
                    "Exemplos: Portaria Principal, Bloco A, Area Externa, Estacionamento."
                ),
            ),
            # 3. Inspetor Responsavel
            WizardStep(
                id="inspetor",
                name="Inspetor Responsavel",
                description="Nome e cargo do inspetor que realizara a ronda",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome do inspetor responsavel pela ronda?",
                required=True,
                validation_rules={"min_length": 5, "max_length": 200},
                help_text=("Informe o nome completo do inspetor, supervisor, gerente ou lider que realizara a ronda."),
            ),
            # 4. Data e Hora de Agendamento
            WizardStep(
                id="data_agendamento",
                name="Data e Hora",
                description="Data e hora de agendamento da ronda",
                step_type=StepType.DATE_INPUT,
                question="Qual a data e hora para agendamento? (DD/MM/AAAA HH:MM)",
                required=True,
                help_text=(
                    "Informe a data e hora em que a ronda deve ser iniciada.\n"
                    "Formato: DD/MM/AAAA HH:MM\n"
                    "Exemplo: 30/01/2026 08:00"
                ),
            ),
            # 5. Pontos de Verificacao (Checkpoints)
            WizardStep(
                id="checkpoints",
                name="Pontos de Verificacao",
                description="Lista de pontos a serem verificados durante a ronda",
                step_type=StepType.TEXT_INPUT,
                question=("Quais os pontos de verificacao da ronda?\n(Separe por virgula ou linha)"),
                required=True,
                validation_rules={"min_length": 5, "max_length": 1000},
                help_text=(
                    "Liste os pontos que o inspetor deve verificar.\n"
                    "Exemplos:\n"
                    "- Portaria Principal, Portaria Lateral, CFTV, Area de Carga\n"
                    "- Ou descreva um por linha:\n"
                    "  Verificar portaria\n"
                    "  Checar cameras\n"
                    "  Inspecionar area externa"
                ),
            ),
            # 6. Observacoes (opcional)
            WizardStep(
                id="observacoes",
                name="Observacoes",
                description="Observacoes adicionais para a ronda (opcional)",
                step_type=StepType.TEXT_INPUT,
                question="Alguma observacao adicional? (ou digite 'pular' para continuar)",
                required=False,
                validation_rules={"max_length": 500},
                help_text=(
                    "Informacoes adicionais que o inspetor deve saber.\n"
                    "Exemplos: alarme desativado no bloco B, portao lateral em manutencao."
                ),
            ),
            # 7. Confirmacao (revisao dos dados)
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.REVIEW,
                question="Revise os dados acima e confirme a criacao da ronda.",
                required=True,
                options=["Confirmar", "Voltar e editar", "Cancelar"],
                help_text="Confira todas as informacoes antes de confirmar.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da criacao da ronda."""
        # Processar checkpoints: separar por virgula ou linha
        checkpoints_raw = data.get("checkpoints", "")
        if isinstance(checkpoints_raw, str):
            # Tenta separar por virgula primeiro, depois por quebra de linha
            if "," in checkpoints_raw:
                checkpoints_list = [cp.strip() for cp in checkpoints_raw.split(",") if cp.strip()]
            elif "\n" in checkpoints_raw:
                checkpoints_list = [cp.strip() for cp in checkpoints_raw.split("\n") if cp.strip()]
            else:
                checkpoints_list = [checkpoints_raw.strip()] if checkpoints_raw.strip() else []
        else:
            checkpoints_list = checkpoints_raw if isinstance(checkpoints_raw, list) else []

        # Processar observacoes
        observacoes = data.get("observacoes", "")
        if isinstance(observacoes, str) and observacoes.lower() in ("pular", "nenhuma", "nao", "n", "-", ""):
            observacoes = None

        return {
            "ronda": {
                "tipo_inspecao": data.get("tipo_ronda"),
                "area_setor": data.get("area"),
                "inspetor_nome": data.get("inspetor"),
                "data_agendamento": data.get("data_agendamento"),
                "checkpoints": checkpoints_list,
                "total_checkpoints": len(checkpoints_list),
                "observacoes": observacoes,
            },
            "proximos_passos": [
                "Salvar ronda no sistema",
                "Notificar inspetor responsavel",
                "Agendar lembrete automatico",
                "Preparar formulario de checkpoints",
            ],
            "alertas": self._generate_alerts(data, checkpoints_list),
        }

    def _generate_alerts(self, data: dict, checkpoints_list: list) -> list:
        """Gera alertas baseados nos dados coletados."""
        alerts = []

        # Verificar tipo emergencial
        tipo = data.get("tipo_ronda", "")
        if tipo == "Emergencial":
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": "Ronda emergencial - prioridade alta. Notificar supervisao imediatamente.",
                }
            )

        # Verificar quantidade de checkpoints
        if len(checkpoints_list) == 0:
            alerts.append(
                {
                    "tipo": "error",
                    "mensagem": "Nenhum ponto de verificacao definido. A ronda precisa de pelo menos 1 checkpoint.",
                }
            )
        elif len(checkpoints_list) > 20:
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": f"{len(checkpoints_list)} checkpoints definidos. Considere dividir em mais de uma ronda.",
                }
            )

        # Verificar data de agendamento
        data_str = data.get("data_agendamento", "")
        if isinstance(data_str, str) and data_str:
            try:
                # Tentar parsear DD/MM/AAAA ou DD/MM/AAAA HH:MM
                for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
                    try:
                        dt = datetime.strptime(data_str, fmt)
                        if dt < datetime.utcnow():
                            alerts.append(
                                {
                                    "tipo": "warning",
                                    "mensagem": "Data de agendamento no passado. Verifique se esta correto.",
                                }
                            )
                        break
                    except ValueError:
                        continue
            except Exception:
                logger.debug("Erro ao analisar data/hora do agendamento")

        # Verificar ronda noturna
        if tipo == "Noturna":
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": "Ronda noturna - verificar se inspetor possui autorizacao para trabalho noturno.",
                }
            )

        # Verificar ronda fim de semana
        if tipo == "Fim de Semana/Feriado":
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": "Ronda em dia especial - verificar adicional de plantao e autorizacao.",
                }
            )

        return alerts
