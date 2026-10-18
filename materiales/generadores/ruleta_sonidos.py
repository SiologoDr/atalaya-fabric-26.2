"""
Los sonidos de la Ruleta (17-10-2026), la tragaperras de los cambios de dificultad. Juan: «esa animación tiene que ser
fluida y con sonido de casino»; y en la segunda versión, «que aparezca ya girando, más inmersivo y que dé esa tensión;
más rápido el giro y que dure el doble o un poco más». Todo nuestro, hecho de cosas de verdad (el trinquete del
rodillo, el tambor, las bombillas, el corazón) y de la música de las máquinas (las campanitas, el redoble, el timbre).
El rodillo suena a la par de lo que se ve: cada diente que pasa es un clic y cada icono, una nota, sacados de la misma
curva que mueve el rodillo en RuletaCliente.

  ruleta.animacion    0-170: el medallón entra con un golpe, ya girando a tope; se encienden las bombillas de una
                      pasada. El rodillo: el tambor que zumba, los dientes (un ronroneo deprisa; tic... tic... al
                      frenar) y las campanitas, que deprisa dan vueltas a un arpegio y al frenar suben nota a nota.
                      Mientras frena, una subida que aprieta; desde 126, el corazón cada vez más seguido; casi parado
                      en el señuelo, un redoble de campanitas que crece; un instante de silencio y, en 170, el cerrojo
  ruleta.mob          170, si para en el huevo: el cascarón que se raja, unas notas que suben como una pregunta y el
                      piar de algo que nace
  ruleta.dificultad   170, en la advertencia: el timbre de alarma y dos golpes de metales graves que avisan
  ruleta.penalizacion 170, en la penalización: el «uah, uah, uaaah» de la mala suerte, con una cadena y hielo
  ruleta.minijuego    170, en el minijuego: un arpegio de recreativa que sube y el acorde de «¡a jugar!»
  ruleta.sale         200: el medallón se va y el icono vuela al chat
  ruleta.aviso        206, con el aviso del chat: el «¡din-din!» de un timbre de mostrador

Usa las utilidades de minijefes_sonidos.py. Uso: python ruleta_sonidos.py <raiz> [hoja]
"""
import math
import sys

import numpy as np

import minijefes_sonidos as ms
from minijefes_sonidos import (SR, bp, caida, curva, en, filtro_mov, mezclar, modos, n_, pa, pb, pico, resonar, reverb,
                               ruido, saturar, t_, ventana)

ms.SUBTITULOS['ruleta'] = {
    'animacion': ('Gira una tragaperras', 'A slot machine spins'),
    'mob': ('Se raja un cascarón', 'An eggshell cracks'),
    'dificultad': ('Suena una alarma', 'An alarm rings'),
    'penalizacion': ('La mala suerte', 'Bad luck'),
    'minijuego': ('¡A jugar!', "Let's play!"),
    'sale': ('La tragaperras se va', 'The slot machine leaves'),
    'aviso': ('Suena un timbre', 'A bell dings'),
    'enciende': ('Se enciende un interruptor', 'A switch turns on'),
    'apaga': ('Se apaga un interruptor', 'A switch turns off'),
}
ms.SALAS['ruleta'] = ('plaza', 8000)


def s_(tick):
    return tick / 20.0


# ----------------------------------------------------------------------------------------------------------------
#  El calendario (ticks) y el rodillo: lo mismo que RuletaCliente
# ----------------------------------------------------------------------------------------------------------------
T_ENTRA = 8
T_FRENA = 60
T_LENTO = 128
T_PARA = 170
T_SALE = 200
T_AVISO = 206
LATIDOS = (126, 137, 146, 153, 159, 164, 168)
BOMBILLAS = 22
# La curva del rodillo: (tick, posición en iconos, velocidad en iconos por tick). Entre dos puntos, una cúbica de
# Hermite. Sale ya a tope, frena, pasa despacio un par de iconos, se queda casi parado en el señuelo y pasa al bueno.
RODILLO = [(0, 0.0, 1.8), (60, 108.0, 1.8), (128, 161.5, 0.12), (146, 162.82, 0.03), (156, 163.02, 0.005),
           (170, 164.0, 0.0)]
DIENTES = 4


