"""
Musica de combate de los tres jefes de Atalaya. Compuesta como datos y
sintetizada desde cero: nada de samples, bancos de sonido ni descargas.
Cada pista es un BUCLE SIN COSTURA de un numero exacto de compases (estereo,
44100 Hz, Ogg Vorbis).

  NEREA, Guardiana de los Mares (nerea.ogg). Re menor con color dorico, 6/8
  a 66 negras con puntillo: pesada, majestuosa, de marea. 72 compases, 2:11.
      1-8   intro: el fondo del mar. Oleaje, el CORAZON maldito (lub-dub en
            bombo grave y timbal), cadenas, canto de ballena, arpa, campanas
            de cristal; entra el oleaje de los chelos y la llamada de trompas.
      9-24  A: el leitmotiv noble y tragico en las trompas (dos veces; la
            segunda con contracanto de violines y coro "oo" -> "oh").
      25-32 B1: el lamento de la sirena (soprano "oh/ah") sobre el arpa.
      33-40 B2: la maldicion crece. La cabeza del tema sube en secuencia
            sobre un bajo cromatico (re-mib-mi-fa-fa#-sol-sol#-la), tremolos,
            el corazon late dos veces por compas, timbal y platillo en redoble.
      41-56 A': tutti. Tema en trompas + trombones (octavas) + coro, violines
            con el contracanto y luego el tema una octava arriba.
      57-64 C: la maldicion (napolitano Mib contra Re menor), lamento de
            trompas, trombones que se hinchan, coro "ah", cadenas.
      65-72 la marea se retira: eco del tema y vuelta a la intro.

  AERALIS, Reina del Vendaval (aeralis.ogg). Mi menor con fa natural
  (frigio), 4/4 a 168: urgente, en vuelo. 88 compases, 2:06.
      1-8   intro: trueno, spiccato en semicorcheas (acento 3+3+2),
            corcheas graves, toms, acordes frigios de metales, subida.
      9-24  A: la flauta (seno con aliento y vibrato, con eco de ida y
            vuelta) "despega" en arpegios y sube en secuencias; la segunda
            vez con giro frigio, violines y contracanto de trompas.
      25-40 B: medio tiempo. El tema de la majestad en trompas y trombones,
            coro "ah", tremolos medidos como aleteos, truenos.
      41-48 C: sube la tormenta. Los despegues en secuencia sobre un bajo
            cromatico, redoble de caja y timbal, rachas.
      49-64 A': climax. Tema en flauta + violines + trompetas + trompas,
            contracanto de trombones, caja atras, truenos.
      65-80 D: el ojo de la tormenta (coro, celesta, flauta lenta, viento)
            y la vuelta del spiccato.  81-88 final que empuja al principio.

  RAJANG, el Jaguar de Jade (rajang.ogg). La menor (armonica y frigio
  dominante) con melodias pentatonicas, 4/4 a 132: tribal, pesada, antigua.
  80 compases, 2:25.
      1-8   intro: terremoto, grito y rugido de metales; dron como de
            didgeridoo (la boca mueve un formante en 3+3+2), sonajas,
            tambores de marco, tambor de tronco, llamada de la ocarina.
      9-24  A: el tema de la ocarina de barro (pentatonico, apoyaturas y
            trinos) sobre marimba y tronco; taikos, timbales graves y
            marcos entrelazados, un tambor en 3 contra 4; la segunda vez
            con la flauta de pan una octava abajo.
      25-40 B: el canto grave de hombres "oh" contestado por metales que
            rugen (Rem - Sib - Mi: frigio dominante), flauta de pan arriba.
      41-48 C: tambores y terremotos, gritos y rugidos.
      49-64 A': la furia de jade (ocarina + flauta de pan + trompas).
      65-72 D: el templo en silencio.  73-80 el jaguar vuelve (cabeza del
            tema en los metales graves, redobles hacia el principio).

COMO SE HACE
  - La musica son datos: notas con altura, inicio en pulsos, duracion,
    intensidad y articulacion (Partitura; las melodias se escriben como
    texto 'A3:2 D4:1 F4:3 | ...' y se comprueba que cada compas cuadre),
    acordes con conduccion de voces, patrones de percusion y curvas de
    dinamica. Se humaniza un poco el tiempo y la intensidad.
  - Cuerdas, metales, coro, flautas y el dron: osciladores de tabla con el
    espectro de cada nota (armonicos con su envolvente en Hz: cuerpo del
    violin, formantes de vocal, boca del didgeridoo), limitados en banda y
    con filas de brillo (abrir el filtro con la intensidad, la vocal u->a).
    Varias voces desafinadas con vibrato que entra tarde, portamento,
    ataque de lengua o arco, golpe de brillo y subida de tono en el metal.
  - Arpa por Karplus-Strong; marimba, tronco y celesta modales; campanas de
    cristal en FM; tambores con tono que cae y ruido de piel; truenos,
    terremotos, cadenas, ballenas, viento y oleaje con ruido filtrado.
  - Mezcla: buses con paneo, ecualizacion y envios a salas de convolucion
    (respuestas estereo de ruido que decae por bandas) y a un eco de ida y
    vuelta a tempo.
  - Bucle: se renderiza el bucle mas una cola de 10 s y la cola se suma al
    principio. Todo lo que va despues (graves al centro, filtro, compresor,
    limitador) es circular: el final entra en el principio sin chasquido.
  - Master: sonoridad integrada (BS.1770) a -15,5 / -16 LUFS, compresor
    suave que solo toca lo mas fuerte, limitador con techo -1,3 dBFS. Se
    vuelve a leer el .ogg para medir picos, RMS, LUFS y la costura.

Escribe src/main/resources/assets/atalaya/sounds/musica/{nerea,aeralis,
rajang}.ogg. NO toca sounds.json: los eventos de musica se dan de alta aparte
(conviene "stream": true).

Uso: python musica_jefes.py <raiz del proyecto> [carpeta_de_revision] [pista,...]
  - carpeta_de_revision: por pista, espectrograma y forma de onda en PNG,
    los ultimos 15 s + los primeros 15 s en WAV (para oir la costura) y los
    niveles de cada bus.
  - pista: solo esas (nerea, aeralis, rajang).
  - Con MEDIR=1 en el entorno imprime niveles por seccion y por bandas.
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import os, re, sys, time

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
    __slots__ = ('t', 'd', 'm', 'v', 'art', 'lig', 'frase', 'vocal', 'bend', 'trino', 'pan', 'gl')

    def __init__(self, t, d, m, v=0.7, art='leg', lig=True, frase=None, vocal=0.0, bend=0.0, trino=0.0, pan=0.0, gl=0.0):
        self.t, self.d, self.m, self.v, self.art, self.lig = t, d, m, v, art, lig
        self.frase, self.vocal, self.bend, self.trino, self.pan, self.gl = frase, vocal, bend, trino, pan, gl


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
        if nt.gl:
            m += nt.gl * np.clip((tc - s) / max(nt.d, 1e-3), 0, 1) ** 1.6
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
        y = leer_trozos(tabla(tm, n0.m + max(0.0, n0.gl), P['B']), fase, bri)
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
    if P.get('am'):
        ar, ad = P['am']
        vida = vida * (1 + ad * np.sin(2 * np.pi * ar * rng.uniform(0.94, 1.06, V)[:, None] * tc + rng.uniform(0, 6.3, (V, 1))))
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


def tom(f_base=110.0, fuerza=2, variante=0, tau=0.24):
    return tambor(f_base, tau, fuerza, variante, 0.65, 0.025, (150, 1500, 0.45, 0.05), (1200, 5000, 0.3, 0.006), (1.5, 0.3, 0.09))


def bombo_seco(fuerza=2, variante=0):
    """Bombo grande pero corto, para tempos rapidos: pega y deja sitio."""
    return tambor(54.0, 0.2, fuerza, variante, 1.1, 0.022, (70, 900, 0.6, 0.04), (900, 4000, 0.35, 0.006), (1.6, 0.3, 0.07), dur=1.0)


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
    y += bp(rng.standard_normal(N), 1600, 7500) * np.exp(-t / 0.1) * (0.55 + 0.15 * fuerza)
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
    lub = pico_(tambor(54.0, 0.28, 3, 0, 0.8, 0.03, (70, 700, 0.9, 0.05), (500, 2200, 0.3, 0.012), (1.52, 0.4, 0.09)), 1.0)
    dub = pico_(tambor(62.0, 0.2, 2, 1, 0.7, 0.025, (90, 900, 0.9, 0.04), (600, 2500, 0.3, 0.01), (1.52, 0.4, 0.07)), 0.72)
    sep = n_(0.2)
    y = np.zeros(max(len(lub), sep + len(dub)))
    y[:len(lub)] += lub
    y[sep:sep + len(dub)] += dub
    return pb(y, 2200) * fuerza


def periodica(n, f_lo, f_hi, semilla, componentes=24):
    """Curva lenta al azar (desviacion ~1) que se repite exacta cada n
    muestras: rachas, oleaje y temblores que no saltan en el bucle."""
    r = np.random.default_rng(semilla)
    T = n / SR
    k_lo, k_hi = max(1, int(f_lo * T)), max(2, int(f_hi * T))
    ks = r.integers(k_lo, k_hi + 1, componentes)
    paso_ = 64
    t = np.arange(0, n + paso_, paso_) / n
    y = np.zeros(len(t))
    for k in ks:
        y += np.sin(2 * np.pi * k * t + r.uniform(0, 2 * np.pi)) / np.sqrt(k)
    y = np.interp(np.arange(n) / n, t, y)
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
        h *= paso(t / densidad)
        pd = n_(predelay)
        h = np.concatenate([np.zeros(pd), h[:n - pd]])
        for k in range(tempranas):
            d = n_(predelay * 0.3 + r.uniform(0.004, 0.075))
            h[d] += r.choice([-1, 1]) * r.uniform(0.3, 1.0) * 4.0 * np.exp(-d / SR / 0.05)
        h = pb(h, oscuro)
        out.append(h / np.sqrt(np.sum(h ** 2)))
    return np.array(out, dtype=np.float32)


def curva_db(puntos, muestras_compas, n):
    """Automatizacion: [(compas (desde 1, con decimales), dB), ...] a una
    ganancia lineal por muestra."""
    xs = np.array([(p[0] - 1) * muestras_compas for p in puntos], dtype=float)
    ys = np.array([p[1] for p in puntos], dtype=float)
    idx = np.arange(n, dtype=float)
    return (10 ** (np.interp(idx, xs, ys) / 20)).astype(np.float32)


class Mezcla:
    def __init__(self, n, salas, tramos=None):
        self.n = n
        self.mix = np.zeros((2, n), dtype=np.float32)
        self.salas = salas
        self.envios = {k: np.zeros((2, n), dtype=np.float32) for k in salas}
        self.niveles = {}
        self.tramos = tramos or []
        self.por_tramo = {}

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
        self.niveles[nombre] = 10 * np.log10(np.einsum('ij,ij->', x, x, dtype=np.float64) / x.size + 1e-18)
        self.por_tramo[nombre] = [10 * np.log10(np.einsum('ij,ij->', x[:, a:b], x[:, a:b], dtype=np.float64) / max(1, x[:, a:b].size) + 1e-18)
                                  for a, b, _ in self.tramos]

    def cerrar(self):
        for k, ir in self.salas.items():
            e = self.envios[k]
            if not np.any(e):
                continue
            e = pa(e, 170, 2).astype(np.float32)
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


def graves_al_centro(x, corte=120.0):
    """Por debajo de `corte` todo al centro (fase cero y circular: el bucle
    no nota el filtro). Arriba queda igual: la suma reconstruye exacto."""
    pad = n_(2.0)
    xp = np.pad(x, ((0, 0), (pad, pad)), mode='wrap')
    g = signal.sosfiltfilt(signal.butter(2, corte, 'low', fs=SR, output='sos'), xp, axis=-1)[:, pad:-pad]
    mono = 0.5 * (g[0] + g[1])
    return x - g + mono[None, :]


def master(x, objetivo_lufs=-16.0, techo_db=-1.3):
    """Graves al centro, canales equilibrados, sonoridad al objetivo,
    pegamento que solo toca lo mas fuerte (umbral relativo a la media, asi se
    conserva el arco de dinamica), una pizca de saturacion y el limitador."""
    x = _circular(lambda z: pa(z, 28, 2), graves_al_centro(x), n_(3.0))
    rl, rr = np.sqrt(np.mean(x[0] ** 2)), np.sqrt(np.mean(x[1] ** 2))
    corr = np.clip(np.sqrt(rr / rl), 10 ** (-0.5 / 20), 10 ** (0.5 / 20))
    x = x * np.array([[corr], [1.0 / corr]])
    x = x * 10 ** ((objetivo_lufs - lufs(x)) / 20)
    media = 10 * np.log10(np.mean(x ** 2) + 1e-12)
    x = compresor(x, umbral_db=media + 4.0, ratio=2.0, rodilla=8.0, t_det=0.06, t_gan=0.35)
    for _ in range(4):
        x = x * 10 ** ((objetivo_lufs - lufs(x)) / 20)
        y, gmin = limitador(np.tanh(x * 1.1) / 1.1, techo_db)
        error = objetivo_lufs - lufs(y)
        if abs(error) < 0.1:
            break
        x = x * 10 ** (error / 20)
    return y, gmin

# ======================================================================
#  Partitura: la musica escrita como datos
# ======================================================================
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

    def respiro(self, puntos, compas, fraccion=0.125, hondo=-11.0):
        """Corte de toda la mezcla justo antes del tiempo fuerte de `compas`
        (la ultima `fraccion` del compas anterior): el tutti cae con mas peso."""
        base = float(np.interp(compas, [q[0] for q in puntos], [q[1] for q in puntos]))
        nuevos = [(compas - fraccion - 0.03, base), (compas - fraccion + 0.01, base + hondo),
                  (compas - 0.012, base + hondo), (compas, base)]
        return sorted([q for q in puntos if not (compas - fraccion - 0.03 <= q[0] <= compas)] + nuevos)


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


def informe(mz, mezcla, tramos):
    """MEDIR=1: nivel de cada bus por seccion y reparto por bandas de la mezcla."""
    print('  %-12s' % 'bus' + ''.join('%11s' % nom[:10] for _, _, nom in tramos))
    for k, v in mz.por_tramo.items():
        print('  %-12s' % k + ''.join('%11.1f' % x for x in v))
    bandas = [(30, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000), (8000, 16000)]
    print('  %-12s' % 'banda(Hz)' + ''.join('%11s' % nom[:10] for _, _, nom in tramos))
    for lo, hi in bandas:
        fila = []
        for a, b, _ in tramos:
            seg = mezcla[:, a:b].mean(axis=0)[:2 ** 21]
            X = np.abs(np.fft.rfft(seg)) ** 2
            f = np.fft.rfftfreq(len(seg), 1 / SR)
            fila.append(10 * np.log10(X[(f >= lo) & (f < hi)].sum() / X.sum() + 1e-12))
        print('  %-12s' % ('%d-%d' % (lo, hi)) + ''.join('%11.1f' % x for x in fila))
    print('  %-12s' % 'total' + ''.join('%11.1f' % (10 * np.log10(np.mean(mezcla[:, a:b].astype(np.float64) ** 2) + 1e-18))
                                        for a, b, _ in tramos))


def producir(p, inst, salas, cola=10.0, objetivo=-16.0):
    """inst: nombre -> dict(tipo='frase'|'golpe'|'nota_golpe'|'lecho', ...).
    Toca cada instrumento en su bus, mezcla, pliega el bucle y masteriza."""
    t0 = time.time()
    n = p.L + n_(cola)
    cortes = [c for c, _ in p.secciones] + [p.nc + 1]
    tramos = [(int(round(p.t(c) * SR)), int(round(p.t(d) * SR)), nom) for (c, nom), d in zip(p.secciones, cortes[1:])]
    mz = Mezcla(n, salas, tramos)
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
                if np.ndim(x) == 2:
                    poner(bus, np.asarray(x, dtype=np.float32) * v, t, p.L)
                    continue
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
    if os.environ.get('MEDIR'):
        informe(mz, mezcla, tramos)
    bucle = plegar(mezcla, p.L)
    if '_mezcla' in p.auto:
        # el fader general va despues de plegar: las colas que dan la vuelta
        # reciben la misma ganancia que el sitio donde suenan
        bucle *= curva_db(p.auto['_mezcla'], p.mc, p.L)
    final, gmin = master(bucle, objetivo)
    if os.environ.get('MEDIR'):
        print('  %-12s' % 'LUFS final' + ''.join('%11.1f' % lufs(final[:, a:min(b, p.L)]) for a, b, _ in tramos))
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
#  Sonidos de los elementos: agua, viento y tierra (todo afinado o sin
#  agudos: que se oiga el elemento sin ruido de fondo constante)
# ======================================================================
def t_seno(k, fk, b):
    return np.where(k == 1, 1.0, 0.0)


def t_armonica(k, fk, b):
    """Armonica de cristal: copas frotadas, casi un seno puro."""
    return np.where(k == 1, 1.0, np.where(k == 2, 0.05 + 0.08 * b, np.where(k == 3, 0.025 * b, 0.0)))


def t_silbato(k, fk, b):
    """Silbato de madera: el fundamental y un poco de los primeros armonicos."""
    return np.where(k == 1, 1.0, np.where(k == 2, 0.04 + 0.08 * b, np.where(k == 3, 0.03 + 0.05 * b, 0.0)))


def respuesta_eco(retardo, repeticiones=6, caida=0.55, oscuro=5000.0):
    """Eco de ida y vuelta (izquierda, derecha...) como respuesta al impulso:
    la convolucion lo hace igual que una reverb, y da la vuelta al bucle."""
    n = n_(retardo * (repeticiones + 1)) + 1
    h = np.zeros((2, n))
    for k in range(1, repeticiones + 1):
        h[(k + 1) % 2, n_(retardo * k)] = caida ** k
    h = pb(h, oscuro)
    return (h / np.max(np.abs(h))).astype(np.float32)


# ---------------------------------------------------------------- agua
@cacheado
def gota(m, fuerza=2, variante=0):
    """Gota afinada: una burbuja que nace un poco grave y sube a su nota
    (como las de verdad al soltarse) y se apaga enseguida. A veces deja
    otra burbujita detras, una quinta arriba."""
    f = float(hz(m))
    N = n_(0.9)
    t = np.arange(N) / SR
    ph = 2 * np.pi * f * np.cumsum(1 - 0.28 * np.exp(-t / 0.025)) / SR
    tau = float(np.clip(0.22 * (523.0 / f) ** 0.4, 0.08, 0.35))
    y = np.sin(ph) * np.exp(-t / tau) + 0.1 * np.sin(2 * ph + 0.5) * np.exp(-t / (tau * 0.4))
    if variante % 2 == 1:
        d = n_(rng.uniform(0.05, 0.09))
        ph2 = 2 * np.pi * 1.5 * f * np.cumsum(1 - 0.3 * np.exp(-t[:N - d] / 0.02)) / SR
        y[d:] += 0.28 * np.sin(ph2) * np.exp(-t[:N - d] / (tau * 0.6))
    y *= caida(N, 10.0, 0.0015)
    return y / (np.max(np.abs(y)) + 1e-9)


def ola(dur=4.0, pan0=-0.6, pan1=0.6, cresta=0.55, brillo=1.0):
    """Una ola: ruido rosa que crece abriendose (la cresta suena mas clara),
    rompe y se retira, y cruza el estereo de un lado al otro. Sin siseo:
    nada por encima de unos 2,5 kHz."""
    N = n_(dur)
    t = np.arange(N) / SR
    u = t / dur
    x = ruido(N, 'rosa')
    forma = np.where(u < cresta, (u / cresta) ** 2, np.exp(-(u - cresta) / max(1e-3, 1 - cresta) * 3.2))
    forma = forma * paso((1 - u) / 0.1) * paso(u / 0.02)
    y = (pb(x, 260, 2) * forma * (0.55 + 0.45 * forma) + bp(x, 260, 900) * forma ** 1.6 * 0.6 * brillo
         + bp(x, 900, 2400) * forma ** 3 * 0.25 * brillo)
    pan = pan0 + (pan1 - pan0) * paso(u)
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    st = np.vstack([y * np.cos(th), y * np.sin(th)])
    return st / (np.max(np.abs(st)) + 1e-9)


# ---------------------------------------------------------------- viento
@cacheado
def campanilla(m, fuerza=2, variante=0):
    """Campanilla de viento: un tubo de metal colgado (modos de barra libre),
    golpe blando y una cola larga que bate despacio."""
    f = float(hz(m))
    N = n_(3.6)
    t = np.arange(N) / SR
    y = np.zeros(N)
    for r, a, tau in ((1.0, 1.0, 2.2), (2.756, 0.3, 0.9), (5.404, 0.08, 0.35), (8.933, 0.025, 0.15)):
        if f * r < 11000:
            y += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6)) * np.exp(-t / tau)
    y += 0.25 * np.sin(2 * np.pi * f * 1.0025 * t + 1.3) * np.exp(-t / 2.0)
    y *= caida(N, 10.0, 0.002)
    return y / (np.max(np.abs(y)) + 1e-9)


def rafaga_st(dur=2.5, f0=400.0, f1=2400.0, pan0=-0.8, pan1=0.8):
    """Racha que cruza el estereo: la banda sube y baja y el viento pasa de
    un lado al otro."""
    y = rafaga(dur, f0, f1)
    u = np.arange(len(y)) / len(y)
    th = (np.clip(pan0 + (pan1 - pan0) * paso(u), -1, 1) + 1) * np.pi / 4
    return np.vstack([y * np.cos(th), y * np.sin(th)])


def rafaga(dur=2.5, f0=400.0, f1=3000.0):
    """Racha de viento: ruido en una banda que sube y vuelve a bajar, que
    crece y se apaga (banco de bandas que se cruzan)."""
    N = n_(dur)
    t = np.arange(N) / SR
    x = rng.standard_normal(N)
    forma = np.sin(np.pi * t / dur) ** 1.5
    centro = f0 * (f1 / f0) ** forma
    y = np.zeros(N)
    for fc in np.geomspace(min(f0, f1) / 1.2, max(f0, f1) * 1.2, 6):
        w = np.exp(-0.5 * (np.log2(centro / fc) / 0.5) ** 2)
        y += bp(x, fc / 1.4, fc * 1.4) * w
    y *= forma * (1 + 0.3 * np.sin(2 * np.pi * 3.1 * t + rng.uniform(0, 6)))
    return y / (np.max(np.abs(y)) + 1e-9)


def trueno_lejano(dur=5.0):
    """Trueno lejano: solo el retumbo grave que rueda, sin chasquido."""
    N = n_(dur)
    t = np.arange(N) / SR
    x = ruido(N, 'marron')
    env = np.zeros(N)
    for k in range(4):
        c = rng.uniform(0.0, 0.4) + k * dur * 0.17
        env += rng.uniform(0.5, 1.0) * np.exp(-np.maximum(0, t - c) / (dur * 0.22)) * paso((t - c) / 0.35)
    y = pb(x, 150, 2) * env + 0.25 * bp(x, 150, 450) * env ** 2
    y *= paso((dur - t) / 0.6)
    return y / (np.max(np.abs(y)) + 1e-9)


# ---------------------------------------------------------------- tierra
@cacheado
def kalimba(m, fuerza=2, variante=0):
    """Kalimba: una lengueta de metal sobre una caja de madera. Fundamental
    larga, el segundo modo de la lengueta (x6,27) que se apaga enseguida,
    el golpe del pulgar y el cuerpo de la caja."""
    f = float(hz(m))
    tau = float(np.clip(1.5 * (440.0 / f) ** 0.35, 0.6, 2.2))
    N = n_(tau * 4)
    t = np.arange(N) / SR
    ph = 2 * np.pi * f * np.cumsum(1 + 0.004 * np.exp(-t / 0.02)) / SR
    y = np.sin(ph) * np.exp(-t / tau)
    if 6.27 * f < 12000:
        y += (0.14 + 0.06 * fuerza) * np.sin(6.27 * ph + 0.3) * np.exp(-t / (tau / 9))
    if 17.55 * f < 12000:
        y += 0.04 * np.sin(17.55 * ph + 1.1) * np.exp(-t / (tau / 30))
    y += pb(rng.standard_normal(N), 1800) * np.exp(-t / 0.004) * 0.2
    y += resonar_bp(rng.standard_normal(N), 220, 4.0) * np.exp(-t / 0.03) * 0.12
    y *= caida(N, 10.0, 0.0012)
    return y / (np.max(np.abs(y)) + 1e-9)


@cacheado
def piedra(fuerza=2, variante=0):
    """Dos piedras que chocan: un clic seco con un poco de cuerpo."""
    N = n_(0.12)
    t = np.arange(N) / SR
    y = np.zeros(N)
    for _ in range(3):
        y += rng.uniform(0.4, 1.0) * np.sin(2 * np.pi * rng.uniform(1500, 3000) * t + rng.uniform(0, 6)) * np.exp(-t / rng.uniform(0.005, 0.011))
    y += 0.7 * np.sin(2 * np.pi * rng.uniform(260, 400) * t) * np.exp(-t / 0.012)
    y += bp(rng.standard_normal(N), 1000, 4500) * np.exp(-t / 0.002) * 0.4
    y *= caida(N, 10.0, 0.0004)
    return pb(y / (np.max(np.abs(y)) + 1e-9), 5500)


def retumbo(dur=5.0, f_sub=32.7):
    """Retumbo de la tierra: un subgrave afinado que crece y se va, con un
    poco de ruido muy grave debajo (nada de agudos)."""
    N = n_(dur)
    t = np.arange(N) / SR
    env = np.sin(np.pi * t / dur) ** 1.5
    sub_ = np.sin(2 * np.pi * f_sub * t + 0.3 * np.sin(2 * np.pi * 0.7 * t)) + 0.3 * np.sin(4 * np.pi * f_sub * t)
    rr = pb(ruido(N, 'marron'), 90, 2)
    y = (0.75 * sub_ + 0.35 * rr / (np.std(rr) + 1e-9)) * env
    return y / (np.max(np.abs(y)) + 1e-9)


def semillas(dur=0.6, subida_=True):
    """Sonaja de semillas que se agita cada vez mas (o una sacudida larga)."""
    N = n_(dur)
    t = np.arange(N) / SR
    env = (t / dur) ** 2 if subida_ else np.sin(np.pi * t / dur) ** 1.2
    agite = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 9.0 * t))
    clics = (rng.random(N) < 0.22 * env * agite) * rng.uniform(0.2, 1.0, N)
    y = bp(clics, 2000, 7000, 2) + 0.15 * bp(rng.standard_normal(N), 2000, 6000) * env
    fin = n_(0.01)
    y[-fin:] *= np.linspace(1, 0, fin)
    return y / (np.max(np.abs(y)) + 1e-9)


def raiz_timbal(acorde):
    """La fundamental del acorde en la octava de los timbales (La1 a Sol#2)."""
    pc = _pcs(acorde)[0]
    return 33 + (pc - 9) % 12


def _nombre(m):
    nombres = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    return '%s%d' % (nombres[m % 12], m // 12 - 1)



# ======================================================================
#  NEREA, Guardiana de los Mares. Re menor (dorico a ratos), 6/8 a 66.
#  Todo suena a agua: arpa, celesta, armonica de cristal, gotas afinadas,
#  olas, cantos de ballena y un coro sin palabras.
# ======================================================================
NEREA_AC = {
    # acorde: (raiz grave, ola de chelos, voces centrales, notas del acorde)
    'Dm': ('D2', 'D2 A2 D3 F3 D3 A2', 'D4 F4 A4', 'D F A'),
    'Bb': ('Bb1', 'F2 Bb2 D3 F3 D3 Bb2', 'D4 F4 Bb4', 'Bb D F'),
    'Bb/D': ('D2', 'D2 Bb2 D3 F3 D3 Bb2', 'D4 F4 Bb4', 'Bb D F'),
    'Gm': ('G1', 'D2 G2 Bb2 D3 Bb2 G2', 'D4 G4 Bb4', 'G Bb D'),
    'A': ('A1', 'E2 A2 C#3 E3 C#3 A2', 'C#4 E4 A4', 'A C# E'),
    'A7': ('A1', 'E2 A2 C#3 G3 C#3 A2', 'C#4 G4 A4', 'A C# E G'),
    'F': ('F1', 'C2 F2 A2 C3 A2 F2', 'C4 F4 A4', 'F A C'),
    'Eb': ('Eb2', 'Eb2 Bb2 Eb3 G3 Eb3 Bb2', 'Eb4 G4 Bb4', 'Eb G Bb'),
    'C/E': ('E2', 'E2 G2 C3 E3 C3 G2', 'C4 E4 G4', 'C E G'),
    'D/F#': ('F#1', 'F#2 A2 D3 F#3 D3 A2', 'D4 F#4 A4', 'D F# A'),
    'E/G#': ('G#1', 'G#2 B2 E3 G#3 E3 B2', 'E4 G#4 B4', 'E G# B'),
}

NEREA_TEMA = ("A3:2 D4:1 F4:3 | G4:2 F4:1( D4:3 | D4:2 G4:1 Bb4:3 | A4:2 G4:1( E4:3",
              "A3:2 D4:1 A4:3 | G4:2 F4:1( D5:3 | C5:2 Bb4:1( A4:2 G4:1( | F4:2 E4:1( D4:3")
NEREA_CONTRA = "A5:3 G5:2 F5:1 | F5:3 G5:2 A5:1 | Bb5:3 A5:2 G5:1 | A5:3 G5:2 E5:1 | F5:3 E5:2 D5:1 | D5:3 E5:2 F5:1 | G5:3 A5:3 | A5:6"


def nerea():
    global rng
    rng = np.random.default_rng(20261008)
    p = Partitura('nerea', 68, 6, 60.0 / 66 / 3)
    AC = NEREA_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c if isinstance(c, tuple) else (c,)
    tema_ac = ['Dm', 'Bb', 'Gm', 'A7', 'Dm', 'Bb', ('Gm', 'A7'), 'Dm']
    armonia(1, ['Dm', 'Dm', 'Bb/D', 'Dm', 'Dm', 'Bb', 'Gm', 'A', 'Dm', 'A'])
    armonia(11, tema_ac * 2)
    armonia(27, ['Dm', 'Eb', 'C/E', 'F', 'D/F#', 'Gm', 'E/G#', 'A', 'A', 'A'])
    armonia(37, tema_ac * 2 + ['Bb', 'A', 'Dm', 'Dm'])
    armonia(57, ['Dm', 'Bb', 'Gm', 'A'] * 3)

    def trozos(c):
        a = arm[c]
        return [(0, 6, a[0])] if len(a) == 1 else [(0, 3, a[0]), (3, 3, a[1])]

    def rodar(c0, c1, v0, v1=None, art='leg'):
        """Chelos: el oleaje, arpegio que sube y baja en cada compas."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                notas = AC[ch][1].split()[:dur]
                for k, nm in enumerate(notas):
                    acento = art if k % 3 else ('acc' if art == 'leg' else art)
                    p.nota('chelos', nm, c, pos + k, 1.3, v * (1.0, 0.74, 0.82, 0.96, 0.76, 0.8)[k], acento)

    def bajos(c0, c1, v0, v1=None, art='swell', inst='contrabajos', pulso=False):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                if pulso:
                    for k in range(0, dur, 3):
                        p.nota(inst, AC[ch][0], c, pos + k, 3, v * (1.0 if pos + k == 0 else 0.8), 'acc' if pos + k == 0 else 'leg')
                else:
                    p.nota(inst, AC[ch][0], c, pos, dur, v, art)

    def arpa_ola(c0, c1, v0, v1=None, paso_=1.0, desde='D4', inst='arpa'):
        """El arpa como agua que corre: arpegio que sube y vuelve a bajar."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos, dur, ch in trozos(c):
                cuantas = int(round(dur / paso_))
                arriba = subir(_pcs(AC[ch][3]), midi(desde), cuantas // 2 + 1 + (1 if paso_ < 1 else 0))
                figura = arriba + arriba[-2:0:-1]
                for k in range(cuantas):
                    m = figura[k % len(figura)]
                    p.nota(inst, m, c, pos + k * paso_, paso_, v * (0.78 + 0.22 * (m - midi(desde)) / 24.0))

    def gotas(c0, c1, v, por_compas=2):
        """Gotas afinadas: notas del acorde que caen al agua aqui y alla."""
        for c in range(c0, c1 + 1):
            for pos, dur, ch in trozos(c):
                opciones = subir(_pcs(AC[ch][3]), midi('A5'), 5)
                for k in range(max(1, int(round(por_compas * dur / 6)))):
                    pp = pos + rng.choice([0.5, 1.0, 1.5, 2.0, 3.5, 4.0, 4.5]) * dur / 6
                    p.nota('gotas', int(rng.choice(opciones)), c, pp, 1, v * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.7, 0.7))

    def pads(inst, c0, c1, vel, vocal=0.0, transp=0, art='leg'):
        acordes = []
        for c in range(c0, c1 + 1):
            for pos, dur, ch in trozos(c):
                texto = AC[ch][2]
                if transp:
                    texto = ' '.join(_nombre(midi(x) + transp) for x in texto.split())
                acordes.append((c, pos, dur, texto))
        ligar_acordes(p, inst, acordes, vel, art, vocal=vocal)

    def subgrave(c0, c1, v):
        for c in range(c0, c1 + 1):
            for pos, dur, ch in trozos(c):
                r = midi(AC[ch][0])
                p.nota('sub', r + (12 if r < midi('C2') else 0), c, pos, dur, v, 'swell')

    def corazon(c0, c1, v0, v1=None, por_compas=1):
        """El corazon maldito en los timbales: lub (re) - dub (la), afinado."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for pos in ((0,) if por_compas == 1 else (0, 3)):
                p.nota('timbales', 'D2', c, pos, 1, v)
                p.nota('timbales', 'A1', c, pos + 0.66, 1, v * 0.72)

    def redoble(c, pos, dur, m, v0, v1, ritmo=0.075):
        t = 0.0
        k = 0
        while t < dur * p.u - 0.02:
            p.nota('timbales', m, c, pos + t / p.u, 0.5, (v0 + (v1 - v0) * t / (dur * p.u)) * (0.85 + 0.15 * (k % 2)))
            t += ritmo * (1 + 0.08 * rng.standard_normal())
            k += 1

    def olas(lista, v):
        for i, c in enumerate(lista):
            a, b = (-0.7, 0.6) if i % 2 == 0 else (0.7, -0.6)
            p.golpe('olas', c, 0, v, dur=4.2, pan0=a, pan1=b)

    # ------------------------------------------------ INTRO (1-10): el fondo del mar
    p.seccion(1, 'intro')
    olas([1, 3, 5, 7, 9], 0.55)
    p.golpe('ballena', 1, 2, 0.75, dur=6.0, puntos=[(0, 73.4), (0.4, 110.0), (1, 87.3)], brillo=170.0, pan=-0.3)
    p.golpe('ballena', 6, 0, 0.65, dur=5.5, puntos=[(0, 110.0), (0.5, 146.8), (1, 130.8)], brillo=200.0, pan=0.35)
    p.nota('sub', 'D2', 1, 0, 24, 0.55, 'swell')
    subgrave(5, 10, 0.45)
    arpa_ola(1, 10, 0.3, 0.4)
    gotas(3, 10, 0.42, 2)
    p.melodia('armonica', 'mp ' + NEREA_TEMA[0], 5, transp=12)
    pads('coro', 8, 10, 0.3, vocal=0.0)
    corazon(9, 10, 0.3, 0.38)
    for k, nm in enumerate(['A4', 'C#5', 'E5', 'A5', 'C#6', 'E6']):
        p.nota('celesta', nm, 10, 1 + 0.75 * k, 1, 0.35 + 0.05 * k)

    # ------------------------------------------------ A (11-26): el tema, como agua
    p.seccion(11, 'tema')
    p.melodia('armonica', 'mf ' + NEREA_TEMA[0], 11, transp=12)
    p.melodia('armonica', 'mf ' + NEREA_TEMA[1], 15, transp=12)
    p.melodia('coro_tema', 'mp ' + NEREA_TEMA[0], 11, vocal=0.0)
    p.melodia('coro_tema', 'mp ' + NEREA_TEMA[1], 15, vocal=0.0)
    p.melodia('trompas', 'mp ' + NEREA_TEMA[0], 19, lig=False)
    p.melodia('trompas', 'mf ' + NEREA_TEMA[1], 23, lig=False)
    p.melodia('coro_tema', 'mf ' + NEREA_TEMA[0], 19, vocal=0.35)
    p.melodia('coro_tema', 'mf ' + NEREA_TEMA[1], 23, vocal=0.45)
    p.melodia('celesta', 'mp ' + NEREA_TEMA[0], 19, transp=12)
    p.melodia('celesta', 'mp ' + NEREA_TEMA[1], 23, transp=12)
    p.melodia('violines', 'mp ' + NEREA_CONTRA, 19)
    arpa_ola(11, 18, 0.4, 0.42)
    arpa_ola(19, 26, 0.38, 0.45, paso_=0.5)
    for c in range(11, 19):
        for pos, dur, ch in trozos(c):
            p.nota('chelos', AC[ch][1].split()[1], c, pos, dur, 0.3, 'swell')
    rodar(19, 26, 0.45, 0.6)
    bajos(11, 26, 0.38, 0.55, pulso=True)
    pads('coro', 11, 18, 0.3, vocal=0.0)
    pads('coro', 19, 26, 0.36, vocal=0.3)
    pads('violas', 11, 26, 0.24, transp=-12)
    corazon(11, 26, 0.36, 0.5)
    gotas(11, 26, 0.36, 1)
    olas([11, 15, 19, 23], 0.42)
    p.golpe('ballena', 14, 3, 0.55, dur=5.0, puntos=[(0, 87.3), (0.5, 116.5), (1, 110.0)], brillo=200.0, pan=0.4)
    p.golpe('ballena', 22, 0, 0.5, dur=5.0, puntos=[(0, 73.4), (0.4, 98.0), (1, 87.3)], brillo=180.0, pan=-0.4)

    # ------------------------------------------------ B (27-36): sube la marea
    p.seccion(27, 'crece')
    secuencia = ['A3:2 D4:1 F4:3', 'Bb3:2 Eb4:1 G4:3', 'C4:2 E4:1 G4:3', 'C4:2 F4:1 A4:3',
                 'D4:2 F#4:1 A4:3', 'D4:2 G4:1 Bb4:3', 'E4:2 G#4:1 B4:3', 'E4:2 A4:1 C#5:3']
    for i, frag in enumerate(secuencia):
        v = 0.48 + 0.42 * i / 7
        p.melodia('trompas', frag, 27 + i, vel=v, lig=False)
        p.melodia('coro_tema', frag, 27 + i, vel=v * 0.9, vocal=0.3 + 0.5 * i / 7)
        if i >= 4:
            p.melodia('trombones', frag, 27 + i, vel=v, transp=-12, lig=False)
    p.acorde('trompas', 'E4 A4 C#5', 35, 0, 12, 0.8, 'cresc')
    p.acorde('trombones', 'A2 E3 A3', 35, 0, 12, 0.8, 'cresc')
    p.nota('tuba', 'A1', 35, 0, 12, 0.75, 'cresc')
    pads('coro', 27, 36, 0.42, vocal=0.5)
    for c in range(27, 37):
        for pos, dur, ch in trozos(c):
            for nm in subir(_pcs(AC[ch][3]), midi('D5'), 3):
                p.nota('violines', nm, c, pos, dur, 0.3 + 0.45 * (c - 27) / 9, 'trem')
    rodar(27, 34, 0.58, 0.85)
    p.nota('chelos', 'A2', 35, 0, 12, 0.7, 'cresc')
    p.nota('chelos', 'E3', 35, 0, 12, 0.6, 'cresc')
    bajos(27, 34, 0.5, 0.75, art='marc', pulso=True)
    p.nota('contrabajos', 'A1', 35, 0, 12, 0.75, 'cresc')
    corazon(27, 34, 0.5, 0.8, por_compas=2)
    redoble(35, 0, 12, 'A1', 0.25, 1.0)
    arpa_ola(27, 36, 0.42, 0.55, paso_=0.5)
    olas([27, 29, 31, 33], 0.62)
    p.golpe('olas', 35, 0, 0.85, dur=12 * p.u, pan0=-0.2, pan1=0.2, cresta=0.97)
    p.nota('sub', 'A1', 35, 0, 12, 0.6, 'cresc')
    p.automatizar('coro', [(1, 0), (27, -3), (36.9, 3), (37, 0), (69, 0)])

    # ------------------------------------------------ C (37-56): la ola gigante
    p.seccion(37, 'CLIMAX')
    p.golpe('olas', 37, 0, 1.0, dur=5.5, pan0=0.0, pan1=0.0, cresta=0.05, brillo=1.25)
    p.golpe('olas', 45, 0, 0.8, dur=5.0, pan0=0.3, pan1=-0.3, cresta=0.05, brillo=1.15)
    olas([41, 49], 0.6)
    p.nota('timbales', 'D2', 37, 0, 2, 1.0)
    p.golpe('bombo', 37, 0, 1.0)
    p.acorde('trombones', 'D2 A2 D3', 37, 0, 3, 1.0, 'fp')
    p.nota('tuba', 'D2', 37, 0, 3, 1.0, 'fp')
    p.acorde('coro', 'D4 F4 A4 D5', 37, 0, 3, 0.85, 'fp', vocal=1.0)
    for c, f in ((37, 'ff'), (45, 'ff')):
        p.melodia('trompas', f + ' ' + NEREA_TEMA[0], c, lig=False)
        p.melodia('trompas', f + ' ' + NEREA_TEMA[1], c + 4, lig=False)
        p.melodia('trombones', 'f ' + NEREA_TEMA[0], c, transp=-12, lig=False)
        p.melodia('trombones', 'f ' + NEREA_TEMA[1], c + 4, transp=-12, lig=False)
        p.melodia('coro_tema', 'f ' + NEREA_TEMA[0], c, vocal=1.0)
        p.melodia('coro_tema', 'f ' + NEREA_TEMA[1], c + 4, vocal=1.0)
    p.melodia('violines', 'f ' + NEREA_CONTRA, 37)
    p.melodia('violines', 'f ' + NEREA_TEMA[0], 45, transp=12)
    p.melodia('violines', 'f ' + NEREA_TEMA[1], 49, transp=12)
    p.melodia('violas', 'mf ' + NEREA_CONTRA, 45, transp=-12)
    p.melodia('celesta', 'mf ' + NEREA_TEMA[0], 45, transp=12)
    p.melodia('celesta', 'mf ' + NEREA_TEMA[1], 49, transp=12)
    rodar(37, 52, 0.8, 0.9, art='acc')
    bajos(37, 52, 0.75, 0.85, art='marc', pulso=True)
    bajos(37, 52, 0.55, 0.65, art='marc', inst='tuba')
    corazon(37, 52, 0.75, 0.85, por_compas=2)
    for c in range(37, 53):
        p.golpe('bombo', c, 0, 0.62 if c % 2 else 0.5)
        if c % 4 == 0:
            for k in (3, 4, 5):
                p.nota('timbales', 'A1', c, k, 1, 0.5 + 0.08 * (k - 3))
    arpa_ola(37, 52, 0.48, 0.5, paso_=0.5)
    pads('coro', 37, 52, 0.58, vocal=1.0)
    subgrave(37, 52, 0.5)
    # cierre: la ola rompe y se retira
    p.acorde('trombones', 'Bb1 F2 Bb2 D3', 53, 0, 6, 0.9, 'fpc')
    p.acorde('trompas', 'D4 F4 Bb4', 53, 0, 6, 0.85, 'fpc')
    p.acorde('coro', 'D4 F4 Bb4 D5', 53, 0, 6, 0.75, 'fpc', vocal=1.0)
    p.nota('contrabajos', 'Bb1', 53, 0, 6, 0.85, 'fpc')
    p.acorde('trombones', 'A1 E2 A2 C#3', 54, 0, 6, 0.95, 'fpc')
    p.acorde('trompas', 'C#4 E4 A4', 54, 0, 6, 0.9, 'fpc')
    p.acorde('coro', 'C#4 E4 A4 C#5', 54, 0, 6, 0.8, 'fpc', vocal=1.0)
    p.nota('contrabajos', 'A1', 54, 0, 6, 0.9, 'fpc')
    redoble(54, 0, 6, 'A1', 0.4, 1.0)
    rodar(53, 54, 0.85, 0.95, art='acc')
    p.golpe('olas', 55, 0, 0.95, dur=6.5, pan0=0.0, pan1=0.0, cresta=0.04, brillo=1.2)
    p.golpe('bombo', 55, 0, 1.0)
    p.nota('timbales', 'D2', 55, 0, 2, 1.0)
    p.acorde('trombones', 'D2 A2 D3 F3', 55, 0, 9, 0.95, 'dim')
    p.nota('tuba', 'D2', 55, 0, 9, 0.9, 'dim')
    p.acorde('trompas', 'D4 F4 A4', 55, 0, 12, 0.85, 'dim')
    p.acorde('coro', 'D4 F4 A4 D5', 55, 0, 12, 0.8, 'dim', vocal=1.0)
    p.nota('contrabajos', 'D2', 55, 0, 12, 0.8, 'dim')
    p.nota('chelos', 'D3', 55, 0, 12, 0.7, 'dim')
    for k, nm in enumerate(['D6', 'A5', 'F5', 'D5', 'A4', 'F4', 'D4', 'A3', 'F3', 'D3']):
        p.nota('arpa', nm, 55, 3 + 0.5 * k, 1, 0.5 - 0.02 * k)
    p.nota('sub', 'D2', 55, 0, 12, 0.6, 'dim')

    # ------------------------------------------------ D (57-68): calma, el mar solo
    p.seccion(57, 'calma')
    arpa_ola(57, 68, 0.3, 0.3)
    p.melodia('celesta', 'mp ' + NEREA_TEMA[0], 57, transp=12)
    p.melodia('armonica', 'mp A4:2 D5:1 A5:3 | G5:2 F5:1( D6:3 | C6:2 Bb5:1( A5:2 G5:1( | F5:2 E5:1( E5:3', 61)
    gotas(57, 68, 0.36, 2)
    olas([57, 59, 61, 63, 65, 67], 0.45)
    subgrave(57, 68, 0.4)
    p.golpe('ballena', 58, 2, 0.6, dur=6.0, puntos=[(0, 87.3), (0.45, 130.8), (1, 110.0)], brillo=210.0, pan=0.4)
    p.golpe('ballena', 64, 0, 0.55, dur=6.0, puntos=[(0, 73.4), (0.5, 110.0), (1, 98.0)], brillo=180.0, pan=-0.4)
    pads('coro', 65, 68, 0.26, vocal=0.0)
    for k, nm in enumerate(['A5', 'E6', 'C#6', 'A5']):
        p.nota('celesta', nm, 68, 0.5 + 1.25 * k, 1, 0.3)

    p.automatizar('_mezcla', p.respiro([(1, 1.5), (10, 1.0), (11, 0), (26, 0), (36, 0), (37, 0), (56, 0), (57, 1.5), (69, 1.5)],
                                       37, 1.0 / 6))
    return p


def instrumentos_nerea():
    P = presets()
    P['violines'].update(b0=0.22, bk=0.5)
    P['trompas'].update(V=5, det=4.5)
    P['coro'].update(vocales=('u', 'a'), tilt=1.2, suave=0.8)
    coro_tema = dict(P['coro'], voz='A', vocales=('u', 'a'), V=6, det=7.0, vib=(5.2, 16, 0.25, 0.5), ataque=0.1,
                     soltar=0.45, mono=True, glide=0.07, suave=0.6, tilt=1.15)
    armonica = dict(timbre=t_armonica, B=6, V=2, det=4.0, pan=-0.15, ancho=0.3, vib=(5.0, 0, 0.5, 0.5), am=(5.5, 0.07),
                    glide=0.06, ataque=0.12, soltar=1.1, b0=0.25, bk=0.5, bexp=1.0, mono=True, hum_t=0.006,
                    ruido=((1500, 5000, 0.004, 'nivel'),))
    sub = dict(timbre=t_seno, B=1, V=1, det=0.0, pan=0.0, ancho=0.0, vib=(5.0, 0, 0.5, 0.5), glide=0.2, ataque=0.8,
               soltar=1.2, b0=0.0, bk=0.0, bexp=1.0)
    sala = {'sala': respuesta_sala(4.2, 0.035, 5200, semilla=3, graves=1.2, agudos=0.5),
            'camara': respuesta_sala(1.2, 0.012, 6000, semilla=4, graves=1.0, agudos=0.6, densidad=0.012)}
    I = {
        'sub': dict(tipo='frase', P=sub, gan=-12, eq=[('pa', 28), ('pb', 220)], envios={'sala': 0.05}),
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-7, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2500)], envios={'sala': 0.15}),
        'chelos': dict(tipo='frase', P=P['chelos'], gan=-7.5, eq=[('pa', 60), ('pico', 250, -3, 1.0), ('pico', 1500, 1.5, 1.0), ('pb', 5500)],
                       envios={'sala': 0.3}),
        'violas': dict(tipo='frase', P=P['violas'], gan=-11, eq=[('pa', 150), ('pico', 280, -3, 1.0), ('pb', 6500)], envios={'sala': 0.4}),
        'violines': dict(tipo='frase', P=P['violines'], gan=-7, eq=[('pa', 220), ('pico', 3000, 1.0, 1.0), ('pb', 8500)], envios={'sala': 0.42}),
        'trompas': dict(tipo='frase', P=P['trompas'], gan=-3, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pico', 1200, 1.0, 1.0), ('pb', 6500)],
                        envios={'sala': 0.45}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-7, eq=[('pa', 60), ('pico', 250, -2, 1.0), ('pb', 6000)], envios={'sala': 0.35}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-9, eq=[('pa', 30), ('pb', 1800)], envios={'sala': 0.15}),
        'coro': dict(tipo='frase', P=P['coro'], gan=-8, eq=[('pa', 160), ('pico', 350, -3, 1.0), ('pico', 2500, 1.5, 1.0), ('pb', 8500)],
                     envios={'sala': 0.55}),
        'coro_tema': dict(tipo='frase', P=coro_tema, gan=-8, eq=[('pa', 150), ('pico', 380, -2, 1.0), ('pico', 2500, 1.5, 1.0), ('pb', 8500)],
                          envios={'sala': 0.5}),
        'armonica': dict(tipo='frase', P=armonica, gan=-7, eq=[('pa', 200), ('pb', 7000)], envios={'sala': 0.55}),
        'arpa': dict(tipo='nota_golpe', fn=arpa, pan=lambda nt: -0.5 + 0.015 * (nt.m - 50), gan=-6.5, eq=[('pa', 90), ('pb', 8500)],
                     envios={'sala': 0.5}),
        'celesta': dict(tipo='nota_golpe', fn=celesta, pan=lambda nt: 0.35 - 0.01 * (nt.m - 72), gan=-11, eq=[('pa', 300), ('pb', 8000)],
                        envios={'sala': 0.6}),
        'gotas': dict(tipo='nota_golpe', fn=gota, pan=0.0, gan=-15, eq=[('pa', 300), ('pb', 7000)], envios={'sala': 0.65}),
        'timbales': dict(tipo='nota_golpe', fn=timbal, pan=0.12, gan=-8, eq=[('pa', 40), ('pb', 4500)], envios={'sala': 0.25, 'camara': 0.3}),
        'bombo': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(_nivel(v), var, 0.8), pan=0.0, gan=-8, eq=[('pa', 30), ('pb', 2500)],
                      envios={'sala': 0.25, 'camara': 0.3}),
        'olas': dict(tipo='golpe', fn=lambda v, var, dur=4.0, pan0=-0.6, pan1=0.6, cresta=0.55, brillo=1.0, **kw:
                     ola(dur, pan0, pan1, cresta, brillo), gan=-15, eq=[('pa', 50), ('pb', 3000)], envios={'sala': 0.3}),
        'ballena': dict(tipo='golpe', fn=lambda v, var, dur, puntos, brillo=650.0, **kw: ballena(dur, puntos, brillo), gan=-12,
                        eq=[('pa', 45), ('pb', 1600)], envios={'sala': 0.7}),
    }
    return I, sala


# ======================================================================
#  AERALIS, Reina del Vendaval. Mi menor con el alivio dorico (La mayor) y
#  un puente lidio, 4/4 a 168: ligera y rapida. Todo suena a viento:
#  flautas y silbatos, cuerdas que corren, rachas, campanillas, truenos.
# ======================================================================
AER_AC = {
    # acorde: (raiz grave, notas del acorde para los arpegios, voces centrales)
    'Em': ('E2', 'E G B', 'E4 G4 B4'),
    'A': ('A1', 'A C# E', 'E4 A4 C#5'),
    'A/G': ('G1', 'A C# E', 'E4 A4 C#5'),
    'G': ('G1', 'G B D', 'D4 G4 B4'),
    'D': ('D2', 'D F# A', 'D4 F#4 A4'),
    'C': ('C2', 'C E G', 'E4 G4 C5'),
    'F#m': ('F#1', 'F# A C#', 'C#4 F#4 A4'),
    'Bm': ('B1', 'B D F#', 'D4 F#4 B4'),
}

AER_TEMA = ("B4:0.5 E5:0.5 G5:0.5 B5:0.5 E6:2 | D6:0.5 C#6:0.5 B5:1 A5:2 | "
            "B4:0.5 D5:0.5 G5:0.5 B5:0.5 D6:2 | E6:0.5 D6:0.5 A5:1 F#5:2 | "
            "B4:0.5 E5:0.5 G5:0.5 B5:0.5 E6:1.5 F#6:0.5 | E6:2 C#6:1 A5:1 | "
            "G5:0.5 A5:0.5 B5:0.5 C6:0.5 E6:1 D6:1 | F#5:1 A5:1 D6:2")
AER_PUENTE = ("D5:2 G5:1 A5:1 | B5:2 C#6:1 A5:1 | B5:1 A5:1 G5:1 D5:1 | E5:2 C#5:2 | "
              "E5:1 G5:1 B5:2 | A5:1 F#5:1 D6:2 | C6:2 B5:1 G5:1 | A5:2 F#5:1 D5:1")
AER_CONTRA = "B3:2 E4:2 | C#4:2 E4:2 | D4:2 B3:2 | A3:2 D4:2 | E4:2 G4:2 | E4:2 C#4:2 | C4:2 E4:2 | D4:2 F#4:2"
AER_CALMA = ("E5:2 B5:2 | A5:4 | G5:2 B5:2 | E5:4 | E5:2 G5:2 | D5:4 | E5:2 F#5:2 | G5:4 | "
             "A5:2 G5:2 | E5:4 | D5:2 F#5:2 | A5:4 | B5:4 | A5:4 | G5:2 F#5:2 | E5:4")


def aeralis():
    global rng
    rng = np.random.default_rng(20261009)
    p = Partitura('aeralis', 88, 4, 60.0 / 168)
    AC = AER_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c
    tema_ac = ['Em', 'A', 'G', 'D', 'Em', 'A', 'C', 'D']
    puente_ac = ['G', 'A/G', 'G', 'A/G', 'Em', 'D', 'C', 'D']
    armonia(1, ['Em', 'A', 'Em', 'A'] + tema_ac)
    armonia(13, tema_ac * 2 + puente_ac)
    armonia(37, ['Em', 'F#m', 'G', 'A', 'Bm', 'C', 'D', 'D', 'Em', 'C', 'D', 'D'])
    armonia(49, tema_ac * 2 + puente_ac)
    armonia(73, ['Em', 'A', 'Em', 'A', 'C', 'G', 'D', 'Em', 'C', 'Em', 'D', 'D', 'Em', 'A', 'Em', 'A'])

    def carrera(c0, c1, v0, v1=None, desde='E4'):
        """Las cuerdas que corren como el viento: arpegio ligado en
        semicorcheas que sube dos octavas y vuelve a bajar."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            arriba = subir(_pcs(AC[arm[c]][1]), midi(desde), 9)
            figura = arriba + arriba[-2:0:-1]
            p._fr += 1
            for k in range(16):
                m = figura[k % len(figura)]
                p.nota('carrera', m, c, k * 0.25, 0.25, v * (1.0 if k % 4 == 0 else 0.78), 'leg', lig=True, frase=p._fr)

    def tremolo(c0, c1, v0, v1=None, inst='violas'):
        v1 = v0 if v1 is None else v1
        acordes = []
        for c in range(c0, c1 + 1):
            acordes.append((c, 0, 4, AC[arm[c]][2]))
        for c, pos, dur, texto in acordes:
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for nm in texto.split():
                p.nota(inst, nm, c, pos, dur, v, 'trem')

    def bajo(c0, c1, v0, v1=None, figura='blancas'):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0])
            if figura == 'blancas':
                p.nota('contrabajos', r, c, 0, 2, v, 'leg')
                p.nota('contrabajos', r, c, 2, 2, v * 0.85, 'leg')
            else:
                for k in range(8):
                    ac = k in (0, 3, 6)
                    p.nota('chelos', r + 12 + (12 if k in (3, 6) else 0), c, k * 0.5, 0.5, v * (1.0 if ac else 0.66), 'acc' if ac else 'stac')
                    p.nota('contrabajos', r, c, k * 0.5, 0.5, v * (1.0 if ac else 0.6), 'acc' if ac else 'stac')

    def pads(inst, c0, c1, vel, vocal=0.0):
        ligar_acordes(p, inst, [(c, 0, 4, AC[arm[c]][2]) for c in range(c0, c1 + 1)], vel, 'leg', vocal=vocal)

    def campanillas(c0, c1, densidad, v):
        """Una rafaga mueve las campanillas: grupos de 2 a 5 golpes en la
        escala pentatonica de mi (mi sol la si re)."""
        escala = [midi(x) for x in ('E5', 'G5', 'A5', 'B5', 'D6', 'E6')]
        for c in range(c0, c1 + 1):
            if rng.random() < densidad:
                pos = float(rng.choice([0.5, 1.0, 2.0, 2.5]))
                for k in range(int(rng.integers(2, 6))):
                    p.nota('campanillas', int(rng.choice(escala)), c, pos + k * rng.uniform(0.18, 0.4), 1,
                           v * rng.uniform(0.5, 1.0), pan=rng.uniform(-0.8, 0.8))

    def rachas(lista, v, dur_compases=2.0, f1=2200.0):
        for i, c in enumerate(lista):
            a, b = (-0.85, 0.85) if i % 2 == 0 else (0.85, -0.85)
            p.golpe('rafaga', c, 0, v, dur=dur_compases * 4 * p.u, f0=350.0, f1=f1, pan0=a, pan1=b)

    def tambores(c0, c1, v, lleno=True):
        p.patron('taiko', 'X.....x.X.....x.' if lleno else 'X.......X.......', c0, c1, 0.25, v)
        p.patron('tom_grave', '..x..x....x..x..' if lleno else '..........x.....', c0, c1, 0.25, v * 0.75)
        p.patron('tom_medio', '......x.......xx' if lleno else '..............x.', c0, c1, 0.25, v * 0.65)
        p.patron('marco', 'x.ox.ox.x.ox.oxo', c0, c1, 0.25, v * 0.55)

    def redoble_timbal(c, pos, dur, m, v0, v1):
        t = 0.0
        while t < dur - 1e-6:
            p.nota('timbales', m, c, pos + t, 0.25, v0 + (v1 - v0) * t / dur)
            t += 0.17 * (1 + 0.06 * rng.standard_normal())

    # ------------------------------------------------ INTRO (1-12): se levanta el viento
    p.seccion(1, 'intro')
    p.golpe('trueno_lejano', 1, 0, 0.6, pan=-0.3)
    p.golpe('trueno_lejano', 9, 0, 0.5, pan=0.4)
    rachas([1, 3, 5, 7, 9, 11], 0.5)
    campanillas(1, 12, 0.6, 0.45)
    tremolo(1, 12, 0.18, 0.3)
    p.melodia('quena', 'mp ' + AER_TEMA, 5)
    bajo(9, 12, 0.3, 0.4)
    p.patron('marco', 'x...x...x...x...', 9, 12, 0.25, 0.35)
    carrera(11, 12, 0.25, 0.35)

    # ------------------------------------------------ A (13-36): el tema en vuelo
    p.seccion(13, 'tema')
    p.melodia('flauta', 'mf ' + AER_TEMA, 13)
    p.melodia('flauta', 'f ' + AER_TEMA, 21)
    p.melodia('violines', 'mp ' + AER_TEMA, 21, transp=-12)
    p.melodia('trompas', 'p ' + AER_CONTRA, 21, lig=False)
    p.melodia('silbato', 'mf ' + AER_PUENTE, 29)
    p.melodia('quena', 'mp ' + AER_PUENTE, 29, transp=-12)
    carrera(13, 36, 0.4, 0.5)
    tremolo(13, 36, 0.25, 0.3)
    bajo(13, 28, 0.42, 0.5, figura='corcheas')
    bajo(29, 36, 0.4, 0.45)
    pads('coro', 21, 36, 0.3, vocal=0.3)
    p.patron('marco', 'x..x..x.x..x..x.', 13, 36, 0.25, 0.45)
    p.patron('taiko', 'X...............', 13, 36, 0.25, 0.4)
    p.patron('tom_medio', '..............x.', 17, 36, 0.25, 0.35)
    campanillas(13, 36, 0.3, 0.38)
    rachas([20, 28, 35], 0.45)

    # ------------------------------------------------ B (37-48): sube la tormenta
    p.seccion(37, 'crece')
    despegues = ['E4:0.5 G4:0.5 B4:0.5 E5:0.5 G5:2', 'F#4:0.5 A4:0.5 C#5:0.5 F#5:0.5 A5:2',
                 'G4:0.5 B4:0.5 D5:0.5 G5:0.5 B5:2', 'A4:0.5 C#5:0.5 E5:0.5 A5:0.5 C#6:2',
                 'B4:0.5 D5:0.5 F#5:0.5 B5:0.5 D6:2', 'C5:0.5 E5:0.5 G5:0.5 C6:0.5 E6:2',
                 'D5:0.5 F#5:0.5 A5:0.5 D6:0.5 F#6:2', 'E6:1 D6:1 A5:1 F#5:1']
    for i, frag in enumerate(despegues):
        v = 0.55 + 0.35 * i / 7
        p.melodia('flauta', frag, 37 + i, vel=v)
        p.melodia('violines', frag, 37 + i, vel=v * 0.9, transp=-12)
    p.melodia('flauta', 'f B5:4~2 | C6:4~2 | D6:4~2 | D6:2 r:2', 45)
    carrera(37, 48, 0.5, 0.82)
    tremolo(37, 48, 0.3, 0.6)
    bajo(37, 48, 0.5, 0.8, figura='corcheas')
    for c in range(37, 49):
        voces = ' '.join(_nombre(x) for x in subir(_pcs(AC[arm[c]][1]), midi('B2'), 3))
        p.acorde('trombones', voces, c, 0, 4, 0.35 + 0.5 * (c - 37) / 11, 'fpc')
    pads('coro', 41, 48, 0.45, vocal=0.6)
    p.automatizar('coro', [(1, 0), (41, -4), (48.9, 2), (49, 0), (89, 0)])
    tambores(37, 40, 0.55, lleno=False)
    tambores(41, 46, 0.7)
    p.patron('tom_grave', 'x.x.x.x.x.x.x.x.', 47, 47, 0.25, 0.7)
    p.patron('tom_medio', '.x.x.x.x.x.x.x.x', 47, 48, 0.25, 0.65)
    p.patron('taiko', 'X...X...X.X.X.X.', 48, 48, 0.25, 0.85)
    redoble_timbal(47, 0, 8, 'B1', 0.3, 0.95)
    for c, v in ((37, 0.55), (41, 0.65), (45, 0.75)):
        p.golpe('trueno_lejano', c, 0, v, pan=(-0.4 if c == 41 else 0.4))
    rachas([39, 43], 0.55)
    p.golpe('rafaga', 46, 0, 0.75, dur=12 * p.u, f0=300.0, f1=2600.0, pan0=-0.6, pan1=0.6)

    # ------------------------------------------------ C (49-72): el vendaval en todo su poder
    p.seccion(49, 'CLIMAX')
    for c in (49, 57, 65):
        p.golpe('trueno', c, 0, 0.95 if c == 49 else 0.8, pan=(-0.3 if c == 57 else 0.3))
        p.nota('timbales', 'E2' if c != 65 else 'G1', c, 0, 2, 1.0)
        p.golpe('taiko', c, 0, 1.0)
    p.acorde('trombones', 'E2 B2 E3', 49, 0, 2, 1.0, 'fp')
    p.nota('tuba', 'E2', 49, 0, 2, 1.0, 'fp')
    p.acorde('coro', 'E4 G4 B4 E5', 49, 0, 2, 0.85, 'fp', vocal=1.0)
    p.melodia('flauta', 'ff ' + AER_TEMA, 49)
    p.melodia('flauta', 'ff ' + AER_TEMA, 57)
    p.melodia('flauta', 'ff ' + AER_PUENTE, 65)
    p.melodia('violines', 'f ' + AER_TEMA, 49)
    p.melodia('violines', 'f ' + AER_TEMA, 57)
    p.melodia('violines', 'f ' + AER_PUENTE, 65)
    p.melodia('trompas', 'f ' + AER_TEMA, 49, transp=-24, lig=False)
    p.melodia('trompas', 'f ' + AER_TEMA, 57, transp=-24, lig=False)
    p.melodia('trompas', 'ff ' + AER_PUENTE, 65, transp=-12, lig=False)
    p.melodia('trombones', 'mf ' + AER_CONTRA, 49, lig=False)
    p.melodia('trombones', 'mf ' + AER_CONTRA, 57, lig=False)
    p.melodia('trombones', 'f ' + AER_PUENTE, 65, transp=-24, lig=False)
    carrera(49, 72, 0.6, 0.65)
    tremolo(49, 72, 0.45, 0.5)
    bajo(49, 72, 0.7, 0.75, figura='corcheas')
    for c in range(49, 73):
        p.nota('tuba', AC[arm[c]][0], c, 0, 2, 0.6, 'acc')
        p.nota('tuba', AC[arm[c]][0], c, 2, 2, 0.5, 'leg')
    pads('coro', 49, 72, 0.62, vocal=1.0)
    tambores(49, 71, 0.85)
    p.patron('taiko', 'X.X.X.X.XXXX....', 72, 72, 0.25, 0.8)
    campanillas(49, 72, 0.25, 0.4)
    rachas([56, 64], 0.55)

    # ------------------------------------------------ D (73-88): calma, la flauta sola sobre el viento
    p.seccion(73, 'calma')
    p.golpe('trueno_lejano', 73, 0, 0.55, pan=0.3)
    p.golpe('trueno_lejano', 83, 0, 0.4, pan=-0.4)
    p.melodia('flauta', 'mp ' + AER_CALMA, 73)
    rachas([73, 75, 77, 79, 81, 83, 85, 87], 0.42, 2.0, 1800.0)
    campanillas(73, 88, 0.55, 0.4)
    tremolo(81, 88, 0.12, 0.2)
    for c in range(73, 89, 2):
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 8, 0.25, 'swell')

    p.automatizar('_mezcla', p.respiro([(1, 1.5), (12, 1.0), (13, 0), (36, 0), (48, 0), (49, 0), (72, 0), (73, 1.5), (89, 1.5)], 49))
    return p


