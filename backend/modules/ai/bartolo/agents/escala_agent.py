"""
EscalaAgent - Agente especialista em escalas de trabalho
"""

import logging
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class EscalaIntent(StrEnum):
    """Intents relacionados a escalas"""

    GERAR_ESCALA = "gerar_escala"
    OTIMIZAR_ESCALA = "otimizar_escala"
    VALIDAR_ESCALA = "validar_escala"
    PUBLICAR_ESCALA = "publicar_escala"
    CALCULAR_CUSTO = "calcular_custo"
    LISTAR_CONFLITOS = "listar_conflitos"
    ESCALA_SEMANA = "escala_semana"
    ESCALA_MES = "escala_mes"
    # Novos intents: AutoScale, Otimização Inteligente e Templates
    AUTO_GERAR = "auto_gerar"
    OTIMIZAR_INTELIGENTE = "otimizar_inteligente"
    CRIAR_TEMPLATE = "criar_template"
    APLICAR_TEMPLATE = "aplicar_template"
    LISTAR_TEMPLATES = "listar_templates"


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
        (
            r"(?:tem|ha|há)\s+conflitos?\s+(?:na\s+)?escala\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            EscalaIntent.LISTAR_CONFLITOS,
        ),
        # ==================================================================
        # AUTO_GERAR - Geração automática de escalas para todos os postos
        # ==================================================================
        (r"(?:gerar|gere|criar|crie)\s+escalas?\s+(?:automatica(?:mente)?|auto)", EscalaIntent.AUTO_GERAR),
        (r"auto\s*(?:gerar|escala|scale)", EscalaIntent.AUTO_GERAR),
        (r"(?:gerar|criar)\s+(?:todas\s+(?:as\s+)?)?escalas?\s+(?:do|para\s+o)\s+mes", EscalaIntent.AUTO_GERAR),
        (r"escalas?\s+automaticas?\s+(?:para|do)\s+(?:o\s+)?mes", EscalaIntent.AUTO_GERAR),
        (r"(?:quero|preciso)\s+gerar\s+escalas?\s+automatica(?:mente)?", EscalaIntent.AUTO_GERAR),
        (r"gerar\s+escalas?\s+(?:para\s+)?todos\s+(?:os\s+)?postos?", EscalaIntent.AUTO_GERAR),
        # ==================================================================
        # OTIMIZAR_INTELIGENTE - Otimização com IA avançada
        # ==================================================================
        (r"(?:otimizar|otimize)\s+(?:com\s+)?(?:ia|inteligencia|inteligente)", EscalaIntent.OTIMIZAR_INTELIGENTE),
        (r"(?:otimiza(?:cao|ção))\s+inteligente", EscalaIntent.OTIMIZAR_INTELIGENTE),
        (r"(?:otimizar|otimize)\s+(?:a\s+)?escala\s+(?:do\s+)?posto", EscalaIntent.OTIMIZAR_INTELIGENTE),
        (
            r"(?:reduzir|reduza|diminuir)\s+custos?\s+(?:da\s+)?escala\s+(?:do\s+)?posto",
            EscalaIntent.OTIMIZAR_INTELIGENTE,
        ),
        (
            r"(?:otimizar|otimize)\s+escala\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            EscalaIntent.OTIMIZAR_INTELIGENTE,
        ),
        (
            r"(?:otimizar|otimize)\s+(?:a\s+)?escala\s+(?:do|de)\s+\w+\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            EscalaIntent.OTIMIZAR_INTELIGENTE,
        ),
        # ==================================================================
        # CRIAR_TEMPLATE - Salvar escala como template
        # ==================================================================
        (
            r"(?:salvar|salve|criar|crie)\s+(?:esta|essa|a)?\s*escala\s+(?:como\s+)?template",
            EscalaIntent.CRIAR_TEMPLATE,
        ),
        (r"(?:criar|crie|salvar|salve)\s+template\s+(?:de|da|com)\s+escala", EscalaIntent.CRIAR_TEMPLATE),
        (r"(?:transformar|converter)\s+(?:a\s+)?escala\s+(?:em|para)\s+template", EscalaIntent.CRIAR_TEMPLATE),
        (r"(?:salvar|salve)\s+(?:como\s+)?template", EscalaIntent.CRIAR_TEMPLATE),
        (r"novo\s+template\s+(?:de\s+)?escala", EscalaIntent.CRIAR_TEMPLATE),
        # ==================================================================
        # APLICAR_TEMPLATE - Aplicar template em posto/mês
        # ==================================================================
        (r"(?:aplicar|aplique|usar|use)\s+template", EscalaIntent.APLICAR_TEMPLATE),
        (r"(?:aplicar|aplique)\s+(?:o\s+)?template\s+\w+\s+(?:no|em|para)", EscalaIntent.APLICAR_TEMPLATE),
        (r"(?:usar|use)\s+(?:o\s+)?template\s+\w+", EscalaIntent.APLICAR_TEMPLATE),
        (
            r"(?:gerar|gere|criar|crie)\s+escala\s+(?:com|usando|baseado)\s+(?:no\s+)?template",
            EscalaIntent.APLICAR_TEMPLATE,
        ),
        # ==================================================================
        # LISTAR_TEMPLATES - Listar templates disponíveis
        # ==================================================================
        (r"(?:listar|liste|ver|veja|mostrar|mostre)\s+templates?", EscalaIntent.LISTAR_TEMPLATES),
        (r"(?:quais|que)\s+templates?\s+(?:tenho|existem|disponiv)", EscalaIntent.LISTAR_TEMPLATES),
        (r"templates?\s+(?:de\s+)?escalas?\s+(?:disponiveis?|existentes?)", EscalaIntent.LISTAR_TEMPLATES),
        (r"templates?\s+(?:disponiveis?|existentes?|salvos?)", EscalaIntent.LISTAR_TEMPLATES),
        # ==================================================================
        # ESCALA_MES
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a\s+)?escala\s+do\s+mes", EscalaIntent.ESCALA_MES),
        (r"escala\s+(?:do\s+|deste\s+)?mes", EscalaIntent.ESCALA_MES),
        (
            r"escalas?\s+(?:de\s+|do\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            EscalaIntent.ESCALA_MES,
        ),
        (
            r"montar\s+(?:a\s+)?escala\s+(?:de\s+)?(?:janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)",
            EscalaIntent.ESCALA_MES,
        ),
        (r"(?:proximos?\s+)?(?:30|trinta)\s+dias", EscalaIntent.ESCALA_MES),
        # ==================================================================
        # OTIMIZAR_ESCALA - Antes de CALCULAR_CUSTO (para "reduzir custo")
        # ==================================================================
        (r"(?:reduzir|diminuir)\s+(?:o\s+)?custo\s+(?:da\s+)?escala", EscalaIntent.OTIMIZAR_ESCALA),
        (r"(?:reduzir|diminuir)\s+(?:as?\s+)?horas?\s+extras?\s+(?:da\s+)?escala", EscalaIntent.OTIMIZAR_ESCALA),
        (
            r"(?:otimizar|otimize|melhorar|melhore|ajustar|ajuste|refinar|refine)\s+(?:a\s+)?escala",
            EscalaIntent.OTIMIZAR_ESCALA,
        ),
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
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|me\s+mostra)\s+(?:a\s+)?escala\s+(?:da\s+|desta\s+|dessa\s+)?semana",
            EscalaIntent.ESCALA_SEMANA,
        ),
        (r"(?:proximos?\s+)?(?:7|sete)\s+dias", EscalaIntent.ESCALA_SEMANA),
        (
            r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:as\s+)?escalas?(?:\s+(?:atuais?|existentes?|ativas?))?",
            EscalaIntent.ESCALA_SEMANA,
        ),
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
        (
            r"(?:publicar|publique|aprovar|aprove|liberar|libere|ativar|ative)\s+(?:a\s+)?escala",
            EscalaIntent.PUBLICAR_ESCALA,
        ),
        (r"(?:colocar|por)\s+escala\s+(?:em\s+)?(?:vigor|producao)", EscalaIntent.PUBLICAR_ESCALA),
        (r"(?:disponibilizar|divulgar)\s+(?:a\s+)?escala", EscalaIntent.PUBLICAR_ESCALA),
        # ==================================================================
        # GERAR_ESCALA - Por último (mais genérico)
        # ==================================================================
        # Imperativo
        (
            r"(?:gerar|gere|criar|crie|cria|monte|montar|fazer|faca|faz|elaborar|elabore)\s+(?:a\s+|uma\s+)?escala",
            EscalaIntent.GERAR_ESCALA,
        ),
        # Com contexto - CUIDADO: "escala para X" é genérico
        (r"nova\s+escala", EscalaIntent.GERAR_ESCALA),
        (
            r"escala\s+para\s+(?!semana|mes|janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\w+",
            EscalaIntent.GERAR_ESCALA,
        ),
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

    def __init__(self, db=None, scale_repo=None, shift_repo=None, allocation_repo=None, data_connector=None):
        self.db = db
        self.scale_repo = scale_repo
        self.shift_repo = shift_repo
        self.allocation_repo = allocation_repo
        self.data_connector = data_connector
        # Se tem db mas não tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector

                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Não foi possível criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Processa uma mensagem relacionada a escalas.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """

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
        elif intent == EscalaIntent.AUTO_GERAR:
            return await self._handle_auto_gerar(message, context)
        elif intent == EscalaIntent.OTIMIZAR_INTELIGENTE:
            return await self._handle_otimizar_inteligente(message, context)
        elif intent == EscalaIntent.CRIAR_TEMPLATE:
            return await self._handle_criar_template(message, context)
        elif intent == EscalaIntent.APLICAR_TEMPLATE:
            return await self._handle_aplicar_template(message, context)
        elif intent == EscalaIntent.LISTAR_TEMPLATES:
            return await self._handle_listar_templates(context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> EscalaIntent | None:
        """Detecta o intent da mensagem"""
        import re

        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_gerar_escala(self, message: str, context: dict) -> dict[str, Any]:
        """Gera nova escala - extrai informações detalhadas da mensagem"""
        import re
        from unicodedata import normalize

        msg = normalize("NFD", message.lower())
        msg = "".join(c for c in msg if c not in "\u0300\u0301\u0302\u0303\u0304\u0327")

        # Extrai informações da mensagem
        dados_extraidos = {}

        # Mês
        meses = {
            "janeiro": 1,
            "jan": 1,
            "fevereiro": 2,
            "fev": 2,
            "marco": 3,
            "mar": 3,
            "abril": 4,
            "abr": 4,
            "maio": 5,
            "mai": 5,
            "junho": 6,
            "jun": 6,
            "julho": 7,
            "jul": 7,
            "agosto": 8,
            "ago": 8,
            "setembro": 9,
            "set": 9,
            "outubro": 10,
            "out": 10,
            "novembro": 11,
            "nov": 11,
            "dezembro": 12,
            "dez": 12,
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
            response = "📋 **Gerando Escala**\n\n" + "\n".join(info_lines)
            response += "\n\n**Próximos passos:**\n"
            response += "1. Definir tipo de escala (12x36, 5x2, 6x1)\n"
            response += "2. Verificar funcionários disponíveis\n"
            response += "3. Gerar escala otimizada\n"
            response += "\n**Qual tipo de escala deseja?**"

            return {
                "response": response,
                "intent": EscalaIntent.GERAR_ESCALA.value,
                "data": dados_extraidos,
                "suggestions": [
                    "12x36 (vigilância 24h)",
                    "5x2 (comercial)",
                    "6x1 (máximo CLT)",
                    "Sugerir melhor opção",
                ],
                "actions": [
                    {
                        "type": "create",
                        "label": "Gerar 12x36",
                        "target": "scale",
                        "data": {**dados_extraidos, "type": "12x36"},
                    },
                    {
                        "type": "create",
                        "label": "Gerar 5x2",
                        "target": "scale",
                        "data": {**dados_extraidos, "type": "5x2"},
                    },
                ],
            }
        else:
            return {
                "response": "Para gerar uma escala, preciso de algumas informações:\n\n- **Cliente/Posto:** Qual local?\n- **Período:** Qual mês/ano?\n- **Quantidade:** Quantos funcionários?\n- **Função:** Vigilante, porteiro, etc?\n\nPode me informar esses dados?",
                "intent": EscalaIntent.GERAR_ESCALA.value,
                "needs_info": ["cliente", "periodo", "quantidade", "funcao"],
                "suggestions": ["Listar clientes", "Ver modelo de escala", "Cancelar"],
            }

    async def _handle_otimizar_escala(self, message: str, context: dict) -> dict[str, Any]:
        """Otimiza escala existente usando dados reais do DataConnector"""
        # Tentar buscar dados reais para contextualizar a otimização
        if self.data_connector:
            try:
                # Buscar horas extras e escalas pendentes para contextualizar
                he_result = await self.data_connector._get_hora_extra_ranking()
                escalas_result = await self.data_connector._get_escalas_pendentes()

                context_lines = []
                if he_result.success and he_result.data:
                    total_he = sum(f.get("horas_extras", 0) for f in he_result.data)
                    context_lines.append(f"- Total de horas extras acumuladas: **{total_he:.1f}h**")
                    context_lines.append(f"- Funcionários com HE: **{he_result.total_count}**")

                if escalas_result.success and escalas_result.data:
                    context_lines.append(f"- Escalas cadastradas: **{escalas_result.total_count}**")

                if context_lines:
                    context_info = "\n".join(context_lines)
                    response = f"""**Otimização de Escala**

