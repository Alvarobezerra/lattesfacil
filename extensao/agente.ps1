param(
  [string]$AppUrl = "https://lattesfacil.onrender.com",
  [string]$ProtocolUri = "",
  [switch]$Daemon
)
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ldDir = Join-Path $env:LOCALAPPDATA "LattesData"
$profileDir = Join-Path $ldDir "perfil-navegador"
$corePath = Join-Path $ldDir "autofill_core.js"
$ps1Path = Join-Path $ldDir "agente.ps1"
$coreJs = [System.IO.File]::ReadAllText($corePath, [System.Text.Encoding]::UTF8)
$cdpPort = 19229

# 1. Registra o protocolo lattesdata:// no Windows (por usuario, sem precisar de Admin)
try {
  $regBase = "HKCU:\Software\Classes\lattesdata"
  New-Item -Path $regBase -Force | Out-Null
  Set-ItemProperty -Path $regBase -Name "(Default)" -Value "URL:LattesData Automation Protocol" -Force
  Set-ItemProperty -Path $regBase -Name "URL Protocol" -Value "" -Force
  $cmdKey = Join-Path $regBase "shell\open\command"
  New-Item -Path $cmdKey -Force | Out-Null
  $cmdVal = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ps1Path`" -ProtocolUri `"%1`""
  Set-ItemProperty -Path $cmdKey -Name "(Default)" -Value $cmdVal -Force
} catch {}

# 2. Cria atalho na Area de Trabalho
try {
  $desktop = [Environment]::GetFolderPath("Desktop")
  $lnkPath = Join-Path $desktop "LattesData Automático.lnk"
  if (-not (Test-Path $lnkPath)) {
    $wsh = New-Object -ComObject WScript.Shell
    $sc = $wsh.CreateShortcut($lnkPath)
    $sc.TargetPath = "powershell.exe"
    $sc.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ps1Path`" -AppUrl `"$AppUrl`""
    $sc.Description = "Abrir LattesData com Automação de Cadastro no Lattes"
    $sc.Save()
  }
} catch {}

# 3. Se foi disparado pelo clique em "Enviar" via lattesdata://fill?job=...&server=...
$pendingPayload = ""
if ($ProtocolUri -match "^lattesdata://") {
  try {
    $u = [Uri]$ProtocolUri
    $qs = [System.Web.HttpUtility]::ParseQueryString($u.Query)
  } catch {}
  $jobMatch = [regex]::Match($ProtocolUri, "[?&]job=([^&]+)")
  $srvMatch = [regex]::Match($ProtocolUri, "[?&]server=([^&]+)")
  if ($srvMatch.Success) {
    $AppUrl = [Uri]::UnescapeDataString($srvMatch.Groups[1].Value)
  }
  if ($jobMatch.Success) {
    $jobId = [Uri]::UnescapeDataString($jobMatch.Groups[1].Value)
    $jobUrl = "$($AppUrl.TrimEnd('/'))/api/lattes/job?id=$jobId"
    try {
      $resp = Invoke-RestMethod -Uri $jobUrl -TimeoutSec 8 -ErrorAction Stop
      if ($resp.ok -and $resp.data) {
        $pendingPayload = ($resp.data | ConvertTo-Json -Compress -Depth 10)
      }
    } catch {}
  }
}

$browsers = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$browserExe = $browsers | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browserExe) {
  Write-Host "Erro: Google Chrome ou Microsoft Edge nao encontrado." -ForegroundColor Red
  Start-Sleep -Seconds 5
  exit 1
}

function Start-LattesBrowser([string]$targetUrl) {
  Start-Process -FilePath $browserExe -ArgumentList @(
    "--user-data-dir=$profileDir",
    "--remote-debugging-port=$cdpPort",
    "--remote-allow-origins=*",
    "--no-first-run",
    "--no-default-browser-check",
    $targetUrl
  ) | Out-Null
  Start-Sleep -Seconds 2
}

$cdpAlive = $false
try {
  $null = Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json/version" -TimeoutSec 1 -ErrorAction Stop
  $cdpAlive = $true
} catch {}

$initialTarget = if ($pendingPayload) { "https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form" } else { $AppUrl }