def instrumentos_aeralis():
    P = presets()
    flauta = dict(timbre=t_flauta, B=6, V=1, det=0.0, pan=0.08, ancho=0.0, vib=(5.3, 16, 0.18, 0.3), glide=0.04, ataque=0.04,
                  soltar=0.25, b0=0.12, bk=0.7, bexp=1.0, ruido=((1500, 6000, 0.035, 'nivel'), (900, 4500, 0.16, 'soplo')),
                  mono=True, hum_t=0.004)
    quena = dict(timbre=t_quena, B=6, V=1, det=0.0, pan=-0.2, ancho=0.0, vib=(5.0, 8, 0.35, 0.4), glide=0.03, ataque=0.035,
                 soltar=0.3, b0=0.2, bk=0.55, bexp=1.0, ruido=((1200, 6000, 0.06, 'nivel'), (800, 5000, 0.3, 'soplo')),
                 mono=True, hum_t=0.006)
    silbato = dict(timbre=t_silbato, B=6, V=1, det=0.0, pan=0.18, ancho=0.0, vib=(5.6, 14, 0.25, 0.35), glide=0.035,
                   ataque=0.03, soltar=0.25, b0=0.15, bk=0.6, bexp=1.0, ruido=((1500, 6000, 0.03, 'nivel'), (900, 5000, 0.15, 'soplo')),
                   mono=True, hum_t=0.005)
    carrera = dict(P['violines'], V=4, det=5.0, pan=-0.3, ancho=0.45, vib=(5.6, 0, 0.3, 0.4), glide=0.012, ataque=0.03,
                   soltar=0.2, b0=0.25, bk=0.45, mono=True, hum_t=0.004, ruido=((2500, 8000, 0.008, 'nivel'),))
    violines = dict(P['violines'], b0=0.25, bk=0.5, pan=0.25)
    violas = dict(P['violas'], V=4, pan=-0.05, ancho=0.5, trem=(11.0, 14.0))
    coro = dict(P['coro'], vocales=('o', 'a'), tilt=1.3, suave=1.0, ruido=((2000, 6000, 0.03, 'nivel'),), V=5, det=9.0)
    sala = {'sala': respuesta_sala(3.2, 0.03, 7000, semilla=5, graves=1.1, agudos=0.6),
            'camara': respuesta_sala(0.9, 0.01, 6500, semilla=6, graves=1.0, agudos=0.6, densidad=0.01),
            'eco': respuesta_eco(0.75 * 60 / 168, 6, 0.5, 4200)}
    tam = lambda v: _nivel(v)
    I = {
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-8, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2500)], envios={'sala': 0.12}),
        'chelos': dict(tipo='frase', P=P['chelos'], gan=-9, eq=[('pa', 70), ('pico', 250, -3, 1.0), ('pb', 5500)], envios={'sala': 0.2}),
        'violas': dict(tipo='frase', P=violas, gan=-12, eq=[('pa', 200), ('pico', 300, -2, 1.0), ('pb', 7000)], envios={'sala': 0.45}),
        'carrera': dict(tipo='frase', P=carrera, gan=-9, eq=[('pa', 220), ('pico', 300, -2, 1.0), ('pb', 8000)], envios={'sala': 0.38, 'eco': 0.08}),
        'violines': dict(tipo='frase', P=violines, gan=-8, eq=[('pa', 200), ('pb', 8500)], envios={'sala': 0.4}),
        'flauta': dict(tipo='frase', P=flauta, gan=-5, eq=[('pa', 280), ('pb', 8500)], envios={'sala': 0.42, 'eco': 0.22}),
        'quena': dict(tipo='frase', P=quena, gan=-7, eq=[('pa', 200), ('pb', 8000)], envios={'sala': 0.45, 'eco': 0.25}),
        'silbato': dict(tipo='frase', P=silbato, gan=-6, eq=[('pa', 300), ('pb', 8000)], envios={'sala': 0.42, 'eco': 0.2}),
        'trompas': dict(tipo='frase', P=P['trompas'], gan=-5, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pb', 6500)], envios={'sala': 0.4}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-8, eq=[('pa', 60), ('pico', 250, -2, 1.0), ('pb', 6000)], envios={'sala': 0.3}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-10, eq=[('pa', 30), ('pb', 1800)], envios={'sala': 0.12}),
        'coro': dict(tipo='frase', P=coro, gan=-9, eq=[('pa', 200), ('pico', 350, -3, 1.0), ('pico', 2800, 1.5, 1.0), ('pb', 8500)],
                     envios={'sala': 0.55}),
        'campanillas': dict(tipo='nota_golpe', fn=campanilla, pan=0.0, gan=-17, eq=[('pa', 500), ('pb', 7500)], envios={'sala': 0.55}),
        'timbales': dict(tipo='nota_golpe', fn=timbal, pan=0.1, gan=-8, eq=[('pa', 40), ('pb', 4500)], envios={'sala': 0.2, 'camara': 0.3}),
        'taiko': dict(tipo='golpe', fn=lambda v, var, **kw: bombo_seco(tam(v), var), pan=0.0, gan=-6, eq=[('pa', 35), ('pb', 3500)],
                      envios={'sala': 0.15, 'camara': 0.35}),
        'tom_grave': dict(tipo='golpe', fn=lambda v, var, **kw: tom(100.0, tam(v), var, 0.16), pan=0.25, gan=-9, eq=[('pa', 70), ('pb', 5000)],
                          envios={'sala': 0.15, 'camara': 0.35}),
        'tom_medio': dict(tipo='golpe', fn=lambda v, var, **kw: tom(150.0, tam(v), var, 0.14), pan=-0.3, gan=-11, eq=[('pa', 90), ('pb', 5500)],
                          envios={'sala': 0.15, 'camara': 0.35}),
        'marco': dict(tipo='golpe', fn=lambda v, var, **kw: marco(tam(v), var), pan=0.15, gan=-13, eq=[('pa', 80), ('pb', 5000)],
                      envios={'sala': 0.15, 'camara': 0.35}),
        'trueno': dict(tipo='golpe', fn=lambda v, var, **kw: trueno(3, var), gan=-9, eq=[('pa', 30), ('pb', 2500)], envios={'sala': 0.35}),
        'trueno_lejano': dict(tipo='golpe', fn=lambda v, var, **kw: trueno_lejano(5.0), gan=-10, eq=[('pa', 30), ('pb', 900)],
                              envios={'sala': 0.45}),
        'rafaga': dict(tipo='golpe', fn=lambda v, var, dur=3.0, f0=400.0, f1=2400.0, pan0=-0.8, pan1=0.8, **kw:
                       rafaga_st(dur, f0, f1, pan0, pan1), gan=-17, eq=[('pa', 200), ('pb', 4500)], envios={'sala': 0.3}),
    }
    return I, sala


