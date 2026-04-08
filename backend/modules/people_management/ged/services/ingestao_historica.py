"""
Ingestão Histórica — Conecta PRO
Varre os ZIPs do Google Drive, descompacta,
extrai texto dos PDFs, identifica cliente e mês,
e alimenta ATLAS + SOPHIA com o histórico completo.
"""

import io
import logging
import os
import re
import uuid as _uuid_mod
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

GED_STORAGE_BASE = os.environ.get("GED_STORAGE_PATH", "/app/uploads/ged")

logger = logging.getLogger(__name__)

# Mapeamento de meses em português
MESES = {
    "janeiro": "01",
    "fevereiro": "02",
    "março": "03",
    "marco": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12",
}

# Tipos de documento por padrão de nome
PADROES_TIPO = {
    r"holerite|contracheque|recibo.*salario": "holerite",
    r"espelho.*ponto|ponto.*espelho": "espelho_ponto",
    r"nf[se]|nota.*fiscal|aprel": "nota_fiscal",
    r"boleto|cobranca": "boleto",
    r"cnd|certidao.*negativa|certidao.*debito": "certidao",
    r"crf.*fgts|fgts|comprovante.*fgts": "crf_fgts",
    r"crf|regularidade.*fgts": "crf_fgts",
    r"aso|atestado.*saude": "aso",
    r"epi|equipamento.*protecao": "ficha_epi",
    r"rescisao|trct|demissao": "rescisao",
    r"admissao|contrato.*trabalho": "contrato_admissao",
    r"comprovante.*pagamento.*salario|pagto.*salario": "comprovante_salario",
    r"comprovante.*pagamento.*fgts": "comprovante_fgts",
    r"nr-?\d+|treinamento|certificado": "certificado_nr",
}

KITS_FOLDER = "1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck"  # pragma: allowlist secret

# Estado in-memory do processo de ingestão
_status: dict[str, Any] = {
    "em_andamento": False,
    "iniciado_em": None,
    "concluido_em": None,
    "total_zips": 0,
    "zips_processados": 0,
    "pdfs_extraidos": 0,
    "docs_indexados": 0,
    "erros": [],
    "ultimo_zip": None,
}


# ---------------------------------------------------------------------------
# Consultas ao banco via SQLAlchemy sync (psycopg2 — sem depender do Docker CLI)
# ---------------------------------------------------------------------------


def _exec_sync(query: str, params: dict | None = None) -> list[tuple]:
    """Executa query síncrona via SyncSessionLocal (psycopg2) e retorna linhas."""
    try:
        from sqlalchemy import text as sa_text

        from core.database.session import SyncSessionLocal

        with SyncSessionLocal() as db:
            result = db.execute(sa_text(query), params or {})
            return list(result.fetchall())
    except Exception as e:
        logger.warning("INGESTAO: erro ao consultar banco: %s", e)
        return []


def _exec_write_sync(query: str, params: dict | None = None) -> list[tuple]:
    """Executa INSERT/UPDATE com commit e retorna linhas (RETURNING)."""
    try:
        from sqlalchemy import text as sa_text

        from core.database.session import SyncSessionLocal

        with SyncSessionLocal() as db:
            result = db.execute(sa_text(query), params or {})
            db.commit()
            try:
                return list(result.fetchall())
            except Exception:
                return []
    except Exception as e:
        logger.warning("INGESTAO: erro de escrita no banco: %s", e)
        return []


def _mapear_clients_para_ged() -> dict[str, str]:
    """Retorna {clients.id: ged_clients.id} via correspondência de nome."""
    rows = _exec_sync("SELECT c.id::text, g.id::text FROM clients c JOIN ged_clients g ON g.name ILIKE c.name")
    return dict(rows)


def _buscar_clientes() -> dict[str, str]:
    """Buscar todos os clientes do banco. Retorna {NOME_UPPER: uuid}."""
    rows = _exec_sync(
        "SELECT id::text, name FROM clients "
        "WHERE name NOT ILIKE '%conecta mais%' "
        "AND name NOT ILIKE '%matriz%' "
        "ORDER BY name"
    )
    return {str(nome).strip().upper(): str(uuid).strip() for uuid, nome in rows if nome}


