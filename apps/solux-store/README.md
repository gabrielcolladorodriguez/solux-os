# Solux Store

Tienda de aplicaciones gráfica de Solux OS (Python 3 + GTK 3).

- Lee el catálogo de `catalog.json` (categorías, subcategorías, backend por app).
- Soporta dos backends: **APT** (paquetes Debian/Kali) y **Flatpak** (Flathub).
- Instala/desinstala con privilegios vía `pkexec` (APT) sin exponer la contraseña.
- Incluye el **arsenal completo de Kali** clasificado por disciplina (recolección de
  información, análisis de vulnerabilidades, explotación, contraseñas, inalámbrico,
  sniffing, forense, reversing) más categorías de uso general (internet, ofimática,
  desarrollo, multimedia, privacidad y sistema).

## Ejecutar en desarrollo

```bash
python3 solux_store.py
```

Requiere `python3-gi`, `gir1.2-gtk-3.0` y, para instalar, `policykit-1` (pkexec) y
`flatpak` con el remoto Flathub configurado.

## Instalación en el sistema

El hook de build copia esta carpeta a `/usr/share/solux/store/` y crea el lanzador
`/usr/bin/solux-store`:

```bash
#!/bin/sh
exec python3 /usr/share/solux/store/solux_store.py "$@"
```

El archivo `solux-store.desktop` va a `/usr/share/applications/`.

## Ampliar el catálogo

Edita `catalog.json`. Cada app necesita `name`, `pkg` (identificador real del paquete),
`backend` (`apt` o `flatpak`) y `desc`. Para agrupar, usa `categories[].apps` o
`categories[].subcategories[].apps`.
