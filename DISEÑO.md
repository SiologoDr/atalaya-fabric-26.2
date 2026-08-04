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

De ahí salió el idioma que comparten los tres efectos del mod:

- **Silueta sólida y centrada**, sin huecos interiores
- **Núcleo claro** y **borde oscuro**
- Alguna **mota suelta** alrededor
- Lo único que cambia entre ellos es el **matiz**

Ese último punto es el que más importa y se explica solo en el punto 4.

---

## 2. Tamaños

| Qué | Lienzo | Cuánto ocupar |
|---|---|---|
| Efecto de estado | **18 × 18** | ~11 × 13, centrado, con aire alrededor |
| Item | **16 × 16** | Casi todo el lienzo |
| Icono de HUD | **16 × 16** | Depende del hueco; ver la gota |

Dejar aire es deliberado en los efectos: van pegados unos a otros en la barra y
sin margen se tocan.

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

Y lo que de verdad decide el diseño de un efecto:

> **El matiz es la única información que se lee rápido.** Morado la radiación,
> naranja la insolación, verde ácido la corrosión. Si los tres pueden coincidir en
> la barra de efectos, distinguirse de un vistazo es lo único que importa — la
> forma se mira después, si acaso.

Antes de elegir un color, comprobar que no choque con los que ya existen.

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

**Un degradado sin pintarlo.** Si el relleno de la textura es una rampa de gris,
pintarla de un solo color conserva la rampa. La gota de hidratación es gris
255→132 de arriba abajo; teñida de celeste sale celeste claro arriba y hondo
abajo, sin dibujar franjas en el código.

**Una sola imagen para dos estados.** Negro por cualquier color sigue siendo
negro, así que el contorno aguanta cualquier tinte. La misma gota vale para el
agua (celeste) y para el hueco vacío (azul casi negro).

Cuando la textura se vaya a teñir, el relleno se dibuja en **grises**, no en color.

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
