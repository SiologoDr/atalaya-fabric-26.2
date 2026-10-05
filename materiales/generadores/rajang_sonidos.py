"""
Sonidos de Rajang, el Jaguar de Jade. Sintetizados desde cero: nada de
vanilla ni de bancos de sonido.

Rajang es un dientes de sable colosal tallado en jade y maldito (la
Maldicion de la Raiz) que pelea en la plaza de un templo de la selva. Todo
sale de la PIEDRA, la TIERRA y el JADE, modelados con su fisica:

  - TIERRA QUE RETUMBA: ruido marron muy filtrado cuya amplitud late lenta
    (las capas de roca que se mueven), con arenilla por encima.
  - PIEDRA QUE SE ARRASTRA: friccion de "pegarse y soltarse" (stick-slip).
    Cada suelta es un microgolpe que hace sonar los modos anchos de los
    bloques (el gemido grave de una puerta de templo) y la arena atrapada
    entre las caras raspa por encima.
  - ROCA QUE SE RAJA: una racha de microfracturas (chasquidos de 1 ms, de
    banda ancha) que hacen sonar un instante las bandas agudas de la piedra
    y el golpe grave de su masa.
  - GRAVA Y ESCOMBROS: cada piedra es un chasquido y un timbre corto, mas
    agudo cuanto mas pequena (f ~ 1/tamano); muchas pequenas y pocas grandes
    (ley de potencias). Lo que salta en un golpe vuelve a caer despues: la
    lluvia llega a su maximo cuando aterriza, no en el golpe.
  - GOLPES PESADOS: el golpe de presion grave que cae de tono, el cuerpo
    sordo, la roca que se raja, el suelo que retumba y los escombros.
  - CANTOS QUE RUEDAN: botes cada vez mas seguidos y mas flojos
    (coeficiente de restitucion).
  - PICOS QUE BROTAN: una barra empotrada que asoma: cuanto mas sale, mas
    larga queda libre y mas grave canta (f ~ 1/L^2), mientras roza la tierra.
  - GRIETAS QUE CORREN: chasquidos cada vez mas seguidos, fuertes y
    brillantes a medida que llegan (de cerca el aire se come menos agudos) y
    un Doppler que sube las bandas.

El JADE es piedra densa y dura que suena casi como vidrio (como las piedras
sonoras de jade): modos inarmonicos de barra libre (1 : 2,76 : 5,40 : 8,93),
cada uno partido en dos porque la talla no es simetrica (el batido le da el
brillo). Frotado canta como una copa: ruido por resonancias estrechisimas.
Asi suenan los GLIFOS y la MALDICION: un zumbido verde y hondo que late
contra si mismo, con un hilo de jade muy arriba. El FUEGO VERDE de los
fragmentos es combustion turbulenta que parpadea, con chasquidos.

La VOZ es la de un felino de ocho bloques: pulsos de garganta graves (60 a
110 Hz) con jitter, fritura, subarmonicos y tramos caoticos (los rugidos de
leon y de tigre los tienen), los formantes de un tracto larguisimo que se
abren de "o" a "a" y se cierran (el tono sube y cae), una segunda garganta
una octava abajo que le da el pecho, la piedra que muele dentro (pasada por
los mismos formantes: es una estatua viva) y el zumbido de la maldicion.

El espacio es la plaza de un templo en la selva: muros y escalinatas de
piedra que devuelven ecos cercanos y claros, y una selva alrededor que se
traga los agudos de la cola.

Escribe los .ogg (mono, para que se oigan en 3D) en
assets/atalaya/sounds/rajang/, sus eventos en sounds.json
(rajang.<evento>, subtitulo subtitles.atalaya.rajang.<evento>) y los textos
de los subtitulos en materiales/generadores/rajang_subtitulos.json.

Los de las mejoras de octubre de 2026 (embestida, tumba, furia, escalones y
pulso del totem) van al final con su propia semilla: se pueden generar sueltos,
sin tocar los demas, con rajang_mejoras_sonidos.py.

Uso: python rajang_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png]
"""
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator
import os, sys, json, collections

SR = 44100
RAIZ = sys.argv[1]
OUT = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/rajang')
os.makedirs(OUT, exist_ok=True)
for viejo in os.listdir(OUT):
    if viejo.endswith('.ogg'):
        os.remove(os.path.join(OUT, viejo))
rng = np.random.default_rng(20261005)
EVENTOS = collections.OrderedDict()
GUARDADOS = []


# ======================================================================
#  Utilidades (las mismas que los sonidos de Nerea y Aeralis)
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


# ---------------------------------------------------------------- reverb
_IRS = {}


def respuesta(cola, oscuro):
    """La plaza del templo: los muros, las escalinatas y la piramide devuelven
    ecos cercanos y claros (la piedra refleja casi todo), y la selva de
    alrededor se traga los agudos de la cola."""
    clave = (round(cola, 2), int(oscuro))
    if clave not in _IRS:
        t = t_(cola)
        r = np.random.default_rng(int(cola * 1000) + int(oscuro) + 7)
        x = r.standard_normal(len(t))
        h = (pb(x, 500) * np.exp(-6.9 * t / cola)
             + bp(x, 500, 3000) * np.exp(-6.9 * t / (cola * 0.55)) * 0.75
             + pa(x, 3000) * np.exp(-6.9 * t / (cola * 0.18)) * 0.35)
        h = pb(h, oscuro)
        a = n_(0.03)
        h[:a] *= np.linspace(0, 1, a) ** 2
        ref = np.sqrt(np.mean(h[:n_(0.12)] ** 2))
        # primeros ecos: las escalinatas, los muros de la plaza y la piramide
        for seg, g, claro in ((0.043, 0.75, 7000), (0.079, 0.6, 5500), (0.127, 0.45, 4500), (0.21, 0.3, 3000),
                              (0.37, 0.22, 2200)):
            if seg < cola * 0.8:
                i = n_(seg)
                eco = pb(r.standard_normal(n_(0.014)), claro) * np.exp(-t_(0.014) / 0.0035)
                h[i:i + len(eco)] += g * eco * ref * 7
        _IRS[clave] = h / np.sqrt(np.sum(h ** 2))
    return _IRS[clave]


def reverb(x, mezcla=0.25, cola=1.8, oscuro=6500):
    h = respuesta(cola, oscuro)
    mojado = signal.fftconvolve(x, h)
    seco = np.concatenate([x, np.zeros(len(h) - 1)])
    return (1 - mezcla) * seco + mezcla * mojado


# ======================================================================
#  TIERRA Y PIEDRA
# ======================================================================
def boom(f0=60, f1=26, tau=0.25, dur=None):
    """El golpe de presion: el suelo empujado de golpe, que cae de tono."""
    dur = dur or tau * 5
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) + 0.25 * np.sin(2 * fase)) * caida(dur, tau, 0.003)


def retumbo(dur, fc=120, lento=1.2, prof=0.45, grano=0.35):
    """Tierra que retumba: ruido marron muy filtrado cuya amplitud late lenta
    (las capas de roca que se mueven) y la arenilla que vibra encima."""
    n = n_(dur)
    am = np.exp(prof * suave(n, lento))
    bajo = pa(pb(ruido(dur, 'marron'), fc, 4), 28) * am
    medio = bp(ruido(dur, 'rosa'), fc * 1.3, fc * 6) * am * np.exp(0.5 * prof * suave(n, lento * 3))
    return mezclar(pico(bajo, 1.0), pico(medio, grano))


TAMANOS = np.geomspace(0.4, 30.0, 16)    # cm, de arenilla a cascote
_PIEDRAS = []


def _piedras():
    """Banco de piedras: un chasquido de contacto y unos modos irregulares
    que se apagan enseguida (la roca esta muy amortiguada). f ~ 1/tamano."""
    if not _PIEDRAS:
        for s in TAMANOS:
            clase = []
            for _ in range(6):
                f = min(11500.0, 4500.0 / s * rng.uniform(0.8, 1.25))
                tau = 0.0016 + 0.0013 * s
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
    """Lluvia de piedras (tasa por segundo, numero o curva) de tamanos entre
    tam[0] y tam[1] cm: muchas pequenas y pocas grandes, que suenan mas."""
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
    """Lo que salta al golpe: unas esquirlas que salen rozando el suelo al
    instante y el resto, que vuela y vuelve a caer: la lluvia es maxima a
    los `vuelo` segundos y se apaga."""
    t = t_(dur)
    x = t / vuelo
    tasa = 700 * fuerza * (salpica * np.exp(-t / 0.04) + x ** 1.5 * np.exp(1.5 * (1 - x)))
    return grava(dur, tasa, tam)


ROCA = ((92, 5.0, 1.0), (163, 6.0, 0.9), (281, 7.0, 0.75), (455, 8.0, 0.55), (742, 8.0, 0.4), (1210, 9.0, 0.28),
        (1960, 10.0, 0.18))


def moler(dur, peso=1.0, tasa=(16, 45), arena=1.0, velocidad=1.0):
    """Piedra que se arrastra sobre piedra: friccion de pegarse y soltarse.
    Cada suelta es un microgolpe que hace sonar los modos anchos de los
    bloques (un gemido ronco, mas grave cuanto mas `peso`) y la arena atrapada
    entre las caras raspa. `velocidad` (numero o curva) acelera el roce."""
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
    """Una roca que se parte: una racha de microfracturas (chasquidos de 1 ms
    de banda ancha) que hacen sonar un instante las bandas agudas de la
    piedra y el golpe grave de su masa."""
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


def canto(tam=15.0, fuerza=1.0, chinas=True):
    """Un canto de piedra que golpea el suelo: un 'toc' grave y opaco."""
    f = 4500.0 / tam * rng.uniform(0.85, 1.15)
    tau = 0.0016 + 0.0013 * tam
    d = min(0.6, 7 * tau + 0.03)
    parc = ((1, 1.0), (rng.uniform(1.4, 1.8), 0.7), (rng.uniform(2.1, 2.7), 0.45), (rng.uniform(3.2, 4.0), 0.25))
    capas = [pico(modos(f, d, parc, tau), 1.0),
             pico(pb(ruido(0.025), 1200) * caida(0.025, 0.004, 0.0005), 0.6),
             pico(boom(f * 0.55, f * 0.4, 0.03 + 0.002 * tam), 0.5)]
    if chinas:
        capas.append(pico(grava(0.3, 400 * np.exp(-t_(0.3) / 0.05), (0.4, 2.0)), 0.2))
    return fuerza * mezclar(*capas)


def rodar(dur, tam=15.0, botes=7, amp=1.0, intervalo=0.22):
    """Un canto que cae y rueda: botes cada vez mas seguidos y mas flojos."""
    out = np.zeros(n_(dur) + n_(0.7))
    s, a, iv = 0.0, 1.0, intervalo
    for _ in range(botes):
        if s >= dur:
            break
        c = canto(tam * rng.uniform(0.8, 1.2), a)
        i = n_(s)
        out[i:i + len(c)] += c[:len(out) - i]
        s += iv * rng.uniform(0.85, 1.15)
        iv *= rng.uniform(0.62, 0.8)
        a *= rng.uniform(0.6, 0.8)
    return amp * np.trim_zeros(out, 'b')


