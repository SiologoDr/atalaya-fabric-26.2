"""
Los sonidos de los cuatro mini jefes, sintetizados desde cero: nada de vanilla ni de bancos de sonido.

No salen de la misma fisica que los jefes (la roca y el jade de Rajang, el agua de Nerea, el viento de Aeralis, el fuego
de Novilis): cada mini jefe tiene sus INSTRUMENTOS y su forma de sonar, para que no se confundan con ellos.

  MOCTEZUMA, guerrero aguila: la musica de guerra mexica. El huehuetl (el tambor grande, que hace de golpe de tierra) y
    el teponaztli de madera (redobles, escaleras pentatonicas), los ayoyotes (cascabeles de semilla de los tobillos),
    el silbato de la muerte (un grito aspero de aire en una camara), el silbato de aguila, la ocarina de barro, el coro
    de guerreros que grita y el filo de obsidiana que canta ('shiing'). El barro cocido revienta donde caen los
    fragmentos.
  YIATZO, mago del viento: la magia, no el viento. Cuencos cantores (golpeados o frotados, con su batido), el arbol de
    campanas, la armonica de cristal, la flauta de caña con glissandos, el arpa eolica (un acorde fantasma), el tono
    de Shepard que sube sin fin (el ciclon), coros sin palabras, susurros y la reverb al reves (sonidos aspirados).
  ATLAHUA, triton del abismo: lo que lleva el triton, no el agua (eso es de Nerea, y suena sumergida). Su caracola
    (Triton la toca), su tridente que canta como un diapason, las voces del mar (llamadas de orca, silbidos de delfin,
    cantos de ballena y los clics de la ecolocalizacion, que se aceleran cuando fija a su presa), el sonar, el gong que
    cae de tono al hundirse y el tam-tam con redoble para las olas.
  XIUHQUETZAL, fenix: un ave que CANTA. Frases silbadas, trinos, el aleteo de las plumas, chispas de campana, la
    bengala que chisporrotea (no el fuego que ruge), silbidos de cohete, fuegos artificiales que crepitan y coros de luz.

Cada uno suena en su sitio (la reverb): la plaza con sus ecos, la cumbre abierta, el abismo oscuro y el volcan.

Escribe los .ogg (mono, para que se oigan en 3D) en assets/atalaya/sounds/<nombre>/, sus eventos en sounds.json
(<nombre>.<evento>, subtitulo subtitles.atalaya.<nombre>.<evento>) y los subtitulos en es_es y en_us.

Uso: python minijefes_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png] [jefes separados por comas]
"""
import collections
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator

SR = 44100
RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
HOJA = sys.argv[2] if len(sys.argv) > 2 else None
SONIDOS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds')
rng = np.random.default_rng(20261011)
EVENTOS = collections.OrderedDict()
GUARDADOS = []
JEFE = None


# ======================================================================
#  Utilidades (las de los jefes)


# ======================================================================
#  Utilidades (genericas: senales, filtros, envolventes, voces, reverb)
# ======================================================================
def n_(dur):
    return max(1, int(round(dur * SR)))


def t_(dur):
    return np.arange(n_(dur)) / SR


def ruido(dur, color='blanco'):
    n = rng.standard_normal(n_(dur))
    if color == 'rosa':
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        n = signal.lfilter(b, a, n)
    elif color == 'marron':
        n = signal.lfilter([1], [1, -0.995], n)
    return n / (np.std(n) + 1e-12)


def suave(n, fc):
    """Ruido lento (por debajo de fc), de desviacion 1."""
    pre = int(min(3 * SR / fc, 4 * SR))
    x = signal.sosfilt(signal.butter(2, fc, 'lowpass', fs=SR, output='sos'), rng.standard_normal(n + pre))[pre:]
    return x / (np.std(x) + 1e-12)


def _sos(tipo, f, orden=2):
    ny = SR / 2
    if tipo == 'bandpass':
        f = [max(15.0, f[0]), min(ny * 0.95, f[1])]
    else:
        f = min(ny * 0.95, max(15.0, f))
    return signal.butter(orden, f, btype=tipo, fs=SR, output='sos')


def pb(x, f, orden=2):
    return signal.sosfilt(_sos('lowpass', f, orden), x)


def pa(x, f, orden=2):
    return signal.sosfilt(_sos('highpass', f, orden), x)


def bp(x, lo, hi, orden=2):
    return signal.sosfilt(_sos('bandpass', (lo, hi), orden), x)


def resonar(x, f, q):
    b, a = signal.iirpeak(min(f, SR * 0.45), q, fs=SR)
    return signal.lfilter(b, a, x)


def filtro_mov(x, fc, tipo='low', q=0.707, bloque=64):
    """Biquad (RBJ) con la frecuencia moviendose: barridos, formantes, Doppler."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    y = np.empty_like(x)
    zi = np.zeros(2)
    for i in range(0, len(x), bloque):
        f = float(np.clip(fc[i], 20.0, SR * 0.45))
        w = 2 * np.pi * f / SR
        cw, al = np.cos(w), np.sin(w) / (2 * q)
        if tipo == 'low':
            b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        elif tipo == 'high':
            b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        else:
            b = [al, 0.0, -al]
        a = [1 + al, -2 * cw, 1 - al]
        y[i:i + bloque], zi = signal.lfilter(np.array(b) / a[0], np.array(a) / a[0], x[i:i + bloque], zi=zi)
    return y


def curva(n, puntos):
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    if len(xs) == 1:
        return np.full(n, float(ys[0]))
    return PchipInterpolator(xs, ys)(np.linspace(0, 1, n))


def mezclar(*capas):
    capas = [c for c in capas if c is not None and len(c)]
    out = np.zeros(max(len(c) for c in capas))
    for c in capas:
        out[:len(c)] += c
    return out


def en(seg, x):
    return np.concatenate([np.zeros(n_(seg)), x])


def pico(x, a=1.0):
    m = np.max(np.abs(x))
    return x * (a / m) if m > 0 else x


def caida(dur, tau, ataque=0.002, sostener=0.0):
    t = t_(dur)
    e = np.exp(-np.maximum(0.0, t - ataque - sostener) / tau)
    a = n_(ataque)
    e[:a] *= np.linspace(0, 1, a)
    f = max(1, len(e) // 8)
    e[-f:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f))
    return e


def campana_env(dur, p=2.0):
    return np.sin(np.pi * np.linspace(0, 1, n_(dur))) ** p


def ventana(dur, ataque, soltar):
    n = n_(dur)
    e = np.ones(n)
    a, s = min(n, n_(ataque)), min(n, n_(soltar))
    e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    e[n - s:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, s))
    return e


def saturar(x, k=2.0):
    return np.tanh(k * x) / np.tanh(k)


def limitar(x, umbral=0.55):
    y = pico(x)
    m = np.abs(y)
    sobre = m > umbral
    y[sobre] = np.sign(y[sobre]) * (umbral + (1 - umbral) * np.tanh((m[sobre] - umbral) / (1 - umbral)))
    return y


def modos(f, dur, parciales, tau, batido=0.0):
    """Suma de modos que se apagan (los agudos antes), cada uno partido en dos si hay batido."""
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        if f * r < SR * 0.45:
            for d in ((-batido, batido) if batido else (0.0,)):
                s += a * np.sin(2 * np.pi * f * r * (1 + d) * t + rng.uniform(0, 6)) * np.exp(-t / (tau / r ** 0.5))
    a = n_(0.0008)
    s[:a] *= np.linspace(0, 1, a)
    return s


_IRS = {}

def respuesta(cola, oscuro, ecos):
    clave = (round(cola, 2), int(oscuro), ecos)
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro) + 7)
        x = r.standard_normal(len(t))
        h = (pb(x, 500) * np.exp(-6.9 * t / cola) + bp(x, 500, 3000) * np.exp(-6.9 * t / (cola * 0.55)) * 0.75
             + pa(x, 3000) * np.exp(-6.9 * t / (cola * 0.18)) * 0.35)
        h = pb(h, oscuro)
        a = n_(0.03)
        h[:a] *= np.linspace(0, 1, a) ** 2
        ref = np.sqrt(np.mean(h[:n_(0.12)] ** 2))
        for seg, g, claro in {'plaza': ((0.043, 0.7, 7000), (0.079, 0.55, 5500), (0.127, 0.4, 4500), (0.21, 0.28, 3000)),
                              'cumbre': ((0.11, 0.35, 5000), (0.29, 0.25, 3500), (0.55, 0.18, 2500)),
                              'abismo': ((0.06, 0.5, 2500), (0.14, 0.4, 2000), (0.26, 0.3, 1500)),
                              'volcan': ((0.05, 0.6, 6000), (0.12, 0.45, 4000), (0.23, 0.3, 3000))}[ecos]:
            if seg < cola * 0.8:
                i = n_(seg)
                eco = pb(r.standard_normal(n_(0.014)), claro) * np.exp(-t_(0.014) / 0.0035)
                h[i:i + len(eco)] += g * eco * ref * 7
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


SALAS = {'moctezuma': ('plaza', 6500), 'yiatzo': ('cumbre', 8000), 'atlahua': ('abismo', 5000), 'xiuhquetzal': ('volcan', 7000)}

def reverb(x, mezcla=0.25, cola=1.8):
    ecos, oscuro = SALAS[JEFE]
    h = respuesta(cola, oscuro, ecos)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


def boom(f0=60, f1=26, tau=0.25, dur=None):
    """El golpe de presion que cae de tono."""
    dur = dur or tau * 5
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) + 0.25 * np.sin(2 * fase)) * caida(dur, tau, 0.003)


def soplo(dur, f0, f1, q=1.2, silba=0.2, forma=1.3):
    """Algo que corta el aire: una banda de ruido que se mueve (Doppler), con su silbido."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.45, (f0 * f1) ** 0.5 * 1.15), (1, f1)])
    s = filtro_mov(ruido(dur, 'rosa'), f, 'band', q)
    canta = filtro_mov(ruido(dur), f * 1.6, 'band', 22, 32)
    e = campana_env(dur, forma) ** 1.4
    return mezclar(pico(s * e, 1.0), pico(canta * e, silba))


