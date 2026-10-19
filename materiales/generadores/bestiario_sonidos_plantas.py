"""
Los sonidos de las plantas del bestiario (bestia.<id>.<nombre>): hechos de hojas que se rozan (un susurro seco de
chasquidos finos), tallos que crujen (una fricción lenta y áspera, como madera verde que se dobla), lo húmedo (burbujas
y chapoteos cortos) y, en cada una, lo suyo:

  fauces_*      la respiración húmeda de la boca entreabierta, el mordisco (el golpe de las dos mandíbulas, el
                castañeteo de los dientes y el chapoteo) y lo de su color: el ácido que chisporrotea (verde), la
                llamarada (carmín) y la escarcha que cruje al cuajar (escarcha)
  trampa        casi nada mientras espera (un roce de hierba); al cerrarse, un latigazo de hojas y el golpe de las
                pestañas; al masticar, chapoteos; al abrirse, el crujido lento de la bisagra
  pina          una vocecita gruñona (sílabas cortas y ásperas), el crujido de la corona, los pasitos de raíz y el
                puñetazo (un silbido corto y un golpe sordo)
  zombi_planta  el gemido de zombi mezclado con hojas y con el zumbido del polen, los pasos que se arrancan del suelo,
                las raíces que te atrapan (crujidos de madera y tierra) y el florecer al sol (unas notas claras y aire)

Uso: python bestiario_sonidos_plantas.py <raíz> [hoja] [ids]
"""
import sys

import numpy as np

import bestiario_sonidos as bs
import minijefes_sonidos as ms
from minijefes_sonidos import (boom, bp, burbujas, caida, chasquidos, curva, en, filtro_mov, formantes, garganta,
                               mezclar, n_, pa, pb, pico, reverb, ruido, saturar, seno, soplo, t_, ventana)

rng = np.random.default_rng(20261022)


# ======================================================================================================================
#  Lo de todas
# ======================================================================================================================
def hojas(dur, tasa=60.0, f=3000.0):
    """Hojas que se rozan: chasquidos finos y un soplo de ruido que va y viene."""
    n = n_(dur)
    t = t_(dur)
    vaiven = 0.55 + 0.45 * np.sin(2 * np.pi * rng.uniform(1.5, 3.0) * t + rng.uniform(0, 6))
    c = chasquidos(dur, tasa * vaiven, f * 0.5, f * 2.6)
    s = bp(ruido(dur, 'rosa'), f * 0.6, f * 2.2) * vaiven
    return mezclar(pico(c, 0.9), pico(s, 0.35)) * ventana(dur, dur * 0.15, dur * 0.35)


def crujido(dur, f0=55.0, aspero=0.8):
    """Un tallo que cruje al doblarse: una fricción lenta, a tirones (madera verde)."""
    n = n_(dur)
    tirones = np.clip(np.cumsum(rng.normal(0, 1, n)) / np.sqrt(n) * 3, -1, 1)
    f = f0 * (1.0 + 0.5 * tirones)
    voz = garganta(f, dur, ((380, 120, 1.0), (950, 160, 0.6), (2300, 300, 0.3)), aspereza=aspero, sub=0.1,
                   jitter=0.12, aliento=0.1, fmax=3000, caos=0.5)
    return voz * ventana(dur, 0.05, dur * 0.3)


def chapoteo(dur=0.25, f=700.0, fuerza=1.0):
    """Algo húmedo: un golpe de agua corto y unas burbujas."""
    golpe = bp(ruido(dur), f * 0.5, f * 2.5) * caida(dur, dur * 0.18, 0.002)
    return mezclar(pico(golpe, fuerza), pico(burbujas(dur, 40, f * 0.6, f * 2.2), 0.5))


def golpe_hojas(fuerza=1.0, f=900.0):
    """El latigazo de algo verde que se cierra de golpe: un chasquido de banda ancha y su cuerpo grave."""
    seco = bp(ruido(0.06), f * 0.4, f * 6) * caida(0.06, 0.012, 0.001)
    cuerpo = boom(f * 0.18, f * 0.08, 0.04, 0.2)
    return mezclar(pico(seco, 1.0 * fuerza), pico(cuerpo, 0.7 * fuerza))


