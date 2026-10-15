# Murena

**Murena, la Morena del Arrecife.** Es una morena cinta colosal, larga y fina, que sale de su
guarida de roca y se alza en una ese muy alta hacia quien se acerca. Tiene las fauces abiertas que
arden por dentro. Es azul noche y limón.

Salió de una idea de Juan, al quitar a Escila de las fichas: «sus morenas, puedes hacer un boss tipo
morena».

- **La primera ficha** tenía tres morenas (la Dragona, la Cinta y la Gigante). Juan eligió la Cinta:
  «me gusta la opción B, de esa hagamos 3 tipos de diseños».
- **La segunda** sacó tres tipos de ella (la Cinta, la Trenza y la del Velo). Juan se quedó con la
  primera: «en Murena solo deja la opción 1 y quita la mini serpiente de su boca, haz eso y solo
  guarda esa opción».

La «mini serpiente» era la segunda mandíbula de las morenas, que le salía de la garganta. Se quitó, y
al fondo de la garganta quedó el núcleo, como en los demás jefes.

## Cómo es

- **La cabeza manda.** Es alta y larga, con la nuca en joroba.
  - Las fauces van abiertas, con el paladar encendido en escalones, los dientes dibujados en hoja
    por los bordes, dos colmillos en el centro del paladar y el núcleo al fondo.
  - Los ojos son pequeños y encendidos, arriba y cerca del hocico, y detrás de la boca está el
    agujero de la agalla.
  - Las narices se abren como hojas en la punta del hocico.
- **El cuerpo** es largo, fino y aplastado de lado, sin escamas, azul noche, con una veta limón que
  brilla a lo largo. Se alza en una ese muy alta.
- **La aleta del lomo** le corre de la nuca a la cueva, alta, en bandas, con el canto encendido.
- **La guarida** es parte del jefe: una roca con la boca de la cueva por delante, percebes y coral
  rojo encima.
- **Todo de cajas**, con texturas limpias. Va a PPB 4 y ESCALA 0,6. Mide 35 bloques de alto y 31 de
  largo.

## Los bocetos

Salen de:

- `materiales/generadores/murena_modelo.py` (`murena('A')`);
  - las opciones descartadas siguen como opciones de la cabeza: el gancho y las narices en tubo de la
    Dragona, las quijadas de la Gigante y la segunda mandíbula (`segunda=True`);
- `jefa_modelo.py`, del que toma los tubos de bloques;
- `murena_escenas.py`, con las escenas `heroe_A`, `cabeza_A`, `cartel_A`, `escala` (con un jugador) y
  `materiales`. La escena es un arrecife de noche, con rocas y columnas de basalto.

Todas las fotos van sin letras y con el borde blanco: `murena_heroe.jpg`, `murena_cabeza.jpg`,
`murena_cartel.jpg`, `murena_escala.jpg` y `murena_materiales.jpg`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `murena_ficha.html`: se abre con el
navegador. Desde el 14-10-2026 las fichas no se publican; van en HTML dentro de su carpeta.
