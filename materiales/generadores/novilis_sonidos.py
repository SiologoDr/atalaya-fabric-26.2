"""
Sonidos de Novilis, el Caballero Solar. Sintetizados desde cero: nada de
vanilla ni de bancos de sonido.

Novilis es un caballero de dieciseis bloques con armadura de acero quemado,
grietas de lava, filo de oro, corona de puas, cuernos, un halo de fuego
detras de la cabeza, capa roja y un flamberge enorme con un canal de lava en
la hoja. Trae su propio sol, pequeno, que flota encima de el. Pelea en el
Altar del Sol. Todo sale del FUEGO, la LAVA, el ACERO y el SOL, modelados
con su fisica:

  - FUEGO QUE RUGE: la combustion turbulenta es ruido grave cuya amplitud
    late con los remolinos; las lenguas que lamen son una banda media que se
    abre y se cierra; y las brasas saltan: cada chasquido es una bolsa de gas
    o de savia que revienta (un impulso de 0,2-2,5 ms que hace sonar un
    instante la astilla o la escoria), con amplitudes de cola larga (muchos
    flojos y unos pocos fuertes).
  - FUEGO QUE PRENDE ('fwump'): el aire que se traga la llama, la bocanada
    que se abre en agudos y se cierra, el golpe de presion.
  - LAVA: roca fundida y viscosa. Cada burbuja de gas sube, se estrecha y
    revienta: un 'blop' grave y muy amortiguado que sube de tono, el
    chasquido de la piel que se rompe y un soplo de gas caliente. Debajo, un
    gorgoteo hondo; encima, el vapor que sisea donde toca algo frio.
  - ACERO: las placas de la armadura son placas gruesas (modos inarmonicos
    de una placa, cada uno partido en dos porque la forja no es simetrica:
    el batido). Las placas que rozan bajo el peso chirrian (friccion de
    pegarse y soltarse, casi periodica, por resonancias estrechas) y las
    sueltas traquetean (muchos golpecitos metalicos).
  - EL SOL: una nota honda con muchos armonicos que se abren con el brillo,
    dos voces casi iguales que laten entre si, la quinta que entra y sale, un
    pulso de plasma y el rugido del fuego por debajo. Los TONOS que suben son
    senos con pocos armonicos y un coro de voces desafinadas.
  - EXPLOSIONES de fuego: el golpe de presion, el chasquido, la bola de
    fuego (ruido que se cierra de agudos a graves), el fuego que sigue, las
    brasas, la lava que llueve y el retumbo que rueda.
  - PIEDRA del altar y de las estatuas de marmol: la misma fisica que
    Rajang (roca que se raja, grava, cantos, piedra que se arrastra).

La VOZ es la de un caballero: una garganta humana grave (60 a 150 Hz) con
los formantes de un tracto enorme, una segunda voz una octava abajo que le
da el pecho, rugosidad a rachas en lo mas alto y, sobre todo, el YELMO: la
voz sale por las rendijas de una cabeza de acero (un tubo corto que resuena
como un peine, el casco que vibra con ella y las rendijas que se comen los
agudos).

Las TROMPETAS de las estatuas son metales sintetizados: diente de sierra
(armonicos 1/k, limitados en banda) por el formante de la campana, con el
brillo que sube con la intensidad (como un metal de verdad), el ataque de
lengua con el tono que entra un poco bajo, vibrato que llega tarde y el
aliento. Cuatro voces del mismo coral (melodia, contracanto, armonia y
trompeta baja), en ficheros sueltos de la misma duracion exacta.

El espacio es el Altar del Sol: un patio de marmol en lo alto, rodeado de
columnas y abierto al cielo. Ecos claros y seguidos entre las columnas y
una cola abierta que se oscurece pronto.

Escribe los .ogg (mono, para que se oigan en 3D) en
assets/atalaya/sounds/novilis/ y sus eventos en sounds.json
(novilis.<evento>, subtitulo subtitles.atalaya.novilis.<evento>); las
melodias van con "stream": true. Los textos de los subtitulos estan en
SUBTITULOS (abajo) y se copian a mano a lang/.

Uso: python novilis_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png]
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator
import os, sys, json, collections

SR = 44100
RAIZ = sys.argv[1]
OUT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/novilis')
os.makedirs(OUT, exist_ok=True)
for viejo in os.listdir(OUT):
    if viejo.endswith('.ogg'):
        os.remove(os.path.join(OUT, viejo))
rng = np.random.default_rng(20261020)
EVENTOS = collections.OrderedDict()
GUARDADOS = []
STREAM = set()


# ======================================================================
#  Utilidades (las mismas que los sonidos de Nerea, Aeralis y Rajang)
# ======================================================================
def n_(dur):
    return max(1, int(round(dur * SR)))


def t_(dur):
    return np.arange(n_(dur)) / SR


def hz(m):
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


_LETRAS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(txt):
    """'C#4' -> 61, 'Bb3' -> 58 (do central = C4 = 60)."""
    i, alt = 1, 0
    while txt[i] in '#b':
        alt += 1 if txt[i] == '#' else -1
        i += 1
    return 12 * (int(txt[i:]) + 1) + _LETRAS[txt[0]] + alt


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


def paso(x):
    """Rampa suave 0..1 (smoothstep)."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def saturar(x, k=2.0):
    return np.tanh(k * x) / np.tanh(k)


def limitar(x, umbral=0.55):
    """Compresion suave de los picos: mas cuerpo sin que nada recorte."""
    y = pico(x)
    m = np.abs(y)
    sobre = m > umbral
    y[sobre] = np.sign(y[sobre]) * (umbral + (1 - umbral) * np.tanh((m[sobre] - umbral) / (1 - umbral)))
    return y


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


def _campana_db(f, fc, db, ancho):
    """Ganancia (lineal) de una joroba en dB centrada en fc, ancho en octavas."""
    return 10 ** (db / 20 * np.exp(-0.5 * (np.log2(np.maximum(f, 1.0) / fc) / ancho) ** 2))


# ---------------------------------------------------------------- reverb
_IRS = {}


def respuesta(cola, oscuro):
    """El Altar del Sol: un patio de marmol en lo alto, rodeado de columnas y
    abierto al cielo. El suelo pulido y las columnas devuelven ecos claros y
    seguidos (un aleteo entre las dos filas), y como no hay techo la cola es
    abierta y se oscurece pronto."""
    clave = (round(cola, 2), int(oscuro))
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro) + 11)
        x = r.standard_normal(len(t))
        h = (pb(x, 500) * np.exp(-6.9 * t / cola)
             + bp(x, 500, 3000) * np.exp(-6.9 * t / (cola * 0.6)) * 0.8
             + pa(x, 3000) * np.exp(-6.9 * t / (cola * 0.2)) * 0.35)
        h = pb(h, oscuro)
        a = n_(0.025)
        h[:a] *= np.linspace(0, 1, a) ** 2
        ref = np.sqrt(np.mean(h[:n_(0.12)] ** 2))
        # el suelo de marmol y el aleteo entre las columnas (cada vez mas flojo)
        ecos = [(0.011, 0.8, 8000)] + [(0.031 + 0.026 * k, 0.62 * 0.8 ** k, 6500 - 450 * k) for k in range(7)]
        for seg, g, claro in ecos:
            if seg < cola * 0.8:
                i = n_(seg)
                eco = pb(r.standard_normal(n_(0.012)), claro) * np.exp(-t_(0.012) / 0.003)
                h[i:i + len(eco)] += g * eco * ref * 7
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


def reverb(x, mezcla=0.25, cola=1.8, oscuro=6500):
    h = respuesta(cola, oscuro)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


# ======================================================================
#  PIEDRA (la del altar y las estatuas; la misma fisica que Rajang)
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
    que se apagan enseguida. f ~ 1/tamano. El marmol es mas duro y mas
    brillante que la roca de la selva."""
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
    """Lluvia de piedras (tasa por segundo, numero o curva)."""
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
    `vuelo` segundos y se apaga."""
    t = t_(dur)
    x = t / vuelo
    tasa = 700 * fuerza * (salpica * np.exp(-t / 0.04) + x ** 1.5 * np.exp(1.5 * (1 - x)))
    return grava(dur, tasa, tam)


ROCA = ((92, 5.0, 1.0), (163, 6.0, 0.9), (281, 7.0, 0.75), (455, 8.0, 0.55), (742, 8.0, 0.4), (1210, 9.0, 0.28),
        (1960, 10.0, 0.18))


def moler(dur, peso=1.0, tasa=(16, 45), arena=1.0, velocidad=1.0):
    """Piedra que se arrastra sobre piedra: friccion de pegarse y soltarse
    por los modos anchos de los bloques, con la arena que raspa."""
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
    """Una roca que se parte: una racha de microfracturas que hacen sonar las
    bandas agudas de la piedra y el golpe grave de su masa."""
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


def canto(tam=15.0, fuerza=1.0, chinas=True, duro=1.0):
    """Un canto de piedra (o un trozo de marmol) que golpea: un 'toc'."""
    f = 4500.0 * duro / tam * rng.uniform(0.85, 1.15)
    tau = 0.0016 + 0.0013 * tam
    d = min(0.6, 7 * tau + 0.03)
    parc = ((1, 1.0), (rng.uniform(1.4, 1.8), 0.7), (rng.uniform(2.1, 2.7), 0.45), (rng.uniform(3.2, 4.0), 0.25))
    capas = [pico(modos(f, d, parc, tau), 1.0),
             pico(pb(ruido(0.025), 1200 * duro) * caida(0.025, 0.004, 0.0005), 0.6),
             pico(boom(f * 0.55, f * 0.4, 0.03 + 0.002 * tam), 0.5)]
    if chinas:
        capas.append(pico(grava(0.3, 400 * np.exp(-t_(0.3) / 0.05), (0.4, 2.0)), 0.2))
    return fuerza * mezclar(*capas)


def rodar(dur, tam=15.0, botes=7, amp=1.0, intervalo=0.22):
    """Un trozo que cae y rueda: botes cada vez mas seguidos y mas flojos."""
    out = np.zeros(n_(dur) + n_(0.7))
    s, a, iv = 0.0, 1.0, intervalo
    for _ in range(botes):
        if s >= dur:
            break
        c = canto(tam * rng.uniform(0.8, 1.2), a, duro=1.15)
        i = n_(s)
        out[i:i + len(c)] += c[:len(out) - i]
        s += iv * rng.uniform(0.85, 1.15)
        iv *= rng.uniform(0.62, 0.8)
        a *= rng.uniform(0.6, 0.8)
    return amp * np.trim_zeros(out, 'b')


def golpe_tierra(peso=1.0, grieta=1.0, restos=1.0, dur=2.5):
    """Algo enorme contra las losas del altar: el golpe de presion, el
    cuerpo sordo, la piedra que se raja, el suelo que retumba y lo que cae."""
    t = t_(dur)
    sub = saturar(boom(78, 30, 0.26 * peso, dur), 2.5)
    cuerpo = bp(ruido(0.5, 'rosa'), 90, 700) * caida(0.5, 0.05 * peso, 0.002)
    aplasta = bp(ruido(0.3, 'rosa'), 300, 2800) * caida(0.3, 0.035, 0.001)
    choque = bp(ruido(0.08), 150, 7000) * caida(0.08, 0.008, 0.0005)
    raja = rajar_roca(int(5 + 9 * grieta), 0.03 + 0.07 * grieta, 1.0, 0.8)
    temblor = retumbo(dur, 110, 2.5, 0.35, 0.6) * caida(dur, 0.35 * peso, 0.01)
    caen = escombros(dur, restos, 0.3 + 0.12 * peso, (0.4, 4 + 6 * restos))
    polvo = pb(ruido(dur, 'rosa'), 800) * np.interp(t, [0, 0.04, 0.5, dur], [0, 1, 0.35, 0])
    return mezclar(pico(sub, 0.5), pico(cuerpo, 0.6), pico(aplasta, 0.9), pico(choque, 0.7), pico(raja, 0.75 * grieta),
                   pico(temblor, 0.25), pico(caen, 0.7 * restos), pico(polvo, 0.25))


def pasada(dur, f0, f1, q=1.8, silba=0.25):
    """Algo grande que corta el aire: la banda se mueve (Doppler) y silba."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.45, (f0 * f1) ** 0.5 * 1.15), (1, f1)])
    soplo = filtro_mov(ruido(dur, 'rosa'), f, 'band', q)
    canta = filtro_mov(ruido(dur), f * 1.6, 'band', 22, 32)
    e = campana_env(dur, 1.3) ** 1.4
    return mezclar(pico(soplo * e, 1.0), pico(canta * e, silba))


def crepitar(dur, tasa, fc, q=1.2):
    """Chasquidos que se suceden por una banda que se mueve (algo que se
    rasga o que se carga)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    exc = np.zeros(n)
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    exc[cuando] = rng.uniform(0.2, 1.0, len(cuando)) * rng.choice([-1.0, 1.0], len(cuando))
    nucleo = pa(ruido(0.002), 400) * caida(0.002, 0.0005, 0.0001)
    exc = signal.fftconvolve(exc, nucleo)[:n]
    return filtro_mov(exc, fc, 'band', q, 32)


# ======================================================================
#  FUEGO Y LAVA
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


def chasquidos(dur, tasa, brillo=1.0):
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
    out = out[:n]
    if brillo < 1.0:
        out = pb(out, 9000 * brillo)
    return out


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
    capas = [pico(sopla, 1.0), pico(golpe, 0.55), pico(chispas, 0.3)]
    x = mezclar(*capas)
    if aspira:
        na = n_(aspira)
        traga = filtro_mov(ruido(aspira, 'rosa'), curva(na, [(0, 300), (1, 1800)]), 'low', 0.8) * rampa(aspira, 2.2)
        x = mezclar(pico(traga, 0.4), en(aspira, x))
    return fuerza * x


