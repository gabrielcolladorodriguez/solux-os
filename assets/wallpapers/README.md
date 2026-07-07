# Fondos de pantalla de Solux OS

Solux OS incluye **dos juegos** de fondos:

1. **Fotográficos oficiales** (`photo/solux-wallpaper-0*.jpg`) — los fondos de marca de
   Pollocrudo Company (sol dorado sobre azul). El `solux-wallpaper-01.jpg` es el **fondo
   por defecto** del escritorio y de la pantalla de login. Se copian tal cual a
   `/usr/share/backgrounds/solux/`.
2. **Vectoriales originales** (`0*.svg`) — cinco alternativas SVG escalables a cualquier
   resolución. En la compilación se rasterizan a PNG 1920×1080 y se copian junto a los
   anteriores, para que el usuario pueda elegir.

El hook de branding crea un enlace `default.jpg` al fondo elegido, que es al que apuntan
la config de XFCE y el greeter de LightDM.

| Archivo | Nombre | Descripción |
|---------|--------|-------------|
| `01-phoenix-dawn.svg` | Phoenix Dawn | Amanecer sobre montañas, el "renacer" de Solux. Fondo por defecto. |
| `02-synthwave-grid.svg` | Synthwave Grid | Retícula synthwave con sol en bandas. |
| `03-secure-waves.svg` | Secure Waves | Ondas de degradado naranja→azul con escudo tenue. |
| `04-cyber-matrix.svg` | Cyber Matrix | Malla hexagonal con grafo de nodos. |
| `05-solux-minimal.svg` | Solux Minimal | Logo centrado, minimalista. |

## Rasterizar a PNG

Con Inkscape o rsvg-convert (lo hace el hook de build automáticamente):

```bash
for f in *.svg; do
  rsvg-convert -w 1920 -h 1080 "$f" -o "../../build/generated/${f%.svg}.png"
  rsvg-convert -w 3840 -h 2160 "$f" -o "../../build/generated/${f%.svg}-4k.png"
done
```

El fondo por defecto (`01-phoenix-dawn`) se referencia desde la configuración de XFCE en
`config/xfce4/xfce4-desktop.xml`.
