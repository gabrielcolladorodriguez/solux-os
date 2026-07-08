#!/usr/bin/env bash
# Solux OS — Constructor de la ISO con live-build
# © 2026 Pollocrudo Company. Licencia GPLv3.
#
# Uso:  sudo ./build.sh
# Requiere: Debian/Ubuntu con live-build, ejecutado como root.
set -euo pipefail

# --- Rutas ---
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$BUILD_DIR/.." && pwd)"
WORK_DIR="$BUILD_DIR/work"
DIST="solux-os-1.0-phoenix-amd64.iso"

log() { printf '\033[1;33m[Solux]\033[0m %s\n' "$*"; }

# --- Comprobaciones ---
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script debe ejecutarse como root (usa: sudo ./build.sh)" >&2
    exit 1
fi
if ! command -v lb >/dev/null 2>&1; then
    log "Instalando live-build y dependencias..."
    apt-get update
    apt-get install -y live-build git ca-certificates rsync librsvg2-bin
fi

# --- Preparar árbol de trabajo ---
log "Preparando árbol de trabajo en $WORK_DIR"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# --- Configuración de live-build ---
log "Configurando live-build (Debian Bookworm, XFCE, amd64)..."
lb config \
    --mode debian \
    --distribution bookworm \
    --architectures amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --apt-secure true \
    --mirror-bootstrap "http://deb.debian.org/debian/" \
    --mirror-chroot "http://deb.debian.org/debian/" \
    --mirror-chroot-security "http://security.debian.org/debian-security/" \
    --mirror-binary "http://deb.debian.org/debian/" \
    --mirror-binary-security "http://security.debian.org/debian-security/" \
    --parent-mirror-bootstrap "http://deb.debian.org/debian/" \
    --parent-mirror-chroot "http://deb.debian.org/debian/" \
    --parent-mirror-chroot-security "http://security.debian.org/debian-security/" \
    --parent-mirror-binary "http://deb.debian.org/debian/" \
    --parent-mirror-binary-security "http://security.debian.org/debian-security/" \
    --binary-images iso-hybrid \
    --bootloaders "syslinux,grub-efi" \
    --debian-installer none \
    --bootappend-live "boot=live components username=solux hostname=solux locales=es_ES.UTF-8 keyboard-layouts=es" \
    --iso-application "Solux OS" \
    --iso-publisher "Pollocrudo Company" \
    --iso-volume "Solux OS 1.0 Phoenix" \
    --memtest none

# --- Rebranding del menú de arranque (BIOS/UEFI dice "Solux OS", no Debian) ---
log "Rebrandeando el menú de arranque a Solux OS..."
if [ -d /usr/share/live/build/bootloaders ]; then
    rm -rf config/bootloaders
    cp -r /usr/share/live/build/bootloaders config/bootloaders
    # Reemplazar todas las menciones de Debian por Solux OS en los textos del menú
    grep -rIl "Debian" config/bootloaders 2>/dev/null | while read -r f; do
        sed -i 's|Debian GNU/Linux|Solux OS|g; s|Debian Live|Solux OS|g; s|Debian|Solux OS|g' "$f"
    done
fi

