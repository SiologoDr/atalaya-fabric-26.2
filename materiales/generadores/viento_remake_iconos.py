"""
El icono de la Marca del Vendaval del remake (propuesta): una polilla de
viento, la misma que persigue a la presa en la Caceria, en lugar de la espiral.
Mismo matiz (el azul de la marca de hoy, en la franja clara: luminancia >= 150)
y el metodo de DISENO.md: silueta como datos, contorno calculado, sombreado
radial desde los ocelos y motas sueltas. Solo vista previa.

Uso: python viento_remake_iconos.py <raiz del proyecto> <salida.png>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
EFE = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/mob_effect')

CANTO = (90, 170, 255)      # luminancia 153: el tono mas oscuro, como la marca de hoy
MEDIO = (120, 190, 255)
CLARO = (162, 211, 255)
NUCLEO = (222, 242, 255)

EJE = 8
# Por fila: los |dx| ocupados (el cuerpo es el 0). Las alas de delante anchas,
# una muesca entre las dos parejas y las de detras con su cola.
FILAS = {
    3: [0, 3, 4, 5],
    4: [0, 1, 2, 3, 4, 5, 6],
    5: [0, 1, 2, 3, 4, 5, 6, 7],
    6: [0, 1, 2, 3, 4, 5, 6, 7],
    7: [0, 1, 2, 3, 4, 5, 6],
    8: [0, 1, 2, 3, 4],
    9: [0, 1, 2, 3, 4, 5],
    10: [0, 1, 2, 3, 4, 5],
    11: [0, 1, 2, 3, 4],
    12: [0, 2, 3],
    13: [0, 3],
    14: [3],
}
ANTENAS = [(EJE - 1, 2), (EJE - 2, 1), (EJE + 1, 2), (EJE + 2, 1)]
OCELOS = [(EJE - 4, 5.5), (EJE + 4, 5.5), (EJE - 3, 9.5), (EJE + 3, 9.5)]
MOTAS = [(1, 14, MEDIO), (16, 3, CLARO), (15, 12, MEDIO)]


def polilla():
    solido = set(ANTENAS)
    for y, dxs in FILAS.items():
        for dx in dxs:
            solido.add((EJE - dx, y))
            solido.add((EJE + dx, y))
    im = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    px = im.load()
    for (x, y) in solido:
        if x == EJE:
            c = NUCLEO if y in (4, 5, 6) else CLARO                     # el cuerpo
        elif any((x + dx, y + dy) not in solido for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c = CANTO                                                   # el contorno, calculado
        else:
            d = min(((x - ox) ** 2 + (y - oy) ** 2) ** 0.5 for ox, oy in OCELOS)
            c = NUCLEO if d < 0.8 else CLARO if d < 1.7 else MEDIO
        px[x, y] = (*c, 255)
    for (x, y) in ANTENAS:
        px[x, y] = (*CLARO, 255)
    for x, y, c in MOTAS:
        if (x, y) not in solido:
            px[x, y] = (*c, 255)
    return im


nueva = polilla()
antes = [Image.open(os.path.join(EFE, n + '.png')).convert('RGBA') for n in ('marca_vendaval', 'bendicion_vientos')]
fondo = (49, 49, 49, 255)          # el marco de los efectos, casi negro
K = 10
hoja = Image.new('RGBA', (960, 330), (237, 242, 245, 255))
d = ImageDraw.Draw(hoja)
f = ImageFont.truetype('C:/Windows/Fonts/Montserrat-SemiBold.ttf', 18)
piezas = [('Marca del Vendaval · hoy', antes[0]), ('Marca del Vendaval · remake', nueva), ('Bendicion · se queda', antes[1])]
for i, (t, im) in enumerate(piezas):
    x = 30 + i * 290
    caja = Image.new('RGBA', (18 * K + 20, 18 * K + 20), fondo)
    caja.alpha_composite(im.resize((18 * K, 18 * K), Image.NEAREST), (10, 10))
    hoja.alpha_composite(caja, (x, 40))
    real = Image.new('RGBA', (26, 26), fondo)
    real.alpha_composite(im, (4, 4))
    hoja.alpha_composite(real.resize((52, 52), Image.NEAREST), (x + 200, 40))
    hoja.alpha_composite(real, (x + 200, 100))
    d.text((x, 12), t, font=f, fill=(30, 50, 80))
d.text((30, 290), 'A 10x, y a la derecha a x2 y a tamano real sobre el marco de los efectos.', font=f, fill=(70, 90, 120))
hoja.convert('RGB').save(SALIDA, quality=95)
print('ok')
