---
name: recrear-primero-luego-mejorar
description: "Con una ilustración original (los mobs del DEDsafío), primero recrearla tal cual en el juego y solo después mejorarla; nunca mejorar de entrada"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T20:49:46.901Z
---

Juan, 19-10-2026, sobre los fantasmas del DEDsafío (Blanco, Negro, Amarillo, Rojo, Farola y Parca): «por el momento los fantasmas que veo en las representaciones no me gustan, debes de hacer primero recrear los fantasmas de las imágenes y luego mejorarlas».

Yo había empezado directamente con mi versión «mejorada»:
- Primero, figuras de capucha, iguales para todos.
- Luego, caras propias y cuerpos inventados.

Las dos le parecieron «horribles».

Lo mismo había pasado antes:
- Con las bombas y las arañas: «ni copiar el cartel ni copiar vanilla; superarlos».
- La regla es en dos pasos, y el primero es la copia fiel.

**Why:** si se mejora sin haber recreado antes, el diseño se aleja del original y deja de ser ese mob. Primero hay que acertar con lo que es.

Segunda corrección, sobre esa recreación hecha a mano: «se parecen pero no como las ilustraciones, más que todo las caras, las manos y su cola de fantasma… te dije que le pongas más píxeles en estos casos». Las caras dibujadas a ojo no valen.

Lo que funcionó fue calcarlas:
- Se endereza la cara del cartel (un cuadrilátero, con `calcar.py`) a 32 por bloque.
- Se clasifica en letras de la paleta, por el tono cuando hay sombra (`hacer_mapas.py`; los dos scripts están en `scratchpad/calco`).
- El resultado va como mapa en `materiales/generadores/fantasmas_mapas.py`.
- Las colas y las manos, también a 32 por bloque.

Tercera corrección: «las manos de los fantasmas no son igual, revisa bien». Luego: «solo los 4 fantasmas, no la parca ni el farolero, y cada fantasma tiene sus brazos, todos los 4».

Lo que no había visto:
- Al restar el cielo y subir el contraste salen los brazos translúcidos del Negro y del Amarillo.
- Lo que tomé por «jirones» del Rojo son sus brazos.
- El Blanco está en pose de «¡bu!»: el antebrazo sube del codo a la mano, junto a la cabeza.

Con esto, dos cosas nuevas en el método:
- Comparar desde el mismo ángulo que el dibujo, unos 39° por el lado derecho: `vista_original.py`.
- Comparar sobre su mismo fondo de cielo (`CIELO=1`), porque sobre fondo oscuro lo translúcido parece macizo.

Cuarta corrección: «los brazos y la falda tienen que ser igual entre todos; solo cambian el color y la cara». Luego Juan dibujó encima de mi captura del Blanco (azul, los brazos; verde, la cola): «sus manos deberían ser así y su cola así, porque estos fantasmas van a volar».

Con eso quedó:
- los brazos en «¡bu!» para los cuatro;
- una cola de una pieza en vez de piernas.

Después lo marcó de frente («es así»):
- cada brazo, una sola caja ancha (unos 4,5 px), sin el tramo del cuerpo al codo;
- la cola, del ancho de la cabeza.

Y luego: «el brazo tiene 2 partes… el hombro como una 2.ª capa, y su mano normal con el color del fantasma, no transparente; lo mismo con su cuerpo, que su falda sea una 2.ª capa».
- Lo translúcido va solo como 2.ª capa, medio píxel más grande, igual que la segunda capa de una skin.
- Debajo, la pieza es maciza y del color del fantasma.

Después, sobre la 2.ª capa: era como los dientes de las Fauces ([[segunda-capa-como-dientes]]). Y sobre el cuerpo: «esas partes están como más chicas y su textura no es como todo su cuerpo». Las piezas que siguen a una parte calcada:
- no van más estrechas que ella;
- llevan su misma textura: el mismo tono y las manchas de lo de más abajo del calco, no un degradado liso.

Al mejorar (19-10), yo limpié las caras calcadas y les puse pupilas de neón. Juan: «sus caras déjalas como antes, me gustaban más, y el diseño de los fantasmas mejóralos no solo en textura sino en diseño».
- Al mejorar, la cara aprobada del calco no se toca.
- La mejora es de diseño: una pieza propia por mob que salga de lo que hace (alas de hielo, la jaula con el corazón, la corona de llamas, los grilletes), con el cuerpo común intacto.

Después vino un muestrario de tres piezas por fantasma (B1–R3): «ninguno me gustó, mejor déjalo como está». Los fantasmas se quedan como la recreación, solo con las texturas del cuerpo limpias.
- Lección: con estos mobs recreados de un dibujo, añadir piezas (accesorios, coronas, jaulas, garras) no mejora nada para Juan.
- Si vuelve a pedir mejorar uno, pregúntale antes qué quiere cambiar, o pídele una referencia; no le vuelvas a ofrecer piezas añadidas.

Al alinear, la escala sale bien midiendo la tapa de la cabeza en las dos imágenes. La búsqueda a ciegas tardó mucho y falló.

Cuando Juan dibuja encima de una captura mía:
- Busco la escala y el desplazamiento de su imagen sobre mi render, ignorando sus trazos (`scratchpad/alinear_juan.py`).
- Pinto sus trazos sobre el modelo nuevo (`superponer.py`).
- Saco los puntos 3D proyectando con la misma cámara (`ajuste_brazos.py`).

**How to apply:**
1. **Estudiar el original.** Bajar el cartel en grande y ampliarlo píxel a píxel para leer bien la forma y la cara: `scratchpad/fantasmas_ref`, con medios.json y recortes.json.
2. **Recrearlo fiel**, al píxel de Minecraft:
   - las proporciones, los colores y las piezas tal cual;
   - las caras como mapas de píxeles copiados de la ilustración (`mapa()` en `bestiario_fantasmas_v2.py`);
   - nada añadido.
3. **Enseñarlo junto al original**, en una página local con el original a la izquierda.
4. **Mejorar solo cuando Juan dé la recreación por buena**, y sin perder lo que es.
5. Si un mob no tiene ilustración, no se recrea. Juan: «como no tenemos una ilustración no podemos recrearlos como tal y mejorarlos».

Con los reptiles (19-10) pasó otra vez: una recreación a ojo, con cajas lisas, fue «un chiste al lado de los originales». Lo que funcionó:
- medir cada pieza en píxeles del icono (a 4K, un píxel de textura son unos 4 del cartel);
- sacar la paleta del propio cartel;
- comparar con el contorno del original encima y en grande al lado;
- texturas de 4 o 5 tonos al píxel con su dibujo (escamas, anillos, mechones), como los originales.

Relacionado: [[seguir-referencias-al-pie]], [[atalaya-hormigas-plantas-2026-10]].
