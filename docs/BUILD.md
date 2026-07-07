# Guía de compilación de la ISO — Solux OS

Solux OS se construye con **live-build**, la herramienta oficial de Debian para crear
imágenes en vivo. La compilación **debe hacerse en un entorno Linux** (nativo, WSL2 o
Docker). Este documento cubre las tres rutas.

## Requisitos

- **Espacio en disco:** ~25 GB libres para el árbol de compilación.
- **RAM:** 4 GB mínimo (8 GB recomendado).
- **Conexión a internet:** se descargan los paquetes de los repos de Debian y Kali.
- **Privilegios:** la compilación necesita `sudo`/root (chroot, montajes de loopback).

## Opción A — WSL2 (recomendada en Windows)

1. Abre PowerShell **como administrador** e instala Debian en WSL2 (una sola vez):

   ```powershell
   wsl --install Debian
   ```

   Reinicia si te lo pide y crea el usuario de WSL cuando arranque Debian.

2. Desde la carpeta del proyecto, ejecuta el script de compilación:

   ```powershell
   .\build\wsl-build.ps1
   ```

   El script instala las dependencias dentro de WSL, copia el proyecto y lanza
   `build.sh`. Al terminar, la ISO aparece en `build/` y se copia a la carpeta del
   proyecto en Windows.

## Opción B — Docker

Requiere **Docker Desktop** instalado y en ejecución.

```powershell
.\build\docker-build.ps1
```

Esto construye una imagen Debian con live-build (`build/Dockerfile`), monta el proyecto y
genera la ISO dentro del contenedor, copiándola al host al finalizar.

## Opción C — Linux nativo

En Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y live-build git ca-certificates
cd build
sudo ./build.sh
```

## Qué hace `build.sh`

1. Configura live-build (`lb config`) con Debian Bookworm, arquitectura amd64, XFCE.
2. Añade los repositorios de Kali Linux y sus claves para incluir el arsenal.
3. Copia las listas de paquetes de `build/config/package-lists/`.
4. Copia los archivos de personalización (`includes.chroot`): temas, iconos, wallpapers,
   apps Solux, configuración de XFCE.
5. Ejecuta los *hooks* de `build/hooks/` (personalización + hardening).
6. Construye la ISO (`lb build`) y la renombra a `solux-os-1.0-phoenix-amd64.iso`.

## Probar la ISO

Sin grabarla, en QEMU:

```bash
qemu-system-x86_64 -enable-kvm -m 4096 -cdrom solux-os-1.0-phoenix-amd64.iso
```

O grábala a un USB con `dd` (Linux) o Rufus/Balena Etcher (Windows) y arranca desde él.

## Solución de problemas

- **`lb: command not found`** → instala `live-build`.
- **Fallo de montaje/loopback en WSL** → asegúrate de usar WSL2 (no WSL1) y kernel actual.
- **Descarga de Kali falla** → revisa la clave del repo en `hooks/01-repos.sh`.
- **ISO no arranca en UEFI** → verifica que `grub-efi-amd64` esté en las listas de paquetes.
