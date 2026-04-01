"""
DiaristaAgent - Agente especialista em diaristas
"""

import contextlib
import logging
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class DiaristaIntent(StrEnum):
    """Intents relacionados a diaristas"""

    VER_DIARISTAS = "ver_diaristas"
    DIARISTA_DETALHES = "diarista_detalhes"
    DIARISTAS_DISPONIVEIS = "diaristas_disponiveis"
    DIARISTAS_ESCALADOS = "diaristas_escalados"
    ESTATISTICAS = "estatisticas"
    REGISTRAR_DIARISTA = "registrar_diarista"
    AVALIAR = "avaliar"
    VER_AVALIACOES = "ver_avaliacoes"
    GERAR_PAGAMENTO = "gerar_pagamento"
    VER_PAGAMENTOS = "ver_pagamentos"
    APROVAR_PAGAMENTO = "aprovar_pagamento"
    VER_AGENDA_DETALHADA = "ver_agenda_detalhada"


class DiaristaAgent:
    """
    Agente especializado em operacoes de diaristas.

    Capabilities:
    - Listar diaristas ativos
    - Detalhar diarista especifico
    - Verificar disponiveis para trabalho
    - Listar escalados hoje/semana
    - Estatisticas gerais
    - Redirecionar para registro (action)
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista exaustiva para detecao de intencoes
    # IMPORTANTE: Patterns mais especificos devem vir ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # AVALIAR - Avaliar desempenho de diarista
        # ==================================================================
        (r"(?:avaliar|avaliac[aã]o|avaliar\s+desempenho)\s+(?:da?\s+)?diarista", DiaristaIntent.AVALIAR),
        (r"(?:dar|registrar|fazer|criar)\s+(?:uma?\s+)?avaliac[aã]o\s+(?:da?\s+)?diarista", DiaristaIntent.AVALIAR),
        (r"(?:nota|notas|pontuar)\s+(?:da?\s+)?diarista", DiaristaIntent.AVALIAR),
        (r"avaliar\s+(?:servico|trabalho)\s+(?:da?\s+)?diarista", DiaristaIntent.AVALIAR),
        (r"diarista\s+(?:avaliar|avaliacao)", DiaristaIntent.AVALIAR),
        # ==================================================================
        # VER_AVALIACOES - Historico de avaliacoes
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|listar)\s+(?:as?\s+)?avaliac[oõ]es\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_AVALIACOES,
        ),
        (r"(?:historico|hist[oó]rico)\s+(?:de\s+)?avaliac[oõ]es\s+(?:da?\s+)?diarista", DiaristaIntent.VER_AVALIACOES),
        (r"avaliac[oõ]es\s+(?:da?\s+)?diarista", DiaristaIntent.VER_AVALIACOES),
        (
            r"(?:como|qual)\s+(?:esta|e|eh|sao)\s+(?:as?\s+)?avaliac[oõ]es?\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_AVALIACOES,
        ),
        (r"diarista\s+avaliac[oõ]es", DiaristaIntent.VER_AVALIACOES),
        # ==================================================================
        # GERAR_PAGAMENTO - Gerar pagamento para diarista
        # ==================================================================
        (r"(?:gerar|criar|emitir)\s+pagamento\s+(?:da?\s+|para\s+)?diarista", DiaristaIntent.GERAR_PAGAMENTO),
        (r"pagamento\s+(?:da?\s+)?diarista\s+(?:gerar|criar|emitir)", DiaristaIntent.GERAR_PAGAMENTO),
        (
            r"(?:gerar|criar)\s+(?:folha|recibo)\s+(?:de\s+)?pagamento\s+(?:da?\s+)?diarista",
            DiaristaIntent.GERAR_PAGAMENTO,
        ),
        (r"(?:fechar|fechamento)\s+(?:folha|pagamento)\s+(?:da?\s+)?diarista", DiaristaIntent.GERAR_PAGAMENTO),
        # ==================================================================
        # APROVAR_PAGAMENTO - Aprovar pagamento pendente
        # ==================================================================
        (r"(?:aprovar|autorizar|liberar)\s+pagamento\s+(?:da?\s+|para\s+)?diarista", DiaristaIntent.APROVAR_PAGAMENTO),
        (r"pagamento\s+(?:da?\s+)?diarista\s+(?:aprovar|autorizar|liberar)", DiaristaIntent.APROVAR_PAGAMENTO),
        (r"(?:aprovar|autorizar)\s+(?:o\s+)?pagamento\s+(?:id|numero|num)", DiaristaIntent.APROVAR_PAGAMENTO),
        # ==================================================================
        # VER_PAGAMENTOS - Ver pagamentos pendentes/realizados
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|listar)\s+(?:os?\s+)?pagamentos?\s+(?:da?\s+|de\s+)?diarista",
            DiaristaIntent.VER_PAGAMENTOS,
        ),
        (r"pagamentos?\s+(?:da?\s+|de\s+)?diarista", DiaristaIntent.VER_PAGAMENTOS),
        (
            r"(?:pagamentos?|financeiro)\s+(?:pendentes?|realizados?|pagos?|cancelados?)\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_PAGAMENTOS,
        ),
        (r"diarista\s+pagamentos?", DiaristaIntent.VER_PAGAMENTOS),
        (r"(?:quais|quantos)\s+pagamentos?\s+(?:da?\s+)?diarista", DiaristaIntent.VER_PAGAMENTOS),
        # ==================================================================
        # VER_AGENDA_DETALHADA - Agenda com check-ins/outs e status
        # ==================================================================
        (
            r"(?:agenda|cronograma)\s+(?:detalhad[oa]|complet[oa])\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_AGENDA_DETALHADA,
        ),
        (
            r"(?:ver|veja|mostrar|mostre)\s+(?:a?\s+)?agenda\s+(?:detalhad[oa]\s+)?(?:da?\s+)?diarista",
            DiaristaIntent.VER_AGENDA_DETALHADA,
        ),
        (
            r"(?:check-?ins?|checkins?)\s+(?:e\s+)?(?:check-?outs?|checkouts?)\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_AGENDA_DETALHADA,
        ),
        (r"diarista\s+agenda\s+(?:detalhad[oa]|complet[oa])", DiaristaIntent.VER_AGENDA_DETALHADA),
        (
            r"(?:historico|hist[oó]rico)\s+(?:de\s+)?(?:agenda|presenca|frequencia)\s+(?:da?\s+)?diarista",
            DiaristaIntent.VER_AGENDA_DETALHADA,
        ),
        # ==================================================================
        # REGISTRAR_DIARISTA - Antes de VER_DIARISTAS (mais especifico)
        # ==================================================================
        (
            r"(?:registrar|cadastrar|cadastra|adicionar|adiciona|criar|crie|cria|incluir|inclua)\s+(?:uma?\s+)?(?:nova?\s+)?diarista",
            DiaristaIntent.REGISTRAR_DIARISTA,
        ),
        (r"(?:nova?\s+)?diarista\s+(?:nova?|cadastro|registro)", DiaristaIntent.REGISTRAR_DIARISTA),
        (
            r"(?:quero|preciso)\s+(?:registrar|cadastrar|adicionar)\s+(?:uma?\s+)?diarista",
            DiaristaIntent.REGISTRAR_DIARISTA,
        ),
        # ==================================================================
        # DIARISTA_DETALHES - Antes de VER_DIARISTAS (mais especifico)
        # ==================================================================
        (
            r"(?:detalhe|detalhes|info|informacoes?|dados?|perfil)\s+(?:da?\s+)?diarista",
            DiaristaIntent.DIARISTA_DETALHES,
        ),
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a?\s+)?diarista\s+\w+", DiaristaIntent.DIARISTA_DETALHES),
        (r"diarista\s+(?:cpf|nome|id)\s*[:=]?\s*\w+", DiaristaIntent.DIARISTA_DETALHES),
        (r"(?:quem\s+e|quem\s+eh|sobre)\s+(?:a\s+)?diarista", DiaristaIntent.DIARISTA_DETALHES),
        (r"(?:buscar|procurar)\s+diarista\s+\w+", DiaristaIntent.DIARISTA_DETALHES),
        # ==================================================================
        # DIARISTAS_ESCALADOS - escalados hoje/semana
        # ==================================================================
        (
            r"(?:diaristas?|quem)\s+(?:escalad[oa]s?|alocad[oa]s?|agendad[oa]s?)\s+(?:para\s+)?hoje",
            DiaristaIntent.DIARISTAS_ESCALADOS,
        ),
        (
            r"(?:diaristas?|quem)\s+(?:escalad[oa]s?|alocad[oa]s?|agendad[oa]s?)\s+(?:para\s+)?(?:esta|essa|da)\s+semana",
            DiaristaIntent.DIARISTAS_ESCALADOS,
        ),
        (r"(?:diaristas?|quem)\s+(?:trabalha|trabalham|vem|vao)\s+hoje", DiaristaIntent.DIARISTAS_ESCALADOS),
        (
            r"(?:diaristas?|quem)\s+(?:trabalha|trabalham|vem|vao)\s+(?:esta|essa)\s+semana",
            DiaristaIntent.DIARISTAS_ESCALADOS,
        ),
        (r"(?:agenda|escala|programacao)\s+(?:de\s+)?diaristas?\s+(?:de\s+)?hoje", DiaristaIntent.DIARISTAS_ESCALADOS),
        (
            r"(?:agenda|escala|programacao)\s+(?:de\s+)?diaristas?\s+(?:da\s+)?semana",
            DiaristaIntent.DIARISTAS_ESCALADOS,
        ),
        (r"(?:quem|quais)\s+(?:sao\s+)?(?:as?\s+)?diaristas?\s+(?:de\s+)?hoje", DiaristaIntent.DIARISTAS_ESCALADOS),
        (r"diaristas?\s+(?:do\s+)?dia", DiaristaIntent.DIARISTAS_ESCALADOS),
        # ==================================================================
        # DIARISTAS_DISPONIVEIS - disponiveis para trabalho
        # ==================================================================
        (r"diaristas?\s+(?:disponive[li]s?|livres?|desocupad[oa]s?)", DiaristaIntent.DIARISTAS_DISPONIVEIS),
        (r"(?:quem|quais)\s+(?:diaristas?\s+)?(?:esta|estao)\s+disponive[li]s?", DiaristaIntent.DIARISTAS_DISPONIVEIS),
        (r"(?:tem|ha|há)\s+diaristas?\s+disponive[li]s?", DiaristaIntent.DIARISTAS_DISPONIVEIS),
        (
            r"(?:preciso|precisamos)\s+(?:de\s+)?(?:uma?\s+)?diarista\s+(?:para|disponivel)",
            DiaristaIntent.DIARISTAS_DISPONIVEIS,
        ),
        (r"(?:buscar|procurar|encontrar)\s+diaristas?\s+disponive[li]s?", DiaristaIntent.DIARISTAS_DISPONIVEIS),
        (r"diaristas?\s+(?:para|pra)\s+(?:hoje|amanha|semana|trabalhar)", DiaristaIntent.DIARISTAS_DISPONIVEIS),
        # ==================================================================
        # ESTATISTICAS - stats gerais
        # ==================================================================
        (
            r"(?:estatisticas?|stats?|metricas?|indicadores?|numeros?|dados?)\s+(?:de\s+|das?\s+)?diaristas?",
            DiaristaIntent.ESTATISTICAS,
        ),
        (r"(?:resumo|dashboard|painel|visao\s+geral)\s+(?:de\s+|das?\s+)?diaristas?", DiaristaIntent.ESTATISTICAS),
        (r"(?:quantas?|quantos?|total)\s+(?:de\s+)?diaristas?", DiaristaIntent.ESTATISTICAS),
        (r"diaristas?\s+(?:em\s+)?(?:numeros?|estatisticas?|stats?|resumo)", DiaristaIntent.ESTATISTICAS),
        (r"(?:ranking|top|melhores)\s+diaristas?", DiaristaIntent.ESTATISTICAS),
        (r"(?:gastos?|custo|investimento)\s+(?:com\s+)?diaristas?", DiaristaIntent.ESTATISTICAS),
        # ==================================================================
        # VER_DIARISTAS - listar (mais generico, por ultimo)
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:as?\s+|os?\s+)?diaristas?",
            DiaristaIntent.VER_DIARISTAS,
        ),
        (r"(?:quais|quem)\s+(?:sao\s+)?(?:as?\s+)?diaristas?", DiaristaIntent.VER_DIARISTAS),
        (r"(?:lista|listagem|relacao)\s+(?:de\s+)?diaristas?", DiaristaIntent.VER_DIARISTAS),
        (r"diaristas?\s+(?:ativ[oa]s?|cadastrad[oa]s?|registrad[oa]s?)", DiaristaIntent.VER_DIARISTAS),
        (r"(?:todos?|todas?)\s+(?:as?\s+|os?\s+)?diaristas?", DiaristaIntent.VER_DIARISTAS),
    ]

    def __init__(self, db=None, diarist_repo=None, data_connector=None):
        self.db = db
        self.diarist_repo = diarist_repo
        self.data_connector = data_connector
        # Se tem db mas nao tem repo, criar automaticamente
        if db and not diarist_repo:
            try:
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                self.diarist_repo = DiaristRepository(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DiaristRepository: {e}")
                self.diarist_repo = None
        # Se tem db mas nao tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector

                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Processa uma mensagem relacionada a diaristas.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == DiaristaIntent.VER_DIARISTAS:
            return await self._handle_ver_diaristas(message, context)
        elif intent == DiaristaIntent.DIARISTA_DETALHES:
            return await self._handle_diarista_detalhes(message, context)
        elif intent == DiaristaIntent.DIARISTAS_DISPONIVEIS:
            return await self._handle_diaristas_disponiveis(message, context)
        elif intent == DiaristaIntent.DIARISTAS_ESCALADOS:
            return await self._handle_diaristas_escalados(message, context)
        elif intent == DiaristaIntent.ESTATISTICAS:
            return await self._handle_estatisticas(message, context)
        elif intent == DiaristaIntent.REGISTRAR_DIARISTA:
            return await self._handle_registrar_diarista(message, context)
        elif intent == DiaristaIntent.AVALIAR:
            return await self._handle_avaliar(message, context)
        elif intent == DiaristaIntent.VER_AVALIACOES:
            return await self._handle_ver_avaliacoes(message, context)
        elif intent == DiaristaIntent.GERAR_PAGAMENTO:
            return await self._handle_gerar_pagamento(message, context)
        elif intent == DiaristaIntent.VER_PAGAMENTOS:
            return await self._handle_ver_pagamentos(message, context)
        elif intent == DiaristaIntent.APROVAR_PAGAMENTO:
            return await self._handle_aprovar_pagamento(message, context)
        elif intent == DiaristaIntent.VER_AGENDA_DETALHADA:
            return await self._handle_ver_agenda_detalhada(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> DiaristaIntent | None:
        """Detecta o intent da mensagem"""
        import re

        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_ver_diaristas(self, message: str, context: dict) -> dict[str, Any]:
        """Lista diaristas ativos usando DiaristRepository"""
        if self.diarist_repo:
            try:
                from modules.operacional.diaristas.models.diarist import DiaristStatus

                diaristas = await self.diarist_repo.list_all(
                    status=DiaristStatus.ATIVO,
                    limit=20,
                )

                if diaristas:
                    lines = []
                    for i, d in enumerate(diaristas[:15], 1):
                        tipos = ", ".join(d.tipos_servico or []) or "N/A"
                        avaliacao = f"{float(d.avaliacao_media or 0):.1f}" if d.avaliacao_media else "N/A"
                        valor = f"R$ {float(d.valor_diaria or 0):,.2f}"
                        lines.append(f"| {i} | {d.nome} | {tipos} | {avaliacao} | {valor} | {d.status} |")

                    tabela = "\n".join(lines)
                    response = f"""**Diaristas Ativas ({len(diaristas)})**

