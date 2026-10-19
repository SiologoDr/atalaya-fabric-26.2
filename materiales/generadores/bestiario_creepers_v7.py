"""
Los creepers, sexta vuelta (18-10-2026). Juan, al ver la quinta en el juego:

  «el Creeper Atómico está excelente en todo sentido, diseño y textura»  -> se queda tal cual
  el Ciego, el Marchito y la Enredadera, «un poco raros»: las orejas y las costillas (y lo demás añadido) «deberían ser
  texturas sobrepuestas como una 2.ª capa, no como está ahorita»  -> lo añadido va en una 2.ª capa (una caja algo mayor
  que la pieza, como la capa de fuera de una skin, con la textura recortada) o en láminas planas (las orejas del
  warden, las lianas, las matas), como hace vanilla
  la Tarta: «el diseño está god», pero la textura de la cabeza «muy limpia»  -> el bizcocho con poros, la mermelada y
  la nata, el glaseado con su brillo, sus gotas redondas y los fideos
  el Latido «no se parece nada a su ilustración»  -> el Creeper Visceral del cartel: la cabeza de bultos de carne con la
  orla de dientes oscuros, los bultos de los hombros, el cuerpo fino morado y las patas abiertas
  el Artillero «es igual a un creeper»  -> un shulker hecho creeper: la carne clara dentro de su concha (la tapa en la
  cabeza, el collar, las placas del cuerpo y las botas)
  Matojo, Volcánico y Gelatina, a mejorar  -> el Matojo, de bloque de pasto (los pies de tierra y la hierba que
  cuelga); el Volcánico, de bloque de magma con las crestas de llama del original; la Gelatina, con el gel trabajado
  (brillo, burbujas, canto), las babas y el charco

Después, sobre la sexta (una séptima vuelta hecha por mi cuenta la deshizo entera), lo que él dijo, tal cual: el Ciego,
las antenas del warden en vez de los «cachos»; el Matojo, a cuatro patas y solo hierba en la cabeza; la Gelatina, sin
las babas de la cara ni la cara de creeper («solo como slime»); el Latido, sin la cara de creeper ni los pinchos; el
Volcánico y el Artillero, quitados del mod. El Atómico, la Tarta, el Marchito y la Enredadera, tal cual. Luego quitó
también el Latido («quitemos el creeper de la foto») y el pulido de las texturas («está medio raro»).

Uso: python bestiario_creepers_v7.py <raíz> [carpeta de la ficha] [ids]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
import bestiario_creepers as bc
from bestiario_limpio import rampa

LADOS = bc.LADOS
PATAS = bc.PATAS


# ======================================================================================================================
#  Lo común: la 2.ª capa, lo encendido y los puntos sueltos
# ======================================================================================================================
def capa(m, parte, base, tam, pint, infla=0.8, caras=None):
    """La 2.ª capa de una pieza (como la capa de fuera de una skin): la caja que crece desde 'base' con 'tam', 'infla'
    mayor por cada lado, con la textura recortada (lo que no se pinta queda transparente)."""
    w, h, d = tam
    x, y, z = base
    m.caja_desde(parte, (x, y - infla, z), (w + 2 * infla, h + 2 * infla, d + 2 * infla), pint, caras=caras)


def recorte(rgb, a, emis=None):
    """La textura de una capa: el color donde 'a' (de 0 a 1) pasa de la mitad; lo demás, transparente."""
    tex = L._rgba(rgb)
    tex[..., 3] = np.where(a >= 0.5, 255, 0)
    if emis is not None:
        emis = emis.copy()
        emis[..., 3] = np.where(a >= 0.5, emis[..., 3], 0)
    return tex, emis


def encender(tex, a, rc, v=3.0):
    """Lo encendido encima: la rampa 'rc' (en v) donde 'a' (de 0 a 1, con el borde ya fundido). Devuelve la textura y
    su brillo (o None si no hay nada encendido)."""
    a = np.clip(a, 0.0, 1.0)
    if not (a > 0.02).any():
        return tex, None
    luz = L.color_continuo(rc, np.broadcast_to(np.asarray(v, float), a.shape))
    a3 = a[..., None]
    tex = tex.copy()
    tex[..., :3] = np.clip(np.round(tex[..., :3] * (1 - a3) + luz * a3), 0, 255)
    emis = np.zeros_like(tex)
    emis[..., :3] = np.clip(np.round(luz), 0, 255)
    emis[..., 3] = np.where(a > 0.02, np.round(a * 255), 0)
    return tex, emis


def mezclar(rgb, a, otro):
    a3 = np.clip(a, 0, 1)[..., None]
    return rgb * (1 - a3) + otro * a3


def puntos(tw, th, s, n, margen=0.5):
    """n puntos fijos (x, y, k) en la cara, de la semilla s (k, de 0 a 1, para variar el tamaño)."""
    rng = np.random.default_rng((int(s) * 7919 + 104729) % (2 ** 31))
    return [(rng.uniform(margen, max(margen + 0.01, tw - margen)), rng.uniform(margen, max(margen + 0.01, th - margen)),
             rng.random()) for _ in range(max(1, int(n)))]


def _t(tw, th, cara, franja):
    """La altura de cada fila en la pieza (de 0 arriba a 1 abajo), en las caras de lado."""
    f0, f1 = franja
    ys = np.mgrid[0:th, 0:tw][0] + 0.5
    if cara == 'arriba':
        return np.zeros((th, tw))
    if cara == 'abajo':
        return np.ones((th, tw))
    return f0 + ys / th * (f1 - f0)


# ======================================================================================================================
#  El Ciego (Creeper Warden): el creeper de sculk del original, con lo del warden en 2.ª capa
# ======================================================================================================================
SCULK = bc.SCULK
SCULK_OSC = rampa('020608', '050d11', '08151b', '0c1d25', '10262f')
CIAN = bc.CIAN
HUESO_W = rampa('7a7254', 'a89e78', 'cfc59a', 'e8dfb6', 'faf4d6')


def sculk16(franja=(0.0, 1.0), almas=False):
    """El sculk del warden, suave y con detalle: el azul petróleo que corre por la rampa, manchas grandes y blandas más
    oscuras, motitas de cian apagado y alguna encendida; con 'almas', el resplandor del pecho (detrás de las costillas)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        v = L.tono_suave(tw, th, cara, s, 1.9, 0.6, 0.1, 6.0, franja=franja)
        n = L._ruido(tw, th, s * 13 + 1, 4.0)
        v = v - np.clip((n - 0.55) / 0.15, 0, 1) * 0.9
        rgb = L.color_continuo(SCULK, v)
        a_luz = np.zeros((th, tw))
        for (px, py, k) in puntos(tw, th, s + 3, tw * th / 34):
            g = np.clip(1 - np.hypot(x - px, y - py) / (0.6 + k * 0.6), 0, 1)
            if k > 0.86:
                a_luz = np.maximum(a_luz, g)
            else:
                rgb = mezclar(rgb, g * 0.55, L.color_continuo(CIAN, np.full((th, tw), 0.8)))
        if almas and cara == 'frente':
            t = _t(tw, th, cara, franja)
            g = np.clip(1 - np.hypot((x - tw / 2) / (tw * 0.34), (t - 0.43) / 0.27), 0, 1)
            a_luz = np.maximum(a_luz, g ** 0.7 * 0.95)
        return encender(L._rgba(rgb), a_luz, CIAN, 1.3 + a_luz * 1.7)
    return fn


def zarcillo(nombre):
    """La oreja del warden (su zarcillo), plana como las suyas: un cuerno ancho que sube desde la base, se curva hacia
    fuera y enrosca la punta hacia dentro; el canto oscuro, el sculk dentro (más claro hacia la punta) y tres manchas de
    cian encendidas a lo largo (a la resolución del modelo)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        X = xs + 0.5
        Y = (th - ys - 0.5)
        sd = np.full((th, tw), 99.0)
        tpar = np.zeros((th, tw))
        n = 48
        for i in range(n + 1):
            t = i / n
            cu = 0.26 + 0.52 * math.sin(t * math.pi / 2) ** 1.4 - 0.5 * max(0.0, t - 0.78) ** 1.5
            cv = 0.04 + 0.86 * t
            w = (0.2 * (1 - t) ** 0.55 + 0.035) * tw
            d = np.hypot(X - cu * tw, Y - cv * th) - w
            mejor = d < sd
            sd = np.where(mejor, d, sd)
            tpar = np.where(mejor, t, tpar)
        dentro = sd < 0
        canto = dentro & (sd > -1.6 * min(1.0, tw / 18.0))         # (pintada a 32 por bloque, de 18 de ancho)
        val = 1.8 + tpar * 1.4 + L.tono_suave(tw, th, 'frente', s, 0.0, 0.0, 0.1, 6.0)
        rgb = L.color_continuo(SCULK, val)
        rgb[canto] = L.color_continuo(SCULK_OSC, np.full(canto.sum(), 1.5))
        g = np.zeros((th, tw))
        for t0, r0 in ((0.28, 0.5), (0.55, 0.42), (0.78, 0.32)):
            cu = 0.26 + 0.52 * math.sin(t0 * math.pi / 2) ** 1.4 - 0.5 * max(0.0, t0 - 0.78) ** 1.5
            cv = 0.04 + 0.86 * t0
            w = (0.2 * (1 - t0) ** 0.55 + 0.035) * tw
            g = np.maximum(g, np.clip(1.2 - np.hypot(X - cu * tw, Y - cv * th) / (w * r0 * 1.6), 0, 1))
        tex, emis = encender(L._rgba(rgb), np.clip(g * 1.4, 0, 1) * (dentro & ~canto), CIAN, 1.5 + g * 1.8)
        tex[..., 3] = np.where(dentro, 255, 0)
        if emis is not None:
            emis[..., 3] = np.where(dentro, emis[..., 3], 0)
        return tex, emis
    return B.Pintor(nombre, fn)


def sculk8(franja=(0.0, 1.0), almas=False, brillos=True):
    """El sculk al píxel de Minecraft: el azul petróleo, más claro arriba, con manchas oscuras, motas de cian apagado de
    un píxel y (si 'brillos') alguna encendida; con 'almas', el resplandor del pecho detrás de las costillas."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        a = _azar1(xs, ys, s)
        v = L.tono_suave(tw, th, cara, s, 1.9, 0.6, 0.05, 3.0, franja=franja)
        n = L._ruido(tw, th, s * 13 + 1, 2.5)
        v = v - (n > 0.62) * 0.8
        rgb = L.color_continuo(SCULK, v)
        mota = (a < 0.08) & (n <= 0.62)
        rgb = np.where(mota[..., None], L.color_continuo(CIAN, np.full(a.shape, 0.9)), rgb)
        a_luz = np.where((a < 0.025) & brillos, 1.0, 0.0)
        if almas and cara == 'frente':
            t = _t(tw, th, cara, franja)
            g = np.clip(1 - np.hypot((x - tw / 2) / (tw * 0.34), (t - 0.43) / 0.27), 0, 1)
            a_luz = np.maximum(a_luz, np.where(g > 0.05, 0.55 + g * 0.45, 0.0))
        return encender(L._rgba(rgb), a_luz, CIAN, 1.3 + a_luz * 1.7)
    return fn


