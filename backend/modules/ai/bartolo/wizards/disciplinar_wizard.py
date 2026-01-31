"""
Wizard de Medida Disciplinar.

Guia o usuario no processo de criacao de uma medida disciplinar,
coletando todos os dados necessarios e validando conforme CLT.

Steps:
1. tipo_acao - Tipo (advertencia verbal, escrita, suspensao)
2. funcionario - Funcionario envolvido
3. motivo - Motivo/infracao
4. descricao - Descricao detalhada
5. evidencias - Evidencias/provas
6. ocorrencia_vinculada - Vincular a ocorrencia (opcional)
7. medida_corretiva - Medida corretiva proposta
8. prazo - Prazo para cumprimento (se aplicavel)
9. confirmacao - Revisao e confirmacao

Author: Conecta PRO Team
Date: 2026-01-29
"""

from datetime import datetime, date
from typing import Any
from modules.ai.bartolo.wizards.base_wizard import (
    BaseWizard, WizardStep, StepType
)


class DisciplinarWizard(BaseWizard):
    """Wizard para criacao de medida disciplinar."""

    def get_wizard_type(self) -> str:
        return "medida_disciplinar"

    def get_wizard_name(self) -> str:
        return "Medida Disciplinar"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a registrar uma medida disciplinar, "
            "coletando todas as informacoes necessarias e validando "
            "conforme a CLT."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # === Step 1: Tipo da Acao ===
            WizardStep(
                id="tipo_acao",
                name="Tipo de Medida",
                description="Tipo da medida disciplinar conforme CLT",
                step_type=StepType.CHOICE,
                question="Qual o tipo de medida disciplinar a ser aplicada?",
                required=True,
                options=[
                    "Advertencia Verbal",
                    "Advertencia Escrita",
                    "Suspensao",
                    "Demissao por Justa Causa",
                ],
                help_text=(
                    "Progressao recomendada: Advertencia Verbal -> "
                    "Advertencia Escrita -> Suspensao -> Justa Causa. "
                    "O tipo deve ser proporcional a gravidade da infracao."
                ),
            ),

            # === Step 2: Funcionario ===
            WizardStep(
                id="funcionario",
                name="Funcionario",
                description="Identificacao do funcionario envolvido",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome completo do funcionario envolvido?",
                required=True,
                validation_rules={"min_length": 3, "max_length": 255},
                help_text="Informe o nome completo conforme registro no sistema.",
            ),

            # === Step 3: Motivo/Infracao ===
            WizardStep(
                id="motivo",
                name="Motivo/Infracao",
                description="Categoria do motivo da medida disciplinar",
                step_type=StepType.CHOICE,
                question="Qual a categoria do motivo/infracao?",
                required=True,
                options=[
                    "Falta Injustificada",
                    "Atraso Recorrente",
                    "Insubordinacao",
                    "Indisciplina",
                    "Dano ao Patrimonio",
                    "Negligencia",
                    "Embriaguez em Servico",
                    "Abandono de Emprego",
                    "Ato de Improbidade",
                    "Violacao de Segredo",
                    "Ofensa Fisica",
                    "Ofensa Moral",
                    "Outros",
                ],
                help_text=(
                    "Categorias baseadas no Art. 482 da CLT. "
                    "Selecione a categoria mais adequada para a infracao."
                ),
            ),

            # === Step 4: Descricao Detalhada ===
            WizardStep(
                id="descricao",
                name="Descricao Detalhada",
                description="Descricao completa da ocorrencia que motivou a medida",
                step_type=StepType.TEXT_INPUT,
                question=(
                    "Descreva detalhadamente a ocorrencia que motivou a medida. "
                    "Inclua data, hora, local e o que aconteceu."
                ),
                required=True,
                validation_rules={"min_length": 20, "max_length": 5000},
                help_text=(
                    "Seja o mais detalhado possivel. Uma descricao completa "
                    "e fundamental para a validade juridica da medida. "
                    "Exemplo: 'No dia 20/01/2026, o funcionario nao compareceu "
                    "ao posto de trabalho (Condominio Solar) no turno das 07h "
                    "as 19h, sem apresentar justificativa ou atestado medico.'"
                ),
            ),

            # === Step 5: Evidencias ===
            WizardStep(
                id="evidencias",
                name="Evidencias/Provas",
                description="Evidencias que comprovam a infracao",
                step_type=StepType.TEXT_INPUT,
                question=(
                    "Quais evidencias comprovam a infracao? "
                    "(relatorios, registros de ponto, depoimentos, cameras, etc)"
                ),
                required=True,
                validation_rules={"min_length": 5, "max_length": 2000},
                help_text=(
                    "Liste todas as evidencias disponiveis. "
                    "Exemplos: registro de ponto, relatorio de ronda, "
                    "imagens de cameras, depoimento de testemunhas, "
                    "boletim de ocorrencia, etc."
                ),
            ),

            # === Step 6: Ocorrencia Vinculada (Opcional) ===
            WizardStep(
                id="ocorrencia_vinculada",
                name="Ocorrencia Vinculada",
                description="Vincular a uma ocorrencia existente no sistema",
                step_type=StepType.TEXT_INPUT,
                question=(
                    "Deseja vincular a uma ocorrencia existente? "
                    "Informe o codigo da ocorrencia ou 'nao' para pular."
                ),
                required=False,
                help_text=(
                    "Se a medida disciplinar esta relacionada a uma "
                    "ocorrencia registrada no sistema, informe o codigo. "
                    "Exemplo: OC-2026-00001. Digite 'nao' para pular."
                ),
            ),

            # === Step 7: Medida Corretiva ===
            WizardStep(
                id="medida_corretiva",
                name="Medida Corretiva",
                description="Medida corretiva proposta para o funcionario",
                step_type=StepType.TEXT_INPUT,
                question=(
                    "Qual a medida corretiva proposta? "
                    "O que o funcionario deve fazer para evitar reincidencia?"
                ),
                required=True,
                validation_rules={"min_length": 5, "max_length": 1000},
                help_text=(
                    "A medida corretiva complementa a punitiva e "
                    "demonstra carater educativo. Exemplos: "
                    "reciclagem de treinamento, acompanhamento pelo "
                    "supervisor, plano de melhoria de conduta, etc."
                ),
            ),

            # === Step 8: Prazo (Condicional - apenas para suspensao) ===
            WizardStep(
                id="prazo",
                name="Prazo/Dias",
                description="Prazo para cumprimento ou dias de suspensao",
                step_type=StepType.NUMBER_INPUT,
                question=(
                    "Informe o prazo em dias. "
                    "Para suspensao: numero de dias (max 30 CLT). "
                    "Para outras medidas: prazo para cumprimento da medida corretiva."
                ),
                required=False,
                validation_rules={"min_value": 1, "max_value": 30},
                help_text=(
                    "Para suspensao, o limite maximo e de 30 dias "
                    "conforme CLT Art. 474. Para advertencias, informe "
                    "o prazo para a medida corretiva. "
                    "Digite '0' ou 'pular' se nao aplicavel."
                ),
                skip_condition=lambda data: data.get("tipo_acao") not in [
                    "Suspensao", "3", "suspensao"
                ],
            ),

            # === Step 9: Confirmacao ===
            WizardStep(
                id="confirmacao",
                name="Revisao e Confirmacao",
                description="Revisao final dos dados e confirmacao",
                step_type=StepType.CONFIRMATION,
                question="Deseja confirmar a criacao desta medida disciplinar?",
                required=True,
                options=["Sim, criar medida", "Nao, voltar e editar"],
                help_text=(
                    "Revise todos os dados acima. Apos a confirmacao, "
                    "a medida sera criada no status 'Rascunho' e "
                    "encaminhada para aprovacao do supervisor."
                ),
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da criacao de medida disciplinar."""

        # Mapear tipo de acao para enum
        tipo_map = {
            "Advertencia Verbal": "advertencia_verbal",
            "Advertencia Escrita": "advertencia_escrita",
            "Suspensao": "suspensao",
            "Demissao por Justa Causa": "demissao_justa_causa",
        }

        # Mapear motivo para enum
        motivo_map = {
            "Falta Injustificada": "falta",
            "Atraso Recorrente": "atraso",
            "Insubordinacao": "insubordinacao",
            "Indisciplina": "indisciplina",
            "Dano ao Patrimonio": "dano_patrimonio",
            "Negligencia": "negligencia",
            "Embriaguez em Servico": "embriaguez",
            "Abandono de Emprego": "abandono_emprego",
            "Ato de Improbidade": "ato_improbidade",
            "Violacao de Segredo": "violacao_segredo",
            "Ofensa Fisica": "ofensa_fisica",
            "Ofensa Moral": "ofensa_moral",
            "Outros": "outros",
        }

        tipo_acao = data.get("tipo_acao", "")
        action_type = tipo_map.get(tipo_acao, "advertencia_escrita")
        motivo = data.get("motivo", "")
        reason_category = motivo_map.get(motivo, "outros")

        # Ocorrencia vinculada
        ocorrencia = data.get("ocorrencia_vinculada", "")
        if ocorrencia and ocorrencia.lower() in ["nao", "n", "nenhuma", "pular", "-", ""]:
            ocorrencia = None

        # Prazo
        prazo = data.get("prazo")
        suspension_days = None
        if action_type == "suspensao" and prazo:
            try:
                suspension_days = int(float(prazo))
            except (ValueError, TypeError):
                suspension_days = None

        result = {
            "medida_disciplinar": {
                "tipo_acao": tipo_acao,
                "action_type": action_type,
                "funcionario": data.get("funcionario"),
                "motivo": motivo,
                "reason_category": reason_category,
                "descricao": data.get("descricao"),
                "evidencias": data.get("evidencias"),
                "ocorrencia_vinculada": ocorrencia,
                "medida_corretiva": data.get("medida_corretiva"),
                "prazo_dias": suspension_days,
                "incident_date": date.today().isoformat(),
            },
            "action_data": {
                "action_type": action_type,
                "employee_name": data.get("funcionario"),
                "reason_category": reason_category,
                "reason_description": data.get("descricao"),
                "incident_date": date.today().isoformat(),
                "suspension_days": suspension_days,
                "requires_approval": True,
            },
            "proximos_passos": self._generate_next_steps(action_type, data),
            "alertas": self._generate_alerts(data),
        }

        return result

    def _generate_next_steps(self, action_type: str, data: dict) -> list:
        """Gera lista de proximos passos apos criacao."""
        steps = [
            "Medida sera criada no status 'Rascunho'",
            "Submeter para aprovacao do supervisor",
        ]

        if action_type in ["advertencia_escrita", "suspensao", "demissao_justa_causa"]:
            steps.append("Gerar documento a partir do template")
            steps.append("Coletar assinatura do funcionario")
            steps.append("Coletar assinatura do supervisor")
            steps.append("Coletar assinatura do RH")

        if action_type == "suspensao":
            steps.append("Registrar afastamento no DP")

        if action_type == "demissao_justa_causa":
            steps.append("Processar rescisao contratual")
            steps.append("Enviar evento S-2299 ao eSocial")

        steps.append("Arquivar no prontuario do funcionario")

        return steps

    def _generate_alerts(self, data: dict) -> list:
        """Gera alertas baseados nos dados coletados."""
        alerts = []

        tipo_acao = data.get("tipo_acao", "")

        # Alerta de suspensao
        if tipo_acao == "Suspensao":
            prazo = data.get("prazo")
            if prazo:
                try:
                    dias = int(float(prazo))
                    if dias > 30:
                        alerts.append({
                            "tipo": "error",
                            "mensagem": f"Suspensao de {dias} dias excede limite de 30 dias (CLT Art. 474)",
                        })
                    elif dias > 15:
                        alerts.append({
                            "tipo": "warning",
                            "mensagem": f"Suspensao de {dias} dias e longa. Verifique proporcionalidade.",
                        })
                except (ValueError, TypeError):
                    pass

        # Alerta de justa causa
        if tipo_acao == "Demissao por Justa Causa":
            alerts.append({
                "tipo": "warning",
                "mensagem": (
                    "Demissao por justa causa requer comprovacao robusta. "
                    "Verifique se ha historico de medidas previas e evidencias solidas."
                ),
            })

        # Alerta de descricao curta
        descricao = data.get("descricao", "")
        if descricao and len(descricao) < 50:
            alerts.append({
                "tipo": "warning",
                "mensagem": (
                    "Descricao muito curta. Uma descricao detalhada "
                    "e fundamental para a validade juridica da medida."
                ),
            })

        # Alerta de evidencias
        evidencias = data.get("evidencias", "")
        if evidencias and len(evidencias) < 20:
            alerts.append({
                "tipo": "warning",
                "mensagem": (
                    "Poucas evidencias informadas. Recomenda-se listar "
                    "todas as provas disponiveis (registros, depoimentos, imagens, etc)."
                ),
            })

        # Alerta de confirmacao negativa
        confirmacao = data.get("confirmacao")
        if confirmacao is False:
            alerts.append({
                "tipo": "info",
                "mensagem": "Criacao da medida cancelada pelo usuario.",
            })

        return alerts
