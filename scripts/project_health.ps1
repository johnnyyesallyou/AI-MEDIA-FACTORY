# AI Media Factory
# Project Health Check


Write-Host ""
Write-Host "================================="
Write-Host "AI MEDIA FACTORY HEALTH CHECK"
Write-Host "================================="
Write-Host ""


Write-Host "1. Structure"
Write-Host "----------------"

.\scripts\verify_structure.ps1


Write-Host ""
Write-Host "2. Documentation"
Write-Host "----------------"

.\scripts\check_docs.ps1


Write-Host ""
Write-Host "3. Python Environment"
Write-Host "----------------"


if (Test-Path ".venv") {

Write-Host "Virtual environment detected" -ForegroundColor Green

}
else {

Write-Host "Virtual environment missing" -ForegroundColor Yellow

}



Write-Host ""
Write-Host "4. Docker"
Write-Host "----------------"


if (Test-Path "docker-compose.yml") {

Write-Host "Docker configuration detected" -ForegroundColor Green

}
else {

Write-Host "docker-compose.yml missing" -ForegroundColor Yellow

}



Write-Host ""
Write-Host "Health check completed"

