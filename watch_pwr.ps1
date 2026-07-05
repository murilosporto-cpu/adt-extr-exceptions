# Script de Automação para Relatórios PWR Domino's
# Inicia um servidor Web local e monitora a pasta 'pwr_reports' para reprocessar planilhas Excel.

$BASE_DIR = Resolve-Path "C:\Users\Murilo Porto\.gemini\antigravity\scratch\cafe com pwr"
$REPORTS_DIR = Join-Path $BASE_DIR "pwr_reports"
$APP_DIR = Join-Path $BASE_DIR "app"
$DATA_JSON = Join-Path $APP_DIR "data.json"
$STORES_JSON = Join-Path $APP_DIR "stores_mapping.json"

# Garante a existência dos diretórios
if (-not (Test-Path $REPORTS_DIR)) { New-Item -ItemType Directory -Path $REPORTS_DIR -Force }
if (-not (Test-Path $APP_DIR)) { New-Item -ItemType Directory -Path $APP_DIR -Force }

# Funções de conversão seguras
function Get-SafeDouble {
    param($val)
    if ($val -eq $null) { return 0.0 }
    $strVal = [string]$val
    
    $strVal = $strVal -replace "`r", ""
    $strVal = $strVal -replace "`n", ""
    $strVal = $strVal -replace "`t", ""
    $strVal = $strVal -replace " ", ""
    $strVal = $strVal -replace [string][char]160, ""
    $strVal = $strVal -replace '\s+', ''
    $strVal = $strVal.Trim()
    if ($strVal -eq "") { return 0.0 }
    
    if ($strVal -like "*%") {
        $strVal = $strVal -replace "%", ""
        $strVal = $strVal.Trim()
        $outVal = 0.0
        if ([double]::TryParse($strVal, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$outVal)) {
            return ($outVal / 100.0)
        }
        if ([double]::TryParse($strVal, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::CurrentCulture, [ref]$outVal)) {
            return ($outVal / 100.0)
        }
    }
    
    $outVal = 0.0
    if ([double]::TryParse($strVal, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$outVal)) {
        return $outVal
    }
    if ([double]::TryParse($strVal, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::CurrentCulture, [ref]$outVal)) {
        return $outVal
    }
    
    try {
        $clean = $strVal -replace ",", "." -replace " ", ""
        return [System.Convert]::ToDouble($clean, [System.Globalization.CultureInfo]::InvariantCulture)
    } catch {
        try {
            $clean = $strVal -replace "\.", "," -replace " ", ""
            return [System.Convert]::ToDouble($clean, [System.Globalization.CultureInfo]::GetCultureInfo("pt-BR"))
        } catch {
            return 0.0
        }
    }
}

function Get-SafeInt {
    param($val)
    if ($val -eq $null) { return 0 }
    $strVal = [string]$val
    
    $strVal = $strVal -replace "`r", ""
    $strVal = $strVal -replace "`n", ""
    $strVal = $strVal -replace "`t", ""
    $strVal = $strVal -replace " ", ""
    $strVal = $strVal -replace [string][char]160, ""
    $strVal = $strVal -replace '\s+', ''
    $strVal = $strVal.Trim()
    if ($strVal -eq "") { return 0 }
    
    $outVal = 0
    if ([int]::TryParse($strVal, [ref]$outVal)) {
        return $outVal
    }
    
    $dblVal = Get-SafeDouble $val
    return [int]$dblVal
}

