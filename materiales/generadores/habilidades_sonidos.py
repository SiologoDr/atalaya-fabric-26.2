"""
Los sonidos de las habilidades de las armaduras elementales y de sus armas
(octubre de 2026). Sintetizados desde cero, como todos los del mod: nada de
vanilla ni de bancos de sonido.

Cada armadura tiene un papel, una habilidad activa (tecla R: 30 s de efecto
y 120 s de espera) y su arma:

  agua    sanadora (Nerea)    MANANTIAL: un manantial que cura a pulsos a los
                              aliados. Arma: el Tridente de las Mareas, que
                              se lanza y vuelve a la mano.
  tierra  tanque (Rajang)     MURALLA DE JADE: atrae al jefe hacia el tanque y
                              escuda a los aliados. Arma: el Martillo de Jade,
                              pesado y lento; el golpe cargado aturde.
  viento  apoyo (Aeralis)     CORRIENTE ASCENDENTE: una corriente que da
                              velocidad y corazones dorados a los aliados y
                              una rafaga que aparta a los mobs. Arma: el Arco
                              del Vendaval, de flechas rapidas.
  fuego   dano (Novilis)      FURIA SOLAR: una furia de sol y fuego. Arma: el
                              Mandoble Solar.

La fisica de cada elemento es la de su jefe (copiada de sus generadores: no
se pueden importar porque al cargarse borran y escriben su carpeta):

  - AGUA (Nerea): cada burbuja es la resonancia de Minnaert de una bolsa de
    aire (f = 3,26 / radio) que se apaga y sube un poco de tono; una nube de
    ellas es un borboton o una estela. Las gotas, su 'plink'. El remolino, un
    peine que se mueve.
  - TIERRA Y JADE (Rajang): el golpe de presion que cae de tono, la roca que
    se raja (microfracturas que hacen sonar las bandas de la piedra), la
    grava, la piedra que se arrastra (pegarse y soltarse) y el JADE, piedra
    densa que suena casi como vidrio (modos de barra libre partidos en dos:
    el batido le da el brillo).
  - AIRE (Aeralis): turbulencia por una banda que se mueve con la racha,
    silbidos eolicos (bandas estrechisimas), plumas que aletean y
    campanillas de viento (tubos: modos de barra libre).
  - FUEGO Y SOL (Novilis): la llama que prende ('fwump'), el fuego que ruge,
    las brasas que revientan, el oro que suena como una campana, los
    destellos de luz y los tonos que suben, como un metal.

Los golpes de las armas siguen la receta de los golpes de espada de
armaduras_sonidos.py (el corte del aire, el golpe seco, la sala corta, el
pico a -3 dBFS y nada por encima de 9 kHz), para que suenen a lo mismo.

Los toques que se repiten o que avisan (el pulso del Manantial, 'lista',
las curas) son tonales, suaves, sin ruido y con el ataque redondo, y tienen
un techo de sonoridad: con poco pico llevan mucha energia y no deben sonar
mas que los golpes.

Cada sonido lleva su propia semilla (sale de su nombre): se puede cambiar uno
sin que cambien los demas.

Escribe (mono, Vorbis, 44,1 kHz):
  sounds/armadura/  muralla, manantial, manantial_pulso, corriente, furia,
                    lista, martillo_carga, martillo_carga2, tridente_lanzar,
                    tridente_vuelve, tridente_cura, arco_disparo1..2,
                    flecha_aliado
  sounds/espada/    solar_golpe1..3, jade_martillo1..3, mareas_tridente1..3
Los golpes de espada de antes (<tema>_golpe1..3) los hace
armaduras_sonidos.py; este no los toca. Los eventos de sounds.json y los
subtitulos se ponen a mano.

Uso: python habilidades_sonidos.py <raiz del proyecto> [carpeta de revision]
  En la carpeta de revision deja un .wav de cada sonido y revision.png: la
  onda y el espectrograma de todos, para revisarlos sin escuchar.
"""
import os
import sys
import zlib
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator

SR = 44100
RAIZ = sys.argv[1]
SONIDOS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds')
REVISION = sys.argv[2] if len(sys.argv) > 2 else None
ALTO = 10 ** (-3.0 / 20)          # pico de cada .ogg: -3 dBFS, como los golpes de espada
GUARDADOS = []
rng = np.random.default_rng(20261006)


def sembrar(nombre):
    """Cada sonido con su semilla, sacada de su nombre: cambiar uno no cambia los demas."""
    global rng
    rng = np.random.default_rng(zlib.crc32(nombre.encode('utf-8')) ^ 20261006)


# ======================================================================
#  Utilidades (las mismas que los sonidos de los jefes)
# ======================================================================
def n_(dur):
    return max(1, int(round(dur * SR)))


def t_(dur):
    return np.arange(n_(dur)) / SR


def hz(m):
    """Nota MIDI a hercios (la 4 = 69 = 440 Hz)."""
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


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
    """Ruido lento (por debajo de fc), de desviacion 1: temblores, rachas."""
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
    """Valor que pasa suave por (tiempo relativo 0..1, valor), sin pasarse."""
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
    """La capa x, empezando a los `seg` segundos."""
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


def cortar(x, dur, soltar=None):
    """Deja x en `dur` segundos y apaga el final con una rampa de coseno
    (`soltar` segundos; si no, un cuarto de la duracion y 0,3 s como mucho):
    nada acaba en seco."""
    n = n_(dur)
    x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n].copy()
    s = min(n, n_(soltar if soltar else min(0.3, dur * 0.25)))
    x[n - s:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, s))
    return x


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


