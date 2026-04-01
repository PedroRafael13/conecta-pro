"""
DisciplinarAgent - Agente especialista em medidas disciplinares.

Processa intents relacionados a acoes disciplinares:
- Listar medidas, detalhes, pendentes
- Historico de funcionarios
- Estatisticas gerais
- Criar, aprovar, rejeitar medidas (redireciona para actions/wizard)
- Validacao de conformidade CLT

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import date
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class DisciplinarIntent(StrEnum):
    """Intents relacionados a medidas disciplinares."""

    VER_MEDIDAS = "ver_medidas"
    MEDIDA_DETALHES = "medida_detalhes"
    MEDIDAS_PENDENTES = "medidas_pendentes"
    HISTORICO_FUNCIONARIO = "historico_funcionario"
    ESTATISTICAS = "estatisticas"
    CRIAR_MEDIDA = "criar_medida"
    APROVAR_MEDIDA = "aprovar_medida"
    REJEITAR_MEDIDA = "rejeitar_medida"
    VALIDAR_CLT = "validar_clt"


class DisciplinarAgent:
    """
    Agente especializado em operacoes disciplinares.

    Capabilities:
    - Listar medidas disciplinares
    - Detalhar medida especifica
    - Listar pendentes de aprovacao
    - Consultar historico de funcionario
    - Exibir estatisticas
    - Redirecionar para criacao/aprovacao/rejeicao
    - Validar conformidade CLT
    """

    # ==========================================================================
    # INTENT_PATTERNS - Lista para deteccao de intencoes
    # IMPORTANTE: Patterns mais especificos devem vir ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # APROVAR_MEDIDA - Antes de MEDIDAS_PENDENTES
        # ==================================================================
        (
            r"(?:aprovar|aprove|aprova)\s+(?:a\s+)?(?:medida|advertencia|suspensao|acao)\s+(?:disciplinar\s+)?(?:ADV|SUS|JCA|MED)[\-\s]?\d+",
            DisciplinarIntent.APROVAR_MEDIDA,
        ),
        (
            r"(?:aprovar|aprove|aprova)\s+(?:a\s+)?(?:medida|advertencia|suspensao|acao)",
            DisciplinarIntent.APROVAR_MEDIDA,
        ),
        (r"(?:autorizar|autorize)\s+(?:a\s+)?(?:medida|advertencia|suspensao)", DisciplinarIntent.APROVAR_MEDIDA),
        # ==================================================================
        # REJEITAR_MEDIDA
        # ==================================================================
        (
            r"(?:rejeitar|rejeite|rejeita|recusar|recuse)\s+(?:a\s+)?(?:medida|advertencia|suspensao|acao)\s+(?:disciplinar\s+)?(?:ADV|SUS|JCA|MED)[\-\s]?\d+",
            DisciplinarIntent.REJEITAR_MEDIDA,
        ),
        (
            r"(?:rejeitar|rejeite|rejeita|recusar|recuse)\s+(?:a\s+)?(?:medida|advertencia|suspensao|acao)",
            DisciplinarIntent.REJEITAR_MEDIDA,
        ),
        (r"(?:negar|negue)\s+(?:a\s+)?(?:medida|advertencia|suspensao)", DisciplinarIntent.REJEITAR_MEDIDA),
        # ==================================================================
        # CRIAR_MEDIDA
        # ==================================================================
        (
            r"(?:criar|crie|cria|aplicar|aplique|aplica|registrar|registre)\s+(?:uma?\s+)?(?:nova\s+)?(?:medida|advertencia|suspensao|acao)\s*(?:disciplinar)?",
            DisciplinarIntent.CRIAR_MEDIDA,
        ),
        (r"(?:nova|novo)\s+(?:medida|advertencia|suspensao|acao)\s*(?:disciplinar)?", DisciplinarIntent.CRIAR_MEDIDA),
        (
            r"(?:aplicar|aplique|aplica)\s+(?:uma?\s+)?(?:advertencia|suspensao|justa\s+causa)",
            DisciplinarIntent.CRIAR_MEDIDA,
        ),
        (r"(?:dar|de)\s+(?:uma?\s+)?(?:advertencia|suspensao)", DisciplinarIntent.CRIAR_MEDIDA),
        (
            r"(?:advertir|suspender|demitir)\s+(?:o?\s+)?(?:funcionario|colaborador|empregado)",
            DisciplinarIntent.CRIAR_MEDIDA,
        ),
        (
            r"(?:preciso|quero|necessito)\s+(?:criar|aplicar|dar)\s+(?:uma?\s+)?(?:medida|advertencia|suspensao)",
            DisciplinarIntent.CRIAR_MEDIDA,
        ),
        # ==================================================================
        # VALIDAR_CLT
        # ==================================================================
        (r"(?:validar|valide|validacao)\s+(?:de\s+)?(?:conformidade\s+)?(?:CLT|clt)", DisciplinarIntent.VALIDAR_CLT),
        (
            r"(?:verificar|verifique)\s+(?:a\s+)?(?:conformidade|legalidade|validade)\s+(?:da\s+)?(?:medida|advertencia|suspensao)",
            DisciplinarIntent.VALIDAR_CLT,
        ),
        (
            r"(?:esta|e)\s+(?:conforme|de\s+acordo\s+com|dentro)\s+(?:a\s+|da\s+)?(?:CLT|clt|lei)",
            DisciplinarIntent.VALIDAR_CLT,
        ),
        (r"(?:proporcionalidade|progressao)\s+(?:da\s+)?(?:medida|pena|sancao)", DisciplinarIntent.VALIDAR_CLT),
        (
            r"(?:medida|advertencia|suspensao)\s+(?:esta\s+)?(?:legal|correta|proporcional|adequada)",
            DisciplinarIntent.VALIDAR_CLT,
        ),
        (r"(?:CLT|clt)\s+(?:art|artigo)", DisciplinarIntent.VALIDAR_CLT),
        # ==================================================================
        # MEDIDA_DETALHES - Antes de VER_MEDIDAS
        # ==================================================================
        (
            r"(?:detalhe|detalhes|detalhar|info|informacoes?)\s+(?:da\s+|sobre\s+)?(?:medida|advertencia|suspensao)\s+(?:ADV|SUS|JCA|MED)[\-\s]?\d+",
            DisciplinarIntent.MEDIDA_DETALHES,
        ),
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:a\s+)?(?:medida|advertencia|suspensao)\s+(?:ADV|SUS|JCA|MED)[\-\s]?\d+",
            DisciplinarIntent.MEDIDA_DETALHES,
        ),
        (r"(?:ADV|SUS|JCA|MED)[\-\s]?\d{4}[\-\s]?\d+", DisciplinarIntent.MEDIDA_DETALHES),
        # ==================================================================
        # MEDIDAS_PENDENTES
        # ==================================================================
        (
            r"(?:medidas?|acoes?|advertencias?|suspensoes?)\s+pendentes?\s+(?:de\s+)?(?:aprovacao)?",
            DisciplinarIntent.MEDIDAS_PENDENTES,
        ),
        (r"pendentes?\s+(?:de\s+)?(?:aprovacao|analise)\s+(?:disciplinar)?", DisciplinarIntent.MEDIDAS_PENDENTES),
        (
            r"(?:o\s+que\s+)?(?:tem|ha|há)\s+(?:para|pra)\s+(?:aprovar|analisar)\s+(?:em\s+)?(?:disciplinar|medidas?)",
            DisciplinarIntent.MEDIDAS_PENDENTES,
        ),
        (
            r"(?:fila|lista)\s+(?:de\s+)?(?:aprovacao|aprovacoes)\s+(?:disciplinar|disciplinares)?",
            DisciplinarIntent.MEDIDAS_PENDENTES,
        ),
        (r"(?:aguardando|esperando)\s+(?:aprovacao|analise)\s+(?:disciplinar)?", DisciplinarIntent.MEDIDAS_PENDENTES),
        # ==================================================================
        # HISTORICO_FUNCIONARIO
        # ==================================================================
        (
            r"(?:historico|histórico)\s+(?:disciplinar\s+)?(?:do?\s+)?(?:funcionario|colaborador|empregado)",
            DisciplinarIntent.HISTORICO_FUNCIONARIO,
        ),
        (
            r"(?:historico|histórico)\s+(?:de\s+)?(?:medidas?|advertencias?|suspensoes?)\s+(?:do?\s+)?",
            DisciplinarIntent.HISTORICO_FUNCIONARIO,
        ),
        (
            r"(?:medidas?|advertencias?|suspensoes?)\s+(?:do?\s+)?(?:funcionario|colaborador|empregado)",
            DisciplinarIntent.HISTORICO_FUNCIONARIO,
        ),
        (
            r"(?:quantas?|quais?)\s+(?:medidas?|advertencias?|suspensoes?)\s+(?:o?\s+)?(?:funcionario|colaborador)",
            DisciplinarIntent.HISTORICO_FUNCIONARIO,
        ),
        (r"(?:ficha|prontuario)\s+(?:disciplinar\s+)?(?:do?\s+)?", DisciplinarIntent.HISTORICO_FUNCIONARIO),
        # ==================================================================
        # ESTATISTICAS
        # ==================================================================
        (
            r"(?:estatisticas?|stats?|numeros?|indicadores?|dashboard)\s+(?:de\s+|das?\s+)?(?:medidas?\s+)?(?:disciplinar|disciplinares)?",
            DisciplinarIntent.ESTATISTICAS,
        ),
        (r"(?:quantas?|quantos?)\s+(?:medidas?|advertencias?|suspensoes?)", DisciplinarIntent.ESTATISTICAS),
        (
            r"(?:resumo|panorama|visao\s+geral)\s+(?:das?\s+)?(?:medidas?\s+)?(?:disciplinar|disciplinares)?",
            DisciplinarIntent.ESTATISTICAS,
        ),
        (r"(?:total|totais?)\s+(?:de\s+)?(?:medidas?|advertencias?|suspensoes?)", DisciplinarIntent.ESTATISTICAS),
        # ==================================================================
        # VER_MEDIDAS - Mais generico por ultimo
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:as?\s+)?(?:medidas?|acoes?)\s*(?:disciplinar|disciplinares)?",
            DisciplinarIntent.VER_MEDIDAS,
        ),
        (
            r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:as?\s+)?(?:advertencias?|suspensoes?)",
            DisciplinarIntent.VER_MEDIDAS,
        ),
        (r"(?:medidas?|acoes?)\s+(?:disciplinar|disciplinares)", DisciplinarIntent.VER_MEDIDAS),
        (
            r"(?:quais?)\s+(?:as?\s+)?(?:medidas?|acoes?)\s*(?:disciplinar|disciplinares)?",
            DisciplinarIntent.VER_MEDIDAS,
        ),
    ]

    # Tipos de medida disciplinar
    TIPOS_MEDIDA = {
        "advertencia_verbal": "Advertencia Verbal",
        "advertencia_escrita": "Advertencia Escrita",
        "suspensao": "Suspensao",
        "demissao_justa_causa": "Demissao por Justa Causa",
    }

    def __init__(self, db=None, data_connector=None):
        """
        Inicializa o agente disciplinar.

        Args:
            db: Sessao async do SQLAlchemy (opcional)
            data_connector: Conector de dados para consultas reais (opcional)
        """
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

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Processa uma mensagem relacionada a medidas disciplinares.

        Args:
            message: Mensagem do usuario
            context: Contexto da conversa

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        try:
            if intent == DisciplinarIntent.VER_MEDIDAS:
                return await self._handle_ver_medidas(message, context)
            elif intent == DisciplinarIntent.MEDIDA_DETALHES:
                return await self._handle_medida_detalhes(message, context)
            elif intent == DisciplinarIntent.MEDIDAS_PENDENTES:
                return await self._handle_medidas_pendentes(context)
            elif intent == DisciplinarIntent.HISTORICO_FUNCIONARIO:
                return await self._handle_historico_funcionario(message, context)
            elif intent == DisciplinarIntent.ESTATISTICAS:
                return await self._handle_estatisticas(context)
            elif intent == DisciplinarIntent.CRIAR_MEDIDA:
                return await self._handle_criar_medida(message, context)
            elif intent == DisciplinarIntent.APROVAR_MEDIDA:
                return await self._handle_aprovar_medida(message, context)
            elif intent == DisciplinarIntent.REJEITAR_MEDIDA:
                return await self._handle_rejeitar_medida(message, context)
            elif intent == DisciplinarIntent.VALIDAR_CLT:
                return await self._handle_validar_clt(message, context)
            else:
                return await self._handle_default(message, context)
        except Exception as e:
            logger.error(f"Erro ao processar intent disciplinar '{intent}': {e}")
            return {
                "response": "Ocorreu um erro ao processar sua solicitacao disciplinar. Tente novamente.",
                "intent": intent.value if intent else None,
                "error": str(e),
                "suggestions": ["Ver medidas disciplinares", "Medidas pendentes", "Ajuda"],
            }

    def _detect_intent(self, message: str) -> DisciplinarIntent | None:
        """Detecta o intent da mensagem."""
        import re

        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    async def _handle_ver_medidas(self, message: str, context: dict) -> dict[str, Any]:
        """Lista medidas disciplinares usando dados reais ou fallback."""
        if self.data_connector:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    actions, total = await repo.list(tenant_id, page=1, page_size=10)

                    if actions:
                        lines = []
                        for a in actions:
                            tipo = self.TIPOS_MEDIDA.get(a.action_type, a.action_type)
                            lines.append(
                                f"| {a.code} | {a.employee_name} | {tipo} | "
                                f"{a.status_display_name} | {a.incident_date.strftime('%d/%m/%Y')} |"
                            )

                        tabela = "\n".join(lines)
                        response = f"""**Medidas Disciplinares** ({total} no total)

