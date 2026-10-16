"""
Los sonidos y la música del Momento Maldición (15-10-2026). Todo nuestro: los compañeros dejaron una idea, pero Juan
pidió crearlo todo («aquí todo lo creamos»). Va a la par de la cinemática (MomentoMaldicionCliente; los ticks de
abajo son los suyos):

  momento.animacion   0-126: el corazón que late (cada vez más seguido), el Sello que se dibuja (el zumbido de
                      cristal del círculo, el del segundo círculo que baja, un golpe de cristal por cada punta de la
                      estrella y una campanita por cada runa, subiendo la escala) y los susurros que suben
  momento.titulo      126-168: el núcleo del Sello que se carga (un zumbido que sube, los chispazos de sus rayos,
                      un coro hondo, el corazón desbocado), el Sello que cruje al rajarse y, en 168, el silencio de
                      golpe con un pitido de oído
  momento.cielo       180: el cielo entero que se raja, de lo alto al horizonte (cristal que corre y rueda)
  momento.desprende   mientras dura, cada trozo del cielo que se suelta y cae
  momento.fractura    174: la pantalla que revienta: cristal en esquirlas, el golpe grave y el retumbar
  momento.aviso       224, con el título y el texto en el chat: una campana grave de tercera menor con un susurro
  momento.fin         al pararlo: las esquirlas al revés, un soplo que sube, campanitas y un coro mayor
  momento.musica      mientras dura, en bucle: una nana maldita. Una cajita de música rota (algo desafinada, con
                      el vaivén de un muelle cansado) en re menor armónica y en tres por cuatro, sobre un dron
                      grave, un coro de fondo y el corazón (pum-pum) al principio de cada compás de 3,7 s, que es el
                      latido del cielo y de las grietas en el juego. Dieciséis compases (59,2 s); la cola de la
                      reverberación se pliega al principio, así el bucle no tiene costura.

Usa las herramientas de minijefes_sonidos.py. Uso: python momento_maldicion_sonidos.py <raiz del proyecto> [hoja]
"""
import os
import sys

import numpy as np
import soundfile as sf

import minijefes_sonidos as ms
from minijefes_sonidos import (arbol_campanas, boom, caida, chasquidos, coro_voces, cuenco, curva, en, filtro_mov,
                               huehuetl, mezclar, modos, n_, pb, pico, reverb, ruido, shepard, soplo, susurro, t_,
                               ventana)

ms.SUBTITULOS['momento'] = {
    'animacion': ('Se dibuja un sello maldito', 'A cursed seal is drawn'),
    'titulo': ('El sello se carga', 'The seal charges'),
    'cielo': ('El cielo se raja', 'The sky cracks open'),
    'desprende': ('Cae un trozo del cielo', 'A piece of the sky falls'),
    'fractura': ('Algo se rompe', 'Something shatters'),
    'aviso': ('Dobla la campana maldita', 'The cursed bell tolls'),
    'fin': ('La maldición se rompe', 'The curse breaks'),
}
ms.SALAS['momento'] = ('abismo', 5500)


def s_(tick):
    return tick / 20.0


# El calendario de la cinemática (ticks), el mismo que MomentoMaldicionCliente.
LATIDOS_ANIMACION = [0, 30, 54, 74, 90, 104, 116]
LATIDOS_TITULO = [126, 134, 142, 149, 155, 160, 164]
T_CIRCULO = (18, 40)
T_CIRCULO2 = (40, 56)
T_ESTRELLA = (56, 80)
T_RUNAS = (80, 118)
RUNAS = 16
T_TITULO = 126
T_GRIETAS = 150
T_SILENCIO = 168

# Re menor armónica (la escala de la nana y de las runas).
ESCALA = [62, 64, 65, 67, 69, 70, 73]
CAMPANA = ((0.5, 0.9), (1.0, 1.0), (1.183, 0.7), (1.506, 0.45), (2.0, 0.5), (2.514, 0.25), (2.662, 0.3),
           (3.011, 0.15), (4.166, 0.12), (5.433, 0.07))
