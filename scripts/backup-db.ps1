# AI Media Factory - Database Backup
param([string]$OutputDir = ".\backups")

Write-Host "AI Media Factory - Database Backup" -ForegroundColor Cyan

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "[OK] Created directory: $OutputDir" -ForegroundColor Green
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = Join-Path $OutputDir "ai_media_factory_$timestamp.sql"

Write-Host "[...] Creating backup: $backupFile" -ForegroundColor Yellow

try {
    docker exec amf_postgres pg_dump -U amf_user -d ai_media_factory > $backupFile
    
    if ($LASTEXITCODE -eq 0 -and (Get-Item $backupFile).Length -gt 100) {
        $fileSize = [math]::Round((Get-Item $backupFile).Length / 1KB, 2)
        Write-Host "[OK] Backup created: $fileSize KB" -ForegroundColor Green
        return $backupFile
    } else {
        Write-Host "[FAIL] Backup failed or empty" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}