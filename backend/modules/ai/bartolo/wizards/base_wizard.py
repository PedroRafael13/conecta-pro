"""
Base Wizard - Classe base para assistencia guiada.

Define a estrutura padrao para todos os wizards do Bartolo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Callable
from uuid import UUID, uuid4


class WizardState(str, Enum):
    """Estado do wizard."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING_INPUT = "waiting_input"
    VALIDATING = "validating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class StepType(str, Enum):
    """Tipo de passo do wizard."""
    TEXT_INPUT = "text_input"           # Entrada de texto livre
    NUMBER_INPUT = "number_input"       # Entrada numerica
    CHOICE = "choice"                   # Selecao unica
    MULTI_CHOICE = "multi_choice"       # Selecao multipla
    DATE_INPUT = "date_input"           # Entrada de data
    CONFIRMATION = "confirmation"       # Confirmacao sim/nao
    DISPLAY = "display"                 # Apenas exibicao
    CALCULATION = "calculation"         # Passo de calculo
    REVIEW = "review"                   # Revisao de dados


@dataclass
class WizardStep:
    """Passo do wizard."""
    id: str
    name: str
    description: str
    step_type: StepType
    question: str
    required: bool = True
    options: list = field(default_factory=list)
    default_value: Any = None
    validation_rules: dict = field(default_factory=dict)
    help_text: Optional[str] = None
    depends_on: Optional[str] = None
    skip_condition: Optional[Callable] = None


@dataclass
class WizardData:
    """Dados coletados pelo wizard."""
    wizard_id: UUID
    wizard_type: str
    user_id: int
    session_id: str
    state: WizardState = WizardState.NOT_STARTED
    current_step: int = 0
    total_steps: int = 0
    collected_data: dict = field(default_factory=dict)
    validation_errors: list = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class WizardResponse:
    """Resposta de um passo do wizard."""
    wizard_id: UUID
    step_id: str
    step_number: int
    total_steps: int
    state: WizardState
    message: str
    question: Optional[str] = None
    step_type: Optional[StepType] = None
    options: list = field(default_factory=list)
    help_text: Optional[str] = None
    collected_data: dict = field(default_factory=dict)
    validation_error: Optional[str] = None
    can_go_back: bool = True
    progress_percent: float = 0.0


