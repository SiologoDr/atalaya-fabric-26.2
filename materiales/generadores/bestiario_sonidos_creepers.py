"""
Los sonidos de los creepers del bestiario (bestia.<id>.<nombre>), cada uno de su material:

  matojo      hierba: el roce de las matas, la mecha que sisea entre las hojas, el estallido con su lluvia de briznas
              y el saltito al salir del matojo
  marchito    pétalos secos y un aliento oscuro; su estallido deja un zumbido que se apaga (el Wither)
  enredadera  madera que cruje (el roce que se engancha y suelta) y hojas; el latigazo de las lianas, el apretón al
              atraparte y el chasquido al soltarse
  gelatina    gel: chapoteos y burbujas; su estallido es mojado y acaba en estática (te deja sin señal)
  atomico     acero: el contador Geiger y el zumbido eléctrico; la mecha es una sirena; su estallido, un trueno largo
              y la onda que llega lejos
  ciego       sculk: clics que se aceleran cuando te oye y un chillido al encontrarte
  tarta       una fiesta: el matasuegras, la nata que chapotea y el corcho al salir; el estallido pringa

Uso: python bestiario_sonidos_creepers.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, burbujas, caida, campana_env, chasquidos, clics, curva, en, filtro_mov,
                               mezclar, modos, n_, pa, pb, pico, resonar, reverb, ruido, saturar, seno, soplo, susurro,
                               t_, ventana)

rng = np.random.default_rng(20261018)


# ======================================================================================================================
#  Lo que comparten
# ======================================================================================================================
def roce(dur, fuerza=1.0, claro=1.0):
    """El roce de las matas: muchas briznas que se rozan (ráfagas cortas de ruido en la banda de las hojas)."""
    n = n_(dur)
    x = np.zeros(n)
    t = 0.0
    while t < dur:
        d = rng.uniform(0.02, 0.07)
        trozo = bp(ruido(d), 1800 * claro, 7000 * claro) * caida(d, d * 0.4, 0.002)
        i = int(t * ms.SR)
        x[i:i + len(trozo)] += trozo[:max(0, n - i)] * rng.uniform(0.4, 1.0)
        t += rng.uniform(0.008, 0.05)
    return x * fuerza * ventana(dur, 0.03, dur * 0.4)


def tallos(dur, cuantos=6):
    """Los tallos que se doblan y crujen: chasquidos secos y graves."""
    return chasquidos(dur, cuantos / max(0.05, dur), 400, 3000, 1.0)


def retumbo(dur, f=60.0, tau=None):
    """Un retumbo grave que se apaga (la tierra, la roca, el trueno lejano)."""
    return pb(ruido(dur, 'marron'), f * 2) * caida(dur, tau or dur * 0.35, 0.04)


def chof(dur=0.25, f0=900.0, f1=250.0, q=5.0):
    """Un chapoteo: ruido por un filtro estrecho que cae (algo blando que se aplasta)."""
    n = n_(dur)
    return filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, f0), (1, f1)]), 'band', q) * caida(dur, dur * 0.35, 0.004)


def crujido(dur, tasa0=40.0, tasa1=120.0, f=600.0):
    """Madera que cruje: el roce que se engancha y suelta (un tren de clics que se acelera), resonando."""
    n = n_(dur)
    c = clics(dur, curva(n, [(0, tasa0), (1, tasa1)]), 300, 3000)
    return (resonar(c, f, 6) + 0.3 * c) * ventana(dur, 0.02, dur * 0.3)


def golpe_madera(f=180.0, dur=0.35):
    return modos(f, dur, ((1, 1.0), (2.1, 0.5), (3.6, 0.25), (5.2, 0.12)), 0.05)


def clang(f=320.0, dur=1.2, tau=0.25):
    """Chapa de acero golpeada: modos inarmónicos que tardan en apagarse."""
    return modos(f, dur, ((1, 1.0), (2.76, 0.6), (5.4, 0.35), (8.93, 0.2), (13.3, 0.1)), tau, 0.002)


def hueco(f=240.0, dur=0.3):
    """Un golpe hueco (el caparazón): pocos modos, casi armónicos, y el aire de dentro."""
    return mezclar(pico(modos(f, dur, ((1, 1.0), (1.62, 0.55), (2.45, 0.3)), 0.045), 1.0),
                   pico(bp(ruido(0.05), 400, 2500) * caida(0.05, 0.012), 0.4))


def latir(fuerza=1.0, f=55.0):
    """Un latido: el golpe grave y el segundo, más flojo («pum-pum»), apagados por la carne."""
    a = boom(f + 20, f - 15, 0.07, 0.4)
    b = boom(f + 30, f - 10, 0.05, 0.3)
    carne = pb(ruido(0.12), 260) * caida(0.12, 0.03)
    x = mezclar(pico(a, 1.0), en(0.17, pico(b, 0.65)), pico(carne, 0.3), en(0.17, pico(carne, 0.2)))
    return pb(x, 400) * fuerza


def sirena(dur, f0=520.0, f1=980.0, ciclos=2.0):
    """La sirena: un tono áspero que sube y baja."""
    n = n_(dur)
    t = np.linspace(0, 1, n)
    f = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(2 * np.pi * ciclos * t))
    s = seno(f, dur, ((1, 1.0), (2, 0.35), (3, 0.2), (4, 0.1), (5, 0.06)))
    return saturar(s * 0.8, 1.5) * ventana(dur, 0.05, 0.2)


def matasuegras(dur, f0=420.0, f1=470.0):
    """El matasuegras de las fiestas: un zumbido de lengüeta que se desenrolla subiendo un poco."""
    n = n_(dur)
    f = curva(n, [(0, f0 * 0.88), (0.15, f0), (0.8, f1), (1, f1 * 0.96)])
    s = seno(f, dur, tuple((k, 1.0 / k ** 0.8) for k in range(1, 14)), 0.012, 7)
    return pb(saturar(s * 0.6, 2.0), 3500) * ventana(dur, 0.02, 0.08)


def estatica(dur):
    """La estática de una pantalla sin señal: ruido con el zumbido de la red y chasquidos."""
    t = t_(dur)
    zumbido = 0.65 + 0.35 * (np.sin(2 * np.pi * 60 * t) > 0)
    return mezclar(pico(bp(ruido(dur), 600, 9000) * zumbido, 0.8),
                   pico(chasquidos(dur, 40, 1000, 9000), 0.6)) * ventana(dur, 0.01, 0.3)


def geiger(dur, tasa):
    """El contador Geiger: chasquidos secos al azar (tasa por segundo, número o curva)."""
    return chasquidos(dur, tasa, 1800, 7500)


def chillido(dur=0.9, f0=280.0, f1=610.0):
    """Un chillido que no es de garganta: un tono inarmónico que sube y el aire que silba encima."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.3, f0 * 1.85), (1, f1)])
    tono = seno(f, dur, ((1, 1.0), (1.51, 0.5), (2.23, 0.35), (3.1, 0.2)), 0.03, 11)
    aire = filtro_mov(ruido(dur), f * 3.2, 'band', 8)
    return mezclar(pico(tono, 0.8), pico(aire, 0.6)) * ventana(dur, 0.06, dur * 0.45)


