"""
Bocetos B y C de la Mariposa del Vendaval (jefe elemental del aire), a partir
de las imagenes que trajo el usuario.

  B  DRAGON MARIPOSA  Un dragon de escamas negro azuladas con grietas de rayo
                      cian, un racimo de ojos-gema en la cabeza, cuernos de
                      cristal, garras, cola larga con cristales de amatista y
                      dos alas de mariposa enormes sobre un armazon de dragon:
                      huesos-dedo oscuros y la membrana con una espiral de
                      viento como una galaxia.
  C  POLILLA DE RAYOS La polilla de su primera imagen: cuerpo negro con vetas
                      de rayo, dos ojos azules grandes, antenas finas con la
                      punta encendida, cristales de amatista en hombros y
                      cabeza, y las mismas alas de armazon oscuro y espiral.

Mismo sistema que viento_modelo.py (diseno A): cajas en pixeles de modelo
(16 = 1 bloque, Y hacia abajo, frente a -Z), losetas en mosaico para el cuerpo
e imagenes estiradas para las alas. Se dibujan escalados: B a x2,2 y C a x1,35
(ESCALA_B, ESCALA_C), para que el cuerpo pese frente a las alas.
"""
import math, random
import numpy as np
import nerea_modelo as nm
import viento_modelo as vm

_hex = nm._hex
_loseta = nm._loseta
nodo = nm.nodo

ESCALA_B, ESCALA_C = 2.2, 1.35
ESCAMA = vm._rampa('07090f', '0d1120', '141a30', '1d2644', '2a3660')
VIENTRE = vm._rampa('101830', '182444', '22325a', '2e4472', '3f5a8e')
AMATISTA = vm._rampa('3a1650', '5a2478', '7d3aa6', 'a65ad0', 'd6a8f6')
HUESO = vm._rampa('1a2236', '2c3852', '46587a', '6c80a4', '9eb0cc')
RAYO = (143, 246, 255)
OJO_C, OJO_B = _hex('effcff'), _hex('2ea8ff')


