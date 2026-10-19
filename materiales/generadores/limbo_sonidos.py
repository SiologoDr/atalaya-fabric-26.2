"""
Los sonidos del Limbo (18-10-2026), sintetizados como todos los del mod (minijefes_sonidos.py):

  limbo.musica            la música de fondo (75 s, en re menor): un zumbido grave que late, un coro lejano que
                          aparece y se va, campanas de cuenco que doblan sueltas, susurros al revés y unas notas de
                          cristal; sin ritmo, para perderse
  limbo.susurro           lo que se oye de vez en cuando (el «mood» de la dimensión): voces sin cuerdas que cuchichean
  limbo.destierro         al entrar: un soplo al revés que te arrastra y una campana grave que dobla
  limbo.salida            el zumbido de la salida (cada dos segundos; se oye de lejos y sirve para encontrarla): un
                          acorde de coro y cristal que respira
  limbo.cambia            la salida cambia de sitio: un retumbo grave y la campana que se aleja
  limbo.escapa            al salir: notas de cristal que suben y un soplo que se abre
  limbo.bloque.*          la piedra del Limbo: pasos (piedra con un eco que no es de este mundo), golpe, poner,
                          romper y caída

Uso: python limbo_sonidos.py <raíz> [hoja]
"""
import collections
import json
import os
import sys

import numpy as np

import minijefes_sonidos as ms
from minijefes_sonidos import (armonica_cristal, boom, bp, caida, chasquidos, coro_voces, cuenco, curva, en, filtro_mov,
                               mezclar, modos, n_, pa, pb, pico, reverb, ruido, seno, soplo, susurro, t_, ventana)

rng = np.random.default_rng(20261024)
D2, A2, D3, F3, A3, C4, D4, F4, A4, C5, D5 = 73.42, 110.0, 146.83, 174.61, 220.0, 261.63, 293.66, 349.23, 440.0, 523.25, 587.33
EVENTOS = collections.OrderedDict()
SUBS = {
    'musica': ('Música del Limbo', 'Limbo music'),
    'susurro': ('Susurran en el Limbo', 'Whispers in the Limbo'),
    'destierro': ('Alguien cae al Limbo', 'Someone falls into the Limbo'),
    'salida': ('Zumba la salida del Limbo', 'The way out hums'),
    'cambia': ('La salida del Limbo se mueve', 'The way out moves'),
    'escapa': ('Alguien sale del Limbo', 'Someone escapes the Limbo'),
    'bloque.paso': ('Pasos en el Limbo', 'Footsteps in the Limbo'),
    'bloque.golpe': ('Golpe en la piedra del Limbo', 'Limbo stone is hit'),
    'bloque.poner': ('Se pone piedra del Limbo', 'Limbo stone is placed'),
    'bloque.romper': ('Se rompe piedra del Limbo', 'Limbo stone breaks'),
    'bloque.caida': ('Algo cae en el Limbo', 'Something lands in the Limbo'),
}


def guardar(evento, archivo, x, alto=0.85, stream=False, **kw):
    ms.guardar(archivo, x, None, alto=alto, **kw)
    EVENTOS.setdefault(evento, []).append((archivo, stream))


