"""
El cuerpo de las jefas (13-10-2026), hecho con lo que Juan eligio del muestrario («Se quedan: C3, B2, B3,
B5, B6, L2, L3, L4, L5, P1»): la cara C3 (anime: ojos de 4 x 3 con la pestana y su rabillo, el blanco por
fuera y dos brillos), los brazos B2 (codo de bloque, mano de bloque), B3 (guante largo), B5 (armadura) y
B6 (garra), las piernas L2 (rodilla limpia), L3 (botas altas), L4 (medias con liga) y L5 (estilizada), y
el pecho P1 (el bloque de un pixel con su ribete).

Y con cuerpo de MUJER ADULTA. Juan: «la anatomia que me mostraste es como una nina; debe verse como una
mujer adulta». La cabeza sigue midiendo 8, pero el cuerpo mide 51,5 (seis cabezas y media; el muestrario
tenia cuatro): el cuello largo, los hombros anchos, la cintura estrecha, las caderas y la grupa, los
muslos que se afinan hacia la rodilla, el gemelo y el tobillo fino, y las piernas de la mitad de la
altura. El codo cae a la altura de la cintura y la muneca a la de la cadera.

Todo de cajas, como un modelo de Blockbench, en pixeles de la piel de Minecraft con 2 pixeles de textura
por unidad; al final se escala a la escena (ESCALA). Codos y rodillas giran por el canto de fuera (la
espalda del codo, el frente de la rodilla): las dos cajas se tocan siempre por ese canto y la union se ve
limpia, como un carton doblado.

Cada jefa (vulpina_modelo, gorgona_modelo) pone su paleta, su pelo, su ropa y lo suyo de monstruo.
"""
import math, random
import numpy as np
from PIL import Image
import vigia_render as vr
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel

D = vr.D2R
_r = bm._r
PPB = 2                                         # pixeles de textura por unidad
ESCALA = 0.58                                   # de pixeles de piel a la escena (la jefa mide unas 30)
I4 = np.eye(4)
BLANCO = _r('7c7884', 'a8a4b0', 'd0ccd6', 'e9e5ed', 'fbf9fd')


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def caja(out, M, x0, x1, y0, y1, z0, z1, pin, semilla=0):
    bm.cubo(out, M, x0, y0, z0, x1 - x0, y1 - y0, z1 - z0, pin, semilla=semilla)


def pt(M, p):
    return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]


# ----------------------------------------------------------------------
#  Los pintores de cada jefa (con su paleta)
# ----------------------------------------------------------------------
def liso(rampa, base=2, luz=1, sombra=1):
    def f(tw, th, cara, s):
        return _imagen(_bisel(np.full((th, tw), base), luz, sombra), rampa), None
    return f


