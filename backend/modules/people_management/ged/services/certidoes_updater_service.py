"""D5.4 — CertidoesUpdaterService: orquestra 5 clients §42.4 + atualiza ged_certidoes."""

import json
import logging
import os
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

EMPRESA_CNPJ = os.environ.get("EMPRESA_CNPJ", "35710481000103")

# Mapeamento document_type → (modulo, classe, metodo)
# certidao_negativa_inss usa CNDFederal (RFB unificada) — dedup via cache
CLIENTS_MAP: dict[str, tuple[str, str, str]] = {
    "certidao_negativa_fgts": (
        "modules.bidding.integrations.receita_federal.crf_client",
        "CRFFGTSClient",
        "consultar_crf",
    ),
    "certidao_negativa_federal": (
        "modules.bidding.integrations.receita_federal.cnd_client",
        "CNDFederalClient",
        "consultar_cnd",
    ),
    "certidao_negativa_inss": (
        "modules.bidding.integrations.receita_federal.cnd_client",
        "CNDFederalClient",
        "consultar_cnd",
    ),
    "certidao_negativa_trabalhista": (
        "modules.bidding.integrations.receita_federal.cndt_client",
        "CNDTTrabalhistaClient",
        "consultar_cndt",
    ),
    "certidao_negativa_estadual": (
        "modules.bidding.integrations.receita_federal.sefaz_am_client",
        "SefazAMClient",
        "consultar_cnd",
    ),
    "certidao_negativa_municipal": (
        "modules.bidding.integrations.receita_federal.prefeitura_manaus_client",
        "PrefeituraManausClient",
        "consultar_cnd",
    ),
}

# Validade padrao por tipo (dias) — usado quando client nao retorna data_validade
_VALIDADE_PADRAO: dict[str, int] = {
    "certidao_negativa_fgts": 30,
    "certidao_negativa_federal": 180,
    "certidao_negativa_inss": 180,
    "certidao_negativa_trabalhista": 180,
    "certidao_negativa_estadual": 180,
    "certidao_negativa_municipal": 180,
}


