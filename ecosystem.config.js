module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python',
      interpreter_args: '-u',
      env: {
        DRY_RUN: 'false',
        START_FS_WATCHER: 'false'
      },
      env_production: {
        DRY_RUN: 'false',
        START_FS_WATCHER: 'false'
      },
      autorestart: true,
      restart_delay: 5000
    },
    {
      name: 'filesystem-watcher',
      script: 'filesystem_watcher.py',
      interpreter: 'python',
      interpreter_args: '-u',
      env: {
        DRY_RUN: 'false'
      },
      env_production: {
        DRY_RUN: 'false'
      },
      autorestart: true,
      restart_delay: 5000
    }
  ]
};
