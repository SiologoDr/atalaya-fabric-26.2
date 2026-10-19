---
name: posters-solo-el-jefe
description: "Cómo quiere los pósters de los jefes — presentar al jefe, sin jugadores ni lista de ataques"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-04T20:11:51.464Z
---

Los pósters de los jefes presentan AL JEFE: grande, con algunos de sus ataques como efecto visual (tornados, cuchillas, rayos…), su nombre, subtítulo y una frase. Nada de jugadores ni siluetas, ni lista de ataques con descripciones, ni franja de datos (vida, fases, botín). La barra de jefe del juego, la etiqueta HARDCORE y «Minecraft 26.2 · Fabric» sí pueden ir.

**Why:** lo dijo al ver el póster de Aeralis (2026-10-04): «lo esencial de los pósters es presentar al boss, no sus ataques».

**How to apply:** en cualquier póster nuevo (`materiales/generadores/*_poster.py`), seguir el de Nerea (`nerea_poster.py`); los tres actuales ya siguen este estilo. Ver [[jefes-rapidos-e-imponentes]].

**El listón es el póster de Nerea** (2026-10-04): le pareció «increíble, más que los demás» y pidió rehacer los de Aeralis y el Vigía «con ese mismo toque». Ese toque:
- el jefe llena la mitad derecha, visto desde abajo;
- los efectos le rodean en 3D (pasan por detrás del cuerpo y por delante solo de lo bajo, sin tapar la cara ni el pecho);
- un efecto estrella viene hacia la cámara (la cadena con el arpón, la cuchilla, la Mirada) con estelas de movimiento;
- muchas partículas propias a distintas profundidades;
- luz de contorno fuerte y capas de ambiente (haces, niebla, siluetas lejanas).

Están en `nerea_poster.py`, `aeralis_poster.py` y `vigia_poster.py`.

