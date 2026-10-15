# El Trasgo

El mob que **se te aferra al cuerpo**. Es el trasgo de las leyendas de Asturias y Cantabria, pero
nuestro:

- un duendecillo flaco y encorvado, de cabeza grande;
- en la cabeza, **el gorro**, las orejas largas en punta, la nariz ganchuda, **los ojos rasgados
  que brillan** y una sonrisa llena de dientes;
- **brazos larguísimos con garras**;
- como en la leyenda, un agujero en la palma de la mano izquierda.

Te salta encima y no te suelta.

Es el segundo de los «mobs que hacen algo». Juan pidió estos mobs después de mirar los de Dedsafío 3
y 4. El primero, el Izador (un globo vivo con una jaula), no gustó: «se ve raro y su cara no me
gustó; la mecánica es buena». Por eso este es un bicho creíble, con una cara que se lee de lejos.

Juan lo aprobó a la primera, el 15-10-2026: «guárdalos en mobs».

## Lo que hace

1. **Acecha** agazapado en las minas y las cuevas, con los ojos brillando en la oscuridad.
2. **Te salta encima** desde unos bloques de distancia.
3. **Se te aferra**, y lo que te hace depende del tipo.

Cómo quitártelo:

- golpearlo rápido;
- que un compañero le pegue;
- tirarte al agua.

La luz fuerte de una antorcha en la mano lo espanta antes de que salte.

## Lo que comparten los tres

- **La pose de acecho:** agazapado, con una mano en el suelo y la otra en alto, con las garras
  abiertas.
- **La cabeza:**
  - el cráneo, el ceño, los pómulos y la nariz ganchuda;
  - los ojos rasgados con la pupila de raja;
  - la boca oscura con una raja de neón al fondo y los dientes en hoja;
  - las orejas en hoja;
  - el gorro de lana con el borde vuelto.
- **Las manos:** tres dedos largos con garras curvas.
- **El tamaño:** agazapado mide 1,5 bloques, y 2 con la garra en alto.
- **La construcción:** cajas a un téxel por píxel, en píxeles del jugador (16 por bloque).

## Los tres tipos

| Tipo | Cómo es | Dónde se agarra y qué te hace |
|---|---|---|
| A · el Colgón | verde grisáceo, con gorro rojo, la cola larga de gancho, púas en la nuca y ojos ámbar | se te cuelga de la espalda, abrazado al cuello: pesa (no corres ni saltas) y te muerde |
| B · el Jinete | gris pálido, de cueva, con gorro rojo, dos cuernecillos, los dedos muy largos y ojos azul hielo | se te sube a los hombros, te tapa los ojos con las manos y te lleva caminando hacia la lava o el barranco |
| C · el Ladrón | rojizo, con gorro negro, las orejas enormes, el saco del botín con oro y ojos verdes | se te cuelga del brazo, te arranca lo que llevas en la mano y huye |

## Los bocetos

Salen de:

- `materiales/generadores/trasgo_modelo.py`:
  - `trasgo('A', postura)`, con `'B'` y `'C'` para los otros tipos;
  - el modelo está articulado: la postura da la pelvis, el giro del cuerpo y de la cabeza, y los
    codos, las manos, las rodillas y los pies;
  - las posturas son `'acecho'`, `postura_espalda()`, `postura_hombros()` y
    `postura_brazo(mano)`.
- `trasgo_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `accion_X` (agarrado a un jugador),
  `tres` (con un jugador) y `materiales`.

La escena es una mina abandonada: la galería de piedra, las vigas de madera, los raíles, los faroles
y alguna veta de oro.

Todas las fotos van sin letras y con el borde blanco:

- `trasgo_<tipo>_heroe.jpg`, `trasgo_<tipo>_cabeza.jpg` y `trasgo_<tipo>_accion.jpg`, con los
  tipos colgon, jinete y ladron;
- `trasgo_tres_variantes.jpg` y `trasgo_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `trasgo_ficha.html`: se abre con el
navegador.
