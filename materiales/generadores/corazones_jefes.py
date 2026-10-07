"""
Los corazones del jugador en combate con un jefe (CorazonesJefe, en el cliente).

Uso: python corazones_jefes.py <raiz del proyecto> [--opcion=A|B|C] [--ficha=carpeta]

Sin --ficha escribe los sprites de la opcion elegida en
assets/atalaya/textures/gui/sprites/hud/heart/<jefe>_*.png (y sus .mcmeta si
van animados). Con --ficha pinta las tres opciones, para elegir, en esa
carpeta: los sprites ampliados, el HUD de mentira encima de una foto del
combate y, la animada, en GIF.

Lo que no se toca (DISENO.md, punto 19): el ROJO del relleno es la vida y se
queda rojo. Los de veneno (verde), congelado (cian), absorcion (oro) y wither
(negro) dicen otra cosa con su color; si los de un jefe fueran cian o dorados se
confundirian. El jefe se lee en el MARCO (y en el brillo).

La silueta es la de vanilla (el hueco, container.png, y el relleno, full.png,
que se pinta encima), sacada del jar: asi el medio corazon y el temblor encajan
igual que en vanilla. El lienzo es de 9 x 9 y no se puede salir: el juego lo
pinta en un cuadro fijo.

  A  Filo: el contorno de 1 px con la rampa del jefe (claro arriba, hondo
     abajo); el relleno rojo de vanilla, con el brillo del color del jefe.
  B  Engastado: contorno casi negro y un aro de 1 px del jefe; dentro, una gema
     roja mas pequena con su brillo. Mas de jefe, menos rojo.
  C  Engastado vivo: B, y el aro se mueve (Nerea, una ola que baja; Aeralis,
     una rafaga que cruza; Rajang, un pulso lento; Novilis, brasas).
"""
import glob
import io
import json
import math
import os
import random
import sys
import zipfile

from PIL import Image

RAIZ = next((a for a in sys.argv[1:] if not a.startswith('--')), '../..')
# Juan eligio la C el 07-10-2026 (la que va en el mod); A y B quedan para la ficha.
OPCION = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--opcion=')), 'C')
FICHA = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--ficha=')), None)

JEFES = ['nerea', 'aeralis', 'rajang', 'novilis']


def hexa(c):
    return ((c >> 16) & 255, (c >> 8) & 255, c & 255)


def mezcla(a, b, k):
    return tuple(round(a[i] * (1 - k) + b[i] * k) for i in range(3))


# La rampa de cada jefe, de claro a hondo, el fondo del hueco y su brillo.
PALETA = {
    # Nerea: de cian arriba a su morado abajo (sus dos colores).
    'nerea': dict(rampa=[0xA6F7FF, 0x3FD6F5, 0x2C7FC8, 0x5A2A8C], hueco=0x0F2230, brillo=0xDDFDFF),
    # Aeralis: plata palida, de cian a lila.
    'aeralis': dict(rampa=[0xEEFBFF, 0xB3D4FF, 0x8F7AE6, 0x45368A], hueco=0x1D1B31, brillo=0xFFFFFF),
    # Rajang: el oro arriba y el jade abajo.
    'rajang': dict(rampa=[0xF8DC80, 0x5BE38A, 0x26A05E, 0x0F5232], hueco=0x0F2619, brillo=0xFFE9A0),
    # Novilis: oro que se quema hacia abajo.
    'novilis': dict(rampa=[0xFFF0A6, 0xFFC23A, 0xD8701A, 0x7A2810], hueco=0x2A1610, brillo=0xFFF5CC),
}
# El rojo de la vida: el de vanilla (ff1313 y bb1313) con un claro y un hondo.
ROJO_CLARO = hexa(0xFF6A55)
ROJO = hexa(0xFF1313)
ROJO_SOMBRA = hexa(0xBB1313)
ROJO_HONDO = hexa(0x7E0C14)
# Al parpadear (recibir dano) vanilla aclara: ffa1a1, dea1a1, ffe3e3.
PALIDO = hexa(0xFFA1A1)
PALIDO_SOMBRA = hexa(0xDEA1A1)
PALIDO_CLARO = hexa(0xFFE3E3)


# ----------------------------------------------------------------------
#  Lo de vanilla: la silueta y el HUD de mentira
# ----------------------------------------------------------------------

def jar():
    js = [j for j in glob.glob(os.path.join(RAIZ, '.gradle/loom-cache/minecraftMaven/**/minecraft-clientOnly-*.jar'),
                               recursive=True) if 'sources' not in j]
    assert js, 'no encuentro el jar del cliente'
    return zipfile.ZipFile(js[0])


