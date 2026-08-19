# AI Media Factory
# Structure Verification Script

Write-Host "Checking project structure..." -ForegroundColor Cyan

$required = @(
    "backend",
    "engines",
    "core",
    "docs",
    "tests",
    "scripts",
    "AI_CONTEXT.md",
    "STATUS.md",
    "TASK.md",
    "PROJECT_CONTEXT.md"
)


$missing = @()


foreach ($item in $required) {

    if (!(Test-Path $item)) {
        $missing += $item
    }

}


if ($missing.Count -eq 0) {

    Write-Host "Structure OK" -ForegroundColor Green

}
else {

    Write-Host "Missing items:" -ForegroundColor Red

    foreach ($item in $missing) {
        Write-Host "- $item"
    }

}

