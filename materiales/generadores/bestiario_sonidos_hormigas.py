"""
Los sonidos de las hormigas del bestiario (bestia.<id>.<nombre>): todas con el chasquido de las mandíbulas, la
estridulación (el rascado con el que se avisan unas a otras: un tren de clics muy rápido que sube y baja), los pasitos
de seis patas y el mordisco; y cada una lo suyo:

  lancera     el roce de la lanza (un silbido de madera)
  polvorin    la mecha de la bomba y el reventón de barro cocido
  cabezona    todo más grave y el mordisco de tenaza, más fuerte
  radiactiva  el contador Geiger que la acompaña
  brasa       el crepitar de las brasas y el fuego que prende

Uso: python bestiario_sonidos_hormigas.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, caida, chasquidos, clics, curva, en, filtro_mov, mezclar, n_, pb, pico, reverb,
                               ruido, saturar, seno, soplo, t_, ventana)

rng = np.random.default_rng(20261021)


def estridulacion(dur, tasa=180.0, f=2600.0):
    """El rascado de hormiga: un tren de clics muy rápido que sube y baja, resonando en el caparazón."""
    n = n_(dur)
    t = t_(dur)
    vaiven = 0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t + rng.uniform(0, 6))
    c = clics(dur, tasa * (0.5 + vaiven), f * 0.5, f * 2.5)
    return mezclar(pico(c, 1.0), pico(bp(c, f * 0.8, f * 1.3), 0.6)) * ventana(dur, 0.04, dur * 0.3)


def mandibulas(dur, tasa=8.0, f=1800.0):
    """El castañeteo de las mandíbulas: pares de clics secos."""
    n = n_(dur)
    out = np.zeros(n + n_(0.05))
    t = 0.0
    while t < dur:
        for d in (0.0, 0.035):
            c = bp(ruido(0.006), f, f * 4) * caida(0.006, 0.0015)
            i = int((t + d) * ms.SR)
            out[i:i + len(c)] += c * rng.uniform(0.6, 1.0)
        t += rng.exponential(1.0 / tasa)
    return out[:n]


def pasitos(dur, tasa=50.0, f=2800.0):
    return chasquidos(dur, tasa, f * 0.5, f * 2.0)


def mordisco(f=1500.0, fuerza=1.0):
    seco = bp(ruido(0.025), f, f * 5) * caida(0.025, 0.005)
    golpe = boom(f * 0.25, f * 0.12, 0.02, 0.1)
    return mezclar(pico(seco, 1.0), pico(golpe, 0.5 * fuerza))


def geiger(dur, tasa):
    return chasquidos(dur, tasa, 1800, 7500)


def crepitar(dur, tasa=40.0):
    return mezclar(pico(chasquidos(dur, tasa, 1200, 7000), 0.8), pico(pb(ruido(dur, 'rosa'), 700) * 0.3, 0.4))


def hormiga(ident, nombre_es, nombre_en, tono=1.0, extra=None, sala=('plaza', 6000)):
    bs.empezar(ident, sala)
    subs = {
        'ambiente': (f'Rasca una {nombre_es}', f'{nombre_en} chirps'),
        'herido': (f'Chirría una {nombre_es}', f'{nombre_en} squeaks'),
        'muerte': (f'Muere una {nombre_es}', f'{nombre_en} dies'),
        'paso': ('Patitas de hormiga', 'Ant legs patter'),
        'mordisco': (f'Muerde una {nombre_es}', f'{nombre_en} bites'),
    }
    if extra:
        subs.update(extra[0])
    bs.subtitulos(ident, subs)
    for k in range(3):
        d = 0.6 + 0.2 * k
        x = mezclar(pico(estridulacion(d, 160 + 30 * k, 2600 * tono), 0.7), en(0.15, pico(mandibulas(d * 0.7, 6, 1800 * tono), 0.6)))
        if extra and extra[1]:
            x = mezclar(x, pico(extra[1](d), 0.5))
        bs.guardar('ambiente', reverb(x, 0.15, 1.0), k + 1, alto=0.45)
    for k in range(2):
        x = mezclar(pico(estridulacion(0.25, 320, 3400 * tono), 0.9), pico(mandibulas(0.2, 20, 2000 * tono), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.7)
        bs.guardar('paso', pico(pasitos(0.15, 60, 2800 * tono), 1.0), k + 1, alto=0.3)
    n = n_(1.0)
    x = mezclar(pico(estridulacion(1.0, 260, 3000 * tono) * curva(n, [(0, 1.0), (1, 0.0)]), 0.8),
                en(0.3, pico(pasitos(0.6, 40, 2400 * tono) * np.linspace(1, 0, n_(0.6)), 0.5)))
    bs.guardar('muerte', reverb(x, 0.2, 1.2), alto=0.75)
    bs.guardar('mordisco', mordisco(1500 * tono, 1.4 if tono < 0.9 else 1.0), alto=0.8)


def lancera():
    hormiga('lancera', 'Hormiga Lancera', 'Spear Ant', 1.0)


def polvorin():
    hormiga('polvorin', 'Hormiga Polvorín', 'Powder Ant', 1.05, ({
        'mecha': ('Chisporrotea una mecha', 'A fuse fizzes'),
        'estalla': ('Revienta una Hormiga Polvorín', 'Powder Ant bursts'),
    }, lambda d: chasquidos(d, 60, 3500, 11000) * 0.4))
    dur = 1.5
    n = n_(dur)
    sis = filtro_mov(ruido(dur), curva(n, [(0, 3500), (1, 7000)]), 'band', 2.0) * curva(n, [(0, 0.3), (1, 1.0)])
    bs.guardar('mecha', mezclar(pico(sis, 0.7), pico(chasquidos(dur, curva(n, [(0, 40), (1, 240)]), 3000, 11000), 0.6),
                                pico(estridulacion(dur, 400, 3200), 0.4)), alto=0.85)
    golpe = mezclar(pico(boom(80, 30, 0.35, 1.6), 1.0), pico(bp(ruido(0.3), 300, 3500) * caida(0.3, 0.07), 0.7),
                    en(0.05, pico(chasquidos(0.9, curva(n_(0.9), [(0, 160), (1, 4)]), 800, 6000), 0.5)))
    bs.guardar('estalla', reverb(saturar(pico(golpe, 1.0), 1.6), 0.2, 1.5), alto=0.95, limite=0.75)


def cabezona():
    hormiga('cabezona', 'Hormiga Cabezona', 'Bighead Ant', 0.75)


def radiactiva():
    hormiga('radiactiva', 'Hormiga Radiactiva', 'Radiant Ant', 1.1, ({}, lambda d: geiger(d, 9)))


def brasa():
    hormiga('brasa', 'Hormiga Brasa', 'Ember Ant', 1.0, ({
        'quema': ('Prende el fuego de una Hormiga Brasa', 'Ember Ant sets you ablaze'),
    }, lambda d: crepitar(d, 30)))
    x = mezclar(pico(soplo(0.6, 300, 1200, 0.9, 0.0), 1.0), pico(crepitar(0.8, 90), 0.6),
                pico(boom(120, 60, 0.04, 0.3), 0.4))
    bs.guardar('quema', x, alto=0.8)


MOBS = {'lancera': lancera, 'polvorin': polvorin, 'cabezona': cabezona, 'radiactiva': radiactiva, 'brasa': brasa}


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
