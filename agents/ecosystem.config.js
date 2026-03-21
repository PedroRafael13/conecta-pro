module.exports = {
  apps: [
    {
      name: 'telegram-assistant',
      script: '/opt/conecta-pro/agents/telegram_assistant.py',
      interpreter: 'python3',
      cwd: '/opt/conecta-pro',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      max_restarts: 10,
      restart_delay: 5000,
      autorestart: true,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/opt/conecta-pro/logs/telegram-assistant-error.log',
      out_file: '/opt/conecta-pro/logs/telegram-assistant.log',
      merge_logs: true,
    },
  ],
};
