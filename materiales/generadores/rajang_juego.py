"""
Rajang, el Jaguar de Jade, para el juego: el modelo de la ficha
(tierra_modelo.py) pasado a piezas animables, su atlas de textura por fases
pintado cara por cara (tierra_piel.py) y el codigo Java que lo construye.

Es la UNICA fuente de la geometria del juego. De aqui salen:
  - src/client/.../RajangMalla.java              piezas, cajas y texOffs
  - textures/entity/rajang/rajang_fN.png         el atlas de cada fase (1-4)
  - textures/entity/rajang/rajang_brillo_fN.png  lo que brilla (ojos, boca,
                                                 grietas, cristales, el sol)
  - textures/entity/rajang/rajang_libre.png y rajang_brillo_libre.png
                                                 la liberacion: jade de la
                                                 fase I y las grietas en oro
  - textures/entity/rajang/rajang_coloso.png (+ brillo): el Coloso de Tierra
                                                 del Sello, la misma malla en
                                                 tierra y roca
y rajang_juego_anim.py importa este modulo para animar y sacar los puntos
que usa el servidor.

Unidades: pixeles de modelo, Y hacia abajo, el frente mira a -Z, los pies en
y=24 (como cualquier modelo de Minecraft). El atlas va a un texel por pixel:
cada caja tiene su propio hueco (ninguna se repite) y cada texel se pinta
segun el punto del cuerpo en reposo al que va, asi que las rosetas, el
mosaico, las espirales de oro y las grietas salen igual que en la ficha.

El peto de oro y el sol del pecho van en piezas propias: el peto se cae en la
fase IV y el sol late. Los cristales crecen con la fase escalando su pieza
desde la base (lo hace el modelo del cliente).
"""
import math
import numpy as np
from PIL import Image
import vigia_render as vr
import tierra_modelo as tm
import tierra_piel as tp

ANCHO_ATLAS = 1024
D2R = math.pi / 180
# El origen de la entidad va al pecho, no a la cintura: el cuerpo mide 17
# bloques y la caja principal tapa el pecho y las patas de delante; la cabeza
# y la grupa llevan cajas propias (RajangParteEntity). Toda la malla se echa
# atras 3,5 bloques.
DESPLAZA = 56.0


class Parte:
    def __init__(self, nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]      # (x0, y0, z0, w, h, d, mat)
        self.hijos = []


PARTES = {}
ORDEN = []
EMISIVOS = {'ojo', 'brillo'}
CRISTALES = []      # piezas que crecen con la fase (escaladas desde su base)


def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
    assert nombre not in PARTES, nombre
    p = Parte(nombre, padre, pivote, rot, cajas)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    return p


def construir():
    PARTES.clear()
    ORDEN.clear()
    CRISTALES.clear()
    raiz = tm.esqueleto(1)

    def visitar(n, padre):
        nombre, off, rot, cajas, hijos = n
        propias, peto, sol = [], [], []
        for box, mat in cajas:
            if nombre == 'cuerpo' and mat == 'oro' and abs(box[2] + 117.5) < 0.01:
                peto.append((*box, mat))
            elif mat == 'sol_img':
                sol.append((*box, mat))
            else:
                propias.append((*box, mat))
        parte(nombre, padre, off, rot, propias)
        if any(m == 'cristal' for *_, m in propias):
            CRISTALES.append(nombre)
        if peto:
            parte('peto', nombre, (0, 0, 0), (0, 0, 0), peto)
        if sol:
            parte('sol', nombre, (0, 0, 0), (0, 0, 0), sol)
        for h in hijos:
            visitar(h, nombre)

    visitar(raiz, None)
    PARTES['raiz'].pivote = (0.0, 0.0, DESPLAZA)


# ----------------------------------------------------------------------
#  Cinematica directa
# ----------------------------------------------------------------------
def matrices(pose=None):
    pose = pose or {}
    out = {}

    def visitar(p, M):
        ex = pose.get(p.nombre, {})
        r = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        e = ex.get('esc', (1, 1, 1))
        L = vr.T(*q) @ vr.Rz(r[2] * D2R) @ vr.Ry(r[1] * D2R) @ vr.Rx(r[0] * D2R) @ np.diag([e[0], e[1], e[2], 1.0])
        Mn = M @ L
        out[p.nombre] = Mn
        for h in p.hijos:
            visitar(h, Mn)

    for n in ORDEN:
        if PARTES[n].padre is None:
            visitar(PARTES[n], np.eye(4))
    return out


