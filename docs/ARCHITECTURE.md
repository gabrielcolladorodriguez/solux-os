# Arquitectura de Solux OS

Este documento describe cómo encajan las piezas de Solux OS, desde la base del sistema
hasta las aplicaciones propias.

## Capas del sistema

```
┌─────────────────────────────────────────────────────────┐
│  Apps propias (Python/GTK3)                              │
│  Solux Store · Security Center · Welcome · Installer     │
├─────────────────────────────────────────────────────────┤
│  Escritorio XFCE 4.18 + Tema Solux Dark + Iconos Solux   │
├─────────────────────────────────────────────────────────┤
│  Capa de seguridad                                       │
│  AppArmor · nftables/UFW · Fail2ban · AIDE · ClamAV      │
├─────────────────────────────────────────────────────────┤
│  Base Debian 12 Bookworm + repos de Kali + kernel HW     │
└─────────────────────────────────────────────────────────┘
```

## Componentes

### Base del sistema
- **Distribución:** Debian 12 Bookworm (rama estable).
- **Repositorios extra:** Kali Linux (para el arsenal de herramientas de seguridad).
- **Init:** systemd.
- **Kernel:** linux-image-amd64 con parámetros de lockdown.

### Escritorio
- **Entorno:** XFCE 4.18.
- **Gestor de ventanas:** xfwm4 con tema Solux.
- **Compositor:** xfwm4 interno (sombras, transparencia moderada).
- **Panel:** un panel superior con menú, ventanas, systray y reloj; un dock inferior
  (plank o panel 2) con las apps principales.
- **Login:** LightDM con greeter GTK y fondo de marca.

### Apps propias (`apps/`)
Todas escritas en **Python 3 + GTK 3** (PyGObject), lo que permite integración nativa con
XFCE, empaquetado sencillo y bajo consumo:

- **solux-store** — Frontend gráfico sobre APT/Flatpak. Cataloga miles de paquetes por
  categoría y ofrece el arsenal de Kali en un clic. Modelo de datos en `catalog.json`.
- **solux-security-center** — Panel con 10 secciones que ejecutan y muestran el estado de
  las herramientas de seguridad del sistema.
- **solux-welcome** — Asistente de primer arranque.

### Instalador
- **Calamares** con módulos configurados en `installer/calamares/`, branding propio y
  cifrado LUKS activado por defecto.

## Flujo de arranque

1. **GRUB** (con contraseña) → menú con tema Solux.
2. **Plymouth** → animación de arranque con el logo.
3. **LightDM** → pantalla de login con fondo de marca.
4. **XFCE** → sesión con panel, dock y Conky.
5. Primer arranque → **Solux Welcome** se abre automáticamente.

## Flujo de compilación

Ver `docs/BUILD.md`. En resumen: `live-build` toma la configuración de
`build/config/`, incorpora los archivos de `includes.chroot` (que reflejan la estructura
de `/` en el sistema final) y ejecuta los hooks de personalización y hardening antes de
empaquetar la ISO.

## Dónde vive cada cosa en el sistema instalado

| Recurso | Ruta en el sistema |
|---------|--------------------|
| Temas GTK | `/usr/share/themes/SoluxOS-Dark/` |
| Iconos | `/usr/share/icons/Solux-Icons/` |
| Wallpapers | `/usr/share/backgrounds/solux/` |
| Logos | `/usr/share/pixmaps/solux/` |
| Apps Solux | `/usr/share/solux/<app>/` + lanzador en `/usr/bin/` |
| Lanzadores | `/usr/share/applications/*.desktop` |
| Config XFCE por defecto | `/etc/skel/.config/xfce4/` |
| Hardening | aplicado en tiempo de build por los hooks |
