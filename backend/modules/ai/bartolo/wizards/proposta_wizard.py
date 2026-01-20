"""
Wizard de Proposta Comercial.

Guia o usuario passo a passo na criacao de uma proposta comercial,
calculando custos baseados na CCT SINDCOND 2026.
"""

from dataclasses import dataclass
from typing import Any, Optional
from modules.ai.bartolo.wizards.base_wizard import (
    BaseWizard, WizardStep, StepType, WizardResponse
)


# Tabela CCT SINDCOND 2026 - Pisos Salariais
CCT_PISOS_2026 = {
    "Porteiro": 1847.12,
    "Porteiro Lider": 2124.19,
    "Controlador de Acesso": 1847.12,
    "Vigia": 1724.51,
    "Vigilante": 2456.78,
    "Vigilante Lider": 2824.30,
    "Zelador": 1970.23,
    "Faxineiro": 1601.90,
    "Auxiliar de Limpeza": 1540.13,
    "Encarregado de Limpeza": 2247.30,
    "Jardineiro": 1724.51,
    "Piscineiro": 1847.12,
    "Eletricista": 2370.41,
    "Encanador": 2124.19,
    "Auxiliar de Manutencao": 1724.51,
    "Recepcionista": 1847.12,
    "Ascensorista": 1724.51,
    "Garagista": 1724.51,
    "Manobrista": 1847.12,
    "Copeira": 1601.90,
    "Sindico Profissional": 4500.00,
    "Gerente Predial": 3800.00,
    "Supervisor de Seguranca": 2824.30,
}

# Tipos de escala
ESCALAS = {
    "12x36 Diurno": {"horas_mes": 180, "adicional_noturno": False, "dsr": True},
    "12x36 Noturno": {"horas_mes": 180, "adicional_noturno": True, "dsr": True},
    "5x2 (44h)": {"horas_mes": 220, "adicional_noturno": False, "dsr": False},
    "6x1 (44h)": {"horas_mes": 220, "adicional_noturno": False, "dsr": False},
    "Comercial (8h)": {"horas_mes": 176, "adicional_noturno": False, "dsr": False},
}

# Encargos sociais aproximados
ENCARGOS_SOCIAIS = 0.72  # 72% sobre o salario


@dataclass
class PostoTrabalho:
    """Posto de trabalho para proposta."""
    cargo: str
    quantidade: int
    escala: str
    salario_base: float
    adicional_periculosidade: bool = False
    adicional_noturno: bool = False

    @property
    def salario_total(self) -> float:
        """Calcula salario com adicionais."""
        salario = self.salario_base
        if self.adicional_periculosidade:
            salario *= 1.30  # 30% periculosidade
        if self.adicional_noturno:
            salario *= 1.20  # 20% noturno
        return salario

    @property
    def custo_mensal_unitario(self) -> float:
        """Custo mensal por funcionario."""
        return self.salario_total * (1 + ENCARGOS_SOCIAIS)

    @property
    def custo_mensal_total(self) -> float:
        """Custo mensal total do posto."""
        return self.custo_mensal_unitario * self.quantidade


