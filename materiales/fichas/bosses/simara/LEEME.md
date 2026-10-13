# Simara, la Sierpe de las Simas

A Juan le gustaron el monstruo y sus tres tipos (12-10-2026): «me gustaron este
monstruo y sus variables». Es la primera ficha de «una sola entidad en tres tipos»
y la primera con texturas limpias como las de Ofidia.

## Lo que comparten los tres tipos

Los tres usan el mismo modelo:

- una sierpe colosal que sale de una sima, de unos 20 bloques de alto;
- el cuerpo de tambores cuadrados ceñidos por cinturones con remaches, con una
  franja de escudos en el vientre;
- una cabeza de fauces enormes con dientes en peine y colmillos delante;
- lo nuevo: al fondo de la garganta gira un remolino que brilla.

## Los tres tipos

- **A · Abisal (neón cian).** Escamas en U con fotóforos, una aleta en cada tambor,
  un abanico de espinas en la nuca y otros dos a los lados, y dos barbillones con
  un bulbo de luz. Su remolino es de agua.
- **B · Volcánica (neón naranja).** Obsidiana con vetas de magma que serpentean,
  púas en el lomo, una corona de cuernos y dos látigos de lava. Su remolino es de
  magma.
- **C · Espectral (neón magenta).** Hueso lila con manchas de alma, cinturones de
  bronce, astas de hueso, una mortaja de jirones y dos cadenas con farolillos de
  almas. Su remolino es de almas. Es la que más se acerca a Ofidia.

## Las texturas limpias

Todas están dibujadas a 8 píxeles por bloque:

- manchas grandes con su borde;
- escamas, escudos en bandas y remaches de 2 x 2;
- vetas que siguen las curvas de nivel de un campo suave;
- degradados en escalones;
- sin ruido ni motas sueltas.

La lámina de materiales está en `simara_materiales.jpg`.

## Los bocetos

Salen de `materiales/generadores/sierpe_modelo.py` (`simara('A' | 'B' | 'C')`) y de
`sierpe_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `tres` y `materiales`.