def costillas8():
    """Las costillas al píxel de Minecraft (2.ª capa del pecho): por delante, el esternón de un píxel y cuatro
    costillas de un píxel con un píxel de hueco entre ellas (la punta, una fila más abajo); por los costados, siguen;
    por detrás, el espinazo con sus vértebras. Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = np.zeros((th, tw), bool)
        v = np.full((th, tw), 2.8)
        filas = [2 + 2 * k for k in range(4)]
        if cara == 'frente':
            c = tw // 2
            esternon = (xs == c) & (ys >= 1) & (ys <= filas[-1] + 1)
            a |= esternon
            v = np.where(esternon, 3.3, v)
            for f in filas:
                punta = (xs == 0) | (xs == tw - 1)
                rib = np.where(punta, ys == f + 1, ys == f) & (xs != c)
                a |= rib
                v = np.where(rib, np.where(punta, 2.5, 3.0), v)
        elif cara in ('izq', 'der'):
            for f in filas:
                rib = ys == f + 1
                a |= rib
                v = np.where(rib, 2.6 + (xs == tw // 2) * 0.3, v)
        elif cara == 'atras':
            c = tw // 2
            espina = (xs == c) & (ys >= 1) & (ys <= th - 2)
            vertebra = (np.abs(xs - c) == 1) & (ys % 2 == 0) & (ys >= 2) & (ys <= th - 3)
            a |= espina | vertebra
            v = np.where(espina, 3.1, np.where(vertebra, 2.6, v))
        return recorte(L.color_continuo(HUESO_W, v), a.astype(float))
    return fn


def garras8():
    """Las garras al píxel de Minecraft (2.ª capa de los pies): tres dedos de hueso de un píxel de ancho y dos de alto
    por delante, abajo (la punta, más oscura). Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = np.zeros((th, tw), bool)
        v = np.full((th, tw), 3.0)
        if cara == 'frente':
            dedo = (xs % 2 == 0) & (ys >= th - 2)
            a |= dedo
            v = np.where(ys == th - 1, 2.4, 3.2)
        return recorte(L.color_continuo(HUESO_W, v), a.astype(float))
    return fn


