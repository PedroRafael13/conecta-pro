"""
GEDEON Fase 3 — Onvio HTTP Client
Usa cookies do Redis para autenticação. TTL gerenciado por onvio_auth.py.
"""

import json
import os

import redis
import requests

ONVIO_BASE = "https://onvio.com.br"
CLIENT_ID = "92A4D531C6314E309B62FDF3D9F1359C"
REDIS_KEY = "onvio:session"


class OnvioClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis = redis.from_url(redis_url)
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
            }
        )

    def _load_session(self) -> bool:
        raw = self._redis.get(REDIS_KEY)
        if not raw:
            raise RuntimeError("Sessão Onvio não encontrada no Redis. Execute onvio_auth.py.")
        d = json.loads(raw)
        for name, value in d.get("cookies", {}).items():
            self._session.cookies.set(name, value, domain="onvio.com.br")
        self._session.headers["UDS-Session-Token"] = d.get("uds_token", "")
        return True

    def _get(self, path: str, params: dict = None) -> dict:
        self._load_session()
        url = f"{ONVIO_BASE}{path}"
        resp = self._session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def listar_documentos(self, folder_id: str | None = None, page: int = 1, page_size: int = 100) -> dict:
        params = {"from": page, "pageSize": page_size, "loadPermission": "true", "readByClientUser": ""}
        if folder_id:
            params["parentIds"] = folder_id
        else:
            params["customFields"] = json.dumps([{"name": "clientId", "value": CLIENT_ID, "ignoreCase": True}])
        return self._get("/api/storage/v1/containers/documents", params)

    def listar_todos_documentos(self) -> list:
        """Pagina automaticamente até buscar todos os documentos."""
        todos = []
        page = 1
        while True:
            data = self.listar_documentos(page=page, page_size=100)
            items = data.get("data", {}).get("items", [])
            todos.extend(items)
            if not data.get("data", {}).get("hasMore", False):
                break
            page += 1
        return todos

    def baixar_pdf(self, folder_id: str, doc_id: str) -> bytes:
        self._load_session()
        url = f"{ONVIO_BASE}/api/storage/v1/Folders/{folder_id}/documents/{doc_id}"
        resp = self._session.get(url, timeout=60)
        resp.raise_for_status()
        return resp.content

    def get_tree(self, count_docs: bool = True) -> dict:
        return self._get(
            "/api/storage/v1/containers/tree",
            {"clientId": CLIENT_ID, "includeOrphans": "true", "countDocuments": str(count_docs).lower()},
        )

    def validar_sessao(self) -> bool:
        try:
            self._load_session()
            resp = self._session.get(f"{ONVIO_BASE}/api/security/v1/session-and-bindings", timeout=10)
            return resp.status_code == 200
        except Exception:
            return False
