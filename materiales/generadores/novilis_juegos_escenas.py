"""
Renders de la cuarta ficha de minijuegos de Novilis (octubre de 2026). De la
tercera Juan se quedo solo con la Forja del Juramento: "crea mas, sorprendeme".
Esta vez, juegos que todo el mundo conoce (como le gustaron en Rajang: el
puntero laser, Among Us, TNT Run) jugados contra un caballero de leyenda, en
el Altar del Sol y con las ayudas de novilis_mecanicas_escenas:

  manda      El Caballero Manda (Simon dice): alza la espada y sobre el, el
             estandarte con la orden; cuatro se arrodillan, uno no y arde
  mediodia   Duelo al Mediodia (desenfundar): el sol en lo alto, un "!" enorme;
             uno desenfunda a tiempo, otro se adelanto y arde
  mesa       La Mesa Redonda (sillas musicales): la mesa de piedra con fuego,
             los tronos de oro, los angeles tocando; uno se queda sin trono y le
             cae el rayo de su sol
  laberinto  El Laberinto del Sol (Pac-Man): un laberinto de muros con brasas,
             soles de oro por los pasillos, cuatro fuegos fatuos; uno se come
             el sol grande y dos huyen azules
  raya       Tres en Raya: el tablero de fuego en el suelo; los estandartes del
             grupo y los soles de el; uno golpea el estandarte de la tercera

Quinta ficha (de la cuarta Juan se quedo con El Caballero Manda, sin "dadme la
espalda"; faltan las fases III y IV):

  llamas     Las Cuatro Llamas (el Simon de las luces): cuatro braseros de
             colores; el enciende el azul (la secuencia) y uno golpea el rojo
  angeles    Los Angeles de Marmol (se mueven si nadie los mira): dos quietos
             porque los miran; otro, a la espalda de uno, alza la trompeta
  caliente   Frio o Caliente: sus brasas enterradas; cada uno con su termometro;
             uno, "ardiendo", cava donde brilla la grieta
  piedra     Piedra, Papel o Tijera: su puno en alto con la piedra de fuego; los
             jugadores con lo suyo encima; los de papel le ganan
  gallinita  Gallinita Ciega: la venda en el yelmo; se gira con la espada hacia
             el ruido; detras, dos agachados y uno que le pega en la espalda

Uso: python novilis_juegos_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import novilis_mecanicas_escenas as nme  # lee la raiz y la carpeta de salida de sys.argv
from novilis_mecanicas_escenas import (fe, fm, nm, ne, vr, SS, TAU, FUENTE, ORO, ORO_CLARO, BRASA, ROJO, BLANCO, SOMBRA,
                                       pose, caballero, jugador, rotulo, cifra, acabar, guardar, marco_camara, resplandor,
                                       arde, haz_oro, modelo_en, en_mano, bola_de_fuego, rayos_sol, sprite_item)

AZUL = (110, 170, 255)
AZUL_CLARO = (205, 228, 255)
ROJO_CLARO = (255, 170, 150)
VERDE = (150, 240, 120)

# El jugador de Minecraft (nerea_escenas): cuerpo, cabeza, brazos bi/bd y piernas pi/pd; Y hacia abajo.
AGACHADO = {'cuerpo': {'rot': (28, 0, 0)}, 'bi': {'rot': (-20, 0, -6)}, 'bd': {'rot': (-20, 0, 6)},
            'pi': {'rot': (-8, 0, 0)}, 'pd': {'rot': (8, 0, 0)}}
QUIETO = {'bi': {'rot': (-6, 0, -4)}, 'bd': {'rot': (6, 0, 4)}}
CORRE = {'pi': {'rot': (-38, 0, 0)}, 'pd': {'rot': (38, 0, 0)}, 'bi': {'rot': (42, 0, 0)}, 'bd': {'rot': (-42, 0, 0)}}
GOLPE = {'bd': {'rot': (-115, -20, 0)}, 'bi': {'rot': (-10, 0, -8)}, 'pi': {'rot': (-15, 0, 0)}, 'pd': {'rot': (15, 0, 0)}}
DESENFUNDA = {'bd': {'rot': (-80, -30, 0)}, 'bi': {'rot': (-14, 0, -10)}, 'pi': {'rot': (-24, 0, 0)}, 'pd': {'rot': (20, 0, 0)},
              'cuerpo': {'rot': (8, 0, 0)}}
SENTADO = {'pi': {'rot': (-90, 0, -4)}, 'pd': {'rot': (-90, 0, 4)}, 'bi': {'rot': (-30, 0, -6)}, 'bd': {'rot': (-30, 0, 6)}}
SALTA = {'pi': {'rot': (-30, 0, -4)}, 'pd': {'rot': (14, 0, 4)}, 'bi': {'rot': (-150, 0, -24)}, 'bd': {'rot': (-140, 0, 26)}}
BRAZOS_ARRIBA = {'bi': {'rot': (-160, 0, -25)}, 'bd': {'rot': (-150, 0, 30)}, 'pi': {'rot': (12, 0, -6)}, 'pd': {'rot': (-12, 0, 6)}}


def fuente(tam):
    return ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)


def texto(d, xy, t, f, color, sombra=3):
    for o in ((sombra, sombra), (sombra - 1, sombra - 1), (-1, 1)):
        d.text((xy[0] + o[0], xy[1] + o[1]), t, font=f, fill=(*SOMBRA, 255))
    d.text(xy, t, font=f, fill=(*color, 255))


def pastilla(img, x, y, t, tam=24, color=ORO_CLARO, fondo=(32, 16, 10, 210), borde=ORO, centro=False):
    """Una pastilla de texto (los chips de las ordenes, el marcador)."""
    d = ImageDraw.Draw(img)
    f = fuente(tam)
    w = d.textlength(t, font=f)
    if centro:
        x -= (w + tam) / 2
    caja = (x, y, x + w + tam, y + tam * 1.55)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    dc.rounded_rectangle((caja[0] + 3, caja[1] + 3, caja[2] + 3, caja[3] + 3), radius=tam * 0.4, fill=(*SOMBRA, 150))
    dc.rounded_rectangle(caja, radius=tam * 0.4, fill=fondo, outline=(*borde, 255), width=2)
    img.alpha_composite(capa)
    d.text((x + tam / 2, y + tam * 0.18), t, font=f, fill=(*color, 255))
    return caja


def estandarte_orden(img, cx, y, linea1, linea2, ancho=None):
    """El estandarte con la orden, colgado arriba: pano carmesi con flecos de oro y el sol bordado."""
    d = ImageDraw.Draw(img)
    f1, f2 = fuente(30), fuente(64)
    w = max(d.textlength(linea1, font=f1), d.textlength(linea2, font=f2)) + 90 if ancho is None else ancho
    x0, x1 = cx - w / 2, cx + w / 2
    alto = 150
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    # la vara de oro y el pano con su cola en pico
    dc.rectangle((x0 - 24, y - 10, x1 + 24, y + 2), fill=(*ORO, 255), outline=(120, 74, 20, 255), width=2)
    for xx in (x0 - 24, x1 + 24):
        dc.ellipse((xx - 11, y - 15, xx + 11, y + 7), fill=(*ORO_CLARO, 255), outline=(120, 74, 20, 255), width=2)
    pano = [(x0, y + 2), (x1, y + 2), (x1, y + alto), (cx, y + alto + 34), (x0, y + alto)]
    dc.polygon([(px + 5, py + 6) for px, py in pano], fill=(*SOMBRA, 140))
    dc.polygon(pano, fill=(120, 22, 18, 245), outline=(*ORO, 255))
    dc.line([(x0 + 10, y + 12), (x1 - 10, y + 12)], fill=(*ORO, 255), width=3)
    dc.line([(x0 + 10, y + alto - 10), (cx, y + alto + 22), (x1 - 10, y + alto - 10)], fill=(*ORO, 255), width=3)
    for k in range(int(w // 14)):                      # los flecos
        xx = x0 + 7 + k * 14
        if xx > x1 - 4:
            break
        yb = y + alto + (34 * (1 - abs(xx - cx) / (w / 2)))
        dc.line([(xx, yb - 2), (xx, yb + 10)], fill=(*ORO, 230), width=3)
    img.alpha_composite(capa)
    d.text((cx - d.textlength(linea1, font=f1) / 2, y + 22), linea1, font=f1, fill=(*ORO_CLARO, 255))
    texto(d, (cx - d.textlength(linea2, font=f2) / 2, y + 56), linea2, f2, (255, 236, 190))


# ======================================================================
#  1. El Caballero Manda
# ======================================================================
def manda(W=1600, H=900, fase=1):
    cam = vr.Camara(ojo=(-1.5, 3.4, -24.0), objetivo=(0.6, 7.0, 10.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    N = np.array([1.0, 0.0, 11.0])
    p = pose('GRITO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], -1.0, -12.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.8)
    # los que obedecen, en el aire de cara a el; el que no, en el suelo y ardiendo
    obedecen = ((-6.0, -12.5, 1.2), (-2.6, -15.0, 1.0), (1.4, -12.0, 1.3), (6.2, -14.0, 1.1))
    for x, z, alto in obedecen:
        jugador(lz, cam, x, z, (N[0], N[2]), SALTA, y=alto, niebla=niebla)
        sombra_suelo(lz, cam, x, z)
    rebelde = np.array([3.6, 0.0, -9.6])
    jugador(lz, cam, rebelde[0], rebelde[2], (N[0], N[2]), QUIETO, niebla=niebla)
    arde(lz, cam, rebelde, fase, 1.0, 3)
    img = acabar(lz, cam, W, H, fase, 201)
    estandarte_orden(img, W / 2 + 20, 30, 'EL CABALLERO MANDA:', '«¡POR EL SOL... SALTAD!»')
    rotulo(img, cam, rebelde + np.array([0, 2.4, 0]), 'NO SALTA: ARDE', -70, -110, 40, ROJO_CLARO)
    rotulo(img, cam, np.array([-6.0, 3.4, -12.5]), 'OBEDECEN', -40, -80, 40, ORO_CLARO)
    # las ordenes que puede dar, abajo
    x = 40
    for t in ('ARRODILLAOS (SHIFT)', 'SALTAD', 'MIRAD AL SOL', 'QUIETOS'):
        caja = pastilla(img, x, H - 62, t, 22)
        x = caja[2] + 12
    pastilla(img, W - 230, 34, 'ÓRDENES 3/6', 30)
    guardar(img, 'manda')


def sombra_suelo(lz, cam, x, z, r=0.55, k=0.45):
    """La sombra redonda de vanilla bajo un jugador en el aire."""
    n = 64
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    t = np.zeros((n, n, 4), np.uint8)
    t[..., 3] = (np.clip(1 - d, 0, 1) ** 0.7 * 255 * k).astype(np.uint8)
    fe.trans(lz, cam, fe.suelo_cuad(x, z, r, 0.07), t, 1.0)


# ======================================================================
#  2. Duelo al Mediodia
# ======================================================================
def mediodia(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-1.0, 2.6, -15.0), objetivo=(0.0, 7.4, 6.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase, cerca=20.0)
    N = np.array([8.5, 0.0, 6.0])
    p = pose('REPOSO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], -9.0, 4.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.7)
    # el sol, justo en lo alto
    sol = np.array([0.0, 19.5, 9.0])
    bola_de_fuego(lz, cam, sol, 2.2, 5, 0.6)
    # los retados, en fila de cara a el
    a_tiempo = np.array([-5.4, 0.0, -6.0])
    Mj, pj = jugador(lz, cam, a_tiempo[0], a_tiempo[2], (N[0], N[2]), DESENFUNDA, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'espada', 0.42, 0.5)
    adelanto = np.array([-8.6, 0.0, -1.6])
    jugador(lz, cam, adelanto[0], adelanto[2], (N[0], N[2]), DESENFUNDA, niebla=niebla)
    arde(lz, cam, adelanto, fase, 1.0, 5)
    otro = np.array([-7.2, 0.0, 3.4])
    Mo, po = jugador(lz, cam, otro[0], otro[2], (N[0], N[2]), DESENFUNDA, niebla=niebla)
    en_mano(lz, cam, Mo, po, 'espada', 0.42, 0.5)
    # el tajo de luz del que llega a tiempo, hacia el
    pecho = np.array([N[0] - 1.5, 7.5, N[2] - 0.8])
    haz_oro(lz, cam, [a_tiempo + np.array([0.6, 1.4, 0]), (a_tiempo + pecho) / 2 + np.array([0, 2.0, 0]), pecho], 0.25, 1.3)
    resplandor(lz, cam, pecho, 2.2, ORO, 0.8)
    img = acabar(lz, cam, W, H, fase, 202)
    rayos_sol(img, cam, sol, 2.2, 22, 1.6, ORO_CLARO, 4)
    cifra(img, cam, np.array([0.5, 10.5, 5.0]), '¡!', 230, (255, 236, 160))
    rotulo(img, cam, sol, 'MEDIODÍA: EL SOL EN LO ALTO... SILENCIO', 90, -30, 36, ORO_CLARO, linea=False)
    rotulo(img, cam, a_tiempo + np.array([0, 2.0, 0]), '¡A TIEMPO!', -80, -150, 44, ORO_CLARO)
    rotulo(img, cam, adelanto + np.array([0, 2.3, 0]), 'SE ADELANTÓ: ¡DESHONRA!', 60, -150, 40, ROJO_CLARO)
    rotulo(img, cam, N + np.array([0, 4.0, 0]), 'ESPERA, LA ESPADA BAJA', 60, 120, 34, BLANCO)
    pastilla(img, W / 2, H - 70, 'EN CUANTO SALGA «¡!», CLIC (0,4 s)', 28, centro=True)
    guardar(img, 'mediodia')


# ======================================================================
#  3. La Mesa Redonda
# ======================================================================
fm.registrar('cojin', nme.tex_moteado(((150, 26, 22), (128, 20, 18), (172, 36, 28), (140, 24, 20)), 301))


def trono_modelo():
    """Un trono de oro (px, Y hacia abajo, el asiento mira a -Z): zocalo, cojin, brazos y respaldo con su sol."""
    return nm.nodo('trono', (0, 0, 0), (0, 0, 0), [
        ((-7, -7, -7, 14, 7, 14), 'oro_bloque'),
        ((-6, -8.5, -6, 12, 1.5, 12), 'cojin'),
        ((-8, -14, -6, 2, 7, 12), 'oro_bloque'), ((6, -14, -6, 2, 7, 12), 'oro_bloque'),
        ((-7, -30, 5, 14, 23, 3), 'oro_bloque'),
        ((-5, -27, 4.4, 10, 18, 0.6), 'cojin'),
        ((-3, -35, 5.5, 6, 6, 2), 'magma')])


TRONO = trono_modelo()
ESC_TRONO = 1.35


def mesa(W=1600, H=900, fase=4):
    cam = vr.Camara(ojo=(-6.5, 7.6, -10.5), objetivo=(0.4, 4.6, 5.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    C = np.array([0.0, 0.0, 3.0])
    # la mesa redonda, de bloques (redonda a lo Minecraft): piedra con el canto de oro
    qs = []
    for gx in range(-4, 4):
        for gz in range(-4, 4):
            d = math.hypot(gx + 0.5, gz + 0.5)
            if d > 3.9:
                continue
            x, z = C[0] + gx, C[2] + gz
            qs += fe.caja_mundo(x, 0, z, 1, 0.9, 1, 'basalto_j')
            qs += fe.caja_mundo(x, 0.9, z, 1, 0.2, 1, 'oro_bloque' if d > 2.9 else 'marmol')
    fm.dibujar(lz, cam, qs, fe.LUCES, fe.AMB, niebla, 1.0, fase)
    fe.llamas_en(lz, cam, C + np.array([0, 1.1, 0]), 1.6, fase, 6, 3, 1.2)
    # los tronos alrededor, de cara a la mesa
    sentados = []
    n = 7
    for k in range(n):
        a = TAU * k / n + 0.35
        x, z = C[0] + math.cos(a) * 5.4, C[2] + math.sin(a) * 5.4
        g = fe.guinada_hacia(x, z, C[0], C[2])
        M = modelo_en(x, 0, z, g + 180, 0, ESC_TRONO)
        fm.dibujar(lz, cam, nm.quads(TRONO, {}, M), fe.LUCES, fe.AMB, niebla, 1.0, fase)
        sentados.append((x, z))
    # los angeles tocando en las esquinas
    nota = fe.tex_nota((255, 210, 120))
    r = random.Random(4)
    for a in (35, 145):
        x, z = C[0] + math.cos(math.radians(a)) * 11.0, C[2] + math.sin(math.radians(a)) * 11.0
        Me = fe.dibujar_estatua(lz, cam, x, z, fe.guinada_hacia(x, z, C[0], C[2]) + 180, niebla, fase=fase)
        boca = (Me @ np.array([0, -64, -34, 1.0]))[:3]
        for k in range(5):
            q = boca + (C - boca) * (0.1 + 0.12 * k) + np.array([0, 1.2 + math.sin(k * 1.3 + a) * 0.6, 0])
            fe.aditivo(lz, cam, [fe.billboard(q, 0.55, cam, r.uniform(-0.3, 0.3))], nota, 0.9)
    # Novilis detras, dirigiendo
    N = np.array([1.5, 0.0, 21.0])
    p = pose('CASTIGO_ALZA')
    Mn = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], C[0], C[2]), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, Mn, p, fase, k=0.7)
    # los sentados (todos los tronos menos uno, que lo esta cogiendo uno) y el que se queda sin
    for k, (x, z) in enumerate(sentados):
        hacia = C - np.array([x, 0, z])
        hacia /= np.linalg.norm(hacia)
        if k == 2:
            jugador(lz, cam, x + hacia[0] * 0.9, z + hacia[2] * 0.9, (x, z), CORRE, niebla=niebla, extra=180)
            continue
        jugador(lz, cam, x + hacia[0] * 0.1, z + hacia[2] * 0.1, (C[0], C[2]), SENTADO, y=0.62, niebla=niebla)
    sin = C + np.array([-6.0, 0, -4.2])
    jugador(lz, cam, sin[0], sin[2], (C[0], C[2]), BRAZOS_ARRIBA, niebla=niebla)
    fe.haz_vertical(lz, cam, sin[0], sin[2], 0.42, 0.0, 30.0, fase, 0.65)
    arde(lz, cam, sin, fase, 1.0, 9)
    img = acabar(lz, cam, W, H, fase, 203)
    rotulo(img, cam, C + np.array([0, 1.4, 0]), 'LA MÚSICA PARA: ¡A UN TRONO!', -260, 150, 44, ORO_CLARO)
    rotulo(img, cam, sin + np.array([0, 1.6, 0]), 'SIN TRONO: EL RAYO DE SU SOL', 70, 20, 40, ROJO_CLARO)
    rotulo(img, cam, np.array([C[0] + math.cos(math.radians(35)) * 11.0, 4.5, C[2] + math.sin(math.radians(35)) * 11.0]),
           'LOS ÁNGELES TOCAN', 60, -80, 34, ORO_CLARO)
    pastilla(img, W - 380, 34, 'RONDA 2/3 · UN TRONO MENOS', 26)
    guardar(img, 'mesa')


# ======================================================================
#  4. El Laberinto del Sol
# ======================================================================
LABERINTO = [
    '#####################',
    '#O........#........O#',
    '#.###.###.#.###.###.#',
    '#...................#',
    '#.###.#.#####.#.###.#',
    '#.....#...#...#.....#',
    '#####.###.#.###.#####',
    '#.......     .......#',
    '#####.#.##-##.#.#####',
    '#.....#.......#.....#',
    '#.###.#.#####.#.###.#',
    '#...#...........#...#',
    '###.#.###.#.###.#.###',
    '#O........#........O#',
    '#####################',
]
CELDA = 2.0


def tex_fatuo(color, asustado=False, mira=(1, 0), n=96):
    """Un fuego fatuo con forma del fantasma de Pac-Man: cupula, flecos de llama y los ojos."""
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cuerpo = (60, 100, 255) if asustado else color
    claro = tuple(min(255, int(c * 0.5 + 128)) for c in cuerpo)
    m = n * 0.1
    d.pieslice((m, m, n - m, n * 0.95 - m), 180, 360, fill=(*cuerpo, 255))
    d.rectangle((m, n * 0.45, n - m, n * 0.78), fill=(*cuerpo, 255))
    for k in range(4):                                  # los flecos de abajo, como llamas
        x0 = m + k * (n - 2 * m) / 4
        d.polygon([(x0, n * 0.78), (x0 + (n - 2 * m) / 8, n * 0.92), (x0 + (n - 2 * m) / 4, n * 0.78)], fill=(*cuerpo, 255))
    capa = im.filter(ImageFilter.GaussianBlur(n / 40))
    arr = np.array(capa).astype(float)
    yy = np.mgrid[0:n, 0:n][0] / n
    k = np.clip(0.9 - yy, 0, 1)[..., None] * 0.6         # mas claro arriba, como una llama
    arr[..., :3] = arr[..., :3] * (1 - k) + np.array(claro) * k
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    if asustado:
        for x in (0.36, 0.64):
            d.rectangle((n * x - n * 0.05, n * 0.38, n * x + n * 0.05, n * 0.48), fill=(255, 220, 200, 255))
        d.line([(n * 0.3, n * 0.66), (n * 0.4, n * 0.6), (n * 0.5, n * 0.66), (n * 0.6, n * 0.6), (n * 0.7, n * 0.66)],
               fill=(255, 220, 200, 255), width=max(2, n // 30))
    else:
        for x in (0.36, 0.64):
            d.ellipse((n * x - n * 0.09, n * 0.3, n * x + n * 0.09, n * 0.5), fill=(255, 255, 255, 255))
            px, pz = mira
            d.ellipse((n * x - n * 0.045 + px * n * 0.04, n * 0.36 + pz * n * 0.04, n * x + n * 0.045 + px * n * 0.04,
                       n * 0.45 + pz * n * 0.04), fill=(30, 50, 160, 255))
    return np.array(im)


def laberinto(W=1600, H=900, fase=4):
    cam = vr.Camara(ojo=(0.0, 20.0, -13.0), objetivo=(0.0, 0.0, 10.5), fov=66, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(40, 90)
    fe.suelo(lz, cam, niebla, fase, ext=30, desde=-12, prof=50)
    cols = len(LABERINTO[0])
    assert all(len(f) == cols for f in LABERINTO)
    x0 = -cols * CELDA / 2
    z0 = 22.0

    def centro(c, f):
        return np.array([x0 + (c + 0.5) * CELDA, 0.0, z0 - (f + 0.5) * CELDA])

    qs = []
    grandes = []
    for f, fila in enumerate(LABERINTO):
        for c, ch in enumerate(fila):
            q = centro(c, f)
            if ch in '#-':
                alto = 1.5 if ch == '#' else 0.5
                borde = f in (0, len(LABERINTO) - 1) or c in (0, len(LABERINTO[0]) - 1)
                qs += fe.caja_mundo(q[0] - CELDA / 2, 0, q[2] - CELDA / 2, CELDA, alto, CELDA, 'basalto_j')
                qs += fe.caja_mundo(q[0] - CELDA / 2, alto, q[2] - CELDA / 2, CELDA, 0.15, CELDA,
                                    'oro_bloque' if borde else ('magma' if ch == '-' else 'negra'))
            elif ch == 'O':
                grandes.append(q)
    fm.dibujar(lz, cam, qs, fe.LUCES, fe.AMB, niebla, 1.0, fase)
    moneda = fe.tex_disco((255, 252, 220), (255, 200, 60), 64, 0.5, 1.6)
    comidas = {(5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (1, 3), (2, 3), (3, 3), (4, 3), (1, 4), (1, 5), (1, 2)}
    for f, fila in enumerate(LABERINTO):
        for c, ch in enumerate(fila):
            if ch == '.' and (c, f) not in comidas:
                fe.aditivo(lz, cam, [fe.billboard(centro(c, f) + np.array([0, 0.7, 0]), 0.32, cam)], moneda, 1.0)
    for k, q in enumerate(grandes):
        if k == 1:
            continue                                    # este se lo acaban de comer
        bola_de_fuego(lz, cam, q + np.array([0, 1.0, 0]), 0.6, 11 + k, 0.5)
    # los jugadores por los pasillos
    yo = centro(18, 2)
    jugador(lz, cam, yo[0], yo[2], (yo[0] - 4, yo[2] + 1), CORRE, niebla=niebla)
    resplandor(lz, cam, yo + np.array([0, 1.2, 0]), 3.0, ORO, 0.7)
    for (c, f), mira in (((5, 3), (-1, 0)), ((10, 9), (1, 0)), ((3, 11), (0, -1))):
        q = centro(c, f)
        jugador(lz, cam, q[0], q[2], (q[0] + mira[0] * 4, q[2] - mira[1] * 4), CORRE, niebla=niebla)
    # los fuegos fatuos: dos persiguen, dos huyen azules del que se comio el sol grande
    for (c, f), color, asustado, mira in (((9, 9), (255, 70, 50), False, (1, 0)), ((7, 11), (255, 150, 200), False, (-1, 0)),
                                          ((16, 3), (90, 230, 255), True, (0, 0)), ((14, 4), (255, 170, 60), True, (0, 0))):
        q = centro(c, f) + np.array([0, 1.25, 0])
        fe.trans(lz, cam, [fe.billboard(q + np.array([0, 0.3, 0]), 1.35, cam)], tex_fatuo(color, asustado, mira), 1.0, None, 0.8)
        resplandor(lz, cam, q, 2.2, (60, 100, 255) if asustado else color, 0.5)
    # Novilis al fondo, mirando su laberinto
    N = np.array([0.0, 0.0, 30.0])
    p = pose('REPOSO')
    Mn = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], 0.0, 0.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, Mn, p, fase, k=0.6)
    img = acabar(lz, cam, W, H, fase, 204)
    rotulo(img, cam, yo + np.array([0, 2.0, 0]), 'SOL GRANDE: ¡AHORA HUYEN DE TI!', 40, -110, 38, ORO_CLARO)
    rotulo(img, cam, centro(9, 9) + np.array([0, 2.0, 0]), 'FUEGOS FATUOS: TE PERSIGUEN', -60, 90, 38, (255, 170, 150))
    rotulo(img, cam, centro(12, 1) + np.array([0, 0.8, 0]), 'RECOGED TODOS LOS SOLES', 40, -70, 36, BLANCO)
    pastilla(img, W - 260, 34, 'SOLES 96/150', 30)
    guardar(img, 'laberinto')


# ======================================================================
#  5. Tres en Raya
# ======================================================================
fm.registrar('tela_azul', nme.tex_moteado(((70, 120, 230), (58, 104, 210), (90, 140, 245), (64, 112, 220)), 305))
fm.registrar('tela_blanca', nme.tex_moteado(((236, 230, 216), (222, 214, 198), (246, 242, 230)), 306))


def estandarte(x, z, tela):
    """Un estandarte de la casilla: asta de oro, travesano y el pano (azul: del grupo; blanco: libre)."""
    qs = fe.caja_mundo(x - 0.1, 0, z - 0.1, 0.2, 3.4, 0.2, 'oro_bloque')
    qs += fe.caja_mundo(x - 0.8, 3.2, z - 0.08, 1.6, 0.16, 0.16, 'oro_bloque')
    qs += fe.caja_mundo(x - 0.7, 1.5, z - 0.04, 1.4, 1.7, 0.08, tela)
    qs += fe.caja_mundo(x - 0.25, 3.4, z - 0.25, 0.5, 0.5, 0.5, 'magma')
    return qs


def raya(W=1600, H=900, fase=1):
    cam = vr.Camara(ojo=(1.5, 19.0, -9.5), objetivo=(0.0, 0.0, 7.5), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(34, 80)
    fe.suelo(lz, cam, niebla, fase)
    L = 6.0
    cx, cz = 0.0, 6.0
    # el tablero: losas oscuras bajo las casillas, para que se lea
    fm.dibujar(lz, cam, fe.caja_mundo(cx - 1.5 * L - 0.5, 0.0, cz - 1.5 * L - 0.5, 3 * L + 1, 0.06, 3 * L + 1, 'negra'),
               fe.LUCES, fe.AMB, niebla, 1.0, fase)

    def casilla(c, f):
        return np.array([cx + (c - 1) * L, 0.0, cz + (f - 1) * L])

    # las rayas de fuego del tablero
    for k in (-0.5, 0.5):
        for a, b in (((cx + k * L, cz - 1.5 * L), (cx + k * L, cz + 1.5 * L)), ((cx - 1.5 * L, cz + k * L), (cx + 1.5 * L, cz + k * L))):
            nme.linea_puntos(lz, cam, a, b, BRASA, 0.12, 0.45, 0.45, 0.5, 1.8)
            for t in np.linspace(0.05, 0.95, 9):
                q = np.array([a[0] + (b[0] - a[0]) * t, 0.05, a[1] + (b[1] - a[1]) * t])
                fe.llamas_en(lz, cam, q, 0.6, fase, 2, int(t * 20 + k * 10), 0.6)
    # el estado: el grupo (estandarte azul y la cruz de luz) en dos de la diagonal; los soles de el en dos
    grupo = [(0, 2), (1, 1)]
    suyos = [(2, 1), (0, 1)]
    qs = []
    for c in range(3):
        for f in range(3):
            q = casilla(c, f)
            if (c, f) in suyos:
                continue
            tela = 'tela_azul' if (c, f) in grupo else 'tela_blanca'
            qs += estandarte(q[0] - 2.2, q[2] + 2.2, tela)
    fm.dibujar(lz, cam, qs, fe.LUCES, fe.AMB, niebla, 1.0, fase)
    for c, f in grupo:
        q = casilla(c, f)
        for giro in (45, -45):
            g = math.radians(giro)
            d = np.array([math.cos(g), 0, math.sin(g)]) * 2.4
            haz_oro(lz, cam, [q - d + np.array([0, 0.15, 0]), q + d + np.array([0, 0.15, 0])], 0.6, 1.4, AZUL, AZUL_CLARO)
    for c, f in suyos:
        q = casilla(c, f)
        nme.aro_suelo(lz, cam, q[0], q[2], 2.2, ORO, 0.9, 0.7, 0.09, 0, 0)
        bola_de_fuego(lz, cam, q + np.array([0, 1.0, 0]), 0.75, 21 + c, 0.5)
    # el que golpea el estandarte de la tercera de la diagonal
    ultima = casilla(2, 0)
    banda = ultima + np.array([-2.2, 0, 2.2])
    Mj, pj = jugador(lz, cam, banda[0] - 1.0, banda[2] - 0.9, (banda[0], banda[2]), GOLPE, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'espada', 0.42, 0.9)
    resplandor(lz, cam, banda + np.array([0, 2.2, 0]), 1.8, AZUL, 0.9)
    nme.linea_puntos(lz, cam, (casilla(0, 2)[0], casilla(0, 2)[2]), (ultima[0], ultima[2]), AZUL_CLARO, 0.2, 1.0, 0.55, 0.18, 1.3)
    # otros dos del grupo, mirando
    for x, z in ((-8.5, -4.0), (3.5, -4.8)):
        jugador(lz, cam, x, z, (cx, cz), QUIETO, niebla=niebla)
    # Novilis al fondo lanza su sol a una casilla libre (su sello en el suelo)
    N = np.array([2.0, 0.0, 26.0])
    p = pose('SOL')
    Mn = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], cx, cz), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, Mn, p, fase, k=0.7)
    destino = casilla(2, 2)
    fe.sello(lz, cam, destino[0], destino[2], 2.3, fase)
    vuelo = destino + np.array([1.2, 7.0, 3.5])
    bola_de_fuego(lz, cam, vuelo, 0.9, 31, 0.6)
    img = acabar(lz, cam, W, H, fase, 205)
    rotulo(img, cam, banda + np.array([0, 3.0, 0]), 'TU TURNO: GOLPEA SU ESTANDARTE', -40, -110, 38, AZUL_CLARO)
    rotulo(img, cam, casilla(1, 1) + np.array([0, 0.3, 0]), '¡TRES EN RAYA!', 140, 120, 46, AZUL_CLARO)
    rotulo(img, cam, vuelo, 'SU TURNO: UN SOL A UNA CASILLA', 60, -40, 36, ORO_CLARO)
    pastilla(img, W - 330, 34, 'TURNO DEL GRUPO: 5 s', 30)
    guardar(img, 'raya')


# ======================================================================
#  Quinta ficha
# ======================================================================
def mezcla(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


_LLAMA_COLOR = {}


def tex_llama_color(color, semilla=0):
    """Una lengua de fuego del color dado (como las de fuego_escenas, pero de cualquier color)."""
    k = (color, semilla % 4)
    if k not in _LLAMA_COLOR:
        t = fe.tex_llamas(mezcla(color, (255, 255, 255), 0.75), color, mezcla(color, (0, 0, 0), 0.55), 32, 48,
                         semilla=semilla + 3, densidad=1.3)
        x = np.abs(np.arange(32) - 15.5) / 15.5
        t[..., 3] = (t[..., 3] * np.clip(1.15 - x ** 2 * 1.2, 0, 1)[None, :]).astype(np.uint8)
        _LLAMA_COLOR[k] = t
    return _LLAMA_COLOR[k]


def llamas_color(lz, cam, p, tam, color, n=5, semilla=0, brillo=1.0):
    r = random.Random(semilla)
    p = np.array(p, float)
    for i in range(n):
        q = p + np.array([r.uniform(-0.4, 0.4) * tam, tam * r.uniform(0.6, 1.0), r.uniform(-0.4, 0.4) * tam])
        fe.aditivo(lz, cam, [fe.billboard(q, tam * r.uniform(0.4, 0.6), cam, r.uniform(-0.2, 0.2), alto=tam * r.uniform(0.8, 1.1))],
                   tex_llama_color(color, i + semilla), brillo * 0.9)
    resplandor(lz, cam, p + np.array([0, tam * 0.5, 0]), tam * 1.6, color, 0.45 * brillo)


def puntos_secuencia(img, cx, y, colores, actual, r=26):
    """La secuencia que hay que repetir: un circulo de luz por color; el que toca, mas grande."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    paso = r * 2.8
    x0 = cx - paso * (len(colores) - 1) / 2
    for i, c in enumerate(colores):
        rr = r * (1.25 if i == actual else 1.0)
        x = x0 + i * paso
        d.ellipse((x - rr - 3, y - rr - 3, x + rr + 3, y + rr + 3), fill=(*SOMBRA, 200))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(*c, 255), outline=(*mezcla(c, (255, 255, 255), 0.6), 255), width=3)
    halo = capa.filter(ImageFilter.GaussianBlur(r / 2.5))
    img.alpha_composite(halo)
    img.alpha_composite(capa)


