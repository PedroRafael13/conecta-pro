# 📊 RELATÓRIO DE CONFIGURAÇÃO DE CACHE (Redis)

**Projeto:** Conecta PRO
**Stack:** Redis 7 (Cache + Celery Broker)
**Data:** 2026-02-05

---

## 1. Uso Atual do Redis

### Funcionalidades Implementadas

| Funcionalidade | Status | Configuração |
|---------------|--------|--------------|
| Cache de respostas API | ✅ | `@cache_response` decorator |
| Celery Broker | ✅ | Redis DB 0 |
| Celery Result Backend | ✅ | `result_expires=86400` (24h) |
| Health Check | ✅ | Latência no `/health` |
| Conexão Async | ✅ | `redis.asyncio` com pool |

### Funcionalidades NÃO Implementadas

| Funcionalidade | Status | Impacto |
|---------------|--------|---------|
| Cache de dados de referência | ❌ | Consultas desnecessárias ao PG |
| Blacklist de tokens JWT | ❌ | Problema em multi-instância |
| Cache de sessões | ❌ | Validação JWT a cada request |
| Cache warming | ❌ | Cold cache após restart |
| Invalidação seletiva | ⚠️ Parcial | Apenas `cache_clear_pattern` |

---

## 2. Cache Atual (@cache_response)

### Controllers Cacheados

```python
# modules/operacional/controllers/

# scale_controller.py
@cache_response(ttl=180, prefix="api:scale")  # 3 minutos

# post_controller.py
@cache_response(ttl=300, prefix="api:post")  # 5 minutos

# scale_template_controller.py
@cache_response(ttl=300)

# time_bank_controller.py
@cache_response(ttl=240)

# occurrence_controller.py
@cache_response(ttl=180)

# disciplinary_controller.py
@cache_response(ttl=240)
```

### Configuração

```python
# core/config/settings.py

class Settings(BaseSettings):
    # Redis URLs
    redis_url: str = "redis://localhost:6379/1"  # Cache
    redis_celery_url: str = "redis://localhost:6379/0"  # Celery
    redis_ttl: int = 3600  # 1 hora padrão

    # TTLs específicos
    cache_ttl_scale: int = 180
    cache_ttl_post: int = 300
    cache_ttl_occurrence: int = 180
```

---

## 3. Oportunidades de Cache

### Prioridade 1: Configurações do Sistema

**Problema:** Configurações consultadas frequentemente, sempre do banco.

```python
# modules/config/services/config_service.py

from core.cache.redis import cache_get, cache_set, cache_delete

class ConfigService:
    CACHE_TTL = 3600  # 1 hora

    async def get_system_config_value(
        self,
        chave: str,
        default: Any = None
    ) -> Any:
        # 1. Tentar cache
        cache_key = f"config:system:{chave}"
        cached = await cache_get(cache_key)

        if cached is not None:
            return cached

        # 2. Buscar do banco
        config = await self.repository.get_by_key(chave)
        value = config.typed_value if config else default

        # 3. Salvar no cache
        if config and config.cacheable:
            await cache_set(cache_key, value, ttl=self.CACHE_TTL)

        return value

    async def update_system_config(
        self,
        config_id: UUID,
        value: Any
    ):
        # Atualizar no banco
        config = await self.repository.update(config_id, value)

        # Invalidar cache
        await cache_delete(f"config:system:{config.chave}")

        return config
```

**Impacto:**
- Redução de ~1000 queries/hora para configs
- Tempo de resposta: ~50ms → ~2ms

---

### Prioridade 2: Dados de Referência

```python
# core/cache/reference_data.py

from functools import lru_cache
from core.cache.redis import cache_response

class ReferenceDataCache:
    """Cache para dados de referência (UF, cidades, etc.)"""

    @staticmethod
    @cache_response(ttl=86400, prefix="ref:estados")  # 24h
    async def get_estados() -> List[EstadoSchema]:
        """Lista de estados brasileiros."""
        return await repository.get_all_estados()

    @staticmethod
    @cache_response(ttl=86400, prefix="ref:municipios")
    async def get_municipios_by_uf(uf: str) -> List[MunicipioSchema]:
        """Municípios por UF."""
        return await repository.get_municipios_by_uf(uf)

    @staticmethod
    @cache_response(ttl=3600, prefix="ref:cargos")
    async def get_cargos() -> List[CargoSchema]:
        """Cargos de funcionários."""
        return await repository.get_all_cargos()

    @staticmethod
    @cache_response(ttl=86400, prefix="ref:tipos_contrato")
    async def get_tipos_contrato() -> List[TipoContratoSchema]:
        """Tipos de contrato."""
        return await repository.get_tipos_contrato()

# Uso em controllers
@router.get("/estados")
async def list_estados():
    return await ReferenceDataCache.get_estados()

@router.get("/municipios/{uf}")
async def list_municipios(uf: str):
    return await ReferenceDataCache.get_municipios_by_uf(uf)
```

