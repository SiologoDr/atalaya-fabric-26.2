"""
Los iconos de la barra de armadura con un conjunto entero puesto (IconosArmadura,
en el cliente): la pechera del conjunto, con sus colores, y un brillo que la
cruza de vez en cuando (como el de los corazones de batalla).

Uso: python iconos_armadura_hud.py <raiz del proyecto> [--ficha=carpeta]

Sin --ficha escribe assets/atalaya/textures/gui/sprites/hud/armor/<conjunto>_
{full,half,empty}.png (y el .mcmeta de los animados). Con --ficha pinta en esa
carpeta el HUD de mentira con cada conjunto, ampliado y en GIF.

La silueta es la de vanilla (hud/armor_full.png, sacada del jar): 9 x 9, el
juego la pinta en un cuadro fijo. Los colores salen de la pechera de cada
conjunto (textures/item/<conjunto>_chestplate.png, DISENO.md punto 1):

  mareas    hombreras de perla, peto verde azulado, franja de perla y cinto cian
  jade      hombreras de oro, peto de jade oscuro, gema verde con marco de oro
  vendaval  hombreras lila, peto anil, gema celeste
  solar     hombreras de oro, peto de hierro quemado, el sol en el pecho
  hazmat    amarillo de aviso con las correas negras

El medio es como el de vanilla: la mitad izquierda llena, la raya negra en
medio y la derecha vacia. El vacio, el contorno con el fondo del conjunto muy
oscuro (que se vea que falta).
"""
import glob
import io
import json
import os
import sys
import zipfile

from PIL import Image

RAIZ = next((a for a in sys.argv[1:] if not a.startswith('--')), '../..')
FICHA = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--ficha=')), None)


def hexa(c):
    return ((c >> 16) & 255, (c >> 8) & 255, c & 255)


def mezcla(a, b, k):
    return tuple(round(a[i] * (1 - k) + b[i] * k) for i in range(3))


# Por conjunto: contorno, hombreras (claro, medio, oscuro), peto (claro, medio,
# oscuro), cinto (claro, oscuro), el fondo del vacio y lo que lleva en el pecho.
CONJUNTOS = {
    'mareas': dict(contorno=0x0B161D, hombro=[0xFFF4FA, 0xF0D4E2, 0xD6AAC0], peto=[0x527F8A, 0x386470, 0x284C58],
                   cinto=[0x3FE0FF, 0x1B8AA6], vacio=0x16262C,
                   pecho={(4, 3): 0xFFF4FA, (4, 4): 0xF0D4E2, (4, 5): 0xD6AAC0}),
    'jade': dict(contorno=0x0C140F, hombro=[0xFFF2C0, 0xF8D97C, 0xD4A83A], peto=[0x4B6A53, 0x35503D, 0x273C2E],
                 cinto=[0xD4A83A, 0x9A7420], vacio=0x18241C,
                 pecho={(4, 3): 0xF8D97C, (3, 4): 0xD4A83A, (4, 4): 0x5BE38A, (5, 4): 0x9A7420, (4, 5): 0xD4A83A}),
    'vendaval': dict(contorno=0x0B0A20, hombro=[0xEEE2FF, 0xBF9CFF, 0x8E5CFF], peto=[0x46529A, 0x343C7C, 0x272D62],
                     cinto=[0xBF9CFF, 0x8E5CFF], vacio=0x1A1838,
                     pecho={(4, 3): 0xBF9CFF, (4, 4): 0xB8F0FF, (4, 5): 0x5CC8FF}),
    'solar': dict(contorno=0x110B0D, hombro=[0xFFD77A, 0xE8A83A, 0xC07C22], peto=[0x62504C, 0x4A3B3B, 0x382C2E],
                  cinto=[0xE8A83A, 0xC07C22], vacio=0x241A1A,
                  pecho={(4, 3): 0xE8A83A, (3, 4): 0xFF8A1E, (4, 4): 0xFFF0B0, (5, 4): 0xE8A83A, (4, 5): 0xC07C22}),
    'hazmat': dict(contorno=0x1B1B1B, hombro=[0xFFE680, 0xFFD84F, 0xDA9C00], peto=[0xFFD84F, 0xFFCA47, 0xCC8C02],
                   cinto=[0x2D2D2D, 0x242424], vacio=0x2E2A1C,
                   pecho={(3, 3): 0x2D2D2D, (3, 4): 0x2D2D2D, (3, 5): 0x2D2D2D, (3, 6): 0x2D2D2D,
                          (5, 3): 0x242424, (5, 4): 0x242424, (5, 5): 0x242424, (5, 6): 0x242424}),
}