| # | Nome | Tipo | Avaliacao | Diaria | Status |
|---|------|------|-----------|--------|--------|
{tabela}

**Total:** {len(diaristas)} diarista(s) ativa(s)"""

                    return {
                        "response": response,
                        "intent": DiaristaIntent.VER_DIARISTAS.value,
                        "data": {
                            "diaristas": [
                                {
                                    "id": str(d.id),
                                    "nome": d.nome,
                                    "tipos_servico": d.tipos_servico,
                                    "status": d.status,
                                    "avaliacao_media": float(d.avaliacao_media or 0),
                                    "valor_diaria": float(d.valor_diaria or 0),
                                }
                                for d in diaristas
                            ],
                            "total": len(diaristas),
                        },
                        "suggestions": [
                            "/diarista disponiveis",
                            "/diarista escalados",
                            "/diarista stats",
                        ],
                    }
                else:
                    return {
                        "response": "**Diaristas**\n\nNenhuma diarista ativa encontrada no sistema.",
                        "intent": DiaristaIntent.VER_DIARISTAS.value,
                        "data": {"diaristas": [], "total": 0},
                        "suggestions": ["Cadastrar diarista", "/diarista help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao listar diaristas via Repository: {e}")

        # Fallback estatico
        return {
            "response": """**Diaristas Ativas**

