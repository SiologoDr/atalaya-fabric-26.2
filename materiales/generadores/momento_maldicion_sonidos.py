"""
Los sonidos y la música del Momento Fractura (nació como Momento Maldición, 15-10-2026). Todo nuestro. El 16-10-2026
Juan pidió rehacer los de la animación («es similar a lo que tenemos de los bosses... más realistas») y luego que
intimiden: «como si aparece la animación los jugadores van a saber que es algo malo»; «al romperse, un vidrio que se
rompe; cuando el cielo se rompe, un estruendo». Ya no usan los instrumentos de los jefes: son cosas de verdad hechas
con su física (las copas, la grieta que corre, cientos de esquirlas, el trueno) y el lenguaje de las películas de
miedo (la bocina, el dron, las cuerdas que tiemblan, el golpe grave):

  momento.animacion   0-126: nada más empezar, la BOCINA de las películas de miedo (un acorde grave de sierras
                      desafinadas que se abre de golpe, saturado) con su golpe grave: se sabe que viene algo malo.
                      Debajo, un dron que ruge (dos notas a un semitono), el corazón hondo cada vez más seguido y unas
                      cuerdas de terror (un racimo disonante con trémolo) que crecen mientras se dibuja el Sello, con
                      algo muy pesado que se arrastra sobre piedra; un golpe sordo por cada punta de la estrella y, por
                      cada sigilo, un sello de hierro que se clava en la piedra, cada vez más fuerte, como tambores que
                      llevan a la segunda bocina. Nada de cristal ni de brillo: Juan, de los sigilos, «que no suene
                      como brillos o cristal, le quita el toque de seriedad e intimidación»
  momento.titulo      126-168: la segunda bocina, más alta, y todo sube (las cuerdas, un tono que se dispara, el
                      corazón desbocado, el cristal que se queja y, desde 150, se raja); en 168, silencio de golpe y el
                      pitido del oído
  momento.fractura    174: el cristal de la pantalla estalla: el crac, el golpe del vidrio que se parte, cientos de
                      esquirlas que saltan, caen y rebotan, y un golpe grave
  momento.cielo       180: el cielo se rompe con un estruendo: el latigazo del rayo, el trueno que rueda, un retumbar
                      grave que no acaba y el cielo que se desgarra; lejos, llueven esquirlas
  momento.aviso       224, con el aviso del chat: una campana de bronce grande y vieja con una bocina grave debajo
  momento.fin         al pararlo: el estallido al revés (el cristal que se recompone), un aire que sube y una campana
                      pequeña, la calma
  momento.musica      mientras dura, en bucle: una nana maldita. Una cajita de música rota (algo desafinada, con
                      el vaivén de un muelle cansado) en re menor armónica y en tres por cuatro, sobre un dron
                      grave, un coro de fondo y el corazón (pum-pum) al principio de cada compás de 3,7 s, que es el
                      latido del cielo y de las grietas en el juego. Dieciséis compases (59,2 s); la cola de la
                      reverberación se pliega al principio, así el bucle no tiene costura.

Usa las utilidades de señal de minijefes_sonidos.py (filtros, sala). Uso: python momento_maldicion_sonidos.py <raiz>
[hoja]
"""
import os
import sys

import numpy as np
import soundfile as sf

import minijefes_sonidos as ms
from minijefes_sonidos import (bp, caida, coro_voces, curva, en, filtro_mov, mezclar, modos, n_, pa, pb, pico, resonar,
                               reverb, ruido, saturar, soplo, susurro, t_, ventana)

ms.SUBTITULOS['momento'] = {
    'animacion': ('Ruge una bocina maldita', 'A cursed horn roars'),
    'titulo': ('El cristal cruje', 'Glass creaks'),
    'cielo': ('El cielo se rompe con un estruendo', 'The sky breaks with a roar'),
    'fractura': ('Estalla el cristal', 'Glass shatters'),
    'aviso': ('Dobla una campana', 'A bell tolls'),
    'fin': ('El cristal se recompone', 'The glass mends'),
}
ms.SALAS['momento'] = ('abismo', 5500)


def s_(tick):
    return tick / 20.0


# El calendario de la cinemática (ticks), el mismo que MomentoMaldicionCliente.
LATIDOS_ANIMACION = [0, 30, 54, 74, 90, 104, 116]
LATIDOS_TITULO = [126, 134, 142, 149, 155, 160, 164]
T_CIRCULO = (18, 40)
T_CIRCULO2 = (40, 56)
T_ESTRELLA = (56, 80)
T_RUNAS = (80, 118)
RUNAS = 16
T_TITULO = 126
T_GRIETAS = 150
T_SILENCIO = 168

