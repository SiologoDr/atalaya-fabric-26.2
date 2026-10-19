"""
Las fotos de las fichas del bestiario (18-10-2026), como las del Fogonazo y el Coco: el mob en su sitio, en plano bajo,
con su luz, la niebla, el revelado (tono, bloom, viñeta) y el contorno blanco; sin letras. Pinta los modelos del juego
(bestiario.Modelo, ya exportados) en las escenas, así que lo que se ve en la ficha es lo que sale en el juego.

  sitios     noche (el campo de noche del Fogonazo: césped, hierba alta, flores, cerca y robles), cueva, nieve, nether
  escenas    heroe (plano bajo, de tres cuartos), cabeza (de cerca), fila (todos juntos con un jugador de escala)
  ficha      la página (local; no se publica) con las fotos y lo que cuenta cada uno

Uso (desde otro script):  import bestiario_escenas as be;  be.heroe(m, 'noche', ruta);  be.fila([...], ruta)
"""
import html
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import bestiario as B
import bestias_modelo as bm
import nerea_escenas as ne
import nerea_modelo as nm
import quimeras_escenas as qe
import quimeras_modelo as qm
import vigia_render as vr

RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
TAU = math.tau
_r = bm._r


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


# ======================================================================================================================
#  Los sitios
# ======================================================================================================================
SITIOS = {
    'noche': dict(luces=[((-0.5, 0.75, 0.4), (0.66, 0.78, 1.0), 0.75, 'llave'), ((-0.45, 0.5, -1.0), (0.66, 0.78, 1.0), 0.9, 'contra')],
                  amb=(0.2, 0.23, 0.3), niebla=(0.025, 0.035, 0.06), niebla_d=(12, 60),
                  cielo=((0.008, 0.012, 0.03), (0.02, 0.035, 0.08), (0.06, 0.09, 0.16)), luna=(0.66, 0.78, 1.0),
                  suelo='cesped', cerca=True),
    'nieve': dict(luces=[((-0.5, 0.8, 0.4), (0.8, 0.88, 1.0), 0.9, 'llave'), ((-0.4, 0.5, -1.0), (0.7, 0.8, 1.0), 0.8, 'contra')],
                  amb=(0.28, 0.31, 0.38), niebla=(0.12, 0.14, 0.2), niebla_d=(12, 55),
                  cielo=((0.03, 0.04, 0.08), (0.08, 0.1, 0.18), (0.2, 0.24, 0.34)), luna=(0.8, 0.88, 1.0),
                  suelo='nieve', cerca=False),
    'cueva': dict(luces=[((-0.3, 0.9, 0.5), (0.55, 0.6, 0.75), 0.45, 'llave'), ((-0.4, 0.4, -1.0), (0.5, 0.55, 0.7), 0.6, 'contra')],
                  amb=(0.12, 0.13, 0.17), niebla=(0.02, 0.025, 0.035), niebla_d=(6, 30),
                  cielo=((0.01, 0.012, 0.018), (0.015, 0.018, 0.026), (0.02, 0.024, 0.034)), luna=None,
                  suelo='piedra', cerca=False),
    'nether': dict(luces=[((-0.4, 0.8, 0.5), (1.0, 0.6, 0.4), 0.7, 'llave'), ((-0.3, 0.4, -1.0), (1.0, 0.4, 0.25), 0.9, 'contra')],
                   amb=(0.3, 0.14, 0.1), niebla=(0.12, 0.03, 0.02), niebla_d=(10, 50),
                   cielo=((0.08, 0.01, 0.01), (0.16, 0.03, 0.02), (0.28, 0.07, 0.03)), luna=None,
                   suelo='netherrack', cerca=False),
    'end': dict(luces=[((-0.4, 0.8, 0.5), (0.92, 0.84, 1.0), 0.75, 'llave'), ((-0.3, 0.4, -1.0), (0.75, 0.55, 0.95), 0.85, 'contra')],
                amb=(0.22, 0.18, 0.28), niebla=(0.05, 0.03, 0.08), niebla_d=(12, 60),
                cielo=((0.015, 0.008, 0.03), (0.04, 0.025, 0.07), (0.09, 0.055, 0.13)), luna=None,
                suelo='endstone', cerca=False),
}