CRISTAL = ((1.0, 1.0), (2.32, 0.6), (4.25, 0.35), (6.63, 0.2))
# Una púa de cajita de música: el modo de flexión y sus parciales altos.
PUA = ((1.0, 1.0), (2.0, 0.1), (6.27, 0.28), (17.55, 0.07))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def nota_escala(i, base=74):
    """La nota i de la escala menor armónica desde base (i puede pasar de la octava)."""
    o, k = divmod(i, len(ESCALA))
    return base - 62 + ESCALA[k] + 12 * o


def latido(fuerza=1.0, doble=True):
    """Pum-pum: el corazón, hondo, con el segundo golpe más flojo."""
    # Solo la membrana, sin el golpe de la mano: un latido, no un tambor.
    pum = pico(pb(huehuetl(54.0, 1.0, 0.7, 0.13), 260, 2), 1.0)
    x = pico(pum, fuerza)
    if doble:
        x = mezclar(x, en(0.22, pico(pb(huehuetl(48.0, 0.8, 0.6, 0.12), 240, 2), 0.65 * fuerza)))
    return x


def zumbido(dur, f0, f1, brillo=0.3):
    """El trazo de luz del Sello: un tono de cristal que se desliza, con su chisporroteo."""
    n = n_(dur)
    f = curva(n, [(0, f0), (1, f1)])
    fase = 2 * np.pi * np.cumsum(f) / ms.SR
    tono = np.sin(fase) + 0.45 * np.sin(2 * fase + 0.3) + 0.25 * np.sin(3.01 * fase) + 0.12 * np.sin(5.02 * fase)
    tono *= 1 + 0.15 * np.sin(2 * np.pi * 7.0 * t_(dur))
    chispa = filtro_mov(ruido(dur), f * 9, 'band', 6.0)
    env = ventana(dur, dur * 0.15, dur * 0.35)
    return mezclar(pico(tono * env, 1.0), pico(chispa * env, brillo))


def golpe_cristal(f, fuerza=1.0):
    return pico(modos(f, 1.6, CRISTAL, 0.55, 0.002), fuerza)


# ----------------------------------------------------------------------------------------------------------------
#  La cinemática
# ----------------------------------------------------------------------------------------------------------------
def animacion():
    dur = s_(T_TITULO) + 0.6
    capas = []
    # El mundo se apaga: un golpe grave y un dron que crece.
    capas.append(pico(boom(64, 26, 0.55, 3.0), 0.9))
    n = n_(dur)
    dron = (np.sin(2 * np.pi * 36.7 * t_(dur)) + 0.4 * np.sin(2 * np.pi * 55.0 * t_(dur) + 1.0)) * curva(n, [(0, 0.0), (0.15, 0.35), (1, 0.8)])
    capas.append(pico(dron, 0.35))
    # El corazón, cada vez más seguido y más fuerte.
    for k, tick in enumerate(LATIDOS_ANIMACION):
        capas.append(en(s_(tick), latido(0.55 + 0.35 * k / len(LATIDOS_ANIMACION))))
    # El Sello: el círculo de fuera que sube, el de dentro que baja, las puntas de la estrella y las runas.
    a, b = T_CIRCULO
    capas.append(en(s_(a), pico(zumbido(s_(b - a), 196.0, 392.0), 0.45)))
    a, b = T_CIRCULO2
    capas.append(en(s_(a), pico(zumbido(s_(b - a), 523.0, 294.0, 0.2), 0.32)))
    a, b = T_ESTRELLA
    for k in range(7):
        capas.append(en(s_(a + k * (b - a) / 7), golpe_cristal(midi(nota_escala(k * 2, 74)), 0.4)))
    a, b = T_RUNAS
    for k in range(RUNAS):
        f = midi(nota_escala(k, 74))
        capas.append(en(s_(a + k * (b - a) / RUNAS), pico(cuenco(f, 1.4, 0.8, 0.0, 0.003), 0.18 + 0.12 * k / RUNAS)))
    # Los susurros: entran con el Sello y suben hasta el nombre.
    for k, (cuando, vocal) in enumerate(((1.0, 'o'), (2.2, 'a'), (3.4, 'e'), (4.4, 'o'), (5.2, 'a'))):
        d = 1.6
        capas.append(en(cuando, pico(susurro(d, vocal, 1.0 + 0.05 * k, curva(n_(d), [(0, 0.9), (1, 1.2)])), 0.12 + 0.05 * k)))
    capas.append(en(1.0, pico(coro_voces(dur - 1.0, [73.4, 77.8, 110.0], 'o', curva(n_(dur - 1.0), [(0, 1.0), (1, 1.03)]), 0.5)
                              * curva(n_(dur - 1.0), [(0, 0.0), (0.4, 0.4), (1, 1.0)]), 0.28)))
    x = reverb(mezclar(*capas), 0.3, 2.0)
    return x


