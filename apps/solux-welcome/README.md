# Solux Welcome

Asistente de bienvenida de Solux OS (Python 3 + GTK 3). Se abre en el primer arranque
para orientar al usuario:

- Presentación del sistema y del lema.
- Tarjetas de acción: revisar seguridad, instalar apps, personalizar el escritorio,
  mantener el sistema actualizado.
- Enlace a la documentación.
- Interruptor "No mostrar esto al iniciar" (crea `~/.config/solux/welcome-disabled`).

## Autostart

`solux-welcome-autostart.desktop` se instala en `/etc/skel/.config/autostart/` para que
aparezca en la primera sesión de cada usuario y deje de mostrarse cuando se marca la
casilla.

## Instalación en el sistema

Se copia a `/usr/share/solux/welcome/` con lanzador `/usr/bin/solux-welcome` y el
`.desktop` en `/usr/share/applications/`.
