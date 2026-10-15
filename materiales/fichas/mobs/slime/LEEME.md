# El Slime, rediseñado

El rediseño del **Slime** de vanilla para que imponga, en tres tipos. Sigue siendo un Slime:

- el cubo de gelatina que se transparenta;
- el cubo de dentro con la cara delante;
- el charco que deja.

Lo nuevo:

- una **cara de monstruo** que brilla a través de la gelatina: el ceño en uve y los ojos rasgados;
- en cada tipo, **una cosa grande que lo cambia**: unas fauces, armas clavadas o el ácido.

Se hizo después del Blaze, con la misma idea: que se reconozca el mob, pero que imponga. Juan no
mandó referencias.

Juan lo aprobó el 15-10-2026: «guarda el mob». Después pidió pasar a mobs que hagan algo.

## Lo que comparten los tres

- **La gelatina, translúcida de verdad:** se ve lo que hay dentro y lo que hay detrás. Tiene el
  canto un tono más claro, un brillo en forma de L arriba a la izquierda y un par de burbujas.
- **El cubo de dentro** y, delante, **la cara**, como en el de vanilla, pero de monstruo.
- **La pose:** plantado sobre su charco.
- **El tamaño:** 3 bloques de ancho; el Slime grande de vanilla mide 2.
- **La construcción:** cajas a un téxel por píxel y los dientes en hoja.

## Los tres tipos

| Tipo | Lo que lo cambia | La cara | La gelatina | Alto |
|---|---|---|---|---|
| A · el Tragón | el cubo se abre en fauces (la parte de arriba se levanta, con la bisagra detrás). Tiene dientes de gelatina dura, babas, la garganta que brilla, y dentro, huesos y un yelmo | ojos verdes | verde de siempre | casi 3 bloques |
| B · el Erizo | las armas de los que no pudieron con él, clavadas: tres espadas, un hacha, cinco flechas, una lanza y un escudo hundido de canto | ojos ámbar y una mueca de dientes | verde de ciénaga, azulada | 3,7 bloques con las espadas |
| C · el Fundido | se derrite: goterones cortos desde el borde de arriba, el charco de ácido que brilla con huesos comidos y burbujas que suben por los lados | ojos que lloran ácido y la boca como una raja que brilla | negra | 2,6 bloques; el charco, casi 4 |

## Lo que se aprendió en las pruebas

- Un núcleo pequeño entre los ojos se lee como una nariz. Va grande y detrás de la cara, como en
  vanilla.
- Los chorretones largos por las caras hacen rayas.
- Un charco con el borde encendido en cada losa parece una placa de circuitos.
- Las motas encendidas ensucian.

## Los bocetos

Salen de:

- `materiales/generadores/slime_modelo.py`:
  - `slime('A')`, `'B'` y `'C'` devuelven lo opaco, la gelatina y la información;
  - `dibujar()` pinta la gelatina translúcida, de atrás adelante;
  - `vanilla_a_escala()` es el Slime de vanilla, dibujado por nosotros para comparar.
- `slime_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `tres` (con el Slime de
  vanilla y un jugador) y `materiales`.

La escena es la ciénaga de noche: agua oscura con nenúfares, islas de césped, robles de pantano con
lianas, setas, la luna cuadrada y luciérnagas.

Todas las fotos van sin letras y con el borde blanco:

- `slime_<tipo>_heroe.jpg`, `slime_<tipo>_cabeza.jpg` y `slime_<tipo>_cartel.jpg`, con los tipos
  tragon, erizo y fundido;
- `slime_tres_variantes.jpg` y `slime_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `slime_ficha.html`: se abre con el
navegador.