def musica():
    dur = 75.0
    n = n_(dur)
    t = t_(dur)
    # El zumbido: re y la graves, con un batido lento.
    zumbido = mezclar(seno(D2 * (1 + 0.002 * np.sin(2 * np.pi * 0.05 * t)), dur, ((1, 1.0), (2, 0.3), (3, 0.12))),
                      seno(A2 * 1.003, dur, ((1, 0.7), (2, 0.2))), seno(D3 * 0.997, dur, ((1, 0.4),)))
    zumbido *= 0.6 + 0.4 * np.sin(2 * np.pi * t / 19.0 + 1.0) ** 2
    zumbido = pb(zumbido, 900)
    # El coro lejano: dos acordes que aparecen y se van.
    coro = np.zeros(n)
    for (ini, largo, notas) in ((8.0, 16.0, (D3, F3, A3)), (34.0, 14.0, (C4 * 0.5 * 2, F3, A3)), (55.0, 15.0, (D3, F3, C4))):
        c = coro_voces(largo, notas, 'o', aliento=0.5) * ventana(largo, largo * 0.4, largo * 0.45)
        coro = mezclar(coro, en(ini, pb(c, 2500)))
    coro = coro[:n]
    # Las campanas: doblan sueltas, en notas de la escala.
    campanas = np.zeros(n)
    tt = 4.0
    while tt < dur - 6:
        f = rng.choice((D4, F4, A4, C5, D5)) * rng.choice((0.5, 1.0))
        c = cuenco(f, 6.0, 1.0, 0.0, 0.003) * rng.uniform(0.4, 0.9)
        campanas = mezclar(campanas, en(tt, c))
        tt += rng.uniform(6.0, 11.0)
    campanas = campanas[:n]
    # Susurros al revés.
    sus = np.zeros(n)
    tt = 6.0
    while tt < dur - 4:
        d = rng.uniform(1.2, 2.4)
        s = susurro(d, rng.choice(['a', 'o', 'e', 'u']), rng.uniform(0.9, 1.3))[::-1]
        sus = mezclar(sus, en(tt, bp(s, 400, 3500) * rng.uniform(0.3, 0.7)))
        tt += rng.uniform(4.0, 9.0)
    sus = sus[:n]
    # El cristal: cuatro notas que bajan, dos veces.
    cristal = np.zeros(n)
    for ini in (26.0, 60.0):
        for k, f in enumerate((D5, C5, A4, F4)):
            cristal = mezclar(cristal, en(ini + k * 2.2, armonica_cristal(f, 3.4) * 0.6))
    cristal = cristal[:n]
    x = mezclar(pico(zumbido, 0.55), pico(coro, 0.35), pico(campanas, 0.45), pico(sus, 0.18), pico(cristal, 0.3))
    x = reverb(x, 0.45, 3.0)[:n]
    x *= ventana(dur, 4.0, 6.0)
    guardar('musica', 'musica', x, alto=0.6, stream=True)


def susurros():
    for k in range(3):
        d = 2.0 + 0.6 * k
        capas = []
        tt = 0.0
        while tt < d - 0.6:
            dd = rng.uniform(0.4, 0.9)
            capas.append(en(tt, bp(susurro(dd, rng.choice(['a', 'e', 'o']), rng.uniform(1.0, 1.4)), 600, 5000)
                            * rng.uniform(0.5, 1.0)))
            tt += dd * rng.uniform(0.5, 0.9)
        x = mezclar(*capas)
        guardar('susurro', f'susurro{k + 1}', reverb(x, 0.4, 2.5), alto=0.4)


def destierro():
    arrastra = soplo(1.2, 300, 2400, 1.0, 0.3)[::-1]
    campana = mezclar(pico(cuenco(D3, 4.0, 1.0, 0.0, 0.004), 1.0), pico(boom(60, 30, 0.4, 2.0), 0.6))
    coro = coro_voces(2.5, (D3, A3, D4), 'u', aliento=0.6)
    x = mezclar(pico(arrastra, 0.8), en(1.1, pico(campana, 1.0)), en(1.0, pico(coro, 0.4)))
    guardar('destierro', 'destierro', reverb(x, 0.4, 3.0), alto=0.9)


def zumbido_salida():
    dur = 2.2
    acorde = coro_voces(dur, (D4, F4, A4), 'a', aliento=0.25) * ventana(dur, 0.6, 0.9)
    vidrio = mezclar(armonica_cristal(D5, dur), armonica_cristal(A4 * 2, dur) * 0.5)
    x = mezclar(pico(acorde, 0.7), pico(vidrio, 0.5))
    guardar('salida', 'salida', reverb(x, 0.35, 2.0), alto=0.7)


def cambia():
    retumbo = mezclar(pico(boom(45, 25, 0.8, 3.0), 1.0), pico(pb(ruido(3.0, 'marron'), 200) * ventana(3.0, 0.3, 2.0), 0.6))
    campana = cuenco(A3, 4.0, 1.0, 0.0, 0.005)
    n = n_(4.0)
    campana = campana * curva(n, [(0, 1.0), (1, 0.2)])
    x = mezclar(pico(retumbo, 0.9), en(0.3, pico(campana, 0.7)))
    guardar('cambia', 'cambia', reverb(x, 0.45, 3.0), alto=0.85)


