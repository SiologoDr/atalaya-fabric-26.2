# Ofidia y sus variantes

Ofidia es la sirena-sierpe de la tercera dungeon de **Dedsafio 4**, con diseño de
Eufonia Studio. Su cartel oficial está en
https://x.com/dedsafio/status/2109039127597560179.

Juan pidió el 12-10-2026 recrearla igual y hacerle variantes propias, «para no copiarla
como tal». La primera versión no se parecía, porque le faltaban los brazos, la boca de
monstruo y la cola: «fíjate bien cómo es Ofidia… date tu tiempo, investiga más». Esta
segunda versión sale de estudiarla fotograma a fotograma.

**La original es solo para estudiarla; no va al mod.** Las candidatas son las tres
variantes. A Juan le gustó la Encadenada.

## Cómo es Ofidia de verdad

Las fuentes son tres:

- el cartel oficial;
- el retrato de su barra de jefe;
- la presentación del directo del 10-10-2026, día 18 de farfadox en Kick.

En la forma de monstruo se ve:

- **La cola**: una sierpe de tambores de mármol azul con cinturones granates con
  remaches. Se enrosca en el suelo y se alza.
- **La cintura**: un cinturón y una falda de jirones.
- **El torso**: un costillar abierto que brilla rosa por dentro. Las costillas son
  blancas y la columna, oscura con vértebras grises.
- **Dos brazos** largos de mármol, con hombreras oscuras, muñequeras y una banda rosa
  encendida, y mangas rotas. Las manos son dos cubos rosas que brillan.
- **La cabeza** tiene:
  - una capucha puntiaguda de azul noche;
  - una visera lila con una gema blanca;
  - dos cuernos lila y una media luna lila;
  - un gancho negro con remaches turquesa;
  - la boca de monstruo: una cortina de colmillos rosas y blancos arriba y dientes
    rojos abajo;
  - tres cebos: varillas dobladas que acaban en cubos rosas.
- Fuera del combate tiene una **forma de sirena**: sentada en una roca en el mar, con
  pelo azul, piel lila, arneses negros y un vestido largo. Es la de la canción «Dulce
  Azar».

## Las variantes

Las tres tienen el mismo cuerpo que Ofidia: la cola, el costillar, los dos brazos y la
boca. Cambian la forma de lo que enmarca la cabeza, el material y el neón.

- **De la Capucha (azul hielo).** Su capucha se abre en una capucha de cobra enorme, con
  dos ojos falsos. No lleva cebos ni mangas. Mármol de luna y cinturones de hierro.
- **De los Faroles (verde de almas).** Sus cebos son una corona de seis faroles con
  almas, con cadenas entre ellos, y lleva otro farol en cada mano. Mármol pizarra y
  latón.
- **Encadenada (carmesí).** Lleva:
  - grilletes oxidados con la cadena rota;
  - barrotes delante del pecho, que es una celda;
  - cadenas por la cola;
  - un bozal de hierro roto;
  - cuernos de carnero y jirones.

  Mármol negro con vetas rojas.

## Los bocetos

Salen de `materiales/generadores/ofidia_modelo.py` (`ofidia('O' | 'A' | 'B' | 'C')`) y
de `ofidia_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cuatro` y `materiales`.