def _buscar_funcionarios() -> dict[str, str]:
    """Buscar funcionários ativos e cliente associado. Retorna {primeiro_nome: CLIENTE_UPPER}."""
    rows = _exec_sync(
        "SELECT e.nome, c.name AS cliente "
        "FROM employees e "
        "JOIN allocations a ON a.employee_id = e.id "
        "JOIN posts p ON p.id = a.post_id "
        "JOIN clients c ON c.id = p.client_id "
        "WHERE a.status IN ('ativo', 'active') "
        "AND e.nome IS NOT NULL"
    )
    result: dict[str, str] = {}
    for nome, cliente in rows:
        if not nome:
            continue
        primeiro = str(nome).strip().split()[0].lower()
        if len(primeiro) > 2:
            result[primeiro] = str(cliente).strip().upper()
    return result


# ---------------------------------------------------------------------------
# Extração de texto de PDF
# ---------------------------------------------------------------------------


def extrair_texto_pdf(conteudo: bytes) -> str:
    """Extrai texto de PDF — PyMuPDF primário, PyPDF2 fallback. Máx 3 pág/2000 chars."""
    # Primário: PyMuPDF (fitz)
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=conteudo, filetype="pdf")
        partes: list[str] = []
        for i, page in enumerate(doc):
            if i >= 3:
                break
            partes.append(page.get_text())
        doc.close()
        texto = " ".join(partes).strip()
        if texto:
            return texto[:2000]
    except Exception as e:
        logger.debug("fitz falhou: %s", e)

    # Fallback: PyPDF2
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        partes = []
        for i, page in enumerate(reader.pages):
            if i >= 3:
                break
            txt = page.extract_text()
            if txt:
                partes.append(txt)
        return " ".join(partes).strip()[:2000]
    except Exception as e:
        logger.debug("PyPDF2 falhou: %s", e)

    return ""


# ---------------------------------------------------------------------------
# Classificação e identificação
# ---------------------------------------------------------------------------


def classificar_documento(nome_arquivo: str, conteudo_bytes: bytes = b"") -> dict:
    """
    Classificar documento pelo nome e conteúdo.
    Retorna tipo, mes_detectado, func_no_nome.
    """
    nome_lower = nome_arquivo.lower()
    nome_clean = re.sub(r"[_\-\.]", " ", nome_lower)

    # Detectar tipo
    tipo = "outros"
    for padrao, tipo_doc in PADROES_TIPO.items():
        if re.search(padrao, nome_clean, re.IGNORECASE):
            tipo = tipo_doc
            break

    # Detectar mês no nome do arquivo
    mes_detectado = None
    for mes_nome, mes_num in MESES.items():
        if mes_nome in nome_clean:
            mes_detectado = mes_num
            break

    # Detectar possível nome de funcionário no arquivo
    func_no_nome = None
    partes = re.split(r"[_\-\s]+", nome_clean)
    if len(partes) >= 2:
        for p in partes[1:]:
            if len(p) > 3 and p not in MESES and not p.isdigit():
                func_no_nome = p
                break

    return {
        "tipo": tipo,
        "mes_detectado": mes_detectado,
        "func_no_nome": func_no_nome,
        "nome_original": nome_arquivo,
    }


def identificar_cliente_por_texto(
    texto_pdf: str,
    clientes: dict[str, str],
) -> str | None:
    """
    Identificar cliente pelo texto do PDF.
    Procura o nome do cliente nas primeiras linhas.
    Retorna client_id ou None.
    """
    if not texto_pdf or not clientes:
        return None

    texto_upper = texto_pdf.upper()
    for nome_cliente, client_id in clientes.items():
        palavras = nome_cliente.split()
        if len(palavras) >= 2:
            matches = sum(1 for p in palavras if p in texto_upper and len(p) > 3)
            if matches >= min(2, len(palavras)):
                return client_id
    return None


