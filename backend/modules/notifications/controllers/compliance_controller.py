"""
Controller para endpoints de compliance LGPD.

Implementa os direitos dos titulares conforme LGPD:
- Direito de acesso (Art. 15)
- Direito de portabilidade (Art. 18)
- Direito de exclusão (Art. 18)
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database.session import get_db
from modules.notifications.compliance.lgpd_manager import DataRequestType, LGPDComplianceManager
from modules.notifications.schemas.compliance_schemas import (
    DataExportResponse,
    DataRequestCreate,
    DataRequestResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/compliance",
    tags=["notifications-compliance"],
)


def get_lgpd_manager() -> LGPDComplianceManager:
    """Dependency para obter instância do LGPDComplianceManager."""
    return LGPDComplianceManager()


@router.get("/my-data", response_model=DataExportResponse)
async def export_my_data(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    lgpd_manager: LGPDComplianceManager = Depends(get_lgpd_manager),
) -> DataExportResponse:
    """
    Exporta todos os dados pessoais do usuário autenticado.

    **Direito de Acesso (LGPD Art. 15)**

    Retorna informações completas sobre:
    - Dados cadastrais
    - Preferências de notificação
    - Histórico de notificações
    - Dispositivos registrados
    - Dados de engajamento
    - Registros de consentimento

    **Rate Limiting:** 1 requisição por hora por usuário.
    **Retenção:** Dados exportados são válidos no momento da consulta.
    """
    try:
        user_id = current_user["user_id"]

        logger.info(f"Iniciando exportação de dados LGPD para usuário {user_id}")

        # Coleta todos os dados do usuário (inclui audit logging)
        user_data = await lgpd_manager.export_user_data(db, user_id, actor_id=user_id)

        await db.commit()

        logger.info(f"Exportação de dados LGPD concluída para usuário {user_id}")

        return DataExportResponse(
            success=True,
            message="Dados exportados com sucesso",
            data=user_data,
            export_format="json",
            export_date=user_data["export_date"],
        )

    except ValueError as e:
        logger.error(f"Usuário não encontrado na exportação LGPD: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    except Exception as e:
        logger.error(f"Erro na exportação de dados LGPD: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno na exportação de dados"
        )


@router.post("/data-request", response_model=DataRequestResponse)
async def create_data_request(
    request_data: DataRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    lgpd_manager: LGPDComplianceManager = Depends(get_lgpd_manager),
) -> DataRequestResponse:
    """
    Cria solicitação de dados LGPD.

    **Tipos suportados:**
    - `access`: Direito de acesso aos dados
    - `portability`: Direito de portabilidade
    - `deletion`: Direito de exclusão/esquecimento
    - `rectification`: Direito de correção
    - `restriction`: Direito de restrição do tratamento

    **Processamento:**
    - Solicitações são processadas conforme prazos legais
    - Usuário recebe notificações sobre o status
    - Dados são disponibilizados via API ou email
    """
    try:
        user_id = current_user["user_id"]

        logger.info(f"Criando solicitação LGPD tipo {request_data.request_type} para usuário {user_id}")

        # Cria a solicitação via LGPDManager
        request_result = await lgpd_manager.create_data_request(
            db=db,
            user_id=user_id,
            request_type=DataRequestType(request_data.request_type),
            description=request_data.description,
            requester_email=current_user.get("email"),
        )

        await db.commit()

        logger.info(f"Solicitação LGPD {request_result.id} criada com sucesso para usuário {user_id}")

        return DataRequestResponse(
            success=True,
            message="Solicitação criada com sucesso",
            request_id=str(request_result.id),
            request_type=request_data.request_type,
            status=request_result.status.value,
            estimated_completion=request_result.estimated_completion.isoformat()
            if request_result.estimated_completion
            else None,
        )

    except ValueError as e:
        logger.error(f"Erro de validação na solicitação LGPD: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na criação de solicitação LGPD: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno na criação da solicitação"
        )


@router.get("/data-request/{request_id}", response_model=DataRequestResponse)
async def get_data_request_status(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    lgpd_manager: LGPDComplianceManager = Depends(get_lgpd_manager),
) -> DataRequestResponse:
    """
    Consulta status de solicitação LGPD.

    **Status possíveis:**
    - `pending`: Solicitação recebida, aguardando processamento
    - `processing`: Em processamento
    - `completed`: Concluída, dados disponíveis
    - `rejected`: Rejeitada (com justificativa)
    - `cancelled`: Cancelada pelo usuário
    """
    try:
        user_id = current_user["user_id"]

        # Busca a solicitação (apenas do usuário autenticado)
        request_info = await lgpd_manager.get_data_request_status(db=db, request_id=request_id, user_id=user_id)

        if not request_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada")

        return DataRequestResponse(
            success=True,
            message="Status da solicitação",
            request_id=str(request_info.id),
            request_type=request_info.request_type.value,
            status=request_info.status.value,
            created_at=request_info.created_at.isoformat() if request_info.created_at else None,
            estimated_completion=request_info.estimated_completion.isoformat()
            if request_info.estimated_completion
            else None,
            completion_date=request_info.completion_date.isoformat() if request_info.completion_date else None,
            result_data=request_info.result_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na consulta de solicitação LGPD {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno na consulta da solicitação"
        )


@router.delete("/my-data")
async def delete_my_data(
    confirmation: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    lgpd_manager: LGPDComplianceManager = Depends(get_lgpd_manager),
) -> dict[str, Any]:
    """
    Exclui todos os dados pessoais do usuário.

    **Direito de Exclusão (LGPD Art. 18)**

    ⚠️ **AÇÃO IRREVERSÍVEL**

    **Dados excluídos:**
    - Histórico de notificações
    - Preferências de notificação
    - Dispositivos registrados
    - Dados de engajamento

    **Dados mantidos (base legal):**
    - Logs de auditoria (obrigação legal)
    - Dados financeiros/contratuais (se aplicável)

    **Confirmação obrigatória:** Enviar `confirmation="DELETE_MY_DATA"`
    """
    # Validação de confirmação
    if confirmation != "DELETE_MY_DATA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Confirmação inválida. Use: confirmation='DELETE_MY_DATA'"
        )

    try:
        user_id = current_user["user_id"]

        logger.warning(f"Iniciando exclusão de dados LGPD para usuário {user_id}")

        # Cria solicitação de exclusão
        delete_request = await lgpd_manager.create_data_request(
            db=db,
            user_id=user_id,
            request_type=DataRequestType.DELETION,
            description="Solicitação de exclusão de dados via API",
            requester_email=current_user.get("email"),
        )

        # Processa a exclusão imediatamente
        await lgpd_manager._delete_user_data(db, user_id)

        # Atualiza status da solicitação
        await lgpd_manager.complete_data_request(
            db=db,
            request_id=delete_request.id,
            result_data={"deleted": True, "deletion_date": delete_request.created_at.isoformat()},
        )

        await db.commit()

        logger.warning(f"Exclusão de dados LGPD concluída para usuário {user_id}")

        return {
            "success": True,
            "message": "Dados excluídos com sucesso",
            "deletion_date": delete_request.created_at.isoformat(),
            "request_id": str(delete_request.id),
            "note": "Alguns dados podem ser mantidos por obrigações legais",
        }

    except Exception as e:
        logger.error(f"Erro na exclusão de dados LGPD: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno na exclusão de dados"
        )


@router.get("/privacy-policy")
async def get_privacy_policy() -> dict[str, Any]:
    """
    Retorna informações sobre tratamento de dados.

    **Transparência (LGPD Art. 9)**

    Informa sobre:
    - Finalidades do tratamento
    - Base legal
    - Período de retenção
    - Direitos do titular
    - Contato do controlador/DPO
    """
    return {
        "privacy_policy": {
            "controller": {
                "name": "Conecta Mais",
                "contact": "dpo@conectamais.pro",
                "address": "São Paulo, SP, Brasil",
            },
            "data_processing": {
                "purposes": [
                    "Envio de notificações do sistema",
                    "Personalização da experiência do usuário",
                    "Análise de engajamento e melhorias do serviço",
                    "Cumprimento de obrigações contratuais",
                ],
                "legal_basis": [
                    "Consentimento do titular (Art. 7, I)",
                    "Execução de contrato (Art. 7, V)",
                    "Interesse legítimo (Art. 7, IX)",
                    "Cumprimento de obrigação legal (Art. 7, II)",
                ],
                "retention_period": "Dados mantidos enquanto a conta estiver ativa, ou conforme obrigações legais",
                "data_sharing": "Dados não são compartilhados com terceiros sem consentimento",
            },
            "data_subject_rights": {
                "access": "Direito de acesso aos seus dados via /api/v1/notifications/compliance/my-data",
                "rectification": "Direito de correção via configurações de conta",
                "deletion": "Direito de exclusão via /api/v1/notifications/compliance/my-data (DELETE)",
                "portability": "Direito de portabilidade via exportação de dados",
                "objection": "Direito de oposição via desativação de notificações",
                "restriction": "Direito de limitação via configurações de privacidade",
            },
            "contact": {
                "dpo_email": "dpo@conectamais.pro",
                "privacy_email": "privacidade@conectamais.pro",
                "complaints": "Para reclamações, contate a ANPD: https://www.gov.br/anpd",
            },
        },
        "last_updated": "2026-02-03",
        "version": "1.0",
    }
