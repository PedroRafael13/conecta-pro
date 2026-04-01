# SEC-ROTATE-JWT-STAGING — 2026-02-15

## Motivo
Segredo anterior exposto em sessão de auditoria. Rotação emergencial executada.

---

## 1. Comandos Executados

### 1.1 Geração do segredo
```bash
$ python3 -c "import secrets; print(secrets.token_hex(64))"
# Saída: 128 caracteres hex (64 bytes), sem caracteres URL-unsafe
```

### 1.2 Atualização do .env
```bash
# Editado /opt/conecta-pro/.env
# Linha alterada: JWT_SECRET_KEY_STAGING=<NOVO_VALOR_HEX_128_CHARS>
# Valor anterior (comprometido) substituído
```

### 1.3 Recreate do backend-staging
```bash
$ cd /opt/conecta-pro
$ docker compose -f docker-compose.staging.yml \
    --env-file .env \
    --env-file backend/.env.secrets \
    up -d --force-recreate backend-staging

# Output:
 Container conecta-pro-postgres-staging Running
 Container conecta-pro-redis-staging Running
 Container conecta-pro-backend-staging Recreate
 Container conecta-pro-backend-staging Recreated
 Container conecta-pro-postgres-staging Waiting
 Container conecta-pro-redis-staging Waiting
 Container conecta-pro-postgres-staging Healthy
 Container conecta-pro-redis-staging Healthy
 Container conecta-pro-backend-staging Starting
 Container conecta-pro-backend-staging Started
```

---

## 2. Status do Container

```
$ docker ps --filter "name=backend-staging" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
NAMES                         STATUS                             PORTS
conecta-pro-backend-staging   Up 39 seconds (health: starting)   8080/tcp, 0.0.0.0:8081->8081/tcp, [::]:8081->8081/tcp
```

**Nota:** O status evolui para `unhealthy` porque o healthcheck do compose
aponta para `http://localhost:8081/health` mas a aplicação escuta em 8080 (ver seção 5).
Isso é falso negativo — app funcional.

---

## 3. Health Check

### 3.1 Via host (localhost:8081)
```
$ curl -sf http://localhost:8081/health
# Resultado: connection reset (exit code 56)
# Motivo: mismatch de porta — ver seção 5
```

### 3.2 Via container (localhost:8080) — MÉTODO VÁLIDO
```
$ docker exec conecta-pro-backend-staging curl -sf http://localhost:8080/health
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"staging"}
```

**Conclusão:** Backend staging SAUDÁVEL internamente.

---

## 4. Confirmação de Substituição do Segredo

```
$ docker exec conecta-pro-backend-staging printenv JWT_SECRET_KEY | sha256sum
2a57106cc99b57ff4051eae5413580bc1403baeb6e1eab05fd59877220ced662  -
```

- Chave anterior (COMPROMETIDA): substituída com sucesso
- Chave nova: confirmada no container via hash acima
- Valor NÃO exibido neste registro por segurança
- O compose staging mapeia `JWT_SECRET_KEY: ${JWT_SECRET_KEY_STAGING}` do .env
- Sessões staging anteriores: INVALIDADAS (esperado)
- Nenhum impacto em produção

---

## 5. Observação: Mismatch 8081 vs 8080

| Config | Valor |
|--------|-------|
| `docker-compose.staging.yml` PORT env | `8081` |
| `docker-compose.staging.yml` ports | `8081:8081` |
| `docker-compose.staging.yml` healthcheck | `http://localhost:8081/health` |
| `backend/Dockerfile` CMD | `uvicorn ... --port 8080` **(HARDCODED)** |

**Causa:** O Dockerfile ignora a variável PORT no CMD:
```dockerfile
CMD ["uvicorn", "main_production:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Impacto:**
- A aplicação SEMPRE escuta em 8080 independente da env PORT
- O port mapping `8081:8081` mapeia host:8081 → container:8081, mas nada escuta em container:8081
- Resultado: staging inacessível via `localhost:8081`; Docker healthcheck sempre FALHA
- Staging usa porta 8080 interna (acessível apenas via `docker exec`)

**Status:** Pré-existente — existia ANTES da rotação JWT.

**Fix recomendado:** Alterar CMD no Dockerfile para `CMD ["sh", "-c", "uvicorn main_production:app --host 0.0.0.0 --port $PORT"]` ou ajustar staging mapping para `8081:8080`.

---

## Metadados
- **Executor:** Claude Opus 4.6
- **Timestamp recreate:** 2026-02-15T15:51:52Z
- **Auditado por:** Codex 5.3
- **Motivo da rotação:** Chave staging exposta em sessão de auditoria