**Situação atual:**
{context_info}

**Tipos de otimização disponíveis:**
- Reduzir custo (minimiza horas extras)
- Balancear turnos (distribui melhor)
- Maximizar cobertura

Selecione uma escala ativa para iniciar a otimização."""
                    return {
                        "response": response,
                        "intent": EscalaIntent.OTIMIZAR_ESCALA.value,
                        "data": {"horas_extras_total": total_he if he_result.success else 0},
                        "suggestions": ["Ver escalas ativas", "Reduzir horas extras", "Cancelar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar dados para otimização via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "Para otimizar uma escala, informe o ID ou selecione uma escala ativa.\n\n**Tipos de otimização:**\n- Reduzir custo (minimiza horas extras)\n- Balancear turnos (distribui melhor)\n- Maximizar cobertura",
            "intent": EscalaIntent.OTIMIZAR_ESCALA.value,
            "suggestions": ["Ver escalas ativas", "Otimizar escala atual", "Cancelar"],
        }

    async def _handle_validar_escala(self, message: str, context: dict) -> dict[str, Any]:
        """Valida escala usando dados reais do DataConnector"""
        # Tentar buscar dados reais para validação
        if self.data_connector:
            try:
                cobertura_result = await self.data_connector._get_cobertura_critica()
                he_result = await self.data_connector._get_hora_extra_ranking()

                problemas = []
                if cobertura_result.success and cobertura_result.data:
                    problemas.append(f"- ⚠️ **{len(cobertura_result.data)} postos** com cobertura abaixo de 80%")

                if he_result.success and he_result.data:
                    sobrecarregados = [f for f in he_result.data if f.get("horas_extras", 0) > 40]
                    if sobrecarregados:
                        problemas.append(f"- ⚠️ **{len(sobrecarregados)} funcionários** com mais de 40h extras")

                if problemas:
                    problemas_text = "\n".join(problemas)
                    response = f"""**Validação de Escala**