def paso(x):
    """Rampa suave 0..1 (smoothstep)."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def saturar(x, k=2.0):
    return np.tanh(k * x) / np.tanh(k)


def modos(f, dur, parciales, tau):
    """Suma de modos que se apagan (los agudos antes)."""
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        if f * r < SR * 0.45:
            s += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6)) * np.exp(-t / (tau / r ** 0.5))
    a = n_(0.0008)
    s[:a] *= np.linspace(0, 1, a)
    return s


def flanger(x, lfo_hz, base_ms=1.5, prof_ms=5.0, mezcla=0.7):
    """Peine que se mueve: el agua (o el aire) girando en un remolino."""
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
    """Al aire libre, alrededor del jugador: el suelo devuelve un eco muy
    cercano, dos mas flojos llegan de lo que haya cerca y la cola, difusa y
    corta, pierde antes los agudos (la misma receta que las de los jefes, sin
    sus muros)."""
    clave = (round(cola, 2), int(oscuro))
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro) + 7)
        x = r.standard_normal(len(t))
        h = (pb(x, 600) * np.exp(-6.9 * t / cola)
             + bp(x, 600, 3500) * np.exp(-6.9 * t / (cola * 0.6)) * 0.75
             + pa(x, 3500) * np.exp(-6.9 * t / (cola * 0.25)) * 0.35)
        h = pb(h, oscuro)
        a = n_(0.02)
        h[:a] *= np.linspace(0, 1, a) ** 2
        ref = np.sqrt(np.mean(h[:n_(0.1)] ** 2))
        for seg, g, claro in ((0.009, 0.7, 7000), (0.037, 0.4, 5000), (0.071, 0.25, 4000)):
            i = n_(seg)
            eco = pb(r.standard_normal(n_(0.01)), claro) * np.exp(-t_(0.01) / 0.0025)
            h[i:i + len(eco)] += g * eco * ref * 6
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


def reverb(x, mezcla=0.22, cola=1.4, oscuro=6500):
    h = respuesta(cola, oscuro)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


# ======================================================================
#  LOS GOLPES DE ESPADA (la receta de armaduras_sonidos.py)
# ======================================================================
def barrido(dur, f0, f1, q=2.5, env=None):
    """Ruido por un paso banda que se mueve de f0 a f1: el corte del aire."""
    n = n_(dur)
    f = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    out = pico(filtro_mov(rng.standard_normal(n), np.minimum(f, SR * 0.22), 'band', q, 16))
    if env is not None:
        out = out * env[:n]
    m = max(1, n // 4)
    out[-m:] *= np.linspace(1, 0, m) ** 2      # que se apague del todo al final (sin corte)
    return out


def shing(f0, dur=0.22, tau=0.07, brillo=1.0):
    """El 'shing' del filo: un racimo de parciales agudos, desafinados, que se
    apaga deprisa, con un poco de ruido metalico dentro. Corto y aspero."""
    x = t_(dur)
    out = np.zeros_like(x)
    for r, a in ((1.0, 1.0), (1.27, 0.8), (1.62, 0.65), (2.03, 0.5), (2.51, 0.35), (3.1, 0.22)):
        f = f0 * r * brillo
        if f > SR * 0.45:
            continue
        for desafina in (-0.004, 0.004):
            out += a * np.sin(2 * np.pi * f * (1 + desafina) * x + rng.random() * 6.28) * np.exp(-x / (tau / (0.6 + 0.4 * r)))
    raspa = bp(ruido(dur), f0 * 0.9, min(SR * 0.45, f0 * 3.2)) * np.exp(-x / (tau * 0.5))
    return pico(out) * 0.75 + pico(raspa) * 0.35 * np.clip(x / 0.0015, 0, 1)


def golpe_seco(f=110.0, dur=0.12, tau=0.03):
    """El golpe en el cuerpo: un grave muy corto y un chasquido sordo."""
    x = t_(dur)
    tono = np.sin(2 * np.pi * f * x * (1 - 0.35 * x / dur)) * np.exp(-x / tau)
    sordo = pb(ruido(dur), 900) * np.exp(-x / (tau * 0.5))
    return pico(tono) * 0.8 + pico(sordo) * 0.5


def chapoteo(dur=0.35, brillo=2600):
    """Un chapoteo: ruido por un paso bajo que se cierra, con su cola."""
    x = t_(dur)
    env = np.clip(x / 0.004, 0, 1) * np.exp(-x / 0.08)
    return pico(pb(ruido(dur), brillo, 2)) * env


def sala(x, mezcla=0.18):
    """Una sala corta: que no suene seco."""
    cola = np.zeros(n_(0.35))
    for retardo, g in ((0.017, 0.5), (0.029, 0.4), (0.041, 0.3), (0.063, 0.22), (0.089, 0.15), (0.13, 0.09)):
        cola[int(retardo * SR)] = g
    cola = pb(cola, 5000, 1)
    mojado = signal.fftconvolve(x, cola)[:len(x)]
    return x + mezcla * mojado


def montar(dur, *capas):
    """capas: (onda, ganancia, desde segundos). La sala corta, nada por encima
    de 9 kHz, sin clic al final y el pico a -3 dBFS."""
    out = np.zeros(n_(dur))
    for onda, g, desde in capas:
        i = n_(desde)
        trozo = onda[:max(0, len(out) - i)]
        out[i:i + len(trozo)] += g * trozo
    out = sala(out)
    out = pb(out, 9000, 2)
    out[-n_(0.02):] *= np.linspace(1, 0, n_(0.02))
    return pico(out, ALTO)


# ======================================================================
#  TIERRA Y JADE (la misma fisica que Rajang)
# ======================================================================
def boom(f0=60, f1=26, tau=0.25, dur=None):
    """El golpe de presion: algo empujado de golpe, que cae de tono."""
    dur = dur or tau * 5
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) + 0.25 * np.sin(2 * fase)) * caida(dur, tau, 0.003)


def retumbo(dur, fc=120, lento=1.2, prof=0.45, grano=0.35):
    """Retumbo: ruido marron muy filtrado cuya amplitud late lenta."""
    n = n_(dur)
    am = np.exp(prof * suave(n, lento))
    bajo = pa(pb(ruido(dur, 'marron'), fc, 4), 28) * am
    medio = bp(ruido(dur, 'rosa'), fc * 1.3, fc * 6) * am * np.exp(0.5 * prof * suave(n, lento * 3))
    return mezclar(pico(bajo, 1.0), pico(medio, grano))


TAMANOS = np.geomspace(0.4, 30.0, 16)    # cm, de arenilla a cascote
_PIEDRAS = []


def _piedras():
    """Banco de piedras: un chasquido de contacto y unos modos irregulares
    que se apagan enseguida. f ~ 1/tamano."""
    if not _PIEDRAS:
        for s in TAMANOS:
            clase = []
            for _ in range(6):
                f = min(12000.0, 5200.0 / s * rng.uniform(0.8, 1.25))
                tau = 0.0018 + 0.0014 * s
                d = min(0.3, 6 * tau + 0.004)
                parc = ((1, 1.0), (rng.uniform(1.45, 1.85), 0.6), (rng.uniform(2.2, 2.9), 0.4), (rng.uniform(3.3, 4.3), 0.22))
                anillo = modos(f, d, parc, tau)
                dc = 0.0008 + 0.00012 * s
                choque = pb(ruido(dc), min(15000, f * 3.5)) * caida(dc, dc * 0.25, 0.0001)
                p = mezclar(pico(anillo, 1.0), pico(choque, 0.7))
                clase.append(p / np.max(np.abs(p)))
            _PIEDRAS.append(clase)
    return _PIEDRAS


def grava(dur, tasa, tam=(0.4, 4.0), beta=2.2, amp=1.0):
    """Lluvia de piedras (tasa por segundo, numero o curva): muchas pequenas y
    pocas grandes."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    ps = _piedras()
    clases = np.nonzero((TAMANOS >= tam[0] * 0.999) & (TAMANOS <= tam[1] * 1.001))[0]
    if len(clases) == 0:
        clases = np.array([int(np.argmin(np.abs(TAMANOS - tam[0])))])
    w = TAMANOS[clases] ** (1 - beta)
    w /= w.sum()
    elegidas = rng.choice(clases, size=len(cuando), p=w)
    out = np.zeros(n + n_(0.35))
    tope = TAMANOS[clases[-1]]
    for i, k in zip(cuando, elegidas):
        g = ps[k][rng.integers(6)] * rng.uniform(0.2, 1.0) * (TAMANOS[k] / tope) ** 0.5
        out[i:i + len(g)] += g
    return amp * out[:n]


def escombros(dur, fuerza=1.0, vuelo=0.35, tam=(0.4, 8.0), salpica=0.6):
    """Lo que salta al golpe y vuelve a caer: la lluvia es maxima a los
    `vuelo` segundos (cuando aterriza) y se apaga."""
    t = t_(dur)
    x = t / vuelo
    tasa = 700 * fuerza * (salpica * np.exp(-t / 0.04) + x ** 1.5 * np.exp(1.5 * (1 - x)))
    return grava(dur, tasa, tam)


ROCA = ((92, 5.0, 1.0), (163, 6.0, 0.9), (281, 7.0, 0.75), (455, 8.0, 0.55), (742, 8.0, 0.4), (1210, 9.0, 0.28),
        (1960, 10.0, 0.18))


def moler(dur, peso=1.0, tasa=(16, 45), arena=1.0, velocidad=1.0):
    """Piedra que se arrastra sobre piedra (o sobre la tierra): friccion de
    pegarse y soltarse por los modos anchos de los bloques, con la arena que
    raspa."""
    n = n_(dur)
    vel = np.broadcast_to(np.asarray(velocidad, dtype=float), (n,))
    lo, hi = tasa
    ritmo = (lo + (hi - lo) * (0.5 + 0.5 * np.tanh(1.3 * suave(n, 3)))) * vel
    fase = np.cumsum(ritmo) / SR
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    exc = np.zeros(n)
    exc[golpes] = rng.uniform(0.25, 1.0, len(golpes))
    nucleo = pb(ruido(0.005), 3000) * caida(0.005, 0.0012, 0.0002)
    exc = signal.fftconvolve(exc, nucleo)[:n]
    exc += 0.05 * pb(ruido(dur, 'rosa'), 2500) * np.clip(vel, 0, None) * (0.6 + 0.4 * np.abs(suave(n, 8)))
    gemido = sum(g * resonar(exc, min(f / peso, 9000.0), q) for f, q, g in ROCA)
    capas = [pico(gemido, 1.0)]
    if arena:
        capas.append(pico(grava(dur, 900 * arena * np.clip(vel, 0, None), (0.4, 1.2)), 0.3 * arena))
    return mezclar(*capas)


def rajar_roca(cuantos=6, dur=0.05, brillo=1.0, grave=1.0):
    """Una roca (o el jade) que se parte: una racha de microfracturas que
    hacen sonar las bandas agudas de la piedra y el golpe grave de su masa."""
    n = n_(dur + 0.2)
    exc = np.zeros(n)
    for s in np.sort(rng.uniform(0, 1, cuantos) ** 1.6 * dur):
        c = pa(ruido(0.0016), 500) * caida(0.0016, 0.0004, 0.0001) * rng.uniform(0.3, 1.0)
        i = n_(s)
        exc[i:i + len(c)] += c[:n - i]
    anillo = sum(resonar(exc, rng.uniform(lo, hi) * brillo, rng.uniform(25, 50))
                 for lo, hi in ((1300, 2100), (2500, 3500), (4000, 5400), (6200, 8200)))
    cuerpo = sum(g * resonar(exc, f * grave, 7) for f, g in ((170, 1.0), (320, 0.8), (600, 0.6)))
    return mezclar(pico(exc, 1.0), pico(anillo, 0.55), pico(cuerpo, 0.6))


def golpe_tierra(peso=1.0, grieta=1.0, restos=1.0, dur=2.0):
    """Algo muy pesado contra el suelo: el golpe de presion, el cuerpo sordo,
    la tierra que se aplasta, la piedra que se raja, el suelo que retumba y lo
    que salta y vuelve a caer."""
    t = t_(dur)
    sub = saturar(boom(78, 30, 0.22 * peso, dur), 2.5)
    cuerpo = bp(ruido(0.5, 'rosa'), 90, 700) * caida(0.5, 0.05 * peso, 0.002)
    aplasta = bp(ruido(0.3, 'rosa'), 300, 2800) * caida(0.3, 0.035, 0.001)
    choque = bp(ruido(0.08), 150, 7000) * caida(0.08, 0.008, 0.0005)
    raja = rajar_roca(int(5 + 9 * grieta), 0.03 + 0.07 * grieta, 1.0, 0.8)
    temblor = retumbo(dur, 110, 2.5, 0.35, 0.6) * caida(dur, 0.3 * peso, 0.01)
    caen = escombros(dur, restos, 0.3 + 0.12 * peso, (0.4, 4 + 6 * restos))
    polvo = pb(ruido(dur, 'rosa'), 800) * np.interp(t, [0, 0.04, 0.5, dur], [0, 1, 0.35, 0])
    return mezclar(pico(sub, 0.5), pico(cuerpo, 0.6), pico(aplasta, 0.9), pico(choque, 0.7), pico(raja, 0.75 * grieta),
                   pico(temblor, 0.25), pico(caen, 0.7 * restos), pico(polvo, 0.25))