def dientes(dur=0.12, tasa=90.0):
    """El castañeteo de los dientes al cruzarse."""
    return chasquidos(dur, tasa, 2500, 9000) * ventana(dur, 0.002, dur * 0.5)


def respiracion(dur, f=420.0):
    """La boca entreabierta que respira: aire húmedo por una garganta de planta (sin cuerdas)."""
    n = n_(dur)
    t = t_(dur)
    entra = np.sin(np.pi * t / dur) ** 1.5
    aire = filtro_mov(ruido(dur, 'rosa'), f * (0.8 + 0.4 * entra), 'band', 1.4) * entra
    return mezclar(pico(aire, 0.8), pico(burbujas(dur, 6, 200, 700) * entra, 0.3))


def chisporroteo(dur, tasa=140.0):
    """Ácido que chisporrotea: crepitar agudo y un siseo."""
    return mezclar(pico(chasquidos(dur, tasa, 3500, 12000), 0.8), pico(pa(ruido(dur), 5000) * 0.3, 0.4))


def escarcha(dur, sube=True):
    """La escarcha que cuaja: crujidos cristalinos cada vez más seguidos y unas notas de vidrio."""
    n = n_(dur)
    tasa = curva(n, [(0, 20), (1, 260)] if sube else [(0, 200), (1, 10)])
    cr = chasquidos(dur, tasa, 3000, 13000)
    vidrio = np.zeros(n)
    for k in range(5):
        f = rng.uniform(2400, 5200)
        i = int(rng.uniform(0, dur * 0.8) * ms.SR)
        d = min(0.5, (n - i) / ms.SR)
        x = seno(f, d, ((1, 1.0), (2.76, 0.4), (5.4, 0.2))) * caida(d, 0.12, 0.001)
        vidrio[i:i + len(x)] += x[:n - i]
    hielo = bp(ruido(dur), 4000, 9000) * curva(n, [(0, 0.1), (1, 0.6)] if sube else [(0, 0.6), (1, 0.1)])
    return mezclar(pico(cr, 0.8), pico(vidrio, 0.4), pico(hielo, 0.3))


def llamarada(dur=0.6):
    return mezclar(pico(soplo(dur, 250, 1100, 0.9, 0.0), 1.0), pico(chasquidos(dur, 90, 1200, 7000), 0.5),
                   pico(boom(110, 50, 0.05, 0.3), 0.4))


# ======================================================================================================================
#  Las Fauces
# ======================================================================================================================
COLOR = {'verde': ('Verde', 'Green', 1.0), 'carmin': ('Carmín', 'Crimson', 0.88), 'escarcha': ('Escarcha', 'Frost', 1.1)}


