# Para continuar (19-10-2026)

Nota para seguir en otra máquina, con Claude o a mano. Las notas de Claude sobre lo que Juan ha decidido en este
proyecto (sus gustos, lo que ya rechazó, cómo probar) están copiadas en `materiales/notas_claude/`: en la otra máquina,
Claude no las tiene, así que conviene pedirle que las lea primero (empezando por `MEMORY.md`, que es el índice).

## Dónde está todo

- **Rama:** todo está en `develop` (Juan trabaja directamente en ella; no crear ramas aparte). En la otra máquina:
  `git checkout develop` y `git pull`.
- **Versión:** sigue en 1.2.2. No se sube la versión ni se deja un jar en `entrega/` hasta que Juan lo pida.

## Qué se hizo en esta tanda

Meter en el juego lo del DEDsafío 2, 3 y 4 (la investigación está en `materiales/ideas/`):

- **Catálogo** con tres menús (`/atalaya menu cambios|mobs|momentos`, `MenuCatalogoScreen`): 72 cambios de dificultad y
  28 momentos hechos.
- **El Limbo** (la dimensión del laberinto con la salida que cambia de sitio).
- **El bestiario** (los mobs nuevos), familia a familia:
  - **Creepers (7):** Atómico, Ciego, Tarta, Matojo, Marchito, Enredadera y Gelatina. El Volcánico, el Artillero y el
    Latido (con su Altavoz) se quitaron.
  - **Bombas voladoras (4):** Ámbar, Carmesí, Negra y del Abismo. Son solo el cubo con su material, la mecha y dos alas
    de verdad, de dos tramos que se doblan al batir. **Sin cara ni nada más** (lo pidió Juan).
  - **Arañas:** quitadas («se ven raras»). Las siete y su telaraña están guardadas fuera del repo por si vuelven.
  - **Hormigas (5) y plantas (6):** rehechas el 19-10 al píxel de Minecraft y como sus fichas de la DEDciclopedia
    (`bestiario_hormigas.py`, `bestiario_plantas.py`). Las hormigas van **erguidas** (cuatro patas en el suelo, el
    tórax levantado, los brazos y la cabeza arriba): la Lancera con casco de bellota y lanza, la Polvorín con la bomba en
    alto, la Cabezona de cabeza ámbar, la Radiactiva con el gáster hinchado que brilla y la Brasa con su tea. Las
    plantas: las Fauces con el tallo en J y la cabeza de dos mandíbulas, la Trampa de dos lóbulos con pestañas, la Piña
    sin cara y el Zombi Planta con la anatomía del zombi y la hiedra en 2.ª capa. **Aprobadas** («los diseños
    están god»).
  - **Fantasmas:** solo los **cuatro** con ilustración (Blanco, Negro, Amarillo y Rojo; Juan, 19-10: «no hagamos la
    parca ni el fantasma farolero»). Se están recreando de sus dibujos en `bestiario_fantasmas_v2.py`: las caras,
    calcadas del cartel a 32 por bloque (`fantasmas_mapas.py`). Los cuatro llevan **el mismo cuerpo** y solo cambian
    el color y la cara. Ese cuerpo es el que Juan marcó encima del Blanco:
    - cada brazo macizo y de su color, con el hombro arriba en una 2.ª capa como los dientes de las Fauces (picos
      que se levantan; `picos_capa`);
    - como vuelan, un cuerpo macizo de su color en vez de piernas, con la falda en una 2.ª capa de picos que cuelgan;
    - nada translúcido (Juan: «quita ese transparente»);
    - el cuerpo, del ancho de la cabeza; cuerpo y brazos, con la misma textura que la cabeza (el Amarillo y el Rojo
      siguen con lo de abajo de su calco: el parámetro `piel`).

    La recreación quedó «más o menos» (19-10). Se probó a mejorarlos (caras con neón, una pieza por fantasma y un
    muestrario de tres ideas por fantasma) y no le gustó nada: «mejor déjalo como está». **El diseño queda así**:
    las caras calcadas tal cual y las texturas del cuerpo limpias, sin motas.

    **En el juego (19-10)**, con huevo (y sueltos solo si se encienden en el menú de los mobs), en
    `bestiario/mobs/Fantasmas.java`. Vuelan y cualquier arma les hace daño (Juan: «la espada fantasmal no la hagas»).
    - Blanco: zarpazos cada ocho ticks, cada uno con Lentitud.
    - Negro: cada golpe te quita un corazón para siempre (`CorazonesRobados`, sigue al morir). Al morir suelta un
      **Corazón Blanco** por cada uno que robó; se come y te devuelve uno (Juan: «con un corazón blanco, no uno dorado»).
    - Amarillo: te gasta el tótem de la mano (`TotemInvoker`), se te mete dentro cinco segundos y sale a por otro jugador.
    - Rojo: te agarra (enraizado) y te sigue pegando hasta que muere él o mueres tú.

    La prueba es `materiales/pruebas/prueba_fantasmas.py`. Los demás fantasmas del viejo `bestiario_fantasmas.py` (sin
    ilustración) no se hacen.