CESPED = _r('16240e', '1e3014', '283c1a', '334a20', '405a28')
TIERRA = _r('1e140c', '2a1c12', '382618', '46301e', '563c26')
HIERBA = _r('14240c', '1c3212', '284418', '34561e', '426a26')
MADERA = _r('2a1c10', '3a2816', '4e361e', '644628', '7a5832')
TRONCO = _r('1a120a', '261a10', '342416', '42301c', '503a22')
HOJAS = _r('0c180a', '12220e', '1a2e14', '223a18', '2c481e')
NIEVE = _r('8a96aa', 'a8b4c6', 'c8d2e0', 'dfe6f0', 'f2f6fa')
PIEDRA = _r('1c1c20', '26262c', '303038', '3c3c46', '4a4a56')
NETHER = _r('3a0e0c', '541412', '6e1c18', '86261e', '9e3226')
FIN = _r('7e7856', '9e9868', 'bcb684', 'd4ce9c', 'e8e2b4')
OBSID = _r('08050e', '120c1c', '1c142a', '281c3c', '362650')


def _losa(rampa, semilla, n=16):
    rng = random.Random(semilla)
    idx = np.full((n, n), 2)
    for _ in range(24):
        x, y = rng.randrange(n), rng.randrange(n)
        idx[y, x] = rng.choice((1, 3, 3))
        if rng.random() < 0.5:
            idx[(y + 1) % n, x] = idx[y, x]
    return bm._imagen(idx, rampa)


for _n, _rp in (('cesped', CESPED), ('nieve', NIEVE), ('piedra', PIEDRA), ('netherrack', NETHER), ('endstone', FIN)):
    qm._reg('be_' + _n, _losa(_rp, 5))


def p_tierra(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    t = bm._imagen(np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 6) == 0, 1, 2), TIERRA)
    borde = ys < 3 + ((xs * 7 + s) % 3 == 0)
    t[borde] = bm._imagen(np.full((th, tw), 2), CESPED)[borde]
    return t, None


def p_cesped(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((xs * 3 + ys * 5 + s) % 7 == 0, 3, 2), CESPED), None


def p_hierba(tw, th, cara, s):
    t = np.zeros((th, tw, 4), np.uint8)
    rng = random.Random(s)
    for x in range(tw):
        if rng.random() < 0.45:
            continue
        alto = int(th * rng.uniform(0.45, 1.0))
        for y in range(th - alto, th):
            c = HIERBA[3] if y < th - alto + 2 else HIERBA[2 if (x + y) % 3 else 1]
            t[y, x] = (*c, 255)
    return t, None