def extrair_mes_do_nome_zip(nome_zip: str) -> str | None:
    """
    Extrai competência (YYYY-MM) do nome do arquivo ZIP.

    Exemplos:
      kits_2025_01.zip           → 2025-01
      KIT DE DOCUMENTOS - SET... → 2025-09 (ano_zip - 1)
      2024-12_folha.zip          → 2024-12
    """
    nome_upper = nome_zip.upper()

    # Detectar mês em português
    mes_num = None
    for mes_nome, num in MESES.items():
        if mes_nome.upper() in nome_upper:
            mes_num = num
            break

    # Detectar ano — padrão YYYY
    ano_match = re.search(r"20(\d{2})", nome_zip)
    if ano_match:
        ano_zip = int("20" + ano_match.group(1))
        # Kits do Drive são do mês anterior ao ano do ZIP
        ano_kit = ano_zip - 1 if mes_num else ano_zip
    else:
        ano_kit = 2025  # default para histórico

    if mes_num:
        return f"{ano_kit}-{mes_num}"

    # Formato YYYY-MM ou YYYY_MM direto
    m = re.search(r"(\d{4})[-_](\d{2})", nome_zip)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    return None


# ---------------------------------------------------------------------------
# Drive helpers (síncronos, executados via run_in_executor)
# ---------------------------------------------------------------------------


def _get_drive_service():
    """Obtém serviço Google Drive API ou lança RuntimeError.

    Tenta em ordem:
    1. Service account (google_drive_service._get_drive_service)
    2. OAuth2 singleton (gdrive_service._service) — conectado via /gdrive/autorizar
    """
    from modules.people_management.ged.services.google_drive_service import _get_drive_service as _gds

    service = _gds()
    if service:
        return service

    # Fallback: OAuth2 singleton (gdrive_service)
    try:
        from modules.gdrive.services.gdrive_service import gdrive_service as _oauth_svc

        if _oauth_svc._service is not None:
            logger.info("INGESTAO: usando OAuth2 gdrive_service singleton")
            return _oauth_svc._service
        # Tenta inicializar via service account como último recurso
        if _oauth_svc._init_service():
            return _oauth_svc._service
    except Exception as _e:
        logger.debug("INGESTAO: fallback OAuth2 falhou: %s", _e)

    raise RuntimeError(
        "Google Drive não configurado — verifique GOOGLE_DRIVE_CREDENTIALS "
        "ou acesse /api/v1/gdrive/autorizar para conectar."
    )


def _listar_zips_na_pasta(service, folder_id: str) -> list[dict]:
    """Lista todos os arquivos ZIP dentro de uma pasta do Drive."""
    result = (
        service.files()
        .list(
            q=(f"'{folder_id}' in parents and mimeType='application/zip' and trashed=false"),
            fields="files(id, name, size, modifiedTime)",
            pageSize=100,
        )
        .execute()
    )
    return result.get("files", [])


