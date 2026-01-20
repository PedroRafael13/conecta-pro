"""Middleware de compressão para mobile."""

import gzip
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware de compressão adaptativa para mobile.

    Comprime respostas com base no tipo de conteúdo,
    tamanho e preferências do cliente.
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 1024,
        compression_level: int = 6,
        compress_types: set[str] = None,
    ) -> None:
        """
        Inicializa o middleware.

        Args:
            app: Aplicação ASGI
            minimum_size: Tamanho mínimo para compressão (bytes)
            compression_level: Nível de compressão gzip (1-9)
            compress_types: Content-types a comprimir
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.compress_types = compress_types or {
            "application/json",
            "text/plain",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/xml",
            "text/xml",
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Processa a requisição e comprime a resposta se apropriado."""
        # Verificar se cliente aceita gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        accepts_gzip = "gzip" in accept_encoding.lower()

        # Processar requisição
        response = await call_next(request)

        # Não comprimir se cliente não aceita gzip
        if not accepts_gzip:
            return response

        # Verificar content-type
        content_type = response.headers.get("content-type", "")
        base_type = content_type.split(";")[0].strip()

        if base_type not in self.compress_types:
            return response

        # Verificar se já está comprimido
        if response.headers.get("content-encoding"):
            return response

        # Coletar corpo da resposta
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Verificar tamanho mínimo
        if len(body) < self.minimum_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Comprimir
        compressed = gzip.compress(body, compresslevel=self.compression_level)

        # Só usar se realmente reduziu o tamanho
        if len(compressed) >= len(body):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Atualizar headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed))
        headers["vary"] = "Accept-Encoding"

        logger.debug(
            f"Compressed response: {len(body)} -> {len(compressed)} bytes "
            f"({(1 - len(compressed)/len(body)) * 100:.1f}% reduction)"
        )

        return Response(
            content=compressed,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )


async def compress_data(
    data: bytes,
    level: int = 6,
    minimum_size: int = 1024,
) -> tuple[bytes, bool]:
    """
    Comprime dados se valer a pena.

    Args:
        data: Dados a comprimir
        level: Nível de compressão (1-9)
        minimum_size: Tamanho mínimo para comprimir

    Returns:
        Tupla (dados, foi_comprimido)
    """
    if len(data) < minimum_size:
        return data, False

    compressed = gzip.compress(data, compresslevel=level)

    if len(compressed) < len(data):
        return compressed, True

    return data, False


async def decompress_data(data: bytes) -> bytes:
    """Descomprime dados gzip."""
    try:
        return gzip.decompress(data)
    except gzip.BadGzipFile:
        return data
