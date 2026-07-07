# Solux Security Center

Centro de seguridad gráfico de Solux OS (Python 3 + GTK 3). Diez secciones que consultan
y accionan las defensas del sistema:

1. **Estado general** — resumen de AppArmor, UFW, Fail2ban, ClamAV y actualizaciones.
2. **Firewall** — estado de UFW y nftables; ver reglas.
3. **Antivirus** — ClamAV: firmas y escaneo de `/home`.
4. **Integridad de ficheros** — AIDE: comprobar y reconstruir base de datos.
5. **Amenazas** — rkhunter (rootkits) y Fail2ban (cárceles).
6. **Red** — puertos a la escucha, conexiones activas, aleatorización de MAC.
7. **Privacidad** — DNS cifrado, telemetría, Firejail.
8. **Actualizaciones** — parches de seguridad (unattended-upgrades).
9. **Sandbox** — AppArmor y Firejail.
10. **Auditoría** — Lynis: auditoría de hardening.

Las comprobaciones corren en hilos (no bloquean la UI). Las acciones con privilegios usan
`pkexec`.

## Ejecutar

```bash
python3 solux_security_center.py
```

## Instalación en el sistema

Se copia a `/usr/share/solux/security-center/` con lanzador `/usr/bin/solux-security-center`
y `solux-security-center.desktop` en `/usr/share/applications/`.
