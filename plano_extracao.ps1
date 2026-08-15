# ============================================================
#  PLANO DE EXTRACAO PWR  -  o "cerebro" da automacao
#  ------------------------------------------------------------
#  Dada a data de hoje, calcula EXATAMENTE quais arquivos devem
#  existir em cada pasta e:
#    - gera "downloads_pendentes.json"  -> o robo baixa esses
#    - (com -Apply) move os arquivos errados/velhos p/ _lixeira_pwr
#  Principio unico: tudo reflete o dado fechado ATE ONTEM.
#  Nao depende do estado anterior -> se autocorrige, sem looping.
#
#  VOLATIL = arquivo que muda todo dia (semana atual, acumulado,
#  mes corrente). Esses sao SEMPRE re-baixados e qualquer versao
#  antiga vai pra lixeira, pra nunca sobrar um orfao confundindo.
# ============================================================
param(
    [datetime]$Today       = (Get-Date).Date,
    [string]  $ProjectRoot = $(if ($PSScriptRoot) { $PSScriptRoot } else { "C:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr" }),
    [switch]  $Apply        # sem isto = so mostra (nao mexe em nada)
)

function MondayOf([datetime]$d) { $off = ([int]$d.DayOfWeek + 6) % 7; return $d.AddDays(-$off) }

$yesterday = $Today.AddDays(-1)   # PWR so fecha ate ontem

# ---------- PERIODOS SEMANAIS: 4 semanas + 1 acumulado ----------
$weekly = New-Object System.Collections.ArrayList
$curMon = MondayOf $yesterday
[void]$weekly.Add([pscustomobject]@{ Start=$curMon; End=$yesterday; Acc=$false; Volatil=$true })    # semana atual (muda todo dia)
for ($i=1; $i -le 3; $i++) { $s=$curMon.AddDays(-7*$i); [void]$weekly.Add([pscustomobject]@{ Start=$s; End=$s.AddDays(6); Acc=$false; Volatil=$false }) }  # semanas fechadas
$accStart = Get-Date -Year $yesterday.Year -Month $yesterday.Month -Day 1
[void]$weekly.Add([pscustomobject]@{ Start=$accStart; End=$yesterday; Acc=$true; Volatil=$true })   # acumulado (muda todo dia)

# ---------- PERIODOS MENSAIS: jan ate o mes de ontem ----------
$monthly = New-Object System.Collections.ArrayList
for ($m=1; $m -le $yesterday.Month; $m++) {
    $s = Get-Date -Year $yesterday.Year -Month $m -Day 1
    if ($m -eq $yesterday.Month) { $e=$yesterday; $vol=$true } else { $e=$s.AddMonths(1).AddDays(-1); $vol=$false }  # mes corrente = volatil
    [void]$monthly.Add([pscustomobject]@{ Start=$s; End=$e; Volatil=$vol })
}

function FileName($report, $scope, $start, $end, $acc) {
    if ($report -eq 'summary') { $prefix = "Keys Summary - $scope (Stores)" }
    else { $prefix = "KEYS Service Main Service Exceptions - $scope (Stores)" }
    $range  = "({0:yyyy-MM-dd} - {1:yyyy-MM-dd})" -f $start, $end
    $suffix = if ($acc) { " acumulado" } else { "" }
    return "$prefix$range$suffix.xlsx"
}

$dashboards = @(
    [pscustomobject]@{ Folder='franquias';      Scope='Franquias' },
    [pscustomobject]@{ Folder='lojas-proprias'; Scope='Lojas Corporativas' }
)

Write-Host ("HOJE: {0:yyyy-MM-dd} ({1})  ->  dado fechado ate ONTEM: {2:yyyy-MM-dd}`n" -f $Today, $Today.DayOfWeek, $yesterday) -ForegroundColor Cyan

$downloadQueue = New-Object System.Collections.ArrayList