def siseo(dur, lo=2500, hi=9000, aleteo=1.0):
    """Vapor que sisea (la lava que toca algo frio, el metal que se enfria)."""
    n = n_(dur)
    return bp(ruido(dur), lo, hi) * np.clip(0.6 + 0.4 * aleteo * np.tanh(suave(n, 3.0)), 0.05, None)


def burbuja_lava(f=110.0, dur=None, fuerza=1.0):
    """Una burbuja de gas en la roca fundida: un 'blop' grave y muy
    amortiguado que sube de tono al estrecharse el cuello, el chasquido de la
    piel que se rompe y un soplo de gas caliente."""
    dur = dur or rng.uniform(0.12, 0.3)
    t = t_(dur)
    sube = f * (1 + 1.2 * (t / dur) ** 2)
    fase = 2 * np.pi * np.cumsum(sube) / SR
    blop = (np.sin(fase) + 0.3 * np.sin(2 * fase + 0.5)) * np.exp(-t / (dur * 0.35)) * (1 - np.exp(-t / 0.006))
    golpe = pb(ruido(dur), 400) * np.exp(-t / 0.02)
    s = dur * rng.uniform(0.15, 0.35)
    revienta = en(s, pa(ruido(0.006), 1200) * caida(0.006, 0.0012, 0.0002))
    gas = en(dur * 0.25, bp(ruido(dur * 0.8), 1800, 7000) * caida(dur * 0.8, dur * 0.15, 0.005))
    return fuerza * mezclar(pico(blop, 1.0), pico(golpe, 0.25), pico(revienta, 0.35), pico(gas, 0.12))


def lava_charco(dur, tasa=7.0, siseo_=1.0, grave=1.0):
    """Un charco de lava: burbujas de muchos tamanos, el gorgoteo hondo de la
    roca fundida, el vapor que sisea y la costra que cruje."""
    n = n_(dur)
    t = t_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    burb = np.zeros(n + n_(0.4))
    for i in cuando:
        b = burbuja_lava(np.exp(rng.uniform(np.log(55), np.log(230))) * grave, None, rng.uniform(0.3, 1.0))
        burb[i:i + len(b)] += b
    gorgoteo = pa(pb(ruido(dur, 'marron'), 160 * grave), 30) * np.exp(0.6 * suave(n, 2.5))
    sisea = siseo(dur) * (0.5 + 0.5 * np.clip(suave(n, 0.7), -1, 1))
    crujen = chasquidos(dur, 12)
    return mezclar(pico(burb[:n], 1.0), pico(gorgoteo, 0.4), pico(sisea, 0.16 * siseo_), pico(crujen, 0.18))


def salpicadura(fuerza=1.0):
    """Un goterón de lava que cae: el golpe blando, el chisporroteo y el vapor."""
    d = 0.9
    t = t_(d)
    golpe = mezclar(pico(boom(130, 60, 0.04), 1.0), pico(pb(ruido(0.1, 'rosa'), 900) * caida(0.1, 0.015), 0.7))
    chisp = chasquidos(d, 700 * np.exp(-t / 0.12))
    vapor = siseo(0.7) * caida(0.7, 0.18, 0.01)
    return fuerza * mezclar(pico(golpe, 1.0), pico(chisp, 0.45), en(0.01, pico(vapor, 0.3)),
                            pico(burbuja_lava(rng.uniform(80, 150), 0.18), 0.4))


def explosion(fuerza=1.0, dur=3.2, lava=0.0, cola=1.0, grave=1.0, piedra=0.6):
    """Explosion de fuego: el golpe de presion, el chasquido, la bola de fuego
    (ruido que se cierra de agudos a graves), el fuego que sigue ardiendo, las
    brasas, la lava que llueve, lo que salta del suelo y el retumbo."""
    n = n_(dur)
    t = t_(dur)
    golpe = saturar(boom(72 * grave, 22 * grave, 0.3 * fuerza, dur), 2.6)
    estallido = mezclar(pico(pa(ruido(0.06), 300) * caida(0.06, 0.007, 0.0003), 1.0),
                        pico(crepitar(0.12, 3000 * np.exp(-t_(0.12) / 0.03), 2500, 0.8), 0.6))
    fc = curva(n, [(0, 7000), (0.03, 4500), (0.2, 1100), (0.6, 400), (1, 200)])
    bola = filtro_mov(ruido(dur, 'rosa'), fc, 'low', 0.8) * np.interp(t, [0, 0.008, 0.25, dur], [0, 1, 0.55, 0]) ** 1.3
    arde = llama(dur, 1.0, curva(n, [(0, 1.6), (0.3, 1.0), (1, 0.6)])) * np.exp(-t / (0.9 * cola)) * paso(t / 0.1)
    brasas = chasquidos(dur, 1200 * np.exp(-t / 0.25) + 30 * np.exp(-t / 1.5))
    rueda = retumbo(dur, 130, 1.8, 0.5, 0.5) * np.interp(t, [0, 0.15, 0.6, dur], [0, 1, 0.6, 0]) * cola
    capas = [pico(golpe, 0.75), pico(estallido, 0.6), pico(bola, 0.9), pico(arde, 0.4), pico(brasas, 0.35), pico(rueda, 0.35)]
    if piedra:
        capas.append(pico(escombros(dur, 0.8 * piedra, 0.4, (0.4, 6.0)), 0.3 * piedra))
    if lava:
        gotas = mezclar(*[en(s, salpicadura(rng.uniform(0.4, 1.0))) for s in np.sort(rng.uniform(0.25, 1.6, int(6 * lava) + 2))])
        capas.append(pico(gotas, 0.4 * min(1.0, lava)))
        capas.append(pico(siseo(dur) * np.interp(t, [0, 0.3, 1.2, dur], [0, 1, 0.5, 0]), 0.12 * lava))
    return mezclar(*capas)


# ======================================================================
#  ACERO: placas, guanteletes, la hoja
# ======================================================================
PLACA = ((1.0, 1.0), (1.47, 0.75), (2.09, 0.6), (2.56, 0.5), (2.94, 0.42), (3.42, 0.35), (4.11, 0.25), (4.68, 0.18),
         (5.36, 0.13), (6.2, 0.09))
BARRA = ((1, 1.0), (2.756, 0.55), (5.404, 0.32), (8.933, 0.18), (13.34, 0.08))     # la hoja: una barra libre
CAMPANA = ((0.5, 0.55), (1, 1.0), (1.19, 0.5), (1.5, 0.35), (2.0, 0.6), (2.5, 0.25), (3.0, 0.2), (4.2, 0.12))
CASCO = ((0.53, 0.6), (1.0, 1.0), (1.47, 0.6), (2.09, 0.45), (2.56, 0.3), (3.3, 0.2))


def metal(f, dur=None, tau=0.3, parciales=PLACA, dureza=1.0, batido=0.0025, agudos=0.7):
    """Acero golpeado: modos inarmonicos, cada uno partido en dos (la forja
    no es simetrica: el batido le da vida), los agudos que se apagan antes y
    el toque seco del contacto."""
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


_TICS = []


def _tics():
    """Banco de golpecitos de acero (placas sueltas, hebillas, escamas)."""
    if not _TICS:
        for _ in range(40):
            f = np.exp(rng.uniform(np.log(700), np.log(3400)))
            x = metal(f, None, rng.uniform(0.015, 0.06), PLACA[:6], 0.8, 0.004)
            _TICS.append(x / np.max(np.abs(x)))
    return _TICS


def placas(dur, tasa, amp=1.0):
    """La armadura que traquetea: muchos golpecitos de acero (tasa: numero o
    curva por segundo)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    banco = _tics()
    out = np.zeros(n + n_(0.4))
    for i in cuando:
        c = banco[rng.integers(len(banco))] * rng.uniform(0.15, 1.0)
        out[i:i + len(c)] += c
    return amp * out[:n]


def clang(f=300.0, tau=0.4, fuerza=1.0, sordo=1.0):
    """Un golpe en la armadura: la placa que suena, un modo agudo de la
    pieza, el golpe sordo del cuerpo debajo y las placas vecinas que
    traquetean."""
    placa = metal(f, None, tau, PLACA, 1.0)
    alto = metal(f * rng.uniform(2.6, 3.1), None, tau * 0.35, PLACA[:5], 1.0)
    golpe = mezclar(pico(boom(f * 0.5, f * 0.3, 0.05), 1.0), pico(pb(ruido(0.08, 'rosa'), 1500) * caida(0.08, 0.012), 0.7))
    vecinas = placas(0.3, 160 * np.exp(-t_(0.3) / 0.06))
    return fuerza * mezclar(pico(placa, 1.0), pico(alto, 0.35), pico(golpe, 0.6 * sordo), en(0.012, pico(vecinas, 0.25)))


def chirriar(dur, f=380.0, tasa=(35, 110), q=35.0, velocidad=1.0, peso=1.0):
    """Placas de acero que rozan bajo un peso enorme: friccion de pegarse y
    soltarse. Las sueltas salen casi periodicas (el 'iiirrr' de una bisagra)
    y cada una hace sonar los modos de la placa."""
    n = n_(dur)
    vel = np.broadcast_to(np.asarray(velocidad, dtype=float), (n,))
    lo, hi = tasa
    ritmo = (lo + (hi - lo) * (0.5 + 0.5 * np.tanh(1.5 * suave(n, 2.5)))) * np.clip(vel, 0, None)
    fase = np.cumsum(ritmo) / SR
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    exc = np.zeros(n)
    exc[golpes] = rng.uniform(0.4, 1.0, len(golpes))
    exc = signal.fftconvolve(exc, pa(ruido(0.003), 800) * caida(0.003, 0.0006, 0.0001))[:n]
    canta = sum(g * resonar(exc, min(f * r / peso, 12000.0), q) for r, g in ((1, 1.0), (1.47, 0.7), (2.09, 0.5), (2.94, 0.3), (4.11, 0.18)))
    roce = bp(ruido(dur, 'rosa'), 1500, 6000) * np.clip(vel, 0, None)
    return mezclar(pico(canta, 1.0), pico(roce, 0.12))


# ======================================================================
#  EL SOL: zumbido, tonos que suben, campanas y destellos
# ======================================================================
def zumbido_solar(dur, f=55.0, brillo=0.5, latido=1.2, plasma=1.0, quinta=0.35):
    """El sol de Novilis: una nota honda con muchos armonicos (el brillo los
    abre), dos voces casi iguales que laten entre si, la quinta que entra y
    sale, un pulso lento como un corazon de plasma y, por debajo, el rugido
    sordo del fuego. f, brillo y latido pueden ser curvas."""
    n = n_(dur)
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    br = np.clip(np.broadcast_to(np.asarray(brillo, dtype=float), (n,)), 0, 1.2)
    lat = np.broadcast_to(np.asarray(latido, dtype=float), (n,))
    pulso = 0.72 + 0.28 * np.sin(2 * np.pi * np.cumsum(lat) / SR)
    pend = 2.4 - 1.5 * br                      # pendiente del espectro: menos, mas brillante
    lentos = [np.clip(1 + 0.25 * suave(n, 0.6), 0.2, None) for _ in range(4)]
    out = np.zeros(n)
    for v, det in enumerate((0.0, 0.37)):
        fase = 2 * np.pi * np.cumsum(f + det) / SR + rng.uniform(0, 6)
        for k in range(1, 40):
            if k * np.max(f) > 11000:
                break
            out += np.exp(-pend * np.log(k)) * np.sin(k * fase + rng.uniform(0, 6)) * lentos[(k + v) % 4]
    fase5 = 2 * np.pi * np.cumsum(f * 1.5) / SR
    q5 = sum(np.sin(k * fase5 + rng.uniform(0, 6)) / k ** 1.6 for k in range(1, 7))
    q5 *= np.clip(0.5 + 0.5 * suave(n, 0.35), 0, None)
    fuego = pb(llama(dur, 0.6, 0.5 + 0.6 * br, 6.0, 0.4, 1.2), 1100)
    return mezclar(pico(out * pulso, 1.0), pico(q5 * pulso, quinta), pico(fuego, 0.35 * plasma))


def tono_sube(dur, f0, f1, voces=3, brillo=0.4, det=7.0, curvatura=1.0):
    """Un tono brillante que sube (energia que se carga): senos con pocos
    armonicos, un coro de voces un poco desafinadas y un brillo que crece."""
    n = n_(dur)
    x = np.linspace(0, 1, n) ** curvatura
    f = f0 * (f1 / f0) ** x
    out = np.zeros(n)
    for v in range(voces):
        c = (v - (voces - 1) / 2) * det + rng.normal(0, 1.5)
        fase = 2 * np.pi * np.cumsum(f * 2 ** (c / 1200)) / SR + rng.uniform(0, 6)
        for k, a in ((1, 1.0), (2, 0.35 * brillo + 0.1), (3, 0.25 * brillo), (4, 0.15 * brillo), (6, 0.08 * brillo)):
            out += a * np.sin(k * fase) * (k * np.max(f) < 15000)
    return out * (0.4 + 0.6 * x)


def campana(f, tau=1.5, parciales=CAMPANA, dureza=0.5):
    """Una campana de oro: el hum una octava abajo, la tercera menor, la
    quinta y la octava; larga y batiendo despacio."""
    return metal(f, None, tau, parciales, dureza, 0.0012, 0.5)


def destellos(dur, tasa, fmin=2500, fmax=8000, tau=(0.05, 0.25)):
    """Brillo de luz: campanitas agudas y sueltas (tasa: numero o curva)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(1.8))
    for i in cuando:
        g = metal(rng.uniform(fmin, fmax), None, rng.uniform(*tau), BARRA[:3], 0.2, 0.002) * rng.uniform(0.2, 1.0)
        out[i:i + len(g)] += g[:len(out) - i]
    return out[:n] if np.any(out) else np.zeros(n)


# ======================================================================
#  CORO (las estatuas, la liberacion)
# ======================================================================
CORO_ALTO = {'a': ((800, 1150, 2900, 3900), (80, 90, 120, 130), (0, -6, -32, -20)),
             'o': ((450, 800, 2830, 3800), (70, 80, 100, 130), (0, -11, -22, -22)),
             'u': ((325, 700, 2700, 3800), (50, 60, 170, 180), (0, -16, -35, -40))}