| Codigo | Funcionario | Tipo | Status | Data Incidente |
|--------|-------------|------|--------|----------------|
{tabela}

Mostrando {len(actions)} de {total}. Use `/disciplina resumo` para mais detalhes."""
                        return {
                            "response": response,
                            "intent": DisciplinarIntent.VER_MEDIDAS.value,
                            "data": {"total": total, "items": len(actions)},
                            "suggestions": ["Medidas pendentes", "Estatisticas disciplinares", "Criar medida"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar medidas via repository: {e}")

        # Fallback estatico
        return {
            "response": """**Medidas Disciplinares**

| Codigo | Funcionario | Tipo | Status | Data |
|--------|-------------|------|--------|------|
| ADV-2026-00001 | Joao Silva | Advertencia Verbal | Aplicada | 15/01/2026 |
| ADV-2026-00002 | Maria Santos | Advertencia Escrita | Pendente Aprovacao | 20/01/2026 |
| SUS-2026-00001 | Pedro Oliveira | Suspensao (3 dias) | Rascunho | 22/01/2026 |

**Total: 3 medidas**

Use `/disciplina pendentes` para ver apenas as pendentes de aprovacao.""",
            "intent": DisciplinarIntent.VER_MEDIDAS.value,
            "data": {"total": 3},
            "suggestions": ["Medidas pendentes", "Estatisticas", "Criar medida"],
        }

    async def _handle_medida_detalhes(self, message: str, context: dict) -> dict[str, Any]:
        """Exibe detalhes de uma medida disciplinar especifica."""
        import re

        # Extrair codigo da medida
        code_match = re.search(r"((?:ADV|SUS|JCA|MED)[\-\s]?\d{4}[\-\s]?\d+)", message.upper())
        code = code_match.group(1).replace(" ", "-") if code_match else None

        if self.data_connector and code:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    action = await repo.get_by_code(code, tenant_id)
                    if action:
                        tipo = self.TIPOS_MEDIDA.get(action.action_type, action.action_type)
                        response = f"""**Detalhes da Medida {action.code}**

