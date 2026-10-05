"""
Aeralis, la Mariposa del Vendaval (diseno A), para el juego: la malla del boceto pasada
a piezas animables, su atlas de textura por fases y el codigo Java que la
construye.

Es la UNICA fuente de la geometria. De aqui salen:
  - src/client/.../AeralisMalla.java            piezas, cajas y texOffs
  - textures/entity/aeralis/aeralis_fN.png     el atlas de cada fase
  - textures/entity/aeralis/aeralis_brillo_fN.png  lo que brilla
  - textures/entity/aeralis/aeralis_brillo_libre.png
y vendaval_juego_anim.py importa este modulo para animar y sacar los puntos
que usa el servidor (nucleo, ojos, punta de las alas).

Unidades: pixeles de modelo, Y hacia abajo, el frente mira a -Z, la base de la
caja de golpe (los "pies" de la entidad) en y=24. El renderer NO escala: un
pixel de modelo es 1/16 de bloque.

La textura va a MEDIA resolucion: el atlas se declara de 1024 de ancho y el
PNG mide 512, asi que cada pixel de la imagen cubre dos unidades de modelo
(1/8 de bloque, como Nerea a x1,6). Asi caben unas alas de 12 bloques sin un
atlas enorme.

Las piezas planas (alas, cintas, nucleo) son cajas de grosor cero con una
imagen: la cara de delante la lleva tal cual y la de detras en espejo, para
que desde atras se vea el mismo dibujo traslucido.
"""
import math, random
import numpy as np
from PIL import Image
import nerea_modelo as nm
import viento_modelo as vm

ESCALA = 1.0
DENSIDAD = 2              # unidades de modelo por pixel de la textura
ANCHO_ATLAS = 1024        # ancho declarado (unidades); el PNG mide ANCHO_ATLAS / DENSIDAD

# Medidas de las piezas planas, en unidades de modelo
TAM_SUP = (200, 132)
TAM_INF = (128, 146)
TAM_CINTA = (14, 96)
TAM_NUCLEO = (26, 26)

ALTURA_TORAX = -82        # y del centro del torax (los pies de la entidad en y=24)


class Parte:
    def __init__(self, nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]      # (x0, y0, z0, w, h, d, mat)
        self.hijos = []


PARTES = {}
ORDEN = []


def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
    assert nombre not in PARTES, nombre
    p = Parte(nombre, padre, pivote, rot, cajas)
    PARTES[nombre] = p
    ORDEN.append(nombre)
    if padre:
        PARTES[padre].hijos.append(p)
    return p


# Materiales de imagen (piezas planas): nombre -> (ancho, alto) en unidades
PLANOS = {
    'ala_sup_izq': TAM_SUP, 'ala_sup_der': TAM_SUP,
    'ala_inf_izq': TAM_INF, 'ala_inf_der': TAM_INF,
    'cinta_izq': TAM_CINTA, 'cinta_der': (TAM_CINTA[0], 84),
}
# El nucleo es una caja fina: su cara de delante lleva la imagen del ciclon.
NUCLEO = 'nucleo'
EMISIVOS = {'ojo', 'brillo'}