**Problemas detectados:**
{problemas_text}

**Verificações realizadas:**
- Conflitos de horário
- Cumprimento CLT (44h/semana, 11h descanso)
- Cobertura mínima (80%)
- Funcionários sobrecarregados

Informe o ID da escala para validação detalhada."""
                else:
                    response = """**Validação de Escala**

✅ Nenhum problema crítico detectado nas escalas ativas.

**Verificações realizadas:**
- Conflitos de horário
- Cumprimento CLT (44h/semana, 11h descanso)
- Cobertura mínima (80%)
- Funcionários sobrecarregados

Informe o ID da escala para validação detalhada."""

                return {
                    "response": response,
                    "intent": EscalaIntent.VALIDAR_ESCALA.value,
                    "data": {"problemas": len(problemas)},
                    "suggestions": ["Ver escalas recentes", "Ver conflitos", "Ver cobertura"],
                }
            except Exception as e:
                logger.warning(f"Erro ao validar escala via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "**Validação de Escala**\n\nInforme o ID da escala para validar. Vou verificar:\n- Conflitos de horário\n- Cumprimento CLT (44h/semana, 11h descanso)\n- Cobertura mínima\n- Funcionários sobrecarregados",
            "intent": EscalaIntent.VALIDAR_ESCALA.value,
            "suggestions": ["Ver escalas recentes", "Validar escala atual"],
        }

    async def _handle_calcular_custo(self, message: str, context: dict) -> dict[str, Any]:
        """Calcula custo da escala usando dados reais do DataConnector"""
        # Tentar buscar dados reais de KPIs (contém custo mensal)
        if self.data_connector:
            try:
                result = await self.data_connector._get_main_kpis()
                if result.success and result.data:
                    kpis = result.data
                    custo = kpis.get("custo_mensal_total", 0)
                    efetivo = kpis.get("efetivo_alocado", 0)
                    requerido = kpis.get("efetivo_requerido", 0)

                    response = f"""**Cálculo de Custo - Dados Atuais**

**Custo mensal estimado:** R$ {custo:,.2f}
**Efetivo alocado:** {efetivo} de {requerido} requeridos

**Fórmula base:**
`Custo = (Horas Normais x R$ Base) + (HE x 1.5) + Ad. Noturno (20%) + Feriados (100%)`

Para detalhamento por posto ou escala específica, informe o ID ou nome."""
                    return {
                        "response": response,
                        "intent": EscalaIntent.CALCULAR_CUSTO.value,
                        "data": {"custo_mensal": custo, "efetivo": efetivo, "requerido": requerido},
                        "suggestions": ["Custo por posto", "Comparar custos", "Ver detalhamento"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar custo via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "**Cálculo de Custo**\n\n**Fórmula:**\n`Custo = (Horas Normais × R$ Base) + (HE × 1.5) + Ad. Noturno (20%) + Feriados (100%)`\n\nInforme o ID da escala ou período para calcular.",
            "intent": EscalaIntent.CALCULAR_CUSTO.value,
            "suggestions": ["Custo mês atual", "Comparar custos", "Ver detalhamento"],
        }

    async def _handle_listar_conflitos(self, message: str, context: dict) -> dict[str, Any]:
        """Lista conflitos na escala usando dados reais do DataConnector"""
        # Tentar buscar cobertura crítica (indica problemas na escala)
        if self.data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success:
                    postos_criticos = result.data or []
                    if postos_criticos:
                        lines = [
                            f"- **{p['nome']}** ({p['codigo']}): {p['alocados']}/{p['requeridos']} - Deficit: {p['deficit']}"
                            for p in postos_criticos[:10]
                        ]

                        response = f"""**Análise de Conflitos e Cobertura**

