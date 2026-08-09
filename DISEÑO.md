# Cómo se diseñan las texturas de Atalaya

Este fichero no describe el mod — eso está en el [README](README.md). Describe
**cómo se dibuja**: proporciones, rampas de color, sombreado y qué hace que un
icono de 18 píxeles se entienda de un vistazo.

Está escrito a partir de cómo salió **`corrosion.png`**, que es el ejemplo que se
usa en todo el documento. El script que lo genera vive en el scratchpad como
`corrosion.py` y sirve de plantilla.

---

## 1. Mirar lo que ya hay, ampliado, antes de dibujar

Lo primero **no** es dibujar: es abrir las texturas existentes a tamaño grande y
sacarles la paleta. Un icono nuevo tiene que parecer del mismo mod.

```python
from PIL import Image
im = Image.open('radiacion.png').convert('RGBA')
im.resize((im.width*16, im.height*16), Image.NEAREST).save('grande.png')

# y la paleta, con cuentas
colores = {}
for r, g, b, a in im.getdata():
    if a >= 16:
        colores[(r, g, b)] = colores.get((r, g, b), 0) + 1
```

De ahí salió el idioma que comparten los efectos del mod:

- **Silueta sólida y centrada**, sin apenas huecos interiores
- **Núcleo claro** y **canto más apagado**
- Alguna **mota suelta** alrededor
- Lo único que cambia entre ellos es el **matiz**

Ese último punto es el que más importa y se explica solo en el punto 4.

Mirar la paleta sirve para copiar el color. Para saber si lo nuevo **pega de
verdad** hay que medirlo: el punto 16.

---

## 2. Tamaños

| Qué | Lienzo | Cuánto ocupar |
|---|---|---|
| Efecto de estado | **18 × 18, obligatorio** | ~11 × 15, centrado, con aire alrededor |
| Item | **16 × 16** | Casi todo el lienzo |
| Icono de HUD | **el que quieras** | Depende del hueco; ver la gota y el copo |

Dejar aire es deliberado en los efectos: van pegados unos a otros en la barra y
sin margen se tocan.

### La diferencia entre "obligatorio" y "el que quieras"

No es un convenio, es cómo se dibuja cada cosa:

- **El icono de un efecto** lo pinta el juego en un cuadro fijo. En el bytecode
  es literal: `blitSprite(..., 18, 18)`. Si la textura mide otra cosa, se
  remuestrea.
- **Un elemento de HUD propio** lo dibujas tú, con el tamaño que le pases al
  `blit`. Si textura y dibujo miden lo mismo, cada téxel cae en un píxel de
  interfaz y sale limpio a cualquier escala.

Y remuestrear un dibujo hecho píxel a píxel lo destroza. Un copo de 25 metido en
el cuadro de 18 pierde **7 filas y 7 columnas de cada 25**: de 224 píxeles llegan
120, se caen las filas 1, 5, 8, 12, 16, 19 y 23, y la simetría se rompe.

```
a 25, como se dibujó        a 18, como lo vería el juego
    ....A....                    .......####.......
   ...AAA...                     ..###.##..##.###..
  ..AA.AA..                      ..#.#..####..#.#..
```

> Antes de dar por bueno un tamaño: **simula el remuestreo y míralo.** Son cinco
> líneas de script y evita descubrir en el juego que el icono es una mancha.

Subir la resolución solo ayuda **si el elemento también ocupa más pantalla**.
En el medidor del frío sí —se dibuja al tamaño de su textura—; en el icono del
efecto, nunca.

---

## 3. La silueta se escribe como datos, no se dibuja

Nada de colocar píxeles a mano. La forma es **una lista de medias anchuras por
fila**, y se retoca cambiando un número:

```python
#            y2 y3 y4 y5 y6 y7 y8 y9 y10 y11 y12 y13 y14
SEMIANCHOS = [0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 4, 3]
ARRIBA = 2   # primera fila dentro del lienzo
EJE = 8      # columna del eje

for i, semi in enumerate(SEMIANCHOS):
    y = ARRIBA + i
    for x in range(EJE - semi, EJE + semi + 1):
        solido.add((x, y))
```

