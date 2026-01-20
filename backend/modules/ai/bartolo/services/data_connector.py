"""
Data Connector - Conector de Dados do Sistema.

Permite ao Bartolo consultar dados reais do Conecta PRO
para responder perguntas com informacoes atualizadas.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Tipos de consulta."""
    COUNT = "count"
    LIST = "list"
    DETAIL = "detail"
    AGGREGATE = "aggregate"
    REPORT = "report"


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

    # Mapeamento de entidades para tabelas/modelos
    ENTITY_MAP = {
        "cliente": {"table": "clients", "name_field": "name"},
        "clientes": {"table": "clients", "name_field": "name"},
        "funcionario": {"table": "employees", "name_field": "full_name"},
        "funcionarios": {"table": "employees", "name_field": "full_name"},
        "contrato": {"table": "contracts", "name_field": "number"},
        "contratos": {"table": "contracts", "name_field": "number"},
        "proposta": {"table": "proposals", "name_field": "number"},
        "propostas": {"table": "proposals", "name_field": "number"},
        "lead": {"table": "leads", "name_field": "name"},
        "leads": {"table": "leads", "name_field": "name"},
        "posto": {"table": "work_posts", "name_field": "name"},
        "postos": {"table": "work_posts", "name_field": "name"},
        "ocorrencia": {"table": "occurrences", "name_field": "title"},
        "ocorrencias": {"table": "occurrences", "name_field": "title"},
        "edital": {"table": "tenders", "name_field": "number"},
        "editais": {"table": "tenders", "name_field": "number"},
        "licitacao": {"table": "tenders", "name_field": "number"},
        "licitacoes": {"table": "tenders", "name_field": "number"},
        "certidao": {"table": "certificates", "name_field": "type"},
        "certidoes": {"table": "certificates", "name_field": "type"},
    }

    # Padroes de consulta em linguagem natural
    QUERY_PATTERNS = [
        # Contagem
        (r"quantos?\s+(\w+)", QueryType.COUNT),
        (r"total\s+de\s+(\w+)", QueryType.COUNT),
        (r"numero\s+de\s+(\w+)", QueryType.COUNT),

        # Listagem
        (r"listar?\s+(\w+)", QueryType.LIST),
        (r"mostrar?\s+(\w+)", QueryType.LIST),
        (r"ver\s+(\w+)", QueryType.LIST),
        (r"quais\s+(\w+)", QueryType.LIST),

        # Detalhe
        (r"detalhes?\s+d[oa]\s+(\w+)", QueryType.DETAIL),
        (r"informacoes?\s+d[oa]\s+(\w+)", QueryType.DETAIL),
    ]

    def __init__(self, db_session=None):
        """Inicializa o conector."""
        self.db = db_session
        self._query_cache = {}

    def detect_data_query(self, message: str) -> Optional[DataQuery]:
        """
        Detecta se mensagem contem consulta de dados.

        Args:
            message: Mensagem do usuario

        Returns:
            DataQuery se detectado, None caso contrario
        """
        message_lower = message.lower()

        for pattern, query_type in self.QUERY_PATTERNS:
            match = re.search(pattern, message_lower)
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

        # Filtro de data
        if "hoje" in message:
            filters["date"] = date.today()
        elif "este mes" in message or "mes atual" in message:
            today = date.today()
            filters["month"] = today.month
            filters["year"] = today.year

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
            # Por enquanto retorna dados simulados
            # Em producao, integrar com os repositorios do sistema
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
        dashboards = {
            "crm": {
                "leads_novos": 15,
                "leads_qualificados": 8,
                "oportunidades_abertas": 12,
                "propostas_mes": 5,
                "valor_pipeline": 450000.00,
            },
            "operacoes": {
                "funcionarios_ativos": 387,
                "postos_ativos": 45,
                "escalas_hoje": 52,
                "ocorrencias_abertas": 3,
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
