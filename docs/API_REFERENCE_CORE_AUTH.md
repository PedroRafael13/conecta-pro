# API Reference - Core e Autenticação

Documentação de referência para os módulos Core (autenticação, usuários e health check) do Conecta PRO.

**Base URL:** `https://erp.conectamais.pro/api/v1`

---

## Índice

1. [Autenticação](#endpoints-de-autenticação)
2. [Usuários](#endpoints-de-usuários)
3. [Health Check](#endpoints-de-health-check)
4. [Schemas](#schemas)
5. [Exemplos de Uso](#exemplos-de-uso)

---

## Endpoints de Autenticação

| Método | Path | Descrição | Auth | Request | Response |
|--------|------|-----------|------|---------|----------|
| POST | `/auth/register` | Registra novo usuário | ❌ | `UserCreate` | `UserResponse` (201) |
| POST | `/auth/login` | Autentica usuário e retorna tokens | ❌ | `OAuth2PasswordRequestForm` | `TokenResponse` |
| POST | `/auth/refresh` | Renova tokens usando refresh token | ❌ | `TokenRefreshRequest` | `TokenResponse` |
| GET | `/auth/me` | Retorna informações do usuário atual | ✅ Bearer | - | `UserResponse` |
| GET | `/auth/google` | Inicia fluxo OAuth2 com Google | ❌ | - | Redirect |
| GET | `/auth/google/callback` | Callback do Google OAuth2 | ❌ | `code`, `error` (query) | Redirect |

---

## Endpoints de Usuários

| Método | Path | Descrição | Auth | Request | Response |
|--------|------|-----------|------|---------|----------|
| GET | `/users/` | Lista todos os usuários (admin) | ✅ Bearer | `page`, `per_page`, `role`, `search` (query) | `UserListResponse` |
| GET | `/users/pending` | Lista usuários pendentes (admin) | ✅ Bearer | - | `UserResponse[]` |
| GET | `/users/roles` | Lista roles disponíveis | ✅ Bearer | - | `RolesList` |
| GET | `/users/{user_id}` | Obtém detalhes de um usuário (admin) | ✅ Bearer | `user_id` (path) | `UserResponse` |
| PATCH | `/users/{user_id}/role` | Atualiza role do usuário (admin) | ✅ Bearer | `user_id` (path), `UserUpdateRole` | `UserResponse` |
| PATCH | `/users/{user_id}/activate` | Ativa um usuário (admin) | ✅ Bearer | `user_id` (path) | `UserResponse` |
| PATCH | `/users/{user_id}/deactivate` | Desativa um usuário (admin) | ✅ Bearer | `user_id` (path) | `UserResponse` |
| DELETE | `/users/{user_id}` | Exclui um usuário (admin) | ✅ Bearer | `user_id` (path) | `204 No Content` |

---

## Endpoints de Health Check

| Método | Path | Descrição | Auth | Request | Response |
|--------|------|-----------|------|---------|----------|
| GET | `/health` | Verifica saúde de todos os componentes | ❌ | `detailed` (query) | `HealthStatus` |
| GET | `/health/ready` | Readiness probe (Kubernetes) | ❌ | - | `ReadinessStatus` |
| GET | `/health/live` | Liveness probe (Kubernetes) | ❌ | - | `LivenessStatus` |

---

## Schemas

### TokenResponse
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

### TokenRefreshRequest
```json
{
  "refresh_token": "string"
}
```

### UserCreate
```json
{
  "email": "user@example.com",
  "name": "Nome Completo",
  "phone": "+55 11 99999-9999",
  "password": "senha123",
  "role": "operador"
}
```

### UserResponse
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Nome Completo",
  "phone": "+55 11 99999-9999",
  "role": "operador",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

### UserListResponse
```json
{
  "users": [UserResponse],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### UserUpdateRole
```json
{
  "role": "admin"
}
```

### HealthStatus
```json
{
  "status": "healthy|degraded|unhealthy",
  "healthy_count": 2,
  "total_count": 3,
  "timestamp": "2024-01-01T00:00:00Z",
  "components": {
    "database": {"status": "healthy", "response_time_ms": 15},
    "redis": {"status": "healthy", "response_time_ms": 5}
  }
}
```

### Roles Disponíveis

| Role | Descrição |
|------|-----------|
| `admin` | Acesso total ao ERP |
| `gestor` | Dashboard, relatórios, operações |
| `operador` | Operações básicas |
| `funcionario` | Portal do Funcionário (ponto, escalas, docs) |
| `pending` | Aguardando aprovação |
| `administrador` | Poder total no módulo operacional |
| `gerente_operacional` | Gestão completa do operacional |
| `supervisor` | Aprova escalas, coordena equipes |
| `inspetor` | Fiscaliza postos, visualiza relatórios |
| `lider` | Coordena equipe local |
| `agente` | Acesso à própria escala e check-in/out |

---

## Códigos de Resposta

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 204 | Sem conteúdo (sucesso) |
| 400 | Requisição inválida |
| 401 | Não autorizado (token inválido/ausente) |
| 403 | Proibido (sem permissão) |
| 404 | Recurso não encontrado |
| 422 | Erro de validação |
| 503 | Serviço indisponível |

---

## Exemplos de Uso

### 1. Registrar Novo Usuário

```bash
curl -X POST "https://erp.conectamais.pro/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo.usuario@empresa.com",
    "name": "Novo Usuário",
    "password": "SenhaSegura123!",
    "phone": "+55 11 99999-9999",
    "role": "operador"
  }'
```

**Resposta (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "novo.usuario@empresa.com",
  "name": "Novo Usuário",
  "phone": "+55 11 99999-9999",
  "role": "operador",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login": null
}
```

---

### 2. Login (Obter Tokens)

```bash
curl -X POST "https://erp.conectamais.pro/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=novo.usuario@empresa.com&password=SenhaSegura123!"
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. Renovar Token

```bash
curl -X POST "https://erp.conectamais.pro/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 4. Obter Informações do Usuário Atual

```bash
curl -X GET "https://erp.conectamais.pro/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "novo.usuario@empresa.com",
  "name": "Novo Usuário",
  "phone": "+55 11 99999-9999",
  "role": "operador",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T14:20:00Z"
}
```

---

### 5. Listar Usuários (Admin)

```bash
curl -X GET "https://erp.conectamais.pro/api/v1/users/?page=1&per_page=10&role=operador&search=joao" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta (200):**
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "joao.silva@empresa.com",
      "name": "João Silva",
      "role": "operador",
      "is_active": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z",
      "last_login": "2024-01-15T09:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

---

### 6. Atualizar Role do Usuário (Admin)

```bash
curl -X PATCH "https://erp.conectamais.pro/api/v1/users/550e8400-e29b-41d4-a716-446655440000/role" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "role": "gestor"
  }'
```

**Resposta (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "joao.silva@empresa.com",
  "name": "João Silva",
  "role": "gestor",
  "is_active": true,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T16:45:00Z",
  "last_login": "2024-01-15T09:30:00Z"
}
```

---

### 7. Health Check

```bash
curl -X GET "https://erp.conectamais.pro/api/v1/health?detailed=true"
```

**Resposta (200):**
```json
{
  "status": "healthy",
  "healthy_count": 2,
  "total_count": 2,
  "timestamp": "2024-01-15T16:50:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection OK",
      "response_time_ms": 12,
      "checked_at": "2024-01-15T16:50:00Z"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection OK",
      "response_time_ms": 3,
      "checked_at": "2024-01-15T16:50:00Z"
    }
  }
}
```

---

### 8. Autenticação com Google OAuth2

**Passo 1:** Redirecionar o usuário para:
```
https://erp.conectamais.pro/api/v1/auth/google
```

**Passo 2:** Após autorização no Google, o usuário é redirecionado para:
```
https://erp.conectamais.pro/auth/callback?access_token=xxx&refresh_token=yyy&token_type=bearer
```

---

## Segurança

- Todos os endpoints protegidos (🔒) requerem Bearer token no header `Authorization`
- Tokens de acesso expiram em 30 minutos
- Tokens de refresh expiram em 7 dias
- Rate limiting aplicado: 1000 requisições/hora por usuário
- Headers de segurança aplicados em todas as respostas

## Headers de Segurança Padrão

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; ...
```

---

*Documentação gerada em: 2024-02-05*
*Versão da API: 1.0.0*
