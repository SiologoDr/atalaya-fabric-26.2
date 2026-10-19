# Para continuar (18-10-2026)

Nota para seguir en otra máquina, con Claude o a mano. Las notas de Claude sobre lo que Juan ha decidido en este
proyecto (sus gustos, lo que ya rechazó, cómo probar) están copiadas en `materiales/notas_claude/`: en la otra máquina,
Claude no las tiene, así que conviene pedirle que las lea primero (empezando por `MEMORY.md`, que es el índice).

## Dónde está todo

- **Rama:** `bestiario-pixel-minecraft` (sale de `develop`). En la otra máquina: `git fetch` y
  `git checkout bestiario-pixel-minecraft`. Cuando esté bien, se junta con `develop`.
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
  - **Hormigas (5), plantas (6) y fantasmas:** en el juego con el diseño viejo. **Falta rehacerlas** como las de arriba.

## Las reglas que salieron de esta tanda (las de Juan)

1. **El píxel de la textura, del tamaño del de Minecraft:** 16 por bloque en el mundo. Con un modelo al doble y a
   escala 0,55, el píxel es de 2 del modelo (`B.TEXEL = 2.0` en `bestiario.py`). Cada detalle se dibuja a ese píxel:
   un poro o un fideo es un píxel; un tallo, un píxel en escalera. Nada de pintar a más resolución.
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
  - `materiales/pruebas/prueba_creepers.py` y `prueba_bombas.py` crean el mundo `MiniJefes` con un datapack que pone
    los mobs y saca fotos.
  - Necesitan el mundo base `run/saves/PruebaVigia` (copian su `level.dat`). En una máquina nueva hay que crearlo
    antes: un mundo plano con ese nombre.
  - Las fotos salen solas si existe `run/atalaya_fotos.flag`: el chat `FOTO nombre` guarda
    `run/screenshots/nombre.png` (ver `FotosPrueba.java`).
  - Se lanza con `./gradlew runClient --args="--quickPlaySingleplayer MiniJefes"`.
  - Las pruebas dan visión nocturna, porque la luz del suelo recién puesto a veces no carga.

## Lo que queda pendiente

1. **Bombas:** Juan aún no ha visto la versión final (sin cara, con las texturas de material) en el juego.
2. **El Atómico:** dejarlo con su píxel (unos 21 por bloque, casi el de vanilla) o igualarlo al resto. Juan no ha
   respondido.
3. **Hormigas y plantas:** rehacerlas al píxel de Minecraft y con su rediseño.
4. **Lo que falta del catálogo:**
   - Mobs: los fantasmas (con la Espada Fantasmal y la Linterna), phantoms, reptiles, la Gleba, los del agua y los
     sueltos.
   - Momentos que dependen de mobs.
   - Cambios: el tótem con trampa, la perla nuclear, el sueño pesado, las flores con dientes y mirar la luna.
5. **Al final:** el README, y la versión solo si Juan la pide.
