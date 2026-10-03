"""
Renderizador 3D por software del Vigia, para arte promocional.

Lee la MISMA geometria que VigiaModel.java (huesos, cajas, texOffs, espejo) y
las mismas texturas, y la pinta con camara en perspectiva, luz de luna, contra-
luz roja, capa emisiva con bloom y niebla. Asi la pose es la que se quiera
—no la que tenga la animacion en ese tick— y el resultado es el bicho real.

Uso como modulo: render(pose, camara, ...) -> (rgb, alfa, emisivo) en numpy.
"""
import math
import numpy as np
from PIL import Image

D2R = math.pi / 180.0

# ----------------------------------------------------------------------
#  Geometria: transcripcion de VigiaModel.crear()
# ----------------------------------------------------------------------
JOROBA = 25.0

def _brazo(lado, nombre):
    esp = lado < 0
    return ('brazo_' + nombre, (6.5 * lado, -14, 0), (-JOROBA, 0, 0), [((32, 16), (-1.5, -1.5, -1.5, 3, 14, 3), esp)], [
        ('hombrera_' + nombre, (0, 0, 0), (0, 0, 0), [((88, 0), (-2, -2.5, -2.5, 4, 3, 5), esp)], []),
        ('antebrazo_' + nombre, (0, 12.5, 0), (-10, 0, 0), [((44, 16), (-1, 0, -1, 2, 14, 2), esp)], [
            ('garras_' + nombre, (0, 13.5, 0), (-15, 0, 0), [
                ((52, 16), (-1.6, 0, -0.5, 1, 6, 1), False),
                ((52, 16), (-0.5, 0, -1.2, 1, 6, 1), False),
                ((52, 16), (0.6, 0, -0.5, 1, 6, 1), False)], []),
        ]),
    ])

def _pierna(lado, nombre):
    esp = lado < 0
    return ('pierna_' + nombre, (2.5 * lado, 0, 0.5), (-10, 0, 0), [((0, 40), (-1.5, 0, -1.5, 3, 11, 3), esp)], [
        ('espinilla_' + nombre, (0, 11, 0), (20, 0, 0), [((12, 40), (-1, 0, -1, 2, 11, 2), esp)], [
            ('pie_' + nombre, (0, 11, 0), (-10, 0, 0), [((20, 40), (-1.5, 0, -3.5, 3, 2, 5), esp)], []),
        ]),
    ])

def _cuerno(lado, nombre):
    return ('cuerno_' + nombre, (2.5 * lado, -8, 0.5), (-12, 0, 25 * lado), [((44, 0), (-0.5, -7, -0.5, 1, 7, 1), False)], [
        ('punta_' + nombre, (0, -4, 0), (0, 0, 40 * lado), [((48, 0), (-0.5, -3, -0.5, 1, 3, 1), False)], []),
    ])

ESQUELETO = ('raiz', (0, 0, 0), (0, 0, 0), [], [
    ('torso', (0, 0, 0), (JOROBA, 0, 0), [((0, 16), (-5, -16, -3, 10, 16, 6), False)], [
        ('capa', (0, -15, 3.05), (-JOROBA + 8, 0, 0), [((64, 0), (-5, 0, 0, 10, 18, 0), False)], []),
        ('cuello', (0, -16, -1), (-10, 0, 0), [((32, 0), (-1.5, -5, -1.5, 3, 5, 3), False)], [
            ('cabeza', (0, -5, 0), (-15, 0, 0), [((0, 0), (-4, -8, -4, 8, 8, 8), False)], [
                ('ojo', (0, -4, -4), (0, 0, 0), [((32, 8), (-2, -2, -0.5, 4, 4, 1), False)], []),
                _cuerno(1, 'izq'), _cuerno(-1, 'der'),
            ]),
        ]),
        _brazo(1, 'izq'), _brazo(-1, 'der'),
    ]),
    _pierna(1, 'izq'), _pierna(-1, 'der'),
])

# ----------------------------------------------------------------------
#  Matrices
# ----------------------------------------------------------------------
def T(x, y, z):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m

