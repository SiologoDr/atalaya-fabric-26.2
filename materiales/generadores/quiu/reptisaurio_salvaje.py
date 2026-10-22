"""
El Reptisaurio Salvaje (DEDsafío 2, cartel del día 2; libro del juego: «Un reptil encorvado, verde oliva casi negro,
con musgo en la cabeza y huesos en los hombros: anda con los brazos colgando hasta las rodillas y ataca cuerpo a cuerpo
con sus garras, que empujan»).

Rehecho con la misma anatomía realista, proporciones de gorila, cabeza tótem y animaciones dinámicas que el Reptisaurio
con Lanza:
  - Cabeza tótem apilada con cráneo, ojos de caja con ceja que doblan la esquina, hocico saliente con fosas nasales,
    boca con cuatro dientes cuadrados (dos largos en los extremos y dos cortos en medio) y mandíbula móvil con mentón.
  - Cresta y melena de hojas de musgo salvaje a lo largo del cráneo y la espalda.
  - Huesos en L característicos en cada hombro que acompañan la caída del brazo.
  - Brazos largos con brazaletes de hueso y tres garras curvas en gancho en cada mano.
  - Modo neutral: brazos relajados cayendo a los costados al andar y reposar; al detectar objetivo entra en alerta
    alzando las garras en guardia de combate.
  - Animaciones: zarpazo doble feroz, rugido al detectar presa y salto con azote de garras.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa
from bestiario_reptiles import FINO, H, P, caja_en, lamina
from quiu.reptisaurio_lancero import (
    CABEZA_GIRO_LANCERO,
    CABEZA_Y_LANCERO,
    CABEZA_Z_LANCERO,
    ENCORVADO_LANCERO,
    LADOS_LANCERO,
    Y_CADERA_LANCERO,
    dir_lancero,
    hoja_en_lancero,
    hoja_lancero,
    hueso_lancero,
    garra_lancero,
    piernas_lancero,
    tronco_lancero,
    boca_lancero,
    dientes_lancero,
    mandibula_lancero,
    hocico_lancero,
    ojo_caja_lancero,
    _sobre_piel_lancero,
    _pon,
)

ID = 'reptisaurio_salvaje'
TAM = 1.0

# ======================================================================================================================
#  Paleta y colores
# ======================================================================================================================
VERDE_SALVAJE = rampa('061c0a', '0c3214', '165222', '247c36', '38a84c')
CRESTA_SALVAJE = rampa('0a2a08', '164e10', '28761a', '42a42a', '6acd46')
OJO_SALVAJE = rampa('8a7c1e', 'a69628', 'c0ae30', 'd4c440', 'e8da5c')
BOCA_SALVAJE = rampa('1c0006', '2e020a', '420410', '580a18', '701422')
HUESO_SALVAJE = rampa('5c564a', '7a7364', '9c9482', 'bcb4a0', 'ded6c2')
NEGRO_SALVAJE = H('050403')

HUEVO = (
    ('165222', '0c3214', '061c0a'),
    ('42a42a', '0a2a08'),
    [
        ((5, 6), 'd4c440'), ((6, 6), '050403'), ((9, 6), 'd4c440'), ((10, 6), '050403'),
        ((7, 2), '6acd46'), ((8, 3), '42a42a'), ((6, 9), '420410'), ((9, 9), '420410'),
        ((4, 4), 'ded6c2'), ((11, 4), 'ded6c2'),
    ],
)


# ======================================================================================================================
#  Pintores
# ======================================================================================================================
def piel_salvaje(nombre, R_=VERDE_SALVAJE, base=2.1, luz=0.7, bandas=0, semilla=0):
    """Piel verde musgosa profunda con variación orgánica al píxel."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), base + luz * 0.9)
        elif c == 'abajo':
            v = np.full((th, tw), base - luz * 0.8)
        else:
            v = base + luz * (0.3 - (ys + 0.5) / th * 0.6)
        a = _azar1((xs + (ys // 2) % 2) // 2, ys // 2, s * 7 + semilla)
        v = v + np.where(a < 0.22, -0.6, np.where(a > 0.8, 0.55, 0.0))
        b = _azar1(xs // 2, ys // 3, s * 11 + semilla + 5)
        v = v - (b < 0.08) * 0.65
        if bandas and c not in ('arriba', 'abajo'):
            v = v - ((ys % bandas) == bandas - 1) * 0.35
        idx = np.clip(np.round(v), 0, len(R_) - 1)
        return L._rgba(L.color_continuo(R_, idx)), None
    return B.Pintor(nombre, fn)


def craneo_salvaje(nombre, piel):
    """Cráneo del salvaje con franja de musgo a lo largo de la frente y coronilla."""
    oscuro = CRESTA_SALVAJE[1] * 0.75 + VERDE_SALVAJE[1] * 0.25
    claro = CRESTA_SALVAJE[2] * 0.7 + VERDE_SALVAJE[2] * 0.3

    def dib(tex, xs, ys, tw, th, c):
        if c in ('frente', 'arriba', 'atras'):
            cx = tw / 2.0
            izq = (xs >= cx - 2) & (xs < cx)
            der = (xs >= cx) & (xs < cx + 2)
            _pon(tex, izq, oscuro)
            _pon(tex, der, claro)
    return _sobre_piel_lancero(nombre, piel, dib, fino=True)


# ======================================================================================================================
#  Construcción de partes
# ======================================================================================================================
def cabeza_salvaje(m, Mt, piel):
    """Cabeza tótem apilada idéntica a la anatomía del lancero pero con los tonos y ojos del salvaje."""
    Mh = T(0, CABEZA_Y_LANCERO, CABEZA_Z_LANCERO) @ B.girar((CABEZA_GIRO_LANCERO, 0, 0))
    m.parte('cabeza', 'tronco', tuple(P(Mh, (0, 5.0, -9.0))))
    craneo = craneo_salvaje('craneo_salvaje', piel)

    caja_en(m, 'cabeza', Mh, (0, 11.2, -5.5), (13, 7.0, 11), piel,
            caras={'frente': craneo, 'arriba': craneo, 'atras': craneo})
    caja_en(m, 'cabeza', Mh, (0, 5.0, -7.0), (12, 5.0, 8.0), piel)

    for lado, ld in LADOS_LANCERO:
        ojo = ojo_caja_lancero(f'ojo_{ld}_salvaje', piel)
        caja_en(m, 'cabeza', Mh, (lado * 4.85, 10.45, -0.05), (4.5, 3.5, 2.5), ojo)

    caja_en(m, 'cabeza', Mh, (0, 6.2, 0.6), (12, 3.0, 6.0), hocico_lancero('hocico_salvaje', piel))

    boca = boca_lancero('boca_salvaje', R_=BOCA_SALVAJE)
    caja_en(m, 'cabeza', Mh, (0, 3.45, 0.9), (11, 2.5, 3.0), boca)
    caja_en(m, 'cabeza', Mh, (0, 3.45, 3.15), (11.4, 2.5, 0.6), dientes_lancero('dientes_salvaje'))

    gozne = P(Mh, (0, 4.37, -8.0))
    m.parte('mandibula', 'cabeza', tuple(gozne))
    Mj = T(*gozne) @ B.girar((CABEZA_GIRO_LANCERO + 10.0, 0, 0))
    suelo = boca_lancero('suelo_boca_salvaje', R_=BOCA_SALVAJE, base=0.7)
    caja_en(m, 'mandibula', Mj, (0, -1.115, 6.24), (12, 2.23, 12.48), mandibula_lancero('mandibula_salvaje', piel, suelo))
    return Mh


def cresta_salvaje(m, Mh, Mt):
    """Cresta de hojas musgosas a lo largo de la coronilla y crin de hojas a la espalda."""
    hojas = [hoja_lancero(f'hoja_salvaje_{k}', R_=CRESTA_SALVAJE, ancho=a, muesca=mu, lado=ld, base=b)
             for k, (a, mu, ld, b) in enumerate(((2, 0.4, 1, 0.6), (3, 0.5, -1, 0.9), (2, 0.55, -1, 1.1),
                                                 (3, 0.35, 1, 0.5)))]
    techo = 14.7
    for k, (z, x, alto, atras, giro) in enumerate(((-0.8, -0.5, 3.6, 18, -24), (-2.4, 0.4, 7.0, 14, 20),
                                                    (-4.0, -0.3, 5.8, 22, -14), (-5.8, 0.5, 5.2, 28, 18),
                                                    (-7.6, -0.4, 4.8, 34, -20), (-9.4, 0.3, 4.4, 42, 16))):
        p = P(Mh, (x, techo - 0.2, z))
        g = math.radians(giro)
        hoja_en_lancero(m, 'cabeza', p, dir_lancero(atras, 0), (math.sin(g), 0, math.cos(g)),
                        2.6 if k % 2 else 2.0, alto, hojas[k % len(hojas)])

    for k, (y, x, alto, atras, abre) in enumerate(((19.4, 0.0, 8.2, 40, 0), (18.8, 1.0, 8.6, 55, 50),
                                                    (18.8, -1.0, 8.6, 55, -50), (16.8, 1.5, 8.0, 75, 78),
                                                    (16.8, -1.5, 8.0, 75, -78), (15.8, 0.5, 9.2, 70, 15),
                                                    (14.2, 2.0, 8.2, 85, 62), (14.2, -2.0, 8.2, 85, -62),
                                                    (12.6, -0.5, 8.2, 80, -15), (11.0, 2.0, 7.2, 95, 72),
                                                    (11.0, -2.0, 7.2, 95, -72), (10.0, 0.0, 6.2, 90, 0))):
        p = P(Mt, (x, y, -5.0))
        d = dir_lancero(atras, abre)
        arriba = np.array((0.0, 1.0, 0.0)) - d[1] * d
        if np.linalg.norm(arriba) < 0.2:
            arriba = np.array((0.0, 0.0, 1.0))
        hoja_en_lancero(m, 'tronco', p, d, arriba, 3.0, alto, hojas[(k + 1) % len(hojas)])


def huesos_hombro_salvaje(m, parte, hombro, lado, hueso):
    """Los huesos en L de los hombros del Salvaje: emergen en la parte superior del hombro y bajan siguiendo la línea del brazo."""
    a = hombro + np.array((lado * 0.4, 2.4, 0.0))
    b = a + np.array((lado * 2.2, 1.6, 0.0))
    c = b + np.array((lado * 4.6, -2.2, 0.4))
    m.viga(parte, a, b, 2.8, hueso, extra=1.0)
    m.viga(parte, b, c, 2.4, hueso, extra=1.2)


def brazo_salvaje(m, lado, ld, hombro, codo_d, mano_d, piel_brazo, piel, brazalete, garra):
    """Brazo largo y poderoso con brazalete de hueso y tres garras en gancho hacia dentro."""
    n = m.parte(f'brazo_{ld}', 'tronco', tuple(hombro))
    codo = hombro + np.asarray(codo_d, float)
    muneca = codo + np.asarray(mano_d, float)
    m.viga(n, codo, hombro, 5.2, piel_brazo, extra=2.6)
    a = m.parte(f'antebrazo_{ld}', n, tuple(codo))
    m.viga(a, muneca, codo, 4.8, piel_brazo, extra=1.0)
    eje = B._u(muneca - codo)
    m.viga(a, muneca + eje * 0.2, muneca - eje * 3.0, 5.6, brazalete)
    puno = muneca + eje * 2.4
    m.viga(a, muneca + eje * 4.6, muneca + eje * 0.2, 5.0, piel, ancho=5.0)
    for k in (-1, 0, 1):
        raiz = muneca + eje * 4.4 + np.array((-lado * 1.2, 0, k * 1.5 + 0.6))
        hoja_en_lancero(m, a, raiz, -eje, (0, 0, 1), 2.5, 4.8, garra[0])
        hoja_en_lancero(m, a, raiz, -eje, (-lado, 0, 0), 2.5, 4.8, garra[1])
    return n, a, codo, muneca, puno


# ======================================================================================================================
#  Modelo
# ======================================================================================================================
def construir():
    """Construye el Reptisaurio Salvaje a tamaño base 1.0 (TAM = 1.0)."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    m.parte('cuerpo', None, (0, Y_CADERA_LANCERO, 0))

    piel = piel_salvaje('piel_salvaje', VERDE_SALVAJE, base=2.1, luz=0.7)
    piel_miembro = piel_salvaje('piel_miembro_salvaje', VERDE_SALVAJE, base=2.1, luz=0.7, bandas=4, semilla=3)
    garra_pie = garra_lancero('garra_pie_salvaje', R_=HUESO_SALVAJE, gancho=1, ancho=2)

    piernas_lancero(m, piel, piel_miembro, garra_pie)
    Mt, hombros = tronco_lancero(m, piel)
    Mh = cabeza_salvaje(m, Mt, piel)
    cresta_salvaje(m, Mh, Mt)

    hueso_spur = hueso_lancero('hueso_spur_salvaje', R_=HUESO_SALVAJE, base=3.0)
    brazalete = hueso_lancero('brazalete_salvaje', R_=HUESO_SALVAJE, base=3.0, rayas='ccggcc', fino=True)
    garras = (
        garra_lancero('garra_mano_salvaje', R_=HUESO_SALVAJE, gancho=1, ancho=3),
        garra_lancero('garra_mano_b_salvaje', R_=HUESO_SALVAJE, gancho=-1, ancho=3),
    )

    for lado, ld, hombro in hombros:
        # En reposo y andar neutral, ambos brazos caen a los costados naturalmente
        d1 = (lado * 2.0, -14.0, 0.6)
        d2 = (-lado * 1.5, -13.6, 0.8)
        n, a, codo, muneca, puno = brazo_salvaje(m, lado, ld, hombro, d1, d2, piel_miembro, piel, brazalete, garras)
        huesos_hombro_salvaje(m, n, hombro, lado, hueso_spur)

    m.mirar(('cabeza', 0.8))
    anims_salvaje(m)
    return m


# ======================================================================================================================
#  Animaciones
# ======================================================================================================================
# Guardia feral salvaje: brazos arqueados hacia afuera con las garras apuntando hacia la presa
GUARDIA_SALVAJE = {
    'brazo_d': (-52.0, -22.0, -26.0),
    'antebrazo_d': (-58.0, 16.0, 6.0),
    'brazo_i': (-52.0, 22.0, 26.0),
    'antebrazo_i': (-58.0, -16.0, -6.0),
}


def anims_salvaje(m):
    """Animaciones del salvaje:
    reposo: postura baja encorvada de bestia simiesca, brazos muy bajos tocando el suelo, respiracion salvaje profunda.
    alerta: guardia amenazante arqueando el lomo y abriendo garras hacia afuera.
    andar: marcha pesada semicuadrupeda con hombros bamboleantes.
    correr: galope primitivo agresivo a ras de suelo.
    ataque: zarpazo cruzado salvaje desgarrando primero con derecha y luego con izquierda.
    especial: rugido feral alzando garras al cielo.
    especial2: salto brutal y azote de garras doble aplastando el suelo.
    """
    G = GUARDIA_SALVAJE
    # Reposo salvaje: cuerpo agazapado, torso inclinado hacia adelante, brazos rozando el suelo
    r = m.anim('reposo', 3.6, bucle=True)
    r.rot('tronco', [(0, 12, 0, 0), (1.8, 15, 0, 0), (3.6, 12, 0, 0)])
    r.mov('tronco', [(0, 0, -1.0, 0.4), (1.8, 0, -1.5, 0.6), (3.6, 0, -1.0, 0.4)])
    # Patas flexionadas en cuclillas de bestia
    for k, (lado, ld) in enumerate(LADOS_LANCERO):
        r.rot(f'pierna_{ld}', [(0, 10, 0, 0), (1.8, 12, 0, 0), (3.6, 10, 0, 0)])
        r.rot(f'espinilla_{ld}', [(0, -14, 0, 0), (1.8, -16, 0, 0), (3.6, -14, 0, 0)])
        # Brazos colgando muy bajos y abiertos
        r.rot(f'brazo_{ld}', [(0, 8, 0, lado * 6), (1.8, 12, 0, lado * 7), (3.6, 8, 0, lado * 6)])
        r.rot(f'antebrazo_{ld}', [(0, -12, 0, -lado * 4), (1.8, -15, 0, -lado * 4), (3.6, -12, 0, -lado * 4)])
    # Movimientos bruscos de cabeza de depredador olfateando
    r.rot('cabeza', [(0, -6, 0, 0), (0.6, -4, 18, 0), (1.2, -8, 20, 0), (1.8, -6, 0, 0),
                     (2.4, -4, -18, 0), (3.0, -8, -20, 0), (3.6, -6, 0, 0)])
    r.rot('mandibula', [(0, 4, 0, 0), (1.8, 12, 0, 0), (3.6, 4, 0, 0)])

    # Alerta: amenaza feral alzando las zarpas con garfas abiertas
    al = m.anim('alerta', 1.8, bucle=True)
    al.rot('tronco', [(0, 4, 0, 0), (0.9, 8, 0, 0), (1.8, 4, 0, 0)])
    al.rot('mandibula', [(0, 14, 0, 0), (0.9, 20, 0, 0), (1.8, 14, 0, 0)])
    for parte, (rx, ry, rz) in G.items():
        al.rot(parte, [(0.0, rx, ry, rz), (0.9, rx - 4.0, ry, rz + 3.0), (1.8, rx, ry, rz)])

    s_ = m.anim('siempre', 2.0, bucle=True)
    s_.onda('mandibula', 'r', 0, 4.0, periodo=2.0)

    # Andar semicuadrúpedo y correr
    for nombre, largo, amp, inclina in (('andar', 1.2, 1.0, 8.0), ('correr', 0.70, 1.4, 16.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS_LANCERO):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 26 * amp, periodo=largo, fase=f)
            a.onda(f'espinilla_{ld}', 'r', 0, 26 * amp, periodo=largo, fase=f - 0.25, forma=lambda v: max(0.0, v))
        if nombre == 'andar':
            a.onda('brazo_i', 'r', 0, 18 * amp, periodo=largo, fase=0.0)
            a.onda('antebrazo_i', 'r', 0, 12 * amp, periodo=largo, fase=0.25, base=-10 * amp)
            a.onda('brazo_d', 'r', 0, 18 * amp, periodo=largo, fase=0.5)
            a.onda('antebrazo_d', 'r', 0, 12 * amp, periodo=largo, fase=0.75, base=-10 * amp)
        else:
            a.onda('brazo_i', 'r', 0, 10.0, periodo=largo, fase=0.0)
            a.onda('brazo_d', 'r', 0, 10.0, periodo=largo, fase=0.5)
        # Gran bamboleo de hombros de gorila salvaje
        a.onda('tronco', 'r', 2, 4.5 * amp, periodo=largo)
        a.onda('tronco', 'r', 1, 5.0 * amp, periodo=largo, fase=0.25)
        a.onda('tronco', 'r', 0, 2.5 * amp, periodo=largo / 2, base=inclina)
        a.onda('tronco', 'm', 1, 0.6 * amp, periodo=largo / 2)
        a.onda('cabeza', 'r', 0, 3.0 * amp, periodo=largo / 2, fase=0.25, base=-inclina * 0.7)

    # Ataque: zarpazo doble cruzado con desgarre
    at = m.anim('ataque', 0.65)
    at.mov('cuerpo', [(0, 0, 0, 0), (0.15, 0, 0.4, -1.2), (0.32, 0, -0.6, 3.2), (0.48, 0, -0.3, 1.8), (0.65, 0, 0, 0)])
    at.rot('tronco', [(0, 0, 0, 0), (0.15, -10, -26, 0), (0.32, 20, 28, 0), (0.48, 10, -18, 0), (0.65, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.15, 8, 20, 0), (0.32, -14, -22, 0), (0.65, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.15, 12, 0, 0), (0.32, 28, 0, 0), (0.50, 10, 0, 0), (0.65, 0, 0, 0)])
    # Brazo derecho lanza zarpazo horizontal furioso
    at.rot('brazo_d', [(0, *G['brazo_d']), (0.15, -25, -35, -45), (0.32, -92, 20, 15), (0.48, -60, 5, -5), (0.65, *G['brazo_d'])])
    at.rot('antebrazo_d', [(0, *G['antebrazo_d']), (0.15, -85, 15, 0), (0.32, -15, 0, 0), (0.65, *G['antebrazo_d'])])
    # Brazo izquierdo entra inmediatamente en contragolpe
    at.rot('brazo_i', [(0, *G['brazo_i']), (0.15, -70, 15, 25), (0.32, -35, -10, 15), (0.48, -90, -22, -15), (0.65, *G['brazo_i'])])
    at.rot('antebrazo_i', [(0, *G['antebrazo_i']), (0.15, -35, 0, 0), (0.32, -80, 0, 0), (0.48, -15, 0, 0), (0.65, *G['antebrazo_i'])])

    # Especial: rugido al cielo sacudiendo el lomo
    e = m.anim('especial', 0.90)
    e.rot('tronco', [(0, 0, 0, 0), (0.30, -18, 0, 0), (0.65, -12, 0, 0), (0.90, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.30, -32, 0, 0), (0.65, -24, 0, 0), (0.90, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.25, 34, 0, 0), (0.70, 30, 0, 0), (0.90, 0, 0, 0)])
    e.rot('brazo_d', [(0, 0, 0, 0), (0.32, -75, -20, -40), (0.70, -60, -15, -30), (0.90, *G['brazo_d'])])
    e.rot('antebrazo_d', [(0, 0, 0, 0), (0.32, -60, 0, 0), (0.70, -50, 0, 0), (0.90, *G['antebrazo_d'])])
    e.rot('brazo_i', [(0, 0, 0, 0), (0.32, -75, 20, 40), (0.70, -60, 15, 30), (0.90, *G['brazo_i'])])
    e.rot('antebrazo_i', [(0, 0, 0, 0), (0.32, -60, 0, 0), (0.70, -50, 0, 0), (0.90, *G['antebrazo_i'])])

    # Especial2: salto alto y azote de garras doble al suelo
    e2 = m.anim('especial2', 0.95)
    e2.mov('cuerpo', [(0, 0, 0, 0), (0.28, 0, 3.2, -1.2), (0.52, 0, -2.0, 4.4), (0.72, 0, -1.0, 2.4), (0.95, 0, 0, 0)])
    e2.rot('tronco', [(0, 0, 0, 0), (0.28, -24, 0, 0), (0.52, 28, 0, 0), (0.72, 16, 0, 0), (0.95, 0, 0, 0)])
    e2.rot('cabeza', [(0, 0, 0, 0), (0.28, -18, 0, 0), (0.52, 16, 0, 0), (0.95, 0, 0, 0)])
    e2.rot('mandibula', [(0, 0, 0, 0), (0.28, 30, 0, 0), (0.52, 18, 0, 0), (0.95, 0, 0, 0)])
    e2.rot('brazo_d', [(0, *G['brazo_d']), (0.28, -110, -15, -15), (0.52, -45, 8, 8), (0.95, *G['brazo_d'])])
    e2.rot('antebrazo_d', [(0, *G['antebrazo_d']), (0.28, -75, 0, 0), (0.52, -10, 0, 0), (0.95, *G['antebrazo_d'])])
    e2.rot('brazo_i', [(0, *G['brazo_i']), (0.28, -110, 15, 15), (0.52, -45, -8, -8), (0.95, *G['brazo_i'])])
    e2.rot('antebrazo_i', [(0, *G['antebrazo_i']), (0.28, -75, 0, 0), (0.52, -10, 0, 0), (0.95, *G['antebrazo_i'])])

    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 6, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, -15, 0, 0), (1.0, 10, 0, 0)])

    ap = m.anim('aparece', 1.2)
    ap.mov('cuerpo', [(0, 0, -8, 0), (0.6, 0, -2, 0), (1.2, 0, 0, 0)])
    ap.rot('tronco', [(0, 30, 0, 0), (0.6, 20, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('cabeza', [(0, 20, 0, 0), (0.8, -12, 0, 0), (1.2, 0, 0, 0)])