## Las reglas que salieron de esta tanda (las de Juan)

1. **El píxel de la textura, del tamaño del de Minecraft:** 16 por bloque en el mundo. Con un modelo al doble y a
   escala 0,55, el píxel es de 2 del modelo (`B.TEXEL = 2.0` en `bestiario.py`). Cada detalle se dibuja a ese píxel:
   un poro o un fideo es un píxel; un tallo, un píxel en escalera. **Excepción (Juan, 19-10-2026: «en algunos casos sí
   deberías aumentar los píxeles para que quede bien»):** los detalles que a 16 por bloque salen toscos (escamas de la
   piña, dientes, ojos, mandíbulas, grietas, cuerdas, hiedra) se pintan a 32 por bloque con `B.fino(pintor)`; el
   cuerpo, a 16. Probado en hormigas y plantas (ficha de antes y después), falta que Juan lo apruebe.
2. **Rediseñar como el Blaze y el Slime:** sigue siendo el mob, pero mejor que el original. No hay que copiar el cartel
   ni el mob de vanilla, sino superarlos. Pero no todo lleva cara: una bomba es un objeto que vuela.
3. **Las alas tienen que parecer alas:** de dos tramos (brazo y mano), vistas de frente, que baten y se doblan.
4. **Mejorar texturas no es meter brillos:** se probaron el «pulido» (luz pintada) y pintar a 32 por bloque, y los dos
   se descartaron.
5. **Cambiar el diseño de un mob ya aprobado:** que Juan diga cómo, o enseñarle antes una muestra. Cuando algo no le
   convence, a veces prefiere quitarlo.
6. **Si hay ilustración del original, mirarla primero:** los carteles están en `materiales/ideas/medios.json` (la URL
   de cada cartel) y `recortes.json` (la caja de cada icono, en %).
7. **No hacer commit, push ni subir versión** sin que lo pida.

## Cómo se hacen y se prueban

- **Generadores** (en `materiales/generadores/`, se corren desde ahí):
  - `python bestiario_creepers_v7.py ../.. -` hace los creepers.
  - `python bestiario_bombas.py ../.. -` hace las bombas.
  - Las demás familias tienen su `bestiario_<familia>.py`.
  - Escriben el modelo, las texturas, el huevo y el icono del menú en `src/main/resources`.
- **Prueba en el juego:**
  - `materiales/pruebas/prueba_<familia>.py` (creepers, bombas, hormigas, plantas) crean el mundo `MiniJefes` con un
    datapack que pone los mobs y saca fotos.
  - Necesitan el mundo base `run/saves/PruebaVigia` (copian su `level.dat`). En una máquina nueva hay que crearlo
    antes: un mundo plano con ese nombre.
  - Las fotos salen solas si existe `run/atalaya_fotos.flag`: el chat `FOTO nombre` guarda
    `run/screenshots/nombre.png` (ver `FotosPrueba.java`).
  - Se lanza con `./gradlew runClient --args="--quickPlaySingleplayer MiniJefes"`.
  - Las pruebas dan visión nocturna, porque la luz del suelo recién puesto a veces no carga.

## Lo que queda pendiente