class CertidoesUpdaterService:
    """Orquestra 5 clients §42.4-compliant e atualiza ged_certidoes.

    Responsabilidades:
    - Consultar cada client de certidao para o CNPJ da empresa
    - Deduplicar chamadas (certidao_negativa_inss reusa resultado do federal)
    - Atualizar expiry_date, notes, alerta_ativo nas 6 rows de ged_certidoes
    - Retornar {certidoes_atualizadas, alertas_disparados, erros}

    Principio §42.4: regular=None NUNCA True via fallback. Nunca afirma
    regularidade baseado apenas em CNPJ ativo na RFB.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def executar(self, cnpj: str = EMPRESA_CNPJ) -> dict[str, Any]:
        """Consulta clients e atualiza ged_certidoes.

        Returns:
            dict com certidoes_atualizadas, alertas_disparados, erros
        """
        certidoes_atualizadas = 0
        alertas_disparados = 0
        erros: list[dict[str, Any]] = []

        # Cache in-memory: evita chamada duplicada para CNDFederal (federal + inss)
        _cache: dict[tuple[str, str, str], dict[str, Any]] = {}

        for doc_type, (mod_path, cls_name, method_name) in CLIENTS_MAP.items():
            cache_key = (mod_path, cls_name, method_name)
            try:
                if cache_key in _cache:
                    resultado = _cache[cache_key]
                    logger.debug("D5.4 dedup: reusando cache %s para %s", cls_name, doc_type)
                else:
                    resultado = await self._chamar_client(mod_path, cls_name, method_name, cnpj)
                    _cache[cache_key] = resultado

                row_info = await self._atualizar_certidao(doc_type, resultado)
                if row_info is None:
                    continue

                certidoes_atualizadas += 1
                alerta = self._deve_alertar(resultado, row_info["expiry_date"])
                await self._set_alerta(row_info["id"], alerta)
                if alerta:
                    alertas_disparados += 1

            except Exception as exc:
                logger.warning("D5.4 erro em %s: %s", doc_type, exc)
                erros.append({"document_type": doc_type, "erro": str(exc)})

        logger.info(
            "D5.4 CertidoesUpdater: atualizadas=%d alertas=%d erros=%d",
            certidoes_atualizadas,
            alertas_disparados,
            len(erros),
        )
        return {
            "certidoes_atualizadas": certidoes_atualizadas,
            "alertas_disparados": alertas_disparados,
            "erros": erros,
        }

    async def _chamar_client(
        self,
        mod_path: str,
        cls_name: str,
        method_name: str,
        cnpj: str,
    ) -> dict[str, Any]:
        """Importa, instancia e chama o client de certidao."""
        import importlib

        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        client = cls()
        try:
            return await getattr(client, method_name)(cnpj)
        finally:
            if hasattr(client, "close"):
                await client.close()

    async def _atualizar_certidao(self, doc_type: str, resultado: dict[str, Any]) -> dict[str, Any] | None:
        """UPDATE em ged_certidoes para o doc_type dado.

        Returns:
            {"id": str, "expiry_date": date | None} se row existir, None caso contrario
        """
        row = (
            (
                await self.db.execute(
                    text("SELECT id, expiry_date FROM ged_certidoes WHERE document_type = :dt LIMIT 1"),
                    {"dt": doc_type},
                )
            )
            .mappings()
            .first()
        )

        if not row:
            logger.debug("D5.4: sem row para %s — skip (nao cria)", doc_type)
            return None

        expiry = self._calcular_expiry_date(resultado, row.get("expiry_date"), doc_type)
        notes_text = json.dumps(
            {
                "fonte": resultado.get("fonte"),
                "situacao": resultado.get("situacao"),
                "regular": resultado.get("regular"),
                "cnpj_ativo_rfb": resultado.get("cnpj_ativo_rfb"),
                "validade_dias": resultado.get("validade_dias"),
                "consultado_em": resultado.get("consultado_em"),
                "nota": resultado.get("nota") or resultado.get("mensagem"),
            },
            ensure_ascii=False,
        )

        await self.db.execute(
            text("UPDATE ged_certidoes SET expiry_date = :expiry, notes = :notes, updated_at = NOW() WHERE id = :id"),
            {"expiry": expiry, "notes": notes_text, "id": str(row["id"])},
        )
        return {"id": str(row["id"]), "expiry_date": expiry}

    async def _set_alerta(self, cert_id: str, ativo: bool) -> None:
        await self.db.execute(
            text("UPDATE ged_certidoes SET alerta_ativo = :v WHERE id = :id"),
            {"v": ativo, "id": cert_id},
        )

    def _deve_alertar(self, resultado: dict[str, Any], expiry_date: date | None) -> bool:
        """alerta_ativo=True quando: irregular, indeterminado, ou vencendo em <30d."""
        regular = resultado.get("regular")
        if regular is False:
            return True
        if regular is None:
            return True  # indeterminado portal indisponivel — alerta preventivo
        if expiry_date is not None and expiry_date < date.today() + timedelta(days=30):
            return True
        return False

    def _calcular_expiry_date(
        self,
        resultado: dict[str, Any],
        atual: date | None,
        doc_type: str,
    ) -> date | None:
        """Calcula nova expiry_date a partir do resultado ou mantém atual."""
        validade_raw = resultado.get("data_validade")
        if validade_raw:
            try:
                return datetime.fromisoformat(str(validade_raw).split("T")[0]).date()
            except (ValueError, TypeError):
                pass
        validade_dias = resultado.get("validade_dias") or _VALIDADE_PADRAO.get(doc_type, 180)
        if validade_dias:
            return date.today() + timedelta(days=int(validade_dias))
        return atual
