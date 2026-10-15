# Zotzara

**Zotzara, la Murciélaga de Xibalbá.** Sale de Camazotz, el murciélago de la muerte de los mayas,
el que cortaba cabezas en la casa de los murciélagos del inframundo. Es una figura flaca y
encorvada, agachada, con las alas abiertas del todo y la cabeza enmarcada por orejas enormes y
pedernal.

- **La primera ficha** (14-10-2026) tenía tres poses: la Encapuchada (con las alas cerradas como una
  capa), la Abierta (con las alas abiertas) y la Colgada (boca abajo de un árbol muerto).
- **Juan la aprobó con una condición:** «guarda Zotzara, pero que todos tengan la misma pose;
  recuerda que esto de los tipos es de un solo boss, una misma pose pero diferentes».

Los tres tipos van con la pose de la Abierta, y cambian las orejas, la nariz y el borde de las alas.

## Lo que comparten los tres

- **Del murciélago le quedan rastros:** las alas de membrana, las orejas enormes, la hoja de la
  nariz y la costumbre de colgarse boca abajo.
- **La pose:** agachada, con las alas abiertas del todo, chillando.
- **La cabeza** es ancha y corta, con el morro chato y vuelto hacia arriba, los ojos pequeños y
  encendidos y una ceja encima.
  - La enmarcan las orejas y la hoja de la nariz, de pedernal tallado en lascas, como el cuchillo
    de los sacrificios.
  - Las fauces se abren desde muy atrás, con el paladar encendido en escalones, los dientes en
    hoja, dos colmillos largos arriba y dos abajo, el suelo de la boca encendido y el núcleo al
    fondo.
- **Las alas:** cada ala es un brazo con el pulgar en garra y cuatro dedos largos. La membrana es
  oscura y en bandas, con el borde libre encendido, y del último dedo baja hasta el pie.
- **El cuerpo** es flaco y encorvado, con el pecho hondo, un collar de pelo tieso y dos patas que
  acaban en tres garras de cuerno.
- **Solo arden** las fauces, los ojos y el borde de las alas.
- **Todo de cajas**, con texturas limpias. Va a PPB 4, ESCALA 0,62 y la cabeza a 1,45.

## Los tres tipos

| Tipo | Orejas | Nariz | Alas | Luz | Medidas |
|---|---|---|---|---|---|
| A · la Pedernal | dos, altas | un cuchillo de pedernal | en festones lisos | jade | 28 de alto · 41 de ancho |
| B · la Desgarrada | con una muesca mordida | dos cuchillos en V | rotas, con desgarros y el borde mellado | sangre | 28 de alto · 41 de ancho |
| C · la Coronada | cuatro, en corona | herradura de cuerno y un cuchillo corto | en festones, con un garfio en cada dedo | oro | 28 de alto · 45 de ancho |

## Los bocetos

Salen de:

- `materiales/generadores/zotzara_modelo.py` (`zotzara('A')`, `'B'` y `'C'`);
  - las poses descartadas siguen como opciones: `pose='capa'` (la Encapuchada) y `pose='colgada'`
    (la Colgada, con su árbol muerto);
- `kelpia_modelo.py` y `jefa_modelo.py`, de los que toma los pintores comunes y los tubos de
  bloques;
- `zotzara_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `tres` (con un
  jugador) y `materiales`. La escena es la entrada de Xibalbá de noche: piedra oscura y agrietada,
  estalagmitas, rocas y riscos al fondo.

Todas las fotos van sin letras y con el borde blanco: `zotzara_<tipo>_heroe.jpg`,
`zotzara_<tipo>_cabeza.jpg` y `zotzara_<tipo>_cartel.jpg` (pedernal, desgarrada y coronada), más
`zotzara_tres_variantes.jpg` y `zotzara_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `zotzara_ficha.html`: se abre con el
navegador.
