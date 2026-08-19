# AI Media Factory - Database Restore
param([Parameter(Mandatory=$true)][string]$BackupFile)

Write-Host "AI Media Factory - Database Restore" -ForegroundColor Cyan

if (-not (Test-Path $BackupFile)) {
    Write-Host "[FAIL] Backup not found: $BackupFile" -ForegroundColor Red
    exit 1
}

$fileSize = [math]::Round((Get-Item $BackupFile).Length / 1KB, 2)
Write-Host "[...] Restoring from: $BackupFile ($fileSize KB)" -ForegroundColor Yellow
Write-Host "[!] WARNING: This will OVERWRITE current database!" -ForegroundColor Red

$confirm = Read-Host "Are you sure? (type 'yes' to continue)"
if ($confirm -ne "yes") {
    Write-Host "[X] Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host "[...] Stopping backend..." -ForegroundColor Yellow
docker compose stop backend
Start-Sleep -Seconds 5

try {
    Get-Content $BackupFile -Encoding UTF8 | docker exec -i amf_postgres psql -U amf_user -d ai_media_factory 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database restored" -ForegroundColor Green
        Write-Host "[...] Starting backend..." -ForegroundColor Yellow
        docker compose start backend
        Start-Sleep -Seconds 10
        
        $status = docker inspect --format='{{.State.Status}}' amf_backend
        if ($status -eq "running") {
            Write-Host "[OK] Backend is running" -ForegroundColor Green
        } else {
            Write-Host "[!] Backend status: $status" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[FAIL] Restore failed (exit: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}