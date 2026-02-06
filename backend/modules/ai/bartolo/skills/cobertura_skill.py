"""
Skill /cobertura - Analise de cobertura de postos
Skill /relatorio - Relatorios operacionais avancados
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class CoberturaSkill(BaseSkill):
    """Skill para analise de cobertura e relatorios avancados"""

    name = "cobertura"
    description = "Analise de cobertura de postos e relatorios operacionais"
    commands = [
        "", "critica", "hoje", "semana", "help",
        # Relatorios avancados
        "relatorio",
    ]

    # Subcomandos de relatorio validos
    REPORT_TYPES = [
        "horas_extras", "custos", "banco_horas", "substituicoes",
        "disciplinar", "ocorrencias", "diaristas", "rondas",
    ]

    def __init__(self, data_connector: Optional["DataConnector"] = None, db=None):
        super().__init__(data_connector=data_connector)
        self.db = db

    async def execute(self, command: str, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        if not command or command == "help":
            return await self._visao_geral(context)

        # Roteamento para relatorios avancados
        if command == "relatorio":
            return await self._relatorio_dispatch(args, context)

        handlers = {
            "critica": self._critica,
            "hoje": self._hoje,
            "semana": self._semana,
        }

        handler = handlers.get(command, self._posto_especifico)
        return await handler(args if args else [command], context)

    async def _visao_geral(self, context: Dict) -> Dict[str, Any]:
        """Visao geral da cobertura - usa dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                # Buscar operacao geral para taxa de cobertura
                op_result = await self.data_connector._get_operacao_geral()
                # Buscar postos criticos
                crit_result = await self.data_connector._get_cobertura_critica()

                if op_result.success and op_result.data:
                    op = op_result.data
                    taxa = op.get("taxa_cobertura", 0)
                    postos_total = op.get("postos_total", 0)
                    postos_vagas = op.get("postos_com_vagas", 0)
                    postos_ok = postos_total - postos_vagas
                    efetivo_aloc = op.get("efetivo_alocado", 0)
                    efetivo_req = op.get("efetivo_requerido", 0)

                    # Classificar postos
                    criticos = 0
                    atencao = 0
                    ok = 0
                    linhas_criticos = []

                    if crit_result.success and crit_result.data:
                        criticos = crit_result.total_count
                        for p in crit_result.data[:5]:
                            linhas_criticos.append(
                                f"- {p.get('nome', 'N/A')} ({p.get('codigo', '')}): {p.get('cobertura', 0)}%"
                            )

                    # Estima atencao e ok
                    if postos_total > 0:
                        ok = postos_ok - criticos
                        if ok < 0:
                            ok = 0

                    pct_ok = round((ok / postos_total) * 100) if postos_total > 0 else 0
                    pct_crit = round((criticos / postos_total) * 100) if postos_total > 0 else 0

                    criticos_text = ""
                    if linhas_criticos:
                        criticos_text = "\n\n**Postos criticos:**\n" + "\n".join(linhas_criticos)

                    return {
                        "response": f"""**Cobertura Geral** (Dados Reais)

| Status | Postos | % |
|--------|--------|---|
| [OK] OK (>90%) | {ok} | {pct_ok}% |
| [X] Critico (<80%) | {criticos} | {pct_crit}% |

**Cobertura media: {taxa}%**
**Efetivo:** {efetivo_aloc}/{efetivo_req}{criticos_text}""",
                        "data": {"media": taxa, "criticos": criticos, "total_postos": postos_total},
                        "suggestions": ["/cobertura critica", "/cobertura hoje", "/cobertura semana"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura geral real: {e}")

        # Fallback estatico
        return {
            "response": """**Cobertura Geral**

| Status | Postos | % |
|--------|--------|---|
| [OK] OK (>90%) | 6 | 60% |
| [!] Atencao (80-90%) | 2 | 20% |
| [X] Critico (<80%) | 2 | 20% |

**Cobertura media: 87.5%**

**Postos criticos:**
- Centro-001: 45%
- Norte-003: 75%""",
            "data": {"media": 87.5, "criticos": 2},
            "suggestions": ["/cobertura critica", "/cobertura hoje", "/cobertura Centro-001"],
        }

    async def _critica(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Postos com cobertura critica - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": {
                            "postos_criticos": result.data,
                            "total": result.total_count,
                        },
                    }
                    # Sugestoes baseadas nos postos criticos
                    suggestions = []
                    if result.data:
                        for p in result.data[:2]:
                            nome = p.get("nome", "")
                            if nome:
                                suggestions.append(f"Buscar substituto {nome}")
                    suggestions.append("Ver funcionarios disponiveis")
                    response_data["suggestions"] = suggestions
                    return response_data
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura critica real: {e}")

        # Fallback estatico
        return {
            "response": """**[X] Postos com Cobertura Critica (<80%)**

| Posto | Cobertura | Faltam | Acao |
|-------|-----------|--------|------|
| Centro-001 | 45% | 2 func | URGENTE |
| Norte-003 | 75% | 1 func | Alocar |

**Acoes sugeridas:**
1. Buscar substituto para Centro-001
2. Redistribuir turno para Norte-003""",
            "suggestions": ["Buscar substituto Centro-001", "Ver funcionarios disponiveis"],
        }

    async def _hoje(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Cobertura de hoje - dados reais quando disponivel"""

        if self.has_data_connector:
            try:
                # Usa operacao geral para dados de hoje
                result = await self.data_connector._get_operacao_geral()
                if result.success and result.data:
                    op = result.data
                    taxa = op.get("taxa_cobertura", 0)
                    turnos = op.get("turnos_hoje", 0)
                    status_icon = op.get("status_icon", "")
                    status = op.get("status", "OK")

                    return {
                        "response": f"""**Cobertura de Hoje** (Dados Reais)

**Taxa de cobertura atual:** {taxa}% {status_icon} {status}

**Turnos programados hoje:** {turnos}
**Efetivo:** {op.get('efetivo_alocado', 0)}/{op.get('efetivo_requerido', 0)}

_Para detalhes por turno, consulte o modulo de escalas._""",
                        "data": {"taxa": taxa, "turnos": turnos},
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura hoje real: {e}")

        # Fallback estatico
        return {
            "response": """**Cobertura de Hoje**

**Manha (06:00-14:00):** 92%
**Tarde (14:00-22:00):** 88%
**Noite (22:00-06:00):** 95%

**Media do dia: 91.7%** [OK]""",
        }

    async def _semana(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Projecao semanal - estatico por enquanto (requer dados historicos)"""
        return {
            "response": """**Projecao da Semana**

| Dia | Projecao | Status |
|-----|----------|--------|
| Seg | 95% | [OK] |
| Ter | 92% | [OK] |
| Qua | 88% | [!] |
| Qui | 90% | [OK] |
| Sex | 85% | [!] |
| Sab | 78% | [X] |
| Dom | 80% | [!] |

[!] **Atencao:** Sabado com cobertura critica""",
        }

    async def _posto_especifico(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Cobertura de posto especifico"""
        posto = args[0] if args else "desconhecido"

        # Se temos data_connector, tenta buscar dados criticos e ver se o posto esta la
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success and result.data:
                    # Procurar o posto nos dados
                    for p in result.data:
                        nome = p.get("nome", "").lower()
                        codigo = p.get("codigo", "").lower()
                        if posto.lower() in nome or posto.lower() == codigo:
                            cobertura = p.get("cobertura", 0)
                            alocados = p.get("alocados", 0)
                            requeridos = p.get("requeridos", 0)
                            deficit = p.get("deficit", 0)

                            return {
                                "response": f"""**Cobertura do Posto {p.get('nome', posto)}** ({p.get('codigo', '')})

**Atual:** {cobertura}% [{'X' if cobertura < 80 else '!' if cobertura < 90 else 'OK'}]
**Necessario:** {requeridos} funcionarios
**Alocados:** {alocados} funcionarios
**Deficit:** {deficit}

**Acao recomendada:** {'URGENTE - Buscar substituto' if cobertura < 80 else 'Alocar funcionario adicional'}""",
                                "suggestions": [f"Buscar substituto {posto}", "Ver funcionarios disponiveis"],
                            }
            except Exception as e:
                logger.warning(f"Erro ao buscar posto especifico real: {e}")

        # Fallback estatico
        return {
            "response": f"""**Cobertura do Posto {posto}**

**Atual:** 85%
**Necessario:** 3 funcionarios
**Alocados:** 2 funcionarios + 1 folga

**Turnos:**
- 06:00-14:00: Joao Silva [OK]
- 14:00-22:00: Maria Santos [OK]
- 22:00-06:00: VAGO [X]""",
            "suggestions": ["Buscar substituto noturno", "Ver historico"],
        }

    # ==================================================================
    # RELATORIOS AVANCADOS
    # ==================================================================

    def _parse_periodo(self, args: List[str], offset: int = 0) -> tuple:
        """Extrai periodo dos argumentos. Retorna (start_date, end_date, label)."""
        periodo = args[offset].lower() if len(args) > offset else "mes"
        today = date.today()

        if periodo in ("hoje", "dia"):
            return today, today, "Hoje"
        elif periodo in ("semana", "semanal"):
            start = today - timedelta(days=today.weekday())
            return start, today, "Semana atual"
        elif periodo in ("mes", "mensal"):
            start = today.replace(day=1)
            return start, today, f"{today.strftime('%m/%Y')}"
        elif periodo in ("trimestre", "trimestral"):
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_start_month, day=1)
            return start, today, f"Trimestre {((today.month - 1) // 3) + 1}/{today.year}"
        else:
            # Tenta parsear como mes/ano ou assume mes atual
            start = today.replace(day=1)
            return start, today, f"{today.strftime('%m/%Y')}"

    async def _relatorio_dispatch(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Roteamento dos relatorios avancados."""
        if not args:
            return {
                "response": self._get_relatorio_help(),
                "suggestions": [
                    "/relatorio horas_extras",
                    "/relatorio custos",
                    "/relatorio ocorrencias",
                    "/relatorio rondas",
                ],
            }

        tipo = args[0].lower()
        sub_args = args[1:]

        report_handlers = {
            "horas_extras": self._relatorio_horas_extras,
            "custos": self._relatorio_custos,
            "banco_horas": self._relatorio_banco_horas,
            "substituicoes": self._relatorio_substituicoes,
            "disciplinar": self._relatorio_disciplinar,
            "ocorrencias": self._relatorio_ocorrencias,
            "diaristas": self._relatorio_diaristas,
            "rondas": self._relatorio_rondas,
        }

        handler = report_handlers.get(tipo)
        if handler:
            return await handler(sub_args, context)

        return {
            "response": f"Tipo de relatorio '{tipo}' nao reconhecido.\n\n{self._get_relatorio_help()}",
            "suggestions": [f"/relatorio {t}" for t in self.REPORT_TYPES[:4]],
        }

    def _get_relatorio_help(self) -> str:
        """Texto de ajuda dos relatorios."""
        return """**Relatorios Disponiveis:**
```
/relatorio horas_extras [periodo] [posto]  - Horas extras
/relatorio custos [periodo] [posto]        - Custos detalhados
/relatorio banco_horas [funcionario]       - Banco de horas
/relatorio substituicoes [periodo]         - Substituicoes
/relatorio disciplinar [periodo]           - Medidas disciplinares
/relatorio ocorrencias [periodo] [sev]     - Ocorrencias
/relatorio diaristas [periodo]             - Diaristas
/relatorio rondas [periodo]                - Rondas de inspecao
```
**Periodos:** hoje, semana, mes (padrao), trimestre"""

    async def _relatorio_horas_extras(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de horas extras."""
        start_date, end_date, label = self._parse_periodo(args)
        posto_filtro = args[1] if len(args) > 1 else None

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.repositories.reports_repository import ReportsRepository
                repo = ReportsRepository(self.db)
                data = await repo.get_hours(start_date, end_date)

                if data:
                    total_he = sum(d.get("overtime_hours", 0) for d in data)
                    total_turnos = sum(d.get("total_shifts", 0) for d in data)
                    total_horas = sum(d.get("total_hours", 0) for d in data)

                    # Top 10 por HE
                    sorted_data = sorted(data, key=lambda x: x.get("overtime_hours", 0), reverse=True)
                    top_10 = sorted_data[:10]

                    lines = []
                    for idx, d in enumerate(top_10, 1):
                        emp_id = d.get("employee_id", "N/A")[:8]
                        he = d.get("overtime_hours", 0)
                        turnos = d.get("total_shifts", 0)
                        lines.append(f"| {idx} | {emp_id}... | {turnos} | {he:.1f}h |")

                    table_rows = "\n".join(lines) if lines else "| - | Nenhum registro | - | - |"

                    return {
                        "response": f"""**RELATORIO DE HORAS EXTRAS** - {label}
Periodo: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}

**Resumo:**
| Indicador | Valor |
|-----------|-------|
| Total de Turnos | {total_turnos} |
| Total de Horas | {total_horas:.1f}h |
| Total Horas Extras | {total_he:.1f}h |
| Funcionarios com HE | {len([d for d in data if d.get('overtime_hours', 0) > 0])} |

**Top 10 - Mais Horas Extras:**

| # | Funcionario | Turnos | HE |
|---|-------------|--------|----|
{table_rows}

{'**ALERTA:** Horas extras acima de 200h no periodo!' if total_he > 200 else ''}""",
                        "data": {"total_he": total_he, "total_turnos": total_turnos, "periodo": label},
                        "suggestions": ["/relatorio custos", "/relatorio banco_horas", "/relatorio substituicoes"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de horas extras: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE HORAS EXTRAS** - {label}

| Indicador | Valor |
|-----------|-------|
| Total de Turnos | 320 |
| Total de Horas | 2.560h |
| Total Horas Extras | 186h |
| Funcionarios com HE | 15 |

**Top 5:**
1. Funcionario A - 32h extras
2. Funcionario B - 28h extras
3. Funcionario C - 22h extras
4. Funcionario D - 18h extras
5. Funcionario E - 15h extras

_Dados ilustrativos. Conecte ao banco para dados reais._""",
            "suggestions": ["/relatorio custos", "/relatorio banco_horas"],
        }

    async def _relatorio_custos(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de custos detalhados."""
        start_date, end_date, label = self._parse_periodo(args)
        posto_filtro = args[1] if len(args) > 1 else None

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.repositories.reports_repository import ReportsRepository
                repo = ReportsRepository(self.db)
                data = await repo.get_costs(start_date, end_date, post_id=posto_filtro)

                if data:
                    total_custo = sum(d.get("total_cost", 0) for d in data)
                    total_turnos = sum(d.get("total_shifts", 0) for d in data)

                    # Ordenar por custo desc
                    sorted_data = sorted(data, key=lambda x: x.get("total_cost", 0), reverse=True)

                    lines = []
                    for d in sorted_data[:10]:
                        nome = d.get("post_name", "N/A")
                        custo = d.get("total_cost", 0)
                        turnos = d.get("total_shifts", 0)
                        lines.append(f"| {nome[:25]} | {turnos} | R$ {custo:,.2f} |")

                    table_rows = "\n".join(lines) if lines else "| - | - | - |"

                    return {
                        "response": f"""**RELATORIO DE CUSTOS** - {label}
Periodo: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}

**Total Geral:** R$ {total_custo:,.2f}
**Total de Turnos:** {total_turnos}
**Custo Medio por Turno:** R$ {(total_custo / total_turnos if total_turnos > 0 else 0):,.2f}

**Custos por Posto (Top 10):**

| Posto | Turnos | Custo |
|-------|--------|-------|
{table_rows}""",
                        "data": {"total_custo": total_custo, "total_turnos": total_turnos, "periodo": label},
                        "suggestions": ["/relatorio horas_extras", "/relatorio diaristas"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de custos: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE CUSTOS** - {label}

**Total Geral:** R$ 45.230,00
**Total de Turnos:** 320
**Custo Medio por Turno:** R$ 141,34

**Top 5 Postos:**
1. Portaria Central - R$ 12.500,00
2. Recepcao Bloco A - R$ 8.300,00
3. Guarita Norte - R$ 7.200,00
4. Portaria Servico - R$ 6.800,00
5. Ronda Perimetral - R$ 5.430,00

_Dados ilustrativos._""",
            "suggestions": ["/relatorio horas_extras", "/relatorio diaristas"],
        }

    async def _relatorio_banco_horas(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de banco de horas."""
        funcionario_filtro = args[0] if args else None

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.repositories import TimeBankRepository
                repo = TimeBankRepository(self.db)

                if funcionario_filtro:
                    # Busca saldo individual
                    try:
                        entries, total = await repo.list(page=1, page_size=50)
                        # Filtra pelo nome/id do funcionario
                        filtered = [
                            e for e in entries
                            if funcionario_filtro.lower() in str(getattr(e, 'employee_name', '')).lower()
                            or funcionario_filtro.lower() in str(getattr(e, 'employee_id', '')).lower()
                        ]
                        if filtered:
                            lines = []
                            for e in filtered[:10]:
                                nome = getattr(e, 'employee_name', 'N/A')
                                saldo = getattr(e, 'balance_hours', 0)
                                lines.append(f"- **{nome}**: {saldo:+.1f}h")

                            return {
                                "response": f"""**BANCO DE HORAS** - Funcionario: {funcionario_filtro}

{chr(10).join(lines)}

_Saldo positivo = credito | Saldo negativo = debito_""",
                                "data": {"filtro": funcionario_filtro, "resultados": len(filtered)},
                                "suggestions": ["/relatorio horas_extras", "/relatorio banco_horas"],
                            }
                    except Exception:
                        pass

                # Listagem geral
                entries, total = await repo.list(page=1, page_size=20)
                if entries:
                    positivos = 0
                    negativos = 0
                    lines = []
                    for e in entries[:15]:
                        nome = getattr(e, 'employee_name', 'N/A')
                        saldo = getattr(e, 'balance_hours', 0)
                        icon = "+" if saldo >= 0 else "-"
                        if saldo >= 0:
                            positivos += 1
                        else:
                            negativos += 1
                        lines.append(f"| {nome[:25]} | {saldo:+.1f}h | {'Credito' if saldo >= 0 else 'Debito'} |")

                    return {
                        "response": f"""**RELATORIO DE BANCO DE HORAS**

**Resumo:** {total} funcionarios | {positivos} com credito | {negativos} com debito

| Funcionario | Saldo | Status |
|-------------|-------|--------|
{chr(10).join(lines)}

{'*Exibindo os primeiros 15 registros.*' if total > 15 else ''}""",
                        "data": {"total": total, "positivos": positivos, "negativos": negativos},
                        "suggestions": ["/relatorio horas_extras", "/relatorio substituicoes"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de banco de horas: {e}")

        # Fallback estatico
        return {
            "response": """**RELATORIO DE BANCO DE HORAS**

| Funcionario | Saldo | Status |
|-------------|-------|--------|
| Joao Silva | +12.5h | Credito |
| Maria Santos | -3.0h | Debito |
| Carlos Lima | +8.0h | Credito |
| Ana Souza | +2.5h | Credito |
| Pedro Costa | -6.0h | Debito |

**Resumo:** 5 funcionarios | 3 com credito | 2 com debito

_Dados ilustrativos._""",
            "suggestions": ["/relatorio horas_extras", "/relatorio substituicoes"],
        }

    async def _relatorio_substituicoes(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de substituicoes."""
        start_date, end_date, label = self._parse_periodo(args)

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.repositories import SubstitutionRepository
                repo = SubstitutionRepository(self.db)
                entries, total = await repo.list(page=1, page_size=50)

                if entries:
                    pendentes = sum(1 for e in entries if getattr(e, 'status', '') in ('pending', 'pendente'))
                    aprovadas = sum(1 for e in entries if getattr(e, 'status', '') in ('approved', 'aprovada'))
                    rejeitadas = sum(1 for e in entries if getattr(e, 'status', '') in ('rejected', 'rejeitada'))
                    concluidas = sum(1 for e in entries if getattr(e, 'status', '') in ('completed', 'concluida'))

                    lines = []
                    for e in entries[:10]:
                        emp_name = getattr(e, 'employee_name', 'N/A')
                        sub_name = getattr(e, 'substitute_name', 'N/A')
                        status = getattr(e, 'status', 'N/A')
                        dt = getattr(e, 'date', 'N/A')
                        lines.append(f"| {emp_name[:15]} | {sub_name[:15]} | {status} | {dt} |")

                    return {
                        "response": f"""**RELATORIO DE SUBSTITUICOES** - {label}

**Resumo:**
| Status | Qtd |
|--------|-----|
| Pendentes | {pendentes} |
| Aprovadas | {aprovadas} |
| Rejeitadas | {rejeitadas} |
| Concluidas | {concluidas} |
| **Total** | **{total}** |

**Ultimas Substituicoes:**

| Titular | Substituto | Status | Data |
|---------|-----------|--------|------|
{chr(10).join(lines)}""",
                        "data": {"total": total, "pendentes": pendentes, "periodo": label},
                        "suggestions": ["/relatorio horas_extras", "/relatorio custos"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de substituicoes: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE SUBSTITUICOES** - {label}

| Status | Qtd |
|--------|-----|
| Pendentes | 3 |
| Aprovadas | 8 |
| Rejeitadas | 1 |
| Concluidas | 22 |
| **Total** | **34** |

_Dados ilustrativos._""",
            "suggestions": ["/relatorio horas_extras", "/relatorio custos"],
        }

    async def _relatorio_disciplinar(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de medidas disciplinares."""
        start_date, end_date, label = self._parse_periodo(args)

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository
                repo = DisciplinaryRepository(self.db)
                entries, total = await repo.list(page=1, page_size=50)

                if entries:
                    por_tipo: Dict[str, int] = {}
                    por_status: Dict[str, int] = {}
                    for e in entries:
                        tipo = getattr(e, 'action_type', 'outros')
                        status = getattr(e, 'status', 'desconhecido')
                        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
                        por_status[status] = por_status.get(status, 0) + 1

                    tipo_lines = [f"| {t.replace('_', ' ').title()} | {c} |" for t, c in sorted(por_tipo.items(), key=lambda x: x[1], reverse=True)]
                    status_lines = [f"| {s.replace('_', ' ').title()} | {c} |" for s, c in sorted(por_status.items(), key=lambda x: x[1], reverse=True)]

                    return {
                        "response": f"""**RELATORIO DISCIPLINAR** - {label}

**Total de Medidas:** {total}

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
{chr(10).join(tipo_lines)}

**Por Status:**
| Status | Qtd |
|--------|-----|
{chr(10).join(status_lines)}""",
                        "data": {"total": total, "por_tipo": por_tipo, "periodo": label},
                        "suggestions": ["/relatorio ocorrencias", "/relatorio substituicoes"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio disciplinar: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DISCIPLINAR** - {label}

**Total:** 12 medidas

**Por Tipo:**
| Tipo | Qtd |
|------|-----|
| Advertencia Verbal | 5 |
| Advertencia Escrita | 4 |
| Suspensao | 2 |
| Demissao | 1 |

_Dados ilustrativos._""",
            "suggestions": ["/relatorio ocorrencias", "/relatorio substituicoes"],
        }

    async def _relatorio_ocorrencias(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de ocorrencias com filtro de severidade."""
        start_date, end_date, label = self._parse_periodo(args)
        severidade_filtro = args[1].lower() if len(args) > 1 else None

        if self.has_data_connector and self.db:
            try:
                from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
                repo = OccurrenceRepository(self.db)
                stats = await repo.get_stats()

                if stats.total > 0:
                    sev_icons = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}
                    sev_lines = []
                    for sev in ["gravissima", "grave", "moderada", "leve"]:
                        count = stats.by_severity.get(sev, 0)
                        if count > 0:
                            sev_lines.append(f"| {sev_icons.get(sev, '')} {sev.title()} | {count} |")

                    tipo_lines = []
                    sorted_types = sorted(stats.by_type.items(), key=lambda x: x[1], reverse=True)
                    for tipo, count in sorted_types[:8]:
                        tipo_label = tipo.replace("_", " ").title()
                        tipo_lines.append(f"| {tipo_label} | {count} |")

                    cat_lines = []
                    sorted_cats = sorted(stats.by_category.items(), key=lambda x: x[1], reverse=True)
                    for cat, count in sorted_cats:
                        cat_label = cat.replace("_", " ").title()
                        cat_lines.append(f"| {cat_label} | {count} |")

                    avg_time = f"{stats.avg_resolution_time_hours:.1f}h" if stats.avg_resolution_time_hours else "N/A"
                    taxa_resolucao = (stats.resolved / stats.total * 100) if stats.total > 0 else 0

                    return {
                        "response": f"""**RELATORIO DE OCORRENCIAS** - {label}
{f'Filtro de severidade: {severidade_filtro}' if severidade_filtro else ''}

**Indicadores Gerais:**
| Indicador | Valor |
|-----------|-------|
| Total | {stats.total} |
| Abertas | {stats.open} |
| Em Analise | {stats.in_analysis} |
| Resolvidas | {stats.resolved} |
| Graves/Gravissimas | {stats.severe} {'🚨' if stats.severe > 0 else ''} |
| Taxa de Resolucao | {taxa_resolucao:.1f}% |
| Tempo Medio Resolucao | {avg_time} |

**Por Severidade:**
| Severidade | Qtd |
|------------|-----|
{chr(10).join(sev_lines) if sev_lines else '| Nenhum dado | - |'}

**Por Tipo (Top 8):**
| Tipo | Qtd |
|------|-----|
{chr(10).join(tipo_lines) if tipo_lines else '| Nenhum dado | - |'}

**Por Categoria:**
| Categoria | Qtd |
|-----------|-----|
{chr(10).join(cat_lines) if cat_lines else '| Nenhum dado | - |'}""",
                        "data": {
                            "total": stats.total,
                            "abertas": stats.open,
                            "graves": stats.severe,
                            "taxa_resolucao": taxa_resolucao,
                            "periodo": label,
                        },
                        "suggestions": ["/relatorio disciplinar", "/relatorio rondas", "/ocorrencia stats"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de ocorrencias: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE OCORRENCIAS** - {label}

| Indicador | Valor |
|-----------|-------|
| Total | 42 |
| Abertas | 5 |
| Resolvidas | 31 |
| Graves | 8 |
| Taxa Resolucao | 73.8% |
| Tempo Medio | 48.3h |

_Dados ilustrativos._""",
            "suggestions": ["/relatorio disciplinar", "/relatorio rondas"],
        }

    async def _relatorio_diaristas(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de diaristas (servicos, pagamentos)."""
        start_date, end_date, label = self._parse_periodo(args)

        if self.has_data_connector and self.db:
            try:
                from sqlalchemy import select, func
                from modules.operacional.diaristas.models.diarist import Diarist

                # Busca diaristas ativos
                result = await self.db.execute(
                    select(Diarist).where(Diarist.ativo.is_(True))
                )
                diaristas = list(result.scalars().all())

                if diaristas:
                    total = len(diaristas)
                    lines = []
                    for d in diaristas[:15]:
                        nome = getattr(d, 'nome', 'N/A')
                        especialidade = getattr(d, 'especialidade', 'N/A')
                        valor_diaria = getattr(d, 'valor_diaria', 0)
                        lines.append(f"| {nome[:25]} | {especialidade} | R$ {valor_diaria:,.2f} |")

                    return {
                        "response": f"""**RELATORIO DE DIARISTAS** - {label}

**Total de Diaristas Ativos:** {total}

| Nome | Especialidade | Valor Diaria |
|------|--------------|--------------|
{chr(10).join(lines)}

{'*Exibindo os primeiros 15 registros.*' if total > 15 else ''}""",
                        "data": {"total": total, "periodo": label},
                        "suggestions": ["/relatorio custos", "/relatorio horas_extras"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de diaristas: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE DIARISTAS** - {label}

**Total Ativos:** 8

| Nome | Especialidade | Valor Diaria |
|------|--------------|--------------|
| Maria Silva | Limpeza | R$ 150,00 |
| Joao Pereira | Jardinagem | R$ 180,00 |
| Ana Costa | Limpeza | R$ 150,00 |

_Dados ilustrativos._""",
            "suggestions": ["/relatorio custos", "/relatorio horas_extras"],
        }

    async def _relatorio_rondas(self, args: List[str], context: Dict) -> Dict[str, Any]:
        """Relatorio de rondas de inspecao."""
        start_date, end_date, label = self._parse_periodo(args)

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_rondas_hoje()
                if result.success and result.data:
                    rondas = result.data
                    total = result.total_count

                    # Contar por status
                    concluidas = sum(1 for r in rondas if r.get("status") in ("concluida", "completed"))
                    em_andamento = sum(1 for r in rondas if r.get("status") in ("em_andamento", "in_progress"))
                    pendentes = sum(1 for r in rondas if r.get("status") in ("agendada", "scheduled", "pendente"))

                    lines = []
                    for r in rondas[:10]:
                        code = r.get("codigo", "N/A")
                        inspetor = r.get("inspetor", "N/A")
                        status = r.get("status", "N/A")
                        conformidade = r.get("conformidade", "N/A")
                        status_icon = {"concluida": "✅", "em_andamento": "🔄", "agendada": "📅"}.get(status, "⚪")
                        lines.append(f"| {status_icon} {code} | {inspetor[:15]} | {status} | {conformidade}% |")

                    return {
                        "response": f"""**RELATORIO DE RONDAS** - {label}

**Resumo:**
| Status | Qtd |
|--------|-----|
| Concluidas | {concluidas} |
| Em Andamento | {em_andamento} |
| Pendentes/Agendadas | {pendentes} |
| **Total** | **{total}** |

**Detalhamento:**

| Ronda | Inspetor | Status | Conformidade |
|-------|----------|--------|-------------|
{chr(10).join(lines) if lines else '| - | - | - | - |'}""",
                        "data": {"total": total, "concluidas": concluidas, "periodo": label},
                        "suggestions": ["/relatorio ocorrencias", "/relatorio disciplinar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao gerar relatorio de rondas: {e}")

        # Fallback estatico
        return {
            "response": f"""**RELATORIO DE RONDAS** - {label}

| Status | Qtd |
|--------|-----|
| Concluidas | 12 |
| Em Andamento | 2 |
| Agendadas | 4 |
| **Total** | **18** |

_Dados ilustrativos._""",
            "suggestions": ["/relatorio ocorrencias", "/relatorio disciplinar"],
        }

    def get_help(self) -> str:
        return """**Skill /cobertura**

**Comandos:**
```
/cobertura              - Visao geral
/cobertura critica      - Postos < 80%
/cobertura hoje         - Cobertura do dia
/cobertura semana       - Projecao semanal
/cobertura <posto>      - Posto especifico
```

**Relatorios Avancados (/relatorio):**
```
/relatorio horas_extras [periodo] [posto]  - Horas extras
/relatorio custos [periodo] [posto]        - Custos detalhados
/relatorio banco_horas [funcionario]       - Banco de horas
/relatorio substituicoes [periodo]         - Substituicoes
/relatorio disciplinar [periodo]           - Medidas disciplinares
/relatorio ocorrencias [periodo] [sev]     - Ocorrencias
/relatorio diaristas [periodo]             - Diaristas
/relatorio rondas [periodo]                - Rondas de inspecao
```
**Periodos:** hoje, semana, mes (padrao), trimestre"""