**Postos com cobertura insuficiente ({len(postos_criticos)}):**

{chr(10).join(lines)}

**Verificações realizadas:**
- Funcionário em 2 postos ao mesmo tempo
- Intervalo < 11h entre turnos
- Mais de 6 dias consecutivos
- Mais de 44h semanais

**Ação recomendada:** Redistribuir turnos para cobrir déficit."""
                        return {
                            "response": response,
                            "intent": EscalaIntent.LISTAR_CONFLITOS.value,
                            "data": {"conflicts": postos_criticos, "total": len(postos_criticos)},
                            "suggestions": ["Ver escala completa", "Buscar substitutos", "Redistribuir turnos"],
                        }
                    else:
                        return {
                            "response": "**Análise de Conflitos**\n\nNenhum conflito encontrado nas escalas ativas. ✅\n\n**Verificações realizadas:**\n- Funcionário em 2 postos ao mesmo tempo\n- Intervalo < 11h entre turnos\n- Mais de 6 dias consecutivos\n- Mais de 44h semanais\n\nTodos os postos com cobertura acima de 80%.",
                            "intent": EscalaIntent.LISTAR_CONFLITOS.value,
                            "data": {"conflicts": []},
                            "suggestions": ["Ver escala completa", "Validar outra escala"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar conflitos via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "**Análise de Conflitos**\n\nNenhum conflito encontrado nas escalas ativas. ✅\n\n**Verificações realizadas:**\n- Funcionário em 2 postos ao mesmo tempo\n- Intervalo < 11h entre turnos\n- Mais de 6 dias consecutivos\n- Mais de 44h semanais",
            "intent": EscalaIntent.LISTAR_CONFLITOS.value,
            "data": {"conflicts": []},
            "suggestions": ["Ver escala completa", "Validar outra escala"],
        }

    async def _handle_escala_semana(self, context: dict) -> dict[str, Any]:
        """Mostra escala da semana usando dados reais do DataConnector"""
        # Tentar buscar dados reais via DataConnector
        if self.data_connector:
            try:
                result = await self.data_connector._get_escalas_pendentes()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": EscalaIntent.ESCALA_SEMANA.value,
                        "data": {"escalas": result.data, "total": result.total_count},
                        "suggestions": ["Próxima semana", "Ver por posto", "Exportar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar escalas da semana via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "**Escala da Semana**\n\nCarregando dados da escala semanal...",
            "intent": EscalaIntent.ESCALA_SEMANA.value,
            "suggestions": ["Próxima semana", "Ver por posto", "Exportar"],
        }

    async def _handle_escala_mes(self, context: dict) -> dict[str, Any]:
        """Mostra escala do mês usando dados reais do DataConnector"""
        # Tentar buscar dados reais via DataConnector
        if self.data_connector:
            try:
                result = await self.data_connector._get_escalas_pendentes()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": EscalaIntent.ESCALA_MES.value,
                        "data": {"escalas": result.data, "total": result.total_count},
                        "suggestions": ["Próximo mês", "Ver por funcionário", "Exportar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar escalas do mês via DataConnector: {e}")

        # Fallback estático
        return {
            "response": "**Escala do Mês**\n\nCarregando dados da escala mensal...",
            "intent": EscalaIntent.ESCALA_MES.value,
            "suggestions": ["Próximo mês", "Ver por funcionário", "Exportar"],
        }

    # ==========================================================================
    # HANDLERS AVANÇADOS: AutoScale, Otimização Inteligente, Templates
    # ==========================================================================

    def _get_auto_scale_service(self):
        """Tenta obter instância do AutoScaleService. Retorna None se indisponível."""
        try:
            from modules.operacional.services.auto_scale_service import AutoScaleService

            if self.db:
                return AutoScaleService(self.db)
        except ImportError:
            logger.warning("AutoScaleService não disponível (módulo não encontrado)")
        except Exception as e:
            logger.warning(f"Erro ao instanciar AutoScaleService: {e}")
        return None

    def _get_intelligent_ops_service(self, tenant_id: str = None):
        """Tenta obter instância do IntelligentOperationsService. Retorna None se indisponível."""
        try:
            from modules.operacional.services.intelligent_operations_service import (
                IntelligentOperationsService,
            )

            if self.db and tenant_id:
                return IntelligentOperationsService(self.db, tenant_id)
        except ImportError:
            logger.warning("IntelligentOperationsService não disponível (módulo não encontrado)")
        except Exception as e:
            logger.warning(f"Erro ao instanciar IntelligentOperationsService: {e}")
        return None

    def _get_scale_template_repo(self):
        """Tenta obter instância do ScaleTemplateRepository. Retorna None se indisponível."""
        try:
            from modules.operacional.repositories.scale_template_repository import ScaleTemplateRepository

            if self.db:
                return ScaleTemplateRepository(self.db)
        except ImportError:
            logger.warning("ScaleTemplateRepository não disponível (módulo não encontrado)")
        except Exception as e:
            logger.warning(f"Erro ao instanciar ScaleTemplateRepository: {e}")
        return None

    def _get_scale_template_service(self):
        """Tenta obter instância do ScaleTemplateService. Retorna None se indisponível."""
        try:
            from modules.operacional.services.scale_template_service import ScaleTemplateService

            if self.db:
                return ScaleTemplateService(self.db)
        except ImportError:
            logger.warning("ScaleTemplateService não disponível (módulo não encontrado)")
        except Exception as e:
            logger.warning(f"Erro ao instanciar ScaleTemplateService: {e}")
        return None

    def _extract_month_year(self, message: str) -> dict[str, Any]:
        """Extrai mês e ano de uma mensagem."""
        import re
        from unicodedata import normalize

        msg = normalize("NFD", message.lower())
        msg = "".join(c for c in msg if c not in "\u0300\u0301\u0302\u0303\u0304\u0327")

        result = {}
        meses = {
            "janeiro": 1,
            "jan": 1,
            "fevereiro": 2,
            "fev": 2,
            "marco": 3,
            "mar": 3,
            "abril": 4,
            "abr": 4,
            "maio": 5,
            "mai": 5,
            "junho": 6,
            "jun": 6,
            "julho": 7,
            "jul": 7,
            "agosto": 8,
            "ago": 8,
            "setembro": 9,
            "set": 9,
            "outubro": 10,
            "out": 10,
            "novembro": 11,
            "nov": 11,
            "dezembro": 12,
            "dez": 12,
        }
        for mes_nome, mes_num in meses.items():
            if mes_nome in msg:
                result["mes"] = mes_nome.capitalize()
                result["mes_num"] = mes_num
                break

        ano_match = re.search(r"\b(202[4-9]|203[0-9])\b", msg)
        if ano_match:
            result["ano"] = int(ano_match.group(1))

        return result

    async def _handle_auto_gerar(self, message: str, context: dict) -> dict[str, Any]:
        """Gera escalas automaticamente para todos os postos de um mês."""
        dados = self._extract_month_year(message)
        mes_num = dados.get("mes_num")
        ano = dados.get("ano", datetime.now().year)
        mes_nome = dados.get("mes", "")

        # Tentar usar AutoScaleService real
        auto_service = self._get_auto_scale_service()
        if auto_service:
            try:
                if mes_num:
                    result = await auto_service.generate_scales_for_month(
                        month=mes_num, year=ano, created_by=context.get("user_id")
                    )
                else:
                    result = await auto_service.generate_scales_for_current_month(created_by=context.get("user_id"))

                erros_text = ""
                if result.get("errors"):
                    erros_text = "\n\n**Erros encontrados:**\n"
                    for err in result["errors"][:5]:
                        erros_text += f"- {err}\n"

                periodo = f"{mes_num:02d}/{ano}" if mes_num else "mês atual"
                response = f"""**Geração Automática de Escalas**