| # | Nome | Tipo | Avaliacao | Diaria | Status |
|---|------|------|-----------|--------|--------|
| 1 | Maria Silva | limpeza | 4.8 | R$ 180,00 | ativo |
| 2 | Ana Souza | faxina | 4.5 | R$ 150,00 | ativo |
| 3 | Joana Lima | jardinagem | 4.2 | R$ 200,00 | ativo |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.VER_DIARISTAS.value,
            "data": {"diaristas": [], "total": 0, "is_fallback": True},
            "suggestions": ["/diarista disponiveis", "/diarista stats", "/diarista help"],
        }

    async def _handle_diarista_detalhes(self, message: str, context: dict) -> dict[str, Any]:
        """Detalhe de um diarista especifico"""
        import re

        # Tentar extrair identificador (CPF, nome ou ID)
        identificador = None
        cpf_match = re.search(r"(\d{3}\.?\d{3}\.?\d{3}-?\d{2})", message)
        if cpf_match:
            identificador = cpf_match.group(1)

        if not identificador:
            # Tentar extrair nome apos palavras-chave
            nome_match = re.search(
                r"(?:diarista|detalhes?|info|perfil)\s+(?:da?\s+)?([A-Za-zÀ-ÿ\s]{3,})",
                message,
                re.IGNORECASE,
            )
            if nome_match:
                identificador = nome_match.group(1).strip()

        if self.diarist_repo and identificador:
            try:
                diarista = None
                # Tentar buscar por CPF
                if re.match(r"\d", identificador):
                    cpf_limpo = re.sub(r"\D", "", identificador)
                    diarista = await self.diarist_repo.get_by_cpf(cpf_limpo)

                # Tentar buscar por nome
                if not diarista:
                    diaristas = await self.diarist_repo.list_all(search=identificador, limit=1)
                    if diaristas:
                        diarista = diaristas[0]

                if diarista:
                    tipos = ", ".join(diarista.tipos_servico or []) or "N/A"
                    dias = ", ".join(diarista.dias_disponiveis or []) or "N/A"
                    especialidades = ", ".join(diarista.especialidades or []) or "N/A"
                    avaliacao = f"{float(diarista.avaliacao_media or 0):.1f}/5.0"
                    idade_str = f"{diarista.idade} anos" if diarista.idade else "N/A"

                    response = f"""**Detalhes da Diarista**

**Nome:** {diarista.nome}
**CPF:** {diarista.cpf}
**Status:** {diarista.status}
**Idade:** {idade_str}
**Telefone:** {diarista.telefone or "N/A"}
**Email:** {diarista.email or "N/A"}

**Profissional:**
- **Tipos de servico:** {tipos}
- **Especialidades:** {especialidades}
- **Experiencia:** {diarista.experiencia_anos or 0} anos

**Disponibilidade:**
- **Dias:** {dias}
- **Horario:** {diarista.hora_inicio_disponivel or "08:00"} - {diarista.hora_fim_disponivel or "17:00"}
- **Aceita hora extra:** {"Sim" if diarista.aceita_hora_extra else "Nao"}

**Financeiro:**
- **Valor diaria:** R$ {float(diarista.valor_diaria or 0):,.2f}
- **Valor hora:** R$ {float(diarista.valor_hora or 0):,.2f}
- **Valor hora extra:** R$ {float(diarista.valor_hora_extra or 0):,.2f}

**Metricas:**
- **Avaliacao:** {avaliacao} ({diarista.total_avaliacoes or 0} avaliacoes)
- **Total servicos:** {diarista.total_servicos or 0}"""

                    return {
                        "response": response,
                        "intent": DiaristaIntent.DIARISTA_DETALHES.value,
                        "data": {
                            "id": str(diarista.id),
                            "nome": diarista.nome,
                            "cpf": diarista.cpf,
                            "status": diarista.status,
                            "tipos_servico": diarista.tipos_servico,
                            "avaliacao_media": float(diarista.avaliacao_media or 0),
                            "valor_diaria": float(diarista.valor_diaria or 0),
                        },
                        "suggestions": [
                            "Ver agenda da diarista",
                            "Ver avaliacoes",
                            "Voltar para lista",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes da diarista: {e}")

        # Fallback - pedir identificacao
        return {
            "response": """**Detalhes de Diarista**

Para consultar os detalhes, informe:
- **Nome:** Ex: "detalhes diarista Maria Silva"
- **CPF:** Ex: "diarista cpf 123.456.789-00"

Ou use `/diarista listar` para ver todas as diaristas.""",
            "intent": DiaristaIntent.DIARISTA_DETALHES.value,
            "needs_info": ["identificador"],
            "suggestions": ["/diarista listar", "/diarista help"],
        }

    async def _handle_diaristas_disponiveis(self, message: str, context: dict) -> dict[str, Any]:
        """Diaristas disponiveis para trabalho"""
        import re

        # Extrair data da mensagem
        data_busca = date.today()
        if "amanha" in message.lower() or "amanhã" in message.lower():
            data_busca = date.today() + timedelta(days=1)

        # Extrair tipo de servico
        tipo_servico = None
        tipo_match = re.search(
            r"(?:tipo|servico|para)\s+(?:de\s+)?(limpeza|faxina|jardinagem|manutencao|cozinha|passadeira|cuidador|baba|motorista)",
            message.lower(),
        )
        if tipo_match:
            tipo_servico = tipo_match.group(1)

        if self.diarist_repo:
            try:
                from modules.operacional.diaristas.models.diarist import DiaristType

                tipo_enum = None
                if tipo_servico:
                    with contextlib.suppress(ValueError):
                        tipo_enum = DiaristType(tipo_servico)

                disponiveis = await self.diarist_repo.get_available_diarists(
                    data=data_busca,
                    tipo=tipo_enum,
                )

                if disponiveis:
                    lines = []
                    for i, d in enumerate(disponiveis[:15], 1):
                        tipos = ", ".join(d.tipos_servico or []) or "N/A"
                        avaliacao = f"{float(d.avaliacao_media or 0):.1f}" if d.avaliacao_media else "N/A"
                        valor = f"R$ {float(d.valor_diaria or 0):,.2f}"
                        lines.append(f"| {i} | {d.nome} | {tipos} | {avaliacao} | {valor} |")

                    tabela = "\n".join(lines)
                    filtro_info = f" (tipo: {tipo_servico})" if tipo_servico else ""
                    response = f"""**Diaristas Disponiveis - {data_busca.strftime("%d/%m/%Y")}{filtro_info}**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
{tabela}

**Total:** {len(disponiveis)} diarista(s) disponivel(is)

*Ordenadas por avaliacao (melhor primeiro).*"""

                    return {
                        "response": response,
                        "intent": DiaristaIntent.DIARISTAS_DISPONIVEIS.value,
                        "data": {
                            "disponiveis": [
                                {
                                    "id": str(d.id),
                                    "nome": d.nome,
                                    "tipos_servico": d.tipos_servico,
                                    "avaliacao_media": float(d.avaliacao_media or 0),
                                    "valor_diaria": float(d.valor_diaria or 0),
                                }
                                for d in disponiveis
                            ],
                            "total": len(disponiveis),
                            "data": data_busca.isoformat(),
                        },
                        "suggestions": [
                            "Escalar diarista",
                            "Ver detalhes",
                            "Disponiveis amanha",
                        ],
                        "actions": [
                            {
                                "type": "create",
                                "label": "Escalar diarista",
                                "target": "diarist_schedule",
                                "data": {"data": data_busca.isoformat()},
                            }
                        ],
                    }
                else:
                    return {
                        "response": f"**Diaristas Disponiveis - {data_busca.strftime('%d/%m/%Y')}**\n\nNenhuma diarista disponivel para esta data.",
                        "intent": DiaristaIntent.DIARISTAS_DISPONIVEIS.value,
                        "data": {"disponiveis": [], "total": 0, "data": data_busca.isoformat()},
                        "suggestions": ["Ver para amanha", "Ver todas diaristas", "Cadastrar diarista"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar diaristas disponiveis: {e}")

        # Fallback estatico
        return {
            "response": f"""**Diaristas Disponiveis - {data_busca.strftime("%d/%m/%Y")}**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
| 1 | Maria Silva | limpeza | 4.8 | R$ 180,00 |
| 2 | Joana Lima | jardinagem | 4.2 | R$ 200,00 |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.DIARISTAS_DISPONIVEIS.value,
            "data": {"disponiveis": [], "total": 0, "is_fallback": True},
            "suggestions": ["/diarista escalados", "/diarista listar"],
        }

    async def _handle_diaristas_escalados(self, message: str, context: dict) -> dict[str, Any]:
        """Diaristas escalados hoje ou na semana"""
        import re

        # Detectar periodo
        is_semana = bool(re.search(r"semana", message.lower()))
        hoje = date.today()

        if is_semana:
            # Segunda a sexta da semana atual
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            fim_semana = inicio_semana + timedelta(days=6)
            data_inicio = inicio_semana
            data_fim = fim_semana
            periodo_label = f"Semana {inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m/%Y')}"
        else:
            data_inicio = hoje
            data_fim = hoje
            periodo_label = f"Hoje - {hoje.strftime('%d/%m/%Y')}"

        if self.diarist_repo:
            try:
                schedules = await self.diarist_repo.list_schedules(
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    limit=50,
                )

                # Filtrar apenas ativos (AGENDADO, CONFIRMADO, EM_ANDAMENTO)
                ativos_status = {"AGENDADO", "CONFIRMADO", "EM_ANDAMENTO"}
                schedules_ativos = [
                    s
                    for s in schedules
                    if (s.status.value if hasattr(s.status, "value") else str(s.status)) in ativos_status
                ]

                if schedules_ativos:
                    lines = []
                    for i, s in enumerate(schedules_ativos[:20], 1):
                        nome = s.diarist.nome if s.diarist else "N/A"
                        data_str = s.data_trabalho.strftime("%d/%m") if s.data_trabalho else "N/A"
                        hora_ini = s.hora_inicio.strftime("%H:%M") if s.hora_inicio else "08:00"
                        hora_fim = s.hora_fim.strftime("%H:%M") if s.hora_fim else "17:00"
                        status_str = s.status.value if hasattr(s.status, "value") else str(s.status)
                        lines.append(f"| {i} | {nome} | {data_str} | {hora_ini}-{hora_fim} | {status_str} |")

                    tabela = "\n".join(lines)
                    response = f"""**Diaristas Escalados - {periodo_label}**

| # | Nome | Data | Horario | Status |
|---|------|------|---------|--------|
{tabela}

**Total:** {len(schedules_ativos)} agendamento(s)"""

                    return {
                        "response": response,
                        "intent": DiaristaIntent.DIARISTAS_ESCALADOS.value,
                        "data": {
                            "schedules": [
                                {
                                    "id": str(s.id),
                                    "diarist_nome": s.diarist.nome if s.diarist else "N/A",
                                    "data_trabalho": s.data_trabalho.isoformat() if s.data_trabalho else None,
                                    "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                                }
                                for s in schedules_ativos
                            ],
                            "total": len(schedules_ativos),
                            "periodo": periodo_label,
                        },
                        "suggestions": [
                            "/diarista disponiveis",
                            "Ver detalhes",
                            "Escalar diarista",
                        ],
                    }
                else:
                    return {
                        "response": f"**Diaristas Escalados - {periodo_label}**\n\nNenhum agendamento encontrado para o periodo.",
                        "intent": DiaristaIntent.DIARISTAS_ESCALADOS.value,
                        "data": {"schedules": [], "total": 0},
                        "suggestions": ["/diarista disponiveis", "Escalar diarista"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar diaristas escalados: {e}")

        # Fallback estatico
        return {
            "response": f"""**Diaristas Escalados - {periodo_label}**

| # | Nome | Data | Horario | Status |
|---|------|------|---------|--------|
| 1 | Maria Silva | {hoje.strftime("%d/%m")} | 08:00-17:00 | CONFIRMADO |
| 2 | Ana Souza | {hoje.strftime("%d/%m")} | 08:00-12:00 | AGENDADO |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.DIARISTAS_ESCALADOS.value,
            "data": {"schedules": [], "total": 0, "is_fallback": True},
            "suggestions": ["/diarista disponiveis", "/diarista listar"],
        }

    async def _handle_estatisticas(self, message: str, context: dict) -> dict[str, Any]:
        """Estatisticas gerais de diaristas"""
        if self.diarist_repo:
            try:
                from modules.operacional.diaristas.models.diarist import DiaristStatus

                # Contagens por status
                total_ativos = await self.diarist_repo.count(status=DiaristStatus.ATIVO)
                total_inativos = await self.diarist_repo.count(status=DiaristStatus.INATIVO)
                total_geral = total_ativos + total_inativos

                # Estatisticas gerais
                stats = await self.diarist_repo.get_condominio_statistics()

                # Top diaristas
                top = await self.diarist_repo.get_top_diarists(limit=5)
                top_lines = []
                for i, t in enumerate(top, 1):
                    d = t["diarist"]
                    top_lines.append(f"| {i} | {d.nome} | {t['avaliacao_media']:.1f} | {t['total_servicos']} |")

                top_tabela = "\n".join(top_lines) if top_lines else "| - | Sem dados | - | - |"

                response = f"""**Estatisticas de Diaristas**

**Cadastro:**
- Total cadastradas: **{total_geral}**
- Ativas: **{total_ativos}**
- Inativas: **{total_inativos}**

**Ultimos 30 dias:**
- Total agendamentos: **{stats.get("agendamentos", {}).get("total", 0)}**
- Concluidos: **{stats.get("agendamentos", {}).get("concluidos", 0)}**
- Taxa conclusao: **{stats.get("agendamentos", {}).get("taxa_conclusao", 0):.1f}%**
- Gastos total: **R$ {stats.get("gastos_total", 0):,.2f}**
- Media avaliacoes: **{stats.get("media_avaliacoes", 0):.1f}/5.0**

**Ranking - Melhores Diaristas:**

| # | Nome | Avaliacao | Servicos |
|---|------|-----------|----------|
{top_tabela}"""

                return {
                    "response": response,
                    "intent": DiaristaIntent.ESTATISTICAS.value,
                    "data": {
                        "total_ativos": total_ativos,
                        "total_inativos": total_inativos,
                        "total_geral": total_geral,
                        "stats": stats,
                    },
                    "suggestions": [
                        "/diarista listar",
                        "/diarista disponiveis",
                        "Ver detalhes de diarista",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas de Diaristas**

**Cadastro:**
- Total cadastradas: **12**
- Ativas: **8**
- Inativas: **4**

**Ultimos 30 dias:**
- Total agendamentos: **45**
- Concluidos: **40**
- Taxa conclusao: **88.9%**
- Gastos total: **R$ 7.200,00**
- Media avaliacoes: **4.3/5.0**

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.ESTATISTICAS.value,
            "data": {"is_fallback": True},
            "suggestions": ["/diarista listar", "/diarista disponiveis"],
        }

    async def _handle_registrar_diarista(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona para action de registro de diarista"""
        return {
            "response": """**Registrar Nova Diarista**

Para cadastrar uma nova diarista, preciso dos seguintes dados:

**Obrigatorios:**
- **Nome completo**
- **CPF**
- **Valor da diaria** (R$)

**Opcionais:**
- Telefone, email
- Tipos de servico (limpeza, faxina, jardinagem, etc.)
- Dias disponiveis
- Dados bancarios (PIX, banco, agencia, conta)

Informe os dados ou confirme para prosseguir com o cadastro.""",
            "intent": DiaristaIntent.REGISTRAR_DIARISTA.value,
            "needs_info": ["nome", "cpf", "valor_diaria"],
            "suggestions": ["Cancelar", "/diarista listar", "/diarista help"],
            "actions": [
                {
                    "type": "create",
                    "label": "Cadastrar Diarista",
                    "target": "diarist",
                    "data": {},
                }
            ],
        }

    async def _handle_avaliar(self, message: str, context: dict) -> dict[str, Any]:
        """Iniciar avaliacao de diarista apos trabalho"""
        import re

        # Extrair diarist_id ou nome
        diarist_id = None
        schedule_id = None
        uuid_matches = re.findall(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if len(uuid_matches) >= 1:
            diarist_id = uuid_matches[0]
        if len(uuid_matches) >= 2:
            schedule_id = uuid_matches[1]

        if self.diarist_repo and diarist_id:
            try:
                from uuid import UUID

                diarista = await self.diarist_repo.get_by_id(UUID(diarist_id))

                if diarista:
                    # Se schedule_id fornecido, verificar se existe avaliacao
                    avaliacao_existente = None
                    if schedule_id:
                        with contextlib.suppress(Exception):
                            avaliacao_existente = await self.diarist_repo.get_evaluation_by_schedule(UUID(schedule_id))

                    if avaliacao_existente:
                        return {
                            "response": f"**Avaliacao ja existe**\n\nJa existe uma avaliacao para este agendamento da diarista **{diarista.nome}**.\nNota geral: **{avaliacao_existente.nota_geral}/5**",
                            "intent": DiaristaIntent.AVALIAR.value,
                            "data": {"diarist_id": diarist_id, "already_evaluated": True},
                            "suggestions": ["/diarista avaliacoes " + diarist_id, "/diarista listar"],
                        }

                    schedule_info = f"\n- **Agendamento:** {schedule_id}" if schedule_id else ""
                    return {
                        "response": f"""**Avaliar Diarista - {diarista.nome}**

Para registrar a avaliacao, informe as notas (1 a 5):

**Notas:**
- **Geral** (obrigatoria): nota de 1 a 5
- **Pontualidade:** nota de 1 a 5
- **Qualidade:** nota de 1 a 5
- **Comportamento:** nota de 1 a 5
- **Comunicacao:** nota de 1 a 5

**Dados:**
- **Diarista:** {diarista.nome} (ID: {diarist_id}){schedule_info}
- **Comentario:** (opcional)
- **Recomendaria:** Sim/Nao

Confirme os dados para prosseguir com a avaliacao.""",
                        "intent": DiaristaIntent.AVALIAR.value,
                        "needs_info": ["nota_geral"],
                        "data": {
                            "diarist_id": diarist_id,
                            "diarist_nome": diarista.nome,
                            "schedule_id": schedule_id,
                        },
                        "suggestions": ["Cancelar", "/diarista avaliacoes " + diarist_id],
                        "actions": [
                            {
                                "type": "create",
                                "label": "Registrar Avaliacao",
                                "target": "diarist_evaluation",
                                "data": {
                                    "diarist_id": diarist_id,
                                    "schedule_id": schedule_id,
                                },
                            }
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao preparar avaliacao: {e}")

        # Fallback - pedir dados
        return {
            "response": """**Avaliar Diarista**

Para avaliar, informe:
- **Diarista ID:** ID da diarista a avaliar
- **Agendamento ID:** (opcional) ID do agendamento concluido

Exemplo: "avaliar diarista [diarist_id] [schedule_id]"

Ou use `/diarista listar` para ver as diaristas.""",
            "intent": DiaristaIntent.AVALIAR.value,
            "needs_info": ["diarist_id"],
            "suggestions": ["/diarista listar", "/diarista escalados", "/diarista help"],
        }

    async def _handle_ver_avaliacoes(self, message: str, context: dict) -> dict[str, Any]:
        """Ver historico de avaliacoes de diarista"""
        import re

        # Extrair diarist_id
        diarist_id = None
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if uuid_match:
            diarist_id = uuid_match.group(0)

        # Tentar extrair nome
        nome_busca = None
        if not diarist_id:
            nome_match = re.search(
                r"(?:avaliac[oõ]es?|historico)\s+(?:da?\s+)?(?:diarista\s+)?([A-Za-zÀ-ÿ\s]{3,})",
                message,
                re.IGNORECASE,
            )
            if nome_match:
                nome_busca = nome_match.group(1).strip()

        if self.diarist_repo:
            try:
                from uuid import UUID

                diarista = None
                if diarist_id:
                    diarista = await self.diarist_repo.get_by_id(UUID(diarist_id))
                elif nome_busca:
                    diaristas = await self.diarist_repo.list_all(search=nome_busca, limit=1)
                    if diaristas:
                        diarista = diaristas[0]
                        diarist_id = str(diarista.id)

                if diarista:
                    avaliacoes = await self.diarist_repo.list_evaluations(diarist_id=diarista.id, limit=20)

                    if avaliacoes:
                        lines = []
                        for i, av in enumerate(avaliacoes[:15], 1):
                            data_str = av.created_at.strftime("%d/%m/%Y") if av.created_at else "N/A"
                            pont = av.nota_pontualidade or "-"
                            qual = av.nota_qualidade or "-"
                            comp = av.nota_comportamento or "-"
                            comu = av.nota_comunicacao or "-"
                            recomenda = "Sim" if av.recomendaria else "Nao"
                            lines.append(
                                f"| {i} | {data_str} | {av.nota_geral} | {pont} | {qual} | {comp} | {comu} | {recomenda} |"
                            )

                        tabela = "\n".join(lines)
                        media_str = f"{float(diarista.avaliacao_media or 0):.1f}"

                        return {
                            "response": f"""**Avaliacoes - {diarista.nome}**

**Media geral:** {media_str}/5.0 ({diarista.total_avaliacoes or 0} avaliacoes)

| # | Data | Geral | Pont. | Qual. | Comp. | Comun. | Recomenda |
|---|------|-------|-------|-------|-------|--------|-----------|
{tabela}""",
                            "intent": DiaristaIntent.VER_AVALIACOES.value,
                            "data": {
                                "diarist_id": str(diarista.id),
                                "diarist_nome": diarista.nome,
                                "total_avaliacoes": len(avaliacoes),
                                "media": float(diarista.avaliacao_media or 0),
                                "avaliacoes": [
                                    {
                                        "id": str(av.id),
                                        "nota_geral": av.nota_geral,
                                        "data": av.created_at.isoformat() if av.created_at else None,
                                    }
                                    for av in avaliacoes
                                ],
                            },
                            "suggestions": [
                                f"/diarista avaliar {diarist_id}",
                                "/diarista listar",
                                "/diarista stats",
                            ],
                        }
                    else:
                        return {
                            "response": f"**Avaliacoes - {diarista.nome}**\n\nNenhuma avaliacao encontrada para esta diarista.",
                            "intent": DiaristaIntent.VER_AVALIACOES.value,
                            "data": {"diarist_id": str(diarista.id), "total_avaliacoes": 0},
                            "suggestions": [f"/diarista avaliar {diarist_id}", "/diarista listar"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar avaliacoes: {e}")

        # Fallback
        return {
            "response": """**Avaliacoes de Diarista**

Para ver avaliacoes, informe o ID ou nome da diarista:
- "avaliacoes diarista [ID]"
- "avaliacoes diarista Maria Silva"

Ou use `/diarista listar` para ver as diaristas.""",
            "intent": DiaristaIntent.VER_AVALIACOES.value,
            "needs_info": ["diarist_id"],
            "suggestions": ["/diarista listar", "/diarista help"],
        }

    async def _handle_gerar_pagamento(self, message: str, context: dict) -> dict[str, Any]:
        """Gerar pagamento para diarista em periodo"""
        import re

        diarist_id = None
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if uuid_match:
            diarist_id = uuid_match.group(0)

        # Extrair periodo (YYYY-MM ou mes/ano)
        periodo = None
        periodo_match = re.search(r"(\d{4})-(\d{2})", message)
        if periodo_match:
            periodo = periodo_match.group(0)
        else:
            mes_match = re.search(r"(\d{1,2})/(\d{4})", message)
            if mes_match:
                periodo = f"{mes_match.group(2)}-{mes_match.group(1).zfill(2)}"

        if not periodo:
            # Default: mes atual
            periodo = datetime.now().strftime("%Y-%m")

        if self.diarist_repo and diarist_id:
            try:
                from uuid import UUID

                diarista = await self.diarist_repo.get_by_id(UUID(diarist_id))

                if diarista:
                    # Buscar schedules concluidos no periodo
                    ano, mes = periodo.split("-")
                    data_inicio = date(int(ano), int(mes), 1)
                    if int(mes) == 12:
                        data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
                    else:
                        data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)

                    schedules = await self.diarist_repo.list_schedules(
                        diarist_id=diarista.id,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                    )
                    concluidos = [
                        s
                        for s in schedules
                        if (s.status.value if hasattr(s.status, "value") else str(s.status)) == "CONCLUIDO"
                    ]

                    qtd = len(concluidos)
                    valor_diaria = float(diarista.valor_diaria or 0)
                    valor_bruto = qtd * valor_diaria

                    # Calculo de retencoes estimadas
                    inss = round(valor_bruto * 0.11, 2) if valor_bruto > 0 else 0
                    iss = round(valor_bruto * 0.05, 2) if valor_bruto > 0 else 0
                    irrf = round(valor_bruto * 0.075, 2) if valor_bruto > 1903.98 else 0
                    total_retencoes = inss + iss + irrf
                    valor_liquido = valor_bruto - total_retencoes

                    return {
                        "response": f"""**Gerar Pagamento - {diarista.nome}**

**Periodo:** {periodo} ({data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m/%Y")})

**Resumo:**
- Diarias concluidas: **{qtd}**
- Valor por diaria: **R$ {valor_diaria:,.2f}**
- **Valor bruto: R$ {valor_bruto:,.2f}**

**Retencoes estimadas:**
- INSS (11%): R$ {inss:,.2f}
- ISS (5%): R$ {iss:,.2f}
- IRRF (7.5%): R$ {irrf:,.2f}
- **Total retencoes: R$ {total_retencoes:,.2f}**

**Valor liquido: R$ {valor_liquido:,.2f}**

Confirme para gerar o pagamento.""",
                        "intent": DiaristaIntent.GERAR_PAGAMENTO.value,
                        "data": {
                            "diarist_id": diarist_id,
                            "diarist_nome": diarista.nome,
                            "periodo": periodo,
                            "quantidade_diarias": qtd,
                            "valor_bruto": valor_bruto,
                            "retencao_inss": inss,
                            "retencao_iss": iss,
                            "retencao_irrf": irrf,
                            "valor_liquido": valor_liquido,
                            "schedules_ids": [str(s.id) for s in concluidos],
                        },
                        "suggestions": ["Confirmar", "Cancelar", "/diarista pagamentos " + diarist_id],
                        "actions": [
                            {
                                "type": "create",
                                "label": "Gerar Pagamento",
                                "target": "diarist_payment",
                                "data": {
                                    "diarist_id": diarist_id,
                                    "periodo": periodo,
                                    "valor_bruto": valor_bruto,
                                    "retencao_inss": inss,
                                    "retencao_iss": iss,
                                    "retencao_irrf": irrf,
                                    "valor_liquido": valor_liquido,
                                    "schedules_ids": [str(s.id) for s in concluidos],
                                },
                            }
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao preparar pagamento: {e}")

        # Fallback
        return {
            "response": f"""**Gerar Pagamento de Diarista**

Para gerar pagamento, informe:
- **Diarista ID:** obrigatorio
- **Periodo:** YYYY-MM (padrao: {periodo})

Exemplo: "gerar pagamento diarista [diarist_id] {periodo}"

Ou use `/diarista listar` para ver as diaristas.""",
            "intent": DiaristaIntent.GERAR_PAGAMENTO.value,
            "needs_info": ["diarist_id"],
            "suggestions": ["/diarista listar", "/diarista pagamentos", "/diarista help"],
        }

    async def _handle_ver_pagamentos(self, message: str, context: dict) -> dict[str, Any]:
        """Ver pagamentos pendentes/realizados de diarista"""
        import re

        diarist_id = None
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if uuid_match:
            diarist_id = uuid_match.group(0)

        # Detectar filtro de status
        status_filtro = None
        if re.search(r"pendentes?", message.lower()):
            status_filtro = "PENDENTE"
        elif re.search(r"(?:pagos?|realizados?)", message.lower()):
            status_filtro = "PAGO"
        elif re.search(r"aprovados?", message.lower()):
            status_filtro = "APROVADO"

        if self.diarist_repo:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.models.diarist import PaymentStatus

                diarist_uuid = UUID(diarist_id) if diarist_id else None
                status_enum = None
                if status_filtro:
                    with contextlib.suppress(ValueError):
                        status_enum = PaymentStatus(status_filtro)

                pagamentos = await self.diarist_repo.list_payments(
                    diarist_id=diarist_uuid,
                    status=status_enum,
                    limit=20,
                )

                if pagamentos:
                    lines = []
                    total_bruto = 0
                    total_liquido = 0
                    for i, p in enumerate(pagamentos[:15], 1):
                        nome = p.diarist.nome if p.diarist else "N/A"
                        ref = p.data_referencia.strftime("%m/%Y") if p.data_referencia else "N/A"
                        bruto = float(p.valor_bruto or 0)
                        liquido = float(p.valor_liquido or 0)
                        status_str = (
                            p.status
                            if isinstance(p.status, str)
                            else (p.status.value if hasattr(p.status, "value") else str(p.status))
                        )
                        venc = p.data_vencimento.strftime("%d/%m") if p.data_vencimento else "N/A"
                        total_bruto += bruto
                        total_liquido += liquido
                        lines.append(
                            f"| {i} | {nome} | {ref} | R$ {bruto:,.2f} | R$ {liquido:,.2f} | {status_str} | {venc} |"
                        )

                    tabela = "\n".join(lines)
                    filtro_label = f" ({status_filtro})" if status_filtro else ""

                    return {
                        "response": f"""**Pagamentos de Diaristas{filtro_label}**

| # | Diarista | Ref. | Bruto | Liquido | Status | Venc. |
|---|----------|------|-------|---------|--------|-------|
{tabela}

**Totais:** Bruto: R$ {total_bruto:,.2f} | Liquido: R$ {total_liquido:,.2f}
**Total:** {len(pagamentos)} pagamento(s)""",
                        "intent": DiaristaIntent.VER_PAGAMENTOS.value,
                        "data": {
                            "total": len(pagamentos),
                            "total_bruto": total_bruto,
                            "total_liquido": total_liquido,
                            "pagamentos": [
                                {
                                    "id": str(p.id),
                                    "diarist_nome": p.diarist.nome if p.diarist else "N/A",
                                    "valor_bruto": float(p.valor_bruto or 0),
                                    "valor_liquido": float(p.valor_liquido or 0),
                                    "status": p.status
                                    if isinstance(p.status, str)
                                    else (p.status.value if hasattr(p.status, "value") else str(p.status)),
                                }
                                for p in pagamentos
                            ],
                        },
                        "suggestions": [
                            "/diarista pagamentos pendentes",
                            "/diarista pagamento aprovar",
                            "/diarista stats",
                        ],
                    }
                else:
                    return {
                        "response": f"**Pagamentos de Diaristas{' (' + status_filtro + ')' if status_filtro else ''}**\n\nNenhum pagamento encontrado.",
                        "intent": DiaristaIntent.VER_PAGAMENTOS.value,
                        "data": {"total": 0},
                        "suggestions": ["/diarista pagamento gerar", "/diarista listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar pagamentos: {e}")

        # Fallback
        return {
            "response": """**Pagamentos de Diaristas**

| # | Diarista | Ref. | Bruto | Liquido | Status | Venc. |
|---|----------|------|-------|---------|--------|-------|
| 1 | Maria Silva | 01/2026 | R$ 3.600,00 | R$ 2.844,00 | PENDENTE | 05/02 |
| 2 | Ana Souza | 01/2026 | R$ 2.400,00 | R$ 1.896,00 | PAGO | 05/02 |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.VER_PAGAMENTOS.value,
            "data": {"is_fallback": True},
            "suggestions": ["/diarista listar", "/diarista stats"],
        }

    async def _handle_aprovar_pagamento(self, message: str, context: dict) -> dict[str, Any]:
        """Aprovar pagamento pendente de diarista"""
        import re

        pagamento_id = None
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if uuid_match:
            pagamento_id = uuid_match.group(0)

        if self.diarist_repo and pagamento_id:
            try:
                from uuid import UUID

                pagamento = await self.diarist_repo.get_payment_by_id(UUID(pagamento_id))

                if pagamento:
                    status_str = (
                        pagamento.status
                        if isinstance(pagamento.status, str)
                        else (pagamento.status.value if hasattr(pagamento.status, "value") else str(pagamento.status))
                    )
                    nome = pagamento.diarist.nome if pagamento.diarist else "N/A"

                    if status_str != "PENDENTE":
                        return {
                            "response": f"**Aprovar Pagamento**\n\nPagamento para **{nome}** nao pode ser aprovado.\nStatus atual: **{status_str}** (precisa estar PENDENTE).",
                            "intent": DiaristaIntent.APROVAR_PAGAMENTO.value,
                            "data": {"pagamento_id": pagamento_id, "status": status_str},
                            "suggestions": ["/diarista pagamentos pendentes", "/diarista help"],
                        }

                    bruto = float(pagamento.valor_bruto or 0)
                    liquido = float(pagamento.valor_liquido or 0)
                    ref = pagamento.data_referencia.strftime("%m/%Y") if pagamento.data_referencia else "N/A"
                    retencoes = (
                        float(pagamento.retencao_inss or 0)
                        + float(pagamento.retencao_iss or 0)
                        + float(pagamento.retencao_irrf or 0)
                        + float(pagamento.outros_descontos or 0)
                    )

                    return {
                        "response": f"""**Aprovar Pagamento**

**Diarista:** {nome}
**Referencia:** {ref}
**Valor bruto:** R$ {bruto:,.2f}
**Retencoes:** R$ {retencoes:,.2f}
**Valor liquido:** R$ {liquido:,.2f}
**Vencimento:** {pagamento.data_vencimento.strftime("%d/%m/%Y") if pagamento.data_vencimento else "N/A"}

Confirme para aprovar este pagamento.""",
                        "intent": DiaristaIntent.APROVAR_PAGAMENTO.value,
                        "data": {
                            "pagamento_id": pagamento_id,
                            "diarist_nome": nome,
                            "valor_bruto": bruto,
                            "valor_liquido": liquido,
                        },
                        "suggestions": ["Confirmar", "Cancelar", "/diarista pagamentos"],
                        "actions": [
                            {
                                "type": "update",
                                "label": "Aprovar Pagamento",
                                "target": "diarist_payment",
                                "data": {"pagamento_id": pagamento_id, "novo_status": "APROVADO"},
                            }
                        ],
                    }
                else:
                    return {
                        "response": f"**Aprovar Pagamento**\n\nPagamento com ID {pagamento_id} nao encontrado.",
                        "intent": DiaristaIntent.APROVAR_PAGAMENTO.value,
                        "suggestions": ["/diarista pagamentos pendentes", "/diarista help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar pagamento para aprovacao: {e}")

        # Fallback - pedir ID
        return {
            "response": """**Aprovar Pagamento de Diarista**

Para aprovar, informe o ID do pagamento:
- "aprovar pagamento diarista [pagamento_id]"

Ou use `/diarista pagamentos pendentes` para ver os pendentes.""",
            "intent": DiaristaIntent.APROVAR_PAGAMENTO.value,
            "needs_info": ["pagamento_id"],
            "suggestions": ["/diarista pagamentos pendentes", "/diarista help"],
        }

    async def _handle_ver_agenda_detalhada(self, message: str, context: dict) -> dict[str, Any]:
        """Ver agenda detalhada com check-ins/outs e status"""
        import re

        diarist_id = None
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            message,
        )
        if uuid_match:
            diarist_id = uuid_match.group(0)

        # Detectar periodo
        periodo = None
        periodo_match = re.search(r"(\d{4})-(\d{2})", message)
        if periodo_match:
            periodo = periodo_match.group(0)

        # Detectar semana/mes
        is_semana = bool(re.search(r"semana", message.lower()))
        is_mes = bool(re.search(r"m[eê]s", message.lower()))

        hoje = date.today()
        if periodo:
            ano, mes = periodo.split("-")
            data_inicio = date(int(ano), int(mes), 1)
            if int(mes) == 12:
                data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
            else:
                data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)
            periodo_label = f"{periodo}"
        elif is_mes:
            data_inicio = date(hoje.year, hoje.month, 1)
            if hoje.month == 12:
                data_fim = date(hoje.year + 1, 1, 1) - timedelta(days=1)
            else:
                data_fim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
            periodo_label = f"{hoje.strftime('%m/%Y')}"
        elif is_semana:
            data_inicio = hoje - timedelta(days=hoje.weekday())
            data_fim = data_inicio + timedelta(days=6)
            periodo_label = f"Semana {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"
        else:
            # Ultimos 7 dias como padrao
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje
            periodo_label = f"{data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"

        if self.diarist_repo:
            try:
                from uuid import UUID

                diarist_uuid = UUID(diarist_id) if diarist_id else None

                schedules = await self.diarist_repo.list_schedules(
                    diarist_id=diarist_uuid,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    limit=50,
                )

                if schedules:
                    lines = []
                    total_concluidos = 0
                    total_faltas = 0
                    for i, s in enumerate(schedules[:30], 1):
                        nome = s.diarist.nome if s.diarist else "N/A"
                        data_str = s.data_trabalho.strftime("%d/%m") if s.data_trabalho else "N/A"
                        hora_ini = s.hora_inicio.strftime("%H:%M") if s.hora_inicio else "08:00"
                        hora_fim = s.hora_fim.strftime("%H:%M") if s.hora_fim else "17:00"
                        status_str = (
                            s.status
                            if isinstance(s.status, str)
                            else (s.status.value if hasattr(s.status, "value") else str(s.status))
                        )

                        checkin_str = s.checkin_real.strftime("%H:%M") if s.checkin_real else "-"
                        checkout_str = s.checkout_real.strftime("%H:%M") if s.checkout_real else "-"

                        duracao = "-"
                        if s.checkin_real and s.checkout_real:
                            delta = s.checkout_real - s.checkin_real
                            horas = int(delta.total_seconds() // 3600)
                            minutos = int((delta.total_seconds() % 3600) // 60)
                            duracao = f"{horas}h{minutos:02d}"

                        if status_str == "CONCLUIDO":
                            total_concluidos += 1
                        elif status_str == "NAO_COMPARECEU":
                            total_faltas += 1

                        lines.append(
                            f"| {i} | {nome} | {data_str} | {hora_ini}-{hora_fim} | {checkin_str} | {checkout_str} | {duracao} | {status_str} |"
                        )

                    tabela = "\n".join(lines)
                    diarist_label = f" - {schedules[0].diarist.nome}" if diarist_id and schedules[0].diarist else ""

                    return {
                        "response": f"""**Agenda Detalhada{diarist_label} - {periodo_label}**

| # | Diarista | Data | Horario | Check-in | Check-out | Duracao | Status |
|---|----------|------|---------|----------|-----------|---------|--------|
{tabela}

**Resumo:** {len(schedules)} agendamento(s) | {total_concluidos} concluido(s) | {total_faltas} falta(s)""",
                        "intent": DiaristaIntent.VER_AGENDA_DETALHADA.value,
                        "data": {
                            "total": len(schedules),
                            "concluidos": total_concluidos,
                            "faltas": total_faltas,
                            "periodo": periodo_label,
                            "schedules": [
                                {
                                    "id": str(s.id),
                                    "diarist_nome": s.diarist.nome if s.diarist else "N/A",
                                    "data_trabalho": s.data_trabalho.isoformat() if s.data_trabalho else None,
                                    "status": s.status
                                    if isinstance(s.status, str)
                                    else (s.status.value if hasattr(s.status, "value") else str(s.status)),
                                    "checkin": s.checkin_real.isoformat() if s.checkin_real else None,
                                    "checkout": s.checkout_real.isoformat() if s.checkout_real else None,
                                }
                                for s in schedules
                            ],
                        },
                        "suggestions": [
                            "/diarista escalados",
                            "/diarista stats",
                            "/diarista avaliar",
                        ],
                    }
                else:
                    return {
                        "response": f"**Agenda Detalhada - {periodo_label}**\n\nNenhum agendamento encontrado para o periodo.",
                        "intent": DiaristaIntent.VER_AGENDA_DETALHADA.value,
                        "data": {"total": 0},
                        "suggestions": ["/diarista escalados", "/diarista disponiveis"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar agenda detalhada: {e}")

        # Fallback
        return {
            "response": f"""**Agenda Detalhada - {periodo_label}**

| # | Diarista | Data | Horario | Check-in | Check-out | Duracao | Status |
|---|----------|------|---------|----------|-----------|---------|--------|
| 1 | Maria Silva | {hoje.strftime("%d/%m")} | 08:00-17:00 | 07:55 | 17:10 | 9h15 | CONCLUIDO |
| 2 | Ana Souza | {hoje.strftime("%d/%m")} | 08:00-12:00 | 08:10 | - | - | EM_ANDAMENTO |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "intent": DiaristaIntent.VER_AGENDA_DETALHADA.value,
            "data": {"is_fallback": True},
            "suggestions": ["/diarista escalados", "/diarista disponiveis"],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrao - retorna None para permitir que DataConnector processe"""
        return None

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capabilities do agente"""
        return [
            "Listar diaristas ativas",
            "Detalhar diarista especifico",
            "Verificar diaristas disponiveis",
            "Listar diaristas escalados hoje/semana",
            "Estatisticas gerais de diaristas",
            "Redirecionar para cadastro de diarista",
            "Avaliar desempenho de diarista",
            "Ver historico de avaliacoes",
            "Gerar pagamento para periodo",
            "Ver pagamentos pendentes/realizados",
            "Aprovar pagamento pendente",
            "Ver agenda detalhada com check-ins/outs",
        ]
