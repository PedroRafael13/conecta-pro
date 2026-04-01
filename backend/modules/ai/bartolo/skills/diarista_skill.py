"""
Skill /diarista - Gerenciamento de diaristas via comando
"""

import contextlib
import logging
from typing import TYPE_CHECKING, Any, Optional

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class DiaristaSkill(BaseSkill):
    """
    Skill para gerenciamento de diaristas.

    Comandos:
        /diarista listar                             - Lista diaristas ativas
        /diarista disponiveis [data]                 - Disponiveis para trabalho
        /diarista escalados                          - Escalados hoje
        /diarista stats                              - Estatisticas
        /diarista avaliar [diarista_id] [schedule_id]  - Iniciar avaliacao
        /diarista avaliacoes [diarista_id]            - Ver historico de avaliacoes
        /diarista pagamento gerar [diarista_id] [periodo] - Gerar pagamento
        /diarista pagamento aprovar [pagamento_id]   - Aprovar pagamento
        /diarista pagamentos [diarista_id]            - Listar pagamentos
        /diarista agenda [diarista_id] [periodo]     - Ver agenda detalhada
        /diarista help                               - Ajuda
    """

    name = "diarista"
    description = "Gerenciamento de diaristas"
    commands = [
        "listar",
        "disponiveis",
        "escalados",
        "stats",
        "avaliar",
        "avaliacoes",
        "pagamento",
        "pagamentos",
        "agenda",
        "help",
    ]

    def __init__(self, data_connector: Optional["DataConnector"] = None, diarist_repo=None):
        super().__init__(data_connector=data_connector)
        self.diarist_repo = diarist_repo

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa comando de diarista"""

        if not command or command == "help":
            return {"response": self.get_help(), "suggestions": self.commands[:4]}

        handlers = {
            "listar": self._listar,
            "disponiveis": self._disponiveis,
            "escalados": self._escalados,
            "stats": self._stats,
            "avaliar": self._avaliar,
            "avaliacoes": self._avaliacoes,
            "pagamento": self._pagamento,
            "pagamentos": self._pagamentos,
            "agenda": self._agenda,
        }

        handler = handlers.get(command)
        if handler:
            return await handler(args, context)

        return {
            "response": f"Comando '{command}' nao reconhecido. Use /diarista help para ver os comandos.",
            "suggestions": self.commands[:4],
        }

    async def _listar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar diaristas ativas"""
        # Tenta buscar dados reais via repository do DataConnector
        if self.has_data_connector:
            try:
                from modules.operacional.diaristas.models.diarist import DiaristStatus
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)

                # Filtro por tipo se fornecido
                search_term = args[0] if args else None

                diaristas = await repo.list_all(
                    status=DiaristStatus.ATIVO,
                    search=search_term,
                    limit=20,
                )

                if diaristas:
                    lines = []
                    for i, d in enumerate(diaristas[:15], 1):
                        tipos = ", ".join(d.tipos_servico or []) or "N/A"
                        avaliacao = f"{float(d.avaliacao_media or 0):.1f}" if d.avaliacao_media else "N/A"
                        valor = f"R$ {float(d.valor_diaria or 0):,.2f}"
                        lines.append(f"| {i} | {d.nome} | {tipos} | {avaliacao} | {valor} |")

                    tabela = "\n".join(lines)
                    filtro_info = f" (busca: {search_term})" if search_term else ""

                    return {
                        "response": f"""**Diaristas Ativas{filtro_info} ({len(diaristas)})**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
{tabela}

**Total:** {len(diaristas)} diarista(s)""",
                        "data": {
                            "total": len(diaristas),
                            "diaristas": [{"id": str(d.id), "nome": d.nome, "status": d.status} for d in diaristas],
                        },
                        "suggestions": ["/diarista disponiveis", "/diarista stats"],
                    }
                else:
                    return {
                        "response": "**Diaristas**\n\nNenhuma diarista ativa encontrada.",
                        "data": {"total": 0},
                        "suggestions": ["/diarista help"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao listar diaristas reais: {e}")

        # Fallback estatico
        return {
            "response": """**Diaristas Ativas**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
| 1 | Maria Silva | limpeza | 4.8 | R$ 180,00 |
| 2 | Ana Souza | faxina | 4.5 | R$ 150,00 |
| 3 | Joana Lima | jardinagem | 4.2 | R$ 200,00 |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "suggestions": ["/diarista disponiveis", "/diarista stats"],
        }

    async def _disponiveis(self, args: list[str], context: dict) -> dict[str, Any]:
        """Diaristas disponiveis para trabalho"""
        from datetime import date, timedelta

        # Parsear data dos args
        data_busca = date.today()
        if args:
            arg = args[0].lower()
            if arg in ("amanha", "amanhã"):
                data_busca = date.today() + timedelta(days=1)
            else:
                try:
                    # Tentar parse dd/mm/yyyy ou yyyy-mm-dd
                    if "/" in arg:
                        parts = arg.split("/")
                        data_busca = date(int(parts[2]), int(parts[1]), int(parts[0]))
                    elif "-" in arg:
                        data_busca = date.fromisoformat(arg)
                except (ValueError, IndexError):
                    pass

        if self.has_data_connector:
            try:
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                disponiveis = await repo.get_available_diarists(data=data_busca)

                if disponiveis:
                    lines = []
                    for i, d in enumerate(disponiveis[:15], 1):
                        tipos = ", ".join(d.tipos_servico or []) or "N/A"
                        avaliacao = f"{float(d.avaliacao_media or 0):.1f}" if d.avaliacao_media else "N/A"
                        valor = f"R$ {float(d.valor_diaria or 0):,.2f}"
                        lines.append(f"| {i} | {d.nome} | {tipos} | {avaliacao} | {valor} |")

                    tabela = "\n".join(lines)
                    return {
                        "response": f"""**Diaristas Disponiveis - {data_busca.strftime("%d/%m/%Y")}**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
{tabela}

**Total:** {len(disponiveis)} disponivel(is)
*Ordenadas por avaliacao (melhor primeiro).*""",
                        "data": {"total": len(disponiveis), "data": data_busca.isoformat()},
                        "suggestions": ["/diarista escalados", "/diarista listar"],
                    }
                else:
                    return {
                        "response": f"**Diaristas Disponiveis - {data_busca.strftime('%d/%m/%Y')}**\n\nNenhuma diarista disponivel.",
                        "data": {"total": 0, "data": data_busca.isoformat()},
                        "suggestions": ["/diarista disponiveis amanha", "/diarista listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar disponiveis: {e}")

        # Fallback estatico
        return {
            "response": f"""**Diaristas Disponiveis - {data_busca.strftime("%d/%m/%Y")}**

| # | Nome | Tipo | Avaliacao | Diaria |
|---|------|------|-----------|--------|
| 1 | Maria Silva | limpeza | 4.8 | R$ 180,00 |
| 2 | Joana Lima | jardinagem | 4.2 | R$ 200,00 |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "data": {"data": data_busca.isoformat()},
            "suggestions": ["/diarista escalados", "/diarista listar"],
        }

    async def _escalados(self, args: list[str], context: dict) -> dict[str, Any]:
        """Diaristas escalados hoje"""
        from datetime import date

        hoje = date.today()

        if self.has_data_connector:
            try:
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                schedules = await repo.get_schedules_by_date(data=hoje)

                if schedules:
                    lines = []
                    for i, s in enumerate(schedules[:20], 1):
                        nome = s.diarist.nome if s.diarist else "N/A"
                        hora_ini = s.hora_inicio.strftime("%H:%M") if s.hora_inicio else "08:00"
                        hora_fim = s.hora_fim.strftime("%H:%M") if s.hora_fim else "17:00"
                        status_str = s.status.value if hasattr(s.status, "value") else str(s.status)
                        checkin = "Sim" if s.checkin_real else "Nao"
                        lines.append(f"| {i} | {nome} | {hora_ini}-{hora_fim} | {status_str} | {checkin} |")

                    tabela = "\n".join(lines)
                    return {
                        "response": f"""**Diaristas Escalados Hoje - {hoje.strftime("%d/%m/%Y")}**

| # | Nome | Horario | Status | Check-in |
|---|------|---------|--------|----------|
{tabela}

**Total:** {len(schedules)} agendamento(s)""",
                        "data": {"total": len(schedules), "data": hoje.isoformat()},
                        "suggestions": ["/diarista disponiveis", "/diarista stats"],
                    }
                else:
                    return {
                        "response": f"**Diaristas Escalados - {hoje.strftime('%d/%m/%Y')}**\n\nNenhum agendamento para hoje.",
                        "data": {"total": 0},
                        "suggestions": ["/diarista disponiveis", "/diarista listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar escalados hoje: {e}")

        # Fallback estatico
        return {
            "response": f"""**Diaristas Escalados Hoje - {hoje.strftime("%d/%m/%Y")}**

| # | Nome | Horario | Status | Check-in |
|---|------|---------|--------|----------|
| 1 | Maria Silva | 08:00-17:00 | CONFIRMADO | Sim |
| 2 | Ana Souza | 08:00-12:00 | AGENDADO | Nao |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "data": {"data": hoje.isoformat()},
            "suggestions": ["/diarista disponiveis", "/diarista stats"],
        }

    async def _stats(self, args: list[str], context: dict) -> dict[str, Any]:
        """Estatisticas de diaristas"""
        if self.has_data_connector:
            try:
                from modules.operacional.diaristas.models.diarist import DiaristStatus
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)

                total_ativos = await repo.count(status=DiaristStatus.ATIVO)
                total_inativos = await repo.count(status=DiaristStatus.INATIVO)
                total_geral = total_ativos + total_inativos

                stats = await repo.get_condominio_statistics()

                top = await repo.get_top_diarists(limit=5)
                top_lines = []
                for i, t in enumerate(top, 1):
                    d = t["diarist"]
                    top_lines.append(f"| {i} | {d.nome} | {t['avaliacao_media']:.1f} | {t['total_servicos']} |")

                top_tabela = "\n".join(top_lines) if top_lines else "| - | Sem dados | - | - |"

                return {
                    "response": f"""**Estatisticas de Diaristas**

**Cadastro:**
- Total: **{total_geral}** | Ativas: **{total_ativos}** | Inativas: **{total_inativos}**

**Ultimos 30 dias:**
- Agendamentos: **{stats.get("agendamentos", {}).get("total", 0)}**
- Concluidos: **{stats.get("agendamentos", {}).get("concluidos", 0)}**
- Taxa conclusao: **{stats.get("agendamentos", {}).get("taxa_conclusao", 0):.1f}%**
- Gastos: **R$ {stats.get("gastos_total", 0):,.2f}**
- Media avaliacoes: **{stats.get("media_avaliacoes", 0):.1f}/5.0**

**Top 5 Diaristas:**

| # | Nome | Avaliacao | Servicos |
|---|------|-----------|----------|
{top_tabela}""",
                    "data": {
                        "total_ativos": total_ativos,
                        "total_inativos": total_inativos,
                        "total_geral": total_geral,
                        "stats": stats,
                    },
                    "suggestions": ["/diarista listar", "/diarista disponiveis"],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar stats: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas de Diaristas**

**Cadastro:**
- Total: **12** | Ativas: **8** | Inativas: **4**

**Ultimos 30 dias:**
- Agendamentos: **45**
- Concluidos: **40**
- Taxa conclusao: **88.9%**
- Gastos: **R$ 7.200,00**
- Media avaliacoes: **4.3/5.0**

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "suggestions": ["/diarista listar", "/diarista disponiveis"],
        }

    async def _avaliar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Iniciar avaliacao de diarista"""
        if not args:
            return {
                "response": """**Avaliar Diarista**

Uso: `/diarista avaliar [diarista_id] [schedule_id]`

- **diarista_id:** ID da diarista (obrigatorio)
- **schedule_id:** ID do agendamento concluido (opcional)

Exemplo: `/diarista avaliar abc123-... def456-...`""",
                "suggestions": ["/diarista listar", "/diarista escalados"],
            }

        diarist_id = args[0]
        schedule_id = args[1] if len(args) > 1 else None

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                diarista = await repo.get_by_id(UUID(diarist_id))

                if not diarista:
                    return {
                        "response": f"**Erro:** Diarista com ID `{diarist_id}` nao encontrada.",
                        "suggestions": ["/diarista listar"],
                    }

                # Verificar avaliacao existente para o schedule
                if schedule_id:
                    try:
                        avaliacao_existente = await repo.get_evaluation_by_schedule(UUID(schedule_id))
                        if avaliacao_existente:
                            return {
                                "response": f"**Avaliacao ja existe** para o agendamento `{schedule_id}` da diarista **{diarista.nome}**.\nNota geral: **{avaliacao_existente.nota_geral}/5**",
                                "suggestions": [f"/diarista avaliacoes {diarist_id}", "/diarista listar"],
                            }
                    except Exception:
                        logger.debug(f"Erro ao verificar avaliacao existente para agendamento {schedule_id}")

                schedule_info = f"\n- **Agendamento:** `{schedule_id}`" if schedule_id else ""
                return {
                    "response": f"""**Avaliar Diarista - {diarista.nome}**

Informe as notas (1 a 5):
- **nota_geral** (obrigatoria)
- **nota_pontualidade** (opcional)
- **nota_qualidade** (opcional)
- **nota_comportamento** (opcional)
- **nota_comunicacao** (opcional)
- **comentario** (opcional)
- **recomendaria** Sim/Nao (padrao: Sim)

**Dados:**
- **Diarista:** {diarista.nome} (ID: `{diarist_id}`){schedule_info}

Confirme os dados para registrar a avaliacao.""",
                    "data": {
                        "diarist_id": diarist_id,
                        "diarist_nome": diarista.nome,
                        "schedule_id": schedule_id,
                    },
                    "suggestions": ["Confirmar", "Cancelar", f"/diarista avaliacoes {diarist_id}"],
                    "actions": [
                        {
                            "type": "create",
                            "label": "Registrar Avaliacao",
                            "target": "diarist_evaluation",
                            "data": {"diarist_id": diarist_id, "schedule_id": schedule_id},
                        }
                    ],
                }
            except Exception as e:
                logger.warning(f"Erro ao preparar avaliacao via skill: {e}")

        return {
            "response": f"**Avaliar Diarista** `{diarist_id}`\n\n*Conecte ao banco para registrar avaliacoes reais.*",
            "suggestions": ["/diarista listar", "/diarista help"],
        }

    async def _avaliacoes(self, args: list[str], context: dict) -> dict[str, Any]:
        """Ver historico de avaliacoes"""
        if not args:
            return {
                "response": """**Avaliacoes de Diarista**

Uso: `/diarista avaliacoes [diarista_id]`

Exemplo: `/diarista avaliacoes abc123-...`""",
                "suggestions": ["/diarista listar"],
            }

        diarist_id = args[0]

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                diarista = await repo.get_by_id(UUID(diarist_id))

                if not diarista:
                    return {
                        "response": f"**Erro:** Diarista com ID `{diarist_id}` nao encontrada.",
                        "suggestions": ["/diarista listar"],
                    }

                avaliacoes = await repo.list_evaluations(diarist_id=diarista.id, limit=20)

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
                        "data": {
                            "diarist_id": diarist_id,
                            "total": len(avaliacoes),
                            "media": float(diarista.avaliacao_media or 0),
                        },
                        "suggestions": [f"/diarista avaliar {diarist_id}", "/diarista listar"],
                    }
                else:
                    return {
                        "response": f"**Avaliacoes - {diarista.nome}**\n\nNenhuma avaliacao encontrada.",
                        "data": {"diarist_id": diarist_id, "total": 0},
                        "suggestions": [f"/diarista avaliar {diarist_id}", "/diarista listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar avaliacoes via skill: {e}")

        return {
            "response": f"**Avaliacoes** de diarista `{diarist_id}`\n\n*Conecte ao banco para dados reais.*",
            "suggestions": ["/diarista listar"],
        }

    async def _pagamento(self, args: list[str], context: dict) -> dict[str, Any]:
        """Subcomando de pagamento: gerar ou aprovar"""
        if not args:
            return {
                "response": """**Pagamento de Diarista**

Subcomandos:
```
/diarista pagamento gerar [diarista_id] [periodo]   - Gerar pagamento
/diarista pagamento aprovar [pagamento_id]           - Aprovar pagamento
```

Exemplo:
- `/diarista pagamento gerar abc123-... 2026-01`
- `/diarista pagamento aprovar def456-...`""",
                "suggestions": ["/diarista pagamentos", "/diarista listar"],
            }

        subcommand = args[0].lower()
        sub_args = args[1:]

        if subcommand == "gerar":
            return await self._pagamento_gerar(sub_args, context)
        elif subcommand == "aprovar":
            return await self._pagamento_aprovar(sub_args, context)
        else:
            return {
                "response": f"Subcomando '{subcommand}' nao reconhecido. Use `gerar` ou `aprovar`.",
                "suggestions": ["/diarista pagamento gerar", "/diarista pagamento aprovar"],
            }

    async def _pagamento_gerar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Gerar pagamento para diarista em periodo"""
        from datetime import date, timedelta

        if not args:
            return {
                "response": """**Gerar Pagamento**

Uso: `/diarista pagamento gerar [diarista_id] [periodo]`
- **periodo:** YYYY-MM (padrao: mes atual)

Exemplo: `/diarista pagamento gerar abc123-... 2026-01`""",
                "suggestions": ["/diarista listar", "/diarista pagamentos"],
            }

        diarist_id = args[0]
        from datetime import datetime as dt

        periodo = args[1] if len(args) > 1 else dt.now().strftime("%Y-%m")

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                diarista = await repo.get_by_id(UUID(diarist_id))

                if not diarista:
                    return {
                        "response": f"**Erro:** Diarista com ID `{diarist_id}` nao encontrada.",
                        "suggestions": ["/diarista listar"],
                    }

                # Periodo
                ano, mes = periodo.split("-")
                data_inicio = date(int(ano), int(mes), 1)
                if int(mes) == 12:
                    data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
                else:
                    data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)

                # Buscar schedules concluidos
                schedules = await repo.list_schedules(
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

                # Retencoes estimadas
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
                    "suggestions": ["Confirmar", "Cancelar", f"/diarista pagamentos {diarist_id}"],
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
                logger.warning(f"Erro ao gerar pagamento via skill: {e}")

        return {
            "response": f"**Gerar Pagamento** para diarista `{diarist_id}` periodo `{periodo}`\n\n*Conecte ao banco para dados reais.*",
            "suggestions": ["/diarista listar"],
        }

    async def _pagamento_aprovar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Aprovar pagamento pendente"""
        if not args:
            return {
                "response": """**Aprovar Pagamento**

Uso: `/diarista pagamento aprovar [pagamento_id]`

Exemplo: `/diarista pagamento aprovar abc123-...`""",
                "suggestions": ["/diarista pagamentos", "/diarista help"],
            }

        pagamento_id = args[0]

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)
                pagamento = await repo.get_payment_by_id(UUID(pagamento_id))

                if not pagamento:
                    return {
                        "response": f"**Erro:** Pagamento com ID `{pagamento_id}` nao encontrado.",
                        "suggestions": ["/diarista pagamentos"],
                    }

                status_str = (
                    pagamento.status
                    if isinstance(pagamento.status, str)
                    else (pagamento.status.value if hasattr(pagamento.status, "value") else str(pagamento.status))
                )
                nome = pagamento.diarist.nome if pagamento.diarist else "N/A"

                if status_str != "PENDENTE":
                    return {
                        "response": f"**Pagamento** para **{nome}** nao pode ser aprovado.\nStatus atual: **{status_str}** (precisa estar PENDENTE).",
                        "suggestions": ["/diarista pagamentos pendentes"],
                    }

                bruto = float(pagamento.valor_bruto or 0)
                liquido = float(pagamento.valor_liquido or 0)
                ref = pagamento.data_referencia.strftime("%m/%Y") if pagamento.data_referencia else "N/A"

                return {
                    "response": f"""**Aprovar Pagamento**

**Diarista:** {nome}
**Referencia:** {ref}
**Valor bruto:** R$ {bruto:,.2f}
**Valor liquido:** R$ {liquido:,.2f}

Confirme para aprovar.""",
                    "data": {"pagamento_id": pagamento_id, "diarist_nome": nome},
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
            except Exception as e:
                logger.warning(f"Erro ao aprovar pagamento via skill: {e}")

        return {
            "response": f"**Aprovar Pagamento** `{pagamento_id}`\n\n*Conecte ao banco para dados reais.*",
            "suggestions": ["/diarista pagamentos"],
        }

    async def _pagamentos(self, args: list[str], context: dict) -> dict[str, Any]:
        """Listar pagamentos de diaristas"""
        diarist_id = args[0] if args else None
        status_filtro = None

        # Detectar filtro de status nos args
        for arg in args:
            arg_lower = arg.lower()
            if arg_lower in ("pendente", "pendentes"):
                status_filtro = "PENDENTE"
            elif arg_lower in ("pago", "pagos", "realizado", "realizados"):
                status_filtro = "PAGO"
            elif arg_lower in ("aprovado", "aprovados"):
                status_filtro = "APROVADO"

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.models.diarist import PaymentStatus
                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)

                diarist_uuid = None
                if diarist_id and not status_filtro:
                    # Verificar se o primeiro arg eh UUID ou filtro de status
                    try:
                        diarist_uuid = UUID(diarist_id)
                    except ValueError:
                        # Nao eh UUID, pode ser filtro
                        if diarist_id.lower() in ("pendente", "pendentes"):
                            status_filtro = "PENDENTE"
                        elif diarist_id.lower() in ("pago", "pagos"):
                            status_filtro = "PAGO"
                        elif diarist_id.lower() in ("aprovado", "aprovados"):
                            status_filtro = "APROVADO"

                status_enum = None
                if status_filtro:
                    with contextlib.suppress(ValueError):
                        status_enum = PaymentStatus(status_filtro)

                pagamentos = await repo.list_payments(
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
                        "data": {"total": len(pagamentos), "total_bruto": total_bruto, "total_liquido": total_liquido},
                        "suggestions": ["/diarista pagamento gerar", "/diarista pagamento aprovar", "/diarista stats"],
                    }
                else:
                    return {
                        "response": f"**Pagamentos{' (' + status_filtro + ')' if status_filtro else ''}**\n\nNenhum pagamento encontrado.",
                        "data": {"total": 0},
                        "suggestions": ["/diarista pagamento gerar", "/diarista listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao listar pagamentos via skill: {e}")

        return {
            "response": """**Pagamentos de Diaristas**

| # | Diarista | Ref. | Bruto | Liquido | Status | Venc. |
|---|----------|------|-------|---------|--------|-------|
| 1 | Maria Silva | 01/2026 | R$ 3.600,00 | R$ 2.844,00 | PENDENTE | 05/02 |
| 2 | Ana Souza | 01/2026 | R$ 2.400,00 | R$ 1.896,00 | PAGO | 05/02 |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "suggestions": ["/diarista pagamento gerar", "/diarista stats"],
        }

    async def _agenda(self, args: list[str], context: dict) -> dict[str, Any]:
        """Ver agenda detalhada com check-ins/outs e status"""
        from datetime import date, timedelta

        diarist_id = args[0] if args else None
        periodo = args[1] if len(args) > 1 else None

        hoje = date.today()

        # Parsear periodo
        if periodo:
            try:
                if len(periodo) == 7 and "-" in periodo:
                    # YYYY-MM
                    ano, mes = periodo.split("-")
                    data_inicio = date(int(ano), int(mes), 1)
                    if int(mes) == 12:
                        data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
                    else:
                        data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)
                    periodo_label = periodo
                elif periodo.lower() == "semana":
                    data_inicio = hoje - timedelta(days=hoje.weekday())
                    data_fim = data_inicio + timedelta(days=6)
                    periodo_label = f"Semana {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"
                elif periodo.lower() == "mes":
                    data_inicio = date(hoje.year, hoje.month, 1)
                    if hoje.month == 12:
                        data_fim = date(hoje.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        data_fim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
                    periodo_label = f"{hoje.strftime('%m/%Y')}"
                else:
                    data_inicio = hoje - timedelta(days=7)
                    data_fim = hoje
                    periodo_label = f"{data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"
            except (ValueError, IndexError):
                data_inicio = hoje - timedelta(days=7)
                data_fim = hoje
                periodo_label = f"{data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"
        else:
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje
            periodo_label = f"{data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m/%Y')}"

        if self.has_data_connector:
            try:
                from uuid import UUID

                from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository

                repo = DiaristRepository(self.data_connector.db)

                diarist_uuid = None
                if diarist_id:
                    try:
                        diarist_uuid = UUID(diarist_id)
                    except ValueError:
                        # Nao eh UUID, talvez seja periodo
                        if diarist_id.lower() in ("semana", "mes") or "-" in diarist_id:
                            # Re-parsear como periodo
                            pass

                schedules = await repo.list_schedules(
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

                    return {
                        "response": f"""**Agenda Detalhada - {periodo_label}**

| # | Diarista | Data | Horario | Check-in | Check-out | Duracao | Status |
|---|----------|------|---------|----------|-----------|---------|--------|
{tabela}

**Resumo:** {len(schedules)} agendamento(s) | {total_concluidos} concluido(s) | {total_faltas} falta(s)""",
                        "data": {"total": len(schedules), "concluidos": total_concluidos, "faltas": total_faltas},
                        "suggestions": ["/diarista escalados", "/diarista stats", "/diarista avaliar"],
                    }
                else:
                    return {
                        "response": f"**Agenda Detalhada - {periodo_label}**\n\nNenhum agendamento encontrado.",
                        "data": {"total": 0},
                        "suggestions": ["/diarista escalados", "/diarista disponiveis"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar agenda via skill: {e}")

        return {
            "response": f"""**Agenda Detalhada - {periodo_label}**

| # | Diarista | Data | Horario | Check-in | Check-out | Duracao | Status |
|---|----------|------|---------|----------|-----------|---------|--------|
| 1 | Maria Silva | {hoje.strftime("%d/%m")} | 08:00-17:00 | 07:55 | 17:10 | 9h15 | CONCLUIDO |
| 2 | Ana Souza | {hoje.strftime("%d/%m")} | 08:00-12:00 | 08:10 | - | - | EM_ANDAMENTO |

*Dados ilustrativos - conecte ao banco para dados reais.*""",
            "suggestions": ["/diarista escalados", "/diarista stats"],
        }

    def get_help(self) -> str:
        return """**Skill /diarista**

**Comandos disponiveis:**
```
/diarista listar [busca]                             - Lista diaristas ativas
/diarista disponiveis [data]                         - Disponiveis para trabalho
/diarista escalados                                  - Escalados hoje
/diarista stats                                      - Estatisticas gerais
/diarista avaliar [diarista_id] [schedule_id]        - Iniciar avaliacao
/diarista avaliacoes [diarista_id]                   - Ver historico de avaliacoes
/diarista pagamento gerar [diarista_id] [periodo]    - Gerar pagamento
/diarista pagamento aprovar [pagamento_id]           - Aprovar pagamento
/diarista pagamentos [diarista_id|status]            - Listar pagamentos
/diarista agenda [diarista_id] [periodo]             - Ver agenda detalhada
/diarista help                                       - Esta ajuda
```

**Exemplos:**
- `/diarista listar`
- `/diarista listar Maria`
- `/diarista disponiveis`
- `/diarista disponiveis amanha`
- `/diarista disponiveis 15/02/2026`
- `/diarista escalados`
- `/diarista stats`
- `/diarista avaliar abc123-def456-... ghi789-...`
- `/diarista avaliacoes abc123-def456-...`
- `/diarista pagamento gerar abc123-... 2026-01`
- `/diarista pagamento aprovar def456-...`
- `/diarista pagamentos pendentes`
- `/diarista pagamentos abc123-...`
- `/diarista agenda abc123-... semana`
- `/diarista agenda abc123-... 2026-01`"""
