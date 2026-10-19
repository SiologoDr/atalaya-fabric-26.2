"""
Las hormigas del bestiario, rehechas (19-10-2026): las cinco hormigas del DEDsafío 2 (Cantimplo, Bombermant, Parapona,
Compona y Solvetus) como en sus fichas de la DEDciclopedia, pero mejor: hormigas soldado ERGUIDAS, con las cuatro patas
de atrás en el suelo, el tórax levantado como un centauro, las patas de delante hechas brazos y la cabeza arriba.

Al píxel de Minecraft (materiales/CONTINUAR.md, regla 1): van a escala 1 y con B.TEXEL = 1, así que cada píxel de la
textura es uno de Minecraft (16 por bloque) y todas las piezas miden píxeles enteros (las patas, de 2 x 2; las antenas
y el asta de la lanza, de 1 x 1). Los pintores pintan a ese píxel: un poro, una sutura o un pelo es un píxel.

  lancera     (Cantimplo)  parda, con la cúpula de una bellota por casco y una lanza de madera con la punta de pedernal
                           tallado, sujeta en alto con la mano derecha: la soldado del hormiguero
  polvorin    (Bombermant) gris pizarra, con una bomba de barro cocido (atada con cuerda, la mecha encendida) en alto
                           con los dos brazos: la que revienta
  cabezona    (Parapona)   castaña, con la cabeza el doble de grande, la frente acorazada y unas mandíbulas de tenaza
                           dentadas: su mordisco te deja lentísimo
  radiactiva  (Compona)    negra, con el gáster hinchado como el de las hormigas de miel y las membranas entre sus
                           placas encendidas de verde, como los ojos: su mordisco deja radiación
  brasa       (Solvetus)   roja, con grietas de brasa por todo el cuerpo y una tea encendida en la mano: tocarla te
                           prende un fuego que solo se apaga con agua

Lo que hacen (las mecánicas, los sonidos y los efectos) no cambia: está en Hormigas.java.

Uso: python bestiario_hormigas.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import rampa

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))          # +X es la izquierda de la hormiga (mira hacia +Z)
E = 0.04                               # lo que se encogen las cajas de dentro de una pieza redonda (sin caras a ras)


# ======================================================================================================================
#  Las piezas
# ======================================================================================================================
def redondo(m, parte, centro, tam, pint, rot=(0, 0, 0), frente=None, caras=None, bisel=1):
    """Una pieza de cantos achaflanados (tres cajas cruzadas, de píxeles enteros; con bisel 2, una cuarta que rellena
    el escalón, para las piezas grandes): así no se ve el cubo y sigue siendo de Minecraft. 'frente', el pintor de la
    cara de delante de la caja que asoma por delante (la cara); 'caras', pintores por cara."""
    w, h, d = tam
    b = 2 * bisel
    m.caja(parte, centro, (w, h - b, d - b), pint, rot=rot, caras=caras)
    m.caja(parte, centro, (w - b - E, h, d - b - E), pint, rot=rot, caras=caras)
    c = dict(caras or {})
    if frente is not None:
        c['frente'] = frente
    m.caja(parte, centro, (w - b - 2 * E, h - b - E, d), pint, rot=rot, caras=c or None)
    if bisel >= 2:
        m.caja(parte, centro, (w - 2, h - 2, d - 2), pint, rot=rot, caras=caras)


def rotar(p, piv, rot):
    """El punto p girado 'rot' (grados, como ModelPart) alrededor de piv."""
    R = B.girar(rot)[:3, :3]
    piv = np.asarray(piv, float)
    return piv + R @ (np.asarray(p, float) - piv)


# ======================================================================================================================
#  Los pintores, al píxel de Minecraft
# ======================================================================================================================
def _azar1(xs, ys, s):
    """Un número fijo de 0 a 1 por cada píxel."""
    h = (np.asarray(xs, np.int64) * 374761393 + np.asarray(ys, np.int64) * 668265263 + int(s) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _v(tw, th, cara, s, base=2.0, luz=1.0):
    """El tono de la quitina: corre por la rampa, más clara arriba y más oscura abajo; los cantos de lado, un poco
    más oscuros (lo redondo); sin ruido."""
    xs, ys = L._malla(tw, th)
    if cara == 'arriba':
        v = np.full((th, tw), base + luz * 0.55)
    elif cara == 'abajo':
        v = np.full((th, tw), base - luz * 0.9)
    else:
        v = base + luz * (0.45 - (ys + 0.5) / th)
    if tw > 2:
        v = v - ((xs == 0) | (xs == tw - 1)) * 0.35
    return v


def quitina(nombre, R, base=2.0, poros=0.06, sutura=None, marca=None, rm=None):
    """La quitina de hormiga al píxel: el tono que corre por la rampa, poros de un píxel (más oscuros) y, en la fila de
    arriba de las caras de lado, el canto más claro. 'sutura' (una fracción del alto): una junta oscura de un píxel de
    lado a lado, como la que separa las placas del tórax. 'marca' (fn(xs, ys, tw, th, cara, s) -> 0..1): lo que se
    enciende encima con la rampa 'rm' (grietas de brasa...)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara, s, base)
        if cara not in ('arriba', 'abajo') and th > 2:
            v = v + (ys == 0) * 0.45
        v = v - (a < poros) * 0.7
        if sutura is not None and cara not in ('arriba', 'abajo'):
            v = np.where(ys == int(th * sutura), v - 0.9, v)
            v = np.where(ys == int(th * sutura) + 1, v + 0.3, v)
        tex = L._rgba(L.color_continuo(R, v))
        if marca is None:
            return tex, None
        mk = marca(xs, ys, tw, th, cara, s)
        return encender(tex, mk, rm, 1.6 + mk * 1.0)
    return B.Pintor(nombre, fn)


