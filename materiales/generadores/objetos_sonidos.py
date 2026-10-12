"""
Los sonidos de los objetos de apoyo (11-10-2026):

  objeto.reparar   el Kit de Reparación sobre la armadura de un compañero: tres golpes de martillo sobre chapa (cada
                   uno algo más agudo, la chapa que vibra y una chispa) y el roce del paño que la deja como nueva
  objeto.elixir    al acabar de beber el Elixir de Vida: un latido hondo, el corazón que vuelve, y unas campanitas
                   cálidas que suben

Usa las herramientas de minijefes_sonidos.py. Uso: python objetos_sonidos.py <raiz del proyecto> [hoja]
"""
import numpy as np

import minijefes_sonidos as ms
from minijefes_sonidos import (arbol_campanas, bp, caida, chispas, cuenco, en, huehuetl, mezclar, modos, pico, reverb,
                               ruido, soplo)

ms.SUBTITULOS['objeto'] = {
    'reparar': ('Martillazos sobre una armadura', 'Hammer strikes on armor'),
    'elixir': ('Vuelve la vida', 'Life returns'),
}
ms.SALAS['objeto'] = ('plaza', 7000)

# La chapa de una armadura: parciales inarmónicos de metal fino.
CHAPA = ((1.0, 1.0), (2.76, 0.55), (5.40, 0.32), (8.93, 0.18), (13.3, 0.08))


def martillazo(f, fuerza=1.0):
    golpe = bp(ruido(0.03), 1500, 9000) * caida(0.03, 0.006, 0.0005)
    chapa = modos(f, 0.9, CHAPA, 0.22, 0.004)
    return mezclar(pico(golpe, 0.7 * fuerza), pico(chapa, 0.8 * fuerza), pico(chispas(0.25, 30.0), 0.2 * fuerza))


def objetos():
    ms.empezar('objeto')
    golpes = mezclar(martillazo(1180.0), en(0.17, martillazo(1320.0, 0.9)), en(0.36, martillazo(1480.0, 1.1)))
    pano = pico(soplo(0.5, 2500.0, 5000.0, silba=0.05), 0.35)
    brillo = pico(arbol_campanas(0.5, 9000.0, 4000.0, 8, baja=False), 0.3)
    ms.guardar('reparar', reverb(mezclar(golpes, en(0.55, pano), en(0.7, brillo)), 0.2, 1.2), alto=0.8)
    latido = mezclar(pico(huehuetl(58.0, 1.0, 0.6, 0.12), 0.9), en(0.22, pico(huehuetl(52.0, 0.8, 0.6, 0.12), 0.7)))
    sube = pico(arbol_campanas(0.8, 6400.0, 1500.0, 16, baja=False), 0.45)
    calido = pico(cuenco(523.3, 1.8, golpe=0.0, frote=1.0), 0.35)
    ms.guardar('elixir', reverb(mezclar(latido, en(0.3, sube), en(0.25, calido)), 0.3, 1.8), alto=0.8)


if __name__ == '__main__':
    objetos()
    ms.escribir_json()
    if ms.HOJA:
        ms.hoja(ms.HOJA)