def construir():
    PARTES.clear()
    ORDEN.clear()
    # El cuerpo: lo que sube, baja y se inclina al volar.
    parte('cuerpo', None, (0, ALTURA_TORAX, 0))
    parte('torax', 'cuerpo', (0, 0, 0), (-8, 0, 0), [
        (-21, -24, -16, 42, 48, 32, 'quitina'),
        (-24, -29, -19, 48, 17, 38, 'pelaje'),              # el collar de pelaje
        (-28, -26, -8, 8, 14, 24, 'pelaje'),                # mechones de los hombros
        (20, -26, -8, 8, 14, 24, 'pelaje'),
        (-15, -9, -17.2, 30, 30, 1.2, 'quitina_osc'),       # peto
        (-19, 22, -15, 38, 4, 30, 'pelaje'),                # pelo de la cintura
    ])
    # El ojo de la tormenta: aparte, para que lata y gire con la fase.
    parte('nucleo', 'torax', (0, 8, -17.6), cajas=[(-13, -13, -0.6, 26, 26, 0.6, NUCLEO)])

    parte('cabeza', 'torax', (0, -27, -5), (12, 0, 0), [
        (-16, -26, -14, 32, 26, 27, 'quitina'),
        (-18, -31, -7, 36, 9, 22, 'pelaje'),                # cresta
        (-5, -7, -15, 10, 7, 1.2, 'quitina_osc'),           # la boca
    ])
    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('ojo_' + n, 'cabeza', (12 * s, -14, -12), (0, 0, -18 * s), [(-5, -8, -4, 10, 15, 13, 'ojo')])
        parte('ceno_' + n, 'cabeza', (8 * s, -21, -16.5), (0, 0, -20 * s),
              [(-7 if s > 0 else -8, -2.5, -1, 15, 4, 5, 'quitina_osc')])
        parte('colmillo_' + n, 'cabeza', (5 * s, -3, -14), (-12, 0, -16 * s), [(-1.6, 0, -1.6, 3.2, 10, 3.2, 'quitina_osc')])
        parte('colmillo_punta_' + n, 'colmillo_' + n, (0, 10, 0), (-30, 0, 34 * s), [(-1.1, 0, -1.1, 2.2, 8, 2.2, 'pelaje')])
        # antenas plumosas: el tallo y sus barbas, y la punta encendida aparte
        barbas = []
        for i in range(13):
            L = 10 - abs(i - 5) * 0.9
            y = -8 - i * 4.4
            barbas.append((0.8, y, -0.6, L, 1.4, 1.2, 'pelaje'))
            barbas.append((-0.8 - L, y, -0.6, L, 1.4, 1.2, 'pelaje'))
        parte('antena_' + n, 'cabeza', (8 * s, -24, -6), (-30, 0, 24 * s),
              [(-1.4, -64, -1.4, 2.8, 64, 2.8, 'quitina_osc'), *barbas])
        parte('antena_punta_' + n, 'antena_' + n, (0, -64, 0), (-46, 0, -12 * s),
              [(-1, -14, -1, 2, 14, 2, 'quitina_osc'), (-1.5, -17, -1.5, 3, 3, 3, 'brillo')])

    # Las alas: planos con su imagen. El pivote es el encaje en el torax.
    for s, n in ((1, 'izq'), (-1, 'der')):
        W, H = TAM_SUP
        parte('ala_sup_' + n, 'torax', (19 * s, -14, 12), (0, -18 * s, -14 * s),
              [(0.0 if s > 0 else -W, -H * 0.42, 0.0, W, H, 0.0, 'ala_sup_' + n)])
        W, H = TAM_INF
        parte('ala_inf_' + n, 'torax', (18 * s, 10, 13), (0, -26 * s, 10 * s),
              [(0.0 if s > 0 else -W, -H * 0.08, 0.0, W, H, 0.0, 'ala_inf_' + n)])

    # Seis patas: las de delante en alto, como un insecto de presa.
    for s, n in ((1, 'izq'), (-1, 'der')):
        for i in range(3):
            rot = [(-38, 0, 34 * s), (-6, 0, 52 * s), (30, 0, 52 * s)][i]
            nom = f'pata{i}_{n}'
            parte(nom, 'torax', (17 * s, -8 + i * 13, -8 + i * 4), rot, [(-2, 0, -2, 4, 28, 4, 'quitina')])
            parte(nom + '_tibia', nom, (0, 28, 0), (-70 if i == 0 else 50, 0, 0), [
                (-1.5, 0, -1.5, 3, 30, 3, 'quitina_osc'),
                *([(-2.5, 6, -2, 1, 16, 1, 'pelaje')] if i == 0 else [])])
            parte(nom + '_garra', nom + '_tibia', (0, 30, 0), (34, 0, 0), [(-2, 0, -0.75, 4, 8, 1.5, 'quitina')])

    # El abdomen: cinco segmentos sueltos para que ondule, y las cintas de viento.
    parte('abdomen', 'torax', (0, 24, 4), (10, 0, 0), [(-17, 0, -14, 34, 20, 28, 'anillos')])
    parte('abdomen2', 'abdomen', (0, 20, 0), (8, 0, 0), [(-14, 0, -11, 28, 18, 22, 'anillos')])
    parte('abdomen3', 'abdomen2', (0, 18, 0), (8, 0, 0), [(-10.5, 0, -8.5, 21, 17, 17, 'anillos')])
    parte('abdomen4', 'abdomen3', (0, 17, 0), (10, 0, 0), [(-7, 0, -6, 14, 14, 12, 'anillos')])
    parte('punta', 'abdomen4', (0, 14, 0), (10, 0, 0), [(-3.5, 0, -3, 7, 9, 6, 'quitina'), (-2, 8, -2, 4, 4, 4, 'brillo')])
    parte('cinta_izq', 'punta', (1.5, 10, 0), (0, 0, -8), [(-7, 0, 0, TAM_CINTA[0], TAM_CINTA[1], 0, 'cinta_izq')])
    parte('cinta_der', 'punta', (-1.5, 10, 0), (0, 0, 10), [(-7, 0, 0, TAM_CINTA[0], 84, 0, 'cinta_der')])


