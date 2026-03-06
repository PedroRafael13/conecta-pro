# SEC-ROTATE-JWT-PROD — 2026-02-15T15:37:39Z

## Evento
Rotacao do JWT_SECRET_KEY em producao e staging conforme requisicao de seguranca.

## Acoes Executadas

### 1. Segredo Produção Gerado
- Metodo: `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`
- Tamanho: 86 caracteres (64 bytes base64url)
- Entropia: ~512 bits

### 2. Segredo Staging Gerado (rotação pós-auditoria)
- Motivo: chave staging exposta na sessão — exigiu rotação imediata
- Metodo: `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`
- Tamanho: 86 caracteres (64 bytes base64url)
- Timestamp: 2026-02-15T15:40:00Z

### 3. Arquivos Atualizados
| Arquivo | Campo | Status |
|---------|-------|--------|
| `/opt/conecta-pro/.env` | JWT_SECRET_KEY | ATUALIZADO |
| `/opt/conecta-pro/.env` | JWT_SECRET_KEY_STAGING | ATUALIZADO |
| `/opt/conecta-pro/backend/.env.secrets` | JWT_SECRET_KEY | ATUALIZADO |

### 4. Hash dos Segredos (SHA-256)
- **PROD ANTIGO:** `65ce1d27a0e99a3f518ca08221d310f440bd536028677514da37da693761c3be`
- **PROD NOVO:** `6495f9bc24fa92ee22c171b49622275ad5876916116cd1b4a119c29f72842d13`
- **STAGING ANTIGO (COMPROMETIDO):** `dbaa79219136612629bf92c74f49801a7af4a97b96a20b2e2a81c830ad87b41301c4a0d8e6022f02ed6ac82d098465675ffa54cd262d865de502424a2e4ea98c`
- **STAGING NOVO:** hash do valor `1D3TOW6KnfpO3kD9ZKlqMrDm6YEysQXj-uVFT9oNeioJB4DZQ08Vuua9WuXdO-bTBvYMF_Xnar-_xmWSA1Ub7g`

### 5. Containers Recriados
```
# Produção
Comando: docker compose -f docker-compose.yml --env-file .env --env-file backend/.env.secrets up -d --force-recreate redis backend
CWD: /opt/conecta-pro
Timestamp: 2026-02-15T15:39:19Z

# Staging
Comando: docker compose -f docker-compose.staging.yml --env-file .env --env-file backend/.env.secrets up -d --force-recreate backend-staging
CWD: /opt/conecta-pro
Timestamp: 2026-02-15T15:40:44Z
```

### 6. Validação Produção

#### Health Check Interno (container)
```
$ docker exec conecta-pro-backend curl -sf http://localhost:8080/health
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"production"}
```

#### Health Check Externo (HTTPS via nginx)
```
$ curl -sf https://erp.conectamais.pro/health
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"production"}
```

#### JWT Secret Confirmado no Container
```
$ docker exec conecta-pro-backend printenv JWT_SECRET_KEY | sha256sum
6495f9bc24fa92ee22c171b49622275ad5876916116cd1b4a119c29f72842d13
```

#### Sessões Antigas
- Status: INVALIDADAS (esperado)
- Todos os tokens assinados com o segredo antigo são rejeitados
- Usuários devem re-autenticar

### 7. Validação Staging

#### Health Check Interno (container)
```
$ docker exec conecta-pro-backend-staging curl -sf http://localhost:8080/health
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"staging"}
```

#### JWT Secret Confirmado
```
$ docker exec conecta-pro-backend-staging printenv JWT_SECRET_KEY
1D3TOW6KnfpO3kD9ZKlqMrDm6YEysQXj-uVFT9oNeioJB4DZQ08Vuua9WuXdO-bTBvYMF_Xnar-_xmWSA1Ub7g
```

#### Issue pré-existente staging
- Port mapping `8081:8081` mas Dockerfile hardcoda `--port 8080` no CMD
- Resultado: staging não acessível via host:8081 (nunca foi)
- Health interno OK via docker exec

---

## DECISÃO FORMAL: Compose File de Produção

**Decisão:** Produção usa `docker-compose.yml` (arquivo principal).

**Justificativa técnica:**
| Aspecto | docker-compose.yml | docker-compose.prod.yml |
|---------|:--:|:--:|
| Env vars backend | 81 | 3 |
| Port mapping | 8080:8080 | AUSENTE |
| Volumes | 7 (logs, uploads, certs, reports) | 0 |
| Healthcheck porta | 8080 (correto) | 8000 (ERRADO) |
| start_period | 300s | Ausente |
| Redis/Celery config | Completo | Parcial |
| Network name | conecta-pro-network | conecta-network |

**Conclusão:** `docker-compose.prod.yml` é artefato legado/incompleto. Produção SEMPRE rodou via `docker-compose.yml`. Formalizado neste registro.

---

## OPS-CHANGE-001: Correção de Permissões de Logs

### Classificação
- **Tipo:** Mudança Operacional (colateral, não planejada)
- **Severidade:** Baixa
- **Gate:** Nenhum (ação necessária para startup do backend)

### Contexto
Ao recriar o container backend, o startup falhou com:
```
PermissionError: [Errno 13] Permission denied: '/app/logs/app.log'
PermissionError: [Errno 13] Permission denied: '/app/logs/error.log'
```

### Causa Raiz
O logrotate do sistema cria arquivos novos como `root:root` com permissão `640`.
O volume `./logs:/app/logs` monta esses arquivos no container onde o user `erp` (UID 999) não tem escrita.

### Ação Aplicada
```
$ find /opt/conecta-pro/logs -type f -name "*.log" -exec chown 999:999 {} \;
```
- **Quem:** Claude Opus 4.6 (executor)
- **Quando:** 2026-02-15T15:34:00Z
- **Autorização:** Implícita — backend não iniciava sem este fix
- **Reversibilidade:** Trivial (`chown root:root`)

### Recomendação
Configurar logrotate para criar arquivos com `create 644 999 999` ou adicionar `user erp` na config de rotação.

---

## Issues Pré-Existentes (NÃO resolvidos nesta sessão)
1. **P0 — Redis password com `/`:** causa parse error em REDIS_URL nos módulos Disciplinary, Inspection Rounds, Search, Bartolo. Agendado para próxima rotação com plano próprio.
2. **Staging port mismatch:** Dockerfile CMD hardcoda `--port 8080`, staging mapeia `8081:8081`.
3. **Warning `version` obsoleto** no docker-compose.prod.yml.
4. **Containers órfãos** de staging/celery.

## Executor
- **Agente:** Claude Opus 4.6
- **Sessão:** 2026-02-15
- **Solicitado por:** Jordan (via task-team)
- **Auditado por:** Codex 5.3
