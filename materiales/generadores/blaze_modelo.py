"""
El Blaze rediseñado (15-10-2026, tercera vuelta). Las dos primeras no valieron. Juan paso dos referencias: «a lo que me
refiero con redisenar al blaze y se vea mas intimidante, me referia a esto; ahora si, con esto creame 3 blazes».

En las referencias el Blaze sigue siendo un Blaze (la cabeza de bloque que flota, el fuego, lo que gira alrededor),
pero las varas se convierten en algo grande que flota: espadas de fuego apuntando abajo, o tablillas con runas
encendidas. La cabeza lleva cuernos y el cuerpo es una columna solida que brilla. Tres blazes con esa idea:

    A  el de las Espadas    (la primera referencia) rojo y naranja: la cabeza en bandas con dos cuernos de punta
                            amarilla y los ojos y la boca en rayas amarillas; cuatro espadas de fuego que flotan con la
                            punta abajo (dos grandes fuera y dos pequenas dentro), con el pomo y la guarda en uve con su
                            gema, el puno a rayas y la hoja amarilla con el canto rojo y los bordes dentados; y dos varas
                            grandes delante
    B  el de las Tablillas  (la segunda referencia) de carbon con las brasas naranjas: la cabeza alta con dos cuernos
                            largos, los ojos y la gema morados y la cara encendida por abajo; el nucleo morado en el
                            pecho; tres tablillas que flotan alrededor, encendidas, con una runa oscura en medio
    C  el de las Lanzas     (nuestro, con la misma idea) de ceniza y fuego de alma: la cabeza con los cuernos echados
                            atras; seis lanzas de hierro que flotan de pie en corona, con la punta en hoja de fuego azul

Se modela como un mob: en pixeles del modelo con un texel por pixel (como las referencias), y luego se agranda.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import lamina
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 1


def _h(*cs):
    return [nm._hex(c) for c in cs]


VARIANTES = {
    'A': dict(clave='BEA', nombre='el de las Espadas', corto='espadas', escala=1.25,
              piel=_h('3a0806', '5a0c0a', '8e1a12', 'c0301c', 'e8601a'),
              brasa=_h('e8601a', 'ffb21a', 'ffd23a', 'fff2a0'),
              ojo=_h('ffd23a', 'fff2a0'), gema=_h('ffd23a', 'fff2a0'),
              luz='ffa81a'),
    'B': dict(clave='BEB', nombre='el de los Cristales', corto='tablillas', escala=1.35,
              piel=_h('0c0808', '140e0e', '1e1616', '2a1e1c', '3a2a26'),
              brasa=_h('c04a0a', 'ff9a1a', 'ffd04a', 'fff2a0'),
              ojo=_h('ff3ad8', 'ffb2f0'), gema=_h('c02ad0', 'ff7af0'),
              luz='ff9a1a'),
    'C': dict(clave='BEC', nombre='el de las Lanzas', corto='lanzas', escala=1.35,
              piel=_h('121418', '1c2026', '282e36', '363e48', '485260'),
              brasa=_h('1a6ad0', '3ad8ff', 'aef6ff', 'f0ffff'),
              ojo=_h('3ad8ff', 'f0ffff'), gema=_h('3ad8ff', 'f0ffff'),
              luz='3ad8ff'),
}

ROJO = _h('5a0c0a', '8e1a12', 'c0301c', 'e8601a', 'ffb21a', 'ffd23a', 'fff2a0')
HIERRO = _h('16181c', '22262c', '30363e', '424a54', '5a6470')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _mota(x, y, s, n):
    """Un indice de moteado fijo por pixel (0..n-1), sin ruido suelto: en manchitas de dos pixeles."""
    return ((x // 2) * 7 + (y // 2) * 13 + s * 5 + ((x // 2) * (y // 2)) % 3) % n


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    piel, brasa, ojo, gema = V['piel'], V['brasa'], V['ojo'], V['gema']
    tipo = V['corto']

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'be%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def lienzo(tw, th, cara, s):
        """La piel de cada uno: en el de las Espadas, rojo en bandas (como la cabeza de la referencia); en los otros, el
        tono oscuro moteado con alguna brasa que brilla."""
        t = np.zeros((th, tw, 4), np.uint8)
        e = np.zeros((th, tw), bool)
        for y in range(th):
            for x in range(tw):
                m = _mota(x, y, s, 6)
                if tipo == 'espadas':
                    banda = (y // 2) % 3 == 2
                    c = piel[1] if banda else (piel[2] if m < 4 else piel[3])
                    if m == 5 and not banda:
                        c = piel[4]
                else:
                    c = piel[2] if m < 3 else (piel[1] if m < 5 else piel[3])
                    if (x * 3 + y * 5 + s) % 23 == 0:
                        c = brasa[1]
                        e[y, x] = True
                t[y, x] = (*c, 255)
        if cara == 'arriba':
            t[..., :3] = np.minimum(255, t[..., :3].astype(int) + 18).astype(np.uint8)
        elif cara == 'abajo':
            t[..., :3] = (t[..., :3].astype(int) * 0.7).astype(np.uint8)
        return t, e

    def piel_p(tw, th, cara, s):
        t, e = lienzo(tw, th, cara, s)
        return t, (_emis(t, e, 255) if e.any() else None)
    reg('piel', piel_p)

    def cara(tw, th, cara_, s):
        """La cara de cada uno."""
        t, e = lienzo(tw, th, 'frente', s)
        cx = tw / 2
        if tipo == 'espadas':                                       # el ceno en uve, los ojos rasgados y los dientes
            ey = int(th * 0.42)
            for x in range(tw):                                      # el ceno: baja hacia el medio
                yb = ey - 2 + int(round(max(0.0, 1.6 - abs(x + 0.5 - cx) * 0.45)))
                t[max(0, yb), x] = (*piel[0], 255)
                t[max(0, yb - 1), x] = (*piel[1], 255)
            for lado in (-1, 1):
                for i, f in enumerate((0.0, 1.0, 2.0)):              # el ojo: tres pixeles, la punta de dentro mas baja
                    x = int(round(cx + lado * (1.0 + f))) - (1 if lado < 0 else 0)
                    y = ey + (1 if i == 0 else 0)
                    t[y, x] = (*ojo[1 if i == 1 else 0], 255)
                    e[y, x] = True
                    t[y + 1, x] = (*piel[0], 255)                     # la sombra de la cuenca
            for x in range(1, tw - 1):                               # los dientes de arriba, en la ultima fila
                if x in (2, tw - 3):
                    t[th - 3:th, x] = (*brasa[3], 255)               # los colmillos, mas largos
                elif x % 2 == 0:
                    t[th - 2:th, x] = (*brasa[2], 255)
                else:
                    t[th - 2:th, x] = (*piel[0], 255)
        elif tipo == 'tablillas':                                   # la gema, los ojos morados y el fuego de abajo
            gy = int(th * 0.15)
            x0 = tw // 2 - 1
            for x, y, c in ((x0, gy, 0), (x0 + 1, gy, 0), (x0, gy + 1, 1), (x0 + 1, gy + 1, 0), (x0, gy + 2, 0),
                            (x0 + 1, gy + 2, 0)):
                t[y, x] = (*gema[c], 255)
                e[y, x] = True
            ey = int(th * 0.45)
            for x0 in (1, tw - 3):
                for x in (x0, x0 + 1):
                    t[ey, x] = (*ojo[0], 255)
                    t[ey + 1, x] = (*brasa[1], 255)
                    e[ey:ey + 2, x] = True
            rng = random.Random(s)
            for x in range(tw):                                      # las lenguas de fuego que suben desde abajo
                alto = rng.choice((2, 3, 3, 4)) if 0 < x < tw - 1 else 1
                for j in range(alto):
                    y = th - 1 - j
                    t[y, x] = (*brasa[2 if j == 0 else 1], 255)
                    e[y, x] = True
        else:                                                        # cuatro ojos rasgados, el ceno de hueso y los dientes
            for ey, ancho in ((int(th * 0.3), 3), (int(th * 0.52), 2)):
                for lado in (-1, 1):
                    for i in range(ancho):
                        x = int(round(cx + lado * (1.0 + i))) - (1 if lado < 0 else 0)
                        y = ey + (1 if i == 0 else 0)
                        t[y, x] = (*ojo[1 if i == 0 else 0], 255)
                        e[y, x] = True
                        t[max(0, y - 1), x] = (*piel[0], 255)
            for y in range(int(th * 0.3) - 2, th - 3):               # la cresta de hueso en medio de la frente
                t[y, int(cx) - 1:int(cx) + 1] = (*piel[4], 255)
            for x in range(1, tw - 1):                               # los dientes de arriba, desiguales
                largo = 3 if x in (2, tw - 3, int(cx)) else 2
                if x % 2 == 0 or largo == 3:
                    t[th - largo:th, x] = (*piel[4], 255)
                    t[th - 1, x] = (*brasa[1], 255)
                    e[th - 1, x] = True
                else:
                    t[th - 2:th, x] = (*piel[0], 255)
        return t, _emis(t, e, 255)
    reg('cara', cara)

    def vara(tw, th, cara_, s):
        """Las varas grandes del de las Espadas: moteadas de rojo, naranja y amarillo, como las de la referencia."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            for x in range(tw):
                m = _mota(x, y, s, 7)
                t[y, x] = (*ROJO[[1, 2, 2, 3, 3, 4, 5][m]], 255)
        return t, _emis(t, t[..., 0] > 230, 140)
    reg('vara', vara)

    def cuerno(tw, th, cara_, s):
        """El cuerno: del color de la piel, con la punta (arriba) de brasa."""
        t, e = lienzo(tw, th, cara_, s)
        if cara_ not in ('arriba', 'abajo'):
            t[0:max(1, th // 3), :] = (*brasa[1], 255)
            e[0:max(1, th // 3), :] = True
        elif cara_ == 'arriba':
            t[...] = (*brasa[2], 255)
            e[...] = True
        return t, _emis(t, e, 255)
    reg('cuerno', cuerno)

    def nucleo(tw, th, cara_, s):
        """El nucleo del pecho: la gema que arde."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*gema[0], 255)
        t[(abs(xs - (tw - 1) / 2) < tw * 0.25) & (abs(ys - (th - 1) / 2) < th * 0.25)] = (*gema[1], 255)
        return t, None
    reg('nucleo', nucleo, pleno=True)

    def llama(tw, th, cara_, s):
        """La llama, en hoja: lenguas que suben, claras por dentro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th
        u = (xs + 0.5) / tw
        alto = 0.4 + 0.6 * np.abs(np.cos(u * math.pi * 1.5 + s * 0.7)) ** 0.7
        dentro = f < alto
        img = np.zeros((th, tw, 4), np.uint8)
        img[dentro] = (*brasa[1], 255)
        img[dentro & (f < alto * 0.5) & (abs(u - 0.5) < 0.3)] = (*brasa[2], 255)
        img[dentro & (f > alto - 0.18)] = (*brasa[0], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, None
    reg('llama', llama, pleno=True)

    # ---- las espadas
    def hoja_espada(tw, th, cara_, s):
        """La hoja de la espada (la empunadura arriba y la punta abajo): amarilla en el centro, naranja y roja hacia el
        canto, con el vaciado rojo cerca de la guarda y los bordes dentados como llamas."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t_ = (ys + 0.5) / th                                     # 0 en la guarda, 1 en la punta
        c = (tw - 1) / 2
        w = (tw / 2) * np.where(t_ < 0.8, 0.82 + 0.18 * ((ys // 3) % 2), 0.82 * (1 - (t_ - 0.8) / 0.2))
        w = np.where(t_ < 0.08, tw / 2 * 0.7, w)
        d = abs(xs - c) / np.maximum(w, 0.5)
        dentro = d <= 1.0
        img = np.zeros((th, tw, 4), np.uint8)
        img[dentro] = (*ROJO[3], 255)
        img[dentro & (d < 0.75)] = (*ROJO[4], 255)
        img[dentro & (d < 0.45)] = (*ROJO[5], 255)
        img[dentro & (d < 0.12) & (t_ > 0.45)] = (*ROJO[6], 255)
        img[dentro & (d > 0.9)] = (*ROJO[2], 255)
        vaciado = dentro & (d < 0.2) & (t_ < 0.35)
        img[vaciado] = (*ROJO[1], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        img[dentro & (d > 0.9) & (((ys // 3) % 2) == 0) & (t_ < 0.8)] = (*ROJO[1], 255)
        return img, _emis(img, dentro & ~vaciado & (d < 0.5), 120)
    reg('hoja_espada', hoja_espada)

    def guarda(tw, th, cara_, s):
        """La guarda y el pomo: rojo oscuro con el canto claro y, por delante, la gema en rombo."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            for x in range(tw):
                t[y, x] = (*ROJO[[0, 1, 1, 2][_mota(x, y, s, 4)]], 255)
        t[0, :] = (*ROJO[2], 255)
        e = np.zeros((th, tw), bool)
        if cara_ in ('frente', 'atras') and tw >= 3 and th >= 3:
            cx, cy = (tw - 1) / 2, (th - 1) / 2
            ys, xs = np.mgrid[0:th, 0:tw]
            rombo = (abs(xs - cx) / max(tw * 0.18, 0.6) + abs(ys - cy) / max(th * 0.32, 0.6)) <= 1.0
            t[rombo] = (*ROJO[5], 255)
            e = rombo
        return t, (_emis(t, e, 255) if e.any() else None)
    reg('guarda', guarda)

    def puno(tw, th, cara_, s):
        """El puno: a rayas amarillas y naranjas, de traves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = ys if cara_ not in ('arriba', 'abajo') else xs
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*ROJO[3], 255)
        t[(a % 3) == 0] = (*ROJO[5], 255)
        t[(a % 3) == 1] = (*ROJO[4], 255)
        return t, _emis(t, (a % 3) == 0, 160)
    reg('puno', puno)

    # ---- las tablillas
    def tablilla(tw, th, cara_, s):
        """La cara de la tablilla: el marco oscuro, el fondo encendido (amarillo en el centro y naranja hacia el borde,
        moteado), una runa oscura en medio y cuadritos en las esquinas."""
        t = np.zeros((th, tw, 4), np.uint8)
        e = np.zeros((th, tw), bool)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        for y in range(th):
            for x in range(tw):
                if x == 0 or y == 0 or x == tw - 1 or y == th - 1:
                    t[y, x] = (*piel[1], 255)
                    continue
                d = max(abs(x - cx) / (tw / 2), abs(y - cy) / (th / 2))
                m = _mota(x, y, s, 5)
                c = brasa[2] if d < 0.45 and m < 3 else brasa[1] if d < 0.8 else brasa[0]
                if d > 0.82 and m < 2:
                    c = brasa[0]
                t[y, x] = (*c, 255)
                e[y, x] = True
        # la runa: un tronco con dos brazos en cruz que bajan, la cabeza de dos cuernos y las patas abiertas
        runa = []
        h = th // 2
        y0 = int(cy - h / 2)
        xc = int(cx)
        for y in range(y0 + 2, y0 + h - 2):
            runa.append((xc, y))
        for i in range(3):
            runa += [(xc - 1 - i, y0 + 4 + i), (xc + 1 + i, y0 + 4 + i)]
        runa += [(xc - 3, y0 + 7), (xc + 3, y0 + 7), (xc - 3, y0 + 8), (xc + 3, y0 + 8)]
        runa += [(xc - 1, y0 + 1), (xc + 1, y0 + 1), (xc - 2, y0), (xc + 2, y0)]
        for i in range(3):
            runa += [(xc - 1 - i, y0 + h - 2 + i), (xc + 1 + i, y0 + h - 2 + i)]
        for x, y in runa:
            if 1 <= x < tw - 1 and 1 <= y < th - 1:
                t[y, x] = (*piel[1], 255)
                e[y, x] = False
        for x, y in ((2, 2), (tw - 3, 2), (2, th - 3), (tw - 3, th - 3)):
            t[y, x] = (*piel[1], 255)
            e[y, x] = False
        return t, _emis(t, e, 150)
    reg('tablilla', tablilla)

    def canto(tw, th, cara_, s):
        t, _ = lienzo(tw, th, cara_, s)
        return t, None
    reg('canto', canto)

    # ---- las lanzas
    def asta(tw, th, cara_, s):
        """El asta de hierro, con anillos que brillan del fuego de alma."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = ys if cara_ not in ('arriba', 'abajo') else xs
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*HIERRO[2], 255)
        t[(xs == 0)] = (*HIERRO[3], 255)
        anillo = (a % 9) == 0
        t[anillo] = (*brasa[1], 255)
        return t, _emis(t, anillo, 255)
    reg('asta', asta)

    def punta(tw, th, cara_, s):
        """La punta de la lanza, en hoja (la base abajo): una hoja de hierro con el filo de fuego de alma."""
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th                                   # 0 en la base, 1 en la punta
        c = (tw - 1) / 2
        w = (tw / 2) * np.where(f < 0.35, 0.4 + f / 0.35 * 0.6, 1.0 - (f - 0.35) / 0.65)
        d = abs(xs - c) / np.maximum(w, 0.4)
        dentro = d <= 1.0
        img = np.zeros((th, tw, 4), np.uint8)
        img[dentro] = (*HIERRO[3], 255)
        filo = dentro & (d > 0.6)
        img[filo] = (*brasa[1], 255)
        img[dentro & (d < 0.2)] = (*brasa[2], 255)
        img[..., 3] = np.where(dentro, 255, 0)
        return img, _emis(img, filo | (dentro & (d < 0.2)), 255)
    reg('punta', punta)

    def boca(tw, th, cara_, s):
        """El fuego de dentro de la boca."""
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*brasa[1], 255)
        t[(ys + xs) % 3 == 0] = (*brasa[2], 255)
        return t, None
    reg('boca', boca, pleno=True)

    def quijada(tw, th, cara_, s):
        """La quijada: la piel, y por delante los dientes de abajo en la primera fila (los colmillos de las esquinas,
        mas largos)."""
        t, e = lienzo(tw, th, cara_, s + 4)
        if cara_ == 'frente':
            for x in range(1, tw - 1):
                if x in (1, tw - 2):
                    t[0:2, x] = (*(piel[4] if tipo == 'lanzas' else brasa[3]), 255)
                elif x % 2 == 1:
                    t[0, x] = (*(piel[4] if tipo == 'lanzas' else brasa[2]), 255)
        return t, (_emis(t, e, 255) if e.any() else None)
    reg('quijada', quijada)

    def colmillo(tw, th, cara_, s):
        """El colmillo, en hoja (la base abajo y la punta arriba)."""
        t = np.zeros((th, tw, 4), np.uint8)
        claro = piel[4] if tipo == 'lanzas' else brasa[3]
        for y in range(th):
            w = tw * (y + 1) / th
            a, b = (tw - w) / 2, (tw + w) / 2
            for x in range(int(math.floor(a)), min(tw, int(math.ceil(b)))):
                t[y, x] = (*(claro if x < tw / 2 else piel[3]), 255)
        return t, None
    reg('colmillo', colmillo)

    CRISTAL = _h('120c2c', '20164c', '30226c', '44308e', '5c42ae', '7c5ec8', 'a688e0', 'dcccfa')

    def cristal_nivel(nivel):
        base = (4, 4, 5, 5)[nivel]

        def f(tw, th, cara_, s):
            """El cristal, como una amatista de verdad: cada cara lisa, de un solo morado frio (que no se vuelve rosa con
            la luz roja de la fortaleza), con los dos filos mas claros, que es donde pega la luz en una gema; las caras
            se distinguen por la luz que les da, y las puntas son un tono mas claras y brillan algo mas."""
            xs = np.mgrid[0:th, 0:tw][1]
            idx = np.full((th, tw), base)
            if cara_ in ('arriba', 'abajo'):
                idx = idx + (1 if cara_ == 'arriba' else -1)
            elif tw >= 3:
                idx = np.where((xs == 0) | (xs == tw - 1), base + 1, idx)       # los filos, claros
            elif tw == 2:
                idx = np.where(xs == 0, base + 1, idx)
            t = np.zeros((th, tw, 4), np.uint8)
            for k, c in enumerate(CRISTAL):
                t[idx == k] = (*c, 255)
            return t, _emis(t, idx >= 4, 60 + 20 * nivel)
        return f
    for n in range(4):
        reg('cristal%d' % n, cristal_nivel(n))

    def hierro(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*HIERRO[3], 255)
        t[0, :] = (*HIERRO[4], 255)
        return t, None
    reg('hierro', hierro)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def marco_y(p, d, frente=(0.0, 0.0, 1.0)):
    """Un marco en p con el eje y hacia d."""
    y = _u(d)
    f = np.asarray(frente, float)
    if abs(f @ y) > 0.95:
        f = np.array((1.0, 0.0, 0.0))
    x = _u(np.cross(y, f))
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


def barra(out, pin, abajo, arriba, ancho, fondo=None, frente=(0.0, 0.0, 1.0), caras=None, semilla=0):
    """Una caja de abajo arriba (con el eje y a lo largo), de seccion ancho x fondo."""
    abajo, arriba = np.asarray(abajo, float), np.asarray(arriba, float)
    L = float(np.linalg.norm(arriba - abajo))
    M = marco_y(abajo, arriba - abajo, frente)
    f = ancho if fondo is None else fondo
    bm.cubo(out, M, -ancho / 2, 0.0, -f / 2, ancho, L, f, pin, caras=caras, semilla=semilla)
    return M


def hoja(out, P4, pintor, ancho, alto, semilla=0):
    a, b, c, d = [np.asarray(p, float) for p in P4]
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def llama(out, P, base, ancho, alto, giro, semilla=0):
    base = np.asarray(base, float)
    for g in (giro, giro + math.pi / 2):
        l = np.array((math.cos(g), 0.0, math.sin(g))) * ancho / 2
        sube = np.array((0.0, alto, 0.0))
        hoja(out, (base - l, base + l, base + l + sube, base - l + sube), P['llama'], ancho, alto, semilla)


def cuerpo(out, P, V, alto_cabeza=10.0):
    """La cabeza de bloque con su cara, el cuello, la columna del cuerpo que brilla (el pecho, el vientre y la cola que se
    afina) y el fuego de abajo. Devuelve el centro de la cara y el nucleo."""
    pi = P['piel']
    H = 44.0
    boca = V['corto'] in ('espadas', 'lanzas')
    caras_cabeza = {'frente': P['cara'], 'abajo': P['boca']} if boca else {'frente': P['cara']}
    bm.cubo(out, vr.T(0.0, H, 0.0), -5.0, -5.0, -5.0, 10.0, alto_cabeza, 10.0, pi, caras=caras_cabeza, semilla=1)
    if boca:                                                                                        # la quijada, abierta
        Mj = vr.T(0.0, H - 5.0, -4.6) @ vr.Rx(0.5)
        bm.cubo(out, Mj, -4.6, -3.0, 0.0, 9.2, 3.0, 9.6, P['quijada'], caras={'arriba': P['boca']}, semilla=8)
        for sx in (-1, 1):                                                                          # los colmillos de abajo
            b = pt(Mj, (sx * 3.6, 0.0, 9.0))
            arriba_j = Mj[:3, :3] @ np.array((0.0, 1.0, 0.0))
            for ll in (np.array((1.0, 0.0, 0.0)), np.array((0.0, 0.0, 1.0))):
                hoja(out, (b - ll * 0.8, b + ll * 0.8, b + ll * 0.1 + arriba_j * 4.2, b - ll * 0.1 + arriba_j * 4.2),
                     P['colmillo'], 1.6, 4.2, semilla=9)
    barra(out, pi, (0.0, H - 8.0, 0.0), (0.0, H - 5.0, 0.0), 3.0, semilla=2)                       # el cuello
    barra(out, pi, (0.0, H - 15.0, 0.0), (0.0, H - 8.0, 0.0), 9.0, 6.0, semilla=3)                # el pecho
    for sx in (-1, 1):                                                                              # los hombros
        bm.cubo(out, vr.T(sx * 5.6, H - 11.0, 0.0), -2.4, -2.4, -2.6, 4.8, 4.8, 5.2, pi, semilla=4)
    if V['corto'] == 'tablillas':
        bm.cubo(out, vr.T(0.0, H - 12.0, 3.0), -1.8, -1.8, 0.0, 3.6, 3.6, 0.6, P['nucleo'], semilla=4)
    barra(out, pi, (0.0, H - 25.0, 0.0), (0.0, H - 15.0, 0.0), 6.0, 4.4, semilla=5)              # el vientre
    barra(out, pi, (0.0, H - 33.0, -0.6), (0.0, H - 25.0, 0.0), 4.0, 3.2, semilla=6)            # la cola
    for g in (0.0, 2.1, 4.2):
        llama(out, P, np.array((math.cos(g) * 1.2, H - 39.0, math.sin(g) * 1.2 - 0.6)), 3.2, 7.0, g, semilla=7)
    return np.array((0.0, H, 5.0)), np.array((0.0, H - 12.0, 0.0))


def cuernos(out, P, V, H=44.0, alto_cabeza=10.0):
    """Los cuernos de cada uno: cortos y de punta de brasa (Espadas), largos en punta (Tablillas) o echados atras
    (Lanzas)."""
    arriba = H - 5.0 + alto_cabeza
    for s in (-1, 1):
        if V['corto'] == 'espadas':
            pts = [(s * 3.4, arriba - 0.5, 0.0), (s * 3.8, arriba + 3.6, 0.0), (s * 3.6, arriba + 6.6, 0.4)]
            gruesos = (3.0, 2.6)
        elif V['corto'] == 'tablillas':
            pts = [(s * 3.2, arriba - 0.5, -0.5), (s * 3.8, arriba + 6.0, -0.8), (s * 3.2, arriba + 12.0, -1.0),
                   (s * 2.4, arriba + 16.0, -1.0)]
            gruesos = (3.0, 2.2, 1.2)
        else:
            pts = [(s * 4.0, arriba - 1.5, 0.0), (s * 5.8, arriba + 1.4, -3.4), (s * 6.4, arriba + 2.2, -8.0),
                   (s * 5.6, arriba + 1.0, -12.0)]
            gruesos = (3.0, 2.4, 1.4)
        for j, g in enumerate(gruesos):
            a, b = np.array(pts[j]), np.array(pts[j + 1])
            if a[1] > b[1]:
                a, b = b, a
            barra(out, P['cuerno'], a, b, g, semilla=10 + j)


# ======================================================================
#  A · EL DE LAS ESPADAS
# ======================================================================
def espada(out, P, tope, largo_hoja, ancho_hoja, fuera=(0.0, 0.0, 1.0), semilla=0):
    """Una espada que flota con la punta abajo, con la cara de la hoja hacia 'fuera': el pomo con la gema, el puno a
    rayas, la guarda en uve con la gema y la hoja de fuego (dos hojas con un nervio en medio)."""
    tope = np.asarray(tope, float)
    fuera = _u(np.asarray(fuera, float))
    abajo = _u(np.array((0.0, -1.0, 0.0)) + fuera * 0.06)
    lado = _u(np.cross(abajo, fuera))
    k = ancho_hoja / 7.0
    pomo = tope + abajo * 1.6 * k
    bm.cubo(out, marco_y(pomo, -abajo, fuera), -1.6 * k, -1.6 * k, -1.6 * k, 3.2 * k, 3.2 * k, 3.2 * k, P['guarda'],
            semilla=semilla)
    g0 = tope + abajo * 3.2 * k
    g1 = g0 + abajo * 7.0 * k
    barra(out, P['puno'], g1, g0, 2.2 * k, frente=fuera, semilla=semilla + 1)
    centro = g1 + abajo * 1.4 * k                                    # la guarda: el centro y dos alas que suben
    bm.cubo(out, marco_y(centro - abajo * 1.4 * k, -abajo, fuera), -2.2 * k, 0.0, -1.4 * k, 4.4 * k, 3.4 * k, 2.8 * k,
            P['guarda'], semilla=semilla + 2)
    for sg in (-1, 1):
        a = centro + lado * sg * 1.6 * k
        b = a + lado * sg * 4.6 * k - abajo * 2.6 * k
        barra(out, P['guarda'], a, b, 2.2 * k, frente=fuera, semilla=semilla + 3)
    raiz = centro + abajo * 1.6 * k
    punta = raiz + abajo * largo_hoja
    w = ancho_hoja / 2
    hoja(out, (punta - lado * w, punta + lado * w, raiz + lado * w, raiz - lado * w), P['hoja_espada'], ancho_hoja, largo_hoja,
         semilla=semilla + 4)
    barra(out, P['guarda'], raiz + abajo * largo_hoja * 0.4, raiz, 1.2 * k, 1.6 * k, frente=fuera, semilla=semilla + 5)


def espadas(out, P, V):
    """Seis espadas de fuego que giran alrededor, en corona: tres grandes y tres pequenas, alternas, la cara de la hoja
    hacia fuera; ninguna delante de la cara."""
    cara, nuc = cuerpo(out, P, V)
    cuernos(out, P, V)
    for i, ang in enumerate((-20.0, 40.0, 140.0, 200.0, 260.0, 320.0)):   # con hueco delante de la cara
        g = ang * D
        c, s_ = math.cos(g), math.sin(g)
        grande = i % 2 == 0
        r = 19.0 if grande else 16.0
        tope = (c * r, 62.0 if grande else 54.0, s_ * r)
        espada(out, P, tope, 36.0 if grande else 26.0, 10.0 if grande else 8.0, fuera=(c, 0.0, s_), semilla=20 + i * 6)
    return cara, nuc


# ======================================================================
#  B · EL DE LAS TABLILLAS
# ======================================================================
TRAMOS_CRISTAL = ((0.46, 1.0), (0.24, 0.7), (0.17, 0.42), (0.15, 0.16))      # (largo, ancho) de cada tramo


def cristal(out, P, centro, d, largo, ancho, giro=0.0, semilla=0):
    """Un cristal de amatista con punta en los dos lados: desde el medio, tramos de una caja puesta en rombo (con un
    filo hacia fuera) que se estrechan hasta la punta, hacia arriba y hacia abajo. Una sola caja por tramo: con dos
    cruzadas salia una estrella llena de rayas."""
    centro, d = np.asarray(centro, float), _u(d)
    mitad = largo / 2
    for sentido in (1.0, -1.0):
        M0 = marco_y(centro, d * sentido) @ vr.Ry(giro)
        y = -0.4
        for nivel, (f, w) in enumerate(TRAMOS_CRISTAL):
            h = mitad * f
            M = M0 @ vr.Ry(math.pi / 4)
            aw = ancho * w * (1.0 if sentido > 0 else 0.97)                     # la mitad de abajo, un pelo mas fina:
            bm.cubo(out, M, -aw / 2, y, -aw / 2, aw, h, aw, P['cristal%d' % nivel],        # asi no se pisan en el medio
                    semilla=semilla + nivel)
            y += h * 0.92


def tablillas(out, P, V):
    """El cuerpo y la cara de la segunda referencia, y alrededor, en vez de las tablillas, cristales de amatista con
    punta en los dos lados, que flotan y giran casi de pie (un poco abiertos): cinco grandes abajo y
    cinco pequenos a la altura de los hombros."""
    cara, nuc = cuerpo(out, P, V, alto_cabeza=10.0)
    cuernos(out, P, V, alto_cabeza=10.0)
    for i, ang in enumerate((-30.0, 30.0, 150.0, 210.0, 270.0)):           # los grandes, con hueco delante
        g = ang * D
        c, s_ = math.cos(g), math.sin(g)
        centro = np.array((c * 14.0, 17.0 + (i % 2) * 3.0, s_ * 14.0))
        cristal(out, P, centro, (c * 0.16, 1.0, s_ * 0.16), 30.0 - (i % 2) * 5.0, 4.4, giro=g, semilla=50 + i)
    for i, ang in enumerate((0.0, 120.0, 180.0, 240.0, 300.0)):           # los pequenos, a la altura de los hombros
        g = ang * D
        c, s_ = math.cos(g), math.sin(g)
        centro = np.array((c * 19.0, 36.0 + (i % 2) * 5.0, s_ * 19.0))
        cristal(out, P, centro, (c * 0.2, 1.0, s_ * 0.2), 12.0, 2.6, giro=g, semilla=56 + i)
    return cara, nuc


# ======================================================================
#  C · EL DE LAS LANZAS
# ======================================================================
def lanzas(out, P, V):
    cara, nuc = cuerpo(out, P, V)
    cuernos(out, P, V)
    for i, ang in enumerate((-15.0, 35.0, 145.0, 195.0, 245.0, 295.0)):    # con hueco delante de la cara
        g = ang * D
        c, s = math.cos(g), math.sin(g)
        base = np.array((c * 14.0, 6.0 + (i % 2) * 6.0, s * 14.0))
        d = _u(np.array((c * 0.12, 1.0, s * 0.12)))
        tope = base + d * 36.0
        barra(out, P['asta'], base, tope, 2.8, semilla=60 + i % 3)
        bm.cubo(out, marco_y(tope - d * 1.0, d), -3.4, 0.0, -1.4, 6.8, 2.0, 2.8, P['hierro'], semilla=63)   # la cruz
        lado = _u(np.cross(d, np.array((c, 0.0, s)))) if i % 2 == 0 else _u(np.cross(d, (0.0, 0.0, 1.0)))
        w, h = 4.4, 12.0
        a = tope + d * 0.6
        for ll in (lado, _u(np.cross(d, lado))):
            hoja(out, (a - ll * w, a + ll * w, a + ll * w + d * h, a - ll * w + d * h), P['punta'], 2 * w, h, semilla=64)
        llama(out, P, base - d * 1.0, 1.6, 3.0, g, semilla=65)
    return cara, nuc


DISENOS = {'A': espadas, 'B': tablillas, 'C': lanzas}
FUEGO = ('fff2a0', 'ffa81a', 'c0301c')


def blaze(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        cara, nuc = DISENOS[tipo](out, P, V)
    finally:
        bm.PPB = ppb
    k = V['escala'] / 16.0
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([k, k, k, 1.0]) @ vr.T(0.0, -y0 + 6.0, 0.0)
    out = qm.transformar(out, E)
    return out, {'cabeza': pt(E, cara), 'nucleo': pt(E, nuc), 'luces': [pt(E, nuc)], 'luz': V['luz']}


def vanilla_a_escala():
    """El Blaze de vanilla tal cual, para compararlo: la cabeza y sus tres anillos de cuatro varas (con su paleta)."""
    import blaze_modelo_vanilla as bv
    return bv.vanilla_a_escala()


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
