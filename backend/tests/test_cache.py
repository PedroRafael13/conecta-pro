"""Testes para o sistema de cache Redis."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.cache.redis import (
    cache_clear_pattern,
    cache_delete,
    cache_get,
    cache_response,
    cache_set,
    close_redis,
    get_redis,
)


class TestGetRedis:
    """Testes para conexão Redis."""

    @pytest.mark.asyncio
    async def test_get_redis_creates_client(self):
        """Testa criação de cliente Redis."""
        with patch("core.cache.redis.redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client

            # Reset global client
            import core.cache.redis as cache_module

            cache_module.redis_client = None

            client = await get_redis()

            mock_redis.from_url.assert_called_once()
            assert client == mock_client

    @pytest.mark.asyncio
    async def test_get_redis_reuses_client(self):
        """Testa reutilização de cliente existente."""
        mock_client = AsyncMock()

        import core.cache.redis as cache_module

        cache_module._state["client"] = mock_client

        client = await get_redis()
        assert client == mock_client


class TestCloseRedis:
    """Testes para fechamento de conexão."""

    @pytest.mark.asyncio
    async def test_close_redis_closes_client(self):
        """Testa fechamento de cliente."""
        mock_client = AsyncMock()

        import core.cache.redis as cache_module

        cache_module._state["client"] = mock_client

        await close_redis()

        mock_client.close.assert_called_once()
        assert cache_module._state["client"] is None

    @pytest.mark.asyncio
    async def test_close_redis_no_client(self):
        """Testa fechamento sem cliente."""
        import core.cache.redis as cache_module

        cache_module._state["client"] = None

        # Não deve lançar erro
        await close_redis()
        assert cache_module._state["client"] is None


class TestCacheGet:
    """Testes para cache_get."""

    @pytest.mark.asyncio
    async def test_cache_get_returns_json(self):
        """Testa obtenção de valor JSON."""
        mock_client = AsyncMock()
        mock_client.get.return_value = '{"name": "test"}'

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_get("test_key")

            assert result == {"name": "test"}
            mock_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_get_returns_string(self):
        """Testa obtenção de valor string simples."""
        mock_client = AsyncMock()
        mock_client.get.return_value = "simple_value"

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_get("test_key")

            assert result == "simple_value"

    @pytest.mark.asyncio
    async def test_cache_get_returns_none(self):
        """Testa chave inexistente."""
        mock_client = AsyncMock()
        mock_client.get.return_value = None

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_get("missing_key")

            assert result is None

    @pytest.mark.asyncio
    async def test_cache_get_invalid_json(self):
        """Testa valor não-JSON."""
        mock_client = AsyncMock()
        mock_client.get.return_value = "not{json"

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_get("test_key")

            # Retorna string original se não for JSON válido
            assert result == "not{json"


class TestCacheSet:
    """Testes para cache_set."""

    @pytest.mark.asyncio
    async def test_cache_set_dict(self):
        """Testa armazenamento de dicionário."""
        mock_client = AsyncMock()

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_set("test_key", {"name": "test"}, ttl=60)

            assert result is True
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert call_args[0][0] == "test_key"
            assert call_args[0][1] == 60
            assert json.loads(call_args[0][2]) == {"name": "test"}

    @pytest.mark.asyncio
    async def test_cache_set_list(self):
        """Testa armazenamento de lista."""
        mock_client = AsyncMock()

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_set("test_key", [1, 2, 3], ttl=60)

            assert result is True
            call_args = mock_client.setex.call_args
            assert json.loads(call_args[0][2]) == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_cache_set_string(self):
        """Testa armazenamento de string."""
        mock_client = AsyncMock()

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_set("test_key", "value", ttl=60)

            assert result is True
            call_args = mock_client.setex.call_args
            assert call_args[0][2] == "value"

    @pytest.mark.asyncio
    async def test_cache_set_default_ttl(self):
        """Testa TTL default."""
        mock_client = AsyncMock()

        with (
            patch("core.cache.redis.get_redis", return_value=mock_client),
            patch("core.cache.redis.settings") as mock_settings,
        ):
            mock_settings.redis_ttl = 300

            await cache_set("test_key", "value")

            call_args = mock_client.setex.call_args
            assert call_args[0][1] == 300


class TestCacheDelete:
    """Testes para cache_delete."""

    @pytest.mark.asyncio
    async def test_cache_delete_success(self):
        """Testa remoção bem-sucedida."""
        mock_client = AsyncMock()
        mock_client.delete.return_value = 1

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_delete("test_key")

            assert result is True
            mock_client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_delete_not_found(self):
        """Testa remoção de chave inexistente."""
        mock_client = AsyncMock()
        mock_client.delete.return_value = 0

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_delete("missing_key")

            assert result is False


class TestCacheClearPattern:
    """Testes para cache_clear_pattern."""

    @pytest.mark.asyncio
    async def test_clear_pattern_with_keys(self):
        """Testa limpeza de padrão com chaves."""
        mock_client = AsyncMock()

        # Mock do scan_iter
        async def mock_scan_iter(match):
            for key in ["user:1", "user:2", "user:3"]:
                yield key

        mock_client.scan_iter = mock_scan_iter
        mock_client.delete.return_value = 3

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_clear_pattern("user:*")

            assert result == 3
            mock_client.delete.assert_called_once_with("user:1", "user:2", "user:3")

    @pytest.mark.asyncio
    async def test_clear_pattern_no_keys(self):
        """Testa limpeza de padrão sem chaves."""
        mock_client = AsyncMock()

        async def mock_scan_iter(match):
            return
            yield  # Generator vazio

        mock_client.scan_iter = mock_scan_iter

        with patch("core.cache.redis.get_redis", return_value=mock_client):
            result = await cache_clear_pattern("empty:*")

            assert result == 0
            mock_client.delete.assert_not_called()


class TestCacheResponseDecorator:
    """Testes para decorator cache_response."""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Testa cache hit."""
        with patch("core.cache.redis.cache_get") as mock_get:
            mock_get.return_value = {"cached": True}

            @cache_response(ttl=60)
            async def my_func():
                return {"fresh": True}

            result = await my_func()

            assert result == {"cached": True}

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Testa cache miss."""
        with patch("core.cache.redis.cache_get") as mock_get, patch("core.cache.redis.cache_set") as mock_set:
            mock_get.return_value = None

            @cache_response(ttl=60)
            async def my_func():
                return {"fresh": True}

            result = await my_func()

            assert result == {"fresh": True}
            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_error_get(self):
        """Testa erro ao buscar cache."""
        with patch("core.cache.redis.cache_get") as mock_get, patch("core.cache.redis.cache_set"):
            mock_get.side_effect = Exception("Redis error")

            @cache_response(ttl=60)
            async def my_func():
                return {"fresh": True}

            result = await my_func()

            # Deve retornar resultado mesmo com erro no cache
            assert result == {"fresh": True}

    @pytest.mark.asyncio
    async def test_cache_error_set(self):
        """Testa erro ao salvar cache."""
        with patch("core.cache.redis.cache_get") as mock_get, patch("core.cache.redis.cache_set") as mock_set:
            mock_get.return_value = None
            mock_set.side_effect = Exception("Redis error")

            @cache_response(ttl=60)
            async def my_func():
                return {"fresh": True}

            result = await my_func()

            # Deve retornar resultado mesmo com erro no cache
            assert result == {"fresh": True}

    @pytest.mark.asyncio
    async def test_cache_with_prefix(self):
        """Testa prefixo customizado."""
        with patch("core.cache.redis.cache_get") as mock_get, patch("core.cache.redis.cache_set") as mock_set:
            mock_get.return_value = None

            @cache_response(ttl=60, prefix="custom")
            async def my_func():
                return {"data": 1}

            await my_func()

            call_args = mock_set.call_args
            assert call_args[0][0].startswith("custom:")
