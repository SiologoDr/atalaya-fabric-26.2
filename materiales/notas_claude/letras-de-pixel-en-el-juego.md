---
name: letras-de-pixel-en-el-juego
description: Todo rótulo que se vea dentro de Minecraft va en letras de píxel (las de las barras de vida), nunca en fuentes de ordenador suavizadas
metadata:
  type: feedback
---

Los rótulos que salen dentro del juego (cartel de la presentación de los jefes, HUD, barras) van en **letras de píxel**: las de las barras de vida (glifos de 7 filas con trazo de 2 px, contorno oscuro y sombra; el juego completo está en `novilis_hud.py`). Para textos largos, una letra pequeña de 3×5 del mismo estilo (`presentacion_jefes.py`). El pixel art se dibuja a una base y se amplía por enteros con vecino más próximo.

**Why:** el 2026-10-08 el usuario pidió que las letras de la presentación «no las hagas como textos fuera de Minecraft, deben ser píxeles», con las mismas de la barra de vida. Antes iban en Oswald/Montserrat suavizadas, como los pósters.

**How to apply:** las fuentes de ordenador solo sirven para material de fuera del juego (pósters, teasers). Dentro del juego, siempre píxel. Ver [[todo-propio-sin-vanilla]] y [[posters-solo-el-jefe]].