CORO_BAJO = {'a': ((600, 1040, 2250, 2450), (60, 70, 110, 120), (0, -7, -9, -9)),
             'o': ((400, 750, 2400, 2600), (40, 80, 100, 120), (0, -11, -21, -20)),
             'u': ((350, 600, 2400, 2675), (40, 80, 100, 120), (0, -20, -32, -28))}


def coro(dur, notas, vocal='a', voces=4, vib=(5.2, 16.0), det=9.0, aliento=0.08):
    """Un coro: por cada nota, varias voces un poco desafinadas con vibrato
    que llega tarde (una fuente de pulsos de la glotis) y los formantes de la
    vocal (de soprano y alto arriba, de tenor y bajo abajo)."""
    n = n_(dur)
    t = t_(dur)
    out = np.zeros(n)
    for m in notas:
        f0 = hz(m)
        F, W, G = (CORO_ALTO if m >= 57 else CORO_BAJO)[vocal]
        src = np.zeros(n)
        for _ in range(voces):
            cents = (rng.normal(0, det) + vib[1] * paso((t - 0.25) / 0.5) * np.sin(2 * np.pi * vib[0] * rng.uniform(0.93, 1.07) * t
                                                                                  + rng.uniform(0, 6)) + 5 * suave(n, 0.8))
            fase = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / SR + rng.uniform(0, 6)
            for k in range(1, int(min(40, 5000 / f0)) + 1):
                src += np.sin(k * fase + rng.uniform(0, 6)) / k ** 1.3
        src += aliento * np.std(src) * ruido(dur, 'rosa')
        y = sum(10 ** (g / 20) * resonar(src, Fi, Fi / Wi) for Fi, Wi, g in zip(F, W, G))
        out += pico(y, 1.0)
    return out


# ======================================================================
#  METALES: la trompeta de las estatuas
# ======================================================================
def metales(f, amp, fc, voz=1.0, coro_=2, det=5.0):
    """El sonido de un metal: diente de sierra limitado en banda (armonicos
    1/k) por el formante de la campana (1,25 kHz y 2,8 kHz, mas abajo cuanto
    mas grande el instrumento, `voz`), con un paso bajo que se abre con la
    intensidad (fc, en Hz: un metal suave es oscuro y uno fuerte, brillante).
    f, amp y fc son curvas; coro_ voces casi al unisono."""
    n = len(f)
    paso_c = 32
    idx = np.arange(0, n, paso_c)
    todo = np.arange(n)
    out = np.zeros(n)
    fmin = float(np.min(f))
    for c in range(coro_):
        cents = (c - (coro_ - 1) / 2) * det + 2.5 * suave(n, 0.9)
        fc_ = f * 2 ** (cents / 1200)
        fase = 2 * np.pi * np.cumsum(fc_) / SR + rng.uniform(0, 6)
        for k in range(1, 90):
            if k * fmin > 10500:
                break
            fk = k * f[idx]
            peso = (_campana_db(fk, 1250 * voz, 6.0, 0.55) * _campana_db(fk, 2800 * voz, 3.0, 0.45)
                    / np.sqrt(1 + (fk / fc[idx]) ** 4) / np.sqrt(1 + (fk / 9000) ** 6)) / k
            peso[fk > 15000] = 0.0
            out += np.interp(todo, idx, peso) * np.sin(k * fase)
    return out * amp


def nota_metal(m, dur, vel=0.7, art='leg', voz=1.0, brillo=1.0, soltar=0.11, vib=(5.2, 13.0, 0.32), scoop=32.0):
    """Una nota de trompeta: ataque de lengua (un golpe de aire con el tono
    que entra un poco bajo), el cuerpo segun la articulacion, vibrato que
    llega tarde, el brillo que sigue a la intensidad y el aliento."""
    f0 = hz(m)
    total = dur + soltar
    n = n_(total)
    t = t_(total)
    tt = np.minimum(t, dur)
    if art == 'acc':
        forma = 0.72 + 0.28 * np.exp(-tt / 0.12)
    elif art == 'cresc':
        forma = 0.62 + 0.5 * (tt / dur) ** 1.4
    elif art == 'dim':
        forma = 1.0 - 0.6 * (tt / dur) ** 0.9
    else:
        forma = 0.9 + 0.1 * np.exp(-tt / 0.15)
    ataque = 0.028 if art != 'cresc' else 0.05
    lengua = 1 + 0.16 * vel * np.exp(-t / 0.05)
    suelta = np.where(t < dur, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - dur) / soltar, 0, 1)))
    amp = vel * paso(t / ataque) ** 0.8 * forma * lengua * suelta * (1 + 0.025 * suave(n, 5))
    fc = f0 * 1.3 + (650 + 5200 * brillo) * np.clip(amp, 0, 1.2) ** 1.6
    cents = -scoop * (0.5 + vel) * np.exp(-t / 0.03)
    cents += vib[1] * paso((t - vib[2]) / 0.35) * np.sin(2 * np.pi * vib[0] * rng.uniform(0.95, 1.05) * t + rng.uniform(0, 6))
    cents += 3.0 * suave(n, 1.2)
    f = f0 * 2 ** (cents / 1200)
    x = metales(f, amp, fc, voz)
    # el aire: un golpe de lengua corto (unos -10 dB bajo la nota) y un hilo
    # que sigue a la intensidad, medidos contra lo que suena la nota por
    # unidad de intensidad
    por_unidad = np.std(x) / (np.sqrt(np.mean(amp ** 2)) + 1e-12)
    aire = bp(ruido(total), 1000 * voz, 4500 * voz, 3)
    aire *= por_unidad / (np.std(aire) + 1e-12) * (0.3 * vel * np.exp(-t / 0.015) * paso(t / 0.003) + 0.03 * amp)
    return x + aire


DINAMICAS = {'pp': 0.25, 'p': 0.36, 'mp': 0.5, 'mf': 0.63, 'f': 0.78, 'ff': 0.92, 'fff': 1.0}


def leer_linea(texto, unidad):
    """'C5:1.5 C5:0.5 F5:2 | ...' -> [(inicio s, duracion s, midi, intensidad,
    articulacion)]. Dinamicas sueltas (pp..fff); sufijos > acento, < crescendo,
    - diminuendo; 'r' silencio; '|' comprueba que el compas mida 4."""
    notas = []
    t = 0.0
    vel = DINAMICAS['mf']
    en_compas = 0.0
    for tok in texto.split():
        if tok == '|':
            assert abs(en_compas - 4) < 1e-6, ('compas de %.3f en %s' % (en_compas, texto[:30]))
            en_compas = 0.0
            continue
        if tok in DINAMICAS:
            vel = DINAMICAS[tok]
            continue
        art = 'leg'
        if tok[-1] in '><-':
            art = {'>': 'acc', '<': 'cresc', '-': 'dim'}[tok[-1]]
            tok = tok[:-1]
        nm, d = tok.split(':')
        d = float(d)
        en_compas += d
        if nm != 'r':
            notas.append((t * unidad, d * unidad, midi(nm), vel * (1.12 if art == 'acc' else 1.0), art))
        t += d
    assert abs(en_compas - 4) < 1e-6 or en_compas == 0, 'ultimo compas incompleto'
    return notas


def trompeta_muere(m=72, dur=2.4, voz=1.0):
    """Una trompeta que se ahoga: la nota sube de golpe a un chillido (sobre-
    soplada, brillante del todo), se quiebra y cae dos octavas mientras el
    aire se le corta a tirones."""
    n = n_(dur)
    t = t_(dur)
    cents = curva(n, [(0, 0), (0.04, 0), (0.09, 1500), (0.16, 1380), (0.3, 300), (0.6, -1200), (1, -2300)])
    f = hz(m) * 2 ** ((cents + 25 * suave(n, 9)) / 1200)
    corte = np.clip(0.55 + 0.45 * np.tanh(3 * suave(n, 14)) - 0.6 * (t / dur) ** 1.5, 0, 1)
    amp = curva(n, [(0, 0.0), (0.015, 1.0), (0.18, 1.05), (0.4, 0.7), (1, 0.0)]).clip(0, None) * (0.4 + 0.6 * corte)
    fc = curva(n, [(0, 6000), (0.15, 9000), (0.4, 2500), (1, 500)])
    x = metales(f, amp, fc, voz)
    aire = bp(ruido(dur), 1200, 6000) * amp * (0.3 + 0.7 * (1 - corte))
    return mezclar(pico(x, 1.0), pico(aire, 0.18))


# ======================================================================
#  VOZ: un caballero con yelmo
# ======================================================================
H_A = (730, 1090, 2440, 3400)
H_O = (570, 840, 2410, 3300)
H_U = (330, 800, 2240, 3200)
ANCHOS_H = (100, 120, 170, 250)
GAN_H = (1.0, 0.72, 0.32, 0.18)


def formantes_voz(cerrada, abierta, abre, escala=0.78):
    """Formantes de la voz segun lo abierta que este la boca (numero o
    curva), en un tracto enorme (`escala` < 1: todo mas grave)."""
    return tuple(((c + (o - c) * abre) * escala, w, g) for c, o, w, g in zip(cerrada, abierta, ANCHOS_H, GAN_H))


def garganta(f0, dur, formantes, aspereza=0.5, sub=0.4, jitter=0.03, aliento=0.25, fmax=5000,
             caos=0.0, fritura=0.0, fritura_hz=26.0, pecho=0.0):
    """Una garganta: pulsos con jitter, subarmonico que la raspa, tramos
    caoticos, fritura (los pulsos que se oyen sueltos), formantes y el pecho."""
    n = n_(dur)
    f0 = np.broadcast_to(np.asarray(f0, dtype=float), (n,))
    f = f0 * (1 + jitter * suave(n, 25)) * (1 + 0.25 * jitter * suave(n, 140))
    fase = 2 * np.pi * np.cumsum(f) / SR
    src = np.zeros(n)
    for k in range(1, int(min(160, fmax / np.max(f))) + 1):
        src += np.sin(k * fase) / k ** 1.1
    sub = np.broadcast_to(np.asarray(sub, dtype=float), (n,))
    src *= 1 + sub * np.sin(fase / 2 + 0.3 * suave(n, 3))
    src *= 1 + 0.3 * aspereza * suave(n, 60)
    sd = np.std(src)
    caos = np.broadcast_to(np.asarray(caos, dtype=float), (n,))
    if np.any(caos > 0):
        rasp = ruido(dur, 'rosa') * (0.5 + 0.5 * np.cos(fase)) ** 2
        src = src * (1 - 0.6 * caos) + caos * 2.2 * sd * rasp / (np.std(rasp) + 1e-12)
    if np.any(np.asarray(fritura) > 0):
        fr = np.broadcast_to(np.asarray(fritura_hz, dtype=float), (n,)) * (1 + 0.12 * suave(n, 6))
        pul = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(fr) / SR)) ** 3
        fri = np.broadcast_to(np.asarray(fritura, dtype=float), (n,))
        src *= (1 - fri) + fri * 2.2 * pul
    src += aliento * sd * ruido(dur, 'rosa') * (0.6 + 0.4 * np.sin(fase))
    out = np.zeros(n)
    for F, bw, g in formantes:
        if np.isscalar(F):
            out += g * resonar(src, F, F / bw)
        else:
            out += g * filtro_mov(src, F, 'band', float(np.mean(F)) / bw)
    if pecho:
        out += pecho * pb(src, 220) * np.std(out) / (np.std(pb(src, 220)) + 1e-12)
    return saturar(pico(out), 1.2 + 2.5 * aspereza)


_CASCOS = {}


def yelmo(x, cuanto=0.55, f=640.0):
    """El yelmo: la voz sale por las rendijas de una cabeza de acero. Un tubo
    corto que resuena (un peine con realimentacion), el casco que vibra con
    ella (los modos de una campana de acero muy amortiguada) y las rendijas
    que se comen los agudos."""
    D = max(2, int(round(SR / f)))
    peine = signal.lfilter([1.0], np.r_[1.0, np.zeros(D - 1), -0.55], x)
    if f not in _CASCOS:
        t = t_(0.12)
        r = np.random.default_rng(int(f))
        ir = sum(a * np.sin(2 * np.pi * f * k * t + r.uniform(0, 6)) * np.exp(-t / (0.05 / k ** 0.5)) for k, a in CASCO)
        _CASCOS[f] = ir / np.sqrt(np.sum(ir ** 2))
    casco = signal.fftconvolve(x, _CASCOS[f])[:len(x)]
    y = mezclar(pico(x, 1.0 - 0.5 * cuanto), pico(peine, 0.6 * cuanto), pico(casco, 0.45 * cuanto))
    return pb(y, 3400, 2)


