"""
Sistema de Audit Trail para Integrações Governamentais.

Registra todas as operações para compliance e rastreabilidade.
"""

from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
import json
import logging
import hashlib

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TipoEvento(Enum):
    """Tipos de evento de auditoria."""
    # Operações de leitura
    CONSULTA = "consulta"
    DOWNLOAD = "download"
    EXPORTACAO = "exportacao"

    # Operações de escrita
    CRIACAO = "criacao"
    ATUALIZACAO = "atualizacao"
    EXCLUSAO = "exclusao"

    # Operações de integração
    ENVIO_GOVERNO = "envio_governo"
    RECEBIMENTO_GOVERNO = "recebimento_governo"
    SINCRONIZACAO = "sincronizacao"

    # Operações de segurança
    LOGIN = "login"
    LOGOUT = "logout"
    ACESSO_NEGADO = "acesso_negado"
    ALTERACAO_PERMISSAO = "alteracao_permissao"

    # Operações com dados sensíveis
    ACESSO_DADOS_PESSOAIS = "acesso_dados_pessoais"
    MASCARAMENTO = "mascaramento"
    ANONIMIZACAO = "anonimizacao"

    # LGPD
    SOLICITACAO_TITULAR = "solicitacao_titular"
    CONSENTIMENTO = "consentimento"
    REVOGACAO_CONSENTIMENTO = "revogacao_consentimento"

    # Sistema
    ERRO = "erro"
    ALERTA = "alerta"


@dataclass
class AuditEvent:
    """Evento de auditoria."""
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    tipo: TipoEvento = TipoEvento.CONSULTA
    recurso: str = ""  # Ex: "nfe", "funcionario", "certificado"
    recurso_id: Optional[str] = None
    acao: str = ""  # Descrição da ação
    ip_origem: Optional[str] = None
    user_agent: Optional[str] = None
    dados_antes: Optional[Dict] = None
    dados_depois: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)
    sucesso: bool = True
    erro: Optional[str] = None

    # Campos para rastreabilidade
    request_id: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "usuario_id": str(self.usuario_id) if self.usuario_id else None,
            "tipo": self.tipo.value,
            "recurso": self.recurso,
            "recurso_id": self.recurso_id,
            "acao": self.acao,
            "ip_origem": self.ip_origem,
            "sucesso": self.sucesso,
            "erro": self.erro,
            "metadata": self.metadata,
        }


