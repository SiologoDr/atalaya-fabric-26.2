"""
Musica de trailer para el video, sintetizada: nada de bancos de sonidos.

Un dron en re menor que respira, un latido grave, "braams" (golpes de metal
grave de trailer) en los momentos que se le pasen, un ascenso de ruido antes
del cierre y un golpe final con cola.
"""
import numpy as np
from scipy import signal

SR = 48000

def _t(d):
    return np.arange(int(d * SR)) / SR

def _env(d, a=0.01, curva=4.0):
    t = _t(d); e = np.exp(-curva * t / d); n = int(a * SR)
    if n:
        e[:n] *= np.linspace(0, 1, n)
    return e

def _lp(x, f):
    return signal.sosfilt(signal.butter(2, f, 'lowpass', fs=SR, output='sos'), x)

def _bp(x, lo, hi):
    return signal.sosfilt(signal.butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)

def _saw(f, d, det=0.0):
    t = _t(d)
    fase = (f * (1 + det)) * t
    return 2 * (fase % 1.0) - 1

def braam(d=3.0):
    """Metal grave de trailer: sierras en re desafinadas, saturadas, filtro que se abre y se cierra."""
    x = sum(_saw(f, d, det) for f in (36.7, 73.4, 110.0) for det in (-0.006, 0.0, 0.007))
    x = np.tanh(x * 0.9)
    t = _t(d)
    corte = 120 + 1400 * np.exp(-3.0 * t)       # se abre de golpe y se cierra
    y = np.zeros_like(x)
    # filtro variable por tramos
    paso = SR // 50
    zi = None
    sos = None
    for i in range(0, len(x), paso):
        sos = signal.butter(2, corte[i], 'lowpass', fs=SR, output='sos')
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        y[i:i + paso], zi = signal.sosfilt(sos, x[i:i + paso], zi=zi)
    sub = np.sin(2 * np.pi * 36.7 * t) * 0.8
    return (y + sub) * _env(d, 0.01, 2.2)

def latido():
    d = 0.5
    t = _t(d)
    golpe = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-6 * t) + 38) / SR) * _env(d, 0.003, 7)
    return golpe

def ascenso(d):
    t = _t(d)
    r = np.random.default_rng(3).standard_normal(len(t))
    x = np.zeros_like(r)
    paso = SR // 25
    for i in range(0, len(r), paso):
        f = 300 + 6000 * (i / len(r)) ** 2
        x[i:i + paso] = _bp(r[i:i + paso], f * 0.7, f * 1.3)
    return x * (t / d) ** 2.5 * 0.6

def dron(d):
    t = _t(d)
    x = (_lp(_saw(73.4, d, -0.003) + _saw(73.4, d, 0.004) + 0.6 * _saw(110.0, d, 0.002), 380)
         + 0.4 * np.sin(2 * np.pi * 36.7 * t))
    respiro = 0.65 + 0.35 * np.sin(2 * np.pi * t / 7.0)
    return x * respiro

def componer(duracion, golpes, inicio_cierre, latido_desde, latido_hasta):
    """golpes: lista de segundos donde va un braam. Devuelve estereo (n, 2)."""
    n = int(duracion * SR)
    m = np.zeros(n)
    dr = dron(duracion) * 0.22
    fade = int(2.0 * SR)
    dr[:fade] *= np.linspace(0, 1, fade)
    m += dr
    # latido: 72 ppm, y al doble en el tramo de accion
    t = latido_desde
    while t < latido_hasta:
        i = int(t * SR); l = latido() * 0.55
        m[i:i + len(l)] += l[:max(0, n - i)]
        accion = 0.35 < (t - latido_desde) / max(latido_hasta - latido_desde, 1) < 0.85
        t += 0.42 if accion else 0.83
    for g in golpes:
        i = int(g * SR); b = braam() * 0.75
        m[i:i + len(b)] += b[:max(0, n - i)]
    # ascenso de 2,5 s que muere justo en el cierre, y el golpe final
    a = ascenso(2.5)
    i = int((inicio_cierre - 2.5) * SR)
    m[i:i + len(a)] += a[:max(0, n - i)]
    i = int(inicio_cierre * SR); b = braam(5.0) * 1.0
    m[i:i + len(b)] += b[:max(0, n - i)]
    m = np.tanh(m * 0.9)
    # un pelo de anchura: retardo corto en un canal
    r = np.roll(m, int(0.012 * SR))
    return np.stack([m, 0.85 * m + 0.15 * r], axis=1)