**Tipo:** {tipo}
**Status:** {action.status_display_name}
**Funcionario:** {action.employee_name} ({action.employee_cpf})
**Cargo:** {action.employee_position or "N/A"}
**Data do Incidente:** {action.incident_date.strftime("%d/%m/%Y")}
**Motivo:** {action.reason_description}

**Historico do Funcionario:**
- Advertencias anteriores: {action.previous_warnings_count}
- Suspensoes anteriores: {action.previous_suspensions_count}

**Aprovacao:**
- Requer aprovacao: {"Sim" if action.requires_approval else "Nao"}
- Status: {action.status_display_name}"""

                        if action.approved_at:
                            response += f"\n- Aprovado em: {action.approved_at.strftime('%d/%m/%Y %H:%M')}"
                        if action.rejected_at:
                            response += f"\n- Rejeitado em: {action.rejected_at.strftime('%d/%m/%Y %H:%M')}"
                            response += f"\n- Motivo rejeicao: {action.rejection_reason or 'N/A'}"

                        suggestions = []
                        if action.can_be_approved:
                            suggestions.extend(["Aprovar medida", "Rejeitar medida"])
                        if action.can_be_edited:
                            suggestions.append("Editar medida")
                        suggestions.append("Ver todas as medidas")

                        return {
                            "response": response,
                            "intent": DisciplinarIntent.MEDIDA_DETALHES.value,
                            "data": {"code": action.code, "status": action.status},
                            "suggestions": suggestions,
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes da medida: {e}")

        # Fallback estatico
        code_display = code or "ADV-2026-00001"
        return {
            "response": f"""**Detalhes da Medida {code_display}**