# Re menor armónica (la escala de la nana y de las runas).
ESCALA = [62, 64, 65, 67, 69, 70, 73]
CAMPANA = ((0.5, 0.9), (1.0, 1.0), (1.183, 0.7), (1.506, 0.45), (2.0, 0.5), (2.514, 0.25), (2.662, 0.3),
           (3.011, 0.15), (4.166, 0.12), (5.433, 0.07))
# Una púa de cajita de música: el modo de flexión y sus parciales altos.
PUA = ((1.0, 1.0), (2.0, 0.1), (6.27, 0.28), (17.55, 0.07))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def nota_escala(i, base=74):
    """La nota i de la escala menor armónica desde base (i puede pasar de la octava)."""
    o, k = divmod(i, len(ESCALA))
    return base - 62 + ESCALA[k] + 12 * o


def latido(fuerza=1.0, doble=True):
    """Un corazón de verdad, oído desde dentro del pecho: el «lub» (las válvulas que se cierran: un golpe grave que
    baja de tono, con su chasquido sordo) y, un cuarto de segundo después, el «dub», más corto y más alto. Todo
    apagado, como a través del cuerpo."""
    def golpe(f0, f1, dur, clic):
        t = t_(dur)
        f = f1 + (f0 - f1) * np.exp(-t / (dur * 0.25))
        fase = 2 * np.pi * np.cumsum(f) / ms.SR
        cuerpo = np.sin(fase) * (1 - np.exp(-t / 0.004)) * np.exp(-t / (dur * 0.32))
        golpe_sordo = pb(ruido(dur), 140, 2) * np.exp(-t / (dur * 0.12))
        chasquido = bp(ruido(dur), 160, 520) * np.exp(-t / 0.012)
        return mezclar(pico(cuerpo, 1.0), pico(golpe_sordo, 0.45), pico(chasquido, clic))
    lub = golpe(62, 38, 0.17, 0.35)
    x = pico(lub, fuerza)
    if doble:
        dub = golpe(78, 50, 0.11, 0.28)
        x = mezclar(x, en(0.24 + ms.rng.uniform(-0.01, 0.01), pico(dub, 0.7 * fuerza)))
    return pb(saturar(pico(x, 1.0), 1.4), 260, 2) * fuerza


def toque(f, fuerza=1.0, tau=0.9, partes=None):
    """Un golpecito a un cristal: los modos de una copa (no armónicos: suena a vidrio y no a campana), cada uno con su
    pequeño batido, y el clic del golpe."""
    partes = partes or ((1.0, 1.0), (2.71, 0.45), (5.15, 0.22), (8.43, 0.1), (12.3, 0.05))
    dur = min(4.0, tau * 5)
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in partes:
        fr = f * r * ms.rng.uniform(0.992, 1.008)
        if fr < ms.SR * 0.45:
            for d in (-0.0012, 0.0012):
                s += a * np.sin(2 * np.pi * fr * (1 + d) * t + ms.rng.uniform(0, 6)) * np.exp(-t / (tau / r ** 0.7))
    clic = pa(ruido(0.004), 3000) * np.exp(-t_(0.004) / 0.0007)
    s[:len(clic)] += clic * 0.5
    return pico(s, fuerza)


def esquirla(f, fuerza=1.0, tau=0.05):
    """Una esquirla de cristal que suena: un tintineo corto y agudo."""
    return toque(f, fuerza, tau, ((1.0, 1.0), (2.71, 0.5), (5.15, 0.25)))


def chasquido(fuerza=1.0, claro=1.0, pew=True):
    """El crac de un cristal (o del hielo) que se raja: un golpe seco de todo el espectro y, detrás, el silbido que
    baja muy deprisa (las ondas agudas corren más por el cristal que las graves)."""
    dur = 0.16
    t = t_(dur)
    golpe = pa(ruido(dur), 900 * claro) * np.exp(-t / 0.0015)
    capas = [pico(golpe, 1.0)]
    if pew:
        f0, f1 = ms.rng.uniform(5000, 9000) * claro, ms.rng.uniform(300, 700)
        f = f1 + (f0 - f1) * np.exp(-t / ms.rng.uniform(0.012, 0.03))
        silba = np.sin(2 * np.pi * np.cumsum(f) / ms.SR) * np.exp(-t / 0.035) * (1 - np.exp(-t / 0.0008))
        capas.append(pico(silba, 0.55))
    cuerpo = bp(ruido(dur), 1200 * claro, 4500 * claro) * np.exp(-t / 0.012)
    capas.append(pico(cuerpo, 0.5))
    return pico(mezclar(*capas), fuerza)