def posicion(t):
    """Dónde va el rodillo (iconos desde que sale) en el tick t."""
    if t <= RODILLO[0][0]:
        return RODILLO[0][2] * t
    for (t0, p0, v0), (t1, p1, v1) in zip(RODILLO, RODILLO[1:]):
        if t <= t1:
            h = t1 - t0
            s = (t - t0) / h
            s2, s3 = s * s, s * s * s
            return ((2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * h * v0 + (-2 * s3 + 3 * s2) * p1
                    + (s3 - s2) * h * v1)
    return RODILLO[-1][1]


def velocidad(t, dt=0.01):
    return (posicion(t + dt) - posicion(t - dt)) / (2 * dt)


def cruces(paso):
    """Los momentos (s) en que el rodillo pasa por cada múltiplo de 'paso' (iconos), con su índice."""
    ts = np.arange(0, T_PARA * 64 + 1) / 64.0
    ps = np.array([posicion(t) for t in ts])
    k = np.floor(ps / paso + 1e-9)
    out = []
    for i in np.nonzero(np.diff(k) > 0)[0]:
        # dentro del intervalo, donde cruza de verdad
        p0, p1 = ps[i], ps[i + 1]
        meta = k[i + 1] * paso
        f = (meta - p0) / (p1 - p0) if p1 > p0 else 0.0
        out.append((s_(ts[i] + f / 64.0), int(k[i + 1])))
    return out


# ----------------------------------------------------------------------------------------------------------------
#  Los instrumentos
# ----------------------------------------------------------------------------------------------------------------
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def campanita(f, fuerza=1.0, tau=0.22, dur=0.7):
    """Una campanita de celesta (las notas del giro)."""
    x = modos(f, dur, ((1, 1.0), (2.0, 0.16), (2.76, 0.2), (5.4, 0.07), (8.93, 0.03)), tau)
    return x / (np.max(np.abs(x)) + 1e-9) * fuerza


def marimba(f, fuerza=1.0, dur=0.9):
    """Una láminas de madera (la pregunta del huevo): cálidas y cortas."""
    x = modos(f, dur, ((1, 1.0), (3.93, 0.28), (9.2, 0.08)), 0.32)
    golpe = bp(ruido(0.008), f * 2, min(f * 8, 12000)) * caida(0.008, 0.0015) * 0.3
    x = mezclar(x / (np.max(np.abs(x)) + 1e-9), golpe)
    return x * fuerza


def clic(fuerza=1.0, claro=1.0):
    """Un diente del trinquete: un golpecito duro con su chasquido de plástico."""
    x = bp(ruido(0.014), 1500 * claro, 7500) * caida(0.014, 0.0016)
    x = mezclar(x, 0.6 * modos(2300 * claro, 0.03, ((1, 1.0), (2.37, 0.45), (3.9, 0.2)), 0.007))
    return pico(x, fuerza)


def clinc(f=3150.0, fuerza=1.0, tau=0.16, dur=0.7):
    """La moneda contra el metal: parciales altos y desafinados entre sí."""
    x = modos(f, dur, ((1, 1.0), (1.53, 0.7), (2.41, 0.45), (3.37, 0.28), (4.62, 0.16)), tau, batido=0.002)
    golpe = bp(ruido(0.006), 3500, 12000) * caida(0.006, 0.0012)
    return pico(mezclar(x / (np.max(np.abs(x)) + 1e-9), golpe * 0.8), fuerza)


def golpe_grave(f0=95.0, f1=42.0, tau=0.12, fuerza=1.0):
    """El golpe sordo de algo pesado (la máquina que cae, el cerrojo)."""
    dur = tau * 6
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.4))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    x += 0.4 * pb(ruido(dur), 400) * np.exp(-t / (tau * 0.3))
    return pico(x, fuerza)


def chapa(dur=0.45, fuerza=1.0):
    """La chapa del mueble que vibra con el golpe."""
    r = ruido(dur)
    x = resonar(r, 310, 30) + 0.8 * resonar(r, 740, 40) + 0.5 * resonar(r, 1630, 50) + 0.3 * resonar(r, 2950, 60)
    return pico(x * caida(dur, dur * 0.22), fuerza)


