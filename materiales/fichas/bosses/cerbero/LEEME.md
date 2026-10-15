# Cerbero y sus formas

**Cerbero.** Es el perro de varias cabezas que guarda la puerta del Hades, del mismo mito
griego que la Gorgona y el Minotauro. Sus tres formas son el Guardián, Ortro y el
Encadenado. Es el primer jefe de las fichas con cuerpo de perro de presa.

Juan lo pidió el 14-10-2026, al guardar el Minotauro: «créame otro boss». El mismo día lo
dio por bueno, aunque avisó de que se parece algo a otros jefes: «lo mismo con cerbero, pero
este sí déjalo en fichas en bosses porque me gustó su diseño y sus tipos». La Tarasca, que se
hizo a la vez, se descartó: «no me convence, es que tenemos bosses que se parecen».

## Lo que comparten las tres formas

- **Las cabezas mandan**: son de perro de presa, agrandadas ×1,4, y miran a cámara.
  - Las fauces abiertas arden por dentro con un solo neón, en escalones.
  - Los dientes van dibujados en hojas. Lleva dos colmillos arriba y dos abajo, y al fondo
    de la garganta está el núcleo.
  - Los ojos encendidos van bajo un ceño en ángulo.
  - El cráneo lleva la coronilla en escalón.
  - Las orejas son en punta, en tres escalones, echadas hacia atrás.
  - El hocico es largo, con el caballete y la trufa negra.
  - Lleva la gola de pelo en las mejillas y la barba bajo la mandíbula.
- **Lo que enmarca cada cabeza**: las orejas, la gola y el collar. El collar es un aro de
  metal con remaches y ocho pinchos.
- **Los cuellos** llevan una crin de mechones por arriba.
- **El cuerpo de perro de presa**, oscuro y enjuto:
  - el pecho es hondo, con la quilla y la pechera de pelo, y la cintura va recogida;
  - los hombros y la grupa son de músculo, con una cresta de pelo por el lomo;
  - las cuatro patas son largas y pisan de puntillas, con cuatro dedos y sus uñas.
- **La cola es una serpiente** de escamas en U, con la boca encendida como las cabezas. Es
  lo que hace que no sea un perro agrandado.
- **Todo de cajas**, con texturas limpias: el pelo con manchas grandes, la crin en hebras,
  las escamas en U y el metal con remaches de 2×2. Va a PPB 4 y ESCALA 0,72.

## Las tres formas

Cambian la silueta: ancho con tres cabezas, largo y bajo con dos, o sentado y alto con las
cadenas.

- **A · Cerbero, el Guardián (amarillo azufre).**
  - Está plantado sobre las cuatro patas, con las tres cabezas abiertas en abanico.
  - Por el lomo le sale la crin de cinco serpientes, abiertas a los lados.
  - La cola-serpiente se arquea en alto, hacia un lado.
  - Los collares son de bronce.
  - Es la más ancha: 31 bloques de alto y 37 de cabeza a cabeza.
- **B · Ortro, el Perro de Gerión (fucsia).** El hermano de dos cabezas.
  - Es más largo y flaco, y está agazapado para saltar: el pecho bajo y la grupa alta.
  - Tiene las orejas más largas y una cresta de pelo alta.
  - La cola-serpiente se alza a un lado.
  - Los collares son de hierro.
  - Es la más larga y la más baja: 49 bloques de largo y 23 de alto.
- **C · Cerbero Encadenado (azul de alma).** El que sacó Heracles del Hades.
  - Está sentado sobre los cuartos traseros, muy alto, con las tres cabezas mirando hacia
    abajo.
  - De los collares le cuelgan las cadenas rotas hasta el suelo, y otras dos unen los
    collares.
  - La cola-serpiente se enrosca en el suelo y alza la cabeza delante.
  - Es la más alta: 34 bloques sentado, con las bocas a 22 del suelo.

## Los bocetos

Salen de:

- `materiales/generadores/cerbero_modelo.py` (`cerbero('A' | 'B' | 'C')`);
- `jefa_modelo.py`, del que toma los tubos de bloques;
- `cerbero_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `tres` y
  `materiales`. La escena es la orilla del Estigio, con rocas y columnas de basalto.

Todas las fotos van sin letras y con el borde blanco. Los archivos se llaman
`cerbero_<forma>_<vista>.jpg`, con la forma en `guardian`, `ortro` o `encadenado`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `cerbero_ficha.html`: se abre con el navegador. Desde el 14-10-2026 las fichas no se publican (Juan borró los artifacts: «no quiero que salgan»); van en HTML dentro de su carpeta.
