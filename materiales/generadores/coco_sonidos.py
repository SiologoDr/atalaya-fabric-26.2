"""
Los sonidos del Coco (16-10-2026), el mob que te mete en la barriga. Todos nuestros:

  coco.ambiente    lo que se le oye cerca: las tripas que gruñen, un resuello hondo y, a veces, la nana tarareada con la
                   boca cerrada (las tres primeras notas de «duermete niño»)
  coco.paso        el paso pesado: un golpe sordo y la carne de la barriga que rebota
  coco.herido      al pegarle: el golpe hueco de la cascara (un coco que suena a coco) y un gruñido
  coco.muerte      al morir: un quejido largo que baja, la cascara que se raja y el aire que se le escapa
  coco.aviso       el segundo de aviso: la cascara que cruje al abrirse y la boca que aspira
  coco.traga       te traga: el golpe de la quijada, el trago (un «glup» que baja) y la barriga que se cierra
  coco.digiere     con alguien dentro: las tripas que borbotean (cada vez que te quita vida)
  coco.latido      lo que oye el que esta dentro: un corazon grande y sordo, a traves de la carne
  coco.revienta    al matarlo con alguien dentro: la barriga que revienta y el que sale
  coco.manotazo    el manotazo con el que se defiende: el aire y el golpe

Usa las utilidades de minijefes_sonidos.py. Uso: python coco_sonidos.py <raiz> [hoja]
"""
import sys
import numpy as np

import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, burbujas, caida, chasquidos, curva, en, filtro_mov, formantes, garganta,
                               mezclar, modos, n_, pa, pb, pico, resonar, reverb, ruido, saturar, t_, ventana)

ms.SUBTITULOS['coco'] = {
    'ambiente': ('Le gruñen las tripas a un Coco', 'Coco\'s stomach growls'),
    'paso': ('Pasos pesados', 'Heavy footsteps'),
    'herido': ('Un Coco gruñe', 'Coco grunts'),
    'muerte': ('Muere un Coco', 'Coco dies'),
    'aviso': ('Un Coco abre la cáscara', 'Coco cracks its shell open'),
    'traga': ('Un Coco traga', 'Coco swallows'),
    'digiere': ('Un Coco hace la digestión', 'Coco digests'),
    'latido': ('Un latido, a través de la carne', 'A heartbeat, through the flesh'),
    'revienta': ('Revienta la barriga de un Coco', 'Coco\'s belly bursts'),
    'manotazo': ('Un Coco da un manotazo', 'Coco swipes'),
}
ms.SALAS['coco'] = ('plaza', 6000)               # en las afueras de la aldea
rng = np.random.default_rng(20261016)


def cascara(fuerza=1.0, f=640.0):
    """El golpe hueco de la cascara: un coco de verdad suena a madera hueca (un modo grave y dos agudos que se apagan
    enseguida), con el chasquido de la fibra."""
    golpe = modos(f, 0.35, ((1.0, 1.0), (2.3, 0.45), (3.9, 0.25)), 0.05)
    fibra = bp(ruido(0.03), 2500, 9000) * caida(0.03, 0.004, 0.0003)
    return pico(mezclar(pico(golpe, 1.0), pico(fibra, 0.5)), fuerza)


def gruñido(dur, f0, f1, vocal='o', aspereza=0.6, caos=0.3):
    """Una voz grande y ronca, con la boca medio cerrada."""
    n = n_(dur)
    v = garganta(curva(n, [(0, f0), (1, f1)]), dur, formantes(vocal, 0.62), aspereza=aspereza, sub=0.45, jitter=0.05,
                 aliento=0.3, fmax=3000, caos=caos)
    return pb(v, 2200, 2) * ventana(dur, 0.04, dur * 0.5)


