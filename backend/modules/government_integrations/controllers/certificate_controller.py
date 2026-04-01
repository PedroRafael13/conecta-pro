"""
Module: Certificate Controller
Description: Endpoints REST para gerenciamento de certificados digitais A1
Author: Conecta PRO Team
Date: 2026-01-15
Quality Score Target: 99+/100
"""

import base64
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from core.auth.dependencies import CurrentActiveUser
from modules.government_integrations.core.certificate_manager import (
    CertificateManager,
    CertificateStore,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/certificates", tags=["Certificates"])


# =============================================================================
# Schemas
# =============================================================================


class CertificateUploadResponse(BaseModel):
    """Resposta do upload de certificado."""

    success: bool
    certificate_id: str
    subject: str
    issuer: str
    cpf_cnpj: str | None
    valid_from: datetime
    valid_until: datetime
    days_until_expiry: int
    type: str
    message: str


class CertificateInfoResponse(BaseModel):
    """Informacoes do certificado."""

    certificate_id: str
    subject_cn: str
    issuer_cn: str
    cpf_cnpj: str | None
    serial_number: str
    valid_from: datetime
    valid_until: datetime
    days_until_expiry: int
    is_valid: bool
    status: str
    type: str


class CertificateListResponse(BaseModel):
    """Lista de certificados."""

    total: int
    certificates: list[CertificateInfoResponse]


class CertificateValidationResponse(BaseModel):
    """Resultado da validacao do certificado."""

    is_valid: bool
    message: str
    subject: str | None
    cpf_cnpj: str | None
    valid_until: datetime | None
    days_until_expiry: int | None
    warnings: list[str]


class CertificateDeleteResponse(BaseModel):
    """Resposta de exclusao de certificado."""

    success: bool
    message: str


# =============================================================================
# Certificate Store Instance
# =============================================================================

# Instancia global do store de certificados
_certificate_store: CertificateStore | None = None


def get_certificate_store() -> CertificateStore:
    """Retorna instancia do CertificateStore."""
    global _certificate_store
    if _certificate_store is None:
        _certificate_store = CertificateStore()
    return _certificate_store


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/upload",
    response_model=CertificateUploadResponse,
    summary="Upload de Certificado A1",
    description="Faz upload de um certificado digital A1 (.pfx ou .p12, status_code=201)",
)
async def upload_certificate(
    current_user: CurrentActiveUser,
    file: UploadFile = File(..., description="Arquivo .pfx ou .p12 do certificado"),
    password: str = Form(..., description="Senha do certificado"),
    alias: str | None = Form(None, description="Alias/nome identificador do certificado"),
    store: CertificateStore = Depends(get_certificate_store),
):
    """
    Faz upload de um certificado digital A1.

    - **file**: Arquivo do certificado (.pfx ou .p12)
    - **password**: Senha para desbloquear o certificado
    - **alias**: Nome identificador opcional
    """
    # Valida extensao do arquivo
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome do arquivo nao informado")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pfx", "p12"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato invalido. Use .pfx ou .p12")

    try:
        # Le conteudo do arquivo
        content = await file.read()

        # Cria CertificateManager com dados em memoria
        cert_manager = CertificateManager(pfx_data=content, password=password)

        # Carrega e valida
        if not cert_manager.load():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Falha ao carregar certificado. Verifique a senha."
            )

        # Valida certificado
        is_valid, validation_msg = cert_manager.validate()
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Certificado invalido: {validation_msg}"
            )

        # Obtem informacoes
        cert_info = cert_manager.get_info()

        # Armazena no store
        cert_alias = alias or cert_info.subject_cn
        cert_id = store.add(cert_alias, cert_manager)

        logger.info("Certificado carregado: %s (CPF/CNPJ: %s)", cert_info.subject_cn, cert_info.cpf_cnpj or "N/A")

        return CertificateUploadResponse(
            success=True,
            certificate_id=cert_id,
            subject=cert_info.subject_cn,
            issuer=cert_info.issuer_cn,
            cpf_cnpj=cert_info.cpf_cnpj,
            valid_from=cert_info.valid_from,
            valid_until=cert_info.valid_until,
            days_until_expiry=cert_info.days_until_expiry,
            type="A1",
            message=f"Certificado carregado com sucesso. Valido ate {cert_info.valid_until.date()}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro no upload do certificado: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar certificado: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=CertificateValidationResponse,
    summary="Valida Certificado A1",
    description="Valida um certificado digital sem armazena-lo",
    status_code=201,
)
async def validate_certificate(
    current_user: CurrentActiveUser,
    file: UploadFile = File(..., description="Arquivo .pfx ou .p12 do certificado"),
    password: str = Form(..., description="Senha do certificado"),
):
    """
    Valida um certificado digital A1 sem armazena-lo.

    Verifica:
    - Formato do arquivo
    - Senha correta
    - Validade temporal
    - Cadeia de certificacao
    """
    # Valida extensao
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome do arquivo nao informado")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pfx", "p12"]:
        return CertificateValidationResponse(
            is_valid=False,
            message="Formato invalido. Use .pfx ou .p12",
            subject=None,
            cpf_cnpj=None,
            valid_until=None,
            days_until_expiry=None,
            warnings=[],
        )

    try:
        content = await file.read()

        cert_manager = CertificateManager(pfx_data=content, password=password)

        if not cert_manager.load():
            return CertificateValidationResponse(
                is_valid=False,
                message="Falha ao carregar certificado. Senha incorreta ou arquivo corrompido.",
                subject=None,
                cpf_cnpj=None,
                valid_until=None,
                days_until_expiry=None,
                warnings=[],
            )

        is_valid, validation_msg = cert_manager.validate()
        cert_info = cert_manager.get_info()

        warnings = []
        if cert_info.days_until_expiry < 30:
            warnings.append(f"Certificado vence em {cert_info.days_until_expiry} dias")
        if cert_info.days_until_expiry < 7:
            warnings.append("URGENTE: Certificado proximo do vencimento!")

        return CertificateValidationResponse(
            is_valid=is_valid,
            message=validation_msg,
            subject=cert_info.subject_cn,
            cpf_cnpj=cert_info.cpf_cnpj,
            valid_until=cert_info.valid_until,
            days_until_expiry=cert_info.days_until_expiry,
            warnings=warnings,
        )

    except Exception as e:
        logger.error("Erro na validacao do certificado: %s", str(e))
        return CertificateValidationResponse(
            is_valid=False,
            message=f"Erro ao validar: {str(e)}",
            subject=None,
            cpf_cnpj=None,
            valid_until=None,
            days_until_expiry=None,
            warnings=[],
        )


