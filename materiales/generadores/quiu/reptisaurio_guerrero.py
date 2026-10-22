"""
El Reptisaurio Guerrero (DEDsafío 2, cartel del día 2; libro del juego: «El reptisaurio de los asentamientos: pardo,
con llamas naranjas en la cabeza, calaveras de vaca en los hombros y un cuchillo de hueso. Ataca cuerpo a cuerpo y
su golpe te deja Veneno Primitivo (veneno II, ocho segundos)»).

Rehecho con la misma anatomía realista, cabeza tótem y animaciones de alta calidad que el Reptisaurio con Lanza:
  - Piel parda reptiliana y cresta de llamas ardientes anaranjadas en el cráneo y la espalda.
  - Calaveras de vaca con cuernos curvos sentadas en cada hombro.
  - Bandolera diagonal y taparrabos con rayas amarillas y negras, ceñido con cinturón verde y hojas colgantes.
  - Gran cuchillo/machete de hueso sostenido en la mano derecha.
  - Modo neutral: brazos abajo y cuchillo relajado a su costado al reposar y andar; al detectar amenaza alza el
    cuchillo en guardia de combate y corre agresivamente.
  - Animaciones: tajo diagonal con el cuchillo de hueso, rugido de desafío alzando el arma y salto con estocada/tajo.
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

ID = 'reptisaurio_guerrero'
TAM = 1.0

# ======================================================================================================================
#  Paleta y colores
# ======================================================================================================================
PARDO_GUERRERO = rampa('1c0e06', '381c0e', '5c3018', '844824', 'b06434')
VIENTRE_GUERRERO = rampa('28180a', '482e14', '704c22', '9c6e32', 'c89448')
LLAMA_GUERRERO = rampa('4a1204', '7c2006', 'b4360a', 'e45c12', 'f88e22')
HUESO_GUERRERO = rampa('5c564a', '7a7364', '9c9482', 'bcb4a0', 'ded6c2')
GRIS_CALAVERA = rampa('3a3834', '524f4a', '6a6660', '7f7b74', '948f87')
FAJA_AMARILLA = rampa('6e600e', 'a49a16', 'cec424', 'e6dc30', 'f6ee70')
CINTO_VERDE = rampa('0e2e0c', '194612', '1e6a20', '28902e', '44b448')
BOCA_GUERRERO = rampa('1c0006', '2e020a', '420410', '580a18', '701422')
NEGRO_GUERRERO = H('050403')

HUEVO = (
    ('844824', '5c3018', '1c0e06'),
    ('e45c12', '7c2006'),
    [
        ((5, 6), 'd4c440'), ((6, 6), '050403'), ((9, 6), 'd4c440'), ((10, 6), '050403'),
        ((7, 2), 'f88e22'), ((8, 3), 'e45c12'), ((6, 9), '420410'), ((9, 9), '420410'),
        ((4, 4), 'ded6c2'), ((11, 4), 'ded6c2'), ((7, 10), 'e6dc30'),
    ],
)


# ======================================================================================================================
#  Pintores
# ======================================================================================================================
def piel_guerrero(nombre, R_=PARDO_GUERRERO, base=2.1, luz=0.7, bandas=0, semilla=0):
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


def craneo_guerrero(nombre, piel):
    oscuro = LLAMA_GUERRERO[1] * 0.75 + PARDO_GUERRERO[1] * 0.25
    claro = LLAMA_GUERRERO[2] * 0.7 + PARDO_GUERRERO[2] * 0.3

    def dib(tex, xs, ys, tw, th, c):
        if c in ('frente', 'arriba', 'atras'):
            cx = tw / 2.0
            izq = (xs >= cx - 2) & (xs < cx)
            der = (xs >= cx) & (xs < cx + 2)
            _pon(tex, izq, oscuro)
            _pon(tex, der, claro)
    return _sobre_piel_lancero(nombre, piel, dib, fino=True)


def rayas_diag(nombre, R1=PARDO_GUERRERO, R2=FAJA_AMARILLA, ancho=2, paso=5, base=2.4):
    """Tela a rayas diagonales amarillas y pardas oscuras."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s + 3)
        v = base + 0.5 * (0.5 - (ys + 0.5) / th) + np.where(a < 0.1, -1.0, np.where(a > 0.9, 1.0, 0.0)) * 0.6
        if c == 'arriba':
            v = v + 0.5
        elif c == 'abajo':
            v = v - 0.6
        raya = ((xs + ys) % paso) < ancho
        idx = np.clip(np.round(v), 0, 4)
        rgb = np.where(raya[..., None], L.color_continuo(R2, np.clip(idx + 1, 2, 4)),
                       L.color_continuo(R1, np.clip(idx - 1, 0, 2)))
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Construcción
# ======================================================================================================================
def cabeza_guerrero(m, Mt, piel):
    Mh = T(0, CABEZA_Y_LANCERO, CABEZA_Z_LANCERO) @ B.girar((CABEZA_GIRO_LANCERO, 0, 0))
    m.parte('cabeza', 'tronco', tuple(P(Mh, (0, 5.0, -9.0))))
    craneo = craneo_guerrero('craneo_guerrero', piel)

    caja_en(m, 'cabeza', Mh, (0, 11.2, -5.5), (13, 7.0, 11), piel,
            caras={'frente': craneo, 'arriba': craneo, 'atras': craneo})
    caja_en(m, 'cabeza', Mh, (0, 5.0, -7.0), (12, 5.0, 8.0), piel)

    for lado, ld in LADOS_LANCERO:
        ojo = ojo_caja_lancero(f'ojo_{ld}_guerrero', piel)
        caja_en(m, 'cabeza', Mh, (lado * 4.85, 10.45, -0.05), (4.5, 3.5, 2.5), ojo)

    caja_en(m, 'cabeza', Mh, (0, 6.2, 0.6), (12, 3.0, 6.0), hocico_lancero('hocico_guerrero', piel))

    boca = boca_lancero('boca_guerrero', R_=BOCA_GUERRERO)
    caja_en(m, 'cabeza', Mh, (0, 3.45, 0.9), (11, 2.5, 3.0), boca)
    caja_en(m, 'cabeza', Mh, (0, 3.45, 3.15), (11.4, 2.5, 0.6), dientes_lancero('dientes_guerrero'))

    gozne = P(Mh, (0, 4.37, -8.0))
    m.parte('mandibula', 'cabeza', tuple(gozne))
    Mj = T(*gozne) @ B.girar((CABEZA_GIRO_LANCERO + 10.0, 0, 0))
    suelo = boca_lancero('suelo_boca_guerrero', R_=BOCA_GUERRERO, base=0.7)
    caja_en(m, 'mandibula', Mj, (0, -1.115, 6.24), (12, 2.23, 12.48), mandibula_lancero('mandibula_guerrero', piel, suelo))
    return Mh


