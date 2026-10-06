"""
Musica de COMBATE de los tres jefes de Atalaya y sus golpes de musica.
Compuesta como datos y sintetizada desde cero: nada de samples, bancos de
sonido ni descargas. Cada pista es un BUCLE SIN COSTURA de un numero exacto
de compases (estereo, 44100 Hz, Ogg Vorbis) que suena MIENTRAS el jefe pelea:
pulso que no para, riff grave, tambores casi siempre, metales que golpean,
coro que grita en el climax y una calma que no relaja (acecho).

Forma de las tres: intro que crece -> combate (riff y tema) -> crece mas ->
CLIMAX -> acecho (dron, latido, notas sueltas) -> vuelta al principio.

  NEREA, Guardiana de los Mares (nerea.ogg). Re menor frigio (el mib), 6/8
  a 104 negras con puntillo: un galope de olas. 112 compases, 2:09.
      1-16   intro: el corazon maldito en los timbales (re-la), canto de
             ballena, gotas, entra el riff de chelos, el arpa, los tambores
             y la cabeza del tema; subida disonante y ola que crece.
      17-48  combate: el riff (raiz, quinta, raiz, mib, raiz, quinta) y el
             tema oscuro en trompas (re-mib-re, do-sib-la...), luego con
             trombones, el lamento con bajo cromatico en violines y el tema
             otra vez; bombo y tom rompen como olas, golpes de metales.
      49-64  crece: la celda del tema sube a medios tonos (re, mib, mi, fa
             menor) y un pedal de la7(b9) con coro en golpes, redoble y
             racimo de cuerdas que sube.
      65-96  CLIMAX: la ola gigante; tema en trompas, trombones, violines y
             el coro que lo grita en silabas cortas, taikos y timbales.
      97-112 acecho: latido, dron grave, ballena, gotas, la armonica de
             cristal con el tema y un racimo re-mib en tremolo.

  AERALIS, Reina del Vendaval (aeralis.ogg). Mi menor frigio (el fa), 4/4
  a 160. 84 compases, 2:06.
      1-12   intro: trueno lejano, un pulso como un corazon en los toms,
             el spiccato que se levanta, la flauta aulla la celda del tema,
             redoble de caja, subida disonante y racha que cruza.
      13-36  combate: spiccato en semicorcheas (con el fa), corcheas graves,
             el tema de la flauta (rafagas que suben hasta el fa y caen),
             segunda vuelta con violines, lamento cromatico; toms rapidos y
             redobles de caja como rachas de tormenta, golpes de metales.
      37-48  crece: la celda sube a medios tonos (mi, fa, fa#, sol menor),
             pedal de si7(b9), coro en golpes, redobles, racimo que sube.
      49-72  CLIMAX: truenos, flauta y violines con el tema, trompas abajo,
             coro gritando en 3+3+2, caja atras, cuerdas que corren.
      73-84  acecho: dron, latido, rafagas, campanillas sueltas, la flauta
             de pan grave con la celda y un racimo mi-fa en tremolo.

  RAJANG, el Jaguar de Jade (rajang.ogg). Do menor frigio (el reb), 4/4 a
  136: taikos pesados a medio tiempo. 72 compases, 2:07.
      1-10   intro: retumbo, latido de taiko, dron de la tierra, el riff del
             tambor de tronco, la kalimba con el tema, marimba grave.
      11-30  combate: el tema en trompas (3+3+2: do-mib-sol, fa-mib-reb-do)
             doblado por la ocarina de barro; tronco, marimba, taikos,
             timbales graves, marcos, piedras, sonajas; gritos del coro.
      31-40  crece: la celda en trompas y trombones, el coro en golpes,
             pedal de sol7(b9), taikos en semicorcheas, subida, retumbo.
      41-60  CLIMAX: la furia de jade; tema en metales y ocarina, el coro
             de hombres lo grita, tambores de guerra, terremotos.
      61-72  acecho: dron, latido de taiko, kalimba suelta, piedras.

GOLPES DE MUSICA (stingers), por jefe, en la misma carpeta: el juego los
dispara encima de la pista cuando el jefe pega (y baja la pista un momento).
Mismos instrumentos, salas, tonalidad y modo: acorde de tonica, sin chocar.
    <jefe>_golpe1 / _golpe2  golpe pesado, 1,2-1,3 s (dos variantes).
    <jefe>_grande            momento grande, 3,2 s: golpe, metales y coro
                             que se hinchan, acorde oscuro que se apaga.
    <jefe>_fase              cambio de fase, 3,2-3,4 s: subida corta, golpe
                             y la cabeza del leitmotiv en los metales.

COMO SE HACE
  - La musica son datos: notas con altura, inicio en pulsos, duracion,
    intensidad y articulacion (Partitura; las melodias se escriben como
    texto 'D4:2 Eb4:1 D4:3 | ...' y se comprueba que cada compas cuadre),
    riffs y patrones de percusion, curvas de dinamica. Se humaniza un poco.
  - Cuerdas, metales, coro, flautas, armonica de cristal y el dron:
    osciladores de tabla con el espectro de cada nota (cuerpo del violin,
    formantes de vocal, boca del didgeridoo), limitados en banda y con
    filas de brillo. Voces desafinadas con vibrato, portamento, ataque de
    lengua o arco y glissando (subidas disonantes).
  - Arpa por Karplus-Strong; marimba, tronco, kalimba y campanillas
    modales; gotas afinadas; tambores con tono que cae y ruido de piel;
    olas, rachas, truenos, terremotos y retumbos con ruido filtrado.
  - Mezcla: buses con paneo, ecualizacion y envios a salas de convolucion
    (respuestas estereo que decaen por bandas) y a un eco a tempo.
  - Bucle: se renderiza el bucle mas una cola de 10 s y la cola se suma al
    principio; lo que va despues (fader general, graves al centro, filtro,
    compresor, limitador) es circular: el final entra en el principio sin
    chasquido.
  - Master: sonoridad integrada (BS.1770) de -17 LUFS, compresor suave que
    solo toca lo mas fuerte, limitador con techo -1,3 dBFS. Se vuelve a
    leer cada .ogg para medir picos, RMS, LUFS y la costura.

Escribe src/main/resources/assets/atalaya/sounds/musica/: nerea.ogg,
aeralis.ogg, rajang.ogg y los golpes <jefe>_golpe1/_golpe2/_grande/_fase.ogg.
NO toca sounds.json: los eventos se dan de alta aparte (pistas con
"stream": true).

Uso: python musica_jefes.py <raiz del proyecto> [carpeta_de_revision] [pista,...]
  - carpeta_de_revision: por pista, espectrograma y forma de onda en PNG,
    los ultimos 15 s + los primeros 15 s en WAV (para oir la costura), los
    niveles de cada bus y un PNG por golpe.
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


def tocar_buses(p, inst, mz, n):
    """Toca cada instrumento en su bus y lo suma a la mezcla (con sus envios)."""
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
    return tiempos


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
    tiempos = tocar_buses(p, inst, mz, n)
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


# ======================================================================
#  Sonidos de los elementos: agua, viento y tierra (todo afinado o sin
#  agudos: que se oiga el elemento sin ruido de fondo constante)
# ======================================================================
def t_seno(k, fk, b):
    return np.where(k == 1, 1.0, 0.0)


def t_armonica(k, fk, b):
    """Armonica de cristal: copas frotadas, casi un seno puro."""
    return np.where(k == 1, 1.0, np.where(k == 2, 0.05 + 0.08 * b, np.where(k == 3, 0.025 * b, 0.0)))


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
#  NEREA, Guardiana de los Mares: musica de COMBATE. Re menor frigio (mib),
#  6/8 a 104 negras con puntillo: un galope de olas que no para. Suena a
#  agua (arpa, armonica de cristal, gotas, olas, canto de ballena) sobre un
#  riff grave de cuerdas, tambores que rompen como olas y metales.
# ======================================================================
NEREA_AC = {
    # acorde: (raiz grave, riff de chelos (raiz, quinta, raiz, vecina, raiz, quinta), notas del acorde, voces)
    'Dm': ('D2', 'D3 A2 D3 Eb3 D3 A2', 'D F A', 'D4 F4 A4'),
    'Eb/D': ('D2', 'D3 Bb2 D3 Eb3 D3 Bb2', 'Eb G Bb', 'Eb4 G4 Bb4'),
    'Bb': ('Bb1', 'Bb2 F2 Bb2 C3 Bb2 F2', 'Bb D F', 'D4 F4 Bb4'),
    'Bb7': ('Bb1', 'Bb2 F2 Bb2 Ab2 Bb2 F2', 'Bb D F Ab', 'D4 Ab4 Bb4'),
    'Gm': ('G1', 'G2 D2 G2 Ab2 G2 D2', 'G Bb D', 'D4 G4 Bb4'),
    'A7b9': ('A1', 'A2 E2 A2 Bb2 A2 E2', 'A C# E G Bb', 'C#4 G4 Bb4'),
    'C#o7': ('C#2', 'C#3 Bb2 C#3 E3 C#3 Bb2', 'C# E G Bb', 'E4 G4 Bb4'),
    'A/C#': ('C#2', 'C#3 A2 C#3 D3 C#3 A2', 'A C# E G', 'C#4 G4 A4'),
    'Dm/C': ('C2', 'C3 A2 C3 D3 C3 A2', 'D F A C', 'C4 F4 A4'),
    'Bo': ('B1', 'B2 F2 B2 C3 B2 F2', 'B D F A', 'D4 F4 A4'),
    'Ebm': ('Eb2', 'Eb3 Bb2 Eb3 E3 Eb3 Bb2', 'Eb Gb Bb', 'Eb4 Gb4 Bb4'),
    'Em': ('E2', 'E3 B2 E3 F3 E3 B2', 'E G B', 'E4 G4 B4'),
    'Fm': ('F2', 'F3 C3 F3 Gb3 F3 C3', 'F Ab C', 'F4 Ab4 C5'),
}

NER_M1 = ("D4:2 Eb4:1 D4:3 | C4:2 Bb3:1 A3:3 | D4:2 Eb4:1 F4:3 | G4:2 F4:1 Eb4:3 | "
          "F4:2 Eb4:1 D4:3 | D4:2 C4:1 Bb3:3 | A3:2 Bb3:1 C#4:3 | E4:2 D4:1 C#4:3")
NER_M2 = ("G4:2 Ab4:1 G4:3 | F4:2 Eb4:1 D4:3 | D4:2 Eb4:1 F4:3 | G4:2 F4:1 Eb4:3 | "
          "F4:2 G4:1 Ab4:3 | Bb4:2 A4:1 G4:3 | F4:2 E4:1 D4:3 | C#4:6")
NER_LAM = ("A4:2 Bb4:1 A4:3 | G4:2 A4:1 E4:3 | F4:2 G4:1 F4:3 | D4:2 F4:1 A4:3 | "
           "G4:2 F4:1 D4:3 | Bb3:2 C4:1 D4:3 | E4:2 F4:1 E4:3 | D4:2 C#4:1 A3:3")
NER_CELDA = "D4:2 Eb4:1 D4:3 | C4:2 Bb3:1 A3:3"


def nerea():
    global rng
    rng = np.random.default_rng(20261011)
    p = Partitura('nerea', 112, 6, 60.0 / 104 / 3)
    AC = NEREA_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c
    m1 = ['Dm', 'Dm', 'Dm', 'Eb/D', 'Bb', 'Gm', 'A7b9', 'A7b9']
    m2 = ['Gm', 'Gm', 'Dm', 'Eb/D', 'Bb7', 'C#o7', 'A7b9', 'A7b9']
    lam = ['Dm', 'A/C#', 'Dm/C', 'Bo', 'Bb', 'Bb', 'A7b9', 'A7b9']
    pedal = ['Dm', 'Dm', 'Dm', 'Eb/D']
    armonia(1, pedal * 3 + ['Dm', 'Dm', 'A7b9', 'A7b9'])
    armonia(17, m1 + m2 + lam + m1)
    armonia(49, ['Dm', 'Dm', 'Ebm', 'Ebm', 'Em', 'Em', 'Fm', 'Fm'] + ['A7b9'] * 8)
    armonia(65, m1 + m2 + lam + m1)
    armonia(97, pedal + ['Dm', 'Eb/D'] * 2 + ['Bb', 'Gm', 'A7b9', 'A7b9'] + ['Dm', 'Eb/D', 'A7b9', 'A7b9'])

    def riff(c0, c1, v0, v1=None, inst='chelos', transp=0, art='stac'):
        """El riff que no para: raiz, quinta, raiz, la vecina de arriba
        (medio tono: el mib de re), raiz, quinta. Una ola que se arrastra."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for k, nm in enumerate(AC[arm[c]][1].split()):
                p.nota(inst, midi(nm) + transp, c, k, 1, v * (1.0, 0.7, 0.82, 0.95, 0.72, 0.8)[k], art)

    def bajos(c0, c1, v0, v1=None, inst='contrabajos'):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0])
            p.nota(inst, r, c, 0, 3, v, 'marc')
            p.nota(inst, r, c, 3, 3, v * 0.8, 'marc')

    def arpa_ola(c0, c1, v0, v1=None, paso_=1.0, desde='D4'):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            cuantas = int(round(6 / paso_))
            arriba = subir(_pcs(AC[arm[c]][2]), midi(desde), cuantas // 2 + 1 + (1 if paso_ < 1 else 0))
            figura = arriba + arriba[-2:0:-1]
            for k in range(cuantas):
                m = figura[k % len(figura)]
                p.nota('arpa', m, c, k * paso_, paso_, v * (0.8 + 0.2 * (m - midi(desde)) / 24.0))

    def tremolo(c0, c1, v0, v1=None, inst='violines', transp=12):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for nm in AC[arm[c]][3].split():
                p.nota(inst, midi(nm) + transp, c, 0, 6, v, 'trem')

    def golpes_metal(c0, c1, v, posiciones=(2, 5)):
        """Golpes de metales en los contratiempos del 6/8."""
        for c in range(c0, c1 + 1):
            r = midi(AC[arm[c]][0]) + 12
            voces = subir(_pcs(AC[arm[c]][2]), r, 3)
            for pos in posiciones:
                for m in voces:
                    p.nota('trombones', m, c, pos, 1, v, 'stac')

    def corazon(c0, c1, v0, v1=None):
        """El corazon maldito en los timbales: lub (re) - dub (la)."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            p.nota('timbales', 'D2', c, 0, 1, v)
            p.nota('timbales', 'A1', c, 1, 1, v * 0.7)

    def redoble(c, pos, dur, m, v0, v1, ritmo=0.07):
        t = 0.0
        k = 0
        while t < dur * p.u - 0.02:
            p.nota('timbales', m, c, pos + t / p.u, 0.5, (v0 + (v1 - v0) * t / (dur * p.u)) * (0.85 + 0.15 * (k % 2)))
            t += ritmo * (1 + 0.08 * rng.standard_normal())
            k += 1

    def olas_rompen(c0, c1, v, cada=4):
        """Tambores que rompen como olas: bombo grave en los dos pulsos,
        tom grave en los contratiempos, el marco que empuja en corcheas."""
        p.patron('bombo', 'X..x..', c0, c1, 1.0, v)
        p.patron('tom_grave', '..x..x', c0, c1, 1.0, v * 0.75)
        p.patron('marco', 'xooxoo', c0, c1, 1.0, v * 0.55)
        for c in range(c0, c1 + 1):
            if (c - c0) % cada == 0:
                p.nota('timbales', raiz_timbal(AC[arm[c]][2]), c, 0, 2, v * 0.95)
            if (c - c0) % cada == cada - 1:
                p.patron('tom_grave', 'xxxxxx', c, c, 0.5, v * 0.6, offset=3.0)

    def canto(c0, c1, v, posiciones=(0, 2, 3), vocal=1.0):
        """El coro en golpes cortos sobre las voces del acorde."""
        for c in range(c0, c1 + 1):
            for pos in posiciones:
                for nm in AC[arm[c]][3].split():
                    p.nota('coro_canto', nm, c, pos, 1, v * (1.0 if pos == 0 else 0.8), 'stac', vocal=vocal)
                p.nota('coro_canto', midi(AC[arm[c]][0]) + 12, c, pos, 1, v, 'stac', vocal=vocal)

    def subida(c, compases, v, base=('D5', 'Eb5', 'E5', 'A4', 'Bb4'), semitonos=12):
        """Subida disonante: un racimo de cuerdas a medio tono que sube."""
        for nm in base:
            p.nota('subida', nm, c, 0, 6 * compases, v, 'cresc', gl=float(semitonos))

    # ------------------------------------------------ INTRO (1-16): el corazon bajo el agua
    p.seccion(1, 'intro')
    corazon(1, 16, 0.3, 0.55)
    p.nota('sub', 'D2', 1, 0, 6 * 8, 0.5, 'swell')
    p.golpe('ballena', 1, 2, 0.75, dur=5.5, puntos=[(0, 73.4), (0.45, 103.8), (1, 87.3)], brillo=170.0, pan=-0.35)
    p.golpe('ballena', 8, 0, 0.6, dur=5.0, puntos=[(0, 110.0), (0.5, 155.6), (1, 146.8)], brillo=200.0, pan=0.35)
    for c in range(2, 9):
        p.nota('gotas', int(rng.choice([midi('D5'), midi('Eb5'), midi('A5'), midi('F5')])), c, float(rng.choice([1, 2, 4])), 1,
               0.4 * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.6, 0.6))
    riff(5, 16, 0.32, 0.62)
    bajos(9, 16, 0.4, 0.6)
    arpa_ola(9, 16, 0.3, 0.42)
    p.patron('bombo', 'X.....', 9, 12, 1.0, 0.5)
    p.patron('bombo', 'X..x..', 13, 16, 1.0, 0.6)
    p.patron('tom_grave', '..x..x', 13, 16, 1.0, 0.45)
    p.acorde('trompas', 'D3 A3', 9, 0, 12, 0.5, 'swell')
    p.acorde('trompas', 'Eb3 Bb3', 12, 0, 6, 0.5, 'swell')
    p.melodia('armonica', 'mp ' + NER_CELDA, 9, transp=12)
    p.melodia('trompas', 'mf ' + NER_CELDA, 13, lig=False)
    p.acorde('trompas', 'C#3 G3 Bb3', 15, 0, 12, 0.6, 'cresc')
    redoble(16, 0, 6, 'A1', 0.3, 0.9)
    subida(15, 2, 0.45, base=('A4', 'Bb4', 'C#5'), semitonos=7)
    p.golpe('olas', 15, 0, 0.7, dur=12 * p.u, pan0=-0.3, pan1=0.3, cresta=0.97)

    # ------------------------------------------------ COMBATE (17-48): el tema y el riff
    p.seccion(17, 'combate')
    p.golpe('olas', 17, 0, 0.85, dur=4.5, pan0=0.0, pan1=0.0, cresta=0.05, brillo=1.15)
    p.golpe('bombo', 17, 0, 0.95)
    riff(17, 48, 0.68, 0.75)
    riff(25, 48, 0.4, 0.48, inst='violas', transp=12, art='spic')
    bajos(17, 48, 0.62, 0.7)
    arpa_ola(17, 48, 0.4, 0.44)
    olas_rompen(17, 48, 0.72)
    p.melodia('trompas', 'mf ' + NER_M1, 17, lig=False)
    p.melodia('celesta', 'mp ' + NER_M1, 17, transp=24)
    p.melodia('trompas', 'f ' + NER_M2, 25, lig=False)
    p.melodia('trombones', 'mf ' + NER_M2, 25, transp=-12, lig=False)
    tremolo(17, 32, 0.22, 0.32)
    p.melodia('violines', 'f ' + NER_LAM, 33)
    p.melodia('trompas', 'mf ' + NER_LAM, 33, transp=-12, lig=False)
    p.melodia('trompas', 'f ' + NER_M1, 41, lig=False)
    p.melodia('trombones', 'f ' + NER_M1, 41, transp=-12, lig=False)
    p.melodia('violines', 'f ' + NER_M1, 41, transp=12)
    golpes_metal(25, 48, 0.55)
    for c in (24, 32, 40):
        p.golpe('olas', c, 0, 0.55, dur=6 * p.u, pan0=(-0.5 if c != 32 else 0.5), pan1=(0.5 if c != 32 else -0.5), cresta=0.95)
        redoble(c, 3, 3, 'A1', 0.3, 0.75)
    p.golpe('olas', 33, 0, 0.6, dur=4.0, pan0=0.0, pan1=0.0, cresta=0.05)

    # ------------------------------------------------ CRECE (49-64): la marea sube a medios tonos
    p.seccion(49, 'crece')
    for i, c in enumerate(range(49, 57, 2)):
        v = 0.6 + 0.1 * i
        p.melodia('trompas', NER_CELDA, c, vel=v, transp=i, lig=False)
        p.melodia('trombones', NER_CELDA, c, vel=v * 0.9, transp=i - 12, lig=False)
        p.melodia('violines', NER_CELDA, c, vel=v * 0.85, transp=i + 12)
    riff(49, 64, 0.72, 0.95)
    riff(49, 64, 0.45, 0.65, inst='violas', transp=12, art='spic')
    bajos(49, 64, 0.65, 0.9)
    arpa_ola(49, 64, 0.42, 0.55, paso_=0.5)
    p.patron('bombo', 'X..x..', 49, 52, 1.0, 0.75)
    p.patron('bombo', 'X.xX.x', 53, 56, 1.0, 0.8)
    p.patron('bombo', 'XxxXxx', 57, 62, 1.0, 0.8)
    p.patron('tom_grave', '..x..x', 49, 56, 1.0, 0.6)
    p.patron('tom_grave', 'x.xx.x', 57, 62, 1.0, 0.65)
    p.patron('marco', 'xoxxox', 49, 64, 1.0, 0.55)
    p.patron('tom_grave', 'xxxxxxxxxxxx', 63, 64, 0.5, 0.75)
    p.acorde('trompas', 'C#4 G4 Bb4', 57, 0, 6 * 8, 0.75, 'cresc')
    p.acorde('trombones', 'A2 E3 A3', 57, 0, 6 * 8, 0.75, 'cresc')
    p.nota('tuba', 'A1', 57, 0, 6 * 8, 0.7, 'cresc')
    canto(59, 62, 0.55, posiciones=(0, 3), vocal=1.0)
    canto(63, 64, 0.75, posiciones=(0, 2, 3, 5), vocal=1.0)
    golpes_metal(57, 62, 0.6, posiciones=(2, 5))
    redoble(63, 0, 12, 'A1', 0.35, 1.0)
    subida(63, 2, 0.6)
    p.golpe('olas', 63, 0, 0.85, dur=12 * p.u, pan0=-0.2, pan1=0.2, cresta=0.97)
    p.nota('sub', 'A1', 57, 0, 6 * 8, 0.55, 'cresc')

    # ------------------------------------------------ CLIMAX (65-96): rompe la ola gigante
    p.seccion(65, 'CLIMAX')
    for c in (65, 73, 81, 89):
        p.golpe('olas', c, 0, 1.0 if c == 65 else 0.8, dur=4.5, pan0=0.0, pan1=0.0, cresta=0.04, brillo=1.2)
        p.golpe('taiko', c, 0, 1.0)
    p.acorde('trombones', 'D2 A2 D3', 65, 0, 3, 1.0, 'fp')
    p.nota('tuba', 'D2', 65, 0, 3, 1.0, 'fp')
    riff(65, 96, 0.9, 0.95)
    riff(65, 96, 0.6, 0.65, inst='violas', transp=12, art='spic')
    bajos(65, 96, 0.85, 0.9)
    bajos(65, 96, 0.6, 0.65, inst='tuba')
    arpa_ola(65, 96, 0.48, 0.5, paso_=0.5)
    for c, texto in ((65, NER_M1), (73, NER_M2), (81, NER_LAM), (89, NER_M1)):
        p.melodia('trompas', 'ff ' + texto, c, lig=False)
        p.melodia('trombones', 'f ' + texto, c, transp=-12, lig=False)
        p.melodia('violines', 'f ' + texto, c, transp=12)
        p.melodia('coro_canto', 'f ' + texto, c, art='stac', vocal=1.0)
        p.melodia('coro_canto', 'f ' + texto, c, transp=-12, art='stac', vocal=0.6)
    p.melodia('celesta', 'mf ' + NER_M2, 73, transp=24)
    golpes_metal(65, 96, 0.68)
    p.patron('taiko', 'X..X..', 65, 96, 1.0, 0.85)
    p.patron('bombo', '.x...x', 65, 96, 1.0, 0.6)
    p.patron('tom_grave', '..x.xx', 65, 96, 1.0, 0.7)
    p.patron('marco', 'xoooxoxoooxo', 65, 96, 0.5, 0.6)
    for c in range(65, 97):
        p.nota('timbales', raiz_timbal(AC[arm[c]][2]), c, 0, 2, 0.75)
        if c % 4 == 0:
            p.patron('tom_grave', 'xxxxxx', c, c, 0.5, 0.75, offset=3.0)
    redoble(96, 0, 6, 'A1', 0.5, 1.0)

    # ------------------------------------------------ CALMA AMENAZANTE (97-112): algo respira en el fondo
    p.seccion(97, 'acecho')
    corazon(97, 112, 0.42, 0.5)
    p.nota('sub', 'D2', 97, 0, 6 * 12, 0.5, 'swell')
    p.nota('contrabajos', 'D2', 97, 0, 6 * 8, 0.3, 'trem')
    p.nota('contrabajos', 'D2', 105, 0, 6 * 6, 0.32, 'trem')
    p.melodia('armonica', 'mp ' + NER_M1.split(' | ')[0] + ' | ' + ' | '.join(NER_M1.split(' | ')[1:4]), 97, transp=12)
    p.melodia('armonica', 'mp ' + ' | '.join(NER_M1.split(' | ')[4:8]), 105, transp=12)
    for c in range(97, 113):
        if c % 2 == 0:
            p.nota('gotas', int(rng.choice([midi('D5'), midi('Eb5'), midi('A5'), midi('D6')])), c, float(rng.choice([2, 4, 5])), 1,
                   0.38 * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.6, 0.6))
        if c % 4 == 1:
            p.nota('arpa', int(rng.choice([midi('D3'), midi('A3')])), c, 3, 3, 0.4)
    p.golpe('ballena', 99, 0, 0.7, dur=6.0, puntos=[(0, 87.3), (0.4, 116.5), (1, 103.8)], brillo=190.0, pan=0.4)
    p.golpe('ballena', 106, 3, 0.6, dur=5.5, puntos=[(0, 73.4), (0.5, 110.0), (1, 98.0)], brillo=170.0, pan=-0.4)
    for c in (97, 101, 105, 109):
        p.golpe('olas', c, 0, 0.42, dur=4.2, pan0=(-0.6 if c % 8 == 1 else 0.6), pan1=(0.6 if c % 8 == 1 else -0.6))
    p.acorde('violines', 'D5 Eb5', 101, 0, 6 * 4, 0.16, 'trem')
    riff(109, 112, 0.22, 0.3)

    p.automatizar('_mezcla', p.respiro([(1, 2.5), (16, 1.0), (17, 0), (48, 0), (64, 0), (65, 0), (96, 0), (97, 3.0), (113, 2.5)],
                                       65, 1.0 / 6))
    return p


def instrumentos_nerea():
    P = presets()
    P['violines'].update(b0=0.22, bk=0.5)
    P['trompas'].update(V=5, det=4.5)
    P['chelos'].update(b0=0.28, bk=0.6, hum_t=0.004)
    P['contrabajos'].update(hum_t=0.004)
    coro_canto = dict(P['coro'], vocales=('o', 'a'), tilt=1.05, suave=0.45, V=7, det=8.0, vib=(5.0, 6, 0.3, 0.5), ataque=0.02,
                      soltar=0.15, ruido=((400, 3000, 0.07, 'soplo'),), disp=0.012, hum_t=0.004, mono=False)
    armonica = dict(timbre=t_armonica, B=6, V=2, det=4.0, pan=-0.15, ancho=0.3, vib=(5.0, 0, 0.5, 0.5), am=(5.5, 0.07),
                    glide=0.06, ataque=0.12, soltar=1.1, b0=0.25, bk=0.5, bexp=1.0, mono=True, hum_t=0.006,
                    ruido=((1500, 5000, 0.004, 'nivel'),))
    sub = dict(timbre=t_seno, B=1, V=1, det=0.0, pan=0.0, ancho=0.0, vib=(5.0, 0, 0.5, 0.5), glide=0.2, ataque=0.8,
               soltar=1.2, b0=0.0, bk=0.0, bexp=1.0)
    subida_ = dict(P['violines'], V=3, det=8.0, pan=0.0, ancho=0.6, vib=(5.5, 0, 0.3, 0.4), ataque=0.3, soltar=0.08, b0=0.3, bk=0.5)
    sala = {'sala': respuesta_sala(3.4, 0.03, 5500, semilla=3, graves=1.15, agudos=0.5),
            'camara': respuesta_sala(1.0, 0.01, 6000, semilla=4, graves=1.0, agudos=0.6, densidad=0.01)}
    tam = lambda v: _nivel(v)
    I = {
        'sub': dict(tipo='frase', P=sub, gan=-12, eq=[('pa', 28), ('pb', 220)], envios={'sala': 0.05}),
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-8, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2500)], envios={'sala': 0.12}),
        'chelos': dict(tipo='frase', P=P['chelos'], gan=-6, eq=[('pa', 60), ('pico', 250, -3, 1.0), ('pico', 1500, 2, 1.0), ('pb', 6000)],
                       envios={'sala': 0.2, 'camara': 0.1}),
        'violas': dict(tipo='frase', P=P['violas'], gan=-10, eq=[('pa', 150), ('pico', 300, -2, 1.0), ('pb', 7000)], envios={'sala': 0.3}),
        'violines': dict(tipo='frase', P=P['violines'], gan=-8, eq=[('pa', 220), ('pico', 3000, 1.0, 1.0), ('pb', 8500)], envios={'sala': 0.38}),
        'subida': dict(tipo='frase', P=subida_, gan=-12, eq=[('pa', 300), ('pb', 7500)], envios={'sala': 0.4}),
        'trompas': dict(tipo='frase', P=P['trompas'], gan=-3.5, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pico', 1200, 1.5, 1.0), ('pb', 6500)],
                        envios={'sala': 0.38}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-7, eq=[('pa', 60), ('pico', 250, -2, 1.0), ('pb', 6000)], envios={'sala': 0.3}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-9, eq=[('pa', 30), ('pb', 1800)], envios={'sala': 0.12}),
        'coro_canto': dict(tipo='frase', P=coro_canto, gan=-7, eq=[('pa', 110), ('pico', 350, -2.5, 1.0), ('pico', 2500, 1.5, 1.0), ('pb', 8000)],
                           envios={'sala': 0.4}),
        'armonica': dict(tipo='frase', P=armonica, gan=-7, eq=[('pa', 200), ('pb', 7000)], envios={'sala': 0.55}),
        'arpa': dict(tipo='nota_golpe', fn=arpa, pan=lambda nt: -0.5 + 0.015 * (nt.m - 50), gan=-7, eq=[('pa', 90), ('pb', 8000)],
                     envios={'sala': 0.42}),
        'celesta': dict(tipo='nota_golpe', fn=celesta, pan=lambda nt: 0.35 - 0.01 * (nt.m - 72), gan=-14, eq=[('pa', 300), ('pb', 7500)],
                        envios={'sala': 0.6}),
        'gotas': dict(tipo='nota_golpe', fn=gota, pan=0.0, gan=-13, eq=[('pa', 300), ('pb', 7000)], envios={'sala': 0.65}),
        'timbales': dict(tipo='nota_golpe', fn=timbal, pan=0.12, gan=-6, eq=[('pa', 40), ('pb', 4500)], envios={'sala': 0.22, 'camara': 0.3}),
        'bombo': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(tam(v), var, 0.85), pan=0.0, gan=-6, eq=[('pa', 32), ('pb', 3000)],
                      envios={'sala': 0.18, 'camara': 0.3}),
        'taiko': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(tam(v), var, 1.0), pan=0.0, gan=-6, eq=[('pa', 32), ('pb', 3500)],
                      envios={'sala': 0.2, 'camara': 0.3}),
        'tom_grave': dict(tipo='golpe', fn=lambda v, var, **kw: tom(92.0, tam(v), var, 0.2), pan=0.25, gan=-9, eq=[('pa', 60), ('pb', 5000)],
                          envios={'sala': 0.15, 'camara': 0.35}),
        'marco': dict(tipo='golpe', fn=lambda v, var, **kw: marco(tam(v), var), pan=-0.25, gan=-12, eq=[('pa', 80), ('pb', 4500)],
                      envios={'sala': 0.15, 'camara': 0.3}),
        'olas': dict(tipo='golpe', fn=lambda v, var, dur=4.0, pan0=-0.6, pan1=0.6, cresta=0.55, brillo=1.0, **kw:
                     ola(dur, pan0, pan1, cresta, brillo), gan=-14, eq=[('pa', 50), ('pb', 3000)], envios={'sala': 0.3}),
        'ballena': dict(tipo='golpe', fn=lambda v, var, dur, puntos, brillo=650.0, **kw: ballena(dur, puntos, brillo), gan=-11,
                        eq=[('pa', 45), ('pb', 1600)], envios={'sala': 0.7}),
    }
    return I, sala


# ======================================================================
#  AERALIS, Reina del Vendaval: musica de COMBATE. Mi menor frigio (fa
#  natural), 4/4 a 160. Suena a viento: flauta y flauta de pan que aullan en
#  rafagas, cuerdas en spiccato que no paran, toms y redobles de caja como
#  rachas de tormenta, rafagas que cruzan, truenos y campanillas.
# ======================================================================
AER_AC = {
    # acorde: (raiz grave, celdas de spiccato (pulsos 1-3 / 2-4), notas del acorde, voces)
    'Em': ('E2', ('E4 B3 E4 F4', 'E4 B3 G4 F4'), 'E G B', 'E4 G4 B4'),
    'F/E': ('E2', ('F4 C4 F4 E4', 'F4 C4 A4 G4'), 'F A C', 'F4 A4 C5'),
    'C': ('C2', ('E4 C4 E4 G4', 'E4 C4 G4 F4'), 'C E G', 'E4 G4 C5'),
    'B7': ('B1', ('D#4 B3 D#4 F#4', 'D#4 B3 A4 F#4'), 'B D# F# A', 'D#4 F#4 A4'),
    'Am': ('A1', ('C4 A3 C4 E4', 'C4 A3 E4 D4'), 'A C E', 'C4 E4 A4'),
    'F': ('F1', ('C4 A3 C4 F4', 'C4 A3 F4 E4'), 'F A C', 'C4 F4 A4'),
    'B7/D#': ('D#2', ('D#4 B3 D#4 F#4', 'D#4 B3 A4 F#4'), 'B D# F# A', 'D#4 F#4 A4'),
    'Em/D': ('D2', ('E4 B3 E4 F4', 'E4 B3 G4 F4'), 'E G B', 'D4 G4 B4'),
    'C#o': ('C#2', ('E4 C#4 E4 G4', 'E4 C#4 G4 E4'), 'C# E G B', 'E4 G4 B4'),
    'Fm': ('F2', ('F4 C4 F4 Gb4', 'F4 C4 Ab4 Gb4'), 'F Ab C', 'F4 Ab4 C5'),
    'F#m': ('F#2', ('F#4 C#4 F#4 G4', 'F#4 C#4 A4 G4'), 'F# A C#', 'F#4 A4 C#5'),
    'Gm': ('G2', ('G4 D4 G4 Ab4', 'G4 D4 Bb4 Ab4'), 'G Bb D', 'G4 Bb4 D5'),
    'B7b9': ('B1', ('D#4 B3 D#4 F#4', 'D#4 B3 A4 C5'), 'B D# F# A C', 'D#4 A4 C5'),
}

AER_MA = ("B4:0.25 C5:0.25 D5:0.25 E5:0.25 F5:2 E5:1 | G5:0.5 F5:0.5 E5:0.5 D5:0.5 E5:2 | "
          "A4:0.25 B4:0.25 C5:0.25 D5:0.25 E5:2 D5:1 | F5:0.5 E5:0.5 D5:0.5 C5:0.5 B4:2 | "
          "B4:0.25 C5:0.25 D5:0.25 E5:0.25 F5:2 E5:1 | G5:0.5 F5:0.5 E5:0.5 D5:0.5 E5:2 | "
          "A4:0.25 B4:0.25 C5:0.25 D#5:0.25 F#5:2 E5:1 | D#5:1 C5:1 B4:2")
AER_MB = ("E5:0.25 F5:0.25 G5:0.25 A5:0.25 B5:2 A5:1 | C6:0.5 B5:0.5 A5:0.5 G5:0.5 F5:2 | "
          "E5:0.25 F5:0.25 G5:0.25 A5:0.25 C6:2 A5:1 | B5:0.5 A5:0.5 G5:0.5 F5:0.5 E5:2 | "
          "A4:0.25 B4:0.25 C5:0.25 D5:0.25 E5:2 C5:1 | F5:0.5 E5:0.5 D5:0.5 C5:0.5 A4:2 | "
          "B4:0.25 C5:0.25 D#5:0.25 F#5:0.25 A5:2 G5:1 | F#5:2 D#5:2")
AER_MC = ("E5:2 G5:1 F#5:1 | F#5:2 D#5:2 | E5:2 B4:2 | C#5:2 E5:1 G5:1 | "
          "G5:2 E5:1 C5:1 | B4:1 C5:1 D#5:1 F#5:1 | E5:3 F5:1 | D#5:2 B4:2")
AER_CELDA = "B4:0.25 C5:0.25 D5:0.25 E5:0.25 F5:2 E5:1 | G5:0.5 F5:0.5 E5:0.5 D5:0.5 E5:2"


def aeralis():
    global rng
    rng = np.random.default_rng(20261012)
    p = Partitura('aeralis', 84, 4, 60.0 / 160)
    AC = AER_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c
    ma = ['Em', 'Em', 'F/E', 'Em', 'C', 'C', 'B7', 'B7']
    mb = ['Em', 'Em', 'F/E', 'Em', 'Am', 'F', 'B7', 'B7']
    mc = ['Em', 'B7/D#', 'Em/D', 'C#o', 'C', 'B7', 'Em', 'B7']
    pedal = ['Em', 'Em', 'F/E', 'Em']
    armonia(1, pedal * 2 + ['Em', 'Em', 'B7', 'B7'])
    armonia(13, ma + mb + mc)
    armonia(37, ['Em', 'Em', 'Fm', 'Fm', 'F#m', 'F#m', 'Gm', 'Gm', 'B7b9', 'B7b9', 'B7b9', 'B7b9'])
    armonia(49, ma + mb + mc)
    armonia(73, ['Em', 'F/E'] * 4 + ['Em', 'F/E', 'B7', 'B7'])

    def spiccato(c0, c1, v0, v1=None, inst='spic', octava=0):
        """Las semicorcheas del vendaval, con el acento 3+3+2."""
        v1 = v0 if v1 is None else v1
        acento = (1.0, 0.62, 0.7, 0.95, 0.62, 0.7, 0.95, 0.66) * 2
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            celdas = AC[arm[c]][1]
            for pulso in range(4):
                for k, nm in enumerate(celdas[pulso % 2].split()):
                    paso_ = pulso * 4 + k
                    p.nota(inst, midi(nm) + 12 * octava, c, paso_ * 0.25, 0.25, v * acento[paso_], 'spic')

    def corcheas(c0, c1, v0, v1=None):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            r = midi(AC[arm[c]][0])
            for k in range(8):
                ac = k in (0, 3, 6)
                p.nota('chelos', r + 12 + (12 if k in (3, 6) else 0), c, k * 0.5, 0.5, v * (1.0 if ac else 0.66), 'marc' if ac else 'stac')
                p.nota('contrabajos', r, c, k * 0.5, 0.5, v * (1.0 if ac else 0.6), 'marc' if ac else 'stac')

    def carrera(c0, c1, v0, v1=None, desde='E4'):
        """Rafagas de cuerdas: arpegio ligado que sube dos octavas y baja."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            arriba = subir(_pcs(AC[arm[c]][2]), midi(desde), 9)
            figura = arriba + arriba[-2:0:-1]
            p._fr += 1
            for k in range(16):
                p.nota('carrera', figura[k % len(figura)], c, k * 0.25, 0.25, v * (1.0 if k % 4 == 0 else 0.78), 'leg', lig=True, frase=p._fr)

    def golpes_metal(c0, c1, v, posiciones=(1.5, 3.0)):
        for c in range(c0, c1 + 1):
            voces = subir(_pcs(AC[arm[c]][2]), midi(AC[arm[c]][0]) + 12, 3)
            for pos in posiciones:
                for m in voces:
                    p.nota('trombones', m, c, pos, 0.5, v, 'stac')

    def hinchar(c0, c1, v0, v1=None):
        """Trompas graves que se hinchan en cada cambio de armonia."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            if c > c0 and arm[c] == arm[c - 1]:
                continue
            dur = 4
            while c + dur // 4 <= c1 and arm.get(c + dur // 4) == arm[c]:
                dur += 4
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            p.acorde('trompas', AC[arm[c]][3], c, 0, dur, v, 'fpc', transp=-12)

    def canto(c0, c1, v, patron='X..X..X.', vocal=1.0):
        """El coro en golpes cortos (3+3+2) sobre las voces del acorde."""
        for c in range(c0, c1 + 1):
            for k, ch in enumerate(patron):
                if ch in 'Xx':
                    fuerza = v * (1.0 if ch == 'X' else 0.75)
                    for nm in AC[arm[c]][3].split():
                        p.nota('coro_canto', nm, c, k * 0.5, 0.5, fuerza, 'stac', vocal=vocal)
                    p.nota('coro_canto', midi(AC[arm[c]][0]) + 12, c, k * 0.5, 0.5, fuerza, 'stac', vocal=vocal)

    def redoble_caja(c, pos, dur, v0, v1):
        k = 0
        t = 0.0
        while t < dur - 1e-6:
            p.golpe('caja', c, pos + t, (v0 + (v1 - v0) * t / dur) * (0.85 + 0.15 * (k % 2)))
            t += 0.125
            k += 1

    def redoble_timbal(c, pos, dur, m, v0, v1):
        t = 0.0
        while t < dur - 1e-6:
            p.nota('timbales', m, c, pos + t, 0.25, v0 + (v1 - v0) * t / dur)
            t += 0.16 * (1 + 0.06 * rng.standard_normal())

    def tormenta(c0, c1, v, caja=False):
        """Tambores de tormenta: bombo, toms rapidos, marco en semicorcheas."""
        p.patron('taiko', 'X.....x.X.....x.', c0, c1, 0.25, v)
        p.patron('tom_grave', '..x..x....x..x..', c0, c1, 0.25, v * 0.75)
        p.patron('tom_medio', '......x.......xx', c0, c1, 0.25, v * 0.65)
        p.patron('marco', 'xoxoxoxoxoxoxoxo', c0, c1, 0.25, v * 0.45)
        if caja:
            p.patron('caja', '....X.......X...', c0, c1, 0.25, v * 0.8)
        for c in range(c0, c1 + 1):
            if (c - c0) % 8 == 7:
                redoble_caja(c, 2, 2, 0.35 * v, 0.95 * v)
                p.patron('tom_medio', 'xxxx', c, c, 0.25, v * 0.7, offset=3.0)

    def latido(c0, c1, v0, v1=None):
        """Un pulso como un corazon: dos golpes graves de tom por compas."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            p.golpe('tom_grave', c, 0, v)
            p.golpe('tom_grave', c, 0.5, v * 0.7)

    def subida(c, compases, v, base=('D#5', 'E5', 'F5', 'B4', 'C5'), semitonos=12):
        for nm in base:
            p.nota('subida', nm, c, 0, 4 * compases, v, 'cresc', gl=float(semitonos))

    def rachas(lista, v, f1=2200.0, compases=2.0):
        for i, c in enumerate(lista):
            a, b = (-0.85, 0.85) if i % 2 == 0 else (0.85, -0.85)
            p.golpe('rafaga', c, 0, v, dur=compases * 4 * p.u, f0=350.0, f1=f1, pan0=a, pan1=b)

    # ------------------------------------------------ INTRO (1-12): se levanta la tormenta
    p.seccion(1, 'intro')
    p.golpe('trueno_lejano', 1, 0, 0.6, pan=-0.3)
    rachas([1, 5, 9], 0.55)
    latido(1, 12, 0.35, 0.55)
    p.nota('contrabajos', 'E2', 1, 0, 32, 0.3, 'trem')
    spiccato(3, 12, 0.3, 0.7)
    corcheas(5, 12, 0.4, 0.62)
    p.patron('tom_medio', '......x.......x.', 5, 8, 0.25, 0.4)
    p.melodia('flauta', 'mf ' + AER_CELDA, 7)
    tormenta(9, 12, 0.6)
    p.acorde('trompas', 'D#3 F#3 A3', 11, 0, 8, 0.65, 'cresc')
    redoble_caja(12, 0, 4, 0.3, 0.95)
    redoble_timbal(12, 2, 2, 'B1', 0.4, 0.9)
    subida(11, 2, 0.45, base=('B4', 'C5', 'D#5'), semitonos=7)
    p.golpe('rafaga', 11, 0, 0.7, dur=8 * p.u, f0=300.0, f1=2600.0, pan0=-0.6, pan1=0.6)

    # ------------------------------------------------ COMBATE (13-36): el vendaval ataca
    p.seccion(13, 'combate')
    p.golpe('trueno', 13, 0, 0.75, pan=0.3)
    p.golpe('taiko', 13, 0, 0.95)
    spiccato(13, 36, 0.72, 0.78)
    corcheas(13, 36, 0.66, 0.72)
    tormenta(13, 36, 0.78)
    p.melodia('flauta', 'f ' + AER_MA, 13)
    p.melodia('flauta', 'f ' + AER_MB, 21)
    p.melodia('violines', 'mf ' + AER_MB, 21, transp=-12)
    p.melodia('violines', 'f ' + AER_MC, 29)
    p.melodia('trompas', 'mf ' + AER_MC, 29, transp=-12, lig=False)
    p.melodia('quena', 'mp ' + AER_MC, 29)
    hinchar(13, 28, 0.45, 0.55)
    golpes_metal(21, 36, 0.55)
    for c in range(13, 37, 8):
        p.nota('timbales', raiz_timbal(AC[arm[c]][2]), c, 0, 2, 0.8)
    rachas([20, 28, 36], 0.5, compases=1.0)

    # ------------------------------------------------ CRECE (37-48): la tormenta sube a medios tonos
    p.seccion(37, 'crece')
    for i, c in enumerate(range(37, 45, 2)):
        v = 0.6 + 0.1 * i
        p.melodia('flauta', AER_CELDA, c, vel=v, transp=i)
        p.melodia('violines', AER_CELDA, c, vel=v * 0.9, transp=i - 12)
        p.melodia('trompas', AER_CELDA, c, vel=v * 0.85, transp=i - 24, lig=False)
    spiccato(37, 48, 0.75, 0.95)
    corcheas(37, 48, 0.7, 0.9)
    p.patron('taiko', 'X.....x.X.....x.', 37, 40, 0.25, 0.8)
    p.patron('taiko', 'X..x..x.X..x..x.', 41, 46, 0.25, 0.85)
    p.patron('tom_grave', '..x..x....x..x..', 37, 46, 0.25, 0.65)
    p.patron('tom_medio', '......x.......xx', 37, 46, 0.25, 0.6)
    p.patron('marco', 'xoxoxoxoxoxoxoxo', 37, 48, 0.25, 0.5)
    for c in (38, 40, 42, 44):
        redoble_caja(c, 3, 1, 0.4, 0.85)
    p.acorde('trompas', 'D#4 A4 C5', 45, 0, 16, 0.75, 'cresc', transp=-12)
    p.acorde('trombones', 'B2 F#3 B3', 45, 0, 16, 0.75, 'cresc')
    p.nota('tuba', 'B1', 45, 0, 16, 0.7, 'cresc')
    canto(45, 46, 0.55, 'X..X..X.')
    canto(47, 48, 0.75, 'X.XX.XXX')
    golpes_metal(45, 47, 0.6)
    redoble_caja(47, 0, 8, 0.4, 1.0)
    redoble_timbal(47, 0, 8, 'B1', 0.35, 1.0)
    p.patron('tom_grave', 'x.x.x.x.x.x.x.x.', 48, 48, 0.25, 0.8)
    p.patron('tom_medio', '.x.x.x.x.x.x.x.x', 48, 48, 0.25, 0.75)
    subida(47, 2, 0.6)
    p.golpe('trueno_lejano', 45, 0, 0.75, pan=0.4)
    p.golpe('rafaga', 46, 0, 0.8, dur=12 * p.u, f0=300.0, f1=2600.0, pan0=0.6, pan1=-0.6)

    # ------------------------------------------------ CLIMAX (49-72): el ojo de la tormenta encima
    p.seccion(49, 'CLIMAX')
    for c in (49, 57, 65):
        p.golpe('trueno', c, 0, 0.95 if c == 49 else 0.8, pan=(-0.3 if c == 57 else 0.3))
        p.golpe('taiko', c, 0, 1.0)
        p.nota('timbales', raiz_timbal(AC[arm[c]][2]), c, 0, 2, 1.0)
    p.acorde('trombones', 'E2 B2 E3', 49, 0, 2, 1.0, 'fp')
    p.nota('tuba', 'E2', 49, 0, 2, 1.0, 'fp')
    spiccato(49, 72, 0.9, 0.95)
    carrera(49, 72, 0.42, 0.48)
    corcheas(49, 72, 0.85, 0.9)
    for c, texto in ((49, AER_MA), (57, AER_MB), (65, AER_MC)):
        p.melodia('flauta', 'ff ' + texto, c)
        p.melodia('violines', 'f ' + texto, c)
        p.melodia('trompas', 'f ' + texto, c, transp=-12, lig=False)
    canto(49, 72, 0.68, 'X..X..X.')
    golpes_metal(49, 72, 0.7)
    for c in range(49, 73):
        p.nota('tuba', AC[arm[c]][0], c, 0, 2, 0.6, 'marc')
    tormenta(49, 72, 0.92, caja=True)
    rachas([56, 64], 0.6, compases=1.0)

    # ------------------------------------------------ ACECHO (73-84): el viento busca
    p.seccion(73, 'acecho')
    p.golpe('trueno_lejano', 73, 0, 0.7, pan=0.3)
    p.golpe('trueno_lejano', 79, 0, 0.55, pan=-0.4)
    latido(73, 84, 0.45, 0.5)
    p.nota('contrabajos', 'E2', 73, 0, 48, 0.32, 'trem')
    p.nota('chelos', 'E3', 73, 0, 32, 0.22, 'swell')
    rachas([73, 75, 77, 79, 81, 83], 0.45)
    for c in (74, 76, 78, 80, 82):
        for k in range(int(rng.integers(1, 3))):
            p.nota('campanillas', int(rng.choice([midi('E5'), midi('F5'), midi('B5')])), c, float(rng.choice([0.5, 1.5, 2.5])) + 0.3 * k, 1,
                   0.35 * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.7, 0.7))
    p.melodia('quena', 'mp ' + AER_CELDA, 77, transp=-12)
    p.melodia('quena', 'p ' + AER_CELDA, 81, transp=-12)
    p.acorde('violines', 'E5 F5', 81, 0, 16, 0.16, 'trem')
    spiccato(83, 84, 0.25, 0.32)

    p.automatizar('_mezcla', p.respiro([(1, 6.0), (12, 3.0), (13, 0), (36, 0), (48, 0), (49, 0), (72, 0), (73, 7.5), (85, 6.0)], 49))
    return p