**Impacto:**
- Redução de ~500 queries/hora
- Dados imutáveis (quase) nunca mais consultam banco

---

### Prioridade 3: Feature Flags

```python
# modules/config/services/config_service.py

class ConfigService:
    FLAG_CACHE_TTL = 300  # 5 minutos

    async def evaluate_flag_cached(
        self,
        codigo: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Avalia feature flag com cache.
        """
        # Chave de cache inclui tenant e usuário
        cache_key = f"flag:{codigo}:t{tenant_id}:u{user_id}"

        # Tentar cache
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached["enabled"], cached.get("variant")

        # Avaliar
        enabled, variant = await self.evaluate_flag(
            codigo, tenant_id, user_id
        )

        # Salvar no cache
        await cache_set(
            cache_key,
            {"enabled": enabled, "variant": variant},
            ttl=self.FLAG_CACHE_TTL
        )

        return enabled, variant

    async def invalidate_flag_cache(self, codigo: str):
        """Invalida cache de uma flag específica."""
        pattern = f"flag:{codigo}:*"
        await cache_clear_pattern(pattern)
```

**Impacto:**
- Redução de ~2000 avaliações/hora
- Resposta instantânea para flags

---

### Prioridade 4: JWT Blacklist

```python
# core/auth/jwt.py

from core.cache.redis import redis_client

class JWTService:
    BLACKLIST_TTL = 86400 * 7  # 7 dias (tempo do refresh token)

    async def revoke_token(self, token: str, token_type: str = "access"):
        """Adiciona token à blacklist."""
        jti = self.get_jti(token)
        cache_key = f"jwt:blacklist:{jti}"

        await redis_client.setex(
            cache_key,
            self.BLACKLIST_TTL,
            "revoked"
        )

    async def is_token_revoked(self, token: str) -> bool:
        """Verifica se token está na blacklist."""
        jti = self.get_jti(token)
        cache_key = f"jwt:blacklist:{jti}"

        revoked = await redis_client.get(cache_key)
        return revoked is not None

    async def validate_token_cached(self, token: str) -> Dict:
        """Valida token com cache de decode."""
        # Usar hash do token como chave
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        cache_key = f"jwt:decode:{token_hash}"

        # Tentar cache (5 minutos)
        cached = await cache_get(cache_key)
        if cached:
            return cached

        # Validar
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Salvar no cache
        await cache_set(cache_key, payload, ttl=300)

        return payload
```

**Impacto:**
- Suporte a logout em múltiplas instâncias
- Cache de validação JWT: ~10ms → ~1ms

---

## 4. Estratégia de Invalidação

### Padrão de Invalidação

```python
# core/cache/invalidation.py

class CacheInvalidator:
    """Gerencia invalidação de cache."""

    INVALIDATION_RULES = {
        # Entidade -> Padrões de chave a invalidar
        "client": ["api:clients:*", "api:dashboard:*"],
        "employee": ["api:employees:*", "api:dashboard:*", "api:escalas:*"],
        "scale": ["api:scales:*", "api:dashboard:*", "api:kpis:*"],
        "occurrence": ["api:occurrences:*", "api:dashboard:*"],
        "post": ["api:posts:*", "api:dashboard:*"],
        "config": ["config:*", "api:config:*"],
    }

    async def invalidate_entity(self, entity_type: str, entity_id: Optional[str] = None):
        """Invalida cache de uma entidade."""
        patterns = self.INVALIDATION_RULES.get(entity_type, [])

        for pattern in patterns:
            if entity_id:
                # Invalidar específico + lista
                await cache_delete(f"{pattern}:{entity_id}")
            await cache_clear_pattern(pattern)

    async def invalidate_tenant(self, tenant_id: str):
        """Invalida todo cache de um tenant."""
        pattern = f"*:{tenant_id}:*"
        await cache_clear_pattern(pattern)

# Uso em repositories
class ClientRepository:
    async def update(self, client_id: UUID, data: dict):
        # Atualizar no banco
        client = await self._update_db(client_id, data)

        # Invalidar cache
        await CacheInvalidator().invalidate_entity("client", str(client_id))

        return client
```

