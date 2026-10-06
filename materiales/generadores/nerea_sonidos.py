"""
Sonidos de Nerea, Guardian de los Mares. Sintetizados desde cero: nada de
vanilla ni de bancos de sonido.

Todo sale del AGUA, modelada con su fisica:

  - BURBUJAS: cada una es la resonancia de Minnaert de una bolsa de aire
    (f = 3,26 / radio), que se apaga rapido y sube un poco de tono al subir
    (modelo de van den Doel). Una nube de miles, con radios repartidos como
    en el agua de verdad, es burbujeo, torrente, espuma o hervor segun la
    tasa y el tamano.
  - GOTAS: la burbuja que atrapa una gota al caer, con su "plink" que sube.
  - CHAPUZONES: el golpe, la lamina que salta, la nube de burbujas que deja,
    el "whump" de la cavidad al cerrarse y las gotas que vuelven a caer.
  - OLAS: la ola que crece, rompe y se deshace en espuma (burbujas diminutas).
  - CHORROS a presion, VAPOR (el agua contra la antorcha), REMOLINO que
    desagua con gorgoteos graves.

Y lo que lleva encima, siempre mojado: HUESO y CORAL que crujen bajo la
presion, PRISMARINA que se raja como cristal, CADENAS oxidadas que gotean.

La VOZ es la de un leviatan: garganta enorme con gargaras de agua, y por
encima un lamento de sirena (Nerea es una nereida), todo sumergido.

Escribe los .ogg (mono, para que se oigan en 3D) en
assets/atalaya/sounds/nerea/ y sus eventos en sounds.json
(nerea.<evento>, subtitulo subtitles.atalaya.nerea.<evento>).

Uso: python nerea_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png]
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator
import os, sys, json, collections

SR = 44100
RAIZ = sys.argv[1]
OUT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/nerea')
os.makedirs(OUT, exist_ok=True)
for viejo in os.listdir(OUT):
    if viejo.endswith('.ogg'):
        os.remove(os.path.join(OUT, viejo))
rng = np.random.default_rng(20261003)
EVENTOS = collections.OrderedDict()
GUARDADOS = []


# ======================================================================
#  Utilidades
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
    """Ruido lento (por debajo de fc), de desviacion 1: para jitter y temblores."""
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
    """Biquad (RBJ) con la frecuencia moviendose: barridos, aspiraciones, olas."""
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
    """Valor que pasa suave por (tiempo relativo 0..1, valor)."""
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
    e[-f:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f))   # que nada acabe en seco
    return e


def campana_env(dur, p=2.0):
    return np.sin(np.pi * np.linspace(0, 1, n_(dur))) ** p


def rampa(dur, p=1.0, desde=0.0, hasta=1.0):
    return desde + (hasta - desde) * np.linspace(0, 1, n_(dur)) ** p


def ventana(dur, ataque, soltar):
    """Sube en `ataque`, se mantiene y se apaga en `soltar` (rampas de coseno)."""
    n = n_(dur)
    e = np.ones(n)
    a, s = min(n, n_(ataque)), min(n, n_(soltar))
    e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    e[n - s:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, s))
    return e


def saturar(x, k=2.0):
    return np.tanh(k * x) / np.tanh(k)


def limitar(x, umbral=0.55):
    """Compresion suave de los picos: mas cuerpo sin que nada recorte."""
    y = pico(x)
    m = np.abs(y)
    sobre = m > umbral
    y[sobre] = np.sign(y[sobre]) * (umbral + (1 - umbral) * np.tanh((m[sobre] - umbral) / (1 - umbral)))
    return y


# ---------------------------------------------------------------- reverb
_IRS = {}


def respuesta(cola, oscuro):
    """Sala submarina: cola densa, sin ecos sueltos, que pierde los agudos antes."""
    clave = (round(cola, 2), int(oscuro))
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro))
        x = r.standard_normal(len(t))
        h = (pb(x, 450) * np.exp(-6.9 * t / cola)
             + bp(x, 450, 2500) * np.exp(-6.9 * t / (cola * 0.65)) * 0.8
             + pa(x, 2500) * np.exp(-6.9 * t / (cola * 0.3)) * 0.5)
        h = pb(h, oscuro)
        a = n_(0.012)
        h[:a] *= np.linspace(0, 1, a) ** 2
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


def reverb(x, mezcla=0.3, cola=1.6, oscuro=3500):
    h = respuesta(cola, oscuro)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


# ======================================================================
#  AGUA
# ======================================================================
def burbuja(r_mm, xi=0.1, amp=1.0, amortigua=1.0, temblor=0.0):
    """Una burbuja de radio r_mm: resonancia de Minnaert que se apaga y sube."""
    f0 = min(3260.0 / r_mm, SR * 0.42)
    d = (0.043 * f0 + 0.0014 * f0 ** 1.5) * amortigua
    dur = min(1.6, 6.5 / d)
    t = t_(dur)
    f = f0 * (1 + xi * d * t)
    if temblor:
        f *= 1 + temblor * np.sin(2 * np.pi * rng.uniform(6, 11) * t)
    fase = 2 * np.pi * np.cumsum(np.minimum(f, SR * 0.45)) / SR
    e = np.exp(-d * t)
    a = min(len(t), n_(0.0004))
    e[:a] *= np.linspace(0, 1, a)
    return amp * np.sin(fase) * e


def nube(dur, tasa, rmin, rmax, beta=2.0, xi=0.1, amortigua=1.0, potencia=1.0):
    """Muchas burbujas: tasa (por segundo, numero o curva), radios en ley de
    potencia entre rmin y rmax (mm). Pocas grandes, muchas pequenas."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    u = rng.random(len(cuando))
    if abs(beta - 1) < 1e-6:
        radios = rmin * (rmax / rmin) ** u
    else:
        k = 1 - beta
        radios = (rmin ** k + u * (rmax ** k - rmin ** k)) ** (1 / k)
    out = np.zeros(n + n_(1.7))
    for i, r in zip(cuando, radios):
        b = burbuja(r, xi * rng.uniform(0.6, 1.5), (r ** potencia) * rng.uniform(0.35, 1.0), amortigua)
        out[i:i + len(b)] += b
    return np.trim_zeros(out, 'b')


def gota(r=None, amp=1.0):
    """Una gota que cae al agua: un toque y el 'plink' que sube."""
    r = r if r is not None else rng.uniform(1.8, 4.2)
    toque = bp(ruido(0.004), 2500, 9000) * caida(0.004, 0.0008, 0.0002) * 0.25
    return amp * mezclar(toque, en(0.001, burbuja(r, rng.uniform(0.22, 0.42), 1.0, 0.8)))


def goteo(dur, cuantas, desde=0.0, amp=1.0, apagar=True):
    """Gotas que caen dispersas (de la piel, de las cadenas, del agua que salto)."""
    capas = []
    for k in range(cuantas):
        s = desde + rng.uniform(0, dur) ** (1.3 if apagar else 1.0) * (dur ** (-0.3) if apagar else 1.0)
        a = amp * rng.uniform(0.3, 1.0) * ((1 - 0.6 * (s - desde) / max(dur, 1e-3)) if apagar else 1.0)
        capas.append(en(max(0.0, s), gota(amp=a)))
    return mezclar(*capas) if capas else np.zeros(1)


def chapuzon(tam=1.0, dur=None):
    """Algo grande que golpea el agua: golpe, lamina, burbujas, whump y gotas."""
    dur = dur or 0.7 + 0.8 * tam
    t = t_(dur)
    golpe = pico(bp(ruido(0.15), 200, 7500) * caida(0.15, 0.010 + 0.018 * tam, 0.001), 1.0)
    lamina = pico(filtro_mov(ruido(dur, 'rosa'), 2200 + 6500 * np.exp(-t / (0.12 + 0.1 * tam)), 'low')
                  * caida(dur, 0.10 + 0.22 * tam, 0.004), 0.65)
    burb = pico(nube(dur, (500 + 1200 * tam) * np.exp(-t / (0.12 + 0.22 * tam)), 0.6, 2.5 + 4.5 * tam, beta=2.1), 0.75)
    capas = [golpe, lamina, burb, goteo(0.4 + 0.7 * tam, int(3 + 7 * tam), 0.15, 0.35)]
    if tam >= 0.7:
        f = 55 + 60 / tam
        whump = np.sin(2 * np.pi * np.cumsum(f * (0.55 + 0.45 * np.exp(-t_(0.5) / 0.08))) / SR) * caida(0.5, 0.06 + 0.06 * tam, 0.004)
        capas.append(en(0.02, pico(whump, 0.45 * min(tam, 2.0))))
    return mezclar(*capas)


