"""
Servico de Ingestao Historica — GED.

Varre a pasta Google Drive de kits historicos, extrai texto de PDFs
dentro de ZIPs e alimenta o indice SOPHIA para busca semantica.

Estrategia de extracao de texto:
- Primaria: PyMuPDF (fitz) — rapido, preciso
- Fallback: PyPDF2 3.0.1 — compatibilidade

KITS_FOLDER_ID: ID da pasta raiz no Google Drive com os ZIPs historicos.
"""

import io
import logging
import os
import re
import zipfile
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

KITS_FOLDER = os.environ.get("GDRIVE_KITS_FOLDER_ID", "1jRBw8XG4lJjm0y5oSg9_H-M3QQcGy9Ck")

# Estado in-memory do processo de ingestao
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
# Helpers de extracao de texto
# ---------------------------------------------------------------------------


def _extrair_texto_fitz(conteudo: bytes) -> str:
    """Extrai texto de PDF usando PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=conteudo, filetype="pdf")
        partes: list[str] = []
        for page in doc:
            partes.append(page.get_text())
        doc.close()
        return " ".join(partes).strip()
    except Exception as e:
        logger.debug("fitz falhou: %s", e)
        return ""


def _extrair_texto_pypdf2(conteudo: bytes) -> str:
    """Extrai texto de PDF usando PyPDF2 (fallback)."""
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        partes: list[str] = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                partes.append(txt)
        return " ".join(partes).strip()
    except Exception as e:
        logger.debug("PyPDF2 falhou: %s", e)
        return ""


def extrair_texto_pdf(conteudo: bytes) -> str:
    """Extrai texto de PDF — PyMuPDF primario, PyPDF2 fallback."""
    texto = _extrair_texto_fitz(conteudo)
    if not texto:
        texto = _extrair_texto_pypdf2(conteudo)
    return texto


# ---------------------------------------------------------------------------
# Classificacao por nome de arquivo
# ---------------------------------------------------------------------------

_PADROES_TIPO: list[tuple] = [
    (r"holerite|folha|salario|pagamento", "holerite"),
    (r"rescisao|termina|demissao|TRCT", "rescisao"),
    (r"ferias|descanso", "ferias"),
    (r"certidao|CNDT|CND|CRF|FGTS|SEFIP", "certidao"),
    (r"contrato|admissao|admissao", "contrato"),
    (r"aso|exame|medico|pcmso", "aso"),
    (r"nfse|nota.?fiscal|NFS", "nfse"),
    (r"gps|guia|inss|previdencia", "guia_inss"),
    (r"grf|gfip|fgts", "guia_fgts"),
    (r"decl|declaracao|informe", "declaracao"),
    (r"crachá|cracha|identidade|rg|cpf", "identificacao"),
]


def classificar_documento(nome_arquivo: str, conteudo_bytes: bytes = b"") -> dict:
    """Classifica documento por padrao no nome do arquivo."""
    nome_lower = nome_arquivo.lower()
    for padrao, tipo in _PADROES_TIPO:
        if re.search(padrao, nome_lower, re.IGNORECASE):
            return {"tipo": tipo, "confianca": "alto"}
    return {"tipo": "outro", "confianca": "baixo"}


def extrair_mes_do_nome_zip(nome_zip: str) -> str | None:
    """
    Extrai competencia (YYYY-MM) do nome do ZIP.

    Exemplos aceitos:
      kits_2025_01.zip  → 2025-01
      KIT_JAN_2025.zip  → 2025-01
      2024-12_folha.zip → 2024-12
    """
    # Formato YYYY-MM ou YYYY_MM
    m = re.search(r"(\d{4})[-_](\d{2})", nome_zip)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    # Formato mes abreviado PT
    meses = {
        "jan": "01",
        "fev": "02",
        "mar": "03",
        "abr": "04",
        "mai": "05",
        "jun": "06",
        "jul": "07",
        "ago": "08",
        "set": "09",
        "out": "10",
        "nov": "11",
        "dez": "12",
    }
    m2 = re.search(r"(\d{4}).*?(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)", nome_zip, re.IGNORECASE)
    if m2:
        return f"{m2.group(1)}-{meses[m2.group(2).lower()]}"

    m3 = re.search(r"(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez).*?(\d{4})", nome_zip, re.IGNORECASE)
    if m3:
        return f"{m3.group(2)}-{meses[m3.group(1).lower()]}"

    return None


# ---------------------------------------------------------------------------
# Drive helpers (sync, executados em executor)
# ---------------------------------------------------------------------------


def _listar_zips_na_pasta(service, folder_id: str) -> list[dict]:
    """Lista todos os arquivos ZIP dentro de uma pasta do Drive."""
    query = f"'{folder_id}' in parents and mimeType='application/zip' and trashed=false"
    result = (
        service.files()
        .list(
            q=query,
            fields="files(id, name, size, modifiedTime)",
            pageSize=100,
        )
        .execute()
    )
    return result.get("files", [])


def _baixar_arquivo(service, file_id: str) -> bytes:
    """Baixa conteudo de um arquivo do Google Drive."""
    from googleapiclient.http import MediaIoBaseDownload

    buf = io.BytesIO()
    request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class IngestaoHistorica:
    """
    Processa ZIPs historicos do Google Drive e alimenta SOPHIA.

    Uso:
        ingestao = IngestaoHistorica(db)
        resultado = await ingestao.processar_todos_os_zips()
    """

    def __init__(self, db: Any) -> None:
        self.db = db

    def _get_drive(self):
        from modules.people_management.ged.services.google_drive_service import _get_drive_service

        service = _get_drive_service()
        if not service:
            raise RuntimeError("Google Drive nao configurado — verifique GOOGLE_DRIVE_CREDENTIALS")
        return service

    async def processar_zip(self, zip_id: str, zip_nome: str, conteudo_zip: bytes) -> dict:
        """
        Processa um unico ZIP:
        - extrai PDFs
        - classifica cada PDF
        - extrai texto
        - indexa no SOPHIA
        """
        from modules.gedeon.agents.sophia import sophia

        competencia = extrair_mes_do_nome_zip(zip_nome) or datetime.utcnow().strftime("%Y-%m")
        pdfs_ok = 0
        erros_zip: list[str] = []

        try:
            with zipfile.ZipFile(io.BytesIO(conteudo_zip), "r") as zf:
                nomes_pdf = [n for n in zf.namelist() if n.lower().endswith(".pdf")]
                for nome_pdf in nomes_pdf:
                    try:
                        conteudo_pdf = zf.read(nome_pdf)
                        texto = extrair_texto_pdf(conteudo_pdf)
                        if not texto:
                            texto = f"Documento: {nome_pdf}"

                        classificacao = classificar_documento(nome_pdf)
                        nome_base = os.path.basename(nome_pdf)

                        meta = {
                            "fonte": "ingestao_historica",
                            "zip_id": zip_id,
                            "zip_nome": zip_nome,
                            "nome_pdf": nome_base,
                            "competencia": competencia,
                            "tipo": classificacao["tipo"],
                        }

                        doc_id = f"hist_{zip_id}_{nome_base}"
                        sophia.indexar_documento(doc_id, texto, meta)
                        pdfs_ok += 1

                    except Exception as e:
                        erros_zip.append(f"{nome_pdf}: {e}")
                        logger.warning("Erro ao processar PDF %s no ZIP %s: %s", nome_pdf, zip_nome, e)

        except zipfile.BadZipFile as e:
            erros_zip.append(f"ZIP corrompido: {e}")
            logger.error("ZIP invalido %s: %s", zip_nome, e)

        return {"pdfs_indexados": pdfs_ok, "erros": erros_zip}

    async def processar_todos_os_zips(self, folder_id: str = KITS_FOLDER) -> dict:
        """
        Lista todos os ZIPs na pasta do Drive e processa cada um.

        Returns:
            Resumo com total_zips, pdfs_extraidos, docs_indexados, erros.
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
            service = self._get_drive()
        except RuntimeError as e:
            _status["em_andamento"] = False
            _status["erros"].append(str(e))
            return {"ok": False, "erro": str(e)}

        import asyncio

        loop = asyncio.get_event_loop()

        # Listar ZIPs em thread (API sincrona)
        zips = await loop.run_in_executor(None, _listar_zips_na_pasta, service, folder_id)
        _status["total_zips"] = len(zips)
        logger.info("INGESTAO: %d ZIPs encontrados na pasta %s", len(zips), folder_id)

        total_pdfs = 0
        total_indexados = 0

        for arquivo in zips:
            zip_id = arquivo["id"]
            zip_nome = arquivo["name"]
            _status["ultimo_zip"] = zip_nome

            try:
                conteudo = await loop.run_in_executor(None, _baixar_arquivo, service, zip_id)
                resultado = await self.processar_zip(zip_id, zip_nome, conteudo)
                total_pdfs += resultado["pdfs_indexados"]
                total_indexados += resultado["pdfs_indexados"]
                _status["zips_processados"] += 1
                _status["pdfs_extraidos"] += resultado["pdfs_indexados"]
                _status["docs_indexados"] += resultado["pdfs_indexados"]
                if resultado["erros"]:
                    _status["erros"].extend(resultado["erros"])
                logger.info(
                    "INGESTAO: %s — %d PDFs indexados",
                    zip_nome,
                    resultado["pdfs_indexados"],
                )
            except Exception as e:
                _status["erros"].append(f"{zip_nome}: {e}")
                logger.error("Erro ao processar ZIP %s: %s", zip_nome, e)

        # Persistir novos docs no banco
        try:
            from modules.gedeon.agents.sophia import sophia

            await sophia.indexar_acervo_completo()
            logger.info("INGESTAO: SOPHIA reindexado com %d docs historicos", total_indexados)
        except Exception as e:
            logger.warning("INGESTAO: falha ao persistir no banco: %s", e)

        _status["em_andamento"] = False
        _status["concluido_em"] = datetime.utcnow().isoformat()

        return {
            "ok": True,
            "total_zips": len(zips),
            "zips_processados": _status["zips_processados"],
            "pdfs_extraidos": total_pdfs,
            "docs_indexados": total_indexados,
            "erros": len(_status["erros"]),
        }


def get_status() -> dict:
    """Retorna snapshot do status atual da ingestao."""
    return dict(_status)
