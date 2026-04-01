"""
Wizard de Criacao de Posto de Trabalho.

Guia o usuario no processo de criacao/cadastro de um novo posto,
coletando nome, tipo, endereco, turno, requisitos e armamento.
"""

from datetime import datetime

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep


class PostoWizard(BaseWizard):
    """Wizard para criacao guiada de posto de trabalho."""

    def get_wizard_type(self) -> str:
        return "posto"

    def get_wizard_name(self) -> str:
        return "Criacao de Posto de Trabalho"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a cadastrar um novo posto de trabalho, "
            "coletando todas as informacoes necessarias como tipo, "
            "endereco, requisitos e configuracoes de turno."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Nome do posto
            WizardStep(
                id="nome",
                name="Nome do Posto",
                description="Nome identificador do posto de trabalho",
                step_type=StepType.TEXT_INPUT,
                question="Qual o nome do posto? (ex: Portaria Principal, Guarita Norte)",
                required=True,
                validation_rules={"min_length": 3, "max_length": 200},
                help_text="Informe um nome descritivo para o posto.",
            ),
            # 2. Tipo do posto
            WizardStep(
                id="tipo",
                name="Tipo do Posto",
                description="Tipo/categoria do posto",
                step_type=StepType.CHOICE,
                question="Qual o tipo do posto?",
                required=True,
                options=[
                    "Portaria",
                    "Guarita",
                    "Recepcao",
                    "Ronda Motorizada",
                    "Ronda a Pe",
                    "CFTV (Monitoramento)",
                    "Limpeza",
                    "Manutencao",
                    "Administrativo",
                    "Outro",
                ],
                help_text="Selecione o tipo de servico prestado no posto.",
            ),
            # 3. Endereco/Localizacao
            WizardStep(
                id="endereco",
                name="Endereco/Localizacao",
                description="Endereco ou localizacao do posto",
                step_type=StepType.TEXT_INPUT,
                question="Qual o endereco ou localizacao do posto?",
                required=True,
                validation_rules={"min_length": 5, "max_length": 500},
                help_text="Informe o endereco completo ou referencia de localizacao.",
            ),
            # 4. Cliente/Condominio
            WizardStep(
                id="cliente",
                name="Cliente/Condominio",
                description="Cliente ou condominio ao qual o posto pertence",
                step_type=StepType.TEXT_INPUT,
                question="Qual o cliente ou condominio? (nome ou ID)",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text="Informe o nome do cliente/condominio ou seu ID no sistema.",
            ),
            # 5. Turno
            WizardStep(
                id="turno",
                name="Turno de Operacao",
                description="Horarios de funcionamento do posto",
                step_type=StepType.CHOICE,
                question="Qual o regime de turno do posto?",
                required=True,
                options=[
                    "24 horas (diurno + noturno)",
                    "Diurno (06:00 - 18:00)",
                    "Noturno (18:00 - 06:00)",
                    "Comercial (08:00 - 17:00)",
                    "12 horas (diurno)",
                    "12 horas (noturno)",
                    "Personalizado",
                ],
                help_text="Selecione o regime de horario do posto.",
            ),
            # 6. Efetivo minimo
            WizardStep(
                id="efetivo_minimo",
                name="Efetivo Minimo",
                description="Quantidade minima de funcionarios por turno",
                step_type=StepType.NUMBER_INPUT,
                question="Qual o efetivo minimo por turno? (numero de funcionarios)",
                required=True,
                validation_rules={"min_value": 1, "max_value": 50},
                help_text="Informe a quantidade minima de funcionarios necessarios por turno.",
            ),
            # 7. Requisitos
            WizardStep(
                id="requisitos",
                name="Requisitos do Posto",
                description="Requisitos e qualificacoes necessarias",
                step_type=StepType.MULTI_CHOICE,
                question="Quais os requisitos do posto? (selecione todos que se aplicam)",
                required=False,
                options=[
                    "Vigilancia Armada",
                    "Curso de Reciclagem em dia",
                    "CNH (veiculo)",
                    "Curso de Brigadista",
                    "Treinamento CFTV",
                    "NR-35 (Trabalho em Altura)",
                    "NR-10 (Eletricidade)",
                    "Experiencia minima 1 ano",
                    "Nenhum requisito especial",
                ],
                help_text="Selecione os requisitos obrigatorios para trabalhar neste posto.",
            ),
            # 8. Armamento (condicional)
            WizardStep(
                id="armamento",
                name="Armamento",
                description="Tipo de armamento do posto",
                step_type=StepType.CHOICE,
                question="Qual o tipo de armamento?",
                required=False,
                options=[
                    "Revolver .38",
                    "Pistola .380",
                    "Espingarda calibre 12",
                    "Desarmado (apenas colete)",
                    "Nao se aplica",
                ],
                help_text="Selecione o armamento autorizado para o posto.",
                skip_condition=lambda data: "Vigilancia Armada" not in (data.get("requisitos") or ""),
            ),
            # 9. Observacoes
            WizardStep(
                id="observacoes",
                name="Observacoes",
                description="Observacoes e instrucoes adicionais",
                step_type=StepType.TEXT_INPUT,
                question="Alguma observacao adicional? (ou 'nao' para pular)",
                required=False,
                help_text="Instrucoes especiais, regras do posto, contatos de emergencia, etc.",
            ),
            # 10. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.CONFIRMATION,
                question="Os dados estao corretos? Deseja cadastrar este posto?",
                required=True,
                options=["Sim, cadastrar posto", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar o cadastro.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final do cadastro de posto."""
        # Mapear tipo
        tipo_map = {
            "Portaria": "portaria",
            "Guarita": "guarita",
            "Recepcao": "recepcao",
            "Ronda Motorizada": "ronda_motorizada",
            "Ronda a Pe": "ronda_pe",
            "CFTV (Monitoramento)": "cftv",
            "Limpeza": "limpeza",
            "Manutencao": "manutencao",
            "Administrativo": "administrativo",
            "Outro": "outro",
        }

        turno_map = {
            "24 horas (diurno + noturno)": "24h",
            "Diurno (06:00 - 18:00)": "diurno",
            "Noturno (18:00 - 06:00)": "noturno",
            "Comercial (08:00 - 17:00)": "comercial",
            "12 horas (diurno)": "12h_diurno",
            "12 horas (noturno)": "12h_noturno",
            "Personalizado": "personalizado",
        }

        tipo_valor = tipo_map.get(data.get("tipo", ""), "outro")
        turno_valor = turno_map.get(data.get("turno", ""), "personalizado")

        # Requisitos
        requisitos_raw = data.get("requisitos", "")
        if isinstance(requisitos_raw, str):
            requisitos = [r.strip() for r in requisitos_raw.split(",") if r.strip()]
        elif isinstance(requisitos_raw, list):
            requisitos = requisitos_raw
        else:
            requisitos = []

        # Armamento
        armamento = data.get("armamento")
        if armamento and armamento in ("Nao se aplica", "Desarmado (apenas colete)"):
            armamento_valor = None if armamento == "Nao se aplica" else "desarmado"
        elif armamento:
            armamento_map = {
                "Revolver .38": "revolver_38",
                "Pistola .380": "pistola_380",
                "Espingarda calibre 12": "espingarda_12",
            }
            armamento_valor = armamento_map.get(armamento, armamento)
        else:
            armamento_valor = None

        # Efetivo
        efetivo = data.get("efetivo_minimo", 1)
        if isinstance(efetivo, str):
            try:
                efetivo = int(float(efetivo))
            except ValueError:
                efetivo = 1

        # Observacoes
        obs = data.get("observacoes", "")
        if obs and obs.lower() in ("nao", "n", "nenhuma", "sem", "-", ""):
            obs = None

        # Verificar vigilancia armada
        armado = "Vigilancia Armada" in (requisitos_raw if isinstance(requisitos_raw, str) else str(requisitos_raw))

        return {
            "posto": {
                "nome": data.get("nome"),
                "tipo": tipo_valor,
                "endereco": data.get("endereco"),
                "cliente": data.get("cliente"),
                "turno": turno_valor,
                "efetivo_minimo": efetivo,
                "requisitos": requisitos,
                "armamento": armamento_valor,
                "armado": armado,
                "observacoes": obs,
                "data_criacao": datetime.utcnow().isoformat(),
                "status": "ativo",
            },
            "proximos_passos": self._generate_next_steps(tipo_valor, armado),
            "alertas": self._generate_alerts(data, tipo_valor, armado),
        }

    def _generate_next_steps(self, tipo: str, armado: bool) -> list:
        """Gera proximos passos apos cadastro."""
        steps = [
            "Cadastrar posto no sistema",
            "Definir efetivo e escala para o posto",
            "Alocar funcionarios ao posto",
        ]

        if armado:
            steps.extend(
                [
                    "Verificar documentacao de armamento (RA, CLCB)",
                    "Configurar controle de armamento no sistema",
                    "Registrar armas no livro de registro",
                ]
            )

        if tipo in ("cftv",):
            steps.append("Configurar equipamentos de CFTV e monitoramento")

        if tipo in ("ronda_motorizada",):
            steps.append("Cadastrar veiculo e rota de ronda")

        steps.extend(
            [
                "Configurar checklist de ronda (se aplicavel)",
                "Treinar equipe sobre procedimentos do posto",
            ]
        )

        return steps

    def _generate_alerts(self, data: dict, tipo: str, armado: bool) -> list:
        """Gera alertas baseados nos dados."""
        alerts = []

        if armado:
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": (
                        "Posto armado: Verificar se todos os vigilantes possuem "
                        "CNV (Certificado Nacional de Vigilante) valido e reciclagem em dia."
                    ),
                }
            )

        efetivo = data.get("efetivo_minimo", 1)
        if isinstance(efetivo, (int, float)) and efetivo >= 5:
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        f"Efetivo de {int(efetivo)} funcionarios por turno. "
                        "Considere incluir reservas tecnicas na escala."
                    ),
                }
            )

        if tipo == "portaria":
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Posto de portaria: Configurar controle de acesso (biometria, facial, cartao) se disponivel."
                    ),
                }
            )

        return alerts
