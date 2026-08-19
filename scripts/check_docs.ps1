# AI Media Factory
# Documentation Verification


Write-Host "Checking documentation..." -ForegroundColor Cyan


$requiredDocs = @(

"docs\architecture\ARCHITECTURE.md",

"docs\architecture\EVENT_BUS.md",

"docs\architecture\PIPELINES.md",

"docs\backend\DATABASE.md",

"docs\backend\API_CONTRACT.md",

"docs\ai\AGENTS.md",

"docs\ai\MODELS.md",

"docs\development\TESTING.md"

)



$missing = @()



foreach ($doc in $requiredDocs) {


if (!(Test-Path $doc)) {

$missing += $doc

}

}



if ($missing.Count -eq 0) {


Write-Host "Documentation OK" -ForegroundColor Green


}

else {


Write-Host "Missing documentation:" -ForegroundColor Red


foreach ($doc in $missing){

Write-Host "- $doc"

}


}