JADE = ((1, 1.0), (2.756, 0.5), (5.404, 0.28), (8.933, 0.15))          # barra libre (piedras sonoras)
JADE_TALLA = ((1, 1.0), (1.53, 0.55), (2.41, 0.42), (3.28, 0.3), (4.63, 0.18), (6.1, 0.1))   # pieza tallada


def jade(f, dur=None, tau=0.3, parciales=JADE, dureza=1.0, batido=0.0014):
    """Jade golpeado: piedra densa que suena casi como vidrio. Modos
    inarmonicos, cada uno partido en dos (la talla no es simetrica: el batido
    le da el brillo), y el toque seco del contacto."""
    dur = dur or min(4.0, tau * 6 + 0.02)
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        fr = f * r
        if fr >= SR * 0.45:
            continue
        tr = tau / r ** 0.6
        for d in (-batido, batido):
            s += a * np.sin(2 * np.pi * fr * (1 + d) * t + rng.uniform(0, 6)) * np.exp(-t / tr)
    k = n_(0.0006)
    s[:k] *= np.linspace(0, 1, k)
    toque = pb(ruido(0.003), 2500 + 7000 * dureza) * caida(0.003, 0.0006, 0.0001)
    return mezclar(pico(s, 1.0), pico(toque, 0.35 * dureza))


def esquirlas(cuantas, dur, fmin=1800, fmax=6500, amp=1.0, parciales=JADE_TALLA, tau=(0.03, 0.12)):
    """Lascas de jade que saltan y tintinean al caer (casi todas al principio)."""
    capas = []
    for _ in range(cuantas):
        s = rng.uniform(0, dur) ** 1.5 / max(dur, 1e-3) ** 0.5
        capas.append(en(s, jade(rng.uniform(fmin, fmax), None, rng.uniform(*tau), parciales, 1.0, 0.002)
                        * rng.uniform(0.2, 1.0)))
    return amp * mezclar(*capas)


def canto_jade(dur, f, parciales=((1, 1.0), (2.756, 0.4), (5.404, 0.15)), q=300, lento=0.6):
    """Jade que canta frotado (como una copa): ruido por resonancias
    estrechisimas, cada una partida en dos (late), que respiran lento."""
    n = n_(dur)
    s = np.zeros(n)
    for r, a in parciales:
        fr = f * r
        if fr > SR * 0.45:
            continue
        for d in (-0.0012, 0.0012):
            s += a * pico(resonar(ruido(dur), fr * (1 + d), q))
    return s * np.exp(0.3 * suave(n, lento))


