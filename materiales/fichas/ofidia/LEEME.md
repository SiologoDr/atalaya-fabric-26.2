# Ofidia y sus variantes

Ofidia es la sirena-sierpe de la tercera dungeon de **Dedsafio 4**, con diseño de
Eufonia Studio. Su cartel oficial está en
https://x.com/dedsafio/status/2109039127597560179.

Juan pidió el 12-10-2026 recrearla igual y hacerle variantes propias, «para no copiarla
como tal». Hicieron falta cinco versiones:

1. La primera no se parecía: «fíjate bien cómo es Ofidia… date tu tiempo, investiga
   más».
2. La segunda tenía brazos y no estaba bien la boca: «no son manos o brazos, son alas lo
   que tiene, aparte su boca es como triangular, revisa bien su portada».
3. La tercera seguía teniendo la mandíbula rara y unas alas que no eran como las suyas:
   «la mandíbula sigue rara y las alas no son así como Ofidia… tú puedes».
4. La cuarta se hizo comparando cada render con la portada y con los fotogramas del
   directo, lado a lado y desde el mismo ángulo. Aun así: «su mandíbula está rara; tanto su
   mandíbula superior e inferior deben ser medio rectángulo triangular, y sus alas deben
   ser como las de un murciélago».
5. Esta quinta hace las dos mandíbulas como cuñas y las alas de murciélago, y se comprobó
   de frente, de tres cuartos y de lado.

**La original es solo para estudiarla; no va al mod.** Las candidatas son las tres
variantes. A Juan le gustó la Encadenada.

## Cómo es Ofidia de verdad

Las fuentes son cuatro:

- la portada oficial, la más fiel;
- el retrato de su barra de jefe;
- la presentación del directo del 10-10-2026 (día 18 de farfadox en Kick), sobre todo
  el plano de frente;
- un vuelo en la pelea del mismo directo (a las 5:22:13), con las alas abiertas.

En la forma de monstruo se ve:

- **La cola**: una sierpe de tambores de mármol azul con cinturones granates con
  remaches. Se enrosca en el suelo y se alza.
- **La cintura**: un cinturón con remaches.
- **El torso**: un costillar abierto que brilla rosa por dentro. Las costillas son
  blancas y la columna, oscura con vértebras grises.
- **Dos alas de murciélago, no brazos**:
  - el brazo, con el codo hacia atrás y la muñeca hacia delante;
  - un cubo rosa encendido en la muñeca, que hace de pulgar;
  - cuatro dedos largos que salen de la muñeca en abanico;
  - la membrana azul noche tendida entre los dedos, con el borde en arcos;
  - del último dedo, la membrana baja hasta el costado.
- **La cabeza** tiene:
  - una capucha puntiaguda de azul noche;
  - una visera lila con una gema blanca;
  - dos cuernos lila, una media luna lila y una espina rosa;
  - un gancho negro con remaches turquesa;
  - un tallo negro con muescas en la coronilla.
- **La boca es de dos cuñas**: cada mandíbula es medio rectángulo partido en diagonal.
  - La de arriba lleva encima la visera lila en rampa, con la gema blanca. Delante tiene
    una banda oscura con remaches turquesa, y debajo, el paladar rosa, del que cuelgan los
    colmillos planos rosas y blancos, con la punta en escalón.
  - La de abajo es la cuña al revés: llana y rosa por dentro, en rampa por fuera. Se
    estrecha hasta la barbilla y lleva dientes rojos en escalón por los bordes.
  - Abierta, de lado se ven las dos cuñas, y de frente, un triángulo rosa justo debajo de
    la visera.
- **Los tres cebos**: el de arriba sale del tallo negro, sube y se dobla hacia atrás, y
  los de los lados salen de la capucha y se doblan hacia atrás y abajo. Acaban en cubos
  rosas encendidos.
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
  de cada muñeca. Mármol pizarra y latón.
- **Encadenada (carmesí).** Lleva:
  - grilletes oxidados en los brazos de las alas, con la cadena rota;
  - barrotes delante del pecho, que es una celda;
  - cadenas por la cola, y dos cadenas rotas en vez de cebos;
  - un bozal de hierro roto;
  - cuernos de carnero y jirones.

  Mármol negro con vetas rojas.

## Los bocetos

Salen de `materiales/generadores/ofidia_modelo.py` (`ofidia('O' | 'A' | 'B' | 'C')`) y
de `ofidia_escenas.py`, con las escenas `heroe_X`, `cabeza_X` (de tres cuartos y desde
abajo, como la portada), `cuatro` y `materiales`. Para comparar con las referencias hay
tres escenas más: `cartel_X` (el ángulo de la portada), `frente_X` (el del plano de
frente del directo) y `lado_X` (de perfil, para ver las dos cuñas).