def instrumentos_aeralis():
    P = presets()
    flauta = dict(timbre=t_flauta, B=6, V=1, det=0.0, pan=0.08, ancho=0.0, vib=(5.3, 14, 0.18, 0.3), glide=0.035, ataque=0.035,
                  soltar=0.2, b0=0.14, bk=0.7, bexp=1.0, ruido=((1500, 6000, 0.035, 'nivel'), (900, 4500, 0.16, 'soplo')),
                  mono=True, hum_t=0.004)
    quena = dict(timbre=t_quena, B=6, V=1, det=0.0, pan=-0.2, ancho=0.0, vib=(5.0, 8, 0.35, 0.4), glide=0.03, ataque=0.035,
                 soltar=0.3, b0=0.2, bk=0.55, bexp=1.0, ruido=((1200, 6000, 0.06, 'nivel'), (800, 5000, 0.3, 'soplo')),
                 mono=True, hum_t=0.006)
    spic = dict(P['violines'], V=4, det=5.0, pan=-0.2, ancho=0.55, b0=0.3, bk=0.55, hum_t=0.004, hum_v=0.05, disp=0.008,
                ruido=((3000, 8000, 0.015, 'nivel'),))
    carrera = dict(P['violines'], V=4, det=5.0, pan=0.35, ancho=0.4, vib=(5.6, 0, 0.3, 0.4), glide=0.012, ataque=0.03,
                   soltar=0.2, b0=0.25, bk=0.45, mono=True, hum_t=0.004, ruido=((2500, 8000, 0.008, 'nivel'),))
    violines = dict(P['violines'], b0=0.25, bk=0.5, pan=0.25)
    chelos = dict(P['chelos'], b0=0.3, bk=0.55, hum_t=0.004)
    contrabajos = dict(P['contrabajos'], hum_t=0.004)
    coro_canto = dict(P['coro'], vocales=('o', 'a'), tilt=1.05, suave=0.45, V=7, det=8.0, vib=(5.0, 6, 0.3, 0.5), ataque=0.02,
                      soltar=0.15, ruido=((400, 3000, 0.07, 'soplo'),), disp=0.012, hum_t=0.004, mono=False)
    subida_ = dict(P['violines'], V=3, det=8.0, pan=0.0, ancho=0.6, vib=(5.5, 0, 0.3, 0.4), ataque=0.3, soltar=0.08, b0=0.3, bk=0.5)
    sala = {'sala': respuesta_sala(2.8, 0.025, 7000, semilla=5, graves=1.1, agudos=0.6),
            'camara': respuesta_sala(0.9, 0.01, 6500, semilla=6, graves=1.0, agudos=0.6, densidad=0.01),
            'eco': respuesta_eco(0.75 * 60 / 160, 6, 0.5, 4200)}
    tam = lambda v: _nivel(v)
    I = {
        'contrabajos': dict(tipo='frase', P=contrabajos, gan=-8, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2500)], envios={'sala': 0.1}),
        'chelos': dict(tipo='frase', P=chelos, gan=-8.5, eq=[('pa', 70), ('pico', 250, -3, 1.0), ('pico', 1500, 2, 1.0), ('pb', 6000)],
                       envios={'sala': 0.18}),
        'spic': dict(tipo='frase', P=spic, gan=-4, eq=[('pa', 180), ('pico', 300, -2, 1.0), ('pico', 3000, 1.0, 1.0), ('pb', 8500)],
                     envios={'sala': 0.25, 'camara': 0.15}),
        'carrera': dict(tipo='frase', P=carrera, gan=-11, eq=[('pa', 220), ('pico', 300, -2, 1.0), ('pb', 8000)], envios={'sala': 0.35}),
        'violines': dict(tipo='frase', P=violines, gan=-7.5, eq=[('pa', 200), ('pb', 8500)], envios={'sala': 0.35}),
        'subida': dict(tipo='frase', P=subida_, gan=-12, eq=[('pa', 300), ('pb', 7500)], envios={'sala': 0.4}),
        'flauta': dict(tipo='frase', P=flauta, gan=-5, eq=[('pa', 280), ('pb', 8500)], envios={'sala': 0.38, 'eco': 0.18}),
        'quena': dict(tipo='frase', P=quena, gan=-7, eq=[('pa', 150), ('pb', 7500)], envios={'sala': 0.45, 'eco': 0.25}),
        'trompas': dict(tipo='frase', P=P['trompas'], gan=-4.5, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pico', 1200, 1.0, 1.0), ('pb', 6500)],
                        envios={'sala': 0.35}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-7.5, eq=[('pa', 60), ('pico', 250, -2, 1.0), ('pb', 6000)], envios={'sala': 0.28}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-10, eq=[('pa', 30), ('pb', 1800)], envios={'sala': 0.12}),
        'coro_canto': dict(tipo='frase', P=coro_canto, gan=-7.5, eq=[('pa', 110), ('pico', 350, -2.5, 1.0), ('pico', 2500, 1.5, 1.0), ('pb', 8000)],
                           envios={'sala': 0.38}),
        'campanillas': dict(tipo='nota_golpe', fn=campanilla, pan=0.0, gan=-15, eq=[('pa', 500), ('pb', 7500)], envios={'sala': 0.6}),
        'timbales': dict(tipo='nota_golpe', fn=timbal, pan=0.1, gan=-7, eq=[('pa', 40), ('pb', 4500)], envios={'sala': 0.2, 'camara': 0.3}),
        'taiko': dict(tipo='golpe', fn=lambda v, var, **kw: bombo_seco(tam(v), var), pan=0.0, gan=-5, eq=[('pa', 35), ('pb', 3500)],
                      envios={'sala': 0.12, 'camara': 0.35}),
        'tom_grave': dict(tipo='golpe', fn=lambda v, var, **kw: tom(100.0, tam(v), var, 0.16), pan=0.25, gan=-8, eq=[('pa', 70), ('pb', 5000)],
                          envios={'sala': 0.12, 'camara': 0.35}),
        'tom_medio': dict(tipo='golpe', fn=lambda v, var, **kw: tom(150.0, tam(v), var, 0.14), pan=-0.3, gan=-10, eq=[('pa', 90), ('pb', 5500)],
                          envios={'sala': 0.12, 'camara': 0.35}),
        'caja': dict(tipo='golpe', fn=lambda v, var, **kw: caja(tam(v), var), pan=0.05, gan=-9, eq=[('pa', 150), ('pb', 6000)],
                     envios={'sala': 0.2, 'camara': 0.35}),
        'marco': dict(tipo='golpe', fn=lambda v, var, **kw: marco(tam(v), var), pan=0.15, gan=-14, eq=[('pa', 80), ('pb', 5000)],
                      envios={'sala': 0.12, 'camara': 0.3}),
        'trueno': dict(tipo='golpe', fn=lambda v, var, **kw: trueno(3, var), gan=-8, eq=[('pa', 30), ('pb', 2500)], envios={'sala': 0.35}),
        'platillos': dict(tipo='golpe', fn=lambda v, var, **kw: platillo(tam(v), var), pan=0.2, gan=-14, eq=[('pa', 400), ('pb', 7000)],
                          envios={'sala': 0.35}),
        'trueno_lejano': dict(tipo='golpe', fn=lambda v, var, **kw: trueno_lejano(5.0), gan=-9, eq=[('pa', 30), ('pb', 900)],
                              envios={'sala': 0.45}),
        'rafaga': dict(tipo='golpe', fn=lambda v, var, dur=3.0, f0=400.0, f1=2400.0, pan0=-0.8, pan1=0.8, **kw:
                       rafaga_st(dur, f0, f1, pan0, pan1), gan=-15, eq=[('pa', 200), ('pb', 4500)], envios={'sala': 0.3}),
    }
    return I, sala