def golpe_tierra(peso=1.0, grieta=1.0, restos=1.0, dur=2.5):
    """Algo enorme contra la tierra: el golpe de presion, el cuerpo sordo,
    la roca que se raja, el suelo que retumba y lo que vuelve a caer."""
    t = t_(dur)
    sub = saturar(boom(78, 30, 0.26 * peso, dur), 2.5)   # el suelo no responde lineal: armonicos que se oyen
    cuerpo = bp(ruido(0.5, 'rosa'), 90, 700) * caida(0.5, 0.05 * peso, 0.002)
    aplasta = bp(ruido(0.3, 'rosa'), 300, 2800) * caida(0.3, 0.035, 0.001)    # la piedra que revienta debajo
    choque = bp(ruido(0.08), 150, 7000) * caida(0.08, 0.008, 0.0005)
    raja = rajar_roca(int(5 + 9 * grieta), 0.03 + 0.07 * grieta, 1.0, 0.8)
    temblor = retumbo(dur, 110, 2.5, 0.35, 0.6) * caida(dur, 0.35 * peso, 0.01)
    caen = escombros(dur, restos, 0.3 + 0.12 * peso, (0.4, 4 + 6 * restos))
    polvo = pb(ruido(dur, 'rosa'), 800) * np.interp(t, [0, 0.04, 0.5, dur], [0, 1, 0.35, 0])
    return mezclar(pico(sub, 0.5), pico(cuerpo, 0.6), pico(aplasta, 0.9), pico(choque, 0.7), pico(raja, 0.75 * grieta),
                   pico(temblor, 0.25), pico(caen, 0.7 * restos), pico(polvo, 0.25))


def brota(dur=0.3, f_ini=1300.0, f_fin=320.0, peso=1.0):
    """Una roca que sale del suelo empujada: roza contra la tierra que la
    sujeta y vibra como una barra empotrada: cuanto mas asoma, mas larga queda
    libre y mas grave canta (f ~ 1/L^2). Se frena al final."""
    n = n_(dur)
    L = curva(n, [(0, 0.45), (0.6, 0.9), (1, 1.0)])
    fc = np.minimum(f_fin / L ** 2, f_ini)
    vel = curva(n, [(0, 1.0), (0.6, 0.8), (1, 0.15)])
    m = moler(dur, peso, (60, 150), 0.9, velocidad=vel)
    canta = filtro_mov(m, fc, 'band', 3.0, 32)
    return mezclar(pico(canta, 1.0), pico(pb(m, 900), 0.6)) * ventana(dur, 0.005, dur * 0.3)


def crepitar(dur, tasa, fc, q=1.2):
    """Chasquidos que se suceden (algo que se rasga o que se carga):
    impulsos al azar por una banda que se mueve."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    exc = np.zeros(n)
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    exc[cuando] = rng.uniform(0.2, 1.0, len(cuando)) * rng.choice([-1.0, 1.0], len(cuando))
    nucleo = pa(ruido(0.002), 400) * caida(0.002, 0.0005, 0.0001)
    exc = signal.fftconvolve(exc, nucleo)[:n]
    return filtro_mov(exc, fc, 'band', q, 32)


def grieta_viaja(dur=1.1, fuerza=1.0):
    """Una grieta encendida que corre por el suelo hacia ti: chasquidos cada
    vez mas seguidos, fuertes y brillantes (de cerca el aire se come menos
    agudos), las bandas de la roca que suben con el Doppler, la tierra que
    retumba debajo y el chasquido final a tus pies."""
    n = n_(dur)
    t = t_(dur)
    cerca = (t / dur) ** 1.7
    doppler = curva(n, [(0, 0.92), (0.85, 1.07), (1, 1.0)])
    tasa = 50 + 1100 * cerca
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    exc = np.zeros(n)
    exc[cuando] = rng.uniform(0.2, 1.0, len(cuando)) * (0.25 + 0.75 * cerca[cuando])
    nucleo = pa(ruido(0.0015), 300) * caida(0.0015, 0.0004, 0.0001)
    exc = signal.fftconvolve(exc, nucleo)[:n]
    roca = sum(g * filtro_mov(exc, f * doppler, 'band', q, 32)
               for f, q, g in ((380, 3, 1.0), (900, 4, 0.8), (2000, 6, 0.55), (4200, 8, 0.4)))
    roca = roca + 0.5 * pa(exc, 3000) * cerca ** 2
    hondo = pa(filtro_mov(ruido(dur, 'marron'), 90 + 500 * cerca, 'low', 0.9), 28) * (0.15 + 0.85 * cerca)
    brilla = filtro_mov(ruido(dur), 520 * doppler * (1 + 0.5 * cerca), 'band', 45) * cerca
    piedras = grava(dur, 250 * cerca, (0.4, 3.0))
    llega = mezclar(pico(rajar_roca(10, 0.05, 1.1, 0.9), 1.0), pico(boom(120, 55, 0.08), 0.7),
                    pico(escombros(0.9, 0.5, 0.25, (0.4, 4.0)), 0.4))
    return mezclar(pico(roca, 0.9), pico(hondo, 0.5), pico(brilla, 0.1), pico(piedras, 0.3),
                   en(dur - 0.04, pico(llega, 0.8 * fuerza)))


def pasada(dur, f0, f1, q=1.8, silba=0.25):
    """Algo grande que corta el aire: la banda se mueve (Doppler) y silba."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.45, (f0 * f1) ** 0.5 * 1.15), (1, f1)])
    soplo = filtro_mov(ruido(dur, 'rosa'), f, 'band', q)
    canta = filtro_mov(ruido(dur), f * 1.6, 'band', 22, 32)
    e = campana_env(dur, 1.3) ** 1.4
    return mezclar(pico(soplo * e, 1.0), pico(canta * e, silba))


# ======================================================================
#  JADE, GLIFOS, MALDICION Y FUEGO VERDE
# ======================================================================
JADE = ((1, 1.0), (2.756, 0.5), (5.404, 0.28), (8.933, 0.15))          # barra libre (piedras sonoras)
JADE_TALLA = ((1, 1.0), (1.53, 0.55), (2.41, 0.42), (3.28, 0.3), (4.63, 0.18), (6.1, 0.1))   # pieza tallada
ORO = ((0.5, 0.7), (1, 1.0), (1.25, 0.45), (1.5, 0.4), (2, 0.55), (2.5, 0.25), (3, 0.18), (4.07, 0.1))  # campana


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


def destellos(dur, tasa, fmin=2500, fmax=7500, tau=(0.08, 0.3)):
    """Brillo cristalino: toques de jade agudos y sueltos (tasa: numero o curva)."""
    n = n_(dur)
    tasa = np.broadcast_to(np.asarray(tasa, dtype=float), (n,))
    cuando = np.nonzero(rng.random(n) < tasa / SR)[0]
    out = np.zeros(n + n_(4.1))
    for i in cuando:
        g = jade(rng.uniform(fmin, fmax), None, rng.uniform(*tau), JADE, 0.4, 0.002) * rng.uniform(0.2, 1.0)
        out[i:i + len(g)] += g[:len(out) - i]
    return np.trim_zeros(out, 'b') if np.any(out) else np.zeros(n)


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


def maldicion(dur, f=55.0, alto=1.0):
    """La Maldicion de la Raiz: la tierra y el jade zumbando juntos, grave y
    verde. Una nota honda que late contra si misma, su quinta que entra y
    sale y, muy arriba, un hilo de jade frotado."""
    n = n_(dur)
    hondo = canto_jade(dur, f, ((1, 1.0), (2, 0.55), (3, 0.35), (4, 0.2), (5, 0.12)), 220, 0.4)
    quinta = canto_jade(dur, f * 1.5, ((1, 1.0), (2, 0.4)), 260, 0.5) * np.clip(0.5 + 0.5 * suave(n, 0.4), 0, None)
    hilo = canto_jade(dur, f * 16, JADE[:3], 500, 0.8)
    return mezclar(pico(hondo, 1.0), pico(quinta, 0.35), pico(hilo, 0.12 * alto))


def glifo(f=220.0, fuerza=1.0, dur=1.2):
    """Un glifo de la maldicion que se enciende: el jade que canta de golpe
    (un 'uom' que se hincha y se apaga), un toque de jade y un golpe sordo."""
    t = t_(dur)
    env = (1 - np.exp(-t / 0.04)) * np.exp(-t / (dur * 0.3))
    canto_ = canto_jade(dur, f, JADE[:3], 90, 1.0) * env
    toque = jade(f * 2, dur, 0.3 * dur, JADE, 0.6)
    sordo = boom(f * 0.4, f * 0.3, 0.08)
    return fuerza * mezclar(pico(canto_, 1.0), pico(toque, 0.35), pico(sordo, 0.35))


def campana_oro(f, tau=3.0):
    """Jade engastado en oro: una campana honda (el hum una octava abajo, la
    tercera mayor, la quinta y la octava)."""
    return jade(f, None, tau, ORO, 0.6, 0.0009)


def llama(dur, fuerza=1.0, parpadeo=11.0, brillo=1.0):
    """Fuego verde que ruge: la combustion turbulenta (ruido grave que
    parpadea), las lenguas que lamen y los chasquidos."""
    n = n_(dur)
    brillo = np.broadcast_to(np.asarray(brillo, dtype=float), (n,))
    flick = np.exp(0.45 * suave(n, parpadeo)) * np.exp(0.3 * suave(n, 2.5))
    ruge = filtro_mov(ruido(dur, 'rosa'), 520 * brillo, 'low', 0.8) * flick
    lenguas = filtro_mov(ruido(dur), 1500 * brillo, 'band', 1.2) * np.exp(0.9 * suave(n, 7))
    chasq = np.zeros(n + n_(0.01))
    for s in np.nonzero(rng.random(n) < 30 * fuerza / SR)[0]:
        c = pa(ruido(0.003), 1500) * caida(0.003, 0.0007, 0.0001) * rng.uniform(0.2, 1.0)
        chasq[s:s + len(c)] += c
    return mezclar(pico(ruge, 1.0), pico(lenguas, 0.35), pico(chasq[:n], 0.3 * fuerza))


# ======================================================================
#  VOZ
# ======================================================================
FEL_CERRADO = (240, 640, 1250, 1900, 2650)      # "o": boca casi cerrada, tracto larguisimo
FEL_ABIERTO = (580, 1020, 1600, 2250, 3000)     # "a": las fauces abiertas del todo
ANCHOS = (140, 160, 200, 240, 300)
GANANCIAS = (1.0, 0.85, 0.5, 0.32, 0.18)


def formantes_felino(abre, escala=1.0):
    """Formantes del felino segun lo abierta que este la boca (numero o curva)."""
    return tuple(((c + (o - c) * abre) * escala, w, g) for c, o, w, g in zip(FEL_CERRADO, FEL_ABIERTO, ANCHOS, GANANCIAS))


def garganta(f0, dur, formantes, aspereza=0.5, sub=0.4, jitter=0.03, aliento=0.25, fmax=5000,
             caos=0.0, fritura=0.0, fritura_hz=26.0, pecho=0.0):
    """Una garganta enorme: pulsos con jitter, subarmonico que la raspa,
    tramos caoticos (ruido que late con cada ciclo), fritura (los pulsos que
    se oyen sueltos: el gruñido), formantes (pueden ser curvas) y el pecho."""
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


def bufido(f=70.0, dur=0.4, abre=0.5):
    """Un gruñido corto, de esfuerzo o de remate (los leones cierran asi el rugido)."""
    n = n_(dur)
    tono = curva(n, [(0, f), (0.25, f * 1.08), (1, f * 0.72)])
    v = garganta(tono, dur, formantes_felino(curva(n, [(0, 0.3), (0.3, abre), (1, 0.15)])), 0.7, 0.4, 0.03, 0.5,
                 4000, 0.15, pecho=0.4)
    return v * caida(dur, dur * 0.3, 0.03)