# ----------------------------------------------------------------------
#  Losetas
# ----------------------------------------------------------------------
def _escamas(rampa):
    def f(x, y, r):
        # escamas en tejado: media luna clara arriba, sombra abajo
        fx, fy = (x + (y // 4 % 2) * 2) % 4, y % 4
        if fy == 3:
            return rampa[0]
        if fy == 0 and fx in (1, 2):
            return rampa[3]
        return rampa[r.choice([1, 2, 2])]
    return f


def _vetas(semilla, n=3):
    """Grietas de rayo: caminos que zigzaguean por la loseta."""
    r = random.Random(semilla)
    puntos = set()
    for _ in range(n):
        x, y = r.randrange(16), 0
        while y < 16:
            puntos.add((x % 16, y))
            if r.random() < 0.35:
                x += r.choice((-1, 1))
                puntos.add((x % 16, y))
            y += 1
    return puntos


def _con_vetas(base, semilla, densidad=2):
    tex = base.copy()
    emis = np.zeros_like(tex)
    for (x, y) in _vetas(semilla, densidad):
        tex[y, x, :3] = (70, 150, 176)
        emis[y, x] = (*RAYO, 95)
    return tex, emis


def materiales_bc():
    escama = _loseta(301, _escamas(ESCAMA))
    vientre = _loseta(302, lambda x, y, r: VIENTRE[0] if y % 5 == 4 else VIENTRE[r.choice([1, 2, 2, 3])])

    def cristal(x, y, r):
        # facetas: diagonal clara, base oscura
        if (x + y) % 6 == 0:
            return AMATISTA[4]
        if (x - y) % 7 == 0:
            return AMATISTA[1]
        return AMATISTA[r.choice([2, 3, 3])]
    ama = _loseta(303, cristal)
    ama_emis = np.zeros_like(ama)
    ama_emis[..., :3] = ama[..., :3]
    ama_emis[..., 3] = 70

    def gema(x, y, r):
        d = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
        if d > 0.86:
            return tuple(int(c * 0.35) for c in OJO_B)
        k = max(0.0, 1 - d * 1.2)
        return tuple(int(OJO_B[i] + (OJO_C[i] - OJO_B[i]) * k) for i in range(3))

    hueso = _loseta(305, lambda x, y, r: HUESO[r.choice([1, 2, 2, 3])] if x % 6 else HUESO[0])
    return {
        'escama': escama,
        'escama_rayo': _con_vetas(escama, 310, 1),
        'escama_rayo2': _con_vetas(escama, 311, 2),
        'vientre': _con_vetas(vientre, 312, 1),
        'amatista': (ama, ama_emis),
        'gema': _loseta(304, gema),
        'hueso': hueso,
        'garra': _loseta(306, lambda x, y, r: HUESO[r.choice([3, 3, 4])] if y % 5 else HUESO[2]),
        'brillo_c': _loseta(307, nm.emisivo('ffffff', '8ff6ff')),
    }


EMISIVOS_BC = {'gema', 'brillo_c'}


# ----------------------------------------------------------------------
#  Alas de armazon y espiral
# ----------------------------------------------------------------------
BANDAS = [(246, 251, 255), (216, 234, 251), (170, 212, 245), (238, 247, 255), (104, 156, 224), (30, 54, 116)]


def _ala_espiral(W, H, poly, muneca, costillas, centro, semilla, raiz=(0.0, 0.5)):
    r = random.Random(semilla)
    im = np.zeros((H, W, 4), np.uint8)
    gl = np.zeros((H, W, 4), np.uint8)
    P = [(u * W, v * H) for u, v in poly]
    cx, cy, R = centro[0] * W, centro[1] * H, centro[2] * W
    for y in range(H):
        for x in range(W):
            if not vm._dentro(P, x + 0.5, y + 0.5):
                continue
            d = min(vm._dist_seg(x + 0.5, y + 0.5, P[i], P[(i + 1) % len(P)]) for i in range(len(P)))
            col = np.array((222, 236, 252)) * (0.92 + 0.08 * r.random())
            a = 178
            dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / R
            if dd < 1.0:
                ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                t = ((ang + 3.8 * math.log(max(dd, 0.03))) / (2 * math.pi) * 3) % 1.0
                banda = int(t * len(BANDAS))
                col = np.array(BANDAS[banda])
                a = 236
                if banda == 0:
                    gl[y, x] = (60, 100, 150, 255)
                if dd < 0.12:
                    col, a = np.array((250, 255, 255)), 255
                    gl[y, x] = (200, 245, 255, 255)
            if d < 1.3:
                col, a = np.array((12, 16, 34)), 255
            im[y, x] = (*np.clip(col, 0, 255).astype(int), a)
    # florituras: rizos pequenos de viento por la membrana
    for _ in range(7):
        for _intento in range(20):
            x0, y0 = r.uniform(0.1, 0.9) * W, r.uniform(0.1, 0.9) * H
            if vm._dentro(P, x0, y0) and math.hypot(x0 - cx, y0 - cy) > R * 1.15:
                break
        rr = r.uniform(3.0, 6.5)
        sentido = r.choice((-1, 1))
        prev = None
        for k in range(40):
            th = k / 40 * 3.2 * math.pi
            rad = rr * (1 - k / 46)
            px, py = x0 + sentido * math.cos(th) * rad, y0 + math.sin(th) * rad
            if prev:
                vm._linea(im, prev[0], prev[1], px, py, (70, 118, 196, 235))
            prev = (px, py)
    # el armazon: huesos-dedo oscuros desde la muneca, y el brazo hasta ella
    mx, my = muneca[0] * W, muneca[1] * H
    oscuro = (12, 16, 34, 255)
    for grosor, (u0, v0, u1, v1) in [(2.4, (raiz[0], raiz[1], muneca[0], muneca[1]))] + \
            [(1.6, (muneca[0], muneca[1], u, v)) for (u, v) in costillas]:
        x0, y0, x1, y1 = u0 * W, v0 * H, u1 * W, v1 * H
        for o in np.linspace(-grosor / 2, grosor / 2, 3):
            nx, ny = -(y1 - y0), (x1 - x0)
            n = math.hypot(nx, ny) + 1e-6
            vm._linea(im, x0 + nx / n * o, y0 + ny / n * o, x1 + nx / n * o, y1 + ny / n * o, oscuro)
    # el borde se deshace en estelas
    for _ in range(26):
        y = r.randint(0, H - 1)
        fila = np.nonzero(im[y, :, 3])[0]
        if len(fila) == 0:
            continue
        x0 = fila[-1] + 1
        for k in range(r.randint(2, 7)):
            if x0 + k < W:
                im[y, x0 + k] = (220, 236, 255, max(0, 120 - k * 18))
    return im, gl


# B: ala de dragon, festoneada entre los dedos
POLY_B = [(0.0, 0.25), (0.36, 0.06), (1.0, 0.0), (0.84, 0.3), (0.93, 0.55), (0.74, 0.6), (0.69, 0.86),
          (0.52, 0.8), (0.38, 1.0), (0.22, 0.83), (0.08, 0.86), (0.0, 0.7)]
COSTILLAS_B = [(1.0, 0.0), (0.93, 0.55), (0.69, 0.86), (0.38, 1.0), (0.08, 0.86)]
# C: ala de polilla con el mismo armazon
POLY_C_SUP = [(0.0, 0.3), (0.3, 0.06), (0.7, 0.0), (1.0, 0.03), (0.96, 0.22), (0.86, 0.32), (0.9, 0.5), (0.76, 0.56),
              (0.72, 0.78), (0.56, 0.76), (0.46, 0.96), (0.3, 0.84), (0.14, 0.92), (0.0, 0.72)]
COSTILLAS_C_SUP = [(1.0, 0.03), (0.9, 0.5), (0.72, 0.78), (0.46, 0.96), (0.14, 0.92)]
POLY_C_INF = [(0.0, 0.0), (0.4, 0.04), (0.78, 0.2), (0.92, 0.42), (0.78, 0.5), (0.74, 0.7), (0.58, 0.68),
              (0.48, 0.92), (0.32, 0.78), (0.14, 0.86), (0.0, 0.5)]
COSTILLAS_C_INF = [(0.92, 0.42), (0.74, 0.7), (0.48, 0.92), (0.14, 0.86)]

_IMG = {}


def imagenes_bc():
    if not _IMG:
        b, gb = _ala_espiral(80, 62, POLY_B, (0.36, 0.06), COSTILLAS_B, (0.56, 0.42, 0.3), 21, raiz=(0.0, 0.45))
        cs, gcs = _ala_espiral(80, 56, POLY_C_SUP, (0.3, 0.07), COSTILLAS_C_SUP, (0.56, 0.42, 0.3), 22)
        ci, gci = _ala_espiral(60, 54, POLY_C_INF, (0.06, 0.1), COSTILLAS_C_INF, (0.46, 0.42, 0.32), 23, raiz=(0.0, 0.2))
        for nombre, (im, g) in (('ala_b', (b, gb)), ('ala_c_sup', (cs, gcs)), ('ala_c_inf', (ci, gci))):
            _IMG[nombre + '_izq'] = (im, g)
            _IMG[nombre + '_der'] = (im[:, ::-1].copy(), g[:, ::-1].copy())
    return _IMG


PLANOS_BC = {f'{a}_{l}' for a in ('ala_b', 'ala_c_sup', 'ala_c_inf') for l in ('izq', 'der')}
TRANSLUCIDOS_BC = set(PLANOS_BC)


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def cristales(nombre, off, n=4, tam=5, semilla=0, inclina=(0, 0, 0)):
    """Racimo de cristales de amatista: prismas de distinto alto y angulo."""
    r = random.Random(semilla)
    hijos = []
    for i in range(n):
        alto = tam * r.uniform(0.9, 2.2)
        ancho = tam * r.uniform(0.45, 0.75)
        rot = (inclina[0] + r.uniform(-35, 35), r.uniform(0, 90), inclina[2] + r.uniform(-35, 35))
        hijos.append(nodo(f'{nombre}_{i}', (r.uniform(-tam, tam) * 0.6, 0, r.uniform(-tam, tam) * 0.6), rot,
                          [((-ancho / 2, -alto, -ancho / 2, ancho, alto, ancho), 'amatista')]))
    return nodo(nombre, off, (0, 0, 0), [], hijos)


def _hueso_ala(nombre, p0, p1, grosor=4.0):
    """Hueso del borde del ala entre dos puntos del plano del ala (X, Y)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    return nodo(nombre, (p0[0], p0[1], 0.0), (0, 0, ang), [((0, -grosor / 2, -grosor / 2, L, grosor, grosor), 'escama')])


def _ala(nombre, lado, off, rot, W, H, poly_img, muneca, v0_frac, cristal_semilla=None):
    """Plano del ala con su imagen, mas el hueso del borde de ataque en 3D
    (de la raiz a la muneca y de la muneca a la punta) y cristales en la
    muneca."""
    s = lado
    x0 = 0.0 if s > 0 else -W
    v0 = -H * v0_frac
    def p(u, v):
        return (s * u * W, v0 + v * H)
    hijos = [_hueso_ala(nombre + '_brazo', p(0.0, poly_img[0][1] + 0.08), p(*muneca), 5.0),
             _hueso_ala(nombre + '_dedo', p(*muneca), p(1.0, 0.0), 3.5)]
    if cristal_semilla is not None:
        mx, my = p(*muneca)
        hijos.append(cristales(nombre + '_cristal', (mx, my - 1, 0), 4, 4.5, cristal_semilla))
    return nodo(nombre, off, rot, [((x0, v0, 0.0, W, H, 0.0), nombre)], hijos)


# ----------------------------------------------------------------------
#  B: dragon mariposa de multiples ojos
# ----------------------------------------------------------------------
def _ojos_racimo():
    """Ocho ojos-gema en la frente y el hocico, de distinto tamano."""
    r = random.Random(77)
    cajas = []
    sitios = [(-6, -15, -10, 5), (1, -15.5, -11, 5.5), (-1.5, -14, -16, 4), (5.5, -13.5, -15, 4),
              (-8.5, -11, -15, 3.5), (8, -10.5, -12, 3.5), (-4, -11.5, -21, 3.5), (2.5, -11, -22, 3)]
    for x, y, z, t in sitios:
        cajas.append(((x - t / 2, y - t / 2, z - t / 2, t, t, t), 'gema'))
    return cajas


def _pata_b(lado, delante):
    s = lado
    n = ('brazo_' if delante else 'pierna_') + ('izq' if s > 0 else 'der')
    if delante:
        return nodo(n, (15 * s, -20, -8), (34, 0, 18 * s), [((-3, 0, -3, 6, 15, 6), 'escama_rayo')], [
            nodo(n + '_ante', (0, 15, 0), (-62, 0, 0), [((-2.5, 0, -2.5, 5, 14, 5), 'escama')], [
                nodo(n + '_mano', (0, 14, 0), (20, 0, 0), [
                    *[((-2.6 + i * 2.1, 0, -1.2, 1.4, 7, 1.4), 'garra') for i in range(3)]]),
            ]),
        ])
    return nodo(n, (10 * s, 6, 4), (-34, 0, 12 * s), [((-5, 0, -5, 10, 17, 10), 'escama_rayo2')], [
        nodo(n + '_espinilla', (0, 17, 0), (66, 0, 0), [((-3.5, 0, -3.5, 7, 16, 7), 'escama')], [
            nodo(n + '_pie', (0, 16, 0), (-36, 0, 0), [((-4, 0, -8, 8, 4, 11), 'escama'),
                                                         *[((-3.6 + i * 2.6, 1, -11, 1.6, 2, 4), 'garra') for i in range(3)]]),
        ]),
    ])


def _cola_b():
    segs = 8
    nodo_ = None
    for i in reversed(range(segs)):
        t = i / segs
        g = 12 - 8.5 * t
        cajas = [((-g / 2, 0, -g / 2, g, 14, g), 'escama_rayo' if i % 2 else 'escama')]
        hijos = [nodo_] if nodo_ else []
        if i in (1, 3, 5):
            hijos.append(cristales(f'cola_cristal_{i}', (0, 6, g / 2), 3, 3.5 - 0.3 * i, 40 + i, inclina=(60, 0, 0)))
        if i == segs - 1:
            cajas.append(((-0.5, 12, -5, 1, 9, 10), 'escama'))           # aleta de la punta
        nodo_ = nodo(f'cola_{i}', (0, 14 if i else 0, 0), (-5 if i else 0, 0, 6 if i % 3 else -4), cajas, hijos)
    return nodo('cola', (0, 4, 13), (58, 0, 0), [], [nodo_])


def esqueleto_b(altura=3.6):
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('cuerpo', (0, 24 - altura * 16, 0), (0, 0, 0), [], [
            nodo('torso', (0, 0, 0), (26, 0, 0), [
                ((-17, -30, -14, 34, 36, 28), 'escama_rayo'),
                ((-12, -26, -15.5, 24, 30, 2), 'vientre'),
                ((-14, 2, -12, 28, 8, 24), 'escama'),                       # cadera
            ], [
                cristales('cristal_hombro_izq', (15, -30, 6), 5, 5.5, 1),
                cristales('cristal_hombro_der', (-15, -30, 6), 5, 5.5, 2),
                cristales('cristal_lomo', (0, -18, 14), 4, 4.5, 3, inclina=(40, 0, 0)),
                nodo('cuello', (0, -30, -5), (-34, 0, 0), [((-7.5, -18, -7.5, 15, 18, 15), 'escama_rayo')], [
                    nodo('cabeza', (0, -18, -2), (40, 0, 0), [
                        ((-11, -14, -14, 22, 15, 22), 'escama'),
                        ((-7, -10, -30, 14, 10, 17), 'escama'),             # hocico
                        *_ojos_racimo(),
                    ], [
                        nodo('mandibula', (0, 0, -12), (16, 0, 0), [((-6.5, 0, -17, 13, 4, 17), 'escama'),
                                                                     *[((-5.5 + i * 2.6, -2, -16.5, 1.4, 2.5, 1.4), 'garra') for i in range(5)]]),
                        nodo('cuerno_izq', (7, -13, 4), (-58, 0, -20), [((-1.8, -12, -1.8, 3.6, 12, 3.6), 'escama'),
                                                                        ((-1.2, -17, -1.2, 2.4, 5, 2.4), 'brillo_c')]),
                        nodo('cuerno_der', (-7, -13, 4), (-58, 0, 20), [((-1.8, -12, -1.8, 3.6, 12, 3.6), 'escama'),
                                                                         ((-1.2, -17, -1.2, 2.4, 5, 2.4), 'brillo_c')]),
                        cristales('cristal_cabeza', (0, -14, 2), 4, 3.5, 4, inclina=(-30, 0, 0)),
                    ]),
                ]),
                _pata_b(1, True), _pata_b(-1, True),
                _pata_b(1, False), _pata_b(-1, False),
                _ala('ala_b_izq', 1, (14, -26, 10), (0, -16, -14), 92, 72, POLY_B, (0.36, 0.06), 0.25, 11),
                _ala('ala_b_der', -1, (-14, -26, 10), (0, 16, 14), 92, 72, POLY_B, (0.36, 0.06), 0.25, 12),
                _cola_b(),
            ]),
        ]),
    ])


# ----------------------------------------------------------------------
#  C: polilla de rayos
# ----------------------------------------------------------------------
def _antena_c(lado):
    s = lado
    n = 'antena_' + ('izq' if s > 0 else 'der')
    return nodo(n, (6 * s, -24, -6), (-26, 0, 22 * s), [((-1, -40, -1, 2, 40, 2), 'escama')], [
        nodo(n + '_punta', (0, -40, 0), (-40, 0, -14 * s), [((-0.8, -14, -0.8, 1.6, 14, 1.6), 'escama'),
                                                            ((-2, -18, -2, 4, 4, 4), 'brillo_c')]),
    ])


def esqueleto_c(altura=6.6):
    patas = []
    for s in (1, -1):
        for i in range(3):
            rot = [(-30, 0, 34 * s), (-4, 0, 52 * s), (30, 0, 52 * s)][i]
            n = f'pata{i}_{"izq" if s > 0 else "der"}'
            patas.append(nodo(n, (16 * s, -6 + i * 12, -6 + i * 4), rot, [((-2, 0, -2, 4, 26, 4), 'escama')], [
                nodo(n + '_t', (0, 26, 0), (60 if i else -60, 0, 0), [((-1.5, 0, -1.5, 3, 26, 3), 'escama')]),
            ]))
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('cuerpo', (0, 24 - altura * 16, 0), (0, 0, 0), [], [
            nodo('torax', (0, 0, 0), (-8, 0, 0), [
                ((-20, -24, -15, 40, 46, 30), 'escama_rayo'),
                ((-22, -27, -17, 44, 10, 34), 'escama_rayo2'),
            ], [
                cristales('cristal_hombro_izq', (18, -26, 2), 5, 6, 5),
                cristales('cristal_hombro_der', (-18, -26, 2), 5, 6, 6),
                cristales('cristal_pecho', (0, -6, -15), 3, 3.5, 7, inclina=(-80, 0, 0)),
                nodo('cabeza', (0, -26, -5), (14, 0, 0), [
                    ((-14, -24, -13, 28, 24, 24), 'escama'),
                    ((-17, -20, -15, 11, 12, 13), 'gema'),                     # dos ojos grandes
                    ((6, -20, -15, 11, 12, 13), 'gema'),
                    ((-4, -6, -14, 8, 6, 2), 'escama_rayo'),
                ], [
                    cristales('cristal_cabeza_izq', (8, -24, 2), 4, 4.5, 8, inclina=(-20, 0, -20)),
                    cristales('cristal_cabeza_der', (-8, -24, 2), 4, 4.5, 9, inclina=(-20, 0, 20)),
                    _antena_c(1), _antena_c(-1),
                ]),
                _ala('ala_c_sup_izq', 1, (18, -14, 12), (0, -18, -14), 150, 104, POLY_C_SUP, (0.3, 0.07), 0.3, 13),
                _ala('ala_c_sup_der', -1, (-18, -14, 12), (0, 18, 14), 150, 104, POLY_C_SUP, (0.3, 0.07), 0.3, 14),
                _ala('ala_c_inf_izq', 1, (17, 10, 13), (0, -26, 14), 98, 88, POLY_C_INF, (0.06, 0.1), 0.05),
                _ala('ala_c_inf_der', -1, (-17, 10, 13), (0, 26, -14), 98, 88, POLY_C_INF, (0.06, 0.1), 0.05),
                *patas,
                nodo('abdomen', (0, 22, 4), (10, 0, 0), [((-16, 0, -13, 32, 20, 26), 'escama_rayo')], [
                    nodo('abdomen2', (0, 20, 0), (8, 0, 0), [((-13, 0, -10, 26, 18, 20), 'escama_rayo2')], [
                        nodo('abdomen3', (0, 18, 0), (8, 0, 0), [((-10, 0, -8, 20, 17, 16), 'escama_rayo')], [
                            nodo('abdomen4', (0, 17, 0), (10, 0, 0), [((-6.5, 0, -5.5, 13, 14, 11), 'escama_rayo2')], [
                                nodo('punta', (0, 14, 0), (10, 0, 0), [((-3, 0, -3, 6, 9, 6), 'escama'),
                                                                       ((-2, 8, -2, 4, 4, 4), 'brillo_c')]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ])


def quads(raiz, pose, M):
    return vm.quads(raiz, pose, M, planos=PLANOS_BC)


def dibujar(lienzo, cam, qs, luces, ambiente, niebla=None, brillo=1.4, extra=None):
    vm.dibujar(lienzo, cam, qs, luces, ambiente, niebla=niebla, brillo=brillo, extra=extra,
               mats=materiales_bc(), imgs=imagenes_bc(), translucidos_=TRANSLUCIDOS_BC, emisivos=EMISIVOS_BC)