# ======================================================================
#  RAJANG, el Jaguar de Jade: musica de COMBATE. Do menor frigio (reb), 4/4
#  a 136. Suena a tierra: taikos pesados a medio tiempo sobre el riff del
#  tambor de tronco, marimba grave, kalimba, piedras, sonajas, el dron de la
#  tierra, metales graves y un coro que grita en golpes.
# ======================================================================
RAJ_AC = {
    # acorde: (raiz grave, riff del tronco (8 corcheas), notas del acorde, voces)
    'Cm': ('C2', 'C3 G2 C3 Db3 C3 G2 Bb2 G2', 'C Eb G', 'C4 Eb4 G4'),
    'Db/C': ('C2', 'C3 Ab2 C3 Db3 C3 Ab2 F2 Ab2', 'Db F Ab', 'Db4 F4 Ab4'),
    'Ab': ('Ab1', 'Ab2 Eb2 Ab2 Bb2 Ab2 Eb2 G2 Eb2', 'Ab C Eb', 'C4 Eb4 Ab4'),
    'Fm': ('F1', 'F2 C2 F2 G2 F2 C2 Eb2 C2', 'F Ab C', 'C4 F4 Ab4'),
    'Db': ('Db2', 'Db3 Ab2 Db3 Eb3 Db3 Ab2 C3 Ab2', 'Db F Ab', 'Db4 F4 Ab4'),
    'G7': ('G1', 'G2 D2 G2 Ab2 G2 D2 F2 D2', 'G B D F', 'B3 D4 F4'),
    'G7b9': ('G1', 'G2 D2 G2 Ab2 G2 D2 F2 D2', 'G B D F Ab', 'B3 F4 Ab4'),
}