def escapa():
    notas = (D4, F4, A4, D5)
    x = np.zeros(n_(2.5))
    for k, f in enumerate(notas):
        x = mezclar(x, en(0.12 * k, armonica_cristal(f, 1.6) * 0.8))
    abre = soplo(1.4, 600, 4000, 0.9, 0.2)
    x = mezclar(pico(x, 0.8), en(0.3, pico(abre, 0.6)))
    guardar('escapa', 'escapa', reverb(x, 0.35, 2.0), alto=0.85)


def piedra_golpe(fuerza=1.0, f=900.0, eco=True):
    seco = bp(ruido(0.05), f * 0.4, f * 4) * caida(0.05, 0.01, 0.001)
    cuerpo = boom(f * 0.12, f * 0.07, 0.03, 0.15)
    x = mezclar(pico(seco, 1.0 * fuerza), pico(cuerpo, 0.5 * fuerza))
    if eco:
        # El eco que no es de este mundo: una sombra del golpe, más aguda y desafinada, que llega tarde.
        sombra = modos(f * 1.7, 0.3, ((1, 1.0), (1.41, 0.5), (2.3, 0.2)), 0.07, 0.004) * 0.12
        x = mezclar(x, en(0.08, sombra))
    return x


def bloques():
    for k in range(4):
        guardar('bloque.paso', f'bloque_paso{k + 1}', piedra_golpe(0.6, 700 + 90 * k), alto=0.35)
    for k in range(2):
        guardar('bloque.golpe', f'bloque_golpe{k + 1}', piedra_golpe(0.8, 1100 + 150 * k, False), alto=0.45)
    guardar('bloque.poner', 'bloque_poner', piedra_golpe(1.0, 600, False), alto=0.6)
    x = mezclar(pico(piedra_golpe(1.2, 500), 1.0), en(0.02, pico(chasquidos(0.4, 120, 800, 6000), 0.5)))
    guardar('bloque.romper', 'bloque_romper', x, alto=0.7)
    guardar('bloque.caida', 'bloque_caida', piedra_golpe(0.9, 450, False), alto=0.5)


def escribir_json(raiz):
    r = os.path.join(raiz, 'src/main/resources/assets/atalaya/sounds.json')
    datos = json.load(open(r, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    for k in [k for k in datos if k.startswith('limbo.')]:
        del datos[k]
    for ev, archivos in EVENTOS.items():
        sonidos = []
        for a, stream in archivos:
            sonidos.append({'name': f'atalaya:limbo/{a}', 'stream': True} if stream else f'atalaya:limbo/{a}')
        datos[f'limbo.{ev}'] = {'subtitle': f'subtitles.atalaya.limbo.{ev}', 'sounds': sonidos}
    with open(r, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    for idioma, k in (('es_es', 0), ('en_us', 1)):
        p = os.path.join(raiz, f'src/main/resources/assets/atalaya/lang/{idioma}.json')
        d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        for clave in [c for c in d if c.startswith('subtitles.atalaya.limbo.')]:
            del d[clave]
        for ev in EVENTOS:
            d[f'subtitles.atalaya.limbo.{ev}'] = SUBS[ev][k]
        with open(p, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
    print(len(EVENTOS), 'eventos del Limbo')


def _escribir_a_trozos(ruta, datos, sr, format=None, subtype=None):
    """sf.write, pero a trozos de un segundo: el codificador de ogg revienta (desbordamiento de pila) si le das 75 s de
    una vez."""
    import soundfile
    with soundfile.SoundFile(ruta, 'w', sr, 1, format=format, subtype=subtype) as f:
        for i in range(0, len(datos), sr):
            f.write(datos[i:i + sr])


def main():
    ms.sf.write = _escribir_a_trozos
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    ms.RAIZ = raiz
    ms.SONIDOS = raiz + '/src/main/resources/assets/atalaya/sounds'
    ms.SALAS['limbo'] = ('abismo', 4200)
    ms.empezar('limbo')
    musica()
    susurros()
    destierro()
    zumbido_salida()
    cambia()
    escapa()
    bloques()
    escribir_json(raiz)
    if len(sys.argv) > 2:
        ms.hoja(sys.argv[2])


if __name__ == '__main__':
    main()
