"""
El Fogonazo en el juego (16-10-2026): de la ficha aprobada (el Destello: Juan, «este diseño va a ser, metámoslo en el
juego») a la malla de Minecraft, su textura y la de lo que brilla.

Las piezas son las mismas cajas del boceto (fogonazo_modelo.py): se recogen al construirlo, agrupadas en las partes que se
mueven (el cuerpo, el farol con su nucleo y sus placas, la cabeza con el escudo, la quijada, las mandibulas y las
antenas, y las cuatro patas con su canilla), y cada caja va a su propia pieza de ModelPart con su giro (una caja de
ModelPart no se puede girar sola). Las caras se pintan con los mismos pintores del boceto, a un texel por pixel, en una
textura cuatro veces mas fina que su cuadricula: asi las medidas con decimales caen en pixeles enteros.

Del boceto (Y arriba, el frente en +Z) a Minecraft (Y abajo desde la altura 24, el frente en -Z): C = diag(1, -1, -1).

Uso: python fogonazo_juego.py <raiz del proyecto> [carpeta de la vista previa]
"""
import math, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import quimeras_modelo as qm
import bestias_modelo as bm
import fogonazo_modelo as fg

TIPO = 'A'
K = 4                         # pixeles de la textura por unidad de la cuadricula
ANCHO = 256                   # ancho de la cuadricula (unidades)
ATRAS = 2.6                   # el boceto va adelantado: se corre hacia atras para centrarlo en su caja
C = np.diag([1.0, -1.0, -1.0, 1.0])
A = vr.T(0.0, 24.0, 0.0) @ C @ vr.T(0.0, 0.0, -ATRAS)


# ----------------------------------------------------------------------
#  Recoger las cajas del boceto, por partes
# ----------------------------------------------------------------------
class Parte:
    def __init__(self, nombre, padre, marco):
        self.nombre, self.padre, self.marco = nombre, padre, np.asarray(marco, float)
        self.cajas = []                   # (matriz del boceto, x0, y0, z0, w, h, d, {cara: pintor})
        self.hijos = []


PARTES, ORDEN = {}, []
ACTUAL = [None]


def parte(nombre, padre, marco):
    p = Parte(nombre, padre, marco)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    ACTUAL[0] = p
    return p


def en(nombre):
    ACTUAL[0] = PARTES[nombre]


CARAS = ('frente', 'atras', 'der', 'izq', 'arriba', 'abajo')


def _cubo(out, M, x0, y0, z0, w, h, d, pintor, caras=None, semilla=0):
    pint = {c: (caras or {}).get(c, pintor) for c in CARAS}
    ACTUAL[0].cajas.append((np.array(M, float), x0, y0, z0, w, h, d, pint))


def _hoja(out, P4, pintor, ancho, alto, semilla=0):
    """Una hoja (un diente, un diente de la sierra): un plano sin grosor con la textura entera, la base arriba."""
    a, b, c, d = [np.asarray(p, float) for p in P4]
    abajo, arriba = (a + b) / 2, (c + d) / 2
    x = c - d
    W = max(float(np.linalg.norm(x)), float(np.linalg.norm(b - a)), 0.3)
    x = fg._u(x)
    y = arriba - abajo
    H = float(np.linalg.norm(y))
    y = fg._u(y - x * float(x @ y))
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, abajo
    ACTUAL[0].cajas.append((M, -W / 2, 0.0, 0.0, W, H, 0.0, {c: (pintor if c in ('frente', 'atras') else None)
                                                              for c in CARAS}))


bm.cubo = _cubo
fg.hoja = _hoja
pt = fg.pt
T, Rx, Ry, Rz = vr.T, vr.Rx, vr.Ry, vr.Rz


