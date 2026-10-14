# Vulpina y sus tipos

**Vulpina, la Dama de las Nueve Colas.** Es una kitsune: una dama zorra con nueve
colas y un fuego en la punta de cada una. Con la Gorgona, es una de las dos primeras
jefas con cuerpo de mujer, y las dos comparten el cuerpo y la cara (`jefa_modelo.py`).

Juan la dio por buena el 13-10-2026. Primero dijo: «los diseños están bien, solo que
la cara es muy kawaii, no parece intimidante o imponente… todo lo demás está good». Con
la cara cambiada: «ok, guarda estas 2 y sus tipos en fichas bosses».

## Cómo se llegó

1. **La primera** era una dama elegante con la cara pintada en una caja grande. Juan:
   «la cara está rara… y esta ya se pasa de femenina, es el típico doncella con
   colas». Lo femenino tenía que estar en la anatomía, y encima, lo que la hace jefa.
2. **La segunda** era una zorra demonio con patas de zorra. Tenía la cara esculpida en
   bloques, como la Reina Amuna de Mitologías RPG, porque Juan pidió que «todo no debe
   ser texturas». No gustó: «la cara sigue siendo el problema, y veo que la rodilla está
   rara, los brazos igual».
3. **El muestrario.** Juan eligió pieza a pieza entre 8 caras, 6 brazos, 6 piernas y
   6 pechos (`catalogo_dama.py`). Se quedaron:
   - la cara C3;
   - los brazos B2, B3, B5 y B6;
   - las piernas L2, L3, L4 y L5;
   - el pecho P1.

   Y avisó de que el muestrario se veía infantil: «la anatomía que me mostraste es como
   una niña; debe verse como una mujer adulta».
4. **La tercera** se hizo con esas piezas y con cuerpo de mujer adulta. Gustó todo menos
   la cara: «muy kawaii».
5. **La cuarta**, la de esta ficha, lleva la C3 con mirada de jefa.

## Lo que comparten los tres tipos

- **El cuerpo de mujer adulta**, todo de cajas, como un modelo de Blockbench:
  - mide 51,5 píxeles de piel con una cabeza de 8, es decir, seis cabezas y media (el
    muestrario tenía cuatro y por eso parecía una niña);
  - lleva el cuello largo, los hombros, la cintura estrecha, las caderas con la grupa,
    los muslos que se afinan, el gemelo y el tobillo fino;
  - las piernas son la mitad de la altura;
  - codos y rodillas doblan por el canto de fuera, como un cartón doblado;
  - mide unos 30 bloques hasta la coronilla.
- **La cara C3 con mirada de jefa.** Tiene el mismo tamaño y el mismo píxel que la C3
  del muestrario, pero:
  - el párpado de arriba cae en ángulo hacia la nariz y entrecierra la mirada;
  - la pupila es rasgada y el iris brilla;
  - las cejas, a la vista, van en ceño;
  - la sombra del flequillo cae sobre los ojos;
  - lleva un trazo rojo de pintura de guerra bajo el rabillo;
  - no lleva colorete;
  - la boca es una línea fina con media sonrisa;
  - la cabeza mira un poco hacia abajo.
- **Lo de zorra, también de bloques**:
  - las orejas grandes en escalones, con la punta del color de la cola;
  - la melena hasta la cintura;
  - la máscara de zorro de laca a un lado de la cabeza y las horquillas de oro al otro;
  - el corpiño de kimono con el pecho P1 y el cuello rojo cruzado en V;
  - el obi, con su lazo detrás y el cordón con la gema;
  - la soga sagrada con dos papeles en zigzag;
  - la falda con el bajo rasgado;
  - las nueve colas, tubos de bloques de ocho lados con el fuego en la punta.

## Los tres tipos

Cambian la forma de las colas, la pose y los brazos y las piernas del muestrario.

- **A · del Abanico (blanca, roja y oro; ojos ámbar).**
  - Abre las nueve colas en abanico detrás de ella, como un sol.
  - Alza los brazos con los guantes largos rojos (B3) y sostiene un fuego sobre cada
    mano.
  - Lleva medias negras con liga y tacón (L4).
  - Es la más ancha: 35 bloques de cola a cola.
- **B · de la Llama (negra y carmín; ojos rojos).**
  - Alza las colas juntas como una llama que se riza en la punta.
  - Tiene garras de escamas con gorguera de pelo (B6): una en alto con un fuego grande
    y la otra abajo, abierta.
  - Lleva botas altas de cuero con hebillas de oro (L3).
  - Es la más alta: 41 bloques hasta el fuego.
- **C · del Manto (plata y rosa; ojos rosas).**
  - Dos colas le rodean los hombros como una estola de piel y siete se arrastran detrás,
    como la cola de un manto.
  - Lleva la armadura de samurái en los brazos (B5): hombrera de tres láminas, codera,
    brazal y guantelete.
  - Tiene una mano en la cadera y en la otra un fuego, y un anillo de nueve fuegos a su
    alrededor.
  - Las piernas son estilizadas, con medias y tacón (L5).

## Los bocetos

Salen de:

- `materiales/generadores/vulpina_modelo.py` (`vulpina('A' | 'B' | 'C')`);
- `jefa_modelo.py`, con el cuerpo, la cara y las piezas del muestrario;
- `vulpina_escenas.py`, con las escenas:
  - `heroe_X`, en la explanada;
  - `cabeza_X`;
  - `cartel_X`, de cerca y desde abajo, con el cielo y la luz de su neón;
  - `cara_X`, el primer plano de la cara con el fondo de estudio del muestrario;
  - `tres` y `materiales`.

Todas las fotos van sin letras y con el borde blanco. Los archivos se llaman
`vulpina_<tipo>_<vista>.jpg`, con el tipo en `abanico`, `llama` o `manto`.