El ancho real de cada fila es `2·semi + 1`, así que siempre sale **impar y
simétrico**. Para una gota: crecer despacio arriba (`0,0,1,1,2,2`) y ensanchar de
golpe abajo (`3,4,4,5,5`) — eso es lo que la separa de un óvalo.

> Una lección cara: la primera pata alada tenía la base cortada en plano y leía
> como huevo. **La curva de cierre importa más que el tamaño.** Si la última fila
> es ancha, no es una gota.

---

## 4. La rampa: cinco pasos, y el matiz es lo que diferencia

Cada textura usa **cinco tonos** del mismo color, de borde a núcleo:

```python
BORDE  = (0x1E, 0x3A, 0x0F)   # casi negro, con el tinte del color
OSCURO = (0x3E, 0x7A, 0x18)
MEDIO  = (0x6F, 0xBF, 0x2A)
CLARO  = (0xA8, 0xE6, 0x3C)
NUCLEO = (0xE8, 0xFF, 0x8A)   # casi blanco, tirando al color
```

Dos reglas que hacen que la rampa funcione:

- **El borde no es negro puro**: lleva el tinte del color. Negro puro ensucia.
- **El núcleo no es blanco puro**: tira hacia el color. Blanco puro apaga el tono.

> Ojo: esta rampa vale para un **item**, que se ve sobre el gris claro del
> inventario. Para un **efecto de estado** el fondo es casi negro y hay que
> subirla entera — ver el punto siguiente.

Y lo que de verdad decide el diseño de un efecto:

> **El matiz es la única información que se lee rápido.** Morado la radiación,
> naranja la insolación, verde ácido la corrosión. Si los tres pueden coincidir en
> la barra de efectos, distinguirse de un vistazo es lo único que importa — la
> forma se mira después, si acaso.

Antes de elegir un color, comprobar que no choque con los que ya existen.

---

## 4-bis. El fondo es oscuro: la rampa entera va por encima

Lo anterior vale para un item sobre el inventario. Para un **efecto de estado**
hay que corregirlo, porque su marco es un gris casi negro y eso cambia las reglas.

Un tono oscuro sobre fondo oscuro **no dibuja un borde: desaparece**. En vez de
recortar la silueta, se funde con el marco y el icono pierde forma justo por
donde debería definirse.

La solución es subir **toda la rampa**, no solo el núcleo. La regla salió de
comparar los iconos por luminancia (0 = negro, 255 = blanco) cuando solo la
insolación estaba rehecha:

| Icono | Tono más oscuro, antes | Después |
|---|---|---|
| **insolación** | **153** | 153 |
| corrosión | 45 | **157** |
| radiación | 15 | **161** |
| empapado | 33 | **157** |

La insolación no bajaba de 153 en ningún píxel, así que su silueta entera flotaba
sobre el marco. Las otras tres tenían tonos tan oscuros como el propio fondo y se
comían su contorno; se rehicieron todas a la franja clara, y hoy el mínimo de la
familia está entre 153 y 161.

Dos consecuencias prácticas:

- **Nada de borde casi negro** en un efecto. Si se quiere contorno, que sea un
  tono medio del propio color, no un oscuro.
- **El degradado sustituye al contorno.** Con toda la rampa clara, lo que separa
  el icono del fondo es el salto de luminancia contra el marco, y lo que le da
  volumen es el degradado interno. No hacen falta las dos cosas.

Y ahí se puede gastar el presupuesto de tonos: la insolación usa nueve porque
todos caben en la franja clara. Cinco eran pocos para un degradado suave cuando
el rango útil se ha reducido a la mitad de arriba.

---

## 5. El contorno se calcula, no se dibuja

Un píxel es contorno si toca el aire por alguno de sus cuatro lados. Nunca se
pinta a mano:

