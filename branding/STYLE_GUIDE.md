# Guía de estilo de marca — Solux OS

La identidad de Solux OS transmite **seguridad, energía y renacimiento** (el "Phoenix").
Un sol tecnológico sobre la oscuridad: cálido pero preciso.

## Paleta de colores

### Principales

| Nombre | Hex | Uso |
|--------|-----|-----|
| Solux Orange | `#F97316` | Color de marca primario, acentos, botones principales |
| Solux Gold | `#FBBF24` | Degradado del sol, resaltados |
| Solux Blue | `#3B82F6` | Color secundario, enlaces, anillo del logo |
| Solux Cyan | `#22D3EE` | Acentos fríos, gráficos, estados "info" |

### Fondos y superficies (tema oscuro)

| Nombre | Hex | Uso |
|--------|-----|-----|
| Base | `#0D0D1A` | Fondo principal de la interfaz |
| Surface | `#15152A` | Tarjetas, paneles |
| Surface Alt | `#1E1E38` | Superficies elevadas, hover |
| Border | `#2A2A4A` | Bordes y separadores |

### Texto

| Nombre | Hex | Contraste sobre Base | Uso |
|--------|-----|----------------------|-----|
| Text Primary | `#F1F5F9` | ~15:1 | Texto principal |
| Text Secondary | `#94A3B8` | ~7:1 | Texto secundario |
| Text Disabled | `#64748B` | ~3.5:1 | Texto deshabilitado (mínimo AA para UI) |

### Estados

| Nombre | Hex | Uso |
|--------|-----|-----|
| Success | `#22C55E` | Correcto, protegido |
| Warning | `#F59E0B` | Advertencia |
| Danger | `#EF4444` | Error, amenaza |
| Info | `#38BDF8` | Información |

> **Accesibilidad:** todos los pares texto/fondo cumplen WCAG AA. Nunca se usa `#475569`
> sobre fondo oscuro (contraste insuficiente); se sustituyó por `#64748B` o `#94A3B8`.

## Tipografía

- **Interfaz:** Inter (respaldo: Noto Sans, sans-serif).
- **Monoespaciada / terminal / código:** JetBrains Mono (respaldo: Fira Mono, monospace).
- **Titulares de marca:** Inter Display / Inter con peso 800.

Escala tipográfica (px): 12 · 14 · 16 · 20 · 24 · 32 · 48.

## Logo

- **Símbolo:** un sol estilizado con rayos y la letra "S" integrada, en degradado
  naranja→oro, rodeado por un anillo azul (órbita/escudo).
- **Variantes:** `solux-logo.svg` (completo), `solux-logo-mark.svg` (solo símbolo),
  `solux-logo-mono.svg` (monocromo para fondos claros).
- **Área de protección:** margen mínimo igual a la altura de la "S" alrededor del símbolo.
- **Tamaño mínimo:** 24 px de alto para el símbolo.
- **Prohibido:** deformar, rotar, cambiar los colores del degradado o añadir sombras
  duras ajenas a la marca.

## Voz y tono

- Cercano pero riguroso. La seguridad se explica, no se impone.
- Español neutro por defecto; términos técnicos en su forma más reconocible.
- Lema: **"Seguridad que renace contigo."**