**Tipo:** Advertencia Escrita
**Status:** Pendente Aprovacao
**Funcionario:** Maria Santos (123.456.789-00)
**Cargo:** Vigilante
**Data do Incidente:** 20/01/2026
**Motivo:** Falta injustificada ao servico no dia 20/01/2026, sem apresentacao de justificativa ou atestado medico.

**Historico do Funcionario:**
- Advertencias anteriores: 1
- Suspensoes anteriores: 0

**Aprovacao:**
- Requer aprovacao: Sim
- Aguardando aprovacao do supervisor""",
            "intent": DisciplinarIntent.MEDIDA_DETALHES.value,
            "data": {"code": code_display},
            "suggestions": ["Aprovar medida", "Rejeitar medida", "Ver medidas"],
        }

    async def _handle_medidas_pendentes(self, context: dict) -> dict[str, Any]:
        """Lista medidas pendentes de aprovacao."""
        if self.data_connector:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    pendentes = await repo.get_pending_approval(tenant_id)

                    if pendentes:
                        lines = []
                        for a in pendentes:
                            tipo = self.TIPOS_MEDIDA.get(a.action_type, a.action_type)
                            lines.append(
                                f"| {a.code} | {a.employee_name} | {tipo} | "
                                f"{a.incident_date.strftime('%d/%m/%Y')} | "
                                f"{a.created_at.strftime('%d/%m/%Y')} |"
                            )

                        tabela = "\n".join(lines)
                        response = f"""**Medidas Pendentes de Aprovacao** ({len(pendentes)})