def p_flor(tw, th, cara, s):
    t = np.zeros((th, tw, 4), np.uint8)
    cx = tw // 2
    t[th // 3:, cx] = (*HIERBA[2], 255)
    for dx, dy in ((0, 0), (-1, 1), (1, 1), (0, 2), (0, 1)):
        if 0 <= cx + dx < tw:
            t[1 + dy, cx + dx] = (120, 150, 230, 255) if (dx, dy) != (0, 1) else (240, 230, 160, 255)
    return t, None


def p_madera(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara in ('arriba', 'abajo'):
        idx = np.where((xs + ys) % 4 == 0, 3, 2)
    else:
        idx = np.where((xs % 4) == 0, 1, 2)
        idx[(ys % 7) == 3] = 3
    return bm._imagen(idx, MADERA), None


def p_tronco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + s) % 4 == 0, 1, 2)
    idx[((ys // 3) + xs + s) % 7 == 0] = 3
    return bm._imagen(idx, TRONCO), None


def p_hojas(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = 2 + (((xs // 2) * 5 + (ys // 2) * 3 + s) % 4 == 0).astype(int) - (((xs // 2) * 3 + (ys // 2) * 7 + s) % 5 == 0)
    return bm._imagen(np.clip(idx, 0, 4), HOJAS), None


def p_monte(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 1, 0), HOJAS), None


def p_roca(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((((xs // 3) * 5 + (ys // 3) * 3 + s) % 5) == 0, 1, 2)
    idx[ys == 0] = 3
    return bm._imagen(idx, PIEDRA), None


def p_obsidiana(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 6) == 0, 3, 1)
    idx[(((xs // 3) * 7 + (ys // 3) * 5 + s) % 9) == 0] = 2
    return bm._imagen(idx, OBSID), None


def p_monte_nieve(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 1, 2), NIEVE), None


for _n, _f in (('tierra', p_tierra), ('cesped', p_cesped), ('hierba', p_hierba), ('flor', p_flor), ('madera', p_madera),
               ('tronco', p_tronco), ('hojas', p_hojas), ('monte', p_monte), ('roca', p_roca),
               ('monte_nieve', p_monte_nieve), ('obsidiana', p_obsidiana)):
    _f.__name__ = 'beE_' + _n


def _hoja(qs, P4, pintor, ancho, alto, semilla=0):
    tw, th = max(1, int(round(ancho * 8))), max(1, int(round(alto * 8)))
    clave = ('beH', pintor.__name__, tw, th, semilla % 7)
    nombre = 'beH_%s_%d_%d_%d' % (pintor.__name__, tw, th, semilla % 7)
    if nombre not in qm.MAT:
        tex, emis = pintor(tw, th, 'frente', semilla)
        qm._reg(nombre, tex, emis, estira=True)
    uv = [(0, 1), (1, 1), (1, 0), (0, 0)]
    qs.append(([np.asarray(p, float) for p in P4], uv, nombre))


def _plano(qs, centro, ancho, alto, giro, pintor, semilla):
    x, y, z = centro
    for a in (giro, giro + math.pi / 2):
        dx, dz = math.cos(a) * ancho / 2, math.sin(a) * ancho / 2
        P4 = ((x - dx, y, z - dz), (x + dx, y, z + dz), (x + dx, y + alto, z + dz), (x - dx, y + alto, z - dz))
        _hoja(qs, P4, pintor, ancho * 2, alto * 2, semilla)


def roble(qs, x, z, alto, semilla):
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.5, 0.0, -0.5, 1.0, alto, 1.0, p_tronco, semilla=semilla)
    bm.cubo(qs, M, -2.5, alto - 1.5, -2.5, 5.0, 2.0, 5.0, p_hojas, semilla=semilla)
    bm.cubo(qs, M, -1.5, alto + 0.5, -1.5, 3.0, 1.2, 3.0, p_hojas, semilla=semilla + 1)


def suelo(lz, cam, niebla, S, luces, libre=None, semilla=4):
    """El suelo del sitio (por bloques cerca y por losas lejos) y lo de alrededor: en el campo, la hierba alta, las
    flores, la cerca y los robles; en la nieve, montes blancos; en la cueva, paredes de roca."""
    libre = libre or (lambda x, z: False)
    r = random.Random(semilla)
    qs = []
    mat = 'be_' + S['suelo']

    def baldosa(gx, gz, p, y):
        P = [(gx + p, y, gz), (gx, y, gz), (gx, y, gz + p), (gx + p, y, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(p, 0), (0, 0), (0, p), (p, p)], mat))
    ext = 64
    for gx in range(-ext, ext, 8):
        for gz in range(-ext, ext, 8):
            if not (-16 <= gx < 16 and -16 <= gz < 16):
                baldosa(gx, gz, 8, 0.0)
    for gx in range(-16, 16):
        for gz in range(-16, 16):
            baldosa(gx, gz, 1, 0.0)
    ojo = cam.ojo
    if S['suelo'] == 'cesped':
        for k in range(260):
            x, z = r.uniform(-13, 13), r.uniform(-13, 13)
            if libre(x, z) or math.hypot(x - ojo[0], z - ojo[2]) < 3.0:
                continue
            if r.random() < 0.14:
                _plano(qs, (x, 0.0, z), 0.5, 0.55, r.uniform(0, 1), p_flor, k % 5)
            else:
                _plano(qs, (x, 0.0, z), 0.9, r.uniform(0.5, 0.9), r.uniform(0, 1), p_hierba, k % 7)
        if S.get('cerca'):
            zc = -4.5
            for x in range(-9, 10, 2):
                if libre(x, zc):
                    continue
                bm.cubo(qs, vr.T(x, 0.0, zc), -0.13, 0.0, -0.13, 0.26, 1.5, 0.26, p_madera, semilla=x % 5)
                if x < 9:
                    for y in (0.55, 1.1):
                        bm.cubo(qs, vr.T(x, y, zc), 0.0, 0.0, -0.07, 2.0, 0.2, 0.14, p_madera, semilla=1)
        for k, (x, z, alto) in enumerate(((-11, -12, 5), (8, -14, 6), (15, -9, 5), (-17, -6, 6), (3, -22, 5),
                                          (-6, -26, 6), (20, -20, 5))):
            if not libre(x, z):
                roble(qs, x + 0.5, z + 0.5, alto, semilla + k)
        pint_monte = p_monte
    elif S['suelo'] == 'nieve':
        pint_monte = p_monte_nieve
    else:
        fin = S['suelo'] == 'endstone'
        pint_monte = p_obsidiana if fin else p_roca
        # Paredes de roca alrededor (cueva o nether), o las columnas de obsidiana del End: bloques altos, lejos.
        for k in range(26):
            a = r.uniform(0, TAU)
            d = r.uniform(9, 16)
            x, z = math.cos(a) * d, math.sin(a) * d
            if math.hypot(x - ojo[0], z - ojo[2]) < 4 or libre(x, z):
                continue
            w, alto = (r.uniform(1.6, 3.0), r.uniform(6, 16)) if fin else (r.uniform(2, 5), r.uniform(3, 9))
            bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(k), -w / 2, 0.0, -w / 2, w, alto, w, pint_monte, semilla=k)
    for k in range(12):
        a = -math.pi / 2 + r.uniform(-1.4, 1.4)
        d = r.uniform(46, 60)
        x, z = math.cos(a) * d, math.sin(a) * d
        w, alto = r.uniform(10, 18), r.uniform(5, 11)
        bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(k), -w / 2, 0.0, -w / 2, w, alto, w, pint_monte, semilla=k)
    qm.dibujar(lz, cam, qs, luces, S['amb'], niebla)


def cielo(W, H, horizonte, S, luna_x=0.18):
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    if S.get('luna'):
        r = random.Random(5)
        for _ in range(int(110 * W / 1600)):
            x, yy = r.randrange(W), r.randrange(max(1, int(horizonte * 0.8)))
            g = max(1, int(W / 1600 * r.choice((1, 1, 2))))
            col[yy:yy + g, x:x + g] = np.array((0.75, 0.82, 0.95)) * r.uniform(0.35, 0.9)
        lado = int(H * 0.085)
        lx, ly = int(W * luna_x), int(min(horizonte * 0.35, H * 0.2))
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.hypot((xx - lx) / W, (yy - ly) / H * 0.62)
        col += np.array(S['luna'])[None, None, :] * (np.exp(-(d / 0.08) ** 2) * 0.2)[..., None]
        celda = max(1, lado // 8)
        for j in range(8):
            for i in range(8):
                tono = 0.92 if (i * 3 + j * 5) % 7 not in (0, 3) else 0.74
                if (i, j) in ((2, 2), (5, 4), (3, 5), (6, 1)):
                    tono = 0.66
                col[ly - lado // 2 + j * celda: ly - lado // 2 + (j + 1) * celda,
                    lx - lado // 2 + i * celda: lx - lado // 2 + (i + 1) * celda] = np.array((0.86, 0.9, 0.95)) * tono
    return np.clip(col, 0, 1)


def revelar(lz, cam, W, H, S, brillo=0.9, fuerza_vineta=0.4, motas=0, color_motas=(255, 240, 200), semilla=3):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, S)
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * brillo, radios=((2 * K, 0.5), (10 * K, 0.45), (40 * K, 0.4))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if motas:
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        r = random.Random(semilla)
        for _ in range(int(motas * W / 1600)):
            x, y = r.uniform(0, W), r.uniform(H * 0.25, H * 0.9)
            g = max(1, int(r.choice((1, 2, 2)) * W / 1600))
            d.rectangle((x, y, x + g, y + g), fill=(*color_motas, r.randint(150, 240)))
        glow = capa.filter(ImageFilter.GaussianBlur(4))
        img = Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)
    return img


def perfilar(lz, mascara, grosor, color=(1.0, 0.97, 1.0)):
    zc = np.where(mascara, lz.z, np.inf)
    for _ in range(grosor):
        e = zc.copy()
        e[1:] = np.minimum(e[1:], zc[:-1])
        e[:-1] = np.minimum(e[:-1], zc[1:])
        e[:, 1:] = np.minimum(e[:, 1:], zc[:, :-1])
        e[:, :-1] = np.minimum(e[:, :-1], zc[:, 1:])
        zc = np.where(mascara, zc, e)
    borde = ~mascara & np.isfinite(zc) & (lz.z > zc)
    lz.color[borde] = color
    lz.alfa[borde] = 1.0
    lz.emis[borde] = np.array(color) * 0.15


# ======================================================================================================================
#  El modelo del juego en la escena
# ======================================================================================================================
def quads_modelo(m, anim=None, t=0.0, M=None, extra=None, gel=False):
    """Los cuadros del modelo del juego (ya exportado), a su escala, puestos con M (en bloques). Si el mob es translúcido,
    como en el juego, en dos pasadas: lo opaco (sin el gel) y, con 'gel', solo el gel."""
    nombre = f'bestia_{m.id}' + ('_gel' if gel else '')
    tex, brillo = m._base, m._brillo
    if getattr(m, 'translucido', False):
        semi = (tex[..., 3] > 0) & (tex[..., 3] < 255)
        if gel:
            t2 = np.zeros_like(tex)
            t2[semi] = tex[semi]
            tex, brillo = t2, None
        else:
            tex = tex.copy()
            tex[semi, 3] = 0
    qm._reg(nombre, tex, brillo, estira=True)
    a = m.anims[anim] if isinstance(anim, str) else anim
    ex = [(m.anims[e], tt) if isinstance(e, str) else (e, tt) for e, tt in (extra or [])]
    if 'siempre' in m.anims and not any(x[0] is m.anims['siempre'] for x in ex) and a is not m.anims.get('siempre'):
        ex.append((m.anims['siempre'], t if a is None else 0.4))
    qs = m.quads(nombre, a, t, ex)
    k = m.escala
    S = np.diag([k, k, k, 1.0])
    return qm.transformar(qs, (M if M is not None else np.eye(4)) @ S)


def dibujar(lz, cam, qs, luces, amb, niebla):
    qm.dibujar(lz, cam, qs, luces, amb, niebla, 1.4)


def dibujar_gel(lz, cam, qs, luces, amb, niebla, cuanto=0.62):
    """Lo translúcido (el gel), después de lo opaco y de atrás adelante: se mezcla con lo que hay detrás."""
    ojo = np.asarray(cam.ojo, float)
    for P, UV, mat in sorted(qs, key=lambda q: -float(np.linalg.norm(np.mean(q[0], axis=0) - ojo))):
        luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], qm.MAT[mat], luz, None, niebla,
                         translucido=cuanto)


def escena(modelos, sitio='noche', ojo=(1.75, 0.6, 3.0), objetivo=(0.0, 0.8, 0.0), fov=48, W=1600, H=1000,
           jugador=None, luces_extra=(), brillo=0.9, motas=18, color_motas=(255, 240, 200), libre=None,
           contorno=True):
    """Una foto: el sitio, los modelos (cada uno: (m, anim, t, M)), el jugador de escala (x, z, guiñada) si se pide,
    el contorno blanco y el revelado."""
    W, H = int(W * K), int(H * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = SITIOS[sitio]
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara(ojo, objetivo, fov, W * SS, H * SS)
    luces = list(S['luces']) + list(luces_extra)
    centros = []
    lista, geles = [], []
    for (m, anim, t, M) in modelos:
        M = M if M is not None else np.eye(4)
        lista.append(quads_modelo(m, anim, t, M))
        if getattr(m, 'translucido', False):
            geles.append(quads_modelo(m, anim, t, M, gel=True))
        centros.append(M[:3, 3])
    if libre is None:
        def libre(x, z):
            return any(math.hypot(x - c[0], z - c[2]) < 1.6 for c in centros) or (
                jugador is not None and math.hypot(x - jugador[0], z - jugador[1]) < 0.8)
    suelo(lz, cam, niebla, S, luces, libre)
    figura = np.zeros(lz.z.shape, bool)
    for qs in lista:
        z0 = lz.z.copy()
        dibujar(lz, cam, qs, luces, S['amb'], niebla)
        figura |= lz.z < z0
    for qs in geles:
        c0 = lz.color.copy()
        dibujar_gel(lz, cam, qs, luces, S['amb'], niebla)
        figura |= np.any(np.abs(lz.color - c0) > 1e-6, axis=-1)
    if contorno:
        perfilar(lz, figura, max(1, int(round(3 * SS * K))))
    if jugador is not None:
        x, z, g = jugador
        nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(x, z, g)), luces, S['amb'], niebla)
    return revelar(lz, cam, W, H, S, brillo=brillo, motas=motas, color_motas=color_motas)


def heroe(m, sitio, ruta, anim=None, t=0.0, luces_extra=(), alto=None, **kw):
    """El mob en plano bajo de tres cuartos (la cámara a la altura de su pecho, un poco por debajo de la cabeza)."""
    a = alto or max(0.8, m.altura() / 16.0 * m.escala)
    d = max(2.6, a * 1.55)
    ojo = (d * 0.55, a * 0.32, d * 0.95)
    obj = (0.0, a * 0.52, 0.0)
    img = escena([(m, anim, t, None)], sitio, ojo, obj, 48, luces_extra=luces_extra, **kw)
    img.convert('RGB').save(ruta, quality=92)
    print('ok', os.path.basename(ruta), flush=True)
    return img


def cabeza(m, sitio, ruta, centro, anim=None, t=0.0, luces_extra=(), dist=1.2, **kw):
    """De cerca, un poco por debajo de la cabeza (para ver dentro de la boca)."""
    c = np.asarray(centro, float)
    ojo = tuple(c + np.array((dist * 0.45, -dist * 0.12, dist)))
    img = escena([(m, anim, t, None)], sitio, ojo, tuple(c), 50, luces_extra=luces_extra, motas=6, **kw)
    img.convert('RGB').save(ruta, quality=92)
    print('ok', os.path.basename(ruta), flush=True)
    return img


def fila(modelos, sitio, ruta, luces_extra=(), separa=2.4, **kw):
    """Todos juntos en fila, con un jugador de pie al lado (para la escala)."""
    n = len(modelos)
    xs = [(k - (n - 1) / 2) * separa for k in range(n)]
    lista = []
    for (m, anim, t), x in zip(modelos, xs):
        g = 0.25 if x < 0 else (-0.25 if x > 0 else 0.0)
        lista.append((m, anim, t, vr.T(x, 0, 0) @ vr.Ry(g)))
    alto = max(max(0.8, m.altura() / 16.0 * m.escala) for m, _, _ in modelos)
    ancho = (n - 1) * separa + 3.0
    d = max(ancho * 0.95, alto * 2.2) + 1.0
    xj = xs[-1] + separa * 0.75
    img = escena(lista, sitio, (0.3, alto * 0.45, d), (0.3, alto * 0.42, 0.0), 40, W=1800, H=860,
                 jugador=(xj, 0.3, 200), luces_extra=luces_extra, **kw)
    img.convert('RGB').save(ruta, quality=92)
    print('ok', os.path.basename(ruta), flush=True)
    return img


# ======================================================================================================================
#  La ficha (local)
# ======================================================================================================================
CSS = """
:root{--tinta:#0d0b09;--hoja:#17140f;--filo:#352f26;--texto:#efe8da;--texto2:#bdb3a2;--tenue:#8c8373;
--display:'IM Fell English SC','IM Fell English',Georgia,serif;--cuerpo:'Alegreya Sans',system-ui,sans-serif;
--mono:'IBM Plex Mono',Consolas,monospace;color-scheme:dark}
body{background:var(--tinta);color:var(--texto);font-family:var(--cuerpo);font-size:17px;line-height:1.6;margin:0}
.libro{max-width:1080px;margin:0 auto;padding:0 20px 80px}
img{max-width:100%;display:block;border-radius:6px;border:1px solid var(--filo)}
p{max-width:70ch}
h1{font-family:var(--display);font-weight:400;font-size:clamp(36px,6vw,60px);line-height:1.04;margin:28px 0 6px}
h2{font-family:var(--display);font-weight:400;font-size:clamp(26px,3.4vw,36px);line-height:1.1;margin:8px 0 8px}
.eyebrow,.tipo{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--tenue)}
.tipo{display:block;margin:60px 0 0}
.lede{color:var(--texto2)}
.par{display:grid;grid-template-columns:1fr 300px;gap:14px;align-items:start;margin:12px 0 0}
.par .ref{background:var(--hoja);border:1px solid var(--filo);border-radius:8px;padding:10px}
.par .ref p{font-size:14px;color:var(--tenue);margin:6px 0 0}
@media (max-width:760px){.par{grid-template-columns:1fr}}
.dos{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0 0}
@media (max-width:760px){.dos{grid-template-columns:1fr}}
ul{color:var(--texto2)} li b{color:var(--texto);font-weight:500}
"""


def ficha(ruta, titulo, subtitulo, secciones, fila_img=None):
    """La página de la ficha: secciones = [(nombre, original, texto, [lineas], heroe, cabeza, referencia)]."""
    e = html.escape
    partes = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              f'<title>{e(titulo)}</title>',
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=IM+Fell+English&family=Alegreya+Sans:wght@400;500;700&family=IBM+Plex+Mono&display=swap">',
              f'<style>{CSS}</style><div class="libro">',
              f'<p class="eyebrow">Bestiario de Atalaya · rediseños del DEDsafío</p><h1>{e(titulo)}</h1>',
              f'<p class="lede">{subtitulo}</p>']
    for im in ([fila_img] if isinstance(fila_img, str) else (fila_img or [])):
        partes.append(f'<img src="{e(im)}" alt="Los mobs de esta ficha juntos, con un jugador al lado" style="margin:0 0 12px">')
    for (nombre, original, texto, lineas, heroe_img, cabeza_img, ref) in secciones:
        partes.append(f'<span class="tipo">Antes: {e(original)}</span><h2>{e(nombre)}</h2><p class="lede">{texto}</p>')
        partes.append('<div class="par">')
        partes.append(f'<img src="{e(heroe_img)}" alt="{e(nombre)}, de cuerpo entero">')
        if ref:
            partes.append(f'<div class="ref"><img src="{e(ref)}" alt="El original del DEDsafío">'
                          f'<p>El original del DEDsafío (cartel oficial), como referencia.</p></div>')
        partes.append('</div>')
        if cabeza_img:
            partes.append(f'<div class="dos"><img src="{e(cabeza_img)}" alt="La cabeza de {e(nombre)}, de cerca">'
                          f'<div><ul>{"".join(f"<li>{l}</li>" for l in lineas)}</ul></div></div>')
        else:
            partes.append(f'<ul>{"".join(f"<li>{l}</li>" for l in lineas)}</ul>')
    partes.append('</div>')
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(partes))
    print('ok ficha', ruta)