def encender(tex, a, rc, v):
    """Lo que brilla encima: la rampa 'rc' (en v) donde 'a' (de 0 a 1). La textura y su brillo (o None)."""
    a = np.clip(a, 0.0, 1.0)
    if not (a > 0.02).any():
        return tex, None
    luz = L.color_continuo(rc, np.broadcast_to(np.asarray(v, float), a.shape))
    a3 = a[..., None]
    tex = tex.copy()
    tex[..., :3] = np.clip(np.round(tex[..., :3] * (1 - a3) + luz * a3), 0, 255)
    emis = np.zeros_like(tex)
    emis[..., :3] = np.clip(np.round(luz), 0, 255)
    emis[..., 3] = np.where(a > 0.02, np.round(a * 255), 0)
    return tex, emis


def gaster(nombre, R, placas=3, base=2.0, membrana=None, rm=None, largo=None, fino=True):
    """El gáster: placas que se solapan (de delante atrás), cada una con su canto claro y la sombra de la siguiente
    debajo; poros finos. Con 'membrana' (una rampa encendida), entre placa y placa asoma la membrana, que brilla (la
    Radiactiva). Con 'fino', pintado a 32 por bloque (las juntas, finas)."""
    k_px = 2 if fino else 1
    largo = largo * k_px if largo else largo

    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara, s, base)
        # Lo largo del gáster: en las caras de lado es lo ancho de la textura; arriba y abajo, lo alto.
        if cara in ('izq', 'der'):
            u, n = xs, tw
        elif cara in ('arriba', 'abajo'):
            u, n = ys, th
        else:
            u, n = None, 1
        mk = np.zeros((th, tw))
        if u is not None and largo:
            # Todas las cajas de la pieza están centradas: la posición a lo largo de la pieza entera.
            u = u + (largo - n) / 2.0
            n = largo
        if u is not None and n >= placas * 2:
            paso = n / placas
            k = np.floor(u / paso).astype(int)
            pos = u - k * paso
            # La junta entre placas: un píxel oscuro y, detrás, el canto claro de la placa siguiente.
            junta = (pos >= paso - k_px) & (k < placas - 1)
            v = v - junta * 0.75 + ((pos < k_px) & (k > 0)) * 0.4
            if membrana is not None:
                mk = junta.astype(float)
        v = v - (a < 0.05) * 0.6
        tex = L._rgba(L.color_continuo(R, v))
        if membrana is None:
            return tex, None
        return encender(tex, mk, membrana, 2.6 + _azar1(xs, ys, s + 7) * 1.2)
    p = B.Pintor(nombre, fn)
    return B.fino(p) if fino else p


def pata(nombre, R, base=2.0):
    """Una pata (o un brazo): la quitina con la junta oscura en la punta de cada tramo, el lado de delante más claro y
    pelillos de un píxel (más claros) a lo largo."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        if cara in ('arriba', 'abajo'):
            v = np.full((th, tw), base - (0.5 if cara == 'abajo' else -0.2))
        else:
            v = np.full((th, tw), base) + (xs == 0) * 0.5 - (xs == tw - 1) * 0.4
            v = v - (ys == th - 1) * 0.9 + (ys == 0) * 0.3
            v = v + ((a < 0.1) & (ys > 0) & (ys < th - 1)) * 0.6
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def antena(nombre, R, punta=None):
    """La antena: anillada (un píxel claro, uno oscuro); con 'punta' (una rampa), la maza del final encendida."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 2.2) - ((ys + xs) % 2) * 0.6
        tex = L._rgba(L.color_continuo(R, v))
        return tex, None
    return B.Pintor(nombre, fn)


OJO = rampa('000000', '07080a', '12141a', '262a34', 'cfd6e2')


def ojo_compuesto(nombre, R=OJO, brilla=None):
    """El ojo compuesto: negro con las facetas en damero (un tono más claro) y un píxel de reflejo arriba a la
    izquierda; con 'brilla' (una rampa), encendido entero, con el centro más claro."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        if brilla is not None:
            d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
            tex = L._rgba(L.color_continuo(brilla, 2.6 + d * 0.8))
            return tex, tex.copy()
        # Las facetas, pintadas finas: celdillas de 2 x 2 en filas desplazadas, cada una con su píxel de luz.
        fila = ys // 2
        col = (xs + (fila % 2)) // 2
        v = 1.3 + ((col + fila) % 2) * 0.5 + (((xs + (fila % 2)) % 2 == 0) & (ys % 2 == 0)) * 0.5
        # El brillo del ojo: apagado (un azul gris), un arco pequeño arriba a la izquierda; nada de punto blanco.
        if cara not in ('abajo', 'atras'):
            arco = ((xs + ys) <= 2) & ((xs + ys) >= 1)
            v = np.where(arco, 3.0, v)
        return L._rgba(L.color_continuo(R, v)), None
    return B.fino(B.Pintor(nombre, fn))


def cara(nombre, R, base=2.0):
    """La cara de la hormiga (la de delante de la cabeza): la V oscura de las carenas de la frente (el ceño), los dos
    hoyos de las antenas y el clípeo, la placa clara de abajo sobre las mandíbulas."""
    def fn(tw, th, cara_, s):
        xs, ys = L._malla(tw, th)
        v = _v(tw, th, 'frente', s, base) + (ys == 0) * 0.45
        cx = (tw - 1) / 2
        dx = np.abs(xs - cx)
        # Las carenas de la frente: el surco del centro (un píxel oscuro de arriba a media cara) con el canto claro a
        # los lados, como las crestas de entre las antenas.
        surco = (dx < 0.6) & (ys <= th // 2)
        v = np.where(surco, v - 0.8, v)
        v = np.where((np.abs(dx - 1) < 0.6) & (ys <= th // 2) & (ys > 0), v + 0.35, v)
        # El clípeo: la placa de abajo, un tono más claro, con su borde oscuro encima.
        v = np.where((ys == th - 1) & (dx < cx - 0.5), v + 0.5, v)
        v = np.where((ys == th - 2) & (dx < cx - 0.5), v - 0.5, v)
        return L._rgba(L.color_continuo(R, v)), None
    return B.fino(B.Pintor(nombre, fn))


AMBAR = rampa('1a0a04', '3c1a08', '66300e', '965018', 'c87c2c')


def mandibula(nombre, R=AMBAR):
    """Una mandíbula (y las uñas): ámbar oscuro, más clara arriba, con los dientes de un píxel (claros, uno sí y uno
    no) a lo largo."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 2.0) + (xs == 0) * 0.5 - (xs == tw - 1) * 0.5
        if cara in ('izq', 'der', 'abajo', 'arriba'):
            v = v + ((ys % 3) == 0) * 0.9 - ((ys % 3) == 2) * 0.3
        v = v - (ys >= th - 2) * 0.8
        return L._rgba(L.color_continuo(R, v)), None
    return B.fino(B.Pintor(nombre, fn))


