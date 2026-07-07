# Sistema de compilación de Solux OS

Genera la ISO arrancable de Solux OS con **live-build** de Debian.

## Archivos

| Archivo | Propósito |
|---------|-----------|
| `build.sh` | Orquestador: configura live-build, copia listas/hooks/includes y construye la ISO. |
| `Dockerfile` | Imagen Debian con live-build para compilar en contenedor. |
| `docker-build.ps1` | Lanza la compilación vía Docker desde Windows. |
| `wsl-build.ps1` | Lanza la compilación vía WSL2 Debian desde Windows. |
| `config/package-lists/` | Qué paquetes entran en la ISO (base, seguridad, arsenal Kali). |
| `hooks/normal/` | Scripts que personalizan y endurecen el sistema durante la build. |

## Hooks (orden de ejecución)

1. `01-repos.hook.chroot` — añade el repositorio de Kali con pinning.
2. `02-branding.hook.chroot` — aplica identidad, rasteriza logos/wallpapers, crea lanzadores.
3. `03-security.hook.chroot` — **hardening en 20 fases** (ver `docs/SECURITY.md`).
4. `04-liveuser.hook.chroot` — usuario en vivo `solux`, root bloqueado, lanzador del instalador.

## Cómo compilar

Ver `../docs/BUILD.md`. Resumen:

```bash
# Linux nativo
sudo ./build.sh
```
```powershell
# Windows con WSL2
.\wsl-build.ps1
# Windows con Docker
.\docker-build.ps1
```

Resultado: `build/solux-os-1.0-phoenix-amd64.iso`.

## Notas

- El arsenal completo de Kali es enorme. Por defecto se incluye `kali-linux-headless`
  más metapaquetes por categoría; puedes recortar la lista en
  `config/package-lists/solux-kali-arsenal.list.chroot` para una ISO más ligera.
- La contraseña de GRUB usa un hash de marcador (`SOLUXPLACEHOLDERHASH`). Genera el tuyo
  con `grub-mkpasswd-pbkdf2` y sustitúyelo en `hooks/normal/03-security.hook.chroot`
  antes de compilar para producción.