def chispazo(dur=0.09, fuerza=1.0):
    """Un rayo pequeño que salta: un chasquido de ruido agudo que zumbea (la corriente) y se corta."""
    n = n_(dur)
    t = t_(dur)
    zumba = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * ms.rng.uniform(70, 130) * t))
    x = ms.bp(ruido(dur), 1800, 9000) * zumba * caida(dur, dur * 0.35, 0.001)
    return pico(x, fuerza)


def titulo():
    """126-168: el nucleo se carga (Juan quitó el texto de la animación: ya no es el nombre). Un zumbido que sube, los
    chispazos de los rayos que saltan a la estrella, el coro, el corazón desbocado y, desde 150, el sello que cruje."""
    dur = s_(T_SILENCIO - T_TITULO)
    n = n_(dur)
    sube = curva(n, [(0, 0.3), (0.7, 0.7), (1, 1.0)])
    coro = pico(coro_voces(dur, [146.8, 155.6, 220.0, 293.7], 'a', curva(n, [(0, 1.0), (1, 1.08)]), 0.45) * sube, 0.5)
    gira = pico(shepard(dur, 1.0, 6, 55.0) * sube, 0.22)
    f = curva(n, [(0, 110), (1, 620)])
    fase = 2 * np.pi * np.cumsum(f) / ms.SR
    carga = pico((np.sin(fase) + 0.5 * np.sin(2 * fase) + 0.25 * np.sin(3 * fase)) * sube ** 1.5
                 * (1 + 0.3 * np.sin(2 * np.pi * curva(n, [(0, 6), (1, 22)]) * t_(dur))), 0.35)
    capas = [coro, gira, carga]
    # Los chispazos, cada dos ticks a partir de que salen los rayos (a veces dos).
    for k in range(int((T_SILENCIO - T_TITULO - 6) / 2)):
        if ms.rng.random() < 0.6 + 0.3 * k / 20:
            capas.append(en(s_(6 + 2 * k) + ms.rng.uniform(0, 0.05), chispazo(ms.rng.uniform(0.05, 0.12), 0.25 + 0.2 * k / 20)))
    for k, tick in enumerate(LATIDOS_TITULO):
        capas.append(en(s_(tick - T_TITULO), latido(0.8 + 0.2 * k / len(LATIDOS_TITULO), doble=False)))
    # El Sello cruje al rajarse: chasquidos que se aceleran y un crujido que baja.
    g = s_(T_GRIETAS - T_TITULO)
    dg = dur - g
    cruje = mezclar(pico(chasquidos(dg, curva(n_(dg), [(0, 8), (1, 120)]), 900, 7000), 0.5),
                    pico(filtro_mov(ruido(dg, 'marron'), curva(n_(dg), [(0, 900), (1, 160)]), 'band', 8.0), 0.45))
    capas.append(en(g, cruje))
    x = reverb(mezclar(*capas), 0.22, 1.2)[:n]
    # En 168, el silencio de golpe; en él, solo un pitido de oído que se va.
    x[-n_(0.008):] *= np.linspace(1, 0, n_(0.008))
    pitido = np.sin(2 * np.pi * 6800 * t_(0.32)) * caida(0.32, 0.12, 0.002)
    return np.concatenate([x, pico(pitido, 0.05)])