def chasquidos(dur, tasa, lo=800, hi=9000, amp=1.0):
    """Chasquidos sueltos (tasa por segundo, numero o curva)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    exc = np.zeros(n)
    exc[cuando] = rng.uniform(0.2, 1.0, len(cuando)) * rng.choice([-1.0, 1.0], len(cuando))
    nucleo = bp(ruido(0.003), lo, hi) * caida(0.003, 0.0006, 0.0001)
    return amp * signal.fftconvolve(exc, nucleo)[:n]


def garganta(f0, dur, formantes, aspereza=0.5, sub=0.3, jitter=0.03, aliento=0.25, fmax=5000, caos=0.0):
    """Una garganta: pulsos con jitter, subarmonico, tramos caoticos y formantes (pueden ser curvas)."""
    n = n_(dur)
    f0 = np.broadcast_to(np.asarray(f0, dtype=float), (n,))
    f = f0 * (1 + jitter * suave(n, 25)) * (1 + 0.25 * jitter * suave(n, 140))
    fase = 2 * np.pi * np.cumsum(f) / SR
    src = np.zeros(n)
    for k in range(1, int(min(120, fmax / np.max(f))) + 1):
        src += np.sin(k * fase) / k ** 1.1
    src *= 1 + sub * np.sin(fase / 2 + 0.3 * suave(n, 3))
    sd = np.std(src)
    caos = np.broadcast_to(np.asarray(caos, dtype=float), (n,))
    if np.any(caos > 0):
        rasp = ruido(dur, 'rosa') * (0.5 + 0.5 * np.cos(fase)) ** 2
        src = src * (1 - 0.6 * caos) + caos * 2.2 * sd * rasp / (np.std(rasp) + 1e-12)
    src += aliento * sd * ruido(dur, 'rosa') * (0.6 + 0.4 * np.sin(fase))
    out = np.zeros(n)
    for F, bw, g in formantes:
        if np.isscalar(F):
            out += g * resonar(src, F, F / bw)
        else:
            out += g * filtro_mov(src, F, 'band', float(np.mean(F)) / bw)
    return saturar(pico(out), 1.2 + 2.5 * aspereza)


def formantes(vocal, escala=1.0):
    """Formantes de una voz grande: 'a', 'o', 'u', 'e' (escala < 1, mas grande)."""
    tabla = {'a': (700, 1150, 2500, 3300), 'o': (450, 800, 2600, 3300), 'u': (320, 700, 2400, 3200),
             'e': (450, 1900, 2600, 3400)}
    anchos = (110, 130, 180, 250)
    gan = (1.0, 0.7, 0.35, 0.2)
    return tuple((f * escala, w * escala, g) for f, w, g in zip(tabla[vocal], anchos, gan))


def susurro(dur, vocal='o', escala=1.0, mueve=None):
    """Una voz sin cuerdas: aire por formantes (el mago no tiene cara)."""
    n = n_(dur)
    x = ruido(dur, 'rosa')
    out = np.zeros(n)
    for F, bw, g in formantes(vocal, escala):
        if mueve is not None:
            F = F * mueve
            out += g * filtro_mov(x, F, 'band', float(np.mean(F)) / bw)
        else:
            out += g * resonar(x, F, F / bw)
    return out * ventana(dur, dur * 0.2, dur * 0.4)


def burbujas(dur, tasa, fmin=300, fmax=1600, amp=1.0):
    """Burbujas: cada una un seno que se apaga y sube de tono al cerrarse (Minnaert)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(0.2))
    for i in cuando:
        f = np.exp(rng.uniform(np.log(fmin), np.log(fmax)))
        d = min(0.15, 6.0 / f + 0.01)
        tt = t_(d)
        tau = d / 3
        fr = f * (1 + 0.6 * tt / d)
        b = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / tau) * rng.uniform(0.2, 1.0)
        out[i:i + len(b)] += b
    return amp * out[:n]


# ======================================================================
#  Instrumentos de los mini jefes (ninguno sale de la fisica de los jefes)
# ======================================================================
def seno(f, dur, armonicos=((1, 1.0),), vibrato=0.0, vel_vib=5.0):
    """Un tono (f numero o curva) con sus armonicos (pueden ser inarmonicos) y vibrato."""
    n = n_(dur)
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,)).copy()
    if vibrato:
        f *= 1 + vibrato * np.sin(2 * np.pi * vel_vib * t_(dur) + rng.uniform(0, 6))
    fase = 2 * np.pi * np.cumsum(f) / SR
    s = np.zeros(n)
    tope = np.max(f)
    for k, a in armonicos:
        if k * tope < SR * 0.45:
            s += a * np.sin(k * fase)
    return s


def acelerando(desde, hasta, hueco, minimo, factor=0.82):
    """Tiempos de golpes cada vez mas seguidos."""
    out = []
    s = desde
    while s < hasta:
        out.append(s)
        s += hueco
        hueco = max(minimo, hueco * factor)
    return out


def coro_voces(dur, notas, vocal='a', curva_tono=None, aliento=0.35):
    """Un coro sin palabras: una voz clara por nota, cada una algo desafinada y con su vibrato."""
    n = n_(dur)
    capas = []
    for f in notas:
        tono = f * (1 + 0.004 * rng.standard_normal()) * (curva_tono if curva_tono is not None else np.ones(n))
        tono = tono * (1 + 0.006 * np.sin(2 * np.pi * rng.uniform(4.5, 5.8) * t_(dur) + rng.uniform(0, 6)))
        capas.append(pico(garganta(tono, dur, formantes(vocal, 1.0 if f < 300 else 1.25), 0.05, 0.0, 0.004, aliento, 7000), 1.0))
    return mezclar(*capas) * ventana(dur, min(0.3, dur * 0.25), dur * 0.35)


# --- Moctezuma: la musica de guerra mexica ---
def huehuetl(f=62.0, fuerza=1.0, dur=1.2, tau=0.32):
    """El tambor grande de pie: la membrana grave que baja de tono, el golpe de la mano y la caja de madera."""
    t = t_(dur)
    fr = f * (1 + 0.35 * np.exp(-t / 0.05))
    fase = 2 * np.pi * np.cumsum(fr) / SR
    membrana = (np.sin(fase) + 0.4 * np.sin(1.59 * fase) + 0.2 * np.sin(2.14 * fase)) * caida(dur, tau, 0.002)
    mano = bp(ruido(0.06), 200, 2500) * caida(0.06, 0.012, 0.0005)
    caja = resonar(pb(ruido(0.4), 900) * caida(0.4, 0.05), 180, 6)
    return fuerza * mezclar(pico(membrana, 1.0), pico(mano, 0.45), pico(caja, 0.25))


def redoble(dur, f=380.0, tasa=(6, 22), fuerza=1.0):
    """Un redoble de teponaztli (de tasa[0] a tasa[1] golpes por segundo), alternando sus dos lenguetas."""
    n = n_(dur)
    fase = np.cumsum(curva(n, [(0, tasa[0]), (1, tasa[1])])) / SR
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    out = np.zeros(n + n_(0.5))
    for k, i in enumerate(golpes):
        g = teponaztli(f if k % 2 == 0 else f * 0.79, rng.uniform(0.6, 1.0))
        out[i:i + len(g)] += g
    return fuerza * out


def ayoyotes(dur, sacudidas, fuerza=1.0):
    """Los ayoyotes (cascabeles de cascara de semilla) de los tobillos: cada sacudida (inicio, fuerza) es una nube de
    golpecitos huecos y el roce de las semillas."""
    n = n_(dur)
    out = np.zeros(n + n_(0.2))
    for s, a in sacudidas:
        for _ in range(int(rng.integers(12, 22) * fuerza)):
            i = n_(s + abs(rng.normal(0, 0.03)))
            if i >= n:
                continue
            c = modos(rng.uniform(2200, 5200), 0.012, ((1, 1.0), (1.65, 0.5), (2.4, 0.25)), 0.0025) * rng.uniform(0.2, 1.0) * a
            out[i:i + len(c)] += c
        i = n_(s)
        roce = bp(ruido(0.08), 3000, 9000) * campana_env(0.08, 1.0) * a * 0.15
        out[i:i + len(roce)] += roce[:len(out) - i]
    out = out + 0.5 * resonar(out, 1100, 6)
    return out[:n]


def silbato_muerte(dur, f0=1100.0, forma=None, soltar=0.35):
    """El silbato de la muerte (ehecachichtli): el aire que choca en su camara da un grito aspero, casi humano."""
    n = n_(dur)
    k = curva(n, forma) if forma else curva(n, [(0, 0.85), (0.25, 1.05), (0.7, 1.0), (1, 0.8)])
    f = f0 * k * (1 + 0.015 * suave(n, 18))
    x = ruido(dur)
    aspero = 1 + 0.9 * np.abs(suave(n, 60))
    grito = (filtro_mov(x, f, 'band', 9, 32) + 0.7 * filtro_mov(x, f * 2.07, 'band', 7, 32)
             + 0.4 * filtro_mov(x, f * 3.2, 'band', 6, 32)) * aspero
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.abs(suave(n, 25)))
    aire = bp(ruido(dur, 'rosa'), 700, 6000)
    e = ventana(dur, dur * 0.12, dur * soltar)
    return mezclar(pico(grito * e, 1.0), pico(tono * e, 0.3), pico(aire * e, 0.2))


def silbato_aguila(dur=0.9, f0=2200.0):
    """El silbato de barro con forma de aguila: un 'kiii' que sube y cae, y la bolita de dentro que lo hace trinar."""
    n = n_(dur)
    f = f0 * curva(n, [(0, 0.8), (0.15, 1.1), (0.6, 1.0), (1, 0.75)])
    bola = 1 + 0.035 * pb(np.sign(np.sin(2 * np.pi * 24 * t_(dur))), 120)
    s = seno(f * bola, dur, ((1, 1.0), (2, 0.08)))
    so = filtro_mov(ruido(dur), f, 'band', 6, 32)
    e = ventana(dur, 0.03, dur * 0.4)
    return mezclar(pico(s * e, 1.0), pico(so * e, 0.3))


def ocarina(notas, dur_nota=0.35, aliento=0.25):
    """Una ocarina de barro: un tono casi puro con su soplo, ligado de nota en nota."""
    seg = n_(dur_nota)
    f = np.concatenate([np.full(seg, float(x)) for x in notas] + [np.full(n_(0.25), float(notas[-1]))])
    b, a = [0.004], [1, -0.996]
    f = signal.lfilter(b, a, f, zi=signal.lfilter_zi(b, a) * f[0])[0]
    n = len(f)
    dur = n / SR
    e = np.ones(n)
    w = n_(0.04)
    for k in range(1, len(notas)):
        i = k * seg
        e[i - w:i + w] *= 0.55 + 0.45 * np.abs(np.linspace(-1, 1, 2 * w))
    vib = 1 + 0.01 * np.sin(2 * np.pi * 5.2 * np.arange(n) / SR) * np.clip(np.arange(n) / n_(0.3), 0, 1)
    fase = 2 * np.pi * np.cumsum(f * vib) / SR
    s = np.sin(fase) + 0.1 * np.sin(2 * fase) + 0.03 * np.sin(3 * fase)
    so = filtro_mov(ruido(dur), f, 'band', 4, 32)
    v = ventana(dur, 0.06, 0.25)
    return mezclar(pico(s * e * v, 1.0), pico(so * e * v, aliento))


def grito_guerra(silabas, f0=170.0, voces=6):
    """Un grito de guerra a coro: varios guerreros (cada uno con su tono y su retraso) gritan las silabas
    (inicio, duracion, vocal)."""
    capas = []
    for v in range(voces):
        fv = f0 * 2 ** rng.normal(0, 0.06) * (1.5 if v % 3 == 2 else 1.0)
        esc = rng.uniform(0.85, 1.0)
        for s, d, voc in silabas:
            n = n_(d)
            tono = fv * curva(n, [(0, 0.9), (0.2, 1.08), (1, 0.85)])
            g = garganta(tono, d, formantes(voc, esc), 0.55, 0.15, 0.025, 0.35, 5000, 0.1) * ventana(d, 0.02, d * 0.5)
            ja = bp(ruido(0.05), 1000, 4500) * ventana(0.05, 0.005, 0.03)
            capas.append(en(s + rng.uniform(0, 0.03), mezclar(pico(ja, 0.3), en(0.03, g)) * rng.uniform(0.6, 1.0)))
    return mezclar(*capas)