# ======================================================================================================================
#  El cuerpo de la hormiga soldado, erguida
# ======================================================================================================================
LEAN = 12            # lo que se inclina hacia delante el tórax levantado (grados)


def hormiga(m, P, cabeza=(7, 6, 6), mandibulas=1.0, ojo=None, antenas=None, gaster_tam=(8, 7, 10),
            brazos='lanza'):
    """El cuerpo: el tórax de atrás (con las cuatro patas en el suelo), la cintura (el pecíolo) y el gáster detrás, el
    tórax de delante levantado (con los dos brazos), el cuello y la cabeza con la cara, los ojos compuestos, las
    antenas acodadas y las mandíbulas. P: los pintores ('torax', 'gaster', 'pata', 'brazo', 'cabeza', 'cara',
    'mandibula', 'antena'). brazos: 'lanza' (la derecha sujeta un asta delante, la izquierda abierta), 'alto' (los dos
    arriba, sujetando algo sobre la cabeza) o 'guardia' (los dos delante, cerrados). Devuelve los puntos que usan los
    añadidos de cada una."""
    # El tórax de atrás: la raíz. Las cuatro patas salen de aquí.
    m.parte('cuerpo', None, (0, 8, 0))
    redondo(m, 'cuerpo', (0, 8, -0.5), (6, 5, 8), P['torax'])
    # El pecíolo (la cintura, con su escama de pie) y el gáster, detrás.
    m.caja('cuerpo', (0, 8.5, -5.5), (2, 3, 2), P['torax'])
    gw, gh, gd = gaster_tam
    m.parte('gaster', 'cuerpo', (0, 8.5, -6))
    c_gas = np.array((0, 8.5 + (gh - 7) * 0.3, -6.5 - gd / 2))
    redondo(m, 'gaster', tuple(c_gas), gaster_tam, P['gaster'], rot=(-10, 0, 0), bisel=2)
    # La parte de delante del gáster, más estrecha: la forma de huevo.
    redondo(m, 'gaster', tuple(rotar(c_gas + np.array((0, -0.2, gd / 2 + 0.6)), c_gas, (-10, 0, 0))),
            (gw - 2, gh - 2, 3), P['gaster'], rot=(-10, 0, 0))

    # El tórax de delante, levantado e inclinado hacia delante.
    piv_t = np.array((0, 9.5, 2.0))
    m.parte('torso', 'cuerpo', tuple(piv_t))
    rt = (LEAN, 0, 0)
    redondo(m, 'torso', tuple(rotar((0, 13.0, 2.0), piv_t, rt)), (6, 8, 5), P['torax'], rot=rt)
    m.caja('torso', tuple(rotar((0, 17.5, 2.0), piv_t, rt)), (3, 2, 3), P['torax'], rot=rt)
    cuello = rotar((0, 18.0, 2.0), piv_t, rt)

    # La cabeza.
    cw, ch, cd = cabeza
    m.parte('cabeza', 'torso', tuple(cuello))
    rc = (6, 0, 0)
    c_cab = cuello + np.array((0, ch / 2 + 0.2, cd / 2 - 1.5))
    redondo(m, 'cabeza', tuple(c_cab), cabeza, P['cabeza'], rot=rc, frente=P['cara'])
    frente_z = c_cab[2] + cd / 2
    # Los ojos compuestos, ovalados, a los lados de la cabeza y hacia delante: asoman un píxel (de frente se ven como
    # dos bultos a los lados de la cara).
    o = ojo or ojo_compuesto('ojo_hormiga')
    alto_ojo = 3 if ch >= 6 else 2
    for lado, ld in LADOS:
        # En la esquina de delante, a ras: rellena el chaflán (de frente, una columna de un píxel; de lado, tres).
        m.caja('cabeza', tuple(rotar((lado * (cw / 2 - 0.5 + 0.03), c_cab[1] + 0.5, c_cab[2] + cd / 2 - 1.5 + 0.03),
                                     c_cab, rc)), (1, alto_ojo, 3), o, rot=rc)
    # Las antenas acodadas: el escapo sube y se abre; el funículo va hacia delante.
    if antenas is not None:
        for lado, ld in LADOS:
            base = np.array((lado * 1.5, c_cab[1] + ch / 2 - 1.0, frente_z - 0.8))
            m.parte(f'antena_{ld}', 'cabeza', tuple(base))
            codo = base + np.array((lado * 1.6, 4.0, 0.6))
            m.viga(f'antena_{ld}', base, codo, 1, antenas)
            m.parte(f'antena_{ld}b', f'antena_{ld}', tuple(codo))
            punta = codo + np.array((lado * 1.4, 0.6, 4.6))
            m.viga(f'antena_{ld}b', codo, punta, 1, antenas)
    # Las mandíbulas, debajo del clípeo: hacia delante y cerrándose hacia dentro.
    mand = []
    if mandibulas:
        for lado, ld in LADOS:
            k = mandibulas
            piv = np.array((lado * min(2.0, cw / 2 - 1.5), c_cab[1] - ch / 2 + 0.8, frente_z - 0.8))
            m.parte(f'mandibula_{ld}', 'cabeza', tuple(piv))
            a = piv
            b = a + np.array((lado * 0.4 * k, -0.9 * k, 2.2 * k))
            c = b + np.array((-lado * 1.9 * k, -0.4 * k, 0.8 * k))
            m.viga(f'mandibula_{ld}', a, b, 1 if k < 1.5 else 2, P['mandibula'], ancho=2, extra=0.6)
            m.viga(f'mandibula_{ld}', b, c, 1, P['mandibula'], ancho=1 if k < 1.5 else 2, extra=0.6)
            mand.append(c)

    # Los brazos (las patas de delante), desde los hombros.
    hombros = {}
    manos = {}
    for lado, ld in LADOS:
        h = rotar((lado * 3.0, 15.5, 2.0), piv_t, rt)
        hombros[ld] = h
        if brazos == 'alto':
            codo = h + np.array((lado * 2.4, 5.0, 0.4))
            mano = codo + np.array((-lado * 1.6, 5.0, 0.2))
        elif brazos == 'guardia':
            codo = h + np.array((lado * 1.4, -3.6, 2.2))
            mano = codo + np.array((-lado * 1.4, 1.6, 3.4))
        else:
            # El asta, de pie delante del hombro derecho: la mano derecha la coge arriba y la izquierda, cruzando por
            # delante del pecho, más abajo (la guardia del soldado).
            # El asta, de pie al costado derecho: la mano derecha la coge delante del hombro; la izquierda, suelta,
            # algo adelantada con la garra hacia abajo.
            if lado < 0:
                codo = h + np.array((-1.6, -3.6, 1.0))
                mano = codo + np.array((-0.4, 0.8, 3.4))
            else:
                codo = h + np.array((1.2, -3.8, 1.4))
                mano = codo + np.array((-0.2, -1.4, 3.0))
        m.parte(f'brazo_{ld}', 'torso', tuple(h))
        m.viga(f'brazo_{ld}', h, codo, 2, P['brazo'], extra=0.6)
        m.parte(f'antebrazo_{ld}', f'brazo_{ld}', tuple(codo))
        m.viga(f'antebrazo_{ld}', codo, mano, 2, P['brazo'], extra=0.4)
        # La garra: dos uñas de un píxel.
        d = B._u(mano - codo)
        m.viga(f'antebrazo_{ld}', mano, mano + d * 1.2 + np.array((0, -0.6, 0)), 1, P['mandibula'])
        manos[ld] = mano

    # Las cuatro patas: el muslo sube un poco hasta la rodilla y la tibia baja al suelo, abiertas.
    tripodes = ([], [])
    for i, (z, ang) in enumerate(((1.0, 38), (-2.5, -40))):
        for lado, ld in LADOS:
            phi = math.radians(ang)
            dvec = np.array((lado * math.cos(phi), 0.0, math.sin(phi)))
            cadera = np.array((lado * 2.6, 7.0, z))
            rodilla = cadera + dvec * 4.2 + np.array((0, 2.0, 0))
            pie = rodilla + dvec * 3.4 + np.array((0, -rodilla[1] + 0.5, 0))
            theta = math.degrees(math.atan2(dvec[0], dvec[2]))
            n = m.parte(f'pata_{ld}{i}', 'cuerpo', tuple(cadera), rot=(0, theta, 0))
            m.viga(n, cadera, rodilla, 2, P['pata'], extra=0.6)
            n2 = m.parte(f'pata_{ld}{i}b', n, tuple(rodilla), rot=(0, theta, 0))
            m.viga(n2, rodilla, pie, 2, P['pata'], extra=0.4)
            # El tarso: la uña que apoya, hacia fuera.
            m.viga(n2, pie + np.array((0, 0.0, 0)), pie + dvec * 1.8 + np.array((0, -0.4, 0)), 1, P['mandibula'])
            tripodes[(i + (0 if lado > 0 else 1)) % 2].append((f'pata_{ld}{i}', f'pata_{ld}{i}b', lado, i))
    m.mirar(('cabeza', 0.7))
    return dict(tripodes=tripodes, cabeza=c_cab, gaster=c_gas, manos=manos, hombros=hombros, cuello=cuello,
                frente=frente_z, torso=piv_t)


