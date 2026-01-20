"""
Sistema de De-duplicação de Documentos.

Gerencia unicidade de documentos fiscais e eventos.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AcaoDedup(Enum):
    """Ação resultante da de-duplicação."""
    INSERIDO = "inserido"
    ATUALIZADO = "atualizado"
    IGNORADO = "ignorado"


@dataclass
class RegraDedup:
    """Regra de de-duplicação para um tipo de documento."""
    tipo_documento: str
    tabela: str
    campos_chave: List[str]
    campos_comparacao: List[str]  # Campos para detectar se houve alteração
    permite_atualizacao: bool = True


@dataclass
class ResultadoDedup:
    """Resultado de operação de de-duplicação."""
    acao: AcaoDedup
    documento_id: UUID
    existia: bool
    versao: int
    dados_anteriores: Optional[Dict[str, Any]] = None


class DeduplicadorDocumentos:
    """Gerencia de-duplicação de documentos fiscais."""

    # Regras de de-duplicação por tipo
    REGRAS: Dict[str, RegraDedup] = {
        "nfe": RegraDedup(
            tipo_documento="nfe",
            tabela="documentos_fiscais_nfe",
            campos_chave=["chave_acesso"],
            campos_comparacao=["codigo_status", "protocolo", "data_autorizacao"],
            permite_atualizacao=True,
        ),
        "nfce": RegraDedup(
            tipo_documento="nfce",
            tabela="documentos_fiscais_nfce",
            campos_chave=["chave_acesso"],
            campos_comparacao=["codigo_status", "protocolo"],
            permite_atualizacao=True,
        ),
        "cte": RegraDedup(
            tipo_documento="cte",
            tabela="documentos_fiscais_cte",
            campos_chave=["chave_acesso"],
            campos_comparacao=["codigo_status", "protocolo"],
            permite_atualizacao=True,
        ),
        "mdfe": RegraDedup(
            tipo_documento="mdfe",
            tabela="documentos_fiscais_mdfe",
            campos_chave=["chave_acesso"],
            campos_comparacao=["codigo_status", "protocolo", "situacao"],
            permite_atualizacao=True,
        ),
        "nfse": RegraDedup(
            tipo_documento="nfse",
            tabela="documentos_fiscais_nfse",
            campos_chave=["numero", "prestador_cnpj", "codigo_municipio"],
            campos_comparacao=["codigo_verificacao", "situacao"],
            permite_atualizacao=True,
        ),
        "esocial": RegraDedup(
            tipo_documento="esocial",
            tabela="eventos_esocial",
            campos_chave=["id_evento", "numero_recibo"],
            campos_comparacao=["situacao"],
            permite_atualizacao=False,  # Eventos eSocial não são atualizados
        ),
        "fgts_guia": RegraDedup(
            tipo_documento="fgts_guia",
            tabela="guias_fgts",
            campos_chave=["numero_guia", "competencia", "tenant_id"],
            campos_comparacao=["valor_total", "situacao"],
            permite_atualizacao=True,
        ),
        "reinf": RegraDedup(
            tipo_documento="reinf",
            tabela="eventos_reinf",
            campos_chave=["id_evento", "numero_recibo"],
            campos_comparacao=["situacao"],
            permite_atualizacao=False,
        ),
    }

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def processar(
        self,
        tipo_documento: str,
        dados: Dict[str, Any],
        tenant_id: str,
        forcar_atualizacao: bool = False
    ) -> ResultadoDedup:
        """
        Processa documento com de-duplicação.

        Args:
            tipo_documento: Tipo do documento
            dados: Dados do documento
            tenant_id: ID do tenant
            forcar_atualizacao: Se True, atualiza mesmo sem alterações

        Returns:
            ResultadoDedup com ação tomada
        """
        regra = self.REGRAS.get(tipo_documento)
        if not regra:
            raise ValueError(f"Tipo de documento não suportado: {tipo_documento}")

        # Construir condição de chave
        chave = {campo: dados.get(campo) for campo in regra.campos_chave}
        chave["tenant_id"] = tenant_id

        # Verificar se existe
        existente = await self._buscar_existente(regra, chave)

        if existente is None:
            # Inserir novo
            documento_id = await self._inserir(regra, dados, tenant_id)
            return ResultadoDedup(
                acao=AcaoDedup.INSERIDO,
                documento_id=documento_id,
                existia=False,
                versao=1,
            )

        # Documento existe
        documento_id = existente["id"]
        versao_atual = existente.get("versao", 1)

        # Verificar se houve alteração
        houve_alteracao = self._detectar_alteracao(regra, existente, dados)

        if not houve_alteracao and not forcar_atualizacao:
            return ResultadoDedup(
                acao=AcaoDedup.IGNORADO,
                documento_id=documento_id,
                existia=True,
                versao=versao_atual,
            )

        # Verificar se permite atualização
        if not regra.permite_atualizacao:
            logger.info(
                f"Documento {tipo_documento} já existe e não permite atualização"
            )
            return ResultadoDedup(
                acao=AcaoDedup.IGNORADO,
                documento_id=documento_id,
                existia=True,
                versao=versao_atual,
            )

        # Atualizar
        nova_versao = await self._atualizar(
            regra, documento_id, dados, existente
        )

        return ResultadoDedup(
            acao=AcaoDedup.ATUALIZADO,
            documento_id=documento_id,
            existia=True,
            versao=nova_versao,
            dados_anteriores=existente,
        )

    async def _buscar_existente(
        self,
        regra: RegraDedup,
        chave: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Busca documento existente pela chave."""
        condicoes = " AND ".join(f"{k} = :{k}" for k in chave.keys())

        result = await self.db.execute(
            text(f"""
            SELECT * FROM {regra.tabela}
            WHERE {condicoes}
            AND ativo = true
            """),
            chave
        )

        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return None

    async def _inserir(
        self,
        regra: RegraDedup,
        dados: Dict[str, Any],
        tenant_id: str
    ) -> UUID:
        """Insere novo documento."""
        documento_id = uuid4()

        # Preparar dados
        dados_insert = {
            **dados,
            "id": documento_id,
            "tenant_id": tenant_id,
            "versao": 1,
            "ativo": True,
            "created_at": datetime.utcnow(),
        }

        # Construir query
        campos = list(dados_insert.keys())
        placeholders = [f":{c}" for c in campos]

        await self.db.execute(
            text(f"""
            INSERT INTO {regra.tabela} ({', '.join(campos)})
            VALUES ({', '.join(placeholders)})
            """),
            dados_insert
        )

        logger.info(
            f"Documento {regra.tipo_documento} inserido: {documento_id}"
        )

        return documento_id

    async def _atualizar(
        self,
        regra: RegraDedup,
        documento_id: UUID,
        dados: Dict[str, Any],
        dados_anteriores: Dict[str, Any]
    ) -> int:
        """Atualiza documento existente e registra histórico."""
        nova_versao = dados_anteriores.get("versao", 1) + 1

        # Registrar versão anterior no histórico
        await self.db.execute(
            text("""
            INSERT INTO documentos_historico (
                id, documento_id, tipo_documento, versao,
                dados_anteriores, motivo_alteracao, created_at
            ) VALUES (
                :id, :doc_id, :tipo, :versao, :dados, :motivo, NOW()
            )
            """),
            {
                "id": uuid4(),
                "doc_id": documento_id,
                "tipo": regra.tipo_documento,
                "versao": dados_anteriores.get("versao", 1),
                "dados": str(dados_anteriores),  # JSON em produção
                "motivo": "Atualização automática",
            }
        )

        # Atualizar documento
        campos_update = [
            f"{k} = :{k}" for k in dados.keys()
            if k not in ["id", "tenant_id", "created_at"]
        ]
        campos_update.append("versao = :nova_versao")
        campos_update.append("updated_at = NOW()")

        dados_update = {
            **dados,
            "nova_versao": nova_versao,
            "doc_id": documento_id,
        }

        await self.db.execute(
            text(f"""
            UPDATE {regra.tabela}
            SET {', '.join(campos_update)}
            WHERE id = :doc_id
            """),
            dados_update
        )

        logger.info(
            f"Documento {regra.tipo_documento} atualizado: "
            f"{documento_id} (versão {nova_versao})"
        )

        return nova_versao

    def _detectar_alteracao(
        self,
        regra: RegraDedup,
        existente: Dict[str, Any],
        novos: Dict[str, Any]
    ) -> bool:
        """Detecta se houve alteração nos campos relevantes."""
        for campo in regra.campos_comparacao:
            valor_existente = existente.get(campo)
            valor_novo = novos.get(campo)

            if valor_existente != valor_novo:
                logger.debug(
                    f"Alteração detectada em {campo}: "
                    f"{valor_existente} -> {valor_novo}"
                )
                return True

        return False

    async def verificar_duplicata(
        self,
        tipo_documento: str,
        chave: Dict[str, Any],
        tenant_id: str
    ) -> Tuple[bool, Optional[UUID]]:
        """
        Verifica se documento já existe.

        Returns:
            Tupla (existe, documento_id)
        """
        regra = self.REGRAS.get(tipo_documento)
        if not regra:
            return False, None

        chave["tenant_id"] = tenant_id
        existente = await self._buscar_existente(regra, chave)

        if existente:
            return True, existente["id"]
        return False, None

    @classmethod
    def obter_campos_chave(cls, tipo_documento: str) -> List[str]:
        """Retorna campos que formam a chave única do documento."""
        regra = cls.REGRAS.get(tipo_documento)
        if regra:
            return regra.campos_chave
        return []
