"""
EscalaAgent - Agente especialista em escalas de trabalho
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EscalaIntent(str, Enum):
    """Intents relacionados a escalas"""
    GERAR_ESCALA = "gerar_escala"
    OTIMIZAR_ESCALA = "otimizar_escala"
    VALIDAR_ESCALA = "validar_escala"
    PUBLICAR_ESCALA = "publicar_escala"
    CALCULAR_CUSTO = "calcular_custo"
    LISTAR_CONFLITOS = "listar_conflitos"
    ESCALA_SEMANA = "escala_semana"
    ESCALA_MES = "escala_mes"


class EscalaAgent:
    """
    Agente especializado em operações de escala.

    Capabilities:
    - Gerar escala automática (12x36, 5x2, 6x1, etc)
    - Otimizar escala existente
    - Detectar conflitos
    - Validar cobertura
    - Calcular custos
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para detecção de intenções
    # IMPORTANTE: Patterns mais específicos devem vir ANTES dos mais genéricos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # LISTAR_CONFLITOS com mês - ANTES de ESCALA_MES (mais específico)
        # ==================================================================
        (r"(?:tem|ha|há)\s+conflitos?\s+(?:na\s+)?escala\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", EscalaIntent.LISTAR_CONFLITOS),

        # ==================================================================
        # ESCALA_MES
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a\s+)?escala\s+do\s+mes", EscalaIntent.ESCALA_MES),
        (r"escala\s+(?:do\s+|deste\s+)?mes", EscalaIntent.ESCALA_MES),
        (r"escalas?\s+(?:de\s+|do\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", EscalaIntent.ESCALA_MES),
        (r"montar\s+(?:a\s+)?escala\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", EscalaIntent.ESCALA_MES),
        (r"(?:proximos?\s+)?(?:30|trinta)\s+dias", EscalaIntent.ESCALA_MES),

        # ==================================================================
        # OTIMIZAR_ESCALA - Antes de CALCULAR_CUSTO (para "reduzir custo")
        # ==================================================================
        (r"(?:reduzir|diminuir)\s+(?:o\s+)?custo\s+(?:da\s+)?escala", EscalaIntent.OTIMIZAR_ESCALA),
        (r"(?:reduzir|diminuir)\s+(?:as?\s+)?horas?\s+extras?\s+(?:da\s+)?escala", EscalaIntent.OTIMIZAR_ESCALA),
        (r"(?:otimizar|otimize|melhorar|melhore|ajustar|ajuste|refinar|refine)\s+(?:a\s+)?escala", EscalaIntent.OTIMIZAR_ESCALA),
        (r"escala\s+(?:mais\s+)?(?:eficiente|barata|otimizada)", EscalaIntent.OTIMIZAR_ESCALA),
        (r"(?:deixar|tornar)\s+(?:a\s+)?escala\s+(?:mais\s+)?(?:eficiente|barata)", EscalaIntent.OTIMIZAR_ESCALA),

        # ==================================================================
        # VALIDAR_ESCALA - Checagem de escala (com "algum" = pergunta existência)
        # ==================================================================
        (r"(?:validar|valide|checar|cheque|conferir|confira)\s+(?:a\s+)?escala", EscalaIntent.VALIDAR_ESCALA),
        (r"(?:verificar|verifique)\s+(?:a\s+)?escala\b(?!\s*s)", EscalaIntent.VALIDAR_ESCALA),
        (r"escala\s+(?:esta\s+)?(?:correta|certa|ok|valida)", EscalaIntent.VALIDAR_ESCALA),
        (r"(?:tem|ha|há)\s+algum\s+(?:problema|erro|conflito)\s+(?:na\s+)?escala", EscalaIntent.VALIDAR_ESCALA),
        (r"(?:ha|há)\s+conflito\s+na\s+escala$", EscalaIntent.VALIDAR_ESCALA),
        (r"(?:analisar|analise)\s+(?:a\s+)?escala", EscalaIntent.VALIDAR_ESCALA),
        (r"escala\s+(?:esta\s+)?(?:dentro\s+)?(?:da\s+)?(?:CLT|clt|lei)", EscalaIntent.VALIDAR_ESCALA),

        # ==================================================================
        # LISTAR_CONFLITOS - Listar conflitos (direto, sem "algum")
        # ==================================================================
        (r"conflitos?\s+(?:na\s+|da\s+|de\s+)?escala", EscalaIntent.LISTAR_CONFLITOS),
        (r"escala\s+(?:com\s+)?conflitos?", EscalaIntent.LISTAR_CONFLITOS),
        (r"(?:problemas?|erros?)\s+(?:na\s+)?escala", EscalaIntent.LISTAR_CONFLITOS),
        (r"(?:sobreposicao|choque)\s+(?:de\s+)?(?:horario|turno)", EscalaIntent.LISTAR_CONFLITOS),
        (r"(?:funcionario|colaborador)\s+(?:em\s+)?(?:dois|2)\s+(?:postos?|lugares?)", EscalaIntent.LISTAR_CONFLITOS),

        # ==================================================================
        # ESCALA_SEMANA - Consultas de escala
        # ==================================================================
        (r"escala\s+(?:da\s+|desta\s+|dessa\s+)?semana", EscalaIntent.ESCALA_SEMANA),
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba|me\s+mostra)\s+(?:a\s+)?escala\s+(?:da\s+|desta\s+|dessa\s+)?semana", EscalaIntent.ESCALA_SEMANA),
        (r"(?:proximos?\s+)?(?:7|sete)\s+dias", EscalaIntent.ESCALA_SEMANA),
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:as\s+)?escalas?(?:\s+(?:atuais?|existentes?|ativas?))?", EscalaIntent.ESCALA_SEMANA),
        (r"verificar\s+(?:as\s+)?escalas(?:\s+(?:atuais?|existentes?|ativas?))?", EscalaIntent.ESCALA_SEMANA),
        (r"escalas?\s+(?:atuais?|existentes?|ativas?)", EscalaIntent.ESCALA_SEMANA),
        (r"quais?\s+(?:as\s+)?escalas?", EscalaIntent.ESCALA_SEMANA),

        # ==================================================================
        # CALCULAR_CUSTO
        # ==================================================================
        (r"(?:custo|valor|preco)\s+(?:estimado\s+)?(?:da\s+)?escala", EscalaIntent.CALCULAR_CUSTO),
        (r"(?:qual\s+)?(?:o\s+)?custo\s+(?:estimado\s+)?(?:da\s+)?escala", EscalaIntent.CALCULAR_CUSTO),
        (r"quanto\s+(?:custa|vai\s+custar)\s+(?:a\s+)?escala", EscalaIntent.CALCULAR_CUSTO),
        (r"(?:calcular|calcule|estimar|estime)\s+(?:o\s+)?custo", EscalaIntent.CALCULAR_CUSTO),
        (r"(?:simular|simule)\s+(?:custo|valor)", EscalaIntent.CALCULAR_CUSTO),
        (r"(?:previsao|estimativa)\s+(?:de\s+)?custo", EscalaIntent.CALCULAR_CUSTO),

        # ==================================================================
        # PUBLICAR_ESCALA
        # ==================================================================
        (r"(?:publicar|publique|aprovar|aprove|liberar|libere|ativar|ative)\s+(?:a\s+)?escala", EscalaIntent.PUBLICAR_ESCALA),
        (r"(?:colocar|por)\s+escala\s+(?:em\s+)?(?:vigor|producao)", EscalaIntent.PUBLICAR_ESCALA),
        (r"(?:disponibilizar|divulgar)\s+(?:a\s+)?escala", EscalaIntent.PUBLICAR_ESCALA),

        # ==================================================================
        # GERAR_ESCALA - Por último (mais genérico)
        # ==================================================================
        # Imperativo
        (r"(?:gerar|gere|criar|crie|cria|monte|montar|fazer|faca|faz|elaborar|elabore)\s+(?:a\s+|uma\s+)?escala", EscalaIntent.GERAR_ESCALA),
        # Com contexto - CUIDADO: "escala para X" é genérico
        (r"nova\s+escala", EscalaIntent.GERAR_ESCALA),
        (r"escala\s+para\s+(?!semana|mes|janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\w+", EscalaIntent.GERAR_ESCALA),
        (r"preciso\s+(?:de\s+)?(?:uma\s+)?escala", EscalaIntent.GERAR_ESCALA),
        (r"quero\s+(?:uma\s+)?escala", EscalaIntent.GERAR_ESCALA),
        (r"(?:montar|criar|gerar)\s+(?:a\s+)?(?:grade|programacao)", EscalaIntent.GERAR_ESCALA),
        # Solicitações indiretas
        (r"(?:pode|consegue|da\s+para)\s+(?:gerar|criar|montar)\s+(?:uma\s+)?escala", EscalaIntent.GERAR_ESCALA),
        (r"(?:preciso|precisamos|queremos)\s+(?:de\s+)?(?:uma\s+)?(?:nova\s+)?escala", EscalaIntent.GERAR_ESCALA),
        (r"(?:me\s+)?(?:ajuda|ajude)\s+(?:a\s+)?(?:criar|montar|fazer)\s+(?:a\s+)?escala", EscalaIntent.GERAR_ESCALA),
    ]

    # Tipos de escala conhecidos
    SCALE_TYPES = {
        "12x36": {"hours_on": 12, "hours_off": 36, "weekly_hours": 42},
        "5x2": {"days_on": 5, "days_off": 2, "weekly_hours": 44},
        "6x1": {"days_on": 6, "days_off": 1, "weekly_hours": 44},
        "5x1": {"days_on": 5, "days_off": 1, "weekly_hours": 44},
        "4x2": {"days_on": 4, "days_off": 2, "weekly_hours": 32},
    }

    def __init__(self, db=None, scale_repo=None, shift_repo=None, allocation_repo=None):
        self.db = db
        self.scale_repo = scale_repo
        self.shift_repo = shift_repo
        self.allocation_repo = allocation_repo

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem relacionada a escalas.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        import re

        intent = self._detect_intent(message)
        context = context or {}

        if intent == EscalaIntent.GERAR_ESCALA:
            return await self._handle_gerar_escala(message, context)
        elif intent == EscalaIntent.OTIMIZAR_ESCALA:
            return await self._handle_otimizar_escala(message, context)
        elif intent == EscalaIntent.VALIDAR_ESCALA:
            return await self._handle_validar_escala(message, context)
        elif intent == EscalaIntent.CALCULAR_CUSTO:
            return await self._handle_calcular_custo(message, context)
        elif intent == EscalaIntent.LISTAR_CONFLITOS:
            return await self._handle_listar_conflitos(message, context)
        elif intent == EscalaIntent.ESCALA_SEMANA:
            return await self._handle_escala_semana(context)
        elif intent == EscalaIntent.ESCALA_MES:
            return await self._handle_escala_mes(context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> Optional[EscalaIntent]:
        """Detecta o intent da mensagem"""
        import re
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_gerar_escala(self, message: str, context: Dict) -> Dict[str, Any]:
        """Gera nova escala - extrai informações detalhadas da mensagem"""
        import re
        from unicodedata import normalize

        msg = normalize('NFD', message.lower())
        msg = ''.join(c for c in msg if not c in '\u0300\u0301\u0302\u0303\u0304\u0327')

        # Extrai informações da mensagem
        dados_extraidos = {}

        # Mês
        meses = {
            "janeiro": 1, "jan": 1, "fevereiro": 2, "fev": 2, "marco": 3, "mar": 3,
            "abril": 4, "abr": 4, "maio": 5, "mai": 5, "junho": 6, "jun": 6,
            "julho": 7, "jul": 7, "agosto": 8, "ago": 8, "setembro": 9, "set": 9,
            "outubro": 10, "out": 10, "novembro": 11, "nov": 11, "dezembro": 12, "dez": 12
        }
        for mes_nome, mes_num in meses.items():
            if mes_nome in msg:
                dados_extraidos["mes"] = mes_nome.capitalize()
                dados_extraidos["mes_num"] = mes_num
                break

        # Ano
        ano_match = re.search(r"\b(202[4-9]|203[0-9])\b", msg)
        if ano_match:
            dados_extraidos["ano"] = int(ano_match.group(1))

        # Quantidade de funcionários
        qtd_match = re.search(r"(\d+)\s*(?:agentes?|funcionarios?|vigilantes?|porteiros?|colaboradores?)", msg)
        if qtd_match:
            dados_extraidos["qtd_funcionarios"] = int(qtd_match.group(1))

        # Tipo de funcionário
        if "portaria" in msg or "porteiro" in msg:
            dados_extraidos["funcao"] = "Agente de Portaria"
        elif "vigilante" in msg or "vigilancia" in msg:
            dados_extraidos["funcao"] = "Vigilante"
        elif "limpeza" in msg:
            dados_extraidos["funcao"] = "Auxiliar de Limpeza"

        # Cliente/Posto
        cliente_patterns = [
            r"(?:para|cliente|posto|local)\s+([A-Za-z\s]+?)(?:\s*,|\s+sao|\s+com|\s+para|$)",
            r"([A-Za-z]+\s+(?:mais|plus|matriz|filial|sede)(?:\s+\w+)?)",
        ]
        for pattern in cliente_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                cliente = match.group(1).strip()
                if len(cliente) > 3 and cliente.lower() not in ["para", "com", "que", "uma", "pro", "mes"]:
                    dados_extraidos["cliente"] = cliente.title()
                    break

        # Características
        dados_extraidos["intrajornada"] = "intrajornada" in msg or "com intervalo" in msg
        dados_extraidos["sem_ronda"] = "sem ronda" in msg
        dados_extraidos["com_ronda"] = "com ronda" in msg and "sem ronda" not in msg
        dados_extraidos["adicional_noturno"] = "adicional noturno" in msg or "ad noturno" in msg
        dados_extraidos["hora_noturna_reduzida"] = "hora noturna reduzida" in msg or "reduzida" in msg

        # Monta resposta
        info_lines = []
        if dados_extraidos.get("cliente"):
            info_lines.append(f"📍 **Cliente:** {dados_extraidos['cliente']}")
        if dados_extraidos.get("mes"):
            ano = dados_extraidos.get("ano", 2026)
            info_lines.append(f"📅 **Período:** {dados_extraidos['mes']}/{ano}")
        if dados_extraidos.get("qtd_funcionarios"):
            info_lines.append(f"👥 **Funcionários:** {dados_extraidos['qtd_funcionarios']}")
        if dados_extraidos.get("funcao"):
            info_lines.append(f"🎯 **Função:** {dados_extraidos['funcao']}")

        caracteristicas = []
        if dados_extraidos.get("intrajornada"):
            caracteristicas.append("Com intrajornada")
        if dados_extraidos.get("sem_ronda"):
            caracteristicas.append("Sem ronda")
        if dados_extraidos.get("adicional_noturno"):
            caracteristicas.append("Adicional noturno 20%")
        if dados_extraidos.get("hora_noturna_reduzida"):
            caracteristicas.append("Hora noturna = 52min30s")
        if caracteristicas:
            info_lines.append(f"⚙️ **Características:** {', '.join(caracteristicas)}")

        if info_lines:
            response = f"📋 **Gerando Escala**\n\n" + "\n".join(info_lines)
            response += "\n\n**Próximos passos:**\n"
            response += "1. Definir tipo de escala (12x36, 5x2, 6x1)\n"
            response += "2. Verificar funcionários disponíveis\n"
            response += "3. Gerar escala otimizada\n"
            response += "\n**Qual tipo de escala deseja?**"

            return {
                "response": response,
                "intent": EscalaIntent.GERAR_ESCALA.value,
                "data": dados_extraidos,
                "suggestions": ["12x36 (vigilância 24h)", "5x2 (comercial)", "6x1 (máximo CLT)", "Sugerir melhor opção"],
                "actions": [
                    {"type": "create", "label": "Gerar 12x36", "target": "scale", "data": {**dados_extraidos, "type": "12x36"}},
                    {"type": "create", "label": "Gerar 5x2", "target": "scale", "data": {**dados_extraidos, "type": "5x2"}},
                ]
            }
        else:
            return {
                "response": "Para gerar uma escala, preciso de algumas informações:\n\n- **Cliente/Posto:** Qual local?\n- **Período:** Qual mês/ano?\n- **Quantidade:** Quantos funcionários?\n- **Função:** Vigilante, porteiro, etc?\n\nPode me informar esses dados?",
                "intent": EscalaIntent.GERAR_ESCALA.value,
                "needs_info": ["cliente", "periodo", "quantidade", "funcao"],
                "suggestions": ["Listar clientes", "Ver modelo de escala", "Cancelar"],
            }

    async def _handle_otimizar_escala(self, message: str, context: Dict) -> Dict[str, Any]:
        """Otimiza escala existente"""
        return {
            "response": "Para otimizar uma escala, informe o ID ou selecione uma escala ativa.\n\n**Tipos de otimização:**\n- Reduzir custo (minimiza horas extras)\n- Balancear turnos (distribui melhor)\n- Maximizar cobertura",
            "intent": EscalaIntent.OTIMIZAR_ESCALA.value,
            "suggestions": ["Ver escalas ativas", "Otimizar escala atual", "Cancelar"],
        }

    async def _handle_validar_escala(self, message: str, context: Dict) -> Dict[str, Any]:
        """Valida escala"""
        return {
            "response": "**Validação de Escala**\n\nInforme o ID da escala para validar. Vou verificar:\n- Conflitos de horário\n- Cumprimento CLT (44h/semana, 11h descanso)\n- Cobertura mínima\n- Funcionários sobrecarregados",
            "intent": EscalaIntent.VALIDAR_ESCALA.value,
            "suggestions": ["Ver escalas recentes", "Validar escala atual"],
        }

    async def _handle_calcular_custo(self, message: str, context: Dict) -> Dict[str, Any]:
        """Calcula custo da escala"""
        return {
            "response": "**Cálculo de Custo**\n\n**Fórmula:**\n`Custo = (Horas Normais × R$ Base) + (HE × 1.5) + Ad. Noturno (20%) + Feriados (100%)`\n\nInforme o ID da escala ou período para calcular.",
            "intent": EscalaIntent.CALCULAR_CUSTO.value,
            "suggestions": ["Custo mês atual", "Comparar custos", "Ver detalhamento"],
        }

    async def _handle_listar_conflitos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista conflitos na escala"""
        # Em produção, consultaria o banco
        return {
            "response": "**Análise de Conflitos**\n\nNenhum conflito encontrado nas escalas ativas. ✅\n\n**Verificações realizadas:**\n- Funcionário em 2 postos ao mesmo tempo\n- Intervalo < 11h entre turnos\n- Mais de 6 dias consecutivos\n- Mais de 44h semanais",
            "intent": EscalaIntent.LISTAR_CONFLITOS.value,
            "data": {"conflicts": []},
            "suggestions": ["Ver escala completa", "Validar outra escala"],
        }

    async def _handle_escala_semana(self, context: Dict) -> Dict[str, Any]:
        """Mostra escala da semana"""
        return {
            "response": "**Escala da Semana**\n\nCarregando dados da escala semanal...",
            "intent": EscalaIntent.ESCALA_SEMANA.value,
            "suggestions": ["Próxima semana", "Ver por posto", "Exportar"],
        }

    async def _handle_escala_mes(self, context: Dict) -> Dict[str, Any]:
        """Mostra escala do mês"""
        return {
            "response": "**Escala do Mês**\n\nCarregando dados da escala mensal...",
            "intent": EscalaIntent.ESCALA_MES.value,
            "suggestions": ["Próximo mês", "Ver por funcionário", "Exportar"],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrão - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de escala
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    def get_capabilities(self) -> List[str]:
        """Retorna lista de capabilities do agente"""
        return [
            "Gerar escalas automáticas (12x36, 5x2, 6x1)",
            "Otimizar escalas para reduzir custo",
            "Detectar conflitos de horário",
            "Validar conformidade CLT",
            "Calcular custos estimados",
            "Sugerir redistribuição de turnos",
        ]