def estallido(golpe=1.0, cola=1.4, f0=70, f1=30, tau=0.35):
    """El estallido de todos (el golpe de presión y el chasquido del aire), para ponerle encima lo de cada uno."""
    return mezclar(pico(boom(f0, f1, tau, 1.8), golpe), pico(bp(ruido(0.3), 300, 3000) * caida(0.3, 0.08), 0.7 * golpe),
                   pico(retumbo(cola, 50), 0.5 * golpe))


# ======================================================================================================================
#  El Matojo
# ======================================================================================================================
def matojo():
    bs.empezar('matojo')
    bs.subtitulos('matojo', {
        'ambiente': ('Cruje un matojo', 'A tuft rustles'),
        'herido': ('Un Creeper Matojo recibe un golpe', 'Tuft Creeper hurts'),
        'muerte': ('Se deshace un Creeper Matojo', 'Tuft Creeper falls apart'),
        'paso': ('Pasos entre la hierba', 'Rustling steps'),
        'mecha': ('Sisea un Creeper Matojo', 'Tuft Creeper hisses'),
        'estalla': ('Estalla un Creeper Matojo', 'Tuft Creeper explodes'),
        'aparece': ('Algo salta de un matojo', 'Something leaps out of a bush'),
    })
    for k in range(3):
        x = mezclar(pico(roce(0.7 + 0.2 * k, 1.0, 0.9 + 0.1 * k), 0.8), en(0.2, pico(tallos(0.3, 3), 0.25)))
        bs.guardar('ambiente', x, k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(roce(0.25, 1.0, 1.1), 1.0), pico(tallos(0.2, 5), 0.6))
        bs.guardar('herido', x, k + 1, alto=0.8)
        bs.guardar('paso', pico(roce(0.12, 1.0, 0.8), 1.0), k + 1, alto=0.45)
    x = mezclar(pico(roce(1.2, 1.0, 0.8), 0.8), en(0.1, pico(tallos(0.9, 10), 0.6)),
                en(0.6, pico(roce(0.6, 1.0, 0.6) * np.linspace(1, 0, n_(0.6)), 0.6)))
    bs.guardar('muerte', x, alto=0.8)
    # La mecha: un siseo (el de la mecha de vanilla es del creeper: este es suyo) que sube, con las hojas temblando.
    dur = 1.6
    sis = filtro_mov(ruido(dur), curva(n_(dur), [(0, 2500), (1, 6500)]), 'band', 2.0)
    sis *= curva(n_(dur), [(0, 0.2), (0.15, 0.8), (1, 1.0)])
    x = mezclar(pico(sis, 0.7), pico(roce(dur, 1.0, 1.2), 0.6))
    bs.guardar('mecha', x, alto=0.8)
    # El estallido: el golpe y una lluvia de briznas que cae.
    golpe = boom(70, 30, 0.35, 1.6)
    lluvia = roce(1.4, 1.0, 1.0) * curva(n_(1.4), [(0, 1.0), (1, 0.0)])
    x = mezclar(pico(golpe, 1.0), pico(bp(ruido(0.3), 300, 3000) * caida(0.3, 0.08), 0.7), en(0.1, pico(lluvia, 0.6)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.6), 0.2, 1.4), alto=0.95, limite=0.75)
    # El salto: un roce brusco y el «pff» de las hojas al apartarse.
    x = mezclar(pico(roce(0.35, 1.0, 1.2), 1.0), en(0.05, pico(pb(ruido(0.15), 1200) * caida(0.15, 0.05), 0.5)))
    bs.guardar('aparece', x, alto=0.85)


