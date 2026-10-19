---
name: rajang-jaguar-de-jade
description: "Jefe elemental de la tierra (3 de 4), Rajang el Jaguar de Jade — referencias del usuario, reglas pedidas en el chat y ficha de diseño pendiente de aprobar"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-05T00:37:07.773Z
---

Tercer jefe elemental (tierra), empezado el 2026-10-04. El usuario lo llamó **Rajang** y pasó una lámina «Jaguar de Jade, Dominador de la Tierra» con 4 ataques más reglas de un chat:

- **Garra Terrestre** (1 jugador): picos de tierra que dañan y lanzan.
- **Terremoto Ancestral**: columnas al azar en un área amplia. Además pone lentitud y el jefe gana resistencia.
- **Sello de la Tierra** (cooperativo): 4 tótems que hay que activar a la vez, con un tiempo corto pero no tanto. Si fallan: rugido verde que lanza a todos y quita entre 2 y 8 corazones al azar.
- **Cataclismo de Jade**: meteoritos de jade con marcas en el suelo; el impacto directo mata al instante. Si mata a alguien recupera un 5 % de vida; si no mata a nadie queda paralizado 10 s.

Mi diseño propio (ficha publicada: https://claude.ai/artifact/FGaMwDdQAkZDN8q8j3H88j):
- **Aspecto (rediseño, versión 2):** la primera versión, un jaguar «de bloques», al usuario le pareció rara y hasta graciosa, nada imponente. Ahora es un **dientes de sable con anatomía realista de felino**: pecho hondo, joroba de los omoplatos, cintura recogida, anca potente, patas traseras en zigzag, cabeza baja y larga con sables de unos 2 bloques bajo los belfos y la boca encendida. El jade lleva rosetas y encima solo **accesorios**: máscara y placas de oro, cresta de cristales en el lomo, garras de obsidiana, sol de jade en el pecho tras un peto y una cola larga con anillos y punta de cristal. Unos 8 bloques a la cruz, 17 de largo y 25 con la cola.
- **Fases:** Selva → Grieta → Raíz → Corazón (en la IV el peto revienta).
- **Números propuestos:** 15.000 de vida y +10 por fase.
- **Botín:** Colmillo de Jade y Bendición de la tierra.

Generadores (en `materiales/generadores/`):
- `tierra_modelo.py`: el modelo.
- `tierra_piel.py`: la piel pintada cara por cara, a 1 texel por píxel, lista para el atlas del juego.
- `tierra_ataques.py`: mallas y texturas propias de los ataques.
- `tierra_escenas.py`: las escenas de la ficha.

Ronda 3 (2026-10-04): el usuario aprobó la anatomía pero pidió mejorar la textura (repetitiva, rara en las fases) y rehacer los ataques sin bloques de Minecraft. Se rehízo la piel: rosetas únicas, y grietas que nacen del sol del pecho y se extienden por fase. Se rehicieron los ataques:
- Garra Terrestre: esquirlas de jade.
- Terremoto Ancestral: haces de columnas hexagonales de basalto y jade, onda de losas, avisos hexagonales, lastre ámbar y aros de runas de oro para la Piel de Jade.
- Sello de la Tierra: estelas talladas con aro flotante y círculo del sello con cuenta atrás.
- Cataclismo de Jade: fragmentos con llama, cielo rajado, marcas con cuenta atrás y cráteres.

**Why:** mismo proceso que Nerea y Aeralis: ficha, aprobación y luego construir. Pidió «primero haz el diseño y luego vamos con todo lo demás».

**How to apply:** en los felinos (y en general), primero anatomía real del animal y luego los adornos; nada caricaturesco. No construir nada en el mod hasta que apruebe la ficha. Preguntas abiertas: el aspecto, la mecánica de la fase IV (salta y el Cataclismo vuelve antes, sin el «agotado» cada 25 s) y los números. Ver [[disenar-con-libertad]], [[jefes-rapidos-e-imponentes]], [[mariposa-vendaval]].

Ronda 4 (2026-10-04): le gustó, pero pidió acercarlo a sus ilustraciones. Se mantuvo la anatomía y se añadió:
- piel en **mosaico de bloques de jade** con bisel y esmeraldas sueltas;
- **espirales cuadradas de oro** en hombros, costados, frente, carrilleras y patas;
- **cúmulos de cristales** en bloque;
- más dientes y la boca oscura que brilla.

Ataques al estilo de las ilustraciones:
- esquirlas de **roca parda** en cúmulos;
- pilares de roca en bloques;
- terrones cúbicos.

El **Sello** cambió de mecánica a petición suya: cada tótem (columna de glifos verdes) está en lo alto de una **plataforma de tierra a la que se sube con parkour** (piedras flotantes en espiral) y **hay que romperlo**. Propuesta: los cuatro con menos de 8 s entre el primero y el último, dentro de 25 s; detrás se alza el Coloso de Tierra (Rajang gigante de roca, paleta «fase 5»). Las plataformas serían bloques propios del mod que se deshacen después.

**Construido en el mod (2026-10-04)** tras su «listo, creemos al boss».
- **Números:** 15 000 de vida y +10 por fase.
- **Sello:** se quitó la ventana de 8 s entre el primer y el último tótem (los rotos se rehacían sin avisar y parecía un bug). Ahora un tótem roto se queda roto, y Rajang es inmune mientras dura el Sello.
- **Generadores:**
  - `rajang_juego.py`: malla y atlas 1024² pintado por texel, con el origen en el pecho (DESPLAZA 56 px).
  - `rajang_juego_anim.py`: 19 animaciones y RajangGeometria.
  - `rajang_piezas.py`: texturas de las piezas y del bloque.
  - `rajang_sonidos.py`: 41 eventos.
  - `rajang_hud.py` y `rajang_extras.py`: barra, partículas, icono, huevo y miedo.
- **Java:**
  - Entidades: `RajangEntity`; cajas extra en cabeza y grupa con `RajangParteEntity`; `PicoTierraEntity`, `PilarTierraEntity`, `TotemSelloEntity`, `ColosoTierraEntity`, `FragmentoJadeEntity`.
  - Bloque temporal `tierra_sello` (AtalayaBloques).
  - Efectos `peso_tierra` y `bendicion_tierra`.
  - Comando `/atalaya rajang <orden>`.
- **Prueba:** probado en el juego con `rajang_escena.py` (46 fotos), sin errores. El salto se arregló para que suba 3,5 bloques en arco.

**Revisión tras probarlo (2026-10-04)**, a petición suya:
- **Quitado el Coloso de Tierra.** El Rugido de Jade (Sello fallido) lo hace el propio Rajang: vuelve al estado RUGIDO con `rugidoFinal`.
- **Ningún bloque del mundo, ni propio.** El Sello usa `PlataformaSelloEntity`, que se pisa con `canBeCollidedWith`:
  - columna de **26 de alto** (pidió el doble) y 4 de ancho;
  - 25 piedras flotantes en espiral, cada una un bloque más alta;
  - las 4 columnas van en las diagonales de Rajang, a 18 bloques.
  - El juego solo busca choques con entidades cuyo origen está a ≤4 bloques por debajo, así que la columna se pisa por **tramos invisibles de 3 bloques** (tipo TRAMO).
  - Sello de 45 s (con 25 saltos, 30 s no daban).
- **Garra:** un zarpazo de verdad (tajo en el aire, daño en un abanico delante, marcas de garra en el suelo y sonido `zarpazo`), y luego una fila de **pinchos en bloque escalonados**, al estilo de los pilares del Terremoto, que le gustan.
- **Galope:** el reloj va a velocidad/0,89 bloques por tick, porque las zarpas iban 3 veces más rápido que el suelo; además el cuerpo va más bajo.
- **Cristales:** cambian de color en cada fase (verde → verde vivo → lima → oro), con latido y chispas en cada fase.
- **Meteoritos:** terrón de jade en bloques que da vueltas y deja cráter de terrones.
- **Miedo de tierra:** más sutil, solo en los bordes.
- **Cataclismo:** bajada con pose propia (antes reusaba el golpe del Terremoto y resbalaba hacia delante). `ponerEstado` corta un salto a medias: si no, quedaba `saltando` activo y en la fase IV resbalaba alzado.
- **Vitrina en el juego:** `rajang_vitrina.py` (en el scratchpad) monta en PruebaVigia un recorrido de unos 3 min por todo el combate, sin textos en pantalla. Se repite cada vez que se abre ese mundo.

**How to apply (tierra):** sus ataques en bloques escalonados le parecen «de Minecraft»; las esquirlas facetadas, raras. Para comprobar que algo se pisa, haz una prueba de verdad (`tellraw` con `Pos[1]`).


**Ajustes del 2026-10-08 (pedidos por el usuario, en 1.1.10):**
- El Peso de la Tierra dura siempre **2 s**, venga de donde venga.
- Embestida: 2 s más de aviso con la flecha puesta; solo sigue a su presa el primer segundo y luego el rumbo queda fijo, para que dé tiempo a apartarse.
- Ídolo de Oro: Rajang solo anda o corre hacia el portador y solo usa la Garra (que, si le da, recupera el ídolo); el ídolo se ve **sobre la cabeza** del portador y una flecha con los metros más un camino de oro señalan el altar.
  - Un jugador no se puede montar (el servidor no deja), así que lo pinta el propio RajangRenderer a partir del id sincronizado del portador.
- Escalones del Sello: el que se pisa tiembla a los 0,8 s y cae. Con 100 piedras, que temblaran al azar no se notaba («no se rompen»).
