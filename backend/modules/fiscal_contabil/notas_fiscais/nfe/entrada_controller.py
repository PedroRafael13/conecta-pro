"""
NF-e Entrada Controller
Upload e consulta de NF-e recebidas (compras) + estoque virtual.

Endpoints:
  POST /nfe-entrada/upload-xml   — faz upload de XML e atualiza estoque
  GET  /nfe-entrada/listar       — lista NF-e de compra recebidas
  GET  /nfe-entrada/estoque      — exibe estoque virtual de compras
  POST /nfe-entrada/sync-sefaz   — consulta SEFAZ e importa novas NF-e
"""

import logging
import os

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/nfe-entrada", tags=["NF-e Entrada/Compras"])

logger = logging.getLogger(__name__)

CNPJ_EMPRESA = os.getenv("NFSE_MANAUS_CNPJ", "35710481000103")


def _get_conn():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


# --------------------------------------------------------------------------- #
#  POST /nfe-entrada/upload-xml                                                #
# --------------------------------------------------------------------------- #


@router.post("/upload-xml", summary="Upload XML de NF-e de compra — atualiza estoque")
async def upload_xml_nfe(arquivo: UploadFile = File(...)):
    """
    Recebe XML de NF-e de compra emitida por fornecedor.
    Salva em disco e atualiza o estoque virtual automaticamente.
    """
    from modules.government_integrations.services.nfe_entrada_sync_service import (
        NFEEntradaSyncService,
    )

    if not (arquivo.filename or "").endswith(".xml"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser XML")

    conteudo = await arquivo.read()
    xml_str = conteudo.decode("utf-8", errors="ignore")

    # Salvar XML em disco
    pasta = os.getenv("NFE_UPLOADS_DIR", "/tmp/nfe/entrada")  # nosec B108
    os.makedirs(pasta, exist_ok=True)
    xml_path = f"{pasta}/{arquivo.filename}"
    with open(xml_path, "wb") as f:
        f.write(conteudo)

    svc = NFEEntradaSyncService()
    conn = _get_conn()
    try:
        resultado = svc.processar_xml_nfe(xml_str, conn)
    except Exception as exc:
        logger.error("Erro ao processar XML NF-e: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()

    if "erro" in resultado:
        raise HTTPException(status_code=422, detail=resultado.get("erro", "Erro desconhecido"))

    return {"arquivo_salvo": xml_path, "processamento": resultado}


# --------------------------------------------------------------------------- #
#  GET /nfe-entrada/listar                                                     #
# --------------------------------------------------------------------------- #


@router.get("/listar")
def listar_nfe_entrada(limit: int = 50, offset: int = 0, processada: bool | None = None):
    """
    Lista NF-e de compra registradas (emitidas por fornecedores contra a empresa).
    """
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Garante que a tabela existe antes de consultar
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nfe_entradas (
                    id              SERIAL PRIMARY KEY,
                    chave_acesso    VARCHAR(44) UNIQUE NOT NULL,
                    nsu             VARCHAR(20),
                    numero          VARCHAR(20),
                    serie           VARCHAR(5),
                    emitente_cnpj   VARCHAR(14),
                    emitente_nome   VARCHAR(200),
                    destinatario_cnpj VARCHAR(14),
                    data_emissao    DATE,
                    valor_total     NUMERIC(15,2),
                    status          VARCHAR(30) DEFAULT 'recebida',
                    xml_raw         TEXT,
                    processada      BOOLEAN DEFAULT FALSE,
                    created_at      TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()

            where = ""
            params: list = []
            if processada is not None:
                where = "WHERE processada = %s"
                params.append(processada)

            cur.execute(
                f"""
                SELECT id, chave_acesso, numero, serie, emitente_cnpj, emitente_nome,
                       data_emissao, valor_total, status, processada, created_at
                FROM nfe_entradas
                {where}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

        return {"total": len(rows), "nfes": [dict(r) for r in rows]}
    except Exception as exc:
        logger.error("Erro ao listar NF-e entrada: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
#  GET /nfe-entrada/estoque                                                    #
# --------------------------------------------------------------------------- #


@router.get("/estoque")
def listar_estoque_compras(limit: int = 100, offset: int = 0, busca: str = ""):
    """
    Exibe estoque virtual atualizado pelas NF-e de compra.
    """
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nfe_compras_estoque (
                    id                  SERIAL PRIMARY KEY,
                    item_code           VARCHAR(60) UNIQUE NOT NULL,
                    descricao           VARCHAR(200),
                    ncm                 VARCHAR(8),
                    unidade             VARCHAR(6),
                    qty_on_hand         NUMERIC(15,4) DEFAULT 0,
                    unit_cost           NUMERIC(15,4) DEFAULT 0,
                    avg_cost            NUMERIC(15,4) DEFAULT 0,
                    last_purchase_date  DATE,
                    last_nfe_key        VARCHAR(44),
                    updated_at          TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()

            where = ""
            params: list = []
            if busca:
                where = "WHERE item_code ILIKE %s OR descricao ILIKE %s"
                params = [f"%{busca}%", f"%{busca}%"]

            cur.execute(
                f"""
                SELECT item_code, descricao, ncm, unidade,
                       qty_on_hand, unit_cost, avg_cost,
                       last_purchase_date, last_nfe_key, updated_at
                FROM nfe_compras_estoque
                {where}
                ORDER BY descricao
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

        return {"total_itens": len(rows), "estoque": [dict(r) for r in rows]}
    except Exception as exc:
        logger.error("Erro ao listar estoque NF-e: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
#  POST /nfe-entrada/sync-sefaz                                                #
# --------------------------------------------------------------------------- #


@router.post("/sync-sefaz", summary="Sincronizar NF-e entrada via SEFAZ")
async def sync_sefaz_entrada(ultimo_nsu: str = "0"):
    """Consulta NF-e distribuição no SEFAZ-AM."""
    from modules.government_integrations.services.nfe_entrada_sync_service import (
        NFEEntradaSyncService,
    )

    svc = NFEEntradaSyncService()
    resultado = svc.buscar_nfe_recebidas(ultimo_nsu)
    return resultado