# ----------------------------------------------------------------------
#  La silueta de vanilla
# ----------------------------------------------------------------------

def jar():
    js = [j for j in glob.glob(os.path.join(RAIZ, '.gradle/loom-cache/minecraftMaven/**/minecraft-clientOnly-*.jar'),
                               recursive=True) if 'sources' not in j]
    assert js, 'no encuentro el jar del cliente'
    return zipfile.ZipFile(js[0])


JAR = jar()


def vanilla(ruta):
    return Image.open(io.BytesIO(JAR.read('assets/minecraft/textures/gui/sprites/' + ruta + '.png'))).convert('RGBA')


_lleno = vanilla('hud/armor_full')
CONTORNO = {(x, y) for y in range(9) for x in range(9) if _lleno.getpixel((x, y))[3] > 0
            and _lleno.getpixel((x, y))[0] < 16}
DENTRO = {(x, y) for y in range(9) for x in range(9) if _lleno.getpixel((x, y))[3] > 0} - CONTORNO
HOMBROS = {(x, y) for (x, y) in DENTRO if y <= 2} | {(1, 3), (7, 3)}
CINTO = {(x, y) for (x, y) in DENTRO if y == 7}
PETO = DENTRO - HOMBROS - CINTO
# La raya del medio en el medio icono (como vanilla): de la fila 2 a la 7.
RAYA = {(4, y) for y in range(2, 8)}


def pinta(conj, fase=None):
    """El icono lleno; "fase" (0 a 1) es por donde va el brillo (None: sin brillo)."""
    c = CONJUNTOS[conj]
    hombro = [hexa(v) for v in c['hombro']]
    peto = [hexa(v) for v in c['peto']]
    cinto = [hexa(v) for v in c['cinto']]
    im = Image.new('RGBA', (9, 9), (0, 0, 0, 0))
    for p in CONTORNO:
        im.putpixel(p, hexa(c['contorno']) + (255,))
    for (x, y) in DENTRO:
        if (x, y) in HOMBROS:
            # La luz arriba a la izquierda de cada hombrera; los brazos, en sombra.
            col = hombro[0] if (x, y) in ((1, 1), (5, 2)) or (x, y) == (6, 1) else \
                hombro[2] if (x, y) in ((1, 3), (7, 3), (3, 2), (7, 2)) else hombro[1]
        elif (x, y) in CINTO:
            col = cinto[1] if x >= 5 else cinto[0]
        else:
            col = peto[0] if x == 2 else peto[2] if x == 6 or y == 6 else peto[1]
        if (x, y) in c['pecho']:
            col = hexa(c['pecho'][(x, y)])
        if fase is not None:
            # Un brillo en diagonal que baja de arriba a la izquierda.
            d = (x + y) / 14.0 - (fase * 1.5 - 0.2)
            k = max(0.0, 1.0 - abs(d) / 0.1)
            if k > 0:
                col = mezcla(col, mezcla(hombro[0], (255, 255, 255), 0.4), 0.65 * k)
        im.putpixel((x, y), col + (255,))
    return im


def vacio(conj):
    c = CONJUNTOS[conj]
    im = Image.new('RGBA', (9, 9), (0, 0, 0, 0))
    for p in CONTORNO:
        im.putpixel(p, hexa(c['contorno']) + (255,))
    for p in DENTRO:
        im.putpixel(p, hexa(c['vacio']) + (255,))
    return im


def medio(lleno, vac, conj):
    im = vac.copy()
    for (x, y) in DENTRO:
        if x < 4:
            im.putpixel((x, y), lleno.getpixel((x, y)))
    for p in RAYA:
        im.putpixel(p, hexa(CONJUNTOS[conj]['contorno']) + (255,))
    return im


# El brillo: 24 cuadros de 2 ticks (2,4 s); pasa en los 9 primeros y luego descansa.
CUADROS = 24
PASA = 9
TICKS_CUADRO = 2


def fases():
    return [min(1.0, i / PASA) if i < PASA else None for i in range(CUADROS)]


def sprites(conj):
    """Cada sprite como tira vertical de cuadros (el lleno y el medio, animados) y el vacio quieto."""
    vac = vacio(conj)
    llenos = [pinta(conj, f) for f in fases()]
    medios = [medio(l, vac, conj) for l in llenos]
    s = {}
    for nombre, cuadros in (('full', llenos), ('half', medios)):
        tira = Image.new('RGBA', (9, 9 * CUADROS), (0, 0, 0, 0))
        for i, cu in enumerate(cuadros):
            tira.paste(cu, (0, 9 * i))
        s[nombre] = tira
    s['empty'] = vac
    return s, llenos, medios, vac