def _baixar_arquivo(service, file_id: str) -> bytes:
    """Baixa conteúdo de um arquivo do Google Drive. Retorna b'' em caso de erro."""
    from googleapiclient.http import MediaIoBaseDownload

    buf = io.BytesIO()
    try:
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    except Exception as exc:
        logger.warning("INGESTAO: falha ao baixar arquivo %s: %s", file_id, exc)
        return b""
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class IngestaoHistorica:
    """
    Processa os ZIPs históricos do Drive e alimenta ATLAS + SOPHIA.

    Uso:
        ingestao = IngestaoHistorica()
        resultado = await ingestao.processar_todos_os_zips()
    """

    def __init__(self) -> None:
        self._clientes: dict[str, str] = {}
        self._funcionarios: dict[str, str] = {}

    def _carregar_contexto(self) -> None:
        """Carregar clientes e funcionários do banco."""
        self._clientes = _buscar_clientes()
        self._funcionarios = _buscar_funcionarios()
        logger.info(
            "INGESTAO: contexto carregado — %d clientes, %d funcionarios",
            len(self._clientes),
            len(self._funcionarios),
        )

    def processar_zip(self, conteudo_zip: bytes, nome_zip: str) -> dict:
        """
        Processar um arquivo ZIP completo.
        Retorna lista de documentos classificados.
        """
        from modules.gedeon.agents.sophia import sophia

        resultado: dict[str, Any] = {
            "nome_zip": nome_zip,
            "mes_zip": extrair_mes_do_nome_zip(nome_zip),
            "documentos": [],
            "erros": [],
        }

        if not conteudo_zip:
            resultado["erros"].append("Arquivo vazio ou falha no download")
            logger.warning("INGESTAO: ZIP %s vazio — ignorando", nome_zip)
            return resultado

        try:
            with zipfile.ZipFile(io.BytesIO(conteudo_zip)) as zf:
                for entry in zf.infolist():
                    if entry.is_dir():
                        continue
                    if not entry.filename.lower().endswith(".pdf"):
                        continue

                    try:
                        pdf_bytes = zf.read(entry.filename)
                        nome_pdf = Path(entry.filename).name
                        classificacao = classificar_documento(nome_pdf, pdf_bytes)

                        # Identificar cliente
                        client_id = None
                        texto = ""

                        # 1. Pelo nome do funcionário no nome do arquivo
                        func = classificacao.get("func_no_nome")
                        if func and func in self._funcionarios:
                            nome_cli = self._funcionarios[func]
                            client_id = self._clientes.get(nome_cli)

                        # 2. Pelo texto do PDF
                        if not client_id:
                            texto = extrair_texto_pdf(pdf_bytes)
                            client_id = identificar_cliente_por_texto(texto, self._clientes)

                        competencia = resultado["mes_zip"] or datetime.utcnow().strftime("%Y-%m")

                        doc_entry = {
                            "nome": nome_pdf,
                            "tipo": classificacao["tipo"],
                            "client_id": client_id,
                            "competencia": competencia,
                            "tamanho": len(pdf_bytes),
                            "conteudo": pdf_bytes,
                        }
                        resultado["documentos"].append(doc_entry)

                        # Indexar no SOPHIA
                        texto_idx = texto or extrair_texto_pdf(pdf_bytes) or f"Documento: {nome_pdf}"
                        meta = {
                            "fonte": "historico_drive",
                            "origem": "historico_drive",
                            "zip_nome": nome_zip,
                            "nome_pdf": nome_pdf,
                            "competencia": competencia,
                            "tipo": classificacao["tipo"],
                            "client_id": client_id or "",
                        }
                        sophia.indexar_documento(f"hist_{nome_zip}_{nome_pdf}", texto_idx, meta)

                    except Exception as e:
                        resultado["erros"].append(f"{entry.filename}: {e}")
                        logger.warning("INGESTAO: erro PDF %s no ZIP %s: %s", entry.filename, nome_zip, e)

        except zipfile.BadZipFile as e:
            resultado["erros"].append(f"ZIP corrompido: {e}")
            logger.error("INGESTAO: ZIP invalido %s: %s", nome_zip, e)
        except Exception as e:
            resultado["erros"].append(str(e))

        return resultado

    async def processar_todos_os_zips(self, folder_id: str = KITS_FOLDER) -> dict:
        """
        Varrer pasta kits no Drive, baixar ZIPs,
        processar cada um, e alimentar ATLAS + SOPHIA.
        """
        global _status

        _status.update(
            {
                "em_andamento": True,
                "iniciado_em": datetime.utcnow().isoformat(),
                "concluido_em": None,
                "total_zips": 0,
                "zips_processados": 0,
                "pdfs_extraidos": 0,
                "docs_indexados": 0,
                "erros": [],
                "ultimo_zip": None,
            }
        )

        try:
            service = _get_drive_service()
        except RuntimeError as e:
            _status["em_andamento"] = False
            _status["erros"].append(str(e))
            return {
                "erro": str(e),
                "instrucao": "Acesse /api/v1/gdrive/autorizar para conectar",
            }

        import asyncio

        loop = asyncio.get_event_loop()

        # Carregar contexto do banco
        self._carregar_contexto()

        # Mapeamento clients.id → ged_clients.id (carregado uma vez)
        mapa_ged = await loop.run_in_executor(None, _mapear_clients_para_ged)
        logger.info("INGESTAO: mapa GED carregado — %d clientes", len(mapa_ged))

        # Listar ZIPs
        zips = await loop.run_in_executor(None, _listar_zips_na_pasta, service, folder_id)
        _status["total_zips"] = len(zips)
        logger.info("INGESTAO: %d ZIPs encontrados na pasta %s", len(zips), folder_id)

        total_docs = 0
        total_indexados = 0
        total_ged_salvos = 0
        resultados_por_zip: list[dict] = []

        for zip_info in zips:
            zip_id = zip_info["id"]
            zip_name = zip_info["name"]
            _status["ultimo_zip"] = zip_name

            try:
                conteudo_zip = await loop.run_in_executor(None, _baixar_arquivo, service, zip_id)
                resultado_zip = self.processar_zip(conteudo_zip, zip_name)

                docs = resultado_zip["documentos"]
                total_docs += len(docs)
                total_indexados += len(docs)
                _status["zips_processados"] += 1
                _status["pdfs_extraidos"] += len(docs)
                _status["docs_indexados"] += len(docs)

                if resultado_zip["erros"]:
                    _status["erros"].extend(resultado_zip["erros"])

                # Registrar no ATLAS (por cliente/competência único no ZIP)
                competencia_zip = resultado_zip.get("mes_zip") or datetime.utcnow().strftime("%Y-%m")
                clientes_no_zip = {d["client_id"] for d in docs if d.get("client_id")}

                from modules.gedeon.agents.atlas import atlas

                for client_id in clientes_no_zip:
                    docs_cliente = [d for d in docs if d.get("client_id") == client_id]
                    atlas.registrar_kit_concluido(
                        client_id=client_id,
                        competencia=competencia_zip,
                        tipo_kit="historico_drive",
                        score_final=100,
                        docs_total=len(docs_cliente),
                        docs_auto=len(docs_cliente),
                        observacoes=f"Ingestao historica — {zip_name}",
                        criado_por="ingestao_historica",
                    )

                # Persistir no GED (filesystem + ged_document_kits + ged_kit_documents)
                ged_result = await loop.run_in_executor(None, self._persistir_docs_no_ged, docs, mapa_ged)
                total_ged_salvos += ged_result["salvos"]
                if ged_result["erros"]:
                    _status["erros"].extend(ged_result["erros"])

                resultados_por_zip.append(
                    {
                        "zip": zip_name,
                        "docs": len(docs),
                        "ged_salvos": ged_result["salvos"],
                        "clientes_id": list(clientes_no_zip),
                        "competencia": competencia_zip,
                    }
                )
                logger.info(
                    "INGESTAO: %s — %d PDFs indexados, %d no GED",
                    zip_name,
                    len(docs),
                    ged_result["salvos"],
                )

            except Exception as e:
                _status["erros"].append(f"{zip_name}: {e}")
                logger.error("INGESTAO: erro ao processar ZIP %s: %s", zip_name, e)

        # Persistir tudo no banco via SOPHIA (método síncrono — rodar em executor)
        try:
            from modules.gedeon.agents.sophia import sophia

            await loop.run_in_executor(None, sophia.indexar_acervo_completo)
            logger.info("INGESTAO: SOPHIA reindexado — %d docs historicos persistidos", total_indexados)
        except Exception as e:
            logger.warning("INGESTAO: falha ao persistir no banco SOPHIA: %s", e)

        _status["em_andamento"] = False
        _status["concluido_em"] = datetime.utcnow().isoformat()

        return {
            "ok": True,
            "total_zips": len(zips),
            "zips_processados": _status["zips_processados"],
            "pdfs_extraidos": total_docs,
            "docs_indexados": total_indexados,
            "ged_salvos": total_ged_salvos,
            "erros": len(_status["erros"]),
            "resultados_por_zip": resultados_por_zip,
        }

    def _persistir_docs_no_ged(self, docs: list[dict], mapa_ged: dict[str, str]) -> dict:
        """
        Salva cada PDF no filesystem e cria registros em
        ged_document_kits + ged_kit_documents.

        docs: lista retornada por processar_zip (cada item tem 'conteudo' bytes)
        mapa_ged: {clients.id -> ged_clients.id}
        """
        salvos = 0
        erros_ged: list[str] = []

        # Agrupar por (ged_client_id, competencia)
        grupos: dict[tuple[str, str], list[dict]] = {}
        for doc in docs:
            client_id = doc.get("client_id")
            if not client_id:
                continue
            ged_client_id = mapa_ged.get(str(client_id))
            if not ged_client_id:
                continue
            competencia = doc.get("competencia") or datetime.utcnow().strftime("%Y-%m")
            grupos.setdefault((ged_client_id, competencia), []).append(doc)

        for (ged_client_id, competencia), group_docs in grupos.items():
            try:
                ano, mes = competencia.split("-")
                ref_month = f"{ano}-{mes}-01"

                # Diretório físico
                storage_dir = os.path.join(GED_STORAGE_BASE, "historico", ged_client_id, competencia)
                os.makedirs(storage_dir, exist_ok=True)

                # Criar ou garantir kit (ON CONFLICT não altera nada mas retorna id)
                rows = _exec_write_sync(
                    "INSERT INTO ged_document_kits "
                    "(client_id, reference_month, status, notes) "
                    "VALUES (CAST(:cid AS uuid), CAST(:refm AS date), 'completo', "
                    "'Ingestão histórica — Google Drive') "
                    "ON CONFLICT (client_id, reference_month) DO UPDATE "
                    "SET updated_at = NOW() "
                    "RETURNING id::text",
                    {"cid": ged_client_id, "refm": ref_month},
                )
                if not rows:
                    erros_ged.append(f"Sem kit_id para {ged_client_id}/{competencia}")
                    continue
                kit_id = rows[0][0]

                # Salvar cada PDF
                for doc in group_docs:
                    try:
                        nome_pdf = doc["nome"]
                        pdf_bytes = doc.get("conteudo") or b""
                        tipo = doc.get("tipo") or "outros"

                        safe_name = f"{str(_uuid_mod.uuid4())[:8]}_{nome_pdf}"
                        rel_path = os.path.join("historico", ged_client_id, competencia, safe_name)
                        full_path = os.path.join(GED_STORAGE_BASE, rel_path)

                        with open(full_path, "wb") as fh:
                            fh.write(pdf_bytes)

                        _exec_write_sync(
                            "INSERT INTO ged_kit_documents "
                            "(kit_id, document_type, document_name, file_path, "
                            "file_size_bytes, mime_type, source_module, auto_generated) "
                            "VALUES (CAST(:kid AS uuid), :dtype, :dname, :fpath, "
                            ":fsize, 'application/pdf', 'historico_drive', TRUE)",
                            {
                                "kid": kit_id,
                                "dtype": tipo,
                                "dname": nome_pdf,
                                "fpath": rel_path,
                                "fsize": len(pdf_bytes),
                            },
                        )
                        salvos += 1
                    except Exception as exc:
                        erros_ged.append(f"{doc.get('nome', '?')}: {exc}")
                        logger.warning("GED persist doc error: %s", exc)

                # Atualizar contagem total no kit
                _exec_write_sync(
                    "UPDATE ged_document_kits "
                    "SET total_documents = ("
                    "  SELECT COUNT(*) FROM ged_kit_documents WHERE kit_id = CAST(:kid AS uuid)"
                    "), updated_at = NOW() "
                    "WHERE id = CAST(:kid AS uuid)",
                    {"kid": kit_id},
                )

            except Exception as exc:
                erros_ged.append(f"Kit {ged_client_id}/{competencia}: {exc}")
                logger.error("GED persist kit error: %s", exc)

        logger.info("GED persist: %d docs salvos, %d erros", salvos, len(erros_ged))
        return {"salvos": salvos, "erros": erros_ged}


# Singleton — compatível com o prompt original (sem db no construtor)
ingestao = IngestaoHistorica()


def get_status() -> dict:
    """Retorna snapshot do status atual da ingestão."""
    return dict(_status)
