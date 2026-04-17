"""GEDEON Fase 3 — Onvio Sync Service"""

import logging
import time
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.models.onvio_models import FgtsGuia, InssGuia, OnvioDocument, OnvioSyncLog
from modules.gedeon.onvio.onvio_client import OnvioClient
from modules.gedeon.onvio.onvio_parser import classificar_documento

logger = logging.getLogger(__name__)
STORAGE_BASE = Path("/opt/conecta-pro/storage/onvio")

# Mapa de pastas Onvio → nome da categoria (IDs de pasta do portal Onvio)
# IDs não são segredos — são identificadores públicos de pastas do cliente  # pragma: allowlist secret
FOLDER_MAP = {
    "ed1872253de94cbfaada2ee0b8217a2c": "Encargos da Folha",  # pragma: allowlist secret
    "9d9d30601efd41d29b7708bfdf9febf6": "Folha de Pagamento",  # pragma: allowlist secret
    "58c0e7f322584741b52907632d79e683": "Rescisão",  # pragma: allowlist secret
    "a70de7ac1afc4793add90eb1ef6d2b1b": "Admissão",  # pragma: allowlist secret
    "b87638b642f14d7180a0696574428c59": "Recibo de Férias",  # pragma: allowlist secret
    "5c221841a5ec4fd5afcf6c052c7b7c7b": "Aviso Prévio de Férias",  # pragma: allowlist secret
    "9fec13524823450cadb2a863e715cfd0": "13º Salário",  # pragma: allowlist secret
    "f783c90e5ad84c3b82149ed44eee0e52": "Fiscal",  # pragma: allowlist secret
    "21954971a53c4cb4aeebd558f859ac7e": "Registro de Empresas",  # pragma: allowlist secret
}


class OnvioSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = OnvioClient()

    async def sync_completo(self, mes_ref: str | None = None) -> dict:
        """Sincroniza todos os documentos do Onvio. Se mes_ref=None, busca tudo."""
        inicio = time.time()
        log = OnvioSyncLog(mes_ref=mes_ref or "all", status="running")
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        try:
            todos_docs = self.client.listar_todos_documentos()
            novos = erros = 0

            for item in todos_docs:
                try:
                    onvio_id = item.get("id")
                    if await self._ja_importado(onvio_id):
                        continue
                    cl = classificar_documento(item)
                    if mes_ref and cl.mes_ref and cl.mes_ref != mes_ref:
                        continue
                    caminho = self._baixar_e_salvar(item, cl)
                    await self._salvar_db(item, cl, caminho)
                    novos += 1
                except Exception as e:
                    logger.error("Erro doc %s: %s", item.get("name"), e)
                    erros += 1

            log.status = "success" if erros == 0 else "partial"
            log.docs_baixados = novos + erros
            log.docs_novos = novos
            log.docs_erro = erros
            log.duracao_s = round(time.time() - inicio, 2)
            await self.db.commit()
            return {
                "status": log.status,
                "novos": novos,
                "erros": erros,
                "duracao": log.duracao_s,
            }

        except Exception as e:
            log.status = "error"
            log.detalhes = str(e)
            await self.db.commit()
            raise

    async def _ja_importado(self, onvio_id: str | None) -> bool:
        if not onvio_id:
            return False
        result = await self.db.execute(select(OnvioDocument).where(OnvioDocument.onvio_id == onvio_id))
        return result.scalar_one_or_none() is not None

    def _baixar_e_salvar(self, item: dict, cl) -> str:
        folder_id = item.get("parentId", item.get("containerId", ""))
        doc_id = item.get("id", str(uuid.uuid4()))
        mes = cl.mes_ref or "sem-ref"
        cat_dir = STORAGE_BASE / cl.categoria / mes
        cat_dir.mkdir(parents=True, exist_ok=True)
        nome = item.get("name", f"{doc_id}.pdf")
        caminho = cat_dir / nome
        pdf = self.client.baixar_pdf(folder_id, doc_id)
        caminho.write_bytes(pdf)
        return str(caminho)

    async def _salvar_db(self, item: dict, cl, caminho: str) -> None:
        doc = OnvioDocument(
            onvio_id=item.get("id", str(uuid.uuid4())),
            onvio_folder_id=item.get("parentId", ""),
            nome_arquivo=item.get("name", ""),
            categoria=cl.categoria,
            mes_ref=cl.mes_ref,
            caminho_local=caminho,
            data_onvio=item.get("createdDate"),
            processado=False,
        )
        self.db.add(doc)

        # Criar registros específicos por categoria
        if cl.categoria in ("fgts_guia", "fgts_consignado", "fgts_relatorio"):
            self.db.add(
                FgtsGuia(
                    mes_ref=cl.mes_ref or "",
                    tipo=cl.categoria.replace("fgts_", "").upper(),
                    arquivo_pdf=caminho,
                )
            )
        elif cl.categoria == "inss_guia":
            self.db.add(
                InssGuia(
                    mes_ref=cl.mes_ref or "",
                    arquivo_pdf=caminho,
                )
            )

        await self.db.commit()