def quejido(dur, tasa0=25.0, tasa1=90.0, grave=1.0, fuerza=1.0):
    """El cristal que aguanta un peso: se agarra y se suelta (un tren de golpecitos cada vez más seguido) y suena en
    sus modos graves: un crujido largo, como el hielo de un lago o un barco de madera, pero de vidrio."""
    n = n_(dur)
    tasa = curva(n, [(0, tasa0), (1, tasa1)]) * (1 + 0.35 * ms.rng.standard_normal(n).cumsum() / np.sqrt(n) / 6)
    fase = np.cumsum(np.maximum(tasa, 5)) / ms.SR
    pulsos = np.zeros(n)
    i = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    pulsos[i] = ms.rng.uniform(0.3, 1.0, len(i))
    x = mezclar(*[resonar(pulsos, f * grave, q) * a for f, q, a in ((520, 18, 1.0), (1130, 22, 0.7), (2380, 26, 0.4),
                                                                      (3900, 30, 0.2))])
    return pico(x * ventana(dur, dur * 0.2, dur * 0.25), fuerza)


def estallido(dur=3.2, cuantas=520, fuerza=1.0):
    """Un cristal enorme que revienta: el crac, el golpe grave, el crujido del vidrio que se parte y cientos de
    esquirlas que suenan al saltar (muy seguidas al principio) y al caer y rebotar (cada vez menos)."""
    capas = [pico(chasquido(1.0, 1.0, False), 1.0)]
    t = t_(0.5)
    f = 34 + 40 * np.exp(-t / 0.06)
    golpe = np.sin(2 * np.pi * np.cumsum(f) / ms.SR) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.16)
    capas.append(pico(golpe, 0.95))
    capas.append(pico(bp(ruido(0.35), 700, 5000) * caida(0.35, 0.07, 0.001), 0.7))
    tandas = []
    for k in range(cuantas):
        # Dos tandas: las que saltan (en el primer medio segundo) y las que caen y rebotan (hasta el final).
        if k < cuantas * 0.55:
            cuando = ms.rng.exponential(0.12)
            a = ms.rng.uniform(0.3, 1.0) * np.exp(-cuando / 0.4)
        else:
            cuando = 0.25 + ms.rng.exponential(dur * 0.28)
            a = ms.rng.uniform(0.15, 0.6) * np.exp(-cuando / (dur * 0.5))
        if cuando > dur:
            continue
        fq = np.exp(ms.rng.uniform(np.log(2200), np.log(11000)))
        tandas.append(en(cuando, esquirla(fq, a, ms.rng.uniform(0.012, 0.09))))
    capas.append(pico(mezclar(*tandas), 0.85))
    return pico(mezclar(*capas), fuerza)


def trueno(dur, fuerza=1.0, lejos=0.0):
    """Un trueno que rueda: un estruendo grave que va y viene en golpes, cada vez más lejos."""
    n = n_(dur)
    base = pb(ruido(dur, 'marron'), 260 - 120 * lejos, 2)
    golpes = np.zeros(n)
    cuando = 0.0
    while cuando < dur * 0.8:
        i = n_(cuando)
        ancho = ms.rng.uniform(0.15, 0.5)
        tt = (np.arange(n) - i) / ms.SR
        golpes += ms.rng.uniform(0.4, 1.0) * np.exp(-cuando / (dur * 0.45)) * np.exp(-(tt / ancho) ** 2) * (tt > -ancho * 2)
        cuando += ms.rng.uniform(0.15, 0.55)
    medio = bp(ruido(dur), 300, 1200 - 600 * lejos) * golpes * 0.25
    return pico(mezclar(base * (0.2 + golpes), medio) * ventana(dur, 0.02, dur * 0.4), fuerza)


def campana(f=73.4, dur=8.0, fuerza=1.0, rajada=0.004):
    """Una campana de bronce grande y vieja: sus parciales de verdad (el zumbido, la fundamental, la tercera menor que
    la hace triste, la quinta, la octava y los de arriba), cada uno con su caída, un poco desafinados entre sí (está
    algo rajada: bate), y el golpe metálico del badajo."""
    parciales = ((0.5, 0.55, 1.0), (1.0, 1.0, 0.75), (1.183, 0.7, 0.55), (1.506, 0.35, 0.4), (2.0, 0.55, 0.32),
                 (2.514, 0.25, 0.22), (2.662, 0.2, 0.2), (3.011, 0.18, 0.16), (4.166, 0.12, 0.11), (5.433, 0.08, 0.08),
                 (6.796, 0.05, 0.06))
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a, cola in parciales:
        for d in (-rajada, rajada * 0.7):
            s += a * np.sin(2 * np.pi * f * 2 * r * (1 + d) * t + ms.rng.uniform(0, 6)) * np.exp(-t / (dur * cola))
    badajo = bp(ruido(0.02), 1800, 7000) * np.exp(-t_(0.02) / 0.004)
    s[:len(badajo)] += pico(badajo, 0.6) * np.max(np.abs(s[:4000]))
    a = n_(0.002)
    s[:a] *= np.linspace(0, 1, a)
    return pico(s, fuerza)