def rugido(dur=3.4, f0=70.0, f1=116.0, abre=1.0, fuego=1.0, pecho=1.0, escala=0.76, cola=2.2, mezcla=0.28, sube=0.2,
           contorno=None, yelmo_=0.55):
    """El grito de guerra de Novilis: la garganta sube y cae de tono mientras
    la boca se abre de "o" a "a" y se cierra, con rugosidad a rachas en lo
    mas alto; una segunda voz algo desfasada y otra una octava abajo que le
    dan tamano; todo por el yelmo. El fuego de las grietas se aviva con el
    grito y las placas tiemblan."""
    n = n_(dur)
    if contorno is None:
        contorno = [(0, f0 / f1), (sube, 1.0), (0.5, 0.97), (0.78, 0.86), (1, 0.82 * f0 / f1)]
    tono = f1 * curva(n, contorno)
    ab = abre * curva(n, [(0, 0.1), (sube * 0.9, 0.9), (0.55, 1.0), (0.85, 0.55), (1, 0.12)])
    fs = formantes_voz(H_O, H_A, ab, escala)
    sub_ = curva(n, [(0, 0.15), (sube + 0.08, 0.45), (0.7, 0.35), (1, 0.25)])
    x = np.linspace(0, 1, n)
    caos = 0.03 + sum(h * np.exp(-((x - c) / w) ** 2) for c, w, h in
                      ((sube + 0.06, 0.05, 0.28), (rng.uniform(0.45, 0.55), 0.04, 0.2), (rng.uniform(0.66, 0.74), 0.05, 0.22)))
    voz = garganta(tono, dur, fs, 0.6, sub_, 0.016, 0.18, 5500, caos, pecho=0.35)
    doble = garganta(tono * 1.005, dur, fs, 0.6, sub_, 0.02, 0.18, 5500, caos, pecho=0.35)
    hondo = garganta(tono * 0.5, dur, formantes_voz(H_U, H_O, ab * 0.5, escala * 0.9), 0.75, 0.5, 0.04, 0.3, 2800,
                     fritura=0.3, pecho=0.6)
    amp = ventana(dur, 0.08, dur * 0.38) * curva(n, [(0, 0.4), (sube, 1.0), (0.6, 0.92), (1, 0.6)])
    v = mezclar(pico(voz * amp, 1.0), en(0.009, pico(doble * amp, 0.35)), pico(hondo * amp, 0.45 * pecho))
    v = yelmo(v, yelmo_)
    arde = llama(dur, 1.0, 0.7 + 0.7 * amp) * amp
    tiembla = placas(dur, 45 * amp)
    capas = [pico(v, 1.0), pico(arde, 0.2 * fuego), pico(tiembla, 0.07), pico(boom(48, 26, 0.4), 0.3)]
    return reverb(mezclar(*capas), mezcla, cola, 6500)


def quejido(dur=0.65, f=105.0, abre=0.8, escala=0.8):
    """Un gruñido de dolor por el yelmo: sube de golpe, se abre y se cierra."""
    n = n_(dur)
    tono = curva(n, [(0, f * 0.9), (0.15, f * 1.3), (0.5, f * 1.1), (1, f * 0.72)])
    fs = formantes_voz(H_U, H_A, curva(n, [(0, 0.3), (0.15, abre), (1, 0.2)]), escala)
    v = garganta(tono, dur, fs, 0.7, 0.4, 0.025, 0.3, 5000, 0.15, pecho=0.3)
    return yelmo(v * caida(dur, dur * 0.3, 0.02), 0.6)


def respiro(dur, sale=True, f0=52.0, voz=0.35, fuerza=1.0):
    """Una bocanada por las rendijas del yelmo: el aire por un tracto enorme
    (ruido por formantes graves) que resuena en el casco y, al soltarlo, la
    garganta que vibra un poco."""
    n = n_(dur)
    if sale:
        env = ventana(dur, dur * 0.12, dur * 0.65) * curva(n, [(0, 1.0), (1, 0.55)])
        F = ((300, 2.2, 1.0), (760, 3.5, 0.6), (1400, 5.0, 0.3))
    else:
        env = ventana(dur, dur * 0.6, dur * 0.18)
        F = ((440, 2.5, 1.0), (1100, 4.0, 0.7), (2200, 6.0, 0.35))
    x = ruido(dur, 'rosa')
    aire = sum(g * resonar(x, f, q) for f, q, g in F) * (1 + 0.25 * suave(n, 10))
    capas = [pico(aire * env, 1.0)]
    if sale and voz:
        v = garganta(curva(n, [(0, f0), (1, f0 * 0.88)]), dur, formantes_voz(H_U, H_O, 0.15, 0.8), 0.7, 0.45, 0.04, 1.0, 3000,
                     fritura=0.45, fritura_hz=22.0, pecho=0.5)
        capas.append(pico(v * env, voz))
    return fuerza * yelmo(mezclar(*capas), 0.5, 600.0)


# ======================================================================
#  Guardar
# ======================================================================
# Duracion maxima de cada evento (lo demas es cola muy floja que se apaga).
LARGOS = {'despertar': 7.6, 'paso': 1.5, 'ambiente': 6.0, 'herido': 1.5, 'rugido': 5.0, 'tajo': 0.9, 'tajo_fuego': 2.2,
          'castigo_alza': 1.65, 'castigo_aviso': 0.95, 'castigo_rayo': 3.6, 'castigo_clava': 3.8, 'onda': 2.4,
          'sol_forma': 1.15, 'sol_lanza': 1.3, 'sol_explota': 4.2, 'lava': 3.0, 'estatuas': 5.0, 'estatua_golpe': 1.5,
          'estatua_rota': 3.6, 'carga': 15.0, 'supernova': 8.5,
          'embestida': 2.6, 'camino': 2.8, 'infernal_salto': 1.8, 'infernal_golpe': 3.8, 'grieta': 2.6, 'geiser': 2.2,
          'infernal_explota': 5.0, 'mar': 6.0,
          'sol_apaga': 4.2, 'ofrenda_marca': 2.2, 'ofrenda_agarra': 1.8, 'ofrenda_tecla': 0.35, 'ofrenda_fallo': 0.8,
          'ofrenda_libre': 2.3, 'dios': 4.8, 'dios_aviso': 1.8, 'dios_explosion': 2.9, 'grito': 2.6, 'furia': 3.9,
          'aturdido': 4.5, 'tambaleo': 4.6, 'inmune': 1.2, 'liberacion': 6.5, 'disolver': 3.8}
ALTO = 10 ** (-3.0 / 20)          # pico de cada .ogg: -3 dBFS


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


def _escribir(nombre, x):
    """Escribe el .ogg y lo vuelve a leer: Vorbis puede subir un pelo los
    picos; si pasan de -2,5 dBFS se baja y se escribe otra vez."""
    ruta = os.path.join(OUT, nombre + '.ogg')
    for _ in range(3):
        # por bloques: libsndfile se cae si se le da un fichero largo de golpe
        with sf.SoundFile(ruta, 'w', SR, 1, subtype='VORBIS', format='OGG') as fh:
            y = x.astype(np.float32)
            for i in range(0, len(y), 32768):
                fh.write(y[i:i + 32768])
        z, _sr = sf.read(ruta, dtype='float64')
        pk = np.max(np.abs(z))
        if pk <= 10 ** (-2.5 / 20):
            break
        x = x * (ALTO / pk)
    return z


def guardar(evento, x, variante=None, alto=ALTO, limite=None, largo=None, techo=None, exacto=None, normalizar=True):
    """`largo`: duracion maxima; la cola que sobra se apaga con una rampa de
    coseno. `techo`: sonoridad maxima (dB A): los toques tonales, con poco
    pico y mucha energia, no deben sonar mas que los golpes. `exacto`: la
    duracion justa en segundos, sin recortar la cola (las melodias)."""
    x = pa(np.asarray(x, dtype=float), 25)
    if limite:
        x = limitar(x, limite)
    if exacto:
        x = np.concatenate([x, np.zeros(max(0, n_(exacto) - len(x)))])[:n_(exacto)].copy()
    else:
        largo = largo or LARGOS.get(evento)
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
    if normalizar:
        x = pico(x, alto)
        if techo is not None:
            x *= min(1.0, 10 ** ((techo - sonoridad_a(x)) / 20))
    nombre = evento if variante is None else f'{evento}{variante}'
    z = _escribir(nombre, x)
    EVENTOS.setdefault(evento, []).append(nombre)
    GUARDADOS.append((nombre, z))
    pk = 20 * np.log10(np.max(np.abs(z)) + 1e-12)
    rms = 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-12)
    aviso = '  <-- FLOJO' if rms < -45 else ''
    print(f'  {nombre:18s} {len(z) / SR:6.2f} s  pico {pk:6.1f} dBFS  rms {rms:6.1f} dB{aviso}', flush=True)


# ======================================================================
#  AMBIENTE: el fuego de las grietas crepita bajo, respira hondo por el
#  yelmo, la armadura cruje un poco y su sol zumba arriba.
# ======================================================================
for i in range(3):
    d = 5.6
    n = n_(d)
    arde = llama(d, 0.7, 0.6 + 0.1 * i, 6.0, 0.8, 0.9) * ventana(d, 1.0, 1.5)
    entra = respiro(1.5, False)
    sale = respiro(2.3, True, 50.0 + 3 * i, 0.4)
    cruje = chirriar(0.9, 330 + 60 * i, (22, 60), 30) * campana_env(0.9, 1.4)
    sol = zumbido_solar(d, 55.0 + 2 * i, 0.3, 0.7, 0.5) * ventana(d, 1.5, 1.8)
    capas = mezclar(pico(arde, 0.32), en(0.2, pico(entra, 0.45)), en(1.6, pico(sale, 0.8)), en(0.8 + 1.4 * i, pico(cruje, 0.14)),
                    pico(sol, 0.1))
    guardar('ambiente', reverb(capas, 0.28, 1.8, 5500), i + 1, alto=10 ** (-5 / 20))


# ======================================================================
#  PASO: un escarpe de acero de dos bloques sobre las losas del altar: el
#  golpe hondo, las placas que chocan, la piedra que cruje y las brasas que
#  sisean al pisar.
# ======================================================================
def pisada(peso=1.0):
    sub = saturar(boom(70, 28, 0.16 * peso), 2.2)
    cuerpo = bp(ruido(0.3, 'rosa'), 80, 650) * caida(0.3, 0.05 * peso, 0.002)
    escarpe = clang(rng.uniform(170, 230), 0.22, 1.0, 0.4)
    placas_ = en(0.03, placas(0.4, 260 * np.exp(-t_(0.4) / 0.07)))
    cruje = grava(0.45, 2200 * np.exp(-t_(0.45) / 0.03), (0.4, 3.0))
    machaca = rajar_roca(4, 0.03, 1.0, 0.8)
    brasas = en(0.04, chasquidos(0.9, 500 * np.exp(-t_(0.9) / 0.15) + 5))
    vapor = en(0.03, siseo(0.6, 3000, 9000) * caida(0.6, 0.12, 0.01))
    return mezclar(pico(sub, 0.4), pico(cuerpo, 0.7), en(0.004, pico(escarpe, 0.5)), pico(placas_, 0.22), pico(cruje, 0.5),
                   pico(machaca, 0.45), pico(brasas, 0.22), pico(vapor, 0.07))


for i in range(4):
    guardar('paso', reverb(pisada(1.0 + 0.1 * i), 0.15, 1.0, 5000), i + 1, limite=0.45)

# ======================================================================
#  HERIDO: el arma contra el peto: la placa suena, el golpe sordo, las
#  brasas que saltan de la grieta y un gruñido por el yelmo.
# ======================================================================
for i in range(3):
    golpe = clang(rng.uniform(280, 380), 0.45, 1.0)
    brasas = chasquidos(0.6, 900 * np.exp(-t_(0.6) / 0.08))
    queja = quejido(0.65, 100 + 10 * i)
    guardar('herido', reverb(mezclar(pico(golpe, 0.85), pico(brasas, 0.25), en(0.03, pico(queja, 0.95))), 0.22, 1.6),
            i + 1, limite=0.6)

# ======================================================================
#  INMUNE: el golpe resbala por el acero sin hacer nada: un clang limpio y
#  claro y el filo que patina.
# ======================================================================
for i in range(3):
    choque = clang(620 + 120 * i, 0.32, 1.0, 0.25)
    patina = pasada(0.16, 5000, 2500, 3.0, 0.4) * 0.5
    chispa = chasquidos(0.2, 300 * np.exp(-t_(0.2) / 0.04))
    guardar('inmune', reverb(mezclar(pico(choque, 1.0), en(0.01, pico(patina, 0.2)), pico(chispa, 0.12)), 0.2, 1.4), i + 1,
            limite=0.6, techo=-19.0)

# ======================================================================
#  RUGIDO: el grito de guerra, metalico y enorme
# ======================================================================
guardar('rugido', rugido(3.4, 70, 116), 1, limite=0.6)
guardar('rugido', rugido(3.1, 66, 108, escala=0.73, contorno=[(0, 0.6), (0.18, 1.0), (0.45, 1.04), (0.75, 0.88), (1, 0.62)]), 2,
        limite=0.6)

# ======================================================================
#  DESPERTAR: se levanta de la rodilla. La armadura cruje bajo el peso, el
#  guantelete en la rodilla, las placas que se asientan, el pie que se
#  planta; el fuego prende en las grietas una tras otra, su sol se enciende
#  arriba de golpe y ruge por el yelmo.
# ======================================================================
d = 7.5
dl = 2.7
cruje = chirriar(dl, 300, (25, 90), 30, velocidad=curva(n_(dl), [(0, 0.4), (0.5, 1.0), (1, 0.7)]), peso=1.4)
cruje *= np.interp(t_(dl), [0, 0.3, 2.2, dl], [0, 1, 0.8, 0])
cruje2 = en(0.7, chirriar(1.6, 520, (40, 120), 45) * campana_env(1.6, 1.2))
asientan = mezclar(*[en(s, placas(0.35, 160 * np.exp(-t_(0.35) / 0.1))) for s in (0.4, 1.15, 1.75, 2.5)])
rodilla = en(1.05, clang(190, 0.4, 1.0, 0.8))
pie = en(2.5, pisada(1.3))
grietas = mezclar(*[en(s, ignicion(0.6, a, 2200, 80)) for s, a in zip(np.sort(rng.uniform(1.6, 3.0, 6)), np.linspace(0.4, 0.9, 6))])
dl = d - 1.8
arde = en(1.8, llama(dl, 1.0, curva(n_(dl), [(0, 0.5), (0.25, 1.1), (1, 0.8)])) * np.interp(t_(dl), [0, 1.2, dl - 1.5, dl], [0, 1, 0.8, 0]))
sol = en(3.0, mezclar(pico(ignicion(1.6, 1.0, 5000, 45, aspira=0.4), 1.0),
                      en(0.4, pico(zumbido_solar(4.0, 55, 0.6, 1.0) * ventana(4.0, 0.25, 2.2), 0.55)),
                      en(0.2, pico(tono_sube(1.4, 220, 880) * ventana(1.4, 0.4, 0.5), 0.18))))
