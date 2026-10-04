"""
Renders de la opcion C ("La Leyenda de las Mareas") y la comparativa A / C.

Uso: python nerea_c_escenas.py <raiz del proyecto> <carpeta de salida> [escena,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ, OUT = sys.argv[1], sys.argv[2]
SOLO = sys.argv[3].split(',') if len(sys.argv) > 3 else None
sys.argv = sys.argv[:3]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_c_modelo as nc
import nerea_escenas as ne

SS, FUENTE, TEX = ne.SS, ne.FUENTE, ne.TEX
LUCES = [((-0.3, 1.0, -0.4), (0.6, 0.85, 0.95), 1.05, 'llave'),
         ((0.7, 0.2, 0.8), (0.85, 0.35, 0.95), 1.0, 'contra'),       # la perla tine la espalda de violeta
         ((-0.9, 0.1, 0.3), (0.2, 0.75, 0.95), 0.55, 'contra')]
AMB = (0.16, 0.22, 0.28)
ESC_A = 1.6

def escena(nombre, W, H, cam, piezas, semilla=3, rayos_k=1.0, burbujas_extra=None):
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(10, 40)
    ne.suelo(lz, cam, ext=22, prof=46, niebla=niebla)
    for fn in piezas:
        fn(lz, cam, niebla)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    img = ne.componer(lz, W, H, horiz, semilla, rayos_k)
    if burbujas_extra:
        img = burbujas_extra(img, cam)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)

def figura(p, libre=False, x=0.0, z=0.0, guinada=18):
    def f(lz, cam, n):
        nc.dibujar(lz, cam, nm.quads(nc.esqueleto(libre), nc.pose(p), nm.entidad_a_mundo(x, 0, z, guinada)), LUCES, AMB, n, brillo=1.5)
    return f

def pilares(lz, cam, n, alto=11):
    nm.dibujar(lz, cam, ne.pilar(-10, 13, alto) + ne.pilar(11, 12, alto), LUCES, AMB, n)

def cadenas(lz, cam, n, pares):
    for p0, p1 in pares:
        nm.dibujar(lz, cam, nm.cadena_mundo(p0, p1, 2.6), LUCES, AMB, n)

# ---------------------------------------------------------------- poses
REPOSO = {
    'brazo_izq': {'rot': (-30, 0, -26)}, 'antebrazo_izq': {'rot': (-45, 0, 0)},
    'brazo_der': {'rot': (-12, 0, 22)}, 'antebrazo_der': {'rot': (-20, 0, 0)},
}
HEROICA = {
    'pecho': {'rot': (-4, -12, 0)},
    'cuello': {'rot': (12, 0, 0)},
    'cabeza': {'rot': (12, -14, 0)},
    'brazo_izq': {'rot': (-50, 0, -72)}, 'antebrazo_izq': {'rot': (-55, 0, 0)},
    'caracola': {'rot': (-30, 0, 20)},
    'brazo_der': {'rot': (-35, 0, 74)}, 'antebrazo_der': {'rot': (-35, 0, 0)},
    'latigo': {'rot': (40, 0, -20)},
}
CARACOLA = {
    'pecho': {'rot': (-8, 10, 0)},
    'cuello': {'rot': (0, 0, 0)},
    'cabeza': {'rot': (-6, 10, 0)},
    'brazo_izq': {'rot': (-150, 10, 6)}, 'antebrazo_izq': {'rot': (-70, 0, 0)},
    'caracola': {'rot': (-30, 0, 20)},
    'brazo_der': {'rot': (-40, 0, 60)}, 'antebrazo_der': {'rot': (-40, 0, 0)},
}
LIBERADO = {
    'abdomen': {'rot': (4, 0, 0)},
    'pecho': {'rot': (18, 0, -10)},
    'cuello': {'rot': (20, 0, 8)},
    'cabeza': {'rot': (14, 0, 0)},
    'brazo_izq': {'rot': (-20, 0, -40)}, 'antebrazo_izq': {'rot': (-30, 0, 0)},
    'brazo_der': {'rot': (-20, 0, 40)}, 'antebrazo_der': {'rot': (-30, 0, 0)},
}

# ---------------------------------------------------------------- escenas
def c_heroica(W=1600, H=900):
    cam = vr.Camara(ojo=(-6.4, 0.5, -9.4), objetivo=(0.6, 6.0, 0), fov=64, ancho=W * SS, alto=H * SS)
    def pil(lz, cam, n):
        pilares(lz, cam, n)
        cadenas(lz, cam, n, (((-0.9, 5.4, 0.8), (-10, 10, 12.2)), ((1.0, 5.2, 0.8), (11, 10, 11.2)),
                             ((-0.8, 3.2, 0.6), (-9.6, 1.8, 12.2)), ((0.9, 3.0, 0.6), (10.6, 1.8, 11.2))))
    escena('c_heroica', W, H, cam, [pil, figura(HEROICA, guinada=22)])

def c_vistas(W=1500, H=760):
    lienzos = []
    for g in (0, -90, 180):
        cam = vr.Camara(ojo=(0, 4.9, -70), objetivo=(0, 4.9, 0), fov=9.0, ancho=500 * SS, alto=H * SS)
        lz = vr.Lienzo(500 * SS, H * SS)
        luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.9, 'llave'), ((0.6, 0.3, 0.8), (0.7, 0.6, 1), 0.5, 'contra')]
        nc.dibujar(lz, cam, nm.quads(nc.esqueleto(), nc.pose(REPOSO), nm.entidad_a_mundo(0, 0, 0, g)), luces, (0.34, 0.36, 0.4), brillo=1.2)
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
        lienzos.append(Image.fromarray((arr * 255).astype(np.uint8)).resize((500, H), Image.LANCZOS))
    img = Image.new('RGB', (W, H), (237, 242, 245))
    for i, im in enumerate(lienzos):
        img.paste(im, (i * 500, 0))
    img.save(os.path.join(OUT, 'c_vistas.jpg'), quality=92)

def mundo(raiz, pose, M, objetivo, local=(0, 0, 0)):
    """Posicion en el mundo de un punto local de un hueso."""
    res = {}
    def visitar(n, Mp):
        nombre, off, rot, cajas, hijos = n
        ex = pose.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        Mn = Mp @ vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(ex.get('esc', 1.0))
        if nombre == objetivo:
            res['p'] = (M @ Mn @ np.array([*local, 1.0]))[:3]
        for h in hijos:
            visitar(h, Mn)
    visitar(raiz, np.eye(4))
    return res['p']

def c_caracola(W=1600, H=900):
    cam = vr.Camara(ojo=(-4.5, 2.2, -15.5), objetivo=(-0.6, 5.2, 0), fov=52, ancho=W * SS, alto=H * SS)
    guinada = 6
    jugadores = ((-6.5, -7.5, 200), (-2.0, -9.5, 170), (3.8, -8.0, 150))
    pose = nc.pose(CARACOLA)
    M = nm.entidad_a_mundo(0, 0, 0, guinada)
    boca = mundo(nc.esqueleto(), pose, M, 'boca_car', (0, 2, 0))
    def todo(lz, cam, n):
        pilares(lz, cam, n)
        nc.dibujar(lz, cam, nm.quads(nc.esqueleto(), pose, M), LUCES, AMB, n, brillo=1.5)
        for (x, z, g) in jugadores:
            nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(x, z, g)), LUCES, AMB, n)
    def burbujas(img, cam):
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for k, (x, z, _) in enumerate(jugadores):
            fin = np.array([x, 1.2, z])
            for t in (0.22, 0.48, 0.74):
                p = boca + (fin - boca) * t + np.array([0, 1.4 * math.sin(math.pi * t), 0])
                px, py, prof = cam.proyectar(p)
                rad = 0.55 * cam.foco / prof / SS
                px /= SS; py /= SS
                d.ellipse((px - rad, py - rad, px + rad, py + rad), fill=(120, 220, 255, 55), outline=(210, 245, 255, 230), width=2)
                d.ellipse((px - rad * 0.55, py - rad * 0.6, px - rad * 0.15, py - rad * 0.2), fill=(240, 255, 255, 210))
                d.ellipse((px - rad * 0.28, py - rad * 0.28, px + rad * 0.28, py + rad * 0.28), fill=(255, 110, 200, 150))
        # una ya revento junto a un jugador: la onda
        px, py, prof = cam.proyectar(np.array([3.8, 0.6, -8.0]))
        px /= SS; py /= SS
        esc = cam.foco / prof / SS
        for r_, a_ in ((2.4, 150), (1.6, 110), (0.9, 220)):
            d.ellipse((px - r_ * esc, py - r_ * esc * 0.4, px + r_ * esc, py + r_ * esc * 0.4), outline=(255, 140, 210, a_), width=4)
        return Image.alpha_composite(img.convert('RGBA'), capa.filter(ImageFilter.GaussianBlur(0.8)))
    escena('c_caracola', W, H, cam, [todo], 13, 0.8, burbujas)

def c_liberado(W=1600, H=900):
    cam = vr.Camara(ojo=(-8.5, 2.6, -16.5), objetivo=(0.4, 4.8, 0), fov=42, ancho=W * SS, alto=H * SS)
    def todo(lz, cam, n):
        nm.dibujar(lz, cam, ne.pilar(-9, 11, 11), LUCES, AMB, n)
        figura(LIBERADO, libre=True, guinada=8)(lz, cam, n)
    escena('c_liberado', W, H, cam, [todo])

def escala(W=1700, H=900):
    cam = vr.Camara(ojo=(-1.0, 5.4, -120), objetivo=(-1.0, 5.4, 0), fov=6.0, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.33, 0.35, 0.39)
    xs = {'jugador': 9.6, 'vigia': 7.0, 'a': 1.4, 'c': -7.2}
    qa = nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(xs['a'], 0, 0, -20, ESC_A))
    qc = nm.quads(nc.esqueleto(), nc.pose(REPOSO), nm.entidad_a_mundo(xs['c'], 0, 0, -20))
    nm.dibujar(lz, cam, qa, luces, amb, brillo=1.2)
    nc.dibujar(lz, cam, qc, luces, amb, brillo=1.2)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vbr = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vr.dibujar_quads(lz, cam, vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(xs['vigia'], 0, 0, -20)), vt,
                     emis=vbr, luces=luces, ambiente=amb, brillo=1.2)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(xs['jugador'], 0, -20)), luces, amb)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 12):
        _, y, _ = cam.proyectar((0, b, 0)); y /= SS
        if 0 <= y <= H:
            d.line((60, y, W - 20, y), fill=(40, 70, 80, 110 if b else 220), width=2 if b == 0 else 1)
            d.text((22, y - 11), f'{b}', font=f, fill=(40, 70, 80, 255))
    img = Image.alpha_composite(img, rej)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 28)
    fa = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 17)
    alto_a = max(max(p[1] for p in q[0]) for q in qa)
    alto_c = max(max(p[1] for p in q[0]) for q in qc)
    for nombre, x, alto in (('JUGADOR', xs['jugador'], 1.8), ('VIGÍA', xs['vigia'], 2.9),
                            ('NEREA · A', xs['a'], alto_a), ('NEREA · C', xs['c'], alto_c)):
        px_, py, _ = cam.proyectar((x, alto + 0.3, 0)); px_ /= SS; py /= SS
        cifra = f'{alto:.1f}'.replace('.', ',') + ' bloques'
        wn = d.textlength(nombre, font=fn); wa = d.textlength(cifra, font=fa)
        d.text((px_ - wn / 2, py - 62), nombre, font=fn, fill=(16, 52, 60, 255))
        d.text((px_ - wa / 2, py - 24), cifra, font=fa, fill=(60, 96, 104, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala_ac.jpg'), quality=92)
    print('alturas A=%.2f C=%.2f' % (alto_a, alto_c))

TAREAS = {'c_heroica': c_heroica, 'c_vistas': c_vistas, 'c_caracola': c_caracola,
          'c_liberado': c_liberado, 'escala': escala}

if __name__ == '__main__':
    for k in (SOLO or TAREAS):
        TAREAS[k]()
        print('hecho', k)
