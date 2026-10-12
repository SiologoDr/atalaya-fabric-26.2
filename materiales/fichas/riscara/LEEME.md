# Riscara, la Dragona de los Riscos

A Juan le gustaron el monstruo y sus tres tipos (12-10-2026): «me gustó también ese
monstruo y sus variables». Es el segundo monstruo hecho con la receta de Simara:
una sola entidad en tres tipos, con texturas limpias y las fauces encendidas.

## Lo que comparten los tres tipos

Los tres usan el mismo modelo:

- se planta sobre dos patas en lo alto de un risco, con las alas abiertas y el
  cuello en ese;
- mide unos 22 bloques de alto y 35 de envergadura;
- su cabeza tiene fauces abiertas con dientes en peine, colmillos y un núcleo
  encendido en la garganta;
- lo nuevo: las alas tienen nervios como los de una libélula y el borde
  encendido, por donde le corre su elemento.

## Los tres tipos

- **De Tormenta (neón amarillo).** Escamas de pizarra, dos cuernos como
  pararrayos con la punta encendida, rayos en zigzag en las alas y una cola en
  tridente.
- **De Escarcha (neón azul hielo).** Escamas blancas de escarcha, una corona de
  carámbanos y carámbanos en la quijada, estrellas de escarcha en las alas y una
  cola de cristales.
- **De Ponzoña (neón verde).** Escamas oscuras con manchas de veneno, una
  gorguera de membrana, bulbos de esporas, pústulas que brillan en las alas y una
  cola con un bulbo y un aguijón.

## Las alas

La membrana es oscura, en bandas, con tres nervios largos. El borde libre va en
festones y encendido, y lleva unos pocos acentos de cada tipo. La primera versión
tenía todos los nervios encendidos y parecía una red de neón.

## Los bocetos

Salen de `materiales/generadores/riscara_modelo.py` (`riscara('A' | 'B' | 'C')`) y
de `riscara_escenas.py`, con las escenas `heroe_X`, `cabeza_X`, `tres` y
`materiales`. Usan los pintores limpios de `sierpe_modelo.py`.
