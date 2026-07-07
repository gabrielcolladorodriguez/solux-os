# Solux Tweaks

Panel de ajustes rápidos (Python 3 + GTK 3) que une los dos usos de Solux OS: escritorio
cómodo para el día a día y estación de seguridad.

## Qué hace

- **Perfiles de uso:**
  - *Modo Diario* — firewall activo pero permisivo en la salida; cómodo para trabajar,
    navegar y ver vídeo.
  - *Modo Seguridad* — bloqueo estricto de entrada, Fail2ban reiniciado; máximo blindaje.
- **Retoques rápidos:** interruptores para el firewall, modo "no molestar" y ver el
  estado de la aleatorización de MAC.
- **Mantenimiento:** actualizar el sistema, quitar paquetes huérfanos, limpiar caché de
  APT y liberar espacio del journal.
- **Apariencia:** accesos directos a fondo de pantalla y a los ajustes de XFCE.

Las acciones con privilegios usan `pkexec`; las de usuario se aplican al momento.

## Ejecutar

```bash
python3 solux_tweaks.py
```

## Instalación en el sistema

Se copia a `/usr/share/solux/tweaks/` con lanzador `/usr/bin/solux-tweaks` y
`solux-tweaks.desktop` en `/usr/share/applications/`.
