"""Controller para modulo Fiscal - Endpoints de NF-e, NFS-e, SPED, Retencoes."""
# pylint: disable=too-many-lines,too-many-arguments,too-many-positional-arguments
# pylint: disable=unused-argument,fixme,logging-fstring-interpolation
# pylint: disable=raise-missing-from,redefined-outer-name,no-else-return

import logging
from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user, require_permission
from core.config.settings import settings
from core.database.session import get_db
from modules.financial.integrations.nfe_provider import (
    NFeError,
    create_nfe_provider,
)
from modules.financial.models.cfop_ncm import CFOPS_VIGILANCIA_ZFM
from modules.financial.models.fiscal_obligation import (
    SIMPLES_ANEXO_III_FAIXAS,
    calcular_das_anexo_iii,
)
from modules.financial.repositories.fiscal_repository import FiscalRepository
from modules.financial.schemas.fiscal_schemas import (
    CalculoRetencaoRequest,
    CalculoRetencaoResponse,
    CFOPCreate,
    CFOPListResponse,
    CFOPResponse,
    CFOPUpdate,
    DASCalcularRequest,
    DASCalcularResponse,
    FiscalDashboard,
    FiscalStats,
    NCMCreate,
    NCMListResponse,
    NCMResponse,
    NCMUpdate,
    NFeCancelarRequest,
    NFeCreate,
    NFeEmitirRequest,
    NFeEmitirResponse,
    NFeInutilizarRequest,
    NFeListResponse,
    NFeResponse,
    NFeUpdate,
    NFSeCancelarRequest,
    NFSeCreate,
    NFSeEmitirRequest,
    NFSeEmitirResponse,
    NFSeListResponse,
    NFSeResponse,
    NFSeUpdate,
    ObrigacaoFiscalCreate,
    ObrigacaoFiscalListResponse,
    ObrigacaoFiscalResponse,
    ObrigacaoFiscalUpdate,
    RetencaoFederalCreate,
    RetencaoFederalListResponse,
    RetencaoFederalResponse,
    RetencaoFederalUpdate,
    SimplesNacionalDASCreate,
    SimplesNacionalDASResponse,
    SPEDFileCreate,
    SPEDFileListResponse,
    SPEDFileResponse,
    SPEDGerarRequest,
    SPEDTransmitirRequest,
    SUFRAMAConfigCreate,
    SUFRAMAConfigResponse,
    SUFRAMAOperacaoCreate,
    SUFRAMAOperacaoListResponse,
    SUFRAMAOperacaoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fiscal", tags=["Fiscal"])


def get_repository(db: AsyncSession = Depends(get_db)) -> FiscalRepository:
    """Retorna instancia do repository fiscal."""
    return FiscalRepository(db)


# ============================================================
# CFOP Endpoints
# ============================================================


@router.post("/cfop", response_model=CFOPResponse, status_code=status.HTTP_201_CREATED)
async def criar_cfop(
    data: CFOPCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:cfop:create")),
) -> CFOPResponse:
    """Cria um novo CFOP."""
    try:
        cfop = await repo.create_cfop(data.model_dump())
        logger.info(f"CFOP {cfop.codigo} criado por {current_user['email']}")
        return CFOPResponse.model_validate(cfop)
    except Exception as e:
        logger.error(f"Erro ao criar CFOP: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar CFOP")


@router.get("/cfop", response_model=CFOPListResponse)
async def listar_cfops(
    tipo: str | None = Query(None, description="entrada ou saida"),
    grupo: str | None = Query(None, description="1,2,3,5,6,7"),
    natureza: str | None = None,
    zfm_aplicavel: bool | None = None,
    active: bool = True,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> CFOPListResponse:
    """Lista CFOPs com filtros."""
    cfops, total = await repo.list_cfops(
        tipo=tipo,
        grupo=grupo,
        natureza=natureza,
        zfm_aplicavel=zfm_aplicavel,
        active=active,
        search=search,
        page=page,
        page_size=page_size,
    )
    return CFOPListResponse(
        items=[CFOPResponse.model_validate(c) for c in cfops],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/cfop/vigilancia-zfm", response_model=dict[str, str])
async def listar_cfops_vigilancia_zfm(
    current_user: dict = Depends(get_current_user),
) -> dict[str, str]:
    """Lista CFOPs comuns para servicos de vigilancia em ZFM."""
    return CFOPS_VIGILANCIA_ZFM


@router.get("/cfop/{cfop_id}", response_model=CFOPResponse)
async def obter_cfop(
    cfop_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> CFOPResponse:
    """Busca CFOP por ID."""
    cfop = await repo.get_cfop_by_id(cfop_id)
    if not cfop:
        raise HTTPException(status_code=404, detail="CFOP nao encontrado")
    return CFOPResponse.model_validate(cfop)


@router.get("/cfop/codigo/{codigo}", response_model=CFOPResponse)
async def obter_cfop_por_codigo(
    codigo: str,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> CFOPResponse:
    """Busca CFOP por codigo."""
    cfop = await repo.get_cfop_by_codigo(codigo)
    if not cfop:
        raise HTTPException(status_code=404, detail="CFOP nao encontrado")
    return CFOPResponse.model_validate(cfop)


@router.patch("/cfop/{cfop_id}", response_model=CFOPResponse)
async def atualizar_cfop(
    cfop_id: UUID,
    data: CFOPUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:cfop:update")),
) -> CFOPResponse:
    """Atualiza CFOP."""
    cfop = await repo.update_cfop(cfop_id, data.model_dump(exclude_unset=True))
    if not cfop:
        raise HTTPException(status_code=404, detail="CFOP nao encontrado")
    return CFOPResponse.model_validate(cfop)


# ============================================================
# NCM Endpoints
# ============================================================


@router.post("/ncm", response_model=NCMResponse, status_code=status.HTTP_201_CREATED)
async def criar_ncm(
    data: NCMCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:ncm:create")),
) -> NCMResponse:
    """Cria um novo NCM."""
    try:
        ncm = await repo.create_ncm(data.model_dump())
        logger.info(f"NCM {ncm.codigo} criado por {current_user['email']}")
        return NCMResponse.model_validate(ncm)
    except Exception as e:
        logger.error(f"Erro ao criar NCM: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar NCM")


@router.get("/ncm", response_model=NCMListResponse)
async def listar_ncms(
    capitulo: str | None = None,
    posicao: str | None = None,
    tributacao_monofasica: bool | None = None,
    zfm_isento_ipi: bool | None = None,
    active: bool = True,
    vigente: bool = True,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NCMListResponse:
    """Lista NCMs com filtros."""
    ncms, total = await repo.list_ncms(
        capitulo=capitulo,
        posicao=posicao,
        tributacao_monofasica=tributacao_monofasica,
        zfm_isento_ipi=zfm_isento_ipi,
        active=active,
        vigente=vigente,
        search=search,
        page=page,
        page_size=page_size,
    )
    return NCMListResponse(
        items=[NCMResponse.model_validate(n) for n in ncms],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/ncm/{ncm_id}", response_model=NCMResponse)
async def obter_ncm(
    ncm_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NCMResponse:
    """Busca NCM por ID."""
    ncm = await repo.get_ncm_by_id(ncm_id)
    if not ncm:
        raise HTTPException(status_code=404, detail="NCM nao encontrado")
    return NCMResponse.model_validate(ncm)


@router.get("/ncm/codigo/{codigo}", response_model=NCMResponse)
async def obter_ncm_por_codigo(
    codigo: str,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NCMResponse:
    """Busca NCM por codigo."""
    ncm = await repo.get_ncm_by_codigo(codigo)
    if not ncm:
        raise HTTPException(status_code=404, detail="NCM nao encontrado")
    return NCMResponse.model_validate(ncm)


@router.patch("/ncm/{ncm_id}", response_model=NCMResponse)
async def atualizar_ncm(
    ncm_id: UUID,
    data: NCMUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:ncm:update")),
) -> NCMResponse:
    """Atualiza NCM."""
    ncm = await repo.update_ncm(ncm_id, data.model_dump(exclude_unset=True))
    if not ncm:
        raise HTTPException(status_code=404, detail="NCM nao encontrado")
    return NCMResponse.model_validate(ncm)


# ============================================================
# Retencao Federal Endpoints
# ============================================================


@router.post(
    "/retencao",
    response_model=RetencaoFederalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_retencao(
    data: RetencaoFederalCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:retencao:create")),
) -> RetencaoFederalResponse:
    """Cria configuracao de retencao federal."""
    try:
        retencao = await repo.create_retencao(
            data.condominio_id,
            data.model_dump(exclude={"condominio_id"}),
        )
        logger.info(f"Retencao {retencao.nome} criada por {current_user['email']}")
        return RetencaoFederalResponse.model_validate(retencao)
    except Exception as e:
        logger.error(f"Erro ao criar retencao: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar retencao")


@router.get("/retencao", response_model=RetencaoFederalListResponse)
async def listar_retencoes(
    condominio_id: UUID,
    servico_vigilancia: bool | None = None,
    active: bool = True,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> RetencaoFederalListResponse:
    """Lista configuracoes de retencao."""
    retencoes = await repo.list_retencoes(
        condominio_id=condominio_id,
        servico_vigilancia=servico_vigilancia,
        active=active,
    )
    return RetencaoFederalListResponse(
        items=[RetencaoFederalResponse.model_validate(r) for r in retencoes],
        total=len(retencoes),
    )


@router.get("/retencao/{retencao_id}", response_model=RetencaoFederalResponse)
async def obter_retencao(
    retencao_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> RetencaoFederalResponse:
    """Busca configuracao de retencao por ID."""
    retencao = await repo.get_retencao_by_id(retencao_id)
    if not retencao:
        raise HTTPException(status_code=404, detail="Retencao nao encontrada")
    return RetencaoFederalResponse.model_validate(retencao)


@router.patch("/retencao/{retencao_id}", response_model=RetencaoFederalResponse)
async def atualizar_retencao(
    retencao_id: UUID,
    data: RetencaoFederalUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:retencao:update")),
) -> RetencaoFederalResponse:
    """Atualiza configuracao de retencao."""
    retencao = await repo.update_retencao(retencao_id, data.model_dump(exclude_unset=True))
    if not retencao:
        raise HTTPException(status_code=404, detail="Retencao nao encontrada")
    return RetencaoFederalResponse.model_validate(retencao)


@router.post("/retencao/calcular", response_model=CalculoRetencaoResponse)
async def calcular_retencoes(
    data: CalculoRetencaoRequest,
    condominio_id: UUID = Query(...),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> CalculoRetencaoResponse:
    """Calcula retencoes federais para um valor de servico.

    Considera:
    - INSS: 11% (pode ter liminar que exime)
    - IR: 1.5% (base minima R$ 666,66)
    - PCC: PIS 0.65% + COFINS 3% + CSLL 1% = 4.65% (base minima R$ 215,05)
    - ISS: conforme aliquota municipal

    Para servicos de vigilancia do Simples Nacional Anexo III,
    se houver liminar ativa e o cliente aceitar, INSS = 0.
    """
    # Busca configuracao
    if data.retencao_id:
        retencao = await repo.get_retencao_by_id(data.retencao_id)
    else:
        retencao = await repo.get_retencao_padrao_vigilancia(condominio_id)

    if not retencao:
        raise HTTPException(
            status_code=404,
            detail="Configuracao de retencao nao encontrada",
        )

    # Calcula
    resultado = retencao.calcular_retencoes(
        data.valor_servico,
        data.cliente_aceita_liminar,
    )

    return CalculoRetencaoResponse(
        valor_servico=resultado["valor_servico"],
        inss=resultado["inss"],
        ir=resultado["ir"],
        csll=resultado["csll"],
        pis=resultado["pis"],
        cofins=resultado["cofins"],
        iss=resultado["iss"],
        total=resultado["total"],
        valor_liquido=resultado["valor_liquido"],
        liminar_aplicada=resultado["liminar_aplicada"],
        liminar_numero=resultado.get("liminar_numero"),
        detalhamento={
            "inss_aliquota": float(retencao.inss_aliquota),
            "ir_aliquota": float(retencao.ir_aliquota),
            "pcc_aliquota": float(retencao.aliquota_pcc),
            "liminar_ativa": retencao.inss_liminar_ativa,
            "anexo": "III",
            "observacao": (
                "CPP ja incluso no DAS do Simples Nacional. Retencao de INSS caracteriza bitributacao."
                if retencao.inss_liminar_ativa
                else None
            ),
        },
    )


# ============================================================
# NF-e Endpoints
# ============================================================


@router.post("/nfe", response_model=NFeResponse, status_code=status.HTTP_201_CREATED)
async def criar_nfe(
    data: NFeCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfe:create")),
) -> NFeResponse:
    """Cria uma nova NF-e."""
    try:
        # Gera numero se nao informado
        if not data.numero:
            data.numero = await repo.get_proximo_numero_nfe(data.condominio_id, data.serie)

        nfe = await repo.create_nfe(
            data.condominio_id,
            data.model_dump(exclude={"condominio_id", "itens"}),
            [item.model_dump() for item in data.itens],
        )
        logger.info(f"NF-e {nfe.numero} criada por {current_user['email']}")
        return NFeResponse.model_validate(nfe)
    except Exception as e:
        logger.error(f"Erro ao criar NF-e: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar NF-e: {e}")


@router.get("/nfe", response_model=NFeListResponse)
async def listar_nfes(  # pylint: disable=too-many-locals
    condominio_id: UUID,
    tipo: str | None = None,
    status: str | None = None,
    serie: int | None = None,
    numero_inicial: int | None = None,
    numero_final: int | None = None,
    data_inicial: date | None = None,
    data_final: date | None = None,
    destinatario_cpf_cnpj: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NFeListResponse:
    """Lista NF-es com filtros."""
    nfes, total = await repo.list_nfes(
        condominio_id=condominio_id,
        tipo=tipo,
        status=status,
        serie=serie,
        numero_inicial=numero_inicial,
        numero_final=numero_final,
        data_inicial=data_inicial,
        data_final=data_final,
        destinatario_cpf_cnpj=destinatario_cpf_cnpj,
        search=search,
        page=page,
        page_size=page_size,
    )
    return NFeListResponse(
        items=[NFeResponse.model_validate(n) for n in nfes],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/nfe/{nfe_id}", response_model=NFeResponse)
async def obter_nfe(
    nfe_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NFeResponse:
    """Busca NF-e por ID."""
    nfe = await repo.get_nfe_by_id(nfe_id)
    if not nfe:
        raise HTTPException(status_code=404, detail="NF-e nao encontrada")
    return NFeResponse.model_validate(nfe)


@router.get("/nfe/chave/{chave_acesso}", response_model=NFeResponse)
async def obter_nfe_por_chave(
    chave_acesso: str,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NFeResponse:
    """Busca NF-e por chave de acesso."""
    nfe = await repo.get_nfe_by_chave(chave_acesso)
    if not nfe:
        raise HTTPException(status_code=404, detail="NF-e nao encontrada")
    return NFeResponse.model_validate(nfe)


@router.patch("/nfe/{nfe_id}", response_model=NFeResponse)
async def atualizar_nfe(
    nfe_id: UUID,
    data: NFeUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfe:update")),
) -> NFeResponse:
    """Atualiza NF-e (apenas rascunho)."""
    nfe = await repo.get_nfe_by_id(nfe_id)
    if not nfe:
        raise HTTPException(status_code=404, detail="NF-e nao encontrada")
    if nfe.status != "rascunho":
        raise HTTPException(
            status_code=400,
            detail="Apenas NF-e em rascunho pode ser editada",
        )

    nfe = await repo.update_nfe(nfe_id, data.model_dump(exclude_unset=True))
    return NFeResponse.model_validate(nfe)


@router.post("/nfe/emitir", response_model=NFeEmitirResponse)
async def emitir_nfe(
    data: NFeEmitirRequest,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfe:emitir")),
) -> NFeEmitirResponse:
    """Emite NF-e para a SEFAZ.

    TODO: Integrar com biblioteca de NF-e (pynfe, brazilfiscal, etc)
    """
    nfe = await repo.get_nfe_by_id(data.nfe_id)
    if not nfe:
        raise HTTPException(status_code=404, detail="NF-e nao encontrada")
    if nfe.status not in ["rascunho", "rejeitada"]:
        raise HTTPException(
            status_code=400,
            detail=f"NF-e em status {nfe.status} nao pode ser emitida",
        )

    # Integração real com SEFAZ via NFeProvider
    try:
        # Criar provedor NF-e com configurações do ambiente
        nfe_provider = create_nfe_provider(
            certificado_path=settings.NFE_CERT_PATH,
            certificado_senha=settings.NFE_CERT_PASSWORD,
            ambiente=data.ambiente,  # Usar ambiente da requisição (1=prod, 2=homolog)
            uf=settings.NFE_UF,
        )

        # Preparar dados da NF-e para emissão
        nfe_data = {
            "destinatario": nfe.dados_destinatario if hasattr(nfe, "dados_destinatario") else {},
            "items": nfe.items if hasattr(nfe, "items") else [],
            "dados_adicionais": nfe.dados_adicionais if hasattr(nfe, "dados_adicionais") else {},
        }

        # Emitir NF-e na SEFAZ
        resultado = await nfe_provider.emitir_nfe(nfe_data=nfe_data, nfe_id=data.nfe_id, numero=nfe.numero)

        # Atualizar NF-e no banco com resultado da SEFAZ
        await repo.update_nfe(
            data.nfe_id,
            {
                "status": resultado["status"],
                "chave_acesso": resultado["chave_acesso"],
                "protocolo": resultado.get("protocolo"),
                "xml_autorizado": resultado.get("xml_autorizado"),
                "data_emissao": datetime.now(),
            },
        )

        logger.info(
            f"NF-e {nfe.numero} emitida com sucesso - "
            f"Status: {resultado['status']} - "
            f"Chave: {resultado['chave_acesso'][:16]}..."
        )

        return NFeEmitirResponse(
            nfe_id=data.nfe_id,
            status=resultado["status"],
            chave_acesso=resultado["chave_acesso"],
            protocolo=resultado.get("protocolo"),
            mensagem=resultado["mensagem"],
            xml_autorizado=resultado.get("xml_autorizado"),
            pdf_danfe=resultado.get("pdf_danfe"),
        )

    except NFeError as nfe_error:
        logger.error(f"Erro NF-e {nfe.numero}: {nfe_error.message}")
        # Atualizar status para rejeitada em caso de erro
        await repo.update_nfe(
            data.nfe_id, {"status": "rejeitada", "erro_sefaz": nfe_error.message, "codigo_erro": nfe_error.code}
        )
        raise HTTPException(status_code=400, detail=f"Erro na emissão NF-e: {nfe_error.message}")
    except Exception as e:
        logger.error(f"Erro inesperado na emissão NF-e {nfe.numero}: {str(e)}")
        await repo.update_nfe(data.nfe_id, {"status": "rejeitada", "erro_sefaz": f"Erro interno: {str(e)}"})
        raise HTTPException(status_code=500, detail="Erro interno na emissão da NF-e")


@router.post("/nfe/cancelar")
async def cancelar_nfe(
    data: NFeCancelarRequest,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfe:cancelar")),
) -> dict[str, Any]:
    """Cancela NF-e autorizada."""
    nfe = await repo.get_nfe_by_id(data.nfe_id)
    if not nfe:
        raise HTTPException(status_code=404, detail="NF-e nao encontrada")
    if nfe.status != "autorizada":
        raise HTTPException(
            status_code=400,
            detail="Apenas NF-e autorizada pode ser cancelada",
        )

    # Cancelamento real na SEFAZ via NFeProvider
    try:
        # Criar provedor NF-e
        nfe_provider = create_nfe_provider(
            certificado_path=settings.NFE_CERT_PATH,
            certificado_senha=settings.NFE_CERT_PASSWORD,
            ambiente=settings.NFE_AMBIENTE,
            uf=settings.NFE_UF,
        )

        # Verificar se NF-e tem chave de acesso
        if not nfe.chave_acesso:
            raise HTTPException(status_code=400, detail="NF-e não possui chave de acesso para cancelamento")

        # Cancelar na SEFAZ
        resultado = await nfe_provider.cancelar_nfe(
            chave_acesso=nfe.chave_acesso, motivo=data.justificativa, nfe_id=data.nfe_id
        )

        # Atualizar no banco
        await repo.update_nfe(
            data.nfe_id,
            {
                "status": resultado["status"],
                "protocolo_cancelamento": resultado.get("protocolo"),
                "data_cancelamento": datetime.now(),
                "motivo_cancelamento": data.justificativa,
            },
        )

        logger.info(
            f"NF-e {nfe.numero} cancelada com sucesso - "
            f"Chave: {nfe.chave_acesso[:16]}... - "
            f"Motivo: {data.justificativa}"
        )

        return {
            "message": resultado["mensagem"],
            "nfe_id": str(data.nfe_id),
            "status": resultado["status"],
            "protocolo": resultado.get("protocolo"),
            "data_cancelamento": resultado["data_cancelamento"],
        }

    except NFeError as nfe_error:
        logger.error(f"Erro cancelamento NF-e {nfe.numero}: {nfe_error.message}")
        raise HTTPException(status_code=400, detail=f"Erro no cancelamento: {nfe_error.message}")
    except Exception as e:
        logger.error(f"Erro inesperado no cancelamento NF-e {nfe.numero}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no cancelamento da NF-e")


@router.post("/nfe/inutilizar")
async def inutilizar_numeracao(
    data: NFeInutilizarRequest,
    condominio_id: UUID = Query(...),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfe:inutilizar")),
) -> dict[str, Any]:
    """Inutiliza faixa de numeracao de NF-e."""
    # TODO: Implementar inutilizacao na SEFAZ
    logger.info(
        f"Inutilizando NF-e serie {data.serie} numeros "
        f"{data.numero_inicial} a {data.numero_final}: {data.justificativa}"
    )

    return {
        "message": "Numeracao inutilizada com sucesso",
        "serie": data.serie,
        "numero_inicial": data.numero_inicial,
        "numero_final": data.numero_final,
    }


# ============================================================
# NFS-e Endpoints
# ============================================================


@router.post("/nfse", response_model=NFSeResponse, status_code=status.HTTP_201_CREATED)
async def criar_nfse(
    data: NFSeCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfse:create")),
) -> NFSeResponse:
    """Cria uma nova NFS-e."""
    try:
        # Gera numero RPS se nao informado
        if not data.numero_rps:
            data.numero_rps = await repo.get_proximo_numero_rps(data.condominio_id, data.serie_rps)

        nfse = await repo.create_nfse(
            data.condominio_id,
            data.model_dump(exclude={"condominio_id"}),
        )
        logger.info(f"NFS-e RPS {nfse.numero_rps} criada por {current_user['email']}")
        return NFSeResponse.model_validate(nfse)
    except Exception as e:
        logger.error(f"Erro ao criar NFS-e: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar NFS-e: {e}")


@router.get("/nfse", response_model=NFSeListResponse)
async def listar_nfses(
    condominio_id: UUID,
    status: str | None = None,
    data_inicial: date | None = None,
    data_final: date | None = None,
    competencia_mes: int | None = None,
    competencia_ano: int | None = None,
    tomador_cpf_cnpj: str | None = None,
    codigo_servico: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NFSeListResponse:
    """Lista NFS-es com filtros."""
    nfses, total = await repo.list_nfses(
        condominio_id=condominio_id,
        status=status,
        data_inicial=data_inicial,
        data_final=data_final,
        competencia_mes=competencia_mes,
        competencia_ano=competencia_ano,
        tomador_cpf_cnpj=tomador_cpf_cnpj,
        codigo_servico=codigo_servico,
        search=search,
        page=page,
        page_size=page_size,
    )
    return NFSeListResponse(
        items=[NFSeResponse.model_validate(n) for n in nfses],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/nfse/{nfse_id}", response_model=NFSeResponse)
async def obter_nfse(
    nfse_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> NFSeResponse:
    """Busca NFS-e por ID."""
    nfse = await repo.get_nfse_by_id(nfse_id)
    if not nfse:
        raise HTTPException(status_code=404, detail="NFS-e nao encontrada")
    return NFSeResponse.model_validate(nfse)


@router.patch("/nfse/{nfse_id}", response_model=NFSeResponse)
async def atualizar_nfse(
    nfse_id: UUID,
    data: NFSeUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfse:update")),
) -> NFSeResponse:
    """Atualiza NFS-e (apenas rascunho)."""
    nfse = await repo.get_nfse_by_id(nfse_id)
    if not nfse:
        raise HTTPException(status_code=404, detail="NFS-e nao encontrada")
    if nfse.status != "rascunho":
        raise HTTPException(
            status_code=400,
            detail="Apenas NFS-e em rascunho pode ser editada",
        )

    nfse = await repo.update_nfse(nfse_id, data.model_dump(exclude_unset=True))
    return NFSeResponse.model_validate(nfse)


@router.post("/nfse/emitir", response_model=NFSeEmitirResponse)
async def emitir_nfse(
    data: NFSeEmitirRequest,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfse:emitir")),
) -> NFSeEmitirResponse:
    """Emite NFS-e para a prefeitura.

    TODO: Integrar com webservice da prefeitura de Manaus (ABRASF 2.0)
    """
    nfse = await repo.get_nfse_by_id(data.nfse_id)
    if not nfse:
        raise HTTPException(status_code=404, detail="NFS-e nao encontrada")
    if nfse.status not in ["rascunho", "rejeitada"]:
        raise HTTPException(
            status_code=400,
            detail=f"NFS-e em status {nfse.status} nao pode ser emitida",
        )

    # TODO: Implementar integracao com prefeitura
    logger.info(f"Emitindo NFS-e RPS {nfse.numero_rps} - ambiente {data.ambiente}")

    await repo.update_nfse(data.nfse_id, {"status": "enviando"})

    return NFSeEmitirResponse(
        nfse_id=data.nfse_id,
        status="enviando",
        numero_nfse=None,
        codigo_verificacao=None,
        link_nfse=None,
        protocolo=None,
        mensagem="NFS-e enviada para processamento",
        xml=None,
        pdf=None,
    )


@router.post("/nfse/cancelar")
async def cancelar_nfse(
    data: NFSeCancelarRequest,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:nfse:cancelar")),
) -> dict[str, Any]:
    """Cancela NFS-e autorizada."""
    nfse = await repo.get_nfse_by_id(data.nfse_id)
    if not nfse:
        raise HTTPException(status_code=404, detail="NFS-e nao encontrada")
    if nfse.status != "autorizada":
        raise HTTPException(
            status_code=400,
            detail="Apenas NFS-e autorizada pode ser cancelada",
        )

    # TODO: Implementar cancelamento na prefeitura
    logger.info(f"Cancelando NFS-e {nfse.numero_nfse}: {data.codigo_cancelamento}")

    await repo.update_nfse(data.nfse_id, {"status": "cancelada"})

    return {"message": "NFS-e cancelada com sucesso", "nfse_id": str(data.nfse_id)}


@router.get("/nfse/retencoes/competencia")
async def obter_retencoes_competencia(
    condominio_id: UUID,
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2000),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Retorna total de retencoes de uma competencia.

    Util para conferencia de DAS e relatorios fiscais.
    Inclui economia com liminar de INSS.
    """
    retencoes = await repo.calcular_total_retencoes_competencia(condominio_id, mes, ano)
    return {
        "competencia": f"{mes:02d}/{ano}",
        **{k: float(v) for k, v in retencoes.items()},
    }


# ============================================================
# SPED Endpoints
# ============================================================


@router.post("/sped", response_model=SPEDFileResponse, status_code=status.HTTP_201_CREATED)
async def criar_sped(
    data: SPEDFileCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:sped:create")),
) -> SPEDFileResponse:
    """Cria arquivo SPED."""
    try:
        sped = await repo.create_sped_file(
            data.condominio_id,
            data.model_dump(exclude={"condominio_id"}),
        )
        logger.info(f"SPED {sped.tipo} criado por {current_user['email']}")
        return SPEDFileResponse.model_validate(sped)
    except Exception as e:
        logger.error(f"Erro ao criar SPED: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar SPED")


@router.get("/sped", response_model=SPEDFileListResponse)
async def listar_speds(
    condominio_id: UUID,
    tipo: str | None = None,
    status: str | None = None,
    ano: int | None = None,
    mes: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> SPEDFileListResponse:
    """Lista arquivos SPED."""
    speds, total = await repo.list_sped_files(
        condominio_id=condominio_id,
        tipo=tipo,
        status=status,
        ano=ano,
        mes=mes,
        page=page,
        page_size=page_size,
    )
    return SPEDFileListResponse(
        items=[SPEDFileResponse.model_validate(s) for s in speds],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sped/{sped_id}", response_model=SPEDFileResponse)
async def obter_sped(
    sped_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> SPEDFileResponse:
    """Busca arquivo SPED por ID."""
    sped = await repo.get_sped_file_by_id(sped_id)
    if not sped:
        raise HTTPException(status_code=404, detail="SPED nao encontrado")
    return SPEDFileResponse.model_validate(sped)


@router.post("/sped/gerar")
async def gerar_sped(
    data: SPEDGerarRequest,
    condominio_id: UUID = Query(...),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:sped:gerar")),
) -> dict[str, Any]:
    """Gera arquivo SPED.

    TODO: Implementar geracao de arquivos SPED
    """
    logger.info(f"Gerando SPED {data.tipo} para {data.ano}/{data.mes or 'anual'}")

    # Cria registro
    sped = await repo.create_sped_file(
        condominio_id,
        {
            "tipo": data.tipo,
            "ano": data.ano,
            "mes": data.mes,
            "finalidade": data.finalidade,
            "status": "gerando",
        },
    )

    # TODO: Implementar geracao assincrona

    return {
        "message": "Geracao de SPED iniciada",
        "sped_id": str(sped.id),
        "tipo": data.tipo,
    }


@router.post("/sped/{sped_id}/validar")
async def validar_sped(
    sped_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:sped:validar")),
) -> dict[str, Any]:
    """Valida arquivo SPED."""
    sped = await repo.get_sped_file_by_id(sped_id)
    if not sped:
        raise HTTPException(status_code=404, detail="SPED nao encontrado")

    # TODO: Implementar validacao com PVA
    logger.info(f"Validando SPED {sped.id}")

    await repo.update_sped_file(sped_id, {"status": "validando"})

    return {"message": "Validacao iniciada", "sped_id": str(sped_id)}


@router.post("/sped/{sped_id}/transmitir")
async def transmitir_sped(
    sped_id: UUID,
    data: SPEDTransmitirRequest,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:sped:transmitir")),
) -> dict[str, Any]:
    """Transmite arquivo SPED."""
    sped = await repo.get_sped_file_by_id(sped_id)
    if not sped:
        raise HTTPException(status_code=404, detail="SPED nao encontrado")
    if sped.status not in ["validado", "assinado"]:
        raise HTTPException(
            status_code=400,
            detail="SPED precisa estar validado/assinado para transmitir",
        )

    # TODO: Implementar transmissao
    logger.info(f"Transmitindo SPED {sped.id} - ambiente {data.ambiente}")

    await repo.update_sped_file(sped_id, {"status": "transmitindo"})

    return {"message": "Transmissao iniciada", "sped_id": str(sped_id)}


# ============================================================
# Obrigacao Fiscal Endpoints
# ============================================================


@router.post(
    "/obrigacao",
    response_model=ObrigacaoFiscalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_obrigacao(
    data: ObrigacaoFiscalCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:obrigacao:create")),
) -> ObrigacaoFiscalResponse:
    """Cria obrigacao fiscal."""
    obrigacao = await repo.create_obrigacao(
        data.condominio_id,
        data.model_dump(exclude={"condominio_id"}),
    )
    return ObrigacaoFiscalResponse.model_validate(obrigacao)


@router.get("/obrigacao", response_model=ObrigacaoFiscalListResponse)
async def listar_obrigacoes(
    condominio_id: UUID,
    tipo: str | None = None,
    status: str | None = None,
    mes: int | None = None,
    ano: int | None = None,
    vencimento_inicio: date | None = None,
    vencimento_fim: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ObrigacaoFiscalListResponse:
    """Lista obrigacoes fiscais."""
    obrigacoes, total = await repo.list_obrigacoes(
        condominio_id=condominio_id,
        tipo=tipo,
        status=status,
        mes=mes,
        ano=ano,
        vencimento_inicio=vencimento_inicio,
        vencimento_fim=vencimento_fim,
        page=page,
        page_size=page_size,
    )

    pendentes = await repo.get_obrigacoes_pendentes(condominio_id)
    atrasadas = await repo.get_obrigacoes_atrasadas(condominio_id)

    return ObrigacaoFiscalListResponse(
        items=[ObrigacaoFiscalResponse.model_validate(o) for o in obrigacoes],
        total=total,
        proximas_a_vencer=len(pendentes),
        atrasadas=len(atrasadas),
    )


@router.get("/obrigacao/pendentes")
async def listar_obrigacoes_pendentes(
    condominio_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> list[ObrigacaoFiscalResponse]:
    """Lista obrigacoes pendentes ordenadas por vencimento."""
    obrigacoes = await repo.get_obrigacoes_pendentes(condominio_id)
    return [ObrigacaoFiscalResponse.model_validate(o) for o in obrigacoes]


@router.get("/obrigacao/atrasadas")
async def listar_obrigacoes_atrasadas(
    condominio_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> list[ObrigacaoFiscalResponse]:
    """Lista obrigacoes atrasadas."""
    obrigacoes = await repo.get_obrigacoes_atrasadas(condominio_id)
    return [ObrigacaoFiscalResponse.model_validate(o) for o in obrigacoes]


@router.get("/obrigacao/{obrigacao_id}", response_model=ObrigacaoFiscalResponse)
async def obter_obrigacao(
    obrigacao_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> ObrigacaoFiscalResponse:
    """Busca obrigacao por ID."""
    obrigacao = await repo.get_obrigacao_by_id(obrigacao_id)
    if not obrigacao:
        raise HTTPException(status_code=404, detail="Obrigacao nao encontrada")
    return ObrigacaoFiscalResponse.model_validate(obrigacao)


@router.patch("/obrigacao/{obrigacao_id}", response_model=ObrigacaoFiscalResponse)
async def atualizar_obrigacao(
    obrigacao_id: UUID,
    data: ObrigacaoFiscalUpdate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:obrigacao:update")),
) -> ObrigacaoFiscalResponse:
    """Atualiza obrigacao fiscal."""
    obrigacao = await repo.update_obrigacao(obrigacao_id, data.model_dump(exclude_unset=True))
    if not obrigacao:
        raise HTTPException(status_code=404, detail="Obrigacao nao encontrada")
    return ObrigacaoFiscalResponse.model_validate(obrigacao)


# ============================================================
# Simples Nacional / DAS Endpoints
# ============================================================


@router.post("/das", response_model=SimplesNacionalDASResponse, status_code=status.HTTP_201_CREATED)
async def criar_das(
    data: SimplesNacionalDASCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:das:create")),
) -> SimplesNacionalDASResponse:
    """Cria DAS do Simples Nacional."""
    das = await repo.create_das(
        data.condominio_id,
        data.model_dump(exclude={"condominio_id"}),
    )
    return SimplesNacionalDASResponse.model_validate(das)


@router.get("/das")
async def listar_das(
    condominio_id: UUID,
    ano: int | None = None,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> list[SimplesNacionalDASResponse]:
    """Lista DAS do Simples Nacional."""
    das_list = await repo.list_das(condominio_id, ano)
    return [SimplesNacionalDASResponse.model_validate(d) for d in das_list]


@router.get("/das/competencia")
async def obter_das_competencia(
    condominio_id: UUID,
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2000),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> SimplesNacionalDASResponse | None:
    """Busca DAS de uma competencia."""
    das = await repo.get_das_competencia(condominio_id, mes, ano)
    if not das:
        return None
    return SimplesNacionalDASResponse.model_validate(das)


@router.post("/das/calcular", response_model=DASCalcularResponse)
async def calcular_das(
    data: DASCalcularRequest,
    condominio_id: UUID = Query(...),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> DASCalcularResponse:
    """Calcula DAS do Simples Nacional.

    Para servicos de vigilancia (Anexo III):
    - ISS ja esta INCLUSO no DAS
    - CPP (INSS patronal) ja esta INCLUSO no DAS
    - Nao deve haver retencao adicional de INSS (bitributacao)
    """
    # Calcula faixa e aliquota
    resultado = calcular_das_anexo_iii(
        data.receita_bruta_mes,
        data.receita_bruta_12_meses,
    )

    # Data de vencimento: dia 20 do mes seguinte
    if data.competencia_mes == 12:
        vencimento = date(data.competencia_ano + 1, 1, 20)
    else:
        vencimento = date(data.competencia_ano, data.competencia_mes + 1, 20)

    return DASCalcularResponse(
        faixa=resultado["faixa"],
        aliquota_nominal=resultado["aliquota_nominal"],
        parcela_deduzir=resultado["parcela_deduzir"],
        aliquota_efetiva=resultado["aliquota_efetiva"],
        valor_devido=resultado["valor_devido"],
        reparticao=resultado["reparticao"],
        data_vencimento=vencimento,
    )


@router.get("/das/faixas")
async def obter_faixas_simples(
    anexo: str = Query("III", description="III, IV ou V"),
    current_user: dict = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Retorna tabela de faixas do Simples Nacional.

    Anexo III - Servicos de vigilancia, limpeza, conservacao:
    - ISS INCLUSO no DAS
    - CPP INCLUSO no DAS (nao reter INSS adicional)
    """
    if anexo == "III":
        return SIMPLES_ANEXO_III_FAIXAS
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Anexo {anexo} nao implementado. Use III.",
        )


@router.get("/das/receita-12-meses")
async def obter_receita_12_meses(
    condominio_id: UUID,
    mes_referencia: int = Query(..., ge=1, le=12),
    ano_referencia: int = Query(..., ge=2000),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Calcula receita bruta dos ultimos 12 meses para DAS."""
    receita = await repo.get_receita_12_meses(condominio_id, mes_referencia, ano_referencia)
    return {
        "referencia": f"{mes_referencia:02d}/{ano_referencia}",
        "receita_bruta_12_meses": float(receita),
    }


# ============================================================
# SUFRAMA Endpoints
# ============================================================


@router.post(
    "/suframa/config",
    response_model=SUFRAMAConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_suframa_config(
    data: SUFRAMAConfigCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:suframa:create")),
) -> SUFRAMAConfigResponse:
    """Cria configuracao SUFRAMA."""
    config = await repo.create_suframa_config(
        data.condominio_id,
        data.model_dump(exclude={"condominio_id"}),
    )
    return SUFRAMAConfigResponse.model_validate(config)


@router.get("/suframa/config", response_model=SUFRAMAConfigResponse | None)
async def obter_suframa_config(
    condominio_id: UUID,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> SUFRAMAConfigResponse | None:
    """Busca configuracao SUFRAMA ativa."""
    config = await repo.get_suframa_config(condominio_id)
    if not config:
        return None
    return SUFRAMAConfigResponse.model_validate(config)


@router.post(
    "/suframa/operacao",
    response_model=SUFRAMAOperacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_operacao_suframa(
    data: SUFRAMAOperacaoCreate,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(require_permission("fiscal:suframa:create")),
) -> SUFRAMAOperacaoResponse:
    """Registra operacao com beneficio SUFRAMA."""
    operacao = await repo.create_suframa_operacao(
        data.condominio_id,
        data.model_dump(exclude={"condominio_id"}),
    )
    return SUFRAMAOperacaoResponse.model_validate(operacao)


@router.get("/suframa/operacoes", response_model=SUFRAMAOperacaoListResponse)
async def listar_operacoes_suframa(
    condominio_id: UUID,
    data_inicial: date | None = None,
    data_final: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> SUFRAMAOperacaoListResponse:
    """Lista operacoes com beneficio SUFRAMA."""
    operacoes, total = await repo.list_suframa_operacoes(
        condominio_id=condominio_id,
        data_inicial=data_inicial,
        data_final=data_final,
        page=page,
        page_size=page_size,
    )

    economia = await repo.get_economia_suframa_periodo(
        condominio_id,
        data_inicial or date(date.today().year, 1, 1),
        data_final or date.today(),
    )

    return SUFRAMAOperacaoListResponse(
        items=[SUFRAMAOperacaoResponse.model_validate(o) for o in operacoes],
        total=total,
        total_economia_ipi=economia["ipi"],
        total_economia_icms=economia["icms"],
        total_economia_pis_cofins=economia["pis_cofins"],
    )


@router.get("/suframa/economia")
async def obter_economia_suframa(
    condominio_id: UUID,
    data_inicial: date,
    data_final: date,
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Calcula economia SUFRAMA de um periodo."""
    economia = await repo.get_economia_suframa_periodo(condominio_id, data_inicial, data_final)
    return {
        "periodo": f"{data_inicial.isoformat()} a {data_final.isoformat()}",
        "economia_ipi": float(economia["ipi"]),
        "economia_icms": float(economia["icms"]),
        "economia_pis_cofins": float(economia["pis_cofins"]),
        "total": float(economia["total"]),
    }


# ============================================================
# Dashboard e Estatisticas
# ============================================================


@router.get("/stats", response_model=FiscalStats)
async def obter_stats_fiscal(
    condominio_id: UUID,
    mes: int = Query(default=None, ge=1, le=12),
    ano: int = Query(default=None, ge=2000),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> FiscalStats:
    """Retorna estatisticas fiscais do mes."""
    if not mes:
        mes = date.today().month
    if not ano:
        ano = date.today().year

    stats = await repo.get_fiscal_stats(condominio_id, mes, ano)
    return FiscalStats(**stats)


@router.get("/dashboard", response_model=FiscalDashboard)
async def obter_dashboard_fiscal(
    condominio_id: UUID,
    mes: int = Query(default=None, ge=1, le=12),
    ano: int = Query(default=None, ge=2000),
    repo: FiscalRepository = Depends(get_repository),
    current_user: dict = Depends(get_current_user),
) -> FiscalDashboard:
    """Retorna dashboard fiscal completo."""
    if not mes:
        mes = date.today().month
    if not ano:
        ano = date.today().year

    stats = await repo.get_fiscal_stats(condominio_id, mes, ano)

    # Notas recentes
    nfes, _ = await repo.list_nfes(condominio_id, page_size=5)
    nfses, _ = await repo.list_nfses(condominio_id, page_size=5)

    notas_recentes = []
    for nfe in nfes[:3]:
        notas_recentes.append(
            {
                "tipo": "NF-e",
                "numero": nfe.numero,
                "valor": float(nfe.valor_total_nota or 0),
                "data": nfe.data_emissao.isoformat(),
                "status": nfe.status,
            }
        )
    for nfse in nfses[:3]:
        notas_recentes.append(
            {
                "tipo": "NFS-e",
                "numero": nfse.numero_nfse,
                "valor": float(nfse.valor_servicos or 0),
                "data": nfse.data_emissao.isoformat(),
                "status": nfse.status,
            }
        )

    # Obrigacoes proximas
    obrigacoes = await repo.get_obrigacoes_pendentes(condominio_id)
    obrigacoes_proximas = [
        {
            "tipo": o.tipo,
            "nome": o.nome,
            "vencimento": o.data_vencimento.isoformat(),
            "valor": float(o.valor_devido or 0),
            "dias_restantes": (o.data_vencimento - date.today()).days,
        }
        for o in obrigacoes[:5]
    ]

    # Alertas
    alertas = []
    atrasadas = await repo.get_obrigacoes_atrasadas(condominio_id)
    if atrasadas:
        alertas.append(
            {
                "tipo": "error",
                "mensagem": f"{len(atrasadas)} obrigacoes fiscais atrasadas",
            }
        )

    return FiscalDashboard(
        stats=FiscalStats(**stats),
        notas_recentes=notas_recentes,
        obrigacoes_proximas=obrigacoes_proximas,
        alertas=alertas,
        grafico_impostos=[],  # TODO
        grafico_notas=[],  # TODO
    )
