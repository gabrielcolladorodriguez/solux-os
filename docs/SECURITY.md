# Modelo de seguridad de Solux OS

Solux OS está diseñado bajo el principio de **seguridad por defecto y en profundidad**
(*defense in depth*). Este documento describe el modelo de amenazas, las capas de
protección y cómo verificar que el endurecimiento está activo.

## Modelo de amenazas

Solux OS protege principalmente contra:

1. **Atacante remoto en la red.** Firewall estricto (deny incoming), sin servicios
   escuchando por defecto, SSH solo con clave, Fail2ban.
2. **Malware local / persistencia.** AppArmor enforce, `noexec` en directorios volátiles,
   ClamAV, rkhunter, AIDE para detectar cambios en ficheros críticos.
3. **Escalada de privilegios.** Kernel lockdown, sysctl restrictivo, BPF deshabilitado
   para usuarios sin privilegios, `hidepid=2`.
4. **Robo físico del dispositivo.** Cifrado LUKS de disco completo, contraseña de GRUB,
   bloqueo de sesión.
5. **Fuga de privacidad.** Sin telemetría, DNS cifrado, aleatorización de MAC, sandboxing
   del navegador.

Fuera de alcance: ataques de firmware/hardware (UEFI malicioso), un atacante con acceso
físico prolongado y sin cifrado, o un usuario root que desactiva deliberadamente las
protecciones.

## Capas de protección (20 fases del hardening)

El script `build/hooks/03-security.sh` aplica, en orden:

| # | Fase | Qué hace |
|---|------|----------|
| 1 | Kernel cmdline | `lockdown=confidentiality`, `slab_nomerge`, `init_on_alloc=1`, `page_alloc.shuffle=1` |
| 2 | sysctl | Restringe `kptr`, `dmesg`, `ptrace`, `bpf`, `unprivileged_userns`, endurece la red (rp_filter, SYN cookies, no redirects) |
| 3 | Módulos | Lista negra: `dccp`, `sctp`, `rds`, `tipc`, `firewire`, `thunderbolt`, `usb-storage` opcional |
| 4 | AppArmor | `enforce` global + perfiles propios de las apps Solux |
| 5 | SSH | Solo clave, `MaxAuthTries 2`, sin X11/agent forwarding, `AllowUsers` |
| 6 | nftables | Firewall con estado, drop de paquetes inválidos, SSH con límite de tasa |
| 7 | UFW | `deny incoming`, `allow outgoing`, SSH solo desde LAN |
| 8 | Fail2ban | Baneo de 2 semanas tras 2 fallos SSH; jail `recidive` |
| 9 | PAM | Contraseña mínima de 16 caracteres, `pam_faillock` (bloqueo tras 5 fallos) |
| 10 | AIDE | Línea base de integridad + cron diario |
| 11 | rkhunter | Comprobación de rootkits diaria |
| 12 | ClamAV | Escaneo diario de `/home` y `/tmp` |
| 13 | Actualizaciones | `unattended-upgrades` solo de seguridad |
| 14 | Firejail | Perfiles de sandbox por defecto + wrappers de navegador |
| 15 | Red / MAC | Aleatorización de MAC vía NetworkManager |
| 16 | DNS | dnscrypt-proxy o DNS-over-TLS en NetworkManager |
| 17 | GRUB | Contraseña PBKDF2 para editar entradas de arranque |
| 18 | Montajes | `/tmp`, `/var/tmp`, `/dev/shm` como tmpfs con `noexec,nosuid,nodev` |
| 19 | /proc | `hidepid=2` para ocultar procesos de otros usuarios |
| 20 | Servicios | Deshabilita 20+ servicios innecesarios (avahi, bluetooth, cups-browsed, etc.) |

## Cuenta de usuario y arranque en vivo

- El usuario en vivo es `solux`, con cambio de contraseña forzado en el primer inicio.
- La cuenta `root` está **bloqueada**; la administración se hace vía `sudo`.
- El instalador exige una contraseña fuerte y ofrece cifrado LUKS activado por defecto.

## Cómo verificar el hardening

Tras instalar, ejecuta desde el Solux Security Center o el terminal:

```bash
# AppArmor
sudo aa-status

# Firewall
sudo nft list ruleset
sudo ufw status verbose

# sysctl endurecido
sysctl kernel.kptr_restrict kernel.unprivileged_bpf_disabled

# Integridad
sudo aide --check

# Rootkits / antivirus
sudo rkhunter --check --skip-keypress
sudo clamscan -r --bell -i /home

# Servicios activos
systemctl list-unit-files --state=enabled
```

## Divulgación responsable

Si encuentras una vulnerabilidad, repórtala de forma privada a
`security@pollocrudo.example`. Agradecemos la divulgación responsable y damos crédito a
quien lo desee.