# ======================================================================
#  AGUA (la misma fisica que Nerea)
# ======================================================================
def burbuja(r_mm, xi=0.1, amp=1.0, amortigua=1.0, ataque=0.0004):
    """Una burbuja de radio r_mm: resonancia de Minnaert que se apaga y sube."""
    f0 = min(3260.0 / r_mm, SR * 0.42)
    d = (0.043 * f0 + 0.0014 * f0 ** 1.5) * amortigua
    dur = min(1.6, 6.5 / d)
    t = t_(dur)
    f = f0 * (1 + xi * d * t)
    fase = 2 * np.pi * np.cumsum(np.minimum(f, SR * 0.45)) / SR
    e = np.exp(-d * t)
    a = min(len(t), n_(ataque))
    e[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
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
    out = np.trim_zeros(out, 'b')
    return out if len(out) else np.zeros(n)


def gota(r=None, amp=1.0, toque=0.25, ataque=0.0004):
    """Una gota que cae al agua: un toque y el 'plink' que sube."""
    r = r if r is not None else rng.uniform(1.8, 4.2)
    golpe = bp(ruido(0.004), 2500, 9000) * caida(0.004, 0.0008, 0.0002) * toque
    return amp * mezclar(golpe, en(0.001, burbuja(r, rng.uniform(0.22, 0.42), 1.0, 0.8, ataque)))


def goteo(dur, cuantas, desde=0.0, amp=1.0):
    """Gotas que caen dispersas, cada vez menos y mas flojas."""
    capas = []
    for _ in range(cuantas):
        s = desde + rng.uniform(0, dur) ** 1.3 * dur ** (-0.3)
        a = amp * rng.uniform(0.3, 1.0) * (1 - 0.6 * (s - desde) / max(dur, 1e-3))
        capas.append(en(max(0.0, s), gota(amp=a)))
    return mezclar(*capas) if capas else np.zeros(1)


# ======================================================================
#  AIRE (la misma fisica que Aeralis)
# ======================================================================
def viento(dur, puntos, q=1.0, racheo=0.6, color='rosa'):
    """Viento: turbulencia por una banda que sube y baja con las rachas."""
    n = n_(dur)
    f = curva(n, puntos) * np.exp(0.18 * racheo * suave(n, 0.9))
    x = filtro_mov(ruido(dur, color), f, 'band', q)
    return x * np.exp(0.55 * racheo * suave(n, 0.6))


def aullido(dur, puntos, q=18.0, temblor=0.025, bloque=32, mult=1.0):
    """El viento que canta en una arista: una banda estrechisima que tiembla."""
    n = n_(dur)
    f = curva(n, puntos) * mult * (1 + temblor * suave(n, 3))
    return filtro_mov(ruido(dur), f, 'band', q, bloque) * (0.55 + 0.45 * np.abs(suave(n, 1.6)))


def pasada(dur, f0, f1, q=1.8, silba=0.25):
    """Algo que pasa cortando el aire: la banda se mueve (Doppler) y silba."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.45, (f0 * f1) ** 0.5 * 1.15), (1, f1)])
    soplo = filtro_mov(ruido(dur, 'rosa'), f, 'band', q)
    canta = filtro_mov(ruido(dur), f * 1.6, 'band', 22, 32)
    e = campana_env(dur, 1.3) ** 1.4
    return mezclar(pico(soplo * e, 1.0), pico(canta * e, silba))


def plumas(dur, aleteo=24.0, lo=700, hi=5500):
    """Plumas que aletean: cada batida las hace golpear el aire muchas veces
    por segundo (un 'frrr'): ruido por una banda media-aguda que se abre y se
    cierra a ese ritmo, que tiembla un poco, dentro de una batida que se
    hincha y se apaga."""
    n = n_(dur)
    f = aleteo * (1 + 0.1 * suave(n, 4))
    fase = 2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6)
    golpes = (0.5 + 0.5 * np.sin(fase)) ** 5
    x = bp(ruido(dur), lo, hi) * (0.15 + golpes)
    return x * campana_env(dur, 1.2)


def batida(tam=0.5, fuerza=1.0):
    """Un ala que bate (o una rafaga que empuja): el soplo que se abre y se
    cierra y el golpe de presion grave."""
    d = 0.3 + 0.5 * tam
    n = n_(d)
    t = t_(d)
    sube = 0.1 * tam + 0.02
    env = np.where(t < sube, (t / sube) ** 1.6, np.exp(-(t - sube) / (0.15 * tam + 0.02)))
    env *= ventana(d, 0.001, d * 0.25)
    aire = filtro_mov(ruido(d, 'rosa'), 180 + 2600 * env ** 1.3 * fuerza, 'low', 0.9) * env
    tw = t_(0.35)
    whump = np.sin(2 * np.pi * np.cumsum(30 + 50 * np.exp(-tw / 0.05)) / SR) * caida(0.35, 0.06 * tam + 0.02, 0.01)
    return mezclar(pico(aire, 1.0), en(sube * 0.7, pico(whump, 0.6 * fuerza)))


BARRA = ((1, 1.0), (2.756, 0.38), (5.404, 0.14))    # un tubo de campanilla: barra libre


def tubo(f, tau=0.7, dureza=0.3):
    """Un tubo de una campanilla de viento: modos de barra libre, cada uno
    partido en dos (late despacio), con un toque blando del badajo."""
    dur = min(3.0, tau * 5)
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in BARRA:
        fr = f * r * rng.uniform(0.997, 1.003)
        if fr >= SR * 0.45:
            continue
        fi = rng.uniform(0, 6)
        for d in (-0.0009, 0.0009):
            s += a * np.sin(2 * np.pi * fr * (1 + d) * t + fi) * np.exp(-t / (tau / r ** 0.8))
    k = n_(0.0015)
    s[:k] *= np.linspace(0, 1, k)
    toque = pb(ruido(0.003), 4000) * caida(0.003, 0.0007, 0.0002)
    return mezclar(pico(s, 1.0), pico(toque, 0.12 * dureza))


def campanillas(dur, tasa, notas, tau=(0.45, 0.9), amp=1.0):
    """Una campanilla de viento: el aire mueve el badajo y suenan los tubos
    al azar (tasa: numero o curva por segundo), nunca dos veces seguidas el
    mismo."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(4.0))
    ultima = -1
    for i in cuando:
        k = rng.integers(len(notas))
        if k == ultima:
            k = (k + 1) % len(notas)
        ultima = k
        g = tubo(notas[k], rng.uniform(*tau)) * rng.uniform(0.35, 1.0)
        out[i:i + len(g)] += g
    out = np.trim_zeros(out, 'b')
    return amp * out if len(out) else np.zeros(n)


# ======================================================================
#  FUEGO Y SOL (la misma fisica que Novilis)
# ======================================================================
_CHASQ = []


def _chasquidos_banco():
    """Banco de brasas que revientan: un impulso de 0,2-2,5 ms de banda
    ancha que hace sonar un instante una resonancia (la astilla, la escoria)."""
    if not _CHASQ:
        for _ in range(64):
            L = rng.uniform(0.0002, 0.0025)
            d = L + 0.012
            c = pa(ruido(d), 600) * caida(d, L * 0.5 + 0.0002, 0.00005)
            f = np.exp(rng.uniform(np.log(900), np.log(7500)))
            c = c + rng.uniform(0.2, 0.9) * pico(resonar(c, f, rng.uniform(3, 14)), np.max(np.abs(c)))
            _CHASQ.append(c / np.max(np.abs(c)))
    return _CHASQ


def chasquidos(dur, tasa):
    """Las brasas que saltan (tasa por segundo, numero o curva): muchos
    flojos y unos pocos fuertes (cola larga, de Pareto)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    banco = _chasquidos_banco()
    out = np.zeros(n + n_(0.02))
    amps = np.clip(rng.pareto(2.2, len(cuando)) * 0.3 + 0.08, 0, 1.0) * rng.choice([-1.0, 1.0], len(cuando))
    for i, a in zip(cuando, amps):
        c = banco[rng.integers(len(banco))]
        out[i:i + len(c)] += a * c
    return out[:n]


def llama(dur, fuerza=1.0, brillo=1.0, parpadeo=8.0, chasq=1.0, grave=1.0):
    """Fuego que ruge: la combustion turbulenta (ruido grave que late con los
    remolinos), el 'whoomph' hondo, las lenguas que lamen y las brasas.
    `brillo` (numero o curva) abre todo hacia los agudos: mas caliente."""
    n = n_(dur)
    brillo = np.broadcast_to(np.asarray(brillo, dtype=float), (n,))
    flick = np.exp(0.45 * suave(n, parpadeo)) * np.exp(0.3 * suave(n, 1.8))
    ruge = filtro_mov(ruido(dur, 'rosa'), 420 * brillo, 'low', 0.75) * flick
    hondo = pa(pb(ruido(dur, 'marron'), 110 * grave, 2), 24) * np.exp(0.5 * suave(n, 3.0))
    lenguas = filtro_mov(ruido(dur), 1400 * brillo, 'band', 0.8) * np.exp(1.1 * suave(n, 5.0))
    ch = chasquidos(dur, 22 * chasq * fuerza)
    return mezclar(pico(ruge, 1.0), pico(hondo, 0.55 * grave), pico(lenguas, 0.22), pico(ch, 0.3 * chasq))


def ignicion(dur=1.3, fuerza=1.0, f_max=3500.0, grave=55.0, aspira=0.0):
    """Fuego que prende de golpe ('fwump'): el aire que se traga la llama
    (si `aspira`), la bocanada que se abre en agudos y se cierra, el golpe
    de presion y las chispas que saltan."""
    n = n_(dur)
    t = t_(dur)
    fc = curva(n, [(0, 250), (0.05, f_max), (0.3, 1100), (1, 320)])
    env = np.interp(t, [0, 0.025, 0.12, dur], [0, 1, 0.65, 0]) ** 1.2
    sopla = filtro_mov(ruido(dur, 'rosa'), fc, 'low', 0.9) * env
    golpe = saturar(boom(grave * 1.7, grave * 0.6, 0.12), 2.0)
    chispas = chasquidos(dur, 900 * np.exp(-t / 0.15) + 15)
    x = mezclar(pico(sopla, 1.0), pico(golpe, 0.55), pico(chispas, 0.3))
    if aspira:
        na = n_(aspira)
        traga = filtro_mov(ruido(aspira, 'rosa'), curva(na, [(0, 300), (1, 1800)]), 'low', 0.8) * rampa(aspira, 2.2)
        x = mezclar(pico(traga, 0.4), en(aspira, x))
    return fuerza * x


PLACA = ((1.0, 1.0), (1.47, 0.75), (2.09, 0.6), (2.56, 0.5), (2.94, 0.42), (3.42, 0.35), (4.11, 0.25))
CAMPANA_ORO = ((0.5, 0.55), (1, 1.0), (1.19, 0.5), (1.5, 0.35), (2.0, 0.6), (2.5, 0.25), (3.0, 0.2), (4.2, 0.12))
DESTELLO = ((1, 1.0), (2.756, 0.55), (5.404, 0.32))


def metal(f, dur=None, tau=0.3, parciales=PLACA, dureza=1.0, batido=0.0025, agudos=0.7):
    """Metal golpeado (el acero de la hoja, el oro): modos inarmonicos, cada
    uno partido en dos (el batido le da vida), los agudos que se apagan antes
    y el toque seco del contacto."""
    dur = dur or min(5.0, tau * 6 + 0.02)
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        fr = f * r * rng.uniform(0.99, 1.01)
        if fr >= SR * 0.45:
            continue
        tr = tau / r ** agudos
        for d in (-batido, batido):
            s += a * np.sin(2 * np.pi * fr * (1 + d) * t + rng.uniform(0, 6)) * np.exp(-t / tr)
    k = n_(0.0005)
    s[:k] *= np.linspace(0, 1, k)
    toque = pb(ruido(0.004), 3000 + 9000 * dureza) * caida(0.004, 0.0007, 0.0001)
    return mezclar(pico(s, 1.0), pico(toque, 0.45 * dureza))


def campana_oro(f, tau=1.0, dureza=0.5):
    """Una campana de oro: el hum una octava abajo, la tercera menor, la
    quinta y la octava; batiendo despacio."""
    return metal(f, None, tau, CAMPANA_ORO, dureza, 0.0012, 0.5)


def destellos(dur, tasa, fmin=2500, fmax=8000, tau=(0.05, 0.25)):
    """Brillo de sol: campanitas agudas y sueltas (tasa: numero o curva)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(1.8))
    for i in cuando:
        g = metal(rng.uniform(fmin, fmax), None, rng.uniform(*tau), DESTELLO, 0.2, 0.002) * rng.uniform(0.2, 1.0)
        out[i:i + len(g)] += g[:len(out) - i]
    return out[:n] if np.any(out) else np.zeros(n)


def metal_tono(f, amp, voces=3, det=6.0, fc0=300.0, fc1=3200.0):
    """Un tono de metal (el heroico de la Furia, el desafiante de la
    Muralla): diente de sierra limitado en banda (armonicos 1/k), unas voces
    casi al unisono y un paso bajo que se abre con la intensidad, como un
    metal de verdad (suave es oscuro; fuerte, brillante). f y amp son curvas."""
    n = len(f)
    fmax = float(np.max(f))
    out = np.zeros(n)
    for v in range(voces):
        c = (v - (voces - 1) / 2) * det + rng.normal(0, 1.0)
        fase = 2 * np.pi * np.cumsum(f * 2 ** (c / 1200)) / SR + rng.uniform(0, 6)
        for k in range(1, int(9000 / fmax) + 1):
            out += np.sin(k * fase + rng.uniform(0, 6)) / k
    out = filtro_mov(out, fc0 + (fc1 - fc0) * np.clip(amp, 0, 1) ** 1.5, 'low', 0.9, 32)
    return out * amp


# ======================================================================
#  CRISTAL: los toques de cura y de aviso
# ======================================================================
def cristal(f, tau=0.3, ataque=0.006, parciales=((1, 1.0), (2.0, 0.1), (3.01, 0.035)), det=0.0007, dur=None,
            temblor=0.0):
    """Una nota de cristal: casi un seno puro con un poco de segundo y tercer
    armonico, partida en dos voces que laten muy despacio (la segunda mas
    floja: el latido nunca apaga la nota del todo), con el ataque redondo (sin
    chasquido) y una caida limpia. `temblor`: un vaiven lento de la amplitud
    (el brillo del agua)."""
    dur = dur or min(3.0, tau * 6)
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        fr = f * r
        if fr > SR * 0.45:
            continue
        fi = rng.uniform(0, 6)                 # las dos voces empiezan juntas y laten despues
        for d, g in ((-det, 1.0), (det, 0.55)):
            s += g * a * np.sin(2 * np.pi * fr * (1 + d) * t + fi) * np.exp(-t / (tau / r ** 0.6))
    a = min(len(t), n_(ataque))
    s[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    if temblor:
        s *= 1 - temblor * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(5.0, 6.5) * t + rng.uniform(0, 6)))
    f_ = max(1, len(s) // 8)
    s[-f_:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f_))
    return s