def fractura():
    rotura = esquirlas(0.9, 14, 1800, 7000, 0.12)
    golpe = pico(boom(72, 24, 0.5, 3.2), 1.0)
    retumba = pico(pb(ruido(3.6, 'marron'), 180, 2) * caida(3.6, 1.1, 0.01), 0.55)
    return reverb(mezclar(pico(rotura, 0.75), golpe, retumba), 0.35, 2.5)


def cielo():
    """El cielo que se raja entero tras la fractura: grietas de cristal que corren de lo alto al horizonte (cada vez
    más lejos y más graves), un trueno de cristal que rueda y esquirlas que caen."""
    dur = 4.6
    capas = []
    for k in range(26):
        cuando = (k / 26) ** 1.4 * 3.2
        lejos = k / 26
        capas.append(en(cuando, pico(chasquidos(0.18, 600, 600 + 2400 * (1 - lejos), 5000 + 5000 * (1 - lejos)), 0.7 - 0.4 * lejos)))
        capas.append(en(cuando, pico(modos(ms.rng.uniform(900, 3200) * (1 - 0.4 * lejos), 1.2, CRISTAL, 0.3), 0.25 * (1 - lejos))))
    rueda = pb(ruido(dur, 'marron'), 220, 2) * curva(n_(dur), [(0, 0.2), (0.15, 1.0), (0.6, 0.6), (1, 0.0)])
    capas.append(pico(rueda, 0.7))
    capas.append(en(0.6, pico(arbol_campanas(3.0, 9000.0, 2500.0, 30), 0.18)))
    return reverb(mezclar(*capas), 0.45, 2.8)


def desprende():
    """Un trozo del cielo que se suelta: el chasquido que lo arranca, el cristal que tintinea al caer y un soplo grave
    que baja (lejos: con mucha sala)."""
    arranca = mezclar(pico(chasquidos(0.12, 900, 2500, 10000), 0.9), pico(modos(ms.rng.uniform(1400, 2200), 1.4, CRISTAL, 0.35), 0.5))
    cae = pico(soplo(1.6, 900.0, 140.0, 1.2, 0.08), 0.4)
    tintinea = pico(arbol_campanas(1.6, 8000.0, 2200.0, 14), 0.22)
    golpe = pico(boom(55, 30, 0.3, 1.2), 0.35)
    return reverb(mezclar(arranca, en(0.1, cae), en(0.2, tintinea), en(1.4, golpe)), 0.5, 2.6)


def esquirlas(dur, cuantas, f_lo, f_hi, tau):
    """Cristal que revienta: muchas esquirlas que suenan una tras otra, cada una en su tono."""
    capas = []
    for k in range(cuantas):
        cuando = (k / cuantas) ** 1.8 * dur * 0.7
        f = ms.rng.uniform(f_lo, f_hi)
        capas.append(en(cuando, pico(modos(f, tau * 4, CRISTAL, tau), ms.rng.uniform(0.3, 1.0))))
    golpe = chasquidos(dur, curva(n_(dur), [(0, 900), (0.15, 300), (1, 10)]), 2000, 12000)
    return mezclar(pico(mezclar(*capas), 0.8), pico(golpe, 0.7))


def aviso():
    campana = mezclar(pico(modos(98.0, 4.0, CAMPANA, 2.2, 0.0025), 1.0),
                      en(0.02, pico(modos(196.0 * 1.183, 2.5, CAMPANA[1:5], 1.0), 0.25)))
    soplo_antes = pico(susurro(0.45, 'e', 1.1) * np.linspace(0, 1, n_(0.45)) ** 2, 0.25)
    coro = pico(coro_voces(3.0, [73.4, 87.3, 110.0], 'o', None, 0.4), 0.22)
    return reverb(mezclar(soplo_antes, en(0.42, campana), en(0.5, coro)), 0.4, 3.0)


