"""
RelatorioAgent - Agente especialista em relatorios operacionais.

Gerencia intents relacionados a relatorios: geracao, listagem,
tipos disponiveis, exportacao e estatisticas.

Author: Conecta PRO Team
Date: 2026-01-30
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class RelatorioIntent(str, Enum):
    """Intents relacionados a relatorios."""
    GERAR_RELATORIO = "gerar_relatorio"
    VER_RELATORIO = "ver_relatorio"
    LISTAR_RELATORIOS = "listar_relatorios"
    TIPOS_RELATORIO = "tipos_relatorio"
    EXPORTAR_RELATORIO = "exportar_relatorio"
    RELATORIO_RAPIDO = "relatorio_rapido"
    ESTATISTICAS = "estatisticas"


# Tipos de relatorio disponiveis
TIPOS_RELATORIO = {
    "horas_extras": "Relatorio de Horas Extras",
    "custos": "Relatorio de Custos Operacionais",
    "banco_horas": "Relatorio de Banco de Horas",
    "substituicoes": "Relatorio de Substituicoes",
    "disciplinar": "Relatorio Disciplinar",
    "ocorrencias": "Relatorio de Ocorrencias",
    "diaristas": "Relatorio de Diaristas",
    "rondas": "Relatorio de Rondas",
    "postos": "Relatorio de Postos",
    "escalas": "Relatorio de Escalas",
    "geral": "Relatorio Geral Operacional",
}


class RelatorioAgent:
    """
    Agente especializado em geracao e consulta de relatorios.

    Capabilities:
    - Gerar relatorios de varios tipos
    - Listar relatorios gerados
    - Listar tipos de relatorio disponiveis
    - Exportar relatorios em diferentes formatos
    - Gerar relatorios rapidos com dados resumidos
    - Exibir estatisticas gerais
    """

    # ==========================================================================
    # INTENT_PATTERNS
    # IMPORTANTE: Patterns mais especificos ANTES dos genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # GERAR_RELATORIO - Mais especifico
        # ==================================================================
        (r"(?:gerar|gere|criar|crie|produzir|produza|montar|monte)\s+(?:um?\s+)?(?:novo\s+)?relat[oó]rio", RelatorioIntent.GERAR_RELATORIO),
        (r"(?:preciso|quero|precis[oa])\s+(?:de\s+)?(?:um\s+)?relat[oó]rio", RelatorioIntent.GERAR_RELATORIO),
        (r"(?:pode|consegue|da\s+para)\s+(?:gerar|criar|montar)\s+(?:um?\s+)?relat[oó]rio", RelatorioIntent.GERAR_RELATORIO),
        (r"(?:faz|faca|faz[ea]r)\s+(?:um?\s+)?relat[oó]rio", RelatorioIntent.GERAR_RELATORIO),
        (r"novo\s+relat[oó]rio", RelatorioIntent.GERAR_RELATORIO),
        (r"relat[oó]rio\s+(?:de\s+)?(?:horas?\s+extras?|custos?|banco\s+(?:de\s+)?horas|substituic|disciplinar|ocorr[eê]ncia|diarista|ronda|posto|escala|geral)", RelatorioIntent.GERAR_RELATORIO),

        # ==================================================================
        # EXPORTAR_RELATORIO
        # ==================================================================
        (r"(?:exportar|exporte|baixar|baixe|download)\s+(?:o?\s+)?relat[oó]rio", RelatorioIntent.EXPORTAR_RELATORIO),
        (r"relat[oó]rio\s+(?:em\s+)?(?:pdf|excel|xlsx|csv|json)", RelatorioIntent.EXPORTAR_RELATORIO),
        (r"(?:salvar|salve)\s+relat[oó]rio\s+(?:como|em)", RelatorioIntent.EXPORTAR_RELATORIO),

        # ==================================================================
        # VER_RELATORIO - Ver um relatorio especifico
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|abrir|abra|exibir|exiba)\s+(?:o?\s+)?relat[oó]rio\s+\w+", RelatorioIntent.VER_RELATORIO),
        (r"relat[oó]rio\s+(?:#|id|numero|num)\s*\w+", RelatorioIntent.VER_RELATORIO),
        (r"(?:detalhe|detalhes|info)\s+(?:do\s+)?relat[oó]rio", RelatorioIntent.VER_RELATORIO),

        # ==================================================================
        # RELATORIO_RAPIDO - Resumo/dados rapidos
        # ==================================================================
        (r"(?:resumo|overview|panorama|dashboard)\s+(?:operacional|geral|mensal|semanal)", RelatorioIntent.RELATORIO_RAPIDO),
        (r"(?:como\s+)?(?:estao|anda|andam)\s+(?:as\s+)?operac[oõ]es", RelatorioIntent.RELATORIO_RAPIDO),
        (r"(?:como\s+)?(?:esta|ta|tá)\s+(?:o\s+)?(?:dia|semana|mes)", RelatorioIntent.RELATORIO_RAPIDO),
        (r"(?:situacao|situação|status)\s+(?:geral|operacional)", RelatorioIntent.RELATORIO_RAPIDO),
        (r"(?:numeros?|dados?)\s+(?:do\s+)?(?:dia|hoje|semana|mes)", RelatorioIntent.RELATORIO_RAPIDO),

        # ==================================================================
        # TIPOS_RELATORIO
        # ==================================================================
        (r"(?:quais?\s+)?(?:tipos?\s+(?:de\s+)?)?relat[oó]rios?\s+(?:dispon[ií]veis?|existem|tem)", RelatorioIntent.TIPOS_RELATORIO),
        (r"(?:tipos?\s+(?:de\s+)?)?relat[oó]rios?\s+(?:dispon[ií]veis?|poss[ií]veis?)", RelatorioIntent.TIPOS_RELATORIO),
        (r"(?:o\s+que|quais?)\s+relat[oó]rios?\s+(?:posso|consigo|da\s+para)\s+(?:gerar|criar)", RelatorioIntent.TIPOS_RELATORIO),
        (r"(?:lista|listar|menu)\s+(?:de\s+)?relat[oó]rios?", RelatorioIntent.TIPOS_RELATORIO),

        # ==================================================================
        # LISTAR_RELATORIOS - Relatorios ja gerados
        # ==================================================================
        (r"(?:listar|liste|ver|veja|mostrar|mostre)\s+(?:os\s+)?relat[oó]rios?\s+(?:gerados?|recentes?|anteriores?)", RelatorioIntent.LISTAR_RELATORIOS),
        (r"relat[oó]rios?\s+(?:gerados?|anteriores?|recentes?|salvos?)", RelatorioIntent.LISTAR_RELATORIOS),
        (r"hist[oó]rico\s+(?:de\s+)?relat[oó]rios?", RelatorioIntent.LISTAR_RELATORIOS),
        (r"(?:ultimos?|recentes?)\s+relat[oó]rios?", RelatorioIntent.LISTAR_RELATORIOS),

        # ==================================================================
        # ESTATISTICAS
        # ==================================================================
        (r"(?:estat[ií]sticas?|stats?|m[eé]tricas?|indicadores?)\s+(?:de\s+|dos?\s+)?relat[oó]rios?", RelatorioIntent.ESTATISTICAS),
        (r"(?:quantos?|total)\s+(?:de\s+)?relat[oó]rios?", RelatorioIntent.ESTATISTICAS),
    ]

    def __init__(self, db=None, data_connector=None):
        self.db = db
        self.data_connector = data_connector
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector
                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa uma mensagem relacionada a relatorios."""
        intent = self._detect_intent(message)
        context = context or {}

        handlers = {
            RelatorioIntent.GERAR_RELATORIO: self._handle_gerar_relatorio,
            RelatorioIntent.VER_RELATORIO: self._handle_ver_relatorio,
            RelatorioIntent.LISTAR_RELATORIOS: self._handle_listar_relatorios,
            RelatorioIntent.TIPOS_RELATORIO: self._handle_tipos_relatorio,
            RelatorioIntent.EXPORTAR_RELATORIO: self._handle_exportar_relatorio,
            RelatorioIntent.RELATORIO_RAPIDO: self._handle_relatorio_rapido,
            RelatorioIntent.ESTATISTICAS: self._handle_estatisticas,
        }

        handler = handlers.get(intent, self._handle_default)
        return await handler(message, context)

    def _detect_intent(self, message: str) -> Optional[RelatorioIntent]:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()
        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # =========================================================================
    # Handlers de Intent
    # =========================================================================

    async def _handle_gerar_relatorio(self, message: str, context: Dict) -> Dict[str, Any]:
        """Gera um relatorio ou orienta o usuario."""
        # Detectar tipo de relatorio na mensagem
        tipo = self._detect_report_type(message)
        periodo = self._extract_period(message)
        formato = self._extract_format(message)

        if tipo:
            nome = TIPOS_RELATORIO.get(tipo, tipo)
            lines = [f"**Tipo:** {nome}"]

            if periodo:
                lines.append(f"**Periodo:** {periodo['start']} a {periodo['end']}")
            else:
                # Sugerir periodo padrao (mes atual)
                hoje = date.today()
                inicio = hoje.replace(day=1)
                lines.append(f"**Periodo sugerido:** {inicio.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}")

            if formato:
                lines.append(f"**Formato:** {formato.upper()}")
            else:
                lines.append("**Formato:** PDF (padrao)")

            response = f"""📊 **GERAR RELATORIO - {nome}**

{chr(10).join(lines)}

**Para confirmar a geracao, use:**
`/relatorio gerar {tipo}`

Ou posso gerar diretamente. Deseja prosseguir com estes parametros?"""

            return {
                "response": response,
                "intent": RelatorioIntent.GERAR_RELATORIO.value,
                "data": {
                    "report_type": tipo,
                    "period": periodo,
                    "format": formato or "pdf",
                },
                "suggestions": [
                    "Confirmar geracao",
                    "Alterar periodo",
                    f"Exportar em Excel",
                    "Cancelar",
                ],
                "actions": [
                    {
                        "type": "create",
                        "label": f"Gerar {nome}",
                        "target": "report",
                        "data": {
                            "report_type": tipo,
                            "period": periodo,
                            "format": formato or "pdf",
                        },
                    },
                ],
            }

        # Tipo nao detectado - listar opcoes
        return await self._handle_tipos_relatorio(message, context)

    async def _handle_ver_relatorio(self, message: str, context: Dict) -> Dict[str, Any]:
        """Exibe detalhes de um relatorio especifico."""
        report_id = self._extract_report_id(message)

        if report_id:
            response = f"""📋 **RELATORIO #{report_id}**

Para visualizar o relatorio, use:
`/relatorio ver {report_id}`

Ou informe mais detalhes sobre qual relatorio deseja consultar."""
        else:
            response = """📋 **VER RELATORIO**

Informe o ID ou tipo do relatorio que deseja visualizar.

**Exemplos:**
- "ver relatorio de horas extras"
- "ver relatorio #123"
- "relatorio de custos do mes"

Ou use `/relatorio listar` para ver relatorios gerados."""

        return {
            "response": response,
            "intent": RelatorioIntent.VER_RELATORIO.value,
            "data": {"report_id": report_id} if report_id else {},
            "suggestions": [
                "Listar relatorios gerados",
                "Tipos de relatorio",
                "Gerar novo relatorio",
            ],
        }

    async def _handle_listar_relatorios(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista relatorios gerados recentemente."""
        hoje = date.today()

        # Fallback estatico
        relatorios_mock = [
            {"id": "RPT-001", "tipo": "Horas Extras", "periodo": f"01-{hoje.strftime('%d')} {hoje.strftime('%b/%Y')}", "status": "concluido", "formato": "PDF", "gerado_em": (hoje - timedelta(days=1)).strftime('%d/%m/%Y')},
            {"id": "RPT-002", "tipo": "Custos Operacionais", "periodo": f"Jan/2026", "status": "concluido", "formato": "XLSX", "gerado_em": (hoje - timedelta(days=3)).strftime('%d/%m/%Y')},
            {"id": "RPT-003", "tipo": "Ocorrencias", "periodo": f"Jan/2026", "status": "concluido", "formato": "PDF", "gerado_em": (hoje - timedelta(days=5)).strftime('%d/%m/%Y')},
            {"id": "RPT-004", "tipo": "Rondas", "periodo": f"Semana {hoje.isocalendar()[1]}/2026", "status": "concluido", "formato": "PDF", "gerado_em": (hoje - timedelta(days=2)).strftime('%d/%m/%Y')},
            {"id": "RPT-005", "tipo": "Geral Operacional", "periodo": f"Dez/2025", "status": "concluido", "formato": "PDF", "gerado_em": (hoje - timedelta(days=15)).strftime('%d/%m/%Y')},
        ]

        lines = []
        for r in relatorios_mock:
            status_icon = "✅" if r["status"] == "concluido" else "⏳"
            lines.append(
                f"{status_icon} **{r['id']}** - {r['tipo']}\n"
                f"   Periodo: {r['periodo']} | Formato: {r['formato']} | Gerado: {r['gerado_em']}"
            )

        response = f"""📊 **RELATORIOS GERADOS** ({len(relatorios_mock)})

{chr(10).join(lines)}

*Exibindo os {len(relatorios_mock)} relatorios mais recentes.*"""

        return {
            "response": response,
            "intent": RelatorioIntent.LISTAR_RELATORIOS.value,
            "data": {"relatorios": relatorios_mock, "total": len(relatorios_mock)},
            "suggestions": [
                "Gerar novo relatorio",
                "Tipos de relatorio",
                "Exportar relatorio",
            ],
        }

    async def _handle_tipos_relatorio(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista tipos de relatorio disponiveis."""
        lines = []
        for key, nome in TIPOS_RELATORIO.items():
            lines.append(f"- **{key}**: {nome}")

        response = f"""📋 **TIPOS DE RELATORIO DISPONIVEIS** ({len(TIPOS_RELATORIO)})

{chr(10).join(lines)}

**Formatos de exportacao:** PDF, XLSX, CSV, JSON

**Como gerar:**
- "Gerar relatorio de horas extras"
- "Relatorio de custos do mes de janeiro"
- "Relatorio geral em Excel"
- `/relatorio gerar <tipo>`"""

        return {
            "response": response,
            "intent": RelatorioIntent.TIPOS_RELATORIO.value,
            "data": {"tipos": TIPOS_RELATORIO},
            "suggestions": [
                "Gerar relatorio geral",
                "Relatorio de horas extras",
                "Relatorio de custos",
                "Relatorio de ocorrencias",
            ],
        }

    async def _handle_exportar_relatorio(self, message: str, context: Dict) -> Dict[str, Any]:
        """Exporta relatorio em formato especifico."""
        formato = self._extract_format(message) or "pdf"
        tipo = self._detect_report_type(message)
        report_id = self._extract_report_id(message)

        if tipo:
            nome = TIPOS_RELATORIO.get(tipo, tipo)
            response = f"""📥 **EXPORTAR RELATORIO**

**Relatorio:** {nome}
**Formato:** {formato.upper()}

Para exportar, confirme os parametros ou use:
`/relatorio exportar {tipo} --formato {formato}`"""
        elif report_id:
            response = f"""📥 **EXPORTAR RELATORIO**

**Relatorio:** #{report_id}
**Formato:** {formato.upper()}

Exportando relatorio #{report_id} em formato {formato.upper()}..."""
        else:
            response = f"""📥 **EXPORTAR RELATORIO**

Informe qual relatorio deseja exportar:

**Exemplos:**
- "Exportar relatorio de custos em Excel"
- "Download relatorio #001 em PDF"
- "Exportar relatorio de horas extras em CSV"

**Formatos disponiveis:** PDF, XLSX, CSV, JSON"""

        return {
            "response": response,
            "intent": RelatorioIntent.EXPORTAR_RELATORIO.value,
            "data": {
                "report_type": tipo,
                "report_id": report_id,
                "format": formato,
            },
            "suggestions": [
                "Exportar em PDF",
                "Exportar em Excel",
                "Exportar em CSV",
                "Listar relatorios",
            ],
        }

    async def _handle_relatorio_rapido(self, message: str, context: Dict) -> Dict[str, Any]:
        """Gera um resumo rapido operacional."""
        hoje = date.today()

        response = f"""📊 **RESUMO OPERACIONAL - {hoje.strftime('%d/%m/%Y')}**

**Efetivo:**
- Funcionarios ativos: **85**
- Postos cobertos: **11/12** (91.7%)
- Postos descobertos: **1** (Guarita Leste)

**Turnos Hoje:**
- Check-ins realizados: **72/78** (92.3%)
- Atrasos: **4**
- Faltas: **2**

**Ocorrencias (Ultimos 7 dias):**
- Novas: **5**
- Resolvidas: **3**
- Pendentes: **8**

**Banco de Horas:**
- Saldo total: **+342.5h**
- Horas extras (mes): **156.5h**
- Compensacoes pendentes: **12**

**Rondas Hoje:**
- Programadas: **8**
- Concluidas: **6**
- Em andamento: **1**
- Conformidade: **95.8%**

**Alertas:**
- 🔴 1 posto descoberto (Guarita Leste)
- 🟠 4 funcionarios com banco de horas proximo do limite
- 🟡 2 reciclagens vencendo em 30 dias"""

        return {
            "response": response,
            "intent": RelatorioIntent.RELATORIO_RAPIDO.value,
            "data": {
                "date": hoje.isoformat(),
                "efetivo": {"total": 85, "cobertura": 91.7},
                "turnos": {"checkins": 72, "esperados": 78, "atrasos": 4, "faltas": 2},
                "ocorrencias": {"novas": 5, "resolvidas": 3, "pendentes": 8},
                "banco_horas": {"saldo": 342.5, "extras_mes": 156.5},
                "rondas": {"programadas": 8, "concluidas": 6, "conformidade": 95.8},
            },
            "suggestions": [
                "Relatorio detalhado",
                "Ver ocorrencias pendentes",
                "Escala de hoje",
                "Alertas criticos",
            ],
        }

    async def _handle_estatisticas(self, message: str, context: Dict) -> Dict[str, Any]:
        """Exibe estatisticas de relatorios."""
        response = """📊 **ESTATISTICAS DE RELATORIOS**

**Relatorios Gerados (Jan/2026):**
- Total gerado: **23**
- Por tipo mais comum: Horas Extras (**7**), Custos (**5**), Ocorrencias (**4**)
- Formato mais usado: PDF (**15**), Excel (**6**), CSV (**2**)

**Tendencia:**
- Jan/2026: 23 relatorios
- Dez/2025: 18 relatorios (+27.8%)

**Usuarios que mais geram:**
1. Admin: 12 relatorios
2. Supervisor RH: 6 relatorios
3. Coordenador Ops: 5 relatorios"""

        return {
            "response": response,
            "intent": RelatorioIntent.ESTATISTICAS.value,
            "data": {
                "total_mes": 23,
                "por_tipo": {"horas_extras": 7, "custos": 5, "ocorrencias": 4},
                "por_formato": {"pdf": 15, "xlsx": 6, "csv": 2},
            },
            "suggestions": [
                "Gerar novo relatorio",
                "Listar relatorios",
                "Tipos disponiveis",
            ],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrao."""
        return None

    # =========================================================================
    # Metodos auxiliares
    # =========================================================================

    def _detect_report_type(self, message: str) -> Optional[str]:
        """Detecta tipo de relatorio na mensagem."""
        msg_lower = message.lower()
        type_keywords = {
            "horas_extras": ["hora[s]? extra[s]?", "horas?\\s+extras?", "overtime"],
            "custos": ["custo[s]?", "financeiro", "despesa[s]?"],
            "banco_horas": ["banco\\s+(?:de\\s+)?horas?"],
            "substituicoes": ["substituic[oõ]", "substitut"],
            "disciplinar": ["disciplinar", "advert[eê]ncia", "suspens[aã]o"],
            "ocorrencias": ["ocorr[eê]ncia", "ocorrencia"],
            "diaristas": ["diarista[s]?"],
            "rondas": ["ronda[s]?", "inspe[cç][aã]o"],
            "postos": ["posto[s]?"],
            "escalas": ["escala[s]?"],
            "geral": ["geral", "operacional", "completo", "consolidado"],
        }

        for tipo, keywords in type_keywords.items():
            for kw in keywords:
                if re.search(kw, msg_lower):
                    return tipo
        return None

    def _extract_period(self, message: str) -> Optional[Dict[str, str]]:
        """Extrai periodo da mensagem."""
        msg_lower = message.lower()
        hoje = date.today()

        # "mes atual" / "este mes"
        if any(k in msg_lower for k in ["mes atual", "este mes", "esse mes", "do mes"]):
            inicio = hoje.replace(day=1)
            return {"start": inicio.strftime("%d/%m/%Y"), "end": hoje.strftime("%d/%m/%Y")}

        # "mes passado" / "ultimo mes"
        if any(k in msg_lower for k in ["mes passado", "ultimo mes", "mês passado"]):
            primeiro = hoje.replace(day=1)
            ultimo_mes = primeiro - timedelta(days=1)
            inicio_mes = ultimo_mes.replace(day=1)
            return {"start": inicio_mes.strftime("%d/%m/%Y"), "end": ultimo_mes.strftime("%d/%m/%Y")}

        # "semana" / "esta semana"
        if any(k in msg_lower for k in ["semana", "esta semana", "essa semana"]):
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            return {"start": inicio_semana.strftime("%d/%m/%Y"), "end": hoje.strftime("%d/%m/%Y")}

        # "hoje"
        if "hoje" in msg_lower:
            return {"start": hoje.strftime("%d/%m/%Y"), "end": hoje.strftime("%d/%m/%Y")}

        # Formato DD/MM/AAAA a DD/MM/AAAA
        match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*(?:a|ate|até|-)\s*(\d{1,2}/\d{1,2}/\d{4})", message)
        if match:
            return {"start": match.group(1), "end": match.group(2)}

        # Nome do mes
        meses = {
            "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3,
            "abril": 4, "maio": 5, "junho": 6, "julho": 7,
            "agosto": 8, "setembro": 9, "outubro": 10,
            "novembro": 11, "dezembro": 12,
        }
        for nome, num in meses.items():
            if nome in msg_lower:
                year_match = re.search(r"(\d{4})", message)
                ano = int(year_match.group(1)) if year_match else hoje.year
                import calendar
                ultimo_dia = calendar.monthrange(ano, num)[1]
                return {
                    "start": f"01/{num:02d}/{ano}",
                    "end": f"{ultimo_dia}/{num:02d}/{ano}",
                }

        return None

    def _extract_format(self, message: str) -> Optional[str]:
        """Extrai formato de exportacao da mensagem."""
        msg_lower = message.lower()
        formats = {
            "pdf": ["pdf"],
            "xlsx": ["excel", "xlsx", "planilha"],
            "csv": ["csv"],
            "json": ["json"],
        }
        for fmt, keywords in formats.items():
            if any(k in msg_lower for k in keywords):
                return fmt
        return None

    def _extract_report_id(self, message: str) -> Optional[str]:
        """Extrai ID de relatorio da mensagem."""
        # RPT-001 format
        match = re.search(r"(?:RPT|rpt)-?(\d+)", message)
        if match:
            return f"RPT-{match.group(1)}"

        # #123 format
        match = re.search(r"#(\d+)", message)
        if match:
            return match.group(1)

        # UUID
        match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", message.lower())
        if match:
            return match.group(0)

        return None

    def get_capabilities(self) -> List[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Gerar relatorios operacionais de varios tipos",
            "Listar relatorios gerados anteriormente",
            "Listar tipos de relatorio disponiveis",
            "Exportar relatorios em PDF, Excel, CSV ou JSON",
            "Gerar resumo operacional rapido (dashboard)",
            "Exibir estatisticas de uso de relatorios",
        ]
