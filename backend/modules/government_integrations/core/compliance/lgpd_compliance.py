"""
Sistema de Compliance LGPD.

Implementa controles para conformidade com a Lei Geral de Proteção de Dados.
"""

import importlib.util as _ilu
import json
import logging
import os as _os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_validator_path = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), "..", "..", "..", "..", "core", "security", "sql_validator.py")
)
_spec = _ilu.spec_from_file_location("_sql_validator", _validator_path)
_sql_validator = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_sql_validator)
validate_table_name = _sql_validator.validate_table_name

from .audit_logger import AuditEvent, AuditLogger, TipoEvento, get_audit_logger  # noqa: E402

logger = logging.getLogger(__name__)


class ConsentimentoStatus(Enum):
    """Status de consentimento."""

    PENDENTE = "pendente"
    CONCEDIDO = "concedido"
    REVOGADO = "revogado"
    EXPIRADO = "expirado"


class TipoSolicitacao(Enum):
    """Tipos de solicitação do titular."""

    ACESSO = "acesso"  # Art. 18, II - acesso aos dados
    CORRECAO = "correcao"  # Art. 18, III - correção de dados
    ANONIMIZACAO = "anonimizacao"  # Art. 18, IV - anonimização
    BLOQUEIO = "bloqueio"  # Art. 18, IV - bloqueio
    ELIMINACAO = "eliminacao"  # Art. 18, VI - eliminação
    PORTABILIDADE = "portabilidade"  # Art. 18, V - portabilidade
    INFORMACAO_COMPARTILHAMENTO = "informacao_compartilhamento"  # Art. 18, VII
    REVOGACAO_CONSENTIMENTO = "revogacao_consentimento"  # Art. 18, IX


class StatusSolicitacao(Enum):
    """Status de solicitação."""

    ABERTA = "aberta"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"


@dataclass
class Consentimento:
    """Registro de consentimento."""

    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    titular_id: UUID = None  # ID da pessoa
    finalidade: str = ""  # Ex: "processamento_folha", "envio_esocial"
    dados_autorizados: list[str] = field(default_factory=list)
    status: ConsentimentoStatus = ConsentimentoStatus.PENDENTE
    data_consentimento: datetime | None = None
    data_revogacao: datetime | None = None
    data_expiracao: datetime | None = None
    ip_origem: str | None = None
    evidencia: str | None = None  # Hash ou referência da evidência
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SolicitacaoTitular:
    """Solicitação de titular de dados."""

    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    titular_id: UUID = None
    tipo: TipoSolicitacao = TipoSolicitacao.ACESSO
    status: StatusSolicitacao = StatusSolicitacao.ABERTA
    descricao: str = ""
    dados_solicitados: list[str] = field(default_factory=list)
    resposta: str | None = None
    dados_resposta: dict | None = None
    prazo: datetime = None  # 15 dias conforme LGPD
    responsavel_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    concluida_em: datetime | None = None


