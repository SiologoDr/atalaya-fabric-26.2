# Cómo hacemos los monstruos de Atalaya (y cómo seguir)

Esta guía junta lo aprendido el 12 de octubre de 2026, ronda a ronda, con lo que dijo
Juan de cada propuesta. Sirve para hacer el siguiente monstruo sin repetir
errores.

## El objetivo

Monstruos al nivel de **Ofidia** (Dedsafio 4) y de **Espinara**: inventados, hechos de
dos o tres criaturas mezcladas con algo nuevo. No un animal de verdad agrandado.

## La receta

1. **La cabeza manda.** Es grande, mira a cámara y tiene las fauces abiertas: dos
   mandíbulas, arriba y abajo. Lleva dientes blancos en peine y colmillos delante.
2. **La boca brilla por dentro con un solo neón.** El paladar va en escalones de luz
   (blanco al fondo, neón, sombra) y al fondo de la garganta hay un núcleo o un remolino.
3. **Algo enmarca la cabeza.** Cuernos, una capucha, una corona, una membrana, aletas,
   cebos de luz o faroles.
4. **El cuerpo es oscuro, casi de un solo color, y se alza.** Es colosal y se ve en plano
   bajo, desde abajo.
5. **Las texturas son limpias.** Se dibujan a 8 píxeles por bloque y cada material
   tiene una paleta de 5 tonos. Valen escamas en U, escudos en bandas, placas en bandas,
   manchas grandes de borde limpio, remaches de 2×2 y vetas como curvas de nivel.
   **Nada de ruido ni motas sueltas.**
6. **Las membranas son oscuras y van en bandas.** El borde libre va encendido y lleva
   pocos acentos. Si todo brilla, parece una red de neón.
7. **Es una sola entidad con tres variantes que cambian de FORMA.** Cambian los
   cuellos, la corona, la piel y la silueta, no solo el color. Tienen que distinguirse
   de lejos, solo por la silueta. Cada variante lleva su neón.

## Lo que no (y de dónde sale)

| No | Por qué | Ronda |
|---|---|---|
| Ideas cósmicas o exageradas (lunas, auroras, estrellas) | «lo llevas a algo muy exagerado» | Tres Cielos |
| Bichos de cuerpo entero con la boca pequeña | parecen mobs, no jefes | Cuatro Materias |
| Texturas con ruido y motas | se ven sucias | Fauces |
| Un animal real agrandado | «es un escorpión literalmente, no un monstruo» | Tenazara |
| Tres variantes iguales con otro color | «deben ser variados los tipos de variantes, no lo mismo» | Tenazara |
| Un pico que se abre en cuatro | se parece a Espinara o al Demogorgon | Fauces |
| Placas en cuadrícula | se leen como bloques de Minecraft | Lernara (prueba) |
| Cráneos cúbicos | se leen como la calavera de Minecraft | Quimeras |
| Objetos y arquitectura (velas, papel, máscaras, torres) | gustan menos que lo orgánico | Quimeras, Fauces |
| Copiar a Ofidia tal cual | hay que hacer variantes propias | Ofidia |
| Recrear de memoria o de una sola imagen | la primera Ofidia no se parecía: le faltaban los brazos, la boca y la cola | Ofidia |

## Lo que hay hasta ahora

| Ficha | Qué es | Veredicto de Juan |
|---|---|---|
| `espinara/` | zarza que florece, flor carnívora por cabeza | le gustó mucho |
| `simara/` | sierpe de tambores y cinturones, en 3 tipos | le gustó: es el formato |
| `riscara/` | dragona de los riscos, en 3 tipos | le gustó |
| `guaridas/` | yeti, sapo-caimán, buitre y topo | bien, no excelentes |
| `tenazara/` | alacrana de tenazas-fauces, en 3 tipos | guardada, pero es un animal literal |
| `lernara/` | hidra de 3, 5 y 2 cabezas | guardada; primera con variantes de forma |
| `ofidia/` | Ofidia recreada con su cuerpo de verdad y 3 variantes nuestras sobre ese cuerpo | le gustó la Encadenada; la original es solo estudio |

Formas de cuerpo que ya están, contando los jefes del mod:

- **Jefes del mod:** mar (Nerea), mariposa (Aeralis), jaguar (Rajang) y caballero (Novilis).
- **Fichas guardadas:** zarza (Espinara), sierpe (Simara), dragona (Riscara), alacrana
  (Tenazara), hidra (Lernara), sirena-sierpe (Ofidia), y yeti, sapo, buitre y topo
  (Guaridas).

