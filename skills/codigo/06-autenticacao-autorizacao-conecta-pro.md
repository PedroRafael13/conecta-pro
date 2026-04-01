---
name: autenticacao-autorizacao-conecta-pro
description: Auditoria e implementação do sistema de autenticação e autorização do Conecta PRO — JWT, roles, permissões e segurança dos endpoints FastAPI. Usar para auditar endpoints sem proteção, corrigir vulnerabilidades de auth e implementar controle de acesso por perfil.
---

# Autenticação e Autorização — Conecta PRO

## Sistema atual
- Auth: JWT Bearer token
- Login: POST /api/v1/auth/login (form-data)
- Google OAuth: POST /api/v1/auth/google/callback
- Token: access_token (curta duração) + refresh_token
- Roles: admin, manager, user (verificar no banco)

## Credenciais de teste
```bash
# Login Jordan (admin)
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:40}..."
```

## Quando usar
- Endpoint retorna 401 inesperadamente
- Endpoint retorna 200 sem token (vulnerabilidade)
- Precisa adicionar autenticação em endpoint novo
- Precisa implementar controle por role/perfil

## Auditoria de segurança dos endpoints

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Verificar endpoints SEM autenticação (possível vulnerabilidade)
python3 << 'PYEOF'
import subprocess, json

TOKEN = subprocess.run(
    "curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-d 'username=jjesus@conectamais.pro&password=Jordan0612' "
    "| python3 -c \"import sys,json; "
    "print(json.load(sys.stdin)['access_token'])\"",
    shell=True, capture_output=True, text=True
).stdout.strip()

# Obter lista de endpoints
openapi = subprocess.run(
    f'curl -sf "http://127.0.0.1:8080/openapi.json" '
    f'-H "Authorization: Bearer {TOKEN}"',
    shell=True, capture_output=True, text=True
).stdout.strip()

try:
    data = json.loads(openapi)
    paths = data.get("paths", {})
    vulneraveis = []

    for path, methods in paths.items():
        # Pular rotas públicas legítimas
        if any(x in path for x in ["/auth/", "/health", "/docs",
                                     "/openapi", "/redoc"]):
            continue
        if "get" in methods:
            # Testar sem token
            status = subprocess.run(
                f'curl -sf -o /dev/null -w "%{{http_code}}" '
                f'"http://127.0.0.1:8080{path}"',
                shell=True, capture_output=True, text=True
            ).stdout.strip()
            if status == "200":
                vulneraveis.append(f"GET {path}")

    if vulneraveis:
        print(f"⚠️  {len(vulneraveis)} endpoint(s) SEM autenticação:")
        for ep in vulneraveis[:10]:
            print(f"  🔓 {ep}")
    else:
        print("✅ Todos os endpoints protegidos por autenticação")
except Exception as e:
    print(f"Erro: {e}")
PYEOF
```

## Padrão de autenticação nos endpoints FastAPI

```python
# CORRETO — todo endpoint deve exigir autenticação
from core.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

@router.get("/kits")
async def listar_kits(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)  # ← OBRIGATÓRIO
):
    # current_user.id → UUID do usuário logado
    # current_user.name → nome (usar no Bartolo greeting)
    # current_user.role → role para controle de acesso
    pass

# ERRADO — endpoint sem autenticação
@router.get("/kits")
async def listar_kits(db: AsyncSession = Depends(get_db)):
    # ← Sem get_current_user = qualquer um acessa
    pass
```

## Controle de acesso por role

```python
# Implementar verificação de role quando necessário
from fastapi import HTTPException

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Acesso restrito a administradores."
            }
        )
    return current_user

# Uso no endpoint
@router.delete("/funcionarios/{id}")
async def deletar_funcionario(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)  # só admin pode deletar
):
    pass
```

## Verificar usuários e roles no banco

```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Ver usuários cadastrados
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT id, name, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;" 2>/dev/null

# Ver roles existentes
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT DISTINCT role, COUNT(*) as qtd
FROM users
GROUP BY role ORDER BY qtd DESC;" 2>/dev/null

# Verificar tabela de refresh tokens
docker exec $CONTAINER psql -U postgres -d conectapro -c "
SELECT COUNT(*) as tokens_ativos,
  COUNT(*) FILTER (WHERE expires_at > NOW()) as validos,
  COUNT(*) FILTER (WHERE expires_at <= NOW()) as expirados
FROM refresh_tokens;" 2>/dev/null
```

## Google OAuth — configuração atual

```bash
# Verificar variáveis OAuth no container
docker exec $CONTAINER env | grep -i "google\|oauth\|client" \
  2>/dev/null | grep -v "PASSWORD\|SECRET"

# Callback URL registrada:
# https://erp.conectamais.pro/api/v1/auth/google/callback
# Client ID: 576020339239-bs4amjo67m3v0j9gerqnrk6gpohvjqvd.apps.googleusercontent.com

# Testar o endpoint de callback
curl -sf -o /dev/null -w "OAuth endpoint: %{http_code}\n" \
  "http://127.0.0.1:8080/api/v1/auth/google/callback"
```

## Tokens JWT — diagnóstico

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Decodificar token JWT (sem verificar assinatura — só para debug)
python3 -c "
import base64, json, sys
token = '$TOKEN'
parts = token.split('.')
# Payload é a segunda parte
payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
decoded = json.loads(base64.b64decode(payload))
print(json.dumps(decoded, indent=2, default=str))
" 2>/dev/null
```