def rugido(dur=3.3, f0=62.0, f1=106.0, abre=1.0, piedra=1.0, verde=1.0, pecho=1.0, final=0, escala=1.0,
           cola=2.2, mezcla=0.3, sube=0.22, contorno=None):
    """El rugido de Rajang: la garganta que sube y cae de tono mientras las
    fauces se abren de "o" a "a" y se cierran, con subarmonicos y caos en lo
    mas alto; una segunda garganta (algo desfasada) y otra una octava abajo
    que le dan tamano; la piedra que muele dentro, pasada por los mismos
    formantes; crujidos del jade que se tensa y el zumbido de la maldicion."""
    n = n_(dur)
    if contorno is None:
        contorno = [(0, f0 / f1), (sube, 1.0), (0.5, 0.97), (0.78, 0.84), (1, 0.8 * f0 / f1)]
    tono = f1 * curva(n, contorno)
    ab = abre * curva(n, [(0, 0.1), (sube * 0.9, 0.9), (0.55, 1.0), (0.85, 0.55), (1, 0.1)])
    fs = formantes_felino(ab, escala)
    sub_ = curva(n, [(0, 0.2), (sube + 0.08, 0.5), (0.7, 0.4), (1, 0.3)])
    # caos a rachas (como en los rugidos de verdad): tramos cortos en lo alto
    x = np.linspace(0, 1, n)
    caos = 0.04 + sum(h * np.exp(-((x - c) / w) ** 2) for c, w, h in
                      ((sube + 0.06, 0.05, 0.32), (rng.uniform(0.45, 0.55), 0.04, 0.22), (rng.uniform(0.66, 0.74), 0.05, 0.28)))
    voz = garganta(tono, dur, fs, 0.6, sub_, 0.018, 0.18, 6000, caos, pecho=0.35)
    doble = garganta(tono * 1.004, dur, fs, 0.6, sub_, 0.02, 0.18, 6000, caos, pecho=0.35)
    hondo = garganta(tono * 0.5, dur, formantes_felino(ab * 0.45, escala * 0.85), 0.75, 0.5, 0.05, 0.3, 3000,
                     fritura=0.35, pecho=0.6)
    amp = ventana(dur, 0.1, dur * 0.38) * curva(n, [(0, 0.4), (sube, 1.0), (0.6, 0.92), (1, 0.6)])
    m = moler(dur, 1.1, (22, 60), 0.8)
    roca = filtro_mov(m, fs[0][0], 'band', 2.5) + 0.7 * filtro_mov(m, fs[1][0], 'band', 3.0)
    grietas = mezclar(*[en(rng.uniform(sube, 0.8) * dur, rajar_roca(int(rng.integers(3, 8)), 0.04) * rng.uniform(0.4, 1.0))
                        for _ in range(4)])
    capas = [pico(voz * amp, 1.0), en(0.011, pico(doble * amp, 0.35)), pico(hondo * amp, 0.45 * pecho),
             pico(roca * amp, 0.2 * piedra), pico(grietas, 0.13 * piedra), pico(maldicion(dur, 55.0) * amp, 0.07 * verde),
             pico(boom(50, 28, 0.45), 0.35)]
    for k in range(final):
        capas.append(en(dur - 0.25 + 0.42 * k, pico(bufido(f0 * (1.05 - 0.08 * k), 0.4, 0.55), 0.55 - 0.12 * k)))
    return reverb(mezclar(*capas), mezcla, cola, 6500)


def grunido(dur=1.3, f0=60.0, abre=0.5, cola=1.8):
    """Un gruñido: garganta grave con los pulsos sueltos (fritura), los
    belfos recogidos (formantes algo mas altos), el aire que silba entre los
    sables y la piedra que muele."""
    n = n_(dur)
    tono = curva(n, [(0, f0 * 0.85), (0.25, f0 * 1.1), (0.7, f0), (1, f0 * 0.8)])
    ab = curva(n, [(0, 0.15), (0.3, abre), (0.75, abre * 0.8), (1, 0.2)])
    fs = formantes_felino(ab, 1.08)
    fr = curva(n, [(0, 18), (0.4, 27), (1, 17)])
    voz = garganta(tono, dur, fs, 0.75, 0.45, 0.025, 0.3, 5000, 0.12, fritura=0.6, fritura_hz=fr, pecho=0.4)
    siseo = bp(ruido(dur), 2500, 8000) * (0.5 + 0.5 * np.abs(suave(n, 20)))
    amp = ventana(dur, 0.06, dur * 0.45) * curva(n, [(0, 0.5), (0.3, 1.0), (1, 0.6)])
    roca = filtro_mov(moler(dur, 1.0, (18, 45), 0.6), fs[0][0], 'band', 2.5)
    capas = mezclar(pico(voz * amp, 1.0), pico(siseo * amp, 0.08), pico(roca * amp, 0.22),
                    pico(maldicion(dur, 55.0) * amp, 0.05))
    return reverb(capas, 0.25, cola, 6500)


def quejido(dur=0.7, f=100.0, abre=0.85):
    """Un gruñido de dolor corto: sube de golpe, se abre y se cierra."""
    n = n_(dur)
    tono = curva(n, [(0, f * 0.9), (0.15, f * 1.35), (0.5, f * 1.15), (1, f * 0.7)])
    fs = formantes_felino(curva(n, [(0, 0.3), (0.15, abre), (1, 0.2)]), 1.05)
    v = garganta(tono, dur, fs, 0.75, 0.45, 0.025, 0.25, 6000, 0.18, pecho=0.3)
    return v * caida(dur, dur * 0.3, 0.02)


def respiro(dur, sale=True, f0=46.0, voz=0.4, fuerza=1.0):
    """Una bocanada de un felino de ocho bloques: el aire por un tracto
    enorme (ruido por formantes graves) y, al soltarlo, la garganta que
    vibra un poco: un gruñido hondo y pulsado."""
    n = n_(dur)
    if sale:
        env = ventana(dur, dur * 0.12, dur * 0.65) * curva(n, [(0, 1.0), (1, 0.55)])
        F = ((280, 2.2, 1.0), (720, 3.5, 0.6), (1300, 5.0, 0.3))
    else:
        env = ventana(dur, dur * 0.6, dur * 0.18)
        F = ((420, 2.5, 1.0), (1050, 4.0, 0.7), (2100, 6.0, 0.35))
    x = ruido(dur, 'rosa')
    aire = sum(g * resonar(x, f, q) for f, q, g in F) * (1 + 0.25 * suave(n, 10))
    capas = [pico(aire * env, 1.0)]
    if sale and voz:
        v = garganta(curva(n, [(0, f0), (1, f0 * 0.86)]), dur, formantes_felino(0.12, 0.9), 0.75, 0.5, 0.05, 1.0, 3000,
                     fritura=0.55, fritura_hz=21.0, pecho=0.6)
        capas.append(pico(v * env, voz))
    return fuerza * mezclar(*capas)


# ======================================================================
#  Guardar
# ======================================================================
# Duracion maxima de cada evento (lo demas es cola muy floja que se apaga).
LARGOS = {'ambiente': 6.2, 'dormido': 7.0, 'paso': 1.4, 'herido': 1.4, 'inmune': 1.4, 'rugido': 5.0, 'grunido': 2.0,
          'despertar': 7.2, 'zarpazo': 1.4, 'garra_alza': 1.3, 'garra_golpe': 2.6, 'grieta': 2.0, 'pico': 2.0, 'pico_golpe': 1.5,
          'terremoto': 5.0, 'onda': 2.0, 'pilar': 2.4, 'aviso': 1.8, 'piel_jade': 2.6, 'lastre': 1.8, 'sello': 6.0,
          'plataforma': 4.0, 'totem': 3.0, 'totem_golpe': 1.6, 'totem_roto': 3.2, 'totem_rehace': 3.4, 'columna': 6.5,
          'rugido_jade': 6.0, 'reloj': 0.6, 'cataclismo': 7.0, 'cielo': 5.0, 'fragmento': 2.8, 'impacto': 3.0,
          'marca': 1.8, 'salto': 1.6, 'aterriza': 3.0, 'aturdido': 4.5, 'paralizado': 5.0, 'cura': 3.0, 'tambaleo': 4.5,
          'liberacion': 7.0, 'disolver': 3.6,
          # las mejoras de octubre de 2026
          'embestida_aviso': 1.9, 'embestida': 2.6, 'embestida_frena': 2.4, 'estampado': 2.6, 'tumba': 3.9,
          'tumba_estalla': 3.2, 'furia': 3.8, 'escalon_tiembla': 1.4, 'escalon_cae': 2.2, 'totem_pulso': 2.4}


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


def guardar(evento, x, variante=None, alto=0.89, limite=None, largo=None, techo=None):
    """`largo`: duracion maxima; la cola que sobra (reverb, el jade que
    sigue sonando muy flojo) se apaga con una rampa de coseno. `techo`:
    sonoridad maxima (dB A): los toques tonales, con poco pico y mucha
    energia, no deben sonar mas que los golpes; y las variantes, parejas."""
    largo = largo or LARGOS.get(evento)
    x = pa(x, 25)
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
    sf.write(os.path.join(OUT, nombre + '.ogg'), x.astype(np.float32), SR, format='OGG', subtype='VORBIS')
    EVENTOS.setdefault(evento, []).append(nombre)
    GUARDADOS.append((nombre, x))
    print(f'  {nombre:22s} {len(x) / SR:5.2f} s', flush=True)


# ======================================================================
#  AMBIENTE: despierto. Respira hondo con un gruñido dentro, la piedra de
#  su cuerpo se asienta, rueda alguna china y la maldicion zumba.
# ======================================================================
for i in range(2):
    d = 5.6
    entra = respiro(1.6, False)
    sale = respiro(2.4, True, 44.0 + 4 * i, 0.6)
    piedras = moler(1.1, 1.3, (12, 30), 0.6) * campana_env(1.1, 1.2)
    rueda = rodar(1.2, 5.0 + 2 * i, 4, 1.0, 0.15)
    cristal = jade(rng.uniform(1900, 2600), None, 0.3, JADE_TALLA, 0.5)
    hum = maldicion(d, 55.0 - 4 * i) * ventana(d, 1.5, 1.8)
    capas = mezclar(pico(entra, 0.45), en(1.5, pico(sale, 0.8)), en(0.9 + 2.6 * i, pico(piedras, 0.3)),
                    en(3.6 - 2.2 * i, pico(rueda, 0.18)), en(rng.uniform(2.0, 4.0), pico(cristal, 0.07)), pico(hum, 0.14))
    guardar('ambiente', reverb(capas, 0.3, 2.0, 5500), i + 1, alto=0.7)

# ======================================================================
#  DORMIDO: una esfinge de piedra. Una sola respiracion, lentisima; el
#  pecho de piedra cruje al llenarse y suelta un hilo de polvo.
# ======================================================================
for i in range(2):
    d = 6.6
    n = n_(d)
    entra = pb(respiro(2.6, False), 1500)
    sale = pb(respiro(3.2, True, 39.0 + 3 * i, 0.3), 1300)
    sube = moler(2.6, 1.9, (7, 16), 0.25) * campana_env(2.6, 1.6)
    baja = moler(2.4, 2.0, (6, 14), 0.2) * campana_env(2.4, 1.6)
    polvo = grava(d, 7 * np.clip(1 + suave(n, 0.4), 0, None), (0.4, 1.4))
    hum = maldicion(d, 49.0 + 2 * i) * ventana(d, 2.0, 2.0)
    capas = mezclar(pico(entra, 0.5), en(0.2, pico(sube, 0.25)), en(2.8, pico(sale, 0.6)), en(3.0, pico(baja, 0.2)),
                    pico(polvo, 0.06), pico(hum, 0.1))
    guardar('dormido', reverb(capas, 0.3, 2.2, 4500), i + 1, alto=0.6)


# ======================================================================
#  PASO: una zarpa de jade de dos bloques sobre las losas de la plaza
# ======================================================================
def pisada(peso=1.0):
    sub = saturar(boom(72, 30, 0.15 * peso), 2.2)
    cuerpo = bp(ruido(0.3, 'rosa'), 90, 700) * caida(0.3, 0.05 * peso, 0.002)
    toc = canto(24, 1.0, False)
    unas = mezclar(*[en(0.004 * k + rng.uniform(0, 0.006), jade(rng.uniform(2200, 3400), None, 0.02, JADE_TALLA, 1.0))
                     for k in range(4)])      # las garras de obsidiana
    cruje = grava(0.5, 2500 * np.exp(-t_(0.5) / 0.03), (0.4, 3.0))
    machaca = rajar_roca(5, 0.03, 0.9, 0.8)
    polvo = pb(ruido(0.8, 'rosa'), 900) * caida(0.8, 0.18, 0.01)
    caen = escombros(1.0, 0.25, 0.22, (0.4, 2.5), 0.2)
    return mezclar(pico(sub, 0.32), pico(cuerpo, 0.7), en(0.006, pico(toc, 0.85)), pico(unas, 0.15), pico(cruje, 0.7),
                   pico(machaca, 0.6), pico(polvo, 0.2), pico(caen, 0.3))