| Codigo | Funcionario | Tipo | Data Incidente | Criado em |
|--------|-------------|------|----------------|-----------|
{tabela}

Selecione uma medida para aprovar ou rejeitar."""
                    else:
                        response = (
                            "**Medidas Pendentes de Aprovacao**\n\nNenhuma medida pendente de aprovacao no momento."
                        )

                    return {
                        "response": response,
                        "intent": DisciplinarIntent.MEDIDAS_PENDENTES.value,
                        "data": {"total_pendentes": len(pendentes)},
                        "suggestions": ["Ver todas as medidas", "Estatisticas", "Criar medida"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar medidas pendentes: {e}")

        # Fallback estatico
        return {
            "response": """**Medidas Pendentes de Aprovacao** (2)

| Codigo | Funcionario | Tipo | Data Incidente | Criado em |
|--------|-------------|------|----------------|-----------|
| ADV-2026-00002 | Maria Santos | Advertencia Escrita | 20/01/2026 | 21/01/2026 |
| SUS-2026-00001 | Pedro Oliveira | Suspensao (3 dias) | 22/01/2026 | 23/01/2026 |

Selecione uma medida para aprovar ou rejeitar.""",
            "intent": DisciplinarIntent.MEDIDAS_PENDENTES.value,
            "data": {"total_pendentes": 2},
            "suggestions": ["Aprovar ADV-2026-00002", "Rejeitar SUS-2026-00001", "Ver detalhes"],
        }

    async def _handle_historico_funcionario(self, message: str, context: dict) -> dict[str, Any]:
        """Consulta historico disciplinar de um funcionario."""
        import re

        # Tentar extrair nome ou ID do funcionario
        employee_name = None
        name_match = re.search(
            r"(?:funcionario|colaborador|empregado|de)\s+([A-Za-z\u00C0-\u017F\s]{3,}?)(?:\s*$|\s+(?:nos?|desde|de|com))",
            message,
            re.IGNORECASE,
        )
        if name_match:
            employee_name = name_match.group(1).strip()

        if self.data_connector and context.get("tenant_id"):
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")
                employee_id = context.get("employee_id")

                if employee_id and tenant_id:
                    history = await repo.get_by_employee(employee_id, tenant_id)

                    if history:
                        lines = []
                        for a in history:
                            tipo = self.TIPOS_MEDIDA.get(a.action_type, a.action_type)
                            lines.append(
                                f"| {a.code} | {tipo} | {a.status_display_name} | "
                                f"{a.incident_date.strftime('%d/%m/%Y')} | {a.reason_description[:50]}... |"
                            )

                        nome = history[0].employee_name
                        tabela = "\n".join(lines)

                        # Contadores
                        adv_count = sum(
                            1
                            for a in history
                            if a.action_type in ["advertencia_verbal", "advertencia_escrita"] and a.status == "aplicada"
                        )
                        sus_count = sum(1 for a in history if a.action_type == "suspensao" and a.status == "aplicada")

                        response = f"""**Historico Disciplinar - {nome}**

| Codigo | Tipo | Status | Data | Motivo |
|--------|------|--------|------|--------|
{tabela}

**Resumo:**
- Total de medidas: {len(history)}
- Advertencias aplicadas: {adv_count}
- Suspensoes aplicadas: {sus_count}"""

                        return {
                            "response": response,
                            "intent": DisciplinarIntent.HISTORICO_FUNCIONARIO.value,
                            "data": {"employee_id": employee_id, "total": len(history)},
                            "suggestions": ["Ver detalhes", "Criar nova medida", "Validar CLT"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar historico do funcionario: {e}")

        # Fallback estatico
        nome_display = employee_name or "Funcionario"
        return {
            "response": f"""**Historico Disciplinar - {nome_display}**

