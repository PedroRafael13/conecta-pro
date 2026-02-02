# Rate Limiting - Conecta Pro

## Visão Geral

O Conecta Pro implementa rate limiting para proteger a API contra abuso, garantir fair usage e melhorar a estabilidade do sistema.

## Tecnologia

- **Biblioteca:** slowapi (baseada em Flask-Limiter)
- **Storage:** Redis (distribuído) ou memória (desenvolvimento)
- **Identificação:** User ID (autenticado) ou IP Address (público)

## Configuração

### Variáveis de Ambiente

```bash
# Redis para rate limiting distribuído
REDIS_URL=redis://localhost:6379/1
```

### Limites Padrão

| Tipo de Endpoint | Limite | Descrição |
|------------------|--------|-----------|
| **Global** | 1000/hour | Limite padrão para todos os endpoints |
| **Público** | 10/minute | Endpoints sem autenticação |
| **Autenticação** | 5/minute | Login, registro, reset de senha |
| **Leitura (GET)** | 100/minute | Endpoints de consulta |
| **Escrita (POST/PUT/PATCH/DELETE)** | 30/minute | Endpoints de modificação |
| **Crítico** | 10/minute | Operações sensíveis (geração de escalas) |
| **Bulk** | 5/minute | Operações em lote |
| **Export** | 3/minute | Relatórios e exportações |

## Endpoints com Rate Limiting

### Operações em Lote (5/minute)
- `DELETE /api/v1/operations/allocations/bulk`
- `PATCH /api/v1/operations/allocations/bulk`
- `PATCH /api/v1/operations/shifts/bulk`

### Operações Críticas (10/minute)
- `POST /api/v1/operations/scales/generate`
- `POST /api/v1/operations/scales/auto-generate`

## Como Usar

### Aplicar Rate Limit em um Endpoint

```python
from fastapi import APIRouter, Request
from core.rate_limit import limiter, CRITICAL_LIMIT

router = APIRouter()

@router.post("/critical-operation")
@limiter.limit(CRITICAL_LIMIT)
async def critical_operation(request: Request):
    # Request parameter é obrigatório para slowapi funcionar
    return {"status": "ok"}
```

### Limites Personalizados

```python
from core.rate_limit import limiter

@router.post("/custom")
@limiter.limit("5/minute")  # Limite customizado
async def custom_endpoint(request: Request):
    return {"status": "ok"}
```

### Múltiplos Limites

```python
@router.post("/multi")
@limiter.limit("10/minute")   # Por minuto
@limiter.limit("100/hour")    # Por hora
@limiter.limit("1000/day")    # Por dia
async def multi_limit(request: Request):
    return {"status": "ok"}
```

## Headers de Resposta

Quando rate limiting está ativo, os seguintes headers são incluídos nas respostas:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1709654400
```

## Erro 429 - Too Many Requests

Quando o limite é excedido, a API retorna:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Limite de requisições excedido. Tente novamente mais tarde.",
  "detail": "10 per 1 minute",
  "retry_after": "60"
}
```

**Headers adicionais:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1709654400
```

## Identificação de Usuários

### Usuários Autenticados
- Identificados por `user_id` do token JWT
- Limite compartilhado entre todas as sessões do usuário
- Formato: `user:{user_id}`

### Usuários Não Autenticados
- Identificados por IP address
- Limite por IP (pode afetar múltiplos usuários atrás de NAT)
- Formato: `ip:{ip_address}`

### API Keys
- Identificadas por hash da API key
- Limite maior que usuários normais (5000/hour)
- Formato: `apikey:{hash}`

## Monitoramento

### Logs Estruturados

Quando um limite é excedido:

```json
{
  "level": "warning",
  "message": "Rate limit excedido",
  "action": "rate_limit_exceeded",
  "path": "/api/v1/operations/scales/generate",
  "identifier": "user:123abc",
  "limit": "10 per 1 minute"
}
```

### Métricas (Prometheus)

```promql
# Requisições com rate limit excedido
rate_limit_exceeded_total{path="/api/v1/operations/scales/generate"}

# Requisições totais por endpoint
http_requests_total{path="/api/v1/operations/scales/generate"}
```

## Desenvolvimento

### Desabilitar Rate Limiting (Temporário)

**Não recomendado para produção!**

```python
# Em main.py, comentar:
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
```

### Testar Rate Limiting

```bash
# Fazer múltiplas requisições rapidamente
for i in {1..15}; do
  curl -X POST http://localhost:8080/api/v1/operations/scales/generate \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{...}'
  sleep 0.1
done
```

A partir da 11ª requisição (limite: 10/minute), deve retornar 429.

## Produção

### Recomendações

1. **Use Redis**: Nunca use memória em produção
2. **Configure REDIS_URL**: Apontar para instância Redis dedicada
3. **Monitore**: Acompanhe métricas de rate limiting
4. **Ajuste Limites**: Baseado em padrões de uso reais
5. **API Keys**: Para integrações, use API keys com limites maiores
6. **CDN/WAF**: Considere Cloudflare Rate Limiting para proteção adicional

### Clustering

Com Redis, o rate limiting funciona corretamente em ambiente distribuído:

```
                  ┌─────────────┐
                  │   Redis     │
                  │  (Shared)   │
                  └─────────────┘
                        ▲
                        │
            ┌───────────┴───────────┐
            │                       │
    ┌───────▼────────┐    ┌────────▼──────┐
    │   Backend 1    │    │  Backend 2    │
    │  (Instance)    │    │  (Instance)   │
    └────────────────┘    └───────────────┘
```

Todas as instâncias compartilham o mesmo contador no Redis.

## Troubleshooting

### Redis não conecta

```python
# Fallback para memória (logs mostram warning)
logger.warning("Rate limiting usando memória (não recomendado para produção)")
```

### Limites muito restritivos

Edite `core/rate_limit.py`:

```python
# Aumentar limites
CRITICAL_LIMIT = "20/minute"  # Era 10/minute
BULK_LIMIT = "10/minute"      # Era 5/minute
```

### Bypass para IPs específicos

```python
def get_user_identifier(request: Request) -> str:
    # Whitelist de IPs internos
    if get_remote_address(request) in ["10.0.0.1", "192.168.1.1"]:
        return "internal:bypass"

    # Lógica normal
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address(request)}"
```

## Segurança

### DDoS Protection

Rate limiting é **uma** camada de proteção, mas não suficiente contra DDoS:

1. **Camada Application (FastAPI)**: Rate limiting via slowapi ✅
2. **Camada Network (Nginx)**: `limit_req_zone` + `limit_conn_zone` ⚠️
3. **Camada CDN (Cloudflare)**: Rate limiting + DDoS protection 🔥

### Rate Limiting vs Throttling

- **Rate Limiting**: Limite rígido (429 após exceder)
- **Throttling**: Desacelera requisições (não implementado)

## Referências

- [slowapi Documentation](https://github.com/laurents/slowapi)
- [Redis Rate Limiting Patterns](https://redis.io/docs/manual/patterns/rate-limiter/)
- [OWASP Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