# ======================================================================
#  LAS HABILIDADES
# ======================================================================
def muralla():
    """La Muralla de Jade: el muro sube del suelo rozando la tierra (piedra
    que se arrastra, cada vez mas deprisa y mas aguda al subir, el suelo que
    retumba y la tierra que cae de encima), se asienta de golpe (el golpe
    hondo de la tierra, la piedra que se raja y lo que salta), el jade suena
    entero como una piedra sonora (dos notas en quinta, con sus lascas) y
    debajo queda un tono grave y desafiante: una quinta honda de metal que se
    hincha y se apaga."""
    d = 2.45
    sube = 0.72                                   # cuando se asienta
    ns = n_(sube + 0.04)
    vel = curva(ns, [(0, 0.15), (0.3, 0.8), (0.85, 1.0), (1, 0.4)])
    roce = moler(sube + 0.04, 1.0, (35, 110), 0.7, velocidad=vel)
    roce = mezclar(pico(filtro_mov(roce, curva(ns, [(0, 240), (1, 950)]), 'band', 1.6, 32), 1.0), pico(pb(roce, 700), 0.5))
    roce *= curva(ns, [(0, 0.0), (0.2, 0.25), (0.9, 1.0), (1, 0.6)])
    tiembla = retumbo(sube + 0.1, 100, 3.0, 0.4, 0.5) * curva(n_(sube + 0.1), [(0, 0.05), (0.85, 1.0), (1, 0.7)])
    tierra = grava(sube, curva(ns - n_(0.04), [(0, 20), (0.7, 260), (1, 120)]), (0.4, 2.0))

    golpe = golpe_tierra(1.15, 0.7, 0.55, 1.8)

    jade1 = jade(hz(76), None, 0.55, JADE_TALLA, 0.8)          # mi 5
    jade2 = jade(hz(83), None, 0.42, JADE, 0.6)                # si 5: la quinta
    lascas = esquirlas(6, 0.35, 2600, 6800, 1.0)
    brillo = canto_jade(1.4, hz(88), JADE[:3], 260, 0.9) * caida(1.4, 0.35, 0.05)

    dt = 1.65
    nt = n_(dt)
    tt = t_(dt)
    env = curva(nt, [(0, 0.0), (0.06, 0.55), (0.32, 1.0), (0.62, 0.55), (1, 0.0)])
    raiz = hz(40) * (1 - 0.05 * np.exp(-tt / 0.06)) * (1 + 0.004 * paso((tt - 0.4) / 0.3) * np.sin(2 * np.pi * 4.8 * tt))
    tono = mezclar(pico(metal_tono(raiz, env, 3, 7.0, 300, 2600), 1.0),
                   pico(metal_tono(raiz * 1.5, env * 0.9, 2, 6.0, 340, 2800), 0.7),
                   pico(np.sin(2 * np.pi * np.cumsum(raiz * 0.5) / SR) * env, 0.2))
    tono = saturar(tono / np.max(np.abs(tono)), 1.6)

    capas = mezclar(pico(roce, 0.32), pico(tiembla, 0.2), pico(tierra, 0.18),
                    en(sube, pico(golpe, 1.0)),
                    en(sube + 0.004, pico(jade1, 0.42)), en(sube + 0.03, pico(jade2, 0.3)),
                    en(sube + 0.01, pico(lascas, 0.2)), en(sube + 0.05, pico(brillo, 0.12)),
                    en(sube + 0.06, pico(tono, 0.42)))
    return cortar(reverb(capas, 0.22, 1.5, 5500), d, 0.4)


def manantial():
    """El Manantial: el agua que brota del suelo (unos gorgoteos graves, el
    agua que sube y se abre en agudos al salir, una nube de burbujas cada vez
    mas pequenas y seguidas) y encima una campanilla de cura que brilla: un
    arpegio que sube, de cristal mojado, que tiembla como el agua y gira un
    poco (un remolino lento), y unas gotas al final."""
    d = 2.25
    n = n_(d)
    t = t_(d)
    glugs = mezclar(*[en(s, burbuja(r, 0.35, a, 1.4, 0.004))
                      for s, r, a in ((0.05, 13.0, 0.35), (0.14, 10.5, 0.55), (0.22, 11.5, 0.8), (0.3, 8.5, 1.0),
                                      (0.38, 9.5, 0.85))])
    fc = curva(n, [(0, 220), (0.25, 1900), (0.5, 1300), (1, 600)])
    brota = filtro_mov(ruido(d, 'rosa'), fc, 'low', 0.8) * curva(n, [(0, 0), (0.08, 0.4), (0.25, 1.0), (0.55, 0.45), (1, 0)])
    brota *= np.exp(0.35 * suave(n, 6))
    grandes = nube(d, curva(n, [(0, 30), (0.2, 260), (0.5, 80), (1, 0)]), 2.0, 6.0, 2.0, 0.15)
    chicas = nube(d, curva(n, [(0, 0), (0.18, 150), (0.38, 900), (0.7, 180), (1, 0)]), 0.6, 2.0, 1.8, 0.2)

    notas = (hz(81), hz(85), hz(88), hz(93), hz(97))           # la mayor que sube: la5 do#6 mi6 la6 do#7
    arpegio = mezclar(*[en(0.42 + 0.085 * k, pico(cristal(f, 0.75 - 0.06 * k, 0.012, temblor=0.18), 1.0 - 0.1 * k))
                        for k, f in enumerate(notas)])
    halo = mezclar(en(0.8, pico(cristal(hz(69), 0.6, 0.12, ((1, 1.0), (2, 0.2))), 0.4)),
                   en(0.82, pico(cristal(hz(76), 0.55, 0.12, ((1, 1.0), (2, 0.15))), 0.3)))
    cura = flanger(mezclar(arpegio, halo), 0.7, 1.2, 2.5, 0.35)
    gotas = goteo(1.0, 5, 1.1, 0.6)

    capas = mezclar(pico(glugs, 0.3), pico(brota, 0.42), pico(grandes, 0.35), pico(chicas, 0.3),
                    pico(cura, 0.55), pico(gotas, 0.2))
    return cortar(reverb(capas, 0.25, 1.6, 5000), d + 0.2, 0.4)


def manantial_pulso():
    """El pulso del Manantial (suena cada 3 s mientras dura): una burbuja
    grande y blanda que sube de tono y dos notas de cristal en quinta (do6 y
    sol6), muy suaves. Sin ruido, sin golpe, con el ataque redondo y sin
    agudos que piquen: se oye muchas veces seguidas y no debe cansar."""
    burb = burbuja(5.5, 0.3, 1.0, 0.65, 0.006)
    a = cristal(hz(84), 0.16, 0.01, ((1, 1.0), (2.0, 0.06)))
    b = cristal(hz(91), 0.14, 0.012, ((1, 1.0), (2.0, 0.05)))
    capas = mezclar(pico(burb, 0.55), en(0.03, pico(a, 0.75)), en(0.075, pico(b, 0.5)))
    return cortar(pb(reverb(capas, 0.2, 0.9, 4500), 6500), 0.6, 0.2)


def corriente():
    """La Corriente Ascendente: la rafaga que aparta a los mobs (un empujon
    de aire con su golpe de presion), la corriente que sube silbando cada vez
    mas aguda, unas plumas que aletean dentro (batidas cada vez mas seguidas)
    y una campanilla de viento que suena con ella."""
    d = 1.9
    n = n_(d)
    empujon = batida(0.55, 1.0)
    sube = pa(viento(d, [(0, 300), (0.3, 600), (0.65, 1900), (1, 3600)], 2.4, 0.4), 220)
    sube *= curva(n, [(0, 0), (0.1, 0.3), (0.25, 0.22), (0.62, 1.0), (0.82, 0.7), (1, 0)])
    silbo = aullido(d, [(0, 620), (0.35, 950), (0.7, 2000), (1, 2900)], 14)
    silbo *= curva(n, [(0, 0), (0.3, 0.3), (0.62, 1.0), (0.85, 0.6), (1, 0)])
    silbo2 = aullido(d, [(0, 930), (0.35, 1425), (0.7, 3000), (1, 4350)], 20)
    silbo2 *= curva(n, [(0, 0), (0.4, 0.15), (0.68, 1.0), (0.9, 0.3), (1, 0)])
    aleteos = mezclar(*[en(s, pico(plumas(dd, 22 + 4 * k, 450, 3200), 1.0 - 0.12 * k))
                        for k, (s, dd) in enumerate(((0.2, 0.17), (0.4, 0.15), (0.57, 0.14), (0.72, 0.12), (0.85, 0.11)))])
    tubos = (hz(86), hz(88), hz(91), hz(93), hz(95))          # re6 mi6 sol6 la6 si6: pentatonica
    campana = campanillas(1.3, curva(n_(1.3), [(0, 3), (0.3, 10), (0.7, 7), (1, 0)]), tubos, (0.35, 0.7))
    golpe_tubo = tubo(hz(91), 0.8)                             # el primero, seguro, con la corriente
    capas = mezclar(pico(empujon, 0.75), pico(sube, 0.8), pico(silbo, 0.3), pico(silbo2, 0.14),
                    pico(aleteos, 0.5), en(0.42, pico(golpe_tubo, 0.4)), en(0.45, pico(campana, 0.45)))
    return cortar(reverb(capas, 0.22, 1.5, 7000), d + 0.1, 0.35)