for i in range(3):
    guardar('paso', reverb(pisada(1.0 + 0.12 * i), 0.15, 1.0, 5000), i + 1, limite=0.45)

# ======================================================================
#  HERIDO: el golpe le salta una lasca. Chasquido, el jade que suena, las
#  esquirlas que caen y un gruñido de dolor.
# ======================================================================
for i in range(3):
    golpe = mezclar(pico(pb(ruido(0.1), 2500) * caida(0.1, 0.01), 0.7), pico(boom(120, 60, 0.06), 0.5))
    raja = rajar_roca(8 + 2 * i, 0.04, 1.0, 1.0)
    timbre = jade(rng.uniform(600, 900), None, 0.22, JADE_TALLA, 1.0)
    lascas = mezclar(pico(esquirlas(5, 0.25, 2000, 6000), 1.0), pico(escombros(0.9, 0.25, 0.25, (0.4, 2.0)), 0.8))
    queja = quejido(0.7, 96 + 12 * i)
    guardar('herido', reverb(mezclar(golpe, pico(raja, 0.6), pico(timbre, 0.3), pico(lascas, 0.25), en(0.035, pico(queja, 0.95))),
                             0.22, 1.6), i + 1, limite=0.6)

# ======================================================================
#  INMUNE: dormido o despertando, el arma resbala por el jade: el toque
#  seco, la piedra que canta y el filo que patina.
# ======================================================================
for i in range(3):
    choque = mezclar(pico(pa(ruido(0.012), 1500) * caida(0.012, 0.002), 1.0), pico(boom(240, 160, 0.03), 0.35))
    timbre = jade(780 + 140 * i, None, 0.32, JADE_TALLA, 1.0)
    alto_ = jade(2300 + 200 * i, None, 0.18, JADE, 1.0)
    resbala = moler(0.18, 0.35, (180, 320), 0.6) * caida(0.18, 0.05)
    chinas = esquirlas(2, 0.15, 3500, 7000)
    guardar('inmune', reverb(mezclar(choque, pico(timbre, 0.6), pico(alto_, 0.3), en(0.01, pico(resbala, 0.25)),
                                     pico(chinas, 0.15)), 0.2, 1.5), i + 1, limite=0.6, techo=-19.0)

# ======================================================================
#  RUGIDO y GRUNIDO
# ======================================================================
guardar('rugido', rugido(3.3, 62, 106), 1, limite=0.6)
guardar('rugido', rugido(3.0, 58, 98, final=2), 2, limite=0.6)
guardar('grunido', grunido(1.3, 60, 0.5), 1, limite=0.65)
guardar('grunido', grunido(1.1, 66, 0.6), 2, limite=0.65)

# ======================================================================
#  DESPERTAR: la esfinge se levanta. La piedra muele, la costra de piedra
#  se raja y se desprende, cae polvo y grava, la tierra retumba, se le
#  encienden los glifos y ruge.
# ======================================================================
d = 7.0
dl = 3.2
levanta = moler(dl, 1.6, (10, 34), 0.7, velocidad=curva(n_(dl), [(0, 0.4), (0.6, 1.0), (1, 1.2)]))
levanta *= np.interp(t_(dl), [0, 0.5, 2.6, dl], [0, 0.6, 1, 0.3])
costra = mezclar(*[en(s, rajar_roca(int(rng.integers(4, 11)), 0.05, 1.0, 0.9) * (0.3 + 0.7 * s / 2.8))
                   for s in np.sort(rng.uniform(0.2, 2.8, 10))])
cae = grava(3.4, np.interp(t_(3.4), [0, 0.6, 2.4, 3.4], [20, 400, 900, 100]), (0.4, 6.0))
tierra = retumbo(4.0, 110, 1.2, 0.4, 0.8) * np.interp(t_(4.0), [0, 1.5, 2.8, 4.0], [0.1, 0.7, 1.0, 0])
cantos = mezclar(en(1.3, rodar(1.2, 14, 5)), en(2.2, rodar(1.0, 9, 4, 0.7)))
guardar('despertar', mezclar(pico(levanta, 0.5), pico(costra, 0.35), pico(cae, 0.3), pico(tierra, 0.45), pico(cantos, 0.3),
                             en(2.2, pico(glifo(220, 1.0, 1.4), 0.35)),
                             en(2.75, pico(rugido(3.5, 60, 104, cola=2.4), 1.0))), limite=0.55)

# ======================================================================
#  GARRA TERRESTRE: alza la zarpa (el aire que arrastra y la tierra que se
#  carga, crepitando y cantando) y la descarga contra el suelo.
# ======================================================================
for i in range(2):
    d = 0.9
    n = n_(d)
    barre = pasada(d, 260, 1000 + 120 * i, 1.4, 0.08)
    carga = crepitar(d, 40 + 900 * rampa(d, 2.0), curva(n, [(0, 700), (1, 2600)]), 1.5) * rampa(d, 1.5)
    canta = filtro_mov(ruido(d), curva(n, [(0, 300 + 30 * i), (1, 950 + 60 * i)]), 'band', 40) * rampa(d, 2.0)
    hombro = moler(0.5, 1.2, (20, 50), 0.5) * campana_env(0.5, 1.0)
    corte = ventana(d, 0.005, 0.07)
    guardar('garra_alza', reverb(mezclar(pico(barre, 0.6), pico(carga * corte, 0.35), pico(canta * corte, 0.18), pico(hombro, 0.35)),
                                 0.22, 1.5), i + 1, techo=-20.0)
for i in range(2):
    zarpazo = pasada(0.22, 1500, 300, 1.4, 0.06)
    golpe = golpe_tierra(1.3 + 0.1 * i, 1.4, 1.0, 2.6)
    unas = mezclar(*[en(0.006 * k, jade(rng.uniform(1600, 2400), None, 0.03, JADE_TALLA, 1.0)) for k in range(4)])
    guardar('garra_golpe', reverb(mezclar(pico(zarpazo, 0.35), en(0.08, golpe), en(0.08, pico(unas, 0.2))), 0.25, 2.0),
            i + 1, limite=0.55)

# La grieta encendida que corre hacia el objetivo.
for i in range(2):
    guardar('grieta', reverb(grieta_viaja(1.05 + 0.1 * i), 0.22, 1.6), i + 1, limite=0.45)

# Los picos de roca que revientan el suelo: la tierra se abomba, cada pico
# raja la piedra al salir y canta al asomar, y lo arrancado vuelve a caer.
for i in range(3):
    capas = [pico(retumbo(0.12, 140, 6, 0.3) * rampa(0.12, 2.0), 0.4)]
    for j in range(3 + i % 2):
        s = 0.06 + j * rng.uniform(0.035, 0.07)
        estallo = mezclar(pico(rajar_roca(10, 0.04, 1.1, 0.9), 1.0), pico(boom(110, 50, 0.07), 0.6),
                          en(0.004, pico(brota(rng.uniform(0.22, 0.32), 1400, rng.uniform(280, 420), 0.8), 0.7)))
        capas.append(en(s, estallo * (1 - 0.15 * j)))
    capas.append(en(0.06, pico(escombros(1.6, 0.9, 0.35, (0.4, 6.0)), 0.35)))
    capas.append(en(0.06, pico(pb(ruido(1.0, 'rosa'), 900) * caida(1.0, 0.25, 0.01), 0.12)))
    guardar('pico', reverb(mezclar(*capas), 0.22, 1.7), i + 1, limite=0.55)
# Un pico te alcanza y te lanza: el golpe sordo en el cuerpo, la roca que
# cruje y el aire que silba hacia arriba.
for i in range(2):
    golpe = mezclar(pico(boom(150, 70, 0.05), 0.9), pico(pb(ruido(0.12, 'rosa'), 1400) * caida(0.12, 0.018), 0.8))
    roca = rajar_roca(6, 0.03, 1.0, 1.0)
    lanza = pasada(0.7, 500, 2600 + 200 * i, 1.5, 0.15)
    piedras = grava(0.6, 1500 * np.exp(-t_(0.6) / 0.06), (0.4, 3.0))
    guardar('pico_golpe', reverb(mezclar(golpe, pico(roca, 0.5), en(0.03, pico(lanza, 0.55)), pico(piedras, 0.2)), 0.18, 1.4),
            i + 1, limite=0.6)

# ======================================================================
#  TERREMOTO ANCESTRAL: dos zarpazos contra el suelo y la tierra entera
#  que tiembla: retumbo, sacudidas, las piedras sueltas que traquetean, las
#  losas que se rajan y algun canto que rueda.
# ======================================================================
for i in range(2):
    d = 4.8
    n = n_(d)
    t = t_(d)
    env = np.interp(t, [0, 0.35, 0.7, 3.2, d], [0, 0.4, 1.0, 0.8, 0])
    sacude = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(5.0 + 1.5 * suave(n, 1.0)) / SR)
    temblor = retumbo(d, 120, 1.5, 0.5, 1.0) * env * (0.75 + 0.25 * sacude)
    gime = moler(d, 2.2, (7, 18), 0.3) * env
    traquetea = grava(d, 500 * env * sacude, (0.4, 5.0))
    rajas = mezclar(*[en(s, rajar_roca(int(rng.integers(5, 12)), 0.06, 1.0, 0.8)) for s in rng.uniform(0.5, 3.6, 6)])
    cantos = mezclar(*[en(s, rodar(1.2, rng.uniform(8, 18), 5, rng.uniform(0.5, 1.0))) for s in rng.uniform(0.6, 3.2, 3)])
    patas = mezclar(pico(golpe_tierra(1.5, 1.2, 0.8, 2.5), 1.0), en(0.34 + 0.04 * i, pico(golpe_tierra(1.6, 1.4, 0.9, 2.5), 1.0)))
    guardar('terremoto', reverb(mezclar(pico(patas, 1.0), pico(temblor, 0.65), pico(gime, 0.4), pico(traquetea, 0.45),
                                        pico(rajas, 0.35), pico(cantos, 0.35)), 0.28, 2.4, 5000), i + 1, limite=0.45)

# La onda: el golpe de presion que pasa, el aire que barre y las losas que
# saltan una tras otra, como fichas, con la grava encima.
for i in range(2):
    d = 1.6
    t = t_(d)
    whoomp = saturar(boom(95, 34, 0.12), 2.2)
    barre = filtro_mov(ruido(d, 'rosa'), curva(n_(d), [(0, 200), (0.25, 1300 + 150 * i), (1, 240)]), 'band', 1.2)
    barre *= np.interp(t, [0, 0.2, 0.5, d], [0, 1, 0.4, 0])
    losas = mezclar(*[en(0.03 + 0.045 * k * rng.uniform(0.85, 1.15), canto(rng.uniform(18, 30), np.sin(np.pi * (k + 1) / 10), False))
                      for k in range(9)])
    piedras = grava(d, 1600 * np.exp(-((t - 0.25) / 0.15) ** 2), (0.4, 3.0))
    guardar('onda', reverb(mezclar(pico(whoomp, 0.6), pico(barre, 0.55), pico(losas, 0.65), pico(piedras, 0.4)), 0.25, 1.8),
            i + 1, limite=0.6)