class BaseWizard(ABC):
    """
    Classe base para wizards do Bartolo.

    Todos os wizards devem herdar desta classe e implementar
    os metodos abstratos.
    """

    def __init__(self, user_id: int, session_id: str):
        """Inicializa o wizard."""
        self.wizard_id = uuid4()
        self.user_id = user_id
        self.session_id = session_id
        self.steps: list[WizardStep] = []
        self.data = WizardData(
            wizard_id=self.wizard_id,
            wizard_type=self.get_wizard_type(),
            user_id=user_id,
            session_id=session_id,
        )
        self._setup_steps()

    @abstractmethod
    def get_wizard_type(self) -> str:
        """Retorna o tipo do wizard."""
        pass

    @abstractmethod
    def get_wizard_name(self) -> str:
        """Retorna o nome amigavel do wizard."""
        pass

    @abstractmethod
    def get_wizard_description(self) -> str:
        """Retorna descricao do wizard."""
        pass

    @abstractmethod
    def _setup_steps(self) -> None:
        """Configura os passos do wizard."""
        pass

    @abstractmethod
    async def process_result(self, data: dict) -> dict:
        """Processa o resultado final do wizard."""
        pass

    def start(self) -> WizardResponse:
        """Inicia o wizard."""
        self.data.state = WizardState.IN_PROGRESS
        self.data.started_at = datetime.utcnow()
        self.data.total_steps = len(self.steps)
        self.data.current_step = 0

        return self._get_current_step_response(
            message=f"Vamos comecar! {self.get_wizard_description()}"
        )

    def process_input(self, user_input: str) -> WizardResponse:
        """
        Processa entrada do usuario.

        Args:
            user_input: Entrada do usuario

        Returns:
            WizardResponse com proximo passo ou resultado
        """
        if self.data.state == WizardState.COMPLETED:
            return WizardResponse(
                wizard_id=self.wizard_id,
                step_id="completed",
                step_number=self.data.total_steps,
                total_steps=self.data.total_steps,
                state=WizardState.COMPLETED,
                message="Este wizard ja foi concluido.",
                progress_percent=100.0,
            )

        if self.data.state == WizardState.CANCELLED:
            return WizardResponse(
                wizard_id=self.wizard_id,
                step_id="cancelled",
                step_number=self.data.current_step,
                total_steps=self.data.total_steps,
                state=WizardState.CANCELLED,
                message="Este wizard foi cancelado.",
                progress_percent=0.0,
            )

        # Verifica comandos especiais
        if user_input.lower() in ["cancelar", "sair", "parar"]:
            return self.cancel()

        if user_input.lower() in ["voltar", "anterior"]:
            return self.go_back()

        # Processa entrada do passo atual
        current_step = self.steps[self.data.current_step]

        # Valida entrada
        validation_error = self._validate_input(current_step, user_input)
        if validation_error:
            return self._get_current_step_response(
                message=f"Hmm, {validation_error}",
                validation_error=validation_error,
            )

        # Salva dados
        processed_value = self._process_value(current_step, user_input)
        self.data.collected_data[current_step.id] = processed_value

        # Avanca para proximo passo
        return self._advance_step()

    def go_back(self) -> WizardResponse:
        """Volta ao passo anterior."""
        if self.data.current_step > 0:
            self.data.current_step -= 1
            return self._get_current_step_response(
                message="Ok, voltando ao passo anterior."
            )
        else:
            return self._get_current_step_response(
                message="Voce ja esta no primeiro passo."
            )

    def cancel(self) -> WizardResponse:
        """Cancela o wizard."""
        self.data.state = WizardState.CANCELLED
        return WizardResponse(
            wizard_id=self.wizard_id,
            step_id="cancelled",
            step_number=self.data.current_step,
            total_steps=self.data.total_steps,
            state=WizardState.CANCELLED,
            message="Wizard cancelado. Posso ajudar com outra coisa?",
            progress_percent=0.0,
        )

    def _advance_step(self) -> WizardResponse:
        """Avanca para o proximo passo."""
        self.data.current_step += 1

        # Pula passos condicionais
        while self.data.current_step < len(self.steps):
            step = self.steps[self.data.current_step]
            if step.skip_condition and step.skip_condition(self.data.collected_data):
                self.data.current_step += 1
            else:
                break

        # Verifica se completou
        if self.data.current_step >= len(self.steps):
            return self._complete_wizard()

        return self._get_current_step_response(
            message="Otimo! Vamos continuar."
        )

    def _complete_wizard(self) -> WizardResponse:
        """Completa o wizard."""
        self.data.state = WizardState.COMPLETED
        self.data.completed_at = datetime.utcnow()

        # Gera resumo dos dados coletados
        summary = self._generate_summary()

        return WizardResponse(
            wizard_id=self.wizard_id,
            step_id="completed",
            step_number=self.data.total_steps,
            total_steps=self.data.total_steps,
            state=WizardState.COMPLETED,
            message=f"Perfeito! Aqui esta o resumo:\n\n{summary}\n\nDeseja confirmar?",
            collected_data=self.data.collected_data,
            progress_percent=100.0,
            options=["Confirmar", "Voltar e editar", "Cancelar"],
            step_type=StepType.CONFIRMATION,
        )

    def _get_current_step_response(
        self,
        message: str,
        validation_error: Optional[str] = None,
    ) -> WizardResponse:
        """Gera resposta para o passo atual."""
        if self.data.current_step >= len(self.steps):
            return self._complete_wizard()

        step = self.steps[self.data.current_step]
        progress = (self.data.current_step / self.data.total_steps) * 100

        return WizardResponse(
            wizard_id=self.wizard_id,
            step_id=step.id,
            step_number=self.data.current_step + 1,
            total_steps=self.data.total_steps,
            state=WizardState.WAITING_INPUT,
            message=message,
            question=step.question,
            step_type=step.step_type,
            options=step.options,
            help_text=step.help_text,
            collected_data=self.data.collected_data,
            validation_error=validation_error,
            can_go_back=self.data.current_step > 0,
            progress_percent=progress,
        )

    def _validate_input(self, step: WizardStep, user_input: str) -> Optional[str]:
        """Valida entrada do usuario."""
        # Verifica se e obrigatorio
        if step.required and not user_input.strip():
            return "Este campo e obrigatorio."

        # Valida por tipo
        if step.step_type == StepType.NUMBER_INPUT:
            try:
                float(user_input.replace(",", ".").replace("R$", "").strip())
            except ValueError:
                return "Por favor, informe um numero valido."

        if step.step_type == StepType.CHOICE:
            valid_options = [str(i + 1) for i in range(len(step.options))]
            valid_options.extend([o.lower() for o in step.options])
            if user_input.lower() not in valid_options:
                return f"Por favor, escolha uma opcao valida: {', '.join(step.options)}"

        # Validacoes customizadas
        if step.validation_rules:
            if "min_length" in step.validation_rules:
                if len(user_input) < step.validation_rules["min_length"]:
                    return f"Minimo de {step.validation_rules['min_length']} caracteres."
            if "max_length" in step.validation_rules:
                if len(user_input) > step.validation_rules["max_length"]:
                    return f"Maximo de {step.validation_rules['max_length']} caracteres."
            if "min_value" in step.validation_rules:
                try:
                    value = float(user_input.replace(",", ".").replace("R$", "").strip())
                    if value < step.validation_rules["min_value"]:
                        return f"Valor minimo: {step.validation_rules['min_value']}"
                except ValueError:
                    pass
            if "max_value" in step.validation_rules:
                try:
                    value = float(user_input.replace(",", ".").replace("R$", "").strip())
                    if value > step.validation_rules["max_value"]:
                        return f"Valor maximo: {step.validation_rules['max_value']}"
                except ValueError:
                    pass

        return None

    def _process_value(self, step: WizardStep, user_input: str) -> Any:
        """Processa valor de entrada."""
        if step.step_type == StepType.NUMBER_INPUT:
            return float(user_input.replace(",", ".").replace("R$", "").strip())

        if step.step_type == StepType.CHOICE:
            # Se for numero, retorna a opcao correspondente
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(step.options):
                    return step.options[idx]
            except ValueError:
                pass
            return user_input

        if step.step_type == StepType.CONFIRMATION:
            return user_input.lower() in ["sim", "s", "yes", "y", "1", "confirmar"]

        return user_input.strip()

    def _generate_summary(self) -> str:
        """Gera resumo dos dados coletados."""
        lines = []
        for step in self.steps:
            if step.id in self.data.collected_data:
                value = self.data.collected_data[step.id]
                if isinstance(value, float):
                    value = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lines.append(f"- **{step.name}**: {value}")
        return "\n".join(lines)

    def get_state(self) -> WizardData:
        """Retorna estado atual do wizard."""
        return self.data

    def set_initial_data(self, data: dict) -> None:
        """Define dados iniciais."""
        self.data.collected_data.update(data)
