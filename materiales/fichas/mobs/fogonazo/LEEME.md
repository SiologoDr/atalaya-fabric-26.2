# El Fogonazo

Un mob que hace algo: el bicho-luciérnaga de la noche que lleva la luz dentro. Si se te acerca, estalla como un
creeper (empuja, hace daño y rompe bloques) y te deja la pantalla en blanco 4 segundos. Juan lo pidió el 16-10-2026:
«un mob que, si se te acerca a cierta distancia, explote y te aparezca la pantalla en blanco».

## Lo que comparten las variantes

- La misma pose: agazapado a cuatro patas, con las rodillas de atrás altas.
- El pecho acorazado de placas y, detrás, levantado sobre el lomo como el abdomen de una luciérnaga, el farol.
- La cabeza de luciérnaga:
  - el escudo (el pronoto) abombado, con el borde de color y la mancha oscura;
  - los ojos compuestos, negros, con el canto de abajo encendido;
  - las mandíbulas en hoz, la boca pequeña encendida con dientes en aguja, los palpos;
  - las antenas en sierra, echadas hacia atrás.
- Al estallar se abre: levanta las placas y el escudo, abre la boca y las mandíbulas, y se le encienden los ojos.
- Mide unos 2 bloques de largo y 1,4 de alto hasta el farol.

## Las variantes

- **A, el Destello:** pizarra oscura, escudo rojo teja y luz blanca cálida. El farol va en bandas, con las placas
  detrás. Deja en blanco a todos los que estén a menos de 6 bloques. **Es el que está en el juego.**
- **B, el Argos:** pálido, de cueva, con luz blanca y fría. Su farol es un racimo de ojos cerrados, que se abren todos
  al estallar. Solo deja en blanco a quien lo mira.
- **C, el Racimo:** pardo rojizo y ámbar. En lugar del farol lleva un racimo de vainas de luz, que suelta al estallar
  y que revientan una tras otra.

## Veredicto de Juan

- **Primera ficha, 16-10-2026** (la cara era de fauces, con los ojos cerrados): «cámbiale la cara por una más tipo
  luciérnaga; que estalle a 3 bloques está bien; el blanco, 4 segundos, está bien; que al estallar sea como una
  explosión de creeper: te va a empujar, cegar y hacer daño; que salga por ahora en huevo».
- **Segunda ficha:** «este diseño va a ser, metámoslo en el juego». Eligió el Destello.

## En el juego (16-10-2026)

- Está **en silencio**: no suena al andar ni quieto. Solo suena al pegarle, al morir, en la mecha (un segundo antes
  de estallar) y en el estallido. Juan: «no va a tener ruido, va a ser silencio; un segundo antes de que explote recién
  va a sonar»; y «sonido cuando le atacas sí debe tener, lo mismo al morir».
- **Corre como un jugador que esprinta:** 5,7 bloques por segundo, medido en el juego.
- **Las animaciones:**
  - trota en diagonal, doblando las rodillas, con el farol que se balancea;
  - quieto, tantea con las antenas, mira a los lados, mueve las mandíbulas, respira y da golpecitos con las patas;
  - al cebarse, se abre.

## De dónde sale

- **Los bocetos:** `materiales/generadores/fogonazo_modelo.py` y `fogonazo_escenas.py`, en un campo de noche.
- **En el juego:**
  - `fogonazo_juego.py`: la malla de Minecraft con las mismas cajas, la textura, lo que brilla, el huevo y los nombres;
  - `fogonazo_sonidos.py`: los sonidos.
  - El código está en el README, en «El Fogonazo».