voz = en(4.0, rugido(3.3, 66, 104, cola=2.0))
guardar('despertar', mezclar(pico(reverb(mezclar(pico(cruje, 0.5), pico(cruje2, 0.25), pico(asientan, 0.25), pico(rodilla, 0.45),
                                                 pico(pie, 0.75)), 0.25, 1.8), 0.6),
                             pico(reverb(mezclar(pico(grietas, 0.5), pico(arde, 0.35)), 0.25, 1.8), 0.45),
                             pico(reverb(sol, 0.3, 2.2), 0.6), pico(voz, 0.95)), limite=0.55)

# ======================================================================
#  TAJO: el flamberge (una hoja de diez bloques envuelta en fuego) barre el
#  aire: el soplo grave que pasa, el fuego que ruge pegado a la hoja, el
#  filo que canta un instante y las brasas que quedan detras.
# ======================================================================
for i in range(3):
    d = 0.65
    n = n_(d)
    t = t_(d)
    barre = pasada(d, 220 + 30 * i, 900 + 150 * i, 1.2, 0.12)
    fc = curva(n, [(0, 400), (0.45, 1600 + 200 * i), (1, 500)])
    fuego = filtro_mov(llama(d, 1.0, 1.2, 14.0, 0.0), fc, 'band', 0.7) * campana_env(d, 1.2)
    filo = metal(rng.uniform(1900, 2400), None, 0.12, BARRA[:3], 0.3) * 0.5
    rastro = en(0.2, chasquidos(0.6, 400 * np.exp(-t_(0.6) / 0.15)))
    hondo = pb(ruido(d, 'marron'), 120) * campana_env(d, 1.5)
    guardar('tajo', reverb(mezclar(pico(barre, 1.0), pico(fuego, 0.6), en(0.18, pico(filo, 0.08)), pico(rastro, 0.2),
                                   pico(hondo, 0.35)), 0.2, 1.3), i + 1, limite=0.6)

# TAJO DE FUEGO: de la hoja sale una media luna de fuego que se aleja: la
# bocanada al soltarse, el fuego que ruge y se va (cada vez mas grave y mas
# lejos: el aire se come los agudos) y las brasas que se quedan.
for i in range(2):
    d = 2.0
    n = n_(d)
    t = t_(d)
    lejos = (t / d) ** 0.8
    sale = ignicion(0.8, 1.0, 4500, 60)
    ruge = llama(d, 1.0, curva(n, [(0, 1.6), (1, 0.45)]), 12.0, 0.6) * (1 - 0.85 * lejos)
    ruge = filtro_mov(ruge, curva(n, [(0, 6000), (1, 900)]), 'low', 0.8)
    aire = pasada(d, 1600 + 200 * i, 300, 1.2, 0.08) * (1 - 0.6 * lejos)
    brasas = chasquidos(d, 300 * np.exp(-t / 0.4))
    guardar('tajo_fuego', reverb(mezclar(pico(sale, 0.8), pico(ruge, 0.75), pico(aire, 0.5), pico(brasas, 0.15)), 0.28, 2.0),
            i + 1, limite=0.55)

# ======================================================================
#  CASTIGO SOLAR: alza la espada al cielo y se bebe el sol (un zumbido que
#  sube una octava y se abre, el fuego que se aspira y el brazo que cruje);
#  la marca bajo un jugador (una campanada clara con el zumbido); el rayo de
#  fuego solar (el aire que se carga chisporroteando, el chasquido de trueno,
#  el golpe, la bola de fuego y el trueno que rueda); y la espada clavada en
#  el suelo (el golpe enorme, la hoja que vibra, la piedra que se raja y la
#  lava que sisea por las grietas).
# ======================================================================
d = 1.6
n = n_(d)
t = t_(d)
sube = zumbido_solar(d, curva(n, [(0, 55), (1, 110)]), curva(n, [(0, 0.2), (1, 0.95)]), curva(n, [(0, 1.5), (1, 9.0)]))
sube *= rampa(d, 1.6, 0.15, 1.0)
aspira = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 300), (1, 3000)]), 'low', 0.9) * rampa(d, 2.0)
brazo = chirriar(0.7, 420, (40, 110), 40) * campana_env(0.7, 1.3)
brillo = tono_sube(d, 330, 1320, 3, 0.6) * rampa(d, 2.5)
guardar('castigo_alza', reverb(mezclar(pico(sube, 1.0), pico(aspira, 0.35), pico(brazo, 0.25), pico(brillo, 0.18)), 0.25, 1.8),
        limite=0.6)

for i in range(2):
    d = 0.9
    tono = mezclar(pico(campana(880.0 * (1 + 0.06 * i), 0.5), 1.0), en(0.015, pico(campana(1318.5 * (1 + 0.06 * i), 0.35), 0.6)))
    zumba = zumbido_solar(d, 110.0 * (1 + 0.06 * i), 0.6, 4.0, 0.3) * ventana(d, 0.08, 0.45)
    guardar('castigo_aviso', reverb(mezclar(pico(tono, 0.9), pico(zumba, 0.5)), 0.25, 1.4), i + 1, techo=-19.0)

for i in range(2):
    dc = 0.3
    carga = mezclar(crepitar(dc, curva(n_(dc), [(0, 200), (1, 4000)]), curva(n_(dc), [(0, 1200), (1, 4500)]), 1.0),
                    0.4 * tono_sube(dc, 600, 2400, 2, 0.8)) * rampa(dc, 1.5)
    d = 3.2
    t = t_(d)
    trueno = mezclar(pico(crepitar(0.25, 6000 * np.exp(-t_(0.25) / 0.05), 2500, 0.6), 1.0),
                     pico(pa(ruido(0.05), 500) * caida(0.05, 0.005, 0.0002), 0.9))
    rueda = retumbo(d, 160, 3.0, 0.6) * np.interp(t, [0, 0.2, 1.0, d], [0, 1, 0.55, 0])
    golpe = explosion(1.1, d, 0.0, 1.0, 1.0, 0.8)
    guardar('castigo_rayo', reverb(mezclar(pico(carga, 0.45), en(dc, pico(trueno, 0.85)), en(dc, pico(golpe, 1.0)),
                                           en(dc + 0.05, pico(rueda, 0.5))), 0.3, 2.6, 5500), i + 1, limite=0.5)

d = 3.6
t = t_(d)
desliza = pasada(0.25, 5000, 2000, 2.5, 0.5)
golpe = golpe_tierra(2.2, 1.6, 1.3, 3.2)
hoja = metal(132.0, 2.5, 1.1, BARRA, 0.8, 0.003, 0.5)
raja = mezclar(*[en(s, rajar_roca(int(rng.integers(8, 16)), 0.08, 1.0, 0.8)) for s in np.sort(rng.uniform(0.05, 0.7, 5))])
grieta = crepitar(1.6, 900 * np.exp(-t_(1.6) / 0.5), curva(n_(1.6), [(0, 2500), (1, 800)]), 1.3)
vapor = en(0.45, siseo(2.4) * np.interp(t_(2.4), [0, 0.3, 1.2, 2.4], [0, 1, 0.5, 0]))
lava = en(0.6, lava_charco(2.4, 9.0, 0.5) * np.interp(t_(2.4), [0, 0.4, 1.5, 2.4], [0, 1, 0.6, 0]))
guardar('castigo_clava', reverb(mezclar(pico(desliza, 0.3), en(0.08, pico(golpe, 1.0)), en(0.08, pico(hoja, 0.35)),
                                        en(0.1, pico(raja, 0.5)), en(0.15, pico(grieta, 0.3)), pico(vapor, 0.12), pico(lava, 0.3)),
                                0.3, 2.6, 5000), limite=0.45)

# ======================================================================
#  ONDA: un anillo de fuego que corre por el suelo hacia fuera: prende de
#  golpe, pasa rugiendo (se acerca, pasa y se va: la banda sube y baja), con
#  las brasas y el suelo que retumba.
# ======================================================================
for i in range(2):
    d = 2.2
    n = n_(d)
    t = t_(d)
    prende = ignicion(1.0, 1.0, 3000, 55)
    cerca = np.exp(-((t - 0.55 - 0.05 * i) / 0.35) ** 2)
    pasa = llama(d, 1.0, 0.6 + 1.1 * cerca, 12.0, 1.0) * (0.25 + 0.75 * cerca) * ventana(d, 0.05, 0.6)
    aire = filtro_mov(ruido(d, 'rosa'), 300 + 1500 * cerca, 'band', 1.1) * (0.2 + 0.8 * cerca) * ventana(d, 0.05, 0.6)
    suelo = retumbo(d, 120, 2.0, 0.4) * np.interp(t, [0, 0.1, 0.8, d], [0, 1, 0.5, 0])
    guardar('onda', reverb(mezclar(pico(prende, 0.7), pico(pasa, 0.8), pico(aire, 0.35), pico(suelo, 0.35)), 0.25, 1.8),
            i + 1, limite=0.55)

# ======================================================================
#  SOL x3: un sol pequeno se forma en su mano (zumba cada vez mas hondo y
#  mas fuerte, el fuego se aspira); lo lanza (un soplo pesado, el sol que se
#  aleja zumbando); revienta (fuego y lava).
# ======================================================================
d = 1.1
n = n_(d)
nace = zumbido_solar(d, curva(n, [(0, 70), (1, 98)]), curva(n, [(0, 0.3), (1, 0.85)]), curva(n, [(0, 3), (1, 12)]))
aspira = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 400), (1, 2600)]), 'low', 0.9)
chispas = chasquidos(d, curva(n, [(0, 20), (1, 500)]))
guardar('sol_forma', reverb(mezclar(pico(nace, 1.0), pico(aspira, 0.3), pico(chispas, 0.2)) * rampa(d, 1.3, 0.15, 1.0), 0.22, 1.5),
        limite=0.6)

for i in range(2):
    d = 1.2
    n = n_(d)
    t = t_(d)
    soplo = pasada(d, 180 + 20 * i, 650, 1.0, 0.06)
    hondo = pb(ruido(d, 'marron'), 140) * campana_env(d, 1.2)
    va = zumbido_solar(d, curva(n, [(0, 98), (1, 80)]), 0.6, 10.0) * np.exp(-t / 0.35)
    fuego = llama(d, 1.0, curva(n, [(0, 1.3), (1, 0.5)])) * np.exp(-t / 0.4)
    esfuerzo = quejido(0.45, 78, 0.6, 0.76)
    guardar('sol_lanza', reverb(mezclar(pico(soplo, 1.0), pico(hondo, 0.5), pico(va, 0.5), pico(fuego, 0.4), pico(esfuerzo, 0.25)),
                                0.22, 1.6), i + 1, limite=0.6)

for i in range(2):
    guardar('sol_explota', reverb(explosion(1.4 + 0.1 * i, 3.8, 1.0, 1.1, 0.95 - 0.08 * i, 0.7), 0.3, 2.6, 5500), i + 1, limite=0.45)

# LAVA: un charco que borbotea y sisea (casi en bucle: entra y sale suave).
for i in range(2):
    d = 3.0
    guardar('lava', lava_charco(d, 6.0 + 2 * i, 1.0, 1.0 - 0.1 * i) * ventana(d, 0.25, 0.3), i + 1, alto=10 ** (-4 / 20))

# ======================================================================
#  TROMPETAS DEL APOCALIPSIS: cuatro estatuas de angeles suben del suelo
#  (la piedra que se arrastra, el retumbo, lo que cae) y un coro que se
#  hincha un momento; los golpes en el marmol (piedra dura y un poco del
#  bronce de la trompeta que suena); la estatua que revienta, con su
#  trompeta que chilla y se ahoga.
# ======================================================================
d = 4.8
n = n_(d)
t = t_(d)
sube_env = np.interp(t, [0, 0.4, 2.8, 3.6, d], [0, 0.6, 1.0, 0.3, 0])
muele =mezclar(*[en(s, moler(3.2, 1.8 + 0.2 * k, (9, 26), 0.6) * ventana(3.2, 0.4, 0.8)) for k, s in enumerate((0.0, 0.15, 0.3, 0.45))])
tierra = retumbo(d, 100, 1.2, 0.4, 0.8) * sube_env
caen = grava(d, 400 * sube_env, (0.4, 6.0))
asientan = mezclar(*[en(3.3 + 0.12 * k, mezclar(pico(canto(28, 1.0, False), 1.0), pico(boom(70, 35, 0.12), 0.7))) for k in range(4)])
voces = coro(3.2, [midi(x) for x in ('F3', 'C4', 'F4', 'Ab4', 'C5')], 'a', 4) * curva(n_(3.2), [(0, 0), (0.45, 1.0), (0.7, 0.8), (1, 0)])
guardar('estatuas', mezclar(pico(reverb(mezclar(pico(muele, 0.8), pico(tierra, 0.6), pico(caen, 0.35), pico(asientan, 0.5)), 0.28, 2.2),
                                 1.0),
                            en(1.4, pico(reverb(voces, 0.45, 3.0, 7000), 0.55))), limite=0.55)

for i in range(3):
    toc = canto(rng.uniform(16, 22), 1.0, False, 1.5)
    raja = rajar_roca(6 + 2 * i, 0.03, 1.2, 1.0)
    bronce = metal(rng.uniform(950, 1300), None, 0.3, CAMPANA[1:], 0.6)
    lascas = escombros(0.8, 0.25, 0.22, (0.4, 2.5))
    guardar('estatua_golpe', reverb(mezclar(pico(toc, 1.0), pico(raja, 0.5), pico(bronce, 0.22), pico(lascas, 0.3)), 0.22, 1.5),
            i + 1, limite=0.55, techo=-18.0)