# ----------------------------------------------------------------------
#  Cinematica directa
# ----------------------------------------------------------------------
T, Rx, Ry, Rz, S = nm.vr.T, nm.vr.Rx, nm.vr.Ry, nm.vr.Rz, nm.vr.S
D2R = math.pi / 180


def matrices(pose=None):
    pose = pose or {}
    out = {}

    def visitar(p, M):
        ex = pose.get(p.nombre, {})
        r = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        e = ex.get('esc', (1, 1, 1))
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
    M = matrices(pose)[pieza]
    return (M @ np.array([*local, 1.0]))[:3]


def a_bloques(p):
    """Del modelo (px, Y abajo, frente -Z) al espacio de la entidad en bloques:
    (izquierda, alto, frente)."""
    k = ESCALA / 16
    return (p[0] * k, (24.016 - p[1]) * k, -p[2] * k)


# ----------------------------------------------------------------------
#  Atlas UV (en unidades de modelo; el PNG va a 1/DENSIDAD)
# ----------------------------------------------------------------------
def tam_uv(c):
    x0, y0, z0, w, h, d, mat = c
    return int(math.ceil(2 * (d + w))) + 2, int(math.ceil(d + h)) + 2


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
        # alineado a la densidad: cada caja empieza en un pixel entero del PNG
        w += (-w) % DENSIDAD
        h += (-h) % DENSIDAD
        if x + w > ANCHO_ATLAS:
            x, y, fila = 0, y + fila, 0
        uv[k] = (x, y)
        x += w
        fila = max(fila, h)
    alto = y + fila
    alto_atlas = 1 << (alto - 1).bit_length()
    return uv, alto_atlas


def caras_uv(u, v, w, h, d):
    return {
        'arriba': (u + d, v, w, d),
        'abajo': (u + d + w, v, w, d),
        'oeste': (u, v + d, d, h),
        'frente': (u + d, v + d, w, h),
        'este': (u + d + w, v + d, d, h),
        'espalda': (u + 2 * d + w, v + d, w, h),
    }


# ----------------------------------------------------------------------
#  Las imagenes de las piezas planas, a la resolucion exacta del atlas
# ----------------------------------------------------------------------
def _redim(im, w, h):
    return np.array(Image.fromarray(im).resize((max(1, w), max(1, h)), Image.NEAREST))


def _paleta_libre():
    """La liberacion: la tormenta se despeja (paleta de la fase I) y lo que
    brilla pasa a oro."""
    P = dict(vm.FASES[1])
    P['brillo_c'], P['brillo_b'] = 'fffbe0', 'ffc23a'
    return P


