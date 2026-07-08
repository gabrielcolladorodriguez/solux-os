# Solux Browser

Navegador web propio de Solux OS (Python 3 + GTK 3 + **WebKit2GTK**).

El **motor de render** es WebKit (software libre, el mismo de GNOME Web/Epiphany o Safari);
la **aplicación** —interfaz, marca, pestañas, modo privado, integración con Solux— es
original de Solux OS. Ningún navegador escribe su propio motor desde cero (ni Brave, ni
Edge, ni Vivaldi); todos usan Blink o WebKit. Solux Browser hace lo mismo, con tu marca.

## Funciones
- Pestañas reordenables con título y cierre.
- Navegación atrás/adelante/recargar y barra de direcciones inteligente.
- Búsqueda con **DuckDuckGo** (privacidad) si no escribes una URL.
- **Modo privado** (`solux-browser --private`): contexto efímero, sin historial ni cookies.
- DNT activado, sin prefetch de DNS, sin telemetría, tema oscuro Solux.
- Accesos directos a Solux Store y Centro de Seguridad desde el menú.

## Dependencias
`python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-webkit2-4.1` (o 4.0), `libwebkit2gtk-4.1-0`.

## Ejecutar
```bash
python3 solux_browser.py            # normal
python3 solux_browser.py --private  # ventana privada
```

## Instalación en el sistema
Se copia a `/usr/share/solux/browser/` con lanzador `/usr/bin/solux-browser` y
`solux-browser.desktop` en `/usr/share/applications/`.
