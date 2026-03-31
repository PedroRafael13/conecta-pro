---
name: dockerfile-otimizado-conecta-pro
description: Auditoria e otimização dos containers Docker do Conecta PRO — backend FastAPI e frontend Next.js. Usar para diagnosticar problemas de build, otimizar tamanho das imagens, corrigir permissões e garantir restart automático dos serviços.
---

# Docker e Containers — Conecta PRO

## Contexto
- Backend: Docker (conecta-pro-backend) · FastAPI · porta 8080
- Frontend: PM2 (conecta-pro-frontend) · Next.js · porta 3001
- PostgreSQL: Docker (conecta-pro-postgres)
- Redis: Docker (conecta-pro-redis)
- VPS: srv1134814.hstgr.cloud (82.25.75.74)

## Quando usar
- Container travou ou não sobe
- Hot copy não está funcionando
- Build do frontend falha (OOM)
- Serviço não reinicia após deploy

## Diagnóstico dos containers

```bash
# Status de todos os containers
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Ver uso de recursos
docker stats --no-stream

# Ver logs do backend (últimos erros)
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
docker logs $CONTAINER --tail 50 2>&1 | \
  grep -i "error\|exception\|warning\|traceback" | head -20

# Ver logs do PostgreSQL
PG_CONTAINER=$(docker ps --filter ancestor=conecta-pro-postgres \
  --format '{{.Names}}' 2>/dev/null | head -1 || \
  docker ps | grep postgres | awk '{print $NF}' | head -1)
docker logs $PG_CONTAINER --tail 20 2>/dev/null

# Verificar PM2 (frontend)
pm2 list
pm2 logs conecta-pro-frontend --lines 20 --nostream 2>/dev/null
```

## Hot copy backend (padrão de deploy rápido)

```bash
# Forma correta de aplicar mudanças no backend SEM rebuild completo
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Copiar arquivo modificado
docker cp /opt/conecta-pro/backend/modules/[modulo]/[arquivo].py \
  $CONTAINER:/app/modules/[modulo]/[arquivo].py

# Reiniciar container (não rebuild — muito mais rápido)
docker restart $CONTAINER && sleep 8

# Validar que subiu corretamente
docker logs $CONTAINER --tail 5 2>/dev/null
curl -sf -o /dev/null -w "Backend: %{http_code}\n" \
  http://127.0.0.1:8080/docs
```

## Build do frontend (padrão correto)

```bash
# SEMPRE usar NODE_OPTIONS para evitar OOM no VPS Hostinger KV4
# NUNCA rodar dois builds simultâneos — mata o VPS

# Verificar memória disponível antes do build
free -m | awk '/^Mem:/{print "RAM livre: " $4 "MB"}'

# Build correto
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build 2>&1 | tail -25

# Se o build OK, reiniciar PM2
pm2 restart conecta-pro-frontend --update-env && pm2 save && sleep 8

# Verificar que frontend subiu
curl -sf -o /dev/null -w "Frontend: %{http_code}\n" \
  https://erp.conectamais.pro/dashboard

# Verificar logs do PM2
pm2 logs conecta-pro-frontend --lines 10 --nostream 2>/dev/null
```

## Recuperar serviços travados

```bash
# Backend travado — reiniciar
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
docker restart $CONTAINER && sleep 10
echo "Backend: $(curl -sf -o /dev/null -w '%{http_code}' \
  http://127.0.0.1:8080/docs)"

# Frontend travado — reiniciar PM2
pm2 restart conecta-pro-frontend --update-env
pm2 save
sleep 5
echo "Frontend: $(curl -sf -o /dev/null -w '%{http_code}' \
  https://erp.conectamais.pro)"

# Se PM2 não existir — iniciar do zero
if ! pm2 list | grep -q "conecta-pro-frontend"; then
  cd /opt/conecta-pro/frontend
  pm2 start npm --name "conecta-pro-frontend" \
    -- start -- --port 3001
  pm2 save
  pm2 startup
fi

# Container não existe mais — recriar via compose
# ⚠️ NÃO editar docker-compose.yml — só executar
cd /opt/conecta-pro
docker-compose up -d --no-recreate 2>/dev/null || \
  docker compose up -d --no-recreate
```

## Permissões dos certificados bancários

```bash
# Certificados Cora e Inter precisam de permissão especial
# para o usuário do container (UID 999)
ls -la /opt/conecta-pro/credentials/ 2>/dev/null \
  | grep -v "^total"

# Corrigir permissões se necessário
for cert_file in /opt/conecta-pro/credentials/*.key \
                 /opt/conecta-pro/credentials/*.pem; do
  [ -f "$cert_file" ] && \
    chown root:999 "$cert_file" && \
    chmod 640 "$cert_file" && \
    echo "✓ $(basename $cert_file)"
done
```

## Monitoramento contínuo

```bash
# Script de health check completo
python3 << 'PYEOF'
import subprocess, datetime

def check(name, cmd):
    r = subprocess.run(cmd, shell=True,
        capture_output=True, text=True, timeout=10)
    ok = r.returncode == 0 or "200" in r.stdout
    icon = "✅" if ok else "❌"
    print(f"  {icon} {name}")
    return ok

print(f"\n=== HEALTH CHECK {datetime.datetime.now().strftime('%H:%M:%S')} ===")
checks = [
    ("Backend HTTP",
     'curl -sf -o /dev/null -w "%{http_code}" '
     'http://127.0.0.1:8080/docs | grep -q "200"'),
    ("Frontend HTTP",
     'curl -sf -o /dev/null -w "%{http_code}" '
     'https://erp.conectamais.pro | grep -q "200"'),
    ("PostgreSQL",
     'docker exec $(docker ps --filter ancestor=conecta-pro-backend '
     '--format "{{.Names}}" | head -1) '
     'psql -U postgres -d conectapro -c "SELECT 1" -t 2>/dev/null '
     '| grep -q "1"'),
    ("PM2 Frontend",
     'pm2 list | grep -q "online"'),
]
resultados = [check(n, c) for n, c in checks]
total = sum(resultados)
print(f"\nSaúde: {total}/{len(resultados)} serviços operacionais")
PYEOF
```
