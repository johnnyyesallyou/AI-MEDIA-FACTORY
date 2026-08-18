<#
.SYNOPSIS
    Smoke-test всех API v1 эндпоинтов AI Media Factory Dashboard.

.USAGE
    .\scripts\Test-DashboardAPI.ps1
    .\scripts\Test-DashboardAPI.ps1 -BaseUrl "http://localhost:8000"
#>

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$Endpoints = @(
    @{ Name = "Dashboard Health";        Path = "/api/v1/dashboard/health" }
    @{ Name = "Dashboard Stats";         Path = "/api/v1/dashboard/stats" }
    @{ Name = "Channels List";           Path = "/api/v1/channels/" }
    @{ Name = "Content Lifecycle";       Path = "/api/v1/content/" }
    @{ Name = "AI Models";               Path = "/api/v1/ai/models" }
    @{ Name = "AI Routing";              Path = "/api/v1/ai/routing" }
    @{ Name = "Automation Settings";     Path = "/api/v1/automation/" }
    @{ Name = "Analytics Overview";      Path = "/api/v1/analytics/overview" }
    @{ Name = "Analytics Best Performers"; Path = "/api/v1/analytics/best-performers" }
    @{ Name = "Analytics Time Series";   Path = "/api/v1/analytics/time-series" }
    @{ Name = "Knowledge Insights";      Path = "/api/v1/knowledge/insights" }
    @{ Name = "Assets Library";          Path = "/api/v1/assets/" }
    @{ Name = "Integrations";            Path = "/api/v1/integrations/" }
    @{ Name = "Logs";                    Path = "/api/v1/logs/" }
    @{ Name = "Users";                   Path = "/api/v1/users/" }
    @{ Name = "Users Me";                Path = "/api/v1/users/me" }
    @{ Name = "Settings";                Path = "/api/v1/settings/" }
    @{ Name = "OpenAPI schema";          Path = "/openapi.json" }
)

$results = @()

Write-Host "`n=== AI Media Factory - API Smoke Test ===" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl`n"

foreach ($ep in $Endpoints) {
    $url = "$BaseUrl$($ep.Path)"
    $status = $null
    $preview = ""
    $ok = $false

    try {
        $resp = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $status = [int]$resp.StatusCode
        $ok = ($status -ge 200 -and $status -lt 300)
        $rawPreview = $resp.Content
        if ($rawPreview.Length -gt 120) { $rawPreview = $rawPreview.Substring(0, 120) + "..." }
        $preview = $rawPreview
    }
    catch {
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        else {
            $status = "N/A"
        }
        $preview = $_.Exception.Message
        $ok = $false
    }

    $color = if ($ok) { "Green" } elseif ($status -eq 404) { "Yellow" } else { "Red" }
    $icon = if ($ok) { "OK" } elseif ($status -eq 404) { "??" } else { "XX" }

    Write-Host "$icon [$status] $($ep.Name)" -ForegroundColor $color
    Write-Host "     $url" -ForegroundColor DarkGray
    if (-not $ok) {
        Write-Host "     $preview" -ForegroundColor DarkGray
    }

    $results += [PSCustomObject]@{
        Name   = $ep.Name
        Path   = $ep.Path
        Status = $status
        OK     = $ok
    }
}

Write-Host "`n=== Итог ===" -ForegroundColor Cyan
$passed = ($results | Where-Object { $_.OK }).Count
$total  = $results.Count
Write-Host "Прошло: $passed / $total" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

$failed = $results | Where-Object { -not $_.OK }
if ($failed.Count -gt 0) {
    Write-Host "`nНе прошли:" -ForegroundColor Red
    $failed | Format-Table Name, Path, Status -AutoSize
}