```python
if any((x+dx, y+dy) not in solido for dx, dy in ((1,0), (-1,0), (0,1), (0,-1))):
    px[x, y] = BORDE
```

Sale perfecto siempre, y sigue saliendo perfecto cuando cambias la silueta.

---

## 6. Sombreado radial para lo compacto

En un icono pequeño y macizo el degradado va **por distancia a un punto**, no por
filas. El núcleo se pone donde la forma es más ancha — en una gota, la panza:

```python
NUCLEO_XY = (8.0, 10.5)
d = math.hypot(x - NUCLEO_XY[0], y - NUCLEO_XY[1])
c = NUCLEO if d < 1.6 else CLARO if d < 3.0 else MEDIO if d < 4.6 else OSCURO
```

Los cortes (1.6 / 3.0 / 4.6) reparten los cuatro tonos en anillos. Subirlos
engorda el brillo; bajarlos lo concentra.

El degradado **por filas** (claro arriba, oscuro abajo) se reserva para cuando el
código va a recortar la imagen por altura — ver el punto siguiente.

---

## 7. Cuando el color lo pone el código: el tinte multiplica

Los medidores del HUD se dibujan con `blit(..., color)`, y ese color **multiplica**
la textura. De ahí salen dos trucos que ahorran trabajo:

**Una sola imagen para dos estados.** Negro por cualquier color sigue siendo
negro, así que el contorno aguanta cualquier tinte. La misma gota vale para el
agua y para el hueco vacío, cambiando solo el color del `blit`.

**Un degradado sin pintarlo.** Si el relleno es una rampa de gris, teñirla de un
color conserva la rampa: sale claro arriba y hondo abajo sin dibujar franjas en
el código.

### Pero el segundo truco tiene un techo

Multiplicar una rampa de gris por un color **encierra el degradado en un solo
matiz**: solo puede ir de claro a oscuro del mismo tono. Y si el tinte es pálido,
ni eso — la gota teñida de celeste claro tenía tan poca diferencia entre la punta
y la base que parecía plana.

La salida es meter el color **dentro de la imagen** y teñir el relleno de
**blanco**, que la deja tal cual. El primer truco —una imagen, dos estados— sigue
funcionando igual, porque el hueco se tiñe de un gris oscuro que la apaga entera.

| | Color en el tinte | Color en la imagen |
|---|---|---|
| Degradado | un solo matiz | el que quieras |
| Recolorear | cambiar un `int` | regenerar el PNG |
| Estados | los que sean | los que sean |

Así que: **grises mientras el color sea uno y plano; color dentro en cuanto el
degradado tenga que girar de tono.** La gota va de cian pálido a azul de agua y
el copo de blanco a cian de hielo — eso con un tinte no se puede.

---

## 8. Las motas: lo que separa un icono de una mancha

Tres o cuatro píxeles sueltos alrededor, en los tonos medios, y el dibujo pasa de
blob a **cosa que ocurre**. En la corrosión sugieren que la lluvia sigue cayendo;
en la radiación, que algo se desprende.

```python
MOTAS = [(3, 4, MEDIO), (13, 6, MEDIO), (14, 12, OSCURO), (12, 2, CLARO)]
```

Repartirlas **asimétricamente** — simétricas parecen un error. Y fuera de la
silueta, nunca encima.

---

## 9. Mirar ampliado y a tamaño real

Un icono puede verse estupendo a 16× y ser papilla a 18 píxeles. Hay que
comprobar las dos cosas, y el tamaño real es el que manda:

```python
grande = im.resize((18*16, 18*16), Image.NEAREST)   # para juzgar la forma
real   = im.resize((18*2,  18*2),  Image.NEAREST)   # para juzgar si se lee
```

Y siempre **al lado de los que ya existen**, sobre un fondo oscuro parecido al del
juego. Un icono no se juzga solo.

---

## 10. Cuando el dibujo lo traes tú: componer, no redibujar

