# 🔒 Relatório de Configurações de Segurança - Conecta PRO

> **Documento:** SECURITY_CONFIGURATION.md
> **Versão:** 1.0.0
> **Data:** Fevereiro 2026
> **Ambiente:** Production (erp.conectamais.pro)

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Docker e Network Security](#docker-e-network-security)
3. [Variáveis de Ambiente e Secrets](#variáveis-de-ambiente-e-secrets)
4. [Headers de Segurança HTTP](#headers-de-segurança-http)
5. [Configuração CORS](#configuração-cors)
6. [SSL/TLS](#ssltls)
7. [Rate Limiting](#rate-limiting)
8. [JWT Security](#jwt-security)
9. [Recomendações de Hardening](#recomendações-de-hardening)
10. [Checklist de Segurança](#checklist-de-segurança)

---

## Visão Geral

O Conecta PRO implementa uma arquitetura de segurança em camadas, utilizando múltiplos mecanismos de proteção em diferentes níveis da aplicação:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS (TLS 1.2+)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│   🔒 Nginx (Reverse Proxy)                                      │
│   • SSL/TLS termination                                         │
│   • Rate limiting por IP                                        │
│   • Security headers                                            │
│   • WAF básico                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Frontend   │ │   Backend   │ │   Grafana   │
│  Next.js    │ │  FastAPI    │ │  Monitor    │
│  :3000      │ │  :8080      │ │  :3000      │
└─────────────┘ └──────┬──────┘ └─────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────┐               ┌─────────────┐
│  PostgreSQL │               │    Redis    │
│  (Internal) │               │  (Internal) │
│   :5432     │               │   :6379     │
└─────────────┘               └─────────────┘
```

---

## Docker e Network Security

### 1.1 Arquitetura de Rede

| Aspecto | Configuração | Status |
|---------|--------------|--------|
| Driver de rede | `bridge` | ✅ |
| Isolamento de containers | Rede dedicada `conecta-pro-network` | ✅ |
| Exposição de portas DB | **NÃO expostas** (comentadas) | ✅ |
| Exposição Redis | **NÃO exposto** (comentado) | ✅ |

### 1.2 Configuração Docker Compose (Network)

```yaml
networks:
  conecta-pro-network:
    driver: bridge
```

**Boas práticas implementadas:**
- ✅ PostgreSQL e Redis não expõem portas publicamente
- ✅ Comunicação interna apenas via rede Docker
- ✅ Health checks configurados para todos os serviços
- ✅ Restart policy `unless-stopped`

### 1.3 Volumes e Permissões

| Serviço | Volume | Permissão | Observação |
|---------|--------|-----------|------------|
| Backend | `./credentials` | `:ro` (read-only) | Certificados digitais |
| Backend | `./uploads` | `rw` | Uploads GED |
| Backend | Módulos externos | `:ro` | Fase 3 read-only |
| Nginx | `./certs` | `:ro` | Certificados SSL |
| Nginx | `./config` | `:ro` | Configurações |

### 1.4 Usuário Não-Root (Backend)

```dockerfile
# Dockerfile backend
RUN groupadd -r erp && useradd -r -g erp erp
...
USER erp  # Container roda como usuário não-privilegiado
```

---

## Variáveis de Ambiente e Secrets

### 2.1 Gestão de Secrets

| Tipo | Localização | Método | Status |
|------|-------------|--------|--------|
| Secrets sensíveis | `.env` | Arquivo local (não versionado) | ⚠️ |
| JWT Secret | `${JWT_SECRET_KEY}` | Env var | ⚠️ |
| API Keys | `${OPENAI_API_KEY}`, `${ANTHROPIC_API_KEY}` | Env var | ⚠️ |
| DB Password | `${POSTGRES_PASSWORD}` | Env var | ⚠️ |
| Google OAuth | `${GOOGLE_CLIENT_SECRET}` | Env var | ⚠️ |

### 2.2 Valores Padrão Críticos (Requerem Alteração)

```yaml
# docker-compose.yml - VALORES QUE DEVEM SER ALTERADOS
JWT_SECRET_KEY: ${JWT_SECRET_KEY:-CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN}
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
```

> ⚠️ **ALERTA:** O valor padrão `CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN` deve ser substituído por uma chave forte em produção!

### 2.3 Validação de JWT Secret

```python
# core/config/settings.py
@field_validator("jwt_secret_key")
@classmethod
def validate_jwt_secret(cls, v, info):
    """Valida que JWT secret tem tamanho adequado em produção."""
    if info.data.get("environment") == "production" and len(v) < 32:
        raise ValueError("JWT secret deve ter pelo menos 32 caracteres em produção")
    return v
```

### 2.4 Recomendações para Secrets

1. **Gerar JWT Secret forte:**
   ```bash
   openssl rand -hex 32
   ```

2. **Permissões do arquivo .env:**
   ```bash
   chmod 600 /opt/conecta-pro/.env
   chown root:root /opt/conecta-pro/.env
   ```

3. **Considerar Docker Secrets ou Vault:**
   - Docker Swarm Secrets
   - HashiCorp Vault
   - AWS Secrets Manager (se migrar para cloud)

---

## Headers de Segurança HTTP

### 3.1 Headers no Backend (FastAPI)

```python
# main.py - SecurityHeadersMiddleware
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self'; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors 'none'"
)
response.headers["Strict-Transport-Security"] = (
    "max-age=31536000; includeSubDomains; preload"
)
```

### 3.2 Headers no Nginx

```nginx
# config/nginx/conf.d/security-headers.conf
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Content-Security-Policy "default-src 'self'; ..." always;
```

### 3.3 Headers no Frontend (Next.js)

```javascript
// next.config.ts
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      ],
    },
  ];
}
```

### 3.4 Análise de Headers de Segurança

| Header | Valor | Nível | Observação |
|--------|-------|-------|------------|
| `X-Frame-Options` | `DENY` / `SAMEORIGIN` | ✅ | Proteção contra clickjacking |
| `X-Content-Type-Options` | `nosniff` | ✅ | Previne MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | ✅ | Proteção XSS (legado) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | ✅ | Controle de referrer |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | ✅ | HSTS ativo |
| `Content-Security-Policy` | Definido | ⚠️ | `unsafe-inline` e `unsafe-eval` presentes |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | ✅ | APIs restritas |

> ⚠️ **Nota CSP:** O uso de `'unsafe-inline'` e `'unsafe-eval'` é necessário para algumas bibliotecas React/Next.js, mas aumenta a superfície de ataque XSS.

---

## Configuração CORS

### 4.1 Backend CORS (FastAPI)

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2 Configuração de Origens

```python
# core/config/settings.py
cors_origins_str: str = Field(default="http://localhost:3000", alias="cors_origins")

@property
def cors_origins(self) -> list[str]:
    """Retorna lista de CORS origins parseada."""
    if isinstance(self.cors_origins_str, str):
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
    return ["http://localhost:3000"]
```

### 4.3 Valores de Produção (Esperados)

```bash
# .env
CORS_ORIGINS=https://erp.conectamais.pro,https://app.conectamais.pro
```

### 4.4 Análise CORS

| Aspecto | Configuração | Status | Recomendação |
|---------|--------------|--------|--------------|
| Origens permitidas | Configurável via env | ✅ | Especificar domínios exatos |
| Credentials | `allow_credentials=True` | ✅ | Necessário para cookies/JWT |
| Métodos | `["*"]` (todos) | ⚠️ | Restringir para necessários |
| Headers | `["*"]` (todos) | ⚠️ | Especificar headers necessários |

> ⚠️ **Atenção:** `main_lite.py` usa `allow_origins=["*"]` - não usar em produção!

---

## SSL/TLS

### 5.1 Configuração SSL (Nginx)

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name erp.conectamais.pro;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/nginx/certs/live/erp.conectamais.pro/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/live/erp.conectamais.pro/privkey.pem;
    include /etc/nginx/ssl-params.conf;
}
```

### 5.2 SSL Hardening (ssl-params.conf)

```nginx
# TLS 1.2+ apenas
ssl_protocols TLSv1.2 TLSv1.3;

# Cipher suites fortes
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...
ssl_prefer_server_ciphers off;

# Session cache
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

### 5.3 Análise SSL/TLS

| Aspecto | Configuração | Status | Score |
|---------|--------------|--------|-------|
| Protocolos | TLS 1.2, TLS 1.3 | ✅ | A+ |
| Ciphers | ECDHE + AES-GCM/POLY1305 | ✅ | A+ |
| HSTS | `max-age=63072000` (2 anos) | ✅ | A+ |
| OCSP Stapling | Ativo | ✅ | A+ |
| HTTP/2 | Ativo | ✅ | Performance |
| Redirect HTTP→HTTPS | 301 | ✅ | Obrigatório |

### 5.4 Configurações de SSL Audit

```nginx
# Redirecionamento HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name erp.conectamais.pro;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
```

**Nota:** DH Parameter (`ssl_dhparam`) está comentado. Recomenda-se gerar:
```bash
openssl dhparam -out /opt/conecta-pro/certs/dhparam.pem 4096
```

---

## Rate Limiting

### 6.1 Nginx Rate Limiting

```nginx
# nginx.conf - Rate Limiting Zones
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/s;

# Aplicação
location / {
    limit_req zone=general burst=20 nodelay;
    ...
}

location /api/v1/auth/login {
    limit_req zone=login burst=5 nodelay;  # Anti brute-force
    ...
}
```

### 6.2 Backend Rate Limiting (slowapi + Redis)

```python
# core/rate_limit.py
storage_uri = settings.redis_url  # Redis para storage distribuído

limiter = Limiter(
    key_func=get_user_identifier,  # user_id + IP
    storage_uri=storage_uri,
)

def get_user_identifier(request: Request) -> str:
    """Prioridade: user_id do JWT → IP address"""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address(request)}"
```

### 6.3 Rate Limits Configurados

| Zona | Taxa | Burst | Uso |
|------|------|-------|-----|
| `general` | 10 req/s | 20 | Páginas gerais |
| `api` | 20 req/s | 40 | API endpoints |
| `login` | 5 req/s | 5 | Autenticação (anti brute-force) |

---

## JWT Security

### 7.1 Configuração JWT

```python
# core/config/settings.py
jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN")
jwt_algorithm: str = Field(default="HS256")
jwt_access_token_expire_minutes: int = Field(default=240)  # 4 horas
jwt_refresh_token_expire_days: int = Field(default=7)
```

### 7.2 Análise JWT

| Aspecto | Configuração | Status |
|---------|--------------|--------|
| Algoritmo | HS256 | ✅ |
| Expiração Access | 240 min (4 horas) | ⚠️ Longo para aplicação financeira |
| Expiração Refresh | 7 dias | ✅ |
| Validação tamanho | ≥32 chars em produção | ✅ |

**Recomendação:** Considerar reduzir access token para 15-30 minutos para aplicações com dados sensíveis.

---

## Recomendações de Hardening

### 8.1 Prioridade Alta

| # | Recomendação | Impacto | Esforço |
|---|--------------|---------|---------|
| 1 | **Gerar JWT_SECRET_KEY forte** | Crítico | Baixo |
| 2 | **Restringir CORS origins em produção** | Alto | Baixo |
| 3 | **Habilitar `ssl_dhparam`** | Médio | Baixo |
| 4 | **Permissões 600 no .env** | Médio | Baixo |
| 5 | **Reduzir JWT expiry para 30min** | Médio | Baixo |

### 8.2 Prioridade Média

| # | Recomendação | Impacto | Esforço |
|---|--------------|---------|---------|
| 6 | Implementar Fail2Ban | Alto | Médio |
| 7 | WAF (ModSecurity/Cloudflare) | Alto | Médio |
| 8 | Remover `unsafe-inline` do CSP | Médio | Alto |
| 9 | Secrets management (Vault) | Médio | Alto |
| 10 | Audit logging | Médio | Médio |

### 8.3 Prioridade Baixa

| # | Recomendação | Impacto | Esforço |
|---|--------------|---------|---------|
| 11 | IP Whitelist admin | Baixo | Baixo |
| 12 | Database encryption at rest | Baixo | Alto |
| 13 | Network policies (Kubernetes) | Baixo | Alto |

---

## Checklist de Segurança

### Pre-Deploy

- [ ] JWT_SECRET_KEY gerado com `openssl rand -hex 32`
- [ ] POSTGRES_PASSWORD alterado do padrão
- [ ] CORS_ORIGINS configurado com domínios de produção
- [ ] Arquivo `.env` com permissões 600
- [ ] Certificados SSL válidos e não expirados
- [ ] `main_lite.py` não usado em produção

### Post-Deploy

- [ ] Headers de segurança verificados (`curl -I https://erp.conectamais.pro`)
- [ ] SSL Labs test (https://www.ssllabs.com/ssltest/)
- [ ] Security Headers scan (https://securityheaders.com/)
- [ ] Rate limiting testado
- [ ] Logs de acesso sendo gerados

### Manutenção

- [ ] Renovação automática Let's Encrypt funcionando
- [ ] Logs auditados semanalmente
- [ ] Dependências atualizadas mensalmente
- [ ] Penetration test anual

---

## Referências

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [Nginx Security Best Practices](https://www.nginx.com/blog/http-security-headers/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Documento gerado em:** Fevereiro 2026
**Responsável:** Equipe de Segurança Conecta PRO
**Próxima revisão:** Março 2026
