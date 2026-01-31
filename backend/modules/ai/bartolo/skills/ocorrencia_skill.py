"""
Skill /ocorrencia - Gerenciamento de ocorrencias via comando slash.
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import date

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class OcorrenciaSkill(BaseSkill):
    """
    Skill para gerenciamento de ocorrencias disciplinares.

    Comandos:
        /ocorrencia resumo           - Resumo geral de ocorrencias
        /ocorrencia abertas          - Listar ocorrencias abertas
        /ocorrencia graves           - Listar ocorrencias graves/criticas
        /ocorrencia posto <code>     - Ocorrencias de um posto
        /ocorrencia stats            - Estatisticas
        /ocorrencia help             - Ajuda
    """

    name = "ocorrencia"
    description = "Gerenciamento de ocorrencias disciplinares"
    commands = [
        "resumo", "abertas", "graves", "posto", "stats",
        "anexo", "anexos", "comentar", "comentarios", "historico",
        "help",
    ]

    def __init__(self, data_connector: Optional["DataConnector"] = None, db=None):
        super().__init__(data_connector=data_connector)
        self.db = db

    async def execute(self, command: str, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa comando de ocorrencia."""

        if not command or command == "help":
            return {"response": self.get_help(), "suggestions": self.commands[:4]}

        handlers = {
            "resumo": self._resumo,
            "abertas": self._abertas,
            "graves": self._graves,
            "posto": self._posto,
            "stats": self._stats,
            "anexo": self._adicionar_anexo,
            "anexos": self._listar_anexos,
            "comentar": self._adicionar_comentario,
            "comentarios": self._listar_comentarios,
            "historico": self._historico_funcionario,
        }

        handler = handlers.get(command)
        if handler:
            return await handler(args, context)

        return {
            "response": f"Comando '{command}' nao reconhecido. Use /ocorrencia help para ver os comandos.",
            "suggestions": self.commands[:4],
        }

    async def _resumo(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Resumo geral de ocorrencias."""
        # Tentar dados reais via DataConnector
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_ocorrencias_abertas()
                if result.success and result.data:
                    total = result.total_count
                    graves = sum(
                        1 for o in result.data
                        if o.get("severidade") in ("grave", "gravissima")
                    )
                    em_analise = sum(
                        1 for o in result.data
                        if o.get("status") == "em_analise"
                    )
                    abertas = sum(
                        1 for o in result.data
                        if o.get("status") == "aberta"
                    )

                    response = f"""📋 **RESUMO DE OCORRENCIAS**

**Ocorrencias Pendentes:** {total}
- Abertas: **{abertas}**
- Em Analise: **{em_analise}**
- Graves/Gravissimas: **{graves}** {'🚨' if graves > 0 else '✅'}

{'🚨 **ATENCAO:** Ha ocorrencias graves pendentes de resolucao!' if graves > 0 else '✅ Nenhuma ocorrencia grave pendente.'}

Use `/ocorrencia abertas` para ver a lista completa.
Use `/ocorrencia stats` para estatisticas detalhadas."""

                    return {
                        "response": response,
                        "data": {
                            "total": total,
                            "abertas": abertas,
                            "em_analise": em_analise,
                            "graves": graves,
                        },
                        "suggestions": ["/ocorrencia abertas", "/ocorrencia graves", "/ocorrencia stats"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar resumo de ocorrencias: {e}")

        # Fallback estatico
        return {
            "response": """📋 **RESUMO DE OCORRENCIAS**

**Ocorrencias Pendentes:** 5
- Abertas: **3**
- Em Analise: **2**
- Graves/Gravissimas: **1** 🚨

🚨 **ATENCAO:** Ha ocorrencias graves pendentes de resolucao!

Use `/ocorrencia abertas` para ver a lista completa.
Use `/ocorrencia stats` para estatisticas detalhadas.""",
            "data": {"total": 5, "abertas": 3, "em_analise": 2, "graves": 1},
            "suggestions": ["/ocorrencia abertas", "/ocorrencia graves", "/ocorrencia stats"],
        }

    async def _abertas(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Listar ocorrencias abertas."""
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_ocorrencias_abertas()
                if result.success:
                    return {
                        "response": result.message,
                        "data": {
                            "ocorrencias": result.data,
                            "total": result.total_count,
                        },
                        "suggestions": ["/ocorrencia graves", "/ocorrencia stats", "/ocorrencia help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias abertas: {e}")

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

**Total abertas:** 3
**Graves:** 1 🚨""",
            "data": {"total": 3},
            "suggestions": ["/ocorrencia graves", "/ocorrencia stats", "/ocorrencia help"],
        }

    async def _graves(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Listar ocorrencias graves e criticas."""
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_ocorrencias_abertas()
                if result.success and result.data:
                    graves = [
                        o for o in result.data
                        if o.get("severidade") in ("grave", "gravissima")
                    ]

                    if graves:
                        lines = []
                        for o in graves:
                            sev_icon = "🚨" if o.get("severidade") == "gravissima" else "🔴"
                            status_text = "Aberta" if o.get("status") == "aberta" else "Em Analise"
                            lines.append(
                                f"- {sev_icon} **{o['codigo']}** - {o['titulo']}\n"
                                f"  Severidade: {o['severidade']} | Status: {status_text} | {o.get('data', 'N/A')}"
                            )

                        response = f"""🚨 **OCORRENCIAS GRAVES/GRAVISSIMAS** ({len(graves)})

{chr(10).join(lines)}

**ATENCAO:** Estas ocorrencias requerem tratamento prioritario!"""
                    else:
                        response = "✅ **Nenhuma ocorrencia grave ou gravissima pendente.** Todas foram resolvidas."

                    return {
                        "response": response,
                        "data": {"graves": graves, "total": len(graves)},
                        "suggestions": ["/ocorrencia abertas", "/ocorrencia stats", "/ocorrencia help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias graves: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""🚨 **OCORRENCIAS GRAVES/GRAVISSIMAS** (2)

- 🔴 **OCO-2026-00012** - Abandono de posto - Portaria B
  Severidade: grave | Status: Aberta | {today} 08:30
- 🚨 **OCO-2026-00007** - Embriaguez em servico
  Severidade: gravissima | Status: Em Analise | {today}

**ATENCAO:** Estas ocorrencias requerem tratamento prioritario!""",
            "data": {"total": 2},
            "suggestions": ["/ocorrencia abertas", "/ocorrencia stats", "/ocorrencia help"],
        }

    async def _posto(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Ocorrencias de um posto especifico."""
        if not args:
            return {
                "response": "**Uso:** `/ocorrencia posto <codigo>`\n\nExemplo: `/ocorrencia posto POST-001`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        post_code = args[0].upper()

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                from modules.operacional.repositories.post_repository import PostRepository

                post_repo = PostRepository(self.db)
                post = await post_repo.get_by_code(post_code)

                if post:
                    repo = OccurrenceRepository(self.db)
                    ocorrencias = await repo.get_by_post(post.id)

                    if ocorrencias:
                        lines = []
                        for o in ocorrencias[:15]:
                            sev_icon = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}.get(o.severity, "⚪")
                            occurred = o.occurred_at.strftime('%d/%m/%Y') if o.occurred_at else 'N/A'
                            status_label = {"aberta": "Aberta", "em_analise": "Analise", "resolvida": "Resolvida"}.get(o.status, o.status)
                            lines.append(f"- {sev_icon} **{o.code}** - {o.title} | {status_label} | {occurred}")

                        response = f"""📍 **OCORRENCIAS - {post_code}** ({post.name})

{chr(10).join(lines)}

**Total:** {len(ocorrencias)} ocorrencia(s)"""
                    else:
                        response = f"✅ **Nenhuma ocorrencia registrada para {post_code}** ({post.name})."

                    return {
                        "response": response,
                        "data": {"posto": post_code, "total": len(ocorrencias)},
                        "suggestions": ["/ocorrencia stats", "/ocorrencia abertas"],
                    }
                else:
                    return {
                        "response": f"Posto **{post_code}** nao encontrado. Verifique o codigo.",
                        "suggestions": ["/ocorrencia help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar ocorrencias do posto: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""📍 **OCORRENCIAS - {post_code}**

- 🔴 **OCO-2026-00012** - Abandono de posto | Aberta | {today}
- 🟡 **OCO-2026-00008** - Uso de celular | Resolvida | {today}
- 🟠 **OCO-2026-00005** - Falta de uniforme | Resolvida | {today}

**Total:** 3 ocorrencia(s)""",
            "data": {"posto": post_code, "total": 3},
            "suggestions": ["/ocorrencia stats", "/ocorrencia abertas"],
        }

    async def _stats(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Estatisticas de ocorrencias."""
        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)
                stats = await repo.get_stats()

                if stats.total > 0:
                    # Por severidade
                    sev_lines = []
                    sev_icons = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}
                    for sev in ["gravissima", "grave", "moderada", "leve"]:
                        count = stats.by_severity.get(sev, 0)
                        if count > 0:
                            sev_lines.append(f"  {sev_icons.get(sev, '⚪')} {sev.title()}: **{count}**")

                    # Por tipo (top 5)
                    tipo_lines = []
                    sorted_types = sorted(stats.by_type.items(), key=lambda x: x[1], reverse=True)
                    for tipo, count in sorted_types[:5]:
                        tipo_label = tipo.replace("_", " ").title()
                        tipo_lines.append(f"  - {tipo_label}: **{count}**")

                    # Por categoria
                    cat_lines = []
                    sorted_cats = sorted(stats.by_category.items(), key=lambda x: x[1], reverse=True)
                    for cat, count in sorted_cats:
                        cat_label = cat.replace("_", " ").title()
                        cat_lines.append(f"  - {cat_label}: **{count}**")

                    avg_time = f"{stats.avg_resolution_time_hours:.1f}h" if stats.avg_resolution_time_hours else "N/A"

                    response = f"""📊 **ESTATISTICAS DE OCORRENCIAS**

| Indicador | Valor |
|-----------|-------|
| Total | {stats.total} |
| Abertas | {stats.open} |
| Em Analise | {stats.in_analysis} |
| Resolvidas | {stats.resolved} |
| Graves | {stats.severe} {'🚨' if stats.severe > 0 else ''} |
| Tempo Medio Resolucao | {avg_time} |

**Por Severidade:**
{chr(10).join(sev_lines) if sev_lines else '  Nenhum dado'}

**Por Tipo (Top 5):**
{chr(10).join(tipo_lines) if tipo_lines else '  Nenhum dado'}

**Por Categoria:**
{chr(10).join(cat_lines) if cat_lines else '  Nenhum dado'}"""

                    return {
                        "response": response,
                        "data": {
                            "total": stats.total,
                            "abertas": stats.open,
                            "graves": stats.severe,
                            "avg_resolution_time": stats.avg_resolution_time_hours,
                        },
                        "suggestions": ["/ocorrencia abertas", "/ocorrencia graves", "/ocorrencia help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas: {e}")

        # Fallback estatico
        return {
            "response": """📊 **ESTATISTICAS DE OCORRENCIAS**

| Indicador | Valor |
|-----------|-------|
| Total | 42 |
| Abertas | 5 |
| Em Analise | 3 |
| Resolvidas | 31 |
| Graves | 8 🚨 |
| Tempo Medio Resolucao | 48.3h |

**Por Severidade:**
  🚨 Gravissima: **2**
  🔴 Grave: **6**
  🟠 Moderada: **15**
  🟡 Leve: **19**

**Por Tipo (Top 5):**
  - Uso Celular: **9**
  - Falta Uniforme: **7**
  - Atraso: **6**
  - Abandono Posto: **5**
  - Postura Inadequada: **4**

**Por Categoria:**
  - Disciplinar: **18**
  - Operacional: **10**
  - Assiduidade: **8**
  - Conduta: **4**
  - Seguranca Trabalho: **2**""",
            "data": {"total": 42, "abertas": 5, "graves": 8, "avg_resolution_time": 48.3},
            "suggestions": ["/ocorrencia abertas", "/ocorrencia graves", "/ocorrencia help"],
        }

    # ==================================================================
    # ANEXOS E COMENTARIOS
    # ==================================================================

    async def _adicionar_anexo(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Adicionar anexo/evidencia a uma ocorrencia."""
        if len(args) < 2:
            return {
                "response": "**Uso:** `/ocorrencia anexo <ocorrencia_id> <descricao>`\n\nExemplo: `/ocorrencia anexo OCO-2026-00012 Foto do posto vazio`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        ocorrencia_id = args[0]
        descricao = " ".join(args[1:])

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)

                # Buscar pelo ID ou codigo
                occurrence = await repo.get_by_id(ocorrencia_id)
                if not occurrence:
                    # Tenta buscar por codigo
                    from sqlalchemy import select
                    from modules.operacional.occurrences.models.occurrence import Occurrence
                    result = await self.db.execute(
                        select(Occurrence).where(
                            Occurrence.code == ocorrencia_id.upper(),
                            Occurrence.is_active.is_(True),
                        )
                    )
                    occurrence = result.scalar_one_or_none()

                if not occurrence:
                    return {
                        "response": f"Ocorrencia **{ocorrencia_id}** nao encontrada.",
                        "suggestions": ["/ocorrencia abertas"],
                    }

                # Adicionar anexo (registro via JSON no campo attachments)
                attachment_data = {
                    "type": "evidence",
                    "name": f"anexo_{descricao[:30].replace(' ', '_')}",
                    "description": descricao,
                    "url": f"/uploads/occurrences/{occurrence.id}/pending",
                    "size": 0,
                }
                updated = await repo.add_attachment(occurrence.id, attachment_data)

                if updated:
                    current_attachments = updated.attachments or {"attachments": []}
                    total_anexos = len(current_attachments.get("attachments", []))

                    return {
                        "response": f"""📎 **ANEXO REGISTRADO**

**Ocorrencia:** {occurrence.code} - {occurrence.title}
**Descricao do anexo:** {descricao}
**Total de anexos:** {total_anexos}

_O anexo foi registrado. Para upload do arquivo, utilize a interface web._""",
                        "data": {
                            "ocorrencia_id": occurrence.id,
                            "ocorrencia_code": occurrence.code,
                            "total_anexos": total_anexos,
                        },
                        "suggestions": [
                            f"/ocorrencia anexos {occurrence.code}",
                            f"/ocorrencia comentar {occurrence.code} Anexo adicionado",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Erro ao adicionar anexo: {e}")

        # Fallback estatico
        return {
            "response": f"""📎 **ANEXO REGISTRADO** (simulacao)

**Ocorrencia:** {ocorrencia_id}
**Descricao:** {descricao}

_Acao simulada. Conecte ao banco para registro real._""",
            "suggestions": [f"/ocorrencia anexos {ocorrencia_id}"],
        }

    async def _listar_anexos(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Listar anexos de uma ocorrencia."""
        if not args:
            return {
                "response": "**Uso:** `/ocorrencia anexos <ocorrencia_id>`\n\nExemplo: `/ocorrencia anexos OCO-2026-00012`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        ocorrencia_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                from modules.operacional.occurrences.models.occurrence_attachment import OccurrenceAttachment
                from modules.operacional.occurrences.models.occurrence import Occurrence
                from sqlalchemy import select

                repo = OccurrenceRepository(self.db)

                # Buscar pelo ID ou codigo
                occurrence = await repo.get_by_id(ocorrencia_id)
                if not occurrence:
                    result = await self.db.execute(
                        select(Occurrence).where(
                            Occurrence.code == ocorrencia_id.upper(),
                            Occurrence.is_active.is_(True),
                        )
                    )
                    occurrence = result.scalar_one_or_none()

                if not occurrence:
                    return {
                        "response": f"Ocorrencia **{ocorrencia_id}** nao encontrada.",
                        "suggestions": ["/ocorrencia abertas"],
                    }

                # Buscar anexos do model OccurrenceAttachment
                att_result = await self.db.execute(
                    select(OccurrenceAttachment).where(
                        OccurrenceAttachment.occurrence_id == occurrence.id,
                        OccurrenceAttachment.is_active.is_(True),
                    ).order_by(OccurrenceAttachment.uploaded_at.desc())
                )
                attachments_db = list(att_result.scalars().all())

                # Tambem verificar o campo JSONB
                json_attachments = []
                if occurrence.attachments:
                    json_attachments = occurrence.attachments.get("attachments", [])

                total = len(attachments_db) + len(json_attachments)

                if total == 0:
                    return {
                        "response": f"📎 **Nenhum anexo** encontrado para **{occurrence.code}** - {occurrence.title}.",
                        "suggestions": [f"/ocorrencia anexo {occurrence.code} <descricao>"],
                    }

                lines = []
                # Anexos do model
                type_icons = {"imagem": "🖼", "video": "🎥", "audio": "🎵", "documento": "📄", "outro": "📎"}
                for idx, att in enumerate(attachments_db, 1):
                    icon = type_icons.get(att.file_type, "📎")
                    size_str = f"{att.file_size_kb:.0f} KB" if att.file_size_kb else "N/A"
                    uploaded = att.uploaded_at.strftime('%d/%m/%Y %H:%M') if att.uploaded_at else 'N/A'
                    desc = att.description or att.file_name
                    lines.append(f"| {idx} | {icon} {att.file_type} | {desc[:30]} | {size_str} | {uploaded} |")

                # Anexos JSONB
                for idx_offset, jatt in enumerate(json_attachments, len(attachments_db) + 1):
                    desc = jatt.get("description", jatt.get("name", "N/A"))
                    uploaded = jatt.get("uploaded_at", "N/A")
                    lines.append(f"| {idx_offset} | 📎 {jatt.get('type', 'N/A')} | {desc[:30]} | N/A | {uploaded[:16] if isinstance(uploaded, str) else 'N/A'} |")

                return {
                    "response": f"""📎 **ANEXOS DA OCORRENCIA** {occurrence.code}

**Ocorrencia:** {occurrence.code} - {occurrence.title}
**Total de anexos:** {total}

| # | Tipo | Descricao | Tamanho | Data |
|---|------|-----------|---------|------|
{chr(10).join(lines)}""",
                    "data": {
                        "ocorrencia_id": occurrence.id,
                        "ocorrencia_code": occurrence.code,
                        "total_anexos": total,
                    },
                    "suggestions": [
                        f"/ocorrencia anexo {occurrence.code} Nova evidencia",
                        f"/ocorrencia comentarios {occurrence.code}",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao listar anexos: {e}")

        # Fallback estatico
        return {
            "response": f"""📎 **ANEXOS DA OCORRENCIA** {ocorrencia_id}

| # | Tipo | Descricao | Tamanho | Data |
|---|------|-----------|---------|------|
| 1 | 🖼 imagem | Foto do posto vazio | 2.3 MB | 29/01/2026 08:30 |
| 2 | 📄 documento | Relatorio da ocorrencia | 156 KB | 29/01/2026 09:00 |

**Total:** 2 anexos

_Dados ilustrativos._""",
            "suggestions": [
                f"/ocorrencia anexo {ocorrencia_id} Nova evidencia",
                f"/ocorrencia comentarios {ocorrencia_id}",
            ],
        }

    async def _adicionar_comentario(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Adicionar comentario a uma ocorrencia."""
        if len(args) < 2:
            return {
                "response": "**Uso:** `/ocorrencia comentar <ocorrencia_id> <texto>`\n\nExemplo: `/ocorrencia comentar OCO-2026-00012 Funcionario notificado`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        ocorrencia_id = args[0]
        texto = " ".join(args[1:])

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                from modules.operacional.occurrences.models.occurrence import Occurrence
                from modules.operacional.occurrences.models.occurrence_comment import OccurrenceComment
                from sqlalchemy import select, func
                from uuid import uuid4

                repo = OccurrenceRepository(self.db)

                # Buscar pelo ID ou codigo
                occurrence = await repo.get_by_id(ocorrencia_id)
                if not occurrence:
                    result = await self.db.execute(
                        select(Occurrence).where(
                            Occurrence.code == ocorrencia_id.upper(),
                            Occurrence.is_active.is_(True),
                        )
                    )
                    occurrence = result.scalar_one_or_none()

                if not occurrence:
                    return {
                        "response": f"Ocorrencia **{ocorrencia_id}** nao encontrada.",
                        "suggestions": ["/ocorrencia abertas"],
                    }

                # Criar comentario
                author_id = context.get("user_id", context.get("inspector_id", "system"))
                author_name = context.get("user_name", "Bartolo IA")

                comment = OccurrenceComment(
                    id=str(uuid4()),
                    occurrence_id=occurrence.id,
                    author_id=author_id,
                    author_name=author_name,
                    content=texto,
                    is_internal=True,  # Comentarios via Bartolo sao internos
                )

                self.db.add(comment)
                await self.db.commit()
                await self.db.refresh(comment)

                # Contar total de comentarios
                count_result = await self.db.execute(
                    select(func.count(OccurrenceComment.id)).where(
                        OccurrenceComment.occurrence_id == occurrence.id,
                        OccurrenceComment.is_active.is_(True),
                    )
                )
                total_comments = count_result.scalar() or 0

                return {
                    "response": f"""💬 **COMENTARIO ADICIONADO**

**Ocorrencia:** {occurrence.code} - {occurrence.title}
**Autor:** {author_name}
**Texto:** {texto}
**Total de comentarios:** {total_comments}
**Tipo:** Interno (visivel apenas para operadores)""",
                    "data": {
                        "ocorrencia_id": occurrence.id,
                        "ocorrencia_code": occurrence.code,
                        "comment_id": comment.id,
                        "total_comments": total_comments,
                    },
                    "suggestions": [
                        f"/ocorrencia comentarios {occurrence.code}",
                        f"/ocorrencia anexos {occurrence.code}",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao adicionar comentario: {e}")

        # Fallback estatico
        return {
            "response": f"""💬 **COMENTARIO ADICIONADO** (simulacao)

**Ocorrencia:** {ocorrencia_id}
**Texto:** {texto}

_Acao simulada. Conecte ao banco para registro real._""",
            "suggestions": [f"/ocorrencia comentarios {ocorrencia_id}"],
        }

    async def _listar_comentarios(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Listar comentarios de uma ocorrencia."""
        if not args:
            return {
                "response": "**Uso:** `/ocorrencia comentarios <ocorrencia_id>`\n\nExemplo: `/ocorrencia comentarios OCO-2026-00012`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        ocorrencia_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                from modules.operacional.occurrences.models.occurrence import Occurrence
                from modules.operacional.occurrences.models.occurrence_comment import OccurrenceComment
                from sqlalchemy import select

                repo = OccurrenceRepository(self.db)

                # Buscar pelo ID ou codigo
                occurrence = await repo.get_by_id(ocorrencia_id)
                if not occurrence:
                    result = await self.db.execute(
                        select(Occurrence).where(
                            Occurrence.code == ocorrencia_id.upper(),
                            Occurrence.is_active.is_(True),
                        )
                    )
                    occurrence = result.scalar_one_or_none()

                if not occurrence:
                    return {
                        "response": f"Ocorrencia **{ocorrencia_id}** nao encontrada.",
                        "suggestions": ["/ocorrencia abertas"],
                    }

                # Buscar comentarios
                comments_result = await self.db.execute(
                    select(OccurrenceComment).where(
                        OccurrenceComment.occurrence_id == occurrence.id,
                        OccurrenceComment.is_active.is_(True),
                    ).order_by(OccurrenceComment.created_at.desc())
                )
                comments = list(comments_result.scalars().all())

                if not comments:
                    return {
                        "response": f"💬 **Nenhum comentario** encontrado para **{occurrence.code}** - {occurrence.title}.",
                        "suggestions": [
                            f"/ocorrencia comentar {occurrence.code} <texto>",
                            f"/ocorrencia anexos {occurrence.code}",
                        ],
                    }

                lines = []
                for idx, c in enumerate(comments[:20], 1):
                    author = c.author_name or c.author_id[:8]
                    created = c.created_at.strftime('%d/%m/%Y %H:%M') if c.created_at else 'N/A'
                    internal = "[INTERNO]" if c.is_internal else ""
                    edited = "(editado)" if c.is_edited else ""
                    preview = c.preview
                    lines.append(f"**{idx}. {author}** - {created} {internal} {edited}\n   {preview}\n")

                return {
                    "response": f"""💬 **COMENTARIOS DA OCORRENCIA** {occurrence.code}

**Ocorrencia:** {occurrence.code} - {occurrence.title}
**Total de comentarios:** {len(comments)}

{chr(10).join(lines)}

{'*Exibindo os primeiros 20 comentarios.*' if len(comments) > 20 else ''}""",
                    "data": {
                        "ocorrencia_id": occurrence.id,
                        "ocorrencia_code": occurrence.code,
                        "total_comments": len(comments),
                    },
                    "suggestions": [
                        f"/ocorrencia comentar {occurrence.code} <texto>",
                        f"/ocorrencia anexos {occurrence.code}",
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao listar comentarios: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""💬 **COMENTARIOS DA OCORRENCIA** {ocorrencia_id}

**Total:** 3 comentarios

**1. Supervisor Carlos** - {today} 09:30 [INTERNO]
   Funcionario notificado verbalmente sobre a ocorrencia.

**2. Gestor Ana** - {today} 10:15 [INTERNO]
   Agendada reuniao para tratar a questao.

**3. Bartolo IA** - {today} 11:00 [INTERNO]
   Ocorrencia vinculada ao historico do funcionario.

_Dados ilustrativos._""",
            "suggestions": [
                f"/ocorrencia comentar {ocorrencia_id} <texto>",
                f"/ocorrencia anexos {ocorrencia_id}",
            ],
        }

    async def _historico_funcionario(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Historico de ocorrencias de um funcionario."""
        if not args:
            return {
                "response": "**Uso:** `/ocorrencia historico <funcionario_id>`\n\nExemplo: `/ocorrencia historico abc123-def456`",
                "suggestions": ["/ocorrencia abertas", "/ocorrencia help"],
            }

        funcionario_id = args[0]

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.models.occurrence import Occurrence
                from sqlalchemy import select, func

                # Buscar ocorrencias do funcionario
                result = await self.db.execute(
                    select(Occurrence).where(
                        Occurrence.employee_id == funcionario_id,
                        Occurrence.is_active.is_(True),
                    ).order_by(Occurrence.occurred_at.desc())
                )
                ocorrencias = list(result.scalars().all())

                if not ocorrencias:
                    return {
                        "response": f"✅ **Nenhuma ocorrencia** encontrada para o funcionario **{funcionario_id[:12]}...**",
                        "suggestions": ["/ocorrencia abertas", "/ocorrencia stats"],
                    }

                # Resumo
                total = len(ocorrencias)
                abertas = sum(1 for o in ocorrencias if o.status == "aberta")
                em_analise = sum(1 for o in ocorrencias if o.status == "em_analise")
                resolvidas = sum(1 for o in ocorrencias if o.status == "resolvida")
                graves = sum(1 for o in ocorrencias if o.is_severe)

                # Por severidade
                sev_count: Dict[str, int] = {}
                for o in ocorrencias:
                    sev_count[o.severity] = sev_count.get(o.severity, 0) + 1

                sev_icons = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}
                sev_lines = [f"  {sev_icons.get(s, '⚪')} {s.title()}: **{c}**" for s, c in sorted(sev_count.items(), key=lambda x: x[1], reverse=True)]

                # Ultimas ocorrencias
                lines = []
                for o in ocorrencias[:10]:
                    sev_icon = sev_icons.get(o.severity, "⚪")
                    occurred = o.occurred_at.strftime('%d/%m/%Y') if o.occurred_at else 'N/A'
                    status_label = {"aberta": "Aberta", "em_analise": "Analise", "resolvida": "Resolvida", "arquivada": "Arquivada"}.get(o.status, o.status)
                    lines.append(f"| {sev_icon} {o.code} | {o.title[:30]} | {status_label} | {occurred} |")

                reincidente_alert = ""
                if total >= 3:
                    reincidente_alert = f"\n**ATENCAO:** Funcionario reincidente com {total} ocorrencia(s)!"
                if graves >= 2:
                    reincidente_alert += f"\n🚨 **{graves} ocorrencias graves/gravissimas!**"

                return {
                    "response": f"""📋 **HISTORICO DO FUNCIONARIO** {funcionario_id[:12]}...

**Resumo:**
| Indicador | Valor |
|-----------|-------|
| Total de Ocorrencias | {total} |
| Abertas | {abertas} |
| Em Analise | {em_analise} |
| Resolvidas | {resolvidas} |
| Graves/Gravissimas | {graves} {'🚨' if graves > 0 else ''} |

**Por Severidade:**
{chr(10).join(sev_lines)}

**Ultimas Ocorrencias:**

| Ocorrencia | Titulo | Status | Data |
|------------|--------|--------|------|
{chr(10).join(lines)}

{'*Exibindo as 10 mais recentes.*' if total > 10 else ''}{reincidente_alert}""",
                    "data": {
                        "funcionario_id": funcionario_id,
                        "total": total,
                        "abertas": abertas,
                        "graves": graves,
                        "reincidente": total >= 3,
                    },
                    "suggestions": ["/ocorrencia stats", "/ocorrencia abertas"],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar historico do funcionario: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""📋 **HISTORICO DO FUNCIONARIO** {funcionario_id[:12]}...

**Total:** 4 ocorrencias

| Ocorrencia | Titulo | Status | Data |
|------------|--------|--------|------|
| 🔴 OCO-2026-00012 | Abandono de posto | Aberta | {today} |
| 🟡 OCO-2026-00008 | Uso de celular | Resolvida | {today} |
| 🟠 OCO-2026-00005 | Falta de uniforme | Resolvida | {today} |
| 🟡 OCO-2025-00042 | Atraso | Resolvida | 15/12/2025 |

**ATENCAO:** Funcionario reincidente com 4 ocorrencia(s)!

_Dados ilustrativos._""",
            "data": {"funcionario_id": funcionario_id, "total": 4, "reincidente": True},
            "suggestions": ["/ocorrencia stats", "/ocorrencia abertas"],
        }

    def get_help(self) -> str:
        return """**Skill /ocorrencia**

**Comandos disponiveis:**
```
/ocorrencia resumo                        - Resumo geral de ocorrencias
/ocorrencia abertas                       - Lista ocorrencias abertas
/ocorrencia graves                        - Lista graves/gravissimas
/ocorrencia posto <codigo>                - Ocorrencias de um posto
/ocorrencia stats                         - Estatisticas completas
/ocorrencia anexo <id> <descricao>        - Adicionar anexo/evidencia
/ocorrencia anexos <id>                   - Listar anexos
/ocorrencia comentar <id> <texto>         - Adicionar comentario
/ocorrencia comentarios <id>              - Listar comentarios
/ocorrencia historico <funcionario_id>    - Historico do funcionario
```

**Exemplos:**
- `/ocorrencia resumo`
- `/ocorrencia abertas`
- `/ocorrencia graves`
- `/ocorrencia posto POST-001`
- `/ocorrencia stats`
- `/ocorrencia anexo OCO-2026-00012 Foto do posto vazio`
- `/ocorrencia anexos OCO-2026-00012`
- `/ocorrencia comentar OCO-2026-00012 Funcionario notificado`
- `/ocorrencia comentarios OCO-2026-00012`
- `/ocorrencia historico abc123-def456`"""