def fin():
    al_reves = esquirlas(0.8, 10, 2200, 7500, 0.1)[::-1]
    al_reves = pico(al_reves * np.linspace(0.2, 1.0, len(al_reves)) ** 2, 0.5)
    sube = pico(soplo(1.6, 400.0, 3200.0, 1.0, 0.15), 0.4)
    luz = pico(arbol_campanas(1.6, 9000.0, 1800.0, 18, baja=False), 0.35)
    coro = pico(coro_voces(3.2, [220.0, 277.2, 329.6, 440.0], 'a', None, 0.3), 0.5)
    return reverb(mezclar(al_reves, en(0.55, sube), en(0.8, luz), en(0.75, coro)), 0.4, 2.8)


# ----------------------------------------------------------------------------------------------------------------
#  La nana maldita (la música, en estéreo y en bucle)
# ----------------------------------------------------------------------------------------------------------------
COMPAS = 3.7
PULSO = COMPAS / 3
COMPASES = 16
# La frase de la nana: (compás, pulso, nota MIDI, pulsos que dura).
FRASE = [
    (0, 0, 69, 1), (0, 1, 74, 1), (0, 2, 77, 1),
    (1, 0, 76, 2), (1, 2, 74, 1),
    (2, 0, 73, 1), (2, 1, 76, 1), (2, 2, 69, 1),
    (3, 0, 74, 3),
    (4, 0, 77, 1), (4, 1, 79, 0.5), (4, 1.5, 77, 0.5), (4, 2, 76, 1),
    (5, 0, 74, 1), (5, 1, 70, 2),
    (6, 0, 69, 1), (6, 1, 67, 0.5), (6, 1.5, 69, 0.5), (6, 2, 73, 1),
    (7, 0, 74, 3),
]
# Los acordes del coro, uno por compás de la frase.
ACORDES = [(50, 53, 57), (50, 53, 57), (45, 49, 52), (50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52), (50, 53, 57)]


def pua(f, dur, rota=0.0):
    """Una nota de la cajita: el golpe de la púa y su timbre de metal fino; rota la desafina un poco."""
    f = f * 2 ** (rota * ms.rng.uniform(-0.12, 0.12) / 12)
    golpe = pico(pb(ruido(0.01), 9000, 2) * caida(0.01, 0.002, 0.0002), 0.25)
    return mezclar(pico(modos(f, dur, PUA, 0.9), 1.0), golpe)


