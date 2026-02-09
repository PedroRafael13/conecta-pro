"""
Controller para NFC-e (Nota Fiscal de Consumidor Eletronica).
Modelo 65 - Vendas ao consumidor final.

Endpoints:
- POST /nfce/emitir - Emite NFC-e
- GET /nfce/consultar/{chave} - Consulta NFC-e por chave
- POST /nfce/cancelar - Cancela NFC-e
- POST /nfce/inutilizar - Inutiliza numeracao
- GET /nfce/status - Status do servico
- POST /nfce/contingencia/transmitir - Transmite NFC-e em contingencia
- GET /nfce/danfe/{chave} - Gera DANFE NFC-e
- GET /nfce/xml/{chave} - Download XML autorizado
- GET /nfce/listar - Lista NFC-e emitidas

Author: Conecta PRO
Date: 2026-01-17
"""

import logging
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.responses import Response

from ..schemas.common import StandardResponse
from ..schemas.nfce import (
    NFCeCancelamentoRequest,
    NFCeContingenciaRequest,
    NFCeEmissaoRequest,
    NFCeInutilizacaoRequest,
    TipoPagamentoNFCe,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nfce", tags=["NFC-e - Nota Fiscal Consumidor"])


@router.post(
    "/emitir",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Emite NFC-e",
    description="Emite Nota Fiscal de Consumidor Eletronica (modelo 65).",
)
async def emitir_nfce(request: NFCeEmissaoRequest) -> StandardResponse:
    """
    Emite NFC-e para venda ao consumidor final.

    Args:
        request: Dados da NFC-e (itens, pagamentos, consumidor opcional).

    Returns:
        StandardResponse: Dados da emissao (chave, protocolo, QR Code).

    Raises:
        HTTPException: Se falhar a emissao.
    """
    try:
        from ..core.nfce_manager import NFCETransmitter, NFCEXMLBuilder
        from ..core.sefaz_manager import (
            Destinatario,
            DocumentType,
            Emitente,
            Endereco,
            NotaFiscal,
            Pagamento,
            PaymentType,
            Produto,
        )

        # Carregar configuracoes (em producao, vem do banco/config)
        # TODO: Integrar com configuracoes do tenant
        uf = "AM"
        ambiente = "2"  # Homologacao
        csc_id = "000001"
        csc_token = "CSC-TOKEN-HOMOLOGACAO"  # noqa: S105

        # Inicializar transmissor
        transmitter = NFCETransmitter(uf=uf, ambiente=ambiente, csc_id=csc_id, csc_token=csc_token)

        # Montar dados do emitente (em producao, vem do banco)
        emitente = Emitente(
            cnpj="35710481000103",
            razao_social="JORDAN SANTOS DE JESUS LTDA",
            nome_fantasia="CONECTA MAIS",
            inscricao_estadual="054265746",
            regime_tributario="1",  # Simples Nacional
            endereco=Endereco(
                logradouro="RUA EXEMPLO",
                numero="123",
                bairro="CENTRO",
                municipio="MANAUS",
                codigo_municipio="1302603",
                uf="AM",
                cep="69000000",
            ),
        )

        # Montar destinatario (consumidor)
        destinatario = None
        if request.consumidor and request.consumidor.cpf:
            destinatario = Destinatario(
                cpf_cnpj=request.consumidor.cpf,
                nome=request.consumidor.nome,
                email=request.consumidor.email,
            )

        # Montar produtos
        produtos = []
        for item in request.itens:
            produto = Produto(
                codigo=item.codigo,
                ean=item.ean,
                descricao=item.descricao,
                ncm=item.ncm,
                cest=item.cest,
                cfop=item.cfop,
                unidade=item.unidade,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                valor_desconto=item.valor_desconto,
                origem=item.origem,
                cst_icms=item.cst_icms,
                aliquota_icms=item.aliquota_icms,
            )
            produtos.append(produto)

        # Montar pagamentos
        pagamentos = []
        payment_type_map = {
            TipoPagamentoNFCe.DINHEIRO: PaymentType.DINHEIRO,
            TipoPagamentoNFCe.CARTAO_CREDITO: PaymentType.CARTAO_CREDITO,
            TipoPagamentoNFCe.CARTAO_DEBITO: PaymentType.CARTAO_DEBITO,
            TipoPagamentoNFCe.PIX: PaymentType.PIX,
        }
        for pag in request.pagamentos:
            payment_type = payment_type_map.get(pag.tipo, PaymentType.OUTROS)
            pagamento = Pagamento(
                tipo=payment_type,
                valor=pag.valor,
            )
            pagamentos.append(pagamento)

        # Criar NotaFiscal
        nf = NotaFiscal(
            tipo=DocumentType.NFCE,
            serie=request.serie,
            emitente=emitente,
            destinatario=destinatario,
            produtos=produtos,
            pagamentos=pagamentos,
        )

        # Gerar XML
        xml_builder = NFCEXMLBuilder(csc_id, csc_token)
        xml_builder.build_nfce(nf, ambiente)

        # Em producao, assinar e transmitir
        # Por enquanto, retornar dados simulados
        resultado = {
            "chave_acesso": nf.chave_acesso,
            "numero": nf.numero,
            "serie": nf.serie,
            "protocolo": f"313260000{datetime.now().strftime('%H%M%S')}",
            "codigo": "100",
            "mensagem": "Autorizado o uso da NFC-e",
            "data_autorizacao": datetime.now().isoformat(),
            "valor_total": float(nf.valor_total),
            "qrcode_url": transmitter.generate_qrcode(
                nf.chave_acesso,
                datetime.now().isoformat(),
                nf.valor_total,
                Decimal("0"),
                "DIGEST_VALUE_PLACEHOLDER",
                request.consumidor.cpf if request.consumidor else None,
            ),
            "url_consulta": transmitter.qrcode_generator.get_url_chave(),
        }

        logger.info(f"NFC-e emitida: {nf.chave_acesso}")

        return StandardResponse(
            success=True,
            message="NFC-e autorizada com sucesso",
            data=resultado,
        )

    except ValueError as e:
        logger.warning(f"Dados invalidos na emissao NFC-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados invalidos: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro ao emitir NFC-e: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao emitir NFC-e",
        )


@router.get(
    "/consultar/{chave_acesso}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta NFC-e por chave",
    description="Consulta situacao de NFC-e pela chave de acesso.",
)
async def consultar_nfce(
    chave_acesso: str = Path(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da NFC-e (44 digitos)",
    ),
) -> StandardResponse:
    """
    Consulta NFC-e pela chave de acesso.

    Args:
        chave_acesso: Chave de acesso da NFC-e.

    Returns:
        StandardResponse: Dados da NFC-e.
    """
    try:
        # Validar formato da chave
        if not chave_acesso.isdigit():
            raise ValueError("Chave deve conter apenas numeros")

        # Verificar modelo (posicoes 21-22 devem ser 65 para NFC-e)
        modelo = chave_acesso[20:22]
        if modelo != "65":
            raise ValueError(f"Chave nao e de NFC-e (modelo {modelo})")

        # TODO: Consultar na SEFAZ
        # Por enquanto, retornar dados simulados
        resultado = {
            "chave_acesso": chave_acesso,
            "situacao": "autorizada",
            "codigo": "100",
            "mensagem": "Autorizado o uso da NFC-e",
            "protocolo": "313260000123456",
            "data_autorizacao": "2026-01-17T10:30:00-04:00",
        }

        return StandardResponse(
            success=True,
            message="NFC-e encontrada",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao consultar NFC-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar NFC-e",
        )


@router.post(
    "/cancelar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancela NFC-e",
    description="Cancela NFC-e autorizada (prazo de 30 minutos para NFC-e).",
)
async def cancelar_nfce(request: NFCeCancelamentoRequest) -> StandardResponse:
    """
    Cancela NFC-e autorizada.

    Prazo para cancelamento: 30 minutos apos autorizacao (pode variar por UF).

    Args:
        request: Chave de acesso e justificativa.

    Returns:
        StandardResponse: Dados do cancelamento.
    """
    try:
        if len(request.justificativa) < 15:
            raise ValueError("Justificativa deve ter no minimo 15 caracteres")

        # TODO: Enviar evento de cancelamento para SEFAZ
        resultado = {
            "chave_acesso": request.chave_acesso,
            "protocolo_cancelamento": f"313260000{datetime.now().strftime('%H%M%S')}",
            "data_cancelamento": datetime.now().isoformat(),
            "codigo": "135",
            "mensagem": "Evento registrado e vinculado a NFC-e",
        }

        logger.info(f"NFC-e cancelada: {request.chave_acesso}")

        return StandardResponse(
            success=True,
            message="NFC-e cancelada com sucesso",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao cancelar NFC-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cancelar NFC-e",
        )


@router.post(
    "/inutilizar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Inutiliza numeracao",
    description="Inutiliza faixa de numeracao de NFC-e.",
)
async def inutilizar_nfce(request: NFCeInutilizacaoRequest) -> StandardResponse:
    """
    Inutiliza numeracao de NFC-e.

    Usado quando numeros sao pulados (falha de sistema, etc).

    Args:
        request: Serie, numeros inicial/final e justificativa.

    Returns:
        StandardResponse: Dados da inutilizacao.
    """
    try:
        if request.numero_final < request.numero_inicial:
            raise ValueError("Numero final deve ser >= numero inicial")

        # TODO: Enviar para SEFAZ
        resultado = {
            "serie": request.serie,
            "numero_inicial": request.numero_inicial,
            "numero_final": request.numero_final,
            "protocolo": f"313260000{datetime.now().strftime('%H%M%S')}",
            "data_inutilizacao": datetime.now().isoformat(),
            "codigo": "102",
            "mensagem": "Inutilizacao de numero homologado",
        }

        logger.info(f"Numeracao inutilizada: serie {request.serie}, {request.numero_inicial}-{request.numero_final}")

        return StandardResponse(
            success=True,
            message="Numeracao inutilizada com sucesso",
            data=resultado,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao inutilizar numeracao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao inutilizar numeracao",
        )


@router.get(
    "/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Status do servico NFC-e",
    description="Consulta status do servico de NFC-e na SEFAZ.",
)
async def status_servico_nfce(
    uf: str = Query(default="AM", min_length=2, max_length=2, description="UF do servico"),
) -> StandardResponse:
    """
    Consulta status do servico NFC-e na SEFAZ.

    Args:
        uf: UF para consulta.

    Returns:
        StandardResponse: Status do servico.
    """
    try:
        # TODO: Consultar status real na SEFAZ
        resultado = {
            "uf": uf.upper(),
            "online": True,
            "codigo": "107",
            "mensagem": "Servico em Operacao",
            "tempo_medio": 250,
            "data_consulta": datetime.now().isoformat(),
            "ambiente": "Homologacao",
        }

        return StandardResponse(
            success=True,
            message="Servico NFC-e operacional",
            data=resultado,
        )

    except Exception as e:
        logger.error(f"Erro ao consultar status NFC-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao consultar status",
        )


@router.post(
    "/contingencia/transmitir",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Transmite NFC-e em contingencia",
    description="Transmite NFC-e que foi emitida em contingencia offline.",
)
async def transmitir_contingencia(request: NFCeContingenciaRequest) -> StandardResponse:
    """
    Transmite NFC-e emitida em contingencia.

    Quando o servico fica offline, a NFC-e pode ser emitida em
    contingencia offline e transmitida posteriormente.

    Args:
        request: XML da contingencia e dados.

    Returns:
        StandardResponse: Resultado da transmissao.
    """
    try:
        # TODO: Transmitir XML para SEFAZ
        resultado = {
            "protocolo": f"313260000{datetime.now().strftime('%H%M%S')}",
            "codigo": "100",
            "mensagem": "Autorizado o uso da NFC-e",
            "data_autorizacao": datetime.now().isoformat(),
            "contingencia_regularizada": True,
        }

        logger.info("NFC-e contingencia transmitida")

        return StandardResponse(
            success=True,
            message="NFC-e em contingencia autorizada",
            data=resultado,
        )

    except Exception as e:
        logger.error(f"Erro ao transmitir contingencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao transmitir contingencia",
        )


@router.get(
    "/danfe/{chave_acesso}",
    summary="Gera DANFE NFC-e",
    description="Gera DANFE (cupom fiscal) da NFC-e.",
)
async def gerar_danfe_nfce(
    chave_acesso: str = Path(..., min_length=44, max_length=44),
    formato: str = Query(default="pdf", pattern=r"^(pdf|html|escpos)$"),
) -> Response:
    """
    Gera DANFE da NFC-e.

    Formatos suportados:
    - pdf: PDF para impressao A4 ou termica
    - html: HTML responsivo
    - escpos: Comandos ESC/POS para impressora termica

    Args:
        chave_acesso: Chave de acesso da NFC-e.
        formato: Formato de saida.

    Returns:
        Response: DANFE no formato solicitado.
    """
    try:
        # TODO: Gerar DANFE real
        # Por enquanto, retornar placeholder

        if formato == "html":
            content = f"""
            <html>
            <head><title>DANFE NFC-e</title></head>
            <body>
            <h1>DANFE NFC-e</h1>
            <p>Chave: {chave_acesso}</p>
            <p>Consulte em: nfce.sefaz.am.gov.br</p>
            </body>
            </html>
            """
            return Response(content=content, media_type="text/html")

        elif formato == "escpos":
            # Comandos ESC/POS simplificados
            content = f"DANFE NFC-e\nChave: {chave_acesso}\n"
            return Response(content=content, media_type="text/plain")

        else:
            # PDF placeholder
            return Response(
                content=b"PDF_PLACEHOLDER",
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=danfe_{chave_acesso}.pdf"},
            )

    except Exception as e:
        logger.error(f"Erro ao gerar DANFE: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar DANFE",
        )


@router.get(
    "/xml/{chave_acesso}",
    summary="Download XML NFC-e",
    description="Download do XML autorizado da NFC-e.",
)
async def download_xml_nfce(
    chave_acesso: str = Path(..., min_length=44, max_length=44),
) -> Response:
    """
    Download XML autorizado da NFC-e.

    Args:
        chave_acesso: Chave de acesso da NFC-e.

    Returns:
        Response: XML da NFC-e.
    """
    try:
        # TODO: Buscar XML do banco/storage
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <NFe>
        <infNFe Id="NFe{chave_acesso}" versao="4.00">
            <!-- XML da NFC-e -->
        </infNFe>
    </NFe>
    <protNFe>
        <infProt>
            <chNFe>{chave_acesso}</chNFe>
            <cStat>100</cStat>
            <xMotivo>Autorizado o uso da NFC-e</xMotivo>
        </infProt>
    </protNFe>
</nfeProc>"""

        return Response(
            content=xml,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={chave_acesso}-nfce.xml"},
        )

    except Exception as e:
        logger.error(f"Erro ao baixar XML: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao baixar XML",
        )


@router.get(
    "/listar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista NFC-e emitidas",
    description="Lista NFC-e emitidas com filtros.",
)
async def listar_nfce(
    data_inicio: str | None = Query(None, description="Data inicio (YYYY-MM-DD)"),
    data_fim: str | None = Query(None, description="Data fim (YYYY-MM-DD)"),
    _status_nfce: str | None = Query(None, description="Status (autorizada, cancelada)"),
    page: int = Query(default=1, ge=1, description="Pagina"),
    per_page: int = Query(default=20, ge=1, le=100, description="Itens por pagina"),
) -> StandardResponse:
    """
    Lista NFC-e emitidas com filtros opcionais.

    Args:
        data_inicio: Filtro data inicio.
        data_fim: Filtro data fim.
        status_nfce: Filtro por status.
        page: Numero da pagina.
        per_page: Itens por pagina.

    Returns:
        StandardResponse: Lista paginada de NFC-e.
    """
    try:
        # TODO: Buscar do banco de dados
        resultado = {
            "items": [
                {
                    "chave_acesso": "13260135710481000103650010000000011234567890",
                    "numero": 1,
                    "serie": 1,
                    "data_emissao": "2026-01-17T10:30:00",
                    "valor_total": 150.00,
                    "status": "autorizada",
                    "consumidor_cpf": None,
                },
            ],
            "total": 1,
            "page": page,
            "per_page": per_page,
            "pages": 1,
        }

        return StandardResponse(
            success=True,
            message="NFC-e listadas com sucesso",
            data=resultado,
        )

    except Exception as e:
        logger.error(f"Erro ao listar NFC-e: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar NFC-e",
        )
