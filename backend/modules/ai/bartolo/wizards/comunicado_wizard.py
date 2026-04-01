"""
Wizard de Criacao de Comunicado.

Guia o usuario no processo de criacao de um comunicado,
coletando tipo, titulo, conteudo, prioridade e destinatarios.
"""

from datetime import datetime

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep


class ComunicadoWizard(BaseWizard):
    """Wizard para criacao guiada de comunicado."""

    def get_wizard_type(self) -> str:
        return "comunicado"

    def get_wizard_name(self) -> str:
        return "Criacao de Comunicado"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a criar um novo comunicado, "
            "coletando todas as informacoes necessarias como "
            "tipo, titulo, conteudo, prioridade e destinatarios."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Tipo do comunicado
            WizardStep(
                id="tipo",
                name="Tipo do Comunicado",
                description="Categoria do comunicado",
                step_type=StepType.CHOICE,
                question="Qual o tipo do comunicado?",
                required=True,
                options=[
                    "Informativo",
                    "Alerta",
                    "Procedimento",
                    "Escala",
                    "Treinamento",
                    "Politica",
                    "Urgente",
                    "Outro",
                ],
                help_text=(
                    "Tipos de comunicado:\n"
                    "- Informativo: Avisos gerais\n"
                    "- Alerta: Alertas de seguranca ou operacionais\n"
                    "- Procedimento: Novos procedimentos ou alteracoes\n"
                    "- Escala: Informacoes sobre escalas\n"
                    "- Treinamento: Convocacao ou info de treinamento\n"
                    "- Politica: Novas politicas internas\n"
                    "- Urgente: Comunicado urgente"
                ),
            ),
            # 2. Titulo
            WizardStep(
                id="titulo",
                name="Titulo",
                description="Titulo do comunicado",
                step_type=StepType.TEXT_INPUT,
                question="Qual o titulo do comunicado?",
                required=True,
                validation_rules={"min_length": 5, "max_length": 200},
                help_text="Informe um titulo claro e objetivo. Ex: 'Alteracao de procedimento de acesso'",
            ),
            # 3. Conteudo
            WizardStep(
                id="conteudo",
                name="Conteudo",
                description="Texto completo do comunicado",
                step_type=StepType.TEXT_INPUT,
                question="Qual o conteudo do comunicado? (texto completo)",
                required=True,
                validation_rules={"min_length": 10, "max_length": 5000},
                help_text="Escreva o conteudo completo do comunicado. Seja claro e objetivo.",
            ),
            # 4. Prioridade
            WizardStep(
                id="prioridade",
                name="Prioridade",
                description="Nivel de prioridade do comunicado",
                step_type=StepType.CHOICE,
                question="Qual a prioridade?",
                required=True,
                options=[
                    "Baixa",
                    "Normal",
                    "Alta",
                    "Urgente",
                ],
                help_text=(
                    "Prioridades:\n"
                    "- Baixa: Informacao complementar\n"
                    "- Normal: Comunicado padrao\n"
                    "- Alta: Requer atencao prioritaria\n"
                    "- Urgente: Notificacao push imediata"
                ),
            ),
            # 5. Destinatarios
            WizardStep(
                id="destinatarios",
                name="Destinatarios",
                description="Quem recebera o comunicado",
                step_type=StepType.CHOICE,
                question="Para quem sera enviado?",
                required=True,
                options=[
                    "Todos os funcionarios",
                    "Apenas supervisores/gestores",
                    "Posto especifico",
                    "Departamento especifico",
                    "Funcionario(s) especifico(s)",
                ],
                help_text="Selecione o grupo de destinatarios do comunicado.",
            ),
            # 6. Detalhe destinatarios (condicional)
            WizardStep(
                id="destinatarios_detalhe",
                name="Detalhe dos Destinatarios",
                description="Especificar quais postos, departamentos ou funcionarios",
                step_type=StepType.TEXT_INPUT,
                question="Especifique os destinatarios (nomes, IDs ou postos separados por virgula):",
                required=False,
                validation_rules={"min_length": 2, "max_length": 500},
                help_text="Informe os nomes, IDs ou postos separados por virgula.",
                skip_condition=lambda data: (
                    data.get("destinatarios")
                    in (
                        "Todos os funcionarios",
                        "Apenas supervisores/gestores",
                    )
                ),
            ),
            # 7. Requer confirmacao de leitura
            WizardStep(
                id="requer_confirmacao",
                name="Confirmacao de Leitura",
                description="Exigir confirmacao de leitura dos destinatarios",
                step_type=StepType.CHOICE,
                question="Exigir confirmacao de leitura?",
                required=True,
                options=[
                    "Sim",
                    "Nao",
                ],
                help_text=(
                    "Se 'Sim', os destinatarios deverao confirmar que leram o comunicado. "
                    "Recomendado para comunicados importantes."
                ),
            ),
            # 8. Publicacao
            WizardStep(
                id="publicacao",
                name="Publicacao",
                description="Quando publicar o comunicado",
                step_type=StepType.CHOICE,
                question="Quando deseja publicar?",
                required=True,
                options=[
                    "Publicar agora",
                    "Salvar como rascunho",
                    "Agendar publicacao",
                ],
                help_text="Escolha quando o comunicado sera publicado e enviado.",
            ),
            # 9. Data agendamento (condicional)
            WizardStep(
                id="data_agendamento",
                name="Data de Agendamento",
                description="Data e hora para publicacao agendada",
                step_type=StepType.TEXT_INPUT,
                question="Para qual data e hora agendar? (ex: 15/02/2026 09:00)",
                required=False,
                validation_rules={"min_length": 5, "max_length": 30},
                help_text="Formato: DD/MM/AAAA HH:MM",
                skip_condition=lambda data: data.get("publicacao") != "Agendar publicacao",
            ),
            # 10. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.CONFIRMATION,
                question="Os dados estao corretos? Deseja criar este comunicado?",
                required=True,
                options=["Sim, criar comunicado", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da criacao de comunicado."""
        # Mapear tipo
        tipo_map = {
            "Informativo": "informativo",
            "Alerta": "alerta",
            "Procedimento": "procedimento",
            "Escala": "escala",
            "Treinamento": "treinamento",
            "Politica": "politica",
            "Urgente": "urgente",
            "Outro": "outro",
        }

        prioridade_map = {
            "Baixa": "baixa",
            "Normal": "normal",
            "Alta": "alta",
            "Urgente": "urgente",
        }

        destinatarios_map = {
            "Todos os funcionarios": "all",
            "Apenas supervisores/gestores": "role",
            "Posto especifico": "post",
            "Departamento especifico": "department",
            "Funcionario(s) especifico(s)": "user",
        }

        tipo_valor = tipo_map.get(data.get("tipo", ""), "informativo")
        prioridade_valor = prioridade_map.get(data.get("prioridade", ""), "normal")
        dest_tipo = destinatarios_map.get(data.get("destinatarios", ""), "all")

        # Destinatarios especificos
        dest_detalhe = data.get("destinatarios_detalhe", "")
        dest_ids = []
        if dest_detalhe:
            dest_ids = [d.strip() for d in dest_detalhe.split(",") if d.strip()]

        # Roles para supervisores
        target_roles = []
        if dest_tipo == "role":
            target_roles = ["supervisor", "gestor", "admin", "coordenador"]

        # Confirmacao de leitura
        requer_ack = data.get("requer_confirmacao", "Nao")
        requer_ack_bool = requer_ack in ("Sim", "sim", "s", "S", True)

        # Publicacao
        pub_map = {
            "Publicar agora": "publish",
            "Salvar como rascunho": "draft",
            "Agendar publicacao": "schedule",
        }
        pub_action = pub_map.get(data.get("publicacao", ""), "draft")
        data_agendamento = data.get("data_agendamento") if pub_action == "schedule" else None

        # Status baseado na acao
        status_map = {
            "publish": "publicado",
            "draft": "rascunho",
            "schedule": "agendado",
        }

        return {
            "comunicado": {
                "titulo": data.get("titulo"),
                "conteudo": data.get("conteudo"),
                "tipo": tipo_valor,
                "prioridade": prioridade_valor,
                "target_type": dest_tipo,
                "target_ids": dest_ids if dest_ids else None,
                "target_roles": target_roles if target_roles else None,
                "requires_acknowledgment": requer_ack_bool,
                "status": status_map.get(pub_action, "rascunho"),
                "publish_action": pub_action,
                "schedule_at": data_agendamento,
                "data_criacao": datetime.utcnow().isoformat(),
            },
            "proximos_passos": self._generate_next_steps(pub_action, prioridade_valor),
            "alertas": self._generate_alerts(data, prioridade_valor, requer_ack_bool),
        }

    def _generate_next_steps(self, pub_action: str, prioridade: str) -> list:
        """Gera proximos passos."""
        steps = []

        if pub_action == "publish":
            steps.extend(
                [
                    "Comunicado sera publicado imediatamente",
                    "Destinatarios serao notificados",
                ]
            )
            if prioridade in ("alta", "urgente"):
                steps.append("Notificacao push sera enviada com prioridade")
        elif pub_action == "draft":
            steps.extend(
                [
                    "Comunicado salvo como rascunho",
                    "Revisar e editar antes de publicar",
                    "Publicar quando estiver pronto",
                ]
            )
        elif pub_action == "schedule":
            steps.extend(
                [
                    "Comunicado sera publicado na data agendada",
                    "Verificar se a data de agendamento esta correta",
                ]
            )

        steps.extend(
            [
                "Acompanhar metricas de leitura",
                "Verificar confirmacoes de leitura (se habilitado)",
            ]
        )

        return steps

    def _generate_alerts(self, data: dict, prioridade: str, requer_ack: bool) -> list:
        """Gera alertas."""
        alerts = []

        if prioridade == "urgente":
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": (
                        "Comunicado URGENTE: Notificacao push sera enviada imediatamente "
                        "a todos os destinatarios. Certifique-se do conteudo."
                    ),
                }
            )

        if not requer_ack and prioridade in ("alta", "urgente"):
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Comunicado de alta prioridade sem confirmacao de leitura. "
                        "Considere habilitar para garantir ciencia de todos."
                    ),
                }
            )

        dest = data.get("destinatarios", "")
        if dest == "Todos os funcionarios":
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": "Comunicado sera enviado para TODOS os funcionarios do sistema.",
                }
            )

        return alerts