# ======================================================================================================================
#  El Marchito
# ======================================================================================================================
def zumbido_oscuro(dur, f=55.0, sube=1.0):
    """El zumbido del Wither (el nuestro): un acorde grave e inarmónico que tiembla."""
    n = n_(dur)
    fr = f * curva(n, [(0, 1.0), (1, sube)])
    return seno(fr, dur, ((1, 1.0), (1.49, 0.6), (2.03, 0.4), (2.97, 0.25)), 0.02, 4.5)


def marchito():
    bs.empezar('marchito', ('abismo', 4500))
    bs.subtitulos('marchito', {
        'ambiente': ('Susurran unos pétalos secos', 'Dry petals whisper'),
        'herido': ('Un Creeper Marchito cruje', 'Withered Creeper creaks'),
        'muerte': ('Se marchita un Creeper Marchito', 'Withered Creeper withers away'),
        'paso': ('Pasos secos', 'Dry steps'),
        'mecha': ('Sisea un Creeper Marchito', 'Withered Creeper hisses'),
        'estalla': ('Estalla un Creeper Marchito', 'Withered Creeper explodes'),
    })
    for k in range(3):
        d = 1.2 + 0.3 * k
        x = mezclar(pico(roce(d, 1.0, 0.55), 0.7), pico(susurro(d, 'u', 0.8 + 0.1 * k), 0.6),
                    pico(zumbido_oscuro(d, 50 + 4 * k) * campana_env(d, 1.5), 0.2))
        bs.guardar('ambiente', reverb(x, 0.25, 1.6), k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(tallos(0.25, 7), 1.0), pico(roce(0.25, 1.0, 0.6), 0.6))
        bs.guardar('herido', x, k + 1, alto=0.8)
        bs.guardar('paso', pico(roce(0.1, 1.0, 0.5), 1.0), k + 1, alto=0.4)
    x = mezclar(pico(tallos(1.0, 14), 0.8), pico(roce(1.4, 1.0, 0.5) * np.linspace(1, 0, n_(1.4)), 0.7),
                pico(zumbido_oscuro(1.6, 60, 0.6) * caida(1.6, 0.5), 0.45))
    bs.guardar('muerte', reverb(x, 0.3, 1.8), alto=0.8)
    dur = 1.6
    n = n_(dur)
    sis = filtro_mov(ruido(dur), curva(n, [(0, 1800), (1, 4200)]), 'band', 2.5) * curva(n, [(0, 0.2), (1, 1.0)])
    x = mezclar(pico(sis, 0.6), pico(zumbido_oscuro(dur, 55, 2.0) * curva(n, [(0, 0.1), (1, 1.0)]), 0.6),
                pico(roce(dur, 1.0, 0.7), 0.4))
    bs.guardar('mecha', x, alto=0.85)
    # El estallido: el golpe, los pétalos que salen volando y el zumbido del Wither que se queda.
    x = mezclar(estallido(1.0, 1.4), en(0.05, pico(soplo(0.9, 2500, 600, 1.0, 0.1), 0.6)),
                en(0.15, pico(roce(1.2, 1.0, 0.6) * np.linspace(1, 0, n_(1.2)), 0.5)),
                en(0.2, pico(zumbido_oscuro(2.4, 48, 0.85) * caida(2.4, 0.9, 0.2), 0.45)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.6), 0.25, 2.0), alto=0.95, limite=0.75)