def imagenes(fase):
    """{material: (imagen, brillo)} a la resolucion del PNG. fase: 1-4 o 'libre'."""
    clave_fase = fase
    if fase == 'libre':
        vm.FASES['libre'] = _paleta_libre()
    out = {}
    W, H = TAM_SUP[0] // DENSIDAD, TAM_SUP[1] // DENSIDAD
    sup, gsup = vm._ala(W, H, vm.POLY_SUP, vm.VENAS_SUP, vm.OCELO_SUP, clave_fase, 7)
    W, H = TAM_INF[0] // DENSIDAD, TAM_INF[1] // DENSIDAD
    inf, ginf = vm._ala(W, H, vm.POLY_INF, vm.VENAS_INF, vm.OCELO_INF, clave_fase, 8)
    out['ala_sup_izq'] = (sup, gsup)
    out['ala_sup_der'] = (sup[:, ::-1].copy(), gsup[:, ::-1].copy())
    out['ala_inf_izq'] = (inf, ginf)
    out['ala_inf_der'] = (inf[:, ::-1].copy(), ginf[:, ::-1].copy())
    for nombre, sem in (('cinta_izq', 1), ('cinta_der', 2)):
        im, g = vm._cinta(clave_fase, sem)
        w, h = PLANOS[nombre]
        out[nombre] = (_redim(im, w // DENSIDAD, h // DENSIDAD), _redim(g, w // DENSIDAD, h // DENSIDAD))
    nuc, gnuc = vm._nucleo(clave_fase)
    n = TAM_NUCLEO[0] // DENSIDAD
    out[NUCLEO] = (_redim(nuc, n, n), _redim(gnuc, n, n))
    if fase == 'libre':
        del vm.FASES['libre']
    return out


# ----------------------------------------------------------------------
#  Pintar el atlas de una fase
# ----------------------------------------------------------------------
def pintar_atlas(uv, alto, fase=1):
    """Devuelve (base, brillo) en la resolucion del PNG. fase: 1-4 o 'libre'
    (la liberacion: la piel de la fase I y el brillo en oro)."""
    ancho_png, alto_png = ANCHO_ATLAS // DENSIDAD, alto // DENSIDAD
    base = np.zeros((alto_png, ancho_png, 4), np.uint8)
    brillo = np.zeros_like(base)
    f_tex = 1 if fase == 'libre' else fase
    if fase == 'libre':
        vm.FASES['libre'] = _paleta_libre()
        mats = vm.materiales('libre')
        del vm.FASES['libre']
    else:
        mats = vm.materiales(f_tex)
    imgs = imagenes(fase)
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
            if mat in PLANOS or mat == NUCLEO:
                im, gl = imgs[mat]
                caras = caras_uv(u, v, w, h, d)
                for cara, espejo in (('frente', False), ('espalda', True)):
                    fx, fy, fw, fh = caras[cara]
                    x0, y0 = int(round(fx / DENSIDAD)), int(round(fy / DENSIDAD))
                    x1, y1 = int(round((fx + fw) / DENSIDAD)), int(round((fy + fh) / DENSIDAD))
                    if x1 <= x0 or y1 <= y0:
                        continue
                    a, b = im, gl
                    if a.shape[0] != y1 - y0 or a.shape[1] != x1 - x0:
                        a, b = _redim(a, x1 - x0, y1 - y0), _redim(b, x1 - x0, y1 - y0)
                    if espejo:
                        a, b = a[:, ::-1], b[:, ::-1]
                    base[y0:y1, x0:x1] = a
                    brillo[y0:y1, x0:x1] = b
                if mat == NUCLEO:
                    # los cantos del nucleo, de quitina oscura
                    for cara in ('arriba', 'abajo', 'oeste', 'este'):
                        fx, fy, fw, fh = caras[cara]
                        x0, y0 = int(math.floor(fx / DENSIDAD)), int(math.floor(fy / DENSIDAD))
                        x1, y1 = int(math.ceil((fx + fw) / DENSIDAD)), int(math.ceil((fy + fh) / DENSIDAD))
                        if x1 > x0 and y1 > y0:
                            base[y0:y1, x0:x1] = (*vm.FASES[f_tex]['quitina'][0], 255)
                continue
            loseta = mats[mat]
            ox, oy = rnd.randrange(16), rnd.randrange(16)
            for cara, (fx, fy, fw, fh) in caras_uv(u, v, w, h, d).items():
                x0, y0 = int(math.floor(fx / DENSIDAD)), int(math.floor(fy / DENSIDAD))
                x1, y1 = int(math.ceil((fx + fw) / DENSIDAD)), int(math.ceil((fy + fh) / DENSIDAD))
                if x1 <= x0 or y1 <= y0:
                    continue
                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        col = loseta[(yy - y0 + oy) % 16, (xx - x0 + ox) % 16].astype(float)
                        j = (yy - y0) / max(1, (y1 - y0 - 1))
                        if mat not in EMISIVOS:
                            if cara == 'abajo':
                                col[:3] *= 0.72
                            elif cara != 'arriba':
                                if yy == y1 - 1 and y1 - y0 > 2:
                                    col[:3] *= 0.8
                                elif yy == y0 and y1 - y0 > 2:
                                    col[:3] = np.minimum(255, col[:3] * 1.12)
                                col[:3] *= 1.0 - 0.10 * j
                        base[yy, xx] = np.clip(col, 0, 255)
                        if mat in EMISIVOS:
                            brillo[yy, xx] = np.clip(col, 0, 255)
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
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '',
         '/**',
         ' * La malla de Aeralis, la Mariposa del Vendaval. GENERADO por',
         ' * materiales/generadores/vendaval_juego.py: no se edita a mano. Cambiar una',
         ' * caja aqui sin cambiar el script descuadra la textura, que se pinta con la',
         ' * misma cuadricula (a media resolucion: el atlas se declara de ' + str(ANCHO_ATLAS) + ' y el PNG',
         ' * mide la mitad).',
         ' */',
         'public final class AeralisMalla {', '',
         '    private AeralisMalla() {', '    }', '',
         '    public static LayerDefinition crear() {',
         '        MeshDefinition malla = new MeshDefinition();',
         '        PartDefinition p_root = malla.getRoot();']
    for n in ORDEN:
        p = PARTES[n]
        padre = var(p.padre) if p.padre else 'p_root'
        cub = 'CubeListBuilder.create()'
        for c in p.cajas:
            u, v = uv[clave(c)]
            cub += f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, {f(c[3])}, {f(c[4])}, {f(c[5])})'
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
        for c in PARTES[n].cajas:
            u, v = uv[clave(c)]
            for pts, uvs in nm.vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(M @ np.array([*q_, 1.0]))[:3] for q_ in pts]
                out.append((w, uvs, n, c[6]))
    return out


construir()
