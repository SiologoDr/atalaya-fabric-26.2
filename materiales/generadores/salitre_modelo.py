"""
Salitre, el Capitan Hundido, y sus tipos (15-10-2026, version 2). Juan, viendo la primera: «veo que con ilustracion no
queda bien; mejor sigamos, ahora hazlo fiel a la ilustracion; ojo, no quiero que se vea que tenga cuadrados; ten en
cuenta como estamos haciendo las texturas y disenos». La primera llevaba la armadura en mosaico de teselas (una
cuadricula: la guia ya lo prohibe, «se lee como bloques de Minecraft») y cubitos sueltos por todas partes.

Esta sigue la ilustracion («MOB DE ELITE») pieza a pieza, pero hecha como hacemos los monstruos:
  - las formas, redondeadas: el tronco, las piernas, los brazos y las hombreras son losas y tubos de ocho lados
    (dos cajas cruzadas), no cajas;
  - las texturas, limpias y de cinco tonos: placas en bandas con su bisel, manchas grandes de borde limpio, remaches
    de 2 x 2, ribetes de bronce; nada de cuadricula ni de ruido;
  - los detalles finos, en hoja: los dientes, los faldones rotos, los dientes de la espada.

Como en la ilustracion: plantado con las piernas abiertas y el tronco echado un poco adelante; la calavera azul con los
ojos que arden, metida entre las hombreras; el tricornio grande con la calavera delante; los tentaculos que le cuelgan
de debajo del sombrero y de la quijada; las hombreras en tres capas con el canto de bronce; las correas en aspa; el
cinturon ancho con la hebilla cuadrada; los faldones rotos hasta las rodillas; las rodilleras y las botas de bronce;
la espada de hueso dentado, enorme, en diagonal hacia arriba a su derecha; y la pistola de chispa a su izquierda.

Los tres tipos tienen la misma pose y cambian el color y lo que les crece encima:

    A  de la Prismarina   el de la ilustracion: turquesa y bronce, la luz cian
    B  del Coral          coral rojo, cuernos de coral naranja en el sombrero y en las hombreras; la luz ambar
    C  del Abismo         negro con lunares que brillan y el cebo de un pez abisal colgando del sombrero; la luz azul
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
ESCALA = 0.34
CABEZA = 1.4            # la cabeza y el sombrero, mas grandes que el resto, como en la ilustracion

VARIANTES = {
    'A': dict(
        clave='TA', nombre='de la Prismarina', corto='prismarina', crece='prismarina', lunares=False,
        placa=_r('0a2a2c', '134440', '1d6058', '2a8070', '44a690'),
        tela=_r('061416', '0c2224', '14322e', '1e463e', '2c5e50'),
        hueso=_r('0e2230', '1a3a4c', '2a5468', '3e7488', '5c98ac'),
        tentaculo=_r('0a2e30', '12484a', '1c6866', '2a8c86', '48b4a8'),
        hoja=_r('6a6452', 'a29c80', 'ccc6a8', 'eae4ca', 'fffaea'),
        coral=_r('0a3a3a', '12585a', '1e7e7e', '38a8a2', '6ad4c8'),
        neon=('e8ffff', '3ae8ff', '04466a'),
    ),
    'B': dict(
        clave='TB', nombre='del Coral', corto='coral', crece='coral', lunares=False,
        placa=_r('3a0a0e', '601418', '8c2420', 'b83a2a', 'e0623c'),
        tela=_r('1e0a06', '30120a', '461c10', '5e2a18', '7a3a22'),
        hueso=_r('2a1a14', '463020', '684a30', '8c6a46', 'b48e62'),
        tentaculo=_r('4a1206', '72200c', '9e3414', 'c84e20', 'ee7438'),
        hoja=_r('5a0e10', '8e1c1c', 'c0362c', 'e85a3a', 'ff8c5a'),
        coral=_r('5a1004', '8e2208', 'c43c10', 'f06a1e', 'ffa04a'),
        neon=('fff4d8', 'ffaa1a', '6a3404'),
    ),
    'C': dict(
        clave='TC', nombre='del Abismo', corto='abismo', crece='abismo', lunares=True,
        placa=_r('04040a', '0a0a16', '121224', '1c1c34', '2a2a48'),
        tela=_r('040408', '08080e', '0e0e18', '161624', '202034'),
        hueso=_r('101018', '1c1c2a', '2c2c40', '40405a', '5c5c7a'),
        tentaculo=_r('060a22', '0c1438', '142052', '203070', '304890'),
        hoja=_r('0a0a10', '16161e', '22222e', '30303e', '424252'),
        coral=_r('0a1430', '122050', '1c3478', '2c50a8', '4a7ad8'),
        neon=('e6f0ff', '3a7aff', '06125a'),
    ),
}

BRONCE = _r('3a2410', '6a4420', '9a6a30', 'c69446', 'eac06a')
CUERO = _r('1a0e08', '2e1a0e', '462a16', '623c20', '80522c')
MADERA = _r('1e1008', '34200e', '4e3016', '6a4420', '8a5c2e')
HIERRO = _r('0e1012', '1c2024', '2e3338', '444a52', '626a74')
FIELTRO = _r('060c10', '0c161c', '14222a', '1e3038', '2a4048')
DIENTE = _r('6a6452', 'a09a7e', 'cac4a6', 'e6e0c4', 'fbf8e6')


def _u(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# ----------------------------------------------------------------------
#  Los pintores: limpios, de cinco tonos, sin cuadricula
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}
    neo = [nm._hex(c) for c in V['neon']]
    OSCURO = (4, 10, 14, 255)

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'sal%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    def remaches(img, tw, th, fila, paso=8):
        """Remaches de 2 x 2 en fila (claro arriba a la izquierda, oscuro abajo a la derecha), de bronce."""
        if th < fila + 3 or tw < 6:
            return img
        for x in range(3, tw - 3, paso):
            for dy, dx, t in ((0, 0, 4), (0, 1, 3), (1, 0, 3), (1, 1, 1)):
                img[fila + dy, x + dx] = (*BRONCE[t], 255)
        return img

    def placa(tw, th, cara, s):
        """La placa de la armadura: un tono de fondo con manchas grandes de borde limpio (como la prismarina), el bisel
        del canto y, en el Abismo, lunares que brillan."""
        m = _manchas(tw, th, s, celda=12.0, umbral=0.66, alto=0.9)
        idx = np.array([2, 2, 2, 3, 3])[m]
        if cara == 'arriba':
            idx = idx + 1
        elif cara == 'abajo':
            idx = idx - 1
        img = _imagen(_bisel(np.clip(idx, 0, 4), 1, 1), V['placa'])
        brilla = np.zeros((th, tw), bool)
        if V['lunares']:
            rng = random.Random(s)
            for _ in range(max(1, tw * th // 110)):
                x, y = rng.randrange(1, max(2, tw - 2)), rng.randrange(1, max(2, th - 2))
                img[y:y + 2, x:x + 2] = (*neo[1], 255)
                brilla[y:y + 2, x:x + 2] = True
        return img, (_emis(img, brilla, 255) if brilla.any() else None)
    reg('placa', placa)

    def placa_rib(tw, th, cara, s):
        """La placa con el ribete de bronce alrededor y una fila de remaches arriba."""
        img, em_ = placa(tw, th, cara, s + 3)
        ys, xs = np.mgrid[0:th, 0:tw]
        rib = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
        img = np.where(rib[..., None], _imagen(np.where((xs == 0) | (ys == 0), 4, 2), BRONCE), img)
        img = remaches(img, tw, th, 2)
        if em_ is not None:
            em_[rib] = 0
        return img, em_
    reg('placa_rib', placa_rib)

    def bronce(tw, th, cara, s):
        """El bronce de los ribetes, las rodilleras y las botas: liso, con una acanaladura por el medio y el bisel."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        if th >= 5:
            idx = np.where(abs(ys - th / 2 + 0.5) < 0.6, 2, idx)
        return _imagen(_bisel(idx, 1, 1), BRONCE), None
    reg('bronce', bronce)

    def brazal(tw, th, cara, s):
        """El brazal: cuero tostado con tres bandas de bronce."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if cara in ('der', 'izq') else ys                    # a lo largo del tubo
        n = max(tw, th) if cara in ('der', 'izq') else th
        banda = (a % 9 < 2)
        img = _imagen(_bisel(np.full((th, tw), 2), 1, 1), CUERO)
        img = np.where(banda[..., None], _imagen(np.where(a % 9 == 0, 4, 2), BRONCE), img)
        return img, None
    reg('brazal', brazal)

    def cuero(tw, th, cara, s):
        """El cuero de las correas y las botas: liso, con la costura de puntos por los dos cantos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        largo_x = tw >= th
        a, t = (xs, ys) if largo_x else (ys, xs)
        ancho = th if largo_x else tw
        idx = np.full((th, tw), 2)
        if ancho >= 4:
            idx = np.where(((t == 1) | (t == ancho - 2)) & (a % 2 == 0), 3, idx)
        return _imagen(_bisel(idx, 1, 1), CUERO), None
    reg('cuero', cuero)

    def cinturon(tw, th, cara, s):
        """El cinturon: cuero ancho con una fila de tachuelas de bronce por el medio."""
        img, _ = cuero(tw, th, cara, s)
        return remaches(img, tw, th, max(0, th // 2 - 1), paso=6), None
    reg('cinturon', cinturon)

    def faldon(tw, th, cara, s):
        """El faldon de la casaca: pano oscuro con pliegues, el ribete de bronce arriba y a los lados, y el canto de abajo
        roto por el mar (en tiras de dos pixeles, limpias)."""
        ys, xs = np.mgrid[0:th, 0:tw]
        rng = random.Random(s)
        corte = np.zeros(tw, int)
        for x in range(0, tw, 2):
            corte[x:x + 2] = th - rng.choice((0, 0, 1, 2, 3, 4, 6))
        idx = np.where(xs % 5 == 0, 1, np.where(xs % 5 == 2, 3, 2))
        img = _imagen(idx, V['tela'])
        rib = (ys < 2) | (xs == 0) | (xs == tw - 1)
        img = np.where(rib[..., None], _imagen(np.where((ys == 0) | (xs == 0), 4, 2), BRONCE), img)
        img[..., 3] = np.where(ys < corte[None, :], 255, 0)
        return img, None
    reg('faldon', faldon)

    def hueso(tw, th, cara, s):
        """El hueso de la calavera: liso, con el bisel y alguna grieta fina."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 3)
        rng = random.Random(s)
        if tw > 8 and th > 8:
            x = rng.randrange(2, tw - 2)
            for y in range(1, th // 2):
                idx[y, min(tw - 1, x)] = 2
                x += rng.choice((-1, 0, 1))
        return _imagen(_bisel(idx, 1, 1), V['hueso']), None
    reg('hueso', hueso)

    def cara(tw, th, cara_, s):
        """La cara de la calavera: las cuencas hondas con el ceno (la esquina de dentro mas baja), la sombra del pomulo
        debajo, el hueco de la nariz en punta y una grieta."""
        ys, xs = np.mgrid[0:th, 0:tw]
        img = _imagen(_bisel(np.full((th, tw), 3), 1, 1), V['hueso'])
        som = _imagen(np.full((th, tw), 1), V['hueso'])
        for cx in (0.29, 0.71):
            haz = 1 if cx < 0.5 else -1
            u = (xs + 0.5 - cx * tw) / (0.16 * tw)
            v = (ys + 0.5 - 0.42 * th) / (0.19 * th)
            d = np.maximum(abs(u), abs(v)) * 0.25 + np.hypot(u, v) * 0.75
            ceno = v < -0.7 + haz * u * 0.45
            hueco = (d < 1.0) & ~ceno
            pomulo = (d >= 0.9) & (d < 1.35) & (v > 0.4)
            img[pomulo] = som[pomulo]
            img[hueco] = OSCURO
        yy = ys + 0.5 - 0.66 * th
        xx = abs(xs + 0.5 - tw / 2)
        nariz = (yy > -0.1 * th) & (yy < 0.12 * th) & (xx < (yy + 0.1 * th) * 0.55 + 0.4)
        img[nariz] = OSCURO
        g = int(tw * 0.62)
        for y in range(0, int(th * 0.22)):
            img[y, min(tw - 1, g + (y // 2) % 2)] = tuple(som[0, 0])
        return img, None
    reg('cara', cara)

    def ojo(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[1], 255)
        t[(abs(xs - (tw - 1) / 2) <= max(0.5, tw / 4)) & (abs(ys - (th - 1) / 2) <= max(0.5, th / 4))] = (*neo[0], 255)
        return t, None
    reg('ojo', ojo, pleno=True)

    def gema(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        d = np.maximum(abs(xs - (tw - 1) / 2) / max(tw / 2, 1), abs(ys - (th - 1) / 2) / max(th / 2, 1))
        t = np.zeros((th, tw, 4), np.uint8)
        t[...] = (*neo[2], 255)
        t[d < 0.75] = (*neo[1], 255)
        t[d < 0.35] = (*neo[0], 255)
        return t, None
    reg('gema', gema, pleno=True)

    def piedra(tw, th, cara_, s):
        """La piedra oscura del centro de la hebilla."""
        idx = _bisel(np.full((th, tw), 2), 1, 1)
        return _imagen(idx, V['placa']), None
    reg('piedra', piedra)

    def dientes(base_arriba):
        def f(tw, th, cara_, s):
            """Los dientes de la calavera, dibujados en hoja: largos, de punta roma, con un hueco entre uno y otro."""
            ys, xs = np.mgrid[0:th, 0:tw]
            t = np.zeros((th, tw, 4), np.uint8)
            fila = ys if base_arriba else th - 1 - ys
            diente = (xs % 3 != 2) & ~((fila == th - 1) & (xs % 3 == 1))
            t[diente] = (*DIENTE[3], 255)
            t[diente & (xs % 3 == 1)] = (*DIENTE[2], 255)
            t[diente & (fila == 0)] = (*DIENTE[1], 255)
            return t, None
        return f
    reg('dientes_arriba', dientes(True))
    reg('dientes_abajo', dientes(False))

    def tentaculo(tw, th, cara_, s):
        """El tentaculo: liso, en anillos suaves a lo largo, con el bisel."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a = xs if cara_ in ('der', 'izq') else ys
        idx = np.where(a % 6 == 0, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V['tentaculo']), None
    reg('tentaculo', tentaculo)

    def ventosas(tw, th, cara_, s):
        """La cara de abajo del tentaculo: las ventosas en fila, claras, con el centro oscuro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (ys, xs) if th >= tw else (xs, ys)
        ancho = min(tw, th)
        img = _imagen(np.full((th, tw), 2), V['tentaculo'])
        c = ancho // 2
        anillo = (a % 4 != 3) & (abs(t - c) <= 1) & ~((a % 4 == 1) & (t == c))
        img[anillo] = (*V['tentaculo'][4], 255)
        img[(a % 4 == 1) & (t == c)] = (*V['tentaculo'][0], 255)
        return img, None
    reg('ventosas', ventosas)

    def hoja(tw, th, cara_, s):
        """La hoja de la espada: hueso con el nervio del medio y los poros, con el bisel."""
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (xs, ys) if tw >= th else (ys, xs)
        ancho = min(tw, th)
        idx = np.where(abs(t - ancho / 2 + 0.5) < 0.7, 2, 3)
        idx = np.where((a % 7 == 3) & (t % 4 == 1), 2, idx)
        return _imagen(_bisel(idx, 1, 1), V['hoja']), None
    reg('hoja', hoja)

    def sierra(tw, th, cara_, s):
        """Los dientes de la espada, dibujados en hoja: la base abajo y la punta arriba, echada hacia la punta de la
        espada, con su canto oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        paso = 7
        for x0 in range(0, tw - 2, paso):
            for y in range(th):
                f = (th - 1 - y) / max(th - 1, 1)                   # 0 en la base, 1 en la punta
                w = 5.0 * (1 - f)
                a = x0 + 4.0 * f
                for x in range(int(math.floor(a)), min(tw, int(math.ceil(a + w)))):
                    c = V['hoja'][3] if x - a < w * 0.5 else V['hoja'][2]
                    if x == int(math.floor(a)) or y == th - 1:
                        c = V['hoja'][1]
                    t[y, x] = (*c, 255)
        return t, None
    reg('sierra', sierra)

    def madera(tw, th, cara_, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        a, t = (xs, ys) if tw >= th else (ys, xs)
        idx = np.where((t + a // 6) % 3 == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), MADERA), None
    reg('madera', madera)

    def hierro(tw, th, cara_, s):
        return _imagen(_bisel(np.full((th, tw), 2), 1, 1), HIERRO), None
    reg('hierro', hierro)

    def fieltro(tw, th, cara_, s):
        """El fieltro del sombrero: oscuro, con pliegues suaves."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs + ys * 2) % 11 == 0, 1, 2)
        return _imagen(_bisel(idx, 1, 1), FIELTRO), None
    reg('fieltro', fieltro)

    def emblema(tw, th, cara_, s):
        """La calavera y los huesos cruzados del sombrero, en hueso claro sobre el fieltro."""
        img = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        cx, cy = (tw - 1) / 2, (th - 1) * 0.45
        blanco = _imagen(np.full((th, tw), 4), DIENTE)
        gris = _imagen(np.full((th, tw), 2), DIENTE)
        L = min(tw * 0.42, th * 0.9)
        for sg in (1, -1):
            t = ((xs - cx) + sg * (ys - cy)) / 2
            n = ((xs - cx) - sg * (ys - cy)) / 2
            h = (abs(n) < 0.8) & (abs(t) < L * 0.5)
            for e in (1, -1):
                h |= np.hypot(xs - (cx + e * L * 0.5), ys - (cy + sg * e * L * 0.5)) < 1.4
            img = np.where(h[..., None], gris, img)
        R = min(tw, th) * 0.28
        cr = (np.hypot((xs - cx) / R, (ys - cy) / (R * 1.05)) < 1.0) | ((abs(xs - cx) < R * 0.55) & (ys > cy) & (ys < cy + R * 1.4))
        img = np.where(cr[..., None], blanco, img)
        for dx in (-1, 1):
            img[np.hypot(xs - cx - dx * R * 0.42, ys - cy) < R * 0.32] = (10, 10, 12, 255)
        return img, None
    reg('emblema', emblema)

    def coral(tw, th, cara_, s):
        """El coral: liso, con los polipos en puntos claros sueltos."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs * 3 + ys * 5) % 7 == 0, 4, 3)
        return _imagen(_bisel(idx, 1, 1), V['coral']), None
    reg('coral', coral)
    return P


# ----------------------------------------------------------------------
#  Formas redondeadas
# ----------------------------------------------------------------------
def losa(out, M, y0, y1, rx, rz, pin, caras=None, k=0.72, semilla=0):
    """Una losa de ocho lados en planta (dos cajas cruzadas), de y0 a y1, con los radios rx y rz."""
    bm.cubo(out, M, -rx, y0, -rz * k, 2 * rx, y1 - y0, 2 * rz * k, pin, caras=caras, semilla=semilla)
    bm.cubo(out, M, -rx * k, y0, -rz, 2 * rx * k, y1 - y0, 2 * rz, pin, caras=caras, semilla=semilla + 1)


def tubo(out, pts, radios, pin, caras=None, achata=1.0, semilla=0, arriba=(0.0, 1.0, 0.0)):
    """Un tubo de ocho lados por los puntos: en cada tramo, dos cajas cruzadas que se meten un poco en el siguiente."""
    for j in range(len(pts) - 1):
        p0, p1 = np.asarray(pts[j], float), np.asarray(pts[j + 1], float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            continue
        up = np.asarray(arriba, float)
        if abs(_u(d) @ _u(up)) > 0.95:
            up = np.array((0.0, 0.0, 1.0)) if abs(_u(d)[2]) < 0.95 else np.array((1.0, 0.0, 0.0))
        M = em.marco(p0, d, up=up)
        r = (radios[j] + radios[j + 1]) / 2
        for kx, ky in ((1.0, 0.72), (0.72, 1.0)):
            bm.cubo(out, M, -r * kx, -r * ky * achata, -r * 0.3, 2 * r * kx, 2 * r * ky * achata, L + r * 0.6, pin,
                    caras=caras, semilla=semilla + j % 3)


def hoja_doble(out, P4, pintor, ancho, alto, semilla=0):
    """Una lamina que se ve por las dos caras."""
    a, b, c, d = P4
    lamina(out, (a, b, c, d), pintor, ancho, alto, semilla)
    lamina(out, (b, a, d, c), pintor, ancho, alto, semilla)


def tentaculo(out, P, base, dirl, largo, rosca, r0=1.1, semilla=0, n=7):
    """Un tentaculo que cuelga desde 'base' hacia 'dirl', se afina y se enrosca en la punta ('rosca': hacia donde)."""
    p = np.asarray(base, float)
    d = _u(dirl)
    giro = _u(rosca)
    pts, rs = [p], [r0]
    for i in range(n):
        t = (i + 1) / n
        d = _u(d + giro * (0.02 + 0.6 * t ** 4))
        p = p + d * largo / n
        pts.append(p)
        rs.append(r0 * (1.0 - 0.8 * t))
    tubo(out, pts, rs, P['tentaculo'], caras={'abajo': P['ventosas']}, semilla=semilla)


def racimo(out, P, base, arriba, n, largo, semilla=0):
    """Un racimo de coral: ramas de ocho lados que crecen abiertas, cada una con su ramita."""
    rng = random.Random(semilla)
    base, up = np.asarray(base, float), _u(arriba)
    for i in range(n):
        d = _u(up + np.array((rng.uniform(-0.6, 0.6), rng.uniform(-0.1, 0.2), rng.uniform(-0.6, 0.6))))
        L = largo * rng.uniform(0.6, 1.1)
        q = base + np.array((rng.uniform(-1.5, 1.5), 0.0, rng.uniform(-1.5, 1.5)))
        tubo(out, [q, q + d * L * 0.5, q + d * L], [0.8, 0.65, 0.45], P['coral'], semilla=i)
        m = q + d * L * rng.uniform(0.4, 0.7)
        dd = _u(d + np.array((rng.uniform(-1, 1), 0.2, rng.uniform(-1, 1))))
        tubo(out, [m, m + dd * L * 0.45], [0.55, 0.35], P['coral'], semilla=i + 1)


def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes por los puntos (x, z) a la altura y: baja si alto < 0 y sube si alto > 0."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado = float(np.linalg.norm(B - A))
        if alto < 0:
            hoja_doble(out, (A2, B2, B, A), pintor, lado, abs(alto), semilla + j)
        else:
            hoja_doble(out, (A, B, B2, A2), pintor, lado, abs(alto), semilla + j)


# ======================================================================
#  SALITRE, EL CAPITAN HUNDIDO
# ======================================================================
TRONCO = [  # (y0, y1, rx, rz): las caderas, el vientre, el pecho y los hombros
    (40.0, 44.0, 11.6, 8.4), (44.0, 48.0, 12.4, 8.8), (48.0, 53.0, 13.2, 9.2), (53.0, 59.0, 14.4, 9.8),
    (59.0, 65.0, 15.0, 10.2), (65.0, 69.0, 14.2, 9.6), (69.0, 71.0, 11.0, 8.0)]


def salitre(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    pl, br = P['placa'], P['bronce']
    try:
        # ---- las piernas, abiertas y plantadas, con las rodillas un poco dobladas
        for s, dz in ((-1, -1.5), (1, 2.0)):
            cad = np.array((s * 7.0, 42.0, 0.0))
            rod = np.array((s * 9.6, 26.0, dz + 2.8))
            tob = np.array((s * 10.6, 12.0, dz))
            tubo(out, [cad, (cad + rod) / 2 + np.array((s * 0.6, 0.0, 0.6)), rod], [6.0, 5.8, 5.0], pl, semilla=1)
            tubo(out, [rod, tob], [4.8, 4.2], pl, semilla=2)
            Mr = vr.T(*(rod + np.array((0.0, 0.0, 3.0)))) @ vr.Rx(-0.2)                      # la rodillera
            losa(out, Mr, -3.4, 3.4, 4.6, 2.4, br, semilla=3)
            losa(out, Mr @ vr.T(0.0, 0.0, 1.0), -2.2, 2.2, 3.0, 2.0, br, semilla=4)
            Mb = vr.T(tob[0], 0.0, tob[2]) @ vr.Ry(s * 0.12)                                     # la bota
            losa(out, Mb, 0.0, 12.0, 5.4, 5.6, P['cuero'], semilla=5)
            losa(out, Mb, 11.0, 15.6, 6.8, 7.0, br, semilla=6)                                  # la vuelta de bronce
            losa(out, Mb, 15.0, 16.0, 7.0, 7.2, P['cuero'], semilla=7)
            losa(out, Mb @ vr.T(0.0, 0.0, 4.6), 0.0, 4.6, 4.6, 4.6, P['cuero'], semilla=8)       # el pie
            losa(out, Mb @ vr.T(0.0, 0.0, 8.0), 0.0, 3.6, 3.8, 2.6, br, semilla=9)              # la puntera
        # ---- el tronco, echado un poco adelante
        Mt = vr.T(0.0, 42.0, 0.0) @ vr.Rx(8 * D) @ vr.T(0.0, -42.0, 0.0)
        for i, (y0, y1, rx, rz) in enumerate(TRONCO):
            losa(out, Mt, y0, y1, rx, rz, pl, semilla=10 + i)
        for j, y in enumerate((48.0, 50.8)):                                                    # las lamas del vientre
            bm.cubo(out, Mt, -9.6, y, 9.0, 19.2, 2.6, 1.0, P['placa_rib'], semilla=17 + j)
        for s in (-1, 1):                                                                       # los petos
            Mp = Mt @ vr.T(s * 6.8, 60.0, 9.8) @ vr.Ry(s * 0.18)
            bm.cubo(out, Mp, -6.2, -6.4, 0.0, 12.4, 12.8, 1.4, P['placa_rib'], semilla=19)
        # ---- el cinturon ancho y la hebilla cuadrada
        losa(out, Mt, 42.0, 47.4, 12.9, 9.3, P['cinturon'], semilla=20)
        bm.cubo(out, Mt, -4.0, 41.4, 9.0, 8.0, 6.6, 1.4, br, semilla=21)
        bm.cubo(out, Mt, -2.4, 42.9, 10.2, 4.8, 3.6, 0.5, P['piedra'], semilla=22)
        # ---- los faldones rotos, alrededor, hasta las rodillas
        for i in range(12):
            g = TAU * i / 12
            c, s_ = math.cos(g), math.sin(g)
            r_arriba, r_abajo = np.array((s_ * 12.8, 0.0, c * 9.4)), np.array((s_ * 14.6, 0.0, c * 11.2))
            tang = np.array((c, 0.0, -s_)) * 3.6
            largo = 17.0 if abs(c) > 0.5 else 15.0
            a0 = pt(Mt, np.array((0.0, 42.6, 0.0)) + r_arriba)
            a1 = np.array((0.0, 42.6 - largo, 0.0)) + r_abajo
            hoja_doble(out, (a1 - tang, a1 + tang, a0 + tang, a0 - tang), P['faldon'], 7.2, largo, semilla=23 + i)
        # ---- las correas en aspa y el medallon
        for a, b in (((-11.0, 65.6), (10.5, 47.5)), ((11.0, 65.6), (-10.5, 47.5))):
            p0, p1 = pt(Mt, (a[0], a[1], 11.0)), pt(Mt, (b[0], b[1], 10.6))
            M = em.marco(p0, p1 - p0, up=Mt[:3, 2])
            bm.cubo(out, M, -1.5, -0.5, 0.0, 3.0, 1.0, float(np.linalg.norm(p1 - p0)), P['cuero'], semilla=24)
        Mm = Mt @ vr.T(0.0, 56.3, 11.4)
        losa(out, Mm @ vr.Rx(math.pi / 2), -0.4, 1.0, 2.6, 2.6, br, semilla=25)
        losa(out, Mm @ vr.Rx(math.pi / 2), 0.9, 1.4, 1.4, 1.4, P['gema'], semilla=26)
        # ---- las hombreras: tres capas con el canto de bronce y una cupula encima
        for s in (-1, 1):
            Mh = vr.T(*pt(Mt, (s * 15.4, 67.0, 0.0))) @ vr.Rz(-s * 0.22)
            for j, (y, h, rx, rz) in enumerate(((0.0, 4.4, 9.0, 9.6), (-3.6, 3.8, 8.6, 9.2), (-7.0, 3.8, 8.0, 8.6))):
                Mj = Mh @ vr.T(s * j * 0.9, 0.0, 0.0)
                losa(out, Mj, y + 0.6, y + h, rx, rz, pl, semilla=30 + j)
                losa(out, Mj, y, y + 0.9, rx + 0.4, rz + 0.4, br, semilla=33)
            losa(out, Mh, 4.2, 6.6, 6.8, 7.2, pl, semilla=36)
            losa(out, Mh, 6.4, 7.6, 4.2, 4.6, pl, semilla=37)
            if V['crece'] == 'coral':
                racimo(out, P, pt(Mh, (s * 1.0, 7.0, -1.0)), (s * 0.5, 1.0, 0.0), 6, 10.0, semilla=38 + s)
            elif V['crece'] == 'prismarina' and s < 0:
                racimo(out, P, pt(Mh, (-2.0, 6.8, -2.0)), (-0.3, 1.0, -0.2), 3, 5.0, semilla=38)
        # ---- los brazos: el derecho (-x) con la espada; el izquierdo (+x), tendido, con la pistola
        ho_d, co_d, mu_d = pt(Mt, (-16.0, 63.0, 1.0)), np.array((-24.0, 51.0, 5.0)), np.array((-21.0, 41.0, 12.0))
        ho_i, co_i, mu_i = pt(Mt, (16.0, 63.0, 1.0)), np.array((27.0, 57.0, 6.0)), np.array((36.0, 60.0, 13.0))
        for ho, co, mu in ((ho_d, co_d, mu_d), (ho_i, co_i, mu_i)):
            tubo(out, [ho, co], [5.2, 4.6], pl, semilla=40)
            losa(out, vr.T(*co), -3.2, 3.2, 3.8, 3.8, br, semilla=41)                          # el codal
            d = _u(mu - co)
            L = float(np.linalg.norm(mu - co))
            tubo(out, [co, co + d * L * 0.3], [4.4, 4.2], pl, semilla=42)
            tubo(out, [co + d * L * 0.3, mu], [4.4, 4.0], P['brazal'], semilla=43)              # el brazal
            tubo(out, [mu, mu + d * 3.4], [3.1, 2.9], P['cuero'], semilla=44)                  # el guantelete
        espada(out, P, V, mu_d + _u(mu_d - co_d) * 2.4)
        pistola(out, P, V, mu_i + _u(mu_i - co_i) * 2.6, _u(np.array((0.84, 0.22, 0.5))))
        # ---- la cabeza, metida entre las hombreras
        Mc = Mt @ vr.T(0.0, 65.4, 3.6) @ vr.Rx(-6 * D) @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        cabeza(out, P, V, Mc)
        sombrero(out, P, V, Mc)
        bm.PPB = PPB
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    ojos = pt(E @ Mc, (0.0, 8.0, 6.6))
    return out, {'ojos': ojos, 'luces': [pt(E @ Mc, (0.0, 6.0, 15.0)), pt(E @ Mt, (0.0, 57.0, 16.0))]}


def cabeza(out, P, V, Mc):
    """La calavera: el craneo redondeado, la cara con las cuencas, la ceja de hueso, los pomulos, los ojos que arden,
    los dientes de arriba, la quijada entreabierta con los de abajo, la barba de tentaculos y los que cuelgan de debajo
    del sombrero."""
    hu = P['hueso']
    bm.cubo(out, Mc, -6.8, 3.4, -5.4, 13.6, 9.0, 10.4, hu, semilla=50)                                   # el craneo
    bm.cubo(out, Mc, -5.6, 2.4, -6.6, 11.2, 11.0, 12.6, hu, caras={'frente': P['cara']}, semilla=51)
    bm.cubo(out, Mc, -6.0, 9.8, 5.4, 12.0, 1.4, 1.2, hu, semilla=52)                                     # la ceja
    for s in (-1, 1):
        bm.cubo(out, Mc, s * 2.35 - 0.65, 8.0, 5.9, 1.3, 1.1, 0.3, P['ojo'], semilla=53)                # los ojos
        bm.cubo(out, Mc, (3.4 if s > 0 else -5.8), 4.6, 5.0, 2.4, 1.8, 1.6, hu, semilla=54)              # los pomulos
    hilera(out, Mc, [(-4.6, 4.6), (-4.4, 6.2), (4.4, 6.2), (4.6, 4.6)], 2.6, -1.8, P['dientes_arriba'], semilla=55)
    Mj = Mc @ vr.T(0.0, 2.6, -2.4) @ vr.Rx(0.3)                                                         # la quijada
    bm.cubo(out, Mj, -5.0, -3.0, -2.6, 10.0, 3.0, 9.2, hu, semilla=56)
    hilera(out, Mj, [(-4.4, 3.4), (-4.2, 6.4), (4.2, 6.4), (4.4, 3.4)], 0.0, 1.6, P['dientes_abajo'], semilla=57)
    rng = random.Random(3)
    for i, x in enumerate(np.linspace(-4.2, 4.2, 7)):                                                 # la barba de tentaculos
        b = pt(Mj, (x, -2.6, 5.0 - abs(x) * 0.3))
        tentaculo(out, P, b, (x * 0.06, -1.0, 0.55), (rng.uniform(10.0, 15.0) - abs(x) * 0.4) * CABEZA,
                  (rng.choice((-1, 1)) * 0.6, 0.3, 0.8), r0=1.1 * CABEZA, semilla=58 + i % 3)
    for s in (-1, 1):                                                                                  # los de debajo del sombrero
        for j, z in enumerate((-2.4, 0.6, 3.6)):
            b = pt(Mc, (s * 6.9, 11.6, z))
            tentaculo(out, P, b, (s * 0.12, -1.0, 0.2), rng.uniform(11.0, 15.0) * CABEZA, (s * 0.5, 0.0, 0.6),
                      r0=1.2 * CABEZA, semilla=61 + j)


def sombrero(out, P, V, Mc):
    """El tricornio grande: la copa, la cinta de bronce, las tres alas dobladas hacia arriba con el canto de bronce (la
    punta delante) y la calavera con los huesos delante; y encima, lo de cada tipo."""
    fi = P['fieltro']
    losa(out, Mc, 12.6, 19.4, 7.4, 7.6, fi, semilla=70)
    losa(out, Mc, 12.6, 13.8, 7.6, 7.8, P['bronce'], semilla=71)
    for i in range(3):
        g = TAU * i / 3 + TAU / 6
        Ma = Mc @ vr.T(0.0, 12.0, 0.0) @ vr.Ry(g) @ vr.T(0.0, 0.0, 7.0) @ vr.Rx(-0.32)
        bm.cubo(out, Ma, -12.6, 0.0, -0.6, 25.2, 7.6, 1.2, fi, semilla=72)
        bm.cubo(out, Ma, -12.8, 7.2, -0.7, 25.6, 1.0, 1.4, P['bronce'], semilla=73)
        bm.cubo(out, Ma, -12.8, -0.4, -0.7, 25.6, 0.8, 1.4, P['bronce'], semilla=73)
    Me = Mc @ vr.T(0.0, 13.6, 14.3) @ vr.Rx(-0.32)
    hoja_doble(out, (pt(Me, (-3.2, 0.0, 0.0)), pt(Me, (3.2, 0.0, 0.0)), pt(Me, (3.2, 5.4, 0.0)), pt(Me, (-3.2, 5.4, 0.0))),
               P['emblema'], 6.4, 5.4, semilla=74)
    if V['crece'] == 'coral':
        for s in (-1, 1):
            racimo(out, P, pt(Mc, (s * 4.0, 19.2, -1.0)), (s * 0.6, 1.0, -0.2), 5, 11.0 * CABEZA, semilla=75 + s)
    elif V['crece'] == 'abismo':                                                                     # el cebo del pez abisal
        a = pt(Mc, (0.0, 19.2, 2.0))
        ps = [a, a + np.array((0.0, 8.0, 4.0)), a + np.array((0.0, 11.0, 11.0)), a + np.array((0.0, 8.6, 16.6))]
        tubo(out, ps, [0.8, 0.7, 0.55, 0.5], P['hueso'], semilla=76)
        losa(out, vr.T(*ps[-1]), -4.0, 0.0, 2.0, 2.0, P['gema'], semilla=77)
    else:
        racimo(out, P, pt(Mc, (-4.4, 19.2, -1.4)), (-0.4, 1.0, -0.2), 4, 6.0 * CABEZA, semilla=78)


def espada(out, P, V, mano):
    """La espada de hueso dentado, enorme, en diagonal hacia arriba a su derecha: el puno de cuero, el pomo y la guarda
    de bronce, y la hoja de hueso que se estrecha, con los dientes por los dos cantos, dibujados en hoja."""
    d = _u(np.array((-0.62, 0.72, 0.3)))
    lado = _u(np.cross(d, (0.0, 0.0, 1.0)))
    frente = np.cross(lado, d)
    tubo(out, [mano - d * 6.0, mano + d * 2.6], [1.2, 1.2], P['cuero'], arriba=frente, semilla=90)
    losa(out, em.marco(mano - d * 7.2, d, up=frente) @ vr.Rx(math.pi / 2), -1.6, 1.6, 1.6, 1.6, P['bronce'], semilla=91)
    Mg = em.marco(mano + d * 2.6, d, up=frente)
    bm.cubo(out, Mg, -6.4, -1.4, 0.0, 12.8, 2.8, 2.2, P['bronce'], semilla=92)                     # la guarda
    for s in (-1, 1):
        bm.cubo(out, Mg, (5.2 if s > 0 else -7.6), -1.8, -0.6, 2.4, 3.6, 3.4, P['bronce'], semilla=93)
    L, n = 60.0, 12
    base = mano + d * 4.8
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        a, b = base + d * L * t0, base + d * L * t1
        w = 8.6 - 4.6 * t0
        M = em.marco(a, d, up=frente)
        bm.cubo(out, M, -w / 2, -0.9, 0.0, w, 1.8, L / n + 0.15, P['hoja'], semilla=94)
        for s in (-1, 1):
            ca, cb = a + lado * s * w / 2, b + lado * s * (w - 4.0 / n) / 2
            h = 5.2 - 2.4 * t0
            hoja_doble(out, (ca, cb, cb + lado * s * h, ca + lado * s * h), P['sierra'], float(np.linalg.norm(cb - ca)), h,
                       semilla=95)
    punta = base + d * L
    M = em.marco(punta, d, up=frente)
    bm.cubo(out, M, -1.8, -0.8, -0.2, 3.6, 1.6, 3.0, P['hoja'], semilla=96)
    bm.cubo(out, M, -0.9, -0.6, 2.6, 1.8, 1.2, 2.6, P['hoja'], semilla=97)


def pistola(out, P, V, mano, apunta):
    """La pistola de chispa: la culata curva de madera con su remate de bronce, la caja, la llave de bronce con el
    martillo, el canon de hierro con sus anillos y la boca un poco abierta."""
    lado = _u(np.cross(apunta, (0.0, 1.0, 0.0)))
    arriba = _u(np.cross(lado, apunta))
    culata = mano - apunta * 3.4 - arriba * 5.6
    tubo(out, [culata, mano - apunta * 1.0, mano + apunta * 1.4], [1.9, 1.7, 1.6], P['madera'], arriba=lado, semilla=100)
    losa(out, em.marco(culata, -arriba, up=apunta) @ vr.Rx(-math.pi / 2), -1.2, 1.2, 2.2, 2.2, P['bronce'], semilla=101)
    tubo(out, [mano, mano + apunta * 13.0], [1.7, 1.4], P['madera'], arriba=arriba, semilla=102)
    b0, b1 = mano + arriba * 1.5 + apunta * 0.5, mano + arriba * 1.5 + apunta * 21.0
    tubo(out, [b0, b1], [0.95, 0.95], P['hierro'], arriba=arriba, semilla=103)
    for t in (0.3, 0.62, 0.95):
        q = b0 + (b1 - b0) * t
        tubo(out, [q, q + apunta * 0.8], [1.3, 1.3], P['bronce'], arriba=arriba, semilla=104)
    tubo(out, [b1, b1 + apunta * 1.4], [1.4, 1.7], P['bronce'], arriba=arriba, semilla=105)
    Ml = em.marco(mano + arriba * 1.2 - apunta * 1.0, apunta, up=arriba)
    bm.cubo(out, Ml, -1.9, -0.8, 0.0, 0.6, 2.0, 4.0, P['bronce'], semilla=106)                     # la llave
    bm.cubo(out, Ml, -1.0, 1.0, 0.4, 0.8, 2.2, 0.8, P['hierro'], semilla=107)                      # el martillo


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
