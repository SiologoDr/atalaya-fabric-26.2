"""
Ficha de las mejoras de Rajang (octubre de 2026): los ataques nuevos y los
cambios tras las pruebas del grupo, con la malla y las texturas del juego,
para revisarlos antes de pasarlos al juego.

  embestida   la Embestida de Jade: la flecha del aviso en el suelo con las
              dos filas donde van a reventar los pinchos, el lanzado a la
              carrera y los pinchos mortales a su paso, con alguien por el aire
  tumba       la Tumba de Raices: ruge contra el suelo y el circulo se llena
              desde el; quien siga dentro cuando se llene, cae
  sello       el Sello endurecido: un escalon que tiembla, otro que se cae, y
              el pulso de tierra al romperse un totem, que echa de la columna
  furia       la Furia de Jade: el aura verde que le queda si el Sello falla

Uso: python rajang_mejoras_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import copy, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import tierra_ataques as ta
import tierra_escenas as ts
import rajang_juego as rj
import rajang_juego_anim as ra

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
ENT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/rajang')
SS = ts.SS
TAU = math.tau
UV_ATLAS, ALTO_ATLAS = rj.empaquetar()


# ----------------------------------------------------------------------
#  El lienzo del poster: lo opaco que tapa algo le borra tambien el brillo
# ----------------------------------------------------------------------
class Lienzo(vr.Lienzo):
    def triangulo(self, cam, P_, UV, tex, luz_fn, emis_tex=None, niebla=None, aditivo=False, brillo=1.0, envolver=False,
                  translucido=0.0):
        if aditivo or translucido > 0:
            return super().triangulo(cam, P_, UV, tex, luz_fn, emis_tex, niebla, aditivo, brillo, envolver, translucido)
        s = [cam.proyectar(p) for p in P_]
        if min(q[2] for q in s) < 0.05:
            return
        xs = [q[0] for q in s]
        ys = [q[1] for q in s]
        x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), self.W - 1)
        y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), self.H - 1)
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
        z = 1 / (l1 / az + l2 / bz + l3 / cz)
        u = (l1 * UV[0][0] / az + l2 * UV[1][0] / bz + l3 * UV[2][0] / cz) * z
        v = (l1 * UV[0][1] / az + l2 * UV[1][1] / bz + l3 * UV[2][1] / cz) * z
        th, tw = tex.shape[:2]
        if envolver:
            tu, tv = np.floor(u * tw).astype(int) % tw, np.floor(v * th).astype(int) % th
        else:
            tu, tv = np.clip((u * tw).astype(int), 0, tw - 1), np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = dentro & (texel[..., 3] > 25) & (z < zb)
        if not m.any():
            return
        rgb = texel[..., :3] / 255.0 * luz_fn
        if niebla is not None:
            f = niebla(z)[..., None]
            rgb = rgb * (1 - f) + np.array(niebla.color) * f
        col = self.color[y0:y1 + 1, x0:x1 + 1]
        col[m] = rgb[m]
        self.alfa[y0:y1 + 1, x0:x1 + 1][m] = 1.0
        zb[m] = z[m]
        em = self.emis[y0:y1 + 1, x0:x1 + 1]
        em[m] = 0.0
        if emis_tex is not None:
            et = emis_tex[tv, tu]
            ea = et[..., 3] / 255.0
            me = m & (ea > 0.01)
            k = 1.0 if niebla is None else (1 - niebla(z))[..., None]
            em[me] = (et[..., :3] / 255.0 * ea[..., None] * brillo * k)[me]
            col[me] = np.maximum(col, et[..., :3] / 255.0 * k)[me]


# ----------------------------------------------------------------------
#  Rajang con la malla del juego
# ----------------------------------------------------------------------
_PIELES = {}


def piel(fase):
    if fase not in _PIELES:
        _PIELES[fase] = (vr.cargar(os.path.join(ENT, f'rajang_f{fase}.png')),
                         vr.cargar(os.path.join(ENT, f'rajang_brillo_f{fase}.png')))
    return _PIELES[fase]


def con_fase(pose, fase):
    """Los cristales crecidos de la fase (como RajangModel) y, en la IV, sin peto."""
    pose = copy.deepcopy(pose)
    k = (1.0, 1.12, 1.3, 1.55)[fase - 1]
    for c in rj.CRISTALES:
        d = pose.setdefault(c, {})
        e = d.get('esc', (1, 1, 1))
        d['esc'] = (e[0] * math.sqrt(k), e[1] * k, e[2] * math.sqrt(k))
    if fase >= 4:
        pose['peto'] = {'oculto': True}
    return pose


def guinada_hacia(dx, dz):
    """La guinada que hace mirar a Rajang hacia (dx, dz): el frente del modelo es -Z."""
    return math.degrees(math.atan2(-dx, -dz))


def rajang(lz, cam, x, z, guinada, pose, fase, luces, amb, niebla=None, k_cristal=0.45):
    M = vr.entidad_a_mundo(x, 0, z, guinada)
    tex, brillo = piel(fase)
    qs = rj.quads(con_fase(pose, fase), UV_ATLAS, ALTO_ATLAS, M)
    for Pq, UVq, _, mat in qs:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb)
        k = k_cristal if mat == 'cristal' else 1.0
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[i] for i in tri], [UVq[i] for i in tri], tex, luz, brillo, niebla, brillo=k)
    return qs


def silueta(cam, W, H, qs):
    solo = vr.Lienzo(W * SS, H * SS)
    blanco = np.full((4, 4, 4), 255, np.uint8)
    for Pq, _, _, _ in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(cam, [Pq[i] for i in tri], [(0, 0), (1, 0), (1, 1)], blanco, np.ones(3))
    return np.array(Image.fromarray((solo.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255


# ----------------------------------------------------------------------
#  Los pinchos del juego (RajangDibujo / PicoTierraRenderer), como en el poster
# ----------------------------------------------------------------------
TEX_ROCA = vr.cargar(os.path.join(ENT, 'roca.png'))
TEX_VETAS = vr.cargar(os.path.join(ENT, 'roca_brillo.png'))
CARAS_CAJA = ((0, 4, 6, 2), (5, 1, 3, 7), (1, 0, 2, 3), (4, 5, 7, 6), (2, 6, 7, 3), (0, 1, 5, 4))


def _xrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0], q[1] * c + q[2] * s, q[2] * c - q[1] * s])


def _yrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0] * c + q[2] * s, q[1], q[2] * c - q[0] * s])


def _zrot(q, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([q[0] * c + q[1] * s, q[1] * c - q[0] * s, q[2]])


def bloque(out, r, x, y, z, hx, hy, hz, mover, gx, gy, gz, densidad, tw, th):
    v = []
    for i in range(8):
        sx, sy, sz = (1 if i & 1 else -1), (1 if i & 2 else -1), (1 if i & 4 else -1)
        q = np.array([sx * hx * (1 + (r.random() - 0.5) * mover), sy * hy * (1 + (r.random() - 0.5) * mover),
                      sz * hz * (1 + (r.random() - 0.5) * mover)])
        q = _yrot(_xrot(_zrot(q, math.radians(gz)), math.radians(gx)), math.radians(gy))
        v.append(q + np.array([x, y, z]))
    lados = ((hz, hy), (hz, hy), (hx, hy), (hx, hy), (hz, hx), (hx, hz))
    for k, c in enumerate(CARAS_CAJA):
        du = min(1.0, 2 * lados[k][0] * densidad / tw)
        dv = min(1.0, 2 * lados[k][1] * densidad / th)
        u0, v0 = r.random() * (1 - du), r.random() * (1 - dv)
        out.append(([v[c[0]], v[c[1]], v[c[2]], v[c[3]]], [(u0, v0 + dv), (u0 + du, v0 + dv), (u0 + du, v0), (u0, v0)]))


def pincho(out, r, x, z, alto, ancho, inclina, ladea):
    e = _xrot(_zrot(np.array([0.0, 1.0, 0.0]), math.radians(ladea)), math.radians(-inclina))
    n = max(3, min(7, int(round(alto / max(0.45, ancho * 0.75)))))
    paso = alto / e[1] / n
    base = np.array([x, 0.0, z])
    s = -0.35
    for i in range(n):
        m = max(0.09, ancho * 0.5 * (1 - i / n) ** 0.8)
        h = paso * (0.95 + r.random() * 0.15)
        c = base + e * (s + h / 2)
        bloque(out, r, *c, m * (0.9 + r.random() * 0.15), h / 2 * 1.04, m * (0.85 + r.random() * 0.2), 0.1, -inclina,
               (r.random() - 0.5) * 18, ladea, 12, 32, 64)
        s += h * 0.9
    m = max(0.07, ancho * 0.08)
    c = base + e * (s + paso * 0.25)
    bloque(out, r, *c, m, paso * 0.3, m, 0.1, -inclina, (r.random() - 0.5) * 18, ladea, 12, 32, 64)


def pico_tierra(x, z, tam, rumbo, semilla, sale=1.0, y=0.0):
    """Un golpe de pinchos como PicoTierraRenderer; 'sale' de 0 a 1 lo que ha salido."""
    r = random.Random(semilla)
    caras = []
    alto = 6.0 * tam
    ancho = 0.5 + 1.25 * tam
    pincho(caras, r, 0, 0, alto, ancho, 16 + r.random() * 10, (r.random() - 0.5) * 12)
    if tam > 0.25:
        n = 2 + r.randrange(3)
        for i in range(n):
            a = (i + r.random() * 0.5) / n * TAU
            d = ancho * (0.55 + r.random() * 0.3)
            abre = 22 + r.random() * 18
            pincho(caras, r, math.cos(a) * d, math.sin(a) * d, alto * (0.3 + r.random() * 0.3), ancho * (0.45 + r.random() * 0.2),
                   math.sin(a) * abre, math.cos(a) * abre)
        for i in range(6):
            a = r.random() * TAU
            d = ancho * (0.9 + r.random() * 0.7)
            t = ancho * (0.12 + r.random() * 0.1)
            bloque(caras, r, math.cos(a) * d, t * 0.4, math.sin(a) * d, t, t * 0.7, t, 0.2, (r.random() - 0.5) * 50,
                   r.random() * 90, (r.random() - 0.5) * 50, 12, 32, 64)
    M = vr.T(x, y - alto * (1 - sale), z) @ vr.Ry(math.radians(-rumbo))
    return [([(M @ np.array([*p, 1.0]))[:3] for p in pts], uvs) for pts, uvs in caras]


def pintar(lz, cam, caras, tex, emis, luces, amb, brillo=1.0, niebla=None):
    for pts, uvs in caras:
        luz = vr.iluminar(vr.normal(pts), cam, np.mean(pts, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [pts[i] for i in tri], [uvs[i] for i in tri], tex, luz, emis, niebla, brillo=brillo)


# ----------------------------------------------------------------------
#  Calcos nuevos del suelo
# ----------------------------------------------------------------------
GLOW = np.array([150, 255, 120])
BLANCO_JADE = np.array([226, 255, 200])


def _tex_flecha(w=128, h=1024, lleno=0.62, galones=9):
    """La flecha de la Embestida, a lo largo (v crece hacia la punta): el
    carril con sus dos filetes, los galones que apuntan adonde va a correr y
    lo que ya se ha llenado del aviso (la cuenta atras)."""
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5) / w * 2 - 1          # -1 a 1 a lo ancho
    v = (yy + 0.5) / h                  # 0 en la cola, 1 en la punta
    a = np.zeros((h, w))
    # los filetes de los lados
    a += np.exp(-((np.abs(u) - 0.92) / 0.035) ** 2) * 0.95
    # lo llenado: un tinte suave hasta 'lleno', con el frente encendido
    a += np.where(v < lleno, 0.16, 0.0)
    a += np.exp(-((v - lleno) / 0.006) ** 2) * 0.9
    # los galones (V que apuntan hacia v=1)
    paso = 1.0 / galones
    fase = (v % paso) / paso
    galon = np.exp(-((fase - (0.55 - 0.32 * np.abs(u))) / 0.05) ** 2) * (np.abs(u) < 0.8)
    a += galon * np.where(v < lleno, 0.95, 0.45)
    # la punta: un triangulo grande al final
    punta = (v > 0.9) & (np.abs(u) < (1 - v) / 0.1)
    a = np.where(punta, np.maximum(a, 0.85), a)
    a *= np.clip(v / 0.05, 0, 1)
    t = np.zeros((h, w, 4))
    k = np.clip(a, 0, 1)
    t[..., :3] = GLOW * (1 - k[..., None] * 0.3) + BLANCO_JADE * k[..., None] * 0.3
    t[..., 3] = k * 255
    return t.astype(np.uint8)


def _tex_carril(w=32, h=1024, n=14):
    """Por donde van a reventar los pinchos: una fila de rombos pequenos."""
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5) / w * 2 - 1
    v = (yy + 0.5) / h * n
    f = v % 1.0 - 0.5
    rombo = (np.abs(u) * 0.5 + np.abs(f)) < 0.32
    borde = (np.abs(u) * 0.5 + np.abs(f)) < 0.4
    a = np.where(rombo, 0.85, np.where(borde, 0.35, 0.0)) * np.clip(np.minimum(v, n - v) / 0.5, 0, 1)
    t = np.zeros((h, w, 4))
    t[..., :3] = GLOW
    t[..., 3] = a * 255
    return t.astype(np.uint8)


def _tex_tumba(n=1024, lleno=0.68, semilla=5):
    """El circulo de la Tumba de Raices: el borde (donde hay que salir) bien
    marcado desde el principio, y dentro lo que ya se ha llenado, que crece
    desde el centro con raices y grietas; el frente del llenado, encendido."""
    r = random.Random(semilla)
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = (xx + 0.5) / n * 2 - 1, (yy + 0.5) / n * 2 - 1
    d = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    a = np.zeros((n, n))
    # el borde: dos aros y unas muescas que giran
    a += np.exp(-((d - 0.985) / 0.006) ** 2) * 1.0
    a += np.exp(-((d - 0.955) / 0.004) ** 2) * 0.7
    muescas = (np.abs(((ang / TAU * 36) % 1.0) - 0.5) < 0.12) & (d > 0.958) & (d < 0.982)
    a = np.where(muescas, np.maximum(a, 0.8), a)
    # lo llenado
    dentro = d < lleno
    a += np.where(dentro, 0.2 + 0.12 * (d / max(lleno, 1e-3)), 0.0)
    a += np.exp(-((d - lleno) / 0.008) ** 2) * 1.0 * (d < 0.95)
    # raices: lineas quebradas desde el centro hasta el frente
    capa = Image.new('L', (n, n), 0)
    dr = ImageDraw.Draw(capa)
    for k in range(22):
        x, y = n / 2, n / 2
        th = TAU * k / 22 + r.uniform(-0.1, 0.1)
        largo = 0
        while largo < lleno * n / 2:
            th += r.uniform(-0.35, 0.35)
            paso = r.uniform(14, 30)
            x1, y1 = x + math.cos(th) * paso, y + math.sin(th) * paso
            dr.line((x, y, x1, y1), fill=230, width=max(2, int(5 * (1 - largo / (n / 2)))))
            if r.random() < 0.18:
                th2 = th + r.choice([-1, 1]) * r.uniform(0.5, 1.0)
                dr.line((x1, y1, x1 + math.cos(th2) * paso * 1.5, y1 + math.sin(th2) * paso * 1.5), fill=170, width=2)
            x, y, largo = x1, y1, largo + paso
    raices = np.array(capa).astype(float) / 255 * (d < lleno)
    a += raices * 0.8
    t = np.zeros((n, n, 4))
    k = np.clip(a, 0, 1)
    t[..., :3] = GLOW * (1 - raices[..., None] * 0.2) + BLANCO_JADE * raices[..., None] * 0.2
    t[..., 3] = k * 255
    return t.astype(np.uint8)


def _tex_aura(n=64):
    """El aura de la Furia: bandas en diagonal que corren por el cuerpo, como
    la carga del creeper pero en verde de maldicion."""
    yy, xx = np.mgrid[0:n, 0:n]
    s = ((xx + yy) % 16) / 16.0
    a = np.exp(-((s - 0.5) / 0.18) ** 2) * 0.9 + 0.08
    t = np.zeros((n, n, 4))
    t[..., :3] = np.array([110, 255, 90])
    t[..., 3] = np.clip(a, 0, 1) * 255
    return t.astype(np.uint8)


FLECHA = _tex_flecha()
CARRIL = _tex_carril()
AURA = _tex_aura()


def calco_tramo(lz, cam, x0, z0, x1, z1, medio_ancho, textura, brillo=1.0, y=0.05):
    """Un calco a lo largo de un tramo del suelo (v=0 en (x0, z0), v=1 en (x1, z1))."""
    L = math.hypot(x1 - x0, z1 - z0)
    giro = math.degrees(math.atan2(-(x1 - x0), z1 - z0))
    ta.calco(lz, cam, (x0 + x1) / 2, (z0 + z1) / 2, medio_ancho, textura, brillo, giro=giro, y=y, largo=L / 2)


# ----------------------------------------------------------------------
#  Lo comun de las escenas
# ----------------------------------------------------------------------
def plaza_templo(radio=26, prof=60, ext=40):
    return ts.plaza(radio, prof, ext)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


def etiqueta(img, cam, p, texto, dx, dy):
    """Un rotulo con su linea hasta el punto p del mundo, desplazado (dx, dy)
    en una imagen de 1600 de ancho (escala con la imagen)."""
    from PIL import ImageFont
    k = img.size[0] / 1600
    f = ImageFont.truetype(ts.FUENTE + 'Montserrat-SemiBold.ttf', max(10, int(22 * k)))
    sx, sy, z = cam.proyectar(p)
    if z < 0.5:
        return
    sx, sy = sx / SS, sy / SS
    tx, ty = sx + dx * k, sy + dy * k
    d = ImageDraw.Draw(img)
    d.line([(sx, sy), (tx, ty)], fill=(235, 255, 220, 230), width=max(1, int(2 * k)))
    d.ellipse((sx - 4 * k, sy - 4 * k, sx + 4 * k, sy + 4 * k), fill=(235, 255, 220, 255))
    w = d.textlength(texto, font=f)
    pad = 8 * k
    x0 = tx - (w + 2 * pad if dx < 0 else 0)
    caja = (x0, ty - 16 * k, x0 + w + 2 * pad, ty + 16 * k)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle(caja, radius=6 * k, fill=(8, 22, 14, 200), outline=(150, 255, 120, 220),
                                           width=max(1, int(2 * k)))
    img.alpha_composite(capa)
    ImageDraw.Draw(img).text((x0 + pad, ty - 13 * k), texto, font=f, fill=(236, 255, 226, 255))


def lineas_movimiento(img, cam, p, direccion, n, largo, semilla, color=(220, 255, 200), ancho=3):
    """Rayas de velocidad detras de algo que se mueve (en 2D)."""
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(capa)
    d = np.array(direccion, float)
    d /= np.linalg.norm(d)
    for _ in range(n):
        q = np.array(p) + np.array([r.uniform(-1, 1), r.uniform(-0.6, 1.4), r.uniform(-1, 1)]) * 2.4
        a = cam.proyectar(q)
        b = cam.proyectar(q - d * largo * r.uniform(0.5, 1.0))
        if min(a[2], b[2]) < 0.5:
            continue
        dr.line([(a[0] / SS, a[1] / SS), (b[0] / SS, b[1] / SS)], fill=(*color, r.randint(60, 150)), width=ancho)
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(1)))


# ----------------------------------------------------------------------
#  1. Embestida de Jade
#
#  Corre hacia +x. Detras de el, a los dos lados de su camino, los pinchos que
#  revientan a su paso (uno ha lanzado a alguien por el aire); delante, lo que
#  queda de la flecha del aviso, con las dos filas de rombos donde van a salir
#  los siguientes.
# ----------------------------------------------------------------------
EMB_DESDE, EMB_HASTA = -30.0, 24.0
EMB_LADO = 4.2


def embestida(W=1600, H=900):
    cam = vr.Camara(ojo=(6.0, 7.5, -29.0), objetivo=(-3.0, 3.8, 0.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(26, 70)
    escena = plaza_templo() + ts.piramide(-6, 40) + ts._arboles((-30, 26, 15, 9), (26, 30, 17, 10), (36, 8, 14, 8))
    ts.dibujar_mundo(lz, cam, escena, niebla, 2)
    r = random.Random(4)
    rx = 2.0                                         # donde esta ahora (su pecho)
    # el surco que deja por el centro del camino
    ta.grieta(lz, cam, EMB_DESDE + 2, 0.0, rx - 6, 0.0, 1.6, semilla=31, parte='oscura')
    # los pinchos: pares a los dos lados, de su arranque hasta justo detras de el
    piedras, polvos = [], []
    x = EMB_DESDE + 3.0
    i = 0
    while x < rx - 9.0:
        for lado in (-1, 1):
            cerca = rx - 9.0 - x
            sale = 1.0 if cerca > 4.0 else 0.35 + 0.65 * cerca / 4.0
            tam = r.uniform(0.62, 0.8)
            piedras += pico_tierra(x + r.uniform(-0.4, 0.4), lado * (EMB_LADO + r.uniform(-0.3, 0.3)), tam,
                                   90 + lado * r.uniform(10, 30), 300 + i, sale)
            if cerca < 6:
                polvos.append((x, 0.3, lado * EMB_LADO, 2.0))
            i += 1
        x += 2.2
    luces_roca = [((-0.6, 0.6, -0.5), (1.0, 0.86, 0.66), 0.95, 'llave'), ((0.55, 0.75, 0.6), (0.72, 1.0, 0.45), 0.75, 'contra')]
    pintar(lz, cam, piedras, TEX_ROCA, TEX_VETAS, luces_roca, (0.2, 0.19, 0.16), brillo=1.4, niebla=niebla)
    # los jugadores: uno por los aires (le pillo un pincho), uno que se aparta a tiempo
    # y otro que mira desde fuera del carril
    ts.jugador(lz, cam, -9.0, -EMB_LADO - 0.4, 30, y=13.0, niebla=niebla)
    ts.jugador(lz, cam, 14.0, -8.5, 200, niebla=niebla)
    ts.jugador(lz, cam, 19.0, 7.5, 250, niebla=niebla)
    # Rajang a la carrera, la cabeza baja y los sables por delante
    pose = ra.sumar(ra.pose_en('CORRER', 0.62), ra.cabeza(x=10, boca=18, orejas=-14), ra.cuerpo(x=3, baja=2))
    qs = rajang(lz, cam, rx, 0.0, guinada_hacia(1, 0), pose, 2, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # lo que brilla: la flecha de delante y las filas de rombos, y las grietas
    calco_tramo(lz, cam, rx + 8.0, 0.0, EMB_HASTA, 0.0, 3.0, FLECHA, 1.2)
    for lado in (-1, 1):
        calco_tramo(lz, cam, rx + 6.0, lado * EMB_LADO, EMB_HASTA - 1.0, lado * EMB_LADO, 0.5, CARRIL, 1.1)
    ta.grieta(lz, cam, EMB_DESDE + 2, 0.0, rx - 6, 0.0, 1.6, semilla=31, brillo=1.0, parte='brillo')
    img = ts.componer(lz, W, H, ts.horizonte(cam), 21)
    ta.polvo_en(img, cam, polvos + [(rx - 6, 0.4, 0, 3.4), (rx - 11, 0.4, 0, 3.0)], SS, (128, 110, 80), 22)
    lineas_movimiento(img, cam, (rx - 4, 3.5, 0), (1, 0, 0), 26, 9.0, 23)
    etiqueta(img, cam, (EMB_HASTA - 5, 0.05, 0.0), 'Aviso: por donde va a cargar', 30, 150)
    etiqueta(img, cam, (rx + 10, 0.05, -EMB_LADO), 'Aquí saldrán los pinchos', 230, 50)
    etiqueta(img, cam, (-16.0, 3.0, -EMB_LADO), 'Pinchos a su paso: mortales', 40, -170)
    etiqueta(img, cam, (-9.0, 14.0, -EMB_LADO - 0.4), 'Lanzado ~15 bloques', 60, -60)
    guardar(img, 'embestida')


# ----------------------------------------------------------------------
#  2. Tumba de Raices
# ----------------------------------------------------------------------
TUMBA_RADIO = 16.0


def tumba(W=1600, H=900, lleno=0.68):
    cam = vr.Camara(ojo=(-25.0, 9.5, -14.0), objetivo=(0.5, 2.0, 4.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 80)
    escena = plaza_templo(26, 70, 44) + ts.piramide(4, 42) + ts._arboles((-34, 20, 16, 10), (30, 26, 18, 11))
    ts.dibujar_mundo(lz, cam, escena, niebla, 3)
    r = random.Random(9)
    cx, cz = 0.0, 4.0
    # las grietas de las raices dentro de lo llenado (lo oscuro)
    grietas = []
    for k in range(10):
        a = TAU * k / 10 + r.uniform(-0.2, 0.2)
        d1 = TUMBA_RADIO * lleno * r.uniform(0.8, 1.0)
        grietas.append((cx + math.cos(a) * 3.0, cz + math.sin(a) * 3.0, cx + math.cos(a) * d1, cz + math.sin(a) * d1,
                        r.uniform(0.5, 0.8), 80 + k))
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], parte='oscura')
    # jugadores huyendo hacia fuera: uno que ya esta fuera, uno en el borde, uno a
    # medio camino y uno que se ha quedado pegado a el
    for (d, a, g) in ((19.5, -0.7, 200), (15.0, 2.2, 40), (10.5, 3.6, 250), (6.2, -2.4, 140)):
        ts.jugador(lz, cam, cx + math.cos(a) * d, cz + math.sin(a) * d, g, niebla=niebla)
    pose = ra.sumar(ra.pose_en('TERREMOTO', 1.1), ra.cabeza(x=6, boca=6))
    rajang(lz, cam, cx, cz, guinada_hacia(-1, 0.25), pose, 3, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # lo que brilla
    ta.calco(lz, cam, cx, cz, TUMBA_RADIO, _tex_tumba(lleno=lleno), 1.15, y=0.05)
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], brillo=1.0, parte='brillo')
    img = ts.componer(lz, W, H, ts.horizonte(cam), 24, oscuro=0.25, rayos=False)
    ta.polvo_en(img, cam, [(cx, 0.5, cz, 6.0)], SS, (110, 120, 80), 25)
    etiqueta(img, cam, (cx - TUMBA_RADIO * 0.7, 0.05, cz - TUMBA_RADIO * 0.7), 'Borde: salir antes de que se llene', -60, 110)
    etiqueta(img, cam, (cx - TUMBA_RADIO * lleno * 0.8, 0.05, cz + TUMBA_RADIO * lleno * 0.5), 'Lo llenado (crece desde él)', -420, -60)
    guardar(img, 'tumba')


# ----------------------------------------------------------------------
#  3. El Sello endurecido: una columna de cerca con su espiral de piedras
# ----------------------------------------------------------------------
COL_ALTO, COL_RADIO = 26.0, 4.0


def sello(W=1600, H=900):
    cam = vr.Camara(ojo=(-21.0, 17.0, -22.0), objetivo=(0.0, 15.0, 0.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(40, 90)
    escena = plaza_templo(26, 60, 44) + ts._arboles((-30, 26, 17, 10), (26, 34, 19, 11), (-10, 44, 20, 12))
    ts.dibujar_mundo(lz, cam, escena, niebla, 2)
    r = random.Random(17)
    mallas = ta.plataforma(0, 0, COL_ALTO, 4.6, semilla=3)
    # la espiral: 25 piedras, un bloque mas alta cada una
    tiembla, cae, falta = 20, 9, 14
    a0 = -2.2
    pasos = []
    for k in range(25):
        a = a0 + k * 0.62
        px, pz = math.cos(a) * COL_RADIO, math.sin(a) * COL_RADIO
        h = 1.0 + k * (COL_ALTO / 26.0)
        if k == falta:
            pasos.append((px, h, pz, 'falta'))
            continue
        if k == cae:
            # cayendo: tres bloques por debajo de su sitio, ladeada
            caida = ta.piedra_flotante(0, 0, 0, 1.05, semilla=k)
            M = vr.T(px + 0.4, h - 3.2, pz - 0.3) @ vr.Rz(0.45) @ vr.Rx(-0.3)
            mallas += [(np.array([(M @ np.array([*p, 1.0]))[:3] for p in P]), UV, m) for P, UV, m in caida]
            pasos.append((px, h, pz, 'cae'))
            continue
        if k == tiembla:
            pieza = ta.piedra_flotante(0, 0, 0, 1.05, semilla=k)
            M = vr.T(px + 0.12, h, pz - 0.08) @ vr.Rz(0.06) @ vr.Rx(-0.05)
            mallas += [(np.array([(M @ np.array([*p, 1.0]))[:3] for p in P]), UV, m) for P, UV, m in pieza]
            pasos.append((px, h, pz, 'tiembla'))
            continue
        mallas += ta.piedra_flotante(px, h, pz, 1.05, semilla=k)
        pasos.append((px, h, pz, 'ok'))
    # el totem de arriba, roto: el pulso lo acaba de reventar
    mallas += ta.totem(0, COL_ALTO - 0.05, 0, 'on', 1.5, giro=30, semilla=2, roto=True)
    for j in range(10):
        a = r.uniform(0, TAU)
        mallas += ta.roca_cubica(math.cos(a) * r.uniform(2.5, 6), COL_ALTO + r.uniform(0.5, 3.5), math.sin(a) * r.uniform(2.5, 6),
                                 r.uniform(0.15, 0.35), semilla=400 + j)
    ta.dibujar(lz, cam, mallas, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # jugadores: el que rompio el totem, echado de la columna por el pulso (en
    # horizontal, sin subir); uno que esperaba en la piedra que se cae, cayendo;
    # y uno subiendo
    ts.jugador(lz, cam, -6.2, -2.4, 70, y=COL_ALTO + 0.2, niebla=niebla)
    pc = pasos[cae]
    ts.jugador(lz, cam, pc[0] + 0.3, pc[2] - 0.2, 120, y=pc[1] - 1.8, niebla=niebla)
    p12 = pasos[11]
    ts.jugador(lz, cam, p12[0], p12[2], 200, y=p12[1], niebla=niebla)
    # lo que brilla: el pulso del totem, los aros bajo las piedras y el aviso del que tiembla
    ta.calco(lz, cam, 0, 0, 7.0, ta.ONDA, 1.4, y=COL_ALTO + 0.08)
    ta.calco(lz, cam, 0, 0, 4.2, ta.ONDA, 1.0, y=COL_ALTO + 0.1)
    ta.cartel(lz, cam, (0, COL_ALTO + 2.0, 0), 3.0, ta.HALO, 1.0)
    for (px, h, pz, est) in pasos:
        if est == 'ok':
            ta.calco(lz, cam, px, pz, 1.0, ts.ARO_PIEDRA, 0.6, y=h - 0.75)
        elif est == 'tiembla':
            ta.calco(lz, cam, px, pz, 1.4, ta.AVISO, 1.4, y=h + 0.06)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 26, oscuro=0.3)
    pt = pasos[tiembla]
    ta.polvo_en(img, cam, [(pt[0], pt[1] - 0.8, pt[2], 1.0), (pc[0], pc[1] - 2.0, pc[2], 1.6)], SS, (128, 110, 80), 27)
    # el temblor: rayas cortas a los lados del escalon que tiembla
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(capa)
    sx, sy, _ = cam.proyectar((pt[0], pt[1] - 0.3, pt[2]))
    sx, sy = sx / SS, sy / SS
    for k in range(3):
        for s in (-1, 1):
            x0 = sx + s * (46 + k * 12)
            dr.line([(x0, sy - 14 + k * 9), (x0 + s * 10, sy - 8 + k * 9)], fill=(240, 255, 210, 200), width=3)
    img.alpha_composite(capa)
    # la piedra que cae: rayas de caida hacia arriba
    lineas_movimiento(img, cam, (pc[0], pc[1] - 3.0, pc[2]), (0, -1, 0), 10, 3.0, 28, (230, 220, 190), 2)
    # el echado por el pulso: rayas horizontales
    lineas_movimiento(img, cam, (-6.2, COL_ALTO + 1.0, -2.4), (-0.93, 0, -0.36), 12, 4.0, 29)
    etiqueta(img, cam, (0, COL_ALTO + 0.5, 0), 'Pulso al romper el tótem', -320, 40)
    etiqueta(img, cam, (-6.2, COL_ALTO + 1.0, -2.4), 'Echado de la columna (sin alzar)', 60, 40)
    etiqueta(img, cam, (pt[0], pt[1], pt[2]), 'Tiembla 1 s…', 120, -10)
    etiqueta(img, cam, (pc[0], pc[1] - 3.0, pc[2]), '…se cae y vuelve a los 3 s', -330, 20)
    guardar(img, 'sello')


# ----------------------------------------------------------------------
#  4. La Furia de Jade: el aura verde tras un Sello fallido
# ----------------------------------------------------------------------
def aura(lz, cam, qs, centro, hincha=0.16, brillo=0.55):
    """La capa del aura: cada cara un poco hacia fuera, con las bandas que
    corren en diagonal (el UV sale del sitio en el mundo, como la carga del
    creeper que se desliza por encima del cuerpo)."""
    c = np.array(centro, float)
    for Pq, _, _, _ in qs:
        P = [np.array(p) for p in Pq]
        n = vr.normal(P)
        if n @ (np.mean(P, axis=0) - c) < 0:
            n = -n
        P = [p + n * hincha for p in P]
        UV = [((p[0] * 0.6 + p[2] * 0.6) * 0.22, p[1] * 0.22) for p in P]
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], AURA, np.ones(3), None, None, aditivo=True,
                         brillo=brillo, envolver=True)


def furia(W=1600, H=900):
    cam = vr.Camara(ojo=(-14.0, 2.2, -20.0), objetivo=(1.0, 5.0, 2.0), fov=50, ancho=W * SS, alto=H * SS)
    lz = Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(26, 60)
    niebla.color = (0.08, 0.16, 0.1)
    luces = [((-0.4, 0.9, -0.5), (0.7, 1.0, 0.6), 0.85, 'llave'), ((0.7, 0.3, 0.7), (0.5, 1.0, 0.4), 1.4, 'contra'),
             ((-0.8, 0.2, 0.6), (0.4, 1.0, 0.5), 0.9, 'contra')]
    amb = (0.13, 0.2, 0.14)
    escena = plaza_templo(26, 60, 40) + ts.piramide(6, 40)
    ts.dibujar_mundo(lz, cam, escena, niebla, 3, luces, amb)
    r = random.Random(30)
    grietas = []
    for k in range(9):
        a = TAU * k / 9 + r.uniform(-0.25, 0.25)
        d1 = r.uniform(8, 15)
        grietas.append((2.5 + math.cos(a) * 3, 4 + math.sin(a) * 3, 2.5 + math.cos(a) * d1, 4 + math.sin(a) * d1,
                        r.uniform(0.5, 0.8), 120 + k))
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], parte='oscura')
    ts.jugador(lz, cam, -6.5, -7.0, 200, niebla=niebla)
    ts.jugador(lz, cam, -10.0, -3.0, 230, niebla=niebla)
    pose = ra.sumar(ra.cuerpo(x=-5, baja=14), ra.mano(1, 14.0, -29.5, 20.5, 9), ra.mano(-1, 20.0, -28.9, 13.9, 9),
                    ra.pata(1, -33.4, 38.3, -10, 10.1, 5), ra.pata(-1, -30.1, 43.2, -10, 1.9, 5),
                    ra.cabeza(x=8, y=-16, boca=36, cuello=14, cuello_y=-12, orejas=-26),
                    ra.cola(sube=34, lado=-24, fase=1.4, onda=18))
    qs = rajang(lz, cam, 2.5, 4.0, -40, pose, 3, luces, amb, niebla, k_cristal=0.7)
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], brillo=1.2, parte='brillo')
    aura(lz, cam, qs, (2.5, 4.0, 4.0))
    ta.calco(lz, cam, 2.5, 4.0, 11.0, ta.ONDA, 0.5)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 31, oscuro=0.55, rayos=False)
    # llamas verdes que suben del cuerpo
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(capa)
    for _ in range(90):
        p = (2.5 + r.uniform(-4, 4), r.uniform(1, 10), 4 + r.uniform(-8, 8))
        sx, sy, z = cam.proyectar(p)
        if z < 1:
            continue
        rr = r.uniform(3, 9)
        sx, sy = sx / SS, sy / SS
        dr.polygon([(sx - rr, sy), (sx, sy - rr * 3.2), (sx + rr, sy)], fill=(120, 255, 100, r.randint(60, 150)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(3)))
    etiqueta(img, cam, (2.5, 8.5, 4.0), 'Furia de Jade: más rápido y más daño', 120, -110)
    guardar(img, 'furia')


ESCENAS = {'embestida': embestida, 'tumba': tumba, 'sello': sello, 'furia': furia}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)