def teponaztli(f=380.0, fuerza=1.0):
    """El tambor de hendidura de madera: dos lengüetas con su tono seco."""
    dur = 0.45
    s = modos(f, dur, ((1, 1.0), (2.7, 0.35), (4.1, 0.15)), 0.08)
    golpe = bp(ruido(0.01), 600, 5000) * caida(0.01, 0.002, 0.0002)
    return fuerza * mezclar(pico(s, 1.0), pico(golpe, 0.4))


def obsidiana(dur=0.8, brillo=1.0):
    """El filo de obsidiana que canta: un 'shiing' de vidrio volcanico (un peine que barre el siseo) y sus modos
    agudos que laten."""
    n = n_(dur)
    x = pa(ruido(dur), 2500) * caida(dur, dur * 0.18, 0.002)
    d = curva(n, [(0, 0.0002), (1, 0.0012)]) * SR
    i = np.arange(n)
    barrido = x + np.interp(i - d, i, x, left=0.0)
    canto = modos(3900 * brillo, dur, ((1, 1.0), (1.34, 0.7), (1.93, 0.45), (2.61, 0.3)), dur * 0.25, 0.005)
    return mezclar(pico(barrido, 0.7), pico(canto, 0.55))


def ceramica(fuerza=1.0, dur=0.9):
    """Una vasija de barro cocido que revienta: el golpe, el 'clonc' corto del barro y los tiestos que caen."""
    golpe = bp(ruido(0.05), 200, 3000) * caida(0.05, 0.008, 0.0005)
    cuerpo = modos(rng.uniform(500, 700), 0.3, ((1, 1.0), (1.83, 0.6), (2.9, 0.4), (4.2, 0.25)), 0.035)
    trozos = mezclar(*[en(0.05 + rng.uniform(0, dur * 0.55) ** 1.5,
                          modos(rng.uniform(900, 2600), 0.08, ((1, 1.0), (1.9, 0.5), (3.1, 0.3)), 0.012) * rng.uniform(0.2, 0.9))
                       for _ in range(int(14 * fuerza))])
    return mezclar(pico(golpe, 0.8), pico(cuerpo, 0.6), pico(trozos, 0.55))


# --- Yiatzo: la magia del viento ---
CUENCO = ((1, 1.0), (2.71, 0.55), (5.15, 0.3), (8.21, 0.15))


def cuenco(f, dur, golpe=1.0, frote=0.0, batido=0.0035):
    """Un cuenco cantor: golpeado (modos largos que laten entre si) y/o frotado (la nota que crece y ondula)."""
    n = n_(dur)
    s = np.zeros(n)
    if golpe:
        s += golpe * pico(modos(f, dur, CUENCO, dur * 0.35, batido), 1.0)
    if frote:
        x = ruido(dur, 'rosa')
        canta = sum(a * resonar(x, f * r, 900) for r, a in CUENCO[:3])
        ondula = 1 + 0.35 * np.sin(2 * np.pi * max(0.5, batido * f * 2) * t_(dur))
        s += frote * pico(canta * ondula * ventana(dur, dur * 0.3, dur * 0.3), 1.0)
    return s


def arbol_campanas(dur, f_alto=9000.0, f_bajo=2500.0, cuantas=24, baja=True):
    """Un arbol de campanas: campanitas de agudo a grave (o al reves), cada vez mas seguidas."""
    capas = []
    for k in range(cuantas):
        x = k / max(1, cuantas - 1)
        f = f_alto * (f_bajo / f_alto) ** (x if baja else 1 - x)
        capas.append(en(dur * x ** 0.75, modos(f * rng.uniform(0.98, 1.02), 0.9, ((1, 1.0), (2.4, 0.3), (4.1, 0.1)), 0.35, 0.002)
                        * (0.5 + 0.5 * rng.random())))
    return mezclar(*capas)


def armonica_cristal(f, dur):
    """La armonica de cristal: copas frotadas, una nota pura que aparece sin golpe y tiembla."""
    s = seno(f, dur, ((1, 1.0), (2, 0.08), (3, 0.03)), 0.003, 5.5)
    roce = resonar(ruido(dur), f, 400)
    return mezclar(pico(s, 1.0), pico(roce, 0.25)) * ventana(dur, dur * 0.3, dur * 0.4)


def flauta(f, dur, aliento=0.3, vib=0.008):
    """Una flauta de caña que sopla el viento: tono con soplo y vibrato (f puede ser curva: glissandos)."""
    n = n_(dur)
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    s = seno(f, dur, ((1, 1.0), (2, 0.25), (3, 0.1)), vib, 5.0)
    so = filtro_mov(ruido(dur), f, 'band', 5, 32)
    e = ventana(dur, min(0.08, dur * 0.3), dur * 0.35)
    return mezclar(pico(s * e, 1.0), pico(so * e, aliento))


def arpa_eolica(dur, f0=110.0, armonicos=range(3, 13)):
    """El arpa eolica: el viento hace cantar sus cuerdas en armonicos que crecen y se apagan solos (un acorde
    fantasma, no un soplo)."""
    n = n_(dur)
    x = ruido(dur, 'rosa')
    out = np.zeros(n)
    for k in armonicos:
        if f0 * k > SR * 0.4:
            break
        a = np.clip(suave(n, 0.5) + 0.2, 0, None) ** 2
        out += resonar(x, f0 * k, 500) * a / k ** 0.3
    return out


def shepard(dur, vueltas=1.5, octavas=7, base=40.0):
    """Un tono de Shepard-Risset: octavas que suben sin fin (el ciclon que nunca deja de crecer)."""
    n = n_(dur)
    pos = np.linspace(0, vueltas, n)
    out = np.zeros(n)
    for k in range(octavas):
        o = (k + pos) % octavas
        a = 0.5 - 0.5 * np.cos(2 * np.pi * o / octavas)
        out += a * np.sin(2 * np.pi * np.cumsum(base * 2 ** o) / SR)
    return out


def aspirar(x, cola=0.8, g=0.6):
    """La reverb al reves antes del sonido: llega aspirado, como un hechizo. Devuelve el soplo y el sonido detras."""
    h = respuesta(cola, 8000, SALAS[JEFE][0])
    y = signal.fftconvolve(x[::-1], h)[::-1]
    return mezclar(pico(y, g), en((len(h) - 1) / SR, x))


# --- Atlahua: el triton (su caracola, su tridente, las voces del mar y el gong) ---
def caracola(dur, f0=196.0, baja=False):
    """La caracola de Triton: un bramido de labios en la concha, con sus armonicos, que al final puede caer."""
    n = n_(dur)
    forma = [(0, 0.95), (0.2, 1.0), (0.6, 0.9), (1, 0.6)] if baja else [(0, 0.9), (0.12, 1.0), (1, 0.97)]
    s = garganta(f0 * curva(n, forma), dur, ((f0 * 2.2, 120, 1.0), (f0 * 4.4, 200, 0.5), (f0 * 6.6, 260, 0.25)),
                 0.2, 0.1, 0.01, 0.3, 3000)
    return s * ventana(dur, 0.12, dur * 0.4)


def clics(dur, tasa, fmin=4000.0, fmax=14000.0):
    """La ecolocalizacion: trenes de clics secos y brillantes (tasa en clics por segundo, numero o curva; cuando se
    acelera hasta zumbar es que ha fijado a su presa)."""
    n = n_(dur)
    fase = np.cumsum(np.broadcast_to(np.asarray(tasa, dtype=float), (n,))) / SR
    out = np.zeros(n + n_(0.01))
    for i in np.nonzero(np.diff(np.floor(fase)) > 0)[0]:
        c = bp(ruido(0.0015), fmin, fmax) * caida(0.0015, 0.0003, 0.00005) * rng.uniform(0.6, 1.0)
        out[i:i + len(c)] += c
    return out[:n]


def silbido_delfin(dur, tono, gorjeo=0.0):
    """Un silbido de delfin: un tono puro muy agudo que se desliza (tono: curva de puntos en Hz)."""
    n = n_(dur)
    f = curva(n, tono) * (1 + gorjeo * np.sin(2 * np.pi * 9 * t_(dur)))
    return seno(f, dur, ((1, 1.0), (2, 0.12))) * ventana(dur, 0.02, dur * 0.3)


def llamada_orca(dur, tono, aspereza=0.4):
    """La llamada de una orca: un tono 'pulsado' (zumbon, lleno de armonicos agudos) que sube y cae de golpe."""
    n = n_(dur)
    v = garganta(curva(n, tono), dur, ((1800, 500, 1.0), (3500, 800, 0.6), (6000, 1200, 0.3)), aspereza, 0.0, 0.006, 0.05, 9000)
    return v * ventana(dur, 0.02, dur * 0.3)


def ballena(dur, tono, aspereza=0.15):
    """El canto de una ballena: un gemido que se desliza (tono: curva de puntos) y se abre al subir."""
    n = n_(dur)
    f = curva(n, tono)
    abre = 0.75 + 0.25 * np.clip((f - f.min()) / (np.ptp(f) + 1e-9), 0, 1)
    fs = ((np.maximum(f * 1.05, 380 * abre), 90, 1.0), (1000 * abre, 160, 0.6), (2300 * abre, 300, 0.25))
    v = garganta(f, dur, fs, aspereza, 0.15, 0.008, 0.12, 3500, 0.0)
    return v * ventana(dur, min(0.15, dur * 0.25), dur * 0.35)


def diapason(f, dur=1.5, fuerza=1.0):
    """El tridente es un diapason: sus puntas dan una nota pura y larga que late (dos puntas casi iguales), con el
    golpe y su modo agudo, que se apaga enseguida."""
    t = t_(dur)
    s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 1.0035 * t)) * np.exp(-t / (dur * 0.4))
    if f * 6.27 < SR * 0.45:
        s += 0.35 * fuerza * np.sin(2 * np.pi * f * 6.27 * t) * np.exp(-t / 0.03)
    s[:n_(0.001)] *= np.linspace(0, 1, n_(0.001))
    golpe = bp(ruido(0.004), 2000, 9000) * caida(0.004, 0.001, 0.0001)
    return mezclar(pico(s, 1.0), pico(golpe, 0.3 * fuerza))


def sonar(f=1500.0, dur=2.5, ecos=3):
    """Un pulso de sonar: un 'ping' puro que se apaga y sus ecos en el fondo, cada vez mas sordos."""
    p = seno(f, 0.6, ((1, 1.0), (2, 0.05))) * caida(0.6, 0.12, 0.003)
    out = np.zeros(n_(dur))
    for k in range(ecos + 1):
        i = n_(k * 0.42)
        e = pb(p, 6000 / (k + 1)) * 0.45 ** k
        out[i:i + len(e)] += e[:len(out) - i]
    return out


GONG = ((1, 1.0), (1.47, 0.7), (1.98, 0.55), (2.44, 0.4), (2.9, 0.3), (3.48, 0.2))