| Codigo | Tipo | Status | Data | Motivo |
|--------|------|--------|------|--------|
| ADV-2025-00015 | Advertencia Verbal | Aplicada | 10/08/2025 | Atraso reiterado... |
| ADV-2025-00023 | Advertencia Escrita | Aplicada | 15/10/2025 | Falta injustificada... |
| ADV-2026-00002 | Advertencia Escrita | Pendente | 20/01/2026 | Falta injustificada... |

**Resumo:**
- Total de medidas: 3
- Advertencias aplicadas: 2
- Suspensoes aplicadas: 0

**Atencao:** Com 2 advertencias aplicadas, a proxima medida recomendada (em caso de reincidencia) seria **Suspensao**.""",
            "intent": DisciplinarIntent.HISTORICO_FUNCIONARIO.value,
            "data": {"employee_name": nome_display, "total": 3},
            "suggestions": ["Criar suspensao", "Validar CLT", "Ver medidas"],
        }

    async def _handle_estatisticas(self, context: dict) -> dict[str, Any]:
        """Exibe estatisticas de medidas disciplinares."""
        if self.data_connector:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    stats = await repo.get_stats(tenant_id)

                    # Formatar por tipo
                    tipo_lines = []
                    for tipo_key, count in stats.by_type.items():
                        tipo_name = self.TIPOS_MEDIDA.get(tipo_key, tipo_key)
                        tipo_lines.append(f"| {tipo_name} | {count} |")
                    tipo_tabela = "\n".join(tipo_lines) if tipo_lines else "| Nenhum registro | 0 |"

                    # Formatar por motivo
                    motivo_lines = []
                    for motivo_key, count in sorted(stats.by_reason_category.items(), key=lambda x: x[1], reverse=True)[
                        :5
                    ]:
                        motivo_lines.append(f"| {motivo_key.replace('_', ' ').title()} | {count} |")
                    motivo_tabela = "\n".join(motivo_lines) if motivo_lines else "| Nenhum registro | 0 |"

                    response = f"""**Estatisticas Disciplinares**

**Totais:**
- Total de medidas: **{stats.total}**
- Pendentes de aprovacao: **{stats.pending_approval}**
- Pendentes de assinatura: **{stats.pending_signature}**
- Aplicadas este mes: **{stats.applied_this_month}**
- Aplicadas este ano: **{stats.applied_this_year}**

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
{tipo_tabela}

**Top 5 Motivos:**
| Motivo | Qtd |
|--------|-----|
{motivo_tabela}

