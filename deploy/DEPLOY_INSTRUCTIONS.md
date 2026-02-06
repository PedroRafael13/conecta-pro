# Conecta PRO - Instrucoes de Deploy

## Informacoes do Ambiente

| Item | Valor |
|------|-------|
| Dominio | conectamais.pro |
| VPS IP | 82.25.75.74 |
| VPS ID | 1134814 |
| Hostname | srv1134814.hstgr.cloud |
| OS | Ubuntu 24.04 LTS |
| Specs | 4 CPUs, 16GB RAM, 200GB disk |

## Pre-Requisitos

- [x] Integracao Hostinger API configurada
- [x] Backend Conecta PRO desenvolvido
- [x] Testes passando (1057/1058)
- [ ] DNS atualizado para 82.25.75.74
- [ ] SSL configurado
- [ ] Nginx configurado
- [ ] Docker instalado no VPS

## Passo a Passo do Deploy

### 1. Atualizar DNS (quando pronto)

```bash
export HOSTINGER_API_TOKEN='seu_token'
./deploy/update-dns.sh
```

Ou via API diretamente:
```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/conectamais.pro" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "zone": [
      {
        "name": "@",
        "type": "A",
        "ttl": 300,
        "records": [{"content": "82.25.75.74"}]
      }
    ],
    "overwrite": false
  }'
```

### 2. Configurar VPS

```bash
# SSH para o VPS
ssh root@82.25.75.74

# Instalar Docker (se necessario)
curl -fsSL https://get.docker.com | sh

# Instalar Certbot
apt update && apt install -y certbot python3-certbot-nginx

# Clonar projeto
cd /opt
git clone <repo> conecta-pro
cd conecta-pro
```

### 3. Configurar Nginx

```bash
# Criar configuracao
cat > /etc/nginx/sites-available/conecta-pro << 'EOF'
server {
    listen 80;
    server_name conectamais.pro www.conectamais.pro;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/conecta-pro /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 4. Obter SSL

```bash
certbot --nginx -d conectamais.pro -d www.conectamais.pro
```

### 5. Deploy da Aplicacao

```bash
cd /opt/conecta-pro
docker compose up -d
```

### 6. Verificar

```bash
# Health check
curl https://conectamais.pro/health

# Logs
docker compose logs -f
```

## Comandos Uteis

```bash
# Ver status VPS via API
curl -s "https://developers.hostinger.com/api/vps/v1/virtual-machines/1134814" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Ver DNS atual
curl -s "https://developers.hostinger.com/api/dns/v1/zones/conectamais.pro" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Restart VPS via API
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/1134814/restart" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Contatos

- Hostinger Support: support.hostinger.com
- VPS ID: 1134814
- Subscription: AzZJggV2pCsGa2NJi
