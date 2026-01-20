# ARQUITETURA DE IA AVANÇADA - MÓDULO OPERACIONAL
## Agentes Inteligentes, Skills e MCP Servers

**Data:** 2026-01-18
**Versão:** 1.0
**Qualidade Alvo:** 99+/100

---

## 1. VISÃO GERAL DA ARQUITETURA DE IA

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MÓDULO OPERACIONAL INTELIGENTE                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                 │
│  │  BARTOLO CORE   │◄──►│  AGENTES IA     │◄──►│   MCP SERVERS   │                 │
│  │  (Orquestrador) │    │  (Especialistas)│    │  (Ferramentas)  │                 │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘                 │
│           │                      │                      │                          │
│           ▼                      ▼                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                        SKILLS OPERACIONAIS                                   │   │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤   │
│  │ Escala      │ Ocorrência  │ Substituição│ Medida      │ Análise             │   │
│  │ Inteligente │ Analyzer    │ Optimizer   │ Advisor     │ Preditiva           │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                        KNOWLEDGE BASE                                        │   │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤   │
│  │ CLT/Leis    │ CCT/Acordos │ Políticas   │ Histórico   │ Padrões             │   │
│  │ Trabalhistas│ Coletivos   │ Internas    │ Operacional │ Comportamento       │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. AGENTES DE IA ESPECIALIZADOS

### 2.1 OperationalAgent (Agente Principal)

```python
# /backend/modules/ai/agents/operational_agent.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, date

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


class OperationalAgentCapability(str, Enum):
    """Capacidades do agente operacional."""
    SCALE_MANAGEMENT = "scale_management"
    OCCURRENCE_HANDLING = "occurrence_handling"
    SUBSTITUTION_OPTIMIZATION = "substitution_optimization"
    DISCIPLINARY_ADVISORY = "disciplinary_advisory"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    REAL_TIME_MONITORING = "real_time_monitoring"
    REPORT_GENERATION = "report_generation"


@dataclass
class AgentContext:
    """Contexto do agente para a sessão."""
    user_id: str
    user_role: str
    tenant_id: str
    department: str
    permissions: List[str]
    current_module: str
    conversation_history: List[Dict[str, Any]]


class OperationalAgent:
    """
    Agente de IA especializado em operações.

    Orquestra sub-agentes e skills para resolver problemas
    operacionais complexos de forma autônoma.
    """

    SYSTEM_PROMPT = """Você é o Assistente Operacional Inteligente da Conecta Mais.

Seu papel é ajudar gestores, supervisores, inspetores e líderes de posto
a gerenciar operações de forma eficiente e inteligente.

SUAS CAPACIDADES:
1. ESCALAS: Gerar, otimizar e validar escalas de trabalho
2. OCORRÊNCIAS: Analisar, classificar e sugerir resoluções
3. SUBSTITUIÇÕES: Encontrar o melhor substituto considerando múltiplos fatores
4. MEDIDAS: Orientar sobre aplicação correta de medidas administrativas
5. ANÁLISE: Identificar padrões, prever problemas, sugerir melhorias
6. MONITORAMENTO: Acompanhar indicadores em tempo real

REGRAS IMPORTANTES:
- Sempre considere a legislação trabalhista (CLT)
- Respeite as permissões do usuário
- Priorize a qualidade do serviço ao cliente
- Otimize custos sem prejudicar colaboradores
- Registre todas as ações para auditoria

CONTEXTO DO USUÁRIO:
- Cargo: {user_role}
- Departamento: {department}
- Permissões: {permissions}

Seja proativo, sugira ações e antecipe problemas."""

    def __init__(
        self,
        llm,
        tools: List[Tool],
        context: AgentContext,
        memory_window: int = 10
    ):
        self.llm = llm
        self.tools = tools
        self.context = context
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            return_messages=True,
            memory_key="chat_history"
        )
        self.agent = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Cria o agente com ferramentas e prompt."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT.format(
                user_role=self.context.user_role,
                department=self.context.department,
                permissions=", ".join(self.context.permissions)
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )

    async def process(self, user_input: str) -> Dict[str, Any]:
        """Processa input do usuário e retorna resposta."""
        try:
            result = await self.agent.ainvoke({
                "input": user_input,
                "chat_history": self.memory.chat_memory.messages
            })

            return {
                "success": True,
                "response": result["output"],
                "actions_taken": self._extract_actions(result),
                "suggestions": self._generate_suggestions(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(user_input)
            }

    def _extract_actions(self, result: Dict) -> List[Dict]:
        """Extrai ações executadas pelo agente."""
        # Implementar extração de ações do resultado
        return []

    def _generate_suggestions(self, result: Dict) -> List[str]:
        """Gera sugestões proativas baseadas no contexto."""
        # Implementar geração de sugestões
        return []

    def _get_fallback_response(self, input: str) -> str:
        """Resposta de fallback em caso de erro."""
        return "Desculpe, não consegui processar sua solicitação. Por favor, tente novamente ou contate o suporte."
```

### 2.2 Sub-Agentes Especializados

