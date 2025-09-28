# Run E2E tests and Sonar scan helper for Windows PowerShell
# Usage:
# 1) Ative seu venv ou deixe o script ativar: .\.venv\Scripts\Activate.ps1
# 2) (Opcional) Defina $env:SONAR_TOKEN na sessão atual para executar Sonar localmente
#    $env:SONAR_TOKEN = 'seu_token_aqui'
# 3) .\scripts\run-e2e.ps1

param(
    [int]$Port = 5001,
    [int]$WaitSeconds = 120
)

$ErrorActionPreference = 'Stop'

Write-Host "Iniciando run-e2e.ps1 (porta $Port)" -ForegroundColor Cyan

# Ativar venv se existir
$venvActivate = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Ativando virtualenv: $venvActivate"
    try {
        . $venvActivate
    } catch {
        Write-Host "Falha ao ativar virtualenv: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "Virtualenv não encontrado em .venv - supondo que Python e deps estejam no PATH" -ForegroundColor Yellow
}

# Start the Flask app in background
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) { throw "Python não encontrado no PATH. Ative o venv ou instale Python." }

$runScript = Join-Path -Path $PSScriptRoot -ChildPath "..\run_v2.py"
if (-not (Test-Path $runScript)) { throw "run_v2.py não encontrado na raiz do projeto." }

Write-Host "Iniciando aplicação: python $runScript" -ForegroundColor Green
# Use Start-Process to show app logs in this console and avoid redirect buffering issues
$projectRoot = Resolve-Path (Join-Path -Path $PSScriptRoot -ChildPath "..")
$proc = Start-Process -FilePath $pythonPath -ArgumentList "`"$runScript`"" -WorkingDirectory $projectRoot -NoNewWindow -PassThru
Start-Sleep -Seconds 1
if (-not $proc) { throw "Falha ao iniciar o processo Python." }
Write-Host "Aplicação iniciada (PID: $($proc.Id)). Aguardando disponibilidade (até $WaitSeconds segundos)..."

# Wait until the server responds
$healthUrl = "http://localhost:$Port/"
$healthUrlNoSlash = $healthUrl.TrimEnd('/')
$timeout = (Get-Date).AddSeconds($WaitSeconds)
$end = (Get-Date).AddSeconds($WaitSeconds)
$startTime = Get-Date
$alive = $false
while ((Get-Date) -lt $end) {
    try {
        $r = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $alive = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $alive) {
    Write-Host "A aplicação não respondeu em $WaitSeconds segundos. Ver logs." -ForegroundColor Red
    Write-Host "Killing process $($proc.Id)" -ForegroundColor Yellow
    try { $proc.Kill() } catch {}
    exit 1
}

Write-Host "Aplicação disponível em $healthUrl" -ForegroundColor Green

# Run Cypress tests (requires node and cypress installed locally)
Write-Host "Executando Cypress (npx cypress run)" -ForegroundColor Cyan
try {
    Write-Host "Running Cypress with baseUrl=$healthUrlNoSlash"
    & npx cypress run --config "baseUrl=$healthUrlNoSlash"
    $cypressExit = $LASTEXITCODE
} catch {
    Write-Host "Erro ao rodar Cypress: $_" -ForegroundColor Red
    $cypressExit = 2
}

# Run Sonar Scanner if token is present
if ($env:SONAR_TOKEN -and $env:SONAR_TOKEN.Trim().Length -gt 0) {
    Write-Host "SONAR_TOKEN detectado - executando sonar-scanner" -ForegroundColor Cyan
    try {
        $sonarArgs = "-Dsonar.login=$env:SONAR_TOKEN"
        $sonarProc = Start-Process -FilePath "sonar-scanner" -ArgumentList $sonarArgs -WorkingDirectory $projectRoot -NoNewWindow -Wait -PassThru
        $sonarExit = $sonarProc.ExitCode
    } catch {
        Write-Host "Erro ao executar sonar-scanner: $_" -ForegroundColor Red
        $sonarExit = 2
    }
} else {
    Write-Host "SONAR_TOKEN não definido - pulando Sonar Scanner" -ForegroundColor Yellow
    $sonarExit = 0
}

# Stop the Flask process
Write-Host "Finalizando aplicação (PID: $($proc.Id))" -ForegroundColor Cyan
try { $proc.Kill() } catch { }

if ($cypressExit -ne 0) { Write-Host "Cypress retornou código $cypressExit" -ForegroundColor Red }
if ($sonarExit -ne 0) { Write-Host "Sonar retornou código $sonarExit" -ForegroundColor Red }

if ($cypressExit -eq 0 -and $sonarExit -eq 0) { Write-Host "E2E + Sonar concluídos com sucesso." -ForegroundColor Green; exit 0 }
exit 1