def cresta_guerrero(m, Mh, Mt):
    """Llamas flamígeras en lo alto de la cabeza y a lo largo de la espalda."""
    hojas = [hoja_lancero(f'hoja_guerrero_{k}', R_=LLAMA_GUERRERO, ancho=a, muesca=mu, lado=ld, base=b)
             for k, (a, mu, ld, b) in enumerate(((2, 0.4, 1, 0.6), (3, 0.5, -1, 0.9), (2, 0.55, -1, 1.1),
                                                 (3, 0.35, 1, 0.5)))]
    techo = 14.7
    for k, (z, x, alto, atras, giro) in enumerate(((-0.8, -0.5, 3.8, 18, -24), (-2.4, 0.4, 7.2, 14, 20),
                                                    (-4.0, -0.3, 6.0, 22, -14), (-5.8, 0.5, 5.4, 28, 18),
                                                    (-7.6, -0.4, 5.0, 34, -20), (-9.4, 0.3, 4.6, 42, 16))):
        p = P(Mh, (x, techo - 0.2, z))
        g = math.radians(giro)
        hoja_en_lancero(m, 'cabeza', p, dir_lancero(atras, 0), (math.sin(g), 0, math.cos(g)),
                        2.6 if k % 2 else 2.0, alto, hojas[k % len(hojas)])

    for k, (y, x, alto, atras, abre) in enumerate(((19.4, 0.0, 8.4, 40, 0), (18.8, 1.0, 8.8, 55, 50),
                                                    (18.8, -1.0, 8.8, 55, -50), (16.8, 1.5, 8.2, 75, 78),
                                                    (16.8, -1.5, 8.2, 75, -78), (15.8, 0.5, 9.4, 70, 15),
                                                    (14.2, 2.0, 8.4, 85, 62), (14.2, -2.0, 8.4, 85, -62),
                                                    (12.6, -0.5, 8.4, 80, -15), (11.0, 2.0, 7.4, 95, 72),
                                                    (11.0, -2.0, 7.4, 95, -72), (10.0, 0.0, 6.4, 90, 0))):
        p = P(Mt, (x, y, -5.0))
        d = dir_lancero(atras, abre)
        arriba = np.array((0.0, 1.0, 0.0)) - d[1] * d
        if np.linalg.norm(arriba) < 0.2:
            arriba = np.array((0.0, 0.0, 1.0))
        hoja_en_lancero(m, 'tronco', p, d, arriba, 3.0, alto, hojas[(k + 1) % len(hojas)])


