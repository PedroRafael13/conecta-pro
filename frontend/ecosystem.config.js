module.exports = {
  apps: [
    {
      name: 'conecta-pro-frontend',
      script: '.next/standalone/server.js',
      cwd: '/opt/conecta-pro/frontend',
      env: {
        NODE_ENV: 'production',
        PORT: 3001,
        HOSTNAME: '0.0.0.0',
        NODE_OPTIONS: '--max-old-space-size=4096',
      },
      // Restart policy
      max_restarts: 10,
      restart_delay: 5000,
      exp_backoff_restart_delay: 500,
      max_memory_restart: '512M',
      // Logs
      error_file: '/root/.pm2/logs/conecta-pro-frontend-error.log',
      out_file: '/root/.pm2/logs/conecta-pro-frontend-out.log',
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      // Misc
      watch: false,
      autorestart: true,
      kill_timeout: 5000,
    },
  ],
};
