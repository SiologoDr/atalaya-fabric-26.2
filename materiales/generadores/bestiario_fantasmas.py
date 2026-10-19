"""
Los fantasmas del bestiario (18-10-2026): los del Limbo y los que te mandan a él (DEDsafío 3 y 4), con nuestro diseño.
Casi todos flotan y son de tela translúcida (se pintan en dos pasadas, como la Gelatina: lo opaco y el gel encima), con
los ojos encendidos.

  espectro_rojo      sudario carmín hecho jirones, capucha con la cara negra y dos ojos de brasa, brazos largos que se
                     estiran con garras; va inclinado hacia delante, con prisa
  espectro_blanco    blanco escarcha, sin capucha: una máscara de porcelana (ojos negros y una raya de boca) y el pelo
                     largo y blanco que le cae por la espalda; mangas anchas
  espectro_negro     humo negro con reflejos violeta, ojos violeta y, en el pecho, un hueco con un corazón rojo que late
                     (los que roba)
  espectro_amarillo  dorado, con una sonrisa enorme de dientes encendidos y el cuerpo que acaba en una sola cola en
                     espiral (por ahí se te mete dentro)
  parca_menor        una parca chica: túnica negra, la calavera blanca con dos puntos rojos y su hoz pequeña
  parca              la grande: túnica negra rota, calavera con ojos de brasa, manos de hueso y una guadaña enorme con el
                     filo encendido
  murcielago_vampiro un murciélago grande de pelo granate, orejas en punta, ojos rojos, colmillos y alas de membrana

Uso: python bestiario_fantasmas.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
from bestiario import rampa
from bestiario import brizna

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))


def juntar(*rampas):
    return np.vstack(rampas)


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('siempre', 0.5), ('ataque', 0.2), ('ataque', 0.35), ('muerte', 0.6)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


def hoja_hacia(m, parte, base, a, incl, ancho, alto, pint):
    """Una hoja que nace en 'base' y sale hacia el rumbo 'a' (grados, 0 = adelante), inclinada 'incl' desde la vertical
    (más de 90, hacia abajo). La punta de la textura (su fila de arriba) queda en la punta."""
    ar, ir = math.radians(a), math.radians(incl)
    up = np.array((math.sin(ir) * math.sin(ar), math.cos(ir), math.sin(ir) * math.cos(ar)))
    m.hoja(parte, tuple(np.asarray(base, float) + up * alto / 2), ancho, alto, pint, rot=(incl, a, 0))


def colmillo(m, parte, base, hacia, tangente, largo, ancho, pint):
    base = np.asarray(base, float)
    m.dientes(parte, base, base + np.asarray(tangente, float) * 0.01, 1, largo, hacia, pint, ancho=ancho)


# ======================================================================================================================
#  Los materiales
# ======================================================================================================================
def tela(nombre, r, alfa=170, pliegue=3, roto=True):
    """Tela de sudario: pliegues verticales (una raya oscura y, al lado, el brillo), el canto de abajo más oscuro y algún
    roto (transparente) cerca del borde de abajo. 'alfa' < 255 la hace translúcida (va al gel)."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        g = B._azar(s * 11 + tw + th * 3)
        idx = np.full((th, tw), 2)
        fase = int(g.integers(0, pliegue))
        idx[((xs + fase) % pliegue) == 0] = 1
        idx[((xs + fase) % pliegue) == 1] = 3
        if cara == 'arriba':
            idx[...] = 3
        idx[ys == th - 1] = np.minimum(idx[ys == th - 1], 1)
        tex = B._img(idx, r)
        a = np.full((th, tw), alfa, int)
        a[idx == 3] = min(254, alfa + 25)
        if roto and cara not in ('arriba', 'abajo') and th >= 4:
            for _ in range(max(1, tw // 5)):
                x = int(g.integers(0, tw))
                largo = int(g.integers(1, max(2, th // 3)))
                a[th - largo:, x] = 0
        tex[..., 3] = a
        return tex, None
    return B.Pintor(nombre, fn)


def jiron(nombre, r, alfa=160):
    """Un jirón de tela (en una hoja): ancho arriba (donde nace) y roto en punta abajo; la fila de arriba de la textura es
    la punta."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        g = B._azar(s * 7 + 3)
        u = (xs + 0.5) / tw
        v = (ys + 0.5) / th          # 0, la punta; 1, la raíz
        borde = np.array([g.uniform(-0.12, 0.12) for _ in range(th)])[:, None]
        dentro = np.abs(u - 0.5 + borde * (1 - v)) < 0.5 * (0.25 + 0.75 * v)
        idx = np.where(((xs + int(s)) % 3) == 0, 1, 2)
        idx = np.where(v < 0.2, 1, idx)
        tex = B._img(idx, r)
        tex[..., 3] = np.where(dentro, alfa, 0)
        return tex, None
    return B.Pintor(nombre, fn)


HUESO = rampa('6a6254', '9a907a', 'c8bea4', 'e6dcc4', 'f8f2e2')
NEGRO = rampa('050307', '0c0910', '15111b', '201a28', '2c2436')
HIERRO = rampa('1a1a1e', '2c2c32', '42424a', '5c5c66', '7a7a86')


def ojo_luz(nombre, centro, borde):
    return B.luz(nombre, rampa(borde, borde, centro, centro, 'ffffff'))


# ======================================================================================================================
#  El cuerpo de espectro
# ======================================================================================================================
def sudario(m, parte, y0, y1, perfil, pint, cortes=8, z=0.0):
    """El sudario: rebanadas de abajo arriba (dos cajas cruzadas cada una, octogonal vista desde arriba) del radio que
    da perfil(t) (t: 0 abajo, 1 arriba) -> (rx, rz)."""
    h = (y1 - y0) / cortes
    for k in range(cortes):
        t = (k + 0.5) / cortes
        rx, rz = perfil(t)
        y = y0 + h * (k + 0.5)
        m.caja(parte, (0, y, z), (2 * rx, h + 0.04, 2 * rz * 0.76), pint)
        m.caja(parte, (0, y, z), (2 * rx * 0.76, h + 0.04, 2 * rz), pint)


def pliegue(nombre, r, alfa=170, rota=True):
    """Un panel de tela de la túnica: el pliegue (una raya oscura en medio y los cantos claros), y si 'rota', el borde de
    abajo deshilachado (transparente a picos). La fila de arriba de la textura es la de arriba del panel."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        g = B._azar(s * 5 + tw * 3)
        idx = np.full((th, tw), 2)
        idx[xs == tw // 2] = 1
        idx[(xs == 0) | (xs == tw - 1)] = 3
        if cara in ('arriba', 'abajo'):
            idx[...] = 1
        tex = B._img(idx, r)
        a = np.full((th, tw), alfa, int)
        a[idx == 3] = min(254, alfa + 25)
        if rota and cara not in ('arriba', 'abajo'):
            for x in range(tw):
                largo = int(g.integers(0, max(2, th // 4)))
                if largo:
                    a[th - largo:, x] = 0
        tex[..., 3] = a
        return tex, None
    return B.Pintor(nombre, fn)


def tunica(m, parte, y_alto, y_bajo, r_alto, r_medio, r_bajo, n, pint, pint_bajo, z=0.0, aplana=0.82, quiebre=0.5,
           grueso=0.6):
    """La túnica de paneles: n tiras de tela alrededor, cada una en dos tramos (el de arriba, del hombro a la cintura;
    el de abajo, que se abre en campana y acaba roto), tangentes al cuerpo. Devuelve el radio de abajo."""
    y_med = y_bajo + (y_alto - y_bajo) * quiebre
    for k in range(n):
        a = k * math.tau / n
        sa, ca = math.sin(a), math.cos(a)
        p0 = np.array((sa * r_alto, y_alto, z + ca * r_alto * aplana))
        p1 = np.array((sa * r_medio, y_med, z + ca * r_medio * aplana))
        p2 = np.array((sa * r_bajo, y_bajo, z + ca * r_bajo * aplana))
        w1 = math.tau * (r_alto + r_medio) / 2 / n * 1.12
        w2 = math.tau * (r_medio + r_bajo) / 2 / n * 1.12
        m.viga(parte, p0, p1, grueso, pint, ancho=w1, extra=0.3, rodar=-math.degrees(a))
        m.viga(parte, p1, p2, grueso, pint_bajo, ancho=w2, extra=0.2, rodar=-math.degrees(a))
    return r_bajo


def jirones(m, nombre, padre, y, rx, rz, n, largo, ancho, pint, fase=0.0, z=0.0):
    """Los jirones que cuelgan del borde de abajo del sudario, en su propia parte (para que ondeen)."""
    p = m.parte(nombre, padre, (0, y, z))
    for k in range(n):
        a = (k + fase) * 360.0 / n
        ar = math.radians(a)
        base = (math.sin(ar) * rx * 0.9, y + 0.4, z + math.cos(ar) * rz * 0.9)
        hoja_hacia(m, p, base, a, 168 - (k % 2) * 8, ancho, largo * (0.8 + 0.2 * ((k * 7) % 3) / 2), pint)
    return p


def pano(nombre, r, alfa=230, oscuro=False):
    """Paño liso (para lo redondeado, como la capucha: sin las rayas de los pliegues ni el canto oscuro, que en las
    rebanadas marcarían escalones): el tono de base con motas sueltas un tono más oscuras y lo de arriba más claro."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2 if not oscuro else 1)
        idx[((xs * 5 + ys * 3 + s) % 17) == 0] = 1 if not oscuro else 0
        tex = B._img(idx, r)
        tex[..., 3] = alfa
        return tex, None
    return B.Pintor(nombre, fn)


def capucha(m, parte, c, ancho, alto, fondo, pint, cara, ojos, ojo_tam=(1.2, 0.8), sep=1.7, borde=None):
    """La capucha: una cúpula de paño (rebanadas) y, por delante, la abertura: la cara oscura en arco (dos placas, la de
    arriba más estrecha) pegada a la cúpula, y el borde de tela que la enmarca (dos tiras que suben y se juntan arriba)
    adelantado un píxel, que es lo que le da hondura. Los ojos, encendidos sobre la cara. Devuelve la z de la cara (para
    poner encima una máscara o una calavera)."""
    cx, cy, cz = c
    r = ancho / 2
    n = 8
    h = alto / n
    for k in range(n):
        y = -alto / 2 + h * (k + 0.5)
        f = math.sqrt(max(0.08, 1.0 - (y / (alto / 2 * 1.1)) ** 2))
        w = r * f * 1.04
        m.caja(parte, (cx, cy + y, cz - 0.4), (2 * w, h + 0.04, fondo * f * 0.78), pint)
        m.caja(parte, (cx, cy + y, cz - 0.4), (2 * w * 0.78, h + 0.04, fondo * f), pint)
    zf = cz - 0.4 + fondo / 2
    borde = borde or pint
    if cara is not None:
        m.caja(parte, (cx, cy - alto * 0.12, zf + 0.25), (ancho * 0.6, alto * 0.52, 0.5), cara)
        m.caja(parte, (cx, cy + alto * 0.2, zf + 0.2), (ancho * 0.36, alto * 0.16, 0.5), cara)
    for lado in (-1, 1):
        a0 = np.array((cx + lado * ancho * 0.35, cy - alto * 0.42, zf + 0.75))
        a1 = np.array((cx + lado * ancho * 0.33, cy + alto * 0.06, zf + 0.8))
        a2 = np.array((cx, cy + alto * 0.36, zf + 0.75))
        m.viga(parte, a0, a1, 1.3, borde, ancho=1.3, extra=0.3)
        m.viga(parte, a1, a2, 1.3, borde, ancho=1.3, extra=0.5)
    if ojos is not None:
        for lado in (-1, 1):
            m.caja(parte, (cx + lado * sep / 2, cy - 0.1, zf + 0.55), (ojo_tam[0], ojo_tam[1], 0.2), ojos)
    m.viga(parte, (cx, cy + alto / 2 - 0.6, cz - fondo / 2 + 0.6), (cx, cy + alto / 2 + 0.2, cz - fondo / 2 - 1.8), 1.8,
           pint)
    return zf + 0.5


def brazo(m, nombre, padre, lado, hombro, codo, mano, grueso, manga, mano_p, garra_p, dedos=3, largo_garra=2.2):
    """Un brazo de espectro: la manga en dos tramos (que se ensancha en la muñeca, como una manga de túnica), la mano
    de hueso con sus dedos y las garras."""
    p = m.parte(nombre, padre, tuple(hombro))
    hombro, codo, mano = (np.asarray(v, float) for v in (hombro, codo, mano))
    m.viga(p, hombro, codo, grueso, manga, extra=0.4)
    m.viga(p, codo, mano, grueso * 1.25, manga, extra=0.2)
    d = mano - codo
    d = d / np.linalg.norm(d)
    # El puño de la manga, que se abre en campana.
    m.viga(p, mano - d * 1.4, mano + d * 0.2, grueso * 1.7, manga)
    palma = mano + d * 0.6
    m.caja(p, tuple(palma), (1.3, 1.3, 1.3), mano_p)
    lado_v = np.cross(d, (0, 1, 0))
    if np.linalg.norm(lado_v) < 1e-3:
        lado_v = np.array((1.0, 0, 0))
    lado_v = lado_v / np.linalg.norm(lado_v)
    for k in range(dedos):
        off = (k - (dedos - 1) / 2) * 0.55
        raiz = palma + lado_v * off + d * 0.5
        punta = raiz + d * 1.6 + np.array((0, -0.6, 0))
        m.viga(p, raiz, punta, 0.38, mano_p)
        colmillo(m, p, punta, d * 0.6 + np.array((0, -1, 0)), lado_v, largo_garra, 0.4, garra_p)
    return p


def anims_espectro(m, cuerpo='cuerpo', colas=('colas',), brazos=('brazo_i', 'brazo_d'), cabeza='cabeza', flota=1.4,
                   prisa=10, golpe='garras'):
    """Las animaciones de un espectro: flota (sube y baja), las colas ondean, los brazos se mecen; al andar se inclina;
    al atacar, el zarpazo (o el golpe de dos manos); al morir se deshace subiendo; al aparecer, crece del suelo."""
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda(cuerpo, 'm', 1, flota, periodo=3.0)
    for k, c in enumerate(colas):
        s.onda(c, 'r', 0, 9, periodo=1.5, fase=0.25 * k)
        s.onda(c, 'r', 2, 6, periodo=3.0, fase=0.1 + 0.3 * k)
    for k, b in enumerate(brazos):
        s.onda(b, 'r', 0, 5, periodo=3.0, fase=0.5 * k)
    if cabeza:
        s.onda(cabeza, 'r', 2, 4, periodo=6.0 / 2)
    a = m.anim('andar', 1.0, bucle=True)
    a.onda(cuerpo, 'r', 0, 2, base=prisa)
    for c in colas:
        a.onda(c, 'r', 0, 6, base=20)
    at = m.anim('ataque', 0.5)
    if golpe == 'garras':
        bi, bd = brazos[0], brazos[1]
        at.rot(bi, [(0, 0, 0, 0), (0.12, -55, -15, 0), (0.25, 35, 10, 0), (0.5, 0, 0, 0)])
        at.rot(bd, [(0, 0, 0, 0), (0.18, -55, 15, 0), (0.32, 35, -10, 0), (0.5, 0, 0, 0)])
    else:
        for b in brazos:
            at.rot(b, [(0, 0, 0, 0), (0.15, -70, 0, 0), (0.28, 30, 0, 0), (0.5, 0, 0, 0)])
    at.rot(cuerpo, [(0, 0, 0, 0), (0.12, -8, 0, 0), (0.25, 14, 0, 0), (0.5, 0, 0, 0)])
    at.mov(cuerpo, [(0, 0, 0, 0), (0.25, 0, 0, 2.0), (0.5, 0, 0, 0)])
    d = m.anim('muerte', 1.2)
    d.mov(cuerpo, [(0, 0, 0, 0), (1.2, 0, 10, 0)])
    d.rot(cuerpo, [(0, 0, 0, 0), (1.2, 0, 160, 0)])
    d.esc(cuerpo, [(0, 1, 1, 1), (0.4, 1.1, 0.9, 1.1), (1.2, 0.05, 1.6, 0.05)])
    ap = m.anim('aparece', 0.8)
    ap.mov(cuerpo, [(0, 0, -12, 0), (0.8, 0, 0, 0)])
    ap.esc(cuerpo, [(0, 0.2, 0.2, 0.2), (0.6, 1.1, 1.1, 1.1), (0.8, 1, 1, 1)])


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


def voluta(color, n=16):
    """Una voluta de tela o de humo: una mancha alargada y deshilachada."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            u, v = x - 0.5, y - 0.5
            d = np.hypot(u * (1.0 + 0.3 * k), v * 1.6)
            borde = 0.36 + 0.06 * np.sin(np.arctan2(v, u) * 5 + k)
            a = (d < borde) * (150 - 30 * k)
            return (color[0], color[1], color[2], a)
        cuadros.append(B.sprite(n, f))
    return cuadros


# ======================================================================================================================
#  Los espectros
# ======================================================================================================================
def espectro(raiz, ident, R, ojos_c, nombre_es, nombre_en, extra=None, alfa=165, retrato=None, huevo=None,
             particulas=(), cara='capucha', inclinado=12, post=None):
    m = B.Modelo(ident, K=2, ancho=128)
    m.translucido = True
    T = tela(f'tela_{ident}', R, alfa)
    Tc = pano(f'capucha_{ident}', R, 255)
    Tb = pano(f'borde_{ident}', R, 255, oscuro=True)
    J = jiron(f'jiron_{ident}', R, alfa - 10)
    ojos = ojo_luz(f'ojos_{ident}', *ojos_c)
    # El cuerpo flota: su raíz va a 4 píxeles del suelo (las colas llegan casi al suelo).
    y0, y1 = 7.0, 25.0
    m.parte('cuerpo', None, (0, 20, 0), rot=(inclinado, 0, 0))

    P = pliegue(f'pliegue_{ident}', R, alfa, rota=False)
    Pb = pliegue(f'pliegue_bajo_{ident}', R, alfa - 10, rota=True)
    tunica(m, 'cuerpo', y1, y0, 3.8, 4.6, 5.6, 10, P, Pb)
    # Los hombros (un casquete que cierra la túnica por arriba).
    m.caja('cuerpo', (0, y1 - 0.4, 0), (8.2, 1.6, 6.2), T)
    m.caja('cuerpo', (0, y1 - 0.4, 0), (6.2, 1.6, 7.4), T)
    jirones(m, 'colas', 'cuerpo', y0 + 1.0, 4.8, 3.9, 7, 5.5, 2.4, J)
    m.parte('cabeza', 'cuerpo', (0, y1, 0.6))
    if cara == 'capucha':
        capucha(m, 'cabeza', (0, y1 + 3.2, 0.8), 7.4, 7.0, 7.0, Tc, B.liso(f'cara_{ident}', NEGRO, base=1), ojos,
                borde=Tb)
    for lado, ld in LADOS:
        hombro = (lado * 4.2, y1 - 1.5, 0.6)
        codo = (lado * 5.4, y1 - 5.0, 4.0)
        mano = (lado * 4.6, y1 - 7.0, 8.2)
        brazo(m, f'brazo_{ld}', 'cuerpo', lado, hombro, codo, mano, 1.8, T,
              B.hueso(f'mano_{ident}', HUESO), B.diente(f'garra_{ident}', NEGRO))
    if extra:
        extra(m, y0, y1)
    m.mirar(('cabeza', 0.8))
    anims_espectro(m, prisa=inclinado)
    if post:
        post(m)
    return terminar(m, raiz, nombre_es, nombre_en, huevo, retrato or ((1.3, 1.6, 2.6), (0, 1.1, 0)),
                    particulas=particulas,
                    poses=[('siempre', 0.5), ('ataque', 0.12), ('ataque', 0.25), ('muerte', 0.6)])


ROJO = rampa('2a0408', '540a12', '8a1420', 'c02832', 'f05050')
BLANCO = rampa('5a6a7a', '8a9aaa', 'c0ccd8', 'e4ecf4', 'ffffff')
VACIO = rampa('06040a', '120a1c', '1e1230', '30204a', '4a3070')
ORO = rampa('5a3a04', '9a6a0a', 'd8a020', 'f6d050', 'fff4b0')


def espectro_rojo(raiz):
    def dib(px, filas, c):
        for x in range(5, 11):
            px[x, 4] = c('8a1420')
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('ffe080')
        for f in range(9, 14):
            px[4, f] = px[11, f] = c('c02832')
    return espectro(raiz, 'espectro_rojo', ROJO, ('ffd060', 'ff8020'), 'Espectro Rojo', 'Red Wraith',
                    huevo=(('f05050', 'c02832', '8a1420'), ('2a0408', '140204'), dib),
                    particulas=(('brasa', chispa((255, 120, 60))), ('jiron', voluta((192, 40, 50)))))


def espectro_blanco(raiz):
    def extra(m, y0, y1):
        # Dentro de la capucha, la máscara de porcelana (dos crucetas: los ojos negros, la raya de la boca y una lágrima
        # pintada), y la melena blanca que se le sale por delante y le cae por el pecho.
        cy = y1 + 3.2
        zcara = 0.8 - 0.4 + 7.0 / 2 + 0.5
        porcelana = B.trazo('mascara_blanco', lambda xs, ys, tw, th, c, s_: _mascara(xs, ys, tw, th, c), rampa(
            '000000', '1a1a20', 'c8ccd4', 'eef2f6', 'ffffff'))
        m.caja('cabeza', (0, cy - 0.5, zcara + 0.25), (3.6, 4.2, 0.4), porcelana)
        m.caja('cabeza', (0, cy - 0.5, zcara + 0.2), (2.8, 4.8, 0.4), porcelana)
        pelo = jiron('pelo_blanco', rampa('8a96a6', 'b8c4d2', 'dce4ee', 'f4f8fc', 'ffffff'), 240)
        for lado in (-1, 1):
            for k, x in enumerate((2.3, 1.6)):
                hoja_hacia(m, 'cabeza', (lado * x, cy + 0.6 - k * 0.4, zcara + 0.4 + k * 0.2), lado * 10, 176, 1.5,
                           9.0 + k * 3.0, pelo)

    def dib(px, filas, c):
        for x in range(5, 11):
            for f in (3, 4, 5, 6):
                px[x, f] = c('eef2f6')
        for x, f in ((6, 4), (9, 4)):
            px[x, f] = c('000000')
        for x in (7, 8):
            px[x, 6] = c('1a1a20')
    return espectro(raiz, 'espectro_blanco', BLANCO, ('ffffff', '9ad8ff'), 'Espectro Blanco', 'White Wraith',
                    extra=extra, alfa=150,
                    huevo=(('ffffff', 'e4ecf4', 'c0ccd8'), ('5a6a7a', '2a3440'), dib),
                    particulas=(('escarcha', chispa((200, 230, 255))), ('jiron', voluta((228, 236, 244)))))


def _mascara(xs, ys, tw, th, cara):
    idx = np.full((th, tw), 3)
    idx[ys == 0] = 4
    if cara == 'frente':
        u, v = (xs + 0.5) / tw, (ys + 0.5) / th
        ojo = ((np.abs(u - 0.3) < 0.11) | (np.abs(u - 0.7) < 0.11)) & (np.abs(v - 0.38) < 0.09)
        boca = (np.abs(u - 0.5) < 0.18) & (np.abs(v - 0.72) < 0.03)
        lagrima = (np.abs(u - 0.3) < 0.03) & (v > 0.45) & (v < 0.62)
        idx[ojo] = 0
        idx[boca | lagrima] = 1
    return idx


def espectro_negro(raiz):
    def extra(m, y0, y1):
        # El hueco del pecho con el corazón rojo que late (en su parte, para que lata).
        m.caja('cuerpo', (0, y1 - 4.5, 4.0), (3.6, 3.6, 0.6), B.liso('hueco_negro', NEGRO, base=0))
        m.parte('corazon', 'cuerpo', (0, y1 - 4.5, 4.3))
        latido = B.luz('corazon_negro', rampa('5a0008', '8a0010', 'd0102a', 'ff4a60', 'ffc0c8'))
        m.caja('corazon', (0, y1 - 4.3, 4.35), (1.8, 1.4, 0.8), latido)
        m.caja('corazon', (0, y1 - 5.2, 4.35), (1.0, 0.8, 0.8), latido)
        for lado in (-1, 1):
            m.caja('corazon', (lado * 0.5, y1 - 3.6, 4.35), (0.9, 0.6, 0.8), latido)

    def post(m):
        # El corazón late (dos golpes por segundo, el «pum-pum»).
        claves = []
        for k in range(3):
            t0 = k * 1.0
            claves += [(t0, 1, 1, 1), (t0 + 0.1, 1.35, 1.35, 1.35), (t0 + 0.22, 1, 1, 1), (t0 + 0.34, 1.2, 1.2, 1.2),
                       (t0 + 0.5, 1, 1, 1)]
        claves.append((3.0, 1, 1, 1))
        m.anims['siempre'].esc('corazon', claves)

    def dib(px, filas, c):
        for x in range(5, 11):
            px[x, 4] = c('1e1230')
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('c080ff')
        for x, f in ((7, 10), (8, 10), (7, 11), (8, 11), (6, 10), (9, 10)):
            px[x, f] = c('d0102a')
    m = espectro(raiz, 'espectro_negro', VACIO, ('e0c0ff', '9040ff'), 'Espectro Negro', 'Black Wraith',
                 extra=extra, alfa=185, post=post,
                 huevo=(('30204a', '1e1230', '120a1c'), ('06040a', '000000'), dib),
                 particulas=(('humo', voluta((40, 28, 60))), ('corazon', chispa((220, 30, 50)))))
    return m


def espectro_amarillo(raiz):
    def extra(m, y0, y1):
        # La sonrisa: una boca negra ancha con los dientes encendidos.
        cy = y1 + 3.2
        zcara = 0.8 - 0.4 + 7.0 / 2 + 0.5
        dientes = B.luz('dientes_amarillo', rampa('d8a020', 'f6d050', 'fff4b0', 'ffffff', 'ffffff'))
        # La sonrisa: una media luna de dientes encendidos, de oreja a oreja (en el fondo de la capucha).
        for k in range(7):
            x = -2.1 + k * 0.7
            y = cy - 1.7 + 0.12 * (x * x)
            m.caja('cabeza', (x, y, zcara + 0.1), (0.55, 0.9 if k % 2 else 0.6, 0.2), dientes)
        # La cola en espiral (en vez de jirones sueltos): rebanadas que bajan girando.
        m.parte('espiral', 'cuerpo', (0, y0, 0))
        T = tela('espiral_amarillo', ORO, 170, roto=False)
        for k in range(7):
            t = k / 6
            a = math.radians(k * 55)
            r = 2.6 * (1 - t) + 0.5
            m.caja('espiral', (math.sin(a) * 1.4 * t, y0 - 1.0 - k * 1.4, math.cos(a) * 1.4 * t), (2 * r, 1.5, 2 * r),
                   T, rot=(0, k * 30, 0))

    def dib(px, filas, c):
        for x in range(5, 11):
            px[x, 4] = c('9a6a0a')
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('ff8020')
        for x in range(5, 11):
            px[x, 8] = c('000000')
        for x in (6, 8, 10):
            px[x, 8] = c('fff4b0')
    return espectro(raiz, 'espectro_amarillo', ORO, ('fff0a0', 'ff9020'), 'Espectro Amarillo', 'Yellow Wraith',
                    extra=extra, alfa=165,
                    huevo=(('fff4b0', 'f6d050', 'd8a020'), ('5a3a04', '2a1a02'), dib),
                    particulas=(('chispa', chispa((255, 220, 90))), ('jiron', voluta((216, 160, 32)))))


# ======================================================================================================================
#  Las parcas
# ======================================================================================================================
TUNICA = rampa('050407', '0e0b12', '18141e', '24202c', '322c3c')


def calavera(m, parte, c, tam, ojos):
    """Una calavera en relieve (para dentro de la capucha): el cráneo y la mandíbula en placas de hueso, las cuencas
    negras con su punto encendido, la nariz y los dientes. 'c' es el centro de su cara de atrás."""
    cx, cy, cz = c
    hueso = B.hueso('craneo', HUESO)
    m.caja(parte, (cx, cy + tam * 0.12, cz + 0.45), (tam, tam * 0.78, 0.9), hueso)
    m.caja(parte, (cx, cy - tam * 0.38, cz + 0.4), (tam * 0.7, tam * 0.3, 0.8), hueso)
    zf = cz + 0.92
    negro = B.liso('cuenca', NEGRO, base=0)
    for lado in (-1, 1):
        m.caja(parte, (cx + lado * tam * 0.22, cy + tam * 0.08, zf), (tam * 0.28, tam * 0.24, 0.12), negro)
        m.caja(parte, (cx + lado * tam * 0.22, cy + tam * 0.06, zf + 0.06), (tam * 0.1, tam * 0.1, 0.12), ojos)
    m.caja(parte, (cx, cy - tam * 0.14, zf), (tam * 0.12, tam * 0.14, 0.12), negro)
    dientes = B.diente('dientes_calavera', HUESO)
    m.dientes(parte, (cx - tam * 0.26, cy - tam * 0.26, zf - 0.02), (cx + tam * 0.26, cy - tam * 0.26, zf - 0.02), 5,
              tam * 0.12, (0, -1, 0), dientes, ancho=tam * 0.08)


def guadana(m, parte, mano, largo, hoja_largo, mango_p, hoja_p, filo_p, inclina=10):
    """La guadaña (o la hoz): el mango de madera oscura en la mano y, arriba, la hoja curva (tres tramos que se doblan
    hacia delante) con el filo encendido."""
    mano = np.asarray(mano, float)
    arriba = mano + np.array((0, largo * 0.62, -0.4))
    abajo = mano + np.array((0, -largo * 0.38, 0.4))
    m.viga(parte, abajo, arriba, 0.8, mango_p)
    # La hoja sale de arriba hacia delante y se curva hacia abajo.
    p0 = arriba
    tramos = ((0.36, 0.0), (0.34, -25.0), (0.3, -55.0))
    ang = -inclina
    for k, (f, giro) in enumerate(tramos):
        ang += giro
        a = math.radians(ang)
        d = np.array((0, math.sin(a), math.cos(a)))
        p1 = p0 + d * hoja_largo * f
        ancho = 1.8 - k * 0.5
        m.viga(parte, p0, p1, 0.35, hoja_p, ancho=ancho)
        # El filo (por debajo de la hoja), encendido.
        m.viga(parte, p0 + np.array((0, -ancho * 0.5, 0)), p1 + np.array((0, -ancho * 0.45, 0)), 0.4, filo_p,
               ancho=0.4)
        p0 = p1


def parca(raiz, ident='parca', chica=False):
    m = B.Modelo(ident, K=2, ancho=128)
    m.translucido = True
    k = 0.62 if chica else 1.0
    m.escala = 1.0
    T = tela(f'tunica_{ident}', TUNICA, 215)
    J = jiron(f'jiron_{ident}', TUNICA, 190)
    ojos = ojo_luz(f'ojos_{ident}', 'ff6040', 'c01010')
    y0, y1 = 6.0 * k + 2, 34.0 * k + 2
    m.parte('cuerpo', None, (0, y1 - 6 * k, 0), rot=(6, 0, 0))

    P = pliegue(f'pliegue_{ident}', TUNICA, 225, rota=False)
    Pb = pliegue(f'pliegue_bajo_{ident}', TUNICA, 205, rota=True)
    tunica(m, 'cuerpo', y1, y0, 4.4 * k, 5.4 * k, 6.8 * k, 12 if not chica else 10, P, Pb, quiebre=0.55,
           grueso=0.7 * k + 0.2)
    m.caja('cuerpo', (0, y1 - 0.5, 0), (9.6 * k, 1.8, 7.2 * k), T)
    m.caja('cuerpo', (0, y1 - 0.5, 0), (7.2 * k, 1.8, 8.6 * k), T)
    jirones(m, 'colas', 'cuerpo', y0 + 1.2, 6.0 * k, 4.9 * k, 8, 6.0 * k + 1.5, 2.8 * k + 0.4, J)
    m.parte('cabeza', 'cuerpo', (0, y1, 0.4))
    # La capucha (la cara, negra y honda, con la calavera dentro).
    cy = y1 + 4.0 * k
    Tc = pano(f'capucha_{ident}', TUNICA, 245)
    zcara = capucha(m, 'cabeza', (0, cy, 0.4 * k), 9.0 * k, 8.8 * k, 8.6 * k, Tc, B.liso(f'cara_{ident}', NEGRO, base=0),
                    None, borde=pano(f'borde_{ident}', TUNICA, 255, oscuro=False))
    calavera(m, 'cabeza', (0, cy - 0.7 * k, zcara - 0.1), 4.4 * k, ojos)
    # Los brazos: el derecho con la guadaña, el izquierdo con la mano de hueso abierta.
    mango = B.anillos(f'mango_{ident}', rampa('140c08', '24160e', '382214', '4c301c', '603e24'), paso=3)
    hoja = B.metal(f'hoja_{ident}', rampa('1a1c22', '30343e', '4c5260', '707888', '9aa2b2'), panel=6)
    filo = B.luz(f'filo_{ident}', rampa('6a2a8a', '9a4ad0', 'd0a0ff', 'f4e8ff', 'ffffff'))
    for lado, ld in LADOS:
        hombro = (lado * 5.0 * k, y1 - 2.0 * k, 0.4)
        codo = (lado * 6.4 * k, y1 - 8.0 * k, 3.0 * k)
        mano = (lado * 5.6 * k, y1 - 11.0 * k, 6.8 * k)
        p = brazo(m, f'brazo_{ld}', 'cuerpo', lado, hombro, codo, mano, 2.4 * k, T, B.hueso(f'mano_{ident}', HUESO),
                  B.diente(f'una_{ident}', HUESO), dedos=4, largo_garra=1.2 * k + 0.4)
        if lado < 0:
            guadana(m, p, (mano[0], mano[1] + 0.4, mano[2] + 0.8), (30.0 if not chica else 16.0) * (1 if not chica else 1),
                    (16.0 if not chica else 8.5), mango, hoja, filo)
    m.mirar(('cabeza', 0.7))
    anims_espectro(m, flota=1.0 if not chica else 1.4, prisa=6, golpe='guadana')
    # El golpe de guadaña: el brazo derecho (el de la guadaña) sube por encima de la cabeza y baja de un tajo.
    at = m.anims['ataque']
    at.canales = [c for c in at.canales if c[0] not in ('brazo_d',)]
    at.rot('brazo_d', [(0, 0, 0, 0), (0.15, -150, 0, 20), (0.3, 30, 0, -10), (0.5, 0, 0, 0)])

    def dib(px, filas, c):
        for x in range(5, 11):
            for f in range(3, 8):
                px[x, f] = c('e6dcc4')
        for x, f in ((6, 5), (9, 5)):
            px[x, f] = c('c01010')
        for f in range(2, 14):
            px[12, f] = c('382214')
        for x in (9, 10, 11):
            px[x, 2] = c('d0a0ff')
    nombre = ('Parca Menor', 'Lesser Reaper') if chica else ('Parca', 'Reaper')
    return terminar(m, raiz, nombre[0], nombre[1], (('322c3c', '24202c', '18141e'), ('050407', '000000'), dib),
                    ((1.3, 1.6, 2.6), (0, 1.0, 0)) if chica else ((1.9, 2.6, 3.8), (0, 1.6, 0)),
                    particulas=(('alma', chispa((208, 160, 255))), ('jiron', voluta((36, 32, 44)))),
                    poses=[('siempre', 0.5), ('ataque', 0.15), ('ataque', 0.3), ('muerte', 0.6)])


def parca_menor(raiz):
    return parca(raiz, 'parca_menor', chica=True)


def parca_grande(raiz):
    return parca(raiz, 'parca', chica=False)


# ======================================================================================================================
#  El Murciélago Vampiro
# ======================================================================================================================
PELO = rampa('1a0608', '30080e', '4a1018', '6a1a24', '8a2a32')
MEMBRANA = rampa('140608', '24080c', '3a1016', '561a22', '742a32')


def murcielago(raiz):
    m = B.Modelo('murcielago_vampiro', K=2, ancho=128)
    pelo = B.pelaje('pelo_vampiro', PELO, largo=2)
    m.parte('cuerpo', None, (0, 8, 0))
    m.ovalo('cuerpo', (0, 7.0, -0.5), (2.6, 3.2, 2.2), pelo)
    m.parte('cabeza', 'cuerpo', (0, 10.0, 0.6))
    m.ovalo('cabeza', (0, 11.2, 1.2), (2.2, 2.0, 2.0), pelo)
    # El hocico, las orejas en punta, los ojos y los colmillos.
    m.caja('cabeza', (0, 10.6, 3.2), (1.6, 1.2, 1.2), B.liso('hocico_vampiro', PELO, base=3))
    oreja = brizna('oreja_vampiro', MEMBRANA, ancho_base=1.6)
    for lado in (-1, 1):
        hoja_hacia(m, 'cabeza', (lado * 1.3, 12.6, 0.8), lado * 30, 22, 2.6, 2.8, oreja)
        m.caja('cabeza', (lado * 0.9, 11.6, 3.05), (0.8, 0.7, 0.3), ojo_luz('ojos_vampiro', 'ff4040', 'a00010'))
        colmillo(m, 'cabeza', (lado * 0.45, 10.1, 3.7), (0, -1, 0.1), (1, 0, 0), 1.0, 0.35,
                 B.diente('colmillo_vampiro'))
    # Las alas: el brazo de hueso hasta el codo y, desde ahí, tres dedos en abanico (hacia delante, hacia fuera y hacia
    # atrás); la membrana (horizontal, con el borde de atrás festoneado) va del cuerpo al codo y del codo a los dedos.
    hueso = B.anillos('dedo_vampiro', rampa('2a1a14', '3a261c', '4e3426', '644432', '7a5440'), paso=2)

    def membrana(nombre):
        def fn(tw, th, cara, s_):
            ys, xs = np.mgrid[0:th, 0:tw]
            u, v = (xs + 0.5) / tw, (ys + 0.5) / th
            idx = np.full((th, tw), 2)
            idx[(xs % 4) == 0] = 1
            idx[ys == 0] = 3
            tex = B._img(idx, MEMBRANA)
            festón = 0.82 + 0.18 * np.abs(np.sin(u * math.pi * 3))
            tex[..., 3] = np.where(v < festón, 255, 0)
            return tex, None
        return B.Pintor(nombre, fn)
    mem = membrana('membrana_vampiro')
    for lado, ld in LADOS:
        p = m.parte(f'ala_{ld}', 'cuerpo', (lado * 2.0, 8.6, 0))
        hombro = np.array((lado * 2.0, 8.6, 0.0))
        codo = np.array((lado * 6.2, 9.0, 0.6))
        m.viga(p, hombro, codo, 0.7, hueso)
        m.hoja(p, (lado * 4.0, 8.85, -1.6), 4.6, 4.4, mem, rot=(90, 0, 0))
        p2 = m.parte(f'mano_{ld}', p, tuple(codo))
        for (dx, dz) in ((3.6, 3.4), (6.0, 0.4), (4.0, -3.8)):
            punta = codo + np.array((lado * dx, 0.2, dz))
            m.viga(p2, codo, punta, 0.45, hueso)
        m.hoja(p2, (codo[0] + lado * 3.4, 9.05, -0.6), 7.4, 7.6, mem, rot=(90, 0, 0))

    # Las patitas con garras.
    for lado, ld in LADOS:
        m.viga('cuerpo', (lado * 0.9, 4.4, -0.8), (lado * 1.1, 2.6, -1.2), 0.5, hueso)
    m.mirar(('cabeza', 0.6))
    s = m.anim('siempre', 0.4, bucle=True)
    for lado, ld in LADOS:
        s.onda(f'ala_{ld}', 'r', 2, lado * 40, periodo=0.4)
        s.onda(f'mano_{ld}', 'r', 2, lado * 25, periodo=0.4, fase=0.12)
    s.onda('cuerpo', 'm', 1, 0.8, periodo=0.4, fase=0.25)
    at = m.anim('ataque', 0.4)
    at.rot('cabeza', [(0, 0, 0, 0), (0.12, -25, 0, 0), (0.22, 25, 0, 0), (0.4, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.12, 0, 1.0, -1.0), (0.22, 0, -0.5, 2.0), (0.4, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (1.0, 0, 0, 180)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -6, 0)])
    for lado, ld in LADOS:
        d.rot(f'ala_{ld}', [(0, 0, 0, 0), (1.0, 0, 0, lado * -60)])

    def dib(px, filas, c):
        for x in range(3, 13):
            px[x, 8] = c('3a1016')
        for x in (2, 13):
            px[x, 7] = c('3a1016')
        for x, f in ((7, 7), (8, 7)):
            px[x, f] = c('6a1a24')
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('ff4040')
    return terminar(m, raiz, 'Murciélago Vampiro', 'Vampire Bat', (('8a2a32', '6a1a24', '4a1018'), ('1a0608', '0a0204'),
                                                                 dib),
                    ((0.9, 0.9, 1.4), (0, 0.5, 0)),
                    particulas=(('sangre', chispa((200, 20, 30))), ('corazon', chispa((255, 60, 80)))),
                    poses=[('siempre', 0.0), ('siempre', 0.1), ('ataque', 0.15), ('muerte', 1.0)])


# ======================================================================================================================
#  El Farolero
# ======================================================================================================================
ABRIGO = rampa('10141c', '1a202a', '262e3a', '343e4c', '465264')
LLAMA_F = rampa('3a1a6a', '6a3ac0', 'a080ff', 'd8ccff', 'ffffff')


def farolero(raiz):
    """El Farolero: alto y flaco, con un abrigo largo de fantasma (gris azulado y roto por abajo) y, en vez de cabeza,
    un farol de hierro con los cristales empañados y una llama fría violeta dentro (que respira y, cuando va a reventar,
    se hincha). En la mano izquierda lleva un cayado con otro farolito colgado."""
    m = B.Modelo('farolero', K=2, ancho=128)
    m.translucido = True
    T = tela('tela_farolero', ABRIGO, 200)
    P = pliegue('pliegue_farolero', ABRIGO, 205, rota=False)
    Pb = pliegue('pliegue_bajo_farolero', ABRIGO, 190, rota=True)
    J = jiron('jiron_farolero', ABRIGO, 180)
    y0, y1 = 6.0, 28.0
    m.parte('cuerpo', None, (0, 22, 0), rot=(5, 0, 0))
    tunica(m, 'cuerpo', y1, y0, 3.6, 4.2, 5.4, 10, P, Pb, quiebre=0.55)
    m.caja('cuerpo', (0, y1 - 0.4, 0), (8.0, 1.6, 6.0), T)
    m.caja('cuerpo', (0, y1 - 0.4, 0), (6.0, 1.6, 7.2), T)
    # El cuello alto del abrigo.
    m.caja('cuerpo', (0, y1 + 0.8, 0.2), (5.0, 1.6, 4.6), T)
    jirones(m, 'colas', 'cuerpo', y0 + 1.0, 4.6, 3.8, 7, 5.0, 2.2, J)
    # La cabeza-farol: la base, cuatro barrotes de esquina, el techo con su aro, los cristales (gel) y la llama.
    hierro = B.metal('hierro_farolero', HIERRO, panel=4)
    cristal = pano('cristal_farolero', rampa('2a2a46', '3e3e66', '5a5a8a', '8080b0', 'b0b0d8'), 120)
    m.parte('cabeza', 'cuerpo', (0, y1 + 1.6, 0.2))
    cy = y1 + 1.6
    m.caja('cabeza', (0, cy + 0.5, 0.2), (6.4, 1.0, 6.4), hierro)
    for dx in (-2.8, 2.8):
        for dz in (-2.6, 3.0):
            m.caja('cabeza', (dx, cy + 4.2, dz), (0.8, 6.4, 0.8), hierro)
    m.caja('cabeza', (0, cy + 7.8, 0.2), (6.6, 1.0, 6.6), hierro)
    m.caja('cabeza', (0, cy + 8.8, 0.2), (4.2, 1.0, 4.2), hierro)
    m.viga('cabeza', (0, cy + 9.3, 0.2), (0, cy + 10.8, 0.2), 0.5, hierro)
    m.caja('cabeza', (0, cy + 11.2, 0.2), (1.6, 0.5, 0.5), hierro)
    for (x, z, w, d) in ((0, 3.0, 5.0, 0.3), (0, -2.6, 5.0, 0.3), (2.8, 0.2, 0.3, 5.0), (-2.8, 0.2, 0.3, 5.0)):
        m.caja('cabeza', (x, cy + 4.2, z), (w, 6.0, d), cristal)
    m.parte('llama', 'cabeza', (0, cy + 1.2, 0.2))
    llama = B.luz('llama_farolero', LLAMA_F)
    m.caja('llama', (0, cy + 2.2, 0.2), (2.6, 2.0, 2.6), llama)
    m.caja('llama', (0, cy + 3.8, 0.2), (1.8, 1.8, 1.8), llama)
    m.caja('llama', (0.2, cy + 5.2, 0.3), (1.0, 1.4, 1.0), llama)
    # Los brazos: el derecho con garras, el izquierdo con el cayado y el farolito colgado.
    madera = B.anillos('cayado_farolero', rampa('140c08', '24160e', '382214', '4c301c', '603e24'), paso=3)
    for lado, ld in LADOS:
        hombro = (lado * 4.0, y1 - 1.2, 0.4)
        codo = (lado * 5.0, y1 - 6.0, 2.6)
        mano = (lado * 4.4, y1 - 8.0, 6.4)
        p = brazo(m, f'brazo_{ld}', 'cuerpo', lado, hombro, codo, mano, 1.7, T, B.hueso('mano_farolero', HUESO),
                  B.diente('garra_farolero', NEGRO))
        if lado > 0:
            pm = np.array(mano) + np.array((0, 0.4, 0.8))
            arriba = pm + np.array((0, 14.0, 0.4))
            m.viga(p, pm + np.array((0, -8.0, -0.2)), arriba, 0.8, madera)
            m.viga(p, arriba, arriba + np.array((0, 1.0, 3.0)), 0.7, madera)
            gancho = arriba + np.array((0, 1.0, 3.0))
            m.viga(p, gancho, gancho + np.array((0, -2.4, 0)), 0.3, hierro)
            f = gancho + np.array((0, -3.6, 0))
            m.caja(p, tuple(f), (1.8, 2.2, 1.8), cristal)
            m.caja(p, tuple(f + np.array((0, 1.25, 0))), (2.0, 0.4, 2.0), hierro)
            m.caja(p, tuple(f + np.array((0, -1.25, 0))), (2.0, 0.4, 2.0), hierro)
            m.caja(p, tuple(f), (0.9, 1.2, 0.9), llama)
    m.mirar(('cabeza', 0.7))
    anims_espectro(m, flota=1.2, prisa=5, cabeza=None)
    s = m.anims['siempre']
    s.onda('llama', 'e', 1, 0.12, base=1.0, periodo=0.5)
    s.onda('cabeza', 'r', 2, 3, periodo=3.0)
    # especial: la llama se hincha y se pone blanca (va a reventar).
    es = m.anim('especial', 1.5)
    es.esc('llama', [(0, 1, 1, 1), (0.8, 1.5, 1.6, 1.5), (1.2, 1.9, 2.0, 1.9), (1.5, 2.3, 2.4, 2.3)])
    es.rot('cabeza', [(0, 0, 0, 0), (0.5, 0, 0, 4), (0.75, 0, 0, -4), (1.0, 0, 0, 5), (1.25, 0, 0, -5), (1.5, 0, 0, 0)])

    def dib(px, filas, c):
        for f in range(2, 8):
            px[5, f] = px[10, f] = c('42424a')
        for x in range(5, 11):
            px[x, 2] = px[x, 8] = c('42424a')
        for x, f in ((7, 4), (8, 4), (7, 5), (8, 5), (7, 6), (8, 6)):
            px[x, f] = c('d8ccff')
    return terminar(m, raiz, 'Farolero', 'Lamplighter Wraith', (('465264', '343e4c', '262e3a'), ('10141c', '06080c'),
                                                               dib),
                    ((1.5, 2.4, 3.0), (0, 1.4, 0)),
                    particulas=(('llama', chispa((176, 140, 255))), ('cristal', chispa((180, 180, 216))),
                                ('humo', voluta((30, 36, 48)))),
                    poses=[('siempre', 0.5), ('ataque', 0.12), ('especial', 1.2), ('muerte', 0.6)])


# ======================================================================================================================
#  Los Reclusos Espectrales y los Colosos Prisioneros
# ======================================================================================================================
PRESOS = {
    'morado': (rampa('1e0a30', '341454', '52247e', '7a40b0', 'a878e0'), 'Morado', 'Purple', 'd0a0ff', '9050ff'),
    'rojo': (rampa('2a0606', '4a0c0e', '701818', 'a02a2a', 'd05050'), 'Rojo', 'Red', 'ffb090', 'ff4030'),
    'rosa': (rampa('3a0a24', '5e1640', '8a2a62', 'c04a8e', 'f080c0'), 'Rosa', 'Pink', 'ffd0f0', 'ff60c0'),
}


def cadena(m, parte, a, b, eslabon, pint, grueso=0.5):
    """Una cadena de a a b: eslabones que se alternan (uno de canto y el siguiente de plano)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    largo = float(np.linalg.norm(b - a))
    n = max(1, int(largo / (eslabon * 0.8)))
    for k in range(n):
        p0 = a + (b - a) * (k / n)
        p1 = a + (b - a) * ((k + 1) / n)
        m.viga(parte, p0, p1, grueso, pint, ancho=eslabon * 0.55, extra=0.15, rodar=90 if k % 2 else 0)


def recluso(raiz, color):
    """Un Recluso Espectral: un preso fantasma, chico y encorvado, con harapos del color (translúcidos y rotos), la
    cabeza redonda con una cara triste (las cuencas encendidas y la boca abierta), los grilletes de hierro en las
    muñecas unidos por una cadena, y otra cadena del tobillo a una bola de hierro que arrastra."""
    R, nombre_es, nombre_en, c1, c2 = PRESOS[color]
    ident = f'recluso_{color}'
    m = B.Modelo(ident, K=2, ancho=128)
    m.translucido = True
    T = tela(f'tela_{ident}', R, 175)
    P = pliegue(f'pliegue_{ident}', R, 180, rota=False)
    Pb = pliegue(f'pliegue_bajo_{ident}', R, 165, rota=True)
    J = jiron(f'jiron_{ident}', R, 160)
    hierro = B.metal(f'hierro_{ident}', HIERRO, panel=4)
    eslabon = B.liso(f'eslabon_{ident}', HIERRO, base=3)
    y0, y1 = 4.0, 16.0
    m.parte('cuerpo', None, (0, 13, 0), rot=(18, 0, 0))
    tunica(m, 'cuerpo', y1, y0, 3.0, 3.6, 4.4, 8, P, Pb, quiebre=0.5)
    m.caja('cuerpo', (0, y1 - 0.3, 0), (6.4, 1.4, 5.0), T)
    jirones(m, 'colas', 'cuerpo', y0 + 0.8, 3.8, 3.1, 6, 4.0, 2.0, J)
    # La cabeza: redonda, de la tela del color (más opaca), la cara triste.
    cabeza = pano(f'cabeza_{ident}', R, 235)
    m.parte('cabeza', 'cuerpo', (0, y1 + 0.6, 0.8))
    cy = y1 + 3.2
    for k in range(5):
        y = -2.4 + k * 1.2 + 0.6
        f = math.sqrt(max(0.1, 1 - (y / 2.8) ** 2))
        m.caja('cabeza', (0, cy + y, 1.0), (5.2 * f, 1.24, 4.2 * f), cabeza)
        m.caja('cabeza', (0, cy + y, 1.0), (4.2 * f, 1.24, 5.2 * f), cabeza)
    ojos = ojo_luz(f'ojos_{ident}', c1, c2)
    zf = 1.0 + 2.6
    negro = B.liso(f'boca_{ident}', NEGRO, base=0)
    for lado in (-1, 1):
        m.caja('cabeza', (lado * 1.1, cy + 0.4, zf), (1.2, 1.4, 0.3), negro)
        m.caja('cabeza', (lado * 1.1, cy + 0.3, zf + 0.12), (0.6, 0.6, 0.2), ojos)
        # Las cejas caídas (tristes).
        m.caja('cabeza', (lado * 1.2, cy + 1.45, zf + 0.05), (1.4, 0.35, 0.3), negro, rot=(0, 0, -lado * 20))
    m.caja('cabeza', (0, cy - 1.3, zf), (1.2, 1.4, 0.3), negro)
    # Los brazos, con los grilletes y la cadena entre ellos.
    manos = {}
    for lado, ld in LADOS:
        hombro = (lado * 3.4, y1 - 1.0, 0.6)
        codo = (lado * 3.8, y1 - 4.4, 2.6)
        mano = (lado * 1.8, y1 - 5.8, 5.0)
        p = brazo(m, f'brazo_{ld}', 'cuerpo', lado, hombro, codo, mano, 1.4, T, B.hueso(f'mano_{ident}', HUESO),
                  B.diente(f'una_{ident}', HUESO), dedos=3, largo_garra=0.8)
        d = np.array(mano) - np.array(codo)
        d = d / np.linalg.norm(d)
        m.viga(p, tuple(np.array(mano) - d * 1.0), tuple(np.array(mano) + d * 0.1), 2.0, hierro)
        manos[ld] = np.array(mano)
    cadena(m, 'brazo_i', manos['i'] + np.array((-0.6, -0.6, 0)), (0, manos['i'][1] - 2.2, manos['i'][2] + 0.4), 1.2,
           eslabon)
    cadena(m, 'brazo_d', manos['d'] + np.array((0.6, -0.6, 0)), (0, manos['d'][1] - 2.2, manos['d'][2] + 0.4), 1.2,
           eslabon)
    # La bola de hierro, que arrastra detrás por el suelo (en su parte, suelta del cuerpo: el cuerpo flota, la bola no).
    m.parte('bola', None, (0.8, y0 + 0.5, -2.0))
    cadena(m, 'bola', (0.8, y0 + 0.5, -2.0), (1.6, 1.6, -8.0), 1.2, eslabon)
    m.esfera('bola', (1.6, 1.6, -9.6), 1.8, lambda k, n: hierro, cortes=5)
    m.mirar(('cabeza', 0.8))
    anims_espectro(m, flota=0.8, prisa=18)
    s = m.anims['siempre']
    s.onda('bola', 'r', 1, 6, periodo=3.0)
    s.onda('cuerpo', 'r', 0, 2, periodo=3.0, base=12)
    d = m.anims['muerte']
    d.rot('bola', [(0, 0, 0, 0), (1.2, 40, 0, 0)])

    def dib(px, filas, c):
        for x, f in ((6, 5), (9, 5)):
            px[x, f] = c(c1)
        for x in (7, 8):
            px[x, 8] = c('000000')
        for x in range(4, 12):
            px[x, 11] = c('42424a')
        px[3, 12] = px[12, 12] = c('42424a')
    hexes = ['%02x%02x%02x' % tuple(R[i].astype(int)) for i in range(5)]
    return terminar(m, raiz, f'Recluso Espectral {nombre_es}', f'{nombre_en} Spectral Inmate',
                    ((hexes[4], hexes[3], hexes[2]), (hexes[0], '000000'), dib),
                    ((1.0, 1.2, 1.9), (0, 0.7, 0)),
                    particulas=(('jiron', voluta(tuple(int(v) for v in R[3]))), ('chispa', chispa(tuple(int(v) for v in R[4]))),
                                ('hierro', chispa((120, 120, 134)))),
                    poses=[('siempre', 0.5), ('ataque', 0.15), ('ataque', 0.3), ('muerte', 0.6)])


def coloso(raiz, color):
    """Un Coloso Prisionero: un gigante fantasma encorvado (casi tres bloques y medio), de hombros enormes y brazos que
    le llegan al suelo, del color de su recluso; un collar de hierro con cadenas rotas, una mordaza de hierro en la
    boca, grilletes en las muñecas con su cadena rota colgando y el cuerpo que se deshace en jirones por abajo."""
    R, nombre_es, nombre_en, c1, c2 = PRESOS[color]
    ident = f'coloso_{color}'
    m = B.Modelo(ident, K=2, ancho=128)
    m.translucido = True
    m.escala = 1.25
    T = tela(f'tela_{ident}', R, 185)
    P = pliegue(f'pliegue_{ident}', R, 190, rota=False)
    Pb = pliegue(f'pliegue_bajo_{ident}', R, 170, rota=True)
    J = jiron(f'jiron_{ident}', R, 165)
    hierro = B.metal(f'hierro_{ident}', HIERRO, panel=5)
    eslabon = B.liso(f'eslabon_{ident}', HIERRO, base=3)
    y0, y1 = 6.0, 30.0
    m.parte('cuerpo', None, (0, 24, 0), rot=(16, 0, 0))
    # El cuerpo se estrecha hacia abajo (como un fantasma); arriba, el pecho y los hombros enormes, y la joroba.
    tunica(m, 'cuerpo', y1 - 3.0, y0, 6.4, 4.8, 3.2, 12, P, Pb, quiebre=0.55, grueso=1.0)
    for k, (w, d, y) in enumerate(((16.0, 9.0, y1 - 4.0), (18.0, 9.6, y1 - 1.6), (15.0, 8.6, y1 + 0.6))):
        m.caja('cuerpo', (0, y, 0.4), (w, 2.6, d * 0.76), T)
        m.caja('cuerpo', (0, y, 0.4), (w * 0.82, 2.6, d), T)
    m.caja('cuerpo', (0, y1 + 2.0, -1.8), (11.0, 3.2, 7.0), T)
    m.caja('cuerpo', (0, y1 + 3.2, -2.6), (7.0, 2.0, 5.0), T)
    jirones(m, 'colas', 'cuerpo', y0 + 1.5, 6.0, 5.0, 9, 6.0, 3.0, J)
    # El collar de hierro con dos cadenas rotas que cuelgan.
    m.caja('cuerpo', (0, y1 + 0.6, 2.2), (8.0, 2.0, 6.0), hierro)
    cadena(m, 'cuerpo', (-3.0, y1 - 0.2, 5.0), (-3.6, y1 - 7.0, 6.6), 1.4, eslabon, 0.6)
    cadena(m, 'cuerpo', (3.2, y1 - 0.2, 5.0), (3.8, y1 - 5.0, 6.4), 1.4, eslabon, 0.6)
    # La cabeza, pequeña para el cuerpo y hundida entre los hombros, por delante; con los ojos y la mordaza.
    cabeza = pano(f'cabeza_{ident}', R, 240)
    m.parte('cabeza', 'cuerpo', (0, y1 + 0.5, 3.6))
    cy = y1 + 2.8
    for k in range(5):
        y = -2.2 + k * 1.1 + 0.55
        f = math.sqrt(max(0.1, 1 - (y / 2.6) ** 2))
        m.caja('cabeza', (0, cy + y, 4.0), (5.6 * f, 1.14, 4.8 * f), cabeza)
        m.caja('cabeza', (0, cy + y, 4.0), (4.8 * f, 1.14, 5.6 * f), cabeza)
    ojos = ojo_luz(f'ojos_{ident}', c1, c2)
    zf = 4.0 + 2.9
    for lado in (-1, 1):
        m.caja('cabeza', (lado * 1.2, cy + 0.6, zf), (1.4, 0.9, 0.3), B.liso(f'cuenca_{ident}', NEGRO, base=0))
        m.caja('cabeza', (lado * 1.2, cy + 0.6, zf + 0.1), (0.9, 0.5, 0.2), ojos)
    m.caja('cabeza', (0, cy - 1.0, zf - 0.3), (5.0, 1.6, 1.2), hierro)
    m.caja('cabeza', (0, cy - 1.0, 4.0), (5.8, 0.8, 5.8), hierro)
    # Los brazos: enormes, colgando casi hasta el suelo, con los grilletes y la cadena rota.
    for lado, ld in LADOS:
        hombro = (lado * 8.6, y1 - 1.0, 0.6)
        codo = (lado * 10.4, y1 - 11.0, 2.4)
        mano = (lado * 9.0, y1 - 20.0, 5.0)
        p = brazo(m, f'brazo_{ld}', 'cuerpo', lado, hombro, codo, mano, 4.6, T, B.hueso(f'mano_{ident}', HUESO),
                  B.diente(f'una_{ident}', HUESO), dedos=4, largo_garra=1.6)
        # El hombro: una hombrera de tela gruesa encima.
        m.caja(p, (lado * 8.4, y1 + 0.2, 0.6), (6.0, 3.4, 6.4), T)
        d = np.array(mano) - np.array(codo)
        d = d / np.linalg.norm(d)
        m.viga(p, tuple(np.array(mano) - d * 2.6), tuple(np.array(mano) - d * 0.2), 8.8, hierro)
        cadena(m, p, np.array(mano) + np.array((0, -1.2, -2.6)), np.array(mano) + np.array((lado * 1.4, -6.4, -3.8)), 1.6,
               eslabon, 0.7)
    m.mirar(('cabeza', 0.6))
    anims_espectro(m, flota=0.6, prisa=16, golpe='guadana')
    m.anims['siempre'].onda('cuerpo', 'r', 0, 1.5, periodo=3.0, base=10)
    # El golpe de coloso: los dos puños arriba y abajo, de mazazo.
    at = m.anims['ataque']
    at.canales = [c for c in at.canales if c[0] not in ('brazo_i', 'brazo_d')]
    for ld in ('i', 'd'):
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.2, -120, 0, 0), (0.32, 20, 0, 0), (0.5, 0, 0, 0)])

    def dib(px, filas, c):
        for x in range(3, 13):
            px[x, 7] = c('%02x%02x%02x' % tuple(R[2].astype(int)))
        for x, f in ((6, 4), (9, 4)):
            px[x, f] = c(c1)
        for x in range(5, 11):
            px[x, 6] = c('42424a')
        px[3, 11] = px[12, 11] = c('42424a')
    hexes = ['%02x%02x%02x' % tuple(R[i].astype(int)) for i in range(5)]
    return terminar(m, raiz, f'Coloso Prisionero {nombre_es}', f'{nombre_en} Prisoner Colossus',
                    ((hexes[4], hexes[3], hexes[2]), (hexes[0], '000000'), dib),
                    ((2.6, 3.6, 4.8), (0, 2.3, 0)),
                    particulas=(('jiron', voluta(tuple(int(v) for v in R[3]))), ('hierro', chispa((120, 120, 134))),
                                ('polvo', voluta((70, 66, 80)))),
                    poses=[('siempre', 0.5), ('ataque', 0.2), ('ataque', 0.32), ('muerte', 0.6)])


# ======================================================================================================================
#  El Ojo Errante
# ======================================================================================================================
ESCLERA = rampa('8a7a72', 'c8b8ae', 'e6d8ce', 'f6eee6', 'fffaf4')
VENA = rampa('5a0a10', '8a1420', 'b02030', 'd04048', 'f07070')
CARNE = rampa('2a0a12', '4a1420', '6a2030', '8a3040', 'aa4a58')
IRIS = rampa('2a0a4a', '5a1a8a', '9a40d0', 'd090ff', 'f4e0ff')


def ojo_errante(raiz):
    """El Ojo Errante: un ojo enorme que flota (la esclera blanca con venas rojas), el iris violeta encendido con la
    pupila de raja; lo envuelve por detrás un párpado de carne oscura (que parpadea) y le cuelgan cinco nervios como
    tentáculos que se mecen."""
    m = B.Modelo('ojo_errante', K=2, ancho=128)

    def esclera(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 3)
        venas = B.grietas(tw, th, s, cara, cuantas=max(1, tw * th // 28), giro=0.45, ramas=0.15)
        idx[venas] = 6
        idx[B.vecinos(venas) & ((xs + ys) % 2 == 0)] = 2
        if cara == 'arriba':
            idx[idx == 3] = 4
        return idx
    pint = B.trazo('esclera', esclera, juntar(ESCLERA, VENA))
    m.parte('cuerpo', None, (0, 14, 0))
    r = 6.0
    m.esfera('cuerpo', (0, 14, 0), r, lambda k, n: pint, cortes=9)
    # El iris (encendido) y la pupila de raja, por delante.
    m.parte('iris', 'cuerpo', (0, 14, r))
    iris = B.luz('iris_ojo', IRIS)
    zf = r * 1.03 * 0.98
    m.caja('iris', (0, 14, zf), (5.2, 5.2, 0.6), iris)
    m.caja('iris', (0, 14, zf - 0.1), (6.2, 3.8, 0.6), iris)
    m.caja('iris', (0, 14, zf - 0.1), (3.8, 6.2, 0.6), iris)
    m.caja('iris', (0, 14, zf + 0.35), (1.0, 4.4, 0.3), B.liso('pupila_ojo', NEGRO, base=0))
    # El párpado: una concha de carne por detrás y por arriba (en su parte: parpadea).
    carne = B.trazo('carne_ojo', lambda xs, ys, tw, th, c, s: np.where(((xs + ys * 2) % 5) == 0, 1,
                                                                        np.where((xs * 3 + ys) % 7 == 0, 3, 2)), CARNE)
    m.parte('parpado', 'cuerpo', (0, 14, -1.0))
    for k in range(6):
        y = -4.8 + k * 1.9 + 0.95
        f = math.sqrt(max(0.1, 1 - (y / 6.6) ** 2))
        m.caja('parpado', (0, 14 + y, -2.6), (2 * 6.6 * f, 1.95, 7.0 * f), carne)
    m.caja('parpado', (0, 14 + 5.6, 0.6), (8.4, 1.4, 8.0), carne)
    m.caja('parpado', (0, 14 - 5.6, 0.0), (7.6, 1.2, 6.8), carne)
    # Las pestañas (de arriba): pinchos oscuros.
    for k in range(7):
        x = -3.6 + k * 1.2
        colmillo(m, 'parpado', (x, 14 + 6.0, 4.0 - abs(x) * 0.3), (x * 0.08, 0.6, 1.0), (1, 0, 0), 1.8, 0.4,
                 B.diente('pestana_ojo', NEGRO))
    # Los nervios: cinco tentáculos de tres tramos (cada uno, su parte; se mecen a destiempo).
    nervio = B.anillos('nervio_ojo', CARNE, paso=2)
    for k in range(5):
        a = math.radians(k * 72 + 20)
        base = np.array((math.sin(a) * 3.0, 14 - 5.0, math.cos(a) * 2.0 - 1.5))
        n = m.parte(f'nervio{k}', 'cuerpo', tuple(base))
        p = base
        for t in range(3):
            q = p + np.array((math.sin(a) * 0.8, -3.0 + t * 0.3, math.cos(a) * 0.6))
            m.viga(n, p, q, 1.1 - t * 0.25, nervio, extra=0.3)
            p = q
    m.mirar(('cuerpo', 1.0))
    s = m.anim('siempre', 4.0, bucle=True)
    s.onda('cuerpo', 'm', 1, 1.6, periodo=4.0)
    for k in range(5):
        s.onda(f'nervio{k}', 'r', 0, 14, periodo=2.0, fase=k * 0.2)
        s.onda(f'nervio{k}', 'r', 2, 10, periodo=4.0, fase=k * 0.13)
    s.onda('iris', 'e', 0, 0.08, base=1.0, periodo=2.0)
    # Parpadea: el párpado baja tapando el ojo un instante (cada cuatro segundos).
    s.esc('parpado', [(0, 1, 1, 1), (3.5, 1, 1, 1), (3.6, 1.05, 1.0, 1.25), (3.75, 1, 1, 1), (4.0, 1, 1, 1)])
    # especial: la luz de la Linterna le duele: se encoge y tiembla.
    es = m.anim('especial', 0.6)
    es.esc('iris', [(0, 1, 1, 1), (0.1, 0.5, 0.5, 1), (0.6, 1, 1, 1)])
    es.rot('cuerpo', [(0, 0, 0, 0), (0.1, 0, 12, 4), (0.2, 0, -12, -4), (0.3, 0, 8, 3), (0.45, 0, -6, -2), (0.6, 0, 0, 0)])
    at = m.anim('ataque', 0.5)
    at.esc('iris', [(0, 1, 1, 1), (0.15, 1.4, 1.4, 1), (0.5, 1, 1, 1)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.15, 0, 0, 2.0), (0.5, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.esc('cuerpo', [(0, 1, 1, 1), (0.6, 1.25, 1.25, 1.25), (0.8, 1.4, 0.6, 1.4), (1.0, 0.05, 0.05, 0.05)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -4, 0)])

    def dib(px, filas, c):
        for f in range(4, 13):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('f6eee6')
        for x, f in ((6, 7), (9, 7), (7, 6), (8, 6), (7, 9), (8, 9), (6, 8), (9, 8)):
            px[x, f] = c('9a40d0')
        for f in (6, 7, 8, 9):
            px[7, f] = px[8, f] = c('000000') if f in (7, 8) else px[7, f]
    return terminar(m, raiz, 'Ojo Errante', 'Wandering Eye', (('fffaf4', 'e6d8ce', 'c8b8ae'), ('4a1420', '2a0a12'), dib),
                    ((1.6, 1.4, 2.2), (0, 0.85, 0)),
                    particulas=(('lagrima', chispa((210, 160, 255))), ('carne', chispa((140, 40, 60)))),
                    poses=[('siempre', 0.5), ('siempre', 3.62), ('especial', 0.15), ('muerte', 0.75)])


# ======================================================================================================================
#  El Pálido
# ======================================================================================================================
PALIDA = rampa('6e6a70', '9a969c', 'c2bec4', 'dcd8de', 'f2eef4')
TRAPO = rampa('060608', '0e0e12', '18181e', '24242c', '32323c')


def palido(raiz):
    """El Pálido: una figura alta y flaca, de piel gris blanquecina, con ropa negra raída; los brazos le cuelgan hasta
    las rodillas y acaban en dedos largos. La cabeza calva no tiene boca: solo dos ojos blancos, sin pupila, que
    brillan. Se queda quieto, mirándote, con la cabeza un poco ladeada."""
    m = B.Modelo('palido', K=2, ancho=128)
    m.escala = 1.1
    piel = B.trazo('piel_palido', lambda xs, ys, tw, th, c, s: np.where(((xs * 7 + ys * 3 + s) % 13) == 0, 1, 2),
                   PALIDA)
    ropa = tela('ropa_palido', TRAPO, 255, pliegue=4, roto=False)
    m.parte('cuerpo', None, (0, 14, 0))
    m.caja_desde('cuerpo', (0, 14, 0), (7.0, 11.0, 3.6), ropa)
    m.caja('cuerpo', (0, 24.4, 0), (8.0, 1.6, 4.0), ropa)
    # Las costillas que se le marcan por un roto de la camisa.
    m.caja('cuerpo', (1.4, 19.5, 1.85), (2.6, 3.0, 0.2), piel)
    for k in range(3):
        m.caja('cuerpo', (1.4, 18.6 + k * 1.0, 1.98), (2.4, 0.3, 0.1), B.liso('costilla_palido', PALIDA, base=1))
    m.parte('cabeza', 'cuerpo', (0, 25.0, 0.2))
    m.caja_desde('cabeza', (0, 25.6, 0.2), (6.4, 7.6, 6.0), piel,
                 caras={'frente': B.trazo('cara_palido', _cara_palida, PALIDA)})
    m.caja('cabeza', (0, 25.2, 0.2), (3.0, 1.2, 3.0), piel)
    ojos = B.luz('ojos_palido', rampa('d8e8ff', 'e8f0ff', 'f4f8ff', 'ffffff', 'ffffff'))
    for lado in (-1, 1):
        m.caja('cabeza', (lado * 1.5, 29.6, 3.25), (1.6, 0.8, 0.3), ojos)
    for lado, ld in LADOS:
        hombro = np.array((lado * 4.4, 24.2, 0.2))
        codo = np.array((lado * 5.0, 17.0, 0.4))
        mano = np.array((lado * 5.2, 9.8, 0.8))
        p = m.parte(f'brazo_{ld}', 'cuerpo', tuple(hombro))
        m.viga(p, hombro, codo, 1.8, ropa, extra=0.4)
        m.viga(p, codo, mano, 1.5, piel, extra=0.3)
        for k in range(4):
            off = (k - 1.5) * 0.4
            raiz_ = mano + np.array((off, -0.4, 0.3))
            m.viga(p, raiz_, raiz_ + np.array((off * 0.5, -3.0 - (k % 2) * 0.6, 0.4)), 0.35, piel)
        pierna = m.parte(f'pierna_{ld}', 'cuerpo', (lado * 1.8, 14, 0))
        m.caja_desde(pierna, (lado * 1.8, 0, 0), (3.0, 14.0, 3.0), ropa)
    m.mirar(('cabeza', 1.0))
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('cabeza', 'r', 2, 3, base=12, periodo=4.0)
    r.onda('cuerpo', 'e', 1, 0.01, base=1.0, periodo=4.0)
    a = m.anim('andar', 1.2, bucle=True)
    a.onda('pierna_d', 'r', 0, 18)
    a.onda('pierna_i', 'r', 0, 18, fase=0.5)
    a.onda('brazo_d', 'r', 0, 4, fase=0.5)
    a.onda('brazo_i', 'r', 0, 4)
    at = m.anim('ataque', 0.5)
    for ld in ('i', 'd'):
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, -95, 0, 0), (0.3, -80, 0, 0), (0.5, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.15, 0, 0, -12), (0.5, 0, 0, 0)])
    es = m.anim('especial', 0.5)
    es.esc('cuerpo', [(0, 1, 1, 1), (0.1, 1.1, 0.9, 1.1), (0.2, 0.9, 1.1, 0.9), (0.3, 1.2, 0.8, 1.2), (0.5, 0.01, 1.5, 0.01)])
    d = m.anim('muerte', 1.0)
    d.esc('cuerpo', [(0, 1, 1, 1), (1.0, 0.01, 1.4, 0.01)])

    def dib(px, filas, c):
        for f in range(2, 9):
            a, b = filas[f]
            for x in range(max(a + 1, 4), min(b, 12)):
                px[x, f] = c('c2bec4')
        for x, f in ((6, 5), (9, 5)):
            px[x, f] = c('ffffff')
        for f in range(9, 15):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('18181e')
    return terminar(m, raiz, 'El Pálido', 'The Pale One', (('dcd8de', 'c2bec4', '9a969c'), ('18181e', '060608'), dib),
                    ((1.1, 2.3, 1.9), (0, 1.75, 0)),
                    particulas=(('ceniza', chispa((200, 196, 204))), ('humo', voluta((20, 20, 26)))),
                    poses=[('reposo', 1.0), ('andar', 0.3), ('ataque', 0.2), ('especial', 0.3)])


def _cara_palida(xs, ys, tw, th, cara, s):
    idx = np.full((th, tw), 2)
    u, v = (xs + 0.5) / tw, (ys + 0.5) / th
    # Las cuencas, un tono más oscuras; sin boca.
    cuenca = ((np.abs(u - 0.27) < 0.15) | (np.abs(u - 0.73) < 0.15)) & (np.abs(v - 0.47) < 0.09)
    idx[cuenca] = 1
    idx[(np.abs(u - 0.5) < 0.04) & (v > 0.5) & (v < 0.66)] = 1
    return idx


# ======================================================================================================================
#  El Vindicador del Limbo
# ======================================================================================================================
PIEL_V = rampa('3a3446', '4e4660', '625a78', '7a7290', '948ca8')
TUNICA_V = rampa('120a1e', '1e1230', '2c1a46', '3c2660', '50347a')
FILO_V = rampa('4a2a8a', '7a4ad0', 'b090ff', 'e0d4ff', 'ffffff')


def vindicador(raiz):
    """El Vindicador del Limbo: un saqueador que bajó al Limbo y se quedó: la piel gris violácea, la nariz larga y el
    ceño de los suyos, los ojos encendidos de violeta; una túnica morada oscura con hombreras y peto de hierro negro con
    runas que brillan, y un hacha espectral (el mango negro y la hoja translúcida, violeta, con el filo encendido)."""
    m = B.Modelo('vindicador_limbo', K=2, ancho=128)
    m.translucido = True
    tunica_p = tela('tunica_vindicador', TUNICA_V, 255, pliegue=3, roto=False)
    piel = B.liso('piel_vindicador', PIEL_V)
    hierro = B.metal('hierro_vindicador', HIERRO, panel=4)
    runa = B.luz('runa_vindicador', FILO_V)
    m.parte('cuerpo', None, (0, 12, 0))
    m.caja_desde('cuerpo', (0, 12, 0), (8.0, 12.0, 6.0), tunica_p)
    # El faldón de la túnica (hasta las rodillas).
    m.caja('cuerpo', (0, 9.0, 0), (8.4, 6.0, 6.4), tunica_p)
    # El peto y las hombreras de hierro negro, con runas.
    m.caja('cuerpo', (0, 19.5, 3.05), (6.4, 6.0, 0.4), hierro)
    for k, (x, y) in enumerate(((-1.4, 20.5), (1.4, 20.5), (0, 18.6))):
        m.caja('cuerpo', (x, y, 3.3), (0.8, 0.8, 0.2), runa)
    m.parte('cabeza', 'cuerpo', (0, 24, 0))
    m.caja_desde('cabeza', (0, 24, 0), (8, 10, 8), piel, caras={'frente': B.trazo('cara_vindicador', _cara_vindicador,
                                                                                    juntar(PIEL_V, FILO_V),
                                                                                    brilla=True)})
    m.caja('cabeza', (0, 27.0, 4.6), (2.0, 4.0, 2.0), piel)
    for lado, ld in LADOS:
        p = m.parte(f'brazo_{ld}', 'cuerpo', (lado * 5.0, 22, 0))
        m.caja_desde(p, (lado * 6.0, 12, 0), (4, 12, 4), tunica_p)
        m.caja(p, (lado * 6.0, 23.2, 0), (5.2, 2.6, 5.2), hierro)
        m.caja(p, (lado * 6.0, 13.0, 0.6), (3.6, 2.4, 3.6), piel)
        pierna = m.parte(f'pierna_{ld}', 'cuerpo', (lado * 2.0, 12, 0))
        m.caja_desde(pierna, (lado * 2.0, 0, 0), (4, 12, 4), B.liso('pantalon_vindicador', TUNICA_V, base=1))
    # El hacha, en la mano derecha (brazo_d), hacia delante.
    mango = B.anillos('mango_vindicador', NEGRO, paso=3)
    hoja = B.trazo('hoja_vindicador', lambda xs, ys, tw, th, c, s: np.where(xs == 0, 3, 2), FILO_V)

    def hoja_gel(tw, th, cara, s):
        tex, _ = hoja.fn(tw, th, cara, s)
        tex[..., 3] = 170
        return tex, None
    hoja_t = B.Pintor('hoja_vindicador_gel', hoja_gel)
    mano = np.array((-6.0, 13.0, 1.4))
    m.viga('brazo_d', mano + np.array((0, -2.0, -1.0)), mano + np.array((0, 1.0, 9.0)), 1.0, mango)
    centro = mano + np.array((0, 1.6, 8.0))
    m.caja('brazo_d', tuple(centro), (0.6, 6.4, 4.0), hoja_t)
    m.caja('brazo_d', tuple(centro + np.array((0, 0, 2.2))), (0.7, 6.8, 0.5), runa)
    m.mirar(('cabeza', 1.0))
    a = m.anim('andar', 1.0, bucle=True)
    a.onda('pierna_d', 'r', 0, 30)
    a.onda('pierna_i', 'r', 0, 30, fase=0.5)
    a.onda('brazo_i', 'r', 0, 25, fase=0.5)
    a.onda('brazo_d', 'r', 0, 10)
    s = m.anim('siempre', 2.0, bucle=True)
    s.onda('cabeza', 'r', 2, 2, periodo=2.0)
    at = m.anim('ataque', 0.6)
    at.rot('brazo_d', [(0, 0, 0, 0), (0.2, -150, 0, 10), (0.32, -20, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.2, -6, 0, 0), (0.32, 10, 0, 0), (0.6, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.6, -70, 0, 6), (1.0, -88, 0, 8)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, -2)])

    def dib(px, filas, c):
        for f in range(2, 9):
            a, b = filas[f]
            for x in range(max(a + 1, 4), min(b, 12)):
                px[x, f] = c('625a78')
        for x, f in ((6, 5), (9, 5)):
            px[x, f] = c('b090ff')
        for f in (6, 7, 8):
            px[7, f] = px[8, f] = c('4e4660')
        for f in range(9, 15):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('2c1a46')
    return terminar(m, raiz, 'Vindicador del Limbo', 'Limbo Vindicator', (('948ca8', '7a7290', '625a78'),
                                                                           ('2c1a46', '120a1e'), dib),
                    ((1.2, 2.2, 2.0), (0, 1.6, 0)),
                    particulas=(('runa', chispa((176, 144, 255))), ('chispa', chispa((224, 212, 255)))),
                    poses=[('andar', 0.25), ('andar', 0.75), ('ataque', 0.2), ('muerte', 1.0)])


def _cara_vindicador(xs, ys, tw, th, cara, s):
    idx = np.full((th, tw), 2)
    u, v = (xs + 0.5) / tw, (ys + 0.5) / th
    ojo = ((np.abs(u - 0.3) < 0.08) | (np.abs(u - 0.7) < 0.08)) & (np.abs(v - 0.42) < 0.05)
    ceja = (np.abs(v - 0.34) < 0.04) & (np.abs(u - 0.5) < 0.36)
    boca = (np.abs(u - 0.5) < 0.18) & (np.abs(v - 0.82) < 0.03)
    idx[ceja | boca] = 0
    idx[ojo] = 8
    return idx, ojo


MOBS = {
    'espectro_rojo': espectro_rojo,
    'espectro_blanco': espectro_blanco,
    'espectro_negro': espectro_negro,
    'espectro_amarillo': espectro_amarillo,
    'parca_menor': parca_menor,
    'parca': parca_grande,
    'murcielago_vampiro': murcielago,
    'farolero': farolero,
    'ojo_errante': ojo_errante,
    'palido': palido,
    'vindicador_limbo': vindicador,
}
for _c in PRESOS:
    MOBS[f'recluso_{_c}'] = (lambda c: lambda raiz: recluso(raiz, c))(_c)
    MOBS[f'coloso_{_c}'] = (lambda c: lambda raiz: coloso(raiz, c))(_c)


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