def gong_agua(f=180.0, dur=3.0, baja=0.35, cuando=0.15):
    """Un gong que se hunde en el agua: su nota cae de tono al sumergirse."""
    t = t_(dur)
    k = 1 - baja * (1 - np.exp(-np.maximum(0, t - cuando) / 0.5))
    out = np.zeros(len(t))
    for r, a in GONG:
        fr = f * r * k * (1 + 0.002 * rng.standard_normal())
        out += a * np.sin(2 * np.pi * np.cumsum(fr) / SR + rng.uniform(0, 6)) * np.exp(-t / (dur * 0.35 / r ** 0.4))
    out[:n_(0.001)] *= np.linspace(0, 1, n_(0.001))
    golpe = pb(ruido(0.02), 2000) * caida(0.02, 0.004, 0.0005)
    return mezclar(pico(out, 1.0), pico(golpe, 0.3))


def tamtam(dur, forma, f_bajo=70.0, cuantos=48):
    """Un tam-tam con redoble (el mar que crece): muchos modos de metal que se encienden con los golpes de la maza
    (forma: curva de la fuerza del redoble)."""
    n = n_(dur)
    c = curva(n, forma)
    fase = np.cumsum(np.full(n, 13.0)) / SR
    exc = np.zeros(n)
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    exc[golpes] = c[golpes] * rng.uniform(0.6, 1.0, len(golpes))
    exc = signal.fftconvolve(exc, pb(ruido(0.006), 1500) * caida(0.006, 0.0015, 0.0003))[:n]
    exc += 0.08 * pb(ruido(dur, 'rosa'), 2000) * c
    out = np.zeros(n)
    for k in range(1, cuantos + 1):
        f = f_bajo * k ** 1.35 * rng.uniform(0.97, 1.03)
        if f > 7000:
            break
        out += resonar(exc, f, rng.uniform(150, 400)) / k ** 0.4
    return out


def presion(dur, f=38.0, forma=None):
    """La presion del agua que empuja: un tono muy grave que crece, con agua turbia por encima."""
    n = n_(dur)
    c = curva(n, forma) if forma else campana_env(dur, 1.0)
    fase = 2 * np.pi * np.cumsum(f * (1 + 0.04 * suave(n, 0.7))) / SR
    agua = pb(ruido(dur, 'marron'), 300, 4)
    return mezclar(pico((np.sin(fase) + 0.3 * np.sin(2 * fase)) * c, 1.0), pico(agua * c, 0.6))


# --- Xiuhquetzal: el fenix que canta ---
def trino(dur, f, salto=1.12, vel=16.0):
    """Un trino de pajaro: la nota salta a otra y vuelve muy deprisa (f y vel pueden ser curvas)."""
    n = n_(dur)
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    vel = np.broadcast_to(np.asarray(vel, dtype=float), (n,))
    alt = 0.5 + 0.5 * np.tanh(4 * np.sin(2 * np.pi * np.cumsum(vel) / SR))
    s = seno(f * (1 + (salto - 1) * alt), dur, ((1, 1.0), (2, 0.15), (3, 0.05)))
    return s * (0.55 + 0.45 * alt)


def llamada(notas):
    """El canto del fenix: una frase de notas silbadas (f, duracion, fuerza), cada una con su 'chirp' de entrada."""
    capas = []
    t0 = 0.0
    for f, d, a in notas:
        fr = f * curva(n_(d), [(0, 0.86), (0.18, 1.02), (0.8, 1.0), (1, 0.97)])
        capas.append(en(t0, seno(fr, d, ((1, 1.0), (2, 0.18), (3, 0.06)), 0.01, 9) * ventana(d, 0.012, d * 0.4) * a))
        t0 += d * 0.92
    return mezclar(*capas)


def aleteo_plumas(dur=0.6, fuerza=1.0):
    """Las alas de plumas: el aire que empujan y el temblor rapido de las plumas."""
    n = n_(dur)
    e = campana_env(dur, 0.9)
    aire = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 250), (0.4, 900), (1, 350)]), 'low', 0.9) * e
    tiembla = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 18), (1, 30)])) / SR)) ** 3
    plumas = bp(ruido(dur), 1500, 6000) * tiembla * e ** 1.5
    return mezclar(pico(aire, 1.0), pico(plumas, 0.45 * fuerza))


def chispas(dur, tasa, fmin=5000.0, fmax=11000.0):
    """Chispas magicas: puntitos de campana muy agudos y cortos."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    out = np.zeros(n + n_(0.3))
    for i in np.nonzero(rng.random(n) < tasa / SR)[0]:
        g = modos(rng.uniform(fmin, fmax), 0.25, ((1, 1.0), (2.3, 0.2)), rng.uniform(0.04, 0.1), 0.002) * rng.uniform(0.2, 1.0)
        out[i:i + len(g)] += g
    return out[:n]


def chisporroteo(dur, fuerza=1.0):
    """Una bengala: un siseo fino y muy agudo que chisporrotea (no el fuego que ruge)."""
    n = n_(dur)
    siseo = pa(ruido(dur), 5000) * np.exp(0.7 * suave(n, 35))
    return mezclar(pico(siseo, 0.6), pico(chasquidos(dur, 150 * fuerza, 3500, 12000), 0.8 * min(1.0, fuerza)))


def estrellas(dur, tasa):
    """Las estrellas de un fuego artificial que crepitan: rafagas de estallidos secos y brillantes."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,)) * np.exp(1.2 * suave(n, 8))
    return chasquidos(dur, tasa, 1200, 11000) + 0.5 * resonar(chasquidos(dur, tasa * 0.3, 2000, 8000), 3200, 3)


def silbido_cohete(dur, f0, f1, soplo_=0.3):
    """El silbido de un cohete: un tono que sube (o cae) gritando, con su soplo."""
    n = n_(dur)
    f = curva(n, [(0, f0), (1, f1)])
    s = seno(f, dur, ((1, 1.0), (2, 0.35), (3, 0.12)), 0.006, 30)
    so = filtro_mov(ruido(dur), f, 'band', 3, 32)
    e = ventana(dur, 0.02, dur * 0.2)
    return mezclar(pico(s * e, 1.0), pico(so * e, soplo_))


def estallido_luz(fuerza=1.0, dur=2.5):
    """Un fuego artificial que revienta: el golpe, el destello y las estrellas que crepitan al caer."""
    t = t_(dur)
    golpe = saturar(boom(70, 30, 0.2 * fuerza, dur), 2.2)
    destello = bp(ruido(0.3), 300, 9000) * caida(0.3, 0.04, 0.001)
    crepita = estrellas(dur, 900 * fuerza * np.clip((t - 0.25) / 0.1, 0, 1) * np.exp(-np.maximum(t - 0.25, 0) / (0.5 * fuerza)))
    brillo = chispas(dur, 40 * fuerza * np.exp(-t / 0.8))
    return mezclar(pico(golpe, 0.8), pico(destello, 0.7), pico(crepita, 0.55), pico(brillo, 0.3))


