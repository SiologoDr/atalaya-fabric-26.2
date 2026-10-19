---
name: detalle-sin-cubos-visibles
description: "Mucho detalle de forma, sin que se note cada cubito, pero que en el juego se vea como un mob de Minecraft (bloques con textura de pixel y luz plana), como los jefes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-11T18:54:51.665Z
---

Al diseñar mobs y jefes, Juan quiere geometría rica: más piezas y siluetas complejas, como sus imágenes de referencia. Pero **no se debe notar que está hecho de cubitos**: "no tiene que verse que está conformado por bloques… estos mobs tienen más bloques pero no son perceptibles y lo ocultan con color".

Y en el juego tiene que **seguir pareciendo un mob de Minecraft**, como los jefes.

**Why:**
- 11-10-2026: pidió "crea más bloques, no te limites". La primera versión en vóxeles mostraba cada cubo y le pareció que "se ve como si estuviera conformado por muchos bloques". Le gustó el guerrero azteca una vez pintado por zonas.
- Ese mismo día, ya en el juego: "se siente rara la textura… no son como los bosses que creamos… su textura no parece ya mobs de minecraft". Cada vóxel de un píxel era geometría con la luz suavizada: parecía un render.

**How to apply:**
- Color por manchas y zonas, y dibujos de textura (escamas, pliegues, runas). Nunca ruido aleatorio por cubo ni borde por cubo.
- En el juego: la forma en bloques de unos 2 píxeles, el detalle como textura de píxel en sus caras y la luz plana por cara, como vanilla.
- Nada de luz suavizada que haga parecer un render.
- `minijefes_juego.py` ya lo hace así.

Relacionado: [[mini-jefes]], [[disenar-con-libertad]].