---

## 5. Cache Warming

```python
# tasks/cache_warming.py

from celery_app import celery_app

@celery_app.task(queue='maintenance')
def warm_reference_data_cache():
    """Pré-carrega dados de referência no cache."""
    import asyncio
    asyncio.run(_warm_cache())

async def _warm_cache():
    # Dados críticos
    await ReferenceDataCache.get_estados()
    await ReferenceDataCache.get_cargos()
    await ReferenceDataCache.get_tipos_contrato()

    # Configurações frequentes
    config_service = ConfigService()
    await config_service.get_system_config_value("app_name")
    await config_service.get_system_config_value("app_version")

    logger.info("Cache warming completed")

# Agendar na inicialização
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Warming a cada 6 horas
    sender.add_periodic_task(
        21600,  # 6 horas
        warm_reference_data_cache.s(),
        name='warm-reference-data-cache'
    )
```

---

## 6. Métricas e Monitoramento

### Métricas de Cache

```python
# core/monitoring/cache_metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Métricas
cache_hits = Counter(
    'cache_hits_total',
    'Total de cache hits',
    ['cache_name', 'key_pattern']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total de cache misses',
    ['cache_name', 'key_pattern']
)

cache_latency = Histogram(
    'cache_operation_duration_seconds',
    'Latência de operações de cache',
    ['operation']  # get, set, delete
)

cache_size = Gauge(
    'cache_entries_count',
    'Número de entradas no cache',
    ['cache_name']
)

# Decorator com métricas
def cached_with_metrics(ttl: int, prefix: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{generate_key(*args, **kwargs)}"

            with cache_latency.labels(operation='get').time():
                cached = await cache_get(cache_key)

            if cached is not None:
                cache_hits.labels(
                    cache_name=prefix,
                    key_pattern=prefix
                ).inc()
                return cached

            cache_misses.labels(
                cache_name=prefix,
                key_pattern=prefix
            ).inc()

            result = await func(*args, **kwargs)

            with cache_latency.labels(operation='set').time():
                await cache_set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
```

### Alertas

```yaml
# alertmanager rules
rules:
  - alert: CacheHitRatioLow
    expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Cache hit ratio baixo"

  - alert: CacheLatencyHigh
    expr: histogram_quantile(0.95, rate(cache_operation_duration_seconds_bucket[5m])) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Latência de cache alta"
```

---

## 7. Checklist de Implementação

### Semana 1
- [ ] Implementar cache em `ConfigService`
- [ ] Criar `ReferenceDataCache`
- [ ] Adicionar cache para estados/cidades
- [ ] Testar invalidação

### Semana 2
- [ ] Implementar cache para feature flags
- [ ] Implementar JWT blacklist
- [ ] Criar `CacheInvalidator`
- [ ] Adicionar invalidação em repositories

### Semana 3
- [ ] Implementar cache warming
- [ ] Adicionar métricas Prometheus
- [ ] Configurar alertas
- [ ] Documentar estratégia

---

## 8. Resumo de TTLs Recomendados

| Dado | TTL | Justificativa |
|------|-----|---------------|
| Configurações sistema | 1h | Mudam raramente |
| Feature flags | 5min | Mudam ocasionalmente |
| Estados/UF | 24h | Quase nunca mudam |
| Municípios | 24h | Quase nunca mudam |
| Cargos | 1h | Mudam raramente |
| Dashboard | 1min | Dados dinâmicos |
| KPIs | 5min | Dados semi-estáticos |
| Listagens | 5min | Cache curto |
| JWT decode | 5min | Reduce CPU |
| JWT blacklist | 7d | Tempo do refresh token |

---

**Relatório gerado:** 2026-02-05
**Status:** Aguardando implementação