if (-not $cdpAlive -and -not $Daemon) {
  Write-Host "==========================================================" -ForegroundColor Cyan
  Write-Host "  LattesData — Navegador Automatico de Cadastro no Lattes" -ForegroundColor Cyan
  Write-Host "==========================================================" -ForegroundColor Cyan
  Write-Host "Abrindo navegador dedicado ($initialTarget)..." -ForegroundColor Green
  Write-Host "Protocolo lattesdata:// registrado no Windows com sucesso!" -ForegroundColor Green
  Start-LattesBrowser $initialTarget
} elseif ($cdpAlive -and $pendingPayload) {
  # Se o navegador ja estava aberto e chegou um job via protocolo lattesdata://
  $existingTabs = @(Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json" -TimeoutSec 2)
  $lt = @($existingTabs | Where-Object { $_.type -eq "page" -and $_.url -match "wwws\.cnpq\.br" })
  if ($lt.Count -eq 0) {
    Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$cdpPort/json/new?https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form" -TimeoutSec 2 | Out-Null
  } else {
    Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json/activate/$($lt[0].id)" -TimeoutSec 2 | Out-Null
  }
}

$script:wsPool = @{}
$script:cdpMsgId = 0

function Invoke-CdpEval([string]$wsUrl, [string]$jsExpr) {
  if (-not $wsUrl) { return $null }
  $ct = [System.Threading.CancellationToken]::None
  try {
    $ws = $script:wsPool[$wsUrl]
    if (-not $ws -or $ws.State -ne [System.Net.WebSockets.WebSocketState]::Open) {
      if ($ws) { try { $ws.Dispose() } catch {} }
      $ws = New-Object System.Net.WebSockets.ClientWebSocket
      $ws.ConnectAsync([Uri]$wsUrl, $ct).Wait(2500) | Out-Null
      if ($ws.State -ne [System.Net.WebSockets.WebSocketState]::Open) { return $null }
      $script:wsPool[$wsUrl] = $ws
    }
    $script:cdpMsgId++
    $msg = @{ id = $script:cdpMsgId; method = "Runtime.evaluate"; params = @{ expression = $jsExpr; returnByValue = $true } } | ConvertTo-Json -Compress -Depth 5
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait(2500) | Out-Null
    $buf = New-Object byte[] 262144
    $sb = New-Object System.Text.StringBuilder
    do {
      $seg = [ArraySegment[byte]]::new($buf)
      $task = $ws.ReceiveAsync($seg, $ct)
      if (-not $task.Wait(3000)) { break }
      $res = $task.Result
      $sb.Append([System.Text.Encoding]::UTF8.GetString($buf, 0, $res.Count)) | Out-Null
    } while (-not $res.EndOfMessage)
    $parsed = $sb.ToString() | ConvertFrom-Json
    return $parsed.result.result.value
  } catch {
    if ($script:wsPool.ContainsKey($wsUrl)) {
      try { $script:wsPool[$wsUrl].Dispose() } catch {}
      $script:wsPool.Remove($wsUrl)
    }
    return $null
  }
}

$nextToast = ""
$failCount = 0
$pollServers = @("http://127.0.0.1:8799", $AppUrl.TrimEnd('/')) | Select-Object -Unique

while ($true) {
  Start-Sleep -Milliseconds 1200

  # Verifica se chegou algum job na fila do servidor (funciona de qualquer navegador!)
  if (-not $pendingPayload) {
    foreach ($srv in $pollServers) {
      try {
        $jResp = Invoke-RestMethod -Uri "$srv/api/lattes/job?next=1" -TimeoutSec 2 -ErrorAction Stop
        if ($jResp -and $jResp.ok -and $jResp.data) {
          $pendingPayload = ($jResp.data | ConvertTo-Json -Compress -Depth 10)
          Write-Host ">> Job recebido de $srv!" -ForegroundColor Green
          break
        }
      } catch {}
    }
  }

  $tabs = @()
  $browserRunning = $false
  try {
    $tabs = @(Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json" -TimeoutSec 2 -ErrorAction Stop)
    $browserRunning = $true
    $failCount = 0
  } catch {
    $browserRunning = $false
  }

  if (-not $browserRunning) {
    if ($pendingPayload) {
      Write-Host ">> Abrindo navegador automatico no Lattes para executar o cadastro..." -ForegroundColor Cyan
      Start-LattesBrowser "https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form"
      continue
    }
    if (-not $Daemon) {
      $failCount++
      if ($failCount -gt 6) { break }
    }
    continue
  }

  # Se chegou um job via fila e o navegador ja estava aberto mas sem aba do Lattes, abre/ativa a aba do Lattes
  $lattesTabsCheck = @($tabs | Where-Object { $_.type -eq "page" -and $_.url -match "wwws\.cnpq\.br" })
  if ($pendingPayload -and $lattesTabsCheck.Count -eq 0) {
    try {
      Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$cdpPort/json/new?https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form" -TimeoutSec 2 | Out-Null
      Start-Sleep -Milliseconds 800
      $tabs = @(Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json" -TimeoutSec 2 -ErrorAction Stop)
    } catch {}
  } elseif ($pendingPayload -and $lattesTabsCheck.Count -gt 0) {
    try {
      Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json/activate/$($lattesTabsCheck[0].id)" -TimeoutSec 2 | Out-Null
    } catch {}
  }

  $lattesTabs = @($tabs | Where-Object { $_.type -eq "page" -and $_.url -match "wwws\.cnpq\.br" })
  $appTabs = @($tabs | Where-Object { $_.type -eq "page" -and ($_.url -match "onrender\.com" -or $_.url -match "127\.0\.0\.1" -or $_.url -match "localhost") })

  $lattesOnline = $false
  $lattesName = ""

  if ($lattesTabs.Count -gt 0) {
    $ltWs = $lattesTabs[0].webSocketDebuggerUrl
    $probeJs = "(function(){try{var d=window.top.document;var e=d.getElementById('nmeLt')||d.querySelector('.dadosPrinc .nome');var n=e?e.textContent.trim():'';var m=!!(window.top.modalCV2&&typeof window.top.modalCV2.setarUrl==='function');var f=!!d.querySelector('[name=`"f_titulo`"]');return JSON.stringify({online:!!(n||m||f),name:n});}catch(err){return JSON.stringify({online:false,name:''});}})()"
    $probeRaw = Invoke-CdpEval $ltWs $probeJs
    if ($probeRaw) {
      try {
        $probeObj = $probeRaw | ConvertFrom-Json
        $lattesOnline = [bool]$probeObj.online
        $lattesName = [string]$probeObj.name
      } catch {}
    }
  }

  foreach ($at in $appTabs) {
    $onlineJson = if ($lattesTabs.Count -gt 0) { if ($lattesOnline) { "true" } else { "false" } } else { "null" }
    $nameEsc = ($lattesName -replace "\\", "\\\\" -replace "'", "\'")
    $toastEsc = ($nextToast -replace "\\", "\\\\" -replace "'", "\'")
    $appJs = @"
(function(online, name, toastMsg){
  if (!window.__lfCdpHooked) {
    window.__lfCdpHooked = true;
    window.addEventListener('message', function(e) {
      if (e.source !== window || !e.data) return;
      if (e.data.type === 'lattesdata-ext-ping') {
        window.postMessage({ type: 'lattesdata-ext-pong', version: 'cdp-1.0' }, location.origin);
      } else if (e.data.type === 'lattesdata-ext-fill') {
        window.__lfCdpQueue = JSON.stringify(e.data.data);
      }
    });
    window.postMessage({ type: 'lattesdata-ext-pong', version: 'cdp-1.0' }, location.origin);
  }
  var b = document.getElementById('extStatusBadge');
  if (b) b.textContent = '✅ Navegador Automático Conectado';
  var box = document.getElementById('extInstallBox');
  if (box) box.style.display = 'none';
  if (online !== null) {
    window.postMessage({ type: 'lattesfacil-status', online: online, name: name || '' }, location.origin);
  }
  if (toastMsg) {
    window.postMessage({ type: 'lattesdata-ext-result', ok: true, message: toastMsg }, location.origin);
  }
  var q = window.__lfCdpQueue || '';
  window.__lfCdpQueue = '';
  return q;
})($onlineJson, '$nameEsc', '$toastEsc')
"@
    $queued = Invoke-CdpEval $at.webSocketDebuggerUrl $appJs
    if ($nextToast) { $nextToast = "" }
    if ($queued) {
      $pendingPayload = $queued
      Write-Host ">> Recebido pedido de cadastro do LattesData!" -ForegroundColor Green
      if ($lattesTabs.Count -eq 0) {
        $loginUrl = "https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form"
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$cdpPort/json/new?$loginUrl" -TimeoutSec 2 | Out-Null
        $nextToast = "🔐 Abri o Lattes! Faça seu login (1ª vez) — assim que entrar, o formulário será aberto e preenchido sozinho!"
      } else {
        Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json/activate/$($lattesTabs[0].id)" -TimeoutSec 2 | Out-Null
        if ($lattesOnline) {
          $nextToast = "🚀 Abrindo formulário no Lattes e efetuando o cadastro automaticamente!"
        } else {
          $nextToast = "🔐 Aguardando seu login na aba do Lattes — o cadastro continuará sozinho assim que o currículo abrir!"
        }
      }
    }
  }

  if ($pendingPayload -and $lattesTabs.Count -gt 0) {
    $ltTab = $lattesTabs[0]
    if (-not $lattesOnline) {
      $bannerJs = "(function(){if(document.getElementById('ld-cdp-ban'))return;var b=document.createElement('div');b.id='ld-cdp-ban';b.style.cssText='position:fixed;top:0;left:0;right:0;z-index:2147483647;background:linear-gradient(90deg,#0b192c,#0369a1);color:#fff;padding:12px 20px;font:600 14px system-ui,sans-serif;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.3);border-bottom:2px solid #38bdf8';b.textContent='🚀 LattesData: Faça seu login no Lattes. Assim que entrar, o formulário será aberto e preenchido automaticamente!';if(document.body)document.body.appendChild(b);})()"
      Invoke-CdpEval $ltTab.webSocketDebuggerUrl $bannerJs | Out-Null
    } else {
      $payloadToRun = $pendingPayload
      $pendingPayload = ""
      Write-Host ">> Lattes logado! Abrindo formulario e preenchendo automaticamente..." -ForegroundColor Cyan
      Invoke-RestMethod -Uri "http://127.0.0.1:$cdpPort/json/activate/$($ltTab.id)" -TimeoutSec 2 | Out-Null
      $fullRunJs = $coreJs + "`nwindow.__lfAutofill(" + $payloadToRun + ");"
      Invoke-CdpEval $ltTab.webSocketDebuggerUrl $fullRunJs | Out-Null
    }
  }
}