```python
# Sub-agentes que o OperationalAgent pode invocar

class ScaleOptimizerAgent:
    """
    Agente especializado em otimização de escalas.

    Capacidades:
    - Gerar escalas otimizadas considerando múltiplos fatores
    - Balancear carga de trabalho entre funcionários
    - Minimizar horas extras desnecessárias
    - Considerar preferências dos funcionários
    - Respeitar todas as regras CLT
    """

    async def generate_optimized_scale(
        self,
        post_id: str,
        month: int,
        year: int,
        employees: List[str],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera escala otimizada usando algoritmos de IA."""
        pass

    async def analyze_scale_quality(
        self,
        scale_id: str
    ) -> Dict[str, Any]:
        """Analisa qualidade de uma escala existente."""
        pass

    async def suggest_improvements(
        self,
        scale_id: str
    ) -> List[Dict[str, Any]]:
        """Sugere melhorias para uma escala."""
        pass


class OccurrenceAnalyzerAgent:
    """
    Agente especializado em análise de ocorrências.

    Capacidades:
    - Classificar automaticamente severidade
    - Identificar padrões recorrentes
    - Sugerir ações de resolução
    - Prever escalação necessária
    - Recomendar medidas preventivas
    """

    async def classify_occurrence(
        self,
        description: str,
        post_info: Dict,
        employee_info: Optional[Dict]
    ) -> Dict[str, Any]:
        """Classifica ocorrência automaticamente."""
        pass

    async def analyze_patterns(
        self,
        post_id: Optional[str] = None,
        client_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Analisa padrões de ocorrências."""
        pass

    async def suggest_resolution(
        self,
        occurrence_id: str
    ) -> List[Dict[str, Any]]:
        """Sugere resolução para ocorrência."""
        pass


class SubstitutionOptimizerAgent:
    """
    Agente especializado em otimização de substituições.

    Capacidades:
    - Encontrar substituto ideal (custo x qualidade)
    - Considerar proximidade geográfica
    - Avaliar histórico do substituto
    - Prever aceitação da substituição
    - Minimizar impacto no banco de horas
    """

    async def find_optimal_substitute(
        self,
        shift_id: str,
        urgency: str,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Encontra substitutos ordenados por adequação."""
        pass

    async def predict_acceptance(
        self,
        employee_id: str,
        shift_info: Dict
    ) -> float:
        """Prevê probabilidade de aceitação."""
        pass


class DisciplinaryAdvisorAgent:
    """
    Agente especializado em assessoria disciplinar.

    Capacidades:
    - Orientar sobre medida adequada
    - Validar conformidade legal
    - Sugerir texto do documento
    - Verificar proporcionalidade
    - Alertar sobre riscos trabalhistas
    """

    async def recommend_action(
        self,
        occurrence_id: str,
        employee_history: Dict
    ) -> Dict[str, Any]:
        """Recomenda medida administrativa adequada."""
        pass

    async def validate_legal_compliance(
        self,
        action_type: str,
        reason: str,
        employee_history: Dict
    ) -> Dict[str, Any]:
        """Valida conformidade legal da medida."""
        pass

    async def generate_document_text(
        self,
        action_type: str,
        occurrence: Dict,
        employee: Dict
    ) -> str:
        """Gera texto do documento de medida."""
        pass


class PredictiveAnalysisAgent:
    """
    Agente especializado em análise preditiva.

    Capacidades:
    - Prever faltas e ausências
    - Identificar risco de turnover
    - Prever demanda de substituições
    - Alertar sobre vencimentos (banco de horas, documentos)
    - Identificar tendências de ocorrências
    """

    async def predict_absences(
        self,
        period: str,
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Prevê ausências prováveis no período."""
        pass

    async def identify_turnover_risk(
        self,
        employee_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Identifica funcionários com risco de saída."""
        pass

    async def forecast_demand(
        self,
        client_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Prevê demanda operacional."""
        pass
```

---

## 3. SKILLS OPERACIONAIS

### 3.1 Definição de Skills

