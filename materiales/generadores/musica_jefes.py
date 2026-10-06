"""
MOTOR (en construccion)
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import os, sys, time

SR = 44100
rng = np.random.default_rng(0)


# ======================================================================
#  Utilidades
# ======================================================================
def n_(seg):
    return max(1, int(round(seg * SR)))


def hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


_LETRAS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(txt):
    """'C#4' -> 61, 'Bb3' -> 58 (do central = C4 = 60)."""
    i, alt = 1, 0
    while txt[i] in '#b':
        alt += 1 if txt[i] == '#' else -1
        i += 1
    return 12 * (int(txt[i:]) + 1) + _LETRAS[txt[0]] + alt


def suavizar(x, tau):
    """Paso bajo de un polo (tau en segundos) que arranca en el primer valor."""
    if tau <= 0:
        return x
    a = np.exp(-1.0 / (tau * SR))
    y, _ = signal.lfilter([1 - a], [1, -a], x, axis=-1, zi=x[..., :1] * a)
    return y


def paso(x):
    """Rampa suave 0..1 (smoothstep) para x en [0, 1]."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _campana(f, fc, db, ancho):
    """Ganancia (lineal) de una joroba en dB centrada en fc, ancho en octavas."""
    return 10 ** (db / 20 * np.exp(-0.5 * (np.log2(np.maximum(f, 1.0) / fc) / ancho) ** 2))


def _pasabajos(f, fc, orden=2):
    return 1.0 / np.sqrt(1 + (f / fc) ** (2 * orden))


def _lorentz(f, F, bw):
    return 1.0 / (1 + ((f - F) / (0.5 * bw)) ** 2)


# ---------------------------------------------------------------- filtros
def _sos(tipo, f, orden=2):
    ny = SR / 2
    if tipo == 'bandpass':
        f = [max(15.0, f[0]), min(ny * 0.95, f[1])]
    else:
        f = min(ny * 0.95, max(15.0, f))
    return signal.butter(orden, f, btype=tipo, fs=SR, output='sos')


def pb(x, f, orden=2):
    return signal.sosfilt(_sos('lowpass', f, orden), x, axis=-1)


def pa(x, f, orden=2):
    return signal.sosfilt(_sos('highpass', f, orden), x, axis=-1)


def bp(x, lo, hi, orden=2):
    return signal.sosfilt(_sos('bandpass', (lo, hi), orden), x, axis=-1)


def _biquad(b, a):
    return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])


def sos_pico(f, db, q):
    A = 10 ** (db / 40)
    w = 2 * np.pi * f / SR
    al, c = np.sin(w) / (2 * q), np.cos(w)
    return _biquad([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A])


def sos_estante(f, db, alto=True, q=0.707):
    A = 10 ** (db / 40)
    w = 2 * np.pi * f / SR
    al, c = np.sin(w) / (2 * q), np.cos(w)
    r = 2 * np.sqrt(A) * al
    if alto:
        b = [A * ((A + 1) + (A - 1) * c + r), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - r)]
        a = [(A + 1) - (A - 1) * c + r, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - r]
    else:
        b = [A * ((A + 1) - (A - 1) * c + r), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - r)]
        a = [(A + 1) + (A - 1) * c + r, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - r]
    return _biquad(b, a)


def ecualizar(x, bandas):
    """bandas: ('pa', f[, orden]) ('pb', f[, orden]) ('pico', f, db, q)
    ('graves', f, db) ('agudos', f, db). Todo en una cascada de biquads."""
    sos = []
    for b in bandas:
        if b[0] == 'pa':
            sos.append(_sos('highpass', b[1], b[2] if len(b) > 2 else 2))
        elif b[0] == 'pb':
            sos.append(_sos('lowpass', b[1], b[2] if len(b) > 2 else 2))
        elif b[0] == 'pico':
            sos.append(sos_pico(b[1], b[2], b[3]))
        elif b[0] == 'graves':
            sos.append(sos_estante(b[1], b[2], alto=False))
        elif b[0] == 'agudos':
            sos.append(sos_estante(b[1], b[2], alto=True))
    if not sos:
        return x
    return signal.sosfilt(np.vstack(sos), x, axis=-1)


# ---------------------------------------------------------------- ruido
_BANCO = {}


def banda_ruido(lo, hi, largo=12.0):
    """Ruido blanco filtrado en banda, largo y cacheado: de aqui se sacan
    trozos al azar para el arco, el aliento y los soplos."""
    clave = (int(lo), int(hi))
    if clave not in _BANCO:
        r = np.random.default_rng(int(lo) * 7919 + int(hi))
        x = r.standard_normal(n_(largo))
        if lo <= 20:
            x = pb(x, hi, 2)
        elif hi >= SR * 0.45:
            x = pa(x, lo, 2)
        else:
            x = bp(x, lo, hi, 2)
        _BANCO[clave] = (x / np.std(x)).astype(np.float32)
    return _BANCO[clave]


def trozo_ruido(lo, hi, n):
    b = banda_ruido(lo, hi)
    if n >= len(b):
        return np.resize(b, n)
    i = int(rng.integers(0, len(b) - n))
    return b[i:i + n]


def ruido(n, color='blanco'):
    x = rng.standard_normal(n)
    if color == 'rosa':
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        x = signal.lfilter(b, a, x)
    elif color == 'marron':
        x = signal.lfilter([1], [1, -0.995], x)
    return x / (np.std(x) + 1e-12)