Si ya hay una textura hecha a mano, **no rehacerla**. Sus detalles internos son lo
que la hace reconocible y se pierden al redibujarla pequeña.

Lo correcto es **componer con sus píxeles reales**: recortar al contenido, encoger
con `NEAREST` y montar.

```python
im = Image.open(f).convert('RGBA')
recorte = im.crop(im.getbbox())
alto = 9
ancho = round(recorte.width * alto / recorte.height)   # respetar la proporción
pequeno = recorte.resize((ancho, alto), Image.NEAREST)
```

> La pata alada costó cuatro intentos por saltarse esto. Redibujada salía cuchilla
> + nuez; compuesta con los píxeles de la pata ligera y el alón, salió a la
> primera. Y en la primera tanda **achaté el ala** por encoger a medidas
> arbitrarias: si no se respeta la proporción, un ala parece un pez.

Para recolorear conservando un dibujo: clasificar los píxeles por **saturación**
(qué mitad es cuál) y remapear por **luminancia relativa** dentro de cada grupo.
Así el volumen se mantiene aunque la paleta cambie entera.

---

## 11. Generar con script, e iterar mirando

Todas las texturas del mod salen de un script en el scratchpad, no de un editor.
Eso permite retocar una forma cambiando un número, y volver atrás.

El ciclo es: **generar → renderizar ampliado → mirarlo → ajustar**. En serio
mirarlo: la corrosión salió a la primera, pero la pata alada necesitó ocho vueltas
y cada una arregló algo que solo se veía al verlo.

Y antes de tocar una textura que no hiciste tú, **copiarla al scratchpad**. Las
que aporta el usuario no siempre están en git todavía.

---

## 12. Recolorear no es rediseñar

Reducir tonos, subir la rampa o añadir un contorno son operaciones **automáticas**:
mejoran una textura, pero no la rediseñan. Si lo que se pide es un rediseño, hay
que **volver a dibujar la silueta** respetando la idea; retocar los píxeles
existentes da otra versión del mismo dibujo, no una propuesta nueva.

Y al revés: cuando el original ya tiene una silueta buena, retocarla es
justamente lo correcto y **cambiarla es empeorarla**. La esquirla irregular de la
miel cristalizada dice "trozo roto de resina"; sustituirla por un rombo la
convierte en una gema genérica.

Antes de empezar, decidir cuál de las dos cosas se está haciendo.

---

## 13. Trampas de PowerShell al generar texturas

Todas cuestan tiempo y ninguna da un error que apunte a la causa:

**`@()` aplana los arrays anidados.** Escribir las motas en línea da escalares:

```powershell
foreach ($m in @(@(3,3,2), @(14,5,3))) { ... }   # $m vale 3, luego 3, luego 2...
```

Funciona si se pasan como **parámetro de función**, donde el array de arrays
sobrevive. Si no, hay que escribir las llamadas sueltas.

**La coma se evalúa antes que el `+` dentro de los corchetes.** Indexar un array
de dos dimensiones con cuentas escritas en línea no hace lo que parece:

```powershell
$mapa[$r+1, $c+1]        # se lee como  $r + @(1,$c) + 1
```

y el error habla de `op_Addition` sobre `Object[]`, que no apunta al índice.
Hay que escribir `$mapa[($r+1), ($c+1)]`.

**Las variables no distinguen mayúsculas.** Un `$n = $orden.Count` machaca un
`$N = 18` de arriba, y los bitmaps salen del tamaño equivocado. El síntoma
—"x debe ser menor que el ancho", con x=16 en un lienzo de 18— no apunta a nada.
Pasa igual con un `foreach ($n in ...)` y un `$N = $b.Width` dentro: la tabla
sale con los nombres cambiados y parece un fallo de los datos.