```python
# /backend/modules/ai/skills/operational_skills.py

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio


class SkillCategory(str, Enum):
    """Categorias de skills."""
    QUERY = "query"           # Consultas
    ACTION = "action"         # Ações no sistema
    ANALYSIS = "analysis"     # Análises
    GENERATION = "generation" # Geração de conteúdo
    PREDICTION = "prediction" # Previsões


@dataclass
class Skill:
    """Definição de uma skill."""
    id: str
    name: str
    description: str
    category: SkillCategory
    required_permissions: List[str]
    parameters: Dict[str, Any]
    handler: Callable
    examples: List[str]


# =============================================================================
# SKILLS DE CONSULTA
# =============================================================================

SKILL_CONSULTAR_ESCALA = Skill(
    id="consultar_escala",
    name="Consultar Escala",
    description="Consulta a escala de trabalho de um funcionário ou posto",
    category=SkillCategory.QUERY,
    required_permissions=["operacoes.escalas.visualizar"],
    parameters={
        "employee_id": {"type": "uuid", "required": False},
        "post_id": {"type": "uuid", "required": False},
        "month": {"type": "int", "required": False},
        "year": {"type": "int", "required": False}
    },
    handler=None,  # Definido na implementação
    examples=[
        "Qual a escala do João Silva em janeiro?",
        "Quem está escalado no posto Central amanhã?",
        "Mostra a escala do mês"
    ]
)

SKILL_CONSULTAR_PRESENCA = Skill(
    id="consultar_presenca",
    name="Consultar Presença",
    description="Verifica quem está trabalhando agora em um posto ou cliente",
    category=SkillCategory.QUERY,
    required_permissions=["operacoes.turnos.visualizar"],
    parameters={
        "post_id": {"type": "uuid", "required": False},
        "client_id": {"type": "uuid", "required": False},
        "date": {"type": "date", "required": False, "default": "today"}
    },
    handler=None,
    examples=[
        "Quem está de plantão agora?",
        "Quem está trabalhando no cliente X?",
        "Lista os funcionários em serviço"
    ]
)

SKILL_CONSULTAR_BANCO_HORAS = Skill(
    id="consultar_banco_horas",
    name="Consultar Banco de Horas",
    description="Consulta saldo e histórico de banco de horas",
    category=SkillCategory.QUERY,
    required_permissions=["operacoes.banco_horas.visualizar"],
    parameters={
        "employee_id": {"type": "uuid", "required": True},
        "include_history": {"type": "bool", "required": False, "default": False}
    },
    handler=None,
    examples=[
        "Qual o saldo de banco de horas do João?",
        "Quantas horas o funcionário X tem para compensar?",
        "Mostra histórico de banco de horas"
    ]
)

SKILL_CONSULTAR_HISTORICO_DISCIPLINAR = Skill(
    id="consultar_historico_disciplinar",
    name="Consultar Histórico Disciplinar",
    description="Consulta advertências e suspensões de um funcionário",
    category=SkillCategory.QUERY,
    required_permissions=["operacoes.medidas.visualizar"],
    parameters={
        "employee_id": {"type": "uuid", "required": True},
        "period_months": {"type": "int", "required": False, "default": 12}
    },
    handler=None,
    examples=[
        "O funcionário X tem advertências?",
        "Quantas advertências o João já recebeu?",
        "Mostra histórico disciplinar"
    ]
)

# =============================================================================
# SKILLS DE AÇÃO
# =============================================================================

SKILL_CRIAR_OCORRENCIA = Skill(
    id="criar_ocorrencia",
    name="Criar Ocorrência",
    description="Registra uma nova ocorrência no sistema",
    category=SkillCategory.ACTION,
    required_permissions=["operacoes.ocorrencias.criar"],
    parameters={
        "post_id": {"type": "uuid", "required": True},
        "category": {"type": "enum", "required": True, "values": ["SEGURANCA", "LIMPEZA", "COMPORTAMENTO", "ACIDENTE", "MANUTENCAO", "OUTRO"]},
        "severity": {"type": "enum", "required": True, "values": ["BAIXA", "MEDIA", "ALTA", "CRITICA"]},
        "title": {"type": "str", "required": True},
        "description": {"type": "str", "required": True},
        "employee_involved_id": {"type": "uuid", "required": False}
    },
    handler=None,
    examples=[
        "Registrar ocorrência de falta no posto X",
        "Criar ocorrência de segurança crítica",
        "Registrar problema de limpeza"
    ]
)

SKILL_SOLICITAR_SUBSTITUICAO = Skill(
    id="solicitar_substituicao",
    name="Solicitar Substituição",
    description="Solicita substituição para um turno",
    category=SkillCategory.ACTION,
    required_permissions=["operacoes.substituicoes.criar"],
    parameters={
        "shift_id": {"type": "uuid", "required": True},
        "reason": {"type": "enum", "required": True, "values": ["SICK_LEAVE", "VACATION", "PERSONAL", "TRAINING", "NO_SHOW", "EMERGENCY"]},
        "reason_details": {"type": "str", "required": False}
    },
    handler=None,
    examples=[
        "Preciso de substituto para o João que faltou",
        "Solicitar substituição por atestado médico",
        "O funcionário X não vai comparecer hoje"
    ]
)

SKILL_CRIAR_ADVERTENCIA = Skill(
    id="criar_advertencia",
    name="Criar Advertência",
    description="Cria rascunho de advertência para aprovação",
    category=SkillCategory.ACTION,
    required_permissions=["operacoes.medidas.criar"],
    parameters={
        "employee_id": {"type": "uuid", "required": True},
        "action_type": {"type": "enum", "required": True, "values": ["ADVERTENCIA_VERBAL", "ADVERTENCIA_ESCRITA"]},
        "reason_category": {"type": "str", "required": True},
        "reason_description": {"type": "str", "required": True},
        "occurrence_id": {"type": "uuid", "required": False}
    },
    handler=None,
    examples=[
        "Criar advertência escrita por falta injustificada",
        "Registrar advertência verbal",
        "Aplicar advertência baseada na ocorrência X"
    ]
)

# =============================================================================
# SKILLS DE ANÁLISE
# =============================================================================

SKILL_ANALISAR_COBERTURA = Skill(
    id="analisar_cobertura",
    name="Analisar Cobertura",
    description="Analisa cobertura operacional de um período",
    category=SkillCategory.ANALYSIS,
    required_permissions=["operacoes.relatorios.visualizar"],
    parameters={
        "start_date": {"type": "date", "required": True},
        "end_date": {"type": "date", "required": True},
        "client_id": {"type": "uuid", "required": False},
        "post_id": {"type": "uuid", "required": False}
    },
    handler=None,
    examples=[
        "Como foi a cobertura essa semana?",
        "Analisa cobertura do cliente X em janeiro",
        "Taxa de cobertura do mês"
    ]
)

SKILL_ANALISAR_HORAS_EXTRAS = Skill(
    id="analisar_horas_extras",
    name="Analisar Horas Extras",
    description="Analisa horas extras realizadas no período",
    category=SkillCategory.ANALYSIS,
    required_permissions=["operacoes.relatorios.visualizar"],
    parameters={
        "start_date": {"type": "date", "required": True},
        "end_date": {"type": "date", "required": True},
        "group_by": {"type": "enum", "required": False, "values": ["employee", "post", "client"], "default": "employee"}
    },
    handler=None,
    examples=[
        "Quanto de hora extra fizemos esse mês?",
        "Ranking de horas extras por funcionário",
        "Horas extras por cliente"
    ]
)

# =============================================================================
# SKILLS DE GERAÇÃO
# =============================================================================

SKILL_GERAR_ESCALA = Skill(
    id="gerar_escala",
    name="Gerar Escala",
    description="Gera escala de trabalho automaticamente",
    category=SkillCategory.GENERATION,
    required_permissions=["operacoes.escalas.criar"],
    parameters={
        "post_id": {"type": "uuid", "required": True},
        "scale_type": {"type": "enum", "required": True, "values": ["12x36", "6x1", "5x2", "4x2", "administrativo"]},
        "month": {"type": "int", "required": True},
        "year": {"type": "int", "required": True},
        "employee_ids": {"type": "list[uuid]", "required": True}
    },
    handler=None,
    examples=[
        "Gera escala 12x36 para janeiro",
        "Monta escala do posto X",
        "Cria escala administrativa"
    ]
)

SKILL_GERAR_RELATORIO = Skill(
    id="gerar_relatorio",
    name="Gerar Relatório",
    description="Gera relatório operacional",
    category=SkillCategory.GENERATION,
    required_permissions=["operacoes.relatorios.gerar"],
    parameters={
        "report_type": {"type": "enum", "required": True, "values": ["cobertura", "horas_extras", "ocorrencias", "substituicoes", "disciplinar"]},
        "start_date": {"type": "date", "required": True},
        "end_date": {"type": "date", "required": True},
        "format": {"type": "enum", "required": False, "values": ["pdf", "excel", "json"], "default": "pdf"}
    },
    handler=None,
    examples=[
        "Gera relatório de cobertura do mês",
        "Exporta relatório de horas extras em Excel",
        "Relatório de ocorrências para o cliente"
    ]
)

# =============================================================================
# SKILLS DE PREVISÃO
# =============================================================================

SKILL_PREVER_AUSENCIAS = Skill(
    id="prever_ausencias",
    name="Prever Ausências",
    description="Prevê ausências prováveis usando IA",
    category=SkillCategory.PREDICTION,
    required_permissions=["operacoes.analise_preditiva.visualizar"],
    parameters={
        "period_days": {"type": "int", "required": False, "default": 7},
        "post_id": {"type": "uuid", "required": False},
        "confidence_threshold": {"type": "float", "required": False, "default": 0.7}
    },
    handler=None,
    examples=[
        "Quem pode faltar essa semana?",
        "Previsão de ausências para o posto X",
        "Alerta de possíveis faltas"
    ]
)

SKILL_SUGERIR_SUBSTITUTO = Skill(
    id="sugerir_substituto",
    name="Sugerir Substituto",
    description="Sugere o melhor substituto para um turno",
    category=SkillCategory.PREDICTION,
    required_permissions=["operacoes.substituicoes.criar"],
    parameters={
        "shift_id": {"type": "uuid", "required": True},
        "max_suggestions": {"type": "int", "required": False, "default": 5}
    },
    handler=None,
    examples=[
        "Quem pode cobrir o turno do João?",
        "Sugere substituto para amanhã",
        "Melhor opção para cobrir o posto X"
    ]
)


# =============================================================================
# REGISTRO DE SKILLS
# =============================================================================

OPERATIONAL_SKILLS = {
    # Consultas
    "consultar_escala": SKILL_CONSULTAR_ESCALA,
    "consultar_presenca": SKILL_CONSULTAR_PRESENCA,
    "consultar_banco_horas": SKILL_CONSULTAR_BANCO_HORAS,
    "consultar_historico_disciplinar": SKILL_CONSULTAR_HISTORICO_DISCIPLINAR,

    # Ações
    "criar_ocorrencia": SKILL_CRIAR_OCORRENCIA,
    "solicitar_substituicao": SKILL_SOLICITAR_SUBSTITUICAO,
    "criar_advertencia": SKILL_CRIAR_ADVERTENCIA,

    # Análises
    "analisar_cobertura": SKILL_ANALISAR_COBERTURA,
    "analisar_horas_extras": SKILL_ANALISAR_HORAS_EXTRAS,

    # Geração
    "gerar_escala": SKILL_GERAR_ESCALA,
    "gerar_relatorio": SKILL_GERAR_RELATORIO,

    # Previsões
    "prever_ausencias": SKILL_PREVER_AUSENCIAS,
    "sugerir_substituto": SKILL_SUGERIR_SUBSTITUTO,
}
```

