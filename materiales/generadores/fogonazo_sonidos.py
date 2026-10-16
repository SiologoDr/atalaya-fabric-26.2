"""
Los sonidos del Fogonazo (16-10-2026), el bicho-luciernaga que estalla en luz. Todos nuestros. Va en silencio (Juan:
«no va a tener ruido, va a ser silencio; un segundo antes de que explote recien va a sonar»; y luego: «sonido cuando le
atacas si debe tener, lo mismo al morir»): nada al andar ni quieto. Solo:

  fogonazo.herido     al pegarle: un chirrido de bicho que se corta, con la luz que chisporrotea
  fogonazo.muerte     al morir: la luz que se muere; chisporrotea cada vez mas despacio, baja de tono y se apaga

  fogonazo.mecha      el farol que se hincha: el zumbido sube y se acelera durante el segundo de aviso, con chispazos
  fogonazo.estallido  el estallido: el chasquido de la luz (seco y brillante), el golpe grave de la explosion, el aire que
                      empuja y el trueno que rueda
  fogonazo.pitido     el pitido del oido mientras la pantalla esta en blanco: agudo y fino, se va apagando

Usa las utilidades de minijefes_sonidos.py. Uso: python fogonazo_sonidos.py <raiz> [hoja]
"""
import sys
import numpy as np

import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, caida, chasquidos, curva, en, filtro_mov, mezclar, n_, pa, pb, pico, reverb,
                               ruido, saturar, t_, ventana)

ms.SUBTITULOS['fogonazo'] = {
    'herido': ('Un Fogonazo chirría', 'Fogonazo screeches'),
    'muerte': ('Se apaga un Fogonazo', 'Fogonazo goes dark'),
    'mecha': ('Un Fogonazo se hincha de luz', 'Fogonazo swells with light'),
    'estallido': ('Estalla un Fogonazo', 'Fogonazo bursts'),
    'pitido': ('Te pitan los oídos', 'Your ears ring'),
}
ms.SALAS['fogonazo'] = ('cumbre', 7000)          # al aire libre, de noche
rng = np.random.default_rng(20261016)


def zumbido(dur, f0=118.0, f1=None, temblor=6.0, brillo=1.0):
    """El zumbido del farol: una luz electrica (la nota y sus armonicos, mas los impares), con un temblor que respira."""
    n = n_(dur)
    t = t_(dur)
    f = np.full(n, f0) if f1 is None else f0 * (f1 / f0) ** (t / dur)
    fase = 2 * np.pi * np.cumsum(f) / ms.SR
    x = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.5), (3, 0.55), (5, 0.3), (7, 0.2), (9, 0.12)):
        x += a * np.sin(k * fase + rng.uniform(0, 6)) * (brillo if k > 2 else 1.0)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(np.broadcast_to(temblor, n)) / ms.SR)
    return x * trem


def chirrido(dur, f0, f1, fuerza=1.0):
    """El chirrido de un bicho: golpecitos muy seguidos (la estridulacion) que barren de tono."""
    n = n_(dur)
    tasa = curva(n, [(0, 90), (1, 60)])
    exc = chasquidos(dur, tasa, 2000, 9000, 1.0)
    tono = filtro_mov(ruido(dur), curva(n, [(0, f0), (1, f1)]), 'band', 6.0)
    return pico(mezclar(pico(exc, 1.0), pico(tono, 0.7)) * ventana(dur, 0.01, dur * 0.4), fuerza)


def herido(k):
    """Al pegarle: un chirrido de bicho que se corta, con la luz que chisporrotea."""
    dur = 0.45
    x = chirrido(dur, 5200 - 600 * k, 2600, 1.0)
    chispa = chasquidos(dur, curva(n_(dur), [(0, 140), (1, 20)]), 1500, 12000, 1.0)
    return reverb(mezclar(pico(x, 1.0), pico(chispa, 0.5), pico(pb(zumbido(dur, 160, 90), 3000, 2) * caida(dur, 0.15), 0.5)),
                  0.15, 1.0)