def construir():
    """El Destello en su pose de acecho, como fogonazo_modelo.fogonazo(), pero apuntando cada caja en su parte."""
    V = fg.VARIANTES[TIPO]
    P = fg.pintores(V)
    Q = fg.POSTURAS['acecho']
    bm.PPB = 1
    Mt = T(0.0, 9.0, 3.0) @ Rx(Q['alza'])
    parte('cuerpo', None, Mt)
    fg.ovalo(None, Mt, 4.6, 3.6, 5.0, P['piel'], semilla=1)
    for i, t in enumerate((-0.75, -0.05, 0.65)):
        Mi = fg.marco_arco(Mt, t, 4.4, 5.6)
        parte(f'pecho{i}', 'cuerpo', Mi)
        _placa(P, Mi, 11.0, 4.6, 2.6, i)
    Fw = Mt @ T(0.0, 1.8, -4.2) @ Rx(1.1)
    Ma = Fw @ T(0.0, 0.0, -6.4) @ Rz(math.pi)
    rx, ry, rz = 5.6, 5.4, 7.0
    parte('farol', 'cuerpo', Fw)
    parte('nucleo', 'farol', Ma)
    fg.ovalo(None, Ma, rx, ry, rz, P['luz'], semilla=3)
    en('farol')
    for i, z in enumerate((-3.6, 0.0, 3.6)):
        for a, b in ((1.0, 0.72), (0.74, 1.0)):
            bm.cubo(None, Ma, -(rx + 0.5) * a, -(ry + 0.5) * b, z - 0.7, 2 * (rx + 0.5) * a, 2 * (ry + 0.5) * b, 1.4,
                    P['banda'], semilla=4 + i)
    Mc = Ma @ T(0.0, 0.0, -rz + 0.5)
    bm.cubo(None, Mc, -2.2, -2.2, -2.6, 4.4, 4.4, 2.6, P['piel'], semilla=6)
    bm.cubo(None, Mc, -1.2, -1.2, -4.4, 2.4, 2.4, 2.0, P['piel'], semilla=7)
    for i, t in enumerate((-0.95, -0.32, 0.3, 0.9)):
        Mi = fg.marco_arco(Ma, t, ry + 0.8, rz + 0.8)
        parte(f'placa{i}', 'farol', Mi)
        _placa(P, Mi, 2 * rx + 2.4, 4.9, 3.0, i)
    en('cuerpo')
    fg.hueso(None, pt(Mt, (0.0, 1.0, -3.6)), pt(Ma, (0.0, -0.5, rz - 1.0)), 3.6, P['piel'], semilla=8)
    Mh = Mt @ T(0.0, -1.8, 5.4) @ Rx(-Q['alza'] + Q['cab'])
    parte('cabeza', 'cuerpo', Mh)
    _cabeza(P, Mh, Q['abre'])
    for lado, nombre in ((-1, 'antena_d'), (1, 'antena_i')):
        parte(nombre, 'cabeza', Mh @ T(lado * 1.0, 3.8, 4.8))
        fg.antena(None, P, Mh, lado, 0.0, 11, semilla=40)
    for lado, ld in ((-1, 'd'), (1, 'i')):
        s = np.array((lado, 1.0, 1.0))
        _pata(P, 'pata_d' + ld, pt(Mt, (lado * 3.8, -2.0, 2.6)), np.array(Q['codo']) * s, np.array(Q['pie_d']) * s,
              2.2, 1.4)
        _pata(P, 'pata_t' + ld, pt(Mt, (lado * 4.0, -1.4, -2.6)), np.array(Q['rodilla']) * s,
              np.array(Q['pie_t']) * s, 3.2, 1.5)
    return {'nucleo': pt(Ma, (0, 0, 0)), 'cabeza': pt(Mh, (0.0, 3.0, 5.0))}


def _placa(P, Mi, ancho, largo, faldon, i):
    bm.cubo(None, Mi, -ancho / 2, 0.0, -largo / 2, ancho, 1.8, largo, P['placa'], semilla=10 + i)
    for lado in (-1, 1):
        Mf = Mi @ T(lado * (ancho / 2 - 0.3), 1.2, 0.0) @ Rz(lado * 0.32)
        bm.cubo(None, Mf, -0.7, -faldon, -largo / 2, 1.4, faldon + 0.4, largo, P['placa'], semilla=20 + i)