def anims_hormiga(m, info, paso=0.5, swing=20, alza=14):
    """andar: el paso en diagonal de las cuatro patas (dos apoyadas, dos que se adelantan levantadas), el torso que se
    mece y los brazos quietos; correr: lo mismo más deprisa y con el torso echado hacia delante; reposo: respira (el
    gáster sube y baja) y mece el torso; siempre: las antenas tantean y las mandíbulas se abren y cierran; muerte: se le
    doblan las patas y cae de lado, con las patas encogidas."""
    for nombre, per, inclina in (('andar', paso, 0.0), ('correr', paso * 0.62, 10.0)):
        a = m.anim(nombre, per, bucle=True)
        for g, tri in enumerate(info['tripodes']):
            for muslo, tib, lado, i in tri:
                fase = 0.5 * g
                a.onda(muslo, 'r', 1, swing * (1.0 if i == 0 else -1.0) * (-lado), fase=fase)
                a.onda(muslo, 'r', 0, -alza, fase=fase + 0.25, forma=lambda v: max(0.0, v))
                a.onda(tib, 'r', 0, alza * 0.6, fase=fase + 0.25, forma=lambda v: max(0.0, v))
        a.onda('torso', 'r', 2, 3, periodo=per)
        a.onda('torso', 'r', 0, 2.5, periodo=per / 2, base=inclina)
        a.onda('gaster', 'r', 0, 3, periodo=per / 2, fase=0.25)
        a.onda('cabeza', 'r', 2, -2, periodo=per)
    r = m.anim('reposo', 3.0, bucle=True)
    r.onda('gaster', 'r', 0, 3, periodo=1.5)
    r.onda('gaster', 'e', 1, 0.03, periodo=1.5, base=1.0)
    r.onda('torso', 'r', 0, 2, periodo=3.0)
    r.onda('cabeza', 'r', 1, 6, periodo=3.0, fase=0.2)
    s = m.anim('siempre', 2.0, bucle=True)
    for lado, ld in LADOS:
        if f'antena_{ld}' in m.partes:
            s.onda(f'antena_{ld}', 'r', 0, 10, periodo=1.0, fase=0.25 if lado > 0 else 0.0)
            s.onda(f'antena_{ld}b', 'r', 1, 12 * lado, periodo=0.66, fase=0.4 if lado > 0 else 0.1)
        if f'mandibula_{ld}' in m.partes:
            s.onda(f'mandibula_{ld}', 'r', 1, -lado * 9, periodo=1.0, forma=lambda v: max(0.0, v))
    d = m.anim('muerte', 1.2)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.25, 4, 0, -6), (0.6, 0, 0, -70), (0.85, 0, 0, -86), (1.2, 0, 0, -84)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.25, 0, -1.5, 0), (0.6, 0, -3.0, 0), (1.2, 0, -3.6, 0)])
    d.rot('torso', [(0, 0, 0, 0), (0.3, -18, 0, 0), (0.7, 22, 0, 0), (1.2, 18, 0, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, -20, 0, 0), (0.9, 30, 0, 10), (1.2, 26, 0, 10)])
    for tri in info['tripodes']:
        for muslo, tib, lado, i in tri:
            d.rot(muslo, [(0, 0, 0, 0), (0.5, -30, 0, 0), (1.2, -45, 0, 0)])
            d.rot(tib, [(0, 0, 0, 0), (0.5, 40, 0, 0), (1.2, 70, 0, 0)])
    for lado, ld in LADOS:
        d.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.6, -40, 0, lado * 20), (1.2, -30, 0, lado * 30)])
        d.rot(f'antebrazo_{ld}', [(0, 0, 0, 0), (0.6, -50, 0, 0), (1.2, -60, 0, 0)])