RAJ_MR = ("C4:1.5 Eb4:1.5 G4:1 | F4:1.5 Eb4:1.5 Db4:0.5 C4:0.5 | C4:1.5 Eb4:1.5 G4:1 | Ab4:1.5 G4:1.5 F4:0.5 Eb4:0.5 | "
          "F4:1.5 Ab4:1.5 C5:1 | Db5:1.5 C5:1.5 Bb4:0.5 Ab4:0.5 | G4:1.5 F4:1.5 Eb4:0.5 D4:0.5 | B3:4")
RAJ_MR2 = ("C4:1.5 Eb4:1.5 G4:1 | F4:1.5 Eb4:1.5 Db4:0.5 C4:0.5 | C4:1.5 Eb4:1.5 G4:1 | Ab4:1.5 G4:1.5 F4:0.5 Eb4:0.5 | "
           "F4:1.5 Ab4:1.5 C5:1 | Db5:1.5 Eb5:1.5 Db5:0.5 C5:0.5 | B4:1.5 Ab4:1.5 G4:0.5 F4:0.5 | G4:4")
RAJ_CELDA = "C4:1.5 Eb4:1.5 G4:1 | F4:1.5 Eb4:1.5 Db4:0.5 C4:0.5"


def rajang():
    global rng
    rng = np.random.default_rng(20261013)
    p = Partitura('rajang', 72, 4, 60.0 / 136)
    AC = RAJ_AC
    arm = {}

    def armonia(desde, lista):
        for i, c in enumerate(lista):
            arm[desde + i] = c
    mr = ['Cm', 'Db/C', 'Cm', 'Ab', 'Fm', 'Db', 'G7', 'G7']
    mr2 = ['Cm', 'Db/C', 'Cm', 'Ab', 'Fm', 'Db', 'G7b9', 'G7b9']
    pedal = ['Cm', 'Cm', 'Cm', 'Db/C']
    armonia(1, ['Cm', 'Cm', 'Cm', 'Db/C', 'Cm', 'Db/C', 'Cm', 'Ab', 'G7', 'G7'])
    armonia(11, mr + mr2 + ['Ab', 'Db', 'G7', 'G7'])
    armonia(31, ['Cm', 'Db/C', 'Cm', 'Db/C', 'Fm', 'Db', 'Ab', 'Db', 'G7b9', 'G7b9'])
    armonia(41, mr + mr2 + ['Ab', 'Db', 'G7b9', 'G7b9'])
    armonia(61, ['Cm', 'Db/C'] * 4 + ['Cm', 'Db/C', 'G7', 'G7'])

    def tronco_riff(c0, c1, v0, v1=None):
        """El riff de la tierra en el tambor de tronco: raiz, quinta y el reb
        (medio tono arriba), acentos 3+3+2."""
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for k, nm in enumerate(AC[arm[c]][1].split()):
                p.nota('tronco', nm, c, k * 0.5, 0.5, v * (1.0 if k in (0, 3, 6) else 0.62))

    def riff_cuerdas(c0, c1, v0, v1=None):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            for k, nm in enumerate(AC[arm[c]][1].split()):
                p.nota('chelos', nm, c, k * 0.5, 0.5, v * (1.0 if k in (0, 3, 6) else 0.65), 'marc' if k in (0, 3, 6) else 'stac')

    def marimba_pat(c0, c1, v0, v1=None, figura16=True):
        v1 = v0 if v1 is None else v1
        acento = (1.0, 0.55, 0.65, 0.9, 0.55, 0.65, 0.9, 0.6) * 2
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            arriba = subir(_pcs(AC[arm[c]][2]), midi(AC[arm[c]][0]) + 12, 7)
            figura = arriba + arriba[-2:0:-1]
            pasos_ = 16 if figura16 else 8
            for k in range(pasos_):
                p.nota('marimba', figura[k % len(figura)], c, k * 4.0 / pasos_, 0.25, v * (acento[k] if figura16 else (1.0 if k % 2 == 0 else 0.7)))

    def dron(c0, c1, v0, v1=None, suave=False):
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

    def guerra(c0, c1, v, lleno=True):
        """Taikos pesados a medio tiempo, timbales graves y marcos que no
        paran, piedras y sonajas."""
        p.patron('taiko', 'X.......X.....x.', c0, c1, 0.25, v)
        p.patron('timbal_grave', '..x...x...x.x..x' if lleno else '......x.......x.', c0, c1, 0.25, v * 0.7)
        p.patron('marco', 'x.ox.ox.x.oxx.ox', c0, c1, 0.25, v * 0.55)
        p.patron('piedras', '..x...x...x...x.', c0, c1, 0.25, v * 0.5)
        p.patron('sonajas', 'x.o.x.o.x.o.x.o.', c0, c1, 0.25, v * 0.45)
        if lleno:
            p.patron('tres', 'x..', c0, c1, 0.25, v * 0.5)
        for c in range(c0, c1 + 1):
            if (c - c0) % 4 == 3:
                p.patron('taiko', 'X.X.XXXX', c, c, 0.25, v * 0.85, offset=2.0)

    def golpes_metal(c0, c1, v, posiciones=(1.5, 3.5)):
        for c in range(c0, c1 + 1):
            voces = subir(_pcs(AC[arm[c]][2]), midi(AC[arm[c]][0]) + 12, 3)
            for pos in posiciones:
                for m in voces:
                    p.nota('trombones', m, c, pos, 0.5, v, 'stac')

    def grito(c, pos, v, vocal=1.0, dur=0.5):
        """Un grito del coro de hombres (HO / HA) en las voces del acorde."""
        r = midi(AC[arm[c]][0]) + 12
        for m in subir(_pcs(AC[arm[c]][2]), r, 3):
            p.nota('canto', m, c, pos, dur, v, 'stac', vocal=vocal)
            p.nota('canto', m + 12, c, pos, dur, v * 0.8, 'stac', vocal=vocal)

    def canto_golpes(c0, c1, v, posiciones=(0, 1.5, 3)):
        for c in range(c0, c1 + 1):
            for i, pos in enumerate(posiciones):
                grito(c, pos, v * (1.0 if i == 0 else 0.8), vocal=(1.0 if i % 2 == 0 else 0.2))

    def corazon(c0, c1, v0, v1=None):
        v1 = v0 if v1 is None else v1
        for c in range(c0, c1 + 1):
            v = v0 + (v1 - v0) * (c - c0) / max(1, c1 - c0)
            p.golpe('taiko', c, 0, v)
            p.golpe('taiko', c, 0.5, v * 0.65)

    def subida(c, compases, v, base=('G3', 'Ab3', 'B3', 'D4'), semitonos=12):
        for nm in base:
            p.nota('subida', nm, c, 0, 4 * compases, v, 'cresc', gl=float(semitonos))

    # ------------------------------------------------ INTRO (1-10): la tierra despierta
    p.seccion(1, 'intro')
    p.golpe('retumbo', 1, 0, 0.75, dur=6.0, f_sub=32.7)
    corazon(1, 10, 0.35, 0.6)
    dron(1, 10, 0.45, 0.6, suave=True)
    tronco_riff(3, 10, 0.35, 0.7)
    p.melodia('kalimba', 'mp ' + RAJ_MR.split(' | ')[0] + ' | ' + ' | '.join(RAJ_MR.split(' | ')[1:4]), 5, transp=12)
    p.patron('piedras', '..x.........x...', 3, 10, 0.25, 0.4)
    p.patron('sonajas', 'x.o.x.o.x.o.x.o.', 5, 10, 0.25, 0.35)
    marimba_pat(7, 10, 0.35, 0.5)
    p.patron('taiko', 'X.......X.......', 7, 8, 0.25, 0.6)
    p.patron('timbal_grave', '......x.......x.', 7, 10, 0.25, 0.5)
    p.acorde('trompas', 'B3 D4 F4', 9, 0, 8, 0.6, 'cresc', transp=-12)
    p.acorde('trombones', 'G2 D3', 9, 0, 8, 0.6, 'cresc')
    p.patron('taiko', 'X.X.X.X.XXXXXXXX', 10, 10, 0.25, 0.8)
    subida(9, 2, 0.4, base=('G3', 'Ab3', 'B3'), semitonos=7)
    p.golpe('semillas', 9, 0, 0.7, dur=8 * p.u, pan=-0.3)
    p.golpe('retumbo', 9, 0, 0.6, dur=4.0, f_sub=49.0)

    # ------------------------------------------------ COMBATE (11-30): el jaguar acecha y ataca
    p.seccion(11, 'combate')
    p.golpe('terremoto', 11, 0, 0.75)
    grito(11, 0, 0.8)
    guerra(11, 18, 0.78, lleno=False)
    guerra(19, 30, 0.85)
    tronco_riff(11, 30, 0.72, 0.78)
    riff_cuerdas(19, 30, 0.55, 0.62)
    marimba_pat(11, 30, 0.5, 0.56)
    dron(11, 30, 0.55, 0.62)
    p.melodia('trompas', 'mf ' + RAJ_MR, 11, lig=False)
    p.melodia('ocarina', 'mf ' + RAJ_MR, 11, transp=12)
    p.melodia('trompas', 'f ' + RAJ_MR2, 19, lig=False)
    p.melodia('trombones', 'mf ' + RAJ_MR2, 19, transp=-12, lig=False)
    p.melodia('ocarina', 'f ' + RAJ_MR2, 19, transp=12)
    golpes_metal(19, 30, 0.55)
    for c in range(11, 31, 2):
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 8, 0.55, 'marc')
    for c in range(27, 31):
        grito(c, 0, 0.7, vocal=1.0)
        grito(c, 1.5, 0.55, vocal=0.2)
    p.acorde('trompas', 'B3 D4 F4', 29, 0, 8, 0.7, 'cresc', transp=-12)
    p.golpe('semillas', 18, 2, 0.6, dur=2 * p.u, pan=0.35)

    # ------------------------------------------------ CRECE (31-40): tiembla el templo
    p.seccion(31, 'crece')
    p.melodia('trompas', 'f ' + RAJ_CELDA, 31, lig=False)
    p.melodia('trombones', 'f ' + RAJ_CELDA, 33, transp=-12, lig=False)
    p.melodia('trompas', 'f ' + RAJ_CELDA, 33, lig=False)
    p.melodia('trompas', 'ff F4:1.5 Ab4:1.5 C5:1 | Db5:1.5 C5:1.5 Bb4:0.5 Ab4:0.5', 35, lig=False)
    p.melodia('ocarina', 'f ' + RAJ_CELDA, 31, transp=12)
    p.melodia('ocarina', 'f ' + RAJ_CELDA, 33, transp=12)
    tronco_riff(31, 40, 0.78, 0.95)
    riff_cuerdas(31, 40, 0.6, 0.85)
    marimba_pat(31, 40, 0.55, 0.7)
    dron(31, 40, 0.62, 0.8)
    p.patron('taiko', 'X.......X.....x.', 31, 34, 0.25, 0.85)
    p.patron('taiko', 'X..x..x.X..x..x.', 35, 38, 0.25, 0.9)
    p.patron('timbal_grave', '..x...x...x.x..x', 31, 38, 0.25, 0.7)
    p.patron('marco', 'xoxoxoxoxoxoxoxo', 31, 40, 0.25, 0.55)
    p.patron('tres', 'x..', 31, 38, 0.25, 0.55)
    p.patron('piedras', '..x...x...x...x.', 31, 40, 0.25, 0.5)
    canto_golpes(37, 38, 0.6, posiciones=(0, 3))
    canto_golpes(39, 40, 0.8, posiciones=(0, 1.5, 3, 3.5))
    golpes_metal(35, 38, 0.65)
    p.acorde('trompas', 'B3 F4 Ab4', 39, 0, 8, 0.8, 'cresc', transp=-12)
    p.acorde('trombones', 'G2 D3 G3', 39, 0, 8, 0.8, 'cresc')
    p.nota('tuba', 'G1', 39, 0, 8, 0.75, 'cresc')
    p.patron('taiko', 'XxXxXxXxXXXXXXXX', 39, 40, 0.25, 0.9)
    p.patron('timbal_grave', 'x.x.x.x.x.x.x.x.', 39, 40, 0.25, 0.8)
    subida(39, 2, 0.55)
    p.golpe('retumbo', 39, 0, 0.8, dur=3.5, f_sub=49.0)
    p.golpe('semillas', 39, 0, 0.9, dur=8 * p.u, pan=0.3)

    # ------------------------------------------------ CLIMAX (41-60): la furia de jade
    p.seccion(41, 'CLIMAX')
    for c in (41, 49):
        p.golpe('terremoto', c, 0, 0.95 if c == 41 else 0.75)
    p.acorde('trombones', 'C2 G2 C3', 41, 0, 2, 1.0, 'fp')
    p.nota('tuba', 'C2', 41, 0, 2, 1.0, 'fp')
    for c, texto in ((41, RAJ_MR), (49, RAJ_MR2)):
        p.melodia('trompas', 'ff ' + texto, c, lig=False)
        p.melodia('trombones', 'f ' + texto, c, transp=-12, lig=False)
        p.melodia('ocarina', 'ff ' + texto, c, transp=12)
        p.melodia('canto', 'f ' + texto, c, art='stac', vocal=1.0)
        p.melodia('canto', 'f ' + texto, c, transp=-12, art='stac', vocal=0.3)
    canto_golpes(41, 56, 0.55, posiciones=(0, 3))
    golpes_metal(41, 60, 0.7)
    guerra(41, 60, 0.95)
    p.patron('taiko', '..X.....X.X.....', 41, 60, 0.25, 0.55)
    tronco_riff(41, 60, 0.85, 0.9)
    riff_cuerdas(41, 60, 0.72, 0.78)
    marimba_pat(41, 60, 0.6, 0.62)
    dron(41, 60, 0.68, 0.72)
    for c in range(41, 61):
        p.nota('tuba', AC[arm[c]][0], c, 0, 2, 0.65, 'marc')
        p.nota('contrabajos', AC[arm[c]][0], c, 0, 4, 0.65, 'marc')
    for c in range(41, 57, 2):
        for k, m in enumerate(subir(_pcs(AC[arm[c]][2]), midi('C5'), 6)):
            p.nota('kalimba', m, c, 0.5 * k, 0.5, 0.35)
    # cierre: Lab - Reb - Sol (b9), todo el coro y los metales
    for c in range(57, 61):
        p.acorde('trompas', AC[arm[c]][3], c, 0, 4, 0.9, 'fpc', transp=-12)
        p.acorde('trombones', ' '.join(_nombre(m) for m in subir(_pcs(AC[arm[c]][2]), midi(AC[arm[c]][0]) + 12, 3)), c, 0, 4, 0.9, 'fpc')
    canto_golpes(57, 60, 0.8, posiciones=(0, 1.5, 3, 3.5))
    p.patron('taiko', 'XxXxXxXxXXXXXXXX', 60, 60, 0.25, 0.95)

    # ------------------------------------------------ ACECHO (61-72): el jaguar ronda en la oscuridad
    p.seccion(61, 'acecho')
    p.golpe('retumbo', 61, 0, 0.6, dur=6.0, f_sub=32.7)
    p.golpe('retumbo', 67, 0, 0.5, dur=5.0, f_sub=32.7)
    corazon(61, 72, 0.45, 0.5)
    dron(61, 72, 0.42, 0.48, suave=True)
    for c in range(61, 73):
        if c % 2 == 1:
            p.nota('kalimba', int(rng.choice([midi('C5'), midi('Db5'), midi('G5'), midi('Eb5')])), c, float(rng.choice([1, 2, 2.5])), 1,
                   0.4 * rng.uniform(0.7, 1.0), pan=rng.uniform(-0.5, 0.5))
    p.melodia('kalimba', 'mp ' + RAJ_CELDA, 65, transp=12)
    p.patron('piedras', '..x.............', 61, 72, 0.25, 0.35)
    p.golpe('semillas', 63, 2, 0.45, dur=2 * p.u, subida_=False, pan=-0.5)
    p.golpe('semillas', 69, 2, 0.45, dur=2 * p.u, subida_=False, pan=0.5)
    tronco_riff(71, 72, 0.25, 0.32)

    p.automatizar('_mezcla', p.respiro([(1, 6.5), (10, 3.0), (11, 0), (30, 0), (40, 0), (41, 0), (60, 0), (61, 8.5), (73, 6.5)], 41))
    return p