# ======================================================================
#  MOCTEZUMA
# ======================================================================
def moctezuma():
    empezar('moctezuma')
    P = [392.0, 440.0, 523.3, 587.3, 659.3, 784.0, 880.0]
    # Ambiente: los ayoyotes de sus tobillos, una ocarina lejana y un toque de teponaztli.
    for i in range(2):
        d = 4.2
        cas = ayoyotes(d, [(0.4 + i * 0.3, 0.6), (1.9, 0.4), (3.1 - i * 0.4, 0.5)])
        frase = ocarina([P[k] for k in ((2, 3, 1, 0) if i == 0 else (4, 2, 3, 1))], 0.42, 0.3)
        tep = mezclar(teponaztli(380, 0.6), en(0.22, teponaztli(300, 0.45)))
        guardar('ambiente', reverb(mezclar(pico(cas, 0.35), en(0.8, pico(frase, 0.45)), en(2.6 + i * 0.5, pico(tep, 0.3))), 0.35, 2.2),
                i + 1, alto=0.65)
    # Paso: el pie contra la losa y los cascabeles del tobillo.
    for i in range(3):
        golpe = mezclar(pico(huehuetl(70 + 6 * i, 1.0, 0.6, 0.09), 0.8), pico(bp(ruido(0.12, 'rosa'), 80, 600) * caida(0.12, 0.03), 0.4))
        guardar('paso', reverb(mezclar(golpe, pico(ayoyotes(0.4, [(0.0, 1.0), (0.09, 0.45)]), 0.55)), 0.15, 1.0), i + 1, limite=0.5)
    # Herido: la madera del escudo, la obsidiana y un chillido corto del silbato de la muerte.
    for i in range(3):
        guardar('herido', reverb(mezclar(pico(teponaztli(300 + 40 * i, 1.0), 0.7), pico(obsidiana(0.35, 1.0 + 0.1 * i), 0.45),
                                         en(0.03, pico(silbato_muerte(0.32, 1300 + 120 * i), 0.6)),
                                         pico(ayoyotes(0.3, [(0.0, 0.8)]), 0.3)), 0.2, 1.2), i + 1)
    # Muerte: el silbato de la muerte grita y se apaga, el tambor late cada vez mas despacio, cae y la ocarina se despide.
    n = n_(3.0)
    grito = silbato_muerte(3.0, 1150, [(0, 0.9), (0.15, 1.08), (0.5, 0.95), (1, 0.55)]) * curva(n, [(0, 1), (0.6, 0.7), (1, 0.0)])
    latidos = mezclar(*[en(s, huehuetl(48, a, 1.4, 0.3)) for s, a in ((0.2, 0.9), (1.0, 0.75), (1.95, 0.6), (3.1, 0.45))])
    cae = mezclar(en(2.4, huehuetl(36, 1.0, 2.0, 0.45)), en(2.4, pico(ayoyotes(0.8, [(0.0, 1.0), (0.12, 0.6), (0.3, 0.3)]), 0.6)))
    guardar('muerte', reverb(mezclar(pico(grito, 0.6), pico(latidos, 0.8), pico(cae, 0.9), en(3.2, pico(ocarina([P[2], P[1], P[0] * 0.75], 0.6, 0.35), 0.3))),
                             0.35, 2.6))
    guardar('inmune', reverb(mezclar(pico(obsidiana(0.6, 1.1), 0.8), pico(teponaztli(420, 0.8), 0.5)), 0.25, 1.4), techo=-12)
    # Despertar: los tambores empiezan y se aceleran, la ocarina sube y los silbatos llaman a la guerra.
    d = 4.8
    golpes = acelerando(0.2, 3.6, 0.75, 0.2)
    tambores = mezclar(*[en(s, huehuetl(55, 0.5 + 0.5 * s / d, 1.2, 0.3)) for s in golpes])
    cas = ayoyotes(d, [(s, 0.5) for s in golpes])
    guardar('despertar', reverb(mezclar(pico(tambores, 0.8), en(1.6, pico(redoble(2.2, 380, (4, 18), 0.6), 0.4)),
                                        en(0.6, pico(ocarina([P[0], P[1], P[2], P[4], P[5]], 0.3, 0.25), 0.35)),
                                        en(3.4, mezclar(pico(silbato_aguila(1.2, 2300), 0.6), pico(silbato_muerte(1.4, 1150), 0.5))), pico(cas, 0.3)), 0.3, 2.4))
    # Arranca el arma del suelo: la tierra que suelta y la obsidiana que sale cantando.
    n = n_(0.8)
    tierra = pb(ruido(0.8, 'marron'), 400) * curva(n, [(0, 0), (0.3, 1), (1, 0)])
    guardar('arranca', reverb(mezclar(pico(tierra, 0.5), en(0.25, pico(obsidiana(0.9, 0.9), 0.8)), pico(huehuetl(90, 0.6, 0.5, 0.08), 0.4),
                                      en(0.25, pico(ayoyotes(0.4, [(0.0, 0.8)]), 0.35))), 0.25, 1.6))
    # El macuahuitl contra el chimalli: cuero, madera, obsidiana y cascabeles.
    guardar('choque', reverb(mezclar(pico(huehuetl(130, 1.0, 0.5, 0.12), 0.8), pico(teponaztli(250, 1.0), 0.6), pico(obsidiana(0.7, 1.0), 0.55),
                                     pico(ayoyotes(0.4, [(0.0, 1.0)]), 0.35)), 0.3, 1.8))
    # El grito de guerra: un coro de guerreros ("¡ja, ja, joo!") con el tambor y el silbato del aguila.
    silabas = [(0.0, 0.32, 'a'), (0.42, 0.32, 'a'), (0.84, 0.75, 'o')]
    tambor = mezclar(*[en(s, huehuetl(55, 1.0, 1.2, 0.3)) for s, _, _ in silabas])
    guardar('grito', reverb(mezclar(pico(grito_guerra(silabas, 170, 6), 0.9), pico(tambor, 0.7), en(1.0, pico(silbato_aguila(1.1, 2300), 0.5))),
                            0.35, 2.6))
    # El cartel: los tambores de guerra, los ayoyotes, el silbato de aguila y el de la muerte detras.
    ritmo = mezclar(*[en(s, huehuetl(58, a)) for s, a in ((0, 1.0), (0.32, 0.6), (0.64, 1.0), (0.8, 0.5), (0.96, 0.9))],
                    *[en(s, teponaztli(f, 0.6)) for s, f in ((0.16, 380), (0.48, 300), (0.72, 380), (0.88, 300))])
    guardar('cartel', reverb(mezclar(pico(ritmo, 0.9), pico(ayoyotes(2.0, [(s, 0.6) for s in (0, 0.32, 0.64, 0.96)]), 0.35),
                                     en(1.1, pico(silbato_aguila(1.4, 2200), 0.5)), en(1.15, pico(silbato_muerte(1.2, 1250), 0.25))), 0.3, 2.6),
            alto=0.8)
    # Corte: el tajo que corta el aire y el filo de obsidiana que canta.
    for i in range(2):
        guardar('corte', reverb(mezclar(pico(soplo(0.4, 350, 2000, 1.3, 0.2), 0.8), en(0.08, pico(obsidiana(0.6, 1.0 + 0.08 * i), 0.55))),
                                0.2, 1.2), i + 1)
    guardar('corte_golpe', reverb(mezclar(pico(huehuetl(65, 1.0, 1.0, 0.18), 0.8), pico(teponaztli(280, 1.0), 0.5), pico(obsidiana(0.9, 1.15), 0.7),
                                          pico(ceramica(0.6), 0.4)), 0.25, 1.6), limite=0.55)
    guardar('salto', reverb(mezclar(pico(soplo(0.7, 200, 900, 1.0, 0.1), 0.8), pico(ayoyotes(0.5, [(0.0, 1.0), (0.1, 0.5)]), 0.5),
                                    en(0.1, pico(silbato_aguila(0.6, 2000), 0.45))), 0.2, 1.2))
    # El Terremoto: cae del cielo y tiene que imponer (Juan: "cuando cae del cielo debe de sonar imponente"). El
    # chasquido seco del impacto, una presion enorme que baja de tono, el tambor gigante y su eco en la tierra, el
    # barro que revienta, el redoble que se frena, la avalancha de cascabeles y el silbato de la muerte; cola larga.
    d = 4.2
    impacto = mezclar(pico(bp(ruido(0.09), 60, 7000) * caida(0.09, 0.012, 0.0004), 1.0),
                      pico(saturar(boom(52, 17, 0.7, d), 2.8), 1.0),
                      pico(huehuetl(30, 1.0, d, 0.9), 0.9), pico(teponaztli(150, 1.0), 0.45),
                      pico(ceramica(2.5, 2.2), 0.4))
    guardar('terremoto', reverb(mezclar(pico(impacto, 1.0), en(0.32, pico(huehuetl(26, 0.8, 3.2, 0.9), 0.6)),
                                        en(0.1, pico(redoble(2.8, 260, (26, 6), 0.8), 0.4)),
                                        pico(ayoyotes(2.4, [(k * 0.07, 1 - k * 0.06) for k in range(14)]), 0.4),
                                        en(0.05, pico(silbato_muerte(2.0, 900), 0.3))), 0.4, 3.6), limite=0.42)
    # Los pinchos de jade: una escalera de madera que sube (pentatonica) y la obsidiana arriba.
    for i in range(2):
        escala = [190, 226, 254, 302, 340, 380, 452, 508]
        sube = mezclar(*[en(k * 0.045, teponaztli(f * (1 + 0.03 * i), 0.5 + 0.06 * k)) for k, f in enumerate(escala)])
        guardar('pinchos', reverb(mezclar(pico(huehuetl(80, 1.0, 0.7, 0.12), 0.6), pico(sube, 0.8), en(0.33, pico(obsidiana(0.8, 1.2), 0.6))),
                                  0.25, 1.8), i + 1)
    # La Tormenta de Obsidiana: silbatos de la muerte que giran, destellos de obsidiana y el redoble que crece.
    d = 4.0
    n = n_(d)
    gira = 1 + 0.5 * np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 0.8), (1, 2.5)])) / SR)
    silbos = mezclar(*[en(s, silbato_muerte(2.2, f, [(0, 0.8), (0.5, 1.15), (1, 0.85)]) * 0.7) for s, f in ((0.0, 900), (0.9, 1250), (1.7, 1100))])
    brillos = mezclar(*[en(rng.uniform(0, d - 0.5), obsidiana(0.5, rng.uniform(0.9, 1.4)) * rng.uniform(0.2, 0.6)) for _ in range(14)])
    redob = redoble(d, 340, (5, 26), 1.0)
    redob = redob * curva(len(redob), [(0, 0.2), (1, 1.0)])
    guardar('tormenta', reverb(mezclar(pico(silbos[:n] * gira[:len(silbos[:n])], 0.6), pico(brillos, 0.35), pico(redob, 0.5)), 0.3, 2.4))
    # El fragmento que cae: el silbato que baja de tono.
    n = n_(1.0)
    guardar('fragmento', reverb(pico(silbato_muerte(1.0, 1500, [(0, 1.1), (1, 0.5)], 0.08) * curva(n, [(0, 0.2), (1, 1.0)]), 1.0), 0.25, 1.6))
    for i in range(2):
        guardar('fragmento_golpe', reverb(mezclar(pico(huehuetl(48, 1.0, 1.4, 0.25), 0.8), pico(ceramica(1.0), 0.6),
                                                  pico(obsidiana(0.7, 1.2 + 0.1 * i), 0.45), pico(saturar(boom(70, 30, 0.15), 2), 0.4)),
                                          0.25, 1.8), i + 1, limite=0.55)
    d = 3.4
    guardar('erupcion', reverb(mezclar(pico(huehuetl(30, 1.0, d, 0.7), 1.0), pico(saturar(boom(55, 22, 0.5, d), 2.0), 0.6),
                                       pico(ceramica(2.0, 1.5), 0.4), pico(ayoyotes(1.5, [(k * 0.06, 1 - k * 0.07) for k in range(12)]), 0.4),
                                       en(0.15, pico(silbato_aguila(1.4, 2000), 0.4)), en(0.05, pico(silbato_muerte(1.6, 950), 0.35))), 0.35, 3.0),
            limite=0.5)


