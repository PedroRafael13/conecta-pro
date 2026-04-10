"""
Conector Domínio Sistemas (Contabilidade TOTVS)

Integração com o sistema contábil Domínio Sistemas para sincronização
de lançamentos, plano de contas e funcionários.

Modo de operação:
- API_AVAILABLE=True: consome API REST quando disponível
- API_AVAILABLE=False: fallback para exportação de arquivos (DominioExporterAgent)

Configuração (.env):
    DOMINIO_API_KEY=<chave fornecida pelo contador>
    DOMINIO_API_URL=https://api.dominiosistemas.com.br
    DOMINIO_CNPJ=35710481000103
    DOMINIO_ENABLED=true
"""

import logging
import time
from typing import Any

import httpx

from core.config.settings import settings

logger = logging.getLogger(__name__)

API_KEY: str = settings.DOMINIO_API_KEY
API_URL: str = settings.DOMINIO_API_URL
DOMINIO_CNPJ: str = settings.DOMINIO_CNPJ
ENABLED: bool = settings.DOMINIO_ENABLED

TIMEOUT = 15.0
_CONNECTIVITY_CACHE: dict[str, Any] = {"checked_at": 0.0, "available": False}
_CACHE_TTL = 300  # 5 minutos


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CNPJ": DOMINIO_CNPJ,
    }


async def check_connectivity() -> dict[str, Any]:
    """
    Verifica se a API Domínio está acessível.
    Resultado em cache por 5 minutos.
    """
    now = time.monotonic()
    if now - _CONNECTIVITY_CACHE["checked_at"] < _CACHE_TTL:
        return {
            "available": _CONNECTIVITY_CACHE["available"],
            "cached": True,
        }

    result: dict[str, Any] = {
        "available": False,
        "cached": False,
        "url": API_URL,
        "error": None,
        "http_status": None,
    }

    if not ENABLED or not API_KEY:
        result["error"] = "Integração desabilitada ou sem chave configurada"
        _CONNECTIVITY_CACHE.update({"checked_at": now, "available": False})
        return result

    endpoints_to_try = [
        f"{API_URL}/v1/status",
        f"{API_URL}/v1/ping",
        f"{API_URL}/health",
        f"{API_URL}/",
    ]

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False) as client:
            for endpoint in endpoints_to_try:
                try:
                    resp = await client.get(endpoint, headers=_headers())
                    result["http_status"] = resp.status_code
                    result["endpoint_tested"] = endpoint
                    if resp.status_code < 500:
                        result["available"] = resp.status_code not in (0,)
                        if resp.status_code in (200, 201, 204):
                            result["available"] = True
                            break
                        elif resp.status_code == 401:
                            result["available"] = True  # API existe, mas chave inválida
                            result["error"] = "Chave API inválida ou expirada"
                            break
                        elif resp.status_code == 403:
                            result["available"] = True
                            result["error"] = "Sem permissão — verificar chave/CNPJ"
                            break
                except (httpx.ConnectError, httpx.TimeoutException):
                    continue
    except Exception as exc:
        result["error"] = str(exc)

    _CONNECTIVITY_CACHE.update({"checked_at": now, "available": result["available"]})
    return result


async def exportar_lancamentos(
    periodo: str,
    lancamentos: list[dict],
) -> dict[str, Any]:
    """
    Envia lançamentos contábeis ao Domínio.
    Tenta API REST; fallback para arquivo de exportação.

    Args:
        periodo: Período no formato YYYY-MM
        lancamentos: Lista de lançamentos contábeis
    """
    conn = await check_connectivity()

    if conn.get("available") and not conn.get("error"):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(
                    f"{API_URL}/v1/lancamentos",
                    headers=_headers(),
                    json={
                        "cnpj": DOMINIO_CNPJ,
                        "periodo": periodo,
                        "lancamentos": lancamentos,
                    },
                )
                if resp.status_code in (200, 201):
                    return {
                        "sucesso": True,
                        "modo": "api",
                        "total": len(lancamentos),
                        "periodo": periodo,
                        "resposta": resp.json(),
                    }
        except Exception as exc:
            logger.warning("[Domínio] Falha na API, usando exportação de arquivo: %s", exc)

    # Fallback: exportação de arquivo
    return _exportar_arquivo(periodo, lancamentos)


def _exportar_arquivo(periodo: str, lancamentos: list[dict]) -> dict[str, Any]:
    """Fallback: gera arquivo no formato Domínio para importação manual."""
    try:
        from modules.empresas.agents.dominio_exporter import DominioExporterAgent

        agent = DominioExporterAgent()
        resultado = agent.exportar_lancamentos("conecta", periodo, lancamentos)
        return {
            **resultado,
            "modo": "arquivo",
            "instrucao": (
                "API indisponível. Arquivo gerado para importação manual no Domínio. "
                "Encaminhar ao contador: Jordan Santos de Jesus Ltda (35.710.481/0001-03)"
            ),
        }
    except Exception as exc:
        logger.error("[Domínio] Falha no fallback de arquivo: %s", exc)
        return {"sucesso": False, "modo": "arquivo", "erro": str(exc)}


async def get_status() -> dict[str, Any]:
    """Retorna status completo da integração Domínio."""
    conn = await check_connectivity()
    return {
        "enabled": ENABLED,
        "api_key_configured": bool(API_KEY),
        "cnpj": DOMINIO_CNPJ,
        "api_url": API_URL,
        "api_available": conn.get("available", False),
        "api_error": conn.get("error"),
        "modo_operacao": "api" if conn.get("available") and not conn.get("error") else "arquivo",
        "ultimo_check": conn,
    }