def nana():
    largo = COMPASES * COMPAS
    total = largo + 8.0
    L = np.zeros(n_(total))
    R = np.zeros(n_(total))

    def poner(x, cuando, pan=0.0, ganancia=1.0):
        i = n_(cuando)
        x = x[:len(L) - i] * ganancia
        L[i:i + len(x)] += x * np.sqrt(0.5 * (1 - pan))
        R[i:i + len(x)] += x * np.sqrt(0.5 * (1 + pan))

    # El dron grave (re y la), con su batido, y un viento muy bajo.
    t = t_(total)
    dron = (np.sin(2 * np.pi * 73.4 * t) + 0.6 * np.sin(2 * np.pi * 73.9 * t) + 0.45 * np.sin(2 * np.pi * 110.0 * t)) \
        * (0.8 + 0.2 * np.sin(2 * np.pi * t / COMPAS))
    poner(pico(dron, 0.16), 0.0)
    poner(pico(pb(ruido(total, 'marron'), 600, 2), 0.1), 0.0)
    # El corazón al principio de cada compás: el latido del cielo en el juego.
    for c in range(COMPASES):
        poner(latido(0.5), c * COMPAS)
    # La cajita: la frase entera en los compases 4-11 y la mitad, una octava abajo, en 12-15.
    for c0, octava, compases, ganancia in ((4, 0, 8, 0.32), (12, -12, 4, 0.26)):
        for (c, p, m, d) in FRASE:
            if c >= compases:
                continue
            cuando = (c0 + c) * COMPAS + p * PULSO
            x = pua(midi(m + octava), max(1.8, d * PULSO + 1.0), rota=1.0)
            poner(x, cuando, pan=0.35 if (c + int(p * 2)) % 2 else -0.35, ganancia=ganancia)
            # Un eco más agudo y lejano en la segunda vuelta.
            if octava < 0 and p == 0:
                poner(pua(midi(m + 12), 1.4, rota=1.0), cuando + PULSO * 0.5, pan=0.6, ganancia=0.08)
    # El coro de fondo, un acorde por compás con la frase.
    for k in range(12):
        acorde = ACORDES[k % 8]
        c = 4 + k
        voces = coro_voces(COMPAS + 0.6, [midi(m) for m in acorde], 'o', None, 0.45)
        poner(pico(voces, 0.16), c * COMPAS - 0.2, pan=-0.2)
        poner(pico(voces, 0.16), c * COMPAS - 0.188, pan=0.2)
    # Susurros sueltos y, antes de volver a empezar, un soplo al revés que se traga el bucle.
    for c, vocal, pan in ((2, 'o', -0.6), (6, 'a', 0.6), (10, 'e', -0.5), (14, 'o', 0.5)):
        poner(pico(susurro(1.8, vocal, 1.0, curva(n_(1.8), [(0, 0.85), (1, 1.15)])), 0.1), c * COMPAS + PULSO, pan=pan)
    sopla = soplo(2.2, 3000.0, 300.0, 1.0, 0.1)[::-1]
    poner(pico(sopla, 0.14), largo - 2.2)
    # La campana lejana que abre la nana.
    poner(pico(modos(98.0, 5.0, CAMPANA, 2.4, 0.0025), 0.2), 0.0)
    # La sala, y la cola plegada al principio: así el final suena dentro del principio y no hay costura.
    L = reverb(L, 0.35, 2.6)
    R = reverb(R, 0.35, 2.6)
    n = n_(largo)
    estereo = np.stack([L[:n].copy(), R[:n].copy()], axis=1)
    cola = min(len(L) - n, n)
    estereo[:cola, 0] += L[n:n + cola]
    estereo[:cola, 1] += R[n:n + cola]
    return estereo * (0.85 / np.max(np.abs(estereo)))


def escribir_estereo(nombre, x):
    ruta = os.path.join(ms.SONIDOS, 'momento', nombre + '.ogg')
    # Por trozos: libsndfile se cae sin avisar si se le da un OGG largo de una vez.
    with sf.SoundFile(ruta, 'w', ms.SR, 2, format='OGG', subtype='VORBIS') as fh:
        for i in range(0, len(x), 16384):
            fh.write(x[i:i + 16384].astype(np.float32))
    print(f'  momento/{nombre:22s} {len(x) / ms.SR:5.2f} s (estéreo, en bucle)', flush=True)


def escribir_json_musica():
    """La música va en stream y sin subtítulo, como la de los jefes."""
    import collections
    import json
    ruta = os.path.join(ms.RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
    with open(ruta, encoding='utf-8') as fh:
        datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
    datos['momento.musica'] = {'sounds': [{'name': 'atalaya:momento/musica', 'stream': True}]}
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')


def main():
    ms.empezar('momento')
    ms.guardar('animacion', animacion(), alto=0.85)
    ms.guardar('titulo', titulo(), alto=0.8)
    ms.guardar('fractura', fractura(), alto=0.92, limite=0.7)
    ms.guardar('aviso', aviso(), alto=0.8)
    ms.guardar('fin', fin(), alto=0.8)
    ms.guardar('cielo', cielo(), alto=0.85, limite=0.75)
    ms.guardar('desprende', desprende(), alto=0.75)
    escribir_estereo('musica', nana())
    ms.escribir_json()
    escribir_json_musica()
    if len(sys.argv) > 2:
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
