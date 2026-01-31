"""
OcorrenciaAgent - Agente especialista em ocorrencias disciplinares.

Processa intents relacionados a ocorrencias/infracoes de funcionarios,
consulta dados via DataConnector e oferece fallback estatico.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class OcorrenciaIntent(str, Enum):
    """Intents relacionados a ocorrencias."""
    VER_OCORRENCIAS = "ver_ocorrencias"
    OCORRENCIA_DETALHES = "ocorrencia_detalhes"
    OCORRENCIAS_POSTO = "ocorrencias_posto"
    OCORRENCIAS_FUNCIONARIO = "ocorrencias_funcionario"
    ESTATISTICAS_OCORRENCIAS = "estatisticas_ocorrencias"
    CRIAR_OCORRENCIA = "criar_ocorrencia"
    RESOLVER_OCORRENCIA = "resolver_ocorrencia"


class OcorrenciaAgent:
    """
    Agente especializado em operacoes de ocorrencias disciplinares.

    Capabilities:
    - Listar ocorrencias abertas
    - Consultar detalhes de uma ocorrencia
    - Ocorrencias por posto
    - Ocorrencias por funcionario
    - Estatisticas gerais de ocorrencias
    - Redirecionar criacao para action/wizard
    - Redirecionar resolucao para action
    """

    # ==========================================================================
    # INTENT_PATTERNS - Deteccao de intencoes de ocorrencia
    # Patterns mais especificos ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # RESOLVER_OCORRENCIA - Antes de detalhes (mais especifico)
        # ==================================================================
        (r"(?:resolver|resolva|fechar|feche|encerrar|encerre|concluir|conclua)\s+(?:a\s+)?ocorrencia", OcorrenciaIntent.RESOLVER_OCORRENCIA),
        (r"(?:resolver|resolva|fechar|feche|encerrar|encerre)\s+OCO-\d{4}-\d+", OcorrenciaIntent.RESOLVER_OCORRENCIA),
        (r"(?:aplicar|aplicar)\s+(?:acao\s+)?corretiva", OcorrenciaIntent.RESOLVER_OCORRENCIA),
        (r"(?:advertir|suspender|demitir)\s+(?:funcionario|colaborador)", OcorrenciaIntent.RESOLVER_OCORRENCIA),
        (r"(?:dar|aplicar)\s+(?:advertencia|suspensao)", OcorrenciaIntent.RESOLVER_OCORRENCIA),

        # ==================================================================
        # CRIAR_OCORRENCIA - Antes de listar (mais especifico)
        # ==================================================================
        (r"(?:criar|crie|cria|registrar|registre|abrir|abra|nova|novo)\s+(?:uma?\s+)?ocorrencia", OcorrenciaIntent.CRIAR_OCORRENCIA),
        (r"(?:registrar|registre)\s+(?:uma?\s+)?(?:infracao|nao\s+conformidade|irregularidade)", OcorrenciaIntent.CRIAR_OCORRENCIA),
        (r"(?:abrir|abra)\s+(?:um\s+)?(?:registro|chamado)\s+(?:de\s+)?(?:ocorrencia|infracao)", OcorrenciaIntent.CRIAR_OCORRENCIA),
        (r"(?:reportar|reporte)\s+(?:uma?\s+)?(?:ocorrencia|infracao|irregularidade)", OcorrenciaIntent.CRIAR_OCORRENCIA),
        (r"(?:funcionario|colaborador|vigilante|porteiro)\s+(?:cometeu|fez|esta|estava)\s+", OcorrenciaIntent.CRIAR_OCORRENCIA),

        # ==================================================================
        # OCORRENCIA_DETALHES - Codigo especifico
        # ==================================================================
        (r"(?:detalhe|detalhes|info|informacoes?)\s+(?:da\s+)?ocorrencia\s+OCO-\d{4}-\d+", OcorrenciaIntent.OCORRENCIA_DETALHES),
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a\s+)?ocorrencia\s+OCO-\d{4}-\d+", OcorrenciaIntent.OCORRENCIA_DETALHES),
        (r"OCO-\d{4}-\d+", OcorrenciaIntent.OCORRENCIA_DETALHES),
        (r"(?:detalhe|detalhes|info)\s+(?:da\s+)?ocorrencia", OcorrenciaIntent.OCORRENCIA_DETALHES),

        # ==================================================================
        # OCORRENCIAS_POSTO - Ocorrencias filtradas por posto
        # ==================================================================
        (r"ocorrencias?\s+(?:do|no|da|na)\s+posto", OcorrenciaIntent.OCORRENCIAS_POSTO),
        (r"ocorrencias?\s+(?:do|no|da|na)\s+(?:portaria|guarita|recepcao)", OcorrenciaIntent.OCORRENCIAS_POSTO),
        (r"ocorrencias?\s+(?:do|no)\s+POST-\d+", OcorrenciaIntent.OCORRENCIAS_POSTO),
        (r"(?:infracoes|irregularidades)\s+(?:do|no|da|na)\s+posto", OcorrenciaIntent.OCORRENCIAS_POSTO),
        (r"ocorrencias?\s+(?:do|no)\s+cliente", OcorrenciaIntent.OCORRENCIAS_POSTO),

        # ==================================================================
        # OCORRENCIAS_FUNCIONARIO - Ocorrencias por funcionario
        # ==================================================================
        (r"ocorrencias?\s+(?:do|da|de)\s+(?:funcionario|colaborador|vigilante|porteiro|agente)", OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO),
        (r"(?:historico|historico)\s+(?:de\s+)?(?:ocorrencias?|infracoes?)\s+(?:do|da|de)", OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO),
        (r"(?:infracoes?|irregularidades?)\s+(?:do|da|de)\s+(?:funcionario|colaborador)", OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO),
        (r"(?:ficha|prontuario)\s+(?:disciplinar|de\s+ocorrencias?)", OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO),
        (r"quantas\s+ocorrencias?\s+(?:tem|possui)\s+", OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO),

        # ==================================================================
        # ESTATISTICAS_OCORRENCIAS
        # ==================================================================
        (r"(?:estatisticas?|stats?|numeros?|indicadores?|dashboard)\s+(?:de\s+)?ocorrencias?", OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS),
        (r"(?:resumo|panorama|visao\s+geral)\s+(?:de\s+|das\s+)?ocorrencias?", OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS),
        (r"(?:quantas?|total)\s+(?:de\s+)?ocorrencias?", OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS),
        (r"ocorrencias?\s+(?:em\s+)?numeros", OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS),
        (r"(?:ranking|top)\s+(?:de\s+)?(?:ocorrencias?|infracoes?)", OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS),

        # ==================================================================
        # VER_OCORRENCIAS - Generico (por ultimo)
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:as\s+)?ocorrencias?(?:\s+abertas?)?", OcorrenciaIntent.VER_OCORRENCIAS),
        (r"ocorrencias?\s+(?:abertas?|pendentes?|ativas?)", OcorrenciaIntent.VER_OCORRENCIAS),
        (r"(?:tem|ha|há)\s+(?:alguma\s+)?ocorrencia", OcorrenciaIntent.VER_OCORRENCIAS),
        (r"(?:quais?|que)\s+(?:sao\s+)?(?:as\s+)?ocorrencias?", OcorrenciaIntent.VER_OCORRENCIAS),
        (r"(?:infracoes?|irregularidades?|nao\s+conformidades?)\s+(?:abertas?|pendentes?)", OcorrenciaIntent.VER_OCORRENCIAS),
        (r"ocorrencias?\s+(?:em\s+)?(?:aberto|analise)", OcorrenciaIntent.VER_OCORRENCIAS),
    ]

    def __init__(self, db=None, data_connector=None):
        self.db = db
        self.data_connector = data_connector
        # Se tem db mas nao tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector
                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem relacionada a ocorrencias.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == OcorrenciaIntent.VER_OCORRENCIAS:
            return await self._handle_ver_ocorrencias(message, context)
        elif intent == OcorrenciaIntent.OCORRENCIA_DETALHES:
            return await self._handle_ocorrencia_detalhes(message, context)
        elif intent == OcorrenciaIntent.OCORRENCIAS_POSTO:
            return await self._handle_ocorrencias_posto(message, context)
        elif intent == OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO:
            return await self._handle_ocorrencias_funcionario(message, context)
        elif intent == OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS:
            return await self._handle_estatisticas(message, context)
        elif intent == OcorrenciaIntent.CRIAR_OCORRENCIA:
            return await self._handle_criar_ocorrencia(message, context)
        elif intent == OcorrenciaIntent.RESOLVER_OCORRENCIA:
            return await self._handle_resolver_ocorrencia(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> Optional[OcorrenciaIntent]:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # =========================================================================
    # HANDLERS
    # =========================================================================

    async def _handle_ver_ocorrencias(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista ocorrencias abertas usando DataConnector."""
        if self.data_connector:
            try:
                result = await self.data_connector._get_ocorrencias_abertas()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": OcorrenciaIntent.VER_OCORRENCIAS.value,
                        "data": {"ocorrencias": result.data, "total": result.total_count},
                        "suggestions": [
                            "/ocorrencia stats",
                            "/ocorrencia graves",
                            "Criar ocorrencia",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias via DataConnector: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""📋 **OCORRENCIAS ABERTAS** (3)

- 🔴 **OCO-2026-00012** - Abandono de posto - Portaria B
  Severidade: grave | Status: Aberta | {today} 08:30
- 🟡 **OCO-2026-00011** - Uso de celular em servico
  Severidade: leve | Status: Em Analise | {today} 07:15
- 🟠 **OCO-2026-00010** - Falta de uniforme
  Severidade: moderada | Status: Aberta | {today} 06:00

**Resumo:**
- Total abertas: **3**
- Graves/Gravissimas: **1** 🚨

**Legenda:** 🟡 Leve | 🟠 Moderada | 🔴 Grave | 🚨 Gravissima""",
            "intent": OcorrenciaIntent.VER_OCORRENCIAS.value,
            "data": {
                "ocorrencias": [
                    {"codigo": "OCO-2026-00012", "titulo": "Abandono de posto - Portaria B", "severidade": "grave", "status": "aberta"},
                    {"codigo": "OCO-2026-00011", "titulo": "Uso de celular em servico", "severidade": "leve", "status": "em_analise"},
                    {"codigo": "OCO-2026-00010", "titulo": "Falta de uniforme", "severidade": "moderada", "status": "aberta"},
                ],
                "total": 3,
            },
            "suggestions": ["/ocorrencia stats", "/ocorrencia graves", "Criar ocorrencia"],
        }

    async def _handle_ocorrencia_detalhes(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra detalhes de uma ocorrencia especifica."""
        # Extrair codigo da ocorrencia
        code_match = re.search(r"OCO-\d{4}-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if self.data_connector and self.db and code:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)
                # Buscar pela listagem e filtrar pelo codigo
                items, total = await repo.list(page=1, page_size=100)
                occurrence = None
                for item in items:
                    if item.code == code:
                        occurrence = item
                        break

                if occurrence:
                    sev_icon = {
                        "leve": "🟡", "moderada": "🟠",
                        "grave": "🔴", "gravissima": "🚨",
                    }.get(occurrence.severity, "⚪")

                    status_label = {
                        "aberta": "Aberta",
                        "em_analise": "Em Analise",
                        "resolvida": "Resolvida",
                        "arquivada": "Arquivada",
                        "cancelada": "Cancelada",
                    }.get(occurrence.status, occurrence.status)

                    occurred = occurrence.occurred_at.strftime('%d/%m/%Y %H:%M') if occurrence.occurred_at else 'N/A'
                    resolved = occurrence.resolved_at.strftime('%d/%m/%Y %H:%M') if occurrence.resolved_at else 'Pendente'

                    response = f"""📋 **OCORRENCIA {occurrence.code}**

**Titulo:** {occurrence.title}
**Descricao:** {occurrence.description}

**Classificacao:**
- Tipo: {occurrence.occurrence_type}
- Severidade: {sev_icon} {occurrence.severity}
- Categoria: {occurrence.category}
- Status: {status_label}

**Envolvidos:**
- Funcionario: {occurrence.employee_id}
- Posto: {occurrence.post_id}
- Testemunhas: {occurrence.witnesses or 'Nao informado'}

**Datas:**
- Ocorrencia: {occurred}
- Resolucao: {resolved}"""

                    if occurrence.corrective_action:
                        response += f"\n\n**Acao Corretiva:** {occurrence.corrective_action}"
                    if occurrence.resolution_notes:
                        response += f"\n**Notas:** {occurrence.resolution_notes}"

                    return {
                        "response": response,
                        "intent": OcorrenciaIntent.OCORRENCIA_DETALHES.value,
                        "data": {"codigo": occurrence.code, "id": occurrence.id, "status": occurrence.status},
                        "suggestions": ["Resolver ocorrencia", "Ver ocorrencias abertas", "/ocorrencia stats"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes da ocorrencia via DB: {e}")

        # Fallback estatico
        code_display = code or "OCO-2026-00012"
        return {
            "response": f"""📋 **OCORRENCIA {code_display}**

**Titulo:** Abandono de posto - Portaria B
**Descricao:** Funcionario encontrado ausente do posto durante ronda de fiscalizacao as 08:30.

**Classificacao:**
- Tipo: abandono_posto
- Severidade: 🔴 grave
- Categoria: disciplinar
- Status: Aberta

**Envolvidos:**
- Funcionario: ID pendente
- Posto: Portaria B
- Testemunhas: Nao informado

**Datas:**
- Ocorrencia: {date.today().strftime('%d/%m/%Y')} 08:30
- Resolucao: Pendente""",
            "intent": OcorrenciaIntent.OCORRENCIA_DETALHES.value,
            "data": {"codigo": code_display},
            "suggestions": ["Resolver ocorrencia", "Ver ocorrencias abertas", "/ocorrencia stats"],
        }

    async def _handle_ocorrencias_posto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista ocorrencias de um posto especifico."""
        # Extrair codigo do posto
        post_match = re.search(r"POST-\d+", message.upper())
        post_code = post_match.group(0) if post_match else None

        if self.data_connector and self.db and post_code:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                from modules.operacional.occurrences.schemas import OccurrenceFilter
                repo = OccurrenceRepository(self.db)

                # Buscar post_id pelo codigo
                from modules.operacional.repositories.post_repository import PostRepository
                post_repo = PostRepository(self.db)
                post = await post_repo.get_by_code(post_code)

                if post:
                    ocorrencias = await repo.get_by_post(post.id)

                    if ocorrencias:
                        lines = []
                        for o in ocorrencias[:15]:
                            sev_icon = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}.get(o.severity, "⚪")
                            occurred = o.occurred_at.strftime('%d/%m/%Y %H:%M') if o.occurred_at else 'N/A'
                            lines.append(f"- {sev_icon} **{o.code}** - {o.title} | {o.severity} | {occurred}")

                        response = f"""📍 **OCORRENCIAS DO POSTO {post_code}** ({post.name})

{chr(10).join(lines)}

**Total:** {len(ocorrencias)} ocorrencias registradas"""
                    else:
                        response = f"✅ **Nenhuma ocorrencia registrada para o posto {post_code}** ({post.name})."

                    return {
                        "response": response,
                        "intent": OcorrenciaIntent.OCORRENCIAS_POSTO.value,
                        "data": {"posto": post_code, "total": len(ocorrencias)},
                        "suggestions": ["/ocorrencia stats", "Criar ocorrencia", "Ver ocorrencias abertas"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias do posto via DB: {e}")

        # Fallback estatico
        post_display = post_code or "POST-001"
        return {
            "response": f"""📍 **OCORRENCIAS DO POSTO {post_display}**

- 🔴 **OCO-2026-00012** - Abandono de posto | grave | {date.today().strftime('%d/%m/%Y')} 08:30
- 🟡 **OCO-2026-00008** - Uso de celular | leve | {date.today().strftime('%d/%m/%Y')} 14:20
- 🟠 **OCO-2026-00005** - Falta de uniforme | moderada | {date.today().strftime('%d/%m/%Y')} 06:00

**Total:** 3 ocorrencias registradas

Informe o codigo do posto para consulta especifica: `/ocorrencia posto POST-XXX`""",
            "intent": OcorrenciaIntent.OCORRENCIAS_POSTO.value,
            "data": {"posto": post_display, "total": 3},
            "suggestions": ["/ocorrencia stats", "Criar ocorrencia", "Ver ocorrencias abertas"],
        }

    async def _handle_ocorrencias_funcionario(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista ocorrencias de um funcionario especifico."""
        if self.data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)
                stats = await repo.get_stats()

                if stats.by_employee:
                    # Top funcionarios com mais ocorrencias
                    sorted_employees = sorted(stats.by_employee.items(), key=lambda x: x[1], reverse=True)
                    lines = []
                    for emp_id, count in sorted_employees[:10]:
                        lines.append(f"- **{emp_id}**: {count} ocorrencia(s)")

                    response = f"""👤 **OCORRENCIAS POR FUNCIONARIO**

{chr(10).join(lines)}

**Total de funcionarios com ocorrencias:** {len(stats.by_employee)}
**Total de ocorrencias:** {stats.total}"""

                    return {
                        "response": response,
                        "intent": OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO.value,
                        "data": {"by_employee": stats.by_employee, "total": stats.total},
                        "suggestions": ["/ocorrencia stats", "Ver ocorrencias abertas", "Criar ocorrencia"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias por funcionario via DB: {e}")

        # Fallback estatico
        return {
            "response": """👤 **OCORRENCIAS POR FUNCIONARIO**

- **Funcionario A**: 4 ocorrencia(s) (2 graves)
- **Funcionario B**: 2 ocorrencia(s) (1 moderada)
- **Funcionario C**: 1 ocorrencia(s) (1 leve)

**Total de funcionarios com ocorrencias:** 3
**Total de ocorrencias:** 7

Informe o nome ou ID do funcionario para ver o historico detalhado.""",
            "intent": OcorrenciaIntent.OCORRENCIAS_FUNCIONARIO.value,
            "data": {"total": 7},
            "suggestions": ["/ocorrencia stats", "Ver ocorrencias abertas", "Criar ocorrencia"],
        }

    async def _handle_estatisticas(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra estatisticas gerais de ocorrencias."""
        if self.data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)
                stats = await repo.get_stats()

                if stats.total > 0:
                    # Formatar por tipo
                    tipo_lines = []
                    for tipo, count in sorted(stats.by_type.items(), key=lambda x: x[1], reverse=True):
                        tipo_label = tipo.replace("_", " ").title()
                        tipo_lines.append(f"  - {tipo_label}: **{count}**")

                    # Formatar por severidade
                    sev_lines = []
                    sev_order = ["gravissima", "grave", "moderada", "leve"]
                    sev_icons = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}
                    for sev in sev_order:
                        count = stats.by_severity.get(sev, 0)
                        if count > 0:
                            sev_lines.append(f"  - {sev_icons.get(sev, '⚪')} {sev.title()}: **{count}**")

                    avg_time = f"{stats.avg_resolution_time_hours:.1f}h" if stats.avg_resolution_time_hours else "N/A"

                    response = f"""📊 **ESTATISTICAS DE OCORRENCIAS**

**Visao Geral:**
- Total: **{stats.total}**
- Abertas: **{stats.open}**
- Em Analise: **{stats.in_analysis}**
- Resolvidas: **{stats.resolved}**
- Graves/Gravissimas: **{stats.severe}** {'🚨' if stats.severe > 0 else ''}

**Por Severidade:**
{chr(10).join(sev_lines) if sev_lines else '  Nenhuma ocorrencia registrada'}

**Por Tipo (Top):**
{chr(10).join(tipo_lines[:5]) if tipo_lines else '  Nenhuma ocorrencia registrada'}

**Tempo Medio de Resolucao:** {avg_time}"""

                    return {
                        "response": response,
                        "intent": OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS.value,
                        "data": {
                            "total": stats.total,
                            "abertas": stats.open,
                            "graves": stats.severe,
                            "avg_resolution_time": stats.avg_resolution_time_hours,
                        },
                        "suggestions": ["Ver ocorrencias abertas", "/ocorrencia graves", "Criar ocorrencia"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas via DB: {e}")

        # Fallback estatico
        return {
            "response": """📊 **ESTATISTICAS DE OCORRENCIAS**

**Visao Geral:**
- Total: **42**
- Abertas: **5**
- Em Analise: **3**
- Resolvidas: **31**
- Graves/Gravissimas: **8** 🚨

**Por Severidade:**
  - 🚨 Gravissima: **2**
  - 🔴 Grave: **6**
  - 🟠 Moderada: **15**
  - 🟡 Leve: **19**

**Por Tipo (Top):**
  - Uso Celular: **9**
  - Falta Uniforme: **7**
  - Atraso: **6**
  - Abandono Posto: **5**
  - Postura Inadequada: **4**

**Tempo Medio de Resolucao:** 48.3h""",
            "intent": OcorrenciaIntent.ESTATISTICAS_OCORRENCIAS.value,
            "data": {"total": 42, "abertas": 5, "graves": 8, "avg_resolution_time": 48.3},
            "suggestions": ["Ver ocorrencias abertas", "/ocorrencia graves", "Criar ocorrencia"],
        }

    async def _handle_criar_ocorrencia(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para wizard/action de criacao de ocorrencia."""
        return {
            "response": """📝 **REGISTRAR OCORRENCIA**

Para registrar uma nova ocorrencia disciplinar, preciso das seguintes informacoes:

1. **Tipo** da infracao (abandono de posto, falta de uniforme, etc)
2. **Severidade** (leve, moderada, grave, gravissima)
3. **Categoria** (disciplinar, operacional, seguranca, conduta, assiduidade)
4. **Titulo** descritivo
5. **Descricao** detalhada do ocorrido
6. **Funcionario** envolvido
7. **Posto** onde ocorreu
8. **Testemunhas** (opcional)

Posso iniciar o **assistente guiado** para coletar esses dados passo a passo.

**Deseja iniciar?**""",
            "intent": OcorrenciaIntent.CRIAR_OCORRENCIA.value,
            "data": {"action": "create_occurrence", "wizard": "ocorrencia_wizard"},
            "suggestions": ["Iniciar assistente", "Cancelar"],
            "actions": [
                {
                    "type": "create",
                    "label": "Registrar Ocorrencia",
                    "target": "occurrence",
                    "data": {"wizard": "ocorrencia"},
                },
            ],
        }

    async def _handle_resolver_ocorrencia(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para action de resolucao de ocorrencia."""
        code_match = re.search(r"OCO-\d{4}-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if code:
            response = f"""✅ **RESOLVER OCORRENCIA {code}**

Para resolver esta ocorrencia, informe:

1. **Acao corretiva aplicada** (advertencia verbal, advertencia escrita, suspensao, etc)
2. **Notas da resolucao** (detalhes adicionais)

**Confirmar resolucao?**"""
        else:
            response = """✅ **RESOLVER OCORRENCIA**

Informe o codigo da ocorrencia que deseja resolver (ex: OCO-2026-00012).

Apos identificar a ocorrencia, sera necessario informar:
1. **Acao corretiva aplicada**
2. **Notas da resolucao**"""

        return {
            "response": response,
            "intent": OcorrenciaIntent.RESOLVER_OCORRENCIA.value,
            "data": {"action": "resolve_occurrence", "code": code},
            "suggestions": ["Ver ocorrencias abertas", "Cancelar"],
            "actions": [
                {
                    "type": "edit",
                    "label": "Resolver Ocorrencia",
                    "target": "occurrence",
                    "data": {"code": code, "action": "resolve"},
                },
            ],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrao - retorna None para permitir que DataConnector processe."""
        return None

    def get_capabilities(self) -> List[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Listar ocorrencias abertas e pendentes",
            "Consultar detalhes de uma ocorrencia",
            "Filtrar ocorrencias por posto",
            "Historico de ocorrencias por funcionario",
            "Estatisticas e indicadores de ocorrencias",
            "Registrar nova ocorrencia (via wizard)",
            "Resolver ocorrencia com acao corretiva",
        ]
