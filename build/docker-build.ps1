# Solux OS - Compilacion de la ISO via Docker (Windows PowerShell)
# (c) 2026 Pollocrudo Company
#
# Requiere Docker Desktop instalado y en ejecucion.
# Uso:  .\build\docker-build.ps1

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Write-Host "[Solux] Proyecto: $ProjectDir" -ForegroundColor Yellow

# Comprobar Docker
$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "Docker no esta instalado o no esta en el PATH." -ForegroundColor Red
    Write-Host "Instala Docker Desktop desde https://www.docker.com/products/docker-desktop/"
    exit 1
}

try { docker info | Out-Null } catch {
    Write-Host "Docker no esta en ejecucion. Abre Docker Desktop y reintenta." -ForegroundColor Red
    exit 1
}

Write-Host "[Solux] Construyendo la imagen de compilacion..." -ForegroundColor Yellow
docker build -t solux-builder (Join-Path $ProjectDir "build")
if ($LASTEXITCODE -ne 0) { Write-Host "Fallo al construir la imagen." -ForegroundColor Red; exit 1 }

Write-Host "[Solux] Compilando la ISO (esto tarda bastante)..." -ForegroundColor Yellow
# --privileged es necesario para los montajes loopback de live-build
docker run --rm --privileged `
    -v "${ProjectDir}:/solux" `
    -w /solux/build `
    solux-builder bash ./build.sh

if ($LASTEXITCODE -eq 0) {
    Write-Host "[Solux] ISO generada en: $ProjectDir\build\solux-os-1.0-phoenix-amd64.iso" -ForegroundColor Green
} else {
    Write-Host "[Solux] La compilacion fallo. Revisa los mensajes anteriores." -ForegroundColor Red
    exit 1
}