# ======================================================================================================================
#  La Enredadera
# ======================================================================================================================
def enredadera():
    bs.empezar('enredadera', ('plaza', 6000))
    bs.subtitulos('enredadera', {
        'ambiente': ('Cruje un Creeper Enredadera', 'Vine Creeper creaks'),
        'herido': ('Un Creeper Enredadera recibe un golpe', 'Vine Creeper hurts'),
        'muerte': ('Se rompe un Creeper Enredadera', 'Vine Creeper snaps apart'),
        'paso': ('Pasos de madera', 'Wooden steps'),
        'mecha': ('Se tensan unas lianas', 'Vines tighten'),
        'estalla': ('Estalla un Creeper Enredadera', 'Vine Creeper explodes'),
        'latigo': ('Restallan unas lianas', 'Vines lash'),
        'atrapa': ('Unas lianas te atrapan', 'Vines grab you'),
        'suelta': ('Se rompen unas lianas', 'Vines snap'),
    })
    for k in range(3):
        d = 0.9 + 0.3 * k
        x = mezclar(pico(crujido(d, 25 + 10 * k, 70 + 20 * k, 450 + 120 * k), 0.8), en(0.2, pico(roce(0.5, 1.0, 0.8), 0.4)))
        bs.guardar('ambiente', reverb(x, 0.15, 1.0), k + 1, alto=0.55)
    for k in range(2):
        x = mezclar(pico(golpe_madera(170 + 30 * k, 0.4), 1.0), pico(roce(0.3, 1.0, 0.9), 0.5),
                    pico(crujido(0.25, 80, 160, 700), 0.4))
        bs.guardar('herido', x, k + 1, alto=0.8)
        x = mezclar(pico(golpe_madera(120 + 20 * k, 0.15), 1.0), pico(roce(0.08, 1.0, 0.8), 0.3))
        bs.guardar('paso', x, k + 1, alto=0.45)
    x = mezclar(pico(chasquidos(0.5, 160, 500, 6000), 1.0), en(0.1, pico(crujido(1.0, 120, 20, 380), 0.7)),
                en(0.3, pico(roce(0.9, 1.0, 0.8) * np.linspace(1, 0, n_(0.9)), 0.5)), pico(golpe_madera(110, 0.6), 0.6))
    bs.guardar('muerte', reverb(x, 0.2, 1.4), alto=0.85)
    dur = 2.0
    n = n_(dur)
    x = mezclar(pico(crujido(dur, 20, 260, 520), 0.9),
                pico(filtro_mov(ruido(dur), curva(n, [(0, 2000), (1, 5500)]), 'band', 2.0) * curva(n, [(0, 0.1), (1, 0.8)]), 0.5))
    bs.guardar('mecha', x, alto=0.85)
    x = mezclar(estallido(1.0, 1.4), en(0.03, pico(chasquidos(0.8, curva(n_(0.8), [(0, 200), (1, 10)]), 500, 7000), 0.6)),
                en(0.1, pico(roce(1.3, 1.0, 0.9) * np.linspace(1, 0, n_(1.3)), 0.5)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.6), 0.2, 1.5), alto=0.95, limite=0.75)
    # El latigazo: el aire que corta y el restallido seco al final.
    x = mezclar(pico(soplo(0.3, 600, 3500, 1.4, 0.3), 0.8), en(0.24, pico(chasquidos(0.05, 600, 1500, 9000), 1.0)),
                en(0.24, pico(bp(ruido(0.04), 2000, 9000) * caida(0.04, 0.008), 0.8)))
    bs.guardar('latigo', x, alto=0.85)
    # Te atrapa: las lianas se enroscan (roce que sube) y aprietan crujiendo.
    n = n_(0.8)
    x = mezclar(pico(filtro_mov(ruido(0.8, 'rosa'), curva(n, [(0, 700), (1, 2600)]), 'band', 2.5) * ventana(0.8, 0.05, 0.3), 0.7),
                en(0.25, pico(crujido(0.6, 60, 200, 520), 0.9)), en(0.05, pico(golpe_madera(140, 0.3), 0.5)))
    bs.guardar('atrapa', x, alto=0.85)
    # Te sueltas: chasquido de madera rota y las hojas.
    x = mezclar(pico(chasquidos(0.12, 400, 600, 8000), 1.0), pico(golpe_madera(260, 0.3), 0.6),
                en(0.05, pico(roce(0.5, 1.0, 1.0), 0.5)))
    bs.guardar('suelta', x, alto=0.85)


