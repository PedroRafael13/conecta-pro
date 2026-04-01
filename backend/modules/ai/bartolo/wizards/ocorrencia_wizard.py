"""
Wizard de Registro de Ocorrencia Disciplinar.

Guia o usuario no processo de registro de uma ocorrencia,
coletando tipo, severidade, categoria, descricao e envolvidos.
"""

from datetime import datetime

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep


class OcorrenciaWizard(BaseWizard):
    """Wizard para registro de ocorrencia disciplinar."""

    def get_wizard_type(self) -> str:
        return "registro_ocorrencia"

    def get_wizard_name(self) -> str:
        return "Registro de Ocorrencia Disciplinar"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a registrar uma nova ocorrencia disciplinar, "
            "coletando todas as informacoes necessarias para o registro formal."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Tipo de ocorrencia
            WizardStep(
                id="tipo_ocorrencia",
                name="Tipo de Ocorrencia",
                description="Tipo da infracao/nao conformidade",
                step_type=StepType.CHOICE,
                question="Qual o tipo de ocorrencia?",
                required=True,
                options=[
                    "Abandono de Posto",
                    "Falta de Uniforme",
                    "Falta de EPI",
                    "Dormindo em Servico",
                    "Uso de Celular",
                    "Falta de Limpeza",
                    "Postura Inadequada",
                    "Atraso",
                    "Falta Injustificada",
                    "Nao Conformidade Documental",
                    "Embriaguez",
                    "Desrespeito",
                    "Negligencia",
                    "Insubordinacao",
                    "Outros",
                ],
                help_text="Selecione o tipo de infracao encontrada durante a fiscalizacao.",
            ),
            # 2. Severidade
            WizardStep(
                id="severidade",
                name="Severidade",
                description="Nivel de gravidade da infracao",
                step_type=StepType.CHOICE,
                question="Qual a severidade desta ocorrencia?",
                required=True,
                options=[
                    "Leve (Advertencia verbal)",
                    "Moderada (Advertencia escrita)",
                    "Grave (Suspensao)",
                    "Gravissima (Demissao por justa causa)",
                ],
                help_text=(
                    "A severidade define a acao disciplinar recomendada:\n"
                    "- Leve: Orientacao/advertencia verbal\n"
                    "- Moderada: Advertencia por escrito\n"
                    "- Grave: Suspensao de 1 a 30 dias\n"
                    "- Gravissima: Demissao por justa causa (art. 482 CLT)"
                ),
            ),
            # 3. Categoria
            WizardStep(
                id="categoria",
                name="Categoria",
                description="Categoria da infracao",
                step_type=StepType.CHOICE,
                question="Qual a categoria da ocorrencia?",
                required=True,
                options=[
                    "Disciplinar",
                    "Operacional",
                    "Seguranca do Trabalho",
                    "Conduta",
                    "Assiduidade",
                    "Outros",
                ],
                help_text="Classifique a area/natureza da infracao.",
            ),
            # 4. Titulo
            WizardStep(
                id="titulo",
                name="Titulo",
                description="Titulo descritivo da ocorrencia",
                step_type=StepType.TEXT_INPUT,
                question="Qual o titulo da ocorrencia? (descricao curta do ocorrido)",
                required=True,
                validation_rules={"min_length": 5, "max_length": 255},
                help_text="Ex: 'Abandono de posto - Portaria B', 'Uso de celular durante turno noturno'",
            ),
            # 5. Descricao
            WizardStep(
                id="descricao",
                name="Descricao Detalhada",
                description="Descricao completa do ocorrido",
                step_type=StepType.TEXT_INPUT,
                question="Descreva detalhadamente o que foi encontrado/observado:",
                required=True,
                validation_rules={"min_length": 10, "max_length": 2000},
                help_text=(
                    "Inclua: o que aconteceu, quando, circunstancias, "
                    "evidencias observadas. Quanto mais detalhado, melhor."
                ),
            ),
            # 6. Funcionario
            WizardStep(
                id="funcionario",
                name="Funcionario Envolvido",
                description="ID ou nome do funcionario que cometeu a infracao",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome ou ID do funcionario envolvido?",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text="Informe o nome completo ou o ID do funcionario no sistema.",
            ),
            # 7. Posto
            WizardStep(
                id="posto",
                name="Posto de Trabalho",
                description="Local onde ocorreu a infracao",
                step_type=StepType.TEXT_INPUT,
                question="Em qual posto/local ocorreu? (nome ou codigo do posto)",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text="Ex: 'POST-001', 'Portaria Principal', 'Guarita Norte'",
            ),
            # 8. Testemunhas (opcional)
            WizardStep(
                id="testemunhas",
                name="Testemunhas",
                description="Testemunhas do ocorrido",
                step_type=StepType.TEXT_INPUT,
                question="Ha testemunhas? Se sim, informe os nomes. (ou digite 'nao' para pular)",
                required=False,
                help_text="Liste os nomes das pessoas que presenciaram o fato. Opcional.",
            ),
            # 9. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.CONFIRMATION,
                question="Os dados acima estao corretos? Deseja registrar esta ocorrencia?",
                required=True,
                options=["Sim, registrar", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar o registro.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final do registro de ocorrencia."""
        # Mapear opcoes para enums do model
        tipo_map = {
            "Abandono de Posto": "abandono_posto",
            "Falta de Uniforme": "falta_uniforme",
            "Falta de EPI": "falta_epi",
            "Dormindo em Servico": "dormindo_servico",
            "Uso de Celular": "uso_celular",
            "Falta de Limpeza": "falta_limpeza",
            "Postura Inadequada": "postura_inadequada",
            "Atraso": "atraso",
            "Falta Injustificada": "falta_injustificada",
            "Nao Conformidade Documental": "nao_conformidade_documental",
            "Embriaguez": "embriaguez",
            "Desrespeito": "desrespeito",
            "Negligencia": "negligencia",
            "Insubordinacao": "insubordinacao",
            "Outros": "outros",
        }

        severidade_map = {
            "Leve (Advertencia verbal)": "leve",
            "Moderada (Advertencia escrita)": "moderada",
            "Grave (Suspensao)": "grave",
            "Gravissima (Demissao por justa causa)": "gravissima",
        }

        categoria_map = {
            "Disciplinar": "disciplinar",
            "Operacional": "operacional",
            "Seguranca do Trabalho": "seguranca_trabalho",
            "Conduta": "conduta",
            "Assiduidade": "assiduidade",
            "Outros": "outros",
        }

        tipo_valor = tipo_map.get(data.get("tipo_ocorrencia", ""), "outros")
        severidade_valor = severidade_map.get(data.get("severidade", ""), "leve")
        categoria_valor = categoria_map.get(data.get("categoria", ""), "outros")

        # Tratar testemunhas
        testemunhas = data.get("testemunhas", "")
        if testemunhas and testemunhas.lower() in ("nao", "n", "nenhuma", "sem", "-", ""):
            testemunhas = None

        # Definir acao corretiva recomendada pela severidade
        acoes_recomendadas = {
            "leve": "Advertencia verbal com orientacao",
            "moderada": "Advertencia por escrito",
            "grave": "Suspensao disciplinar (1-30 dias)",
            "gravissima": "Demissao por justa causa (art. 482 CLT)",
        }

        return {
            "ocorrencia": {
                "titulo": data.get("titulo"),
                "descricao": data.get("descricao"),
                "tipo": tipo_valor,
                "severidade": severidade_valor,
                "categoria": categoria_valor,
                "funcionario": data.get("funcionario"),
                "posto": data.get("posto"),
                "testemunhas": testemunhas,
                "data_ocorrencia": datetime.utcnow().isoformat(),
            },
            "acao_recomendada": acoes_recomendadas.get(severidade_valor, "A definir"),
            "proximos_passos": self._generate_next_steps(severidade_valor),
            "alertas": self._generate_alerts(data, severidade_valor),
        }

    def _generate_next_steps(self, severidade: str) -> list:
        """Gera proximos passos baseados na severidade."""
        steps = [
            "Registrar ocorrencia no sistema",
            "Notificar funcionario envolvido",
            "Notificar gestor responsavel do posto",
        ]

        if severidade in ("leve", "moderada"):
            steps.extend(
                [
                    "Agendar conversa com funcionario",
                    "Documentar advertencia",
                    "Atualizar prontuario disciplinar",
                ]
            )
        elif severidade == "grave":
            steps.extend(
                [
                    "Emitir notificacao formal de suspensao",
                    "Notificar RH para providencias",
                    "Agendar substituto para periodo de suspensao",
                    "Documentar no prontuario disciplinar",
                    "Avaliar historico de reincidencia",
                ]
            )
        elif severidade == "gravissima":
            steps.extend(
                [
                    "Notificar RH e Juridico IMEDIATAMENTE",
                    "Documentar todas as evidencias",
                    "Coletar depoimento de testemunhas",
                    "Avaliar enquadramento no art. 482 CLT",
                    "Preparar documentacao para desligamento",
                    "Agendar substituto imediato",
                ]
            )

        return steps

    def _generate_alerts(self, data: dict, severidade: str) -> list:
        """Gera alertas baseados nos dados."""
        alerts = []

        if severidade == "gravissima":
            alerts.append(
                {
                    "tipo": "error",
                    "mensagem": (
                        "GRAVISSIMA - Requer acao IMEDIATA. "
                        "Acionar RH e Juridico para avaliar demissao por justa causa."
                    ),
                }
            )

        if severidade == "grave":
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": (
                        "GRAVE - Requer suspensao disciplinar. "
                        "Verificar historico do funcionario antes de definir dias de suspensao."
                    ),
                }
            )

        if not data.get("testemunhas") or (
            data.get("testemunhas", "").lower() in ("nao", "n", "nenhuma", "sem", "-", "")
        ):
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Sem testemunhas registradas. "
                        "Recomenda-se buscar evidencias adicionais (cameras, registros de acesso)."
                    ),
                }
            )

        # Verificar tipos que exigem atencao especial
        tipos_criticos = {
            "Embriaguez": "Embriaguez em servico e falta grave (art. 482 CLT). Documentar com teste/evidencia.",
            "Abandono de Posto": "Abandono de posto pode configurar falta grave. Verificar tempo de ausencia.",
            "Dormindo em Servico": "Dormir em servico compromete a seguranca. Avaliar reincidencia.",
        }

        tipo_ocorrencia = data.get("tipo_ocorrencia", "")
        if tipo_ocorrencia in tipos_criticos:
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": tipos_criticos[tipo_ocorrencia],
                }
            )

        return alerts
