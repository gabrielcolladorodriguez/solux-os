# Solux OS 1.0 "Phoenix"

**El sistema operativo de ciberseguridad de Pollocrudo Company**
© 2026 Pollocrudo Company — Todos los derechos reservados.

---

Solux OS es una distribución Linux completa, original y de alta calidad, basada en
**Debian 12 (Bookworm)** con un escritorio **XFCE4** profundamente personalizado. Es un
sistema **de doble propósito**, igual que Kali Linux: sirve como **estación de
ciberseguridad** (con el arsenal completo de Kali y hardening estricto) y a la vez como
**escritorio cómodo para el día a día** (navegador, ofimática, multimedia, juegos y
comunicación). Incluye su propia **tienda de aplicaciones** (Solux Store) con miles de
programas de código abierto, un **centro de seguridad**, un panel de **ajustes rápidos**
(Solux Tweaks), un **asistente de bienvenida**, un **instalador gráfico** y una identidad
visual única.

> "De las cenizas del software cerrado, renace la libertad segura." — Lema de Solux OS

---

## Tabla de contenidos

- [Filosofía](#filosofía)
- [Características principales](#características-principales)
- [Identidad visual](#identidad-visual)
- [Aplicaciones propias](#aplicaciones-propias)
- [Seguridad extrema (hardening)](#seguridad-extrema-hardening)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo compilar la ISO](#cómo-compilar-la-iso)
- [Requisitos del sistema](#requisitos-del-sistema)
- [Créditos y licencia](#créditos-y-licencia)

---

## Filosofía

Solux OS nace con tres principios innegociables:

1. **Seguridad primero.** Cada decisión por defecto prioriza la protección del usuario:
   cifrado, sandboxing, firewall estricto, autenticación robusta y auditoría continua.
2. **Libertad total.** 100% software libre y de código abierto. Sin telemetría, sin
   rastreo, sin puertas traseras. El usuario es dueño de su máquina.
3. **Belleza y usabilidad.** La seguridad no está reñida con una experiencia elegante,
   coherente y original. Solux OS se ve y se siente distinto a todo lo demás.

## Características principales

| Área | Detalle |
|------|---------|
| **Base** | Debian 12 Bookworm (estable) + kernel endurecido |
| **Escritorio** | XFCE 4.18 con tema Solux Dark, dock, panel y layout propios |
| **Seguridad** | Hardening de 20 fases, AppArmor *enforce*, nftables, Fail2ban, AIDE, rkhunter, ClamAV |
| **Privacidad** | Sin telemetría, DNS cifrado, aleatorización de MAC, navegador endurecido |
| **Uso diario** | Firefox endurecido, LibreOffice, VLC, GIMP, correo, comunicación y juegos |
| **Herramientas** | Arsenal completo de Kali (600+), más miles de apps open source en la Store |
| **Cifrado** | LUKS full-disk por defecto en el instalador, `/home` cifrable |
| **Apps propias** | Solux Store, Solux Security Center, Solux Welcome, Solux Installer |
| **Idiomas** | Español e inglés por defecto, más locales de Debian |

## Identidad visual

- **Nombre:** Solux OS 1.0 "Phoenix"
- **Colores de marca:** Naranja `#F97316` + Azul `#3B82F6` sobre fondo oscuro `#0D0D1A`
- **Logo:** un sol estilizado con la letra "S", en degradado naranja-oro con anillo azul.
- **Tipografía:** Inter (interfaz) + JetBrains Mono (terminal y código).
- **Fondos de pantalla:** 5 wallpapers originales incluidos (ver `assets/wallpapers/`).

## Aplicaciones propias

| App | Descripción |
|-----|-------------|
| **Solux Store** | Tienda gráfica con miles de apps open source clasificadas por categoría (seguridad, internet, ofimática, comunicación, multimedia, juegos, diseño, desarrollo, virtualización…), incluyendo todo el arsenal de Kali. |
| **Solux Security Center** | Panel de control de seguridad con 10 secciones: estado, firewall, antivirus, integridad, amenazas, red, privacidad, actualizaciones, sandbox y auditoría. |
| **Solux Tweaks** | Ajustes rápidos: alterna entre *Modo Diario* (cómodo) y *Modo Seguridad* (blindado), retoques y mantenimiento sin abrir el terminal. |
| **Solux Welcome** | Asistente de primer arranque que guía la configuración inicial y la seguridad. |
| **Solux Installer** | Instalador gráfico (basado en Calamares) con cifrado LUKS por defecto. |

## Seguridad extrema (hardening)

Solux OS aplica un endurecimiento en 20 fases (ver `build/hooks/03-security.sh`):

- Kernel lockdown, `sysctl` restrictivo, BPF deshabilitado para usuarios sin privilegios.
- Lista negra de módulos (`dccp`, `sctp`, `firewire`, protocolos poco comunes).
- AppArmor en modo *enforce* para todo + perfiles propios de las apps Solux.
- SSH solo con clave, `MaxAuthTries 2`, sin reenvío.
- Firewall **nftables** con estado + **UFW** (deny incoming) + **Fail2ban** (baneo 2 semanas).
- **PAM** con contraseñas de 16+ caracteres y bloqueo por intentos fallidos.
- **AIDE** (integridad de ficheros), **rkhunter** (rootkits), **ClamAV** (antivirus) con cron diario.
- `unattended-upgrades` de seguridad, **Firejail** para sandboxing de navegadores.
- Aleatorización de MAC, DNS cifrado, `/tmp` y `/dev/shm` con `noexec,nosuid,nodev`.
- `hidepid=2` en `/proc`, contraseña en GRUB, más de 20 servicios innecesarios deshabilitados.

## Estructura del proyecto

```
Solux OS/
├── README.md                     Este archivo
├── LICENSE                       Licencia (GPLv3)
├── CHANGELOG.md                  Historial de versiones
├── docs/                         Documentación técnica
│   ├── SECURITY.md               Modelo de seguridad y hardening
│   ├── BUILD.md                  Guía de compilación detallada
│   └── ARCHITECTURE.md           Arquitectura del sistema
├── assets/                       Marca: logos y fondos de pantalla
│   ├── logos/
│   └── wallpapers/
├── branding/                     Colores, tipografías y guía de estilo
├── themes/SoluxOS-Dark/          Tema GTK2/3/4 + XFWM4
├── icons/Solux-Icons/            Índice del tema de iconos
├── config/                       Configuración del escritorio
│   ├── xfce4/
│   ├── conky/
│   ├── grub/
│   └── plymouth/
├── apps/                         Aplicaciones propias (Python/GTK3)
│   ├── solux-store/
│   ├── solux-security-center/
│   └── solux-welcome/
├── installer/calamares/          Instalador gráfico
└── build/                        Sistema de compilación de la ISO
    ├── build.sh                  Constructor con live-build
    ├── Dockerfile                Compilación vía Docker
    ├── docker-build.ps1          Script Windows (Docker)
    ├── wsl-build.ps1             Script Windows (WSL2)
    ├── config/package-lists/     Listas de paquetes
    └── hooks/                    Hooks de personalización y hardening
```

## Cómo compilar la ISO

Solux OS se compila con **live-build** de Debian, en un entorno Linux. Desde Windows
tienes dos rutas (ver `docs/BUILD.md` para el detalle):

**Opción A — WSL2 (recomendada en Windows):**
```powershell
wsl --install Debian           # una sola vez, como administrador
.\build\wsl-build.ps1          # compila la ISO dentro de WSL2
```

**Opción B — Docker:**
```powershell
.\build\docker-build.ps1       # requiere Docker Desktop
```

**Opción C — Linux nativo:**
```bash
cd build
sudo ./build.sh
```

El resultado es `solux-os-1.0-phoenix-amd64.iso`, arrancable en BIOS y UEFI, lista para
grabar en USB o probar en una máquina virtual.

## Requisitos del sistema

| | Mínimo | Recomendado |
|---|---|---|
| CPU | 2 núcleos x86-64 | 4+ núcleos |
| RAM | 2 GB | 8 GB |
| Disco | 25 GB | 60 GB SSD |
| Firmware | BIOS o UEFI | UEFI con Secure Boot |
| Gráficos | 1024×768 | 1920×1080+ |

## Créditos y licencia

Solux OS es un proyecto de **Pollocrudo Company** © 2026.

Distribuido bajo licencia **GNU GPLv3** (ver `LICENSE`). Solux OS se construye sobre el
trabajo de Debian, XFCE, Kali Linux, y miles de proyectos de software libre a quienes
agradecemos y respetamos. Las marcas de terceros pertenecen a sus respectivos dueños.

---

*Solux OS — Seguridad que renace contigo.*