def escribir():
    dest = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/sprites/hud/armor')
    os.makedirs(dest, exist_ok=True)
    for conj in CONJUNTOS:
        s, _, _, _ = sprites(conj)
        for nombre, im in s.items():
            p = os.path.join(dest, f'{conj}_{nombre}.png')
            im.save(p)
            if im.height > 9:
                with open(p + '.mcmeta', 'w', encoding='utf-8', newline='\n') as f:
                    json.dump({'animation': {'frametime': TICKS_CUADRO, 'interpolate': False}}, f, indent=2)
                    f.write('\n')
    print('iconos de armadura en', dest)


# ----------------------------------------------------------------------
#  La ficha
# ----------------------------------------------------------------------

FOTO = os.path.join(RAIZ, 'run/screenshots/presenta_rajang_10_jugador.png')
GUI = 2


def hud(armadura, puntos=20, vida=20):
    """El HUD de supervivencia a escala de interfaz, encima de la foto; armadura: (lleno, medio, vacio)."""
    fondo = Image.open(FOTO).convert('RGBA')
    gw, gh = fondo.width // GUI, fondo.height // GUI
    g = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
    x0 = gw // 2 - 91
    g.alpha_composite(vanilla('hud/hotbar'), (x0, gh - 22))
    g.alpha_composite(vanilla('hud/hotbar_selection'), (x0 - 1, gh - 23))
    g.alpha_composite(vanilla('hud/experience_bar_background'), (x0, gh - 29))
    lleno, med, vac = armadura
    for i in range(10):
        x = x0 + i * 8
        icono = lleno if puntos >= 2 * i + 2 else med if puntos == 2 * i + 1 else vac
        g.alpha_composite(icono, (x, gh - 49))
        g.alpha_composite(vanilla('hud/heart/container'), (x, gh - 39))
        if vida >= 2 * i + 2:
            g.alpha_composite(vanilla('hud/heart/full'), (x, gh - 39))
        g.alpha_composite(vanilla('hud/food_full'), (x0 + 182 - 9 - i * 8, gh - 39))
    g = g.resize((gw * GUI, gh * GUI), Image.NEAREST)
    fondo.alpha_composite(g)
    w, h = fondo.size
    r = fondo.convert('RGB').crop((w // 2 - 200, h - 120, w // 2 + 200, h))
    return r.resize((r.width * 2, r.height * 2), Image.NEAREST)


def ampliado(lleno, med, vac, k=12):
    out = Image.new('RGBA', (34, 22), (0, 0, 0, 0))
    for fila, fondo in enumerate(((44, 44, 48), (132, 170, 255))):
        for i, icono in enumerate((lleno, med, vac)):
            c = Image.new('RGBA', (11, 11), fondo + (255,))
            c.alpha_composite(icono, (1, 1))
            out.paste(c, (i * 11 + (1 if i else 0), fila * 11))
    return out.resize((out.width * k, out.height * k), Image.NEAREST)


def ficha():
    os.makedirs(FICHA, exist_ok=True)
    van = (vanilla('hud/armor_full'), vanilla('hud/armor_half'), vanilla('hud/armor_empty'))
    hud(van).save(os.path.join(FICHA, 'armadura_vanilla_hud.png'))
    for conj in CONJUNTOS:
        _, llenos, medios, vac = sprites(conj)
        hud((llenos[-1], medios[-1], vac)).save(os.path.join(FICHA, f'armadura_{conj}_hud.png'))
        cuadros = [hud((l, m, vac), puntos=15) for l, m in zip(llenos, medios)]
        cuadros[0].save(os.path.join(FICHA, f'armadura_{conj}_hud.gif'), save_all=True, append_images=cuadros[1:],
                        duration=TICKS_CUADRO * 50, loop=0)
        grandes = [ampliado(l, m, vac) for l, m in zip(llenos, medios)]
        grandes[0].save(os.path.join(FICHA, f'armadura_{conj}_iconos.gif'), save_all=True, append_images=grandes[1:],
                        duration=TICKS_CUADRO * 50, loop=0, disposal=2)
        ampliado(llenos[-1], medios[-1], vac).save(os.path.join(FICHA, f'armadura_{conj}_iconos.png'))
    print('ficha en', FICHA)


if __name__ == '__main__':
    if FICHA:
        ficha()
    else:
        escribir()
