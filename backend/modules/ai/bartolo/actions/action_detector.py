"""
Detector de intenções de ação em mensagens do usuário.
"""

import logging
import re
from typing import Any

from .action_schemas import ActionRequest
from .action_types import ActionCategory, ActionType

logger = logging.getLogger(__name__)


class ActionDetector:
    """Detecta intenções de ação via pattern matching."""

    ACTION_PATTERNS = {
        ActionType.CREATE_SCALE: [
            r"criar?\s+(?:uma\s+)?escala",
            r"gerar?\s+(?:uma\s+)?escala",
            r"montar?\s+(?:uma\s+)?escala",
            r"nova\s+escala",
        ],
        ActionType.APPROVE_SCALE: [
            r"aprovar?\s+(?:a\s+)?escala",
            r"aprovar?\s+escala",
        ],
        ActionType.PUBLISH_SCALE: [
            r"publicar?\s+(?:a\s+)?escala",
            r"divulgar?\s+(?:a\s+)?escala",
        ],
        ActionType.ALLOCATE_EMPLOYEE: [
            r"alocar?\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)",
            r"colocar\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)\s+n[oa]",
            r"designar?\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)",
        ],
        ActionType.TERMINATE_ALLOCATION: [
            r"(?:encerrar|terminar|finalizar)\s+(?:a\s+)?aloca[cç][aã]o",
            r"remover\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)\s+d[oa]",
        ],
        ActionType.TRANSFER_EMPLOYEE: [
            r"transferir?\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)",
            r"mudar\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)\s+(?:de|para)",
        ],
        ActionType.CREATE_SHIFT: [
            r"criar?\s+(?:um\s+)?turno",
            r"registrar?\s+(?:um\s+)?turno",
            r"lan[cç]ar?\s+(?:um\s+)?turno",
        ],
        ActionType.REGISTER_CHECKIN: [
            r"(?:registrar|fazer|bater)\s+(?:a\s+)?(?:entrada|check-?in)",
            r"marcar?\s+entrada",
        ],
        ActionType.REGISTER_CHECKOUT: [
            r"(?:registrar|fazer|bater)\s+(?:a\s+)?(?:sa[ií]da|check-?out)",
            r"marcar?\s+sa[ií]da",
        ],
        ActionType.MARK_ABSENCE: [
            r"marcar?\s+(?:como\s+)?(?:falta|ausente)",
            r"registrar?\s+(?:a\s+)?(?:falta|aus[eê]ncia)",
        ],
        ActionType.CREATE_SUBSTITUTION: [
            r"criar?\s+(?:uma\s+)?substitui[cç][aã]o",
            r"substituir?\s+(?:o\s+)?(?:funcion[aá]rio|colaborador)",
        ],
        # Ocorrências
        ActionType.CREATE_OCCURRENCE: [
            r"(?:criar|registrar|abrir|lan[cç]ar)\s+(?:uma?\s+)?(?:ocorr[eê]ncia|ocorrencia)",
            r"nova\s+(?:ocorr[eê]ncia|ocorrencia)",
        ],
        ActionType.RESOLVE_OCCURRENCE: [
            r"(?:resolver|fechar|concluir|encerrar)\s+(?:a?\s+)?(?:ocorr[eê]ncia|ocorrencia)",
        ],
        ActionType.UPDATE_OCCURRENCE: [
            r"(?:atualizar|editar|alterar)\s+(?:a?\s+)?(?:ocorr[eê]ncia|ocorrencia)",
        ],
        # Disciplinares
        ActionType.CREATE_DISCIPLINARY: [
            r"(?:criar|registrar|aplicar|lan[cç]ar)\s+(?:uma?\s+)?(?:medida\s+)?disciplinar",
            r"(?:criar|registrar|aplicar)\s+(?:uma?\s+)?(?:advert[eê]ncia|suspens[aã]o)",
        ],
        ActionType.APPROVE_DISCIPLINARY: [
            r"(?:aprovar|autorizar|confirmar)\s+(?:a?\s+)?(?:medida\s+)?disciplinar",
        ],
        ActionType.REJECT_DISCIPLINARY: [
            r"(?:rejeitar|recusar|negar)\s+(?:a?\s+)?(?:medida\s+)?disciplinar",
        ],
        # Rondas
        ActionType.CREATE_ROUND: [
            r"(?:criar|registrar|agendar)\s+(?:uma?\s+)?(?:ronda|inspe[cç][aã]o)",
            r"nova\s+(?:ronda|inspe[cç][aã]o)",
        ],
        ActionType.START_ROUND: [
            r"(?:iniciar|come[cç]ar|ativar)\s+(?:a?\s+)?(?:ronda|inspe[cç][aã]o)",
        ],
        ActionType.COMPLETE_ROUND: [
            r"(?:completar|finalizar|concluir|encerrar)\s+(?:a?\s+)?(?:ronda|inspe[cç][aã]o)",
        ],
        # Diaristas
        ActionType.CREATE_DIARIST: [
            r"(?:cadastrar|registrar|criar)\s+(?:uma?\s+)?diarista",
            r"nov[oa]\s+diarista",
        ],
        ActionType.SCHEDULE_DIARIST: [
            r"(?:escalar|agendar|programar)\s+(?:uma?\s+)?diarista",
            r"(?:alocar)\s+diarista",
        ],
        # Comunicados
        ActionType.CREATE_ANNOUNCEMENT: [
            r"(?:criar|redigir|escrever)\s+(?:um?\s+)?(?:comunicado|an[uú]ncio|aviso)",
            r"nov[oa]\s+(?:comunicado|an[uú]ncio|aviso)",
        ],
        ActionType.PUBLISH_ANNOUNCEMENT: [
            r"(?:publicar|enviar|divulgar)\s+(?:o?\s+)?(?:comunicado|an[uú]ncio|aviso)",
        ],
        ActionType.SEND_NOTIFICATION: [
            r"enviar?\s+(?:uma\s+)?notifica[cç][aã]o",
            r"notificar",
            r"avisar",
        ],
        ActionType.GENERATE_REPORT: [
            r"gerar?\s+(?:um\s+)?relat[oó]rio",
            r"criar?\s+(?:um\s+)?relat[oó]rio",
            r"exportar?\s+(?:um\s+)?relat[oó]rio",
        ],
        # Banco de Horas
        ActionType.APPROVE_OVERTIME: [
            r"(?:aprovar|autorizar|confirmar)\s+(?:a?\s+)?hora[s]?\s+extra[s]?",
            r"(?:aprovar|autorizar)\s+(?:o?\s+)?banco\s+(?:de\s+)?horas",
        ],
        ActionType.REQUEST_COMPENSATION: [
            r"(?:solicitar|pedir|requerer)\s+(?:a?\s+)?compensa[cç][aã]o",
            r"(?:compensar|folgar)\s+(?:as?\s+)?horas",
        ],
        ActionType.VIEW_BALANCE: [
            r"(?:ver|consultar|mostrar)\s+(?:o?\s+)?saldo\s+(?:de\s+)?(?:horas|banco)",
            r"saldo\s+(?:do\s+)?banco\s+(?:de\s+)?horas",
        ],
        # Postos
        ActionType.CREATE_POST: [
            r"(?:criar|cadastrar|registrar)\s+(?:um?\s+)?posto",
            r"nov[oa]\s+posto",
        ],
        ActionType.UPDATE_POST: [
            r"(?:atualizar|editar|alterar)\s+(?:o?\s+)?posto",
            r"(?:modificar)\s+(?:o?\s+)?posto",
        ],
        ActionType.DELETE_POST: [
            r"(?:excluir|remover|deletar|desativar)\s+(?:o?\s+)?posto",
        ],
        ActionType.GET_POST_STATS: [
            r"(?:estat[ií]stica|stats?|resumo)\s+(?:do?\s+)?posto[s]?",
            r"(?:indicadores|m[eé]tricas)\s+(?:do?\s+)?posto[s]?",
        ],
        # Escalas (avançado)
        ActionType.AUTO_GENERATE_SCALE: [
            r"(?:auto\s*gerar|gerar?\s+automaticamente)\s+(?:a?\s+)?escala",
            r"escala\s+autom[aá]tica",
        ],
        ActionType.OPTIMIZE_SCALE: [
            r"(?:otimizar|melhorar|ajustar)\s+(?:a?\s+)?escala",
            r"otimiza[cç][aã]o\s+(?:de\s+)?escala",
        ],
        ActionType.CREATE_SCALE_TEMPLATE: [
            r"(?:criar|salvar)\s+(?:um?\s+)?template\s+(?:de\s+)?escala",
            r"(?:criar|salvar)\s+modelo\s+(?:de\s+)?escala",
        ],
        ActionType.APPLY_SCALE_TEMPLATE: [
            r"(?:aplicar|usar)\s+(?:o?\s+)?template\s+(?:de\s+)?escala",
            r"(?:aplicar|usar)\s+modelo\s+(?:de\s+)?escala",
        ],
        # Diaristas (avançado)
        ActionType.EVALUATE_DIARIST: [
            r"(?:avaliar|dar\s+nota)\s+(?:a?\s+)?diarista",
            r"avalia[cç][aã]o\s+(?:da?\s+)?diarista",
        ],
        ActionType.APPROVE_DIARIST_PAYMENT: [
            r"(?:aprovar|autorizar)\s+(?:o?\s+)?pagamento\s+(?:da?\s+)?diarista",
        ],
        ActionType.GENERATE_DIARIST_PAYMENT: [
            r"(?:gerar|criar|calcular)\s+(?:o?\s+)?pagamento\s+(?:da?\s+)?diarista",
            r"(?:gerar|criar)\s+folha\s+(?:de\s+)?diarista",
        ],
        # Rondas (avançado)
        ActionType.REGISTER_CHECKPOINT: [
            r"(?:registrar|marcar)\s+(?:o?\s+)?checkpoint",
            r"(?:registrar|marcar)\s+ponto\s+(?:de\s+)?(?:ronda|inspe[cç][aã]o)",
        ],
        ActionType.PAUSE_ROUND: [
            r"(?:pausar|interromper|suspender)\s+(?:a?\s+)?(?:ronda|inspe[cç][aã]o)",
        ],
        ActionType.RESUME_ROUND: [
            r"(?:retomar|continuar|reativar)\s+(?:a?\s+)?(?:ronda|inspe[cç][aã]o)",
        ],
    }

    CATEGORY_MAP = {
        ActionType.CREATE_SCALE: ActionCategory.OPERATIONAL,
        ActionType.APPROVE_SCALE: ActionCategory.ADMINISTRATIVE,
        ActionType.PUBLISH_SCALE: ActionCategory.ADMINISTRATIVE,
        ActionType.ALLOCATE_EMPLOYEE: ActionCategory.OPERATIONAL,
        ActionType.TERMINATE_ALLOCATION: ActionCategory.OPERATIONAL,
        ActionType.TRANSFER_EMPLOYEE: ActionCategory.OPERATIONAL,
        ActionType.CREATE_SHIFT: ActionCategory.OPERATIONAL,
        ActionType.REGISTER_CHECKIN: ActionCategory.OPERATIONAL,
        ActionType.REGISTER_CHECKOUT: ActionCategory.OPERATIONAL,
        ActionType.MARK_ABSENCE: ActionCategory.OPERATIONAL,
        ActionType.CREATE_SUBSTITUTION: ActionCategory.OPERATIONAL,
        ActionType.CREATE_OCCURRENCE: ActionCategory.OPERATIONAL,
        ActionType.RESOLVE_OCCURRENCE: ActionCategory.OPERATIONAL,
        ActionType.UPDATE_OCCURRENCE: ActionCategory.OPERATIONAL,
        ActionType.CREATE_DISCIPLINARY: ActionCategory.ADMINISTRATIVE,
        ActionType.APPROVE_DISCIPLINARY: ActionCategory.ADMINISTRATIVE,
        ActionType.REJECT_DISCIPLINARY: ActionCategory.ADMINISTRATIVE,
        ActionType.CREATE_ROUND: ActionCategory.OPERATIONAL,
        ActionType.START_ROUND: ActionCategory.OPERATIONAL,
        ActionType.COMPLETE_ROUND: ActionCategory.OPERATIONAL,
        ActionType.CREATE_DIARIST: ActionCategory.OPERATIONAL,
        ActionType.SCHEDULE_DIARIST: ActionCategory.OPERATIONAL,
        ActionType.CREATE_ANNOUNCEMENT: ActionCategory.NOTIFICATION,
        ActionType.PUBLISH_ANNOUNCEMENT: ActionCategory.NOTIFICATION,
        ActionType.SEND_NOTIFICATION: ActionCategory.NOTIFICATION,
        ActionType.GENERATE_REPORT: ActionCategory.REPORT,
        # Banco de Horas
        ActionType.APPROVE_OVERTIME: ActionCategory.ADMINISTRATIVE,
        ActionType.REQUEST_COMPENSATION: ActionCategory.OPERATIONAL,
        ActionType.VIEW_BALANCE: ActionCategory.OPERATIONAL,
        # Postos
        ActionType.CREATE_POST: ActionCategory.OPERATIONAL,
        ActionType.UPDATE_POST: ActionCategory.OPERATIONAL,
        ActionType.DELETE_POST: ActionCategory.ADMINISTRATIVE,
        ActionType.GET_POST_STATS: ActionCategory.REPORT,
        # Escalas (avançado)
        ActionType.AUTO_GENERATE_SCALE: ActionCategory.OPERATIONAL,
        ActionType.OPTIMIZE_SCALE: ActionCategory.OPERATIONAL,
        ActionType.CREATE_SCALE_TEMPLATE: ActionCategory.ADMINISTRATIVE,
        ActionType.APPLY_SCALE_TEMPLATE: ActionCategory.OPERATIONAL,
        # Diaristas (avançado)
        ActionType.EVALUATE_DIARIST: ActionCategory.OPERATIONAL,
        ActionType.APPROVE_DIARIST_PAYMENT: ActionCategory.ADMINISTRATIVE,
        ActionType.GENERATE_DIARIST_PAYMENT: ActionCategory.OPERATIONAL,
        # Rondas (avançado)
        ActionType.REGISTER_CHECKPOINT: ActionCategory.OPERATIONAL,
        ActionType.PAUSE_ROUND: ActionCategory.OPERATIONAL,
        ActionType.RESUME_ROUND: ActionCategory.OPERATIONAL,
    }

    def detect(self, message: str, user_id: str, session_id: str) -> ActionRequest | None:
        """
        Detecta ação na mensagem do usuário.

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            session_id: ID da sessão

        Returns:
            ActionRequest se detectou ação, None caso contrário
        """
        message_lower = message.lower()

        for action_type, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    logger.info(f"Ação detectada: {action_type.value} (pattern: {pattern})")

                    parameters = self._extract_parameters(message, action_type)
                    confidence = self._calculate_confidence(message, action_type, parameters)

                    return ActionRequest(
                        action_type=action_type,
                        category=self._get_category(action_type),
                        parameters=parameters,
                        detected_from_message=message,
                        confidence=confidence,
                        user_id=user_id,
                        session_id=session_id,
                    )

        return None

    def _get_category(self, action_type: ActionType) -> ActionCategory:
        """Retorna categoria da ação."""
        return self.CATEGORY_MAP.get(action_type, ActionCategory.OPERATIONAL)

    # Stop words usadas para delimitar nome do posto
    # \b no final impede match parcial ("de" em "dei")
    _POST_NAME_STOP = (
        r"(?:em|para|de|do|da|no|na|dos|das|nos|nas|"
        r"janeiro|fevereiro|mar[cç]o|abril|maio|junho|"
        r"julho|agosto|setembro|outubro|novembro|dezembro|"
        r"\d{1,2}/\d{4}|\d{4}|turno|escala)\b"
    )

    def _extract_parameters(self, message: str, action_type: ActionType) -> dict[str, Any]:
        """
        Extrai parâmetros da mensagem baseado no tipo de ação.

        Args:
            message: Mensagem do usuário
            action_type: Tipo de ação detectada

        Returns:
            Dicionário com parâmetros extraídos
        """
        params: dict[str, Any] = {}
        message_lower = message.lower()

        # --- Extração de posto ---
        # 1. Código explícito: POST-0021, post-21, post 0021
        post_code_match = re.search(r"\bpost[- ]?(\d{3,4})\b", message_lower)
        if not post_code_match:
            # "posto 21", "posto 0021"
            post_code_match = re.search(r"\bposto\s+(\d{1,4})\b", message_lower)

        if post_code_match:
            code_num = post_code_match.group(1).zfill(4)
            params["post_code"] = f"POST-{code_num}"
        else:
            # 2. Nome natural após keywords: "posto Prime Arena", "condomínio Michelangelo"
            post_name_match = re.search(
                r"(?:posto|condom[ií]nio|residencial|base)\s+(?:d[aeo]s?\s+)?"
                r"(.+?)(?:\s+" + self._POST_NAME_STOP + r"|\s*$)",
                message_lower,
            )
            if post_name_match:
                name = post_name_match.group(1).strip()
                # Remove artigos/preposições trailing
                name = re.sub(r"\s+(?:para|em|de|do|da|no|na|o|a)\s*$", "", name).strip()
                if len(name) >= 3:
                    params["post_name"] = name

        # Extração de mês/ano
        month_match = re.search(
            r"\b(janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b",
            message_lower,
        )
        if month_match:
            months = {
                "janeiro": 1,
                "fevereiro": 2,
                "março": 3,
                "marco": 3,
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
            params["month"] = months.get(month_match.group(1))

        # Extração de mês numérico (ex: 02/2024, em fevereiro)
        month_num_match = re.search(r"\b(\d{1,2})/(\d{4})\b", message)
        if month_num_match:
            params["month"] = int(month_num_match.group(1))
            params["year"] = int(month_num_match.group(2))

        # Extração de ano (ex: 2024, em 2024)
        if "year" not in params:
            year_match = re.search(r"\b(20\d{2})\b", message)
            if year_match:
                params["year"] = int(year_match.group(1))

        # Extração de ID de funcionário (UUID explícito)
        employee_match = re.search(
            r"(?:funcion[aá]rio|colaborador|empregado)[:\s-]*([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
            message_lower,
        )
        if employee_match:
            params["employee_id"] = employee_match.group(1)

        # Extração de matrícula de funcionário
        if "employee_id" not in params:
            matricula_match = re.search(r"(?:matr[ií]cula|mat\.?)\s*[:=]?\s*(\d{3,10})", message_lower)
            if matricula_match:
                params["employee_matricula"] = matricula_match.group(1)

        # Extração de nome de funcionário (nome próprio após keywords)
        if "employee_id" not in params and "employee_matricula" not in params:
            # "funcionário João Silva", "colaborador Carlos", "vigilante Roberto"
            emp_name_match = re.search(
                r"(?:funcion[aá]rio|colaborador|vigilante|porteiro|seguran[cç]a)\s+"
                r"(?:d[aeo]s?\s+)?"
                r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ÿ][a-zà-ÿ]+)*)",
                message,  # usa original (não lowercase) para detectar nomes próprios
            )
            if emp_name_match:
                name = emp_name_match.group(1).strip()
                if len(name) >= 3:
                    params["employee_name"] = name

            # "alocar o João", "transferir a Maria Silva"
            if "employee_name" not in params:
                verb_name_match = re.search(
                    r"(?:alocar|transferir|escalar)\s+"
                    r"(?:o|a|do|da)\s+"
                    r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ÿ][a-zà-ÿ]+)*)",
                    message,
                )
                if verb_name_match:
                    name = verb_name_match.group(1).strip()
                    if len(name) >= 3:
                        params["employee_name"] = name

        # Extração de ID de escala
        scale_match = re.search(r"(?:escala)[:\s-]*([a-z0-9-]+)", message_lower)
        if scale_match:
            params["scale_id"] = scale_match.group(1)

        logger.debug(f"Parâmetros extraídos: {params}")
        return params

    def _calculate_confidence(self, message: str, action_type: ActionType, parameters: dict[str, Any]) -> float:
        """
        Calcula confiança da detecção.

        Args:
            message: Mensagem original
            action_type: Tipo de ação detectada
            parameters: Parâmetros extraídos

        Returns:
            Score de confiança entre 0.0 e 1.0
        """
        confidence = 0.7  # Base

        # Aumenta confiança se tem parâmetros relevantes
        # post_name conta como alternativa a post_code
        has_post = "post_code" in parameters or "post_name" in parameters
        param_bonus = {
            ActionType.CREATE_SCALE: ["_post", "month", "year"],
            ActionType.APPROVE_SCALE: ["scale_id", "_post"],
            ActionType.PUBLISH_SCALE: ["scale_id", "_post"],
            ActionType.ALLOCATE_EMPLOYEE: ["employee_id", "_post"],
            ActionType.TERMINATE_ALLOCATION: ["employee_id"],
            ActionType.TRANSFER_EMPLOYEE: ["employee_id", "_post"],
        }

        expected_params = param_bonus.get(action_type, [])
        if expected_params:
            found_params = 0
            for p in expected_params:
                if p == "_post":
                    found_params += 1 if has_post else 0
                elif p in parameters:
                    found_params += 1
            confidence += (found_params / len(expected_params)) * 0.3

        return min(confidence, 1.0)