def pitido(dur, f=7800.0, fuerza=1.0):
    """El pitido del oído después de un golpe muy fuerte."""
    t = t_(dur)
    x = np.sin(2 * np.pi * f * t) * (1 + 0.05 * np.sin(2 * np.pi * 4.1 * t)) * np.exp(-t / (dur * 0.45))
    a = n_(0.01)
    x[:a] *= np.linspace(0, 1, a)
    return pico(x, fuerza)


def sierra(f, dur, voces=3, desafina=0.006, techo=4200.0):
    """Una sierra (todos los armonicos) sin aliasing, en varias voces un poco desafinadas: el cuerpo de una bocina o
    de unas cuerdas."""
    t = t_(dur)
    s = np.zeros_like(t)
    for v in range(voces):
        d = 1 + desafina * (v - (voces - 1) / 2) / max(1, (voces - 1) / 2)
        fv = f * d
        fase = ms.rng.uniform(0, 6)
        for k in range(1, int(techo / fv) + 1):
            s += np.sin(2 * np.pi * k * fv * t + fase * k) / k
    return s / voces


def braam(f=36.7, dur=4.5, fuerza=1.0, abre=2600.0):
    """La bocina de las películas de miedo: un acorde grave (la nota, su quinta y su octava, con un sub debajo) de
    sierras desafinadas que se abre de golpe (el filtro sube en un cuarto de segundo) y se va cerrando, saturado: se
    oye y se sabe que viene algo malo."""
    n = n_(dur)
    x = sierra(f, dur, 4, 0.008) + 0.7 * sierra(f * 1.5, dur, 3, 0.007) + 0.55 * sierra(f * 2, dur, 3, 0.006)
    x += 1.2 * np.sin(2 * np.pi * f / 2 * t_(dur))
    fc = curva(n, [(0, 120), (0.06, abre), (0.35, abre * 0.45), (1, 260)])
    x = filtro_mov(x, fc, 'low', 1.3)
    env = curva(n, [(0, 0), (0.012, 1.0), (0.3, 0.75), (1, 0.0)])
    x = saturar(pico(x * env, 1.0), 2.6)
    aire = filtro_mov(ruido(dur, 'rosa'), fc * 0.8, 'band', 1.4) * env
    return pico(mezclar(pico(x, 1.0), pico(aire, 0.18)), fuerza)


def golpe_sub(fuerza=1.0, dur=1.4, f0=58.0, f1=26.0):
    """El golpe grave de los trailers: un sub que cae de tono, saturado, con su chasquido."""
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / 0.12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / ms.SR) * (1 - np.exp(-t / 0.004)) * np.exp(-t / (dur * 0.35))
    clic = pa(ruido(0.03), 1500) * np.exp(-t_(0.03) / 0.004)
    x = saturar(pico(sub, 1.0), 2.0)
    x[:len(clic)] += clic * 0.35
    return pico(x, fuerza)


def dron(dur, f=36.7, fuerza=1.0):
    """El dron de debajo: dos notas graves a un semitono (baten y rugen), con un filtro que respira despacio."""
    n = n_(dur)
    x = sierra(f, dur, 2, 0.004, 1200.0) + 0.8 * sierra(f * 1.0595, dur, 2, 0.004, 1200.0)
    fc = 160 + 90 * np.sin(2 * np.pi * 0.31 * t_(dur)) + curva(n, [(0, 0), (1, 140)])
    x = filtro_mov(x, fc, 'low', 1.8)
    return pico(x * ventana(dur, dur * 0.3, dur * 0.15), fuerza)


def cuerdas(dur, notas, fuerza=1.0, sube=None):
    """Cuerdas de terror: un racimo de notas pegadas (disonante), en sierras con trémolo (el arco que tiembla), cada
    voz a su velocidad; crecen."""
    n = n_(dur)
    t = t_(dur)
    capas = []
    for i, f in enumerate(notas):
        x = sierra(f, dur, 2, 0.003, 7000.0)
        trem = 0.55 + 0.45 * np.sin(2 * np.pi * (9 + 1.7 * i) * t + ms.rng.uniform(0, 6))
        capas.append(x * trem)
    x = pb(mezclar(*capas), 5200, 2)
    env = curva(n, sube or [(0, 0), (0.6, 0.5), (1, 1)])
    return pico(x * env, fuerza)


