"""
Los sonidos de las bombas voladoras del bestiario (bestia.<id>.<nombre>): cada una con sus alas y su material.

  ambar    el zumbido de las alas de insecto, el cristal que tintinea; al estallar, el siseo del agua que se seca
  carmesi  el zumbido grave de libélula, el hierro que resuena; al estallar, las llamas que prenden
  negra    el aleteo de cuero de murciélago, el hierro macizo; el estallido más grande
  abismo   el aleteo de membrana y los clics del sculk; al estallar, el chillido que deja la oscuridad

Todas: ambiente (×3), herido (×2), muerte, mecha (la chispa que corre y las alas que se vuelven locas) y estalla. No
tienen pasos: vuelan.

Uso: python bestiario_sonidos_bombas.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, caida, chasquidos, clics, curva, en, filtro_mov, mezclar, modos, n_, pa, pb,
                               pico, reverb, ruido, saturar, seno, t_, ventana)

rng = np.random.default_rng(20261019)


def zumbido(dur, f, vel=1.0, aspero=0.6):
    """Las alas que baten muy deprisa: un tono grave con sus armónicos, modulado por el batido."""
    t = t_(dur)
    batido = 0.6 + 0.4 * np.sin(2 * np.pi * f * 0.5 * t)
    s = seno(f * (1 + 0.02 * np.sin(2 * np.pi * 3 * vel * t)), dur, tuple((k, 1.0 / k ** aspero) for k in range(1, 9)))
    return s * batido * ventana(dur, 0.06, dur * 0.3)


def aleteo(dur, tasa, grave=600.0, fuerza=1.0):
    """Alas grandes que empujan el aire (cuero, membrana): golpes de aire grave a ritmo."""
    n = n_(dur)
    out = np.zeros(n)
    t = 0.0
    while t < dur:
        d = 0.09
        golpe = pb(ruido(d, 'rosa'), grave) * np.sin(np.pi * np.linspace(0, 1, n_(d))) ** 1.5
        i = int(t * ms.SR)
        out[i:i + len(golpe)] += golpe[:max(0, n - i)] * rng.uniform(0.7, 1.0)
        t += 1.0 / tasa
    return out * fuerza


def mecha_corre(dur):
    """La chispa que corre por la mecha: un chisporroteo fino que se acelera."""
    n = n_(dur)
    sis = filtro_mov(ruido(dur), curva(n, [(0, 3500), (1, 7000)]), 'band', 2.0) * curva(n, [(0, 0.3), (1, 1.0)])
    return mezclar(pico(sis, 0.6), pico(chasquidos(dur, curva(n, [(0, 40), (1, 220)]), 3000, 11000), 0.6))


def tintineo(f=2600.0, dur=0.6):
    """Cristal de ámbar que tintinea."""
    return modos(f, dur, ((1, 1.0), (2.32, 0.5), (4.25, 0.25), (6.6, 0.12)), 0.12, 0.003)


def hierro(f=420.0, dur=0.8):
    """Hierro que resuena (la bomba golpeada)."""
    return modos(f, dur, ((1, 1.0), (2.76, 0.55), (5.4, 0.3), (8.93, 0.16)), 0.18, 0.002)


def golpe_bomba(golpe=1.0, f0=75, f1=28, tau=0.4):
    return mezclar(pico(boom(f0, f1, tau, 2.0), golpe), pico(bp(ruido(0.3), 300, 3500) * caida(0.3, 0.07), 0.7 * golpe),
                   pico(pb(ruido(1.6, 'marron'), 100) * caida(1.6, 0.5, 0.04), 0.5 * golpe))


def comunes(ident, subs, amb, her, muere, mecha, estalla):
    bs.empezar(ident, subs.pop('_sala'))
    bs.subtitulos(ident, subs)
    for k in range(3):
        bs.guardar('ambiente', amb(k), k + 1, alto=0.5)
    for k in range(2):
        bs.guardar('herido', her(k), k + 1, alto=0.8)
    bs.guardar('muerte', muere(), alto=0.85)
    bs.guardar('mecha', mecha(), alto=0.85)
    bs.guardar('estalla', estalla(), alto=0.95, limite=0.75)


def ambar():
    comunes('ambar', {
        '_sala': ('plaza', 7000),
        'ambiente': ('Zumba una Bomba Ámbar', 'Amber Bomb buzzes'),
        'herido': ('Tintinea una Bomba Ámbar', 'Amber Bomb clinks'),
        'muerte': ('Se apaga una Bomba Ámbar', 'Amber Bomb fizzles out'),
        'mecha': ('Chisporrotea una mecha', 'A fuse fizzes'),
        'estalla': ('Estalla una Bomba Ámbar', 'Amber Bomb explodes'),
    },
        lambda k: mezclar(pico(zumbido(1.0 + 0.2 * k, 190 + 25 * k), 0.8), en(0.3, pico(tintineo(2400 + 300 * k, 0.4), 0.2))),
        lambda k: mezclar(pico(tintineo(2200 + 400 * k, 0.5), 1.0), pico(zumbido(0.25, 260), 0.4)),
        lambda: mezclar(pico(tintineo(2000, 0.9), 0.7), pico(zumbido(1.0, 220) * np.linspace(1, 0, n_(1.0)), 0.6),
                        en(0.3, pico(chasquidos(0.5, 60, 2000, 8000), 0.4))),
        lambda: mezclar(pico(mecha_corre(1.0), 0.8), pico(zumbido(1.0, 320, 3.0), 0.6)),
        lambda: reverb(saturar(pico(mezclar(golpe_bomba(), en(0.05, pico(chasquidos(0.6, 200, 3000, 11000), 0.5)),
                                            en(0.1, pico(pa(ruido(1.6), 3000) * caida(1.6, 0.5), 0.5))), 1.0), 1.6),
                       0.2, 1.5))


def carmesi():
    def llamas(dur):
        n = n_(dur)
        return mezclar(pico(pb(ruido(dur, 'rosa'), 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t_(dur)))), 0.8),
                       pico(chasquidos(dur, curva(n, [(0, 80), (1, 20)]), 1500, 7000), 0.5)) * ventana(dur, 0.05, dur * 0.4)
    comunes('carmesi', {
        '_sala': ('plaza', 6000),
        'ambiente': ('Zumba una Bomba Carmesí', 'Crimson Bomb drones'),
        'herido': ('Resuena una Bomba Carmesí', 'Crimson Bomb clangs'),
        'muerte': ('Se apaga una Bomba Carmesí', 'Crimson Bomb fizzles out'),
        'mecha': ('Chisporrotea una mecha', 'A fuse fizzes'),
        'estalla': ('Estalla una Bomba Carmesí', 'Crimson Bomb explodes'),
    },
        lambda k: pico(zumbido(1.1 + 0.2 * k, 120 + 15 * k, 1.5, 0.4), 0.8),
        lambda k: mezclar(pico(hierro(380 + 60 * k, 0.6), 1.0), pico(zumbido(0.25, 140), 0.4)),
        lambda: mezclar(pico(hierro(300, 1.2), 0.7), pico(zumbido(1.0, 130) * np.linspace(1, 0, n_(1.0)), 0.6)),
        lambda: mezclar(pico(mecha_corre(1.0), 0.8), pico(zumbido(1.0, 180, 3.0, 0.4), 0.6)),
        lambda: reverb(saturar(pico(mezclar(golpe_bomba(), en(0.08, pico(llamas(1.6), 0.6))), 1.0), 1.6), 0.2, 1.5))


def negra():
    comunes('negra', {
        '_sala': ('plaza', 5500),
        'ambiente': ('Aletea una Bomba Negra', 'Black Bomb flaps'),
        'herido': ('Resuena una Bomba Negra', 'Black Bomb clangs'),
        'muerte': ('Cae una Bomba Negra', 'Black Bomb falls'),
        'mecha': ('Chisporrotea una mecha gorda', 'A thick fuse fizzes'),
        'estalla': ('Estalla una Bomba Negra', 'Black Bomb explodes'),
    },
        lambda k: pico(aleteo(1.2 + 0.2 * k, 2.2 + 0.3 * k, 500), 0.8),
        lambda k: mezclar(pico(hierro(200 + 30 * k, 1.0), 1.0), pico(boom(110, 60, 0.05, 0.3), 0.5)),
        lambda: mezclar(pico(hierro(160, 1.4), 0.6), pico(aleteo(0.8, 4, 400) * np.linspace(1, 0, n_(0.8)), 0.6),
                        en(0.7, pico(boom(80, 40, 0.1, 0.5), 0.8))),
        lambda: mezclar(pico(mecha_corre(1.2), 0.8), pico(aleteo(1.2, 6, 500), 0.6)),
        lambda: reverb(saturar(pico(mezclar(golpe_bomba(1.0, 60, 22, 0.6),
                                            en(0.1, pico(chasquidos(1.2, curva(n_(1.2), [(0, 120), (1, 4)]), 300, 4000), 0.5))),
                                    1.0), 1.9), 0.25, 2.0))


def abismo():
    def chillido(dur):
        n = n_(dur)
        f = curva(n, [(0, 300), (0.3, 560), (1, 640)])
        tono = seno(f, dur, ((1, 1.0), (1.51, 0.5), (2.23, 0.35)), 0.03, 11)
        aire = filtro_mov(ruido(dur), f * 3.2, 'band', 8)
        return mezclar(pico(tono, 0.8), pico(aire, 0.6)) * ventana(dur, 0.05, dur * 0.45)
    comunes('abismo', {
        '_sala': ('abismo', 3500),
        'ambiente': ('Chasquea una Bomba del Abismo', 'Abyss Bomb clicks'),
        'herido': ('Cruje una Bomba del Abismo', 'Abyss Bomb crunches'),
        'muerte': ('Se apaga una Bomba del Abismo', 'Abyss Bomb fades'),
        'mecha': ('Vibra una mecha', 'A fuse vibrates'),
        'estalla': ('Estalla una Bomba del Abismo', 'Abyss Bomb shrieks'),
    },
        lambda k: reverb(mezclar(pico(aleteo(1.2 + 0.2 * k, 2.6, 380, 0.7), 0.6),
                                 pico(clics(1.2 + 0.2 * k, curva(n_(1.2 + 0.2 * k), [(0, 4), (0.5, 12), (1, 4)]), 1500, 6000), 0.6)),
                         0.3, 1.8),
        lambda k: mezclar(pico(chasquidos(0.25, 200, 300, 3000), 1.0), pico(clics(0.25, 40, 2000, 7000), 0.5)),
        lambda: reverb(mezclar(pico(clics(1.4, curva(n_(1.4), [(0, 30), (1, 1)]), 1500, 6000), 0.6),
                               pico(seno(curva(n_(1.4), [(0, 160), (1, 50)]), 1.4, ((1, 1.0), (1.5, 0.5))) * caida(1.4, 0.5), 0.4)),
                       0.3, 2.0),
        lambda: mezclar(pico(clics(1.0, curva(n_(1.0), [(0, 15), (1, 160)]), 1500, 8000), 0.7),
                        pico(chillido(1.0) * curva(n_(1.0), [(0, 0.1), (1, 1.0)]), 0.6)),
        lambda: reverb(saturar(pico(mezclar(golpe_bomba(), en(0.08, pico(chillido(1.4), 0.6))), 1.0), 1.6), 0.3, 2.2))


MOBS = {'ambar': ambar, 'carmesi': carmesi, 'negra': negra, 'abismo': abismo}


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
