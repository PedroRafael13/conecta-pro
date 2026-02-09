"""
Controller para integracao SEFAZ-AM (Amazonas).

Endpoints especificos para NF-e no estado do Amazonas:
- GET /sefaz-am/status - Status do servico
- GET /sefaz-am/nfe/{chave} - Consulta NF-e por chave
- GET /sefaz-am/cadastro/ie/{ie} - Consulta cadastro por IE
- GET /sefaz-am/cadastro/cnpj/{cnpj} - Consulta cadastro por CNPJ
- GET /sefaz-am/dfe - Consulta DF-e (notas destinadas)
- POST /sefaz-am/cancelar - Cancela NF-e
- POST /sefaz-am/carta-correcao - Registra carta de correcao
- POST /sefaz-am/inutilizar - Inutiliza numeracao
"""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db

logger = logging.getLogger(__name__)


def get_sefaz_service(db: Session = None):
    """
    Helper para inicializar SefazAMService com certificado.

    Args:
        db: Sessão do banco de dados (opcional)

    Returns:
        Tuple[SefazAMService, CertificateManager]: Service e gerenciador de certificado
    """
    from modules.government_integrations.core.certificate_manager import CertificateManager
    from modules.government_integrations.core.sefaz_am import SefazAMService

    cert_path = os.getenv("CERTIFICATE_PATH", "/opt/conecta-pro/credentials/certificates/certificado.pfx")
    cert_password = os.getenv("CERTIFICATE_PASSWORD", "")

    cert_manager = CertificateManager(pfx_path=cert_path, password=cert_password)
    service = SefazAMService(db_session=db, certificate_manager=cert_manager)

    return service, cert_manager


router = APIRouter(prefix="/sefaz-am", tags=["SEFAZ-AM (Amazonas)"])


# =========================================================================
# SCHEMAS
# =========================================================================


class StatusServicoResponse(BaseModel):
    """Resposta de status do servico."""

    disponivel: bool
    codigo: str
    mensagem: str
    tempo_resposta_ms: float
    ambiente: str
    data_consulta: str


class ConsultaNFeResponse(BaseModel):
    """Resposta de consulta NF-e."""

    sucesso: bool
    codigo: str
    mensagem: str
    chave_acesso: str | None = None
    protocolo: str | None = None
    data_autorizacao: str | None = None
    status_nota: str | None = None
    eventos: list[dict] = []


class CadastroContribuinteResponse(BaseModel):
    """Resposta de consulta cadastral."""

    sucesso: bool
    codigo: str
    mensagem: str
    contribuintes: list[dict] = []


class DFeResponse(BaseModel):
    """Resposta de consulta DF-e."""

    sucesso: bool
    codigo: str
    mensagem: str
    ultimo_nsu: str | None = None
    quantidade_documentos: int = 0
    documentos: list[dict] = []


class CancelamentoRequest(BaseModel):
    """Requisicao de cancelamento."""

    chave_acesso: str = Field(..., min_length=44, max_length=44)
    cnpj: str = Field(..., min_length=14, max_length=14)
    justificativa: str = Field(..., min_length=15, max_length=255)


class CartaCorrecaoRequest(BaseModel):
    """Requisicao de carta de correcao."""

    chave_acesso: str = Field(..., min_length=44, max_length=44)
    cnpj: str = Field(..., min_length=14, max_length=14)
    correcao: str = Field(..., min_length=15, max_length=1000)
    sequencia: int = Field(default=1, ge=1, le=20)


class InutilizacaoRequest(BaseModel):
    """Requisicao de inutilizacao."""

    cnpj: str = Field(..., min_length=14, max_length=14)
    serie: int = Field(..., ge=0, le=999)
    numero_inicial: int = Field(..., ge=1)
    numero_final: int = Field(..., ge=1)
    justificativa: str = Field(..., min_length=15, max_length=255)
    ano: int | None = None


class EventoResponse(BaseModel):
    """Resposta de evento."""

    sucesso: bool
    codigo: str
    mensagem: str
    protocolo: str | None = None
    data_registro: str | None = None


# =========================================================================
# ENDPOINTS
# =========================================================================


@router.get("/status", response_model=StatusServicoResponse)
async def consultar_status_servico(
    ambiente: str = Query("producao", enum=["producao", "homologacao"]),
    db: Session = Depends(get_db),
):
    """
    Consulta status do servico SEFAZ-AM.

    Verifica se o webservice NfeStatusServico4 esta operando.
    Deve ser chamado antes de transmissoes para verificar disponibilidade.
    """
    try:
        service, cert_manager = get_sefaz_service(db)

        resultado = await service.verificar_status()

        return StatusServicoResponse(
            disponivel=resultado["disponivel"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            tempo_resposta_ms=resultado.get("tempo_resposta_ms", 0),
            ambiente=ambiente,
            data_consulta=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Erro consultando status SEFAZ-AM: {e}")
        return StatusServicoResponse(
            disponivel=False,
            codigo="999",
            mensagem=str(e),
            tempo_resposta_ms=0,
            ambiente=ambiente,
            data_consulta=datetime.now().isoformat(),
        )


@router.get("/nfe/{chave_acesso}", response_model=ConsultaNFeResponse)
async def consultar_nfe(
    chave_acesso: str,
    db: Session = Depends(get_db),
):
    """
    Consulta NF-e por chave de acesso.

    Retorna dados do protocolo, status e eventos associados.
    Endpoint: NfeConsulta4
    """
    if len(chave_acesso) != 44:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chave de acesso deve ter 44 digitos",
        )

    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.consultar_nfe(chave_acesso)

        dados = resultado.get("dados", {})
        return ConsultaNFeResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            chave_acesso=dados.get("chave_acesso"),
            protocolo=dados.get("protocolo"),
            data_autorizacao=dados.get("data_autorizacao"),
            status_nota=dados.get("status_protocolo"),
            eventos=dados.get("eventos", []),
        )

    except Exception as e:
        logger.error(f"Erro consultando NF-e {chave_acesso}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar NF-e: {str(e)}",
        )