# Las columnas que revientan el suelo: el crujido hondo, la columna que
# sube rozando, el tope al asentarse y la roca que cae rodando.
for i in range(3):
    cruje = mezclar(pico(saturar(boom(80, 32, 0.2), 2.5), 0.55), pico(rajar_roca(16, 0.08, 0.8, 0.7), 0.8),
                    pico(bp(ruido(0.2, 'rosa'), 90, 700) * caida(0.2, 0.04), 0.6),
                    pico(bp(ruido(0.3, 'rosa'), 300, 2800) * caida(0.3, 0.035, 0.001), 0.7))
    sube = brota(0.6, 900, 160 + 30 * i, 1.6)
    tope = mezclar(pico(canto(28, 1.0, False), 1.0), pico(boom(85, 50, 0.08), 0.6))
    rueda = rodar(1.4, 10 + 4 * i, 6)
    caen = escombros(2.0, 1.0, 0.45, (0.4, 8.0))
    guardar('pilar', reverb(mezclar(cruje, en(0.02, pico(sube, 0.75)), en(0.58, pico(tope, 0.6)), en(0.6, pico(rueda, 0.45)),
                                    pico(caen, 0.4)), 0.25, 1.9), i + 1, limite=0.55)

# El aviso: un glifo hexagonal se enciende en el suelo y la tierra crepita.
for i in range(2):
    d = 1.4
    zumba = maldicion(d, 55.0 * (1 + 0.06 * i)) * ventana(d, 0.35, 0.5)
    crepita = mezclar(grava(d, 60 + 260 * rampa(d, 1.5), (0.4, 1.5)), en(0.3, rajar_roca(4, 0.5, 1.2, 0.6) * 0.4))
    guardar('aviso', reverb(mezclar(pico(zumba, 0.45), pico(glifo(165 + 20 * i, 1.0, 1.2), 0.75), pico(crepita, 0.3)), 0.3, 1.8),
            i + 1, limite=0.6)

# Piel de Jade: un brillo de cristal que crece y la piedra que se aprieta
# hasta cerrarse con un golpe seco; los aros de runas suenan.
d = 2.0
n = n_(d)
brillo = destellos(d, 20 + 260 * rampa(d, 1.3))
canta = canto_jade(d, 330, JADE, 200) * ventana(d, 0.4, 0.5)
dl = 1.25
aprieta = filtro_mov(moler(dl, 0.9, (25, 70), 0.6, velocidad=curva(n_(dl), [(0, 0.5), (1, 1.6)])),
                     curva(n_(dl), [(0, 300), (1, 900)]), 'band', 1.5) * rampa(dl, 1.2, 0.2, 1.0)
cierra = mezclar(pico(jade(196, None, 0.5, JADE_TALLA, 0.8), 0.8), pico(boom(90, 60, 0.08), 0.7),
                 pico(pb(ruido(0.03), 3000) * caida(0.03, 0.004), 0.5))
guardar('piel_jade', reverb(mezclar(pico(brillo, 0.3), pico(canta, 0.3), pico(aprieta, 0.45), en(dl, cierra),
                                    en(dl + 0.02, pico(glifo(262, 1.0, 1.0), 0.35))), 0.3, 2.0))

# Lastre: un peso de piedra que te cae encima y te hunde, con grava.
for i in range(2):
    d = 1.4
    t = t_(d)
    cae = saturar(boom(130, 38, 0.15), 2.2)
    hunde = filtro_mov(ruido(0.7, 'rosa'), curva(n_(0.7), [(0, 900), (1, 150)]), 'low', 1.0) * caida(0.7, 0.25, 0.01)
    pesa = moler(0.9, 2.0, (9, 20), 0.4) * caida(0.9, 0.3, 0.02)
    ambar = jade(140 + 15 * i, None, 0.4, JADE_TALLA, 0.5)
    arena = grava(d, 300 * np.exp(-t / 0.3), (0.4, 2.0))
    guardar('lastre', reverb(mezclar(pico(cae, 0.5), pico(hunde, 0.5), pico(pesa, 0.65), pico(ambar, 0.35), pico(arena, 0.45)),
                             0.22, 1.5), i + 1, limite=0.6)

# ======================================================================
#  SELLO DE LA TIERRA: ruge y la tierra se levanta en cuatro plataformas;
#  los cuatro totems se encienden uno tras otro.
# ======================================================================
d = 4.6
t = t_(d)
sube_env = np.interp(t, [0, 0.6, 3.0, 4.0, d], [0, 0.3, 1.0, 0.5, 0])
tierra = retumbo(d, 110, 1.0, 0.4, 0.9) * sube_env
gime = moler(d, 1.8, (9, 24), 0.6, velocidad=0.5 + sube_env) * sube_env
cae = grava(d, 500 * sube_env, (0.4, 6.0))
glifos = mezclar(*[en(1.3 + 0.32 * k, glifo(f, 0.8, 1.2)) for k, f in enumerate((165, 196, 220, 262))])
guardar('sello', mezclar(pico(rugido(2.6, 64, 108, cola=2.0), 1.0), pico(reverb(mezclar(pico(tierra, 0.7), pico(gime, 0.45), pico(cae, 0.3)),
                                                                                 0.3, 2.4), 0.8),
                         pico(reverb(glifos, 0.35, 2.4), 0.45)), limite=0.55)

# La plataforma de tierra que sube con el parkour: gemido largo, retumbo,
# lo que se desprende y el golpe al asentarse.
for i in range(2):
    d = 3.2
    n = n_(d)
    vel = curva(n, [(0, 0.5), (0.2, 1.0), (0.85, 1.0), (1, 0.2)])
    gime = moler(d, 1.9 + 0.2 * i, (10, 26), 0.8, velocidad=vel) * ventana(d, 0.25, 0.5)
    tierra = retumbo(d, 130, 1.8, 0.4, 0.9) * ventana(d, 0.3, 0.6)
    caen = grava(d, 350 * vel, (0.4, 6.0))
    cantos = mezclar(en(0.8, rodar(1.0, 10, 4, 0.7)), en(1.9, rodar(1.0, 13, 5, 0.8)))
    asienta = mezclar(pico(canto(30, 1.0, False), 1.0), pico(boom(70, 35, 0.12), 0.8))
    guardar('plataforma', reverb(mezclar(pico(gime, 0.75), pico(tierra, 0.5), pico(caen, 0.35), pico(cantos, 0.3),
                                         en(d - 0.35, pico(asienta, 0.6))), 0.28, 2.2), i + 1, limite=0.6)

# El totem encendido: una columna de jade que canta frotada, la maldicion
# debajo y un pulso de los glifos cada segundo (se repite mientras vive).
for i in range(2):
    d = 3.0
    f = (110.0, 98.0)[i]
    canta = canto_jade(d, f, JADE[:3], 250, 0.5)
    hondo = maldicion(d, f / 2)
    pulsos = mezclar(*[en(s, glifo(f * 2, 0.7, 0.85)) for s in (0.12, 1.12, 2.12)])
    capas = mezclar(pico(canta, 0.5), pico(hondo, 0.5), pico(pulsos, 0.6))[:n_(d)] * ventana(d, 0.3, 0.4)
    guardar('totem', capas, i + 1, techo=-22.0)
for i in range(3):
    choque = mezclar(pico(pb(ruido(0.06), 3500) * caida(0.06, 0.006), 0.8), pico(boom(200, 120, 0.035), 0.35))
    raja = rajar_roca(6, 0.03, 1.0, 1.1)
    lasca = escombros(0.8, 0.2, 0.2, (0.4, 3.0))
    anillo = jade(520 + 90 * i, None, 0.4, JADE, 0.8)
    parpadea = canto_jade(0.5, 220, JADE[:2], 60) * caida(0.5, 0.12, 0.01)
    guardar('totem_golpe', reverb(mezclar(choque, pico(raja, 0.6), pico(lasca, 0.25), pico(anillo, 0.45), pico(parpadea, 0.2)),
                                  0.22, 1.6), i + 1, limite=0.5, techo=-19.5)
# Roto: la columna revienta en trozos que ruedan, el nucleo de jade salta
# en esquirlas y el canto de los glifos se apaga cayendo de tono.
for i in range(2):
    d = 3.0
    n = n_(d)
    t = t_(d)
    estalla = mezclar(pico(saturar(boom(80, 30, 0.25), 2.5), 0.55), pico(rajar_roca(24, 0.12, 1.0, 0.8), 0.9),
                      pico(bp(ruido(0.3), 200, 6000) * caida(0.3, 0.04), 0.5))
    trozos = mezclar(*[en(rng.uniform(0.1, 0.5), rodar(1.5, rng.uniform(8, 20), 5, rng.uniform(0.5, 1.0))) for _ in range(4)])
    vidrio = esquirlas(18, 0.4, 1500, 7000)
    caen = escombros(2.0, 1.2, 0.4, (0.4, 8.0))
    muere = filtro_mov(ruido(d), curva(n, [(0, 440 - 30 * i), (0.5, 180), (1, 100)]), 'band', 60) * caida(d, 0.6, 0.005)
    apaga = maldicion(d, 55.0) * np.exp(-t / 0.5)
    guardar('totem_roto', reverb(mezclar(estalla, pico(trozos, 0.5), pico(vidrio, 0.45), pico(caen, 0.4), pico(muere, 0.25),
                                         pico(apaga, 0.25)), 0.28, 2.2), i + 1, limite=0.55)
# Se rehace: la piedra y el jade vuelven a juntarse (el sonido al reves),
# se cierra de golpe y el glifo se enciende otra vez subiendo.
junta = mezclar(pico(escombros(1.6, 1.0, 0.4, (0.4, 6.0)), 0.6), pico(rodar(1.5, 12, 5), 0.5),
                pico(rajar_roca(14, 0.1, 1.0, 0.8), 0.5), pico(esquirlas(10, 0.4, 1500, 6000), 0.4))[:n_(1.6)]
junta = junta[::-1] * rampa(1.6, 1.5, 0.3, 1.0)
reenciende = filtro_mov(ruido(1.7), curva(n_(1.7), [(0, 110), (1, 440)]), 'band', 60) * rampa(1.7, 2.0)
cierra = mezclar(pico(canto(26, 1.0, False), 1.0), pico(boom(95, 55, 0.12), 0.7), pico(jade(330, None, 0.6, JADE, 0.8), 0.45),
                 pico(glifo(220, 1.0, 1.0), 0.5))
guardar('totem_rehace', reverb(mezclar(pico(junta, 0.7), pico(reenciende, 0.25), en(1.6, cierra)), 0.28, 2.0), limite=0.6)

# ======================================================================
#  LAS COLUMNAS DEL SELLO: cuatro torres de roca que suben a empellones en
#  las esquinas del templo. Retumbo hondisimo, piedra que gime grave, rocas
#  que se les caen y la maldicion debajo de todo.
# ======================================================================
d = 6.0
n = n_(d)
t = t_(d)
env = np.interp(t, [0, 1.5, 4.0, 5.2, d], [0.1, 0.6, 1.0, 0.6, 0])
temblor = retumbo(d, 85, 0.9, 0.5, 1.0) * env
gime = pb(moler(d, 3.0, (6, 15), 0.5, velocidad=0.6 + 0.6 * env), 1800) * env
caen = pb(mezclar(*[en(s, rodar(1.6, rng.uniform(15, 30), 6, rng.uniform(0.4, 1.0))) for s in rng.uniform(0.8, 4.8, 7)]), 2200)
rajas = pb(mezclar(*[en(s, rajar_roca(int(rng.integers(8, 16)), 0.1, 0.8, 0.6)) for s in rng.uniform(0.6, 4.5, 6)]), 3000)
escombro = pb(grava(d, 300 * env, (1.0, 12.0)), 3000)
zumba = maldicion(d, 41.2) * env
asienta = boom(42, 22, 0.6)
guardar('columna', reverb(mezclar(pico(temblor, 0.5), pico(gime, 1.0), pico(caen, 0.7), pico(rajas, 0.45), pico(escombro, 0.55),
                                 pico(zumba, 0.25), en(4.3, pico(saturar(asienta, 2.0), 0.3))), 0.4, 3.2, 3500), limite=0.45)

