"""
SOPHIA v2.0 — Subscriber de Eventos Cross-Módulo

Escuta eventos dos 8 módulos do escopo e indexa documentos automaticamente.
Módulos: dp, rh, ged, operacional, fiscal, contratos, licitacoes, financeiro
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Mapeamento: event_type_prefix → modulo
_MODULO_POR_EVENTO: dict[str, str] = {
    "dp.": "dp",
    "gp.funcionario": "dp",
    "gp.folha": "dp",
    "gp.holerite": "dp",
    "gp.ponto": "dp",
    "gp.ferias": "dp",
    "rh.": "rh",
    "gp.aso": "rh",
    "gp.treinamento": "rh",
    "gp.epi": "rh",
    "gp.advertencia": "rh",
    "ged.": "ged",
    "gedeon.": "ged",
    "certidao.": "ged",
    "operacional.": "operacional",
    "fiscal.": "fiscal",
    "nfse.": "fiscal",
    "contratos.": "contratos",
    "licitacoes.": "licitacoes",
    "financeiro.": "financeiro",
    "financial.": "financeiro",
    "billing.": "financeiro",
}

# Prefixos de eventos de todos os 8 módulos (para subscrição)
SOPHIA_EVENT_PREFIXES = [
    "dp.*",
    "rh.*",
    "ged.*",
    "gedeon.*",
    "operacional.*",
    "fiscal.*",
    "contratos.*",
    "licitacoes.*",
    "financeiro.*",
    "financial.*",
    "gp.funcionario.*",
    "gp.folha.*",
    "gp.holerite.*",
    "gp.aso.*",
    "gp.treinamento.*",
]


def _detectar_modulo_evento(event_type: str) -> str:
    """Detecta módulo a partir do tipo de evento."""
    et = event_type.lower()
    for prefix, modulo in _MODULO_POR_EVENTO.items():
        if et.startswith(prefix):
            return modulo
    return "ged"


def _extrair_texto_do_evento(event_type: str, payload: dict[str, Any]) -> str:
    """Extrai texto indexável do payload do evento."""
    partes = [event_type.replace(".", " ").replace("_", " ")]

    # Campos comuns
    for campo in (
        "nome",
        "name",
        "titulo",
        "descricao",
        "description",
        "tipo",
        "type",
        "documento_tipo",
        "document_type",
        "numero",
        "number",
        "referencia",
    ):
        val = payload.get(campo)
        if val and isinstance(val, str):
            partes.append(val)

    # Campos de valor monetário
    for campo in ("valor", "value", "amount", "total"):
        val = payload.get(campo)
        if val is not None:
            partes.append(f"valor {val}")

    # Competência e datas
    for campo in ("competencia", "data", "date", "vencimento", "vigencia"):
        val = payload.get(campo)
        if val and isinstance(val, str):
            partes.append(val)

    # Nomes de pessoas/clientes
    for campo in (
        "funcionario_nome",
        "employee_name",
        "cliente_nome",
        "client_name",
        "nome_funcionario",
        "nome_cliente",
    ):
        val = payload.get(campo)
        if val and isinstance(val, str):
            partes.append(val)

    # Módulo / origem
    for campo in ("modulo", "module", "origem", "source"):
        val = payload.get(campo)
        if val and isinstance(val, str):
            partes.append(val)

    return " ".join(str(p) for p in partes if p)


def _extrair_metadados_do_evento(
    event_type: str,
    payload: dict[str, Any],
    modulo: str,
) -> dict[str, Any]:
    """Extrai metadados estruturados do evento para indexação."""
    meta: dict[str, Any] = {
        "modulo": modulo,
        "event_type": event_type,
        "tipo": payload.get("tipo") or payload.get("type") or payload.get("document_type", ""),
        "competencia": payload.get("competencia", ""),
        "cliente_id": str(payload.get("client_id") or payload.get("cliente_id") or ""),
        "cliente_nome": payload.get("client_name") or payload.get("cliente_nome", ""),
        "funcionario_id": str(payload.get("funcionario_id") or payload.get("employee_id") or ""),
        "funcionario_nome": payload.get("funcionario_nome") or payload.get("employee_name", ""),
        "vencimento": payload.get("vencimento") or payload.get("validade") or payload.get("expiry_date", ""),
        "valor": payload.get("valor") or payload.get("value") or payload.get("amount"),
        "origem": "event_bus",
    }

    # Detectar impacto_folha
    impacto_modulos = {"dp", "rh", "ged", "financeiro"}
    impacto_tipos = {"holerite", "folha_pagamento", "rescisao", "crf_fgts", "cndt", "cnd", "certidao"}
    tipo_str = str(meta.get("tipo", "")).lower()
    meta["impacto_folha"] = (
        modulo in impacto_modulos or any(t in tipo_str for t in impacto_tipos) or bool(payload.get("impacto_folha"))
    )

    # Remover valores vazios
    return {k: v for k, v in meta.items() if v not in (None, "", [])}


async def processar_evento_sophia(event: Any) -> bool:
    """
    Callback para processar eventos e indexar no SOPHIA v2.0.
    Compatível com ConectaEvent e dicts.
    """
    try:
        from modules.gedeon.agents.sophia import sophia

        # Normalizar evento
        if hasattr(event, "event_type"):
            event_type = event.event_type
            payload = event.payload if hasattr(event, "payload") else {}
            _source_module = getattr(event, "source_module", "")
            funcionario_id = getattr(event, "funcionario_id", None)
            cliente_id = getattr(event, "cliente_id", None)
            competencia = getattr(event, "competencia", None)
        elif isinstance(event, dict):
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})
            _source_module = event.get("source_module", "")
            funcionario_id = event.get("funcionario_id")
            cliente_id = event.get("cliente_id")
            competencia = event.get("competencia")
        else:
            return False

        if not event_type:
            return False

        # Detectar módulo
        modulo = _detectar_modulo_evento(event_type)

        # Extrair texto e metadados
        if isinstance(payload, str):
            import json

            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}

        texto = _extrair_texto_do_evento(event_type, payload)
        if not texto or len(texto.strip()) < 5:
            return False

        meta = _extrair_metadados_do_evento(event_type, payload, modulo)

        # Enriquecer com campos do evento de nível superior
        if funcionario_id:
            meta["funcionario_id"] = str(funcionario_id)
        if cliente_id:
            meta["cliente_id"] = str(cliente_id)
        if competencia:
            meta["competencia"] = competencia

        # Gerar doc_id único baseado no evento
        event_id = (
            getattr(event, "event_id", None) or (event.get("event_id") if isinstance(event, dict) else None) or ""
        )
        doc_id = f"evt_{modulo}_{event_type.replace('.', '_')}_{event_id[:8] if event_id else 'auto'}"

        # Indexar
        ok = sophia.indexar_documento(doc_id=doc_id, texto=texto, metadados=meta)
        if ok:
            logger.debug("SOPHIA subscriber: indexado evento %s → %s", event_type, doc_id)
        return ok

    except Exception as e:
        logger.warning("SOPHIA subscriber erro: %s", e)
        return False


def registrar_subscriber(event_bus: Any) -> None:
    """
    Registra SOPHIA como subscriber no event bus para todos os 8 módulos.
    Chama esta função no startup da aplicação.
    """
    import asyncio

    def _sync_callback(event: Any) -> None:
        """Wrapper síncrono para o callback assíncrono."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(processar_evento_sophia(event))
            else:
                loop.run_until_complete(processar_evento_sophia(event))
        except Exception as e:
            logger.debug("SOPHIA subscriber callback erro: %s", e)

    patterns = [
        "dp.*",
        "rh.*",
        "ged.*",
        "gedeon.*",
        "operacional.*",
        "fiscal.*",
        "contratos.*",
        "licitacoes.*",
        "financeiro.*",
        "financial.*",
        "gp.funcionario.*",
        "gp.folha.*",
        "gp.aso.*",
        "gp.treinamento.*",
        "gp.holerite.*",
    ]

    registered = 0
    for pattern in patterns:
        try:
            if hasattr(event_bus, "subscribe"):
                event_bus.subscribe(pattern, _sync_callback)
                registered += 1
        except Exception as e:
            logger.debug("SOPHIA: não foi possível registrar pattern %s: %s", pattern, e)

    logger.info("SOPHIA v2.0 subscriber: %d padrões registrados no event bus", registered)
