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


def _veneno_sonido():
    burbujas = ms.burbujas(0.8, 30, 300, 1400)
    return reverb(mezclar(pico(siseo(0.8, 1800, 6000), 0.8), pico(burbujas, 0.6)), 0.25, 1.2)


def _rompe_bloques():
    golpe = boom(85, 34, 0.16)
    roca = chasquidos(0.45, 180, 400, 4200)
    polvo = pb(ruido(0.45, 'marron'), 1100) * caida(0.45, 0.12)
    return reverb(saturar(mezclar(pico(golpe, 1.0), pico(roca, 0.7), pico(polvo, 0.6)), 1.3), 0.25, 1.5)


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
    bs.guardar('veneno', _veneno_sonido(), alto=0.7)


def reptisaurio_arquero():
    reptisaurio('reptisaurio_arquero', 'Reptisaurio Arquero', 'Reptisaur Archer', 88,
                {'zarpazo': ('Zarpazo de un Reptisaurio Arquero', 'Reptisaur Archer slashes'),
                 'rugido': ('Ruge un Reptisaurio Arquero', 'Reptisaur Archer roars'),
                 'disparo': ('Dispara su arco un Reptisaurio Arquero', 'Reptisaur Archer shoots'),
                 'veneno': ('Te envenena un Reptisaurio Arquero', 'Reptisaur Archer poisons you')})
    cuerda = modos(210, 0.25, ((1, 1.0), (2.0, 0.5), (3.1, 0.25)), 0.05)
    aire = soplo(0.28, 3200, 1100)
    bs.guardar('disparo', reverb(mezclar(pico(cuerda, 0.9), en(0.03, pico(aire, 0.85))), 0.2, 1.1), alto=0.85)
    bs.guardar('veneno', _veneno_sonido(), alto=0.7)


def reptisaurio_lancero():
    reptisaurio('reptisaurio_lancero', 'Reptisaurio con Lanza', 'Reptisaur Lancer', 84,
                {'zarpazo': ('Zarpazo de un Reptisaurio con Lanza', 'Reptisaur Lancer slashes'),
                 'rugido': ('Ruge un Reptisaurio con Lanza', 'Reptisaur Lancer roars'),
                 'lanza': ('Estocada de un Reptisaurio con Lanza', 'Reptisaur Lancer thrusts'),
                 'veneno': ('Te envenena un Reptisaurio con Lanza', 'Reptisaur Lancer poisons you')})
    corte = mezclar(pico(soplo(0.3, 2800, 900), 0.9), en(0.14, pico(boom(125, 55, 0.07), 0.95)),
                    en(0.14, pico(modos(780, 0.16, ((1, 1.0), (2.4, 0.5)), 0.03), 0.6)))
    bs.guardar('lanza', reverb(corte, 0.2, 1.2), alto=0.88)
    bs.guardar('veneno', _veneno_sonido(), alto=0.7)


def raptor(ident, nombre_es, nombre_en, f0, rapido, extra_subs=None):
    subs = {
        'ambiente': (f'Chilla un {nombre_es}', f'{nombre_en} screeches'),
        'mordisco': (f'Muerde un {nombre_es}', f'{nombre_en} bites'),
        'llamada': (f'Llama a su manada un {nombre_es}', f'{nombre_en} calls its pack'),
    }
    if extra_subs:
        subs.update(extra_subs)
    comunes(ident, nombre_es, nombre_en, ('plaza', 6000), subs)
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


def dromoraptor_verde():
    raptor('dromoraptor_verde', 'Dromoraptor Verde', 'Green Dromoraptor', 300, True,
           {'veneno': ('Te envenena un Dromoraptor Verde', 'Green Dromoraptor poisons you')})
    bs.guardar('veneno', _veneno_sonido(), alto=0.7)


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