# El Rugido de Jade: el Sello no se rompio y Rajang ruge con toda la tierra
# (una garganta aun mas grande y mas grave) y la onda verde revienta: golpe de presion, el aire que arrasa,
# lo que vuela, el brillo del jade y la maldicion que se hincha.
d = 3.0
t = t_(d)
golpe = boom(48, 18, 0.6, d)
arrasa = filtro_mov(ruido(d, 'rosa'), curva(n_(d), [(0, 300), (0.05, 3500), (0.4, 800), (1, 220)]), 'low', 0.9)
arrasa *= np.interp(t, [0, 0.06, 0.5, d], [0, 1, 0.5, 0]) ** 1.3
vuela = escombros(d, 1.5, 0.5, (0.4, 12.0))
verde = mezclar(pico(destellos(1.5, 400 * np.exp(-t_(1.5) / 0.3)), 1.0), pico(maldicion(d, 41.2) * np.exp(-t / 1.0), 1.0))
onda = mezclar(pico(golpe, 1.0), pico(arrasa, 0.75), pico(vuela, 0.3), pico(verde, 0.3), pico(rajar_roca(20, 0.15, 1.0, 0.7), 0.5))
guardar('rugido_jade', mezclar(pico(rugido(4.0, 44, 80, escala=0.82, pecho=1.4, piedra=1.6, verde=1.5, cola=3.0, mezcla=0.38), 1.0),
                                 en(1.1, pico(reverb(onda, 0.35, 3.0, 4500), 0.95))), limite=0.5)

# El reloj del sello: un 'toc' hondo de piedra con un poco de jade.
toc = modos(150, 0.5, ((1, 1.0), (1.62, 0.6), (2.43, 0.4), (3.7, 0.2)), 0.05)
clic = pb(ruido(0.01), 3000) * caida(0.01, 0.0015)
guardar('reloj', reverb(mezclar(pico(toc, 1.0), pico(clic, 0.5), pico(jade(600, None, 0.18, JADE, 0.6), 0.2),
                                pico(boom(95, 70, 0.04), 0.6)), 0.18, 0.9), alto=0.85)

# ======================================================================
#  CATACLISMO DE JADE: se encabrita, ruge al cielo y el cielo se oscurece.
#  Luego el cielo se rasga, caen fragmentos de jade envueltos en fuego
#  verde y revientan donde estaban las marcas.
# ======================================================================
d = 6.0
n = n_(d)
t = t_(d)
encabrita = moler(1.0, 1.4, (14, 40), 0.6, velocidad=curva(n_(1.0), [(0, 0.5), (1, 1.3)])) * ventana(1.0, 0.2, 0.3)
oscurece_env = np.interp(t, [0, 0.8, 4.5, d], [0, 0.3, 1.0, 0])
oscurece = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 2500), (1, 260)]), 'low', 1.0) * oscurece_env
zumba = maldicion(d, 41.2) * oscurece_env
hondo = retumbo(d, 90, 0.8, 0.4) * oscurece_env
cruje_cielo = pb(mezclar(destellos(2.0, 30), en(0.4, rajar_roca(6, 0.6, 1.5, 0.6))), 5000)
ruge = rugido(3.8, 64, 118, abre=1.1, sube=0.3, cola=2.6, contorno=[(0, 64 / 118), (0.3, 1.0), (0.6, 1.08), (0.85, 1.0), (1, 0.7)])
guardar('cataclismo', mezclar(pico(reverb(encabrita, 0.25, 2.0), 0.4), en(0.6, pico(ruge, 1.0)),
                              pico(reverb(mezclar(pico(oscurece, 0.6), pico(zumba, 0.5), pico(hondo, 0.6)), 0.35, 2.8), 0.55),
                              en(3.8, pico(reverb(cruje_cielo, 0.5, 3.0), 0.15))), limite=0.55)

# El cielo se rasga: un desgarro de chasquidos cada vez mas seguidos que
# barre de grave a agudo, el trueno que rueda y el cielo de jade que se
# raja en cristal.
d = 4.5
n = n_(d)
t = t_(d)
tasa = np.interp(t, [0, 0.4, 1.0, 1.8, 3.0, d], [30, 400, 1600, 900, 150, 0])
rasga = crepitar(d, tasa, curva(n, [(0, 400), (0.3, 1800), (0.6, 1100), (1, 500)]), 1.0)
trueno_env = np.interp(t, [0, 0.3, 1.2, 2.5, d], [0, 0.6, 1.0, 0.5, 0])
trueno = retumbo(d, 160, 4.0, 0.6) * trueno_env
cristal = mezclar(pico(destellos(d, 300 * np.exp(-t / 1.0) + 20, 2000, 9000, (0.1, 0.5)), 1.0),
                  en(0.35, pico(rajar_roca(18, 0.4, 1.6, 0.6), 0.6)),
                  en(0.8, pico(jade(98, None, 2.0, JADE_TALLA, 0.3), 0.5)), en(1.0, pico(jade(147, None, 1.8, JADE_TALLA, 0.3), 0.4)))
guardar('cielo', reverb(mezclar(pico(rasga, 0.8), pico(trueno, 0.9), pico(cristal, 0.4), pico(boom(55, 22, 0.6), 0.45)),
                        0.4, 3.0, 5000), limite=0.55)

# Un fragmento que cae: el aire que ruge al paso (la banda baja con el
# Doppler a medida que se acerca), el fuego verde que lo envuelve y el
# jade que chisporrotea con el calor; cada vez mas fuerte.
for i in range(2):
    d = 2.2
    n = n_(d)
    t = t_(d)
    cerca = (t / d) ** 2
    aire = filtro_mov(ruido(d, 'rosa'), curva(n, [(0, 2600 + 200 * i), (1, 650)]), 'band', 1.3) * (0.15 + 0.85 * cerca)
    fuego = llama(d, 1.0, 11, curva(n, [(0, 0.6), (1, 1.3)])) * (0.2 + 0.8 * cerca)
    ruge = pa(pb(ruido(d, 'marron'), 160), 28) * cerca
    chispea = pb(destellos(d, 25 + 60 * cerca, 2000, 6000, (0.03, 0.1))[:n], 7000)
    silba = filtro_mov(ruido(d), curva(n, [(0, 1700 + 150 * i), (1, 850)]), 'band', 20) * cerca
    capas = mezclar(pico(aire, 0.7), pico(fuego, 0.7), pico(ruge, 0.6), pico(chispea, 0.12), pico(silba, 0.08))
    guardar('fragmento', reverb(capas[:n] * ventana(d, 0.35, 0.06), 0.25, 2.2), i + 1, alto=0.85)
# El impacto: explosion, el fragmento que estalla en cristal, el fuego que
# se abre y los escombros.
for i in range(3):
    d = 2.0
    t = t_(d)
    golpe = golpe_tierra(1.8 + 0.1 * i, 1.2, 1.3, 3.0)
    rebufo = filtro_mov(ruido(d, 'rosa'), curva(n_(d), [(0, 300), (0.05, 4000), (0.4, 900), (1, 250)]), 'low', 0.9)
    rebufo *= np.interp(t, [0, 0.05, 0.4, d], [0, 1, 0.45, 0]) ** 1.3
    vidrio = mezclar(pico(rajar_roca(20, 0.04, 1.6, 0.6), 1.0), pico(esquirlas(40, 0.5, 1800, 8000), 0.8),
                     en(0.3, pico(esquirlas(20, 1.2, 2500, 7000), 0.35)))
    fuego = llama(1.8, 1.0, 14) * caida(1.8, 0.4, 0.005)
    guardar('impacto', reverb(mezclar(pico(golpe, 1.0), pico(rebufo, 0.6), pico(vidrio, 0.5), pico(fuego, 0.4)), 0.3, 2.4),
            i + 1, limite=0.5)
# La marca en el suelo: un toque de cristal y el zumbido del glifo.
for i in range(2):
    d = 1.4
    t = t_(0.8)
    ping = mezclar(pico(jade(1320 + 180 * i, None, 0.5, JADE, 1.0), 1.0), en(0.03, pico(jade(660 + 90 * i, None, 0.7, JADE, 0.5), 0.6)))
    zumba = canto_jade(d, 165 * (1 + 0.1 * i), JADE[:2], 120) * ventana(d, 0.15, 0.6)
    quema = grava(0.8, 300 * np.exp(-t / 0.2), (0.4, 1.2))
    guardar('marca', reverb(mezclar(pico(ping, 0.7), pico(zumba, 0.5), pico(quema, 0.15)), 0.3, 2.0), i + 1, techo=-19.0)

# ======================================================================
#  FASE IV: salta y cae como una montana
# ======================================================================
for i in range(2):
    rasca = moler(0.3, 1.2, (40, 90), 1.0) * caida(0.3, 0.1)
    empuje = golpe_tierra(0.9, 0.8, 0.6, 1.5)
    aire = pasada(0.9, 250, 1200 + 100 * i, 1.2, 0.1)
    esfuerzo = bufido(78 + 6 * i, 0.4, 0.5)
    guardar('salto', reverb(mezclar(pico(rasca, 0.4), en(0.03, pico(empuje, 1.0)), en(0.08, pico(aire, 0.55)),
                                    en(0.02, pico(esfuerzo, 0.6))), 0.25, 1.8), i + 1, limite=0.6)
for i in range(2):
    golpe = golpe_tierra(1.9 + 0.1 * i, 1.5, 1.4, 3.0)
    traseras = golpe_tierra(1.2, 0.8, 0.6, 1.5)
    unas = mezclar(*[en(0.006 * k, jade(rng.uniform(1600, 2400), None, 0.03, JADE_TALLA, 1.0)) for k in range(4)])
    guardar('aterriza', reverb(mezclar(pico(golpe, 1.0), en(0.13 + 0.03 * i, pico(traseras, 0.6)), pico(unas, 0.15)), 0.28, 2.2),
            i + 1, limite=0.5)

# ======================================================================
#  ATURDIDO: cae de lado; la piedra gime tambaleandose, los cristales del
#  lomo tiemblan y suenan, y se queja hondo.
# ======================================================================
d = 3.8
n = n_(d)
t = t_(d)
bambolea = 1 + 0.25 * np.sin(2 * np.pi * 1.6 * t)
gime = filtro_mov(moler(d, 1.5, (8, 20), 0.4), 260 * bambolea, 'band', 1.5) * ventana(d, 0.1, 1.2) * (0.6 + 0.4 * bambolea)
cristales = mezclar(*[en(s, jade(rng.uniform(1400, 3000), None, 0.9, JADE, 0.4)) for s in np.sort(rng.uniform(0.1, 2.4, 7))])
cristales = cristales * (1 + 0.5 * np.sin(2 * np.pi * 7 * np.arange(len(cristales)) / SR))
queja = garganta(curva(n_(2.6), [(0, 58), (1, 44)]), 2.6, formantes_felino(0.2), 0.7, 0.5, 0.05, 0.6, 3000, fritura=0.3,
                 pecho=0.5) * ventana(2.6, 0.2, 1.4)
guardar('aturdido', reverb(mezclar(pico(golpe_tierra(1.2, 0.8, 0.8, 2.0), 0.8), pico(gime, 0.45), en(0.2, pico(cristales, 0.25)),
                                   en(0.35, pico(queja, 0.55))), 0.3, 2.2), limite=0.55)

# PARALIZADO: el Cataclismo no mato a nadie. La piedra se le traba (el roce
# se frena a sacudidas y cada articulacion se cierra con un golpe), lo
# recorre un crepitar de piedra que se endurece y gime, apagandose.
d = 4.2
n = n_(d)
t = t_(d)
vel = curva(n, [(0, 1.2), (0.25, 0.8), (0.5, 0.3), (0.7, 0.05), (1, 0.0)])
traba = moler(d, 1.4, (12, 35), 0.5, velocidad=vel) * ventana(d, 0.05, 1.0)
cierres = mezclar(*[en(s, mezclar(pico(canto(28, 1.0, False), 1.0), pico(jade(180 + 25 * k, None, 0.5, JADE_TALLA, 0.6), 0.4)))
                    for k, s in enumerate((0.6, 1.3, 2.1))])