def rompiente(dur=2.4, cresta=0.4, fuerza=1.0):
    """Una ola: crece, rompe en `cresta` (segundos) y se deshace en espuma."""
    t = t_(dur)
    sube = np.clip(t / max(cresta, 1e-3), 0, 1) ** 2.2
    baja = np.exp(-np.maximum(0, t - cresta) / (dur * 0.33))
    forma = np.where(t < cresta, sube, baja)
    cuerpo = filtro_mov(ruido(dur, 'rosa'), 300 + 5200 * forma ** 1.4, 'low', 0.8) * (0.15 + 0.85 * forma)
    trueno = pb(ruido(dur, 'marron'), 140) * forma ** 0.7
    tras = np.where(t < cresta, 0.0, np.exp(-np.maximum(0, t - cresta) / (dur * 0.45)))
    espuma = nube(dur, 3500 * fuerza * tras, 0.25, 1.4, beta=1.7)
    medias = nube(dur, 350 * fuerza * tras, 1.4, 6.0, beta=2.2)
    golpe = en(max(0.0, cresta - 0.01), bp(ruido(0.25), 150, 6000) * caida(0.25, 0.05, 0.003))
    fin = ventana(dur, 0.001, dur * 0.3)
    return mezclar(pico(cuerpo * fin, 0.8), pico(trueno * fin, 0.5 * fuerza), pico(espuma, 0.45), pico(medias, 0.35),
                   pico(golpe, 0.6 * fuerza))


def chorro(dur=0.6, fuerza=1.0):
    """Agua que sale a presion por una grieta: silbido turbulento con burbujas."""
    t = t_(dur)
    turb = 1 + 0.45 * suave(n_(dur), 28)
    silbido = bp(ruido(dur), 450, 5500) * caida(dur, dur * 0.4, 0.005) * turb * ventana(dur, 0.001, dur * 0.3)
    burb = nube(dur, 1600 * fuerza * np.exp(-t / (dur * 0.5)), 0.5, 3.5, beta=2.0)
    return mezclar(pico(silbido, 0.7), pico(burb, 0.45))


def torrente(dur, tasa=2200, rmax=6.0, brillo=3500):
    """Mucha agua moviendose: lecho de ruido con una nube densa encima."""
    lecho = bp(ruido(dur, 'rosa'), 180, brillo)
    return mezclar(pico(lecho, 0.55), pico(nube(dur, tasa, 0.5, rmax, beta=2.0), 0.6))[:n_(dur)]


def vapor(dur=0.9):
    """La antorcha contra el agua: siseo de vapor y el chisporroteo de la llama."""
    t = t_(dur)
    fin = ventana(dur, 0.001, dur * 0.3)
    sis = pa(ruido(dur), 2600) * caida(dur, dur * 0.45, 0.01) * (1 + 0.5 * suave(n_(dur), 12)) * fin
    cuerpo = bp(ruido(dur, 'rosa'), 900, 3200) * caida(dur, dur * 0.3, 0.02) * fin
    chispas = np.zeros(n_(dur) + 400)
    for s in np.sort(rng.uniform(0, dur * 0.9, 70)):
        c = bp(ruido(0.003), 2500, 10000) * caida(0.003, 0.0006, 0.0001) * rng.uniform(0.2, 1.0) * np.exp(-s / dur * 1.5)
        i = n_(s)
        chispas[i:i + len(c)] += c
    hervor = nube(dur, 500 * np.exp(-t / (dur * 0.5)), 0.4, 1.4)
    return mezclar(pico(sis, 0.8), pico(cuerpo, 0.3), pico(chispas, 0.5), pico(hervor, 0.3))


def flanger(x, lfo_hz, base_ms=1.5, prof_ms=5.0, mezcla=0.7):
    """Peine que se mueve: el agua girando en un remolino."""
    n = len(x)
    lfo = np.broadcast_to(np.asarray(lfo_hz, dtype=float), (n,))
    fase = 2 * np.pi * np.cumsum(lfo) / SR
    idx = np.arange(n)
    d1 = (base_ms + prof_ms * (0.5 + 0.5 * np.sin(fase))) * SR / 1000
    d2 = (base_ms + prof_ms * (0.5 + 0.5 * np.sin(fase + 2.1))) * SR / 1000
    y1 = np.interp(idx - d1, idx, x, left=0)
    y2 = np.interp(idx - d2, idx, x, left=0)
    return x + mezcla * y1 - 0.5 * mezcla * y2


def sumergir(x, corte=1800, gargaras=0.3):
    """Lo que hace que algo suene bajo el agua: sin agudos, un coro lento y
    el temblor de las gargaras."""
    x = pb(x, corte, 4)
    n = len(x)
    t = np.arange(n) / SR
    d = (0.011 + 0.004 * np.sin(2 * np.pi * 0.6 * t)) * SR
    idx = np.arange(n)
    coro = np.interp(idx - d, idx, x, left=0)
    trino = bp(rng.standard_normal(n), 14, 32)
    trino = 1 + gargaras * trino / (np.std(trino) + 1e-12)
    return (0.75 * x + 0.45 * coro) * np.clip(trino, 0.2, 2.0)


# ======================================================================
#  HUESO, CORAL, PRISMARINA, CADENAS
# ======================================================================
def boom(f0=60, f1=26, tau=0.25, dur=None):
    """El golpe grave de algo enorme contra el suelo."""
    dur = dur or tau * 5
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) + 0.25 * np.sin(2 * fase)) * caida(dur, tau, 0.003)


def impacto(grave=1.0, piedras=12):
    """Piedra contra piedra: boom, el golpe seco y la gravilla que salta."""
    seco = pb(ruido(0.12), 1500) * caida(0.12, 0.016, 0.001)
    crujido = mezclar(*[en(rng.uniform(0, 0.06), bp(ruido(0.01), 600, 4000) * caida(0.01, 0.002) * rng.uniform(0.3, 1))
                        for _ in range(8)])
    grava = mezclar(*[en(0.08 + rng.uniform(0, 0.6) ** 1.6, bp(ruido(0.006), 1500, 6000) * caida(0.006, 0.0012) * rng.uniform(0.1, 0.5))
                      for _ in range(piedras)])
    return mezclar(pico(boom(58 * grave, 24 * grave, 0.22 * grave), 1.0), pico(seco, 0.7), pico(crujido, 0.45), pico(grava, 0.3))


def modos(f, dur, parciales, tau):
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        if f * r < SR * 0.45:
            s += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6)) * np.exp(-t / (tau / r ** 0.5))
    a = n_(0.0008)
    s[:a] *= np.linspace(0, 1, a)
    return s


METAL = ((1, 1), (1.47, 0.7), (2.09, 0.45), (2.56, 0.35), (3.9, 0.2))
CRISTAL = ((1, 1), (2.32, 0.6), (4.25, 0.35), (6.63, 0.2))


def eslabon(grave=True, amp=1.0):
    """Un eslabon oxidado contra otro: poco brillo, mucho golpe."""
    f = rng.uniform(650, 1400) if grave else rng.uniform(1400, 3000)
    toque = bp(ruido(0.004), 2500, 10000) * caida(0.004, 0.0008) * 0.5
    return amp * mezclar(toque, modos(f, 0.25, METAL, rng.uniform(0.03, 0.07)))