# Função para extrair dados dos arquivos de Excel
function Process-ExcelFiles {
    Write-Host "Processando planilhas de Excel em: $REPORTS_DIR..."
    
    # Carrega mapeamento persistido de lojas
    $stores = @{}
    if (Test-Path $STORES_JSON) {
        try {
            $existing = Get-Content $STORES_JSON -Raw | ConvertFrom-Json
            foreach ($prop in $existing.PSObject.Properties) {
                $stores[$prop.Name] = @{
                    "id" = $prop.Value.id
                    "name" = $prop.Value.name
                    "status" = $prop.Value.status
                    "consultant" = $prop.Value.consultant
                    "franchisee" = $prop.Value.franchisee
                }
            }
            Write-Host "  -> Carregado mapeamento de $($stores.Count) lojas de stores_mapping.json"
        } catch {
            Write-Warning "Falha ao carregar stores_mapping.json: $_"
        }
    }
    
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false

    try {
        $adtData = @{ "acumulado" = @(); "weeks" = @{} }
        $exceptionData = @{ "acumulado" = @(); "weeks" = @{} }
        $weekStartDates = @{ }

        $files = Get-ChildItem -Path $REPORTS_DIR -Filter "*.xlsx" -File
        
        foreach ($file in $files) {
            $filePath = $file.FullName
            Write-Host "Lendo arquivo: $($file.Name)"
            
            # Tenta extrair período das datas no nome do arquivo (ex: 2026-06-01 - 2026-06-30)
            $periodName = $null
            if ($file.Name -match "(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})") {
                try {
                    $startDate = [datetime]::ParseExact($Matches[1], "yyyy-MM-dd", $null)
                    $endDate = [datetime]::ParseExact($Matches[2], "yyyy-MM-dd", $null)
                    $startDay = $startDate.ToString("dd")
                    $endDay = $endDate.ToString("dd")
                    $diffDays = ($endDate - $startDate).TotalDays
                    
                    if ($startDay -eq "01" -and $diffDays -ge 27) {
                        $periodName = "acumulado"
                    } else {
                        $periodName = "$startDay a $endDay"
                    }
                    Write-Host "  -> Período identificado pelo nome: $periodName"
                } catch {
                    Write-Warning "Não foi possível analisar as datas no nome: $_"
                }
            }
            
            $wb = $excel.Workbooks.Open($filePath, [Type]::Missing, $true) # Somente leitura

            # Se houver aba de consultores, carrega/atualiza o mapeamento
            $storeSheet = $null
            foreach ($sheet in $wb.Worksheets) {
                if ($sheet.Name -like "*consultor*") {
                    $storeSheet = $sheet
                    break
                }
            }
            if ($storeSheet) {
                Write-Host "  -> Atualizando mapeamento de consultores/lojas..."
                $r = 2
                while ($true) {
                    $id = $storeSheet.Cells.Item($r, 1).Value2
                    if (-not $id) { break }
                    $storeId = [string](Get-SafeInt $id)
                    $storeName = [string]$storeSheet.Cells.Item($r, 2).Value2
                    $status = [string]$storeSheet.Cells.Item($r, 3).Value2
                    $consultant = [string]$storeSheet.Cells.Item($r, 4).Value2
                    $franchisee = [string]$storeSheet.Cells.Item($r, 5).Value2
                    
                    $stores[$storeId] = @{
                        "id" = $storeId
                        "name" = $storeName
                        "status" = $status
                        "consultant" = $consultant
                        "franchisee" = $franchisee
                    }
                    $r++
                }
                
                # Salva mapeamento atualizado no disco
                $storesJsonStr = ConvertTo-Json -InputObject $stores -Depth 5
                [System.IO.File]::WriteAllText($STORES_JSON, $storesJsonStr, [System.Text.Encoding]::UTF8)
            }

            # Identifica as abas que serão lidas no arquivo
            # Se o período foi identificado no nome do arquivo, lemos apenas a primeira aba do arquivo!
            # Caso contrário, lemos as abas internas "acumulado", "01 a 07" etc. (legado/suporte a arquivos consolidados)
            $sheetsToRead = @()
            if ($periodName) {
                $sheetsToRead += @{ "sheet" = $wb.Worksheets.Item(1); "period" = $periodName }
            } else {
                foreach ($sheet in $wb.Worksheets) {
                    if ($sheet.Name -eq "acumulado") {
                        $sheetsToRead += @{ "sheet" = $sheet; "period" = "acumulado" }
                    } elseif ($sheet.Name -match "^\d+ a \d+$") {
                        $sheetsToRead += @{ "sheet" = $sheet; "period" = $sheet.Name }
                    }
                }
            }

            foreach ($item in $sheetsToRead) {
                $ws = $item.sheet
                $pName = $item.period
                
                if ($pName -ne "acumulado") {
                    $weekStartDates[$pName] = $startDate
                }
                
                Write-Host "  -> Lendo aba: $($ws.Name) como período: $pName"

                # Mapeia cabeçalhos
                $wsHeaders = @{}
                for ($c = 1; $c -le 60; $c++) {
                    $val = $ws.Cells.Item(1, $c).Value2
                    if ($val) { $wsHeaders[[string]$val] = $c }
                }

                $isADT = $wsHeaders.ContainsKey("eADT")
                $isExceptions = $wsHeaders.ContainsKey("Service Exceptions")
                $storeCol = if ($wsHeaders.ContainsKey("Store")) { $wsHeaders["Store"] } else { 1 }
                
                $rows = @()
                $r = 2
                while ($true) {
                    $id = $ws.Cells.Item($r, $storeCol).Value2
                    if (-not $id) { break }
                    $storeId = [string](Get-SafeInt $id)

                    if ($isADT) {
                        $adtCol = $wsHeaders["eADT"]
                        $extCol = $wsHeaders["% of Est Extreme Deliveries"]
                        $cntCol = $wsHeaders["Order Count"]

                        $adtVal = $ws.Cells.Item($r, $adtCol).Value2
                        $extVal = $ws.Cells.Item($r, $extCol).Value2
                        $cntVal = $ws.Cells.Item($r, $cntCol).Value2

                        $rows += @{
                            "storeId" = $storeId
                            "adt" = Get-SafeDouble $adtVal
                            "extreme" = Get-SafeDouble $extVal
                            "orders" = Get-SafeInt $cntVal
                        }
                    }
                    elseif ($isExceptions) {
                        $excCol = $wsHeaders["Service Exceptions"]
                        $totCol = $wsHeaders["Total Order Count"]
                        $delCol = $wsHeaders["Delv Order Count"]
                        $excCntCol = $wsHeaders["Service Exceptions Count"]

                        $excVal = $ws.Cells.Item($r, $excCol).Value2
                        $totVal = $ws.Cells.Item($r, $totCol).Value2
                        $delVal = $ws.Cells.Item($r, $delCol).Value2
                        $excCntVal = $ws.Cells.Item($r, $excCntCol).Value2

                        $rows += @{
                            "storeId" = $storeId
                            "exceptions" = Get-SafeDouble $excVal
                            "totalOrders" = Get-SafeInt $totVal
                            "delvOrders" = Get-SafeInt $delVal
                            "exceptionsCount" = Get-SafeInt $excCntVal
                        }
                    }
                    $r++
                }

                # Guarda dados no container
                if ($isADT) {
                    if ($pName -eq "acumulado") {
                        # Mescla ou define
                        $adtData["acumulado"] += $rows
                    } else {
                        if (-not $adtData["weeks"].ContainsKey($pName)) { $adtData["weeks"][$pName] = @() }
                        $adtData["weeks"][$pName] += $rows
                    }
                } elseif ($isExceptions) {
                    if ($pName -eq "acumulado") {
                        $exceptionData["acumulado"] += $rows
                    } else {
                        if (-not $exceptionData["weeks"].ContainsKey($pName)) { $exceptionData["weeks"][$pName] = @() }
                        $exceptionData["weeks"][$pName] += $rows
                    }
                }
            }

            $wb.Close($false)
        }

        # Cria JSON estruturado
        $payload = @{
            "stores" = $stores
            "weeks" = $weekStartDates.Keys | Sort-Object { $weekStartDates[$_] }
            "adt" = $adtData
            "exceptions" = $exceptionData
            "updatedAt" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        }

        $jsonString = ConvertTo-Json -InputObject $payload -Depth 5
        [System.IO.File]::WriteAllText($DATA_JSON, $jsonString, [System.Text.Encoding]::UTF8)
        Write-Host "data.json gerado com sucesso!" -ForegroundColor Green

    } catch {
        Write-Error "Erro ao processar as planilhas: $_"
    } finally {
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}

# Processa inicialmente
Process-ExcelFiles

# Configura o FileSystemWatcher para atualizar quando houver alterações em pwr_reports
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $REPORTS_DIR
$watcher.Filter = "*.xlsx"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$onChanged = Register-ObjectEvent $watcher "Changed" -Action {
    Write-Host "Alteração detectada em: $($Event.SourceEventArgs.FullPath). Atualizando dados..." -ForegroundColor Yellow
    Process-ExcelFiles
}
$onCreated = Register-ObjectEvent $watcher "Created" -Action {
    Write-Host "Novo arquivo detectado: $($Event.SourceEventArgs.FullPath). Processando..." -ForegroundColor Yellow
    Process-ExcelFiles
}

# Inicia o Servidor HTTP local simples usando HttpListener
$port = 8080
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")

try {
    $listener.Start()
    Write-Host "Servidor Web local rodando em http://localhost:$port" -ForegroundColor Green
    Write-Host "Pressione CTRL+C nesta janela ou encerre a task para fechar o servidor."
    
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $urlPath = $request.Url.LocalPath
        if ($urlPath -eq "/") { $urlPath = "/index.html" }
        
        $localFile = Join-Path $APP_DIR $urlPath.Replace("/", "\").TrimStart("\")
        
        if (Test-Path $localFile -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($localFile)
            $ext = [System.IO.Path]::GetExtension($localFile).ToLower()
            
            $contentType = switch ($ext) {
                ".html" { "text/html; charset=utf-8" }
                ".css"  { "text/css" }
                ".js"   { "application/javascript" }
                ".json" { "application/json" }
                ".svg"  { "image/svg+xml" }
                ".png"  { "image/png" }
                ".jpg"  { "image/jpeg" }
                default { "application/octet-stream" }
            }
            
            $response.ContentType = $contentType
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
            $response.ContentType = "text/plain"
            $response.ContentLength64 = $errBytes.Length
            $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
        }
        $response.Close()
    }
} catch {
    Write-Error "Erro no servidor HTTP: $_"
} finally {
    $listener.Stop()
    $watcher.Dispose()
    Unregister-Event -SourceIdentifier $onChanged.Name -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier $onCreated.Name -ErrorAction SilentlyContinue
}