def clanc(fuerza=1.0):
    """Hierro contra hierro (la palanca que llega abajo, el cerrojo del rodillo)."""
    x = modos(520, 0.6, ((1, 1.0), (1.71, 0.6), (2.63, 0.45), (3.8, 0.25), (5.2, 0.12)), 0.09, batido=0.004)
    golpe = bp(ruido(0.01), 1200, 9000) * caida(0.01, 0.002)
    return pico(mezclar(x / (np.max(np.abs(x)) + 1e-9), golpe), fuerza)


def muelle(dur=0.5, fuerza=1.0):
    """El muelle de la palanca que vuelve: un «boing» metálico que tiembla."""
    t = t_(dur)
    f = 150 * (1 + 0.28 * np.exp(-t / 0.12) * np.sin(2 * np.pi * 11 * t))
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(fase) + 0.35 * np.sin(2.76 * fase) + 0.2 * np.sin(5.1 * fase)) * np.exp(-t / 0.16)
    x += 0.3 * bp(ruido(dur), 2000, 6000) * np.exp(-t / 0.02)
    return pico(x, fuerza)


def zumbido(dur, f=100.0):
    """El zumbido eléctrico de la máquina encendida."""
    t = t_(dur)
    x = sum(np.sin(2 * np.pi * f * k * t + k) / k ** 1.2 for k in range(1, 12))
    return x / np.max(np.abs(x))


def soplo(dur, f0, f1, fuerza=1.0, q=1.4):
    """Aire que pasa, con su tono moviéndose (de f0 a f1)."""
    fc = curva(n_(dur), [(0, f0), (1, f1)])
    x = filtro_mov(ruido(dur), fc, tipo='band', q=q)
    return pico(x * ventana(dur, dur * 0.35, dur * 0.5), fuerza)


def sierra(f, dur, voces=3, desafina=0.008):
    t = t_(dur)
    x = np.zeros_like(t)
    for v in range(voces):
        d = 1 + desafina * (v - (voces - 1) / 2)
        fase = (f * d * t + 0.13 * v) % 1.0
        x += 2 * fase - 1
    return pb(x / voces, 7000)


def cuadrada(f, dur):
    """Una cuadrada sin aristas (los armónicos impares hasta 9 kHz): la voz de la recreativa."""
    t = t_(dur)
    x = np.zeros_like(t)
    k = 1
    while f * k < 9000:
        x += np.sin(2 * np.pi * f * k * t) / k
        k += 2
    return x * (4 / np.pi)


def cascara(fuerza=1.0, granos=9, largo=0.05):
    """El cascarón que se raja: un racimo de chasquidos secos."""
    x = np.zeros(n_(largo + 0.05))
    r = np.random.default_rng(int(fuerza * 1000) + granos)
    for _ in range(granos):
        i = int(r.uniform(0, largo) * SR)
        c = bp(ruido(0.006), r.uniform(1800, 3500), 9000) * caida(0.006, 0.0008) * r.uniform(0.4, 1.0)
        x[i:i + len(c)] += c
    x += 0.5 * resonar(x, 2600, 8)
    return pico(x, fuerza)


def piar(dur=0.18, fuerza=1.0, f0=1500.0, f1=2600.0):
    """El piar de algo pequeño que acaba de nacer."""
    t = t_(dur)
    f = f0 + (f1 - f0) * np.sin(np.pi * t / dur * 0.5) ** 2 + 120 * np.sin(2 * np.pi * 28 * t)
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(fase) + 0.3 * np.sin(2 * fase)) * ventana(dur, 0.02, 0.08)
    return pico(x, fuerza)


def timbre_alarma(dur=0.95, f=2050.0, golpes=21.0, fuerza=1.0):
    """El timbre eléctrico: el martillo que golpea la campana muy deprisa («rrrrring»)."""
    t = t_(dur)
    x = np.zeros_like(t)
    n = int(dur * golpes)
    toque = modos(f, 0.25, ((1, 1.0), (1.47, 0.5), (2.09, 0.35), (2.56, 0.2), (3.97, 0.1)), 0.05, batido=0.003)
    for i in range(n):
        j = int(i / golpes * SR)
        seg = toque[:max(0, len(x) - j)] * (0.75 + 0.25 * ((i % 2) == 0))
        x[j:j + len(seg)] += seg
    return pico(x * ventana(dur, 0.005, 0.18), fuerza)