def instrumentos_rajang():
    P = presets()
    ocarina = dict(timbre=t_ocarina, B=6, V=1, det=0.0, pan=-0.1, ancho=0.0, vib=(5.6, 10, 0.3, 0.4), glide=0.035, ataque=0.035,
                   soltar=0.2, b0=0.15, bk=0.6, bexp=1.0, ruido=((900, 5000, 0.035, 'nivel'), (700, 4000, 0.18, 'soplo')),
                   mono=True, hum_t=0.005)
    dron_ = dict(timbre=t_dron, B=8, V=2, det=3.0, pan=0.0, ancho=0.15, vib=(5.0, 0, 0.5, 0.5), glide=0.06, ataque=0.15,
                 soltar=0.6, b0=0.05, bk=0.75, bexp=1.0, mono=True, ruido=((150, 1000, 0.03, 'nivel'),), hum_t=0.003)
    canto = dict(P['coro'], voz='B', vocales=('o', 'a'), tilt=1.0, suave=0.4, V=7, det=9.0, vib=(5.0, 6, 0.3, 0.5), ataque=0.02,
                 soltar=0.15, ruido=((350, 2500, 0.08, 'soplo'),), disp=0.012, hum_t=0.004, mono=False)
    chelos = dict(P['chelos'], b0=0.3, bk=0.55, hum_t=0.004)
    subida_ = dict(P['violas'], V=3, det=8.0, pan=0.0, ancho=0.6, vib=(5.5, 0, 0.3, 0.4), ataque=0.3, soltar=0.08, b0=0.3, bk=0.5)
    sala = {'sala': respuesta_sala(2.4, 0.022, 6500, semilla=7, graves=1.1, agudos=0.55, tempranas=16),
            'camara': respuesta_sala(0.8, 0.008, 6000, semilla=8, graves=1.0, agudos=0.6, densidad=0.008, tempranas=12),
            'eco': respuesta_eco(0.75 * 60 / 136, 5, 0.45, 3800)}
    tam = lambda v: _nivel(v)
    I = {
        'contrabajos': dict(tipo='frase', P=P['contrabajos'], gan=-10, eq=[('pa', 35), ('pico', 250, -2, 1.0), ('pb', 2000)], envios={'sala': 0.1}),
        'tuba': dict(tipo='frase', P=P['tuba'], gan=-10, eq=[('pa', 30), ('pb', 1600)], envios={'sala': 0.12}),
        'chelos': dict(tipo='frase', P=chelos, gan=-9, eq=[('pa', 60), ('pico', 250, -3, 1.0), ('pico', 1500, 2, 1.0), ('pb', 5500)],
                       envios={'sala': 0.18}),
        'subida': dict(tipo='frase', P=subida_, gan=-12, eq=[('pa', 200), ('pb', 6500)], envios={'sala': 0.35}),
        'dron': dict(tipo='frase', P=dron_, gan=-10, eq=[('pa', 40), ('pico', 300, -2, 1.0), ('pb', 3000)], envios={'sala': 0.2}),
        'trombones': dict(tipo='frase', P=P['trombones'], gan=-7.5, eq=[('pa', 50), ('pico', 300, -2, 1.0), ('pb', 5500)], envios={'sala': 0.28}),
        'trompas': dict(tipo='frase', P=dict(P['trompas'], V=5), gan=-4, eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pico', 1200, 1.0, 1.0), ('pb', 6500)],
                        envios={'sala': 0.32}),
        'canto': dict(tipo='frase', P=canto, gan=-7, eq=[('pa', 80), ('pico', 300, -2.5, 1.0), ('pico', 2500, 1.0, 1.0), ('pb', 7000)],
                      envios={'sala': 0.35}),
        'ocarina': dict(tipo='frase', P=ocarina, gan=-8, eq=[('pa', 250), ('pb', 7500)], envios={'sala': 0.32, 'eco': 0.14}),
        'kalimba': dict(tipo='nota_golpe', fn=kalimba, pan=0.0, gan=-9, eq=[('pa', 150), ('pb', 7000)], envios={'sala': 0.35, 'eco': 0.15}),
        'marimba': dict(tipo='nota_golpe', fn=marimba, pan=lambda nt: -0.45 + 0.025 * (nt.m - 48), gan=-10,
                        eq=[('pa', 90), ('pico', 300, -2, 1.0), ('pb', 7000)], envios={'sala': 0.22}),
        'tronco': dict(tipo='nota_golpe', fn=tronco, pan=0.3, gan=-7, eq=[('pa', 55), ('pb', 4000)], envios={'sala': 0.18, 'camara': 0.3}),
        'taiko': dict(tipo='golpe', fn=lambda v, var, **kw: taiko(tam(v), var, 1.0), pan=0.0, gan=-4.5, eq=[('pa', 32), ('pb', 3500)],
                      envios={'sala': 0.18, 'camara': 0.35}),
        'tres': dict(tipo='golpe', fn=lambda v, var, **kw: tom(118.0, tam(v), var, 0.18), pan=-0.35, gan=-13, eq=[('pa', 80), ('pb', 4500)],
                     envios={'sala': 0.12, 'camara': 0.35}),
        'timbal_grave': dict(tipo='golpe', fn=lambda v, var, **kw: tom(78.0, tam(v), var, 0.2), pan=0.3, gan=-9, eq=[('pa', 55), ('pb', 4500)],
                             envios={'sala': 0.12, 'camara': 0.35}),
        'marco': dict(tipo='golpe', fn=lambda v, var, **kw: marco(tam(v), var), pan=-0.2, gan=-12, eq=[('pa', 70), ('pb', 4500)],
                      envios={'sala': 0.12, 'camara': 0.35}),
        'sonajas': dict(tipo='golpe', fn=lambda v, var, **kw: sonaja(tam(v), var, brillo=0.7), pan=0.45, gan=-17, eq=[('pa', 1200), ('pb', 6500)],
                        envios={'sala': 0.15}),
        'semillas': dict(tipo='golpe', fn=lambda v, var, dur=0.6, subida_=True, **kw: semillas(dur, subida_), gan=-16,
                         eq=[('pa', 1200), ('pb', 6500)], envios={'sala': 0.3}, ancho=0.01),
        'piedras': dict(tipo='golpe', fn=lambda v, var, **kw: piedra(tam(v), var), pan=-0.4, gan=-14, eq=[('pa', 200), ('pb', 5500)],
                        envios={'camara': 0.3, 'sala': 0.15}),
        'retumbo': dict(tipo='golpe', fn=lambda v, var, dur=5.0, f_sub=32.7, **kw: retumbo(dur, f_sub), gan=-9, eq=[('pa', 25), ('pb', 300)],
                        envios={'sala': 0.15}),
        'terremoto': dict(tipo='golpe', fn=lambda v, var, **kw: terremoto(3, var), gan=-8, eq=[('pa', 25), ('pb', 2500)], envios={'sala': 0.25}),
    }
    return I, sala


