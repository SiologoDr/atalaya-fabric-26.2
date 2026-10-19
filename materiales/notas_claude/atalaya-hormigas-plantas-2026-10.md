---
name: atalaya-hormigas-plantas-2026-10
description: "Hormigas (5) y plantas (6) del bestiario rehechas el 19-10-2026 al píxel de Minecraft y como sus fichas de la DEDciclopedia (hormigas erguidas); sin commit, falta que Juan las vea"
metadata:
  node_type: memory
  type: project
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T14:53:05.825Z
---

El 19-10-2026, con el relevo de la otra máquina (punto 3 de `materiales/CONTINUAR.md`), rehice las hormigas y las plantas del bestiario. Las mecánicas, los sonidos y los efectos no cambian (`Hormigas.java`, `Plantas.java`).

**Cómo se hicieron:**
- A escala 1 y con `B.TEXEL = 1`, todas las piezas miden píxeles enteros.
- Las piezas redondas usan `redondo()` (de `bestiario_hormigas.py`): tres cajas cruzadas, encogidas 0,04 para que ninguna cara quede a ras.
- Los pintores pintan a un píxel por detalle.
- Generadores: `bestiario_hormigas.py` y `bestiario_plantas.py`.
- Pruebas: `materiales/pruebas/prueba_hormigas.py` y `prueba_plantas.py`.

**Las referencias:** las fichas de la DEDciclopedia del D2 son los tuits 1554535823281897472 y 1554548825016209409 de @dedsafio (cuatro fotos cada uno).
- Las hormigas del original van **de pie**: cuatro patas en el suelo, el tórax erguido y la lanza en la mano. Por eso las hice erguidas.
- Las de antes eran de seis patas a ras de suelo.

**Lo que salió, y lo que corregí por el camino:**
- **Hormigas:**
  - Los ojos van a ras de las esquinas de la cabeza. Sobresaliendo parecían orejeras o gafas.
  - Las mandíbulas son de ámbar, en V. Antes parecían un bigote.
  - La frente lleva un surco en el centro. La V que tenía parecía una sonrisa.
  - El gáster tiene bisel de 2. Antes parecía un barril con duelas.
  - Lancera: bicolor, con casco de cúpula de bellota y la lanza al costado.
  - Polvorín: la bomba en alto con los dos brazos, con la cuerda pintada.
  - Cabezona: cabeza ámbar de 10×8×8 y tenazas.
  - Radiactiva: el gáster hinchado, con las membranas verdes encendidas y los ojos verdes.
  - Brasa: color carbón con vetas naranjas, y una tea.
- **Plantas:**
  - Fauces: el tallo en J de cuatro tramos y la cabeza de dos mandíbulas con dientes de 1 píxel separados. La verde lleva baba, la carmín espinas y la boca encendida, y la escarcha carámbanos.
  - Trampa: los lóbulos en escalones con pestañas.
  - Piña: sin cara, de un bloque de alto.
  - Zombi Planta: la anatomía del zombi, con la hiedra en 2.ª capa, la flor en el ojo y el arbolito a la espalda.

**Las correcciones de Juan, el mismo 19-10:** «las 3 plantas carnívoras un poco más grandes y sus dientes como 2.ª capa; en la piña, en algunos casos, sí deberías aumentar los píxeles para que quede bien; prueba eso con las hormigas y las plantas».
- **Más píxeles, pero solo en los detalles.** Esto cambia la regla del píxel de Minecraft: los detalles que a 16 por bloque salen toscos se pintan a 32 por bloque con `B.fino(pintor)`, que añade `Pintor.texel` en `bestiario.py`. El cuerpo sigue a 16.
  - En las hormigas: los ojos, la cara, las mandíbulas, el gáster, la cúpula, el pedernal, la bomba, las llamas y el cuerpo entero de la Brasa (por las grietas).
  - En las plantas: la boca y los dientes de las Fauces, la piel y la corona de la piña, la hiedra y la flor del zombi, y las venas y el césped de la Trampa.
- **Las Fauces**, de 1,8 bloques, con una caja de golpe de 1,1 × 1,85. Los dientes van en `dientes_capa`, una caja algo mayor que cada mandíbula, recortada, con dientes triangulares y la encía.
- **La piña**: una sola caja de 6 × 7 × 6 con rombos de 6 píxeles finos. Con tres cajas cruzadas, los rombos no cabían en cada cara.
- La ficha del antes y el después está en `ficha_v3/mas_pixeles_ficha.html` del scratchpad.
- Las pruebas sacan ahora fotos de cerca: `<familia>_zoom_<id>`.

**Aprobadas el 19-10-2026:** «lo demás, los diseños están god, me convencen».

Solo pidió más camuflaje para la Trampa escondida: «solo un poco debe diferenciarse; si un despistado no presta la atención mínima, va a caer en la trampa». Se hizo así:
- Lo que se ve tumbada es del gris de la hierba de vanilla: media 147, desviación 18, a 16 por bloque, que el juego tiñe.
- Está hundida 1,2 píxeles.
- Las pestañas son grises algo más claras: es lo único que la delata.

**Sin hacer:** commit de nada.

**El estado:**
- Las cajas de golpe de las hormigas pasaron a 0,9 × 1,5 en `Fichas.java`, y sus textos se cambiaron.
- La ficha local se generó en el scratchpad de la sesión 8b154ffb, en `ficha_hormigas_plantas/`.
- **Sin commit:** la regla 7 de `CONTINUAR.md` es no subir sin que lo pida.

Relacionado: [[atalaya-dos-maquinas]], [[atalaya-ideas-dedsafio]], [[atalaya-todo-propio]].
