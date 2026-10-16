"""
El Coco en el juego (16-10-2026): de la ficha (Juan: «haz el diseño 1 con todas sus animaciones, huevo, etc.»: el
Gloton) a la malla de Minecraft, su textura y la de lo que brilla.

Las piezas son las mismas cajas del boceto (coco_modelo.py), en la postura de reposo (las dos manos en el suelo y la boca
cerrada): se recogen al construirlo, repartidas en las partes que se mueven (coco_modelo.PARTE y EN marcan donde empieza
cada una): el cuerpo, el tronco con la giba, la barriga, la cabeza con la quijada y la cresta, los brazos (brazo,
antebrazo, mano y cada dedo con sus dos falanges) y las piernas (pierna, canilla y pie). Cada caja va a su propia pieza
de ModelPart con su giro (una caja de ModelPart no se puede girar sola). Las caras se pintan con los mismos pintores del
boceto, a un texel por pixel, en una textura cuatro veces mas fina que su cuadricula: asi las medidas con decimales caen
en pixeles enteros.

Del boceto (Y arriba, el frente en +Z) a Minecraft (Y abajo desde la altura 24, el frente en -Z): C = diag(1, -1, -1).

Uso: python coco_juego.py <raiz del proyecto> [carpeta de la vista previa]
"""
import collections, json, math, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import quimeras_modelo as qm
import bestias_modelo as bm
import coco_modelo as co

TIPO = 'A'
K = 4                         # pixeles de la textura por unidad de la cuadricula
ANCHO = 256                   # ancho de la cuadricula (unidades)
ATRAS = 3.5                   # el boceto va adelantado (la cabeza y la barriga): se corre atras para centrarlo en su caja
C = np.diag([1.0, -1.0, -1.0, 1.0])
A = vr.T(0.0, 24.0, 0.0) @ C @ vr.T(0.0, 0.0, -ATRAS)
T, Rx, Ry, Rz = vr.T, vr.Rx, vr.Ry, vr.Rz


# ----------------------------------------------------------------------
#  Recoger las cajas del boceto, por partes
# ----------------------------------------------------------------------
class Parte:
    def __init__(self, nombre, padre, marco):
        self.nombre, self.padre, self.marco = nombre, padre, np.asarray(marco, float)
        self.cajas = []                   # (matriz del boceto, x0, y0, z0, w, h, d, {cara: pintor})


PARTES, ORDEN = {}, []
ACTUAL = [None]
CARAS = ('frente', 'atras', 'der', 'izq', 'arriba', 'abajo')


def parte(nombre, padre, marco):
    PARTES[nombre] = Parte(nombre, padre, marco)
    ORDEN.append(nombre)
    ACTUAL[0] = PARTES[nombre]


def en(nombre):
    ACTUAL[0] = PARTES[nombre]


def _cubo(out, M, x0, y0, z0, w, h, d, pintor, caras=None, semilla=0):
    pint = {c: (caras or {}).get(c, pintor) for c in CARAS}
    ACTUAL[0].cajas.append((np.array(M, float), x0, y0, z0, w, h, d, pint))


def _hoja(out, P4, pintor, ancho, alto, semilla=0):
    """Una hoja (un diente, una hebra de estopa): un plano sin grosor con la textura entera, la base arriba."""
    a, b, c, d = [np.asarray(p, float) for p in P4]
    abajo, arriba = (a + b) / 2, (c + d) / 2
    x = c - d
    W = max(float(np.linalg.norm(x)), float(np.linalg.norm(b - a)), 0.3)
    x = co._u(x)
    y = arriba - abajo
    H = float(np.linalg.norm(y))
    y = co._u(y - x * float(x @ y))
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, abajo
    ACTUAL[0].cajas.append((M, -W / 2, 0.0, 0.0, W, H, 0.0, {c: (pintor if c in ('frente', 'atras') else None)
                                                              for c in CARAS}))


bm.cubo = _cubo
co.hoja = _hoja
co.PARTE = parte
co.EN = en
co.JUEGO = True


