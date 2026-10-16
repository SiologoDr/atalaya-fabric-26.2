# El Coco

Un mob que hace algo: te mete en su barriga y te va quitando vida poco a poco. Si hay alguien que lo mate, sales; si
estás solo, te mata. Juan lo pidió el 16-10-2026: «un mob que meta al jugador dentro de su panza, como atrapado, y le
quite vida lentamente; no tanto daño, pero si no hay una persona cerca esa cosa puede ser mortal; la única forma de
salvar a un jugador es matando al mob».

Es el Coco de la nana («duérmete niño, duérmete ya, que viene el Coco y te comerá»), pero nuestro. La leyenda no le da
forma; lo que cuenta es que el coco, la fruta, se llama así por él (los marineros vieron en sus tres agujeros la cara
del monstruo).

## Lo que comparten las variantes

- La misma pose, al acecho: encorvado, con la giba, una mano apoyada en el suelo y la otra alzada hacia ti.
- **La cabeza es una cáscara de coco**, con los tres agujeros: los dos ojos, hondos y con una brasa al fondo, y el de la
  nariz. Las aristas del coco bajan hasta el ceño en uve, y lleva pómulos.
- **Al abrir la boca se parte como un coco roto:** lo blanco del canto es la carne del coco, y esa carne son los
  dientes, partidos y de largos distintos, con la raya parda de la semilla.
- El cuerpo es pesado, con las piernas cortas y arqueadas y los brazos larguísimos. Las manos tienen cuatro dedos y
  garras de cuerno claro.
- La barriga es grande y colgante, con la luz en el centro y el ombligo. **No es translúcida** (Juan): cuando tiene a
  alguien dentro, encima del Coco sale el aviso (el icono de alerta, el nombre del jugador y «¡ha sido atrapado!»).
- Mide unos 2,9 bloques de alto.

## Las variantes

- **A, el Glotón:** cáscara parda con la cresta de estopa (la fibra del coco), cuerpo de carbón y ojos de brasa. Te
  traga y se queda quieto haciendo la digestión, defendiéndose a manotazos. **Es el que está en el juego.**
- **B, el del Saco:** cáscara de hueso pálido bajo una capucha de arpillera que acaba en un pico atado con una cuerda,
  capa de arpillera y la barriga cosida como un saco, con un remiendo. Ojos de azufre. Te traga y huye.
- **C, el de la Nana:** cáscara negra y alta, con agujeros que brillan (por ahí silba la nana) y la barba de estopa.
  Cuerpo de musgo y ojos lilas. Su nana adormece a los que la oyen y entonces te traga.

## Veredicto de Juan

- **Durante el diseño (16-10-2026):** «no quiero panza translúcida, sino que, si ha tragado a un jugador, arriba del
  mob salga el nombre de la persona y diga ¡ha sido atrapado!, y un icono de alerta».
- **Con la ficha:** «haz el diseño 1 con todas sus animaciones, huevo, etc.». Está en el juego el Glotón.

## En el juego (16-10-2026)

- Te ve y viene a por ti. A 2,5 bloques se para y da el segundo de aviso: alza los brazos y abre la cáscara. Si sigues
  a su alcance cuando acaba, te traga.
- **Dentro:**
  - no se te ve y no puedes salir con mayúsculas;
  - no puedes pegar, romper ni usar nada (ni comer ni una perla de ender);
  - cada 2 segundos te quita medio corazón, sin que cuente la armadura: con la vida llena, 40 segundos;
  - ves la pantalla roja y oscura con un latido, y debajo tus corazones bajando.
- **El aviso de encima** (el icono, tu nombre y «¡ha sido atrapado!») se ve a 48 bloques y a través de las paredes.
- **Lleno**, no se mueve: hace la digestión y da manotazos a quien se acerca.
- **Solo sales si alguien lo mata:** la barriga revienta y caes fuera.
- Tiene 20 corazones y por ahora solo sale con su huevo.
- **Las animaciones:**
  - anda pesado, bamboleándose, con los brazos apoyándose en el suelo y la barriga que bota;
  - quieto, respira, mira, abre la boca a ratos, le suenan las tripas y tamborilea con los dedos;
  - el aviso, el trago, la barriga llena con las patadas del de dentro (y las palmadas en la barriga) y el manotazo.

## De dónde sale

- **Los bocetos:** `materiales/generadores/coco_modelo.py` y `coco_escenas.py`, en una aldea al anochecer.
- **En el juego:**
  - `coco_juego.py`: la malla de Minecraft con las mismas cajas, la textura, lo que brilla, el huevo y el icono del aviso;
  - `coco_sonidos.py`: los sonidos.
  - El código está en el README, en «El Coco».