def _cabeza(P, M, abre):
    """fogonazo_modelo.cabeza() en la pose de reposo, con el escudo, la quijada y las mandibulas en sus partes."""
    ojo = P['compuesto']
    pal = {'abajo': P['paladar']}
    bm.cubo(None, M, -3.2, 0.4, -2.8, 6.4, 4.6, 6.6, P['piel'], semilla=1)
    bm.cubo(None, M, -2.4, 0.8, 3.6, 4.8, 3.0, 1.4, P['piel'], semilla=2)
    for lado in (-1, 1):
        fg.ovalo(None, M @ T(lado * 3.2, 3.0, 2.0), 2.3, 2.5, 2.5, ojo, semilla=3)
    bm.cubo(None, M, -2.0, -0.8, 2.4, 4.0, 1.6, 2.6, P['piel'], caras={'frente': P['garganta']}, semilla=8)
    for x in (-1.5, -0.5, 0.5, 1.5):
        _diente(P, pt(M, (x, 0.8, 5.1)), -M[:3, 1], 1.6 if abs(x) < 1 else 2.0, 0.8, M[:3, 0])
    q = pt(M, (-1.5, -0.4, 4.6)), pt(M, (1.5, -0.4, 4.6))
    for lado, base in zip((-1, 1), q):
        r = base + M[:3, :3] @ np.array((lado * 0.5, -1.4, 0.9))
        bm.viga(None, base, r, 0.6, 0.6, P['piel'], extra=0.1)
        bm.viga(None, r, r + M[:3, :3] @ np.array((lado * 0.2, -1.0, 0.9)), 0.5, 0.5, P['piel'], extra=0.1)
    Me = M @ T(0.0, 5.0, -1.6) @ Rx(0.22)
    parte('escudo', 'cabeza', Me)
    bm.cubo(None, Me, -6.2, 0.0, -5.6, 12.4, 1.4, 9.6, P['escudo'], semilla=4)
    bm.cubo(None, Me, -3.8, 1.3, -4.6, 7.6, 1.0, 7.4, P['escudo'], semilla=5)
    bm.cubo(None, Me, -5.4, -0.1, 4.0, 10.8, 1.3, 1.4, P['escudo'], semilla=6)
    bm.cubo(None, Me, -4.2, -0.2, 5.4, 8.4, 1.2, 1.2, P['escudo'], semilla=6)
    bm.cubo(None, Me, -2.6, -0.3, 6.6, 5.2, 1.1, 0.9, P['escudo'], semilla=6)
    for lado in (-1, 1):
        bm.cubo(None, Me @ T(lado * 6.0, 0.6, -0.8) @ Rz(lado * 0.55), -0.6, -2.6, -4.6, 1.2, 3.0, 8.4, P['escudo'],
                semilla=7)
    Mq = M @ T(0.0, -0.8, 2.2) @ Rx(abre * 0.6)
    parte('quijada', 'cabeza', Mq)
    bm.cubo(None, Mq, -2.2, -1.2, 0.0, 4.4, 1.2, 3.4, P['piel'], caras={'arriba': P['paladar']}, semilla=9)
    for x in (-1.0, 0.0, 1.0):
        _diente(P, pt(Mq, (x, 0.0, 3.3)), Mq[:3, 1], 1.4, 0.8, Mq[:3, 0])
    for lado, nombre in ((-1, 'mandibula_d'), (1, 'mandibula_i')):
        p = pt(M, (lado * 2.4, 0.4, 4.4))
        parte(nombre, 'cabeza', M @ T(lado * 2.4, 0.4, 4.4))
        d = M[:3, :3] @ fg._u((lado * 0.45, -0.35, 1.0))
        for k in range(3):
            q2 = p + d * 1.7
            g = 1.1 - 0.25 * k
            bm.viga(None, p, q2, g, g, P['cuerno'], extra=0.15)
            p = q2
            d = fg._u(d + M[:3, :3] @ np.array((-lado * (0.42 + 0.12 * k), 0.08, -0.12)))


def _diente(P, base, hacia, largo, ancho, eje):
    ll = eje * ancho / 2
    punta = base + hacia * largo
    fg.hoja(None, (punta - ll * 0.12, punta + ll * 0.12, base + ll, base - ll), P['diente'], 1, 3)


