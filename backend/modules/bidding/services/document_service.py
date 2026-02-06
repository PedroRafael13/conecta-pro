"""
Service de Documento da Empresa - Licitacoes
============================================
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from modules.bidding.repositories.document_repository import DocumentRepository
from modules.bidding.models.company_document import CompanyDocument, DocumentType, DocumentStatus
from modules.bidding.schemas.document import (
    CompanyDocumentCreate, CompanyDocumentUpdate, CompanyDocumentResponse,
    DocumentExpiringResponse, DocumentTypeInfo
)

logger = logging.getLogger(__name__)


class DocumentService:
    """Service para operacoes com documentos da empresa."""

    # Documentos obrigatorios para licitacao
    DOCUMENTOS_OBRIGATORIOS = [
        DocumentType.CND_FEDERAL,
        DocumentType.CND_TRABALHISTA,
        DocumentType.CRF_FGTS,
        DocumentType.CND_MUNICIPAL,
        DocumentType.CNPJ,
        DocumentType.CONTRATO_SOCIAL,
    ]

    # Validade padrao por tipo (dias)
    VALIDADE_PADRAO = {
        DocumentType.CND_FEDERAL.value: 180,
        DocumentType.CND_TRABALHISTA.value: 180,
        DocumentType.CRF_FGTS.value: 30,
        DocumentType.CND_MUNICIPAL.value: 90,
        DocumentType.CND_ESTADUAL.value: 90,
        DocumentType.CERTIDAO_FALENCIA.value: 90,
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = DocumentRepository(db)

    async def get(self, document_id: UUID) -> Optional[CompanyDocumentResponse]:
        """Busca documento por ID."""
        doc = await self.repository.get_by_id(document_id)
        if not doc:
            return None
        return self._to_response(doc)

    async def get_by_tipo(self, tipo: str) -> Optional[CompanyDocumentResponse]:
        """Busca documento mais recente por tipo."""
        doc = await self.repository.get_by_tipo(tipo)
        if not doc:
            return None
        return self._to_response(doc)

    async def list(
        self,
        tipo: str = None,
        status: str = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[CompanyDocumentResponse], int]:
        """Lista documentos."""
        items, total = await self.repository.list(tipo, status, page, size)
        return [self._to_response(d) for d in items], total

    async def create(
        self,
        data: CompanyDocumentCreate,
        user_id: UUID = None
    ) -> CompanyDocumentResponse:
        """Cria novo documento."""
        doc = await self.repository.create(data, user_id)
        return self._to_response(doc)

    async def update(
        self,
        document_id: UUID,
        data: CompanyDocumentUpdate,
        user_id: UUID = None
    ) -> Optional[CompanyDocumentResponse]:
        """Atualiza documento."""
        doc = await self.repository.update(document_id, data, user_id)
        if not doc:
            return None
        return self._to_response(doc)

    async def delete(self, document_id: UUID) -> bool:
        """Remove documento."""
        return await self.repository.delete(document_id)

    async def get_expiring(self, days: int = 30) -> DocumentExpiringResponse:
        """Lista documentos vencendo e vencidos."""
        expiring = await self.repository.get_expiring(days)
        expired = await self.repository.get_expired()

        return DocumentExpiringResponse(
            documentos_vencendo=[self._to_response(d) for d in expiring],
            documentos_vencidos=[self._to_response(d) for d in expired],
            total_vencendo=len(expiring),
            total_vencidos=len(expired),
            dias_alerta=days
        )

    async def verificar_habilitacao(self) -> dict:
        """Verifica se empresa esta habilitada para licitar."""
        todos_docs = await self.repository.list(page=1, size=100)
        docs_by_tipo = {d.tipo: d for d, _ in [todos_docs]}

        resultado = {
            "habilitada": True,
            "documentos_ok": [],
            "documentos_pendentes": [],
            "documentos_vencidos": [],
            "documentos_vencendo": []
        }

        for tipo_obrigatorio in self.DOCUMENTOS_OBRIGATORIOS:
            tipo = tipo_obrigatorio.value
            doc = docs_by_tipo.get(tipo)

            if not doc:
                resultado["habilitada"] = False
                resultado["documentos_pendentes"].append(tipo)
            elif doc.status == DocumentStatus.EXPIRED.value:
                resultado["habilitada"] = False
                resultado["documentos_vencidos"].append(tipo)
            elif doc.status == DocumentStatus.EXPIRING.value:
                resultado["documentos_vencendo"].append(tipo)
                resultado["documentos_ok"].append(tipo)
            else:
                resultado["documentos_ok"].append(tipo)

        return resultado

    async def get_tipos_documento(self) -> List[DocumentTypeInfo]:
        """Retorna informacoes sobre tipos de documento."""
        tipos = []
        for doc_type in DocumentType:
            tipo = DocumentTypeInfo(
                tipo=doc_type.value,
                nome=doc_type.name.replace("_", " ").title(),
                descricao=self._get_descricao_tipo(doc_type),
                renovacao_automatica_disponivel=doc_type in [
                    DocumentType.CND_FEDERAL,
                    DocumentType.CND_TRABALHISTA,
                    DocumentType.CRF_FGTS
                ],
                validade_padrao_dias=self.VALIDADE_PADRAO.get(doc_type.value),
                obrigatorio_licitacao=doc_type in self.DOCUMENTOS_OBRIGATORIOS
            )
            tipos.append(tipo)
        return tipos

    async def get_status_geral(self) -> dict:
        """Retorna status geral dos documentos."""
        contagem = await self.repository.count_by_status()
        expiring = await self.repository.get_expiring(30)
        expired = await self.repository.get_expired()

        total = sum(contagem.values())
        validos = contagem.get(DocumentStatus.VALID.value, 0)

        return {
            "total_documentos": total,
            "documentos_validos": validos,
            "documentos_vencendo": len(expiring),
            "documentos_vencidos": len(expired),
            "por_status": contagem,
            "percentual_regularidade": (validos / total * 100) if total > 0 else 0
        }

    async def atualizar_todos_status(self) -> int:
        """Atualiza status de todos os documentos."""
        return await self.repository.update_all_status()

    def _to_response(self, doc: CompanyDocument) -> CompanyDocumentResponse:
        """Converte model para response."""
        return CompanyDocumentResponse(
            id=doc.id,
            tipo=doc.tipo,
            nome=doc.nome,
            descricao=doc.descricao,
            numero=doc.numero,
            orgao_emissor=doc.orgao_emissor,
            status=doc.status,
            ativo=doc.ativo,
            data_emissao=doc.data_emissao,
            data_validade=doc.data_validade,
            arquivo_url=doc.arquivo_url,
            arquivo_nome=doc.arquivo_nome,
            arquivo_tamanho=doc.arquivo_tamanho,
            certidao_automatica=doc.certidao_automatica,
            ultima_verificacao=doc.ultima_verificacao,
            ultima_renovacao=doc.ultima_renovacao,
            erro_renovacao=doc.erro_renovacao,
            metadados=doc.metadados or {},
            observacoes=doc.observacoes,
            esta_valido=doc.esta_valido,
            dias_para_vencer=doc.dias_para_vencer,
            esta_vencendo=doc.esta_vencendo,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )

    def _get_descricao_tipo(self, tipo: DocumentType) -> str:
        """Retorna descricao do tipo de documento."""
        descricoes = {
            DocumentType.CND_FEDERAL: "Certidao Negativa de Debitos relativos a Creditos Tributarios Federais e a Divida Ativa da Uniao",
            DocumentType.CND_TRABALHISTA: "Certidao Negativa de Debitos Trabalhistas (CNDT)",
            DocumentType.CRF_FGTS: "Certificado de Regularidade do FGTS (CRF)",
            DocumentType.CND_MUNICIPAL: "Certidao Negativa de Debitos Municipais (ISS/IPTU)",
            DocumentType.CND_ESTADUAL: "Certidao Negativa de Debitos Estaduais (ICMS)",
            DocumentType.CONTRATO_SOCIAL: "Contrato Social e suas alteracoes",
            DocumentType.CNPJ: "Cartao de inscricao no CNPJ",
            DocumentType.ATESTADO_CAPACIDADE: "Atestado de Capacidade Tecnica",
            DocumentType.BALANCO_PATRIMONIAL: "Balanco Patrimonial e DRE",
            DocumentType.CERTIDAO_FALENCIA: "Certidao Negativa de Falencia e Recuperacao Judicial",
        }
        return descricoes.get(tipo, tipo.value)