JAR = jar()


def vanilla(ruta):
    return Image.open(io.BytesIO(JAR.read('assets/minecraft/textures/gui/sprites/' + ruta + '.png'))).convert('RGBA')


def mascara(im, cond):
    return {(x, y) for y in range(im.height) for x in range(im.width) if cond(im.getpixel((x, y)))}


_hueco = vanilla('hud/heart/container')
_lleno = vanilla('hud/heart/full')
CONTORNO = mascara(_hueco, lambda p: p[3] > 0 and p[0] < 16)
DENTRO = mascara(_hueco, lambda p: p[3] > 0 and p[0] >= 16)
RELLENO = mascara(_lleno, lambda p: p[3] > 0)
assert RELLENO <= DENTRO | CONTORNO
# El aro: lo del relleno que toca algo que no es relleno (vecindad-4, DISENO.md 14).
ARO = {(x, y) for (x, y) in RELLENO if any((x + dx, y + dy) not in RELLENO
                                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
GEMA = RELLENO - ARO
MITAD = 4  # el medio corazon de vanilla llega hasta la columna 4


def luz(x, y):
    """De 0 (arriba a la izquierda, donde da la luz) a 1 (la punta de abajo)."""
    return max(0.0, min(1.0, (y - 0.5) / 7.5 * 0.8 + (x - 1) / 7.0 * 0.2))


def tono(rampa, x, y, mas=0.0):
    k = max(0.0, min(0.999, luz(x, y) + mas))
    return rampa[int(k * len(rampa))]


def lienzo():
    return Image.new('RGBA', (9, 9), (0, 0, 0, 0))


def pon(im, x, y, c, a=255):
    im.putpixel((x, y), tuple(c) + (a,))


# ----------------------------------------------------------------------
#  Las tres opciones
# ----------------------------------------------------------------------

def rampa_de(jefe):
    return [hexa(c) for c in PALETA[jefe]['rampa']]


def gema_roja(im, palido=False, brillo=None, celdas=GEMA):
    """El rojo de dentro, con su volumen: claro arriba a la izquierda, hondo en la punta."""
    for (x, y) in celdas:
        k = luz(x, y)
        if palido:
            c = PALIDO_SOMBRA if k > 0.62 else PALIDO
        else:
            c = ROJO_HONDO if k > 0.8 else ROJO_SOMBRA if k > 0.6 else ROJO if k > 0.18 else ROJO_CLARO
        pon(im, x, y, c)
    if brillo is not None:
        # El brillo del jefe donde vanilla tiene el suyo.
        pon(im, 2, 2, PALIDO_CLARO if palido else brillo)


def opcion_a(jefe, fase=None):
    r = rampa_de(jefe)
    hueco = hexa(PALETA[jefe]['hueco'])
    brillo = hexa(PALETA[jefe]['brillo'])
    s = {}
    for parp in (False, True):
        im = lienzo()
        for (x, y) in CONTORNO:
            c = tono(r, x, y)
            pon(im, x, y, mezcla(c, (255, 255, 255), 0.75) if parp else c)
        for (x, y) in DENTRO:
            pon(im, x, y, hueco)
        s['container' + ('_blinking' if parp else '')] = im
        im = lienzo()
        # El relleno de vanilla, con un hondo en la punta y el brillo del jefe.
        for (x, y) in RELLENO:
            k = luz(x, y)
            borde = (x, y) in ARO and k > 0.5
            if parp:
                c = PALIDO_SOMBRA if borde else PALIDO
            else:
                c = ROJO_HONDO if (x, y) == (4, 7) else ROJO_SOMBRA if borde else ROJO
            pon(im, x, y, c)
        pon(im, 2, 2, PALIDO_CLARO if parp else brillo)
        s['full' + ('_blinking' if parp else '')] = im
    return medios(s)


def aro_de(jefe, parp, x, y, fase=None):
    """El color del aro del jefe en (x, y); "fase" (0 a 1) mueve el brillo en la C."""
    r = rampa_de(jefe)
    mas = 0.0
    luzextra = 0.0
    if fase is not None:
        if jefe == 'nerea':
            # Una ola que baja por el aro.
            d = y / 8.0 - (fase * 1.6 - 0.3)
            luzextra = max(0.0, 1.0 - abs(d) / 0.16)
        elif jefe == 'aeralis':
            # Una rafaga que lo cruza de izquierda a derecha, inclinada.
            d = (x + (8 - y) * 0.5) / 12.0 - (fase * 1.6 - 0.3)
            luzextra = max(0.0, 1.0 - abs(d) / 0.12)
        elif jefe == 'rajang':
            # Un pulso lento: todo el aro sube y baja.
            luzextra = 0.5 * (0.5 - 0.5 * math.cos(fase * 2 * math.pi))
        elif jefe == 'novilis':
            # Brasas: cada pixel parpadea a su aire.
            g = random.Random(x * 31 + y * 7 + int(fase * 12) * 101)
            mas = -0.25 if g.random() < 0.3 else 0.0
    c = tono(r, x, y, mas)
    if luzextra > 0:
        c = mezcla(c, r[0], min(1.0, luzextra))
        if luzextra > 0.85:
            c = mezcla(c, hexa(PALETA[jefe]['brillo']), 0.5)
    if parp:
        c = mezcla(c, (255, 255, 255), 0.6)
    return c


def opcion_b(jefe, fase=None):
    r = rampa_de(jefe)
    hueco = hexa(PALETA[jefe]['hueco'])
    brillo = hexa(PALETA[jefe]['brillo'])
    filo = mezcla(r[3], (0, 0, 0), 0.6)
    s = {}
    for parp in (False, True):
        im = lienzo()
        for (x, y) in CONTORNO:
            pon(im, x, y, (255, 255, 255) if parp else filo)
        for (x, y) in DENTRO:
            pon(im, x, y, aro_de(jefe, parp, x, y, fase) if (x, y) in ARO else hueco)
        s['container' + ('_blinking' if parp else '')] = im
        im = lienzo()
        for (x, y) in ARO:
            pon(im, x, y, aro_de(jefe, parp, x, y, fase))
        gema_roja(im, parp, brillo)
        s['full' + ('_blinking' if parp else '')] = im
    return medios(s)


def medios(s):
    """El medio corazon: la mitad izquierda del lleno (como en vanilla)."""
    for parp in ('', '_blinking'):
        lleno = s['full' + parp]
        im = lienzo()
        for y in range(9):
            for x in range(MITAD + 1):
                im.putpixel((x, y), lleno.getpixel((x, y)))
        s['half' + parp] = im
    return s


# La animacion de la C: 24 cuadros de 2 ticks (1,2 s). Rajang, mas lento.
CUADROS = 24
TICKS_CUADRO = {'nerea': 2, 'aeralis': 2, 'rajang': 3, 'novilis': 2}
# En Nerea y Aeralis el brillo pasa en los 10 primeros cuadros y el resto descansa.
PASA = 10


def fase_de(jefe, i):
    if jefe in ('nerea', 'aeralis'):
        return min(1.0, i / PASA) if i < PASA else 1.5
    return i / CUADROS


def opcion_c(jefe):
    """Cada sprite como una tira vertical de cuadros (lo que pide un .mcmeta)."""
    cuadros = [opcion_b(jefe, fase_de(jefe, i)) for i in range(CUADROS)]
    s = {}
    for nombre in cuadros[0]:
        tira = Image.new('RGBA', (9, 9 * CUADROS), (0, 0, 0, 0))
        for i, c in enumerate(cuadros):
            tira.paste(c[nombre], (0, 9 * i))
        s[nombre] = tira
    return s, cuadros


def sprites(opcion, jefe):
    if opcion == 'A':
        return opcion_a(jefe), None
    if opcion == 'B':
        return opcion_b(jefe), None
    return opcion_c(jefe)


# ----------------------------------------------------------------------
#  Escribir en el mod
# ----------------------------------------------------------------------

def escribir():
    dest = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/sprites/hud/heart')
    os.makedirs(dest, exist_ok=True)
    for j in JEFES:
        s, _ = sprites(OPCION, j)
        for nombre, im in s.items():
            p = os.path.join(dest, f'{j}_{nombre}.png')
            im.save(p)
            meta = p + '.mcmeta'
            if OPCION == 'C':
                with open(meta, 'w', encoding='utf-8', newline='\n') as f:
                    json.dump({'animation': {'frametime': TICKS_CUADRO[j], 'interpolate': False}}, f, indent=2)
                    f.write('\n')
            elif os.path.exists(meta):
                os.remove(meta)
    print('corazones', OPCION, 'en', dest)


# ----------------------------------------------------------------------
#  La ficha: el HUD de mentira sobre una foto del combate
# ----------------------------------------------------------------------

FOTOS = os.path.join(RAIZ, 'run/screenshots')
ESCALA_GUI = 2  # las fotos son de 854 x 480 a escala 2


def hud(foto, s, vida=15, sel=0):
    """El HUD de supervivencia (a escala de interfaz) encima de la foto."""
    fondo = Image.open(foto).convert('RGBA')
    gw, gh = fondo.width // ESCALA_GUI, fondo.height // ESCALA_GUI
    g = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
    x0 = gw // 2 - 91
    g.alpha_composite(vanilla('hud/hotbar'), (x0, gh - 22))
    g.alpha_composite(vanilla('hud/hotbar_selection'), (x0 - 1 + sel * 20, gh - 23))
    g.alpha_composite(vanilla('hud/experience_bar_background'), (x0, gh - 29))
    for i in range(10):
        x = x0 + i * 8
        g.alpha_composite(vanilla('hud/armor_full'), (x, gh - 49))
        g.alpha_composite(s['container'], (x, gh - 39))
        if vida >= 2 * i + 2:
            g.alpha_composite(s['full'], (x, gh - 39))
        elif vida == 2 * i + 1:
            g.alpha_composite(s['half'], (x, gh - 39))
        g.alpha_composite(vanilla('hud/food_full'), (x0 + 182 - 9 - i * 8, gh - 39))
    g = g.resize((gw * ESCALA_GUI, gh * ESCALA_GUI), Image.NEAREST)
    fondo.alpha_composite(g)
    return fondo.convert('RGB')


def vanilla_s():
    return {n: vanilla('hud/heart/' + n) for n in ('container', 'full', 'half')}


def ampliado(s, k=12):
    """Lleno, medio, hueco, y los tres al parpadear, ampliados sobre gris oscuro y sobre cielo."""
    nombres = [('container', 'full'), ('container', 'half'), ('container', None),
               ('container_blinking', 'full_blinking'), ('container_blinking', 'half_blinking')]
    w = len(nombres) * 11 + 1
    out = Image.new('RGBA', (w, 22), (0, 0, 0, 0))
    for fila, fondo in enumerate(((44, 44, 48), (132, 170, 255))):
        for i, (h, f) in enumerate(nombres):
            c = Image.new('RGBA', (11, 11), fondo + (255,))
            c.alpha_composite(s[h], (1, 1))
            if f:
                c.alpha_composite(s[f], (1, 1))
            out.paste(c, (i * 11, fila * 11))
    return out.resize((out.width * k, out.height * k), Image.NEAREST)


def recorte_hud(im):
    """El trozo de abajo con los corazones, a 2x."""
    w, h = im.size
    r = im.crop((w // 2 - 200, h - 120, w // 2 + 200, h))
    return r.resize((r.width * 2, r.height * 2), Image.NEAREST)


def ficha():
    os.makedirs(FICHA, exist_ok=True)
    datos = {}
    for j in JEFES:
        foto = os.path.join(FOTOS, f'presenta_{j}_9_jugador.png')
        hud(foto, vanilla_s()).save(os.path.join(FICHA, f'vanilla_{j}.jpg'), quality=92)
        recorte_hud(hud(foto, vanilla_s())).save(os.path.join(FICHA, f'vanilla_{j}_hud.png'))
        for op in 'ABC':
            s, cuadros = sprites(op, j)
            base = {k: (v.crop((0, 0, 9, 9)) if v.height > 9 else v) for k, v in s.items()}
            hud(foto, base).save(os.path.join(FICHA, f'{op}_{j}.jpg'), quality=92)
            recorte_hud(hud(foto, base)).save(os.path.join(FICHA, f'{op}_{j}_hud.png'))
            ampliado(base).save(os.path.join(FICHA, f'{op}_{j}_sprites.png'))
            if cuadros:
                # El GIF: el recorte del HUD, cuadro a cuadro, al ritmo del juego (20 ticks/s).
                frames = [recorte_hud(hud(foto, c)) for c in cuadros]
                frames[0].save(os.path.join(FICHA, f'{op}_{j}_hud.gif'), save_all=True, append_images=frames[1:],
                               duration=TICKS_CUADRO[j] * 50, loop=0)
                big = [ampliado(c, 10) for c in cuadros]
                big[0].save(os.path.join(FICHA, f'{op}_{j}_sprites.gif'), save_all=True, append_images=big[1:],
                            duration=TICKS_CUADRO[j] * 50, loop=0, disposal=2)
    print('ficha en', FICHA)


if __name__ == '__main__':
    if FICHA:
        ficha()
    else:
        escribir()