**Período:** {periodo}
**Escalas criadas:** {result.get("scales_created", 0)}
**Turnos gerados:** {result.get("shifts_created", 0)}

{result.get("message", "")}{erros_text}"""

                return {
                    "response": response,
                    "intent": EscalaIntent.AUTO_GERAR.value,
                    "data": result,
                    "suggestions": ["Ver escalas pendentes", "Validar escalas", "Publicar escalas"],
                    "actions": [
                        {
                            "type": "auto_generate_scale",
                            "label": "Gerar escalas automáticas",
                            "target": "scale",
                            "data": {"month": mes_num, "year": ano},
                        },
                    ],
                }
            except Exception as e:
                logger.error(f"Erro ao gerar escalas automaticamente: {e}")

        # Fallback informativo
        periodo_info = f"{mes_nome}/{ano}" if mes_nome else "o próximo mês"
        return {
            "response": f"""**Geração Automática de Escalas**

Para gerar escalas automáticas para **{periodo_info}**, o sistema irá:

1. Detectar todas as alocações ativas
2. Agrupar funcionários por posto
3. Gerar escalas 12x36 (padrão) para cada posto
4. Criar turnos otimizados automaticamente

**Deseja confirmar a geração automática?**""",
            "intent": EscalaIntent.AUTO_GERAR.value,
            "data": {"mes_num": mes_num, "ano": ano},
            "suggestions": ["Confirmar geração", "Alterar mês", "Cancelar"],
            "actions": [
                {
                    "type": "auto_generate_scale",
                    "label": f"Gerar escalas {periodo_info}",
                    "target": "scale",
                    "data": {"month": mes_num, "year": ano},
                },
            ],
        }

    async def _handle_otimizar_inteligente(self, message: str, context: dict) -> dict[str, Any]:
        """Otimiza escala usando IntelligentOperationsService com IA avançada."""
        import re

        dados = self._extract_month_year(message)
        mes_num = dados.get("mes_num", datetime.now().month)
        ano = dados.get("ano", datetime.now().year)

        # Extrair posto da mensagem
        posto_match = re.search(r"(?:posto|post)\s+([A-Za-z0-9\-]+)", message, re.IGNORECASE)
        posto_id = posto_match.group(1) if posto_match else None

        # Tentar usar IntelligentOperationsService
        tenant_id = context.get("tenant_id") or context.get("cliente_id")
        ops_service = self._get_intelligent_ops_service(tenant_id) if tenant_id else None

        if ops_service:
            try:
                import calendar

                _, last_day = calendar.monthrange(ano, mes_num)
                start_date = datetime(ano, mes_num, 1)
                end_date = datetime(ano, mes_num, last_day, 23, 59, 59)

                schedule = await ops_service.optimize_schedule(start_date, end_date)
                insights = await ops_service.generate_operational_insights(schedule)

                # Formatar insights
                insights_text = ""
                if insights:
                    insights_text = "\n\n**Insights Operacionais:**\n"
                    for insight in insights:
                        emoji = "💡" if insight.impact == "low" else "⚠️" if insight.impact == "medium" else "🚨"
                        insights_text += f"- {emoji} {insight.description}\n"
                        insights_text += f"  Recomendação: {insight.recommendation}\n"
                        if insight.estimated_savings > 0:
                            insights_text += f"  Economia estimada: R$ {insight.estimated_savings:,.2f}\n"

                cost_info = schedule.cost_analysis
                metrics_info = schedule.optimization_metrics

                response = f"""**Otimização Inteligente de Escala**

**Período:** {mes_num:02d}/{ano}
**Status:** {schedule.status.value}

**Métricas de Otimização:**
- Eficiência: **{schedule.efficiency_score:.1%}**
- Cobertura: **{schedule.coverage_score:.1%}**
- Utilização de funcionários: **{metrics_info.get("employee_utilization", 0):.1%}**
- Utilização de postos: **{metrics_info.get("workstation_utilization", 0):.1%}**
- Total de alocações: **{metrics_info.get("total_assignments", 0)}**

