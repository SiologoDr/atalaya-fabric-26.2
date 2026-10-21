---
name: atalaya-revision-imagenes-2026-10
description: "Revisión completa de imágenes de los mobs del DEDsafío 2, 3 y 4 (20-10): registro en materiales/ideas/imagenes_mobs.md; el libro del juego del D4 tiene el dibujo de casi todo"
metadata:
  type: project
---

El 20-10-2026 Juan pidió una revisión completa para que no se queden mobs sin recrear «porque no estaban sus imágenes porque se nos pasó» (ver [[buscar-imagen-antes-de-descartar]]).

**Resultado:**
- **D2**: 48 mobs. 24 con imagen buena, 20 parcial y 4 sin imagen. Las buenas salen de las fichas oficiales de los días 5 y 11 y de la DEDciclopedia en vídeo.
- **D3**: 50 mobs. 33 con imagen, 12 parcial y 5 sin imagen. Salen de los carteles, de clips de X y Twitch y del libro de crafteos de VickyPalami.
  - Mob nuevo: el **Creeper Ninja**, negro con cinta roja.
  - La calavera emplumada de los clips de muerte es REviil.
- **D4**: 71 mobs.
  - 41 tienen icono y nombre confirmado por su aviso, 13 nombre probable y 13 icono sin nombre todavía.
  - Sin imagen: Herobrine, Médusa Ósea, Guardián del Corazón y Bomba Negra.

**La fuente clave del D4 es el libro del juego.** Es la «Interfaz de Información» que abren los streamers: una fila por día con el icono de cada mob y, al pasar el ratón, su nombre, qué hace, qué suelta y dónde sale.
- La página completa está en elded, 13-10, 5:58-5:59.
- Las filas de las naves Phora salen en iChurroX, 17-10, 4:20.
- Hay más avisos leídos en elded 30-09 (1:31 y 2:37), 02-10 (5:27), 10-10 (3:45 y 4:00) y 13-10.
- **El «Reptisaurio Cavador» es el Molusco Rocoso** del libro. Ojo: en el original se entierra cuando te **alejas**, no cuando te acercas.

**Material:**
- En el repo, `materiales/ideas/imagenes_mobs.md` (solo las fuentes).
- En el scratchpad de la sesión 8b154ffb:
  - la página `revision_imagenes/index.html` y `revision_d4_pagina_1013.png`, con los iconos en `iconos_1013/`;
  - `revision_d2/` y `revision_d3/`, con un recorte por mob.
- Herramientas del scratchpad:
  - `buscar_bestiario.py`, que encuentra el libro abierto en un VOD de Kick;
  - `buscar_mobs_kick.py`, que busca la página de mobs en los VOD de 20 participantes (lista en `kick_participantes.json`). Se paró en el 25 de 527 por lento;
  - `tramo_mobs.py`, `avisos_tooltip.py`, `leer_titulos.py` (OCR con rapidocr), `coser_pagina.py` e `iconos_pagina.py`.

**How to apply:** antes de recrear un mob del DEDsafío, mirar su fila en `imagenes_mobs.md`. Si el nombre de su icono no está confirmado, buscar su aviso en el libro de un VOD (`tramo_mobs.py`) antes de empezar.
