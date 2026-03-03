module.exports = {
  apps: [
    {
      name: 'bronze-vault-orchestrator',
      script: 'src/orchestrator.py',
      interpreter: 'python',
      interpreter_args: '-u',
      env: {
        DRY_RUN: 'true'
      },
      env_production: {
        DRY_RUN: 'false'
      },
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: '.pm2/error.log',
      out_file: '.pm2/out.log',
      merge_logs: true
    }
  ]
};
