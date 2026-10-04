"""
Ficha v2 de Nerea: los dos disenos a 9-10 bloques.

  A  "El Guardian Ahogado": el de las referencias, escalado x1,6 (~9 bloques)
  B  "La Marea Encadenada": propuesta propia (~10 bloques)

Uso: python nerea_v2.py <raiz del proyecto> <carpeta de salida> [escena,escena,...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ, OUT = sys.argv[1], sys.argv[2]
SOLO = sys.argv[3].split(',') if len(sys.argv) > 3 else None
sys.argv = sys.argv[:3]                      # nerea_escenas lee sus propios argumentos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_b_modelo as nb
import nerea_escenas as ne

SS = ne.SS
FUENTE = ne.FUENTE
TEX = ne.TEX
LUCES, AMB = ne.LUCES_MAR, ne.AMB_MAR
ESC_A = 1.6

nm.MAT['llama'] = nm._loseta(50, nm.emisivo('fff6c0', 'ff9a1a'))
nm.EMISIVOS.add('llama')

def altura_real(qs):
    return max(max(p[1] for p in q[0]) for q in qs)

def pilares_grandes(alto=11):
    return ne.pilar(-10, 13, alto) + ne.pilar(11, 12, alto)

def cadenas(lz, cam, n, pares, grosor=2.6):
    for p0, p1 in pares:
        nm.dibujar(lz, cam, nm.cadena_mundo(p0, p1, grosor), LUCES, AMB, n)

def escena(nombre, W, H, cam, piezas, semilla=3, rayos_k=1.0):
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(10, 40)
    ne.suelo(lz, cam, ext=22, prof=46, niebla=niebla)
    for fn in piezas:
        fn(lz, cam, niebla)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    img = ne.componer(lz, W, H, horiz, semilla, rayos_k)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)

# ---------------------------------------------------------------- A
def a_heroica(W=1600, H=900):
    cam = vr.Camara(ojo=(-6.6, 0.45, -9.6), objetivo=(0.4, 6.2, 0), fov=64, ancho=W * SS, alto=H * SS)
    def pil(lz, cam, n):
        nm.dibujar(lz, cam, pilares_grandes(), LUCES, AMB, n)
        cadenas(lz, cam, n, (((-1.1, 6.2, 1.1), (-10, 10, 12.2)), ((1.3, 5.9, 1.1), (11, 10, 11.2)),
                             ((-1.0, 3.4, 1.0), (-9.6, 1.8, 12.2)), ((1.1, 3.2, 1.0), (10.6, 1.8, 11.2))))
    def ner(lz, cam, n):
        nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), ne.HEROICA, nm.entidad_a_mundo(0, 0, 0, 24, ESC_A)), LUCES, AMB, n, brillo=1.5)
    escena('a_heroica', W, H, cam, [pil, ner])

def a_molino(W=1600, H=900):
    cam = vr.Camara(ojo=(-12, 16.5, -18), objetivo=(0, 2.0, 0), fov=46, ancho=W * SS, alto=H * SS)
    R, alto = 11.0, 1.3
    def todo(lz, cam, n):
        nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), ne.MOLINO, nm.entidad_a_mundo(0, 0, 0, 20, ESC_A)), LUCES, AMB, n, brillo=1.5)
        pares = [((0.4 * math.cos(math.radians(20 + k * 90)), 3.8, 0.4 * math.sin(math.radians(20 + k * 90))),
                  (R * math.cos(math.radians(20 + k * 90)), alto, R * math.sin(math.radians(20 + k * 90)))) for k in range(4)]
        pares += [((R * math.cos(2 * math.pi * k / 34), alto, R * math.sin(2 * math.pi * k / 34)),
                   (R * math.cos(2 * math.pi * (k + 1) / 34), alto, R * math.sin(2 * math.pi * (k + 1) / 34))) for k in range(34)]
        cadenas(lz, cam, n, pares)
        for (x, z, g, y) in ((-8.5, -9.0, 40, 0.0), (10.0, -5.5, -60, 1.2), (3.0, 12.5, 200, 0.0), (-13.5, 3.0, 100, 0.0), (1.4, -1.8, 10, 0.0)):
            nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, g)), LUCES, AMB, n)
    escena('a_molino', W, H, cam, [todo], 9, 0.6)

def a_liberado(W=1600, H=900):
    cam = vr.Camara(ojo=(-8.0, 2.4, -17.0), objetivo=(0.3, 4.6, 0), fov=40, ancho=W * SS, alto=H * SS)
    def todo(lz, cam, n):
        nm.dibujar(lz, cam, ne.pilar(-9, 11, 11), LUCES, AMB, n)
        nm.dibujar(lz, cam, nm.quads(nm.esqueleto(True), ne.LIBERADO, nm.entidad_a_mundo(0, 0, 0, 10, ESC_A)), LUCES, AMB, n, brillo=1.5)
    escena('a_liberado', W, H, cam, [todo])

# ---------------------------------------------------------------- B
HEROICA_B = {
    'torso': {'rot': (-2, -14, 0)},
    'casco': {'rot': (12, 12, 4)},
    'brazo_izq': {'rot': (-28, 0, -58)}, 'antebrazo_izq': {'rot': (-55, 0, 0)},
    'cadena_ancla_izq': {'rot': (40, 0, 20)},
    'brazo_der': {'rot': (-75, 0, 42)}, 'antebrazo_der': {'rot': (-15, 0, 0)},
    'cadena_ancla_der': {'rot': (10, 0, 0)},
}
REPOSO_B = {
    # antebrazos al frente y las cadenas a plomo: las anclas cuelgan sin tocar el suelo
    'brazo_izq': {'rot': (-20, 0, -14)}, 'brazo_der': {'rot': (-20, 0, 14)},
    'antebrazo_izq': {'rot': (-70, 0, 0)}, 'antebrazo_der': {'rot': (-70, 0, 0)},
    'cadena_ancla_izq': {'rot': (84, 0, 6)}, 'cadena_ancla_der': {'rot': (84, 0, -6)},
}
LIBERADO_B = {
    'torso': {'rot': (14, 0, 0)},
    'casco': {'rot': (22, 0, 0)},
    'brazo_izq': {'rot': (-4, 0, -6)}, 'brazo_der': {'rot': (-4, 0, 6)},
    'antebrazo_izq': {'rot': (-6, 0, 0)}, 'antebrazo_der': {'rot': (-6, 0, 0)},
    'cadena_ancla_izq': {'oculto': True}, 'cadena_ancla_der': {'oculto': True},
}
REMOLINO_B = {
    'torso': {'rot': (-6, 0, 0)}, 'casco': {'rot': (14, 0, 0)},
    'brazo_izq': {'rot': (-60, 0, -70)}, 'antebrazo_izq': {'rot': (-40, 0, 0)},
    'brazo_der': {'rot': (-60, 0, 70)}, 'antebrazo_der': {'rot': (-40, 0, 0)},
    'cadena_ancla_izq': {'rot': (60, 0, 0)}, 'cadena_ancla_der': {'rot': (60, 0, 0)},
}

def b_figura(pose, libre=False, x=0.0, z=0.0, guinada=18, giro=0.0):
    def f(lz, cam, n):
        nb.dibujar(lz, cam, nm.quads(nb.esqueleto(libre, giro), pose, nm.entidad_a_mundo(x, 0, z, guinada)), LUCES, AMB, n, brillo=1.5)
    return f

def b_heroica(W=1600, H=900):
    cam = vr.Camara(ojo=(-6.2, 0.45, -9.0), objetivo=(0.6, 6.0, 0), fov=64, ancho=W * SS, alto=H * SS)
    def pil(lz, cam, n):
        nm.dibujar(lz, cam, pilares_grandes(), LUCES, AMB, n)
        cadenas(lz, cam, n, (((-1.0, 5.6, 0.9), (-10, 10, 12.2)), ((1.1, 5.4, 0.9), (11, 10, 11.2)),
                             ((-1.0, 3.6, 0.9), (-9.6, 1.8, 12.2)), ((1.1, 3.4, 0.9), (10.6, 1.8, 11.2))))
    escena('b_heroica', W, H, cam, [pil, b_figura(HEROICA_B, giro=8)])

def vistas(nombre, quads_fn, dibujar, alto_cam, fov, W=1500, H=760):
    lienzos = []
    for g in (0, -90, 180):
        cam = vr.Camara(ojo=(0, alto_cam, -70), objetivo=(0, alto_cam, 0), fov=fov, ancho=500 * SS, alto=H * SS)
        lz = vr.Lienzo(500 * SS, H * SS)
        luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
        dibujar(lz, cam, quads_fn(g), luces, (0.32, 0.34, 0.38), brillo=1.2)
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
        lienzos.append(Image.fromarray((arr * 255).astype(np.uint8)).resize((500, H), Image.LANCZOS))
    img = Image.new('RGB', (W, H), (237, 242, 245))
    for i, im in enumerate(lienzos):
        img.paste(im, (i * 500, 0))
    img.save(os.path.join(OUT, nombre + '.jpg'), quality=92)

def b_vistas():
    vistas('b_vistas', lambda g: nm.quads(nb.esqueleto(), REPOSO_B, nm.entidad_a_mundo(0, 0, 0, g)), nb.dibujar, 5.0, 8.8)

def a_vistas():
    vistas('a_vistas', lambda g: nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(0, 0, 0, g, ESC_A)), nm.dibujar, 4.8, 8.8)

def espiral_espuma():
    qs = []
    base = vr.T(0, 0.04, 0) @ np.diag([1 / 16, 1 / 16, 1 / 16, 1])
    for i in range(300):
        t = i / 300
        a = t * 2 * math.pi * 3.2
        r = 1.6 + t * 12.5
        raiz = nm.nodo('esp', (r * math.cos(a) * 16, 0, r * math.sin(a) * 16), (0, -math.degrees(a), 0),
                       [((-7, 0, -3, 14, 1.2, 6), 'espuma')])
        qs += nm.quads(raiz, {}, base)
    return qs

def b_remolino(W=1600, H=900):
    cam = vr.Camara(ojo=(-13, 13.0, -19), objetivo=(0, 3.0, 0), fov=46, ancho=W * SS, alto=H * SS)
    def todo(lz, cam, n):
        nb.dibujar(lz, cam, espiral_espuma(), LUCES, AMB, n)
        b_figura(REMOLINO_B, giro=25)(lz, cam, n)
        # arrastrados hacia el centro, ladeados por la corriente
        for (x, z) in ((-7.5, -6.0), (8.0, -4.0), (6.0, 8.0), (-9.0, 5.0)):
            ang = math.degrees(math.atan2(-x, -z))
            M = ne.jugador_a_mundo(x, z, ang + 180) @ vr.T(0, 24, 0) @ vr.Rx(-24 * vr.D2R) @ vr.T(0, -24, 0)
            nm.dibujar(lz, cam, nm.quads(ne.jugador(), {'bd': {'rot': (-150, 0, 0)}, 'bi': {'rot': (-150, 0, 0)}}, M), LUCES, AMB, n)
        # el de la antorcha, quieto
        M = ne.jugador_a_mundo(-3.0, -11.5, 200)
        nm.dibujar(lz, cam, nm.quads(ne.jugador(), {'bd': {'rot': (-80, 0, 0)}}, M), LUCES, AMB, n)
        antorcha = nm.nodo('t', (0, 0, 0), (0, 0, 0), [((-1, -10, -1, 2, 10, 2), 'oxido'), ((-1.8, -15, -1.8, 3.6, 5, 3.6), 'llama')])
        mano = M @ vr.T(-6, 2, 0) @ vr.Rx(-80 * vr.D2R) @ vr.T(0, 10, 0) @ vr.Rx(80 * vr.D2R)
        nm.dibujar(lz, cam, nm.quads(antorcha, {}, mano), LUCES, AMB, n)
    escena('b_remolino', W, H, cam, [todo], 11, 0.7)

def b_liberado(W=1600, H=900):
    cam = vr.Camara(ojo=(-8.5, 3.0, -17.0), objetivo=(0.4, 5.0, 0), fov=42, ancho=W * SS, alto=H * SS)
    def todo(lz, cam, n):
        nm.dibujar(lz, cam, ne.pilar(-9, 11, 11), LUCES, AMB, n)
        for (x, z, g) in ((-4.2, -1.2, 20), (3.8, -0.8, -30)):
            M = vr.T(x, 0.25, z) @ vr.Ry(g * vr.D2R) @ vr.Rz(90 * vr.D2R) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
            nm.dibujar(lz, cam, nm.quads(nb.ancla('a', (0, 0, 0)), {}, M), LUCES, AMB, n)
        b_figura(LIBERADO_B, libre=True, guinada=8)(lz, cam, n)
    escena('b_liberado', W, H, cam, [todo])

# ---------------------------------------------------------------- escala
def escala(W=1700, H=900):
    cam = vr.Camara(ojo=(-1.0, 5.4, -120), objetivo=(-1.0, 5.4, 0), fov=6.0, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.32, 0.34, 0.38)
    # la camara mira a +Z: +X queda a la IZQUIERDA de la imagen
    xs = {'jugador': 9.6, 'vigia': 7.0, 'a': 1.4, 'b': -7.0}
    qa = nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(xs['a'], 0, 0, -20, ESC_A))
    qb = nm.quads(nb.esqueleto(), REPOSO_B, nm.entidad_a_mundo(xs['b'], 0, 0, -20))
    nm.dibujar(lz, cam, qa, luces, amb, brillo=1.2)
    nb.dibujar(lz, cam, qb, luces, amb, brillo=1.2)
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
    alto_a, alto_b = altura_real(qa), altura_real(qb)
    for nombre, x, alto in (('JUGADOR', xs['jugador'], 1.8), ('VIGÍA', xs['vigia'], 2.9),
                            ('NEREA · A', xs['a'], alto_a), ('NEREA · B', xs['b'], alto_b)):
        px_, py, _ = cam.proyectar((x, alto + 0.3, 0)); px_ /= SS; py /= SS
        cifra = f'{alto:.1f}'.replace('.', ',') + ' bloques'
        wn = d.textlength(nombre, font=fn); wa = d.textlength(cifra, font=fa)
        d.text((px_ - wn / 2, py - 62), nombre, font=fn, fill=(16, 52, 60, 255))
        d.text((px_ - wa / 2, py - 24), cifra, font=fa, fill=(60, 96, 104, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala_v2.jpg'), quality=92)
    print('alturas A=%.2f B=%.2f' % (alto_a, alto_b))

TAREAS = {'a_heroica': a_heroica, 'a_molino': a_molino, 'a_liberado': a_liberado, 'a_vistas': a_vistas,
          'b_heroica': b_heroica, 'b_vistas': b_vistas, 'b_remolino': b_remolino, 'b_liberado': b_liberado,
          'escala': escala}

if __name__ == '__main__':
    for k in (SOLO or TAREAS):
        TAREAS[k]()
        print('hecho', k)
