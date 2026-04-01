"""
SignatureService - Servico de Assinaturas Digitais.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.disciplinary.models import (
    DigitalSignature,
    DisciplinaryAction,
    DisciplinaryActionStatus,
    SignerType,
)
from modules.operacional.disciplinary.repositories import (
    DisciplinaryRepository,
    SignatureRepository,
)
from modules.operacional.disciplinary.schemas import (
    RefuseSignRequest,
    SignatureCreate,
    SignatureVerifyRequest,
    SignatureVerifyResponse,
    SignRequest,
)


class SignatureServiceError(Exception):
    """Excecao base para erros do servico de assinaturas."""

    pass


class SignatureNotFoundError(SignatureServiceError):
    """Assinatura nao encontrada."""

    pass


class SignatureValidationError(SignatureServiceError):
    """Erro de validacao de assinatura."""

    pass


class SignatureService:
    """
    Servico para gestao de assinaturas digitais.

    Gerencia coleta, validacao e verificacao de assinaturas
    em documentos disciplinares.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o servico.

        Args:
            db: Sessao async do SQLAlchemy
        """
        self.db = db
        self.repo = SignatureRepository(db)
        self.disciplinary_repo = DisciplinaryRepository(db)

    async def sign_document(
        self,
        action_id: str,
        tenant_id: str,
        signer_id: str,
        signer_name: str,
        signer_cpf: str | None,
        request: SignRequest,
    ) -> DigitalSignature:
        """
        Assina um documento disciplinar.

        Args:
            action_id: ID da medida disciplinar
            tenant_id: ID do tenant
            signer_id: ID do signatario
            signer_name: Nome do signatario
            signer_cpf: CPF do signatario
            request: Dados da assinatura

        Returns:
            Assinatura criada

        Raises:
            SignatureValidationError: Se assinatura invalida
        """
        # Buscar medida
        action = await self.disciplinary_repo.get_by_id(action_id, tenant_id)
        if not action:
            raise SignatureValidationError(f"Medida {action_id} nao encontrada")

        if not action.can_be_signed:
            raise SignatureValidationError(f"Medida {action.code} nao pode ser assinada no status {action.status}")

        if not action.document_text:
            raise SignatureValidationError(f"Medida {action.code} nao possui documento gerado")

        # Calcular hash do documento atual
        document_hash = DigitalSignature.create_hash(action.document_text)

        # Criar assinatura
        signature_data = SignatureCreate(
            signer_id=signer_id,
            signer_type=request.signer_type,
            signer_name=signer_name,
            signer_cpf=signer_cpf,
            document_type="disciplinary_action",
            document_id=action_id,
            signature_data=request.signature_data,
            signature_hash=document_hash,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            latitude=request.latitude,
            longitude=request.longitude,
            geolocation_accuracy=request.geolocation_accuracy,
        )

        signature = await self.repo.create(signature_data, tenant_id)

        # Atualizar medida com a assinatura
        await self._update_action_signature(action, signature, request.signer_type)

        logger.info(
            f"Documento assinado: {action.code}",
            extra={
                "action_id": action_id,
                "signature_id": signature.id,
                "signer_type": request.signer_type.value,
            },
        )

        return signature

    async def _update_action_signature(
        self,
        action: DisciplinaryAction,
        signature: DigitalSignature,
        signer_type: SignerType,
    ) -> None:
        """
        Atualiza a medida com os dados da assinatura.

        Args:
            action: Medida disciplinar
            signature: Assinatura criada
            signer_type: Tipo do signatario
        """
        now = datetime.utcnow()

        if signer_type == SignerType.EMPLOYEE:
            action.employee_signature_id = signature.id
            action.employee_signed_at = now
            action.employee_acknowledged = True
            action.acknowledged_at = now
        elif signer_type == SignerType.SUPERVISOR:
            action.supervisor_signature_id = signature.id
            action.supervisor_signed_at = now
        elif signer_type == SignerType.HR:
            action.hr_signature_id = signature.id
            action.hr_signed_at = now

        # Verificar se todas assinaturas necessarias foram coletadas
        if await self._check_all_signatures_collected(action):
            action.status = DisciplinaryActionStatus.ASSINADA.value

        action.updated_at = now
        await self.db.commit()

    async def _check_all_signatures_collected(self, action: DisciplinaryAction) -> bool:
        """
        Verifica se todas as assinaturas necessarias foram coletadas.

        Args:
            action: Medida disciplinar

        Returns:
            True se todas assinaturas coletadas
        """
        # Funcionario e obrigatorio (ou recusa)
        if not action.employee_signature_id and not action.employee_refused_sign:
            return False

        # Supervisor e obrigatorio
        if not action.supervisor_signature_id:
            return False

        # RH e opcional para advertencias, obrigatorio para suspensoes e justa causa
        if action.is_suspension or action.is_termination:
            if not action.hr_signature_id:
                return False

        return True

    async def refuse_signature(
        self,
        action_id: str,
        tenant_id: str,
        request: RefuseSignRequest,
    ) -> DisciplinaryAction:
        """
        Registra recusa de assinatura do funcionario.

        Para advertencias escritas, requer duas testemunhas.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            request: Dados da recusa com testemunhas

        Returns:
            Medida atualizada

        Raises:
            SignatureValidationError: Se dados invalidos
        """
        action = await self.disciplinary_repo.get_by_id(action_id, tenant_id)
        if not action:
            raise SignatureValidationError(f"Medida {action_id} nao encontrada")

        if not action.can_be_signed:
            raise SignatureValidationError(
                f"Medida {action.code} nao pode ter recusa registrada no status {action.status}"
            )

        # Atualizar medida
        action.employee_refused_sign = True
        action.refusal_witness_1_name = request.witness_1_name
        action.refusal_witness_1_cpf = request.witness_1_cpf
        action.refusal_witness_2_name = request.witness_2_name
        action.refusal_witness_2_cpf = request.witness_2_cpf
        action.employee_acknowledged = True
        action.acknowledged_at = datetime.utcnow()

        # Verificar se pode mudar status
        if action.supervisor_signature_id:
            if action.is_suspension or action.is_termination:
                if action.hr_signature_id:
                    action.status = DisciplinaryActionStatus.RECUSADA_ASSINATURA.value
            else:
                action.status = DisciplinaryActionStatus.RECUSADA_ASSINATURA.value

        action.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(action)

        logger.info(
            f"Recusa de assinatura registrada: {action.code}",
            extra={
                "action_id": action_id,
                "witness_1": request.witness_1_name,
                "witness_2": request.witness_2_name,
            },
        )

        return action

    async def verify_signature(
        self,
        request: SignatureVerifyRequest,
        tenant_id: str,
    ) -> SignatureVerifyResponse:
        """
        Verifica validade de uma assinatura.

        Compara o hash armazenado com o hash do documento atual.

        Args:
            request: Dados para verificacao
            tenant_id: ID do tenant

        Returns:
            Resultado da verificacao

        Raises:
            SignatureNotFoundError: Se assinatura nao encontrada
        """
        signature = await self.repo.get_by_id(request.signature_id, tenant_id)
        if not signature:
            raise SignatureNotFoundError(f"Assinatura {request.signature_id} nao encontrada")

        # Verificar hash
        hash_matches = signature.verify_hash(request.document_content)

        # Montar resposta
        if not signature.is_valid:
            message = f"Assinatura invalidada em {signature.invalidated_at}: {signature.invalidation_reason}"
            is_valid = False
        elif not hash_matches:
            message = "Documento foi modificado apos assinatura"
            is_valid = False
        else:
            message = "Assinatura valida"
            is_valid = True

        return SignatureVerifyResponse(
            is_valid=is_valid,
            hash_matches=hash_matches,
            signature_date=signature.created_at,
            signer_name=signature.signer_name,
            signer_type=signature.signer_type,
            message=message,
        )

    async def get_by_id(self, signature_id: str, tenant_id: str) -> DigitalSignature:
        """
        Busca assinatura por ID.

        Args:
            signature_id: ID da assinatura
            tenant_id: ID do tenant

        Returns:
            Assinatura

        Raises:
            SignatureNotFoundError: Se nao encontrada
        """
        signature = await self.repo.get_by_id(signature_id, tenant_id)
        if not signature:
            raise SignatureNotFoundError(f"Assinatura {signature_id} nao encontrada")
        return signature

    async def get_by_document(
        self,
        document_id: str,
        tenant_id: str,
    ) -> list[DigitalSignature]:
        """
        Lista assinaturas de um documento.

        Args:
            document_id: ID do documento
            tenant_id: ID do tenant

        Returns:
            Lista de assinaturas
        """
        return await self.repo.get_by_document("disciplinary_action", document_id, tenant_id)

    async def invalidate(
        self,
        signature_id: str,
        tenant_id: str,
        reason: str,
    ) -> DigitalSignature:
        """
        Invalida uma assinatura.

        Args:
            signature_id: ID da assinatura
            tenant_id: ID do tenant
            reason: Motivo da invalidacao

        Returns:
            Assinatura invalidada

        Raises:
            SignatureNotFoundError: Se nao encontrada
        """
        signature = await self.repo.invalidate(signature_id, tenant_id, reason)
        if not signature:
            raise SignatureNotFoundError(f"Assinatura {signature_id} nao encontrada")

        logger.warning(
            f"Assinatura invalidada: {signature_id}",
            extra={"reason": reason, "tenant_id": tenant_id},
        )

        return signature


def get_signature_service(db: AsyncSession) -> SignatureService:
    """
    Factory para criar instancia do servico.

    Args:
        db: Sessao do banco de dados

    Returns:
        Instancia do SignatureService
    """
    return SignatureService(db)