# ======================================================================================================================
#  La Gelatina
# ======================================================================================================================
def gelatina():
    bs.empezar('gelatina', ('abismo', 5000))
    bs.subtitulos('gelatina', {
        'ambiente': ('Burbujea un Creeper Gelatina', 'Jelly Creeper bubbles'),
        'herido': ('Un Creeper Gelatina se aplasta', 'Jelly Creeper squishes'),
        'muerte': ('Se derrite un Creeper Gelatina', 'Jelly Creeper melts'),
        'paso': ('Pasos blandos', 'Squishy steps'),
        'mecha': ('Hierve un Creeper Gelatina', 'Jelly Creeper boils'),
        'estalla': ('Estalla un Creeper Gelatina', 'Jelly Creeper bursts'),
        'estatica': ('Se pierde la señal', 'Signal lost'),
    })
    for k in range(3):
        d = 1.0 + 0.3 * k
        x = mezclar(pico(burbujas(d, 8 + 3 * k, 250, 1100), 0.8), en(0.3, pico(chof(0.3, 700, 300, 6), 0.5)))
        bs.guardar('ambiente', reverb(x, 0.2, 1.2), k + 1, alto=0.55)
    for k in range(2):
        x = mezclar(pico(chof(0.3, 1300 - 200 * k, 280, 4), 1.0), pico(burbujas(0.25, 30, 400, 1400), 0.4))
        bs.guardar('herido', x, k + 1, alto=0.8)
        bs.guardar('paso', pico(chof(0.12, 800 + 150 * k, 300, 5), 1.0), k + 1, alto=0.45)
    x = mezclar(pico(chof(0.6, 1200, 180, 3), 1.0), en(0.15, pico(burbujas(1.2, curva(n_(1.2), [(0, 40), (1, 2)]), 200, 900), 0.6)),
                en(0.8, pico(chof(0.25, 500, 150, 6), 0.5)))
    bs.guardar('muerte', reverb(x, 0.25, 1.5), alto=0.85)
    dur = 1.6
    n = n_(dur)
    x = mezclar(pico(burbujas(dur, curva(n, [(0, 6), (1, 80)]), 250, 1600), 0.9),
                pico(seno(curva(n, [(0, 180), (1, 420)]), dur, ((1, 1.0), (2, 0.3)), 0.04, 9) * curva(n, [(0, 0.05), (1, 0.5)]), 0.4))
    bs.guardar('mecha', x, alto=0.85)
    x = mezclar(estallido(0.9, 1.2), pico(chof(0.7, 2200, 200, 2), 0.8), en(0.25, pico(estatica(0.9), 0.5)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.6), 0.2, 1.5), alto=0.95, limite=0.75)
    bs.guardar('estatica', pico(estatica(2.4), 1.0), alto=0.6)