def tripas(dur, fuerza=1.0):
    """Las tripas: borboteo grave con resonancias de cavidad y un gruñido de fondo que sube y baja."""
    n = n_(dur)
    b = burbujas(dur, curva(n, [(0, 6), (0.3, 22), (0.7, 14), (1, 3)]), 90, 520, 1.0)
    cav = resonar(pb(ruido(dur, 'marron'), 300, 2), 140, 4.0) * curva(n, [(0, 0), (0.2, 1), (0.8, 0.6), (1, 0)])
    rugido = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 90), (0.5, 220), (1, 80)]), 'band', 5.0)
    rugido *= 0.5 + 0.5 * np.sin(2 * np.pi * 7.0 * t_(dur)) ** 2
    return pico(mezclar(pico(b, 1.0), pico(cav, 0.6), pico(rugido, 0.45)) * ventana(dur, 0.08, dur * 0.4), fuerza)


def tararea(notas, dur_nota=0.42):
    """La nana tarareada con la boca cerrada: «mm» de voz grave, con un poco de vibrato."""
    partes = []
    for f in notas:
        n = n_(dur_nota)
        tono = f * (1 + 0.012 * np.sin(2 * np.pi * 5.0 * t_(dur_nota)))
        v = garganta(tono, dur_nota, ((250, 60, 1.0), (800, 120, 0.25), (2300, 200, 0.05)), aspereza=0.15, sub=0.2,
                     jitter=0.02, aliento=0.1, fmax=2500)
        partes.append(pb(v, 1200, 2) * ventana(dur_nota, 0.06, 0.14))
    return np.concatenate(partes)


def ambiente(k):
    if k == 0:
        return reverb(mezclar(pico(tripas(1.8), 1.0), en(0.3, pico(gruñido(1.0, 62, 52, 'u', 0.4, 0.2), 0.45))), 0.2, 1.4)
    if k == 1:                                                    # duer-me-te: mi, mi, do (abajo, con la boca cerrada)
        x = tararea((82.4, 82.4, 65.4), 0.46)
        return reverb(mezclar(pico(x, 1.0), en(1.1, pico(tripas(0.7), 0.3))), 0.25, 1.6)
    soplo = pb(ruido(1.2, 'rosa'), 700, 2) * curva(n_(1.2), [(0, 0), (0.3, 1), (0.6, 0.2), (0.8, 0.8), (1, 0)])
    return reverb(mezclar(pico(soplo, 0.6), pico(gruñido(1.2, 58, 48, 'o', 0.7, 0.4), 0.8)), 0.2, 1.4)


def paso(k):
    golpe = boom(58 - 6 * k, 30, 0.12, 0.45)
    carne = bp(ruido(0.25, 'rosa'), 120, 600) * caida(0.25, 0.05, 0.003)
    rebote = en(0.09, boom(90, 60, 0.05, 0.2)) * 0.5
    return mezclar(pico(golpe, 1.0), pico(carne, 0.5), pico(rebote, 0.4))


def herido(k):
    dur = 0.7
    return reverb(mezclar(pico(cascara(1.0, 620 + 70 * k), 1.0), en(0.02, pico(gruñido(0.55, 95 - 10 * k, 70), 0.75))),
                  0.15, 1.0)


def muerte():
    dur = 2.4
    queja = gruñido(1.9, 85, 38, 'a', 0.8, 0.5)
    raja = chasquidos(0.5, curva(n_(0.5), [(0, 400), (1, 40)]), 900, 6000, 1.0) * ventana(0.5, 0.005, 0.3)
    aire = pb(ruido(1.2, 'rosa'), 900, 2) * curva(n_(1.2), [(0, 0), (0.15, 1), (1, 0)])
    x = mezclar(pico(queja, 0.9), en(0.6, pico(raja, 0.6)), en(0.6, pico(cascara(0.8, 520), 0.7)), en(1.1, pico(aire, 0.4)))
    return reverb(x, 0.25, 1.8)