def subida(dur, f0=90.0, f1=900.0, fuerza=1.0):
    """Lo que sube hasta reventar: un tono que se dispara (con su trémolo cada vez más deprisa) y un siseo que crece."""
    n = n_(dur)
    t = t_(dur)
    f = f0 * (f1 / f0) ** (t / dur) ** 1.6
    fase = 2 * np.pi * np.cumsum(f) / ms.SR
    tono = np.sin(fase) + 0.5 * np.sin(2 * fase) + 0.3 * np.sin(3 * fase)
    tono *= 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 4), (1, 26)])) / ms.SR)
    sisea = filtro_mov(ruido(dur, 'rosa'), f * 4, 'band', 2.0)
    env = curva(n, [(0, 0.05), (0.7, 0.45), (1, 1.0)]) ** 1.5
    return pico(mezclar(pico(tono * env, 1.0), pico(sisea * env, 0.55)), fuerza)


def golpe_sordo(fuerza=1.0):
    """Un golpe hondo y sordo, como un tambor enorme muy lejos."""
    t = t_(1.2)
    f = 42 + 50 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / ms.SR) * (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.3)
    x = mezclar(pico(x, 1.0), pico(pb(ruido(1.2), 180, 2) * np.exp(-t / 0.08), 0.4))
    return pico(saturar(x, 1.6), fuerza)


def estallido_grande(fuerza=1.0):
    """Un cristal enorme que estalla: el crac, el golpe del vidrio que se parte (un chasquido ancho y brillante que se
    apaga en medio segundo, el ruido de verdad de un cristal roto), cientos de esquirlas que saltan y luego caen y
    rebotan, con su golpe grave."""
    crac = chasquido(1.0, 1.2, False)
    cuerpo = pa(ruido(1.2), 1800) * caida(1.2, 0.22, 0.001)
    cuerpo = mezclar(pico(cuerpo, 1.0), pico(bp(ruido(1.2), 3000, 12000) * caida(1.2, 0.5, 0.001), 0.6))
    esquirlas = estallido(3.6, 1100)
    # El golpe grave ya va en las esquirlas (otro mas, a un tono cercano, batia con el).
    return pico(mezclar(pico(crac, 1.0), pico(cuerpo, 0.75), en(0.01, pico(esquirlas, 0.95))), fuerza)


def estruendo(dur=7.5, fuerza=1.0):
    """El cielo que se rompe: un trueno enorme. El latigazo del rayo (un chasquido seco y ancho), el estruendo que
    rueda en golpes cada vez más lejos, un retumbar grave que no acaba y el cielo que se desgarra (un ruido grave que
    baja)."""
    n = n_(dur)
    t = t_(dur)
    latigo = mezclar(pico(chasquido(1.0, 0.9, False), 1.0), pico(pb(ruido(0.4), 2500, 2) * caida(0.4, 0.05, 0.0005), 0.8))
    rueda = trueno(dur, 1.0, 0.0)
    retumba = pb(ruido(dur, 'marron'), 70, 2) * curva(n, [(0, 0), (0.04, 1), (0.6, 0.6), (1, 0)])
    rasga = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 900), (0.5, 220), (1, 120)]), 'band', 1.2)
    rasga *= curva(n, [(0, 0), (0.05, 1), (0.5, 0.5), (1, 0)])
    golpes = [en(c, pico(golpe_sub(1.0, 1.8, 50, 24), a)) for c, a in ((0.02, 1.0), (1.1, 0.6), (2.4, 0.45))]
    x = mezclar(pico(latigo, 1.0), en(0.03, pico(rueda, 1.0)), pico(retumba, 0.8), pico(rasga, 0.45), *golpes)
    return pico(saturar(pico(x, 1.0), 1.5), fuerza)


def arrastre(dur, fuerza=1.0):
    """Algo muy pesado que se arrastra sobre piedra, a tirones: un roce grave que se agarra y se suelta, con el retumbar
    de debajo. Como si alguien moviera la losa del Sello."""
    n = n_(dur)
    t = t_(dur)
    roce = filtro_mov(ruido(dur, 'marron'), curva(n, [(0, 150), (0.5, 240), (1, 170)]), 'band', 1.6)
    tirones = 0.6 + 0.4 * np.sin(2 * np.pi * 5.5 * t + 1.4 * np.sin(2 * np.pi * 0.8 * t))
    debajo = pb(ruido(dur, 'marron'), 90, 2)
    x = mezclar(pico(roce * tirones, 1.0), pico(debajo, 0.6))
    return pico(saturar(pico(x * ventana(dur, dur * 0.25, dur * 0.35), 1.0), 1.4), fuerza)


