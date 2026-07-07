# Changelog — Solux OS

Todas las novedades notables de este proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.0.0/) y el
proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] "Phoenix" — 2026-07-06

### Añadido
- Primera versión pública de Solux OS.
- Base Debian 12 Bookworm con escritorio XFCE 4.18 personalizado.
- Tema **Solux Dark** para GTK2/3/4 y XFWM4.
- Identidad visual completa: logo, 5 fondos de pantalla, paleta y tipografías.
- **Solux Store**: tienda gráfica con miles de apps open source y el arsenal de Kali.
- **Solux Security Center**: panel de seguridad con 10 secciones.
- **Solux Welcome**: asistente de primer arranque.
- **Solux Installer**: instalador gráfico basado en Calamares con cifrado LUKS por defecto.
- Endurecimiento (hardening) de seguridad en 20 fases.
- Sistema de compilación de la ISO con live-build, Docker y WSL2.

### Seguridad
- AppArmor en modo enforce global con perfiles propios.
- Firewall nftables + UFW + Fail2ban.
- AIDE, rkhunter y ClamAV con revisiones diarias automáticas.
- Kernel lockdown, sysctl restrictivo y lista negra de módulos.
- DNS cifrado, aleatorización de MAC y navegador endurecido con Firejail.

[1.0.0]: https://pollocrudo.example/solux-os/releases/1.0.0
