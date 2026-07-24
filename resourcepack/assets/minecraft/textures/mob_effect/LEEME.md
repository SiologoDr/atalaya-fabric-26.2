# Imagen del efecto de radiación

Coloca aquí la imagen del ícono del efecto de radiación.

- **Nombre sugerido:** `radiacion.png`
- **Tamaño:** 16 x 16 píxeles (PNG con transparencia)
- **Ruta final (resource pack):** `assets/minecraft/textures/mob_effect/radiacion.png`

## Importante (léelo)

Minecraft muestra los íconos de efecto desde el **cliente**, no desde el servidor.
Para que este ícono se vea, hace falta:

1. Un **resource pack** que el servidor envíe al jugador (auto-descarga), y
2. Que el efecto esté **registrado** — los efectos *totalmente nuevos* no se
   pueden añadir a un cliente vanilla sin un mod de cliente.

Por eso, hoy la radiación se comunica **100% server-side** con:
- Barra de acción: `☢ Radiacion - Nivel X`
- Sonido tipo geiger
- Partículas verdes alrededor del jugador

Cuando quieras dar el salto a un ícono/HUD custom, esta carpeta ya tiene la
estructura lista para el resource pack. Guarda aquí el arte mientras tanto.