def narval():
    comunes('narval', 'Narval', 'Narwhal', ('abismo', 3800), {
        'ambiente': ('Canta un Narval', 'Narwhal calls'),
        'paso': ('Chapotea un Narval', 'Narwhal splashes'),
        'mordisco': ('Muerde un Narval', 'Narwhal bites'),
        'embiste': ('Embiste un Narval', 'Narwhal charges'),
    })
    for k in range(3):
        d = 1.4 + 0.3 * k
        canto = bramido(d, 110 + 12 * k, 72)
        burb = ms.burbujas(d * 0.7, 22, 220, 950)
        bs.guardar('ambiente', reverb(mezclar(pico(canto, 0.85), en(0.2, pico(burb, 0.45))), 0.4, 2.4), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(grunido(0.45, 165 + 20 * k, 110, 'u', 0.8, 0.7), 1.0),
                    pico(ms.burbujas(0.4, 28, 280, 1200), 0.4))
        bs.guardar('herido', reverb(x, 0.3, 1.5), k + 1, alto=0.75)
    x = mezclar(pico(bramido(1.8, 120, 48), 1.0), en(0.4, pico(ms.burbujas(1.2, 30, 180, 900), 0.55)))
    bs.guardar('muerte', reverb(x, 0.45, 2.6), alto=0.82)
    ola = mezclar(pico(soplo(0.25, 900, 320), 0.7), pico(ms.burbujas(0.25, 26, 260, 1100), 0.6))
    bs.guardar('paso', ola, alto=0.4)
    bs.guardar('mordisco', reverb(mezclar(pico(mordisco(0.85), 1.0), pico(ola, 0.5)), 0.25, 1.4), alto=0.85)
    emb = mezclar(pico(soplo(0.55, 1400, 360), 0.85), pico(ms.burbujas(0.55, 40, 240, 1300), 0.7),
                  en(0.18, pico(boom(95, 42, 0.14), 0.95)))
    bs.guardar('embiste', reverb(saturar(emb, 1.25), 0.3, 1.8), alto=0.9)


def fluviosaurus():
    comunes('fluviosaurus', 'Fluviosaurus', 'Fluviosaurus', ('plaza', 5400), {
        'ambiente': ('Gorgotea un Fluviosaurus', 'Fluviosaurus gurgles'),
        'mordisco': ('Muerde un Fluviosaurus', 'Fluviosaurus bites'),
        'rompe': ('Destroza bloques un Fluviosaurus', 'Fluviosaurus smashes blocks'),
    })
    for k in range(3):
        d = 0.8 + 0.2 * k
        x = mezclar(pico(grunido(d, 190 + 18 * k, 140, 'e', 1.0, 0.7), 0.85),
                    pico(ms.burbujas(d, 26, 350, 1500), 0.55))
        bs.guardar('ambiente', reverb(x, 0.3, 1.6), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(chillido_raptor(0.32, 260 + 25 * k, 'e'), 0.95),
                    pico(ms.burbujas(0.3, 30, 400, 1600), 0.45))
        bs.guardar('herido', x, k + 1, alto=0.75)
    x = mezclar(pico(grunido(1.1, 210, 85, 'o', 0.9, 0.8), 1.0), en(0.3, pico(ms.burbujas(0.8, 25, 250, 1100), 0.5)))
    bs.guardar('muerte', reverb(x, 0.35, 1.8), alto=0.8)
    bs.guardar('paso', mezclar(pico(paso(0.55, 115, 0.7), 0.8), pico(ms.burbujas(0.14, 18, 400, 1400), 0.35)), alto=0.35)
    bs.guardar('mordisco', mezclar(pico(mordisco(1.15), 1.0), pico(grunido(0.22, 220, 150, 'e'), 0.5)), alto=0.85)
    bs.guardar('rompe', _rompe_bloques(), alto=0.9)