def muerte():
    """Al morir: la luz que se muere; chisporrotea cada vez mas despacio, baja de tono y se apaga con un soplo."""
    dur = 1.6
    n = n_(dur)
    hum = pb(zumbido(dur, 150.0, 45.0, temblor=curva(n, [(0, 12), (1, 3)])), 2000, 2) * curva(n, [(0, 1), (0.8, 0.4), (1, 0)])
    chispa = chasquidos(dur, curva(n, [(0, 160), (0.6, 30), (1, 2)]), 1200, 11000, 1.0)
    soplo = pb(ruido(0.5, 'rosa'), 1200, 2) * ventana(0.5, 0.05, 0.4)
    x = mezclar(pico(hum, 0.8), pico(chispa, 0.6), en(1.05, pico(soplo, 0.35)), pico(chirrido(0.3, 4800, 2400), 0.5))
    return reverb(x, 0.25, 1.8)


def mecha():
    """Un segundo: lo que dura la mecha (20 ticks)."""
    dur = 1.05
    n = n_(dur)
    t = t_(dur)
    hum = zumbido(dur, 110.0, 520.0, temblor=curva(n, [(0, 6), (1, 40)]), brillo=1.4)
    hum = filtro_mov(hum, curva(n, [(0, 1200), (1, 7000)]), 'low', 0.9) * curva(n, [(0, 0.3), (1, 1.0)]) ** 1.3
    sube = filtro_mov(ruido(dur, 'rosa'), 300 * (14 ** (t / dur)), 'band', 3.0) * curva(n, [(0, 0), (1, 1)]) ** 2
    chispa = chasquidos(dur, curva(n, [(0, 10), (1, 120)]), 2000, 12000, 1.0)
    return mezclar(pico(saturar(pico(hum, 1.0), 1.5), 0.9), pico(sube, 0.4), pico(chispa, 0.35))


def estallido():
    dur = 3.4
    crac = pa(ruido(0.06), 1200) * caida(0.06, 0.006, 0.0005)
    luz = bp(ruido(0.35), 4000, 16000) * caida(0.35, 0.05, 0.001)
    golpe = boom(70, 24, 0.32, 1.8)
    aire = pb(ruido(1.0, 'marron'), 400, 2) * caida(1.0, 0.25, 0.005)
    trueno = pb(ruido(dur, 'marron'), 160, 2) * curva(n_(dur), [(0, 0), (0.03, 1), (0.25, 0.6), (1, 0)])
    rodar = trueno * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.7 * t_(dur))))
    x = mezclar(pico(crac, 1.0), pico(luz, 0.6), pico(golpe, 1.0), pico(aire, 0.7), en(0.04, pico(rodar, 0.6)))
    return reverb(pico(saturar(pico(x, 1.0), 1.8), 1.0), 0.3, 2.6)


def pitido():
    dur = 6.0
    n = n_(dur)
    t = t_(dur)
    f = 7200.0 * (1 + 0.004 * np.sin(2 * np.pi * 0.6 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / ms.SR) + 0.25 * np.sin(2 * np.pi * np.cumsum(f * 0.51) / ms.SR)
    env = np.clip(curva(n, [(0, 0), (0.01, 1), (0.6, 0.6), (1, 0)]), 0.0, None) ** 1.2
    sordo = pb(ruido(dur, 'marron'), 220, 2) * curva(n, [(0, 0.6), (1, 0)])
    return mezclar(pico(x * env, 1.0), pico(sordo, 0.35))


def main():
    ms.empezar('fogonazo')
    for k in range(2):
        ms.guardar('herido', herido(k), k + 1, alto=0.85)
    ms.guardar('muerte', muerte(), alto=0.85)
    ms.guardar('mecha', mecha(), alto=0.9)
    ms.guardar('estallido', estallido(), alto=0.95, limite=0.7)
    ms.guardar('pitido', pitido(), alto=0.5)
    ms.escribir_json()
    if len(sys.argv) > 2:
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
