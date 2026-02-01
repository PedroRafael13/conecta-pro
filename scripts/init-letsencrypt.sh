#!/bin/bash
# ==========================================================================
# Inicialização SSL com Let's Encrypt - Conecta PRO
# Uso: sudo bash scripts/init-letsencrypt.sh
# ==========================================================================

set -e

DOMAIN="${NGINX_HOST:-erp.conectamais.pro}"
EMAIL="${LETSENCRYPT_EMAIL:-admin@conectamais.pro}"
CERT_PATH="/opt/conecta-pro/certs"
WEBROOT="/opt/conecta-pro/certbot"

echo "=== Inicializando SSL para ${DOMAIN} ==="

# 1. Instalar certbot se necessário
if ! command -v certbot &> /dev/null; then
    echo "Instalando certbot..."
    apt-get update
    apt-get install -y certbot
fi

# 2. Criar diretórios
mkdir -p "${CERT_PATH}" "${WEBROOT}"

# 3. Gerar certificado
echo "Gerando certificado para ${DOMAIN}..."
certbot certonly \
    --webroot \
    --webroot-path="${WEBROOT}" \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "${DOMAIN}"

# 4. Copiar certificados para path do Nginx
echo "Copiando certificados..."
mkdir -p "${CERT_PATH}/live/${DOMAIN}"
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem "${CERT_PATH}/live/${DOMAIN}/"
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem "${CERT_PATH}/live/${DOMAIN}/"

# 5. Configurar auto-renewal via cron
CRON_JOB="0 0 1 * * certbot renew --quiet --deploy-hook 'docker exec conecta-pro-nginx nginx -s reload'"
(crontab -l 2>/dev/null | grep -v certbot; echo "${CRON_JOB}") | crontab -

# 6. Reload nginx
docker exec conecta-pro-nginx nginx -s reload 2>/dev/null || echo "Nginx não está rodando (será carregado no próximo docker-compose up)"

echo "=== SSL configurado com sucesso! ==="
echo "Certificado: ${CERT_PATH}/live/${DOMAIN}/"
echo "Auto-renewal: Configurado via cron (1x/mês)"