def metales(notas, dur, fuerza=1.0, abre=2600.0):
    """Un golpe de metales graves: un acorde de sierras que se abre y se cierra («¡buaamp!»)."""
    x = sum(sierra(midi(m), dur, voces=3, desafina=0.01) for m in notas)
    fc = curva(n_(dur), [(0, 300), (0.08, abre), (0.5, abre * 0.45), (1, 260)])
    x = filtro_mov(x, fc, tipo='low', q=1.1)
    return pico(saturar(x * ventana(dur, 0.012, dur * 0.5), 1.6), fuerza)


def uah(f, dur, fuerza=1.0, vibrato=0.0):
    """Una nota con sordina que hace «uah» (la mala suerte): sierra con un filtro que se abre y se cierra."""
    t = t_(dur)
    fv = f * (1 + vibrato * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.3, 0, 1))
    fase = np.cumsum(fv) / SR
    x = 2 * (fase % 1.0) - 1
    x = pb(x, 6000)
    fc = curva(n_(dur), [(0, 380), (0.3, 1500), (1, 520)])
    x = filtro_mov(x, fc, tipo='band', q=2.2) + 0.25 * filtro_mov(x, fc * 2.1, tipo='band', q=3)
    return pico(x * ventana(dur, 0.02, dur * 0.35), fuerza)


def cadena(dur=0.3, fuerza=1.0, eslabones=7):
    """Una cadena que suena: eslabones que chocan."""
    x = np.zeros(n_(dur + 0.4))
    r = np.random.default_rng(eslabones)
    for i in range(eslabones):
        j = int(r.uniform(0, dur) * SR)
        c = clinc(r.uniform(2200, 3600), r.uniform(0.3, 0.8), tau=0.05, dur=0.25)
        x[j:j + len(c)] += c
    return pico(x, fuerza)


def hielo(dur=1.4, fuerza=1.0):
    """Un brillo de hielo: parciales de cristal muy altos que se apagan."""
    x = np.zeros(n_(dur))
    r = np.random.default_rng(7)
    for i in range(14):
        j = int(r.uniform(0, dur * 0.4) * SR)
        c = modos(r.uniform(4200, 9000), dur * 0.6, ((1, 1.0), (2.32, 0.3)), 0.25)
        seg = c[:max(0, len(x) - j)] * r.uniform(0.2, 0.6)
        x[j:j + len(seg)] += seg
    return pico(x, fuerza)


def destellos(dur, cuantos, fmin=5000.0, fmax=10000.0, semilla=3):
    """Brillitos sueltos (monedas, chispas)."""
    x = np.zeros(n_(dur + 0.3))
    r = np.random.default_rng(semilla)
    for i in range(cuantos):
        j = int(r.uniform(0, dur) * SR)
        c = modos(r.uniform(fmin, fmax), 0.25, ((1, 1.0), (2.1, 0.3)), 0.06) * r.uniform(0.3, 1.0)
        x[j:j + len(c)] += c
    return pico(x, 1.0)


def poner(x, seg, señal, g=1.0):
    """Suma la señal en x a partir del segundo seg (x crece si hace falta)."""
    i = n_(seg) if seg > 0 else 0
    fin = i + len(señal)
    if fin > len(x):
        x = np.concatenate([x, np.zeros(fin - len(x))])
    x[i:fin] += g * señal
    return x


# ----------------------------------------------------------------------------------------------------------------
#  Los sonidos
# ----------------------------------------------------------------------------------------------------------------
# Do mayor pentatónica (las campanitas del giro y de las bombillas).
PENTA = [0, 2, 4, 7, 9]