def construir():
    """El Gloton en su postura de reposo, como coco_modelo.coco(), con cada caja apuntada en su parte."""
    co.coco(TIPO, 'reposo')
    vacias = [n for n in ORDEN if not PARTES[n].cajas and n not in ('cuerpo',)]
    assert not vacias, vacias


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
         ' * La malla del Coco. GENERADO por materiales/generadores/coco_juego.py: no se edita a mano (la textura se pinta',
         ' * con la misma cuadricula). Las partes con nombre son las que mueve CocoModel; cada caja va en su propia pieza',
         ' * ("_c" y un numero) con su giro.',
         ' */',
         'public final class CocoMalla {', '',
         '    private CocoMalla() {', '    }', '',
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
def _matriz(L):
    (px, py, pz), (rx, ry, rz) = pose_mc(L)
    return T(px, py, pz) @ Rz(rz) @ Ry(ry) @ Rx(rx)


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


def vista_previa(carpeta, uv, alto, base):
    import quimeras_escenas as qe
    os.makedirs(carpeta, exist_ok=True)
    qm._reg('coco_atlas', base, None, estira=True)
    qs = quads(uv, alto, 'coco_atlas')
    for nombre, ojo, obj in (('previa_heroe', (2.3, 1.2, 5.6), (0.0, 1.4, 0.0)),
                             ('previa_lado', (6.0, 1.5, 0.0), (0.0, 1.4, 0.0)),
                             ('previa_atras', (-2.6, 2.0, -5.0), (0.0, 1.4, 0.0))):
        W, H = 800, 600
        lz = qe.Lienzo(W, H)
        cam = vr.Camara(ojo, obj, 45, W, H)
        luces = [((-0.5, 0.75, 0.4), (0.95, 0.92, 0.88), 0.8, 'llave'), ((0.6, 0.4, -0.8), (0.6, 0.7, 1.0), 0.5, 'contra')]
        qm.dibujar(lz, cam, qs, luces, (0.35, 0.36, 0.4), None, 1.2)
        arr = lz.color * lz.alfa[..., None] + np.array((0.12, 0.12, 0.16)) * (1 - lz.alfa[..., None])
        Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(os.path.join(carpeta, nombre + '.png'))
    print('vista previa en', carpeta)


# ----------------------------------------------------------------------
#  El huevo, los nombres y lo del objeto
# ----------------------------------------------------------------------
SILUETA = [(2, 6, 9), (3, 5, 10), (4, 4, 11), (5, 3, 12), (6, 3, 12), (7, 2, 13), (8, 2, 13), (9, 2, 13),
           (10, 2, 13), (11, 2, 13), (12, 2, 13), (13, 3, 12), (14, 4, 11), (15, 5, 10)]


def huevo():
    """El huevo, al estilo de huevos_jefes.py (la silueta de vanilla, la luz desde arriba a la izquierda y el contorno
    de dos tonos): arriba la cascara parda con la cresta de estopa que asoma, los dos ojos de brasa y el agujero de la
    nariz, el canto blanco de la carne con los dientes, y abajo el cuerpo de carbon con la barriga."""
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
            if f <= 8:                                                  # la cascara
                if borde:
                    px[x, f] = c('140c06') if luz > 0.9 else c('24160c')
                else:
                    px[x, f] = c('744c2c') if luz < 0.45 else c('583820') if luz < 1.05 else c('402816')
            else:                                                       # el cuerpo de carbon
                if borde:
                    px[x, f] = c('0c0a0a') if luz > 0.9 else c('171312')
                else:
                    px[x, f] = c('443d3a') if luz < 0.7 else c('312a27') if luz < 1.3 else c('231e1c')
    for x, f in ((6, 1), (8, 0), (9, 1), (7, 1)):
        px[x, f] = c('a07444')                                          # la estopa de la cresta
    px[8, 1] = c('c49a62')
    for x in (4, 5, 10, 11):                                            # los ojos hondos, con la brasa
        px[x, 5] = c('050302')
    px[5, 5] = px[10, 5] = c('ff6a2a')
    px[4, 4] = px[5, 4] = px[10, 4] = px[11, 4] = c('2c1b10')           # el ceño
    px[7, 6] = px[8, 6] = c('050302')                                   # la nariz
    a, b = filas[8]
    for x in range(a + 1, b):
        px[x, 8] = c('faf6ec')                                          # el canto de la carne
    for x in range(a + 1, b, 2):
        px[x, 9] = c('e2dccc')                                          # los dientes
    for f in (11, 12, 13):                                              # la barriga
        for x in range(6, 10):
            px[x, f] = c('806450') if (x, f) != (8, 12) else c('3e2e26')
    return im


