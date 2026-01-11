"""
Service de Certidao - Licitacoes
================================
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from modules.bidding.models.certificate import (
    Certificate, CertificateType, CertificateStatus, CertificateSource
)
from modules.bidding.schemas.certificate import (
    CertificateCreate, CertificateUpdate, CertificateResponse,
    CertificateRenewRequest, CertificateRenewResponse,
    CertificateBulkStatusResponse, CertificateTypeInfo
)

logger = logging.getLogger(__name__)


class CertificateService:
    """Service para operacoes com certidoes."""

    # URLs para emissao de certidoes
    URLS_EMISSAO = {
        CertificateType.CND_FEDERAL.value: "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir",
        CertificateType.CND_TRABALHISTA.value: "https://www.tst.jus.br/certidao1",
        CertificateType.CRF_FGTS.value: "https://consulta-crf.caixa.gov.br/",
    }

    # Validade padrao (dias)
    VALIDADE_PADRAO = {
        CertificateType.CND_FEDERAL.value: 180,
        CertificateType.CND_TRABALHISTA.value: 180,
        CertificateType.CRF_FGTS.value: 30,
        CertificateType.CND_ESTADUAL.value: 90,
        CertificateType.CND_MUNICIPAL.value: 90,
        CertificateType.CERTIDAO_FALENCIA.value: 90,
    }

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, certificate_id: UUID) -> Optional[CertificateResponse]:
        """Busca certidao por ID."""
        result = await self.db.execute(
            select(Certificate).where(
                Certificate.id == certificate_id,
                Certificate.ativo == True
            )
        )
        cert = result.scalar_one_or_none()
        if not cert:
            return None
        return self._to_response(cert)

    async def get_by_tipo(
        self,
        cnpj: str,
        tipo: str
    ) -> Optional[CertificateResponse]:
        """Busca certidao mais recente por CNPJ e tipo."""
        result = await self.db.execute(
            select(Certificate).where(
                Certificate.cnpj == cnpj,
                Certificate.tipo == tipo,
                Certificate.ativo == True
            ).order_by(Certificate.data_validade.desc())
        )
        cert = result.scalar_one_or_none()
        if not cert:
            return None
        return self._to_response(cert)

    async def list(
        self,
        cnpj: str = None,
        tipo: str = None,
        status: str = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[CertificateResponse], int]:
        """Lista certidoes com filtros."""
        query = select(Certificate).where(Certificate.ativo == True)

        if cnpj:
            query = query.where(Certificate.cnpj == cnpj)

        if tipo:
            query = query.where(Certificate.tipo == tipo)

        if status:
            query = query.where(Certificate.status == status)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginacao
        query = query.order_by(Certificate.data_validade.asc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return [self._to_response(c) for c in items], total

    async def create(
        self,
        data: CertificateCreate,
        user_id: UUID = None
    ) -> CertificateResponse:
        """Cria nova certidao."""
        cert = Certificate(
            **data.model_dump(exclude_unset=True),
            created_by=user_id
        )
        cert.atualizar_status()

        self.db.add(cert)
        await self.db.commit()
        await self.db.refresh(cert)
        logger.info(f"Certidao criada: {cert.tipo} - {cert.cnpj}")
        return self._to_response(cert)

    async def update(
        self,
        certificate_id: UUID,
        data: CertificateUpdate,
        user_id: UUID = None
    ) -> Optional[CertificateResponse]:
        """Atualiza certidao."""
        result = await self.db.execute(
            select(Certificate).where(Certificate.id == certificate_id)
        )
        cert = result.scalar_one_or_none()
        if not cert:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cert, field, value)

        cert.updated_by = user_id
        cert.updated_at = datetime.utcnow()
        cert.atualizar_status()

        await self.db.commit()
        await self.db.refresh(cert)
        return self._to_response(cert)

    async def delete(self, certificate_id: UUID) -> bool:
        """Remove certidao (soft delete)."""
        result = await self.db.execute(
            select(Certificate).where(Certificate.id == certificate_id)
        )
        cert = result.scalar_one_or_none()
        if not cert:
            return False

        cert.ativo = False
        cert.updated_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def get_status_geral(self, cnpj: str) -> CertificateBulkStatusResponse:
        """Retorna status geral das certidoes de uma empresa."""
        certidoes, _ = await self.list(cnpj=cnpj, page=1, size=100)

        validas = [c for c in certidoes if c.status == CertificateStatus.VALID.value]
        vencendo = [c for c in certidoes if c.status == CertificateStatus.EXPIRING.value]
        vencidas = [c for c in certidoes if c.status == CertificateStatus.EXPIRED.value]
        pendentes = [c for c in certidoes if c.status == CertificateStatus.PENDING.value]
        com_erro = [c for c in certidoes if c.status == CertificateStatus.ERROR.value]

        # Agrupa por tipo
        por_tipo = {}
        for c in certidoes:
            if c.tipo not in por_tipo:
                por_tipo[c.tipo] = {"total": 0, "validas": 0, "vencidas": 0}
            por_tipo[c.tipo]["total"] += 1
            if c.status == CertificateStatus.VALID.value:
                por_tipo[c.tipo]["validas"] += 1
            elif c.status == CertificateStatus.EXPIRED.value:
                por_tipo[c.tipo]["vencidas"] += 1

        # Alertas
        alertas = []
        if vencidas:
            alertas.append(f"{len(vencidas)} certidao(oes) vencida(s)")
        if vencendo:
            alertas.append(f"{len(vencendo)} certidao(oes) vencendo em breve")
        if pendentes:
            alertas.append(f"{len(pendentes)} certidao(oes) pendente(s)")

        return CertificateBulkStatusResponse(
            total=len(certidoes),
            validas=len(validas),
            vencendo=len(vencendo),
            vencidas=len(vencidas),
            pendentes=len(pendentes),
            com_erro=len(com_erro),
            certidoes=certidoes,
            por_tipo=por_tipo,
            alertas=alertas
        )

    async def renovar(
        self,
        request: CertificateRenewRequest
    ) -> CertificateRenewResponse:
        """Solicita renovacao de certidao."""
        result = await self.db.execute(
            select(Certificate).where(Certificate.id == request.certificate_id)
        )
        cert = result.scalar_one_or_none()

        if not cert:
            return CertificateRenewResponse(
                certificate_id=request.certificate_id,
                sucesso=False,
                mensagem="Certidao nao encontrada"
            )

        if not cert.obtencao_automatica:
            return CertificateRenewResponse(
                certificate_id=request.certificate_id,
                sucesso=False,
                mensagem="Certidao nao possui renovacao automatica habilitada"
            )

        # Marca para renovacao
        cert.status = CertificateStatus.RENEWING.value
        cert.proxima_tentativa = datetime.utcnow()
        await self.db.commit()

        return CertificateRenewResponse(
            certificate_id=cert.id,
            sucesso=True,
            mensagem="Renovacao agendada"
        )

    async def atualizar_todos_status(self, cnpj: str = None) -> int:
        """Atualiza status de todas as certidoes."""
        query = select(Certificate).where(Certificate.ativo == True)
        if cnpj:
            query = query.where(Certificate.cnpj == cnpj)

        result = await self.db.execute(query)
        certidoes = result.scalars().all()

        updated = 0
        for cert in certidoes:
            old_status = cert.status
            cert.atualizar_status()
            if cert.status != old_status:
                updated += 1

        await self.db.commit()
        logger.info(f"Status atualizado para {updated} certidoes")
        return updated

    async def get_pending_renewal(self) -> List[CertificateResponse]:
        """Lista certidoes pendentes de renovacao automatica."""
        agora = datetime.utcnow()
        result = await self.db.execute(
            select(Certificate).where(
                Certificate.ativo == True,
                Certificate.obtencao_automatica == True,
                Certificate.proxima_tentativa <= agora,
                Certificate.status.in_([
                    CertificateStatus.EXPIRED.value,
                    CertificateStatus.EXPIRING.value,
                    CertificateStatus.RENEWING.value
                ])
            )
        )
        return [self._to_response(c) for c in result.scalars().all()]

    async def get_tipos_certidao(self) -> List[CertificateTypeInfo]:
        """Retorna informacoes sobre tipos de certidao."""
        tipos = []
        for cert_type in CertificateType:
            tipo = CertificateTypeInfo(
                tipo=cert_type.value,
                nome=cert_type.name.replace("_", " ").title(),
                descricao=self._get_descricao_tipo(cert_type),
                orgao_emissor=self._get_orgao_emissor(cert_type),
                url_emissao=self.URLS_EMISSAO.get(cert_type.value),
                validade_padrao_dias=self.VALIDADE_PADRAO.get(cert_type.value, 180),
                renovacao_automatica_disponivel=cert_type in [
                    CertificateType.CND_FEDERAL,
                    CertificateType.CND_TRABALHISTA,
                    CertificateType.CRF_FGTS
                ],
                obrigatoria=cert_type in [
                    CertificateType.CND_FEDERAL,
                    CertificateType.CND_TRABALHISTA,
                    CertificateType.CRF_FGTS,
                    CertificateType.CND_MUNICIPAL,
                    CertificateType.CERTIDAO_FALENCIA
                ]
            )
            tipos.append(tipo)
        return tipos

    def _to_response(self, cert: Certificate) -> CertificateResponse:
        """Converte model para response."""
        return CertificateResponse(
            id=cert.id,
            tipo=cert.tipo,
            nome=cert.nome,
            cnpj=cert.cnpj,
            razao_social=cert.razao_social,
            status=cert.status,
            ativo=cert.ativo,
            codigo_verificacao=cert.codigo_verificacao,
            data_emissao=cert.data_emissao,
            data_validade=cert.data_validade,
            hora_emissao=cert.hora_emissao,
            situacao=cert.situacao,
            texto_certidao=cert.texto_certidao,
            observacoes_orgao=cert.observacoes_orgao,
            arquivo_url=cert.arquivo_url,
            arquivo_nome=cert.arquivo_nome,
            arquivo_hash=cert.arquivo_hash,
            fonte=cert.fonte,
            obtencao_automatica=cert.obtencao_automatica,
            ultima_tentativa=cert.ultima_tentativa,
            proxima_tentativa=cert.proxima_tentativa,
            tentativas_falha=cert.tentativas_falha,
            erro_obtencao=cert.erro_obtencao,
            alerta_enviado_30d=cert.alerta_enviado_30d,
            alerta_enviado_15d=cert.alerta_enviado_15d,
            alerta_enviado_7d=cert.alerta_enviado_7d,
            orgao_emissor=cert.orgao_emissor,
            orgao_uf=cert.orgao_uf,
            orgao_url=cert.orgao_url,
            metadados=cert.metadados or {},
            esta_valida=cert.esta_valida,
            dias_para_vencer=cert.dias_para_vencer,
            horas_para_vencer=cert.horas_para_vencer,
            esta_vencendo=cert.esta_vencendo,
            precisa_renovar=cert.precisa_renovar,
            pode_usar_licitacao=cert.pode_usar_licitacao,
            observacoes=cert.observacoes,
            created_at=cert.created_at,
            updated_at=cert.updated_at
        )

    def _get_descricao_tipo(self, tipo: CertificateType) -> str:
        """Retorna descricao do tipo."""
        descricoes = {
            CertificateType.CND_FEDERAL: "Certidao Negativa de Debitos relativos a Creditos Tributarios Federais e a Divida Ativa da Uniao (CND)",
            CertificateType.CND_TRABALHISTA: "Certidao Negativa de Debitos Trabalhistas (CNDT)",
            CertificateType.CRF_FGTS: "Certificado de Regularidade do FGTS (CRF)",
            CertificateType.CND_ESTADUAL: "Certidao Negativa de Debitos Estaduais",
            CertificateType.CND_MUNICIPAL: "Certidao Negativa de Debitos Municipais",
            CertificateType.CERTIDAO_FALENCIA: "Certidao Negativa de Falencia e Recuperacao Judicial",
        }
        return descricoes.get(tipo, tipo.value)

    def _get_orgao_emissor(self, tipo: CertificateType) -> str:
        """Retorna orgao emissor."""
        orgaos = {
            CertificateType.CND_FEDERAL: "Receita Federal do Brasil",
            CertificateType.CND_TRABALHISTA: "Tribunal Superior do Trabalho",
            CertificateType.CRF_FGTS: "Caixa Economica Federal",
            CertificateType.CND_ESTADUAL: "Secretaria de Fazenda Estadual",
            CertificateType.CND_MUNICIPAL: "Prefeitura Municipal",
            CertificateType.CERTIDAO_FALENCIA: "Tribunal de Justica",
        }
        return orgaos.get(tipo, "Nao especificado")