def _pata(P, nombre, raiz, rodilla, pie, gruesa, fina):
    raiz, rodilla, pie = (np.asarray(p, float) for p in (raiz, rodilla, pie))
    parte(nombre, 'cuerpo', T(*raiz))
    medio = raiz + (rodilla - raiz) * 0.55
    fg.hueso(None, raiz, medio, gruesa, P['piel'])
    fg.hueso(None, medio, rodilla, gruesa * 0.72, P['piel'])
    parte(nombre + '_canilla', nombre, T(*rodilla))
    fg.hueso(None, rodilla, pie + np.array((0.0, 0.8, 0.0)), fina, P['piel'])
    delante = fg._u(np.array((pie[0] - raiz[0], 0.0, 0.0)) * 0.3 + np.array((0.0, 0.0, 1.0)))
    lat = fg._u(np.cross(np.array((0.0, 1.0, 0.0)), delante))
    for a in (-0.55, 0.0, 0.55):
        d = fg._u(delante * math.cos(a) + lat * math.sin(a) + np.array((0.0, 0.25, 0.0)))
        fg.garra(None, P, pie + np.array((0.0, 0.8, 0.0)), d, fg._u(np.cross(np.array((0.0, 1.0, 0.0)), d)), 2.6)


# ----------------------------------------------------------------------
#  A Minecraft
# ----------------------------------------------------------------------
def euler_zyx(R):
    """(x, y, z) en radianes con R = Rz(z) Ry(y) Rx(x), como ModelPart."""
    sy = -R[2, 0]
    sy = max(-1.0, min(1.0, sy))
    y = math.asin(sy)
    if abs(math.cos(y)) > 1e-6:
        x = math.atan2(R[2, 1], R[2, 2])
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        z = 0.0
    return x, y, z


def pose_mc(L):
    x, y, z = euler_zyx(L[:3, :3])
    return tuple(L[:3, 3]), (x, y, z)


def local_mc(nombre):
    """La pose de una parte respecto a su padre, en Minecraft."""
    p = PARTES[nombre]
    if p.padre is None:
        return A @ p.marco @ C
    return C @ np.linalg.inv(PARTES[p.padre].marco) @ p.marco @ C


def caja_mc(p, caja):
    M, x0, y0, z0, w, h, d, pint = caja
    B = C @ np.linalg.inv(p.marco) @ M @ C
    return B, (x0, -(y0 + h), -(z0 + d), w, h, d)


# ----------------------------------------------------------------------
#  La textura
# ----------------------------------------------------------------------
def nombre_pintor(f):
    return f.__name__ if f else '-'


def clave(caja):
    M, x0, y0, z0, w, h, d, pint = caja
    return (round(w, 2), round(h, 2), round(d, 2), tuple(nombre_pintor(pint[c]) for c in CARAS))


def tam(caja):
    w, h, d = caja[4], caja[5], caja[6]
    return int(math.ceil(2 * (d + w))) + 1, int(math.ceil(d + h)) + 1


def empaquetar():
    unicas = {}
    for n in ORDEN:
        for c in PARTES[n].cajas:
            unicas.setdefault(clave(c), c)
    orden = sorted(unicas, key=lambda k: (-tam(unicas[k])[1], -tam(unicas[k])[0]))
    uv, x, y, fila = {}, 0, 0, 0
    for k in orden:
        w, h = tam(unicas[k])
        if x + w > ANCHO:
            x, y, fila = 0, y + fila, 0
        uv[k] = (x, y)
        x += w
        fila = max(fila, h)
    alto = 1 << (y + fila - 1).bit_length()
    return uv, alto, unicas


def huecos(u, v, w, h, d):
    """Donde va cada cara del boceto en el desplegado de ModelPart (la de abajo, volteada)."""
    return {'arriba': (u + d, v, w, d), 'abajo': (u + d + w, v, w, d), 'izq': (u, v + d, d, h),
            'frente': (u + d, v + d, w, h), 'der': (u + d + w, v + d, d, h), 'atras': (u + 2 * d + w, v + d, w, h)}


TAM_CARA = {'frente': lambda w, h, d: (w, h), 'atras': lambda w, h, d: (w, h), 'der': lambda w, h, d: (d, h),
            'izq': lambda w, h, d: (d, h), 'arriba': lambda w, h, d: (w, d), 'abajo': lambda w, h, d: (w, d)}