def penta(i, base=72):
    return base + 12 * (i // 5) + PENTA[i % 5]


def corazon(fuerza=1.0):
    """Un latido oído desde dentro: el «pum» grave y, detrás, el «pum» más corto."""
    def golpe(f0, f1, tau, dur):
        t = t_(dur)
        f = f1 + (f0 - f1) * np.exp(-t / (tau * 0.5))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
        x += 0.25 * pb(ruido(dur), 180) * np.exp(-t / (tau * 0.4))
        a = n_(0.006)
        x[:a] *= np.linspace(0, 1, a)
        return x
    x = mezclar(golpe(72, 46, 0.085, 0.45), en(0.17, 0.62 * golpe(84, 52, 0.06, 0.35)))
    return pico(x, fuerza)


def subida(dur, f0=110.0, f1=520.0):
    """La subida que aprieta mientras frena: un tono que sube con sus armónicos y aire que sube con él."""
    t = t_(dur)
    f = f0 * (f1 / f0) ** (t / dur) ** 1.6
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(fase) + 0.45 * np.sin(2 * fase + 0.3) + 0.22 * np.sin(3 * fase + 0.7) + 0.1 * np.sin(5 * fase)
    x = x * (1 + 0.08 * np.sin(2 * np.pi * 5.5 * t))
    aire = filtro_mov(ruido(dur), f * 4.0, tipo='band', q=1.6)
    x = mezclar(x / np.max(np.abs(x)), 0.5 * aire / (np.max(np.abs(aire)) + 1e-9))
    return x * curva(n_(dur), [(0, 0.0), (0.3, 0.25), (0.8, 0.7), (1, 1.0)])


def chispazo(fuerza=1.0):
    """La máquina que se enciende: un chispazo eléctrico con su zumbido."""
    dur = 0.35
    t = t_(dur)
    x = bp(ruido(dur), 2000, 9000) * np.exp(-t / 0.03)
    x += 0.6 * np.sign(np.sin(2 * np.pi * 120 * t)) * np.exp(-t / 0.08) * 0.4
    return pico(pb(x, 9000), fuerza)


def animacion():
    x = np.zeros(n_(s_(T_PARA) + 1.6))
    # La entrada: aire que sube hasta el golpe del medallón al llegar, y se enciende (un chispazo y las bombillas).
    x = poner(x, 0.0, soplo(0.3, 260, 2800, q=1.3), 0.45)
    x = poner(x, 0.24, golpe_grave(125, 48, 0.1), 0.9)
    x = poner(x, 0.24, chapa(0.45), 0.22)
    x = poner(x, 0.18, chispazo(), 0.3)
    for i in range(BOMBILLAS):
        tt = s_(T_ENTRA) * i / (BOMBILLAS - 1)
        x = poner(x, tt, clic(1.0, 1.4), 0.09)
        x = poner(x, tt, campanita(midi(penta(i % 12, 79)), tau=0.1, dur=0.3), 0.1)
    hum = zumbido(s_(T_PARA) + 0.1)
    x = poner(x, 0.15, pb(hum, 1200) * curva(len(hum), [(0, 0.0), (0.02, 0.6), (0.06, 0.3), (1, 0.25)]), 0.1)
    # El tambor: zumba más agudo y más fuerte cuanto más deprisa va.
    dur = s_(T_PARA)
    ts = np.arange(n_(dur)) / SR * 20
    v = np.array([velocidad(tt) for tt in ts[::64]])
    v = np.repeat(v, 64)[:len(ts)]
    tambor = filtro_mov(ruido(dur), 300 + 520 * v, tipo='band', q=0.9) * (v / 1.8) ** 0.7 * 0.55
    tambor *= curva(len(tambor), [(0, 0.0), (0.02, 1.0), (1, 1.0)])
    x = poner(x, 0.0, tambor, 0.5)
    # Los dientes del trinquete: cada uno, un clic (deprisa se juntan en un ronroneo; al frenar se oyen sueltos).
    for seg, k in cruces(1.0 / DIENTES):
        vv = velocidad(seg * 20)
        g = 0.26 / (1 + 3.0 * vv) + 0.03
        x = poner(x, seg, clic(1.0, 0.85 + 0.1 * (k % 2)), g)
    # Las campanitas: deprisa, una cada tres iconos dando vueltas a un arpegio; al frenar, una por icono, subiendo; ya
    # despacio, cada icono que pasa es una campana más grave (el señuelo, la más).
    giro = [0, 2, 4, 2, 5, 4, 2, 1]
    sube = 0
    for seg, k in cruces(1.0):
        tick = seg * 20
        vv = velocidad(tick)
        if tick >= T_PARA - 1:
            continue
        if tick >= T_LENTO:
            x = poner(x, seg, campanita(midi(62 - 5 * (k % 2)), tau=0.9, dur=2.0), 0.3)
            x = poner(x, seg, clanc(), 0.12)
        elif vv > 0.6:
            if k % 3:
                continue
            nota = penta(giro[(k // 3) % len(giro)], 79)
            x = poner(x, seg, campanita(midi(nota), tau=0.14, dur=0.4), 0.15)
        else:
            nota = penta(3 + min(sube, 9), 74)
            sube += 1
            x = poner(x, seg, campanita(midi(nota), tau=0.3), 0.22)
    # La subida que aprieta mientras frena, cortada un instante antes del cerrojo.
    t0, t1 = s_(T_FRENA), s_(T_PARA) - 0.06
    x = poner(x, t0, subida(t1 - t0) * ventana(t1 - t0, 0.5, 0.02), 0.13)
    # El corazón, cada vez más seguido y más fuerte.
    for i, l in enumerate(LATIDOS):
        x = poner(x, s_(l), corazon(), 0.45 + 0.5 * i / (len(LATIDOS) - 1))
    # El redoble: casi parado en el señuelo, las campanitas tiemblan cada vez más fuerte; un instante de silencio.
    t0, t1 = s_(146), s_(T_PARA) - 0.08
    n_red = int((t1 - t0) * 18)
    for i in range(n_red):
        tt = t0 + i / 18.0
        g = 0.04 + 0.2 * (i / n_red) ** 1.8
        x = poner(x, tt, campanita(midi(penta(12 + (i % 2), 74)), tau=0.07, dur=0.22), g)
        x = poner(x, tt, bp(ruido(0.02), 2500, 9000) * caida(0.02, 0.004), g * 0.5)
    # El cerrojo: ¡clonc!
    x = poner(x, s_(T_PARA), golpe_grave(90, 36, 0.16), 1.0)
    x = poner(x, s_(T_PARA), clanc(), 0.65)
    x = poner(x, s_(T_PARA), chapa(0.45), 0.3)
    return reverb(x, 0.12, 1.2)


def mob():
    """El huevo: el cascarón que se raja tres veces, unas notas que suben como una pregunta y algo que pía."""
    x = np.zeros(n_(2.0))
    for seg, g, gr in ((0.0, 0.5, 6), (0.16, 0.7, 9), (0.36, 1.0, 14)):
        x = poner(x, seg, cascara(1.0, gr), g * 0.6)
    notas = [(0.0, 64), (0.11, 68), (0.22, 71), (0.33, 75)]
    for seg, m in notas:
        x = poner(x, seg, marimba(midi(m)), 0.42)
    # La última, la de la pregunta: se queda y sube un poco.
    t = t_(1.1)
    f = midi(78) * (1 + 0.06 * np.clip((t - 0.15) / 0.4, 0, 1) ** 2)
    fase = 2 * np.pi * np.cumsum(f) / SR
    preg = (np.sin(fase) + 0.25 * np.sin(2 * fase) + 0.1 * np.sin(3.9 * fase)) * caida(1.1, 0.42) * \
        (1 + 0.04 * np.sin(2 * np.pi * 6 * t))
    x = poner(x, 0.44, preg, 0.3)
    x = poner(x, 0.44, marimba(midi(78)), 0.35)
    x = poner(x, 0.62, piar(0.16), 0.2)
    x = poner(x, 0.82, piar(0.12, f0=1800, f1=2900), 0.16)
    x = poner(x, 0.4, destellos(0.6, 10), 0.08)
    return reverb(x, 0.2, 1.4)


def dificultad():
    """La advertencia: el timbre de alarma y dos golpes de metales graves, el segundo más bajo."""
    x = np.zeros(n_(2.2))
    x = poner(x, 0.0, timbre_alarma(0.95), 0.42)
    x = poner(x, 0.0, metales([50, 53, 57], 0.38), 0.5)
    x = poner(x, 0.44, metales([49, 52, 55, 58], 0.9, abre=2200), 0.62)
    x = poner(x, 0.0, golpe_grave(70, 34, 0.18), 0.6)
    x = poner(x, 0.44, golpe_grave(60, 30, 0.22), 0.7)
    return reverb(x, 0.2, 1.6)


def penalizacion():
    """La mala suerte: uah, uah, uah, uaaah (cada vez más bajo), con una cadena y un brillo de hielo."""
    x = np.zeros(n_(2.4))
    for seg, m, d in ((0.0, 67, 0.24), (0.27, 66, 0.24), (0.54, 65, 0.24)):
        x = poner(x, seg, uah(midi(m), d), 0.5)
    x = poner(x, 0.81, uah(midi(64), 1.1, vibrato=0.012), 0.55)
    x = poner(x, 0.0, cadena(0.28), 0.3)
    x = poner(x, 0.8, cadena(0.2, eslabones=4), 0.18)
    x = poner(x, 0.0, hielo(1.6), 0.16)
    x = poner(x, 0.81, golpe_grave(60, 32, 0.2), 0.35)
    return reverb(x, 0.18, 1.4)


def minijuego():
    """El minijuego: un arpegio de recreativa que sube y el acorde de «¡a jugar!», con monedas."""
    x = np.zeros(n_(2.0))
    arp = [60, 64, 67, 72, 76, 79, 84]
    for i, m in enumerate(arp):
        nota = cuadrada(midi(m), 0.09) * caida(0.09, 0.05)
        x = poner(x, i * 0.045, pb(nota, 7000), 0.16)
    t0 = len(arp) * 0.045 + 0.02
    acorde = sum(cuadrada(midi(m), 0.7) for m in (72, 76, 79)) / 3
    acorde = pb(acorde, 5000) * caida(0.7, 0.3, ataque=0.004)
    x = poner(x, t0, acorde, 0.3)
    for m in (84, 88, 91):
        x = poner(x, t0, campanita(midi(m), tau=0.4, dur=1.0), 0.18)
    x = poner(x, t0, destellos(0.7, 16, semilla=5), 0.12)
    x = poner(x, 0.0, golpe_grave(110, 60, 0.06), 0.3)
    return reverb(x, 0.18, 1.2)


def sale():
    """La máquina se va y el icono vuela al chat: aire que sube y brillitos."""
    x = np.zeros(n_(1.0))
    x = poner(x, 0.0, soplo(0.36, 500, 4200, q=1.6), 0.5)
    x = poner(x, 0.12, destellos(0.4, 12, 6000, 11000, semilla=8), 0.22)
    x = poner(x, 0.05, campanita(midi(91), tau=0.2, dur=0.5), 0.12)
    return reverb(x, 0.18, 1.0)


def aviso():
    """¡Din-din!: un timbre de mostrador, dos veces."""
    x = np.zeros(n_(1.6))
    toque = modos(2420, 1.4, ((1, 1.0), (2.32, 0.35), (4.25, 0.16), (6.63, 0.06)), 0.55, batido=0.0015)
    toque = toque / np.max(np.abs(toque))
    golpe = bp(ruido(0.005), 3000, 11000) * caida(0.005, 0.001)
    x = poner(x, 0.0, mezclar(toque, golpe * 0.6), 0.5)
    x = poner(x, 0.13, mezclar(toque, golpe * 0.5), 0.42)
    return reverb(x, 0.15, 1.0)


def interruptor(sube):
    """El interruptor de los menus de los cambios: el clic de la palanca, el cerrojo y dos campanitas que suben al
    encender (o bajan al apagar)."""
    x = np.zeros(n_(0.8))
    x = poner(x, 0.0, clic(1.0, 1.1), 0.5)
    x = poner(x, 0.035, clic(1.0, 0.8), 0.35)
    notas = (76, 83) if sube else (79, 72)
    for i, m in enumerate(notas):
        x = poner(x, 0.05 + i * 0.07, campanita(midi(m), tau=0.18, dur=0.5), 0.22 if sube else 0.16)
    return reverb(x, 0.1, 0.8)


def main():
    ms.empezar('ruleta')
    ms.guardar('animacion', animacion(), alto=0.9, limite=0.62)
    ms.guardar('mob', mob(), alto=0.88, limite=0.65)
    ms.guardar('dificultad', dificultad(), alto=0.9, limite=0.6)
    ms.guardar('penalizacion', penalizacion(), alto=0.88, limite=0.65)
    ms.guardar('minijuego', minijuego(), alto=0.86, limite=0.65)
    ms.guardar('sale', sale(), alto=0.8)
    ms.guardar('aviso', aviso(), alto=0.82)
    ms.guardar('enciende', interruptor(True), alto=0.7)
    ms.guardar('apaga', interruptor(False), alto=0.6)
    ms.escribir_json()
    if ms.HOJA:
        ms.hoja(ms.HOJA)


if __name__ == '__main__':
    main()
