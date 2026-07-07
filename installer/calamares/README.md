# Instalador de Solux OS (Calamares)

Configuración del instalador gráfico basado en **Calamares**, con branding propio y
seguridad reforzada desde la primera instalación.

## Puntos clave

- **Cifrado LUKS2 activado por defecto** (`modules/partition.conf`): el disco se cifra
  salvo que el usuario lo desactive explícitamente.
- **Política de contraseñas estricta** (`modules/users.conf`): mínimo 12 caracteres, 3
  clases, sin contraseñas débiles; `root` queda bloqueado (se usa `sudo`).
- **Post-instalación de seguridad** (`modules/shellprocess-security.conf`): reactiva y
  habilita los servicios de hardening (UFW, nftables, Fail2ban, AppArmor, ClamAV,
  unattended-upgrades), inicializa AIDE y regenera GRUB dentro del sistema instalado.
- **Branding Solux** (`branding/solux/`): logo, colores de marca y presentación durante
  la copia de archivos.

## Instalación en el sistema en vivo

El hook de build copia:

- `settings.conf` → `/etc/calamares/settings.conf`
- `modules/*.conf` → `/etc/calamares/modules/`
- `branding/solux/` → `/etc/calamares/branding/solux/`

Y crea un lanzador "Instalar Solux OS" en el escritorio y el menú del sistema en vivo.
Las imágenes `logo.png` y `welcome.png` se generan del logo SVG en tiempo de build.