---

## 4. MCP SERVERS PARA OPERACIONAL

### 4.1 Arquitetura MCP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP SERVER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────┐     ┌───────────────────────┐                   │
│  │  mcp-operational      │     │  mcp-hr-integration   │                   │
│  │  (Operações Core)     │◄───►│  (Integração RH/DP)   │                   │
│  └───────────────────────┘     └───────────────────────┘                   │
│           │                              │                                  │
│           ▼                              ▼                                  │
│  ┌───────────────────────┐     ┌───────────────────────┐                   │
│  │  mcp-scale-optimizer  │     │  mcp-notification     │                   │
│  │  (Otimização Escalas) │     │  (Notificações)       │                   │
│  └───────────────────────┘     └───────────────────────┘                   │
│           │                              │                                  │
│           ▼                              ▼                                  │
│  ┌───────────────────────┐     ┌───────────────────────┐                   │
│  │  mcp-document-gen     │     │  mcp-analytics        │                   │
│  │  (Geração Documentos) │     │  (Analytics/BI)       │                   │
│  └───────────────────────┘     └───────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 MCP Server: Operacional Core

```python
# /backend/mcp/servers/operational_server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Any
import json


class OperationalMCPServer:
    """
    MCP Server para operações do módulo operacional.

    Expõe ferramentas que podem ser usadas por agentes de IA
    para executar ações no sistema operacional.
    """

    def __init__(self, db_session, services):
        self.server = Server("mcp-operational")
        self.db = db_session
        self.services = services
        self._register_tools()

    def _register_tools(self):
        """Registra todas as ferramentas do servidor."""

        # POSTOS
        @self.server.tool()
        async def list_posts(
            client_id: str = None,
            status: str = "ACTIVE",
            limit: int = 50
        ) -> str:
            """Lista postos de trabalho com filtros."""
            posts = await self.services.post_service.list_posts(
                client_id=client_id,
                status=status,
                limit=limit
            )
            return json.dumps([p.to_dict() for p in posts])

        @self.server.tool()
        async def get_post_coverage(
            post_id: str,
            date: str
        ) -> str:
            """Retorna cobertura de um posto em uma data."""
            coverage = await self.services.post_service.get_coverage(
                post_id=post_id,
                date=date
            )
            return json.dumps(coverage)

        # ESCALAS
        @self.server.tool()
        async def get_scale(
            post_id: str = None,
            employee_id: str = None,
            month: int = None,
            year: int = None
        ) -> str:
            """Consulta escala de trabalho."""
            scale = await self.services.scale_service.get_scale(
                post_id=post_id,
                employee_id=employee_id,
                month=month,
                year=year
            )
            return json.dumps(scale.to_dict() if scale else None)

        @self.server.tool()
        async def generate_scale(
            post_id: str,
            scale_type: str,
            month: int,
            year: int,
            employee_ids: list[str]
        ) -> str:
            """Gera escala automaticamente."""
            result = await self.services.scale_generator.generate(
                post_id=post_id,
                scale_type=scale_type,
                month=month,
                year=year,
                employee_ids=employee_ids
            )
            return json.dumps(result)

        # TURNOS
        @self.server.tool()
        async def get_current_shifts(
            post_id: str = None,
            client_id: str = None
        ) -> str:
            """Retorna turnos em andamento."""
            shifts = await self.services.shift_service.get_current_shifts(
                post_id=post_id,
                client_id=client_id
            )
            return json.dumps([s.to_dict() for s in shifts])

        @self.server.tool()
        async def register_check_in(
            shift_id: str,
            latitude: float = None,
            longitude: float = None,
            photo_path: str = None
        ) -> str:
            """Registra check-in de turno."""
            result = await self.services.shift_service.check_in(
                shift_id=shift_id,
                latitude=latitude,
                longitude=longitude,
                photo_path=photo_path
            )
            return json.dumps(result)

        # SUBSTITUIÇÕES
        @self.server.tool()
        async def suggest_substitutes(
            shift_id: str,
            max_suggestions: int = 5
        ) -> str:
            """Sugere substitutos para um turno."""
            suggestions = await self.services.substitution_service.suggest_substitutes(
                shift_id=shift_id,
                max_suggestions=max_suggestions
            )
            return json.dumps(suggestions)

        @self.server.tool()
        async def create_substitution_request(
            shift_id: str,
            reason: str,
            reason_details: str = None,
            substitute_employee_id: str = None
        ) -> str:
            """Cria solicitação de substituição."""
            result = await self.services.substitution_service.create_request(
                shift_id=shift_id,
                reason=reason,
                reason_details=reason_details,
                substitute_employee_id=substitute_employee_id
            )
            return json.dumps(result.to_dict())

        # BANCO DE HORAS
        @self.server.tool()
        async def get_time_bank_balance(
            employee_id: str
        ) -> str:
            """Retorna saldo de banco de horas."""
            balance = await self.services.time_bank_service.get_balance(
                employee_id=employee_id
            )
            return json.dumps(balance)

        @self.server.tool()
        async def get_expiring_time_bank(
            days_ahead: int = 30
        ) -> str:
            """Retorna horas próximas de vencer."""
            expiring = await self.services.time_bank_service.get_expiring(
                days_ahead=days_ahead
            )
            return json.dumps(expiring)

        # OCORRÊNCIAS
        @self.server.tool()
        async def create_occurrence(
            post_id: str,
            category: str,
            severity: str,
            title: str,
            description: str,
            employee_involved_id: str = None
        ) -> str:
            """Cria nova ocorrência."""
            result = await self.services.occurrence_service.create(
                post_id=post_id,
                category=category,
                severity=severity,
                title=title,
                description=description,
                employee_involved_id=employee_involved_id
            )
            return json.dumps(result.to_dict())

        @self.server.tool()
        async def list_pending_occurrences(
            post_id: str = None,
            client_id: str = None,
            severity: str = None
        ) -> str:
            """Lista ocorrências pendentes."""
            occurrences = await self.services.occurrence_service.list_pending(
                post_id=post_id,
                client_id=client_id,
                severity=severity
            )
            return json.dumps([o.to_dict() for o in occurrences])

        # MEDIDAS ADMINISTRATIVAS
        @self.server.tool()
        async def get_disciplinary_history(
            employee_id: str,
            months: int = 12
        ) -> str:
            """Retorna histórico disciplinar."""
            history = await self.services.disciplinary_service.get_history(
                employee_id=employee_id,
                months=months
            )
            return json.dumps(history)

        @self.server.tool()
        async def create_disciplinary_action(
            employee_id: str,
            action_type: str,
            reason_category: str,
            reason_description: str,
            occurrence_id: str = None
        ) -> str:
            """Cria medida administrativa (rascunho)."""
            result = await self.services.disciplinary_service.create_draft(
                employee_id=employee_id,
                action_type=action_type,
                reason_category=reason_category,
                reason_description=reason_description,
                occurrence_id=occurrence_id
            )
            return json.dumps(result.to_dict())

        # ANALYTICS
        @self.server.tool()
        async def get_operational_kpis(
            start_date: str,
            end_date: str,
            client_id: str = None
        ) -> str:
            """Retorna KPIs operacionais."""
            kpis = await self.services.analytics_service.get_kpis(
                start_date=start_date,
                end_date=end_date,
                client_id=client_id
            )
            return json.dumps(kpis)

        @self.server.tool()
        async def predict_absences(
            period_days: int = 7,
            confidence_threshold: float = 0.7
        ) -> str:
            """Prevê ausências prováveis."""
            predictions = await self.services.predictive_service.predict_absences(
                period_days=period_days,
                confidence_threshold=confidence_threshold
            )
            return json.dumps(predictions)
```