El siguiente debería tener una forma de cuerpo que no esté.

## Cómo se hace uno nuevo, paso a paso

1. **Leer** `DISEÑO.md` y esta guía.
2. **Elegir una forma de cuerpo** que no esté en la lista y que sea de monstruo (de los
   de siempre o inventada), no de un animal real.
   - Si se parte de un monstruo que ya existe (como Ofidia), hay que estudiarlo a fondo
     antes de dibujar: el cartel, sus retratos y fotogramas de los directos.
   - Kick guarda los directos de los streamers del evento. La API
     `https://kick.com/api/v2/channels/<canal>/videos` da la lista m3u8 de cada uno, y de
     ahí se sacan fotogramas con ffmpeg.
   - Hay que mirarlo de frente, de lado y de arriba, y apuntar cada pieza.
3. **Pensar la mezcla y lo nuevo**: qué dos o tres criaturas lo forman, qué enmarca la
   cabeza y qué detalle no tiene ningún otro.
4. **Pensar las tres variantes de forma**: qué cambia en la silueta de cada una.
   - Lernara cambia el número de cuellos y cómo salen.
   - Ofidia cambia lo que enmarca la cabeza.
5. **Escribir el boceto** en `materiales/generadores/`:
   - `<nombre>_modelo.py` construye el monstruo con cajas.
   - `<nombre>_escenas.py` hace los renders.
   - Se copia la estructura de `lernara_modelo.py` y de `lernara_escenas.py`.
6. **Probar a media resolución.** Se lanzan los renders de prueba, se miran y se
   corrige lo que no se lea. Se repite hasta que quede bien.
7. **Hacer los renders finales.** Son los mismos comandos sin `RAPIDO=1`.
8. **Publicar la ficha** (un link de Claude con la cuenta de Juan) y esperar a que Juan
   elija.
9. **Guardarla** en `materiales/fichas/<nombre>/` con su `LEEME.md` cuando Juan lo diga.
10. **No implementarla en el juego** hasta que Juan lo pida.

## Las herramientas

- `bestias_modelo.py` tiene la caja con las caras pintadas (`cubo`), la viga entre dos
  puntos (`viga`), los dientes y púas (`pua`), las garras (`garra`) y los cristales
  (`cristal`). `PPB = 8` son los píxeles por bloque.
- `sierpe_modelo.py` tiene los pintores limpios: `_escamas_cara`, `_escudos`,
  `_manchas`, `_bisel`, `_remaches`, `_degradado` (el paladar), `_limpiar` y
  `_borde_de`. También tiene `lamina` (una membrana entre cuatro puntos), `bola`
  (esfera de píxel), `cadena` y `_marcos` (marcos a lo largo de una curva).
- `riscara_modelo.py` tiene `bloque` (caja de esquinas comidas), `cuello` y la
  cabeza de dragón.
- `lernara_modelo.py` tiene el cuello con collar, la cabeza con corona (cuernos,
  cresta o capucha) y un cuerpo de cuatro patas.
- `quimeras_escenas.py` tiene el lienzo, la niebla, el revelado (`tono`, `bloom`,
  `vineta`) y el rótulo (`rotular`).

Cada ficha tiene las mismas escenas: `heroe_X` (el monstruo en su sitio, plano bajo),
`cabeza_X` (de cerca, un poco por debajo de la cabeza para mirar dentro de las fauces),
`tres` o `cuatro` (todas juntas con un jugador de 1,8 delante) y `materiales` (la lámina
de texturas).

Comandos, desde `materiales/generadores/`:

```
RAPIDO=1 python lernara_escenas.py ../.. <carpeta> heroe_A,cabeza_A
python lernara_escenas.py ../.. <carpeta>
```

El primero hace pruebas a media resolución. El segundo hace todas las escenas en
grande.

## Cómo se guarda una ficha

- La carpeta es `materiales/fichas/<nombre>/`.
- Los renders se llaman `<nombre>_<variante>_heroe.jpg` y `<nombre>_<variante>_cabeza.jpg`,
  más `<nombre>_tres_variantes.jpg` (o `_cuatro_`) y `<nombre>_materiales.jpg`.
- El `LEEME.md` lleva:
  - lo que comparten las variantes;
  - cada variante;
  - el veredicto de Juan, con sus palabras;
  - de qué scripts salen los bocetos.
