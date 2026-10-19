"""
Los sonidos de los phantoms del bestiario (bestia.<id>.<nombre>): los dos chillan como un phantom (un chillido ronco
que resbala hacia abajo, por la garganta), baten las alas de cuero y, al lanzarse en picado, el aire silba.

  phantom_oscuro     la pesadilla: el chillido más grave, con mucha sala; al golpearte, el desgarro (un tirón de cuero
                     y lo que se te cae, que repica en el suelo)
  phantom_explosivo  la brasa: el chillido con el chisporroteo de sus grietas; la mecha que corre y el estallido

Todos: ambiente (×3), herido (×2), muerte y picado. No tienen pasos: vuelan.

Uso: python bestiario_sonidos_phantoms.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from bestiario_sonidos_bombas import aleteo, golpe_bomba, mecha_corre
from minijefes_sonidos import (boom, bp, caida, chasquidos, curva, en, filtro_mov, formantes, garganta, mezclar, modos,
                               n_, pb, pico, reverb, ruido, saturar, t_, ventana)

rng = np.random.default_rng(20261019)


def chillido(dur, f0, f1, vocal='a', aspero=0.7):
    """El chillido del phantom: una voz ronca que resbala de f0 a f1, con un temblor."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.2, f0 * 1.08), (1, f1)]) * (1 + 0.03 * np.sin(2 * np.pi * 9 * t_(dur)))
    v = garganta(f, dur, formantes(vocal, 1.3), aspereza=aspero, sub=0.05, jitter=0.06, aliento=0.35, caos=0.4)
    return v * ventana(dur, 0.02, dur * 0.4)


def picado(dur=0.8):
    """El aire que silba al lanzarse en picado: un soplo que baja de tono y crece."""
    n = n_(dur)
    s = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 2600), (1, 700)]), 'band', 2.5) * curva(n, [(0, 0.2), (0.8, 1.0), (1, 0.0)])
    return s


def brasas(dur, tasa=60.0):
    """El chisporroteo de las grietas de brasa."""
    return chasquidos(dur, tasa, 1500, 7000) * ventana(dur, 0.05, dur * 0.3)


def desgarro():
    """El desgarro del Oscuro: un tirón de cuero y lo que se te cae, que repica."""
    tiron = bp(ruido(0.25), 500, 4000) * curva(n_(0.25), [(0, 0.2), (0.15, 1.0), (1, 0.0)])
    raspa = mezclar(pico(tiron, 1.0), pico(chasquidos(0.25, 160, 800, 5000), 0.6))
    caen = mezclar(*[en(0.18 + 0.09 * k, pico(modos(900 + 300 * k, 0.25, ((1, 1.0), (2.7, 0.4)), 0.08, 0.003),
                                              0.5 - 0.1 * k)) for k in range(3)])
    return mezclar(raspa, caen)


def comunes(ident, nombre_es, nombre_en, f0, vocal, sala, extra_subs, chispas=0.0):
    bs.empezar(ident, sala)
    subs = {
        'ambiente': (f'Chilla un {nombre_es}', f'{nombre_en} screeches'),
        'herido': (f'Se queja un {nombre_es}', f'{nombre_en} hurts'),
        'muerte': (f'Muere un {nombre_es}', f'{nombre_en} dies'),
        'paso': ('Bate unas alas', 'Wings flap'),
        'picado': (f'Se lanza en picado un {nombre_es}', f'{nombre_en} swoops'),
    }
    subs.update(extra_subs)
    bs.subtitulos(ident, subs)
    for k in range(3):
        d = 1.0 + 0.25 * k
        x = mezclar(pico(chillido(d, f0 * (1.1 + 0.1 * k), f0 * 0.7, vocal), 0.8), pico(aleteo(d, 3.0, 500), 0.4),
                    pico(brasas(d), chispas))
        bs.guardar('ambiente', reverb(x, 0.4, 2.2), k + 1, alto=0.55)
    for k in range(2):
        x = mezclar(pico(chillido(0.4, f0 * (1.6 + 0.2 * k), f0 * 1.1, 'e', 0.9), 1.0), pico(aleteo(0.4, 7.0, 600), 0.4))
        bs.guardar('herido', x, k + 1, alto=0.75)
    x = mezclar(pico(chillido(1.6, f0 * 1.3, f0 * 0.4, vocal), 0.9),
                pico(aleteo(1.2, 6.0, 500) * curva(n_(1.2), [(0, 1), (1, 0)]), 0.5))
    bs.guardar('muerte', reverb(x, 0.45, 2.4), alto=0.8)
    bs.guardar('paso', aleteo(0.5, 4.0, 500), alto=0.35)
    x = mezclar(pico(picado(0.8), 0.9), en(0.5, pico(chillido(0.4, f0 * 1.4, f0 * 0.9, 'a', 0.8), 0.7)))
    bs.guardar('picado', reverb(x, 0.3, 1.6), alto=0.8)


def phantom_oscuro():
    comunes('phantom_oscuro', 'Phantom Oscuro', 'Dark Phantom', 210, 'o', ('abismo', 4200), {
        'arranca': ('Un Phantom Oscuro te arranca lo que llevas', 'Dark Phantom rips your items away'),
    })
    bs.guardar('arranca', reverb(desgarro(), 0.3, 1.6), alto=0.85)


def phantom_explosivo():
    comunes('phantom_explosivo', 'Phantom Explosivo', 'Explosive Phantom', 260, 'a', ('plaza', 6000), {
        'mecha': ('Chisporrotea una mecha', 'A fuse fizzes'),
        'estalla': ('Estalla una brasa', 'An ember explodes'),
    }, chispas=0.4)
    bs.guardar('mecha', mezclar(pico(mecha_corre(1.5), 0.9), pico(brasas(1.5, 90), 0.5)), alto=0.85)

    def llamas(dur):
        n = n_(dur)
        return mezclar(pico(pb(ruido(dur, 'rosa'), 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t_(dur)))), 0.8),
                       pico(chasquidos(dur, curva(n, [(0, 80), (1, 20)]), 1500, 7000), 0.5)) * ventana(dur, 0.05, dur * 0.4)
    x = reverb(saturar(pico(mezclar(golpe_bomba(), en(0.08, pico(llamas(1.4), 0.6))), 1.0), 1.6), 0.2, 1.5)
    bs.guardar('estalla', x, alto=0.95, limite=0.75)


MOBS = {'phantom_oscuro': phantom_oscuro, 'phantom_explosivo': phantom_explosivo}


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