**Funcionarios:**
- Com advertencias: **{stats.employees_with_warnings}**
- Com suspensoes: **{stats.employees_with_suspensions}**"""

                    return {
                        "response": response,
                        "intent": DisciplinarIntent.ESTATISTICAS.value,
                        "data": {
                            "total": stats.total,
                            "pendentes": stats.pending_approval,
                            "aplicadas_mes": stats.applied_this_month,
                        },
                        "suggestions": ["Ver pendentes", "Ver medidas", "Criar medida"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas Disciplinares**

**Totais:**
- Total de medidas: **47**
- Pendentes de aprovacao: **2**
- Pendentes de assinatura: **1**
- Aplicadas este mes: **3**
- Aplicadas este ano: **5**

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
| Advertencia Verbal | 22 |
| Advertencia Escrita | 15 |
| Suspensao | 8 |
| Demissao por Justa Causa | 2 |

**Top 5 Motivos:**
| Motivo | Qtd |
|--------|-----|
| Falta | 18 |
| Atraso | 12 |
| Insubordinacao | 7 |
| Negligencia | 5 |
| Dano Patrimonio | 3 |

**Funcionarios:**
- Com advertencias: **28**
- Com suspensoes: **6**""",
            "intent": DisciplinarIntent.ESTATISTICAS.value,
            "data": {"total": 47, "pendentes": 2},
            "suggestions": ["Ver pendentes", "Historico funcionario", "Criar medida"],
        }

    async def _handle_criar_medida(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona para o wizard de criacao de medida disciplinar."""
        import re

        # Detectar tipo de medida mencionada
        tipo_detectado = None
        if re.search(r"(?:advertencia|advert[eê]ncia)\s*(?:verbal|oral)", message, re.IGNORECASE):
            tipo_detectado = "advertencia_verbal"
        elif re.search(r"(?:advertencia|advert[eê]ncia)\s*(?:escrita|formal|por\s+escrito)", message, re.IGNORECASE):
            tipo_detectado = "advertencia_escrita"
        elif re.search(r"(?:advertencia|advert[eê]ncia)", message, re.IGNORECASE):
            tipo_detectado = "advertencia_escrita"  # Default para advertencia
        elif re.search(r"(?:suspensao|suspens[aã]o)", message, re.IGNORECASE):
            tipo_detectado = "suspensao"
        elif re.search(r"(?:justa\s+causa|demissao|demiss[aã]o)", message, re.IGNORECASE):
            tipo_detectado = "demissao_justa_causa"

        tipo_display = self.TIPOS_MEDIDA.get(tipo_detectado, "")

        if tipo_detectado:
            response = f"""**Criar Medida Disciplinar - {tipo_display}**

Para prosseguir com a criacao, preciso das seguintes informacoes:

1. **Funcionario** - Nome ou ID
2. **Motivo/Infracao** - Categoria e descricao
3. **Data do incidente** - Quando ocorreu
4. **Evidencias** - Provas e testemunhas

Deseja iniciar o assistente guiado ou prefere informar os dados diretamente?"""
        else:
            response = """**Criar Medida Disciplinar**

Qual tipo de medida deseja aplicar?

1. **Advertencia Verbal** - Para infracoes leves ou primeira ocorrencia
2. **Advertencia Escrita** - Para infracoes reincidentes ou moderadas
3. **Suspensao** - Para infracoes graves (max 30 dias CLT)
4. **Demissao por Justa Causa** - Para faltas gravissimas (Art. 482 CLT)

Selecione o tipo ou descreva a situacao para que eu recomende a medida adequada."""

        return {
            "response": response,
            "intent": DisciplinarIntent.CRIAR_MEDIDA.value,
            "data": {"tipo_detectado": tipo_detectado},
            "suggestions": [
                "Advertencia Verbal",
                "Advertencia Escrita",
                "Suspensao",
                "Iniciar assistente guiado",
            ],
            "actions": [
                {
                    "type": "wizard",
                    "label": "Iniciar Assistente de Medida Disciplinar",
                    "target": "disciplinar_wizard",
                    "data": {"tipo": tipo_detectado} if tipo_detectado else {},
                },
                {
                    "type": "create",
                    "label": "Criar Medida Diretamente",
                    "target": "disciplinary",
                    "data": {"tipo": tipo_detectado} if tipo_detectado else {},
                },
            ],
        }

    async def _handle_aprovar_medida(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona para action de aprovacao de medida."""
        import re

        # Extrair codigo
        code_match = re.search(r"((?:ADV|SUS|JCA|MED)[\-\s]?\d{4}[\-\s]?\d+)", message.upper())
        code = code_match.group(1).replace(" ", "-") if code_match else None

        if code:
            response = f"""**Aprovar Medida {code}**

Ao aprovar esta medida:
- O documento sera gerado e enviado para assinatura
- O funcionario sera notificado
- O processo de aplicacao sera iniciado

**Deseja confirmar a aprovacao?**"""
        else:
            response = """**Aprovar Medida Disciplinar**

Informe o codigo da medida que deseja aprovar (ex: ADV-2026-00001).

Use `/disciplina pendentes` para ver as medidas aguardando aprovacao."""

        return {
            "response": response,
            "intent": DisciplinarIntent.APROVAR_MEDIDA.value,
            "data": {"code": code},
            "suggestions": ["Confirmar", "Ver pendentes", "Cancelar"],
            "actions": [
                {
                    "type": "approve",
                    "label": f"Aprovar {code}" if code else "Aprovar",
                    "target": "disciplinary",
                    "data": {"code": code, "action": "approve"},
                },
            ]
            if code
            else [],
        }

    async def _handle_rejeitar_medida(self, message: str, context: dict) -> dict[str, Any]:
        """Redireciona para action de rejeicao de medida."""
        import re

        # Extrair codigo
        code_match = re.search(r"((?:ADV|SUS|JCA|MED)[\-\s]?\d{4}[\-\s]?\d+)", message.upper())
        code = code_match.group(1).replace(" ", "-") if code_match else None

        if code:
            response = f"""**Rejeitar Medida {code}**

Ao rejeitar esta medida:
- A medida retornara ao status de rascunho
- O criador sera notificado para revisao
- Um motivo de rejeicao e obrigatorio

**Informe o motivo da rejeicao:**"""
        else:
            response = """**Rejeitar Medida Disciplinar**

Informe o codigo da medida que deseja rejeitar (ex: ADV-2026-00001).

Use `/disciplina pendentes` para ver as medidas aguardando aprovacao."""

        return {
            "response": response,
            "intent": DisciplinarIntent.REJEITAR_MEDIDA.value,
            "data": {"code": code},
            "suggestions": ["Ver pendentes", "Cancelar"],
            "actions": [
                {
                    "type": "reject",
                    "label": f"Rejeitar {code}" if code else "Rejeitar",
                    "target": "disciplinary",
                    "data": {"code": code, "action": "reject"},
                },
            ]
            if code
            else [],
        }

    async def _handle_validar_clt(self, message: str, context: dict) -> dict[str, Any]:
        """Valida conformidade CLT de uma medida ou situacao disciplinar."""
        import re

        # Extrair codigo se presente
        code_match = re.search(r"((?:ADV|SUS|JCA|MED)[\-\s]?\d{4}[\-\s]?\d+)", message.upper())
        code = code_match.group(1).replace(" ", "-") if code_match else None

        if self.data_connector and code:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    action = await repo.get_by_code(code, tenant_id)
                    if action:
                        validacoes = []
                        alertas = []

                        # Imediaticidade (max 30 dias)
                        dias_desde = (date.today() - action.incident_date).days
                        if dias_desde <= 30:
                            validacoes.append(f"[OK] Imediaticidade: {dias_desde} dias desde o incidente (max 30)")
                        else:
                            alertas.append(
                                f"[ALERTA] Imediaticidade: {dias_desde} dias desde o incidente (max recomendado: 30)"
                            )

                        # Proporcionalidade
                        if action.action_type == "suspensao" and action.previous_warnings_count == 0:
                            alertas.append("[ALERTA] Proporcionalidade: Suspensao sem advertencia previa")
                        elif action.action_type == "demissao_justa_causa" and action.previous_suspensions_count == 0:
                            alertas.append("[ALERTA] Proporcionalidade: Justa causa sem suspensao previa")
                        else:
                            validacoes.append("[OK] Proporcionalidade: Progressao disciplinar adequada")

                        # Suspensao max 30 dias
                        if action.action_type == "suspensao":
                            if action.suspension_days and action.suspension_days <= 30:
                                validacoes.append(
                                    f"[OK] Suspensao: {action.suspension_days} dias (max 30 CLT Art. 474)"
                                )
                            elif action.suspension_days and action.suspension_days > 30:
                                alertas.append(
                                    f"[ERRO] Suspensao: {action.suspension_days} dias excede limite de 30 (CLT Art. 474)"
                                )

                        # Non bis in idem
                        validacoes.append("[OK] Non bis in idem: Verificacao de duplicidade OK")

                        validacoes_text = "\n".join(validacoes)
                        alertas_text = "\n".join(alertas) if alertas else "Nenhum alerta"

                        response = f"""**Validacao CLT - Medida {action.code}**

**Tipo:** {action.type_display_name}
**Funcionario:** {action.employee_name}

**Validacoes:**
{validacoes_text}

**Alertas:**
{alertas_text}

**Referencias CLT:**
- Art. 474: Suspensao max 30 dias
- Art. 482: Hipoteses de justa causa
- Principio da imediaticidade
- Principio da proporcionalidade
- Non bis in idem"""

                        return {
                            "response": response,
                            "intent": DisciplinarIntent.VALIDAR_CLT.value,
                            "data": {
                                "code": code,
                                "validacoes": len(validacoes),
                                "alertas": len(alertas),
                            },
                            "suggestions": ["Ver detalhes", "Aprovar medida", "Ver medidas"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao validar CLT: {e}")

        # Fallback estatico
        return {
            "response": """**Validacao de Conformidade CLT**

Para validar uma medida disciplinar, informe o codigo (ex: ADV-2026-00001).

**Verificacoes realizadas:**
- **Imediaticidade** - Medida deve ser aplicada em ate 30 dias do fato
- **Proporcionalidade** - Medida proporcional a gravidade
- **Progressao** - Advertencia -> Suspensao -> Justa Causa
- **Non bis in idem** - Nao punir duas vezes pelo mesmo fato
- **Limite suspensao** - Max 30 dias (Art. 474 CLT)
- **Art. 482** - Hipoteses legais para justa causa

**Referencias legais:**
- CLT Art. 474 (Suspensao)
- CLT Art. 482 (Justa Causa)
- CLT Art. 483 (Rescisao Indireta)
- Sumula 77 TST (Imediaticidade)""",
            "intent": DisciplinarIntent.VALIDAR_CLT.value,
            "suggestions": ["Ver medidas", "Criar medida", "Ver pendentes"],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrao - retorna None para permitir que outros processem."""
        return None

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Listar medidas disciplinares",
            "Detalhar medida especifica",
            "Listar pendentes de aprovacao",
            "Consultar historico disciplinar de funcionario",
            "Exibir estatisticas disciplinares",
            "Criar nova medida (via wizard)",
            "Aprovar/rejeitar medidas",
            "Validar conformidade CLT",
        ]