# ======================================================================================================================
#  El Atómico
# ======================================================================================================================
def atomico():
    bs.empezar('atomico', ('cumbre', 6000))
    bs.subtitulos('atomico', {
        'ambiente': ('Chasquea un contador Geiger', 'A Geiger counter clicks'),
        'herido': ('Resuena la chapa de un Creeper Atómico', 'Atomic Creeper clangs'),
        'muerte': ('Se apaga un Creeper Atómico', 'Atomic Creeper powers down'),
        'paso': ('Pasos de acero', 'Heavy steel steps'),
        'mecha': ('Suena la alarma de un Creeper Atómico', 'Atomic Creeper alarm'),
        'estalla': ('Estalla un Creeper Atómico', 'Atomic Creeper detonates'),
        'onda': ('Llega la onda expansiva', 'Shockwave hits'),
    })
    for k in range(3):
        d = 1.4 + 0.3 * k
        t = t_(d)
        zumbido = seno(60.0, d, ((1, 0.5), (2, 1.0), (3, 0.35), (5, 0.15))) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t))
        x = mezclar(pico(geiger(d, curva(n_(d), [(0, 6 + 4 * k), (0.5, 18), (1, 5)])), 0.9), pico(zumbido, 0.25))
        bs.guardar('ambiente', x, k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(clang(300 + 60 * k, 0.9, 0.2), 1.0), pico(boom(110, 60, 0.05, 0.3), 0.5),
                    pico(geiger(0.4, 60), 0.3))
        bs.guardar('herido', x, k + 1, alto=0.8)
        x = mezclar(pico(boom(85, 40, 0.06, 0.3), 1.0), pico(clang(140 + 20 * k, 0.3, 0.05), 0.4))
        bs.guardar('paso', x, k + 1, alto=0.55)
    d = 2.2
    n = n_(d)
    x = mezclar(pico(clang(260, 1.6, 0.3), 0.8), en(0.25, pico(clang(410, 1.2, 0.2), 0.5)),
                pico(seno(curva(n, [(0, 120), (1, 30)]), d, ((1, 1.0), (2, 0.5), (3, 0.3))) * caida(d, 0.8), 0.5),
                pico(geiger(d, curva(n, [(0, 30), (1, 0)])), 0.4))
    bs.guardar('muerte', reverb(x, 0.2, 1.6), alto=0.85)
    # La mecha: tres segundos de sirena (la del mod) con el Geiger que se vuelve loco.
    dur = 3.0
    n = n_(dur)
    x = mezclar(pico(sirena(dur, 480, 960, 3.0), 0.8), pico(geiger(dur, curva(n, [(0, 20), (1, 260)])), 0.6),
                pico(seno(55.0, dur, ((1, 1.0), (2, 0.4))) * curva(n, [(0, 0.1), (1, 0.7)]), 0.3))
    bs.guardar('mecha', reverb(x, 0.15, 1.2), alto=0.9)
    # El estallido: un trueno que no acaba (el golpe, el rugido largo, los cascotes) y el silencio con el Geiger.
    dur = 6.0
    n = n_(dur)
    x = mezclar(pico(boom(45, 16, 0.9, 4.0), 1.0), pico(bp(ruido(0.5), 150, 2500) * caida(0.5, 0.12), 0.8),
                pico(retumbo(dur, 40, 1.8), 0.9), en(0.3, pico(chasquidos(3.0, curva(n_(3.0), [(0, 120), (1, 2)]), 300, 4000), 0.4)),
                en(3.0, pico(geiger(3.0, curva(n_(3.0), [(0, 40), (1, 8)])), 0.15)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 2.2), 0.3, 3.0), alto=0.98, limite=0.7, largo=7.0)
    # La onda que llega lejos: el aire que empuja y un retumbo.
    x = mezclar(pico(soplo(1.4, 180, 60, 0.8, 0.0), 1.0), pico(retumbo(2.0, 35, 0.8), 0.8),
                pico(boom(60, 25, 0.3, 1.2), 0.6))
    bs.guardar('onda', reverb(x, 0.25, 2.0), alto=0.9, limite=0.75)