SIMON = {'rojo': (255, 70, 50), 'azul': (80, 150, 255), 'verde': (90, 230, 110), 'amarillo': (255, 214, 60)}


def llamas(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-2.0, 5.2, -18.0), objetivo=(0.5, 5.2, 8.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    braseros = (('amarillo', (8.5, -1.0)), ('verde', (3.2, -4.0)), ('azul', (-3.2, -4.0)), ('rojo', (-8.5, -1.0)))
    N = np.array([0.0, 0.0, 15.0])
    p = pose('SENALA')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], -3.2, -4.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.6)
    alto = 3.0
    for nombre, (x, z) in braseros:
        fm.dibujar(lz, cam, fe.brasero(x, z, alto), fe.LUCES, fe.AMB, niebla, 1.1, fase)
    for nombre, (x, z) in braseros:
        lit = nombre == 'azul'
        llamas_color(lz, cam, (x, alto + 0.7, z), 2.3 if lit else 1.0, SIMON[nombre], 7 if lit else 4, len(nombre),
                     1.5 if lit else 0.6)
        if lit:
            nota = fe.tex_nota(mezcla(SIMON[nombre], (255, 255, 255), 0.4))
            for k in range(5):
                q = np.array([x + math.sin(k * 1.7) * 1.2, alto + 4.0 + k * 1.1, z])
                fe.aditivo(lz, cam, [fe.billboard(q, 0.6, cam, 0.2 * math.sin(k))], nota, 0.9)
    # uno golpea el rojo (el primero de la secuencia); otros dos miran
    rojo = np.array(braseros[3][1])
    Mj, pj = jugador(lz, cam, rojo[0] + 1.6, rojo[1] - 2.0, (rojo[0], rojo[1]), GOLPE, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'espada', 0.42, 0.9)
    resplandor(lz, cam, np.array([rojo[0] + 0.9, 2.2, rojo[1] - 1.0]), 1.6, SIMON['rojo'], 0.8)
    for x, z in ((0.5, -9.0), (5.5, -8.0)):
        jugador(lz, cam, x, z, (-3.2, -4.0), QUIETO, niebla=niebla)
    img = acabar(lz, cam, W, H, fase, 211)
    d = ImageDraw.Draw(img)
    f = fuente(32)
    t = 'REPITE LA SECUENCIA'
    texto(d, (W / 2 - d.textlength(t, font=f) / 2, 24), t, f, ORO_CLARO)
    puntos_secuencia(img, W / 2, 104, [SIMON['rojo'], SIMON['azul'], SIMON['amarillo'], SIMON['azul']], 1)
    rotulo(img, cam, np.array([-3.2, alto + 2.6, -4.0]), 'ÉL ENCIENDE: ¡AZUL!', -60, -60, 40, (190, 215, 255))
    rotulo(img, cam, np.array([rojo[0] + 1.6, 2.0, rojo[1] - 2.0]), 'GOLPEA EN EL MISMO ORDEN', -40, 120, 38, ORO_CLARO)
    pastilla(img, W - 300, 34, 'SECUENCIA 4 DE 6', 30)
    guardar(img, 'llamas')


