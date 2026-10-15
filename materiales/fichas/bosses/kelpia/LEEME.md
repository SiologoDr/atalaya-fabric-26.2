# Kelpia

**Kelpia, la Acechadora del Lago.** Es un monstruo del lago inventado. Va cargado de hombros, con
una joroba de hueso de la que le caen las algas como una cortina, y espera en la orilla con la
cabeza baja y las fauces abiertas que arden en ámbar.

Salió del kelpie de las leyendas escocesas, el caballo de agua que arrastra a la gente al fondo del
lago. Del caballo solo le quedan rastros: la crin de algas y las pezuñas.

- **La primera ficha** (14-10-2026) tenía tres caballos de agua: la Kelpia (encabritada), el
  Hipocampo (con cola de pez) y la Acechadora (de pie, con la cabeza baja). Juan dijo: «el tipo C
  me gusta su diseño pero no en su anatomía, hubiera sido mejor que no hubiera sido un caballo
  sino algo creado nuevo… está bien usar referencias pero no hacerlas iguales».
- **La Acechadora se rehízo** con un cuerpo inventado y se quedó con su diseño. Juan la aprobó:
  «ahora sí me gustó, excelente trabajo, este sí se acercó a lo que busco». Los dos caballos no se
  guardan.

## Cómo es

- **La cabeza manda.** Es ancha, alta y corta.
  - Tiene dos cejas de hueso en pico, de mal genio, y unos nudos de hueso por el hocico y la
    coronilla.
  - Tiene cuatro ojos encendidos, dos por lado: uno grande arriba y uno pequeño en el hocico.
  - Las fauces se abren desde muy atrás, con el paladar encendido en escalones, los dientes en
    hoja, dos pares de colmillos arriba y uno abajo, el suelo de la boca encendido y el núcleo al
    fondo.
  - La quijada es honda, con dos alas de hueso a los lados, y de las comisuras le cuelgan dos
    barbos de alga ondulados.
- **La joroba** de los hombros lleva una cresta de hueso. De sus dos lados le caen las algas hasta
  casi el suelo, como una cortina, y por delante le tapan el cuello y le enmarcan la cabeza. Las
  algas tienen el nervio encendido y vejigas que brillan.
- **Los brazos son largos**, uno apoyado y otro alzado. **Las patas de atrás son cortas**, y el lomo
  cae hacia la cola. Brazos y patas acaban en pezuñas partidas en tres garras de cuerno.
- **La cola** es un muñón del que salen las algas, que se arrastran por el suelo.
- **La piel** es parda y mojada, con hilos de agua que le chorrean. Solo arden las fauces, los
  ojos, el nervio de las algas y las vejigas.
- **Todo de cajas**, con texturas limpias. Va a PPB 4 y ESCALA 0,62. Mide 22 bloques de alto y 38
  de largo.

## Los bocetos

Salen de:

- `materiales/generadores/kelpia_modelo.py`:
  - `kelpia('C')` llama a `acechadora()`, que es esta;
  - los dos caballos descartados (la Kelpia y el Hipocampo) siguen en `caballo()`;
- `jefa_modelo.py`, del que toma los tubos de bloques;
- `kelpia_escenas.py`, con las escenas `heroe_C`, `cabeza_C`, `cartel_C`, `escala_C` (con un
  jugador) y `materiales_C`. La escena es la orilla de un lago de noche: el agua negra con las
  ondas, los juncos, las piedras con musgo y, al otro lado, los montes en gradas.

Todas las fotos van sin letras y con el borde blanco: `kelpia_heroe.jpg`, `kelpia_cabeza.jpg`,
`kelpia_cartel.jpg`, `kelpia_escala.jpg` y `kelpia_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `kelpia_ficha.html`: se abre con el
navegador.