# ======================================================================
#  RAJANG, el Jaguar de Jade. Do menor con color frigio (Reb mayor), 4/4 a
#  120: un groove pesado y constante. Todo suena a tierra, madera y
#  piedra: taikos, tambores de marco, tronco, marimba grave, kalimba,
#  piedras, sonajas, el dron de la tierra, metales graves y coro.
# ======================================================================
RAJ_AC = {
    # acorde: (raiz grave, notas de la marimba grave, voces del coro, notas del acorde)
    'Cm': ('C2', 'C3 Eb3 G3 Bb3', 'C4 Eb4 G4', 'C Eb G'),
    'Bb': ('Bb1', 'Bb2 D3 F3 Bb3', 'D4 F4 Bb4', 'Bb D F'),
    'Ab': ('Ab1', 'Ab2 C3 Eb3 G3', 'C4 Eb4 Ab4', 'Ab C Eb'),
    'G': ('G1', 'G2 B2 D3 G3', 'B3 D4 G4', 'G B D'),
    'Fm': ('F1', 'F2 Ab2 C3 Eb3', 'C4 F4 Ab4', 'F Ab C'),
    'Db': ('Db2', 'Db3 F3 Ab3 Db4', 'Db4 F4 Ab4', 'Db F Ab'),
}

RAJ_TEMA1 = "gD6 C6:1.5 G5:1.5 Bb5:1 | G5:1.5 F5:1.5 Eb5:0.5 F5:0.5 | gC6 Bb5:1.5 F5:1.5 G5:1 | Eb5:1.5 C5:2.5~2"
RAJ_TEMA2 = "C5:1 Eb5:1 F5:1 G5:1 | gD6 C6:1.5 Bb5:1.5 G5:1 | F5:1.5 Eb5:1.5 D5:0.5 B4:0.5 | D5:4~1"
RAJ_TEMA2B = "C5:1 Eb5:1 F5:1 Bb5:1 | C6:1.5 Eb6:1.5 C6:1 | B5:1.5 Ab5:1.5 G5:0.5 F5:0.5 | G5:4"
RAJ_CANTO = ("C4:1 Eb4:1 Ab4:2 | G4:1 F4:1 Eb4:2 | D4:1 F4:1 Bb4:2 | Ab4:1 G4:1 F4:2 | "
             "Db4:1 F4:1 Ab4:2 | Bb4:1 Ab4:1 F4:2 | D4:1 G4:1 B4:2 | D5:2 B4:2")