def estatua_en(lz, cam, x, z, guinada, niebla, fase, esc=1.0, rota=False):
    """Un angel de marmol de las Trompetas, al tamano que se pida (las Trompetas lo ponen a 2,2)."""
    M = vr.T(x, 0, z) @ vr.Ry(math.radians(guinada)) @ vr.S(esc) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    fm.dibujar(lz, cam, nm.quads(fe.estatua(rota), {}, M), fe.LUCES, fe.AMB, niebla, 1.2, fase)
    return M


def angeles(W=1600, H=900, fase=4):
    cam = vr.Camara(ojo=(0.0, 3.8, -15.0), objetivo=(0.0, 3.4, 6.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(28, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase, cerca=16.0)
    N = np.array([2.0, 0.0, 24.0])
    p = pose('CASTIGO_CLAVA')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], 0.0, 0.0), p, fase, niebla, con_espada=False)
    fe.espada_clavada(lz, cam, M, 0, -30, nme.V, fase, niebla, inclina=0.0)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.6)
    esc = 1.3
    # los que miran (y la mirada que las deja quietas)
    j1, a1 = np.array([3.4, 0.0, -2.0]), np.array([8.5, 0.0, 7.0])
    j2, a2 = np.array([-1.6, 0.0, -1.2]), np.array([-8.0, 0.0, 8.0])
    for j, a in ((j1, a1), (j2, a2)):
        estatua_en(lz, cam, a[0], a[2], fe.guinada_hacia(a[0], a[2], j[0], j[2]) + 180, niebla, fase, esc)
        jugador(lz, cam, j[0], j[2], (a[0], a[2]), QUIETO, niebla=niebla)
        ojo = j + np.array([0, 1.6, 0])
        cara = a + np.array([0, 3.0 * esc, 0])
        haz_oro(lz, cam, [ojo, (ojo + cara) / 2, cara], 0.08, 0.6)
        resplandor(lz, cam, a + np.array([0, 2.2 * esc, 0]), 3.6, ORO, 0.35)
    # la que nadie mira: a la espalda del segundo, con la trompeta hacia el
    a3 = np.array([-3.2, 0.0, -6.2])
    estatua_en(lz, cam, a3[0], a3[2], fe.guinada_hacia(a3[0], a3[2], j2[0], j2[2]) + 180, niebla, fase, esc)
    resplandor(lz, cam, a3 + np.array([0, 2.4 * esc, 0]), 4.4, ROJO, 0.5)
    for k, q in enumerate((a3 + np.array([-0.4, 0.3, -1.4]), a3 + np.array([-0.8, 0.3, -2.8]))):
        nme.vapor(lz, cam, q, 1.0, 4, k, 0.45, 0.8)
    # y una ya rota
    a4 = np.array([4.0, 0.0, 15.0])
    estatua_en(lz, cam, a4[0], a4[2], 30, niebla, fase, esc, rota=True)
    img = acabar(lz, cam, W, H, fase, 212)
    rotulo(img, cam, a1 + np.array([0, 3.8 * esc, 0]), 'LA MIRAN: NO SE MUEVE', -40, -90, 38, ORO_CLARO)
    rotulo(img, cam, a3 + np.array([0, 1.8 * esc, 0]), 'NADIE LA MIRA: SE ACERCA', 70, 60, 40, ROJO_CLARO)
    rotulo(img, cam, a4 + np.array([0, 1.0, 0]), 'ROTA A GOLPES', 60, -70, 34, BLANCO)
    pastilla(img, W - 250, 34, 'ÁNGELES 1/4', 30)
    guardar(img, 'angeles')


