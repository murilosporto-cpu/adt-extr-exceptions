# ============================================================
#  VALIDADOR DE EXTRACAO PWR  -  a "trava de seguranca"
#  ------------------------------------------------------------
#  Confere o CONTEUDO de cada planilha baixada (nao so o nome):
#    - arquivo "...Exceptions..."  deve ter a aba "KEYS Service Exceptions"
#    - arquivo "Keys Summary..."   deve ter a aba com "Summary"
#  Se o conteudo nao bate com o nome (ex.: baixaram Summary e salvaram
#  como Exceptions), o arquivo e MOVIDO para _lixeira_pwr\_conteudo_errado
#  e reportado. Assim, dado errado NUNCA entra no data.json sem avisar.
#
#  Rodar DEPOIS de baixar e ANTES de gerar o data.json.
#  Se acusar erro, rode 'plano_extracao.ps1 -Apply' de novo e rebaixe.
# ============================================================
param(
    [string]$ProjectRoot = $(if ($PSScriptRoot) { $PSScriptRoot } else { "C:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr" })
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-SheetNames([string]$xlsxPath) {
    $names = @()
    try {
        $zip = [System.IO.Compression.ZipFile]::OpenRead($xlsxPath)
        $entry = $zip.Entries | Where-Object { $_.FullName -eq 'xl/workbook.xml' }
        if ($entry) {
            $sr = New-Object System.IO.StreamReader($entry.Open())
            $xml = $sr.ReadToEnd(); $sr.Close()
            [regex]::Matches($xml, '<sheet[^>]*?name="([^"]+)"') | ForEach-Object { $names += $_.Groups[1].Value }
        }
        $zip.Dispose()
    } catch { }
    return $names
}

$problemas = 0
$conferidos = 0

foreach ($p in 'franquias','lojas-proprias') {
    foreach ($sub in 'pwr_reports','pwr_reports_mensal') {
        $dir = Join-Path $ProjectRoot "$p\$sub"
        if (-not (Test-Path $dir)) { continue }

        Get-ChildItem $dir -Filter *.xlsx -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike '*consultor*' } | ForEach-Object {
            $conferidos++
            $abas = Get-SheetNames $_.FullName
            $abasTxt = $abas -join ', '

            $ehException = $_.Name -like '*Exceptions*'
            $ehSummary   = $_.Name -like 'Keys Summary*'

            $conteudoException = ($abas | Where-Object { $_ -like '*Service Exceptions*' }).Count -gt 0
            $conteudoSummary   = ($abas | Where-Object { $_ -like '*Summary*' }).Count -gt 0

            $errado = $false
            $motivo = ''
            if ($ehException -and -not $conteudoException) { $errado = $true; $motivo = "nome diz Exceptions mas a aba e '$abasTxt' (conteudo de Summary)" }
            elseif ($ehSummary -and -not $conteudoSummary) { $errado = $true; $motivo = "nome diz Summary mas a aba e '$abasTxt'" }

            if ($errado) {
                $problemas++
                $lixo = Join-Path $dir "_lixeira_pwr\_conteudo_errado"
                New-Item -ItemType Directory -Path $lixo -Force | Out-Null
                Move-Item -LiteralPath $_.FullName -Destination (Join-Path $lixo $_.Name) -Force
                Write-Host "  [ERRADO] $p\$sub :: $($_.Name)" -ForegroundColor Red
                Write-Host "           -> $motivo  (movido para a lixeira)" -ForegroundColor DarkYellow
            }
        }
    }
}

Write-Host ""
if ($problemas -eq 0) {
    Write-Host "OK! $conferidos arquivos conferidos, todos com o conteudo certo." -ForegroundColor Green
    exit 0
} else {
    Write-Host "ATENCAO: $problemas arquivo(s) com CONTEUDO ERRADO foram movidos para a lixeira." -ForegroundColor Red
    Write-Host "         Rode 'plano_extracao.ps1 -Apply' e rebaixe esses itens (relatorio CORRETO no PWR)." -ForegroundColor Yellow
    exit 1
}
