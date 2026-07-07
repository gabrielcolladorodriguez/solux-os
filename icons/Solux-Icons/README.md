# Solux-Icons

Tema de iconos de Solux OS. Para mantener consistencia y cobertura total sin dibujar
miles de iconos, **hereda de Papirus-Dark** (software libre, GPLv3) y añade encima los
iconos de marca de las apps propias (Store, Security Center, Welcome).

Los iconos propios en formato SVG viven en `scalable/apps/`:

- `solux-store.svg`
- `solux-security-center.svg`
- `solux-welcome.svg`
- `solux-logo.svg`

En la compilación se instala `papirus-icon-theme` como base y este tema se copia a
`/usr/share/icons/Solux-Icons/`, quedando como tema de iconos por defecto.
