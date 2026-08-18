<#
.SYNOPSIS
    Генерирует PROJECT_CONTEXT.md - актуальный "слепок" состояния проекта AI Media Factory.

.USAGE
    .\scripts\Update-ProjectContext.ps1
    .\scripts\Update-ProjectContext.ps1 -RootPath "C:\Projects\ai-media-factory"
#>

param(
    [string]$RootPath = (Get-Location).Path,
    [string]$OutputFile = "PROJECT_CONTEXT.md"
)

$ExcludeDirs = @(
    'venv', '.venv', '__pycache__', '.git', 'node_modules',
    '.pytest_cache', '.idea', '.vscode', 'dist', 'build', '.mypy_cache'
)

function Get-CleanTree {
    param(
        [string]$Path,
        [string]$Indent = ""
    )

    $items = Get-ChildItem -LiteralPath $Path -Force |
        Where-Object {
            $_.Name -notin $ExcludeDirs -and
            $_.Name -notmatch '\.egg-info$' -and
            $_.Name -ne $OutputFile
        } |
        Sort-Object @{Expression = { $_.PSIsContainer }; Descending = $true }, Name

    $lines = @()
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            $lines += "$Indent├── $($item.Name)/"
            $lines += Get-CleanTree -Path $item.FullName -Indent "$Indent│   "
        }
        else {
            $lines += "$Indent├── $($item.Name)"
        }
    }
    return $lines
}

function Add-FileSection {
    param(
        [System.Text.StringBuilder]$Builder,
        [string]$Title,
        [string]$FilePath,
        [string]$FenceLang = ""
    )

    [void]$Builder.AppendLine("## $Title")
    if (Test-Path $FilePath) {
        if ($FenceLang -ne "") {
            [void]$Builder.AppendLine('```' + $FenceLang)
            [void]$Builder.AppendLine((Get-Content $FilePath -Raw))
            [void]$Builder.AppendLine('```')
        }
        else {
            [void]$Builder.AppendLine((Get-Content $FilePath -Raw))
        }
    }
    else {
        [void]$Builder.AppendLine("_Файл не найден: $(Split-Path $FilePath -Leaf)_")
    }
    [void]$Builder.AppendLine("")
}

$sb = New-Object System.Text.StringBuilder
$now = Get-Date -Format "yyyy-MM-dd HH:mm"

[void]$sb.AppendLine("# PROJECT CONTEXT — AI Media Factory")
[void]$sb.AppendLine("_Автоматически сгенерировано: $now_")
[void]$sb.AppendLine("")

Add-FileSection -Builder $sb -Title "📌 Текущий статус проекта" -FilePath (Join-Path $RootPath "STATUS.md")

[void]$sb.AppendLine("## 📁 Структура проекта")
[void]$sb.AppendLine('```')
[void]$sb.AppendLine((Split-Path $RootPath -Leaf) + "/")
Get-CleanTree -Path $RootPath | ForEach-Object { [void]$sb.AppendLine($_) }
[void]$sb.AppendLine('```')
[void]$sb.AppendLine("")

[void]$sb.AppendLine("## 📦 Зависимости")
$depFiles = @("requirements.txt", "pyproject.toml", "package.json")
$foundDeps = $false
foreach ($df in $depFiles) {
    $p = Join-Path $RootPath $df
    if (Test-Path $p) {
        $foundDeps = $true
        [void]$sb.AppendLine("### $df")
        [void]$sb.AppendLine('```')
        [void]$sb.AppendLine((Get-Content $p -Raw))
        [void]$sb.AppendLine('```')
    }
}
if (-not $foundDeps) { [void]$sb.AppendLine("_Файлы зависимостей не найдены._") }
[void]$sb.AppendLine("")

Add-FileSection -Builder $sb -Title "🐳 Docker Compose" -FilePath (Join-Path $RootPath "docker-compose.yml") -FenceLang "yaml"
Add-FileSection -Builder $sb -Title "📖 README" -FilePath (Join-Path $RootPath "README.md")

[void]$sb.AppendLine("## 🕒 Последние 15 коммитов")
[void]$sb.AppendLine('```')
try {
    $gitLog = git -C $RootPath log -15 --pretty=format:"%h | %ad | %an | %s" --date=short 2>$null
    if ($gitLog) {
        [void]$sb.AppendLine(($gitLog -join "`n"))
    }
    else {
        [void]$sb.AppendLine("Нет данных git log (репозиторий не инициализирован или нет коммитов).")
    }
}
catch {
    [void]$sb.AppendLine("Git недоступен или это не git-репозиторий.")
}
[void]$sb.AppendLine('```')

$outputPath = Join-Path $RootPath $OutputFile
$sb.ToString() | Set-Content -Path $outputPath -Encoding UTF8

Write-Host "✅ Файл '$OutputFile' успешно создан/обновлён: $outputPath" -ForegroundColor Green