def fauces(color):
    nombre_es, nombre_en, tono = COLOR[color]
    ident = f'fauces_{color}'
    bs.empezar(ident)
    extra = {'verde': ('acido', ('Chisporrotea el ácido de una Fauces', 'Maw acid sizzles')),
             'carmin': ('quema', ('Prende el mordisco de una Fauces', 'Maw bite ignites')),
             'escarcha': ('hiela', ('Cruje la escarcha de una Fauces', 'Maw frost crackles'))}[color]
    bs.subtitulos(ident, {
        'ambiente': (f'Respira una Fauces {nombre_es}', f'{nombre_en} Maw breathes'),
        'herido': (f'Chilla una Fauces {nombre_es}', f'{nombre_en} Maw shrieks'),
        'muerte': (f'Se marchita una Fauces {nombre_es}', f'{nombre_en} Maw withers'),
        'mordisco': (f'Muerde una Fauces {nombre_es}', f'{nombre_en} Maw bites'),
        extra[0]: extra[1],
    })
    for k in range(3):
        d = 1.2 + 0.3 * k
        x = mezclar(pico(respiracion(d, 420 * tono), 0.8), en(0.2 + 0.2 * k, pico(hojas(0.6, 40, 2800 * tono), 0.4)))
        if k == 1:
            x = mezclar(x, en(0.6, pico(crujido(0.5, 60 * tono, 0.7), 0.35)))
        if k == 2:
            x = mezclar(x, en(0.9, pico(dientes(0.1, 60), 0.4)))
        bs.guardar('ambiente', reverb(x, 0.15, 1.0), k + 1, alto=0.45)
    for k in range(2):
        voz = garganta(curva(n_(0.35), [(0, 700 * tono), (0.3, 950 * tono), (1, 500 * tono)]), 0.35,
                       formantes('e', 1.5), aspereza=0.9, sub=0.0, jitter=0.08, aliento=0.6, caos=0.5)
        x = mezclar(pico(voz * ventana(0.35, 0.01, 0.15), 0.7), pico(hojas(0.3, 160, 3200), 0.6),
                    pico(chapoteo(0.2, 600 * tono), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.7)
    dur = 1.6
    n = n_(dur)
    x = mezclar(pico(crujido(dur, curva(n, [(0, 70 * tono), (1, 35 * tono)]), 0.9), 0.8),
                pico(hojas(dur, 90, 2600) * curva(n, [(0, 0.3), (0.6, 1.0), (1, 0.2)]), 0.6),
                en(1.2, pico(golpe_hojas(0.6, 500), 0.5)))
    bs.guardar('muerte', reverb(x, 0.2, 1.3), alto=0.75)
    for k in range(2):
        x = mezclar(pico(golpe_hojas(1.2, 800 * tono), 1.0), en(0.005, pico(dientes(0.1, 120), 0.7)),
                    en(0.02, pico(chapoteo(0.3, 700 * tono, 1.0), 0.7)))
        bs.guardar('mordisco', reverb(saturar(pico(x, 1.0), 1.4), 0.12, 0.9), k + 1, alto=0.9)
    if color == 'verde':
        x = mezclar(pico(chisporroteo(0.9, 160), 0.9), pico(burbujas(0.9, 30, 400, 1800), 0.5))
        bs.guardar('acido', x * ventana(0.9, 0.01, 0.4), alto=0.7)
    elif color == 'carmin':
        bs.guardar('quema', llamarada(0.7), alto=0.8)
    else:
        bs.guardar('hiela', reverb(escarcha(1.0), 0.25, 1.4), alto=0.8)


# ======================================================================================================================
#  La Trampa Verde
# ======================================================================================================================
def trampa():
    bs.empezar('trampa')
    bs.subtitulos('trampa', {
        'ambiente': ('Se mece la hierba', 'Grass rustles'),
        'herido': ('Se retuerce una Trampa Verde', 'Green Trap writhes'),
        'muerte': ('Se marchita una Trampa Verde', 'Green Trap withers'),
        'cierra': ('Se cierra una Trampa Verde', 'Green Trap snaps shut'),
        'mastica': ('Mastica una Trampa Verde', 'Green Trap chews'),
        'abre': ('Se abre una Trampa Verde', 'Green Trap opens'),
    })
    for k in range(2):
        bs.guardar('ambiente', hojas(1.0 + 0.4 * k, 20, 2400) * 0.6, k + 1, alto=0.25)
    for k in range(2):
        x = mezclar(pico(crujido(0.4, 90, 0.9), 0.7), pico(hojas(0.35, 180, 2800), 0.6),
                    pico(chapoteo(0.25, 500), 0.5))
        bs.guardar('herido', x, k + 1, alto=0.7)
    x = mezclar(pico(crujido(1.4, curva(n_(1.4), [(0, 80), (1, 40)]), 0.8), 0.7),
                pico(hojas(1.4, 70, 2400), 0.6))
    bs.guardar('muerte', reverb(x, 0.2, 1.2), alto=0.72)
    # El cierre: el roce de las hojas que se levantan, el latigazo y las pestañas que se cruzan.
    sube = soplo(0.12, 900, 3000, 1.0, 0.1)
    x = mezclar(pico(sube, 0.5), en(0.1, pico(golpe_hojas(1.6, 700), 1.0)), en(0.105, pico(dientes(0.14, 160), 0.8)),
                en(0.12, pico(chapoteo(0.3, 450, 0.8), 0.6)))
    bs.guardar('cierra', reverb(saturar(pico(x, 1.0), 1.5), 0.15, 1.0), alto=0.95, limite=0.8)
    for k in range(2):
        x = mezclar(pico(chapoteo(0.3, 400 + 120 * k), 0.8), en(0.05, pico(crujido(0.25, 70, 0.6), 0.4)),
                    en(0.12, pico(chapoteo(0.2, 650), 0.5)))
        bs.guardar('mastica', x, k + 1, alto=0.6)
    x = mezclar(pico(crujido(0.9, curva(n_(0.9), [(0, 45), (1, 75)]), 0.6), 0.8), pico(hojas(0.9, 50, 2600), 0.5))
    bs.guardar('abre', x, alto=0.6)


# ======================================================================================================================
#  La Piña Brava
# ======================================================================================================================
def gruñido(dur, f0=360.0, vocal='a'):
    """Una sílaba gruñona de la Piña: corta, áspera, con el tono que cae."""
    n = n_(dur)
    f = curva(n, [(0, f0 * 1.15), (0.3, f0), (1, f0 * 0.8)])
    v = garganta(f, dur, formantes(vocal, 1.55), aspereza=0.75, sub=0.25, jitter=0.05, aliento=0.3, caos=0.25)
    return v * ventana(dur, 0.012, dur * 0.4)


def pina():
    bs.empezar('pina')
    bs.subtitulos('pina', {
        'ambiente': ('Gruñe una Piña Brava', 'Fierce Pineapple grumbles'),
        'herido': ('Chilla una Piña Brava', 'Fierce Pineapple squeals'),
        'muerte': ('Revienta una Piña Brava', 'Fierce Pineapple bursts'),
        'paso': ('Pasitos de raíz', 'Root feet patter'),
        'puno': ('Da un puñetazo una Piña Brava', 'Fierce Pineapple punches'),
    })
    for k in range(3):
        silabas = []
        t = 0.0
        for j in range(2 + k):
            d = rng.uniform(0.09, 0.16)
            silabas.append(en(t, pico(gruñido(d, rng.uniform(320, 420), rng.choice(['a', 'o', 'e'])), 0.9)))
            t += d + rng.uniform(0.03, 0.08)
        x = mezclar(*silabas, en(0.05, pico(hojas(t + 0.2, 70, 3400), 0.35)))
        bs.guardar('ambiente', reverb(x, 0.12, 0.8), k + 1, alto=0.5)
    for k in range(2):
        v = garganta(curva(n_(0.22), [(0, 600), (0.4, 820), (1, 520)]), 0.22, formantes('e', 1.7), aspereza=0.8,
                     sub=0.1, jitter=0.06, aliento=0.4, caos=0.4) * ventana(0.22, 0.008, 0.1)
        x = mezclar(pico(v, 0.8), pico(hojas(0.2, 220, 3600), 0.5), pico(golpe_hojas(0.4, 1200), 0.3))
        bs.guardar('herido', x, k + 1, alto=0.7)
    v = garganta(curva(n_(0.5), [(0, 520), (1, 260)]), 0.5, formantes('o', 1.6), aspereza=0.8, sub=0.2, jitter=0.06,
                 aliento=0.4, caos=0.3) * ventana(0.5, 0.01, 0.3)
    x = mezclar(pico(v, 0.7), en(0.3, pico(chapoteo(0.35, 900, 1.0), 0.8)), en(0.3, pico(hojas(0.6, 160, 3000), 0.5)))
    bs.guardar('muerte', reverb(x, 0.15, 1.0), alto=0.75)
    for k in range(2):
        x = mezclar(pico(boom(160 + 30 * k, 80, 0.015, 0.08), 1.0), pico(chasquidos(0.06, 80, 600, 3000), 0.4))
        bs.guardar('paso', x, k + 1, alto=0.3)
    for k in range(2):
        x = mezclar(pico(soplo(0.1, 600, 2200, 1.2, 0.15), 0.6),
                    en(0.08, pico(boom(140, 60, 0.03, 0.15), 1.0)), en(0.08, pico(golpe_hojas(0.7, 1400), 0.6)))
        bs.guardar('puno', x, k + 1, alto=0.75)


# ======================================================================================================================
#  El Zombi Planta
# ======================================================================================================================
def gemido(dur, f0=95.0, vocal='o'):
    n = n_(dur)
    f = curva(n, [(0, f0 * 0.9), (0.4, f0 * 1.1), (1, f0 * 0.75)])
    v = garganta(f, dur, formantes(vocal, 0.95), aspereza=0.7, sub=0.4, jitter=0.06, aliento=0.35, caos=0.35)
    return v * ventana(dur, dur * 0.15, dur * 0.4)


def polen(dur):
    """El zumbido del polen: un siseo que tiembla."""
    t = t_(dur)
    return bp(ruido(dur), 2800, 6000) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t)) * ventana(dur, dur * 0.2, dur * 0.4)