# ======================================================================
#  YIATZO
# ======================================================================
def yiatzo():
    empezar('yiatzo')
    # Ambiente: el orbe zumba como un cuenco frotado, un arbol de campanas lejano y un susurro al reves.
    for i in range(2):
        d = 4.5
        voz = susurro(1.4, 'u', 1.1)[::-1]
        guardar('ambiente', reverb(mezclar(pico(cuenco(392 + 49 * i, d, 0.0, 1.0), 0.5), en(1.5 + i, pico(arbol_campanas(1.2, 8000, 3500, 10), 0.2)),
                                          en(2.4 - 0.8 * i, pico(voz, 0.25))), 0.4, 2.6), i + 1, alto=0.6)
    # Herido: dos cuencos que chocan (un tritono) y el aliento que se le escapa.
    for i in range(3):
        f = 520 + 40 * i
        guardar('herido', reverb(mezclar(pico(cuenco(f, 0.9), 0.6), pico(cuenco(f * 1.414, 0.9), 0.45), pico(susurro(0.4, 'a', 1.3), 0.5)),
                                 0.3, 1.6), i + 1)
    # Muerte: el coro cae de tono y se apaga, las campanas caen despacio y el orbe se calla.
    d = 3.2
    n = n_(d)
    voces = coro_voces(d, [262, 330, 392], 'o', curva(n, [(0, 1.0), (1, 0.55)])) * curva(n, [(0, 1), (1, 0)])
    guardar('muerte', reverb(mezclar(pico(voces, 0.6), en(0.4, pico(arbol_campanas(2.5, 7000, 1800, 18), 0.35)),
                                     pico(cuenco(392, d, 0.0, 1.0) * curva(n, [(0, 1), (1, 0)]), 0.4), en(2.6, pico(boom(50, 25, 0.5), 0.4))),
                             0.45, 3.0))
    guardar('inmune', reverb(mezclar(pico(armonica_cristal(1318.5, 0.8), 0.8), pico(chispas(0.5, 30, 6000, 10000), 0.3)), 0.3, 1.6), techo=-12)
    # Despertar: el soplo aspirado hasta un cuenco enorme, el arpa eolica que crece, la flauta y las campanas que suben.
    d = 5.0
    n = n_(d)
    guardar('despertar', reverb(mezclar(pico(aspirar(cuenco(196, 4.0, 1.0, 0.6), 1.0, 0.6), 0.8),
                                        pico(arpa_eolica(d, 98, range(3, 12)) * curva(n, [(0, 0), (0.4, 0.5), (1, 1.0)]), 0.4),
                                        en(2.6, pico(flauta(curva(n_(2.0), [(0, 523), (0.6, 784), (1, 1046)]), 2.0, 0.35), 0.4)),
                                        en(3.3, pico(arbol_campanas(1.5, 9000, 3000, 16, False), 0.3))), 0.4, 2.8))

    # Las losas de glifos giran: cada una pasa zumbando (un tono grave con Doppler) por el aire.
    def losa(f):
        dl = 0.7
        m = n_(dl)
        fr = f * curva(m, [(0, 1.08), (1, 0.92)])
        s = seno(fr, dl, ((1, 1.0), (2, 0.4), (3, 0.2))) * campana_env(dl, 1.5)
        aire = filtro_mov(ruido(dl, 'rosa'), fr * 6, 'band', 2) * campana_env(dl, 2)
        return mezclar(pico(s, 1.0), pico(aire, 0.4))
    guardar('losas', reverb(mezclar(*[en(k * 0.16, losa(130 * 2 ** (k / 5)) * 0.7) for k in range(5)],
                                    en(0.1, pico(cuenco(262, 1.5, 0.0, 1.0), 0.3))), 0.35, 2.0))
    # El grito del mago: un coro con susurros y el arpa eolica.
    d = 2.4
    n = n_(d)
    coro = coro_voces(d, [220, 277, 330, 440], 'a', curva(n, [(0, 0.92), (0.3, 1.0), (1, 1.04)]))
    susurros = mezclar(*[pico(susurro(d, v, e), 0.5) for v, e in (('a', 1.0), ('o', 1.26), ('u', 1.5))])
    guardar('grito', reverb(mezclar(pico(coro, 0.8), pico(susurros, 0.5), pico(arpa_eolica(d, 110, range(4, 12)) * ventana(d, 0.3, 1.0), 0.3)),
                            0.45, 3.0))
    guardar('golpe', reverb(mezclar(pico(cuenco(165, 2.2), 0.8), pico(cuenco(660, 1.2), 0.4), pico(boom(80, 40, 0.12), 0.45),
                                    pico(arbol_campanas(0.6, 9000, 4000, 8), 0.3)), 0.4, 2.4))
    # El cartel: una melodia de armonica de cristal, el arbol de campanas y el acorde del arpa eolica.
    mel = mezclar(*[en(k * 0.45, armonica_cristal(f, 1.6)) for k, f in enumerate((659.3, 784.0, 987.8))])
    guardar('cartel', reverb(mezclar(pico(mel, 0.7), pico(arbol_campanas(1.4, 9000, 2500, 16), 0.35),
                                     pico(arpa_eolica(2.6, 82.4, range(3, 10)) * ventana(2.6, 0.5, 1.0), 0.35)), 0.45, 3.0), alto=0.8)
    # La Rafaga: la flauta que sube de golpe ('fwiip'), el soplo y unas campanitas al final.
    for i in range(2):
        n = n_(0.5)
        fw = flauta(curva(n, [(0, 600 + 80 * i), (1, 2400 + 200 * i)]), 0.5, 0.6)
        guardar('rafaga', reverb(mezclar(pico(fw, 0.8), pico(soplo(0.45, 500, 3000, 1.6, 0.0), 0.6),
                                         en(0.35, pico(arbol_campanas(0.4, 10000, 5000, 6), 0.25))), 0.3, 1.6), i + 1)
    # La cuchilla: un 'zing' de cristal que cae de tono.
    n = n_(0.6)
    zing = seno(curva(n, [(0, 3200), (1, 1900)]), 0.6, ((1, 1.0), (2.71, 0.3))) * caida(0.6, 0.15, 0.002)
    guardar('cuchilla', reverb(mezclar(pico(zing, 0.8), pico(soplo(0.25, 3000, 900, 2.0, 0.0), 0.5), pico(cuenco(1046.5, 0.6), 0.3)), 0.25, 1.4))
    n = n_(1.2)
    guardar('tormenta', reverb(mezclar(pico(shepard(1.2, 0.8) * curva(n, [(0, 0.1), (1, 1.0)]), 0.7),
                                       pico(arpa_eolica(1.2, 130, range(3, 10)) * curva(n, [(0, 0), (1, 1)]), 0.4)), 0.35, 1.8))
    # El estallido: un acorde de cuencos golpeados, el golpe grave, las campanas que caen y el aire que se va.
    acorde = mezclar(*[cuenco(f, 2.5) for f in (196, 247, 294, 392)])
    guardar('estallido', reverb(mezclar(pico(acorde, 0.8), pico(saturar(boom(55, 25, 0.3), 2), 0.6), pico(arbol_campanas(1.5, 10000, 2500, 20), 0.35),
                                        pico(soplo(1.2, 1500, 250, 0.8, 0.0), 0.45)), 0.4, 2.8), limite=0.5)
    # El ciclon: el tono de Shepard que sube sin fin, el arpa eolica que gira, susurros y el cuenco grave.
    d = 5.0
    n = n_(d)
    gira = 1 + 0.45 * np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 0.5), (1, 2.2)])) / SR)
    sube = shepard(d, 2.0) * curva(n, [(0, 0.0), (0.3, 0.7), (1, 1.0)])
    arpa = arpa_eolica(d, 73.4, range(3, 14)) * gira * curva(n, [(0, 0.2), (1, 1.0)])
    guardar('ciclon', reverb(mezclar(pico(sube, 0.6), pico(arpa, 0.6), pico(susurro(d, 'u', 1.2) * gira, 0.3), pico(cuenco(98, d, 0.0, 1.0), 0.4)),
                             0.35, 2.4))
    acorde = mezclar(*[cuenco(f, 3.0) for f in (147, 196, 247, 294, 370)])
    guardar('ciclon_estalla', reverb(mezclar(pico(saturar(boom(48, 22, 0.4), 2), 0.8), pico(acorde, 0.8), pico(arbol_campanas(2.0, 11000, 2000, 28), 0.4),
                                             pico(soplo(1.6, 1200, 200, 0.7, 0.0), 0.5)), 0.45, 3.0), limite=0.5)


# ======================================================================
#  ATLAHUA
# ======================================================================
def atlahua():
    empezar('atlahua')
    # Ambiente: las voces del mar a lo lejos (una orca, un delfin, una ballena), clics sueltos y un ping de sonar.
    for i in range(2):
        d = 4.5
        orca = llamada_orca(0.9, [(0, 900), (0.3, 1400), (1, 1000)] if i == 0 else [(0, 1200), (0.6, 800), (1, 950)], 0.3)
        delfin = silbido_delfin(0.7, [(0, 7000), (0.5, 10500), (1, 8500)], 0.02)
        guardar('ambiente', reverb(pb(mezclar(en(0.4 + i, pico(orca, 0.35)), en(2.0 - i * 0.6, pico(delfin, 0.2)),
                                              en(1.2, pico(ballena(2.0, [(0, 180), (0.4, 260), (1, 150)]), 0.3)),
                                              pico(clics(d, 4 * campana_env(d, 2.0) + 0.5), 0.15),
                                              en(3.0, pico(sonar(1250 + 150 * i, 1.5, 2), 0.2))), 7000), 0.4, 2.6), i + 1, alto=0.65)
    # Paso: el golpe del pie, la carne mojada y el tridente que vibra un poco.
    for i in range(3):
        golpe = mezclar(pico(boom(70, 32, 0.12), 0.7), pico(bp(ruido(0.2, 'rosa'), 60, 500) * caida(0.2, 0.05), 0.5))
        n = n_(0.25)
        carne = filtro_mov(ruido(0.25, 'rosa'), curva(n, [(0, 1600), (1, 280)]), 'band', 3.0) * caida(0.25, 0.06, 0.004)
        guardar('paso', reverb(mezclar(golpe, pico(carne, 0.4), en(0.02, pico(diapason(880 + 60 * i, 0.6, 0.4), 0.12))), 0.2, 1.2), i + 1,
                limite=0.5)
    # Herido: un chillido de orca, el gong y unos clics.
    for i in range(3):
        grito = llamada_orca(0.45, [(0, 1100 + 100 * i), (0.3, 1700 + 100 * i), (1, 900)], 0.6)
        guardar('herido', reverb(mezclar(pico(grito, 0.8), pico(gong_agua(420 + 30 * i, 0.8, 0.15, 0.05), 0.4), pico(clics(0.3, 60), 0.2)),
                                 0.3, 1.6), i + 1)
    # Muerte: la llamada que cae, el lamento de la ballena, la caracola que se apaga, el gong que se hunde y un ultimo
    # sonar sin respuesta.
    orca = llamada_orca(2.2, [(0, 1400), (0.3, 1100), (1, 500)], 0.5) * curva(n_(2.2), [(0, 1), (1, 0.3)])
    lamento = ballena(3.0, [(0, 220), (0.3, 260), (1, 70)]) * curva(n_(3.0), [(0, 1), (1, 0.2)])
    guardar('muerte', reverb(mezclar(pico(orca, 0.9), en(0.6, pico(lamento, 0.5)), en(1.4, pico(caracola(2.4, 130, True), 0.45)),
                                     en(2.6, pico(gong_agua(110, 3.0, 0.4, 0.1), 0.6)), en(3.4, pico(sonar(900, 3.0, 4), 0.2))), 0.4, 3.0))
    guardar('inmune', reverb(mezclar(pico(diapason(1318.5, 1.0), 0.8), pico(sonar(2200, 1.0, 1), 0.3)), 0.3, 1.4), techo=-12)
    # Despertar: el sonar que se acelera, el tam-tam que crece, una orca, la caracola dos veces y el gong que se hunde.
    d = 5.0
    pings = mezclar(*[en(s, sonar(1400, 1.2, 1) * (0.4 + 0.6 * s / d)) for s in acelerando(0.2, 2.6, 0.8, 0.25)])
    llamadas = mezclar(en(2.0, caracola(1.2, 147)), en(3.2, caracola(1.8, 196)))
    guardar('despertar', reverb(mezclar(pico(pings, 0.5), pico(llamadas, 0.7),
                                        en(1.2, pico(llamada_orca(1.0, [(0, 700), (0.5, 1500), (1, 1300)], 0.4), 0.6)),
                                        pico(tamtam(d, [(0, 0), (0.6, 0.6), (1, 0.2)]), 0.35), en(3.2, pico(gong_agua(140, 2.6, 0.35, 0.1), 0.5))),
                                0.4, 2.8))
    # El rugido del rey del mar: la caracola grave a dos voces (una quinta) y el grito de una orca encima.
    d = 3.0
    guardar('rugido', reverb(mezclar(pico(caracola(d, 110), 0.8), pico(caracola(d, 165), 0.5),
                                     en(0.1, pico(llamada_orca(1.6, [(0, 900), (0.2, 1600), (0.7, 1450), (1, 800)], 0.7), 0.9)),
                                     pico(boom(45, 25, 0.4), 0.4)), 0.4, 3.0))
    guardar('clava', reverb(mezclar(pico(saturar(boom(65, 28, 0.2), 2), 0.7), pico(gong_agua(160, 2.4, 0.35, 0.08), 0.8),
                                    pico(diapason(660, 2.0, 1.0), 0.5), pico(clics(0.4, curva(n_(0.4), [(0, 300), (1, 30)])), 0.3)), 0.35, 2.4))
    # El cartel: la caracola en dos notas, delfines y el tam-tam.
    d = 2.8
    fanfarria = mezclar(caracola(0.9, 147), en(0.7, caracola(1.8, 220)))
    delfines = mezclar(*[en(0.9 + k * 0.25, silbido_delfin(0.5, [(0, 6000 + 800 * k), (1, 9500 + 600 * k)])) for k in range(3)])
    guardar('cartel', reverb(mezclar(pico(fanfarria, 0.9), pico(delfines, 0.45), pico(tamtam(d, [(0, 0.3), (0.3, 1.0), (1, 0.0)]), 0.3)),
                             0.45, 3.0), alto=0.8)
    # La Estocada: los clics que se aceleran (ha fijado a su presa), el empuje y el tridente que canta.
    for i in range(2):
        n = n_(0.6)
        empuje = filtro_mov(ruido(0.6, 'rosa'), curva(n, [(0, 300), (0.4, 1800), (1, 500)]), 'band', 1.2) * campana_env(0.6, 1.0)
        fija = clics(0.3, curva(n_(0.3), [(0, 40), (1, 400)]))
        guardar('estocada', reverb(mezclar(pico(fija, 0.4), en(0.2, pico(empuje, 0.7)), en(0.3, pico(diapason(988 + 110 * i, 1.4, 1.0), 0.6))),
                                   0.3, 1.6), i + 1)
    guardar('golpe', reverb(mezclar(pico(saturar(boom(55, 22, 0.35, 2.0), 2.2), 1.0), pico(gong_agua(90, 2.8, 0.4, 0.06), 0.7),
                                    pico(diapason(523, 2.2, 1.0), 0.4), pico(clics(0.6, curva(n_(0.6), [(0, 500), (1, 20)])), 0.3)),
                            0.4, 2.6), limite=0.5)
    # Las Olas del Abismo: un redoble de tam-tam que crece y se va, delfines que suben con la ola y la caracola grave.
    for i in range(2):
        d = 2.2
        n = n_(d)
        forma = [(0, 0.1), (0.55, 1.0), (1, 0.0)]
        silbos = mezclar(*[silbido_delfin(d, [(0, f), (0.55, f * 1.5), (1, f * 0.9)]) for f in (4200 + 300 * i, 5300, 6400 - 200 * i)])
        guardar('ola', reverb(mezclar(pico(tamtam(d, forma, 60 + 8 * i), 0.9), pico(silbos * curva(n, forma), 0.25),
                                      pico(caracola(d, 98 + 6 * i) * curva(n, forma), 0.4)), 0.35, 2.2), i + 1)
    # El Tsunami: el tam-tam que crece sin parar, la caracola que sube nota a nota, orcas y la presion.
    d = 5.0
    caracolas = mezclar(*[en(s, caracola(1.3, f)) for s, f in ((0.6, 110), (1.8, 131), (3.0, 147), (3.9, 165))])
    orcas = mezclar(*[en(s, llamada_orca(1.0, [(0, 700 + 150 * k), (0.6, 1500 + 150 * k), (1, 1300 + 150 * k)], 0.4))
                      for k, s in enumerate((1.0, 2.2, 3.4))])
    guardar('tsunami', reverb(mezclar(pico(tamtam(d, [(0, 0.05), (0.75, 1.0), (1, 1.0)], 55), 0.9), pico(caracolas, 0.6), pico(orcas, 0.5),
                                      pico(presion(d, 30, [(0, 0.05), (0.75, 1), (1, 1)]), 0.4)), 0.4, 2.8))
    d = 3.0
    guardar('tsunami_rompe', reverb(mezclar(pico(saturar(boom(48, 20, 0.45, d), 2.2), 1.0), pico(gong_agua(70, d, 0.45, 0.05), 0.7),
                                            pico(tamtam(d, [(0, 1.0), (0.1, 0.8), (1, 0.0)], 50), 0.6),
                                            pico(clics(1.2, curva(n_(1.2), [(0, 600), (1, 10)])), 0.3),
                                            en(0.2, pico(llamada_orca(1.4, [(0, 1600), (0.3, 1900), (1, 700)], 0.6), 0.6))), 0.45, 3.0),
            limite=0.5)