def marca(f=52.0, fuerza=1.0):
    """Un sigilo que se graba: un sello de hierro enorme que se clava en la piedra. El golpe grave que cae de tono, el
    cuerpo sordo de la piedra, un gruñido grave saturado y el filo del golpe (en medios, para que se oiga también en
    altavoces pequeños). Corto, para que los dieciséis seguidos no se emborronen."""
    dur = 0.7
    t = t_(dur)
    fr = f * 0.75 + f * 0.6 * np.exp(-t / 0.04)
    sub = np.sin(2 * np.pi * np.cumsum(fr) / ms.SR) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.16)
    piedra = pb(ruido(dur, 'marron'), 260, 2) * np.exp(-t / 0.05)
    grune = pb(sierra(f * 1.5, dur, 2, 0.01, 900.0), 320, 2) * np.exp(-t / 0.12)
    filo = bp(ruido(0.02), 300, 1500) * np.exp(-t_(0.02) / 0.004)
    x = mezclar(pico(sub, 1.0), pico(piedra, 0.5), pico(grune, 0.35), pico(filo, 0.25))
    return pico(saturar(pico(x, 1.0), 1.8), fuerza)


def retumbo(dur, fuerza=1.0):
    """Lo que crece debajo de los sigilos hasta la segunda bocina: un retumbar grave que sube y se abre."""
    n = n_(dur)
    x = filtro_mov(ruido(dur, 'marron'), curva(n, [(0, 70), (1, 420)]), 'low', 1.2)
    return pico(x * curva(n, [(0, 0), (1, 1)]) ** 1.8, fuerza)


# ----------------------------------------------------------------------------------------------------------------
#  La cinemática (a la par de MomentoMaldicionCliente)
# ----------------------------------------------------------------------------------------------------------------
def animacion():
    """0-126: nada más empezar, la BOCINA (el braam) con su golpe grave: se sabe que viene algo malo. Debajo, un dron
    que ruge, el corazón hondo cada vez más seguido y unas cuerdas de terror que crecen mientras se dibuja el Sello
    (con la losa que se arrastra); un golpe sordo por cada punta de la estrella y, por cada sigilo, un sello de hierro
    que se clava en la piedra, cada vez más fuerte, sobre un retumbar que sube. Nada de cristal ni de brillos (Juan:
    «le quita el toque de seriedad e intimidación»)."""
    dur = s_(T_TITULO) + 0.8
    capas = [pico(braam(36.7, 5.0), 1.0), pico(golpe_sub(1.0, 1.6), 0.9), en(0.4, pico(dron(dur - 0.4), 0.42))]
    for k, tick in enumerate(LATIDOS_ANIMACION):
        if tick > 0:
            capas.append(en(s_(tick), pico(latido(1.0), 0.75 + 0.25 * k / len(LATIDOS_ANIMACION))))
    a, b = T_CIRCULO
    capas.append(en(s_(a), pico(cuerdas(dur - s_(a), [587.3, 622.3, 659.3, 698.5], 1.0), 0.3)))
    capas.append(en(s_(a), pico(arrastre(s_(T_CIRCULO2[1] - a)), 0.3)))
    a, b = T_ESTRELLA
    for k in range(7):
        capas.append(en(s_(a + k * (b - a) / 7), golpe_sordo(0.55 + 0.05 * k)))
    a, b = T_RUNAS
    capas.append(en(s_(a), pico(retumbo(s_(T_TITULO - a) + 0.3), 0.35)))
    # Los sigilos, con su sala corta (con la larga se emborronaban: van casi ocho por segundo).
    marcas = []
    for k in range(RUNAS):
        # Como dos manos en un tambor: una nota y la otra, la segunda algo mas floja; crecen hasta la bocina.
        cuando = s_(a + k * (b - a) / RUNAS)
        fuerza = (0.3 + 0.6 * k / (RUNAS - 1)) * (1.0 if k % 2 == 0 else 0.82)
        marcas.append(en(cuando, marca(55.0 if k % 2 == 0 else 49.0, fuerza)))
    return mezclar(reverb(mezclar(*capas), 0.3, 2.6), reverb(mezclar(*marcas), 0.15, 0.9))


def titulo():
    """126-168: la segunda BOCINA, más alta, y todo sube: las cuerdas, un tono que se dispara, el corazón desbocado y
    el cristal que se queja y, desde 150, se raja (chasquidos cada vez más seguidos). En 168, silencio de golpe: solo
    el pitido del oído."""
    dur = s_(T_SILENCIO - T_TITULO)
    n = n_(dur)
    capas = [
        pico(braam(55.0, dur + 0.6, 1.0, 3400.0)[:n], 0.85),
        pico(cuerdas(dur, [880.0, 932.3, 987.8, 1046.5], 1.0, [(0, 0.5), (1, 1.0)]), 0.32),
        pico(subida(dur, 80.0, 700.0), 0.5),
        pico(quejido(dur, 30, 160, 1.0) * curva(n, [(0, 0.3), (1, 1.0)]), 0.3),
    ]
    for k, tick in enumerate(LATIDOS_TITULO):
        capas.append(en(s_(tick - T_TITULO), pico(latido(1.0), 0.85 + 0.15 * k / len(LATIDOS_TITULO))))
    g = s_(T_GRIETAS - T_TITULO)
    cuando = g
    while cuando < dur - 0.02:
        capas.append(en(cuando, chasquido(0.35 + 0.65 * (cuando - g) / (dur - g), ms.rng.uniform(0.7, 1.2))))
        cuando += max(0.02, 0.22 * np.exp(-(cuando - g) / 0.35)) * ms.rng.uniform(0.6, 1.4)
    x = reverb(mezclar(*capas), 0.25, 1.6)[:n]
    # El silencio de golpe, y en él el pitido.
    x[-n_(0.006):] *= np.linspace(1, 0, n_(0.006))
    return np.concatenate([x, pico(pitido(0.4), 0.05)])