# ======================================================================================================================
#  El Ciego
# ======================================================================================================================
def ciego():
    bs.empezar('ciego', ('abismo', 3500))
    bs.subtitulos('ciego', {
        'ambiente': ('Chasquea un Creeper Ciego', 'Blind Creeper clicks'),
        'herido': ('Un Creeper Ciego cruje', 'Blind Creeper crunches'),
        'muerte': ('Se apaga un Creeper Ciego', 'Blind Creeper fades'),
        'paso': ('Pasos sordos', 'Muffled steps'),
        'mecha': ('Vibra un Creeper Ciego', 'Blind Creeper vibrates'),
        'estalla': ('Estalla un Creeper Ciego', 'Blind Creeper explodes'),
        'escucha': ('Algo te ha oído', 'Something heard you'),
        'chillido': ('Chilla un Creeper Ciego', 'Blind Creeper shrieks'),
    })
    for k in range(3):
        d = 1.2 + 0.3 * k
        n = n_(d)
        x = mezclar(pico(clics(d, curva(n, [(0, 3), (0.5, 9 + 3 * k), (1, 4)]), 1500, 6000), 0.8),
                    pico(seno(70.0 + 8 * k, d, ((1, 1.0), (1.5, 0.4))) * campana_env(d, 1.2), 0.25))
        bs.guardar('ambiente', reverb(x, 0.3, 1.8), k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(chasquidos(0.25, 200, 300, 3000), 1.0), pico(clics(0.25, 40, 2000, 7000), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.8)
        bs.guardar('paso', pico(pb(ruido(0.1), 300 + 60 * k) * caida(0.1, 0.03), 1.0), k + 1, alto=0.4)
    n = n_(1.6)
    x = mezclar(pico(chasquidos(0.8, curva(n_(0.8), [(0, 150), (1, 5)]), 300, 3000), 0.8),
                pico(clics(1.6, curva(n, [(0, 30), (1, 1)]), 1500, 6000), 0.5),
                pico(seno(curva(n, [(0, 160), (1, 50)]), 1.6, ((1, 1.0), (1.5, 0.5))) * caida(1.6, 0.6), 0.4))
    bs.guardar('muerte', reverb(x, 0.3, 2.0), alto=0.85)
    # Te oye: un tren de clics que se acelera hasta zumbar.
    n = n_(0.6)
    bs.guardar('escucha', pico(clics(0.6, curva(n, [(0, 12), (1, 90)]), 1500, 8000) * ventana(0.6, 0.01, 0.15), 1.0),
               alto=0.8)
    bs.guardar('chillido', reverb(chillido(1.0), 0.3, 2.0), alto=0.85)
    dur = 1.6
    n = n_(dur)
    x = mezclar(pico(clics(dur, curva(n, [(0, 15), (1, 160)]), 1500, 8000), 0.7),
                pico(chillido(dur, 180, 520) * curva(n, [(0, 0.1), (1, 1.0)]), 0.7))
    bs.guardar('mecha', x, alto=0.85)
    x = mezclar(estallido(1.0, 1.4), en(0.1, pico(chillido(1.4, 600, 240), 0.5)),
                en(0.05, pico(clics(1.0, curva(n_(1.0), [(0, 120), (1, 4)]), 1500, 7000), 0.4)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.6), 0.3, 2.2), alto=0.95, limite=0.75)


