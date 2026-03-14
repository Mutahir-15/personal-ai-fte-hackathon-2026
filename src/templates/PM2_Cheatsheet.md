# PM2 Cheatsheet for AI Employee

## 🚀 Basic Commands
- `pm2 start ecosystem.config.js`: Start all processes
- `pm2 stop <name|id|all>`: Stop processes
- `pm2 restart <name|id|all>`: Restart processes
- `pm2 delete <name|id|all>`: Remove processes from PM2

## 📊 Monitoring
- `pm2 status`: List all processes and their status
- `pm2 logs`: View real-time logs
- `pm2 monit`: Open interactive monitoring dashboard

## 💾 Persistence
- `pm2 save`: Save current process list
- `pm2 startup`: Generate startup script

## 🛠️ Management
- `pm2 flush`: Clear all logs
- `pm2 reload all`: Zero-downtime reload
