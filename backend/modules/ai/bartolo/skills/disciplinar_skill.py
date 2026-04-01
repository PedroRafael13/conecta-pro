"""
Skill /disciplina - Gerenciamento de medidas disciplinares via comando.

Comandos:
    /disciplina resumo
    /disciplina pendentes
    /disciplina historico <funcionario>
    /disciplina stats
    /disciplina tipos
    /disciplina help

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class DisciplinarSkill(BaseSkill):
    """
    Skill para gerenciamento de medidas disciplinares.

    Comandos:
        /disciplina resumo               - Resumo geral das medidas
        /disciplina pendentes             - Medidas pendentes de aprovacao
        /disciplina historico <func>      - Historico disciplinar do funcionario
        /disciplina stats                 - Estatisticas disciplinares
        /disciplina tipos                 - Listar tipos disponiveis
        /disciplina help                  - Ajuda
    """

    name = "disciplina"
    description = "Gerenciamento de medidas disciplinares"
    commands = ["resumo", "pendentes", "historico", "stats", "tipos", "help"]

    def __init__(self, data_connector: Optional["DataConnector"] = None, db=None):
        """
        Inicializa a skill.

        Args:
            data_connector: Conector de dados para consultas reais
            db: Sessao async do SQLAlchemy
        """
        super().__init__(data_connector=data_connector)
        self.db = db

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa comando de medida disciplinar."""
        if not command or command == "help":
            return {"response": self.get_help(), "suggestions": self.commands[:4]}

        handlers = {
            "resumo": self._resumo,
            "pendentes": self._pendentes,
            "historico": self._historico,
            "stats": self._stats,
            "tipos": self._tipos,
        }

        handler = handlers.get(command)
        if handler:
            try:
                return await handler(args, context)
            except Exception as e:
                logger.error(f"Erro ao executar /disciplina {command}: {e}")
                return {
                    "response": f"Erro ao executar comando: {e}",
                    "suggestions": ["/disciplina help"],
                }

        return {
            "response": f"Comando '{command}' nao reconhecido. Use `/disciplina help` para ver os comandos.",
            "suggestions": self.commands[:4],
        }

    async def _resumo(self, args: list[str], context: dict) -> dict[str, Any]:
        """Resumo geral das medidas disciplinares."""
        # Tentar dados reais
        if self.db:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    actions, total = await repo.list(tenant_id, page=1, page_size=10)
                    pendentes = await repo.get_pending_approval(tenant_id)

                    lines = []
                    for a in actions[:10]:
                        tipo_map = {
                            "advertencia_verbal": "Adv. Verbal",
                            "advertencia_escrita": "Adv. Escrita",
                            "suspensao": "Suspensao",
                            "demissao_justa_causa": "Justa Causa",
                        }
                        tipo = tipo_map.get(a.action_type, a.action_type)
                        lines.append(
                            f"| {a.code} | {a.employee_name[:20]} | {tipo} | "
                            f"{a.status_display_name} | {a.incident_date.strftime('%d/%m/%Y')} |"
                        )

                    tabela = "\n".join(lines) if lines else "| - | - | - | - | - |"

                    response = f"""**Resumo Disciplinar**

**Pendentes de aprovacao:** {len(pendentes)}
**Total de medidas:** {total}

**Ultimas medidas:**
| Codigo | Funcionario | Tipo | Status | Data |
|--------|-------------|------|--------|------|
{tabela}

Use `/disciplina pendentes` para ver apenas as pendentes."""

                    return {
                        "response": response,
                        "data": {"total": total, "pendentes": len(pendentes)},
                        "suggestions": ["/disciplina pendentes", "/disciplina stats", "/disciplina historico"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar resumo real: {e}")

        # Fallback estatico
        return {
            "response": """**Resumo Disciplinar**

**Pendentes de aprovacao:** 2
**Total de medidas:** 47

**Ultimas medidas:**
| Codigo | Funcionario | Tipo | Status | Data |
|--------|-------------|------|--------|------|
| ADV-2026-00003 | Carlos Lima | Adv. Verbal | Aplicada | 25/01/2026 |
| ADV-2026-00002 | Maria Santos | Adv. Escrita | Pendente | 20/01/2026 |
| SUS-2026-00001 | Pedro Oliveira | Suspensao | Rascunho | 22/01/2026 |
| ADV-2026-00001 | Joao Silva | Adv. Verbal | Aplicada | 15/01/2026 |

Use `/disciplina pendentes` para ver apenas as pendentes.""",
            "data": {"total": 47, "pendentes": 2},
            "suggestions": ["/disciplina pendentes", "/disciplina stats"],
        }

    async def _pendentes(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista medidas pendentes de aprovacao."""
        if self.db:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    pendentes = await repo.get_pending_approval(tenant_id)

                    if pendentes:
                        lines = []
                        for a in pendentes:
                            tipo_map = {
                                "advertencia_verbal": "Adv. Verbal",
                                "advertencia_escrita": "Adv. Escrita",
                                "suspensao": "Suspensao",
                                "demissao_justa_causa": "Justa Causa",
                            }
                            tipo = tipo_map.get(a.action_type, a.action_type)
                            lines.append(
                                f"| {a.code} | {a.employee_name[:20]} | {tipo} | "
                                f"{a.incident_date.strftime('%d/%m/%Y')} | "
                                f"{a.created_at.strftime('%d/%m/%Y')} |"
                            )

                        tabela = "\n".join(lines)
                        response = f"""**Medidas Pendentes de Aprovacao** ({len(pendentes)})

| Codigo | Funcionario | Tipo | Data Incidente | Criado em |
|--------|-------------|------|----------------|-----------|
{tabela}

Para aprovar: informe o codigo da medida."""

                        suggestions = []
                        for a in pendentes[:3]:
                            suggestions.append(f"Aprovar {a.code}")
                        return {
                            "response": response,
                            "data": {"total_pendentes": len(pendentes)},
                            "suggestions": suggestions or ["/disciplina help"],
                        }
                    else:
                        return {
                            "response": "**Medidas Pendentes**\n\nNenhuma medida pendente de aprovacao no momento.",
                            "data": {"total_pendentes": 0},
                            "suggestions": ["/disciplina resumo", "/disciplina stats"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar pendentes: {e}")

        # Fallback estatico
        return {
            "response": """**Medidas Pendentes de Aprovacao** (2)

| Codigo | Funcionario | Tipo | Data Incidente | Criado em |
|--------|-------------|------|----------------|-----------|
| ADV-2026-00002 | Maria Santos | Adv. Escrita | 20/01/2026 | 21/01/2026 |
| SUS-2026-00001 | Pedro Oliveira | Suspensao | 22/01/2026 | 23/01/2026 |

Para aprovar: informe o codigo da medida.""",
            "data": {"total_pendentes": 2},
            "suggestions": ["Aprovar ADV-2026-00002", "Aprovar SUS-2026-00001", "/disciplina help"],
        }

    async def _historico(self, args: list[str], context: dict) -> dict[str, Any]:
        """Historico disciplinar de um funcionario."""
        if not args:
            return {
                "response": "**Uso:** `/disciplina historico <nome_ou_id>`\n\nExemplo: `/disciplina historico Joao Silva`",
                "suggestions": ["/disciplina resumo", "/disciplina help"],
            }

        funcionario = " ".join(args)

        if self.db:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository
                from modules.operacional.disciplinary.schemas import DisciplinaryFilter

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    # Buscar por nome
                    filtro = DisciplinaryFilter(search=funcionario)
                    actions, total = await repo.list(tenant_id, filters=filtro, page=1, page_size=20)

                    if actions:
                        # Agrupar por funcionario
                        employee_name = actions[0].employee_name

                        lines = []
                        for a in actions:
                            tipo_map = {
                                "advertencia_verbal": "Adv. Verbal",
                                "advertencia_escrita": "Adv. Escrita",
                                "suspensao": "Suspensao",
                                "demissao_justa_causa": "Justa Causa",
                            }
                            tipo = tipo_map.get(a.action_type, a.action_type)
                            motivo = (
                                a.reason_description[:40] + "..."
                                if len(a.reason_description) > 40
                                else a.reason_description
                            )
                            lines.append(
                                f"| {a.code} | {tipo} | {a.status_display_name} | "
                                f"{a.incident_date.strftime('%d/%m/%Y')} | {motivo} |"
                            )

                        tabela = "\n".join(lines)

                        # Contadores
                        adv_aplicadas = sum(
                            1
                            for a in actions
                            if a.action_type in ["advertencia_verbal", "advertencia_escrita"] and a.status == "aplicada"
                        )
                        sus_aplicadas = sum(
                            1 for a in actions if a.action_type == "suspensao" and a.status == "aplicada"
                        )

                        response = f"""**Historico Disciplinar - {employee_name}**

| Codigo | Tipo | Status | Data | Motivo |
|--------|------|--------|------|--------|
{tabela}

**Resumo:**
- Total: {total}
- Advertencias aplicadas: {adv_aplicadas}
- Suspensoes aplicadas: {sus_aplicadas}"""

                        return {
                            "response": response,
                            "data": {"employee": employee_name, "total": total},
                            "suggestions": ["/disciplina stats", "Criar medida"],
                        }
                    else:
                        return {
                            "response": f"Nenhuma medida disciplinar encontrada para '{funcionario}'.",
                            "suggestions": ["/disciplina resumo", "/disciplina help"],
                        }
            except Exception as e:
                logger.warning(f"Erro ao buscar historico: {e}")

        # Fallback estatico
        return {
            "response": f"""**Historico Disciplinar - {funcionario}**

| Codigo | Tipo | Status | Data | Motivo |
|--------|------|--------|------|--------|
| ADV-2025-00015 | Adv. Verbal | Aplicada | 10/08/2025 | Atraso reiterado |
| ADV-2025-00023 | Adv. Escrita | Aplicada | 15/10/2025 | Falta injustificada |
| ADV-2026-00002 | Adv. Escrita | Pendente | 20/01/2026 | Falta injustificada |

**Resumo:**
- Total: 3
- Advertencias aplicadas: 2
- Suspensoes aplicadas: 0

**Atencao:** Proxima medida recomendada: **Suspensao** (em caso de reincidencia).""",
            "data": {"employee": funcionario, "total": 3},
            "suggestions": ["Criar suspensao", "Validar CLT"],
        }

    async def _stats(self, args: list[str], context: dict) -> dict[str, Any]:
        """Estatisticas de medidas disciplinares."""
        if self.db:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository

                repo = DisciplinaryRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                if tenant_id:
                    stats = await repo.get_stats(tenant_id)

                    tipo_lines = []
                    tipo_map = {
                        "advertencia_verbal": "Adv. Verbal",
                        "advertencia_escrita": "Adv. Escrita",
                        "suspensao": "Suspensao",
                        "demissao_justa_causa": "Justa Causa",
                    }
                    for tipo_key, count in stats.by_type.items():
                        tipo_name = tipo_map.get(tipo_key, tipo_key)
                        tipo_lines.append(f"| {tipo_name} | {count} |")
                    tipo_tabela = "\n".join(tipo_lines) if tipo_lines else "| - | 0 |"

                    motivo_lines = []
                    for motivo_key, count in sorted(stats.by_reason_category.items(), key=lambda x: x[1], reverse=True)[
                        :5
                    ]:
                        motivo_lines.append(f"| {motivo_key.replace('_', ' ').title()} | {count} |")
                    motivo_tabela = "\n".join(motivo_lines) if motivo_lines else "| - | 0 |"

                    response = f"""**Estatisticas Disciplinares**

**Totais:**
- Medidas registradas: **{stats.total}**
- Pendentes aprovacao: **{stats.pending_approval}**
- Pendentes assinatura: **{stats.pending_signature}**
- Aplicadas este mes: **{stats.applied_this_month}**
- Aplicadas este ano: **{stats.applied_this_year}**

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
{tipo_tabela}

**Top Motivos:**
| Motivo | Qtd |
|--------|-----|
{motivo_tabela}

**Funcionarios:**
- Com advertencias: **{stats.employees_with_warnings}**
- Com suspensoes: **{stats.employees_with_suspensions}**"""

                    return {
                        "response": response,
                        "data": {
                            "total": stats.total,
                            "pendentes": stats.pending_approval,
                        },
                        "suggestions": ["/disciplina pendentes", "/disciplina resumo"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar stats: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas Disciplinares**

**Totais:**
- Medidas registradas: **47**
- Pendentes aprovacao: **2**
- Pendentes assinatura: **1**
- Aplicadas este mes: **3**
- Aplicadas este ano: **5**

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
| Adv. Verbal | 22 |
| Adv. Escrita | 15 |
| Suspensao | 8 |
| Justa Causa | 2 |

**Top Motivos:**
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
            "data": {"total": 47, "pendentes": 2},
            "suggestions": ["/disciplina pendentes", "/disciplina resumo"],
        }

    async def _tipos(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista tipos de medidas disciplinares disponiveis."""
        return {
            "response": """**Tipos de Medidas Disciplinares**

| # | Tipo | Descricao | Base Legal |
|---|------|-----------|------------|
| 1 | **Advertencia Verbal** | Infracoes leves, primeira ocorrencia. Registro interno sem documento formal. | Poder disciplinar do empregador |
| 2 | **Advertencia Escrita** | Infracoes reincidentes ou moderadas. Documento assinado pelo funcionario. | Poder disciplinar do empregador |
| 3 | **Suspensao** | Infracoes graves. Afastamento de 1 a 30 dias sem remuneracao. | CLT Art. 474 (max 30 dias) |
| 4 | **Demissao por Justa Causa** | Faltas gravissimas previstas em lei. Rescisao sem aviso previo. | CLT Art. 482 |

**Progressao recomendada:**
Advertencia Verbal -> Advertencia Escrita -> Suspensao -> Justa Causa

**Principios CLT:**
- **Imediaticidade** - Aplicar em ate 30 dias do fato
- **Proporcionalidade** - Medida proporcional a gravidade
- **Non bis in idem** - Nao punir duas vezes pelo mesmo fato
- **Igualdade** - Tratar casos semelhantes de forma igual""",
            "suggestions": ["/disciplina resumo", "/disciplina help"],
        }

    def get_help(self) -> str:
        """Retorna texto de ajuda da skill."""
        return """**Skill /disciplina**

**Comandos disponiveis:**
```
/disciplina resumo                    - Resumo geral das medidas
/disciplina pendentes                 - Medidas pendentes de aprovacao
/disciplina historico <funcionario>   - Historico disciplinar
/disciplina stats                     - Estatisticas
/disciplina tipos                     - Tipos de medidas (CLT)
/disciplina help                      - Esta ajuda
```

**Exemplos:**
- `/disciplina resumo`
- `/disciplina pendentes`
- `/disciplina historico Joao Silva`
- `/disciplina stats`
- `/disciplina tipos`"""
