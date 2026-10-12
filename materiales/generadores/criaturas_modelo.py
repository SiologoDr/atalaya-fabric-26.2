"""
Bocetos de cuatro jefes que no salen de animales (ficha de diseno, 12-10-2026).
Juan, tras las Cuatro Guaridas: «te basaste en animales, eso es bueno, pero no
todo debe ser basado en animales, porque si no no vamos a tener nuevas criaturas
como Espinara». Aqui la materia es el monstruo, como la zarza en Espinara:

  A  Micelia, la Reina de las Esporas      HONGOS
     una seta que anda: el pie es el cuerpo, el sombrero la cabeza, y las laminas
     de debajo se abren en vertical como una boca con las esporas encendidas
  B  Betuna, la que Todo lo Traga          BREA
     un charco de alquitran que se levanta; lleva dentro lo que se trago (un
     craneo, una espada, un farol que aun alumbra) y la boca le hierve naranja
  C  Mandragora, la Raiz que Grita         RAIZ
     una raiz con forma de persona que grita: cara de huecos, corona de hojas y
     flores moradas, brazos y pies de raicillas
  D  Velaria, la que se Derrite            CERA
     una figura de cera que se derrite, con velas encendidas en la cabeza y los
     hombros, ojos de llama y un manto de lacre

Mismo oficio que bestias_modelo (de ahi se toman la caja con las caras pintadas
a 8 px por bloque y las ayudas): pocas piezas gordas, la boca por foco, de 7 a 12
bloques de alto y nada cosmico.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import (cubo, caja_c, viga, redondo, pua, garra, dientes, punto, _ruido, _tonos, _luz, _imagen,
                            _emis, _paseo, p_hueso, p_diente, p_boca_brasa)

TAU = math.tau
D = vr.D2R
_r = bm._r

# ----------------------------------------------------------------------
#  Rampas
# ----------------------------------------------------------------------
SOMBRERO = _r('1a0e22', '2e1a3a', '462a56', '624072', '86609a')
LAMINA = _r('6a6050', '9a8e78', 'c8bca0', 'e4dac0', 'f6f0de')
PIE = _r('7e745e', 'aa9e82', 'cec2a6', 'e6dec6', 'f6f2e4')
VOLVA = _r('3a3226', '5e5240', '867a62', 'aa9e84', 'cac0a8')
YESCA = _r('3a1a08', '6a3412', '9a5420', 'c47a34', 'e8a85a')
MICELIO = _r('8a847a', 'b8b2a6', 'dedad0', 'f0ede6', 'fcfbf8')
ESPORA = _r('0a3a3a', '16706a', '2aaea0', '6ae8d8', 'c8fff6')

BREA = _r('050508', '0c0c14', '161622', '24243a', '3a3a5a')
HIERRO = _r('1a1614', '3a3430', '5a524c', '7e7670', 'a49c94')
OXIDO = _r('3a1806', '6a2e0c', '9a4a16', 'c46e2a', 'e8a05a')

RAIZ = _r('3a2814', '6a4a26', '9a7444', 'c4a06a', 'e2c896')
RAICILLA = _r('6a5a40', '9a8664', 'c4b08a', 'e0d0ac', 'f2e8d0')
HOJA_M = _r('0e1a0a', '1c3212', '2e4e1c', '46702a', '6a9a3e')
FLOR_M = _r('2a1046', '4a2276', '6e3aa6', '9a62d0', 'c89af0')
TIERRA = _r('1a120a', '2e2014', '46321e', '5e462c', '7a5e3e')

CERA = _r('7a6a4e', 'b4a27e', 'd8c8a2', 'eee2c4', 'faf4e2')
CERA_R = _r('3a0a08', '6a1410', '9a2418', 'c43a28', 'e46a50')
MECHA = _r('0a0806', '1a1410', '2a221a', '3a3024', '4e4232')


# ----------------------------------------------------------------------
#  Pintores de Micelia
# ----------------------------------------------------------------------
def p_sombrero(tw, th, cara, s):
    """El sombrero: terciopelo de ciruela con manchas que brillan teal (a medias)."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 3.0)
    glow = np.zeros((th, tw), bool)
    for _ in range(max(1, tw * th // 45)):
        cx, cy, r = rng.uniform(0, tw), rng.uniform(0, th), rng.choice((0.8, 1.2, 1.7))
        ys, xs = np.mgrid[0:th, 0:tw]
        m = np.hypot(xs - cx, ys - cy) <= r
        glow |= m
    if cara not in ('arriba', 'abajo'):
        idx[-1, :] = 0
    tex = _imagen(_luz(idx, cara), SOMBRERO)
    if glow.any():
        c = np.array([(*ESPORA[3], 255), (*ESPORA[4], 255)], np.uint8)
        tex[glow] = c[(np.indices((th, tw)).sum(0)[glow] % 3 == 0).astype(int)]
        return tex, _emis(tex, glow, 170)
    return tex, None


def p_laminas(tw, th, cara, s):
    """Las laminas de debajo del sombrero: rayos claros desde el centro, con luz teal
    hacia dentro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    cx, cy = (tw - 1) / 2, (th - 1) / 2
    ang = np.arctan2(ys - cy, xs - cx)
    d = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
    idx = np.where((np.floor(ang / (TAU / 48)) % 2) == 0, 3, 1)
    idx[d > 0.95] = 2
    tex = _imagen(idx, LAMINA)
    glow = (d < 0.45) & (idx == 3)
    tex[glow] = (*ESPORA[3], 255)
    return tex, _emis(tex, glow, 160)


def p_lamina_diente(tw, th, cara, s):
    idx = np.full((th, tw), 3)
    idx[:, :1] = 4
    idx[-1:, :] = 2
    return _imagen(idx, LAMINA), None


def p_pie(tw, th, cara, s):
    """El pie de la seta: fibras a lo largo y alguna escama."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 2.5)
    if cara not in ('arriba', 'abajo'):
        for x in range(tw):
            if rng.random() < 0.35:
                idx[:, x] = np.clip(idx[:, x] + rng.choice((-1, 1)), 1, 3)
        for _ in range(max(1, tw * th // 30)):
            x, y = rng.randrange(tw), rng.randrange(th)
            idx[y, x] = 1
            if y + 1 < th:
                idx[y + 1, x] = 0
    return _imagen(_luz(idx, cara), PIE), None


def p_volva(tw, th, cara, s):
    idx = _tonos(tw, th, s, 2.0)
    return _imagen(_luz(idx, cara), VOLVA), None


def p_anillo(tw, th, cara, s):
    """El anillo del pie, que cuelga como una gorguera: el borde de abajo deshilachado."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 2.0) + 1
    for x in range(tw):
        largo = rng.randint(1, 3)
        idx[max(0, th - largo):, x] = 1
    return _imagen(np.clip(_luz(idx, cara), 0, 4), PIE), None


def p_yesca(tw, th, cara, s):
    """Hongo de repisa: bandas en arco desde la raiz y el canto claro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara == 'arriba' or cara == 'abajo':
        d = np.hypot((xs - (tw - 1) / 2) / max(tw / 2, 1), ys / max(th, 1))
        bandas = (d * 7.0 + _ruido(tw, th, s, 2.0) * 0.8).astype(int)
        idx = np.where(bandas % 2 == 0, 2, 3)
        idx[d > 0.9] = 4
        if cara == 'abajo':
            idx = np.full((th, tw), 1) + (_ruido(tw, th, s, 1.0) > 0.6).astype(int)
    else:
        idx = np.full((th, tw), 2)
        idx[0, :] = 4
        idx[(ys % 2 == 1)] = 3
    return _imagen(_luz(idx, cara), YESCA), None


def p_micelio(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.4, (0.3, 0.6)) + 1
    return _imagen(np.clip(_luz(idx, cara), 0, 4), MICELIO), None


def p_esporas(tw, th, cara, s):
    return bm.p_boca(tw, th, cara, s, ESPORA)


def p_seta_luz(tw, th, cara, s):
    return qm._emisivo('e8fffa', '3ad8c8', max(2, tw), max(2, th)), None


# ----------------------------------------------------------------------
#  Pintores de Betuna
# ----------------------------------------------------------------------
def p_brea(tw, th, cara, s):
    """Brea: negro pulido con un brillo de aceite ancho y suave (que tira a morado o
    a teal en el canto) y chorretones que caen por los lados."""
    rng = random.Random(s)
    v = _ruido(tw, th, s, 4.0) * 0.75 + _ruido(tw, th, s + 1, 1.6) * 0.25
    idx = np.where(v > 0.5, 2, 1)
    brillo = (v > 0.62) & (v < 0.7)
    idx[brillo] = 3
    idx[(v > 0.655) & (v < 0.675)] = 4
    if cara not in ('arriba', 'abajo'):
        for x in range(tw):
            if rng.random() < 0.25:
                largo = rng.randint(2, max(3, th // 2))
                idx[:largo, x] = 0
    tex = _imagen(_luz(idx, cara), BREA)
    ys, xs = np.mgrid[0:th, 0:tw]
    canto = brillo & (((xs + ys) // 4) % 5 == 0)
    tex[canto & (v < 0.65)] = (92, 60, 140, 255)
    tex[canto & (v >= 0.65)] = (54, 120, 136, 255)
    return tex, None


def p_burbuja(tw, th, cara, s):
    """Un ojo de burbuja: brea pulida, la pupila de fuego en medio y el brillo arriba."""
    ys, xs = np.mgrid[0:th, 0:tw]
    d = np.hypot((xs - (tw - 1) / 2) / max(tw / 2, 1), (ys - (th - 1) / 2) / max(th / 2, 1))
    idx = np.where(d < 0.22, 4, np.where(d < 0.42, 3, np.where(d < 0.6, 2, 1)))
    rampa = _r('08060a', '16121a', '5a2410', 'f0781a', 'ffe08a')
    tex = _imagen(idx, rampa)
    hx, hy = max(0, int(tw * 0.25)), max(0, int(th * 0.2))
    tex[hy:hy + max(1, th // 8), hx:hx + max(1, tw // 8)] = (236, 236, 244, 255)
    return tex, _emis(tex, idx >= 3, 210)


def p_hierro(tw, th, cara, s):
    """Hierro viejo: gris con manchas de oxido."""
    idx = _tonos(tw, th, s, 2.0)
    tex = _imagen(_luz(idx, cara), HIERRO)
    m = _ruido(tw, th, s + 3, 2.0) > 0.62
    oxi = _imagen(np.clip(_luz(_tonos(tw, th, s + 5, 1.5), cara), 0, 4), OXIDO)
    tex[m] = oxi[m]
    return tex, None


def p_farol(tw, th, cara, s):
    """El cristal del farol que se trago y aun alumbra."""
    t = qm._emisivo('fff4c0', 'ffa030', max(2, tw), max(2, th))
    t[:, :1] = (40, 34, 30, 255)
    t[:, -1:] = (40, 34, 30, 255)
    return t, _emis(t, t[..., 0] > 100, 230)


# ----------------------------------------------------------------------
#  Pintores de Mandragora
# ----------------------------------------------------------------------
def p_raiz(tw, th, cara, s):
    """Piel de raiz: anillos de crecimiento que estrangulan, nudos y pelillos."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 4.5, (0.3, 0.7))
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara not in ('arriba', 'abajo'):
        anillo = ((ys + 1.2 * np.sin(xs * 0.6 + s)) % 7) < 1.0
        idx[anillo] = 1
        idx[np.roll(anillo, -1, axis=0) & ~anillo] = 3
    for _ in range(max(1, tw * th // 40)):
        x, y = rng.randrange(tw), rng.randrange(th)
        for k in range(rng.randint(2, 3)):
            if 0 <= y + k < th and 0 <= x + k < tw:
                idx[y + k, x + k] = 0
    for _ in range(max(1, tw * th // 90)):
        cx, cy = rng.randrange(tw), rng.randrange(th)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= cy + dy < th and 0 <= cx + dx < tw:
                    idx[cy + dy, cx + dx] = 1 if (dx or dy) else 3
    return _imagen(_luz(idx, cara), RAIZ), None


def p_raicilla(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.5)
    return _imagen(_luz(idx, cara), RAICILLA), None


def p_hoja_m(tw, th, cara, s):
    """Hoja ancha: el nervio en medio (a lo largo), nervios de lado y el canto oscuro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    cx = (tw - 1) / 2
    idx = 2 + (_ruido(tw, th, s, 2.0) > 0.55).astype(int)
    idx[np.abs(xs - cx) < 0.6] = 4
    idx[((ys + np.abs(xs - cx) * 1.2) % 5 < 0.9) & (np.abs(xs - cx) > 0.6)] = 3
    idx[:, :1] = 0
    idx[:, -1:] = 0
    return _imagen(idx, HOJA_M), None


def p_flor_m(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.2) + 1
    idx[:1, :] = 4
    return _imagen(np.clip(_luz(idx, cara), 0, 4), FLOR_M), None


def p_tierra(tw, th, cara, s):
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 1.6)
    for _ in range(max(1, tw * th // 25)):
        idx[rng.randrange(th), rng.randrange(tw)] = 4
    return _imagen(_luz(idx, cara), TIERRA), None


def p_hueco(tw, th, cara, s):
    """Un hueco en la raiz: negro, con un resplandor palido muy al fondo."""
    return bm.p_boca(tw, th, cara, s, _r('060604', '0e0e0a', '1a1c10', '4a5420', 'c8e070'))


# ----------------------------------------------------------------------
#  Pintores de Velaria
# ----------------------------------------------------------------------
def p_cera(tw, th, cara, s, rampa=CERA):
    """Cera: lisa y algo translucida, con goterones claros que caen, su sombra al
    lado y la bola al final."""
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 4.0) > 0.62).astype(int)
    if cara not in ('arriba', 'abajo'):
        for _ in range(max(1, tw // 2)):
            x = rng.randrange(tw)
            largo = rng.randint(max(2, th // 3), max(3, th))
            ancho = rng.choice((1, 1, 2))
            for y in range(min(largo, th)):
                idx[y, x:x + ancho] = 4 if y < 2 else 3
                if x + ancho < tw:
                    idx[y, x + ancho] = 1
            if largo < th:
                idx[largo - 1:min(th, largo + 1), max(0, x - 1):x + ancho + 1] = 4
                if largo + 1 < th:
                    idx[largo + 1, x:x + ancho] = 1
    return _imagen(_luz(idx, cara), rampa), None


def p_cera_roja(tw, th, cara, s):
    return p_cera(tw, th, cara, s, CERA_R)


def p_mecha(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.2)
    return _imagen(idx, MECHA), None


def p_llama(tw, th, cara, s):
    """Llama: blanca abajo, amarilla y naranja hacia la punta (emisivo entero)."""
    th2, tw2 = max(2, th), max(2, tw)
    t = np.zeros((th2, tw2, 4), np.uint8)
    for y in range(th2):
        k = y / max(th2 - 1, 1)
        c = qm._mezcla(nm._hex('ff7a1a'), nm._hex('fff2b0'), k)
        t[y, :] = (*c, 255)
    return t, None


bm.PLENOS.add(p_seta_luz)
bm.PLENOS.add(p_llama)


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def repisa(out, M, r, grosor=0.35, semilla=0):
    """Un hongo de repisa: medio disco a escalones que sale hacia +z desde z=0."""
    for i, (fw, fd) in enumerate(((1.0, 0.45), (0.78, 0.78), (0.45, 1.0))):
        cubo(out, M, -r * fw, -grosor / 2, 0, 2 * r * fw, grosor, r * fd, p_yesca, semilla=semilla + i)


def setita(out, M, h, r=0.22, semilla=0):
    """Una seta pequena que brilla."""
    cubo(out, M, -0.06, 0, -0.06, 0.12, h, 0.12, p_pie, semilla=semilla)
    cubo(out, M, -r, h, -r, 2 * r, 0.14, 2 * r, p_seta_luz, semilla=semilla)


def vela(out, M, h, r=0.2, semilla=0):
    """Una vela con su mecha y su llama, y un goteron que le cae."""
    cubo(out, M, -r, 0, -r, 2 * r, h, 2 * r, p_cera, semilla=semilla)
    cubo(out, M, -0.04, h, -0.04, 0.08, 0.14, 0.08, p_mecha, semilla=semilla)
    cubo(out, M, -0.1, h + 0.12, -0.1, 0.2, 0.26, 0.2, p_llama, semilla=semilla)
    cubo(out, M, -0.05, h + 0.36, -0.05, 0.1, 0.16, 0.1, p_llama, semilla=semilla)
    cubo(out, M, r - 0.02, h * 0.45, -0.07, 0.1, h * 0.5, 0.14, p_cera, semilla=semilla + 1)


def goteron(out, M, x, y, z, largo, g=0.22, pintor=None, semilla=0):
    """Un goteron que cuelga de (x, y, z) con su bola al final."""
    pintor = pintor or p_cera
    cubo(out, M, x - g / 2, y - largo, z - g / 2, g, largo, g, pintor, semilla=semilla)
    cubo(out, M, x - g * 0.75, y - largo - g * 0.8, z - g * 0.75, g * 1.5, g * 1.1, g * 1.5, pintor, semilla=semilla + 1)


# ======================================================================
#  A · MICELIA, la Reina de las Esporas (hongos)
# ======================================================================
def micelia(abre=1.0, semilla=1):
    out = []
    rng = random.Random(semilla)
    # las piernas: dos pies de seta que acaban en la volva, con el micelio por el suelo
    for s in (1, -1):
        viga(out, (s * 1.3, 4.0, 0.0), (s * 1.5, 0.9, 0.3), 1.7, 1.7, p_pie, extra=0.2, semilla=1)
        redondo(out, vr.T(s * 1.5, 0, 0.3), 0, 1.1, 1.35, 1.35, p_volva, n=3, semilla=2)
        for k in range(6):
            a = k * TAU / 6 + (0.3 if s > 0 else 0.8)
            viga(out, (s * 1.5 + math.cos(a) * 0.9, 0.12, 0.3 + math.sin(a) * 0.9),
                 (s * 1.5 + math.cos(a) * 3.0, 0.06, 0.3 + math.sin(a) * 3.0), 0.2, 0.12, p_micelio, semilla=3)
    # el cuerpo: el pie de la seta, y arriba la cara
    redondo(out, vr.T(0, 3.4, 0), 0, 2.9, 1.95, 1.6, p_pie, n=3, semilla=4)
    Mp = vr.T(0, 6.2, 0.15) @ vr.Rx(6 * D)
    redondo(out, Mp, 0, 2.9, 1.75, 1.5, p_pie, n=3, semilla=5)
    # la gorguera (el anillo del pie), que enmarca la cara por debajo
    for k in range(14):
        a = k * TAU / 14
        M = Mp @ vr.T(0, 0.15, 0) @ vr.Ry(a) @ vr.T(0, 0, 1.6) @ vr.Rx(-55 * D)
        cubo(out, M, -0.45, -1.4, -0.05, 0.9, 1.4, 0.1, p_anillo, semilla=9)
    # la boca: el pie se raja en vertical y dentro se ven las laminas encendidas
    cubo(out, Mp, -0.8, 0.45, 1.2, 1.6, 2.35, 0.42, p_esporas, semilla=6)
    for s in (1, -1):
        Ml = Mp @ vr.T(s * 0.8, 0.3, 1.45) @ vr.Ry(-s * 38 * abre * D)
        cubo(out, Ml, 0 if s > 0 else -0.75, 0, -0.12, 0.75, 2.6, 0.3, p_pie, caras={'izq' if s > 0 else 'der': p_laminas}, semilla=7)
        for k in range(7):
            y = 0.6 + k * 0.32
            cubo(out, Mp, 0.3 if s > 0 else -0.8, y, 1.35, 0.5, 0.09, 0.4, p_lamina_diente, semilla=8)
    for k in range(5):                                         # una barba de micelio bajo la boca
        viga(out, punto(Mp, (-0.6 + k * 0.3, 0.45, 1.6)), punto(Mp, (-0.7 + k * 0.35, -0.6 - (k % 2) * 0.4, 1.8)), 0.1, 0.1, p_micelio, semilla=10)
    # el sombrero: ancho y bajo, ciruela con pecas de luz; el ala de delante da sombra a la cara
    Mc = Mp @ vr.T(0, 2.75, 0.2) @ vr.Rx(14 * D)
    redondo(out, Mc, 0.0, 0.6, 4.2, 4.0, p_sombrero, n=4, caras={'abajo': p_laminas}, semilla=10)
    redondo(out, Mc, 0.6, 1.3, 3.6, 3.4, p_sombrero, n=4, semilla=11)
    redondo(out, Mc, 1.3, 1.9, 2.6, 2.4, p_sombrero, n=3, semilla=12)
    redondo(out, Mc, 1.9, 2.25, 1.4, 1.3, p_sombrero, n=2, semilla=13)
    for s in (1, -1):                                         # los ojos: pecas de luz bajo el ala, sobre la boca
        for (x, z, r) in ((0.7, 2.2, 0.26), (1.4, 2.0, 0.22), (2.1, 1.6, 0.18)):
            cubo(out, Mc, s * x - r, -0.14, z - r, 2 * r, 0.14, 2 * r, p_seta_luz, semilla=14)
    for k in range(9):                                        # setitas en el sombrero
        a = rng.uniform(0, TAU)
        rr = rng.uniform(0.8, 2.8)
        y = 2.25 if rr < 1.3 else 1.9 if rr < 2.4 else 1.3
        setita(out, Mc @ vr.T(math.cos(a) * rr * 0.8, y, math.sin(a) * rr * 0.8) @ vr.Rz(rng.uniform(-15, 15) * D),
               rng.uniform(0.3, 0.6), semilla=15)
    # los brazos largos, con manos de micelio, y hongos de repisa
    for s in (1, -1):
        hom = punto(Mp, (s * 1.7, 2.0, 0.2))
        codo = np.array((s * 3.2, 6.0, 1.3))
        mun = np.array((s * 3.5, 3.3, 2.5))
        viga(out, hom, codo, 1.15, 1.15, p_pie, extra=0.2, semilla=16)
        viga(out, codo, mun, 1.0, 1.0, p_pie, extra=0.2, semilla=17)
        for k in range(5):
            dirs = np.array((s * (0.15 + 0.12 * k), -0.6, 0.55 - k * 0.12))
            garra(out, mun, dirs, (s * 0.1, -1, 0.15), 0.9, 0.8, 0.2, p_micelio, semilla=18 + k)
        repisa(out, em.marco((hom + codo) / 2, codo - hom, up=(s, 0, 0)) @ vr.Rx(-90 * D), 0.75, semilla=23)
        repisa(out, em.marco(codo * 0.6 + mun * 0.4, mun - codo, up=(s, 0, 0)) @ vr.Rx(-90 * D), 0.6, semilla=24)
    # hongos de repisa por la espalda, en escalera
    for k, (x, y, r) in enumerate(((-0.7, 4.0, 1.0), (0.8, 5.1, 0.9), (-0.6, 6.4, 0.8), (0.6, 7.6, 0.7))):
        repisa(out, vr.T(x, y, -1.4) @ vr.Ry(180 * D), r, semilla=26 + k)
    return out, {}


# ======================================================================
#  B · BETUNA, la que Todo lo Traga (brea)
# ======================================================================
def betuna(semilla=2):
    out = []
    rng = random.Random(semilla)
    # el charco y el monton de brea que se levanta
    redondo(out, vr.T(0, 0, 0.3), 0, 0.25, 5.6, 5.0, p_brea, n=4, semilla=1)
    for (y0, h, rx, rz, z) in ((0.2, 2.4, 4.2, 3.8, 0.0), (2.6, 1.8, 3.5, 3.1, -0.2), (4.4, 1.4, 2.7, 2.3, -0.3), (5.8, 0.8, 1.7, 1.4, -0.4)):
        redondo(out, vr.T(0, y0, z), 0, h, rx, rz, p_brea, n=4, semilla=2)
    # la boca: hierve naranja dentro, con chorretones por dientes
    cubo(out, vr.T(0, 0, 0), -1.5, 2.5, 2.95, 3.0, 1.9, 0.35, p_boca_brasa, semilla=3)
    cubo(out, vr.T(0, 0, 0), -1.8, 4.2, 2.8, 3.6, 0.6, 0.85, p_brea, semilla=4)        # el labio de arriba
    cubo(out, vr.T(0, 0, 0), -1.7, 2.1, 2.8, 3.4, 0.5, 0.85, p_brea, semilla=5)        # el de abajo
    for k in range(7):
        x = -1.45 + k * 0.48
        goteron(out, vr.T(0, 0, 0), x, 4.25, 3.35, 0.35 + (k % 3) * 0.25, 0.2, p_brea, semilla=6)
    for k in range(5):
        x = -1.2 + k * 0.6
        pua(out, vr.T(x, 2.55, 3.3), 0.12, 0.35 + (k % 2) * 0.2, p_brea, semilla=7)
    for k in range(4):                                         # burbujas que revientan en la boca
        cubo(out, vr.T(0, 0, 0), -1.1 + k * 0.7, 2.7 + (k % 2) * 0.7, 3.25, 0.35, 0.35, 0.12, p_brea, semilla=8)
    # los ojos: dos burbujas con el fuego dentro
    for s in (1, -1):
        redondo(out, vr.T(s * 1.0, 5.75, 0.75), 0.2, 1.5, 0.82, 0.82, p_brea, n=4, semilla=9)
        cubo(out, vr.T(s * 1.0, 5.75, 0.75), -0.62, 0.3, 0.82, 1.24, 1.1, 0.12, p_burbuja, semilla=9)
    redondo(out, vr.T(-2.0, 4.8, 1.0), 0, 0.7, 0.4, 0.4, p_brea, n=3, semilla=10)
    cubo(out, vr.T(-2.0, 4.8, 1.0), -0.3, 0.1, 0.4, 0.6, 0.5, 0.1, p_burbuja, semilla=10)
    goteron(out, vr.T(0, 0, 0), 0.6, 2.2, 3.5, 1.6, 0.26, p_brea, semilla=11)
    # los brazos: dos coladas que se arrastran hacia delante
    for s in (1, -1):
        p0, p1, p2 = np.array((s * 3.3, 3.0, 1.2)), np.array((s * 4.4, 1.5, 3.3)), np.array((s * 4.7, 0.35, 4.6))
        viga(out, p0, p1, 1.7, 1.6, p_brea, extra=0.3, semilla=11)
        viga(out, p1, p2, 1.3, 1.1, p_brea, extra=0.3, semilla=12)
        for k in (-0.4, 0.0, 0.4):
            viga(out, p2, p2 + np.array((s * 0.3 + k, -0.2, 1.0)), 0.35, 0.3, p_brea, semilla=13)
        for t_ in (0.3, 0.7):
            p = p0 + (p1 - p0) * t_
            goteron(out, vr.T(*p), 0, -0.6, 0, 0.6 + t_, 0.22, p_brea, semilla=14)
    # lo que se trago: un craneo, unas costillas, una espada, un yelmo y un farol que aun alumbra
    Mk = vr.T(-3.4, 2.5, 1.1) @ vr.Ry(35 * D) @ vr.Rz(12 * D)
    cubo(out, Mk, -0.5, -0.4, -0.5, 1.0, 0.95, 1.0, p_hueso, semilla=15)
    for s in (1, -1):
        cubo(out, Mk, s * 0.24 - 0.14, 0.05, 0.47, 0.28, 0.28, 0.06, bm.p_garra_ave, semilla=16)
    cubo(out, Mk, -0.3, -0.45, 0.4, 0.6, 0.2, 0.15, p_diente, semilla=17)
    for k in range(4):
        y = 2.0 + k * 0.55
        viga(out, (3.0, y, -0.8 + k * 0.1), (4.1, y + 0.5, 0.4), 0.22, 0.22, p_hueso, semilla=18)
    hoja0, hoja1 = np.array((0.9, 5.6, -1.6)), np.array((2.0, 8.3, -2.8))
    viga(out, hoja0, hoja1, 0.3, 0.08, p_hierro, semilla=19)
    viga(out, hoja1 + np.array((-0.45, -0.05, 0.4)), hoja1 + np.array((0.45, 0.05, -0.4)), 0.18, 0.18, p_hierro, semilla=20)
    viga(out, hoja1, hoja1 + (hoja1 - hoja0) / np.linalg.norm(hoja1 - hoja0) * 0.8, 0.16, 0.16, bm.p_garra_ave, semilla=21)
    Mc = vr.T(2.7, 3.9, 1.6) @ vr.Ry(-30 * D) @ vr.Rz(-28 * D)
    redondo(out, Mc, 0, 0.55, 0.6, 0.6, p_hierro, n=2, semilla=22)
    cubo(out, Mc, -0.62, 0.0, -0.62, 1.24, 0.12, 1.24, p_hierro, semilla=23)
    Mf = vr.T(-1.3, 6.1, -1.0) @ vr.Rz(20 * D) @ vr.Rx(-15 * D)
    cubo(out, Mf, -0.35, 0, -0.35, 0.7, 0.85, 0.7, p_farol, semilla=24)
    cubo(out, Mf, -0.42, 0.85, -0.42, 0.84, 0.15, 0.84, p_hierro, semilla=25)
    cubo(out, Mf, -0.1, 1.0, -0.1, 0.2, 0.3, 0.2, p_hierro, semilla=26)
    # goterones por los bordes y burbujas por encima
    for k in range(22):
        a = k * TAU / 22 + rng.uniform(-0.1, 0.1)
        capa = k % 3
        y, rx, rz = ((2.55, 4.0, 3.6), (4.35, 3.3, 2.9), (5.75, 2.5, 2.1))[capa]
        goteron(out, vr.T(0, 0, 0), math.cos(a) * rx, y, math.sin(a) * rz - 0.2 * capa, rng.uniform(0.3, 0.9), 0.24, p_brea, semilla=27)
    for k in range(12):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(1.0, 3.6)
        y = 2.6 if rr > 3.0 else 4.4 if rr > 2.2 else 5.8
        redondo(out, vr.T(math.cos(a) * rr, y, math.sin(a) * rr * 0.85), 0, 0.3, 0.3, 0.3, p_brea, n=2, semilla=28)
    return out, {}


# ======================================================================
#  C · MANDRAGORA, la Raiz que Grita (raiz)
# ======================================================================
def mandragora(semilla=3):
    out = []
    rng = random.Random(semilla)
    # las piernas de raiz y las raicillas que se hunden
    for s in (1, -1):
        viga(out, (s * 0.9, 2.6, 0.0), (s * 1.5, 0.3, 0.4), 1.25, 1.25, p_raiz, extra=0.2, semilla=1)
        for k in range(7):
            a = k * TAU / 7 + s
            p0 = np.array((s * 1.5, 0.35, 0.4))
            viga(out, p0, p0 + np.array((math.cos(a) * 1.8, -0.4, math.sin(a) * 1.8)), 0.18, 0.18, p_raicilla, semilla=2)
        for k in range(2):
            caja_c(out, vr.T(s * 1.15 + rng.uniform(-0.3, 0.3), 1.0 + k * 0.8, 0.7), 0, 0, 0, 0.55, 0.4, 0.5, p_tierra, semilla=3)
    # el cuerpo: una raiz gorda que se estrecha en un cuello, y encima la cabeza
    for (y0, y1, rx, rz) in ((2.0, 3.2, 1.7, 1.5), (3.2, 5.0, 2.4, 2.1), (5.0, 6.2, 2.2, 1.9), (6.2, 6.8, 1.5, 1.35),
                             (6.8, 8.6, 2.2, 2.0), (8.6, 9.3, 1.6, 1.45), (9.3, 9.7, 0.8, 0.8)):
        redondo(out, vr.T(0, 0, 0), y0, y1, rx, rz, p_raiz, n=4, semilla=4)
    # la cara de la cabeza: dos huecos con una chispa palida, cejas de pena y la boca que grita
    zc = 2.02
    for s in (1, -1):
        cubo(out, vr.T(0, 0, 0), s * 0.72 - 0.4, 8.1, zc - 0.02, 0.8, 0.9, 0.14, p_hueco, semilla=5)
        cubo(out, vr.T(0, 0, 0), s * 0.72 - 0.08, 8.45, zc + 0.1, 0.16, 0.16, 0.06, p_seta_luz, semilla=6)
        cubo(out, vr.T(s * 0.72, 9.15, zc) @ vr.Rz(s * 24 * D), -0.6, -0.15, -0.15, 1.2, 0.3, 0.5, p_raiz, semilla=7)
    cubo(out, vr.T(0, 0, 0), -0.7, 6.95, zc + 0.05, 1.4, 1.1, 0.14, p_hueco, semilla=8)
    cubo(out, vr.T(0, 0, 0), -0.48, 6.7, zc + 0.05, 0.96, 1.55, 0.14, p_hueco, semilla=9)
    for (x, y, w, h) in ((0, 8.0, 1.3, 0.25), (0, 6.55, 1.1, 0.25), (-0.86, 7.45, 0.25, 1.15), (0.86, 7.45, 0.25, 1.15)):
        caja_c(out, vr.T(0, 0, 0), x, y, zc + 0.2, w, h, 0.32, p_raiz, semilla=10)
    for k in range(3):
        cubo(out, vr.T(-0.3 + k * 0.3, 8.0, zc + 0.12) @ vr.Rx(180 * D), -0.04, 0, -0.04, 0.08, 0.35 + (k % 2) * 0.2, 0.08, p_raicilla, semilla=11)
    # pelillos de raiz por el cuerpo
    for k in range(34):
        a = rng.uniform(0, TAU)
        y = rng.uniform(2.3, 9.0)
        if math.sin(a) > 0.6 and 6.4 < y < 9.3:
            continue
        rr = 2.3 if 3.2 < y < 5.0 else 2.0 if 2.0 < y < 6.2 else 1.85 if 6.8 < y < 8.4 else 1.4
        p = np.array((math.cos(a) * rr, y, math.sin(a) * rr * 0.9))
        viga(out, p, p + np.array((math.cos(a) * 0.6, rng.uniform(-0.4, 0.2), math.sin(a) * 0.6)), 0.08, 0.08, p_raicilla, semilla=12)
    # la corona: hojas anchas que salen y se caen hacia fuera, y tres varas de flores moradas
    top = np.array((0, 9.6, 0))
    for k in range(9):
        a = k * TAU / 9 + 0.2
        base = top + np.array((math.cos(a) * 0.4, 0.0, math.sin(a) * 0.4))
        fuera = np.array((math.cos(a), 0, math.sin(a)))
        M1 = em.marco(base, fuera * 0.75 + np.array((0, 0.66, 0)), up=(math.cos(a), -0.6, math.sin(a)))
        cubo(out, M1, -0.7, -0.05, 0, 1.4, 0.1, 1.4, p_hoja_m, semilla=13)
        M2 = M1 @ vr.T(0, 0, 1.35) @ vr.Rx(-34 * D)
        cubo(out, M2, -0.75, -0.05, 0, 1.5, 0.1, 1.4, p_hoja_m, semilla=14)
        M3 = M2 @ vr.T(0, 0, 1.35) @ vr.Rx(-40 * D)
        cubo(out, M3, -0.45, -0.05, 0, 0.9, 0.1, 0.9, p_hoja_m, semilla=15)
    for k in range(3):
        a = k * TAU / 3 + 0.6
        p0 = top + np.array((math.cos(a) * 0.2, 0.0, math.sin(a) * 0.2))
        p1 = top + np.array((math.cos(a) * 0.6, 1.9 + 0.3 * k, math.sin(a) * 0.6))
        viga(out, p0, p1, 0.13, 0.13, p_hoja_m, semilla=17)
        for j in range(4):
            q = p1 + np.array((math.cos(a + j * 1.6) * 0.32, -0.22 * j, math.sin(a + j * 1.6) * 0.32))
            cubo(out, vr.T(*q), -0.2, -0.45, -0.2, 0.4, 0.45, 0.4, p_flor_m, semilla=18)
    # los brazos de raiz, nudosos, con dedos de raicilla
    for s in (1, -1):
        hom, codo, mun = np.array((s * 2.2, 4.7, 0.2)), np.array((s * 3.7, 3.4, 1.0)), np.array((s * 4.0, 1.7, 1.9))
        viga(out, hom, codo, 0.8, 0.8, p_raiz, extra=0.2, semilla=19)
        viga(out, codo, mun, 0.65, 0.65, p_raiz, extra=0.2, semilla=20)
        caja_c(out, vr.T(*codo), 0, 0, 0, 0.95, 0.95, 0.95, p_raiz, semilla=21)
        for k in range(4):
            d1 = np.array((s * (0.2 + 0.15 * k), -0.8, 0.4 - 0.2 * k))
            garra(out, mun, d1, (s * 0.2, -1, 0.1), 0.9 + 0.1 * k, 0.6, 0.18, p_raicilla, semilla=22 + k)
    return out, {}


# ======================================================================
#  D · VELARIA, la que se Derrite (cera)
# ======================================================================
def velaria(semilla=4):
    out = []
    rng = random.Random(semilla)
    # el charco y el cuerpo, como una vela enorme que se ha ido doblando
    redondo(out, vr.T(0, 0, 0.2), 0, 0.35, 3.9, 3.5, p_cera, n=4, semilla=1)
    for k in range(8):
        a = k * TAU / 8 + 0.3
        caja_c(out, vr.T(math.cos(a) * 3.7, 0.12, math.sin(a) * 3.3 + 0.2) @ vr.Ry(-a), 0, 0, 0, 1.5, 0.24, 1.0, p_cera, semilla=2)
    redondo(out, vr.T(0, 0.3, 0), 0, 2.0, 2.35, 2.05, p_cera, n=4, semilla=3)
    redondo(out, vr.T(0.1, 2.3, 0.05) @ vr.Rz(-4 * D), 0, 2.0, 2.0, 1.75, p_cera, n=4, semilla=4)
    Mt = vr.T(0.2, 4.3, 0.15) @ vr.Rz(-8 * D) @ vr.Rx(6 * D)
    redondo(out, Mt, 0, 2.2, 1.7, 1.4, p_cera, n=3, semilla=5)
    # los hombros caidos, el derecho mas bajo que el izquierdo
    cubo(out, Mt @ vr.T(0, 2.0, 0) @ vr.Rz(-10 * D), -2.3, 0, -1.1, 4.6, 1.1, 2.2, p_cera, semilla=6)
    # el manto de lacre: cae por un hombro, por delante, y por la espalda
    Mm = Mt @ vr.T(-1.3, 3.0, 0.9) @ vr.Rx(-10 * D) @ vr.Rz(6 * D)
    cubo(out, Mm, -0.6, -4.2, -0.1, 1.2, 4.2, 0.2, p_cera_roja, semilla=7)
    goteron(out, Mm, 0.1, -4.2, 0, 0.7, 0.22, p_cera_roja, semilla=8)
    for k, x in enumerate((-1.2, 0.0, 1.1)):
        M = Mt @ vr.T(x, 3.0, -1.2) @ vr.Rx(8 * D)
        largo = 5.2 + (k % 2) * 1.0
        cubo(out, M, -0.62, -largo, -0.1, 1.24, largo, 0.2, p_cera_roja, semilla=9)
    # la cabeza vencida a un lado, derritiendose sobre la cara
    Mh = Mt @ vr.T(0.3, 3.0, 0.4) @ vr.Rx(20 * D) @ vr.Rz(-14 * D)
    cubo(out, Mh, -1.05, 0, -0.95, 2.1, 2.0, 1.9, p_cera, semilla=10)
    cubo(out, Mh, -1.15, 1.25, 0.7, 2.3, 0.4, 0.5, p_cera, semilla=11)
    for s in (1, -1):                                                                     # los ojos: huecos con llama
        cubo(out, Mh, s * 0.5 - 0.28, 0.65, 0.92, 0.56, 0.6, 0.1, bm.p_garra_ave, semilla=12)
        cubo(out, Mh, s * 0.5 - 0.15, 0.68, 0.97, 0.3, 0.32, 0.1, p_llama, semilla=13)
        cubo(out, Mh, s * 0.5 - 0.08, 0.98, 0.97, 0.16, 0.2, 0.1, p_llama, semilla=13)
        goteron(out, Mh, s * 0.5 + 0.15 * s, 0.65, 1.0, 0.8 + 0.3 * (s > 0), 0.14, p_cera, semilla=14)      # las lagrimas de cera
    cubo(out, Mh, -0.3, -0.35, 0.92, 0.6, 0.95, 0.1, p_boca_brasa, semilla=15)
    for (x, l) in ((-0.15, 0.9), (0.2, 1.3), (-0.7, 0.6), (0.75, 0.9)):
        goteron(out, Mh, x, -0.1 if abs(x) < 0.5 else 0.15, 0.85, l, 0.2, p_cera, semilla=16)
    # la corona de velas finas, y velas en los hombros y en un brazo
    for k in range(7):
        a = k * TAU / 7 + 0.4
        h = 0.7 + ((k * 3) % 5) * 0.25
        vela(out, Mh @ vr.T(math.cos(a) * 0.72, 2.0, math.sin(a) * 0.62) @ vr.Rz(math.cos(a) * 12 * D) @ vr.Rx(-math.sin(a) * 12 * D), h, 0.13,
             semilla=17 + k)
    for s in (1, -1):
        for k, (x, z, h) in enumerate(((1.5, 0.3, 1.9), (1.95, -0.4, 1.2), (1.1, -0.6, 0.8), (2.1, 0.5, 0.6))):
            vela(out, Mt @ vr.T(s * x, 3.1 - (0.25 if s > 0 else 0.0), z) @ vr.Rz(rng.uniform(-10, 10) * D), h, 0.16 if k else 0.2, semilla=24 + k)
    # los brazos largos, que acaban en goterones por dedos
    for s in (1, -1):
        hom = punto(Mt, (s * 2.2, 2.6, 0.0))
        codo = hom + np.array((s * 0.8, -2.2, 0.8))
        mun = codo + np.array((s * 0.15, -2.0, 0.8))
        viga(out, hom, codo, 0.95, 0.95, p_cera, extra=0.2, semilla=28)
        viga(out, codo, mun, 0.8, 0.8, p_cera, extra=0.2, semilla=29)
        for k in range(4):
            goteron(out, vr.T(*mun), (k - 1.5) * 0.25 * s, 0.0, 0.1 * k, 1.4 + (k % 2) * 0.8, 0.2, p_cera, semilla=30 + k)
    vela(out, vr.T(*(punto(Mt, (-2.6, 1.6, 0.4)))), 0.7, 0.15, semilla=34)
    # goterones por el cuerpo
    for k in range(18):
        a = rng.uniform(-1.3, 1.3) + (0 if k % 3 else math.pi)
        y = rng.uniform(2.2, 6.4)
        rr = 2.0 if y < 4.3 else 1.7
        goteron(out, vr.T(0, 0, 0), math.sin(a) * rr, y, math.cos(a) * rr * 0.85, rng.uniform(0.6, 1.8), 0.2, p_cera, semilla=35)
    return out, {}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.3):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