def furia():
    """La Furia Solar: el aire que se traga la llama, el fuego que prende de
    golpe y ruge, una campana de oro, destellos de sol, y un tono heroico que
    sube una octava con su quinta, brillante como un metal, mientras el fuego
    se va apagando."""
    d = 2.5
    asp = 0.16
    prende = ignicion(1.5, 1.0, 4500.0, 58.0, asp)
    nl = n_(2.1)
    ruge = llama(2.1, 1.0, curva(nl, [(0, 1.6), (0.3, 1.2), (1, 0.7)]), 9.0, 1.2, 0.8)
    ruge *= curva(nl, [(0, 0), (0.06, 1.0), (0.35, 0.75), (1, 0)])
    brasas = chasquidos(2.0, 140 * np.exp(-t_(2.0) / 0.5) + 10)
    oro = mezclar(pico(campana_oro(hz(74), 0.9), 1.0), en(0.025, pico(campana_oro(hz(81), 0.7), 0.6)))
    sol = destellos(1.6, curva(n_(1.6), [(0, 8), (0.25, 60), (0.6, 25), (1, 0)]), 2600, 8000)

    dt = 1.9
    nt = n_(dt)
    tt = t_(dt)
    x = paso(tt / 0.75)
    raiz = hz(50) * 2 ** x * (1 + 0.005 * paso((tt - 0.9) / 0.4) * np.sin(2 * np.pi * 5.2 * tt))   # re3 -> re4
    env = curva(nt, [(0, 0.0), (0.05, 0.35), (0.42, 1.0), (0.65, 0.8), (1, 0.0)])
    tono = mezclar(pico(metal_tono(raiz, env, 3, 7.0, 500, 4500), 1.0),
                   pico(metal_tono(raiz * 1.5, env * 0.95, 3, 6.0, 550, 4800), 0.7),
                   pico(metal_tono(raiz * 2.0, env * 0.8, 2, 5.0, 600, 5000), 0.4))

    capas = mezclar(pico(prende, 1.0), en(asp, pico(ruge, 0.45)), en(asp + 0.05, pico(brasas, 0.22)),
                    en(asp + 0.03, pico(oro, 0.35)), en(asp + 0.06, pico(sol, 0.26)), en(asp + 0.02, pico(tono, 0.38)))
    return cortar(reverb(capas, 0.22, 1.6, 6000), d, 0.4)


def lista():
    """La habilidad vuelve a estar lista: dos notas de cristal que suben una
    cuarta (re6 y sol6), cortas y suaves, con el ataque redondo y sin ruido.
    Neutro: vale para los cuatro elementos."""
    a = cristal(hz(86), 0.09, 0.004, ((1, 1.0), (2.0, 0.12), (3.0, 0.03)))
    b = cristal(hz(91), 0.17, 0.004, ((1, 1.0), (2.0, 0.1), (3.0, 0.025)))
    capas = mezclar(pico(a, 0.75), en(0.075, pico(b, 1.0)))
    return cortar(pb(reverb(capas, 0.15, 0.7, 6000), 8000), 0.45, 0.15)


def martillo_carga(k):
    """El golpe cargado del Martillo de Jade: el martillo que baja pesado
    cortando el aire, el golpe contra el suelo (presion, cuerpo sordo, la
    tierra que cede y lo que salta), el jade que se raja con sus lascas y el
    golpe que aturde: un 'bum' sordo y hondo que llega justo detras, como una
    onda, y un pitido de jade que se tambalea (el mareo) y se apaga."""
    d = 1.2
    baja = pasada(0.17, 650 * (1, 0.9)[k], 240, 1.5, 0.12)
    golpe = golpe_tierra(0.85, 0.8, 0.45, 1.0)
    raja = mezclar(pico(rajar_roca(12, 0.045, (1.15, 1.0)[k], 0.9), 1.0),
                   pico(jade(rng.uniform(1900, 2300), None, 0.1, JADE_TALLA, 1.0), 0.5),
                   en(0.01, pico(esquirlas(5, 0.25, 2600, 6500), 0.45)))
    tt = t_(0.7)
    onda = saturar(boom(62 * (1, 0.92)[k], 32, 0.085, 0.7), 2.2)
    sordo = pb(ruido(0.3, 'rosa'), 300) * caida(0.3, 0.045, 0.003)
    f_mareo = hz((79, 78)[k]) * (1 + 0.03 * np.sin(2 * np.pi * 5.5 * tt) * (1 - np.exp(-tt / 0.1)))
    mareo = np.sin(2 * np.pi * np.cumsum(f_mareo) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f_mareo * 2.756) / SR)
    mareo *= np.clip(tt / 0.03, 0, 1) * np.exp(-tt / 0.22) * (1 + 0.35 * np.sin(2 * np.pi * 7 * tt))
    capas = mezclar(pico(baja, 0.3), en(0.15, pico(golpe, 1.0)), en(0.152, pico(raja, 0.8)),
                    en(0.21, pico(onda, 0.5)), en(0.21, pico(sordo, 0.45)), en(0.23, pico(mareo, 0.13)))
    # por debajo de 40 Hz casi nada se oye y se come el pico: fuera
    return cortar(reverb(pa(capas, 40, 2), 0.2, 1.3, 5000), d, 0.4)


def tridente_lanzar():
    """El Tridente de las Mareas sale lanzado: el impulso (un soplo corto y
    un roce de acero al soltarlo), el tridente que corta el aire y se aleja
    (la banda sube y luego cae con el Doppler; las tres puntas silban a la
    vez, un pelo desafinadas) y la estela de agua que va soltando: rocio,
    burbujitas y unas gotas que caen detras."""
    d = 0.75
    n = n_(d)
    t = t_(d)
    ataque = 0.05
    env = np.where(t < ataque, (t / ataque) ** 1.5, np.exp(-(t - ataque) / 0.16))
    fb = curva(n, [(0, 900), (0.08, 3000), (0.4, 1900), (1, 1100)])
    corte = pa(filtro_mov(ruido(d, 'rosa'), fb, 'band', 2.6), 300) * env
    puntas = sum(filtro_mov(ruido(d), fb * 1.45 * r, 'band', 28, 32) for r in (0.985, 1.0, 1.017)) * env
    soplo = bp(ruido(0.08, 'rosa'), 180, 1000) * caida(0.08, 0.02, 0.006)
    acero = shing(3100, 0.16, 0.035, 1.0)
    rocio = bp(ruido(d), 2500, 8000) * np.exp(0.8 * suave(n, 40)) * np.interp(t, [0, 0.04, 0.15, d], [0, 1, 0.6, 0])
    estela = nube(d, curva(n, [(0, 0), (0.1, 300), (0.5, 120), (1, 0)]), 0.5, 1.6, 1.8, 0.25)
    gotas = goteo(0.4, 4, 0.18, 0.7)
    capas = mezclar(pico(soplo, 0.3), pico(corte, 0.8), pico(puntas, 0.35), en(0.012, pico(acero, 0.16)),
                    pico(rocio, 0.13), en(0.04, pico(estela, 0.3)), pico(gotas, 0.18))
    return cortar(reverb(capas, 0.18, 1.0, 6000), d, 0.2)


def tridente_vuelve():
    """El tridente vuelve a la mano: un remolino de agua al reves (en vez de
    apagarse crece: el agua que se recoge alrededor), el tridente que se
    acerca (la banda sube con el Doppler), el toque blando al cogerlo y una
    campanilla suave de cristal."""
    d = 0.8
    llega = 0.48
    nr = n_(llega)
    tr = t_(llega)
    agua = mezclar(pico(bp(ruido(llega, 'rosa'), 300, 3500), 0.7),
                   pico(nube(llega, 1400 * np.exp(-tr / 0.12), 0.7, 3.5, 2.0, 0.2)[:nr], 0.8))
    remolino = flanger(agua * np.exp(-tr / 0.11), curva(nr, [(0, 9.0), (1, 2.0)]), 1.0, 4.0, 0.8)[::-1].copy()
    remolino[-n_(0.012):] *= np.linspace(1, 0.3, n_(0.012))
    fb = curva(nr, [(0, 1000), (0.7, 1700), (1, 2900)])
    acerca = filtro_mov(ruido(llega, 'rosa'), fb, 'band', 1.8) * rampa(llega, 2.4)
    silba = filtro_mov(ruido(llega), fb * 1.5, 'band', 26, 32) * rampa(llega, 3.0)
    coge = golpe_seco(190, 0.08, 0.014)
    son = mezclar(pico(cristal(hz(91), 0.13, 0.004), 1.0), en(0.045, pico(cristal(hz(98), 0.11, 0.004), 0.6)))
    gotas = goteo(0.2, 2, 0.04, 0.6)
    capas = mezclar(pico(remolino, 0.7), pico(acerca, 0.5), pico(silba, 0.12),
                    en(llega, pico(coge, 0.45)), en(llega + 0.004, pico(son, 0.4)), en(llega, pico(gotas, 0.15)))
    return cortar(reverb(capas, 0.18, 1.0, 6000), d, 0.15)