**`return` desenrolla los arrays.** Devolver un `bool[18,18]` de una función lo
convierte en **324 escalares sueltos**, y quien lo recibe cree tener una máscara.
El síntoma es desconcertante: `$m[$r,$c]` sobre un array de una dimensión
devuelve *dos elementos*, que en un `if` son verdaderos, así que **sale todo
pintado**. La coma lo evita:

```powershell
return , $m
```

**GDI+ bloquea el fichero de origen.** Mientras el `Bitmap` siga abierto no se
puede guardar encima, y recolorear una textura es justo eso: leer y escribir el
mismo PNG. Falla con "Error genérico en GDI+", que no dice nada. Hay que guardar
en un temporal, cerrar el bitmap y mover.

**`Set-Content -Encoding utf8` mete BOM** en PowerShell 5.1. En un `.json` el
juego lo tolera, pero en un `.java` `javac` lo rechaza con
`illegal character: '﻿'`. Para escribir sin BOM:

```powershell
[System.IO.File]::WriteAllText($ruta, $texto, (New-Object System.Text.UTF8Encoding($false)))
```

Y un último detalle, de nombres: los identificadores de recursos de Minecraft solo
aceptan `[a-z0-9_.-]`, así que **nada de eñes ni tildes** en un fichero que vaya a
`assets/`. Además, PowerShell 5.1 lee los `.ps1` sin BOM como ANSI, y una ruta con
eñe escrita literalmente en el script no encuentra el fichero: hay que buscarlo
con `Get-ChildItem -Filter`.

---

## 14. El contorno decide la silueta, no al revés

Regla del §5: el contorno se calcula. La consecuencia, que no es obvia hasta que
pasa: **a 12 píxeles el contorno se come los huecos**.

Un hueco de 2 px entre dos brazos tiene borde por los dos lados, así que se
rellena entero de negro. La forma sigue ahí, pero el hueco deja de leerse: donde
querías aire queda una mancha.

Al diseñar el copo del medidor de frío se probaron seis siluetas **mirando el
ASCII con el contorno ya aplicado**, no la silueta a pelo. El resultado:

| Silueta | Qué salió |
|---|---|
| Copo fino de 6 brazos | El **centro** se rellenó de negro. Justo lo que tenía que brillar |
| Estrella de 8 puntas | Las diagonales quedaron en **píxeles sueltos** rodeados de negro: ruido |
| Cruz gruesa con horquillas | Limpia, pero no parecía un copo |

### La causa no era la silueta: era la vecindad

La primera conclusión fue "hay que usar siluetas gruesas". **Era la equivocada**, y
se vio al probar el copo en el juego: leía como una cruz, no como nieve.

El problema estaba en cómo se calcula el contorno. Con **vecindad-8** —marcar
cualquier hueco que toque la silueta, incluso en diagonal— las cuñas entre brazos
se cierran por los dos lados a la vez. Con **vecindad-4** —solo arriba, abajo,
izquierda y derecha— el borde sigue recortando la forma, pero las cuñas
sobreviven:

```
vecindad-8                    vecindad-4
.oooo##oooo.                  ...o..o##o..o...
.o#oo##oo#o.   <- ruido       .oo#o.o##o.o#oo.   <- brazos con aire
```

Cambiando solo eso, el copo fino de 6 brazos —el que había salido con el centro
negro— pasó a ser el mejor de todos.

Regla, entonces:

> **Silueta con huecos → contorno de vecindad-4. Silueta maciza → da igual.**
> El contorno diagonal solo hace falta cuando no hay nada que preservar.

Y las dos que sí se sostienen:

1. **Nada por debajo de 1 px de grueso, y el detalle apoyado en el brazo.** Una
   horquilla pegada lee como rama; separada un píxel lee como suciedad.
