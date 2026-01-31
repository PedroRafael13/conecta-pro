"""
Wizard Manager - Gerenciador de Wizards do Bartolo.

Gerencia a criacao, execucao e persistencia de wizards.
"""

import logging
from typing import Optional, Type
from uuid import UUID

from modules.ai.bartolo.wizards.base_wizard import BaseWizard, WizardResponse, WizardState
from modules.ai.bartolo.wizards.proposta_wizard import PropostaComercialWizard
from modules.ai.bartolo.wizards.admissao_wizard import AdmissaoWizard
from modules.ai.bartolo.wizards.ocorrencia_wizard import OcorrenciaWizard
from modules.ai.bartolo.wizards.disciplinar_wizard import DisciplinarWizard
from modules.ai.bartolo.wizards.ronda_wizard import RondaWizard
from modules.ai.bartolo.wizards.banco_horas_wizard import BancoHorasWizard
from modules.ai.bartolo.wizards.escala_wizard import EscalaWizard
from modules.ai.bartolo.wizards.posto_wizard import PostoWizard
from modules.ai.bartolo.wizards.diarista_wizard import DiaristaWizard
from modules.ai.bartolo.wizards.comunicado_wizard import ComunicadoWizard

logger = logging.getLogger(__name__)


# Registro de wizards disponiveis
WIZARD_REGISTRY: dict[str, Type[BaseWizard]] = {
    "proposta_comercial": PropostaComercialWizard,
    "proposta_portaria": PropostaComercialWizard,
    "proposta_limpeza": PropostaComercialWizard,
    "proposta_manutencao": PropostaComercialWizard,
    "admissao_funcionario": AdmissaoWizard,
    "admissao": AdmissaoWizard,
    "contratar": AdmissaoWizard,
    "ocorrencia": OcorrenciaWizard,
    "registrar_ocorrencia": OcorrenciaWizard,
    "disciplinar": DisciplinarWizard,
    "medida_disciplinar": DisciplinarWizard,
    "advertencia": DisciplinarWizard,
    "ronda": RondaWizard,
    "inspecao": RondaWizard,
    "ronda_inspecao": RondaWizard,
    "banco_horas": BancoHorasWizard,
    "compensacao": BancoHorasWizard,
    "hora_extra": BancoHorasWizard,
    "escala": EscalaWizard,
    "criar_escala": EscalaWizard,
    "nova_escala": EscalaWizard,
    "posto": PostoWizard,
    "criar_posto": PostoWizard,
    "novo_posto": PostoWizard,
    "cadastrar_posto": PostoWizard,
    "diarista": DiaristaWizard,
    "agendar_diarista": DiaristaWizard,
    "escalar_diarista": DiaristaWizard,
    "comunicado": ComunicadoWizard,
    "criar_comunicado": ComunicadoWizard,
    "novo_comunicado": ComunicadoWizard,
}


