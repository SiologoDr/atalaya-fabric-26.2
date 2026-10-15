# La Gorgona y sus hermanas

**La Gorgona.** Es una jefa con cuerpo de mujer y una cabellera de serpientes vivas. Sus
tres tipos son las tres hermanas del mito: Medusa, Esteno y Euríale. Es la primera jefa con
cuerpo de mujer (`jefa_modelo.py`). Se hizo a la vez que Vulpina, una kitsune, que se quitó de
las fichas por ser «muy fanservice»; de la Gorgona, Juan dijo: «sí tiene ese estilo que
buscamos».

Juan la pidió el 13-10-2026, mientras se hacía Vulpina: «por ejemplo podrías hacer una
medusa o algo así… y haz otro de paso». La dio por buena el mismo día. Primero dijo: «los
diseños están bien, solo que la cara es muy kawaii, no parece intimidante o imponente…
todo lo demás está good». Con la cara cambiada: «ok, guarda estas 2 y sus tipos en fichas
bosses».

## Cómo se llegó

1. **La primera** tenía la cara esculpida en bloques, como la Reina Amuna de Mitologías
   RPG («todo no debe ser texturas»), y el traje griego en piezas. Esteno tenía cola de
   serpiente. Juan: «el diseño está decente, pero la cara sigue siendo el problema, y veo
   que la rodilla está rara, los brazos igual».
2. **El muestrario.** Juan eligió pieza a pieza (`catalogo_dama.py`) y se quedaron:
   - la cara C3;
   - los brazos B2, B3, B5 y B6;
   - las piernas L2, L3, L4 y L5;
   - el pecho P1.

   Y avisó: «la anatomía que me mostraste es como una niña; debe verse como una mujer
   adulta».
3. **La segunda** se hizo con esas piezas y con cuerpo de mujer adulta. Esteno dejó la
   cola de serpiente por piernas de mujer y pasó a ser la arquera. Gustó todo menos la
   cara: «muy kawaii».
4. **La tercera**, la de esta ficha, lleva la C3 con mirada de jefa.

## Lo que comparten las tres hermanas

- **El cuerpo de mujer adulta**, todo de cajas, como un modelo de Blockbench:
  - mide seis cabezas y media;
  - lleva el cuello largo, la cintura estrecha, las caderas con la grupa y las piernas de
    la mitad de la altura;
  - codos y rodillas doblan por el canto de fuera;
  - mide unos 30 bloques hasta la coronilla y unos 35 con las serpientes.
- **La cara C3 con mirada de jefa.** Lleva:
  - el párpado de arriba en ángulo, que entrecierra la mirada;
  - la pupila rasgada de serpiente y el iris que brilla;
  - las cejas en ceño y la sombra del flequillo;
  - un trazo de pintura de guerra bajo el rabillo, del color de sus serpientes;
  - la boca en una línea fina con media sonrisa;
  - la cabeza un poco inclinada, mirando desde arriba.
- **La cabellera**: trece serpientes de bloques.
  - Cinco suben y miran hacia delante, cuatro salen por los lados y cuatro caen por la
    espalda.
  - Cada una tiene el cráneo, el hocico, los ojos encendidos, la boca abierta y dos
    colmillos.
- **Las joyas**: la diadema de oro con su gema encendida y los pendientes de tres cuentas
  con la gota encendida.
- **El quitón de un solo hombro**:
  - el pecho P1 con su ribete de oro;
  - la tira de grecas que sube por el hombro;
  - el cinturón de grecas bajo el pecho y el de oro en la cintura.

## Las tres hermanas

Cambian la silueta, la pose y los brazos y las piernas del muestrario.

- **A · Medusa (esmeralda y oro; ojos verdes).**
  - Lleva el quitón largo esmeralda, abierto por delante, y por la raja asoma la pierna
    con las sandalias de tiras de oro.
  - Tiene una mano en alto, abierta: la que petrifica.
  - Brazos de bloque con brazaletes de oro (B2) y piernas estilizadas (L5).
  - Tiene la cabellera más grande y la piel de porcelana.
- **B · Esteno (cobre, carmín y bronce; ojos ámbar).** La arquera.
  - Lleva la armadura de bronce en los brazos (B5) y grebas de bronce (L3).
  - Viste la falda corta con el faldón de tiras de cuero.
  - Sostiene el arco recurvado en una mano y tiene la otra en alto.
- **C · Euríale (negra, oro y carmín; ojos rojos).** La alada.
  - Abre detrás de los hombros las alas de plumas negras, con el borde carmín y el raquis
    de oro.
  - Lleva garras de escamas (B6) y piernas de rodilla limpia con sandalias (L2).
  - Tiene la piel morena y viste un quitón corto.
  - Es la más ancha: 52 bloques de ala a ala.

## Los bocetos

Salen de:

- `materiales/generadores/gorgona_modelo.py` (`gorgona('A' | 'B' | 'C')`);
- `jefa_modelo.py`, con el cuerpo, la cara y las piezas del muestrario;
- `gorgona_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `cartel_X`, `cara_X`,
  `tres` y `materiales`.

Todas las fotos van sin letras y con el borde blanco. Los archivos se llaman
`gorgona_<hermana>_<vista>.jpg`, con la hermana en `medusa`, `esteno` o `euriale`.

## La ficha

La ficha completa, con las fotos y el veredicto de Juan, es `gorgona_ficha.html`: se abre con el navegador. Desde el 14-10-2026 las fichas no se publican (Juan borró los artifacts: «no quiero que salgan»); van en HTML dentro de su carpeta.