class PropostaComercialWizard(BaseWizard):
    """Wizard para criacao de proposta comercial."""

    def __init__(self, user_id: int, session_id: str):
        self.postos: list[PostoTrabalho] = []
        self.cliente_nome: str = ""
        self.tipo_servico: str = ""
        self.margem_lucro: float = 0.15  # 15% padrao
        self.custos_operacionais: float = 0.0
        super().__init__(user_id, session_id)

    def get_wizard_type(self) -> str:
        return "proposta_comercial"

    def get_wizard_name(self) -> str:
        return "Proposta Comercial"

    def get_wizard_description(self) -> str:
        return "Vou te ajudar a montar uma proposta comercial passo a passo, calculando todos os custos baseados na CCT SINDCOND 2026."

    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        self.steps = [
            # Passo 1: Cliente
            WizardStep(
                id="cliente",
                name="Cliente",
                description="Nome do cliente",
                step_type=StepType.TEXT_INPUT,
                question="Qual e o nome do cliente para esta proposta?",
                required=True,
                help_text="Informe o nome ou razao social do cliente.",
                validation_rules={"min_length": 3, "max_length": 200},
            ),

            # Passo 2: Tipo de Servico
            WizardStep(
                id="tipo_servico",
                name="Tipo de Servico",
                description="Tipo de servico a ser prestado",
                step_type=StepType.CHOICE,
                question="Qual o tipo de servico principal?",
                required=True,
                options=[
                    "Portaria e Controle de Acesso",
                    "Vigilancia Patrimonial",
                    "Limpeza e Conservacao",
                    "Manutencao Predial",
                    "Facilities Completo",
                ],
                help_text="Escolha o tipo de servico que melhor descreve a proposta.",
            ),

            # Passo 3: Cargo
            WizardStep(
                id="cargo",
                name="Cargo",
                description="Cargo do posto de trabalho",
                step_type=StepType.CHOICE,
                question="Qual o cargo para o posto de trabalho?",
                required=True,
                options=list(CCT_PISOS_2026.keys())[:10],  # Primeiros 10 cargos
                help_text="Escolha o cargo. O salario sera baseado na CCT SINDCOND 2026.",
            ),

            # Passo 4: Quantidade
            WizardStep(
                id="quantidade",
                name="Quantidade",
                description="Quantidade de funcionarios",
                step_type=StepType.NUMBER_INPUT,
                question="Quantos funcionarios neste cargo?",
                required=True,
                help_text="Informe a quantidade de funcionarios para este posto.",
                validation_rules={"min_value": 1, "max_value": 100},
            ),

            # Passo 5: Escala
            WizardStep(
                id="escala",
                name="Escala",
                description="Tipo de escala de trabalho",
                step_type=StepType.CHOICE,
                question="Qual a escala de trabalho?",
                required=True,
                options=list(ESCALAS.keys()),
                help_text="Escolha o regime de trabalho. Escalas noturnas incluem adicional de 20%.",
            ),

            # Passo 6: Periculosidade
            WizardStep(
                id="periculosidade",
                name="Periculosidade",
                description="Adicional de periculosidade",
                step_type=StepType.CONFIRMATION,
                question="O cargo tem adicional de periculosidade (30%)?",
                required=True,
                options=["Sim", "Nao"],
                help_text="Vigilantes geralmente tem direito a periculosidade.",
            ),

            # Passo 7: Mais postos
            WizardStep(
                id="mais_postos",
                name="Mais Postos",
                description="Adicionar mais postos",
                step_type=StepType.CONFIRMATION,
                question="Deseja adicionar outro posto de trabalho?",
                required=True,
                options=["Sim, adicionar mais", "Nao, continuar"],
                help_text="Voce pode adicionar quantos postos precisar.",
            ),

            # Passo 8: Custos Operacionais
            WizardStep(
                id="custos_operacionais",
                name="Custos Operacionais",
                description="Custos operacionais adicionais",
                step_type=StepType.NUMBER_INPUT,
                question="Qual o valor estimado de custos operacionais mensais? (uniformes, materiais, etc.)",
                required=False,
                default_value=0,
                help_text="Informe o valor em reais. Se nao houver, digite 0.",
            ),

            # Passo 9: Margem de Lucro
            WizardStep(
                id="margem_lucro",
                name="Margem de Lucro",
                description="Margem de lucro desejada",
                step_type=StepType.CHOICE,
                question="Qual a margem de lucro desejada?",
                required=True,
                options=["10%", "15%", "20%", "25%", "30%"],
                help_text="Margem a ser aplicada sobre o custo total.",
            ),
        ]

    def process_input(self, user_input: str) -> WizardResponse:
        """Processa entrada do usuario com logica especial para postos."""
        # Se estiver no passo de mais postos e responder sim
        if self.data.current_step < len(self.steps):
            current_step = self.steps[self.data.current_step]

            if current_step.id == "mais_postos":
                # Salva o posto atual
                self._save_current_posto()

                if user_input.lower() in ["sim", "s", "1", "sim, adicionar mais"]:
                    # Volta para o passo de cargo para adicionar novo posto
                    self.data.current_step = 2  # indice do passo "cargo"
                    return self._get_current_step_response(
                        message=f"Posto adicionado! Ja temos {len(self.postos)} posto(s). Vamos adicionar mais um."
                    )

        return super().process_input(user_input)

    def _save_current_posto(self) -> None:
        """Salva o posto de trabalho atual."""
        data = self.data.collected_data

        if "cargo" in data and "quantidade" in data and "escala" in data:
            cargo = data["cargo"]
            salario_base = CCT_PISOS_2026.get(cargo, 1847.12)
            escala_config = ESCALAS.get(data["escala"], {})

            posto = PostoTrabalho(
                cargo=cargo,
                quantidade=int(data["quantidade"]),
                escala=data["escala"],
                salario_base=salario_base,
                adicional_periculosidade=data.get("periculosidade", False),
                adicional_noturno=escala_config.get("adicional_noturno", False),
            )

            self.postos.append(posto)

            # Limpa dados do posto para o proximo
            for key in ["cargo", "quantidade", "escala", "periculosidade"]:
                if key in self.data.collected_data:
                    del self.data.collected_data[key]

    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final e gera a proposta."""
        # Salva ultimo posto se houver
        self._save_current_posto()

        # Calcula custos
        custo_mao_obra = sum(p.custo_mensal_total for p in self.postos)
        custos_operacionais = data.get("custos_operacionais", 0) or 0

        # Margem de lucro
        margem_str = data.get("margem_lucro", "15%")
        margem = float(margem_str.replace("%", "")) / 100

        # Calculo final
        custo_total = custo_mao_obra + custos_operacionais
        valor_proposta = custo_total * (1 + margem)

        # Detalhamento dos postos
        postos_detalhamento = []
        for i, posto in enumerate(self.postos, 1):
            postos_detalhamento.append({
                "numero": i,
                "cargo": posto.cargo,
                "quantidade": posto.quantidade,
                "escala": posto.escala,
                "salario_base": posto.salario_base,
                "salario_total": posto.salario_total,
                "custo_unitario": posto.custo_mensal_unitario,
                "custo_total": posto.custo_mensal_total,
                "periculosidade": posto.adicional_periculosidade,
                "adicional_noturno": posto.adicional_noturno,
            })

        return {
            "cliente": data.get("cliente"),
            "tipo_servico": data.get("tipo_servico"),
            "postos": postos_detalhamento,
            "resumo": {
                "total_funcionarios": sum(p.quantidade for p in self.postos),
                "custo_mao_obra": custo_mao_obra,
                "custos_operacionais": custos_operacionais,
                "custo_total": custo_total,
                "margem_lucro": margem,
                "valor_proposta": valor_proposta,
            },
            "observacoes": [
                "Valores baseados na CCT SINDCOND 2026",
                f"Encargos sociais calculados em {ENCARGOS_SOCIAIS * 100:.0f}%",
                "Proposta valida por 30 dias",
            ],
        }

    def _generate_summary(self) -> str:
        """Gera resumo personalizado da proposta."""
        # Salva ultimo posto
        self._save_current_posto()

        if not self.postos:
            return "Nenhum posto de trabalho adicionado."

        lines = [
            f"**Cliente:** {self.data.collected_data.get('cliente', 'N/A')}",
            f"**Tipo de Servico:** {self.data.collected_data.get('tipo_servico', 'N/A')}",
            "",
            "**Postos de Trabalho:**",
        ]

        custo_total_mao_obra = 0
        total_funcionarios = 0

        for i, posto in enumerate(self.postos, 1):
            lines.append(f"  {i}. {posto.cargo} ({posto.quantidade}x) - {posto.escala}")
            lines.append(f"     Salario: R$ {posto.salario_total:,.2f}/mes".replace(",", "X").replace(".", ",").replace("X", "."))
            lines.append(f"     Custo total: R$ {posto.custo_mensal_total:,.2f}/mes".replace(",", "X").replace(".", ",").replace("X", "."))
            custo_total_mao_obra += posto.custo_mensal_total
            total_funcionarios += posto.quantidade

        custos_op = self.data.collected_data.get("custos_operacionais", 0) or 0
        margem_str = self.data.collected_data.get("margem_lucro", "15%")
        margem = float(margem_str.replace("%", "")) / 100

        custo_total = custo_total_mao_obra + custos_op
        valor_proposta = custo_total * (1 + margem)

        lines.extend([
            "",
            f"**Total de Funcionarios:** {total_funcionarios}",
            f"**Custo Mao de Obra:** R$ {custo_total_mao_obra:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"**Custos Operacionais:** R$ {custos_op:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"**Margem de Lucro:** {margem_str}",
            "",
            f"**VALOR MENSAL DA PROPOSTA: R$ {valor_proposta:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."),
        ])

        return "\n".join(lines)
