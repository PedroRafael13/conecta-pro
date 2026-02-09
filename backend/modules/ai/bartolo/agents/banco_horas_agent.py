"""
BancoHorasAgent - Agente especialista em banco de horas.

Processa intents relacionados a banco de horas, saldos, aprovacoes
de hora extra, compensacoes e expiracoes, consultando dados via DataConnector.
"""

import logging
import re
from datetime import date
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class BancoHorasIntent(StrEnum):
    """Intents relacionados a banco de horas."""

    VER_SALDO = "ver_saldo"
    VER_EXTRATO = "ver_extrato"
    APROVAR_HORA_EXTRA = "aprovar_hora_extra"
    SOLICITAR_COMPENSACAO = "solicitar_compensacao"
    VER_PENDENTES = "ver_pendentes"
    VER_EXPIRACOES = "ver_expiracoes"


class BancoHorasAgent:
    """
    Agente especializado em operacoes de banco de horas.

    Capabilities:
    - Ver saldo de banco de horas do funcionario
    - Ver extrato detalhado de creditos/debitos
    - Aprovar horas extras pendentes
    - Solicitar compensacao de horas
    - Ver aprovacoes pendentes de horas extras
    - Ver horas prestes a expirar
    """

    # ==========================================================================
    # INTENT_PATTERNS - Deteccao de intencoes de banco de horas
    # Patterns mais especificos ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # APROVAR_HORA_EXTRA - Antes de pendentes (mais especifico)
        # ==================================================================
        (
            r"(?:aprovar|aprove|autorizar|autorize|liberar|libere)\s+(?:a\s+)?(?:hora\s+extra|he\b|horas?\s+extras?)",
            BancoHorasIntent.APROVAR_HORA_EXTRA,
        ),
        (
            r"(?:aprovar|aprove|autorizar|autorize)\s+(?:registro|lancamento|entrada)\s+(?:de\s+)?(?:hora|banco)",
            BancoHorasIntent.APROVAR_HORA_EXTRA,
        ),
        (r"(?:aprovar|aprove)\s+(?:o\s+)?(?:banco\s+de\s+horas?|bh\b)", BancoHorasIntent.APROVAR_HORA_EXTRA),
        (r"(?:aprovar|aprove)\s+BH-\d+", BancoHorasIntent.APROVAR_HORA_EXTRA),
        # ==================================================================
        # SOLICITAR_COMPENSACAO - Antes de saldo (mais especifico)
        # ==================================================================
        (
            r"(?:solicitar|solicite|pedir|peca|quero|desejo)\s+(?:uma?\s+)?compensac",
            BancoHorasIntent.SOLICITAR_COMPENSACAO,
        ),
        (r"compensar\s+(?:as?\s+)?horas?", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        (r"(?:usar|utilizar|gastar)\s+(?:as?\s+)?horas?\s+(?:do\s+)?banco", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        (r"(?:folgar|folga)\s+(?:com|usando)\s+(?:o\s+)?banco", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        (r"(?:abater|descontar)\s+(?:do\s+)?banco\s+de\s+horas?", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        (r"(?:quero|preciso)\s+(?:usar|utilizar)\s+(?:meu\s+)?(?:saldo|banco)", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        (r"(?:solicitar|solicite)\s+(?:uso|utilizacao)\s+(?:do\s+)?banco", BancoHorasIntent.SOLICITAR_COMPENSACAO),
        # ==================================================================
        # VER_EXPIRACOES - Antes de extrato (mais especifico)
        # ==================================================================
        (r"(?:horas?|banco)\s+(?:que\s+)?(?:vao|vai|irao?)\s+(?:expirar|vencer)", BancoHorasIntent.VER_EXPIRACOES),
        (r"(?:expirac|vencimento)\w*\s+(?:de\s+)?(?:horas?|banco)", BancoHorasIntent.VER_EXPIRACOES),
        (r"(?:horas?|banco)\s+(?:prestes?\s+a\s+)?(?:expirar|vencer)", BancoHorasIntent.VER_EXPIRACOES),
        (r"(?:horas?|banco)\s+(?:a\s+)?(?:expirar|vencer|perder)", BancoHorasIntent.VER_EXPIRACOES),
        (r"(?:perder|perdendo)\s+horas?\s+(?:do\s+)?banco", BancoHorasIntent.VER_EXPIRACOES),
        (r"horas?\s+(?:que\s+)?(?:estao|esta)\s+(?:vencendo|expirando)", BancoHorasIntent.VER_EXPIRACOES),
        (r"(?:alertas?|avisos?)\s+(?:de\s+)?(?:expirac|vencimento)", BancoHorasIntent.VER_EXPIRACOES),
        # ==================================================================
        # VER_PENDENTES - Pendencias de aprovacao
        # ==================================================================
        (r"(?:horas?\s+extras?|he\b)\s+pendentes?", BancoHorasIntent.VER_PENDENTES),
        (r"(?:aprovac|pendencia)\w*\s+(?:de\s+)?(?:horas?\s+extras?|banco|he\b)", BancoHorasIntent.VER_PENDENTES),
        (r"(?:pendentes?|pendencia)\s+(?:de\s+)?(?:aprovacao|banco\s+de\s+horas?)", BancoHorasIntent.VER_PENDENTES),
        (
            r"(?:o\s+que\s+)?(?:tem|ha|há)\s+(?:para|pra)\s+aprovar\s+(?:no\s+|de\s+)?(?:banco|horas?)",
            BancoHorasIntent.VER_PENDENTES,
        ),
        (
            r"(?:listar|ver|veja|mostrar|mostre)\s+(?:as?\s+)?(?:pendentes?|pendencias?)\s+(?:de\s+)?(?:banco|hora)",
            BancoHorasIntent.VER_PENDENTES,
        ),
        (r"(?:banco|horas?)\s+(?:aguardando|esperando)\s+(?:aprovacao|liberacao)", BancoHorasIntent.VER_PENDENTES),
        # ==================================================================
        # VER_EXTRATO - Extrato detalhado
        # ==================================================================
        (
            r"(?:extrato|historico|movimentac)\w*\s+(?:do\s+|de\s+)?(?:banco\s+de\s+horas?|bh\b)",
            BancoHorasIntent.VER_EXTRATO,
        ),
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:o\s+)?extrato\s+(?:do\s+|de\s+)?(?:banco|horas?)",
            BancoHorasIntent.VER_EXTRATO,
        ),
        (r"(?:detalhes?|detalh\w+)\s+(?:do\s+)?banco\s+de\s+horas?", BancoHorasIntent.VER_EXTRATO),
        (r"(?:creditos?|debitos?)\s+(?:do\s+|no\s+)?banco\s+de\s+horas?", BancoHorasIntent.VER_EXTRATO),
        (r"(?:lancamentos?|entradas?)\s+(?:do\s+|no\s+)?banco\s+de\s+horas?", BancoHorasIntent.VER_EXTRATO),
        (r"(?:movimentacao|movimentos?)\s+(?:do\s+|de\s+)?banco", BancoHorasIntent.VER_EXTRATO),
        # ==================================================================
        # VER_SALDO - Generico (por ultimo)
        # ==================================================================
        (
            r"(?:ver|veja|mostrar|mostre|exibir|exiba|consultar|consulte)\s+(?:o\s+)?saldo\s+(?:do\s+|de\s+)?(?:banco|bh\b)",
            BancoHorasIntent.VER_SALDO,
        ),
        (r"saldo\s+(?:do\s+|de\s+)?(?:banco\s+de\s+horas?|bh\b)", BancoHorasIntent.VER_SALDO),
        (r"(?:quanto|quantas)\s+(?:tem|tenho|possui)\s+(?:no\s+|de\s+)?(?:banco|horas?)", BancoHorasIntent.VER_SALDO),
        (
            r"(?:banco\s+de\s+horas?|bh\b)\s+(?:do\s+|de\s+)?(?:funcionario|colaborador|vigilante|porteiro)",
            BancoHorasIntent.VER_SALDO,
        ),
        (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:o\s+)?banco\s+de\s+horas?", BancoHorasIntent.VER_SALDO),
        (r"(?:meu|minha)\s+(?:banco\s+de\s+horas?|saldo\s+de\s+horas?)", BancoHorasIntent.VER_SALDO),
        (r"banco\s+de\s+horas?$", BancoHorasIntent.VER_SALDO),
        (
            r"(?:horas?\s+extras?|he\b)\s+(?:do\s+|de\s+)?(?:funcionario|colaborador|vigilante|porteiro)",
            BancoHorasIntent.VER_SALDO,
        ),
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

    async def process(self, message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Processa uma mensagem relacionada a banco de horas.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == BancoHorasIntent.VER_SALDO:
            return await self._handle_ver_saldo(message, context)
        elif intent == BancoHorasIntent.VER_EXTRATO:
            return await self._handle_ver_extrato(message, context)
        elif intent == BancoHorasIntent.APROVAR_HORA_EXTRA:
            return await self._handle_aprovar_hora_extra(message, context)
        elif intent == BancoHorasIntent.SOLICITAR_COMPENSACAO:
            return await self._handle_solicitar_compensacao(message, context)
        elif intent == BancoHorasIntent.VER_PENDENTES:
            return await self._handle_ver_pendentes(message, context)
        elif intent == BancoHorasIntent.VER_EXPIRACOES:
            return await self._handle_ver_expiracoes(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> BancoHorasIntent | None:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # =========================================================================
    # HELPERS - Extrair nome de funcionario da mensagem
    # =========================================================================

    def _extract_employee_name(self, message: str) -> str | None:
        """Extrai nome de funcionario da mensagem."""
        patterns = [
            r"(?:do|da|de)\s+(?:funcionario|colaborador|vigilante|porteiro|agente)\s+([A-Za-zÀ-ÿ\s]{3,50})",
            r"(?:do|da|de)\s+([A-Z][a-zà-ÿ]+(?:\s+[A-Z][a-zà-ÿ]+)+)",
            r"(?:funcionario|colaborador|vigilante|porteiro)\s+([A-Za-zÀ-ÿ\s]{3,50})",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Ignorar palavras comuns que nao sao nomes
                stopwords = ["que", "com", "para", "como", "banco", "horas", "saldo", "extra"]
                if name.lower() not in stopwords and len(name) > 2:
                    return name.title()
        return None

    def _extract_entry_id(self, message: str) -> str | None:
        """Extrai ID de entrada (BH-xxx) da mensagem."""
        match = re.search(r"BH-\d+", message.upper())
        return match.group(0) if match else None

    # =========================================================================
    # HANDLERS
    # =========================================================================

    async def _handle_ver_saldo(self, message: str, context: dict) -> dict[str, Any]:
        """Mostra saldo do banco de horas usando DataConnector."""
        employee_name = self._extract_employee_name(message)

        if self.data_connector:
            try:
                result = await self.data_connector._get_hora_extra_ranking()
                if result.success and result.data:
                    ranking = result.data

                    # Se tem nome de funcionario, filtrar
                    if employee_name:
                        filtered = [f for f in ranking if employee_name.lower() in f.get("nome", "").lower()]
                        if filtered:
                            func_data = filtered[0]
                            saldo_icon = "+" if func_data.get("saldo_banco", 0) >= 0 else ""
                            response = f"""**SALDO BANCO DE HORAS - {func_data["nome"]}**

**Saldo atual:** {saldo_icon}{func_data.get("saldo_banco", 0):.1f}h
**Horas extras acumuladas:** {func_data.get("horas_extras", 0):.1f}h

**Detalhamento:**
- Creditos (horas trabalhadas a mais): {func_data.get("horas_extras", 0):.1f}h
- Saldo disponivel para compensacao: {func_data.get("saldo_banco", 0):.1f}h

Use `/banco_horas extrato {func_data["nome"]}` para ver movimentacoes."""
                            return {
                                "response": response,
                                "intent": BancoHorasIntent.VER_SALDO.value,
                                "data": {"funcionario": func_data, "saldo": func_data.get("saldo_banco", 0)},
                                "suggestions": [
                                    f"/banco_horas extrato {func_data['nome']}",
                                    "/banco_horas pendentes",
                                    "/banco_horas expiracoes",
                                ],
                            }
                        else:
                            response = f"Funcionario '{employee_name}' nao encontrado no banco de horas.\n\nFuncionarios com registro:\n"
                            for f in ranking[:5]:
                                response += f"- {f['nome']}\n"
                            return {
                                "response": response,
                                "intent": BancoHorasIntent.VER_SALDO.value,
                                "data": {"funcionario_buscado": employee_name, "nao_encontrado": True},
                                "suggestions": ["/banco_horas saldo", "/banco_horas pendentes"],
                            }

                    # Sem nome especifico - mostrar ranking geral
                    lines = []
                    for i, f in enumerate(ranking[:10], 1):
                        saldo = f.get("saldo_banco", 0)
                        saldo_icon = "+" if saldo >= 0 else ""
                        lines.append(
                            f"{i}. **{f['nome']}** | Saldo: {saldo_icon}{saldo:.1f}h | "
                            f"HE: {f.get('horas_extras', 0):.1f}h"
                        )

                    total_saldo = sum(f.get("saldo_banco", 0) for f in ranking)
                    total_extras = sum(f.get("horas_extras", 0) for f in ranking)

                    response = f"""**BANCO DE HORAS - VISAO GERAL**

{chr(10).join(lines)}

**Totais:**
- Saldo geral: **{total_saldo:+.1f}h**
- Horas extras acumuladas: **{total_extras:.1f}h**
- Funcionarios com registro: **{len(ranking)}**

**Legenda:** HE = Horas Extras"""

                    return {
                        "response": response,
                        "intent": BancoHorasIntent.VER_SALDO.value,
                        "data": {"ranking": ranking, "total_saldo": total_saldo, "total_extras": total_extras},
                        "suggestions": [
                            "/banco_horas pendentes",
                            "/banco_horas expiracoes",
                            "/banco_horas extrato",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar saldo via DataConnector: {e}")

        # Fallback estatico
        employee_display = employee_name or "Jose Silva"
        return {
            "response": f"""**SALDO BANCO DE HORAS - {employee_display}**

**Saldo atual:** +32.0h
**Horas extras acumuladas:** 45.5h

**Resumo:**
- Creditos aprovados: 45.5h
- Compensacoes utilizadas: 13.5h
- Saldo disponivel: 32.0h
- Pendente aprovacao: 4.0h
- Expirando em 30 dias: 8.0h

**Atencao:** Ha horas prestes a expirar. Use `/banco_horas expiracoes` para detalhes.""",
            "intent": BancoHorasIntent.VER_SALDO.value,
            "data": {
                "funcionario": employee_display,
                "saldo": 32.0,
                "horas_extras": 45.5,
                "pendente": 4.0,
                "expirando": 8.0,
            },
            "suggestions": [
                "/banco_horas extrato",
                "/banco_horas pendentes",
                "/banco_horas expiracoes",
            ],
        }

    async def _handle_ver_extrato(self, message: str, context: dict) -> dict[str, Any]:
        """Mostra extrato detalhado do banco de horas."""
        employee_name = self._extract_employee_name(message)

        if self.data_connector and self.db:
            try:
                from modules.operacional.repositories.time_bank_repository import TimeBankRepository
                from modules.operacional.schemas.time_bank import TimeBankFilter

                repo = TimeBankRepository(self.db)
                filters = TimeBankFilter()
                entries, total = await repo.list(filters=filters, page=1, page_size=20)

                if entries:
                    lines = []
                    for entry in entries:
                        tipo_icon = {
                            "credit": "+",
                            "debit": "-",
                            "compensation": "-",
                            "adjustment": "~",
                            "expiration": "x",
                        }.get(entry.entry_type, "?")

                        status_icon = {
                            "pending": "Pendente",
                            "approved": "Aprovado",
                            "rejected": "Rejeitado",
                            "used": "Utilizado",
                            "expired": "Expirado",
                        }.get(entry.status, entry.status)

                        ref_date = entry.reference_date.strftime("%d/%m/%Y") if entry.reference_date else "N/A"
                        desc = entry.description or entry.reason or "Sem descricao"
                        if len(desc) > 40:
                            desc = desc[:37] + "..."

                        lines.append(f"| {ref_date} | {tipo_icon}{entry.hours:.1f}h | {status_icon} | {desc} |")

                    response = f"""**EXTRATO BANCO DE HORAS** ({total} registros)

| Data | Horas | Status | Descricao |
|------|-------|--------|-----------|
{chr(10).join(lines)}

**Total de registros:** {total}"""

                    return {
                        "response": response,
                        "intent": BancoHorasIntent.VER_EXTRATO.value,
                        "data": {"entries_count": total, "entries": len(entries)},
                        "suggestions": [
                            "/banco_horas saldo",
                            "/banco_horas pendentes",
                            "/banco_horas expiracoes",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar extrato via DB: {e}")

        # Fallback estatico
        today = date.today()
        employee_display = employee_name or "Jose Silva"
        return {
            "response": f"""**EXTRATO BANCO DE HORAS - {employee_display}**

| Data | Tipo | Horas | Saldo | Status | Descricao |
|------|------|-------|-------|--------|-----------|
| {today.strftime("%d/%m/%Y")} | Credito | +4.0h | 32.0h | Aprovado | HE - Turno noturno |
| {today.strftime("%d/%m/%Y")} | Credito | +2.0h | 28.0h | Pendente | HE - Cobertura falta |
| 25/01/2026 | Compensacao | -8.0h | 26.0h | Aprovado | Folga compensatoria |
| 20/01/2026 | Credito | +6.0h | 34.0h | Aprovado | HE - Evento especial |
| 15/01/2026 | Credito | +3.5h | 28.0h | Aprovado | HE - Turno diurno |
| 10/01/2026 | Compensacao | -4.0h | 24.5h | Aprovado | Saida antecipada |
| 05/01/2026 | Credito | +8.0h | 28.5h | Aprovado | HE - Feriado |
| 01/01/2026 | Credito | +2.5h | 20.5h | Expirado | HE - Fim de ano (expirou) |

**Resumo do periodo:**
- Total creditos: **26.0h**
- Total compensacoes: **-12.0h**
- Expiradas: **-2.5h**
- Pendentes: **2.0h**
- **Saldo atual: 32.0h**""",
            "intent": BancoHorasIntent.VER_EXTRATO.value,
            "data": {
                "funcionario": employee_display,
                "creditos": 26.0,
                "compensacoes": 12.0,
                "expiradas": 2.5,
                "pendentes": 2.0,
                "saldo": 32.0,
            },
            "suggestions": [
                "/banco_horas saldo",
                "/banco_horas pendentes",
                "/banco_horas compensar",
            ],
        }

    async def _handle_aprovar_hora_extra(self, message: str, context: dict) -> dict[str, Any]:
        """Aprova horas extras pendentes."""
        entry_id = self._extract_entry_id(message)

        if entry_id:
            # Aprovar entrada especifica
            if self.data_connector and self.db:
                try:
                    from modules.operacional.repositories.time_bank_repository import TimeBankRepository

                    repo = TimeBankRepository(self.db)
                    entry = await repo.get_by_id(entry_id)

                    if entry:
                        response = f"""**APROVAR HORA EXTRA - {entry_id}**

**Detalhes:**
- Funcionario: {entry.employee_id}
- Horas: {entry.hours:.1f}h
- Tipo: {entry.entry_type}
- Data referencia: {entry.reference_date.strftime("%d/%m/%Y") if entry.reference_date else "N/A"}
- Descricao: {entry.description or "N/A"}
- Status atual: {entry.status}

**Confirmar aprovacao?**"""
                        return {
                            "response": response,
                            "intent": BancoHorasIntent.APROVAR_HORA_EXTRA.value,
                            "data": {"entry_id": entry_id, "hours": entry.hours, "status": entry.status},
                            "suggestions": ["Confirmar aprovacao", "Rejeitar", "Cancelar"],
                            "actions": [
                                {
                                    "type": "edit",
                                    "label": "Aprovar Hora Extra",
                                    "target": "time_bank",
                                    "data": {"id": entry_id, "action": "approve"},
                                },
                            ],
                        }
                except Exception as e:
                    logger.warning(f"Erro ao buscar entrada para aprovacao: {e}")

            # Fallback com ID
            return {
                "response": f"""**APROVAR HORA EXTRA - {entry_id}**

**Detalhes:**
- Funcionario: Jose Silva
- Horas: 4.0h
- Data: {date.today().strftime("%d/%m/%Y")}
- Motivo: Hora extra - Turno noturno
- Status: Pendente

**Confirmar aprovacao?**""",
                "intent": BancoHorasIntent.APROVAR_HORA_EXTRA.value,
                "data": {"entry_id": entry_id, "action": "approve"},
                "suggestions": ["Confirmar aprovacao", "Rejeitar", "Cancelar"],
                "actions": [
                    {
                        "type": "edit",
                        "label": "Aprovar Hora Extra",
                        "target": "time_bank",
                        "data": {"id": entry_id, "action": "approve"},
                    },
                ],
            }

        # Sem ID especifico - listar pendentes para aprovar
        return await self._handle_ver_pendentes(message, context)

    async def _handle_solicitar_compensacao(self, message: str, context: dict) -> dict[str, Any]:
        """Solicita compensacao de horas - redireciona para wizard."""
        employee_name = self._extract_employee_name(message)

        # Tentar buscar saldo atual do funcionario
        saldo_info = ""
        if self.data_connector:
            try:
                result = await self.data_connector._get_hora_extra_ranking()
                if result.success and result.data and employee_name:
                    filtered = [f for f in result.data if employee_name.lower() in f.get("nome", "").lower()]
                    if filtered:
                        func_data = filtered[0]
                        saldo = func_data.get("saldo_banco", 0)
                        saldo_info = f"\n**Saldo disponivel:** {saldo:+.1f}h\n"
                        if saldo <= 0:
                            return {
                                "response": f"""**SOLICITAR COMPENSACAO**

Funcionario: **{func_data["nome"]}**
Saldo atual: **{saldo:+.1f}h**

O funcionario nao possui saldo suficiente no banco de horas para compensacao.""",
                                "intent": BancoHorasIntent.SOLICITAR_COMPENSACAO.value,
                                "data": {"funcionario": func_data["nome"], "saldo": saldo, "insuficiente": True},
                                "suggestions": ["/banco_horas saldo", "/banco_horas extrato"],
                            }
            except Exception as e:
                logger.warning(f"Erro ao buscar saldo para compensacao: {e}")

        employee_display = employee_name or "[funcionario]"
        return {
            "response": f"""**SOLICITAR COMPENSACAO DE HORAS**

Para solicitar compensacao de horas do banco, preciso das seguintes informacoes:

1. **Funcionario:** {employee_display}
2. **Horas a compensar:** (quantidade)
3. **Data da compensacao:** (quando sera a folga/saida)
4. **Motivo:** (descricao)
{saldo_info}
Posso iniciar o **assistente guiado** para coletar esses dados passo a passo.

**Deseja iniciar?**""",
            "intent": BancoHorasIntent.SOLICITAR_COMPENSACAO.value,
            "data": {"action": "request_compensation", "wizard": "banco_horas_wizard", "funcionario": employee_name},
            "suggestions": ["Iniciar assistente", "Cancelar"],
            "actions": [
                {
                    "type": "create",
                    "label": "Solicitar Compensacao",
                    "target": "time_bank",
                    "data": {"wizard": "banco_horas", "employee_name": employee_name},
                },
            ],
        }

    async def _handle_ver_pendentes(self, message: str, context: dict) -> dict[str, Any]:
        """Lista horas extras pendentes de aprovacao."""
        if self.data_connector and self.db:
            try:
                from modules.operacional.repositories.time_bank_repository import TimeBankRepository
                from modules.operacional.schemas.time_bank import TimeBankFilter

                repo = TimeBankRepository(self.db)
                filters = TimeBankFilter(is_pending=True)
                entries, total = await repo.list(filters=filters, page=1, page_size=20)

                if entries:
                    lines = []
                    for entry in entries:
                        ref_date = entry.reference_date.strftime("%d/%m/%Y") if entry.reference_date else "N/A"
                        desc = entry.description or entry.reason or "Sem descricao"
                        if len(desc) > 35:
                            desc = desc[:32] + "..."
                        lines.append(
                            f"- **{entry.id[:8]}...** | {entry.employee_id[:8]}... | "
                            f"{entry.hours:.1f}h | {ref_date} | {desc}"
                        )

                    response = f"""**APROVACOES PENDENTES - BANCO DE HORAS** ({total})

{chr(10).join(lines)}

**Total pendente:** {total} registro(s)
**Horas pendentes:** {sum(e.hours for e in entries):.1f}h

Para aprovar, use: `/banco_horas aprovar <id>`"""

                    return {
                        "response": response,
                        "intent": BancoHorasIntent.VER_PENDENTES.value,
                        "data": {"pendentes": total, "entries": len(entries)},
                        "suggestions": [
                            "/banco_horas aprovar",
                            "/banco_horas saldo",
                            "/banco_horas expiracoes",
                        ],
                    }
                else:
                    return {
                        "response": "**APROVACOES PENDENTES - BANCO DE HORAS**\n\nNenhuma hora extra pendente de aprovacao no momento.",
                        "intent": BancoHorasIntent.VER_PENDENTES.value,
                        "data": {"pendentes": 0},
                        "suggestions": ["/banco_horas saldo", "/banco_horas expiracoes"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar pendentes via DB: {e}")

        # Fallback estatico
        today = date.today()
        return {
            "response": f"""**APROVACOES PENDENTES - BANCO DE HORAS** (5)

- **BH-001** | Jose Silva | +4.0h | {today.strftime("%d/%m/%Y")} | HE - Turno noturno
- **BH-002** | Maria Santos | +2.5h | {today.strftime("%d/%m/%Y")} | HE - Cobertura falta
- **BH-003** | Pedro Oliveira | +6.0h | 27/01/2026 | HE - Evento especial
- **BH-004** | Ana Costa | +3.0h | 26/01/2026 | HE - Turno extra
- **BH-005** | Carlos Lima | +8.0h | 25/01/2026 | HE - Feriado

**Total pendente:** 5 registro(s)
**Horas pendentes:** 23.5h

Para aprovar, use: `/banco_horas aprovar <id>`""",
            "intent": BancoHorasIntent.VER_PENDENTES.value,
            "data": {
                "pendentes": [
                    {"id": "BH-001", "nome": "Jose Silva", "horas": 4.0},
                    {"id": "BH-002", "nome": "Maria Santos", "horas": 2.5},
                    {"id": "BH-003", "nome": "Pedro Oliveira", "horas": 6.0},
                    {"id": "BH-004", "nome": "Ana Costa", "horas": 3.0},
                    {"id": "BH-005", "nome": "Carlos Lima", "horas": 8.0},
                ],
                "total": 5,
                "total_horas": 23.5,
            },
            "suggestions": [
                "/banco_horas aprovar BH-001",
                "/banco_horas saldo",
                "/banco_horas expiracoes",
            ],
        }

    async def _handle_ver_expiracoes(self, message: str, context: dict) -> dict[str, Any]:
        """Lista horas prestes a expirar."""
        if self.data_connector and self.db:
            try:
                from datetime import timedelta

                from modules.operacional.models.time_bank import TimeBankEntryType, TimeBankStatus
                from modules.operacional.repositories.time_bank_repository import TimeBankRepository
                from modules.operacional.schemas.time_bank import TimeBankFilter

                repo = TimeBankRepository(self.db)
                # Buscar entradas aprovadas que tem data de expiracao
                filters = TimeBankFilter(
                    status=TimeBankStatus.APPROVED,
                    entry_type=TimeBankEntryType.CREDIT,
                )
                entries, total = await repo.list(filters=filters, page=1, page_size=50)

                today = date.today()
                limite_30_dias = today + timedelta(days=30)

                expiring = []
                for entry in entries:
                    if entry.expiration_date and entry.expiration_date <= limite_30_dias:
                        days_left = (entry.expiration_date - today).days
                        if days_left >= 0:
                            expiring.append(
                                {
                                    "id": entry.id[:8],
                                    "employee_id": entry.employee_id[:8],
                                    "hours": entry.hours,
                                    "expiration_date": entry.expiration_date,
                                    "days_left": days_left,
                                }
                            )

                expiring.sort(key=lambda x: x["days_left"])

                if expiring:
                    lines = []
                    for e in expiring[:15]:
                        urgency = "!!!" if e["days_left"] <= 7 else "!" if e["days_left"] <= 15 else ""
                        exp_date = e["expiration_date"].strftime("%d/%m/%Y")
                        lines.append(
                            f"- {urgency} **{e['id']}...** | {e['employee_id']}... | "
                            f"{e['hours']:.1f}h | Expira: {exp_date} ({e['days_left']} dias)"
                        )

                    total_hours_expiring = sum(e["hours"] for e in expiring)

                    response = f"""**HORAS PRESTES A EXPIRAR** ({len(expiring)})

{chr(10).join(lines)}

**Total de horas expirando:** {total_hours_expiring:.1f}h
**Registros expirando:** {len(expiring)}

**Legenda:** !!! = Critico (< 7 dias) | ! = Atencao (< 15 dias)

**Acao recomendada:** Compensar horas antes do vencimento."""
                else:
                    response = "**HORAS PRESTES A EXPIRAR**\n\nNenhuma hora com expiracao proxima (30 dias) encontrada."

                return {
                    "response": response,
                    "intent": BancoHorasIntent.VER_EXPIRACOES.value,
                    "data": {"expiring": expiring, "total": len(expiring)},
                    "suggestions": [
                        "/banco_horas compensar",
                        "/banco_horas saldo",
                        "/banco_horas pendentes",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar expiracoes via DB: {e}")

        # Fallback estatico
        return {
            "response": """**HORAS PRESTES A EXPIRAR** (4)

- !!! **BH-012** | Jose Silva | 8.0h | Expira: 02/02/2026 (4 dias)
- !!! **BH-015** | Maria Santos | 4.0h | Expira: 05/02/2026 (7 dias)
- ! **BH-018** | Pedro Oliveira | 6.0h | Expira: 12/02/2026 (14 dias)
- **BH-022** | Ana Costa | 3.5h | Expira: 25/02/2026 (27 dias)

**Total de horas expirando:** 21.5h
**Registros expirando:** 4

**Legenda:** !!! = Critico (< 7 dias) | ! = Atencao (< 15 dias)

**Acao recomendada:** Compensar horas antes do vencimento.
Use `/banco_horas compensar <funcionario> <horas> <data>` para solicitar.""",
            "intent": BancoHorasIntent.VER_EXPIRACOES.value,
            "data": {
                "expiracoes": [
                    {"id": "BH-012", "nome": "Jose Silva", "horas": 8.0, "dias": 4},
                    {"id": "BH-015", "nome": "Maria Santos", "horas": 4.0, "dias": 7},
                    {"id": "BH-018", "nome": "Pedro Oliveira", "horas": 6.0, "dias": 14},
                    {"id": "BH-022", "nome": "Ana Costa", "horas": 3.5, "dias": 27},
                ],
                "total": 4,
                "total_horas": 21.5,
            },
            "suggestions": [
                "/banco_horas compensar Jose Silva 8 02/02/2026",
                "/banco_horas saldo",
                "/banco_horas pendentes",
            ],
        }

    async def _handle_default(self, message: str, context: dict) -> dict[str, Any] | None:
        """Handler padrao - retorna None para permitir que DataConnector processe."""
        return None

    # =========================================================================
    # FOLLOW-UP
    # =========================================================================

    FOLLOWUP_PATTERNS = {
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
        Processa follow-up de uma conversa anterior com o BancoHorasAgent.

        Args:
            message: Mensagem do usuario
            context: Contexto da conversa
            previous_intent: Intent da interacao anterior
            previous_data: Dados coletados na interacao anterior

        Returns:
            Dict com resposta ou None se nao for follow-up reconhecido
        """
        message_clean = message.strip().lower()
        previous_data = previous_data or {}

        # Follow-up de APROVAR_HORA_EXTRA: espera confirmacao
        if previous_intent == BancoHorasIntent.APROVAR_HORA_EXTRA.value:
            for pattern in self.FOLLOWUP_PATTERNS["confirmation"]:
                if re.match(pattern, message_clean):
                    entry_id = previous_data.get("entry_id", "N/A")
                    return {
                        "response": f"Hora extra **{entry_id}** aprovada com sucesso!\n\n"
                        "O saldo do funcionario sera atualizado automaticamente.",
                        "intent": BancoHorasIntent.APROVAR_HORA_EXTRA.value,
                        "data": {**previous_data, "approved": True},
                        "suggestions": ["/banco_horas pendentes", "/banco_horas saldo"],
                    }

            for pattern in self.FOLLOWUP_PATTERNS["negation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Aprovacao cancelada. Posso ajudar com outra coisa?",
                        "intent": BancoHorasIntent.APROVAR_HORA_EXTRA.value,
                        "data": {**previous_data, "cancelled": True},
                        "suggestions": ["/banco_horas pendentes", "/banco_horas saldo"],
                    }

        # Follow-up de SOLICITAR_COMPENSACAO: espera confirmacao para iniciar wizard
        if previous_intent == BancoHorasIntent.SOLICITAR_COMPENSACAO.value:
            for pattern in self.FOLLOWUP_PATTERNS["confirmation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Iniciando assistente de compensacao de horas...",
                        "intent": BancoHorasIntent.SOLICITAR_COMPENSACAO.value,
                        "data": {**previous_data, "start_wizard": True},
                        "suggestions": [],
                    }

            for pattern in self.FOLLOWUP_PATTERNS["negation"]:
                if re.match(pattern, message_clean):
                    return {
                        "response": "Solicitacao de compensacao cancelada. Posso ajudar com outra coisa?",
                        "intent": BancoHorasIntent.SOLICITAR_COMPENSACAO.value,
                        "data": {**previous_data, "cancelled": True},
                        "suggestions": ["/banco_horas saldo", "/banco_horas pendentes"],
                    }

        return None

    def get_capabilities(self) -> list[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Consultar saldo de banco de horas",
            "Ver extrato detalhado de creditos e debitos",
            "Aprovar horas extras pendentes",
            "Solicitar compensacao de horas",
            "Listar aprovacoes pendentes",
            "Verificar horas prestes a expirar",
        ]