petrifica = mezclar(grava(d, 900 * np.interp(t, [0, 0.3, 2.5, d], [0, 1, 0.6, 0]), (0.4, 1.2)),
                    *[en(s, rajar_roca(4, 0.03, 1.2, 0.8) * 0.5) for s in rng.uniform(0.3, 3.0, 8)])
gemido = garganta(curva(n_(2.8), [(0, 52), (0.5, 48), (1, 40)]), 2.8, formantes_felino(0.15), 0.6, 0.5, 0.05, 0.6, 3000,
                  fritura=0.4, pecho=0.5) * ventana(2.8, 0.4, 1.4)
apaga = maldicion(d, 55.0) * np.exp(-t / 1.2)
guardar('paralizado', reverb(mezclar(pico(traba, 0.5), pico(cierres, 0.5), pico(petrifica, 0.3), en(0.8, pico(gemido, 0.55)),
                                     pico(apaga, 0.2)), 0.3, 2.2), limite=0.6)

# CURA: mato a alguien con el Cataclismo. Un arpegio de jade que sube, la
# energia que sube cantando y un gruñido satisfecho.
d = 2.6
notas = (293.7, 349.2, 392.0, 440.0, 523.3, 587.3, 698.5, 880.0)
arpegio = mezclar(*[en(0.08 * k, jade(f, None, 0.7, JADE, 0.6) * (0.5 + 0.5 * k / len(notas))) for k, f in enumerate(notas)])
sube = filtro_mov(ruido(1.4), curva(n_(1.4), [(0, 220), (1, 880)]), 'band', 50) * campana_env(1.4, 1.0)
satisfecho = garganta(curva(n_(1.5), [(0, 50), (0.4, 56), (1, 46)]), 1.5, formantes_felino(0.2), 0.8, 0.5, 0.05, 0.6, 3000,
                      fritura=0.7, fritura_hz=24.0, pecho=0.6) * ventana(1.5, 0.15, 0.7)
guardar('cura', reverb(mezclar(pico(arpegio, 0.6), pico(sube, 0.25), pico(destellos(1.2, 120), 0.15), en(0.65, pico(satisfecho, 0.75))),
                       0.32, 2.2), limite=0.65)

# TAMBALEO: cambia de fase. Una grieta le cruza el cuerpo (todo el jade
# suena), se le caen lascas y ruge.
for i in range(2):
    raja = mezclar(pico(rajar_roca(30, 0.3, 0.9, 0.8), 1.0), pico(boom(72, 30, 0.35), 0.9),
                   pico(retumbo(1.2, 120) * caida(1.2, 0.3), 0.4))
    suena = jade(180 + 20 * i, None, 1.2, JADE_TALLA, 0.8)
    caen = mezclar(pico(esquirlas(14, 0.6, 1500, 6000), 1.0), pico(escombros(2.0, 0.8, 0.45, (0.4, 6.0)), 0.9))
    golpe = reverb(mezclar(raja, pico(suena, 0.35), pico(caen, 0.3)), 0.28, 2.0)
    guardar('tambaleo', mezclar(pico(golpe, 0.9), en(0.4, pico(rugido(2.6, 70 - 4 * i, 112 - 6 * i, cola=2.0), 1.0))), i + 1,
            limite=0.55)

# ======================================================================
#  LIBERACION: el sol maldito del pecho se apaga, las grietas se cierran
#  en oro (chasquidos al reves y una campana honda), la piedra se asienta y
#  suelta todo el aire. Y DISOLVER: se queda quieto, piedra otra vez.
# ======================================================================
d = 7.0
n = n_(d)
t = t_(d)
apaga = maldicion(d, 55.0) * np.interp(t, [0, 0.3, 2.5, 4.0, d], [0.6, 1.0, 0.3, 0.0, 0.0])
baja = filtro_mov(ruido(d), curva(n, [(0, 660), (0.35, 220), (1, 110)]), 'band', 70) * np.interp(t, [0, 0.4, 2.8, 4.5, d], [0, 1, 0.4, 0, 0])
cierran = mezclar(*[en(s, rajar_roca(8, 0.06, 1.0, 0.9)[::-1] * a) for s, a in zip(np.sort(rng.uniform(0.6, 2.2, 7)),
                                                                                       np.linspace(1.0, 0.5, 7))])
campana = campana_oro(146.8, 3.0)
acorde = mezclar(*[en(0.25 * k, jade(f, None, 1.8, JADE, 0.3)) for k, f in enumerate((293.7, 370.0, 440.0, 587.3))])
asientan = mezclar(en(0.2, rodar(1.2, 8, 4, 0.6)), en(1.0, rodar(1.2, 6, 4, 0.4)),
                   grava(3.0, 60 * np.exp(-t_(3.0) / 1.0), (0.4, 3.0)),
                   en(0.4, moler(1.4, 1.6, (8, 20), 0.3) * campana_env(1.4, 1.5) * 0.5))
exhala = respiro(2.8, True, 40.0, 0.35)
guardar('liberacion', reverb(mezclar(pico(apaga, 0.35), pico(baja, 0.2), pico(cierran, 0.3), en(1.6, pico(campana, 0.6)),
                                     en(2.0, pico(acorde, 0.25)), en(3.0, pico(asientan, 0.3)), en(3.3, pico(exhala, 0.55))),
                             0.4, 3.0, 6000))

d = 3.4
t = t_(d)
dl = 2.2
asienta = moler(dl, 1.6, (10, 28), 0.4, velocidad=curva(n_(dl), [(0, 1.0), (0.7, 0.4), (1, 0.0)])) * ventana(dl, 0.1, 0.8)
polvo = pb(ruido(d, 'rosa'), 1400) * np.interp(t, [0, 0.4, 1.5, d], [0, 1, 0.5, 0])
arena = grava(d, 400 * np.interp(t, [0, 0.3, 2.0, d], [0, 1, 0.3, 0]), (0.4, 1.5))
apaga = maldicion(d, 55.0) * np.exp(-t / 0.6)
guardar('disolver', reverb(mezclar(pico(asienta, 0.5), pico(polvo, 0.3), pico(arena, 0.25), pico(apaga, 0.15),
                                   en(2.3, pico(canto(26, 0.8, False), 0.35))), 0.32, 2.2, 5000))

# El zarpazo: la zarpa barre el aire en diagonal y las tres garras de
# obsidiana lo rasgan una tras otra (tres cortes que bajan de tono), con el
# jade de las unas que se queda vibrando y el hombro que cruje al soltarla.
for i in range(2):
    barre = pasada(0.42, 2200 + 200 * i, 380, 1.5, 0.12)
    cortes = mezclar(*[en(0.05 + 0.045 * k, pasada(0.16, 5200 - 700 * k + 300 * i, 1500 - 200 * k, 3.0, 0.5)) for k in range(3)])
    unas = mezclar(*[en(0.06 + 0.045 * k, jade(rng.uniform(1700, 2500), None, 0.08, JADE_TALLA, 1.2)) for k in range(3)])
    hombro = moler(0.35, 1.4, (18, 40), 0.5) * campana_env(0.35, 1.0)
    guardar('zarpazo', reverb(mezclar(pico(barre, 1.0), pico(cortes, 0.8), pico(unas, 0.22), pico(hombro, 0.3),
                                      en(0.04, pico(boom(70, 40, 0.08), 0.35))), 0.22, 1.4), i + 1, limite=0.6)

# ======================================================================
#  MEJORAS DE OCTUBRE DE 2026. Con su propia semilla: anadirlas no cambia
#  los de antes, y rajang_mejoras_sonidos.py las genera sueltas igual que
#  en la pasada entera.
# ======================================================================
rng = np.random.default_rng(20261006)

# EMBESTIDA (aviso): se agazapa gruñendo bajo, rasca dos veces la tierra con
# la zarpa (la piedra que se arrastra, la tierra que se raja, la grava que
# salta) y resopla antes de soltarse.
for i in range(2):
    gru = grunido(1.5, 54 + 4 * i, 0.4, 1.6)
    rascas = []
    for s in (0.38, 0.66):
        raspa = moler(0.26, 1.3, (40, 90), 1.0) * campana_env(0.26, 1.2)
        rascas.append(en(s, mezclar(pico(raspa, 0.8), pico(rajar_roca(5, 0.03, 1.0, 0.9), 0.6),
                                    pico(grava(0.4, 900 * np.exp(-t_(0.4) / 0.08), (0.4, 2.5)), 0.4))))
    sopla = bufido(66 + 6 * i, 0.45, 0.6)
    guardar('embestida_aviso', reverb(mezclar(pico(gru, 0.9), *[pico(r_, 0.55) for r_ in rascas], en(1.05, pico(sopla, 0.8))),
                                      0.22, 1.6), i + 1, limite=0.6)

# EMBESTIDA (carga): una estampida de un animal de ocho bloques. Las cuatro
# zarpas que caen a galope (cuatro golpes seguidos y un hueco), la tierra que
# retumba bajo el, la grava que salta y el aire que arrastra. Arranca con un
# rugido corto.
d = 2.4
t = t_(d)
env = np.interp(t, [0, 0.15, 1.8, d], [0.3, 1.0, 0.9, 0])
tierra = retumbo(d, 95, 3.2, 0.55, 1.0) * env
caidas = []
for k in range(4):
    for j, off in enumerate((0.0, 0.07, 0.27, 0.34)):
        s = 0.12 + k * 0.56 + off + rng.uniform(-0.01, 0.01)
        if s < d - 0.3:
            golpe = mezclar(pico(saturar(boom(78, 34, 0.07), 2.0), 0.8), pico(canto(rng.uniform(18, 26), 0.9, False), 0.7),
                            pico(bp(ruido(0.12, 'rosa'), 120, 900) * caida(0.12, 0.03), 0.6))
            caidas.append(en(s, golpe * (0.75 + 0.25 * (j % 2))))
salta = grava(d, 1100 * env, (0.4, 4.0))
aire = filtro_mov(ruido(d, 'rosa'), curva(n_(d), [(0, 300), (0.5, 900), (1, 400)]), 'band', 1.0) * env
guardar('embestida', reverb(mezclar(pico(rugido(1.2, 66, 104, cola=0.8), 0.8), pico(tierra, 0.6), *[pico(c, 0.55) for c in caidas],
                                    pico(salta, 0.35), pico(aire, 0.25)), 0.22, 1.8), limite=0.5)

# EMBESTIDA (frenada): derrapa con las cuatro zarpas clavadas: la piedra que
# se arrastra cada vez mas despacio, la tierra que se levanta en ola y las
# chinas que saltan; al pararse, resuella dos veces.
d = 2.4
dl = 0.8
arrastra = moler(dl, 1.8, (30, 80), 1.2, velocidad=curva(n_(dl), [(0, 1.4), (0.6, 0.8), (1, 0.1)])) * ventana(dl, 0.02, 0.3)
ola = pb(ruido(1.2, 'rosa'), 1600) * np.interp(t_(1.2), [0, 0.1, 0.6, 1.2], [0, 1, 0.5, 0])
chinas = grava(1.2, 1400 * np.exp(-t_(1.2) / 0.3), (0.4, 3.5))
jadeo = mezclar(en(0.0, respiro(0.5, True, 52.0, 0.5)), en(0.6, respiro(0.45, False)), en(1.05, respiro(0.5, True, 50.0, 0.5)))
guardar('embestida_frena', reverb(mezclar(pico(arrastra, 0.9), pico(ola, 0.4), pico(chinas, 0.4), en(0.9, pico(jadeo, 0.55))),
                                  0.22, 1.6), limite=0.55)