foreach ($d in $dashboards) {
    Write-Host ("################  $($d.Folder.ToUpper())  ################") -ForegroundColor Yellow
    $wDir = Join-Path $ProjectRoot "$($d.Folder)\pwr_reports"
    $mDir = Join-Path $ProjectRoot "$($d.Folder)\pwr_reports_mensal"

    # monta alvos (com Volatil + metadados p/ o robo)
    $targets = New-Object System.Collections.ArrayList
    foreach ($rep in 'summary','exceptions') {
        foreach ($w in $weekly)   { [void]$targets.Add([pscustomobject]@{ Pasta=$wDir; Folder=$d.Folder; Report=$rep; Scope=$d.Scope; Inicio=$w.Start;  Fim=$w.End;  Volatil=$w.Volatil;  Nome=(FileName $rep $d.Scope $w.Start  $w.End  $w.Acc) }) }
        foreach ($mo in $monthly) { [void]$targets.Add([pscustomobject]@{ Pasta=$mDir; Folder=$d.Folder; Report=$rep; Scope=$d.Scope; Inicio=$mo.Start; Fim=$mo.End; Volatil=$mo.Volatil; Nome=(FileName $rep $d.Scope $mo.Start $mo.End $false) }) }
    }

    foreach ($grp in @(@{Dir=$wDir;Lbl='SEMANAL'}, @{Dir=$mDir;Lbl='MENSAL'})) {
        $dir = $grp.Dir
        $here          = @($targets | Where-Object { $_.Pasta -eq $dir })
        $targetNames   = @($here | ForEach-Object Nome)
        $volatilNames  = @($here | Where-Object { $_.Volatil } | ForEach-Object Nome)
        $atual         = @(Get-ChildItem $dir -Filter *.xlsx -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike '*consultor*' } | ForEach-Object Name)

        # baixar: tudo que esta faltando (nome do alvo nao presente na pasta)
        # (a frescura diaria vem de graca: a data-fim esta no nome, entao a semana
        #  atual / acumulado / mes corrente ganham nome novo a cada dia = "faltando")
        $toDownload = $here | Where-Object { $atual -notcontains $_.Nome }
        # remover: presente que nao e alvo (sobra). O CONTEUDO errado quem pega e o validar_extracao.ps1
        $toRemove   = $atual | Where-Object { $targetNames -notcontains $_ }

        Write-Host "  [$($grp.Lbl)] baixar: $(@($toDownload).Count)  |  remover/limpar: $(@($toRemove).Count)"
        foreach ($f in $toDownload) { [void]$downloadQueue.Add($f) }

        if ($Apply -and @($toRemove).Count -gt 0) {
            $lixo = Join-Path $dir "_lixeira_pwr"
            New-Item -ItemType Directory -Path $lixo -Force | Out-Null
            foreach ($s in $toRemove) { Move-Item -LiteralPath (Join-Path $dir $s) -Destination (Join-Path $lixo $s) -Force; Write-Host "      -> lixeira: $s" -ForegroundColor DarkGray }
        }
    }
    Write-Host ""
}

# ---------- Salva a fila de downloads para o robo ----------
$outJson = Join-Path $ProjectRoot "downloads_pendentes.json"
$queueOut = $downloadQueue | ForEach-Object {
    [pscustomobject]@{
        painel       = $_.Folder
        relatorio    = $_.Report
        scope        = $_.Scope
        data_inicio  = ("{0:yyyy-MM-dd}" -f $_.Inicio)
        data_fim     = ("{0:yyyy-MM-dd}" -f $_.Fim)
        pasta        = $_.Pasta
        nome_arquivo = $_.Nome
    }
}
$queueOut | ConvertTo-Json -Depth 4 | Set-Content -Path $outJson -Encoding UTF8

Write-Host ("=> $(@($downloadQueue).Count) downloads pendentes salvos em: downloads_pendentes.json") -ForegroundColor Green
if (-not $Apply) { Write-Host "   (modo VISUALIZACAO - nao movi nada. Use -Apply para arrumar as pastas.)" -ForegroundColor DarkYellow }