# ======================================================================
#  GOLPES DE MUSICA (stingers): acentos cortos que el juego dispara encima
#  de la pista cuando el jefe pega fuerte, con los mismos instrumentos,
#  tonalidad, salas y mezcla que su pista, en el acorde de tonica y el modo
#  de la pista: suenan como parte de la musica y no chocan con el bucle.
#    golpe1, golpe2: golpe pesado (1,2-1,3 s), dos variantes.
#    grande: momento grande (3,2 s): golpe, coro y metales que se hinchan y
#            un acorde oscuro que se apaga.
#    fase:   cambio de fase (3,4 s): subida corta, golpe y la cabeza del
#            leitmotiv en los metales.
# ======================================================================
def _redoble_golpe(p, inst, m, compas, pos, dur, v0, v1, ritmo):
    """Redoble de timbal o de tambor (m=None: golpe sin altura) en unidades."""
    t = 0.0
    k = 0
    while t < dur - 1e-6:
        v = (v0 + (v1 - v0) * t / dur) * (0.85 + 0.15 * (k % 2))
        if m is None:
            p.golpe(inst, compas, pos + t, v)
        else:
            p.nota(inst, m, compas, pos + t, 0.5, v)
        t += ritmo / p.u
        k += 1


def golpes_nerea():
    u = 60.0 / 104 / 3
    o = 0.2

    def base(nombre):
        return Partitura('nerea_' + nombre, 8, 6, u)

    def golpe1():
        p = base('golpe1')
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('bombo', 1, o, 0.8)
        p.golpe('tom_grave', 1, o, 0.7)
        p.nota('timbales', 'D2', 1, o, 2, 1.0)
        p.acorde('trombones', 'D2 A2 D3', 1, o, 1, 1.0, 'stac')
        p.acorde('trompas', 'D3 F3 A3', 1, o, 1, 0.95, 'stac')
        p.nota('tuba', 'D2', 1, o, 1, 0.95, 'stac')
        p.nota('contrabajos', 'D2', 1, o, 1, 0.9, 'stac')
        p.nota('chelos', 'D3', 1, o, 1, 0.9, 'stac')
        p.golpe('olas', 1, o, 0.6, dur=1.2, pan0=0.0, pan1=0.0, cresta=0.04, brillo=1.1)
        for k, nm in enumerate(['A5', 'F5', 'D5', 'A4']):
            p.nota('arpa', nm, 1, o + 1 + 0.5 * k, 1, 0.5 - 0.05 * k)
        return p

    def golpe2():
        p = base('golpe2')
        p.golpe('bombo', 1, o, 1.0)
        p.golpe('taiko', 1, o, 0.8)
        p.nota('timbales', 'D2', 1, o, 1, 1.0)
        p.nota('timbales', 'A1', 1, o + 1, 1, 0.75)
        p.golpe('tom_grave', 1, o + 0.5, 0.6)
        p.golpe('tom_grave', 1, o + 1.0, 0.7)
        p.acorde('trombones', 'D3 F3 A3', 1, o, 1, 1.0, 'stac')
        p.acorde('trompas', 'A3 D4 F4', 1, o, 1, 0.9, 'stac')
        p.acorde('coro_canto', 'D3 A3 D4 F4', 1, o, 1, 0.85, 'stac', vocal=1.0)
        p.nota('contrabajos', 'D2', 1, o, 1, 0.9, 'stac')
        p.nota('gotas', 'D6', 1, o + 1.5, 1, 0.5)
        p.nota('gotas', 'A5', 1, o + 2.5, 1, 0.45)
        p.golpe('olas', 1, o, 0.45, dur=1.0, pan0=-0.3, pan1=0.3, cresta=0.05)
        return p

    def grande():
        p = base('grande')
        p.golpe('olas', 1, o, 1.0, dur=3.2, pan0=0.0, pan1=0.0, cresta=0.04, brillo=1.25)
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('bombo', 1, o, 0.9)
        p.nota('timbales', 'D2', 1, o, 2, 1.0)
        p.acorde('trombones', 'D2 A2 D3', 1, o, 1, 1.0, 'stac')
        p.acorde('coro_canto', 'D3 A3 D4 F4 A4', 1, o, 1, 0.9, 'stac', vocal=1.0)
        p.acorde('trombones', 'D2 A2 D3 F3', 1, o + 0.3, 5, 0.75, 'fpc')
        p.acorde('trompas', 'D3 A3 F4', 1, o + 0.3, 5, 0.7, 'fpc')
        p.acorde('coro_canto', 'D3 A3 D4 F4', 1, o + 0.3, 5, 0.6, 'fpc', vocal=0.6)
        p.acorde('trombones', 'D2 A2 D3 F3', 1, o + 5.3, 10, 0.85, 'dim')
        p.acorde('trompas', 'D3 A3 F4', 1, o + 5.3, 10, 0.8, 'dim')
        p.nota('tuba', 'D2', 1, o + 5.3, 10, 0.8, 'dim')
        p.acorde('coro_canto', 'D3 A3 D4 F4', 1, o + 5.3, 10, 0.7, 'dim', vocal=0.3)
        p.golpe('bombo', 1, o + 5.3, 0.7)
        p.nota('contrabajos', 'D2', 1, o, 15, 0.8, 'dim')
        p.nota('sub', 'D2', 1, o, 15, 0.6, 'dim')
        _redoble_golpe(p, 'timbales', 'A1', 1, o + 2.5, 4, 0.3, 0.7, 0.07)
        for k, nm in enumerate(['D6', 'A5', 'F5', 'D5', 'A4', 'F4', 'D4']):
            p.nota('arpa', nm, 1, o + 0.5 + 0.5 * k, 1, 0.5 - 0.03 * k)
        return p

    def fase():
        p = base('fase')
        h = 4.6
        for nm in ('D4', 'Eb4', 'E4', 'A4', 'Bb4'):
            p.nota('subida', nm, 1, o, h - o, 0.75, 'cresc', gl=12.0)
        p.golpe('olas', 1, o, 0.7, dur=0.85, pan0=-0.4, pan1=0.4, cresta=0.97)
        _redoble_golpe(p, 'timbales', 'A1', 1, o, h - o - 0.3, 0.3, 0.95, 0.07)
        p.golpe('taiko', 1, h, 1.0)
        p.golpe('bombo', 1, h, 0.8)
        p.nota('timbales', 'D2', 1, h, 2, 1.0)
        p.golpe('olas', 1, h, 0.8, dur=2.4, pan0=0.0, pan1=0.0, cresta=0.04, brillo=1.15)
        p.acorde('trombones', 'D2 A2 D3', 1, h, 1, 1.0, 'stac')
        p.melodia('trompas', 'ff ' + NER_CELDA, 1, pos=h, lig=False)
        p.melodia('trombones', 'f ' + NER_CELDA, 1, pos=h, transp=-12, lig=False)
        p.melodia('coro_canto', 'f ' + NER_CELDA, 1, pos=h, art='stac', vocal=1.0)
        p.nota('contrabajos', 'D2', 1, h, 12, 0.8, 'dim')
        p.nota('sub', 'D2', 1, h, 12, 0.55, 'dim')
        for k, nm in enumerate(['D5', 'F5', 'A5', 'D6']):
            p.nota('arpa', nm, 1, h + 6 + 0.5 * k, 1, 0.4)
        return p

    return [('golpe1', golpe1, 1.2), ('golpe2', golpe2, 1.3), ('grande', grande, 3.2), ('fase', fase, 3.4)]