# ======================================================================
#  XIUHQUETZAL
# ======================================================================
def xiuhquetzal():
    empezar('xiuhquetzal')
    P = [880.0, 987.8, 1174.7, 1318.5, 1480.0, 1760.0, 1975.5, 2349.3]
    # Ambiente: una bengala que chisporrotea, chispas y una frase de su canto.
    for i in range(2):
        d = 4.0
        canto = llamada([(P[k], 0.18, 1.0) for k in ((4, 5, 3, 7) if i == 0 else (2, 4, 5, 4, 6))])
        guardar('ambiente', reverb(mezclar(pico(chisporroteo(d, 0.6) * ventana(d, 0.8, 1.2), 0.35), en(1.0 + i * 0.6, pico(canto, 0.35)),
                                          pico(chispas(d, 3), 0.2)), 0.35, 2.2), i + 1, alto=0.6)
    for i in range(3):
        guardar('aleteo', reverb(mezclar(pico(aleteo_plumas(0.6, 1.0), 1.0), pico(chispas(0.6, 25), 0.3),
                                         pico(chisporroteo(0.6, 1.0) * campana_env(0.6, 1.2), 0.25)), 0.25, 1.4), i + 1)
    # Herido: un graznido corto que cae y unos estallidos.
    for i in range(3):
        n = n_(0.35)
        grazna = seno(curva(n, [(0, 2600 + 150 * i), (0.3, 3100 + 150 * i), (1, 1500)]), 0.35, ((1, 1.0), (2, 0.4), (3, 0.2))) * ventana(0.35, 0.01, 0.15)
        guardar('herido', reverb(mezclar(pico(grazna, 0.8), pico(estrellas(0.4, 300 * np.exp(-t_(0.4) / 0.08)), 0.5)), 0.25, 1.4), i + 1)
    # Muerte: su canto cae y se frena, el coro baja y se apaga, la bengala se consume y caen las ultimas estrellas.
    d = 3.6
    n = n_(d)
    canto = llamada([(P[7], 0.25, 1.0), (P[6], 0.28, 0.9), (P[4], 0.32, 0.8), (P[3], 0.4, 0.7), (P[1], 0.55, 0.5), (P[0] * 0.75, 0.9, 0.35)])
    coro = coro_voces(d, [587.3, 740.0, 880.0], 'a', curva(n, [(0, 1), (1, 0.7)])) * curva(n, [(0, 0.0), (0.2, 1), (1, 0)])
    guardar('muerte', reverb(mezclar(pico(canto, 0.7), pico(coro, 0.5), pico(chisporroteo(d, 1.0) * curva(n, [(0, 1), (1, 0)]), 0.25),
                                     en(2.4, pico(estrellas(1.0, 200 * np.exp(-t_(1.0) / 0.3)), 0.35))), 0.4, 2.8))
    guardar('inmune', reverb(mezclar(pico(chispas(0.5, 40), 0.7), pico(seno(2637, 0.6, ((1, 1.0), (2.4, 0.2))) * caida(0.6, 0.15), 0.5)), 0.25, 1.2),
            techo=-12)
    # Despertar: el capullo late, sube un silbido con el coro y renace de golpe (1,8 s) en un fuego artificial y un trino.
    d = 4.0
    n = n_(d)
    late = mezclar(*[en(k * 0.45, boom(55, 38, 0.12) * (0.4 + 0.1 * k)) for k in range(4)])
    coro = coro_voces(d, [440, 554.4, 659.3, 880], 'a') * curva(n, [(0, 0), (0.45, 0.7), (0.5, 1.0), (1, 0.3)])
    guardar('despertar', reverb(mezclar(pico(late, 0.45), en(0.2, pico(silbido_cohete(1.6, 600, 2400, 0.4), 0.4)), pico(coro, 0.5),
                                        en(1.8, pico(estallido_luz(1.0), 1.0)), en(2.3, pico(trino(1.0, 1760, 1.12, 18) * ventana(1.0, 0.05, 0.4), 0.45))),
                                0.35, 2.8), limite=0.5)
    # El canto de guerra del fenix: un grito que se eleva trinando, con su octava grave.
    d = 2.0
    n = n_(d)
    f = curva(n, [(0, 1100), (0.15, 1760), (0.45, 1975), (0.7, 1760), (1, 1318)])
    guardar('chillido', reverb(mezclar(pico(trino(d, f, 1.06, 11) * ventana(d, 0.04, 0.6), 1.0),
                                       pico(seno(f / 2, d, ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.2))) * ventana(d, 0.04, 0.6), 0.35),
                                       pico(chispas(d, 30), 0.25)), 0.4, 2.8))
    frase = llamada([(P[2], 0.16, 0.8), (P[4], 0.16, 0.9), (P[5], 0.3, 1.0), (P[4], 0.14, 0.8), (P[5], 0.14, 0.9), (P[7], 0.7, 1.0)])
    guardar('cartel', reverb(mezclar(pico(frase, 0.8), en(0.6, pico(coro_voces(2.4, [587.3, 740.0, 880.0, 1174.7], 'a'), 0.45)),
                                     pico(chispas(2.4, 20), 0.25)), 0.45, 3.0), alto=0.8)
    # El picado: el silbido de un cohete que cae, la bengala detras y el aire.
    n = n_(0.8)
    guardar('picado', reverb(mezclar(pico(silbido_cohete(0.8, 2800, 900, 0.5) * curva(n, [(0, 0.3), (1, 1.0)]), 0.8),
                                     pico(chisporroteo(0.8, 1.5) * curva(n, [(0, 0.2), (1, 1)]), 0.4), pico(soplo(0.8, 300, 2000, 1.0, 0.0), 0.4)),
                             0.25, 1.4))
    guardar('picotazo', reverb(mezclar(pico(estallido_luz(1.0, 2.0), 1.0), pico(trino(0.3, 2400, 1.1, 20) * ventana(0.3, 0.01, 0.1), 0.35)),
                               0.35, 2.4), limite=0.5)
    # Las plumas: una andanada de dardos que silban.
    for i in range(2):
        voleo = mezclar(*[en(k * 0.05 + rng.uniform(0, 0.02), silbido_cohete(0.35, rng.uniform(1400, 1800), rng.uniform(2600, 3400), 0.5)
                             * rng.uniform(0.4, 1.0)) for k in range(7)])
        guardar('pluma', reverb(mezclar(pico(voleo, 0.8), pico(aleteo_plumas(0.6, 1.2), 0.6)), 0.25, 1.6), i + 1)
    for i in range(2):
        pops = mezclar(*[en(rng.uniform(0, 0.35), mezclar(pico(boom(90, 50, 0.04), 0.5), pico(estrellas(0.5, 600 * np.exp(-t_(0.5) / 0.1)), 0.6))
                            * rng.uniform(0.4, 1.0)) for _ in range(6)])
        guardar('pluma_golpe', reverb(mezclar(pico(pops, 1.0), pico(chispas(0.8, 30), 0.3)), 0.3, 2.0), i + 1)
    # Se vuelve un sol: el coro que crece, trinos cada vez mas rapidos, la bengala y un silbido que sube.
    d = 3.0
    n = n_(d)
    coro = coro_voces(d, [440, 554.4, 659.3, 880], 'a', curva(n, [(0, 0.8), (1, 1.0)])) * curva(n, [(0, 0), (1, 1)])
    trinos = trino(d, curva(n, [(0, 1200), (1, 2400)]), 1.1, curva(n, [(0, 6), (1, 24)])) * curva(n, [(0, 0.1), (1, 0.8)])
    guardar('carga', reverb(mezclar(pico(coro, 0.6), pico(trinos, 0.35), pico(chisporroteo(d, 1.5) * curva(n, [(0, 0.2), (1, 1.0)]), 0.4),
                                    en(2.2, pico(silbido_cohete(0.8, 800, 3000, 0.4), 0.4))), 0.35, 2.4))
    # La Llamarada del Renacimiento: un fuego artificial enorme, un acorde de luz y su grito.
    guardar('nova', reverb(mezclar(pico(estallido_luz(1.8, 4.0), 1.0), pico(coro_voces(2.5, [293.7, 370.0, 440.0, 587.3, 740.0], 'a')
                                                                            * caida(2.5, 0.8, 0.02), 0.5),
                                   en(0.05, pico(trino(1.0, curva(n_(1.0), [(0, 1760), (1, 2349)]), 1.08, 14) * ventana(1.0, 0.02, 0.4), 0.3))),
                           0.45, 3.6), limite=0.45)


