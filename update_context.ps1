$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$outputFile = "project_context.txt"
$content = @()

# 1. СТАТУС ПРОЕКТА
$content += "=== СТАТУС ПРОЕКТА ==="
if (Test-Path "STATUS.md") {
    $content += Get-Content "STATUS.md" -Encoding UTF8
} else {
    $content += "Файл STATUS.md не найден. Создайте его для отслеживания статуса."
}
$content += ""

# 2. СТРУКТУРА ПАПОК (Исключаем мусор)
$content += "=== СТРУКТУРА ПАПОК И ФАЙЛОВ ==="
$treeOutput = cmd /c "tree /A /F" | Where-Object { 
    $_ -notmatch '__pycache__|venv|node_modules|\.git\\|\.idea|\.vscode|\.pytest_cache|\.mypy_cache' 
}
$content += $treeOutput
$content += ""

# 3. ЗАВИСИМОСТИ
$content += "=== ЗАВИСИМОСТИ (Python/Node) ==="
if (Test-Path "requirements.txt") {
    $content += "--- requirements.txt ---"
    $content += Get-Content "requirements.txt" -Encoding UTF8
}
if (Test-Path "pyproject.toml") {
    $content += "--- pyproject.toml ---"
    $content += Get-Content "pyproject.toml" -Encoding UTF8
}
$content += ""

# 4. DOCKER
$content += "=== DOCKER И ОКРУЖЕНИЕ ==="
if (Test-Path "docker-compose.yml") {
    $content += Get-Content "docker-compose.yml" -Encoding UTF8
} else {
    $content += "docker-compose.yml не найден."
}
$content += ""

# 5. README
$content += "=== README ==="
if (Test-Path "README.md") {
    $content += Get-Content "README.md" -Encoding UTF8
} else {
    $content += "README.md не найден."
}
$content += ""

# 6. GIT LOG
$content += "=== ПОСЛЕДНИЕ 15 КОММИТОВ (Git) ==="
try {
    $gitLog = git log -15 --oneline 2>&1
    if ($LASTEXITCODE -eq 0) {
        $content += $gitLog
    } else {
        $content += "Git репозиторий не инициализирован."
    }
} catch {
    $content += "Ошибка при получении Git log."
}

# Сохраняем в файл
$content | Out-File -FilePath $outputFile -Encoding utf8
Write-Host "`n✅ Файл '$outputFile' успешно обновлен!" -ForegroundColor Green
Write-Host "📂 Структура очищена от мусора (venv, __pycache__, .git)." -ForegroundColor Cyan