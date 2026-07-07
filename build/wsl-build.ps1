# Solux OS - Compilacion de la ISO via WSL2 Debian (Windows PowerShell)
# (c) 2026 Pollocrudo Company
#
# Requiere WSL2 con una distribucion Debian instalada:
#     wsl --install Debian        (como administrador, una sola vez)
#
# Uso:  .\build\wsl-build.ps1

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Write-Host "[Solux] Proyecto: $ProjectDir" -ForegroundColor Yellow

# Comprobar WSL
$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wsl) {
    Write-Host "WSL no esta disponible. Instala WSL2 con:  wsl --install" -ForegroundColor Red
    exit 1
}

# Comprobar que hay una distro instalada
$distros = (wsl -l -q) 2>$null | Where-Object { $_ -and $_.Trim() -ne "" }
if (-not $distros) {
    Write-Host "No hay distribuciones WSL instaladas." -ForegroundColor Red
    Write-Host "Ejecuta como administrador:  wsl --install Debian" -ForegroundColor Yellow
    exit 1
}
Write-Host "[Solux] Distros WSL detectadas: $($distros -join ', ')" -ForegroundColor Green

# Convertir la ruta de Windows a ruta WSL (/mnt/c/...)
$wslPath = "/mnt/" + $ProjectDir.Substring(0,1).ToLower() + ($ProjectDir.Substring(2) -replace '\\','/')
Write-Host "[Solux] Ruta WSL del proyecto: $wslPath" -ForegroundColor Yellow

# Script bash que se ejecuta dentro de WSL
$bash = @"
set -e
echo '[Solux] Instalando dependencias de compilacion...'
sudo apt-get update
sudo apt-get install -y live-build git ca-certificates rsync librsvg2-bin xorriso
cd '$wslPath/build'
echo '[Solux] Lanzando build.sh...'
sudo bash ./build.sh
"@

# Guardar el script en un temporal accesible desde WSL y ejecutarlo
$tmp = Join-Path $ProjectDir "build\.wsl-run.sh"
# Escribir en formato Unix (LF)
[IO.File]::WriteAllText($tmp, ($bash -replace "`r`n","`n"))

Write-Host "[Solux] Compilando dentro de WSL2 (esto tarda bastante)..." -ForegroundColor Yellow
wsl bash "$wslPath/build/.wsl-run.sh"

Remove-Item $tmp -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "[Solux] ISO generada en: $ProjectDir\build\solux-os-1.0-phoenix-amd64.iso" -ForegroundColor Green
} else {
    Write-Host "[Solux] La compilacion fallo. Revisa los mensajes anteriores." -ForegroundColor Red
    exit 1
}