def fractura():
    """174: el cristal de la pantalla estalla."""
    return reverb(estallido_grande(1.0), 0.3, 3.0)


def cielo():
    """180: el cielo se rompe con un estruendo, y lejos llueven esquirlas."""
    granizo = []
    for _ in range(140):
        cuando = 0.6 + ms.rng.exponential(1.5)
        if cuando < 6.5:
            granizo.append(en(cuando, esquirla(np.exp(ms.rng.uniform(np.log(1800), np.log(6500))),
                                                ms.rng.uniform(0.1, 0.5), ms.rng.uniform(0.02, 0.07))))
    x = mezclar(pico(estruendo(7.5), 1.0), pico(pb(mezclar(*granizo), 5500, 2), 0.18))
    return reverb(x, 0.4, 3.4)


def aviso():
    """224, con el aviso del chat: dobla una campana de bronce grande y vieja, con una bocina grave debajo."""
    golpe = campana(73.4, 8.0, 1.0)
    debajo = pico(braam(36.7, 4.0, 1.0, 900.0), 0.45)
    return reverb(mezclar(golpe, en(0.02, debajo), pico(golpe_sub(1.0, 1.5), 0.5)), 0.42, 3.4)


def fin():
    """Al pararlo: el estallido al revés (el cristal que se recompone), un aire que sube y la campana pequeña de la
    calma; el viento se va."""
    reves = estallido(1.8, 260)[::-1]
    reves = pico(reves * np.linspace(0.15, 1.0, len(reves)) ** 2.5, 0.6)
    sube = pico(soplo(1.8, 300.0, 2600.0, 1.0, 0.1), 0.35)
    calma = pico(campana(220.0, 4.0, 1.0, 0.0015), 0.35)
    return reverb(mezclar(reves, en(1.0, sube), en(1.75, calma)), 0.4, 3.0)


# ----------------------------------------------------------------------------------------------------------------
#  La nana maldita (la música, en estéreo y en bucle)
# ----------------------------------------------------------------------------------------------------------------
COMPAS = 3.7
PULSO = COMPAS / 3
COMPASES = 16
# La frase de la nana: (compás, pulso, nota MIDI, pulsos que dura).
FRASE = [
    (0, 0, 69, 1), (0, 1, 74, 1), (0, 2, 77, 1),
    (1, 0, 76, 2), (1, 2, 74, 1),
    (2, 0, 73, 1), (2, 1, 76, 1), (2, 2, 69, 1),
    (3, 0, 74, 3),
    (4, 0, 77, 1), (4, 1, 79, 0.5), (4, 1.5, 77, 0.5), (4, 2, 76, 1),
    (5, 0, 74, 1), (5, 1, 70, 2),
    (6, 0, 69, 1), (6, 1, 67, 0.5), (6, 1.5, 69, 0.5), (6, 2, 73, 1),
    (7, 0, 74, 3),
]
# Los acordes del coro, uno por compás de la frase.
ACORDES = [(50, 53, 57), (50, 53, 57), (45, 49, 52), (50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52), (50, 53, 57)]


def pua(f, dur, rota=0.0):
    """Una nota de la cajita: el golpe de la púa y su timbre de metal fino; rota la desafina un poco."""
    f = f * 2 ** (rota * ms.rng.uniform(-0.12, 0.12) / 12)
    golpe = pico(pb(ruido(0.01), 9000, 2) * caida(0.01, 0.002, 0.0002), 0.25)
    return mezclar(pico(modos(f, dur, PUA, 0.9), 1.0), golpe)


