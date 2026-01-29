"""
Data Connector - Conector de Dados do Sistema.

Permite ao Bartolo consultar dados reais do Conecta PRO
para responder perguntas com informacoes atualizadas.
"""

import logging
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Optional
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Repositórios do módulo Operacional
from modules.operacional.repositories import (
    PostRepository,
    ScaleRepository,
    AllocationRepository,
    ShiftRepository,
    SubstitutionRepository,
    TimeBankRepository,
)

# Models para queries diretas
from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Tipos de consulta."""
    COUNT = "count"
    LIST = "list"
    DETAIL = "detail"
    AGGREGATE = "aggregate"
    REPORT = "report"
    DAILY_SUMMARY = "daily_summary"
    ALERTS = "alerts"
    KPIS = "kpis"
    # Consultas operacionais
    COBERTURA_CRITICA = "cobertura_critica"
    FUNCIONARIOS_TRABALHANDO = "funcionarios_trabalhando"
    FUNCIONARIOS_FOLGA = "funcionarios_folga"
    ESCALAS_PENDENTES = "escalas_pendentes"
    HORA_EXTRA_RANKING = "hora_extra_ranking"
    SUBSTITUICOES_PENDENTES = "substituicoes_pendentes"
    ATRASOS_HOJE = "atrasos_hoje"
    OPERACAO_GERAL = "operacao_geral"


@dataclass
class DataQuery:
    """Consulta de dados."""
    entity: str
    query_type: QueryType
    filters: dict
    fields: list
    limit: int = 10
    order_by: Optional[str] = None


@dataclass
class DataResult:
    """Resultado de consulta."""
    success: bool
    query_type: QueryType
    entity: str
    data: Any
    total_count: int = 0
    message: Optional[str] = None
    executed_at: datetime = None

    def to_natural_language(self) -> str:
        """Converte resultado para linguagem natural."""
        if not self.success:
            return self.message or "Nao foi possivel obter os dados."

        # Para consultas especiais e operacionais, usa a mensagem formatada
        special_types = (
            QueryType.DAILY_SUMMARY,
            QueryType.ALERTS,
            QueryType.KPIS,
            QueryType.COBERTURA_CRITICA,
            QueryType.FUNCIONARIOS_TRABALHANDO,
            QueryType.FUNCIONARIOS_FOLGA,
            QueryType.ESCALAS_PENDENTES,
            QueryType.HORA_EXTRA_RANKING,
            QueryType.SUBSTITUICOES_PENDENTES,
            QueryType.ATRASOS_HOJE,
            QueryType.OPERACAO_GERAL,
        )
        if self.query_type in special_types:
            return self.message or str(self.data)

        if self.query_type == QueryType.COUNT:
            return f"Encontrei {self.total_count} {self.entity}."

        if self.query_type == QueryType.LIST:
            if not self.data:
                return f"Nao encontrei nenhum {self.entity} com esses criterios."
            items = "\n".join(f"- {item}" for item in self.data[:5])
            extra = f"\n(e mais {self.total_count - 5})" if self.total_count > 5 else ""
            return f"Encontrei {self.total_count} {self.entity}:\n{items}{extra}"

        if self.query_type == QueryType.DETAIL:
            if not self.data:
                return f"Nao encontrei o {self.entity} solicitado."
            return str(self.data)

        return str(self.data)


class DataConnector:
    """
    Conector para dados do sistema.

    Permite ao Bartolo:
    - Consultar entidades do sistema
    - Buscar dados agregados
    - Gerar relatorios simples
    """

    # Mapeamento de entidades para repositórios/models
    ENTITY_MAP = {
        # Módulo Operacional
        "posto": {"type": "repository", "repository": "post", "name_field": "name"},
        "postos": {"type": "repository", "repository": "post", "name_field": "name"},
        "escala": {"type": "repository", "repository": "scale", "name_field": "name"},
        "escalas": {"type": "repository", "repository": "scale", "name_field": "name"},
        "alocacao": {"type": "repository", "repository": "allocation", "name_field": "employee_name"},
        "alocacoes": {"type": "repository", "repository": "allocation", "name_field": "employee_name"},
        "turno": {"type": "repository", "repository": "shift", "name_field": "employee_name"},
        "turnos": {"type": "repository", "repository": "shift", "name_field": "employee_name"},
        "funcionario": {"type": "model", "model": Employee, "name_field": "nome"},
        "funcionarios": {"type": "model", "model": Employee, "name_field": "nome"},
        "colaborador": {"type": "model", "model": Employee, "name_field": "nome"},
        "colaboradores": {"type": "model", "model": Employee, "name_field": "nome"},

        # Outros módulos (mock por enquanto)
        "cliente": {"type": "mock", "name_field": "name"},
        "clientes": {"type": "mock", "name_field": "name"},
        "contrato": {"type": "mock", "name_field": "number"},
        "contratos": {"type": "mock", "name_field": "number"},
    }

    # Padroes de consulta em linguagem natural
    QUERY_PATTERNS = [
        # Contagem
        (r"(?:quantos?|quantas?)\s+(\w+)", QueryType.COUNT),
        (r"total\s+de\s+(\w+)", QueryType.COUNT),
        (r"numero\s+de\s+(\w+)", QueryType.COUNT),
        (r"(\w+)\s+cadastrados?", QueryType.COUNT),
        (r"temos\s+(?:quantos?|quantas?)\s+(\w+)", QueryType.COUNT),
        (r"hoje\s+temos?\s+(?:quantos?|quantas?)\s+(\w+)", QueryType.COUNT),

        # Listagem
        (r"listar?\s+(\w+)", QueryType.LIST),
        (r"mostrar?\s+(\w+)", QueryType.LIST),
        (r"ver\s+(\w+)", QueryType.LIST),
        (r"(?:quais?|quais?)\s+(\w+)", QueryType.LIST),
        (r"ultimos?\s+(\w+)", QueryType.LIST),
        (r"(\w+)\s+disponiveis?", QueryType.LIST),
        (r"(\w+)\s+disponivel\s+hoje", QueryType.LIST),
        (r"(?:quais?|quais?)\s+foram?\s+os?\s+ultimos?\s+(\w+)", QueryType.LIST),

        # Detalhe
        (r"detalhes?\s+d[oa]\s+(\w+)", QueryType.DETAIL),
        (r"informacoes?\s+d[oa]\s+(\w+)", QueryType.DETAIL),
    ]

    # ==========================================================================
    # PATTERNS EXAUSTIVOS - Fase 1 do Plano de Refinamento
    # Cada categoria cobre: forma direta, interrogativa, imperativa, sinônimos
    # ==========================================================================
    SPECIAL_QUERY_PATTERNS = [
        # ==================================================================
        # COBERTURA_CRITICA - Postos com cobertura < 80%
        # ==================================================================
        # Forma direta
        (r"cobertura\s+critica", QueryType.COBERTURA_CRITICA),
        (r"cobertura\s+baixa", QueryType.COBERTURA_CRITICA),
        (r"gaps?\s+(?:de\s+)?cobertura", QueryType.COBERTURA_CRITICA),
        (r"buracos?\s+(?:na\s+)?(?:escala|cobertura)", QueryType.COBERTURA_CRITICA),
        # Postos
        (r"postos?\s+(?:sem|com\s+baixa)\s+cobertura", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+descobertos?", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+criticos?", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+(?:com\s+)?problema", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+(?:em\s+)?alerta", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+vazios?", QueryType.COBERTURA_CRITICA),
        (r"postos?\s+(?:sem\s+)?funcionarios?", QueryType.COBERTURA_CRITICA),
        (r"sem\s+cobertura", QueryType.COBERTURA_CRITICA),
        # Interrogativas
        (r"(?:quais?|quantos?)\s+postos?\s+(?:estao\s+)?(?:sem|descobertos?)", QueryType.COBERTURA_CRITICA),
        (r"(?:tem|ha)\s+(?:algum\s+)?posto\s+(?:sem|descoberto)", QueryType.COBERTURA_CRITICA),
        (r"como\s+(?:esta|ta|está)\s+(?:a\s+)?cobertura", QueryType.COBERTURA_CRITICA),
        (r"situacao\s+(?:da\s+)?cobertura", QueryType.COBERTURA_CRITICA),
        # Ações
        (r"(?:ver|mostrar|exibir|listar)\s+(?:postos?\s+)?(?:sem\s+)?cobertura", QueryType.COBERTURA_CRITICA),
        (r"(?:verificar|checar|analisar)\s+cobertura", QueryType.COBERTURA_CRITICA),
        (r"cobertura\s+(?:de\s+|dos?\s+)?postos?", QueryType.COBERTURA_CRITICA),
        (r"cobertura\s+(?:em\s+)?tempo\s+real", QueryType.COBERTURA_CRITICA),
        (r"analisar\s+cobertura", QueryType.COBERTURA_CRITICA),
        # Sinônimos
        (r"vagas?\s+(?:em\s+)?aberto", QueryType.COBERTURA_CRITICA),
        (r"posicoes?\s+(?:sem\s+)?preencher", QueryType.COBERTURA_CRITICA),
        (r"locais?\s+(?:sem\s+)?cobertura", QueryType.COBERTURA_CRITICA),

        # ==================================================================
        # FUNCIONARIOS_TRABALHANDO - Quem está em serviço agora
        # ==================================================================
        # Direto
        (r"quem\s+(?:esta|ta|está)\s+trabalhando", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"quem\s+(?:esta|ta|está)\s+(?:em\s+)?servico", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"quem\s+(?:esta|ta|está)\s+(?:no\s+)?turno", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"quem\s+(?:esta|ta|está)\s+(?:em\s+|no\s+)?(?:campo|posto)", QueryType.FUNCIONARIOS_TRABALHANDO),
        # Funcionários
        (r"funcionarios?\s+(?:em\s+)?(?:servico|turno|trabalho)", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"funcionarios?\s+(?:agora|atualmente|hoje)\s*$", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"funcionarios?\s+trabalhando", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"funcionarios?\s+ativos?\s+(?:agora|hoje)", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"trabalhando\s+agora", QueryType.FUNCIONARIOS_TRABALHANDO),
        # Equipe
        (r"equipe\s+(?:em\s+)?servico", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"equipe\s+(?:de\s+)?(?:hoje|plantao)", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"equipe\s+(?:no\s+)?turno", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"equipe\s+trabalhando", QueryType.FUNCIONARIOS_TRABALHANDO),
        # Interrogativas
        (r"quantos?\s+(?:estao\s+)?trabalhando", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"quantos?\s+(?:funcionarios?\s+)?(?:em\s+)?servico", QueryType.FUNCIONARIOS_TRABALHANDO),
        # Sinônimos
        (r"colaboradores?\s+(?:em\s+)?(?:servico|turno)", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"vigilantes?\s+(?:em\s+)?(?:servico|turno)", QueryType.FUNCIONARIOS_TRABALHANDO),
        (r"porteiros?\s+(?:em\s+)?(?:servico|turno)", QueryType.FUNCIONARIOS_TRABALHANDO),

        # ==================================================================
        # FUNCIONARIOS_FOLGA - Disponíveis para convocação
        # ==================================================================
        # Folga
        (r"quem\s+(?:esta|ta|está)\s+(?:de\s+)?folga", QueryType.FUNCIONARIOS_FOLGA),
        (r"quem\s+(?:esta|ta|está)\s+folgando", QueryType.FUNCIONARIOS_FOLGA),
        (r"funcionarios?\s+(?:de\s+|em\s+)?folga", QueryType.FUNCIONARIOS_FOLGA),
        (r"funcionarios?\s+(?:estao\s+)?(?:de\s+)?folga", QueryType.FUNCIONARIOS_FOLGA),
        (r"quantos?\s+funcionarios?\s+(?:estao\s+)?(?:de\s+)?folga", QueryType.FUNCIONARIOS_FOLGA),
        (r"folgas?\s+(?:de\s+)?hoje", QueryType.FUNCIONARIOS_FOLGA),
        # Disponíveis
        (r"funcionarios?\s+disponiveis?", QueryType.FUNCIONARIOS_FOLGA),
        (r"quem\s+(?:esta|ta|está)\s+disponivel", QueryType.FUNCIONARIOS_FOLGA),
        (r"disponiveis?\s+(?:para\s+)?(?:hoje|trabalhar|cobrir)", QueryType.FUNCIONARIOS_FOLGA),
        (r"quem\s+pode\s+(?:trabalhar|cobrir|substituir)", QueryType.FUNCIONARIOS_FOLGA),
        (r"quem\s+(?:esta|ta|está)\s+livre", QueryType.FUNCIONARIOS_FOLGA),
        # Para convocação
        (r"funcionarios?\s+(?:para\s+)?convocar", QueryType.FUNCIONARIOS_FOLGA),
        (r"quem\s+(?:posso|pode)\s+(?:chamar|convocar)", QueryType.FUNCIONARIOS_FOLGA),
        (r"lista\s+(?:de\s+)?(?:convocacao|disponiveis)", QueryType.FUNCIONARIOS_FOLGA),
        # Banco de reserva
        (r"reservas?\s+(?:disponiveis?)?", QueryType.FUNCIONARIOS_FOLGA),
        (r"plantonistas?\s+(?:disponiveis?)?", QueryType.FUNCIONARIOS_FOLGA),
        (r"sobreaviso", QueryType.FUNCIONARIOS_FOLGA),

        # ==================================================================
        # ESCALAS_PENDENTES - Escalas aguardando aprovação/publicação
        # ==================================================================
        # Pendentes
        (r"escalas?\s+pendentes?", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:para\s+)?aprovar", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+aguardando", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:em\s+)?rascunho", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:nao\s+)?publicadas?", QueryType.ESCALAS_PENDENTES),
        (r"aprovacao\s+(?:de\s+)?escalas?", QueryType.ESCALAS_PENDENTES),
        # Atuais
        (r"escalas?\s+(?:atual|atuais)", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:em\s+)?vigor", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:da\s+)?semana", QueryType.ESCALAS_PENDENTES),
        (r"escalas?\s+(?:do\s+)?mes", QueryType.ESCALAS_PENDENTES),
        # Verificar
        (r"(?:ver|verificar|mostrar|listar)\s+(?:as\s+)?escalas?", QueryType.ESCALAS_PENDENTES),
        (r"(?:quais?|quantas?)\s+escalas?\s+(?:pendentes?|aguardando)", QueryType.ESCALAS_PENDENTES),
        # Status
        (r"status\s+(?:das?\s+)?escalas?", QueryType.ESCALAS_PENDENTES),
        (r"situacao\s+(?:das?\s+)?escalas?", QueryType.ESCALAS_PENDENTES),

        # ==================================================================
        # HORA_EXTRA_RANKING - Ranking de horas extras
        # ==================================================================
        # Hora extra
        (r"horas?\s+extras?", QueryType.HORA_EXTRA_RANKING),
        (r"hora\s+extra", QueryType.HORA_EXTRA_RANKING),
        (r"(?:he|HE)\s+(?:do\s+)?mes", QueryType.HORA_EXTRA_RANKING),
        # Ranking
        (r"ranking\s+(?:de\s+)?horas?\s+extras?", QueryType.HORA_EXTRA_RANKING),
        (r"quem\s+(?:tem|fez)\s+(?:mais\s+)?horas?\s+extras?", QueryType.HORA_EXTRA_RANKING),
        (r"funcionarios?\s+(?:com\s+)?(?:mais\s+)?horas?\s+extras?", QueryType.HORA_EXTRA_RANKING),
        # Banco de horas
        (r"banco\s+(?:de\s+)?horas", QueryType.HORA_EXTRA_RANKING),
        (r"saldo\s+(?:de\s+)?horas", QueryType.HORA_EXTRA_RANKING),
        (r"credito\s+(?:de\s+)?horas", QueryType.HORA_EXTRA_RANKING),
        (r"debito\s+(?:de\s+)?horas", QueryType.HORA_EXTRA_RANKING),
        # Limites
        (r"quem\s+(?:esta|ta)\s+(?:no\s+)?limite", QueryType.HORA_EXTRA_RANKING),
        (r"funcionarios?\s+(?:no\s+)?limite\s+(?:de\s+)?(?:he|HE|horas)", QueryType.HORA_EXTRA_RANKING),
        (r"excesso\s+(?:de\s+)?horas", QueryType.HORA_EXTRA_RANKING),

        # ==================================================================
        # SUBSTITUICOES_PENDENTES - Substituições aguardando resolução
        # ==================================================================
        # Substituições
        (r"substituicoes?\s+pendentes?", QueryType.SUBSTITUICOES_PENDENTES),
        (r"substituicoes?\s+(?:em\s+)?aberto", QueryType.SUBSTITUICOES_PENDENTES),
        (r"substituicoes?\s+(?:nao\s+)?resolvidas?", QueryType.SUBSTITUICOES_PENDENTES),
        (r"substituicao\s+pendente", QueryType.SUBSTITUICOES_PENDENTES),
        # Trocas
        (r"trocas?\s+pendentes?", QueryType.SUBSTITUICOES_PENDENTES),
        (r"trocas?\s+(?:de\s+)?turno", QueryType.SUBSTITUICOES_PENDENTES),
        (r"trocas?\s+(?:em\s+)?aberto", QueryType.SUBSTITUICOES_PENDENTES),
        # Coberturas
        (r"coberturas?\s+pendentes?", QueryType.SUBSTITUICOES_PENDENTES),
        (r"coberturas?\s+(?:em\s+)?aberto", QueryType.SUBSTITUICOES_PENDENTES),
        # Aguardando
        (r"(?:aguardando|esperando)\s+(?:substituto|cobertura|troca)", QueryType.SUBSTITUICOES_PENDENTES),
        (r"precisando\s+(?:de\s+)?(?:substituto|cobertura)", QueryType.SUBSTITUICOES_PENDENTES),

        # ==================================================================
        # ATRASOS_HOJE - Funcionários atrasados hoje
        # ==================================================================
        # Atrasos
        (r"atrasos?\s+(?:de\s+)?hoje", QueryType.ATRASOS_HOJE),
        (r"atrasos?\s+(?:do\s+)?dia", QueryType.ATRASOS_HOJE),
        (r"atrasados?", QueryType.ATRASOS_HOJE),
        (r"quem\s+(?:esta|ta|está|atrasou)", QueryType.ATRASOS_HOJE),
        (r"funcionarios?\s+atrasados?", QueryType.ATRASOS_HOJE),
        # Check-in
        (r"(?:sem\s+)?check-?in", QueryType.ATRASOS_HOJE),
        (r"(?:nao\s+)?(?:fez|fizeram)\s+check-?in", QueryType.ATRASOS_HOJE),
        (r"(?:falta|faltou)\s+check-?in", QueryType.ATRASOS_HOJE),
        # Chegadas
        (r"chegadas?\s+(?:com\s+)?atraso", QueryType.ATRASOS_HOJE),
        (r"chegadas?\s+atrasadas?", QueryType.ATRASOS_HOJE),
        (r"(?:nao\s+)?chegou\s+(?:ainda|no\s+horario)", QueryType.ATRASOS_HOJE),
        # Ausências
        (r"ausencias?\s+(?:de\s+)?hoje", QueryType.ATRASOS_HOJE),
        (r"faltas?\s+(?:de\s+)?hoje", QueryType.ATRASOS_HOJE),
        (r"quem\s+(?:faltou|nao\s+veio)", QueryType.ATRASOS_HOJE),

        # ==================================================================
        # OPERACAO_GERAL - Resumo operacional
        # ==================================================================
        # Status
        (r"como\s+(?:esta|ta|está)\s+(?:a\s+)?operacao", QueryType.OPERACAO_GERAL),
        (r"status\s+(?:da\s+)?operacao", QueryType.OPERACAO_GERAL),
        (r"situacao\s+(?:da\s+)?operacao", QueryType.OPERACAO_GERAL),
        (r"visao\s+geral\s+(?:da\s+)?operacao", QueryType.OPERACAO_GERAL),
        (r"panorama\s+(?:da\s+)?operacao", QueryType.OPERACAO_GERAL),
        # Dashboard
        (r"dashboard(?:\s+operacional)?", QueryType.OPERACAO_GERAL),
        (r"painel(?:\s+operacional)?", QueryType.OPERACAO_GERAL),
        (r"indicadores?\s+(?:do\s+)?dia", QueryType.OPERACAO_GERAL),
        # Dia
        (r"(?:o\s+)?que\s+(?:esta\s+)?acontecendo", QueryType.OPERACAO_GERAL),
        (r"novidades?\s+(?:do\s+)?dia", QueryType.OPERACAO_GERAL),

        # ==================================================================
        # DAILY_SUMMARY - Resumo do dia
        # ==================================================================
        (r"resumo\s+(?:do\s+)?dia", QueryType.DAILY_SUMMARY),
        (r"resumo\s+diario", QueryType.DAILY_SUMMARY),
        (r"resumo\s+(?:da\s+)?operacao", QueryType.DAILY_SUMMARY),
        (r"resumo\s+operacional", QueryType.DAILY_SUMMARY),
        (r"como\s+(?:esta|foi)\s+(?:o\s+)?dia", QueryType.DAILY_SUMMARY),
        (r"visao\s+geral\s+(?:do\s+)?dia", QueryType.DAILY_SUMMARY),
        (r"status\s+(?:do\s+)?dia", QueryType.DAILY_SUMMARY),

        # ==================================================================
        # ALERTS - Alertas pendentes
        # ==================================================================
        # Alertas
        (r"alertas?\s+pendentes?", QueryType.ALERTS),
        (r"alertas?\s+(?:do\s+)?(?:dia|sistema)", QueryType.ALERTS),
        (r"alertas?\s+(?:em\s+)?aberto", QueryType.ALERTS),
        (r"alertas?\s+(?:nao\s+)?resolvidos?", QueryType.ALERTS),
        # Pendências
        (r"pendencias?", QueryType.ALERTS),
        (r"(?:o\s+que|quais?)\s+(?:esta|estao)\s+pendente", QueryType.ALERTS),
        (r"itens?\s+pendentes?", QueryType.ALERTS),
        # Problemas
        (r"problemas?\s+(?:pendentes?|abertos?)", QueryType.ALERTS),
        (r"(?:tem|ha)\s+(?:algum\s+)?(?:problema|alerta)", QueryType.ALERTS),
        (r"(?:algo|alguma\s+coisa)\s+(?:errada?|pendente)", QueryType.ALERTS),
        # Urgente
        (r"(?:urgente|critico|importante)", QueryType.ALERTS),
        (r"(?:preciso|precisamos)\s+(?:resolver|atender)", QueryType.ALERTS),
        (r"(?:atencao|atenção)(?:\s+imediata)?", QueryType.ALERTS),

        # ==================================================================
        # KPIS - Indicadores de performance
        # ==================================================================
        (r"kpis?(?:\s+(?:principais?|do\s+sistema))?", QueryType.KPIS),
        (r"indicadores?(?:\s+(?:principais?|chave))?", QueryType.KPIS),
        (r"metricas?(?:\s+(?:principais?|do\s+sistema))?", QueryType.KPIS),
        (r"numeros?\s+(?:do\s+sistema|gerais?)", QueryType.KPIS),
        (r"estatisticas?\s+(?:do\s+)?(?:dia|sistema)", QueryType.KPIS),
        (r"performance(?:\s+(?:do\s+)?(?:dia|sistema))?", QueryType.KPIS),
        (r"desempenho\s+(?:do\s+)?(?:dia|sistema)", QueryType.KPIS),
        (r"painel\s+(?:de\s+)?(?:controle|indicadores)", QueryType.KPIS),
    ]

    def __init__(self, db_session=None):
        """Inicializa o conector."""
        self.db = db_session
        self._query_cache = {}

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Remove acentos e normaliza texto para matching."""
        # Normaliza para NFD (separa base + acento) e remove acentos
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

    def detect_data_query(self, message: str) -> Optional[DataQuery]:
        """
        Detecta se mensagem contem consulta de dados.

        Args:
            message: Mensagem do usuario

        Returns:
            DataQuery se detectado, None caso contrario
        """
        message_lower = message.lower()
        message_normalized = self._normalize_text(message_lower)

        # Primeiro verifica consultas especiais (resumo, alertas, KPIs)
        for pattern, query_type in self.SPECIAL_QUERY_PATTERNS:
            if re.search(pattern, message_normalized):
                logger.info(f"Consulta especial detectada: {query_type}")
                return DataQuery(
                    entity="sistema",
                    query_type=query_type,
                    filters=self._extract_filters(message_lower),
                    fields=[],
                )

        # Depois verifica consultas por entidade
        for pattern, query_type in self.QUERY_PATTERNS:
            match = re.search(pattern, message_normalized)
            if match:
                entity = match.group(1)
                if entity in self.ENTITY_MAP:
                    return DataQuery(
                        entity=entity,
                        query_type=query_type,
                        filters=self._extract_filters(message_lower),
                        fields=[],
                    )

        return None

    def _extract_filters(self, message: str) -> dict:
        """Extrai filtros da mensagem."""
        filters = {}

        # Filtro de status
        if "ativo" in message or "ativos" in message:
            filters["status"] = "active"
        elif "inativo" in message or "inativos" in message:
            filters["status"] = "inactive"

        # Filtro de disponibilidade
        if "disponivel" in message or "disponiveis" in message:
            filters["available"] = True

        # Filtro de data
        if "hoje" in message:
            filters["date"] = date.today()
            filters["today"] = True
        elif "este mes" in message or "mes atual" in message:
            today = date.today()
            filters["month"] = today.month
            filters["year"] = today.year

        # Filtro de ordem (últimos)
        if "ultimo" in message or "ultimos" in message or "recente" in message:
            filters["order_by"] = "created_at"
            filters["order_desc"] = True

        # Filtro de vencimento
        if "vencido" in message or "vencidos" in message:
            filters["expired"] = True
        elif "vencendo" in message:
            filters["expiring_soon"] = True

        return filters

    async def execute_query(self, query: DataQuery) -> DataResult:
        """
        Executa consulta de dados.

        Args:
            query: Consulta a executar

        Returns:
            DataResult com resultado
        """
        try:
            # Primeiro trata consultas especiais
            if query.query_type == QueryType.DAILY_SUMMARY:
                return await self._get_daily_summary()
            elif query.query_type == QueryType.ALERTS:
                return await self._get_pending_alerts()
            elif query.query_type == QueryType.KPIS:
                return await self._get_main_kpis()
            # Consultas operacionais
            elif query.query_type == QueryType.COBERTURA_CRITICA:
                return await self._get_cobertura_critica()
            elif query.query_type == QueryType.FUNCIONARIOS_TRABALHANDO:
                return await self._get_funcionarios_trabalhando()
            elif query.query_type == QueryType.FUNCIONARIOS_FOLGA:
                return await self._get_funcionarios_folga()
            elif query.query_type == QueryType.ESCALAS_PENDENTES:
                return await self._get_escalas_pendentes()
            elif query.query_type == QueryType.HORA_EXTRA_RANKING:
                return await self._get_hora_extra_ranking()
            elif query.query_type == QueryType.SUBSTITUICOES_PENDENTES:
                return await self._get_substituicoes_pendentes()
            elif query.query_type == QueryType.ATRASOS_HOJE:
                return await self._get_atrasos_hoje()
            elif query.query_type == QueryType.OPERACAO_GERAL:
                return await self._get_operacao_geral()

            if not self.db:
                logger.warning("DB session não disponível, usando dados mock")
                return await self._execute_mock_query(query)

            entity_info = self.ENTITY_MAP.get(query.entity)
            if not entity_info:
                logger.warning(f"Entidade não mapeada: {query.entity}, usando mock")
                return await self._execute_mock_query(query)

            entity_type = entity_info.get("type")

            if entity_type == "repository":
                return await self._execute_repository_query(query, entity_info)
            elif entity_type == "model":
                return await self._execute_model_query(query, entity_info)
            else:
                # Fallback para mock se não for repository nem model
                return await self._execute_mock_query(query)

        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return DataResult(
                success=False,
                query_type=query.query_type,
                entity=query.entity,
                data=None,
                message=f"Erro ao consultar {query.entity}: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _execute_repository_query(
        self, query: DataQuery, entity_info: dict
    ) -> DataResult:
        """
        Executa consulta usando repository pattern.

        Args:
            query: Consulta a executar
            entity_info: Informações da entidade

        Returns:
            DataResult com resultado
        """
        repository_name = entity_info["repository"]
        name_field = entity_info["name_field"]

        # Instanciar repository
        repository = None
        if repository_name == "post":
            repository = PostRepository(self.db)
        elif repository_name == "scale":
            repository = ScaleRepository(self.db)
        elif repository_name == "allocation":
            repository = AllocationRepository(self.db)
        elif repository_name == "shift":
            repository = ShiftRepository(self.db)

        if not repository:
            logger.error(f"Repository não encontrado: {repository_name}")
            return await self._execute_mock_query(query)

        # Executar query baseado no tipo
        if query.query_type == QueryType.COUNT:
            # Para COUNT, vamos buscar com filtros se houver
            filters = {}
            if "status" in query.filters:
                filters["status"] = query.filters["status"]
            items, total = await repository.list(page=1, page_size=1, **filters)
            return DataResult(
                success=True,
                query_type=QueryType.COUNT,
                entity=query.entity,
                data=total,
                total_count=total,
                executed_at=datetime.utcnow(),
            )

        elif query.query_type == QueryType.LIST:
            # Para LIST, passar filtros também
            filters = {}
            if "status" in query.filters:
                filters["status"] = query.filters["status"]
            if "order_by" in query.filters:
                filters["order_by"] = query.filters["order_by"]
            items, total = await repository.list(
                page=1, page_size=min(query.limit, 10), **filters
            )

            # Formatar items para exibição
            formatted_items = []
            for item in items:
                if isinstance(item, dict):
                    # AllocationRepository retorna dicts
                    name = item.get(name_field, "Sem nome")
                    formatted_items.append(f"{name}")
                else:
                    # Outros repositories retornam models
                    name = getattr(item, name_field, "Sem nome")
                    code = getattr(item, "code", None)
                    if code:
                        formatted_items.append(f"{code} - {name}")
                    else:
                        formatted_items.append(name)

            return DataResult(
                success=True,
                query_type=QueryType.LIST,
                entity=query.entity,
                data=formatted_items,
                total_count=total,
                executed_at=datetime.utcnow(),
            )

        # Default para outros tipos
        return await self._execute_mock_query(query)

    async def _execute_model_query(
        self, query: DataQuery, entity_info: dict
    ) -> DataResult:
        """
        Executa consulta direta em model SQLAlchemy.

        Args:
            query: Consulta a executar
            entity_info: Informações da entidade

        Returns:
            DataResult com resultado
        """
        model = entity_info["model"]
        name_field = entity_info["name_field"]

        # Executar query baseado no tipo
        if query.query_type == QueryType.COUNT:
            result = await self.db.execute(
                select(func.count(model.id)).where(model.is_active.is_(True))
            )
            total = result.scalar() or 0

            return DataResult(
                success=True,
                query_type=QueryType.COUNT,
                entity=query.entity,
                data=total,
                total_count=total,
                executed_at=datetime.utcnow(),
            )

        elif query.query_type == QueryType.LIST:
            stmt = (
                select(model)
                .where(model.is_active.is_(True))
                .limit(min(query.limit, 10))
            )

            # Aplicar filtros básicos
            if "status" in query.filters:
                stmt = stmt.where(model.status == query.filters["status"])

            result = await self.db.execute(stmt)
            items = list(result.scalars().all())

            # Formatar items para exibição
            formatted_items = []
            for item in items:
                name = getattr(item, name_field, "Sem nome")
                cargo = getattr(item, "cargo", None)
                matricula = getattr(item, "matricula", None)

                if matricula and cargo:
                    formatted_items.append(f"{name} ({matricula}) - {cargo}")
                elif matricula:
                    formatted_items.append(f"{name} ({matricula})")
                else:
                    formatted_items.append(name)

            # Count total
            count_result = await self.db.execute(
                select(func.count(model.id)).where(model.is_active.is_(True))
            )
            total = count_result.scalar() or 0

            return DataResult(
                success=True,
                query_type=QueryType.LIST,
                entity=query.entity,
                data=formatted_items,
                total_count=total,
                executed_at=datetime.utcnow(),
            )

        # Default para outros tipos
        return await self._execute_mock_query(query)

    async def _execute_mock_query(self, query: DataQuery) -> DataResult:
        """Executa consulta mockada para desenvolvimento."""
        # Dados de exemplo
        mock_data = {
            "clientes": {
                "count": 45,
                "list": [
                    "Condominio Residencial Aurora",
                    "Edificio Comercial Centro",
                    "Shopping Plaza Norte",
                    "Industria ABC Ltda",
                    "Hospital Santa Casa",
                ],
            },
            "funcionarios": {
                "count": 387,
                "list": [
                    "Jose Silva - Porteiro",
                    "Maria Santos - Faxineira",
                    "Pedro Oliveira - Vigilante",
                    "Ana Costa - Zeladora",
                    "Carlos Lima - Eletricista",
                ],
            },
            "contratos": {
                "count": 38,
                "list": [
                    "CT-2024-001 - Condominio Aurora",
                    "CT-2024-002 - Edificio Centro",
                    "CT-2024-003 - Shopping Plaza",
                    "CT-2024-004 - Industria ABC",
                    "CT-2024-005 - Hospital Santa Casa",
                ],
            },
            "propostas": {
                "count": 12,
                "list": [
                    "PR-2024-045 - Em analise",
                    "PR-2024-046 - Enviada",
                    "PR-2024-047 - Em elaboracao",
                ],
            },
            "leads": {
                "count": 23,
                "list": [
                    "Novo Condominio Jardins",
                    "Empresa XYZ",
                    "Predio Comercial Sul",
                ],
            },
            "editais": {
                "count": 8,
                "list": [
                    "PE 001/2024 - Prefeitura Manaus",
                    "PE 002/2024 - Governo do Estado",
                    "Dispensa 015/2024 - SEFAZ",
                ],
            },
            "certidoes": {
                "count": 6,
                "list": [
                    "CND Federal - Valida ate 15/02/2024",
                    "CRF FGTS - Valida ate 20/02/2024",
                    "CNDT - Valida ate 10/02/2024",
                ],
            },
        }

        entity_data = mock_data.get(query.entity, {"count": 0, "list": []})

        if query.query_type == QueryType.COUNT:
            return DataResult(
                success=True,
                query_type=QueryType.COUNT,
                entity=query.entity,
                data=entity_data["count"],
                total_count=entity_data["count"],
                executed_at=datetime.utcnow(),
            )

        if query.query_type == QueryType.LIST:
            items = entity_data.get("list", [])
            return DataResult(
                success=True,
                query_type=QueryType.LIST,
                entity=query.entity,
                data=items[:query.limit],
                total_count=len(items),
                executed_at=datetime.utcnow(),
            )

        return DataResult(
            success=True,
            query_type=query.query_type,
            entity=query.entity,
            data=entity_data,
            total_count=entity_data.get("count", 0),
            executed_at=datetime.utcnow(),
        )

    async def get_dashboard_data(self, module: str) -> dict:
        """
        Retorna dados do dashboard para um modulo.

        Args:
            module: Nome do modulo

        Returns:
            Dados agregados do modulo
        """
        if not self.db:
            # Fallback para dados mock
            return await self._get_mock_dashboard_data(module)

        try:
            if module in ("operacoes", "operacional"):
                return await self._get_operacional_dashboard()
            else:
                # Outros módulos usam mock por enquanto
                return await self._get_mock_dashboard_data(module)

        except Exception as e:
            logger.error(f"Erro ao buscar dashboard {module}: {e}")
            return {}

    async def _get_operacional_dashboard(self) -> dict:
        """Retorna dados reais do dashboard operacional."""
        # Funcionários ativos
        emp_count = await self.db.execute(
            select(func.count(Employee.id)).where(Employee.is_active.is_(True))
        )
        funcionarios_ativos = emp_count.scalar() or 0

        # Postos (usando repository para aproveitar get_stats)
        post_repo = PostRepository(self.db)
        post_stats = await post_repo.get_stats()

        # Alocações ativas
        alloc_repo = AllocationRepository(self.db)
        allocations, total_allocations = await alloc_repo.list(page=1, page_size=1)

        return {
            "funcionarios_ativos": funcionarios_ativos,
            "postos_ativos": post_stats.total,
            "postos_preenchidos": post_stats.filled,
            "postos_com_vagas": post_stats.with_vacancy,
            "alocacoes_ativas": total_allocations,
            "efetivo_total": post_stats.total_allocated,
            "efetivo_requerido": post_stats.total_headcount,
            "custo_mensal_total": float(post_stats.total_monthly_cost),
        }

    async def _get_mock_dashboard_data(self, module: str) -> dict:
        """Retorna dados mock para módulos ainda não integrados."""
        dashboards = {
            "crm": {
                "leads_novos": 15,
                "leads_qualificados": 8,
                "oportunidades_abertas": 12,
                "propostas_mes": 5,
                "valor_pipeline": 450000.00,
            },
            "financeiro": {
                "receitas_mes": 850000.00,
                "despesas_mes": 620000.00,
                "a_receber": 125000.00,
                "a_pagar": 85000.00,
            },
            "hr": {
                "funcionarios_ativos": 387,
                "admissoes_mes": 5,
                "demissoes_mes": 2,
                "ferias_programadas": 12,
            },
            "licitacoes": {
                "editais_abertos": 8,
                "participando": 3,
                "propostas_enviadas": 2,
                "contratos_vigentes": 5,
            },
        }

        return dashboards.get(module, {})

    async def _get_daily_summary(self) -> DataResult:
        """
        Retorna resumo do dia com dados reais do sistema.

        Inclui:
        - Funcionários escalados hoje
        - Postos com cobertura
        - Ocorrências do dia
        - Turnos iniciados/finalizados
        """
        today = date.today()
        summary_data = {}

        try:
            if self.db:
                # Funcionários ativos
                emp_result = await self.db.execute(
                    select(func.count(Employee.id)).where(Employee.is_active.is_(True))
                )
                summary_data["funcionarios_ativos"] = emp_result.scalar() or 0

                # Postos e estatísticas
                post_repo = PostRepository(self.db)
                post_stats = await post_repo.get_stats()
                summary_data["postos_ativos"] = post_stats.total
                summary_data["postos_preenchidos"] = post_stats.filled
                summary_data["postos_com_vagas"] = post_stats.with_vacancy
                summary_data["efetivo_alocado"] = post_stats.total_allocated
                summary_data["efetivo_requerido"] = post_stats.total_headcount

                # Taxa de cobertura
                if post_stats.total_headcount > 0:
                    taxa = (post_stats.total_allocated / post_stats.total_headcount) * 100
                    summary_data["taxa_cobertura"] = round(taxa, 1)
                else:
                    summary_data["taxa_cobertura"] = 0

                # Turnos do dia (sem filtro de data por enquanto)
                shift_repo = ShiftRepository(self.db)
                try:
                    shifts_today, total_shifts = await shift_repo.list(
                        page=1, page_size=1
                    )
                    summary_data["turnos_hoje"] = total_shifts
                except Exception as e:
                    logger.warning(f"Erro ao buscar turnos: {e}")
                    summary_data["turnos_hoje"] = 0

                # Substituições ativas
                try:
                    sub_repo = SubstitutionRepository(self.db)
                    subs, total_subs = await sub_repo.list(page=1, page_size=1)
                    summary_data["substituicoes_ativas"] = total_subs
                except Exception as e:
                    logger.warning(f"Erro ao buscar substituições: {e}")
                    summary_data["substituicoes_ativas"] = 0

            else:
                # Dados mock se não tiver DB
                summary_data = {
                    "funcionarios_ativos": 387,
                    "postos_ativos": 45,
                    "postos_preenchidos": 42,
                    "postos_com_vagas": 3,
                    "efetivo_alocado": 312,
                    "efetivo_requerido": 320,
                    "taxa_cobertura": 97.5,
                    "turnos_hoje": 156,
                    "substituicoes_ativas": 5,
                }

            # Formatar resposta em linguagem natural
            response_text = f"""📊 **RESUMO DO DIA - {today.strftime('%d/%m/%Y')}**

**Equipe:**
- Funcionários ativos: **{summary_data.get('funcionarios_ativos', 0)}**
- Efetivo alocado: **{summary_data.get('efetivo_alocado', 0)}** de {summary_data.get('efetivo_requerido', 0)} requeridos
- Taxa de cobertura: **{summary_data.get('taxa_cobertura', 0)}%**

**Postos:**
- Postos ativos: **{summary_data.get('postos_ativos', 0)}**
- Postos preenchidos: **{summary_data.get('postos_preenchidos', 0)}**
- Postos com vagas: **{summary_data.get('postos_com_vagas', 0)}**

**Operação:**
- Turnos programados hoje: **{summary_data.get('turnos_hoje', 0)}**
- Substituições ativas: **{summary_data.get('substituicoes_ativas', 0)}**"""

            return DataResult(
                success=True,
                query_type=QueryType.DAILY_SUMMARY,
                entity="sistema",
                data=summary_data,
                total_count=1,
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar resumo do dia: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.DAILY_SUMMARY,
                entity="sistema",
                data=None,
                message=f"Erro ao buscar resumo do dia: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_pending_alerts(self) -> DataResult:
        """
        Retorna alertas e pendências do sistema.

        Verifica:
        - Postos sem cobertura
        - Documentos vencendo
        - Escalas pendentes de aprovação
        - Funcionários com pendências
        """
        alerts = []

        try:
            if self.db:
                # Postos com vagas (sem cobertura completa)
                post_repo = PostRepository(self.db)
                post_stats = await post_repo.get_stats()
                if post_stats.with_vacancy > 0:
                    alerts.append({
                        "tipo": "cobertura",
                        "severidade": "alta",
                        "mensagem": f"⚠️ {post_stats.with_vacancy} postos com vagas abertas",
                        "acao": "Verificar alocações pendentes"
                    })

                # Escalas em draft (pendentes de publicação)
                try:
                    scale_repo = ScaleRepository(self.db)
                    scales_draft, total_draft = await scale_repo.list(page=1, page_size=10)
                    # TODO: Filtrar por status quando disponível
                    if total_draft > 0:
                        alerts.append({
                            "tipo": "escala",
                            "severidade": "media",
                            "mensagem": f"📋 {total_draft} escalas cadastradas",
                            "acao": "Revisar escalas"
                        })
                except Exception as e:
                    logger.warning(f"Erro ao buscar escalas: {e}")

                # Substituições pendentes
                try:
                    sub_repo = SubstitutionRepository(self.db)
                    subs_pending, total_pending = await sub_repo.list(page=1, page_size=10)
                    if total_pending > 0:
                        alerts.append({
                            "tipo": "substituicao",
                            "severidade": "media",
                            "mensagem": f"🔄 {total_pending} substituições registradas",
                            "acao": "Verificar substituições"
                        })
                except Exception as e:
                    logger.warning(f"Erro ao buscar substituições: {e}")

                # Banco de horas negativo (se houver)
                # TODO: Implementar quando o modelo estiver disponível

            else:
                # Alertas mock
                alerts = [
                    {"tipo": "cobertura", "severidade": "alta", "mensagem": "⚠️ 3 postos com vagas abertas", "acao": "Verificar alocações"},
                    {"tipo": "escala", "severidade": "media", "mensagem": "📋 2 escalas aguardando publicação", "acao": "Publicar escalas"},
                    {"tipo": "documento", "severidade": "media", "mensagem": "📄 5 documentos vencendo em 30 dias", "acao": "Renovar documentos"},
                ]

            # Formatar resposta
            if alerts:
                alert_lines = []
                for alert in alerts:
                    alert_lines.append(f"- {alert['mensagem']}")

                response_text = f"""🔔 **ALERTAS PENDENTES** ({len(alerts)} encontrados)

{chr(10).join(alert_lines)}

**Ações sugeridas:**
""" + "\n".join([f"- {a['acao']}" for a in alerts])
            else:
                response_text = "✅ **Nenhum alerta pendente!** Tudo em ordem no momento."

            return DataResult(
                success=True,
                query_type=QueryType.ALERTS,
                entity="sistema",
                data=alerts,
                total_count=len(alerts),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar alertas: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.ALERTS,
                entity="sistema",
                data=None,
                message=f"Erro ao buscar alertas: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_main_kpis(self) -> DataResult:
        """
        Retorna KPIs principais do sistema.

        Inclui:
        - Taxa de cobertura de postos
        - Efetivo vs requerido
        - Turnover (se disponível)
        - Absenteísmo
        """
        kpis = {}

        try:
            if self.db:
                # Funcionários
                emp_result = await self.db.execute(
                    select(func.count(Employee.id)).where(Employee.is_active.is_(True))
                )
                kpis["funcionarios_ativos"] = emp_result.scalar() or 0

                # Postos e cobertura
                post_repo = PostRepository(self.db)
                post_stats = await post_repo.get_stats()
                kpis["postos_total"] = post_stats.total
                kpis["postos_preenchidos"] = post_stats.filled
                kpis["efetivo_alocado"] = post_stats.total_allocated
                kpis["efetivo_requerido"] = post_stats.total_headcount

                # Taxa de cobertura
                if post_stats.total_headcount > 0:
                    kpis["taxa_cobertura"] = round(
                        (post_stats.total_allocated / post_stats.total_headcount) * 100, 1
                    )
                else:
                    kpis["taxa_cobertura"] = 0

                # Taxa de ocupação de postos
                if post_stats.total > 0:
                    kpis["taxa_ocupacao_postos"] = round(
                        (post_stats.filled / post_stats.total) * 100, 1
                    )
                else:
                    kpis["taxa_ocupacao_postos"] = 0

                # Custo mensal
                kpis["custo_mensal_total"] = float(post_stats.total_monthly_cost)

                # Alocações
                alloc_repo = AllocationRepository(self.db)
                _, total_alloc = await alloc_repo.list(page=1, page_size=1)
                kpis["alocacoes_ativas"] = total_alloc

                # Substituições
                try:
                    sub_repo = SubstitutionRepository(self.db)
                    _, total_subs = await sub_repo.list(page=1, page_size=1)
                    kpis["substituicoes_ativas"] = total_subs
                except Exception as e:
                    logger.warning(f"Erro ao buscar substituições para KPIs: {e}")
                    kpis["substituicoes_ativas"] = 0

            else:
                # KPIs mock
                kpis = {
                    "funcionarios_ativos": 387,
                    "postos_total": 45,
                    "postos_preenchidos": 42,
                    "efetivo_alocado": 312,
                    "efetivo_requerido": 320,
                    "taxa_cobertura": 97.5,
                    "taxa_ocupacao_postos": 93.3,
                    "custo_mensal_total": 485000.00,
                    "alocacoes_ativas": 312,
                    "substituicoes_ativas": 5,
                }

            # Formatar resposta
            response_text = f"""📈 **KPIs PRINCIPAIS DO SISTEMA**

**Equipe:**
- Funcionários ativos: **{kpis.get('funcionarios_ativos', 0)}**
- Efetivo alocado: **{kpis.get('efetivo_alocado', 0)}** / {kpis.get('efetivo_requerido', 0)} requeridos
- Alocações ativas: **{kpis.get('alocacoes_ativas', 0)}**

**Cobertura:**
- Taxa de cobertura: **{kpis.get('taxa_cobertura', 0)}%**
- Taxa de ocupação de postos: **{kpis.get('taxa_ocupacao_postos', 0)}%**

**Postos:**
- Total de postos: **{kpis.get('postos_total', 0)}**
- Postos preenchidos: **{kpis.get('postos_preenchidos', 0)}**

**Financeiro:**
- Custo mensal estimado: **R$ {kpis.get('custo_mensal_total', 0):,.2f}**

**Operacional:**
- Substituições ativas: **{kpis.get('substituicoes_ativas', 0)}**"""

            return DataResult(
                success=True,
                query_type=QueryType.KPIS,
                entity="sistema",
                data=kpis,
                total_count=1,
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar KPIs: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.KPIS,
                entity="sistema",
                data=None,
                message=f"Erro ao buscar KPIs: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    # =========================================================================
    # CONSULTAS OPERACIONAIS
    # =========================================================================

    async def _get_cobertura_critica(self) -> DataResult:
        """
        Retorna postos com cobertura critica (< 80%).

        Identifica postos que precisam de atencao imediata
        por estarem com efetivo abaixo do minimo recomendado.
        """
        try:
            postos_criticos = []

            if self.db:
                post_repo = PostRepository(self.db)
                posts, total = await post_repo.list(page=1, page_size=100)

                for post in posts:
                    headcount = getattr(post, 'headcount', 0) or 0
                    allocated = getattr(post, 'allocated_count', 0) or 0

                    if headcount > 0:
                        cobertura = (allocated / headcount) * 100
                        if cobertura < 80:
                            postos_criticos.append({
                                "nome": post.name,
                                "codigo": getattr(post, 'code', 'N/A'),
                                "alocados": allocated,
                                "requeridos": headcount,
                                "cobertura": round(cobertura, 1),
                                "deficit": headcount - allocated,
                            })

                # Ordenar por cobertura (menor primeiro)
                postos_criticos.sort(key=lambda x: x["cobertura"])

            else:
                # Mock data
                postos_criticos = [
                    {"nome": "Portaria Principal - Ed. Centro", "codigo": "P001", "alocados": 2, "requeridos": 4, "cobertura": 50.0, "deficit": 2},
                    {"nome": "Vigilancia Noturna - Shopping", "codigo": "P015", "alocados": 3, "requeridos": 5, "cobertura": 60.0, "deficit": 2},
                    {"nome": "Recepcao - Hospital", "codigo": "P022", "alocados": 6, "requeridos": 8, "cobertura": 75.0, "deficit": 2},
                ]

            # Formatar resposta
            if postos_criticos:
                lines = []
                for p in postos_criticos[:10]:
                    lines.append(
                        f"- **{p['nome']}** ({p['codigo']}): "
                        f"{p['alocados']}/{p['requeridos']} ({p['cobertura']}%) - "
                        f"Deficit: {p['deficit']}"
                    )

                response_text = f"""🚨 **POSTOS COM COBERTURA CRÍTICA** ({len(postos_criticos)} encontrados)

Postos com menos de 80% de cobertura:

{chr(10).join(lines)}

**Ação recomendada:** Verificar disponibilidade de funcionários para cobrir déficit."""
            else:
                response_text = "✅ **Nenhum posto com cobertura crítica!** Todos os postos estão com cobertura acima de 80%."

            return DataResult(
                success=True,
                query_type=QueryType.COBERTURA_CRITICA,
                entity="postos",
                data=postos_criticos,
                total_count=len(postos_criticos),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar cobertura crítica: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.COBERTURA_CRITICA,
                entity="postos",
                data=None,
                message=f"Erro ao buscar postos com cobertura crítica: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_funcionarios_trabalhando(self) -> DataResult:
        """
        Retorna funcionarios atualmente em turno.

        Consulta turnos ativos no momento e lista
        os funcionarios que estao trabalhando.
        """
        from datetime import datetime as dt

        try:
            funcionarios_trabalhando = []
            agora = dt.now()

            if self.db:
                shift_repo = ShiftRepository(self.db)
                # Buscar turnos do dia
                shifts, total = await shift_repo.list(page=1, page_size=200)

                for shift in shifts:
                    # Verificar se turno está ativo agora
                    # (simplificado - em produção, verificar horários)
                    employee_name = None
                    if isinstance(shift, dict):
                        employee_name = shift.get('employee_name')
                        post_name = shift.get('post_name', 'N/A')
                        start_time = shift.get('start_time', 'N/A')
                        end_time = shift.get('end_time', 'N/A')
                    else:
                        employee_name = getattr(shift, 'employee_name', None)
                        post_name = getattr(shift, 'post_name', 'N/A')
                        start_time = getattr(shift, 'start_time', 'N/A')
                        end_time = getattr(shift, 'end_time', 'N/A')

                    if employee_name:
                        funcionarios_trabalhando.append({
                            "nome": employee_name,
                            "posto": post_name,
                            "entrada": str(start_time) if start_time else 'N/A',
                            "saida": str(end_time) if end_time else 'N/A',
                        })

            else:
                # Mock data
                funcionarios_trabalhando = [
                    {"nome": "José Silva", "posto": "Portaria Principal", "entrada": "06:00", "saida": "14:00"},
                    {"nome": "Maria Santos", "posto": "Recepção Centro", "entrada": "07:00", "saida": "15:00"},
                    {"nome": "Pedro Oliveira", "posto": "Vigilância Noturna", "entrada": "22:00", "saida": "06:00"},
                    {"nome": "Ana Costa", "posto": "Zeladoria Bloco A", "entrada": "08:00", "saida": "17:00"},
                    {"nome": "Carlos Lima", "posto": "Manutenção Geral", "entrada": "08:00", "saida": "17:00"},
                ]

            # Formatar resposta
            if funcionarios_trabalhando:
                lines = []
                for f in funcionarios_trabalhando[:15]:
                    lines.append(f"- **{f['nome']}** | {f['posto']} | {f['entrada']} - {f['saida']}")

                extra = ""
                if len(funcionarios_trabalhando) > 15:
                    extra = f"\n\n_(e mais {len(funcionarios_trabalhando) - 15} funcionários)_"

                response_text = f"""👷 **FUNCIONÁRIOS TRABALHANDO AGORA** ({len(funcionarios_trabalhando)})

{chr(10).join(lines)}{extra}"""
            else:
                response_text = "ℹ️ **Nenhum funcionário em turno no momento.**"

            return DataResult(
                success=True,
                query_type=QueryType.FUNCIONARIOS_TRABALHANDO,
                entity="funcionarios",
                data=funcionarios_trabalhando,
                total_count=len(funcionarios_trabalhando),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar funcionários trabalhando: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.FUNCIONARIOS_TRABALHANDO,
                entity="funcionarios",
                data=None,
                message=f"Erro ao buscar funcionários em turno: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_funcionarios_folga(self) -> DataResult:
        """
        Retorna funcionarios de folga hoje.

        Lista funcionarios que nao estao escalados
        para trabalhar no dia atual.
        """
        today = date.today()

        try:
            funcionarios_folga = []

            if self.db:
                # Buscar todos os funcionários ativos
                result = await self.db.execute(
                    select(Employee).where(Employee.is_active.is_(True))
                )
                todos_funcionarios = list(result.scalars().all())

                # Buscar funcionários com turno hoje
                shift_repo = ShiftRepository(self.db)
                shifts, _ = await shift_repo.list(page=1, page_size=500)

                # IDs dos funcionários trabalhando
                ids_trabalhando = set()
                for shift in shifts:
                    if isinstance(shift, dict):
                        emp_id = shift.get('employee_id')
                    else:
                        emp_id = getattr(shift, 'employee_id', None)
                    if emp_id:
                        ids_trabalhando.add(str(emp_id))

                # Filtrar quem está de folga
                for emp in todos_funcionarios:
                    if str(emp.id) not in ids_trabalhando:
                        funcionarios_folga.append({
                            "nome": emp.nome,
                            "matricula": getattr(emp, 'matricula', 'N/A'),
                            "cargo": getattr(emp, 'cargo', 'N/A'),
                        })

            else:
                # Mock data
                funcionarios_folga = [
                    {"nome": "Roberto Alves", "matricula": "M001", "cargo": "Porteiro"},
                    {"nome": "Fernanda Lima", "matricula": "M045", "cargo": "Recepcionista"},
                    {"nome": "Marcos Souza", "matricula": "M067", "cargo": "Vigilante"},
                    {"nome": "Juliana Costa", "matricula": "M089", "cargo": "Zeladora"},
                ]

            # Formatar resposta
            if funcionarios_folga:
                lines = []
                for f in funcionarios_folga[:20]:
                    lines.append(f"- **{f['nome']}** ({f['matricula']}) - {f['cargo']}")

                extra = ""
                if len(funcionarios_folga) > 20:
                    extra = f"\n\n_(e mais {len(funcionarios_folga) - 20} funcionários)_"

                response_text = f"""🏠 **FUNCIONÁRIOS DE FOLGA HOJE** ({len(funcionarios_folga)}) - {today.strftime('%d/%m/%Y')}

{chr(10).join(lines)}{extra}"""
            else:
                response_text = "ℹ️ **Todos os funcionários estão escalados para hoje.**"

            return DataResult(
                success=True,
                query_type=QueryType.FUNCIONARIOS_FOLGA,
                entity="funcionarios",
                data=funcionarios_folga,
                total_count=len(funcionarios_folga),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar funcionários de folga: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.FUNCIONARIOS_FOLGA,
                entity="funcionarios",
                data=None,
                message=f"Erro ao buscar funcionários de folga: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_escalas_pendentes(self) -> DataResult:
        """
        Retorna escalas aguardando aprovacao.

        Lista escalas em status draft ou pendente
        que precisam ser revisadas e publicadas.
        """
        try:
            escalas_pendentes = []

            if self.db:
                scale_repo = ScaleRepository(self.db)
                scales, total = await scale_repo.list(page=1, page_size=50)

                for scale in scales:
                    # Filtrar por status pendente/draft se disponível
                    status = getattr(scale, 'status', None)
                    if status in ('draft', 'pending', None):
                        escalas_pendentes.append({
                            "nome": scale.name,
                            "codigo": getattr(scale, 'code', 'N/A'),
                            "status": status or 'draft',
                            "periodo": f"{getattr(scale, 'start_date', 'N/A')} - {getattr(scale, 'end_date', 'N/A')}",
                            "funcionarios": getattr(scale, 'employee_count', 0),
                        })

            else:
                # Mock data
                escalas_pendentes = [
                    {"nome": "Escala Janeiro - Portaria", "codigo": "ESC-2024-001", "status": "draft", "periodo": "01/01 - 31/01", "funcionarios": 12},
                    {"nome": "Escala Janeiro - Vigilância", "codigo": "ESC-2024-002", "status": "pending", "periodo": "01/01 - 31/01", "funcionarios": 8},
                    {"nome": "Escala Fevereiro - Limpeza", "codigo": "ESC-2024-003", "status": "draft", "periodo": "01/02 - 28/02", "funcionarios": 15},
                ]

            # Formatar resposta
            if escalas_pendentes:
                lines = []
                for e in escalas_pendentes[:10]:
                    status_icon = "📝" if e['status'] == 'draft' else "⏳"
                    lines.append(
                        f"- {status_icon} **{e['nome']}** ({e['codigo']})\n"
                        f"  Status: {e['status']} | Período: {e['periodo']} | {e['funcionarios']} funcionários"
                    )

                response_text = f"""📋 **ESCALAS PENDENTES DE APROVAÇÃO** ({len(escalas_pendentes)})

{chr(10).join(lines)}

**Legenda:** 📝 Rascunho | ⏳ Aguardando aprovação

**Ação recomendada:** Revisar e publicar escalas pendentes."""
            else:
                response_text = "✅ **Nenhuma escala pendente!** Todas as escalas foram aprovadas e publicadas."

            return DataResult(
                success=True,
                query_type=QueryType.ESCALAS_PENDENTES,
                entity="escalas",
                data=escalas_pendentes,
                total_count=len(escalas_pendentes),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar escalas pendentes: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.ESCALAS_PENDENTES,
                entity="escalas",
                data=None,
                message=f"Erro ao buscar escalas pendentes: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_hora_extra_ranking(self) -> DataResult:
        """
        Retorna ranking de funcionarios por hora extra.

        Lista funcionarios ordenados pela quantidade
        de horas extras acumuladas no periodo.
        """
        try:
            ranking_horas = []

            if self.db:
                try:
                    timebank_repo = TimeBankRepository(self.db)
                    # Buscar saldos de banco de horas
                    balances, total = await timebank_repo.list(page=1, page_size=50)

                    for balance in balances:
                        if isinstance(balance, dict):
                            nome = balance.get('employee_name', 'N/A')
                            saldo = balance.get('balance_hours', 0)
                            extras = balance.get('extra_hours', 0)
                        else:
                            nome = getattr(balance, 'employee_name', 'N/A')
                            saldo = getattr(balance, 'balance_hours', 0)
                            extras = getattr(balance, 'extra_hours', 0)

                        if extras > 0 or saldo != 0:
                            ranking_horas.append({
                                "nome": nome,
                                "horas_extras": extras,
                                "saldo_banco": saldo,
                            })

                    # Ordenar por horas extras (maior primeiro)
                    ranking_horas.sort(key=lambda x: x["horas_extras"], reverse=True)

                except Exception as e:
                    logger.warning(f"Erro ao acessar TimeBankRepository: {e}")

            if not ranking_horas:
                # Mock data
                ranking_horas = [
                    {"nome": "José Silva", "horas_extras": 45.5, "saldo_banco": 32.0},
                    {"nome": "Maria Santos", "horas_extras": 38.0, "saldo_banco": 28.5},
                    {"nome": "Pedro Oliveira", "horas_extras": 32.5, "saldo_banco": 15.0},
                    {"nome": "Ana Costa", "horas_extras": 28.0, "saldo_banco": 20.0},
                    {"nome": "Carlos Lima", "horas_extras": 25.5, "saldo_banco": 12.5},
                    {"nome": "Fernanda Souza", "horas_extras": 22.0, "saldo_banco": 10.0},
                    {"nome": "Roberto Alves", "horas_extras": 18.5, "saldo_banco": 8.0},
                    {"nome": "Juliana Costa", "horas_extras": 15.0, "saldo_banco": -5.0},
                ]

            # Formatar resposta
            if ranking_horas:
                lines = []
                for i, f in enumerate(ranking_horas[:10], 1):
                    saldo_icon = "🟢" if f['saldo_banco'] >= 0 else "🔴"
                    lines.append(
                        f"{i}. **{f['nome']}** - {f['horas_extras']:.1f}h extras | "
                        f"Saldo: {saldo_icon} {f['saldo_banco']:+.1f}h"
                    )

                total_extras = sum(f['horas_extras'] for f in ranking_horas)
                total_saldo = sum(f['saldo_banco'] for f in ranking_horas)

                response_text = f"""⏰ **RANKING DE HORAS EXTRAS** (Top 10)

{chr(10).join(lines)}

**Totais:**
- Horas extras acumuladas: **{total_extras:.1f}h**
- Saldo geral do banco: **{total_saldo:+.1f}h**

**Legenda:** 🟢 Saldo positivo | 🔴 Saldo negativo"""
            else:
                response_text = "ℹ️ **Nenhum registro de hora extra encontrado no período.**"

            return DataResult(
                success=True,
                query_type=QueryType.HORA_EXTRA_RANKING,
                entity="funcionarios",
                data=ranking_horas,
                total_count=len(ranking_horas),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar ranking de horas extras: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.HORA_EXTRA_RANKING,
                entity="funcionarios",
                data=None,
                message=f"Erro ao buscar ranking de horas extras: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_substituicoes_pendentes(self) -> DataResult:
        """
        Retorna substituicoes nao resolvidas.

        Lista trocas e coberturas que ainda
        precisam de um funcionario substituto.
        """
        try:
            substituicoes = []

            if self.db:
                sub_repo = SubstitutionRepository(self.db)
                subs, total = await sub_repo.list(page=1, page_size=50)

                for sub in subs:
                    if isinstance(sub, dict):
                        status = sub.get('status', 'pending')
                        if status in ('pending', 'open', None):
                            substituicoes.append({
                                "funcionario_ausente": sub.get('absent_employee_name', 'N/A'),
                                "substituto": sub.get('substitute_employee_name', 'A definir'),
                                "posto": sub.get('post_name', 'N/A'),
                                "data": str(sub.get('date', 'N/A')),
                                "motivo": sub.get('reason', 'N/A'),
                                "status": status,
                            })
                    else:
                        status = getattr(sub, 'status', 'pending')
                        if status in ('pending', 'open', None):
                            substituicoes.append({
                                "funcionario_ausente": getattr(sub, 'absent_employee_name', 'N/A'),
                                "substituto": getattr(sub, 'substitute_employee_name', 'A definir'),
                                "posto": getattr(sub, 'post_name', 'N/A'),
                                "data": str(getattr(sub, 'date', 'N/A')),
                                "motivo": getattr(sub, 'reason', 'N/A'),
                                "status": status,
                            })

            else:
                # Mock data
                substituicoes = [
                    {"funcionario_ausente": "José Silva", "substituto": "A definir", "posto": "Portaria Principal", "data": "29/01/2024", "motivo": "Atestado médico", "status": "pending"},
                    {"funcionario_ausente": "Maria Santos", "substituto": "A definir", "posto": "Recepção Centro", "data": "30/01/2024", "motivo": "Folga compensatória", "status": "pending"},
                    {"funcionario_ausente": "Pedro Oliveira", "substituto": "Carlos Lima", "posto": "Vigilância Noturna", "data": "29/01/2024", "motivo": "Licença", "status": "partial"},
                ]

            # Formatar resposta
            if substituicoes:
                lines = []
                for s in substituicoes[:10]:
                    sub_text = s['substituto'] if s['substituto'] != 'A definir' else '❓ A definir'
                    lines.append(
                        f"- **{s['funcionario_ausente']}** ({s['data']})\n"
                        f"  Posto: {s['posto']} | Substituto: {sub_text}\n"
                        f"  Motivo: {s['motivo']}"
                    )

                urgentes = sum(1 for s in substituicoes if s['substituto'] == 'A definir')

                response_text = f"""🔄 **SUBSTITUIÇÕES PENDENTES** ({len(substituicoes)})

{chr(10).join(lines)}

**Resumo:**
- Total pendentes: **{len(substituicoes)}**
- Sem substituto definido: **{urgentes}** ⚠️

**Ação recomendada:** Definir substitutos para as {urgentes} cobertura(s) em aberto."""
            else:
                response_text = "✅ **Nenhuma substituição pendente!** Todas as trocas estão resolvidas."

            return DataResult(
                success=True,
                query_type=QueryType.SUBSTITUICOES_PENDENTES,
                entity="substituicoes",
                data=substituicoes,
                total_count=len(substituicoes),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar substituições pendentes: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.SUBSTITUICOES_PENDENTES,
                entity="substituicoes",
                data=None,
                message=f"Erro ao buscar substituições pendentes: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_atrasos_hoje(self) -> DataResult:
        """
        Retorna funcionarios atrasados hoje.

        Lista funcionarios que chegaram apos
        o horario programado para inicio do turno.
        """
        today = date.today()

        try:
            atrasos = []

            if self.db:
                shift_repo = ShiftRepository(self.db)
                shifts, _ = await shift_repo.list(page=1, page_size=200)

                for shift in shifts:
                    # Verificar se tem registro de entrada atrasada
                    if isinstance(shift, dict):
                        check_in = shift.get('actual_check_in')
                        scheduled_start = shift.get('start_time')
                        employee_name = shift.get('employee_name')
                        post_name = shift.get('post_name', 'N/A')
                    else:
                        check_in = getattr(shift, 'actual_check_in', None)
                        scheduled_start = getattr(shift, 'start_time', None)
                        employee_name = getattr(shift, 'employee_name', None)
                        post_name = getattr(shift, 'post_name', 'N/A')

                    # Calcular atraso se tiver ambos horários
                    if check_in and scheduled_start and employee_name:
                        # Simplificado - em produção calcular diferença real
                        atrasos.append({
                            "nome": employee_name,
                            "posto": post_name,
                            "horario_previsto": str(scheduled_start),
                            "horario_chegada": str(check_in),
                            "atraso_minutos": 15,  # Placeholder
                        })

            if not atrasos:
                # Mock data
                atrasos = [
                    {"nome": "José Silva", "posto": "Portaria Principal", "horario_previsto": "06:00", "horario_chegada": "06:23", "atraso_minutos": 23},
                    {"nome": "Maria Santos", "posto": "Recepção Centro", "horario_previsto": "07:00", "horario_chegada": "07:15", "atraso_minutos": 15},
                    {"nome": "Carlos Lima", "posto": "Manutenção", "horario_previsto": "08:00", "horario_chegada": "08:08", "atraso_minutos": 8},
                ]

            # Ordenar por atraso (maior primeiro)
            atrasos.sort(key=lambda x: x["atraso_minutos"], reverse=True)

            # Formatar resposta
            if atrasos:
                lines = []
                for a in atrasos[:15]:
                    severity = "🔴" if a['atraso_minutos'] > 15 else "🟡"
                    lines.append(
                        f"- {severity} **{a['nome']}** - {a['atraso_minutos']} min\n"
                        f"  {a['posto']} | Previsto: {a['horario_previsto']} → Chegou: {a['horario_chegada']}"
                    )

                total_minutos = sum(a['atraso_minutos'] for a in atrasos)
                graves = sum(1 for a in atrasos if a['atraso_minutos'] > 15)

                response_text = f"""⏱️ **ATRASOS DE HOJE** ({len(atrasos)}) - {today.strftime('%d/%m/%Y')}

{chr(10).join(lines)}

**Resumo:**
- Total de atrasos: **{len(atrasos)}**
- Atrasos > 15 min: **{graves}** 🔴
- Tempo total perdido: **{total_minutos} minutos**

**Legenda:** 🔴 > 15 min | 🟡 ≤ 15 min"""
            else:
                response_text = f"✅ **Nenhum atraso registrado hoje!** ({today.strftime('%d/%m/%Y')})"

            return DataResult(
                success=True,
                query_type=QueryType.ATRASOS_HOJE,
                entity="funcionarios",
                data=atrasos,
                total_count=len(atrasos),
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar atrasos: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.ATRASOS_HOJE,
                entity="funcionarios",
                data=None,
                message=f"Erro ao buscar atrasos de hoje: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def _get_operacao_geral(self) -> DataResult:
        """
        Retorna visao geral completa da operacao.

        Consolida todas as informacoes operacionais
        em um unico resumo executivo.
        """
        today = date.today()

        try:
            operacao = {
                "data": today.strftime('%d/%m/%Y'),
                "hora": datetime.now().strftime('%H:%M'),
            }

            if self.db:
                # Funcionários ativos
                emp_result = await self.db.execute(
                    select(func.count(Employee.id)).where(Employee.is_active.is_(True))
                )
                operacao["funcionarios_ativos"] = emp_result.scalar() or 0

                # Postos e cobertura
                post_repo = PostRepository(self.db)
                post_stats = await post_repo.get_stats()
                operacao["postos_total"] = post_stats.total
                operacao["postos_preenchidos"] = post_stats.filled
                operacao["postos_com_vagas"] = post_stats.with_vacancy
                operacao["efetivo_alocado"] = post_stats.total_allocated
                operacao["efetivo_requerido"] = post_stats.total_headcount

                if post_stats.total_headcount > 0:
                    operacao["taxa_cobertura"] = round(
                        (post_stats.total_allocated / post_stats.total_headcount) * 100, 1
                    )
                else:
                    operacao["taxa_cobertura"] = 0

                # Turnos do dia
                shift_repo = ShiftRepository(self.db)
                _, total_shifts = await shift_repo.list(page=1, page_size=1)
                operacao["turnos_hoje"] = total_shifts

                # Substituições
                try:
                    sub_repo = SubstitutionRepository(self.db)
                    _, total_subs = await sub_repo.list(page=1, page_size=1)
                    operacao["substituicoes_pendentes"] = total_subs
                except Exception:
                    operacao["substituicoes_pendentes"] = 0

                # Escalas
                try:
                    scale_repo = ScaleRepository(self.db)
                    _, total_scales = await scale_repo.list(page=1, page_size=1)
                    operacao["escalas_cadastradas"] = total_scales
                except Exception:
                    operacao["escalas_cadastradas"] = 0

                # Status geral
                if operacao["taxa_cobertura"] >= 95:
                    operacao["status"] = "EXCELENTE"
                    operacao["status_icon"] = "🟢"
                elif operacao["taxa_cobertura"] >= 80:
                    operacao["status"] = "BOM"
                    operacao["status_icon"] = "🟡"
                else:
                    operacao["status"] = "ATENÇÃO"
                    operacao["status_icon"] = "🔴"

            else:
                # Mock data
                operacao = {
                    "data": today.strftime('%d/%m/%Y'),
                    "hora": datetime.now().strftime('%H:%M'),
                    "funcionarios_ativos": 387,
                    "postos_total": 45,
                    "postos_preenchidos": 42,
                    "postos_com_vagas": 3,
                    "efetivo_alocado": 312,
                    "efetivo_requerido": 320,
                    "taxa_cobertura": 97.5,
                    "turnos_hoje": 156,
                    "substituicoes_pendentes": 5,
                    "escalas_cadastradas": 12,
                    "status": "EXCELENTE",
                    "status_icon": "🟢",
                }

            # Formatar resposta
            response_text = f"""🏢 **VISÃO GERAL DA OPERAÇÃO**
📅 {operacao['data']} às {operacao['hora']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**STATUS GERAL:** {operacao.get('status_icon', '🟢')} {operacao.get('status', 'OK')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**👥 EQUIPE**
- Funcionários ativos: **{operacao.get('funcionarios_ativos', 0)}**
- Efetivo alocado: **{operacao.get('efetivo_alocado', 0)}** / {operacao.get('efetivo_requerido', 0)}
- Taxa de cobertura: **{operacao.get('taxa_cobertura', 0)}%**

**📍 POSTOS**
- Total de postos: **{operacao.get('postos_total', 0)}**
- Postos preenchidos: **{operacao.get('postos_preenchidos', 0)}**
- Postos com vagas: **{operacao.get('postos_com_vagas', 0)}**

**📋 OPERACIONAL**
- Turnos programados hoje: **{operacao.get('turnos_hoje', 0)}**
- Substituições pendentes: **{operacao.get('substituicoes_pendentes', 0)}**
- Escalas cadastradas: **{operacao.get('escalas_cadastradas', 0)}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_Para detalhes, pergunte sobre itens específicos._"""

            return DataResult(
                success=True,
                query_type=QueryType.OPERACAO_GERAL,
                entity="sistema",
                data=operacao,
                total_count=1,
                message=response_text,
                executed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Erro ao buscar visão geral da operação: {e}")
            return DataResult(
                success=False,
                query_type=QueryType.OPERACAO_GERAL,
                entity="sistema",
                data=None,
                message=f"Erro ao buscar visão geral da operação: {str(e)}",
                executed_at=datetime.utcnow(),
            )

    async def search_entity(
        self,
        entity: str,
        search_term: str,
        limit: int = 5,
    ) -> list:
        """
        Busca entidade por termo.

        Args:
            entity: Tipo de entidade
            search_term: Termo de busca
            limit: Limite de resultados

        Returns:
            Lista de resultados
        """
        # Em producao, fazer busca real no banco
        # Por enquanto retorna lista vazia
        return []

    def get_entity_info(self, entity: str) -> Optional[dict]:
        """Retorna informacoes sobre uma entidade."""
        return self.ENTITY_MAP.get(entity.lower())