def calavera_vaca_hombro(m, parte, hombro, lado, hueso):
    """Calavera de vaca detallada con cuernos curvos sobre el hombro."""
    base = hombro + np.array((lado * 0.8, 2.4, 0.0))
    S = T(*base) @ B.girar((0, lado * 30, 0))
    # Cráneo y hocico
    caja_en(m, parte, S, (0, 1.6, 0.0), (5.2, 4.4, 5.0), hueso)
    caja_en(m, parte, S, (0, 0.6, 3.6), (3.6, 3.0, 3.2), hueso)
    # Cuernos que doblan hacia afuera y arriba
    for s_ in (1, -1):
        a = P(S, (s_ * 2.2, 2.8, 0.4))
        b = P(S, (s_ * 4.6, 2.6, 0.2))
        c2 = P(S, (s_ * 5.4, 4.8, 0.8))
        d = P(S, (s_ * 4.8, 6.2, 1.4))
        m.viga(parte, a, b, 2.0, hueso, extra=0.8)
        m.viga(parte, b, c2, 1.6, hueso, extra=0.6)
        m.viga(parte, c2, d, 1.2, hueso, extra=0.4)


def equipo_guerrero(m, Mt):
    """Bandolera diagonal, cinturón verde con hojas y taparrabos rayado."""
    rayas = rayas_diag('rayas_guerrero')
    cinto = hueso_lancero('cinto_guerrero', R_=CINTO_VERDE, base=2.2)

    # Cinturón
    caja_en(m, 'tronco', Mt, (0, 1.4, 0.0), (13.0, 2.0, 9.8), cinto)

    # Bandolera cruzando el pecho
    a = np.array((-5.4, 18.2, 5.5))
    b = np.array((4.8, 2.8, 5.1))
    m.viga('tronco', P(Mt, b), P(Mt, a), 0.6, rayas, ancho=2.4, extra=0.6)
    m.viga('tronco', P(Mt, (a[0], 19.4, -3.8)), P(Mt, (a[0], 19.4, 3.8)), 0.6, rayas, ancho=2.4)
    m.viga('tronco', P(Mt, (b[0], 2.8, -4.8)), P(Mt, (a[0], 18.2, -5.5)), 0.6, rayas, ancho=2.4, extra=0.6)

    # Faldón rayado
    for z, nombre in ((5.0, 'del'), (-5.0, 'tras')):
        n = m.parte(f'faldon_{nombre}', 'tronco', tuple(P(Mt, (0, 0.8, z))))
        Mf = T(*P(Mt, (0, 1.0, z))) @ B.girar((ENCORVADO_LANCERO * 0.3, 0 if z > 0 else 180, 0))
        lamina(m, n, Mf, 8.4, 8.0, rayas, abajo=True)


def cuchillo_hueso(m, padre, puno):
    """Machete/cuchillo de hueso sostenido firmemente en la mano derecha."""
    n = m.parte('cuchillo', padre, tuple(puno))
    hueso = hueso_lancero('hueso_cuchillo', R_=HUESO_GUERRERO, base=3.2)
    mango = hueso_lancero('mango_cuchillo', R_=PARDO_GUERRERO, base=1.6)

    # Mango empuñado
    m.viga(n, puno + np.array((0, 2.2, -0.6)), puno - np.array((0, 2.0, -0.6)), 1.8, mango)

    # Hoja grande de hueso dentada hacia adelante
    p0 = puno + np.array((0, 1.8, -0.6))
    p1 = p0 + np.array((0, 10.5, 3.2))
    m.viga(n, p0, p1, 1.2, hueso, ancho=3.4, extra=0.8)
    # Punta afilada
    p2 = p1 + np.array((0, 3.0, -1.0))
    m.viga(n, p1, p2, 1.2, hueso, ancho=2.2, extra=0.6)
    return n