2. **El tamaño que la forma pida, no el que use el vecino.** El copo empezó con
   las 12 filas de la gota y pasó a 16 y a 25 buscando sitio para las ramas. El
   que se quedó es de **17**, pero dibujado a mano: resultó que el problema no
   era el tamaño sino el trazo, y una reja fina bien puesta cabe donde una
   generada por fórmula no cabía.

   > Y hay un límite a esto: subir la textura **sin subir el dibujo** no sirve
   > de nada. El icono de un efecto se pinta en un cuadro fijo de 18×18, así que
   > una textura mayor se remuestrea de forma desigual y sale **peor**. Los
   > píxeles de más solo ayudan cuando el elemento también ocupa más pantalla,
   > como el medidor, que se dibuja al mismo tamaño que su textura.

Y el método, que es lo que de verdad importa: **generar el ASCII con contorno y
mirarlo antes de escribir el PNG.** Cuesta un minuto y evita descubrir en el juego
que el centro del copo es negro.

---

## 14-bis. Si no hay término medio, cambia de parametrización

La estrella del icono de hipotermia se intentó primero como **brazos cónicos**:
un eje por brazo y una anchura que se estrecha hacia la punta.
Se probaron seis combinaciones de grosor y curva, y no había término medio:

| Grosor de base | Qué salía |
|---|---|
| 3,2 – 3,6 | Brazos de 2 px: una estrella **espigada**, sin cuerpo |
| 4,8 | Los brazos se tocaban: un **octógono** con cuatro pinchos |

El problema no eran los números: era **con qué se estaba describiendo la forma**.
Un brazo cónico controla el eje y el grosor, que no es lo que define una estrella.
Lo que la define son **el radio de la punta y el del entrante**, y eso se dice
directo con un polígono:

```powershell
$u = [Math]::Atan2($dy, $dx) / ([Math]::PI / 4.0)   # sector de 45 grados
$u = $u - [Math]::Floor($u)
$k = 1.0 - [Math]::Abs(2.0 * $u - 1.0)              # 0 en la punta, 1 en el entrante
if ($d -le ($FUERA + ($DENTRO - $FUERA) * $k)) { ... }
```

Dos números, y salió a la primera.

La regla general, que ya había aparecido antes con otra forma:

> Cuando hay que pelearse con los parámetros y ninguno vale, casi nunca es que
> falte afinar: es que **la parametrización no expresa lo que quieres controlar**.

El otro caso fue estrechar una punta con `w0 * (1 - i/L)^curva`. Los cuatro
exponentes que se probaron daban el mismo defecto —la cola de la curva pasa varias
filas por debajo de medio píxel y sale un **pelo de 1 px de cinco filas**— porque
la curva no controla lo único que importaba ahí, que es **dónde acaba la punta**.
Con las anchuras escritas a mano sí:

```powershell
@(6,  @(5, 5, 5, 5, 3, 3, 3, 3, 1, 1))   # eje, anchuras por fila
```

Anchuras **impares** para que la punta quede centrada, y **el eje en entero** por
lo mismo: con el eje en `x.5` todas las anchuras salen pares y no hay punta.

La fórmula vale para explorar. Para rematar, o la lista o la parametrización que
hable el idioma de la forma.

---

## 15. Dos medidores que se leen al revés

La gota de hidratación se **vacía**; el copo de frío se **llena**. Son sentidos
opuestos a propósito y no una incoherencia:

> La gota vacía avisa de que **falta** algo. El copo lleno avisa de que **sobra**.
> En los dos casos **mucho color es peligro**, que es lo único que hay que
> entender de un vistazo.

Lo que sí comparten, y ahí no se negocia, es el **idioma de las flechas**: la misma
imagen y su reflejo, roja cuando la cosa va a peor y verde cuando va a mejor. Dos
mecánicas distintas pueden leerse al revés; lo que no pueden es hablar distinto.

El frío necesita **dos** flechas porque su nivel se mueve solo en ambos sentidos
—sube pasando frío, baja junto al fuego—. La hidratación solo baja o se queda
quieta, así que le basta una.

---

## 16. Medir contra los que ya hay, no solo mirarlos

