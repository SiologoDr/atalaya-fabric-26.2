"""
Sonidos de Aeralis, la Mariposa del Vendaval. Sintetizados desde cero: nada
de vanilla ni de bancos de sonido.

Todo sale del AIRE, modelado con su fisica:

  - VIENTO: turbulencia (ruido rosa) que pasa por una banda que se mueve con
    las rachas. Cuanto mas rapido el aire, mas aguda y ancha la banda.
  - SILBIDOS: el aire que se parte en una arista suelta remolinos a un ritmo
    fijo (tonos eolicos, f = 0,2 * velocidad / grosor): una banda estrechisima
    que canta y tiembla con la racha.
  - ALETAZOS: una membrana enorme que empuja el aire: el golpe de presion
    grave, el soplo que se abre y se cierra, el flameo de la membrana (como
    una vela) y el chasquido cuando se tensa al final de la batida.
  - TORNADOS: rugido grave, la rotacion que hace latir el sonido, silbidos
    que suben con la velocidad y el polvo y la grava que vuelan dentro.
  - TRUENOS y ESTALLIDOS DE PRESION: el chasquido de la descarga, el retumbo
    que rueda y el aire que vuelve de golpe al hueco.

La VOZ es la de un insecto del tamano de una tormenta: la quitina que raspa
(estridulacion, como una cigarra gigante), una garganta aguda y aspera, un
rugido grave debajo que le da tamano y el viento de sus alas.

Escribe los .ogg (mono, para que se oigan en 3D) en
assets/atalaya/sounds/aeralis/ y sus eventos en sounds.json
(aeralis.<evento>, subtitulo subtitles.atalaya.aeralis.<evento>).

Uso: python aeralis_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png]
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator
import os, sys, json, collections

SR = 44100
RAIZ = sys.argv[1]
OUT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/aeralis')
os.makedirs(OUT, exist_ok=True)
for viejo in os.listdir(OUT):
    if viejo.endswith('.ogg'):
        os.remove(os.path.join(OUT, viejo))
rng = np.random.default_rng(20261004)
EVENTOS = collections.OrderedDict()
GUARDADOS = []


# ======================================================================
#  Utilidades (las mismas que los sonidos de Nerea)
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
    """Ruido lento (por debajo de fc), de desviacion 1: rachas, temblores."""
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
    """Biquad (RBJ) con la frecuencia moviendose: rachas, barridos, silbidos."""
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


def flanger(x, lfo_hz, base_ms=1.5, prof_ms=5.0, mezcla=0.7):
    """Peine que se mueve: el aire girando."""
    n = len(x)
    lfo = np.broadcast_to(np.asarray(lfo_hz, dtype=float), (n,))
    fase = 2 * np.pi * np.cumsum(lfo) / SR
    idx = np.arange(n)
    d1 = (base_ms + prof_ms * (0.5 + 0.5 * np.sin(fase))) * SR / 1000
    d2 = (base_ms + prof_ms * (0.5 + 0.5 * np.sin(fase + 2.1))) * SR / 1000
    y1 = np.interp(idx - d1, idx, x, left=0)
    y2 = np.interp(idx - d2, idx, x, left=0)
    return x + mezcla * y1 - 0.5 * mezcla * y2


# ---------------------------------------------------------------- reverb
_IRS = {}


def respuesta(cola, oscuro):
    """Cielo abierto en la cima: casi nada cerca, una cola difusa que se lleva
    los agudos y dos ecos lejanos que devuelven las laderas."""
    clave = (round(cola, 2), int(oscuro))
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro))
        x = r.standard_normal(len(t))
        h = (pb(x, 600) * np.exp(-6.9 * t / cola)
             + bp(x, 600, 3500) * np.exp(-6.9 * t / (cola * 0.6)) * 0.7
             + pa(x, 3500) * np.exp(-6.9 * t / (cola * 0.25)) * 0.4)
        h = pb(h, oscuro)
        a = n_(0.025)
        h[:a] *= np.linspace(0, 1, a) ** 2
        for seg, g in ((0.31, 0.5), (0.74, 0.3)):
            if seg < cola * 0.9:
                i = n_(seg)
                eco = pb(r.standard_normal(n_(0.06)), 1400) * np.exp(-t_(0.06) / 0.015)
                h[i:i + len(eco)] += g * eco * np.max(np.abs(h[:n_(0.05)] + 1e-9)) * 3
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


def reverb(x, mezcla=0.25, cola=1.8, oscuro=7000):
    h = respuesta(cola, oscuro)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


# ======================================================================
#  AIRE
# ======================================================================
def viento(dur, puntos, q=1.0, racheo=0.6, color='rosa'):
    """Viento: turbulencia por una banda que sube y baja con las rachas."""
    n = n_(dur)
    f = curva(n, puntos) * np.exp(0.18 * racheo * suave(n, 0.9))
    x = filtro_mov(ruido(dur, color), f, 'band', q)
    g = np.exp(0.55 * racheo * suave(n, 0.6))
    return x * g


def aullido(dur, puntos, q=18.0, temblor=0.025, bloque=32, mult=1.0):
    """El viento que canta en una arista: una banda estrechisima que tiembla."""
    n = n_(dur)
    f = curva(n, puntos) * mult * (1 + temblor * suave(n, 3))
    return filtro_mov(ruido(dur), f, 'band', q, bloque) * (0.55 + 0.45 * np.abs(suave(n, 1.6)))


def pasada(dur, f0, f1, q=1.8, silba=0.25):
    """Algo que pasa rapido cortando el aire: la banda cae (Doppler) y silba."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.45, (f0 * f1) ** 0.5 * 1.15), (1, f1)])
    soplo = filtro_mov(ruido(dur, 'rosa'), f, 'band', q)
    canta = filtro_mov(ruido(dur), f * 1.6, 'band', 22, 32)
    e = campana_env(dur, 1.3) ** 1.4
    return mezclar(pico(soplo * e, 1.0), pico(canta * e, silba))


