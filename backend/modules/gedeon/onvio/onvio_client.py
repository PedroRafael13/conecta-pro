"""GEDEON Fase 3 — Onvio Client (T3)

Conecta ao Onvio API (software contábil Thompson Reuters) para baixar
documentos de folha, encargos e fiscal.

Credenciais configuradas via ENV:
  ONVIO_USERNAME  — usuário da empresa no portal Onvio
  ONVIO_PASSWORD  — senha
  ONVIO_BASE_URL  — base URL da API (default: https://api.onvio.com.br)
  ONVIO_COMPANY_ID — CNPJ / company ID no Onvio
"""

import logging
import os

import httpx
import redis

logger = logging.getLogger(__name__)

ONVIO_BASE_URL = os.getenv("ONVIO_BASE_URL", "https://api.onvio.com.br")
ONVIO_USERNAME = os.getenv("ONVIO_USERNAME", "")
ONVIO_PASSWORD = os.getenv("ONVIO_PASSWORD", "")
ONVIO_COMPANY_ID = os.getenv("ONVIO_COMPANY_ID", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SESSION_KEY = "onvio:session"
SESSION_TTL = 3600  # 1h


class OnvioClient:
    """
    Cliente HTTP para a API do Onvio.
    Mantém sessão em Redis. Renova automaticamente ao expirar.
    """

    def __init__(self):
        self._session_token: str | None = None
        self._redis = self._connect_redis()

    # ─── Redis ────────────────────────────────────────────────────────

    def _connect_redis(self):
        try:
            r = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
            r.ping()
            return r
        except Exception:
            logger.warning("OnvioClient: Redis indisponível — sessão apenas em memória")
            return None

    def _get_cached_session(self) -> str | None:
        if self._redis:
            try:
                return self._redis.get(SESSION_KEY)
            except Exception:
                pass
        return self._session_token

    def _cache_session(self, token: str) -> None:
        self._session_token = token
        if self._redis:
            try:
                self._redis.setex(SESSION_KEY, SESSION_TTL, token)
            except Exception:
                pass

    # ─── Auth ─────────────────────────────────────────────────────────

    def autenticar(self) -> str:
        """Autentica no Onvio e retorna token de sessão."""
        if not ONVIO_USERNAME or not ONVIO_PASSWORD:
            logger.warning("OnvioClient: credenciais não configuradas (ONVIO_USERNAME/PASSWORD)")
            return "sem-credenciais"

        try:
            resp = httpx.post(
                f"{ONVIO_BASE_URL}/api/v1/auth/login",
                json={
                    "username": ONVIO_USERNAME,
                    "password": ONVIO_PASSWORD,
                    "companyId": ONVIO_COMPANY_ID,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            token = data.get("token") or data.get("access_token", "")
            self._cache_session(token)
            logger.info("OnvioClient: autenticado com sucesso")
            return token
        except Exception as exc:
            logger.error("OnvioClient: erro na autenticação: %s", exc)
            raise

    def _token(self) -> str:
        token = self._get_cached_session()
        if not token:
            token = self.autenticar()
        return token

    def validar_sessao(self) -> bool:
        """Retorna True se há sessão válida em Redis."""
        cached = self._get_cached_session()
        return bool(cached and cached != "sem-credenciais")

    # ─── Documentos ───────────────────────────────────────────────────

    def listar_documentos_pasta(self, folder_id: str) -> list[dict]:
        """Lista documentos de uma pasta específica no Onvio."""
        token = self._token()
        try:
            resp = httpx.get(
                f"{ONVIO_BASE_URL}/api/v1/documents",
                params={"folderId": folder_id, "companyId": ONVIO_COMPANY_ID},
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("documents", data) if isinstance(data, dict) else data
        except Exception as exc:
            logger.error("OnvioClient: erro listar pasta %s: %s", folder_id, exc)
            return []

    def listar_todos_documentos(self) -> list[dict]:
        """Lista documentos de todas as pastas mapeadas."""
        from modules.gedeon.onvio.onvio_sync_service import FOLDER_MAP

        todos: list[dict] = []
        for folder_id, nome_pasta in FOLDER_MAP.items():
            docs = self.listar_documentos_pasta(folder_id)
            for d in docs:
                d.setdefault("_pasta", nome_pasta)
                d.setdefault("parentId", folder_id)
            todos.extend(docs)
            logger.debug("OnvioClient: pasta '%s' → %d docs", nome_pasta, len(docs))
        logger.info("OnvioClient: total de documentos encontrados: %d", len(todos))
        return todos

    def baixar_pdf(self, folder_id: str, doc_id: str) -> bytes:
        """Baixa o conteúdo binário de um documento PDF."""
        token = self._token()
        try:
            resp = httpx.get(
                f"{ONVIO_BASE_URL}/api/v1/documents/{doc_id}/download",
                params={"folderId": folder_id},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            logger.error("OnvioClient: erro download doc %s: %s", doc_id, exc)
            raise
