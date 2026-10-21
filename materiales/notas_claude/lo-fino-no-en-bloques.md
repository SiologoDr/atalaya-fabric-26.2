---
name: lo-fino-no-en-bloques
description: "Para Juan, los detalles finos de un mob (musgo, llamas, garras, dientes, ojos, cejas, colmillos, membranas) no van en cajas: van dibujados en láminas recortadas o en una 2.ª capa"
metadata:
  type: feedback
---

El 20-10-2026, al revisar los reptiles, Juan repitió en casi todos «no son bloques». Lo dijo del musgo y las llamas de la espalda, de las garras de pies y manos, de los dientes, de los ojos y las cejas, de los colmillos y de la cresta amarilla de los raptores. Como bloques se leen toscos al lado de los dibujos del DEDsafío.

Cómo se hace en `bestiario_reptiles.py`:
- **Láminas recortadas** (`lamina`, `cruz`): planos de grosor cero con una sola cara y textura con transparencia, pintados a 32 por bloque (`B.fino`). En el juego se ven por los dos lados. Con dos cruzadas, como las plantas de Minecraft, se ven desde cualquier lado.
- **Pintores de lámina:**
  - `mata`: briznas de musgo, pelo o llamas;
  - `garras_lamina`, con `garras_mano` (una de frente y otra de perfil) y `garras_pie` (una de perfil por dedo);
  - `aleta`: crestas.
- **Dientes y colmillos:** en una 2.ª capa (`dientes_capa`, `picos_capa`), ver [[segunda-capa-como-dientes]].
- **Ojos y cejas:** pintados en la cara a 32 por bloque (`_con_cara(..., fino=True)`), no en cubos. La excepción es cuando el dibujo los tiene en bloque, como las gafas del Dáctylo, que Juan pidió así.

**Siempre pegado a la piel.** El 20-10 Juan añadió: «debe estar sujetado a la piel, no a la nada». La raíz de cada manojo va dentro de la pieza y crece pegado a ella, no hacia fuera. En la espalda, los manojos echados −75° parecían una masa flotando detrás del lomo.

**Why:** los dibujos del DEDsafío tienen el detalle fino y recortado. En cajas sale un muñeco de bloques.

**How to apply:** en cualquier mob, lo fino va desde el principio en lámina, en 2.ª capa o pintado. Las cajas quedan para el cuerpo, las patas, la cabeza y lo macizo. Ojo con una lámina rectangular vista de frente: también se lee como un bloque, así que hay que darle silueta (esquinas redondas, puntas).

Relacionado: [[recrear-primero-luego-mejorar]], [[atalaya-reptiles-2026-10]], [[atalaya-todo-propio]].
