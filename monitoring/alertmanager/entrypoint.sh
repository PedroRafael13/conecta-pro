#!/bin/sh
# Entrypoint script para AlertManager
# Alertas vão APENAS para OpenClaw webhook (que notifica Telegram com contexto)
# Telegram removido do Alertmanager para evitar duplicatas

CONFIG_FILE=/etc/alertmanager/alertmanager.yml

cat > "$CONFIG_FILE" << EOF
# AlertManager Configuration - ERP Conecta Mais
# Telegram removido — OpenClaw é o único notificador (com diagnóstico + throttle)
global:
  resolve_timeout: 5m
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@conectamais.pro'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

route:
  receiver: 'default-webhook'
  group_by: ['alertname', 'severity', 'job']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'critical-webhook'
      repeat_interval: 1h
    - match:
        severity: warning
      receiver: 'default-webhook'
      group_wait: 1m
      repeat_interval: 8h
    - match:
        severity: info
      receiver: 'default-webhook'
      group_wait: 5m
      repeat_interval: 24h

receivers:
  - name: 'default-webhook'
    webhook_configs:
      - url: 'http://172.19.0.1:8080/api/v1/ai/openclaw/alert-webhook'
        send_resolved: true
  - name: 'critical-webhook'
    webhook_configs:
      - url: 'http://172.19.0.1:8080/api/v1/ai/openclaw/alert-webhook'
        send_resolved: true
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'job']
EOF

exec /bin/alertmanager \
  --config.file="$CONFIG_FILE" \
  --storage.path=/alertmanager \
  --web.external-url="${WEB_EXTERNAL_URL:-http://localhost:9093}" \
  --web.route-prefix=/ \
  "$@"