# ======================================================================
#  Guardar
# ======================================================================
def sonoridad_a(x):
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    num = [(2 * np.pi * f4) ** 2 * (10 ** (1.9997 / 20)), 0, 0, 0, 0]
    den = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2], [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
    den = np.polymul(np.polymul(den, [1, 2 * np.pi * f3]), [1, 2 * np.pi * f2])
    b, a = signal.bilinear(num, den, SR)
    xa = signal.lfilter(b, a, x)
    w = n_(0.4)
    c = np.concatenate([[0.0], np.cumsum(xa ** 2)])
    e = (c[w:] - c[:-w]) / w if len(xa) > w else np.array([np.mean(xa ** 2)])
    return 10 * np.log10(np.max(e) + 1e-20)


def guardar(evento, x, variante=None, alto=0.89, limite=None, largo=None, techo=None):
    x = pa(np.asarray(x, float), 25)
    if limite:
        x = limitar(x, limite)
    m = np.max(np.abs(x))
    resto = np.nonzero(np.abs(x) > m * 10 ** (-58 / 20))[0]
    if len(resto):
        x = x[:min(len(x), resto[-1] + n_(0.06))]
    if largo and len(x) > n_(largo):
        x = x[:n_(largo)].copy()
        r = n_(min(0.45, largo * 0.3))
        x[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    f = min(len(x) // 4, n_(0.004))
    x[:f] *= np.linspace(0, 1, f)
    g = min(len(x) // 4, n_(0.04))
    x[-g:] *= np.linspace(1, 0, g)
    x = pico(x, alto)
    if techo is not None:
        x *= min(1.0, 10 ** ((techo - sonoridad_a(x)) / 20))
    nombre = evento if variante is None else f'{evento}{variante}'
    out = os.path.join(SONIDOS, JEFE)
    sf.write(os.path.join(out, nombre + '.ogg'), x.astype(np.float32), SR, format='OGG', subtype='VORBIS')
    EVENTOS.setdefault((JEFE, evento), []).append(nombre)
    GUARDADOS.append((f'{JEFE}/{nombre}', x))
    print(f'  {JEFE}/{nombre:22s} {len(x) / SR:5.2f} s', flush=True)


def empezar(jefe):
    global JEFE
    JEFE = jefe
    d = os.path.join(SONIDOS, jefe)
    os.makedirs(d, exist_ok=True)
    for viejo in os.listdir(d):
        if viejo.endswith('.ogg'):
            os.remove(os.path.join(d, viejo))
    print(jefe, flush=True)


# ======================================================================
#  Subtitulos, sounds.json y la hoja
# ======================================================================
SUBTITULOS = {
    'moctezuma': {
        'ambiente': ('Suenan los cascabeles de Moctezuma', "Moctezuma's rattles shake"),
        'paso': ('Pasos de Moctezuma', 'Moctezuma steps'),
        'herido': ('Moctezuma recibe un golpe', 'Moctezuma is hit'),
        'muerte': ('Moctezuma cae', 'Moctezuma falls'),
        'inmune': ('La obsidiana de Moctezuma resiste', "Moctezuma's obsidian holds"),
        'despertar': ('Moctezuma despierta', 'Moctezuma awakens'),
        'arranca': ('Moctezuma arranca su arma del suelo', 'Moctezuma pulls his weapon from the ground'),
        'choque': ('Moctezuma golpea su escudo', 'Moctezuma strikes his shield'),
        'grito': ('Moctezuma lanza su grito de guerra', 'Moctezuma lets out his war cry'),
        'cartel': ('Tambores de guerra', 'War drums'),
        'corte': ('Canta el filo de obsidiana', 'The obsidian edge sings'),
        'corte_golpe': ('El Corte de Obsidiana', 'The Obsidian Cut'),
        'salto': ('Moctezuma salta', 'Moctezuma leaps'),
        'terremoto': ('El Terremoto del Águila', 'The Eagle Quake'),
        'pinchos': ('Brotan pinchos de jade', 'Jade spikes burst out'),
        'tormenta': ('Se forma la Tormenta de Obsidiana', 'The Obsidian Storm gathers'),
        'fragmento': ('Silba un fragmento que cae', 'A falling shard whistles'),
        'fragmento_golpe': ('Revienta un fragmento', 'A shard shatters'),
        'erupcion': ('La tierra revienta en jade', 'The earth bursts into jade'),
    },
    'yiatzo': {
        'ambiente': ('Zumba el orbe de Yiatzo', "Yiatzo's orb hums"),
        'herido': ('Yiatzo recibe un golpe', 'Yiatzo is hit'),
        'muerte': ('El viento de Yiatzo se apaga', "Yiatzo's wind dies out"),
        'inmune': ('El viento protege a Yiatzo', 'The wind shields Yiatzo'),
        'despertar': ('Yiatzo despierta', 'Yiatzo awakens'),
        'losas': ('Las losas de glifos giran', 'The glyph stones swirl'),
        'grito': ('Yiatzo invoca al viento', 'Yiatzo calls the wind'),
        'golpe': ('Yiatzo golpea con su bastón', 'Yiatzo strikes with his staff'),
        'cartel': ('Un canto de cristal', 'A crystal song'),
        'rafaga': ('La Ráfaga de Viento', 'The Wind Gust'),
        'cuchilla': ('Corta una cuchilla de viento', 'A wind blade cuts'),
        'tormenta': ('El viento se reúne', 'The wind gathers'),
        'estallido': ('La Tormenta de Viento', 'The Wind Storm'),
        'ciclon': ('Ruge el Ciclón Devastador', 'The Devastating Cyclone roars'),
        'ciclon_estalla': ('Estalla el ciclón', 'The cyclone bursts'),
    },
    'atlahua': {
        'ambiente': ('Las voces del mar rodean a Atlahua', 'Sea voices surround Atlahua'),
        'paso': ('Pasos húmedos de Atlahua', "Atlahua's wet steps"),
        'herido': ('Atlahua recibe un golpe', 'Atlahua is hit'),
        'muerte': ('Atlahua se hunde', 'Atlahua sinks'),
        'inmune': ('El coral protege a Atlahua', 'The coral shields Atlahua'),
        'despertar': ('Atlahua despierta', 'Atlahua awakens'),
        'rugido': ('Ruge el rey del abismo', 'The king of the deep roars'),
        'clava': ('Atlahua clava su tridente', 'Atlahua drives in his trident'),
        'cartel': ('Suena la caracola de Atlahua', "Atlahua's conch sounds"),
        'estocada': ('La Estocada del Tridente', 'The Trident Thrust'),
        'golpe': ('El tridente golpea el suelo', 'The trident strikes the ground'),
        'ola': ('Las Olas del Abismo', 'The Abyssal Waves'),
        'tsunami': ('Se alza el Tsunami del Abismo', 'The Abyssal Tsunami rises'),
        'tsunami_rompe': ('Rompe el tsunami', 'The tsunami crashes'),
    },
    'xiuhquetzal': {
        'ambiente': ('Canta Xiuhquetzal', 'Xiuhquetzal sings'),
        'aleteo': ('Aletea Xiuhquetzal', 'Xiuhquetzal flaps its wings'),
        'herido': ('Xiuhquetzal recibe un golpe', 'Xiuhquetzal is hit'),
        'muerte': ('Xiuhquetzal se consume', 'Xiuhquetzal burns out'),
        'inmune': ('El fuego protege a Xiuhquetzal', 'The fire shields Xiuhquetzal'),
        'despertar': ('Xiuhquetzal renace', 'Xiuhquetzal is reborn'),
        'chillido': ('El fénix lanza su grito', 'The phoenix cries out'),
        'cartel': ('El canto del fénix', 'The song of the phoenix'),
        'picado': ('Xiuhquetzal se lanza en picado', 'Xiuhquetzal dives'),
        'picotazo': ('El Picotazo de Llamas', 'The Flame Peck'),
        'pluma': ('La Tormenta de Plumas Ígneas', 'The Storm of Fiery Feathers'),
        'pluma_golpe': ('Arden las plumas', 'The feathers ignite'),
        'carga': ('Xiuhquetzal se vuelve un sol', 'Xiuhquetzal becomes a sun'),
        'nova': ('La Llamarada del Renacimiento', 'The Rebirth Blaze'),
    },
}


def escribir_json():
    ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
    with open(ruta, encoding='utf-8') as fh:
        datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
    jefes = {j for j, _ in EVENTOS}
    for k in [k for k in datos if k.split('.')[0] in jefes]:
        del datos[k]
    for (j, ev), archivos in EVENTOS.items():
        datos[f'{j}.{ev}'] = {'subtitle': f'subtitles.atalaya.{j}.{ev}', 'sounds': [f'atalaya:{j}/{a}' for a in archivos]}
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    for idioma, k in (('es_es', 0), ('en_us', 1)):
        p = os.path.join(RAIZ, f'src/main/resources/assets/atalaya/lang/{idioma}.json')
        d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        for clave in [c for c in d if any(c.startswith(f'subtitles.atalaya.{j}.') for j in jefes)]:
            del d[clave]
        for (j, ev) in EVENTOS:
            assert ev in SUBTITULOS[j], (j, ev)
            d[f'subtitles.atalaya.{j}.{ev}'] = SUBTITULOS[j][ev][k]
        with open(p, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
    print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')


def hoja(ruta):
    from PIL import Image, ImageDraw
    an, al, col = 300, 110, 5
    filas = (len(GUARDADOS) + col - 1) // col
    im = Image.new('RGB', (an * col, (al + 14) * filas), (12, 14, 18))
    dib = ImageDraw.Draw(im)
    for k, (nombre, x) in enumerate(GUARDADOS):
        f, tt, S = signal.spectrogram(x, SR, nperseg=1024, noverlap=768)
        S = 10 * np.log10(S + 1e-12)
        S = np.clip((S - (S.max() - 65)) / 65, 0, 1)
        fl = np.geomspace(30, 16000, al)
        idx = np.clip(np.searchsorted(f, fl), 0, len(f) - 1)
        img = (S[idx][::-1] * 255).astype(np.uint8)
        p = Image.fromarray(img).resize((an - 4, al), Image.BILINEAR)
        cx, cy = (k % col) * an, (k // col) * (al + 14)
        im.paste(Image.merge('RGB', (p.point(lambda v: int(v * 0.6)), p, p.point(lambda v: int(v * 0.8)))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s', fill=(220, 220, 220))
    im.save(ruta)


if __name__ == '__main__':
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else ['moctezuma', 'yiatzo', 'atlahua', 'xiuhquetzal']
    for j in pedidos:
        {'moctezuma': moctezuma, 'yiatzo': yiatzo, 'atlahua': atlahua, 'xiuhquetzal': xiuhquetzal}[j]()
    escribir_json()
    if HOJA:
        hoja(HOJA)
