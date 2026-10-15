# El Blaze, rediseñado

El rediseño del **Blaze** de vanilla para que imponga, en tres tipos. Sigue siendo un Blaze: la
cabeza de bloque que flota, el fuego de debajo y lo que gira alrededor. Pero **las varas se
convierten en algo grande que flota** (espadas, cristales o lanzas), la cabeza lleva cuernos y el
cuerpo es una columna sólida que brilla.

Cómo se llegó:

1. Una primera vuelta de tres diseños nuevos (Torbellino, Coloso y Heraldo). Juan la rechazó: «no
   parecen blazes».
2. Una segunda vuelta con el Blaze de vanilla agrandado y con piezas nuevas. También la rechazó.
3. Juan mandó dos referencias:
   - un blaze rojo con espadas de fuego que flotan con la punta hacia abajo;
   - un blaze oscuro con tablillas de runas, los ojos y la gema magenta.
   De ahí salieron estos tres.
4. Después pidió unos cambios:
   - en el de las Espadas, quitar las varas de delante y ponerle una cara de monstruo;
   - en el segundo, cambiar las tablillas por cristales con punta arriba y abajo, casi de pie;
   - en el de las Lanzas, otra cara de monstruo;
   - en los cristales, una textura más natural.

Juan lo aprobó el 15-10-2026: «ahora sí me gustó, guárdalo en mobs».

## Lo que comparten los tres

- **El cuerpo:**
  - la cabeza de bloque con cuernos y la cara que arde;
  - el cuello, el pecho con los hombros, el vientre y la cola que se afina;
  - el fuego de debajo.
- **La construcción:** bloques con el píxel detallado, a un téxel por píxel del modelo, como en las
  referencias.
- **Lo que gira alrededor** deja un hueco delante de la cara.
- **El tamaño:** más de 5 bloques con lo que flota, cuando el de vanilla mide 1,8.

## Los tres tipos

| Tipo | Lo que gira | La cara | El fuego | Alto |
|---|---|---|---|---|
| A · el de las Espadas | seis espadas de fuego en corona, tres grandes y tres pequeñas | de monstruo: ceño en uve, ojos rasgados, colmillos y la quijada abierta con el fuego dentro | amarillo y rojo | 4,9 bloques |
| B · el de los Cristales | diez cristales de amatista con punta arriba y abajo, casi de pie: cinco grandes y cinco a la altura de los hombros | la de la referencia: cabeza alta, cuernos largos, la gema y los ojos morados, encendida por abajo | naranja y morado | 5,7 bloques |
| C · el de las Lanzas | seis lanzas de hierro de pie en corona, con anillos azules y la punta en hoja de fuego de alma | de monstruo: cuatro ojos, una cresta de hueso, dientes desiguales y la quijada abierta | de alma, azul | 5,2 bloques |

**El cristal del B:**
- cada tramo es una sola caja en rombo, con un filo hacia fuera;
- cada cara es lisa y de un solo morado frío;
- los filos son un tono más claros y las puntas son más claras y brillan un poco.

Con dos cajas cruzadas en estrella, o con vetas y motas, salía raro.

## Los bocetos

Salen de:

- `materiales/generadores/blaze_modelo.py` (`blaze('A')`, `'B'` y `'C'`);
- `blaze_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `tres` (con el Blaze de
  vanilla y un jugador) y `materiales`;
- `blaze_modelo_vanilla.py`, el Blaze de vanilla dibujado por nosotros, para comparar.

La escena es una fortaleza del Nether: suelo de ladrillo, pilares, cascadas de lava y, en el de las
Lanzas, el aire y los braseros de fuego de alma.

Todas las fotos van sin letras y con el borde blanco:

- `blaze_<tipo>_heroe.jpg`, `blaze_<tipo>_cabeza.jpg` y `blaze_<tipo>_cartel.jpg`, con los tipos
  espadas, cristales y lanzas;
- `blaze_tres_variantes.jpg` y `blaze_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `blaze_ficha.html`: se abre con el
navegador.
