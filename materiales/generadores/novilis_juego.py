"""
Novilis, el Caballero Solar, para el juego: el boceto aprobado (fuego_modelo.py,
variante N: los cuernos de la A, el halo de la B y el cuerpo de la ronda 2)
pasado a piezas animables, con su atlas de textura y el Java que lo construye.

Es la UNICA fuente de la geometria. De aqui salen:
  - src/client/.../NovilisMalla.java          las piezas, cajas y texOffs
  - textures/entity/novilis/novilis_f1..f4    la piel de cada fase (las grietas
    novilis_furia, novilis_libre               de lava van pintadas del color de la
                                               fase) y la de la Furia y la liberacion
  - textures/entity/novilis/novilis_brillo_*  lo que brilla (grietas, lava, nucleo,
                                               corona del halo, la T, la hoja)
y novilis_juego_anim.py importa este modulo para animar y para sacar los puntos
que usa el servidor (manos, pecho, punta de la espada, su sol).

Unidades: pixeles de modelo, Y hacia abajo, el frente mira a -Z, pies en y=24.
El renderer escala x1,753: el yelmo queda a 16 bloques del suelo y el aro del
halo a unos 18 (lo que pidio Juan).

Las piezas, los nombres y las cajas son los mismos que los del boceto
(fuego_modelo.esqueleto_n): las poses de la ficha valen tal cual.
"""
import math, random, os
import numpy as np
from PIL import Image
import vigia_render as vr
import nerea_modelo as nm
import fuego_modelo as fm

# El yelmo, de y=24 (pies) a y=-122: 146 px. 16 bloques son 256 px.
ESCALA = 256.0 / 146.0
D2R = math.pi / 180

# La liberacion: las grietas se enfrian a oro calmo.
fm.FASE['libre'] = ('fff8e0', 'ffd86a', 'b8862a')
fm.GRIETAS['libre'] = 1
fm.NOMBRE_FASE['libre'] = 'Libre'

PIELES = [1, 2, 3, 4, 'furia', 'libre']
NOMBRE_PIEL = {1: 'f1', 2: 'f2', 3: 'f3', 4: 'f4', 'furia': 'furia', 'libre': 'libre'}


class Parte:
    def __init__(self, nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]      # (x0, y0, z0, w, h, d, mat)
        self.hijos = []


PARTES = {}
ORDEN = []
# La espada clavada en el suelo (Ofrenda y Dios de la Guerra): donde la deja la
# animacion. La rellena novilis_juego_anim.py antes de exportar: (pivote, rot).
ESPADA_SUELTA = {}


def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
    assert nombre not in PARTES, nombre
    p = Parte(nombre, padre, pivote, rot, cajas)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    return p


def _desde_nodo(n, padre):
    nombre, off, rot, cajas, hijos = n
    parte(nombre, padre, off, rot, [(*c[:6], m) for c, m in cajas])
    for h in hijos:
        _desde_nodo(h, nombre)


def construir():
    PARTES.clear()
    ORDEN.clear()
    _desde_nodo(fm.esqueleto_n(con_espada=True), None)
    # La espada suelta, clavada: las mismas cajas que la de la mano, en la raiz.
    piv, rot = ESPADA_SUELTA.get('pose', ((0, 0, -40), (0, 0, 0)))
    _desde_nodo(fm.espada('N', 'espada_suelta'), 'raiz')
    PARTES['espada_suelta'].pivote = tuple(piv)
    PARTES['espada_suelta'].rot = tuple(rot)


# ----------------------------------------------------------------------
#  Cinematica directa
# ----------------------------------------------------------------------
T, Rx, Ry, Rz = vr.T, vr.Rx, vr.Ry, vr.Rz


def matrices(pose=None):
    """Matriz de cada pieza (espacio del modelo) para una pose.

    pose: {pieza: {'rot': (grados que se suman), 'pos': (px que se suman, Y abajo),
                   'esc': (sx, sy, sz) o k, 'oculto': bool}}
    """
    pose = pose or {}
    out = {}

    def visitar(p, M):
        ex = pose.get(p.nombre, {})
        r = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        e = ex.get('esc', (1, 1, 1))
        if not isinstance(e, (tuple, list)):
            e = (e, e, e)
        L = T(*q) @ Rz(r[2] * D2R) @ Ry(r[1] * D2R) @ Rx(r[0] * D2R) @ np.diag([e[0], e[1], e[2], 1.0])
        Mn = M @ L
        out[p.nombre] = Mn
        for h in p.hijos:
            visitar(h, Mn)

    for n in ORDEN:
        if PARTES[n].padre is None:
            visitar(PARTES[n], np.eye(4))
    return out


def punto(pose, pieza, local=(0, 0, 0)):
    """Punto de una pieza en el espacio del modelo (px)."""
    M = matrices(pose)[pieza]
    return (M @ np.array([*local, 1.0]))[:3]


def a_bloques(p):
    """Del modelo (px, Y abajo, frente -Z) al espacio de la entidad en bloques:
    (izquierda, alto, frente), con el factor de escala del renderer."""
    k = ESCALA / 16
    return (p[0] * k, (24.016 - p[1]) * k, -p[2] * k)


# ----------------------------------------------------------------------
#  Atlas UV: cada caja distinta (medidas + material) recibe su hueco
# ----------------------------------------------------------------------
ANCHO_ATLAS = 512