El §1 dice que hay que abrir las texturas existentes antes de dibujar. Eso está
bien para sacar la paleta, pero **no basta para saber si lo nuevo pega**. Un icono
puede tener el color correcto y aun así desentonar, y a ojo solo se nota que "se
ve raro" — sin poder decir por qué.

La primera versión del icono de hipotermia era exactamente eso. Puesta al lado de
las otras cuatro y medida, el porqué salió solo:

| icono | ocupa | pintados | tonos | luminancia | huecos |
|---|---|---|---|---|---|
| insolación | 17×17 | 113 | 9 | 153–251 | 4 |
| corrosión | 12×14 | 75 | 5 | 157–245 | 0 |
| empapado | 15×14 | 104 | 6 | 157–246 | 2 |
| radiación | 16×15 | 96 | 8 | 161–248 | 14 |
| **hipotermia (mala)** | 25×25 | 224 | **31** | 151–244 | **133** |

Dos columnas se salían del rango y las dos explicaban la sensación:

- **31 tonos** donde la familia lleva de 5 a 9. Un degradado *continuo* donde los
  demás llevan una rampa *escalonada*.
- **133 huecos interiores** donde la familia lleva de 0 a 14. Una reja donde los
  demás son siluetas macizas.

Rehecho contra esos números —estrella maciza de seis puntas, seis tonos— quedó en
16×16, 108 pintados, 6 tonos, 154–249 y 0 huecos. Dentro de rango por todas las
columnas, y el problema desapareció.

### Las cinco medidas

Se sacan de un script de veinte líneas y valen para cualquier icono nuevo:

1. **Cuánto ocupa** del lienzo — que no sea el doble de grande que sus vecinos
2. **Píxeles pintados** — la masa visual
3. **Cuántos tonos distintos** — rampa escalonada, no degradado continuo
4. **Luminancia mínima y máxima** — el mínimo es la regla del §4-bis
5. **Huecos interiores** — macizo o calado, y la familia decide cuál

> El número que más discrimina es **cuántos tonos**. Es la diferencia entre un
> dibujo hecho a mano y uno generado por una fórmula, y se nota aunque no sepas
> nombrarla.

### Y sirve para elegir entre propuestas

Antes de la estrella se probó una variante de brazos finos con travesaños: 116
pintados y 14 huecos, **dentro de rango también**. Se descartó mirándola —los
huecos del centro leían como suciedad—, no midiéndola.

Las medidas dicen si algo se sale de la familia. No dicen si es bonito.

---

## 17. La simetría no se confía al trazado

Un brazo de un píxel se decide comparando contra **medio píxel exacto**. Ahí los
decimales mandan, y el mismo brazo entra por un lado y no por el otro: el copo
sale torcido y no se ve por qué.

No hay que afinar el redondeo, hay que quitarlo de la ecuación. Combinando cada
celda con sus reflejos, la simetría deja de depender de los decimales:

```powershell
$q = $N - 1 - $r
$p = $N - 1 - $c
if ($m[$r,$c] -or $m[$q,$c] -or $m[$r,$p] -or $m[$q,$p] -or
    $m[$c,$r] -or $m[$p,$r] -or $m[$c,$q] -or $m[$p,$q]) { $sim[$r,$c] = $true }
```

Los cuatro primeros dan simetría de espejo; los cuatro últimos —con las
coordenadas cambiadas— añaden las diagonales, o sea simetría de ocho.

**Tiene un precio: engorda.** Un trazo de 1 px combinado con su reflejo sale de 2.
Hay que trazar más fino de lo que se quiere y dejar que la simetría lo recupere;
si se traza al grosor final, sale el doble de gordo. Y demasiado fino tampoco
vale: por debajo de 0,8 px de grosor los brazos se parten antes de reflejarse.

Para 4 u 8 brazos exactos hay una salida mejor: **plegar el píxel al primer
octante** y evaluar un solo brazo. Sale simétrico por construcción y sin engordar.
Con seis brazos no se puede —60° no cae en la rejilla— y ahí toca reflejar.
