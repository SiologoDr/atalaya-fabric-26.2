# Ofidia y sus variantes

Ofidia es la sirena-sierpe de la tercera dungeon de **Dedsafio 4**, con diseño de
Eufonia Studio. Su cartel oficial está en
https://x.com/dedsafio/status/2109039127597560179.

Juan pidió el 12-10-2026 recrearla igual y hacerle variantes propias, «para no copiarla
como tal». Hicieron falta tres versiones:

1. La primera no se parecía: «fíjate bien cómo es Ofidia… date tu tiempo, investiga
   más».
2. La segunda tenía brazos y no estaba bien la boca: «no son manos o brazos, son alas lo
   que tiene, aparte su boca es como triangular, revisa bien su portada».
3. Esta tercera sigue la portada al detalle.

**La original es solo para estudiarla; no va al mod.** Las candidatas son las tres
variantes. A Juan le gustó la Encadenada.

## Cómo es Ofidia de verdad

Las fuentes son tres:

- la portada oficial, la más fiel;
- el retrato de su barra de jefe;
- la presentación del directo del 10-10-2026, día 18 de farfadox en Kick.

En la forma de monstruo se ve:

- **La cola**: una sierpe de tambores de mármol azul con cinturones granates con
  remaches. Se enrosca en el suelo y se alza.
- **La cintura**: un cinturón con remaches.
- **El torso**: un costillar abierto que brilla rosa por dentro. Las costillas son
  blancas y la columna, oscura con vértebras grises.
- **Dos alas, no brazos**: una viga gruesa de mármol sale de cada hombro y se abre al
  lado, con un codo y una punta. De ella cuelga la membrana azul noche, rota por abajo.
- **La cabeza** tiene:
  - una capucha puntiaguda de azul noche;
  - una visera lila con una gema blanca;
  - dos cuernos lila, una media luna lila y una espina rosa;
  - un gancho negro con remaches turquesa;
  - un tallo negro con muescas en la coronilla.
- **La boca es triangular**:
  - arriba, la mandíbula ancha con una cortina de colmillos rosas y blancos;
  - abajo, una cuña en V que acaba en punta en la barbilla, con dientes rojos;
  - por dentro brilla rosa.
- **Los tres cebos**: el de arriba sale del tallo negro y se dobla, y los de los lados
  cuelgan de debajo de la capucha. Acaban en cubos rosas encendidos.
- Fuera del combate tiene una **forma de sirena**: sentada en una roca en el mar, con
  pelo azul, piel lila, arneses negros y un vestido largo. Es la de la canción «Dulce
  Azar».

## Las variantes

Las tres tienen el mismo cuerpo que Ofidia: la cola, el costillar, las dos alas y la
boca triangular. Cambian la forma de lo que enmarca la cabeza, el material y el neón.

- **De la Capucha (azul hielo).** Su capucha se abre en una capucha de cobra enorme, con
  dos ojos falsos. No lleva cebos. Mármol de luna y cinturones de hierro.
- **De los Faroles (verde de almas).** Sus cebos son faroles con almas: seis en corona
  sobre la capucha, con cadenas entre ellos, uno a cada lado de la cabeza y otro colgando
  de la punta de cada ala. Mármol pizarra y latón.
- **Encadenada (carmesí).** Lleva:
  - grilletes oxidados en las alas con la cadena rota;
  - barrotes delante del pecho, que es una celda;
  - cadenas por la cola, y dos cadenas rotas en vez de cebos;
  - un bozal de hierro roto;
  - cuernos de carnero y jirones.

  Mármol negro con vetas rojas.

## Los bocetos

Salen de `materiales/generadores/ofidia_modelo.py` (`ofidia('O' | 'A' | 'B' | 'C')`) y
de `ofidia_escenas.py`, con las escenas `heroe_X`, `cabeza_X` (de tres cuartos, como la
portada), `cuatro` y `materiales`.
