# PM2 Windows Startup Configuration Script
# This script configures PM2 to run as a Windows service.

Write-Host "--- Configuring PM2 Persistence on Windows ---" -ForegroundColor Cyan

# 1. Check if PM2 is installed
if (!(Get-Command pm2 -ErrorAction SilentlyContinue)) {
    Write-Error "PM2 is not installed. Please install it with 'npm install -g pm2'."
    exit 1
}

# 2. Install pm2-windows-startup if not present
Write-Host "Checking for pm2-windows-startup..."
try {
    npm list -g pm2-windows-startup --depth=0
} catch {
    Write-Host "Installing pm2-windows-startup..."
    npm install -g pm2-windows-startup
}

# 3. Register the startup script
Write-Host "Registering PM2 as a Windows service..."
pm2-startup install

# 4. Start the orchestrator if not running
Write-Host "Starting the Bronze Vault Orchestrator via PM2..."
pm2 start ecosystem.config.js

# 5. Save the PM2 process list
Write-Host "Saving PM2 process list..."
pm2 save

Write-Host "--- PM2 Persistence Configured ---" -ForegroundColor Green
Write-Host "The orchestrator will now start automatically on Windows boot."