def brazo_guerrero(m, lado, ld, hombro, codo_d, mano_d, piel_brazo, piel, brazalete, garra):
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
    """Construye el Reptisaurio Guerrero a tamaño base 1.0 (TAM = 1.0)."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0
    m.parte('cuerpo', None, (0, Y_CADERA_LANCERO, 0))

    piel = piel_guerrero('piel_guerrero', PARDO_GUERRERO, base=2.1, luz=0.7)
    piel_miembro = piel_guerrero('piel_miembro_guerrero', PARDO_GUERRERO, base=2.1, luz=0.7, bandas=4, semilla=3)
    garra_pie = garra_lancero('garra_pie_guerrero', R_=HUESO_GUERRERO, gancho=1, ancho=2)

    piernas_lancero(m, piel, piel_miembro, garra_pie)
    Mt, hombros = tronco_lancero(m, piel)
    Mh = cabeza_guerrero(m, Mt, piel)
    cresta_guerrero(m, Mh, Mt)
    equipo_guerrero(m, Mt)

    calavera_mat = hueso_lancero('calavera_vaca_mat', R_=GRIS_CALAVERA, base=2.6)
    brazalete = hueso_lancero('brazalete_guerrero', R_=HUESO_GUERRERO, base=3.0, rayas='ccggcc', fino=True)
    garras = (
        garra_lancero('garra_mano_guerrero', R_=HUESO_GUERRERO, gancho=1, ancho=3),
        garra_lancero('garra_mano_b_guerrero', R_=HUESO_GUERRERO, gancho=-1, ancho=3),
    )

    for lado, ld, hombro in hombros:
        # En reposo y andar neutral, ambos brazos caen a los costados naturalmente; la mano derecha lleva el cuchillo
        d1 = (lado * 2.0, -14.0, 0.6)
        d2 = (-lado * 1.5, -13.6, 0.8)
        n, a, codo, muneca, puno = brazo_guerrero(m, lado, ld, hombro, d1, d2, piel_miembro, piel, brazalete, garras)
        if lado < 0:
            cuchillo_hueso(m, a, puno)
        calavera_vaca_hombro(m, n, hombro, lado, calavera_mat)

    m.mirar(('cabeza', 0.8))
    anims_guerrero(m)
    return m


# ======================================================================================================================
#  Animaciones
# ======================================================================================================================
# Guardia marcial de duelista tribal: cuchillo alzado a la altura del pecho/cuello con el filo hacia adelante
GUARDIA_GUERRERO = {
    'brazo_d': (-62.0, -18.0, -10.0),
    'antebrazo_d': (-65.0, 16.0, 0.0),
    'cuchillo': (40.0, 0.0, -10.0),
    'brazo_i': (-38.0, 12.0, 22.0),
    'antebrazo_i': (-45.0, -12.0, 0.0),
}


def anims_guerrero(m):
    """Animaciones del guerrero:
    reposo: postura marcial erguida y orgullosa; mano izquierda en el cinto, mano derecha sosteniendo el machete descansando en la cadera.
    alerta: guardia de duelo con cuchillo alzado protegiendo el pecho y hombro izquierdo en punta.
    andar: marcha militar medida y disciplinada con el machete firme.
    correr: embestida de asalto con el cuchillo listo para ensartar.
    ataque: ejecucion de tajo descendente con el machete seguido de corte de revés horizontal.
    especial: rugido de desafío alzando el machete ensangrentado al cielo.
    especial2: estocada gladiatoria profunda combinada con embestida de hombro con calavera de cuernos.
    """
    G = GUARDIA_GUERRERO
    # Reposo marcial: torso erguido, respiración acompasada, pose de centinela
    r = m.anim('reposo', 4.2, bucle=True)
    r.rot('tronco', [(0, -3, 0, 0), (2.1, -1, 0, 0), (4.2, -3, 0, 0)])
    r.mov('tronco', [(0, 0, 0.2, 0), (2.1, 0, 0.5, 0), (4.2, 0, 0.2, 0)])
    # Mano izquierda apoyada en el cinto / cadera
    r.rot('brazo_i', [(0, -14, 6, 16), (2.1, -12, 6, 16), (4.2, -14, 6, 16)])
    r.rot('antebrazo_i', [(0, -38, -10, 0), (2.1, -34, -10, 0), (4.2, -38, -10, 0)])
    # Mano derecha con cuchillo descansando en la pierna / faja
    r.rot('brazo_d', [(0, -12, -8, -10), (2.1, -10, -8, -10), (4.2, -12, -8, -10)])
    r.rot('antebrazo_d', [(0, -32, 10, 0), (2.1, -28, 10, 0), (4.2, -32, 10, 0)])
    r.rot('cuchillo', [(0, 15, 0, 0), (2.1, 12, 0, 0), (4.2, 15, 0, 0)])
    # Cabeza erguida y mirada de guardia
    r.rot('cabeza', [(0, 0, 0, 0), (1.0, -2, 15, 0), (2.1, 0, 0, 0), (3.1, -2, -15, 0), (4.2, 0, 0, 0)])

    # Alerta: adopta guardia marcial de combate levantando el machete
    al = m.anim('alerta', 1.8, bucle=True)
    al.rot('tronco', [(0, 2, -6, 0), (0.9, 4, -4, 0), (1.8, 2, -6, 0)])
    for parte, (rx, ry, rz) in G.items():
        al.rot(parte, [(0.0, rx, ry, rz), (0.9, rx - 3.0, ry, rz), (1.8, rx, ry, rz)])

    s_ = m.anim('siempre', 2.4, bucle=True)
    s_.onda('mandibula', 'r', 0, 2.5, periodo=2.4)

    # Andar marcial y correr
    for nombre, largo, amp, inclina in (('andar', 1.25, 1.0, 0.0), ('correr', 0.72, 1.35, 12.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS_LANCERO):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f)
            a.onda(f'espinilla_{ld}', 'r', 0, 24 * amp, periodo=largo, fase=f - 0.25, forma=lambda v: max(0.0, v))
        a.onda('brazo_i', 'r', 0, 14 * amp, periodo=largo, fase=0.0)
        a.onda('antebrazo_i', 'r', 0, 8 * amp, periodo=largo, fase=0.25, base=-8 * amp)
        if nombre == 'andar':
            # Al andar sostiene el cuchillo en la mano derecha con paso firme
            a.onda('brazo_d', 'r', 0, 10 * amp, periodo=largo, fase=0.5, base=-8 * amp)
            a.onda('antebrazo_d', 'r', 0, 6 * amp, periodo=largo, fase=0.75, base=-25 * amp)
            a.onda('cuchillo', 'r', 0, 5 * amp, periodo=largo, base=18 * amp)
        else:
            a.onda('brazo_d', 'r', 0, 5.0, periodo=largo, fase=0.5)
        a.onda('faldon_del', 'r', 0, 8 * amp, periodo=largo / 2, fase=0.25, base=-4 * amp)
        a.onda('faldon_tras', 'r', 0, 6 * amp, periodo=largo / 2, fase=0.75, base=4 * amp)
        a.onda('tronco', 'r', 2, 2.0 * amp, periodo=largo)
        a.onda('tronco', 'r', 1, 3.0 * amp, periodo=largo, fase=0.25)
        a.onda('tronco', 'r', 0, 1.2 * amp, periodo=largo / 2, base=inclina)
        a.onda('tronco', 'm', 1, 0.35 * amp, periodo=largo / 2)
        a.onda('cabeza', 'r', 0, 2.0 * amp, periodo=largo / 2, fase=0.25, base=-inclina * 0.5)

    # Ataque: combo de duelista: tajo descendente de hueso + estocada de revés
    at = m.anim('ataque', 0.68)
    at.mov('cuerpo', [(0, 0, 0, 0), (0.16, 0, 0.2, -1.0), (0.34, 0, -0.6, 3.0), (0.50, 0, -0.3, 1.5), (0.68, 0, 0, 0)])
    at.rot('tronco', [(0, 0, 0, 0), (0.16, -8, -20, 0), (0.34, 18, 24, 0), (0.50, 6, -10, 0), (0.68, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.16, 6, 16, 0), (0.34, -12, -16, 0), (0.68, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.16, 8, 0, 0), (0.34, 20, 0, 0), (0.50, 6, 0, 0), (0.68, 0, 0, 0)])
    # Brazo derecho: golpe de tajo descendente
    at.rot('brazo_d', [(0, *G['brazo_d']), (0.16, -15, -25, -25), (0.34, -98, 22, -8), (0.50, -70, 10, -5), (0.68, *G['brazo_d'])])
    at.rot('antebrazo_d', [(0, *G['antebrazo_d']), (0.16, -85, 12, 0), (0.34, -10, 0, 0), (0.68, *G['antebrazo_d'])])
    at.rot('cuchillo', [(0, *G['cuchillo']), (0.16, -10, 0, 0), (0.34, 60, 0, 0), (0.68, *G['cuchillo'])])
    # Brazo izquierdo cubre guardia
    at.rot('brazo_i', [(0, *G['brazo_i']), (0.16, -45, 0, 25), (0.34, 15, 0, 18), (0.68, *G['brazo_i'])])
    at.rot('antebrazo_i', [(0, *G['antebrazo_i']), (0.16, -38, 0, 0), (0.34, -12, 0, 0), (0.68, *G['antebrazo_i'])])

    # Especial: rugido marcial alzando el machete en alto
    e = m.anim('especial', 0.88)
    e.rot('tronco', [(0, 0, 0, 0), (0.30, -12, -10, 0), (0.60, -8, -6, 0), (0.88, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.30, -22, 8, 0), (0.60, -14, -4, 0), (0.88, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.26, 26, 0, 0), (0.64, 20, 0, 0), (0.88, 0, 0, 0)])
    e.rot('brazo_d', [(0, 0, 0, 0), (0.32, -90, -14, -22), (0.64, -68, -10, -18), (0.88, *G['brazo_d'])])
    e.rot('antebrazo_d', [(0, 0, 0, 0), (0.32, -25, 10, 0), (0.64, -45, 10, 0), (0.88, *G['antebrazo_d'])])
    e.rot('cuchillo', [(0, 0, 0, 0), (0.32, 65, 0, 0), (0.64, 45, 0, 0), (0.88, *G['cuchillo'])])
    e.rot('brazo_i', [(0, 0, 0, 0), (0.32, -32, 0, 24), (0.88, *G['brazo_i'])])
    e.rot('antebrazo_i', [(0, 0, 0, 0), (0.32, -34, 0, 0), (0.88, *G['antebrazo_i'])])

    # Especial2: estocada gladiatoria profunda con choque de hombro con calavera
    e2 = m.anim('especial2', 0.88)
    e2.mov('cuerpo', [(0, 0, 0, 0), (0.24, 0, 2.0, -1.5), (0.46, 0, -1.0, 4.0), (0.65, 0, -0.4, 2.0), (0.88, 0, 0, 0)])
    e2.rot('tronco', [(0, 0, 0, 0), (0.24, -16, -24, 0), (0.46, 22, 22, 0), (0.65, 12, 10, 0), (0.88, 0, 0, 0)])
    e2.rot('cabeza', [(0, 0, 0, 0), (0.24, -12, 16, 0), (0.46, 14, -14, 0), (0.88, 0, 0, 0)])
    e2.rot('mandibula', [(0, 0, 0, 0), (0.24, 24, 0, 0), (0.46, 16, 0, 0), (0.88, 0, 0, 0)])
    # Estocada directa al frente con el cuchillo
    e2.rot('brazo_d', [(0, *G['brazo_d']), (0.24, -105, -20, -22), (0.46, -50, 15, -8), (0.88, *G['brazo_d'])])
    e2.rot('antebrazo_d', [(0, *G['antebrazo_d']), (0.24, -40, 0, 0), (0.46, -5, 0, 0), (0.88, *G['antebrazo_d'])])
    e2.rot('cuchillo', [(0, *G['cuchillo']), (0.24, 75, 0, 0), (0.46, 25, 0, 0), (0.88, *G['cuchillo'])])
    # Hombro izquierdo cargado hacia adelante para embestir con los cuernos
    e2.rot('brazo_i', [(0, *G['brazo_i']), (0.24, -45, 0, 25), (0.46, 28, 0, 16), (0.88, *G['brazo_i'])])
    e2.rot('antebrazo_i', [(0, *G['antebrazo_i']), (0.24, -35, 0, 0), (0.46, -10, 0, 0), (0.88, *G['antebrazo_i'])])

    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 6, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, -15, 0, 0), (1.0, 10, 0, 0)])

    ap = m.anim('aparece', 1.2)
    ap.mov('cuerpo', [(0, 0, -8, 0), (0.6, 0, -2, 0), (1.2, 0, 0, 0)])
    ap.rot('tronco', [(0, 30, 0, 0), (0.6, 20, 0, 0), (1.2, 0, 0, 0)])
    ap.rot('cabeza', [(0, 20, 0, 0), (0.8, -12, 0, 0), (1.2, 0, 0, 0)])