def zombi_planta():
    bs.empezar('zombi_planta')
    bs.subtitulos('zombi_planta', {
        'ambiente': ('Gime un Zombi Planta', 'Plant Zombie groans'),
        'herido': ('Se queja un Zombi Planta', 'Plant Zombie hurts'),
        'muerte': ('Muere un Zombi Planta', 'Plant Zombie dies'),
        'paso': ('Pasos que arrancan raíces', 'Rooted footsteps'),
        'enraiza': ('Brotan raíces', 'Roots burst out'),
        'florece': ('Florece un Zombi Planta', 'Plant Zombie blooms'),
    })
    for k in range(3):
        d = 1.1 + 0.25 * k
        x = mezclar(pico(gemido(d, 90 + 10 * k, ['o', 'u', 'a'][k]), 0.9), pico(hojas(d, 40, 2600), 0.35),
                    pico(polen(d), 0.2))
        bs.guardar('ambiente', reverb(x, 0.18, 1.2), k + 1, alto=0.55)
    for k in range(2):
        x = mezclar(pico(gemido(0.4, 120 + 15 * k, 'a'), 0.9), pico(hojas(0.3, 160, 3000), 0.4))
        bs.guardar('herido', x, k + 1, alto=0.7)
    x = mezclar(pico(gemido(1.3, 85, 'u') * curva(n_(1.3), [(0, 1.0), (1, 0.4)]), 0.8),
                en(0.5, pico(crujido(0.8, 50, 0.8), 0.5)), en(0.4, pico(hojas(0.9, 120, 2400), 0.5)))
    bs.guardar('muerte', reverb(x, 0.2, 1.4), alto=0.75)
    for k in range(2):
        x = mezclar(pico(boom(90, 45, 0.03, 0.15), 0.8), pico(chasquidos(0.15, 120, 400, 2500), 0.6),
                    pico(hojas(0.15, 120, 2600), 0.3))
        bs.guardar('paso', x, k + 1, alto=0.35)
    dur = 0.9
    n = n_(dur)
    x = mezclar(pico(crujido(dur, curva(n, [(0, 40), (1, 85)]), 1.0), 0.8),
                pico(chasquidos(dur, curva(n, [(0, 30), (0.3, 160), (1, 20)]), 300, 2500), 0.7),
                pico(boom(70, 35, 0.12, 0.6), 0.5))
    bs.guardar('enraiza', reverb(x, 0.15, 1.0), alto=0.85)
    notas = (1175.0, 1568.0, 1760.0, 2349.0)
    x = np.zeros(n_(1.4))
    for i, f in enumerate(notas):
        s = seno(f, 0.9, ((1, 1.0), (2, 0.25), (3, 0.08))) * ventana(0.9, 0.08, 0.6) * 0.5
        x = mezclar(x, en(0.12 * i, s))
    x = mezclar(pico(x[:n_(1.4)], 0.6), pico(hojas(1.4, 30, 3200), 0.3))
    bs.guardar('florece', reverb(x, 0.35, 1.8), alto=0.45)


MOBS = {'fauces_verde': lambda: fauces('verde'), 'fauces_carmin': lambda: fauces('carmin'),
        'fauces_escarcha': lambda: fauces('escarcha'), 'trampa': trampa, 'pina': pina, 'zombi_planta': zombi_planta}


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