class WizardManager:
    """
    Gerenciador de wizards do Bartolo.

    Responsavel por:
    - Criar e iniciar wizards
    - Gerenciar sessoes ativas
    - Processar entradas e retornar respostas
    - Persistir estado de wizards
    """

    def __init__(self):
        """Inicializa o gerenciador."""
        self.active_wizards: dict[str, BaseWizard] = {}

    def get_available_wizards(self) -> list[dict]:
        """Retorna lista de wizards disponiveis."""
        wizards = []
        seen = set()

        for wizard_type, wizard_class in WIZARD_REGISTRY.items():
            if wizard_class not in seen:
                seen.add(wizard_class)
                # Cria instancia temporaria para pegar info
                temp = wizard_class(0, "temp")
                wizards.append({
                    "type": temp.get_wizard_type(),
                    "name": temp.get_wizard_name(),
                    "description": temp.get_wizard_description(),
                })

        return wizards

    def can_handle_wizard(self, intent: str) -> bool:
        """Verifica se existe wizard para a intencao."""
        # Normaliza intent
        intent_lower = intent.lower().strip()

        # Verifica match direto
        if intent_lower in WIZARD_REGISTRY:
            return True

        # Verifica keywords
        wizard_keywords = {
            "proposta": "proposta_comercial",
            "orcamento": "proposta_comercial",
            "orcar": "proposta_comercial",
            "precificar": "proposta_comercial",
            "custo": "proposta_comercial",
            "admissao": "admissao_funcionario",
            "admitir": "admissao_funcionario",
            "contratar": "admissao_funcionario",
            "contratacao": "admissao_funcionario",
            "novo funcionario": "admissao_funcionario",
            "ocorrencia": "ocorrencia",
            "registrar ocorrencia": "ocorrencia",
            "abrir ocorrencia": "ocorrencia",
            "disciplinar": "disciplinar",
            "advertencia": "disciplinar",
            "medida disciplinar": "disciplinar",
            "suspensao": "disciplinar",
            "ronda": "ronda",
            "inspecao": "ronda",
            "ronda inspecao": "ronda",
            "banco de horas": "banco_horas",
            "banco horas": "banco_horas",
            "compensacao": "banco_horas",
            "hora extra": "banco_horas",
            "horas extras": "banco_horas",
            "escala": "escala",
            "criar escala": "escala",
            "nova escala": "escala",
            "montar escala": "escala",
            "posto": "posto",
            "criar posto": "posto",
            "novo posto": "posto",
            "cadastrar posto": "posto",
            "diarista": "diarista",
            "agendar diarista": "diarista",
            "escalar diarista": "diarista",
            "comunicado": "comunicado",
            "criar comunicado": "comunicado",
            "novo comunicado": "comunicado",
            "redigir comunicado": "comunicado",
        }

        for keyword, wizard in wizard_keywords.items():
            if keyword in intent_lower:
                return True

        return False

    def detect_wizard_type(self, intent: str) -> Optional[str]:
        """
        Detecta qual wizard usar baseado na intencao.

        CORRECAO: Agora distingue entre consulta (verificar, listar, mostrar)
        e criação (criar, registrar, nova). Só retorna wizard para criação.
        """
        intent_lower = intent.lower().strip()

        # Match direto
        if intent_lower in WIZARD_REGISTRY:
            return intent_lower

        # CORRECAO: Detecta verbos de consulta - NAO deve iniciar wizard
        query_verbs = [
            'verificar', 'ver', 'listar', 'mostrar', 'consultar', 'buscar',
            'checar', 'conferir', 'exibir', 'qual', 'quais', 'quantos', 'tem', 'existe'
        ]
        first_word = intent_lower.split()[0] if intent_lower.split() else ''
        if first_word in query_verbs or any(verb in intent_lower.split()[:3] for verb in query_verbs):
            # É consulta, não wizard - retorna None
            return None

        # Keywords com verbos de CRIAÇÃO explícitos
        if any(k in intent_lower for k in ["criar proposta", "nova proposta", "orcar", "precificar"]):
            return "proposta_comercial"

        if any(k in intent_lower for k in ["admitir", "contratar", "contratacao", "novo funcionario", "admissao"]):
            return "admissao_funcionario"

        if any(k in intent_lower for k in ["registrar ocorrencia", "abrir ocorrencia", "nova ocorrencia"]):
            return "ocorrencia"

        if any(k in intent_lower for k in ["advertencia", "medida disciplinar", "suspensao", "aplicar disciplinar"]):
            return "disciplinar"

        # Ronda: só wizard se for CRIAR/REGISTRAR ronda, não VERIFICAR ronda
        if any(k in intent_lower for k in ["criar ronda", "nova ronda", "registrar ronda", "agendar ronda", "programar ronda"]):
            return "ronda"

        if any(k in intent_lower for k in ["registrar horas", "lancar horas", "compensar horas"]):
            return "banco_horas"

        # Escala: só wizard para CRIAR/GERAR escala
        if any(k in intent_lower for k in ["criar escala", "nova escala", "montar escala", "gerar escala"]):
            return "escala"

        # Posto: só wizard para CRIAR posto
        if any(k in intent_lower for k in ["criar posto", "novo posto", "cadastrar posto"]):
            return "posto"

        if any(k in intent_lower for k in ["agendar diarista", "escalar diarista", "nova diarista"]):
            return "diarista"

        # Comunicado: só wizard para CRIAR comunicado
        if any(k in intent_lower for k in ["criar comunicado", "novo comunicado", "redigir comunicado", "enviar comunicado"]):
            return "comunicado"

        return None

    def get_session_key(self, user_id: int, session_id: str) -> str:
        """Gera chave de sessao."""
        return f"{user_id}:{session_id}"

    def has_active_wizard(self, user_id: int, session_id: str) -> bool:
        """Verifica se usuario tem wizard ativo."""
        key = self.get_session_key(user_id, session_id)
        if key in self.active_wizards:
            wizard = self.active_wizards[key]
            return wizard.data.state in [WizardState.IN_PROGRESS, WizardState.WAITING_INPUT]
        return False

    def get_active_wizard(self, user_id: int, session_id: str) -> Optional[BaseWizard]:
        """Retorna wizard ativo do usuario."""
        key = self.get_session_key(user_id, session_id)
        return self.active_wizards.get(key)

    def start_wizard(
        self,
        wizard_type: str,
        user_id: int,
        session_id: str,
        initial_data: Optional[dict] = None,
    ) -> WizardResponse:
        """
        Inicia um novo wizard.

        Args:
            wizard_type: Tipo do wizard
            user_id: ID do usuario
            session_id: ID da sessao
            initial_data: Dados iniciais

        Returns:
            WizardResponse com primeiro passo
        """
        # Verifica se wizard existe
        wizard_class = WIZARD_REGISTRY.get(wizard_type)
        if not wizard_class:
            return WizardResponse(
                wizard_id=UUID(int=0),
                step_id="error",
                step_number=0,
                total_steps=0,
                state=WizardState.ERROR,
                message=f"Wizard '{wizard_type}' nao encontrado.",
                progress_percent=0.0,
            )

        # Cria wizard
        wizard = wizard_class(user_id, session_id)

        # Define dados iniciais se houver
        if initial_data:
            wizard.set_initial_data(initial_data)

        # Salva no cache
        key = self.get_session_key(user_id, session_id)
        self.active_wizards[key] = wizard

        logger.info(f"Wizard iniciado: type={wizard_type}, user={user_id}, session={session_id}")

        # Inicia e retorna primeiro passo
        return wizard.start()

    def process_input(
        self,
        user_id: int,
        session_id: str,
        user_input: str,
    ) -> Optional[WizardResponse]:
        """
        Processa entrada do usuario no wizard ativo.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            user_input: Entrada do usuario

        Returns:
            WizardResponse ou None se nao houver wizard ativo
        """
        key = self.get_session_key(user_id, session_id)
        wizard = self.active_wizards.get(key)

        if not wizard:
            return None

        response = wizard.process_input(user_input)

        # Se completou ou cancelou, remove do cache
        if response.state in [WizardState.COMPLETED, WizardState.CANCELLED]:
            # Mantem por um tempo para possivel recuperacao
            pass

        return response

    async def complete_wizard(
        self,
        user_id: int,
        session_id: str,
    ) -> Optional[dict]:
        """
        Completa wizard e processa resultado.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao

        Returns:
            Resultado do wizard ou None
        """
        key = self.get_session_key(user_id, session_id)
        wizard = self.active_wizards.get(key)

        if not wizard or wizard.data.state != WizardState.COMPLETED:
            return None

        # Processa resultado
        result = await wizard.process_result(wizard.data.collected_data)

        # Remove do cache
        del self.active_wizards[key]

        logger.info(f"Wizard completado: type={wizard.get_wizard_type()}, user={user_id}")

        return result

    def cancel_wizard(
        self,
        user_id: int,
        session_id: str,
    ) -> Optional[WizardResponse]:
        """
        Cancela wizard ativo.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao

        Returns:
            WizardResponse de cancelamento ou None
        """
        key = self.get_session_key(user_id, session_id)
        wizard = self.active_wizards.get(key)

        if not wizard:
            return None

        response = wizard.cancel()

        # Remove do cache
        del self.active_wizards[key]

        return response

    def get_wizard_status(
        self,
        user_id: int,
        session_id: str,
    ) -> Optional[dict]:
        """Retorna status do wizard ativo."""
        key = self.get_session_key(user_id, session_id)
        wizard = self.active_wizards.get(key)

        if not wizard:
            return None

        return {
            "wizard_id": str(wizard.wizard_id),
            "wizard_type": wizard.get_wizard_type(),
            "wizard_name": wizard.get_wizard_name(),
            "state": wizard.data.state.value,
            "current_step": wizard.data.current_step,
            "total_steps": wizard.data.total_steps,
            "progress_percent": (wizard.data.current_step / wizard.data.total_steps * 100)
                if wizard.data.total_steps > 0 else 0,
            "collected_data": wizard.data.collected_data,
            "started_at": wizard.data.started_at.isoformat() if wizard.data.started_at else None,
        }

    def get_wizard_help(self, wizard_type: str) -> str:
        """Retorna ajuda sobre um wizard."""
        wizard_class = WIZARD_REGISTRY.get(wizard_type)
        if not wizard_class:
            return "Wizard nao encontrado."

        temp = wizard_class(0, "temp")
        return f"**{temp.get_wizard_name()}**\n\n{temp.get_wizard_description()}"