def rajang():
    global rng
    rng = np.random.default_rng(20261010)
    p = Partitura('rajang', 64, 4, 60.0 / 120)
    AC = RAJ_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c
    tema_a = ['Cm', 'Cm', 'Bb', 'Cm', 'Ab', 'Bb', 'G', 'G']
    tema_b = ['Cm', 'Cm', 'Bb', 'Cm', 'Ab', 'Fm', 'G', 'G']
    armonia(1, ['Cm', 'Cm', 'Cm', 'Cm', 'Bb', 'Cm', 'Ab', 'G'])
    armonia(9, tema_a + tema_b)
    armonia(25, ['Ab', 'Ab', 'Bb', 'Bb', 'Db', 'Db', 'G', 'G'])
    armonia(33, tema_a + tema_b + ['Ab', 'Db', 'G', 'Cm'])
    armonia(53, ['Cm', 'Ab', 'Cm', 'Ab', 'Fm', 'G', 'Cm', 'Cm', 'Ab', 'Bb', 'G', 'G'])

    def marimba_pat(c0, c1, v0, v1=None, figura16=True):
        """Marimba grave: arpegio que sube y baja con el acento 3+3+2."""
        v1 = v0 if v1 is None else v1
        acento = (1.0, 0.55, 0.65, 0.9, 0.55, 0.65, 0.9, 0.6) * 2
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            base = [midi(x) for x in AC[arm[c]][1].split()]
            arriba = base + [m + 12 for m in base]
            figura = arriba[:7] + arriba[6:1:-1]
            pasos_ = 16 if figura16 else 8
            for k in range(pasos_):
                p.nota('marimba', figura[k % len(figura)], c, k * 4.0 / pasos_, 0.25, v * (acento[k] if figura16 else (1.0 if k % 2 == 0 else 0.7)))

    def tronco_pat(c0, c1, v0, v1=None):
        """Tambor de tronco: raiz y quinta en corcheas, 3+3+2."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0]) + 12
            figura = (r, r + 7, r, r + 7, r, r + 7, r + 12, r + 7)
            for k in range(8):
                p.nota('tronco', figura[k], c, k * 0.5, 0.5, v * (1.0 if k in (0, 3, 6) else 0.6))

    def dron(c0, c1, v0, v1=None, suave=False):
        """El dron de la tierra: sigue al bajo y la boca lo mueve en 3+3+2."""
        v1 = v0 if v1 is None else v1
        p._fr += 1
        fr = p._fr
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0])
            r = r + 12 if r < midi('G1') else r
            if suave:
                p.nota('dron', r, c, 0, 4, v, 'swell', lig=True, frase=fr)
            else:
                for pos, dur, a in ((0, 1.5, 'fp'), (1.5, 1.5, 'fp'), (3, 1, 'acc')):
                    p.nota('dron', r, c, pos, dur, v * (1.0 if pos == 0 else 0.8), a, lig=True, frase=fr)

    def tambores(c0, c1, v=0.85, lleno=True):
        p.patron('taiko', 'X.....x.....x...', c0, c1, 0.25, v)
        p.patron('timbal_grave', '..x...x...x.x..x' if lleno else '..........x....x', c0, c1, 0.25, v * 0.7)
        p.patron('marco', 'x.ox.ox.x.oxx.ox', c0, c1, 0.25, v * 0.55)
        p.patron('sonajas', 'x.o.x.o.x.o.x.o.', c0, c1, 0.25, v * 0.5)
        p.patron('piedras', '..x...x...x...x.', c0, c1, 0.25, v * 0.55)
        if lleno:
            p.patron('tres', 'x..', c0, c1, 0.25, v * 0.5)

    def pads(inst, c0, c1, v, vocal=0.0, art='leg'):
        ligar_acordes(p, inst, [(c, 0, 4, AC[arm[c]][2]) for c in range(c0, c1 + 1)], v, art, vocal=vocal)

    def kalimba_arp(c0, c1, v, desde='G4'):
        """Kalimba: notas del acorde en corcheas, una mano y otra."""
        for c in range(c0, c1 + 1):
            notas = subir(_pcs(AC[arm[c]][3]), midi(desde), 5)
            orden = [0, 2, 1, 3, 2, 4, 3, 1]
            for k in range(8):
                p.nota('kalimba', notas[orden[k]], c, k * 0.5, 0.5, v * (1.0 if k % 2 == 0 else 0.75), pan=(-0.3 if k % 2 == 0 else 0.3))

    def metales(c0, c1, v0, v1=None, art='fpc'):
        """Metales graves: un acorde que se hincha en cada cambio de armonia."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            if c > c0 and arm[c] == arm[c - 1]:
                continue
            dur = 4
            while c + dur // 4 <= c1 and arm.get(c + dur // 4) == arm[c]:
                dur += 4
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0]) + 12
            decima = subir([_pcs(AC[arm[c]][3])[1]], r + 8, 1)[0]
            p.acorde('trombones', ' '.join(_nombre(x) for x in (r, r + 7, decima)), c, 0, dur, v, art)
            p.acorde('trompas', AC[arm[c]][2], c, 0, dur, v * 0.85, art)

    # ------------------------------------------------ INTRO (1-8): la tierra despierta
    p.seccion(1, 'intro')
    p.golpe('retumbo', 1, 0, 0.75, dur=7.0, f_sub=32.7)
    p.golpe('retumbo', 7, 0, 0.6, dur=5.0, f_sub=49.0)
    dron(1, 8, 0.45, 0.6, suave=True)
    for k, nm in enumerate(['C5', 'Eb5', 'G5', 'C6', 'G5', 'Eb5', 'C5', 'G4']):
        p.nota('kalimba', nm, 1 + k // 4, (k % 4) * 1.0, 1, 0.45 + 0.05 * (k % 2))
    p.melodia('kalimba', 'mp ' + RAJ_TEMA1, 3)
    p.patron('piedras', '..x.........x...', 3, 8, 0.25, 0.4)
    p.patron('marco', 'X.......x.......', 5, 8, 0.25, 0.45)
    p.patron('taiko', 'X...............', 7, 8, 0.25, 0.55)
    p.golpe('semillas', 4, 2, 0.5, dur=2 * p.u, subida_=False, pan=0.5)
    p.golpe('semillas', 8, 0, 0.65, dur=4 * p.u, pan=-0.4)
    kalimba_arp(7, 8, 0.38)

    # ------------------------------------------------ A (9-24): el groove de la selva de jade
    p.seccion(9, 'tema')
    tambores(9, 16, 0.72, lleno=False)
    tambores(17, 24, 0.8)
    dron(9, 24, 0.5, 0.58)
    tronco_pat(9, 24, 0.6, 0.68)
    marimba_pat(9, 24, 0.5, 0.56)
    p.melodia('ocarina', 'mf ' + RAJ_TEMA1, 9)
    p.melodia('ocarina', 'mf ' + RAJ_TEMA2, 13)
    p.melodia('ocarina', 'f ' + RAJ_TEMA1, 17)
    p.melodia('ocarina', 'f ' + RAJ_TEMA2B, 21)
    p.melodia('kalimba', 'mf ' + RAJ_TEMA1, 17, transp=-12)
    p.melodia('kalimba', 'mf ' + RAJ_TEMA2B, 21, transp=-12)
    metales(17, 24, 0.4, 0.5)
    for c in range(17, 25, 2):
        p.nota('tuba', AC[arm[c]][0], c, 0, 8, 0.5, 'swell')
    p.golpe('semillas', 16, 2, 0.6, dur=2 * p.u, pan=0.35)

    # ------------------------------------------------ B (25-32): crece el canto
    p.seccion(25, 'crece')
    p.melodia('canto', 'f ' + RAJ_CANTO, 25, vocal=0.3)
    p.melodia('canto', 'mf ' + RAJ_CANTO, 25, transp=-12, vocal=0.3)
    metales(25, 32, 0.55, 0.9)
    for c in range(25, 33, 2):
        p.nota('tuba', AC[arm[c]][0], c, 0, 8, 0.7, 'fpc')
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 8, 0.6, 'fpc')
    pads('coro', 29, 32, 0.5, vocal=0.6)
    p.automatizar('coro', [(1, 0), (29, -6), (32.9, 2), (33, 0), (65, 0)])
    p.patron('taiko', 'X..x..x.X..x..x.', 25, 31, 0.25, 0.85)
    p.patron('timbal_grave', '..x...x...x.x..x', 25, 31, 0.25, 0.65)
    p.patron('marco', 'x.ox.ox.x.oxx.ox', 25, 32, 0.25, 0.6)
    p.patron('tres', 'x..', 29, 32, 0.25, 0.55)
    p.patron('sonajas', 'xoxoxoxoxoxoxoxo', 29, 32, 0.25, 0.5)
    p.patron('piedras', '..x...x...x...x.', 25, 32, 0.25, 0.5)
    p.patron('taiko', 'X.X.X.X.XXXXXXXX', 32, 32, 0.25, 0.9)
    tronco_pat(25, 32, 0.65, 0.85)
    marimba_pat(25, 32, 0.5, 0.65)
    dron(25, 32, 0.55, 0.75)
    p.golpe('retumbo', 31, 0, 0.75, dur=4.0, f_sub=49.0)
    p.golpe('semillas', 31, 0, 0.8, dur=8 * p.u, pan=0.3)

    # ------------------------------------------------ C (33-52): tambores de guerra
    p.seccion(33, 'CLIMAX')
    p.golpe('terremoto', 33, 0, 0.9)
    p.golpe('taiko', 33, 0, 1.0)
    p.acorde('trombones', 'C2 G2 C3', 33, 0, 3, 1.0, 'fp')
    p.nota('tuba', 'C2', 33, 0, 3, 1.0, 'fp')
    p.acorde('canto', 'C3 G3 C4', 33, 0, 1.5, 0.95, 'acc', vocal=1.0)
    for c, t2 in ((33, RAJ_TEMA2), (41, RAJ_TEMA2B)):
        f = 'f' if c == 33 else 'ff'
        p.melodia('ocarina', f + ' ' + RAJ_TEMA1, c)
        p.melodia('ocarina', f + ' ' + t2, c + 4)
        p.melodia('trompas', f + ' ' + RAJ_TEMA1, c, transp=-12, lig=False)
        p.melodia('trompas', f + ' ' + t2, c + 4, transp=-12, lig=False)
        p.melodia('trombones', 'f ' + RAJ_TEMA1, c, transp=-24, lig=False)
        p.melodia('trombones', 'f ' + t2, c + 4, transp=-24, lig=False)
        p.melodia('coro_tema', f + ' ' + RAJ_TEMA1, c, transp=-12, vocal=1.0)
        p.melodia('coro_tema', f + ' ' + t2, c + 4, transp=-12, vocal=1.0)
    p.golpe('terremoto', 41, 0, 0.7)
    pads('coro', 33, 52, 0.6, vocal=1.0)
    tambores(33, 48, 0.95)
    p.patron('taiko', 'X..x..x.X..x..x.', 41, 48, 0.25, 0.6)
    tronco_pat(33, 52, 0.75, 0.8)
    marimba_pat(33, 52, 0.6, 0.62)
    kalimba_arp(33, 48, 0.35, desde='G5')
    dron(33, 52, 0.62, 0.68)
    for c in range(33, 49, 2):
        p.nota('tuba', AC[arm[c]][0], c, 0, 8, 0.7, 'swell')
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 8, 0.65, 'swell')
    for c in range(33, 49, 4):
        p.acorde('canto', 'C3 G3' if arm[c] == 'Cm' else 'Bb2 F3' if arm[c] == 'Bb' else 'Ab2 Eb3', c, 0, 1, 0.8, 'acc', vocal=0.8)
    # cierre: Lab - Reb - Sol - Do menor, con todo
    metales(49, 51, 0.9, 1.0)
    for c in range(49, 52):
        p.nota('tuba', AC[arm[c]][0], c, 0, 4, 0.85, 'fpc')
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 4, 0.8, 'fpc')
        p.acorde('canto', ' '.join(AC[arm[c]][2].split()[:2]), c, 0, 4, 0.8, 'fpc', transp=-12, vocal=1.0)
    p.patron('taiko', 'X.....x.X.....x.', 49, 50, 0.25, 0.95)
    p.patron('taiko', 'X.X.X.X.XXXXXXXX', 51, 51, 0.25, 0.95)
    p.patron('timbal_grave', 'x.x.x.x.x.x.x.x.', 49, 51, 0.25, 0.8)
    p.patron('marco', 'xoxoxoxoxoxoxoxo', 49, 51, 0.25, 0.65)
    p.golpe('terremoto', 52, 0, 0.85)
    p.golpe('taiko', 52, 0, 1.0)
    p.acorde('trombones', 'C2 G2 C3 Eb3', 52, 0, 4, 0.95, 'dim')
    p.acorde('trompas', 'C4 Eb4 G4', 52, 0, 4, 0.9, 'dim')
    p.nota('tuba', 'C2', 52, 0, 4, 0.9, 'dim')
    p.acorde('canto', 'C3 G3 C4', 52, 0, 4, 0.9, 'dim', vocal=1.0)

    # ------------------------------------------------ D (53-64): calma, kalimba y dron
    p.seccion(53, 'calma')
    dron(53, 64, 0.38, 0.42, suave=True)
    marimba_pat(53, 64, 0.32, 0.34, figura16=False)
    p.melodia('kalimba', 'mp ' + RAJ_TEMA1, 57)
    kalimba_arp(53, 56, 0.32)
    kalimba_arp(61, 64, 0.3)
    p.patron('piedras', '..x.............', 53, 64, 0.25, 0.35)
    p.patron('marco', 'x...............', 53, 60, 0.25, 0.3)
    p.golpe('semillas', 55, 2, 0.45, dur=2 * p.u, subida_=False, pan=-0.5)
    p.golpe('semillas', 59, 2, 0.45, dur=2 * p.u, subida_=False, pan=0.5)
    p.golpe('retumbo', 63, 0, 0.45, dur=4.0, f_sub=49.0)

    p.automatizar('_mezcla', p.respiro([(1, 1.0), (8, 0.5), (9, 0), (32, 0), (33, 0), (52, 0), (53, 1.5), (65, 1.0)], 33))
    return p