def zarinosa():
    comunes('zarinosa', 'Zarinosa Espigüeya', 'Spiketail Zarinosa', ('plaza', 5800), {
        'ambiente': ('Sisea una Zarinosa Espigüeya', 'Spiketail Zarinosa hisses'),
        'mordisco': ('Muerde una Zarinosa Espigüeya', 'Spiketail Zarinosa bites'),
        'salta': ('Salta una Zarinosa Espigüeya', 'Spiketail Zarinosa leaps'),
    })
    for k in range(3):
        d = 0.75 + 0.2 * k
        x = mezclar(pico(siseo(d, 2200, 7500), 0.85), pico(castaneteo(d * 0.7, 34 + 6 * k), 0.55),
                    pico(grunido(d * 0.6, 210, 165, 'e', 1.1, 0.9), 0.45))
        bs.guardar('ambiente', reverb(x, 0.25, 1.5), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(chillido_raptor(0.28, 360 + 30 * k, 'e'), 1.0), pico(siseo(0.25, 2800, 8000), 0.45))
        bs.guardar('herido', x, k + 1, alto=0.75)
    x = mezclar(pico(chillido_raptor(0.85, 340, 'a'), 0.95), en(0.35, pico(siseo(0.65, 2000, 6500), 0.5)))
    bs.guardar('muerte', reverb(x, 0.3, 1.8), alto=0.8)
    bs.guardar('paso', paso(0.5, 130, 0.9), alto=0.35)
    bs.guardar('mordisco', mezclar(pico(mordisco(1.3), 1.0), pico(siseo(0.2, 2600, 7500), 0.5)), alto=0.85)
    salto = mezclar(pico(chillido_raptor(0.38, 410, 'e'), 0.95), pico(soplo(0.35, 2600, 900), 0.75),
                    en(0.12, pico(castaneteo(0.25, 45), 0.5)))
    bs.guardar('salta', reverb(salto, 0.25, 1.4), alto=0.9)


def kragtops():
    comunes('kragtops', 'Kragtops', 'Kragtops', ('cumbre', 3400), {
        'ambiente': ('Resopla un Kragtops', 'Kragtops snorts'),
        'paso': ('Pisada pesada de un Kragtops', 'Heavy Kragtops footsteps'),
        'embiste': ('Embiste un Kragtops', 'Kragtops charges'),
        'maza': ('Golpe de maza de un Kragtops', 'Kragtops slams its tail club'),
    })
    for k in range(3):
        d = 1.4 + 0.3 * k
        x = mezclar(pico(bramido(d, 74 + 6 * k, 54), 0.9), en(d * 0.5, pico(soplo(0.45, 1100, 350), 0.45)))
        bs.guardar('ambiente', reverb(x, 0.35, 2.2), k + 1, alto=0.6)
    for k in range(2):
        x = mezclar(pico(bramido(0.55, 105 + 10 * k, 75), 1.0), pico(castaneteo(0.25, 30), 0.4))
        bs.guardar('herido', reverb(x, 0.25, 1.6), k + 1, alto=0.75)
    x = mezclar(pico(bramido(2.0, 88, 38), 1.0), en(1.2, pico(boom(62, 26, 0.35), 0.8)))
    bs.guardar('muerte', reverb(x, 0.4, 2.6), alto=0.85)
    bs.guardar('paso', mezclar(pico(boom(62, 30, 0.1), 1.0), pico(pb(ruido(0.22, 'marron'), 500) * caida(0.22, 0.06), 0.45)),
               alto=0.45)
    emb = mezclar(pico(bramido(0.65, 96, 68), 0.85), en(0.22, pico(boom(75, 30, 0.22), 1.0)),
                  en(0.22, pico(chasquidos(0.2, 160, 500, 3500), 0.55)))
    bs.guardar('embiste', reverb(saturar(emb, 1.35), 0.3, 1.8), alto=0.92)
    maza = mezclar(pico(soplo(0.42, 1200, 320), 0.8), en(0.24, pico(boom(64, 24, 0.28), 1.0)),
                   en(0.24, pico(modos(420, 0.22, ((1, 1.0), (2.2, 0.6), (3.5, 0.3)), 0.04), 0.65)))
    bs.guardar('maza', reverb(saturar(maza, 1.4), 0.35, 2.0), alto=0.95, limite=0.78)