def cadena(dur, golpes=8, grave=True, mojada=True):
    """Una cadena que se mueve: golpes de eslabones en racimos, y gotas."""
    out = np.zeros(n_(dur) + n_(0.3))
    hechos = 0
    while hechos < golpes:
        t0 = rng.uniform(0, dur * 0.9)
        for k in range(rng.integers(1, 4)):
            e = eslabon(grave, rng.uniform(0.3, 1.0))
            i = n_(t0 + k * rng.uniform(0.008, 0.03))
            out[i:i + len(e)] += e[:max(0, len(out) - i)]
            hechos += 1
    if mojada:
        out = mezclar(out, goteo(dur, max(1, golpes // 4), 0.05, 0.25, apagar=False))
    return out


def crujir(dur, tasa=(18, 90), resonancias=((240, 22), (530, 28), (910, 30), (1500, 35)), fuerza=1.0):
    """Roce que se pega y se suelta: hueso y coral bajo presion, el casco de un
    barco hundido. Pulsos a ritmo irregular que hacen sonar unas resonancias."""
    n = n_(dur)
    ritmo = tasa[0] + (tasa[1] - tasa[0]) * (0.5 + 0.5 * np.tanh(suave(n, 3)))
    fase = np.cumsum(ritmo) / SR
    pulsos = np.zeros(n)
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    pulsos[golpes] = rng.uniform(0.3, 1.0, len(golpes))
    exc = pulsos + 0.02 * rng.standard_normal(n)
    out = sum(resonar(exc, f, q) * rng.uniform(0.6, 1.0) for f, q in resonancias)
    return fuerza * out * (0.6 + 0.4 * np.abs(suave(n, 2)))


def rajar(cuantos=8, dur=0.05, lo=600, hi=7000):
    """Una grieta que se abre: chasquidos muy seguidos."""
    return mezclar(*[en(rng.uniform(0, dur) ** 1.4 / dur ** 0.4, bp(ruido(0.008), lo, hi) * caida(0.008, 0.0015) * rng.uniform(0.3, 1))
                     for _ in range(cuantos)])


def esquirlas(cuantas, dur, fmin=1800, fmax=5200, amp=1.0):
    return mezclar(*[en(rng.uniform(0, dur) ** 1.5 / max(dur, 1e-3) ** 0.5, modos(rng.uniform(fmin, fmax), 0.6, CRISTAL, 0.12) * rng.uniform(0.2, 1.0) * amp)
                     for _ in range(cuantas)])


def zumbido(dur, puntos, q=1.6, color='rosa'):
    """Whoosh: ruido con una banda que se mueve (puntos: (t relativo, Hz))."""
    return filtro_mov(ruido(dur, color), curva(n_(dur), puntos), 'band', q) * campana_env(dur, 1.5)


def latido(f=55, fuerza=1.0):
    """Un latido humedo: el golpe y el chapoteo de dentro, dos veces."""
    def golpe(ff, a):
        t = t_(0.3)
        sordo = np.sin(2 * np.pi * np.cumsum(ff * (0.7 + 0.6 * np.exp(-t / 0.03))) / SR) * caida(0.3, 0.07, 0.004)
        chof = filtro_mov(ruido(0.3, 'rosa'), 1100 * np.exp(-t / 0.05) + 220, 'band', 2.5) * caida(0.3, 0.05, 0.003)
        return a * mezclar(pico(sordo, 1.0), pico(chof, 0.4))
    return fuerza * pb(mezclar(golpe(f, 1.0), en(0.17, golpe(f * 1.12, 0.65))), 1600)


# ======================================================================
#  VOZ
# ======================================================================
VOCAL_O = ((300, 90, 1.0), (680, 110, 0.75), (1500, 160, 0.35), (2500, 200, 0.18))
VOCAL_A = ((620, 110, 1.0), (1050, 130, 0.8), (2300, 190, 0.35), (3100, 240, 0.15))


def garganta(f0, dur, formantes=VOCAL_O, aspereza=0.5, sub=0.4, jitter=0.03, aliento=0.25, fmax=5000):
    """Una garganta enorme: pulsos con jitter, subarmonico que la raspa y
    formantes de tracto gigante (los F pueden ser curvas)."""
    n = n_(dur)
    f0 = np.broadcast_to(np.asarray(f0, dtype=float), (n,))
    f = f0 * (1 + jitter * suave(n, 25))
    fase = 2 * np.pi * np.cumsum(f) / SR
    src = np.zeros(n)
    for k in range(1, int(min(160, fmax / np.max(f))) + 1):
        src += np.sin(k * fase) / k ** 1.15
    src *= 1 + sub * np.sin(fase / 2)
    src *= 1 + 0.3 * aspereza * suave(n, 60)
    src += aliento * np.std(src) * ruido(dur, 'rosa') * (0.6 + 0.4 * np.sin(fase))
    out = np.zeros(n)
    for F, bw, g in formantes:
        if np.isscalar(F):
            out += g * resonar(src, F, F / bw)
        else:
            out += g * filtro_mov(src, F, 'band', float(np.mean(F)) / bw)
    return saturar(pico(out), 1.2 + 2.5 * aspereza)


def lamento(dur, puntos, armonicos=9, vibrato=0.012, brillo=900):
    """El canto de la sirena: como una ballena, deslizandose entre notas."""
    n = n_(dur)
    t = np.arange(n) / SR
    f = curva(n, puntos) * (1 + vibrato * np.sin(2 * np.pi * 4.2 * t) + 0.004 * suave(n, 6))
    fase = 2 * np.pi * np.cumsum(f) / SR
    s = np.zeros(n)
    for k in range(1, armonicos + 1):
        fk = f * k
        peso = np.exp(-((np.log(fk / brillo)) ** 2) / 1.2) / k ** 0.6
        s += np.sin(k * fase) * peso
    return s * ventana(dur, dur * 0.25, dur * 0.35)


def rugido(dur=2.4, f0=46, f1=72, sirena=1.0, agua=1.0):
    """El rugido de Nerea: garganta de leviatan con gargaras, el lamento de
    sirena por encima, burbujas que le salen de la boca y el agua que escupe."""
    n = n_(dur)
    tono = curva(n, [(0, f0), (0.22, f1), (0.6, f1 * 0.93), (1, f0 * 0.82)])
    F1 = curva(n, [(0, 260), (0.25, 520), (0.7, 450), (1, 300)])
    F2 = curva(n, [(0, 620), (0.25, 1050), (0.7, 900), (1, 650)])
    voz_ = garganta(tono, dur, ((F1, 110, 1.0), (F2, 140, 0.8), (1750, 180, 0.35), (2600, 220, 0.2)),
                    aspereza=0.7, sub=0.65, jitter=0.035, aliento=0.35)
    e = ventana(dur, 0.14, dur * 0.35)
    voz_ = sumergir(voz_ * e, 2300, 0.25)
    canto = lamento(dur * 0.85, [(0, f1 * 3.2), (0.3, f1 * 4.6), (0.7, f1 * 4.3), (1, f1 * 3.3)], brillo=700)
    burb = nube(dur, 700 * e, 1.0, 9.0, beta=2.0)
    escupe = pa(ruido(dur), 2200) * e * (1 + 0.4 * suave(n, 18))
    sub_ = boom(48, 30, 0.45)
    capas = mezclar(pico(voz_, 1.0), en(0.1, pico(sumergir(canto, 2600, 0.1), 0.38 * sirena)),
                    pico(burb, 0.32 * agua), pico(escupe, 0.12 * agua), pico(sub_, 0.45))
    return reverb(capas, 0.3, 1.8, 2600)


def ping(f=520, dur=0.5):
    """Un pulso de sonar: lo que hacen los ojos al fijarse."""
    return modos(f, dur, ((1, 1), (2.01, 0.25), (2.98, 0.08)), dur * 0.25)


# ======================================================================
#  Guardar
# ======================================================================
def guardar(evento, x, variante=None, alto=0.89, limite=None):
    x = pa(x, 25)
    if limite:
        x = limitar(x, limite)
    m = np.max(np.abs(x))
    resto = np.nonzero(np.abs(x) > m * 10 ** (-58 / 20))[0]
    if len(resto):
        x = x[:min(len(x), resto[-1] + n_(0.06))]
    f = min(len(x) // 4, n_(0.004))
    x[:f] *= np.linspace(0, 1, f)
    g = min(len(x) // 4, n_(0.04))
    x[-g:] *= np.linspace(1, 0, g)
    x = pico(x, alto)
    nombre = evento if variante is None else f'{evento}{variante}'
    sf.write(os.path.join(OUT, nombre + '.ogg'), x.astype(np.float32), SR, format='OGG', subtype='VORBIS')
    EVENTOS.setdefault(evento, []).append(nombre)
    GUARDADOS.append((nombre, x))
    print(f'  {nombre:22s} {len(x) / SR:5.2f} s', flush=True)


# ======================================================================
#  AMBIENTE: el fondo del mar. Cerca de ella siempre se oye el agua.
# ======================================================================
for i in range(3):
    d = 4.2
    n = n_(d)
    fondo = pb(ruido(d, 'marron'), 170) * (0.7 + 0.3 * suave(n, 0.8))
    canto = lamento(2.8, [(0, 190 + 25 * i), (0.35, 280 + 30 * i), (0.65, 250), (1, 170 + 10 * i)], brillo=650)
    corriente = nube(d, 18 + 10 * suave(n, 1) ** 2, 1.0, 5.0)
    glugs = mezclar(*[en(rng.uniform(0.3, 3.4), burbuja(rng.uniform(9, 16), 0.15, 1.0, 1.4)) for _ in range(2)])
    huesos = en(rng.uniform(0.5, 2.5), crujir(0.6, (12, 40), ((380, 25), (820, 30), (1300, 30))) * campana_env(0.6))
    capas = mezclar(pico(fondo, 0.45), en(0.6, pico(canto, 0.4)), pico(corriente, 0.3), pico(glugs, 0.25),
                    pico(huesos, 0.12), en(rng.uniform(1.0, 3.0), pico(cadena(0.4, 2), 0.15)), goteo(d, 3, 0.2, 0.12, False))
    guardar('ambiente', reverb(capas, 0.45, 2.4, 2200), i + 1, alto=0.7)

# ======================================================================
#  PASO: un pie de hueso de seis metros sobre piedra encharcada
# ======================================================================
for i in range(4):
    capas = mezclar(pico(impacto(1.0 + 0.08 * i, 8), 1.0),
                    pico(rajar(4, 0.03, 800, 3500), 0.3),
                    en(0.005, pico(chapuzon(0.9), 0.7)),
                    en(0.04, pico(cadena(0.45, 4), 0.18)))
    guardar('paso', reverb(capas, 0.15, 0.9, 3000), i + 1, limite=0.6)

# ======================================================================
#  INMUNE: le pegas y no le hace nada. Clang de cadena, coral duro, agua.
# ======================================================================
for i in range(3):
    clang = modos(390 + 70 * i, 0.9, METAL, 0.45)
    golpe = mezclar(pico(pb(ruido(0.08), 2600) * caida(0.08, 0.008), 1.0), pico(boom(190, 120, 0.04), 0.5))
    rocio = mezclar(pa(ruido(0.4), 2400) * caida(0.4, 0.1, 0.002), nube(0.4, 700 * np.exp(-t_(0.4) / 0.1), 0.3, 1.2))
    guardar('inmune', mezclar(pico(clang, 0.6), golpe, pico(rajar(3, 0.015, 2500, 9000), 0.3), pico(rocio, 0.35),
                              pico(cadena(0.5, 4, grave=False), 0.3)), i + 1)

# ======================================================================
#  HERIDO: el golpe entra en el corazon. Chof, quejido ahogado y aire.
# ======================================================================
for i in range(4):
    t = t_(0.3)
    chof = filtro_mov(ruido(0.3, 'rosa'), 1500 * np.exp(-t / 0.05) + 280, 'band', 2.5) * caida(0.3, 0.07, 0.002)
    golpe = mezclar(pico(pb(ruido(0.15), 1800) * caida(0.15, 0.014), 0.6), pico(boom(95, 45, 0.09), 0.7))
    d = 0.8
    queja = garganta(curva(n_(d), [(0, 92 + 14 * i), (0.3, 104 + 14 * i), (1, 66)]), d, VOCAL_O, 0.6, 0.5)
    queja = sumergir(queja * caida(d, 0.25, 0.03), 2000, 0.35)
    aire = nube(0.7, 150 * np.exp(-t_(0.7) / 0.25), 1.5, 6.0)
    guardar('herido', mezclar(golpe, pico(chof, 0.6), en(0.03, pico(queja, 0.9)), en(0.05, pico(aire, 0.4))), i + 1, limite=0.6)

# ======================================================================
#  RUGIDO
# ======================================================================
guardar('rugido', rugido(2.4, 46, 72), 1, limite=0.6)
guardar('rugido', rugido(2.2, 42, 66, sirena=1.2), 2, limite=0.6)
guardar('rugido', rugido(2.6, 50, 78, sirena=0.8, agua=1.3), 3, limite=0.6)

# ======================================================================
#  DESPERTAR: el fondo retumba, el hueso cruje bajo la presion, el agua le
#  cae a chorros al levantarse, las cadenas se tensan y al final ruge.
# ======================================================================
d = 4.2
n = n_(d)
t = t_(d)
retumbo = pb(ruido(d, 'marron'), 120) * np.interp(t, [0, 2.0, 2.8, 4.2], [0.1, 1.0, 0.8, 0.0])
cascada_tasa = np.interp(t, [0, 0.6, 1.4, 2.6, 4.2], [0, 300, 2600, 1800, 200])
cascada = mezclar(pico(nube(d, cascada_tasa, 0.6, 7.0, beta=2.0), 0.7),
                  pico(bp(ruido(d, 'rosa'), 300, 3500) * np.interp(t, [0, 0.6, 1.4, 3.0, 4.2], [0, 0.2, 1, 0.6, 0.1]), 0.5))
huesos = crujir(1.9, (10, 70), ((210, 20), (470, 26), (860, 30), (1350, 32))) * rampa(1.9, 1.0, 0.2, 1.0)
tension = np.zeros(n)
t0, paso_ = 0.3, 0.3
while t0 < 2.0:
    e = eslabon(True, 0.3 + t0 * 0.35)
    i0 = n_(t0)
    tension[i0:i0 + len(e)] += e[:n - i0]
    t0 += paso_
    paso_ = max(paso_ * 0.82, 0.035)
guardar('despertar', mezclar(pico(retumbo, 0.6), pico(cascada, 0.6), en(0.15, pico(huesos, 0.4)), pico(tension, 0.35),
                             en(1.95, pico(rugido(2.2, 44, 70), 1.0)), goteo(1.4, 8, 2.6, 0.2)), limite=0.6)

# ======================================================================
#  ROMPEOLAS: alza el tridente sorbiendo el agua del suelo, y lo clava:
#  una ola que revienta contra la piedra.
# ======================================================================
for i in range(2):
    d = 0.8
    n = n_(d)
    sorbe = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 240), (1, 2400 + 300 * i)]), 'band', 3.0) * rampa(d, 2.0, 0.1)
    sube = nube(d, rampa(d, 1.5, 80, 1600), 0.8, 5.0)
    aire = zumbido(d, [(0, 300), (1, 1600)], 1.2)
    sorbe *= ventana(d, 0.001, 0.12)
    guardar('rompeolas_alzar', mezclar(pico(sorbe, 0.7), pico(sube, 0.5), pico(aire, 0.3), goteo(0.7, 4, 0.05, 0.2, False)), i + 1)
for i in range(2):
    golpe = mezclar(pico(impacto(1.15 + 0.1 * i, 20), 1.0), pico(rompiente(2.6, 0.03, 1.2), 0.9),
                    pico(chapuzon(2.4), 0.75), en(0.05, pico(rajar(10, 0.12, 400, 3500), 0.35)))
    guardar('rompeolas_golpe', reverb(golpe, 0.25, 1.5, 3000), i + 1, limite=0.5)
for i in range(2):
    guardar('ola', mezclar(rompiente(2.4, 0.45 + 0.1 * i, 1.0), goteo(1.2, 6, 0.9, 0.2)), i + 1, limite=0.6)

# ======================================================================
#  REMOLINO: el agua empieza a girar y desagua por el centro.
# ======================================================================
d = 1.6
n = n_(d)
t = t_(d)
glugs = nube(d, rampa(d, 1.0, 6, 26), 10.0, 24.0, beta=1.5, xi=0.12, amortigua=1.4)
sube = nube(d, rampa(d, 1.6, 40, 900), 1.0, 5.0)
gira = flanger(torrente(d, 900, 4.0, 2500), rampa(d, 1.0, 0.5, 1.6)) * rampa(d, 1.5) * ventana(d, 0.001, 0.3)
guardar('remolino_aviso', mezclar(pico(glugs, 0.7), pico(sube, 0.45), pico(gira, 0.45),
                                  pico(pb(ruido(d, 'marron'), 150) * rampa(d, 1.2) * ventana(d, 0.001, 0.3), 0.4)))

d = 3.4
n = n_(d)
t = t_(d)
giro_hz = rampa(d, 1.0, 0.8, 2.2)
agua = flanger(torrente(d, 2600, 6.0, 3800), giro_hz, 1.2, 6.0, 0.8)
agua *= 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(giro_hz) / SR)
desague = mezclar(pico(nube(d, 24, 12.0, 30.0, beta=1.4, xi=0.15, amortigua=1.5), 0.8),
                  pico(pb(ruido(d, 'marron'), 160), 0.6))