@router.get(
    "/",
    response_model=CertificateListResponse,
    summary="Lista Certificados",
    description="Lista todos os certificados carregados no sistema",
)
async def list_certificates(current_user: CurrentActiveUser, store: CertificateStore = Depends(get_certificate_store)):
    """Lista todos os certificados carregados."""
    certificates = []

    for alias, cert_manager in store.list_all():
        cert_info = cert_manager.get_info()
        is_valid, _ = cert_manager.validate()

        status_str = "valid" if is_valid else "invalid"
        if cert_info.days_until_expiry < 0:
            status_str = "expired"
        elif cert_info.days_until_expiry < 30:
            status_str = "expiring_soon"

        certificates.append(
            CertificateInfoResponse(
                certificate_id=alias,
                subject_cn=cert_info.subject_cn,
                issuer_cn=cert_info.issuer_cn,
                cpf_cnpj=cert_info.cpf_cnpj,
                serial_number=cert_info.serial_number,
                valid_from=cert_info.valid_from,
                valid_until=cert_info.valid_until,
                days_until_expiry=cert_info.days_until_expiry,
                is_valid=is_valid,
                status=status_str,
                type="A1",
            )
        )

    return CertificateListResponse(total=len(certificates), certificates=certificates)


@router.get(
    "/{certificate_id}",
    response_model=CertificateInfoResponse,
    summary="Obtem Certificado",
    description="Obtem informacoes de um certificado especifico",
)
async def get_certificate(
    certificate_id: str, current_user: CurrentActiveUser, store: CertificateStore = Depends(get_certificate_store)
):
    """Obtem informacoes de um certificado especifico."""
    cert_manager = store.get(certificate_id)

    if not cert_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Certificado '{certificate_id}' nao encontrado"
        )

    cert_info = cert_manager.get_info()
    is_valid, _ = cert_manager.validate()

    status_str = "valid" if is_valid else "invalid"
    if cert_info.days_until_expiry < 0:
        status_str = "expired"
    elif cert_info.days_until_expiry < 30:
        status_str = "expiring_soon"

    return CertificateInfoResponse(
        certificate_id=certificate_id,
        subject_cn=cert_info.subject_cn,
        issuer_cn=cert_info.issuer_cn,
        cpf_cnpj=cert_info.cpf_cnpj,
        serial_number=cert_info.serial_number,
        valid_from=cert_info.valid_from,
        valid_until=cert_info.valid_until,
        days_until_expiry=cert_info.days_until_expiry,
        is_valid=is_valid,
        status=status_str,
        type="A1",
    )


