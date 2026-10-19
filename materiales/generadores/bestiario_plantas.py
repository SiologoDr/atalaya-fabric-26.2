"""
Las plantas del bestiario (18-10-2026): las del DEDsafío 2 (las Carnivenus de tres colores, la Tramplanta y la Piña
Malibú) y el Zombie Planta del DEDsafío 4, con nuestro diseño:

  fauces_verde/carmin/escarcha   una planta carnívora plantada en el suelo: la raíz con sus hojas por el suelo, un
                                 tallo grueso y una cabeza de dos mandíbulas con dientes en el borde (por dentro, del
                                 color: verde, carmín o escarcha); te sigue con la cabeza y muerde al que se acerca
  trampa                         una trampa de dos hojas dentadas tumbada en el suelo, del color de la hierba (casi no se
                                 ve); al pisarla salta y se cierra
  pina                           una piña chica con patas, la corona de hojas en punta y cara de pocos amigos
  zombi_planta                   un zombi comido por la planta: musgo, hiedra, flores en la cabeza y los ojos de polen

Uso: python bestiario_plantas.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
from bestiario import rampa
from bestiario import brizna, petalo

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))


def juntar(*rampas):
    return np.vstack(rampas)


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('siempre', 0.5), ('ataque', 0.2), ('ataque', 0.35), ('muerte', 1.0)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


def esquirla(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            a = (np.abs(x - 0.5) + np.abs(y - 0.5) * (0.7 + 0.3 * k) < 0.38) * 255
            sombra = (x + y > 1.05)
            return (np.where(sombra, color[0] * 0.6, color[0]), np.where(sombra, color[1] * 0.6, color[1]),
                    np.where(sombra, color[2] * 0.6, color[2]), a)
        cuadros.append(B.sprite(n, f))
    return cuadros


def chispa(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            centro = d < 0.16
            return (np.where(centro, 255, color[0]), np.where(centro, 240, color[1]), np.where(centro, 210, color[2]),
                    (d < 0.42 - k * 0.1) * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def copo(n=8):
    """Un copo de escarcha: una cruz de seis brazos cortos (a 8 x 8, una estrella de puntas), blanco con el borde
    celeste; tres tamaños."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            u, v = x - 0.5, y - 0.5
            rr = np.hypot(u, v)
            ang = np.arctan2(v, u)
            brazo = (np.abs(np.sin(ang * 3)) < 0.28 + 0.1 * k) & (rr < 0.46 - k * 0.1)
            centro = rr < 0.12
            a = (brazo | centro) * 255
            return (np.where(centro, 255, 200), np.where(centro, 255, 240), 255, a)
        cuadros.append(B.sprite(n, f))
    return cuadros


HOJA = rampa('0e2a08', '1a4a10', '2a6a1a', '3e8a26', '5aac36')
HOJA_O = rampa('081c06', '10300a', '1a4610', '245c18', '307222')
TALLO = rampa('14300c', '204814', '30621c', '427e26', '58a032')
RAIZ = rampa('2e1e10', '4a3018', '6a4824', '8e6634', 'b08850')
DIENTE = rampa('6a6250', 'a89c80', 'd8ccb0', 'f2ead8', 'fffcf2')
COLORES = {
    'verde': (rampa('2a5a04', '4a8a0a', '7ac418', 'b0f040', 'e8ffa0'), 'Verde', 'Green', '7ac418', 'b0f040'),
    'carmin': (rampa('5a0410', '8a0a1e', 'c81a32', 'f04a5a', 'ffb0b8'), 'Carmín', 'Crimson', 'c81a32', 'f04a5a'),
    'escarcha': (rampa('0a4a5a', '127a8a', '2ab8c8', '7ae8f0', 'd8ffff'), 'Escarcha', 'Frost', '2ab8c8', '7ae8f0'),
}


# ======================================================================================================================
#  Las Fauces
# ======================================================================================================================
TIERRA = rampa('24160c', '382412', '503420', '6c4a2c', '8a6640')
DIENTES = {
    'verde': rampa('6a6250', 'a89c80', 'd8ccb0', 'f2ead8', 'fffcf2'),
    'carmin': rampa('6a6250', 'a89c80', 'e0d4b8', 'f6eedc', 'fffcf2'),
    'escarcha': rampa('3a6a7a', '6aa8b8', 'a8e0ea', 'd8f8fc', 'ffffff'),
}


def cupula(m, parte, c, signo, w0, d0, alto, capas, fuera, dentro, labio):
    """Una mandíbula en cúpula: rebanadas desde la del labio (la del borde de la boca) hasta la del lomo, cada una con
    dos cajas cruzadas (octogonal vista desde arriba). La cara de la boca de la primera, 'dentro'; sus lados, el labio
    (la segunda caja del labio, un pelo metida hacia dentro para que su cara de la boca no pise la de la primera).
    Devuelve los medios anchos (W, D) del labio, para los dientes."""
    cx, cy, cz = c
    h = alto / capas
    W = D = 0.0
    for k in range(capas):
        f = math.sqrt(max(0.0, 1.0 - ((k + 0.3) / capas) ** 2))
        y = cy + signo * (h * k + h / 2)
        w, d = w0 * f, d0 * f
        if k == 0:
            W, D = w / 2, d / 2
            caras = {cc: labio for cc in ('frente', 'atras', 'izq', 'der')}
            caras['abajo' if signo > 0 else 'arriba'] = dentro
            caras['arriba' if signo > 0 else 'abajo'] = fuera
            m.caja(parte, (cx, y, cz), (w, h + 0.02, d * 0.74), None, caras=caras)
            m.caja(parte, (cx, y + signo * 0.08, cz), (w * 0.74, h - 0.14, d), None, caras=caras)
        else:
            m.caja(parte, (cx, y, cz), (w, h + 0.02, d * 0.74), fuera)
            m.caja(parte, (cx, y, cz), (w * 0.74, h + 0.02, d), fuera)
    return W, D


def hoja_hacia(m, parte, base, a, incl, ancho, alto, pint):
    """Una hoja que nace en 'base' y sale hacia el rumbo 'a' (grados, 0 = adelante, 90 = a su izquierda), inclinada
    'incl' grados desde la vertical (90, tumbada; más de 90, hacia abajo). La punta de la textura queda en la punta."""
    ar, ir = math.radians(a), math.radians(incl)
    up = np.array((math.sin(ir) * math.sin(ar), math.cos(ir), math.sin(ir) * math.cos(ar)))
    m.hoja(parte, tuple(np.asarray(base, float) + up * alto / 2), ancho, alto, pint, rot=(incl, a, 0))