def instrumentos_rajang():
    P = presets()
    ocarina = dict(timbre=t_ocarina, B=6, V=1, det=0.0, pan=-0.08, ancho=0.0, vib=(5.6, 12, 0.3, 0.4), glide=0.035, ataque=0.035,
                   soltar=0.22, b0=0.15, bk=0.6, bexp=1.0, ruido=((900, 5000, 0.035, 'nivel'), (700, 4000, 0.18, 'soplo')),
                   mono=True, hum_t=0.005)
    dron_ = dict(timbre=t_dron, B=8, V=2, det=3.0, pan=0.0, ancho=0.15, vib=(5.0, 0, 0.5, 0.5), glide=0.06, ataque=0.15,
                 soltar=0.6, b0=0.05, bk=0.75, bexp=1.0, mono=True, ruido=((150, 1000, 0.03, 'nivel'),), hum_t=0.003)
    canto = dict(P['coro'], voz='B', vocales=('o', 'a'), tilt=1.05, suave=0.45, V=6, det=10.0, vib=(5.0, 12, 0.3, 0.5), ataque=0.05,
                 soltar=0.3, glide=0.06, ancho=0.45, ruido=((300, 2500, 0.05, 'soplo'), (500, 3000, 0.01, 'nivel')), mono=True, disp=0.02)
    coro_tema = dict(P['coro'], voz='T', vocales=('o', 'a'), V=6, det=8.0, vib=(5.0, 14, 0.25, 0.5), ataque=0.06, soltar=0.35,
                     mono=True, glide=0.06, suave=0.6, tilt=1.1)
    coro = dict(P['coro'], vocales=('o', 'a'), tilt=1.15, suave=0.7, V=5, det=9.0, ancho=0.6)
    trompas = dict(P['trompas'], V=5)
    sala = {'sala': respuesta_sala(2.6, 0.022, 6500, semilla=7, graves=1.1, agudos=0.55, tempranas=16),
            'camara': respuesta_sala(0.8, 0.008, 6000, semilla=8, graves=1.0, agudos=0.6, densidad=0.008, tempranas=12),
            'eco': respuesta_eco(0.75 * 60 / 120, 5, 0.45, 3800)}
    tam = lambda v: _nivel(v)
    I = {
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-10, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2000)], envios={'sala': 0.1}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-9, eq=[('pa', 30), ('pb', 1600)], envios={'sala': 0.12}),
        'dron': dict(tipo='frase', P=dron_, gan=-10, eq=[('pa', 40), ('pico', 300, -2, 1.0), ('pb', 3000)], envios={'sala': 0.2}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-7, eq=[('pa', 50), ('pico', 300, -2, 1.0), ('pb', 5500)], envios={'sala': 0.3}),
        'trompas': dict(tipo='frase', P=trompas, gan=-5, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pico', 1200, 1.0, 1.0), ('pb', 6500)],
                        envios={'sala': 0.35}),
        'canto': dict(tipo='frase', P=canto, gan=-8, eq=[('pa', 70), ('pico', 300, -2.5, 1.0), ('pico', 2500, 1.0, 1.0), ('pb', 7000)],
                      envios={'sala': 0.4}),
        'coro_tema': dict(tipo='frase', P=coro_tema, gan=-8, eq=[('pa', 120), ('pico', 300, -2.5, 1.0), ('pb', 8000)], envios={'sala': 0.45}),
        'coro': dict(tipo='frase', P=coro, gan=-10, eq=[('pa', 110), ('pico', 300, -3, 1.0), ('pb', 8000)], envios={'sala': 0.5}),
        'ocarina': dict(tipo='frase', P=ocarina, gan=-6, eq=[('pa', 250), ('pb', 8000)], envios={'sala': 0.35, 'eco': 0.16}),
        'kalimba': dict(tipo='nota_golpe', fn=kalimba, pan=0.0, gan=-9, eq=[('pa', 150), ('pb', 7000)], envios={'sala': 0.35, 'eco': 0.12}),
        'marimba': dict(tipo='nota_golpe', fn=marimba, pan=lambda nt: -0.45 + 0.025 * (nt.m - 48), gan=-9,
                        eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pb', 7000)], envios={'sala': 0.25}),
        'tronco': dict(tipo='nota_golpe', fn=tronco, pan=0.3, gan=-9, eq=[('pa', 60), ('pb', 4000)], envios={'sala': 0.2, 'camara': 0.3}),
        'taiko': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(tam(v), var, 1.0), pan=0.0, gan=-5, eq=[('pa', 32), ('pb', 3500)],
                      envios={'sala': 0.18, 'camara': 0.35}),
        'tres': dict(tipo='golpe', fn=lambda v, var, **kw: tom(118.0, tam(v), var, 0.18), pan=-0.35, gan=-13, eq=[('pa', 80), ('pb', 4500)],
                     envios={'sala': 0.12, 'camara': 0.35}),
        'timbal_grave': dict(tipo='golpe', fn=lambda v, var, **kw: tom(78.0, tam(v), var, 0.2), pan=0.3, gan=-9, eq=[('pa', 55), ('pb', 4500)],
                             envios={'sala': 0.12, 'camara': 0.35}),
        'marco': dict(tipo='golpe', fn=lambda v, var, **kw: marco(tam(v), var), pan=-0.2, gan=-11, eq=[('pa', 70), ('pb', 4500)],
                      envios={'sala': 0.12, 'camara': 0.35}),
        'sonajas': dict(tipo='golpe', fn=lambda v, var, **kw: sonaja(tam(v), var, brillo=0.7), pan=0.45, gan=-17, eq=[('pa', 1200), ('pb', 6500)],
                        envios={'sala': 0.15}),
        'semillas': dict(tipo='golpe', fn=lambda v, var, dur=0.6, subida_=True, **kw: semillas(dur, subida_), gan=-16,
                         eq=[('pa', 1200), ('pb', 6500)], envios={'sala': 0.3}, ancho=0.01),
        'piedras': dict(tipo='golpe', fn=lambda v, var, **kw: piedra(tam(v), var), pan=-0.4, gan=-14, eq=[('pa', 200), ('pb', 5500)],
                        envios={'camara': 0.3, 'sala': 0.15}),
        'retumbo': dict(tipo='golpe', fn=lambda v, var, dur=5.0, f_sub=32.7, **kw: retumbo(dur, f_sub), gan=-9, eq=[('pa', 25), ('pb', 300)],
                        envios={'sala': 0.15}),
        'terremoto': dict(tipo='golpe', fn=lambda v, var, **kw: terremoto(3, var), gan=-7, eq=[('pa', 25), ('pb', 2500)], envios={'sala': 0.25}),
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


