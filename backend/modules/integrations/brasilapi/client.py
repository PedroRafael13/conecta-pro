"""BrasilAPI async client with Redis cache + circuit breaker + retries."""

import asyncio
import re

import httpx

from .cache import RedisCache
from .circuit_breaker import _cb
from .exceptions import (
    BrasilAPIError,
    BrasilAPIInvalidFormatError,
    BrasilAPINotFoundError,
    BrasilAPIUnavailableError,
)
from .schemas import CEPResponse, CNPJResponse, Taxa

_BASE = "https://brasilapi.com.br/api"
_VIACEP_BASE = "https://viacep.com.br/ws"

TTL_CNPJ = 60 * 60 * 24 * 30  # 30d
TTL_CEP = 60 * 60 * 24 * 365  # 365d
TTL_TAXAS = 60 * 60 * 6  # 6h


def _normalize_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _validate_cnpj(cnpj: str) -> str:
    digits = _normalize_digits(cnpj)
    if len(digits) != 14:
        raise BrasilAPIInvalidFormatError(f"CNPJ deve ter 14 dígitos, recebido {len(digits)}")
    return digits


def _validate_cep(cep: str) -> str:
    digits = _normalize_digits(cep)
    if len(digits) != 8:
        raise BrasilAPIInvalidFormatError(f"CEP deve ter 8 dígitos, recebido {len(digits)}")
    return digits


class BrasilAPIClient:
    def __init__(self, timeout_seconds: float = 5.0):
        self._cache = RedisCache(prefix="brasilapi")
        self._timeout = timeout_seconds

    async def _request_with_retry(
        self,
        url: str,
        endpoint_key: str,
        max_retries: int = 2,
    ) -> dict:
        if _cb.is_open(endpoint_key):
            raise BrasilAPIUnavailableError(f"Circuit breaker open for {endpoint_key}")

        last_exc: Exception | None = None
        delay = 1.0

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    r = await client.get(url)

                if r.status_code == 200:
                    _cb.record_success(endpoint_key)
                    return r.json()
                if r.status_code == 404:
                    # 404 is a valid answer — not a circuit breaker trigger
                    _cb.record_success(endpoint_key)
                    raise BrasilAPINotFoundError(f"{endpoint_key}: 404")
                if 500 <= r.status_code < 600:
                    last_exc = BrasilAPIUnavailableError(f"{endpoint_key}: HTTP {r.status_code}")
                    raise last_exc
                raise BrasilAPIError(f"{endpoint_key}: HTTP {r.status_code}")

            except BrasilAPINotFoundError:
                raise
            except (
                httpx.TimeoutException,
                httpx.ConnectError,
                BrasilAPIUnavailableError,
            ) as e:
                last_exc = e
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                break

        _cb.record_failure(endpoint_key)
        raise BrasilAPIUnavailableError(f"{endpoint_key}: {last_exc}")

    async def get_cnpj(self, cnpj: str) -> tuple[CNPJResponse, bool]:
        """Returns (response, cache_hit)."""
        digits = _validate_cnpj(cnpj)
        cache_key = f"cnpj:{digits}"

        cached = await self._cache.get(cache_key)
        if cached is not None:
            return CNPJResponse(**cached), True

        data = await self._request_with_retry(
            f"{_BASE}/cnpj/v1/{digits}",
            endpoint_key="cnpj",
        )
        await self._cache.set(cache_key, data, ttl_seconds=TTL_CNPJ)
        return CNPJResponse(**data), False

    async def get_cep(self, cep: str) -> tuple[CEPResponse, bool]:
        """Returns (response, cache_hit). Falls back to ViaCEP if unavailable."""
        digits = _validate_cep(cep)
        cache_key = f"cep:{digits}"

        cached = await self._cache.get(cache_key)
        if cached is not None:
            return CEPResponse(**cached), True

        try:
            data = await self._request_with_retry(
                f"{_BASE}/cep/v2/{digits}",
                endpoint_key="cep",
            )
        except BrasilAPIUnavailableError:
            data = await self._fallback_viacep(digits)

        await self._cache.set(cache_key, data, ttl_seconds=TTL_CEP)
        return CEPResponse(**data), False

    async def _fallback_viacep(self, digits: str) -> dict:
        """ViaCEP fallback — normalize to BrasilAPI-like shape."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(f"{_VIACEP_BASE}/{digits}/json/")
        if r.status_code != 200 or r.json().get("erro"):
            raise BrasilAPIUnavailableError("ViaCEP fallback also failed")
        v = r.json()
        return {
            "cep": digits,
            "state": v.get("uf"),
            "city": v.get("localidade"),
            "neighborhood": v.get("bairro"),
            "street": v.get("logradouro"),
            "service": "viacep-fallback",
        }

    async def get_taxas(self) -> tuple[list[Taxa], bool]:
        """Returns (response, cache_hit)."""
        cache_key = "taxas:all"

        cached = await self._cache.get(cache_key)
        if cached is not None:
            return [Taxa(**t) for t in cached], True

        data = await self._request_with_retry(
            f"{_BASE}/taxas/v1",
            endpoint_key="taxas",
        )
        await self._cache.set(cache_key, data, ttl_seconds=TTL_TAXAS)
        return [Taxa(**t) for t in data], False