def antena8(nombre):
    """La antena del warden al píxel de Minecraft, dibujada a mano (7 x 6, como las de vanilla): plana, sale del lado
    de la cabeza (la raíz, a la izquierda), con el centro redondo y tres dedos romos (arriba, a la derecha y abajo),
    más claros en la punta; encendidos, el centro y el dedo de arriba."""
    dibujo = ('...sl..',
              '..ssc.l',
              '.sssssl',
              'dsscss.',
              '.dssss.',
              '...dll.')
    valor = {'d': 1.3, 's': 2.2, 'l': 3.2, 'c': 2.6}

    def fn(tw, th, cara, s):
        h, w = len(dibujo), len(dibujo[0])
        rgb = np.zeros((h, w, 3))
        a = np.zeros((h, w))
        luz = np.zeros((h, w))
        for j, fila in enumerate(dibujo):
            for i, ch in enumerate(fila):
                if ch == '.':
                    continue
                rgb[j, i] = L.color_continuo(SCULK, np.array([valor[ch]]))[0]
                a[j, i] = 1.0
                luz[j, i] = 1.0 if ch == 'c' else 0.0
        # A la medida de la cara (por si no es de 7 x 6): cada píxel del dibujo, al más cercano.
        jj = np.minimum(h - 1, (np.arange(th) * h) // max(1, th))
        ii = np.minimum(w - 1, (np.arange(tw) * w) // max(1, tw))
        rgb, a, luz = rgb[jj][:, ii], a[jj][:, ii], luz[jj][:, ii]
        tex, emis = encender(L._rgba(rgb), luz, CIAN, 2.0 + luz * 1.5)
        tex[..., 3] = np.where(a > 0, 255, 0)
        if emis is not None:
            emis[..., 3] = np.where(a > 0, emis[..., 3], 0)
        return tex, emis
    return B.Pintor(nombre, fn)


def ciego(raiz):
    m = B.Modelo('ciego', K=2, ancho=128)
    m.escala = 0.55
    piel = L.grueso('piel_ciego', sculk8())
    y_cab = bc.cuerpo(m, L.grueso('pecho_ciego', sculk8(almas=True)), piel)
    # El pecho del warden, en 2.ª capa: el esternón y las costillas de hueso (y el espinazo por detrás); entre ellas,
    # el resplandor de las almas, que está en la piel de debajo.
    m.parte('pecho', 'cuerpo', (0, 24.0, 0))
    capa(m, 'pecho', (0, 12.0, 0), (16, 24, 8), L.grueso('costillas_ciego', costillas8()), infla=0.8,
         caras={'arriba': None, 'abajo': None})
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        capa(m, p, (px, 0.0, pz), (8, 12, 8), L.grueso('garras_ciego', garras8()), infla=0.6,
             caras={'arriba': None, 'abajo': None})
    # La cabeza: la cara de creeper sin ojos, con la boca encendida de cian (la del original); las antenas del warden
    # (sus zarcillos), planas, que salen de lo alto de los lados de la cabeza hacia fuera, casi horizontales.
    y1 = bc.cabeza(m, 'ciego', 'cuerpo', y_cab, lambda fr: sculk8(fr, brillos=False), bc.HUECO_C, neon='3ad8ff',
                   sin_ojos=True)
    antena = antena8('antena_ciego')
    aw, ah = 13.0, 11.0
    for lado, ld in LADOS:
        rot = (0, 0 if lado > 0 else 180, lado * 12)
        pegado = np.array((lado * 7.4, y1 - 4.0, -0.5))
        centro = pegado - B.girar(rot)[:3, :3] @ np.array((-0.5 * aw, (0.42 - 0.5) * ah, 0.0))
        n = m.parte(f'oreja_{ld}', 'cabeza', tuple(pegado))
        m.hoja(n, tuple(centro), aw, ah, antena, rot=rot, dos_caras=False)

    def extra(s):
        for k, ld in enumerate(('i', 'd')):
            s.onda(f'oreja_{ld}', 'r', 2, 4 * (1 if ld == 'i' else -1), periodo=2.0, fase=k * 0.15)
        s.onda('pecho', 'e', 0, 0.025, base=1.0, periodo=3.0)
        s.onda('pecho', 'e', 2, 0.04, base=1.0, periodo=3.0)

    def mecha(h):
        for ld, sg in (('i', 1), ('d', -1)):
            h.rot(f'oreja_{ld}', [(0, 0, 0, 0)] + [(0.1 * k, 0, 0, sg * (10 if k % 2 else -4) * (1 + k * 0.12))
                                                  for k in range(1, 11)])
        h.esc('pecho', [(0, 1, 1, 1), (1.0, 1.06, 1.0, 1.12)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha)
    e2 = m.anim('especial2', 1.2)
    for ld, sg in (('i', 1), ('d', -1)):
        e2.rot(f'oreja_{ld}', [(0, 0, 0, 0), (0.15, 0, 0, sg * 18), (0.25, 0, 0, sg * 10), (0.35, 0, 0, sg * 18),
                               (0.45, 0, 0, sg * 10), (0.9, 0, 0, sg * 15), (1.2, 0, 0, 0)])
    e2.rot('cabeza', [(0, 0, 0, 0), (0.15, 0, 18, 0), (0.35, 0, -12, 0), (0.5, -14, 0, 0), (0.95, -14, 0, 0),
                      (1.2, 0, 0, 0)])
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        bc.huevo_creeper(px, filas, c, '102e36', '102e36', boca='3ad8ff',
                         motas=((2, 2, '3ad8ff'), (13, 2, '3ad8ff'), (2, 3, '183e48'), (13, 3, '183e48'),
                                (6, 11, 'd4cca2'), (9, 11, 'd4cca2'), (6, 13, 'd4cca2'), (9, 13, 'd4cca2'),
                                (7, 12, '3ad8ff'), (8, 12, '3ad8ff')))
    return bc.terminar(m, raiz, 'Creeper Ciego', 'Blind Creeper',
                       (('224e5a', '183e48', '102e36'), ('06404a', '040e12'), dib),
                       ((1.5, 2.4, 2.4), (0, 1.3, 0)),
                       particulas=(('vibracion', bc.anillo((58, 216, 255))), ('sculk', bc.esquirla((20, 58, 68)))))


# ======================================================================================================================
#  La Tarta (Creeper Cake): el mismo diseño, con detalle en la textura
# ======================================================================================================================
CHOCO = bc.CHOCO
CHOCO_N = rampa('120604', '1e0c06', '2c120a', '3a1a0e', '4a2414')
BIZCOCHO = rampa('7a4c22', '9a6630', 'b8803e', 'd09c52', 'e6b86a')
NATA = bc.NATA
MERMELADA = bc.MERMELADA
FIDEO = rampa('6a0a12', 'a01420', 'd02a34', 'ff5a5a', 'ffb0a8')


# ======================================================================================================================
#  Al píxel de Minecraft (Juan, 18-10-2026: «el diseño no sigue los píxeles que deberían tener… en mc ya hay un
#  determinado tamaño para un píxel»): con el modelo al doble y a escala 0,55, el píxel de la textura es de 2 píxeles del
#  modelo (B.TEXEL = 2), 16 por bloque como los de vanilla: la cabeza, 8 x 8; el cuerpo, 8 x 12; las patas, 4 x 6.
#  Estos pintores pintan a ese píxel: cada detalle es un píxel entero (un poro, una pepita, un fideo, una gota).
# ======================================================================================================================
def _azar1(xs, ys, s):
    """Un número fijo de 0 a 1 por cada píxel."""
    h = (np.asarray(xs, np.int64) * 374761393 + np.asarray(ys, np.int64) * 668265263 + int(s) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _fila(ys, th, franja, n):
    """La fila (de 0 arriba a n - 1 abajo) de la pieza entera a la que toca cada píxel de una franja suya."""
    f0, f1 = franja
    return np.floor((f0 + (ys + 0.5) / th * (f1 - f0)) * n + 1e-6).astype(int)


def bizcocho8(franja=(0.0, 1.0)):
    """Los lados de la tarta al píxel de Minecraft: el bizcocho dorado, más claro arriba, con poros de un píxel (más
    oscuros) y alguna miga clara; en la fila del medio, la nata con la mermelada asomando, y debajo su sombra."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = L.tono_suave(tw, th, cara, s, 2.4, 1.0, 0.1, 3.0, franja=franja)
        v = v - (a < 0.14) * 1.1 + (a > 0.93) * 0.7
        rgb = L.color_continuo(BIZCOCHO, v)
        if cara in ('arriba', 'abajo'):
            return L._rgba(rgb), None
        fila = _fila(ys, th, franja, 8)
        nata = fila == 4
        rgb = np.where(nata[..., None], L.color_continuo(NATA, 3.1 + (a - 0.5) * 0.5), rgb)
        mer = nata & (((xs + s) % 4) == 1)
        rgb = np.where(mer[..., None], L.color_continuo(MERMELADA, np.full(a.shape, 2.3)), rgb)
        rgb = np.where((fila == 5)[..., None], rgb * 0.8, rgb)
        return L._rgba(rgb), None
    return fn


def choco8(franja=(0.0, 1.0), relleno=True, filas=12):
    """El bizcocho de chocolate al píxel de Minecraft: el marrón, más claro arriba, con vetas claras del marmolado,
    pepitas negras de un píxel y (si 'relleno') la fila de nata con la mermelada por la mitad."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        a = _azar1(xs, ys, s)
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.9, 0.1, 3.0, franja=franja)
        n = L._ruido(tw, th, s * 5 + 3, 3.0)
        veta = np.sin(x * 0.9 + y * 1.4 + n * 6.0)
        v = v + (veta > 0.8) * 0.9
        rgb = L.color_continuo(CHOCO, v)
        pepita = (a < 0.1) & (veta <= 0.8)
        rgb = np.where(pepita[..., None], L.color_continuo(CHOCO_N, np.full(a.shape, 1.4)), rgb)
        if relleno and cara not in ('arriba', 'abajo'):
            fila = _fila(ys, th, franja, filas)
            nata = fila == filas // 2
            rgb = np.where(nata[..., None], L.color_continuo(NATA, 3.1 + (a - 0.5) * 0.5), rgb)
            mer = nata & (((xs + s) % 4) == 2)
            rgb = np.where(mer[..., None], L.color_continuo(MERMELADA, np.full(a.shape, 2.3)), rgb)
            rgb = np.where((fila == filas // 2 + 1)[..., None], rgb * 0.75, rgb)
        return L._rgba(rgb), None
    return fn


def glaseado8(r=NATA, r_punto=None, gotas=(1, 3), sin_gota=0.35):
    """El glaseado al píxel de Minecraft (una 2.ª capa): por arriba, la nata (más clara arriba a la izquierda) con
    fideos de un píxel; por los lados, la fila de arriba entera y gotas de un píxel de ancho y de largo distinto (la
    punta, algo más clara). Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        if cara == 'abajo':
            return recorte(np.zeros((th, tw, 3)), np.zeros((th, tw)))
        if cara == 'arriba':
            v = 3.3 - (xs + ys) / max(1, tw + th - 2) * 0.8 + (a - 0.5) * 0.25
            rgb = L.color_continuo(r, v)
            if r_punto is not None:
                borde = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1)
                fideo = (a < 0.13) & ~borde
                rgb = np.where(fideo[..., None], L.color_continuo(r_punto, 2.2 + (a < 0.05) * 1.0), rgb)
            return L._rgba(rgb), None
        rng = np.random.default_rng(int(s) * 31 + 3)
        largo = rng.integers(gotas[0], gotas[1] + 1, tw)
        largo = np.where(rng.random(tw) < sin_gota, 0, largo)
        dentro = ys <= largo[xs]
        v = 3.3 - ys * 0.3 + (a - 0.5) * 0.2
        v = np.where((ys == largo[xs]) & (ys > 0), v + 0.5, v)
        return recorte(L.color_continuo(r, v), dentro.astype(float))
    return fn


def cereza8():
    """Una cereza al píxel de Minecraft (de 2 x 2): roja, con el brillo en el píxel de arriba a la izquierda."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = 2.6 - xs * 0.4 - ys * 0.5
        v = np.where((xs == 0) & (ys == 0) & (cara != 'abajo'), 3.7, v)
        if cara == 'abajo':
            v = v - 0.8
        return L._rgba(L.color_continuo(MERMELADA, v)), None
    return fn


def vela8():
    """La vela al píxel de Minecraft: verde, con la espiral blanca en escalones de dos píxeles, más clara a la
    izquierda; por arriba, la cera verde."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = 2.4 + (xs == 0) * 0.6 - ys / max(1, th) * 0.5
        if cara in ('arriba', 'abajo'):
            return L._rgba(L.color_continuo(bc.VELA, v + 0.4)), None
        blanca = ((ys + xs + (cara in ('der', 'atras')) * 2) // 2) % 2 == 0
        rgb = np.where(blanca[..., None], L.color_continuo(NATA, v + 0.6), L.color_continuo(bc.VELA, v))
        return L._rgba(rgb), None
    return fn


def llama8(nombre):
    """La llama de la vela al píxel de Minecraft, como la de vanilla: de un píxel de ancho, amarilla arriba y casi
    blanca abajo (encendida)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = 2.4 + ys / max(1, th - 1) * 1.6
        tex = L._rgba(L.color_continuo(bc.FUEGO, v))
        return tex, tex.copy()
    return B.Pintor(nombre, fn, pleno=True)


def tarta(raiz):
    m = B.Modelo('tarta', K=2, ancho=128)
    m.escala = 0.55
    y_cab = bc.cuerpo(m, L.grueso('choco_tarta', choco8()), L.grueso('choco_pata_tarta', choco8(relleno=False)))
    # Un cuello de glaseado que gotea por el pecho (2.ª capa).
    m.caja_desde('cuerpo', (0, y_cab - 4.0, 0), (16.8, 4.0, 8.8), L.grueso('glaseado_cuello', glaseado8(gotas=(1, 1))),
                 caras={'abajo': None})
    y1 = bc.cabeza(m, 'tarta', 'cuerpo', y_cab, bizcocho8, bc.HUECO_T, neon='d02838')
    # El glaseado de arriba (2.ª capa): la nata con los fideos rojos del original, que gotea por los cantos.
    m.caja_desde('cabeza', (0, y1 - 4.6, 0), (17.0, 5.2, 17.0),
                 L.grueso('glaseado_tarta', glaseado8(r_punto=FIDEO, gotas=(1, 2))))
    # La vela del original (verde y grande, encendida) y dos cerezas (de píxeles enteros).
    m.parte('vela', 'cabeza', (1.0, y1 + 0.6, -1.0))
    m.caja_desde('vela', (1.0, y1 + 0.6, -1.0), (4.0, 12.0, 4.0), L.grueso('vela_tarta', vela8()))
    m.caja_desde('vela', (1.0, y1 + 12.6, -1.0), (2.0, 2.0, 2.0), L.liso('mecha_tarta', bc.HUECO_T, base=1))
    m.parte('llama', 'vela', (1.0, y1 + 14.6, -1.0))
    for giro in (0, 90):
        m.hoja('llama', (1.0, y1 + 14.6 + 2.0, -1.0), 2.0, 4.0, llama8('llama_tarta'), rot=(0, giro, 0))
    cereza = L.grueso('cereza_tarta', cereza8())
    for (x, z) in ((-4.6, 3.6), (4.8, 4.4)):
        m.caja('cabeza', (x, y1 + 2.6, z), (4.0, 4.0, 4.0), cereza)
        m.viga('cabeza', (x, y1 + 4.4, z), (x + 1.0, y1 + 7.0, z - 0.6), 1.0,
               L.liso('rabito', rampa('0a2a06', '14400c', '205a12', '2e7418', '3e8e20')))

    def extra(s):
        s.onda('llama', 'e', 1, 0.12, base=1.0, periodo=0.6)
        s.onda('vela', 'r', 2, 3, periodo=1.2)

    def mecha(h):
        h.esc('llama', [(0, 1, 1, 1), (0.5, 1.4, 1.7, 1.4), (1.0, 1.8, 2.4, 1.8)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha)
    ap = m.anim('aparece', 0.8)
    ap.mov('cuerpo', [(0, 0, -6, 0), (0.25, 0, 8, 0), (0.45, 0, 0, 0), (0.55, 0, 1.0, 0), (0.65, 0, 0, 0)])
    ap.esc('cuerpo', [(0, 0.8, 0.8, 0.8), (0.25, 0.95, 1.12, 0.95), (0.45, 1.12, 0.86, 1.12), (0.65, 1, 1, 1)])
    m.mirar(('cabeza', 0.6))
    m.paso = 2.6

    def dib(px, filas, c):
        bc.huevo_creeper(px, filas, c, '9a6630', 'd02838', boca='2c0e08',
                         motas=tuple((x, f, 'f8f2ea') for f in (2, 3) for x in range(4, 12)) +
                         ((5, 4, 'f8f2ea'), (9, 4, 'f8f2ea'), (6, 2, 'd02a34'), (10, 3, 'd02a34'), (8, 1, '4aa82a'),
                          (4, 8, 'f8f2ea'), (11, 8, 'f8f2ea')))
    return bc.terminar(m, raiz, 'Creeper Tarta', 'Cake Creeper',
                       (('f8f2ea', 'ece4da', '9a6630'), ('462010', '2e1408'), dib),
                       ((1.3, 1.9, 2.0), (0, 1.0, 0)),
                       particulas=(('miga', bc.esquirla((184, 128, 62))), ('nata', bc.esquirla((248, 242, 234)))))


# ======================================================================================================================
#  El Matojo (Creeper de Pasto): chiquito, de bloque de pasto
# ======================================================================================================================
PASTO = rampa('22501a', '326c22', '46902e', '62ae3c', '8acc5a')
TIERRA = rampa('3a2614', '553a20', '6e4c2a', '886036', '9e7444')
AMARILLO_F = bc.AMARILLO_F


def _briznas(x, y, tw, th, s, fuerza=0.55):
    """Las briznas de un lado de hierba: cada columna con su brizna de largo distinto que baja desde arriba (clara en la
    punta, de abajo), y los huecos más oscuros entre ellas."""
    rng = np.random.default_rng(int(s) * 3 + 1)
    largo = rng.uniform(0.25, 1.0, tw + 1) * th
    col = np.clip(x.astype(int), 0, tw)
    L_ = largo[col]
    dentro = y < L_
    fase = np.clip(y / np.maximum(L_, 1), 0, 1)
    return np.where(dentro, fase * fuerza * 0.6 - ((x.astype(int) + int(s)) % 2) * fuerza * 0.4, -fuerza * 0.5)


def pasto16(franja=(0.0, 1.0), tierra=None, base=2.2):
    """El bloque de pasto, suave y con detalle: el verde con briznas de arriba abajo (cada una con su largo, clara en la
    punta), más claro arriba. Con 'tierra' (la parte del alto, de 0 arriba a 1 abajo, donde empieza), abajo la tierra
    con sus piedritas, y la hierba que cuelga sobre ella en puntas (como el lado del bloque de pasto)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        v = L.tono_suave(tw, th, cara, s, base, 0.8, 0.08, 6.0, franja=franja)
        n = L._ruido(tw, th, s * 5 + 2, 3.0)
        if cara in ('arriba', 'abajo'):
            v = v + (n - 0.5) * 0.7 + np.sin(x * 1.3 + n * 4) * np.sin(y * 1.1 + n * 3) * 0.35
        else:
            v = v + np.sin((x + n * 2.2) * 2.0) * 0.2 + _briznas(x, y % 6.0 + (x * 7 % 3), tw, 6.0, s)
        rgb = L.color_continuo(PASTO, v)
        if tierra is not None and cara != 'arriba':
            t = _t(tw, th, cara, franja)
            punta = tierra + (np.abs(np.sin(x * 1.7 + s)) * 0.07 + np.abs(np.sin(x * 0.63 + s * 2)) * 0.06)
            es_t = t > punta
            vt = L.tono_suave(tw, th, cara, s + 7, 2.1, 0.4, 0.12, 4.0, franja=franja)
            for (px, py, k) in puntos(tw, th, s + 11, tw * th / 12, 0.0):
                vt = vt + np.clip(1 - np.hypot(x - px, (y - py) * 1.3) / (0.5 + k * 0.5), 0, 1) * (0.9 if k > 0.5 else -0.8)
            rgb = np.where(es_t[..., None], L.color_continuo(TIERRA, vt), rgb)
            borde = es_t & ~np.roll(es_t, 1, 0)
            rgb = np.where(borde[..., None], rgb * 0.72, rgb)
        return L._rgba(rgb), None
    return fn


def hierba_capa16(colgar=0.24):
    """La 2.ª capa de hierba de la cabeza: por arriba, el césped entero; por los lados, la hierba que cuelga en puntas
    irregulares hasta 'colgar' del alto (como el lado del bloque de pasto, pero suelta). Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        if cara == 'abajo':
            return recorte(np.zeros((th, tw, 3)), np.zeros((th, tw)))
        v = L.tono_suave(tw, th, cara, s, 2.9, 0.6, 0.08, 5.0)
        n = L._ruido(tw, th, s * 3 + 4, 2.5)
        if cara == 'arriba':
            v = v + (n - 0.5) * 0.8 + np.sin(x * 1.4 + n * 5) * np.sin(y * 1.2 + n * 4) * 0.4
            return L._rgba(L.color_continuo(PASTO, v)), None
        # Cada columna, una brizna que cuelga hasta su largo (más larga en algunas), con la punta clara.
        rng = np.random.default_rng(int(s) * 7 + 2)
        largo = th * colgar * (0.45 + 0.75 * rng.random(tw + 1) ** 1.5)
        L_ = largo[np.clip(xs, 0, tw)]
        dentro = y < L_
        v = v + np.sin((x + n * 2.0) * 2.0) * 0.25 - (y / np.maximum(L_, 1)) * 1.4 - ((xs + s) % 2) * 0.35
        v = np.where(dentro & (y > L_ - 1.0), v + 0.9, v)
        return recorte(L.color_continuo(PASTO, v), dentro.astype(float))
    return fn


def mata_plano(nombre, flor=None):
    """Una mata de hierba plana (como la hierba de vanilla, para cruzarla con otra): seis briznas afiladas y algo curvas
    que salen de abajo, más claras en la punta; con 'flor' (una rampa), una flor redonda en lo alto de la del medio."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw
        v = 1 - (ys + 0.5) / th
        a = np.zeros((th, tw), bool)
        val = np.zeros((th, tw))
        rng = np.random.default_rng(int(s) + 5)
        for k in range(6):
            x0 = 0.14 + 0.72 * k / 5 + rng.uniform(-0.04, 0.04)
            alto = rng.uniform(0.5, 0.92) if flor is None or k not in (2, 3) else 0.62
            cx = x0 + rng.uniform(-0.18, 0.18) * v ** 2
            ancho = 0.075 * np.clip(1 - v / alto, 0, 1) + 0.012
            b = (np.abs(u - cx) < ancho) & (v < alto)
            a |= b
            val = np.where(b, 1.2 + v / alto * 2.4, val)
        rgb = L.color_continuo(PASTO, val)
        emis = None
        if flor is not None:
            d = np.hypot((u - 0.5) / 0.17, (v - 0.8) / 0.15)
            f = d < 1
            tallo = (np.abs(u - 0.5) < 0.035) & (v < 0.8)
            a |= f | tallo
            rgb[tallo] = L.color_continuo(PASTO, np.full(tallo.sum(), 1.6))
            rgb[f] = L.color_continuo(flor, 3.3 - d[f] * 1.4)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(a, 255, 0)
        return tex, emis
    return B.Pintor(nombre, fn)


def matojo(raiz):
    m = B.Modelo('matojo', K=2, ancho=128)
    m.escala = 0.34
    # Chiquito y rechoncho, a cuatro patas: la cabeza grande, el cuerpo corto y cuatro patas cortas y separadas (que se
    # vean las cuatro), de bloque de pasto; las patas, con la tierra abajo (como el lado del bloque) y la hierba
    # colgando sobre ella.
    pie = L.grueso('pie_matojo', pasto16(tierra=0.42))
    y_cab = bc.cuerpo(m, L.grueso('piel_matojo', pasto16()), pie, alto_pata=8.0, alto=12.0, fondo=8.0, x=4.6, z=5.2,
                      pata=6.0)
    y1 = bc.cabeza(m, 'matojo', 'cuerpo', y_cab, lambda fr: pasto16(fr, base=1.8), bc.HUECO_P, pupila='d8ff5a')
    # La 2.ª capa de la cabeza: el césped fresco (más claro) que la cubre por arriba y cuelga en briznas por los lados
    # (por delante, solo por encima de los ojos).
    capa(m, 'cabeza', (0, y_cab, 0), (16, 16, 16), L.grueso('cesped_matojo', hierba_capa16(0.34)), infla=0.7,
         caras={'abajo': None, 'frente': L.grueso('cesped_frente_matojo', hierba_capa16(0.2))})
    # Encima, solo hierba: matas planas (como las de vanilla), que se mueven con el viento.
    m.parte('mata', 'cabeza', (0, y1 + 0.7, 0))
    p = mata_plano('mata_matojo_hierba')
    for (x, z, g, alto) in ((-4.0, 1.5, 0, 8.0), (3.4, -3.0, 30, 9.0), (0.2, 4.0, 60, 7.0), (-1.6, -4.0, 15, 8.0),
                            (4.8, 3.2, 20, 10.0), (-5.0, -1.2, 70, 9.0)):
        for giro in (45, -45):
            m.hoja('mata', (x, y1 + 0.7 + alto / 2, z), alto * 0.8, alto, p, rot=(0, giro + g, 0), dos_caras=False)
    # Matitas sueltas que asoman por los cantos de la cabeza y en los hombros (la silueta, de matojo).
    suelta = mata_plano('mata_suelta_matojo')
    for (parte, x, y, z, alto, g) in (('cabeza', -8.4, y1 - 2.0, 5.0, 5.0, 10), ('cabeza', 8.4, y1 - 3.0, -2.0, 5.5, 40),
                                      ('cabeza', -8.2, y1 - 6.0, -5.0, 4.5, 70), ('cabeza', 8.6, y1 - 7.0, 4.0, 4.0, 20),
                                      ('cuerpo', -8.2, y_cab - 3.0, 0.0, 4.5, 0), ('cuerpo', 8.2, y_cab - 4.0, 1.0, 4.0, 50)):
        for giro in (45, -45):
            m.hoja(parte, (x, y + alto / 2, z), alto * 0.9, alto, suelta, rot=(0, giro + g, 0), dos_caras=False)

    def extra(s):
        s.onda('mata', 'r', 2, 6, periodo=1.5)
        s.onda('mata', 'r', 0, 4, periodo=2.0, fase=0.25)

    def mecha(h):
        h.esc('mata', [(0, 1, 1, 1), (0.4, 1.2, 1.3, 1.2), (1.0, 1.4, 1.5, 1.4)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha, paso=0.6, amp=40)
    ap = m.anim('aparece', 0.9)
    ap.mov('cuerpo', [(0, 0, -16, 0), (0.3, 0, 5, 0), (0.5, 0, 0, 0), (0.62, 0, 1.2, 0), (0.75, 0, 0, 0)])
    ap.esc('cuerpo', [(0, 0.5, 0.5, 0.5), (0.3, 0.92, 1.18, 0.92), (0.5, 1.18, 0.82, 1.18), (0.75, 1, 1, 1)])
    m.mirar(('cabeza', 0.6))
    m.paso = 0.9

    def dib(px, filas, c):
        bc.huevo_creeper(px, filas, c, '46902e', '0a200a', boca='0a200a',
                         motas=((5, 1, '8acc5a'), (8, 1, '8acc5a'), (10, 1, '8acc5a'), (11, 2, '62ae3c'),
                                (6, 6, 'd8ff5a'), (10, 6, 'd8ff5a'), (4, 14, '6e4c2a'), (5, 14, '6e4c2a'),
                                (10, 14, '6e4c2a'), (11, 14, '6e4c2a')))
    return bc.terminar(m, raiz, 'Creeper Matojo', 'Bush Creeper',
                       (('8acc5a', '62ae3c', '326c22'), ('22501a', '553a20'), dib),
                       ((0.7, 0.8, 1.0), (0, 0.42, 0)),
                       particulas=(('brizna', bc.hojita((98, 174, 60))),))


# ======================================================================================================================
#  El Marchito (Creeper de Wither Rose): la zarza y los pétalos, en 2.ª capa
# ======================================================================================================================
TALLO = bc.TALLO
PETALO = rampa('14080c', '2e1018', '4c1824', '722434', 'a03a4c')
CORAZON_ROSA = bc.CORAZON_ROSA
ESPINA = bc.ESPINA
HOJA_W = rampa('0c1008', '161c0e', '222c16', '303e1e', '425228')


def tallo16(franja=(0.0, 1.0)):
    """El tallo de la rosa marchita, con detalle: las fibras de arriba abajo, los surcos más oscuros y un brillo húmedo
    en vetas, y alguna mancha de rojo seco."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.7, 0.1, 6.0, franja=franja)
        n = L._ruido(tw, th, s * 7 + 1, 5.0)
        if cara not in ('arriba', 'abajo'):
            fibra = np.sin((x + n * 3.0) * 1.6)
            v = v + fibra * 0.3 - np.clip(-fibra - 0.8, 0, 1) * 1.6
            v = v + np.clip(np.sin((x + n * 2) * 0.5 + y * 0.12) - 0.85, 0, 1) * 3.0
        rgb = L.color_continuo(TALLO, v)
        for (px, py, k) in puntos(tw, th, s + 4, tw * th / 90, 1.0):
            g = np.clip(1 - np.hypot((x - px) * 1.6, y - py) / (1.2 + k), 0, 1)
            rgb = mezclar(rgb, g * 0.5, L.color_continuo(ESPINA, np.full((th, tw), 1.4)))
        return L._rgba(rgb), None
    return fn


def petalo_plano(nombre, r=PETALO):
    """Un pétalo plano de la rosa marchita (a la resolución del modelo): ancho, con la punta redonda y la base estrecha;
    oscuro en la base y más claro hacia el canto, con el nervio del medio y el borde rizado más oscuro."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = 1 - (ys + 0.5) / th
        ancho = 0.5 * np.clip(np.sin(np.clip(v, 0, 1) * math.pi * 0.62 + 0.25), 0, 1)
        ancho = np.where(v > 0.72, np.sqrt(np.clip(0.28 ** 2 - (v - 0.72) ** 2, 0, 1)) / 0.28 * 0.47, ancho)
        dentro = (np.abs(u) < ancho) & (v > 0) & (v < 1.0)
        rizo = dentro & ((ancho - np.abs(u)) * tw < 1.3)
        val = 1.2 + v * 2.2 - (np.abs(u) < 0.03) * 0.8
        val = np.where(rizo, val - 0.9, val)
        tex = L._rgba(L.color_continuo(r, val))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def centro_rosa16():
    """Lo alto de la cabeza, el corazón de la rosa visto desde arriba: los pétalos enroscados en espiral, más oscuros
    hacia el centro."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5 - tw / 2, ys + 0.5 - th / 2
        r = np.hypot(x, y) / (tw / 2)
        a = np.arctan2(y, x)
        espiral = np.sin(a * 1.0 + r * 9.0)
        v = 1.0 + r * 2.0 + np.clip(espiral, 0, 1) * 0.6 - np.clip(-espiral - 0.7, 0, 1) * 1.4
        return L._rgba(L.color_continuo(L.juntar(CORAZON_ROSA[:2], PETALO[2:]), v)), None
    return fn


def zarza8(hojas=True):
    """La zarza al píxel de Minecraft (2.ª capa del tallo): espinas de dos píxeles (la base oscura y la punta clara,
    arriba y hacia fuera), una por cuadro de 3 x 3 como mucho; y, arriba en los costados, una hoja mustia caída con su
    nervio. Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        rgb = np.zeros((th, tw, 3))
        a = np.zeros((th, tw), bool)
        if cara in ('arriba', 'abajo'):
            return recorte(rgb, a.astype(float))
        rng = np.random.default_rng(int(s) * 17 + 5)
        for j0 in range(1, th, 3):
            for i0 in range(0, tw, 3):
                if rng.random() > 0.55:
                    continue
                i, j = i0 + rng.integers(0, 3), j0 + rng.integers(0, 2)
                lado = 1 if rng.random() < 0.5 else -1
                for (di, dj, val) in ((0, 0, 1.6), (lado, -1, 3.0)):
                    ii, jj = i + di, j + dj
                    if 0 <= ii < tw and 0 <= jj < th:
                        rgb[jj, ii] = L.color_continuo(ESPINA, np.array([val]))[0]
                        a[jj, ii] = True
        if hojas and cara in ('izq', 'der'):
            cx, cy = tw * 0.5, th * 0.22
            x, y = xs + 0.5, ys + 0.5
            u = (x - cx) * math.cos(0.6) + (y - cy) * math.sin(0.6)
            w_ = -(x - cx) * math.sin(0.6) + (y - cy) * math.cos(0.6)
            hoja = np.abs(w_) < 1.15 * np.sqrt(np.clip(1 - (u / 2.8) ** 2, 0, 1))
            vv = 2.5 + u * 0.15 - (np.abs(w_) < 0.5) * 0.9
            rgb = np.where(hoja[..., None], L.color_continuo(HOJA_W, vv), rgb)
            a |= hoja
        return recorte(rgb, a.astype(float))
    return fn


def capullo8(franja=(0.0, 1.0)):
    """El capullo al píxel de Minecraft: los pétalos cerrados en escamas de 4 x 3 píxeles, imbricadas (cada fila corrida
    dos), con el canto de arriba claro y el hueco de abajo oscuro, donde asoma el rojo del corazón."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.6, 0.05, 3.0, franja=franja)
        fila = _fila(ys, th, franja, 8)
        banda = fila // 3
        col = (xs + (banda % 2) * 2) % 4
        dentro_f = fila % 3
        v = v + (dentro_f == 0) * 0.8 - ((dentro_f == 2) & ((col == 0) | (col == 3))) * 1.0
        return L._rgba(L.color_continuo(PETALO, v)), None
    return fn


def petalos8():
    """Los pétalos de fuera del capullo al píxel de Minecraft (2.ª capa de la cabeza): suben desde abajo en tres
    lóbulos redondos por cada lado (el canto de arriba claro, la base oscura, el nervio de un píxel); por delante, solo
    en los bordes (la cara queda libre). Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        if cara in ('arriba', 'abajo'):
            return recorte(np.zeros((th, tw, 3)), np.zeros((th, tw)))
        x = np.arange(tw) + 0.5
        if cara == 'frente':
            centros = ((0.5, 1.6), (tw - 0.5, 1.6))
        else:
            centros = ((tw * 0.17, tw * 0.2), (tw * 0.5, tw * 0.2), (tw * 0.83, tw * 0.2))
        alto = np.full(tw, th + 1.0)
        for k, (cx, w_) in enumerate(centros):
            d = (x - cx) / w_
            cima = th * (0.38 + 0.08 * ((k + s) % 2))
            lob = np.where(np.abs(d) < 1.05, cima + (th - cima) * (1 - np.sqrt(np.clip(1 - d * d, 0, 1))) * 0.8, th + 1)
            alto = np.minimum(alto, lob)
        cima_col = np.ceil(alto - 0.5).astype(int)
        dentro = ys >= cima_col[xs]
        prof = ys - cima_col[xs]
        vv = 3.2 - prof * 0.45
        nervio = np.zeros((th, tw), bool)
        for (cx, w_) in centros:
            nervio |= (xs == int(cx)) & (prof >= 1)
        vv = np.where(nervio, vv - 0.9, vv)
        return recorte(L.color_continuo(PETALO, vv), dentro.astype(float))
    return fn


def marchito(raiz):
    m = B.Modelo('marchito', K=2, ancho=128)
    m.escala = 0.55
    tallo = L.grueso('tallo_marchito', tallo16())
    y_cab = bc.cuerpo(m, tallo, tallo)
    # La zarza en 2.ª capa: las espinas por el tallo y las patas, y las hojas mustias caídas en los costados.
    capa(m, 'cuerpo', (0, 12.0, 0), (16, 24, 8), L.grueso('zarza_marchito', zarza8()), infla=0.8,
         caras={'arriba': None, 'abajo': None})
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        capa(m, p, (px, 0.0, pz), (8, 12, 8), L.grueso('zarza_pata_marchito', zarza8(hojas=False)), infla=0.6,
             caras={'arriba': None, 'abajo': None})
    # La cabeza: el capullo, con la cara de creeper honda y el rojo del corazón de la rosa dentro; los pétalos de fuera,
    # en 2.ª capa.
    y1 = bc.cabeza(m, 'marchito', 'cuerpo', y_cab, capullo8, bc.HUECO_W, neon='c0303a',
                   caras={'arriba': L.grueso('centro_rosa_marchito', centro_rosa16())})
    capa(m, 'cabeza', (0, y_cab, 0), (16, 16, 16), L.grueso('petalos_marchito', petalos8()), infla=0.8,
         caras={'arriba': None, 'abajo': None})
    # La cabeza es el corazón de la rosa marchita: los pétalos grandes la abrazan por arriba, en copa (los de los lados
    # y los de las esquinas, que se abren hacia fuera y suben por encima de la coronilla).
    m.parte('rosa', 'cabeza', (0, y1, 0))
    grande = petalo_plano('petalo_marchito')
    chico = petalo_plano('petalo_c_marchito', L.juntar(CORAZON_ROSA[:2], PETALO[2:]))
    for k in range(4):
        phi = 90.0 * k
        ph = math.radians(phi)
        m.hoja('rosa', (math.sin(ph) * 8.6, y1 + 1.6, math.cos(ph) * 8.6), 13.0, 8.0, grande, rot=(28, phi, 0),
               dos_caras=False)
    for k in range(4):
        phi = 45.0 + 90.0 * k
        ph = math.radians(phi)
        m.hoja('rosa', (math.sin(ph) * 10.6, y1 + 0.8, math.cos(ph) * 10.6), 8.0, 7.0, chico, rot=(40, phi, 0),
               dos_caras=False)

    def extra(s):
        s.onda('rosa', 'r', 1, 6, periodo=4.0)

    def mecha(h):
        h.esc('rosa', [(0, 1, 1, 1), (0.5, 1.25, 0.9, 1.25), (1.0, 1.5, 0.8, 1.5)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        bc.huevo_creeper(px, filas, c, '4c1824', 'c0303a', boca='c0303a',
                         motas=((6, 1, '2e1018'), (7, 1, '722434'), (8, 1, '722434'), (9, 1, '2e1018'), (5, 2, '722434'),
                                (10, 2, '722434'), (7, 2, 'b02a36'), (8, 2, 'b02a36'), (3, 10, '303830'), (12, 11, '303830'),
                                (4, 12, '62161c'), (11, 9, '62161c')))
    return bc.terminar(m, raiz, 'Creeper Marchito', 'Withered Creeper',
                       (('722434', '4c1824', '2e1018'), ('86806e', '120a0c'), dib),
                       ((1.6, 2.4, 2.6), (0, 1.25, 0)),
                       particulas=(('petalo', bc.hojita((74, 26, 32))), ('ceniza', bc.esquirla((134, 128, 110)))))


# ======================================================================================================================
#  La Enredadera (Creeper de Raíz de Azalea): las enredaderas y la azalea, en 2.ª capa; las lianas, planas
# ======================================================================================================================
CORTEZA = bc.CORTEZA
MUSGO = bc.MUSGO
HOJA_AZ = rampa('16340e', '224c16', '30661e', '428228', '5aa036')
ROSA_AZ = bc.ROSA_AZ


def corteza8(franja=(0.0, 1.0)):
    """La corteza de raíz al píxel de Minecraft, como el lado de un tronco: la veta de arriba abajo en tres tonos (cada
    columna la suya, cortada en placas de tres a cinco filas), un surco oscuro cada tres columnas y algún nudo; arriba,
    los anillos; y el musgo que sube desde abajo en manchas de píxeles."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        v = L.tono_suave(tw, th, cara, s, 2.1, 0.8, 0.0, 3.0, franja=franja)
        if cara not in ('arriba', 'abajo'):
            fila = _fila(ys, th, franja, 12)
            desfase = (_azar1(xs, np.zeros_like(xs), s + 3) * 4).astype(int)
            placa = _azar1(xs, (fila + desfase) // 4, s + 7)
            v = v + (placa - 0.5) * 0.9 - (((xs + int(s)) % 3) == 0) * 0.7
            nudo = _azar1(xs // 3, fila // 4, s + 11) < 0.12
            v = np.where(nudo & (((xs + int(s)) % 3) == 1), v - 1.2, v)
        else:
            d = np.maximum(np.abs(x - tw / 2), np.abs(y - th / 2))
            v = v + np.where(np.floor(d) % 2 == 0, 0.35, -0.35)
        rgb = L.color_continuo(CORTEZA, v)
        if cara != 'arriba':
            t_ = _t(tw, th, cara, franja)
            m_ = L._ruido(tw, th, s * 4 + 7, 2.0)
            musgo = (m_ - 1.4 + t_ * 0.95) > 0
            vm = 2.3 + (_azar1(xs, ys, s + 5) - 0.5) * 0.8 - t_ * 0.4
            rgb = np.where(musgo[..., None], L.color_continuo(MUSGO, vm), rgb)
        return L._rgba(rgb), None
    return fn


def hojas_azalea(rgb, a, x, y, tw, th, s, densidad=1.0, flores=0.1):
    """Pinta hojitas de azalea (óvalos de tres verdes, con su canto) y alguna flor rosa donde se pida (en rgb y a)."""
    for (px, py, k) in puntos(tw + 2, th + 2, s + 13, (tw + 2) * (th + 2) / 5 * densidad, 0.0):
        px, py = px - 1, py - 1
        ang = k * math.pi * 2
        u = (x - px) * math.cos(ang) + (y - py) * math.sin(ang)
        w_ = -(x - px) * math.sin(ang) + (y - py) * math.cos(ang)
        d = np.hypot(u / 1.5, w_ / 0.95)
        hoja = d < 1
        vv = 1.6 + k * 2.0 - np.clip(d - 0.65, 0, 1) * 2.0
        rgb[hoja] = L.color_continuo(HOJA_AZ, vv[hoja])
        a[hoja] = 1.0
    for (px, py, k) in puntos(tw, th, s + 29, tw * th / 40 * flores * 10, 1.0):
        d = np.hypot(x - px, y - py)
        flor = d < 1.15
        vv = 3.2 - d * 1.2
        rgb[flor] = L.color_continuo(ROSA_AZ, vv[flor])
        a[flor] = 1.0
        centro = d < 0.4
        rgb[centro] = L.color_continuo(rampa('5a4a10', '8a7418', 'c8a828', 'f0d84a', 'fff4a0'), np.full(centro.sum(), 2.6))
    return rgb, a


def azalea_capa16(colgar=0.3):
    """La 2.ª capa de la cabeza: la mata de azalea en flor que la cubre por arriba y cuelga por los lados en un borde de
    hojas irregular (por delante, solo por encima de los ojos). Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        rgb = np.zeros((th, tw, 3))
        a = np.zeros((th, tw))
        if cara == 'abajo':
            return recorte(rgb, a)
        if cara == 'arriba':
            rgb[:] = L.color_continuo(HOJA_AZ, L.tono_suave(tw, th, cara, s, 1.6, 0.5, 0.1, 4.0))[..., :3]
            a[:] = 1.0
            rgb, a = hojas_azalea(rgb, a, x, y, tw, th, s, 1.0, 0.12)
            return recorte(rgb, a)
        c = colgar * (0.78 if cara == 'frente' else 1.0)
        limite = th * c * (0.6 + 0.4 * np.abs(np.sin(x * 0.9 + s)) + 0.2 * np.sin(x * 0.31 + s * 2))
        base = y < limite
        rgb[base] = L.color_continuo(HOJA_AZ, np.full(base.sum(), 1.4))
        a[base] = 1.0
        rgb2, a2 = hojas_azalea(rgb.copy(), a.copy(), x, y, tw, th, s, 1.0, 0.1)
        keep = (y < limite + 0.8)
        rgb = np.where(keep[..., None], rgb2, rgb)
        a = np.where(keep, a2, a)
        return recorte(rgb, a)
    return fn


def enredadera_capa8(n=2):
    """La 2.ª capa del cuerpo y las patas al píxel de Minecraft: enredaderas que lo cruzan en diagonal, el tallo de un
    píxel en escalera y las hojas alternas (un píxel arriba, otro abajo), con alguna flor rosa. Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        rgb = np.zeros((th, tw, 3))
        a = np.zeros((th, tw))
        if cara in ('arriba', 'abajo'):
            return recorte(rgb, a)
        rng = np.random.default_rng(int(s) * 13 + 1)
        for k in range(n):
            y0 = rng.uniform(th * 0.15, th * 0.85)
            pend = (0.5 if (k + s) % 2 else -0.5) * rng.uniform(0.9, 1.1)
            fila = np.floor(y0 + pend * (xs + 0.5) - pend * tw / 2).astype(int)
            tallo = ys == fila
            rgb[tallo] = L.color_continuo(MUSGO, np.full(tallo.sum(), 2.0))
            a[tallo] = 1.0
            lado = np.where(((xs // 2) + k) % 2 == 0, -1, 1)
            hoja = ((xs + k) % 2 == 0) & (ys == fila + lado)
            rgb[hoja] = L.color_continuo(HOJA_AZ, np.full(hoja.sum(), 3.3))
            a[hoja] = 1.0
            flor = hoja & (_azar1(xs, np.full(xs.shape, k), s) < 0.18)
            rgb[flor] = L.color_continuo(ROSA_AZ, np.full(flor.sum(), 3.2))
        return recorte(rgb, a)
    return fn


def liana8(nombre):
    """Una liana plana al píxel de Minecraft (como las enredaderas de vanilla): el tallo de un píxel que baja por el
    medio, una hoja a cada lado cada dos filas (alternas) y la flor de azalea en la punta."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        c = tw // 2
        rgb = np.zeros((th, tw, 3))
        tallo = (xs == c) & (ys < th - 1)
        rgb[tallo] = L.color_continuo(MUSGO, 2.0 + ys[tallo] * 0.05)
        lado = np.where((ys // 2) % 2 == 0, c - 1, c + 1)
        hoja = (ys % 2 == 0) & (ys < th - 2) & (xs == lado)
        rgb[hoja] = L.color_continuo(HOJA_AZ, np.full(hoja.sum(), 3.2))
        flor = ((ys == th - 1) & (np.abs(xs - c) <= 1)) | ((ys == th - 2) & (xs == c))
        rgb[flor] = L.color_continuo(ROSA_AZ, np.where(xs[flor] == c, 3.4, 2.6))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(tallo | hoja | flor, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def enredadera(raiz):
    m = B.Modelo('enredadera', K=2, ancho=128)
    m.escala = 0.55
    piel = L.grueso('piel_enredadera', corteza8())
    y_cab = bc.cuerpo(m, piel, piel)
    # Las enredaderas que lo rodean, en 2.ª capa (el cuerpo y las patas).
    capa(m, 'cuerpo', (0, 12.0, 0), (16, 24, 8), L.grueso('enredaderas_enredadera', enredadera_capa8(2)), infla=0.8,
         caras={'arriba': None, 'abajo': None})
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        capa(m, p, (px, 0.0, pz), (8, 12, 8), L.grueso('enredaderas_pata', enredadera_capa8(1)), infla=0.6,
             caras={'arriba': None, 'abajo': None})
    y1 = bc.cabeza(m, 'enredadera', 'cuerpo', y_cab, corteza8, bc.HUECO_E, neon='b04a80')
    # La mata de azalea en flor: en 2.ª capa por la cabeza (cuelga por los lados) y un copete encima.
    capa(m, 'cabeza', (0, y_cab, 0), (16, 16, 16), L.grueso('azalea_enredadera', azalea_capa16(0.3)), infla=0.8)
    copete = L.grueso('copete_enredadera', azalea_capa16(1.0))
    m.caja_desde('cabeza', (0, y1 + 0.8, -0.5), (13.0, 3.0, 13.0), copete)
    m.caja_desde('cabeza', (1.0, y1 + 3.8, 0.5), (8.0, 2.0, 8.0), copete)
    # Las lianas: dos, planas y cruzadas (como las enredaderas de vanilla), que cuelgan de los lados de la cabeza hasta
    # las rodillas, con su flor en la punta; con ellas te atrapa.
    liana = liana8('liana_enredadera')
    for i, (x, z) in enumerate(((-9.4, 3.0), (9.4, 3.0))):
        n = m.parte(f'liana{i}', 'cabeza', (x, y_cab + 1.0, z))
        n2 = m.parte(f'liana{i}b', n, (x, y_cab - 9.0, z))
        for giro in (30, -60):
            m.hoja(n, (x, y_cab - 4.0, z), 6.0, 10.4, liana, rot=(0, giro, 0), dos_caras=False)
            m.hoja(n2, (x, y_cab - 14.0, z), 6.0, 10.4, liana, rot=(0, giro, 0), dos_caras=False)

    def extra(s):
        for i in range(2):
            s.onda(f'liana{i}', 'r', 0, 6, periodo=1.6, fase=i * 0.23)
            s.onda(f'liana{i}b', 'r', 0, 10, periodo=1.6, fase=i * 0.23 + 0.2)

    def mecha(h):
        for i in range(2):
            lado = -1 if i == 0 else 1
            h.rot(f'liana{i}', [(0, 0, 0, 0), (1.0, -20, 0, lado * 25)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha)
    a = m.anims['andar']
    for i in range(2):
        a.onda(f'liana{i}', 'r', 0, 10, fase=i * 0.5)
    at = m.anim('ataque', 0.9)
    for i in range(2):
        at.rot(f'liana{i}', [(0, 0, 0, 0), (0.12, 25, 0, 0), (0.3, -95, 0, 0), (0.75, -90, 0, 0), (0.9, 0, 0, 0)])
        at.rot(f'liana{i}b', [(0, 0, 0, 0), (0.12, 15, 0, 0), (0.3, -10, 0, 0), (0.75, -6, 0, 0), (0.9, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.12, -10, 0, 0), (0.3, 12, 0, 0), (0.9, 0, 0, 0)])
    est = m.anim('estado1', 1.0, bucle=True)
    for i in range(2):
        est.rot(f'liana{i}', [(0, -84, 0, 0), (0.5, -90, 0, 0), (1.0, -84, 0, 0)])
        est.rot(f'liana{i}b', [(0, -6, 0, 0), (0.5, -12, 0, 0), (1.0, -6, 0, 0)])
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        bc.huevo_creeper(px, filas, c, '56381c', '1a0e08', boca='1a0e08',
                         motas=((4, 1, '428228'), (5, 1, '428228'), (7, 1, 'd8609c'), (9, 1, '428228'), (10, 1, '428228'),
                                (4, 2, '30661e'), (11, 2, '30661e'), (12, 3, 'd8609c'), (3, 9, '3c681e'),
                                (4, 10, '3c681e'), (12, 8, '3c681e'), (11, 9, '428228')))
    return bc.terminar(m, raiz, 'Creeper Enredadera', 'Vine Creeper',
                       (('8a6034', '6e4a26', '56381c'), ('2a1a0e', '0a0604'), dib),
                       ((1.5, 2.1, 2.4), (0, 1.2, 0)),
                       particulas=(('hoja', bc.hojita((66, 130, 40))), ('flor', bc.chispa((240, 142, 192)))))


# ======================================================================================================================
#  La Gelatina (Creeper de Fluido): como el slime, el gel trabajado con el núcleo dentro, sin cara; y el charco
# ======================================================================================================================
GEL = bc.GEL
NUCLEO_G = bc.NUCLEO_G


def gel8(alfa=118):
    """El gel al píxel de Minecraft, como el del slime: translúcido, más claro arriba y algo más espeso en el canto; en
    las caras grandes, el brillo en una L de píxeles arriba a la izquierda y alguna burbuja (un píxel claro con su
    sombra debajo)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = L.tono_suave(tw, th, cara, s, 2.3, 0.8, 0.03, 4.0)
        borde = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        al = np.where(borde == 0, alfa + 45.0, float(alfa))
        v = v + (borde == 0) * 0.3
        if tw >= 6 and th >= 6 and cara != 'abajo':
            ele = ((ys == 1) & (xs >= 1) & (xs <= 2)) | ((xs == 1) & (ys == 2))
            v = np.where(ele, 4.0, v)
            al = np.where(ele, 215.0, al)
            a = _azar1(xs, ys, s)
            burbuja = (a < 0.05) & (borde >= 2)
            v = np.where(burbuja, 3.6, v)
            al = np.where(burbuja, 190.0, al)
            debajo = np.roll(burbuja, 1, 0)
            v = np.where(debajo & ~burbuja, v - 0.5, v)
        tex = L._rgba(L.color_continuo(GEL, v), alfa=np.clip(np.round(al), 60, 235).astype(np.uint8))
        return tex, None
    return fn


def nucleo16(franja=(0.0, 1.0), luz=False):
    """El creeper de dentro, oscuro y suave; con 'luz', el núcleo encendido del pecho (un resplandor de agua)."""
    def fn(tw, th, cara, s):
        v = L.tono_suave(tw, th, cara, s, 2.0, 0.6, 0.12, 6.0, franja=franja)
        tex = L._rgba(L.color_continuo(NUCLEO_G, v))
        if not luz or cara != 'frente':
            return tex, None
        xs, ys = L._malla(tw, th)
        g = np.clip(1 - np.hypot((xs + 0.5 - tw / 2) / (tw * 0.36), (ys + 0.5 - th * 0.32) / (th * 0.16)), 0, 1)
        return encender(tex, g ** 0.6, GEL, 1.6 + g * 2.2)
    return fn


def charco(nombre):
    """El charco de gel que deja a sus pies: una mancha irregular, más espesa en el borde, con brillos."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th - 0.5
        n = L._ruido(tw, th, 41, max(3.0, tw / 6))
        r = np.hypot(u, v * 1.1)
        dentro = r < 0.36 + (n - 0.5) * 0.22
        if cara != 'arriba':
            dentro[:] = False
        val = 2.2 + np.clip(r - 0.25, 0, 1) * 4 + (L._ruido(tw, th, 43, 3.0) > 0.7) * 1.2
        al = np.where(dentro, 165 + np.clip(r - 0.25, 0, 1) * 300, 0)
        tex = L._rgba(L.color_continuo(GEL, val), alfa=np.clip(al, 0, 220).astype(np.uint8))
        return tex, None
    return B.Pintor(nombre, fn)


def gelatina(raiz):
    m = B.Modelo('gelatina', K=2, ancho=128)
    m.escala = 0.55
    m.translucido = True
    gel = L.grueso('gel_gelatina', gel8())
    nucleo = L.grueso('nucleo_gelatina', nucleo16())
    # Como el Slime: dentro, el creeper oscuro (el núcleo, con su luz en el pecho), y por fuera, el gel trabajado.
    m.parte('cuerpo', None, (0, 12.0, 0))
    bc.patas(m, 'cuerpo', 4.0, 8.0, 5.0, 12.0, nucleo)
    for p in PATAS:
        pz = 8.0 if p[5] == 'd' else -8.0
        px = 4.0 if p[6] == 'i' else -4.0
        m.caja_desde(p, (px, 0.01, pz), (8.0, 12.0, 8.0), gel)
    m.caja_desde('cuerpo', (0, 12.0, 0), (11.0, 24.0, 4.0), L.grueso('nucleo_pecho_gelatina', nucleo16(luz=True)))
    m.caja_desde('cuerpo', (0, 12.0, 0), (16.0, 24.2, 8.0), gel)
    # La cabeza, como el slime: el gel y, en medio, el núcleo (un cubo oscuro, sin cara).
    m.parte('cabeza', 'cuerpo', (0, 36.0, 0))
    m.caja_desde('cabeza', (0, 38.1, 0.4), (14.0, 14.0, 14.0), nucleo)
    m.caja_desde('cabeza', (0, 35.6, 0.4), (19.0, 19.0, 19.0), gel)
    # El charco a sus pies.
    m.parte('charco', None, (0, 0, 0))
    m.caja('charco', (0, 0.15, 0), (26.0, 0.2, 30.0), charco('charco_gelatina'),
           caras={c: None for c in ('frente', 'atras', 'izq', 'der', 'abajo')})

    def extra(s):
        s.onda('cuerpo', 'e', 0, 0.02, base=1.0, periodo=1.5)
        s.onda('charco', 'e', 0, 0.04, base=1.0, periodo=2.5)
        s.onda('charco', 'e', 2, 0.04, base=1.0, periodo=2.5, fase=0.3)

    def mecha(h):
        h.esc('cabeza', [(0, 1, 1, 1)] + [(0.1 * k, 1 + 0.012 * k * (1 if k % 2 else -1),
                                           1 - 0.01 * k * (1 if k % 2 else -1),
                                           1 + 0.012 * k * (1 if k % 2 else -1)) for k in range(1, 11)])
    bc.anims(m, extra_siempre=extra, extra_hinchado=mecha)
    m.mirar(('cabeza', 0.5))
    m.paso = 2.6

    def dib(px, filas, c):
        # El huevo, sin cara: el gel y el núcleo oscuro en medio.
        for f in range(2, 15):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('2aac94')
        for f in range(6, 12):
            for x in range(5, 11):
                px[x, f] = c('16564c')
        for x, f, col in ((4, 3, 'bafff2'), (5, 3, 'bafff2'), (4, 4, 'bafff2'), (12, 11, '62dcc2'), (3, 12, '62dcc2'),
                          (11, 4, '62dcc2'), (6, 14, '62dcc2'), (7, 14, '62dcc2')):
            px[x, f] = c(col)
    return bc.terminar(m, raiz, 'Creeper Gelatina', 'Jelly Creeper',
                       (('62dcc2', '2aac94', '188270'), ('bafff2', '0e5244'), dib),
                       ((1.5, 2.2, 2.4), (0, 1.2, 0)),
                       particulas=(('burbuja', bc.anillo((90, 216, 188))), ('gota', bc.gota((36, 168, 142)))))


MOBS = {'atomico': bc.atomico, 'ciego': ciego, 'tarta': tarta, 'matojo': matojo, 'marchito': marchito,
        'enredadera': enredadera, 'gelatina': gelatina}

ORDEN = ('atomico', 'ciego', 'tarta', 'matojo', 'marchito', 'enredadera', 'gelatina')

# Lo que cuenta la ficha de cada uno: el nombre, el original, la idea, las señas, el sitio, la referencia y el centro de
# la cabeza (en bloques) para la foto de cerca.
FICHA = {
    'atomico': bc.FICHA['atomico'],
    'ciego': ('Creeper Ciego', 'Creeper Warden (DEDsafío 3)',
              'El creeper warden del original, mejor hecho: de sculk suave con detalle (manchas oscuras, motitas de '
              'cian), la cara de creeper sin ojos con la boca encendida de cian, y lo del warden encima como una '
              '2.ª capa, no en piezas sueltas.',
              ['<b>Las antenas del warden</b> (sus zarcillos): planas y casi horizontales, abiertas hacia fuera en '
               'tres dedos romos, con las manchas de cian encendidas; tiemblan cuando te oye y con la mecha.',
               '<b>Las costillas de hueso</b> en 2.ª capa (el esternón, las costillas que siguen por los costados y el '
               'espinazo detrás), con el resplandor de las almas entre ellas.',
               'Los dedos de hueso claro en los pies, como los del original.'],
              'cueva', 'ref_warden.png', (0, 1.51, 0.28)),
    'tarta': ('Creeper Tarta', 'Creeper Cake (DEDsafío 3 y 4)',
              'El mismo diseño, con detalle en la textura: el bizcocho dorado con sus poros y migas, la capa de nata '
              'ondulada y la mermelada; el glaseado con su brillo, los fideos rojos y las gotas redondas que caen por '
              'los cantos; el cuerpo de chocolate marmolado con pepitas.',
              ['<b>Un cuello de glaseado</b> que gotea por el pecho; <b>dos cerezas</b> con su brillo junto a la vela.',
               'Con la mecha, la llama se aviva hasta hacerse enorme.'],
              'noche', 'ref_cake.png', (0, 1.51, 0.28)),
    'matojo': ('Creeper Matojo', 'Creeper de Pasto (DEDsafío 4)',
               'Un creeper chiquito y rechoncho hecho de bloque de pasto, como el original, a cuatro patas: el verde '
               'con briznas, las patas con la tierra abajo y la hierba que cuelga sobre ella; la cabeza, cubierta de '
               'césped en 2.ª capa que cuelga en puntas por los lados.',
               ['<b>Matas de hierba</b> planas en la coronilla (como las de vanilla), sin flores.',
                'Sale de la hierba de un salto cuando la rompes, y con la mecha se le eriza la mata.'],
               'noche', 'ref_pasto.png', (0, 0.6, 0.17)),
    'marchito': ('Creeper Marchito', 'Creeper de Wither Rose (DEDsafío 4)',
                 'La rosa marchita hecha creeper, con lo añadido en 2.ª capa: el cuerpo, el tallo negro con fibras, '
                 'con las espinas y las hojas mustias encima; la cabeza, el capullo con sus pétalos de fuera en 2.ª '
                 'capa, la cara honda y el rojo del corazón de la rosa dentro.',
                 ['<b>La rosa marchita</b> abierta encima de la cabeza: el corazón y dos coronas de pétalos gruesos; '
                  'con la mecha se abre del todo.',
                  'Al estallar pone el Wither y siembra rosas marchitas.'],
                 'nether', None, (0, 1.51, 0.28)),
    'enredadera': ('Creeper Enredadera', 'Creeper de Raíz de Azalea (DEDsafío 4)',
                   'Un creeper de corteza de raíz (con sus vetas, nudos y musgo), con lo de la azalea en 2.ª capa: las '
                   'enredaderas que lo rodean y la mata de azalea en flor que le cubre la cabeza y cuelga por los lados.',
                   ['<b>Las lianas</b>, planas y cruzadas como las enredaderas de vanilla, con su flor en la punta: las '
                    'lanza para atraparte y te arrastra; con la mecha, se tensan.'],
                   'noche', None, (0, 1.51, 0.28)),
    'gelatina': ('Creeper Gelatina', 'Creeper de Fluido (DEDsafío 4)',
                 'Como el Slime: el gel translúcido trabajado (el canto más espeso, el brillo, burbujas dentro) y, '
                 'dentro, el cuerpo oscuro con su núcleo que brilla en el pecho; la cabeza, el gel con el núcleo en '
                 'medio, sin cara.',
                 ['<b>El charco</b> de gel que deja a sus pies.',
                  'Con la mecha, el gel tiembla cada vez más.'],
                 'noche', None, (0, 1.51, 0.33)),
}


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    carpeta = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ORDEN)
    hechos = []
    for p in pedidos:
        # El píxel de Minecraft (16 por bloque): 2 píxeles del modelo (al doble, a escala 0,55; el Matojo, chiquito,
        # como las crías de vanilla). El Atómico, como está (a escala 0,75, su píxel de 1 ya es casi el de Minecraft).
        B.TEXEL = None if p == 'atomico' else 2.0
        hechos.append(MOBS[p](raiz))
    B.TEXEL = None
    if carpeta:
        import bestiario_escenas as be
        os.makedirs(carpeta, exist_ok=True)
        fotos = os.environ.get('SIN_FOTOS') != '1'
        secciones = []
        for mm in hechos:
            nombre, original, texto, lineas, sitio, ref, centro = FICHA[mm.id]
            heroe = f'{mm.id}_heroe.jpg'
            cab = f'{mm.id}_cabeza.jpg'
            if fotos:
                be.heroe(mm, sitio, os.path.join(carpeta, heroe))
                be.cabeza(mm, sitio, os.path.join(carpeta, cab), centro, dist=1.4 if mm.id != 'matojo' else 0.8)
            secciones.append((nombre, original, texto, lineas, heroe, cab,
                              ref if ref and os.path.exists(os.path.join(carpeta, ref)) else None))
        grupos = [f'creepers_juntos_{k // 5 + 1}.jpg' for k in range(0, len(hechos), 5)] if len(hechos) > 1 else []
        if fotos and os.environ.get('SIN_GRUPOS') != '1':
            for k, g in zip(range(0, len(hechos), 5), grupos):
                be.fila([(mm, None, 0.0) for mm in hechos[k:k + 5]], 'noche', os.path.join(carpeta, g))
        be.ficha(os.path.join(carpeta, 'creepers_ficha.html'), 'Los creepers, sexta vuelta',
                 'Los diez creepers del DEDsafío con tus correcciones: el Atómico tal cual; lo añadido (costillas, '
                 'orejas, espinas, pétalos, enredaderas, placas) en 2.ª capa o en láminas planas como hace vanilla; '
                 'las texturas suaves pero con detalle; el Latido como su ilustración y el Artillero hecho shulker. Lo '
                 'que se ve es el modelo del juego.',
                 secciones, grupos)


if __name__ == '__main__':
    main()
