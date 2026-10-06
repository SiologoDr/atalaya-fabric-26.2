"""
El golpe de las espadas de los jefes (octubre de 2026), sintetizado. Suena
encima del golpe de vanilla, en el momento del impacto: un golpe de espada de
verdad (el corte del aire, el "shing" corto y brillante del filo y el golpe
seco en el cuerpo) con lo de cada jefe por debajo. Tres variantes por espada
(el juego elige una), mono a 44,1 kHz.

  mareas    el filo corta agua: el corte baja de tono, un chapoteo, burbujas
            que suben y gotas que caen
  jade      el filo de piedra: un golpe mas grave, el crujido de roca que se
            raja, grava que cae y un destello de jade muy corto
  vendaval  el filo de viento: el corte del aire es lo que manda (largo, sube
            de tono), un silbido que se va y un "shing" muy claro

La primera version era casi solo una campana larga ("clink") y sonaba rara:
esta es corta (unos 0,4-0,7 s) y ruidosa, como un tajo.

Escribe sounds/espada/<tema>_golpe1..3.ogg (los eventos espada.<tema>_golpe
ya estan en sounds.json y en AtalayaSonidos).

Uso: python armaduras_sonidos.py <raiz> [carpeta para las ondas de revision]
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal

RAIZ = sys.argv[1]
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/espada')
SR = 44100
rng = np.random.default_rng(20261006)


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def ruido(dur):
    return rng.standard_normal(int(SR * dur))


def bp(x, lo, hi, orden=2):
    sos = signal.butter(orden, [lo, hi], btype='bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def pb(x, f, orden=2):
    return signal.sosfilt(signal.butter(orden, f, btype='low', fs=SR, output='sos'), x)


def pa(x, f, orden=2):
    return signal.sosfilt(signal.butter(orden, f, btype='high', fs=SR, output='sos'), x)


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def caida(dur, tau, ataque=0.002):
    x = t_(dur)
    return np.clip(x / ataque, 0, 1) * np.exp(-x / tau)


def barrido(dur, f0, f1, q=2.5, env=None):
    """Ruido por un paso banda que se mueve de f0 a f1 (filtro de estado variable, muestra a muestra)."""
    n = int(SR * dur)
    x = rng.standard_normal(n)
    f = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    out = np.zeros(n)
    lp = bpv = 0.0
    k = 1.0 / q
    for i in range(n):
        g = 2.0 * np.sin(np.pi * min(f[i], SR * 0.22) / SR)
        hp = x[i] - lp - k * bpv
        bpv += g * hp
        lp += g * bpv
        out[i] = bpv
    out = norm(out)
    if env is not None:
        out *= env
    # que se apague del todo al final (sin corte)
    m = max(1, n // 4)
    out[-m:] *= np.linspace(1, 0, m) ** 2
    return out


def shing(f0, dur=0.22, tau=0.07, brillo=1.0):
    """El "shing" del filo: un racimo de parciales agudos, desafinados, que se apaga deprisa; con un poco
    de ruido metalico dentro. Nada de campana: corto y aspero."""
    x = t_(dur)
    out = np.zeros_like(x)
    for r, a in ((1.0, 1.0), (1.27, 0.8), (1.62, 0.65), (2.03, 0.5), (2.51, 0.35), (3.1, 0.22)):
        f = f0 * r * brillo
        if f > SR * 0.45:
            continue
        for desafina in (-0.004, 0.004):
            out += a * np.sin(2 * np.pi * f * (1 + desafina) * x + rng.random() * 6.28) * np.exp(-x / (tau / (0.6 + 0.4 * r)))
    raspa = bp(ruido(dur), f0 * 0.9, min(SR * 0.45, f0 * 3.2)) * np.exp(-x / (tau * 0.5))
    return norm(out) * 0.75 + norm(raspa) * 0.35 * np.clip(x / 0.0015, 0, 1)


def golpe_seco(f=110.0, dur=0.12, tau=0.03):
    """El golpe en el cuerpo: un grave muy corto y un chasquido sordo."""
    x = t_(dur)
    tono = np.sin(2 * np.pi * f * x * (1 - 0.35 * x / dur)) * np.exp(-x / tau)
    sordo = pb(ruido(dur), 900) * np.exp(-x / (tau * 0.5))
    return norm(tono) * 0.8 + norm(sordo) * 0.5


def burbuja(f0, f1, dur):
    x = t_(dur)
    f = f0 + (f1 - f0) * (x / dur) ** 0.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / (dur / 3)) * np.clip(x / 0.002, 0, 1)


def chapoteo(dur=0.35, brillo=2600):
    """Un chapoteo: ruido pasado por un paso bajo que se cierra, con su cola."""
    x = t_(dur)
    env = np.clip(x / 0.004, 0, 1) * np.exp(-x / 0.08)
    return norm(pb(ruido(dur), brillo, 2)) * env


def grava(dur, tasa, lo=1200, hi=5000):
    """Chinas que caen: clics de ruido filtrado, cada vez menos."""
    n = int(SR * dur)
    out = np.zeros(n)
    tiempo = 0.0
    while True:
        tiempo += rng.exponential(1.0 / tasa) * (1 + 3 * tiempo / dur)
        i = int(tiempo * SR)
        if i >= n - 400:
            break
        largo = rng.integers(60, 300)
        clic = bp(rng.standard_normal(largo), lo, hi) * np.exp(-np.arange(largo) / (largo / 4))
        out[i:i + largo] += norm(clic) * rng.uniform(0.3, 1.0) * (1 - tiempo / dur)
    return out


def crujido(dur=0.06):
    """Roca que se raja: un chasquido de banda ancha con unos rebotes."""
    x = t_(dur)
    out = norm(pa(ruido(dur), 500)) * np.exp(-x / 0.008)
    for k in range(3):
        d = int(SR * rng.uniform(0.006, 0.03))
        out[d:] += 0.5 * out[:-d] * 0.6 ** k
    return norm(out)


def sala(x, mezcla=0.18):
    """Una sala corta: que no suene seco."""
    cola = np.zeros(int(SR * 0.35))
    for retardo, g in ((0.017, 0.5), (0.029, 0.4), (0.041, 0.3), (0.063, 0.22), (0.089, 0.15), (0.13, 0.09)):
        cola[int(retardo * SR)] = g
    cola = pb(cola, 5000, 1)
    mojado = signal.fftconvolve(x, cola)[:len(x)]
    return x + mezcla * mojado


def montar(dur, *capas):
    """capas: (onda, ganancia, desde segundos)."""
    out = np.zeros(int(SR * dur))
    for onda, g, desde in capas:
        i = int(SR * desde)
        trozo = onda[:max(0, len(out) - i)]
        out[i:i + len(trozo)] += g * trozo
    out = sala(out)
    # sin siseo por arriba: el filo brilla hasta unos 9 kHz, no mas
    out = pb(out, 9000, 2)
    # sin clic al final y el pico a -3 dBFS
    out[-int(SR * 0.02):] *= np.linspace(1, 0, int(SR * 0.02))
    return norm(out) * 10 ** (-3.0 / 20)


def mareas(k):
    corte = barrido(0.14, 3800, 900, q=2.0, env=np.sin(np.linspace(0, np.pi, int(SR * 0.14))) ** 1.5)
    capas = [(corte, 0.55, 0.0), (golpe_seco(120 + 10 * k), 0.7, 0.03), (shing(2600 * (1, 1.06, 0.95)[k], 0.2, 0.05), 0.45, 0.03),
             (chapoteo(0.38, 2400 + 300 * k), 0.75, 0.035)]
    for j in range(5 + k):
        desde = 0.06 + rng.uniform(0, 0.25)
        f0 = rng.uniform(380, 700)
        capas.append((burbuja(f0, f0 * rng.uniform(1.8, 2.6), rng.uniform(0.02, 0.045)), rng.uniform(0.15, 0.3), desde))
    for j in range(3):
        capas.append((burbuja(2400, 3600, 0.012), 0.12, 0.15 + rng.uniform(0, 0.3)))
    return montar(0.62, *capas)


def jade(k):
    corte = barrido(0.1, 2400, 1200, q=2.5, env=np.sin(np.linspace(0, np.pi, int(SR * 0.1))) ** 1.5)
    capas = [(corte, 0.35, 0.0), (golpe_seco(80 + 8 * k, 0.16, 0.045), 0.95, 0.025),
             (crujido(0.07), 0.7, 0.03), (shing(2100 * (1, 0.94, 1.07)[k], 0.16, 0.04, 0.9), 0.4, 0.028),
             (grava(0.45, 55 + 10 * k), 0.4, 0.05)]
    return montar(0.58, *capas)


def vendaval(k):
    # La racha entra deprisa (el golpe a los 35 ms, como las otras) y sigue despues, subiendo de tono.
    n = int(SR * 0.34)
    sube = int(SR * 0.035)
    env = np.concatenate([np.linspace(0, 1, sube) ** 1.5, np.exp(-np.linspace(0, 3.2, n - sube))])
    corte = barrido(0.34, 700, 4200 * (1, 1.08, 0.92)[k], q=5.0, env=env)
    silbido = barrido(0.4, 2800, 1500, q=14.0, env=np.exp(-np.linspace(0, 5, int(SR * 0.4))))
    capas = [(corte, 0.85, 0.0), (golpe_seco(140 + 10 * k, 0.09, 0.022), 0.5, 0.035),
             (shing(3400 * (1, 1.05, 0.96)[k], 0.24, 0.06, 1.0), 0.5, 0.035), (silbido, 0.25, 0.05)]
    return montar(0.56, *capas)


os.makedirs(SALIDA, exist_ok=True)
REVISION = sys.argv[2] if len(sys.argv) > 2 else None
for nombre, fn in (('mareas', mareas), ('jade', jade), ('vendaval', vendaval)):
    for k in range(3):
        onda = fn(k).astype(np.float32)
        sf.write(os.path.join(SALIDA, f'{nombre}_golpe{k + 1}.ogg'), onda, SR, format='OGG', subtype='VORBIS')
        if REVISION:
            os.makedirs(REVISION, exist_ok=True)
            sf.write(os.path.join(REVISION, f'{nombre}_golpe{k + 1}.wav'), onda, SR)
        # donde cae el golpe y cuanto dura de verdad (por encima de -40 dB)
        env = np.abs(onda)
        pico = env.argmax() / SR
        vivo = np.where(env > 10 ** (-40 / 20))[0]
        print(f'{nombre} {k + 1}: pico a {pico * 1000:.0f} ms, suena {vivo[-1] / SR:.2f} s, rms {20 * np.log10(np.sqrt(np.mean(onda ** 2))):.1f} dB')