def golpes_aeralis():
    u = 60.0 / 160
    o = 0.1

    def base(nombre):
        return Partitura('aeralis_' + nombre, 8, 4, u)

    def golpe1():
        p = base('golpe1')
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('tom_grave', 1, o, 0.8)
        p.golpe('caja', 1, o, 0.7)
        p.nota('timbales', 'E2', 1, o, 2, 1.0)
        p.acorde('trombones', 'E2 B2 E3', 1, o, 0.5, 1.0, 'stac')
        p.acorde('trompas', 'E3 G3 B3', 1, o, 0.5, 0.95, 'stac')
        p.nota('tuba', 'E2', 1, o, 0.5, 0.95, 'stac')
        p.nota('contrabajos', 'E2', 1, o, 0.5, 0.9, 'stac')
        for k, nm in enumerate(['E4', 'F4', 'G4', 'B4', 'E5']):
            p.nota('spic', nm, 1, o + 0.5 + 0.25 * k, 0.25, 0.75)
        p.golpe('rafaga', 1, o, 0.6, dur=1.1, f0=400.0, f1=2200.0, pan0=-0.7, pan1=0.7)
        return p

    def golpe2():
        p = base('golpe2')
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('tom_medio', 1, o, 0.75)
        p.golpe('tom_grave', 1, o + 0.12, 0.8)
        p.golpe('caja', 1, o, 0.6)
        p.golpe('caja', 1, o + 0.06, 0.75)
        p.nota('timbales', 'E2', 1, o, 1, 1.0)
        p.nota('timbales', 'B1', 1, o + 0.5, 1, 0.7)
        p.acorde('trombones', 'E3 G3 B3', 1, o, 0.5, 1.0, 'stac')
        p.acorde('coro_canto', 'E3 B3 E4 G4', 1, o, 0.5, 0.85, 'stac', vocal=1.0)
        p.nota('contrabajos', 'E2', 1, o, 0.5, 0.9, 'stac')
        p.melodia('flauta', 'f F5:0.5 E5:1.5', 1, pos=o + 0.25, comprobar=False)
        p.golpe('rafaga', 1, o, 0.55, dur=1.1, f0=400.0, f1=2200.0, pan0=0.7, pan1=-0.7)
        return p

    def grande():
        p = base('grande')
        p.golpe('trueno', 1, o, 1.0, pan=0.0)
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('platillos', 1, o, 0.8)
        p.nota('timbales', 'E2', 1, o, 2, 1.0)
        p.acorde('trombones', 'E2 B2 E3', 1, o, 0.5, 1.0, 'stac')
        p.acorde('coro_canto', 'E3 B3 E4 G4 B4', 1, o, 0.5, 0.9, 'stac', vocal=1.0)
        p.acorde('trombones', 'E2 B2 E3 G3', 1, o + 0.2, 2.5, 0.75, 'fpc')
        p.acorde('trompas', 'E3 B3 G4', 1, o + 0.2, 2.5, 0.7, 'fpc')
        p.acorde('coro_canto', 'E3 B3 E4 G4', 1, o + 0.2, 2.5, 0.6, 'fpc', vocal=0.6)
        p.acorde('trombones', 'E2 B2 E3 G3', 1, o + 2.7, 5.5, 0.85, 'dim')
        p.acorde('trompas', 'E3 B3 G4', 1, o + 2.7, 5.5, 0.8, 'dim')
        p.nota('tuba', 'E2', 1, o + 2.7, 5.5, 0.8, 'dim')
        p.acorde('coro_canto', 'E3 B3 E4 G4', 1, o + 2.7, 5.5, 0.7, 'dim', vocal=0.3)
        p.golpe('taiko', 1, o + 2.7, 0.7)
        p.nota('contrabajos', 'E2', 1, o, 8, 0.8, 'dim')
        for nm in ('E4', 'G4', 'B4'):
            p.nota('spic', nm, 1, o + 0.25, 6, 0.4, 'trem')
        p.golpe('rafaga', 1, o + 1, 0.6, dur=2.0, f0=350.0, f1=2000.0, pan0=-0.8, pan1=0.8)
        return p

    def fase():
        p = base('fase')
        h = 2.2
        for nm in ('D#5', 'E5', 'F5', 'B4', 'C5'):
            p.nota('subida', nm, 1, o, h - o, 0.75, 'cresc', gl=12.0)
        p.golpe('rafaga', 1, o, 0.75, dur=0.85, f0=300.0, f1=2600.0, pan0=-0.6, pan1=0.6)
        _redoble_golpe(p, 'caja', None, 1, o, h - o - 0.1, 0.3, 1.0, 0.047)
        _redoble_golpe(p, 'timbales', 'B1', 1, o, h - o - 0.1, 0.3, 0.9, 0.07)
        p.golpe('trueno', 1, h, 0.9, pan=0.0)
        p.golpe('taiko', 1, h, 1.0)
        p.nota('timbales', 'E2', 1, h, 2, 1.0)
        p.acorde('trombones', 'E2 B2 E3', 1, h, 0.5, 1.0, 'stac')
        cabeza = AER_CELDA.split(' | ')[0]
        p.melodia('flauta', 'ff ' + cabeza, 1, pos=h, comprobar=False)
        p.melodia('violines', 'f ' + cabeza, 1, pos=h, comprobar=False)
        p.melodia('trompas', 'ff ' + cabeza, 1, pos=h, transp=-12, lig=False, comprobar=False)
        p.melodia('trombones', 'f ' + cabeza, 1, pos=h, transp=-24, lig=False, comprobar=False)
        p.nota('contrabajos', 'E2', 1, h, 4, 0.8, 'dim')
        return p

    return [('golpe1', golpe1, 1.2), ('golpe2', golpe2, 1.3), ('grande', grande, 3.2), ('fase', fase, 3.2)]


