<#
  Remove o "Ativador/Agente" antigo do LattesData deste Windows (substituído pela extensão do navegador).

  Uso (PowerShell):
    .\remover-agente-antigo.ps1 -Simular        # só mostra o que seria removido, sem alterar nada
    .\remover-agente-antigo.ps1                 # remove (mantém o perfil do navegador dedicado)
    .\remover-agente-antigo.ps1 -ApagarPerfil   # remove também o perfil do Chrome dedicado (apaga o login salvo do Lattes nele)

  O que remove (somente do usuário atual, sem precisar de administrador):
    - processos powershell que executam agente.ps1
    - chave de inicialização HKCU\...\Run\LattesDataAgent
    - protocolo lattesdata:// (HKCU\Software\Classes\lattesdata)
    - atalho "LattesData Automático.lnk" da Área de Trabalho
    - pasta %LOCALAPPDATA%\LattesData (agente, config com token, log, atalhos e autofill_core.js)
#>
param(
  [switch]$Simular,
  [switch]$ApagarPerfil
)
$ErrorActionPreference = "Continue"
$ldDir = Join-Path $env:LOCALAPPDATA "LattesData"
$perfil = Join-Path $ldDir "perfil-navegador"

function Acao([string]$descricao, [scriptblock]$bloco) {
  if ($Simular) { Write-Host "[simulação] $descricao" -ForegroundColor Yellow; return }
  try { & $bloco; Write-Host "[ok] $descricao" -ForegroundColor Green }
  catch { Write-Host "[falhou] $descricao -> $($_.Exception.Message)" -ForegroundColor Red }
}

# 1. Processos do agente (nunca o próprio script)
$procs = @(Get-CimInstance Win32_Process | Where-Object {
  $_.Name -match 'powershell' -and $_.CommandLine -match 'LattesData.*agente\.ps1' -and $_.ProcessId -ne $PID
})
if ($procs.Count -eq 0) { Write-Host "[--] nenhum processo do agente em execução" }
foreach ($p in $procs) { Acao "encerrar processo do agente (PID $($p.ProcessId))" { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop } }

# 2. Inicialização do Windows
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
if (Get-ItemProperty $runKey -Name LattesDataAgent -ErrorAction SilentlyContinue) {
  Acao "remover inicialização automática (Run\LattesDataAgent)" { Remove-ItemProperty -Path $runKey -Name LattesDataAgent -ErrorAction Stop }
} else { Write-Host "[--] inicialização automática já ausente" }

# 3. Protocolo lattesdata://
$proto = "HKCU:\Software\Classes\lattesdata"
if (Test-Path $proto) {
  Acao "remover protocolo lattesdata://" { Remove-Item -Path $proto -Recurse -Force -ErrorAction Stop }
} else { Write-Host "[--] protocolo lattesdata:// já ausente" }

# 4. Atalho da Área de Trabalho
$lnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "LattesData Automático.lnk"
if (Test-Path $lnk) {
  Acao "remover atalho da Área de Trabalho" { Remove-Item -Path $lnk -Force -ErrorAction Stop }
} else { Write-Host "[--] atalho da Área de Trabalho já ausente" }

# 5. Pasta de dados do agente
if (Test-Path $ldDir) {
  $itens = @(Get-ChildItem $ldDir -Force | Where-Object { $ApagarPerfil -or $_.FullName -ne $perfil })
  foreach ($i in $itens) { Acao "apagar $($i.Name)" { Remove-Item -Path $i.FullName -Recurse -Force -ErrorAction Stop } }
  if (-not $ApagarPerfil -and (Test-Path $perfil)) {
    Write-Host "[--] perfil do navegador dedicado mantido (use -ApagarPerfil para apagá-lo): $perfil"
  }
  if ($ApagarPerfil) { Acao "apagar a pasta $ldDir" { Remove-Item -Path $ldDir -Recurse -Force -ErrorAction Stop } }
} else { Write-Host "[--] pasta $ldDir já ausente" }

if ($Simular) { Write-Host "`nSimulação concluída: nada foi alterado." -ForegroundColor Yellow }
else { Write-Host "`nConcluído. Use a extensão do navegador para enviar ao Lattes." -ForegroundColor Cyan }