@router.delete(
    "/{certificate_id}",
    response_model=CertificateDeleteResponse,
    summary="Remove Certificado",
    description="Remove um certificado do sistema",
)
async def delete_certificate(
    certificate_id: str, current_user: CurrentActiveUser, store: CertificateStore = Depends(get_certificate_store)
):
    """Remove um certificado do sistema."""
    if not store.get(certificate_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Certificado '{certificate_id}' nao encontrado"
        )

    store.remove(certificate_id)

    logger.info("Certificado removido: %s", certificate_id)

    return CertificateDeleteResponse(success=True, message=f"Certificado '{certificate_id}' removido com sucesso")


@router.get(
    "/{certificate_id}/public-key",
    summary="Obtem Chave Publica",
    description="Retorna a chave publica do certificado em formato PEM",
)
async def get_public_key(
    certificate_id: str, current_user: CurrentActiveUser, store: CertificateStore = Depends(get_certificate_store)
):
    """Retorna a chave publica do certificado."""
    cert_manager = store.get(certificate_id)

    if not cert_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Certificado '{certificate_id}' nao encontrado"
        )

    try:
        cert_base64 = cert_manager.get_certificate_base64()

        return {"certificate_id": certificate_id, "public_certificate": cert_base64, "format": "X509 DER Base64"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao extrair chave publica: {str(e)}"
        )


@router.post(
    "/{certificate_id}/test-sign",
    summary="Testa Assinatura",
    description="Testa a assinatura digital com o certificado",
    status_code=201,
)
async def test_signature(
    certificate_id: str,
    current_user: CurrentActiveUser,
    data: str = Form(..., description="Dados para assinar"),
    store: CertificateStore = Depends(get_certificate_store),
):
    """Testa a assinatura digital com o certificado."""
    cert_manager = store.get(certificate_id)

    if not cert_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Certificado '{certificate_id}' nao encontrado"
        )

    try:
        # Assina os dados
        signature = cert_manager.sign_data(data.encode("utf-8"))
        signature_b64 = base64.b64encode(signature).decode("utf-8")

        # Verifica assinatura
        is_valid = cert_manager.verify_signature(data.encode("utf-8"), signature)

        return {
            "certificate_id": certificate_id,
            "original_data": data,
            "signature": signature_b64,
            "signature_verified": is_valid,
            "algorithm": "RSA-SHA256",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao testar assinatura: {str(e)}"
        )


# Router para export
certificate_router = router