def golpes_rajang():
    u = 60.0 / 136
    o = 0.1

    def base(nombre):
        return Partitura('rajang_' + nombre, 8, 4, u)

    def golpe1():
        p = base('golpe1')
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('timbal_grave', 1, o, 0.85)
        p.nota('tronco', 'C3', 1, o, 0.5, 1.0)
        p.nota('tronco', 'G2', 1, o + 0.5, 0.5, 0.7)
        p.golpe('piedras', 1, o + 0.25, 0.6)
        p.acorde('trombones', 'C2 G2 C3', 1, o, 0.5, 1.0, 'stac')
        p.acorde('trompas', 'C3 Eb3 G3', 1, o, 0.5, 0.9, 'stac')
        p.nota('tuba', 'C2', 1, o, 0.5, 0.95, 'stac')
        p.nota('contrabajos', 'C2', 1, o, 0.5, 0.9, 'stac')
        p.golpe('semillas', 1, o, 0.45, dur=0.5, subida_=False, pan=0.4)
        return p

    def golpe2():
        p = base('golpe2')
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('taiko', 1, o + 0.12, 0.7)
        p.golpe('marco', 1, o, 0.8)
        for k, nm in enumerate(['C3', 'Db3', 'C3']):
            p.nota('tronco', nm, 1, o + 0.25 * k, 0.25, 0.9 - 0.1 * k)
        p.acorde('canto', 'C3 G3 C4 Eb4', 1, o, 0.5, 0.85, 'stac', vocal=0.2)
        p.acorde('trompas', 'C3 Eb3 G3', 1, o, 0.5, 0.95, 'stac')
        p.acorde('trombones', 'C2 G2', 1, o, 0.5, 0.95, 'stac')
        p.golpe('piedras', 1, o + 0.5, 0.6)
        p.golpe('semillas', 1, o + 0.25, 0.5, dur=0.6, subida_=False, pan=-0.4)
        return p

    def grande():
        p = base('grande')
        p.golpe('terremoto', 1, o, 1.0)
        p.golpe('taiko', 1, o, 1.0)
        p.golpe('retumbo', 1, o, 0.6, dur=3.0, f_sub=32.7)
        p.acorde('trombones', 'C2 G2 C3', 1, o, 0.5, 1.0, 'stac')
        p.acorde('canto', 'C3 G3 C4 Eb4', 1, o, 0.5, 0.9, 'stac', vocal=1.0)
        p.acorde('trombones', 'C2 G2 C3 Eb3', 1, o + 0.2, 2.2, 0.75, 'fpc')
        p.acorde('trompas', 'C3 G3 Eb4', 1, o + 0.2, 2.2, 0.7, 'fpc')
        p.acorde('canto', 'C3 G3 C4 Eb4', 1, o + 0.2, 2.2, 0.6, 'fpc', vocal=0.6)
        p.acorde('trombones', 'C2 G2 C3 Eb3', 1, o + 2.4, 4.6, 0.85, 'dim')
        p.acorde('trompas', 'C3 G3 Eb4', 1, o + 2.4, 4.6, 0.8, 'dim')
        p.nota('tuba', 'C2', 1, o + 2.4, 4.6, 0.8, 'dim')
        p.acorde('canto', 'C3 G3 C4 Eb4', 1, o + 2.4, 4.6, 0.7, 'dim', vocal=0.3)
        p.golpe('taiko', 1, o + 2.4, 0.7)
        p.nota('dron', 'C2', 1, o, 7, 0.6, 'dim')
        for k, nm in enumerate(['C5', 'Eb5', 'G5', 'C6']):
            p.nota('kalimba', nm, 1, o + 0.5 + 0.25 * k, 0.25, 0.45)
        p.golpe('semillas', 1, o + 1, 0.5, dur=1.5, subida_=False, pan=0.3)
        return p

    def fase():
        p = base('fase')
        h = 1.85
        for nm in ('G3', 'Ab3', 'B3', 'D4'):
            p.nota('subida', nm, 1, o, h - o, 0.75, 'cresc', gl=12.0)
        p.golpe('semillas', 1, o, 0.8, dur=0.8, pan=0.3)
        p.golpe('retumbo', 1, o, 0.6, dur=1.0, f_sub=49.0)
        _redoble_golpe(p, 'taiko', None, 1, o + 0.75, h - o - 0.8, 0.4, 0.95, 0.07)
        p.golpe('taiko', 1, h, 1.0)
        p.golpe('terremoto', 1, h, 0.8)
        p.acorde('trombones', 'C2 G2 C3', 1, h, 0.5, 1.0, 'stac')
        cabeza = 'C4:1 Eb4:1 G4:1 Db4:0.5 C4:1.5'
        p.melodia('trompas', 'ff ' + cabeza, 1, pos=h, lig=False, comprobar=False)
        p.melodia('trombones', 'f ' + cabeza, 1, pos=h, transp=-12, lig=False, comprobar=False)
        p.melodia('ocarina', 'f ' + cabeza, 1, pos=h, transp=12, comprobar=False)
        p.melodia('canto', 'f ' + cabeza, 1, pos=h, art='stac', vocal=1.0, comprobar=False)
        p.nota('dron', 'C2', 1, h, 5, 0.6, 'dim')
        p.nota('contrabajos', 'C2', 1, h, 5, 0.75, 'dim')
        return p

    return [('golpe1', golpe1, 1.2), ('golpe2', golpe2, 1.3), ('grande', grande, 3.2), ('fase', fase, 3.4)]


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


def producir_golpe(p, inst, salas, dur, objetivo=-13.0, techo_db=-1.0):
    """Un acento suelto (no es bucle): mismos instrumentos, salas y mezcla que
    la pista; la cola se apaga sola al final; sonoridad de las partes fuertes
    de la pista y pico en -1 dBFS."""
    n = n_(dur)
    p.L = n
    mz = Mezcla(n, salas)
    tocar_buses(p, inst, mz, n)
    x = pa(mz.cerrar().astype(np.float64), 28, 2)
    g = signal.sosfiltfilt(signal.butter(2, 120.0, 'low', fs=SR, output='sos'), x, axis=-1)
    x = x - g + (0.5 * (g[0] + g[1]))[None, :]
    f = n_(dur * 0.35)
    x[:, -f:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f)))[None, :]
    x *= 10 ** ((objetivo - lufs(x)) / 20)
    y, _ = limitador(np.tanh(x * 1.1) / 1.1, techo_db)
    pk = np.max(np.abs(y))
    if pk < 10 ** ((techo_db - 1.0) / 20):
        y *= min(10 ** (techo_db / 20) / pk, 10 ** ((-12.0 - lufs(y)) / 20))
    return y


def guardar_golpes(jefe, golpes, instrumentos, salida, revision=None):
    global rng
    for nombre, construir, dur in golpes:
        rng = np.random.default_rng(_semilla((jefe, nombre)))
        p = construir()
        inst, salas = instrumentos()
        y = producir_golpe(p, inst, salas, dur)
        ruta = os.path.join(salida, '%s_%s.ogg' % (jefe, nombre))
        escribir_ogg(ruta, np.ascontiguousarray(y.T.astype(np.float32)), 0.5)
        z, _ = sf.read(ruta, dtype='float32', always_2d=True)
        z = z.T.astype(np.float64)
        pk = 20 * np.log10(np.max(np.abs(z)) + 1e-12)
        if pk > -1.0:
            escribir_ogg(ruta, np.ascontiguousarray((y * 10 ** ((-1.05 - pk) / 20)).T.astype(np.float32)), 0.5)
            z, _ = sf.read(ruta, dtype='float32', always_2d=True)
            z = z.T.astype(np.float64)
        print('  %-16s %4.2f s  pico %.2f dBFS  %.1f LUFS  %.0f KB' % (
            '%s_%s' % (jefe, nombre), z.shape[1] / SR, 20 * np.log10(np.max(np.abs(z)) + 1e-12), lufs(z), os.path.getsize(ruta) / 1e3), flush=True)
        if revision:
            imagen_revision(z, os.path.join(revision, '%s_%s.png' % (jefe, nombre)), '%s_%s' % (jefe, nombre), ancho=800, alto=260)


PISTAS = {}


def registrar(nombre, compositor, instrumentos, objetivo=-16.0, golpes=None):
    PISTAS[nombre] = (compositor, instrumentos, objetivo, golpes)


registrar('nerea', nerea, instrumentos_nerea, -17.0, golpes_nerea)
registrar('aeralis', aeralis, instrumentos_aeralis, -17.0, golpes_aeralis)
registrar('rajang', rajang, instrumentos_rajang, -17.0, golpes_rajang)


if __name__ == '__main__':
    RAIZ = sys.argv[1]
    REVISION = sys.argv[2] if len(sys.argv) > 2 else None
    SOLO = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/musica')
    os.makedirs(SALIDA, exist_ok=True)
    inicio = time.time()
    for nombre, (compositor, instrumentos, objetivo, golpes) in PISTAS.items():
        if SOLO and nombre not in SOLO:
            continue
        print(nombre, flush=True)
        _TABLAS.clear()
        _CACHE.clear()
        p = compositor()
        inst, salas = instrumentos()
        y, niveles, gmin = producir(p, inst, salas, objetivo=objetivo)
        guardar_pista(nombre, y, p, niveles, gmin, SALIDA, REVISION)
        if golpes:
            guardar_golpes(nombre, golpes(), instrumentos, SALIDA, REVISION)
    print('listo en %.0f s' % (time.time() - inicio))