1. **Bombas:** el 19-10 se le enseñaron como están y le parecieron «excelentes». Sus textos del menú ya no hablan
   de caras.
2. **El Atómico:** se queda con su píxel (Juan, 19-10: «déjalo así, me gusta»).
3. **Hormigas y plantas:** rehechas (19-10). Con sus correcciones del mismo día: las Fauces más grandes (1,8 bloques)
   y con los dientes en 2.ª capa (`dientes_capa`), y los detalles más finos. **Aprobadas** («los diseños están god,
   me convencen»), y la Trampa escondida, más camuflada (del gris de la hierba de vanilla, hundida un píxel; solo la
   delatan las pestañas). Se prueban con
   `materiales/pruebas/prueba_hormigas.py` y `prueba_plantas.py` (mismo uso que las otras).
4. **Lo que falta del catálogo:**
   - Mobs: phantoms, reptiles, la Gleba, los del agua y los sueltos. (Los fantasmas ya están; sin Espada Fantasmal.)
     - **Phantoms (19-10):** solo el Oscuro y el Explosivo tienen dibujo (cartel del 07-10). Recreados y mejorados
       a petición de Juan («sin la TNT», el Oscuro de otro color): el Oscuro añil con alas desgarradas, garras y
       garfio; el Explosivo carbonizado con brasas, buche de fuego y mecha (`bestiario_phantoms.py`). **En el juego**
       (`bestiario/mobs/Phantoms.java`): vuelan en círculos y se lanzan en picado; el Oscuro te hace soltar un hueco
       entero del inventario y el Explosivo te deja una brasa que revienta (radio 3). Vuelan como el phantom de
       Minecraft pero al doble, como pidió Juan: la misma lógica copiada, con velocidad, aceleración y giro al doble
       y un picado cada 4-5 s. Salen en las pesadillas del
       Insomnio y con huevo. Prueba: `materiales/pruebas/prueba_phantoms.py`. Los phantoms ladrones del 2 y el 3 ya
       son un cambio.
   - **Pestaña del creativo (19-10):** todo lo del mod está en su propia pestaña, «Atalaya», con el Ojo del Vigía de
     icono (`item/PestanaAtalaya.java`), y ya no en las de Minecraft. El orden es huevos, armaduras, armas, tótems y
     corazones, objetos de los cambios y materiales. Lo de los minijuegos de los jefes sigue sin salir. Prueba:
     `materiales/pruebas/prueba_pestana.py` (fotos `pestana_*`).
   - **Reptiles (19-10):** los siete con dibujo en los carteles del día 2 y del día 4 están recreados tal cual en
     `bestiario_reptiles.py`. Son el Reptisaurio Salvaje, el Guerrero, los Dromoraptores Rojo y Azul, el Plumosaurio,
     el Dáctylo Bebé y el «Cavador» (el otro «Reptisaurio Salvaje» del día 4; el nombre es provisional). La primera
     recreación, a ojo y con cajas lisas, a Juan le pareció «un chiste al lado de los originales». La segunda está
     medida al píxel en los iconos (cuatro píxeles del cartel por píxel), con la paleta sacada del cartel y texturas de
     4 o 5 tonos con escamas, anillos y mechones como las de los originales. Se comparó cada uno con el contorno del
     original encima. La tercera se afinó pieza a pieza. La cuarta (20-10) aplica su lista de correcciones por mob:
     - lo fino ya no va en bloques (musgo, llamas, garras, dientes, ojos, colmillos y la cresta amarilla van en láminas
       recortadas o en 2.ª capa);
     - texturas nuevas en los siete;
     - los raptores con piernas y brazos de velociraptor;
     - el Plumosaurio con el cuello adelantado y la cabeza en escalera;
     - el Dáctylo rehecho como un quetzalcoatlus de pie;
     - el Cavador con pilar, extremidad y cuerpo.
     La quinta (20-10) sigue los dibujos que Juan hizo encima de los nuestros:
     - los Reptisaurios con manos, 4 dientes, ojos de línea a los costados y piel sin cuadrícula;
     - los raptores con el cuello grande, la pierna grande, el brazo en L y aletas de púas;
     - el Plumosaurio con la cabeza de una pieza, orejas y la escalera unida al cuello;
     - el Cavador con 4 colmillos y pilares de madera;
     - el Dáctylo rehecho como su icono, erguido y con las patas colgando.
     La sexta (20-10):
     - los Reptisaurios con la cara que pintó Juan y las manos giradas hacia dentro (dijo que así «quedarían
       excelentes»);
     - los raptores con anatomía de raptor (cuerpo horizontal, cola larga, pierna en zigzag), según dos referencias suyas;
     - el Plumosaurio con las aletas moradas a los lados de la cabeza («casi listo»);
     - el Cavador con los colmillos más gruesos.
     **El Dáctylo Bebé se eliminó** («no lo vamos a hacer»). La séptima (20-10):
     - los Reptisaurios con el pelo pegado a la piel, los ojos rectángulos, los colmillos enteros con la boca más
       abierta, el hueso del hombro alineado con el brazo y las manos planas mirando hacia dentro;
     - los raptores adultos, con piel de manchas grandes, cabeza de cráneo y hocico, garras gris oscuro (2 y 3) y la
       aleta de los hombros recta;
     - el Plumosaurio con las aletas abiertas y la boca pequeña.
     Después (20-10) Juan pidió el raptor «como estaba antes, y solo mejora su textura» y «mételos al juego».
     - **Raptor:** vuelve a la forma de la 6.ª, con la textura nueva.
     - **En el juego:**
       - el generador exporta el modelo, el huevo, los nombres, el retrato y las partículas
         (`python bestiario_reptiles.py ../.. -`);
       - los sonidos salen de `bestiario_sonidos_reptiles.py`;
       - las mecánicas están en `bestiario/mobs/Reptiles.java` y las fichas en `Fichas.java` (grupo REPTILES, solo con
         huevo);
       - los rótulos del chat, con `catalogo.py`;
       - la prueba es `pruebas/prueba_reptiles.py`.
     - **Ojo con `catalogo.py`:** reescribe todos los PNG de rótulos con otra compresión. Hay que devolver uno a uno los
       que no cambian de píxeles.
     - **Tamaños**, que pidió Juan: Plumosaurio 6,3 bloques, Dromoraptores 3,1, Cavador 1,0, Salvaje 2,9 y Guerrero
       2,6. Se hacen con `TAM` y `agrandar` en el generador, sin cambiar el píxel.
     - **Animaciones** rehechas (20-10):
       - reptisaurios con brazos en V, rodilla, codo, rugido y carrera;
       - raptores con rodilla, cola en dos tramos y la llamada;
       - Plumosaurio con patas que se levantan y una mirada suave que ya no da bandazos;
       - Cavador con pilares que pisan y que se hunde antes de enterrarse.
     - Sigue pendiente preguntarle por el nombre del Cavador. **Falta que la dé por buena**; después tocan la mejora, el Java, los sonidos y la
     prueba. Los que no tienen dibujo (el Dromoraptor Verde, el Arquero, el de Lanza, el Dáctylo Adulto,
     el Fluviosaurus y el Mastodino) no se recrean.
   - **Revisión de imágenes (20-10):** `materiales/ideas/imagenes_mobs.md` dice, para cada mob del DEDsafío 2, 3 y 4,
     si hay imagen y de dónde sale.
     - En el D4, el libro del juego (el bestiario que abren los streamers) tiene el icono de casi todos. La página
       completa está en elded, 13-10, 5:58.
     - **Mirarla antes de recrear un mob.** Ningún mob es «sin dibujo» sin buscar ahí.
     - El «Reptisaurio Cavador» es el **Molusco Rocoso** del libro. Ya está renombrado (`molusco_rocoso`) y con la
       mecánica del original: se entierra si te alejas y te sigue bajo tierra.
     - Los brazos de todos los reptisaurios siguen el dibujo de Juan (`BRAZO_REPTISAURIO`).
   - Momentos que dependen de mobs.
   - Cambios: el tótem con trampa, la perla nuclear, el sueño pesado, las flores con dientes y mirar la luna.
5. **Al final:** el README, y la versión solo si Juan la pide.