# ======================================================================================================================
#  La Tarta
# ======================================================================================================================
def tarta():
    bs.empezar('tarta', ('plaza', 7000))
    bs.subtitulos('tarta', {
        'ambiente': ('Suena un matasuegras', 'A party horn toots'),
        'herido': ('Un Creeper Tarta se aplasta', 'Cake Creeper squishes'),
        'muerte': ('Se desmigaja un Creeper Tarta', 'Cake Creeper crumbles'),
        'paso': ('Pasos de nata', 'Creamy steps'),
        'mecha': ('Chisporrotean unas velas', 'Candles fizz'),
        'estalla': ('Estalla un Creeper Tarta', 'Cake Creeper splatters'),
        'aparece': ('Salta un corcho', 'A cork pops'),
        'pringue': ('Te salpica la nata', 'Cream splatters you'),
    })
    bs.guardar('ambiente', matasuegras(0.55, 430, 480), 1, alto=0.6)
    bs.guardar('ambiente', mezclar(pico(chof(0.3, 900, 350, 5), 0.7), en(0.15, pico(chasquidos(0.5, 25, 3000, 10000), 0.4))),
               2, alto=0.5)
    bs.guardar('ambiente', mezclar(matasuegras(0.25, 470, 500), en(0.3, matasuegras(0.35, 450, 520))), 3, alto=0.6)
    for k in range(2):
        x = mezclar(pico(chof(0.25, 1100 + 150 * k, 300, 4), 1.0), pico(chasquidos(0.2, 80, 1500, 6000), 0.3))
        bs.guardar('herido', x, k + 1, alto=0.8)
        bs.guardar('paso', pico(chof(0.1, 900 + 150 * k, 350, 5), 1.0), k + 1, alto=0.4)
    # La muerte: se desmigaja y el matasuegras que se desinfla.
    n = n_(0.9)
    desinfla = matasuegras(0.9, 420, 300) * curva(n, [(0, 1.0), (1, 0.2)])
    x = mezclar(pico(chof(0.4, 1200, 250, 3), 0.8), en(0.1, pico(chasquidos(0.6, 60, 2000, 8000), 0.4)), en(0.25, pico(desinfla, 0.6)))
    bs.guardar('muerte', x, alto=0.8)
    # La mecha (cortísima): las velas que chisporrotean y el matasuegras que sube.
    dur = 0.6
    n = n_(dur)
    x = mezclar(pico(chasquidos(dur, curva(n, [(0, 80), (1, 400)]), 3000, 11000), 0.7),
                pico(matasuegras(dur, 380, 760), 0.7))
    bs.guardar('mecha', x, alto=0.85)
    x = mezclar(estallido(0.9, 1.0, 90, 40, 0.25), pico(chof(0.6, 2600, 300, 2), 1.0),
                en(0.1, pico(chasquidos(0.8, curva(n_(0.8), [(0, 120), (1, 5)]), 1500, 8000), 0.4)))
    bs.guardar('estalla', reverb(saturar(pico(x, 1.0), 1.5), 0.15, 1.0), alto=0.95, limite=0.75)
    # El corcho: un «pop» seco y redondo.
    x = mezclar(pico(boom(320, 180, 0.012, 0.08), 1.0), pico(bp(ruido(0.02), 1500, 6000) * caida(0.02, 0.004), 0.6))
    bs.guardar('aparece', x, alto=0.85)
    bs.guardar('pringue', mezclar(pico(chof(0.35, 2000, 300, 2.5), 1.0), en(0.05, pico(chof(0.25, 1400, 400, 4), 0.5))),
               alto=0.8)


MOBS = {'matojo': matojo, 'marchito': marchito, 'enredadera': enredadera, 'gelatina': gelatina,
        'atomico': atomico, 'ciego': ciego, 'tarta': tarta}


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    ms.RAIZ = raiz
    ms.SONIDOS = raiz + '/src/main/resources/assets/atalaya/sounds'
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    for p in pedidos:
        MOBS[p]()
    bs.escribir_json(raiz)
    if len(sys.argv) > 2 and sys.argv[2] != '-':
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
