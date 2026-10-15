# El Minotauro y sus formas

**El Minotauro.** Es un coloso con cabeza de toro, del mismo mito griego que la Gorgona. Sus
tres formas son Asterión, el Calcotauro y el Bucentauro. Se hizo después de quitar a Vulpina
por fanservice, con el estilo de la Gorgona: el mito y el monstruo bien a la vista.

Juan lo pidió el 13-10-2026: «ahora sí creamos al siguiente boss con sus subtipos». El
14-10 lo dio por bueno: «ahora sí guarda al minotauro y sus 3 versiones en bosses».

## Cómo se llegó

1. **La primera** tenía tres cuerpos distintos. Solo el Calcotauro iba encorvado y macizo.
   Juan: «el minotauro debe ser como el tipo B… los otros no parecen minotauros, por ahí son
   medio delgados».
2. **La segunda**, la de esta ficha, da a las tres el cuerpo del Calcotauro. La lección: un
   minotauro se lee por **la masa encorvada y la giba**, no solo por la cabeza de toro.

## Lo que comparten las tres formas

- **La cabeza manda**: es de toro, agrandada ×1,45, y mira a cámara.
  - Las fauces abiertas arden por dentro con un solo neón, en escalones.
  - Los dientes van dibujados en hojas. Arriba lleva dos colmillos y abajo, dos defensas
    que suben. Al fondo de la garganta está el núcleo.
  - Los ojos encendidos van bajo un ceño de hueso en ángulo.
  - La nariz es lisa, con un pliegue y el aro de bronce en el tabique. Los ollares pintados
    se leían como ojos y se quitaron.
  - Los cuernos tienen anillos y enmarcan la cabeza.
- **El cuerpo macizo y encorvado**:
  - la cabeza sale por delante de los hombros, no por encima;
  - la giba de pelo sube alta detrás de la nuca, como la de un toro;
  - el pecho y los hombros son el doble de anchos, con los pectorales y el vientre marcados;
  - los brazos son enormes, con el deltoide de bloque, el pelo en el antebrazo y los puños
    de bloque;
  - las piernas son cortas y gruesas, con el pelo largo sobre las pezuñas hendidas;
  - la cola acaba en un penacho;
  - codos y rodillas doblan por el canto, como el cuerpo de la Gorgona.
- **Todo de cajas**, con texturas limpias: la piel con manchas grandes, el cuero, el metal
  con remaches de 2×2. Va a PPB 4 y ESCALA 0,58.

## Las tres formas

Cambian la silueta por el arma, los cuernos y la postura.

- **A · Asterión, el del Laberinto (ámbar).**
  - Lleva el hacha de doble filo (la lábrys) en alto y, en la otra muñeca, el grillete con
    la cadena rota.
  - Tiene los cuernos de marfil hacia delante.
  - Viste el faldón de tiras de cuero con las puntas de bronce y el cinturón con hebilla.
  - Es la más alta: 46 bloques hasta el filo del hacha y 25 de ancho.
- **B · el Calcotauro (turquesa).** El toro de bronce que echa fuego.
  - Va encorvado para embestir, con la cabeza baja.
  - Lleva placas de bronce en la giba, el pecho, el vientre, los hombros, los antebrazos y
    las rodillas. Solo arde la junta de abajo de cada placa: encenderlas enteras parecía
    «Tron».
  - Tiene los cuernos muy abiertos, con el casquillo de bronce.
  - Es la más ancha: 29 bloques de alto y 35 de cuerno a cuerno.
- **C · el Bucentauro (carmesí).**
  - Es el torso del minotauro, también encorvado y con su giba, sobre un cuerpo de toro de
    cuatro patas.
  - Lleva el tridente del toro de Creta, el que salió del mar de Poseidón. Va apartado
    para no tapar la cara.
  - Tiene los cuernos en lira, negros con la punta carmesí.
  - Es la más larga: 40 bloques de alto con el tridente y 34 de largo.

## Los bocetos

Salen de:

- `materiales/generadores/minotauro_modelo.py` (`minotauro('A' | 'B' | 'C')`);
- `jefa_modelo.py`, del que toma los tubos de bloques y las manos;
- `minotauro_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `tres` y
  `materiales`. La escena es el claro de un laberinto en ruinas, con columnas griegas rotas.

Todas las fotos van sin letras y con el borde blanco. Los archivos se llaman
`minotauro_<forma>_<vista>.jpg`, con la forma en `asterion`, `calcotauro` o `bucentauro`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `minotauro_ficha.html`: se abre con el navegador. Desde el 14-10-2026 las fichas no se publican (Juan borró los artifacts: «no quiero que salgan»); van en HTML dentro de su carpeta.