def Rx(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4); m[1, 1] = c; m[1, 2] = -s; m[2, 1] = s; m[2, 2] = c; return m

def Ry(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0] = c; m[0, 2] = s; m[2, 0] = -s; m[2, 2] = c; return m

def Rz(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0] = c; m[0, 1] = -s; m[1, 0] = s; m[1, 1] = c; return m

def S(k):
    m = np.eye(4); m[0, 0] = m[1, 1] = m[2, 2] = k; return m

# ----------------------------------------------------------------------
#  Cajas -> cuadrilateros con UV (orden de vanilla, ModelPart.Cube)
# ----------------------------------------------------------------------
def caja_quads(tex, box, espejo, tw, th):
    (u, v) = tex
    x0, y0, z0, w, h, d = box
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    if espejo:
        x0, x1 = x1, x0
    V = {
        0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
        4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1),
    }
    u0, u1, u2, u3, u4, u5 = u, u + d, u + d + w, u + d + w + w, u + d + w + d, u + d + w + d + w
    v0, v1, v2 = v, v + d, v + d + h
    caras = [
        ((5, 4, 0, 1), (u1, v0, u2, v1)),   # abajo (minY: arriba a la vista)
        ((2, 3, 7, 6), (u2, v1, u3, v0)),   # arriba
        ((0, 4, 7, 3), (u0, v1, u1, v2)),   # oeste
        ((1, 0, 3, 2), (u1, v1, u2, v2)),   # norte (frente)
        ((5, 1, 2, 6), (u2, v1, u4, v2)),   # este
        ((4, 5, 6, 7), (u4, v1, u5, v2)),   # sur
    ]
    out = []
    for idx, (a1, b1, a2, b2) in caras:
        if (a2 - a1) == 0 or (b2 - b1) == 0:
            continue
        pts = [V[i] for i in idx]
        uvs = [(a2, b1), (a1, b1), (a1, b2), (a2, b2)]
        uvs = [(uu / tw, vv / th) for uu, vv in uvs]
        out.append((pts, uvs))
    return out

def quads_del_modelo(pose, tw=128, th=64, modelo_a_mundo=np.eye(4)):
    """pose: {hueso: (rx, ry, rz)} en grados que SE SUMAN al reposo, o
    {hueso: {'rot':(..), 'pos':(..), 'esc':k}}."""
    out = []

    def visitar(nodo, M):
        nombre, off, rot, cajas, hijos = nodo
        extra = pose.get(nombre, {})
        if isinstance(extra, tuple):
            extra = {'rot': extra}
        r = [rot[i] + extra.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + extra.get('pos', (0, 0, 0))[i] for i in range(3)]
        L = T(*p) @ Rz(r[2] * D2R) @ Ry(r[1] * D2R) @ Rx(r[0] * D2R) @ S(extra.get('esc', 1.0))
        Mn = M @ L
        for tex, box, esp in cajas:
            for pts, uvs in caja_quads(tex, box, esp, tw, th):
                w = [(modelo_a_mundo @ Mn @ np.array([*q, 1.0]))[:3] for q in pts]
                out.append((w, uvs, nombre))
        for h in hijos:
            visitar(h, Mn)

    visitar(ESQUELETO, np.eye(4))
    return out

def entidad_a_mundo(x, y, z, guinada_grados, escala=1.0):
    """Como LivingEntityRenderer: pixeles/16, Y invertida, pies en el suelo."""
    return T(x, y, z) @ Ry(guinada_grados * D2R) @ S(escala) @ T(0, 1.501, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])

# ----------------------------------------------------------------------
#  Camara y rasterizado
# ----------------------------------------------------------------------
class Camara:
    def __init__(self, ojo, objetivo, fov, ancho, alto):
        self.ojo = np.array(ojo, float)
        f = np.array(objetivo, float) - self.ojo; f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.W, self.H = ancho, alto
        self.foco = (alto / 2) / math.tan(fov * D2R / 2)

    def proyectar(self, p):
        d = np.asarray(p, float) - self.ojo
        x, y, z = d @ self.r, d @ self.u, d @ self.f
        return (self.W / 2 + self.foco * x / z, self.H / 2 - self.foco * y / z, z)

