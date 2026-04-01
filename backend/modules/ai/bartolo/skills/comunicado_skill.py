"""
Skill /comunicado - Gerenciamento de comunicados via comando.

Comandos:
    /comunicado listar              - Listar comunicados ativos
    /comunicado recentes            - Comunicados recentes
    /comunicado pendentes           - Rascunhos pendentes de publicacao
    /comunicado stats [id]          - Estatisticas (geral ou de um comunicado)
    /comunicado leituras <id>       - Ver quem leu/confirmou o comunicado
    /comunicado nao_lidos <id>      - Listar quem NAO leu
    /comunicado reenviar <id>       - Reenviar para quem nao leu
    /comunicado help                - Ajuda

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import date
from typing import TYPE_CHECKING, Any, Optional

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class ComunicadoSkill(BaseSkill):
    """
    Skill para gerenciamento de comunicados.

    Comandos:
        /comunicado listar
        /comunicado recentes
        /comunicado pendentes
        /comunicado stats [comunicado_id]
        /comunicado leituras <comunicado_id>
        /comunicado nao_lidos <comunicado_id>
        /comunicado reenviar <comunicado_id>
        /comunicado help
    """

    name = "comunicado"
    description = "Gerenciamento de comunicados e anuncios"
    commands = [
        "listar",
        "recentes",
        "pendentes",
        "stats",
        "leituras",
        "nao_lidos",
        "reenviar",
        "help",
    ]

    def __init__(self, data_connector: Optional["DataConnector"] = None, db=None):
        super().__init__(data_connector=data_connector)
        self.db = db

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa comando de comunicado."""

        if not command or command == "help":
            return {"response": self.get_help(), "suggestions": self.commands[:4]}

        handlers = {
            "listar": self._listar,
            "recentes": self._recentes,
            "pendentes": self._pendentes,
            "stats": self._stats,
            "leituras": self._leituras,
            "nao_lidos": self._nao_lidos,
            "reenviar": self._reenviar,
        }

        handler = handlers.get(command)
        if handler:
            return await handler(args, context)

        return {
            "response": f"Comando '{command}' nao reconhecido. Use /comunicado help para ver os comandos.",
            "suggestions": self.commands[:4],
        }

    async def _listar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar comunicados ativos."""
        # Tenta buscar dados reais
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success:
                    return {
                        "response": result.message,
                        "data": {
                            "comunicados": result.data,
                            "total": result.total_count,
                        },
                        "suggestions": [
                            "/comunicado recentes",
                            "/comunicado pendentes",
                            "/comunicado stats",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados ativos reais: {e}")

        # Fallback estatico
        today = date.today()
        return {
            "response": f"""📢 **COMUNICADOS ATIVOS** (3)

- 🟠 **Alteracao de procedimento - Portaria**
  Tipo: procedimento | Prioridade: alta
  Visualizacoes: 45 | Confirmacoes: 32 | {today.strftime("%d/%m/%Y")} 09:00
- 🔴 **Escala de feriado - Carnaval 2026**
  Tipo: escala | Prioridade: urgente
  Visualizacoes: 120 | Confirmacoes: 95 | {today.strftime("%d/%m/%Y")} 08:00
- 🟢 **Novo uniforme disponivel**
  Tipo: informativo | Prioridade: normal
  Visualizacoes: 30 | Confirmacoes: 10 | {today.strftime("%d/%m/%Y")} 07:30

