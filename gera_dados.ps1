# ============================================================
#  GERA DADOS  -  regenera o data.json dos DOIS paineis
#  (roda so a parte de processamento do watch_pwr, SEM subir
#   o servidor local, entao nao trava)
# ============================================================
param(
    [string]$ProjectRoot = $(if ($PSScriptRoot) { $PSScriptRoot } else { "C:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr" })
)

foreach ($panel in 'franquias','lojas-proprias') {
    $wf = Join-Path $ProjectRoot "$panel\watch_pwr.ps1"
    if (-not (Test-Path $wf)) { Write-Host "  (sem watch_pwr em $panel)" -ForegroundColor DarkYellow; continue }

    Write-Host "  Gerando dados de $panel..." -ForegroundColor Cyan
    $lines = Get-Content $wf -Encoding UTF8
    # pega o codigo ate a 1a chamada isolada de Process-ExcelFiles (antes do servidor/watcher)
    $m = $lines | Select-String -Pattern '^\s*Process-ExcelFiles\s*$' | Select-Object -First 1
    $idx = if ($m) { $m.LineNumber } else { 419 }
    $head = $lines[0..($idx-1)]
    # aponta o BASE_DIR para a pasta deste painel (funciona rodando de qualquer lugar)
    $head = $head -replace '\$BASE_DIR\s*=\s*\$PSScriptRoot', ('$BASE_DIR = "' + (Join-Path $ProjectRoot $panel) + '"')

    $tmp = Join-Path $env:TEMP ("regen_" + $panel + ".ps1")
    Set-Content -Path $tmp -Value $head -Encoding UTF8
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tmp
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
Write-Host "Dados dos dois paineis gerados." -ForegroundColor Green