silba = filtro_mov(ruido(d), curva(n, [(0, 380), (1, 540)]), 'band', 14)
guardar('remolino', mezclar(pico(agua, 0.8), pico(desague, 0.6), pico(silba, 0.1))[:n] * ventana(d, 0.35, 0.5), limite=0.65)

for i in range(2):
    guardar('antorcha', vapor(0.9 + 0.15 * i), i + 1)

# ======================================================================
#  BURBUJAS: el corazon bombea tres veces y suelta las bombas de agua.
# ======================================================================
d = 2.1
n = n_(d)
pom = mezclar(*[en(k * 0.32, latido(62, 0.7 + 0.15 * k)) for k in range(3)])
te = t_(1.2)
erupcion = mezclar(pico(nube(1.2, 70 * np.exp(-te / 0.4), 8.0, 22.0, beta=1.4, xi=0.2), 0.8),
                   pico(nube(1.2, 1100 * np.exp(-te / 0.35), 1.0, 4.0), 0.45),
                   pico(zumbido(0.6, [(0, 400), (1, 1500)], 1.3), 0.35))
pompas = mezclar(*[en(0.05 + 0.12 * k, burbuja(rng.uniform(16, 22), 0.25, 1.0, 0.8, temblor=0.06)) for k in range(3)])
guardar('burbujas', mezclar(pico(pom, 0.9), en(0.88, erupcion), en(0.9, pico(pompas, 0.6))), limite=0.6)

