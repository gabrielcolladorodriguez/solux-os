# Tema Solux Dark

Tema oscuro oficial de Solux OS para GTK 2, GTK 3, GTK 4 y el gestor de ventanas xfwm4.

- Fondo profundo `#0D0D1A`, superficies `#15152A`/`#1E1E38`.
- Acento primario naranja `#F97316`, secundario azul `#3B82F6`.
- Botones de acción sugerida con degradado naranja→oro.
- Contraste conforme a WCAG AA en todos los pares texto/fondo.

## Instalación en el sistema

Se copia a `/usr/share/themes/SoluxOS-Dark/`. Se activa por defecto vía la configuración
de XFCE (`config/xfce4/xsettings.xml`) y en `/etc/skel` para todos los usuarios nuevos.

Para probarlo en una sesión XFCE ya instalada:

```bash
xfconf-query -c xsettings -p /Net/ThemeName -s "SoluxOS-Dark"
xfconf-query -c xfwm4 -p /general/theme -s "SoluxOS-Dark"
```

## Estructura

```
SoluxOS-Dark/
├── index.theme        Metadatos del metatema
├── gtk-2.0/gtkrc      GTK 2
├── gtk-3.0/gtk.css    GTK 3
├── gtk-4.0/gtk.css    GTK 4 / libadwaita
└── xfwm4/themerc      Decoración de ventanas
```