### 4.3 MCP Server: Integração RH/DP

```python
# /backend/mcp/servers/hr_integration_server.py

class HRIntegrationMCPServer:
    """
    MCP Server para integração entre Operacional e RH/DP.

    Facilita a comunicação bidirecional entre os módulos.
    """

    def __init__(self, db_session, services):
        self.server = Server("mcp-hr-integration")
        self.db = db_session
        self.services = services
        self._register_tools()

    def _register_tools(self):

        @self.server.tool()
        async def get_employee_info(
            employee_id: str,
            include_sensitive: bool = False
        ) -> str:
            """Retorna informações do funcionário."""
            pass

        @self.server.tool()
        async def notify_disciplinary_action(
            action_id: str
        ) -> str:
            """Notifica DP sobre medida administrativa."""
            pass

        @self.server.tool()
        async def register_absence(
            employee_id: str,
            absence_type: str,
            start_date: str,
            end_date: str,
            reason: str,
            document_path: str = None
        ) -> str:
            """Registra afastamento no DP."""
            pass

        @self.server.tool()
        async def send_overtime_to_payroll(
            employee_id: str,
            reference_month: str,
            overtime_data: dict
        ) -> str:
            """Envia horas extras para folha."""
            pass

        @self.server.tool()
        async def get_employee_schedule_constraints(
            employee_id: str
        ) -> str:
            """Retorna restrições de escala do funcionário."""
            pass
```