def dactylo_adulto():
    comunes('dactylo_adulto', 'Dáctylo Adulto', 'Adult Dactylo', ('cumbre', 5600), {
        'ambiente': ('Chilla un Dáctylo Adulto', 'Adult Dactylo screeches'),
        'paso': ('Aletea un Dáctylo Adulto', 'Adult Dactylo flaps'),
        'picotazo': ('Picotazo de un Dáctylo Adulto', 'Adult Dactylo pecks'),
        'agarra': ('Te agarra un Dáctylo Adulto', 'Adult Dactylo grabs you'),
    })
    for k in range(3):
        d = 0.7 + 0.15 * k
        x = mezclar(pico(chillido_raptor(d, 460 + 35 * k, 'a'), 0.95), en(0.2, pico(soplo(0.35, 1800, 600), 0.35)))
        bs.guardar('ambiente', reverb(x, 0.4, 2.4), k + 1, alto=0.6)
    for k in range(2):
        bs.guardar('herido', reverb(pico(chillido_raptor(0.32, 560 + 40 * k, 'e'), 1.0), 0.25, 1.5), k + 1, alto=0.75)
    x = mezclar(pico(chillido_raptor(1.1, 520, 'a'), 1.0), en(0.5, pico(soplo(0.6, 1400, 400), 0.5)))
    bs.guardar('muerte', reverb(x, 0.4, 2.4), alto=0.8)
    aleteo = mezclar(pico(soplo(0.28, 950, 280), 0.85), pico(boom(90, 45, 0.06), 0.4))
    bs.guardar('paso', aleteo, alto=0.4)
    bs.guardar('picotazo', mezclar(pico(mordisco(1.25), 1.0), pico(chillido_raptor(0.22, 500, 'e'), 0.55)), alto=0.85)
    agarra = mezclar(pico(soplo(0.45, 2200, 650), 0.9), en(0.15, pico(chillido_raptor(0.4, 540, 'a'), 0.85)),
                     en(0.18, pico(mordisco(1.1), 0.75)))
    bs.guardar('agarra', reverb(agarra, 0.3, 1.8), alto=0.9)


def chelonia():
    comunes('chelonia', 'Chelonia', 'Chelonia', ('abismo', 4600), {
        'ambiente': ('Resuena una Chelonia', 'Chelonia resonates'),
        'mordisco': ('Muerde una Chelonia', 'Chelonia bites'),
        'cristal': ('Dispara cristales una Chelonia', 'Chelonia shoots crystals'),
        'esconde': ('Se esconde en su caparazón una Chelonia', 'Chelonia hides in its shell'),
    })
    for k in range(3):
        d = 1.1 + 0.25 * k
        voz = grunido(d, 105 + 8 * k, 78, 'o', 0.75, 0.6)
        cris = modos(1320 + 140 * k, 0.45, ((1, 1.0), (1.5, 0.6), (2.4, 0.35)), 0.08)
        bs.guardar('ambiente', reverb(mezclar(pico(voz, 0.85), en(0.25, pico(cris, 0.4))), 0.35, 2.0), k + 1, alto=0.6)
    for k in range(2):
        cris = modos(1600 + 180 * k, 0.25, ((1, 1.0), (1.8, 0.5)), 0.05)
        x = mezclar(pico(grunido(0.38, 150 + 15 * k, 110, 'a', 0.85, 0.8), 0.9), pico(cris, 0.55))
        bs.guardar('herido', reverb(x, 0.25, 1.4), k + 1, alto=0.75)
    x = mezclar(pico(grunido(1.5, 130, 52, 'u', 0.75, 0.7), 1.0),
                en(0.3, pico(chasquidos(0.7, 90, 1200, 6500), 0.55)))
    bs.guardar('muerte', reverb(x, 0.35, 2.2), alto=0.8)
    bs.guardar('paso', paso(0.85, 85, 0.5), alto=0.4)
    bs.guardar('mordisco', pico(mordisco(0.95), 1.0), alto=0.85)
    disp = mezclar(pico(modos(1480, 0.35, ((1, 1.0), (1.6, 0.7), (2.3, 0.45)), 0.06), 0.95),
                   pico(soplo(0.28, 3400, 1200), 0.7), pico(chasquidos(0.18, 140, 2000, 8500), 0.55))
    bs.guardar('cristal', reverb(disp, 0.3, 1.6), alto=0.88)
    esc = mezclar(pico(boom(95, 42, 0.12), 0.9), pico(castaneteo(0.35, 36), 0.65),
                  en(0.1, pico(modos(1100, 0.25, ((1, 1.0), (1.9, 0.5)), 0.04), 0.45)))
    bs.guardar('esconde', reverb(esc, 0.25, 1.4), alto=0.85)