for i in range(3):
    estalla = mezclar(pico(pa(ruido(0.03), 700) * caida(0.03, 0.003), 1.0),
                      pico(np.sin(2 * np.pi * np.cumsum(np.linspace(950, 520, n_(0.05))) / SR) * caida(0.05, 0.012), 0.45),
                      pico(boom(72 - 6 * i, 28, 0.26), 1.0),
                      en(0.004, pico(chapuzon(2.1 + 0.2 * i), 0.85)),
                      goteo(1.3, 16, 0.25, 0.35))
    guardar('burbuja_revienta', reverb(estalla, 0.2, 1.1, 3500), i + 1, limite=0.5)
for i in range(3):
    pinchada = mezclar(pico(pa(ruido(0.012), 1500) * caida(0.012, 0.002), 0.9),
                       en(0.003, pico(burbuja(6.0 + 1.5 * i, 0.15, 1.0, 0.9), 0.6)),
                       pico(mezclar(pa(ruido(0.3), 2500) * caida(0.3, 0.07), nube(0.3, 900 * np.exp(-t_(0.3) / 0.07), 0.3, 1.0)), 0.3),
                       goteo(0.5, 4, 0.1, 0.3))
    guardar('burbuja_pompa', pinchada, i + 1)

# ======================================================================
#  MOLINO: las cadenas salen a rastras y luego barren el suelo girando.
# ======================================================================
d = 1.4
n = n_(d)
raspa = crujir(d, (150, 420), ((1600, 8), (2700, 10), (4100, 10)), 1.0) * ventana(d, 0.1, 0.3)
charcos = mezclar(*[en(rng.uniform(0.1, 1.1), chapuzon(0.3, 0.5)) for _ in range(4)])
guardar('molino_arrastre', mezclar(pico(cadena(d, 40), 0.6), pico(raspa, 0.35), pico(charcos, 0.35),
                                   pico(bp(ruido(d), 700, 2800) * ventana(d, 0.1, 0.4), 0.15)))
for i in range(3):
    d = 0.75
    vuelo = zumbido(d, [(0, 260), (0.5, 900 + 80 * i), (1, 380)], 1.4)
    rocio = pa(ruido(d), 1900) * campana_env(d, 2)
    guardar('molino_giro', mezclar(pico(vuelo, 0.8), pico(cadena(0.65, 6), 0.3), pico(rocio, 0.28),
                                   pico(pb(ruido(d, 'marron'), 90) * campana_env(d), 0.3), goteo(0.6, 2, 0.15, 0.12, False)), i + 1)

# ======================================================================
#  ARPON: voltea la cadena como un lazo, engancha, rebota, estocada.
# ======================================================================
d = 1.15
vueltas = mezclar(*[en(s, zumbido(0.26 - 0.03 * k, [(0, 350 + 120 * k), (0.5, 1100 + 200 * k), (1, 500)], 1.5) * (0.5 + 0.18 * k))
                    for k, s in enumerate((0.0, 0.3, 0.52, 0.7))])
rocio = mezclar(*[en(s, pa(ruido(0.2), 2200) * campana_env(0.2) * 0.4) for s in (0.05, 0.35, 0.56, 0.73)])
suelta = mezclar(zumbido(0.3, [(0, 1600), (1, 600)], 1.2), cadena(0.3, 14, grave=False, mojada=False))
guardar('arpon_lanzar', mezclar(pico(vueltas, 0.8), pico(rocio, 0.25), pico(cadena(0.8, 8), 0.25), en(0.82, pico(suelta, 0.7))))
for i in range(2):
    t = t_(0.3)
    chof = filtro_mov(ruido(0.3, 'rosa'), 1300 * np.exp(-t / 0.06) + 300, 'band', 3) * caida(0.3, 0.08, 0.002)
    tenso = modos(210 + 30 * i, 0.7, ((1, 1), (2.03, 0.4), (3.1, 0.2)), 0.3)
    guardar('arpon_engancha', mezclar(pico(pb(ruido(0.1), 1500) * caida(0.1, 0.012), 0.8), pico(boom(140, 70, 0.06), 0.6),
                                      pico(modos(720 + 60 * i, 0.5, METAL, 0.22), 0.45), pico(chof, 0.55),
                                      en(0.06, pico(tenso, 0.4)), en(0.06, pico(cadena(0.4, 8), 0.35)),
                                      pico(mezclar(pa(ruido(0.3), 2200) * caida(0.3, 0.08), goteo(0.5, 3, 0.1, 1.0)), 0.25)), i + 1)
for i in range(2):
    guardar('arpon_rebota', mezclar(pico(modos(1300 + 120 * i, 0.8, METAL, 0.35), 0.7),
                                    en(0.03, pico(zumbido(0.35, [(0, 1900), (1, 600)], 2.0), 0.3)),
                                    pico(chapuzon(0.4), 0.45), pico(rajar(3, 0.02, 1500, 6000), 0.35)), i + 1)
for i in range(2):
    estoc = mezclar(pico(zumbido(0.3, [(0, 300), (1, 1900)], 1.4), 0.5),
                    en(0.22, pico(impacto(1.0 + 0.1 * i, 14), 0.95)),
                    en(0.22, pico(filtro_mov(ruido(0.3, 'rosa'), 1400 * np.exp(-t_(0.3) / 0.05) + 260, 'band', 2.5) * caida(0.3, 0.07), 0.5)),
                    en(0.22, pico(chapuzon(1.3), 0.7)))
    guardar('estocada', reverb(estoc, 0.15, 1.0, 3000), i + 1, limite=0.55)

# ======================================================================
#  MIRADA: los ojos se fijan (sonar), el agua hierve alrededor mientras
#  carga, revienta donde da, y el ojo que le rompen estalla con un chorro.
# ======================================================================
d = 1.1
n = n_(d)
aspira = np.pad(nube(d, rampa(d, 1.0, 1500, 50), 0.5, 3.0), (0, n))[:n][::-1]
zumba = mezclar(*[np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 55 * h), (1, 70 * h)])) / SR) / h for h in (1, 2, 3, 4, 5)])
zumba = bp(zumba, 60, 1200) * rampa(d, 1.5) * ventana(d, 0.001, 0.12)
aspira = aspira * ventana(d, 0.001, 0.06)
guardar('mirada_carga', mezclar(pico(reverb(en(0.04, ping(330, 0.6)), 0.5, 2.2, 2500), 0.55), pico(aspira, 0.4),
                                pico(zumba, 0.4), pico(modos(1500, d, CRISTAL, 0.8) * rampa(d, 2.0), 0.12)))

d = 5.2
n = n_(d)
t = t_(d)
ka = np.clip(t / 3.2, 0, 1)
f0 = 55 * (1 + 0.5 * ka)
zumba = sum(np.sin(2 * np.pi * np.cumsum(f0 * h * (1 + 0.003 * j)) / SR) / h ** 0.8 for h in range(1, 9) for j in (0, 1))
zumba = filtro_mov(zumba, 300 + 1200 * ka, 'band', 1.2) * (0.3 + 0.7 * ka)
hervor = mezclar(pico(nube(d, 40 + 2600 * ka ** 2, 0.8, 3.0), 1.0),
                 pico(nube(d, 30 * (1 - ka) + 5, 6.0, 14.0, beta=1.5), 0.5))
pings = np.zeros(n + n_(0.5))
s, intervalo = 0.15, 0.85
while s < d - 0.1:
    k = min(1.0, s / 3.2)
    p_ = ping(560 + 500 * k, 0.4) * (0.5 + 0.5 * k)
    i0 = n_(s)
    pings[i0:i0 + len(p_)] += p_[:len(pings) - i0]
    s += intervalo
    intervalo = max(0.13, intervalo * 0.8)