for i in range(2):
    d = 3.4
    t = t_(d)
    revienta = mezclar(pico(saturar(boom(85, 32, 0.22), 2.5), 0.5), pico(rajar_roca(26, 0.12, 1.2, 0.8), 0.9),
                       pico(bp(ruido(0.3), 200, 6000) * caida(0.3, 0.04), 0.5))
    trozos = mezclar(*[en(rng.uniform(0.1, 0.6), rodar(1.6, rng.uniform(8, 20), 6, rng.uniform(0.5, 1.0))) for _ in range(5)])
    caen = escombros(2.4, 1.2, 0.4, (0.4, 8.0))
    trompeta = trompeta_muere(72 - 2 * i, 2.3)
    guardar('estatua_rota', mezclar(pico(reverb(mezclar(revienta, pico(trozos, 0.5), pico(caen, 0.45)), 0.28, 2.2), 0.85),
                                    en(0.04, pico(reverb(trompeta, 0.35, 2.4, 7000), 0.8))), i + 1, limite=0.5)

# ======================================================================
#  FUENTES SOLARES: ya no estan (Juan, 08-10-2026). Sus recetas se siguen
#  calculando sin guardarse, para que los numeros al azar que gastan sean
#  los mismos y los sonidos de despues (la carga, la supernova, la Ofrenda,
#  el Dios...) no cambien ni un pelo.
# ======================================================================
d = 3.2
capas = []
for k, (s, f) in enumerate(((0.0, 110.0), (0.38, 138.6), (0.74, 164.8))):
    dk = d - s
    nk = n_(dk)
    tk = t_(dk)
    rompe = mezclar(pico(rajar_roca(12, 0.06, 1.0, 0.8), 1.0), pico(saturar(boom(95, 40, 0.1), 2.0), 0.7))
    chorro = filtro_mov(llama(1.4, 1.0, 1.4, 14.0, 1.0), curva(n_(1.4), [(0, 400), (0.2, 2600), (1, 900)]), 'band', 0.8)
    chorro *= np.interp(t_(1.4), [0, 0.06, 0.5, 1.4], [0, 1, 0.6, 0])
    nota = zumbido_solar(dk, f, 0.55, 3.0, 0.4) * np.interp(tk, [0, 0.15, 1.0, dk], [0, 1, 0.45, 0])
    capas.append(en(s, mezclar(pico(rompe, 0.8), pico(chorro, 0.7), en(0.05, pico(nota, 0.35)),
                               pico(escombros(1.2, 0.5, 0.3, (0.4, 4.0)), 0.3))))
_ = reverb(mezclar(*capas), 0.3, 2.4)

for i in range(3):
    toc = canto(rng.uniform(18, 24), 1.0, False, 1.2)
    zas = crepitar(0.35, 2500 * np.exp(-t_(0.35) / 0.06), curva(n_(0.35), [(0, 4000), (1, 1500)]), 1.0)
    hipo = zumbido_solar(0.5, curva(n_(0.5), [(0, 150 + 10 * i), (1, 110)]), 0.7, 6.0, 0.2) * caida(0.5, 0.12, 0.005)
    _ = reverb(mezclar(pico(toc, 1.0), pico(zas, 0.35), pico(hipo, 0.45), pico(rajar_roca(5, 0.03), 0.4)), 0.22, 1.5)

for i in range(2):
    d = 3.0
    n = n_(d)
    t = t_(d)
    destello = pa(ruido(0.4), 1500) * caida(0.4, 0.06, 0.002)
    cae = zumbido_solar(d, curva(n, [(0, 220 - 20 * i), (0.4, 80), (1, 40)]), curva(n, [(0, 1.0), (1, 0.1)]), 8.0, 0.5) * np.exp(-t / 0.6)
    zas = crepitar(0.8, 3000 * np.exp(-t_(0.8) / 0.12), curva(n_(0.8), [(0, 5000), (1, 1200)]), 1.0)
    piedra = mezclar(pico(golpe_tierra(1.0, 1.4, 1.0, 2.5), 1.0), pico(rodar(1.4, 12, 5), 0.4))
    _ = reverb(mezclar(pico(destello, 0.5), pico(cae, 0.7), pico(zas, 0.4), pico(piedra, 0.75),
                       pico(destellos(1.0, 200 * np.exp(-t_(1.0) / 0.25)), 0.15)), 0.3, 2.4)

# ======================================================================
#  LA CARGA DEL SOL (15 s): el sol se hincha. El zumbido sube una octava
#  (fa grave a fa), se abre, el pulso se acelera (de uno a nueve por
#  segundo), el fuego ruge cada vez mas, las brasas se amontonan, tonos
#  brillantes suben uno tras otro cada vez mas seguidos y al final todo
#  esta en lo mas alto.
# ======================================================================
d = 15.0
n = n_(d)
t = t_(d)
x = t / d
f = 43.65 * 2 ** (x ** 1.5)
hum = zumbido_solar(d, f, 0.15 + 0.85 * x ** 1.2, 0.9 + 8.0 * x ** 2, 0.6)
env = (0.22 + 0.78 * x ** 1.15) * paso(t / 1.5)
arde = llama(d, 1.0, 0.5 + 1.1 * x, 13.0, 0.6 + 2.5 * x) * (0.15 + 0.85 * x ** 1.4) * paso(t / 2.0)
brasas = chasquidos(d, 10 + 500 * x ** 2.2)
tonos = np.zeros(n + n_(3.0))
s = 1.0
while s < d - 0.6:
    k = s / d
    dur_ = 2.2 - 1.2 * k
    tn = tono_sube(dur_, 110 * 2 ** (2 * k), 440 * 2 ** (2 * k), 3, 0.3 + 0.6 * k) * campana_env(dur_, 1.0) * (0.3 + 0.7 * k)
    i = n_(s)
    tonos[i:i + len(tn)] += tn
    s += 2.4 - 1.9 * k
tonos = tonos[:n] * ventana(d, 0.5, 0.2)
sube = filtro_mov(ruido(d, 'rosa'), 200 + 3500 * x ** 2, 'low', 0.8) * x ** 2
carga = mezclar(pico(hum * env, 1.0), pico(arde, 0.55), pico(brasas, 0.2), pico(tonos, 0.18), pico(sube, 0.25))
# el batido de las dos voces del sol hace olas lentas de volumen: se nivela
# (media de 1,5 s) para que la subida sea pareja y siga la curva de `env`
nivel = np.sqrt(signal.sosfiltfilt(signal.butter(1, 1 / 1.5, fs=SR, output='sos'), carga ** 2).clip(1e-12, None))
carga = carga / nivel * env * (0.6 + 0.4 * x)
carga *= ventana(d, 0.05, 0.12)
guardar('carga', reverb(carga, 0.25, 2.0)[:n], limite=0.6)

# SUPERNOVA: la carga falla y el sol revienta: el mayor estallido, el
# fogonazo, la bola de fuego que tarda en cerrarse, la lava que llueve, el
# zumbido que cae y un retumbo largo que rueda por todo el altar.
d = 8.0
n = n_(d)
t = t_(d)
golpe = saturar(boom(58, 15, 0.95, d), 3.0)
fogonazo = pa(ruido(0.3), 2000) * caida(0.3, 0.05, 0.0005)
bola = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 9000), (0.02, 6000), (0.12, 1600), (0.45, 450), (1, 160)]), 'low', 0.8)
bola *= np.interp(t, [0, 0.01, 0.6, 2.5, d], [0, 1, 0.7, 0.3, 0]) ** 1.2
grande = explosion(2.0, 4.0, 1.5, 1.5, 0.8, 1.0)
arde = llama(d, 1.0, curva(n, [(0, 1.5), (1, 0.4)]), 7.0) * np.exp(-t / 2.4) * paso(t / 0.2)
rueda = retumbo(d, 120, 0.9, 0.55, 0.6) * np.interp(t, [0, 0.3, 1.5, 4.5, d], [0, 1, 0.8, 0.35, 0])
cae = zumbido_solar(4.0, curva(n_(4.0), [(0, 87.3), (1, 30)]), curva(n_(4.0), [(0, 1.0), (1, 0.0)]), 3.0) * np.exp(-t_(4.0) / 1.0)
guardar('supernova', reverb(mezclar(pico(golpe, 0.9), pico(fogonazo, 0.5), pico(bola, 0.9), pico(grande, 0.8), pico(arde, 0.35),
                                    pico(rueda, 0.55), pico(cae, 0.3)), 0.35, 3.5, 4500), limite=0.4)

# EL SOL SE APAGA: los jugadores aguantaron. El zumbido cae y se le corta a
# tirones, el fuego chisporrotea y se ahoga, el vapor sisea al enfriarse y
# la armadura gime por dentro.
d = 4.0
n = n_(d)
t = t_(d)
tiron = np.clip(0.5 + 0.5 * np.tanh(4 * (suave(n, 9) + 1.3 - 2.6 * t / d)), 0, 1)
tiron = signal.sosfilt(signal.butter(1, 60, fs=SR, output='sos'), tiron)
cae = zumbido_solar(d, curva(n, [(0, 87.3), (0.5, 55), (1, 30)]), curva(n, [(0, 0.8), (1, 0.0)]), curva(n, [(0, 9), (1, 1)]), 0.6)
cae *= tiron * np.exp(-t / 1.4)
chisporrotea = chasquidos(d, 450 * np.exp(-t / 0.9)) + 0.5 * llama(d, 0.6, 0.6) * tiron * np.exp(-t / 1.0)
vapor = siseo(d, 2000, 8000) * np.interp(t, [0, 0.4, 2.0, d], [0, 1, 0.6, 0])
gime = chirriar(2.6, 160, (12, 30), 25, velocidad=curva(n_(2.6), [(0, 0.6), (0.5, 1.0), (1, 0.3)]), peso=1.0) * campana_env(2.6, 1.0)
soplo = ignicion(0.6, 0.5, 900, 50)[::-1] * 0.6
guardar('sol_apaga', reverb(mezclar(pico(cae, 0.9), pico(chisporrotea, 0.4), pico(vapor, 0.18), en(0.9, pico(gime, 0.5)),
                                    en(3.0, pico(soplo, 0.3))), 0.3, 2.4), limite=0.6)

# ======================================================================
#  OFRENDA AL SOL: un rayo de su sol se fija en un jugador (un tono grave y
#  otro a un tritono que suben juntos, y un 'clic' de cristal al fijarse);
#  lo agarra (los guanteletes se cierran con dos golpes de acero y el aire
#  que sube); cada tecla buena (una campanita corta y limpia: el juego le
#  cambia el tono); la mala (un golpe disonante y aspero); y el jugador que
#  se suelta (un estallido de luz).
# ======================================================================
for i in range(2):
    d = 2.0
    n = n_(d)
    t = t_(d)
    a = tono_sube(d, 196 * (1 + 0.04 * i), 392 * (1 + 0.04 * i), 3, 0.5, 12.0, 1.6)
    b = tono_sube(d, 277.2 * (1 + 0.04 * i), 554.4 * (1 + 0.04 * i), 3, 0.5, 12.0, 1.6)
    tiembla = 1 + 0.3 * np.sin(2 * np.pi * np.cumsum(3 + 9 * (t / d) ** 2) / SR)
    zumba = zumbido_solar(d, 55, 0.4, 2.0, 0.3)
    fija = en(d - 0.25, mezclar(pico(campana(1760.0, 0.3), 1.0), pico(metal(3520.0, None, 0.06, BARRA[:2], 1.0), 0.5)))
    capas = mezclar(pico(mezclar(a, b) * tiembla * rampa(d, 1.5, 0.1, 1.0) * ventana(d, 0.3, 0.25), 0.7), pico(zumba * ventana(d, 0.4, 0.3), 0.45),
                    pico(fija, 0.4))
    guardar('ofrenda_marca', reverb(capas, 0.28, 1.8), i + 1, techo=-18.0)

d = 1.6
n = n_(d)
cierra = mezclar(en(0.0, clang(210, 0.3, 1.0, 1.0)), en(0.13, clang(240, 0.28, 0.9, 1.0)))
dedos = chirriar(0.35, 600, (60, 140), 40) * campana_env(0.35, 1.0)
sube = pasada(1.2, 250, 2600, 1.4, 0.1)
guardar('ofrenda_agarra', reverb(mezclar(pico(dedos, 0.3), en(0.05, pico(cierra, 1.0)), en(0.35, pico(sube, 0.7))), 0.22, 1.6),
        limite=0.6)

d = 0.32
t = t_(d)
ding = mezclar(pico(np.sin(2 * np.pi * 1046.5 * t) * np.exp(-t / 0.11) + 0.22 * np.sin(2 * np.pi * 2093.0 * t + 0.4) * np.exp(-t / 0.06)
                    + 0.07 * np.sin(2 * np.pi * 3139.5 * t + 1.1) * np.exp(-t / 0.03), 1.0),
               pico(pb(ruido(0.004), 6000) * caida(0.004, 0.0008, 0.0001), 0.15))
ding *= paso(t / 0.003)
guardar('ofrenda_tecla', reverb(ding, 0.15, 0.6, 9000), techo=-21.0)

d = 0.7
t = t_(d)
duro = np.zeros(n_(d))
for fz in (146.8, 155.6, 207.7, 220.0):
    fase = 2 * np.pi * fz * (1 + 0.004 * rng.standard_normal()) * t
    duro += np.sign(np.sin(fase)) * 0.6 + np.sign(np.sin(1.003 * fase)) * 0.4
duro = pb(duro, 3500) * np.exp(-t / 0.18) * paso(t / 0.003)
golpe = clang(180, 0.25, 1.0, 1.0)
guardar('ofrenda_fallo', reverb(mezclar(pico(saturar(duro, 3.0), 0.8), pico(golpe, 0.7), pico(boom(90, 45, 0.08), 0.5)), 0.2, 1.2),
        limite=0.6, techo=-16.0)

d = 2.2
n = n_(d)
t = t_(d)
fogonazo = pa(ruido(d), 1200) * caida(d, 0.15, 0.003)
acorde = mezclar(*[en(0.03 * k, tono_sube(1.6, hz(m) * 0.94, hz(m), 2, 0.5) * caida(1.6, 0.5, 0.01)) for k, m in
                   enumerate((midi('F5'), midi('A5'), midi('C6'), midi('F6')))])