def tridente_cura():
    """El tridente cura a un aliado: dos gotas que caen en el agua y un
    destello de cristal mojado que sube (tres notas muy rapidas y suaves)."""
    gotas = mezclar(gota(2.6, 1.0, 0.06, 0.002), en(0.055, gota(1.9, 0.7, 0.06, 0.002)))
    notas = mezclar(*[en(0.02 + 0.04 * k, pico(cristal(f, 0.1 + 0.05 * k, 0.005, temblor=0.15), 1.0 - 0.15 * k))
                      for k, f in enumerate((hz(93), hz(97), hz(100)))])
    capas = mezclar(pico(gotas, 0.45), pico(notas, 0.65))
    return cortar(pb(reverb(capas, 0.2, 0.9, 6000), 8500), 0.55, 0.15)


def arco_disparo(k):
    """El Arco del Vendaval dispara: el chasquido de la cuerda al soltarse,
    la cuerda que vibra un instante (muy amortiguada, el tono cae un pelo al
    destensarse) y el golpe sordo de las palas; y la flecha que sale envuelta
    en viento: un soplo que se aleja (la banda sube y cae) con un silbido."""
    d = 0.6
    n = n_(d)
    t = t_(d)
    f0 = (150.0, 172.0)[k]
    dc = 0.22
    tc = t_(dc)
    fase = 2 * np.pi * np.cumsum(f0 * (1 - 0.04 * np.exp(-tc / 0.015))) / SR
    cuerda = sum(np.sin(j * fase + rng.uniform(0, 6)) / j ** 1.1 * np.exp(-tc / (0.06 / j ** 0.4)) for j in range(1, 14))
    cuerda *= np.clip(tc / 0.001, 0, 1)
    chasq = pa(ruido(0.004), 1500) * caida(0.004, 0.0007, 0.0001)
    palas = boom(140, 85, 0.025)
    ataque = 0.03
    env = np.where(t < ataque, (t / ataque) ** 1.3, np.exp(-(t - ataque) / (0.085, 0.075)[k]))
    fb = curva(n, [(0, 1600), (0.07, (3900, 4400)[k]), (0.5, 2100), (1, 1500)])
    flecha = pa(filtro_mov(ruido(d, 'rosa'), fb, 'band', 2.2), 450) * env
    silbido = filtro_mov(ruido(d), fb * 0.75, 'band', 30, 32) * env ** 1.3
    racha = pa(viento(d, [(0, 900), (0.4, 1600), (1, 1100)], 1.2, 0.5), 400) * np.interp(t, [0, 0.05, 0.2, d], [0, 1, 0.4, 0])
    capas = mezclar(pico(chasq, 0.3), pico(cuerda, 0.55), pico(palas, 0.4), en(0.008, pico(flecha, 0.75)),
                    en(0.01, pico(silbido, 0.2)), en(0.02, pico(racha, 0.25)))
    return cortar(reverb(capas, 0.16, 1.0, 7000), d, 0.15)


def flecha_aliado():
    """Una flecha del Vendaval alcanza a un aliado y le da velocidad: un toque
    blando (la flecha se deshace en viento, no hiere), un soplo que sube
    alrededor y una campanilla de aire: tres tubos que suben."""
    d = 0.55
    n = n_(d)
    t = t_(d)
    toque = mezclar(pico(pb(ruido(0.06), 1400) * caida(0.06, 0.008, 0.001), 1.0), pico(boom(220, 140, 0.02), 0.5))
    soplo = pa(viento(d, [(0, 1100), (0.6, 3600), (1, 5200)], 1.6, 0.4), 500) * np.interp(t, [0, 0.03, 0.18, d], [0, 1, 0.7, 0])
    tubos = mezclar(*[en(0.02 + 0.05 * j, pico(tubo(f, 0.35 - 0.04 * j, 0.2), 1.0 - 0.12 * j))
                      for j, f in enumerate((hz(88), hz(93), hz(98)))])
    capas = mezclar(pico(toque, 0.35), pico(soplo, 0.45), pico(tubos, 0.5))
    return cortar(pb(reverb(capas, 0.18, 1.0, 7000), 9000), d, 0.15)


# ======================================================================
#  LOS GOLPES DE LAS ARMAS (sounds/espada, como los <tema>_golpe)
# ======================================================================
def solar_golpe(k):
    """El Mandoble Solar: un filo pesado. El corte del aire (grave, de hoja
    ancha), el golpe seco en el cuerpo, un 'shing' de acero, la llama que
    prende un instante en el tajo ('fwump' corto), las brasas que saltan y el
    oro de la hoja que queda sonando."""
    corte = barrido(0.16, 2600, 700, q=2.2, env=np.sin(np.linspace(0, np.pi, n_(0.16))) ** 1.5)
    t = t_(0.7)
    capas = [(corte, 0.5, 0.0), (golpe_seco(92 + 8 * k, 0.16, 0.04), 0.85, 0.035),
             (shing(2300 * (1, 1.05, 0.95)[k], 0.24, 0.065, 0.95), 0.45, 0.035),
             (ignicion(0.6, 1.0, 3200.0, 70.0), 0.6, 0.03),
             (chasquidos(0.7, 500 * np.exp(-t / 0.1) + 25) * np.exp(-t / 0.22), 0.35, 0.04),
             (campana_oro(880 * (1, 1.06, 0.94)[k], 0.22, 0.6), 0.2, 0.038)]
    return montar(0.78, *capas)


def jade_martillo(k):
    """El Martillo de Jade, golpe normal: pesado y romo, sin filo. El
    martillo que corta el aire despacio (grave), el golpe sordo (un 'tum'
    hondo y un cuerpo de ruido grave), la piedra que cruje, unas chinas que
    caen y un toque apagado del jade de la cabeza."""
    corte = barrido(0.12, 1100, 420, q=1.8, env=np.sin(np.linspace(0, np.pi, n_(0.12))) ** 1.5)
    g = 0.035
    cuerpo = pb(ruido(0.3, 'rosa'), 520) * caida(0.3, 0.045, 0.002)
    aplasta = bp(ruido(0.25, 'rosa'), 250, 2500) * caida(0.25, 0.03, 0.001)
    capas = [(corte, 0.3, 0.0), (golpe_seco(60 + 6 * k, 0.24, 0.065), 0.8, g),
             (cuerpo, 0.7, g), (aplasta, 0.6, g), (pico(boom(95 + 8 * k, 45, 0.06)), 0.4, g),
             (rajar_roca(8, 0.035, (0.9, 1.0, 0.95)[k], 0.9), 0.8, g + 0.004),
             (grava(0.5, 300 * np.exp(-t_(0.5) / 0.12) + 20, (0.4, 3.0)) * np.exp(-t_(0.5) / 0.18), 0.45, g + 0.02),
             (jade(620 * (1, 0.93, 1.08)[k], None, 0.06, JADE_TALLA, 0.4), 0.22, g + 0.002)]
    return montar(0.6, *capas)


def mareas_tridente(k):
    """El Tridente de las Mareas en cuerpo a cuerpo: una estocada. Un soplo
    corto que avanza (la banda sube y se corta), el pinchazo de las tres
    puntas al entrar (tres chasquidos de acero casi a la vez), el golpe seco,
    y el agua: un chapoteo, burbujas que suben y unas gotas."""
    g = 0.035
    n = n_(g + 0.01)
    env = np.concatenate([np.linspace(0, 1, n_(g)) ** 1.6, np.linspace(1, 0, n - n_(g))])
    estocada = barrido(g + 0.01, 1100, 3400, q=2.4, env=env)
    puntas = mezclar(*[en(0.0035 * j, pico(shing(2900 * r, 0.1, 0.022, 1.0), 1.0 - 0.15 * j))
                       for j, r in enumerate(((1.0, 1.08, 0.93), (1.04, 0.97, 1.0), (0.95, 1.02, 1.07))[k])])
    capas = [(estocada, 0.45, 0.0), (puntas, 0.42, g), (golpe_seco(125 + 10 * k, 0.1, 0.025), 0.65, g + 0.002),
             (chapoteo(0.36, 2300 + 300 * k), 0.5, g + 0.005)]
    capas.append((nube(0.4, 900 * np.exp(-t_(0.4) / 0.08), 0.9, 4.0, 2.0, 0.2), 0.28, g + 0.01))
    capas.append((goteo(0.18, 3 + k, 0.0, 0.8), 0.14, g + 0.09))
    return montar(0.55, *capas)


# ======================================================================
#  Guardar
# ======================================================================
def sonoridad_a(x):
    """Sonoridad (dB, ponderacion A) de los 400 ms mas fuertes."""
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


def _escribir(ruta, x):
    """Escribe el .ogg y lo vuelve a leer: Vorbis puede subir un pelo los
    picos; si pasan de -2,5 dBFS se baja y se escribe otra vez."""
    for _ in range(3):
        sf.write(ruta, x.astype(np.float32), SR, format='OGG', subtype='VORBIS')
        z, _sr = sf.read(ruta, dtype='float64')
        pk = np.max(np.abs(z))
        if pk <= 10 ** (-2.5 / 20):
            break
        x = x * (ALTO / pk)
    return z