def nana():
    largo = COMPASES * COMPAS
    total = largo + 8.0
    L = np.zeros(n_(total))
    R = np.zeros(n_(total))

    def poner(x, cuando, pan=0.0, ganancia=1.0):
        i = n_(cuando)
        x = x[:len(L) - i] * ganancia
        L[i:i + len(x)] += x * np.sqrt(0.5 * (1 - pan))
        R[i:i + len(x)] += x * np.sqrt(0.5 * (1 + pan))

    # El dron grave (re y la), con su batido, y un viento muy bajo.
    t = t_(total)
    dron = (np.sin(2 * np.pi * 73.4 * t) + 0.6 * np.sin(2 * np.pi * 73.9 * t) + 0.45 * np.sin(2 * np.pi * 110.0 * t)) \
        * (0.8 + 0.2 * np.sin(2 * np.pi * t / COMPAS))
    poner(pico(dron, 0.16), 0.0)
    poner(pico(pb(ruido(total, 'marron'), 600, 2), 0.1), 0.0)
    # El corazón al principio de cada compás: el latido del cielo en el juego.
    for c in range(COMPASES):
        poner(latido(0.5), c * COMPAS)
    # La cajita: la frase entera en los compases 4-11 y la mitad, una octava abajo, en 12-15.
    for c0, octava, compases, ganancia in ((4, 0, 8, 0.32), (12, -12, 4, 0.26)):
        for (c, p, m, d) in FRASE:
            if c >= compases:
                continue
            cuando = (c0 + c) * COMPAS + p * PULSO
            x = pua(midi(m + octava), max(1.8, d * PULSO + 1.0), rota=1.0)
            poner(x, cuando, pan=0.35 if (c + int(p * 2)) % 2 else -0.35, ganancia=ganancia)
            # Un eco más agudo y lejano en la segunda vuelta.
            if octava < 0 and p == 0:
                poner(pua(midi(m + 12), 1.4, rota=1.0), cuando + PULSO * 0.5, pan=0.6, ganancia=0.08)
    # El coro de fondo, un acorde por compás con la frase.
    for k in range(12):
        acorde = ACORDES[k % 8]
        c = 4 + k
        voces = coro_voces(COMPAS + 0.6, [midi(m) for m in acorde], 'o', None, 0.45)
        poner(pico(voces, 0.16), c * COMPAS - 0.2, pan=-0.2)
        poner(pico(voces, 0.16), c * COMPAS - 0.188, pan=0.2)
    # Susurros sueltos y, antes de volver a empezar, un soplo al revés que se traga el bucle.
    for c, vocal, pan in ((2, 'o', -0.6), (6, 'a', 0.6), (10, 'e', -0.5), (14, 'o', 0.5)):
        poner(pico(susurro(1.8, vocal, 1.0, curva(n_(1.8), [(0, 0.85), (1, 1.15)])), 0.1), c * COMPAS + PULSO, pan=pan)
    sopla = soplo(2.2, 3000.0, 300.0, 1.0, 0.1)[::-1]
    poner(pico(sopla, 0.14), largo - 2.2)
    # La campana lejana que abre la nana.
    poner(pico(modos(98.0, 5.0, CAMPANA, 2.4, 0.0025), 0.2), 0.0)
    # La sala, y la cola plegada al principio: así el final suena dentro del principio y no hay costura.
    L = reverb(L, 0.35, 2.6)
    R = reverb(R, 0.35, 2.6)
    n = n_(largo)
    estereo = np.stack([L[:n].copy(), R[:n].copy()], axis=1)
    cola = min(len(L) - n, n)
    estereo[:cola, 0] += L[n:n + cola]
    estereo[:cola, 1] += R[n:n + cola]
    return estereo * (0.85 / np.max(np.abs(estereo)))


def escribir_estereo(nombre, x):
    ruta = os.path.join(ms.SONIDOS, 'momento', nombre + '.ogg')
    # Por trozos: libsndfile se cae sin avisar si se le da un OGG largo de una vez.
    with sf.SoundFile(ruta, 'w', ms.SR, 2, format='OGG', subtype='VORBIS') as fh:
        for i in range(0, len(x), 16384):
            fh.write(x[i:i + 16384].astype(np.float32))
    print(f'  momento/{nombre:22s} {len(x) / ms.SR:5.2f} s (estéreo, en bucle)', flush=True)


def escribir_json_musica():
    """La música va en stream y sin subtítulo, como la de los jefes."""
    import collections
    import json
    ruta = os.path.join(ms.RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
    with open(ruta, encoding='utf-8') as fh:
        datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
    datos['momento.musica'] = {'sounds': [{'name': 'atalaya:momento/musica', 'stream': True}]}
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')


def main():
    ms.empezar('momento')
    ms.guardar('animacion', animacion(), alto=0.92, limite=0.62)
    ms.guardar('titulo', titulo(), alto=0.92, limite=0.62)
    ms.guardar('fractura', fractura(), alto=0.95, limite=0.6)
    ms.guardar('aviso', aviso(), alto=0.9, limite=0.65)
    ms.guardar('fin', fin(), alto=0.8)
    ms.guardar('cielo', cielo(), alto=0.95, limite=0.6)
    escribir_estereo('musica', nana())
    ms.escribir_json()
    escribir_json_musica()
    if len(sys.argv) > 2:
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