def tam_uv(c):
    x0, y0, z0, w, h, d, mat = c
    return int(math.ceil(2 * (d + w))) + 1, int(math.ceil(d + h)) + 1


def clave(c):
    return (round(c[3], 3), round(c[4], 3), round(c[5], 3), c[6])


def empaquetar():
    claves = {}
    for n in ORDEN:
        for c in PARTES[n].cajas:
            claves.setdefault(clave(c), c)
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
    alto_atlas = 1 << (alto - 1).bit_length()
    return uv, alto_atlas


def caras_uv(u, v, w, h, d):
    """Rectangulos (x, y, ancho, alto) de las seis caras, como ModelPart.Cube."""
    return {
        'arriba': (u + d, v, w, d),
        'abajo': (u + d + w, v, w, d),
        'oeste': (u, v + d, d, h),
        'frente': (u + d, v + d, w, h),
        'este': (u + d + w, v + d, d, h),
        'espalda': (u + 2 * d + w, v + d, w, h),
    }


def pintar_atlas(uv, alto, piel=1):
    """La piel y el brillo de una fase (o de la Furia, o de la liberacion), con los
    materiales en mosaico del boceto: el juego se ve como la ficha."""
    tex, emi, plenos = fm.materiales(piel)
    base = np.zeros((alto, ANCHO_ATLAS, 4), np.uint8)
    brillo = np.zeros_like(base)
    rnd = random.Random(11)
    hechas = set()
    for n in ORDEN:
        for c in PARTES[n].cajas:
            k = clave(c)
            if k in hechas:
                continue
            hechas.add(k)
            u, v = uv[k]
            w, h, d, mat = k
            loseta = tex[mat]
            luz = emi.get(mat)
            estira = mat in fm.ESTIRA
            ox, oy = rnd.randrange(16), rnd.randrange(16)
            for cara, (fx, fy, fw, fh) in caras_uv(u, v, w, h, d).items():
                x0, y0 = int(math.floor(fx)), int(math.floor(fy))
                x1, y1 = int(math.ceil(fx + fw)), int(math.ceil(fy + fh))
                if x1 <= x0 or y1 <= y0:
                    continue
                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        if estira:
                            tx = min(15, int((xx - x0) * 16 / max(1, x1 - x0)))
                            ty = min(15, int((yy - y0) * 16 / max(1, y1 - y0)))
                        else:
                            tx, ty = (xx - x0 + ox) % 16, (yy - y0 + oy) % 16
                        col = loseta[ty, tx].astype(float)
                        if mat not in plenos:
                            j = (yy - y0) / max(1, (y1 - y0 - 1))
                            if cara == 'abajo':
                                col[:3] *= 0.72
                            elif cara != 'arriba':
                                # sombra de contacto abajo y canto claro arriba
                                if yy == y1 - 1 and y1 - y0 > 2:
                                    col[:3] *= 0.8
                                elif yy == y0 and y1 - y0 > 2:
                                    col[:3] = np.minimum(255, col[:3] * 1.12)
                                col[:3] *= 1.0 - 0.08 * j
                        base[yy, xx] = np.clip(col, 0, 255)
                        if mat in plenos:
                            brillo[yy, xx] = (*loseta[ty, tx][:3], 255)
                        elif luz is not None and luz[ty, tx, 3] > 0:
                            brillo[yy, xx] = luz[ty, tx]
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
         ' * La malla de Novilis, el Caballero Solar. GENERADO por',
         ' * materiales/generadores/novilis_juego.py (y novilis_juego_anim.py): no se edita',
         ' * a mano. Cambiar una caja aqui sin cambiar el script descuadra la textura,',
         ' * que se pinta con la misma cuadricula.',
         ' */',
         'public final class NovilisMalla {', '',
         '    private NovilisMalla() {', '    }', '',
         '    public static LayerDefinition crear() {',
         '        return crear(CubeDeformation.NONE);', '    }', '',
         '    /** La misma malla hinchada: la capa del aura de la Furia y del Dios de la Guerra. */',
         '    public static LayerDefinition crearAura() {',
         '        return crear(new CubeDeformation(0.9F));', '    }', '',
         '    private static LayerDefinition crear(CubeDeformation infla) {',
         '        MeshDefinition malla = new MeshDefinition();',
         '        PartDefinition p_root = malla.getRoot();']
    for n in ORDEN:
        p = PARTES[n]
        padre = var(p.padre) if p.padre else 'p_root'
        cub = 'CubeListBuilder.create()'
        for c in p.cajas:
            u, v = uv[clave(c)]
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
#  Cuadrilateros con el UV real del atlas (para las hojas de control)
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
                break
            q = PARTES[q].padre
        if oculto:
            continue
        M = modelo_a_mundo @ Ms[n]
        for c in PARTES[n].cajas:
            u, v = uv[clave(c)]
            for pts, uvs in vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(M @ np.array([*q_, 1.0]))[:3] for q_ in pts]
                out.append((w, uvs, n))
    return out


construir()

if __name__ == '__main__':
    uv, alto = empaquetar()
    print('piezas', len(ORDEN), 'cajas', sum(len(PARTES[n].cajas) for n in ORDEN), 'atlas', ANCHO_ATLAS, 'x', alto,
          'claves', len(uv))
