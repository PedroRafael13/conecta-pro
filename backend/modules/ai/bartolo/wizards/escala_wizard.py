"""
Wizard de Criacao de Escala.

Guia o usuario no processo de criacao de uma escala mensal,
coletando posto, mes, tipo de escala, funcionarios e turnos.
"""

from datetime import date, datetime

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, StepType, WizardStep


class EscalaWizard(BaseWizard):
    """Wizard para criacao guiada de escala."""

    def get_wizard_type(self) -> str:
        return "escala"

    def get_wizard_name(self) -> str:
        return "Criacao de Escala"

    def get_wizard_description(self) -> str:
        return (
            "Vou te ajudar a criar uma nova escala de trabalho, "
            "coletando todas as informacoes necessarias como posto, "
            "periodo, funcionarios e turnos."
        )

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # 1. Posto
            WizardStep(
                id="posto",
                name="Posto de Trabalho",
                description="Posto para o qual a escala sera criada",
                step_type=StepType.TEXT_INPUT,
                question="Para qual posto deseja criar a escala? (nome ou codigo)",
                required=True,
                validation_rules={"min_length": 2, "max_length": 200},
                help_text="Informe o nome ou codigo do posto. Ex: 'POST-001', 'Portaria Principal'",
            ),
            # 2. Mes/Ano
            WizardStep(
                id="mes_ano",
                name="Mes e Ano",
                description="Periodo da escala (mes/ano)",
                step_type=StepType.TEXT_INPUT,
                question="Para qual mes e ano? (ex: 02/2026, fevereiro 2026)",
                required=True,
                validation_rules={"min_length": 4, "max_length": 30},
                help_text="Informe o mes e ano da escala. Formato: MM/AAAA ou nome do mes + ano.",
            ),
            # 3. Tipo de escala
            WizardStep(
                id="tipo_escala",
                name="Tipo de Escala",
                description="Modelo/tipo da escala de trabalho",
                step_type=StepType.CHOICE,
                question="Qual o tipo de escala?",
                required=True,
                options=[
                    "12x36 (12h trabalho, 36h descanso)",
                    "6x1 (6 dias trabalho, 1 folga)",
                    "5x2 (segunda a sexta)",
                    "5x1 (5 dias trabalho, 1 folga)",
                    "24x72 (24h trabalho, 72h descanso)",
                    "Personalizada",
                ],
                help_text=(
                    "Tipos de escala:\n"
                    "- 12x36: Comum em vigilancia (turno de 12h)\n"
                    "- 6x1: Trabalha 6, folga 1 (CLT padrao)\n"
                    "- 5x2: Seg a Sex com sabado/domingo de folga\n"
                    "- 5x1: Trabalha 5, folga 1\n"
                    "- 24x72: Turno de 24h com 72h de descanso\n"
                    "- Personalizada: Definir manualmente"
                ),
            ),
            # 4. Turno
            WizardStep(
                id="turno",
                name="Turno",
                description="Horario do turno de trabalho",
                step_type=StepType.CHOICE,
                question="Qual o turno de trabalho?",
                required=True,
                options=[
                    "Diurno (06:00 - 18:00)",
                    "Noturno (18:00 - 06:00)",
                    "Matutino (06:00 - 14:00)",
                    "Vespertino (14:00 - 22:00)",
                    "Madrugada (22:00 - 06:00)",
                    "Comercial (08:00 - 17:00)",
                    "Personalizado",
                ],
                help_text="Selecione o turno de trabalho ou 'Personalizado' para definir horarios.",
            ),
            # 5. Horario personalizado (condicional)
            WizardStep(
                id="horario_personalizado",
                name="Horario Personalizado",
                description="Horarios de inicio e fim do turno",
                step_type=StepType.TEXT_INPUT,
                question="Informe o horario de inicio e fim (ex: 07:00 - 19:00)",
                required=False,
                validation_rules={"min_length": 5, "max_length": 30},
                help_text="Formato: HH:MM - HH:MM (ex: 07:00 - 19:00)",
                skip_condition=lambda data: data.get("turno") != "Personalizado",
            ),
            # 6. Funcionarios
            WizardStep(
                id="funcionarios",
                name="Funcionarios",
                description="Funcionarios a serem escalados",
                step_type=StepType.TEXT_INPUT,
                question=(
                    "Quais funcionarios devem ser incluidos na escala?\n"
                    "(Nomes ou IDs separados por virgula, ou 'todos' para o efetivo do posto)"
                ),
                required=True,
                validation_rules={"min_length": 2, "max_length": 1000},
                help_text=(
                    "Informe os nomes/IDs dos funcionarios ou:\n"
                    "- 'todos' para incluir todo o efetivo do posto\n"
                    "- 'disponíveis' para incluir apenas os disponíveis"
                ),
            ),
            # 7. Observacoes
            WizardStep(
                id="observacoes",
                name="Observacoes",
                description="Observacoes adicionais para a escala",
                step_type=StepType.TEXT_INPUT,
                question="Alguma observacao adicional? (ou 'nao' para pular)",
                required=False,
                help_text=(
                    "Informe restricoes, preferencias ou observacoes.\n"
                    "Ex: 'Joao nao pode trabalhar aos domingos', "
                    "'Priorizar escala equilibrada'"
                ),
            ),
            # 8. Confirmacao
            WizardStep(
                id="confirmacao",
                name="Confirmacao",
                description="Revisao e confirmacao dos dados",
                step_type=StepType.CONFIRMATION,
                question="Os dados estao corretos? Deseja criar esta escala?",
                required=True,
                options=["Sim, criar escala", "Nao, voltar e corrigir"],
                help_text="Revise todos os dados antes de confirmar a criacao.",
            ),
        ]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final da criacao de escala."""
        # Parsear mes/ano
        mes_ano = data.get("mes_ano", "")
        mes, ano = self._parse_mes_ano(mes_ano)

        # Parsear tipo de escala
        tipo_map = {
            "12x36 (12h trabalho, 36h descanso)": "12x36",
            "6x1 (6 dias trabalho, 1 folga)": "6x1",
            "5x2 (segunda a sexta)": "5x2",
            "5x1 (5 dias trabalho, 1 folga)": "5x1",
            "24x72 (24h trabalho, 72h descanso)": "24x72",
            "Personalizada": "personalizada",
        }

        turno_map = {
            "Diurno (06:00 - 18:00)": {"nome": "diurno", "inicio": "06:00", "fim": "18:00"},
            "Noturno (18:00 - 06:00)": {"nome": "noturno", "inicio": "18:00", "fim": "06:00"},
            "Matutino (06:00 - 14:00)": {"nome": "matutino", "inicio": "06:00", "fim": "14:00"},
            "Vespertino (14:00 - 22:00)": {"nome": "vespertino", "inicio": "14:00", "fim": "22:00"},
            "Madrugada (22:00 - 06:00)": {"nome": "madrugada", "inicio": "22:00", "fim": "06:00"},
            "Comercial (08:00 - 17:00)": {"nome": "comercial", "inicio": "08:00", "fim": "17:00"},
            "Personalizado": {"nome": "personalizado", "inicio": "", "fim": ""},
        }

        tipo_escala = tipo_map.get(data.get("tipo_escala", ""), "personalizada")
        turno_info = turno_map.get(data.get("turno", ""), {"nome": "personalizado", "inicio": "", "fim": ""})

        # Se turno personalizado, usar horario informado
        if turno_info["nome"] == "personalizado" and data.get("horario_personalizado"):
            horario = data["horario_personalizado"]
            partes = horario.replace(" ", "").split("-")
            if len(partes) == 2:
                turno_info["inicio"] = partes[0].strip()
                turno_info["fim"] = partes[1].strip()

        # Parsear funcionarios
        funcionarios_raw = data.get("funcionarios", "")
        if funcionarios_raw.lower().strip() in ("todos", "all"):
            funcionarios = {"tipo": "todos"}
        elif funcionarios_raw.lower().strip() in ("disponiveis", "disponíveis"):
            funcionarios = {"tipo": "disponiveis"}
        else:
            lista = [f.strip() for f in funcionarios_raw.split(",") if f.strip()]
            funcionarios = {"tipo": "lista", "ids": lista}

        # Observacoes
        obs = data.get("observacoes", "")
        if obs and obs.lower() in ("nao", "n", "nenhuma", "sem", "-", ""):
            obs = None

        return {
            "escala": {
                "posto": data.get("posto"),
                "mes": mes,
                "ano": ano,
                "tipo_escala": tipo_escala,
                "turno": turno_info,
                "funcionarios": funcionarios,
                "observacoes": obs,
                "data_criacao": datetime.utcnow().isoformat(),
            },
            "proximos_passos": [
                "Gerar escala automaticamente com base nos parametros",
                "Revisar e ajustar manualmente se necessario",
                "Publicar escala para os funcionarios",
                "Notificar equipe sobre nova escala",
            ],
            "alertas": self._generate_alerts(data, tipo_escala),
        }

    def _parse_mes_ano(self, mes_ano: str) -> tuple:
        """Parseia mes/ano da string."""
        import re

        # Formato MM/AAAA
        match = re.search(r"(\d{1,2})\s*/\s*(\d{4})", mes_ano)
        if match:
            return int(match.group(1)), int(match.group(2))

        # Formato nome do mes + ano
        meses = {
            "janeiro": 1,
            "fevereiro": 2,
            "marco": 3,
            "março": 3,
            "abril": 4,
            "maio": 5,
            "junho": 6,
            "julho": 7,
            "agosto": 8,
            "setembro": 9,
            "outubro": 10,
            "novembro": 11,
            "dezembro": 12,
        }
        mes_lower = mes_ano.lower()
        for nome, num in meses.items():
            if nome in mes_lower:
                year_match = re.search(r"(\d{4})", mes_ano)
                ano = int(year_match.group(1)) if year_match else date.today().year
                return num, ano

        return date.today().month, date.today().year

    def _generate_alerts(self, data: dict, tipo_escala: str) -> list:
        """Gera alertas baseados nos dados da escala."""
        alerts = []

        if tipo_escala == "12x36":
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Escala 12x36: Verificar CLT art. 59-A. Jornada de 12h seguidas exige acordo coletivo."
                    ),
                }
            )

        if tipo_escala == "24x72":
            alerts.append(
                {
                    "tipo": "warning",
                    "mensagem": (
                        "Escala 24x72: Verificar conformidade com convencao coletiva. "
                        "Turno de 24h requer atencao especial a saude do trabalhador."
                    ),
                }
            )

        turno = data.get("turno", "")
        if "Noturno" in turno or "Madrugada" in turno:
            alerts.append(
                {
                    "tipo": "info",
                    "mensagem": (
                        "Turno noturno: Adicional noturno obrigatorio (CLT art. 73). Hora noturna = 52min30s."
                    ),
                }
            )

        return alerts