def punto(pose, pieza, local=(0, 0, 0)):
    M = matrices(pose)[pieza]
    return (M @ np.array([*local, 1.0]))[:3]


def a_bloques(p):
    """Del modelo (px, Y abajo, frente -Z) al espacio de la entidad en bloques:
    (izquierda, alto, frente)."""
    return (p[0] / 16, (24.016 - p[1]) / 16, -p[2] / 16)


# ----------------------------------------------------------------------
#  Atlas UV: un hueco por caja, a un texel por pixel
# ----------------------------------------------------------------------
def tam_uv(c):
    x0, y0, z0, w, h, d, mat = c
    return int(math.ceil(2 * (d + w))) + 2, int(math.ceil(d + h)) + 2


def empaquetar():
    claves = {}
    for n in ORDEN:
        for i, c in enumerate(PARTES[n].cajas):
            claves[(n, i)] = c
    orden = sorted(claves, key=lambda k: (-tam_uv(claves[k])[1], -tam_uv(claves[k])[0]))
    uv = {}
    x = y = fila = 0
    for k in orden:
        w, h = tam_uv(claves[k])
        if x + w > ANCHO_ATLAS:
            x, y, fila = 0, y + fila, 0
        uv[k] = (x, y)
        x += w
        fila = max(fila, h)
    alto = y + fila
    return uv, 1 << (alto - 1).bit_length()


# ----------------------------------------------------------------------
#  Las caras del atlas como caras de tierra_piel (con sus texeles)
# ----------------------------------------------------------------------
def caras_atlas(uv):
    """Lista de (cara, region (X0, Y0, X1, Y1)) y las cajas para la sombra de
    contacto, todo en el cuerpo en reposo."""
    # sin el desplazamiento: la piel se pinta en las medidas de tierra_modelo
    atras = vr.T(0, 0, -DESPLAZA)
    Ms = {n: atras @ M for n, M in matrices().items()}
    cajas, caras = [], []
    indice = {}
    for n in ORDEN:
        Mn = Ms[n]
        inv = np.linalg.inv(Mn)
        for i, c in enumerate(PARTES[n].cajas):
            x0, y0, z0, w, h, d, mat = c
            indice[(n, i)] = len(cajas)
            cajas.append((Mn, inv, np.array([x0 + w / 2, y0 + h / 2, z0 + d / 2]), np.array([w / 2, h / 2, d / 2]), n, i))
    for n in ORDEN:
        Mn = Ms[n]
        R = Mn[:3, :3]
        for i, c in enumerate(PARTES[n].cajas):
            x0, y0, z0, w, h, d, mat = c
            centro_l = np.array([x0 + w / 2, y0 + h / 2, z0 + d / 2])
            u, v = uv[(n, i)]
            for ic, (pts, uvs) in enumerate(vr.caja_quads((u, v), c[:6], False, 1, 1)):
                (a2, b1), (a1, _), (_, b2), _ = uvs
                p0, p1, p2 = (np.array(pts[k], float) for k in (0, 1, 2))
                a, b = np.linalg.norm(p0 - p1), np.linalg.norm(p2 - p1)
                if a < 1e-6 or b < 1e-6:
                    continue
                X0, X1 = int(math.floor(min(a1, a2) + 1e-6)), int(math.ceil(max(a1, a2) - 1e-6))
                Y0, Y1 = int(math.floor(min(b1, b2) + 1e-6)), int(math.ceil(max(b1, b2) - 1e-6))
                if X1 <= X0 or Y1 <= Y0:
                    continue
                xs, ys = np.meshgrid(np.arange(X0, X1) + 0.5, np.arange(Y0, Y1) + 0.5)
                s = np.clip((xs - a1) / (a2 - a1), 0, 1).ravel()
                t = np.clip((ys - b1) / (b2 - b1), 0, 1).ravel()
                L = p1 + s[:, None] * (p0 - p1) + t[:, None] * (p2 - p1)
                P = (np.c_[L, np.ones(len(L))] @ Mn.T)[:, :3]
                k = tp.Cara()
                k.clave, k.mat, k.nodo, k.region = (n, i, ic), mat, n, tp.region(n)
                k.a, k.b = a, b
                k.Ol, k.eul, k.evl = p1, (p0 - p1) / a, (p2 - p1) / b
                k.O = (Mn @ np.array([*p1, 1.0]))[:3]
                k.eu, k.ev = R @ k.eul, R @ k.evl
                nn = np.cross(k.eu, k.ev)
                medio = (Mn @ np.array([*((p0 + p2) / 2), 1.0]))[:3]
                centro = (Mn @ np.array([*centro_l, 1.0]))[:3]
                if nn @ (medio - centro) < 0:
                    nn = -nn
                k.n = nn / max(np.linalg.norm(nn), 1e-9)
                k.caja = indice[(n, i)]
                k.texeles = (X1 - X0, Y1 - Y0, s * a, t * b, P, L)
                caras.append((k, (X0, Y0, X1, Y1)))
    return caras, cajas