def pintar(uv, alto, unicas):
    base = np.zeros((alto * K, ANCHO * K, 4), np.uint8)
    brillo = np.zeros_like(base)
    for k, caja in unicas.items():
        u, v = uv[k]
        _, x0, y0, z0, w, h, d, pint = caja
        for cara, (fx, fy, fw, fh) in huecos(u, v, w, h, d).items():
            f = pint[cara]
            if f is None or fw <= 0 or fh <= 0:
                continue
            tw, th = max(1, int(round(TAM_CARA[cara](w, h, d)[0]))), max(1, int(round(TAM_CARA[cara](w, h, d)[1])))
            tex, emis = f(tw, th, cara, 7)
            if f in bm.PLENOS:
                emis = tex.copy()
            if cara == 'abajo':
                tex = tex[::-1]
                emis = emis[::-1] if emis is not None else None
            X0, Y0 = int(round(fx * K)), int(round(fy * K))
            X1, Y1 = max(X0 + 1, int(round((fx + fw) * K))), max(Y0 + 1, int(round((fy + fh) * K)))
            t = np.array(Image.fromarray(tex).resize((X1 - X0, Y1 - Y0), Image.NEAREST))
            base[Y0:Y1, X0:X1] = t
            if emis is not None:
                e = np.array(Image.fromarray(emis).resize((X1 - X0, Y1 - Y0), Image.NEAREST)).astype(float)
                a = e[..., 3:4] / 255.0
                rgb = (e[..., :3] * a).astype(np.uint8)
                brillo[Y0:Y1, X0:X1, :3] = np.maximum(brillo[Y0:Y1, X0:X1, :3], rgb)
                brillo[Y0:Y1, X0:X1, 3] = np.maximum(brillo[Y0:Y1, X0:X1, 3], (a[..., 0] > 0) * 255)
    return base, brillo


# ----------------------------------------------------------------------
#  Java
# ----------------------------------------------------------------------
def f_(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    return ('0' if s in ('-0', '') else s) + 'F'


def java(uv, alto):
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '',
         '/**',
         ' * La malla del Fogonazo. GENERADO por materiales/generadores/fogonazo_juego.py: no se edita a mano (la textura se',
         ' * pinta con la misma cuadricula). Las partes con nombre son las que mueve FogonazoModel; cada caja va en su',
         ' * propia pieza ("_c" y un numero) con su giro.',
         ' */',
         'public final class FogonazoMalla {', '',
         '    private FogonazoMalla() {', '    }', '',
         '    public static LayerDefinition crear() {',
         '        MeshDefinition malla = new MeshDefinition();',
         '        PartDefinition raiz = malla.getRoot();']
    for n in ORDEN:
        p = PARTES[n]
        (px, py, pz), (rx, ry, rz) = pose_mc(local_mc(n))
        padre = 'raiz' if p.padre is None else 'p_' + p.padre
        L.append(f'        PartDefinition p_{n} = {padre}.addOrReplaceChild("{n}", CubeListBuilder.create(),')
        L.append(f'                PartPose.offsetAndRotation({f_(px)}, {f_(py)}, {f_(pz)}, {f_(rx)}, {f_(ry)}, {f_(rz)}));')
        for i, caja in enumerate(p.cajas):
            B, (x0, y0, z0, w, h, d) = caja_mc(p, caja)
            (bx, by, bz), (ax, ay, az) = pose_mc(B)
            u, v = uv[clave(caja)]
            L.append(f'        p_{n}.addOrReplaceChild("{n}_c{i}", CubeListBuilder.create().texOffs({u}, {v})'
                     f'.addBox({f_(x0)}, {f_(y0)}, {f_(z0)}, {f_(w)}, {f_(h)}, {f_(d)}),')
            L.append(f'                PartPose.offsetAndRotation({f_(bx)}, {f_(by)}, {f_(bz)}, {f_(ax)}, {f_(ay)}, {f_(az)}));')
    L += [f'        return LayerDefinition.create(malla, {ANCHO}, {alto});', '    }', '}', '']
    return '\n'.join(L)


