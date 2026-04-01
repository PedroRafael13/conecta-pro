"""
Sistema de Versionamento de Documentos.

Gerencia histórico de versões de documentos fiscais.
"""

import importlib.util as _ilu
import json
import logging
import os as _os
from dataclasses import dataclass
from datetime import datetime
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

logger = logging.getLogger(__name__)


class MotivoAlteracao(Enum):
    """Motivos de alteração de documento."""

    RETIFICACAO = "retificacao"
    CARTA_CORRECAO = "carta_correcao"
    CANCELAMENTO = "cancelamento"
    INUTILIZACAO = "inutilizacao"
    ATUALIZACAO_STATUS = "atualizacao_status"
    SINCRONIZACAO = "sincronizacao"
    MANUAL = "manual"


@dataclass
class VersaoDocumento:
    """Representa uma versão de documento."""

    id: UUID
    documento_id: UUID
    tipo_documento: str
    versao: int
    dados: dict[str, Any]
    motivo: MotivoAlteracao
    usuario_id: UUID | None
    observacao: str | None
    created_at: datetime


class GerenciadorVersoes:
    """Gerencia versionamento de documentos fiscais."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def registrar_versao(
        self,
        documento_id: UUID,
        tipo_documento: str,
        versao: int,
        dados: dict[str, Any],
        motivo: MotivoAlteracao,
        usuario_id: UUID | None = None,
        observacao: str | None = None,
    ) -> UUID:
        """
        Registra nova versão de documento.

        Args:
            documento_id: ID do documento
            tipo_documento: Tipo (nfe, cte, etc)
            versao: Número da versão
            dados: Dados da versão
            motivo: Motivo da alteração
            usuario_id: ID do usuário (se alteração manual)
            observacao: Observação adicional

        Returns:
            ID do registro de versão
        """
        versao_id = uuid4()

        await self.db.execute(
            text("""
            INSERT INTO documentos_historico (
                id, documento_id, tipo_documento, versao,
                dados_anteriores, motivo_alteracao, usuario_id,
                observacao, created_at
            ) VALUES (
                :id, :doc_id, :tipo, :versao,
                :dados, :motivo, :usuario_id,
                :obs, NOW()
            )
            """),
            {
                "id": versao_id,
                "doc_id": documento_id,
                "tipo": tipo_documento,
                "versao": versao,
                "dados": json.dumps(dados, default=str),
                "motivo": motivo.value,
                "usuario_id": usuario_id,
                "obs": observacao,
            },
        )

        logger.info(
            f"Versão {versao} registrada para documento {documento_id} ({tipo_documento}) - Motivo: {motivo.value}"
        )

        return versao_id

    async def obter_historico(self, documento_id: UUID, limite: int = 10) -> list[VersaoDocumento]:
        """
        Obtém histórico de versões de um documento.

        Args:
            documento_id: ID do documento
            limite: Máximo de versões a retornar

        Returns:
            Lista de versões ordenada da mais recente para mais antiga
        """
        result = await self.db.execute(
            text("""
            SELECT id, documento_id, tipo_documento, versao,
                   dados_anteriores, motivo_alteracao, usuario_id,
                   observacao, created_at
            FROM documentos_historico
            WHERE documento_id = :doc_id
            ORDER BY versao DESC
            LIMIT :limite
            """),
            {"doc_id": documento_id, "limite": limite},
        )

        versoes = []
        for row in result.fetchall():
            versoes.append(
                VersaoDocumento(
                    id=row.id,
                    documento_id=row.documento_id,
                    tipo_documento=row.tipo_documento,
                    versao=row.versao,
                    dados=json.loads(row.dados_anteriores) if row.dados_anteriores else {},
                    motivo=MotivoAlteracao(row.motivo_alteracao),
                    usuario_id=row.usuario_id,
                    observacao=row.observacao,
                    created_at=row.created_at,
                )
            )

        return versoes

    async def obter_versao_especifica(self, documento_id: UUID, versao: int) -> VersaoDocumento | None:
        """
        Obtém uma versão específica de um documento.

        Args:
            documento_id: ID do documento
            versao: Número da versão

        Returns:
            VersaoDocumento ou None se não encontrado
        """
        result = await self.db.execute(
            text("""
            SELECT id, documento_id, tipo_documento, versao,
                   dados_anteriores, motivo_alteracao, usuario_id,
                   observacao, created_at
            FROM documentos_historico
            WHERE documento_id = :doc_id AND versao = :versao
            """),
            {"doc_id": documento_id, "versao": versao},
        )

        row = result.fetchone()
        if not row:
            return None

        return VersaoDocumento(
            id=row.id,
            documento_id=row.documento_id,
            tipo_documento=row.tipo_documento,
            versao=row.versao,
            dados=json.loads(row.dados_anteriores) if row.dados_anteriores else {},
            motivo=MotivoAlteracao(row.motivo_alteracao),
            usuario_id=row.usuario_id,
            observacao=row.observacao,
            created_at=row.created_at,
        )

    async def comparar_versoes(self, documento_id: UUID, versao1: int, versao2: int) -> dict[str, Any]:
        """
        Compara duas versões de um documento.

        Args:
            documento_id: ID do documento
            versao1: Primeira versão
            versao2: Segunda versão

        Returns:
            Dicionário com diferenças entre as versões
        """
        v1 = await self.obter_versao_especifica(documento_id, versao1)
        v2 = await self.obter_versao_especifica(documento_id, versao2)

        if not v1 or not v2:
            raise ValueError("Uma ou ambas versões não encontradas")

        diferencas = {
            "versao_antiga": versao1,
            "versao_nova": versao2,
            "campos_alterados": [],
            "campos_adicionados": [],
            "campos_removidos": [],
        }

        # Campos na versão 1
        chaves_v1 = set(v1.dados.keys())
        chaves_v2 = set(v2.dados.keys())

        # Campos adicionados
        for campo in chaves_v2 - chaves_v1:
            diferencas["campos_adicionados"].append(
                {
                    "campo": campo,
                    "valor_novo": v2.dados[campo],
                }
            )

        # Campos removidos
        for campo in chaves_v1 - chaves_v2:
            diferencas["campos_removidos"].append(
                {
                    "campo": campo,
                    "valor_antigo": v1.dados[campo],
                }
            )

        # Campos alterados
        for campo in chaves_v1 & chaves_v2:
            if v1.dados[campo] != v2.dados[campo]:
                diferencas["campos_alterados"].append(
                    {
                        "campo": campo,
                        "valor_antigo": v1.dados[campo],
                        "valor_novo": v2.dados[campo],
                    }
                )

        return diferencas

    async def restaurar_versao(
        self, documento_id: UUID, versao: int, tabela: str, usuario_id: UUID | None = None
    ) -> bool:
        """
        Restaura documento para uma versão anterior.

        Args:
            documento_id: ID do documento
            versao: Versão a restaurar
            tabela: Tabela do documento
            usuario_id: ID do usuário que está restaurando

        Returns:
            True se restaurado com sucesso
        """
        versao_obj = await self.obter_versao_especifica(documento_id, versao)
        if not versao_obj:
            raise ValueError(f"Versão {versao} não encontrada")

        validate_table_name(tabela)

        # Obter versão atual
        result = await self.db.execute(text(f"SELECT * FROM {tabela} WHERE id = :id"), {"id": documento_id})  # noqa: S608
        atual = result.fetchone()
        if not atual:
            raise ValueError("Documento não encontrado")

        versao_atual = atual.versao if hasattr(atual, "versao") else 1

        # Registrar versão atual antes de restaurar
        await self.registrar_versao(
            documento_id=documento_id,
            tipo_documento=versao_obj.tipo_documento,
            versao=versao_atual,
            dados=dict(atual._mapping),
            motivo=MotivoAlteracao.MANUAL,
            usuario_id=usuario_id,
            observacao=f"Antes de restaurar para versão {versao}",
        )

        # Restaurar dados
        dados = versao_obj.dados
        dados["versao"] = versao_atual + 1
        dados["updated_at"] = datetime.utcnow()

        # Construir UPDATE
        campos_update = [f"{k} = :{k}" for k in dados.keys() if k not in ["id", "tenant_id", "created_at"]]

        await self.db.execute(
            text(f"""
            UPDATE {tabela}
            SET {", ".join(campos_update)}
            WHERE id = :documento_id
            """),
            {**dados, "documento_id": documento_id},
        )

        logger.info(f"Documento {documento_id} restaurado para versão {versao}")

        return True

    async def contar_versoes(self, documento_id: UUID) -> int:
        """Conta número de versões de um documento."""
        result = await self.db.execute(
            text("""
            SELECT COUNT(*) FROM documentos_historico
            WHERE documento_id = :doc_id
            """),
            {"doc_id": documento_id},
        )
        return result.scalar() or 0

    async def obter_versao_mais_recente(self, documento_id: UUID) -> VersaoDocumento | None:
        """Obtém a versão mais recente no histórico."""
        result = await self.db.execute(
            text("""
            SELECT id, documento_id, tipo_documento, versao,
                   dados_anteriores, motivo_alteracao, usuario_id,
                   observacao, created_at
            FROM documentos_historico
            WHERE documento_id = :doc_id
            ORDER BY versao DESC
            LIMIT 1
            """),
            {"doc_id": documento_id},
        )

        row = result.fetchone()
        if not row:
            return None

        return VersaoDocumento(
            id=row.id,
            documento_id=row.documento_id,
            tipo_documento=row.tipo_documento,
            versao=row.versao,
            dados=json.loads(row.dados_anteriores) if row.dados_anteriores else {},
            motivo=MotivoAlteracao(row.motivo_alteracao),
            usuario_id=row.usuario_id,
            observacao=row.observacao,
            created_at=row.created_at,
        )

    async def limpar_historico_antigo(self, dias: int = 365, manter_minimo: int = 5) -> int:
        """
        Remove versões antigas do histórico.

        Args:
            dias: Versões mais antigas que isso podem ser removidas
            manter_minimo: Mínimo de versões a manter por documento

        Returns:
            Número de registros removidos
        """
        # Esta é uma operação complexa que precisa manter
        # pelo menos X versões por documento
        result = await self.db.execute(
            text("""
            DELETE FROM documentos_historico
            WHERE id IN (
                SELECT h.id
                FROM documentos_historico h
                WHERE h.created_at < NOW() - INTERVAL ':dias days'
                AND (
                    SELECT COUNT(*)
                    FROM documentos_historico h2
                    WHERE h2.documento_id = h.documento_id
                    AND h2.versao > h.versao
                ) >= :manter
            )
            """),
            {"dias": dias, "manter": manter_minimo},
        )

        count = result.rowcount
        if count > 0:
            logger.info(f"Removidos {count} registros antigos do histórico")

        return count
