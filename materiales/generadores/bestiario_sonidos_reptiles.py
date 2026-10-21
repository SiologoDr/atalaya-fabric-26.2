"""
Los sonidos de los reptiles del bestiario (bestia.<id>.<nombre>), todos nuestros:

  reptisaurio_salvaje   un gruñido ronco de garganta con un siseo detrás; los pasos, pesados y con el roce de las
                        garras; el zarpazo, el aire que corta y el golpe
  reptisaurio_guerrero  el mismo gruñido, más grave y con un chasquido de huesos; su golpe lleva el siseo del veneno
  dromoraptor_rojo      el chillido seco del raptor (ladridos cortos, con la garganta), los pasos ligeros de garras, el
                        mordisco y la llamada de la manada; el Rojo, más grave y bronco
  dromoraptor_azul      lo mismo, más agudo y más rápido
  plumosaurio           el bramido del coloso, muy grave y con mucha sala; las pisadas, que retumban; su golpe, un
                        trallazo enorme
  molusco_rocoso        un castañeteo seco (como piedras que chocan); al enterrarse, la tierra que escarba; al salir, la
                        tierra que revienta y el mordisco

Todos: ambiente (×3), herido (×2), muerte y paso.

Uso: python bestiario_sonidos_reptiles.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, caida, chasquidos, curva, en, filtro_mov, formantes, garganta, mezclar, modos,
                               n_, pb, pico, reverb, ruido, saturar, soplo, t_, ventana)


def grunido(dur, f0, f1, vocal='o', escala=0.8, aspero=0.8):
    """Un gruñido de reptil: una garganta grave y ronca que baja de f0 a f1, con temblor."""
    n = n_(dur)
    f = curva(n, [(0, f0), (0.3, f0 * 1.05), (1, f1)]) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t_(dur)))
    v = garganta(f, dur, formantes(vocal, escala), aspereza=aspero, sub=0.4, jitter=0.07, aliento=0.3, caos=0.5)
    return v * ventana(dur, 0.04, dur * 0.4)


def siseo(dur, lo=2500, hi=8000):
    """El siseo de un reptil: aire entre los dientes."""
    return bp(ruido(dur, 'rosa'), lo, hi) * ventana(dur, dur * 0.2, dur * 0.5)


def paso(fuerza=1.0, grave=80.0, garras=0.5):
    """Una pisada: el golpe sordo en la tierra, el crujido y el roce de las garras."""
    golpe = boom(grave, grave * 0.5, 0.06) * fuerza
    tierra = pb(ruido(0.12, 'rosa'), 1400) * caida(0.12, 0.03)
    roce = chasquidos(0.15, 60, 2500, 9000) * garras
    return mezclar(pico(golpe, 0.8 * fuerza), pico(tierra, 0.5), pico(roce, 0.4 * garras))


def zarpazo():
    """El aire que corta y el golpe."""
    return mezclar(pico(soplo(0.35, 2400, 800), 0.8), en(0.22, pico(boom(110, 50, 0.07), 0.9)),
                   en(0.22, pico(chasquidos(0.1, 220, 1500, 8000), 0.5)))


def mordisco(grave=1.0):
    """Las mandíbulas que se cierran de golpe: un chasquido seco de hueso."""
    snap = modos(900 * grave, 0.2, ((1, 1.0), (2.3, 0.6), (4.1, 0.3)), 0.03)
    return mezclar(pico(snap, 1.0), pico(chasquidos(0.08, 400, 2000, 9000), 0.6),
                   pico(boom(140 * grave, 70 * grave, 0.04), 0.5))


def chillido_raptor(dur, f0, vocal='e'):
    """El ladrido seco del raptor: una garganta aguda que sube y cae, áspera."""
    n = n_(dur)
    f = curva(n, [(0, f0 * 0.85), (0.3, f0 * 1.15), (1, f0 * 0.7)])
    v = garganta(f, dur, formantes(vocal, 1.1), aspereza=0.9, sub=0.15, jitter=0.08, aliento=0.4, caos=0.6)
    return v * ventana(dur, 0.01, dur * 0.5)


def ladridos(f0, cuantos, hueco, vocal='e'):
    """Unos ladridos cortos seguidos (la llamada de la manada)."""
    return mezclar(*[en(k * hueco, pico(chillido_raptor(0.16 + 0.03 * (k % 2), f0 * (1 + 0.06 * k)), 0.9 - 0.1 * k))
                     for k in range(cuantos)])


def bramido(dur, f0, f1):
    """El bramido del coloso: una garganta muy grave, larga, con mucha sala."""
    n = n_(dur)
    f = curva(n, [(0, f0 * 0.9), (0.25, f0 * 1.1), (0.7, f0), (1, f1)])
    v = garganta(f, dur, formantes('u', 0.62), aspereza=0.5, sub=0.6, jitter=0.03, aliento=0.2, caos=0.2)
    return v * ventana(dur, dur * 0.15, dur * 0.4)


def castaneteo(dur, tasa=28.0):
    """El castañeteo del Cavador: golpecitos secos, como piedras que chocan."""
    n = n_(dur)
    golpes = chasquidos(dur, curva(n, [(0, tasa * 0.6), (0.5, tasa * 1.2), (1, tasa * 0.4)]), 700, 4000)
    return golpes * ventana(dur, 0.02, dur * 0.3)


def escarba(dur):
    """La tierra que escarba: golpes de tierra suelta, uno detrás de otro."""
    n = n_(dur)
    granos = chasquidos(dur, 120, 300, 3000)
    tierra = pb(ruido(dur, 'marron'), 900) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 6 * t_(dur))))
    return mezclar(pico(tierra, 0.8), pico(granos, 0.6)) * curva(n, [(0, 0.2), (0.2, 1.0), (0.8, 1.0), (1, 0)])


def revienta_tierra():
    """La tierra que revienta al salir: el golpe sordo y la lluvia de tierra."""
    golpe = boom(70, 32, 0.12)
    lluvia = pb(ruido(0.9, 'rosa'), 2000) * caida(0.9, 0.25)
    piedras = chasquidos(0.9, curva(n_(0.9), [(0, 160), (1, 10)]), 500, 5000)
    return mezclar(pico(golpe, 1.0), pico(lluvia, 0.6), pico(piedras, 0.5))


def comunes(ident, nombre_es, nombre_en, sala, extra):
    bs.empezar(ident, sala)
    subs = {
        'ambiente': (f'Gruñe un {nombre_es}', f'{nombre_en} growls'),
        'herido': (f'Se queja un {nombre_es}', f'{nombre_en} hurts'),
        'muerte': (f'Muere un {nombre_es}', f'{nombre_en} dies'),
        'paso': ('Pasos con garras', 'Clawed footsteps'),
    }
    subs.update(extra)
    bs.subtitulos(ident, subs)


def reptisaurio(ident, nombre_es, nombre_en, f0, extra):
    comunes(ident, nombre_es, nombre_en, ('plaza', 4800), extra)
    for k in range(3):
        d = 1.0 + 0.3 * k
        x = mezclar(pico(grunido(d, f0 * (1.05 + 0.08 * k), f0 * 0.8), 0.9), en(d * 0.55, pico(siseo(0.6), 0.35)))
        bs.guardar('ambiente', reverb(x, 0.3, 1.8), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(grunido(0.4, f0 * (1.7 + 0.2 * k), f0 * 1.2, 'a', 0.9, 1.0), 1.0), pico(siseo(0.3), 0.3))
        bs.guardar('herido', x, k + 1, alto=0.75)
    x = mezclar(pico(grunido(1.5, f0 * 1.3, f0 * 0.5, 'o', 0.8, 0.9), 1.0), en(0.9, pico(siseo(0.8, 1500, 5000), 0.4)))
    bs.guardar('muerte', reverb(x, 0.35, 2.0), alto=0.8)
    bs.guardar('paso', paso(1.0, 75, 0.6), alto=0.4)
    bs.guardar('zarpazo', reverb(mezclar(pico(zarpazo(), 1.0), en(0.15, pico(grunido(0.35, f0 * 1.5, f0, 'a'), 0.5))),
                                 0.2, 1.2), alto=0.85)
    # El rugido al verte: un gruñido largo y abierto que sube y cae, con el siseo detrás.
    x = mezclar(pico(grunido(1.5, f0 * 1.7, f0 * 0.9, 'a', 0.9, 1.0), 1.0), en(1.0, pico(siseo(0.7, 1800, 6000), 0.45)))
    bs.guardar('rugido', reverb(saturar(pico(x), 1.3), 0.35, 2.2), alto=0.9)


def reptisaurio_salvaje():
    reptisaurio('reptisaurio_salvaje', 'Reptisaurio Salvaje', 'Wild Reptisaur', 95,
                {'zarpazo': ('Zarpazo de un Reptisaurio Salvaje', 'Wild Reptisaur slashes'),
                 'rugido': ('Ruge un Reptisaurio Salvaje', 'Wild Reptisaur roars')})


def reptisaurio_guerrero():
    reptisaurio('reptisaurio_guerrero', 'Reptisaurio Guerrero', 'Reptisaur Warrior', 80,
                {'zarpazo': ('Zarpazo de un Reptisaurio Guerrero', 'Reptisaur Warrior slashes'),
                 'rugido': ('Ruge un Reptisaurio Guerrero', 'Reptisaur Warrior roars'),
                 'veneno': ('Te envenena un Reptisaurio Guerrero', 'Reptisaur Warrior poisons you')})
    burbujas = ms.burbujas(0.8, 30, 300, 1400)
    bs.guardar('veneno', reverb(mezclar(pico(siseo(0.8, 1800, 6000), 0.8), pico(burbujas, 0.6)), 0.25, 1.2),
               alto=0.7)


def raptor(ident, nombre_es, nombre_en, f0, rapido):
    comunes(ident, nombre_es, nombre_en, ('plaza', 6000), {
        'ambiente': (f'Chilla un {nombre_es}', f'{nombre_en} screeches'),
        'mordisco': (f'Muerde un {nombre_es}', f'{nombre_en} bites'),
        'llamada': (f'Llama a su manada un {nombre_es}', f'{nombre_en} calls its pack'),
    })
    hueco = 0.2 if rapido else 0.26
    for k in range(3):
        x = mezclar(pico(ladridos(f0 * (1 + 0.05 * k), 2 + k % 2, hueco), 0.9), pico(siseo(0.5), 0.2))
        bs.guardar('ambiente', reverb(x, 0.3, 1.8), k + 1, alto=0.6)
    for k in range(2):
        bs.guardar('herido', pico(chillido_raptor(0.3, f0 * (1.5 + 0.2 * k), 'a'), 1.0), k + 1, alto=0.75)
    x = mezclar(pico(chillido_raptor(0.9, f0 * 1.3, 'a'), 1.0), en(0.5, pico(grunido(0.8, f0 * 0.5, f0 * 0.3), 0.6)))
    bs.guardar('muerte', reverb(x, 0.35, 2.0), alto=0.8)
    bs.guardar('paso', paso(0.6, 110, 1.0), alto=0.35)
    bs.guardar('mordisco', mezclar(pico(mordisco(1.2 if rapido else 1.0), 1.0),
                                   pico(chillido_raptor(0.18, f0 * 1.2), 0.5)), alto=0.85)
    bs.guardar('llamada', reverb(ladridos(f0 * 1.1, 4, hueco * 0.8, 'a'), 0.4, 2.2), alto=0.8)


def dromoraptor_rojo():
    raptor('dromoraptor_rojo', 'Dromoraptor Rojo', 'Red Dromoraptor', 260, False)


def dromoraptor_azul():
    raptor('dromoraptor_azul', 'Dromoraptor Azul', 'Blue Dromoraptor', 340, True)


def plumosaurio():
    comunes('plumosaurio', 'Plumosaurio', 'Plumosaur', ('cumbre', 3200), {
        'ambiente': ('Brama un Plumosaurio', 'Plumosaur bellows'),
        'paso': ('Retumban unas pisadas', 'Heavy footsteps rumble'),
        'golpe': ('Golpe brutal de un Plumosaurio', 'Plumosaur strikes hard'),
    })
    for k in range(3):
        d = 1.8 + 0.4 * k
        bs.guardar('ambiente', reverb(bramido(d, 62 + 6 * k, 48), 0.45, 2.8), k + 1, alto=0.6)
    for k in range(2):
        bs.guardar('herido', reverb(bramido(0.7, 95 + 10 * k, 70), 0.3, 1.8), k + 1, alto=0.75)
    x = mezclar(pico(bramido(2.6, 80, 34), 1.0), en(1.8, pico(boom(60, 25, 0.4), 0.7)))
    bs.guardar('muerte', reverb(x, 0.45, 3.0), alto=0.85)
    bs.guardar('paso', mezclar(pico(boom(55, 28, 0.12), 1.0), pico(pb(ruido(0.3, 'marron'), 400) * caida(0.3, 0.08), 0.4)),
               alto=0.5)
    x = mezclar(pico(soplo(0.5, 1500, 400), 0.7), en(0.3, pico(boom(70, 26, 0.25), 1.0)),
                en(0.3, pico(chasquidos(0.2, 200, 600, 4000), 0.5)))
    bs.guardar('golpe', reverb(saturar(pico(x), 1.4), 0.3, 2.0), alto=0.95, limite=0.75)


def molusco_rocoso():
    comunes('molusco_rocoso', 'Molusco Rocoso', 'Rocky Mollusk', ('plaza', 5200), {
        'ambiente': ('Castañetea un Molusco Rocoso', 'Rocky Mollusk clatters'),
        'mordisco': ('Muerde un Molusco Rocoso', 'Rocky Mollusk bites'),
        'entierra': ('Se entierra un Molusco Rocoso', 'Rocky Mollusk digs in'),
        'sale': ('Sale de la tierra un Molusco Rocoso', 'Rocky Mollusk bursts out'),
    })
    for k in range(3):
        x = mezclar(pico(castaneteo(0.7 + 0.2 * k, 24 + 6 * k), 0.9), pico(grunido(0.5, 160, 130, 'e', 1.2), 0.3))
        bs.guardar('ambiente', reverb(x, 0.2, 1.2), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(grunido(0.3, 240 + 30 * k, 180, 'a', 1.2, 1.0), 1.0), pico(castaneteo(0.3, 50), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.75)
    x = mezclar(pico(grunido(1.0, 220, 90, 'o', 1.1, 0.9), 1.0), en(0.4, pico(castaneteo(0.8, 40), 0.5)))
    bs.guardar('muerte', reverb(x, 0.3, 1.6), alto=0.8)
    bs.guardar('paso', paso(0.5, 120, 0.8), alto=0.35)
    bs.guardar('mordisco', pico(mordisco(1.4), 1.0), alto=0.85)
    bs.guardar('entierra', reverb(escarba(1.2), 0.2, 1.2), alto=0.8)
    bs.guardar('sale', reverb(mezclar(pico(revienta_tierra(), 1.0), en(0.1, pico(mordisco(1.4), 0.6))), 0.25, 1.6),
               alto=0.95, limite=0.8)


MOBS = {'reptisaurio_salvaje': reptisaurio_salvaje, 'reptisaurio_guerrero': reptisaurio_guerrero,
        'dromoraptor_rojo': dromoraptor_rojo, 'dromoraptor_azul': dromoraptor_azul, 'plumosaurio': plumosaurio,
        'molusco_rocoso': molusco_rocoso}


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