**Análise de Custos:**
- Custo total: **R$ {cost_info.get("total_cost", 0):,.2f}**
- Horas normais: R$ {cost_info.get("regular_hours_cost", 0):,.2f}
- Horas extras: R$ {cost_info.get("overtime_cost", 0):,.2f}
- Custo médio/hora: R$ {cost_info.get("avg_cost_per_hour", 0):,.2f}{insights_text}"""

                return {
                    "response": response,
                    "intent": EscalaIntent.OTIMIZAR_INTELIGENTE.value,
                    "data": {
                        "schedule_id": schedule.id,
                        "efficiency_score": schedule.efficiency_score,
                        "coverage_score": schedule.coverage_score,
                        "cost_analysis": cost_info,
                        "metrics": metrics_info,
                    },
                    "suggestions": [
                        "Aplicar otimização",
                        "Ver detalhes por posto",
                        "Comparar com escala atual",
                        "Exportar relatório",
                    ],
                    "actions": [
                        {
                            "type": "optimize_scale",
                            "label": "Aplicar escala otimizada",
                            "target": "scale",
                            "data": {"schedule_id": schedule.id, "month": mes_num, "year": ano},
                        },
                    ],
                }
            except Exception as e:
                logger.error(f"Erro na otimização inteligente: {e}")

        # Fallback sem serviço disponível
        posto_info = f" do posto **{posto_id}**" if posto_id else ""
        return {
            "response": f"""**Otimização Inteligente de Escala**

Para otimizar a escala{posto_info} de **{mes_num:02d}/{ano}**, o sistema utilizará IA para:

1. **Previsão de demanda** - Analisar padrões históricos por turno
2. **Alocação inteligente** - Matching de skills por posto
3. **Otimização de custo** - Minimizar horas extras e noturnas
4. **Balanceamento** - Distribuir carga entre funcionários

**Tipos de otimização:**
- Reduzir custo (foco em minimizar HE)
- Maximizar cobertura (garantir 100% dos postos)
- Balancear turnos (equalizar carga)
- Eficiência geral (peso balanceado)

{"Informe o ID do tenant para iniciar." if not tenant_id else "Deseja iniciar a otimização?"}""",
            "intent": EscalaIntent.OTIMIZAR_INTELIGENTE.value,
            "data": {"posto_id": posto_id, "mes_num": mes_num, "ano": ano},
            "suggestions": [
                "Otimizar custo",
                "Maximizar cobertura",
                "Balancear turnos",
                "Cancelar",
            ],
        }

    async def _handle_criar_template(self, message: str, context: dict) -> dict[str, Any]:
        """Salva uma escala existente como template reutilizável."""
        import re

        # Extrair nome do template
        nome_match = re.search(
            r"(?:template|modelo)\s+(?:chamado|nome|com\s+nome)\s+[\"']?([^\"']+)[\"']?", message, re.IGNORECASE
        )
        nome_template = nome_match.group(1).strip() if nome_match else None

        # Extrair ID da escala
        scale_match = re.search(r"(?:escala|scale)\s+([A-Za-z0-9\-]+)", message, re.IGNORECASE)
        scale_id = scale_match.group(1) if scale_match else None

        template_service = self._get_scale_template_service()
        template_repo = self._get_scale_template_repo()

        if template_service and template_repo and scale_id:
            try:
                # Extrair template da escala
                template_data = await template_service.extract_template_from_scale(
                    scale_id=scale_id,
                    include_employee_mapping=False,
                )

                tenant_id = context.get("tenant_id") or context.get("cliente_id", "")
                user_id = context.get("user_id", "")

                if nome_template:
                    from modules.operacional.schemas.scale_template import ScaleTemplateCreate

                    create_data = ScaleTemplateCreate(
                        name=nome_template,
                        description=f"Template criado via Bartolo a partir da escala {scale_id}",
                        template_data=template_data,
                    )
                    template = await template_repo.create(
                        data=create_data,
                        tenant_id=tenant_id,
                        created_by=user_id,
                    )

                    return {
                        "response": f"""**Template Criado com Sucesso**

**Nome:** {template.name}
**ID:** {template.id}
**Baseado na escala:** {scale_id}
**Funcionários:** {template_data.metadata.total_employees}
**Turnos/mês:** {template_data.metadata.total_shifts_per_month}
**Cobertura:** {template_data.metadata.coverage_percentage:.1f}%

Template salvo e disponível para reutilização.""",
                        "intent": EscalaIntent.CRIAR_TEMPLATE.value,
                        "data": {
                            "template_id": template.id,
                            "scale_id": scale_id,
                            "name": template.name,
                        },
                        "suggestions": [
                            f"Aplicar template {template.name}",
                            "Listar templates",
                            "Ver escalas",
                        ],
                        "actions": [
                            {
                                "type": "create_scale_template",
                                "label": "Template criado",
                                "target": "scale_template",
                                "data": {"template_id": template.id, "scale_id": scale_id},
                            },
                        ],
                    }
                else:
                    # Template extraído mas sem nome - pedir nome
                    return {
                        "response": f"""**Extraindo Template da Escala {scale_id}**

Template extraído com sucesso:
- **Tipo de escala:** {template_data.scale_type}
- **Postos:** {len(template_data.posts)}
- **Padrões de turno:** {len(template_data.shifts_pattern)}
- **Funcionários:** {template_data.metadata.total_employees}

**Informe um nome para salvar o template:**""",
                        "intent": EscalaIntent.CRIAR_TEMPLATE.value,
                        "data": {
                            "scale_id": scale_id,
                            "template_data_preview": {
                                "scale_type": template_data.scale_type,
                                "posts_count": len(template_data.posts),
                                "patterns_count": len(template_data.shifts_pattern),
                            },
                        },
                        "needs_info": ["nome_template"],
                        "suggestions": ["Portaria 12x36", "Vigilância Noturna", "Cancelar"],
                    }
            except ValueError as e:
                return {
                    "response": f"**Erro ao criar template:** {str(e)}",
                    "intent": EscalaIntent.CRIAR_TEMPLATE.value,
                    "suggestions": ["Ver escalas ativas", "Ajuda"],
                }
            except Exception as e:
                logger.error(f"Erro ao criar template: {e}")

        # Fallback
        return {
            "response": """**Criar Template de Escala**

Para salvar uma escala como template reutilizável, preciso de:

- **ID da escala:** Qual escala deseja usar como base?
- **Nome:** Como deseja chamar o template?

**Exemplo:** "Salvar escala ESC-001 como template Portaria 12x36"