chispas = destellos(1.4, 300 * np.exp(-t_(1.4) / 0.3), 3000, 9000)
sube = pasada(0.9, 400, 3500, 1.4, 0.15)
oro = en(0.05, campana(698.5, 1.4))
guardar('ofrenda_libre', reverb(mezclar(pico(fogonazo, 0.4), pico(acorde, 0.6), pico(chispas, 0.25), pico(sube, 0.45), pico(oro, 0.4)),
                                0.3, 2.0), limite=0.6)

# ======================================================================
#  DIOS DE LA GUERRA: llamas carmesi prenden a su alrededor (un anillo de
#  bocanadas, un fuego grave y oscuro que ruge) y ruge hondo; los sellos
#  carmesi de las zonas (una campana grave a un tritono, el zumbido hondo y
#  el fuego que parpadea); y cada explosion de la cadena.
# ======================================================================
d = 4.6
n = n_(d)
t = t_(d)
anillo = mezclar(*[en(0.07 * k + rng.uniform(0, 0.03), ignicion(0.9, rng.uniform(0.6, 1.0), 1800, 45)) for k in range(7)])
oscuro = llama(d, 1.2, 0.55, 6.0, 0.8, 1.6) * np.interp(t, [0, 0.4, 3.6, d], [0, 1, 0.9, 0])
voz = en(0.6, rugido(3.4, 56, 94, escala=0.7, pecho=1.4, yelmo_=0.6, cola=2.4))
tambor = mezclar(pico(saturar(boom(52, 24, 0.5), 2.5), 1.0), pico(retumbo(2.0, 90) * caida(2.0, 0.6), 0.6))
guardar('dios', mezclar(pico(reverb(mezclar(pico(anillo, 0.8), pico(oscuro, 0.7), pico(tambor, 0.6)), 0.3, 2.4, 5000), 0.8),
                        pico(voz, 1.0)), limite=0.5)

for i in range(2):
    d = 1.6
    t = t_(d)
    sello = mezclar(pico(campana(196.0 * (1 + 0.05 * i), 1.2), 1.0), en(0.02, pico(campana(277.2 * (1 + 0.05 * i), 1.0), 0.7)))
    hondo = zumbido_solar(d, 41.2 * (1 + 0.05 * i), 0.35, 1.5, 0.6) * ventana(d, 0.1, 0.8)
    parpadea = llama(d, 1.0, 0.6, 12.0, 1.2, 1.2) * ventana(d, 0.05, 0.8)
    guardar('dios_aviso', reverb(mezclar(pico(sello, 0.8), pico(hondo, 0.55), pico(parpadea, 0.35)), 0.3, 2.0), i + 1, limite=0.6)

for i in range(3):
    guardar('dios_explosion', reverb(explosion(1.15 + 0.1 * i, 2.6, 0.4, 0.8, 1.0 + 0.08 * (i - 1), 0.5), 0.28, 2.2, 5500), i + 1,
            limite=0.45)

# GRITO DE GUERRA: corto, mas agudo y abierto, con una llamarada.
for i in range(2):
    d = 2.2
    voz = rugido(1.9, 92 + 6 * i, 150 + 8 * i, 1.15, 1.6, 0.7, 0.8, 1.6, 0.25, 0.14,
                 contorno=[(0, 0.7), (0.12, 1.0), (0.5, 0.98), (0.8, 0.85), (1, 0.65)])
    llamarada = ignicion(1.2, 1.0, 4000, 60)
    guardar('grito', mezclar(pico(voz, 1.0), en(0.05, pico(reverb(llamarada, 0.25, 1.6), 0.45))), i + 1, limite=0.55)

# FURIA: prende el fuego azul: mas caliente, mas agudo y mas rapido. Un
# soplete (el chorro de gas que ruge con un siseo fuerte), la bocanada al
# prender y un rugido.
d = 3.6
n = n_(d)
t = t_(d)
prende = ignicion(1.4, 1.0, 7000, 70, aspira=0.3)
azul = llama(d, 1.4, 2.4, 18.0, 1.6, 0.6) * np.interp(t, [0, 0.4, 2.8, d], [0, 1, 0.85, 0])
soplete = bp(ruido(d), 1200, 7000) * (0.8 + 0.2 * suave(n, 25)) * np.interp(t, [0, 0.35, 2.8, d], [0, 1, 0.8, 0])
voz = en(0.25, rugido(3.0, 82, 136, cola=1.8, escala=0.8))
guardar('furia', mezclar(pico(reverb(mezclar(pico(prende, 0.7), pico(azul, 0.8), pico(soplete, 0.25)), 0.25, 2.0), 0.75),
                         pico(voz, 1.0)), limite=0.5)

# ======================================================================
#  ATURDIDO: el yelmo le zumba como una campana (dos parciales que baten y
#  un pitido fino, como en los oidos), la armadura se desploma a medias y
#  se queja hondo, sin fuerza.
# ======================================================================
d = 4.2
n = n_(d)
t = t_(d)
casco = (np.sin(2 * np.pi * 1180 * t) + 0.8 * np.sin(2 * np.pi * 1187.5 * t + 1.0) + 0.3 * np.sin(2 * np.pi * 2530 * t)) * np.exp(-t / 1.6)
casco *= 1 + 0.35 * np.sin(2 * np.pi * 2.3 * t)
pitido = np.sin(2 * np.pi * 3400 * t) * np.interp(t, [0, 0.3, 2.5, d], [0, 1, 0.5, 0])
cae = mezclar(pico(clang(150, 0.5, 1.0, 1.0), 1.0), en(0.25, pico(clang(210, 0.35, 0.7, 1.0), 0.6)),
              pico(placas(1.2, 120 * np.exp(-t_(1.2) / 0.4)), 0.3))
queja = garganta(curva(n_(2.6), [(0, 64), (0.4, 58), (1, 46)]), 2.6, formantes_voz(H_U, H_O, 0.25, 0.8), 0.6, 0.5, 0.05, 0.6, 3000,
                 fritura=0.35, pecho=0.5) * ventana(2.6, 0.2, 1.4)
debil = llama(d, 0.5, 0.5, 5.0, 0.5) * np.exp(-t / 2.0)
guardar('aturdido', reverb(mezclar(pico(cae, 0.7), pico(casco, 0.4), pico(pitido, 0.05), en(0.4, pico(yelmo(queja, 0.6), 0.6)),
                                   pico(debil, 0.2)), 0.3, 2.2), limite=0.55)

# TAMBALEO: cambia de fase. La armadura se abre (el acero que se raja con un
# chasquido y la placa que suena), la lava revienta por la grieta y ruge.
for i in range(2):
    raja = mezclar(*[en(s, metal(rng.uniform(1500, 4000), None, 0.05, PLACA[:4], 1.0)) for s in np.sort(rng.uniform(0, 0.15, 12))])
    abre = clang(160 - 10 * i, 0.9, 1.0, 1.0)
    revienta = mezclar(pico(ignicion(1.6, 1.0, 3500, 50), 1.0), en(0.1, pico(lava_charco(2.0, 18.0, 1.4) * caida(2.0, 0.7), 0.6)),
                       pico(mezclar(*[en(s, salpicadura()) for s in rng.uniform(0.2, 1.2, 4)]), 0.5))
    golpe = reverb(mezclar(pico(raja, 0.5), pico(abre, 0.8), en(0.05, pico(revienta, 0.9))), 0.28, 2.0)
    guardar('tambaleo', mezclar(pico(golpe, 0.85), en(0.45, pico(rugido(2.8, 72 - 4 * i, 114 - 6 * i, cola=2.0), 1.0))), i + 1,
            limite=0.55)

# ======================================================================
#  LIBERACION: el fuego se calma (se apaga hacia los graves, las brasas se
#  espacian) y se vuelve una ola dorada y templada: un acorde mayor del
#  coro que se hincha y se va, una campana de oro y un suspiro por el yelmo.
#  Y DISOLVER: se deshace en brasas y luz que suben.
# ======================================================================
d = 6.4
n = n_(d)
t = t_(d)
calma = llama(d, 0.8, curva(n, [(0, 1.0), (0.4, 0.3), (1, 0.2)]), 6.0, 0.8) * np.interp(t, [0, 0.2, 2.8, 4.0, d], [0.5, 1, 0.3, 0.05, 0])
dorado = coro(4.6, [midi(x) for x in ('F3', 'C4', 'F4', 'A4', 'C5', 'G5')], 'o', 3) * curva(n_(4.6), [(0, 0), (0.45, 1.0), (0.7, 0.75), (1, 0)])
oro = campana(349.2, 2.5)
suspiro = respiro(2.4, True, 48.0, 0.3)
luz = destellos(3.0, 25, 2500, 7000, (0.1, 0.4))
guardar('liberacion', reverb(mezclar(pico(calma, 0.4), en(1.2, pico(dorado, 0.6)), en(1.6, pico(oro, 0.35)), en(3.0, pico(suspiro, 0.4)),
                                     en(1.8, pico(luz, 0.1))), 0.4, 3.0, 6500))

d = 3.6
n = n_(d)
t = t_(d)
brasas = pa(chasquidos(d, 180 * np.exp(-t / 1.1) + 8), 1500)
luz = mezclar(*[en(s, tono_sube(1.6, f, f * 2, 2, 0.3) * campana_env(1.6, 1.0)) for s, f in ((0.1, 523.3), (0.6, 698.5), (1.2, 880.0))])
sube = pasada(2.4, 300, 2200, 1.2, 0.05)
apaga = llama(d, 0.5, 0.5) * np.exp(-t / 0.8)
guardar('disolver', reverb(mezclar(pico(brasas, 0.4), pico(luz, 0.25), pico(sube, 0.35), pico(apaga, 0.3)), 0.35, 2.4, 6000))