def colmillo(m, parte, base, hacia, tangente, largo, ancho, pint):
    """Un diente suelto (una hoja) clavado en 'base', hacia 'hacia'."""
    base = np.asarray(base, float)
    m.dientes(parte, base, base + np.asarray(tangente, float) * 0.01, 1, largo, hacia, pint, ancho=ancho)


def corona_de_dientes(m, parte, c, signo, W, D, pint, desfase):
    """Los dientes del borde de una mandíbula: por delante, en las dos esquinas y por los lados (hasta media cabeza;
    atrás está la bisagra). Apuntan a la otra mandíbula y un poco hacia fuera, para que al cerrar se crucen por fuera
    del labio de la otra. 'desfase' (0 o 1) los corre medio paso, para que los de arriba y los de abajo se crucen."""
    cx, cy, cz = c
    y = cy - signo * 0.1
    abajo = np.array((0.0, -signo, 0.0))
    # Por delante.
    n = 5 - desfase
    xs = np.linspace(-0.62 * W, 0.62 * W, 5)
    if desfase:
        xs = (xs[:-1] + xs[1:]) / 2
    for x in xs:
        colmillo(m, parte, (cx + x, y, cz + D - 0.25), abajo + np.array((0, 0, 0.32)), (1, 0, 0), 2.5, 0.75, pint)
    # Las esquinas (en diagonal) y los lados.
    for lado in (-1, 1):
        diag = np.array((lado * 0.7, 0.0, 0.7))
        p = np.array((cx + lado * 0.87 * W, y, cz + 0.87 * D)) - diag * 0.25
        colmillo(m, parte, p, abajo + diag * 0.45, (-diag[2], 0, diag[0]), 2.2, 0.75, pint)
        for z in ((0.45, -0.15) if not desfase else (0.15, -0.45)):
            colmillo(m, parte, (cx + lado * (W - 0.25), y, cz + z * D), abajo + np.array((lado * 0.32, 0, 0)), (0, 0, 1),
                     1.9, 0.7, pint)
    return n


