"""
Sargazo, el Capitan Ahogado, y sus tipos (15-10-2026). Juan, tras el Mapinguari: «no me gusto el diseno... crea este
boss segun la ilustracion, tal vez asi haces incluso algo mejor que la ilustracion, e igualmente con sus 3 tipos». La
ilustracion («MOB DE ELITE») es un capitan pirata ahogado, de bloques: la calavera azulada con los ojos cian que
brillan, el tricornio con su calavera y sus huesos cruzados, la armadura de prismarina turquesa con coral en el
sombrero y en los hombros, las correas de cuero en aspa con hebillas de oro, la casaca con faldones y las botas, una
espada enorme de hueso dentado (como el pico de un pez sierra) en la mano derecha y un arma de fuego de madera y oro en
la izquierda, en alto; y unas ruinas hundidas con haces de luz, algas y antorchas.

Todo de cajas, como un modelo de Blockbench, en pixeles (2 de textura por unidad), y al final se escala a la escena.

Los tres tipos tienen la misma pose (la espada abajo, el arma de fuego en alto) y cambian lo que llevan en la cabeza, las
armas y el color:

    A  el Capitan    el de la ilustracion: tricornio, prismarina y coral turquesa, la espada de pez sierra y el
                     trabuco; ojos cian
    B  el Arponero   panuelo anudado y un aro de oro, oxido y coral rojo; un ancla por arma y el arpon en alto;
                     ojos naranja
    C  el Almirante  bicornio con penacho blanco y charreteras de flecos, armadura negra y oro con coral blanco; un
                     sable de nacar y un farol encendido en alto; ojos de oro
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _manchas, lamina
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 2
ESCALA = 0.36

VARIANTES = {
    'A': dict(
        clave='KA', nombre='el Capitan', corto='capitan', sombrero='tricornio', arma='sierra', mano='trabuco',
        armadura=_r('0c2a2c', '15403e', '1f5a54', '2e7a6e', '48a090'),
        coral=_r('0a3a3a', '12585a', '1e7e7e', '38a8a2', '6ad4c8'),
        hueso=_r('0e1e2a', '1a3446', '284e64', '3a6a84', '5a8ea6'),
        tela=_r('061416', '0c2224', '143430', '1e4a42', '2c6656'),
        neon=('e8ffff', '3ae8ff', '04466a'),
    ),
    'B': dict(
        clave='KB', nombre='el Arponero', corto='arponero', sombrero='panuelo', arma='ancla', mano='arpon',
        armadura=_r('2a120a', '44200e', '623016', '82441e', 'a8602c'),
        coral=_r('4a0a10', '72121c', '9e1e2a', 'cc3a40', 'f0686a'),
        hueso=_r('2a201a', '463628', '685240', '8c7258', 'b49878'),
        tela=_r('2a0606', '480c0c', '6a1414', '8e2020', 'b0342e'),
        neon=('fff0d8', 'ff7a1a', '6a2404'),
    ),
    'C': dict(
        clave='KC', nombre='el Almirante', corto='almirante', sombrero='bicornio', arma='sable', mano='farol',
        armadura=_r('06060a', '101016', '1a1a24', '282836', '3a3a4c'),
        coral=_r('7a7468', 'a49c8e', 'cac2b2', 'e6e0d2', 'faf6ec'),
        hueso=_r('22202a', '3a3644', '585264', '7a7488', 'a49eb2'),
        tela=_r('060608', '0c0c12', '14141c', '1e1e2a', '2c2c3c'),
        neon=('fff8d8', 'ffd21a', '6a5004'),
    ),
}


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


ORO = _r('5a3a08', '8a5c10', 'c08a1e', 'e8b83a', 'fae27a')
CUERO = _r('1a0e08', '2c1a0e', '422816', '5c3a20', '7a502e')
MADERA = _r('1e1008', '34200e', '4e3016', '6a4420', '8a5c2e')
HIERRO = _r('0e1012', '1c2024', '2e3338', '444a52', '626a74')
ALGA = _r('061a10', '0c2a18', '143c22', '1e522e', '2c6a3c')
PERCEBE = _r('5a5448', '847c6c', 'aca290', 'cec6b2', 'eae4d2')
HUESO_CLARO = _r('7a6a50', 'b0a07e', 'dcceaa', 'f2e8cc', 'fffaea')


# ----------------------------------------------------------------------
#  Los pintores, todos propios
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'cap%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def armadura(tw, th, cara, s):
        """La armadura: placas de bloque en hileras desfasadas, cada una con su canto de luz y de sombra, y alguna mas
        oscura o mas clara (como la prismarina), con percebes sueltos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        alto, ancho = 4, 6
        fila = ys // alto
        col = (xs + (fila % 2) * 3) // ancho
        rng = np.random.default_rng(s)
        tono = rng.integers(0, 5, size=(fila.max() + 2, col.max() + 2))
        base = np.array([2, 2, 2, 3, 1])[tono[fila, col]]
        borde_luz = (ys % alto == 0) | (((xs + (fila % 2) * 3) % ancho) == 0)
        borde_sombra = (ys % alto == alto - 1) | (((xs + (fila % 2) * 3) % ancho) == ancho - 1)
        idx = np.where(borde_luz, base + 1, np.where(borde_sombra, base - 1, base))
        img = _imagen(np.clip(idx, 0, 4), V['armadura'])
        perc = (tono[fila, col] == 4) & ((xs + ys) % 5 == 0) & ~borde_luz
        img = np.where(perc[..., None], _imagen(np.full((th, tw), 3), PERCEBE), img)
        return img, None
    reg('armadura', armadura)

    def tela(tw, th, cara, s):
        """La casaca: pano oscuro con pliegues a lo largo y el ribete de oro en el canto de abajo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 5 == 0, 1, np.where(xs % 5 == 2, 3, 2))
        img = _imagen(idx, V['tela'])
        rib = ys >= th - 2
        img = np.where(rib[..., None], _imagen(np.where(ys == th - 2, 4, 2), ORO), img)
        return img, None
    reg('tela', tela)

    def faldon(tw, th, cara, s):
        """El faldon de la casaca: el pano con el canto de abajo desflecado (roto por el mar) y el ribete de oro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        rng = random.Random(s)
        corte = np.array([th - rng.choice((0, 0, 1, 2, 3)) for _ in range(tw)])
        idx = np.where(xs % 5 == 0, 1, np.where(xs % 5 == 2, 3, 2))
        img = _imagen(idx, V['tela'])
        rib = (xs <= 1) | (xs >= tw - 2)
        img = np.where(rib[..., None], _imagen(np.where((xs == 0) | (xs == tw - 1), 4, 2), ORO), img)
        img[..., 3] = np.where(ys < corte[None, :], 255, 0)
        return img, None
    reg('faldon', faldon)

    def oro(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        return _imagen(_bisel(idx, 1, 1), ORO), None
    reg('oro', oro)

    def cuero(tw, th, cara, s):
        """El cuero de las correas y las botas: con la costura de puntos por los dos cantos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo, de_traves = (ys, xs) if th > tw else (xs, ys)
        idx = np.full((th, tw), 2)
        if min(th, tw) >= 4:
            ancho = tw if th > tw else th
            costura = ((de_traves == 1) | (de_traves == ancho - 2)) & (a_lo_largo % 2 == 0)
            idx = np.where(costura, 4, idx)
        return _imagen(_bisel(idx, 1, 1), CUERO), None
    reg('cuero', cuero)

    def hebilla(tw, th, cara, s):
        """La hebilla: un marco de oro con la piedra oscura en medio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        marco = (xs <= 1) | (xs >= tw - 2) | (ys <= 1) | (ys >= th - 2)
        img = _imagen(np.where(marco, 3, 1), ORO)
        piedra = ~marco & (xs > 2) & (xs < tw - 3) & (ys > 2) & (ys < th - 3)
        img = np.where(piedra[..., None], _imagen(np.full((th, tw), 2), V['armadura']), img)
        return img, None
    reg('hebilla', hebilla)

    def calavera(tw, th, cara, s):
        """La cara: un craneo de verdad. Dos cuencas grandes y redondeadas, un poco caidas hacia fuera, con la luz
        dentro; los pomulos hundidos debajo; el hueco de la nariz en corazon al reves; y las grietas finas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        idx = np.where((xs * 2 + ys * 3) % 17 == 0, 2, idx)
        idx = np.where(ys < 2, 4, idx)
        img = _imagen(_bisel(idx, 1, 1), V['hueso'])
        sombra = _imagen(np.full((th, tw), 1), V['hueso'])
        brilla = np.zeros((th, tw), bool)
        for cx in (0.29, 0.71):
            haz = 1 if cx < 0.5 else -1
            u = (xs + 0.5 - cx * tw) / (0.17 * tw)
            v = (ys + 0.5 - 0.47 * th) / (0.22 * th) + haz * u * 0.2      # la cuenca cae un poco hacia fuera
            d = np.maximum(abs(u), abs(v)) * 0.6 + np.hypot(u, v) * 0.4    # redonda pero con algo de cuadro
            dentro = d < 1.0
            img[dentro] = (4, 8, 12, 255)
            dd = np.hypot((xs + 0.5 - cx * tw) / (0.075 * tw), (ys + 0.5 - 0.5 * th) / (0.075 * th))
            ojo = (dd < 1.0) & dentro
            img[ojo] = (*neo[1], 255)
            img[(dd < 0.5) & dentro] = (*neo[0], 255)
            halo = (dd < 1.8) & dentro & ~ojo
            img[halo] = (*neo[2], 255)
            brilla |= ojo | halo
            pom = (ys > 0.7 * th) & (ys < 0.8 * th) & (abs(xs + 0.5 - cx * tw) < 0.16 * tw) & (abs(xs + 0.5 - tw / 2) > 0.2 * tw)
            img[pom] = sombra[pom]
        yy = ys + 0.5 - 0.72 * th
        xx = abs(xs + 0.5 - tw / 2)
        nariz = ((yy > 0) & (yy < 0.18 * th) & (xx < 0.12 * tw - yy * 0.4)) | ((yy > -0.05 * th) & (yy < 0.03 * th) & (xx < 0.11 * tw) & (xx > 0.015 * tw))
        img[nariz] = (4, 8, 12, 255)
        return img, _emis(img, brilla, 255)
    reg('calavera', calavera)

    def hueso(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        return _imagen(_bisel(idx, 1, 1), V['hueso']), None
    reg('hueso', hueso)

    def boca(tw, th, cara, s):
        """La boca por delante: los dientes de la calavera, apretados, con la luz de dentro entre ellos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        img = _imagen(np.where(xs % 3 == 0, 4, 3), HUESO_CLARO)
        junta = (xs % 3 == 2)
        img[junta] = (4, 8, 12, 255)
        raya = abs(ys - th / 2 + 0.5) < 0.6
        img[raya] = (*neo[2], 255)
        return img, _emis(img, raya, 150)
    reg('boca', boca)

    def alga(tw, th, cara, s):
        """La barba de algas: cintas oscuras con el nervio claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo = ys if th >= tw else xs
        de_traves = xs if th >= tw else ys
        idx = np.where(de_traves == (min(th, tw) // 2), 3, 2)
        idx = np.where(a_lo_largo % 6 == 0, 1, idx)
        return _imagen(idx, ALGA), None
    reg('alga', alga)

    def coral(tw, th, cara, s):
        """El coral: ramas con los polipos en puntos claros."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + ys) % 3 == 0) & ((xs * ys) % 2 == 0), 4, 2)
        idx = np.where((xs + 2 * ys) % 5 == 0, 3, idx)
        return _imagen(_bisel(idx, 1, 1), V['coral']), None
    reg('coral', coral)

    def sombrero(tw, th, cara, s):
        """El sombrero: fieltro negro azulado, con el canto de oro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + ys) % 7 == 0, 1, 2)
        img = _imagen(idx, _r('06080c', '0e1218', '161c24', '202834', '2e3846'))
        rib = (ys <= 1) if cara != 'arriba' else np.zeros((th, tw), bool)
        img = np.where(rib[..., None], _imagen(np.full((th, tw), 3), ORO), img)
        return img, None
    reg('sombrero', sombrero)

    def emblema(tw, th, cara, s):
        """La calavera y los huesos cruzados del sombrero: el craneo redondo con sus cuencas y los dientes, y detras los dos
        huesos en aspa con los nudos de las puntas."""
        img, _ = sombrero(tw, th, cara, s)
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) * 0.42
        blanco = _imagen(np.full((th, tw), 4), PERCEBE)
        gris = _imagen(np.full((th, tw), 2), PERCEBE)
        L = min(tw * 0.42, th * 0.95)
        for sg in (1, -1):                                               # los huesos en aspa
            t = ((xs - cx) + sg * (ys - cy)) / 2
            n = ((xs - cx) - sg * (ys - cy)) / 2
            hueso = (abs(n) < 0.7) & (abs(t) < L * 0.5)
            for e in (1, -1):
                nudo = np.hypot(xs - (cx + e * L * 0.5), ys - (cy + sg * e * L * 0.5)) < 1.3
                hueso |= nudo
            img = np.where(hueso[..., None], gris, img)
        R = min(tw, th) * 0.26
        craneo = np.hypot((xs - cx) / R, (ys - cy) / (R * 1.05)) < 1.0
        quijada = (abs(xs - cx) < R * 0.55) & (ys > cy) & (ys < cy + R * 1.35)
        img = np.where((craneo | quijada)[..., None], blanco, img)
        for dx in (-1, 1):
            ojo = np.hypot(xs - cx - dx * R * 0.42, ys - cy + R * 0.05) < R * 0.3
            img[ojo] = (10, 10, 12, 255)
        dientes = (ys > cy + R * 0.95) & (ys < cy + R * 1.35) & (abs(xs - cx) < R * 0.55) & (np.round(xs) % 2 == 0)
        img[dientes] = (10, 10, 12, 255)
        return img, None
    reg('emblema', emblema)

    def piel(tw, th, cara, s):
        """Las manos: hueso azulado con los nudillos marcados."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 3 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V['hueso']), None
    reg('piel', piel)

    def sierra(tw, th, cara, s):
        """La hoja de la espada: hueso de pez sierra, con una veta por el medio y manchas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo, de_traves = (xs, ys) if tw >= th else (ys, xs)
        ancho = min(tw, th)
        idx = np.where(abs(de_traves - ancho / 2 + 0.5) < 0.7, 2, 4)
        idx = np.where((a_lo_largo % 9 == 0) & (de_traves % 3 == 1), 3, idx)
        return _imagen(_bisel(idx, 0, 1), HUESO_CLARO), None
    reg('sierra', sierra)

    def dientes(tw, th, cara, s):
        """Los dientes de la sierra: triangulos que salen del canto (la base abajo)."""
        t = np.zeros((th, tw, 4), np.uint8)
        paso = 6
        for x0 in range(1, tw, paso):
            for y in range(th):
                w = 3.0 * (1 - (th - 1 - y) / max(th, 1))
                for x in range(x0, min(tw, x0 + int(math.ceil(w)))):
                    t[y, x] = (*(HUESO_CLARO[4] if x == x0 else HUESO_CLARO[2]), 255)
        return t, None
    reg('dientes', dientes)

    def madera(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        a_lo_largo, de_traves = (xs, ys) if tw >= th else (ys, xs)
        idx = np.where((de_traves + a_lo_largo // 7) % 3 == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), MADERA), None
    reg('madera', madera)

    def hierro(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys % 5 == 0, 3, 2)
        return _imagen(_bisel(idx, 1, 1), HIERRO), None
    reg('hierro', hierro)

    def luz(tw, th, cara, s):
        """La luz del farol, o la que sale del canon: el centro blanco y el borde del color del tipo."""
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.maximum(abs(xs - (tw - 1) / 2) / max(tw / 2, 1), abs(ys - (th - 1) / 2) / max(th / 2, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[1], 255)
        t[d < 0.5] = (*neo[0], 255)
        return t, None
    reg('luz', luz, pleno=True)

    def penacho(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 2 == 0, 4, 3)
        return _imagen(idx, PERCEBE), None
    reg('penacho', penacho)
    return P


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def palo(out, p0, p1, ancho, alto, pintor, arriba=(0.0, 1.0, 0.0), semilla=0, caras=None):
    """Una caja de p0 a p1, de seccion ancho x alto."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    if abs(_u(d) @ _u(arriba)) > 0.97:
        arriba = (0.0, 0.0, 1.0)
    M = em.marco(p0, d, up=arriba)
    bm.cubo(out, M, -ancho / 2, -alto / 2, 0.0, ancho, alto, float(np.linalg.norm(d)), pintor, caras=caras, semilla=semilla)
    return M


def coral(out, P, base, dirl, largo, semilla=0, ramas=3):
    """Una rama de coral que crece desde 'base' hacia 'dirl', con ramitas que se abren."""
    rng = random.Random(semilla)
    base, d = np.asarray(base, float), _u(dirl)
    fin = base + d * largo
    palo(out, base, fin, 1.6, 1.6, P['coral'], semilla=semilla)
    for i in range(ramas):
        t = rng.uniform(0.35, 0.8)
        q = base + d * largo * t
        lado = _u(np.cross(d, (rng.uniform(-1, 1), rng.uniform(-0.2, 0.2), rng.uniform(-1, 1))))
        dd = _u(d * 0.6 + lado * 0.8)
        palo(out, q, q + dd * largo * rng.uniform(0.35, 0.55), 1.2, 1.2, P['coral'], semilla=semilla + 1)


def percebes(out, P, M, x0, x1, y0, y1, z, n, semilla=0):
    """Unos percebes pegados en la cara frontal de una pieza (a la altura z del marco M)."""
    rng = random.Random(semilla)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        w = rng.choice((1.0, 1.4, 1.8))
        bm.cubo(out, M, x - w / 2, y - w / 2, z, w, w, 0.8, _PERCEBE, semilla=1)


def _percebe(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs == tw // 2) & (ys == th // 2), 1, 3)
    return _imagen(_bisel(idx, 1, 1), PERCEBE), None


_percebe.__name__ = 'cap_percebe'
_PERCEBE = _percebe


# ======================================================================
#  SARGAZO, EL CAPITAN AHOGADO
# ======================================================================
def capitan(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    ar, te, cu = P['armadura'], P['tela'], P['cuero']
    I = np.eye(4)
    try:
        # las piernas, abiertas: la izquierda (la de +x) un poco adelantada
        for s, dz in ((-1, -1.0), (1, 1.5)):
            x = s * 6.5
            M = vr.T(x, 0.0, dz)
            bm.cubo(out, M, -4.0, 0.0, -4.0, 8.0, 10.0, 8.0, cu, semilla=1)                      # la cana de la bota
            bm.cubo(out, M, -4.0, 0.0, 3.6, 8.0, 3.4, 4.4, cu, semilla=1)                       # el pie, que sale delante
            bm.cubo(out, M, -3.2, 0.0, 7.8, 6.4, 2.4, 1.2, cu, semilla=1)
            Mv = M @ vr.T(0.0, 10.0, 0.0)
            bm.cubo(out, Mv, -5.4, 0.0, -5.4, 10.8, 3.4, 10.8, cu, semilla=2)                   # la vuelta, ancha
            bm.cubo(out, Mv, -5.5, 3.2, -5.5, 11.0, 0.7, 11.0, P['oro'], semilla=3)
            bm.cubo(out, M, -3.0, 4.6, 3.9, 6.0, 1.4, 0.4, P['cuero'], semilla=4)                # la correa con su hebilla
            bm.cubo(out, M, -0.9, 4.3, 4.2, 1.8, 2.0, 0.4, P['oro'], semilla=4)
            bm.cubo(out, M, -3.8, 13.0, -3.8, 7.6, 12.0, 7.6, ar, semilla=5)                     # la pierna
            bm.cubo(out, M, -4.4, 16.0, 2.4, 8.8, 4.6, 2.4, ar, semilla=6)                       # la rodillera
            coral(out, P, pt(M, (s * 3.8, 19.0, 0.0)), (s * 1.0, 0.8, -0.2), 4.0, semilla=7, ramas=2)
        # la cadera, el cinturon y la hebilla grande
        bm.cubo(out, I, -11.0, 22.0, -6.6, 22.0, 6.0, 13.2, ar, semilla=10)
        bm.cubo(out, I, -12.0, 25.0, -7.4, 24.0, 4.4, 14.8, cu, semilla=11)
        bm.cubo(out, I, -3.4, 24.4, 7.3, 6.8, 5.6, 1.0, P['hebilla'], semilla=12)
        # los faldones de la casaca: dos delante, abiertos, y los de atras, largos
        for s in (-1, 1):
            Mf = vr.T(s * 7.0, 26.0, 6.8) @ vr.Ry(s * 0.18) @ vr.Rx(0.12)
            bm.cubo(out, Mf, -4.6, -16.0, 0.0, 9.2, 16.0, 0.9, P['faldon'], semilla=13)
            Mf = vr.T(s * 5.6, 26.0, -7.2) @ vr.Ry(-s * 0.12) @ vr.Rx(-0.2)
            bm.cubo(out, Mf, -5.6, -20.0, -0.9, 11.2, 20.0, 0.9, P['faldon'], semilla=14)
            Mf = vr.T(s * 11.6, 26.0, 0.0) @ vr.Rz(s * 0.16)
            bm.cubo(out, Mf, -0.9 if s > 0 else 0.0, -17.0, -6.4, 0.9, 17.0, 12.8, P['faldon'], semilla=15)
        # el tronco: el peto de prismarina, la casaca abierta a los lados y los hombros
        bm.cubo(out, I, -11.0, 29.0, -6.8, 22.0, 20.0, 13.6, ar, semilla=20)
        bm.cubo(out, I, -9.0, 31.0, 6.6, 18.0, 15.0, 1.4, ar, semilla=21)                          # el peto, que sale
        for s in (-1, 1):                                                                       # las solapas de la casaca
            bm.cubo(out, I, s * 9.0 - 2.4, 29.0, 6.4, 4.8, 20.0, 1.6, te, semilla=22)
            bm.cubo(out, I, s * 9.0 + (1.8 if s < 0 else -2.6), 29.0, 7.9, 0.8, 20.0, 0.5, P['oro'], semilla=23)
            bm.cubo(out, I, s * 11.4 - 0.5, 29.0, -7.0, 1.4, 20.0, 14.0, te, semilla=24)
        bm.cubo(out, I, -11.6, 29.0, -7.6, 23.2, 20.0, 1.2, te, semilla=25)                          # la espalda de la casaca
        bm.cubo(out, I, -3.2, 38.0, 8.0, 6.4, 6.4, 1.0, P['hebilla'], semilla=26)                     # el broche del pecho
        for (a, b) in (((-10.0, 47.0), (9.0, 27.5)), ((10.0, 47.0), (-9.0, 27.5))):                 # las correas en aspa
            palo(out, (a[0], a[1], 8.3), (b[0], b[1], 8.3), 2.6, 0.8, cu, arriba=(0.0, 0.0, 1.0), semilla=27)
        for x, y in ((-5.0, 42.0), (5.0, 42.0), (-5.0, 33.0), (5.0, 33.0)):
            bm.cubo(out, I, x - 1.0, y - 1.0, 8.6, 2.0, 2.0, 0.6, P['oro'], semilla=28)
        percebes(out, P, I, -8.0, 8.0, 31.0, 45.0, 8.0, 6, semilla=29)
        bm.cubo(out, I, -4.0, 48.0, -3.6, 8.0, 3.4, 7.2, P['hueso'], semilla=30)                     # el cuello
        # las hombreras, con coral
        for s in (-1, 1):
            Mh = vr.T(s * 15.0, 46.0, 0.0) @ vr.Rz(-s * 0.18)
            bm.cubo(out, Mh, -5.6, -3.0, -6.0, 11.2, 7.0, 12.0, ar, semilla=31)
            bm.cubo(out, Mh, -5.9, -3.4, -6.3, 11.8, 1.0, 12.6, P['oro'], semilla=32)
            for i, (dx, dz) in enumerate(((-2.0, -2.0), (1.5, 1.0), (3.0, -3.0))):
                coral(out, P, pt(Mh, (dx * s, 4.0, dz)), (s * 0.4 + dx * 0.05, 1.0, dz * 0.08), 5.0 + i, semilla=33 + i)
        # el brazo derecho (-x), abajo, con la espada; el izquierdo (+x), en alto, con el arma de fuego
        ho_d, co_d, mu_d = np.array((-15.0, 43.0, 0.0)), np.array((-19.0, 32.0, 2.4)), np.array((-17.4, 22.0, 9.0))
        ho_i, co_i, mu_i = np.array((15.0, 43.0, 0.0)), np.array((23.0, 41.0, 4.0)), np.array((28.0, 42.0, 11.0))
        for ho, co, mu in ((ho_d, co_d, mu_d), (ho_i, co_i, mu_i)):
            palo(out, ho, co, 7.0, 7.0, ar, semilla=40)
            palo(out, co, mu, 6.6, 6.6, ar, semilla=41)
            caja(out, vr.T(*co), -3.8, 3.8, -3.8, 3.8, -3.8, 3.8, ar, semilla=42)
            Mp = palo(out, co + (mu - co) * 0.62, co + (mu - co) * 0.95, 8.8, 8.8, te, semilla=43)       # la bocamanga
            bm.cubo(out, Mp, -4.5, -4.5, 0.0, 9.0, 9.0, 0.8, P['oro'], semilla=44)
            Mm = palo(out, mu, mu + (mu - co) * 0.48, 5.6, 6.0, P['piel'], semilla=45)                    # la mano
        # la espada (o el ancla, o el sable)
        espada(out, P, V, mu_d)
        arma_alta(out, P, V, mu_i + np.array((1.6, 0.0, 2.2)), _u(np.array((0.62, 0.1, 0.78))))
        # la cabeza: la calavera, la quijada entreabierta y la barba de algas
        Mc = vr.T(0.0, 51.0, 0.6) @ vr.Rx(0.08)
        bm.cubo(out, Mc, -6.0, 3.0, -6.0, 12.0, 10.0, 12.0, P['hueso'], caras={'frente': P['calavera']}, semilla=50)
        bm.cubo(out, Mc, -5.0, -0.4, -4.4, 10.0, 3.6, 10.6, P['hueso'], caras={'frente': P['boca']}, semilla=51)
        rng = random.Random(4)
        for i, x in enumerate(np.linspace(-4.6, 4.6, 6)):                                               # la barba de algas
            L = rng.uniform(9.0, 14.0) - abs(x) * 0.3
            a = pt(Mc, (x, 0.2, 5.2))
            ps = [a, a + np.array((x * 0.25, -L * 0.4, 1.8)), a + np.array((x * 0.5, -L * 0.75, 1.2)),
                  a + np.array((x * 0.8 + (1.0 if i % 2 else -1.0), -L, 2.0))]
            for p0, p1 in zip(ps, ps[1:]):
                palo(out, p0, p1, 1.0, 0.6, P['alga'], arriba=(0.0, 0.0, 1.0), semilla=52)
        sombrero(out, P, V, Mc)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    ojos = pt(E @ Mc, (0.0, 8.0, 6.4))
    return out, {'ojos': ojos, 'luces': [pt(E @ Mc, (0.0, 4.0, 14.0))]}


def sombrero(out, P, V, Mc):
    """Lo de la cabeza: el tricornio (las tres alas dobladas hacia arriba, la punta delante, el emblema y el coral), el
    panuelo anudado con el aro de oro, o el bicornio de almirante con su penacho."""
    so = P['sombrero']
    if V['sombrero'] == 'tricornio':
        bm.cubo(out, Mc, -6.6, 12.0, -6.6, 13.2, 5.6, 13.2, so, semilla=60)                          # la copa
        Me = Mc @ vr.T(0.0, 13.2, 8.3) @ vr.Rx(-0.42)
        bm.cubo(out, Me, -4.2, 0.0, 0.0, 8.4, 6.4, 0.6, P['emblema'], semilla=60)                     # el emblema, delante
        for i in range(3):                                                                          # las tres alas
            g = TAU * i / 3
            Ma = Mc @ vr.T(0.0, 12.0, 0.0) @ vr.Ry(g + TAU / 6) @ vr.T(0.0, 0.0, 7.0) @ vr.Rx(-0.42)
            bm.cubo(out, Ma, -10.6, 0.0, -0.6, 21.2, 7.4, 1.2, so, semilla=61)
            bm.cubo(out, Ma, -10.8, 7.0, -0.7, 21.6, 0.8, 1.4, P['oro'], semilla=61)
        coral(out, P, pt(Mc, (-4.0, 16.0, -3.0)), (-0.5, 1.0, -0.3), 6.0, semilla=62)
        coral(out, P, pt(Mc, (4.6, 15.4, 1.0)), (0.7, 1.0, 0.1), 5.0, semilla=63, ramas=2)
    elif V['sombrero'] == 'panuelo':
        bm.cubo(out, Mc, -6.4, 9.0, -6.4, 12.8, 4.6, 12.8, P['tela'], semilla=60)                     # el panuelo
        Mn = Mc @ vr.T(0.0, 11.0, -6.6)
        bm.cubo(out, Mn, -1.6, -1.6, -1.6, 3.2, 3.2, 1.8, P['tela'], semilla=61)                     # el nudo
        for s in (-1, 1):
            palo(out, pt(Mn, (s * 0.8, -0.6, -1.4)), pt(Mn, (s * 3.0, -9.0, -3.2)), 2.4, 0.8, P['tela'], semilla=62)
        caja(out, Mc @ vr.T(-6.4, 4.0, 0.0), -0.5, 0.5, -2.4, 0.4, -1.4, 1.4, P['oro'], semilla=63)    # el aro
        coral(out, P, pt(Mc, (3.0, 13.4, -2.0)), (0.5, 1.0, -0.4), 5.0, semilla=64)
    else:
        Mb = Mc @ vr.T(0.0, 12.0, 0.0)
        bm.cubo(out, Mb, -6.4, 0.0, -6.4, 12.8, 3.0, 12.8, P['sombrero'], semilla=60)
        bm.cubo(out, Mb, -14.0, 0.0, -1.6, 28.0, 7.0, 3.2, P['sombrero'], semilla=61)                # las dos puntas, de lado
        bm.cubo(out, Mb, -10.0, 7.0, -1.4, 20.0, 2.4, 2.8, P['sombrero'], semilla=61)
        bm.cubo(out, Mb, -14.2, -0.4, -1.8, 28.4, 0.8, 3.6, P['oro'], semilla=62)
        bm.cubo(out, Mb, -2.0, 2.0, 1.6, 4.0, 4.0, 0.6, P['hebilla'], semilla=63)
        for i in range(7):                                                                          # el penacho blanco
            g = -0.9 + 1.8 * i / 6
            a = pt(Mb, (0.0, 8.0, 0.0))
            palo(out, a, a + np.array((math.sin(g) * 6.0, 6.0 + math.cos(g) * 3.0, -2.0)), 2.0, 0.8, P['penacho'],
                 arriba=(0.0, 0.0, 1.0), semilla=64)


def espada(out, P, V, mano):
    """El arma de la mano derecha, que sube cruzada hacia fuera: la espada de pez sierra (la hoja de hueso con los dientes
    por los dos cantos), el ancla, o el sable de nacar."""
    d = _u(np.array((-0.55, 0.78, 0.3)))
    lado = _u(np.cross(d, (0.0, 0.0, 1.0)))
    base = mano + d * 1.0
    palo(out, base - d * 6.0, base + d * 1.5, 2.2, 2.2, P['madera'] if V['arma'] != 'ancla' else P['hierro'], semilla=70)
    if V['arma'] == 'ancla':
        top = base + d * 30.0
        palo(out, base, top, 2.6, 2.6, P['hierro'], semilla=71)
        palo(out, top - d * 4.0 - lado * 6.0, top - d * 4.0 + lado * 6.0, 2.2, 2.2, P['hierro'], semilla=72)   # el cepo
        cab = base + d * 2.0
        for s in (-1, 1):                                                                       # los brazos curvos del ancla
            p1 = cab + lado * s * 6.0 - d * 1.0
            p2 = p1 + lado * s * 2.0 + d * 5.0
            palo(out, cab, p1, 2.6, 2.6, P['hierro'], semilla=73)
            palo(out, p1, p2, 2.4, 2.4, P['hierro'], semilla=73)
            palo(out, p2, p2 + d * 2.0 - lado * s * 1.4, 1.4, 3.6, P['hierro'], semilla=74)
        coral(out, P, top - d * 10.0, lado + d * 0.3, 5.0, semilla=75, ramas=2)
        return
    palo(out, base + d * 1.5 - lado * 6.0, base + d * 1.5 + lado * 6.0, 2.4, 2.0, P['oro'], semilla=76)       # la guarda
    if V['arma'] == 'sable':
        p, tramo = base + d * 2.5, []
        for k in range(8):                                                                      # la hoja curva, de nacar
            q = p + _u(d + lado * 0.07 * k) * 4.0
            tramo.append((p, q))
            p = q
        for i, (a, b) in enumerate(tramo):
            palo(out, a, b, 3.6 - i * 0.3, 0.9, P['sierra'], arriba=np.cross(lado, d), semilla=77)
        return
    L = 40.0
    tip = base + d * (2.0 + L)
    n = 10
    for i in range(n):                                                                          # la hoja del pez sierra
        a = base + d * (2.0 + L * i / n)
        b = base + d * (2.0 + L * (i + 1) / n)
        w = 6.4 - 2.6 * i / n
        palo(out, a, b, w, 1.4, P['sierra'], arriba=np.cross(lado, d), semilla=78)
        for s in (-1, 1):                                                                       # los dientes, por los dos cantos
            ca, cb = a + lado * s * w / 2, b + lado * s * w / 2
            lamina(out, (ca, cb, cb + lado * s * 2.0, ca + lado * s * 2.0) if s > 0 else (cb, ca, ca + lado * s * 2.0, cb + lado * s * 2.0),
                   P['dientes'], float(np.linalg.norm(cb - ca)), 2.0, semilla=79)


def arma_alta(out, P, V, mano, apunta):
    """Lo que alza en la mano izquierda: el trabuco (culata de madera, canon de hierro con boca de campana y anillos de
    oro), el arpon (el canon y la punta de hierro con su cuerda) o el farol encendido."""
    if V['mano'] == 'farol':
        Mf = vr.T(*(mano + np.array((0.0, -14.0, 0.0))))                                    # el farol cuelga de la mano
        caja(out, Mf, -0.4, 0.4, 12.4, 15.0, -0.4, 0.4, P['hierro'], semilla=80)
        caja(out, Mf, -3.0, 3.0, 3.0, 4.0, -3.0, 3.0, P['oro'], semilla=81)
        caja(out, Mf, -2.4, 2.4, 4.0, 10.0, -2.4, 2.4, P['luz'], semilla=82)
        for x, z in ((-2.6, -2.6), (2.6, -2.6), (-2.6, 2.6), (2.6, 2.6)):
            caja(out, Mf, x - 0.4, x + 0.4, 4.0, 10.0, z - 0.4, z + 0.4, P['oro'], semilla=83)
        caja(out, Mf, -3.0, 3.0, 10.0, 11.0, -3.0, 3.0, P['oro'], semilla=84)
        caja(out, Mf, -1.6, 1.6, 11.0, 12.4, -1.6, 1.6, P['oro'], semilla=84)
        return
    culata = mano - apunta * 9.0 + np.array((0.0, -3.4, 0.0))
    palo(out, culata, mano + apunta * 3.0, 2.6, 4.2, P['madera'], semilla=85)
    palo(out, culata - np.array((0.0, 0.6, 0.0)), culata + apunta * 3.0 - np.array((0.0, 0.6, 0.0)), 3.0, 5.4, P['madera'],
         semilla=85)
    boca = mano + apunta * 24.0
    palo(out, mano + apunta * 2.0, boca, 1.8, 1.8, P['hierro'], semilla=86)
    for t in (0.2, 0.55, 0.85):
        q = mano + apunta * 24.0 * t
        palo(out, q, q + apunta * 0.8, 2.6, 2.6, P['oro'], semilla=87)
    if V['mano'] == 'arpon':
        palo(out, boca, boca + apunta * 6.0, 1.2, 1.2, P['hierro'], semilla=88)
        lado = _u(np.cross(apunta, (0.0, 1.0, 0.0)))
        for s in (-1, 1):
            palo(out, boca + apunta * 6.0, boca + apunta * 3.0 + lado * s * 2.2, 1.0, 1.0, P['hierro'], semilla=89)
        palo(out, boca + apunta * 6.0, boca + apunta * 9.0, 1.4, 1.4, P['hierro'], semilla=89)
    else:
        palo(out, boca, boca + apunta * 1.2, 2.8, 2.8, P['oro'], semilla=88)                     # la boca de campana
        palo(out, boca + apunta * 1.2, boca + apunta * 2.2, 4.0, 4.0, P['oro'], semilla=88)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