presion = crujir(d, (10, 60), ((170, 20), (390, 24), (700, 28)), 1.0) * ka
rayo = mezclar(pico(zumba, 0.5), pico(hervor, 0.45), pico(reverb(pings, 0.4, 1.4, 4000), 0.3), pico(presion, 0.18))
guardar('mirada_rayo', rayo * ventana(len(rayo) / SR, 0.25, 0.08), limite=0.65)

for i in range(2):
    previo = pico(nube(0.15, 2500, 0.5, 2.0)[::-1], 0.35)
    revienta = mezclar(pico(pa(ruido(0.01), 1000) * caida(0.01, 0.0018), 1.0), pico(boom(72, 22, 0.4), 1.0),
                       pico(chapuzon(2.0), 0.7), pico(nube(1.2, 260 * np.exp(-t_(1.2) / 0.4), 3.0, 12.0, beta=1.6), 0.4),
                       pico(esquirlas(6, 0.1, 2500, 6000), 0.15))
    guardar('mirada_impacto', reverb(mezclar(previo, en(0.15, revienta)), 0.3, 1.7, 3000), i + 1, limite=0.5)

for i in range(2):
    d = 0.75
    grito = garganta(curva(n_(d), [(0, 150 + 20 * i), (0.25, 175 + 20 * i), (1, 95)]), d, VOCAL_A, 0.6, 0.35, 0.03, 0.3)
    grito = sumergir(grito * caida(d, 0.3, 0.02), 3000, 0.25)
    guardar('ojo_roto', mezclar(pico(rajar(6, 0.02, 1500, 9000), 0.9), pico(esquirlas(12, 0.15), 0.6),
                                en(0.2, pico(esquirlas(7, 0.5, 3000, 6000), 0.2)), pico(chorro(0.7), 0.6),
                                en(0.04, pico(grito, 0.6))), i + 1, limite=0.6)

for i in range(2):
    d = 2.4
    n = n_(d)
    queja = garganta(curva(n, [(0, 82 - 4 * i), (0.4, 70), (1, 46)]), d, VOCAL_O, 0.45, 0.3)
    queja = sumergir(queja * ventana(d, 0.05, 1.2), 1500, 0.4)
    t = t_(1.8)
    mareo = np.sin(2 * np.pi * np.cumsum(520 * (1 + 0.03 * np.sin(2 * np.pi * 3 * t))) / SR) * caida(1.8, 0.6, 0.05)
    guardar('aturdido', mezclar(pico(queja, 0.9), en(0.2, pico(mareo, 0.15)),
                                pico(nube(d, 60 * rampa(d, 1, 1, 0.2), 1.5, 8.0), 0.3), goteo(2.0, 5, 0.2, 0.2)), i + 1)

# ======================================================================
#  OJOS Y CORAZON: el ojo cruje con cada golpe; el corazon se raja al
#  cambiar de fase (se reproduce mas grave) y suelta agua a presion.
# ======================================================================
for i in range(3):
    guardar('sello_golpe', mezclar(pico(pb(ruido(0.06), 3000) * caida(0.06, 0.006), 0.7), pico(boom(230, 160, 0.03), 0.3),
                                   pico(rajar(3, 0.015, 1500, 8000), 0.6), pico(modos(1150 + 170 * i, 0.6, CRISTAL, 0.25), 0.45),
                                   en(0.01, pico(chorro(0.25, 0.4), 0.25))), i + 1)
d = 2.6
inspira = (pb(ruido(0.35, 'marron'), 300) * rampa(0.35, 2.0)) + crujir(0.35, (30, 120), ((300, 20), (700, 25)), 0.3)
grieta = mezclar(pico(rajar(12, 0.05, 600, 6000), 1.0), pico(boom(60, 24, 0.45), 1.0), pico(esquirlas(8, 0.2, 900, 3000), 0.3),
                 en(0.02, pico(chorro(1.0, 1.4), 0.7)), en(0.05, pico(nube(1.2, 200 * np.exp(-t_(1.2) / 0.4), 3.0, 14.0, beta=1.5), 0.45)),
                 en(0.55, pico(latido(50), 0.55)), en(0.85, pico(latido(48), 0.4)))
guardar('sello_roto', reverb(mezclar(pico(inspira, 0.35), en(0.35, grieta)), 0.3, 1.7, 3000), limite=0.5)

for i in range(2):
    estira = crujir(0.16, (60, 200), ((1800, 12), (3100, 15)), 1.0)
    rompe = mezclar(pico(pa(ruido(0.008), 1200) * caida(0.008, 0.0015), 1.0), pico(modos(560 + 60 * i, 0.9, METAL, 0.45), 0.7),
                    pico(zumbido(0.18, [(0, 3000), (1, 800)], 1.2), 0.4), en(0.1, pico(cadena(1.1, 22), 0.5)))
    caen = mezclar(*[en(s, chapuzon(0.35, 0.6)) for s in (0.45, 0.62, 0.85)])
    guardar('cadena_rompe', mezclar(pico(estira, 0.3), en(0.15, rompe), pico(caen, 0.35)), i + 1, limite=0.6)

d = 2.1
guardar('tambaleo', mezclar(pico(rugido(1.5, 72, 52, sirena=0.6), 0.9), en(0.5, pico(impacto(1.2, 14), 1.0)),
                            en(0.5, pico(chapuzon(2.0), 0.7)), en(0.45, pico(cadena(0.7, 10), 0.3))), limite=0.55)

# ======================================================================
#  AGOTADO: de rodillas, respira con el agua en la garganta. Y LATIDO.
# ======================================================================
d = 2.7
resp = []
for s, (lo, hi, dur_) in ((0.0, (180, 900, 0.8)), (0.95, (150, 700, 1.0))):
    aire = bp(ruido(dur_, 'rosa'), lo, hi) * campana_env(dur_, 1.5)
    gorgoteo = nube(dur_, 260 * campana_env(dur_, 1.5), 2.0, 9.0, beta=1.6)
    resp.append(en(s, sumergir(mezclar(pico(aire, 0.7), pico(gorgoteo, 0.6)), 1100, 0.45)))
guardar('agotado', mezclar(pico(mezclar(*resp), 0.8), en(0.4, pico(latido(52), 0.55)), en(1.75, pico(latido(50), 0.5))))
for i in range(3):
    guardar('latido', mezclar(latido(60 + 6 * i), pico(nube(0.3, 40, 1.5, 4.0), 0.12)), i + 1, alto=0.85)

# ======================================================================
#  LIBERACION: el unico acorde mayor del combate. Suspira, se le caen las
#  cadenas al agua, el mar se calma y canta. Y DISOLVER: espuma de mar.
# ======================================================================
d = 6.8
n = n_(d)
t = t_(d)
coro = np.zeros(n)
for f in (130.8, 196.0, 261.6, 329.6, 392.0, 523.3):
    for j in range(3):
        fv = f * (1 + rng.uniform(-0.004, 0.004)) * (1 + 0.005 * np.sin(2 * np.pi * rng.uniform(4.0, 5.2) * t + rng.uniform(0, 6)))
        fase = 2 * np.pi * np.cumsum(fv) / SR
        src = sum(np.sin(k * fase) / k ** 1.6 for k in range(1, 14) if f * k < 6000)
        coro += src * (0.55 if f < 300 else 0.4)
coro = sum(g * resonar(coro, F, F / bw) for F, bw, g in VOCAL_A) * ventana(d, 1.8, 2.6)
arpa = mezclar(*[en(1.6 + 0.45 * q, modos(f, 2.2, ((1, 1), (2.0, 0.12), (3.0, 0.04)), 1.2)) for q, f in enumerate((659.3, 784.0, 1046.5, 1318.5))])
olas = mezclar(*[en(s, pb(ruido(1.8, 'rosa'), 1300) * campana_env(1.8, 2)) for s in (0.5, 2.2, 3.9)])
suspiro = sumergir(garganta(curva(n_(1.6), [(0, 72), (1, 54)]), 1.6, VOCAL_O, 0.25, 0.15, 0.02, 0.8) * ventana(1.6, 0.3, 0.9), 1200, 0.2)
caen = mezclar(*[en(0.3 + q * 0.22 + rng.uniform(0, 0.05), mezclar(pico(cadena(0.35, 3), 0.5), en(0.12, pico(chapuzon(0.3, 0.5), 0.4))))
                 for q in range(7)])