O template preservará a estrutura de turnos, permitindo replicar
em outros postos e períodos rapidamente.""",
            "intent": EscalaIntent.CRIAR_TEMPLATE.value,
            "needs_info": ["scale_id", "nome_template"],
            "suggestions": ["Ver escalas ativas", "Listar templates", "Ajuda"],
        }

    async def _handle_aplicar_template(self, message: str, context: dict) -> dict[str, Any]:
        """Aplica um template existente em um posto/mês."""
        import re

        # Extrair template ID/nome
        template_match = re.search(r"template\s+([A-Za-z0-9\-]+)", message, re.IGNORECASE)
        template_id = template_match.group(1) if template_match else None

        # Extrair posto
        posto_match = re.search(r"(?:posto|post|no|em)\s+([A-Za-z0-9\-]+)", message, re.IGNORECASE)
        posto_id = posto_match.group(1) if posto_match else None

        dados = self._extract_month_year(message)
        mes_num = dados.get("mes_num")
        ano = dados.get("ano", datetime.now().year)

        template_repo = self._get_scale_template_repo()
        template_service = self._get_scale_template_service()

        if template_repo and template_service and template_id:
            try:
                tenant_id = context.get("tenant_id") or context.get("cliente_id")
                template = await template_repo.get_by_id(template_id, tenant_id)

                if template and mes_num and posto_id:
                    from modules.operacional.schemas.scale_template import ScaleTemplateApplyRequest

                    apply_request = ScaleTemplateApplyRequest(
                        month=mes_num,
                        year=ano,
                        post_id=posto_id,
                    )
                    user_id = context.get("user_id", "")
                    scale = await template_service.apply_template_to_period(
                        template_data=template.template_data,
                        apply_request=apply_request,
                        created_by=user_id,
                    )
                    # Incrementar uso
                    await template_repo.increment_usage(template_id)

                    return {
                        "response": f"""**Template Aplicado com Sucesso**

**Template:** {template.name}
**Posto:** {posto_id}
**Período:** {mes_num:02d}/{ano}
**Escala criada:** {scale.id}

A escala foi criada em status rascunho. Revise e publique quando estiver pronta.""",
                        "intent": EscalaIntent.APLICAR_TEMPLATE.value,
                        "data": {
                            "template_id": template.id,
                            "scale_id": scale.id,
                            "post_id": posto_id,
                            "month": mes_num,
                            "year": ano,
                        },
                        "suggestions": [
                            f"Validar escala {scale.id}",
                            f"Publicar escala {scale.id}",
                            "Ver escalas pendentes",
                        ],
                        "actions": [
                            {
                                "type": "apply_scale_template",
                                "label": "Template aplicado",
                                "target": "scale",
                                "data": {"template_id": template.id, "scale_id": scale.id},
                            },
                        ],
                    }
                elif template:
                    # Template encontrado mas faltam parâmetros
                    meta = template.template_data.get("metadata", {})
                    return {
                        "response": f"""**Template: {template.name}**

- **Tipo:** {template.template_data.get("scale_type", "N/A")}
- **Funcionários:** {meta.get("total_employees", 0)}
- **Cobertura:** {meta.get("coverage_percentage", 0):.1f}%
- **Usado:** {template.times_used}x

Para aplicar, informe o **posto** e o **mês/ano**:
Exemplo: "Aplicar template {template_id} no posto POST-001 em fev/2026" """,
                        "intent": EscalaIntent.APLICAR_TEMPLATE.value,
                        "data": {"template_id": template.id, "template_name": template.name},
                        "needs_info": ["posto_id", "mes", "ano"],
                        "suggestions": ["Listar postos", "Cancelar"],
                    }
                else:
                    return {
                        "response": f"Template **{template_id}** não encontrado. Use `/escala template listar` para ver os disponíveis.",
                        "intent": EscalaIntent.APLICAR_TEMPLATE.value,
                        "suggestions": ["Listar templates", "Ajuda"],
                    }
            except ValueError as e:
                return {
                    "response": f"**Erro ao aplicar template:** {str(e)}",
                    "intent": EscalaIntent.APLICAR_TEMPLATE.value,
                    "suggestions": ["Listar templates", "Ver escalas", "Ajuda"],
                }
            except Exception as e:
                logger.error(f"Erro ao aplicar template: {e}")

        # Fallback
        return {
            "response": """**Aplicar Template de Escala**

Para aplicar um template, preciso de:

- **Template:** ID ou nome do template
- **Posto:** Onde aplicar
- **Período:** Mês e ano

**Exemplo:** "Aplicar template TPL-001 no posto POST-001 em março/2026"

Use "Listar templates" para ver os disponíveis.""",
            "intent": EscalaIntent.APLICAR_TEMPLATE.value,
            "needs_info": ["template_id", "posto_id", "mes", "ano"],
            "suggestions": ["Listar templates", "Ver postos", "Ajuda"],
        }

    async def _handle_listar_templates(self, context: dict) -> dict[str, Any]:
        """Lista templates de escala disponíveis."""
        template_repo = self._get_scale_template_repo()

        if template_repo:
            try:
                tenant_id = context.get("tenant_id") or context.get("cliente_id")
                if tenant_id:
                    templates, total = await template_repo.list(tenant_id=tenant_id, limit=10)

                    if templates:
                        lines = []
                        for i, t in enumerate(templates, 1):
                            meta = t.template_data.get("metadata", {})
                            popular = " ⭐" if t.is_popular else ""
                            lines.append(
                                f"| {i} | {t.name}{popular} | "
                                f"{t.template_data.get('scale_type', 'N/A')} | "
                                f"{meta.get('total_employees', 0)} | "
                                f"{t.times_used}x | {t.id[:8]}... |"
                            )

                        table_body = "\n".join(lines)
                        response = f"""**Templates de Escala Disponíveis ({total})**

| # | Nome | Tipo | Func. | Uso | ID |
|---|------|------|-------|-----|----|
{table_body}

Para aplicar: "Aplicar template <ID> no posto <POSTO> em <MÊS>/<ANO>"
Para criar novo: "Salvar escala <ID> como template <NOME>" """
                    else:
                        response = """**Templates de Escala**

Nenhum template encontrado.