@router.get("/cadastro/ie/{inscricao_estadual}", response_model=CadastroContribuinteResponse)
async def consultar_cadastro_ie(
    inscricao_estadual: str,
    db: Session = Depends(get_db),
):
    """
    Consulta cadastro de contribuinte por Inscricao Estadual.

    Verifica status de inscricao estadual de clientes/fornecedores.
    Endpoint: CadConsultaCadastro4
    """
    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.consultar_cadastro_ie(inscricao_estadual)

        return CadastroContribuinteResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            contribuintes=resultado.get("contribuintes", []),
        )

    except Exception as e:
        logger.error(f"Erro consultando cadastro IE {inscricao_estadual}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar cadastro: {str(e)}",
        )


@router.get("/cadastro/cnpj/{cnpj}", response_model=CadastroContribuinteResponse)
async def consultar_cadastro_cnpj(
    cnpj: str,
    db: Session = Depends(get_db),
):
    """
    Consulta cadastro de contribuinte por CNPJ.

    Verifica status de inscricao estadual de clientes/fornecedores.
    Endpoint: CadConsultaCadastro4
    """
    if len(cnpj) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ deve ter 14 digitos",
        )

    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.consultar_cadastro_cnpj(cnpj)

        return CadastroContribuinteResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            contribuintes=resultado.get("contribuintes", []),
        )

    except Exception as e:
        logger.error(f"Erro consultando cadastro CNPJ {cnpj}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar cadastro: {str(e)}",
        )


@router.get("/dfe", response_model=DFeResponse)
async def consultar_dfe_destinadas(
    cnpj: str = Query(..., min_length=14, max_length=14, description="CNPJ do interessado"),
    ultimo_nsu: str = Query("0", description="Ultimo NSU recebido"),
    db: Session = Depends(get_db),
):
    """
    Consulta DF-e destinados ao CNPJ.

    Utiliza o servico nacional NFeDistribuicaoDFe para recuperar
    notas fiscais destinadas a empresa (compras).

    A consulta e paginada via NSU (Numero Sequencial Unico).
    """
    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.consultar_notas_destinadas(cnpj, ultimo_nsu)

        return DFeResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            ultimo_nsu=resultado.get("ultimo_nsu"),
            quantidade_documentos=len(resultado.get("documentos", [])),
            documentos=resultado.get("documentos", []),
        )

    except Exception as e:
        logger.error(f"Erro consultando DF-e CNPJ {cnpj}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar DF-e: {str(e)}",
        )


@router.post("/cancelar", response_model=EventoResponse)
async def cancelar_nfe(
    dados: CancelamentoRequest,
    db: Session = Depends(get_db),
):
    """
    Cancela uma NF-e autorizada.

    Envia evento de cancelamento via RecepcaoEvento4.
    Requer justificativa com minimo de 15 caracteres.
    """
    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.cancelar_nfe(
            chave_acesso=dados.chave_acesso,
            cnpj=dados.cnpj,
            justificativa=dados.justificativa,
        )

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["mensagem"],
            )

        return EventoResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            protocolo=resultado.get("protocolo"),
            data_registro=resultado.get("data_registro"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro cancelando NF-e {dados.chave_acesso}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar NF-e: {str(e)}",
        )


@router.post("/carta-correcao", response_model=EventoResponse)
async def registrar_carta_correcao(
    dados: CartaCorrecaoRequest,
    db: Session = Depends(get_db),
):
    """
    Registra Carta de Correcao (CC-e) para uma NF-e.

    Permite corrigir informacoes nao relacionadas a valores ou
    dados do destinatario. Maximo 20 cartas por nota.
    """
    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.carta_correcao(
            chave_acesso=dados.chave_acesso,
            cnpj=dados.cnpj,
            correcao=dados.correcao,
            sequencia=dados.sequencia,
        )

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["mensagem"],
            )

        return EventoResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            protocolo=resultado.get("protocolo"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro registrando CC-e {dados.chave_acesso}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar carta de correcao: {str(e)}",
        )


@router.post("/inutilizar", response_model=EventoResponse)
async def inutilizar_numeracao(
    dados: InutilizacaoRequest,
    db: Session = Depends(get_db),
):
    """
    Inutiliza faixa de numeracao de NF-e.

    Utilizado quando numeros de NF-e foram pulados por qualquer motivo
    e precisam ser inutilizados para manter a integridade da sequencia.
    """
    if dados.numero_final < dados.numero_inicial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero final deve ser maior ou igual ao inicial",
        )

    try:
        from modules.government_integrations.core.certificate_manager import CertificateManager
        from modules.government_integrations.core.sefaz_am import SefazAMService

        cert_manager = CertificateManager(db)
        service = SefazAMService(db, cert_manager)

        resultado = await service.inutilizar_numeracao(
            cnpj=dados.cnpj,
            serie=dados.serie,
            numero_inicial=dados.numero_inicial,
            numero_final=dados.numero_final,
            justificativa=dados.justificativa,
        )

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["mensagem"],
            )

        return EventoResponse(
            sucesso=resultado["sucesso"],
            codigo=resultado["codigo"],
            mensagem=resultado["mensagem"],
            protocolo=resultado.get("protocolo"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inutilizando numeracao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao inutilizar numeracao: {str(e)}",
        )