---

## 5. PADRÕES DE QUALIDADE DE CÓDIGO (99+/100)

### 5.1 Checklist de Qualidade

```python
# Padrões obrigatórios para todo código do módulo

"""
CHECKLIST DE QUALIDADE - CÓDIGO 99+/100
========================================

1. ESTRUTURA
   [x] Type hints em TODAS as funções e variáveis
   [x] Docstrings completas (Google style)
   [x] Classes com __slots__ quando aplicável
   [x] Dataclasses para DTOs
   [x] Enums para constantes

2. VALIDAÇÃO
   [x] Pydantic models para input
   [x] Field validators customizados
   [x] Model validators para regras complexas
   [x] Mensagens de erro claras em português

3. TRATAMENTO DE ERROS
   [x] Exceções customizadas por domínio
   [x] Try/except específicos (nunca bare except)
   [x] Logging de erros com contexto
   [x] Fallbacks e recuperação quando possível

4. SEGURANÇA
   [x] Validação de permissões em TODA action
   [x] Sanitização de inputs
   [x] SQL parameterizado (SQLAlchemy)
   [x] Soft delete (nunca hard delete)
   [x] Audit trail completo

5. PERFORMANCE
   [x] Índices em campos de busca frequente
   [x] Paginação obrigatória em listagens
   [x] Cache quando aplicável
   [x] Queries otimizadas (evitar N+1)
   [x] Async em operações I/O

6. TESTES
   [x] Cobertura mínima 90%
   [x] Testes unitários para services
   [x] Testes de integração para endpoints
   [x] Mocks para dependências externas
   [x] Fixtures reutilizáveis

7. DOCUMENTAÇÃO
   [x] Docstrings em todas as funções públicas
   [x] README.md atualizado
   [x] Exemplos de uso
   [x] Changelog mantido
"""

# Exemplo de classe com todos os padrões

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID
from enum import Enum
import logging

from pydantic import BaseModel, Field, validator, root_validator
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID

logger = logging.getLogger(__name__)


class OccurrenceSeverity(str, Enum):
    """Severidade de ocorrência."""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class OccurrenceCategory(str, Enum):
    """Categoria de ocorrência."""
    SEGURANCA = "seguranca"
    LIMPEZA = "limpeza"
    COMPORTAMENTO = "comportamento"
    ACIDENTE = "acidente"
    MANUTENCAO = "manutencao"
    OUTRO = "outro"


class OccurrenceError(Exception):
    """Exceção base para erros de ocorrência."""

    def __init__(self, message: str, code: str, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class OccurrenceNotFoundError(OccurrenceError):
    """Ocorrência não encontrada."""

    def __init__(self, occurrence_id: str):
        super().__init__(
            message=f"Ocorrência {occurrence_id} não encontrada",
            code="OCCURRENCE_NOT_FOUND",
            details={"occurrence_id": occurrence_id}
        )


class CreateOccurrenceRequest(BaseModel):
    """Request para criar ocorrência."""

    post_id: UUID = Field(..., description="ID do posto")
    category: OccurrenceCategory = Field(..., description="Categoria")
    severity: OccurrenceSeverity = Field(..., description="Severidade")
    title: str = Field(..., min_length=5, max_length=200, description="Título")
    description: str = Field(..., min_length=10, max_length=5000, description="Descrição")
    employee_involved_id: Optional[UUID] = Field(None, description="Funcionário envolvido")

    @validator('title')
    def title_must_be_meaningful(cls, v: str) -> str:
        """Valida que título é significativo."""
        if len(v.split()) < 2:
            raise ValueError("Título deve ter pelo menos 2 palavras")
        return v.strip()

    @root_validator
    def validate_severity_category_combination(cls, values: Dict) -> Dict:
        """Valida combinação de severidade e categoria."""
        category = values.get('category')
        severity = values.get('severity')

        # Acidente deve ser pelo menos ALTA
        if category == OccurrenceCategory.ACIDENTE and severity == OccurrenceSeverity.BAIXA:
            raise ValueError("Ocorrência de acidente não pode ter severidade BAIXA")

        return values

    class Config:
        schema_extra = {
            "example": {
                "post_id": "550e8400-e29b-41d4-a716-446655440000",
                "category": "comportamento",
                "severity": "media",
                "title": "Atraso no início do turno",
                "description": "Funcionário chegou 30 minutos atrasado sem justificativa",
                "employee_involved_id": "660e8400-e29b-41d4-a716-446655440001"
            }
        }


@dataclass
class OccurrenceDTO:
    """DTO para ocorrência."""

    __slots__ = [
        'id', 'code', 'post_id', 'category', 'severity', 'title',
        'description', 'status', 'created_at', 'created_by'
    ]

    id: UUID
    code: str
    post_id: UUID
    category: OccurrenceCategory
    severity: OccurrenceSeverity
    title: str
    description: str
    status: str
    created_at: datetime
    created_by: UUID

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "post_id": str(self.post_id),
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "created_by": str(self.created_by)
        }


class OccurrenceService:
    """
    Service para gestão de ocorrências.

    Responsável por toda lógica de negócio relacionada a ocorrências,
    incluindo criação, análise, resolução e integração com outros módulos.

    Attributes:
        repository: Repositório de ocorrências
        notification_service: Serviço de notificações
        ai_analyzer: Analisador de IA para classificação

    Example:
        >>> service = OccurrenceService(repo, notifier, analyzer)
        >>> occurrence = await service.create(request, user_id)
        >>> print(occurrence.code)
        'OCC-2026-00001'
    """

    def __init__(
        self,
        repository: "OccurrenceRepository",
        notification_service: "NotificationService",
        ai_analyzer: Optional["OccurrenceAnalyzer"] = None
    ):
        self.repository = repository
        self.notification_service = notification_service
        self.ai_analyzer = ai_analyzer
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def create(
        self,
        request: CreateOccurrenceRequest,
        created_by: UUID,
        tenant_id: UUID
    ) -> OccurrenceDTO:
        """
        Cria nova ocorrência.

        Args:
            request: Dados da ocorrência
            created_by: ID do usuário que está criando
            tenant_id: ID do tenant

        Returns:
            OccurrenceDTO com dados da ocorrência criada

        Raises:
            OccurrenceError: Se houver erro na criação

        Example:
            >>> request = CreateOccurrenceRequest(...)
            >>> occurrence = await service.create(request, user_id, tenant_id)
        """
        self._logger.info(
            "Criando ocorrência",
            extra={
                "post_id": str(request.post_id),
                "category": request.category.value,
                "severity": request.severity.value,
                "created_by": str(created_by)
            }
        )

        try:
            # Gera código único
            code = await self._generate_code(tenant_id)

            # Analisa com IA se disponível
            ai_suggestions = None
            if self.ai_analyzer:
                ai_suggestions = await self.ai_analyzer.analyze(
                    description=request.description,
                    category=request.category
                )

            # Cria no banco
            occurrence = await self.repository.create(
                code=code,
                tenant_id=tenant_id,
                post_id=request.post_id,
                category=request.category,
                severity=request.severity,
                title=request.title,
                description=request.description,
                employee_involved_id=request.employee_involved_id,
                created_by=created_by,
                ai_suggestions=ai_suggestions
            )

            # Notifica se crítica
            if request.severity == OccurrenceSeverity.CRITICA:
                await self._notify_critical_occurrence(occurrence)

            self._logger.info(
                "Ocorrência criada com sucesso",
                extra={"occurrence_id": str(occurrence.id), "code": code}
            )

            return self._to_dto(occurrence)

        except Exception as e:
            self._logger.error(
                "Erro ao criar ocorrência",
                extra={"error": str(e), "post_id": str(request.post_id)},
                exc_info=True
            )
            raise OccurrenceError(
                message="Erro ao criar ocorrência",
                code="CREATE_ERROR",
                details={"original_error": str(e)}
            )

    async def _generate_code(self, tenant_id: UUID) -> str:
        """Gera código único para ocorrência."""
        year = datetime.now().year
        sequence = await self.repository.get_next_sequence(tenant_id, year)
        return f"OCC-{year}-{sequence:05d}"

    async def _notify_critical_occurrence(self, occurrence) -> None:
        """Notifica gestores sobre ocorrência crítica."""
        await self.notification_service.send_critical_alert(
            title=f"[CRÍTICO] {occurrence.title}",
            body=occurrence.description[:200],
            reference_type="occurrence",
            reference_id=str(occurrence.id),
            target_roles=["gerente_operacoes", "supervisor_operacoes"]
        )

    def _to_dto(self, occurrence) -> OccurrenceDTO:
        """Converte model para DTO."""
        return OccurrenceDTO(
            id=occurrence.id,
            code=occurrence.code,
            post_id=occurrence.post_id,
            category=occurrence.category,
            severity=occurrence.severity,
            title=occurrence.title,
            description=occurrence.description,
            status=occurrence.status,
            created_at=occurrence.created_at,
            created_by=occurrence.created_by
        )
```

---

## 6. PRÓXIMOS PASSOS

### 6.1 Implementação Imediata

1. **Criar estrutura de agentes** (`/backend/modules/ai/agents/`)
2. **Definir skills operacionais** (`/backend/modules/ai/skills/`)
3. **Configurar MCP servers** (`/backend/mcp/servers/`)
4. **Expandir knowledge base do Bartolo**

### 6.2 Integração com Bartolo Existente

1. Registrar agentes no `bartolo_engine.py`
2. Conectar skills aos handlers
3. Configurar roteamento por perfil de usuário
4. Implementar fallbacks e recuperação

### 6.3 Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Tempo de resposta do agente | < 2s |
| Precisão de classificação de ocorrências | > 95% |
| Taxa de aceitação de sugestões de substituto | > 80% |
| Cobertura de testes | > 90% |
| Score de qualidade de código | 99+/100 |

---

*Documento gerado em 2026-01-18*
*Versão 1.0*