def ataque_mordisco(m, info):
    """ataque: echa el torso atrás, se lanza y muerde (las mandíbulas se abren y se cierran de golpe)."""
    at = m.anim('ataque', 0.55)
    at.rot('torso', [(0, 0, 0, 0), (0.14, -14, 0, 0), (0.26, 22, 0, 0), (0.55, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.14, -10, 0, 0), (0.26, 14, 0, 0), (0.55, 0, 0, 0)])
    for lado, ld in LADOS:
        if f'mandibula_{ld}' in m.partes:
            at.rot(f'mandibula_{ld}', [(0, 0, 0, 0), (0.14, 0, -lado * 30, 0), (0.26, 0, lado * 10, 0), (0.55, 0, 0, 0)])
    return at


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('andar', 0.12), ('correr', 0.1), ('ataque', 0.26), ('muerte', 1.2)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


# ======================================================================================================================
#  Las partículas
# ======================================================================================================================
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


def nube(color, n=16):
    cuadros = []
    for k in range(4):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            r0 = 0.22 + 0.06 * k
            bulto = (d < r0) | (np.hypot(x - 0.32, y - 0.42) < r0 * 0.7) | (np.hypot(x - 0.66, y - 0.4) < r0 * 0.65)
            return color[0], color[1], color[2], bulto * (235 - 30 * k)
        cuadros.append(B.sprite(n, f))
    return cuadros


# ======================================================================================================================
#  Las cinco hormigas
# ======================================================================================================================
PARDA = rampa('241006', '42210c', '683816', '925426', 'bc7a42')
NEGRA_PARDA = rampa('0c0604', '1a0e08', '2a180e', '3e2618', '5a3a26')
MADERA = rampa('34200e', '543618', '785024', '9c6c34', 'c49250')
PEDERNAL = rampa('1e1e24', '34343c', '4c4c56', '6c6c78', '9a9aa6')
BELLOTA = rampa('2a1e12', '4a3822', '6c5434', '8e7048', 'b09064')
CUERDA = rampa('3a2a14', '5a4424', '7e6236', '9e824a', 'c0a468')


def pintores(nombre, R, gaster_p=None, cabeza_p=None, brazo_r=None, gaster_r=None):
    q = quitina(f'quitina_{nombre}', R, sutura=0.45)
    return {'torax': q, 'gaster': gaster_p or gaster(f'gaster_{nombre}', gaster_r if gaster_r is not None else R),
            'cabeza': cabeza_p or quitina(f'cabeza_{nombre}', R, base=2.2),
            'cara': cara(f'cara_{nombre}', R, base=2.2), 'pata': pata(f'pata_{nombre}', R),
            'brazo': pata(f'brazo_{nombre}', brazo_r if brazo_r is not None else R, base=2.2),
            'mandibula': mandibula('mandibula_ambar'), 'antena': antena(f'antena_{nombre}', R)}


def cupula(nombre):
    """La cúpula de la bellota: escamas en filas desplazadas (cada una, un píxel claro arriba y uno oscuro abajo), más
    clara arriba; el borde de abajo, el canto de las escamas."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = _v(tw, th, cara, s, 2.0, 0.8)
        # Escamas, pintadas finas: de 4 x 3, en filas desplazadas; cada una con la punta clara arriba, la base en sombra
        # y el lado derecho oscuro (donde la tapa la de al lado).
        fila = ys // 3
        xe = (xs + (fila % 2) * 2) % 4
        ye = ys % 3
        v = v + (ye == 0) * 0.6 - (ye == 2) * 0.55 - (xe == 3) * 0.45
        if cara not in ('arriba', 'abajo'):
            v = np.where(ys >= th - 2, v - 0.5, v)
        return L._rgba(L.color_continuo(BELLOTA, v)), None
    return B.fino(B.Pintor(nombre, fn))


def madera(nombre):
    """El asta: la veta a lo largo (un píxel más oscuro de cuando en cuando) y algún nudo."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = np.full((th, tw), 2.2) + (xs == 0) * 0.4
        v = v - (((ys + xs * 3 + s) % 5) == 0) * 0.6 - (a < 0.04) * 1.0
        return L._rgba(L.color_continuo(MADERA, v)), None
    return B.Pintor(nombre, fn)


