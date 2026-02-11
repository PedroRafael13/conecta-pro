#!/bin/sh
# Entrypoint script para AlertManager
# Substitui variáveis de ambiente no arquivo de configuração

CONFIG_FILE=/etc/alertmanager/alertmanager.yml

# Criar configuração a partir do template, substituindo variáveis
cat > "$CONFIG_FILE" << EOF
# AlertManager Configuration - ERP Conecta Mais
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
      continue: true
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
    telegram_configs:
      - bot_token: '${TELEGRAM_BOT_TOKEN}'
        chat_id: ${TELEGRAM_CHAT_ID}
        parse_mode: 'HTML'
        message: |
          {{ if eq .Status "firing" }}🔔 <b>ALERTA</b>{{ else }}✅ <b>RESOLVIDO</b>{{ end }}
          <b>{{ .GroupLabels.alertname }}</b>
          Severidade: {{ .CommonLabels.severity }}
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ end }}
        send_resolved: true
  - name: 'critical-webhook'
    telegram_configs:
      - bot_token: '${TELEGRAM_BOT_TOKEN}'
        chat_id: ${TELEGRAM_CHAT_ID}
        parse_mode: 'HTML'
        message: |
          {{ if eq .Status "firing" }}🚨 <b>CRÍTICO</b>{{ else }}✅ <b>RESOLVIDO</b>{{ end }}
          <b>{{ .GroupLabels.alertname }}</b>
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ .Annotations.description }}
          {{ end }}
        send_resolved: true
  - name: 'email-alerts'
    email_configs:
      - to: 'admin@conectamais.pro'
        headers:
          Subject: '[ALERTA] {{ .GroupLabels.alertname }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'job']
  - source_match:
      alertname: 'InstanceDown'
    target_match:
      alertname: 'HighLatency'
    equal: ['job']
EOF

# Executar o AlertManager com o arquivo gerado
exec /bin/alertmanager \
  --config.file="$CONFIG_FILE" \
  --storage.path=/alertmanager \
  --web.external-url="${WEB_EXTERNAL_URL:-http://localhost:9093}" \
  --web.route-prefix=/ \
  "$@"