# ======================================================================
#  LA MELODIA DE LAS TROMPETAS (24 s exactos, 4 voces sueltas). Con su
#  propia semilla: tocar los sonidos de arriba no cambia las trompetas.
#  Un coral en fa menor a 80 negras: un toque de fanfarria (corchea con
#  puntillo y semicorchea), el coral que crece (i - bVI - V, i - bVII,
#  bVI - bII - V, iv - i, bII - bVI - V7) y el final en lo mas alto, con
#  el reb (b9) de la dominante, que se resuelve en fa menor.
#    1 melodia (trompeta 1)    2 contracanto (trompeta 2)
#    3 armonia (trompeta 3)    4 trompeta baja
# ======================================================================
rng = np.random.default_rng(20261021)
UNIDAD = 60.0 / 80.0
MELODIA = (
    ("mf C5:1.5 C5:0.5 F5:1.5 C5:0.5 | F5:1 Db5:1 E5:2 | "
     "F5:1.5 G5:0.5 Ab5:1 G5:1 | F5:1 Ab5:1 Gb5:1 E5:1 | "
     "f F5:2 C5:1 Db5:1 | Bb5:2 Ab5:1 G5:1 | "
     "ff C6:1> Db6:1 Bb5:1 G5:0.5 E5:0.5 | F5:3< r:1", 1.0, 1.0),
    ("mf F4:1.5 F4:0.5 C5:1 Bb4:0.5 Ab4:0.5 | Ab4:1 F4:1 G4:1 C5:1 | "
     "C5:1 Ab4:0.5 C5:0.5 Bb4:1 Eb5:1 | Db5:1 C5:1 Db5:1 C5:1 | "
     "f Db5:1 Bb4:1 C5:1 Ab4:1 | Db5:1.5 Eb5:0.5 F5:1 E5:1 | "
     "ff Ab5:1> F5:1 Gb5:1 E5:0.5 Db5:0.5 | C5:3< r:1", 0.97, 0.95),
    ("mf Ab4:1.5 Ab4:0.5 C5:1.5 Ab4:0.5 | Ab4:2 G4:2 | "
     "Ab4:2 G4:2 | Ab4:1 F4:1 Bb4:1 G4:1 | "
     "f Bb4:2 Ab4:2 | Gb4:2 F4:1 E4:1 | "
     "ff F4:1> F4:1 Db5:1 C5:0.5 Bb4:0.5 | Ab4:3< r:1", 0.92, 0.9),
    ("mf F2:1.5 F2:0.5 F2:1 C3:1 | Db3:2 C3:2 | "
     "F2:2 Eb3:2 | Db3:2 Gb2:1 C3:1 | "
     "f Bb2:2 F2:2 | Gb2:2 Db3:1 C3:1 | "
     "ff Ab2:1> Bb2:1 Gb2:1 C3:1 | F2:3< r:1", 0.72, 0.8),
)
LARGO_MELODIA = 24.0
voces_mel = []
for texto, voz, brillo in MELODIA:
    notas = leer_linea(texto, UNIDAD)
    assert notas[-1][0] + notas[-1][1] <= LARGO_MELODIA - 0.5
    x = np.zeros(n_(LARGO_MELODIA) + n_(1.0))
    for t0, dd, m, v, art in notas:
        s = nota_metal(m, dd * 0.97, v, art, voz, brillo)
        i = n_(max(0.0, t0 + rng.normal(0, 0.005)))
        x[i:i + len(s)] += s[:len(x) - i]
    x = reverb(x, 0.3, 3.0, 7500)[:n_(LARGO_MELODIA)]
    r = n_(0.5)
    x[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    voces_mel.append(x)
# cada estatua es una fuente suelta: cada voz con su pico en -3 dBFS, la
# melodia delante y la armonia un pelo detras (la sonoridad ponderada A
# no vale aqui: subiria la trompeta baja hasta tapar a las demas)
RECORTE = (0.0, -0.5, -1.0, -0.5)
for k, x in enumerate(voces_mel):
    x = pa(x, 25)
    guardar('melodia_%d' % (k + 1), x * (ALTO * 10 ** (RECORTE[k] / 20) / np.max(np.abs(x))), exacto=LARGO_MELODIA, normalizar=False)
    STREAM.add('melodia_%d' % (k + 1))

# ======================================================================
#  LOS ATAQUES DE OCTUBRE (08-10-2026): Espada del Fuego, Furia Infernal y
#  Mar de Llamas. Con su propia semilla y al final: no tocan los de arriba.
# ======================================================================
rng = np.random.default_rng(20261008)

# EMBESTIDA: sale disparado. El pie que empuja el suelo, el aire que se abre
# (una pasada larga que sube y se va), el fuego de la hoja que ruge al pasar
# y la armadura que traquetea con la carrera.
for i in range(2):
    d = 2.4
    n = n_(d)
    t = t_(d)
    empuja = golpe_tierra(1.2, 0.8, 0.6, 1.6)
    aire = pasada(1.6, 900 + 100 * i, 4200, 1.6, 0.35)
    ruge = llama(d, 1.2, curva(n, [(0, 0.6), (0.2, 1.6), (1, 0.5)]), 14.0, 1.4) * np.interp(t, [0, 0.08, 0.7, d], [0, 1, 0.5, 0])
    traqueteo = placas(1.2, 140 * np.exp(-t_(1.2) / 0.5), 1.0)
    voz = en(0.02, quejido(0.6, 96 + 8 * i, 1.0))
    guardar('embestida', reverb(mezclar(pico(empuja, 0.8), en(0.03, pico(aire, 0.85)), en(0.05, pico(ruge, 0.6)),
                                        en(0.05, pico(traqueteo, 0.25)), pico(voz, 0.45)), 0.25, 1.8), i + 1, limite=0.5)

# EL CAMINO DE LLAMAS: prende detras de el, a golpes seguidos (bocanadas que
# se van alejando), y se queda chisporroteando.
d = 2.8
t = t_(d)
prenden = mezclar(*[en(0.06 * k, ignicion(0.8, 1.0 - 0.06 * k, 2600, 50)) for k in range(9)])
arde = llama(d, 1.0, 0.8, 10.0, 1.6) * np.interp(t, [0, 0.3, 1.5, d], [0, 1, 0.7, 0])
brasas = chasquidos(d, 300 * np.exp(-t / 1.2) + 30)
guardar('camino', reverb(mezclar(pico(prenden, 0.9), pico(arde, 0.55), pico(brasas, 0.25)), 0.25, 1.8), limite=0.55)

# FURIA INFERNAL. El salto: el esfuerzo por el yelmo, el suelo que cede bajo
# su peso, el aire que se abre hacia arriba y las placas.
for i in range(2):
    d = 1.6
    esfuerzo = respiro(0.7, True, 58 + 6 * i, 0.6, 1.2)
    suelo = golpe_tierra(1.0, 0.7, 0.8, 1.2)
    sube = pasada(1.1, 700, 2600 + 300 * i, 1.4, 0.3)
    chapa = placas(0.8, 220 * np.exp(-t_(0.8) / 0.25), 1.0)
    guardar('infernal_salto', reverb(mezclar(pico(esfuerzo, 0.55), pico(suelo, 0.75), en(0.05, pico(sube, 0.7)),
                                             pico(chapa, 0.3)), 0.25, 1.8), i + 1, limite=0.5)

# La caida: dieciseis bloques de acero contra la piedra con la espada por
# delante. El golpe mas hondo, la hoja que se clava (una barra que vibra), la
# roca que revienta en abanico y la lava que ya asoma.
d = 3.8
t = t_(d)
golpe = golpe_tierra(2.8, 2.0, 1.6, 3.4)
hondo = saturar(boom(46, 18, 0.7, d), 2.6)
hoja = metal(118.0, 2.8, 1.2, BARRA, 0.9, 0.003, 0.5)
raja = mezclar(*[en(s, rajar_roca(int(rng.integers(10, 18)), 0.08, 1.1, 0.9)) for s in np.sort(rng.uniform(0.04, 0.9, 7))])
asoma = en(0.5, lava_charco(2.8, 10.0, 0.8) * np.interp(t_(2.8), [0, 0.4, 2.0, 2.8], [0, 1, 0.7, 0]))
guardar('infernal_golpe', reverb(mezclar(pico(golpe, 1.0), pico(hondo, 0.7), en(0.02, pico(hoja, 0.3)), en(0.05, pico(raja, 0.55)),
                                         pico(asoma, 0.3)), 0.3, 2.8, 4800), limite=0.42)

# LA GRIETA: la roca se va rajando a tirones (de cerca a lejos), cruje, y por
# la raja sube el siseo del calor y el borboteo de la lava.
for i in range(3):
    d = 2.4
    t = t_(d)
    raja = mezclar(*[en(s, rajar_roca(int(rng.integers(6, 12)), 0.05, 1.0, 0.9 - 0.1 * i)) for s in np.sort(rng.uniform(0.0, 1.1, 6))])
    cruje = crepitar(1.8, 700 * np.exp(-t_(1.8) / 0.6), curva(n_(1.8), [(0, 3000), (1, 900)]), 1.2)
    calor = en(0.3, siseo(2.0, 2000, 8000) * np.interp(t_(2.0), [0, 0.5, 1.4, 2.0], [0, 1, 0.6, 0]))
    borbotea = en(0.5, lava_charco(1.9, 8.0, 0.4) * np.interp(t_(1.9), [0, 0.4, 1.2, 1.9], [0, 1, 0.6, 0]))
    guardar('grieta', reverb(mezclar(pico(raja, 0.9), pico(cruje, 0.35), pico(calor, 0.15), pico(borbotea, 0.35)), 0.25, 2.0),
            i + 1, limite=0.55)

# EL GEISER: la grieta escupe: la bocanada del fuego que prende, el chorro de
# lava que sube y salpica, la lluvia de gotas y el borboteo que queda.
for i in range(3):
    d = 2.0
    t = t_(d)
    prende = ignicion(1.1, 1.0, 3200 + 300 * i, 50 - 4 * i)
    chorro = filtro_mov(llama(1.3, 1.2, 1.6, 16.0, 1.2), curva(n_(1.3), [(0, 500), (0.15, 3200), (1, 700)]), 'band', 0.8)
    chorro *= np.interp(t_(1.3), [0, 0.05, 0.6, 1.3], [0, 1, 0.5, 0])
    salpica = en(0.08, salpicadura(1.0 + 0.2 * i))
    queda = en(0.4, lava_charco(1.6, 9.0, 0.6) * np.interp(t_(1.6), [0, 0.3, 1.6], [0, 1, 0]))
    guardar('geiser', reverb(mezclar(pico(prende, 0.8), pico(chorro, 0.75), pico(salpica, 0.5), pico(queda, 0.3)), 0.28, 2.0),
            i + 1, limite=0.5)

# LA GRIETA REVIENTA: arranca la espada y todo estalla: la mayor explosion de
# lava, la piedra que sale volando y el retumbo que rueda por el altar.
for i in range(2):
    d = 4.6
    t = t_(d)
    grande = explosion(1.9 + 0.1 * i, 4.2, 1.6, 1.3, 0.85 - 0.06 * i, 1.2)
    arranca = metal(150.0 + 12 * i, 1.2, 0.5, BARRA, 1.0, 0.003, 0.7)
    rueda = retumbo(d, 110, 1.0, 0.5, 0.5) * np.interp(t, [0, 0.3, 1.6, d], [0, 1, 0.6, 0])
    guardar('infernal_explota', reverb(mezclar(pico(arranca, 0.3), en(0.04, pico(grande, 1.0)), en(0.06, pico(rueda, 0.45))),
                                       0.32, 3.0, 4800), i + 1, limite=0.42)

# MAR DE LLAMAS: hunde la espada y el suelo de toda la arena se raja: un
# retumbo largo que viene de lejos, grietas por todas partes que se alejan,
# y el fuego que empieza a rugir por debajo.
d = 6.0
n = n_(d)
t = t_(d)
golpe = golpe_tierra(2.4, 1.8, 1.4, 3.0)
viene = retumbo(d, 95, 0.8, 0.6, 0.5) * np.interp(t, [0, 0.2, 2.5, d], [0, 1, 0.8, 0])
grietas = mezclar(*[en(s, rajar_roca(int(rng.integers(8, 16)), 0.06, 1.0 - 0.5 * s / d, 0.8)) for s in np.sort(rng.uniform(0.1, 4.5, 16))])
ruge = llama(d, 1.0, curva(n, [(0, 0.3), (0.5, 1.2), (1, 0.8)]), 8.0, 1.4, 1.6) * np.interp(t, [0, 0.8, 3.0, d], [0, 0.6, 1, 0])
guardar('mar', reverb(mezclar(pico(golpe, 1.0), pico(viene, 0.6), pico(grietas, 0.55), pico(ruge, 0.5)), 0.32, 3.0, 4800), limite=0.45)

largos = {len(z) for nombre, z in GUARDADOS if nombre.startswith('melodia_')}
assert len(largos) == 1, f'las melodias no miden lo mismo: {largos}'

# ----------------------------------------------------------------------
#  sounds.json: los eventos novilis.* con sus variantes y subtitulo (las
#  melodias, en streaming: son largas y suenan cuatro a la vez)
# ----------------------------------------------------------------------
SUBTITULOS = {
    'ambiente': ('Novilis respira tras el yelmo', 'Novilis breathes behind his helm'),
    'paso': ('Pisadas de Novilis', 'Novilis stomps'),
    'herido': ('Novilis recibe el golpe', 'Novilis is hit'),
    'inmune': ('El golpe rebota en la armadura', 'The blow glances off the armor'),
    'rugido': ('Novilis ruge', 'Novilis roars'),
    'despertar': ('Novilis despierta', 'Novilis awakens'),
    'tajo': ('El mandoble de fuego corta el aire', 'The flaming greatsword swings'),
    'tajo_fuego': ('Una media luna de fuego vuela', 'A fire crescent flies'),
    'castigo_alza': ('Novilis alza la espada al sol', 'Novilis raises his sword to the sun'),
    'castigo_aviso': ('Aparece un sello solar', 'A solar sigil appears'),
    'castigo_rayo': ('Cae un rayo de fuego solar', 'A ray of solar fire strikes'),
    'castigo_clava': ('Novilis clava la espada', 'Novilis drives his sword into the ground'),
    'onda': ('Un anillo de fuego se expande', 'A ring of fire spreads'),
    'sol_forma': ('Un sol se forma en su mano', 'A sun forms in his hand'),
    'sol_lanza': ('Novilis lanza un sol', 'Novilis hurls a sun'),
    'sol_explota': ('Revienta un sol', 'A sun explodes'),
    'lava': ('Burbujea la lava', 'Lava bubbles'),
    'estatuas': ('Se alzan las estatuas de los ángeles', 'The angel statues rise'),
    'melodia_1': ('Tocan las trompetas de los ángeles', 'Angelic trumpets play'),
    'melodia_2': ('Tocan las trompetas de los ángeles', 'Angelic trumpets play'),
    'melodia_3': ('Tocan las trompetas de los ángeles', 'Angelic trumpets play'),
    'melodia_4': ('Tocan las trompetas de los ángeles', 'Angelic trumpets play'),
    'estatua_golpe': ('Cruje una estatua', 'A statue cracks'),
    'estatua_rota': ('Se rompe una estatua', 'A statue shatters'),
    'carga': ('Novilis carga su fuego', 'Novilis gathers his fire'),
    'supernova': ('Estalla una supernova', 'A supernova explodes'),
    'sol_apaga': ('El sol se apaga', 'The sun fizzles out'),
    'ofrenda_marca': ('Un rayo de sol te marca', 'A sunbeam marks you'),
    'ofrenda_agarra': ('Novilis te agarra', 'Novilis grabs you'),
    'ofrenda_tecla': ('Tecla correcta', 'Correct key'),
    'ofrenda_fallo': ('Tecla fallida', 'Wrong key'),
    'ofrenda_libre': ('Te liberas', 'You break free'),
    'dios': ('Novilis se vuelve el Dios de la Guerra', 'Novilis becomes the God of War'),
    'dios_aviso': ('Aparecen sellos carmesí', 'Crimson sigils appear'),
    'dios_explosion': ('Estalla un sello carmesí', 'A crimson sigil explodes'),
    'grito': ('Novilis lanza un grito de guerra', 'Novilis lets out a war cry'),
    'furia': ('Novilis arde en fuego azul', 'Novilis burns with blue fire'),
    'aturdido': ('Novilis queda aturdido', 'Novilis is stunned'),
    'tambaleo': ('Novilis se tambalea', 'Novilis staggers'),
    'liberacion': ('Novilis queda libre', 'Novilis is freed'),
    'disolver': ('Novilis se deshace en brasas', 'Novilis dissolves into embers'),
    'embestida': ('Novilis embiste con la espada en llamas', 'Novilis charges with his flaming sword'),
    'camino': ('Arde un camino de llamas', 'A trail of flames burns'),
    'infernal_salto': ('Novilis salta', 'Novilis leaps'),
    'infernal_golpe': ('Novilis cae clavando la espada', 'Novilis lands, driving his sword down'),
    'grieta': ('El suelo se raja', 'The ground cracks'),
    'geiser': ('Brota lava de la grieta', 'Lava erupts from the crack'),
    'infernal_explota': ('Revienta la grieta', 'The crack explodes'),
    'mar': ('El suelo se raja en llamas', 'The ground cracks into flame'),
}
faltan = [ev for ev in EVENTOS if ev not in SUBTITULOS]
assert not faltan, f'eventos sin subtitulo: {faltan}'

ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for k in [k for k in datos if k.startswith('novilis.')]:
    del datos[k]
for ev, archivos in EVENTOS.items():
    sonidos = [collections.OrderedDict([('name', 'atalaya:novilis/' + a), ('stream', True)]) if ev in STREAM else 'atalaya:novilis/' + a
               for a in archivos]
    datos['novilis.' + ev] = {'subtitle': 'subtitles.atalaya.novilis.' + ev, 'sounds': sonidos}
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
        hoja.paste(Image.merge('RGB', (im, im.point(lambda v: int(v * 0.75)), im.point(lambda v: int(v * 0.45)))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9):.0f}dB',
                 fill=(220, 220, 220))
    hoja.save(sys.argv[2])