def pedernal_tallado(nombre):
    """La punta de pedernal en una hoja: un rombo alargado (lo de fuera, transparente), oscuro, con las lascas del
    tallado (arcos de un píxel más claros) y el filo claro."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th
        ancho = np.where(v < 0.62, v / 0.62, (1 - v) / 0.38) * 0.5
        dentro = np.abs(u) < ancho + 0.02
        val = 2.0 + (np.abs(u) > ancho - 1.0 / tw) * 1.4
        val = val + (((ys + np.abs(xs - (tw - 1) / 2) * 2) % 3) == 0) * 0.7
        tex = L._rgba(L.color_continuo(PEDERNAL, val))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn))


def lancera(raiz):
    """La Hormiga Lancera (Cantimplo): parda y lustrosa, con la cúpula de una bellota por casco (con su rabito) y una
    lanza de madera con la punta de pedernal tallado y atada con cuerda, en alto en la mano derecha: la baja de golpe
    al atacar."""
    m = B.Modelo('lancera', K=2, ancho=128)
    m.escala = 1.0
    P = pintores('parda', PARDA, gaster_r=NEGRA_PARDA)
    info = hormiga(m, P, antenas=P['antena'])
    c = info['cabeza']
    # El casco: la cúpula de la bellota, encajada hasta las cejas, y su rabito.
    rc = (6, 0, 0)
    cu = cupula('cupula')
    sombra = {'abajo': B.liso('cupula_dentro', BELLOTA, base=0)}
    redondo(m, 'cabeza', tuple(rotar(c + np.array((0, 3.0, -0.4)), c, rc)), (9, 5, 8), cu, rot=rc, caras=sombra, bisel=2)
    m.caja('cabeza', tuple(rotar(c + np.array((0, 6.0, -0.6)), c, rc)), (1, 2, 1), B.liso('rabito_bellota', BELLOTA, base=1),
           rot=rc)
    # La lanza, en la mano derecha: el asta de pie, algo echada hacia delante, con la punta muy por encima de la cabeza.
    mano = info['manos']['d']
    m.parte('lanza', 'antebrazo_d', tuple(mano))
    abajo = mano + np.array((0.2, -12.0, -0.6))
    arriba = mano + np.array((-0.1, 13.0, 0.9))
    m.viga('lanza', abajo, arriba, 1, madera('asta'))
    eje = B._u(arriba - abajo)
    punta = pedernal_tallado('pedernal')
    for giro in (0, 90):
        m.hoja('lanza', tuple(arriba + eje * 3.4), 4, 7, punta, rot=(0, giro, 0))
    m.viga('lanza', arriba - eje * 1.2, arriba + eje * 0.6, 2, B.anillos('atadura', CUERDA, paso=1))
    anims_hormiga(m, info)
    at = m.anim('ataque', 0.6)
    at.rot('torso', [(0, 0, 0, 0), (0.18, -16, 0, 0), (0.3, 24, 0, 0), (0.6, 0, 0, 0)])
    at.rot('brazo_d', [(0, 0, 0, 0), (0.18, -40, 0, 0), (0.3, 40, 0, 0), (0.6, 0, 0, 0)])
    at.rot('antebrazo_d', [(0, 0, 0, 0), (0.18, -10, 0, 0), (0.3, 50, 0, 0), (0.6, 0, 0, 0)])
    at.rot('brazo_i', [(0, 0, 0, 0), (0.18, -20, 0, 10), (0.3, 20, 0, 0), (0.6, 0, 0, 0)])
    m.paso = 4.0

    def dib(px, filas, c_):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c_('000000')
        for f in (3, 4):
            for x in range(5, 11):
                px[x, f] = c_('8c7a40')
        for x, f in ((11, 13), (11, 11), (11, 9), (11, 7), (11, 5)):
            px[x, f] = c_('9c6c34')
        px[11, 3] = c_('6c6c78')
    return terminar(m, raiz, 'Hormiga Lancera', 'Spear Ant', (('bc7a42', '925426', '683816'), ('241006', '120802'), dib),
                    ((1.7, 1.5, 2.3), (0, 0.85, 0)),
                    particulas=(('astilla', esquirla((156, 108, 52))),))


GRIS = rampa('1a1e24', '2a2f36', '3e444c', '575e67', '767e88')
BARRO = rampa('3a1a0c', '5e2c14', '84421e', 'a8602e', 'c8844a')
MECHA = rampa('241a0c', '3e2e16', '5c4422', '7c5e30', '9c7c44')
FUEGO = rampa('6a1604', 'c04a0a', 'f08a1a', 'ffc84a', 'fff2b0')
CASTANA = rampa('1a0a04', '341608', '52240e', '763616', '9a4c22')
AMBAR_CAB = rampa('3a1404', '6a2c0a', '9a4a14', 'c87024', 'eaa048')
NEGRA = rampa('040406', '0a0a0e', '14141a', '20202a', '30303c')
VERDE = rampa('0a3a0a', '127012', '2ab82a', '7aff5a', 'd8ffc8')
ROJA = rampa('2a0604', '520c08', '86160c', 'b82a16', 'e65a34')
CARBON = rampa('120302', '2a0705', '4a0e08', '74180c', 'a02a14')


def llama(nombre, r=FUEGO):
    """Una llama en una hoja, al píxel: la gota de fuego (lo de fuera, transparente), amarilla fuera y casi blanca en
    el centro de abajo; encendida entera."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th
        dentro = np.abs(u) < 0.5 * np.clip(v * 1.3, 0.2, 1.0) - 0.02 * (v < 0.3)
        val = 2.2 + v * 1.4 - np.abs(u) * 2.0
        tex = L._rgba(L.color_continuo(r, val))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, tex.copy()
    return B.fino(B.Pintor(nombre, fn, pleno=True))