# ----------------------------------------------------------------------
#  La vista previa: la malla de Minecraft, con su textura, de vuelta al boceto
# ----------------------------------------------------------------------
def quads(uv, alto, mat):
    Ainv = np.linalg.inv(A)
    out = []
    mundo = {}
    for n in ORDEN:
        p = PARTES[n]
        mundo[n] = (np.eye(4) if p.padre is None else mundo[p.padre]) @ _matriz(local_mc(n))
        for caja in p.cajas:
            B, (x0, y0, z0, w, h, d) = caja_mc(p, caja)
            M = Ainv @ mundo[n] @ _matriz(B)
            u, v = uv[clave(caja)]
            x1, y1, z1 = x0 + w, y0 + h, z0 + d
            V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
                 4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
            f4, f5, f6, f7 = u, u + d, u + d + w, u + d + w + w
            f8, f9 = u + d + w + d, u + d + w + d + w
            f10, f11, f12 = v, v + d, v + d + h
            caras = [((5, 4, 0, 1), f5, f10, f6, f11), ((2, 3, 7, 6), f6, f11, f7, f10),
                     ((0, 4, 7, 3), f4, f11, f5, f12), ((1, 0, 3, 2), f5, f11, f6, f12),
                     ((5, 1, 2, 6), f6, f11, f8, f12), ((4, 5, 6, 7), f8, f11, f9, f12)]
            for idx, u1, v1, u2, v2 in caras:
                P4 = [(M @ np.array([*V[i], 1.0]))[:3] / 16.0 for i in idx]
                if np.linalg.norm(np.cross(P4[1] - P4[0], P4[3] - P4[0])) < 1e-9:
                    continue
                UV = [(u2 / ANCHO, v1 / alto), (u1 / ANCHO, v1 / alto), (u1 / ANCHO, v2 / alto), (u2 / ANCHO, v2 / alto)]
                out.append((P4, UV, mat))
    return out


def _matriz(L):
    (px, py, pz), (rx, ry, rz) = pose_mc(L)
    return T(px, py, pz) @ Rz(rz) @ Ry(ry) @ Rx(rx)


# ----------------------------------------------------------------------
#  El huevo, los nombres y lo del objeto
# ----------------------------------------------------------------------
SILUETA = [(2, 6, 9), (3, 5, 10), (4, 4, 11), (5, 3, 12), (6, 3, 12), (7, 2, 13), (8, 2, 13), (9, 2, 13),
           (10, 2, 13), (11, 2, 13), (12, 2, 13), (13, 3, 12), (14, 4, 11), (15, 5, 10)]


def huevo():
    """El huevo, al estilo de huevos_jefes.py (la silueta de vanilla, la luz desde arriba a la izquierda y el contorno
    de dos tonos): la piel pizarra, el escudo rojo teja con la mancha arriba, las antenas que asoman, los ojos con el
    canto encendido, la boca y, abajo, el farol en bandas."""
    def c(h):
        return (*nm._hex(h), 255)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    filas = {f: (a, b) for f, a, b in SILUETA}
    for f, (a, b) in filas.items():
        for x in range(a, b + 1):
            fuera_arriba = f - 1 in filas and not (filas[f - 1][0] <= x <= filas[f - 1][1])
            fuera_abajo = f + 1 in filas and not (filas[f + 1][0] <= x <= filas[f + 1][1])
            borde = x in (a, b) or f in (2, 15) or fuera_arriba or fuera_abajo
            luz = (x - a) / max(1, b - a) + (f - 2) / 13
            if borde:
                px[x, f] = c('0e1014') if luz > 0.9 else c('181c22')
            else:
                px[x, f] = c('343e48') if luz < 0.45 else c('242a32') if luz < 1.25 else c('1c2026')
    for f, xs, col in ((2, range(6, 10), 'c4563a'), (3, range(5, 11), 'c4563a'), (4, range(4, 12), '6e2a20'),
                       (5, range(4, 12), '6e2a20'), (6, range(4, 12), 'c4563a')):
        for x in xs:
            px[x, f] = c(col)
    for x, f in ((7, 4), (8, 4), (7, 5), (8, 5)):
        px[x, f] = c('0e1014')                                          # la mancha del escudo
    px[6, 2] = px[9, 2] = c('e07a5a')                                   # el brillo del escudo
    for x, f in ((5, 1), (4, 0), (10, 1), (11, 0)):
        px[x, f] = c('2a2e34')                                          # las antenas
    for x in (4, 5, 10, 11):                                            # los ojos compuestos
        px[x, 7] = c('0e1014')
        px[x, 8] = c('d8a046')
    px[7, 8] = px[8, 8] = c('fff0cc')                                   # la boca encendida
    for f, col in ((10, 'fffaf0'), (11, '7a5420'), (12, 'ffd894'), (13, '7a5420'), (14, 'd8a046')):
        a, b = filas[f]
        for x in range(a + 1, b):
            px[x, f] = c(col)                                           # el farol, en bandas
    return im