def icono_alerta():
    """El icono del aviso de encima (nuestro, de pixeles): un triangulo rojo de canto oscuro, con la luz en el lado de la
    izquierda y la exclamacion blanca. 16 x 16, con el triangulo de 15 x 14 centrado."""
    t = np.zeros((16, 16, 4), np.uint8)
    W, H = 15, 14
    for y in range(H):
        media = 0.5 + y * 0.5
        for x in range(W):
            d = abs(x - (W - 1) / 2)
            if d <= media:
                borde = d > media - 1.0 or y == H - 1
                col = (70, 8, 10, 255) if borde else ((255, 96, 80, 255) if x < (W - 1) / 2 - media + 2.4 else
                                                      (214, 34, 34, 255))
                t[y + 1, x] = col
    for y in (5, 6, 7, 8, 9):
        t[y, 7] = (255, 250, 240, 255)
    t[11, 7] = (255, 250, 240, 255)
    return Image.fromarray(t)


def objeto(raiz):
    item = os.path.join(raiz, 'src/main/resources/assets/atalaya')
    icono_alerta().save(os.path.join(item, 'textures/gui/coco_alerta.png'))
    huevo().save(os.path.join(item, 'textures/item/huevo_coco.png'))
    with open(os.path.join(item, 'items/huevo_coco.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'model': {'type': 'minecraft:model', 'model': 'atalaya:item/huevo_coco'}}, fh, indent=2)
        fh.write('\n')
    with open(os.path.join(item, 'models/item/huevo_coco.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'atalaya:item/huevo_coco'}}, fh,
                  indent=2)
        fh.write('\n')
    textos = {
        'es_es': (('entity.atalaya.coco', 'Coco'), ('item.atalaya.huevo_coco', 'Huevo generador de coco'),
                  ('entity.atalaya.coco.atrapado', '¡ha sido atrapado!'),
                  ('entity.atalaya.coco.dentro', '¡El Coco te ha tragado! Solo sales si alguien lo mata'),
                  ('death.attack.atalaya.coco', '%1$s fue digerido por %2$s'),
                  ('death.attack.atalaya.coco.player', '%1$s fue digerido mientras huía de %2$s')),
        'en_us': (('entity.atalaya.coco', 'Coco'), ('item.atalaya.huevo_coco', 'Coco Spawn Egg'),
                  ('entity.atalaya.coco.atrapado', 'has been trapped!'),
                  ('entity.atalaya.coco.dentro', 'The Coco swallowed you! Only killing it gets you out'),
                  ('death.attack.atalaya.coco', '%1$s was digested by %2$s'),
                  ('death.attack.atalaya.coco.player', '%1$s was digested while fleeing %2$s')),
    }
    for idioma, pares in textos.items():
        ruta = os.path.join(item, f'lang/{idioma}.json')
        d = json.load(open(ruta, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        claves = {k for k, _ in pares}
        nuevo = collections.OrderedDict()
        for k, v in d.items():
            if k in claves:
                continue
            nuevo[k] = v
            if k == 'item.atalaya.huevo_fogonazo':
                for k2, v2 in pares:
                    nuevo[k2] = v2
        assert all(k in nuevo for k in claves), idioma
        with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(nuevo, fh, indent=2, ensure_ascii=False)
            fh.write('\n')


def main():
    raiz = sys.argv[1]
    objeto(raiz)
    construir()
    uv, alto, unicas = empaquetar()
    base, brillo = pintar(uv, alto, unicas)
    tex_dir = os.path.join(raiz, 'src/main/resources/assets/atalaya/textures/entity/coco')
    os.makedirs(tex_dir, exist_ok=True)
    Image.fromarray(base).save(os.path.join(tex_dir, 'coco.png'))
    Image.fromarray(brillo).save(os.path.join(tex_dir, 'coco_brillo.png'))
    with open(os.path.join(raiz, 'src/client/java/com/atalaya/client/CocoMalla.java'), 'w', encoding='utf-8',
              newline='\n') as fh:
        fh.write(java(uv, alto))
    n = sum(len(PARTES[k].cajas) for k in ORDEN)
    print('ok', len(ORDEN), 'partes', n, 'cajas', len(unicas), 'distintas; atlas', ANCHO, 'x', alto, '(x%d)' % K)
    print(' '.join(ORDEN))
    if len(sys.argv) > 2:
        vista_previa(sys.argv[2], uv, alto, base)


if __name__ == '__main__':
    main()