def barro_cocido(nombre):
    """El barro cocido de la bomba: el tono que corre (más claro arriba), las marcas de los dedos del alfarero (arcos
    de un píxel más oscuros, en filas) y alguna grieta fina."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara, s, 2.2, 1.1)
        # Las marcas de los dedos del alfarero (arcos finos en filas) y alguna grieta.
        dedo = ((xs // 2 + (ys // 4) * 3 + s) % 5 == 0) & ((ys % 4) == 1)
        v = v - dedo * 0.5 - (a < 0.02) * 0.9 + (a > 0.98) * 0.5
        rgb = L.color_continuo(BARRO, v)
        # La cuerda que la ata (todas las cajas de la bomba están centradas): una vuelta por el ecuador y otra de
        # arriba abajo, de dos píxeles finos de gruesa y trenzada (las vueltas en diagonal), con su sombra en el barro.
        cy, cx = th / 2.0, tw / 2.0
        if cara in ('arriba', 'abajo'):
            cuerda = (np.abs(xs + 0.5 - cx) <= 1) | (np.abs(ys + 0.5 - cy) <= 1)
        else:
            cuerda = (np.abs(ys + 0.5 - cy) <= 1) | ((np.abs(xs + 0.5 - cx) <= 1) & (cara in ('frente', 'atras')))
        t = (xs + ys) % 3
        sombra_c = ~cuerda & (np.roll(cuerda, 1, axis=0) if cara not in ('arriba', 'abajo') else False)
        rgb = np.where(sombra_c[..., None], rgb * 0.72, rgb)
        rgb = np.where(cuerda[..., None], L.color_continuo(CUERDA, 1.8 + (t == 0) * 1.6 + (t == 1) * 0.7), rgb)
        return L._rgba(rgb), None
    return B.fino(B.Pintor(nombre, fn))


def polvorin(raiz):
    """La Hormiga Polvorín (Bombermant): gris pizarra, con una bomba de barro cocido en alto, sujeta con los dos brazos
    por encima de la cabeza, atada con dos vueltas de cuerda y con la mecha encendida (chisporrotea siempre); cuando
    te tiene cerca, la bomba se hincha y revienta."""
    m = B.Modelo('polvorin', K=2, ancho=128)
    m.escala = 1.0
    P = pintores('gris', GRIS)
    info = hormiga(m, P, antenas=P['antena'], brazos='alto')
    ma, mb = info['manos']['i'], info['manos']['d']
    cb = (ma + mb) / 2 + np.array((0, 3.0, 0.2))
    m.parte('bomba', 'torso', tuple(cb))
    redondo(m, 'bomba', tuple(cb), (7, 7, 7), barro_cocido('barro_cocido'), bisel=2)
    # La boca de la bomba (el tapón de barro) y la mecha que sale torcida.
    m.caja_desde('bomba', tuple(cb + np.array((0, 3.3, 0))), (3, 1, 3), B.liso('tapon', BARRO, base=1))
    m.parte('chispa', 'bomba', tuple(cb + np.array((1.0, 6.4, -0.6))))
    m1 = cb + np.array((0, 4.2, 0))
    m2 = m1 + np.array((0.4, 1.4, -0.2))
    m3 = m2 + np.array((0.6, 0.8, -0.4))
    m.viga('chispa', m1, m2, 1, B.anillos('mecha_p', MECHA, paso=1), extra=0.4)
    m.viga('chispa', m2, m3, 1, B.anillos('mecha_p', MECHA, paso=1), extra=0.4)
    m.caja('chispa', tuple(m3 + np.array((0, 0.4, 0))), (1, 1, 1), B.luz('ascua_mecha', FUEGO))
    for giro in (0, 90):
        m.hoja('chispa', tuple(m3 + np.array((0, 1.8, 0))), 2, 3, llama('llama_mecha'), rot=(0, giro, 0))
    anims_hormiga(m, info, paso=0.55)
    ataque_mordisco(m, info)
    s = m.anims['siempre']
    s.esc('chispa', [(0, 1, 1, 1), (0.1, 1.3, 1.4, 1.3), (0.2, 0.85, 0.8, 0.85), (0.35, 1.2, 1.3, 1.2), (0.5, 1, 1, 1),
                     (2.0, 1, 1, 1)])
    # Al andar, la bomba se bambolea encima.
    m.anims['andar'].onda('bomba', 'r', 2, 4, periodo=0.55)
    e = m.anim('especial', 1.0)
    e.esc('bomba', [(0, 1, 1, 1), (0.15, 1.08, 1.08, 1.08), (0.3, 1, 1, 1), (0.45, 1.12, 1.12, 1.12), (0.6, 1, 1, 1),
                    (0.75, 1.18, 1.18, 1.18), (1.0, 1.25, 1.25, 1.25)])
    e.esc('chispa', [(0, 1, 1, 1), (1.0, 2.0, 2.4, 2.0)])
    for lado, ld in LADOS:
        e.onda(f'brazo_{ld}', 'r', 2, lado * 4, periodo=0.15)
    m.paso = 3.6

    def dib(px, filas, c_):
        for f in range(3, 7):
            for x in range(6, 10):
                px[x, f] = c_('84421e')
        px[7, 4] = c_('a8602e')
        px[8, 2] = c_('ffc84a')
        for x, f in ((6, 9), (9, 9)):
            px[x, f] = c_('000000')
    return terminar(m, raiz, 'Hormiga Polvorín', 'Powder Ant', (('5a6169', '40464e', '2c3138'), ('101216', '000000'), dib),
                    ((1.8, 1.7, 2.4), (0, 1.0, 0)),
                    particulas=(('chispa', chispa((255, 200, 74))), ('barro', esquirla((132, 66, 30))),
                                ('humo', nube((80, 80, 88)))),
                    poses=[('andar', 0.12), ('correr', 0.1), ('especial', 0.75), ('muerte', 1.2)])


def cabezona(raiz):
    """La Hormiga Cabezona (Parapona): castaña oscura, con la cabeza ámbar el doble de grande que la de las demás (la
    frente acorazada, lisa y lustrosa) y unas mandíbulas de tenaza largas y dentadas: su mordisco te deja lentísimo.
    Lleva los brazos en guardia, delante del pecho."""
    m = B.Modelo('cabezona', K=2, ancho=128)
    m.escala = 1.0
    P = pintores('castana', CASTANA, cabeza_p=quitina('cabeza_ambar', AMBAR_CAB, base=2.2, poros=0.04))
    P['cara'] = cara('cara_ambar', AMBAR_CAB, base=2.2)
    info = hormiga(m, P, cabeza=(10, 8, 8), mandibulas=1.7, antenas=P['antena'], brazos='guardia')
    anims_hormiga(m, info, paso=0.6)
    ataque_mordisco(m, info)
    m.anims['ataque'].rot('cabeza', [(0, 0, 0, 0), (0.14, -16, 0, 0), (0.26, 18, 0, 0), (0.55, 0, 0, 0)])
    m.paso = 3.4

    def dib(px, filas, c_):
        for f in range(2, 8):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c_('c87024')
        for x, f in ((5, 5), (10, 5)):
            px[x, f] = c_('000000')
        for x, f in ((5, 9), (6, 10), (9, 10), (10, 9)):
            px[x, f] = c_('966018')
    return terminar(m, raiz, 'Hormiga Cabezona', 'Bighead Ant', (('9a4c22', '763616', '52240e'), ('1a0a04', '0a0402'), dib),
                    ((1.8, 1.6, 2.4), (0, 0.95, 0)),
                    particulas=(('astilla', esquirla((150, 84, 36))),))


def radiactiva(raiz):
    """La Hormiga Radiactiva (Compona): negra como el carbón, con el gáster hinchado como el de las hormigas de miel y,
    entre sus placas, la membrana tirante que brilla de verde; los ojos, encendidos del mismo verde. Brazos en
    guardia."""
    m = B.Modelo('radiactiva', K=2, ancho=128)
    m.escala = 1.0
    P = pintores('negra', NEGRA, gaster_p=gaster('gaster_radiactivo', NEGRA, placas=4, membrana=VERDE, largo=11))
    info = hormiga(m, P, antenas=P['antena'], gaster_tam=(10, 9, 11), brazos='guardia',
                   ojo=ojo_compuesto('ojo_radiactivo', brilla=VERDE))
    anims_hormiga(m, info)
    ataque_mordisco(m, info)
    # El gáster late despacio (hinchado de lo que lleva dentro).
    m.anims['siempre'].onda('gaster', 'e', 0, 0.035, periodo=1.0, base=1.0)
    m.paso = 3.8

    def dib(px, filas, c_):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c_('7aff5a')
        for f in (9, 11, 13):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c_('2ab82a')
    return terminar(m, raiz, 'Hormiga Radiactiva', 'Radiant Ant', (('30303c', '20202a', '14141a'), ('040406', '000000'), dib),
                    ((1.8, 1.5, 2.4), (0, 0.85, 0)),
                    particulas=(('radiacion', chispa((122, 255, 90))),))


def brasa(raiz):
    """La Hormiga Brasa (Solvetus): roja, con grietas de brasa que brillan por todo el cuerpo y una tea encendida en la
    mano derecha (la blande al atacar); va soltando chispas."""
    m = B.Modelo('brasa', K=2, ancho=128)
    m.escala = 1.0

    def grietas(xs, ys, tw, th, cara_, s):
        # Pintadas finas (a 32 por bloque): grietas largas y continuas, de medio píxel, y alrededor el resplandor.
        g = B.grietas(tw, th, s, cara_, cuantas=max(1, (tw * th) // 110), largo=max(8, max(tw, th) * 2), giro=0.3,
                      ramas=0.08)
        return g.astype(float) * 0.95 + B.vecinos(g).astype(float) * 0.3
    q = B.fino(quitina('quitina_brasa', CARBON, sutura=0.45, marca=grietas, rm=FUEGO))
    P = pintores('carbon', CARBON)
    P['torax'] = q
    P['gaster'] = B.fino(quitina('gaster_brasa', CARBON, marca=grietas, rm=FUEGO))
    P['cabeza'] = B.fino(quitina('cabeza_brasa', CARBON, base=2.2, marca=grietas, rm=FUEGO))
    info = hormiga(m, P, antenas=P['antena'])
    # La tea: un palo corto en la mano derecha, con la punta en ascuas y su llama.
    mano = info['manos']['d']
    m.parte('tea', 'antebrazo_d', tuple(mano))
    abajo = mano + np.array((0.1, -4.0, -0.4))
    arriba = mano + np.array((-0.1, 7.0, 0.9))
    m.viga('tea', abajo, arriba, 1, madera('palo_tea'))
    eje = B._u(arriba - abajo)
    m.viga('tea', arriba - eje * 0.4, arriba + eje * 1.6, 2, B.luz('ascuas_tea', FUEGO))
    m.parte('llama', 'tea', tuple(arriba + eje * 1.6))
    for giro in (0, 90):
        m.hoja('llama', tuple(arriba + eje * 1.6 + np.array((0, 2.5, 0))), 3, 5, llama('llama_tea'), rot=(0, giro, 0))
    anims_hormiga(m, info)
    m.anims['siempre'].onda('llama', 'e', 1, 0.15, base=1.0, periodo=0.5)
    at = m.anim('ataque', 0.55)
    at.rot('torso', [(0, 0, 0, 0), (0.16, -12, 0, 0), (0.28, 18, 0, 0), (0.55, 0, 0, 0)])
    at.rot('brazo_d', [(0, 0, 0, 0), (0.16, -70, 0, -20), (0.28, 30, 0, 10), (0.55, 0, 0, 0)])
    at.rot('antebrazo_d', [(0, 0, 0, 0), (0.16, -20, 0, 0), (0.28, 40, 0, 0), (0.55, 0, 0, 0)])
    m.paso = 4.0

    def dib(px, filas, c_):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c_('000000')
        for x, f in ((4, 9), (5, 10), (10, 9), (11, 11), (7, 12), (8, 13)):
            px[x, f] = c_('ffc84a')
        px[11, 3] = c_('fff2b0')
        px[11, 4] = c_('f08a1a')
    return terminar(m, raiz, 'Hormiga Brasa', 'Ember Ant', (('e65a34', 'b82a16', '86160c'), ('2a0604', '120202'), dib),
                    ((1.8, 1.5, 2.4), (0, 0.85, 0)),
                    particulas=(('brasa', chispa((255, 150, 40))),))


MOBS = {'lancera': lancera, 'polvorin': polvorin, 'cabezona': cabezona, 'radiactiva': radiactiva, 'brasa': brasa}


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    # El píxel de Minecraft (16 por bloque): van a escala 1, así que es de 1 píxel del modelo.
    B.TEXEL = 1.0
    for p in pedidos:
        MOBS[p](raiz)
    B.TEXEL = None


if __name__ == '__main__':
    main()