def hebras(tw, th, s, rampa, base=1, brillo=3):
    """Pelo y pelaje: hebras a lo largo del lado mas largo, con algun brillo suelto."""
    largo_x = tw >= th
    n_l, n_t = (tw, th) if largo_x else (th, tw)
    rng = random.Random(s)
    idx = np.full((n_t, n_l), base)
    for t in range(n_t):
        if (t + s) % 3 == 0:
            idx[t, :] = base + 1
    for _ in range(max(1, n_l * n_t // 14)):
        t, a = rng.randrange(n_t), rng.randrange(n_l)
        idx[t, a:a + rng.randint(2, 4)] = brillo
    if not largo_x:
        idx = idx.T
    return _imagen(_bisel(idx, 1, 1), rampa)


def pintores(V, prefijo):
    """Los pintores comunes del cuerpo con la paleta V. Cada jefa anade los suyos al mismo diccionario."""
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = '%s_%s' % (prefijo, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    reg('piel', liso(V['piel'], 2, 0, 1))
    reg('pelo', lambda tw, th, c, s: (hebras(tw, th, s, V['pelo']), None))
    reg('tela', liso(V['tela'], 2, 1, 1))

    def tela_lisa(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= 3:
            idx[:, 0] += 1
            idx[:, -1] -= 1
        return _imagen(idx, V['tela']), None
    reg('tela_lisa', tela_lisa)
    reg('ribete', liso(V['ribete'], 2, 1, 1))
    reg('cuero', liso(V['cuero'], 2, 1, 1))
    reg('metal', liso(V['metal'], 2, 1, 1))
    reg('oro', liso(V['oro'], 3, 1, 1))
    reg('garra', liso(V['garra'], 2, 2, 1))
    reg('pelaje', lambda tw, th, c, s: (hebras(tw, th, s, V['pelaje'], 2, 4), None))

    def encaje(tw, th, cara, s):
        """El encaje: claro, con la fila de agujeros y el borde de abajo en ondas (recortado)."""
        t = _imagen(_bisel(np.full((th, tw), 3), 1, 1), V.get('encaje', BLANCO))
        if cara in ('arriba', 'abajo') or th < 3:
            return t, None
        xs = np.arange(tw)
        t[th // 2, (xs % 3) == 1] = (*V.get('encaje', BLANCO)[0], 255)
        t[-1, (xs % 3) == 2] = (0, 0, 0, 0)
        return t, None
    reg('encaje', encaje)

    def medias(tw, th, cara, s):
        idx = np.full((th, tw), 1)
        idx[:, ::3] = 2
        return _imagen(_bisel(idx, 1, 1), V['medias']), None
    reg('medias', medias)
    reg('guante', liso(V['guante'], 2, 1, 1))

    def escama(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx[((xs + (ys // 2) % 2 * 2) % 4 == 0)] = 1
        idx[(ys % 2 == 0) & ((xs + (ys // 2) % 2 * 2) % 4 == 2)] = 3
        return _imagen(_bisel(idx, 1, 1), V['escama']), None
    reg('escama', escama)

    nuc, neo, hon = V['neon']

    def gema(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('gema', gema, pleno=True)
    P['_reg'] = reg
    return P


# ----------------------------------------------------------------------
#  La cara C3, con los colores de cada jefa
# ----------------------------------------------------------------------
C3 = ["hhhhhhhh",
      "hhhhhhhh",
      "hhhhhhhh",
      "hhhhhhhh",
      "hhhhhhhh",
      "Hhhhhhhh",
      "Hscccsss",
      "Hsssssss",
      "Hkkkkkss",
      "HswRRRss",
      "Hswzrrss",
      "HsWrnrss",
      "ssbbssss",
      "ssssssss",
      "sssssssm",
      "ssssssss"]


# La C3 con mirada de jefa (13-10). Juan, sobre la C3 en Vulpina y la Gorgona: «los disenos estan bien, solo que
# la cara es muy kawaii, no parece intimidante o imponente». Mismo tamano y mismo estilo de pixel, pero: la sombra
# bajo el flequillo; las cejas a la vista y en cenio (bajan hacia la nariz); el parpado de arriba que cae en angulo
# hacia dentro y tapa la parte de arriba del iris (la mirada entrecerrada); la pupila rasgada y el iris que brilla;
# sin el brillo blanco grande ni el colorete; la marca de la jefa, un trazo en diagonal bajo el rabillo (como pintura
# de guerra); el contorno de la mandibula; la nariz mas larga; y la boca, una linea fina con una comisura que
# sube (media sonrisa de villana).
C3_FEROZ = ["hhhhhhhh",
            "hhhhhhhh",
            "hhhhhhhh",
            "hhhhhhhh",
            "hhhhhhhh",
            "Hhhhhhhh",
            "HSSSSSSS",
            "Hsccssss",
            "Hsssccss",
            "Hkkkksss",
            "HswRRkks",
            "HsWrkrKs",
            "Ssvsssss",
            "Svssssss",
            "SsssssMM",
            "SSssssss"]


def cara_c3(V, feroz=True):
    """La cara C3 entera (16 x 16): la mitad izquierda en espejo; los ojos, el pelo, la piel, las marcas y los
    labios de la paleta de la jefa. Con 'feroz' (lo de siempre desde el 13-10), la mirada de jefa; sin el, la
    C3 tal cual salio en el muestrario. Devuelve la imagen y la mascara de lo que brilla (el iris)."""
    filas = [list(f + f[::-1]) for f in (C3_FEROZ if feroz else C3)]
    filas[12][8] = 'S'
    if feroz:
        filas[11][8] = 'S'
        filas[13][10] = 'M'                         # la comisura que sube: media sonrisa de villana
    o = V['ojos']                                   # (iris, iris oscuro, iris claro)
    labio = hx(V['labios'])
    col = {
        'h': (*V['pelo'][0], 255), 'H': (*V['pelo'][1], 255),
        's': (*V['piel'][2], 255), 'S': (*V['piel'][1], 255),
        'k': (18, 10, 18, 255), 'K': (70, 44, 54, 255), 'w': (244, 240, 242, 255), 'W': (200, 194, 208, 255),
        'z': (255, 255, 255, 255),
        'r': (*hx(o[0]), 255), 'R': (*hx(o[1]), 255), 'n': (*hx(o[2]), 255),
        'b': (*hx(V.get('colorete', 'e896a0')), 255), 'm': (*labio, 255),
        'M': (*(int(c * 0.55) for c in labio), 255),
        'c': (*V['pelo'][0], 255), 'v': (*hx(V.get('marca', '9a1a18')), 255),
    }
    img = np.array([[col[ch] for ch in f] for f in filas], np.uint8)
    brilla = np.array([[ch in ('r', 'n') for ch in f] for f in filas], bool) if feroz else np.zeros((16, 16), bool)
    return img, brilla


def pintor_cara(P, V, feroz=True):
    img, brilla = cara_c3(V, feroz)

    def f(tw, th, cara, s):
        t = np.array(Image.fromarray(img).resize((tw, th), Image.NEAREST))
        if not brilla.any():
            return t, None
        m = np.array(Image.fromarray(brilla.astype(np.uint8) * 255).resize((tw, th), Image.NEAREST)) > 0
        return t, _emis(t, m, 170)
    return P['_reg']('cara' if feroz else 'cara_c3', f)


# ----------------------------------------------------------------------
#  La cabeza y el pelo de base
# ----------------------------------------------------------------------
CUELLO_Y = 43.5                                  # donde se apoya la cabeza


def cabeza(out, Mh, P, V, flequillo=5.6, mechones_cara=True):
    """La cabeza de 8 con la cara C3 y el pelo de base: el casco (la capa de encima), la nuca, los lados,
    el flequillo de siete mechones con la punta en escalon (los del medio, mas cortos) y los dos mechones
    que enmarcan la cara. La melena (o las serpientes) la pone cada jefa."""
    cara = P.get('cara') or pintor_cara(P, V)
    bm.PPB = 2
    try:
        bm.cubo(out, Mh, -4, 0, -4, 8, 8, 8, P['piel'], caras={'frente': None}, semilla=20)
        bm.cubo(out, Mh, -4, 0, 4, 8, 8, 0.0, P['piel'], caras={'frente': cara, 'atras': None}, semilla=21)
    finally:
        bm.PPB = PPB
    pelo = P['pelo']
    caja(out, Mh, -4.5, 4.5, 7.0, 8.6, -4.55, 4.6, pelo, semilla=60)                                   # el casco
    caja(out, Mh, -4.5, 4.5, -0.5, 7.1, -4.6, -3.6, pelo, semilla=61)                                  # la nuca
    for s in (1, -1):
        x0, x1 = sorted((s * 3.95, s * 4.5))
        caja(out, Mh, x0, x1, 1.6, 7.2, -4.4, 2.5, pelo, semilla=62)
    xs = np.linspace(-4.2, 4.2, 8)
    caida = [0.6, 0.15, 0.5, -0.3, -0.3, 0.5, 0.15, 0.6]
    for j in range(7):
        x0, x1 = xs[j], xs[j + 1]
        yb = flequillo - (caida[j] + caida[j + 1]) / 2
        M = Mh @ vr.T((x0 + x1) / 2, 7.2, 4.0) @ vr.Rz((j - 3) * 2.5 * D)
        w = x1 - x0 + 0.08
        bm.cubo(out, M, -w / 2, yb - 7.2 + 0.45, 0.0, w, 7.2 - yb - 0.45 + 0.4, 0.55, pelo, semilla=63 + j % 3)
        bm.cubo(out, M, -w / 4, yb - 7.2, 0.05, w / 2, 0.5, 0.45, pelo, semilla=66)
    if mechones_cara:
        for s in (1, -1):
            M = Mh @ vr.T(s * 4.05, 7.2, 3.6) @ vr.Rz(s * 4 * D)
            caja(out, M, -0.9, 0.7, -8.6, 0.2, -0.8, 0.65, pelo, semilla=67)
            caja(out, M, -0.6, 0.4, -9.6, -8.4, -0.6, 0.45, pelo, semilla=68)


# ----------------------------------------------------------------------
#  El torso de mujer adulta, con el pecho P1
# ----------------------------------------------------------------------
TORSO = [  # (y0, y1, medio ancho, medio fondo, zona)
    (24.0, 25.5, 4.2, 2.3, 'cadera'), (25.5, 28.0, 4.6, 2.45, 'cadera'), (28.0, 29.5, 4.2, 2.3, 'cadera'),
    (29.5, 30.8, 3.6, 2.1, 'cintura'), (30.8, 33.0, 3.1, 1.95, 'cintura'), (33.0, 34.3, 3.45, 2.0, 'pecho'),
    (34.3, 38.5, 3.9, 2.1, 'pecho'), (38.5, 40.2, 4.3, 2.15, 'escote'), (40.2, 41.6, 4.6, 2.05, 'hombros')]


def torso(out, P, ropa):
    """El torso en cajas escalonadas: la cadera ancha con la grupa, la cintura estrecha, las costillas, el
    escote y los hombros; el cuello largo; y el pecho P1 (un bloque que sale un pixel, con su ribete).
    'ropa' dice el pintor de cada zona: cadera, cintura, pecho, escote, hombros, cuello, busto, ribete
    (None en ribete: sin ribete)."""
    for i, (y0, y1, hx_, hz, zona) in enumerate(TORSO):
        caja(out, I4, -hx_, hx_, y0, y1, -hz, hz, ropa.get(zona, P['piel']), semilla=100 + i)
    caja(out, I4, -3.8, 3.8, 24.6, 28.0, -3.15, -2.3, ropa.get('cadera', P['piel']), semilla=110)         # la grupa
    caja(out, I4, -1.2, 1.2, 41.3, 43.8, -1.15, 1.25, ropa.get('cuello', P['piel']), semilla=111)         # el cuello
    caja(out, I4, -3.6, 3.6, 35.0, 38.0, 2.0, 3.2, ropa.get('busto', ropa.get('pecho', P['piel'])), semilla=112)   # el pecho
    if ropa.get('ribete', P['ribete']) is not None:
        caja(out, I4, -3.75, 3.75, 37.75, 38.3, 1.95, 3.35, ropa.get('ribete', P['ribete']), semilla=113)


# ----------------------------------------------------------------------
#  Brazos y manos (B2, B3, B5, B6)
# ----------------------------------------------------------------------
HOMBRO = np.array((6.05, 40.6, 0.0))
L_BRAZO, L_ANTEBRAZO = 9.0, 8.0


def marcos_brazo(s, pose, g1=1.45, g2=1.3):
    """Los marcos del hombro, del codo (que gira por la espalda) y de la muneca."""
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose.get('abd', 8) * D) @ vr.Rx(-pose.get('flex', 0) * D)
          @ vr.Ry(-s * pose.get('giro', 0) * D))
    Mc = Mh @ vr.T(0, -L_BRAZO, -g1) @ vr.Rx(-pose.get('codo', 10) * D) @ vr.T(0, 0, g2)
    Mm = Mc @ vr.T(0, -L_ANTEBRAZO, 0) @ vr.Rx(-pose.get('mun', 0) * D) @ vr.Rz(s * pose.get('mun_lado', 0) * D)
    return Mh, Mc, Mm


def mano(out, M, s, estilo, pin, una=None, k=1.2, cierra=1.0):
    """La mano en el marco de la muneca (los dedos hacia -y, la palma hacia el cuerpo, el pulgar delante).
    'bloque': la palma, los dedos juntos y el pulgar; 'dedos': cuatro dedos de dos falanges algo doblados;
    'garra': mas grande, con unas largas y negras."""
    pal = -s
    caja(out, M, -0.65 * k, 0.65 * k, -2.0 * k, 0.2, -1.15 * k, 1.15 * k, pin, semilla=200)
    if estilo == 'bloque':
        Mf = M @ vr.T(pal * 0.45 * k, -2.0 * k, 0) @ vr.Rz(-pal * 18 * cierra * D)
        caja(out, Mf, -1.05 * k if pal > 0 else -0.05, 0.05 if pal > 0 else 1.05 * k, -1.6 * k, 0.05, -1.1 * k, 1.1 * k, pin, semilla=201)
    else:
        largo = 1.0 if estilo == 'dedos' else 1.3
        for j in range(4):
            zc = (-0.83 + 0.555 * j) * k
            Mf = M @ vr.T(pal * 0.3 * k, -1.95 * k, zc) @ vr.Rz(-pal * 14 * cierra * D)
            caja(out, Mf, -0.42 * k, 0.42 * k, -largo * k, 0.05, -0.25 * k, 0.25 * k, pin, semilla=202)
            Mg = Mf @ vr.T(0, -largo * k, 0) @ vr.Rz(-pal * 22 * cierra * D)
            l2 = (0.8 - 0.08 * abs(j - 1.5)) * k
            caja(out, Mg, -0.36 * k, 0.36 * k, -l2, 0.05, -0.22 * k, 0.22 * k, pin, semilla=203)
            if una is not None:
                Mu = Mg @ vr.T(0, -l2, 0) @ vr.Rz(-pal * 25 * cierra * D)
                lu = (0.55 if estilo == 'dedos' else 1.1) * k
                caja(out, Mu, -0.28 * k, 0.28 * k, -lu, 0.05, -0.2 * k, 0.2 * k, una, semilla=204)
                caja(out, Mu @ vr.T(0, -lu, 0), -0.14 * k, 0.14 * k, -lu * 0.6, 0.02, -0.1 * k, 0.1 * k, una, semilla=205)
    Mp = M @ vr.T(pal * 0.35 * k, -0.6 * k, 0.95 * k) @ vr.Rx(-35 * D) @ vr.Rz(-pal * 20 * D)
    caja(out, Mp, -0.32 * k, 0.32 * k, -1.35 * k, 0.1, -0.32 * k, 0.32 * k, pin, semilla=206)
    if una is not None and estilo == 'garra':
        caja(out, Mp @ vr.T(0, -1.35 * k, 0), -0.2 * k, 0.2 * k, -0.8 * k, 0.02, -0.18 * k, 0.18 * k, una, semilla=207)
    return M @ vr.T(0, -2.6 * k, 0)                                      # el centro de la mano, para lo que sostenga


def brazo(out, P, s, estilo, pose, c=None):
    """Un brazo de cada estilo del muestrario. 'c' cambia los pintores: manga, puno, guante, borde,
    metal, escama, pelaje, una. Devuelve el marco de la mano."""
    c = c or {}
    if estilo == 'B2':                                                   # dos cajas, el codo limpio, mano de bloque
        Mh, Mc, Mm = marcos_brazo(s, pose)
        caja(out, Mh, -1.45, 1.45, -L_BRAZO, 1.6, -1.45, 1.45, P['piel'], semilla=212)
        caja(out, Mc, -1.3, 1.3, -L_ANTEBRAZO, 0.0, -1.3, 1.3, P['piel'], semilla=213)
        if c.get('manga', P['tela']) is not None:
            caja(out, Mh, -1.7, 1.7, -3.2, 1.85, -1.7, 1.7, c.get('manga', P['tela']), semilla=214)
        caja(out, Mc, -1.52, 1.52, -L_ANTEBRAZO, -L_ANTEBRAZO + 1.1, -1.52, 1.52, c.get('puno', P['encaje']), semilla=215)
        return mano(out, Mm, s, 'bloque', P['piel'], cierra=pose.get('cierra', 1.0))
    if estilo == 'B3':                                                   # fino, con guante largo
        Mh, Mc, Mm = marcos_brazo(s, pose, 1.35, 1.2)
        g = c.get('guante', P['guante'])
        caja(out, Mh, -1.35, 1.35, -3.6, 1.6, -1.35, 1.35, P['piel'], semilla=216)
        caja(out, Mh, -1.4, 1.4, -L_BRAZO, -3.6, -1.35, 1.4, g, semilla=217)
        caja(out, Mh, -1.58, 1.58, -4.1, -3.3, -1.58, 1.58, c.get('borde', P['encaje']), semilla=218)
        caja(out, Mc, -1.2, 1.2, -L_ANTEBRAZO, 0.0, -1.2, 1.2, g, semilla=219)
        return mano(out, Mm, s, 'dedos', g, k=1.1, cierra=pose.get('cierra', 1.0))
    if estilo == 'B5':                                                   # armadura: hombrera, codera, brazal y guantelete
        Mh, Mc, Mm = marcos_brazo(s, pose)
        met, bor = c.get('metal', P['metal']), c.get('borde', P['oro'])
        caja(out, Mh, -1.45, 1.45, -L_BRAZO, 1.6, -1.45, 1.45, c.get('manga', P['tela']), semilla=226)
        for j in range(3):                                                                   # la hombrera de tres placas
            Mj = Mh @ vr.T(s * (0.3 + 0.2 * j), 2.4 - 1.5 * j, 0) @ vr.Rz(s * (12 + 10 * j) * D)
            w = 2.35 - 0.12 * j
            caja(out, Mj, -w, w, -1.6, 0.0, -2.3 + 0.1 * j, 2.3 - 0.1 * j, met, semilla=227 + j)
            caja(out, Mj, -w - 0.08, w + 0.08, -1.6, -1.25, -2.38 + 0.1 * j, 2.38 - 0.1 * j, bor, semilla=230)
        caja(out, Mh, -1.75, 1.75, -L_BRAZO - 0.8, -L_BRAZO + 1.4, -2.1, -0.2, met, semilla=231)        # la codera
        caja(out, Mh, -0.5, 0.5, -L_BRAZO - 0.6, -L_BRAZO + 0.7, -2.4, -1.95, bor, semilla=232)
        caja(out, Mc, -1.7, 1.7, -L_ANTEBRAZO + 0.1, -0.4, -1.7, 1.7, met, semilla=233)                 # el brazal
        for y0 in (-L_ANTEBRAZO + 0.1, -1.0):
            caja(out, Mc, -1.82, 1.82, y0, y0 + 0.6, -1.82, 1.82, bor, semilla=234)
        return mano(out, Mm, s, 'dedos', met, k=1.25, cierra=pose.get('cierra', 1.0))
    if estilo == 'B6':                                                   # garra: escamas, gorguera de pelo, unas largas
        Mh, Mc, Mm = marcos_brazo(s, pose)
        esc = c.get('escama', P['escama'])
        caja(out, Mh, -1.45, 1.45, -L_BRAZO, 1.6, -1.45, 1.45, P['piel'], semilla=235)
        caja(out, Mc, -1.55, 1.55, -L_ANTEBRAZO, 0.0, -1.55, 1.55, esc, semilla=236)
        caja(out, Mc, -1.85, 1.85, -1.6, 0.4, -1.85, 1.85, c.get('pelaje', P['pelaje']), semilla=237)   # la gorguera
        for j in range(3):                                                                   # las puas del antebrazo
            Mj = Mc @ vr.T(0.0, -1.9 - 1.9 * j, -1.55) @ vr.Rx(40 * D)
            caja(out, Mj, -0.38, 0.38, 0.0, 1.3 - 0.18 * j, -0.38, 0.38, c.get('una', P['garra']), semilla=238)
        return mano(out, Mm, s, 'garra', esc, una=c.get('una', P['garra']), k=1.45, cierra=pose.get('cierra', 1.0))
    raise ValueError(estilo)


# ----------------------------------------------------------------------
#  Piernas y pies (L2, L3, L4, L5)
# ----------------------------------------------------------------------
CADERA = np.array((2.3, 26.0, 0.0))
L_MUSLO, L_PIERNA = 12.0, 12.0


def marcos_pierna(s, pose, gk=1.85, gs=1.6):
    """Los marcos de la cadera, de la rodilla (que gira por delante) y del tobillo (el pie vuelve a la
    horizontal)."""
    Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose.get('abd', 2) * D) @ vr.Rx(-pose.get('flex', 0) * D)
    Mr = Mt @ vr.T(0, -L_MUSLO, gk) @ vr.Rx(pose.get('rodilla', 3) * D) @ vr.T(0, 0, -gs)
    Mp = (Mr @ vr.T(0, -L_PIERNA, 0) @ vr.Rx((pose.get('flex', 0) - pose.get('rodilla', 3) - pose.get('pie', 0)) * D)
          @ vr.Rz(-s * pose.get('abd', 2) * D))
    return Mt, Mr, Mp


def muslo(out, Mt, pin, semilla=0):
    """El muslo, ancho arriba y mas fino en la rodilla, con el frente recto y la espalda que se afina."""
    caja(out, Mt, -2.2, 2.2, -6.0, 1.2, -2.5, 1.95, pin, semilla=semilla)
    caja(out, Mt, -1.85, 1.85, -L_MUSLO, -5.9, -1.8, 1.85, pin, semilla=semilla + 1)


def espinilla(out, Mr, pin, semilla=0, extra=0.0):
    """La pierna: el gemelo que sale por detras y el tobillo fino, con el frente recto (la espinilla)."""
    caja(out, Mr, -1.6 - extra, 1.6 + extra, -5.0, 0.0, -2.0 - extra, 1.6 + extra, pin, semilla=semilla)
    caja(out, Mr, -1.2 - extra, 1.2 + extra, -L_PIERNA, -4.9, -1.25 - extra, 1.6 + extra, pin, semilla=semilla + 1)


def pie(out, M, estilo, pin, c=None):
    c = c or {}
    if estilo == 'zapato':                                               # zapato de tira
        caja(out, M, -1.35, 1.35, -2.0, 0.3, -1.45, 3.8, pin, semilla=250)
        caja(out, M, -1.4, 1.4, -2.0, -1.65, -1.5, 3.85, c.get('suela', pin), semilla=251)
        caja(out, M, -1.42, 1.42, -0.6, -0.2, 0.3, 1.0, pin, semilla=252)
    elif estilo == 'tacon':
        Mi = M @ vr.Rx(18 * D)
        caja(out, Mi, -1.25, 1.25, -1.1, 0.4, -1.45, 3.7, pin, semilla=253)
        caja(out, M, -0.45, 0.45, -2.0, -0.7, -1.45, -0.55, pin, semilla=254)
    elif estilo == 'bota':
        caja(out, M, -1.55, 1.55, -1.7, 0.6, -1.7, 4.0, pin, semilla=255)
        caja(out, M, -1.6, 1.6, -2.0, -1.6, -1.75, 4.05, c.get('suela', P_NEGRO), semilla=256)
        caja(out, M, -0.6, 0.6, -2.0, -1.3, -1.75, -0.9, c.get('suela', P_NEGRO), semilla=257)
    elif estilo == 'sandalia':
        caja(out, M, -1.25, 1.25, -1.7, 0.2, -1.3, 3.6, c.get('piel', pin), semilla=258)            # el pie
        caja(out, M, -1.4, 1.4, -2.0, -1.7, -1.45, 3.75, pin, semilla=259)                             # la suela
        for z in (0.4, 2.2):
            caja(out, M, -1.32, 1.32, -1.7, -1.4, z, z + 0.4, pin, semilla=260)


def _negro(tw, th, cara, s):
    return _imagen(_bisel(np.full((th, tw), 1), 1, 1), _r('0a090d', '131116', '1c1a22', '29252f', '3b3644')), None


_negro.__name__ = 'jefa_negro'
P_NEGRO = _negro


def pierna(out, P, s, estilo, pose, c=None):
    """Una pierna de cada estilo del muestrario. 'c' cambia los pintores: muslo, media, calcetin, bota,
    zapato, borde, liga, oro."""
    c = c or {}
    piel = c.get('muslo', P['piel'])
    Mt, Mr, Mp = marcos_pierna(s, pose)
    if estilo == 'L2':                                                   # rodilla limpia, calcetin con encaje, zapato de tira
        muslo(out, Mt, piel, 262)
        espinilla(out, Mr, c.get('pierna', P['piel']), 264)
        if c.get('calcetin', P['medias']) is not None:
            caja(out, Mr, -1.32, 1.32, -L_PIERNA, -6.0, -1.37, 1.72, c.get('calcetin', P['medias']), semilla=266)
            caja(out, Mr, -1.42, 1.42, -6.3, -5.8, -1.47, 1.82, c.get('borde', P['encaje']), semilla=267)
        pie(out, Mp, c.get('pie', 'zapato'), c.get('zapato', P_NEGRO), c)
    elif estilo == 'L3':                                                 # botas altas con la vuelta sobre la rodilla
        muslo(out, Mt, piel, 268)
        bota = c.get('bota', P['cuero'])
        espinilla(out, Mr, bota, 270, extra=0.08)
        caja(out, Mr, -1.95, 1.95, -1.3, 1.1, -2.2, 2.0, bota, semilla=272)                                 # la vuelta
        caja(out, Mr, -2.0, 2.0, 0.75, 1.1, -2.25, 2.05, c.get('oro', P['oro']), semilla=273)
        for y in (-3.0, -5.2, -7.4):                                                                     # las hebillas
            caja(out, Mr, -0.65, 0.65, y, y + 0.45, 1.6, 1.85, c.get('oro', P['oro']), semilla=274)
        pie(out, Mp, 'bota', bota, c)
    elif estilo == 'L4':                                                 # medias hasta medio muslo con liga, tacon
        med = c.get('media', P['medias'])
        caja(out, Mt, -2.2, 2.2, -6.0, 1.2, -2.5, 1.95, piel, semilla=276)
        caja(out, Mt, -1.85, 1.85, -L_MUSLO, -5.9, -1.8, 1.85, med, semilla=277)
        caja(out, Mt, -2.0, 2.0, -6.5, -5.6, -1.95, 2.0, c.get('borde', P['encaje']), semilla=278)
        caja(out, Mt, -0.25, 0.25, -5.8, 1.0, 1.85, 2.08, c.get('liga', P_NEGRO), semilla=279)            # la liga
        espinilla(out, Mr, med, 280)
        pie(out, Mp, 'tacon', c.get('zapato', P_NEGRO), c)
    elif estilo == 'L5':                                                 # estilizada: seccion de ocho lados que se afina
        med = c.get('media', P['medias'])
        for kx, kz in ((1.0, 0.72), (0.72, 1.0)):
            caja(out, Mt, -2.2 * kx, 2.2 * kx, -6.0, 1.2, -2.25 * kz - 0.2, 2.0 * kz, piel, semilla=282)
            caja(out, Mt, -1.85 * kx, 1.85 * kx, -L_MUSLO, -5.9, -1.85 * kz, 1.85 * kz, piel, semilla=283)
            caja(out, Mr, -1.6 * kx, 1.6 * kx, -1.2, 0.0, -1.6 * kz, 1.6 * kz, med, semilla=284)
            caja(out, Mr, -1.7 * kx, 1.7 * kx, -5.0, -1.1, -2.0 * kz, 1.6 * kz, med, semilla=285)
            caja(out, Mr, -1.15 * kx, 1.15 * kx, -L_PIERNA, -4.9, -1.15 * kz, 1.15 * kz + 0.3, med, semilla=286)
        if c.get('borde', P['encaje']) is not None:
            caja(out, Mt, -1.95, 1.95, -L_MUSLO + 0.2, -L_MUSLO + 0.9, -1.95, 1.95, c.get('borde', P['encaje']), semilla=287)
        pie(out, Mp, c.get('pie', 'tacon'), c.get('zapato', P_NEGRO), c)
    else:
        raise ValueError(estilo)
    return Mt, Mr, Mp


# ----------------------------------------------------------------------
#  Tubos de bloques (colas, serpientes) y fuego
# ----------------------------------------------------------------------
def curva(ctrl, n=80):
    c, _ = em.catmull([np.asarray(p, float) for p in ctrl], n)
    return [np.asarray(p, float) for p in c]


def a_lo_largo(ctrl, n, perfil, n_curva=90):
    """Los n+1 puntos repartidos por la curva y el radio de cada uno segun el perfil ((t, r), ...)."""
    c = curva(ctrl, n_curva)
    L = [0.0]
    for a, b in zip(c, c[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]
    ts = [j / n for j in range(n + 1)]
    pts = [c[min(int(np.searchsorted(L, t * total)), len(c) - 1)] for t in ts]
    rs = [float(np.interp(t, [a for a, _ in perfil], [b for _, b in perfil])) for t in ts]
    return pts, rs, ts


def tubo(out, pts, radios, pintores_por_tramo, semilla=0, arriba=(0.0, 1.0, 0.0), achata=1.0):
    """Un tubo de bloques: en cada tramo, dos cajas cruzadas (una mas ancha y otra mas alta) que dan una
    seccion de ocho lados, a lo Minecraft; cada tramo se mete un poco en el siguiente."""
    up = np.asarray(arriba, float)
    for j in range(len(pts) - 1):
        p0, p1 = np.asarray(pts[j], float), np.asarray(pts[j + 1], float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            continue
        M = em.marco(p0, d, up=up) if abs(d @ up) < 0.92 * L * np.linalg.norm(up) else em.marco(p0, d)
        r = (radios[j] + radios[j + 1]) / 2
        pin = pintores_por_tramo[j]
        for kx, ky in ((1.0, 0.72), (0.72, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.35, 2 * r * kx, 2 * r * ky * achata, L + r * 0.7, pin, semilla=semilla + j % 4)


def llama(out, pin, p, r, semilla=0):
    """Un fuego de bloques: el nucleo y tres lenguas que suben en escalones."""
    p = np.asarray(p, float)
    M = vr.T(*p)
    caja(out, M, -r, r, -r * 0.8, r * 0.9, -r, r, pin, semilla=semilla)
    caja(out, M, -r * 0.62, r * 0.62, r * 0.85, r * 1.9, -r * 0.62, r * 0.62, pin, semilla=semilla + 1)
    caja(out, M, -r * 0.3, r * 0.3, r * 1.85, r * 2.9, -r * 0.3, r * 0.3, pin, semilla=semilla + 2)
    for s in (1, -1):
        Ml = M @ vr.T(s * r * 0.75, r * 0.6, 0) @ vr.Rz(-s * 18 * D)
        caja(out, Ml, -r * 0.3, r * 0.3, 0.0, r * 1.3, -r * 0.3, r * 0.3, pin, semilla=semilla + 3)


def a_escena(qs):
    return qm.transformar(qs, np.diag([ESCALA, ESCALA, ESCALA, 1.0]))