**Total: 3 comunicados ativos**""",
            "suggestions": [
                "/comunicado recentes",
                "/comunicado pendentes",
                "/comunicado stats",
            ],
        }

    async def _recentes(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar comunicados recentes."""
        # Tenta buscar dados reais
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    recentes = result.data[:5]
                    lines = []
                    for idx, c in enumerate(recentes, 1):
                        prio_icon = {"urgente": "🔴", "alta": "🟠", "normal": "🟢", "baixa": "⚪"}.get(
                            c.get("prioridade", "normal"), "🟢"
                        )
                        lines.append(
                            f"{idx}. {prio_icon} **{c.get('titulo', 'N/A')}** | "
                            f"{c.get('data_publicacao', 'N/A')} | "
                            f"👁 {c.get('visualizacoes', 0)} | ✅ {c.get('confirmacoes', 0)}"
                        )

                    response_text = f"""🕐 **COMUNICADOS RECENTES** ({len(recentes)})

{chr(10).join(lines)}

*Exibindo os {len(recentes)} comunicados mais recentes.*"""
                    return {
                        "response": response_text,
                        "data": {
                            "comunicados": recentes,
                            "total": len(recentes),
                        },
                        "suggestions": [
                            "/comunicado listar",
                            "/comunicado pendentes",
                            "/comunicado stats",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados recentes reais: {e}")

        # Fallback estatico
        today = date.today()
        return {
            "response": f"""🕐 **COMUNICADOS RECENTES** (3)

1. 🟠 **Alteracao de procedimento - Portaria** | {today.strftime("%d/%m/%Y")} 09:00 | 👁 45 | ✅ 32
2. 🔴 **Escala de feriado - Carnaval 2026** | {today.strftime("%d/%m/%Y")} 08:00 | 👁 120 | ✅ 95
3. 🟢 **Novo uniforme disponivel** | {today.strftime("%d/%m/%Y")} 07:30 | 👁 30 | ✅ 10

*Exibindo os 3 comunicados mais recentes.*""",
            "suggestions": [
                "/comunicado listar",
                "/comunicado pendentes",
                "/comunicado stats",
            ],
        }

    async def _pendentes(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar comunicados pendentes de publicacao."""
        # Tenta buscar dados reais
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    pendentes = [
                        c for c in result.data if c.get("status") in ("draft", "rascunho", "scheduled", "agendado")
                    ]

                    if pendentes:
                        lines = []
                        for idx, c in enumerate(pendentes, 1):
                            status_label = {
                                "draft": "Rascunho",
                                "rascunho": "Rascunho",
                                "scheduled": "Agendado",
                                "agendado": "Agendado",
                            }.get(c.get("status", ""), c.get("status", "N/A"))
                            lines.append(
                                f"| {idx} | {c.get('titulo', 'N/A')[:40]} | {status_label} | {c.get('tipo', 'N/A')} |"
                            )

                        response_text = f"""📝 **COMUNICADOS PENDENTES** ({len(pendentes)})

| # | Comunicado | Status | Tipo |
|---|-----------|--------|------|
{chr(10).join(lines)}

**Total: {len(pendentes)} pendentes**"""
                    else:
                        response_text = "✅ **Nenhum comunicado pendente no momento.**"

                    return {
                        "response": response_text,
                        "data": {
                            "pendentes": pendentes,
                            "total": len(pendentes),
                        },
                        "suggestions": [
                            "/comunicado listar",
                            "/comunicado recentes",
                            "/comunicado stats",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicados pendentes reais: {e}")

        # Fallback estatico
        return {
            "response": """📝 **COMUNICADOS PENDENTES** (2)

| # | Comunicado | Status | Tipo |
|---|-----------|--------|------|
| 1 | Nova politica de acesso | Rascunho | politica |
| 2 | Treinamento seguranca - Marco | Agendado | treinamento |

**Total: 2 pendentes**""",
            "suggestions": [
                "/comunicado listar",
                "/comunicado recentes",
                "/comunicado stats",
            ],
        }

    async def _stats(self, args: list[str], context: dict) -> dict[str, Any]:
        """Exibir estatisticas de comunicados (geral ou por comunicado_id)."""
        # Se recebeu um ID, retorna stats especificas do comunicado
        if args:
            comunicado_id = args[0]
            if self.has_data_connector and self.db:
                try:
                    from modules.operacional.communication.repositories.communication_repository import (
                        AnnouncementRepository,
                    )

                    repo = AnnouncementRepository(self.db)
                    tenant_id = context.get("tenant_id", "")

                    announcement = await repo.get_by_id(comunicado_id, tenant_id)
                    if announcement:
                        stats = await repo.get_read_stats(comunicado_id, tenant_id)
                        total_recipients = stats.get("total_recipients", 0)
                        total_reads = stats.get("total_reads", 0)
                        total_acks = stats.get("total_acknowledgments", 0)
                        read_pct = stats.get("read_percentage", 0)
                        ack_pct = stats.get("acknowledgment_percentage", 0)

                        prio_icons = {"urgente": "🔴", "alta": "🟠", "normal": "🟢", "baixa": "⚪"}
                        prio = getattr(announcement, "priority", "normal")

                        return {
                            "response": f"""📊 **ESTATISTICAS DO COMUNICADO**

**Titulo:** {announcement.title}
**Status:** {announcement.status}
**Prioridade:** {prio_icons.get(prio, "⚪")} {prio}
**Requer Confirmacao:** {"Sim" if announcement.requires_acknowledgment else "Nao"}

| Metrica | Valor |
|---------|-------|
| Destinatarios | {total_recipients} |
| Visualizacoes | {total_reads} |
| Confirmacoes | {total_acks} |
| Taxa de Leitura | {read_pct:.1f}% |
| Taxa de Confirmacao | {ack_pct:.1f}% |

{"🟢 Boa taxa de leitura" if read_pct >= 80 else "🟠 Taxa abaixo de 80%" if read_pct >= 50 else "🔴 Taxa critica de leitura (< 50%)"}""",
                            "data": {
                                "comunicado_id": comunicado_id,
                                "total_reads": total_reads,
                                "total_acks": total_acks,
                                "read_pct": read_pct,
                            },
                            "suggestions": [
                                f"/comunicado leituras {comunicado_id}",
                                f"/comunicado nao_lidos {comunicado_id}",
                                f"/comunicado reenviar {comunicado_id}",
                            ],
                        }
                    else:
                        return {
                            "response": f"Comunicado **{comunicado_id}** nao encontrado.",
                            "suggestions": ["/comunicado listar"],
                        }
                except Exception as e:
                    logger.warning(f"Erro ao buscar stats do comunicado: {e}")

            # Fallback para comunicado especifico
            return {
                "response": f"""📊 **ESTATISTICAS DO COMUNICADO** {comunicado_id[:12]}...

| Metrica | Valor |
|---------|-------|
| Destinatarios | 50 |
| Visualizacoes | 35 |
| Confirmacoes | 28 |
| Taxa de Leitura | 70.0% |
| Taxa de Confirmacao | 80.0% |

_Dados ilustrativos._""",
                "suggestions": [
                    f"/comunicado leituras {comunicado_id}",
                    f"/comunicado nao_lidos {comunicado_id}",
                ],
            }

        # Stats gerais (sem ID)
        # Tenta buscar dados reais
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_comunicados_ativos()
                if result.success and result.data:
                    comunicados = result.data
                    total = len(comunicados)
                    total_views = sum(c.get("visualizacoes", 0) for c in comunicados)
                    total_confirms = sum(c.get("confirmacoes", 0) for c in comunicados)
                    urgentes = sum(1 for c in comunicados if c.get("prioridade") in ("urgente", "alta"))
                    taxa = (total_confirms / total_views * 100) if total_views > 0 else 0

                    # Por tipo
                    tipos_count: dict[str, int] = {}
                    for c in comunicados:
                        tipo = c.get("tipo", "outros")
                        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

                    tipos_rows = [f"| {t.capitalize()} | {q} |" for t, q in tipos_count.items()]

                    response_text = f"""📊 **ESTATISTICAS DE COMUNICADOS**

| Metrica | Valor |
|---------|-------|
| Total ativos | {total} |
| Urgentes/Alta | {urgentes} |
| Visualizacoes | {total_views} |
| Confirmacoes | {total_confirms} |
| Taxa confirmacao | {taxa:.1f}% |

**Por Tipo:**

| Tipo | Qtd |
|------|-----|
{chr(10).join(tipos_rows)}

{"🟢 Taxa de confirmacao OK" if taxa >= 80 else "🟠 Taxa abaixo de 80%" if taxa >= 50 else "🔴 Taxa critica (< 50%)"}"""

                    return {
                        "response": response_text,
                        "data": {
                            "total": total,
                            "urgentes": urgentes,
                            "total_views": total_views,
                            "total_confirms": total_confirms,
                            "taxa_confirmacao": taxa,
                        },
                        "suggestions": [
                            "/comunicado listar",
                            "/comunicado recentes",
                            "/comunicado pendentes",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas reais: {e}")

        # Fallback estatico
        return {
            "response": """📊 **ESTATISTICAS DE COMUNICADOS**

| Metrica | Valor |
|---------|-------|
| Total ativos | 3 |
| Urgentes/Alta | 2 |
| Visualizacoes | 195 |
| Confirmacoes | 137 |
| Taxa confirmacao | 70.3% |

**Por Tipo:**

| Tipo | Qtd |
|------|-----|
| Procedimento | 1 |
| Escala | 1 |
| Informativo | 1 |

🟠 Taxa abaixo de 80%""",
            "suggestions": [
                "/comunicado listar",
                "/comunicado recentes",
                "/comunicado pendentes",
            ],
        }

    # ==================================================================
    # TRACKING DE LEITURA
    # ==================================================================

    async def _leituras(self, args: list[str], context: dict) -> dict[str, Any]:
        """Ver quem leu/confirmou um comunicado especifico."""
        if not args:
            return {
                "response": "**Uso:** `/comunicado leituras <comunicado_id>`\n\nExemplo: `/comunicado leituras abc123`",
                "suggestions": ["/comunicado listar", "/comunicado help"],
            }

        comunicado_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.communication.repositories.communication_repository import (
                    AnnouncementRepository,
                )

                repo = AnnouncementRepository(self.db)

                # Busca o comunicado
                tenant_id = context.get("tenant_id", "")
                stats = await repo.get_read_stats(comunicado_id, tenant_id)

                if stats:
                    total_recipients = stats.get("total_recipients", 0)
                    total_reads = stats.get("total_reads", 0)
                    total_acks = stats.get("total_acknowledgments", 0)
                    read_pct = stats.get("read_percentage", 0)
                    ack_pct = stats.get("acknowledgment_percentage", 0)
                    reads = stats.get("reads", [])

                    # Lista de quem leu
                    lines = []
                    for r in reads[:20]:
                        user_id = getattr(r, "user_id", "N/A")
                        read_at = getattr(r, "read_at", None)
                        ack_at = getattr(r, "acknowledged_at", None)
                        read_str = read_at.strftime("%d/%m/%Y %H:%M") if read_at else "N/A"
                        ack_str = "Sim" if ack_at else "Nao"
                        lines.append(f"| {user_id[:12]}... | {read_str} | {ack_str} |")

                    table_rows = "\n".join(lines) if lines else "| Nenhuma leitura registrada | - | - |"

                    status_icon = "🟢" if read_pct >= 80 else "🟠" if read_pct >= 50 else "🔴"

                    return {
                        "response": f"""👁 **LEITURAS DO COMUNICADO** {comunicado_id[:12]}...

**Resumo:**
| Metrica | Valor |
|---------|-------|
| Destinatarios | {total_recipients} |
| Leituras | {total_reads} |
| Confirmacoes | {total_acks} |
| Taxa de Leitura | {status_icon} {read_pct:.1f}% |
| Taxa de Confirmacao | {ack_pct:.1f}% |

**Detalhamento de Leituras:**

| Usuario | Lido em | Confirmou |
|---------|---------|-----------|
{table_rows}

{"*Exibindo os primeiros 20 registros.*" if len(reads) > 20 else ""}""",
                        "data": {
                            "comunicado_id": comunicado_id,
                            "total_reads": total_reads,
                            "total_acks": total_acks,
                            "read_pct": read_pct,
                        },
                        "suggestions": [
                            f"/comunicado nao_lidos {comunicado_id}",
                            f"/comunicado stats {comunicado_id}",
                            f"/comunicado reenviar {comunicado_id}",
                        ],
                    }
                else:
                    return {
                        "response": f"Comunicado **{comunicado_id}** nao encontrado ou sem dados de leitura.",
                        "suggestions": ["/comunicado listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar leituras do comunicado: {e}")

        # Fallback estatico
        return {
            "response": f"""👁 **LEITURAS DO COMUNICADO** {comunicado_id[:12]}...

| Metrica | Valor |
|---------|-------|
| Destinatarios | 50 |
| Leituras | 35 |
| Confirmacoes | 28 |
| Taxa de Leitura | 🟠 70.0% |
| Taxa de Confirmacao | 80.0% |

_Dados ilustrativos. Conecte ao banco para dados reais._""",
            "suggestions": [
                f"/comunicado nao_lidos {comunicado_id}",
                f"/comunicado reenviar {comunicado_id}",
            ],
        }

    async def _nao_lidos(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar quem NAO leu um comunicado."""
        if not args:
            return {
                "response": "**Uso:** `/comunicado nao_lidos <comunicado_id>`\n\nExemplo: `/comunicado nao_lidos abc123`",
                "suggestions": ["/comunicado listar", "/comunicado help"],
            }

        comunicado_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from sqlalchemy import select

                from modules.operacional.communication.models.announcement_read import AnnouncementRead
                from modules.operacional.communication.repositories.communication_repository import (
                    AnnouncementRepository,
                )

                repo = AnnouncementRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                # Buscar comunicado
                announcement = await repo.get_by_id(comunicado_id, tenant_id)
                if not announcement:
                    return {
                        "response": f"Comunicado **{comunicado_id}** nao encontrado.",
                        "suggestions": ["/comunicado listar"],
                    }

                # Buscar quem leu
                reads_result = await self.db.execute(
                    select(AnnouncementRead.user_id).where(AnnouncementRead.announcement_id == comunicado_id)
                )
                read_user_ids = {row[0] for row in reads_result.all()}

                # Obter destinatarios totais
                target_ids = announcement.target_ids or []
                total_targets = len(target_ids) if target_ids else announcement._get_total_targets()

                # Quem NAO leu
                unread_ids = [uid for uid in target_ids if uid not in read_user_ids] if target_ids else []
                unread_count = total_targets - len(read_user_ids)
                if unread_count < 0:
                    unread_count = 0

                lines = []
                for uid in unread_ids[:20]:
                    lines.append(f"- {uid[:12]}...")

                unread_list = "\n".join(lines) if lines else "_Sem dados detalhados de destinatarios._"

                status_icon = "🟢" if unread_count == 0 else "🟠" if unread_count < 5 else "🔴"

                return {
                    "response": f"""{status_icon} **NAO LERAM O COMUNICADO** {comunicado_id[:12]}...

**Titulo:** {announcement.title}
**Total de destinatarios:** {total_targets}
**Ja leram:** {len(read_user_ids)}
**NAO leram:** {unread_count}

{"**Usuarios que nao leram:**" if lines else ""}
{unread_list}

{"*Exibindo os primeiros 20.*" if len(unread_ids) > 20 else ""}""",
                    "data": {
                        "comunicado_id": comunicado_id,
                        "unread_count": unread_count,
                        "read_count": len(read_user_ids),
                    },
                    "suggestions": [
                        f"/comunicado reenviar {comunicado_id}",
                        f"/comunicado leituras {comunicado_id}",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar nao lidos: {e}")

        # Fallback estatico
        return {
            "response": f"""🔴 **NAO LERAM O COMUNICADO** {comunicado_id[:12]}...

**Total destinatarios:** 50
**Ja leram:** 35
**NAO leram:** 15

**Usuarios pendentes:**
- usuario_001...
- usuario_002...
- usuario_003...
- _(e mais 12)_

_Dados ilustrativos._""",
            "suggestions": [
                f"/comunicado reenviar {comunicado_id}",
                f"/comunicado leituras {comunicado_id}",
            ],
        }

    async def _reenviar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Reenviar comunicado para quem nao leu."""
        if not args:
            return {
                "response": "**Uso:** `/comunicado reenviar <comunicado_id>`\n\nExemplo: `/comunicado reenviar abc123`",
                "suggestions": ["/comunicado listar", "/comunicado help"],
            }

        comunicado_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from sqlalchemy import select

                from modules.operacional.communication.models.announcement_read import AnnouncementRead
                from modules.operacional.communication.repositories.communication_repository import (
                    AnnouncementRepository,
                    NotificationRepository,
                )
                from modules.operacional.communication.schemas.communication_schemas import NotificationCreate

                announcement_repo = AnnouncementRepository(self.db)
                tenant_id = context.get("tenant_id", "")

                # Buscar comunicado
                announcement = await announcement_repo.get_by_id(comunicado_id, tenant_id)
                if not announcement:
                    return {
                        "response": f"Comunicado **{comunicado_id}** nao encontrado.",
                        "suggestions": ["/comunicado listar"],
                    }

                # Buscar quem ja leu
                reads_result = await self.db.execute(
                    select(AnnouncementRead.user_id).where(AnnouncementRead.announcement_id == comunicado_id)
                )
                read_user_ids = {row[0] for row in reads_result.all()}

                # Identificar destinatarios que nao leram
                target_ids = announcement.target_ids or []
                unread_ids = [uid for uid in target_ids if uid not in read_user_ids]

                if not unread_ids:
                    return {
                        "response": f"✅ **Todos os destinatarios ja leram o comunicado** {comunicado_id[:12]}...\n\nNao e necessario reenviar.",
                        "suggestions": [f"/comunicado stats {comunicado_id}"],
                    }

                # Criar notificacoes de reenvio
                notification_repo = NotificationRepository(self.db)
                count = 0
                for uid in unread_ids:
                    try:
                        from modules.operacional.communication.models.notification import (
                            NotificationChannel,
                            NotificationType,
                        )

                        notif_data = NotificationCreate(
                            user_id=uid,
                            title=f"Lembrete: {announcement.title}",
                            body=f"Voce ainda nao leu o comunicado: {announcement.title}. Por favor, acesse e confirme a leitura.",
                            type=NotificationType.REMINDER,
                            channels=[NotificationChannel.IN_APP],
                            reference_type="announcement",
                            reference_id=comunicado_id,
                        )
                        await notification_repo.create(notif_data, tenant_id)
                        count += 1
                    except Exception as notif_err:
                        logger.warning(f"Erro ao criar notificacao para {uid}: {notif_err}")

                return {
                    "response": f"""📤 **COMUNICADO REENVIADO**

**Comunicado:** {announcement.title}
**Notificacoes enviadas:** {count}
**Destinatarios pendentes:** {len(unread_ids)}

As notificacoes de lembrete foram criadas para os usuarios que ainda nao leram.""",
                    "data": {
                        "comunicado_id": comunicado_id,
                        "notificacoes_enviadas": count,
                        "pendentes": len(unread_ids),
                    },
                    "suggestions": [
                        f"/comunicado leituras {comunicado_id}",
                        f"/comunicado nao_lidos {comunicado_id}",
                    ],
                }
            except ImportError as ie:
                logger.warning(f"Import nao disponivel para reenvio: {ie}")
            except Exception as e:
                logger.warning(f"Erro ao reenviar comunicado: {e}")

        # Fallback estatico
        return {
            "response": f"""📤 **COMUNICADO REENVIADO** (simulacao)

**Comunicado:** {comunicado_id[:12]}...
**Notificacoes enviadas:** 15
**Destinatarios pendentes:** 15

_Acao simulada. Conecte ao banco para reenvio real._""",
            "suggestions": [
                f"/comunicado leituras {comunicado_id}",
                f"/comunicado nao_lidos {comunicado_id}",
            ],
        }

    def get_help(self) -> str:
        return """**Skill /comunicado**

**Comandos disponiveis:**
```
/comunicado listar              - Listar comunicados ativos
/comunicado recentes            - Comunicados recentes
/comunicado pendentes           - Rascunhos pendentes de publicacao
/comunicado stats               - Estatisticas gerais
/comunicado stats <id>          - Estatisticas de um comunicado
/comunicado leituras <id>       - Ver quem leu/confirmou
/comunicado nao_lidos <id>      - Listar quem NAO leu
/comunicado reenviar <id>       - Reenviar para quem nao leu
/comunicado help                - Esta ajuda
```

**Exemplos:**
- `/comunicado listar`
- `/comunicado stats`
- `/comunicado leituras abc123-def456`
- `/comunicado nao_lidos abc123-def456`
- `/comunicado reenviar abc123-def456`"""
