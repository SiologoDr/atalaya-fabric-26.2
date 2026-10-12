"""
Bocetos de cuatro jefes (ficha de diseno, 12-10-2026). Juan no quiso Boreala,
Nocturna ni Duneara: «lo llevas a algo muy exagerado; vuelve a revisar a
Espinara y Ofidia, y revisa los otros jefes de Dedsafio 4».

Lo que tienen los de Dedsafio 4 (Qumara, el Gran Observalador, Ofidia) y estos
copian en el modo, no en el dibujo:
  - un monstruo que se entiende al momento (planta, bestia, sierpe), mezcla de
    dos o tres bichos y nada cosmico;
  - una cabeza grande con una boca enorme: dientes blancos y, a menudo, luz
    dentro. Es el foco;
  - pocas piezas y gordas, como un modelo de Minecraft de verdad, con la textura
    pintada por cara a pixel grande (8 por bloque) y una paleta corta;
  - de 7 a 13 bloques de alto, no mas.

  A  Yelmora, la Bestia del Glaciar   HIELO
     bruto de pelo blanco + colmillos de morsa + un glaciar que le crece en el
     lomo, con los huesos de lo que cazo congelados dentro
  B  Cienara, la Reina del Fango       PANTANO
     sapo + caiman, ancha y baja; boca de lado a lado y un saco en la garganta
     que brilla verde; en el lomo le crece la cienaga
  C  Osaria, la Carronera              CARRONA
     buitre + chacal; alas de plumas rotas, pico con dientes y el pecho abierto,
     con brasas entre las costillas
  D  Geodra, la Topa de Amatista       CRISTAL
     topo + armadillo; bandas de coraza con drusas de amatista, palas de cavar y
     una nariz de estrella

Cada caja lleva sus seis caras pintadas a su medida por un «pintor» (pelo,
hielo, verrugas, plumas, coraza...), con la luz arriba y la sombra abajo como en
una textura de entidad. Todo dibujado aqui; nada de vanilla.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm

TAU = math.tau
D = vr.D2R
PPB = 8                      # pixeles de textura por bloque
punto = qm.punto


def _r(*hs):
    return [nm._hex(h) for h in hs]


# ----------------------------------------------------------------------
#  Rampas (DISENO.md: cinco tonos, el borde tenido, el nucleo sin blanco puro)
# ----------------------------------------------------------------------
PELO = _r('3a4a62', '7a90aa', 'b4c6d8', 'dce8f2', 'f2f8fc')
PELO_C = _r('6a7e98', 'a8bccf', 'd2e0ec', 'eaf2f8', 'f8fbfe')
PIEL_H = _r('141a24', '222a38', '323c4e', '465264', '5e6a7e')
HIELO = _r('1a5a88', '3a90c0', '6ac8e6', 'aeeaf8', 'e2fbff')
MARFIL = _r('6a5e46', 'a89878', 'd2c4a2', 'eae0c4', 'f8f2e0')
GARRA_H = _r('101820', '1e2a38', '2e3e52', '44586e', '627890')
BOCA_H = _r('0a1018', '14202e', '1e3246', '2a4a62', '3a6a86')

SAPO = _r('1a220c', '2e3a14', '46561e', '66782c', '8ea040')
VIENTRE = _r('5a5a30', '86864a', 'aeac6a', 'cccc8e', 'e6e4b4')
SACO = _r('1e4a0c', '3a7a14', '5eaa1e', '94d63a', 'd2f87a')
ENCIA = _r('2a0a12', '4a1420', '6e2232', '96384a', 'c25a6a')
ESCUDO = _r('16140c', '2a2616', '403a22', '585032', '766c46')
MUSGO = _r('14280c', '244414', '3a6a1e', '5a9a2a', '8ac83e')
JUNCO = _r('2a2a10', '4a4a1c', '6e6a2a', '9a9040', 'c4b862')

PLUMA = _r('140e0c', '261c18', '3a2c24', '584434', '7e6450')
CUERO = _r('1e161c', '34282e', '4c3c44', '66545c', '84727a')
HUESO = _r('4a4232', '7a6e56', 'a89a7c', 'cec2a2', 'eae0c6')
ESCAMA = _r('1a1a1e', '2e2e34', '46464e', '62626c', '84848e')

PLACA = _r('2a2620', '463e34', '62574a', '807262', 'a09080')
TOPO = _r('0c0a0a', '181414', '262020', '362e2c', '4a403c')
AMATISTA = _r('2a0e4a', '5a2a8a', '8a52c8', 'bc8aec', 'e8d2ff')
NARIZ = _r('5a1e2a', '8a3a4a', 'b85a6c', 'dc8696', 'f4b6c2')


# ----------------------------------------------------------------------
#  Ruido y ayudas de pintar
# ----------------------------------------------------------------------
def _ruido(tw, th, semilla, celda):
    """Ruido suave de valor (no hace falta que case: cada cara es suya)."""
    rng = np.random.default_rng(semilla)
    gx, gy = int(tw / celda) + 3, int(th / celda) + 3
    g = rng.random((gy, gx))
    xs, ys = np.arange(tw) / celda, np.arange(th) / celda
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x0 + 1)]
    c, d = g[np.ix_(y0 + 1, x0)], g[np.ix_(y0 + 1, x0 + 1)]
    fx, fy = fx[None, :], fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _tonos(tw, th, semilla, celda=3.0, cortes=(0.38, 0.62)):
    """Indices de rampa 1..3 sacados de dos octavas de ruido."""
    v = _ruido(tw, th, semilla, celda) * 0.7 + _ruido(tw, th, semilla + 7, max(1.0, celda / 2.6)) * 0.3
    return 1 + (v > cortes[0]).astype(int) + (v > cortes[1]).astype(int)


def _luz(idx, cara, fuerza=1):
    """La luz de una textura de entidad: arriba mas claro, abajo mas oscuro."""
    idx = idx.copy()
    if cara == 'arriba':
        idx = idx + fuerza
    elif cara == 'abajo':
        idx = idx - fuerza
    else:
        idx[0, :] += 1
        if idx.shape[0] > 3:
            idx[-1, :] -= 1
    return np.clip(idx, 0, 4)


def _imagen(idx, rampa):
    paleta = np.array([(*c, 255) for c in rampa], np.uint8)
    return paleta[np.clip(idx, 0, 4)]


def _emis(tex, mascara, alfa):
    e = np.zeros_like(tex)
    e[mascara] = tex[mascara]
    e[mascara, 3] = alfa
    return e


def _paseo(idx, rng, x, y, pasos, valor, giro=0.6):
    th, tw = idx.shape
    a = rng.uniform(0, TAU)
    for _ in range(pasos):
        if 0 <= int(y) < th and 0 <= int(x) < tw:
            idx[int(y), int(x)] = valor
        a += rng.uniform(-giro, giro)
        x += math.cos(a)
        y += math.sin(a)


# ----------------------------------------------------------------------
#  Los pintores: (ancho, alto, cara, semilla) -> (textura, emisivo o None)
# ----------------------------------------------------------------------
def p_pelo(tw, th, cara, s, rampa=PELO):
    """Pelo: mechones que caen (en los lados) y matas (arriba)."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 3.5)
    if cara in ('arriba', 'abajo'):
        for _ in range(max(1, tw * th // 10)):
            x, y = rng.randrange(tw), rng.randrange(th)
            t = rng.choice((1, 3, 3))
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                if x + dx < tw and y + dy < th:
                    idx[y + dy, x + dx] = t
    else:
        for x in range(tw):
            y = rng.randrange(-5, 1)
            while y < th:
                largo = rng.randint(2, 5)
                t = rng.choice((1, 2, 2, 3, 3))
                for k in range(largo):
                    if 0 <= y + k < th:
                        idx[y + k, x] = t if k < largo - 1 else max(0, t - 1)
                y += largo + rng.randint(0, 1)
    return _imagen(_luz(idx, cara), rampa), None


def p_pelo_claro(tw, th, cara, s):
    return p_pelo(tw, th, cara, s, PELO_C)


def p_piel(tw, th, cara, s, rampa=PIEL_H, arrugas=True):
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 2.5)
    if arrugas:
        for _ in range(max(1, tw * th // 18)):
            x, y = rng.randrange(tw), rng.randrange(th)
            for k in range(rng.randint(2, 4)):
                if x + k < tw:
                    idx[y, x + k] = 1
    return _imagen(_luz(idx, cara), rampa), None


def p_hielo(tw, th, cara, s, huesos=False):
    """Hielo de glaciar: facetas que cruzan en diagonal, grietas y un brillo frio
    (emisivo a medias). Con huesos, se ve dentro lo que se congelo."""
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 3.0) > 0.55).astype(int)
    off = rng.uniform(0, 9)
    ys, xs = np.mgrid[0:th, 0:tw]
    idx[((xs - ys * 0.75 + off) % 7.5) < 1.1] = 4
    idx[((xs + ys * 0.4 + off * 2) % 11) < 0.8] = 3
    for _ in range(max(1, tw * th // 60)):
        _paseo(idx, rng, rng.uniform(0, tw), rng.uniform(0, th), rng.randint(4, 9), 1, 0.4)
    if huesos and tw >= 8 and th >= 10:
        cx, cy = tw / 2, th * 0.42
        r = min(tw, th) * 0.22
        m = ((xs - cx) ** 2 + ((ys - cy) * 1.15) ** 2) < r * r            # el craneo
        idx[m] = 1
        idx[m & (((xs - cx + r * 0.4) ** 2 + (ys - cy) ** 2) < (r * 0.32) ** 2)] = 0   # las cuencas
        idx[m & (((xs - cx - r * 0.4) ** 2 + (ys - cy) ** 2) < (r * 0.32) ** 2)] = 0
        for k in range(4):                                                  # las costillas
            yy = int(cy + r * 1.5 + k * 2.2)
            if yy < th:
                idx[yy, int(cx - r * 1.3):int(cx + r * 1.3) + 1] = 1
        idx[int(cy + r):min(th, int(cy + r * 1.5 + 10)), int(cx)] = 1        # el espinazo
    tex = _imagen(_luz(idx, cara), HIELO)
    return tex, _emis(tex, idx >= 4, 70)


def p_hielo_huesos(tw, th, cara, s):
    return p_hielo(tw, th, cara, s, huesos=cara in ('frente', 'izq', 'der', 'atras'))


def p_marfil(tw, th, cara, s):
    """Colmillo: anillos de crecimiento a lo ancho y la punta mas oscura."""
    idx = np.full((th, tw), 3)
    ys = np.arange(th)[:, None] * np.ones((1, tw))
    idx[(ys % 3) == 0] = 2
    idx += (_ruido(tw, th, s, 2.0) > 0.7).astype(int)
    return _imagen(_luz(np.clip(idx, 1, 4), cara), MARFIL), None


def p_garra(tw, th, cara, s, rampa=GARRA_H):
    idx = np.full((th, tw), 2)
    idx[:, :max(1, tw // 3)] = 3
    idx[(_ruido(tw, th, s, 1.5) > 0.75)] = 1
    return _imagen(_luz(idx, cara), rampa), None


def p_boca(tw, th, cara, s, rampa=BOCA_H, brillo=None):
    """El fondo de la boca: oscuro, con la luz de la garganta en el centro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    d = np.hypot((xs - (tw - 1) / 2) / max(tw / 2, 1), (ys - (th - 1) / 2) / max(th / 2, 1))
    idx = np.clip(4 - (d * 3.2).astype(int), 0, 4)
    idx[(_ruido(tw, th, s, 1.5) > 0.78)] -= 1
    tex = _imagen(np.clip(idx, 0, 4), rampa)
    return tex, _emis(tex, idx >= 3, 150)


def p_ojo(tw, th, cara, s, c1='f2fdff', c2='7ae8ff'):
    t = qm._emisivo(c1, c2, max(2, tw), max(2, th))
    return t, None


def p_ojo_brasa(tw, th, cara, s):
    return qm._emisivo('fff0b0', 'ff5a10', max(2, tw), max(2, th)), None


def p_verruga(tw, th, cara, s, rampa=SAPO, pustulas=True):
    """Piel de sapo: manchas, verrugas con su brillo y alguna pustula que brilla verde."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 3.0)
    glow = np.zeros((th, tw), bool)
    for _ in range(max(1, tw * th // 22)):
        cx, cy, r = rng.uniform(0, tw), rng.uniform(0, th), rng.choice((1.0, 1.4, 1.9))
        pus = pustulas and rng.random() < 0.12
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if 0 <= x < tw and 0 <= y < th:
                    d = math.hypot(x - cx, y - cy)
                    if d <= r:
                        idx[y, x] = 4 if (x - cx) + (y - cy) < -r * 0.5 else 3
                        if pus:
                            glow[y, x] = True
                    elif d <= r + 0.8 and (x - cx) + (y - cy) > 0:
                        idx[y, x] = 1
    tex = _imagen(_luz(idx, cara), rampa)
    if glow.any():
        verde = np.array([(*SACO[3], 255), (*SACO[4], 255)], np.uint8)
        tex[glow] = verde[(np.indices((th, tw)).sum(0)[glow] % 2)]
        return tex, _emis(tex, glow, 200)
    return tex, None


def p_vientre(tw, th, cara, s):
    """Tripa de sapo: franjas blandas que ondulan, sin cortes rectos."""
    ys, xs = np.mgrid[0:th, 0:tw]
    v = (ys + 1.4 * np.sin(xs * 0.45 + s % 5) + _ruido(tw, th, s, 3.0) * 2.0) % 5.0
    idx = np.where(v < 1.0, 1, np.where(v < 2.6, 2, 3))
    idx[(_ruido(tw, th, s + 4, 1.3) > 0.8)] = 3
    return _imagen(_luz(idx, cara), VIENTRE), None


def p_saco(tw, th, cara, s):
    """El saco de la garganta: verde que brilla, con venas oscuras."""
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 2.5) > 0.5).astype(int)
    for _ in range(max(2, tw * th // 25)):
        _paseo(idx, rng, rng.uniform(0, tw), rng.uniform(0, th), rng.randint(5, 12), 1, 0.5)
    ys, xs = np.mgrid[0:th, 0:tw]
    idx[(np.hypot(xs - tw * 0.35, ys - th * 0.3) < min(tw, th) * 0.18)] = 4
    tex = _imagen(idx, SACO)
    return tex, _emis(tex, idx >= 2, 150)


def p_encia(tw, th, cara, s):
    idx = _tonos(tw, th, s, 2.0)
    return _imagen(_luz(idx, cara), ENCIA), None


def p_garganta(tw, th, cara, s):
    return qm._emisivo('eaffb0', '7ae81a', max(2, tw), max(2, th)), None


def p_escudo(tw, th, cara, s):
    idx = _tonos(tw, th, s, 2.0)
    if cara == 'arriba':
        idx[:, :] += 1
    idx[(_ruido(tw, th, s + 3, 1.2) > 0.8)] = 1
    return _imagen(np.clip(_luz(idx, cara), 0, 4), ESCUDO), None


def p_musgo(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.6, (0.35, 0.6))
    return _imagen(_luz(idx, cara), MUSGO), None


def p_junco(tw, th, cara, s):
    idx = np.full((th, tw), 2)
    idx[:, ::2] = 3
    return _imagen(_luz(idx, cara), JUNCO), None


def p_espadana(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.4)
    return _imagen(_luz(idx, cara), _r('2a1406', '4a2810', '6a3c1a', '8a5226', 'aa6c36')), None


def p_ojo_sapo(tw, th, cara, s):
    """Ojo de sapo: amarillo, con la pupila en raya y el canto oscuro."""
    t = np.zeros((max(2, th), max(2, tw), 4), np.uint8)
    th, tw = t.shape[:2]
    ys, xs = np.mgrid[0:th, 0:tw]
    d = np.hypot((xs - (tw - 1) / 2) / (tw / 2), (ys - (th - 1) / 2) / (th / 2))
    c = np.where(d < 0.55, 3, np.where(d < 0.85, 2, 0))
    rampa = _r('2a1a04', 'a86a0a', 'e8b020', 'ffe070', 'fff6c0')
    t[:] = _imagen(c, rampa)
    t[(abs(ys - (th - 1) / 2) < max(0.6, th * 0.09)) & (d < 0.8)] = (12, 8, 4, 255)
    return t, _emis(t, c >= 2, 120)


def p_pluma(tw, th, cara, s):
    """Plumas en filas al tresbolillo: cada una acaba en punta (una uve), con la punta
    clara, el canto oscuro y el canon en medio; alguna rota."""
    rng = random.Random(s)
    ancho, alto = 4, 6
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // alto
    u = (xs + np.where(fila % 2 == 1, 2, 0)) % ancho - (ancho - 1) / 2
    v = ys % alto
    borde = (alto - 1) - np.abs(u) * 1.2
    idx = np.where(v > borde, 0, np.where(v > borde - 1.6, 3, np.where(np.abs(u) < 0.6, 2, 1)))
    rotas = _ruido(tw, th, s, 2.0) > 0.72
    idx[rotas & (v > borde - 1.6)] = 1
    for _ in range(max(1, tw * th // 60)):
        x, y = rng.randrange(tw), rng.randrange(th)
        idx[y, x] = 3
    return _imagen(_luz(idx, cara), PLUMA), None


def p_cuero(tw, th, cara, s):
    return p_piel(tw, th, cara, s, CUERO)


def p_hueso(tw, th, cara, s):
    """Hueso viejo: grietas, poros y el polvo en lo hondo."""
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 2.5) > 0.45).astype(int)
    for _ in range(max(1, tw * th // 40)):
        _paseo(idx, rng, rng.uniform(0, tw), rng.uniform(0, th), rng.randint(3, 7), 1, 0.7)
    idx[(_ruido(tw, th, s + 9, 1.0) > 0.85)] = 1
    return _imagen(_luz(idx, cara), HUESO), None


def p_brasa(tw, th, cara, s):
    """Brasas: rojo que late y vetas amarillas (emisivo entero)."""
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 2.0) > 0.5).astype(int)
    for _ in range(max(1, tw * th // 20)):
        _paseo(idx, rng, rng.uniform(0, tw), rng.uniform(0, th), rng.randint(3, 6), 4, 0.6)
    idx[(_ruido(tw, th, s + 5, 1.2) > 0.82)] = 0
    tex = _imagen(idx, _r('2a0804', '7a1a08', 'd2480e', 'ff8a1e', 'ffd870'))
    return tex, _emis(tex, idx >= 2, 230)


def p_escama(tw, th, cara, s):
    idx = np.full((th, tw), 2)
    ys, xs = np.mgrid[0:th, 0:tw]
    idx[((xs + (ys // 2) % 2) % 3) == 0] = 1
    idx[(ys % 2 == 0) & ((xs + (ys // 2) % 2) % 3 == 1)] = 3
    return _imagen(_luz(idx, cara), ESCAMA), None


def p_garra_ave(tw, th, cara, s):
    return p_garra(tw, th, cara, s, _r('0c0a08', '1c1814', '2e2822', '443c32', '5e5446'))


def p_placa(tw, th, cara, s):
    """Coraza de topa: queratina en lineas de crecimiento, picada, con el canto claro."""
    rng = random.Random(s)
    idx = _tonos(tw, th, s, 3.0)
    ys = np.arange(th)[:, None] * np.ones((1, tw))
    idx[(ys % 3) == 2] -= 1
    for _ in range(max(1, tw * th // 30)):
        x, y = rng.randrange(tw), rng.randrange(th)
        idx[y, x] = 0
    return _imagen(np.clip(_luz(idx, cara), 0, 4), PLACA), None


def p_amatista(tw, th, cara, s):
    rng = random.Random(s)
    idx = 2 + (_ruido(tw, th, s, 2.5) > 0.5).astype(int)
    off = rng.uniform(0, 7)
    ys, xs = np.mgrid[0:th, 0:tw]
    idx[((xs + ys * 0.6 + off) % 6) < 1.0] = 4
    idx[((xs - ys * 0.9 + off) % 8) < 0.8] = 1
    tex = _imagen(_luz(idx, cara), AMATISTA)
    return tex, _emis(tex, idx >= 3, 120)


def p_topo(tw, th, cara, s):
    return p_pelo(tw, th, cara, s, TOPO)


def p_nariz(tw, th, cara, s):
    idx = _tonos(tw, th, s, 1.5)
    return _imagen(_luz(idx, cara), NARIZ), None


def p_garra_topo(tw, th, cara, s):
    return p_garra(tw, th, cara, s, _r('0a0806', '1a1612', '2c2620', '443a30', '605244'))


def p_boca_cristal(tw, th, cara, s):
    return p_boca(tw, th, cara, s, _r('0e0618', '20102e', '3a1e56', '6a3c9a', 'b48aee'))


def p_boca_brasa(tw, th, cara, s):
    return p_boca(tw, th, cara, s, _r('0e0404', '2a0a06', '5a1a0a', 'b24a14', 'ffa040'))


def p_diente(tw, th, cara, s):
    idx = np.full((th, tw), 3)
    idx[-1:, :] = 2
    idx[:, :1] = 4
    return _imagen(idx, _r('5a5444', '9a927c', 'd6cfba', 'ece6d6', 'faf6ec')), None


PLENOS = {p_ojo, p_ojo_brasa, p_garganta}


# ----------------------------------------------------------------------
#  La caja con sus caras pintadas a medida
# ----------------------------------------------------------------------
_CACHE = {}
_n = [0]
_NUM_CARA = {'frente': 1, 'atras': 2, 'der': 3, 'izq': 4, 'arriba': 5, 'abajo': 6}


def _material(pintor, cara, fw, fh, semilla):
    tw, th = max(1, int(round(fw * PPB))), max(1, int(round(fh * PPB)))
    clave = (pintor.__name__, cara, tw, th, semilla % 7)
    if clave not in _CACHE:
        tex, emis = pintor(tw, th, cara, semilla % 7 * 131 + tw * 7 + th)
        _n[0] += 1
        nombre = 'bst%05d' % _n[0]
        qm._reg(nombre, tex, emis, pleno=pintor in PLENOS, estira=True)
        _CACHE[clave] = nombre
    return _CACHE[clave]


def cubo(out, M, x0, y0, z0, w, h, d, pintor, caras=None, semilla=0):
    """Una caja de modelo: cada cara con su textura a la medida (PPB pixeles por bloque).
    caras cambia el pintor de alguna cara: {'frente': p_ojo, ...}."""
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    C = {
        'frente': ([(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)], w, h),
        'atras': ([(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)], w, h),
        'der': ([(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)], d, h),
        'izq': ([(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)], d, h),
        'arriba': ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], w, d),
        'abajo': ([(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)], w, d),
    }
    uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for cara, (pts, fw, fh) in C.items():
        if fw <= 0 or fh <= 0:
            continue
        p = (caras or {}).get(cara, pintor)
        if p is None:
            continue
        mat = _material(p, cara, fw, fh, semilla + _NUM_CARA[cara])
        out.append(([punto(M, q) for q in pts], uv, mat))


def caja_c(out, M, cx, cy, cz, w, h, d, pintor, caras=None, semilla=0):
    """Una caja centrada en (cx, cy, cz)."""
    cubo(out, M, cx - w / 2, cy - h / 2, cz - d / 2, w, h, d, pintor, caras, semilla)


def viga(out, p0, p1, ancho, alto, pintor, arriba=(0, 1, 0), extra=0.0, caras=None, semilla=0):
    """Una caja de p0 a p1 (mundo), de seccion ancho x alto."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    M = em.marco(p0, p1 - p0, up=arriba)
    cubo(out, M, -ancho / 2, -alto / 2, -extra, ancho, alto, L + 2 * extra, pintor, caras, semilla)


def redondo(out, M, y0, y1, rx, rz, pintor, n=3, caras=None, semilla=0):
    """Un cuerpo redondeado a escalones de pixel (planta x-z), de y0 a y1."""
    for i in range(n):
        a = math.radians(90 * (i + 1) / (n + 1))
        k = 1.0 / math.cos(math.radians(90 / (n + 1)))
        w, d = rx * k * math.cos(a), rz * k * math.sin(a)
        cubo(out, M, -w, y0, -d, 2 * w, y1 - y0, 2 * d, pintor, caras, semilla + i)


def cristal(out, M, r, h, pintor, semilla=0):
    """Un cristal a escalones, girado 45 grados para que se vea en rombo."""
    Mr = M @ vr.Ry(45 * D)
    cubo(out, Mr, -r, -0.2, -r, 2 * r, h * 0.62 + 0.2, 2 * r, pintor, semilla=semilla)
    cubo(out, Mr, -r * 0.62, h * 0.6, -r * 0.62, 1.24 * r, h * 0.27, 1.24 * r, pintor, semilla=semilla + 1)
    cubo(out, Mr, -r * 0.28, h * 0.85, -r * 0.28, 0.56 * r, h * 0.15, 0.56 * r, pintor, semilla=semilla + 2)


def pua(out, M, r, h, pintor, semilla=0):
    """Una pua o un diente de tres escalones a lo largo de la y local."""
    cubo(out, M, -r, 0, -r, 2 * r, h * 0.5, 2 * r, pintor, semilla=semilla)
    cubo(out, M, -r * 0.65, h * 0.48, -r * 0.65, 1.3 * r, h * 0.32, 1.3 * r, pintor, semilla=semilla + 1)
    cubo(out, M, -r * 0.3, h * 0.78, -r * 0.3, 0.6 * r, h * 0.22, 0.6 * r, pintor, semilla=semilla + 2)


def garra(out, p0, dir1, dir2, l1, l2, g, pintor, semilla=0):
    """Una garra curva: dos tramos que se doblan hacia abajo."""
    p0 = np.asarray(p0, float)
    d1 = np.asarray(dir1, float)
    d1 /= np.linalg.norm(d1)
    p1 = p0 + d1 * l1
    viga(out, p0, p1, g, g, pintor, semilla=semilla)
    d2 = np.asarray(dir2, float)
    d2 /= np.linalg.norm(d2)
    viga(out, p1 - d1 * 0.05, p1 + d2 * l2, g * 0.7, g * 0.7, pintor, semilla=semilla + 1)


def dientes(out, M, x0, x1, y, z, n, alto, abajo=True, ancho=0.2, semilla=0):
    """Una fila de dientes de x0 a x1 (en el marco M), hacia abajo o hacia arriba."""
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n
        h = alto * (0.75 + 0.5 * ((k * 7 + semilla) % 3) / 2)
        if abajo:
            pua(out, M @ vr.T(x, y, z) @ vr.Rx(180 * D), ancho / 2, h, p_diente, semilla + k)
        else:
            pua(out, M @ vr.T(x, y, z), ancho / 2, h, p_diente, semilla + k)


# ======================================================================
#  A · YELMORA, la Bestia del Glaciar (hielo)
# ======================================================================
def yelmora(boca=36.0, semilla=1):
    out = []
    rng = random.Random(semilla)
    # piernas cortas y gordas
    for s in (1, -1):
        Mm = vr.T(s * 1.9, 4.4, -0.2) @ vr.Rx(-12 * D)
        cubo(out, Mm, -1.15, -2.5, -1.2, 2.3, 2.7, 2.4, p_pelo, semilla=1)
        Mr = vr.T(s * 1.9, 2.1, 0.4) @ vr.Rx(10 * D)
        cubo(out, Mr, -1.0, -2.0, -1.0, 2.0, 2.3, 2.0, p_pelo, semilla=2)
        cubo(out, vr.T(s * 1.9, 0, 0.8), -1.2, 0, -1.2, 2.4, 0.8, 2.9, p_piel, semilla=3)
        for k in (-0.7, 0.0, 0.7):
            garra(out, (s * 1.9 + k, 0.4, 2.4), (0, -0.2, 1), (0, -1, 0.4), 0.45, 0.35, 0.3, p_garra, semilla=4)
    # el cuerpo: caderas y el pecho echado hacia delante
    cubo(out, vr.T(0, 4.1, -0.2), -2.7, 0, -2.0, 5.4, 2.9, 4.0, p_pelo, semilla=5)
    Mt = vr.T(0, 6.6, 0.0) @ vr.Rx(18 * D)
    cubo(out, Mt, -3.3, 0, -2.3, 6.6, 3.7, 4.6, p_pelo, semilla=6)
    cubo(out, Mt, -2.3, 0.4, 2.3, 4.6, 2.8, 0.25, p_pelo_claro, semilla=7)
    for s in (1, -1):
        cubo(out, Mt, s * 2.2 - 1.4, 3.3, -1.9, 2.8, 1.3, 3.6, p_pelo, semilla=8)
    # el glaciar del lomo: una costra y los cristales, y en el grande, los huesos de lo que cazo
    Mg = Mt @ vr.T(0, 3.7, -1.1)
    cubo(out, Mg, -2.7, -0.4, -1.6, 5.4, 0.9, 2.9, p_hielo, semilla=9)
    for (x, z, h, r, ix, iz, pin) in ((0.0, -0.4, 4.4, 0.95, -14, 0, p_hielo_huesos), (-1.7, 0.0, 2.8, 0.62, -8, 24, p_hielo),
                                      (1.8, -0.2, 3.1, 0.66, -10, -20, p_hielo), (-0.9, 0.9, 1.9, 0.45, 12, 14, p_hielo),
                                      (1.1, 0.9, 2.1, 0.46, 10, -16, p_hielo), (-2.4, -0.9, 1.7, 0.42, -24, 34, p_hielo),
                                      (2.5, -1.0, 2.0, 0.48, -26, -30, p_hielo), (0.3, -1.4, 2.5, 0.55, -36, 6, p_hielo)):
        cristal(out, Mg @ vr.T(x, 0.2, z) @ vr.Rz(iz * D) @ vr.Rx(ix * D), r, h, pin, semilla=10)
    # la cabeza: baja, adelantada, de morsa
    Mh = Mt @ vr.T(0, 2.2, 2.6) @ vr.Rx(-14 * D) @ np.diag([1.25, 1.25, 1.25, 1.0])
    cubo(out, Mh, -1.7, -0.9, -1.2, 3.4, 2.6, 2.9, p_pelo, semilla=11)
    cubo(out, Mh, -1.85, 1.0, 0.9, 3.7, 0.65, 0.9, p_pelo_claro, semilla=12)                 # la ceja de escarcha
    for s in (1, -1):
        cubo(out, Mh, s * 0.85 - 0.25, 0.55, 1.68, 0.5, 0.32, 0.06, p_ojo, semilla=13)       # los ojos
        cubo(out, Mh @ vr.T(s * 1.7, 1.2, -0.3) @ vr.Rz(-s * 20 * D), -0.3, 0, -0.25, 0.6, 0.8, 0.5, p_pelo, semilla=14)
    cubo(out, Mh, -1.35, -0.75, 1.65, 2.7, 1.25, 1.55, p_piel, caras={'abajo': p_boca}, semilla=15)    # el morro
    cubo(out, Mh, -0.6, -0.25, 3.18, 1.2, 0.5, 0.06, p_piel, semilla=16)                      # la nariz
    Mj = Mh @ vr.T(0, -0.75, 1.0) @ vr.Rx((boca + 6) * D)                                    # la mandibula
    cubo(out, Mj, -1.25, -0.75, -0.2, 2.5, 0.75, 2.2, p_piel, caras={'arriba': p_boca}, semilla=17)
    cubo(out, Mh, -1.15, -1.0, 0.0, 2.3, 0.2, 1.7, p_boca, semilla=18)                        # el fondo, que brilla
    dientes(out, Mh, -1.1, 1.1, -0.75, 3.0, 6, 0.4, abajo=True, semilla=19)
    dientes(out, Mj, -1.0, 1.0, 0.0, 1.8, 5, 0.32, abajo=False, semilla=20)
    for s in (1, -1):                                                                          # los colmillos de morsa
        p0 = punto(Mh, (s * 1.05, -0.55, 2.6))
        p1 = punto(Mh, (s * 1.3, -2.6, 3.5))
        p2 = punto(Mh, (s * 1.75, -3.7, 2.8))
        viga(out, p0, p1, 0.5, 0.5, p_marfil, semilla=21)
        viga(out, p1, p2, 0.42, 0.42, p_marfil, semilla=22)
    for k, x in enumerate((-0.7, 0.0, 0.75)):                                                 # carambanos de la barba
        cristal(out, Mj @ vr.T(x, -0.75, 1.0 + k * 0.3) @ vr.Rx(180 * D), 0.14, 0.7 + k * 0.2, p_hielo, semilla=23)
    # los brazos: uno en alto, rugiendo; el otro colgando hasta el suelo. Antebrazos dentro del hielo
    hombro = {s: punto(Mt, (s * 3.5, 3.0, 0.4)) for s in (1, -1)}
    brazos = {s: (np.array((s * 5.9, 8.4, 1.4)), np.array((s * 7.0, 5.9, 3.2))) for s in (1, -1)}
    for s in (1, -1):
        codo, muneca = brazos[s]
        viga(out, hombro[s], codo, 2.0, 2.0, p_pelo, extra=0.3, semilla=24)
        viga(out, codo, muneca, 2.3, 2.3, p_pelo, extra=0.2, semilla=25)
        dirb = (muneca - codo) / np.linalg.norm(muneca - codo)
        for k in range(4):
            p = codo + (muneca - codo) * (0.15 + k * 0.22)
            M = em.marco(p, dirb, up=(s * 0.6, 1, 0)) @ vr.Rz((k * 50 - 60) * D) @ vr.T(0, 1.0, 0) @ vr.Rx(-30 * D)
            cristal(out, M, 0.32, 1.2 + 0.35 * (k % 2), p_hielo, semilla=26)
        Mmano = em.marco(muneca, dirb)
        cubo(out, Mmano, -1.25, -1.2, 0.0, 2.5, 2.4, 1.3, p_piel, semilla=27)
        for k in (-0.8, 0.0, 0.8):
            garra(out, punto(Mmano, (k, 0.4, 1.2)), punto(Mmano, (k, 0.4, 2.2)) - punto(Mmano, (k, 0.4, 1.2)),
                  punto(Mmano, (k, -0.8, 2.4)) - punto(Mmano, (k, 0.4, 2.0)), 0.7, 0.6, 0.34, p_garra, semilla=28)
    return out, {}


# ======================================================================
#  B · CIENARA, la Reina del Fango (pantano)
# ======================================================================
def cienara(boca=40.0, semilla=2):
    out = []
    rng = random.Random(semilla)
    Mc = vr.T(0, 0, -0.5)
    # el cuerpo: ancho, bajo y redondeado a escalones; la tripa clara
    redondo(out, Mc, 0.9, 3.3, 4.4, 4.6, p_verruga, n=3, caras={'abajo': p_vientre}, semilla=1)
    redondo(out, Mc, 3.3, 4.4, 3.6, 3.9, p_verruga, n=3, semilla=2)
    redondo(out, Mc, 4.4, 4.9, 2.4, 2.7, p_verruga, n=2, semilla=3)
    # el lomo: escudos de caiman, musgo, y un poco de cienaga con sus juncos
    for s in (1, -1):
        for k in range(6):
            z = -3.2 + k * 1.15
            y = 4.4 if abs(z) < 2.6 else 3.6
            caja_c(out, Mc, s * 1.25, y + 0.2, z, 0.75, 0.5, 0.85, p_escudo, semilla=4 + k)
    for (x, z, w, d) in ((-1.9, -1.2, 1.6, 1.3), (1.6, 0.6, 1.3, 1.6), (0.3, -2.6, 1.8, 1.2), (-0.6, 1.8, 1.2, 1.0), (2.4, -2.2, 1.0, 1.2)):
        caja_c(out, Mc, x, 4.6 if abs(z) < 2.4 else 4.0, z, w, 0.35, d, p_musgo, semilla=10)
    for (x, z, h) in ((0.9, -2.9, 2.4), (1.3, -2.5, 1.9), (0.5, -2.3, 2.8), (1.6, -3.1, 1.6), (-2.2, -0.6, 1.8)):
        base = 4.2
        caja_c(out, Mc @ vr.T(x, base, z) @ vr.Rz(rng.uniform(-8, 8) * D), 0, h / 2, 0, 0.14, h, 0.14, p_junco, semilla=11)
        caja_c(out, Mc @ vr.T(x, base, z) @ vr.Rz(rng.uniform(-8, 8) * D), 0, h * 0.82, 0, 0.3, h * 0.28, 0.3, p_espadana, semilla=12)
    # la cabeza: plana y ancha como la de un caiman, con la boca de lado a lado
    Mh = vr.T(0, 2.5, 3.6) @ vr.Rx(-14 * D)
    cubo(out, Mh, -3.4, 0.0, -0.6, 6.8, 1.6, 4.4, p_verruga, caras={'abajo': p_encia}, semilla=13)
    cubo(out, Mh, -3.0, 0.0, 3.8, 6.0, 1.3, 0.9, p_verruga, caras={'abajo': p_encia}, semilla=14)
    for s in (1, -1):                                                         # los ojos, en torreta
        cubo(out, Mh, s * 2.2 - 0.75, 1.5, 0.4, 1.5, 1.2, 1.5, p_verruga, semilla=15)
        cubo(out, Mh, s * 2.2 - 0.55, 1.75, 1.9, 1.1, 0.8, 0.06, p_ojo_sapo, semilla=16)
        cubo(out, Mh, s * 2.2 - 0.85, 2.55, 0.3, 1.7, 0.35, 1.75, p_verruga, semilla=17)   # el parpado
        cubo(out, Mh, s * 1.2 - 0.3, 1.25, 4.3, 0.6, 0.25, 0.4, p_verruga, semilla=18)      # las narices
    dientes(out, Mh, -3.1, 3.1, 0.0, 4.5, 11, 0.55, abajo=True, semilla=19)
    for s in (1, -1):
        for k in range(5):
            pua(out, Mh @ vr.T(s * 3.25, 0.0, 0.2 + k * 0.8) @ vr.Rx(180 * D), 0.1, 0.5, p_diente, semilla=20 + k)
    Mj = Mh @ vr.T(0, 0.0, -0.3) @ vr.Rx(boca * D)                           # la mandibula, abierta de par en par
    cubo(out, Mj, -3.3, -1.1, -0.3, 6.6, 1.1, 5.2, p_verruga, caras={'arriba': p_encia, 'abajo': p_vientre}, semilla=21)
    cubo(out, Mj, -1.0, 0.0, 1.4, 2.0, 0.35, 2.4, p_encia, semilla=22)          # la lengua
    dientes(out, Mj, -3.0, 3.0, 0.0, 4.7, 10, 0.5, abajo=False, semilla=23)
    for s in (1, -1):
        for k in range(5):
            pua(out, Mj @ vr.T(s * 3.15, 0.0, 0.4 + k * 0.85), 0.1, 0.45, p_diente, semilla=24 + k)
    cubo(out, Mh, -2.2, -1.6, -0.45, 4.4, 1.7, 0.3, p_garganta, semilla=25)   # el fondo de la garganta
    # el saco de la garganta, que brilla verde
    Ms = vr.T(0, 2.0, 3.0)
    redondo(out, Ms, -1.9, 0.2, 2.5, 1.9, p_saco, n=3, semilla=26)
    redondo(out, Ms, -2.4, -1.9, 1.6, 1.2, p_saco, n=2, semilla=27)
    # las patas: las de delante abiertas como las de un sapo, las de atras dobladas
    for s in (1, -1):
        hom, codo, mun = np.array((s * 3.9, 2.4, 2.4)), np.array((s * 5.7, 2.0, 3.0)), np.array((s * 5.6, 0.35, 3.6))
        viga(out, hom, codo, 1.4, 1.4, p_verruga, extra=0.2, semilla=28)
        viga(out, codo, mun, 1.2, 1.2, p_verruga, extra=0.2, semilla=29)
        cubo(out, vr.T(*mun), -1.1, -0.35, -0.6, 2.2, 0.35, 2.2, p_verruga, semilla=30)
        for k in (-0.75, 0.0, 0.75):
            garra(out, mun + np.array((k, -0.15, 1.5)), (0, 0, 1), (0, -1, 0.5), 0.35, 0.3, 0.22, p_garra, semilla=31)
        cad, rod, tob = np.array((s * 3.6, 2.6, -3.2)), np.array((s * 5.4, 2.4, -1.6)), np.array((s * 5.0, 0.4, -3.4))
        viga(out, cad, rod, 2.0, 2.2, p_verruga, extra=0.3, semilla=32)
        viga(out, rod, tob, 1.4, 1.4, p_verruga, extra=0.2, semilla=33)
        cubo(out, vr.T(*tob), -1.2, -0.4, -0.6, 2.4, 0.4, 2.8, p_verruga, semilla=34)
    # la cola de caiman, corta y gorda, con su cresta
    cola = [np.array((0, 2.2, -4.6)), np.array((0, 1.8, -6.8)), np.array((0.4, 1.3, -8.8)), np.array((1.1, 0.8, -10.4))]
    for k, (anc, alt) in enumerate(((2.6, 1.7), (1.9, 1.3), (1.2, 0.9))):
        viga(out, cola[k], cola[k + 1], anc, alt, p_verruga, extra=0.25, semilla=35 + k)
        M = em.marco(cola[k], cola[k + 1] - cola[k])
        for j in range(2):
            caja_c(out, M, 0, alt / 2 + 0.15, 0.6 + j * 0.9, 0.35, 0.45, 0.6, p_escudo, semilla=38)
    return out, {}


# ======================================================================
#  C · OSARIA, la Carronera (carrona)
# ======================================================================
def osaria(abre=28.0, semilla=3):
    out = []
    rng = random.Random(semilla)
    # patas de ave: muslo con plumas, canilla desnuda con escamas y garras
    for s in (1, -1):
        cad, rod, tob, pie = (np.array((s * 1.3, 5.2, -0.6)), np.array((s * 1.5, 3.7, 0.9)), np.array((s * 1.5, 1.3, -0.5)),
                              np.array((s * 1.5, 0.3, 0.1)))
        viga(out, cad, rod, 1.5, 1.6, p_pluma, extra=0.3, semilla=1)
        viga(out, rod, tob, 0.65, 0.65, p_escama, extra=0.1, semilla=2)
        viga(out, tob, pie, 0.55, 0.55, p_escama, semilla=3)
        for k in (-0.45, 0.0, 0.45):
            garra(out, pie + np.array((k, 0, 0.1)), (k * 0.6, -0.1, 1), (0, -1, 0.3), 0.8, 0.45, 0.22, p_garra_ave, semilla=4)
        garra(out, pie, (0, 0, -1), (0, -1, -0.2), 0.5, 0.3, 0.2, p_garra_ave, semilla=5)
    # el cuerpo encorvado: cuero gris y el pecho abierto, con brasas entre las costillas
    Mt = vr.T(0, 5.0, -0.4) @ vr.Rx(38 * D)
    cubo(out, Mt, -1.8, 0, -1.4, 3.6, 4.4, 2.8, p_cuero, caras={'frente': None}, semilla=6)
    cubo(out, Mt, -1.5, 0.4, 0.4, 3.0, 3.6, 0.3, p_brasa, semilla=7)
    for k in range(5):
        y = 0.8 + k * 0.7
        for s in (1, -1):
            viga(out, punto(Mt, (s * 0.25, y + 0.3, 1.45)), punto(Mt, (s * 1.65, y, 1.2)), 0.26, 0.26, p_hueso, semilla=8)
            viga(out, punto(Mt, (s * 1.65, y, 1.2)), punto(Mt, (s * 1.8, y - 0.3, 0.0)), 0.24, 0.24, p_hueso, semilla=9)
    viga(out, punto(Mt, (0, 0.4, 1.5)), punto(Mt, (0, 4.2, 1.5)), 0.4, 0.3, p_hueso, semilla=10)       # el esternon
    for k in range(4):                                                                       # las vertebras del lomo
        caja_c(out, Mt, 0, 0.8 + k * 1.0, -1.6, 0.5, 0.5, 0.6, p_hueso, semilla=11)
    # la gorguera de plumas y el manto que le cae por la espalda
    Mn = Mt @ vr.T(0, 4.3, 0.2)
    for k in range(14):
        a = k * TAU / 14
        M = Mn @ vr.Ry(a) @ vr.T(0, 0, 1.2) @ vr.Rx(-58 * D)
        cubo(out, M, -0.32, -0.2, -0.08, 0.64, 2.0 + 0.6 * (k % 2), 0.16, p_pluma, semilla=12)
    for fila in range(3):
        for k in range(5):
            x = -1.6 + k * 0.8
            M = Mt @ vr.T(x, 4.0 - fila * 1.2, -1.5 - fila * 0.05) @ vr.Rx(180 * D) @ vr.Rx(-20 * D)
            cubo(out, M, -0.38, 0, -0.08, 0.76, 1.6 + rng.uniform(0, 0.9), 0.16, p_pluma, semilla=13)
    # el cuello pelado y la cabeza: craneo de buitre, pico ganchudo con dientes y ojos de brasa
    cuello = [punto(Mn, (0, 0, 0)), punto(Mn, (0, 1.3, 0.8)), punto(Mn, (0, 1.4, 2.0))]
    viga(out, cuello[0], cuello[1], 0.85, 0.85, p_cuero, extra=0.2, semilla=14)
    viga(out, cuello[1], cuello[2], 0.75, 0.75, p_cuero, extra=0.2, semilla=15)
    Mh = em.marco(cuello[2], (0, -0.35, 1.0))
    cubo(out, Mh, -0.85, -0.7, -0.7, 1.7, 1.5, 1.8, p_hueso, semilla=16)
    for s in (1, -1):
        cubo(out, Mh, s * 0.86 - 0.05, -0.2, 0.1, 0.1, 0.75, 0.85, p_garra_ave, semilla=17)         # la cuenca
        cubo(out, Mh, s * 0.9 - 0.05, -0.05, 0.28, 0.1, 0.42, 0.45, p_ojo_brasa, semilla=18)         # el ojo
        pua(out, Mh @ vr.T(s * 0.5, 0.75, -0.4) @ vr.Rx(-50 * D) @ vr.Rz(-s * 20 * D), 0.14, 0.7, p_hueso, semilla=19)
    # el pico: tres tramos que se curvan hacia abajo, con dientes de sierra
    Mp1 = Mh @ vr.T(0, 0.0, 1.05)
    cubo(out, Mp1, -0.6, -0.45, 0.0, 1.2, 0.95, 1.5, p_hueso, semilla=20)
    Mp2 = Mp1 @ vr.T(0, 0.05, 1.45) @ vr.Rx(16 * D)
    cubo(out, Mp2, -0.45, -0.4, 0.0, 0.9, 0.8, 1.2, p_hueso, semilla=21)
    Mp3 = Mp2 @ vr.T(0, 0.05, 1.15) @ vr.Rx(62 * D)
    cubo(out, Mp3, -0.32, -0.35, 0.0, 0.64, 0.7, 0.95, p_garra_ave, semilla=22)
    Mp4 = Mp3 @ vr.T(0, 0.0, 0.9) @ vr.Rx(40 * D)
    cubo(out, Mp4, -0.2, -0.25, 0.0, 0.4, 0.45, 0.5, p_garra_ave, semilla=22)
    Mpi = Mh @ vr.T(0, -0.6, 0.9) @ vr.Rx(abre * D)
    cubo(out, Mpi, -0.5, -0.35, 0.0, 1.0, 0.35, 2.0, p_hueso, caras={'arriba': p_boca_brasa}, semilla=23)
    cubo(out, Mh, -0.5, -0.65, 0.6, 1.0, 0.18, 1.6, p_boca_brasa, semilla=24)
    dientes(out, Mp1, -0.45, 0.45, -0.45, 1.0, 3, 0.28, abajo=True, ancho=0.16, semilla=25)
    dientes(out, Mp2, -0.35, 0.35, -0.4, 0.6, 3, 0.24, abajo=True, ancho=0.14, semilla=26)
    dientes(out, Mpi, -0.4, 0.4, 0.0, 1.5, 4, 0.24, abajo=False, ancho=0.14, semilla=27)
    # las alas: brazos que se abren, con plumas rotas colgando y manos de hueso
    for s in (1, -1):
        hom = punto(Mt, (s * 1.9, 3.7, 0.0))
        codo = np.array((s * 4.8, 9.9, 0.3))
        mun = np.array((s * 7.0, 8.6, 1.6))
        viga(out, hom, codo, 1.1, 1.1, p_cuero, extra=0.2, semilla=28)
        viga(out, codo, mun, 0.8, 0.8, p_hueso, extra=0.15, semilla=29)
        for k in range(4):                                                    # los dedos de hueso, ganchudos
            dir1 = np.array((s * 0.4, -0.6 - k * 0.12, 0.6 - k * 0.3))
            garra(out, mun, dir1, (s * 0.1, -1, 0.1), 1.1 + k * 0.15, 0.6, 0.2, p_hueso, semilla=30 + k)
        for k in range(13):                                                   # las plumas del ala, rotas y sueltas
            t_ = k / 12
            p = hom + (codo - hom) * (t_ / 0.55) if t_ < 0.55 else codo + (mun - codo) * ((t_ - 0.55) / 0.45)
            largo = 2.4 + 2.8 * math.sin(math.pi * min(1.0, t_ * 1.15)) + rng.uniform(-0.6, 0.6)
            if k % 4 == 3:
                largo *= 0.55                                                  # una rota
            M = vr.T(*p) @ vr.Ry(s * (8 + 14 * t_) * D) @ vr.Rx(180 * D) @ vr.Rz(s * (-12 + 30 * t_ + rng.uniform(-5, 5)) * D)
            cubo(out, M, -0.27, 0, -0.08, 0.54, largo, 0.16, p_pluma, semilla=34 + k)
    # huesos sueltos a sus pies: lo que esta limpiando
    for (x, z, giro) in ((-2.4, 2.8, 30), (2.2, 3.4, -50), (0.4, 4.2, 80)):
        viga(out, (x, 0.25, z), (x + math.cos(math.radians(giro)) * 1.8, 0.25, z + math.sin(math.radians(giro)) * 1.8), 0.32, 0.32, p_hueso,
             semilla=44)
    return out, {}


# ======================================================================
#  D · GEODRA, la Topa de Amatista (cristal)
# ======================================================================
def geodra(abre=26.0, semilla=4):
    out = []
    rng = random.Random(semilla)
    # la coraza: siete bandas como las de un armadillo, cada una un arco a escalones
    bandas = []
    for k in range(7):
        z = -5.0 + k * 1.55
        f = math.sqrt(max(0.15, 1 - ((z + 0.3) / 6.2) ** 2))
        R, H = 4.0 * f + 0.3, 4.8 * f + 0.6
        bandas.append((z, R, H))
        M = vr.T(0, 0.8, z)
        for i, (fw, fh) in enumerate(((1.0, 0.55), (0.86, 0.82), (0.6, 0.97), (0.3, 1.0))):
            cubo(out, M, -R * fw, 0, -0.85, 2 * R * fw, H * fh, 1.7, p_placa, semilla=i + k)
    # las drusas de amatista que le asoman entre banda y banda
    for k in range(1, 6):
        z, R, H = bandas[k]
        for j, (x, ang) in enumerate(((-0.9, 22), (0.5, -10), (1.5, -30), (-1.9, 38))):
            if (k + j) % 2 and j > 1:
                continue
            y = 0.8 + H * math.sqrt(max(0.05, 1 - (x / (R + 0.1)) ** 2)) - 0.3
            M = vr.T(x, y, z - 0.78) @ vr.Rz(ang * D) @ vr.Rx(rng.uniform(-15, 15) * D)
            cristal(out, M, rng.uniform(0.45, 0.72), rng.uniform(2.0, 3.4), p_amatista, semilla=10 + j)
    # la cabeza: casco de coraza, hocico largo y la nariz de estrella
    Mh = vr.T(0, 2.0, 5.3) @ vr.Rx(-2 * D) @ np.diag([1.3, 1.3, 1.3, 1.0])
    cubo(out, Mh, -1.6, -0.6, -0.8, 3.2, 2.5, 2.4, p_topo, caras={'arriba': p_placa}, semilla=20)
    cubo(out, Mh, -1.75, 1.4, -0.9, 3.5, 0.6, 2.0, p_placa, semilla=21)                 # el casco
    cubo(out, Mh, -1.15, -0.3, 1.5, 2.3, 1.6, 1.4, p_topo, caras={'abajo': p_encia}, semilla=22)
    cubo(out, Mh, -0.8, -0.15, 2.8, 1.6, 1.2, 1.2, p_topo, caras={'abajo': p_encia}, semilla=23)
    for s in (1, -1):
        cubo(out, Mh, s * 1.0 - 0.15, 0.85, 1.55, 0.3, 0.22, 0.06, p_ojo, semilla=24)       # ojillos
    Mn = Mh @ vr.T(0, 0.45, 4.0)                                                       # la estrella de la nariz
    cubo(out, Mn, -0.45, -0.45, -0.1, 0.9, 0.9, 0.3, p_nariz, semilla=25)
    for k in range(11):
        a = k * TAU / 11 + 0.15
        M = Mn @ vr.Rz(a) @ vr.T(0, 0.35, 0.08)
        cubo(out, M, -0.1, 0, -0.1, 0.2, 0.75 + 0.15 * (k % 2), 0.2, p_nariz, semilla=26)
    Mj = Mh @ vr.T(0, -0.3, 0.6) @ vr.Rx(abre * D)                                    # la boca, con dientes de cristal
    cubo(out, Mj, -1.05, -0.55, 0.0, 2.1, 0.55, 3.0, p_topo, caras={'arriba': p_boca_cristal}, semilla=27)
    cubo(out, Mh, -0.95, -0.55, 0.9, 1.9, 0.2, 2.6, p_boca_cristal, semilla=28)
    for k in range(4):
        cristal(out, Mh @ vr.T(-0.75 + k * 0.5, -0.25, 3.4) @ vr.Rx(180 * D), 0.1, 0.45, p_amatista, semilla=29)
        cristal(out, Mj @ vr.T(-0.75 + k * 0.5, 0.0, 2.6), 0.09, 0.4, p_amatista, semilla=30)
    # las palas de cavar: brazos cortos y manos anchas con cuatro unas enormes
    for s in (1, -1):
        hom, mun = np.array((s * 3.2, 2.4, 4.4)), np.array((s * 4.0, 0.7, 5.6))
        viga(out, hom, mun, 1.6, 1.6, p_topo, extra=0.3, semilla=31)
        Mm = vr.T(*mun) @ vr.Ry(s * 18 * D)
        cubo(out, Mm, -1.3, -0.45, -0.5, 2.6, 0.8, 1.8, p_topo, semilla=32)
        for k in range(4):
            x = -0.95 + k * 0.63
            garra(out, punto(Mm, (x, 0.0, 1.2)), punto(Mm, (x, 0.0, 2.6)) - punto(Mm, (x, 0.0, 1.2)),
                  punto(Mm, (x, -1.0, 3.0)) - punto(Mm, (x, 0.0, 2.4)), 1.25, 0.7, 0.4, p_garra_topo, semilla=33 + k)
    for s in (1, -1):                                                                   # las patas de atras
        viga(out, (s * 3.0, 1.8, -3.6), (s * 3.4, 0.0, -3.2), 1.5, 1.5, p_topo, extra=0.2, semilla=37)
        for k in (-0.5, 0.0, 0.5):
            garra(out, (s * 3.4 + k, 0.1, -2.6), (0, 0, 1), (0, -1, 0.4), 0.45, 0.3, 0.24, p_garra_topo, semilla=38)
    # la cola corta, con su maza de drusa
    viga(out, (0, 1.8, -5.6), (0, 1.3, -7.6), 1.4, 1.2, p_placa, extra=0.2, semilla=39)
    viga(out, (0, 1.3, -7.6), (0, 1.0, -8.8), 1.0, 0.9, p_placa, extra=0.2, semilla=40)
    for k, (x, y, ang) in enumerate(((0, 1.4, 0), (-0.5, 1.1, 40), (0.55, 1.1, -40), (0.0, 0.7, 180), (0.2, 1.2, 70))):
        cristal(out, vr.T(x, y, -9.0) @ vr.Rz(ang * D) @ vr.Rx(-30 * D), 0.3, 1.2, p_amatista, semilla=41 + k)
    return out, {}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.3):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)