def guardar_pista(nombre, y, p, niveles, gmin, salida, revision=None, calidad=0.5):
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
    vecinos = np.concatenate([np.abs(np.diff(z[:, -201:], axis=1)), np.abs(np.diff(z[:, :201], axis=1))], axis=1)
    tipico = float(vecinos.max())
    w = n_(0.5)
    antes = 20 * np.log10(np.sqrt(np.mean(z[:, -w:] ** 2)) + 1e-12)
    despues = 20 * np.log10(np.sqrt(np.mean(z[:, :w] ** 2)) + 1e-12)
    info = dict(archivo=ruta, segundos=seg, muestras=z.shape[1], esperado=p.L, compases=p.nc,
                pico_db=float(20 * np.log10(np.max(np.abs(z)) + 1e-12)), rms_db=float(rms), lufs=float(lufs(z)),
                mb=os.path.getsize(ruta) / 1e6, nan=bool(np.isnan(z).any()), recortes=int(np.sum(np.abs(z) >= 0.999)),
                salto_costura=float(salto), salto_tipico=float(tipico), rms_antes=float(antes), rms_despues=float(despues),
                limitador_db=float(20 * np.log10(gmin + 1e-12)))
    print('  %-7s %6.1f s (%d compases)  pico %.2f dBFS  rms %.1f dBFS  %.1f LUFS  %.2f MB  costura %.4f (max. alrededor %.4f)  '
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


registrar('nerea', nerea, instrumentos_nerea, -17.0)
registrar('aeralis', aeralis, instrumentos_aeralis, -17.0)
registrar('rajang', rajang, instrumentos_rajang, -17.0)


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