class Lienzo:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.color = np.zeros((H, W, 3))
        self.alfa = np.zeros((H, W))
        self.z = np.full((H, W), np.inf)
        self.emis = np.zeros((H, W, 3))

    def triangulo(self, cam, P, UV, tex, luz_fn, emis_tex=None, niebla=None, aditivo=False, brillo=1.0):
        s = [cam.proyectar(p) for p in P]
        if min(q[2] for q in s) < 0.05:
            return
        xs = [q[0] for q in s]; ys = [q[1] for q in s]
        x0 = max(int(math.floor(min(xs))), 0); x1 = min(int(math.ceil(max(xs))), self.W - 1)
        y0 = max(int(math.floor(min(ys))), 0); y1 = min(int(math.ceil(max(ys))), self.H - 1)
        if x0 > x1 or y0 > y1:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = s
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not dentro.any():
            return
        iw = l1 / az + l2 / bz + l3 / cz
        z = 1 / iw
        u = (l1 * UV[0][0] / az + l2 * UV[1][0] / bz + l3 * UV[2][0] / cz) * z
        v = (l1 * UV[0][1] / az + l2 * UV[1][1] / bz + l3 * UV[2][1] / cz) * z
        th, tw = tex.shape[:2]
        tu = np.clip((u * tw).astype(int), 0, tw - 1)
        tv = np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        a = texel[..., 3] / 255.0
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        if aditivo:
            m = dentro & (a > 0.01) & (z < zb)
            col = texel[..., :3] / 255.0 * a[..., None] * brillo
            self.emis[y0:y1 + 1, x0:x1 + 1][m] += col[m]
            return
        m = dentro & (a > 0.1) & (z < zb)
        if not m.any():
            return
        rgb = texel[..., :3] / 255.0 * luz_fn
        if niebla is not None:
            f = niebla(z)[..., None]
            rgb = rgb * (1 - f) + np.array(niebla.color) * f
        self.color[y0:y1 + 1, x0:x1 + 1][m] = rgb[m]
        self.alfa[y0:y1 + 1, x0:x1 + 1][m] = 1.0
        zb[m] = z[m]
        if emis_tex is not None:
            et = emis_tex[tv, tu]
            ea = et[..., 3] / 255.0
            me = m & (ea > 0.01)
            self.emis[y0:y1 + 1, x0:x1 + 1][me] += (et[..., :3] / 255.0 * ea[..., None] * brillo)[me]
            self.color[y0:y1 + 1, x0:x1 + 1][me] = np.maximum(self.color[y0:y1 + 1, x0:x1 + 1][me], (et[..., :3] / 255.0)[me])

def normal(P):
    n = np.cross(np.array(P[1]) - P[0], np.array(P[2]) - P[0])
    l = np.linalg.norm(n)
    return n / l if l > 1e-9 else np.array([0, 1, 0.0])

def iluminar(n, cam, centro, luces, ambiente):
    vista = cam.ojo - centro; vista /= np.linalg.norm(vista)
    if n @ vista < 0:
        n = -n   # caras de doble lado (la capa): se ilumina la que se ve
    col = np.array(ambiente, float)
    for (dirl, color, k, tipo) in luces:
        dl = np.array(dirl, float); dl /= np.linalg.norm(dl)
        if tipo == 'llave':
            col += np.array(color) * k * max(0.0, n @ dl)
        else:  # contraluz: borde que mira lejos de la camara y hacia la luz
            borde = (1 - abs(n @ vista)) ** 1.5
            col += np.array(color) * k * max(0.0, n @ dl) * (0.35 + borde)
    return col

def dibujar_quads(lienzo, cam, quads, tex, emis=None, luces=(), ambiente=(0.3, 0.3, 0.35), niebla=None, brillo=1.0):
    for P, UV, _ in quads:
        n = normal(P)
        luz = iluminar(n, cam, np.mean(P, axis=0), luces, ambiente)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lienzo.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla, brillo=brillo)

def cargar(path):
    return np.array(Image.open(path).convert('RGBA'))
