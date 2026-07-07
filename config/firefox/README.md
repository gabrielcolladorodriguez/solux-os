# Firefox endurecido de Solux OS

Configuración de Firefox ESR pensada para **privacidad fuerte sin romper el uso diario**
(banca, compras, vídeo, videollamadas).

## Archivos

- `user.js` — preferencias del perfil: sin telemetría, DNS-over-HTTPS, HTTPS-Only,
  protección de rastreo estricta (Total Cookie Protection), WebRTC activo pero sin fuga
  de IP local. Deliberadamente **no** activa `resistFingerprinting` ni el borrado total
  al cerrar, para no molestar en el día a día (el usuario puede activarlos).
- `policies.json` — políticas de empresa: desactiva Pocket/estudios/telemetría,
  preinstala **uBlock Origin**, fuerza HTTPS-Only y limpia la página de inicio.

## Instalación en el sistema (hook de build)

- `policies.json` → `/usr/lib/firefox-esr/distribution/policies.json`
- `user.js` → se aplica a todos los perfiles nuevos vía autoconfig:
  - `/usr/lib/firefox-esr/defaults/pref/autoconfig.js` apunta a `solux.cfg`
  - `/usr/lib/firefox-esr/solux.cfg` incluye estas preferencias
  - y se copia como `user.js` a `/etc/skel` para el primer perfil.

Firefox arranca además dentro de un sandbox de **Firejail** (fase 14 del hardening).