# ESTAMPADO: la carga contra un muro. El golpe de la cabeza de jade contra la
# piedra, el muro que se raja, lo que cae, el jade que se queda vibrando y una
# queja aturdida.
d = 2.4
choque = golpe_tierra(1.8, 1.6, 1.2, 2.4)
timbre = jade(rng.uniform(420, 520), None, 0.6, JADE_TALLA, 1.0)
muro = mezclar(*[en(s, rajar_roca(int(rng.integers(6, 12)), 0.05, 1.0, 0.9)) for s in np.sort(rng.uniform(0.02, 0.4, 4))])
queja = quejido(0.9, 88)
guardar('estampado', reverb(mezclar(pico(choque, 1.0), pico(timbre, 0.3), pico(muro, 0.5), en(0.55, pico(queja, 0.8))), 0.25, 2.0),
        limite=0.5)

# TUMBA DE RAICES: clava las garras y ruge contra el suelo (la voz ahogada
# por la tierra), y la tierra contesta: un retumbo que crece, las raices que
# se rajan cada vez mas deprisa y la maldicion que sube de tono. 3,5 s
# exactos hasta el estallido.
d = 3.8
n = n_(d)
t = t_(d)
crece = np.interp(t, [0, 0.4, 3.4, 3.5, d], [0.1, 0.3, 1.0, 1.0, 0])
tierra = retumbo(d, 90, 2.0, 0.6, 1.2) * crece
raices = crepitar(d, 30 + 700 * np.clip(t / 3.5, 0, 1) ** 2, curva(n, [(0, 600), (0.9, 2600), (1, 2600)]), 1.4) * crece
hum = maldicion(d, 55.0, 1.0) * crece
voz = pb(rugido(3.3, 58, 92, cola=1.0, mezcla=0.2), 1300)
guardar('tumba', reverb(mezclar(pico(tierra, 0.6), pico(raices, 0.35), pico(hum, 0.3), en(0.2, pico(voz, 0.9))), 0.3, 2.2, 4500),
        limite=0.5)

# TUMBA (estallido): el circulo se llena y la tierra revienta: el golpe hondo,
# las raices de piedra que brotan por todas partes, la roca que se raja y lo
# que llueve.
d = 3.0
golpe = golpe_tierra(2.2, 1.8, 1.6, 3.0)
brotan = mezclar(*[en(s, brota(rng.uniform(0.25, 0.4), 1300, rng.uniform(220, 380), 1.2) * rng.uniform(0.6, 1.0))
                   for s in np.sort(rng.uniform(0.0, 0.35, 8))])
rajas = mezclar(*[en(s, rajar_roca(int(rng.integers(8, 16)), 0.06, 1.0, 0.8)) for s in rng.uniform(0.0, 0.5, 6)])
guardar('tumba_estalla', reverb(mezclar(pico(golpe, 1.0), pico(brotan, 0.6), pico(rajas, 0.45)), 0.3, 2.4, 5000), limite=0.45)

# FURIA DE JADE: la maldicion lo prende entero. Un rugido mas agudo y aspero,
# el fuego verde que le corre por las grietas y la nota de la maldicion que
# sube.
d = 3.6
t = t_(d)
fuego = llama(d, 1.3, 13.0, 1.2) * np.interp(t, [0, 0.4, 2.8, d], [0, 1, 0.8, 0])
hum = maldicion(d, 62.0, 1.3) * np.interp(t, [0, 0.6, 3.0, d], [0, 1, 0.7, 0])
guardar('furia', reverb(mezclar(pico(rugido(3.2, 74, 122, cola=1.6), 1.0), pico(fuego, 0.5), pico(hum, 0.3),
                                en(0.1, pico(glifo(260, 1.0, 1.4), 0.35))), 0.3, 2.2), limite=0.5)

# ESCALON QUE TIEMBLA: la piedra que se suelta: un roce que va y viene, los
# crujidos y un hilo de arenilla que cae.
for i in range(2):
    d = 1.2
    t = t_(d)
    vaiven = 0.5 + 0.5 * np.sin(2 * np.pi * (9 + 2 * i) * t)
    roce = moler(d, 0.9, (25, 60), 0.6) * vaiven * np.interp(t, [0, 0.2, 1.0, d], [0.3, 1.0, 1.0, 0.6])
    crujen = mezclar(*[en(s, rajar_roca(int(rng.integers(3, 6)), 0.03, 1.0, 1.0)) for s in np.sort(rng.uniform(0.1, 1.0, 4))])
    arenilla = grava(d, 250 + 250 * vaiven, (0.4, 1.2))
    guardar('escalon_tiembla', reverb(mezclar(pico(roce, 0.7), pico(crujen, 0.5), pico(arenilla, 0.3)), 0.2, 1.4), i + 1,
            limite=0.6)

# ESCALON QUE SE CAE: se suelta de golpe, cae silbando y se rompe abajo.
for i in range(2):
    suelta = mezclar(pico(rajar_roca(8, 0.04, 1.0, 0.9), 1.0), pico(boom(120, 60, 0.06), 0.5))
    silba = pasada(0.7, 1800 + 200 * i, 400, 1.6, 0.1)
    rompe = mezclar(pico(golpe_tierra(0.9, 1.0, 0.8, 1.4), 1.0), en(0.05, pico(rodar(1.0, 12, 5, 0.6), 0.4)))
    guardar('escalon_cae', reverb(mezclar(pico(suelta, 0.7), en(0.05, pico(silba, 0.4)), en(0.75, pico(rompe, 0.8))), 0.22, 1.6),
            i + 1, limite=0.55)

# PULSO DEL TOTEM: el totem se rompe y suelta la tierra que sujetaba de
# golpe: un golpe de presion hondo, el aire que barre hacia fuera y el jade
# que se queda cantando.
d = 2.2
t = t_(d)
golpe = saturar(boom(68, 26, 0.3), 2.6)
barre = filtro_mov(ruido(d, 'rosa'), curva(n_(d), [(0, 180), (0.15, 1500), (1, 200)]), 'band', 1.2)
barre *= np.interp(t, [0, 0.08, 0.6, d], [0, 1, 0.3, 0])
canta = jade(rng.uniform(300, 360), None, 1.1, JADE, 0.8)
guardar('totem_pulso', reverb(mezclar(pico(golpe, 0.9), pico(barre, 0.6), pico(canta, 0.3),
                                      pico(rajar_roca(10, 0.05, 1.0, 0.8), 0.5)), 0.28, 2.0), limite=0.5)

# ----------------------------------------------------------------------
#  sounds.json: los eventos rajang.* con sus variantes y subtitulo
# ----------------------------------------------------------------------
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for k in [k for k in datos if k.startswith('rajang.')]:
    del datos[k]
for ev, archivos in EVENTOS.items():
    datos['rajang.' + ev] = {'subtitle': 'subtitles.atalaya.rajang.' + ev,
                             'sounds': ['atalaya:rajang/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')

# ----------------------------------------------------------------------
#  Subtitulos (los copia quien toque los idiomas): es_es y en_us
# ----------------------------------------------------------------------
SUBTITULOS = {
    'ambiente': ('Rajang respira hondo', 'Rajang breathes deeply'),
    'dormido': ('Rajang duerme como piedra', 'Rajang slumbers like stone'),
    'paso': ('Pisadas de Rajang', 'Rajang stomps'),
    'herido': ('Rajang recibe el golpe', 'Rajang is hit'),
    'inmune': ('El golpe resbala sobre el jade', 'The blow glances off the jade'),
    'despertar': ('Rajang despierta', 'Rajang awakens'),
    'rugido': ('Rajang ruge', 'Rajang roars'),
    'grunido': ('Rajang gruñe', 'Rajang snarls'),
    'garra_alza': ('Rajang alza la garra', 'Rajang raises its claw'),
    'garra_golpe': ('La garra golpea la tierra', 'Claw strikes the ground'),
    'grieta': ('Corre una grieta por el suelo', 'A crack races across the ground'),
    'pico': ('Brotan picos de roca', 'Rock spikes erupt'),
    'pico_golpe': ('Un pico de roca te lanza', 'A rock spike launches you'),
    'terremoto': ('La tierra tiembla', 'The earth quakes'),
    'onda': ('Pasa una onda sísmica', 'A shockwave passes'),
    'pilar': ('Revienta una columna de roca', 'A rock pillar bursts out'),
    'aviso': ('Se enciende un glifo en el suelo', 'A glyph glows on the ground'),
    'piel_jade': ('La piel de Rajang se endurece', "Rajang's hide hardens"),
    'lastre': ('Un lastre de piedra te hunde', 'A stone weight drags you down'),
    'sello': ('Se alza el Sello de la Tierra', 'The Earth Seal rises'),
    'plataforma': ('La tierra se eleva', 'The earth rises'),
    'totem': ('Zumba un tótem', 'A totem hums'),
    'totem_golpe': ('Cruje un tótem', 'A totem cracks'),
    'totem_roto': ('Se rompe un tótem', 'A totem shatters'),
    'totem_rehace': ('Un tótem se rehace', 'A totem reforms'),
    'columna': ('Se alzan las columnas del Sello', 'The Seal columns rise'),
    'rugido_jade': ('El Rugido de Jade', 'The Jade Roar'),
    'reloj': ('Late el sello', 'The seal ticks'),
    'cataclismo': ('Rajang ruge al cielo', 'Rajang roars at the sky'),
    'cielo': ('El cielo se rasga', 'The sky tears open'),
    'fragmento': ('Cae un fragmento de jade', 'A jade fragment falls'),
    'impacto': ('Revienta un fragmento de jade', 'A jade fragment crashes'),
    'marca': ('Aparece una marca', 'A mark appears'),
    'salto': ('Rajang salta', 'Rajang leaps'),
    'aterriza': ('Rajang cae a plomo', 'Rajang lands'),
    'aturdido': ('Rajang queda aturdido', 'Rajang is stunned'),
    'paralizado': ('Rajang queda paralizado', 'Rajang is paralyzed'),
    'cura': ('Rajang se cura', 'Rajang heals'),
    'tambaleo': ('Rajang se tambalea', 'Rajang staggers'),
    'liberacion': ('Rajang queda libre', 'Rajang is freed'),
    'disolver': ('Rajang vuelve a la piedra', 'Rajang turns to stone'),
    'zarpazo': ('Rajang lanza un zarpazo', 'Rajang swipes its claw'),
    'embestida_aviso': ('Rajang rasca la tierra', 'Rajang paws the ground'),
    'embestida': ('Rajang embiste', 'Rajang charges'),
    'embestida_frena': ('Rajang derrapa', 'Rajang skids to a halt'),
    'estampado': ('Rajang se estampa', 'Rajang crashes into a wall'),
    'tumba': ('La tierra se llena de raíces', 'Roots spread through the earth'),
    'tumba_estalla': ('Revientan las raíces', 'The roots burst out'),
    'furia': ('Rajang se enfurece', 'Rajang flies into a rage'),
    'escalon_tiembla': ('Tiembla un escalón', 'A step shakes'),
    'escalon_cae': ('Se cae un escalón', 'A step falls'),
    'totem_pulso': ('Un pulso de tierra', 'An earth pulse'),
}
faltan = [ev for ev in EVENTOS if ev not in SUBTITULOS]
assert not faltan, f'eventos sin subtitulo: {faltan}'
subs = collections.OrderedDict()
for idioma, j in (('es_es', 0), ('en_us', 1)):
    subs[idioma] = collections.OrderedDict(('subtitles.atalaya.rajang.' + ev, SUBTITULOS[ev][j]) for ev in EVENTOS)
with open(os.path.join(RAIZ, 'materiales/generadores/rajang_subtitulos.json'), 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(subs, fh, indent=2, ensure_ascii=False)
    fh.write('\n')

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
        hoja.paste(Image.merge('RGB', (im.point(lambda v: int(v * 0.6)), im, im.point(lambda v: int(v * 0.8)))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9):.0f}dB',
                 fill=(220, 220, 220))
    hoja.save(sys.argv[2])