brillo = nube(4.0, 220 * rampa(4.0, 1.0, 0.3, 1.0), 0.35, 1.4)
guardar('liberacion', reverb(mezclar(pico(suspiro, 0.4), pico(caen, 0.45), en(0.8, pico(coro, 0.6)), pico(arpa, 0.22),
                                     pico(olas, 0.22), en(2.6, pico(brillo, 0.2))), 0.4, 2.8, 6000))

d = 3.4
t = t_(d)
espuma = nube(d, 4200 * np.exp(-t / 1.4), 0.25, 1.0, beta=1.6)
retira = pb(ruido(d, 'rosa'), 2000) * caida(d, 1.1, 0.25)
campanitas = mezclar(*[en(q * 0.18, modos(f, 1.2, CRISTAL, 0.5)) for q, f in enumerate((784, 988, 1175, 1319, 1568, 1976, 2349))])
guardar('disolver', reverb(mezclar(pico(espuma, 0.6), pico(retira, 0.35), pico(campanitas, 0.28)), 0.35, 2.0, 8000))

# ======================================================================
#  REMAKE DE OCTUBRE DE 2026: el Geiser del Abismo, la Gran Marea y la
#  Furia de las Mareas. Con su propia semilla, para que
#  nerea_mejoras_sonidos.py los saque igual sin rehacer los demas.
# ======================================================================
rng = np.random.default_rng(20261007)