def fauces(raiz, color):
    """Una Fauces: plantada en un montículo de tierra con raíces que asoman y seis hojas anchas tumbadas alrededor; un
    tallo grueso en ese y, con una gorguera de hojitas, la cabeza: dos mandíbulas en cúpula (verde oscuro por fuera, con
    venas y motas del color; el labio del color) con una corona de dientes que se cruzan al cerrar. Dentro, del color,
    un señuelo que brilla en la garganta (se le ve por la rendija de la boca, siempre entreabierta). La verde babea
    ácido; la carmín tiene espinas en el tallo y una cresta; la de escarcha, carámbanos, cristales en el lomo y dientes
    de hielo."""
    G, nombre_es, nombre_en, c1, c2 = COLORES[color]
    m = B.Modelo(f'fauces_{color}', K=2, ancho=128)
    m.escala = 1.1
    R = juntar(HOJA, G)

    # ---- El montículo, las raíces y las hojas del suelo.
    def tierra(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 2)
        raices = B.grietas(tw, th, s, cara, cuantas=max(1, tw * th // 50), giro=0.4, ramas=0.08)
        idx[raices] = 4
        idx[B.vecinos(raices) & (ys % 2 == 0)] = 1
        if cara == 'arriba':
            idx[((xs * 7 + ys * 3) % 11) == 0] = 3
        return idx
    pint_tierra = B.trazo('tierra_fauces', tierra, TIERRA)
    m.parte('raiz', None, (0, 0, 0))
    for k, (r, h) in enumerate(((4.4, 1.2), (3.6, 1.1), (2.4, 1.0))):
        y = sum(hh for _, hh in ((4.4, 1.2), (3.6, 1.1), (2.4, 1.0))[:k]) + h / 2
        m.caja('raiz', (0, y, 0), (2 * r, h + 0.02, 2 * r * 0.74), pint_tierra)
        m.caja('raiz', (0, y, 0), (2 * r * 0.74, h + 0.02, 2 * r), pint_tierra)
    raiz_p = B.anillos('raiz_fauces', RAIZ, paso=2)
    for k in range(5):
        a = math.radians(k * 72 + 40)
        m.viga('raiz', (math.sin(a) * 2.6, 1.4, math.cos(a) * 2.6), (math.sin(a) * 6.4, 0.2, math.cos(a) * 6.4), 0.9,
               raiz_p, extra=0.4)
    hoja_suelo = brizna('hoja_suelo', HOJA, ancho_base=1.9)
    for k in range(6):
        a = k * 60 + 10
        hoja_hacia(m, 'raiz', (math.sin(math.radians(a)) * 2.4, 0.9, math.cos(math.radians(a)) * 2.4), a, 80, 4.8, 7.4,
                   hoja_suelo)

    # ---- El tallo, en ese, con dos hojas.
    tallo = B.anillos('tallo_fauces', TALLO, paso=3)
    m.parte('tallo', 'raiz', (0, 2.6, 0))
    m.viga('tallo', (0, 2.2, 0), (1.0, 6.8, -0.6), 2.6, tallo, extra=0.6)
    m.viga('tallo', (1.0, 6.8, -0.6), (0.4, 10.4, -1.2), 2.3, tallo, extra=0.6)
    m.parte('tallob', 'tallo', (0.4, 10.4, -1.2))
    m.viga('tallob', (0.4, 10.4, -1.2), (0, 14.4, 0.0), 2.0, tallo, extra=0.6)
    hoja_tallo = brizna('hoja_tallo', HOJA, ancho_base=1.7)
    hoja_hacia(m, 'tallo', (1.6, 5.6, -0.4), 90, 55, 3.2, 5.6, hoja_tallo)
    hoja_hacia(m, 'tallob', (-0.6, 11.4, -1.0), -100, 60, 2.8, 4.8, hoja_tallo)
    if color == 'carmin':
        espina = B.diente('espina_carmin', G)
        for (y, a) in ((4.0, 30), (5.6, 200), (7.6, 110), (9.2, 300), (11.6, 60), (13.0, 230)):
            ar = math.radians(a)
            # El tallo pasa (más o menos) por el eje: las espinas salen de su piel hacia fuera.
            cxz = (0.6 if y < 11 else 0.2, -0.8 if y < 11 else -0.6)
            base = (cxz[0] + math.sin(ar) * 1.0, y, cxz[1] + math.cos(ar) * 1.0)
            colmillo(m, 'tallo' if y < 10.4 else 'tallob', base, (math.sin(ar), 0.25, math.cos(ar)), (0, 1, 0), 1.6,
                     0.6, espina)

    # ---- La cabeza.
    cy, cz = 17.8, 2.2
    w0, d0, alto = 9.8, 8.6, 4.6
    c = np.array((0.0, cy, cz))
    m.parte('cabeza', 'tallob', (0, 14.4, 0.0))
    # La gorguera: hojitas alrededor del cuello, hacia fuera y hacia abajo.
    gorguera = brizna('gorguera', HOJA_O, ancho_base=1.5)
    for k in range(7):
        a = k * 360 / 7 + 8
        hoja_hacia(m, 'cabeza', (math.sin(math.radians(a)) * 1.0, 13.8, 0.4 + math.cos(math.radians(a)) * 1.0), a, 112,
                   2.2, 3.4, gorguera)

    def piel_fuera(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 1)
        venas = B.grietas(tw, th, s, cara, cuantas=max(1, tw * th // 36), giro=0.35, ramas=0.1)
        idx[venas] = 3
        idx[B.vecinos(venas) & ((xs + ys) % 2 == 0)] = 2
        g = B._azar(s * 3 + tw)
        for _ in range(max(1, tw * th // 45)):
            x, y = int(g.integers(0, tw)), int(g.integers(0, th))
            idx[y, x] = 7
            if x + 1 < tw:
                idx[y, x + 1] = 6
        if cara == 'arriba':
            idx[idx == 1] = 2
        return idx
    fuera = B.trazo(f'fuera_{color}', piel_fuera, R)

    def piel_dentro(xs, ys, tw, th, cara, s):
        # La carne de dentro: del color, la garganta oscura en medio, venas que salen de ella, el borde más oscuro (para
        # que se separe del labio) y tres pelillos claros (los que, al tocarlos, la hacen cerrarse).
        u, v = (xs + 0.5) / tw - 0.5, (ys + 0.5) / th - 0.5
        rr = np.hypot(u, v * 1.1)
        ang = np.arctan2(v, u)
        idx = np.full((th, tw), 7)
        idx[(np.abs(np.sin(ang * 5 + rr * 4)) < 0.16) & (rr > 0.12)] = 8
        idx[rr < 0.22] = 6
        idx[rr < 0.11] = 5
        idx[rr > 0.43] = 6
        for a0 in (0.5, 2.6, 4.7):
            hx, hy = 0.27 * math.cos(a0), 0.27 * math.sin(a0)
            idx[(np.abs(u - hx) < 0.6 / tw) & (np.abs(v - hy) < 0.6 / th)] = 9
        return idx
    dentro = B.trazo(f'dentro_{color}', piel_dentro, R)

    def labio_f(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 7)
        idx[((xs + s) % 4) == 0] = 8
        return idx
    labio = B.trazo(f'labio_{color}', labio_f, R)
    pint_diente = B.diente(f'diente_{color}', DIENTES[color])
    bisagra = (0.0, cy, cz - d0 / 2 * 0.86)
    for nombre, signo in (('mandibula_sup', 1), ('mandibula_inf', -1)):
        n = m.parte(nombre, 'cabeza', bisagra)
        W, D = cupula(m, n, c, signo, w0, d0, alto, 6, fuera, dentro, labio)
        corona_de_dientes(m, n, c, signo, W, D, pint_diente, 0 if signo > 0 else 1)
    # El señuelo: un tallito con una bola que brilla, en la garganta (en la mandíbula de abajo).
    m.viga('mandibula_inf', (0, cy - 0.4, cz + 0.4), (0, cy + 0.3, cz + 0.7), 0.6, B.liso('tallito', G, base=1))
    m.caja('mandibula_inf', (0, cy + 0.6, cz + 0.8), (1.3, 1.2, 1.3), B.luz(f'senuelo_{color}', G))
    # Lo de cada color.
    if color == 'verde':
        baba = B.luz('baba_verde', G)
        m.viga('mandibula_sup', (1.2, cy - 0.2, cz + D - 0.6), (1.4, cy - 2.6, cz + D - 0.2), 0.45, baba)
        m.caja('mandibula_sup', (1.4, cy - 2.9, cz + D - 0.2), (0.8, 0.9, 0.8), baba)
        m.viga('mandibula_sup', (-2.4, cy - 0.2, cz + D - 1.4), (-2.6, cy - 1.6, cz + D - 1.2), 0.4, baba)
    elif color == 'escarcha':
        hielo = B.liso('hielo', G, base=3)
        for (x, z, l) in ((-2.8, 2.6, 2.4), (-0.6, 3.4, 3.2), (1.6, 3.0, 2.0), (3.2, 1.0, 2.6)):
            m.viga('mandibula_inf', (x, cy - alto * 0.55, cz + z * 0.9), (x * 1.05, cy - alto * 0.55 - l, cz + z * 0.9),
                   0.7, hielo)
        cristal = B.luz('cristal_escarcha', rampa('4ac8e0', '8ae8f4', 'c0f8fc', 'e8ffff', 'ffffff'))
        for (x, z, ry) in ((-1.8, -0.6, 25), (0.4, 1.0, -10), (2.0, -1.2, 40)):
            m.viga('mandibula_sup', (x, cy + alto - 1.0, cz + z), (x * 1.5, cy + alto + 2.2, cz + z - 0.8), 1.0, cristal,
                   rodar=ry)
    m.mirar(('cabeza', 0.6), ('tallob', 0.3))

    # siempre: el tallo se mece, la cabeza cabecea y la boca respira entreabierta (se le ve el señuelo).
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('tallo', 'r', 2, 4, periodo=3.0)
    s.onda('tallob', 'r', 0, 5, periodo=1.5, fase=0.2)
    s.onda('cabeza', 'r', 0, 4, periodo=1.5, fase=0.45)
    s.onda('mandibula_sup', 'r', 0, 5, periodo=1.5, base=-15)
    s.onda('mandibula_inf', 'r', 0, -3, periodo=1.5, base=9)
    # ataque: se echa atrás abriendo la boca de par en par y se lanza cerrándola de golpe (y la sujeta un momento).
    at = m.anim('ataque', 0.6)
    at.rot('tallob', [(0, 0, 0, 0), (0.16, -22, 0, 0), (0.28, 34, 0, 0), (0.44, 26, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.16, -16, 0, 0), (0.28, 12, 0, 0), (0.44, 8, 0, 0), (0.6, 0, 0, 0)])
    at.rot('mandibula_sup', [(0, 0, 0, 0), (0.16, -40, 0, 0), (0.27, 17, 0, 0), (0.44, 15, 0, 0), (0.6, 0, 0, 0)])
    at.rot('mandibula_inf', [(0, 0, 0, 0), (0.16, 26, 0, 0), (0.27, -10, 0, 0), (0.44, -9, 0, 0), (0.6, 0, 0, 0)])
    # muerte: se marchita: el tallo se dobla, la cabeza cae con la boca abierta y se encoge.
    d = m.anim('muerte', 1.0)
    d.rot('tallo', [(0, 0, 0, 0), (1.0, 32, 0, 18)])
    d.rot('tallob', [(0, 0, 0, 0), (1.0, 55, 0, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (1.0, 30, 0, 0)])
    d.rot('mandibula_sup', [(0, 0, 0, 0), (1.0, -32, 0, 0)])
    d.rot('mandibula_inf', [(0, 0, 0, 0), (1.0, 18, 0, 0)])
    d.esc('cabeza', [(0, 1, 1, 1), (1.0, 0.85, 0.85, 0.85)])

    def dib(px, filas, c_):
        # La cabeza (dos mandíbulas con dientes) y el tallo.
        for x in range(4, 12):
            px[x, 3] = c_('2a6a1a')
            px[x, 4] = c_(c2)
            px[x, 7] = c_(c2)
            px[x, 8] = c_('2a6a1a')
        for x in (5, 7, 9, 11):
            px[x, 5] = c_('fffcf2')
        for x in (4, 6, 8, 10):
            px[x, 6] = c_('fffcf2')
        for f in range(9, 14):
            px[7, f] = px[8, f] = c_('427e26')
    return terminar(m, raiz, f'Fauces {nombre_es}', f'{nombre_en} Maw',
                    (('5aac36', '3e8a26', '2a6a1a'), ('0e2a08', '061404'), dib),
                    ((1.25, 1.45, 1.95), (0, 0.85, 0.05)),
                    particulas=(('savia', chispa(tuple(int(c2[i:i + 2], 16) for i in (0, 2, 4)))),
                                ('hoja', esquirla((62, 138, 38))))
                    + ((('escarcha', copo()),) if color == 'escarcha' else ()),
                    poses=[('siempre', 0.5), ('ataque', 0.16), ('ataque', 0.3), ('muerte', 1.0)])


# ======================================================================================================================
#  La Trampa Verde
# ======================================================================================================================
# La hierba de dentro, en grises (el juego la tiñe del verde de su bioma mientras espera), y la de las briznas.
CESPED = rampa('707070', '858585', '9a9a9a', 'afafaf', 'c4c4c4')
SALVIA = rampa('5a7a4a', '6e8e5a', '82a26a', '96b67a', 'aaca8a')
PESTANA = rampa('4a6a30', '7a9a50', 'b8d090', 'e0f0c0', 'f8fff0')
CARNE = rampa('5a1a2a', '8a2a40', 'b84a62', 'e07a90', 'ffb8c8')


def trampa(raiz):
    """La Trampa Verde: dos lóbulos en media luna unidos por un nervio (la bisagra), con una fila de pestañas largas en
    el borde. Escondida (estado1), los lóbulos están abiertos y tumbados en el suelo: por dentro son del verde del césped
    (con tres pelillos rosados, los que la disparan) y las pestañas quedan tendidas como si fueran hierba. Al pisarla se
    cierra de golpe: por fuera es verde con las venas oscuras y el borde se enrojece; las pestañas se cruzan arriba.

    Lo de dentro va en grises, como la hierba de Minecraft: mientras espera, el juego la tiñe del verde de la hierba de
    su bioma (BestiaRenderer, getModelTint), así que es del color exacto del suelo en el que está."""
    m = B.Modelo('trampa', K=2, ancho=128)
    m.escala = 1.3
    # El nervio de en medio (la bisagra) y unas briznas que lo tapan.
    m.parte('base', None, (0, 0, 0))
    m.caja('base', (0, 0.5, 0), (1.8, 1.0, 15.6), B.anillos('bisagra_trampa', TALLO, paso=2))
    hierba = brizna('brizna_trampa', SALVIA, ancho_base=0.9)
    for k, (x, z) in enumerate(((-0.4, 6.6), (0.5, 3.8), (-0.3, 1.0), (0.5, -2.0), (-0.5, -4.6), (0.4, -6.8))):
        for g in (30 + k * 17, 120 + k * 17):
            hoja_hacia(m, 'base', (x, 0.8, z), g, 18, 1.1, 2.6 + (k % 2) * 0.6, hierba)

    def fuera_f(alto_):
        def f(xs, ys, tw, th, cara, s):
            idx = np.full((th, tw), 2)
            venas = B.grietas(tw, th, s, cara, cuantas=max(1, tw * th // 30), giro=0.25, ramas=0.12)
            idx[venas] = 1
            if alto_:
                # El borde se enrojece (las filas de arriba de la parte alta del lóbulo).
                v = (ys + 0.5) / th
                idx = np.where((v < 0.45) & ~venas, 7, idx)
                idx = np.where((v < 0.2) & ~venas, 8, idx)
            return idx
        return f
    fuera_bajo = B.trazo('fuera_trampa', fuera_f(False), juntar(HOJA, CARNE))
    fuera_alto = B.trazo('fuera_alto_trampa', fuera_f(True), juntar(HOJA, CARNE))

    def dentro_f(xs, ys, tw, th, cara, s):
        # El césped: motas de dos verdes y alguna más clara, y algún pelillo rosado.
        g = B._azar(s * 5 + tw * 11 + th)
        idx = np.full((th, tw), 2)
        idx[((xs * 3 + ys * 7 + s) % 5) == 0] = 1
        idx[((xs * 5 + ys * 3 + s) % 7) == 0] = 3
        idx[((xs * 2 + ys * 9 + s) % 13) == 0] = 4
        if tw * th > 12 and g.random() < 0.5:
            idx[int(g.integers(0, th)), int(g.integers(0, tw))] = 8
        return idx
    dentro = B.trazo('dentro_trampa', dentro_f, juntar(CESPED, CARNE))
    borde = B.liso('borde_trampa', CARNE, base=2)
    pestana = B.diente('pestana_trampa', PESTANA)
    R = 8.0
    zs = (-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0)
    for lado, ld in LADOS:
        n = m.parte(f'hoja_{ld}', 'base', (lado * 0.9, 1.0, 0))
        ext, inn = ('der', 'izq') if lado > 0 else ('izq', 'der')
        for i, z in enumerate(zs):
            c = math.sqrt(max(0.0, 1.0 - (z / 8.8) ** 2))
            h = R * c + 0.6
            # La parte de abajo, abombada hacia fuera; la de arriba vuelve hacia dentro, inclinada.
            caras_b = {'frente': fuera_bajo, 'atras': fuera_bajo, ext: fuera_bajo, inn: dentro, 'abajo': fuera_bajo,
                       'arriba': fuera_bajo}
            m.caja(n, (lado * (1.4 + 1.3 * c), 1.0 + h * 0.3, z), (1.0, h * 0.6, 2.06), None, caras=caras_b)
            caras_a = {'frente': fuera_alto, 'atras': fuera_alto, ext: fuera_alto, inn: dentro, 'abajo': fuera_alto,
                       'arriba': borde}
            xa = lado * (1.2 + 0.7 * c)
            m.caja(n, (xa, 1.0 + h * 0.78, z), (1.0, h * 0.46, 2.06), None, caras=caras_a, rot=(0, 0, lado * 14))
        # Las pestañas del borde (una por píxel, corridas medio píxel entre un lóbulo y el otro para que se crucen):
        # arriba y hacia dentro; escondida, quedan de punta entre la hierba.
        zc = -7.5 if lado > 0 else -7.0
        while zc <= 7.5 + 1e-6:
            c = math.sqrt(max(0.0, 1.0 - (zc / 8.8) ** 2))
            h = R * c + 0.6
            xa = lado * (1.2 + 0.7 * c)
            s14, c14 = math.sin(math.radians(14)), math.cos(math.radians(14))
            top = (xa - lado * 0.23 * h * s14, 1.0 + 0.78 * h + 0.23 * h * c14 - 0.2, zc)
            colmillo(m, n, top, (-lado * 0.62, 1.0, 0.0), (0, 0, 1), 3.4 * c + 0.4, 0.55, pestana)
            zc += 1.0
    # estado1: escondida (los lóbulos abiertos y tumbados en el suelo).
    e1 = m.anim('estado1', 1.0, bucle=True)
    for lado, ld in LADOS:
        e1.rot(f'hoja_{ld}', [(0, 0, 0, lado * -90), (1.0, 0, 0, lado * -90)])
    # aparece: salta y se cierra de golpe (de tumbada a cerrada, pasándose un poco y rebotando).
    ap = m.anim('aparece', 0.45)
    for lado, ld in LADOS:
        ap.rot(f'hoja_{ld}', [(0, 0, 0, lado * -90), (0.07, 0, 0, lado * -40), (0.12, 0, 0, lado * 8),
                             (0.2, 0, 0, lado * -4), (0.3, 0, 0, 0)])
    ap.mov('base', [(0, 0, 0, 0), (0.08, 0, 2.6, 0), (0.2, 0, -0.4, 0), (0.3, 0, 0, 0)])
    # reposo (cerrada, sin esconderse): mastica, apretando y aflojando.
    r = m.anim('reposo', 1.2, bucle=True)
    for lado, ld in LADOS:
        r.onda(f'hoja_{ld}', 'r', 2, lado * -7, periodo=0.6, forma=lambda v: max(0.0, v))
    r.onda('base', 'e', 1, 0.04, periodo=0.6, base=1.0)
    # ataque: aprieta fuerte (el mordisco de cada golpe de veneno).
    at = m.anim('ataque', 0.4)
    for lado, ld in LADOS:
        at.rot(f'hoja_{ld}', [(0, 0, 0, 0), (0.08, 0, 0, lado * 6), (0.4, 0, 0, 0)])
    at.esc('base', [(0, 1, 1, 1), (0.08, 1.06, 0.92, 1.0), (0.4, 1, 1, 1)])
    # especial: se vuelve a abrir despacio y se tumba (sumado a estado1: de cerrada a tumbada).
    es = m.anim('especial', 1.0)
    for lado, ld in LADOS:
        es.rot(f'hoja_{ld}', [(0, 0, 0, lado * 90), (0.25, 0, 0, lado * 75), (0.35, 0, 0, lado * 80),
                             (0.8, 0, 0, lado * 6), (1.0, 0, 0, 0)])
    # muerte: los lóbulos se abren lacios y todo se encoge.
    d = m.anim('muerte', 1.0)
    for lado, ld in LADOS:
        d.rot(f'hoja_{ld}', [(0, 0, 0, 0), (1.0, 0, 0, lado * -65)])
    d.esc('base', [(0, 1, 1, 1), (1.0, 0.85, 0.6, 0.85)])

    def dib(px, filas, c_):
        for f in range(6, 13):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c_('4e922c' if (x + f) % 3 else '3e7a22')
        for x in (4, 6, 8, 10, 12):
            px[x, 5] = c_('f8fff0')
        for x in (5, 7, 9, 11):
            px[x, 6] = c_('e07a90')
    return terminar(m, raiz, 'Trampa Verde', 'Green Trap', (('88cc56', '5eaa36', '3e7a22'), ('1a4a10', '0e2a08'), dib),
                    ((0.95, 0.95, 1.35), (0, 0.3, 0)),
                    particulas=(('hoja', esquirla((94, 170, 54))), ('pestana', esquirla((224, 240, 192)))),
                    poses=[('estado1', 0.5), ('aparece', 0.1), ('reposo', 0.15), ('muerte', 1.0)])


# ======================================================================================================================
#  La Piña Brava
# ======================================================================================================================
PINA = rampa('6a3a04', 'a8640a', 'd8941a', 'f6c24a', 'fff0a0')
CORONA = rampa('0e3a10', '1a5a1a', '2a7a2a', '42a03a', '6ac85a')


def pina(raiz):
    """La Piña Brava: una piña chica (las escamas en rombos, cada una con su pincho) con una corona de hojas en punta
    en tres pisos (las de dentro, de pie; las de fuera, abiertas), cejas fruncidas, ojos negros con su brillo y una boca
    de dientes apretados; dos bracitos de tallo con los puños de hoja y dos patas cortas de raíz. Pega muy deprisa:
    un uno-dos con los puños."""
    m = B.Modelo('pina', K=2, ancho=128)
    m.escala = 0.85

    def escamas(xs, ys, tw, th, cara, s):
        u = (xs + ys) % 6
        v = (xs - ys) % 6
        idx = np.full((th, tw), 2)
        idx[(u == 0) | (v == 0)] = 1
        idx[(u == 3) & (v == 3)] = 4
        idx[((u == 2) & (v == 3)) | ((u == 3) & (v == 2))] = 3
        if cara == 'abajo':
            idx[...] = 1
        return idx
    pint = B.trazo('escamas_pina', escamas, PINA)
    m.parte('cuerpo', None, (0, 4.0, 0))
    r = 4.6
    cyb = 8.4
    m.esfera('cuerpo', (0, cyb, 0), r, lambda k, n: pint, cortes=7)
    # La cara: ojos negros con su brillo, cejas fruncidas y la boca de dientes apretados.
    zf = r * 1.03 * 0.995 + 0.1
    negro = B.liso('ojo_pina', rampa('000000', '050505', '0c0c0c', '161616', '202020'), base=2)
    brillo = B.liso('brillo_pina', rampa('ffffff', 'ffffff', 'ffffff', 'ffffff', 'ffffff'))
    ceja = B.liso('ceja_pina', rampa('2a1402', '3a1e04', '4a2806', '5a3208', '6a3a0a'), base=2)
    for lado in (-1, 1):
        m.caja('cuerpo', (lado * 1.5, cyb + 1.0, zf), (1.5, 1.5, 0.3), negro)
        m.caja('cuerpo', (lado * 1.5 - lado * 0.35, cyb + 1.4, zf + 0.18), (0.5, 0.5, 0.1), brillo)
        m.caja('cuerpo', (lado * 1.7, cyb + 2.25, zf + 0.12), (2.3, 0.7, 0.4), ceja, rot=(0, 0, lado * 24))
    boca = B.liso('boca_pina', rampa('1a0404', '2a0808', '3a0c0c', '4a1010', '5a1414'), base=1)
    m.caja('cuerpo', (0, cyb - 1.5, zf - 0.05), (3.6, 1.6, 0.3), boca)
    dpina = B.diente('diente_pina')
    m.dientes('cuerpo', (-1.35, cyb - 0.75, zf + 0.12), (1.35, cyb - 0.75, zf + 0.12), 4, 0.8, (0, -1, 0), dpina,
              ancho=0.6)
    m.dientes('cuerpo', (-0.9, cyb - 2.25, zf + 0.12), (0.9, cyb - 2.25, zf + 0.12), 3, 0.7, (0, 1, 0), dpina,
              ancho=0.6)
    # La corona: tres pisos de hojas.
    m.parte('corona', 'cuerpo', (0, cyb + r - 0.4, 0))
    hoja_c = brizna('hoja_corona', CORONA, ancho_base=1.3)
    base_c = (0.0, cyb + r - 0.6, 0.0)
    for k in range(4):
        hoja_hacia(m, 'corona', base_c, k * 90 + 45, 10, 2.4, 7.4, hoja_c)
    for k in range(6):
        hoja_hacia(m, 'corona', base_c, k * 60 + 15, 32, 2.4, 6.0, hoja_c)
    for k in range(8):
        hoja_hacia(m, 'corona', (0.0, cyb + r - 1.0, 0.0), k * 45, 62, 2.2, 4.6, hoja_c)
    # Los bracitos y los puños.
    tallo_b = B.anillos('brazo_pina', TALLO, paso=2)
    puno = B.trazo('puno_pina', lambda xs, ys, tw, th, cara, s: np.where((xs + ys) % 3 == 0, 3, 2), CORONA)
    for lado, ld in LADOS:
        n = m.parte(f'brazo_{ld}', 'cuerpo', (lado * (r - 0.4), cyb - 0.2, 0.4))
        m.viga(n, (lado * (r - 0.4), cyb - 0.2, 0.4), (lado * (r + 1.6), cyb - 2.2, 1.6), 1.0, tallo_b, extra=0.4)
        m.caja(n, (lado * (r + 1.8), cyb - 2.6, 1.9), (1.9, 1.9, 1.9), puno)
    # Las patas.
    pata = B.anillos('pata_pina', RAIZ, paso=2)
    for lado, ld in LADOS:
        n = m.parte(f'pata_{ld}', 'cuerpo', (lado * 1.8, 4.6, 0))
        m.caja_desde(n, (lado * 1.8, 0.6, 0.0), (1.8, 4.6, 1.8), pata)
        m.caja(n, (lado * 1.9, 0.5, 0.7), (2.2, 1.0, 3.0), pata)
    m.mirar(('cuerpo', 0.3))
    a = m.anim('andar', 0.3, bucle=True)
    a.onda('pata_d', 'r', 0, 42)
    a.onda('pata_i', 'r', 0, 42, fase=0.5)
    a.onda('brazo_d', 'r', 0, -30, fase=0.5)
    a.onda('brazo_i', 'r', 0, -30)
    a.onda('cuerpo', 'r', 2, 6, periodo=0.3)
    a.onda('cuerpo', 'm', 1, 0.6, periodo=0.15, forma=lambda v: abs(v))
    a.onda('corona', 'r', 0, 8, periodo=0.15)
    s = m.anim('siempre', 2.0, bucle=True)
    s.onda('corona', 'r', 2, 5, periodo=1.0)
    rp = m.anim('reposo', 1.2, bucle=True)
    rp.onda('cuerpo', 'e', 1, 0.03, base=1.0, periodo=0.6)
    rp.onda('brazo_d', 'r', 0, -12, periodo=0.6, forma=lambda v: max(0.0, v))
    rp.onda('brazo_i', 'r', 0, -12, periodo=0.6, fase=0.5, forma=lambda v: max(0.0, v))
    # ataque: un uno-dos (el puño derecho y luego el izquierdo) echándose adelante.
    at = m.anim('ataque', 0.36)
    at.rot('cuerpo', [(0, 0, 0, 0), (0.08, 12, -12, 0), (0.2, 12, 12, 0), (0.36, 0, 0, 0)])
    at.rot('brazo_d', [(0, 0, 0, 0), (0.06, -70, 0, 0), (0.14, 0, 0, 0)])
    at.rot('brazo_i', [(0, 0, 0, 0), (0.14, 0, 0, 0), (0.2, -70, 0, 0), (0.3, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.5, 60, 0, 10), (1.0, 90, 0, 15)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -3.5, 1)])
    m.paso = 5.0

    def dib(px, filas, c):
        for x, f in ((6, 7), (9, 7)):
            px[x, f] = c('000000')
        for x, f in ((5, 6), (10, 6)):
            px[x, f] = c('3a1e04')
        for x in (6, 7, 8, 9):
            px[x, 10] = c('3a0c0c')
        for x, f in ((6, 1), (8, 0), (10, 1), (7, 2), (9, 2)):
            px[x, f] = c('42a03a')
    return terminar(m, raiz, 'Piña Brava', 'Fierce Pineapple', (('fff0a0', 'f6c24a', 'd8941a'), ('6a3a04', '3a1e02'), dib),
                    ((0.85, 0.85, 1.25), (0, 0.45, 0)),
                    particulas=(('jugo', chispa((246, 194, 74))), ('hoja', esquirla((66, 160, 58)))),
                    poses=[('andar', 0.08), ('andar', 0.22), ('ataque', 0.07), ('ataque', 0.21)])


# ======================================================================================================================
#  El Zombi Planta
# ======================================================================================================================
PIEL_Z = rampa('1a3a1a', '2a5228', '3e6e36', '588c48', '7aac5e')
MUSGO = rampa('0e2a0a', '1a4210', '2a5c18', '3e7a22', '5a9a30')
CORTEZA = rampa('2a1c10', '42301c', '5e4428', '7a5c36', '9a7848')
POLEN = rampa('6a5004', 'a88a0a', 'e8c41a', 'fff060', 'fffcc0')
CAMISA = rampa('0e3a3a', '145252', '1e6a6a', '2a8484', '3aa0a0')
PANTALON = rampa('1a1a34', '26264a', '343464', '46467e', '5c5c98')
FLOR = rampa('6a1a3a', 'a02a5a', 'd84a8a', 'f48ab4', 'ffd0e4')


def zombi_planta(raiz):
    """El Zombi Planta: un zombi al que se ha comido la planta. La ropa de siempre (la camisa turquesa y el pantalón
    azul) desteñida y rota, con la piel verde podrida asomando por los rotos y manchas de musgo; hiedra que le cruza el
    pecho y se enrosca en los brazos; los dedos, raíces que cuelgan; los pies echan raíces al suelo; en la cabeza, musgo,
    flores y hojas; un ojo encendido de polen y, en el otro, una flor que le ha brotado de la cuenca; y a la espalda, un
    arbolito que le crece del hombro."""
    m = B.Modelo('zombi_planta', K=2, ancho=128)
    R = juntar(PIEL_Z, POLEN)

    def piel(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 2)
        g = B._azar(s + tw * 3 + th)
        for _ in range(max(1, (tw * th) // 40)):
            cx, cy = g.integers(0, tw), g.integers(0, th)
            idx[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2] = 1
        idx[((xs + ys * 2) % 7) == 0] = 3
        return idx

    def cara(xs, ys, tw, th, c, s):
        idx = piel(xs, ys, tw, th, c, s)
        u, v = (xs + 0.5) / tw, (ys + 0.5) / th
        # El ojo de polen (el izquierdo del zombi, a la derecha de quien lo mira), la cuenca vacía del otro y la boca.
        ojo = (np.abs(u - 0.7) < 0.11) & (np.abs(v - 0.45) < 0.08)
        cuenca = (np.abs(u - 0.3) < 0.12) & (np.abs(v - 0.45) < 0.1)
        boca = (np.abs(u - 0.5) < 0.24) & (np.abs(v - 0.76) < 0.05)
        idx = np.where(ojo, 8, np.where(cuenca | boca, 0, idx))
        return idx, ojo
    pint = B.trazo('piel_zombi_planta', piel, R)

    def ropa(rampa_, nombre):
        def f(xs, ys, tw, th, cara_, s):
            # La tela, desteñida a manchas, con rotos por los que asoma la piel verde (índices 5..: la piel) y musgo.
            g = B._azar(s * 7 + tw + th * 5)
            idx = np.full((th, tw), 2)
            idx[((xs + ys * 3) % 5) == 0] = 1
            idx[((xs * 2 + ys) % 9) == 0] = 3
            for _ in range(max(1, tw * th // 55)):
                cx, cy = int(g.integers(0, tw)), int(g.integers(0, th))
                rr = g.uniform(0.8, 1.8)
                roto = (xs - cx) ** 2 + (ys - cy) ** 2 < rr * rr
                idx[roto] = 7
                idx[B.vecinos(roto)] = 0
            for _ in range(max(1, tw * th // 70)):
                cx, cy = int(g.integers(0, tw)), int(g.integers(0, th))
                idx[max(0, cy - 1):cy + 1, max(0, cx - 1):cx + 2] = 10 + int(g.integers(2, 4))
            return idx
        return B.trazo(nombre, f, np.vstack((rampa_, PIEL_Z, MUSGO)))
    camisa = ropa(CAMISA, 'camisa_zombi_planta')
    pantalon = ropa(PANTALON, 'pantalon_zombi_planta')
    musgo = B.trazo('musgo', lambda xs, ys, tw, th, c, s: np.where(((xs // 2 + ys // 2) % 3) == 0, 3,
                                                                np.where((xs + ys) % 4 == 0, 1, 2)), MUSGO)
    hiedra = B.anillos('hiedra', MUSGO, paso=2)
    raiz_p = B.anillos('raiz_zombi', CORTEZA, paso=2)
    hoja = brizna('hoja_zombi', HOJA, ancho_base=1.5)
    # El cuerpo: tronco, cabeza, brazos por delante y piernas.
    m.parte('cuerpo', None, (0, 12, 0))
    m.caja_desde('cuerpo', (0, 12, 0), (8, 12, 4), camisa)
    m.caja('cuerpo', (1.6, 21.2, 0.2), (5.6, 3.2, 4.5), musgo)
    # La hiedra que le cruza el pecho (y la espalda).
    m.viga('cuerpo', (-4.2, 23.4, 2.2), (3.6, 13.6, 2.2), 0.8, hiedra, extra=0.2)
    m.viga('cuerpo', (4.2, 22.0, -2.2), (-3.0, 14.4, -2.2), 0.8, hiedra, extra=0.2)
    for (x, y, z, a) in ((-1.6, 20.2, 2.3, 0), (1.4, 16.8, 2.3, 0), (2.0, 18.4, -2.3, 180)):
        hoja_hacia(m, 'cuerpo', (x, y, z), a, 70, 1.8, 3.2, hoja)
    m.parte('cabeza', 'cuerpo', (0, 24, 0))
    m.caja_desde('cabeza', (0, 24, 0), (8, 8, 8), pint, caras={'frente': B.trazo('cara_zombi_planta', cara, R)})
    m.caja('cabeza', (-1.2, 32.3, -0.6), (6.4, 1.4, 6.6), musgo)
    m.caja('cabeza', (2.6, 31.6, 1.8), (3.0, 1.0, 3.4), musgo)
    # La flor que le brota de la cuenca (el ojo derecho del zombi, a la izquierda de quien lo mira).
    flor = petalo('flor_zombi', FLOR)
    centro = B.luz('centro_flor', POLEN)
    m.viga('cabeza', (-1.6, 28.4, 3.6), (-1.9, 28.7, 5.2), 0.5, B.liso('tallo_flor', TALLO))
    m.hoja('cabeza', (-2.0, 28.8, 5.3), 3.4, 3.4, flor, rot=(0, 0, 15))
    m.caja('cabeza', (-2.0, 28.8, 5.45), (0.9, 0.9, 0.5), centro)
    # Una raíz que le cuelga de la boca.
    m.viga('cabeza', (0.8, 25.8, 4.1), (1.1, 23.2, 4.4), 0.45, raiz_p)
    # Lo que le brota de la cabeza: flores y hojas.
    m.parte('brotes', 'cabeza', (0, 32, 0))
    for (x, z, a) in ((-2.4, 1.4, 20), (2.2, -1.6, -30), (0.4, -2.8, 70)):
        m.viga('brotes', (x, 32.6, z), (x * 1.2, 35.6, z * 1.2), 0.5, B.liso('tallo_flor', TALLO))
        m.hoja('brotes', (x * 1.2, 35.9, z * 1.2), 3.2, 3.2, flor, rot=(70, a, 0))
        m.caja('brotes', (x * 1.2, 36.1, z * 1.2), (0.8, 0.8, 0.8), centro)
    for (x, z, a, incl) in ((3.2, 2.6, 60, 50), (-3.4, -2.4, 230, 55), (0.6, 3.4, 10, 40), (-3.0, 2.0, 300, 60)):
        hoja_hacia(m, 'brotes', (x, 32.8, z), a, incl, 2.0, 3.8, hoja)
    # El arbolito del hombro (a la espalda).
    m.parte('arbolito', 'cuerpo', (-2.4, 23.4, -2.2))
    m.viga('arbolito', (-2.4, 23.4, -2.2), (-4.4, 30.4, -4.2), 1.0, raiz_p, extra=0.3)
    m.viga('arbolito', (-3.6, 27.6, -3.4), (-1.6, 31.0, -5.2), 0.6, raiz_p)
    copa = B.trazo('copa_zombi', lambda xs, ys, tw, th, c, s: np.where(((xs * 3 + ys * 5) % 7) == 0, 4,
                                                                    np.where((xs + ys) % 3 == 0, 2, 3)), HOJA)
    m.ovalo('arbolito', (-4.6, 31.4, -4.4), (2.0, 1.6, 2.0), copa)
    m.ovalo('arbolito', (-1.6, 31.6, -5.4), (1.4, 1.2, 1.4), copa)
    # Los brazos, por delante: hiedra enroscada, una hoja y los dedos de raíz.
    for lado, ld in LADOS:
        n = m.parte(f'brazo_{ld}', 'cuerpo', (lado * 5, 22, 0))
        m.caja_desde(n, (lado * 6, 22, -2), (4, 12, 4), pint, rot=(90, 0, 0))
        for k in range(5):
            z0 = -1.4 + k * 2.2
            a0 = k * 1.5 + (0 if lado > 0 else 0.8)
            a1 = a0 + 1.5
            m.viga(n, (lado * 6 + math.cos(a0) * 2.4, 22 + math.sin(a0) * 2.4, z0),
                   (lado * 6 + math.cos(a1) * 2.4, 22 + math.sin(a1) * 2.4, z0 + 2.2), 0.6, hiedra)
        hoja_hacia(m, n, (lado * 8.0, 21.4, 4.0), lado * 90, 60, 1.8, 3.4, hoja)
        for k, dx in enumerate((-1.2, 0.0, 1.2)):
            m.viga(n, (lado * 6 + dx, 20.3, 9.4), (lado * 6 + dx * 1.3, 17.4 - k % 2, 10.0), 0.45, raiz_p)
        p = m.parte(f'pierna_{ld}', 'cuerpo', (lado * 2, 12, 0))
        m.caja_desde(p, (lado * 2, 0, 0), (4, 12, 4), pantalon)
        # Las raíces de los pies, hacia el suelo.
        for (dx, dz) in ((lado * 2.2, 1.6), (lado * 1.0, 2.4), (lado * 2.4, -1.4)):
            m.viga(p, (lado * 2 + dx * 0.6, 1.2, dz * 0.6), (lado * 2 + dx * 1.3, -0.2, dz * 1.4), 0.6, raiz_p)
    m.mirar(('cabeza', 1.0))
    a = m.anim('andar', 1.0, bucle=True)
    a.onda('pierna_d', 'r', 0, 30)
    a.onda('pierna_i', 'r', 0, 30, fase=0.5)
    a.onda('brazo_d', 'r', 0, 6, fase=0.5)
    a.onda('brazo_i', 'r', 0, 6)
    a.onda('arbolito', 'r', 2, 6, periodo=0.5)
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('brotes', 'r', 2, 5)
    s.onda('arbolito', 'r', 0, 4, periodo=1.5)
    s.onda('brazo_d', 'r', 2, 3, periodo=1.5)
    s.onda('brazo_i', 'r', 2, -3, periodo=1.5, fase=0.3)
    at = m.anim('ataque', 0.5)
    for ld in ('d', 'i'):
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, -25, 0, 0), (0.3, 30, 0, 0), (0.5, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.3, 8, 0, 0), (0.5, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.6, -70, 0, 6), (1.0, -88, 0, 8)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, -2)])
    m.paso = 2.0

    def dib(px, filas, c):
        for x, f in ((9, 5),):
            px[x, f] = c('fff060')
        for x, f in ((5, 5), (6, 5), (5, 4), (6, 6)):
            px[x, f] = c('d84a8a')
        for x, f in ((4, 2), (7, 1), (10, 2)):
            px[x, f] = c('d84a8a')
        for x in range(5, 11):
            px[x, 9] = c('1e6a6a')
    return terminar(m, raiz, 'Zombi Planta', 'Plant Zombie', (('7aac5e', '588c48', '3e6e36'), ('1a3a1a', '0a1a0a'), dib),
                    ((1.1, 2.0, 2.0), (0, 1.3, 0)),
                    particulas=(('polen', chispa((232, 196, 26))), ('hoja', esquirla((62, 138, 38))),
                                ('raiz', esquirla((122, 92, 54)))),
                    poses=[('andar', 0.25), ('andar', 0.75), ('ataque', 0.3), ('muerte', 1.0)])


MOBS = {}
for _c in COLORES:
    MOBS[f'fauces_{_c}'] = (lambda c: lambda raiz: fauces(raiz, c))(_c)
MOBS['trampa'] = trampa
MOBS['pina'] = pina
MOBS['zombi_planta'] = zombi_planta


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    for p in pedidos:
        MOBS[p](raiz)


if __name__ == '__main__':
    main()