# --- Copiar listas de paquetes ---
log "Copiando listas de paquetes..."
mkdir -p config/package-lists
cp "$BUILD_DIR"/config/package-lists/*.list.chroot config/package-lists/

# --- Copiar hooks ---
log "Copiando hooks de personalización y hardening..."
mkdir -p config/hooks/normal
cp "$BUILD_DIR"/hooks/normal/*.hook.chroot config/hooks/normal/
chmod +x config/hooks/normal/*.hook.chroot

# --- Incluir archivos en el sistema (includes.chroot) ---
log "Incluyendo temas, iconos, wallpapers, apps y configuración..."
INC="config/includes.chroot"

# Temas e iconos
mkdir -p "$INC/usr/share/themes" "$INC/usr/share/icons"
cp -r "$PROJECT_DIR/themes/SoluxOS-Dark" "$INC/usr/share/themes/"
cp -r "$PROJECT_DIR/icons/Solux-Icons"   "$INC/usr/share/icons/"

# Fuentes de branding para que el hook rasterice (SVG) y assets reales (PNG/JPG)
mkdir -p "$INC/usr/share/solux/_src"
cp -r "$PROJECT_DIR/assets/wallpapers" "$INC/usr/share/solux/_src/"
cp -r "$PROJECT_DIR/assets/logos"      "$INC/usr/share/solux/_src/"

# Wallpapers fotográficos reales (JPG) -> se copian directamente a backgrounds
mkdir -p "$INC/usr/share/backgrounds/solux"
if ls "$PROJECT_DIR/assets/wallpapers/photo/"*.jpg >/dev/null 2>&1; then
    cp "$PROJECT_DIR/assets/wallpapers/photo/"*.jpg "$INC/usr/share/backgrounds/solux/"
fi
# Logo real en PNG -> pixmap del sistema
mkdir -p "$INC/usr/share/pixmaps/solux"
if [ -f "$PROJECT_DIR/assets/logos/solux-logo.png" ]; then
    cp "$PROJECT_DIR/assets/logos/solux-logo.png" "$INC/usr/share/pixmaps/solux/solux-logo-full.png"
fi

# Apps Solux
mkdir -p "$INC/usr/share/solux/store" "$INC/usr/share/solux/security-center" \
         "$INC/usr/share/solux/welcome" "$INC/usr/share/solux/tweaks" \
         "$INC/usr/share/solux/browser" "$INC/usr/share/solux/notes"
cp "$PROJECT_DIR/apps/solux-store/solux_store.py"                    "$INC/usr/share/solux/store/"
cp "$PROJECT_DIR/apps/solux-store/catalog.json"                     "$INC/usr/share/solux/store/"
cp "$PROJECT_DIR/apps/solux-security-center/solux_security_center.py" "$INC/usr/share/solux/security-center/"
cp "$PROJECT_DIR/apps/solux-welcome/solux_welcome.py"               "$INC/usr/share/solux/welcome/"
cp "$PROJECT_DIR/apps/solux-tweaks/solux_tweaks.py"                 "$INC/usr/share/solux/tweaks/"
cp "$PROJECT_DIR/apps/solux-browser/solux_browser.py"              "$INC/usr/share/solux/browser/"
cp "$PROJECT_DIR/apps/solux-notes/solux_notes.py"                  "$INC/usr/share/solux/notes/"

# Lanzadores .desktop
mkdir -p "$INC/usr/share/applications"
cp "$PROJECT_DIR/apps/solux-store/solux-store.desktop"                       "$INC/usr/share/applications/"
cp "$PROJECT_DIR/apps/solux-security-center/solux-security-center.desktop"   "$INC/usr/share/applications/"
cp "$PROJECT_DIR/apps/solux-welcome/solux-welcome.desktop"                   "$INC/usr/share/applications/"
cp "$PROJECT_DIR/apps/solux-tweaks/solux-tweaks.desktop"                     "$INC/usr/share/applications/"
cp "$PROJECT_DIR/apps/solux-browser/solux-browser.desktop"                   "$INC/usr/share/applications/"
cp "$PROJECT_DIR/apps/solux-notes/solux-notes.desktop"                       "$INC/usr/share/applications/"

# Marca en terminal: neofetch propio + ASCII, y colores de terminal
mkdir -p "$INC/etc/solux" "$INC/etc/skel/.config/xfce4/terminal"
cp "$PROJECT_DIR/config/branding/solux.neofetch"   "$INC/etc/solux/neofetch.conf"
cp "$PROJECT_DIR/config/branding/solux-ascii.txt"  "$INC/etc/solux/solux-ascii.txt"
cp "$PROJECT_DIR/config/xfce4/terminalrc"          "$INC/etc/skel/.config/xfce4/terminal/terminalrc"

# Firefox endurecido (políticas + autoconfig)
mkdir -p "$INC/usr/lib/firefox-esr/distribution" "$INC/usr/lib/firefox-esr/defaults/pref"
cp "$PROJECT_DIR/config/firefox/policies.json" "$INC/usr/lib/firefox-esr/distribution/policies.json"
cp "$PROJECT_DIR/config/firefox/user.js"       "$INC/usr/lib/firefox-esr/solux-user.js"
# autoconfig: carga solux.cfg (que a su vez lee las prefs de user.js)
cat > "$INC/usr/lib/firefox-esr/defaults/pref/autoconfig.js" <<'FFEOF'
pref("general.config.filename", "solux.cfg");
pref("general.config.obscure_value", 0);
pref("general.config.sandbox_enabled", false);
FFEOF
# solux.cfg debe empezar con un comentario (lo ignora el parser)
{ echo '// Solux OS Firefox config'; sed 's/^user_pref/lockPref/' "$PROJECT_DIR/config/firefox/user.js"; } \
    > "$INC/usr/lib/firefox-esr/solux.cfg"
# También como user.js en el perfil del primer usuario
mkdir -p "$INC/etc/skel/.mozilla/firefox"
cp "$PROJECT_DIR/config/firefox/user.js" "$INC/etc/skel/.mozilla/firefox/solux-user.js"

# Shell Zsh por defecto y mimeapps
mkdir -p "$INC/etc/skel/.config"
cp "$PROJECT_DIR/config/shell/zshrc" "$INC/etc/skel/.zshrc"
cp "$PROJECT_DIR/config/xfce4/mimeapps.list" "$INC/etc/skel/.config/mimeapps.list"

# Autostart de bienvenida (para todos los usuarios nuevos)
mkdir -p "$INC/etc/skel/.config/autostart"
cp "$PROJECT_DIR/apps/solux-welcome/solux-welcome-autostart.desktop" "$INC/etc/skel/.config/autostart/"

# Config XFCE por defecto (en /etc/skel)
mkdir -p "$INC/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml"
cp "$PROJECT_DIR/config/xfce4/"*.xml "$INC/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/" 2>/dev/null || true

# Menú Whisker (estilo Solux)
mkdir -p "$INC/etc/skel/.config/xfce4/panel"
cp "$PROJECT_DIR/config/xfce4/whiskermenu-1.rc" "$INC/etc/skel/.config/xfce4/panel/whiskermenu-1.rc"

# Dock Plank (tema + dock1 + autostart)
mkdir -p "$INC/etc/skel/.local/share/plank/themes" "$INC/etc/skel/.config/plank/dock1/launchers"
cp -r "$PROJECT_DIR/config/plank/themes/Solux" "$INC/etc/skel/.local/share/plank/themes/"
cp "$PROJECT_DIR/config/plank/dock1/settings" "$INC/etc/skel/.config/plank/dock1/settings"
cp "$PROJECT_DIR/config/plank/dock1/launchers/"*.dockitem "$INC/etc/skel/.config/plank/dock1/launchers/"
cp "$PROJECT_DIR/config/plank/plank-autostart.desktop" "$INC/etc/skel/.config/autostart/plank.desktop"

# Pantalla de login (LightDM greeter Solux)
mkdir -p "$INC/etc/lightdm"
cp "$PROJECT_DIR/config/lightdm/lightdm-gtk-greeter.conf" "$INC/etc/lightdm/lightdm-gtk-greeter.conf"

# Conky
mkdir -p "$INC/etc/skel/.config/conky"
cp "$PROJECT_DIR/config/conky/conky.conf" "$INC/etc/skel/.config/conky/"

# GRUB y Plymouth
mkdir -p "$INC/boot/grub/themes/solux" "$INC/usr/share/plymouth/themes/solux" "$INC/etc/default"
cp "$PROJECT_DIR/config/grub/theme.txt" "$INC/boot/grub/themes/solux/"
cp "$PROJECT_DIR/config/grub/grub-default" "$INC/etc/default/grub"
cp "$PROJECT_DIR/config/plymouth/"* "$INC/usr/share/plymouth/themes/solux/"

# Instalador Calamares — SOLO branding Solux.
# No sobrescribimos settings.conf ni modules: dejamos la config de
# calamares-settings-debian (que SÍ funciona) y solo la rebrandeamos a Solux
# en el hook 02-branding. Enviar nuestra settings.conf incompleta rompía el instalador.
mkdir -p "$INC/etc/calamares/branding/solux"
cp -r "$PROJECT_DIR/installer/calamares/branding/solux/"* "$INC/etc/calamares/branding/solux/"

# --- Construir la ISO ---
log "Construyendo la ISO (esto tarda; descarga cientos de paquetes)..."
lb build

# --- Renombrar el resultado ---
if ls live-image-amd64.hybrid.iso >/dev/null 2>&1; then
    mv live-image-amd64.hybrid.iso "$BUILD_DIR/$DIST"
    log "ISO generada: $BUILD_DIR/$DIST"
else
    log "ADVERTENCIA: no se encontró la ISO de salida. Revisa los logs de lb build."
    exit 1
fi

log "¡Listo! Solux OS 1.0 Phoenix compilado."