def termometro(img, cam, p, k, color, t, dx=30, dy=-60):
    """El termometro que ve cada uno (lo dibujamos junto a el): la barra y el texto."""
    sx, sy, z = cam.proyectar(p)
    if z < 0.5:
        return
    sx, sy = sx / SS + dx, sy / SS + dy
    alto, ancho = 120, 26
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle((sx - ancho / 2 - 4, sy - alto - 4, sx + ancho / 2 + 4, sy + 4), radius=10, fill=(*SOMBRA, 210),
                        outline=(*ORO, 255), width=2)
    lleno = alto * k
    d.rounded_rectangle((sx - ancho / 2 + 3, sy - lleno, sx + ancho / 2 - 3, sy - 3), radius=6, fill=(*color, 255))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(capa)
    dd = ImageDraw.Draw(img)
    f = fuente(30)
    texto(dd, (sx + ancho / 2 + 12, sy - alto / 2 - 18), t, f, color)


def caliente(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-3.0, 6.5, -14.0), objetivo=(0.5, 1.8, 7.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    N = np.array([0.0, 0.0, 22.0])
    p = pose('REPOSO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], 0.0, 0.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.6)
    # la brasa enterrada: la grieta que brilla bajo el que cava
    brasa = np.array([4.2, 0.0, 3.0])
    fe.ruptura(lz, cam, brasa[0], brasa[2], 5, fase, 2.2, 7)
    resplandor(lz, cam, brasa + np.array([0, 0.3, 0]), 2.6, BRASA, 0.9)
    cava = brasa + np.array([-1.0, 0, -1.2])
    Mj, pj = jugador(lz, cam, cava[0], cava[2], (brasa[0], brasa[2]), GOLPE, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'pala' if False else 'espada', 0.42, 1.4)
    medio = np.array([-1.5, 0.0, 5.5])
    jugador(lz, cam, medio[0], medio[2], (brasa[0], brasa[2]), CORRE, niebla=niebla)
    frio = np.array([-7.5, 0.0, -1.5])
    jugador(lz, cam, frio[0], frio[2], (-12.0, 4.0), QUIETO, niebla=niebla)
    # una ya encontrada, flotando en alto
    hallada = np.array([-6.0, 3.2, 12.0])
    bola_de_fuego(lz, cam, hallada, 0.7, 41, 0.6)
    img = acabar(lz, cam, W, H, fase, 213)
    termometro(img, cam, cava + np.array([0, 2.2, 0]), 0.96, (255, 90, 50), '¡ARDIENDO!', 30, -40)
    termometro(img, cam, medio + np.array([0, 2.2, 0]), 0.55, (255, 176, 60), 'TEMPLADO', 30, -40)
    termometro(img, cam, frio + np.array([0, 2.2, 0]), 0.15, (120, 190, 255), 'FRÍO', 30, -40)
    rotulo(img, cam, brasa, 'CAVA AQUÍ: SU BRASA', 80, 70, 38, ORO_CLARO)
    rotulo(img, cam, hallada, 'ENCONTRADA', 60, -20, 34, ORO_CLARO)
    pastilla(img, W - 300, 34, 'BRASAS 1/3 · 30 s', 30)
    guardar(img, 'caliente')


def icono_rps(cual, n=64):
    """El icono de luz de piedra, papel o tijera (de pixeles, como un objeto)."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if cual == 'piedra':
        d.polygon([(3, 10), (4, 6), (7, 4), (11, 4), (13, 7), (13, 11), (10, 13), (5, 13)], fill=(150, 146, 140, 255),
                  outline=(70, 66, 64, 255))
        d.line([(6, 7), (9, 6)], fill=(200, 196, 190, 255))
        d.point([(8, 9), (10, 10)], fill=(100, 96, 92, 255))
    elif cual == 'papel':
        d.rectangle((4, 2, 12, 14), fill=(240, 226, 188, 255), outline=(150, 120, 70, 255))
        d.rectangle((3, 1, 13, 3), fill=(200, 170, 110, 255))
        d.rectangle((3, 13, 13, 15), fill=(200, 170, 110, 255))
        for yy in (6, 8, 10):
            d.line([(6, yy), (10, yy)], fill=(150, 120, 70, 255))
    else:
        d.line([(3, 3), (10, 10)], fill=(210, 214, 222, 255), width=2)
        d.line([(13, 3), (6, 10)], fill=(210, 214, 222, 255), width=2)
        d.ellipse((2, 10, 7, 15), outline=(230, 60, 40, 255), width=2)
        d.ellipse((9, 10, 14, 15), outline=(230, 60, 40, 255), width=2)
    return np.array(im.resize((n, n), Image.NEAREST))


def piedra(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-1.0, 3.6, -17.0), objetivo=(0.5, 7.2, 8.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    N = np.array([0.0, 0.0, 12.0])
    p = pose('SOL')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], 0.0, -12.0), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.7)
    puno = fe.mundo_de(M, nme.V, p, 'mano_izq', (0, 0, 0))
    suyo = puno + np.array([0, 3.2, 0])
    resplandor(lz, cam, suyo, 4.0, BRASA, 0.8)
    nme.sprite(lz, cam, suyo, 1.6, icono_rps('piedra'), 0.0, 1.6)
    jugadas = (((-6.0, -6.0), 'papel'), ((-2.2, -8.0), 'tijera'), ((2.4, -7.2), 'papel'), ((6.2, -5.4), 'piedra'))
    for (x, z), cual in jugadas:
        jugador(lz, cam, x, z, (N[0], N[2]), BRAZOS_ARRIBA if cual == 'papel' else QUIETO, niebla=niebla)
        q = np.array([x, 3.0, z])
        resplandor(lz, cam, q, 1.6, ORO if cual == 'papel' else (BRASA if cual == 'tijera' else BLANCO), 0.5)
        nme.sprite(lz, cam, q, 0.62, icono_rps(cual), 0.0, 1.4)
        if cual == 'tijera':
            arde(lz, cam, np.array([x, 0, z]), fase, 1.0, 13)
        if cual == 'papel':
            haz_oro(lz, cam, [q + np.array([0, 0.5, 0]), (q + suyo) / 2 + np.array([0, 2.0, 0]), suyo], 0.12, 0.9)
    img = acabar(lz, cam, W, H, fase, 214)
    estandarte_orden(img, W / 2 + 20, 26, 'PIEDRA... PAPEL...', '«¡TIJERA!»')
    rotulo(img, cam, suyo + np.array([0, 1.0, 0]), 'ÉL SACA PIEDRA', 90, -10, 40, ORO_CLARO)
    rotulo(img, cam, np.array([-6.0, 3.6, -6.0]), 'PAPEL: GANAN', -40, -70, 38, ORO_CLARO)
    rotulo(img, cam, np.array([-2.2, 2.2, -8.0]), 'TIJERA: ARDE', -60, 110, 38, ROJO_CLARO)
    rotulo(img, cam, np.array([6.2, 3.6, -5.4]), 'EMPATE', 40, -60, 34, BLANCO)
    x = 40
    for t in ('1: PIEDRA', '2: PAPEL', '3: TIJERA'):
        caja = pastilla(img, x, H - 62, t, 24)
        x = caja[2] + 12
    pastilla(img, W - 360, H - 70, 'RONDA 3/5 · GRUPO 2 – ÉL 1', 26)
    guardar(img, 'piedra')


def gallinita(W=1600, H=900, fase=4):
    cam = vr.Camara(ojo=(0.0, 4.4, -15.0), objetivo=(0.0, 6.4, 7.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 72)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    ruido = np.array([-8.0, 0.0, 3.0])
    N = np.array([0.5, 0.0, 9.0])
    p = pose('BARRIDO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], ruido[0], ruido[2]), p, fase, niebla)
    nme.fuego_cuerpo(lz, cam, M, p, fase, k=0.6)
    # la venda: una tela carmesi con filo de oro, delante del yelmo
    cabeza = fe.mundo_de(M, nme.V, p, 'cabeza', (0, -10, -8))
    hacia = cam.ojo - cabeza
    cabeza = cabeza + hacia / np.linalg.norm(hacia) * 1.6
    venda = np.zeros((16, 64, 4), np.uint8)
    venda[..., :3] = (96, 18, 14)
    venda[..., 3] = 255
    venda[0:2, :, :3] = ORO
    venda[14:16, :, :3] = ORO
    venda[6:9, :, :3] = (130, 30, 22)
    fe.trans(lz, cam, [fe.billboard(cabeza, 2.7, cam, 0.15, alto=0.8)], venda, 1.0)
    # los dos cabos de la venda, colgando detras
    for k, (dx, giro) in enumerate(((1.6, 0.9), (1.9, 1.25))):
        q = cabeza + cam.r * dx - cam.u * (0.5 + 0.3 * k)
        fe.trans(lz, cam, [fe.billboard(q, 0.9, cam, giro, alto=0.3)], venda, 1.0)
    # el ruido: anillos en el suelo donde uno acaba de pegar y se va corriendo
    for R, k in ((1.2, 0.95), (2.4, 0.6), (3.6, 0.35)):
        nme.aro_suelo(lz, cam, ruido[0], ruido[2], R, BLANCO, k, 0.6, 0.05, 0, 0)
    jugador(lz, cam, ruido[0] + 0.8, ruido[2] - 2.4, (ruido[0] + 6, ruido[2] - 8), CORRE, niebla=niebla)
    # a su espalda: dos agachados y uno que le pega
    espalda = N + np.array([4.2, 0, -1.0])
    for x, z in ((espalda[0] + 2.6, espalda[2] - 2.6), (espalda[0] + 1.0, espalda[2] + 2.6)):
        jugador(lz, cam, x, z, (N[0], N[2]), AGACHADO, y=-0.18, niebla=niebla)
    Mj, pj = jugador(lz, cam, espalda[0], espalda[2], (N[0], N[2]), GOLPE, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'espada', 0.42, 0.9)
    resplandor(lz, cam, N + np.array([2.6, 3.4, -0.6]), 1.6, ORO, 0.7)
    img = acabar(lz, cam, W, H, fase, 215)
    rotulo(img, cam, cabeza, 'LA VENDA: NO VE, OYE', -60, -60, 40, ORO_CLARO)
    rotulo(img, cam, ruido, '¡RUIDO! AHÍ VA SU ESPADA', -40, 90, 40, ROJO_CLARO)
    rotulo(img, cam, espalda + np.array([2.6, 1.0, -2.6]), 'AGACHADOS NO SE OYEN', 50, 80, 36, BLANCO)
    rotulo(img, cam, espalda + np.array([0, 2.2, 0]), 'GOLPE EN LA ESPALDA', 60, -90, 36, ORO_CLARO)
    pastilla(img, W - 400, 34, 'GOLPES EN LA ESPALDA 9/15', 28)
    guardar(img, 'gallinita')


ESCENAS = {'manda': manda, 'mediodia': mediodia, 'mesa': mesa, 'laberinto': laberinto, 'raya': raya,
           'llamas': llamas, 'angeles': angeles, 'caliente': caliente, 'piedra': piedra, 'gallinita': gallinita}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
