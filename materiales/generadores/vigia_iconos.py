"""Huevo del Vigia, Ojo del Vigia (item) y el icono del efecto Marcado."""
from PIL import Image
import math, sys, os

RAIZ = sys.argv[1]
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')

def hexc(s, a=255):
    s = s.lstrip('#'); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

# ------------------------------------------------------------------
# Huevo: la silueta del huevo del fulminante, recoloreada (DISENO §10).
# Cascara de tela oscura con motas ambar: los colores del bicho.
# ------------------------------------------------------------------
huevo = Image.open(os.path.join(TEX, 'item/huevo_fulminante.png')).convert('RGBA')
MAPA = {
    (168, 143, 99): hexc('1d1a22'),   # contorno
    (213, 196, 150): hexc('38333f'),  # cascara
    (247, 244, 232): hexc('5a5363'),  # brillo de la cascara
    (112, 92, 62): hexc('ffb43a'),    # motas: el ojo
}
out = Image.new('RGBA', huevo.size, (0, 0, 0, 0))
for y in range(16):
    for x in range(16):
        p = huevo.getpixel((x, y))
        if p[3] >= 16:
            out.putpixel((x, y), MAPA.get(p[:3], p))
out.save(os.path.join(TEX, 'item/huevo_vigia.png'))

# ------------------------------------------------------------------
# Ojo del Vigia: el ojo arrancado del farol, con su marco de hierro.
# ------------------------------------------------------------------
HIERRO = [hexc(c) for c in ('231f1c', '3a332d', '554638', '7a5a3c', 'a8683a')]
IRIS = [hexc(c) for c in ('8a4a10', 'c8741a', 'ffb43a', 'ffd36a', 'fff0a8')]
PUPILA = hexc('2b0d05')
ojo = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
q = ojo.load()
C = (7.5, 7.5)
for y in range(16):
    for x in range(16):
        dx, dy = x - C[0], y - C[1]
        d = math.hypot(dx, dy * 1.15)
        if d > 7.2:
            continue
        if d > 5.6:
            # aro de hierro, mas claro arriba a la izquierda
            luz = (-dx - dy) / 10.0
            q[x, y] = HIERRO[0] if d > 6.6 else HIERRO[3 if luz > 0.3 else 2 if luz > -0.3 else 1]
            continue
        # iris radial, nucleo arriba a la izquierda del centro
        dn = math.hypot(x - 6.3, y - 6.3)
        q[x, y] = IRIS[4] if dn < 1.2 else IRIS[3] if dn < 2.6 else IRIS[2] if dn < 4.0 else IRIS[1] if d < 5.0 else IRIS[0]
# pupila en ranura vertical
for y in range(4, 12):
    q[7, y] = PUPILA
    q[8, y] = PUPILA
    if 6 <= y <= 9:
        q[6 if y in (7, 8) else 7, y] = PUPILA if y in (7, 8) else q[7, y]
# remaches del aro
for (x, y) in ((7, 1), (1, 8), (14, 7), (8, 14)):
    q[x, y] = HIERRO[4]
ojo.save(os.path.join(TEX, 'item/ojo_vigia.png'))

# ------------------------------------------------------------------
# Marcado (efecto, 18x18): un ojo almendrado rojo. Rampa entera por encima
# de 150 de luminancia (DISENO §4-bis): el marco del efecto es casi negro.
# ------------------------------------------------------------------
ROJO = [hexc(c) for c in ('e0584c', 'ec7466', 'f59484', 'fbb8a8', 'ffe2d8')]
marca = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
m = marca.load()
for y in range(18):
    for x in range(18):
        dx, dy = (x - 8.5) / 7.5, (y - 8.5)
        # almendra: media anchura vertical que cae con el coseno
        semi = 4.6 * math.cos(dx * math.pi / 2) if abs(dx) <= 1 else -1
        if abs(dy) > semi:
            continue
        borde = abs(dy) > semi - 1.0
        dc = math.hypot(x - 8.5, (y - 8.5) * 1.3)
        if borde:
            m[x, y] = ROJO[0]
        elif dc < 1.4:
            m[x, y] = ROJO[4]
        elif dc < 2.6:
            m[x, y] = ROJO[3]
        elif dc < 3.8:
            m[x, y] = ROJO[2]
        else:
            m[x, y] = ROJO[1]
# la ranura: hueco transparente, que el fondo oscuro haga de pupila
for y in range(6, 12):
    m[8, y] = (0, 0, 0, 0)
    m[9, y] = (0, 0, 0, 0)
# motas: algo se desprende de la mirada
for (x, y, c) in ((2, 3, ROJO[2]), (15, 4, ROJO[1]), (14, 14, ROJO[2]), (3, 13, ROJO[1])):
    m[x, y] = c
marca.save(os.path.join(TEX, 'mob_effect/marcado.png'))

# previsualizacion, sobre fondo oscuro como el del juego
prev = Image.new('RGBA', (16 * 3 + 18 + 40, 24), hexc('2b2b2b'))
prev.alpha_composite(out, (4, 4)); prev.alpha_composite(ojo, (28, 4)); prev.alpha_composite(marca, (52, 3))
fondo_inv = Image.new('RGBA', (20, 20), hexc('8b8b8b'))
prev.alpha_composite(fondo_inv, (76, 2)); prev.alpha_composite(ojo, (78, 4))
prev.resize((prev.width * 10, prev.height * 10), Image.NEAREST).save(sys.argv[2])
print('ok')