def a_largo(x, n):
    """Recorta o rellena con silencio hasta n muestras."""
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def lluvia(dur, tasa):
    """El agua que vuelve a caer: gotas (cada una con su plink) a un ritmo
    que cambia. Como goteo, pero un chaparron entero."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    out = np.zeros(n + n_(0.3))
    for i in np.nonzero(rng.random(n) < tasa / SR)[0]:
        g = gota(amp=rng.uniform(0.15, 1.0))
        out[i:i + len(g)] += g[:len(out) - i]
    return np.trim_zeros(out, 'b')


def sorber(dur, tasa0, tasa1, rmin=0.6, rmax=4.0):
    """Burbujas al reves: el agua que se va sorbida, o que se traga. Lo que
    se oye va de tasa0 a tasa1 burbujas por segundo."""
    n = n_(dur)
    return a_largo(nube(dur, rampa(dur, 1.0, tasa1, tasa0), rmin, rmax), n)[::-1]


def presion_sube(dur, f0, f1, armonicos=6):
    """La presion que sube de tono: un zumbido grave y armonico, como el de
    la Mirada, para la tension antes de que reviente algo."""
    f = curva(n_(dur), [(0, f0), (1, f1)])
    return bp(sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in range(1, armonicos + 1)), 40, 700)


def borboton(fuerza=1.0):
    """Un borboton del fondo: una bocanada de burbujas, un gorgoteo hondo y
    el golpe sordo del agua que se levanta."""
    dd = 0.32
    tt = t_(dd)
    whump = np.sin(2 * np.pi * np.cumsum(68 * (0.6 + 0.4 * np.exp(-tt / 0.04))) / SR) * caida(dd, 0.05, 0.004)
    return fuerza * mezclar(pico(nube(dd, 1500 * np.exp(-tt / 0.08), 0.9, 5.0), 0.6),
                            pico(burbuja(rng.uniform(12, 18), 0.18, 1.0, 1.2), 0.7), pico(whump, 0.5))


# GEISER_AVISO: clava el tridente y bajo los pies se abre un remolino
# oscuro. El fondo empieza a hervir: borbotones cada vez mas seguidos,
# gorgoteos hondos, un retumbo que crece y late cada vez mas deprisa, la
# roca que cruje, la presion que sube de tono y el silbido del agua que
# empuja por las grietas. Acaba en lo mas tenso, justo antes de reventar.
for i in range(3):
    d = 1.5 + 0.1 * i
    n = n_(d)
    t = t_(d)
    k = t / d
    borbotones = np.zeros(n + n_(1.0))
    s, paso_ = 0.04, 0.48 - 0.03 * i
    while s < d - 0.12:
        b = borboton(0.25 + 0.75 * s / d)
        i0 = n_(s)
        borbotones[i0:i0 + len(b)] += b[:len(borbotones) - i0]
        s += paso_
        paso_ = max(0.09, paso_ * 0.7)
    glugs = a_largo(nube(d, 4 + (26 + 4 * i) * k ** 1.3, 8.0, 20.0, beta=1.5, xi=0.14, amortigua=1.3), n) * (0.3 + 0.7 * k)
    hervor = a_largo(nube(d, 30 + 2200 * k ** 2.4, 0.8, 4.0), n)
    late = 1 + 0.5 * np.sin(2 * np.pi * np.cumsum(3 + 9 * k ** 1.5) / SR)
    retumbo = filtro_mov(ruido(d, 'marron'), 70 + 200 * k ** 1.5, 'low', 0.9) * (0.06 + 0.94 * k ** 2) * late
    sube = presion_sube(d, 36 + 3 * i, 72 + 4 * i) * k ** 2.5
    silba = filtro_mov(ruido(d), curva(n, [(0, 500), (1, 3200)]), 'band', 1.2) * k ** 3
    roca = crujir(d, (12, 60), ((160, 18), (350, 22), (620, 26)), 1.0) * k ** 1.5
    aviso = mezclar(pico(a_largo(borbotones, n), 0.8), pico(glugs, 0.6), pico(hervor, 0.45), pico(retumbo, 0.6),
                    pico(sube, 0.3), pico(silba, 0.3), pico(roca, 0.15))
    guardar('geiser_aviso', reverb(aviso, 0.2, 1.2, 2500)[:n] * ventana(d, 0.02, 0.05), i + 1, limite=0.6)

# GEISER: revienta. El estampido sordo de la presion que se suelta y la
# roca que salta, la columna de agua que sube rugiendo (el soplo sube de
# tono), la cresta que se deshace en rocio, el agua que se desploma a
# trozos y la lluvia de gotas que sigue cayendo.
for i in range(2):
    d = 2.2
    n = n_(d)
    estampido = mezclar(pico(pa(ruido(0.025), 700) * caida(0.025, 0.005), 0.9), pico(boom(84 - 8 * i, 28, 0.25), 1.0),
                        pico(rajar(10, 0.05, 300, 3500), 0.45), pico(chapuzon(1.6, 0.5), 0.5))
    dc = 0.8
    tc = t_(dc)
    forma = np.interp(tc, [0, 0.03, 0.35, dc], [0.5, 0.9, 1.0, 0.0])
    barrido = curva(n_(dc), [(0, 240 + 40 * i), (0.6, 2000), (1, 5000)])
    soplo = mezclar(pico(filtro_mov(ruido(dc, 'rosa'), barrido, 'band', 2.5), 1.0),
                    pico(filtro_mov(ruido(dc, 'rosa'), barrido * 2.3, 'band', 3.0), 0.5)) * forma
    chorro_ = mezclar(pico(nube(dc, 3000 * forma ** 2, 0.5, 5.0), 1.0), pico(ruido(dc, 'rosa') * forma ** 2, 0.5))
    chorro_ = filtro_mov(a_largo(chorro_, n_(dc)), barrido * 2 + 600, 'low', 0.7)
    rocio = pa(ruido(0.7), 3000) * np.interp(t_(0.7), [0, 0.12, 0.35, 0.7], [0, 1, 0.4, 0])
    grave = pb(ruido(0.5, 'marron'), 150) * caida(0.5, 0.09, 0.01)
    cae = mezclar(pico(chapuzon(2.3), 1.0), en(0.1, pico(chapuzon(1.6), 0.6)), en(0.22, pico(chapuzon(1.0), 0.45)))
    tl = t_(1.4)
    gotas = mezclar(pico(lluvia(1.4, 900 * np.exp(-tl / 0.4) + 20), 1.0), pico(pa(ruido(1.4), 3500) * np.exp(-tl / 0.35), 0.25))
    geiser = mezclar(estampido, pico(soplo, 1.0), pico(chorro_, 0.45), pico(grave, 0.3), en(0.42, pico(rocio, 0.35)),
                     en(0.66 + 0.05 * i, pico(cae, 1.0)), en(0.76, pico(gotas, 0.5)))
    guardar('geiser', reverb(geiser, 0.15, 1.3, 4500)[:n] * ventana(d, 0.001, 0.3), i + 1, limite=0.5)

# MAREA_ALZA: alza el tridente y el mar se retira antes de la ola. El agua
# que se va sorbida por el fondo (la resaca sobre la grava, gorgoteos que
# desaguan), un retumbo hondo que crece y, lejos, el rugido de la ola que
# se levanta. La tension sube hasta el final.
d = 2.6
n = n_(d)
t = t_(d)
k = t / d
alza = mezclar(pico(zumbido(0.9, [(0, 240), (0.6, 1100), (1, 1700)], 1.2), 0.3), pico(cadena(0.7, 7), 0.15),
               en(0.25, goteo(1.3, 8, 0.0, 0.22, False)))
dr = 1.9
tr = t_(dr)
se_va = np.interp(tr, [0, 0.2, dr], [0, 1, 0]) ** 1.4
resaca = filtro_mov(ruido(dr, 'rosa'), curva(n_(dr), [(0, 3600), (0.35, 1600), (1, 350)]), 'low', 0.8) * se_va
grava = mezclar(*[en(rng.uniform(0, dr) ** 1.6 / dr ** 0.6, bp(ruido(0.005), 1800, 6500) * caida(0.005, 0.001) * rng.uniform(0.2, 1))
                  for _ in range(70)])
desague = nube(dr, rampa(dr, 1.0, 14, 3), 10.0, 24.0, beta=1.4, xi=0.15, amortigua=1.5)
retumbo = pb(ruido(d, 'marron'), 110) * (0.03 + 0.97 * k ** 1.8)
rugir = filtro_mov(pa(ruido(d, 'rosa'), 150), curva(n, [(0, 500), (1, 1600)]), 'low', 0.8) * k ** 1.6
rugir = reverb(rugir * (1 + 0.3 * np.sin(2 * np.pi * 0.9 * t)), 0.65, 2.6, 1500)[:n]
tension = presion_sube(d, 40, 60) * k ** 2.5
siseo = pa(ruido(dr), 1800) * se_va ** 1.5 * (1 + 0.3 * suave(n_(dr), 8))
se_retira = mezclar(alza, pico(resaca, 0.45), pico(siseo, 0.25), pico(sorber(dr, 1800, 30) * se_va, 0.32), pico(grava, 0.2),
                    pico(desague, 0.3))
alzada = mezclar(0.7 * se_retira, pico(retumbo, 0.45), pico(rugir, 1.0), pico(tension, 0.25))
guardar('marea_alza', reverb(alzada, 0.25, 1.8, 2500)[:n] * ventana(d, 0.005, 0.1), limite=0.6)

# MAREA: la Gran Marea. Se la oye venir de lejos (el rugido crece y se
# aclara al acercarse), rompe con un estruendo que hace temblar el suelo y
# se deshace en una cola larga de espuma que sisea y se retira.
for i in range(2):
    d = 4.5
    n = n_(d)
    t = t_(d)
    cresta = 1.7 + 0.2 * i
    acerca = np.clip(t / cresta, 0, 1)
    tras = np.maximum(0.0, t - cresta)
    antes = t < cresta
    rugir = filtro_mov(pa(ruido(d, 'rosa'), 110), 400 + 5600 * acerca ** 2, 'low', 0.7) * np.where(antes, acerca ** 2.2, np.exp(-tras / 0.5))
    trueno = pb(ruido(d, 'marron'), 120) * np.where(antes, acerca ** 2, np.exp(-tras / 0.5))
    choque = mezclar(pico(pa(ruido(0.03), 500) * caida(0.03, 0.006), 0.8), pico(boom(46, 20, 0.5), 1.0),
                     pico(bp(ruido(0.7), 80, 9000) * caida(0.7, 0.16, 0.003), 1.0),
                     pico(chapuzon(2.6), 0.9), en(0.22, pico(chapuzon(1.8), 0.6)), en(0.5, pico(chapuzon(1.2), 0.4)))
    espuma = nube(d, np.where(antes, 0.0, 6000 * np.exp(-tras / 1.5)), 0.22, 1.1, beta=1.6)
    medias = nube(d, np.where(antes, 0.0, 500 * np.exp(-tras / 1.0)), 1.2, 5.0)
    siseo = pa(ruido(d), 2000) * np.where(antes, 0.0, np.exp(-tras / 1.4)) * (1 + 0.35 * suave(n, 5))
    retira = filtro_mov(ruido(d, 'rosa'), 400 + 2800 * np.exp(-tras / 1.1), 'low', 0.8) * np.where(antes, 0.0, np.exp(-tras / 1.3))
    marea = mezclar(pico(rompiente(d, cresta, 1.0), 0.6), pico(rugir, 0.6), pico(trueno, 0.35), en(cresta - 0.02, choque),
                    pico(espuma, 0.7), pico(medias, 0.3), pico(siseo, 0.55), pico(retira, 0.4), goteo(2.2, 16, cresta + 0.3, 0.25))
    guardar('marea', reverb(marea, 0.3, 2.4, 4000)[:n] * ventana(d, 0.01, 0.9), i + 1, limite=0.5)

# FURIA: entra en la Furia de las Mareas. Traga agua, suelta un estampido
# hondo de presion, el mar se le arremolina alrededor y ruge con su voz de
# siempre, pero mas alta y mas rabiosa, con un grunido de garganta debajo
# y las cadenas sacudiendose.
d = 3.5
di = 0.4
traga = mezclar(pico(sorber(di, 60, 2000), 0.7), pico(zumbido(di, [(0, 300), (1, 1300)], 1.3) * rampa(di, 1.5), 0.45),
                pico(pb(ruido(di, 'marron'), 200) * rampa(di, 2.0), 0.3))
golpe = mezclar(pico(boom(46, 18, 0.5, 2.0), 1.0), pico(pb(ruido(0.7, 'marron'), 260) * caida(0.7, 0.16, 0.004), 0.6),
                pico(chapuzon(2.4), 0.55))
do = 3.0
oleada = flanger(pa(torrente(do, 2600, 6.0, 3600), 150), rampa(do, 1.0, 0.6, 1.4), 1.2, 6.0, 0.7)
oleada *= np.interp(t_(do), [0, 0.25, 1.4, 2.5, do], [0, 1, 0.8, 0.35, 0])
dv = 2.3
rabia = garganta(curva(n_(dv), [(0, 34), (0.25, 48), (0.7, 45), (1, 30)]), dv, VOCAL_O, 0.9, 0.8, 0.05, 0.4)
rabia = sumergir(rabia * ventana(dv, 0.15, 0.9), 1400, 0.35)
furia = mezclar(pico(traga, 0.55), en(di - 0.04, pico(golpe, 0.6)), en(di, pico(oleada, 0.35)),
                en(di + 0.06, pico(rugido(2.8, 54, 96, sirena=1.6, agua=1.4), 1.0)), en(di + 0.15, pico(rabia, 0.18)),
                en(di + 0.1, pico(cadena(1.6, 18), 0.22)), goteo(0.9, 8, 2.5, 0.2))
guardar('furia', reverb(furia, 0.2, 2.0, 3000)[:n_(d)] * ventana(d, 0.005, 0.6), limite=0.55)

# ----------------------------------------------------------------------
#  sounds.json: los eventos nerea.* con sus variantes y subtitulo
# ----------------------------------------------------------------------
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for k in [k for k in datos if k.startswith('nerea.')]:
    del datos[k]
for ev, archivos in EVENTOS.items():
    datos['nerea.' + ev] = {'subtitle': 'subtitles.atalaya.nerea.' + ev,
                            'sounds': ['atalaya:nerea/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')

# ----------------------------------------------------------------------
#  Hoja de espectrogramas, para revisar sin escuchar
# ----------------------------------------------------------------------
if len(sys.argv) > 2:
    from PIL import Image, ImageDraw
    an, al, col = 300, 110, 5
    filas = (len(GUARDADOS) + col - 1) // col
    hoja = Image.new('RGB', (an * col, (al + 14) * filas), (12, 14, 18))
    dib = ImageDraw.Draw(hoja)
    for k, (nombre, x) in enumerate(GUARDADOS):
        f, tt, S = signal.spectrogram(x, SR, nperseg=1024, noverlap=768)
        S = 10 * np.log10(S + 1e-12)
        S = np.clip((S - (S.max() - 65)) / 65, 0, 1)
        # eje de frecuencia logaritmico, 30 Hz a 16 kHz
        fl = np.geomspace(30, 16000, al)
        idx = np.clip(np.searchsorted(f, fl), 0, len(f) - 1)
        img = (S[idx][::-1] * 255).astype(np.uint8)
        im = Image.fromarray(img).resize((an - 4, al), Image.BILINEAR)
        cx, cy = (k % col) * an, (k // col) * (al + 14)
        hoja.paste(Image.merge('RGB', (im, im.point(lambda v: int(v * 0.8)), im.point(lambda v: min(255, int(v * 1.3))))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9):.0f}dB', fill=(220, 220, 220))
    hoja.save(sys.argv[2])