class ControleLGPD:
    """
    Sistema de controle LGPD.

    Implementa:
    - Gestão de consentimentos
    - Atendimento a solicitações de titulares
    - Registro de bases legais
    - Relatórios de impacto (RIPD)
    """

    # Prazo padrão para resposta (dias)
    PRAZO_RESPOSTA_DIAS = 15

    # Finalidades padrão e suas bases legais
    FINALIDADES_BASE_LEGAL = {
        "processamento_folha": "execucao_contrato",  # Art. 7, V
        "envio_esocial": "cumprimento_obrigacao_legal",  # Art. 7, II
        "envio_fgts": "cumprimento_obrigacao_legal",
        "envio_sefaz": "cumprimento_obrigacao_legal",
        "emissao_nfe": "execucao_contrato",
        "controle_acesso": "legitimo_interesse",  # Art. 7, IX
        "marketing": "consentimento",  # Art. 7, I
    }

    def __init__(self, db_session: AsyncSession | None = None, audit_logger: AuditLogger | None = None):
        self.db = db_session
        self.audit = audit_logger or get_audit_logger()

    async def registrar_consentimento(
        self,
        tenant_id: UUID,
        titular_id: UUID,
        finalidade: str,
        dados_autorizados: list[str],
        ip_origem: str | None = None,
        evidencia: str | None = None,
        expiracao_dias: int | None = None,
    ) -> Consentimento:
        """
        Registra consentimento do titular.

        Args:
            tenant_id: ID do tenant
            titular_id: ID do titular dos dados
            finalidade: Finalidade do tratamento
            dados_autorizados: Lista de tipos de dados autorizados
            ip_origem: IP de origem do consentimento
            evidencia: Hash ou referência da evidência
            expiracao_dias: Dias até expiração (None = sem expiração)

        Returns:
            Consentimento registrado
        """
        agora = datetime.utcnow()

        consentimento = Consentimento(
            tenant_id=tenant_id,
            titular_id=titular_id,
            finalidade=finalidade,
            dados_autorizados=dados_autorizados,
            status=ConsentimentoStatus.CONCEDIDO,
            data_consentimento=agora,
            data_expiracao=agora + timedelta(days=expiracao_dias) if expiracao_dias else None,
            ip_origem=ip_origem,
            evidencia=evidencia,
        )

        if self.db:
            await self._persistir_consentimento(consentimento)

        # Registrar na auditoria
        await self.audit.registrar(
            AuditEvent(
                tenant_id=tenant_id,
                tipo=TipoEvento.CONSENTIMENTO,
                recurso="consentimento",
                recurso_id=str(consentimento.id),
                acao=f"Consentimento concedido para {finalidade}",
                metadata={
                    "titular_id": str(titular_id),
                    "finalidade": finalidade,
                    "dados_autorizados": dados_autorizados,
                },
                ip_origem=ip_origem,
            )
        )

        logger.info(f"Consentimento registrado: {consentimento.id} (titular={titular_id}, finalidade={finalidade})")

        return consentimento

    async def revogar_consentimento(self, tenant_id: UUID, consentimento_id: UUID, motivo: str | None = None) -> bool:
        """
        Revoga um consentimento.

        Args:
            tenant_id: ID do tenant
            consentimento_id: ID do consentimento
            motivo: Motivo da revogação

        Returns:
            True se revogado com sucesso
        """
        if self.db:
            await self.db.execute(
                text("""
                UPDATE consentimentos
                SET status = :status,
                    data_revogacao = :data_revogacao,
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """),
                {
                    "id": consentimento_id,
                    "tenant_id": tenant_id,
                    "status": ConsentimentoStatus.REVOGADO.value,
                    "data_revogacao": datetime.utcnow(),
                },
            )
            await self.db.commit()

        # Registrar na auditoria
        await self.audit.registrar(
            AuditEvent(
                tenant_id=tenant_id,
                tipo=TipoEvento.REVOGACAO_CONSENTIMENTO,
                recurso="consentimento",
                recurso_id=str(consentimento_id),
                acao="Consentimento revogado",
                metadata={"motivo": motivo},
            )
        )

        logger.info(f"Consentimento revogado: {consentimento_id}")
        return True

    async def verificar_consentimento(self, tenant_id: UUID, titular_id: UUID, finalidade: str) -> bool:
        """
        Verifica se há consentimento válido para uma finalidade.

        Args:
            tenant_id: ID do tenant
            titular_id: ID do titular
            finalidade: Finalidade a verificar

        Returns:
            True se há consentimento válido
        """
        # Verificar se finalidade requer consentimento
        base_legal = self.FINALIDADES_BASE_LEGAL.get(finalidade)
        if base_legal and base_legal != "consentimento":
            # Não requer consentimento (outra base legal)
            return True

        if not self.db:
            return False

        result = await self.db.execute(
            text("""
            SELECT COUNT(*) FROM consentimentos
            WHERE tenant_id = :tenant_id
              AND titular_id = :titular_id
              AND finalidade = :finalidade
              AND status = :status
              AND (data_expiracao IS NULL OR data_expiracao > NOW())
            """),
            {
                "tenant_id": tenant_id,
                "titular_id": titular_id,
                "finalidade": finalidade,
                "status": ConsentimentoStatus.CONCEDIDO.value,
            },
        )

        return (result.scalar() or 0) > 0

    async def criar_solicitacao(
        self,
        tenant_id: UUID,
        titular_id: UUID,
        tipo: TipoSolicitacao,
        descricao: str,
        dados_solicitados: list[str] | None = None,
    ) -> SolicitacaoTitular:
        """
        Cria solicitação de titular.

        Args:
            tenant_id: ID do tenant
            titular_id: ID do titular
            tipo: Tipo de solicitação
            descricao: Descrição da solicitação
            dados_solicitados: Dados específicos solicitados

        Returns:
            Solicitação criada
        """
        agora = datetime.utcnow()

        solicitacao = SolicitacaoTitular(
            tenant_id=tenant_id,
            titular_id=titular_id,
            tipo=tipo,
            descricao=descricao,
            dados_solicitados=dados_solicitados or [],
            prazo=agora + timedelta(days=self.PRAZO_RESPOSTA_DIAS),
        )

        if self.db:
            await self._persistir_solicitacao(solicitacao)

        # Registrar na auditoria
        await self.audit.registrar(
            AuditEvent(
                tenant_id=tenant_id,
                tipo=TipoEvento.SOLICITACAO_TITULAR,
                recurso="solicitacao_lgpd",
                recurso_id=str(solicitacao.id),
                acao=f"Solicitação criada: {tipo.value}",
                metadata={
                    "titular_id": str(titular_id),
                    "tipo": tipo.value,
                    "prazo": solicitacao.prazo.isoformat(),
                },
            )
        )

        logger.info(f"Solicitação LGPD criada: {solicitacao.id} (tipo={tipo.value}, prazo={solicitacao.prazo.date()})")

        return solicitacao

    async def atualizar_solicitacao(
        self,
        tenant_id: UUID,
        solicitacao_id: UUID,
        status: StatusSolicitacao,
        resposta: str | None = None,
        dados_resposta: dict | None = None,
        responsavel_id: UUID | None = None,
    ) -> bool:
        """
        Atualiza status de uma solicitação.

        Args:
            tenant_id: ID do tenant
            solicitacao_id: ID da solicitação
            status: Novo status
            resposta: Texto de resposta
            dados_resposta: Dados da resposta (para exportação)
            responsavel_id: ID do responsável

        Returns:
            True se atualizado com sucesso
        """
        agora = datetime.utcnow()
        concluida_em = agora if status == StatusSolicitacao.CONCLUIDA else None

        if self.db:
            await self.db.execute(
                text("""
                UPDATE solicitacoes_lgpd
                SET status = :status,
                    resposta = :resposta,
                    dados_resposta = :dados_resposta,
                    responsavel_id = :responsavel_id,
                    updated_at = :updated_at,
                    concluida_em = :concluida_em
                WHERE id = :id AND tenant_id = :tenant_id
                """),
                {
                    "id": solicitacao_id,
                    "tenant_id": tenant_id,
                    "status": status.value,
                    "resposta": resposta,
                    "dados_resposta": json.dumps(dados_resposta) if dados_resposta else None,
                    "responsavel_id": responsavel_id,
                    "updated_at": agora,
                    "concluida_em": concluida_em,
                },
            )
            await self.db.commit()

        # Auditoria
        await self.audit.registrar(
            AuditEvent(
                tenant_id=tenant_id,
                usuario_id=responsavel_id,
                tipo=TipoEvento.SOLICITACAO_TITULAR,
                recurso="solicitacao_lgpd",
                recurso_id=str(solicitacao_id),
                acao=f"Solicitação atualizada para {status.value}",
            )
        )

        return True

    async def listar_solicitacoes(
        self, tenant_id: UUID, status: StatusSolicitacao | None = None, titular_id: UUID | None = None, limite: int = 50
    ) -> list[dict]:
        """Lista solicitações de um tenant."""
        if not self.db:
            return []

        conditions = ["tenant_id = :tenant_id"]
        params = {"tenant_id": tenant_id, "limite": limite}

        if status:
            conditions.append("status = :status")
            params["status"] = status.value

        if titular_id:
            conditions.append("titular_id = :titular_id")
            params["titular_id"] = titular_id

        result = await self.db.execute(
            text(f"""
            SELECT id, titular_id, tipo, status, descricao, prazo,
                   created_at, updated_at, concluida_em
            FROM solicitacoes_lgpd
            WHERE {" AND ".join(conditions)}
            ORDER BY created_at DESC
            LIMIT :limite
            """),
            params,
        )

        solicitacoes = []
        for row in result.fetchall():
            solicitacoes.append(
                {
                    "id": str(row.id),
                    "titular_id": str(row.titular_id),
                    "tipo": row.tipo,
                    "status": row.status,
                    "descricao": row.descricao,
                    "prazo": row.prazo.isoformat() if row.prazo else None,
                    "created_at": row.created_at.isoformat(),
                    "vencida": row.prazo < datetime.utcnow() if row.prazo else False,
                }
            )

        return solicitacoes

    async def verificar_solicitacoes_vencidas(self, tenant_id: UUID | None = None) -> list[dict]:
        """Verifica solicitações com prazo vencido."""
        if not self.db:
            return []

        conditions = ["status IN ('aberta', 'em_andamento')", "prazo < NOW()"]
        params = {}

        if tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id

        result = await self.db.execute(
            text(f"""
            SELECT id, tenant_id, titular_id, tipo, prazo, created_at
            FROM solicitacoes_lgpd
            WHERE {" AND ".join(conditions)}
            ORDER BY prazo ASC
            """),
            params,
        )

        vencidas = []
        for row in result.fetchall():
            dias_atraso = (datetime.utcnow() - row.prazo).days
            vencidas.append(
                {
                    "id": str(row.id),
                    "tenant_id": str(row.tenant_id),
                    "titular_id": str(row.titular_id),
                    "tipo": row.tipo,
                    "prazo": row.prazo.isoformat(),
                    "dias_atraso": dias_atraso,
                }
            )

        if vencidas:
            logger.warning(f"Encontradas {len(vencidas)} solicitações LGPD vencidas")

        return vencidas

    async def exportar_dados_titular(
        self, tenant_id: UUID, titular_id: UUID, tabelas: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Exporta todos os dados de um titular (portabilidade).

        Args:
            tenant_id: ID do tenant
            titular_id: ID do titular
            tabelas: Lista de tabelas para exportar (None = todas)

        Returns:
            Dicionário com todos os dados do titular
        """
        # Tabelas padrão que podem conter dados pessoais
        tabelas_padrao = [
            "funcionarios",
            "dependentes",
            "enderecos",
            "contatos",
            "documentos",
            "contratos",
            "folha_pagamento",
        ]

        tabelas = tabelas or tabelas_padrao
        dados_exportados = {
            "titular_id": str(titular_id),
            "exportado_em": datetime.utcnow().isoformat(),
            "dados": {},
        }

        if self.db:
            for tabela in tabelas:
                try:
                    validate_table_name(tabela)
                    # Assumir que todas as tabelas têm coluna funcionario_id ou titular_id
                    result = await self.db.execute(
                        text(f"""
                        SELECT * FROM {tabela}
                        WHERE tenant_id = :tenant_id
                          AND (
                            funcionario_id = :titular_id
                            OR id = :titular_id
                          )
                        """),
                        {"tenant_id": tenant_id, "titular_id": titular_id},
                    )

                    rows = result.fetchall()
                    if rows:
                        dados_exportados["dados"][tabela] = [dict(row._mapping) for row in rows]

                except Exception as e:
                    logger.warning(f"Erro ao exportar tabela {tabela}: {e}")

        # Registrar auditoria
        await self.audit.log_acesso_dados_pessoais(
            tenant_id=tenant_id,
            usuario_id=None,  # Sistema
            titular_id=str(titular_id),
            dados_acessados=list(dados_exportados["dados"].keys()),
            finalidade="portabilidade_lgpd",
        )

        return dados_exportados

    async def anonimizar_dados_titular(
        self, tenant_id: UUID, titular_id: UUID, tabelas: list[str] | None = None
    ) -> dict[str, int]:
        """
        Anonimiza dados de um titular.

        Args:
            tenant_id: ID do tenant
            titular_id: ID do titular
            tabelas: Tabelas para anonimizar

        Returns:
            Contagem de registros anonimizados por tabela
        """
        # Esta é uma operação destrutiva - deve ser usada com cuidado
        resultado = {}

        # Registrar auditoria ANTES da anonimização
        await self.audit.registrar(
            AuditEvent(
                tenant_id=tenant_id,
                tipo=TipoEvento.ANONIMIZACAO,
                recurso="dados_pessoais",
                recurso_id=str(titular_id),
                acao="Anonimização de dados do titular",
                metadata={"tabelas": tabelas},
            )
        )

        logger.warning(f"Anonimização de dados iniciada: tenant={tenant_id}, titular={titular_id}")

        # Implementação depende do schema específico
        # Exemplo simplificado:
        if self.db:
            # Anonimizar tabela de funcionários
            result = await self.db.execute(
                text("""
                UPDATE funcionarios
                SET nome = 'ANONIMIZADO',
                    cpf = '00000000000',
                    email = 'anonimizado@removed.com',
                    telefone = NULL,
                    endereco = NULL,
                    data_nascimento = NULL,
                    anonimizado = TRUE,
                    anonimizado_em = NOW()
                WHERE tenant_id = :tenant_id AND id = :titular_id
                """),
                {"tenant_id": tenant_id, "titular_id": titular_id},
            )
            resultado["funcionarios"] = result.rowcount

            await self.db.commit()

        return resultado

    async def gerar_relatorio_impacto(self, tenant_id: UUID) -> dict[str, Any]:
        """
        Gera Relatório de Impacto à Proteção de Dados (RIPD).

        Art. 38 da LGPD.
        """
        relatorio = {
            "tenant_id": str(tenant_id),
            "gerado_em": datetime.utcnow().isoformat(),
            "versao": "1.0",
        }

        if self.db:
            # Contar titulares
            result = await self.db.execute(
                text("""
                SELECT COUNT(DISTINCT id) as total
                FROM funcionarios
                WHERE tenant_id = :tenant_id AND ativo = TRUE
                """),
                {"tenant_id": tenant_id},
            )
            relatorio["titulares"] = {
                "total_funcionarios": result.scalar() or 0,
            }

            # Contar consentimentos
            result = await self.db.execute(
                text("""
                SELECT finalidade, status, COUNT(*) as total
                FROM consentimentos
                WHERE tenant_id = :tenant_id
                GROUP BY finalidade, status
                """),
                {"tenant_id": tenant_id},
            )
            consentimentos = {}
            for row in result.fetchall():
                if row.finalidade not in consentimentos:
                    consentimentos[row.finalidade] = {}
                consentimentos[row.finalidade][row.status] = row.total
            relatorio["consentimentos"] = consentimentos

            # Solicitações
            result = await self.db.execute(
                text("""
                SELECT tipo, status, COUNT(*) as total
                FROM solicitacoes_lgpd
                WHERE tenant_id = :tenant_id
                GROUP BY tipo, status
                """),
                {"tenant_id": tenant_id},
            )
            solicitacoes = {}
            for row in result.fetchall():
                if row.tipo not in solicitacoes:
                    solicitacoes[row.tipo] = {}
                solicitacoes[row.tipo][row.status] = row.total
            relatorio["solicitacoes"] = solicitacoes

        relatorio["tratamentos"] = [
            {
                "finalidade": finalidade,
                "base_legal": base,
                "dados_tratados": self._dados_por_finalidade(finalidade),
            }
            for finalidade, base in self.FINALIDADES_BASE_LEGAL.items()
        ]

        return relatorio

    def _dados_por_finalidade(self, finalidade: str) -> list[str]:
        """Retorna lista de dados tratados por finalidade."""
        mapeamento = {
            "processamento_folha": ["nome", "cpf", "dados_bancarios", "salario", "dependentes"],
            "envio_esocial": ["nome", "cpf", "dados_trabalhistas", "dependentes", "afastamentos"],
            "envio_fgts": ["nome", "cpf", "salario", "data_admissao"],
            "envio_sefaz": ["cnpj", "razao_social", "endereco"],
            "emissao_nfe": ["nome", "cpf_cnpj", "endereco"],
            "controle_acesso": ["nome", "foto", "biometria"],
            "marketing": ["nome", "email", "telefone"],
        }
        return mapeamento.get(finalidade, [])

    async def _persistir_consentimento(self, consentimento: Consentimento):
        """Persiste consentimento no banco."""
        await self.db.execute(
            text("""
            INSERT INTO consentimentos (
                id, tenant_id, titular_id, finalidade, dados_autorizados,
                status, data_consentimento, data_expiracao, ip_origem,
                evidencia, created_at
            ) VALUES (
                :id, :tenant_id, :titular_id, :finalidade, :dados_autorizados,
                :status, :data_consentimento, :data_expiracao, :ip_origem,
                :evidencia, :created_at
            )
            """),
            {
                "id": consentimento.id,
                "tenant_id": consentimento.tenant_id,
                "titular_id": consentimento.titular_id,
                "finalidade": consentimento.finalidade,
                "dados_autorizados": json.dumps(consentimento.dados_autorizados),
                "status": consentimento.status.value,
                "data_consentimento": consentimento.data_consentimento,
                "data_expiracao": consentimento.data_expiracao,
                "ip_origem": consentimento.ip_origem,
                "evidencia": consentimento.evidencia,
                "created_at": consentimento.created_at,
            },
        )
        await self.db.commit()

    async def _persistir_solicitacao(self, solicitacao: SolicitacaoTitular):
        """Persiste solicitação no banco."""
        await self.db.execute(
            text("""
            INSERT INTO solicitacoes_lgpd (
                id, tenant_id, titular_id, tipo, status, descricao,
                dados_solicitados, prazo, created_at
            ) VALUES (
                :id, :tenant_id, :titular_id, :tipo, :status, :descricao,
                :dados_solicitados, :prazo, :created_at
            )
            """),
            {
                "id": solicitacao.id,
                "tenant_id": solicitacao.tenant_id,
                "titular_id": solicitacao.titular_id,
                "tipo": solicitacao.tipo.value,
                "status": solicitacao.status.value,
                "descricao": solicitacao.descricao,
                "dados_solicitados": json.dumps(solicitacao.dados_solicitados),
                "prazo": solicitacao.prazo,
                "created_at": solicitacao.created_at,
            },
        )
        await self.db.commit()


# Instância singleton
_lgpd_control_instance: ControleLGPD | None = None


def get_lgpd_control() -> ControleLGPD:
    """Obtém instância do controle LGPD."""
    global _lgpd_control_instance
    if _lgpd_control_instance is None:
        _lgpd_control_instance = ControleLGPD()
    return _lgpd_control_instance