_GRANOS = []


def _granos():
    if not _GRANOS:
        for k in range(10):
            d = 0.004 + 0.004 * (k % 3)
            lo = 900 + 450 * k
            _GRANOS.append(bp(ruido(d), lo, min(lo * 3.2, 14000)) * caida(d, d * 0.22, 0.0002))
    return _GRANOS


def granos(dur, tasa, amp=1.0):
    """Polvo, arena y grava que lleva el viento: chasquidos minimos al azar."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(0.02))
    gs = _granos()
    for i in cuando:
        g = gs[rng.integers(len(gs))] * rng.uniform(0.15, 1.0)
        out[i:i + len(g)] += g
    return amp * out[:n]


def aletazo(tam=1.0, fuerza=1.0):
    """Una batida de un ala de diez bloques: golpe de presion, soplo, flameo de
    la membrana y el chasquido cuando se tensa."""
    d = 0.5 + 0.45 * tam
    n = n_(d)
    t = t_(d)
    sube = 0.15 * tam
    env = np.where(t < sube, (t / sube) ** 1.6, np.exp(-(t - sube) / (0.13 * tam)))
    env *= ventana(d, 0.001, d * 0.25)
    aire = filtro_mov(ruido(d, 'rosa'), 160 + 2300 * env ** 1.3 * fuerza, 'low', 0.9) * env
    tw = t_(0.4)
    whump = np.sin(2 * np.pi * np.cumsum(26 + 46 * np.exp(-tw / 0.06)) / SR) * caida(0.4, 0.075 * tam, 0.012)
    aleteo_ = 0.5 + 0.5 * np.sin(2 * np.pi * (21.0 / tam) * t + 1.5 * suave(n, 6))
    flameo = bp(ruido(d), 320, 2600) * aleteo_ ** 3 * env
    snap = bp(ruido(0.05), 700, 3600) * caida(0.05, 0.008, 0.001)
    return mezclar(pico(aire, 1.0), en(sube * 0.7, pico(whump, 0.75 * fuerza)), pico(flameo, 0.26),
                   en(sube * 1.05, pico(snap, 0.2 * fuerza)))


def eolica(dur, f_base, armonicos=(2, 3, 4, 5, 6, 7, 8, 9), lento=0.5, brillo=1.0):
    """Arpa eolica: una cuerda que el viento hace cantar. Los armonicos entran
    y salen con la racha; nunca suenan todos a la vez."""
    n = n_(dur)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in armonicos:
        if f_base * k > 9000:
            continue
        g = np.clip(0.35 + 0.65 * suave(n, lento), 0, None) ** 2
        f = f_base * k * (1 + 0.0015 * suave(n, 3))
        s += g * np.sin(2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6)) / k ** (0.9 / brillo)
    return s


def tornado(dur, giro=2.5, fuerza=1.0, brillo=1.0, polvo=1.0):
    """Un tornado: rugido grave, la rotacion que lo hace latir, silbidos que
    suben con la velocidad y lo que arrastra dentro."""
    n = n_(dur)
    giro = np.broadcast_to(np.asarray(giro, dtype=float), (n,))
    fase = 2 * np.pi * np.cumsum(giro) / SR
    rot = 0.62 + 0.38 * np.sin(fase)
    brillo = np.broadcast_to(np.asarray(brillo, dtype=float), (n,))
    retumbo = pb(ruido(dur, 'marron'), 150) * (0.8 + 0.2 * suave(n, 1.0))
    rugido = filtro_mov(ruido(dur, 'rosa'), (480 + 260 * np.sin(fase + 1.0)) * brillo, 'band', 0.75) * rot
    silb = aullido(dur, [(0, 720), (0.5, 980), (1, 860)], 14, mult=brillo) * (0.6 + 0.4 * np.sin(fase + 2.0))
    silb2 = aullido(dur, [(0, 1500), (1, 1750)], 24, mult=brillo)
    restos = granos(dur, 40 * polvo * fuerza) * rot
    return mezclar(pico(retumbo, 0.75), pico(rugido, 0.85), pico(silb, 0.26), pico(silb2, 0.12), pico(restos, 0.32 * polvo))


def boom(f0=60, f1=26, tau=0.25, dur=None):
    """El golpe de presion: el aire empujado de golpe contra el pecho."""
    dur = dur or tau * 5
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) + 0.25 * np.sin(2 * fase)) * caida(dur, tau, 0.003)


def trueno(dur=3.2, cerca=1.0):
    """Un trueno: el chasquido de la descarga y el retumbo que rueda."""
    n = n_(dur)
    t = t_(dur)
    crack = mezclar(*[en(rng.uniform(0, 1) ** 2 * 0.22, pa(ruido(0.014), 1100) * caida(0.014, 0.0035) * rng.uniform(0.25, 1))
                      for _ in range(int(25 + 40 * cerca))])
    env = np.zeros(n)
    for k in range(6):
        c = 0.05 + rng.uniform(0, 0.55) * dur * (0.4 + 0.12 * k)
        a = rng.uniform(0.4, 1.0) * np.exp(-k * 0.25)
        env += a * np.exp(-((t - c) / (0.12 + 0.1 * k)) ** 2)
    env = (env + 0.9 * np.exp(-t / (dur * 0.35))) * caida(dur, dur * 0.45, 0.01)
    retumbo = pb(ruido(dur, 'marron'), 150 + 260 * cerca) * env * (0.85 + 0.15 * suave(n, 4))
    medio = bp(ruido(dur, 'rosa'), 160, 1100 + 900 * cerca) * env ** 1.6
    return mezclar(pico(crack, 0.75 * cerca), pico(retumbo, 1.0), pico(medio, 0.45))


def estallido(fuerza=1.0, dur=2.4):
    """Explosion de presion: el golpe, el chasquido, el aire que vuelve al
    hueco y el polvo que se dispersa."""
    t = t_(dur)
    golpe = boom(54, 21, 0.42 * fuerza, dur)
    crack = bp(ruido(0.35), 70, 9500) * caida(0.35, 0.035, 0.001)
    rebufo = filtro_mov(ruido(dur, 'rosa'), curva(n_(dur), [(0, 300), (0.12, 2600), (0.5, 900), (1, 300)]), 'low', 0.9)
    rebufo *= np.interp(t, [0, 0.08, 0.3, dur], [0, 1, 0.6, 0]) ** 1.3
    polvo = granos(dur, 600 * np.exp(-t / (0.5 * fuerza)))
    return mezclar(pico(golpe, 1.0), pico(crack, 0.75), pico(rebufo, 0.7), pico(polvo, 0.3))


def chirrido(dur, tasa=(48, 75), resonancias=((2700, 9), (3900, 11), (5200, 13)), fuerza=1.0):
    """Estridulacion: la quitina raspando contra la quitina. Un tren de
    chasquidos muy seguidos que hace sonar unas resonancias agudas."""
    n = n_(dur)
    ritmo = tasa[0] + (tasa[1] - tasa[0]) * (0.5 + 0.5 * np.tanh(suave(n, 2.5)))
    fase = np.cumsum(ritmo) / SR
    pulsos = np.zeros(n)
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    pulsos[golpes] = rng.uniform(0.4, 1.0, len(golpes))
    exc = pulsos + 0.015 * rng.standard_normal(n)
    out = sum(resonar(exc, f, q) * rng.uniform(0.6, 1.0) for f, q in resonancias)
    return fuerza * out * (0.6 + 0.4 * np.abs(suave(n, 3)))


def crujir_quitina(dur, fuerza=1.0):
    """La coraza que cruje al moverse: chasquidos secos y graves."""
    n = n_(dur)
    out = np.zeros(n + n_(0.05))
    for s in np.sort(rng.uniform(0, dur * 0.95, int(10 + 18 * dur))):
        c = sum(resonar(np.r_[1.0, np.zeros(n_(0.03))], f, 18) for f in (rng.uniform(380, 700), rng.uniform(1100, 1900)))
        i = n_(s)
        out[i:i + len(c)] += c * rng.uniform(0.2, 1.0)
    return fuerza * out[:n]


# ======================================================================
#  VOZ
# ======================================================================
VOCAL_O = ((300, 90, 1.0), (680, 110, 0.75), (1500, 160, 0.35), (2500, 200, 0.18))
VOCAL_A = ((620, 110, 1.0), (1050, 130, 0.8), (2300, 190, 0.35), (3100, 240, 0.15))


def garganta(f0, dur, formantes=VOCAL_O, aspereza=0.5, sub=0.4, jitter=0.03, aliento=0.25, fmax=5000):
    """Pulsos con jitter, un subarmonico que los raspa y formantes (los F
    pueden ser curvas)."""
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


def chillido(dur=1.9, f0=430, f1=660, grave=64, fuerza=1.0, alas=1.0, cola=2.2):
    """El chillido de Aeralis: una garganta de insecto aguda y aspera (que se
    desdobla, como dos voces), un rugido grave que le da tamano, la quitina
    raspando y el viento de las alas al abrirse."""
    n = n_(dur)
    tono = curva(n, [(0, f0), (0.16, f1), (0.62, f1 * 0.93), (1, f0 * 0.78)])
    F1 = curva(n, [(0, 480), (0.2, 820), (0.7, 700), (1, 520)])
    F2 = curva(n, [(0, 2100), (0.2, 1450), (0.7, 1350), (1, 1900)])
    voz_ = garganta(tono, dur, ((F1, 120, 1.0), (F2, 170, 0.75), (2900, 260, 0.45), (3900, 330, 0.25)),
                    aspereza=0.9, sub=0.55, jitter=0.045, aliento=0.45, fmax=9500)
    voz_ = flanger(voz_, 0.35, 2.0, 6.0, 0.55)
    e = ventana(dur, 0.07, dur * 0.42)
    hondo = garganta(curva(n, [(0, grave), (0.2, grave * 1.3), (1, grave * 0.85)]), dur, VOCAL_O, 0.75, 0.65, 0.035, 0.35)
    raspa = chirrido(dur, (55, 90), ((3100, 9), (4400, 11), (6100, 13))) * e
    viento_ = viento(dur, [(0, 400), (0.18, 2000), (1, 700)], 0.8, 0.4) * e
    capas = mezclar(pico(voz_ * e, 1.0 * fuerza), pico(hondo * e, 0.55), pico(raspa, 0.26), pico(viento_, 0.3 * alas),
                    pico(boom(46, 30, 0.35), 0.35))
    return reverb(capas, 0.3, cola, 7000)


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
#  AMBIENTE: alrededor de ella siempre sopla. Rachas, silbidos en las
#  aristas, una batida lejana y el polvo que pasa.
# ======================================================================
for i in range(3):
    d = 4.5
    n = n_(d)
    fondo = viento(d, [(0, 260), (0.5, 380 + 40 * i), (1, 300)], 0.7, 0.9)
    alto_ = viento(d, [(0, 1300), (0.4, 1900), (1, 1500)], 1.4, 1.1) * np.clip(suave(n, 0.5), 0, None)
    canta = aullido(d, [(0, 620 + 60 * i), (0.35, 780 + 50 * i), (0.7, 700), (1, 560 + 40 * i)], 20) * campana_env(d, 1.2)
    canta2 = aullido(d, [(0, 1180 + 90 * i), (1, 1040)], 28) * np.clip(suave(n, 0.4), 0, None)
    lejos = pb(en(rng.uniform(0.8, 2.4), aletazo(1.3, 0.7)), 1400)
    polvo = granos(d, 35 * (0.6 + 0.4 * np.clip(suave(n, 0.7), -1, 1)))
    capas = mezclar(pico(fondo, 0.6), pico(alto_, 0.25), pico(canta, 0.2), pico(canta2, 0.1), pico(lejos, 0.35),
                    pico(polvo, 0.12))
    guardar('ambiente', reverb(capas * ventana(len(capas) / SR, 0.5, 0.9), 0.35, 2.4, 6000), i + 1, alto=0.7)

# ======================================================================
#  ALETEO: la batida del vuelo (el cliente la pone con cada golpe de alas)
# ======================================================================
for i in range(4):
    a = aletazo(1.25 + 0.08 * i, 0.9)
    cola_ = viento(1.0, [(0, 900), (1, 400)], 1.0, 0.3) * caida(1.0, 0.25, 0.08)
    guardar('aleteo', reverb(mezclar(pico(a, 1.0), en(0.12, pico(cola_, 0.25))), 0.2, 1.4, 6000), i + 1, limite=0.65)

# ======================================================================
#  INMUNE: le pegas dormida o despertando. El golpe resbala en la quitina
#  y el viento que la envuelve lo desvia.
# ======================================================================
for i in range(3):
    golpe = mezclar(pico(pb(ruido(0.07), 3200) * caida(0.07, 0.007), 1.0), pico(boom(210, 140, 0.035), 0.4))
    quitina = sum(resonar(np.r_[1.0, np.zeros(n_(0.25))], f, 30) for f in (720 + 80 * i, 1650 + 120 * i, 2900))
    desvia = pasada(0.45, 3800, 900, 2.2, 0.3)
    guardar('inmune', mezclar(golpe, pico(quitina, 0.35), en(0.01, pico(desvia, 0.55))), i + 1)

# ======================================================================
#  HERIDO: le entra el golpe. Crujido de quitina, chirrido de dolor y un
#  aletazo brusco.
# ======================================================================
for i in range(4):
    golpe = mezclar(pico(pb(ruido(0.12), 2200) * caida(0.12, 0.013), 0.7), pico(boom(110, 55, 0.07), 0.6))
    cruje = crujir_quitina(0.25, 1.0) * caida(0.25, 0.08)
    d = 0.75
    queja = garganta(curva(n_(d), [(0, 560 + 40 * i), (0.25, 690 + 40 * i), (1, 430)]), d,
                     ((700, 120, 1.0), (1700, 170, 0.7), (3000, 260, 0.4)), 0.85, 0.5, 0.05, 0.5, 8000)
    queja *= caida(d, 0.2, 0.02)
    raspa = chirrido(0.4, (70, 110)) * caida(0.4, 0.12, 0.01)
    sacude = aletazo(0.8, 0.8)
    guardar('herido', reverb(mezclar(golpe, pico(cruje, 0.35), en(0.03, pico(queja, 0.75)), en(0.02, pico(raspa, 0.25)),
                                     en(0.06, pico(sacude, 0.4))), 0.2, 1.5, 7000), i + 1, limite=0.6)

# ======================================================================
#  CHILLIDO
# ======================================================================
guardar('chillido', chillido(1.9, 430, 660, 64), 1, limite=0.6)
guardar('chillido', chillido(1.7, 470, 720, 70, alas=1.3), 2, limite=0.6)
guardar('chillido', chillido(2.1, 400, 610, 58, fuerza=1.1), 3, limite=0.6)

# ======================================================================
#  DESPERTAR: las alas plegadas crujen, se despliegan con un flameo, dos
#  batidas enormes la levantan del suelo y chilla.
# ======================================================================
d = 4.6
t = t_(d)
roce = granos(d, np.interp(t, [0, 0.4, 1.3, 1.6, d], [0, 260, 500, 0, 0]))
cruje = crujir_quitina(1.4, 1.0) * rampa(1.4, 1.0, 0.3, 1.0)
despliega = bp(ruido(0.9), 300, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t_(0.9))) ** 3 * campana_env(0.9, 1.0)
batidas = mezclar(en(1.25, pico(aletazo(1.6, 1.2), 1.0)), en(1.75, pico(aletazo(1.5, 1.1), 0.85)))
levanta = viento(2.0, [(0, 300), (0.4, 1600), (1, 500)], 0.8, 0.5) * campana_env(2.0, 1.2)
polvo = granos(2.2, 900 * np.exp(-t_(2.2) / 0.6))
guardar('despertar', mezclar(pico(roce, 0.25), pico(cruje, 0.35), en(0.85, pico(despliega, 0.35)), pico(batidas, 0.9),
                             en(1.2, pico(levanta, 0.5)), en(1.3, pico(polvo, 0.3)),
                             en(2.1, pico(chillido(2.2, 420, 680, 60), 1.0))), limite=0.6)

# ======================================================================
#  ALETEO CORTANTE: echa las alas atras (el aire se tensa y silba hacia
#  dentro) y las lanza: un soplo enorme y las cuchillas que salen cortando.
# ======================================================================
for i in range(2):
    d = 0.75
    n = n_(d)
    sorbe = viento(d, [(0, 350), (1, 2600 + 300 * i)], 1.3, 0.2) * rampa(d, 2.2, 0.05)
    tensa = aullido(d, [(0, 900 + 100 * i), (1, 2400 + 200 * i)], 12) * rampa(d, 2.0)
    cruje = crujir_quitina(0.6, 0.6) * rampa(0.6, 1.0, 0.2, 1.0)
    corte = ventana(d, 0.001, 0.07)
    guardar('aleteo_carga', reverb(mezclar(pico(sorbe * corte, 0.8), pico(tensa * corte, 0.45), en(0.1, pico(cruje, 0.25))),
                                   0.25, 1.6), i + 1)
for i in range(2):
    golpe = mezclar(pico(aletazo(1.9, 1.4), 1.0), en(0.02, pico(aletazo(1.7, 1.2), 0.8)))
    cortes = mezclar(*[en(0.12 + 0.07 * k + rng.uniform(0, 0.03), pico(pasada(0.55, 6500 - 400 * k, 1300, 3.0, 0.5), 0.6))
                       for k in range(4)])
    silbido_ = aullido(1.1, [(0, 3200 + 200 * i), (1, 1400)], 30) * caida(1.1, 0.35, 0.05)
    guardar('aleteo_corte', reverb(mezclar(golpe, cortes, en(0.1, pico(silbido_, 0.3))), 0.25, 1.9), i + 1, limite=0.6)

# Una cuchilla que te da: el corte seco, el aire que se abre y te empuja.
for i in range(3):
    corte = bp(ruido(0.09), 2500, 11000) * caida(0.09, 0.012, 0.001)
    soplo = pasada(0.5, 5000 - 500 * i, 700, 2.0, 0.35)
    golpe = boom(120, 60, 0.06)
    guardar('cuchilla_golpe', mezclar(pico(corte, 0.9), pico(soplo, 0.8), pico(golpe, 0.5)), i + 1)

# ======================================================================
#  TORNADOS: golpea el aire contra el suelo (onda de presion y polvo) y
#  donde van a nacer el polvo empieza a girar.
# ======================================================================
for i in range(2):
    sube = viento(0.6, [(0, 400), (1, 1500)], 1.0, 0.2) * rampa(0.6, 2.0)
    golpe = mezclar(pico(aletazo(2.0, 1.5), 0.8), en(0.2, pico(estallido(0.8, 2.0), 1.0)))
    guardar('tornados_golpe', reverb(mezclar(pico(sube, 0.4), en(0.4, golpe)), 0.25, 2.0), i + 1, limite=0.6)
for i in range(2):
    d = 1.6
    giro = curva(n_(d), [(0, 0.4), (1, 2.6)])
    nace = tornado(d, giro, 0.6, 0.85 + 0.1 * i, 1.4) * rampa(d, 1.4)
    guardar('tornado_nace', mezclar(pico(nace, 1.0), pico(granos(d, 300 * rampa(d, 1.0)), 0.3)) * ventana(d, 0.01, 0.3),
            i + 1)
# El rugido de un tornado (cada tornado lo repite mientras vaga).
for i in range(2):
    d = 3.0
    guardar('tornado', tornado(d, 2.4 + 0.3 * i, 1.0, 1.0 + 0.08 * i) * ventana(d, 0.35, 0.6), i + 1, alto=0.75)
# Te atrapa: el tiron hacia arriba y el silbido que te envuelve.
for i in range(2):
    tiro = pasada(0.9, 500, 2400 + 300 * i, 1.5, 0.5)
    envuelve = aullido(1.2, [(0, 800), (1, 1900)], 16) * campana_env(1.2, 1.0)
    guardar('tornado_atrapa', mezclar(pico(tiro, 1.0), en(0.2, pico(envuelve, 0.45)),
                                      pico(boom(90, 50, 0.08), 0.4)), i + 1)
for i in range(2):
    guardar('tornado_explota', reverb(mezclar(pico(estallido(1.0 + 0.1 * i, 2.2), 1.0),
                                              en(0.05, pico(pasada(0.8, 900, 4000, 1.6, 0.4), 0.5))), 0.25, 2.0),
            i + 1, limite=0.6)
# Roto a flechazos: pierde el giro, el silbido cae y se deshace en un soplo.
for i in range(2):
    d = 1.4
    giro = curva(n_(d), [(0, 2.6), (1, 0.3)])
    pierde = tornado(d, giro, 0.8, curva(n_(d), [(0, 1.0), (1, 0.55)]), 0.6) * caida(d, 0.45, 0.005)
    puf = mezclar(pico(boom(80, 40, 0.1), 0.6), pico(pb(ruido(0.8, 'rosa'), 1500) * caida(0.8, 0.22, 0.004), 0.7))
    guardar('tornado_rompe', reverb(mezclar(pico(pierde, 0.9), puf), 0.25, 1.6), i + 1)

# ======================================================================
#  LA CACERIA: chilla, las antenas se fijan (un silbido agudo que sube como
#  una flecha) y la marca cae sobre la presa.
# ======================================================================
for i in range(2):
    raspa = chirrido(0.7, (60, 120), ((3300, 10), (4700, 12), (6300, 14))) * rampa(0.7, 1.0, 0.3, 1.0)
    flecha = aullido(0.9, [(0, 1400 + 150 * i), (0.6, 4200 + 200 * i), (1, 4600)], 35) * ventana(0.9, 0.2, 0.25)
    cae = mezclar(pico(boom(150, 70, 0.12), 0.6), pico(pasada(0.6, 4500, 600, 2.0, 0.4), 0.7))
    voz_ = chillido(0.9, 560, 760, 80, alas=0.3, cola=1.6)
    guardar('marca', reverb(mezclar(pico(raspa, 0.35), pico(flecha, 0.4), en(0.55, cae), en(0.05, pico(voz_, 0.6))),
                            0.25, 2.2), i + 1, limite=0.6)
# Lanza una rafaga: el aire se comprime en una bola y sale.
for i in range(3):
    junta = viento(0.3, [(0, 600), (1, 2200)], 1.2, 0.1) * rampa(0.3, 2.0)
    sale = mezclar(pico(aletazo(1.1, 1.1), 0.8), pico(pasada(0.7, 1800 + 200 * i, 500, 1.4, 0.35), 0.8))
    gira = aullido(0.9, [(0, 1100 + 120 * i), (1, 900)], 18) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t_(0.9))) * caida(0.9, 0.3, 0.05)
    guardar('rafaga', reverb(mezclar(pico(junta, 0.4), en(0.22, sale), en(0.25, pico(gira, 0.3))), 0.2, 1.6), i + 1)
# Reventada en el aire: el estallido de la bola y el soplo que se dispersa.
for i in range(3):
    pop = mezclar(pico(boom(140 + 15 * i, 60, 0.06), 0.9), pico(bp(ruido(0.1), 300, 8000) * caida(0.1, 0.012, 0.001), 0.8))
    dispersa = pb(ruido(0.9, 'rosa'), 2500) * caida(0.9, 0.2, 0.004)
    chispa = aullido(0.5, [(0, 2600 + 200 * i), (1, 900)], 22) * caida(0.5, 0.12, 0.002)
    guardar('rafaga_rompe', reverb(mezclar(pop, pico(dispersa, 0.5), pico(chispa, 0.3)), 0.2, 1.4), i + 1)
for i in range(2):
    guardar('rafaga_golpe', mezclar(pico(estallido(0.6, 1.4), 1.0), pico(pasada(0.5, 3000, 500, 2.0, 0.3), 0.5)), i + 1,
            limite=0.6)

# ======================================================================
#  JUICIO DEL CICLON
# ======================================================================
# El silencio: el viento de toda la arena se apaga. Los silbidos caen,
# las rachas se van y queda solo un pitido en los oidos y la presion.
d = 5.0
n = n_(d)
t = t_(d)
apaga = np.interp(t, [0, 0.3, 1.8, 2.6, d], [0.0, 1.0, 0.25, 0.0, 0.0])
rachas = viento(d, [(0, 1400), (0.4, 600), (1, 200)], 0.9, 1.0) * apaga
silbidos = aullido(d, [(0, 1600), (0.35, 700), (0.6, 300), (1, 250)], 20) * apaga
pitido = np.sin(2 * np.pi * 6900 * t) * np.interp(t, [0, 1.6, 2.6, 4.2, d], [0, 0, 1, 1, 0]) ** 2
presion = np.sin(2 * np.pi * np.cumsum(np.full(n, 31.0)) / SR) * np.interp(t, [0, 1.6, 3.0, 4.6, d], [0, 0, 1, 1, 0])
guardar('juicio_silencio', mezclar(pico(rachas, 0.9), pico(silbidos, 0.45), pico(pitido, 0.035), pico(presion, 0.35)),
        alto=0.75)

# El circulo bajo todos: un golpe sordo que se hincha y un acorde de viento
# (tres tonos eolicos) que queda vibrando.
d = 3.6
t = t_(d)
hincha = filtro_mov(ruido(d, 'marron'), curva(n_(d), [(0, 80), (0.25, 600), (1, 150)]), 'low', 1.2) * np.interp(t, [0, 0.8, 1.2, d], [0, 1, 0.7, 0])
acorde = mezclar(*[pico(aullido(d, [(0, f * 0.97), (0.3, f), (1, f)], 60, 0.004), 1.0) * ventana(d, 0.6, 1.4)
                   for f in (330, 392, 494)])
guardar('juicio_circulo', reverb(mezclar(pico(hincha, 1.0), en(0.2, pico(acorde, 0.45)), pico(boom(48, 30, 0.6), 0.6)),
                                 0.35, 2.8, 5000), limite=0.6)

# El ciclon gigante que se forma alrededor del marcado (se repite mientras dura).
d = 6.0
giro = curva(n_(d), [(0, 0.5), (0.5, 2.5), (1, 3.2)])
ciclon = tornado(d, giro, 1.6, curva(n_(d), [(0, 0.6), (1, 1.15)]), 1.3)
ruge = pb(ruido(d, 'marron'), 90) * rampa(d, 0.7, 0.3, 1.0)
guardar('juicio_ciclon', mezclar(pico(ciclon, 1.0), pico(ruge, 0.5)) * ventana(d, 1.4, 0.8), alto=0.8)

# Un nucleo de viento: aire comprimido que gira y silba (se repite).
for i in range(2):
    d = 2.4
    tt = t_(d)
    gira = 0.55 + 0.45 * np.sin(2 * np.pi * (6.5 + i) * tt)
    canto = mezclar(pico(aullido(d, [(0, 980 + 60 * i), (1, 1010 + 60 * i)], 40, 0.01), 1.0),
                    pico(aullido(d, [(0, 1470 + 90 * i), (1, 1500 + 90 * i)], 50, 0.01), 0.6)) * gira
    zumba = np.sin(2 * np.pi * (82 + 5 * i) * tt) * (0.7 + 0.3 * gira)
    soplo = viento(d, [(0, 1200), (1, 1300)], 2.0, 0.3) * gira
    guardar('nucleo', mezclar(pico(canto, 0.6), pico(zumba, 0.35), pico(soplo, 0.4)) * ventana(d, 0.3, 0.3), i + 1, alto=0.7)
for i in range(3):
    golpe = mezclar(pico(boom(180 + 20 * i, 90, 0.05), 0.9), pico(bp(ruido(0.06), 900, 6000) * caida(0.06, 0.01), 0.6))
    escapa = aullido(0.5, [(0, 1300 + 200 * i), (1, 2600 + 200 * i)], 25) * caida(0.5, 0.12, 0.003)
    guardar('nucleo_golpe', mezclar(golpe, pico(escapa, 0.45), pico(pasada(0.35, 3000, 900, 2.0, 0.2), 0.4)), i + 1)
# Roto: el aire comprimido se escapa de golpe (un silbido que cae) y revienta.
for i in range(2):
    d = 1.8
    escape = aullido(d, [(0, 3400), (0.4, 1200), (1, 300)], 9) * caida(d, 0.45, 0.003)
    chorro = filtro_mov(ruido(d), curva(n_(d), [(0, 6000), (1, 800)]), 'band', 1.5) * caida(d, 0.35, 0.003)
    guardar('nucleo_roto', reverb(mezclar(pico(estallido(0.7 + 0.1 * i, 1.6), 0.9), pico(escape, 0.5), pico(chorro, 0.6)),
                                  0.3, 2.2), i + 1, limite=0.6)

# El golpe del juicio: lo lanza al cielo (un tiron que sube) y la palmada de
# sus alas revienta el aire a su alrededor, con un trueno encima.
d = 4.5
tiron = pasada(0.8, 400, 3500, 1.3, 0.6)
golpe = mezclar(pico(estallido(1.6, 3.2), 1.0), pico(trueno(4.0, 1.2), 0.75), en(0.05, pico(aletazo(2.4, 1.6), 0.6)))
guardar('juicio_golpe', reverb(mezclar(pico(tiron, 0.6), en(0.55, golpe)), 0.3, 3.0), limite=0.55)

# ======================================================================
#  TRUENO: los rayos que lleva dentro de las alas desde la fase III
# ======================================================================
for i in range(3):
    guardar('trueno', reverb(trueno(3.0 + 0.5 * i, 0.7 + 0.25 * i), 0.3, 3.0, 5000), i + 1, limite=0.6)

# ======================================================================
#  TAMBALEO: cambia de fase. Un rayo la sacude, se revuelve y chilla.
# ======================================================================
for i in range(2):
    sacude = mezclar(pico(trueno(2.6, 1.3), 0.9), en(0.1, pico(aletazo(1.6, 1.3), 0.6)), en(0.18, pico(crujir_quitina(0.8), 0.3)))
    guardar('tambaleo', mezclar(sacude, en(0.75, pico(chillido(2.0, 450 - 20 * i, 700 - 30 * i, 62), 1.0))), i + 1,
            limite=0.55)

# ======================================================================
#  ATURDIDA y AGOTADA: se estrella contra el suelo. Las alas golpean la
#  tierra, la coraza cruje y queda zumbando.
# ======================================================================
def estrellarse(peso=1.0):
    golpe = mezclar(pico(boom(52, 22, 0.35 * peso), 1.0), pico(pb(ruido(0.2), 1600) * caida(0.2, 0.03), 0.6))
    alas_ = mezclar(*[en(0.05 + 0.09 * k, pico(aletazo(1.0, 0.7), 0.5 - 0.08 * k)) for k in range(4)])
    polvo = granos(2.0, 1100 * np.exp(-t_(2.0) / 0.45))
    return mezclar(golpe, alas_, pico(polvo, 0.35), en(0.05, pico(crujir_quitina(0.9, 1.2), 0.3)))


d = 4.2
mareo = chirrido(d, (18, 40), ((2300, 7), (3400, 9))) * np.interp(t_(d), [0, 1, d], [0, 1, 0.2]) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t_(d)))
guardar('aturdida', reverb(mezclar(estrellarse(1.1), en(0.6, pico(mareo, 0.25)),
                                   en(0.3, pico(chillido(1.2, 360, 420, 52, 0.7, 0.4, 1.8), 0.45))), 0.25, 2.2), limite=0.55)
guardar('agotada', reverb(mezclar(estrellarse(1.3), en(0.5, pico(trueno(2.5, 0.6), 0.35))), 0.25, 2.2), limite=0.55)
# Jadeo: aire que entra y sale de una garganta enorme, y las alas que tiemblan.
for i in range(3):
    d = 1.6
    tt = t_(d)
    entra = filtro_mov(ruido(0.7, 'rosa'), curva(n_(0.7), [(0, 500), (1, 1200)]), 'band', 2.0) * campana_env(0.7, 1.4)
    sale = garganta(curva(n_(0.8), [(0, 120 + 8 * i), (1, 90)]), 0.8, VOCAL_O, 0.6, 0.6, 0.04, 1.2) * campana_env(0.8, 1.2)
    tiembla = bp(ruido(d), 300, 2000) * (0.5 + 0.5 * np.sin(2 * np.pi * 26 * tt)) ** 4 * campana_env(d, 2) * 0.5
    guardar('jadeo', reverb(mezclar(pico(entra, 0.6), en(0.75, pico(sale, 0.7)), pico(tiembla, 0.2)), 0.25, 1.8), i + 1)

# ======================================================================
#  LIBERACION: el ultimo chillido se apaga, baja planeando, el viento se
#  calma en brisa y el arpa del viento canta mientras el cielo se abre.
# ======================================================================
d = 9.5
t = t_(d)
ultimo = chillido(2.0, 520, 600, 70, 0.8, 0.6, 2.6)
planea = pasada(3.0, 1500, 300, 1.0, 0.3)
calma = viento(d, [(0, 900), (0.3, 500), (1, 380)], 0.8, 0.5) * np.interp(t, [0, 1, 3, d], [0.6, 0.8, 0.35, 0.2])
arpa = eolica(d - 2.0, 110.0, (2, 3, 4, 5, 6, 8, 10, 12), 0.6) * ventana(d - 2.0, 2.0, 2.5)
alto_ = eolica(d - 3.5, 220.0, (3, 4, 5, 6, 8), 0.9, 1.4) * ventana(d - 3.5, 1.5, 2.0)
guardar('liberacion', reverb(mezclar(pico(ultimo, 0.7), en(1.2, pico(planea, 0.4)), pico(calma, 0.3),
                                     en(2.0, pico(arpa, 0.4)), en(3.5, pico(alto_, 0.18))), 0.4, 3.2, 8000))

d = 3.2
t = t_(d)
rafaga_tibia = viento(d, [(0, 500), (0.3, 1800), (1, 2600)], 0.9, 0.3) * np.interp(t, [0, 0.5, 1.2, d], [0, 1, 0.6, 0])
brillo = eolica(d, 330.0, (2, 3, 4, 5, 6), 1.2, 1.5) * np.interp(t, [0, 0.6, 1.4, d], [0, 1, 0.7, 0])
polvo = granos(d, 120 * np.interp(t, [0, 0.5, d], [0, 1, 0]))
guardar('disolver', reverb(mezclar(pico(rafaga_tibia, 0.8), pico(brillo, 0.3), pico(polvo, 0.15)), 0.35, 2.4, 9000))

# ----------------------------------------------------------------------
#  sounds.json: los eventos aeralis.* con sus variantes y subtitulo
# ----------------------------------------------------------------------
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for k in [k for k in datos if k.startswith('aeralis.')]:
    del datos[k]
for ev, archivos in EVENTOS.items():
    datos['aeralis.' + ev] = {'subtitle': 'subtitles.atalaya.aeralis.' + ev,
                              'sounds': ['atalaya:aeralis/' + a for a in archivos]}
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
        fl = np.geomspace(30, 16000, al)
        idx = np.clip(np.searchsorted(f, fl), 0, len(f) - 1)
        img = (S[idx][::-1] * 255).astype(np.uint8)
        im = Image.fromarray(img).resize((an - 4, al), Image.BILINEAR)
        cx, cy = (k % col) * an, (k // col) * (al + 14)
        hoja.paste(Image.merge('RGB', (im.point(lambda v: int(v * 0.8)), im, im.point(lambda v: min(255, int(v * 1.3))))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9):.0f}dB', fill=(220, 220, 220))
    hoja.save(sys.argv[2])