def limitar(x, umbral=0.55):
    """Compresion suave de los picos: mas cuerpo sin que nada recorte."""
    y = pico(x)
    m = np.abs(y)
    sobre = m > umbral
    y[sobre] = np.sign(y[sobre]) * (umbral + (1 - umbral) * np.tanh((m[sobre] - umbral) / (1 - umbral)))
    return y


def guardar(carpeta, nombre, x, techo=None, alto=ALTO, largo=None, limite=None):
    """Recorta la cola que ya no se oye (por debajo de -58 dB del pico) o lo
    que pase de `largo`, la apaga sin clic, deja el pico en `alto` y, si hay
    `techo` (dB A), baja el sonido hasta esa sonoridad como mucho. `limite`:
    comprime un poco los picos antes (los golpes muy graves, para que tengan
    cuerpo sin pasarse del pico)."""
    x = pa(np.asarray(x, dtype=float), 25)
    if limite:
        x = limitar(x, limite)
    m = np.max(np.abs(x))
    resto = np.nonzero(np.abs(x) > m * 10 ** (-58 / 20))[0]
    if len(resto):
        x = x[:min(len(x), resto[-1] + n_(0.06))].copy()
    if largo and len(x) > n_(largo):
        x = x[:n_(largo)].copy()
        r = n_(min(0.3, largo * 0.25))
        x[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    f = min(len(x) // 4, n_(0.003))
    x[:f] *= np.linspace(0, 1, f)
    g = min(len(x) // 4, n_(0.03))
    x[-g:] *= np.linspace(1, 0, g)
    x = pico(x, alto)
    if techo is not None:
        x *= min(1.0, 10 ** ((techo - sonoridad_a(x)) / 20))
    destino = os.path.join(SONIDOS, carpeta)
    os.makedirs(destino, exist_ok=True)
    z = _escribir(os.path.join(destino, nombre + '.ogg'), x)
    GUARDADOS.append((f'{carpeta}/{nombre}', z))
    if REVISION:
        os.makedirs(REVISION, exist_ok=True)
        sf.write(os.path.join(REVISION, nombre + '.wav'), z.astype(np.float32), SR)
    pk = 20 * np.log10(np.max(np.abs(z)) + 1e-12)
    rms = 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-12)
    print(f'  {carpeta + "/" + nombre:28s} {len(z) / SR:5.2f} s  pico {pk:6.1f} dBFS  rms {rms:6.1f} dB  '
          f'A {sonoridad_a(z):6.1f} dB', flush=True)


# ======================================================================
#  Todos
# ======================================================================
# Los bancos (piedras, brasas) se hacen una vez y con su propia semilla: asi
# no importa que sonido los pida primero.
sembrar('bancos')
_piedras()
_chasquidos_banco()

# (carpeta, nombre, funcion, techo de sonoridad en dB A o None, compresion o
# None). Todo con el pico a -3 dBFS como los golpes de espada (que estan entre
# -23 y -30 dB A); los toques tonales y los que se repiten llevan techo, y los
# golpes de las armas no pasan de -23 dB A, como los de espada mas fuertes.
SONIDOS_NUEVOS = [
    ('armadura', 'muralla', muralla, -19.0, None),
    ('armadura', 'manantial', manantial, -21.0, None),
    ('armadura', 'manantial_pulso', manantial_pulso, -29.0, None),
    ('armadura', 'corriente', corriente, -20.0, None),
    ('armadura', 'furia', furia, -19.0, None),
    ('armadura', 'lista', lista, -28.0, None),
    ('armadura', 'martillo_carga', lambda: martillo_carga(0), -25.0, 0.6),
    ('armadura', 'martillo_carga2', lambda: martillo_carga(1), -25.0, 0.6),
    ('armadura', 'tridente_lanzar', tridente_lanzar, -23.0, None),
    ('armadura', 'tridente_vuelve', tridente_vuelve, -24.0, None),
    ('armadura', 'tridente_cura', tridente_cura, -27.0, None),
    ('armadura', 'arco_disparo1', lambda: arco_disparo(0), -23.0, None),
    ('armadura', 'arco_disparo2', lambda: arco_disparo(1), -23.0, None),
    ('armadura', 'flecha_aliado', flecha_aliado, -26.0, None),
] + [('espada', f'solar_golpe{k + 1}', (lambda k=k: solar_golpe(k)), -23.0, None) for k in range(3)] \
  + [('espada', f'jade_martillo{k + 1}', (lambda k=k: jade_martillo(k)), -23.0, 0.6) for k in range(3)] \
  + [('espada', f'mareas_tridente{k + 1}', (lambda k=k: mareas_tridente(k)), -23.0, None) for k in range(3)]

for carpeta, nombre, fn, techo, limite in SONIDOS_NUEVOS:
    sembrar(nombre)
    guardar(carpeta, nombre, fn(), techo, limite=limite)


# ----------------------------------------------------------------------
#  Hoja de revision: la onda y el espectrograma de cada uno
# ----------------------------------------------------------------------
if REVISION:
    from PIL import Image, ImageDraw
    an, al_onda, al_esp, col = 640, 80, 170, 2
    alto_celda = 16 + al_onda + al_esp + 10
    filas = (len(GUARDADOS) + col - 1) // col
    hoja = Image.new('RGB', (an * col, alto_celda * filas), (12, 14, 18))
    dib = ImageDraw.Draw(hoja)
    escala_s = 2.7                                   # segundos que caben a lo ancho (todos a la misma escala)
    px_s = (an - 50) / escala_s
    for k, (nombre, x) in enumerate(GUARDADOS):
        cx, cy = (k % col) * an + 40, (k // col) * alto_celda
        ancho = max(1, int(px_s * len(x) / SR))
        y0 = cy + 16 + al_onda
        # la envolvente (rms en ventanas de 10 ms) en dB, de -54 a 0 dBFS, con
        # rayas cada 12 dB; la raya roja es el pico de -3 dBFS
        for db in (-12, -24, -36, -48):
            yy = y0 - int(al_onda * (db + 54) / 54)
            dib.line([(cx, yy), (cx + ancho, yy)], fill=(40, 44, 52))
            dib.text((cx - 28, yy - 6), str(db), fill=(110, 110, 110))
        w = n_(0.01)
        for i in range(ancho):
            a, b = int(i * len(x) / ancho), int((i + 1) * len(x) / ancho)
            c = x[max(0, a - w // 2):max(b, a + w // 2)]
            r = np.sqrt(np.mean(c ** 2)) if len(c) else 0.0
            p = np.max(np.abs(x[a:max(b, a + 1)]))
            hr = int(al_onda * np.clip((20 * np.log10(r + 1e-9) + 54) / 54, 0, 1))
            hp = int(al_onda * np.clip((20 * np.log10(p + 1e-9) + 54) / 54, 0, 1))
            dib.line([(cx + i, y0), (cx + i, y0 - hp)], fill=(50, 90, 110))
            dib.line([(cx + i, y0), (cx + i, y0 - hr)], fill=(120, 200, 230))
        yy = y0 - int(al_onda * 51 / 54)
        dib.line([(cx, yy), (cx + ancho, yy)], fill=(200, 80, 80))
        # el espectrograma, eje de frecuencia logaritmico de 30 Hz a 16 kHz
        f, tt, S = signal.spectrogram(x, SR, nperseg=1024, noverlap=960)
        S = 10 * np.log10(S + 1e-12)
        S = np.clip((S - (S.max() - 72)) / 72, 0, 1)
        fl = np.geomspace(30, 16000, al_esp)
        idx = np.clip(np.searchsorted(f, fl), 0, len(f) - 1)
        im = Image.fromarray((S[idx][::-1] * 255).astype(np.uint8)).resize((ancho, al_esp), Image.BILINEAR)
        hoja.paste(Image.merge('RGB', (im, im.point(lambda v: int(v * 0.8)), im.point(lambda v: int(v * 0.5)))),
                   (cx, y0 + 2))
        for fr, txt in ((100, '100'), (1000, '1k'), (10000, '10k')):
            yy = y0 + 2 + int(al_esp * (1 - np.log(fr / 30) / np.log(16000 / 30)))
            dib.line([(cx - 6, yy), (cx + ancho, yy)], fill=(70, 70, 70))
            dib.text((cx - 32, yy - 6), txt, fill=(110, 110, 110))
        for s in np.arange(0.0, len(x) / SR, 0.1):     # una marca cada 100 ms
            xx = cx + int(px_s * s)
            dib.line([(xx, y0 + al_esp + 2), (xx, y0 + al_esp + (8 if round(s * 10) % 5 == 0 else 5))], fill=(150, 150, 150))
        dib.text((cx, cy + 2), f'{nombre}  {len(x) / SR:.2f} s  pico {20 * np.log10(np.max(np.abs(x))):.1f} dBFS  '
                 f'rms {20 * np.log10(np.sqrt(np.mean(x ** 2))):.1f} dB  A {sonoridad_a(x):.1f} dB', fill=(220, 220, 220))
    hoja.save(os.path.join(REVISION, 'revision.png'))
    print('hoja:', os.path.join(REVISION, 'revision.png'))