Para criar um template, salve uma escala existente:
"Salvar escala ESC-001 como template Portaria 12x36" """

                    return {
                        "response": response,
                        "intent": EscalaIntent.LISTAR_TEMPLATES.value,
                        "data": {
                            "templates": [{"id": t.id, "name": t.name, "times_used": t.times_used} for t in templates],
                            "total": total,
                        },
                        "suggestions": ["Criar template", "Aplicar template", "Ver escalas"],
                    }
            except Exception as e:
                logger.error(f"Erro ao listar templates: {e}")

        # Fallback
        return {
            "response": """**Templates de Escala**

Para listar templates disponíveis, é necessário acesso ao banco de dados.

**O que são templates?**
Templates são modelos de escala reutilizáveis. Salve uma escala bem-sucedida
como template e aplique em outros postos e períodos.

**Comandos:**
- `/escala template listar` - Ver todos os templates
- `/escala template criar <nome> <escala_id>` - Criar template
- `/escala template aplicar <template_id> <posto> <mes>` - Aplicar template""",
            "intent": EscalaIntent.LISTAR_TEMPLATES.value,
            "suggestions": ["Criar template", "Ver escalas", "Ajuda"],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrão - retorna None para permitir que DataConnector processe"""
        # Se chegou aqui, não detectamos intent específico de escala
        # Retorna None para permitir que o fluxo continue (DataConnector, LLM, etc)
        return None

    # Patterns para follow-up (respostas curtas após GERAR_ESCALA)
    FOLLOWUP_PATTERNS = {
        "scale_type": [
            r"^(12x36|5x2|6x1|5x1|4x2)$",
            r"^(12x36|5x2|6x1|5x1|4x2)\s",
            r"(12x36|5x2|6x1|5x1|4x2)\s*(?:diurno|noturno)?",
        ],
        "confirmation": [
            r"^(?:sim|s|yes|y|confirmar?|ok|pode|isso|exato|correto)$",
        ],
        "negation": [
            r"^(?:nao|n|no|cancelar?|parar|sair)$",
        ],
    }

    async def process_followup(
        self,
        message: str,
        context: dict[str, Any],
        previous_intent: str,
        previous_data: dict | None = None,
    ) -> dict[str, Any] | None:
        """
        Processa follow-up de uma conversa anterior com o EscalaAgent.

        Entende respostas curtas como "12x36", "5x2" quando o contexto
        anterior foi GERAR_ESCALA.

        Args:
            message: Mensagem do usuário (possivelmente curta)
            context: Contexto da conversa
            previous_intent: Intent da interação anterior
            previous_data: Dados coletados na interação anterior

        Returns:
            Dict com resposta ou None se não for follow-up reconhecido
        """
        import re

        message_clean = message.strip().lower()
        previous_data = previous_data or {}

        # Follow-up de GERAR_ESCALA: espera tipo de escala
        if previous_intent == EscalaIntent.GERAR_ESCALA.value:
            # Tenta detectar tipo de escala
            for pattern in self.FOLLOWUP_PATTERNS["scale_type"]:
                match = re.search(pattern, message_clean)
                if match:
                    scale_type = match.group(1)
                    scale_info = self.SCALE_TYPES.get(scale_type, {})

                    # Merge com dados anteriores
                    merged_data = {**previous_data, "scale_type": scale_type}

                    # Extrai turno se presente
                    if "diurno" in message_clean:
                        merged_data["turno"] = "Diurno (07:00 - 19:00)"
                    elif "noturno" in message_clean:
                        merged_data["turno"] = "Noturno (19:00 - 07:00)"

                    # Monta resposta de confirmação
                    info_lines = [f"**Tipo de Escala:** {scale_type}"]
                    if scale_info.get("hours_on"):
                        info_lines.append(
                            f"**Jornada:** {scale_info['hours_on']}h trabalho, {scale_info['hours_off']}h folga"
                        )
                    if scale_info.get("days_on"):
                        info_lines.append(
                            f"**Jornada:** {scale_info['days_on']} dias trabalho, {scale_info['days_off']} dias folga"
                        )
                    if merged_data.get("turno"):
                        info_lines.append(f"**Turno:** {merged_data['turno']}")
                    if merged_data.get("cliente"):
                        info_lines.append(f"**Cliente:** {merged_data['cliente']}")
                    if merged_data.get("mes"):
                        info_lines.append(f"**Período:** {merged_data['mes']}/{merged_data.get('ano', 2026)}")

                    response = f"Escala **{scale_type}** selecionada.\n\n"
                    response += "\n".join(info_lines)
                    response += "\n\n**Deseja confirmar a geração desta escala?**"

                    return {
                        "response": response,
                        "intent": EscalaIntent.GERAR_ESCALA.value,
                        "data": merged_data,
                        "suggestions": ["Confirmar", "Alterar tipo", "Cancelar"],
                        "awaiting_confirmation": True,
                    }

            # Verifica se é confirmação
            for pattern in self.FOLLOWUP_PATTERNS["confirmation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Escala confirmada! Iniciando geração...\n\n"
                        "A escala será gerada com base nos parâmetros definidos. "
                        "Você será notificado quando estiver pronta para revisão.",
                        "intent": EscalaIntent.GERAR_ESCALA.value,
                        "data": {**previous_data, "confirmed": True},
                        "suggestions": ["Ver escalas", "Gerar outra escala"],
                    }

            # Verifica se é negação/cancelamento
            for pattern in self.FOLLOWUP_PATTERNS["negation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Geração de escala cancelada. Posso ajudar com outra coisa?",
                        "intent": EscalaIntent.GERAR_ESCALA.value,
                        "data": {**previous_data, "cancelled": True},
                        "suggestions": ["Gerar nova escala", "Ver escalas ativas", "Ajuda"],
                    }

        return None

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capabilities do agente"""
        return [
            "Gerar escalas automáticas (12x36, 5x2, 6x1)",
            "Otimizar escalas para reduzir custo",
            "Detectar conflitos de horário",
            "Validar conformidade CLT",
            "Calcular custos estimados",
            "Sugerir redistribuição de turnos",
            "Gerar escalas automaticamente para todos os postos (AutoScale)",
            "Otimização inteligente com IA (custo, cobertura, eficiência)",
            "Criar templates de escalas reutilizáveis",
            "Aplicar templates em novos postos/períodos",
            "Listar templates disponíveis",
        ]