def aviso():
    """Un segundo (20 ticks): la cascara que cruje al abrirse, cada vez mas, y la boca que aspira."""
    dur = 1.0
    n = n_(dur)
    cruje = chasquidos(dur, curva(n, [(0, 15), (0.7, 160), (1, 240)]), 600, 5000, 1.0)
    cruje = resonar(cruje, 900, 3.0) * 0.6 + cruje * 0.4
    aspira = filtro_mov(ruido(dur, 'rosa'), curva(n, [(0, 300), (1, 1800)]), 'band', 2.0) * curva(n, [(0, 0), (1, 1)]) ** 2
    ronco = gruñido(0.8, 48, 60, 'a', 0.9, 0.6)
    return reverb(mezclar(pico(cruje, 0.8), pico(aspira, 0.5), en(0.2, pico(ronco, 0.55))), 0.15, 1.0)


def traga():
    dur = 1.2
    n = n_(0.35)
    golpe = mezclar(pico(cascara(1.0, 480), 1.0), pico(boom(70, 40, 0.1, 0.4), 0.8))
    glup = np.sin(2 * np.pi * np.cumsum(curva(n, [(0, 320), (1, 70)])) / ms.SR) * caida(0.35, 0.12, 0.01)
    moja = bp(ruido(0.4), 200, 1500) * caida(0.4, 0.08, 0.01)
    cierra = boom(55, 35, 0.2, 0.6)
    x = mezclar(pico(golpe, 0.9), en(0.18, pico(glup, 1.0)), en(0.2, pico(moja, 0.45)), en(0.45, pico(cierra, 0.8)),
                en(0.5, pico(tripas(0.7), 0.4)))
    return reverb(x, 0.18, 1.2)


def digiere(k):
    return reverb(tripas(1.5 + 0.2 * k, 1.0), 0.15, 1.0)


def latido():
    """Lub-dub, grave y sordo, como oido desde dentro."""
    def golpe(f, a):
        return boom(f, f * 0.6, 0.07, 0.3) * a
    x = mezclar(golpe(55, 1.0), en(0.24, golpe(48, 0.7)))
    return pb(x, 180, 2)


def revienta():
    dur = 1.6
    pop = pa(ruido(0.08), 300) * caida(0.08, 0.012, 0.001)
    salpica = bp(ruido(0.7), 500, 4000) * caida(0.7, 0.15, 0.005)
    gotas = burbujas(0.9, curva(n_(0.9), [(0, 60), (1, 2)]), 400, 2000, 1.0)
    golpe = boom(62, 28, 0.25, 1.0)
    x = mezclar(pico(pop, 1.0), pico(salpica, 0.6), en(0.05, pico(gotas, 0.4)), pico(golpe, 0.9),
                en(0.15, pico(gruñido(0.9, 70, 40, 'a', 0.9, 0.5), 0.5)))
    return reverb(saturar(pico(x, 1.0), 1.4), 0.25, 1.6)


def manotazo(k):
    dur = 0.5
    aire = filtro_mov(ruido(0.3, 'rosa'), curva(n_(0.3), [(0, 400), (0.6, 2200), (1, 600)]), 'band', 1.5)
    aire *= np.sin(np.pi * t_(0.3) / 0.3) ** 2
    golpe = boom(80, 45, 0.08, 0.3)
    return mezclar(pico(aire, 0.8), en(0.22, pico(golpe, 1.0)), en(0.2, pico(gruñido(0.3, 110 - 10 * k, 90), 0.4)))


def main():
    ms.empezar('coco')
    for k in range(3):
        ms.guardar('ambiente', ambiente(k), k + 1, alto=0.75)
    for k in range(2):
        ms.guardar('paso', paso(k), k + 1, alto=0.7)
        ms.guardar('herido', herido(k), k + 1, alto=0.85)
        ms.guardar('digiere', digiere(k), k + 1, alto=0.75)
        ms.guardar('manotazo', manotazo(k), k + 1, alto=0.8)
    ms.guardar('muerte', muerte(), alto=0.85)
    ms.guardar('aviso', aviso(), alto=0.85)
    ms.guardar('traga', traga(), alto=0.9)
    ms.guardar('latido', latido(), alto=0.8)
    ms.guardar('revienta', revienta(), alto=0.9, limite=0.7)
    ms.escribir_json()
    if len(sys.argv) > 2:
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