def objeto(raiz):
    import json, collections
    item = os.path.join(raiz, 'src/main/resources/assets/atalaya')
    huevo().save(os.path.join(item, 'textures/item/huevo_fogonazo.png'))
    with open(os.path.join(item, 'items/huevo_fogonazo.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'model': {'type': 'minecraft:model', 'model': 'atalaya:item/huevo_fogonazo'}}, fh, indent=2)
        fh.write('\n')
    with open(os.path.join(item, 'models/item/huevo_fogonazo.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'atalaya:item/huevo_fogonazo'}}, fh,
                  indent=2)
        fh.write('\n')
    for idioma, nombres in (('es_es', ('Fogonazo', 'Huevo generador de fogonazo')),
                            ('en_us', ('Fogonazo', 'Fogonazo Spawn Egg'))):
        ruta = os.path.join(item, f'lang/{idioma}.json')
        d = json.load(open(ruta, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        nuevo = collections.OrderedDict()
        for k, v in d.items():
            if k in ('entity.atalaya.fogonazo', 'item.atalaya.huevo_fogonazo'):
                continue
            nuevo[k] = v
            if k == 'item.atalaya.huevo_fulminante':
                nuevo['entity.atalaya.fogonazo'] = nombres[0]
                nuevo['item.atalaya.huevo_fogonazo'] = nombres[1]
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(nuevo, fh, indent=2, ensure_ascii=False)
            fh.write('\n')


def main():
    raiz = sys.argv[1]
    objeto(raiz)
    construir()
    uv, alto, unicas = empaquetar()
    base, brillo = pintar(uv, alto, unicas)
    tex_dir = os.path.join(raiz, 'src/main/resources/assets/atalaya/textures/entity/fogonazo')
    os.makedirs(tex_dir, exist_ok=True)
    Image.fromarray(base).save(os.path.join(tex_dir, 'fogonazo.png'))
    Image.fromarray(brillo).save(os.path.join(tex_dir, 'fogonazo_brillo.png'))
    with open(os.path.join(raiz, 'src/client/java/com/atalaya/client/FogonazoMalla.java'), 'w', encoding='utf-8',
              newline='\n') as fh:
        fh.write(java(uv, alto))
    n = sum(len(PARTES[k].cajas) for k in ORDEN)
    print('ok', len(ORDEN), 'partes', n, 'cajas', len(unicas), 'distintas; atlas', ANCHO, 'x', alto, '(x%d)' % K)
    if len(sys.argv) > 2:
        vista_previa(sys.argv[2], uv, alto, base)


def vista_previa(carpeta, uv, alto, base):
    import quimeras_escenas as qe
    os.makedirs(carpeta, exist_ok=True)
    qm._reg('fogonazo_atlas', base, None, estira=True)
    qs = quads(uv, alto, 'fogonazo_atlas')
    for nombre, ojo, obj in (('previa_heroe', (1.75, 0.48, 2.95), (0.0, 0.66, 0.1)),
                             ('previa_lado', (3.2, 0.75, 0.3), (0.0, 0.62, 0.0))):
        W, H = 800, 500
        lz = qe.Lienzo(W, H)
        cam = vr.Camara(ojo, obj, 48, W, H)
        luces = [((-0.5, 0.75, 0.4), (0.9, 0.95, 1.0), 0.8, 'llave'), ((0.6, 0.4, -0.8), (0.6, 0.7, 1.0), 0.5, 'contra')]
        qm.dibujar(lz, cam, qs, luces, (0.35, 0.37, 0.42), None, 1.2)
        arr = lz.color * lz.alfa[..., None] + np.array((0.1, 0.12, 0.16)) * (1 - lz.alfa[..., None])
        Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(os.path.join(carpeta, nombre + '.png'))
    print('vista previa en', carpeta)


if __name__ == '__main__':
    main()