def caida(n, tau, ataque=0.002):
    """Golpe: sube en `ataque` y cae con constante tau (segundos)."""
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    a = min(n, n_(ataque))
    e[:a] *= np.linspace(0, 1, a)
    f = max(1, n // 10)
    e[-f:] *= np.linspace(1, 0, f)
    return e


# ======================================================================
#  Osciladores de tabla: cada nota tiene su propio espectro (armonicos con
#  su envolvente en Hz absolutos), limitado en banda y en varias filas de
#  brillo. Leer entre filas es como abrir o cerrar un filtro, sin aliasing.
# ======================================================================
NT = 2048
_TABLAS = {}


def tabla(timbre, m, B):
    m = int(round(m))
    clave = (timbre.__name__, m, B)
    T = _TABLAS.get(clave)
    if T is None:
        f0 = float(hz(m))
        K = int(max(1, min(NT // 2 - 2, 15000.0 / f0)))
        k = np.arange(1, K + 1, dtype=float)
        fk = k * f0
        tope = np.clip((15000.0 - fk) / 4000.0, 0.0, 1.0)
        A = np.empty((B, K))
        for j in range(B):
            a = np.asarray(timbre(k, fk, j / max(1, B - 1)), dtype=float) * tope
            A[j] = a / np.sqrt(np.sum(a ** 2) / 2 + 1e-20)
        esp = np.zeros((B, NT // 2 + 1), dtype=complex)
        esp[:, 1:K + 1] = -0.5j * NT * A
        if getattr(timbre, 'azar', False):
            # fases sueltas: un conjunto no suena en fase (menos zumbido y menos picos)
            esp[:, 1:K + 1] *= np.exp(2j * np.pi * np.random.default_rng(K).random(K))
        T = np.fft.irfft(esp, n=NT, axis=1).astype(np.float32)
        D = (np.roll(T, -1, axis=1) - T).astype(np.float32)
        T = (np.ascontiguousarray(T), np.ascontiguousarray(D))
        _TABLAS[clave] = T
    return T


_DESP = 32 - 11                     # NT = 2048 = 2 ** 11
_MASCARA = np.uint32((1 << _DESP) - 1)
_ESCALA = np.float32(1.0 / (1 << _DESP))


def leer(TD, fase, b):
    """Lee la tabla (filas de brillo y sus pendientes) con la fase en punto
    fijo de 32 bits (da la vuelta sola) y el brillo b en [0, 1]."""
    T, D = TD
    B, N = T.shape
    i = fase >> _DESP
    x = (fase & _MASCARA).astype(np.float32)
    x *= _ESCALA
    if B == 1 or np.ndim(b) == 0 or np.ptp(b) < 1e-4:
        bb = float(np.clip(np.mean(b) * (B - 1), 0, B - 1.0001)) if B > 1 else 0.0
        j = int(bb)
        f = np.float32(bb - j)
        if B > 1:
            filaT, filaD = T[j] + f * (T[j + 1] - T[j]), D[j] + f * (D[j + 1] - D[j])
        else:
            filaT, filaD = T[0], D[0]
        return filaT[i] + x * filaD[i]
    bb = np.clip(np.asarray(b, dtype=np.float32) * (B - 1), 0, B - 1.0001)
    j = bb.astype(np.uint32)
    bf = bb - j
    idx = i + j * np.uint32(N)
    Tf, Df = T.ravel(), D.ravel()
    v0 = Tf[idx] + x * Df[idx]
    idx += np.uint32(N)
    v1 = Tf[idx] + x * Df[idx]
    v1 -= v0
    v1 *= bf
    return v0 + v1


def _nombrar(f, nombre):
    f.__name__ = nombre
    return f


# ---------------------------------------------------------------- timbres
def t_violin(k, fk, b):
    a = 1.0 / k * _pasabajos(fk, 1700 * 3.6 ** b, 2)
    return a * _campana(fk, 290, 2.5, 0.35) * _campana(fk, 1250, -3.0, 0.45) * _campana(fk, 2900, 3.5, 0.45)


def t_viola(k, fk, b):
    a = 1.0 / k * _pasabajos(fk, 1300 * 3.4 ** b, 2)
    return a * _campana(fk, 240, 2.0, 0.4) * _campana(fk, 900, -2.0, 0.5) * _campana(fk, 2200, 3.0, 0.5)


def t_chelo(k, fk, b):
    a = 1.0 / k * _pasabajos(fk, 900 * 4.0 ** b, 2)
    return a * _campana(fk, 180, 2.0, 0.5) * _campana(fk, 380, -2.5, 0.5) * _campana(fk, 1300, 2.5, 0.6)


def t_contrabajo(k, fk, b):
    a = 1.0 / k * _pasabajos(fk, 550 * 3.6 ** b, 2)
    return a * _campana(fk, 90, 2.0, 0.5) * _campana(fk, 330, -3.0, 0.5) * _campana(fk, 900, 2.0, 0.6)


def t_trompa(k, fk, b):
    a = k ** -(2.2 - 1.35 * b) * _pasabajos(fk, 650 * 5.0 ** b, 2)
    return a * _campana(fk, 450, 3.0, 0.6)


def t_trombon(k, fk, b):
    a = k ** -(2.0 - 1.4 * b) * _pasabajos(fk, 480 * 9.0 ** b, 2)
    return a * _campana(fk, 1100, 4.0 * b, 0.6)


def t_tuba(k, fk, b):
    a = k ** -(2.4 - 1.2 * b) * _pasabajos(fk, 280 * 6.0 ** b, 2)
    return a * _campana(fk, 250, 2.0, 0.6)


def t_trompeta(k, fk, b):
    a = k ** -(1.7 - 1.2 * b) * _pasabajos(fk, 1100 * 4.5 ** b, 2)
    return a * _campana(fk, 1300, 3.0, 0.5) * _campana(fk, 2600, 2.0 * b, 0.5)


def t_flauta(k, fk, b):
    a = (0.13 + 0.3 * b) ** (k - 1.0)
    return a * _pasabajos(fk, 5000, 2)


def t_ocarina(k, fk, b):
    return np.where(k == 1, 1.0, np.where(k % 2 == 1, 0.05 + 0.09 * b, 0.025) / (k - 0.5) ** 0.8)


def t_quena(k, fk, b):
    """Flauta de pan (tubo cerrado): impares fuertes, pares casi nada."""
    a = np.where(k % 2 == 1, (0.22 + 0.25 * b) ** ((k - 1) / 2.0), 0.035 * (0.5 + b) / k)
    return a * _pasabajos(fk, 5500, 2)


def t_sub(k, fk, b):
    return np.where(k == 1, 1.0, np.where(k == 2, 0.12 * b, 0.0))


# formantes de coro (Hz, dB, ancho de banda): soprano, alto, tenor, bajo
FORMANTES = {
    ('S', 'a'): ((800, 1150, 2900, 3900, 4950), (0, -6, -32, -20, -50), (80, 90, 120, 130, 140)),
    ('S', 'o'): ((450, 800, 2830, 3800, 4950), (0, -11, -22, -22, -50), (70, 80, 100, 130, 135)),
    ('S', 'u'): ((325, 700, 2700, 3800, 4950), (0, -16, -35, -40, -60), (50, 60, 170, 180, 200)),
    ('A', 'a'): ((800, 1150, 2800, 3500, 4950), (0, -4, -20, -36, -60), (80, 90, 120, 130, 140)),
    ('A', 'o'): ((450, 800, 2830, 3500, 4950), (0, -9, -16, -28, -55), (70, 80, 100, 130, 135)),
    ('A', 'u'): ((325, 700, 2530, 3500, 4950), (0, -12, -30, -40, -64), (50, 60, 170, 180, 200)),
    ('T', 'a'): ((650, 1080, 2650, 2900, 3250), (0, -6, -7, -8, -22), (80, 90, 120, 130, 140)),
    ('T', 'o'): ((400, 800, 2600, 2800, 3000), (0, -10, -12, -12, -26), (40, 80, 100, 120, 120)),
    ('T', 'u'): ((350, 600, 2700, 2900, 3300), (0, -20, -17, -14, -26), (40, 60, 100, 120, 120)),
    ('B', 'a'): ((600, 1040, 2250, 2450, 2750), (0, -7, -9, -9, -20), (60, 70, 110, 120, 130)),
    ('B', 'o'): ((400, 750, 2400, 2600, 2900), (0, -11, -21, -20, -40), (40, 80, 100, 120, 120)),
    ('B', 'u'): ((350, 600, 2400, 2675, 2950), (0, -20, -32, -28, -36), (40, 80, 100, 120, 120)),
}


def tipo_voz(m):
    return 'S' if m >= 67 else 'A' if m >= 60 else 'T' if m >= 52 else 'B'


def t_coro(voz, v1, v2, suave=1.0, tilt=1.25):
    """Coro: fuente glotal por formantes; el eje de brillo es el paso de la
    vocal v1 a la v2 (formantes interpolados). `suave` baja los formantes
    altos (coro piano, sin el brillo del cantante solista)."""
    F1, G1, W1 = FORMANTES[(voz, v1)]
    F2, G2, W2 = FORMANTES[(voz, v2)]

    def f(k, fk, b):
        f0 = fk[0]
        H = np.full_like(fk, 0.004)
        for i in range(5):
            F = np.exp((1 - b) * np.log(F1[i]) + b * np.log(F2[i]))
            G = (1 - b) * G1[i] + b * G2[i] - (6.0 * suave if i >= 2 else 0.0)
            W = (1 - b) * W1[i] + b * W2[i]
            if i == 0:
                F = max(F, 1.08 * f0)
            W = max(W * 1.35, 0.55 * f0)
            H += 10 ** (G / 20) * _lorentz(fk, F, W)
        return H * k ** -tilt * _pasabajos(fk, 6500, 2)
    f.azar = True
    return _nombrar(f, 'coro_%s_%s%s_%d_%d' % (voz, v1, v2, int(suave * 10), int(tilt * 100)))


for _t in (t_violin, t_viola, t_chelo, t_contrabajo):
    _t.azar = True


def t_dron(k, fk, b):
    """Dron de tubo con labios que zumban: la boca mueve un formante (wah)."""
    F = 330 * 4.5 ** b
    H = 0.22 + 2.0 * _lorentz(fk, F, 160 + 120 * b) + 0.8 * _lorentz(fk, 2.6 * F, 380) + 0.5 * _lorentz(fk, 1650, 500)
    return H * k ** -0.55 * _pasabajos(fk, 2600, 2)


# ======================================================================
#  Notas y frases
# ======================================================================
class Nota:
    __slots__ = ('t', 'd', 'm', 'v', 'art', 'lig', 'frase', 'vocal', 'bend', 'trino', 'pan')

    def __init__(self, t, d, m, v=0.7, art='leg', lig=True, frase=None, vocal=0.0, bend=0.0, trino=0.0, pan=0.0):
        self.t, self.d, self.m, self.v, self.art, self.lig = t, d, m, v, art, lig
        self.frase, self.vocal, self.bend, self.trino, self.pan = frase, vocal, bend, trino, pan


def _forma(art, t, d):
    """Como evoluciona la intensidad dentro de una nota."""
    tc = np.minimum(t, d)
    if art == 'marc':
        return 0.6 + 0.4 * np.exp(-tc / 0.13)
    if art == 'acc':
        return 0.8 + 0.2 * np.exp(-tc / 0.1)
    if art == 'fp':
        return 0.3 + 0.7 * np.exp(-tc / 0.09)
    if art == 'cresc':
        return 0.2 + 0.8 * (tc / d) ** 1.7
    if art == 'dim':
        return 1.0 - 0.75 * (tc / d) ** 0.9
    if art == 'swell':
        return 0.3 + 0.7 * np.sin(np.pi * tc / d) ** 1.6
    if art == 'fpc':
        return np.minimum(1.0, 0.25 + 0.75 * (tc / d) ** 2.2 + 0.55 * np.exp(-tc / 0.07))
    return np.ones_like(t)


ATAQUES = {'marc': 0.018, 'acc': 0.03, 'fp': 0.018, 'fpc': 0.02, 'spic': 0.003, 'stac': 0.006}


def leer_trozos(TD, fase, b, bloque=4096):
    """Como leer(), pero donde el brillo no se mueve usa una sola fila."""
    n = fase.shape[-1]
    if np.ndim(b) == 0 or n <= bloque:
        return leer(TD, fase, b)
    out = np.empty(fase.shape, dtype=np.float32)
    for i in range(0, n, bloque):
        bc = b[i:i + bloque]
        if bc.max() - bc.min() < 2e-3:
            out[..., i:i + bloque] = leer(TD, fase[..., i:i + bloque], float(bc.mean()))
        else:
            out[..., i:i + bloque] = leer(TD, fase[..., i:i + bloque], bc)
    return out


def _frase(notas, P):
    """Una frase continua (o una sola nota): curva de altura con portamento,
    curva de intensidad, vibrato que entra tarde, brillo que sigue a la
    intensidad, y V voces un poco desafinadas que se reparten el estereo.
    Las curvas de altura van a ritmo de control (cada K muestras)."""
    V = P['V']
    n0, ult = notas[0], notas[-1]
    unica = len(notas) == 1
    corta = n0.art in ('spic', 'stac')
    if corta:
        suena = min(n0.d, 0.2) if n0.art == 'spic' else min(max(0.09, 0.55 * n0.d), 0.35)
        soltar = 0.04 if n0.art == 'spic' else 0.07
    else:
        suena = ult.d
        soltar = P['soltar']
    offs = (rng.uniform(0, P.get('disp', 0.0), V) * SR).astype(int) if V > 1 else np.zeros(1, dtype=int)
    omax = int(offs.max())
    t_ini = n0.t
    fin = ult.t + suena - t_ini
    n = n_(fin + soltar) + 1 + omax
    S = [0] + [min(n - 1, n_(nt.t - t_ini)) for nt in notas[1:]]
    E = S[1:] + [n]
    K = 32
    nc = -(-n // K) + 1
    tc = np.arange(nc) * (K / SR)
    Sc = [-(-x // K) for x in S]
    Ec = Sc[1:] + [nc]

    # ---- altura (semitonos) y adornos (cents), a ritmo de control
    m = np.full(nc, float(n0.m))
    cents = np.zeros(nc)
    for i, nt in enumerate(notas):
        s = S[i] / SR
        if i > 0 and nt.m != notas[i - 1].m:
            g = P['glide'] if nt.lig else 0.014
            m += (nt.m - notas[i - 1].m) * paso((tc - s + 0.35 * g) / g)
        if nt.bend:
            cents -= nt.bend * np.exp(-np.maximum(0, tc - s) / 0.07) * (tc >= s)
        if (i == 0 or not nt.lig) and P.get('scoop'):
            sc, tau = P['scoop']
            cents -= sc * (0.6 + 0.6 * nt.v) * np.exp(-np.maximum(0, tc - s) / tau) * (tc >= s)
        if nt.trino:
            a, z = Sc[i], Ec[i]
            ts = tc[a:z] - s
            w = 0.5 + 0.5 * np.tanh(4 * np.sin(2 * np.pi * 7.5 * ts - np.pi / 2))
            m[a:z] += nt.trino * w * paso((ts - 0.07) / 0.05) * paso((nt.d - ts - 0.04) / 0.05)

    # ---- vibrato que entra tarde en cada nota
    vr, vd, vdel, vsub = P['vib']
    venv = np.zeros(nc)
    if vd > 0 and not corta:
        for i in range(len(notas)):
            a, z = Sc[i], Ec[i]
            venv[a:z] = paso((tc[a:z] - S[i] / SR - vdel) / vsub)
        if not unica:
            venv = suavizar(venv, 0.06 / K)

    # ---- intensidad (a ritmo de audio)
    tt = np.arange(n) / SR
    if corta:
        tau = 0.055 if n0.art == 'spic' else 0.11
        nivel = n0.v * np.exp(-tt / tau) * (0.75 + 0.25 * np.exp(-tt / 0.02))
    else:
        nivel = np.zeros(n)
        for i, nt in enumerate(notas):
            a, z = S[i], E[i]
            if nt.art in ('leg', 'trem'):
                nivel[a:z] = nt.v
            else:
                nivel[a:z] = nt.v * _forma(nt.art, tt[a:z] - tt[a], nt.d)
        if not unica:
            nivel = suavizar(nivel, 0.02)
            for i, nt in enumerate(notas[1:], 1):
                if not nt.lig:
                    a, z = max(0, S[i] - n_(0.06)), min(n, S[i] + n_(0.03))
                    nivel[a:z] *= 1 - 0.55 * np.exp(-((tt[a:z] - tt[S[i]] + 0.018) / 0.014) ** 2)
    at = ATAQUES.get(n0.art, P['ataque'])
    k = min(n, n_(at) + 1)
    nivel[:k] *= paso(tt[:k] / at) ** 0.8
    k = min(n, n_(fin))
    r = np.clip((tt[k:] - fin) / soltar, 0, 1)
    nivel[k:] *= np.exp(-4.0 * r) * (1 - r)

    # ---- brillo (o vocal)
    if P.get('eje') == 'vocal':
        bri = np.zeros(n)
        for i, nt in enumerate(notas):
            bri[S[i]:E[i]] = nt.vocal
        if not unica:
            bri = suavizar(bri, 0.08)
    else:
        bri = P['b0'] + P['bk'] * (nivel if P['bexp'] == 1.0 else np.abs(nivel) ** P['bexp'])
        if P.get('bt'):
            for i, nt in enumerate(notas):
                if i == 0 or not nt.lig:
                    a, z = S[i], min(n, S[i] + n_(0.4))
                    ts = tt[a:z] - tt[a]
                    bri[a:z] += P['bt'] * nt.v * np.exp(-ts / 0.06) * paso(ts / 0.012)
        bri = np.clip(bri, 0, 1)
    bri = bri.astype(np.float32)

    # ---- voces del conjunto
    det = rng.normal(0, P['det'], V) if V > 1 else np.zeros(1)
    det -= det.mean()
    rates = vr * rng.uniform(0.92, 1.08, V)
    fases = rng.uniform(0, 2 * np.pi, V)
    dr_f = rng.uniform(0.12, 0.5, (V, 2))
    dr_p = rng.uniform(0, 2 * np.pi, (V, 2))
    deriva = P['det'] * 0.35 * (np.sin(2 * np.pi * dr_f[:, :1] * tc + dr_p[:, :1]) + np.sin(2 * np.pi * dr_f[:, 1:] * tc + dr_p[:, 1:]))
    cv = det[:, None] + cents[None, :] + vd * venv[None, :] * np.sin(2 * np.pi * rates[:, None] * tc + fases[:, None]) + deriva
    fc = hz(m)[None, :] * 2.0 ** (cv / 1200.0) / SR
    fase = np.repeat((fc[:, :-1] * 4294967296.0).astype(np.uint32), K, axis=1)[:, :n]
    fase[:, 0] = rng.integers(0, 2 ** 32, V, dtype=np.uint32)
    np.cumsum(fase, axis=1, dtype=np.uint32, out=fase)
    tm = P['timbre']
    if unica or corta:
        y = leer_trozos(tabla(tm, n0.m, P['B']), fase, bri)
    else:
        y = np.zeros((V, n), dtype=np.float32)
        X = n_(0.012)
        for i, nt in enumerate(notas):
            a = max(0, S[i] - X // 2) if i > 0 else 0
            z = min(n, E[i] + X // 2) if i < len(notas) - 1 else n
            if z <= a:
                continue
            w = np.ones(z - a, dtype=np.float32)
            if i > 0:
                q = min(X, z - a)
                w[:q] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(q) / X)
            if i < len(notas) - 1:
                q = min(X, z - a)
                w[-q:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(X - q, X) / X)
            y[:, a:z] += w * leer_trozos(tabla(tm, nt.m, P['B']), fase[:, a:z], bri[a:z])

    # ---- vida de cada voz (y tremolo), entrada escalonada y estereo
    brillo_v = rng.uniform(0.82, 1.0, V)
    sh_f = rng.uniform(0.2, 0.9, V)
    sh_p = rng.uniform(0, 2 * np.pi, V)
    vida = brillo_v[:, None] * (1 + 0.06 * np.sin(2 * np.pi * sh_f[:, None] * tc + sh_p[:, None]))
    if n0.art == 'trem':
        tr = rng.uniform(*P.get('trem', (12.5, 16.5)), V)
        golpes = 0.5 + 0.5 * np.cos(2 * np.pi * tr[:, None] * tc + rng.uniform(0, 6.3, (V, 1)))
        vida = (vida * (0.35 + 0.65 * golpes ** 1.6)).astype(np.float32)
        fr = (np.arange(K, dtype=np.float32) / K)[None, None, :]
        g = (vida[:, :-1, None] + (vida[:, 1:] - vida[:, :-1])[:, :, None] * fr).reshape(V, -1)[:, :n]
    else:
        g = np.repeat(vida[:, :-1].astype(np.float32), K, axis=1)[:, :n]
    nivel_p = np.concatenate([np.zeros(omax, dtype=np.float32), (nivel / np.sqrt(V)).astype(np.float32)])
    for v in range(V):
        g[v] *= nivel_p[omax - offs[v]:omax - offs[v] + n]
    y *= g
    pans = P['pan'] + n0.pan + P['ancho'] * (np.linspace(-1, 1, V) if V > 1 else np.zeros(1))
    th = (np.clip(rng.permutation(pans), -1, 1) + 1) * np.pi / 4
    out = np.stack([np.cos(th), np.sin(th)]).astype(np.float32) @ y

    # ---- aliento, arco, soplos (al centro de la seccion)
    if P.get('ruido'):
        extra = np.zeros(n)
        for lo, hi, lev, modo in P['ruido']:
            rr = trozo_ruido(lo, hi, n)
            if modo == 'nivel':
                extra += lev * rr * nivel
            else:
                e = np.zeros(n)
                for i, nt in enumerate(notas):
                    if i == 0 or not nt.lig:
                        a, z = S[i], min(n, S[i] + n_(0.25))
                        ts = tt[a:z] - tt[a]
                        e[a:z] += nt.v * np.exp(-ts / 0.035) * paso(ts / 0.004)
                extra += lev * rr * e
        thc = (np.clip(P['pan'] + n0.pan, -1, 1) + 1) * np.pi / 4
        out[0] += (extra * np.cos(thc)).astype(np.float32)
        out[1] += (extra * np.sin(thc)).astype(np.float32)
    return out, t_ini


def poner(bus, x, t0, L):
    """Suma x (2, n) en el bus desde t0 (s). Lo que cae antes del cero da
    la vuelta al final del bucle."""
    i = int(round(t0 * SR))
    if x.ndim == 1:
        x = np.vstack([x, x])
    if i < 0:
        k = min(-i, x.shape[1])
        bus[:, L - k:L] += x[:, :k]
        x = x[:, k:]
        i = 0
    j = min(bus.shape[1], i + x.shape[1])
    if j > i:
        bus[:, i:j] += x[:, :j - i]


def tocar(notas, P, bus, L):
    """Humaniza, agrupa en frases (instrumentos monofonicos ligados) y suma
    todas las notas en el bus."""
    grupos = {}
    for nt in notas:
        nt.t += rng.normal(0, P.get('hum_t', 0.006))
        nt.v = float(np.clip(nt.v * (1 + rng.normal(0, P.get('hum_v', 0.04))), 0.02, 1.2))
        clave = nt.frase if (P.get('mono') and nt.frase is not None and nt.art not in ('spic', 'stac', 'trem')) else id(nt)
        grupos.setdefault(clave, []).append(nt)
    for g in grupos.values():
        g.sort(key=lambda q: q.t)
        out, t0 = _frase(g, P)
        poner(bus, out * P.get('gan', 1.0), t0, L)


# ======================================================================
#  Pulsados, laminas y campanas (cada nota se cachea: los arpegios repiten)
# ======================================================================
_CACHE = {}


def _semilla(clave):
    import zlib
    return zlib.crc32(repr(clave).encode())


def cacheado(fn):
    """Cada golpe/nota se sintetiza una vez por (parametros, variante) con su
    propia semilla: el resultado no depende del orden en que se pide."""
    def envoltura(*args, **kw):
        clave = (fn.__name__, args, tuple(sorted(kw.items())))
        x = _CACHE.get(clave)
        if x is None:
            global rng
            guardado = rng
            rng = np.random.default_rng(_semilla(clave))
            try:
                x = np.asarray(fn(*args, **kw), dtype=np.float32)
            finally:
                rng = guardado
            _CACHE[clave] = x
        return x
    envoltura.__name__ = fn.__name__
    return envoltura


@cacheado
def arpa(m, fuerza=2, variante=0):
    """Arpa por Karplus-Strong: la cuerda es un retardo que en cada vuelta
    pierde un poco y se oscurece. El periodo es entero y luego se reafina
    remuestreando, asi afina exacto en todo el registro."""
    f = float(hz(m))
    P = int(np.floor(SR / f - 0.5))
    fg = SR / (P + 0.5)
    t60 = float(np.clip(7.5 * (110.0 / f) ** 0.55, 1.2, 8.0))
    N = n_(min(0.85 * t60, 6.5))
    R = 10 ** (-3.0 / (t60 * fg))
    exc = rng.standard_normal(P)
    a = np.exp(-2 * np.pi * (900 + 1300 * fuerza) / SR)
    exc = signal.lfilter([1 - a], [1, -a], signal.lfilter([1 - a], [1, -a], exc))
    # pulsada lejos del puente: se apagan los armonicos multiplos de 1/0.3
    q = max(1, int(round(0.3 * P)))
    exc = exc - 0.6 * np.roll(exc, q)
    exc -= exc.mean()
    y = np.zeros(N + 1)
    y[1:P + 1] = exc[:min(P, N)]
    s = P + 1
    while s < N + 1:
        e = min(s + P, N + 1)
        y[s:e] = R * (0.5 * y[s - P:e - P] + 0.5 * y[s - P - 1:e - P - 1])
        s = e
    y = y[1:]
    y = np.interp(np.arange(N) * (f / fg), np.arange(N), y)
    dedo = pb(rng.standard_normal(n_(0.01)), 1200) * caida(n_(0.01), 0.0025, 0.0005) * 0.15
    y[:len(dedo)] += dedo * np.std(y[:P * 4])
    a = n_(0.0008)
    y[:a] *= np.linspace(0, 1, a)
    fin = n_(0.3)
    y[-fin:] *= np.linspace(1, 0, fin) ** 2
    return pa(y / (np.max(np.abs(y)) + 1e-9), 55)


@cacheado
def marimba(m, fuerza=2, variante=0):
    """Lamina de madera con resonador: el fundamental largo, el cuarto
    armonico (afinado 1:4) y el decimo, que se apagan muy rapido."""
    f = float(hz(m))
    tau = float(np.clip(0.75 * (220.0 / f) ** 0.6, 0.18, 1.3))
    N = n_(tau * 5)
    t = np.arange(N) / SR
    h = 0.25 + 0.25 * fuerza
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
         + h * 0.6 * np.sin(2 * np.pi * 3.93 * f * t + 1.0) * np.exp(-t / 0.07)
         + h * 0.25 * np.sin(2 * np.pi * 9.2 * f * t + 2.0) * np.exp(-t / 0.025) * (9.2 * f < 15000))
    maza = pb(rng.standard_normal(N), 1500 + 1500 * fuerza) * np.exp(-t / 0.004) * 0.25 * h
    y = (y + maza) * caida(N, 10.0, 0.0012)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def tronco(m, fuerza=2, variante=0):
    """Tambor de tronco (teponaztli): una lengueta de madera dura en un tronco
    hueco. Grave, seco, con el tono que cae un pelo al golpear."""
    f = float(hz(m))
    N = n_(1.4)
    t = np.arange(N) / SR
    caer = 1 + 0.025 * np.exp(-t / 0.03)
    ph = 2 * np.pi * f * np.cumsum(caer) / SR
    y = (np.sin(ph) * np.exp(-t / 0.3) + 0.3 * np.sin(2.03 * ph + 0.5) * np.exp(-t / 0.11)
         + 0.16 * np.sin(3.12 * ph + 1.1) * np.exp(-t / 0.055) + 0.08 * np.sin(4.65 * ph) * np.exp(-t / 0.03))
    hueco = resonar_bp(rng.standard_normal(N), f * 0.5 + 40, 3.0) * np.exp(-t / 0.05) * 0.4
    maza = pb(rng.standard_normal(N), 900 + 600 * fuerza) * np.exp(-t / 0.006) * 0.5
    y = (y + hueco + maza) * caida(N, 10.0, 0.001)
    return pb(y / (np.max(np.abs(y)) + 1e-9), 4000)


def resonar_bp(x, f, q):
    b, a = signal.iirpeak(min(f, SR * 0.45), q, fs=SR)
    return signal.lfilter(b, a, x)


@cacheado
def cristal(m, fuerza=2, variante=0):
    """Campana de cristal (FM con razon inarmonica 3,5): brillo que se apaga
    antes que el cuerpo, como un vaso bajo el agua."""
    f = float(hz(m))
    N = n_(3.6)
    t = np.arange(N) / SR
    ind = (0.6 + 0.5 * fuerza) * np.exp(-t / 0.3) + 0.2
    y = np.sin(2 * np.pi * f * t + ind * np.sin(2 * np.pi * 3.5 * f * t))
    y += 0.35 * np.sin(2 * np.pi * 2.756 * f * t + 0.7) * np.exp(-t / 0.5)
    y += 0.2 * np.sin(2 * np.pi * 1.0035 * f * t + 1.9)
    y *= caida(N, 1.5, 0.003)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def celesta(m, fuerza=2, variante=0):
    """Lamina metalica (celesta/glockenspiel suave): parciales de barra."""
    f = float(hz(m))
    N = n_(2.6)
    t = np.arange(N) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
    y += 0.25 * np.sin(2 * np.pi * 2.756 * f * t + 0.4) * np.exp(-t / 0.25) * (2.756 * f < 15000)
    y += 0.1 * np.sin(2 * np.pi * 5.404 * f * t + 0.9) * np.exp(-t / 0.08) * (5.404 * f < 15000)
    y *= caida(N, 10.0, 0.0015)
    return y / (np.max(np.abs(y)) + 1e-9)


# ======================================================================
#  Percusion
# ======================================================================
@cacheado
def timbal(m, fuerza=2, variante=0):
    """Timbal: los modos de la membrana cargada por el aire (1, 1,5, 1,98,
    2,44, 2,94) con el (0,1) sordo que da el golpe; arranca un pelo alto."""
    f = float(hz(m))
    N = n_(3.2)
    t = np.arange(N) / SR
    sube = 1 + (0.012 + 0.012 * fuerza) * np.exp(-t / 0.06)
    ph = 2 * np.pi * f * np.cumsum(sube) / SR
    y = np.zeros(N)
    for r, a, tau in ((1.0, 1.0, 1.5), (1.5, 0.42, 0.9), (1.98, 0.28, 0.65), (2.44, 0.16, 0.45), (2.94, 0.1, 0.3), (0.58, 0.55, 0.11)):
        y += a * np.sin(r * ph + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    maza = pb(rng.standard_normal(N), 500 + 600 * fuerza) * np.exp(-t / 0.012) * (0.25 + 0.12 * fuerza)
    y = (y + maza) * caida(N, 10.0, 0.0015)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def tambor(f_base, tau, fuerza=2, variante=0, caida_f=0.9, t_caida=0.03, piel=(90, 800, 0.5, 0.06),
           palo=(800, 3500, 0.3, 0.008), modo2=(1.58, 0.35, 0.14), dur=None):
    """Tambor de membrana grande (taiko, timbal grave, tambor de marco): el
    tono que cae mientras la piel se destensa, un segundo modo, el ruido de
    la piel y el chasquido del palo o la mano."""
    N = n_(dur or min(3.0, tau * 5 + 0.1))
    t = np.arange(N) / SR
    f = f_base * (1 + caida_f * (0.6 + 0.2 * fuerza) * np.exp(-t / t_caida))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / tau)
    if modo2:
        y += modo2[1] * np.sin(modo2[0] * ph + 0.4) * np.exp(-t / modo2[2])
    lo, hi, a, tt = piel
    y += bp(rng.standard_normal(N), lo, hi) * np.exp(-t / tt) * a
    lo, hi, a, tt = palo
    y += bp(rng.standard_normal(N), lo, hi) * np.exp(-t / tt) * a * (0.5 + 0.25 * fuerza)
    y *= caida(N, 10.0, 0.0012)
    return y / (np.max(np.abs(y)) + 1e-9)


def taiko(fuerza=2, variante=0, grave=1.0):
    return tambor(56.0 * grave, 0.42, fuerza, variante, 0.9, 0.03, (80, 700, 0.55, 0.07), (700, 3000, 0.28, 0.008), (1.58, 0.32, 0.14))


def tom(f_base=110.0, fuerza=2, variante=0):
    return tambor(f_base, 0.24, fuerza, variante, 0.65, 0.025, (150, 1500, 0.45, 0.05), (1200, 5000, 0.3, 0.006), (1.5, 0.3, 0.09))


def marco(fuerza=2, variante=0, slap=False):
    if slap:
        return tambor(175.0, 0.09, fuerza, variante, 0.4, 0.015, (400, 4000, 0.9, 0.035), (2000, 7000, 0.4, 0.004), (1.6, 0.4, 0.05))
    return tambor(82.0, 0.3, fuerza, variante, 0.5, 0.025, (160, 1800, 0.6, 0.055), (1500, 5000, 0.2, 0.005), (1.55, 0.3, 0.1))


@cacheado
def caja(fuerza=2, variante=0):
    """Caja militar grande: dos modos del parche, la bordonera (ruido que
    vibra con el golpe) y el golpe del palillo."""
    N = n_(0.8)
    t = np.arange(N) / SR
    y = np.sin(2 * np.pi * 182 * t * (1 + 0.04 * np.exp(-t / 0.02))) * np.exp(-t / 0.07)
    y += 0.55 * np.sin(2 * np.pi * 297 * t + 0.6) * np.exp(-t / 0.045)
    y += bp(rng.standard_normal(N), 1600, 8500) * np.exp(-t / 0.15) * (0.55 + 0.15 * fuerza)
    y += bp(rng.standard_normal(N), 300, 3000) * np.exp(-t / 0.012) * 0.7
    y *= caida(N, 10.0, 0.0008)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def palo_madera(f=1400.0, fuerza=2, variante=0):
    """Palo contra el aro o claves de madera: dos modos y un chasquido."""
    N = n_(0.25)
    t = np.arange(N) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.035) + 0.4 * np.sin(2 * np.pi * 2.7 * f * t) * np.exp(-t / 0.012)
    y += bp(rng.standard_normal(N), 1500, 7000) * np.exp(-t / 0.003) * 0.8
    y *= caida(N, 10.0, 0.0005)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def sonaja(fuerza=2, variante=0, largo=0.12, brillo=1.0):
    """Sonaja de semillas: cientos de semillas que chocan, cada una un clic.
    Se agrupan en una nube que crece y se apaga con el golpe de muneca."""
    N = n_(largo + 0.08)
    t = np.arange(N) / SR
    env = paso(t / (0.35 * largo)) * np.exp(-np.maximum(0, t - 0.35 * largo) / (0.3 * largo))
    clics = (rng.random(N) < 0.18 * env) * rng.uniform(0.2, 1.0, N)
    y = bp(clics, 2800 * brillo, min(14000, 9500 * brillo), 2) + 0.25 * bp(rng.standard_normal(N), 3000, 10000) * env
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def platillo(fuerza=2, variante=0, dur=3.2):
    """Platillo suspendido: ruido metalico (muchas resonancias apretadas)
    que se apaga despacio, con el golpe al principio."""
    N = n_(dur)
    t = np.arange(N) / SR
    x = rng.standard_normal(N)
    met = sum(resonar_bp(x, f, 25) for f in rng.uniform(2500, 9000, 9)) * 0.25
    y = (bp(x, 3000, 11000) * 0.8 + met) * (np.exp(-t / (0.35 * dur)) + 0.6 * np.exp(-t / 0.06))
    y += pb(x, 1200) * np.exp(-t / 0.03) * 0.3
    y *= caida(N, 10.0, 0.002)
    return y / (np.max(np.abs(y)) + 1e-9)


def redoble_platillo(dur, curva=2.5):
    """Platillo con mazas que crece hasta el golpe (el remolino de antes del tutti)."""
    N = n_(dur)
    t = np.arange(N) / SR
    x = rng.standard_normal(N)
    y = bp(x, 2500, 9000) + 0.3 * bp(x, 600, 2500)
    e = (t / dur) ** curva * (1 + 0.15 * np.sin(2 * np.pi * 9 * t))
    fin = n_(0.02)
    e[-fin:] *= np.linspace(1, 0, fin)
    return y * e / (np.max(np.abs(y * e)) + 1e-9)


def subida(dur, f0=300.0, f1=6000.0, curva=2.0):
    """Barrido de ruido que sube hasta el golpe (sin filtro movil: un banco
    de bandas que se cruzan)."""
    N = n_(dur)
    t = np.arange(N) / SR
    x = rng.standard_normal(N)
    centro = f0 * (f1 / f0) ** ((t / dur) ** curva)
    bandas = np.geomspace(f0, f1, 7)
    y = np.zeros(N)
    for i, fc in enumerate(bandas):
        w = np.exp(-0.5 * (np.log2(centro / fc) / 0.45) ** 2)
        y += bp(x, fc / 1.5, fc * 1.5) * w
    e = (t / dur) ** 1.6
    fin = n_(0.015)
    e[-fin:] *= np.linspace(1, 0, fin)
    return y * e / (np.max(np.abs(y * e)) + 1e-9)


# ======================================================================
#  Fuerzas de la naturaleza
# ======================================================================
def boom(f0=55, f1=26, tau=0.8, dur=None):
    """Subgrave que cae: el peso de un golpe enorme."""
    dur = dur or tau * 5
    N = n_(dur)
    t = np.arange(N) / SR
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.35))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + 0.2 * np.sin(2 * ph)) * caida(N, tau, 0.004)


@cacheado
def trueno(fuerza=2, variante=0, dur=4.5):
    """Trueno cercano: el chasquido de la descarga (clics que se amontonan),
    el subgrave que cae y el retumbo que rueda y se aleja."""
    N = n_(dur)
    t = np.arange(N) / SR
    cr = np.zeros(N)
    k = n_(0.35)
    golpes = (rng.random(k) < 0.03 * np.exp(-np.arange(k) / SR / 0.1)) * rng.uniform(0.2, 1, k)
    cr[:k] = golpes
    chasquido = pa(cr, 900) + 0.5 * bp(rng.standard_normal(N), 500, 6000) * np.exp(-t / 0.06)
    retumbo = pb(ruido(N, 'marron'), 160) * (np.exp(-t / 1.4)) * (0.7 + 0.6 * np.abs(np.sin(2 * np.pi * 1.3 * t + rng.uniform(0, 3))))
    medio = bp(ruido(N, 'rosa'), 150, 900) * np.exp(-t / 0.5) * 0.5
    y = pico_(chasquido, 0.55) + pico_(retumbo, 0.9) + pico_(medio, 0.4) + pico_(boom(52, 24, 0.9, dur), 0.9)
    return y * caida(N, 10.0, 0.003)


@cacheado
def terremoto(fuerza=2, variante=0, dur=4.0):
    """Golpe de piedra que hace temblar el suelo: subgrave, retumbo grave,
    el crujido de la roca y la gravilla que cae despues."""
    N = n_(dur)
    t = np.arange(N) / SR
    sub_ = boom(46, 21, 0.75, dur)
    retumbo = pb(ruido(N, 'marron'), 120) * np.exp(-t / 1.2) * (1 + 0.5 * np.sin(2 * np.pi * 7 * t) * np.exp(-t / 0.8))
    roca = bp(rng.standard_normal(N), 250, 2500) * np.exp(-t / 0.035)
    grava = np.zeros(N)
    for _ in range(40):
        s = n_(0.05 + rng.uniform(0, 1.6) ** 1.5)
        c = bp(rng.standard_normal(n_(0.012)), 1200, 6000) * np.exp(-np.arange(n_(0.012)) / SR / 0.002)
        grava[s:s + len(c)] += c[:max(0, N - s)] * rng.uniform(0.1, 0.5) * np.exp(-s / SR / 0.8)
    y = pico_(sub_, 1.0) + pico_(retumbo, 0.7) + pico_(roca, 0.5) + pico_(grava, 0.22)
    return y * caida(N, 10.0, 0.002)


def pico_(x, a=1.0):
    m = np.max(np.abs(x))
    return x * (a / m) if m > 0 else x


@cacheado
def cadena(fuerza=2, variante=0, eslabones=5):
    """Cadena oxidada: eslabones de metal (modos inarmonicos) en racimo."""
    N = n_(1.3)
    y = np.zeros(N)
    t0 = 0.0
    for i in range(eslabones):
        f = rng.uniform(500, 1300)
        n = n_(0.6)
        t = np.arange(n) / SR
        e = np.zeros(n)
        for r, a in ((1, 1), (1.47, 0.7), (2.09, 0.45), (2.56, 0.35), (3.9, 0.2)):
            e += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6)) * np.exp(-t / (rng.uniform(0.05, 0.12) / r ** 0.5))
        e += bp(rng.standard_normal(n), 2000, 9000) * np.exp(-t / 0.002) * 0.6
        s = n_(t0)
        y[s:s + n] += e[:max(0, N - s)] * rng.uniform(0.4, 1.0) * (0.85 ** i)
        t0 += rng.uniform(0.02, 0.09)
    y *= caida(N, 10.0, 0.0005)
    return pb(y / (np.max(np.abs(y)) + 1e-9), 6000)


def ballena(dur, puntos, brillo=650.0):
    """Canto de ballena: un tono que se desliza entre alturas (puntos =
    (t relativo, Hz)), con pocos armonicos alrededor de `brillo`."""
    N = n_(dur)
    t = np.arange(N) / SR
    xs, ys = zip(*puntos)
    f = np.exp(np.interp(t / dur, xs, np.log(ys)))
    f = suavizar(f, 0.12)
    f *= 1 + 0.006 * np.sin(2 * np.pi * 4.3 * t) + 0.004 * np.sin(2 * np.pi * 0.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(N)
    for k in range(1, 9):
        w = np.exp(-(np.log(k * f / brillo)) ** 2 / 1.1) / k ** 0.5
        y += np.sin(k * ph) * w
    e = paso(t / (0.3 * dur)) * paso((dur - t) / (0.35 * dur))
    return pb(y * e, 2800)


def latido(fuerza=1.0):
    """El corazon maldito, lub-dub: un golpe grave y sordo (bombo y timbal en
    re apagados) y el segundo, mas corto y un poco mas agudo."""
    lub = pico_(tambor(46.0, 0.32, 3, 0, 0.7, 0.03, (60, 400, 0.6, 0.05), (400, 1500, 0.15, 0.01), (1.5, 0.25, 0.1)), 1.0)
    dub = pico_(tambor(52.0, 0.22, 2, 1, 0.6, 0.025, (70, 500, 0.6, 0.04), (500, 1800, 0.15, 0.008), (1.5, 0.25, 0.08)), 0.62)
    sep = n_(0.19)
    y = np.zeros(max(len(lub), sep + len(dub)))
    y[:len(lub)] += lub
    y[sep:sep + len(dub)] += dub
    return pb(y, 900) * fuerza


def periodica(n, f_lo, f_hi, semilla, componentes=24):
    """Curva lenta al azar (desviacion ~1) que se repite exacta cada n
    muestras: rachas, oleaje y temblores que no saltan en el bucle."""
    r = np.random.default_rng(semilla)
    T = n / SR
    k_lo, k_hi = max(1, int(f_lo * T)), max(2, int(f_hi * T))
    ks = r.integers(k_lo, k_hi + 1, componentes)
    t = np.arange(n) / n
    y = np.zeros(n)
    for k in ks:
        y += np.sin(2 * np.pi * k * t + r.uniform(0, 2 * np.pi)) / np.sqrt(k)
    return y / (np.std(y) + 1e-12)


def ruido_circular(n, filtro, color='blanco', pre=2.0):
    """Ruido filtrado que da la vuelta sin costura: se filtra con el final
    pegado delante, asi el filtro empieza donde acaba."""
    x = ruido(n, color)
    p = min(n, n_(pre))
    y = filtro(np.concatenate([x[-p:], x]))
    return y[p:]


# ======================================================================
#  Mezcla: buses, salas (convolucion), plegado del bucle y master
# ======================================================================
def respuesta_sala(rt60, predelay=0.02, oscuro=7000.0, semilla=1, graves=1.15, agudos=0.55, tempranas=10, densidad=0.03):
    """Respuesta al impulso estereo: cola de ruido que decae por bandas (los
    graves duran mas, los agudos menos), reflexiones tempranas sueltas y una
    entrada difusa. Izquierda y derecha son ruidos distintos: abre el campo."""
    n = n_(rt60 * 1.2 + predelay)
    t = np.arange(n) / SR
    out = []
    for canal in range(2):
        r = np.random.default_rng(semilla * 10 + canal)
        x = r.standard_normal(n)
        h = (pb(x, 400) * np.exp(-6.9 * t / (rt60 * graves)) + bp(x, 400, 2500) * np.exp(-6.9 * t / rt60)
             + pa(x, 2500) * np.exp(-6.9 * t / (rt60 * agudos)) * 0.8)
        h = pb(h, oscuro)
        h *= paso(t / densidad)
        pd = n_(predelay)
        h = np.concatenate([np.zeros(pd), h[:n - pd]])
        for k in range(tempranas):
            d = n_(predelay * 0.3 + r.uniform(0.004, 0.075))
            h[d] += r.choice([-1, 1]) * r.uniform(0.3, 1.0) * 6.0 * np.exp(-d / SR / 0.05)
        out.append(h / np.sqrt(np.sum(h ** 2)))
    return np.array(out, dtype=np.float32)


def curva_db(puntos, muestras_compas, n, unidad=1.0):
    """Automatizacion: [(compas (desde 1, con decimales), dB), ...] a una
    ganancia lineal por muestra."""
    xs = np.array([(p[0] - 1) * muestras_compas for p in puntos], dtype=float)
    ys = np.array([p[1] for p in puntos], dtype=float)
    idx = np.arange(n, dtype=float)
    return (10 ** (np.interp(idx, xs, ys) / 20)).astype(np.float32)


class Mezcla:
    def __init__(self, n, salas):
        self.n = n
        self.mix = np.zeros((2, n), dtype=np.float32)
        self.salas = salas
        self.envios = {k: np.zeros((2, n), dtype=np.float32) for k in salas}
        self.niveles = {}

    def sumar(self, nombre, bus, gan_db=0.0, eq=(), envios=None, auto=None, ancho=1.0):
        x = ecualizar(bus, eq) if eq else bus
        x = (x * 10 ** (gan_db / 20)).astype(np.float32)
        if auto is not None:
            x *= auto
        if ancho != 1.0:
            m, s = 0.5 * (x[0] + x[1]), 0.5 * (x[0] - x[1]) * ancho
            x = np.vstack([m + s, m - s]).astype(np.float32)
        self.mix += x
        for k, a in (envios or {}).items():
            self.envios[k] += a * x
        self.niveles[nombre] = 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)

    def cerrar(self):
        for k, ir in self.salas.items():
            e = self.envios[k]
            if not np.any(e):
                continue
            for c in range(2):
                otro = 1 - c
                h = signal.oaconvolve(e[c] + 0.35 * e[otro], ir[c])[:self.n]
                self.mix[c] += h.astype(np.float32)
        return self.mix


def plegar(x, L):
    """El bucle: lo que suena despues del final (colas, reverb) se suma al
    principio, asi el final entra en el principio sin hueco ni chasquido."""
    y = x[:, :L].astype(np.float64).copy()
    resto = x[:, L:]
    while resto.shape[1]:
        k = min(L, resto.shape[1])
        y[:, :k] += resto[:, :k]
        resto = resto[:, k:]
    return y


def _circular(f, x, pad):
    """Aplica un proceso con memoria como si el bucle no tuviera costura."""
    p = min(pad, x.shape[-1])
    xp = np.concatenate([x[..., -p:], x], axis=-1)
    return f(xp)[..., p:]


def compresor(x, umbral_db=-20.0, ratio=2.0, rodilla=6.0, t_det=0.025, t_gan=0.25):
    """Compresor de bus suave (pegamento): detecta la potencia, calcula la
    reduccion con rodilla blanda y la suaviza. Circular: sin costura."""
    def proc(xp):
        p = np.mean(xp ** 2, axis=0)
        p = suavizar(p, t_det)
        d = 10 * np.log10(p + 1e-12) - umbral_db
        exceso = np.where(d > rodilla / 2, d, np.where(d < -rodilla / 2, 0.0, (d + rodilla / 2) ** 2 / (2 * rodilla)))
        gr = -exceso * (1 - 1 / ratio)
        gr = suavizar(gr, t_gan)
        return xp * 10 ** (gr / 20)
    return _circular(proc, x, n_(3.0))


def limitador(x, techo_db=-1.3, ventana=0.003, suelta=0.05):
    """Limitador con anticipacion, circular: la ganancia baja antes del pico
    (minimo en ventana + promedio) y vuelve despacio."""
    techo = 10 ** (techo_db / 20)
    pk = np.max(np.abs(x), axis=0)
    req = np.minimum(1.0, techo / np.maximum(pk, 1e-9))
    W = n_(ventana)
    g = minimum_filter1d(req, size=2 * W + 1, mode='wrap')
    g = uniform_filter1d(g, size=W, mode='wrap')
    Ws = n_(suelta)
    g2 = minimum_filter1d(g, size=2 * Ws + 1, mode='wrap')
    g2 = uniform_filter1d(g2, size=Ws, mode='wrap')
    g = np.minimum(g, 0.5 * (g + g2))
    y = x * g
    return np.clip(y, -techo, techo), float(np.min(g))


def lufs(x):
    """Sonoridad integrada (ITU-R BS.1770): ponderacion K y puertas."""
    def biq(G, Q, fc, tipo):
        A = 10 ** (G / 40)
        w = 2 * np.pi * fc / SR
        c, al = np.cos(w), np.sin(w) / (2 * Q)
        if tipo == 'estante':
            b = [A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al)]
            a = [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al]
        else:
            b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
            a = [1 + al, -2 * c, 1 - al]
        return _biquad(b, a)
    sos = np.vstack([biq(4.0, 1 / np.sqrt(2), 1500.0, 'estante'), biq(0.0, 0.5, 38.0, 'paso')])
    y = signal.sosfilt(sos, x, axis=-1)
    bl, hop = n_(0.4), n_(0.1)
    cs = np.cumsum(np.concatenate([np.zeros((2, 1)), y ** 2], axis=1), axis=1)
    ini = np.arange(0, y.shape[1] - bl, hop)
    z = (cs[:, ini + bl] - cs[:, ini]) / bl
    lk = -0.691 + 10 * np.log10(z.sum(axis=0) + 1e-12)
    z = z[:, lk > -70]
    lk = lk[lk > -70]
    rel = -0.691 + 10 * np.log10(z.sum(axis=0).mean() + 1e-12) - 10
    z = z[:, lk > rel]
    return -0.691 + 10 * np.log10(z.sum(axis=0).mean() + 1e-12)


def master(x, objetivo_lufs=-16.0, techo_db=-1.3):
    """Pegamento, una pizca de saturacion, sonoridad al objetivo y limitador."""
    x = pa(x, 28, 2)
    x = ecualizar(x, [('agudos', 9000, -1.5)])
    x = compresor(x, umbral_db=-22.0, ratio=1.8)
    for _ in range(3):
        g = 10 ** ((objetivo_lufs - lufs(x)) / 20)
        x = x * g
        y, gmin = limitador(np.tanh(x * 1.1) / 1.1, techo_db)
        error = objetivo_lufs - lufs(y)
        if abs(error) < 0.15:
            break
        x = x * 10 ** (error / 20)
    return y, gmin


# ======================================================================
#  Partitura: la musica escrita como datos
# ======================================================================
import re
_TOKEN = re.compile(r"^(r|[A-G][#b]*\d)(?::(\d+(?:\.\d+)?(?:/\d+)?))?((?:[>^.*_('\"]|~\d?)*)$")
DINAMICAS = {'pp': 0.25, 'p': 0.36, 'mp': 0.5, 'mf': 0.63, 'f': 0.78, 'ff': 0.92, 'fff': 1.0}


class Partitura:
    """Compases de `por_compas` unidades (corcheas en 6/8, negras en 4/4).
    Un compas dura un numero entero de muestras: el bucle cierra exacto."""

    def __init__(self, nombre, compases, por_compas, seg_unidad):
        self.nombre = nombre
        self.nc, self.pc = compases, por_compas
        self.mc = int(round(por_compas * seg_unidad * SR))
        self.u = self.mc / por_compas / SR
        self.L = compases * self.mc
        self.notas = {}
        self.golpes = {}
        self.auto = {}
        self.secciones = []
        self._fr = 0

    def t(self, compas, pos=0.0):
        return ((compas - 1) * self.pc + pos) * self.u

    def seccion(self, compas, nombre):
        self.secciones.append((compas, nombre))

    def nota(self, inst, m, compas, pos, dur, vel=0.6, art='leg', **kw):
        m = midi(m) if isinstance(m, str) else m
        nt = Nota(self.t(compas, pos), dur * self.u, m, vel, art, **kw)
        self.notas.setdefault(inst, []).append(nt)
        return nt

    def acorde(self, inst, texto, compas, pos, dur, vel=0.6, art='leg', transp=0, **kw):
        for nm in texto.split():
            self.nota(inst, midi(nm) + transp, compas, pos, dur, vel, art, **kw)

    def melodia(self, inst, texto, compas, pos=0.0, vel=None, transp=0, art='leg', lig=True, comprobar=True, **kw):
        """Texto: 'A3:2 D4:1 F4:3 | G4:2 ...'. Duracion en unidades (si falta,
        la anterior). Sufijos: > acento, ^ marcato, . staccato, * glissando
        desde abajo, ~N trino de N semitonos, _ ligadura a la siguiente
        (misma nota). 'r' silencio. 'gE5' apoyatura breve antes de la
        siguiente. ( ligada a la anterior, ' picada (con golpe de lengua o
        de arco). Dinamicas sueltas: pp p mp mf f ff. '|' comprueba el
        compas."""
        vel = DINAMICAS['mf'] if vel is None else vel
        self._fr += 1
        frase = self._fr
        t = pos
        dur = self.pc
        en_compas = 0.0
        pend = None
        gracia = None
        for tok in texto.split():
            if tok == '|':
                if comprobar and abs(en_compas - self.pc) > 1e-6:
                    raise ValueError('%s: compas de %.3f unidades en "%s" (compas %d)' % (self.nombre, en_compas, texto[:40], compas))
                en_compas = 0.0
                continue
            if tok in DINAMICAS:
                vel = DINAMICAS[tok]
                continue
            if tok[0] == 'g' and len(tok) > 1 and tok[1] in 'ABCDEFG':
                gracia = midi(tok[1:]) + transp
                continue
            mt = _TOKEN.match(tok)
            if not mt:
                raise ValueError('%s: no entiendo "%s"' % (self.nombre, tok))
            nm, num, mods = mt.group(1), mt.group(2), mt.group(3) or ''
            if num:
                if '/' in num:
                    a_, b_ = num.split('/')
                    dur = float(a_) / float(b_)
                else:
                    dur = float(num)
            en_compas += dur
            if nm == 'r':
                pend = None
                t += dur
                self._fr += 1
                frase = self._fr
                continue
            m = midi(nm) + transp
            if pend is not None and pend.m == m:
                pend.d += dur * self.u
                t += dur
                if '_' not in mods:
                    pend = None
                continue
            v = vel
            a = art
            trino = 0.0
            if '>' in mods:
                v, a = min(1.1, vel * 1.2), 'acc'
            if '^' in mods:
                v, a = min(1.15, vel * 1.28), 'marc'
            if '~' in mods:
                k = mods.index('~')
                trino = float(mods[k + 1]) if len(mods) > k + 1 and mods[k + 1].isdigit() else 2.0
            sonando = dur * (0.5 if '.' in mods else 1.0)
            if gracia is not None:
                g = min(0.08 / self.u, 0.25 * dur)
                self.nota(inst, gracia, compas, t - g, g, v * 0.8, a, lig=True, frase=frase, **kw)
                gracia = None
            ligada = True if '(' in mods else False if "'" in mods else lig
            nt = self.nota(inst, m, compas, t, sonando, v, a, lig=ligada, frase=frase, bend=(90.0 if '*' in mods else 0.0), trino=trino, **kw)
            if '.' in mods:
                self._fr += 1
                frase = self._fr
            pend = nt if '_' in mods else None
            t += dur
        return t

    def golpe(self, inst, compas, pos=0.0, vel=0.8, **kw):
        self.golpes.setdefault(inst, []).append((self.t(compas, pos), vel, kw))

    def patron(self, inst, texto, desde, hasta, paso=1.0, vel=1.0, offset=0.0, **kw):
        """Ritmo por pasos: X fuerte, x normal, o suave, g fantasma, - nada.
        El patron se repite seguido aunque no mida un compas (polirritmos)."""
        pesos = {'X': 1.0, 'x': 0.72, 'o': 0.48, 'g': 0.28}
        pasos = [c for c in texto if c not in ' |']
        total = (hasta - desde + 1) * self.pc
        k = 0
        pos = offset
        while pos < total - 1e-9:
            c = pasos[k % len(pasos)]
            if c in pesos:
                self.golpes.setdefault(inst, []).append((self.t(desde, pos), vel * pesos[c], dict(kw)))
            pos += paso
            k += 1

    def automatizar(self, bus, puntos):
        self.auto[bus] = puntos


# ======================================================================
#  Produccion: instrumentos -> buses -> salas -> bucle -> master -> .ogg
# ======================================================================
def _poner_mono(bus, x, t, gan, pan, L, ancho=0.0):
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    x = np.asarray(x, dtype=np.float32) * gan
    if ancho:
        d = max(1, int(ancho * SR))
        st = np.vstack([np.concatenate([x, np.zeros(d, np.float32)]) * np.cos(th),
                        np.concatenate([np.zeros(d, np.float32), x]) * np.sin(th)])
    else:
        st = np.vstack([x * np.cos(th), x * np.sin(th)])
    poner(bus, st, t, L)


def _nivel(v):
    return 0 if v < 0.45 else 1 if v < 0.7 else 2 if v < 0.9 else 3


def producir(p, inst, salas, cola=10.0, objetivo=-16.0, carpeta=None, ruta=None, extra=None):
    """inst: nombre -> dict(tipo='frase'|'golpe'|'nota_golpe'|'lecho', ...)."""
    t0 = time.time()
    n = p.L + n_(cola)
    mz = Mezcla(n, salas)
    tiempos = {}
    for nombre, cfg in inst.items():
        ti = time.time()
        tipo = cfg['tipo']
        bus = np.zeros((2, n), dtype=np.float32)
        if tipo == 'frase':
            notas = p.notas.get(nombre)
            if not notas:
                continue
            P = cfg['P']
            if P.get('coro'):
                por_voz = {}
                for nt in notas:
                    por_voz.setdefault(P.get('voz') or tipo_voz(nt.m), []).append(nt)
                for vz, nn in por_voz.items():
                    P2 = dict(P, timbre=t_coro(vz, P['vocales'][0], P['vocales'][1], P.get('suave', 1.0), P.get('tilt', 1.25)))
                    tocar(nn, P2, bus, p.L)
            else:
                tocar(notas, P, bus, p.L)
        elif tipo == 'nota_golpe':
            notas = p.notas.get(nombre)
            if not notas:
                continue
            fn = cfg['fn']
            for nt in notas:
                nt.t += rng.normal(0, cfg.get('hum_t', 0.006))
                v = nt.v * (1 + rng.normal(0, 0.06))
                x = fn(int(round(nt.m)), _nivel(v), int(rng.integers(0, cfg.get('variantes', 3))))
                pan = cfg['pan'](nt) if callable(cfg['pan']) else cfg['pan']
                _poner_mono(bus, x, nt.t, v, pan + nt.pan, p.L, cfg.get('ancho', 0.0))
        elif tipo == 'golpe':
            golpes = p.golpes.get(nombre)
            if not golpes:
                continue
            fn = cfg['fn']
            for (t, v, kw) in golpes:
                t += rng.normal(0, cfg.get('hum_t', 0.004))
                v = v * (1 + rng.normal(0, cfg.get('hum_v', 0.05)))
                x = fn(v, int(rng.integers(0, cfg.get('variantes', 3))), **kw)
                pan = kw.get('pan', cfg.get('pan', 0.0))
                if callable(pan):
                    pan = pan()
                _poner_mono(bus, x, t, v, pan, p.L, cfg.get('ancho', 0.0))
        elif tipo == 'lecho':
            x = cfg['fn'](p)
            bus[:, :p.L] += x.astype(np.float32)
        auto = curva_db(p.auto[nombre], p.mc, n) if nombre in p.auto else None
        mz.sumar(nombre, bus, cfg.get('gan', 0.0), cfg.get('eq', ()), cfg.get('envios'), auto, cfg.get('estereo', 1.0))
        tiempos[nombre] = time.time() - ti
    print('  %s: instrumentos %.1f s (%s)' % (p.nombre, time.time() - t0, ', '.join('%s %.1f' % kv for kv in sorted(tiempos.items(), key=lambda kv: -kv[1])[:6])), flush=True)
    mezcla = mz.cerrar()
    bucle = plegar(mezcla, p.L)
    final, gmin = master(bucle, objetivo)
    print('  %s: mezcla y master %.1f s' % (p.nombre, time.time() - t0), flush=True)
    return final, mz.niveles, gmin


# ======================================================================
#  Instrumentos de base (cada pista los copia y los ajusta)
# ======================================================================
def presets():
    return {
        'violines': dict(timbre=t_violin, B=10, V=6, det=6.0, pan=-0.45, ancho=0.3, vib=(5.6, 11, 0.25, 0.4), glide=0.08,
                         ataque=0.14, soltar=0.4, b0=0.15, bk=0.6, bexp=1.0, ruido=((2500, 9000, 0.012, 'nivel'),),
                         disp=0.022, mono=True, hum_t=0.008, trem=(12.0, 15.5)),
        'violas': dict(timbre=t_viola, B=10, V=5, det=6.0, pan=-0.05, ancho=0.25, vib=(5.4, 10, 0.25, 0.4), glide=0.08,
                       ataque=0.15, soltar=0.4, b0=0.15, bk=0.55, bexp=1.0, ruido=((2000, 8000, 0.012, 'nivel'),), disp=0.022,
                       mono=True),
        'chelos': dict(timbre=t_chelo, B=10, V=5, det=5.0, pan=0.3, ancho=0.2, vib=(5.2, 9, 0.3, 0.4), glide=0.08,
                       ataque=0.07, soltar=0.33, b0=0.18, bk=0.55, bexp=1.0, ruido=((1500, 6000, 0.012, 'nivel'),), disp=0.018),
        'contrabajos': dict(timbre=t_contrabajo, B=8, V=4, det=4.0, pan=0.38, ancho=0.12, vib=(5.0, 6, 0.35, 0.5), glide=0.08,
                            ataque=0.12, soltar=0.4, b0=0.22, bk=0.5, bexp=1.0, disp=0.015),
        'trompas': dict(timbre=t_trompa, B=12, V=4, det=4.0, pan=-0.2, ancho=0.25, vib=(5.0, 2.5, 0.4, 0.5), glide=0.05,
                        ataque=0.06, soltar=0.32, b0=0.05, bk=0.85, bexp=0.8, bt=0.12, scoop=(25, 0.04), disp=0.015,
                        mono=True, hum_t=0.008),
        'trombones': dict(timbre=t_trombon, B=12, V=3, det=4.0, pan=0.22, ancho=0.2, vib=(5.0, 0, 0.4, 0.5), glide=0.05,
                          ataque=0.05, soltar=0.3, b0=0.04, bk=0.85, bexp=0.8, bt=0.15, scoop=(20, 0.035), disp=0.012, mono=True),
        'tuba': dict(timbre=t_tuba, B=10, V=2, det=3.0, pan=0.1, ancho=0.05, vib=(5.0, 0, 0.4, 0.5), glide=0.05, ataque=0.06,
                     soltar=0.3, b0=0.05, bk=0.75, bexp=0.8, scoop=(15, 0.04), mono=True),
        'coro': dict(timbre=None, coro=True, vocales=('u', 'a'), B=8, V=5, det=8.0, pan=0.0, ancho=0.55, vib=(5.3, 20, 0.2, 0.6),
                     glide=0.12, ataque=0.32, soltar=0.6, eje='vocal', ruido=((700, 3500, 0.02, 'nivel'),), disp=0.03),
    }


def _pcs(texto):
    return [midi(x + '0') % 12 for x in texto.split()]


def subir(pcs, desde, cuantas):
    """Notas del acorde (clases de altura) hacia arriba desde `desde`."""
    out = []
    m = desde
    while len(out) < cuantas:
        if m % 12 in pcs:
            out.append(m)
        m += 1
    return out


def ligar_acordes(p, inst, acordes, vel, art='leg', ataque_comun=False, **kw):
    """acordes: lista de (compas, pos, dur, 'C4 E4 G4'). Las notas comunes a
    dos acordes seguidos no se repiten: se alargan (conduccion de voces)."""
    vivas = {}
    for compas, pos, dur, texto in acordes:
        t0 = p.t(compas, pos)
        nuevas = {midi(x) for x in texto.split()}
        for m in list(vivas):
            nt = vivas[m]
            if m in nuevas and abs(nt.t + nt.d - t0) < 1e-6 and not ataque_comun:
                nt.d += dur * p.u
            else:
                del vivas[m]
        for m in nuevas:
            if m not in vivas:
                vivas[m] = p.nota(inst, m, compas, pos, dur, vel, art, **kw)


# ======================================================================
#  NEREA, Guardiana de los Mares. Re menor (dorico a ratos), 6/8 a 66.
# ======================================================================
NEREA_AC = {
    # acorde: (contrabajo, ola de chelos, voces centrales, notas del acorde)
    'Dm': ('D2', 'D2 A2 D3 F3 D3 A2', 'D4 F4 A4', 'D F A'),
    'Bb': ('Bb1', 'F2 Bb2 D3 F3 D3 Bb2', 'D4 F4 Bb4', 'Bb D F'),
    'Gm': ('G1', 'D2 G2 Bb2 D3 Bb2 G2', 'D4 G4 Bb4', 'G Bb D'),
    'A': ('A1', 'E2 A2 C#3 E3 C#3 A2', 'C#4 E4 A4', 'A C# E'),
    'A7': ('A1', 'E2 A2 C#3 G3 C#3 A2', 'C#4 G4 A4', 'A C# E G'),
    'G/D': ('D2', 'D2 G2 B2 D3 B2 G2', 'D4 G4 B4', 'G B D'),
    'C': ('C2', 'C2 G2 C3 E3 C3 G2', 'C4 E4 G4', 'C E G'),
    'F': ('F1', 'C2 F2 A2 C3 A2 F2', 'C4 F4 A4', 'F A C'),
    'Eb': ('Eb2', 'Eb2 Bb2 Eb3 G3 Eb3 Bb2', 'Eb4 G4 Bb4', 'Eb G Bb'),
    'Em7b5': ('E2', 'E2 Bb2 D3 G3 D3 Bb2', 'D4 G4 Bb4', 'E G Bb D'),
    'D7/F#': ('F#1', 'F#2 A2 D3 F#3 D3 A2', 'C4 F#4 A4', 'D F# A C'),
    'E7/G#': ('G#1', 'G#2 B2 E3 G#3 E3 B2', 'D4 G#4 B4', 'E G# B D'),
}

NEREA_TEMA = ("A3:2 D4:1 F4:3 | G4:2 F4:1( D4:3 | D4:2 G4:1 Bb4:3 | A4:2 G4:1( E4:3",
              "A3:2 D4:1 A4:3 | G4:2 F4:1( D5:3 | C5:2 Bb4:1( A4:2 G4:1( | F4:2 E4:1( D4:3")
NEREA_CONTRA = "A5:3 G5:2 F5:1 | F5:3 G5:2 A5:1 | Bb5:3 A5:2 G5:1 | A5:3 G5:2 E5:1 | F5:3 E5:2 D5:1 | D5:3 E5:2 F5:1 | G5:3 A5:3 | A5:6"
NEREA_LAMENTO = "D5:2 C5:1 D5:3 | F5:3 E5:2 C5:1 | D5:3 Bb4:2 C5:1 | A4:6 | D5:2 C5:1 D5:2 F5:1 | A5:3 G5:2 F5:1 | E5:2 D5:1 Bb4:3 | C#5:3 A4:3"


def nerea():
    global rng
    rng = np.random.default_rng(20261005)
    p = Partitura('nerea', 72, 6, 60.0 / 66 / 3)
    AC = NEREA_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c if isinstance(c, tuple) else (c,)
    armonia(1, ['Dm', 'Dm', 'G/D', 'Dm', 'Bb', 'C', 'Gm', 'A'])
    armonia(9, ['Dm', 'Bb', 'Gm', 'A7', 'Dm', 'Bb', ('Gm', 'A7'), 'Dm'] * 2)
    armonia(25, ['Bb', 'F', 'Gm', 'Dm', 'Bb', 'F', 'Gm', 'A'])
    armonia(33, ['Dm', 'Eb', 'Em7b5', 'F', 'D7/F#', 'Gm', 'E7/G#', 'A'])
    armonia(41, ['Dm', 'Bb', 'Gm', 'A7', 'Dm', 'Bb', ('Gm', 'A7'), 'Dm', 'Dm', 'Bb', 'Gm', 'A7', 'Dm', 'Bb', ('Gm', 'A7'), 'Bb'])
    armonia(57, ['Eb', 'Dm', 'Eb', 'Dm', 'Bb', 'Gm', 'A', 'A'])
    armonia(65, ['Dm', 'Bb', 'Gm', 'A7', 'Dm', 'Bb', 'Gm', 'A'])

    def trozos(c):
        a = arm[c]
        return [(0, 6, a[0])] if len(a) == 1 else [(0, 3, a[0]), (3, 3, a[1])]

    def ola(c0, c1, v0, v1=None, art='leg'):
        """Chelos: el oleaje, arpegio que sube y baja en cada compas."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                notas = AC[ch][1].split()
                if dur == 3:
                    notas = notas[:3]
                for k, nm in enumerate(notas):
                    p.nota('chelos', nm, c, pos + k, 1.3, v * (0.8, 0.9, 0.98, 1.0, 0.92, 0.84)[k], art)

    def bajos(c0, c1, v0, v1=None, art='swell', inst='contrabajos'):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                p.nota(inst, AC[ch][0], c, pos, dur, v, art)

    def arpa_ola(c0, c1, v0, v1=None, paso=1.0, desde='D4'):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                cuantas = int(round(dur / paso))
                arriba = subir(_pcs(AC[ch][3]), midi(desde), cuantas // 2 + 1 + (1 if paso < 1 else 0))
                figura = arriba + arriba[-2:0:-1]
                for k in range(cuantas):
                    m = figura[k % len(figura)]
                    p.nota('arpa', m, c, pos + k * paso, paso, v * (0.75 + 0.25 * (m - midi(desde)) / 24.0))

    def campanitas(c0, c1, v, por_compas=2):
        for c in range(c0, c1 + 1):
            for pos, dur, ch in trozos(c):
                opciones = subir(_pcs(AC[ch][3]), midi('D6'), 5)
                for k in range(max(1, int(por_compas * dur / 6))):
                    pp = pos + (k * 3 if por_compas > 1 else 0) + rng.choice([0, 0, 1.5])
                    p.nota('cristal', int(rng.choice(opciones)), c, pp, 2, v * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.6, 0.6))

    def pads(inst, c0, c1, vel, vocal=0.0, transp=0, art='leg'):
        acordes = []
        for c in range(c0, c1 + 1):
            for pos, dur, ch in trozos(c):
                acordes.append((c, pos, dur, ' '.join('%s' % x for x in AC[ch][2].split())))
        if transp:
            acordes = [(a, b, d, ' '.join(_nombre(midi(x) + transp) for x in t.split())) for a, b, d, t in acordes]
        ligar_acordes(p, inst, acordes, vel, art, vocal=vocal)

    def corazon(c0, c1, v0, v1=None, por_compas=1):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            p.golpe('latido', c, 0, v)
            if por_compas == 2:
                p.golpe('latido', c, 3, v * 0.85)

    def redoble(c, pos, dur, m, v0, v1, ritmo=0.075):
        t = 0.0
        k = 0
        while t < dur * p.u - 0.02:
            v = v0 + (v1 - v0) * (t / (dur * p.u))
            p.nota('timbales', m, c, pos + t / p.u, 0.5, v * (0.85 + 0.15 * (k % 2)))
            t += ritmo * (1 + 0.08 * rng.standard_normal())
            k += 1

    # ------------------------------------------------ INTRO (1-8): el fondo del mar
    p.seccion(1, 'intro')
    p.golpe('cadenas', 1, 0, 0.9, pan=-0.45)
    p.golpe('cadenas', 1, 2.5, 0.5, pan=0.5)
    p.nota('timbales', 'D2', 1, 0, 2, 0.8)
    p.golpe('bombo', 1, 0, 0.85)
    corazon(1, 8, 0.55, 0.72)
    p.nota('contrabajos', 'D2', 1, 0, 24, 0.4, 'swell')
    p.nota('chelos', 'D3', 1, 0, 24, 0.3, 'swell')
    p.nota('chelos', 'A3', 3, 0, 12, 0.25, 'swell')
    bajos(5, 8, 0.45, 0.6)
    ola(5, 8, 0.4, 0.55)
    arpa_ola(3, 8, 0.32, 0.45)
    campanitas(2, 8, 0.35, 2)
    p.golpe('ballena', 2, 0, 0.7, dur=4.6, puntos=[(0, 587), (0.35, 880), (0.7, 784), (1, 698)], pan=0.55)
    p.golpe('ballena', 6, 1, 0.6, dur=4.0, puntos=[(0, 880), (0.4, 1175), (1, 1047)], pan=-0.55)
    pads('coro', 5, 8, 0.4, vocal=0.0)
    pads('violas', 3, 8, 0.28, transp=-12)
    p.melodia('trompas', "mp D4:3 A4:3 | G4:2 F4:1( E4:3", 7, lig=False)
    redoble(8, 2, 4, 'A1', 0.25, 0.75)
    p.golpe('platillos', 8, 0, 0.45, redoble=6 * p.u)

    # ------------------------------------------------ A (9-24): el tema de Nerea
    p.seccion(9, 'A')
    p.golpe('cadenas', 9, 0, 0.6, pan=0.45)
    p.golpe('platillos', 9, 0, 0.35)
    p.nota('timbales', 'D2', 9, 0, 2, 0.85)
    p.golpe('bombo', 9, 0, 0.7)
    corazon(9, 24, 0.7, 0.8)
    for c in range(11, 25, 2):
        p.nota('timbales', raiz_timbal(AC[arm[c][0]][3]), c, 0, 2, 0.45)
    bajos(9, 24, 0.55, 0.7)
    ola(9, 24, 0.55, 0.72)
    arpa_ola(9, 16, 0.45)
    arpa_ola(17, 24, 0.42, 0.5, paso=0.5)
    campanitas(9, 24, 0.3, 1)
    pads('coro', 9, 16, 0.38, vocal=0.0)
    pads('coro', 17, 24, 0.48, vocal=0.45)
    pads('violas', 9, 24, 0.32, transp=-12)
    p.melodia('trompas', 'mf ' + NEREA_TEMA[0], 9, lig=False)
    p.melodia('trompas', 'mf ' + NEREA_TEMA[1], 13, lig=False)
    p.melodia('trompas', 'mf ' + NEREA_TEMA[0], 17, lig=False)
    p.melodia('trompas', 'f ' + NEREA_TEMA[1], 21, lig=False)
    p.melodia('violines', 'mp ' + NEREA_CONTRA, 17)
    p.golpe('cadenas', 17, 0, 0.55, pan=-0.5)
    p.golpe('platillos', 24, 0, 0.3, redoble=6 * p.u)

    # ------------------------------------------------ B1 (25-32): el lamento de la sirena
    p.seccion(25, 'B1 lamento')
    p.golpe('platillos', 25, 0, 0.25)
    corazon(25, 32, 0.6, 0.55)
    for c in range(25, 33):
        for pos, dur, ch in trozos(c):
            p.nota('contrabajos', AC[ch][0], c, pos, dur, 0.38, 'swell')
            p.nota('chelos', AC[ch][1].split()[1], c, pos, dur, 0.32, 'swell')
    arpa_ola(25, 32, 0.42, 0.42)
    campanitas(25, 32, 0.38, 2)
    pads('violas', 25, 32, 0.3, transp=-12)
    p.melodia('coro_sop', 'mf ' + NEREA_LAMENTO, 25)
    p.golpe('ballena', 26, 2, 0.6, dur=5.0, puntos=[(0, 440), (0.3, 659), (0.65, 587), (1, 523)], pan=-0.6)
    p.golpe('ballena', 30, 0, 0.55, dur=4.4, puntos=[(0, 698), (0.45, 1047), (1, 880)], pan=0.6)
    p.nota('trompas', 'A3', 31, 0, 12, 0.45, 'cresc', lig=False)

    # ------------------------------------------------ B2 (33-40): la maldicion crece
    p.seccion(33, 'B2 crece')
    corazon(33, 40, 0.7, 0.95, por_compas=2)
    for c, v in ((33, 0.75), (35, 0.65), (37, 0.75), (39, 0.85)):
        p.golpe('cadenas', c, 0, v, pan=(-0.5 if c % 4 == 1 else 0.5))
    for c in range(33, 39):
        p.nota('timbales', raiz_timbal(AC[arm[c][0]][3]), c, 0, 2, 0.5 + 0.05 * (c - 33))
    redoble(39, 0, 12, 'A1', 0.35, 1.0)
    bajos(33, 40, 0.6, 0.9, art='marc')
    ola(33, 40, 0.62, 0.9)
    arpa_ola(33, 40, 0.42, 0.55, paso=0.5)
    secuencia = ['A3:2 D4:1 F4:3', 'Bb3:2 Eb4:1 G4:3', 'Bb3:2 E4:1 G4:3', 'C4:2 F4:1 A4:3',
                 'C4:2 F#4:1 A4:3', 'D4:2 G4:1 Bb4:3', 'D4:2 G#4:1 B4:3', 'E4:2 A4:1 C#5:3']
    for i, frag in enumerate(secuencia):
        v = 0.5 + 0.45 * i / 7
        p.melodia('trompas', frag, 33 + i, vel=v, lig=False)
        if i >= 4:
            p.melodia('trombones', frag, 33 + i, vel=v, transp=-12, lig=False)
    for c in range(33, 41):
        for pos, dur, ch in trozos(c):
            for nm in subir(_pcs(AC[ch][3]), midi('D5'), 3):
                p.nota('violines', nm, c, pos, dur, 0.35 + 0.5 * (c - 33) / 7, 'trem')
    pads('coro', 33, 40, 0.5, vocal=0.3)
    p.golpe('platillos', 39, 0, 0.6, redoble=12 * p.u)

    # ------------------------------------------------ A' (41-56): tutti
    p.seccion(41, "A' tutti")
    for c in (41, 49):
        p.golpe('platillos', c, 0, 0.8)
        p.golpe('cadenas', c, 0, 0.9, pan=0.0)
    p.golpe('platillos', 48, 3, 0.45, redoble=3 * p.u)
    corazon(41, 56, 0.95, 0.95, por_compas=2)
    for c in range(41, 57):
        p.golpe('bombo', c, 0, 0.75 if c % 2 else 0.6)
        p.nota('timbales', raiz_timbal(AC[arm[c][0]][3]), c, 0, 2, 0.7)
        if c % 4 == 0:
            p.nota('timbales', 'A1', c, 3, 1, 0.55)
            p.nota('timbales', 'A1', c, 4, 1, 0.65)
            p.nota('timbales', 'A1', c, 5, 1, 0.75)
    bajos(41, 56, 0.85, 0.9, art='marc')
    bajos(41, 56, 0.6, 0.7, art='marc', inst='tuba')
    ola(41, 56, 0.85, 0.95, art='acc')
    arpa_ola(41, 56, 0.5, 0.5, paso=0.5)
    campanitas(41, 56, 0.35, 1)
    p.melodia('trompas', 'ff ' + NEREA_TEMA[0], 41, lig=False)
    p.melodia('trompas', 'ff ' + NEREA_TEMA[1], 45, lig=False)
    p.melodia('trompas', 'ff ' + NEREA_TEMA[0], 49, lig=False)
    p.melodia('trompas', 'ff ' + NEREA_TEMA[1], 53, lig=False)
    for c, tx in ((41, NEREA_TEMA[0]), (45, NEREA_TEMA[1]), (49, NEREA_TEMA[0]), (53, NEREA_TEMA[1])):
        p.melodia('trombones', 'f ' + tx, c, transp=-12, lig=False)
    p.melodia('coro_tema', 'f ' + NEREA_TEMA[0], 41)
    p.melodia('coro_tema', 'f ' + NEREA_TEMA[1], 45)
    p.melodia('violines', 'f ' + NEREA_CONTRA, 41)
    p.melodia('violines', 'f ' + NEREA_TEMA[0], 49, transp=12)
    p.melodia('violines', 'f ' + NEREA_TEMA[1], 53, transp=12)
    p.melodia('violas', 'mf ' + NEREA_CONTRA, 49, transp=-12)
    pads('coro', 49, 56, 0.62, vocal=1.0)

    # ------------------------------------------------ C (57-64): la maldicion
    p.seccion(57, 'C maldicion')
    p.golpe('platillos', 57, 0, 0.75)
    for c, v in ((57, 1.0), (59, 0.8), (61, 0.7)):
        p.golpe('cadenas', c, 0, v, pan=(0.5 if c == 59 else -0.5))
    corazon(57, 64, 1.0, 0.7, por_compas=2)
    for c in range(57, 65):
        p.nota('timbales', raiz_timbal(AC[arm[c][0]][3]), c, 0, 2, 0.8 - 0.04 * (c - 57))
        p.golpe('bombo', c, 0, 0.8 - 0.05 * (c - 57))
    bajos(57, 64, 0.9, 0.6, art='marc')
    bajos(57, 64, 0.7, 0.45, art='fpc', inst='tuba')
    ola(57, 64, 0.85, 0.6, art='acc')
    p.melodia('trompas', "ff G4:6 | F4:6 | G4:3 Bb4:3 | A4:6 | f D5:3 C5:2 Bb4:1 | Bb4:3 A4:2 G4:1 | mf A4:6 | A4:6", 57, lig=False)
    for c, tx in ((57, 'Eb3 Bb3'), (58, 'D3 A3'), (59, 'Eb3 G3 Bb3'), (60, 'D3 F3 A3'), (61, 'Bb2 F3 D4'), (62, 'G2 D3 Bb3'), (63, 'A2 E3 C#4'), (64, 'A2 E3')):
        p.acorde('trombones', tx, c, 0, 6, 0.85 - 0.05 * (c - 57), 'fpc')
    for c in range(57, 65):
        for pos, dur, ch in trozos(c):
            for nm in subir(_pcs(AC[ch][3]), midi('F5'), 2):
                p.nota('violines', nm, c, pos, dur, 0.8 - 0.06 * (c - 57), 'trem')
    pads('coro', 57, 64, 0.75, vocal=1.0)
    p.automatizar('coro', [(1, 0), (33, -4), (40.9, 3), (41, 0), (57, 1), (61, 0), (65, -6), (73, -6)])

    # ------------------------------------------------ T (65-72): la marea se retira
    p.seccion(65, 'transicion')
    corazon(65, 72, 0.7, 0.55)
    bajos(65, 72, 0.6, 0.45)
    ola(65, 72, 0.6, 0.45)
    arpa_ola(65, 72, 0.45, 0.36)
    campanitas(65, 72, 0.35, 2)
    pads('coro', 65, 72, 0.4, vocal=0.0)
    pads('violas', 65, 72, 0.3, transp=-12)
    p.melodia('trompas', 'mp ' + NEREA_TEMA[0], 65, lig=False)
    p.golpe('ballena', 66, 3, 0.6, dur=4.8, puntos=[(0, 587), (0.4, 784), (1, 659)], pan=0.55)
    p.golpe('ballena', 70, 0, 0.55, dur=4.2, puntos=[(0, 880), (0.5, 1175), (1, 988)], pan=-0.55)
    redoble(72, 2, 4, 'A1', 0.2, 0.6)
    p.golpe('platillos', 71, 3, 0.35, redoble=9 * p.u)

    p.automatizar('oleaje', [(1, 0), (8, -2), (9, -6), (24, -6), (25, -1), (32, -2), (33, -8), (64, -10), (65, -3), (73, 0)])
    return p


def raiz_timbal(acorde):
    """La fundamental del acorde en la octava de los timbales (La1 a Sol#2)."""
    pc = _pcs(acorde)[0]
    return 33 + (pc - 9) % 12


def _nombre(m):
    nombres = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    return '%s%d' % (nombres[m % 12], m // 12 - 1)


def oleaje_nerea(p):
    """El mar: dos olas por cada dos compases (ruido rosa oscuro que sube y
    se abre en la cresta), estereo ancho, sin costura en el bucle."""
    n = p.L
    t = np.arange(n)
    ola = 0.5 - 0.5 * np.cos(2 * np.pi * t / (2 * p.mc) - 0.6)
    ola = ola * (0.8 + 0.2 * periodica(n, 0.01, 0.05, 11))
    out = []
    for canal in range(2):
        rosa = ruido_circular(n, lambda x: signal.lfilter([0.049922035, -0.095993537, 0.050612699, -0.004408786],
                                                           [1, -2.494956002, 2.017265875, -0.522189400], x))
        rosa /= np.std(rosa)
        oscuro = _circular(lambda x: pb(x, 280, 2), rosa, n_(1.0))
        claro = _circular(lambda x: bp(x, 300, 1500), rosa, n_(1.0))
        espuma = _circular(lambda x: bp(x, 1800, 5000), rosa, n_(1.0))
        out.append(oscuro * (0.25 + 0.75 * ola) + claro * ola ** 2 * 0.55 + espuma * ola ** 5 * 0.12)
    return np.array(out)


def instrumentos_nerea():
    P = presets()
    P['violines'].update(b0=0.1, bk=0.5)
    P['trompas'].update(V=5, det=4.5)
    coro_sop = dict(P['coro'], voz='S', vocales=('o', 'a'), V=4, det=6.0, vib=(5.4, 30, 0.25, 0.5), ataque=0.12,
                    soltar=0.5, mono=True, glide=0.11, pan=-0.12, ancho=0.3)
    coro_tema = dict(P['coro'], voz='A', vocales=('o', 'a'), V=6, det=7.0, vib=(5.2, 16, 0.25, 0.5), ataque=0.08,
                     soltar=0.4, mono=True, glide=0.06, suave=0.5, tilt=1.1)
    sala = {'sala': respuesta_sala(3.6, 0.03, 5200, semilla=3, graves=1.25, agudos=0.5),
            'camara': respuesta_sala(1.1, 0.012, 6000, semilla=4, graves=1.0, agudos=0.6, densidad=0.012)}
    I = {
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-3, eq=[('pa', 30), ('pb', 2500)], envios={'sala': 0.12}),
        'chelos': dict(tipo='frase', P=P['chelos'], gan=-4, eq=[('pa', 50), ('pico', 300, -2.5, 1.0), ('pb', 5500)], envios={'sala': 0.25}),
        'violas': dict(tipo='frase', P=P['violas'], gan=-8, eq=[('pa', 140), ('pb', 6500)], envios={'sala': 0.35}),
        'violines': dict(tipo='frase', P=P['violines'], gan=-6, eq=[('pa', 200), ('pico', 3200, -2, 1.0), ('pb', 8500)], envios={'sala': 0.38}),
        'trompas': dict(tipo='frase', P=P['trompas'], gan=-3, eq=[('pa', 90), ('pico', 320, -1.5, 1.0), ('pb', 6500)], envios={'sala': 0.42}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-6, eq=[('pa', 60), ('pb', 6000)], envios={'sala': 0.3}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-7, eq=[('pa', 30), ('pb', 2000)], envios={'sala': 0.15}),
        'coro': dict(tipo='frase', P=P['coro'], gan=-9, eq=[('pa', 150), ('pico', 380, -3, 1.0), ('pb', 8000)], envios={'sala': 0.5}),
        'coro_sop': dict(tipo='frase', P=coro_sop, gan=-6, eq=[('pa', 220), ('pb', 9000)], envios={'sala': 0.55}),
        'coro_tema': dict(tipo='frase', P=coro_tema, gan=-9, eq=[('pa', 150), ('pico', 380, -2, 1.0), ('pb', 8000)], envios={'sala': 0.45}),
        'arpa': dict(tipo='nota_golpe', fn=arpa, pan=lambda nt: -0.55 + 0.015 * (nt.m - 50), gan=-9, eq=[('pa', 90), ('pb', 9000)],
                     envios={'sala': 0.45}),
        'cristal': dict(tipo='nota_golpe', fn=cristal, pan=0.0, gan=-17, eq=[('pa', 500), ('pb', 9000)], envios={'sala': 0.7}),
        'timbales': dict(tipo='nota_golpe', fn=timbal, pan=0.15, gan=-5, eq=[('pa', 35), ('pb', 5000)], envios={'sala': 0.22, 'camara': 0.3}),
        'latido': dict(tipo='golpe', fn=lambda v, var, **kw: latido(), pan=0.0, gan=-2, eq=[('pa', 28)], envios={'sala': 0.12, 'camara': 0.25}),
        'bombo': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(_nivel(v), var, 0.8), pan=0.0, gan=-5, eq=[('pa', 28), ('pb', 3000)],
                      envios={'sala': 0.2, 'camara': 0.3}),
        'platillos': dict(tipo='golpe', fn=lambda v, var, redoble=0, **kw: redoble_platillo(redoble) if redoble else platillo(_nivel(v), var),
                          pan=0.25, gan=-15, eq=[('pa', 350), ('pb', 8500)], envios={'sala': 0.4}),
        'cadenas': dict(tipo='golpe', fn=lambda v, var, **kw: cadena(2, var), gan=-12, eq=[('pa', 250), ('pb', 7000)], envios={'sala': 0.55}),
        'ballena': dict(tipo='golpe', fn=lambda v, var, dur, puntos, **kw: ballena(dur, puntos), gan=-16, eq=[('pa', 200), ('pb', 3200)],
                        envios={'sala': 0.9}),
        'oleaje': dict(tipo='lecho', fn=oleaje_nerea, gan=-25, eq=[('pa', 40), ('pb', 4000)], envios={'sala': 0.15}),
    }
    return I, sala


# ======================================================================
#  Revision: espectrograma + forma de onda en PNG (para ver sin escuchar)
# ======================================================================
_PALETA = np.array([(0.0, 4, 4, 12), (0.18, 40, 12, 80), (0.38, 110, 25, 120), (0.56, 190, 55, 110),
                    (0.74, 245, 120, 60), (0.9, 252, 200, 90), (1.0, 252, 252, 200)], dtype=float)


def _colorear(v):
    v = np.clip(v, 0, 1)
    return np.stack([np.interp(v, _PALETA[:, 0], _PALETA[:, c]) for c in (1, 2, 3)], axis=-1).astype(np.uint8)


def imagen_revision(x, ruta, titulo, marcas=(), ancho=1600, alto=420):
    """Espectrograma (frecuencia logaritmica, 30 Hz a 16 kHz) y debajo la
    forma de onda (pico y RMS por columna) con las secciones marcadas."""
    from PIL import Image, ImageDraw, ImageFont
    mono = x.mean(axis=0) if x.ndim > 1 else x
    salto = max(64, len(mono) // ancho)
    nper = 4096 if salto < 4096 else 8192
    _, _, Z = signal.stft(mono, SR, nperseg=nper, noverlap=max(0, nper - salto), boundary=None, padded=False)
    S = 20 * np.log10(np.abs(Z) + 1e-9)
    fr = np.fft.rfftfreq(nper, 1 / SR)
    fl = np.geomspace(30, 16000, alto)
    filas = np.array([np.interp(fl, fr, S[:, c]) for c in range(S.shape[1])]).T[::-1]
    filas = (filas - (filas.max() - 85)) / 85
    esp = Image.fromarray(_colorear(filas)).resize((ancho, alto), Image.BILINEAR)
    alto_onda = 150
    lienzo = Image.new('RGB', (ancho + 60, alto + alto_onda + 60), (10, 10, 16))
    lienzo.paste(esp, (50, 30))
    d = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.load_default(size=13)
    except TypeError:
        fuente = ImageFont.load_default()
    for f in (50, 100, 200, 400, 1000, 2000, 4000, 8000, 16000):
        yy = 30 + alto - 1 - int(np.log(f / 30) / np.log(16000 / 30) * (alto - 1))
        d.line([(44, yy), (50, yy)], fill=(160, 160, 170))
        d.text((2, yy - 7), ('%dk' % (f // 1000)) if f >= 1000 else str(f), fill=(160, 160, 170), font=fuente)
    # forma de onda
    y0 = 30 + alto + 10
    cols = np.array_split(np.abs(x).max(axis=0) if x.ndim > 1 else np.abs(x), ancho)
    cols2 = np.array_split(mono, ancho)
    for c in range(ancho):
        pk = min(1.0, float(cols[c].max())) if len(cols[c]) else 0.0
        rm = min(1.0, float(np.sqrt(np.mean(cols2[c] ** 2)))) if len(cols2[c]) else 0.0
        mid = y0 + alto_onda // 2
        d.line([(50 + c, mid - int(pk * alto_onda / 2)), (50 + c, mid + int(pk * alto_onda / 2))], fill=(70, 110, 160))
        d.line([(50 + c, mid - int(rm * alto_onda / 2)), (50 + c, mid + int(rm * alto_onda / 2))], fill=(150, 200, 255))
    total = len(mono) / SR
    for t, etiqueta in marcas:
        xx = 50 + int(t / total * ancho)
        d.line([(xx, 30), (xx, y0 + alto_onda)], fill=(255, 255, 255), width=1)
        d.text((xx + 3, 32), etiqueta, fill=(255, 255, 255), font=fuente)
    for s in range(0, int(total) + 1, 10):
        xx = 50 + int(s / total * ancho)
        d.line([(xx, y0 + alto_onda), (xx, y0 + alto_onda + 5)], fill=(160, 160, 170))
        if s % 30 == 0:
            d.text((xx - 8, y0 + alto_onda + 6), '%d:%02d' % (s // 60, s % 60), fill=(160, 160, 170), font=fuente)
    d.text((50, 8), titulo, fill=(235, 235, 240), font=fuente)
    lienzo.save(ruta)


# ======================================================================
#  Guardar, comprobar y revisar
# ======================================================================
def escribir_ogg(ruta, y, calidad):
    """Ogg Vorbis por bloques: libsndfile se cae si se le da todo de golpe."""
    with sf.SoundFile(ruta, 'w', SR, y.shape[1], subtype='VORBIS', format='OGG', compression_level=1.0 - calidad) as fh:
        for i in range(0, len(y), 32768):
            fh.write(y[i:i + 32768])


def guardar_pista(nombre, y, p, niveles, gmin, salida, revision=None, calidad=0.45):
    """Escribe el .ogg y lo vuelve a leer para medir lo que de verdad suena:
    duracion, picos, RMS, sonoridad y la costura del bucle."""
    ruta = os.path.join(salida, nombre + '.ogg')
    y = np.ascontiguousarray(y.T.astype(np.float32))
    for _ in range(4):
        escribir_ogg(ruta, y, calidad)
        z, sr2 = sf.read(ruta, dtype='float32', always_2d=True)
        pk = 20 * np.log10(np.max(np.abs(z)) + 1e-12)
        if pk <= -1.0:
            break
        y *= 10 ** ((-1.05 - pk) / 20)
    z = z.T.astype(np.float64)
    seg = z.shape[1] / SR
    rms = 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-12)
    salto = np.abs(z[:, 0] - z[:, -1]).max()
    tipico = np.percentile(np.abs(np.diff(z, axis=1)), 99.9)
    w = n_(0.5)
    antes = 20 * np.log10(np.sqrt(np.mean(z[:, -w:] ** 2)) + 1e-12)
    despues = 20 * np.log10(np.sqrt(np.mean(z[:, :w] ** 2)) + 1e-12)
    info = dict(archivo=ruta, segundos=seg, muestras=z.shape[1], esperado=p.L, compases=p.nc,
                pico_db=float(20 * np.log10(np.max(np.abs(z)) + 1e-12)), rms_db=float(rms), lufs=float(lufs(z)),
                mb=os.path.getsize(ruta) / 1e6, nan=bool(np.isnan(z).any()), recortes=int(np.sum(np.abs(z) >= 0.999)),
                salto_costura=float(salto), salto_tipico=float(tipico), rms_antes=float(antes), rms_despues=float(despues),
                limitador_db=float(20 * np.log10(gmin + 1e-12)))
    print('  %-7s %6.1f s (%d compases)  pico %.2f dBFS  rms %.1f dBFS  %.1f LUFS  %.2f MB  costura %.4f (tipico %.4f)  '
          '0,5 s antes/despues %.1f/%.1f dB  limitador %.1f dB' % (
              nombre, seg, p.nc, info['pico_db'], rms, info['lufs'], info['mb'], salto, tipico, antes, despues, info['limitador_db']),
          flush=True)
    if revision:
        os.makedirs(revision, exist_ok=True)
        marcas = [(p.t(c), s) for c, s in p.secciones]
        titulo = '%s  |  %d compases  %.1f s  |  pico %.1f dBFS  rms %.1f dBFS  %.1f LUFS' % (
            nombre, p.nc, seg, info['pico_db'], rms, info['lufs'])
        imagen_revision(z, os.path.join(revision, nombre + '_espectrograma.png'), titulo, marcas)
        q = n_(15.0)
        costura = np.concatenate([z[:, -q:], z[:, :q]], axis=1)
        sf.write(os.path.join(revision, nombre + '_costura.wav'), costura.T.astype(np.float32), SR, subtype='PCM_16')
        imagen_revision(costura, os.path.join(revision, nombre + '_costura.png'), nombre + ': ultimos 15 s + primeros 15 s (bucle)',
                        [(15.0, 'vuelta')], ancho=1200, alto=300)
        with open(os.path.join(revision, nombre + '_niveles.txt'), 'w', encoding='utf-8') as fh:
            for k, v in sorted(niveles.items(), key=lambda kv: -kv[1]):
                fh.write('%-14s %6.1f dB\n' % (k, v))
            for k, v in info.items():
                fh.write('%s: %s\n' % (k, v))
    return info


PISTAS = {}


def registrar(nombre, compositor, instrumentos, objetivo=-16.0):
    PISTAS[nombre] = (compositor, instrumentos, objetivo)


registrar('nerea', nerea, instrumentos_nerea, -16.0)


if __name__ == '__main__':
    RAIZ = sys.argv[1]
    REVISION = sys.argv[2] if len(sys.argv) > 2 else None
    SOLO = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/musica')
    os.makedirs(SALIDA, exist_ok=True)
    inicio = time.time()
    for nombre, (compositor, instrumentos, objetivo) in PISTAS.items():
        if SOLO and nombre not in SOLO:
            continue
        print(nombre, flush=True)
        _TABLAS.clear()
        _CACHE.clear()
        p = compositor()
        inst, salas = instrumentos()
        y, niveles, gmin = producir(p, inst, salas, objetivo=objetivo)
        guardar_pista(nombre, y, p, niveles, gmin, SALIDA, REVISION)
    print('listo en %.0f s' % (time.time() - inicio))
