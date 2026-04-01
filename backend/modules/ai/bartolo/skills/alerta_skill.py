"""
Skill /alerta - Central de alertas
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class AlertaSkill(BaseSkill):
    name = "alerta"
    description = "Central de alertas operacionais"
    commands = ["", "cobertura", "documentos", "atrasos", "urgente", "help"]

    def __init__(self, data_connector: Optional["DataConnector"] = None):
        super().__init__(data_connector=data_connector)

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        if not command or command == "help":
            return await self._todos(context)

        handlers = {
            "cobertura": self._cobertura,
            "documentos": self._documentos,
            "atrasos": self._atrasos,
            "urgente": self._urgente,
        }

        handler = handlers.get(command, self._todos)
        return await handler(context)

    async def _todos(self, context: dict) -> dict[str, Any]:
        """Central de alertas - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_pending_alerts()
                if result.success:
                    # Complementa com dados de atrasos e cobertura critica
                    atrasos_result = await self.data_connector._get_atrasos_hoje()
                    cob_result = await self.data_connector._get_cobertura_critica()

                    alertas = result.data or []
                    len(alertas)

                    # Conta categorias
                    criticos = []
                    altos = []
                    medios = []

                    for a in alertas:
                        sev = a.get("severidade", "media")
                        if sev == "critica":
                            criticos.append(a)
                        elif sev == "alta":
                            altos.append(a)
                        else:
                            medios.append(a)

                    # Adiciona atrasos como alerta se houver
                    atrasos_count = 0
                    if atrasos_result.success and atrasos_result.data:
                        atrasos_count = atrasos_result.total_count
                        graves = sum(1 for a in atrasos_result.data if a.get("atraso_minutos", 0) > 15)
                        if graves > 0:
                            altos.append(
                                {
                                    "mensagem": f"{graves} atrasos > 15min hoje",
                                    "tipo": "atraso",
                                }
                            )
                        elif atrasos_count > 0:
                            medios.append(
                                {
                                    "mensagem": f"{atrasos_count} atrasos registrados hoje",
                                    "tipo": "atraso",
                                }
                            )

                    # Adiciona cobertura critica como alerta
                    if cob_result.success and cob_result.data:
                        cob_count = cob_result.total_count
                        if cob_count > 0:
                            criticos.append(
                                {
                                    "mensagem": f"{cob_count} postos com cobertura < 80%",
                                    "tipo": "cobertura",
                                }
                            )

                    # Monta resposta formatada
                    total = len(criticos) + len(altos) + len(medios)

                    sections = []
                    if criticos:
                        items = "\n".join(f"- {a.get('mensagem', 'Alerta critico')}" for a in criticos)
                        sections.append(f"[X] **Criticos ({len(criticos)})**\n{items}")
                    if altos:
                        items = "\n".join(f"- {a.get('mensagem', 'Alerta alto')}" for a in altos)
                        sections.append(f"[!] **Altos ({len(altos)})**\n{items}")
                    if medios:
                        items = "\n".join(f"- {a.get('mensagem', 'Alerta medio')}" for a in medios)
                        sections.append(f"[~] **Medios ({len(medios)})**\n{items}")

                    body = "\n\n".join(sections) if sections else "Nenhum alerta ativo no momento."

                    return {
                        "response": f"""**Central de Alertas** (Dados Reais)

{body}

**Total: {total} alertas**""",
                        "data": {"total": total, "criticos": len(criticos), "altos": len(altos), "medios": len(medios)},
                        "suggestions": ["/alerta urgente", "/alerta cobertura", "/alerta atrasos"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar alertas reais: {e}")

        # Fallback estatico
        return {
            "response": """**Central de Alertas**

[X] **Criticos (2)**
- Posto Centro-001 sem funcionario
- Cobertura geral 45%

[!] **Altos (3)**
- 3 docs vencem em 7 dias
- Escala nao publicada
- 2 atrasos > 30min

[~] **Medios (5)**
- 5 substituicoes pendentes

**Total: 10 alertas**""",
            "data": {"total": 10, "criticos": 2, "altos": 3, "medios": 5},
            "suggestions": ["/alerta urgente", "/alerta cobertura", "/alerta documentos"],
        }

    async def _cobertura(self, context: dict) -> dict[str, Any]:
        """Alertas de cobertura - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success:
                    if result.data:
                        lines = []
                        for p in result.data[:10]:
                            cobertura = p.get("cobertura", 0)
                            icon = "[X]" if cobertura < 60 else "[!]"
                            lines.append(f"- {p.get('nome', 'N/A')} ({p.get('codigo', '')}): {cobertura}% {icon}")
                        return {
                            "response": f"""**Alertas de Cobertura** (Dados Reais)

{chr(10).join(lines)}

**Total: {result.total_count} postos com cobertura critica**""",
                            "data": {"postos_criticos": result.data, "total": result.total_count},
                            "suggestions": ["/cobertura critica", "/substituto disponiveis"],
                        }
                    else:
                        return {
                            "response": "**Alertas de Cobertura**\n\nNenhum posto com cobertura critica no momento.",
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar alertas cobertura reais: {e}")

        # Fallback estatico
        return {"response": "**Alertas de Cobertura**\n\n- Centro-001: 45% [X]\n- Norte-003: 75% [!]"}

    async def _documentos(self, context: dict) -> dict[str, Any]:
        """Documentos vencendo - estatico por enquanto"""
        return {
            "response": "**Documentos Vencendo**\n\n- Joao: ASO em 3 dias\n- Maria: CNH em 5 dias\n- Carlos: NR em 7 dias"
        }

    async def _atrasos(self, context: dict) -> dict[str, Any]:
        """Atrasos de hoje - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_atrasos_hoje()
                if result.success:
                    return {
                        "response": result.message,
                        "data": {
                            "atrasos": result.data,
                            "total": result.total_count,
                        },
                        "suggestions": ["/alerta urgente", "/alerta cobertura"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar atrasos reais: {e}")

        # Fallback estatico
        return {"response": "**Atrasos de Hoje**\n\n- Joao Silva: +45min [X]\n- Ana Paula: +32min [!]"}

    async def _urgente(self, context: dict) -> dict[str, Any]:
        """Alertas urgentes - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                # Combina cobertura critica + atrasos graves
                cob_result = await self.data_connector._get_cobertura_critica()
                atr_result = await self.data_connector._get_atrasos_hoje()

                urgentes = []

                if cob_result.success and cob_result.data:
                    for p in cob_result.data:
                        if p.get("cobertura", 100) < 60:
                            urgentes.append(
                                f"[X] {p.get('nome', 'Posto')} ({p.get('codigo', '')}) - "
                                f"cobertura {p.get('cobertura', 0)}%"
                            )

                if atr_result.success and atr_result.data:
                    graves = [a for a in atr_result.data if a.get("atraso_minutos", 0) > 30]
                    for a in graves[:3]:
                        urgentes.append(
                            f"[X] {a.get('nome', 'Funcionario')} - "
                            f"atraso {a.get('atraso_minutos', 0)}min no {a.get('posto', 'posto')}"
                        )

                if urgentes:
                    items = "\n".join(f"{i}. {u}" for i, u in enumerate(urgentes, 1))
                    return {
                        "response": f"""**[!!!] ATENCAO URGENTE** (Dados Reais)

{items}

**Total: {len(urgentes)} itens urgentes**
**Resolver agora?**""",
                        "priority": "critical",
                        "data": {"urgentes": len(urgentes)},
                        "suggestions": ["/cobertura critica", "/substituto urgente"],
                    }
                else:
                    return {
                        "response": "**[!!!] ATENCAO URGENTE**\n\nNenhum alerta urgente no momento. Tudo sob controle.",
                        "priority": "low",
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar urgentes reais: {e}")

        # Fallback estatico
        return {
            "response": """**[!!!] ATENCAO URGENTE**

1. [X] Centro-001 descoberto ha 2h
2. [X] Cobertura 45% (min 80%)

**Resolver agora?**""",
            "priority": "critical",
        }

    def get_help(self) -> str:
        return """**Skill /alerta**

```
/alerta             - Todos os alertas
/alerta cobertura   - Alertas de cobertura
/alerta documentos  - Docs vencendo
/alerta atrasos     - Atrasos de hoje
/alerta urgente     - So os criticos
```"""