def _coloso_bipedo(ident, nombre_es, nombre_en, f0, extra_subs=None):
    subs = {
        'ambiente': (f'Ruge un {nombre_es}', f'{nombre_en} growls'),
        'paso': (f'Retumban las pisadas de un {nombre_es}', f'{nombre_en} stomps'),
        'mordisco': (f'Fauces de un {nombre_es}', f'{nombre_en} snaps its jaws'),
        'rugido': (f'Brama un {nombre_es}', f'{nombre_en} roars'),
        'rompe': (f'Arrasa bloques un {nombre_es}', f'{nombre_en} smashes blocks'),
    }
    if extra_subs:
        subs.update(extra_subs)
    comunes(ident, nombre_es, nombre_en, ('cumbre', 3600), subs)
    for k in range(3):
        d = 1.4 + 0.3 * k
        x = mezclar(pico(grunido(d, f0 * (1.05 + 0.06 * k), f0 * 0.72, 'o', 0.7, 0.85), 0.9),
                    en(d * 0.55, pico(siseo(0.65, 1600, 5200), 0.35)))
        bs.guardar('ambiente', reverb(x, 0.38, 2.4), k + 1, alto=0.65)
    for k in range(2):
        x = mezclar(pico(grunido(0.55, f0 * (1.55 + 0.15 * k), f0 * 1.05, 'a', 0.75, 0.95), 1.0),
                    pico(boom(70, 35, 0.08), 0.4))
        bs.guardar('herido', reverb(x, 0.28, 1.7), k + 1, alto=0.78)
    x = mezclar(pico(bramido(2.2, f0 * 1.2, f0 * 0.45), 1.0), en(1.3, pico(boom(58, 24, 0.38), 0.85)))
    bs.guardar('muerte', reverb(x, 0.45, 2.8), alto=0.88)
    bs.guardar('paso', mezclar(pico(boom(60, 28, 0.11), 1.0),
                               pico(pb(ruido(0.25, 'marron'), 450) * caida(0.25, 0.07), 0.45)), alto=0.5)
    mord = mezclar(pico(mordisco(0.75), 1.0), pico(boom(95, 42, 0.09), 0.8),
                   en(0.05, pico(grunido(0.35, f0 * 1.35, f0 * 0.9, 'a', 0.75, 0.9), 0.6)))
    bs.guardar('mordisco', reverb(saturar(mord, 1.3), 0.25, 1.5), alto=0.9)
    rug = mezclar(pico(bramido(1.7, f0 * 1.5, f0 * 0.75), 1.0),
                  pico(grunido(1.6, f0 * 1.8, f0 * 0.9, 'a', 0.75, 1.0), 0.85),
                  en(0.2, pico(boom(65, 26, 0.28), 0.75)),
                  en(1.0, pico(siseo(0.7, 1500, 5500), 0.45)))
    bs.guardar('rugido', reverb(saturar(rug, 1.45), 0.4, 2.6), alto=0.95, limite=0.78)
    bs.guardar('rompe', _rompe_bloques(), alto=0.9)


def tyrannok():
    _coloso_bipedo('tyrannok', 'Tyrannok', 'Tyrannok', 68)


def mastodino():
    _coloso_bipedo('mastodino', 'Mastodino', 'Mastodino', 62)


def espinosaurio():
    _coloso_bipedo('espinosaurio', 'Espinosaurio', 'Spinosaurus', 74,
                   {'veneno': ('Te envenena un Espinosaurio', 'Spinosaurus poisons you')})
    bs.guardar('veneno', _veneno_sonido(), alto=0.75)


MOBS = {
    'reptisaurio_salvaje': reptisaurio_salvaje,
    'reptisaurio_guerrero': reptisaurio_guerrero,
    'reptisaurio_arquero': reptisaurio_arquero,
    'reptisaurio_lancero': reptisaurio_lancero,
    'dromoraptor_rojo': dromoraptor_rojo,
    'dromoraptor_azul': dromoraptor_azul,
    'dromoraptor_verde': dromoraptor_verde,
    'plumosaurio': plumosaurio,
    'molusco_rocoso': molusco_rocoso,
    'narval': narval,
    'fluviosaurus': fluviosaurus,
    'zarinosa': zarinosa,
    'kragtops': kragtops,
    'dactylo_adulto': dactylo_adulto,
    'chelonia': chelonia,
    'tyrannok': tyrannok,
    'mastodino': mastodino,
    'espinosaurio': espinosaurio,
}


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