class AuditLogger:
    """
    Logger de auditoria para compliance.

    Características:
    - Registro imutável de eventos
    - Hash de integridade
    - Mascaramento automático de dados sensíveis
    - Retenção configurável
    """

    # Campos que devem ser mascarados em logs
    CAMPOS_SENSIVEIS = {
        "senha", "password", "secret", "token", "api_key",
        "cpf", "rg", "cnh", "pis", "nis",
        "numero_cartao", "cvv", "conta_bancaria",
        "private_key", "certificate",
    }

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        mascarar_dados: bool = True
    ):
        self.db = db_session
        self.mascarar_dados = mascarar_dados
        self._buffer: List[AuditEvent] = []
        self._buffer_size = 100

    async def registrar(self, evento: AuditEvent) -> UUID:
        """
        Registra evento de auditoria.

        Args:
            evento: Evento a registrar

        Returns:
            ID do evento registrado
        """
        # Mascarar dados sensíveis
        if self.mascarar_dados:
            evento = self._mascarar_evento(evento)

        # Calcular hash de integridade
        hash_integridade = self._calcular_hash(evento)

        # Registrar no banco
        if self.db:
            await self._persistir_evento(evento, hash_integridade)

        # Log padrão
        log_msg = (
            f"AUDIT [{evento.tipo.value}] "
            f"tenant={evento.tenant_id} "
            f"user={evento.usuario_id} "
            f"recurso={evento.recurso}/{evento.recurso_id} "
            f"acao={evento.acao}"
        )

        if evento.sucesso:
            logger.info(log_msg)
        else:
            logger.warning(f"{log_msg} erro={evento.erro}")

        return evento.id

    def _mascarar_evento(self, evento: AuditEvent) -> AuditEvent:
        """Mascara dados sensíveis no evento."""
        if evento.dados_antes:
            evento.dados_antes = self._mascarar_dict(evento.dados_antes)

        if evento.dados_depois:
            evento.dados_depois = self._mascarar_dict(evento.dados_depois)

        if evento.metadata:
            evento.metadata = self._mascarar_dict(evento.metadata)

        return evento

    def _mascarar_dict(self, dados: Dict) -> Dict:
        """Mascara campos sensíveis em um dicionário."""
        resultado = {}

        for chave, valor in dados.items():
            chave_lower = chave.lower()

            # Verificar se é campo sensível
            if any(s in chave_lower for s in self.CAMPOS_SENSIVEIS):
                if isinstance(valor, str) and len(valor) > 0:
                    resultado[chave] = f"***{valor[-4:]}" if len(valor) > 4 else "****"
                else:
                    resultado[chave] = "****"

            elif isinstance(valor, dict):
                resultado[chave] = self._mascarar_dict(valor)

            elif isinstance(valor, list):
                resultado[chave] = [
                    self._mascarar_dict(item) if isinstance(item, dict) else item
                    for item in valor
                ]

            else:
                resultado[chave] = valor

        return resultado

    def _calcular_hash(self, evento: AuditEvent) -> str:
        """Calcula hash de integridade do evento."""
        dados = json.dumps(evento.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(dados.encode()).hexdigest()

    async def _persistir_evento(self, evento: AuditEvent, hash_integridade: str):
        """Persiste evento no banco de dados."""
        try:
            await self.db.execute(
                text("""
                INSERT INTO audit_log (
                    id, timestamp, tenant_id, usuario_id, tipo,
                    recurso, recurso_id, acao, ip_origem, user_agent,
                    dados_antes, dados_depois, metadata,
                    sucesso, erro, request_id, session_id, hash_integridade
                ) VALUES (
                    :id, :timestamp, :tenant_id, :usuario_id, :tipo,
                    :recurso, :recurso_id, :acao, :ip_origem, :user_agent,
                    :dados_antes, :dados_depois, :metadata,
                    :sucesso, :erro, :request_id, :session_id, :hash
                )
                """),
                {
                    "id": evento.id,
                    "timestamp": evento.timestamp,
                    "tenant_id": evento.tenant_id,
                    "usuario_id": evento.usuario_id,
                    "tipo": evento.tipo.value,
                    "recurso": evento.recurso,
                    "recurso_id": evento.recurso_id,
                    "acao": evento.acao,
                    "ip_origem": evento.ip_origem,
                    "user_agent": evento.user_agent,
                    "dados_antes": json.dumps(evento.dados_antes) if evento.dados_antes else None,
                    "dados_depois": json.dumps(evento.dados_depois) if evento.dados_depois else None,
                    "metadata": json.dumps(evento.metadata) if evento.metadata else None,
                    "sucesso": evento.sucesso,
                    "erro": evento.erro,
                    "request_id": evento.request_id,
                    "session_id": evento.session_id,
                    "hash": hash_integridade,
                }
            )
            await self.db.commit()

        except Exception as e:
            logger.error(f"Erro ao persistir evento de auditoria: {e}")

    # Métodos de conveniência

    async def log_consulta(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        recurso: str,
        recurso_id: str,
        **kwargs
    ) -> UUID:
        """Registra consulta a recurso."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.CONSULTA,
            recurso=recurso,
            recurso_id=recurso_id,
            acao=f"Consulta {recurso}",
            **kwargs
        )
        return await self.registrar(evento)

    async def log_criacao(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        recurso: str,
        recurso_id: str,
        dados: Dict,
        **kwargs
    ) -> UUID:
        """Registra criação de recurso."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.CRIACAO,
            recurso=recurso,
            recurso_id=recurso_id,
            acao=f"Criação de {recurso}",
            dados_depois=dados,
            **kwargs
        )
        return await self.registrar(evento)

    async def log_atualizacao(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        recurso: str,
        recurso_id: str,
        dados_antes: Dict,
        dados_depois: Dict,
        **kwargs
    ) -> UUID:
        """Registra atualização de recurso."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.ATUALIZACAO,
            recurso=recurso,
            recurso_id=recurso_id,
            acao=f"Atualização de {recurso}",
            dados_antes=dados_antes,
            dados_depois=dados_depois,
            **kwargs
        )
        return await self.registrar(evento)

    async def log_exclusao(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        recurso: str,
        recurso_id: str,
        dados: Dict,
        **kwargs
    ) -> UUID:
        """Registra exclusão de recurso."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.EXCLUSAO,
            recurso=recurso,
            recurso_id=recurso_id,
            acao=f"Exclusão de {recurso}",
            dados_antes=dados,
            **kwargs
        )
        return await self.registrar(evento)

    async def log_envio_governo(
        self,
        tenant_id: UUID,
        recurso: str,
        recurso_id: str,
        servico: str,
        sucesso: bool,
        erro: Optional[str] = None,
        **kwargs
    ) -> UUID:
        """Registra envio para serviço governamental."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            tipo=TipoEvento.ENVIO_GOVERNO,
            recurso=recurso,
            recurso_id=recurso_id,
            acao=f"Envio para {servico}",
            sucesso=sucesso,
            erro=erro,
            metadata={"servico": servico, **kwargs.get("metadata", {})},
            **{k: v for k, v in kwargs.items() if k != "metadata"}
        )
        return await self.registrar(evento)

    async def log_acesso_dados_pessoais(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        titular_id: str,
        dados_acessados: List[str],
        finalidade: str,
        **kwargs
    ) -> UUID:
        """Registra acesso a dados pessoais (LGPD)."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.ACESSO_DADOS_PESSOAIS,
            recurso="dados_pessoais",
            recurso_id=titular_id,
            acao=f"Acesso a dados pessoais - {finalidade}",
            metadata={
                "titular_id": titular_id,
                "campos_acessados": dados_acessados,
                "finalidade": finalidade,
            },
            **kwargs
        )
        return await self.registrar(evento)

    async def log_erro(
        self,
        tenant_id: UUID,
        recurso: str,
        erro: str,
        **kwargs
    ) -> UUID:
        """Registra erro no sistema."""
        evento = AuditEvent(
            tenant_id=tenant_id,
            tipo=TipoEvento.ERRO,
            recurso=recurso,
            acao="Erro no sistema",
            sucesso=False,
            erro=erro,
            **kwargs
        )
        return await self.registrar(evento)

    # Consultas de auditoria

    async def buscar_eventos(
        self,
        tenant_id: UUID,
        tipo: Optional[TipoEvento] = None,
        recurso: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Busca eventos de auditoria."""
        if not self.db:
            return []

        # Construir query dinamicamente
        conditions = ["tenant_id = :tenant_id"]
        params = {"tenant_id": tenant_id, "limite": limite, "offset": offset}

        if tipo:
            conditions.append("tipo = :tipo")
            params["tipo"] = tipo.value

        if recurso:
            conditions.append("recurso = :recurso")
            params["recurso"] = recurso

        if usuario_id:
            conditions.append("usuario_id = :usuario_id")
            params["usuario_id"] = usuario_id

        if data_inicio:
            conditions.append("timestamp >= :data_inicio")
            params["data_inicio"] = data_inicio

        if data_fim:
            conditions.append("timestamp <= :data_fim")
            params["data_fim"] = data_fim

        where_clause = " AND ".join(conditions)

        result = await self.db.execute(
            text(f"""
            SELECT id, timestamp, usuario_id, tipo, recurso, recurso_id,
                   acao, ip_origem, sucesso, erro, metadata
            FROM audit_log
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT :limite OFFSET :offset
            """),
            params
        )

        eventos = []
        for row in result.fetchall():
            eventos.append({
                "id": str(row.id),
                "timestamp": row.timestamp.isoformat(),
                "usuario_id": str(row.usuario_id) if row.usuario_id else None,
                "tipo": row.tipo,
                "recurso": row.recurso,
                "recurso_id": row.recurso_id,
                "acao": row.acao,
                "ip_origem": row.ip_origem,
                "sucesso": row.sucesso,
                "erro": row.erro,
                "metadata": json.loads(row.metadata) if row.metadata else {},
            })

        return eventos

    async def gerar_relatorio_compliance(
        self,
        tenant_id: UUID,
        data_inicio: datetime,
        data_fim: datetime
    ) -> Dict[str, Any]:
        """Gera relatório de compliance para o período."""
        if not self.db:
            return {"erro": "Banco de dados não configurado"}

        # Contagem por tipo de evento
        result = await self.db.execute(
            text("""
            SELECT tipo, COUNT(*) as total, SUM(CASE WHEN sucesso THEN 1 ELSE 0 END) as sucesso
            FROM audit_log
            WHERE tenant_id = :tenant_id
              AND timestamp BETWEEN :inicio AND :fim
            GROUP BY tipo
            ORDER BY total DESC
            """),
            {"tenant_id": tenant_id, "inicio": data_inicio, "fim": data_fim}
        )

        eventos_por_tipo = {}
        for row in result.fetchall():
            eventos_por_tipo[row.tipo] = {
                "total": row.total,
                "sucesso": row.sucesso,
                "falha": row.total - row.sucesso,
            }

        # Acessos a dados pessoais
        result = await self.db.execute(
            text("""
            SELECT COUNT(*) as total
            FROM audit_log
            WHERE tenant_id = :tenant_id
              AND timestamp BETWEEN :inicio AND :fim
              AND tipo = :tipo
            """),
            {
                "tenant_id": tenant_id,
                "inicio": data_inicio,
                "fim": data_fim,
                "tipo": TipoEvento.ACESSO_DADOS_PESSOAIS.value,
            }
        )
        acessos_dados_pessoais = result.scalar() or 0

        return {
            "periodo": {
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat(),
            },
            "eventos_por_tipo": eventos_por_tipo,
            "total_eventos": sum(e["total"] for e in eventos_por_tipo.values()),
            "lgpd": {
                "acessos_dados_pessoais": acessos_dados_pessoais,
            },
            "gerado_em": datetime.utcnow().isoformat(),
        }


# Instância singleton
_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Obtém instância do audit logger."""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance
