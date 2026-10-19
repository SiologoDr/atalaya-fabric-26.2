"""
Los sonidos de los fantasmas del bestiario (bestia.<id>.<nombre>), hechos con voces sin cuerdas (aire por formantes),
lamentos que resbalan de tono, tela que ondea, cadenas, campanas lejanas y mucha sala (el Limbo suena hondo):

  espectro_rojo      un siseo rabioso y ronco; el zarpazo (aire cortado y uñas); agarra (un tirón de tela)
  espectro_blanco    un lamento triste, casi una nana; el zarpazo, rápido y fino
  espectro_negro     susurros graves con un latido debajo; roba (un golpe sordo y algo que se sorbe)
  espectro_amarillo  una risita que rebota; se mete (un remolino que sube) y sale (un reventón con risa)
  parca_menor        un resuello áspero; la hoz (un silbido corto); destierra (una campana grave y un soplo al revés)
  parca              la respiración honda y el hueso que castañetea; la guadaña (un tajo largo); el alma (coro y campana)
  murcielago_vampiro chillidos agudos y aleteos; el mordisco y el sorbo
  farolero           el farol que cruje y una llama que zumba; la mecha (la llama que se hincha y silba), el
                     reventón (cristal y fuego frío) y el puzzle (un clic de mecanismo y una nota)
  recluso_*          sollozos y cadenas; el grillete (un cierre de hierro)
  coloso_*           un gemido muy grave y cadenas pesadas; el golpe (un mazazo); sus pasos
  ojo_errante        un zumbido bajo y algo húmedo; la mirada (el zumbido que crece), lo que le quema la Linterna
  palido             casi nada (estática muy floja); aparece y se va (un chasquido de estática); el grito
  vindicador_limbo   un gruñido de saqueador con eco; el hachazo; el escudo que se rompe

Uso: python bestiario_sonidos_fantasmas.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (armonica_cristal, boom, bp, burbujas, caida, chasquidos, coro_voces, cuenco, curva, en,
                               filtro_mov, formantes, garganta, mezclar, modos, n_, pa, pb, pico, reverb, ruido,
                               saturar, seno, soplo, susurro, t_, ventana)

rng = np.random.default_rng(20261025)


# ======================================================================================================================
#  Lo de todos
# ======================================================================================================================
def lamento(dur, f0, f1, vocal='u', aliento=0.7, voces=2, aspero=0.2):
    """Un lamento de fantasma: voces casi sin cuerdas (mucho aliento) que resbalan de tono, un poco desafinadas entre
    sí."""
    n = n_(dur)
    capas = []
    for k in range(voces):
        d = 1 + 0.012 * (k - (voces - 1) / 2)
        f = curva(n, [(0, f0 * d), (0.5, (f0 + f1) / 2 * d * 1.04), (1, f1 * d)])
        v = garganta(f, dur, formantes(vocal, 1.1), aspereza=aspero, sub=0.0, jitter=0.02, aliento=aliento, fmax=4000)
        capas.append(pico(v, 1.0))
    return mezclar(*capas) * ventana(dur, dur * 0.25, dur * 0.4)


def tela_ondea(dur, fuerza=1.0):
    """Tela que ondea: soplos cortos y un roce."""
    n = n_(dur)
    x = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 600), (0.5, 1400), (1, 700)]), 'band', 1.2)
    return pico(x * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t_(dur)) ** 2), fuerza) * ventana(dur, 0.05, dur * 0.4)


def zarpazo(fuerza=1.0, agudo=1.0):
    corte = soplo(0.22, 900 * agudo, 3600 * agudo, 1.3, 0.4)
    unas = chasquidos(0.12, 160, 3000, 10000)
    return mezclar(pico(corte, fuerza), en(0.08, pico(unas, 0.5 * fuerza)))


def cadenas(dur, tasa=18.0, f=1800.0, peso=1.0):
    """Cadenas: eslabones que chocan (metal inarmónico, corto) a ráfagas."""
    n = n_(dur)
    out = np.zeros(n + n_(0.3))
    t = 0.0
    while t < dur:
        ff = f * rng.uniform(0.8, 1.25) / peso
        g = modos(ff, 0.25, ((1, 1.0), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)), 0.05 * peso, 0.002) * rng.uniform(0.3, 1.0)
        i = int(t * ms.SR)
        out[i:i + len(g)] += g
        t += rng.exponential(1.0 / tasa)
    return out[:n]


def campana(f, dur=3.0):
    return cuenco(f, dur, 1.0, 0.0, 0.004)


def estatica(dur, fuerza=1.0):
    n = n_(dur)
    x = bp(ruido(dur), 1500, 9000) * (rng.random(n) < 0.7)
    return pico(x, fuerza) * ventana(dur, 0.005, 0.02)


def risa(dur, f0=420.0):
    """Una risita: sílabas cortas «ji» que suben y bajan."""
    capas = []
    t = 0.0
    k = 0
    while t < dur - 0.1:
        d = rng.uniform(0.07, 0.11)
        f = f0 * (1.0 + 0.15 * np.sin(k * 1.3))
        v = garganta(curva(n_(d), [(0, f * 1.1), (1, f * 0.9)]), d, formantes('e', 1.5), aspereza=0.3, sub=0.0,
                     jitter=0.03, aliento=0.5) * ventana(d, 0.005, d * 0.5)
        capas.append(en(t, pico(v, 1.0)))
        t += d + rng.uniform(0.03, 0.06)
        k += 1
    return mezclar(*capas)


def herido_fantasma(f0, vocal='a'):
    v = garganta(curva(n_(0.4), [(0, f0), (0.3, f0 * 1.5), (1, f0 * 0.8)]), 0.4, formantes(vocal, 1.2), aspereza=0.6,
                 sub=0.1, jitter=0.05, aliento=0.6, caos=0.3) * ventana(0.4, 0.01, 0.2)
    return mezclar(pico(v, 0.9), pico(tela_ondea(0.3), 0.4))


def muerte_fantasma(f0, f1, vocal='u', dur=1.8):
    x = mezclar(pico(lamento(dur, f0, f1, vocal, 0.8, 3), 0.9), en(0.2, pico(soplo(dur * 0.8, 2000, 300, 1.0, 0.2), 0.5)))
    return x * curva(n_(len(x) / ms.SR), [(0, 1.0), (1, 0.2)])


def espectro_base(ident, nombre_es, nombre_en, f_amb, vocal, extra_subs, sala=('abismo', 4200)):
    bs.empezar(ident, sala)
    subs = {
        'ambiente': (f'Gime un {nombre_es}', f'{nombre_en} moans'),
        'herido': (f'Chilla un {nombre_es}', f'{nombre_en} shrieks'),
        'muerte': (f'Se deshace un {nombre_es}', f'{nombre_en} fades away'),
        'paso': ('Ondea una tela', 'Cloth flutters'),
    }
    subs.update(extra_subs)
    bs.subtitulos(ident, subs)
    bs.guardar('herido', reverb(herido_fantasma(f_amb * 2.2, 'a'), 0.3, 1.6), 1, alto=0.7)
    bs.guardar('herido', reverb(herido_fantasma(f_amb * 2.5, 'e'), 0.3, 1.6), 2, alto=0.7)
    bs.guardar('muerte', reverb(muerte_fantasma(f_amb * 1.6, f_amb * 0.6, vocal), 0.45, 2.6), alto=0.8)
    bs.guardar('paso', tela_ondea(0.4, 0.6), 1, alto=0.25)
    bs.guardar('paso', tela_ondea(0.5, 0.6), 2, alto=0.25)


# ======================================================================================================================
#  Los espectros
# ======================================================================================================================
def espectro_rojo():
    espectro_base('espectro_rojo', 'Espectro Rojo', 'Red Wraith', 150, 'a', {
        'zarpazo': ('Zarpazo de un Espectro Rojo', 'Red Wraith slashes'),
        'agarra': ('Te agarra un Espectro Rojo', 'Red Wraith grabs you'),
    })
    for k in range(3):
        d = 1.4 + 0.3 * k
        sis = filtro_mov(ruido(d), curva(n_(d), [(0, 2500), (1, 4500)]), 'band', 2.5) * ventana(d, 0.1, 0.5)
        x = mezclar(pico(lamento(d, 170 + 20 * k, 120, 'a', 0.5, 2, 0.7), 0.8), pico(sis, 0.4))
        bs.guardar('ambiente', reverb(x, 0.4, 2.4), k + 1, alto=0.55)
    for k in range(2):
        bs.guardar('zarpazo', zarpazo(1.0, 1.0 + 0.1 * k), k + 1, alto=0.8)
    x = mezclar(pico(tela_ondea(0.35, 1.0), 0.8), pico(boom(120, 60, 0.04, 0.2), 0.6))
    bs.guardar('agarra', reverb(x, 0.25, 1.2), alto=0.8)


def espectro_blanco():
    espectro_base('espectro_blanco', 'Espectro Blanco', 'White Wraith', 260, 'o', {
        'zarpazo': ('Zarpazo de un Espectro Blanco', 'White Wraith slashes'),
    })
    for k in range(3):
        d = 2.2 + 0.4 * k
        notas = [(0, 330), (0.3, 294), (0.6, 262), (1, 247)] if k % 2 == 0 else [(0, 294), (0.4, 330), (1, 262)]
        n = n_(d)
        f = curva(n, notas)
        v = garganta(f, d, formantes('o', 1.25), aspereza=0.05, sub=0.0, jitter=0.01, aliento=0.65, fmax=5000)
        x = mezclar(pico(v * ventana(d, 0.4, 0.8), 0.7), pico(armonica_cristal(660, d) * 0.5, 0.25))
        bs.guardar('ambiente', reverb(x, 0.5, 3.0), k + 1, alto=0.5)
    for k in range(2):
        bs.guardar('zarpazo', zarpazo(0.8, 1.4 + 0.1 * k), k + 1, alto=0.7)


def espectro_negro():
    espectro_base('espectro_negro', 'Espectro Negro', 'Black Wraith', 95, 'u', {
        'roba': ('Te roba un corazón un Espectro Negro', 'Black Wraith steals a heart'),
    })
    for k in range(3):
        d = 2.0 + 0.3 * k
        latido = np.zeros(n_(d))
        t = 0.2
        while t < d - 0.3:
            latido = mezclar(latido, en(t, pico(boom(55, 35, 0.06, 0.3), 1.0)), en(t + 0.18, pico(boom(50, 32, 0.05, 0.25), 0.7)))
            t += 0.95
        sus = mezclar(*[en(rng.uniform(0, d - 0.8), bp(susurro(0.7, rng.choice(['a', 'o', 'u']), 0.85), 200, 2500))
                        for _ in range(3)])
        x = mezclar(pico(latido[:n_(d)], 0.6), pico(sus, 0.7))
        bs.guardar('ambiente', reverb(x, 0.45, 2.8), k + 1, alto=0.55)
    x = mezclar(pico(boom(48, 28, 0.25, 1.2), 1.0), en(0.15, pico(soplo(0.8, 3000, 300, 1.0, 0.1)[::-1], 0.6)),
                en(0.1, pico(burbujas(0.5, 30, 200, 700), 0.4)))
    bs.guardar('roba', reverb(x, 0.4, 2.2), alto=0.9)


def espectro_amarillo():
    espectro_base('espectro_amarillo', 'Espectro Amarillo', 'Yellow Wraith', 210, 'e', {
        'posee': ('Se te mete dentro un Espectro Amarillo', 'Yellow Wraith possesses you'),
        'sale': ('Sale de alguien un Espectro Amarillo', 'Yellow Wraith bursts out'),
        'zarpazo': ('Zarpazo de un Espectro Amarillo', 'Yellow Wraith slashes'),
    })
    for k in range(3):
        d = 1.0 + 0.3 * k
        x = mezclar(pico(risa(d, 380 + 40 * k), 0.8), pico(tela_ondea(d, 0.5), 0.3))
        bs.guardar('ambiente', reverb(x, 0.45, 2.4), k + 1, alto=0.55)
    sube = filtro_mov(ruido(1.2, 'rosa'), curva(n_(1.2), [(0, 300), (1, 4000)]), 'band', 3.0) * ventana(1.2, 0.1, 0.2)
    x = mezclar(pico(sube, 0.8), en(0.6, pico(risa(0.6, 520), 0.6)))
    bs.guardar('posee', reverb(x, 0.4, 2.0), alto=0.85)
    x = mezclar(pico(boom(90, 40, 0.08, 0.4), 0.8), pico(soplo(0.5, 400, 3000, 1.0, 0.3), 0.7), en(0.1, pico(risa(0.8, 600), 0.7)))
    bs.guardar('sale', reverb(x, 0.4, 2.0), alto=0.9)
    bs.guardar('zarpazo', zarpazo(0.9, 1.2), alto=0.75)


# ======================================================================================================================
#  Las parcas
# ======================================================================================================================
def resuello(dur, f=500.0):
    n = n_(dur)
    t = t_(dur)
    entra = np.abs(np.sin(np.pi * t / (dur / 2)))
    x = filtro_mov(ruido(dur, 'rosa'), f * (0.7 + 0.5 * entra), 'band', 1.5) * entra
    return x * ventana(dur, 0.1, 0.3)


def huesos(dur, tasa=10.0):
    return chasquidos(dur, tasa, 900, 4500) * ventana(dur, 0.02, 0.2)


def parca_menor():
    bs.empezar('parca_menor', ('abismo', 4200))
    bs.subtitulos('parca_menor', {
        'ambiente': ('Resuella una Parca Menor', 'Lesser Reaper wheezes'),
        'herido': ('Chilla una Parca Menor', 'Lesser Reaper shrieks'),
        'muerte': ('Se deshace una Parca Menor', 'Lesser Reaper fades away'),
        'paso': ('Ondea una túnica', 'A robe flutters'),
        'hoz': ('Silba la hoz de una Parca Menor', 'Lesser Reaper swings its sickle'),
        'destierra': ('Una Parca Menor te destierra', 'Lesser Reaper banishes you'),
    })
    for k in range(3):
        d = 1.6 + 0.3 * k
        x = mezclar(pico(resuello(d, 700), 0.8), pico(huesos(d, 6), 0.3))
        bs.guardar('ambiente', reverb(x, 0.4, 2.2), k + 1, alto=0.5)
    bs.guardar('herido', reverb(herido_fantasma(520, 'e'), 0.3, 1.4), 1, alto=0.7)
    bs.guardar('herido', reverb(herido_fantasma(580, 'a'), 0.3, 1.4), 2, alto=0.7)
    bs.guardar('muerte', reverb(muerte_fantasma(400, 160, 'u', 1.6), 0.45, 2.4), alto=0.8)
    bs.guardar('paso', tela_ondea(0.35, 0.5), alto=0.2)
    for k in range(2):
        bs.guardar('hoz', mezclar(pico(soplo(0.28, 1200, 5000, 1.4, 0.6), 1.0), en(0.2, pico(chasquidos(0.05, 200, 4000, 12000), 0.4))),
                   k + 1, alto=0.75)
    x = mezclar(pico(campana(110, 4.0), 1.0), pico(soplo(1.2, 300, 2500, 1.0, 0.3)[::-1], 0.7),
                en(0.3, pico(coro_voces(2.0, (110, 165, 220), 'u', aliento=0.6), 0.4)))
    bs.guardar('destierra', reverb(x, 0.45, 3.0), alto=0.9)


def parca():
    bs.empezar('parca', ('abismo', 3600))
    bs.subtitulos('parca', {
        'ambiente': ('Respira la Parca', 'The Reaper breathes'),
        'herido': ('La Parca recibe un golpe', 'The Reaper is hit'),
        'muerte': ('La Parca se deshace', 'The Reaper fades away'),
        'paso': ('Ondea una túnica', 'A robe flutters'),
        'guadana': ('Tajo de guadaña', 'Scythe slash'),
        'alma': ('La Parca te arrebata el alma', 'The Reaper reaps your soul'),
    })
    for k in range(3):
        d = 2.4 + 0.3 * k
        x = mezclar(pico(resuello(d, 280), 0.9), pico(huesos(d, 5), 0.25), pico(lamento(d, 70, 60, 'u', 0.6, 2, 0.4), 0.4))
        bs.guardar('ambiente', reverb(x, 0.45, 3.0), k + 1, alto=0.55)
    bs.guardar('herido', reverb(mezclar(pico(huesos(0.4, 40), 0.8), pico(herido_fantasma(220, 'o'), 0.7)), 0.35, 1.8), 1,
               alto=0.75)
    bs.guardar('herido', reverb(mezclar(pico(huesos(0.4, 50), 0.8), pico(herido_fantasma(250, 'a'), 0.7)), 0.35, 1.8), 2,
               alto=0.75)
    bs.guardar('muerte', reverb(mezclar(muerte_fantasma(200, 70, 'u', 2.4), en(0.8, pico(campana(82, 4.0), 0.6))), 0.5, 3.4),
               alto=0.85)
    bs.guardar('paso', tela_ondea(0.5, 0.6), alto=0.25)
    for k in range(2):
        x = mezclar(pico(soplo(0.55, 400, 2400, 1.0, 0.5), 1.0), en(0.35, pico(modos(2600, 0.6, ((1, 1.0), (2.4, 0.4), (4.1, 0.2)), 0.2, 0.003), 0.35)))
        bs.guardar('guadana', reverb(x, 0.3, 1.6), k + 1, alto=0.85)
    x = mezclar(pico(coro_voces(2.6, (73, 110, 147, 220), 'o', aliento=0.5), 0.7), en(0.2, pico(campana(73, 4.0), 1.0)),
                pico(soplo(1.5, 3000, 200, 1.0, 0.2), 0.5))
    bs.guardar('alma', reverb(x, 0.5, 3.6), alto=0.95)


# ======================================================================================================================
#  El Murciélago Vampiro
# ======================================================================================================================
def chillido_murcielago(dur=0.12, f=7000.0):
    n = n_(dur)
    s = seno(curva(n, [(0, f * 1.1), (1, f * 0.8)]), dur, ((1, 1.0), (2, 0.3)))
    return s * caida(dur, dur * 0.4, 0.004)


def aleteo(dur, tasa=9.0):
    n = n_(dur)
    out = np.zeros(n + n_(0.1))
    t = 0.0
    while t < dur:
        g = bp(ruido(0.07), 300, 1800) * caida(0.07, 0.02, 0.005)
        i = int(t * ms.SR)
        out[i:i + len(g)] += g * rng.uniform(0.6, 1.0)
        t += 1.0 / tasa
    return out[:n]


def murcielago():
    bs.empezar('murcielago_vampiro', ('abismo', 6000))
    bs.subtitulos('murcielago_vampiro', {
        'ambiente': ('Chilla un Murciélago Vampiro', 'Vampire Bat squeaks'),
        'herido': ('Chilla un Murciélago Vampiro herido', 'Vampire Bat screeches'),
        'muerte': ('Muere un Murciélago Vampiro', 'Vampire Bat dies'),
        'paso': ('Aletea un murciélago', 'Wings flap'),
        'mordisco': ('Muerde un Murciélago Vampiro', 'Vampire Bat bites'),
        'sorbe': ('Un Murciélago Vampiro te roba un corazón', 'Vampire Bat drains a heart'),
    })
    for k in range(3):
        x = mezclar(*[en(rng.uniform(0, 0.6), pico(chillido_murcielago(0.1, rng.uniform(5500, 8000)), rng.uniform(0.5, 1.0)))
                      for _ in range(3 + k)], pico(aleteo(0.8, 8), 0.4))
        bs.guardar('ambiente', reverb(x, 0.3, 1.4), k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(chillido_murcielago(0.25, 6000 + 500 * k), 1.0), pico(aleteo(0.3, 14), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.7)
    x = mezclar(pico(chillido_murcielago(0.5, 5000), 0.9), pico(aleteo(0.6, 12) * curva(n_(0.6), [(0, 1), (1, 0)]), 0.6))
    bs.guardar('muerte', reverb(x, 0.3, 1.4), alto=0.75)
    bs.guardar('paso', aleteo(0.3, 10), alto=0.35)
    x = mezclar(pico(bp(ruido(0.05), 1500, 6000) * caida(0.05, 0.01), 1.0), en(0.03, pico(burbujas(0.3, 50, 300, 1200), 0.6)))
    bs.guardar('mordisco', x, alto=0.8)
    x = mezclar(pico(burbujas(0.8, 40, 200, 900), 0.8), pico(soplo(0.8, 2500, 400, 1.2, 0.2)[::-1], 0.5),
                en(0.5, pico(boom(60, 35, 0.06, 0.3), 0.6)))
    bs.guardar('sorbe', reverb(x, 0.35, 1.8), alto=0.85)


# ======================================================================================================================
#  El Farolero
# ======================================================================================================================
def crujido_farol(dur):
    return chasquidos(dur, 12, 400, 2500) * 0.6


def zumbido_llama(dur, f=110.0):
    t = t_(dur)
    s = seno(f * (1 + 0.01 * np.sin(2 * np.pi * 3 * t)), dur, ((1, 1.0), (2, 0.5), (3, 0.25), (5, 0.1)))
    return s * (0.7 + 0.3 * np.sin(2 * np.pi * 5.3 * t)) * ventana(dur, 0.2, 0.3)


def farolero():
    bs.empezar('farolero', ('abismo', 4200))
    bs.subtitulos('farolero', {
        'ambiente': ('Cruje el farol del Farolero', "The Lamplighter's lantern creaks"),
        'herido': ('El Farolero recibe un golpe', 'The Lamplighter is hit'),
        'muerte': ('Se apaga el Farolero', 'The Lamplighter goes out'),
        'paso': ('Ondea un abrigo', 'A coat flutters'),
        'mecha': ('La llama del Farolero se hincha', "The Lamplighter's flame swells"),
        'estalla': ('Revienta el Farolero', 'The Lamplighter bursts'),
        'puzzle': ('Se te bloquea la vista', 'Your sight locks up'),
        'golpe': ('Golpea el Farolero', 'The Lamplighter strikes'),
    })
    for k in range(3):
        d = 1.8 + 0.3 * k
        x = mezclar(pico(zumbido_llama(d, 98 + 6 * k), 0.6), pico(crujido_farol(d), 0.5),
                    en(0.4, pico(bp(susurro(0.9, 'o', 1.0), 300, 2500), 0.35)))
        bs.guardar('ambiente', reverb(x, 0.4, 2.4), k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(modos(900 + 100 * k, 0.5, ((1, 1.0), (2.1, 0.6), (3.7, 0.3)), 0.12, 0.004), 0.8),
                    pico(herido_fantasma(300, 'o'), 0.5))
        bs.guardar('herido', reverb(x, 0.3, 1.4), k + 1, alto=0.7)
    vidrio = chasquidos(0.6, curva(n_(0.6), [(0, 400), (1, 10)]), 2500, 12000)
    x = mezclar(pico(vidrio, 0.8), pico(zumbido_llama(1.2, 90) * curva(n_(1.2), [(0, 1), (1, 0)]), 0.6))
    bs.guardar('muerte', reverb(x, 0.4, 2.2), alto=0.8)
    bs.guardar('paso', tela_ondea(0.4, 0.5), alto=0.2)
    n = n_(1.5)
    sube = mezclar(pico(zumbido_llama(1.5, 110) * curva(n, [(0, 0.4), (1, 1.0)]), 0.6),
                   pico(filtro_mov(ruido(1.5), curva(n, [(0, 2000), (1, 8000)]), 'band', 3.0) * curva(n, [(0, 0.2), (1, 1.0)]), 0.6))
    bs.guardar('mecha', sube, alto=0.85)
    golpe = mezclar(pico(boom(70, 30, 0.35, 1.8), 1.0), pico(chasquidos(1.0, curva(n_(1.0), [(0, 600), (1, 20)]), 2000, 12000), 0.7),
                    pico(armonica_cristal(880, 1.4), 0.3))
    bs.guardar('estalla', reverb(saturar(pico(golpe, 1.0), 1.5), 0.3, 2.0), alto=0.95, limite=0.8)
    clic = mezclar(pico(modos(3200, 0.15, ((1, 1.0), (2.3, 0.5)), 0.03, 0.0), 1.0), en(0.08, pico(armonica_cristal(523, 0.9), 0.6)))
    bs.guardar('puzzle', reverb(clic, 0.3, 1.4), alto=0.8)
    bs.guardar('golpe', zarpazo(0.9, 0.9), alto=0.75)


# ======================================================================================================================
#  Los Reclusos y los Colosos
# ======================================================================================================================
COLORES = {'morado': ('Morado', 'Purple', 1.0), 'rojo': ('Rojo', 'Red', 0.9), 'rosa': ('Rosa', 'Pink', 1.12)}


def sollozo(dur, f0=320.0):
    capas = []
    t = 0.0
    while t < dur - 0.3:
        d = rng.uniform(0.25, 0.45)
        v = garganta(curva(n_(d), [(0, f0 * 1.15), (0.4, f0), (1, f0 * 0.85)]), d, formantes('u', 1.3), aspereza=0.3,
                     sub=0.0, jitter=0.06, aliento=0.7) * ventana(d, 0.02, d * 0.6)
        capas.append(en(t, pico(v, rng.uniform(0.6, 1.0))))
        t += d + rng.uniform(0.15, 0.35)
    return mezclar(*capas)


def recluso(color):
    nombre_es, nombre_en, tono = COLORES[color]
    ident = f'recluso_{color}'
    bs.empezar(ident, ('abismo', 4200))
    bs.subtitulos(ident, {
        'ambiente': (f'Solloza un Recluso {nombre_es}', f'{nombre_en} Inmate sobs'),
        'herido': (f'Se queja un Recluso {nombre_es}', f'{nombre_en} Inmate whimpers'),
        'muerte': (f'Se libera un Recluso {nombre_es}', f'{nombre_en} Inmate is set free'),
        'paso': ('Arrastra una cadena', 'A chain drags'),
        'grillete': ('Se cierra un grillete', 'A shackle snaps shut'),
        'golpe': (f'Golpea un Recluso {nombre_es}', f'{nombre_en} Inmate strikes'),
    })
    for k in range(3):
        d = 1.6 + 0.4 * k
        x = mezclar(pico(sollozo(d, 300 * tono), 0.8), pico(cadenas(d, 6, 1800 * tono), 0.4))
        bs.guardar('ambiente', reverb(x, 0.45, 2.6), k + 1, alto=0.5)
    for k in range(2):
        bs.guardar('herido', reverb(mezclar(pico(herido_fantasma(400 * tono, 'u'), 0.8), pico(cadenas(0.3, 25, 2000 * tono), 0.5)),
                                    0.3, 1.4), k + 1, alto=0.7)
    bs.guardar('muerte', reverb(mezclar(muerte_fantasma(380 * tono, 520 * tono, 'o', 1.6),
                                        en(0.2, pico(cadenas(0.8, 30, 1600), 0.5))), 0.5, 2.8), alto=0.8)
    bs.guardar('paso', cadenas(0.4, 14, 1500 * tono), 1, alto=0.3)
    bs.guardar('paso', cadenas(0.4, 14, 1650 * tono), 2, alto=0.3)
    x = mezclar(pico(modos(1100 * tono, 0.4, ((1, 1.0), (2.76, 0.5), (5.4, 0.3)), 0.08, 0.002), 1.0),
                pico(boom(160, 80, 0.02, 0.1), 0.6), en(0.05, pico(cadenas(0.3, 30, 1800), 0.5)))
    bs.guardar('grillete', reverb(x, 0.3, 1.4), alto=0.85)
    bs.guardar('golpe', zarpazo(0.8, 1.0), alto=0.7)


def coloso(color):
    nombre_es, nombre_en, tono = COLORES[color]
    ident = f'coloso_{color}'
    bs.empezar(ident, ('abismo', 3200))
    bs.subtitulos(ident, {
        'ambiente': (f'Gime un Coloso {nombre_es}', f'{nombre_en} Colossus groans'),
        'herido': (f'Ruge un Coloso {nombre_es}', f'{nombre_en} Colossus roars'),
        'muerte': (f'Se derrumba un Coloso {nombre_es}', f'{nombre_en} Colossus collapses'),
        'paso': ('Pasos pesados y cadenas', 'Heavy steps and chains'),
        'golpe': (f'Mazazo de un Coloso {nombre_es}', f'{nombre_en} Colossus smashes'),
    })
    for k in range(3):
        d = 2.4 + 0.4 * k
        v = garganta(curva(n_(d), [(0, 60 * tono), (0.5, 72 * tono), (1, 52 * tono)]), d, formantes('o', 0.7), aspereza=0.8,
                     sub=0.5, jitter=0.05, aliento=0.4, caos=0.4) * ventana(d, 0.3, 0.6)
        x = mezclar(pico(v, 0.9), pico(cadenas(d, 5, 900 * tono, 1.6), 0.4))
        bs.guardar('ambiente', reverb(x, 0.4, 2.8), k + 1, alto=0.6)
    for k in range(2):
        v = garganta(curva(n_(0.6), [(0, 90 * tono), (0.3, 130 * tono), (1, 70 * tono)]), 0.6, formantes('a', 0.75),
                     aspereza=0.9, sub=0.5, jitter=0.06, aliento=0.3, caos=0.5) * ventana(0.6, 0.02, 0.3)
        bs.guardar('herido', reverb(v, 0.35, 2.0), k + 1, alto=0.8)
    x = mezclar(pico(garganta(curva(n_(2.0), [(0, 80 * tono), (1, 35 * tono)]), 2.0, formantes('u', 0.7), aspereza=0.8,
                              sub=0.6, jitter=0.05, aliento=0.4, caos=0.4) * ventana(2.0, 0.05, 0.8), 0.8),
                en(1.3, pico(boom(45, 25, 0.3, 1.5), 1.0)), en(1.3, pico(cadenas(1.0, 40, 800, 1.6), 0.5)))
    bs.guardar('muerte', reverb(x, 0.45, 3.0), alto=0.9)
    for k in range(2):
        x = mezclar(pico(boom(55, 30, 0.12, 0.6), 1.0), pico(cadenas(0.4, 20, 900, 1.6), 0.5))
        bs.guardar('paso', x, k + 1, alto=0.5)
    x = mezclar(pico(soplo(0.3, 300, 1200, 1.0, 0.2), 0.6), en(0.25, pico(boom(50, 26, 0.3, 1.4), 1.0)),
                en(0.25, pico(bp(ruido(0.4), 200, 3000) * caida(0.4, 0.08), 0.6)), en(0.3, pico(cadenas(0.6, 40, 900, 1.6), 0.5)))
    bs.guardar('golpe', reverb(saturar(pico(x, 1.0), 1.4), 0.3, 2.0), alto=0.95, limite=0.8)


# ======================================================================================================================
#  El Ojo Errante, El Pálido y el Vindicador del Limbo
# ======================================================================================================================
def ojo_errante():
    bs.empezar('ojo_errante', ('abismo', 4200))
    bs.subtitulos('ojo_errante', {
        'ambiente': ('Zumba un Ojo Errante', 'Wandering Eye hums'),
        'herido': ('Se retuerce un Ojo Errante', 'Wandering Eye writhes'),
        'muerte': ('Revienta un Ojo Errante', 'Wandering Eye bursts'),
        'paso': ('Algo húmedo flota', 'Something wet drifts'),
        'mira': ('Te mira un Ojo Errante', 'Wandering Eye stares at you'),
        'quema': ('La luz quema a un Ojo Errante', 'The light burns a Wandering Eye'),
    })
    for k in range(3):
        d = 2.0 + 0.3 * k
        zum = seno(55 * (1 + 0.03 * np.sin(2 * np.pi * 0.7 * t_(d))), d, ((1, 1.0), (2, 0.6), (3, 0.3), (4, 0.15)))
        x = mezclar(pico(zum * ventana(d, 0.3, 0.5), 0.6), pico(burbujas(d, 6, 150, 600), 0.35),
                    en(0.5, pico(bp(susurro(0.8, 'e', 1.2), 500, 4000), 0.25)))
        bs.guardar('ambiente', reverb(x, 0.4, 2.6), k + 1, alto=0.5)
    for k in range(2):
        x = mezclar(pico(burbujas(0.4, 60, 200, 1200), 0.8), pico(herido_fantasma(180, 'u'), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.7)
    x = mezclar(pico(boom(80, 30, 0.1, 0.5), 0.8), pico(burbujas(0.8, 120, 150, 1500), 0.8),
                pico(bp(ruido(0.4), 300, 3000) * caida(0.4, 0.08), 0.6))
    bs.guardar('muerte', reverb(x, 0.35, 2.0), alto=0.85)
    bs.guardar('paso', burbujas(0.4, 10, 150, 500), alto=0.2)
    n = n_(1.6)
    zum = seno(curva(n, [(0, 55), (1, 110)]), 1.6, ((1, 1.0), (2, 0.6), (3, 0.4), (5, 0.2), (7, 0.1)))
    bs.guardar('mira', reverb(zum * curva(n, [(0, 0.2), (1, 1.0)]) * ventana(1.6, 0.1, 0.2), 0.4, 2.2), alto=0.8)
    x = mezclar(pico(chasquidos(0.8, 160, 2500, 10000), 0.7), pico(burbujas(0.8, 40, 300, 1500), 0.5),
                pico(herido_fantasma(260, 'e'), 0.5))
    bs.guardar('quema', x * ventana(0.8, 0.01, 0.3), alto=0.8)


def palido():
    bs.empezar('palido', ('abismo', 5000))
    bs.subtitulos('palido', {
        'ambiente': ('Algo cruje en el silencio', 'Something crackles in the silence'),
        'herido': ('El Pálido se estremece', 'The Pale One shudders'),
        'muerte': ('El Pálido se desvanece', 'The Pale One vanishes'),
        'paso': ('Pasos que no deberían estar', 'Footsteps that should not be'),
        'aparece': ('Aparece El Pálido', 'The Pale One appears'),
        'desaparece': ('Se va El Pálido', 'The Pale One leaves'),
        'grito': ('El Pálido grita', 'The Pale One screams'),
    })
    for k in range(2):
        bs.guardar('ambiente', estatica(1.2 + 0.4 * k, 0.15) * ventana(1.2 + 0.4 * k, 0.4, 0.5), k + 1, alto=0.2)
    bs.guardar('herido', estatica(0.3, 0.8), alto=0.6)
    x = mezclar(pico(estatica(0.6, 1.0) * curva(n_(0.6), [(0, 1), (1, 0)]), 0.8), pico(soplo(0.8, 2000, 200, 1.0, 0.1), 0.5))
    bs.guardar('muerte', reverb(x, 0.4, 2.0), alto=0.7)
    for k in range(2):
        bs.guardar('paso', pb(bp(ruido(0.08), 200, 1500) * caida(0.08, 0.02), 1500), k + 1, alto=0.2)
    x = mezclar(pico(estatica(0.25, 1.0), 0.8), pico(boom(60, 30, 0.08, 0.4), 0.6))
    bs.guardar('aparece', reverb(x, 0.4, 2.0), alto=0.8)
    x = mezclar(pico(estatica(0.2, 1.0), 0.7), pico(soplo(0.6, 300, 3000, 1.0, 0.2)[::-1], 0.6))
    bs.guardar('desaparece', reverb(x, 0.4, 2.0), alto=0.75)
    v = garganta(curva(n_(1.0), [(0, 600), (0.2, 900), (1, 400)]), 1.0, formantes('a', 1.3), aspereza=1.0, sub=0.2,
                 jitter=0.1, aliento=0.6, caos=0.8) * ventana(1.0, 0.01, 0.4)
    x = mezclar(pico(v, 1.0), pico(estatica(1.0, 1.0), 0.5))
    bs.guardar('grito', reverb(saturar(pico(x, 1.0), 1.6), 0.35, 2.0), alto=0.95, limite=0.8)


def vindicador():
    bs.empezar('vindicador_limbo', ('abismo', 4500))
    bs.subtitulos('vindicador_limbo', {
        'ambiente': ('Gruñe un Vindicador del Limbo', 'Limbo Vindicator grumbles'),
        'herido': ('Se queja un Vindicador del Limbo', 'Limbo Vindicator hurts'),
        'muerte': ('Cae un Vindicador del Limbo', 'Limbo Vindicator falls'),
        'paso': ('Pasos con armadura', 'Armored steps'),
        'hachazo': ('Hachazo espectral', 'Spectral axe chop'),
        'rompe': ('Se te rompe el escudo', 'Your shield breaks'),
    })
    for k in range(3):
        d = 0.8 + 0.2 * k
        v = garganta(curva(n_(d), [(0, 150), (0.4, 175), (1, 130)]), d, formantes('o', 1.0), aspereza=0.6, sub=0.2,
                     jitter=0.04, aliento=0.3, caos=0.2) * ventana(d, 0.03, 0.3)
        bs.guardar('ambiente', reverb(v, 0.45, 2.4), k + 1, alto=0.55)
    for k in range(2):
        v = garganta(curva(n_(0.3), [(0, 180), (0.3, 240), (1, 150)]), 0.3, formantes('a', 1.0), aspereza=0.7, sub=0.2,
                     jitter=0.05, aliento=0.3) * ventana(0.3, 0.01, 0.15)
        bs.guardar('herido', reverb(v, 0.35, 1.6), k + 1, alto=0.7)
    v = garganta(curva(n_(1.0), [(0, 170), (1, 70)]), 1.0, formantes('u', 1.0), aspereza=0.6, sub=0.3, jitter=0.05,
                 aliento=0.4) * ventana(1.0, 0.02, 0.5)
    bs.guardar('muerte', reverb(mezclar(pico(v, 0.8), en(0.6, pico(cadenas(0.4, 30, 1200), 0.4))), 0.45, 2.6), alto=0.8)
    for k in range(2):
        bs.guardar('paso', mezclar(pico(boom(110, 60, 0.02, 0.1), 0.7), pico(cadenas(0.15, 30, 2400), 0.4)), k + 1, alto=0.3)
    x = mezclar(pico(soplo(0.35, 500, 2600, 1.1, 0.4), 0.8), en(0.25, pico(armonica_cristal(740, 0.8), 0.4)))
    bs.guardar('hachazo', reverb(x, 0.3, 1.4), alto=0.85)
    x = mezclar(pico(modos(700, 0.6, ((1, 1.0), (1.8, 0.7), (2.9, 0.5), (4.6, 0.3)), 0.1, 0.01), 1.0),
                pico(chasquidos(0.4, curva(n_(0.4), [(0, 300), (1, 10)]), 1500, 8000), 0.7), pico(boom(90, 45, 0.05, 0.3), 0.6))
    bs.guardar('rompe', reverb(saturar(pico(x, 1.0), 1.3), 0.3, 1.6), alto=0.9)


MOBS = {'espectro_rojo': espectro_rojo, 'espectro_blanco': espectro_blanco, 'espectro_negro': espectro_negro,
        'espectro_amarillo': espectro_amarillo, 'parca_menor': parca_menor, 'parca': parca,
        'murcielago_vampiro': murcielago, 'farolero': farolero, 'ojo_errante': ojo_errante, 'palido': palido,
        'vindicador_limbo': vindicador}
for _c in COLORES:
    MOBS[f'recluso_{_c}'] = (lambda c: lambda: recluso(c))(_c)
    MOBS[f'coloso_{_c}'] = (lambda c: lambda: coloso(c))(_c)


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