# ----------------------------------------------------------------------
#  Pintar el atlas
# ----------------------------------------------------------------------
_hex = tm._hex


def paleta(fase):
    """La paleta de una fase: 1-4, 'libre' (jade de la fase I con las grietas
    cerradas en oro y los ojos en oro) o 'coloso' (tierra y roca)."""
    if fase == 'libre':
        P = dict(tm.FASES[1])
        P['grieta'] = ('fff6d0', 'f0c24a')
        P['ojo'] = ('fffbe0', 'ffc23a')
        P['boca'] = ('ffe9a8', '8a6418')
        P['sol'] = ('fff6d0', 'e2b443')
        P['cristal'] = ('fff6d8', 'd8b24a')
        return P, 4
    if fase == 'coloso':
        return dict(tm.FASES[5]), 5
    return dict(tm.FASES[fase]), fase


def _sol_de(P, fase, n=64):
    c, b = _hex(P['sol'][0]), _hex(P['sol'][1])
    J = P['jade']
    oro = P['oro'][2]
    t = np.zeros((n, n, 4), np.uint8)
    gl = np.zeros((n, n, 4), np.uint8)
    k_ = min(fase, 4)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx)
            if d > 1.0:
                t[y, x] = (*J[1], 255)
                continue
            if d > 0.86:
                t[y, x] = (*oro, 255)
            elif d > 0.55:
                rayo = (int((ang + math.pi) / (2 * math.pi) * 16) % 2 == 0)
                t[y, x] = (*(J[3] if rayo else J[1]), 255)
                if rayo and k_ >= 2 and 0.6 < d < 0.8:
                    gl[y, x] = (*b, 120 + 30 * k_)
            elif d > 0.3:
                t[y, x] = (*J[1], 255)
                if abs(d - 0.42) < 0.05:
                    t[y, x] = (*b, 255)
                    gl[y, x] = (*b, 200)
            else:
                kk = 1 - d / 0.3
                col = tuple(int(b[i] + (c[i] - b[i]) * kk) for i in range(3))
                t[y, x] = (*col, 255)
                gl[y, x] = (*col, 180 + 15 * k_)
    return t, gl


def _premul(emis):
    k = emis[:, 3:4] / 255.0
    return np.c_[emis[:, :3] * k, np.where(emis[:, 3] > 0, 255, 0)]


def pintar_atlas(uv, alto, fase=1):
    """(base, brillo) del atlas. fase: 1-4, 'libre' o 'coloso'."""
    P, f_pint = paleta(fase)
    base = np.zeros((alto, ANCHO_ATLAS, 4), np.uint8)
    brillo = np.zeros_like(base)
    caras, cajas = caras_atlas(uv)
    ros = tp.sembrar_rosetas([c for c, _ in caras], cajas)
    for c, (X0, Y0, X1, Y1) in caras:
        w, h = X1 - X0, Y1 - Y0
        if c.mat in tp.PIEL:
            _, _, col, emis = tp._piel(c, f_pint, P, ros, cajas)
        elif c.mat in tp.PINTORES:
            _, _, col, emis = tp.PINTORES[c.mat](c, f_pint, P, cajas)
        elif c.mat == 'sol_img':
            im, g = _sol_de(P, f_pint)
            im = np.array(Image.fromarray(im).resize((w, h), Image.NEAREST))
            g = np.array(Image.fromarray(g).resize((w, h), Image.NEAREST))
            if c.n[2] > 0:      # la cara de atras, en espejo
                im, g = im[:, ::-1], g[:, ::-1]
            base[Y0:Y1, X0:X1] = im
            brillo[Y0:Y1, X0:X1] = g
            continue
        else:   # ojos (y lo que brille entero): degradado del claro al color
            a_, b_ = np.array(_hex(P['ojo'][0]), float), np.array(_hex(P['ojo'][1]), float)
            _, _, U, V, _, _ = c.texeles
            dd = np.maximum(np.abs(U / c.a - 0.5), np.abs(V / c.b - 0.5)) * 2
            col = a_ * (1 - dd[:, None]) + b_ * dd[:, None]
            emis = np.c_[col, np.full(len(col), 255)]
        tex = np.zeros((h * w, 4))
        tex[:, :3] = np.clip(col, 0, 255)
        tex[:, 3] = 255
        base[Y0:Y1, X0:X1] = tex.reshape(h, w, 4).astype(np.uint8)
        if emis[:, 3].max() > 0:
            brillo[Y0:Y1, X0:X1] = np.clip(_premul(emis), 0, 255).reshape(h, w, 4).astype(np.uint8)
    return base, brillo


# ----------------------------------------------------------------------
#  Exportar a Java
# ----------------------------------------------------------------------
def f(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def var(n):
    return 'p_' + n


def java_malla(uv, alto):
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeDeformation;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '',
         '/**',
         ' * La malla de Rajang, el Jaguar de Jade. GENERADO por',
         ' * materiales/generadores/rajang_juego.py: no se edita a mano. Cada caja tiene su',
         ' * hueco en el atlas (' + str(ANCHO_ATLAS) + 'x' + str(alto) + ', un texel por pixel) y se pinta segun',
         ' * donde cae en el cuerpo: cambiar una caja aqui sin el script descuadra la piel.',
         ' */',
         'public final class RajangMalla {', '',
         '    /** Las piezas de cristal, que crecen con la fase (escaladas desde su base). */',
         '    public static final String[] CRISTALES = {' + ', '.join(f'"{c}"' for c in CRISTALES) + '};', '',
         '    private RajangMalla() {', '    }', '',
         '    public static LayerDefinition crear() {',
         '        return crear(CubeDeformation.NONE);',
         '    }', '',
         '    /** La misma malla hinchada: la capa del aura de la Furia (como la carga del creeper). */',
         '    public static LayerDefinition crearAura() {',
         '        return crear(new CubeDeformation(1.5F));',
         '    }', '',
         '    private static LayerDefinition crear(CubeDeformation infla) {',
         '        MeshDefinition malla = new MeshDefinition();',
         '        PartDefinition p_root = malla.getRoot();']
    for n in ORDEN:
        p = PARTES[n]
        padre = var(p.padre) if p.padre else 'p_root'
        cub = 'CubeListBuilder.create()'
        for i, c in enumerate(p.cajas):
            u, v = uv[(n, i)]
            cub += f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, {f(c[3])}, {f(c[4])}, {f(c[5])}, infla)'
        rx, ry, rz = [r * D2R for r in p.rot]
        pose = f'PartPose.offsetAndRotation({f(p.pivote[0])}, {f(p.pivote[1])}, {f(p.pivote[2])}, {f(rx)}, {f(ry)}, {f(rz)})'
        decl = f'PartDefinition {var(n)} = ' if p.hijos else ''
        L.append(f'        {decl}{padre}.addOrReplaceChild("{n}", {cub},\n                {pose});')
    L.append(f'        return LayerDefinition.create(malla, {ANCHO_ATLAS}, {alto});')
    L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  Cuadrilateros con el UV real del atlas (para los renders de control)
# ----------------------------------------------------------------------
def quads(pose, uv, alto, modelo_a_mundo):
    Ms = matrices(pose)
    out = []
    for n in ORDEN:
        q = n
        oculto = False
        while q:
            if pose.get(q, {}).get('oculto'):
                oculto = True
            q = PARTES[q].padre
        if oculto:
            continue
        M = modelo_a_mundo @ Ms[n]
        for i, c in enumerate(PARTES[n].cajas):
            u, v = uv[(n, i)]
            for pts, uvs in vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(M @ np.array([*q_, 1.0]))[:3] for q_ in pts]
                out.append((w, uvs, n, c[6]))
    return out


construir()
